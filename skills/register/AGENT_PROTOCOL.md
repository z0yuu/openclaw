# Agent 协作协议文档

本文档说明如何开发一个 agent 并与 `my_agent` 集成，实现跨 agent 协作。

> **重要**: 请先阅读 [ENDPOINTS.md](./ENDPOINTS.md) 了解端点区别（Agent 端点 vs SeaTalk Webhook）

---

## 概述

### my_agent 注册中心

`my_agent` 是一个 **中心化的 agent 注册中心**，负责维护所有可用 agent 的名单和元数据。

**部署信息**:

- **服务地址**: `http://10.169.72.91:5002`
- **SeaTalk Webhook**: `http://10.169.72.91:5002/callback` (SeaTalk 专用)
- **Agent 端点**: `http://10.169.72.91:5002/agent` (Agent 间通信)
- **健康检查**: `http://10.169.72.91:5002/health`
- **数据存储**: `~/.my_agent_data/agents.json`

**网络要求**:

- 你的 agent 必须能访问 `10.169.72.91:5002`（注册时使用）
- `my_agent` 必须能访问你的 agent 的 `endpoint`（调用时使用）
- 如果在内网部署，确保防火墙规则允许双向通信

### 协作模型

所有 agent 都向 `my_agent` 注册，形成一个协作网络：

```
                    ┌─────────────────────────┐
                    │   my_agent 注册中心     │
                    │  10.169.72.91:5002      │
                    │                         │
                    │  功能:                  │
                    │  • 维护 agent 名单      │
                    │  • 路由 agent 调用      │
                    │  • 协议格式转换         │
                    └──────────┬──────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
    ┌─────────────────┐ ┌─────────────┐ ┌──────────────┐
    │  report_agent   │ │ monitor_bot │ │ other_agents │
    │  :8080          │ │ :9000       │ │ :xxxx        │
    │  (报表生成)     │ │ (监控告警)  │ │              │
    │  注册 ──────────┤ │ 注册 ───────┤ │ 注册 ────────┤
    │  (Simple)       │ │ (Agent2Agent)│ │ (任意格式)   │
    └─────────────────┘ └─────────────┘ └──────────────┘
              │                │                │
              └────────────────┼────────────────┘
                    互相发现和调用
                    (通过 my_agent)
```

**工作流程**:

1. 各个 agent 启动后，向 `10.169.72.91:5002` 注册
2. 用户通过 SeaTalk 向 my_agent 发送请求
3. my_agent 根据需求搜索合适的 agent 并调用
4. 被调用的 agent 处理任务并返回结果
5. my_agent 将结果返回给用户

### 核心功能

`my_agent` 提供了以下能力：

1. **注册自己** — 将自己的能力和接口信息注册到注册表
2. **被发现** — 被 `my_agent` 或其他 agent 通过搜索找到
3. **被调用** — 通过标准 HTTP 接口接收任务请求
4. **调用他人** — 通过注册表发现并调用其他 agent

---

## 1. Agent 注册

### 1.1 注册方式

向 `my_agent` 注册中心发送注册请求：

```http
POST http://10.169.72.91:5002/agent
Content-Type: application/json

{
  "message": "register_agent(agent_id='your_agent_id', name='Your Agent Name', endpoint='http://your-host:port/api/chat', description='What your agent does', capabilities='cap1,cap2,cap3')"
}
```

**重要提示**:

- ⚠️ 必须使用 Agent 端点：`http://10.169.72.91:5002/agent`
- ⚠️ **不要使用** `/callback`（那是 SeaTalk webhook 专用）
- ⚠️ `endpoint` 参数填写你的 agent 的地址（必须能被 `10.169.72.91` 访问到）
- ⚠️ 如果你的 agent 在内网，使用内网 IP（如 `http://10.x.x.x:port`）
- ⚠️ 如果在公网，使用公网 IP 或域名

**参数说明**：

