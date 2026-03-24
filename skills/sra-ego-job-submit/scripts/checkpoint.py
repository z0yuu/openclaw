#!/usr/bin/env python3
from __future__ import annotations

"""
调用 Checkpoint API（对应 references/checkpoint.md）。
用法：工作目录为 skill 根目录时 python scripts/checkpoint.py list <model_id> <version_id> [选项] ...
"""
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    API_PREFIX,
    CHECKPOINT_SUCCESS_CODE,
    get_base_url,
    handle_error,
    http_get,
)


def list_checkpoints(
    model_id: int,
    version_id: int,
    current: int = 1,
    page_size: int = 10,
    order: str = "descend",
    order_by: str = "checkpoint_id",
    job_id: int | None = None,
    checkpoint_id: int | None = None,
    checkpoint_name: str | None = None,
    only_mine: bool = False,
    verbose: bool = False,
    base_url: str | None = None,
) -> str:
    """GET /api/ego/portal/model/{model_id}/version/{version_id}/checkpoints"""
    base = (base_url or get_base_url()).rstrip("/")
    params: dict[str, Any] = {
        "current": current,
        "pageSize": page_size,
        "order": order,
        "orderBy": order_by,
    }
    if job_id is not None:
        params["job_id"] = job_id
    if checkpoint_id is not None:
        params["checkpoint_id"] = checkpoint_id
    if checkpoint_name:
        params["checkpoint_name"] = checkpoint_name
    if only_mine:
        params["only_mine"] = "true"
    if verbose:
        params["verbose"] = "true"
    url = f"{base}{API_PREFIX}/model/{model_id}/version/{version_id}/checkpoints"
    try:
        resp = http_get(url, params=params, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != CHECKPOINT_SUCCESS_CODE:
            return f"API error: code={data.get('code')}, message={data.get('message', '')}"
        return json.dumps(data.get("data", data), indent=2, ensure_ascii=False)
    except Exception as e:
        return handle_error(e)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="调用 Checkpoint API（references/checkpoint.md）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="cmd", required=True, help="子命令")

    p_list = sub.add_parser("list", help="获取 Checkpoint 列表")
    p_list.add_argument("model_id", type=int)
    p_list.add_argument("version_id", type=int)
    p_list.add_argument("--current", type=int, default=1)
    p_list.add_argument("--page_size", type=int, default=10)
    p_list.add_argument("--order", type=str, default="descend", choices=("ascend", "descend"))
    p_list.add_argument("--order_by", type=str, default="checkpoint_id",
                        choices=("checkpoint_id", "size", "feature_num", "mf_feature_num", "related_job_name", "create_time"))
    p_list.add_argument("--job_id", type=int, default=None)
    p_list.add_argument("--checkpoint_id", type=int, default=None)
    p_list.add_argument("--checkpoint_name", type=str, default=None)
    p_list.add_argument("--only_mine", action="store_true", help="仅当前用户创建的")
    p_list.add_argument("--verbose", action="store_true", help="返回 checkpoint_path、related_job_s3_path")
    p_list.add_argument("--base_url", type=str, default=None)

    args = parser.parse_args()
    cmd = args.cmd

    if cmd == "list":
        print(list_checkpoints(
            args.model_id,
            args.version_id,
            current=args.current,
            page_size=args.page_size,
            order=args.order,
            order_by=args.order_by,
            job_id=args.job_id,
            checkpoint_id=args.checkpoint_id,
            checkpoint_name=args.checkpoint_name,
            only_mine=args.only_mine,
            verbose=args.verbose,
            base_url=args.base_url,
        ))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
