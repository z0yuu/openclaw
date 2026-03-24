# sra-ego-job-troubleshoot scripts

This directory contains two groups of scripts:

1. EGO OpenAPI local orchestration scripts, which replace MCP tool calls
2. Ego FAQ retrieval scripts

## 1) EGO OpenAPI local orchestration scripts

These scripts call EGO Portal HTTP APIs directly inside the skill and do not depend on `mcp_server`.

- `list_jobs.py`: equivalent to `ego_list_jobs`
- `get_job.py`: equivalent to `ego_get_job`
- `get_job_tasks.py`: equivalent to `ego_get_job_tasks`
- `diagnose_soc_job.py`: SOC job status diagnosis with `soc_project_id` and `soc_job_id`
- `get_log_summary.py`: equivalent to `ego_get_log_summary`; retained helper, not used by the default `sra-ego-job-troubleshoot` main flow
- `get_job_log_files.py`: equivalent to `ego_get_job_log_files`
- `get_log_content.py`: equivalent to `ego_get_log_content`; retained helper
- `get_uss_file.py`: equivalent to `ego_get_uss_file`
- `get_confluence.py`: read the body of a specific Confluence page by pageId, title, or URL
- `inspect_model_code_encoding.py`: compile-stage `UnicodeDecodeError` check; downloads code zip by job, unpacks it, and checks UTF-8 or AppleDouble pseudo files
- `compare_model_config.py`: compare current-job and checkpoint-source `model_config.readable` files, then emit structured slot-group and `dnn_slices` differences
- `extract_error_log.py`: stage-1 error extraction; fetch logs, tail N lines, and extract role-specific concrete errors
- `extract_error_info.py`: stage-2 summary extraction; profile and extract from the output of `extract_error_log.py`, then generate FAQ keywords
- `ego_api_common.py`: shared HTTP client and auth logic

### Environment

- Required: `USER_ID_OPENAPI`
- Optional: `EGO_BASE_URL` with default `https://ego-portal.mlp.shopee.io`

### Shell compatibility notes

- For additional log inspection, use the structured extraction scripts in this directory first, then inspect files directly when necessary.

### `extract_error_log.py` rules, stage 1

- Input: `job_id`, `log_file_name`, and failed-instance role such as `worker`, `ss`, or `wc`
- Internal steps: fetch logs, tail the last N lines with default `10000`, then output concrete error information
- `worker` or `wc`: prioritize tail-stack-first scanning on the end of the log
- `ss`: if `pipeline failed` and `python converter` or `cpp-data-converter` clues are present, first filter brpc-style noise, then extract the error
- Output JSON includes:
  - `log_meta`
  - `error_log.strategy` and `error_log.brpc_filtered`
  - `error_log.traceback_blocks`
  - `error_log.primary_error_lines`
  - `error_log.fatal_or_signal_lines`

### `extract_error_info.py` rules, stage 2

- Input: `--from-error-log-json <stage1_json>`
- Internal steps: extract structured summary and FAQ search keywords from stage-1 concrete error information
- Output JSON includes:
  - `profiling`, including role, instance identification, traceback, pipeline-failed, and python-converter signals
  - `extraction.error_class`
  - `extraction.key_error_lines`
  - `extraction.faq_keywords`, which can be fed directly to `search_ego_faq.py`

Online-export special classification:

- If `HttpStartTraining` plus `connection refused` is matched, `error_class` is classified as `online_export_starttraining_connection_refused`.
- For this class, continue with `get_job_tasks.py` and worker, SS, and WC logs to determine readiness. Do not reduce it to generic network jitter.

### `diagnose_soc_job.py` rules

- Use when `soc_project_id` and `soc_job_id` are already known and you need SOC status and duration diagnosis.
- Logic:
  - query SOC API `/api/job/v1/projects/{soc_project_id}/jobs/{soc_job_id}`
  - output SOC diagnosis and duration fields
- Time fields:
  - `soc_elapsed_from_create_minutes`: `now - data.createTime` in minutes
  - `soc_running_minutes`: `now - data.startTime` in minutes, or `0` if `data.startTime=0`
- Status diagnosis:
  - `killed`: return only `soc_status=killed` and the diagnosis text; do not return duration fields
  - `scheduling`: `SOC job 已经调度了XXX 分钟, 如果时长超过5分钟，请联系SOC同学`
  - `queueing`: `由于资源不足，当前SOC JOB还在排队等待资源。`
  - `running`: `SOC JOB已经处于running状态，运行了XXX分钟`

## 2) search_ego_faq.py

This script locates a specific question in Ego FAQ from keywords and returns only content related to that question, or an empty result. It must not return the whole FAQ page. Matching is approximate, not exact, and returns at most three results.

Ego FAQ structure:

- the root page is a question index such as Q1, Q2, Q12
- each question contains either a direct answer or a link to another Confluence page
- the script maps keywords to the question, then returns only that question body from the FAQ root page
- if nothing matches, it returns empty

Usage:

- default path is Confluence API and requires `CONFLUENCE_TOKEN`
- do not use local files unless explicitly required

```bash
# keywords as positional args
python scripts/search_ego_faq.py keyword1 keyword2

# or use --query with space-separated keywords
python scripts/search_ego_faq.py --query "GPU tuning"

# JSON output
python scripts/search_ego_faq.py --query "error code" --json

# use a local saved FAQ HTML only when explicitly needed
python scripts/search_ego_faq.py --local-file /path/to/Ego+FAQ.html --query "keyword"

# print parsed-block count and fallback mode for debugging
python scripts/search_ego_faq.py --query "keyword" -v
```

Parsing logic:

- first parse real Confluence structure such as `<h3 id="EgoFAQ-Q1...">` or headings starting with `Q<number>.` or `Q<number>:`
- if that fails, fall back to whole-page paragraph parsing
- if the local file is a browser “save as” wrapper made of many `td.line-content` cells, the script auto-joins them back into parsable HTML

Failed-file-location fallback:

- when keywords include semantics such as `报错文件`, `定位文件`, `parquet_row_group`, `parquet`, `python converter`, `cpp-data-converter`, or `pipeline failed`, the script first tries to route to the tutorial page `pageId=2668250345`
- it returns the tutorial link instead of breaking the flow

Environment variables:

- `CONFLUENCE_TOKEN`: Confluence Bearer Token

Confluence base URL is fixed to `https://confluence.shopee.io` and does not need extra config.

## 3) get_confluence.py

Read one Confluence page body. This is used by troubleshooting cases that need document-point extraction.

Usage:

```bash
# by pageId
python scripts/get_confluence.py --page-id 2668250345 --json

# by URL, auto-parse pageId or title
python scripts/get_confluence.py --url "https://confluence.shopee.io/display/MLP/How+to+clip+or+map+nn+parameters" --json

# write to file
python scripts/get_confluence.py --url "https://confluence.shopee.io/display/MLP/How+to+clip+or+map+nn+parameters" --json --output /tmp/page.json
```

Dependencies:

```bash
# FAQ retrieval optional dependencies
# pip install html2text
# pip install rapidfuzz
# pip install beautifulsoup4
```
