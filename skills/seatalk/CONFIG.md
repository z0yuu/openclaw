# SeaTalk & AB Platform 凭据配置说明

## 一、App ID / Secret 写到哪里

推荐**只写一份**，放在 OpenClaw 的全局环境里，这样 Gateway 和本机跑的脚本都能读到。

### 方式 1：`~/.openclaw/.env`（推荐）

在**运行 OpenClaw Gateway 的那台机器**上创建或编辑：

```bash
# 路径（Linux/macOS）
~/.openclaw/.env
# 即 $OPENCLAW_STATE_DIR/.env，默认是 /root/.openclaw/.env 或 $HOME/.openclaw/.env
```

内容示例：

```bash
# SeaTalk（发消息用）
SEATALK_APP_ID=你的AppID
SEATALK_APP_SECRET=你的AppSecret
# 若要在 SeaTalk 后台配置「事件回调」并校验签名，再填：
# SEATALK_SIGNING_SECRET=你的SigningSecret

# AB 平台
AB_API_TOKEN=你的AB平台Token
AB_PROJECT_ID=27
# 可选：AB_API_ENV=live|staging|test
```

保存后，**重启 Gateway**（若正在跑），再执行 skill 脚本即可读到这些变量。

### 方式 2：配置文件里的 `env` 块

在 `~/.openclaw/openclaw.json` 里用 `env` 写（敏感信息注意文件权限）：

```json5
{
  env: {
    SEATALK_APP_ID: "你的AppID",
    SEATALK_APP_SECRET: "你的AppSecret",
    AB_API_TOKEN: "你的AB平台Token",
    AB_PROJECT_ID: "27",
  },
}
```

同样，改完后需重启 Gateway。

### 方式 3：当前终端临时使用

仅当前 shell 有效，适合临时测试：

```bash
export SEATALK_APP_ID=xxx
export SEATALK_APP_SECRET=xxx
python skills/seatalk/scripts/send_message.py single "E123" "test"
```

---

## 二、SeaTalk「回调链接」是什么、填哪里

SeaTalk 开放平台里要填的「事件回调 URL」，是**你的一台公网可访问的服务器**上，用来**接收 SeaTalk 推送事件**的接口地址。

- **作用**：用户给 Bot 发消息、新关注等事件时，SeaTalk 会向这个 URL 发 HTTP POST，你的服务收到后可以处理并回复。
- **谁提供这个链接**：必须是你自己部署的、带 HTTPS 的接口，例如：
  - 你跑的 **LLM_minecraft** 服务（FastAPI），或
  - 任何实现了 [SeaTalk 事件回调](https://open.seatalk.io/docs) 的服务。

### 在 LLM_minecraft 项目里

LLM_minecraft 里已经实现了 SeaTalk 回调路由，路径是：

```text
POST /api/webhook/seatalk
```

所以「回调链接」应填你部署 LLM_minecraft 后的**完整 URL**，例如：

```text
https://你的域名或IP:8000/api/webhook/seatalk
```

- 若用 `uvicorn app.main:app --host 0.0.0.0 --port 8000`，且域名为 `bot.yourcompany.com`，则填：  
  `https://bot.yourcompany.com:8000/api/webhook/seatalk`
- 若前面有 Nginx 反代 8000 且已配 HTTPS，可填：  
  `https://bot.yourcompany.com/api/webhook/seatalk`

**注意**：SeaTalk 要求回调地址必须是 **HTTPS**（生产环境），且需能从公网访问。

### 在 OpenClaw Gateway 里

OpenClaw Gateway 已实现与 LLM_minecraft 一致的 **SeaTalk 事件回调**，路径为：

```text
POST /api/webhook/seatalk
```

因此「事件回调 URL」可以填 **Gateway 对外暴露的 base URL + 该路径**，例如：

```text
http(s)://你的主机:18789/api/webhook/seatalk
```

- Gateway 默认端口为 **18789**；若通过 Nginx 反代并配 HTTPS，可填：  
  `https://你的域名/api/webhook/seatalk`
- 需在 `~/.openclaw/.env`（或 Gateway 能读到的环境）中配置：
  - `SEATALK_APP_ID` / `SEATALK_APP_SECRET`（发回复用）
  - `SEATALK_SIGNING_SECRET`（回调签名校验，建议配置）

用户给 Bot 发单聊消息时，Gateway 会先快速返回 200，再在后台用默认 Agent 处理该消息，并把回复通过 SeaTalk 单聊发回用户。

- **只发消息、不接消息**：可不填「事件回调 URL」，只配好 `SEATALK_APP_ID` / `SEATALK_APP_SECRET` 即可。
- **要接用户消息并自动回复**：在 SeaTalk 后台把「事件回调 URL」填成上述 Gateway 地址，或继续使用 LLM_minecraft 等其它服务的回调地址。

---

## 三、小结

| 内容                                 | 写到哪里                                       | 说明                                                                                                                                                                            |
| ------------------------------------ | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SeaTalk App ID / Secret、AB Token 等 | `~/.openclaw/.env` 或 `openclaw.json` 的 `env` | 推荐 `.env`，改完重启 Gateway                                                                                                                                                   |
| SeaTalk 事件回调 URL                 | SeaTalk 开放平台后台「事件回调」配置项         | 填你部署的、能接收 POST 的地址，例如 OpenClaw Gateway 的 `http(s)://主机:18789/api/webhook/seatalk` 或 LLM_minecraft 的 `https://域名:8000/api/webhook/seatalk`；仅发消息可不填 |
