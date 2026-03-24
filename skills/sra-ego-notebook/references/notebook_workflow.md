# EGO Notebook 工作流程详解

本文档详细说明 EGO Notebook 的启动流程、状态管理和常见问题。

## 目录

- [Notebook 生命周期](#notebook-生命周期) - 状态转换和说明
- [启动流程](#启动流程) - 配置检查和启动过程
- [停止和延长时间](#停止和延长时间) - 管理运行中的 Notebook
- [常见问题](#常见问题) - 错误排查和解决方案
- [相关 API](#相关-api) - API 端点参考

---

## Notebook 生命周期

### 状态转换

```
[未配置] → [配置完成] → [启动中] → [运行中] → [停止]
                ↓           ↓          ↓
              [失败]     [失败]    [过期自动停止]
```

### 状态说明

| 状态      | 说明             | 可执行操作           |
| --------- | ---------------- | -------------------- |
| `created` | 已创建，等待调度 | 停止                 |
| `pending` | 正在调度和启动   | 停止                 |
| `running` | 运行中，可访问   | 访问、停止、延长时间 |
| `failed`  | 启动失败         | 查看日志、重新启动   |
| `closed`  | 已停止           | 重新启动             |

---

## 启动流程

### 1. 版本配置检查

启动前必须配置：

**notebook_image**: Docker 镜像路径

- 示例: `harbor.shopee.io/mlp/ego-notebook:tensorflow-2.15.0`
- 必须包含 Jupyter Notebook 环境

**notebook_resource**: 资源配置（JSON 格式）

```json
{
  "server_resource": {
    "cpu": 10,
    "memory": 40,
    "gpu_type": "A100",
    "mig_gpu": "1"
  }
}
```

脚本会自动检查并配置这些字段。

### 2. 并发限制检查

- **每个用户**：同时只能运行 1 个 notebook
- **每个版本**：同时只能有 1 个运行中的 notebook

违反限制时需先停止现有 notebook。

### 3. 权限检查

可以启动 notebook 的用户：

- Model 创建者
- Model Version 创建者
- 项目成员（读写权限）

### 4. 启动过程

1. **创建记录**：在数据库创建 notebook 记录，默认过期时间 3 小时
2. **选择 Zone**：根据项目 quota 和环境自动选择（SG 或 US）
3. **调度任务**：提交到 SOC 平台调度
4. **容器启动**：拉取镜像、启动容器、启动 Jupyter
5. **状态更新**：从 `created` → `pending` → `running`

启动通常需要 1-3 分钟。

---

## 停止和延长时间

### 停止 Notebook

**手动停止**：

```bash
python3 stop_notebook.py --model-name <name> --version-name <version>
```

**自动停止**：

- 运行时间超过过期时间
- 容器 OOM 或节点故障

停止后数据会丢失，需提前保存到 S3 或 Git。

### 延长运行时间

```bash
# 延长 2 小时 = 7200 秒
python3 extend_notebook_time.py --model-name <name> --version-name <version> --extend-time 7200
```

**注意**：

- 只能延长 `running` 状态的 notebook
- 可以多次延长
- 建议每次延长 1-2 小时

---

## 常见问题

### Q1: 启动失败，状态为 failed

**可能原因**：

1. 镜像不存在或无法拉取
2. 资源不足（quota 已用完）
3. SOC 平台调度失败

**排查方法**：

1. 检查 `notebook_image` 是否正确
2. 检查项目 quota 是否有足够资源
3. 查看 EGO job 日志

### Q2: 无法启动新的 Notebook

**可能原因**：

1. 已有运行中的 notebook（用户或版本限制）
2. 未配置 `notebook_image` 或 `notebook_resource`
3. 权限不足

**解决方法**：

1. 使用 `list_notebooks.py` 查看现有 notebook
2. 停止不需要的 notebook
3. 检查版本配置和权限

### Q3: 数据丢失了

**原因**：Notebook 容器是临时的，停止后数据会丢失。

**解决方法**：

1. 将重要数据保存到 S3
2. 将代码提交到 Git
3. 使用挂载的持久化存储（如果配置了）

### Q4: Notebook 突然停止了

**可能原因**：

1. 运行时间超过过期时间
2. 容器 OOM（内存不足）
3. 节点故障

**解决方法**：

1. 及时延长运行时间
2. 调整资源配置（增加内存）
3. 重新启动 notebook

---

## 相关 API

### 启动 Notebook

```
POST /notebook/start
{
  "version_id": 12345,
  "expiration_time": 10800  // 过期时间（秒），默认 3 小时
}
```

### 停止 Notebook

```
POST /notebook/stop
{
  "version_id": 12345
}
```

### 延长运行时间

```
POST /notebook/extend_time
{
  "version_id": 12345,
  "extend_time": 60  // 延长时间（分钟）
}
```

**注意**：API 使用**分钟**作为单位，但脚本参数使用**秒**。

### 查询 Notebook

```
GET /notebooks?version_id=12345
GET /notebooks?status=running
GET /notebooks?scope=0  // 0=个人, 1=所有
```

### 获取 Notebook 详情

```
GET /notebook/{notebook_id}
```

返回包含：

- 状态、创建时间、运行时间
- 剩余时间、过期时间
- 访问链接（如果 running）
