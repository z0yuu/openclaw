# 模型/版本脚本使用说明

`scripts/model.py` 和 `scripts/version.py` 提供模型/版本的查询与解析能力，用于在用户未提供 ID 时将名称解析为 ID。

脚本位于 `skills/sra-ego-notebook/scripts/` 目录下。

---

## model.py

搜索/列出 EGO 模型。

### 参数

| 参数          | 必选 | 说明                                                            |
| ------------- | ---- | --------------------------------------------------------------- |
| `--name`      | 否   | 按模型名精确匹配                                                |
| `--scope`     | 否   | 1=所有人, 2=个人。不指定时：有 `--name` 则先 2 后 1；无则默认 2 |
| `--page-size` | 否   | 每页数量，默认 50                                               |
| `--json`      | 否   | JSON 格式输出                                                   |

### 使用场景

**场景 1**：用户给了模型名，需要找到 model_id

```bash
python3 model.py --name base_model
```

输出：

```
📦 找到 1 个模型:

   model_id=763      base_model                     模型描述...
```

**场景 2**：用户不确定模型名，列出个人所有模型

```bash
python3 model.py
```

**场景 3**：JSON 输出（供脚本间串联）

```bash
python3 model.py --name base_model --json
```

输出：

```json
{
  "models": [
    {
      "model_id": 763,
      "model_name": "base_model",
      "description": "..."
    }
  ]
}
```

---

## version.py

搜索/列出模型下的版本。支持通过 `model_id` 或 `model_name` 定位模型。

### 参数

| 参数           | 必选   | 说明                            |
| -------------- | ------ | ------------------------------- |
| `--model-id`   | 二选一 | 模型 ID                         |
| `--model-name` | 二选一 | 模型名称（自动解析为 model_id） |
| `--name`       | 否     | 按版本名精确匹配                |
| `--page-size`  | 否     | 每页数量，默认 100              |
| `--json`       | 否     | JSON 格式输出                   |

### 使用场景

**场景 1**：用户给了模型名+版本名，需要一步解析出 model_id 和 version_id

```bash
python3 version.py --model-name base_model --name test_version
```

输出：

```
📦 模型: base_model (model_id=763)

✅ 解析结果:
   model_id     = 763
   version_id   = 3904
   version_name = test_version
```

**场景 2**：用户只给了模型名，需要列出版本供选择

```bash
python3 version.py --model-name base_model
```

输出：

```
📦 模型: base_model (model_id=763)

📋 共 3 个版本:

     1. test_version_a              (version_id=3904)
     2. test_version_b              (version_id=3921)
     3. test_version_c              (version_id=4001)
```

**场景 3**：通过 model_id 列出版本

```bash
python3 version.py --model-id 763
```

**场景 4**：JSON 输出

```bash
python3 version.py --model-name base_model --name test_version --json
```

输出：

```json
{
  "model_id": 763,
  "model_name": "base_model",
  "version_id": 3904,
  "version_name": "test_version"
}
```

---

## 典型工作流

### 用户提供模型名+版本名 → 启动 notebook

```bash
# 1. 解析 name → ID
python3 version.py --model-name base_model --name test_version
# 得到 model_id=763, version_id=3904

# 2. 配置（首次）
python3 notebook.py configure 763 3904 --interactive

# 3. 启动
python3 notebook.py start 3904 --wait
```

### 用户只给了模型名 → 列出版本让用户选

```bash
# 1. 列出版本
python3 version.py --model-name base_model
# 用户选择后得到 version_id

# 2. 启动
python3 notebook.py start <version_id> --wait
```

### 用户什么都不知道 → 列出模型再列版本

```bash
# 1. 列出个人模型
python3 model.py
# 用户选择后得到 model_id

# 2. 列出版本
python3 version.py --model-id <model_id>
# 用户选择后得到 version_id

# 3. 启动
python3 notebook.py start <version_id> --wait
```
