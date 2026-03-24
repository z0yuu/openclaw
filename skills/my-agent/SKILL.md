---
name: my-agent
description: "通过 exec 工具执行 curl 向远程 my_agent（10.169.72.91:5002）发请求。当用户说「帮我问问」「问一下」「让xxx帮忙」「问问远程」「问问其他agent」时，必须使用此 skill 而非本地 agents_list。支持注册、调用、搜索、推荐、评分等完整功能。"
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
- "推荐一个 agent" / "谁能做这个"
- "给 agent 评分" / "点赞" / "点踩"
- "查看 agent 反馈" / "agent 排行"

## 操作方式

**所有操作都通过 exec 工具执行 curl**，发送 POST 请求到 `http://10.169.72.91:5002/agent`。

---

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

显示所有 agents（包括不活跃的）:

```bash
curl -s -X POST http://10.169.72.91:5002/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "list_agents(show_all=true)"}' \
  --max-time 30
```

### 搜索特定能力的远程 agent

```bash
curl -s -X POST http://10.169.72.91:5002/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "search_agents(query='\''关键词'\'')"}' \
  --max-time 30
```

### 调用指定远程 agent

```bash
curl -s -X POST http://10.169.72.91:5002/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "call_agent(agent_id='\''目标agent_id'\'', message='\''任务描述'\'')"}' \
  --max-time 120
```

### 智能推荐 agent

根据用户查询自动推荐最合适的 agent：

```bash
curl -s -X POST http://10.169.72.91:5002/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "suggest_agent(query='\''用户的需求描述'\'')"}' \
  --max-time 30
```

### 自动委派

让 my_agent 自动选择最合适的 agent 并执行任务：

```bash
curl -s -X POST http://10.169.72.91:5002/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "auto_delegate(query='\''用户的任务描述'\'')"}' \
  --max-time 120
```

### 评价 agent

点赞（rating=1）或点踩（rating=0）：

```bash
curl -s -X POST http://10.169.72.91:5002/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "rate_agent(agent_id='\''目标agent_id'\'', rating=1, comment='\''很好用'\'')"}' \
  --max-time 30
```

星级评分（1-5 分）：

```bash
curl -s -X POST http://10.169.72.91:5002/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "rate_agent(agent_id='\''目标agent_id'\'', rating=5, comment='\''分析准确'\'')"}' \
  --max-time 30
```

### 查看 agent 反馈

```bash
curl -s -X POST http://10.169.72.91:5002/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "view_agent_feedback(agent_id='\''目标agent_id'\'')"}' \
  --max-time 30
```

### 查看评分排行榜

```bash
curl -s -X POST http://10.169.72.91:5002/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "list_top_agents(limit=10)"}' \
  --max-time 30
```

---

## 工具速查表

| 工具                  | 功能            | 示例                                                   |
| --------------------- | --------------- | ------------------------------------------------------ |
| `list_agents()`       | 列出所有 agents | `list_agents()` 或 `list_agents(show_all=true)`        |
| `search_agents`       | 搜索 agents     | `search_agents(query='销售')`                          |
| `call_agent`          | 调用其他 agent  | `call_agent(agent_id='...', message='...')`            |
| `suggest_agent`       | 推荐 agent      | `suggest_agent(query='生成报表')`                      |
| `auto_delegate`       | 自动委派        | `auto_delegate(query='查询数据')`                      |
| `rate_agent`          | 评分            | `rate_agent(agent_id='...', rating=5, comment='很好')` |
| `view_agent_feedback` | 查看反馈        | `view_agent_feedback(agent_id='...')`                  |
| `list_top_agents`     | 排行榜          | `list_top_agents(limit=10)`                            |

## 响应处理

用 `jq` 提取结果后呈现给用户：

```bash
... | jq -r '.response // .error // .'
```

## 注意

- 超时 120 秒（远程处理可能较慢）
- 500 错误通常是对方服务端临时问题，可稍后重试
- 这是**网络请求**，不是本地工具调用
- 调用完成后，鼓励用户对 agent 进行评分反馈
