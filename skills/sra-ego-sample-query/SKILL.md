---
name: sra-ego-sample-query
description: >
  Query EGO training job sample information (EGO 训练任务样本信息查询) — model names, sample paths, and slot IDs. Supports filtering by tenant/project/job ID or name.
  TRIGGER when: user mentions "样本信息", "sample info", "sample path", "样本路径", "slot_ids", "slot ID", "training sample", "训练样本", "查询样本", or asks about EGO job sample data, model sample paths, or slot information.
  DO NOT TRIGGER when: user wants to submit a new training job, troubleshoot a failed job, analyze training metrics, or query job details without sample information.
---

# EGO Training Job Sample Info Query (训练任务样本信息查询)

## Prerequisites

- **USER_ID_OPENAPI** (required): EGO access token — the `userID` value from your Cookie.
- **EGO_BASE_URL** (optional): Portal URL, defaults to `https://ego-portal.mlp.shopee.io`; use `https://ego-portal.mlp.us.shopee.io` for US region.

## Scripts

Scripts are located in `scripts/`. The working directory must be **this skill's root directory** (`sra-ego-sample-query`). Invoke as `python scripts/<script> [options]`.

| Script                         | Purpose                                                |
| ------------------------------ | ------------------------------------------------------ |
| `scripts/_common.py`           | Shared helpers: auth, HTTP client, error handling      |
| `scripts/query_sample_info.py` | Query `POST /api/ego/portal/jobs/sample_info` endpoint |

---

## API Reference

### Endpoint

`POST /api/ego/portal/jobs/sample_info`

### Request Body

| Field                  | Type     | Required | Default | Description                                                     |
| ---------------------- | -------- | -------- | ------- | --------------------------------------------------------------- |
| `ego_tenant_ids`       | string[] | —        | —       | Tenant IDs (租户 ID)                                            |
| `ego_tenant_names`     | string[] | —        | —       | Tenant names (租户名称)                                         |
| `ego_project_ids`      | string[] | —        | —       | Project IDs (项目 ID)                                           |
| `ego_project_names`    | string[] | —        | —       | Project names (项目名称)                                        |
| `job_ids`              | int64[]  | —        | —       | Job IDs                                                         |
| `job_names`            | string[] | —        | —       | Job names (任务名称)                                            |
| `job_start_time_start` | int64    | —        | 0       | Lower bound of time window (Unix sec, inclusive); 0 = no filter |
| `job_start_time_end`   | int64    | —        | 0       | Upper bound of time window (Unix sec, inclusive); 0 = no filter |
| `current`              | int64    | —        | 1       | Page number                                                     |
| `page_size`            | int64    | —        | 200     | Page size (conservative default; increase as needed)            |

**Validation rules:**

- **At least one** of tenant (IDs/names), project (IDs/names), or job (IDs/names) must be provided.
- When `job_start_time_end > 0`, `job_start_time_start` must be ≤ `job_start_time_end`.

### Response Body

Top-level wrapper:

```json
{
  "code": "9914100",
  "data": { "data": [...], "info": {...} },
  "msg": "trace_id=...",
  "trace_id": "..."
}
```

Success code: `"9914100"`.

`data.data[]` item fields:

| Field              | Type     | Description                                         |
| ------------------ | -------- | --------------------------------------------------- |
| `job_id`           | int64    | Job ID                                              |
| `ego_tenant_id`    | string   | Tenant ID (租户 ID)                                 |
| `ego_tenant_name`  | string   | Tenant name (租户名称)                              |
| `ego_project_id`   | string   | Project ID (项目 ID)                                |
| `ego_project_name` | string   | Project name (项目名称)                             |
| `job_name`         | string   | Job name (任务名称)                                 |
| `job_start_time`   | int64    | Job start time (Unix sec)                           |
| `model_name`       | string   | Model name (模型名称)                               |
| `sample_paths`     | string[] | Sample paths (样本路径); empty array `[]` when none |
| `slot_ids`         | string[] | Slot IDs; empty array `[]` when none                |

`data.info` (pagination):

| Field      | Type  | Description           |
| ---------- | ----- | --------------------- |
| `current`  | int64 | Current page number   |
| `pageSize` | int64 | Page size (camelCase) |
| `total`    | int64 | Total record count    |

### Query Behavior

