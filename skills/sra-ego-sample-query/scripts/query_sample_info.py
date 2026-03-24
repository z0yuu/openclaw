#!/usr/bin/env python3
from __future__ import annotations

"""Query EGO training job sample info via POST jobs/sample_info.

Returns model_name, sample_paths, slot_ids for matching training jobs.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import API_PREFIX, JOB_SUCCESS_CODE, get_base_url, handle_error, http_post


def _parse_ids(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def _parse_int_ids(raw: str) -> list[int]:
    result: list[int] = []
    for x in raw.split(","):
        x = x.strip()
        if x:
            try:
                result.append(int(x))
            except ValueError:
                print(f"Warning: skipping non-integer job ID '{x}'", file=sys.stderr)
    return result


def build_request_body(
    *,
    tenant_ids_raw: str,
    tenant_names_raw: str,
    project_ids_raw: str,
    project_names_raw: str,
    job_ids_raw: str,
    job_names_raw: str,
    start: int,
    end: int,
    current: int,
    page_size: int,
) -> dict:
    tenant_ids = _parse_ids(tenant_ids_raw)
    tenant_names = _parse_ids(tenant_names_raw)
    project_ids = _parse_ids(project_ids_raw)
    project_names = _parse_ids(project_names_raw)
    job_ids = _parse_int_ids(job_ids_raw)
    job_names = _parse_ids(job_names_raw)

    has_tenant = tenant_ids or tenant_names
    has_project = project_ids or project_names
    has_job = job_ids or job_names
    if not has_tenant and not has_project and not has_job:
        raise ValueError(
            "at least one of --tenant-ids/--tenant-names, "
            "--project-ids/--project-names, --job-ids/--job-names is required."
        )

    if end > 0 and start > end:
        raise ValueError("--start must be <= --end when --end is specified.")

    body: dict = {}
    if tenant_ids:
        body["ego_tenant_ids"] = tenant_ids
    if tenant_names:
        body["ego_tenant_names"] = tenant_names
    if project_ids:
        body["ego_project_ids"] = project_ids
    if project_names:
        body["ego_project_names"] = project_names
    if job_ids:
        body["job_ids"] = job_ids
    if job_names:
        body["job_names"] = job_names
    if start > 0:
        body["job_start_time_start"] = start
    if end > 0:
        body["job_start_time_end"] = end
    body["current"] = current
    body["page_size"] = page_size
    return body


def main() -> None:
    p = argparse.ArgumentParser(
        description="Query EGO train job sample info (model_name, sample_paths, slot_ids)."
    )
    p.add_argument("--tenant-ids", default="", help="Comma-separated ego_tenant_ids")
    p.add_argument("--tenant-names", default="", help="Comma-separated ego_tenant_names")
    p.add_argument("--project-ids", default="", help="Comma-separated ego_project_ids")
    p.add_argument("--project-names", default="", help="Comma-separated ego_project_names")
    p.add_argument("--job-ids", default="", help="Comma-separated job_ids (int64)")
    p.add_argument("--job-names", default="", help="Comma-separated job_names")
    p.add_argument("--start", type=int, default=0, help="job_start_time_start (Unix sec)")
    p.add_argument("--end", type=int, default=0, help="job_start_time_end (Unix sec)")
    p.add_argument("--current", type=int, default=1, help="Page number (default: 1)")
    p.add_argument("--page-size", type=int, default=200, help="Page size (default: 200)")
    p.add_argument("--base-url", default="", help="Override EGO_BASE_URL")
    p.add_argument("--dry-run", action="store_true", help="Print request body without sending")
    args = p.parse_args()

    try:
        body = build_request_body(
            tenant_ids_raw=args.tenant_ids,
            tenant_names_raw=args.tenant_names,
            project_ids_raw=args.project_ids,
            project_names_raw=args.project_names,
            job_ids_raw=args.job_ids,
            job_names_raw=args.job_names,
            start=args.start,
            end=args.end,
            current=args.current,
            page_size=args.page_size,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(json.dumps(body, indent=2))
        return

    base = (args.base_url or get_base_url()).rstrip("/")
    url = f"{base}{API_PREFIX}/jobs/sample_info"

    try:
        resp = http_post(url, json_body=body)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected response format: top-level JSON must be an object.")
        if data.get("code") != JOB_SUCCESS_CODE:
            raise ValueError(
                f"API code={data.get('code')} msg={data.get('msg', '')} trace_id={data.get('trace_id', '')}"
            )
        print(json.dumps(data, ensure_ascii=False))
    except Exception as e:
        print(handle_error(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
