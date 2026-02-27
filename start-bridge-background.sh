#!/usr/bin/env bash
# OpenClaw ↔ my_agent 桥接服务 后台启动/停止/重启脚本
# 用法: ./start-bridge-background.sh [start|stop|restart|status]  默认 start

set -e
cd "$(dirname "$0")"

PORT="${BRIDGE_PORT:-8080}"
LOG_DIR="${BRIDGE_LOG_DIR:-/root/.openclaw}"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/bridge.log"
PID_FILE="$LOG_DIR/bridge.pid"
SERVICE_DIR="$(pwd)/service"

port_to_hex() { printf '%04X' "$1"; }

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

collect_all_pids() {
  local pids=""
  [ -f "$PID_FILE" ] && pids="$(cat "$PID_FILE")"
  pids="$pids $(pids_listening_on_port 2>/dev/null)"
  if command -v pgrep &>/dev/null; then
    pids="$pids $(pgrep -f "python3 agent_server" 2>/dev/null)"
  fi
  echo "$pids" | tr -s ' \n' '\n' | grep -E '^[0-9]+$' | sort -u
}

stop_bridge() {
  echo "正在停止桥接服务 (端口 $PORT)…"
  local all_pids
  all_pids=$(collect_all_pids)
  if [ -z "$all_pids" ]; then
    rm -f "$PID_FILE"
    echo "未发现桥接服务进程。"
    return 0
  fi
  echo "$all_pids" | tr '\n' ' ' | xargs kill 2>/dev/null || true
  sleep 1
  echo "$all_pids" | tr '\n' ' ' | xargs kill -9 2>/dev/null || true
  rm -f "$PID_FILE"
  echo "桥接服务已停止 (PID: $(echo $all_pids | tr '\n' ' '))"
}

start_bridge() {
  if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
      echo "桥接服务已在运行 (PID $OLD_PID)，端口 $PORT"
      echo "重启请执行: $0 restart"
      exit 0
    fi
    rm -f "$PID_FILE"
  fi

  if [ -n "$(pids_listening_on_port 2>/dev/null)" ] || [ -n "$(collect_all_pids)" ]; then
    echo "端口 $PORT 被占用，先停止旧进程…"
    stop_bridge || true
    sleep 1
  fi

  nohup python3 "$SERVICE_DIR/agent_server.py" >> "$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  echo "桥接服务已在后台启动 (PID $(cat "$PID_FILE"))，端口 $PORT"

  # 等待服务就绪，然后检查注册结果
  echo ""
  echo "等待服务启动（首次需从 OpenClaw 获取技能列表，约 10 秒）…"
  for i in $(seq 1 15); do
    sleep 1
    if curl -s --max-time 2 "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
      echo "桥接服务 /health: 正常"
      break
    fi
    if [ "$i" -eq 15 ]; then
      echo "桥接服务启动超时，请检查日志: $LOG_FILE"
    fi
  done

  # 从日志中提取注册结果
  echo ""
  echo "--- my_agent 注册结果 ---"
  REG_LINE=$(grep -E "Registered to my_agent|Registration failed" "$LOG_FILE" | tail -1)
  if [ -z "$REG_LINE" ]; then
    echo "未找到注册记录（可能还在进行中），请查看日志: $LOG_FILE"
  elif echo "$REG_LINE" | grep -q "Registered to my_agent"; then
    echo "注册成功: $REG_LINE"
  else
    echo "注册失败: $REG_LINE"
    echo "桥接服务仍正常运行，远程 agent 可直接调用 http://$(hostname -I | awk '{print $1}'):$PORT/api/chat"
    echo "待 my_agent 修复后，重新注册: $0 restart 或 cd service && python3 register.py"
  fi

  echo ""
  echo "日志: tail -f $LOG_FILE"
  echo "停止: $0 stop"
  echo "重启: $0 restart"
  echo "状态: $0 status"
}

show_status() {
  if [ -f "$PID_FILE" ]; then
    local pid
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
      echo "桥接服务运行中 (PID $pid)，端口 $PORT"
      echo "日志: $LOG_FILE"
      # 检查 OpenClaw Gateway 连通性
      if curl -s --max-time 2 http://127.0.0.1:18789/ >/dev/null 2>&1; then
        echo "OpenClaw Gateway: 正常"
      else
        echo "OpenClaw Gateway: 不可达"
      fi
      # 检查桥接服务本身
      if curl -s --max-time 2 "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
        echo "桥接服务 /health: 正常"
      else
        echo "桥接服务 /health: 不可达（可能还在启动中）"
      fi
      return 0
    fi
  fi
  echo "桥接服务未运行。"
  return 1
}

case "${1:-start}" in
  start)   start_bridge ;;
  stop)    stop_bridge ;;
  restart) stop_bridge; sleep 1; start_bridge ;;
  status)  show_status ;;
  *)
    echo "用法: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac
