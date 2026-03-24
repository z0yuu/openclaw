---
name: sra-ego-model-local-run
description: >
  Run an EGO training job locally in Docker with explicit inputs, temporary job assembly, and log verification.
  TRIGGER when: the user asks to run local EGO training, rerun local training in Docker, or start training from local artifacts or a source job id.
  DO NOT TRIGGER when: the task is local compile only, full compile-plus-run orchestration, or general Docker troubleshooting unrelated to EGO local run.
block_until_ms: 600000
---

# Job Local Run

## Skill Scope

This skill handles real local run execution for EGO training jobs in Docker, including rerun with updated inputs.

## Routing Boundary

- If user intent is real local run execution, route to this skill.

## Entry Gate

- `USER_ID_OPENAPI` is mandatory only in portal source mode.
- In local explicit mode, do not require `USER_ID_OPENAPI`.
- In portal mode, resolve `USER_ID_OPENAPI` from current environment first; do not ask user to re-enter it if env already has it.

## Boundary

This skill defines run input contract and execution flow. Task routing decisions should be made by `skill-index.md`.

## Trigger

Use this skill when user asks to:

- run local EGO training
- execute local run in Docker
- rerun local training after modifying model/converter/config files
- run training from natural language input (e.g. source_job_id/image/converter/learner path)

## Interaction Policy

When user says they want to run local training:

1. Pause before execution.
2. Extract as many inputs as possible from user natural language first.
3. Explicitly collect only missing required inputs.
4. Execute only after all required inputs are provided.
5. Do not perform trial runs, dry-run validation, or "test execution" without explicit user approval.
6. Do not infer or substitute required fields from examples/defaults/repo files when unresolved after extraction.

Strict guardrails:

- Missing any required input => stop and ask user to provide it.
- Prefer extraction from user text first; only unresolved required fields should trigger follow-up questions.
- Do not "helpfully" pick example values to verify environment.
- If user asks to execute, first echo collected inputs and wait until all required fields are explicitly provided by user.
- All Docker operations must run with `sudo` by default.
- If `sudo` is unavailable or denied, stop immediately and return explicit environment error; do not silently downgrade.
- `log_dir` is optional; if user does not provide it, agent must generate a temp directory under the system temp area.
- Agent-generated `log_dir` must be shown to user at the end of task, and cleaned up when session ends.
- If first run attempt fails, ask user to provide explicit full input checklist for selected mode and rerun with confirmed values.

## Step 1: Collect Required Inputs

### 1.0 Natural language extraction first (mandatory)

Before asking user for missing fields, extract from request text:

- if text contains `source_job_id=<id>` or obvious job id for portal run, map to `source_job_id`
- if text contains `converter` directory/path, map to `converter_dir`
- if text contains `ego-learner.yaml` path, map to `learner_config`
- if text contains image reference (`harbor...`, `repo:tag`), map to `runtime_image`
- if text contains `run_config.yaml` path, map to `run_config`

Mode selection from extracted info:

- portal-candidate: has `source_job_id`
- local-candidate: has `converter_dir` and/or `learner_config`
- if both candidates exist and conflict, ask user to choose mode first
- if one candidate is clear, continue in that mode and only ask for missing required fields

Common required inputs (both modes):

- `model_dir` (renamed from old `job_dir`)
- `runtime_image`
- `log_dir` (optional; default is an agent-generated temp dir under the system temp area)

Then choose **one** source mode:

### Mode A: Local explicit inputs

Required:

- `converter_dir` (contains converter files such as `.py` or `.lua`)
- `learner_config` (path to `ego-learner.yaml`)

Optional:

- `run_config` (path to `run_config.yaml`; if omitted, use skill default config)

### Mode B: EgoController job source

Required:

- `source_job_id` (EgoController JOB_ID)
- `cluster` (`sg` or `us` or `uat`)
- `USER_ID_OPENAPI` (from current environment by default; user may override explicitly)

Behavior:

- Resolve `converter_dir` and `learner_config` from portal by:

