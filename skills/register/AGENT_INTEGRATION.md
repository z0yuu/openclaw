# Agent 集成指南

完整的外部 agent 接入文档。

---

## 📖 目录

- [快速开始](#快速开始)
- [协议说明](#协议说明)
- [会话隔离](#会话隔离)
- [健康检查](#健康检查)
- [高级功能](#高级功能)
- [API 参考](#api-参考)
- [示例代码](#示例代码)

---

## 快速开始

### 前置要求

- **my_agent 地址**: `http://10.169.72.91:5002`
- **网络要求**: 你的 agent 必须能访问该地址，且 my_agent 能访问你的端口

### 3 步接入

#### 1. 实现 HTTP 接口

```python
from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)
sessions = defaultdict(list)  # 会话存储

@app.route("/health", methods=["GET"])
def health():
    """健康检查（推荐）"""
    return "ok", 200

@app.route("/api/chat", methods=["POST"])
def chat():
    """主处理接口"""
    data = request.get_json()

    # 提取信息
    message = data.get("message", "")
    conversation_id = data.get("conversation_id", "default")
    user_id = data.get("user_id", "")

    # 使用独立会话（重要！避免多用户混淆）
    session = sessions[conversation_id]
    session.append({"role": "user", "content": message})

    # 你的业务逻辑
    response = f"收到: {message}"

    session.append({"role": "assistant", "content": response})

    # 限制历史长度
    if len(session) > 20:
        session[:] = session[-20:]

    return jsonify({"response": response, "status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

#### 2. 注册到 my_agent

```python
import httpx

response = httpx.post(
    "http://10.169.72.91:5002/agent",
    json={
        "message": (
            "register_agent("
            "agent_id='my_agent', "
            "name='My Agent', "
            "endpoint='http://你的IP:8080/api/chat', "
            "description='你的 agent 功能描述', "
            "capabilities='能力1,能力2,能力3'"
            ")"
        )
    },
    timeout=30
)
print(response.json())
```

#### 3. 测试调用

```python
# 测试你的 agent
response = httpx.post(
    "http://10.169.72.91:5002/agent",
    json={
        "message": "call_agent(agent_id='my_agent', message='测试请求')"
    },
    timeout=30
)
print(response.json())
```

---

## 协议说明

my_agent 支持两种协议，根据请求格式自动识别。

### Simple Protocol（推荐，简单易用）

**请求格式**:

```json
{
  "message": "用户的查询",
  "conversation_id": "dm_user123",
  "user_id": "ou_1234567890",
  "user_name": "张三"
}
```

**响应格式**:

```json
{
  "response": "agent 的回复",
  "status": "success"
}
```

### Agent2Agent Protocol（标准化）

**请求格式**:

```json
{
  "sender": {
    "id": "my_agent",
    "name": "My Agent",
    "type": "agent"
  },
  "recipient": {
    "id": "your_agent",
    "name": "Your Agent",
    "type": "agent"
  },
  "action": "process",
  "payload": {
    "message": "用户的查询",
    "context": {
      "conversation_id": "dm_user123",
      "user_id": "ou_1234567890",
      "user_name": "张三"
    }
  },
  "request_id": "req_1707234567890"
}
```

**响应格式**:

```json
{
  "sender": {
    "id": "your_agent",
    "name": "Your Agent",
    "type": "agent"
  },
  "recipient": {
    "id": "my_agent",
    "name": "My Agent",
    "type": "agent"
  },
  "status": "success",
  "payload": {
    "message": "agent 的回复"
  },
  "request_id": "req_1707234567890"
}
```

**兼容实现**（同时支持两种协议）:

```python
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()

    # 自动识别协议
    if "payload" in data:
        # Agent2Agent 协议
        payload = data["payload"]
        message = payload.get("message", "")
        context = payload.get("context", {})
        conversation_id = context.get("conversation_id", "default")
        user_id = context.get("user_id", "")
    else:
        # Simple 协议
        message = data.get("message", "")
        conversation_id = data.get("conversation_id", "default")
        user_id = data.get("user_id", "")

    # 处理消息...
    response = process(message, conversation_id, user_id)

    # 返回（Simple 格式即可，my_agent 会自动转换）
    return jsonify({"response": response, "status": "success"})
```

---

## 会话隔离

### 为什么需要会话隔离？

当多个用户同时使用你的 agent 时，如果不做隔离，会出现上下文混淆：

❌ **错误做法**（所有用户共享一个会话）:

```python
global_history = []  # 所有用户共享！

def chat():
    message = request.json.get("message")
    global_history.append(message)  # 混在一起了
    response = process(global_history)  # 会串话！
    return {"response": response}
```

✅ **正确做法**（每个会话独立）:

```python
from collections import defaultdict
sessions = defaultdict(list)  # 每个 conversation_id 独立

def chat():
    message = request.json.get("message")
    conversation_id = request.json.get("conversation_id", "default")

    # 使用独立的会话历史
    session = sessions[conversation_id]
    session.append({"role": "user", "content": message})

    response = process(session)  # 不会混淆

    session.append({"role": "assistant", "content": response})
    return {"response": response}
```

### 会话信息字段

my_agent 在调用你的 agent 时，会自动传递以下字段：

| 字段              | 说明                               | 示例                           |
| ----------------- | ---------------------------------- | ------------------------------ |
| `conversation_id` | 会话标识符（必须用这个隔离上下文） | `"dm_user123"`, `"thread_456"` |
| `user_id`         | 用户的平台 ID                      | `"ou_1234567890"`              |
| `user_name`       | 用户显示名称                       | `"张三"`                       |

### 会话管理最佳实践

```python
from collections import defaultdict
import time

sessions = defaultdict(list)

def chat():
    data = request.get_json()
    conversation_id = data.get("conversation_id", "default")
    message = data.get("message", "")

    # 1. 获取会话
    session = sessions[conversation_id]

    # 2. 添加用户消息
    session.append({
        "role": "user",
        "content": message,
        "timestamp": time.time()
    })

    # 3. 处理（使用完整历史）
    response = your_llm.generate(messages=session)

    # 4. 添加助手响应
    session.append({
        "role": "assistant",
        "content": response,
        "timestamp": time.time()
    })

    # 5. 限制历史长度（避免内存爆炸）
    if len(session) > 20:
        session[:] = session[-20:]

    return {"response": response, "status": "success"}

# 定期清理过期会话（可选）
def cleanup_old_sessions():
    now = time.time()
    for conv_id, session in list(sessions.items()):
        if session and (now - session[-1].get("timestamp", 0)) > 3600:
            del sessions[conv_id]
```

---

## 健康检查

### 为什么需要健康检查？

my_agent 每 5 分钟自动检查所有 agents 的可用性：

- ✅ **只推荐健康的 agents**
- ✅ **自动过滤不可用的 agents**
- ✅ **提高系统可靠性**

### 实现方式

最简单的实现（推荐）:

```python
@app.route("/health", methods=["GET"])
def health():
    return "ok", 200
```

带依赖检查的实现:

```python
@app.route("/health", methods=["GET"])
def health():
    try:
        # 检查关键依赖
        # db.ping()  # 数据库
        # redis.ping()  # 缓存

        return {"status": "ok", "timestamp": time.time()}, 200
    except Exception as e:
        return {"status": "error", "error": str(e)}, 503
```

### 健康检查流程

my_agent 会依次尝试以下端点（任一成功即为健康）：

1. `GET {your_endpoint}/health`
2. `GET {your_endpoint}/ping`
3. `POST {your_endpoint}` with `{"message": "ping"}`
4. `GET {your_endpoint}` (root)

**推荐**：实现专用的 `/health` 端点（最快）。

---

## 高级功能

### 1. 智能推荐

my_agent 会自动记录你的 agent 完成的任务，并根据以下因素推荐：

- 📝 **历史任务匹配** — 相似问题优先推荐
- 🎯 **能力匹配** — capabilities 关键词匹配
- ✅ **成功率** — 历史成功率高的优先
- ⭐ **用户评分** — 平均评分高的优先

无需额外开发，自动生效！

### 2. 用户评分

用户可以对你的 agent 进行评分（0-5 分）：

- **0 分** = 👎 不满意
- **1-5 分** = ⭐ 满意（5 分最高）

评分会影响你的 agent 在推荐列表中的排名。

### 3. 自动委派

当用户提出问题时，my_agent 可以自动选择最合适的 agent 处理，无需用户手动选择。

你的 agent 被调用的概率取决于：

- 📊 **相关性分数** — 与用户问题的匹配度
- 💚 **健康状态** — 只有健康的 agents 会被考虑
- ⭐ **历史表现** — 成功率和评分

---

## API 参考

### my_agent 提供的工具

你的 agent 可以通过 my_agent 调用这些工具：

| 工具             | 功能            | 示例                                                              |
| ---------------- | --------------- | ----------------------------------------------------------------- |
| `register_agent` | 注册 agent      | `register_agent(agent_id='...', name='...', endpoint='...', ...)` |
| `list_agents`    | 列出所有 agents | `list_agents()` 或 `list_agents(show_all=true)`                   |
| `search_agents`  | 搜索 agents     | `search_agents(query='销售')`                                     |
| `call_agent`     | 调用其他 agent  | `call_agent(agent_id='...', message='...')`                       |
| `suggest_agent`  | 推荐 agent      | `suggest_agent(query='生成报表')`                                 |
| `auto_delegate`  | 自动委派        | `auto_delegate(query='查询数据')`                                 |
| `rate_agent`     | 评分            | `rate_agent(agent_id='...', rating=5, comment='很好')`            |

### 调用示例

```python
import httpx

# 调用 my_agent 的工具
response = httpx.post(
    "http://10.169.72.91:5002/agent",
    json={
        "message": "list_agents()"  # 工具调用
    },
    timeout=30
)
print(response.json()["response"])

# 调用其他 agent
response = httpx.post(
    "http://10.169.72.91:5002/agent",
    json={
        "message": "call_agent(agent_id='report_agent', message='生成月度报表')"
    },
    timeout=30
)
print(response.json()["response"])
```

---

## 示例代码

### 完整可运行示例

```python
from flask import Flask, request, jsonify
from collections import defaultdict
import httpx
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

# 配置
MY_AGENT_ENDPOINT = "http://10.169.72.91:5002/agent"
MY_AGENT_ID = "example_agent"
MY_ENDPOINT = "http://localhost:8080/api/chat"  # 改成你的实际地址

# 会话存储
sessions = defaultdict(list)

@app.route("/health", methods=["GET"])
def health():
    """健康检查"""
    return "ok", 200

@app.route("/api/chat", methods=["POST"])
def chat():
    """主处理接口"""
    data = request.get_json()

    # 兼容两种协议
    if "payload" in data:
        # Agent2Agent 协议
        payload = data["payload"]
        message = payload.get("message", "")
        context = payload.get("context", {})
        conversation_id = context.get("conversation_id", "default")
        user_id = context.get("user_id", "")
        user_name = context.get("user_name", "")
    else:
        # Simple 协议
        message = data.get("message", "")
        conversation_id = data.get("conversation_id", "default")
        user_id = data.get("user_id", "")
        user_name = data.get("user_name", "")

    logger.info(f"Received: conv={conversation_id}, user={user_id}, msg={message[:50]}")

    # 使用独立会话
    session = sessions[conversation_id]
    session.append({"role": "user", "content": message})

    # 处理消息（这里简化为 echo）
    response = f"[{MY_AGENT_ID}] 收到来自 {user_name or user_id} 的消息: {message}"

    session.append({"role": "assistant", "content": response})

    # 限制历史长度
    if len(session) > 20:
        session[:] = session[-20:]

    return jsonify({"response": response, "status": "success"})

def register():
    """注册到 my_agent"""
    try:
        response = httpx.post(
            MY_AGENT_ENDPOINT,
            json={
                "message": (
                    f"register_agent("
                    f"agent_id='{MY_AGENT_ID}', "
                    f"name='Example Agent', "
                    f"endpoint='{MY_ENDPOINT}', "
                    f"description='示例 Agent，展示如何接入 my_agent', "
                    f"capabilities='示例,测试,演示'"
                    f")"
                )
            },
            timeout=30
        )
        logger.info(f"注册成功: {response.json()}")
    except Exception as e:
        logger.error(f"注册失败: {e}")

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)

    # 启动时注册
    register()

    # 启动服务
    app.run(host="0.0.0.0", port=8080)
```

### 测试脚本

```python
import httpx

MY_AGENT_ENDPOINT = "http://10.169.72.91:5002/agent"

# 1. 列出所有 agents
response = httpx.post(
    MY_AGENT_ENDPOINT,
    json={"message": "list_agents()"}
)
print("所有 agents:")
print(response.json()["response"])

# 2. 调用你的 agent
response = httpx.post(
    MY_AGENT_ENDPOINT,
    json={"message": "call_agent(agent_id='example_agent', message='测试消息')"}
)
print("\n调用结果:")
print(response.json()["response"])

# 3. 评分
response = httpx.post(
    MY_AGENT_ENDPOINT,
    json={"message": "rate_agent(agent_id='example_agent', rating=5, comment='很好用')"}
)
print("\n评分结果:")
print(response.json()["response"])
```

---

## 常见问题

### Q: 必须实现所有功能吗？

**A**: 不需要！最小化实现只需要：

- ✅ `/api/chat` 端点（必需）
- ✅ 会话隔离逻辑（强烈推荐）
- ✅ `/health` 端点（推荐）

### Q: 支持哪些编程语言？

**A**: 任何支持 HTTP 的语言都可以。只要能：

1. 接收 HTTP POST 请求
2. 解析 JSON
3. 返回 JSON 响应

### Q: 如何调试？

**A**:

1. 本地测试：`curl -X POST http://localhost:8080/api/chat -d '{"message":"test"}'`
2. 注册后通过 my_agent 测试
3. 查看日志排查问题

### Q: conversation_id 会冲突吗？

**A**: 不会。my_agent 为每个用户生成唯一的 conversation_id：

- DM: `dm_{user_seatalk_id}`
- 群聊: `{thread_id}`
- Agent 调用: `agent_relay_{conversation_id}`（继承上游）

### Q: 如何查看示例代码？

**A**: 查看 my_agent 项目的 `examples/` 文件夹：

- `session_isolation_example.py` — 完整示例
- `health_check_example.py` — 健康检查
- `auto_delegate_example.py` — 自动委派
- `rating_example.py` — 评分系统

---

## 接入检查清单

- [ ] 实现了 `/api/chat` POST 接口
- [ ] 返回格式为 `{"response": "...", "status": "success"}`
- [ ] 实现了会话隔离（基于 conversation_id）
- [ ] 实现了 `/health` GET 接口
- [ ] 网络连通性测试通过
- [ ] 已注册到 my_agent
- [ ] 测试调用成功

---

## 联系信息

**my_agent 地址**:

- Agent 端点: `http://10.169.72.91:5002/agent`
- Health Check: `http://10.169.72.91:5002/health`

**网络要求**:

- 你的 agent 必须能访问 `10.169.72.91:5002`
- my_agent 必须能访问你的 agent 端口

---

**开始开发吧！** 🚀

如有问题，请查看 `examples/` 文件夹中的完整示例代码。
