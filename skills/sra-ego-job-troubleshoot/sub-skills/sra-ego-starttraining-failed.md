---
name: sra-ego-starttraining-failed
description: >
  EGO online export start diagnosis (EGO 在线导出启动诊断) — analyze `HttpStartTraining` connection-refused failures with EgoController retry logic and WC/SS/Worker readiness evidence.
  TRIGGER when: the failed task is `online export start` and logs mention `HttpStartTraining`, `connection refused`, retry timeout, or delayed readiness across WC, SS, or Worker.
  DO NOT TRIGGER when: the failure is a general network issue, export script issue only, or an online export case without StartTraining connection-refused symptoms.
---

# Role

This case handles online export start failures where `HttpStartTraining` returns `connection refused`.

---

# Trigger

Trigger this case only when all of the following are true:

- the failed task is `online export start`
- `fail_reason` or extracted evidence contains both `HttpStartTraining` and `connection refused`
- once matched, this case should run directly and should not compete with other bad cases

---

# Inputs

- `job_id`
- `TMP_DIR`
- `get_job_tasks` result
- `01_error_log.json` / `02_error_info.json`

---

# Preconditions

- `USER_ID_OPENAPI` must be available
- Required executables:
  - `scripts/get_job_log_files.py`
  - `scripts/extract_error_log.py`
  - `scripts/extract_error_info.py`
  - `scripts/diagnose_soc_job.py`

---

# Workflow

1. Read the failed task and `fail_reason` from `get_job_tasks` and confirm the trigger.
2. Add SOC status evidence:

```bash
PYTHONIOENCODING=utf-8 python scripts/diagnose_soc_job.py <soc_project_id> <soc_job_id>
```

3. Fetch `online-export` logs for `worker/ss/wc`, then run the two-stage extraction for each role with the matching `--role`. Write artifacts to:

- `05_worker_error_log.json` / `05_worker_error_info.json`
- `06_ss_error_log.json` / `06_ss_error_info.json`
- `07_wc_error_log.json` / `07_wc_error_info.json`

4. Filter optional-log noise:

- If logs contain `s3cmd get export_initialize.sh` 404 or `NoSuchKey`, treat it as a missing optional initialization script. It is not an error, not a root cause, and must not enter repair suggestions.

5. Root-cause priority classification (required):

- If the `online export start` `fail_reason` already contains `connection refused`, especially with `HttpStartTraining`, classify the primary root cause as `StartTraining retry-timeout / readiness timing`.
- Under that condition, ignore `export_initialize.sh 404` unless the user explicitly asks to investigate that script.

6. Readiness-chain inspection (core):

- You must check whether worker, SS, and WC all reached the EGO C++ ready stage.
- Preferred ready evidence examples:
  - WC: `CoordinatorHttpServiceImpl` started / `Server ... serving on port=9002`
  - Worker/SS: `First Register success` / `RegisterNode status: ONLINE`
- If `Register failed ... connection refused` still appears within the StartTraining retry window and ready evidence is delayed or missing, conclude it is a readiness-timing issue.

7. Output a chain-based root cause:

- Generate the chain dynamically from evidence, for example:
  - `worker not ready -> WC StartTraining timeout -> EgoController retry limit exceeded`
  - `ss not ready -> WC dependency wait timeout -> StartTraining retry limit exceeded`
  - `wc not ready (port 9002 not ready) -> StartTraining connection refused -> retry limit exceeded`

---

# Hard Rules

- Do not classify this scenario as a generic network problem.
- The explanation must include the EGO service chain: `EgoController -> WC StartTraining -> readiness dependencies`.
- `repair_measures` may contain only user-executable actions:
  - user-side actions: model-code changes, training-config changes, or resource adjustments
  - platform-side action must be written explicitly as `请联系EGO同学`
- Do not output internal checks the user cannot perform, such as WC 9002 reachability or internal timeline alignment.
- `s3cmd get export_initialize.sh` 404 / `NoSuchKey` must stay treated as an optional missing script, not an error.
- This case must explicitly provide either ready evidence or missing-ready evidence for worker/ss/wc. Do not quote only `fail_reason`.
- If `fail_reason` already contains `connection refused`, neither `root_cause` nor `repair_measures` may include conclusions based on `export_initialize.sh 404`.

---

# Output Contract

- `case_type`: `httpstarttraining_retry_timeout`
- `root_cause`: `<dynamically generated from ready_evidence; do not hardcode one fixed not-ready role>`
- `ready_evidence`:
  - `wc_ready`: `<9002 service ready evidence or missing evidence>`
  - `worker_ready`: `<worker registration / online evidence or missing evidence>`
  - `ss_ready`: `<ss registration / online evidence or missing evidence>`
  - `optional_script_404_ignored`: `<whether export_initialize.sh 404 was matched and ignored>`
- `repair_measures`:
  - `请联系EGO同学，并附上 job_id 与错误证据（HttpStartTraining connection refused / 重试超限），由平台侧评估调整重试参数`
  - `若模型编译时间异常长，用户可先优化模型代码或配置以缩短编译时长后再重跑`
- `artifacts`:
  - `<TMP_DIR/05_worker_error_info.json>`
  - `<TMP_DIR/06_ss_error_info.json>`
  - `<TMP_DIR/07_wc_error_info.json>`
