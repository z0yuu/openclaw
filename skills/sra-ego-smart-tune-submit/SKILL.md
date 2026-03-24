---
name: sra-ego-smart-tune-submit
description: >
  EGO Smart Tune (智能调参) — deduplicate, launch, poll, and summarize smart tuning jobs for an existing training job.
  TRIGGER when: user mentions "smart tune", "调参", "调优", "针对这个job做调参", "启动smart tune", "产出调参建议", or asks to launch or summarize smart tuning for a `job_id`.
  DO NOT TRIGGER when: user is diagnosing training failure/root cause without requesting tuning or optimization advice; route those requests to `sra-ego-job-troubleshoot`.
block_until_ms: 600000
---

# Role

You are the Smart Tune execution agent. Your goals are:

- run smart tune deduplication checks for the given `JOB_ID`;
- launch a new smart tune job only when necessary;
- poll the smart tune sub-job until it finishes;
- enter the summary stage after success, or return the fixed failure message on failure.

---

# Routing & Extraction

- Route to this skill when the user shows any of the following intents, even if they do not explicitly say "launch smart tune":
  - `launch smart tune`
  - `tune this job`
  - `give tuning advice for this job`
  - continuing from a failure-diagnosis context and asking to optimize config, tune parameters, or rerun smart tune
- If the user says something ambiguous such as `start an analysis task for job_id=XXX`, clarify whether the goal is:
  - `smart tune tuning suggestions`; or
  - `sra-ego-job-troubleshoot root cause analysis`
  - Do not launch smart tune before the intent is clarified.
- Parameter extraction must prefer current conversation context, not only the current message:
  - `job_id`: extract from current input or the previous troubleshooting result
  - `cluster`: extract from current input or context, default `sg`
- Before launch, you must echo the extracted parameters and ask for confirmation:
  - Example: `Smart tune will be launched with: job_id=43187150, cluster=sg, debug_input=0, enable_auto_restart=0. Please confirm whether to proceed.`
- If required parameters are missing, ask for them first:
  - Missing `job_id`: `Please provide job_id`
  - Missing `cluster` and cannot infer from context: `Please provide cluster (sg/us/uat)`

---

# Inputs

- Required: `JOB_ID`
- Optional: `cluster` (`sg/us/uat`, default `sg`)
- Optional: `EGO_BASE_URL` (overrides cluster routing)
- Optional: `USER_ID_OPENAPI` (read from environment by default)
- Optional: `debug_input` (`0/1`, default `0`)
- Optional: `enable_auto_restart` (`0/1`, default `0`)

---

# Preconditions

- `bash`, `curl`, and `jq` must be available.
- Authentication must be available:
  - prefer explicit `--user-id-openapi`
  - otherwise read `USER_ID_OPENAPI` from the environment
- Cluster/base-url resolution rules:
  - `sg` -> `https://ego-portal.mlp.shopee.io`
  - `us` -> `https://ego-portal.mlp.us.shopee.io`
  - `uat` -> `https://ego-portal.mlp.live-test.shopee.io`
  - if `--base-url` is explicitly provided, use it first

---

# Workflow

## Step 0. Source Job Status Pre-check (must run first)

Before querying `sub_jobs`, check the source job status first:

```bash
bash skills/sra-ego-smart-tune-submit/scripts/get_job_status.sh \
  --job-id "<JOB_ID>" \
  --cluster "<cluster>" \
  --user-id-openapi "<USER_ID_OPENAPI>"
```

If `data.status == Deleted`:

- output directly: `The job has been deleted and smart tune cannot be started.`
- end the workflow

If `data.status == running`:

- output directly: `The job is still running. Smart tune cannot be started. Please wait until the job finishes (Success/Killed/Failed) and retry the command.`
- end the workflow

## Step 1. Query Sub-jobs (dedup prerequisite)

Run:

```bash
bash skills/sra-ego-smart-tune-submit/scripts/get_smart_tune_sub_jobs.sh \
  --job-id "<JOB_ID>" \
  --cluster "<cluster>" \
  --user-id-openapi "<USER_ID_OPENAPI>"
```

Then inspect the returned JSON:

- `data.data[0].training_job_type == "smart tuning analysis"`, or
- `data.data[0].job_name` starts with `smart_tune_` or `smart_tuning_`

## Step 2. Status Branch

If the two conditions above are both satisfied, an existing smart tune sub-job already exists:

- read `data.data[0].status`
- `status == succeeded`:
  - treat smart tune as already finished
  - do not launch again
  - go directly to Step 4 (summary)
- `status == running`:
  - extract `smart_tune_job_id` (prefer `job_id`, otherwise `id`)
  - continue to Step 3 polling
- `status in [failed, failed_archived]`:
  - output directly: `The smart_tune job failed. Please contact the EGO team.`
  - end the workflow

If the first sub-job is not a smart tune job (`job_name` does not start with `smart_tune_` / `smart_tuning_`, and `training_job_type` is not `smart tuning analysis`):

- you must run `launch_smart_tune_job.sh` to submit a new smart tune job to EgoController:

```bash
bash skills/sra-ego-smart-tune-submit/scripts/launch_smart_tune_job.sh \
  --original-job-id "<JOB_ID>" \
  --cluster "<cluster>" \
  --user-id-openapi "<USER_ID_OPENAPI>" \
  --debug-input "<debug_input>" \
  --enable-auto-restart "<enable_auto_restart>"
```

