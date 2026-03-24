---
name: seatalk
description: 通过 SeaTalk 开放平台发送单聊或群聊消息。当用户需要「发 SeaTalk」「通知到 SeaTalk」「发到 SeaTalk 群」时使用。
metadata:
  openclaw:
    emoji: "💬"
    requires:
      env: ["SEATALK_APP_ID", "SEATALK_APP_SECRET"]
    primaryEnv: "SEATALK_APP_ID"
---

# SeaTalk 消息发送

通过 [SeaTalk Open Platform](https://open.seatalk.io) 向指定用户（employee_code）或群组（group_code）发送文本或 Markdown 消息。

## 何时使用

- 用户明确要求「发 SeaTalk」「用 SeaTalk 通知」「发到 SeaTalk 群」「at 某人/全员」。
- 需要把当前对话结论、任务结果、告警等推送到 SeaTalk 单聊或群聊。

## 环境变量

| 变量                     | 必需 | 说明                         |
| ------------------------ | ---- | ---------------------------- |
| `SEATALK_APP_ID`         | 是   | SeaTalk 应用 ID              |
| `SEATALK_APP_SECRET`     | 是   | SeaTalk 应用 Secret          |
| `SEATALK_SIGNING_SECRET` | 否   | 回调签名校验（发消息可不配） |

配置示例（写入 `~/.openclaw/workspace/.env` 或 Gateway 环境）：

```bash
export SEATALK_APP_ID="your_app_id"
export SEATALK_APP_SECRET="your_app_secret"
```

## 工具用法

本 skill 通过脚本 `scripts/send_message.py` 发送消息。在**工作区根目录**（或 skill 所在目录）执行。

### 发送单聊

```bash
python skills/seatalk/scripts/send_message.py single <employee_code> <消息内容>

# 示例
python skills/seatalk/scripts/send_message.py single "E12345" "实验 15367 指标已跑完，GMV 提升 +2.3%"
```

- `employee_code`: 目标用户的 employee code（SeaTalk 侧获取）。

### 发送群聊

```bash
python skills/seatalk/scripts/send_message.py group <group_code> <消息内容> [--at-all] [--mention email1,email2]

# 示例
python skills/seatalk/scripts/send_message.py group "G_xxx" "今日 AB 实验汇总见下方"
python skills/seatalk/scripts/send_message.py group "G_xxx" "请查收" --mention "a@shopee.io,b@shopee.io"
```

- `group_code`: 群组 code。
- `--at-all`: 是否 @所有人。
- `--mention`: 逗号分隔的邮箱，用于 @ 指定成员。

### Markdown

默认发送文本。若内容含 Markdown，可先确认平台是否支持；脚本支持 `--markdown` 时以 markdown 类型发送。

## 安全与权限

- 仅使用已配置的 `SEATALK_APP_ID` / `SEATALK_APP_SECRET`，不要将密钥写入对话或日志。
- 单聊仅能发给已关注该 Bot 的用户；群聊需 Bot 在群内且具备发消息权限。

## 参考

- [SeaTalk 开放平台文档](https://open.seatalk.io/docs)
- [发送消息 API](https://open.seatalk.io/docs/messaging_send-message-to-bot-subscriber_)

## Python 版本

- 此 skill 的 Python 脚本按 **Python 3.8+** 使用。
- 当前脚本静态扫描未发现要求 3.9+/3.10+ 的语法，可按 3.8 基线处理。
