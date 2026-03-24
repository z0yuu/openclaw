#!/usr/bin/env python3
"""CLI for EGO list models API."""

from __future__ import annotations

import argparse
import sys

from ego_api_common import EgoApiError, list_models, print_json


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="List EGO models")
    p.add_argument("--current", type=int, default=1)
    p.add_argument("--page-size", type=int, default=10)
    p.add_argument("--order-by", type=str)
    p.add_argument("--order", type=str)
    p.add_argument("--scope", type=int)
    p.add_argument("--model-id", type=int)
    p.add_argument("--model-name", type=str)
    p.add_argument("--project", type=str)
    p.add_argument("--create-time-start", type=int)
    p.add_argument("--create-time-end", type=int)
    p.add_argument("--creator", type=str)
    p.add_argument("--base-url", type=str)
    p.add_argument("--timeout", type=float, default=30.0)
    return p


def main() -> int:
    args = build_parser().parse_args()
    try:
        data = list_models(
            current=args.current,
            page_size=args.page_size,
            order_by=args.order_by,
            order=args.order,
            scope=args.scope,
            model_id=args.model_id,
            model_name=args.model_name,
            project=args.project,
            create_time_start=args.create_time_start,
            create_time_end=args.create_time_end,
            creator=args.creator,
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
