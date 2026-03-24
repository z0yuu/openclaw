---
name: sra-ego-feat-eval-failed
description: >
  EGO feature evaluation diagnosis (EGO 特征评估诊断) — validate `eval_fea_config` and compare the job configuration with the Feature Importance guidance.
  TRIGGER when: `training_job_type` is `feature evaluation` or `feature_evaluation`, or the user asks to diagnose a feature evaluation training failure.
  DO NOT TRIGGER when: the job is a generic training, local compile/run, or troubleshooting case unrelated to feature evaluation configuration.
---

# Role

This case handles failed `feature evaluation` or `feature_evaluation` jobs.
The core workflow is to verify `eval_fea_config` in `ego-learner.yaml` and compare it against the Feature Importance documentation before giving repair actions.

---

# Trigger

Trigger this case when:

- `training_job_type` is `feature evaluation` or `feature_evaluation`.

---

# Inputs

- `job_id`
- `TMP_DIR`
- `get_job.json`
- `01_error_log.json`
- `02_error_info.json`

---

# Preconditions

- `USER_ID_OPENAPI` must be available
- Required executables:
  - `scripts/get_uss_file.py`
  - `scripts/get_confluence.py`
- Required for Confluence access:
  - `CONFLUENCE_TOKEN`

---

# Workflow

1. Primary branch: configuration validation (required)

- Read `config_files` from `get_job.json` and download `ego-learner.yaml` to `<TMP_DIR/04_ego_learner.yaml>`.
- Check whether `train_config.eval_fea_config` exists and is non-empty.
- Also extract the related fields for this case:
  - `train_config.eval_data_path`
  - `train_config.days`
  - `train_config.data_time_format`

2. Primary branch: document validation (required, fixed page)

- You must fetch this document:
  - `https://confluence.shopee.io/display/MLP/How+to+Evaluate+Feature+Importance`
- Use:

```bash
python scripts/get_confluence.py \
  --url "https://confluence.shopee.io/display/MLP/How+to+Evaluate+Feature+Importance" \
  --json --output "$TMP_DIR/09_feature_eval_doc_raw.json"
```

- After a successful fetch, extract the key configuration requirements from the document, compare them with the current `eval_fea_config`, and combine that with the `01/02` log evidence to produce concrete repair actions.

3. Fallback branch: Confluence unavailable

- If `CONFLUENCE_TOKEN` is missing:
  - block and ask the user to provide the token, then retry.
- If the environment is complete but the fetch still fails:
  - output directly:
    `confluence拉取失败，请用户自己参考这个文档：https://confluence.shopee.io/display/MLP/How+to+Evaluate+Feature+Importance`
  - do not attempt any document-comparison-based repair suggestion in this branch.

4. Final fallback branch

- If `eval_fea_config` plus the available log evidence still cannot converge to a root cause:
  - report the evidence gap and ask the user to provide the full `ego-learner.yaml` and the raw failed worker log.

---

# Hard Rules

- You must check the job type first and confirm it is `feature evaluation/feature_evaluation`.
- You must inspect `eval_fea_config` before giving any suggestion.
- You must fetch the fixed Confluence page `How+to+Evaluate+Feature+Importance` before concluding on the root cause.
- Root-cause analysis must be based on the combination of document guidance, current configuration, and `01/02` log evidence. Do not conclude from only one side.
- If the Confluence fetch fails, you must return the fixed fallback sentence with the document link.
- Suggestions must stay within user-executable scope, such as config fixes, code fixes, or resubmitting the job.

---

# Output Contract

- `case_type`: `feature_eval_fails`
- `job_type`: `<training_job_type>`
- `eval_fea_config_present`: `<true|false>`
- `doc_fetch_status`: `<success|missing_env|failed>`
- `root_cause`: `<conclusion based on config plus logs; if doc fetch failed, say the user must refer to the document manually>`
- `repair_measures`:
  - doc fetch success: `concrete executable advice based on the document and config differences`
  - doc fetch failure: `confluence拉取失败，请用户自己参考这个文档：https://confluence.shopee.io/display/MLP/How+to+Evaluate+Feature+Importance`
- `artifacts`:
  - `<TMP_DIR/01_error_log.json>`
  - `<TMP_DIR/02_error_info.json>`
  - `<TMP_DIR/04_ego_learner.yaml>`
  - `<TMP_DIR/09_feature_eval_doc_raw.json>`
