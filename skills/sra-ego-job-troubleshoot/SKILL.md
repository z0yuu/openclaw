---
name: sra-ego-job-troubleshoot
description: >
  Diagnose EGO job failures with an evidence-first workflow, material-aware verification, and sub-skill dispatch.
  TRIGGER when: the user asks why an EGO job failed, requests root-cause analysis for a `job_id` or `job_name`, or asks to troubleshoot training failure logs and repair actions.
  DO NOT TRIGGER when: the user asks for training metric analysis, Smart Tune optimization only, or local compile/local run execution without a failure-diagnosis intent.
block_until_ms: 600000
---

# Role

You are the main orchestration skill for EGO job troubleshooting.
This skill is responsible only for:

- generic evidence collection and artifact archiving
- bad-case identification
- dispatching to the matched sub-skill for deep investigation
- final root-cause and repair-measure synthesis

Do not stack detailed bad-case logic inside the main skill.

---

# Inputs

- Required: `job_id` or `job_name`
- Optional: problem context such as error snippets, failed stage, or user hypothesis

---

# Shared Context

- Required environment variable: `USER_ID_OPENAPI`
- Optional environment variables:
  - `EGO_BASE_URL` (default `https://ego-portal.mlp.shopee.io`)
  - `CONFLUENCE_TOKEN`
- Cluster routing:
  - If the user explicitly provides `cluster`, resolve it to a single `EGO_BASE_URL` before the first EGO API call.
  - `cluster=sg` maps to `https://ego-portal.mlp.shopee.io`.
  - `cluster=us` maps to `https://ego-portal.mlp.us.shopee.io`.
  - Once `EGO_BASE_URL` is determined for the case, reuse it for all subsequent EGO API calls and for the final `job link`.
  - If `cluster` is not confirmed, do not mix the default SG base URL with an explicit US base URL in the same investigation.
- Working-directory convention:
  - run all commands from this skill root directory: `skills/sra-ego-job-troubleshoot`
- Command convention:
  - Python helpers: `python scripts/<script>.py ...`
  - Shell helpers grouped by sub-skill: `bash scripts/<sub-skill>/<script>.sh ...`
- Platform concept guardrails:
  - `training_job_type` is a routing signal and must be checked before log-keyword-only dispatch.
  - Material-related evidence must follow `error signal -> material mapping -> field verification`; do not jump directly from filename to root cause.

---

# Sub-Skill Routing

Load only the matched sub-skill documents. Do not preload all sub-skills.

| User intent                                   | Trigger keywords or conditions                                                                                                                   | Document                                     | Notes                                              |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------- | -------------------------------------------------- |
| Feature-evaluation failure                    | `training_job_type` is `feature evaluation` or `feature_evaluation`                                                                              | `sub-skills/sra-ego-feat-eval-failed.md`     | Mandatory metadata-first dispatch                  |
| Compile Unicode decode failure                | `compile` plus `UnicodeDecodeError` or `utf-8 codec can't decode`                                                                                | `sub-skills/sra-ego-unicode-error.md`        | Compile-stage decoding only                        |
| Online export StartTraining failure           | `online export start` plus `HttpStartTraining` plus `connection refused`                                                                         | `sub-skills/sra-ego-starttraining-failed.md` | Cross-pod readiness chain                          |
| Failed parquet or converter file localization | parquet corruption, converter failure, or `pipeline failed` with no concrete file path yet                                                       | `sub-skills/sra-ego-locate-failed-files.md`  | Uses raw SS log and helper shell script            |
| OOM diagnosis and Smart Tune handoff          | `OOMKilled`, `exitcode: 137`, `CUDA out of memory`, `CUDNN_STATUS_ALLOC_FAILED`, `CUBLAS_STATUS_ALLOC_FAILED`                                    | `sub-skills/sra-ego-oom-tune-handoff.md`     | Smart Tune handoff                                 |
| NN slice value root cause                     | `NN_SLICE_VALUE` or `Check failed: char_buffer.size()`                                                                                           | `sub-skills/sra-ego-nn-slice-rootcause.md`   | Check checkpoint and batchfea chain                |
| Checkpoint load failure                       | `DnnModelLoader`, `LoadNNFromCkptToPs`, `ckpt_gen_config_path`, `ps load_checkpoint` failure, `Load model got exception`, or `slot[...] invalid` | `sub-skills/sra-ego-load-ckpt-failed.md`     | Job-local artifact comparison before HDFS fallback |

