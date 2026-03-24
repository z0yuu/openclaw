#!/usr/bin/env python3
"""CLI for EGO portal config API (GET /api/ego/portal/config)."""

from __future__ import annotations

import argparse
import sys

from ego_api_common import EgoApiError, get_config, print_json


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Get EGO portal config (tenants, user_info, enums, gpu_packages, etc.)"
    )
    parser.add_argument(
        "--tenant-type",
        type=str,
        help="e.g. predictor — only return tenants/projects for that type",
    )
    parser.add_argument("--base-url", type=str)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    try:
        print_json(
            get_config(
                tenant_type=args.tenant_type,
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
