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

因此「事件回调 URL」可以填 **Gateway 对外暴露的 base URL + 以下任一路径**：

- `http(s)://你的主机:18789/api/webhook/seatalk`（推荐）
- `http(s)://你的主机:18789/webhook/seatalk`

例如：`https://10.130.198.103:18789/webhook/seatalk`

- Gateway 默认端口为 **18789**；若通过 Nginx 反代并配 HTTPS，可填：  
  `https://你的域名/api/webhook/seatalk`
- 需在 `~/.openclaw/.env`（或 Gateway 能读到的环境）中配置：
  - `SEATALK_APP_ID` / `SEATALK_APP_SECRET`（发回复用）
  - `SEATALK_SIGNING_SECRET`（回调签名校验，建议配置）

用户给 Bot 发单聊消息时，Gateway 会先快速返回 200，再在后台用默认 Agent 处理该消息，并把回复通过 SeaTalk 单聊发回用户。

- **只发消息、不接消息**：可不填「事件回调 URL」，只配好 `SEATALK_APP_ID` / `SEATALK_APP_SECRET` 即可。
- **要接用户消息并自动回复**：在 SeaTalk 后台把「事件回调 URL」填成上述 Gateway 地址，或继续使用 LLM_minecraft 等其它服务的回调地址。

### 验证不通过时看哪个日志文件

SeaTalk 回调的日志会写入 **OpenClaw 的日志文件**（与 Gateway 其它日志同一文件），subsystem 为 `seatalk`。

**默认日志文件路径**（未在配置里改过 `logging.file` 时）：

- 若存在 **`~/.openclaw`** 目录：**`~/.openclaw/logs/openclaw-YYYY-MM-DD.log`**（例如 `~/.openclaw/logs/openclaw-2026-02-13.log`）
- 否则：**`/tmp/openclaw/openclaw-YYYY-MM-DD.log`**

- 若在 `~/.openclaw/openclaw.json` 里配置了 `logging.file`，则用该路径（如 `"logging": { "file": "/root/.openclaw/gateway.log" }`）。
- Gateway 启动时会在控制台打一行 `log file: <路径>`，那就是当前实际写入的**具体日志文件**。

**若之前是在 `~/.openclaw/gateway.log` 看错误日志，现在没有内容了：**

- `gateway.log` 通常是**进程 stdout 重定向**（例如 `nohup ... >> gateway.log 2>&1`）。若启动方式改了（不再重定向到该文件），就不会有输出。
- 应用内**结构化日志**默认在 `~/.openclaw/logs/openclaw-YYYY-MM-DD.log` 或 `/tmp/openclaw/` 下。若希望**所有日志固定写到** `~/.openclaw/gateway.log`，在 `openclaw.json` 里添加：
  ```json
  "logging": { "file": "/root/.openclaw/gateway.log" }
  ```
  重启 Gateway 后即可在该文件看到所有日志（含 SeaTalk）。路径请按你的实际 home 改（如 `/root/.openclaw/gateway.log`）。

查看 SeaTalk 相关行（JSONL，每行一条）：

```bash
grep seatalk ~/.openclaw/logs/openclaw-2026-02-13.log
# 或你配置的 logging.file 路径，例如：grep seatalk ~/.openclaw/gateway.log
```

日志内容示例（`message` 或控制台里能看到）：

- `SeaTalk webhook request: POST /api/webhook/seatalk` — 请求已进入回调
- `SeaTalk webhook event_type=event_verification` — 收到 URL 验证请求
- `SeaTalk event_verification: returning seatalk_challenge (length=...)` — 已正确返回 challenge
- `SeaTalk webhook signature verification failed` — 签名校验失败（检查 `SEATALK_SIGNING_SECRET` 或是否被代理改 body）
- `SeaTalk webhook invalid JSON` / `body read error` — 请求体异常

若验证不通过且该日志文件里**没有任何 `seatalk` 记录**，说明 **HTTP 请求没有进到当前这台 Gateway 进程**，可依次排查：

