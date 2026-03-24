#!/usr/bin/env python3
"""CLI for EGO list checkpoints (by model/version) API."""

from __future__ import annotations

import argparse
import sys

from ego_api_common import EgoApiError, list_checkpoints, print_json


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="List EGO checkpoints for a model version")
    p.add_argument("model_id", type=int)
    p.add_argument("version_id", type=int)
    p.add_argument("--current", type=int, default=1)
    p.add_argument("--page-size", type=int, default=10)
    p.add_argument("--order", type=str)
    p.add_argument("--order-by", type=str)
    p.add_argument("--job-id", type=int)
    p.add_argument("--checkpoint-id", type=int)
    p.add_argument("--checkpoint-name", type=str)
    p.add_argument("--only-mine", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--base-url", type=str)
    p.add_argument("--timeout", type=float, default=30.0)
    return p


def main() -> int:
    args = build_parser().parse_args()
    try:
        data = list_checkpoints(
            args.model_id,
            args.version_id,
            current=args.current,
            page_size=args.page_size,
            order=args.order,
            order_by=args.order_by,
            job_id=args.job_id,
            checkpoint_id=args.checkpoint_id,
            checkpoint_name=args.checkpoint_name,
            only_mine=args.only_mine if args.only_mine else None,
            verbose=args.verbose if args.verbose else None,
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
