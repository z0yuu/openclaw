#!/usr/bin/env python3
from __future__ import annotations

"""
调用训练作业与日志 API（对应 references/train_job.md）。
本 skill 内主要使用 list、get。用法：工作目录为 skill 根目录时 python scripts/train_job.py list [--job_name xxx ...] 或 python scripts/train_job.py get <job_id>。
"""
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    API_PREFIX,
    JOB_SUCCESS_CODE,
    get_base_url,
    handle_error,
    http_get,
    http_post,
)


def list_jobs(
    current: int = 1,
    page_size: int = 10,
    list_type: int = 1,
    scope: str = "2",
    order: str = "descend",
    order_by: str = "job_id",
    job_id: int | None = None,
    job_name: str | None = None,
    job_status: int | None = None,
    project_id: str | None = None,
    creator: str | None = None,
    version_id: int | None = None,
    zone: str | None = None,
    base_url: str | None = None,
) -> str:
    """GET /api/ego/portal/jobs"""
    base = (base_url or get_base_url()).rstrip("/")
    params: dict[str, Any] = {
        "current": current,
        "pageSize": page_size,
        "list_type": list_type,
        "scope": scope,
        "order": order,
        "orderBy": order_by,
    }
    if job_id is not None:
        params["job_id"] = job_id
    if job_name:
        params["job_name"] = job_name
    if job_status is not None:
        params["job_status"] = job_status
    if project_id:
        params["project_id"] = project_id
    if creator:
        params["creator"] = creator
    if version_id is not None:
        params["version_id"] = version_id
    if zone:
        params["zone"] = zone
    url = f"{base}{API_PREFIX}/jobs"
    try:
        resp = http_get(url, params=params, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != JOB_SUCCESS_CODE:
            return f"API error: code={data.get('code')}, message={data.get('message', '')}"
        return json.dumps(data.get("data", data), indent=2, ensure_ascii=False)
    except Exception as e:
        return handle_error(e)


def get_job(job_id: int, base_url: str | None = None) -> str:
    """GET /api/ego/portal/job/{job_id}"""
    base = (base_url or get_base_url()).rstrip("/")
    url = f"{base}{API_PREFIX}/job/{job_id}"
    try:
        resp = http_get(url, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != JOB_SUCCESS_CODE:
            return f"API error: code={data.get('code')}, message={data.get('message', '')}"
        return json.dumps(data.get("data", data), indent=2, ensure_ascii=False)
    except Exception as e:
        return handle_error(e)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="调用训练作业与日志 API（references/train_job.md）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="cmd", required=True, help="子命令")

    p_list = sub.add_parser("list", help="获取作业列表 GET /jobs")
    p_list.add_argument("--current", type=int, default=1)
    p_list.add_argument("--page_size", type=int, default=10)
    p_list.add_argument("--list_type", type=int, default=1, help="1-训练 2-发布 3-在线学习 4-周期规则 5-最近活跃")
    p_list.add_argument("--scope", type=str, default="2", help="1-全部 2-个人")
    p_list.add_argument("--order", type=str, default="descend", choices=("ascend", "descend"))
    p_list.add_argument("--order_by", type=str, default="job_id",
                        choices=("job_id", "job_name", "start_time", "end_time", "create_time", "status", "creator", "running_time"))
    p_list.add_argument("--job_id", type=int, default=None)
    p_list.add_argument("--job_name", type=str, default=None, help="作业名称模糊")
    p_list.add_argument("--job_status", type=int, default=None)
    p_list.add_argument("--project_id", type=str, default=None)
    p_list.add_argument("--creator", type=str, default=None)
    p_list.add_argument("--version_id", type=int, default=None)
    p_list.add_argument("--zone", type=str, default=None)
    p_list.add_argument("--base_url", type=str, default=None)

    p_get = sub.add_parser("get", help="获取作业详情")
    p_get.add_argument("job_id", type=int)
    p_get.add_argument("--base_url", type=str, default=None)

    args = parser.parse_args()
    cmd = args.cmd

    if cmd == "list":
        print(list_jobs(
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
        ))
    elif cmd == "get":
        print(get_job(args.job_id, base_url=args.base_url))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
