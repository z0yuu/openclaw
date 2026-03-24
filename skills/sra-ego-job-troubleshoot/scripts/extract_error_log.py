#!/usr/bin/env python3
"""Fetch failed-instance log and extract concrete error lines.

Responsibility:
1) Fetch raw log from EGO API.
2) Keep only tail N lines (default 10000).
3) Apply role-specific error-log filtering and return concrete error evidence.

This script does NOT do FAQ-oriented summarization. Use `extract_error_info.py`
on this script's JSON output for structured summary and keyword generation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

from ego_api_common import EgoApiError, get_log_content

ROLE_CHOICES = ("worker", "ss", "wc")

PIPELINE_FAILED_RE = re.compile(r"pipeline\s+failed", re.IGNORECASE)
PYTHON_CONVERTER_RE = re.compile(r"python\s+converter|converter\.py|run converter|cpp-data-converter", re.IGNORECASE)
TRACEBACK_START_RE = re.compile(r"^Traceback \(most recent call last\):", re.MULTILINE)

# Concrete error indicators in raw logs.
ERROR_LINE_RE = re.compile(
    r"(Check failed|FATAL|ERROR|Exception|RuntimeError|ValueError|TypeError|OOM|OutOfMemory|"
    r"SIGABRT|SIGKILL|signal\s+\d+|exitcode|killed|pipeline\s+failed|python\s+converter|"
    r"cpp-data-converter|error code:|HttpStartTraining|CoordinatorService|connection refused|"
    r"failed to start online export|dial tcp)",
    re.IGNORECASE,
)


def _tail_lines(text: str, n: int) -> str:
    if n <= 0:
        return text
    lines = text.splitlines()
    return "\n".join(lines[-n:])


def _filter_out_info_lines(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.startswith("I"))


def _extract_traceback_blocks(lines: list[str], max_blocks: int = 3) -> list[str]:
    blocks: list[str] = []
    n = len(lines)
    i = 0
    while i < n and len(blocks) < max_blocks:
        if TRACEBACK_START_RE.search(lines[i]):
            j = i + 1
            while j < n:
                if lines[j].strip() == "" and j > i + 1:
                    break
                if j > i + 150:
                    break
                j += 1
            block = "\n".join(lines[i:j]).strip()
            if block:
                blocks.append(block)
            i = j
            continue
        i += 1
    return blocks


def _collect_error_lines(lines: list[str], max_lines: int) -> list[str]:
    out: list[str] = []
    for line in lines:
        if ERROR_LINE_RE.search(line):
            out.append(line)
        if len(out) >= max_lines:
            break
    return out


def _extract_error_log(tail_text: str, role: str, max_error_lines: int) -> dict[str, Any]:
    has_pipeline_failed = bool(PIPELINE_FAILED_RE.search(tail_text))
    has_python_converter = bool(PYTHON_CONVERTER_RE.search(tail_text))

    strategy = "tail-stack-first" if role in ("worker", "wc") else "ss-pipeline-converter-aware"
    brpc_filtered = bool(role == "ss" and has_pipeline_failed and has_python_converter)
    working_text = _filter_out_info_lines(tail_text) if brpc_filtered else tail_text
    working_lines = working_text.splitlines()

    # worker/wc: focus on log tail stack; ss: slightly wider window for converter/pipeline failures.
    inspect_window = 600 if role in ("worker", "wc") else 900
    inspect_lines = working_lines[-inspect_window:] if len(working_lines) > inspect_window else working_lines

    traceback_blocks = _extract_traceback_blocks(inspect_lines, max_blocks=3)
    primary_error_lines = _collect_error_lines(inspect_lines, max_lines=max_error_lines)

    if not primary_error_lines and not traceback_blocks:
        # Final fallback: keep the last 80 lines so downstream has concrete text.
        primary_error_lines = inspect_lines[-80:]

    fatal_or_signal_lines = [
        line
        for line in primary_error_lines
        if re.search(r"Check failed|FATAL|signal\s+\d+|SIGABRT|SIGKILL|exitcode", line, re.IGNORECASE)
    ][:20]

    return {
        "role": role,
        "strategy": strategy,
        "brpc_filtered": brpc_filtered,
        "has_pipeline_failed": has_pipeline_failed,
        "has_python_converter_hint": has_python_converter,
        "traceback_blocks": traceback_blocks,
        "primary_error_lines": primary_error_lines,
        "fatal_or_signal_lines": fatal_or_signal_lines,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch failed-instance log and extract concrete error lines"
    )
    parser.add_argument("job_id", type=int)
    parser.add_argument("log_file_name", type=str)
    parser.add_argument("--role", required=True, choices=ROLE_CHOICES, help="failed instance role")
    parser.add_argument("--base-url", type=str)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument(
        "--tail-lines",
        type=int,
        default=10000,
        help="use only the last N lines for extraction (default: 10000; 0 = full log)",
    )
    parser.add_argument(
        "--max-error-lines",
        type=int,
        default=120,
        help="max concrete error lines in output (default: 120)",
    )
    parser.add_argument(
        "--save-log-file",
        type=str,
        help="optional path to save the tail summary used for extraction",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        raw_log = get_log_content(
            args.job_id,
            args.log_file_name,
            base_url=args.base_url,
            timeout=args.timeout,
        )
    except EgoApiError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    tail_text = _tail_lines(raw_log, args.tail_lines)
    if args.save_log_file:
        try:
            with open(args.save_log_file, "w", encoding="utf-8") as f:
                f.write(tail_text)
        except OSError as e:
            print(f"Error: failed to save log file: {e}", file=sys.stderr)
            return 1

    error_log = _extract_error_log(
        tail_text=tail_text,
        role=args.role,
        max_error_lines=args.max_error_lines,
    )
    result = {
        "log_meta": {
            "job_id": args.job_id,
            "log_file_name": args.log_file_name,
            "tail_lines": args.tail_lines,
            "tail_line_count": len(tail_text.splitlines()),
        },
        "error_log": error_log,
    }

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
