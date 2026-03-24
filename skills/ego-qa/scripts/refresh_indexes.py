#!/usr/bin/env python3
"""在线刷新 ego-qa 索引文件。

从 kb-confluence-map.json 读取页面列表，通过 Confluence REST API 拉取每个页面的
最新内容，重新生成四个索引文件：
  - kb-index.md           （技术文档摘要索引）
  - kb-index-meetings.md  （会议纪要索引）
  - kb-heading-index.md   （大文档章节索引）
  - kb-faq.md             （FAQ 关键词路由索引）

同时自动发现 Confluence 空间中的新页面，追加到 kb-confluence-map.json。

用法:
  python refresh_indexes.py [--refs-dir DIR] [--concurrency N] [--discover]

认证:
  CONFLUENCE_TOKEN — Personal Access Token（必需，搜索/列表 API 需要 PAT 权限）

示例:
  # 基于现有 map 刷新全部索引
  python refresh_indexes.py

  # 先发现新页面再刷新
  python refresh_indexes.py --discover

  # 指定 references 目录和并发数
  python refresh_indexes.py --refs-dir skill/ego-qa/references --concurrency 5
"""

from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import httpx

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REFS_DIR = os.path.join(SCRIPT_DIR, "..", "references")

BASE_URL = os.environ.get("CONFLUENCE_BASE_URL", "https://confluence.shopee.io")
SPACE_KEY = os.environ.get("CONFLUENCE_SPACE_KEY", "MLP")

EGO_ROOT_PAGES = [
    ("621646772", "Ego"),
    ("1079221126", "EGO."),
]

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE

STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been",
    "and", "or", "of", "to", "in", "for", "on", "with", "at", "by",
    "from", "as", "it", "its", "this", "that", "can", "will", "do",
    "has", "have", "had", "not", "but", "if", "you", "your", "we",
    "our", "how", "what", "which", "when", "where", "who", "about",
    "so", "also", "need", "first", "then", "before", "after", "into",
    "的", "了", "在", "是", "和", "与", "或", "及", "等", "中",
    "为", "以", "通过", "进行", "使用", "可以", "一个", "如果",
    "这个", "那个", "需要", "已经", "目前", "其中", "以下",
}

URL_NOISE = {
    "http", "https", "www", "com", "io", "org", "html", "htm",
    "confluence", "shopee", "display", "mlp", "id", "doc",
}

EGO_DOMAIN_TERMS = {
    "checkpoint", "ckpt", "ego-learner", "ego_learner", "sample_server",
    "sample-server", "sampleserver", "converter", "cpp_converter",
    "cpp-converter", "online_learning", "online-learning", "period_training",
    "period-training", "predictor", "ego-predictor", "egopredictor",
    "guardian", "parameter_server", "offlineps", "onlineps", "ps",
    "half_precision", "half-precision", "allreduce", "gpu_pooling",
    "gpu-pooling", "xla", "tensorrt", "trt", "onnx", "onnxruntime",
    "deepctr", "ego-lite", "ego_lite", "egolite", "egobox",
    "egotrain", "ego-train", "train_threads", "max_context_per_device",
    "max_session_per_device", "batch_size", "mini_batch", "minibatch",
    "worker", "wc", "ss", "coordinator", "notebook", "compile",
    "publish", "release", "inferencing", "serving", "grey_release",
    "presstest", "press_test", "benchmark", "mig", "a30", "a100",
    "h100", "l4", "l40s", "t4", "gpu", "cpu", "oom", "coredump",
    "hdfs", "kafka", "sparse", "dense", "embedding", "emb",
    "feature", "slot", "admission", "eviction", "evict",
    "round0", "round1", "eval", "train_config", "io_config",
    "ego-portal", "portal", "prd", "grafana", "monitoring",
    "日志", "训练", "推理", "部署", "编译", "发布", "上线",
    "模型", "版本", "任务", "资源", "配置", "参数", "调优",
    "显存", "内存", "磁盘", "带宽", "吞吐", "延迟", "耗时",
    "样本", "特征", "稀疏", "稠密", "嵌入", "向量",
    "周期训练", "在线学习", "离线训练", "批量训练",
    "半精度", "限流", "负载均衡", "灰度发布",
    "检查点", "快照", "回滚", "同步", "跨机房",
    "准入", "淘汰", "白名单", "告警", "监控",
    "数据供给", "数据转换", "数据格式",
}

