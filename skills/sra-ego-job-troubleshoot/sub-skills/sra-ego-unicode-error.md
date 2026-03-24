---
name: sra-ego-unicode-error
description: >
  EGO compile Unicode decode diagnosis (EGO 编译解码诊断) — inspect downloaded code packages for non-UTF-8 files or AppleDouble pseudo files that break compile-time decoding.
  TRIGGER when: the case is in `compile` stage and logs mention `UnicodeDecodeError`, `utf-8 codec can't decode`, `AppleDouble`, or `__MACOSX/._*`.
  DO NOT TRIGGER when: the failure is unrelated to compile-time text decoding, such as runtime import errors, network fetch failures, or generic compile syntax errors.
---

# Role

This case handles `compile` stage failures with `UnicodeDecodeError` or `utf-8 codec can't decode`.

---

# Trigger

Trigger this case only when both are true:

- the failed stage is `compile`
- `fail_reason` or `02_error_info.json` contains `UnicodeDecodeError` or `utf-8 codec can't decode`

---

# Inputs

- `job_id`
- `TMP_DIR`
- `02_error_info.json` (from the main flow)

---

# Preconditions

- `USER_ID_OPENAPI` must be available
- Required executables:
  - `python scripts/inspect_model_code_encoding.py`
  - optional: `scripts/get_uss_file.py --output`

---

# Workflow

1. Run:

```bash
python scripts/inspect_model_code_encoding.py <job_id> --tmp-dir "$TMP_DIR/code_encoding_check" > "$TMP_DIR/04_code_encoding_check.json"
```

2. Inspect `04_code_encoding_check.json`:

- whether `invalid_entries` is non-empty
- whether `__MACOSX/._*` (AppleDouble) is present
- whether `decode_error` exists, typically including `0xa3`

3. If `__MACOSX/._*` is present, prefer the root cause "Mac packaging pseudo file was treated as source code".
4. Produce the case-specific root cause and repair actions, then return them to the main skill.

---

# Hard Rules

- Zip download must use binary mode. Do not stream it through plain-text stdout.
- You must provide concrete matched file paths, at least the first three.
- Do not misclassify this scenario as a generic network problem.

---

# Output Contract

- `case_type`: `compile_unicode_decode`
- `root_cause`: `non-UTF-8 text files or AppleDouble pseudo files exist in the model code package, causing compile-stage decoding failure`
- `repair_measures`:
  - `清理代码包中的非 UTF-8 文件与 AppleDouble 伪文件（如 __MACOSX/._*）后重新打包上传`
  - `确保源码文本文件统一为 UTF-8 编码，再重新提交训练`
- `artifacts`:
  - `<TMP_DIR/04_code_encoding_check.json>`