Execution rules:

1. Read only the matched sub-skill document or documents.
2. If more than one sub-skill matches, execute them in evidence-first order, with metadata-triggered sub-skills before pure log-keyword matches.
3. If the request spans multiple workflows or the intent is ambiguous, clarify before loading extra sub-skills.

---

# Reference Index

Load references only when the current investigation step needs them:

- `references/train_files_usage.md`: material-file usage and evidence mapping
- `references/train_job.md`: training job and log API summary

---

# Unified Artifacts

Unified temp directory: `<system-temp>/job_troubleshoot_<job_id>_<YYYYMMDD_HHMMSS>/`

Minimum artifacts from the main flow:

- `01_error_log.json`
- `02_error_info.json`
- `03_root_cause.md`

Matched sub-skills may append more artifacts based on their own contract.

---

# Main Workflow

## Step 0. Resolve job and create temp directory

0. Before the first EGO API script call, resolve the case-level `EGO_BASE_URL` from the user-provided `cluster` when available, and keep that same base URL for the rest of the investigation.
1. If the input is `job_name`, first resolve a unique `job_id` with `scripts/list_jobs.py`.
2. Create `TMP_DIR`.
3. Use `scripts/get_job.py` and `scripts/get_job_tasks.py` to fetch job status, failed stage, and `fail_reason`.

## Step 1. Status branch

- `running`: run blocking diagnosis with `scripts/diagnose_soc_job.py`, output the blocking status, and stop.
- `failed` or `fail_archived`: continue to Step 2.
- Any other status: output with the non-failure template and stop.

## Step 2. Base evidence collection for failed jobs only

1. Run one SOC status diagnosis with `scripts/diagnose_soc_job.py`.
2. Fetch the log file list with `scripts/get_job_log_files.py`.
3. Run metadata-trigger checks from `get_job.py` first:
   - Always inspect `training_job_type`.
   - Use it to trigger sub-skills that depend on job type, such as `feature evaluation`.
4. Then locate the concrete failed pod or container based on `fail_reason`, `error_detail_message`, and failed task instances.
5. In the first round, extract only from the failed pod with two stages:
   - `scripts/extract_error_log.py --role <worker|ss|wc>` -> `01_error_log.json`
   - `scripts/extract_error_info.py` -> `02_error_info.json`
6. Second-round expansion is on-demand only:
   - Expand to other pods such as WC, SS, or other workers only when one of the following is true:
     - a matched sub-skill explicitly requires multi-role logs
     - failed-pod evidence already points to a cross-pod dependency such as coordinator, remote I/O, register, or data-dispatch chain
     - the failed pod alone cannot converge to a root cause
7. Material-related evidence collection is on-demand and must not be hardcoded:
   - If `01/02` or `fail_reason` points to a problem related to config content, compile artifacts, or runtime dependency files, map the relevant material files via `references/train_files_usage.md` and download them for verification.
   - Verification must reach field-definition level, such as duplicate definitions, missing definitions, conflicting definitions, or invalid values. Do not stop at a vague suspicion that one file may be wrong.
   - Evidence order:
     1. start with the minimum necessary files
     2. expand to neighboring materials only if evidence is still insufficient, for example from `ego-learner.yaml` to `flags.txt` or `ego-config.json`
     3. record why each expansion is needed

## Step 3. Sub-skill dispatch

1. Match the investigation against the `Sub-Skill Routing` table above.
2. Load only the matched `sub-skills/*.md` documents.
3. If no rule matches, use generic root-cause synthesis based on `02_error_info.json` plus `fail_reason`.

## Step 4. Final synthesis

1. Write the final conclusion into `03_root_cause.md`.
2. Output with the unified template: root cause, repair measures, limitations, and debug artifacts.

---

# Hard Rules

