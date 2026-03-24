---
name: sra-ego-job-analysis
description: >
  Analyzes and compares EGO training effect metrics (AUC, gAUC) at version or job level within a single model (EGO 训练效果指标分析).
  TRIGGER when: user wants to analyze training effect metrics, compare versions/jobs, or mentions "效果分析", "AUC", "gAUC", "版本对比", "training effect", "训练效果", "metric comparison", "version level", "job level".
  DO NOT TRIGGER when: user wants to troubleshoot a failed job, submit a new training job, or only list jobs/versions without metric analysis.
category: platform
tags: [ego, train]
---

# EGO 训练效果指标分析

## 说明与约束

- **限定在同一 model 下**（必守）：本技能只做**同一 EGO model** 内的分析。多 version 即该 model 下的多个版本；多 job 即该 model 下的多个任务（各 job 的 related_model 须一致），若用户给出的多 job 跨 model 则须提示并请用户限定到同一 model 或只分析其中一 model 的 job。
- **维度判定与分支**（必守）：
  - **仅含 model、version**（无 job）：直接进行 **version level** 分析，不追问。支持**同一 model 下的多个 version**，按步骤 3～6 逐项解析后步骤 7 用多值 URL 变量拼接。
  - **输入含有 job**（一个或多个 job_id / job_name /「任务 xxx」等）：先看用户表述是否已明确维度 — 若出现「版本效果」「model version」「版本级」「版本 AUC」等 → 按 **version level** 执行；若出现「单任务曲线」「每个 job 的曲线」「job 维度」等 → 按 **job level** 执行。**仅当表述无法判断维度时**才向用户确认「按 version level 还是 job level？」待明确后再执行；**不得在未确认时自行默认任一维度**。同一请求只做一种维度；多个 job 时仍只问一次维度选择；若多 job 来自不同 model，须先请用户限定到同一 model 再继续。
- **从用户表述解析**：round(s)、target(s) 可选；未指定时步骤 7 用 `All`。**同一 model 下的多个 version、或多个 job** 的 id 或名称均按下列步骤解析，逐项 get 详情后用于 URL 与输出。

---

## 前置条件与资源