- `agent_id` **(必填)**: 唯一标识符，建议用下划线风格（如 `report_agent`, `monitor_bot`, `data_analyzer`）
- `name` **(必填)**: 显示名称（如 "报表生成器", "监控告警", "数据分析器"）
- `endpoint` **(必填)**: 你的 agent 的 HTTP 接口 URL（必须可被 `my_agent` 访问）
- `description` (可选): 简短描述你的 agent 能做什么
- `capabilities` (可选): 逗号分隔的能力列表（如 `"chat,image,voice"`）
- `api_key` (可选): 如果你的接口需要认证，提供 API key

### 1.2 注册示例（Python）

**简单格式（Simple）**:

```python
import httpx

MY_AGENT_HOST = "http://10.169.72.91:5002"  # my_agent 的地址
MY_AGENT_ENDPOINT = f"{MY_AGENT_HOST}/agent"  # Agent 端点

def register_to_my_agent():
    """在启动时注册自己到 my_agent（简单格式）"""
    payload = {
        "message": (
            "register_agent("
            "agent_id='report_agent', "
            "name='报表生成器', "
            "endpoint='http://10.169.72.100:8080/api/chat', "
            "description='生成各类业务报表和数据分析', "
            "capabilities='report_generation,data_analysis,excel_export,chart', "
            "protocol='simple'"  # 可省略，默认就是 simple
            ")"
        )
    }

    response = httpx.post(f"{MY_AGENT_ENDPOINT}", json=payload, timeout=30)
    if response.status_code == 200:
        print("✅ 已注册到 my_agent (Simple 格式)")
    else:
        print(f"❌ 注册失败: {response.status_code} {response.text}")

# 在你的 agent 启动时调用
register_to_my_agent()
```

**Agent2Agent 格式**:

```python
def register_to_my_agent_agent2agent():
    """在启动时注册自己到 my_agent（Agent2Agent 格式）"""
    payload = {
        "message": (
            "register_agent("
            "agent_id='monitor_bot', "
            "name='监控告警机器人', "
            "endpoint='http://10.169.72.150:9000/api/chat', "
            "description='系统监控、异常告警、性能分析', "
            "capabilities='monitoring,alerting,performance_analysis,log_analysis', "
            "protocol='agent2agent'"  # 使用 Agent2Agent 格式
            ")"
        )
    }

    response = httpx.post(f"{MY_AGENT_ENDPOINT}", json=payload, timeout=30)
    if response.status_code == 200:
        print("✅ 已注册到 my_agent (Agent2Agent 格式)")
    else:
        print(f"❌ 注册失败: {response.status_code} {response.text}")

register_to_my_agent_agent2agent()
```

### 1.3 查看注册状态

注册成功后，可以通过以下方式验证：

```python
payload = {"message": "list_agents()"}
response = httpx.post(f"{MY_AGENT_ENDPOINT}", json=payload)
print(response.json())
```

---

## 2. Agent HTTP 接口规范

`my_agent` 支持两种协议格式：**简单格式（Simple）** 和 **Agent2Agent 格式（推荐）**。

### 2.1 协议选择

在注册时通过 `protocol` 参数指定：

```python
# 简单格式（适合快速集成）
register_agent(..., protocol="simple")

# Agent2Agent 格式（推荐，标准化）
register_agent(..., protocol="agent2agent")
```

**协议对比**:

| 特性       | Simple   | Agent2Agent         |
| ---------- | -------- | ------------------- |
| 实现复杂度 | ⭐ 简单  | ⭐⭐ 中等           |
| 消息结构   | 扁平     | 结构化              |
| 请求追踪   | ❌ 无    | ✅ request_id       |
| 发送者识别 | ❌ 无    | ✅ sender/recipient |
| 标准化程度 | 低       | 高（Google 标准）   |
| 适用场景   | 快速原型 | 生产环境            |

**选择建议**:

- 🚀 **快速原型、简单集成** → `Simple`
- ⭐ **生产环境、标准化协作** → `Agent2Agent` **(推荐)**

