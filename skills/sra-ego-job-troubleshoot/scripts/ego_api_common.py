#!/usr/bin/env python3
"""Shared EGO OpenAPI client for sra-ego-job-troubleshoot scripts.
This module intentionally contains only the endpoints needed by this skill,
so the skill can run without mcp_server dependency.
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
JOB_SUCCESS_CODE = "9914100"
DEFAULT_TOKEN_FILE = Path(__file__).resolve().parents[1] / ".user_id_openapi"


class EgoApiError(Exception):
    """Raised when API request fails or response is invalid."""


def _token() -> str:
    token = os.environ.get("USER_ID_OPENAPI", "").strip()
    if token:
        return token

    if DEFAULT_TOKEN_FILE.exists():
        file_token = DEFAULT_TOKEN_FILE.read_text(encoding="utf-8").strip()
        if file_token:
            return file_token

    raise EgoApiError(
        "USER_ID_OPENAPI environment variable is required (or set token file at "
        f"{DEFAULT_TOKEN_FILE}). Set it to your EGO access token (Cookie userID value)."
    )


def _base_url(override: str | None = None) -> str:
    base = (override or os.environ.get("EGO_BASE_URL") or DEFAULT_BASE_URL).strip()
    return base.rstrip("/")


def _request(
    url: str,
    *,
    timeout: float = 60.0,
    parse_json: bool = False,
) -> str | dict[str, Any] | list[Any]:
    headers = {
        "Cookie": f"userID={_token()}",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url=url, headers=headers, method="GET")
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


def get_job(job_id: int, base_url: str | None = None, timeout: float = 30.0) -> dict[str, Any]:
    data = _request(_build_url(f"/job/{job_id}", base_url=base_url), timeout=timeout, parse_json=True)
    if not isinstance(data, dict):
        raise EgoApiError("Unexpected response shape for get_job")
    if data.get("code") != JOB_SUCCESS_CODE:
        raise EgoApiError(f"API error: code={data.get('code')}, message={data.get('message', '')}")
    payload = data.get("data", data)
    if not isinstance(payload, dict):
        raise EgoApiError("Unexpected payload shape for get_job")
    return payload


def list_jobs(
    *,
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
    timeout: float = 30.0,
) -> dict[str, Any] | list[Any]:
    params: dict[str, Any] = {
        "current": current,
        "pageSize": page_size,
        "list_type": list_type,
        "scope": scope,
        "order": order,
        "orderBy": order_by,
        "job_id": job_id,
        "job_name": job_name,
        "job_status": job_status,
        "project_id": project_id,
        "creator": creator,
        "version_id": version_id,
        "zone": zone,
    }
    data = _request(_build_url("/jobs", params=params, base_url=base_url), timeout=timeout, parse_json=True)
    if not isinstance(data, dict):
        raise EgoApiError("Unexpected response shape for list_jobs")
    if data.get("code") != JOB_SUCCESS_CODE:
        raise EgoApiError(f"API error: code={data.get('code')}, message={data.get('message', '')}")
    payload = data.get("data", data)
    if not isinstance(payload, (dict, list)):
        raise EgoApiError("Unexpected payload shape for list_jobs")
    return payload


def get_job_tasks(
    job_id: int,
    *,
    verbose: bool = False,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any] | list[Any]:
    params = {"verbose": "true"} if verbose else None
    data = _request(
        _build_url(f"/job/{job_id}/tasks", params=params, base_url=base_url),
        timeout=timeout,
        parse_json=True,
    )
    if not isinstance(data, dict):
        raise EgoApiError("Unexpected response shape for get_job_tasks")
    if data.get("code") != JOB_SUCCESS_CODE:
        raise EgoApiError(f"API error: code={data.get('code')}, message={data.get('message', '')}")
    payload = data.get("data", data)
    if not isinstance(payload, (dict, list)):
        raise EgoApiError("Unexpected payload shape for get_job_tasks")
    return payload


def get_job_log_files(
    job_id: int,
    *,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any] | list[Any]:
    text = _request(_build_url(f"/job/{job_id}/log_files", base_url=base_url), timeout=timeout, parse_json=False)
    if not isinstance(text, str):
        raise EgoApiError("Unexpected response shape for get_job_log_files")
    if "Get UssPath Failed" in text or "Get LogFiles Failed" in text:
        raise EgoApiError(text.strip())
    if not text.strip():
        return {"log_files": []}
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}
    if isinstance(data, dict) and data.get("code") == 200:
        return {"log_files": data.get("data", [])}
    return data


def get_log_content(
    job_id: int,
    log_file_name: str,
    *,
    base_url: str | None = None,
    timeout: float = 60.0,
) -> str:
    text = _request(
        _build_url(f"/job/{job_id}/{urllib.parse.quote(log_file_name, safe='')}", base_url=base_url),
        timeout=timeout,
        parse_json=False,
    )
    if not isinstance(text, str):
        raise EgoApiError("Unexpected response shape for get_log_content")
    if "GetUssLogFilePath Failed" in text or "Not Found Log File" in text:
        raise EgoApiError(text.strip())
    return text


def get_log_summary(
    job_id: int,
    *,
    base_url: str | None = None,
    timeout: float = 120.0,
) -> str:
    text = _request(_build_url(f"/job/{job_id}/log_summary", base_url=base_url), timeout=timeout, parse_json=False)
    if not isinstance(text, str):
        raise EgoApiError("Unexpected response shape for get_log_summary")
    return text or "(empty)"


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

    headers = {
        "Cookie": f"userID={_token()}",
    }
    req = urllib.request.Request(url=cleaned, headers=headers, method="GET")
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
