---
name: sra-ego-parquet-totxt
description: >
  EGO Parquet to Text (Parquet 本地转文本) — read parquet samples from HDFS locally through fixed runtime image mapping and optionally pipe them through a converter.
  TRIGGER when: user mentions "parquet", "读取 parquet", "解析 parquet", "hdfs parquet", "parquet sample", "converter.py", or asks to inspect rows from `hdfs://R2...` or `hdfs://D2...`.
  DO NOT TRIGGER when: user is asking about training job execution, model compile, or job failure diagnosis unrelated to reading parquet samples.
block_until_ms: 600000
---

# EGO Parquet to Text

## Skill Scope

This skill reads parquet samples locally by starting a fixed runtime image in Docker, and can optionally pipe the output through `python converter.py`.

Target output:

- parsed sample content, defaulting to the first 10 rows

## Routing Boundary

- Use this skill when the user wants to read or inspect HDFS parquet samples, with or without a converter.
- Do not use this skill for training job execution, model compile, or job failure diagnosis. Route those requests to the corresponding skill.

## Trigger

Typical trigger requests:

- "Parse a parquet file"
- "Read the first few rows from an HDFS parquet file"
- "Read parquet and convert it with converter.py"
- "Show me samples from hdfs://R2..."

## Interaction Policy

1. Extract parameters from natural language first, then ask follow-up questions only for missing fields.
2. Do not run any command before the required `hdfs_path` is available.
3. Do not guess the HDFS path. Only use values explicitly provided by the user or unambiguously extracted from context.
4. `rows` may default to `10`; other fields should only be auto-filled when they are certain.
5. If the user says "use converter.py" without giving a path, ask for the script file path or script directory path.

## Step 1: Collect Inputs

### 1.0 Required / Optional Inputs

Required:

- `hdfs_path`: must be an HDFS path, and only the following prefixes are supported:
  - `hdfs://R2...`
  - `hdfs://D2...`

Optional:

- `rows`: number of rows to print, default `10`
- `pipe_cmd`: pipeline command, for example `| python converter.py`
- `script_path`: converter file path or script directory path
  - if `pipe_cmd` is not provided, the converter pipeline may be inferred from this path

### 1.1 Natural Language Extraction First (mandatory)

Before asking follow-up questions, first extract from the user text:

1. `hdfs_path`

- match `hdfs://...`
- if not found, ask the user

2. `rows`

- extract `N` from phrases such as "first N rows", "show N rows", or equivalent Chinese phrasing
- otherwise default to `10`

3. `pipe_cmd`

- if the text contains `| ...`, extract the full pipeline fragment directly
- if it contains `python xxx.py`, map it to `| python xxx.py`
- if `pipe_cmd` is not extracted but `script_path` is provided, infer the converter pipeline automatically
- if neither `pipe_cmd` nor `script_path` is available, default to plain parquet sample output only

4. `script_path`

- extract it when the text contains a full `*.py` path
- if only a file name is provided without a path, do not guess; ask the user
- if only `script_path` is provided without `pipe_cmd`, infer the converter command:
  - file path: `| python <file_name>`
  - directory path: if `converter.py` exists, use `| python converter.py`

### 1.2 Missing Input Prompt Template

When input is incomplete, use:

```text
Please provide parquet read parameters:
- hdfs_path (required, must be hdfs://R2... or hdfs://D2...)
- rows (optional, default 10)
- pipe_cmd (optional, for example: | python converter.py)
- script_path (optional; if the converter depends on multiple files, prefer giving a directory)
```

## Step 2: Validate Inputs

Validate the following before execution:

1. `hdfs_path` must start with `hdfs://`.
2. `hdfs_path` must use the `R2` or `D2` prefix; otherwise stop with an error.
3. `rows` must be a positive integer.
4. If `script_path` is provided, the path must exist.
5. If `pipe_cmd` is not provided but `script_path` is given, infer the converter pipeline automatically; otherwise fall back to plain parquet output.

## Step 3: Resolve Runtime Image (fixed rule)

Fixed mapping:

- `hdfs://R2` -> `harbor.shopeemobile.com/mlp-ego/ego-train-runtime:V1.8.4.2-tf1-sg-20251118063218`
- `hdfs://D2` -> `harbor.shopeemobile.com/mlp-ego/ego-train-runtime:V1.8.4.2-tf1-us-20251118063218`

The user may not override this mapping rule.

## Step 4: Execute Script

Use the following entry point:

```bash
bash scripts/read_parquet_local.sh \
  --hdfs-path "<hdfs_path>" \
  [--rows <rows>] \
  [--pipe-cmd "<pipe_cmd>"] \
  [--script-path "<script_path>"] \
  [--output-file "<output_file>"]
```

Core command inside the script:

```bash
export HADOOP_HOME=/usr/share/hadoop-client; \
export CLASSPATH=$(hadoop classpath); \
export HADOOP_HDFS_HOME=/usr/share/hadoop-2.10; \
/workspace/ego-train-v1/bin/parquet-message-reader-printer --hdfs_file_path=<hdfs_path> \
| <pipe_cmd_if_any>
```

Execution behavior:

- if `script_path` is a directory, mount the directory and execute inside it, supporting multi-file dependencies
- if `script_path` is a single file, mount its parent directory and execute as a single-file converter
- if `output_file` is not provided, automatically write to `<system-temp>/sra-ego-parquet-totxt-*/sample_output.txt` instead of the current directory
- stop the upstream reader process as soon as the requested `rows` count is reached; do not wait for the full dataset to finish streaming

## Step 5: Response Contract

The final response must include at least:

- `hdfs_path`
- `resolved_image`
- `rows`
- `pipe_cmd` (if present)
- a short command summary
- `output_file` (sample result file)
- `stderr_log` (execution log file)

## Failure Handling

On failure, clearly explain the reason and the next step:

- `hdfs_path_missing`: missing HDFS path
- `hdfs_prefix_invalid`: path does not start with `hdfs://` or does not use `R2/D2`
- `rows_invalid`: invalid row count
- `script_path_not_found`: script path does not exist
- `docker_runtime_error`: Docker, image, or command execution failure
