#!/usr/bin/env python3
"""
arXiv paper search and daily fetch.

Usage:
  # Search by keyword
  python arxiv_search.py search "transformer attention" --max 10 --days 30

  # Fetch daily papers from categories
  python arxiv_search.py daily --categories cs.AI cs.CL cs.LG --max 30

  # Fetch daily papers from last N hours
  python arxiv_search.py daily --categories cs.AI --hours 48 --max 50

Output: JSON array of paper records to stdout.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone

import arxiv

ARXIV_PAGE_SIZE = 25
ARXIV_DELAY_SECONDS = 3.0
ARXIV_NUM_RETRIES = 5


def _make_record(r) -> dict:
    pub = r.published or getattr(r, "updated", None)
    arxiv_id = r.entry_id.split("/abs/")[-1].rstrip("/")
    return {
        "title": (r.title or "").strip(),
        "arxiv_id": arxiv_id,
        "abstract": (r.summary or "")[:1500],
        "published": pub.isoformat() if pub else "",
        "categories": list(r.categories) if r.categories else [],
        "pdf_url": r.pdf_url or r.entry_id.replace("/abs/", "/pdf/") + ".pdf",
        "authors": [a.name for a in (r.authors or [])],
        "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
    }


def search_papers(query: str, max_results: int = 20, days_back: int = None):
    client = arxiv.Client(
        page_size=min(max_results, ARXIV_PAGE_SIZE),
        delay_seconds=ARXIV_DELAY_SECONDS,
        num_retries=ARXIV_NUM_RETRIES,
    )
    search = arxiv.Search(
        query=query,
        max_results=min(max_results, 200),
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    cutoff = None
    if days_back is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)

    papers = []
    for r in client.results(search):
        if cutoff and r.published:
            pub = r.published if r.published.tzinfo else r.published.replace(tzinfo=timezone.utc)
            if pub < cutoff:
                continue
        papers.append(_make_record(r))
        if len(papers) >= max_results:
            break

    papers.sort(key=lambda p: p["published"], reverse=True)
    return papers


def fetch_daily_papers(
    categories,
    max_results_per_category: int = 50,
    hours_back: int = 24,
):
    submitted_after = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    all_papers = []
    seen_ids: set[str] = set()

    client = arxiv.Client(
        page_size=ARXIV_PAGE_SIZE,
        delay_seconds=ARXIV_DELAY_SECONDS,
        num_retries=ARXIV_NUM_RETRIES,
    )

    for cat in categories:
        search = arxiv.Search(
            query=f"cat:{cat}",
            max_results=max_results_per_category,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )
        for r in client.results(search):
            if r.entry_id in seen_ids:
                continue
            pub = r.published or getattr(r, "updated", None)
            if pub:
                pub_utc = pub if pub.tzinfo else pub.replace(tzinfo=timezone.utc)
                cutoff = submitted_after if submitted_after.tzinfo else submitted_after.replace(tzinfo=timezone.utc)
                if pub_utc < cutoff:
                    continue
            seen_ids.add(r.entry_id)
            all_papers.append(_make_record(r))

    all_papers.sort(key=lambda p: p["published"], reverse=True)
    return all_papers


def format_paper(p, idx: int) -> str:
    authors = ", ".join(p["authors"][:5])
    if len(p["authors"]) > 5:
        authors += f" et al. ({len(p['authors'])} authors)"
    cats = ", ".join(p["categories"][:3])
    lines = [
        f"### {idx}. {p['title']}",
        f"**Authors:** {authors}",
        f"**Published:** {p['published'][:10]}  |  **Categories:** {cats}",
        f"**arXiv:** {p['arxiv_url']}  |  **PDF:** {p['pdf_url']}",
        f"\n> {p['abstract'][:500]}{'...' if len(p['abstract']) > 500 else ''}",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="arXiv paper search")
    sub = parser.add_subparsers(dest="command", required=True)

    sp_search = sub.add_parser("search", help="Search papers by keyword")
    sp_search.add_argument("query", help="Search query")
    sp_search.add_argument("--max", type=int, default=10, help="Max results")
    sp_search.add_argument("--days", type=int, default=None, help="Only papers from last N days")
    sp_search.add_argument("--format", choices=["json", "markdown"], default="json")

    sp_daily = sub.add_parser("daily", help="Fetch daily papers by category")
    sp_daily.add_argument("--categories", nargs="+", required=True, help="arXiv categories")
    sp_daily.add_argument("--max", type=int, default=30, help="Max results per category")
    sp_daily.add_argument("--hours", type=int, default=24, help="Hours to look back")
    sp_daily.add_argument("--format", choices=["json", "markdown"], default="json")

    args = parser.parse_args()

    if args.command == "search":
        papers = search_papers(args.query, max_results=args.max, days_back=args.days)
    else:
        papers = fetch_daily_papers(args.categories, max_results_per_category=args.max, hours_back=args.hours)

    if args.format == "markdown":
        if not papers:
            print("No papers found.")
        else:
            print(f"Found **{len(papers)}** papers:\n")
            for i, p in enumerate(papers, 1):
                print(format_paper(p, i))
                print()
    else:
        json.dump(papers, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
