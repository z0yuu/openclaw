---
name: sra-ego-load-ckpt-failed
description: >
  EGO checkpoint load diagnosis (EGO 检查点加载诊断) — analyze `DnnModelLoader` checkpoint-load failures with document-backed config comparison and repair guidance.
  TRIGGER when: worker logs mention `DnnModelLoader`, `LoadNNFromCkptToPs`, or `ckpt_gen_config_path`, or task metadata shows `ps load_checkpoint` failure, `Load model got exception`, or `slot[...] invalid`.
  DO NOT TRIGGER when: the failure is unrelated to checkpoint loading, such as plain config syntax issues, local compile failures, or general runtime crashes without ckpt signals.
---

# Role

This case covers checkpoint-load failures confirmed either by:

- failed-worker stack signals such as `DnnModelLoader`, `LoadNNFromCkptToPs`, or `ckpt_gen_config_path`
- task-metadata signals such as `ps load_checkpoint` failure, `Load model got exception`, or `slot[...] invalid`

The goal is not to stop at a vague "checkpoint problem" label. This case must produce:

- the relevant clip/map document guidance
- the configuration differences between the current `ego-learner.yaml` and the document
- the exact field-level differences between current-job and checkpoint-source `model_config.readable` when the error points to slot or schema mismatch
- concrete repair actions based on `checkpoint_id` and `filter_nn`

---

# Trigger

Trigger this case when any of the following is true:

- the failed worker stack contains `DnnModelLoader`
- `01_error_log.json` or `02_error_info.json` contains `LoadNNFromCkptToPs` or `ckpt_gen_config_path`
- task metadata or logs show `ps load_checkpoint` failure, `Load model got exception`, or `slot[...] invalid`

---

# Inputs

- `job_id`
- `TMP_DIR`
- `01_error_log.json`
- `02_error_info.json`
- `get_job.json` (or equivalent job detail)
- `get_job_tasks.json` (or equivalent task metadata)

---

# Preconditions

- `USER_ID_OPENAPI` must be available
- `python` and `jq` must be executable
- To extract Confluence content automatically, you also need:
  - `CONFLUENCE_TOKEN`
- Default base URL: `https://ego-portal.mlp.shopee.io`

---

# Workflow

1. Pre-trigger confirmation (required)

- Check checkpoint-load signals in this order:
  1. `get_job_tasks.json` task metadata
  2. failed `worker` stack
  3. `01_error_log.json` / `02_error_info.json`
- If none of the above contains checkpoint-load signals, exit this case.
- If task metadata already proves checkpoint-load failure, do not block on missing worker raw logs.

2. Fetch job configuration and parameters (executed inside this case)

- Read job details and extract:
  - `checkpoint_id`
  - `filter_nn`
  - `dump_url` for `ego-learner.yaml` in `config_files[]`
- Download `ego-learner.yaml` to `<TMP_DIR/04_ego_learner.yaml>`.
- For `ps load_checkpoint` plus `slot invalid` style failures, force the material-comparison branch.
- Artifact retrieval priority:
  1. must try job-local artifacts first:
     - `<TMP_DIR/05_compile_model_config.readable>` from `jobs/${job_id}/compile/model_config.readable`
     - `<TMP_DIR/06_ckpt_model_config.readable>` from `jobs/${job_id}/ckpt/model_config.readable`
  2. use HDFS or `checkpoint_path` only as fallback when job-local artifacts are unavailable
- If the job-local pair is available, continue immediately and do not block on HDFS fallback.
- Parse the following fields, supporting both naming variants:
  - `train_config.load_dnn_config`
  - `train_config.dnn_load_config`

3. Model-config structure comparison (required when both files are available)

- Run:

```bash
python scripts/compare_model_config.py \
  --current "$TMP_DIR/05_compile_model_config.readable" \
  --checkpoint "$TMP_DIR/06_ckpt_model_config.readable" \
  --output "$TMP_DIR/08_model_config_diff.json"
```

- Use this helper only for fact extraction. It must not replace the final diagnosis.
- Inspect at least:
  - `slot_groups.checkpoint_only_slot_ids`
  - `slot_groups.current_only_slot_ids`
  - `slot_groups.mismatched_shared_blocks`
  - `dnn_slices.mismatched_shared_slices`
