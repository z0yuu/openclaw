#!/usr/bin/env python3
"""Fetch one Confluence page and return normalized text/json content.

Auth source:
- CONFLUENCE_TOKEN (Bearer)

Usage examples:
  python scripts/get_confluence.py --page-id 123456 --json
  python scripts/get_confluence.py --url "https://confluence.shopee.io/display/MLP/How+to+clip+or+map+nn+parameters"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from getpass import getpass
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen
from typing import Any, Dict, Optional

try:
    import html2text
except ImportError:
    html2text = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

CONFLUENCE_BASE_URL = "https://confluence.shopee.io"


def _html_to_text(html: str) -> str:
    if not html:
        return ""
    if html2text:
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.body_width = 0
        return h.handle(html).strip()
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()


def _extract_storage_html(page: Dict[str, Any]) -> str:
    body = page.get("body") or {}
    if not isinstance(body, dict):
        return ""
    storage = body.get("storage") or {}
    if isinstance(storage, dict):
        return storage.get("value") or ""
    return ""


def _extract_title_from_url(url: str) -> Optional[str]:
    m = re.search(r"/display/[^/]+/([^?#]+)", url)
    if not m:
        return None
    raw = m.group(1).replace("+", " ")
    try:
        from urllib.parse import unquote

        return unquote(raw)
    except Exception:
        return raw


def _extract_page_id_from_url(url: str) -> Optional[str]:
    m = re.search(r"pageId=(\d+)", url)
    return m.group(1) if m else None


def _normalize_base_url(base_url: str) -> str:
    parsed = urlparse(base_url)
    if not parsed.scheme or not parsed.netloc:
        raise RuntimeError(f"invalid --base-url: {base_url}")
    return f"{parsed.scheme}://{parsed.netloc}"


def _build_auth_headers() -> Dict[str, str]:
    token = os.environ.get("CONFLUENCE_TOKEN", "").strip()
    if not token:
        # Block and wait for user input instead of failing immediately.
        while not token:
            try:
                token = getpass("CONFLUENCE_TOKEN not set. Please input token: ").strip()
            except (EOFError, KeyboardInterrupt) as err:
                raise RuntimeError("CONFLUENCE_TOKEN is required") from err
    return {"Authorization": f"Bearer {token}"}


def _http_get_json(url: str, headers: Dict[str, str]) -> Dict[str, Any]:
    req_headers = {"Accept": "application/json", **headers}
    req = Request(url=url, headers=req_headers, method="GET")
    try:
        with urlopen(req, timeout=30) as resp:
            data = resp.read().decode("utf-8")
    except HTTPError as err:
        body = err.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {err.code} for {url}: {body[:400]}") from err
    except URLError as err:
        raise RuntimeError(f"request failed for {url}: {err}") from err
    try:
        return json.loads(data)
    except json.JSONDecodeError as err:
        raise RuntimeError(f"invalid json response from {url}") from err


def _get_page_by_id(base_url: str, page_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
    expand = "body.storage,version,_links"
    pid = quote(str(page_id), safe="")
    url = f"{base_url}/rest/api/content/{pid}?{urlencode({'expand': expand})}"
    page = _http_get_json(url, headers)
    if not page or not isinstance(page, dict) or not page.get("id"):
        raise RuntimeError(f"page not found by id: {page_id}")
    return page


def _get_page_by_title(base_url: str, space: str, title: str, headers: Dict[str, str]) -> Dict[str, Any]:
    expand = "body.storage,version,_links"
    params = {
        "spaceKey": space,
        "title": title,
        "expand": expand,
        "limit": 5,
    }
    url = f"{base_url}/rest/api/content?{urlencode(params)}"
    payload = _http_get_json(url, headers)
    results = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(results, list) or not results:
        raise RuntimeError(f"page not found by title: {title}")
    exact = next((p for p in results if p.get("title") == title), None)
    return exact or results[0]


def _get_page(base_url: str, headers: Dict[str, str], page_id: Optional[str], title: Optional[str], space: str) -> Dict[str, Any]:
    if page_id:
        return _get_page_by_id(base_url, page_id, headers)
    if title:
        return _get_page_by_title(base_url, space, title, headers)
    raise RuntimeError("one of --page-id / --title / --url is required")


def _build_page_url(base_url: str, page: Dict[str, Any]) -> str:
    links = page.get("_links") or {}
    if not isinstance(links, dict):
        return base_url
    webui = links.get("webui")
    if isinstance(webui, str) and webui:
        if webui.startswith("http://") or webui.startswith("https://"):
            return webui
        return f"{base_url}{webui}"
    return base_url


def _strip_html_text_with_bs4(html: str) -> str:
    if not BeautifulSoup:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    # Prefer main wiki content if present.
    node = soup.select_one(".wiki-content")
    if node is not None:
        return node.get_text("\n", strip=True)
    return soup.get_text("\n", strip=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Confluence page content")
    parser.add_argument("--base-url", default=CONFLUENCE_BASE_URL)
    parser.add_argument("--space", default="MLP")
    parser.add_argument("--page-id")
    parser.add_argument("--title")
    parser.add_argument("--url")
    parser.add_argument("--max-chars", type=int, default=0)
    parser.add_argument("--json", action="store_true", help="print json output")
    parser.add_argument("--output", help="optional output file path")
    args = parser.parse_args()

    page_id = args.page_id
    title = args.title
    if args.url:
        page_id = page_id or _extract_page_id_from_url(args.url)
        title = title or _extract_title_from_url(args.url)

    try:
        base_url = _normalize_base_url(args.base_url)
        headers = _build_auth_headers()
        page = _get_page(base_url, headers, page_id=page_id, title=title, space=args.space)
        html = _extract_storage_html(page)
        text = _strip_html_text_with_bs4(html) or _html_to_text(html)
        if args.max_chars and args.max_chars > 0:
            text = text[: args.max_chars]

        result = {
            "ok": True,
            "id": page.get("id"),
            "title": page.get("title"),
            "url": _build_page_url(base_url, page),
            "text": text,
        }
    except Exception as exc:
        result = {"ok": False, "error": str(exc)}

    output = json.dumps(result, ensure_ascii=False, indent=2) if args.json else result.get("text", "")
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
            if args.json:
                f.write("\n")
    else:
        print(output)

    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
