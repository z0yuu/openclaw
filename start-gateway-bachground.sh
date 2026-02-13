#!/usr/bin/env bash
# OpenClaw Gateway 后台启动/停止脚本
# 用法: ./start-gateway-background.sh [start|stop]  默认 start

set -e
cd "$(dirname "$0")"
PORT="${OPENCLAW_PORT:-18789}"
LOG_DIR="${OPENCLAW_LOG_DIR:-/root/.openclaw}"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/gateway.log"
PID_FILE="$LOG_DIR/gateway.pid"

# 端口转十六进制（/proc/net/tcp 里端口是 hex）
port_to_hex() { printf '%04X' "$1"; }

# 用 /proc 查占用某端口的 PID（不依赖 fuser/lsof/ss）
pids_listening_on_port() {
  local port_hex inodes inode pid fd link
  port_hex=$(port_to_hex "$PORT")
  [ ! -r /proc/net/tcp ] && return 1
  inodes=$(awk -v p="$port_hex" 'NR>1 && $2 ~ ":"p"$" { print $10 }' /proc/net/tcp 2>/dev/null)
  [ -z "$inodes" ] && return 1
  for pid in /proc/[0-9]*; do
    [ ! -d "$pid/fd" ] && continue
    pid=${pid#/proc/}
    for fd in /proc/$pid/fd/*; do
      link=$(readlink "$fd" 2>/dev/null) || continue
      for inode in $inodes; do
        [ "$link" = "socket:[$inode]" ] && echo "$pid" && break
      done
    done
  done
}

# 收集「所有」与本端口 gateway 相关的 PID（pid 文件 + 占端口 + 命令行匹配），去重后一起杀，避免先杀子进程后父进程又拉起新子进程
collect_all_gateway_pids() {
  local pids=""
  local pid
  [ -f "$PID_FILE" ] && pid=$(cat "$PID_FILE") && [ -n "$pid" ] && pids="$pid"
  pids="$pids $(pids_listening_on_port 2>/dev/null)"
  if command -v pgrep &>/dev/null; then
    pids="$pids $(pgrep -f "gateway --port ${PORT}" 2>/dev/null)"
  else
    pids="$pids $(ps -eo pid,args 2>/dev/null | awk -v port="$PORT" '$0 ~ "gateway.*--port.*"port { print $1 }')"
  fi
  # 去重、去空、去掉当前 shell
  echo "$pids" | tr -s ' \n' '\n' | grep -E '^[0-9]+$' | sort -u
}

# 一次性 kill -9 所有收集到的 PID（同时杀整棵树，父进程没机会 respawn）
stop_gateway() {
  echo "正在停止 Gateway (端口 $PORT)…"
  local all_pids
  all_pids=$(collect_all_gateway_pids)
  if [ -z "$all_pids" ]; then
    rm -f "$PID_FILE"
    echo "未发现占用端口 $PORT 的网关进程；已清除 PID 文件。"
    return 0
  fi
  # 先发 SIGTERM 一次，再立刻 SIGKILL 整批，避免父进程在间隙里 respawn
  echo "$all_pids" | tr '\n' ' ' | xargs kill 2>/dev/null
  echo "$all_pids" | tr '\n' ' ' | xargs kill -9 2>/dev/null
  echo "已结束网关进程（同时 kill 整棵树，防 respawn）: $(echo $all_pids | tr '\n' ' ')"
  rm -f "$PID_FILE"
  sleep 1
  # 若还有漏网（例如新 spawn 的），再收一次并 -9
  all_pids=$(collect_all_gateway_pids)
  if [ -n "$all_pids" ]; then
    echo "补杀残留: $(echo $all_pids | tr '\n' ' ')"
    echo "$all_pids" | tr '\n' ' ' | xargs kill -9 2>/dev/null
    sleep 1
  fi
  if [ -z "$(pids_listening_on_port 2>/dev/null)" ]; then
    echo "Gateway 已停止。"
    return 0
  fi
  echo "端口 $PORT 仍被占用；可再执行一次: $0 stop"
  return 1
}

case "${1:-start}" in
  stop)
    stop_gateway
    ;;
  start)
    # 若已有进程在跑，先不重复启动
    if [ -f "$PID_FILE" ]; then
      OLD_PID=$(cat "$PID_FILE")
      if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Gateway 已在运行 (PID $OLD_PID)，端口 $PORT。停止请执行: $0 stop"
        exit 0
      fi
      rm -f "$PID_FILE"
    fi
    # 若端口已被占用，先一次性停掉整棵网关进程再起（避免父进程 respawn）
    if [ -n "$(pids_listening_on_port 2>/dev/null)" ] || [ -n "$(collect_all_gateway_pids)" ]; then
      echo "端口 $PORT 已被占用，先停止旧进程…"
      stop_gateway || true
      sleep 2
    fi
    nohup pnpm openclaw gateway --port "$PORT" --verbose >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Gateway 已在后台启动 (PID $(cat "$PID_FILE"))，端口 $PORT"
    echo "日志: $LOG_FILE"
    echo "确认在跑: ps -ef | grep 18789  或  netstat -anp | grep $PORT（进程名多为 openclaw-gateway/node）"
    echo "停止: $0 stop（脚本会用 kill，必要时自动 kill -9）"
    ;;
  *)
    echo "用法: $0 {start|stop}"
    exit 1
    ;;
esac
