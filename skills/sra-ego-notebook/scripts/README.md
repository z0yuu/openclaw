# EGO Notebook Scripts

EGO Jupyter Notebook 管理脚本集合，提供启动、停止、配置和查看 Notebook 的功能。

## 环境配置

配置在 `~/.zshrc` 或 `~/.bashrc` 中：

```bash
export USER_ID_OPENAPI="your-token-here"
```

脚本会自动读取环境变量，无需手动 `source`。

---

## 快速开始

### 场景 1: 只知道名称，不知道 ID

```bash
# 通过名称解析出 model_id 和 version_id
python3 version.py --model-name base_model --name test_version

# 只知道模型名？列出所有版本
python3 version.py --model-name base_model

# 什么都不知道？先列出模型
python3 model.py
```

### 场景 2: 首次使用（需要配置）

```bash
# 1. 交互式配置镜像和资源
python3 notebook.py configure 763 3904 --interactive

# 2. 启动 notebook
python3 notebook.py start 3904
```

### 场景 3: 已配置，直接启动

```bash
# 启动
python3 notebook.py start 3904

# 等待启动完成
python3 notebook.py start 3904 --wait
```

### 场景 4: 管理运行中的 Notebook

```bash
# 查看状态
python3 notebook.py list --status running

# 延长 2 小时
python3 notebook.py extend 3904 --extend-time 7200

# 停止
python3 notebook.py stop 3904 --force
```

---

## 脚本说明

### model.py

搜索/列出 EGO 模型。

```bash
# 搜索模型
python3 model.py --name base_model

# 列出个人所有模型
python3 model.py

# JSON 格式输出
python3 model.py --name base_model --json
```

---

### version.py

搜索/列出模型下的版本。支持通过 model_id 或 model_name 定位。

```bash
# 通过模型名+版本名解析 ID
python3 version.py --model-name base_model --name test_version

# 列出模型下所有版本
python3 version.py --model-name base_model

# 通过 model_id 列出版本
python3 version.py --model-id 763

# JSON 格式输出
python3 version.py --model-name base_model --json
```

> 详细参数与输出说明见 [../references/common_scripts.md](../references/common_scripts.md)

---

### notebook.py

Notebook 管理工具，通过子命令操作。

#### notebook.py configure

配置 Notebook 镜像和资源。

```bash
# 交互式配置（推荐）
python3 notebook.py configure <model_id> <version_id> --interactive

# 直接指定配置
python3 notebook.py configure <model_id> <version_id> --cpu 10 --memory 40

# 配置镜像和资源
python3 notebook.py configure <model_id> <version_id> \
  --cpu 10 --memory 40 \
  --image harbor.shopeemobile.com/mlp-ego/ego-train-runtime:V1.8.3-tf2-sg-20251014060941
```

**交互式流程**：

1. 显示当前配置
2. 选择镜像（从列表中选择序号，推荐 TF2）
3. 输入资源配置（CPU、Memory、GPU）
4. 确认并保存

#### notebook.py start

启动 Notebook，成功后自动显示 EGO Portal 访问链接。

```bash
# 基本用法
python3 notebook.py start <version_id>

# 指定过期时间（2小时 = 7200秒）
python3 notebook.py start <version_id> --expiration-time 7200

# 等待启动完成（推荐）
python3 notebook.py start <version_id> --wait

# 指定超时时间（默认 5 分钟）
python3 notebook.py start <version_id> --wait --timeout 600
```

#### notebook.py stop

停止 Notebook。

```bash
# 需要确认
python3 notebook.py stop <version_id>

# 跳过确认
python3 notebook.py stop <version_id> --force
```

#### notebook.py extend

延长运行时间。

```bash
# 延长 1 小时 = 3600 秒
python3 notebook.py extend <version_id> --extend-time 3600

# 延长 2 小时 = 7200 秒
python3 notebook.py extend <version_id> --extend-time 7200
```

**注意**：参数单位是**秒**。

#### notebook.py list

列出 Notebooks，自动生成 EGO Portal 访问链接。

```bash
# 列出所有个人 notebooks
python3 notebook.py list

# 列出运行中的
python3 notebook.py list --status running

# 列出指定版本的
python3 notebook.py list --version-id 3904

# JSON 输出
python3 notebook.py list --json
```

---

## 完整工作流示例

```bash
# 1. 配置（首次使用）
python3 notebook.py configure 763 3904 --interactive

# 2. 启动并等待
python3 notebook.py start 3904 --wait

# 3. 查看状态
python3 notebook.py list --status running

# 4. 延长 2 小时
python3 notebook.py extend 3904 --extend-time 7200

# 5. 停止
python3 notebook.py stop 3904 --force
```

---

## 常见问题

### Q1: 不知道 model_id 或 version_id？

**方法 1**：通过名称解析：

```bash
python3 version.py --model-name base_model --name test_version
```

**方法 2**：从 EGO Portal URL 中获取：

```
https://ego-portal.../model/notebook/base_model:763/version/test_version:3904/...
                                              ^^^                        ^^^^
                                           model_id                  version_id
```

**方法 3**：使用 `notebook.py list` 查看已有 notebook 的模型和版本信息。

### Q2: 启动失败怎么办？

查看错误提示：

- **未配置镜像/资源**: 使用 `notebook.py configure --interactive` 配置
- **已有运行中的 notebook**: 使用 `notebook.py stop --force` 停止
- **quota 不足**: 联系管理员或等待资源释放

### Q3: 如何选择镜像？

使用交互式配置，会列出所有可用镜像：

- 推荐选择标记为 `🔥 TF2` 的最新 TensorFlow 2.x 镜像
- 如果不确定，选择序号 1（通常是最新版本）

### Q4: 时间单位转换

| 时长    | 秒数         |
| ------- | ------------ |
| 30 分钟 | 1800         |
| 1 小时  | 3600         |
| 2 小时  | 7200         |
| 3 小时  | 10800 (默认) |
| 6 小时  | 21600        |
| 12 小时 | 43200        |
| 24 小时 | 86400        |

---

## 注意事项

1. **认证**：需要 `USER_ID_OPENAPI` 环境变量
2. **并发限制**：每用户同时只能运行 1 个 notebook，每版本同时只能有 1 个运行中的 notebook
3. **数据持久化**：容器是临时的，停止后数据会丢失，需保存到 S3 或 Git
4. **时间单位**：所有脚本参数使用**秒**作为时间单位

---

## 依赖

```bash
pip install requests
```

---

## 脚本列表

| 脚本                    | 功能           | 参数                                     |
| ----------------------- | -------------- | ---------------------------------------- |
| `model.py`              | 搜索/列出模型  | [--name] [--scope]                       |
| `version.py`            | 搜索/列出版本  | --model-id 或 --model-name, [--name]     |
| `notebook.py configure` | 配置镜像和资源 | model_id, version_id, [--interactive]    |
| `notebook.py start`     | 启动 notebook  | version_id, [--wait] [--expiration-time] |
| `notebook.py stop`      | 停止 notebook  | version_id, [--force]                    |
| `notebook.py extend`    | 延长运行时间   | version_id, --extend-time                |
| `notebook.py list`      | 查看 notebooks | [--status] [--version-id]                |
