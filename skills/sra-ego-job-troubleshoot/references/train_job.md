# Training Job and Log APIs

This document summarizes the job and log related APIs used in EGO troubleshooting, including job list, job detail, job tasks, job creation, log-file list, log content, and log summary.

---

## Environment and Authentication

### Environment

| Environment | Domain                                | Notes                          |
| ----------- | ------------------------------------- | ------------------------------ |
| **SG**      | `https://ego-portal.mlp.shopee.io`    | Singapore environment, default |
| **US**      | `https://ego-portal.mlp.us.shopee.io` | United States environment      |

All API paths use the prefix `/api/ego/portal`. The scripts in this skill use environment variable `EGO_BASE_URL` to select the base URL. If it is unset, the default is SG. In curl examples, replace `$BASE_URL` with the domain above or with your `EGO_BASE_URL`.

### Authentication

- Method: Cookie `userID` = access token
- Token source: environment variable `USER_ID_OPENAPI` must be set before calling the scripts
- curl examples:
  - `-H "Cookie: userID=$USER_ID_OPENAPI"`
  - `-b "userID=$USER_ID_OPENAPI"`

---

- Status codes:
  - Job APIs use category `14`, with success code `9914100`
  - The log-file list API returns `code: 200` as an integer
  - Log content and log summary endpoints return plain text

## Table of Contents

- [1. Get job list](#1-get-job-list)
- [2. Get job detail](#2-get-job-detail)
- [3. Get job task list](#3-get-job-task-list)
- [4. Create job](#4-create-job)
- [5. Get log-file list](#5-get-log-file-list)
- [6. Get log content](#6-get-log-content)
- [7. Get log summary](#7-get-log-summary)
- [Common: File / Resource / error response](#common-file--resource--error-response)

---

## 1. Get job list

- Path: `GET /api/ego/portal/jobs`
- Notes: paginated query, supporting `list_type`, `scope`, `order` or `orderBy`, and multiple filters.

### Request parameters

| Parameter  | Type   | Required | Notes                                                                                              |
| ---------- | ------ | -------- | -------------------------------------------------------------------------------------------------- |
| current    | int64  | yes      | page number, `>= 1`                                                                                |
| pageSize   | int64  | yes      | page size, `>= 1`                                                                                  |
| list_type  | int64  | no       | `1=train`, `2=release`, `3=online learning`, `4=periodic rule`, `5=recent active`                  |
| scope      | string | no       | `1=all`, `2=personal`                                                                              |
| order      | string | no       | `ascend` / `descend`                                                                               |
| orderBy    | string | no       | `job_id`, `job_name`, `start_time`, `end_time`, `create_time`, `status`, `creator`, `running_time` |
| job_id     | int64  | no       | job ID                                                                                             |
| job_name   | string | no       | fuzzy job name                                                                                     |
| job_status | int64  | no       | `1=pending`, `2=running`, `3=failed`, `4=succeeded`, `5=killed`, etc.                              |
| project_id | string | no       | project ID                                                                                         |
| creator    | string | no       | creator email                                                                                      |
| version_id | int64  | no       | model version ID                                                                                   |
| zone       | string | no       | zone                                                                                               |

### Response

- Success:
  - `code: "9914100"`
  - `data.data` contains the job list
  - `data.info` contains `current`, `pageSize`, and `total`
- Main fields of each job object:
  - `job_id`
  - `job_name`
  - `status`
  - `creator`
  - `create_time`
  - `start_time`
  - `end_time`
  - `running_time`
  - `related_model_name`
  - `related_version_name`
  - `can_scale`
  - `can_stop`
  - `can_delete`
  - `can_dump`
  - `tags`
  - `cost_units`

---

## 2. Get job detail

- Path: `GET /api/ego/portal/job/{job_id}`
- Notes: includes configuration, resources, monitor URLs, and related metadata.

### Response

- Success:
  - `code: "9914100"`
  - `data` contains fields such as:
    - `job_id`
    - `job_name`
    - `status`
    - `config_files`
    - `code_file`
    - `flag_file`
    - `wc_resource`
    - `worker_resource`
    - `sample_server_resource`
    - `train_monitor_url`
    - `train_log_url`
    - `tenant_id`
    - `project_id`
    - `checkpoint_id`
- The `File` structure is defined in [Common](#common-file--resource--error-response).
- The `Resource` structure is defined in [Common](#common-file--resource--error-response).

---

## 3. Get job task list

- Path: `GET /api/ego/portal/job/{job_id}/tasks`
- Notes: returns the task list; when `verbose=true`, it also returns `task_extra`.

### Response

- Success:
  - `data.job_tasks` is an array of tasks
  - each task item contains:
    - `job_task_id`
    - `task_name`
    - `task_type`
    - `task_stauts`
    - `fail_reason`
    - `start_time`
    - `end_time`
    - `last_time`
    - `batch_job_link`

---

## 4. Create job

- Path: `POST /api/ego/portal/job`
- Notes:
  - request body is JSON
  - required fields include `job_name` and `training_job_type`
  - `config_files` must be provided as a `File` array
  - `wc_resource`, `worker_resource`, and related resource fields are `Resource` objects

---

## 5. Get log-file list

- Path: `GET /api/ego/portal/job/{job_id}/log_files`
- Notes:
  - returns the list of log file names under the job
  - the response uses integer `code: 200`, not `9914100`
  - on failure, the endpoint may still return HTTP 200 with plain-text errors such as:
    - `Get UssPath Failed`
    - `Get LogFiles Failed`

---

## 6. Get log content

- Path: `GET /api/ego/portal/job/{job_id}/{log_file_name}`
- Notes:
  - returns plain text
  - usually the last about 1000 lines, with a maximum size of 10 MB
  - on failure, the endpoint may still return HTTP 200 with plain-text errors such as:
    - `GetUssLogFilePath Failed`
    - `Not Found Log File`

---

## 7. Get log summary

- Path: `GET /api/ego/portal/job/{job_id}/log_summary`
- Notes:
  - available only for `failed` or `fail_archived` jobs
  - available in UAT and Live
  - returns plain-text summary
  - non-failed jobs may return `job is not finished`
  - processing failures may return `get log summary failed， please retry after few minutes`

---

## Common: File / Resource / Error Response

### File object (`config_files`, `code_file`, `flag_file`, etc.)

| Field     | Type   | Required | Notes                                             |
| --------- | ------ | -------- | ------------------------------------------------- |
| uss_path  | string | yes      | USS path                                          |
| file_name | string | yes      | file name                                         |
| type      | string | no       | MIME or file type                                 |
| md5       | string | no       | checksum                                          |
| dump_url  | string | no       | download URL, possibly returned by the detail API |

### Resource object (`wc_resource`, `worker_resource`, etc.)

| Field    | Type   | Notes                                                              |
| -------- | ------ | ------------------------------------------------------------------ |
| replicas | int64  | replica count                                                      |
| cpu      | int64  | CPU cores                                                          |
| memory   | int64  | memory in GB                                                       |
| mig_gpu  | string | MIG spec such as `"1"` or `"1g.5gb"`, used together with `gpuType` |
| gpuType  | string | such as `A100` or `V100`, used together with `mig_gpu`             |
| gpu      | int64  | deprecated, prefer `mig_gpu + gpuType`                             |

### Job error response (category 14)

- Success: `9914100`
- Failure uses `9914` plus a specific error code, for example:
  - `9914101`: unauthorized
  - `9914102`: forbidden
  - `9914103`: not found
  - `9914107`: bad request
  - `9914108`: required parameter missing
- Time fields use millisecond timestamps.
