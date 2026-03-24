#!/usr/bin/env python3
"""Diagnose SOC job status and elapsed times by soc_project_id + soc_job_id."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any

from ego_api_common import print_json


class SocJobDiagnosisError(Exception):
    """Raised when SOC job diagnosis fails."""


def _to_seconds(ts: int | float | None) -> int:
    if ts is None:
        return 0
    val = int(ts)
    if val >= 10**12:
        return val // 1000
    return val


def _minutes_since(ts: int | float | None, now_ts: int) -> int:
    sec = _to_seconds(ts)
    if sec <= 0:
        return 0
    delta = now_ts - sec
    if delta < 0:
        return 0
    return delta // 60


def _get_soc_job(soc_project_id: str, soc_job_id: str, timeout: float = 30.0) -> dict[str, Any]:
    token = os.environ.get("USER_ID_OPENAPI", "").strip()
    if not token:
        raise SocJobDiagnosisError("USER_ID_OPENAPI environment variable is required.")

    url = f"https://soc.shopee.io/api/job/v1/projects/{soc_project_id}/jobs/{soc_job_id}"
    req = urllib.request.Request(
        url=url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="replace") if err.fp else ""
        raise SocJobDiagnosisError(f"SOC API HTTP {err.code}: {body[:500] if body else 'No body'}") from err
    except urllib.error.URLError as err:
        raise SocJobDiagnosisError(f"SOC API request failed: {err.reason}") from err

    try:
        data = json.loads(text)
    except json.JSONDecodeError as err:
        raise SocJobDiagnosisError(f"Invalid SOC API JSON: {err}") from err

    if not isinstance(data, dict):
        raise SocJobDiagnosisError("Unexpected SOC API response shape")
    payload = data.get("data")
    if not isinstance(payload, dict):
        raise SocJobDiagnosisError("SOC API response missing data object")
    return payload


def _diagnosis_text(soc_status: str, soc_elapsed_create_minutes: int, soc_running_minutes: int) -> str:
    status = (soc_status or "").lower()
    if status == "killed":
        return "SOC JOB状态为killed"
    if status == "scheduling":
        return f"SOC job 已经调度了{soc_elapsed_create_minutes} 分钟, 如果时长超过5分钟，请联系SOC同学"
    if status == "queueing":
        return "由于资源不足，当前SOC JOB还在排队等待资源。"
    if status == "running":
        return f"SOC JOB已经处于running状态，运行了{soc_running_minutes}分钟"
    return f"SOC JOB 当前状态为 {soc_status}。"


def diagnose(soc_project_id: str, soc_job_id: str, timeout: float = 30.0) -> dict[str, Any]:
    now_ts = int(time.time())
    soc_data = _get_soc_job(soc_project_id, soc_job_id, timeout=timeout)

    soc_status = str(soc_data.get("status") or "")
    soc_create_time = soc_data.get("createTime")
    soc_start_time = soc_data.get("startTime")

    soc_elapsed_create_minutes = _minutes_since(soc_create_time, now_ts)
    soc_running_minutes = _minutes_since(soc_start_time, now_ts)

    diagnosis = _diagnosis_text(soc_status, soc_elapsed_create_minutes, soc_running_minutes)

    if soc_status.lower() == "killed":
        return {
            "soc_project_id": soc_project_id,
            "soc_job_id": soc_job_id,
            "soc_status": soc_status,
            "diagnosis": diagnosis,
        }

    return {
        "soc_project_id": soc_project_id,
        "soc_job_id": soc_job_id,
        "soc_status": soc_status,
        "soc_create_time": soc_create_time,
        "soc_start_time": soc_start_time,
        "soc_elapsed_from_create_minutes": soc_elapsed_create_minutes,
        "soc_running_minutes": soc_running_minutes,
        "diagnosis": diagnosis,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose SOC job status by soc_project_id + soc_job_id")
    parser.add_argument("soc_project_id", type=str)
    parser.add_argument("soc_job_id", type=str)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    try:
        result = diagnose(args.soc_project_id, args.soc_job_id, timeout=args.timeout)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except SocJobDiagnosisError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
