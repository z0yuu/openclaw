# my_agent 端点说明

本文档说明 `my_agent` 提供的不同端点及其用途。

---

## 端点总览

| 端点        | 用途            | 协议                   | 访问方式         |
| ----------- | --------------- | ---------------------- | ---------------- |
| `/callback` | SeaTalk Webhook | SeaTalk Event Callback | SeaTalk 平台调用 |
| `/agent`    | Agent 间通信    | Simple / Agent2Agent   | 其他 Agent 调用  |
| `/health`   | 健康检查        | HTTP GET               | 任何客户端       |

---

## 端点详情

### 1. `/callback` - SeaTalk Webhook

**用途**: 接收来自 SeaTalk 平台的事件回调

**协议**: SeaTalk Event Callback Protocol

**请求格式**:

```json
{
  "event_id": "...",
  "event_type": "message_from_bot_subscriber",
  "timestamp": 1709797200,
  "app_id": "...",
  "event": {
    "seatalk_id": "...",
    "employee_code": "...",
    "email": "...",
    "message": {...}
  }
}
```

**调用方**: SeaTalk 平台

**使用场景**:

- 用户向 SeaTalk Bot 发送消息
- 用户在群组中 @Bot
- 用户进入 Bot 聊天室
- 其他 SeaTalk 事件

**配置位置**: SeaTalk 开放平台 → 应用管理 → 事件订阅 → Webhook URL

**重要**: 此端点**仅供 SeaTalk 平台使用**，不应被其他 agent 调用。

---

### 2. `/agent` - Agent 间通信

**用途**: Agent 注册、查询和相互调用

**支持协议**:

- **Simple Protocol** (简单调用)
- **Agent2Agent Protocol** (标准协议，推荐)

**请求格式**:

#### Simple 格式

```json
{
  "message": "register_agent(...)",
  "param1": "value1"
}
```

#### Agent2Agent 格式

```json
{
  "sender": {
    "id": "your_agent_id",
    "name": "Your Agent"
  },
  "recipient": {
    "id": "my_agent",
    "name": "My Agent"
  },
  "action": "process",
  "payload": {
    "message": "..."
  },
  "request_id": "..."
}
```

**调用方**: 其他 Agent、外部系统

**使用场景**:

- Agent 注册到注册中心
- Agent 查询其他 agent 列表
- Agent 间相互调用
- Agent 评分反馈

**访问地址**: `http://10.169.72.91:5002/agent`

**示例**:

```python
import httpx

# 注册 agent
httpx.post(
    "http://10.169.72.91:5002/agent",
    json={"message": "register_agent(...)"}
)

# 调用 agent
httpx.post(
    "http://10.169.72.91:5002/agent",
    json={"message": "call_agent(agent_id='report_agent', message='生成报表')"}
)

# Agent2Agent 协议
httpx.post(
    "http://10.169.72.91:5002/agent",
    json={
        "sender": {"id": "your_agent", "name": "Your Agent"},
        "recipient": {"id": "my_agent", "name": "My Agent"},
        "action": "process",
        "payload": {"message": "生成报表"},
        "request_id": "..."
    }
)
```

---

### 3. `/health` - 健康检查

**用途**: 服务健康状态检查

**方法**: GET

**请求**: 无需参数

**响应**: `ok` (HTTP 200)

**调用方**: 任何客户端

**使用场景**:

- 监控系统检查服务状态
- 负载均衡器健康探测
- 部署验证

**示例**:

```bash
curl http://10.169.72.91:5002/health
# 响应: ok
```

---

## 快速参考

### Agent 开发者

如果你正在开发一个 agent 并想接入 `my_agent` 注册中心：

1. **实现你的 agent 接口** (建议使用 Agent2Agent 协议)
2. **注册到 my_agent**:
   ```python
   httpx.post(
       "http://10.169.72.91:5002/agent",  # 使用 /agent 端点
       json={"message": "register_agent(...)"}
   )
   ```

### SeaTalk 配置

如果你正在配置 SeaTalk Bot：

1. **在 SeaTalk 开放平台配置 Webhook URL**:

   ```
   http://10.169.72.91:5002/callback
   ```

2. **注意**: 不要将 `/agent` 端点配置为 Webhook URL

---

## 常见问题

**Q: 我应该使用哪个端点注册 agent？**  
A: 使用 `/agent` 端点。

**Q: `/callback` 端点可以用来调用 agent 吗？**  
A: 不建议。`/callback` 是为 SeaTalk Webhook 设计的，虽然技术上可行，但应该使用 `/agent` 端点。

**Q: Agent2Agent 协议必须使用 `/agent` 端点吗？**  
A: 是的，Agent2Agent 协议应该使用 `/agent` 端点。

**Q: 两个端点可以互换使用吗？**  
A: 不推荐。虽然代码层面可能兼容，但它们是为不同的使用场景设计的：

- `/callback`: SeaTalk 平台 → my_agent
- `/agent`: Agent ↔ my_agent ↔ Agent

**Q: 为什么要区分两个端点？**  
A:

- **职责清晰**: SeaTalk 事件处理 vs Agent 间通信
- **安全隔离**: 可以对两个端点配置不同的认证和限流策略
- **易于监控**: 分别监控 SeaTalk 流量和 Agent 流量
- **未来扩展**: 可以独立演进两个端点的功能

---

## 部署信息

- **服务地址**: `http://10.169.72.91:5002`
- **SeaTalk Webhook**: `http://10.169.72.91:5002/callback`
- **Agent 端点**: `http://10.169.72.91:5002/agent`
- **健康检查**: `http://10.169.72.91:5002/health`

---

**更新日期**: 2026-02-06  
**版本**: 1.0
