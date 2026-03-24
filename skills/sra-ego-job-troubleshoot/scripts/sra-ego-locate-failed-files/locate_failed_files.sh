#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <raw_ss_log_file> [output_dir]" >&2
  exit 1
fi

LOG_FILE="$1"
OUT_DIR="${2:-./locate_failed_files_out}"

if [[ ! -f "$LOG_FILE" ]]; then
  echo "Error: log file not found: $LOG_FILE" >&2
  exit 1
fi

if [[ ! -s "$LOG_FILE" ]]; then
  echo "Error: log file is empty: $LOG_FILE" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

TAIL_LOG="$OUT_DIR/log_tail_10000.log"
tail -n 10000 "$LOG_FILE" > "$TAIL_LOG"

OPEN_LINES="$OUT_DIR/open_lines.txt"
FINISH_LINES="$OUT_DIR/finish_lines.txt"
PMSG_START_LINES="$OUT_DIR/pmsg_start_lines.txt"

grep "SampleProcessor start one file" "$TAIL_LOG" > "$OPEN_LINES" || true
grep "SampleProcessor finish one file" "$TAIL_LOG" > "$FINISH_LINES" || true
grep "ParquetMessageReader start one file" "$TAIL_LOG" > "$PMSG_START_LINES" || true

SP_MAP="$OUT_DIR/open_sp_file_thread_reader.tsv"
PMSG_MAP="$OUT_DIR/open_pmsg_file_thread_reader.tsv"
FINISH_FILES="$OUT_DIR/finish_files.txt"
OPEN_FILES="$OUT_DIR/open_files.txt"
SUSPECT_FILES="$OUT_DIR/suspect_files.txt"
SUSPECT_FILE_THREAD_MAP="$OUT_DIR/suspect_file_thread_map.tsv"
THREAD_MATCHED="$OUT_DIR/thread_matched_files.txt"

# format: <file>\t<thread_id>\t<reader_index>
sed -n 's/^[A-Z][0-9]\{4\} [0-9:.]\+[[:space:]]\+\([0-9]\+\).*reader index: \([0-9]\+\).*file name: \([^,]*\).*/\3\t\1\t\2/p' \
  "$OPEN_LINES" | sort -u > "$SP_MAP"

sed -n 's/^[A-Z][0-9]\{4\} [0-9:.]\+[[:space:]]\+\([0-9]\+\).*reader index: \([0-9]\+\).*file: \([^,]*\).*/\3\t\1\t\2/p' \
  "$PMSG_START_LINES" | sort -u > "$PMSG_MAP"

cut -f1 "$SP_MAP" | sort -u > "$OPEN_FILES"
sed -n 's/.*file name: \([^,]*\).*/\1/p' "$FINISH_LINES" | sort -u > "$FINISH_FILES"
comm -23 "$OPEN_FILES" "$FINISH_FILES" > "$SUSPECT_FILES"

fatal_line="$(grep -m1 -E 'Check failed|FATAL|SIGABRT|signal 6' "$TAIL_LOG" || true)"
signal_line="$(grep -m1 -E 'Received signal|SIGABRT|signal 6' "$TAIL_LOG" || true)"
thread_id="$(echo "$fatal_line" | sed -n 's/^[A-Z][0-9]\{4\} [0-9:.]\+[[:space:]]\+\([0-9]\+\)[[:space:]]\+.*/\1/p')"

# Prefer ParquetMessageReader thread mapping for thread match accuracy.
grep -F -f "$SUSPECT_FILES" "$PMSG_MAP" | awk -F $'\t' '{print $1"\t"$2}' | sort -u > "$SUSPECT_FILE_THREAD_MAP" || true
if [[ ! -s "$SUSPECT_FILE_THREAD_MAP" ]]; then
  grep -F -f "$SUSPECT_FILES" "$SP_MAP" | awk -F $'\t' '{print $1"\t"$2}' | sort -u > "$SUSPECT_FILE_THREAD_MAP" || true
fi

if [[ -n "$thread_id" ]]; then
  awk -F $'\t' -v t="$thread_id" '$2==t {print $1}' "$SUSPECT_FILE_THREAD_MAP" | sort -u > "$THREAD_MATCHED" || true
else
  : > "$THREAD_MATCHED"
fi

# Fallback: if thread match is empty, use "same thread in ParquetMessageReader starts" and intersect suspect files.
if [[ -n "$thread_id" && ! -s "$THREAD_MATCHED" ]]; then
  PMSG_THREAD_FILES="$OUT_DIR/pmsg_thread_files.txt"
  awk -F $'\t' -v t="$thread_id" '$2==t {print $1}' "$PMSG_MAP" | sort -u > "$PMSG_THREAD_FILES" || true
  if [[ -s "$PMSG_THREAD_FILES" ]]; then
    comm -12 "$SUSPECT_FILES" "$PMSG_THREAD_FILES" > "$THREAD_MATCHED" || true
  fi
fi

primary_file=""
if [[ -s "$THREAD_MATCHED" ]]; then
  primary_file="$(head -n 1 "$THREAD_MATCHED")"
elif [[ -s "$SUSPECT_FILES" ]]; then
  primary_file="$(head -n 1 "$SUSPECT_FILES")"
fi

suspect_start_line="not found"
finish_line="not found"
if [[ -n "$primary_file" ]]; then
  suspect_start_line="$(grep -E 'ParquetMessageReader start one file|SampleProcessor start one file' "$TAIL_LOG" | grep -F "$primary_file" | head -n 1 || true)"
  if [[ -z "$suspect_start_line" ]]; then
    suspect_start_line="not found"
  fi
  finish_line="$(grep -F "$primary_file" "$FINISH_LINES" | head -n 1 || true)"
  if [[ -z "$finish_line" ]]; then
    finish_line="not found"
  fi
fi

echo "error_class: parquet 文件格式/内容异常（row group 相关）"
echo "thread_id: ${thread_id:-not found}"
echo "suspect_files_count: $(wc -l < "$SUSPECT_FILES")"
echo "suspect_files_file: $SUSPECT_FILES"
echo "suspect_file_thread_map_file: $SUSPECT_FILE_THREAD_MAP"
echo "thread_matched_files_file: $THREAD_MATCHED"
echo "evidence:"
echo "  suspect_start_line: ${suspect_start_line:-not found}"
echo "  finish_line: ${finish_line:-not found}"
echo "  fatal_line: ${fatal_line:-not found}"
echo "  signal_line: ${signal_line:-not found}"
echo "next_action: 请优先检查 thread_matched_files；若为空则检查 suspect_files 列表中的 parquet 完整性和 row group。"
