# OpenClaw 安装与部署指南

## 环境要求

- **Node.js ≥ 22**
- 系统：macOS、Linux，或 Windows（建议 WSL2）
- 从源码构建时需要 **pnpm**

---

## 方式一：官方安装器（推荐）

一条命令完成安装 + 环境检查：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

安装器会：

- 检测系统并确保 Node 22+
- 用 npm 全局安装 `openclaw@latest`
- 可选运行新手引导

**跳过交互式引导（CI/脚本）：**

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-onboard
```

**查看安装器帮助：**

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --help
```

---

## 方式二：全局 npm/pnpm 安装

已有 Node 22+ 时可直接安装：

```bash
# npm
npm install -g openclaw@latest

# 或 pnpm（需先批准构建脚本）
pnpm add -g openclaw@latest
pnpm approve-builds -g   # 批准 openclaw、sharp 等
pnpm add -g openclaw@latest
```

若 `sharp` 安装失败（例如系统装了 libvips）：

```bash
SHARP_IGNORE_GLOBAL_LIBVIPS=1 npm install -g openclaw@latest
```

---

## 方式三：从源码安装（当前仓库 /root/agent）

你当前机器上已有源码，可按下面步骤安装并运行：

```bash
cd /root/agent

# 1. 安装依赖
pnpm install

# 2. 构建 UI（首次必须）
pnpm ui:build

# 3. 构建项目
pnpm build

# 4. 新手引导并安装守护进程（systemd/launchd）
pnpm openclaw onboard --install-daemon
```

若已全局安装过 openclaw，可直接：

```bash
openclaw onboard --install-daemon
```

**日常开发（Gateway 热重载）：**

```bash
pnpm gateway:watch
```

**手动启动 Gateway（不装守护进程时）：**

```bash
openclaw gateway --port 18789
# 或从仓库：pnpm openclaw gateway --port 18789
```

---

## 新手引导与首次运行

无论用哪种方式安装，都建议跑一次引导：

```bash
openclaw onboard --install-daemon
```

引导会：

- 配置工作区（如 `~/.openclaw/workspace`）
- 写入配置（如 `~/.openclaw/openclaw.json`）
- 安装并启用 **Gateway 守护进程**（launchd/systemd），开机自启

然后可按需：

```bash
# 配对渠道（如 WhatsApp）
openclaw channels login

# 启动 Gateway（若未装守护进程或想手动起）
openclaw gateway --port 18789

# 发测试消息（需先配对）
openclaw message send --target +15555550123 --message "Hello from OpenClaw"
```

**Linux 注意：** 若希望用户注销后 Gateway 仍运行，需启用 lingering：

```bash
sudo loginctl enable-linger $USER
```

---

## 方式四：Docker 部署

适合：容器化运行、无本地 Node、或 VPS 部署。

**要求：** Docker Desktop 或 Docker Engine + Docker Compose v2。

### 快速开始（在仓库根目录）

```bash
cd /root/agent
./docker-setup.sh
```

脚本会：

- 构建 Gateway 镜像
- 运行新手引导
- 用 Docker Compose 启动 Gateway
- 将 token 写入 `.env`

完成后在浏览器打开：`http://127.0.0.1:18789/`，在控制 UI 里粘贴 token。

### 手动 Docker 流程

```bash
docker build -t openclaw:local -f Dockerfile .
docker compose run --rm openclaw-cli onboard
docker compose up -d openclaw-gateway
```

### Docker 下配对渠道

```bash
# WhatsApp（扫码）
docker compose run --rm openclaw-cli channels login

# Telegram
docker compose run --rm openclaw-cli channels add --channel telegram --token "<token>"

# Discord
docker compose run --rm openclaw-cli channels add --channel discord --token "<token>"
```

### 获取控制 UI 的 token（Docker）

若提示未授权或需配对：

```bash
docker compose run --rm openclaw-cli dashboard --no-open
```

---

## 云端 / VPS 部署

Gateway 跑在 VPS 上，通过控制 UI 或 Tailscale/SSH 从本机访问。

- **推荐阅读：** [VPS 托管](https://docs.openclaw.ai/vps)（Oracle、Fly.io、Hetzner、GCP、exe.dev 等）
- **Docker 上 VPS：** [Hetzner（Docker）](https://docs.openclaw.ai/install/hetzner)
- **安全：** 默认只监听本机；对外暴露时需配置 `gateway.auth.token` 或 `gateway.auth.password`，并用 [Tailscale Serve](https://docs.openclaw.ai/gateway/tailscale) 或 [SSH 隧道](https://docs.openclaw.ai/gateway/remote) 访问。

---

## 常用路径

| 用途   | 路径                                     |
| ------ | ---------------------------------------- |
| 配置   | `~/.openclaw/openclaw.json`              |
| 工作区 | `~/.openclaw/workspace`                  |
| 凭证   | `~/.openclaw/credentials/`               |
| 会话   | `~/.openclaw/agents/<agentId>/sessions/` |

---

## 健康检查与故障排查

```bash
openclaw health
openclaw doctor
```

升级后建议执行：

```bash
openclaw doctor
```

更多：[设置](https://docs.openclaw.ai/start/setup)、[快速开始](https://docs.openclaw.ai/start/quickstart)、[安装总览](https://docs.openclaw.ai/install)。
