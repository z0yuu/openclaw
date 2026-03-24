# Checkpoint API

Checkpoint 列表接口。环境与认证：环境变量 **USER_ID_OPENAPI**（必填）；**EGO_BASE_URL**（可选）。

**状态码**：category=**16**，成功 `9916100`；失败为 `9916`+ 错误码。

---

## 1. 获取 Checkpoint 列表

- **路径**: `GET /api/ego/portal/model/{model_id}/version/{version_id}/checkpoints`
- **说明**: 分页查询指定模型版本下的 Checkpoint，支持 job_id、checkpoint_id、checkpoint_name、only_mine、verbose（返回 checkpoint_path、related_job_s3_path）。
- **响应**: 成功：`data.data` 为 Checkpoint 列表，`data.info` 含 current、pageSize、total。每项含 checkpoint_id, checkpoint_name, checkpoint_path(verbose 时), related_job_id, related_job_name, related_job_s3_path(verbose 时), feature_num, mf_feature_num, size, checkpoint_type, create_time 等。

**说明**：仅返回状态为 succeeded/cleared 的 Checkpoint；时间字段为毫秒时间戳。
