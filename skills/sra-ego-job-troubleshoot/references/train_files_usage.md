# Training Artifact Files and Evidence Workflow

This document describes the key artifact files of an EGO training job, where they are stored, what they mean, and when they should be collected as evidence during troubleshooting.

## 1. Key Artifacts and Directories

### 1.1 `jobs/${job_id}/config/`

- `ego-learner.yaml`
  - Meaning: the main EGO training configuration file.
  - Main use: verify whether training settings, load configuration, data paths, and related parameters match the observed failure.
- `flags.txt`
  - Meaning: the EGO gflags file, used to enable EGO features or configure some runtime hyperparameters.
  - Main use: confirm whether runtime behavior depends on advanced flags or feature toggles.
- `run_files.zip` (the file name depends on the user upload)
  - Meaning: the user-provided runtime dependency package, commonly used for custom converter or runtime logic.
  - Main use: when the failure involves converter or runtime scripts, unpack it and inspect user logic and dependency files.

### 1.2 `jobs/${job_id}/code/`

- `code.zip` (the file name depends on the user upload)
  - Meaning: the model source-code package.
  - Main use: locate model definitions, parameter names or shapes, training logic, and their relationship to the error stack.

### 1.3 `jobs/${job_id}/compile/`

- Notes: this directory stores the compile outputs of the current job. `ego-config.json`, `ego-config.pb`, `model_config.pb`, `model_config.readable`, `graph.pb`, and `graph.readable` are all located in this directory.
- Semantic boundary: the artifacts in this directory describe the model structure and parameter configuration produced by the current job during its own compile step.

- `ego-config.json`
  - Meaning: the structured model compile output.
  - Main use: verify declared features, inputs, targets, rounds, and related model metadata.
- `ego-config.pb`
  - Meaning: the protobuf form of the model compile output.
  - Main use: cross-check configuration consistency against other compile artifacts.
- `graph.pb`
  - Meaning: the binary graph artifact.
  - Main use: validate the actual compiled model structure.
- `graph.readable`
  - Meaning: the human-readable graph artifact.
  - Main use: quickly inspect model structure, nodes, and connections manually.
- `model_config.pb`
  - Meaning: the protobuf form of the EgoPS parameter-server configuration.
  - Main use: verify which slots EgoPS creates when it builds PS tables, and which optimizer plus optimizer hyperparameters each slot uses.
- `model_config.readable`
  - Meaning: the human-readable form of the EgoPS parameter-server configuration.
  - Main use: quickly inspect PS table and slot definitions, optimizer types, and optimizer hyperparameters such as learning rate.

### 1.4 `jobs/${job_id}/ckpt/`

- Notes: this directory stores the checkpoint loaded by the current job, together with the model configuration artifacts that were produced by the job or model which generated that checkpoint. It may also contain `ego-config.json`, `ego-config.pb`, `model_config.pb`, `model_config.readable`, `graph.pb`, and `graph.readable`.
- Semantic boundary: the artifacts in this directory describe the historical source model that produced the checkpoint, not the compile output of the current job.
- Cross-check principle: `ckpt/` and `compile/` may contain files with the same names, but their meanings are different. `ckpt/` reflects the checkpoint source model, while `compile/` reflects the current job model. The underlying models may be the same or different, so troubleshooting must not assume they are equivalent.
- Main use: when the failure is related to checkpoint loading, checkpoint parameter structure, slot or optimizer configuration, or mismatch between the current job and the checkpoint source model, compare `ckpt/` and `compile/` side by side.
- File meanings: the meanings and uses of the files listed above are already defined in the `jobs/${job_id}/compile/` section and are not repeated here.

## 2. Generic Evidence Templates

This section provides generic templates in the form of `error signal -> first-check artifacts -> second-check artifacts -> typical evidence -> output format`. The goal is to help the main workflow and sub-skills perform stable evidence collection without hardcoding a single bad case.

### 2.1 Model-definition consistency issues

