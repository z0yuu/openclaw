---
name: sra-ego-oom-tune-handoff
description: >
  EGO OOM handoff diagnosis (EGO OOM 接力诊断) — identify pod-memory or worker-GPU OOM failures and route the user to Smart Tune with an explicit next command.
  TRIGGER when: logs mention `OOMKilled`, `exitcode: 137`, `CUDA out of memory`, `CUDNN_STATUS_ALLOC_FAILED`, `CUBLAS_STATUS_ALLOC_FAILED`, or other clear memory-exhaustion signals in EGO jobs.
  DO NOT TRIGGER when: the issue is low utilization without OOM evidence, generic performance tuning, or failures unrelated to memory exhaustion.
---

# Role

This sub-skill handles OOM-related bad cases:

- Worker, WC, or SampleServer pod-memory OOM
- Worker GPU-memory OOM during training

The goal is not to give generic tuning advice, but to route the user to `sra-ego-smart-tune-submit` for concrete next-step configuration changes.

---

# Trigger

Trigger this case when any of the following is true:

- `get_job_tasks.fail_reason` or logs contain:
  - `OOMKilled`
  - `exitcode: 137`
  - `Killed ... sample_server` / `Killed process`
  - `OutOfMemory` / `cannot allocate memory`
- Worker logs contain GPU-memory OOM keywords:
  - `CUDA out of memory`
  - `CUDNN_STATUS_ALLOC_FAILED`
  - `CUBLAS_STATUS_ALLOC_FAILED`
  - `ResourceExhaustedError` + `OOM`/`out of memory`
  - `failed to allocate memory on device`

---

# Inputs

- `job_id`
- `TMP_DIR`
- `get_job_tasks` result
- `01_error_log.json`
- `02_error_info.json`

---

# Preconditions

- `get_job_tasks`, `01_error_log.json`, and `02_error_info.json` must already exist.
- The main flow must have completed the failed-pod first-pass extraction before entering this sub-skill.
- If OOM evidence is absent from both task metadata and `01/02`, stop and return control to the main skill instead of forcing an OOM conclusion.

---

# Workflow

1. Primary branch: classify with metadata plus extracted logs

- Use both `fail_reason` and `01/02` evidence to classify the OOM type:
- `pod_memory_oom` (Worker/WC/SS)
- `worker_gpu_memory_oom` (worker GPU memory)
- In `root_cause`, explicitly state:
- which role or instance OOMed, for example `ss-17`
- whether the OOM type is memory or GPU memory
- at least one key evidence line

2. Fallback branch: metadata is vague but logs still show OOM

- If `fail_reason` is vague or empty, re-classify from `01_error_log.json` and `02_error_info.json` alone.
- If multiple roles show OOM, report the earliest directly failed role and mention the ambiguity in `limitations`.

3. Last-resort branch: evidence incomplete

- If the current evidence is insufficient to isolate the exact role but OOM is still clear, keep the root cause at the OOM category level and hand off to Smart Tune anyway.
- If OOM evidence is not clear after checking both metadata and `01/02`, exit this sub-skill and let the main skill continue with another route.

4. `repair_measures` must hand off to Smart Tune. Do not output generic advice such as "increase memory" or "reduce batch size".

---

# Hard Rules

- Do not output vague resource guidance such as "increase memory appropriately".
- You must provide the fixed next-step command containing the current `job_id`:
  - `针对job_id=<job_id>，启动smart tune任务`
- If the user asks "how much resource should be added", still guide them to Smart Tune first so it can produce the concrete configuration.
- Do not output suggestions that only platform engineers can execute.

---

# Output Contract

- `case_type`: `oom_smart_tune_handoff`
- `oom_type`: `pod_memory_oom | worker_gpu_memory_oom`
- `root_cause`: `<instance-level OOM cause plus evidence>`
- `repair_measures`:
  - `请继续输入：针对job_id=<job_id>，启动smart tune任务`
  - `若 smart tune 任务失败，输出：smart_tune任务失败，请联系EGO同学`
- `artifacts`:
  - `<TMP_DIR/01_error_log.json>`
  - `<TMP_DIR/02_error_info.json>`
