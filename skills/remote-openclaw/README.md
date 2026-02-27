# Remote OpenClaw 使用说明

通过 HTTP API 让另一台机器上的脚本调用本机 OpenClaw，或让本机 OpenClaw 调用远程实例。

---

## 一、本机 OpenClaw 配置（被调用方）

编辑 `~/.openclaw/openclaw.json`，确保开启相关端点和认证：

```json
{
  "gateway": {
    "bind": "lan",
    "auth": {
      "token": "你的密钥"
    },
    "http": {
      "endpoints": {
        "chatCompletions": { "enabled": true }
      }
    }
  }
}
```

如果需要使用 hook 模式（异步触发），额外添加：

```json
{
  "hooks": {
    "enabled": true,
    "token": "hook密钥"
  }
}
```

配置说明：

| 字段                                     | 说明                                                                                   |
| ---------------------------------------- | -------------------------------------------------------------------------------------- |
| `gateway.bind`                           | `"lan"` 允许局域网访问；`"loopback"` 仅本地（需 SSH 隧道）；`"tailnet"` 通过 Tailscale |
| `gateway.auth.token`                     | 用于 `/v1/chat/completions` 和 `/tools/invoke` 的 Bearer Token                         |
| `gateway.http.endpoints.chatCompletions` | 设为 `true` 启用 OpenAI 兼容接口                                                       |
| `hooks.enabled` + `hooks.token`          | 启用 `/hooks/agent` 端点及其独立 token                                                 |

修改配置后重启 Gateway：

```bash
openclaw restart
```

---

## 二、网络连通

根据网络环境选择一种方式：

### 方式 A：局域网直连

本机 `gateway.bind: "lan"` 即可。另一台机器用本机 IP 直接访问。

### 方式 B：SSH 隧道（推荐，最安全）

本机保持 `gateway.bind: "loopback"`，在另一台机器上建立隧道：

```bash
ssh -N -L 18789:127.0.0.1:18789 user@本机IP
```

隧道建立后，另一台机器用 `127.0.0.1:18789` 即可访问。

### 方式 C：Tailscale

本机配置 `gateway.tailscale.mode: "serve"` 或 `"funnel"`，通过 Tailscale 网络访问。

---

## 三、测试脚本使用方法

将 `test-remote-openclaw.sh` 复制到另一台机器，确保有 `curl` 和 `jq`。

### 基本用法

```bash
./test-remote-openclaw.sh [选项] "任务描述"
```

### 选项一览

| 选项                   | 说明                           | 默认值       |
| ---------------------- | ------------------------------ | ------------ |
| `-H, --host HOST`      | 远程 OpenClaw 地址             | `127.0.0.1`  |
| `-p, --port PORT`      | Gateway 端口                   | `18789`      |
| `-t, --token TOKEN`    | 认证 token                     | —            |
| `-m, --mode MODE`      | 模式: `chat` / `hook` / `tool` | `chat`       |
| `-s, --stream`         | 流式输出（仅 chat）            | 关闭         |
| `-T, --tool TOOL`      | 工具名（仅 tool 模式）         | —            |
| `-a, --tool-args JSON` | 工具参数（仅 tool 模式）       | `{}`         |
| `-n, --hook-name NAME` | Hook 名称（仅 hook 模式）      | `RemoteTask` |
| `--timeout SECS`       | 请求超时                       | `300`        |
| `--stdin`              | 从 stdin 读取任务              | —            |
| `--raw`                | 输出原始 JSON                  | —            |
| `-v, --verbose`        | 显示详细信息                   | —            |

也可以通过环境变量设置：

```bash
export OPENCLAW_REMOTE_HOST=192.168.1.100
export OPENCLAW_REMOTE_PORT=18789
export OPENCLAW_REMOTE_TOKEN=你的密钥
```

### 三种模式详解

#### 模式 1：chat（同步对话，推荐）

调用 `/v1/chat/completions`，发送任务后等待完整结果返回。

```bash
# 基本用法
./test-remote-openclaw.sh -H 192.168.1.100 -t mytoken "帮我用 Python 写一个快速排序"

# 流式输出（逐字显示）
./test-remote-openclaw.sh -H 192.168.1.100 -t mytoken -s "写一首关于编程的诗"

# 通过 SSH 隧道
./test-remote-openclaw.sh -t mytoken "帮我查看服务器状态"

# 传入长文本（如日志分析）
cat error.log | ./test-remote-openclaw.sh -H 192.168.1.100 -t mytoken --stdin

# 同时附加说明 + stdin
cat data.csv | ./test-remote-openclaw.sh -H 192.168.1.100 -t mytoken --stdin "分析这份数据，找出异常值"
```

#### 模式 2：hook（异步触发）

调用 `/hooks/agent`，立即返回 `runId`，任务在远程后台执行。结果通过远程 OpenClaw 的消息通道（如 Telegram、WebChat）投递。

```bash
./test-remote-openclaw.sh -H 192.168.1.100 -t hooktoken -m hook "生成每日工作报告"

# 自定义 hook 名称
./test-remote-openclaw.sh -H 192.168.1.100 -t hooktoken -m hook -n DailyReport "生成报告"
```

#### 模式 3：tool（调用指定工具）

调用 `/tools/invoke`，直接执行远程 OpenClaw 上的某个工具。

```bash
# 调用远程工具
./test-remote-openclaw.sh -H 192.168.1.100 -t mytoken -m tool -T web_search -a '{"query":"latest AI news"}'

# 调用 memory 工具
./test-remote-openclaw.sh -H 192.168.1.100 -t mytoken -m tool -T memory_search -a '{"query":"项目进度"}'
```

---

## 四、Skill 说明

`SKILL.md` 安装在本机 OpenClaw 的 `skills/remote-openclaw/` 目录下。当 agent 需要调用远程 OpenClaw 时，会参考此 skill 中的 curl 命令模板。

此 skill 让 agent 学会三种调用远程实例的方法：

1. **Chat Completions**（`/v1/chat/completions`）— 同步，最通用
2. **Hook Agent**（`/hooks/agent`）— 异步，适合后台任务
3. **Tool Invoke**（`/tools/invoke`）— 精确调用某个工具

---

## 五、故障排查

| 问题             | 排查方法                                                                                          |
| ---------------- | ------------------------------------------------------------------------------------------------- |
| 连接超时         | 检查防火墙、SSH 隧道是否建立、端口是否正确                                                        |
| 401 Unauthorized | 检查 token 是否正确，chat/tool 用 `gateway.auth.token`，hook 用 `hooks.token`                     |
| 404 Not Found    | chat 模式需确认 `gateway.http.endpoints.chatCompletions: true`；hook 需确认 `hooks.enabled: true` |
| 工具不可用       | 确认远程 OpenClaw 安装了对应的 skill 或插件，且工具策略允许使用                                   |

使用 `-v` 参数查看详细请求信息：

```bash
./test-remote-openclaw.sh -H 192.168.1.100 -t mytoken -v "测试连接"
```
