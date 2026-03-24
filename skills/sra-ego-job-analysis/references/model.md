# 模型 API

模型（Model）相关接口：列表、详情、创建。环境与认证：环境变量 **USER_ID_OPENAPI**（必填）；**EGO_BASE_URL**（可选）。

**状态码**：category=**12**，成功 `9912100`；失败为 `9912`+ 错误码。

## 1. 获取模型列表

- **路径**: `GET /api/ego/portal/models`
- **说明**: 分页查询，支持 scope、orderBy/order、model_id、model_name、project、create_time_start/end、creator。scope：1-全部(有权限项目下) 2-个人。
- **响应**: 成功：`data.data` 为模型列表，`data.info` 含 current、pageSize、total。Model 对象：model_id, model_name, description, tenant_id, project_id, creator, is_private, auth_users, create_time, can_edit, can_delete, can_move。

## 2. 获取模型详情

- **路径**: `GET /api/ego/portal/model/{model_id}`
- **响应**: 成功：`data.model_info` 含 model_id, model_name, description, tenant_name, tenant_id, project_name, project_id, creator, create_time（秒级时间戳）。

## 3. 创建模型

- **路径**: `POST /api/ego/portal/model`
- **说明**: 在指定租户、项目下创建模型；model_name 全局唯一。请求体：model_name, tenant_id, project_id（必填）；description, is_private(0/1), auth_users（可选）。
