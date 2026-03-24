#!/usr/bin/env python3
"""CLI for EGO checkpoint management list API (list_v3)."""

from __future__ import annotations

import argparse
import sys

from ego_api_common import EgoApiError, list_checkpoint_management, print_json


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="List EGO checkpoints (management: flat/by creator/by model/personal/trash)"
    )
    p.add_argument("tenant_id", type=str)
    p.add_argument(
        "list_type",
        type=int,
        choices=[0, 1, 2, 3, 4],
        help="0=flat, 1=by creator, 2=by model, 3=personal, 4=trash",
    )
    p.add_argument("--project-id", type=str)
    p.add_argument("--current", type=int, default=1)
    p.add_argument("--page-size", type=int, default=10)
    p.add_argument("--ckpt-size-min", type=int)
    p.add_argument("--ckpt-size-max", type=int)
    p.add_argument("--creator", type=str)
    p.add_argument("--model-id", type=int)
    p.add_argument("--model-name", type=str)
    p.add_argument("--checkpoint-id", type=int)
    p.add_argument("--checkpoint-name", type=str)
    p.add_argument("--base-url", type=str)
    p.add_argument("--timeout", type=float, default=30.0)
    return p


def main() -> int:
    args = build_parser().parse_args()
    try:
        data = list_checkpoint_management(
            args.tenant_id,
            args.list_type,
            project_id=args.project_id,
            current=args.current,
            page_size=args.page_size,
            ckpt_size_min=args.ckpt_size_min,
            ckpt_size_max=args.ckpt_size_max,
            creator=args.creator,
            model_id=args.model_id,
            model_name=args.model_name,
            checkpoint_id=args.checkpoint_id,
            checkpoint_name=args.checkpoint_name,
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