- The minimum comparison set for `slot invalid` style failures is:
  - slot or slice existence
  - `dim`
  - optimizer type
  - key optimizer params when relevant
- If the failing slot or slice exists on the checkpoint side but not on the current compile side, record it as direct schema-mismatch evidence.
- If the failing slot or slice exists on both sides but `dim`, optimizer type, or optimizer params differ, record the exact conflicting fields as direct schema-mismatch evidence.
- Do not stop at “may be different”; the output must include the exact conflicting field set when the files are available.

4. Extract document guidance (must be written to artifacts, fixed page)

- Document: `https://confluence.shopee.io/display/MLP/How+to+clip+or+map+nn+parameters`
- Fetch it with:

```bash
python scripts/get_confluence.py \\
  --url "https://confluence.shopee.io/display/MLP/How+to+clip+or+map+nn+parameters" \\
  --json --output "$TMP_DIR/09_clip_map_doc_raw.json"
```

- Extract and structure at least these three categories:
  - `doc_required_keys`: required keys for clip/map scenarios
  - `doc_optional_keys`: optional but common keys
  - `doc_common_misconfig`: common misconfigurations listed by the document
- Write the extracted result to `<TMP_DIR/09_clip_map_doc_extract.json>`.
- If the document fetch fails, handle it in this order:
  - first check whether `CONFLUENCE_TOKEN` is missing;
    - if missing, block and ask the user to provide the token, then retry;
  - if the token exists but the fetch still fails, return `confluence拉取失败，请用户自己参考这个文档：https://confluence.shopee.io/display/MLP/How+to+clip+or+map+nn+parameters`.
- In both failure branches above, stop the case immediately and do not continue to root-cause analysis.

5. Configuration difference analysis (required)

- Compare the dnn load configuration in `ego-learner.yaml` against `doc_required_keys` and `doc_common_misconfig`.
- Produce:
  - `present_keys`
  - `missing_required_keys`
  - `suspicious_values`
  - `doc_mismatch_points`
  - `model_config_mismatch_points`

6. Intent inference (required, not a hardcoded case table)

- Infer the user's intended loading mode from the structure of `load_dnn_config/dnn_load_config`. At minimum cover:
  - `name_shape_auto_match`: `load_nn: true` exists and `mappers/layers/filter_layers` are not explicitly used, so loading mainly relies on same-name same-shape matching, optionally with `lax/greedy`.
  - `layer_clip`: `layers` or `filter_layers` are explicitly used.
  - `mapper_remap`: `mappers` are explicitly used, including offset/length.
- For each inferred mode, record the exact inference evidence fields from YAML. Do not output only a conclusion.
- Validate consistency against the Confluence document:
  - when the inferred mode is `name_shape_auto_match` and the scenario implies loading nn on the worker side after a structural change, check whether PS-side `skip_dnn_params/filter_nn` is enabled.
  - allowed sources: `filter_nn`, `user_define_filter_nn`, `feature_management.filter_nn` (use whichever exists and record the source).
  - if the consistency check fails, such as "should be enabled but is actually false", record it as `doc_consistency_violations` and use it as root-cause input instead of hardcoding another bad case.

7. Joint root-cause analysis (required: document + runtime evidence)

- Root-cause input must include both:
  - document extraction result: `09_clip_map_doc_extract.json`
  - runtime evidence: `01_error_log.json`, `02_error_info.json`, `04_ego_learner.yaml`, `08_model_config_diff.json` when available, and `checkpoint_id/filter_nn`
- Do not conclude from only the logs or only the document.
- Branch A0: `08_model_config_diff.json` shows that the failing slot or slice exists only on the checkpoint side
  - Root cause: current compile schema and checkpoint schema are incompatible.
- Branch A1: `08_model_config_diff.json` shows that the failing slot or slice exists on both sides but has conflicting `dim`, optimizer type, or key optimizer params
  - Root cause: current compile schema and checkpoint schema are incompatible at the field-definition level.
- Branch A: `checkpoint_id` is empty or invalid
  - Root cause: no usable checkpoint was loaded.