- Error signals
  - Failures related to `target`, `round`, input-output declaration, shape consistency, or structural consistency.
  - Common patterns: duplicate definitions, index insertion failures, structure mismatch, or disagreement between graph definition and runtime expectation.
- First-check artifacts
  - `compile/ego-config.json`
  - `compile/graph.readable`
- Second-check artifacts
  - `code/code.zip`
  - `config/run_files.zip`
- Typical evidence
  - `ego-config.json` shows duplicate, missing, or conflicting entries in `targets`, `rounds[*].targets`, or input-output declarations.
  - `graph.readable` shows that the actual model structure does not match the compile configuration or the error stack.
  - Source-code tracing can locate the exact origin of target definition, round assembly, or input concatenation.
- Output format
  - First state the confirmed facts from compile artifacts.
  - Then state the possible source location or generation logic from the original files.
  - The conclusion must clearly distinguish which statements come from compile facts and which come from source-location tracing.

### 2.2 Runtime-configuration consistency issues

- Error signals
  - Failures related to training configuration, checkpoint load configuration, days or eval or path settings, flag toggles, or runtime parameter consistency.
  - Common patterns: missing required fields, duplicated or conflicting fields, or behavior mismatch between YAML and gflags.
- First-check artifacts
  - `config/ego-learner.yaml`
- Second-check artifacts
  - `config/flags.txt`
  - `compile/ego-config.json`
- Typical evidence
  - `ego-learner.yaml` contains duplicate fields, invalid values, conflicting configuration combinations, or fields that map directly to the failed assertion.
  - `flags.txt` overrides YAML semantics at runtime, or misses a required flag.
  - `ego-config.json` reflects a compiled result that does not match the expectation from YAML or flags.
- Output format
  - First list the exact fields and values in the configuration files.
  - Then explain how those values correspond to the log-level failure condition.
  - If YAML, flags, and compile artifacts disagree, clearly identify both sides of the conflict.

### 2.3 Runtime or converter dependency issues

- Error signals
  - Failures related to data-conversion logic, converter scripts, runtime dependency files, or dynamic import behavior.
  - Common patterns: missing scripts, module import failures, runtime parsing errors, or converter output that does not match expectation.
- First-check artifacts
  - `config/run_files.zip`
- Second-check artifacts
  - `config/ego-learner.yaml`
  - `code/code.zip`
- Typical evidence
  - `run_files.zip` is missing a referenced file, uses an incorrect script path, or does not package a required module.
  - `ego-learner.yaml` refers to a converter entry, script path, or parameters that do not match the actual zip content.
  - `code.zip` uses an invocation or import pattern that does not match the runtime package.
- Output format
  - First confirm which script or entry point is actually referenced at runtime.
  - Then explain whether the corresponding file exists in the package and whether the path matches.
  - Finally provide source-code or configuration trace-back.

### 2.4 PS table, slot, and optimizer configuration issues

- Error signals
  - Failures related to PS table creation, missing slots, slot dimension or type mismatch, optimizer configuration anomalies, or optimizer hyperparameters such as learning rate not matching expectation.
  - Common patterns: parameter-table initialization failure, missing slot, slot configuration that does not match runtime behavior, or embedding or dense parameters not using the expected optimizer.
- First-check artifacts
  - `compile/model_config.readable`
- Second-check artifacts
  - `compile/model_config.pb`
  - `compile/ego-config.json`
  - `code/code.zip`
- Typical evidence
  - `model_config.readable` directly shows the PS tables created by EgoPS, the slots under those tables, the optimizer type bound to each slot, and key optimizer hyperparameters.
  - Cross-checking `model_config.pb` and `model_config.readable` can confirm whether slot definitions are missing, optimizer assignments are inconsistent, or some hyperparameters did not take effect as expected.
  - `ego-config.json` or source-code parameter definitions do not match the PS or slot configuration reflected in `model_config.*`.
- Output format
  - First list the compiled facts for the target PS table and related slots.
  - Then list the optimizer type and key hyperparameters.
  - Finally explain the difference between those compiled facts and the observed logs, source definitions, or user expectation.
