# 工具与配置 API

门户工具与配置接口：上传文件、门户配置、训练框架版本、项目配额。环境与认证：环境变量 **USER_ID_OPENAPI**（必填）；**EGO_BASE_URL**（可选，默认 https://ego-portal.mlp.shopee.io）。

**状态码**：category=**11**，成功 `9911100`；失败为 `9911`+ 错误码。

## 目录

- [1. 上传文件](#1-上传文件)
- [2. 获取门户配置](#2-获取门户配置)
- [3. 获取训练框架版本列表](#3-获取训练框架版本列表)
- [4. 获取项目配额](#4-获取项目配额)

---

## 1. 上传文件

- **路径**: `POST /api/ego/portal/upload_file`
- **说明**: multipart/form-data，字段名 file1、file2、…；上传到 USS 临时桶，返回每文件 uss_path。单文件最大 **32MB**，空文件拒绝。
- **响应**: 成功：`data.results` 数组，每项含 file_name、uss_path、upload_success、err_msg；`data.bucket_name` 为临时桶名。

---

## 2. 获取门户配置

- **路径**: `GET /api/ego/portal/config`
- **说明**: 返回租户/项目、用户信息、枚举（作业状态/类型、菜单等）、gpu_packages、环境与存储等。可选 Query：tenantType（如 `predictor` 仅返回 predictor 相关租户/项目）。
- **响应**: 成功：data 含 tenants（含 projects）、user_info、job_status_enums、offline_training_job_type、tenants、bucket、host、gpu_packages、menu、checkpoint_type_enums 等。tenant 含 tenant_id、tenant_name、projects；project 含 project_id、project_name。

---

## 3. 获取训练框架版本列表

- **路径**: `GET /api/ego/portal/framework_versions`
- **响应**: 成功：`data.framework_versions` 数组，每项 id、name、image。

---

## 4. 获取项目配额

- **路径**: `GET /api/ego/portal/project_quota/{project_id}`
- **说明**: 按项目 ID 查询 SOC 资源配额，按可用区返回 CPU、内存、GPU（Native/MIG）的 quota、remain、request。
- **响应**: 成功：`data.project_quota` 为按 zone 的数组，每项含 zone、cpu、memory、gpu（按型号如 A100 的 native、mig）。子结构含 unit、quota、remain、request。