- Branch B: `filter_nn == true`
  - Root cause: nn parameters were filtered out during checkpoint loading.
- Branch C: checkpoint and `filter_nn` look normal, but dnn load config is missing required keys or contains invalid values
  - Root cause: `load_dnn_config/dnn_load_config` does not match the document requirements, so `DnnModelLoader` cannot load checkpoint nn metadata correctly.
- Branch D: none of the above match
  - Root cause: the current evidence cannot converge further; fall back to contacting EGO.

8. Output concrete repair steps (no generic guidance)

- Do not write only "fix it according to the document and rerun".
- Repair measures must be specific down to the config-key level, for example:
  - `请在 train_config.load_dnn_config 第 N 项补充 <key>=<expected_value>`
  - `请将 <key> 从 <current> 改为 <expected>`
  - `请移除与文档冲突的 <key>`
- If `08_model_config_diff.json` proves schema mismatch between current compile and checkpoint:
  - tell the user to either align the current model schema back to the checkpoint schema, or switch to a checkpoint that matches the current compile schema
  - do not reduce this case to only `filter_nn` or generic clip-map document advice
- If job-local material files cannot be fetched:
  - explicitly list the missing files and exact target paths
  - explicitly mark the root cause as provisional rather than closed

---

# Hard Rules

- For `slot invalid`, `Load model got exception`, or `ps load_checkpoint` failures, never stop at `fail_reason` alone; always enter the material-comparison branch first.
- For these failures, do not prioritize HDFS `checkpoint_path` before job-local `jobs/${job_id}/ckpt/` and `jobs/${job_id}/compile/` artifacts.
- `ego-learner.yaml` inspection must stay inside this case.
- If the Confluence fetch fails, including missing env vars or auth failure, return immediately and stop the case.
- The Confluence page must stay fixed to `How+to+clip+or+map+nn+parameters`.
- No final root cause is allowed for `slot invalid` style failures unless all are satisfied:
  - both material sides were attempted with job-local priority
  - the slot or slice field diff is shown when the files are available
  - the explanation states why that field diff causes checkpoint load failure
- The output must include all of the following:
  - trigger evidence from task metadata and or stack or logs
  - model-config comparison result when available
  - document extraction summary
  - intent inference evidence from `load_dnn_config` keys/values
  - document-consistency validation result, including `skip_dnn_params/filter_nn`
  - configuration difference points
  - the joint conclusion based on `checkpoint_id/filter_nn`
- If you provide repair measures, they must be config-key specific rather than generic.

---

# Output Contract

- `case_type`: `load_ckpt_fails`
- `trigger_keyword`: `DnnModelLoader`
- `checkpoint_id`: `<value or empty>`
- `filter_nn`: `<true|false|empty>`
- `dnn_load_config_path`: `<train_config.load_dnn_config | train_config.dnn_load_config | empty>`
- `dnn_load_config_present`: `<true|false>`
- `inferred_load_intent`: `<name_shape_auto_match | layer_clip | mapper_remap | unknown>`
- `intent_evidence`: `<which config fields were used for inference>`
- `doc_consistency_violations`: `<document consistency violations, including skip_dnn_params/filter_nn validation>`
- `doc_extract_summary`: `<summary of key clip/map document points>`
- `doc_mismatch_points`: `<list of mismatches against the document>`
- `model_config_mismatch_points`: `<slot/slice/schema differences between current compile and checkpoint when available>`
- `provisional`: `<true|false>`
- `root_cause`: `<branch A0/A1/A/B/C/D conclusion>`
- `repair_measures`: `<config-key-level repair steps>`
- `artifacts`:
  - `<TMP_DIR/01_error_log.json>`
  - `<TMP_DIR/02_error_info.json>`
  - `<TMP_DIR/04_ego_learner.yaml>`
  - `<TMP_DIR/05_compile_model_config.readable>` (optional)
  - `<TMP_DIR/06_ckpt_model_config.readable>` (optional)
  - `<TMP_DIR/08_model_config_diff.json>` (optional)
  - `<TMP_DIR/09_clip_map_doc_extract.json>`
  - `<TMP_DIR/10_load_ckpt_fails.json>`
