#!/usr/bin/env python3
"""CLI for EGO get log content API."""

from __future__ import annotations

import argparse
import sys

from ego_api_common import EgoApiError, get_log_content


def _tail_lines(text: str, n: int) -> str:
    if n <= 0:
        return text
    lines = text.splitlines()
    return "\n".join(lines[-n:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Get EGO log file content")
    parser.add_argument("job_id", type=int)
    parser.add_argument("log_file_name", type=str)
    parser.add_argument("--base-url", type=str)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument(
        "--tail-lines",
        type=int,
        default=10000,
        help="only output the last N lines (default: 10000); use 0 for full content",
    )
    args = parser.parse_args()

    try:
        content = get_log_content(
            args.job_id,
            args.log_file_name,
            base_url=args.base_url,
            timeout=args.timeout,
        )
        print(_tail_lines(content, args.tail_lines))
        return 0
    except EgoApiError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