- Never conclude from a single `fail_reason` alone. Log-level evidence is mandatory, at minimum `01/02`.
- Never replace the two-stage extraction flow by scanning all raw logs directly.
- If additional log inspection is still needed, use the structured extraction flow first, then inspect files directly when necessary.
- Special bad-case investigation flow, additional data collection, and dedicated decision logic must stay inside the matched sub-skill, not in the main skill.
- Dispatch must evaluate both metadata triggers such as `training_job_type` and log-keyword triggers. Do not rely on log keywords alone.
- Always start with failed-pod single-point diagnosis. Before a sub-skill match or explicit cross-pod evidence appears, do not prefetch other pod logs.
- Expand to WC, SS, or other worker logs only when a sub-skill requires it or the failed-pod evidence points to a cross-pod dependency.
- If the error is related to material files, you must execute download, field-level verification, and evidence backfill. Do not conclude only from file names or experience.
- Material-related evidence collection must follow the generic chain of error signal -> material mapping -> field verification. Do not hardcode one individual case as a fixed root cause.
- If one step fails, continue with all remaining usable steps except Step 0, and explain the limitation in `limitations`.
- `repair measures` must prioritize actions the user can directly execute and must stay within user-controllable scope:
  - model code changes
  - training config changes
  - resource-request adjustments
- If `training.fail_reason` hits low-utilization auto-kill semantics such as `GPU shortage`, `Low GPU utilization`, or `Auto-killed by EGO Supervisor`, the first repair measure must be the exact sentence `请继续输入：针对job_id=<job_id>，启动smart tune任务，产出调整建议`.
- In low-utilization auto-kill cases, do not prepend extra phrases such as "according to policy" or "next step"; output only the direct actionable instruction.
- Only when the root cause is an image-internal script bug or image or bin-file bug may you output `请联系EGO同学`, with `job_id` and evidence.
- If the root cause is externally fixable, such as model files, `ego-learner.yaml` format or config, or unreasonable user resource settings, you must tell the user to modify and rerun. Do not tell the user to contact EGO.
- Do not output suggestions that only platform engineers can execute, such as checking internal StartTraining timing or WC readiness timing.

---

# Output Template

- `job name`: <job_name>
- `job link`: `<EGO_BASE_URL>/training/job/<job_id>/detail/info`
- `job status`: <status>
- `error info`: <key evidence summary>
- `root cause`: <clear cause plus evidence sources>
- `repair measures`: <steps the user can execute directly>
- `limitations` (optional): <missing evidence or failed steps>
- `debug artifacts`:
  - `tmp dir`: <TMP_DIR>
  - `error log json`: <TMP_DIR/01_error_log.json>
  - `error info json`: <TMP_DIR/02_error_info.json>
  - `root cause note`: <TMP_DIR/03_root_cause.md>
  - `material evidence` (optional): <TMP*DIR/04*_ / 05\__ ... downloaded materials and parsed outputs>
  - `<sub-skill artifacts>` appended by matched scenarios

---

# Repair Measures Style Guide

Default rules for all bad-case outputs:

- Start each action from the user perspective with direct imperative wording such as `请执行`, `请输入`, or `请确认`.
- Every repair item must be directly actionable. Do not use vague wording such as "adjust appropriately", "it is recommended", or "try to optimize".

The only exception for contacting EGO:

- You may output one direct step: `请联系EGO同学`.
- This applies only to image-internal script bugs or image bin-file bugs.
- Always attach the minimum necessary context: `job_id` plus the key error evidence.

Default rule for externally fixable issues:

- For model files, `ego-learner.yaml`, user resource settings, and similar cases, the recommendation must be “modify and rerun by the user”.

Required wording for low-utilization auto-kill cases, as repair measure item 1:

- `请继续输入：针对job_id=<job_id>，启动smart tune任务，产出调整建议`

## Python 版本

- 此 skill 的 Python 脚本最低按 **Python 3.10+** 使用。
- 依据：PEP 585 built-in generics without postponed annotations；PEP 604 union syntax (X | Y)。
- 若系统默认 `python3` 低于该版本，请先切到对应版本后再执行，避免语法错误或直接运行失败。
