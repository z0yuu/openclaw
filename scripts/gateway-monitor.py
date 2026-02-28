#!/usr/bin/env python3
"""OpenClaw Gateway 实时日志监控

用法:
  python scripts/gateway-monitor.py                # 实时跟踪 (终端彩色)
  python scripts/gateway-monitor.py --session      # 同时监控 session 对话内容
  python scripts/gateway-monitor.py --last 50      # 回放最近 50 条关键事件
  python scripts/gateway-monitor.py --last-session 20  # 回放最近 20 条对话记录
  python scripts/gateway-monitor.py --daemon       # 后台守护模式, 写入 gateway-readable.log
"""

import argparse
import json
import os
import re
import sys
import time
import glob
import signal
from datetime import datetime

SEATALK_META_RE = re.compile(
    r"^Conversation info \(untrusted metadata\):\s*```json\s*\{[^}]*\}\s*```\s*",
    re.DOTALL,
)

DEFAULT_LOG = os.path.expanduser("~/.openclaw/gateway.log")
READABLE_LOG = os.path.expanduser("~/.openclaw/gateway-readable.log")
SESSIONS_DIR = os.path.expanduser("~/.openclaw/agents/main/sessions")
MONITOR_PID = os.path.expanduser("~/.openclaw/gateway-monitor.pid")

ANSI_RE = re.compile(r"\033\[[0-9;]*m")

R   = "\033[0m"
DIM = "\033[2m"
B   = "\033[1m"
CY  = "\033[36m"
GR  = "\033[32m"
YL  = "\033[33m"
RD  = "\033[31m"
MG  = "\033[35m"
BL  = "\033[34m"
WH  = "\033[97m"

_use_color = True

def _c(code):
    return code if _use_color else ""

# ---------------------------------------------------------------------------

def _ts(iso):
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.astimezone().strftime("%H:%M:%S")
    except Exception:
        return iso[:19] if iso else "??:??:??"

def _sid(s, n=8):
    return s[:n] if s else "?"

def _tr(text, mx=120):
    text = text.replace("\n", " ").strip()
    return text[:mx] + "..." if len(text) > mx else text

def _dur(ms):
    if ms is None: return "?"
    ms = int(ms)
    if ms < 1000: return f"{ms}ms"
    s = ms / 1000
    if s < 60: return f"{s:.1f}s"
    return f"{int(s//60)}m{s%60:.0f}s"

def _strip_meta(text):
    text = SEATALK_META_RE.sub("", text)
    text = re.sub(r"^\[.*?\]\s*", "", text, count=1)
    return text.strip()

# ---------------------------------------------------------------------------
# Gateway log parser
# ---------------------------------------------------------------------------

def parse_gw(raw):
    raw = raw.strip()
    if not raw: return None
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return None
    ts = obj.get("time") or obj.get("_meta", {}).get("date", "")
    msg = obj.get("1", "")
    if not isinstance(msg, str):
        msg = str(msg)
    sub = ""
    try:
        s0 = obj.get("0", "{}")
        if isinstance(s0, str):
            sub = json.loads(s0).get("subsystem", "")
        elif isinstance(s0, dict):
            sub = s0.get("subsystem", "")
    except Exception:
        pass
    return ts, sub, msg