```bash
bash scripts/get_run_files_by_job_id.sh \
  --cluster "<cluster>" \
  --job-id "<source_job_id>" \
  --user-id-openapi "<USER_ID_OPENAPI>" \
  --output-ego-learner-path "<portal_output_dir>/ego-learner.yaml" \
  --output-converter-dir "<portal_output_dir>/converter_dir"
```

- `run_config` in Mode B is only from user explicit input (optional). If missing, use default run config.
- Resolve `USER_ID_OPENAPI` with priority:
  1. user explicit override in current turn
  2. current environment variable `USER_ID_OPENAPI`
  3. if still missing, stop and ask user to set env variable

After one run, support `rerun` in the same conversation:

- reuse the latest collected inputs
- do not ask user to repeat inputs unless they want to change them
- if previous run used an agent-generated `log_dir`, generate a new temp `log_dir` for each rerun unless user explicitly sets one
- before every run attempt (including `rerun`), always re-apply Step 2.5 backend compatibility fix to the currently resolved `learner_config`
- if user provides a new `source_job_id` or a new `learner_config` path, treat it as new inputs but still apply the same Step 2.5 fix before launching

## Step 2: Validate Inputs

### 2.0 `log_dir` default and lifecycle

- If user provides `log_dir`, use it as-is.
- If user omits `log_dir`, generate:
  - `<system-temp>/model-local-run-logs/<timestamp>-<rand>`
- Agent must print resolved `log_dir` before run starts.
- At task end (success/failure), always show `log_dir` and a clickable `log_dir_link` for inspection.
- For agent-generated `log_dir`, cleanup is required when session ends.

### 2.1 Required files in `model_dir`

`model_dir` must contain:

- `ego-config.json`
- `ego-config.pb`

Optional model artifacts:

- `graph.pb`
- `graph.readable`

If any required file is missing, stop and report missing files.

### 2.2 `converter_dir` and `learner_config`

- `converter_dir` must exist as a directory and contain at least one `.py` or `.lua` file
- `learner_config` must exist as a file (`ego-learner.yaml`)

If either is missing, stop and report missing inputs.

### 2.3 Fixed `flags.txt` rule

Always overwrite temporary `job_dir/flags.txt` with:

- `scripts/flags.txt`

This applies whether input source already contains flags or not.

Path resolution rule:

- Do not depend on repository absolute paths (for example `.../ego-agent-alpha/ego-agent-try/...`).
- Resolve script/config paths relative to the installed skill root in current environment (`codex` / `cursor`), so packaged installations work directly.

### 2.4 Runtime image is mandatory

If `runtime_image` is missing, stop immediately.

Parse from image tag:

- `zone`: `sg` or `us`
- `tf_version`: `tf1` or `tf2`

### 2.5 Backend compatibility auto-fix (`xla` -> `tensorflow`)

Goal:

- avoid rerun failure caused by XLA requiring GPU-only device setup

Trigger condition (from previous failed run logs):

- error contains:
  - `Check failed: effective_devices.size() == 1 && effective_devices.contains(common::kDeviceTypeGPU) only gpu is supported by ego_xla`

Required behavior:

1. If trigger condition is matched, automatically patch the resolved `learner_config` file before next launch:
   - from: `train_config.backend_type: xla`
   - to: `train_config.backend_type: tensorflow`
2. This patch must happen before starting `host_launch_local_job.sh`.
3. For `rerun`, use the patched `learner_config` as the effective config.
4. Even if user changes inputs on rerun (for example new `source_job_id` or explicit new `learner_config`), still check and apply the same patch when trigger condition is matched.
5. If `train_config.backend_type` is already `tensorflow`, keep it unchanged and continue.
6. If field is missing or file cannot be patched, stop and report explicit error instead of silently continuing.

## Step 3: Prepare Run Config

`run_config` priority:

1. user explicit `run_config` input
2. fallback: `scripts/run_config.yaml`

Expected keys:

- `max_runtime_seconds`
- `resources.memory`
- `resources.cpu`
- `resources.gpu`

Step 3 runner command:

