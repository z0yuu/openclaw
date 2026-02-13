# SeaTalk Skill

通过 SeaTalk 开放平台发送单聊/群聊消息，供 OpenClaw 在需要「发 SeaTalk」「通知到 SeaTalk」时调用。

## 依赖

- Python 3
- `requests`

```bash
pip install requests
```

## 配置

环境变量：`SEATALK_APP_ID`、`SEATALK_APP_SECRET`（可选 `SEATALK_SIGNING_SECRET`）。

## 运行方式

从 **agent 根目录** 或 **workspace 根目录**（即 `skills/` 的上一级）执行：

```bash
python skills/seatalk/scripts/send_message.py single <employee_code> "消息内容"
python skills/seatalk/scripts/send_message.py group <group_code> "消息内容" [--at-all] [--mention a@x.com,b@x.com]
```

参考 `SKILL.md` 的完整说明。
