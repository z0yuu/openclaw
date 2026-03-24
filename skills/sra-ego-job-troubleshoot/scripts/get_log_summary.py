#!/usr/bin/env python3
"""CLI for EGO get log summary API."""

from __future__ import annotations

import argparse
import sys

from ego_api_common import EgoApiError, get_log_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Get EGO log summary")
    parser.add_argument("job_id", type=int)
    parser.add_argument("--base-url", type=str)
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()

    try:
        print(get_log_summary(args.job_id, base_url=args.base_url, timeout=args.timeout))
        return 0
    except EgoApiError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