```bash
sh scripts/host_launch_local_job.sh \
  --model-dir "<model_dir>" \
  --runtime-image "<runtime_image>" \
  --log-dir "<resolved_log_dir>" \
  [--converter-dir "<converter_dir>"] \
  [--learner-config "<learner_config>"] \
  [--run-config "<run_config>"] \
  [--source-job-id "<source_job_id>" --cluster "<cluster>" --user-id-openapi "<USER_ID_OPENAPI>"]
```

Mode A uses explicit `converter_dir` + `learner_config`.
Mode B uses `source_job_id + cluster + USER_ID_OPENAPI`.

## Step 4: Run in Docker

Step 4 is executed inside `scripts/host_launch_local_job.sh`:

1. Assemble temporary `job_dir` directory and mount it to `/workspace/data`:

- copy `model_dir` required files (`ego-config.json`, `ego-config.pb`) and optional graph files
- copy the Step 2.5 processed `learner_config` to `/workspace/data/ego-learner.yaml`
- copy all files under `converter_dir` into temporary `job_dir`
- if user provided `run_config`, copy it as `/workspace/data/run_config.yaml`
- inject fixed `flags.txt`
- copy `container_run_local_job.sh`

2. Validate temporary `job_dir` contains required runtime files before `docker run`:

- `ego-config.json`
- `ego-config.pb`
- `ego-learner.yaml`
- `flags.txt`
- `container_run_local_job.sh`

3. Precheck Docker privilege before run:

- recommended check command: `sudo -n docker ps >/dev/null 2>&1`
- if precheck fails, stop and return clear error (for example: `sudo_not_available` / `sudo_permission_denied` / `docker_requires_privilege`)

4. Start container with `runtime_image` via `sudo docker run`.
5. Apply resource limits from selected `run_config.yaml`:

- memory
- cpu
- gpu

6. Run command:

```bash
sh /workspace/data/container_run_local_job.sh <log_dir> <max_runtime_timeout_seconds>
```

During waiting period, `host_launch_local_job.sh` monitors Docker resource usage
(CPU%, memory usage, memory%) every `5s`.

## Step 5: Success/Failure Criteria

`scripts/container_run_local_job.sh` confirms training start by matching in `coordinator.log`:

- `StartTraining success, TrainingBeginTime ...`

Result rules:

- exit `0`: started successfully
- exit non-zero / timeout: failed
- `max_runtime_seconds` is enforced inside `container_run_local_job.sh` as `max_runtime_timeout`
- when timeout is reached, container script kills `coordinator` / `sample_server` / `worker`, prints `TimeOut`, and exits with code `124`
- at process end, print Docker resource summary (peak CPU%, peak memory%, last memory usage, PIDs, OOMKilled, container exit metadata)
- Docker resource sampling must support fallback by container name when cidfile is unavailable, so summary is not silently empty
- if `stats_samples=0`, explicitly return a diagnostic note (for example: container exited before first sample) instead of only showing `N/A`
- Docker resource summary must include `monitor_interval_seconds=5`
- if timeout happened, `host_launch_local_job.sh` should include `run_termination_reason=TimeOut(max_runtime_timeout)` while still printing Docker resource summary
- if `docker_exit_code=137` and `oom_killed=true`, treat as likely memory pressure/OOM

Always return:

- run status
- used `model_dir`, `runtime_image`, `resolved_log_dir`
- resolved `converter_dir`, `learner_config`, `run_config`
- path to logs (`coordinator.log`, `worker.log`, `sample_server.log`)
- `log_dir_link` (clickable path for user inspection)
- docker resource summary for diagnosis
- when resource stats are unavailable, include explicit `stats_collection_note` field in output

## References

- Launcher: `scripts/host_launch_local_job.sh`
- Portal resolver: `scripts/get_run_files_by_job_id.sh`
- Container script: `scripts/container_run_local_job.sh`
- Fixed flags: `scripts/flags.txt`
- Default config: `scripts/run_config.yaml`
- Example files: `example/launch-local-train-job/`
