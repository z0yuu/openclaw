#!/usr/bin/env python3
"""
Ego FAQ 检索：根据关键词定位到「具体问题」，仅返回与该问题相关的内容，或返回空。
切忌返回完整 FAQ 页面。

匹配规则：不要求完全精确匹配，大概意思一样即算匹配（可选 rapidfuzz）；最多返回 3 条。
页面结构：Ego FAQ 主页面为目录，列出每个问题（Q1. Q2. Q12. ...）；每个问题下为
  直接解答，或包含用于继续阅读的 link。
逻辑：用关键词定位到哪个问题 → 只返回该问题在 FAQ 根页中的相关内容；
  若未匹配到任何问题则返回空。
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request

try:
    import html2text
except ImportError:
    html2text = None

try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

CONFLUENCE_SPACE = "MLP"
CONFLUENCE_ROOT_TITLE = "Ego FAQ"
CONFLUENCE_BASE_URL = "https://confluence.shopee.io"
MAX_RESULTS = 3  # 最多返回 3 条
FUZZY_THRESHOLD = 35  # 模糊匹配阈值（0-100），降低以提高中文/短 query 召回
FUZZY_THRESHOLD_PARTIAL = 45  # partial_ratio 阈值，用于短句
FILE_LOCATE_TUTORIAL_PAGE_ID = "2668250345"

# 新问题块起始：行首的 Q数字.
RE_QUESTION_START = re.compile(r"\n(?=Q\d+\.)", re.IGNORECASE)
# Confluence FAQ 标题：h1–h6 且 id 以 EgoFAQ-Q 开头，或文本以 Q数字. / Q数字: / Q数字： 开头（含全角冒号）
RE_Q_HEADING_ID = re.compile(r"EgoFAQ-Q\d+[.:：]", re.I)
RE_Q_HEADING_TEXT = re.compile(r"^Q\d+[.:：]\s*", re.I)
def get_body_html(page: dict) -> str:
    body = page.get("body") or {}
    if isinstance(body, dict):
        return (body.get("storage") or body.get("view") or {}).get("value") or ""
    return ""


def load_local_faq_html(filepath: str) -> str:
    """
    从本地保存的 Ego FAQ 页面（如浏览器另存为）中还原可解析的 HTML。
    支持：(1) 整文件即 HTML；(2) 源码被拆成多个 td.line-content 的包装格式，拼接各 cell 文本得到 HTML。
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
    except OSError:
        return ""
    if HAS_BS4 and "line-content" in raw:
        soup = BeautifulSoup(raw, "html.parser")
        cells = soup.select("td.line-content")
        if cells:
            # 拼接各 cell 的文本即还原为一行行 HTML 源码，合起来即完整文档
            raw = "".join(c.get_text() for c in cells)
    if not raw.strip().startswith("<") and "<" not in raw[:500]:
        return ""
    if HAS_BS4:
        soup = BeautifulSoup(raw, "html.parser")
        for selector in (".wiki-content", "#main-content", "article"):
            el = soup.select_one(selector)
            if el and "EgoFAQ-Q" in str(el):
                return el.decode_contents() if hasattr(el, "decode_contents") else str(el)
        body = soup.find("body")
        if body:
            return body.decode_contents() if hasattr(body, "decode_contents") else str(body)
    return raw


def html_to_text(html: str) -> str:
    if not html:
        return ""
    if html2text:
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.body_width = 0
        return h.handle(html)
    return re.sub(r"<[^>]+>", " ", html).strip()


def parse_question_blocks(full_text: str) -> list[tuple[str, str]]:
    """Split page text into (question_title, content) blocks. Each block starts with Q#."""
    blocks = []
    # 按「行首 Q数字.」切分，第一段可能是标题等，从 Q 开头的段开始算
    parts = RE_QUESTION_START.split(full_text)
    for part in parts:
        part = part.strip()
        if not part or len(part) < 4:
            continue
        lines = part.split("\n")
        first_line = lines[0].strip()
        if not re.match(r"Q\d+\.", first_line, re.I):
            continue
        rest = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
        blocks.append((first_line, rest))
    return blocks


def parse_faq_blocks_from_html(html: str) -> list[tuple[str, str]]:
    """
    按 Ego FAQ 页面真实结构解析：Confluence 使用 <h3 id="EgoFAQ-Q1....">Q1. ...</h3>
    后跟 <p>、<ul> 等作为解答。不依赖换行，直接按 HTML 标题切块。
    """
    if not HAS_BS4 or not html or not html.strip():
        return []
    soup = BeautifulSoup(html, "html.parser")
    blocks = []
    # 所有可能作为问题标题的节点（按文档顺序）
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        title_text = tag.get_text(separator=" ", strip=True)
        if not title_text:
            continue
        # 匹配：id 含 EgoFAQ-Q数字. 或 文本以 Q数字. 开头
        tag_id = (tag.get("id") or "").strip()
        if RE_Q_HEADING_ID.search(tag_id) or RE_Q_HEADING_TEXT.match(title_text):
            # 收集该标题之后、下一个 Q 标题之前的所有兄弟节点
            content_parts = []
            for sib in tag.find_next_siblings():
                if sib.name and sib.name.lower() in ("h1", "h2", "h3", "h4", "h5", "h6"):
                    sib_text = sib.get_text(separator=" ", strip=True)
                    if RE_Q_HEADING_TEXT.match(sib_text) or RE_Q_HEADING_ID.search(sib.get("id") or ""):
                        break
                if hasattr(sib, "get_text"):
                    text = sib.get_text(separator="\n", strip=True)
                    content_parts.append(text)
                else:
                    content_parts.append(str(sib))
            content = "\n".join(p for p in content_parts if p).strip()
            blocks.append((title_text, content))
    return blocks


