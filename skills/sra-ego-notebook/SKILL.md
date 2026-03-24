---
name: sra-ego-notebook
description: >
  Manages EGO Jupyter Notebooks for interactive debugging (EGO Notebook 启动与管理): start, stop, list, extend sessions; interactive config for Docker image and compute.
  TRIGGER when: EGO notebook, Jupyter debugging, interactive model development, or mentions "启动 Notebook", "停止 Notebook", "Notebook 配置", "Jupyter", "交互调试".
  DO NOT TRIGGER when: submitting training jobs, troubleshooting failed jobs, analyzing metrics, triggering CI, or local compile/run.
allowed-tools: []
category: platform
tags: [ego, train, notebook]
---

# EGO Notebook 启动与管理

通过 Python 脚本管理 EGO Jupyter Notebook 会话，支持启动、停止、查看和延长运行时间。

---

## 文档说明

- **本文档**：流程、信息解析、模型/版本解析、脚本操作、关键约定、输出与错误处理。
- **配套文档**：[references/notebook_workflow.md](references/notebook_workflow.md)：Notebook 生命周期、状态管理、API 参考。
- **模型/版本脚本文档**：[references/common_scripts.md](references/common_scripts.md)：`model.py`、`version.py` 的参数、输出与使用场景。
- **脚本文档**：[scripts/README.md](scripts/README.md)：各脚本的参数与用法。
- **执行顺序**：信息解析与补齐 → 模型/版本解析（如需要）→ 脚本操作。各步有依赖，不可跳步或逆序。
- **概念区分**：**model_id**（模型 ID）与 **version_id**（模型版本 ID）不同，不可混用。

---

## 前置条件

- 环境变量 **USER_ID_OPENAPI**（EGO 访问令牌）已设置。
- 脚本会自动从 `~/.zshrc` 或 `~/.bashrc` 读取环境变量。

---

## 1. 信息解析与补齐（在调用任何脚本之前）

从用户 query 中解析下列信息。

### 1.1 必要信息

| 参数     | 说明                                 |
| -------- | ------------------------------------ |
| 模型     | model_id 或 model_name，二选一。     |
| 模型版本 | version_id 或 version_name，二选一。 |

### 1.2 信息补齐策略

| 用户提供                  | 处理方式                                                   |
| ------------------------- | ---------------------------------------------------------- |
| version_id                | 直接使用，跳到第 3 步                                      |
| model_id + version_id     | 直接使用，跳到第 3 步                                      |
| model_name + version_name | 走第 2 步，用 `version.py` 解析                            |
| 仅 model_name             | 走第 2 步，用 `version.py --model-name` 列出版本供用户选择 |
| 仅 version_name           | 询问用户提供模型名或模型 ID                                |
| 什么都没提供              | 询问用户提供模型名+版本名，或 version_id                   |

---

## 2. 模型/版本解析（仅 name → ID 时需要）

> **已有 version_id 时跳过本步**。
>
> 脚本位于 `scripts/` 目录下。
> 详细参数与输出说明见 [references/common_scripts.md](references/common_scripts.md)。

### 2.1 同时知道模型名和版本名

```bash
python3 version.py --model-name <model_name> --name <version_name>
```

输出 model_id 和 version_id，直接进入第 3 步。

### 2.2 只知道模型名，不知道版本名

```bash
python3 version.py --model-name <model_name>
```

列出该模型下所有版本，向用户展示列表并让用户选择。

### 2.3 只知道 model_id，不知道版本

```bash
python3 version.py --model-id <model_id>
```

列出该模型下所有版本，让用户选择。

### 2.4 什么都不知道

```bash
python3 model.py
```

先列出用户的模型，用户选择后再用 2.2 或 2.3 列出版本。

---

## 3. 执行 Notebook 操作

> 前置：已获得 **version_id**（必须）和 **model_id**（配置操作需要）。
>
> 脚本位于 `scripts/` 目录下。

### 3.1 配置 Notebook（如需要）

如果版本未配置 notebook_image 或 notebook_resource（启动失败时会提示），先进行配置：

```bash
# 交互式配置（推荐）
python3 notebook.py configure <model_id> <version_id> --interactive

# 直接指定配置
python3 notebook.py configure <model_id> <version_id> --cpu 10 --memory 40 --image <image_path>
```

### 3.2 启动 Notebook

```bash
# 启动
python3 notebook.py start <version_id>

# 指定过期时间（2小时 = 7200秒）
python3 notebook.py start <version_id> --expiration-time 7200

# 等待启动完成（推荐）
python3 notebook.py start <version_id> --wait
```

### 3.3 其他操作

**查看 Notebooks**：

```bash
python3 notebook.py list --status running
```

**停止 Notebook**：

```bash
# 停止（需要确认）
python3 notebook.py stop <version_id>

# 强制停止（跳过确认）
python3 notebook.py stop <version_id> --force
```

**延长运行时间**（⚠️ 单位是秒）：

```bash
# 延长 2 小时 = 7200 秒
python3 notebook.py extend <version_id> --extend-time 7200
```

---

## 关键约定（必守）

- **所有操作通过 Python 脚本**：名称解析用 `model.py`、`version.py`，notebook 操作用 `notebook.py` 子命令。
- **model_id 与 version_id 不可混用**：按「版本」操作的脚本使用 version_id，配置脚本同时需要 model_id 和 version_id。
- **信息补齐在前**：未收齐必要信息前，仅做询问与补齐，不调用操作脚本。
- **并发限制**：每用户同时只能运行 1 个 notebook，每版本同时只能有 1 个运行中的 notebook。
- **运行时间**：默认 3 小时（10800 秒），可延长。
- **时间单位转换**：用户说"延长 N 小时"时，必须转换为秒：`N × 3600`。
- **数据持久化**：容器是临时的，停止后数据会丢失，需保存到 S3 或 Git。

---

## 输出格式

### 启动成功

| 字段            | 内容                                                                        |
| --------------- | --------------------------------------------------------------------------- |
| Model           | model_name (model_id)                                                       |
| Version         | version_name (version_id)                                                   |
| Job ID          | 启动任务 ID                                                                 |
| 状态            | 启动成功                                                                    |
| EGO Portal 链接 | `{portal_base}/jupyter/{model_name}:{model_id}/{version_name}:{version_id}` |

### 启动失败

返回失败原因并给出建议：

| 失败原因              | 建议                                                                    |
| --------------------- | ----------------------------------------------------------------------- |
| 版本未配置镜像/资源   | 使用 `notebook.py configure <model_id> <version_id> --interactive` 配置 |
| 已有运行中的 notebook | 使用 `notebook.py stop <version_id> --force` 停止                       |
| 项目 quota 不足       | 联系管理员增加配额或等待资源释放                                        |
| 权限不足              | 确认有项目权限（Model 创建者、Version 创建者或项目成员）                |

---

## 详细参考

- **模型/版本脚本**：[references/common_scripts.md](references/common_scripts.md)
- **脚本使用文档**：[scripts/README.md](scripts/README.md)
- **Notebook 工作流程**：[references/notebook_workflow.md](references/notebook_workflow.md)

## Python 版本

- 此 skill 的 Python 脚本最低按 **Python 3.10+** 使用。
- 依据：PEP 585 built-in generics without postponed annotations；match statement。
- 若系统默认 `python3` 低于该版本，请先切到对应版本后再执行，避免语法错误或直接运行失败。
