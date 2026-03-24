#!/usr/bin/env python3
"""CLI for fetching USS file content by URL.

Default mode prints text content to stdout.
Use `--output` to download binary payload (e.g. zip) to local file.
"""

from __future__ import annotations

import argparse
import json
import sys

from ego_api_common import EgoApiError, download_uss_file, get_uss_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Get USS file content")
    parser.add_argument("url", type=str, help="Full USS file URL")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Write response bytes to local file (required for zip/binary files).",
    )
    args = parser.parse_args()

    try:
        if args.output:
            result = download_uss_file(args.url, args.output, timeout=args.timeout)
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(get_uss_file(args.url, timeout=args.timeout))
        return 0
    except EgoApiError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