1. **先确认进程和端口**  
   在跑 Gateway 的机器上执行：

   ```bash
   curl -s http://127.0.0.1:18789/webhook/seatalk
   ```

   若返回 JSON（如 `{"message":"SeaTalk webhook endpoint; use POST for event callback.",...}`），说明当前进程已注册 SeaTalk 回调且 18789 是本进程在监听。

2. **再确认外网/SeaTalk 能访问**  
   若填的是内网 IP（如 `https://10.130.198.103:18789/webhook/seatalk`），SeaTalk 服务器必须能访问该 IP（同一内网或已做端口转发）。在本机或同网段机器上：

   ```bash
   curl -sk https://10.130.198.103:18789/webhook/seatalk
   ```

   - 若这里都收不到响应，说明请求没到 18789（防火墙、Nginx 未转发、或实际监听的是别的进程）。
   - 若前面 127.0.0.1 有响应而 10.130.198.103 无响应，多半是只监听了 127.0.0.1，需让 Gateway 监听 `0.0.0.0` 或对应网卡 IP。

3. **Nginx 反代**  
   若 18789 前有 Nginx，需保留路径再转发，例如：
   ```nginx
   location /webhook/seatalk {
     proxy_pass http://127.0.0.1:18789;   # 不要写成 http://127.0.0.1:18789/
   }
   ```
   否则路径可能被改写，Gateway 收不到 `/webhook/seatalk`，日志里也不会有 seatalk。

---

### 本机有响应、外部没日志（只监听本机）

若**本机** `curl http://127.0.0.1:18789/webhook/seatalk` 有返回，但 **SeaTalk/外网** 访问 `https://10.130.198.103:18789/webhook/seatalk` 没有任何 seatalk 日志，说明 Gateway 只监听了 **127.0.0.1**，没有监听外网网卡，外部请求根本到不了进程。

**处理：让 Gateway 监听所有网卡（0.0.0.0）**

1. **配置里改**（推荐）  
   编辑 `~/.openclaw/openclaw.json`，在 `gateway` 里加上 `bind` 和认证（监听非本机时必须配置认证）：

   ```json
   {
     "gateway": {
       "bind": "lan",
       "auth": { "token": "你的网关 token" }
     }
   }
   ```

   - `bind: "lan"` 表示监听 `0.0.0.0`，外网可访问。
   - 必须设置 `gateway.auth.token` 或 `gateway.auth.password`（或环境变量 `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`），否则出于安全考虑 Gateway 会拒绝以非本机地址启动。

2. **命令行临时指定**

   ```bash
   openclaw gateway --port 18789 --bind lan
   ```

   同样需要已在配置或环境变量里配好 `gateway.auth.token` / password。

3. **重启 Gateway**  
   改完配置或参数后重启 Gateway，再在 SeaTalk 里重试验证；从外网或本机用 `curl -sk https://10.130.198.103:18789/webhook/seatalk` 应能拿到 JSON 且日志里出现 seatalk。

---

### 外部发消息也访问不通（本机通、外网/同网段不通）

Gateway 已配 `bind: "lan"` 且进程在监听 `0.0.0.0:18789` 时，若**本机** `curl http://127.0.0.1:18789/webhook/seatalk` 能返回 200，但**其他机器或 SeaTalk** 访问 `http(s)://10.130.198.103:18789/webhook/seatalk` 不通，可按下面排查。

**1. 先确认是 HTTP 还是 HTTPS**

- 当前 Gateway 默认**只提供 HTTP**（未配 `gateway.tls` 时）。
- 若在 SeaTalk 里填的是 **`https://`**，而 18789 上没做 TLS（没 Nginx 反代、没开 Gateway TLS），则外网用 HTTPS 连会握手失败，表现为「访问不通」。
- **处理**（二选一）：
  - 在 SeaTalk 里改用 **`http://10.130.198.103:18789/webhook/seatalk`**（仅内网可这样用），或
  - 在前面加一层 **Nginx**：对外 443/HTTPS，反代到 `http://127.0.0.1:18789`，SeaTalk 填 `https://你的域名/webhook/seatalk`。

