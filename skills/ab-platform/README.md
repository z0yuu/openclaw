# AB Platform Skill

查询 Shopee 内部 AB 实验平台指标、多实验对比，供 OpenClaw 在用户问「实验指标」「对比实验」时调用。

## 依赖

- Python 3
- `requests`
- 可选：`python-dotenv`（从 .env 加载配置）

```bash
pip install requests python-dotenv
```

## 配置

环境变量：`AB_API_TOKEN`（必需），`AB_PROJECT_ID`、`AB_API_ENV` 等见 `SKILL.md`。

## 代码结构

- `lib/ab_client/`：AB 平台 API 客户端（platform_api、cache、default_metrics）
- `lib/analysis/`：解析与对比（ab_report、comparison）
- `scripts/`：CLI 入口（fetch_metrics.py、compare.py）

从 **agent 根目录** 或 **workspace 根目录** 运行脚本，例如：

```bash
python skills/ab-platform/scripts/fetch_metrics.py 15367
python skills/ab-platform/scripts/compare.py 15367,15368 --metrics=gmv
```

参考 `SKILL.md` 的完整说明。
