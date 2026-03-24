---
name: sra-ego-locate-failed-files
description: >
  EGO failed data-file locator (EGO 失败数据文件定位) — locate concrete parquet or converter input files from raw SS logs with thread-aware matching.
  TRIGGER when: logs mention parquet corruption, converter pipeline failures, `pipeline failed`, or the user asks to locate the exact failed parquet or data file from SS raw logs.
  DO NOT TRIGGER when: the failure is already narrowed to a non-data-file root cause or only needs high-level summary without raw-log file localization.
---

# Role

This sub-skill locates concrete data files for parquet or converter-related failures.

---

# Trigger

- parquet format failures such as `Check failed: parquet_row_group...`
- or `pipeline failed` involving `python converter` or `cpp-data-converter`
- and the main flow has not yet identified a concrete failed file path

---

# Inputs

- Required: `log_file` (full raw log from the failed SS instance)
- Optional: `output_dir` (default `./locate_failed_files_out`)

---

# Preconditions

- You must use the raw log from the failed instance. Do not replace it with a summary or any secondary excerpt.
- Run commands from the skill root directory.
- Required helper script:
  - `scripts/sra-ego-locate-failed-files/locate_failed_files.sh`
- If the raw log comes from a remote API such as `get_log_content`, you must first save it to a local file, then verify that the file exists and is non-empty before invoking the helper script.

---

# Workflow

1. Primary branch: materialize and validate the raw log, then run the helper script

```bash
# Example: save raw SS log locally first
python scripts/get_log_content.py <job_id> <failed_ss_log_name> > /tmp/failed_ss.log
test -s /tmp/failed_ss.log
```

Only after the local file exists and is non-empty, run:

```bash
chmod +x scripts/sra-ego-locate-failed-files/locate_failed_files.sh
bash scripts/sra-ego-locate-failed-files/locate_failed_files.sh <raw_ss_log_file> [output_dir]
```

The script automatically:

1. takes the last 10,000 lines
2. computes `suspect_files = open - finish`
3. extracts the fatal `thread_id`
4. cross-matches `thread_id` with suspect files
5. writes the evidence files

6. Fallback branch: no direct thread match

- If `thread_matched_files` is empty, fall back to the intersection between the last processed files and `suspect_files`.
- Record that the fallback branch was used.

3. Last-resort branch: still cannot isolate one file

- If the file still cannot be located after the fallback branch, output `未能从日志直接定位具体文件，请EGO同学介入`.
- Preserve the intermediate evidence files so the next investigator can continue from them.

---

# Hard Rules

- Never run raw-log download/materialization and `locate_failed_files.sh` in parallel when the latter depends on the former's output file.
- You must produce all three result sets before concluding:
  - `suspect_files`
  - `suspect_file_thread_map`
  - `thread_matched_files`
- If `thread_matched_files` is empty, fall back to the intersection between the last processed files and `suspect_files`.
- If the file still cannot be located, output `未能从日志直接定位具体文件，请EGO同学介入`.
- Do not invoke the helper shell script from inside `sub-skills/`; use `scripts/sra-ego-locate-failed-files/locate_failed_files.sh` from the skill root.

---

# Output Contract

- `case_type`: `locate_failed_files`
- `error_class`: `parquet_or_converter_file_location`
- `thread_id`: <fatal thread id or `not found`>
- `suspect_files`: <list>
- `suspect_file_thread_map`: <mapping>
- `thread_matched_files`: <list>
- `evidence`:
  - `suspect_start_line`
  - `finish_line`
  - `fatal_line`
  - `signal_line`
