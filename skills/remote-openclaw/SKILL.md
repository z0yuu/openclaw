---
name: remote-openclaw
description: "Send tasks to a remote OpenClaw instance and receive results via its HTTP API (OpenAI-compatible chat completions, hooks, or tool invoke)."
metadata: { "openclaw": { "emoji": "🔗", "requires": { "bins": ["curl"] } } }
---

# Remote OpenClaw

Send a task to another OpenClaw instance running on a different machine and get the result back. The remote instance will use its own skills and tools to complete the task.

## Prerequisites

The remote OpenClaw Gateway must be network-reachable. Common setups:

- **SSH tunnel**: `ssh -N -L 18789:127.0.0.1:18789 user@remote-host`
- **Tailscale**: remote Gateway uses `gateway.tailscale.mode: "serve"` or `"funnel"`
- **LAN / VPN**: remote Gateway uses `gateway.bind: "lan"` or `"custom"`

The remote Gateway must have the relevant API endpoint enabled:

- `/v1/chat/completions` — needs `gateway.http.endpoints.chatCompletions: true`
- `/hooks/agent` — needs `hooks.enabled: true` with a `hooks.token`
- `/tools/invoke` — always available when auth is configured

## Method 1: Chat Completions (recommended, synchronous)

Best for sending a free-form task and waiting for the full response.

```bash
curl -s -X POST "http://REMOTE_HOST:18789/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer REMOTE_TOKEN" \
  -d '{
    "model": "openclaw",
    "stream": false,
    "messages": [
      {"role": "user", "content": "YOUR TASK DESCRIPTION HERE"}
    ]
  }' | jq -r '.choices[0].message.content'
```

With streaming:

```bash
curl -s -N -X POST "http://REMOTE_HOST:18789/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer REMOTE_TOKEN" \
  -d '{
    "model": "openclaw",
    "stream": true,
    "messages": [
      {"role": "user", "content": "YOUR TASK DESCRIPTION HERE"}
    ]
  }'
```

Replace `REMOTE_HOST` with the IP/hostname, `18789` with the remote gateway port, and `REMOTE_TOKEN` with the remote auth token or password.

## Method 2: Hook Agent (asynchronous, fire-and-forget)

Best for triggering a background task on the remote instance. Returns immediately with a `runId`.

```bash
curl -s -X POST "http://REMOTE_HOST:18789/hooks/agent" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer HOOK_TOKEN" \
  -d '{
    "message": "YOUR TASK DESCRIPTION HERE",
    "name": "RemoteTask"
  }' | jq .
```

The hook token is configured separately in `hooks.token` on the remote instance.

## Method 3: Tool Invoke (call a specific remote tool)

Best when you know exactly which tool to call on the remote instance.

```bash
curl -s -X POST "http://REMOTE_HOST:18789/tools/invoke" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer REMOTE_TOKEN" \
  -d '{
    "tool": "TOOL_NAME",
    "args": {"key": "value"}
  }' | jq .
```

## Tips

- When using SSH tunnel, `REMOTE_HOST` is `127.0.0.1` (the tunnel maps local port to remote).
- Use `jq` to parse JSON responses; use `jq -r '.choices[0].message.content'` for plain text from chat completions.
- For large tasks, increase curl timeout: `curl --max-time 300 ...`
- Multi-turn conversation: include previous messages in the `messages` array for chat completions.
- To target a specific agent on the remote instance, set the `model` field to the agent id or use the `agentId` field in hooks.
