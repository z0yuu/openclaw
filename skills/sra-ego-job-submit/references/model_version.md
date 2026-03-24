# 模型版本 API

模型版本（Model Version）相关接口：列表、详情、创建、更新。环境与认证：环境变量 **USER_ID_OPENAPI**（必填）；**EGO_BASE_URL**（可选）。

**状态码**：category=**13**，成功 `9913100`；失败为 `9913`+ 错误码。

## 目录

- [1. 获取版本列表](#1-获取版本列表)
- [2. 获取版本详情](#2-获取版本详情)
- [3. 创建版本](#3-创建版本)
- [4. 更新版本](#4-更新版本)

---

## 1. 获取版本列表

- **路径**: `GET /api/ego/portal/model/{model_id}/versions`
- **说明**: 分页查询指定模型下的版本，支持 version_id、version_name、create_time_start/end、creator、orderBy/order。
- **响应**: 成功：`data.data` 为版本列表，`data.info` 分页。每项含 version_id, model_id, version_name, version_type(normal/baseline), entry_file_name, creator, create_time, code_file, use_git_config 等。

---

## 2. 获取版本详情

- **路径**: `GET /api/ego/portal/model/{model_id}/version/{version_id}`
- **响应**: 成功：data 含 version_id, model_id, version_name, version_type, entry_file_name, description, use_git_config, git_config, code_file, creator, create_time 等。

---

## 3. 创建版本

- **路径**: `POST /api/ego/portal/model/{model_id}/version`
- **说明**: 创建新版本；可先通过 upload_file 上传后，将返回的 uss_path 填入 code_file。请求体必填：version_name, entry_file_name, code_file ([]File，每项 uss_path、file_name)。

---

## 4. 更新版本

- **路径**: `PUT /api/ego/portal/model/{model_id}/version/{version_id}`
- **说明**: 仅传需更新字段；可更新 description、version_type、use_git_config、code_file 等。
