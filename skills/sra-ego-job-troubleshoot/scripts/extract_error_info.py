#!/usr/bin/env python3
"""Summarize and normalize error info from `extract_error_log.py` output.

Responsibility:
1) Read concrete error-log JSON.
2) Build compact profiling summary.
3) Extract normalized key error lines and FAQ search keywords.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

INSTANCE_RE = re.compile(
    r"([a-z0-9-]+-(worker|wc|ss)-\d+|\b(worker|wc|ss)-\d+\b|uniform_predictor_d[-\w]*)",
    re.IGNORECASE,
)


def _read_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("input JSON must be an object")
    return data


def _find_instances(lines: list[str], limit: int = 10) -> list[str]:
    seen: list[str] = []
    for line in lines:
        for m in INSTANCE_RE.finditer(line):
            token = m.group(1)
            if token and token not in seen:
                seen.append(token)
            if len(seen) >= limit:
                return seen
    return seen


def _dedupe_keep_order(items: list[str], max_items: int) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for it in items:
        key = it.strip()
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
        if len(out) >= max_items:
            break
    return out


def _build_faq_keywords(lines: list[str], role: str) -> list[str]:
    text = "\n".join(lines).lower()
    keywords: list[str] = [role]

    # Generic fatal signals.
    if "check failed" in text:
        keywords.append("Check failed")
    if "signal 6" in text or "sigabrt" in text:
        keywords.append("signal 6")
    if "exitcode" in text:
        keywords.append("exitcode")
    if "oom" in text or "outofmemory" in text:
        keywords.append("OOM")
    if "oomkilled" in text or "exitcode: 137" in text:
        keywords.append("OOMKilled")
    if (
        "cuda out of memory" in text
        or "cudnn_status_alloc_failed" in text
        or "cublas_status_alloc_failed" in text
        or ("resourceexhaustederror" in text and ("oom" in text or "out of memory" in text))
        or "failed to allocate memory on device" in text
    ):
        keywords.append("GPU OOM")
    if "unicodedecodeerror" in text:
        keywords.append("UnicodeDecodeError")
    if "utf-8" in text and "decode" in text:
        keywords.append("utf-8 decode")
    if "httpstarttraining" in text:
        keywords.append("HttpStartTraining")
    if "connection refused" in text:
        keywords.append("connection refused")
    if "failed to start online export" in text:
        keywords.append("failed to start online export")

    # Data / parquet related.
    if "parquet" in text:
        keywords.append("parquet")
    if "parquet_row_group" in text or "row_group" in text:
        keywords.append("parquet_row_group")
    if "mio_info_chunk_array" in text:
        keywords.append("mio_info_chunk_array")

    # Converter / pipeline related.
    if "pipeline failed" in text:
        keywords.append("pipeline failed")
    if "python converter" in text or "converter.py" in text:
        keywords.append("python converter")
    if "cpp-data-converter" in text:
        keywords.append("cpp-data-converter")

    return _dedupe_keep_order(keywords, max_items=12)


def _classify_error(lines: list[str]) -> str:
    text = "\n".join(lines).lower()
    is_gpu_oom = (
        "cuda out of memory" in text
        or "cudnn_status_alloc_failed" in text
        or "cublas_status_alloc_failed" in text
        or ("resourceexhaustederror" in text and ("oom" in text or "out of memory" in text))
        or "failed to allocate memory on device" in text
    )
    is_pod_oom = (
        "oomkilled" in text
        or "exitcode: 137" in text
        or ("killed" in text and "sample_server" in text)
        or "cannot allocate memory" in text
    )

    if is_gpu_oom:
        return "worker_gpu_oom_error"
    if is_pod_oom or "oom" in text or "outofmemory" in text:
        return "pod_memory_oom_error"

    if "httpstarttraining" in text and "connection refused" in text:
        return "online_export_starttraining_connection_refused"
    if "unicodedecodeerror" in text and "utf-8" in text:
        return "source_encoding_or_binary_file_error"
    if "parquet" in text and ("check failed" in text or "row_group" in text or "mio_info_chunk_array" in text):
        return "parquet_data_format_error"
    if "pipeline failed" in text and (
        "python converter" in text or "converter.py" in text or "cpp-data-converter" in text
    ):
        return "data_converter_pipeline_error"
    return "generic_runtime_error"


def summarize(input_obj: dict[str, Any]) -> dict[str, Any]:
    log_meta = input_obj.get("log_meta", {})
    error_log = input_obj.get("error_log", {})
    if not isinstance(log_meta, dict) or not isinstance(error_log, dict):
        raise ValueError("invalid extract_error_log JSON format")

    role = str(error_log.get("role", "unknown"))
    primary_error_lines = error_log.get("primary_error_lines", [])
    fatal_or_signal_lines = error_log.get("fatal_or_signal_lines", [])
    traceback_blocks = error_log.get("traceback_blocks", [])

    if not isinstance(primary_error_lines, list):
        primary_error_lines = []
    if not isinstance(fatal_or_signal_lines, list):
        fatal_or_signal_lines = []
    if not isinstance(traceback_blocks, list):
        traceback_blocks = []

    key_error_lines = _dedupe_keep_order(
        [*fatal_or_signal_lines, *primary_error_lines],
        max_items=80,
    )
    instances = _find_instances(key_error_lines, limit=10)

    profiling = {
        "role": role,
        "line_count": len(primary_error_lines),
        "instances": instances,
        "has_traceback": bool(traceback_blocks),
        "has_pipeline_failed": any("pipeline failed" in str(line).lower() for line in primary_error_lines),
        "has_python_converter_hint": any(
            ("python converter" in str(line).lower()) or ("converter.py" in str(line).lower())
            for line in primary_error_lines
        ),
    }

    extraction = {
        "strategy": str(error_log.get("strategy", "")),
        "brpc_filtered": bool(error_log.get("brpc_filtered", False)),
        "error_class": _classify_error(key_error_lines),
        "traceback_blocks": traceback_blocks[:3],
        "key_error_lines": key_error_lines,
        "faq_keywords": _build_faq_keywords(key_error_lines, role=role),
    }

    return {
        "log_meta": log_meta,
        "profiling": profiling,
        "extraction": extraction,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Summarize and normalize info from extract_error_log.py output"
    )
    p.add_argument(
        "--from-error-log-json",
        required=True,
        help="path to JSON output generated by extract_error_log.py",
    )
    return p


def main() -> int:
    args = build_parser().parse_args()
    try:
        input_obj = _read_json(args.from_error_log_json)
        result = summarize(input_obj)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
