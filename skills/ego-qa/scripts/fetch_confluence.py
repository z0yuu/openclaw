#!/usr/bin/env python3
"""Confluence CLI — 通过 REST API 获取 Confluence 页面内容，替代 MCP 服务。

用法:
  python fetch_confluence.py get_page --page_id 2664613148 [--max_chars 8000]
  python fetch_confluence.py get_page --title "GPU任务调优指南"
  python fetch_confluence.py search --query "OOM" [--limit 5]

认证（按优先级）:
  CONFLUENCE_TOKEN            — Personal Access Token（若提供则优先使用）
  CONFLUENCE_USERNAME/PASSWORD — 用户名密码（可按 page_id 读取页面）
"""

import argparse
import base64
import html as html_mod
import os
import re
import ssl
import sys

import httpx

BASE_URL = os.environ.get("CONFLUENCE_BASE_URL", "https://confluence.shopee.io")
SPACE_KEY = os.environ.get("CONFLUENCE_SPACE_KEY", "MLP")

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


def _auth_headers():
    token = os.environ.get("CONFLUENCE_TOKEN", "")
    if token:
        return {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    username = os.environ.get("CONFLUENCE_USERNAME", "")
    password = os.environ.get("CONFLUENCE_PASSWORD", "")
    if username and password:
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        return {"Accept": "application/json", "Authorization": f"Basic {credentials}"}
    print("错误：未设置 CONFLUENCE_TOKEN 或 CONFLUENCE_USERNAME/CONFLUENCE_PASSWORD。",
          file=sys.stderr)
    sys.exit(1)


def html_to_markdown(raw_html: str) -> str:
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
               lambda m: '\n```\n' + re.sub(r'<[^>]+>', '', m.group(1)) + '\n```\n', t, flags=re.DOTALL)
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


def get_page(page_id=None, title=None, max_chars=8000):
    with httpx.Client(timeout=30, verify=_ssl_ctx) as client:
        if page_id:
            resp = client.get(
                f"{BASE_URL}/rest/api/content/{page_id}",
                params={"expand": "body.storage"},
                headers=_auth_headers(),
            )
        elif title:
            resp = client.get(
                f"{BASE_URL}/rest/api/content",
                params={"title": title, "spaceKey": SPACE_KEY,
                        "expand": "body.storage", "limit": 1},
                headers=_auth_headers(),
            )
        else:
            return "错误：page_id 和 title 至少提供一个。"

        if resp.status_code == 401:
            return "错误：认证失败，请检查 CONFLUENCE_TOKEN 或 CONFLUENCE_USERNAME/PASSWORD。"
        if resp.status_code == 404:
            return f"错误：页面未找到（page_id={page_id}, title={title}）。"
        if resp.status_code != 200:
            return f"错误：API 返回 {resp.status_code}"

        data = resp.json()
        if page_id:
            page = data
        else:
            results = data.get("results", [])
            if not results:
                return f"错误：未找到标题为 '{title}' 的页面。"
            page = results[0]

        ptitle = page.get("title", "Unknown")
        pid = page.get("id", "")
        body_html = page.get("body", {}).get("storage", {}).get("value", "")
        url = f"{BASE_URL}/pages/viewpage.action?pageId={pid}"

        content = html_to_markdown(body_html)
        if max_chars and len(content) > max_chars:
            content = content[:max_chars] + f"\n\n... (截断，已显示前 {max_chars} 字符)"

        return f"# {ptitle}\n\n> 来源: [{ptitle}]({url})\n\n{content}"


def search_pages(query, limit=5):
    cql = f'space="{SPACE_KEY}" AND (title~"{query}" OR text~"{query}")'
    with httpx.Client(timeout=30, verify=_ssl_ctx) as client:
        resp = client.get(
            f"{BASE_URL}/rest/api/content/search",
            params={"cql": cql, "limit": limit},
            headers=_auth_headers(),
        )
        if resp.status_code != 200:
            return f"错误：搜索失败，API 返回 {resp.status_code}"

        results = resp.json().get("results", [])
        if not results:
            return f"未找到与 '{query}' 相关的页面。"

        lines = [f"搜索 '{query}' 找到 {len(results)} 个结果：\n"]
        for r in results:
            pid = r.get("id", "")
            t = r.get("title", "")
            lines.append(f"- **{t}** (pageId: {pid})")
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Confluence CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_get = sub.add_parser("get_page", help="获取页面内容")
    p_get.add_argument("--page_id", default=None)
    p_get.add_argument("--title", default=None)
    p_get.add_argument("--max_chars", type=int, default=8000)

    p_search = sub.add_parser("search", help="搜索页面")
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--limit", type=int, default=5)

    args = parser.parse_args()

    if args.command == "get_page":
        print(get_page(args.page_id, args.title, args.max_chars))
    elif args.command == "search":
        print(search_pages(args.query, args.limit))


if __name__ == "__main__":
    main()
