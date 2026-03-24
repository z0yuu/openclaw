#!/usr/bin/env python3
"""
Researcher profile lookup via Google Scholar, Semantic Scholar, and OpenAlex.

Usage:
  python researcher_profile.py "Yann LeCun"
  python researcher_profile.py "Yann LeCun" --org "New York University"
  python researcher_profile.py "Yann LeCun" --scholar-url "https://scholar.google.com/citations?user=WLN3QrAAAAAJ"

Output: JSON profile to stdout.
"""

import argparse
import json
import re
import sys
from collections import Counter
from typing import Any
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

_UA = "Mozilla/5.0 (compatible; openclaw-arxiv-skill/1.0)"


def _http_get_json(url: str, timeout: int = 15) -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": _UA})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="ignore"))


def _http_get_text(url: str, timeout: int = 15) -> str:
    req = Request(url, headers={"User-Agent": _UA})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def _norm_text(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def _scholar_user_id(url: str) -> str:
    m = re.search(r"[?&]user=([A-Za-z0-9_\-]+)", url)
    return m.group(1) if m else ""


def _canonical_scholar_url(url: str) -> str:
    user = _scholar_user_id(url)
    return f"https://scholar.google.com/citations?hl=en&user={user}" if user else url


def _parse_scholar_profile(scholar_url: str) -> dict[str, Any]:
    try:
        html = _http_get_text(scholar_url)
    except Exception:
        return {"name": "", "affiliation": "", "interests": [], "top_cited": []}

    def _first(pattern: str) -> str:
        m = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""

    name = _first(r'id="gsc_prf_in"[^>]*>([^<]+)<')
    affiliation = _first(r'class="gsc_prf_il"[^>]*>([^<]+)<')
    interests = re.findall(r'class="gsc_prf_inta[^"]*"[^>]*>([^<]+)<', html, flags=re.IGNORECASE)
    interests = [re.sub(r"\s+", " ", x).strip() for x in interests if x.strip()][:10]
    coauthors = re.findall(
        r'class="gsc_rsb_a_desc"[\s\S]*?<a[^>]*>([^<]+)</a>', html, flags=re.IGNORECASE
    )
    coauthors = [re.sub(r"\s+", " ", x).strip() for x in coauthors if x.strip()]

    rows = re.findall(
        r'class="gsc_a_tr"[^>]*>.*?class="gsc_a_at"[^>]*>([^<]+)<.*?class="gsc_a_c"[^>]*>(?:<a[^>]*>)?([^<]*)(?:</a>)?</td>.*?class="gsc_a_y"[^>]*>(?:<span[^>]*>)?([^<]*)(?:</span>)?</td>',
        html, flags=re.IGNORECASE | re.DOTALL,
    )
    top_cited = []
    for title, cited, year in rows[:5]:
        top_cited.append({
            "title": re.sub(r"\s+", " ", title).strip(),
            "year": (year or "").strip() or "n/a",
            "citations": (cited or "0").strip() or "0",
        })

    return {
        "name": name,
        "affiliation": affiliation,
        "interests": interests,
        "coauthors": coauthors,
        "top_cited": top_cited,
    }


def _parse_scholar_works(html: str) -> list[dict[str, str]]:
    works = []
    rows = re.findall(r'(<tr class="gsc_a_tr"[\s\S]*?</tr>)', html, flags=re.IGNORECASE)
    for row in rows:
        title_m = re.search(r'class="gsc_a_at"[^>]*>([^<]+)<', row, flags=re.IGNORECASE)
        if not title_m:
            continue
        title = re.sub(r"\s+", " ", title_m.group(1)).strip()
        meta = re.findall(r'class="gs_gray"[^>]*>([^<]*)<', row, flags=re.IGNORECASE)
        authors = re.sub(r"\s+", " ", meta[0]).strip() if len(meta) >= 1 else ""
        venue = re.sub(r"\s+", " ", meta[1]).strip() if len(meta) >= 2 else ""
        cited_m = re.search(r'class="gsc_a_c"[^>]*>(?:<a[^>]*>)?([^<]*)(?:</a>)?</td>', row, flags=re.IGNORECASE)
        year_m = re.search(r'class="gsc_a_y"[^>]*>(?:<span[^>]*>)?([^<]*)(?:</span>)?</td>', row, flags=re.IGNORECASE)
        works.append({
            "title": title,
            "authors": authors,
            "venue": venue,
            "year": (year_m.group(1).strip() if year_m else "") or "n/a",
            "citations": (cited_m.group(1).strip() if cited_m else "") or "0",
        })
    return works


def _fetch_scholar_works(scholar_url: str) -> tuple[list[dict], list[dict]]:
    user = _scholar_user_id(scholar_url)
    if not user:
        return [], []
    base = f"https://scholar.google.com/citations?hl=en&user={user}"
    cited_html = _http_get_text(base)
    cited_works = _parse_scholar_works(cited_html)
    recent_url = f"{base}&view_op=list_works&sortby=pubdate"
    recent_html = _http_get_text(recent_url)
    recent_works = _parse_scholar_works(recent_html)
    if not recent_works:
        recent_works = sorted(cited_works, key=lambda w: int(w["year"]) if w["year"].isdigit() else -1, reverse=True)
    if not cited_works:
        cited_works = sorted(recent_works, key=lambda w: int(w["citations"]) if w["citations"].isdigit() else 0, reverse=True)
    return recent_works, cited_works


def _scholar_search_profile(name: str, organization: str | None = None) -> str | None:
    query = name.strip()
    if organization:
        query = f"{query} {organization}"
    url = f"https://scholar.google.com/citations?view_op=search_authors&mauthors={quote_plus(query)}"
    try:
        html = _http_get_text(url)
    except Exception:
        return None

    name_norm = _norm_text(name)
    blocks = re.findall(r'(<div class="gsc_1usr"[\s\S]*?</div>\s*</div>)', html, flags=re.IGNORECASE)
    candidates = []
    for block in blocks:
        href_match = re.search(r'href="(/citations\?user=[^"&]+[^"]*)"', block, flags=re.IGNORECASE)
        if not href_match:
            continue
        full_url = "https://scholar.google.com" + href_match.group(1)
        n_match = re.search(r'class="gsc_1usr_name"[^>]*>\s*<a[^>]*>([^<]+)<', block, flags=re.IGNORECASE)
        cand_name_norm = _norm_text(n_match.group(1) if n_match else "")
        score = 10 if cand_name_norm == name_norm else (6 if name_norm in cand_name_norm else 0)
        if organization:
            aff_match = re.search(r'class="gsc_1usr_aff"[^>]*>([^<]+)<', block, flags=re.IGNORECASE)
            if aff_match and _norm_text(organization) in _norm_text(aff_match.group(1)):
                score += 10
        if score > 0:
            candidates.append((score, full_url))

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]
    return None


