---
name: sra-ego-job-submit
description: >
  Submits EGO training jobs via local scripts (EGO 训练任务提交): parse inputs → portal config → model/version → quota and template → create job.
  TRIGGER when: user wants to submit a new EGO training job, launch a train job on an existing model/version, or mentions "提交训练任务", "launch train job", "create EGO job", "新建训练任务", "submit training job".
  DO NOT TRIGGER when: user only wants to troubleshoot a failed job, analyze metrics, list jobs, or query job details without creating a new job.
category: platform
tags: [ego, train]
---

# EGO 训练任务提交

## 文档说明

- **本文档**：流程、必要/可选信息、模版与覆盖规则、关键约定、自检清单、输出与错误处理。
- **配套文档**：[launch-train-job-params.md](references/launch-train-job-params.md)：body 字段定义、默认值、`training_job_type` 枚举、常见错误与处理。
- **执行顺序**：信息分类与补齐 → 获取门户配置与权限 → 获取模型记录 → 获取模型版本记录 → 组装请求体并提交。各步有依赖，不可跳步或逆序。
- **概念区分**：**model_id**（模型 ID）与 **version_id**（模型版本 ID）不同，不可混用。按「版本」筛选的接口（如 **list jobs**、**list checkpoints**）一律使用第 4 步得到的 **version_id**，禁止传入 model_id。

---

## 前置条件与资源

