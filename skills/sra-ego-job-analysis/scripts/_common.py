"""
Shared helpers for EGO Portal API scripts.
Auth: Cookie userID from env USER_ID_OPENAPI.
Base URL: env EGO_BASE_URL (default https://ego-portal.mlp.shopee.io).
"""
import os
from typing import Any, Dict, Optional

import httpx

DEFAULT_BASE_URL = "https://ego-portal.mlp.shopee.io"
API_PREFIX = "/api/ego/portal"

JOB_SUCCESS_CODE = "9914100"
MODEL_SUCCESS_CODE = "9912100"
MODEL_VERSION_SUCCESS_CODE = "9913100"
CHECKPOINT_SUCCESS_CODE = "9916100"
UTIL_SUCCESS_CODE = "9911100"


def get_base_url() -> str:
    return os.environ.get("EGO_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def get_token() -> str:
    t = os.environ.get("USER_ID_OPENAPI", "")
    if not t:
        raise ValueError(
            "USER_ID_OPENAPI environment variable is required. "
            "Set it to your EGO access token (Cookie userID value)."
        )
    return t


def get_headers() -> dict[str, str]:
    return {
        "Cookie": f"userID={get_token()}",
        "Content-Type": "application/json",
    }


def http_get(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    timeout: float = 60.0,
) -> httpx.Response:
    with httpx.Client(timeout=timeout) as client:
        return client.get(url, params=params, headers=get_headers())


def http_post(
    url: str,
    json_body: Optional[Dict[str, Any]] = None,
    timeout: float = 60.0,
) -> httpx.Response:
    with httpx.Client(timeout=timeout) as client:
        return client.post(url, json=json_body, headers=get_headers())


def http_put(
    url: str,
    json_body: Optional[Dict[str, Any]] = None,
    timeout: float = 60.0,
) -> httpx.Response:
    with httpx.Client(timeout=timeout) as client:
        return client.put(url, json=json_body, headers=get_headers())


def handle_error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        code = e.response.status_code
        body = e.response.text
        if code == 401:
            return "Error: Unauthorized. Check USER_ID_OPENAPI token."
        if code == 403:
            return "Error: Permission denied."
        if code == 404:
            return "Error: Resource not found."
        return f"Error: HTTP {code} - {body[:500] if body else 'No body'}"
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out."
    return f"Error: {type(e).__name__}: {e}"