---

### 2.2 简单格式（Simple Protocol）

**适用场景**: 快速集成，最小化实现

**请求格式**:

```json
{
  "message": "用户的查询或任务描述",
  "temperature": 0.7,
  "max_tokens": 2000,
  ...其他可选参数
}
```

**响应格式**:

```json
{
  "response": "结果内容",
  "status": "success"
}
```

**核心字段**:

- `message` **(必填)**: 任务描述或用户查询
- 其他字段可自定义

---

### 2.3 Agent2Agent 格式

**适用场景**: 标准化的 agent 间通信，支持复杂的消息路由和上下文传递

**请求格式**:

```json
{
  "sender": {
    "id": "my_agent",
    "name": "My Agent",
    "type": "agent"
  },
  "recipient": {
    "id": "your_agent_id",
    "name": "Your Agent Name",
    "type": "agent"
  },
  "action": "process",
  "payload": {
    "message": "用户的查询或任务描述",
    "context": {
      "conversation_id": "conv_123",
      "user_id": "user_456"
    },
    "metadata": {
      "timestamp": 1707234567.89,
      "protocol_version": "1.0"
    }
  },
  "request_id": "req_1707234567890"
}
```

**字段说明**:

- `sender`: 发送方信息（由 my_agent 自动填充）
- `recipient`: 接收方信息（从注册信息获取）
- `action`: 操作类型（默认 "process"，可自定义如 "query", "execute" 等）
- `payload`: 实际的任务内容
  - `message`: 任务描述（必填）
  - `context`: 上下文信息（可选）
  - `metadata`: 元数据（可选）
- `request_id`: 请求唯一标识

**响应格式**:

```json
{
  "sender": {
    "id": "your_agent_id",
    "name": "Your Agent Name",
    "type": "agent"
  },
  "recipient": {
    "id": "my_agent",
    "name": "My Agent",
    "type": "agent"
  },
  "status": "success",
  "payload": {
    "message": "处理结果内容",
    "result": {
      "key": "value"
    },
    "metadata": {
      "timestamp": 1707234568.12,
      "processing_time_ms": 230
    }
  },
  "request_id": "req_1707234567890"
}
```

**状态码**:

- `success`: 成功
- `error`: 失败
- `pending`: 处理中（异步场景）

---

### 2.4 接口实现要求

**端点**: 你在注册时指定的 `endpoint`（如 `/api/chat`, `/chat`, `/invoke` 等）

**方法**: `POST`

**请求头**:

```http
Content-Type: application/json
Authorization: Bearer <your_api_key>  # 如果注册时提供了 api_key
```

### 2.2 响应格式

你的 agent 应返回 JSON 格式的响应，包含以下字段之一：

**标准响应**（推荐）:

```json
{
  "response": "这是我的回复内容",
  "status": "success",
  "metadata": {
    "tokens_used": 150,
    "duration_ms": 1234
  }
}
```

**其他兼容格式**（`my_agent` 会自动识别）:

```json
{
  "message": "回复内容"
}
```

```json
{
  "content": "回复内容"
}
```

```json
{
  "result": "回复内容"
}
```

**错误响应**:

```json
{
  "error": "错误描述",
  "status": "error",
  "code": "INVALID_REQUEST"
}
```

返回 HTTP 状态码应为：

- `200` — 成功
- `400` — 请求参数错误
- `401` — 认证失败（如果需要 api_key）
- `500` — 服务内部错误
- `503` — 服务暂时不可用

### 2.3 完整示例（Flask）