**2. 放通防火墙 18789**

在**跑 Gateway 的那台机**上执行（按你实际用的防火墙选一个）：

- **firewalld**：
  ```bash
  sudo firewall-cmd --permanent --add-port=18789/tcp
  sudo firewall-cmd --reload
  ```
- **iptables**（放行入站 18789）：
  ```bash
  sudo iptables -I INPUT -p tcp --dport 18789 -j ACCEPT
  ```
- **云主机**：在安全组/防火墙规则里放行**入站 TCP 18789**（源可以是 0.0.0.0/0 或 SeaTalk 出口 IP，视安全要求而定）。

**3. 从同网段另一台机器测**

在能和 10.130.198.103 互通的另一台机器上执行：

```bash
# 若 Gateway 是 HTTP（未配 TLS）
curl -s -o /dev/null -w "%{http_code}\n" http://10.130.198.103:18789/webhook/seatalk
```

- 若返回 **200**：说明端口和路由都通，问题多半在 SeaTalk 填的 URL（用了 https 或错端口）。
- 若 **超时 / 连接被拒**：多半是防火墙或安全组未放行 18789，或 10.130.198.103 不可达（网络/路由）。

---

### 很多 127.0.0.1:18789 进程，希望只留一个 0.0.0.0:18789

能正常被外网验证的机器上，通常**只有一个**进程在监听 **0.0.0.0:18789**。若你这台机上有**多个**进程在监听 **127.0.0.1:18789**（或混有 127.0.0.1 与 0.0.0.0），建议关掉多余的，只保留一个监听 0.0.0.0:18789 的 Gateway。

**1. 看谁在占 18789**

```bash
# 看监听地址和进程
ss -tlnp | grep 18789
# 或
lsof -i :18789
```

- 理想情况：只有一行 **0.0.0.0:18789**，对应一个 `openclaw-gateway`（或 `openclaw`）进程。
- 若有多行且是 **127.0.0.1:18789**，说明有多个实例只监听本机，外部访问会连不上。

**2. 关掉所有占用 18789 的 Gateway**

```bash
# 按 PID 关（把下面 PID 换成你上面看到的）
kill <PID>

# 或一次性按端口杀（慎用，确认 18789 只给 Gateway 用）
fuser -k 18789/tcp
```

若 Gateway 是用 **systemd** 起的，先不要用 `fuser -k`，用：

```bash
sudo systemctl stop openclaw-gateway   # 或你的服务名
```

**3. 只起一个 Gateway，并保证 bind=lan**

- 确认 `~/.openclaw/openclaw.json` 里 **`gateway.bind` 为 `"lan"`**（不要用 `"loopback"`）。
- 只在一个终端或只通过 systemd 起**一次**，例如：
  ```bash
  openclaw gateway --port 18789
  ```
  或
  ```bash
  sudo systemctl start openclaw-gateway
  ```

**4. 再确认一次**

```bash
ss -tlnp | grep 18789
```

应只有**一行**，且为 **0.0.0.0:18789**，对应一个 openclaw 进程。这样外网访问 `http(s)://你的IP:18789/webhook/seatalk` 才会到正确的进程。

---

## 三、小结

| 内容                                 | 写到哪里                                       | 说明                                                                                                                                                                            |
| ------------------------------------ | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SeaTalk App ID / Secret、AB Token 等 | `~/.openclaw/.env` 或 `openclaw.json` 的 `env` | 推荐 `.env`，改完重启 Gateway                                                                                                                                                   |
| SeaTalk 事件回调 URL                 | SeaTalk 开放平台后台「事件回调」配置项         | 填你部署的、能接收 POST 的地址，例如 OpenClaw Gateway 的 `http(s)://主机:18789/api/webhook/seatalk` 或 LLM_minecraft 的 `https://域名:8000/api/webhook/seatalk`；仅发消息可不填 |
