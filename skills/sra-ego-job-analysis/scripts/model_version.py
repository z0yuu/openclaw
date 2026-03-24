#!/usr/bin/env python3
from __future__ import annotations

"""
调用模型版本 API（对应 references/model_version.md）。
用法：工作目录为 skill 根目录时 python scripts/model_version.py list <model_id> [--version_name xxx] 或 python scripts/model_version.py get <model_id> <version_id>。
"""
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    API_PREFIX,
    MODEL_VERSION_SUCCESS_CODE,
    get_base_url,
    handle_error,
    http_get,
    http_post,
    http_put,
)


def list_model_versions(
    model_id: int,
    current: int = 1,
    page_size: int = 10,
    order_by: str = "id",
    order: str = "descend",
    version_id: int | None = None,
    version_name: str | None = None,
    create_time_start: int | None = None,
    create_time_end: int | None = None,
    creator: str | None = None,
    base_url: str | None = None,
) -> str:
    """GET /api/ego/portal/model/{model_id}/versions"""
    base = (base_url or get_base_url()).rstrip("/")
    params: dict[str, Any] = {
        "current": current,
        "pageSize": page_size,
        "orderBy": order_by,
        "order": order,
    }
    if version_id is not None:
        params["version_id"] = version_id
    if version_name:
        params["version_name"] = version_name
    if create_time_start is not None:
        params["create_time_start"] = create_time_start
    if create_time_end is not None:
        params["create_time_end"] = create_time_end
    if creator:
        params["creator"] = creator
    url = f"{base}{API_PREFIX}/model/{model_id}/versions"
    try:
        resp = http_get(url, params=params, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != MODEL_VERSION_SUCCESS_CODE:
            return f"API error: code={data.get('code')}, message={data.get('message', '')}"
        return json.dumps(data.get("data", data), indent=2, ensure_ascii=False)
    except Exception as e:
        return handle_error(e)


def get_model_version(
    model_id: int,
    version_id: int,
    base_url: str | None = None,
) -> str:
    """GET /api/ego/portal/model/{model_id}/version/{version_id}"""
    base = (base_url or get_base_url()).rstrip("/")
    url = f"{base}{API_PREFIX}/model/{model_id}/version/{version_id}"
    try:
        resp = http_get(url, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != MODEL_VERSION_SUCCESS_CODE:
            return f"API error: code={data.get('code')}, message={data.get('message', '')}"
        return json.dumps(data.get("data", data), indent=2, ensure_ascii=False)
    except Exception as e:
        return handle_error(e)


def create_model_version(
    model_id: int,
    body: str,
    base_url: str | None = None,
) -> str:
    """POST /api/ego/portal/model/{model_id}/version."""
    try:
        payload: dict[str, Any] = json.loads(body)
    except json.JSONDecodeError as e:
        return f"Invalid JSON body: {e}"
    if not isinstance(payload, dict):
        return "Body must be a JSON object"
    base = (base_url or get_base_url()).rstrip("/")
    url = f"{base}{API_PREFIX}/model/{model_id}/version"
    try:
        resp = http_post(url, json_body=payload, timeout=60.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != MODEL_VERSION_SUCCESS_CODE:
            return f"API error: code={data.get('code')}, message={data.get('message', '')}"
        return json.dumps(data.get("data", data), indent=2, ensure_ascii=False)
    except Exception as e:
        return handle_error(e)


def update_model_version(
    model_id: int,
    version_id: int,
    body: str,
    base_url: str | None = None,
) -> str:
    """PUT /api/ego/portal/model/{model_id}/version/{version_id}."""
    try:
        payload: dict[str, Any] = json.loads(body)
    except json.JSONDecodeError as e:
        return f"Invalid JSON body: {e}"
    if not isinstance(payload, dict):
        return "Body must be a JSON object"
    base = (base_url or get_base_url()).rstrip("/")
    url = f"{base}{API_PREFIX}/model/{model_id}/version/{version_id}"
    try:
        resp = http_put(url, json_body=payload, timeout=60.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != MODEL_VERSION_SUCCESS_CODE:
            return f"API error: code={data.get('code')}, message={data.get('message', '')}"
        return json.dumps(data.get("data") or {"message": "success"}, indent=2, ensure_ascii=False)
    except Exception as e:
        return handle_error(e)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="调用模型版本 API（references/model_version.md）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="cmd", required=True, help="子命令")

    p_list = sub.add_parser("list", help="获取版本列表 GET /model/{model_id}/versions")
    p_list.add_argument("model_id", type=int)
    p_list.add_argument("--current", type=int, default=1)
    p_list.add_argument("--page_size", type=int, default=10)
    p_list.add_argument("--order_by", type=str, default="id",
                        choices=("id", "create_time", "version_name", "version_id", "creator"))
    p_list.add_argument("--order", type=str, default="descend", choices=("ascend", "descend"))
    p_list.add_argument("--version_id", type=int, default=None)
    p_list.add_argument("--version_name", type=str, default=None)
    p_list.add_argument("--create_time_start", type=int, default=None)
    p_list.add_argument("--create_time_end", type=int, default=None)
    p_list.add_argument("--creator", type=str, default=None)
    p_list.add_argument("--base_url", type=str, default=None)

    p_get = sub.add_parser("get", help="获取版本详情")
    p_get.add_argument("model_id", type=int)
    p_get.add_argument("version_id", type=int)
    p_get.add_argument("--base_url", type=str, default=None)

    p_create = sub.add_parser("create", help="创建版本 POST /model/{model_id}/version")
    p_create.add_argument("model_id", type=int)
    p_create.add_argument("body", type=str, help="JSON 请求体")
    p_create.add_argument("--base_url", type=str, default=None)

    p_update = sub.add_parser("update", help="更新版本 PUT /model/{model_id}/version/{version_id}")
    p_update.add_argument("model_id", type=int)
    p_update.add_argument("version_id", type=int)
    p_update.add_argument("body", type=str, help="JSON 仅传需更新字段")
    p_update.add_argument("--base_url", type=str, default=None)

    args = parser.parse_args()
    cmd = args.cmd

    if cmd == "list":
        print(list_model_versions(
            args.model_id,
            current=args.current,
            page_size=args.page_size,
            order_by=args.order_by,
            order=args.order,
            version_id=args.version_id,
            version_name=args.version_name,
            create_time_start=args.create_time_start,
            create_time_end=args.create_time_end,
            creator=args.creator,
            base_url=args.base_url,
        ))
    elif cmd == "get":
        print(get_model_version(args.model_id, args.version_id, base_url=args.base_url))
    elif cmd == "create":
        print(create_model_version(args.model_id, args.body, base_url=args.base_url))
    elif cmd == "update":
        print(update_model_version(args.model_id, args.version_id, args.body, base_url=args.base_url))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
