---
name: config-release-history
description: 查询 Shopee 内部实验配置平台（Config Platform）的历史发布记录，查看发布 diff 和日期。当用户提到「配置发布」「发布记录」「config 历史」「prerank 配置」「查看发布」或指定地区如「id 地区」「ph 地区」时使用。
metadata:
  openclaw:
    emoji: "📜"
---

# 实验配置平台发布记录查询

从 Shopee Config Platform（通过 OpsGW）获取指定 namespace 的历史发布记录，自动分析 **实验桶（bucket）** 和 **Predictor** 的变更，以结构化方式展示。

## 何时使用

- 用户问「id 地区的发布记录」「ph 地区的配置历史」→ 映射到对应 namespace 查询。
- 用户问「最近发布了什么」「上次发布改了什么」「最近改了什么」→ 查询最新几个版本的 diff。
- 用户想看哪些桶的 DAG 或 Predictor 发生了变化 → 默认桶级别分析会自动列出。
- 用户想看原始 unified diff → 使用 `--raw-diff` 模式。

## 地区到 Namespace 映射

用户提及的地区会自动映射为 namespace：

| 用户说法             | namespace            |
| -------------------- | -------------------- |
| id / ID 地区         | item_prerank_live_id |
| ph / PH 地区         | item_prerank_live_ph |
| sg / SG 地区         | item_prerank_live_sg |
| th / TH 地区         | item_prerank_live_th |
| tw / TW 地区         | item_prerank_live_tw |
| my / MY 地区         | item_prerank_live_my |
| vn / VN 地区         | item_prerank_live_vn |
| br / BR 地区         | item_prerank_live_br |
| mx / MX 地区         | item_prerank_live_mx |
| cl / CL 地区         | item_prerank_live_cl |
| co / CO 地区         | item_prerank_live_co |
| （直接给 namespace） | 按原值使用           |

## 前提条件

- 机器上运行着 OpsGW Caller Agent，UNIX socket 位于 `/tmp/opsgw_caller_agent.sock`。
- Python 2.7+ 或 Python 3.x（脚本兼容两者）。

## 工具用法

```bash
python skills/config-release-history/scripts/fetch_release_history.py <namespace> [options]
```

### 参数

| 参数         | 说明                                             | 示例                 |
| ------------ | ------------------------------------------------ | -------------------- |
| namespace    | 配置 namespace                                   | item_prerank_live_id |
| --project    | 项目名（默认 search_rankservice）                | search_rankservice   |
| --zone       | zone（默认 global）                              | global / all         |
| --limit      | 最多显示几个版本（默认 10）                      | 20                   |
| --raw-diff   | 使用原始 unified diff 模式（默认桶级别智能分析） |                      |
| --key-filter | (仅 --raw-diff) 只看包含此关键字的 key 的变更    | ABLayer              |
| --full-diff  | (仅 --raw-diff) 显示完整 diff 而非摘要           |                      |
| --json       | 输出 JSON 格式                                   |                      |

### 示例

```bash
# 查看 ID 地区最近 10 个版本的发布记录（默认桶级别分析）
python skills/config-release-history/scripts/fetch_release_history.py item_prerank_live_id

# 查看 PH 地区最近 5 个版本
python skills/config-release-history/scripts/fetch_release_history.py item_prerank_live_ph --limit 5

# 使用原始 unified diff 查看详细变更
python skills/config-release-history/scripts/fetch_release_history.py item_prerank_live_ph --limit 3 --raw-diff --full-diff

# 输出 JSON 格式以便进一步处理
python skills/config-release-history/scripts/fetch_release_history.py item_prerank_live_id --json
```

## 输出格式

脚本默认使用**桶级别智能分析**，分别展示 DAG 变更和 Predictor 变更：

```
--- Version 378 (当前生效) ---
  发布时间: 2026-02-24 15:17:34

  与上一版本 (v377) 的差异:

  [DAG] 变更的实验桶 (2 个):
    bucket_id_14: 变更字段 predictor_dag
      predictor_dag:
        旧: ... -> mvp_v5 -> ... -> score_mvp_v4 -> ...
        新: ... -> mvp_v6 -> ... -> score_mvp_v5 -> ...
    bucket_id_16: 变更字段 predictor_dag
      ...

  [Predictor] 变更 (1 个):
    + PH_prerank_merge_score_mix_score_mvp_v5 (MathExprPredictor, expr=...)
```

只要 DAG 或 Predictor 任一有变化就会报告为有变化，并列出具体变更的实验桶和 predictor。

## 代码结构

```
skills/config-release-history/
├── SKILL.md                              # 本说明
└── scripts/
    └── fetch_release_history.py          # 查询入口
```

## 运行环境

脚本兼容 **Python 2.7.18** 与 **Python 3.x**，可任选其一运行（如 `python2.7 scripts/...` 或 `python3 scripts/...`）。

## 注意事项

- 每次 API 调用最多返回 100 个版本，脚本会自动翻页。
- 默认模式按桶级别分析 ABLayer 和 Predictor 的变更，使用 `--raw-diff` 可查看原始 unified diff。
- DAG 变更和 Predictor 变更独立报告，任一有变化即为有变化。