- 环境变量 **USER_ID_OPENAPI**（EGO 访问令牌）已设置。
- **脚本**：在 `scripts/` 下。门户配置与上传用 **`scripts/utils_api.py`**；模型/版本用 **`scripts/model.py`**、**`scripts/model_version.py`**；Checkpoint 用 **`scripts/checkpoint.py`**；作业列表/详情/创建用 **`scripts/train_job.py`**。执行时工作目录为 **本 skill 根目录**（即 `sra-ego-train-job-submit`），命令形式为 `python scripts/<脚本> <子命令> ...`。
- **参考文档**：API 与响应结构见 **references/** 下 train_job.md、utils.md、model.md、model_version.md、checkpoint.md，需要时加载查阅。

---

## 1. 信息分类与补齐（在调用任何 API 之前）

从用户 query/prompt 中解析下列信息。**未收齐全部必要信息前，仅做询问与补齐，不调用脚本**。

### 1.1 必要信息（缺一不可）

| 参数         | 说明                                                                 |
| ------------ | -------------------------------------------------------------------- |
| 模型         | 模型 id 或模型名，二选一。                                           |
| 模型版本     | 模型版本 id 或版本名，二选一。                                       |
| 训练任务名称 | job_name；长度 2–50 字符，符合命名规范。                             |
| 配置文件路径 | 本地路径，用于上传后作为 config_files（至少包含 ego-learner.yaml）。 |

### 1.2 可选信息（可缺省）

未提供时由模版或 [launch-train-job-params.md](references/launch-train-job-params.md) 默认值补齐。

| 类别       | 参数示例                                                                          |
| ---------- | --------------------------------------------------------------------------------- |
| 任务类型   | training_job_type，默认 "21"（train），见 params 枚举。                           |
| 优先级     | job_priority，P1–P7 对应 1–7，无模版时默认 5。                                    |
| 区域与资源 | zone；wc_resource、worker_resource、sample_server_resource。                      |
| 其他       | offline/online_half_precision、train_image、pending_over_time、checkpoint_id 等。 |

---

## 2. 获取门户配置与用户权限

- 执行 **`python scripts/utils_api.py config`**（无需 base_url 时可省略）。
- 使用返回中的：
  - **gpu_packages**：用于 GPU worker 的 gpuType、cpu、memory（见 params 与 5.1 无模版时资源）。
  - **tenants / projects**：用于第 3 步校验模型所属 tenant/project 是否在用户权限内。
- 若用户无任何租户/项目权限（tenants 为空或所有 tenant 下均无 projects），**直接报错并终止**。
- tenant_id / project_id 从**模型记录**获取，不在本步解析。
- **获取 train_image**：若用户未指定 `train_image`，执行 **`python scripts/utils_api.py framework_versions`** 从返回列表中获取合适的框架镜像地址；**默认优先选用 tf1 镜像**（如 name 含 `tf1` 的项）。

---

## 3. 获取模型记录

- **模型名**：先执行 **`python scripts/model.py list --model_name "xxx" --scope 2`**（个人），若无结果再执行 **`python scripts/model.py list --model_name "xxx" --scope 1`**；从返回解析 model_id 后执行 **`python scripts/model.py get <model_id>`**。
- **模型 id**：直接执行 **`python scripts/model.py get <model_id>`**。
- 未查到模型：**直接报错并终止**，不创建新模型、不询问「是否创建」。
- 从详情取得 **model_id、tenant_id、project_id**（列表项或 model_info 均含）。
- **权限校验**：模型所属 tenant_id、project_id 须落在第 2 步 tenants/projects 内，否则报错终止。
- **约定**：后续一律使用本步得到的 tenant_id、project_id，禁止手填或猜测。

---

## 4. 获取模型版本记录

- **版本名**：执行 **`python scripts/model_version.py list <model_id> --version_name "xxx"`** 从返回解析 version_id，再执行 **`python scripts/model_version.py get <model_id> <version_id>`**。
- **版本 id**：直接执行 **`python scripts/model_version.py get <model_id> <version_id>`**。
- 未查到版本：**直接报错并终止**，不创建新版本。
- 得到 **version_id** 后进入第 5 步。

---

## 5. 组装请求体并提交

### 5.0 获取项目配额（先执行）

执行 **`python scripts/utils_api.py project_quota <project_id>`**（project_id 来自第 3 步），获取各 zone 的 cpu、memory、gpu 剩余量，供 5.1 选 zone 与填 resource。默认值见 [launch-train-job-params.md](references/launch-train-job-params.md)。

### 5.1 查找模版（同版本、同任务类型）

- **前置**：必须已得到第 4 步 **version_id**；**禁止**传 null、省略或误传 model_id。
- **list jobs** 命令：**`python scripts/train_job.py list --version_id <version_id> --list_type 1 --scope 2 --order descend --order_by create_time --page_size 10`**。若 scope=2 无记录，再执行一次 **`--scope 1`**（全部）。
- **必须消费完整脚本输出**：解析脚本标准输出中的 `data`（或 `data.data`）数组后再判断有/无模版；**未解析完整返回前不得假定无模版**。
- **选取模版**：在返回的 data 中取 **training_job_type** 与用户指定类型一致的、create_time 最新的一条。列表返回的 `training_job_type` 可能为字符串（如 `"train"`），组装 body 时须转为 API 所需枚举值（如 `"21"`），见 params 中 training_job_type 枚举。

**有模版时的字段覆盖规则**（必须严格执行）：

| 类别                         | 字段                                                                                                                                                                             | 处理                                                                                                                            |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| 必须覆盖                     | job_name、config_files、tenant_id、project_id                                                                                                                                    | 一律用本次信息：config_files 用 **utils_api.py upload** 上传后的 uss_path/file_name；tenant_id/project_id 来自第 3 步模型记录。 |
| 用户提供则覆盖、否则沿用模版 | training_job_type、job_priority、zone、offline/online_half_precision、pending_over_time/Unit、train_image、wc_resource、worker_resource、sample_server_resource、checkpoint 相关 | 用户未指定 checkpoint 时按 5.2「Checkpoint（可选）」自摸索，不直接沿用模版 checkpoint_id。                                      |
| 其余                         | 其他字段                                                                                                                                                                         | 沿用模版，不修改。                                                                                                              |

- 使用模版时 **zone** 可沿用模版，不要求与当前 project_quota 剩余配额一致。

**无模版时**：

- 直接组装 body，未给出参数用 [launch-train-job-params.md](references/launch-train-job-params.md) 默认值。
- **zone**：优先选有 **gpu** 剩余配额的 zone（如 SG 常用 `offline-sg12`）。
- **worker_resource**：有 GPU 剩余则按 **config** 返回的 **gpu_packages** 填 gpuType、cpu、memory，**mig_gpu** 固定如 `"1"`；无则用 CPU 配置。
- **job_priority**：用户未指定时传 **5**。

### 5.2 配置文件与 Checkpoint

- **config_files**（必填）：用户提供的配置文件路径经 **`python scripts/utils_api.py upload /path/to/ego-learner.yaml[,/path/to/other.yaml]`** 上传（逗号分隔多个路径）。将返回的 results 中每项的 uss_path、file_name 组成数组填入 body.config_files。**data_converter**、**flag_file**、**initialization_script** 可选，同样用 upload 上传后填入对应字段。
- **Checkpoint（可选）**：
  - **用户指定 checkpoint**：执行 **`python scripts/checkpoint.py list <model_id> <version_id>`**（可按 checkpoint_name 等筛选）解析出对应 checkpoint_id 填入。
  - **用户未指定**：解析用户提供的 **ego-learner.yaml** 中 **train_config.days**；元素可能为天粒度（如 `2025-12-16`）或小时粒度（如 `2025-12-16/00`）。取**最小时间点**，按该元素维度减 1（天减 1 天，小时减 1 小时）得匹配时间串；再执行 **`python scripts/checkpoint.py list <model_id> <version_id>`**，在结果中找 **checkpoint name 包含该时间串** 的一条，取其 checkpoint_id；**若无匹配则不填 checkpoint_id**，且不沿用模版 checkpoint_id。

### 5.3 提交与失败处理

- 组装好 body 后执行 **`python scripts/train_job.py create '<body_json>'`**。body 为完整请求对象的 **JSON 字符串**，其中 config_files、wc_resource、worker_resource、sample_server_resource 为对象/数组，**勿二次序列化**。若 JSON 过长，可先写入临时文件再执行：`python scripts/train_job.py create "$(cat /tmp/body.json)"`。
- **提交失败时**：① 按返回 code 查 [launch-train-job-params.md](references/launch-train-job-params.md)「常见错误与处理」；② 检查是否违反下文「关键约定」；③ 给出**具体、可执行**的修改建议。

---

## 关键约定（必守）

- **train_image 校验**：`train_image` 必须以 `harbor.shopeemobile.com/mlp-ego/ego-train-runtime` 开头，否则将被 EGO 平台拒绝。
- **模版覆盖**：有模版时严格按 5.1 表格执行；无模版时用 params 默认值。
- **tenant_id / project_id**：仅来自第 3 步模型记录，禁止手填或猜测。
- **version_id 与 model_id**：**list jobs** 只传 **version_id**（第 4 步）；**list checkpoints** 同时传 model_id（第 3 步）与 version_id（第 4 步）。
- **配置文件与上传**：config_files 必传（至少 ego-learner.yaml）；data_converter、flag_file 等可选；均经 **utils_api.py upload** 上传后使用返回的 uss_path/file_name。upload 入参为逗号分隔的本地路径。
- **资源与 Zone**：GPU worker 须同时设 **mig_gpu** 与 **gpuType**；无模版时 zone 须在 **project_quota** 有剩余；使用模版时 zone 可沿用模版。
- **body 格式**：config_files、wc_resource、worker_resource、sample_server_resource 为**对象/数组**，不得二次 JSON 序列化。

---

## 提交前自检清单

调用 **train_job.py create** 前逐项确认：

- [ ] 已根据 list jobs 脚本**完整输出**解析 data，明确有/无模版；有模版时已按 5.1 覆盖规则组装。
- [ ] **list jobs** 传的是第 4 步 **version_id**，未传 null 或 model_id。
- [ ] tenant_id、project_id 来自第 3 步模型记录；job_name（2–50 字符）、training_job_type、job_priority 已填。
- [ ] config_files 至少一项，每项含 uss_path、file_name（来自 **utils_api.py upload**）。
- [ ] zone 与 quota 有剩余的 zone 一致，**使用模版时除外**。
- [ ] wc_resource、worker_resource、sample_server_resource 为**对象**，非 JSON 字符串；GPU 时同时含 mig_gpu 与 gpuType。
- [ ] body 为整份请求对象的 JSON 字符串，内部字段无二次序列化。

---

## 输出格式

- **提交成功**：创建接口返回 job_id 后，执行 **`python scripts/train_job.py get <job_id>`** 获取详情，向用户返回：
  - **任务名称**：job_name（来自详情）
  - **Link**：`{EGO_BASE_URL}/training/job/{job_id}/detail/info`，用创建返回的 **job_id** 填充。**EGO_BASE_URL** 为门户地址：SG 默认 `https://ego-portal.mlp.shopee.io`，US 为 `https://ego-portal.mlp.us.shopee.io`（勿用 USS 域名如 ego-sg.uss.shopee.io）。
  - **状态**：status（来自详情）
- **提交失败**：返回失败原因（code、message 及可读说明），并对照 [launch-train-job-params.md](references/launch-train-job-params.md)「常见错误与处理」给出**具体、可执行**的修改建议。

---

## 错误处理

提交失败时按 5.3「提交失败时」三步处理；回复须包含**问题原因**与**具体修改动作**。code 与建议对照 [launch-train-job-params.md](references/launch-train-job-params.md)「常见错误与处理」。

## Python 版本

- 此 skill 的 Python 脚本最低按 **Python 3.10+** 使用。
- 依据：PEP 585 built-in generics without postponed annotations；PEP 604 union syntax (X | Y)。
- 若系统默认 `python3` 低于该版本，请先切到对应版本后再执行，避免语法错误或直接运行失败。