def parse_fallback_sections(full_text: str, min_len: int = 30) -> list[tuple[str, str]]:
    """当 FAQ 页不是 Q1. Q2. 结构时，按段落或标题切分，便于按关键词召回。"""
    sections = []
    # 按双换行或 Confluence 标题行（如 "h1." "h2." "* " 等）切段
    parts = re.split(r"\n\s*\n+", full_text)
    for i, part in enumerate(parts):
        part = part.strip()
        if len(part) < min_len:
            continue
        lines = part.split("\n")
        first_line = lines[0].strip() if lines else ""
        rest = "\n".join(lines[1:]).strip() if len(lines) > 1 else part
        title = first_line[:80] if first_line else f"Section {i+1}"
        sections.append((title, rest or part))
    return sections


def keyword_chars_in_order(keyword: str, text: str) -> bool:
    """关键词中的字符是否在 text 中按顺序出现（允许中间有间隔），用于中文/变体匹配。"""
    if not keyword or not text:
        return False
    text_lower = text.lower()
    pos = 0
    for ch in keyword.lower():
        idx = text_lower.find(ch, pos)
        if idx == -1:
            return False
        pos = idx + 1
    return True


def block_matches_keywords(block_text: str, keywords: list[str]) -> bool:
    """精确/子串匹配 或 按字符顺序包含（中文友好）：任一关键词匹配即视为命中。"""
    if not keywords or not block_text:
        return False
    # 1) 精确或子串
    pattern = re.compile("|".join(re.escape(k) for k in keywords), re.I)
    if pattern.search(block_text):
        return True
    # 2) 中文/变体：关键词各字符在块中按顺序出现（如 "GPU显存不足" 匹配 "GPU 显存 不足"）
    for k in keywords:
        if len(k) >= 2 and keyword_chars_in_order(k, block_text):
            return True
    return False


def block_fuzzy_score(block_text: str, query: str) -> int:
    """模糊匹配得分 0-100；短 query 用 partial_ratio 提高召回。"""
    if not query or not block_text:
        return 0
    if not HAS_RAPIDFUZZ:
        return 0
    sample = block_text[:3000]
    # 短句或中文：partial_ratio 更宽松，子串相似即可
    if len(query) <= 20 or any("\u4e00" <= c <= "\u9fff" for c in query):
        score = fuzz.partial_ratio(query, sample)
        if score >= FUZZY_THRESHOLD_PARTIAL:
            return score
    return fuzz.token_set_ratio(query, sample)


def _title_keyword_score(title: str, keywords: list[str]) -> int:
    """标题中命中的关键词越多，加分越多。"""
    if not keywords or not title:
        return 0
    title_lower = title.lower()
    hit = sum(1 for k in keywords if k.lower() in title_lower or keyword_chars_in_order(k, title))
    return hit * 15


def _has_keyword_in_title(title: str, keywords: list[str]) -> bool:
    """标题中是否至少命中一个关键词（用于「只返回标题相关」过滤）。"""
    if not keywords or not title:
        return False
    return any(
        k.lower() in title.lower() or keyword_chars_in_order(k, title)
        for k in keywords
    )


# 仅正文命中时要求更高的模糊分，避免无关条目凑数
FUZZY_THRESHOLD_CONTENT_ONLY = 65


def select_matched_blocks(
    blocks: list[tuple[str, str]], keywords: list[str], max_n: int = MAX_RESULTS
) -> list[tuple[str, str]]:
    """
    筛选匹配块：优先返回标题含关键词的条目；不凑数，无关的不列。
    - 若有任一块标题含关键词，则只返回标题含关键词的块。
    - 仅正文命中时需达到更高模糊分，否则不列入。
    """
    query = " ".join(keywords)
    scored = []
    for q_title, content in blocks:
        block_full = f"{q_title}\n{content}"
        in_title = _has_keyword_in_title(q_title, keywords)
        if block_matches_keywords(block_full, keywords):
            score = 100 + _title_keyword_score(q_title, keywords)
            scored.append((score, q_title, content, in_title))
            continue
        score = block_fuzzy_score(block_full, query)
        # 仅正文命中时门槛提高，避免无关条目
        if score >= FUZZY_THRESHOLD_CONTENT_ONLY:
            score = score + _title_keyword_score(q_title, keywords)
            scored.append((score, q_title, content, in_title))
    if not scored:
        return []
    # 若存在标题命中的块，只保留标题命中的，不返回「正文提到但标题无关」的块
    title_hits = [x for x in scored if x[3]]
    if title_hits:
        scored = title_hits
    scored.sort(key=lambda x: -x[0])
    return [(q, c) for _, q, c, _ in scored[:max_n]]