MEETING_PATTERNS = ["Meeting", "Biweekly", "biweekly", "Meeting_Minutes",
                    "Biweekly_Report", "会议纪要", "双周报", "Copy of ", "Copy_of_",
                    "_Backup_", "(Backup)", "_Archived_", "(Archived)"]

HEADING_SIZE_THRESHOLD = 10 * 1024
MAX_SUMMARY_CHARS = 200
MIN_SECTION_CHARS = 30
MAX_FAQ_KEYWORDS = 15


# ---------------------------------------------------------------------------
# Auth & HTTP
# ---------------------------------------------------------------------------

_cached_headers: Optional[dict] = None


def _auth_headers():
    global _cached_headers
    if _cached_headers is None:
        token = os.environ.get("CONFLUENCE_TOKEN", "")
        if not token:
            print("错误：未设置 CONFLUENCE_TOKEN。更新脚本需要 Personal Access Token 才能使用搜索/列表 API。",
                  file=sys.stderr)
            sys.exit(1)
        _cached_headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    return _cached_headers


def _client():
    return httpx.Client(timeout=30, verify=_ssl_ctx)


# ---------------------------------------------------------------------------
# HTML → Markdown (reuse from fetch_confluence.py)
# ---------------------------------------------------------------------------

def html_to_markdown(raw_html: str) -> str:
    import html as html_mod
    t = raw_html
    t = re.sub(r'<ac:structured-macro[^>]*>.*?</ac:structured-macro>', '', t, flags=re.DOTALL)
    t = re.sub(r'<ac:[^>]*/?>', '', t)
    t = re.sub(r'</ac:[^>]*>', '', t)
    t = re.sub(r'<ri:[^>]*/?>', '', t)
    t = re.sub(r'</ri:[^>]*>', '', t)
    t = re.sub(r'<h([1-6])[^>]*>(.*?)</h\1>',
               lambda m: '\n' + '#' * int(m.group(1)) + ' ' + m.group(2) + '\n', t)

    def _table_row(m):
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', m.group(0), re.DOTALL)
        cleaned = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
        return '| ' + ' | '.join(cleaned) + ' |'
    t = re.sub(r'<tr[^>]*>.*?</tr>', _table_row, t, flags=re.DOTALL)

    t = re.sub(r'<pre[^>]*>(.*?)</pre>',
               lambda m: '\n```\n' + re.sub(r'<[^>]+>', '', m.group(1)) + '\n```\n',
               t, flags=re.DOTALL)
    t = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', t)
    t = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', t)
    t = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', t)
    t = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', t)
    t = re.sub(r'<li[^>]*>', '\n- ', t)
    t = re.sub(r'<br\s*/?>', '\n', t)
    t = re.sub(r'<p[^>]*>', '\n', t)
    t = re.sub(r'</p>', '\n', t)
    t = re.sub(r'<img[^>]*alt="([^"]*)"[^>]*/?>',  r'[图: \1]', t)
    t = re.sub(r'<img[^>]*/?>',  '', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = html_mod.unescape(t)
    lines = [line.rstrip() for line in t.split('\n')]
    t = '\n'.join(lines)
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t.strip()


# ---------------------------------------------------------------------------
# Confluence API helpers
# ---------------------------------------------------------------------------

def fetch_page_content(client: httpx.Client, page_id: str) -> dict | None:
    """Fetch a single page, return {title, page_id, body_md, body_size} or None."""
    try:
        resp = client.get(
            f"{BASE_URL}/rest/api/content/{page_id}",
            params={"expand": "body.storage"},
            headers=_auth_headers(),
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if "statusCode" in data and data.get("statusCode") != 200:
            return None
        title = data.get("title", "")
        body_html = data.get("body", {}).get("storage", {}).get("value", "")
        body_md = html_to_markdown(body_html)
        return {
            "title": title,
            "page_id": str(page_id),
            "body_md": body_md,
            "body_size": len(body_md.encode("utf-8")),
        }
    except Exception as e:
        print(f"  [WARN] fetch page_id={page_id} failed: {e}", file=sys.stderr)
        return None


def discover_new_pages(client: httpx.Client, existing_ids: set[str]) -> list[dict]:
    """在 EGO_ROOT_PAGES 下查找尚未收录的新页面。"""
    new_pages = []
    seen = set(existing_ids)

    for root_id, root_title in EGO_ROOT_PAGES:
        start = 0
        limit = 100
        root_new = 0
        while True:
            try:
                cql = f'ancestor="{root_id}" AND type="page"'
                resp = client.get(
                    f"{BASE_URL}/rest/api/content/search",
                    params={"cql": cql, "start": start, "limit": limit},
                    headers=_auth_headers(),
                )
                if resp.status_code != 200:
                    print(f"  [WARN] discover search failed for root={root_title}: HTTP {resp.status_code}",
                          file=sys.stderr)
                    break
                data = resp.json()
                results = data.get("results", [])
                if not results:
                    break
                for r in results:
                    pid = str(r.get("id", ""))
                    if pid and pid not in seen:
                        seen.add(pid)
                        title = r.get("title", "")
                        safe_fn = re.sub(r'[\\/:*?"<>|]', '_', title) + ".md"
                        url = f"{BASE_URL}/pages/viewpage.action?pageId={pid}"
                        new_pages.append({
                            "filename": safe_fn,
                            "page_id": pid,
                            "title": title,
                            "url": url,
                        })
                        root_new += 1
                total = data.get("totalSize", data.get("size", 0))
                start += limit
                if start >= total or len(results) < limit:
                    break
            except Exception as e:
                print(f"  [WARN] discover error for root={root_title}: {e}", file=sys.stderr)
                break
        print(f"  根页面 [{root_title}] (id={root_id}): 发现 {root_new} 个新页面")

    return new_pages


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------

def is_meeting_or_low_value(filename: str) -> bool:
    if re.match(r"^\d{4}-\d{2}-\d{2}", filename):
        return True
    return any(p in filename for p in MEETING_PATTERNS)


# ---------------------------------------------------------------------------
# Index generators
# ---------------------------------------------------------------------------

def gen_kb_index(pages: list[dict], output_path: str, meetings_path: str):
    """Generate kb-index.md and kb-index-meetings.md from fetched page data."""
    tech_lines = []
    meet_lines = []

    for p in sorted(pages, key=lambda x: x.get("filename", "")):
        fn = p["filename"]
        title = p["title"]
        body = p.get("body_md", "")
        summary = _extract_summary(body)
        entry = f"- `{fn}` | **{title}**"
        if summary:
            entry += f" — {summary}"

        if is_meeting_or_low_value(fn):
            meet_lines.append(entry)
        else:
            tech_lines.append(entry)

    _write_index_file(output_path, "EGO 知识库索引（技术文档）", "技术文档",
                      tech_lines, len(tech_lines))
    _write_index_file(meetings_path, "EGO 知识库索引（会议纪要/双周报）",
                      "会议纪要与双周报", meet_lines, len(meet_lines))
    print(f"  kb-index: 技术 {len(tech_lines)} 篇, 会议 {len(meet_lines)} 篇")


def gen_heading_index(pages: list[dict], output_path: str):
    """Generate kb-heading-index.md for documents with heading structure."""
    big_docs = []
    for p in sorted(pages, key=lambda x: x.get("filename", "")):
        if is_meeting_or_low_value(p["filename"]):
            continue
        if p.get("body_size", 0) < HEADING_SIZE_THRESHOLD:
            continue
        body = p.get("body_md", "")
        headings = _extract_headings_from_md(body)
        if not headings:
            continue
        lines_count = body.count('\n') + 1
        big_docs.append({
            "filename": p["filename"],
            "size_kb": p["body_size"] / 1024,
            "lines": lines_count,
            "headings": headings,
        })

    out = [
        "# 章节级索引（大文档）",
        "",
        f"来源: Confluence 在线拉取",
        f"阈值: >= {HEADING_SIZE_THRESHOLD // 1024}KB | 文档数: {len(big_docs)}",
        "",
        "用法: 通过 Grep 搜索标题关键词 → 获取文件名 → 查 kb-confluence-map.json 获取 page_id → 在线读取",
        "",
    ]
    total_headings = 0
    for doc in big_docs:
        h = doc["headings"]
        total_headings += len(h)
        out.append(f"## `{doc['filename']}` ({doc['size_kb']:.0f}KB, {doc['lines']}行, {len(h)}节)")
        out.append("")
        if not h:
            out.append("（无标题结构）")
            out.append("")
            continue
        for line_no, heading in h:
            out.append(f"- L{line_no}: {heading}")
        out.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"  kb-heading-index: {len(big_docs)} 大文档, {total_headings} 个章节标题")


def gen_faq(pages: list[dict], output_path: str):
    """Generate kb-faq.md keyword routing index."""
    all_entries = []
    docs_ok = 0

    for p in sorted(pages, key=lambda x: x.get("filename", "")):
        if is_meeting_or_low_value(p["filename"]):
            continue
        body = p.get("body_md", "")
        if not body or len(body) < 100:
            continue
        sections = _parse_sections(body)
        if not sections:
            continue
        docs_ok += 1
        for sec in sections:
            content_text = " ".join(sec["content_lines"])
            if len(content_text) < MIN_SECTION_CHARS:
                continue
            keywords = _extract_keywords(sec["heading"], content_text)
            if not keywords:
                continue
            kw_str = " ".join(keywords[:10])
            line_range = f"L{sec['start_line']}-L{sec['end_line']}"
            all_entries.append(f"{p['filename']}|{line_range}|{kw_str}")

    header = [
        "# EGO FAQ 路由（仅定位，非答案来源）",
        f"# 覆盖 {docs_ok} 篇 | 格式: 文件名|行范围|关键词",
        "",
    ]
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(header + all_entries))
    print(f"  kb-faq: {docs_ok} 篇文档, {len(all_entries)} 条路由")