def fmt_gw(ts, sub, msg):
    t = _ts(ts)

    if "SeaTalk webhook event_type=message_from_bot_subscriber" in msg:
        return f"{_c(CY)}{t}{_c(R)} {_c(GR)}>>> 收到私聊消息{_c(R)} {_c(DIM)}(SeaTalk){_c(R)}"
    if "SeaTalk webhook event_type=new_mentioned_message_received_from_group_chat" in msg:
        return f"{_c(CY)}{t}{_c(R)} {_c(GR)}>>> 收到群聊@消息{_c(R)} {_c(DIM)}(SeaTalk){_c(R)}"
    if "chat.send" in msg and "req" in msg[:20]:
        return f"{_c(CY)}{t}{_c(R)} {_c(GR)}>>> 收到对话请求{_c(R)} {_c(DIM)}(WebChat){_c(R)}"
    if "prompt.send" in msg and "req" in msg[:20]:
        return f"{_c(CY)}{t}{_c(R)} {_c(GR)}>>> 收到 prompt 请求{_c(R)} {_c(DIM)}(HTTP){_c(R)}"

    m = re.search(r"embedded run start: runId=(\S+) sessionId=(\S+) provider=(\S+) model=(\S+).*messageChannel=(\S+)", msg)
    if m:
        rid, _, prov, model, ch = m.groups()
        return f"{_c(CY)}{t}{_c(R)} {_c(YL)}[开始处理]{_c(R)}  run={_c(B)}{_sid(rid)}{_c(R)}  模型={_c(MG)}{prov}/{model}{_c(R)}  来源={ch}"

    m = re.search(r"embedded run prompt start: runId=(\S+)", msg)
    if m:
        return f"{_c(CY)}{t}{_c(R)} {_c(BL)}[调用模型]{_c(R)}  run={_sid(m.group(1))}  思考中..."

    m = re.search(r"embedded run prompt end: runId=(\S+) sessionId=\S+ durationMs=(\d+)", msg)
    if m:
        return f"{_c(CY)}{t}{_c(R)} {_c(BL)}[模型返回]{_c(R)}  run={_sid(m.group(1))}  耗时={_dur(m.group(2))}"

    m = re.search(r"embedded run done: runId=(\S+) sessionId=\S+ durationMs=(\d+) aborted=(\S+)", msg)
    if m:
        rid, dur, ab = m.group(1), m.group(2), m.group(3)
        if ab == "true":
            return f"{_c(CY)}{t}{_c(R)} {_c(RD)}[已中止]{_c(R)}  run={_sid(rid)}  总耗时={_c(B)}{_dur(dur)}{_c(R)}"
        return f"{_c(CY)}{t}{_c(R)} {_c(GR)}[完成]{_c(R)}  run={_sid(rid)}  总耗时={_c(B)}{_dur(dur)}{_c(R)}"

    m = re.search(r"stream=tool aseq=\d+ tool=start:(\S+) call=(\S+)", msg)
    if m:
        return f"{_c(CY)}{t}{_c(R)} {_c(YL)}  [工具]{_c(R)} {_c(B)}{m.group(1)}{_c(R)}  开始执行"

    m = re.search(r"stream=tool aseq=\d+ tool=result:(\S+) call=\S+\s*(?:meta=(.+?))?(?:\s+err=(\S+))?$", msg)
    if m:
        tool, meta, err = m.group(1), m.group(2) or "", m.group(3)
        if err and err != "false":
            return f"{_c(CY)}{t}{_c(R)} {_c(RD)}  [工具] {tool} 失败{_c(R)}  {_c(DIM)}{_tr(meta,80)}{_c(R)}"
        return f"{_c(CY)}{t}{_c(R)} {_c(DIM)}  [工具] {tool} 完成  {_tr(meta,80)}{_c(R)}"

    if "embedded run tool end" in msg:
        return None

    m = re.search(r"stream=assistant aseq=(\d+) text=(.+)", msg)
    if m:
        aseq = int(m.group(1))
        if aseq <= 2:
            return f"{_c(CY)}{t}{_c(R)} {_c(WH)}[回复]{_c(R)}  {_c(DIM)}{_tr(m.group(2), 100)}{_c(R)}"
        return None

    m = re.search(r"session state:.*prev=(\S+) new=(\S+) reason=\"?([^\"]+)\"?", msg)
    if m:
        prev, new, reason = m.groups()
        if new == "processing":
            return f"{_c(CY)}{t}{_c(R)} {_c(DIM)}[会话] idle -> processing ({reason}){_c(R)}"
        if new == "idle":
            return f"{_c(CY)}{t}{_c(R)} {_c(DIM)}[会话] processing -> idle ({reason}){_c(R)}"
        return None

    m = re.search(r"embedded run timeout: runId=(\S+).*timeoutMs=(\d+)", msg)
    if m:
        return f"{_c(CY)}{t}{_c(R)} {_c(RD)}[超时!]{_c(R)} run={_sid(m.group(1))} timeout={_dur(m.group(2))}"

    if "compaction start" in msg:
        return f"{_c(CY)}{t}{_c(R)} {_c(DIM)}[压缩] 上下文压缩中...{_c(R)}"
    if "compaction retry" in msg:
        return f"{_c(CY)}{t}{_c(R)} {_c(YL)}[压缩] 重试{_c(R)}"

    m = re.search(r"Tracking pending messaging text: tool=(\S+) len=(\d+)", msg)
    if m:
        return f"{_c(CY)}{t}{_c(R)} {_c(DIM)}[发送] {m.group(1)} ({m.group(2)}字){_c(R)}"

    m = re.search(r"lane task done: lane=main durationMs=(\d+)", msg)
    if m:
        return f"{_c(CY)}{t}{_c(R)} {_c(DIM)}[lane] 完成 耗时={_dur(m.group(1))}{_c(R)}"
    m = re.search(r"lane enqueue.*queued=(\d+)", msg)
    if m and int(m.group(1)) > 0:
        return f"{_c(CY)}{t}{_c(R)} {_c(YL)}[排队] 深度={m.group(1)}{_c(R)}"

    if "error" in msg.lower() and "no_active_run" not in msg:
        return f"{_c(CY)}{t}{_c(R)} {_c(RD)}[错误] {_tr(msg,120)}{_c(R)}"

    return None

