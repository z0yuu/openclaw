#!/usr/bin/env python3
from __future__ import annotations

"""
调用模型 API（对应 references/model.md）。
用法：工作目录为 skill 根目录时 python scripts/model.py list [--model_name xxx --scope 2] 或 python scripts/model.py get <model_id>。
"""
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    API_PREFIX,
    MODEL_SUCCESS_CODE,
    get_base_url,
    handle_error,
    http_get,
    http_post,
)


def list_models(
    current: int = 1,
    page_size: int = 10,
    order_by: str = "model_id",
    order: str = "descend",
    scope: int = 1,
    model_id: int | None = None,
    model_name: str | None = None,
    project: str | None = None,
    create_time_start: int | None = None,
    create_time_end: int | None = None,
    creator: str | None = None,
    base_url: str | None = None,
) -> str:
    """GET /api/ego/portal/models"""
    base = (base_url or get_base_url()).rstrip("/")
    params: dict[str, Any] = {
        "current": current,
        "pageSize": page_size,
        "orderBy": order_by,
        "order": order,
        "scope": scope,
    }
    if model_id is not None:
        params["model_id"] = model_id
    if model_name:
        params["model_name"] = model_name
    if project:
        params["project"] = project
    if create_time_start is not None:
        params["create_time_start"] = create_time_start
    if create_time_end is not None:
        params["create_time_end"] = create_time_end
    if creator:
        params["creator"] = creator
    url = f"{base}{API_PREFIX}/models"
    try:
        resp = http_get(url, params=params, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != MODEL_SUCCESS_CODE:
            return f"API error: code={data.get('code')}, message={data.get('message', '')}"
        return json.dumps(data.get("data", data), indent=2, ensure_ascii=False)
    except Exception as e:
        return handle_error(e)


def get_model(model_id: int, base_url: str | None = None) -> str:
    """GET /api/ego/portal/model/{model_id}"""
    base = (base_url or get_base_url()).rstrip("/")
    url = f"{base}{API_PREFIX}/model/{model_id}"
    try:
        resp = http_get(url, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != MODEL_SUCCESS_CODE:
            return f"API error: code={data.get('code')}, message={data.get('message', '')}"
        return json.dumps(data.get("data", data), indent=2, ensure_ascii=False)
    except Exception as e:
        return handle_error(e)


def create_model(
    model_name: str,
    tenant_id: str,
    project_id: str,
    description: str | None = None,
    is_private: int = 0,
    auth_users: str | None = None,
    base_url: str | None = None,
) -> str:
    """POST /api/ego/portal/model"""
    base = (base_url or get_base_url()).rstrip("/")
    body: dict[str, Any] = {
        "model_name": model_name,
        "tenant_id": tenant_id,
        "project_id": project_id,
        "is_private": is_private,
    }
    if description is not None:
        body["description"] = description
    if auth_users:
        body["auth_users"] = [s.strip() for s in auth_users.split(",") if s.strip()]
    url = f"{base}{API_PREFIX}/model"
    try:
        resp = http_post(url, json_body=body, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != MODEL_SUCCESS_CODE:
            return f"API error: code={data.get('code')}, message={data.get('message', '')}"
        return json.dumps(data.get("data", data), indent=2, ensure_ascii=False)
    except Exception as e:
        return handle_error(e)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="调用模型 API（references/model.md）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="cmd", required=True, help="子命令")

    p_list = sub.add_parser("list", help="获取模型列表 GET /models")
    p_list.add_argument("--current", type=int, default=1)
    p_list.add_argument("--page_size", type=int, default=10)
    p_list.add_argument("--order_by", type=str, default="model_id",
                        choices=("model_id", "model_name", "create_time", "creator"))
    p_list.add_argument("--order", type=str, default="descend", choices=("ascend", "descend"))
    p_list.add_argument("--scope", type=int, default=1, help="1-全部(有权限) 2-个人")
    p_list.add_argument("--model_id", type=int, default=None)
    p_list.add_argument("--model_name", type=str, default=None)
    p_list.add_argument("--project", type=str, default=None)
    p_list.add_argument("--create_time_start", type=int, default=None)
    p_list.add_argument("--create_time_end", type=int, default=None)
    p_list.add_argument("--creator", type=str, default=None)
    p_list.add_argument("--base_url", type=str, default=None)

    p_get = sub.add_parser("get", help="获取模型详情")
    p_get.add_argument("model_id", type=int)
    p_get.add_argument("--base_url", type=str, default=None)

    p_create = sub.add_parser("create", help="创建模型 POST /model")
    p_create.add_argument("model_name", type=str)
    p_create.add_argument("tenant_id", type=str)
    p_create.add_argument("project_id", type=str)
    p_create.add_argument("--description", type=str, default=None)
    p_create.add_argument("--is_private", type=int, default=0, choices=(0, 1))
    p_create.add_argument("--auth_users", type=str, default=None)
    p_create.add_argument("--base_url", type=str, default=None)

    args = parser.parse_args()
    cmd = args.cmd

    if cmd == "list":
        print(list_models(
            current=args.current,
            page_size=args.page_size,
            order_by=args.order_by,
            order=args.order,
            scope=args.scope,
            model_id=args.model_id,
            model_name=args.model_name,
            project=args.project,
            create_time_start=args.create_time_start,
            create_time_end=args.create_time_end,
            creator=args.creator,
            base_url=args.base_url,
        ))
    elif cmd == "get":
        print(get_model(args.model_id, base_url=args.base_url))
    elif cmd == "create":
        print(create_model(
            args.model_name,
            args.tenant_id,
            args.project_id,
            description=args.description,
            is_private=args.is_private,
            auth_users=args.auth_users,
            base_url=args.base_url,
        ))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
