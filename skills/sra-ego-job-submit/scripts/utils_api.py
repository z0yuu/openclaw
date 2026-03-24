#!/usr/bin/env python3
from __future__ import annotations

"""
调用工具与配置 API（对应 references/utils.md）。
用法：工作目录为 skill 根目录时 python scripts/utils_api.py <子命令> ...
"""
import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    API_PREFIX,
    UTIL_SUCCESS_CODE,
    get_base_url,
    get_token,
    handle_error,
    http_get,
)


def get_config(
    tenant_type: str | None = None,
    base_url: str | None = None,
) -> str:
    """GET /api/ego/portal/config"""
    base = (base_url or get_base_url()).rstrip("/")
    params: dict[str, Any] = {}
    if tenant_type:
        params["tenantType"] = tenant_type
    url = f"{base}{API_PREFIX}/config"
    try:
        resp = http_get(url, params=params if params else None, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != UTIL_SUCCESS_CODE:
            return f"API error: code={data.get('code')}, message={data.get('message', '')}"
        return json.dumps(data.get("data", data), indent=2, ensure_ascii=False)
    except Exception as e:
        return handle_error(e)


def get_framework_versions(base_url: str | None = None) -> str:
    """GET /api/ego/portal/framework_versions"""
    base = (base_url or get_base_url()).rstrip("/")
    url = f"{base}{API_PREFIX}/framework_versions"
    try:
        resp = http_get(url, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != UTIL_SUCCESS_CODE:
            return f"API error: code={data.get('code')}, message={data.get('message', '')}"
        return json.dumps(data.get("data", data), indent=2, ensure_ascii=False)
    except Exception as e:
        return handle_error(e)


def get_project_quota(project_id: str, base_url: str | None = None) -> str:
    """GET /api/ego/portal/project_quota/{project_id}"""
    base = (base_url or get_base_url()).rstrip("/")
    url = f"{base}{API_PREFIX}/project_quota/{project_id}"
    try:
        resp = http_get(url, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != UTIL_SUCCESS_CODE:
            return f"API error: code={data.get('code')}, message={data.get('message', '')}"
        return json.dumps(data.get("data", data), indent=2, ensure_ascii=False)
    except Exception as e:
        return handle_error(e)


def upload_file(
    file_paths: str,
    base_url: str | None = None,
    timeout: float = 120.0,
) -> str:
    """POST /api/ego/portal/upload_file (multipart file1, file2, ...). 单文件最大 32MB。"""
    paths = [p.strip() for p in (file_paths or "").split(",") if p.strip()]
    if not paths:
        return "Error: at least one file path is required (comma-separated)."
    base = (base_url or get_base_url()).rstrip("/")
    url = f"{base}{API_PREFIX}/upload_file"
    headers = {"Cookie": f"userID={get_token()}"}
    files_dict: dict[str, tuple[str, bytes]] = {}
    for i, path in enumerate(paths):
        with open(path, "rb") as f:
            content = f.read()
        name = os.path.basename(path)
        files_dict[f"file{i + 1}"] = (name, content)
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, headers=headers, files=files_dict)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != UTIL_SUCCESS_CODE:
            return f"API error: code={data.get('code')}, message={data.get('message', '')}"
        return json.dumps(data.get("data", data), indent=2, ensure_ascii=False)
    except FileNotFoundError as e:
        return f"Error: file not found - {e}"
    except Exception as e:
        return handle_error(e)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="调用工具与配置 API（references/utils.md）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="cmd", required=True, help="子命令")

    p_config = sub.add_parser("config", help="获取门户配置 GET /config")
    p_config.add_argument("--tenant_type", type=str, default=None, help="如 predictor 仅返回 predictor 相关")
    p_config.add_argument("--base_url", type=str, default=None)

    p_fw = sub.add_parser("framework_versions", help="获取训练框架版本列表")
    p_fw.add_argument("--base_url", type=str, default=None)

    p_quota = sub.add_parser("project_quota", help="获取项目配额 GET /project_quota/{project_id}")
    p_quota.add_argument("project_id", type=str)
    p_quota.add_argument("--base_url", type=str, default=None)

    p_upload = sub.add_parser("upload", help="上传文件到 USS 临时桶 multipart")
    p_upload.add_argument("file_paths", type=str, help="逗号分隔的本地文件路径")
    p_upload.add_argument("--base_url", type=str, default=None)
    p_upload.add_argument("--timeout", type=float, default=120.0)

    args = parser.parse_args()
    cmd = args.cmd

    if cmd == "config":
        print(get_config(tenant_type=args.tenant_type, base_url=args.base_url))
    elif cmd == "framework_versions":
        print(get_framework_versions(base_url=args.base_url))
    elif cmd == "project_quota":
        print(get_project_quota(args.project_id, base_url=args.base_url))
    elif cmd == "upload":
        print(upload_file(args.file_paths, base_url=args.base_url, timeout=args.timeout))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
