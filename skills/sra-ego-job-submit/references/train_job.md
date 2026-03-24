# 训练作业与日志 API

作业（Job）及日志相关接口：列表、详情、任务、创建、日志文件列表、日志内容、日志摘要。

---

## 环境与认证

### 环境

| 环境        | 域名                                  | 说明               |
| ----------- | ------------------------------------- | ------------------ |
| **SG 环境** | `https://ego-portal.mlp.shopee.io`    | 新加坡环境（默认） |
| **US 环境** | `https://ego-portal.mlp.us.shopee.io` | 美国环境           |

所有 API 路径前缀：`/api/ego/portal`。本 skill 脚本通过环境变量 **`EGO_BASE_URL`** 指定 Base URL（不设则默认 SG）。

### 认证

- **方式**：Cookie `userID` = 访问令牌（Access Token）
- **Token 来源**：环境变量 **`USER_ID_OPENAPI`**（调用脚本前必设）

---

**状态码**：Job 接口 category=**14**，成功 `9914100`；日志文件列表返回 `code: 200`（int）；日志内容/摘要为纯文本。

## 目录

- [1. 获取作业列表](#1-获取作业列表)
- [2. 获取作业详情](#2-获取作业详情)
- [3. 获取作业任务列表](#3-获取作业任务列表)
- [4. 创建作业](#4-创建作业)
- [5. 获取日志文件列表](#5-获取日志文件列表)
- [6. 获取日志内容](#6-获取日志内容)
- [7. 获取日志摘要](#7-获取日志摘要)
- [通用：File / Resource / 错误响应](#通用file--resource--错误响应)

---

## 1. 获取作业列表

- **路径**: `GET /api/ego/portal/jobs`
- **说明**: 分页查询，支持 list_type、scope、order/orderBy 及多种筛选。version_id 为模型版本 ID（非 model_id）。
- **响应**: 成功：`code: "9914100"`，`data.data` 为作业列表，`data.info` 含 current、pageSize、total。Job 对象主要字段：job_id, job_name, status, creator, create_time, start_time, end_time, running_time, related_model_name, related_version_name, training_job_type, can_scale, can_stop, can_delete, can_dump, tags, cost_units。

---

## 2. 获取作业详情

- **路径**: `GET /api/ego/portal/job/{job_id}`
- **说明**: 含配置、资源、监控链接等。
- **响应**: 成功：`data` 含 job_id, job_name, status, config_files, code_file, flag_file, wc_resource, worker_resource, sample_server_resource, train_monitor_url, train_log_url, tenant_id, project_id, checkpoint_id 等。File 结构见 [通用](#通用file--resource--错误响应)；Resource 结构见 [通用](#通用file--resource--错误响应)。

---

## 3. 获取作业任务列表

- **路径**: `GET /api/ego/portal/job/{job_id}/tasks`
- **说明**: 任务列表；`verbose=true` 时返回 task_extra。
- **响应**: 成功：`data.job_tasks` 为任务数组；每项含 job_task_id, task_name, task_type, task_stauts, fail_reason, start_time, end_time, last_time, batch_job_link 等。

---

## 4. 创建作业

- **路径**: `POST /api/ego/portal/job`
- **说明**: Body 为 JSON；必填 job_name、training_job_type；config_files 必传（File 数组）；wc_resource、worker_resource 等为 Resource 对象。
- **必填**: job_name, training_job_type（见 [launch-train-job-params.md](launch-train-job-params.md) 枚举）, project_id, tenant_id, config_files（[]File）, job_priority（建议 7）。
- **常用**: related_model_id, related_version_id, zone, train_image, wc_resource, worker_resource, sample_server_resource, flag_file, data_converter, initialization_script, checkpoint_id。
- **training_job_type**（string）："21"=train, "22"=ego-lite, "23"=evaluation, "24"=feature evaluation, "25"=online evaluation, "26"=tensor evaluation；空或不传按 train。
- File 元素：uss_path、file_name 必填；Resource：replicas, cpu, memory；GPU 用 mig_gpu + gpuType（gpu 已废弃）。
- **响应**: 成功：`code: "9914100"`，`data.job_id` 为新作业 ID。

---

## 5. 获取日志文件列表

- **路径**: `GET /api/ego/portal/job/{job_id}/log_files`
- **说明**: 返回该作业下日志文件名列表；**code 为 int 200**（非 9914100）。

---

## 6. 获取日志内容

- **路径**: `GET /api/ego/portal/job/{job_id}/{log_file_name}`
- **说明**: 返回纯文本，最后约 1000 行（最多 10MB）。

---

## 7. 获取日志摘要

- **路径**: `GET /api/ego/portal/job/{job_id}/log_summary`
- **说明**: 仅**失败/失败归档**作业；返回纯文本摘要。

---

## 通用：File / Resource / 错误响应

### File 对象（config_files、code_file、flag_file 等）

| 字段名    | 类型   | 必填 | 说明                         |
| --------- | ------ | ---- | ---------------------------- |
| uss_path  | string | 是   | USS 路径                     |
| file_name | string | 是   | 文件名                       |
| type      | string | 否   | MIME/类型                    |
| md5       | string | 否   | 校验和                       |
| dump_url  | string | 否   | 下载地址（详情接口可能返回） |

### Resource 对象（wc_resource、worker_resource 等）

| 字段名   | 类型   | 说明                                        |
| -------- | ------ | ------------------------------------------- |
| replicas | int64  | 副本数                                      |
| cpu      | int64  | 核数                                        |
| memory   | int64  | 内存(GB)                                    |
| mig_gpu  | string | MIG 规格，如 "1"、"1g.5gb"；与 gpuType 同用 |
| gpuType  | string | 如 A100、V100；与 mig_gpu 同用              |
| gpu      | int64  | 已废弃，建议用 mig_gpu+gpuType              |

### Job 错误响应（category 14）

- 成功：`9914100`。失败：`9914`+ 错误码，如 9914101 未授权、9914102 禁止、9914103 未找到、9914107 错误请求、9914108 参数必填等。时间字段为毫秒时间戳。