- 环境变量 **USER_ID_OPENAPI**（EGO 访问令牌）已设置。
- **Python 版本**：此 skill 的脚本按 **Python 3.9+** 使用；**不要用 Python 3.8**。原因：脚本里使用了 `dict[str, ...]`、`list[...]`、`X | None` 等 3.9/3.10 语法，在 3.8 上会直接 `TypeError: 'type' object is not subscriptable`。若机器默认 `python3` 是 3.8，先换到 3.9+ 解释器再执行，避免重复试错。
- **脚本**：在 `scripts/` 下。作业列表/详情用 **`scripts/train_job.py`**（list、get）；模型用 **`scripts/model.py`**（list、get）；版本用 **`scripts/model_version.py`**（list、get）；Grafana 指标拉取用 **`scripts/get_train_auc.py`**。执行时工作目录为 **本 skill 根目录**（即 `sra-ego-train-job-analysis`），命令形式为 `python scripts/<脚本> <子命令> ...` 或 `python scripts/get_train_auc.py --url ...`。
- **参考文档**：API 与响应结构见 **references/** 下 train_job.md、model.md、model_version.md，需要时加载查阅。
- 脚本拉取 Grafana 时需 **GRAFANA_API_TOKEN**，见 [scripts/README.md](scripts/README.md)。

---

## 执行流程

### 分支规则

- **先按输入判定**：若输入**含有 job**（一个或多个），先校验多 job 是否**同一 model**，若否则请用户限定；再根据用户表述判断维度（见上「维度判定与分支」），若无法判断则向用户确认「version level 还是 job level？」待明确后再执行。若仅 **model + version**（同一 model 下可多个 version），直接走 version level，无需确认。
- **步骤顺序**：

| 维度              | 步骤顺序                                                                                                                                                                                                                                                                                                                                                  |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **job level**     | 1（若有 job name）→ 2（对**每个** job id 取详情；多 job 时校验 **related_model 一致**）→ **跳过 3～6**（**禁止调用** model.py / model*version.py）→ 7 → 8。单 job 时步骤 7 直接用步骤 2 的 **train_auc_url**；**多 job**（同 model）时从各 job 详情的 related*\* 与 job 名称拼 `var-model_names`、`var-model_versions`、`var-job_names`（多值用重复键）。 |
| **version level** | 若输入含 **job**（且用户已选 version level）：1 → 2（对每个 job 取详情；多 job 须**同一 model**）→ 按需 3～6（从步骤 2 得到该 model 下各 version，去重后逐项 get 详情）→ 7 → 8。若输入仅**模型+版本**（**同一 model** 下多个 version）：3～6（按需，对该 model 下每个 version 解析）→ 7 → 8。                                                             |

- **Job level 时禁止执行步骤 3～6**：不解析 model/version 名称与 id，不调用 `model.py`、`model_version.py`；URL 与输出所需名称均来自步骤 2 的 job 详情（如 `related_model_name`、`related_version_name`、job_name）。

### 步骤 1 — Job name → job id

- 仅当输入含 job name 时：对每个 name 执行 **`python scripts/train_job.py list --job_name "xxx"`**；多同名则请用户确认后取 job_id。

### 步骤 2 — Job id → job 详情

- 对每个 job id（步骤 1 或用户给出）**仅**执行 **`python scripts/train_job.py get <job_id>`** 取 job 详情（含 related*model*_、related*version*_、train_auc_url 等）。**禁止调用其他 job 相关接口**（如 tasks、log_files 等）；本技能仅使用 train_job 的 list、get 以及 model、model_version 的 list、get。

### 步骤 3 — 模型名 → model id（**仅 version level**；job level 不执行）

- 执行 **`python scripts/model.py list --model_name "xxx" --scope 2`**，无则再执行 **`python scripts/model.py list --model_name "xxx" --scope 1`**，按 model_name 得 model_id；多同名请用户确认。再执行 **`python scripts/model.py get <model_id>`**。

### 步骤 4 — 模型 id → 模型记录（**仅 version level**；job level 不执行）

- **`python scripts/model.py get <model_id>`**。

### 步骤 5 — 版本名 → version id（**仅 version level**；job level 不执行）

- model_id 来自步骤 3 或 4。执行 **`python scripts/model_version.py list <model_id> --version_name "xxx"`** 按 version_name 得 version_id；多同名请用户确认。再对每个 version_id 执行 **`python scripts/model_version.py get <model_id> <version_id>`**。

### 步骤 6 — 版本 id → 版本记录（**仅 version level**；job level 不执行）

- 对每个 version id 执行 **`python scripts/model_version.py get <model_id> <version_id>`**，model_id 来自步骤 3 或 4。

### 步骤 7 — Grafana 拉取指标

- **区域与 URL**：按用户环境或 **EGO_BASE_URL** 选 SG 或 US。SG：base `https://monitoring.infra.sz.shopee.io/grafana/d/B6FNSQHVz/ego-train-v1-multiple-models-comparison`，`var-mysql_datasource=EGO-Train-MySQL`；US：同 path，`var-mysql_datasource=EGO-Train-US-MySQL`。query 含 `orgId=38`、`from=now-90d`、`to=now`、`var-tag=None`。
- **URL 变量**（**同一 model 下**多 version / 多 job 时多值用重复键；`var-model_names` 同一 model 只出现一次或重复同值）：
  - **Version level**：`var-model_names` 为同一 model（多 version 时该 name 重复或 Grafana 接受单 model 多 version）；`var-model_versions` 从 get_model_version 返回值；**仅支持同一 model 下多个 version**；`var-job_names=All`。
  - **Job level**：单 job 用步骤 2 的 **train_auc_url**；**多 job**（须同一 model）从步骤 2 各 job 详情的 `related_model_name`、`related_version_name`（缺则用 related\_\*\_id 调 get）与**各 job 名称**拼 `var-model_names`、`var-model_versions`、`var-job_names`（三者在多 job 时一一对应、多值重复键）。
  - **var-rounds / var-targets**：用户未指定则 `All`，否则按用户指定（Grafana 无固定枚举，不做校验）。
  - **var-job_types、var-xgauc_path** 等：由脚本从 dashboard 解析并填充，技能侧不拼 URL。
- **执行**：调用脚本拉取指标，输出 JSON。**脚本路径**（工作目录为 **skill 根目录**）：**`python scripts/get_train_auc.py --url <完整URL> --block versioned`** 或 **`--block job`**。环境与 token 见 [scripts/README.md](scripts/README.md)。

### 步骤 8 — 分析并输出

- 对步骤 7 的 JSON 做 version 或 job 维度的效果分析与对比。输出**须包含**：

| 项             | 内容                                                  |
| -------------- | ----------------------------------------------------- |
| model name     | 模型名称（多则逐项）                                  |
| version name   | 版本名称（多则逐项）                                  |
| job name       | job level 时列出（多则逐项）                          |
| analysis level | version / job                                         |
| 数据来源       | Grafana 完整链接                                      |
| 指标详情       | 表格或折线图 + 完整 JSON 本地缓存（如技能目录下文件） |
| 对比分析       | summary（多版本/多 job 对比要点；单条则为摘要）       |
| 结论/建议      | 文字结论或可执行建议                                  |

---

## 关键约定

- **仅用本 skill 脚本**：只可调用 **scripts/train_job.py**（list、get）、**scripts/model.py**（list、get）、**scripts/model_version.py**（list、get）、**scripts/get_train_auc.py**。**禁止调用其他 EGO API 或脚本**（如 train_job 的 tasks、log_files、create，以及 checkpoint、utils_api 等）。
- **名称来源**：URL 中的 model_names、model_versions、job_names 一律用 get 详情（train_job get、model get、model_version get），禁止用 list 结果直接拼。
- **多同名**：list 解析出多条时须请用户确认再继续。
- **单维度**：同一请求只做 version 或 job 一种。仅 model+version（同一 model 下可多 version）时直接 version level；含 job（可多 job，须同一 model）时必须让用户选择 version level 或 job level 后再分析。
- **同一 model 约束**：多 version 仅限同一 model；多 job 的 related_model 须一致，跨 model 时须提示用户限定到同一 model。名称与 URL 变量均逐项用 get 详情（禁止用 list 直接拼）；多值在 URL 中用重复键拼接；步骤 8 输出与对比分析须覆盖全部所列 version 或 job。

---

## 错误与边界

- 某步脚本/API 失败：该步终止并报错，不继续。
- 未配置 GRAFANA_API_TOKEN：步骤 7 前说明需配置，或跳过脚本并提示用户自行在 Grafana 打开链接。