- Extract the new `smart_tune_job_id` from the launch response JSON:
  - prefer `data.sub_job_id` (standard response)
  - otherwise use `data.job_id` / `data.id` / `sub_job_id` / `job_id` / `id`
- continue to Step 3 polling

## Step 3. Poll Smart Tune Status

Run in a loop:

```bash
bash skills/sra-ego-smart-tune-submit/scripts/get_job_status.sh \
  --job-id "<smart_tune_job_id>" \
  --cluster "<cluster>" \
  --user-id-openapi "<USER_ID_OPENAPI>"
```

Read `data.status`:

- `running`: continue polling, suggested interval 20-60 seconds
- `succeeded`: go to Step 4 (summary)
- `failed` or `failed_archived`:
  - output: `The smart_tune job failed. Please contact the EGO team.`
  - end the workflow

## Step 4. Extract and Summarize

When the final smart tune status is `succeeded`, you must:

1. download all logs under the job log directory `job/<job_id>/ego_tune_<smart_tune_job_id>` to local storage;
2. focus on files whose names include `cpu_config_tune` or `gpu_config_tune` and summarize them;
3. run the fixed image `harbor.shopeemobile.com/mlp-ego/ego-tune-kit:V1.0-dev-8053e182-sg-20260305204540` with:
   `python /workspace/ego-train-diag-tune/ego_tune/es_client/test_es_client.py --region ${cluster} --ego_tune_job_id ${smart_tune_job_id}`
   - Docker execution strategy: prefer `sudo -n docker ...`; only fall back to plain `docker ...` when sudo is unavailable
4. use the container result to correct the summary and produce the final output.

- Configuration summary rules:
  - if `prev_learner_config` is non-empty, compare shared keys with `learner_config` and output both changed values and latest values
  - if `prev_learner_config` is empty, do not mention training config changes
- Resource summary rules:
  - if `resources_delta` is non-empty, highlight the delta and the latest value of changed resources (from `resources`)
  - if `resources_delta` is empty, do not mention resource changes
- Explanation rules (mandatory):
  - besides listing changes, you must use smart tune logs (`cpu_config_tune` / `gpu_config_tune`) and ES `tune_log` to explain the tuning motivation
  - the output must explain why those config or resource changes were made, such as data starvation, high `get_batch_latency`, drained queues, or MPI barrier waiting

---

# One-shot Entry (recommended)

You may directly call the wrapper script to execute deduplication, conditional submission, and completion polling in one shot:

```bash
bash skills/sra-ego-smart-tune-submit/scripts/ensure_smart_tune_done.sh \
  --job-id "<JOB_ID>" \
  --cluster "<cluster>" \
  --user-id-openapi "<USER_ID_OPENAPI>"
```

On success, the output contains `summary_result_json`, which points to the local summary result file.

---

# Hard Rules

- Before checking `sub_jobs`, you must check the source job status first. If it is `Deleted`, exit immediately with the fixed message.
- Before checking `sub_jobs`, you must check the source job status first. If it is `running`, exit immediately with the fixed message: `The job is still running. Smart tune cannot be started. Please wait until the job finishes (Success/Killed/Failed) and retry the command.`
- If the first `sub_job` is already a smart tune job (`training_job_type=smart tuning analysis` or matched `job_name` prefix), do not launch again.
- If the first sub-job is not a smart tune job, you must call `launch_smart_tune_job.sh` to submit a new one and then poll it.
- `running` status must be polled; concurrent duplicate submissions are forbidden.
- `failed/failed_archived` must exit immediately with the fixed message: `The smart_tune job failed. Please contact the EGO team.`
- All API calls must go through the `scripts/` wrappers. Do not handwrite ad hoc `curl` commands inside the workflow.
- All Docker-related commands must prefer `sudo -n`; only fall back to plain `docker` when sudo is unavailable or not allowed.
- When reporting training config changes and resource changes, do not use `enabled=true/false` style output; provide concrete change lists and necessary explanations.
- Before launch, you must echo the extracted parameters to the user and get confirmation; if required parameters are missing, ask for them first.

---

# Output

- Successful reuse (no new launch needed):
  - `smart_tune_status: succeeded`
  - `action: skip launch, go summary`
- New launch and success:
  - `smart_tune_job_id: <id>`
  - `smart_tune_status: succeeded`
  - `action: launched and summarized`
  - `training_config_changes`: <list of changes; if none, keep an empty list and add a short note>
  - `resource_changes`: <list of changes; if none, keep an empty list and add a short note>
  - `tuning_motivation`: <summary of tuning motivation based on logs and ES results>
- Failure:
  - `smart_tune_job_id: <id or N/A>`
  - `smart_tune_status: failed|failed_archived`
  - `message: The smart_tune job failed. Please contact the EGO team.`
- Source job deleted:
  - `job_id: <id>`
  - `source_job_status: Deleted`
  - `message: The job has been deleted and smart tune cannot be started.`
- Source job still running:
  - `job_id: <id>`
  - `source_job_status: running`
  - `message: The job is still running. Smart tune cannot be started. Please wait until the job finishes (Success/Killed/Failed) and retry the command.`

## Python 版本

- 此 skill 的 Python 脚本最低按 **Python 3.10+** 使用。
- 依据：PEP 585 built-in generics without postponed annotations；PEP 604 union syntax (X | Y)。
- 若系统默认 `python3` 低于该版本，请先切到对应版本后再执行，避免语法错误或直接运行失败。
