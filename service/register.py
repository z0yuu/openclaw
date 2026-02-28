"""
独立注册脚本 - 向 my_agent 注册 openclaw_agent（含完整能力描述）
用法: python3 register.py
"""
import httpx
from agent_server import (
    AGENT_ID, AGENT_NAME, ENDPOINT, MY_AGENT_ENDPOINT,
    _build_description, _build_capabilities,
)

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

print(f"Registering {AGENT_ID} to {MY_AGENT_ENDPOINT} ...")
print(f"  Endpoint: {ENDPOINT}")
print(f"  Capabilities ({len(capabilities.split(','))} items): {capabilities[:120]}...")

try:
    resp = httpx.post(MY_AGENT_ENDPOINT, json=payload, timeout=30)
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.text[:300]}")
except Exception as e:
    print(f"  Failed: {e}")

print("\nVerifying (list_agents)...")
try:
    resp = httpx.post(MY_AGENT_ENDPOINT, json={"message": "list_agents()"}, timeout=30)
    print(f"  {resp.text[:500]}")
except Exception as e:
    print(f"  Failed: {e}")