def should_route_to_file_locate_tutorial(keywords: list[str]) -> bool:
    """需要走“定位具体报错文件”FAQ 教程的场景识别。"""
    if not keywords:
        return False
    text = " ".join(keywords).lower()
    signals = [
        "报错文件",
        "定位文件",
        "定位报错",
        "parquet_row_group",
        "parquet",
        "python converter",
        "cpp-data-converter",
        "converter",
        "pipeline failed",
    ]
    return any(s in text for s in signals)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ego FAQ: 按关键词定位到具体问题，仅返回该问题相关内容，或空。"
    )
    parser.add_argument("keywords", nargs="*", help="一个或多个关键词")
    parser.add_argument("--query", type=str, help="空格分隔关键词")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="打印解析到的块数、是否走 fallback 等")
    parser.add_argument("--local-file", type=str, metavar="PATH", help="使用本地保存的 FAQ 页面 HTML，不请求 Confluence API")
    args = parser.parse_args()
    keywords = list(args.keywords) if args.keywords else []
    if args.query:
        keywords.extend(args.query.strip().split())
    keywords = [k.strip() for k in keywords if k.strip()]
    if not keywords:
        print("Usage: search_ego_faq.py KEYWORD [KEYWORD ...] or --query 'kw1 kw2'", file=sys.stderr)
        return 1

    root_html = ""
    if args.local_file:
        root_html = load_local_faq_html(args.local_file)
        if not root_html:
            print(f"Error: Could not load or parse local file: {args.local_file}", file=sys.stderr)
            return 1
    else:
        token = os.environ.get("CONFLUENCE_TOKEN")
        if not token:
            print("Error: Set CONFLUENCE_TOKEN.", file=sys.stderr)
            return 1
        try:
            url = (
                f"{CONFLUENCE_BASE_URL}/rest/api/content?"
                f"spaceKey={urllib.parse.quote(CONFLUENCE_SPACE)}&"
                f"title={urllib.parse.quote(CONFLUENCE_ROOT_TITLE)}&"
                "expand=body.storage"
            )
            req = urllib.request.Request(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = json.loads(resp.read().decode("utf-8", errors="replace"))
        except Exception as e:
            print(f"Error getting Ego FAQ page: {e}", file=sys.stderr)
            return 1
        results = payload.get("results") or []
        root = results[0] if results else None
        if not root:
            if args.json:
                print('{"results": []}')
            else:
                print("")
            return 0
        root_html = get_body_html(root)

    root_text = html_to_text(root_html)
    # 优先按 Confluence 真实 HTML 结构解析（h3 id="EgoFAQ-Q1..." 等），否则再按纯文本 Q 块
    blocks = parse_faq_blocks_from_html(root_html)
    if not blocks:
        blocks = parse_question_blocks(root_text)

    # 匹配：精确/子串命中 或 模糊匹配（大概意思一样），最多 3 条
    matched_blocks = select_matched_blocks(blocks, keywords, max_n=MAX_RESULTS)

    # 若无 Q 块或无一命中：按整页段落做 fallback 检索
    fallback_sections = parse_fallback_sections(root_text)
    used_fallback = False
    if not matched_blocks and fallback_sections:
        matched_blocks = select_matched_blocks(fallback_sections, keywords, max_n=MAX_RESULTS)
        used_fallback = bool(matched_blocks)
    if args.verbose:
        print(f"[verbose] FAQ 页 Q 块数: {len(blocks)}, fallback 段数: {len(fallback_sections)}, 命中: {len(matched_blocks)}, 使用 fallback: {used_fallback}", file=sys.stderr)

    route_file_locate_tutorial = should_route_to_file_locate_tutorial(keywords)
    if not matched_blocks and route_file_locate_tutorial:
        tutorial_url = (
            f"{CONFLUENCE_BASE_URL}/pages/viewpage.action?pageId={FILE_LOCATE_TUTORIAL_PAGE_ID}"
        )
        matched_blocks = [
            (
                "[报错文件定位教程]",
                "建议按该教程定位具体报错文件：\n" + tutorial_url,
            )
        ]

    if not matched_blocks:
        if args.json:
            print('{"results": []}')
        else:
            print("")
        return 0

    results = []
    for q_title, content in matched_blocks:
        answer_content = content.strip()
        one = {
            "question": q_title,
            "content": answer_content[:12000],
        }
        results.append(one)

    if args.json:
        print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
        return 0

    for r in results:
        print(f"## {r['question']}\n")
        print(r["content"])
        print("\n---\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
