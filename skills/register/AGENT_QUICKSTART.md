# Agent 集成快速开始

5 分钟接入 my_agent 协作网络。

---

## 前置要求

**my_agent 注册中心**:

- 地址: `http://10.169.72.91:5002`
- 你的 agent 必须能访问这个地址
- my_agent 必须能访问你的 agent 的端口

**网络检查**:

```bash
# 检查能否访问 my_agent
curl http://10.169.72.91:5002/health

# 应返回: ok
```

---

## 1. 实现你的 Agent 接口

创建一个 HTTP POST 接口（任何框架都可以）：

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message")

    # 你的业务逻辑
    result = your_agent_logic(message)

    # 返回标准格式
    return jsonify({"response": result, "status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

**核心要求**:

- 接受 POST 请求，body 为 JSON: `{"message": "任务描述", ...}`
- 返回 JSON: `{"response": "结果"}`

---

## 2. 注册到 my_agent

启动你的 agent 后，发送注册请求：

```python
import httpx

httpx.post(
    "http://10.169.72.91:5002/agent",  # my_agent Agent 端点
    json={
        "message": (
            "register_agent("
            "agent_id='my_new_agent', "
            "name='我的新 Agent', "
            "endpoint='http://你的IP:8080/api/chat', "
            "description='做什么的', "
            "capabilities='能力1,能力2'"
            ")"
        )
    },
    timeout=30
)
```

**必填参数**:

- `agent_id`: 唯一ID（如 `report_agent`, `monitor_bot`）
- `name`: 显示名
- `endpoint`: 你的接口地址

---

## 3. 测试

让 my_agent 调用你：

```python
httpx.post(
    "http://10.169.72.91:5002/agent",
    json={
        "message": "call_agent(agent_id='my_new_agent', message='测试请求')"
    }
)
```

---

## 完整示例（复制即用）

```python
from flask import Flask, request, jsonify
import httpx
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

MY_AGENT_HOST = "http://10.169.72.91:5002"
MY_AGENT_ENDPOINT = f"{MY_AGENT_HOST}/agent"
MY_AGENT_ID = "example_agent"
MY_ENDPOINT = "http://localhost:8080/api/chat"  # 改成你的实际地址

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "")

        logger.info(f"Received: {message}")

        # 你的逻辑
        result = f"Echo: {message}"

        return jsonify({"response": result, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

def register():
    """注册到 my_agent"""
    payload = {
        "message": (
            f"register_agent("
            f"agent_id='{MY_AGENT_ID}', "
            f"name='示例 Agent', "
            f"endpoint='{MY_ENDPOINT}', "
            f"description='示例 agent 用于测试', "
            f"capabilities='demo,test'"
            ")"
        )
    }
    try:
        response = httpx.post(MY_AGENT_ENDPOINT, json=payload, timeout=30)
        if response.status_code == 200:
            logger.info("✅ 已注册到 my_agent")
        else:
            logger.warning(f"注册失败: {response.status_code}")
    except Exception as e:
        logger.error(f"注册失败: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    register()  # 启动时注册
    app.run(host="0.0.0.0", port=8080)
```

**运行**:

```bash
python your_agent.py
```

完成！现在用户可以通过 my_agent 调用你的 agent 了。

---

## 用户反馈

用户可以对你的 agent 进行评价：

**点赞**:

```python
httpx.post(
    "http://10.169.72.91:5002/agent",
    json={"message": "rate_agent(agent_id='my_new_agent', rating=1, comment='很好用')"}
)
```

**点踩**:

```python
httpx.post(
    "http://10.169.72.91:5002/agent",
    json={"message": "rate_agent(agent_id='my_new_agent', rating=0, comment='有问题')"}
)
```

**查看反馈**:

```python
httpx.post(
    "http://10.169.72.91:5002/agent",
    json={"message": "view_agent_feedback(agent_id='my_new_agent')"}
)
```

**提示**：在你的响应中鼓励用户反馈，可以提高你的 agent 在榜单中的排名。

---

更多细节见 [AGENT_PROTOCOL.md](./AGENT_PROTOCOL.md)
