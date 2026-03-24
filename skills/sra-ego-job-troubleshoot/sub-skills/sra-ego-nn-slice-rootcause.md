---
name: sra-ego-nn-slice-rootcause
description: >
  EGO NN slice diagnosis (EGO NN 切片诊断) — trace `NN_SLICE_VALUE` failures through checkpoint loading, `filter_nn`, and SS/worker batchfea flow.
  TRIGGER when: logs mention `NN_SLICE_VALUE`, `Check failed: char_buffer.size()`, batchfea delivery failure, or the user asks to diagnose missing NN slice values in EGO jobs.
  DO NOT TRIGGER when: the failure is unrelated to NN slice retrieval, such as generic worker crashes, compile issues, or checkpoint problems without `NN_SLICE_VALUE` signals.
---

# Role

This case diagnoses the following direct errors:

- `Check failed: char_buffer.size(). NN_SLICE_VALUE_*`

The goal is to refine the direct failure into an actionable root cause:

1. whether an `evaluation` / `online-evaluation` / `release` job failed to load a checkpoint
2. whether a checkpoint was loaded but `filter_nn=true` filtered out nn parameters
3. whether SS produced batchfea and whether the worker successfully received it

---

# Trigger

Trigger this case when any of the following is true:

- `01_error_log.json` or `02_error_info.json` contains `NN_SLICE_VALUE`
- the failed-instance log contains `Check failed: char_buffer.size(). NN_SLICE_VALUE`

---

# Inputs

- `job_id`
- `TMP_DIR`
- `01_error_log.json`
- `02_error_info.json`
- worker and SS logs for the failed instance, preferably raw logs

---

# Preconditions

- `USER_ID_OPENAPI` must be available
- `curl` and `jq` must be executable
- Default base URL: `https://ego-portal.mlp.shopee.io`

---

# Workflow

1. Job metadata inspection (must run first)

Run:

```bash
curl -X GET "https://ego-portal.mlp.shopee.io/api/ego/portal/job/${JOB_ID}" \
  -H "Content-Type: application/json" \
  -H "Cookie: userID=${USER_ID_OPENAPI}" | jq .
```

2. Extract the following fields from the response, supporting both field layouts:

- `job_type`: prefer `training_job_type`, otherwise `data.training_job_type`
- `checkpoint_id`: prefer `checkpoint_id`, otherwise `data.feature_management.checkpoint_id`
- `filter_nn`: prefer `filter_nn`, otherwise `data.feature_management.filter_nn`

3. Evaluate `job_type`:

- If `job_type == train`, skip checkpoint inspection and go directly to the batchfea chain.
- If `job_type` is `evaluation`, `online-evaluation`, or `release`, continue with checkpoint checks:
  - if `checkpoint_id` is empty, the root cause is "checkpoint not loaded"
  - if `checkpoint_id` is non-empty and `filter_nn == true`, the root cause is "nn parameters were filtered during checkpoint loading, so `NN_SLICE_VALUE` cannot be found"

4. If none of the above match, inspect the batchfea chain:

- scan SS logs for batchfea production signals
- scan worker logs for successful `RemoteIO get batchfea`
- if those success signals are missing, the root cause becomes one of:
  - `SS filtered out all data during the runtime converter stage`
  - `the raw data path is empty or contains no usable data`

5. If all checks above still cannot locate the cause:

- output `联系EGO同学解决`

---

# Hard Rules

- Always inspect job metadata before checking the log chain.
- Do not stop at the direct `NN_SLICE_VALUE` error. You must produce a deeper root-cause branch.
- When `job_type == train`, do not output any "checkpoint not loaded" conclusion. You must inspect the batchfea chain instead.
- If the `checkpoint_id` / `filter_nn` branch already matches, do not downgrade the root cause to a generic "platform issue".
- `联系EGO同学解决` is allowed only as the final fallback when all prior checks fail.

---

# Output Contract

- `case_type`: `nn_slice_value_rootcause`
- `direct_error`: `Check failed: char_buffer.size(). NN_SLICE_VALUE_*`
- `job_type`: `<training_job_type>`
- `checkpoint_id`: `<value or empty>`
- `filter_nn`: `<true|false|empty>`
- `root_cause`: `<matched root-cause branch>`
- `repair_measures`:
  - if checkpoint not loaded: `在 evaluation/online-evaluation/release 任务中正确配置并加载 checkpoint 后重跑（train 类型不适用）`
  - if `filter_nn=true`: `将 checkpoint 加载参数中的 filter_nn 调整为 false（或按需保留 nn 参数）后重跑`
  - if the batchfea chain is broken: `修复 converter 过滤条件或数据路径可用性，确保 SS 产出且 worker 可获取 batchfea 后重跑`
  - final fallback: `联系EGO同学解决`
- `artifacts`:
  - `<TMP_DIR/01_error_log.json>`
  - `<TMP_DIR/02_error_info.json>`
  - `<TMP_DIR/*worker*log*>`
  - `<TMP_DIR/*ss*log*>`
