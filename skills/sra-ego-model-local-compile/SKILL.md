---
name: sra-ego-model-local-compile
description: >
  Compile an EGO model locally with explicit user inputs and reproducible artifact output.
  TRIGGER when: the user asks to compile model code locally, build compile artifacts, or rerun local compile from a local source directory or EgoController identifiers.
  DO NOT TRIGGER when: the task is a local run/full-test flow that should route to another skill.
block_until_ms: 600000
---

# Job Local Compile

## Skill Scope

This skill handles real local compile execution for EGO models (from local source or portal identifiers), including rerun with updated inputs.

## Routing Boundary

- If user intent is real compile execution, route to this skill.

## Entry Gate

- `USER_ID_OPENAPI` is mandatory only in portal mode (`model_id` + `model_version_id`).
- In local mode, do not require `USER_ID_OPENAPI`.
- In portal mode, resolve `USER_ID_OPENAPI` from current environment first; do not ask user to type it again if env already has it.

## Boundary

This skill defines compile input contract and execution flow. Task routing decisions should be made by `skill-index.md`.

## Trigger And Interaction Policy

Use this skill when user asks to run local compile, for example:

- "run local compile"
- "compile my EGO model locally"
- "compile model.py"
- "compile model.py with a specific image"

When triggered:

1. Start the `sra-ego-model-local-compile` workflow immediately.
2. Output the full input checklist to user (including optional/default fields).
3. First extract as many inputs as possible from user natural language and local workspace context.
4. Ask user only for missing required inputs.
5. Validate input completeness and correctness.
6. Continue to next steps only after validation passes.

Guardrails:

- Do not start compile execution before required inputs are complete.
- Prefer automatic input extraction from user natural language first; ask follow-up only for unresolved required fields.
- Only the following defaults are allowed when user does not provide values:
  - `EGO_MODE=TRAINING`
  - `cluster=sg`
  - `output_path=<agent-generated-temp-dir>`
- For fields without defaults, if missing or invalid after extraction, stop and ask user to fix them.
- For `rerun` in the same conversation, reuse last valid inputs unless user explicitly changes them.
- If first compile attempt fails, ask user to provide explicit full input checklist and rerun with confirmed values.
- All execution steps that invoke Docker must run with `sudo` by default.
- If `sudo` is unavailable or denied, stop execution and return explicit environment error (do not downgrade silently).

## Step 1: Collect Required Inputs

Always collect required inputs before execution. Try extraction first, then ask for missing fields.

Required input groups:

1. `file_source` (choose one of two modes)
2. `compile_image`
3. `output_path` (optional; if missing, agent generates a temp dir)
4. `EGO_MODE` (`TRAINING` or `SERVING`, default `TRAINING`)

### 1.0 Natural language extraction first (mandatory)

Before asking user for missing fields, extract and resolve from request text:

- if message contains `*.py`, map to `entry_file`
- if message includes full/relative path, derive `source_dir` + `entry_file`
- if only filename is provided (e.g. `model.py`), search workspace:
  - exactly one hit: auto-fill `source_dir` + `entry_file`
  - multiple hits: ask user to choose one
- if message contains image reference (`harbor...`, `repo:tag`), map to `compile_image`

After extraction, ask only for missing required fields.

### 1.1 `file_source` mode A: local directory

User provides a local directory that contains model `.py` files.

Required fields in this mode:

- `source_dir`
- `entry_file` (user must explicitly specify which `.py` file is the entry file)

Rules:

- Allow resolving `entry_file` from user natural language (`*.py`) and workspace search.
- If unresolved or ambiguous after extraction, stop and ask user to provide/confirm it.

### 1.2 `file_source` mode B: EgoController model identifiers

User provides EgoController identifiers:

- `model_id`
- `model_version_id`
- `cluster` (`sg` or `uat` or `us`, default `sg`)
- `USER_ID_OPENAPI` (from current environment by default; user may override explicitly)

Agent must download:

- code files
- `entry_file` information

Rules:

- Do not ask user to provide `entry_file` in this mode unless service response is incomplete.
- If download or metadata resolution fails, stop and report failure reason.
- Resolve `USER_ID_OPENAPI` with priority:
  1. user explicit override in current turn
  2. current environment variable `USER_ID_OPENAPI`
  3. if still missing, stop and ask user to set env variable
- Resolve source by running script:

```bash
bash scripts/get_code_files_from_portal.sh \
  --cluster "<cluster>" \
  --model-id "<model_id>" \
  --model-version-id "<model_version_id>" \
  --user-id-openapi "<USER_ID_OPENAPI>" \
  --output-dir "<resolve_output_dir>"
```

Script outputs:

- resolved `material_dir`
- resolved `entry_file`
- `uss_paths` from portal `code_file[].uss_path` (keep for potential downstream usage)
- resolution summary json (`source_resolution.json`)

Download rule:

- if a code file is zip: download then unzip into `material_dir`
- if a code file is non-zip: download only (no unzip)

### 1.3 Shared and mode-specific fields (must be fully displayed to user)

After `file_source` is confirmed, always collect/display shared fields:

- `compile_image`
- `output_path` (optional; default agent temp dir)
- `EGO_MODE` (`TRAINING` or `SERVING`; default `TRAINING`)

Portal mode only:

- `cluster` (`sg` or `uat` or `us`; default `sg`)
- `USER_ID_OPENAPI` (optional override; default from current environment)

Rules:

