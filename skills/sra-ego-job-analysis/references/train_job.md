# 训练作业与日志 API（本 skill 仅用 list / get）

作业（Job）列表与详情接口。

---

## 环境与认证

### 环境

| 环境        | 域名                                  | 说明               |
| ----------- | ------------------------------------- | ------------------ |
| **SG 环境** | `https://ego-portal.mlp.shopee.io`    | 新加坡环境（默认） |
| **US 环境** | `https://ego-portal.mlp.us.shopee.io` | 美国环境           |

所有 API 路径前缀：`/api/ego/portal`。脚本通过环境变量 **`EGO_BASE_URL`** 指定 Base URL（不设则默认 SG）。

### 认证

- **方式**：Cookie `userID` = 访问令牌
- **Token 来源**：环境变量 **`USER_ID_OPENAPI`**（调用脚本前必设）

---

**状态码**：Job 接口 category=**14**，成功 `9914100`。

## 1. 获取作业列表

- **路径**: `GET /api/ego/portal/jobs`
- **说明**: 分页查询，支持 job_name、list_type、scope、order/orderBy 等。
- **响应**: 成功：`code: "9914100"`，`data.data` 为作业列表，`data.info` 含 current、pageSize、total。Job 对象主要字段：job_id, job_name, status, creator, create_time, related_model_name, related_version_name, train_auc_url 等。

## 2. 获取作业详情

- **路径**: `GET /api/ego/portal/job/{job_id}`
- **说明**: 含 related*model*_、related*version*_、train_auc_url 等。
- **响应**: 成功：`data` 含 job_id, job_name, status, related_model_id, related_model_name, related_version_id, related_version_name, train_auc_url, train_monitor_url, train_log_url 等。
