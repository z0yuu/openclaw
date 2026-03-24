#!/usr/bin/env python3
"""Shared EGO OpenAPI client for sra-ego-checkpoint scripts.
Covers Model, Model Version, and Checkpoint APIs. No mcp_server dependency.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_BASE_URL = "https://ego-portal.mlp.shopee.io"
API_PREFIX = "/api/ego/portal"
MODEL_SUCCESS_CODE = "9912100"
MODEL_VERSION_SUCCESS_CODE = "9913100"
CHECKPOINT_SUCCESS_CODE = "9916100"
UTIL_SUCCESS_CODE = "9911100"


class EgoApiError(Exception):
    """Raised when API request fails or response is invalid."""


def _token() -> str:
    token = os.environ.get("USER_ID_OPENAPI", "").strip()
    if not token:
        raise EgoApiError(
            "USER_ID_OPENAPI environment variable is required. "
            "Set it to your EGO access token (Cookie userID value)."
        )
    return token


def _base_url(override: str | None = None) -> str:
    base = (override or os.environ.get("EGO_BASE_URL") or DEFAULT_BASE_URL).strip()
    return base.rstrip("/")


def _headers(url: str) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname and parsed.hostname.endswith(".shopee.io"):
        headers["Cookie"] = f"userID={_token()}"
    return headers



def _request(
    url: str,
    *,
    method: str = "GET",
    data: dict[str, Any] | None = None,
    timeout: float = 60.0,
    parse_json: bool = False,
) -> str | dict[str, Any] | list[Any]:
    req = urllib.request.Request(url=url, headers=_headers(url), method=method)
    if data is not None and method.upper() == "POST":
        req.data = json.dumps(data).encode("utf-8")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="replace") if err.fp else ""
        if err.code == 401:
            raise EgoApiError("Unauthorized. Check USER_ID_OPENAPI token.") from err
        if err.code == 403:
            raise EgoApiError("Permission denied.") from err
        if err.code == 404:
            raise EgoApiError("Resource not found.") from err
        raise EgoApiError(f"HTTP {err.code}: {body[:500] if body else 'No body'}") from err
    except urllib.error.URLError as err:
        raise EgoApiError(f"Request failed: {err.reason}") from err

    if not parse_json:
        return raw

    try:
        return json.loads(raw)
    except json.JSONDecodeError as err:
        raise EgoApiError(f"Invalid JSON response: {err}") from err


def _build_url(path: str, params: dict[str, Any] | None = None, base_url: str | None = None) -> str:
    base = _base_url(base_url)
    full = f"{base}{API_PREFIX}{path}"
    if not params:
        return full
    cleaned = {k: v for k, v in params.items() if v is not None and v != ""}
    if not cleaned:
        return full
    query = urllib.parse.urlencode(cleaned, doseq=True)
    return f"{full}?{query}"


def _check_code(resp: dict[str, Any], expected: str, label: str) -> None:
    code = resp.get("code")
    if code != expected:
        raise EgoApiError(
            f"API error ({label}): code={code}, message={resp.get('message', '')}"
        )


# --- Model API ---


def get_model(
    model_id: int,
    *,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    data = _request(
        _build_url(f"/model/{model_id}", base_url=base_url),
        timeout=timeout,
        parse_json=True,
    )
    if not isinstance(data, dict):
        raise EgoApiError("Unexpected response shape for get_model")
    _check_code(data, MODEL_SUCCESS_CODE, "get_model")
    payload = data.get("data", data)
    if not isinstance(payload, dict):
        raise EgoApiError("Unexpected payload shape for get_model")
    return payload


def list_models(
    *,
    current: int = 1,
    page_size: int = 10,
    order_by: str | None = None,
    order: str | None = None,
    scope: int | None = None,
    model_id: int | None = None,
    model_name: str | None = None,
    project: str | None = None,
    create_time_start: int | None = None,
    create_time_end: int | None = None,
    creator: str | None = None,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "current": current,
        "pageSize": page_size,
        "orderBy": order_by,
        "order": order,
        "scope": scope,
        "model_id": model_id,
        "model_name": model_name,
        "project": project,
        "create_time_start": create_time_start,
        "create_time_end": create_time_end,
        "creator": creator,
    }
    data = _request(
        _build_url("/models", params=params, base_url=base_url),
        timeout=timeout,
        parse_json=True,
    )
    if not isinstance(data, dict):
        raise EgoApiError("Unexpected response shape for list_models")
    _check_code(data, MODEL_SUCCESS_CODE, "list_models")
    payload = data.get("data", data)
    if not isinstance(payload, dict):
        raise EgoApiError("Unexpected payload shape for list_models")
    return payload


# --- Model Version API ---


def get_version(
    model_id: int,
    version_id: int,
    *,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    data = _request(
        _build_url(f"/model/{model_id}/version/{version_id}", base_url=base_url),
        timeout=timeout,
        parse_json=True,
    )
    if not isinstance(data, dict):
        raise EgoApiError("Unexpected response shape for get_version")
    _check_code(data, MODEL_VERSION_SUCCESS_CODE, "get_version")
    payload = data.get("data", data)
    if not isinstance(payload, dict):
        raise EgoApiError("Unexpected payload shape for get_version")
    return payload


def list_versions(
    model_id: int,
    *,
    current: int = 1,
    page_size: int = 10,
    order_by: str | None = None,
    order: str | None = None,
    version_id: int | None = None,
    version_name: str | None = None,
    create_time_start: int | None = None,
    create_time_end: int | None = None,
    creator: str | None = None,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "current": current,
        "pageSize": page_size,
        "orderBy": order_by,
        "order": order,
        "version_id": version_id,
        "version_name": version_name,
        "create_time_start": create_time_start,
        "create_time_end": create_time_end,
        "creator": creator,
    }
    data = _request(
        _build_url(f"/model/{model_id}/versions", params=params, base_url=base_url),
        timeout=timeout,
        parse_json=True,
    )
    if not isinstance(data, dict):
        raise EgoApiError("Unexpected response shape for list_versions")
    _check_code(data, MODEL_VERSION_SUCCESS_CODE, "list_versions")
    payload = data.get("data", data)
    if not isinstance(payload, dict):
        raise EgoApiError("Unexpected payload shape for list_versions")
    return payload


# --- Checkpoint API ---


def list_checkpoints(
    model_id: int,
    version_id: int,
    *,
    current: int = 1,
    page_size: int = 10,
    order: str | None = None,
    order_by: str | None = None,
    job_id: int | None = None,
    checkpoint_id: int | None = None,
    checkpoint_name: str | None = None,
    only_mine: bool | None = None,
    verbose: bool | None = None,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "current": current,
        "pageSize": page_size,
        "order": order,
        "orderBy": order_by,
        "job_id": job_id,
        "checkpoint_id": checkpoint_id,
        "checkpoint_name": checkpoint_name,
        "only_mine": only_mine,
        "verbose": verbose,
    }
    data = _request(
        _build_url(
            f"/model/{model_id}/version/{version_id}/checkpoints",
            params=params,
            base_url=base_url,
        ),
        timeout=timeout,
        parse_json=True,
    )
    if not isinstance(data, dict):
        raise EgoApiError("Unexpected response shape for list_checkpoints")
    _check_code(data, CHECKPOINT_SUCCESS_CODE, "list_checkpoints")
    payload = data.get("data", data)
    if not isinstance(payload, dict):
        raise EgoApiError("Unexpected payload shape for list_checkpoints")
    return payload


def get_checkpoint(
    checkpoint_id: int,
    *,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    params: dict[str, Any] = {"checkpoint_id": checkpoint_id}
    data = _request(
        _build_url("/checkpoint", params=params, base_url=base_url),
        timeout=timeout,
        parse_json=True,
    )
    if not isinstance(data, dict):
        raise EgoApiError("Unexpected response shape for get_checkpoint")
    _check_code(data, CHECKPOINT_SUCCESS_CODE, "get_checkpoint")
    payload = data.get("data", data)
    if not isinstance(payload, dict):
        raise EgoApiError("Unexpected payload shape for get_checkpoint")
    return payload


def list_checkpoint_management(
    tenant_id: str,
    list_type: int,
    *,
    project_id: str | None = None,
    current: int = 1,
    page_size: int = 10,
    ckpt_size_min: int | None = None,
    ckpt_size_max: int | None = None,
    creator: str | None = None,
    model_id: int | None = None,
    model_name: str | None = None,
    checkpoint_id: int | None = None,
    checkpoint_name: str | None = None,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "tenant_id": tenant_id,
        "list_type": list_type,
        "current": current,
        "pageSize": page_size,
        "project_id": project_id,
        "ckpt_size_min": ckpt_size_min,
        "ckpt_size_max": ckpt_size_max,
        "creator": creator,
        "model_id": model_id,
        "model_name": model_name,
        "checkpoint_id": checkpoint_id,
        "checkpoint_name": checkpoint_name,
    }
    body = {k: v for k, v in body.items() if v is not None and v != ""}
    url = _base_url(base_url) + API_PREFIX + "/checkpoint/management"
    data = _request(
        url,
        method="POST",
        data=body,
        timeout=timeout,
        parse_json=True,
    )
    if not isinstance(data, dict):
        raise EgoApiError("Unexpected response shape for list_checkpoint_management")
    _check_code(data, CHECKPOINT_SUCCESS_CODE, "list_checkpoint_management")
    payload = data.get("data", data)
    if not isinstance(payload, (dict, list)):
        raise EgoApiError("Unexpected payload shape for list_checkpoint_management")
    return payload

def get_config(
    *,
    tenant_type: str | None = None,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """GET /api/ego/portal/config — tenants, user_info, enums, gpu_packages, etc."""
    params: dict[str, Any] = {}
    if tenant_type:
        params["tenantType"] = tenant_type
    data = _request(
        _build_url("/config", params=params if params else None, base_url=base_url),
        timeout=timeout,
        parse_json=True,
    )
    if not isinstance(data, dict):
        raise EgoApiError("Unexpected response shape for get_config")
    _check_code(data, UTIL_SUCCESS_CODE, "get_config")
    payload = data.get("data", data)
    if not isinstance(payload, dict):
        raise EgoApiError("Unexpected payload shape for get_config")
    return payload


def get_uss_file(
    url: str,
    *,
    timeout: float = 60.0,
) -> str:
    cleaned = (url or "").strip()
    if not cleaned:
        raise EgoApiError("url is required (full USS file URL).")
    if not (cleaned.startswith("http://") or cleaned.startswith("https://")):
        raise EgoApiError("url must be a valid http(s) URL.")
    text = _request(cleaned, timeout=timeout, parse_json=False)
    if not isinstance(text, str):
        raise EgoApiError("Unexpected response shape for get_uss_file")
    return text or "(empty)"


def download_uss_file(
    url: str,
    output_path: str,
    *,
    timeout: float = 60.0,
) -> dict[str, Any]:
    cleaned = (url or "").strip()
    if not cleaned:
        raise EgoApiError("url is required (full USS file URL).")
    if not (cleaned.startswith("http://") or cleaned.startswith("https://")):
        raise EgoApiError("url must be a valid http(s) URL.")
    if not output_path:
        raise EgoApiError("output_path is required for binary download.")

    req = urllib.request.Request(url=cleaned, headers=_headers(cleaned), method="GET")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="replace") if err.fp else ""
        if err.code == 401:
            raise EgoApiError("Unauthorized. Check USER_ID_OPENAPI token.") from err
        if err.code == 403:
            raise EgoApiError("Permission denied.") from err
        if err.code == 404:
            raise EgoApiError("Resource not found.") from err
        raise EgoApiError(f"HTTP {err.code}: {body[:500] if body else 'No body'}") from err
    except urllib.error.URLError as err:
        raise EgoApiError(f"Request failed: {err.reason}") from err

    out.write_bytes(data)
    return {
        "output_path": str(out),
        "bytes": len(data),
        "url": cleaned,
    }


def print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))