# ---------------------------------------------------------------------------
# Session JSONL parser
# ---------------------------------------------------------------------------

def get_latest_session():
    files = glob.glob(os.path.join(SESSIONS_DIR, "*.jsonl"))
    return max(files, key=os.path.getmtime) if files else None


def fmt_session(obj):
    msg = obj.get("message", {})
    role = msg.get("role", "")
    t = _ts(obj.get("timestamp", ""))

    if role == "user":
        content = ""
        for p in msg.get("content", []):
            if isinstance(p, dict) and p.get("type") == "text":
                content = p.get("text", "")
                break
            elif isinstance(p, str):
                content = p
                break
        if not content:
            content = str(msg.get("content", ""))[:200]
        content = _strip_meta(content)
        if not content or content.startswith("A new session was started"):
            return None
        return f"{_c(CY)}{t}{_c(R)} {_c(GR)}{_c(B)}[用户]{_c(R)}  {_tr(content, 150)}"

    if role == "assistant":
        parts = msg.get("content", [])
        if not isinstance(parts, list):
            parts = [parts]
        texts, tools = [], []
        for p in parts:
            if isinstance(p, dict):
                if p.get("type") == "text":
                    texts.append(p.get("text", ""))
                elif p.get("type") == "toolCall":
                    tools.append(p.get("name", "?"))
            elif isinstance(p, str):
                texts.append(p)
        lines = []
        if tools:
            lines.append(f"{_c(CY)}{t}{_c(R)} {_c(YL)}[AI 调用]{_c(R)}  {', '.join(tools)}")
        if texts:
            lines.append(f"{_c(CY)}{t}{_c(R)} {_c(WH)}[AI 回复]{_c(R)}  {_tr(' '.join(texts), 150)}")
        usage = msg.get("usage", {})
        if usage and (usage.get("input") or usage.get("output")):
            model = msg.get("model", "?")
            lines.append(f"{_c(CY)}{t}{_c(R)} {_c(DIM)}         模型={model}  tokens: in={usage.get('input',0)} out={usage.get('output',0)}{_c(R)}")
        return "\n".join(lines) if lines else None

    if role == "toolResult":
        tn = msg.get("toolName", "?")
        content = ""
        for p in msg.get("content", []):
            if isinstance(p, dict) and p.get("type") == "text":
                content = p.get("text", "")[:100]
                break
        if msg.get("isError"):
            return f"{_c(CY)}{t}{_c(R)} {_c(RD)}  [工具结果] {tn} 失败{_c(R)}  {_c(DIM)}{_tr(content,80)}{_c(R)}"
        return f"{_c(CY)}{t}{_c(R)} {_c(DIM)}  [工具结果] {tn}  {_tr(content,80)}{_c(R)}"

    return None


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

_output_file = None

def emit(line):
    if _output_file:
        _output_file.write(line + "\n")
        _output_file.flush()
    else:
        print(line)

