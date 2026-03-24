#!/usr/bin/env python3
"""Shared EGO OpenAPI client for sra-ego-smart-tune-submit scripts."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_BASE_URL = "https://ego-portal.mlp.shopee.io"
API_PREFIX = "/api/ego/portal"


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


def _request(
    url: str,
    *,
    timeout: float = 60.0,
    parse_json: bool = False,
) -> str | dict[str, Any] | list[Any]:
    headers = {
        "Cookie": f"userID={_token()}",
        "Content-Type": "application/json",
        "User-Agent": "sra-ego-smart-tune-submit/1.0",
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


def get_ego_tune_dir_files(
    job_id: int,
    smart_tune_job_id: int,
    *,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any] | list[Any]:
    path = f"/job/{job_id}/ego_tune_{smart_tune_job_id}"
    text = _request(_build_url(path, base_url=base_url), timeout=timeout, parse_json=False)
    if not isinstance(text, str):
        raise EgoApiError("Unexpected response shape for get_ego_tune_dir_files")
    if not text.strip():
        return {"files": []}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}


def get_ego_tune_log_content(
    job_id: int,
    smart_tune_job_id: int,
    log_file_name: str,
    *,
    base_url: str | None = None,
    timeout: float = 60.0,
) -> str:
    encoded_name = urllib.parse.quote(log_file_name, safe="")
    path = f"/job/{job_id}/ego_tune_{smart_tune_job_id}/{encoded_name}"
    text = _request(_build_url(path, base_url=base_url), timeout=timeout, parse_json=False)
    if not isinstance(text, str):
        raise EgoApiError("Unexpected response shape for get_ego_tune_log_content")
    return text


def print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))