- All provided filter fields are combined with **AND** logic.
- Multiple values within the same field use **OR** logic (ES `terms` query), e.g. `job_names: ["a", "b"]` matches job name "a" OR "b".
- Results are sorted by `job_start_time` **descending**.

---

## Workflow

### Step 1 — Parse user input

Extract filtering parameters from the user's query. **At least one** of the following groups is required:

| Group          | By ID             | By Name             |
| -------------- | ----------------- | ------------------- |
| Tenant (租户)  | `ego_tenant_ids`  | `ego_tenant_names`  |
| Project (项目) | `ego_project_ids` | `ego_project_names` |
| Job (任务)     | `job_ids` (int64) | `job_names`         |

- Users can query by **name directly** — no need to resolve names to IDs first.
- **Only provide groups the user explicitly mentions.** For example, if the user only gives a job name, pass `--job-names` and leave tenant/project flags empty — do NOT invent or require additional filters.

Optional time window — when the user mentions a relative time range (e.g. "最近三小时", "last 3 hours"), calculate Unix timestamps accordingly:

| Parameter | Description                                     |
| --------- | ----------------------------------------------- |
| `start`   | `job_start_time_start` — lower bound (Unix sec) |
| `end`     | `job_start_time_end` — upper bound (Unix sec)   |

### Step 2 — Execute query

```bash
# Query by job name only (tenant/project not required)
python scripts/query_sample_info.py \
  --job-names "daily_train_v2,daily_train_v3"

# Query with multiple filters (AND logic across fields)
python scripts/query_sample_info.py \
  --tenant-ids "tid1,tid2" \
  --project-ids "pid1" \
  --job-ids "123,456" \
  --start 1700000000 --end 1700100000 \
  --page-size 20
```

| Flag              | Default   | Notes                                                      |
| ----------------- | --------- | ---------------------------------------------------------- |
| `--tenant-ids`    | —         | Comma-separated tenant IDs                                 |
| `--tenant-names`  | —         | Comma-separated tenant names (租户名称)                    |
| `--project-ids`   | —         | Comma-separated project IDs                                |
| `--project-names` | —         | Comma-separated project names (项目名称)                   |
| `--job-ids`       | —         | Comma-separated job IDs (int64)                            |
| `--job-names`     | —         | Comma-separated job names (任务名称)                       |
| `--start`         | 0         | `job_start_time_start` (Unix sec); 0 = no filter           |
| `--end`           | 0         | `job_start_time_end` (Unix sec); 0 = no filter             |
| `--current`       | 1         | Page number                                                |
| `--page-size`     | 200       | Page size (default conservative value; increase as needed) |
| `--base-url`      | env or SG | Override `EGO_BASE_URL`                                    |
| `--dry-run`       | —         | Print request body without sending                         |

### Step 3 — Present results

Parse `data.data` for records and `data.info` for pagination. Display a Markdown table:

| #   | Job (任务)     | Tenant (租户) | Project (项目) | Model Name (模型名称) | Sample Paths (样本路径)      | Slots    |
| --- | -------------- | ------------- | -------------- | --------------------- | ---------------------------- | -------- |
| 1   | daily_train_v2 | my_tenant     | my_project     | my_model              | /path/to/day1, /path/to/day2 | 100, 101 |
| 2   | daily_train_v3 | my_tenant     | my_project     | bert_base             | /path/to/day3                | 200      |

Pagination: Page 1 / 10 (100 total)

**Rules:**

- Convert `job_start_time` (Unix seconds) to human-readable format.
- Join `sample_paths` and `slot_ids` with commas; show `(none)` when the array is empty.
- If `data.data` is `[]`, prompt the user to verify filter conditions and permissions.

---

## Error Handling

| Scenario                  | Action                                                                         |
| ------------------------- | ------------------------------------------------------------------------------ |
| Missing `USER_ID_OPENAPI` | Script exits with an error message; prompt the user to set the env var         |
| HTTP 401 / 403            | Unauthorized or permission denied; verify token and tenant/project access      |
| HTTP 4xx / 5xx            | Report status code and truncated body; suggest retrying or checking parameters |
| Empty results             | Prompt user to verify tenant/project IDs, job IDs, and time window             |

## Python 版本

- 此 skill 的 Python 脚本按 **Python 3.8+** 使用。
- 当前脚本静态扫描未发现要求 3.9+/3.10+ 的语法，可按 3.8 基线处理。
