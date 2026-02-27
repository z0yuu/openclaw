---
name: my-agent
description: "通过 exec 工具执行 curl 向远程 my_agent（10.169.72.91:5002）发请求。当用户说「帮我问问」「问一下」「让xxx帮忙」「问问远程」「问问其他agent」时，必须使用此 skill 而非本地 agents_list。"
metadata:
  openclaw:
    emoji: "🤝"
    requires:
      bins: ["curl"]
---

# my_agent 远程协作

这是一个**外部服务**，不是本地 agent。必须通过 `exec` 工具执行 curl 命令来调用。

**不要使用本地的 agents_list 工具**，那只能看本地 agent。远程 agent 网络在 `10.169.72.91:5002`。

## 触发词

用户说以下内容时，使用此 skill：

- "帮我问问…" / "问一下…" / "问问远程…"
- "有哪些远程 agent" / "远程能做什么"
- "让xxx帮忙" / "调用xxx agent"

## 操作方式

**所有操作都通过 exec 工具执行 curl**，发送 POST 请求到 `http://10.169.72.91:5002/agent`。

### 直接提问（最常用）

```bash
curl -s -X POST http://10.169.72.91:5002/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "用户的问题内容"}' \
  --max-time 120
```

### 查看远程 agent 列表

```bash
curl -s -X POST http://10.169.72.91:5002/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "list_agents()"}' \
  --max-time 30
```

### 调用指定远程 agent

```bash
curl -s -X POST http://10.169.72.91:5002/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "call_agent(agent_id='\''目标agent_id'\'', message='\''任务描述'\'')"}' \
  --max-time 120
```

### 搜索特定能力的远程 agent

```bash
curl -s -X POST http://10.169.72.91:5002/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "search_agents('\''关键词'\'')"}' \
  --max-time 30
```

## 响应处理

用 `jq` 提取结果后呈现给用户：

```bash
... | jq -r '.response // .error // .'
```

## 注意

- 超时 120 秒（远程处理可能较慢）
- 500 错误通常是对方服务端临时问题，可稍后重试
- 这是**网络请求**，不是本地工具调用
