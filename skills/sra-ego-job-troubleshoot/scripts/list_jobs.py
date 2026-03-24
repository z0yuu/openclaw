#!/usr/bin/env python3
"""CLI for EGO list jobs API."""

from __future__ import annotations

import argparse
import sys

from ego_api_common import EgoApiError, list_jobs, print_json


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="List EGO jobs")
    p.add_argument("--current", type=int, default=1)
    p.add_argument("--page-size", type=int, default=10)
    p.add_argument("--list-type", type=int, default=1)
    p.add_argument("--scope", type=str, default="2")
    p.add_argument("--order", type=str, default="descend")
    p.add_argument("--order-by", type=str, default="job_id")
    p.add_argument("--job-id", type=int)
    p.add_argument("--job-name", type=str)
    p.add_argument("--job-status", type=int)
    p.add_argument("--project-id", type=str)
    p.add_argument("--creator", type=str)
    p.add_argument("--version-id", type=int)
    p.add_argument("--zone", type=str)
    p.add_argument("--base-url", type=str)
    p.add_argument("--timeout", type=float, default=30.0)
    return p


def main() -> int:
    args = build_parser().parse_args()
    try:
        data = list_jobs(
            current=args.current,
            page_size=args.page_size,
            list_type=args.list_type,
            scope=args.scope,
            order=args.order,
            order_by=args.order_by,
            job_id=args.job_id,
            job_name=args.job_name,
            job_status=args.job_status,
            project_id=args.project_id,
            creator=args.creator,
            version_id=args.version_id,
            zone=args.zone,
            base_url=args.base_url,
            timeout=args.timeout,
        )
        print_json(data)
        return 0
    except EgoApiError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
