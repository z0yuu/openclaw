"""
OpenClaw ↔ my_agent 桥接服务

接收 my_agent 的 Simple 协议请求，转发给本地 OpenClaw Gateway 处理，返回结果。
/api/skills 端点实时从 OpenClaw 获取能力列表，新增技能后无需重启。
"""
from flask import Flask, request, jsonify
import httpx
import logging
import time
import threading

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger("openclaw-bridge")

MY_AGENT_HOST = "http://10.169.72.91:5002"
MY_AGENT_ENDPOINT = f"{MY_AGENT_HOST}/agent"
OPENCLAW_URL = "http://127.0.0.1:18789/v1/chat/completions"
OPENCLAW_TOKEN = "936ff5f30a0c0c20695edaf1994a92b8653feba0b78b85e5"

AGENT_ID = "zhaoyu_agent"
AGENT_NAME = "渣渣"
LOCAL_IP = "10.130.198.103"
PORT = 8080
ENDPOINT = f"http://{LOCAL_IP}:{PORT}/api/chat"

SKILLS_PROMPT = (
    "列出你所有可用的工具和技能，严格按以下 JSON 格式输出，不要输出其他内容：\n"
    '{"tools": {"工具名": "一句话描述", ...}, "skills": {"技能名": "一句话描述", ...}}'
)

_skills_cache = {"tools": {}, "skills": {}, "fetched_at": 0}
_skills_lock = threading.Lock()
CACHE_TTL = 300  # 5 分钟缓存


def _call_openclaw(message: str, timeout: int = 120) -> tuple:
    """调用 OpenClaw Gateway，返回 (content, elapsed_ms)。"""
    start = time.time()
    resp = httpx.post(
        OPENCLAW_URL,
        json={
            "model": "openclaw",
            "stream": False,
            "messages": [{"role": "user", "content": message}],
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENCLAW_TOKEN}",
        },
        timeout=timeout,
    )
    elapsed_ms = int((time.time() - start) * 1000)
    if resp.status_code != 200:
        raise RuntimeError(f"OpenClaw HTTP {resp.status_code}: {resp.text}")
    content = (
        resp.json().get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    return content, elapsed_ms


def _fetch_skills() -> dict:
    """从 OpenClaw 实时获取工具和技能列表，带缓存。"""
    now = time.time()
    with _skills_lock:
        if _skills_cache["fetched_at"] and now - _skills_cache["fetched_at"] < CACHE_TTL:
            return _skills_cache

    try:
        content, _ = _call_openclaw(SKILLS_PROMPT, timeout=30)
        # 从回复中提取 JSON（兼容 markdown code block 包裹）
        text = content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            text = text.rsplit("```", 1)[0]
        import json
        data = json.loads(text)
        with _skills_lock:
            _skills_cache["tools"] = data.get("tools", {})
            _skills_cache["skills"] = data.get("skills", {})
            _skills_cache["fetched_at"] = now
        logger.info(f"Refreshed skills: {len(_skills_cache['tools'])} tools, {len(_skills_cache['skills'])} skills")
    except Exception as e:
        logger.warning(f"Failed to fetch skills from OpenClaw: {e}")
    return _skills_cache


def _build_description() -> str:
    return "查询config配置, ab实验结果查询, google文档读写, 查询功能默认为prerank相关"


def _build_capabilities() -> str:
    info = _fetch_skills()
    return ",".join(list(info.get("tools", {}).keys()) + list(info.get("skills", {}).keys()))


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "")
        logger.info(f"Received from my_agent: {message[:200]}")

        content, elapsed_ms = _call_openclaw(message)
        logger.info(f"OpenClaw replied ({elapsed_ms}ms): {content[:200]}")

        return jsonify({
            "response": content,
            "status": "success",
            "metadata": {
                "agent_id": AGENT_ID,
                "processing_time_ms": elapsed_ms,
            },
        })
    except httpx.TimeoutException:
        logger.error("OpenClaw request timed out")
        return jsonify({"error": "OpenClaw timeout", "status": "error"}), 504
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({"error": str(e), "status": "error"}), 500


@app.route("/api/skills", methods=["GET"])
def skills():
    """实时从 OpenClaw 获取能力列表（5 分钟缓存）。"""
    force = request.args.get("refresh") == "1"
    if force:
        with _skills_lock:
            _skills_cache["fetched_at"] = 0

    info = _fetch_skills()
    return jsonify({
        "agent_id": AGENT_ID,
        "agent_name": AGENT_NAME,
        "description": _build_description(),
        "tools": info.get("tools", {}),
        "skills": info.get("skills", {}),
        "cached_at": info.get("fetched_at", 0),
        "usage": "POST /api/chat with {\"message\": \"你的任务描述\"}",
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "agent_id": AGENT_ID})


def register():
    description = _build_description()
    capabilities = _build_capabilities()
    payload = {
        "message": (
            f"register_agent("
            f"agent_id='{AGENT_ID}', "
            f"name='{AGENT_NAME}', "
            f"endpoint='{ENDPOINT}', "
            f"description='{description}', "
            f"capabilities='{capabilities}'"
            ")"
        )
    }
    try:
        resp = httpx.post(MY_AGENT_ENDPOINT, json=payload, timeout=30)
        if resp.status_code == 200:
            logger.info(f"Registered to my_agent: {resp.text}")
        else:
            logger.warning(f"Registration failed ({resp.status_code}): {resp.text}")
            logger.warning("Bridge is still running — retry registration later with: python3 register.py")
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        logger.warning("Bridge is still running — retry registration later with: python3 register.py")


if __name__ == "__main__":
    register()
    app.run(host="0.0.0.0", port=PORT)