# ---------------------------------------------------------------------------
# Text extraction helpers
# ---------------------------------------------------------------------------

def _extract_summary(body_md: str) -> str:
    lines = []
    for line in body_md.split('\n'):
        s = line.strip()
        if not s or s.startswith('#') or s.startswith('![') or s.startswith('```'):
            continue
        lines.append(s)
        if len(" ".join(lines)) >= MAX_SUMMARY_CHARS:
            break
    return " ".join(lines)[:MAX_SUMMARY_CHARS]


def _extract_headings_from_md(body_md: str) -> list[tuple[int, str]]:
    headings = []
    for i, line in enumerate(body_md.split('\n'), start=1):
        if line.startswith('#') and re.match(r'^#{1,6}\s', line):
            headings.append((i, line.rstrip()))
    return headings


def _parse_sections(body_md: str) -> list[dict]:
    sections = []
    lines = body_md.split('\n')
    current = None
    for i, line in enumerate(lines, start=1):
        level = 0
        m = re.match(r'^(#{1,3})\s', line)
        if m:
            level = len(m.group(1))
        if level:
            cleaned = re.sub(r'^#+\s*', '', line).strip()
            if len(cleaned) < 3:
                continue
            if current:
                current["end_line"] = i - 1
                sections.append(current)
            current = {
                "heading": line.rstrip(),
                "heading_clean": cleaned,
                "start_line": i,
                "end_line": len(lines),
                "content_lines": [],
            }
        elif current:
            s = line.strip()
            if s and not s.startswith('!['):
                current["content_lines"].append(s)
    if current:
        current["end_line"] = len(lines)
        sections.append(current)
    return sections


