---
name: sra-ego-checkpoint
description: >
  Retrieve EGO (EGO 平台) checkpoint (检查点) information by checkpoint ID, model/version, tenant, or code file; always include sample date (样本日期) parsed from checkpoint_name in responses.
  TRIGGER when: user asks for checkpoint info, checkpoint list, checkpoint details, "检查点", "样本日期", "样本时间", sample time, or which checkpoint to use for a model/version.
  DO NOT TRIGGER when: user only asks for job submission, job logs, job failure diagnosis, or training metrics without checkpoint lookup.
---

# Role

You orchestrate retrieval of EGO (EGO 平台) checkpoint information. You resolve user inputs (checkpoint ID, model/version, tenant, or code file) to the appropriate API flow, run the scripts, and return checkpoint details. **Whenever you return checkpoint information to the user, you must include the sample date (样本日期)** — see "Sample date in output" below.

---

# Inputs

- **Checkpoint ID** — direct lookup
- **Model + version** — model name/ID and version name/ID; resolve names to IDs via list_models / list_versions, then list checkpoints
- **Model only** — list checkpoints under that model via checkpoint management (list_type=2)
- **Tenant only** — tenant name or ID; list all user checkpoints via checkpoint management (list_type=3)
- **Code file only** — match user-provided code file to a version (via list_models scope=2, list_versions, get_version, get_uss_file), then list checkpoints for that version

---

# Shared Context

- **Environment**: `USER_ID_OPENAPI` required. Optional: `EGO_BASE_URL` (default `https://ego-portal.mlp.shopee.io`).
- **Cluster**: If user specifies `cluster=sg` or `cluster=us`, set `EGO_BASE_URL` to the corresponding domain and use it for all calls. SG: `https://ego-portal.mlp.shopee.io`; US: `https://ego-portal.mlp.us.shopee.io`.
- **Working directory**: Run commands from this skill root (e.g. `skills/sra-ego-checkpoint`).
- **Commands**: `python scripts/<script>.py ...` (scripts import from `ego_api_common` in the same directory).

---

# Sample date in output

Checkpoint names often embed the **sample date (样本日期)** as a segment between `#` delimiters. Formats vary, for example:

- `#YYYY-MM-DD/HH#` → e.g. **2026-01-28/00** (`ckpt#...#2026-01-28/00#6104721`)
- `#YYYY-MM-DD#` → e.g. **2026-03-12** (date only, no hour)

- **Rule**: For every checkpoint you return to the user, parse and include **sample date** when present in `checkpoint_name`.
- **Parsing**: Extract a segment matching date-like patterns, e.g. regex `#(\d{4}-\d{2}-\d{2}(?:/\d{2})?)#` to match both `YYYY-MM-DD/HH` and `YYYY-MM-DD`. If no such segment exists, show "—" or "N/A" for sample date.
- **Display**: In tables or summaries, add a column/field **sample date (样本日期)** so the user can quickly see which date each checkpoint corresponds to.

See `references/checkpoint.md` for patterns and API response fields.

---

# Querying by sample date (按样本时间查询)

**None of the EGO checkpoint APIs support filtering or searching by `checkpoint_name` (or by sample date).**

When the user asks for checkpoints for a **specific sample time** (e.g. "样本时间为 2026-03-11/23 的 checkpoint"):

1. **Do not** assume any API can accept a sample-date or checkpoint_name filter.
2. Use the appropriate flow (Flow 2, 3, 4, or 5) according to what the user provided (model, version, tenant, or code file) to **fetch the full checkpoint list**.
3. **After** you have the results, parse the **sample date (样本日期)** from each `checkpoint_name` (see "Sample date in output" above), compare with the user-specified sample time, and **filter** the list to only those that match.
4. Return only the matching checkpoints (with sample date included) to the user.

If the user did not specify a model/version/tenant, clarify scope or use a flow that returns a broader list (e.g. tenant-only), then filter by sample date on the result.

---

# Workflow

Choose one flow based on what the user provided.

## Flow 1: Checkpoint ID only

1. Call `scripts/get_checkpoint.py <checkpoint_id>`.
2. From the response, get `checkpoint_name` and any API field like `sample_timestamp` if present.
3. Parse **sample date (样本日期)** from `checkpoint_name` (see above) and include it in the output.

## Flow 2: Model + version

1. If user gave **model name**, run `scripts/list_models.py` and resolve to `model_id`.
2. If user gave **version name**, run `scripts/list_versions.py <model_id>` and resolve to `version_id`.
3. Run `scripts/list_checkpoints.py` with `model_id` and `version_id` (pass `--base-url` if cluster set).
4. For each checkpoint in the result, parse **sample date** from `checkpoint_name` and include it in the returned information.

## Flow 3: Model only

1. If user gave model name: run `scripts/list_models.py` to get `model_id`; if user gave model ID: run `scripts/get_model.py <model_id>` to get model details. Both APIs return `tenant_id` and `project_id` in the response.
2. Use the `tenant_id` and `project_id` from that response (or pass `project_id` as "ALL" to skip project filter).
3. Run `scripts/list_checkpoint_management.py` with `tenant_id`, `project_id` (or "ALL"), `model_id`, and `list_type=2`.
4. For each checkpoint, include **sample date (样本日期)** parsed from `checkpoint_name` in the response.

## Flow 4: No model/version — tenant only

1. If user gave **tenant name**, run `scripts/get_config.py` and resolve tenant to `tenant_id`.
2. Run `scripts/list_checkpoint_management.py` with `tenant_id` and `list_type=3`.
3. For each checkpoint returned, parse and include **sample date (样本日期)** in the output.

## Flow 5: Code file only

1. Run `scripts/list_models.py` with `scope=2` to get the user's model list.
2. For each model, run `scripts/list_versions.py <model_id>` to get versions.
3. For each version, run `scripts/get_version.py <model_id> <version_id>` to get details (including `code_file`).
4. Run `scripts/get_uss_file.py <url>` as needed to fetch file content (URL from version's `code_file`) and compare with the user's code file.
5. When a version matches the user's code, use its `model_id` and `version_id` and run `scripts/list_checkpoints.py`.
6. In the checkpoint list returned to the user, include **sample date (样本日期)** for each checkpoint parsed from `checkpoint_name`.

---

# Reference

- `references/checkpoint.md` — Checkpoint APIs, request/response fields, and sample date (样本日期) parsing from `checkpoint_name`.
- `references/model.md` — Model APIs for resolving model name to ID (list_models, get_model).
- `references/model_version.md` — Model version APIs for resolving version and code file (list_versions, get_version, get_uss_file).

---

# Output template

When returning checkpoint information, always include:

- **checkpoint_id**, **checkpoint_name**, **sample date (样本日期)** (parsed from `checkpoint_name`; use "—" or "N/A" if not present)
- Other relevant fields: model_id, model_version_id, size, create_time, related job, etc., as returned by the API

Present as a table when listing multiple checkpoints, with **sample date (样本日期)** as a dedicated column.

## Python 版本

- 此 skill 的 Python 脚本最低按 **Python 3.10+** 使用。
- 依据：PEP 604 union syntax (X | Y)。
- 若系统默认 `python3` 低于该版本，请先切到对应版本后再执行，避免语法错误或直接运行失败。
