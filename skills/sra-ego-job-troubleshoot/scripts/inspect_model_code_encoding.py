#!/usr/bin/env python3
"""Inspect model code package encoding issues for compile UnicodeDecodeError cases."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any

from ego_api_common import EgoApiError, download_uss_file, get_job


TEXT_EXTS = {
    ".py",
    ".txt",
    ".md",
    ".yaml",
    ".yml",
    ".json",
    ".cfg",
    ".ini",
    ".conf",
    ".sh",
    ".sql",
    ".proto",
    ".xml",
}


def _is_appledouble(rel_path: str, content: bytes) -> bool:
    rel = rel_path.replace("\\", "/")
    if "/__MACOSX/" in f"/{rel}" and "/._" in f"/{rel}":
        return True
    # AppleDouble magic: 00 05 16 07
    return content.startswith(b"\x00\x05\x16\x07")


def _looks_text(rel_path: str) -> bool:
    return Path(rel_path).suffix.lower() in TEXT_EXTS


def _decode_utf8(content: bytes) -> tuple[bool, str | None]:
    try:
        content.decode("utf-8")
        return True, None
    except UnicodeDecodeError as e:
        return False, f"{e}"


def _resolve_dump_url(job_id: int, dump_url: str | None, base_url: str | None, timeout: float) -> tuple[str, dict[str, Any] | None]:
    if dump_url:
        return dump_url, None
    job = get_job(job_id, base_url=base_url, timeout=timeout)
    code_files = job.get("code_file") or []
    if not code_files:
        raise EgoApiError(f"job_id={job_id} has no code_file in job payload")
    first = code_files[0] if isinstance(code_files, list) else {}
    url = first.get("dump_url")
    if not url:
        raise EgoApiError(f"job_id={job_id} code_file dump_url is empty")
    return str(url), job


def inspect_archive(zip_path: Path, extract_dir: Path) -> dict[str, Any]:
    extract_dir.mkdir(parents=True, exist_ok=True)
    invalid_entries: list[dict[str, Any]] = []
    text_entries: list[dict[str, Any]] = []
    all_entries: list[str] = []

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)
        for info in zf.infolist():
            if info.is_dir():
                continue
            rel = info.filename
            all_entries.append(rel)
            content = zf.read(info)
            apple_double = _is_appledouble(rel, content)
            is_text_like = _looks_text(rel)
            valid_utf8, error = _decode_utf8(content)

            if is_text_like:
                text_entries.append(
                    {
                        "path": rel,
                        "size": info.file_size,
                        "valid_utf8": valid_utf8,
                        "appledouble": apple_double,
                        "decode_error": error,
                    }
                )

            if (is_text_like and not valid_utf8) or apple_double:
                invalid_entries.append(
                    {
                        "path": rel,
                        "size": info.file_size,
                        "text_like": is_text_like,
                        "appledouble": apple_double,
                        "decode_error": error,
                    }
                )

    likely_cause = any(item["appledouble"] or item.get("decode_error") for item in invalid_entries)
    return {
        "archive_entries_count": len(all_entries),
        "text_entries_count": len(text_entries),
        "invalid_entries": invalid_entries,
        "likely_unicode_decode_cause": likely_cause,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Download and inspect model code archive for UTF-8 issues")
    p.add_argument("job_id", type=int, help="EGO job id")
    p.add_argument("--dump-url", type=str, default="", help="Optional code dump_url; if absent, resolve from get_job")
    p.add_argument("--tmp-dir", type=str, default="", help="Optional output dir; defaults to /tmp/job_code_inspect_<job_id>")
    p.add_argument("--base-url", type=str, default=None, help="Optional EGO base URL override")
    p.add_argument("--timeout", type=float, default=60.0)
    return p


def main() -> int:
    args = build_parser().parse_args()
    try:
        out_dir = Path(args.tmp_dir) if args.tmp_dir else Path(f"/tmp/job_code_inspect_{args.job_id}")
        out_dir.mkdir(parents=True, exist_ok=True)
        dump_url, job_payload = _resolve_dump_url(args.job_id, args.dump_url or None, args.base_url, args.timeout)

        zip_path = out_dir / "model_code.zip"
        dl = download_uss_file(dump_url, str(zip_path), timeout=args.timeout)
        extract_dir = out_dir / "unzipped"
        result = inspect_archive(zip_path, extract_dir)

        output = {
            "job_id": args.job_id,
            "dump_url": dump_url,
            "download": dl,
            "workspace": str(out_dir),
            "extract_dir": str(extract_dir),
            "job_status": (job_payload or {}).get("status"),
            **result,
        }
        print(json.dumps(output, ensure_ascii=False))
        return 0
    except (EgoApiError, OSError, zipfile.BadZipFile, RuntimeError, ValueError) as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