def _extract_keywords(heading: str, content_start: str) -> list[str]:
    cleaned = re.sub(r'^#+\s*', '', heading).strip()
    combined = cleaned + " " + content_start[:300]
    lower_combined = combined.lower()

    seen = set()
    result = []

    def _add(kw):
        k = kw.lower() if len(kw.encode("utf-8")) == len(kw) else kw
        if k not in seen and k not in STOP_WORDS and k not in URL_NOISE:
            seen.add(k)
            result.append(k)

    for term in EGO_DOMAIN_TERMS:
        if term in lower_combined:
            _add(term)

    en_tokens = re.findall(r'[a-zA-Z][a-zA-Z0-9_-]{1,}', combined)
    for w in en_tokens:
        if len(w) > 1:
            _add(w)

    cn_text = re.sub(r'[a-zA-Z0-9_\-\s\[\]()（）#*|`>:：,，.。;；!！?？/\\]', ' ', combined)
    for w in _smart_cn_split(cn_text):
        if len(w) >= 2:
            _add(w)

    return result[:MAX_FAQ_KEYWORDS]


_CN_DOMAIN_WORDS = sorted([t for t in EGO_DOMAIN_TERMS
                           if any('\u4e00' <= c <= '\u9fff' for c in t)],
                          key=len, reverse=True)


def _smart_cn_split(text: str) -> list[str]:
    """Chinese splitting: domain terms first, then jieba or 2-gram fallback."""
    text = text.strip()
    if not text:
        return []

    tokens = []
    remaining = text

    for term in _CN_DOMAIN_WORDS:
        while term in remaining:
            tokens.append(term)
            remaining = remaining.replace(term, " ", 1)

    remaining_clean = re.sub(r'\s+', '', remaining)
    if not remaining_clean:
        return tokens

    try:
        import jieba
        jieba.setLogLevel(40)
        for t in _CN_DOMAIN_WORDS:
            jieba.add_word(t, freq=99999)
        tokens.extend(w for w in jieba.cut(remaining_clean)
                      if len(w) >= 2 and w not in STOP_WORDS)
    except ImportError:
        i = 0
        while i < len(remaining_clean):
            matched = False
            for length in (4, 3, 2):
                chunk = remaining_clean[i:i+length]
                if len(chunk) == length and chunk not in STOP_WORDS:
                    tokens.append(chunk)
                    i += length
                    matched = True
                    break
            if not matched:
                i += 1

    return tokens


