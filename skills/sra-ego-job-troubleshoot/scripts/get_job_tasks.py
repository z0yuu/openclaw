#!/usr/bin/env python3
"""CLI for EGO get job tasks API."""

from __future__ import annotations

import argparse
import sys

from ego_api_common import EgoApiError, get_job_tasks, print_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Get EGO job tasks")
    parser.add_argument("job_id", type=int)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--base-url", type=str)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    try:
        print_json(
            get_job_tasks(
                args.job_id,
                verbose=args.verbose,
                base_url=args.base_url,
                timeout=args.timeout,
            )
        )
        return 0
    except EgoApiError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