def _semantic_scholar_search(name: str) -> dict[str, Any] | None:
    url = f"https://api.semanticscholar.org/graph/v1/author/search?query={quote_plus(name)}&limit=3&fields=name,affiliations,paperCount,citationCount,hIndex"
    try:
        data = _http_get_json(url, timeout=12)
    except Exception:
        return None
    rows = data.get("data") or []
    name_norm = _norm_text(name)
    for r in rows:
        if _norm_text(r.get("name", "")) == name_norm:
            return r
    return rows[0] if rows else None


def build_profile(name: str, organization: str | None = None, scholar_url: str | None = None) -> dict[str, Any]:
    if not scholar_url:
        scholar_url = _scholar_search_profile(name, organization)
        if not scholar_url:
            scholar_url = _scholar_search_profile(name, None)

    profile: dict[str, Any] = {
        "name": name,
        "organization": organization or "",
        "google_scholar_url": None,
        "interests": [],
        "top_recent": [],
        "top_cited": [],
        "coauthors": [],
        "semantic_scholar": None,
    }

    if scholar_url:
        profile["google_scholar_url"] = _canonical_scholar_url(scholar_url)
        meta = _parse_scholar_profile(scholar_url)
        profile["name"] = meta.get("name") or name
        profile["organization"] = meta.get("affiliation") or organization or ""
        profile["interests"] = meta.get("interests", [])
        profile["coauthors"] = meta.get("coauthors", [])
        profile["top_cited"] = meta.get("top_cited", [])
        recent, _ = _fetch_scholar_works(scholar_url)
        profile["top_recent"] = recent[:5]

    ss = _semantic_scholar_search(name)
    if ss:
        profile["semantic_scholar"] = {
            "name": ss.get("name"),
            "paper_count": ss.get("paperCount"),
            "citation_count": ss.get("citationCount"),
            "h_index": ss.get("hIndex"),
        }

    return profile


def format_profile(p: dict) -> str:
    lines = [f"# {p['name']}"]
    if p.get("organization"):
        lines.append(f"**Affiliation:** {p['organization']}")
    if p.get("google_scholar_url"):
        lines.append(f"**Google Scholar:** {p['google_scholar_url']}")
    if p.get("interests"):
        lines.append(f"**Research Interests:** {', '.join(p['interests'])}")

    ss = p.get("semantic_scholar")
    if ss:
        lines.append(f"\n## Semantic Scholar Stats")
        lines.append(f"- Papers: {ss.get('paper_count', 'N/A')}")
        lines.append(f"- Citations: {ss.get('citation_count', 'N/A')}")
        lines.append(f"- h-index: {ss.get('h_index', 'N/A')}")

    if p.get("top_cited"):
        lines.append("\n## Top Cited Papers")
        for i, w in enumerate(p["top_cited"][:5], 1):
            lines.append(f"{i}. **{w['title']}** ({w.get('year', 'n/a')}) — cited {w.get('citations', '?')} times")

    if p.get("top_recent"):
        lines.append("\n## Recent Papers")
        for i, w in enumerate(p["top_recent"][:5], 1):
            lines.append(f"{i}. **{w['title']}** ({w.get('year', 'n/a')})")

    if p.get("coauthors"):
        lines.append(f"\n## Frequent Coauthors")
        lines.append(", ".join(p["coauthors"][:8]))

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Researcher profile lookup")
    parser.add_argument("name", help="Researcher name")
    parser.add_argument("--org", default=None, help="Organization/university")
    parser.add_argument("--scholar-url", default=None, help="Google Scholar profile URL")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")

    args = parser.parse_args()
    profile = build_profile(args.name, organization=args.org, scholar_url=args.scholar_url)

    if args.format == "markdown":
        print(format_profile(profile))
    else:
        json.dump(profile, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