def _write_index_file(path: str, title: str, section: str,
                      entries: list[str], count: int):
    lines = [
        f"# {title}",
        "",
        f"来源: Confluence 在线拉取",
        f"文档总数: {count}",
        "",
        "每条记录格式: `文件名` | 标题 | 摘要",
        "",
        f"## {section}（{count} 篇）",
        "",
    ] + entries + [""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="在线刷新 ego-qa 索引文件（从 Confluence 拉取最新内容）")
    parser.add_argument("--refs-dir", default=DEFAULT_REFS_DIR,
                        help="references 目录路径（默认: 脚本上级 references/）")
    parser.add_argument("--concurrency", type=int, default=5,
                        help="并发请求数（默认: 5）")
    parser.add_argument("--discover", action="store_true",
                        help="先从 Confluence 空间发现新页面，追加到 map")
    args = parser.parse_args()

    refs_dir = os.path.abspath(args.refs_dir)
    map_path = os.path.join(refs_dir, "kb-confluence-map.json")

    if not os.path.isfile(map_path):
        print(f"错误：找不到 {map_path}", file=sys.stderr)
        sys.exit(1)

    with open(map_path, "r", encoding="utf-8") as f:
        page_map: list[dict] = json.load(f)
    print(f"已加载 {len(page_map)} 个页面映射")

    # --- Discover new pages (only under EGO root pages) ---
    if args.discover:
        roots_desc = ", ".join(f"{t}(id={i})" for i, t in EGO_ROOT_PAGES)
        print(f"正在两个 EGO 根页面下发现新页面: {roots_desc}")
        existing_ids = {p["page_id"] for p in page_map}
        with _client() as client:
            new_pages = discover_new_pages(client, existing_ids)
        if new_pages:
            print(f"  共发现 {len(new_pages)} 个新页面，追加到 map")
            page_map.extend(new_pages)
            page_map.sort(key=lambda x: x.get("filename", ""))
            with open(map_path, "w", encoding="utf-8") as f:
                json.dump(page_map, f, ensure_ascii=False, indent=2)
            print(f"  map 已更新: {len(page_map)} 个页面")
        else:
            print("  未发现新页面")

    # --- Fetch all pages ---
    print(f"正在拉取 {len(page_map)} 个页面内容（并发={args.concurrency}）...")
    t0 = time.time()
    fetched = []
    failed = 0

    max_retries = 3

    def _fetch_one(entry):
        for attempt in range(max_retries):
            try:
                with _client() as c:
                    result = fetch_page_content(c, entry["page_id"])
                if result:
                    result["filename"] = entry.get("filename", "")
                    return result
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))
            except Exception:
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))
        return None

    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {pool.submit(_fetch_one, e): e for e in page_map}
        for i, fut in enumerate(as_completed(futures), 1):
            result = fut.result()
            if result:
                fetched.append(result)
            else:
                failed += 1
                entry = futures[fut]
                print(f"  [SKIP] {entry.get('filename', entry.get('page_id', '?'))}")
            if i % 50 == 0:
                print(f"  进度: {i}/{len(page_map)}")

    elapsed = time.time() - t0
    print(f"拉取完成: {len(fetched)} 成功, {failed} 失败, 耗时 {elapsed:.1f}s")

    # --- Generate indexes ---
    print("正在生成索引文件...")

    index_path = os.path.join(refs_dir, "kb-index.md")
    meetings_path = os.path.join(refs_dir, "kb-index-meetings.md")
    heading_path = os.path.join(refs_dir, "kb-heading-index.md")
    faq_path = os.path.join(refs_dir, "kb-faq.md")

    gen_kb_index(fetched, index_path, meetings_path)
    gen_heading_index(fetched, heading_path)
    gen_faq(fetched, faq_path)

    print("\n全部完成！索引文件已更新:")
    for p in [index_path, meetings_path, heading_path, faq_path]:
        size = os.path.getsize(p) / 1024
        print(f"  {os.path.basename(p)}: {size:.1f}KB")


if __name__ == "__main__":
    main()