- If user omits `EGO_MODE`, set `TRAINING`.
- If user omits `output_path`, generate an agent temp dir under the system temp area, for example `<system-temp>/model-local-compile/<timestamp>-<rand>`.
- Even when defaults are available, blocking prompt must still display all fields with default notes.
- In portal mode, if user omits `cluster`, set `sg`.
- In portal mode, if `USER_ID_OPENAPI` is absent in both user override and environment, stop and ask user to set environment variable.
- If any non-default-backed required field is missing, stop and ask user to provide it.
- If `EGO_MODE` is not `TRAINING` or `SERVING`, stop and ask user to fix it.
- In portal mode, if `cluster` is not `sg`/`uat`/`us`, stop and ask user to fix it.
- Echo all collected inputs before starting compile execution.

### 1.4 Input display template (must follow in blocking message)

```text
Please provide the local compile inputs (full checklist):
[choose one `file_source` mode]
- local: source_dir, entry_file
- portal: model_id, model_version_id, cluster (default: sg), USER_ID_OPENAPI (default: env USER_ID_OPENAPI; optional override)

[common]
- compile_image (required)
- EGO_MODE (default: TRAINING)
- output_path (optional; default: agent temp dir)
```

Notes:

1. `cluster` and `USER_ID_OPENAPI` are portal-only fields.
2. In local mode, do not ask user to provide `USER_ID_OPENAPI`.
3. In portal mode, prefer current environment variable `USER_ID_OPENAPI`; only ask user to set it when env is missing.

## Step 2: Execute Compile Script

Permission rule (mandatory):

- Assume host Docker requires elevated permission.
- Always execute Docker commands with `sudo` by default.
- Before running compile, explicitly check that `sudo` is available for Docker execution in current environment.
- If permission check fails, stop and report error clearly; do not continue with partial execution.

### 2.0 Compile process output capture (mandatory)

For every compile attempt, create a temporary log directory and persist compile process output:

- log root: `<system-temp>/model-local-compile-logs/<timestamp>-<rand>`
- `compile_stdout.log`: full compile stdout stream

Execution rule:

- run compile command with stream tee/redirect so terminal output is preserved while logs are written to files
- apply this rule for both first run and every `rerun`
- do not skip log generation on failure; files must exist in both success and failure paths

Determine `tf_version` from `compile_image` URL/tag:

- contains `tf1` => `tf1`
- contains `tf2` => `tf2`
- otherwise => stop and report unsupported image tag

Use the fixed script to run Step 2:

```bash
bash scripts/container_compile_model.sh \
  --material-dir "<material_dir>" \
  --compile-image "<compile_image>" \
  --ego-mode "<EGO_MODE>" \
  --entry-file "<entry_file>" \
  --output-path "<output_path>"
```

Recommended execution mode (host launches container, container runs compile script):

```bash
sudo docker run --rm \
  -v "<repo_root>:/repo" \
  -v "<material_dir>:/workspace/material" \
  -v "<output_path>:/workspace/output" \
  -w /repo \
  "<compile_image>" \
  bash -lc "bash skills/sra-ego-model-local-compile/scripts/container_compile_model.sh \
    --material-dir /workspace/material \
    --compile-image '<compile_image>' \
    --ego-mode '<EGO_MODE>' \
    --entry-file '<entry_file>' \
    --output-path /workspace/output"
```

Precheck example (recommended):

```bash
sudo -n docker ps >/dev/null 2>&1
```

If precheck fails, return a clear error such as:

- `sudo_not_available`
- `sudo_permission_denied`
- `docker_requires_privilege`

Rationale:

- script writes under `/workspace`, so running inside the compile container avoids host `/workspace` permission issues
- script is Bash-only (`set -Eeuo pipefail`, `trap ERR`, `BASH_*` vars), so always use `bash`, not `sh`

Script behavior:

1. Parse `tf_version` from `compile_image`.
2. Prepare code files under `/workspace`:

- if `tf_version=tf1`, copy code files from `material_dir` directly into `/workspace`
- if `tf_version=tf2`, copy code files from `material_dir` into `/workspace/ego_tf1_dir`

3. If `tf_version=tf2`, run extra upgrade flow:

- create `/workspace/ego_tf2_dir`
- source `/workspace/ego-api-v1/scripts/common.sh`
- execute `upgrade_model_def ego_tf1_dir ego_tf2_dir` under `/workspace` (relative path arguments)

4. If `tf_version=tf1`, run `EGO_MODE=${EGO_MODE} python entry_file.py` under `/workspace`.
5. If `tf_version=tf2`, run `EGO_MODE=${EGO_MODE} python entry_file.py` under `/workspace/ego_tf2_dir`.
6. Copy compile artifacts to `output_path`:

- `ego-config.json`
- `ego-config.pb`
- `graph.pb`
- `graph.readable`

Artifact source rules:

- if `tf_version=tf1` and `EGO_MODE=TRAINING`: artifacts are read from `/workspace`
- if `tf_version=tf1` and `EGO_MODE=SERVING`: artifacts are read from `/workspace/serving`
- if `tf_version=tf2` and `EGO_MODE=TRAINING`: artifacts are read from `/workspace/ego_tf2_dir`
- if `tf_version=tf2` and `EGO_MODE=SERVING`: artifacts are read from `/workspace/ego_tf2_dir/serving`

If any required file/script/artifact is missing, stop and report explicit error.
On any script failure, return concrete diagnostics:

- failed command
- exit code
- error line number
- key runtime context (`tf_version`, `EGO_MODE`, compile directory)

After compile (success or failure), always return:

- `compile_output_path`
- `compile_output_link` (rendered as a clickable path link for user inspection)
- `compile_log_dir`
- `compile_stdout_log`
- `compile_stdout_log_link`

## References

- Step-2 script: `scripts/container_compile_model.sh`
- Step-1 source-resolution script: `scripts/get_code_files_from_portal.sh`