# ---------------------------------------------------------------------------
# Replay / Tail
# ---------------------------------------------------------------------------

def replay_gw(path, n):
    events = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            p = parse_gw(raw)
            if not p: continue
            out = fmt_gw(*p)
            if out: events.append(out)
    for ev in events[-n:]:
        emit(ev)


def replay_session(n):
    sf = get_latest_session()
    if not sf:
        print("No session files found.", file=sys.stderr)
        return
    emit(f"Session: {os.path.basename(sf)}")
    emit("-" * 60)
    events = []
    with open(sf, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                obj = json.loads(line)
                if obj.get("type") == "message":
                    out = fmt_session(obj)
                    if out: events.append(out)
            except json.JSONDecodeError:
                pass
    for ev in events[-n:]:
        emit(ev)


def tail_loop(log_path, watch_session):
    emit(f"OpenClaw Gateway 实时监控  日志={log_path}")
    emit("-" * 60)

    sf = None
    spos = 0
    if watch_session:
        sf = get_latest_session()
        if sf:
            spos = os.path.getsize(sf)

    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if line:
                p = parse_gw(line)
                if p:
                    out = fmt_gw(*p)
                    if out: emit(out)

            if watch_session:
                nsf = get_latest_session()
                if nsf and nsf != sf:
                    sf = nsf
                    spos = 0
                    emit(f"-- 新会话: {os.path.basename(sf)} --")
                if sf:
                    try:
                        sz = os.path.getsize(sf)
                    except OSError:
                        sz = 0
                    if sz > spos:
                        with open(sf, "r", encoding="utf-8", errors="replace") as sfh:
                            sfh.seek(spos)
                            for sl in sfh:
                                sl = sl.strip()
                                if not sl: continue
                                try:
                                    obj = json.loads(sl)
                                    if obj.get("type") == "message":
                                        out = fmt_session(obj)
                                        if out: emit(out)
                                except json.JSONDecodeError:
                                    pass
                            spos = sfh.tell()

            if not line:
                time.sleep(0.3)


def daemon_mode(log_path):
    """后台守护: 不带颜色, 输出到 gateway-readable.log, 同时监控 session."""
    global _use_color, _output_file
    _use_color = False

    with open(MONITOR_PID, "w") as pf:
        pf.write(str(os.getpid()))

    def _cleanup(sig, frame):
        try: os.remove(MONITOR_PID)
        except OSError: pass
        sys.exit(0)

    signal.signal(signal.SIGTERM, _cleanup)
    signal.signal(signal.SIGINT, _cleanup)

    for _ in range(60):
        if os.path.exists(log_path):
            break
        time.sleep(1)

    _output_file = open(READABLE_LOG, "a", encoding="utf-8")
    try:
        tail_loop(log_path, watch_session=True)
    finally:
        _output_file.close()
        try: os.remove(MONITOR_PID)
        except OSError: pass


def main():
    ap = argparse.ArgumentParser(description="OpenClaw Gateway 实时日志监控")
    ap.add_argument("--log", default=DEFAULT_LOG, help="gateway.log 路径")
    ap.add_argument("--last", type=int, default=0, metavar="N",
                     help="回放最近 N 条 gateway 关键事件")
    ap.add_argument("--last-session", type=int, default=0, metavar="N",
                     help="回放最近 N 条对话记录")
    ap.add_argument("--session", action="store_true",
                     help="同时监控 session 对话内容")
    ap.add_argument("--daemon", action="store_true",
                     help=f"后台守护模式, 写入 {READABLE_LOG}")
    args = ap.parse_args()

    if not os.path.exists(args.log):
        print(f"日志文件不存在: {args.log}", file=sys.stderr)
        sys.exit(1)

    if args.daemon:
        daemon_mode(args.log)
    elif args.last_session > 0:
        replay_session(args.last_session)
    elif args.last > 0:
        replay_gw(args.log, args.last)
    else:
        try:
            tail_loop(args.log, args.session)
        except KeyboardInterrupt:
            print(f"\n{_c(DIM)}监控已停止{_c(R)}")


if __name__ == "__main__":
    main()