```python
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

# 你的 agent 逻辑
class MyAgent:
    def process(self, message: str, **params) -> str:
        # 实现你的 agent 逻辑
        return f"处理完成: {message}"

agent = MyAgent()

@app.route("/api/chat", methods=["POST"])
def chat():
    """接收来自 my_agent 或其他 agent 的请求"""
    try:
        data = request.get_json()

        # 1. 验证 API key（如果需要）
        api_key = request.headers.get("Authorization", "").replace("Bearer ", "")
        if api_key != "your_secret_key":  # 可选的认证
            return jsonify({"error": "Unauthorized"}), 401

        # 2. 提取参数
        message = data.get("message")
        if not message:
            return jsonify({"error": "message is required"}), 400

        temperature = data.get("temperature", 0.7)
        max_tokens = data.get("max_tokens", 2000)

        logger.info(f"Received request: {message[:100]}")

        # 3. 处理请求
        result = agent.process(message, temperature=temperature, max_tokens=max_tokens)

        # 4. 返回标准格式
        return jsonify({
            "response": result,
            "status": "success",
            "metadata": {
                "agent_id": "your_agent_id",
                "timestamp": time.time()
            }
        })

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

if __name__ == "__main__":
    # 启动前先注册到 my_agent
    register_to_my_agent()

    # 启动服务
    app.run(host="0.0.0.0", port=8080)
```

### 2.4 完整示例（Agent2Agent 格式 - FastAPI）

```python
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

# Agent2Agent 格式的数据模型
class AgentInfo(BaseModel):
    id: str
    name: str
    type: str = "agent"

class Agent2AgentRequest(BaseModel):
    sender: AgentInfo
    recipient: AgentInfo
    action: str = "process"
    payload: Dict[str, Any]
    request_id: str

class Agent2AgentResponse(BaseModel):
    sender: AgentInfo
    recipient: AgentInfo
    status: str
    payload: Dict[str, Any]
    request_id: str

@app.post("/api/chat", response_model=Agent2AgentResponse)
async def chat_agent2agent(
    request: Agent2AgentRequest,
    authorization: str = Header(None)
):
    """Agent2Agent 格式的接口"""
    try:
        # 1. 验证（可选）
        if authorization:
            api_key = authorization.replace("Bearer ", "")
            if api_key != "your_secret_key":
                raise HTTPException(status_code=401, detail="Unauthorized")

        # 2. 提取消息
        message = request.payload.get("message", "")
        context = request.payload.get("context", {})

        logger.info(f"[{request.request_id}] Received from {request.sender.id}: {message[:100]}")

        # 3. 处理任务
        start_time = time.time()
        result = await process_message(message, context)
        processing_time = (time.time() - start_time) * 1000

        # 4. 构建响应
        return Agent2AgentResponse(
            sender=AgentInfo(
                id="your_agent_id",
                name="Your Agent Name",
                type="agent"
            ),
            recipient=request.sender,  # 返回给发送方
            status="success",
            payload={
                "message": result,
                "metadata": {
                    "timestamp": time.time(),
                    "processing_time_ms": processing_time
                }
            },
            request_id=request.request_id
        )

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        # 错误响应也要符合 Agent2Agent 格式
        return Agent2AgentResponse(
            sender=AgentInfo(
                id="your_agent_id",
                name="Your Agent Name",
                type="agent"
            ),
            recipient=request.sender,
            status="error",
            payload={
                "error": str(e),
                "message": "Processing failed"
            },
            request_id=request.request_id
        )

async def process_message(message: str, context: dict) -> str:
    """你的业务逻辑"""
    return f"Processed: {message}"

@app.on_event("startup")
async def startup():
    """注册到 my_agent（Agent2Agent 格式）"""
    import httpx
    MY_AGENT_HOST = "http://10.169.72.91:5002"

    payload = {
        "message": (
            "register_agent("
            "agent_id='your_agent_id', "
            "name='Your Agent', "
            "endpoint='http://your-host:8080/api/chat', "
            "description='Your description', "
            "capabilities='cap1,cap2', "
            "protocol='agent2agent'"  # 指定使用 Agent2Agent 格式
            ")"
        )
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{MY_AGENT_ENDPOINT}", json=payload, timeout=30)
            if response.status_code == 200:
                logger.info("✅ Registered to my_agent (Agent2Agent protocol)")
            else:
                logger.warning(f"Registration failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to register: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### 2.5 完整示例（简单格式 - FastAPI）

```python
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import httpx
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str
    temperature: float = 0.7
    max_tokens: int = 2000

class ChatResponse(BaseModel):
    response: str
    status: str = "success"
    metadata: dict = {}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    authorization: str = Header(None)
):
    """接收来自 my_agent 或其他 agent 的请求"""
    try:
        # 1. 验证 API key（可选）
        if authorization:
            api_key = authorization.replace("Bearer ", "")
            if api_key != "your_secret_key":
                raise HTTPException(status_code=401, detail="Unauthorized")

        logger.info(f"Received: {request.message[:100]}")

        # 2. 处理请求（你的业务逻辑）
        result = await process_message(request.message, request.temperature)

        # 3. 返回响应
        return ChatResponse(
            response=result,
            metadata={
                "agent_id": "your_agent_id",
                "tokens": len(result.split())
            }
        )

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def process_message(message: str, temperature: float) -> str:
    """你的 agent 逻辑"""
    return f"Processed: {message}"

@app.on_event("startup")
async def startup():
    """启动时注册到 my_agent"""
    MY_AGENT_HOST = "http://10.169.72.91:5002"
    payload = {
        "message": (
            "register_agent("
            "agent_id='your_agent_id', "
            "name='Your Agent', "
            "endpoint='http://your-host:8080/api/chat', "
            "description='Your description', "
            "capabilities='cap1,cap2'"
            ")"
        )
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{MY_AGENT_ENDPOINT}", json=payload, timeout=30)
            if response.status_code == 200:
                logger.info("✅ Registered to my_agent")
            else:
                logger.warning(f"Registration failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to register: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

---

## 3. 调用其他 Agent

你的 agent 也可以通过 `my_agent` 的注册表发现并调用其他 agent。

### 3.1 查询可用 agents

```python
def list_available_agents():
    """查询所有可用的 agents"""
    payload = {"message": "list_agents(status='active')"}
    response = httpx.post(f"{MY_AGENT_ENDPOINT}", json=payload)
    return response.json()
```

### 3.2 搜索特定能力的 agent

```python
def find_agent_by_capability(capability: str):
    """搜索具有特定能力的 agent"""
    payload = {"message": f"search_agents('{capability}')"}
    response = httpx.post(f"{MY_AGENT_ENDPOINT}", json=payload)
    return response.json()
```

### 3.3 调用其他 agent

```python
def call_other_agent(agent_id: str, message: str, **params):
    """调用另一个 agent"""
    params_json = json.dumps(params) if params else ""
    payload = {
        "message": (
            f"call_agent("
            f"agent_id='{agent_id}', "
            f"message='{message}'"
            + (f", params='{params_json}'" if params_json else "")
            + ")"
        )
    }

    response = httpx.post(f"{MY_AGENT_ENDPOINT}", json=payload, timeout=60)
    return response.json()

# 示例：调用监控告警 agent
result = call_other_agent(
    agent_id="monitor_bot",
    message="检查 SearchServer 的异常日志",
    hours=24
)
```

---

## 4. 高级特性

### 4.1 流式响应（可选）

如果你的 agent 支持流式响应（SSE），可以在接口中实现：

```python
from fastapi.responses import StreamingResponse

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        # 你的流式生成逻辑
        for chunk in your_streaming_logic(request.message):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

注册时在 `capabilities` 中注明 `"streaming"`。

### 4.2 健康检查（推荐）

提供一个健康检查端点，方便监控：

```python
@app.get("/health")
def health():
    return {"status": "healthy", "agent_id": "your_agent_id"}
```

### 4.3 Webhook 通知（可选）

如果你的 agent 需要主动推送消息给 `my_agent` 或用户，可以：

```python
def notify_my_agent(message: str):
    """主动发送通知给 my_agent"""
    payload = {
        "message": f"send_dm(recipient='user_name', message='{message}')"
    }
    response = httpx.post(f"{MY_AGENT_ENDPOINT}", json=payload)
    return response.json()
```

### 4.4 用户反馈与评分

`my_agent` 提供了完整的反馈系统，帮助用户评价 agent 质量：

#### 反馈类型

1. **点赞/点踩** — 快速评价 agent 体验

   ```python
   # 点赞（rating=1）
   payload = {"message": "rate_agent(agent_id='report_agent', rating=1, comment='生成速度快')"}

   # 点踩（rating=0）
   payload = {"message": "rate_agent(agent_id='report_agent', rating=0, comment='数据有误')"}
   ```

2. **星级评分** — 更细致的评价（1-5 星）

   ```python
   payload = {"message": "rate_agent(agent_id='data_analyzer', rating=5, comment='分析准确，图表清晰')"}
   ```

3. **查看反馈** — 了解 agent 的历史表现

   ```python
   # 查看某个 agent 的评价
   payload = {"message": "view_agent_feedback(agent_id='monitor_bot', limit=10)"}

   # 查看评分最高的 agents
   payload = {"message": "list_top_agents(limit=10)"}
   ```

#### 自动统计

系统会自动跟踪：

- **平均评分** — 所有评价的平均值
- **成功率** — 成功调用数 / 总调用数
- **调用次数** — 总共被调用的次数
- **点赞/点踩比例** — 用户满意度

#### 对 Agent 开发者的建议

1. **监控评分** — 定期查看自己 agent 的反馈，及时优化
2. **响应差评** — 根据用户反馈的问题改进服务
3. **提高成功率** — 确保接口稳定，减少错误
4. **请求反馈** — 在返回结果时，可以提示用户"如果满意请点赞"

#### 示例：在响应中请求反馈

```python
@app.post("/api/chat")
async def chat(request: ChatRequest):
    result = process_request(request.message)

    # 在响应中附上反馈提示
    response_text = f"{result}\n\n如果这个结果有帮助，请点赞支持我们！"

    return {"response": response_text, "status": "success"}
```

---

## 5. 部署建议

### 5.1 网络可达性

**双向连通性要求**:

1. **你 → my_agent** (注册时):
   - 你的 agent 必须能访问 `http://10.169.72.91:5002`
   - 测试: `curl http://10.169.72.91:5002/health`
   - 如果连不通，检查网络配置/防火墙

2. **my_agent → 你** (调用时):
   - `10.169.72.91` 必须能访问你的 `endpoint`
   - 推荐使用内网 IP（如 `http://10.x.x.x:port`）
   - 确保你的端口对 `10.169.72.91` 开放

**网络环境示例**:

```
内网部署（推荐）:
  你的 agent: http://10.169.72.100:8080  ✅
  my_agent:    http://10.169.72.91:5002   ✅
  → 双向直连，延迟低

公网部署:
  你的 agent: http://your-domain.com:8080  ⚠️
  my_agent:    http://10.169.72.91:5002     ✅
  → 需要 my_agent 能访问公网，延迟较高

localhost (错误):
  你的 agent: http://localhost:8080  ❌
  → my_agent 无法访问，注册会失败
```

**端口检查清单**:

- [ ] 我的 agent 能 curl `http://10.169.72.91:5002/health`
- [ ] `10.169.72.91` 能 curl `http://我的IP:我的端口/health`
- [ ] 防火墙规则已配置（如果需要）

### 5.2 容错处理

- 实现超时机制（`my_agent` 默认超时 30 秒）
- 对于长时间任务，考虑异步处理 + webhook 回调
- 添加重试逻辑（网络抖动）

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def register_to_my_agent():
    # 注册逻辑
    pass
```

### 5.3 日志和监控

- 记录所有请求和响应（脱敏后）
- 监控接口的响应时间和成功率
- 定期检查在 `my_agent` 中的注册状态

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
```

---

## 6. 完整工作流示例

### 场景：用户通过 my_agent 调用报表生成 agent

**步骤 1**: `report_agent` 启动并注册

```python
# report_agent 启动时
register_to_my_agent()  # 注册 endpoint: http://10.169.72.100:8080/api/chat
```

**步骤 2**: 用户向 `my_agent` 发送请求

```
用户 → my_agent (SeaTalk): "生成昨天的实验流量报表"
```

**步骤 3**: `my_agent` 搜索并调用 `report_agent`

```python
# my_agent 内部执行
search_agents("report")  # 找到 report_agent
call_agent(
    agent_id="report_agent",
    message="生成昨天的实验流量报表",
    params={"date": "2026-02-05", "format": "excel"}
)
```

**步骤 4**: `report_agent` 接收请求并处理

```python
# report_agent 的 /api/chat 接收到请求
POST http://10.169.72.100:8080/api/chat
Body: {
    "message": "生成昨天的实验流量报表",
    "date": "2026-02-05",
    "format": "excel"
}

# report_agent 处理并返回
{
    "response": "✅ 报表已生成：experiment_traffic_20260205.xlsx",
    "status": "success",
    "file_path": "/tmp/experiment_traffic_20260205.xlsx"
}
```

**步骤 5**: `my_agent` 收到响应并告知用户

```
my_agent → 用户 (SeaTalk): "报表已生成，文件：experiment_traffic_20260205.xlsx"
```

---

## 7. 故障排查

### 7.1 注册失败

**症状**: 调用 `register_agent` 后没有在 `list_agents` 中看到

**检查**:

- 确认 `my_agent` 正在运行
- 检查 `my_agent` 的日志（`serve.py` 的输出）
- 确认请求格式正确（JSON 格式，字段名准确）

### 7.2 调用超时

**症状**: `call_agent` 报错 "Request timed out"

**解决**:

- 确认你的 agent 接口响应时间 < 30 秒
- 优化处理逻辑或改为异步模式
- 在注册时添加说明："长任务请使用 webhook 回调"

### 7.3 认证失败

**症状**: 返回 401 Unauthorized

**检查**:

- 确认注册时的 `api_key` 与你的接口认证逻辑一致
- 检查 `Authorization` header 是否正确解析

### 7.4 无法访问 endpoint

**症状**: `call_agent` 报错 "Connection refused"

**检查**:

- 确认你的 agent 正在运行
- 确认端口号正确且对外开放
- 测试网络连通性：`curl http://your-host:port/health`

---

## 8. API 参考速查

### 8.1 my_agent 提供的工具

| 工具                  | 用途                  | 参数                                                                     |
| --------------------- | --------------------- | ------------------------------------------------------------------------ |
| `register_agent`      | 注册 agent            | `agent_id`, `name`, `endpoint`, `description`, `capabilities`, `api_key` |
| `list_agents`         | 列出 agents（含评分） | `status` (可选: `"active"` / `"inactive"`)                               |
| `search_agents`       | 搜索 agents           | `query`                                                                  |
| `call_agent`          | 调用 agent            | `agent_id`, `message`, `params` (可选), `timeout` (可选)                 |
| `unregister_agent`    | 取消注册              | `agent_id`                                                               |
| `update_agent_status` | 更新状态              | `agent_id`, `status` (`"active"` / `"inactive"`)                         |
| `rate_agent`          | 评价 agent            | `agent_id`, `rating` (0=点踩/1=点赞), `comment` (可选)                   |
| `view_agent_feedback` | 查看反馈              | `agent_id`, `limit` (可选, 默认 10)                                      |
| `list_top_agents`     | 查看评分榜单          | `limit` (可选, 默认 10)                                                  |

### 8.2 标准请求/响应格式

**请求**:

```json
{
  "message": "任务描述",
  "param1": "value1",
  "param2": "value2"
}
```

**成功响应**:

```json
{
  "response": "结果内容",
  "status": "success"
}
```

**错误响应**:

```json
{
  "error": "错误描述",
  "status": "error"
}
```

---

## 9. my_agent 部署信息

### 9.1 服务地址

| 项目             | 地址 / 路径                           |
| ---------------- | ------------------------------------- |
| **注册中心地址** | `http://10.169.72.91:5002`            |
| **注册接口**     | `POST http://10.169.72.91:5002/agent` |
| **健康检查**     | `GET http://10.169.72.91:5002/health` |
| **数据存储**     | `~/.my_agent_data/agents.json`        |
| **日志输出**     | stdout（启动时可见）                  |
| **运行环境**     | Python 3.12 + Sanic                   |

### 9.2 网络配置

**my_agent 所在主机**: `10.169.72.91`

- 可访问内网所有机器（`10.x.x.x` 网段）
- 出站端口：无限制（可访问任意端口）
- 入站端口：`5002` 对内网开放

**你的 agent 要求**:

- ✅ 能访问 `10.169.72.91:5002`（注册时需要）
- ✅ 开放你自己的端口给 `10.169.72.91`（被调用时需要）
- ✅ 使用内网 IP 作为 `endpoint`（推荐，延迟低）

### 9.3 注册数据持久化

注册信息保存在 `~/.my_agent_data/agents.json`：

- 自动持久化，服务重启后不丢失
- 数据格式：JSON
- 可通过 `list_agents` 工具查看当前注册状态

### 9.4 监控与维护

**健康检查**:

```bash
curl http://10.169.72.91:5002/health
# 返回 "ok" 表示服务正常
```

**查看已注册 agents**:

```bash
curl -X POST http://10.169.72.91:5002/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "list_agents()"}'
```

**日志查看**:

- my_agent 的日志在启动终端可见
- 包含所有注册、调用的详细信息
- 格式：`YYYY-MM-DD HH:MM:SS [模块名] 级别: 消息`

### 9.5 故障联系

如有问题：

1. 检查网络连通性（`curl http://10.169.72.91:5002/health`）
2. 查看 my_agent 日志（请联系管理员获取）
3. 确认你的 agent 端口开放且正常运行
4. 联系管理员：`yifan.shi@shopee.com`

---

## 10. 快速参考

### 核心信息速查

```python
# my_agent 注册中心地址
MY_AGENT_HOST = "http://10.169.72.91:5002"
MY_AGENT_ENDPOINT = f"{MY_AGENT_HOST}/agent"

# 注册模板
REGISTER_TEMPLATE = """
register_agent(
    agent_id='your_id',
    name='Your Name',
    endpoint='http://your-ip:your-port/api/chat',
    description='Your description',
    capabilities='cap1,cap2',
    protocol='simple'  # or 'agent2agent'
)
"""

# 快速注册函数
import httpx

def register():
    response = httpx.post(
        MY_AGENT_ENDPOINT,
        json={"message": REGISTER_TEMPLATE},
        timeout=30
    )
    print(response.json())

# 验证注册
def verify():
    response = httpx.post(
        MY_AGENT_ENDPOINT,
        json={"message": "list_agents()"},
        timeout=30
    )
    print(response.json())

# 评价 agent（点赞）
def rate_thumbs_up(agent_id: str, comment: str = ""):
    response = httpx.post(
        MY_AGENT_ENDPOINT,
        json={"message": f"rate_agent(agent_id='{agent_id}', rating=1, comment='{comment}')"},
        timeout=30
    )
    print(response.json())

# 查看反馈
def view_feedback(agent_id: str):
    response = httpx.post(
        MY_AGENT_ENDPOINT,
        json={"message": f"view_agent_feedback(agent_id='{agent_id}')"},
        timeout=30
    )
    print(response.json())
```

---

**版本**: v1.2  
**更新日期**: 2026-02-06  
**注册中心**: http://10.169.72.91:5002
