---
name: config-release-history
description: 查询 Shopee 内部实验配置平台（Config Platform）的历史发布记录，查看发布 diff 和日期。当用户提到「配置发布」「发布记录」「config 历史」「prerank 配置」「查看发布」或指定地区如「id 地区」「ph 地区」时使用。
metadata:
  openclaw:
    emoji: "📜"
---

# 实验配置平台发布记录查询

# 需要现在本地搭建opsgw服务

#命令: curl https://proxy.uss.s3.sz.shopee.io/api/v4/50064306/stoc-sg-live/opsgw_caller_agent_install.sh | sh 安装完成后 可以先用我的下述配置即可（小心外传）
export OPSGW_BU="shopee"
export OPSGW_ENV="live"
export OPSGW_APP_ID="search_rankservice_shopee_live"
export OPSGW_APP_SECRET="83yMSdY04j72"
整体参考 https://confluence.shopee.io/display/STS/%5BOpsAPI+Gateway%5D+Caller+SDK
从 Shopee Config Platform（通过 OpsGW）获取指定 namespace 的历史发布记录，并自动计算相邻版本之间的 diff，以表格/摘要方式展示。

## 何时使用

- 用户问「id 地区的发布记录」「ph 地区的配置历史」→ 映射到对应 namespace 查询。
- 用户问「最近发布了什么」「上次发布改了什么」→ 查询最新几个版本的 diff。
- 用户想看某个 key 的变更历史 → 带上 `--key-filter` 筛选。

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

| 参数         | 说明                              | 示例                 |
| ------------ | --------------------------------- | -------------------- |
| namespace    | 配置 namespace                    | item_prerank_live_id |
| --project    | 项目名（默认 search_rankservice） | search_rankservice   |
| --zone       | zone（默认 global）               | global / all         |
| --limit      | 最多显示几个版本（默认 10）       | 20                   |
| --key-filter | 只看包含此关键字的 key 的变更     | ABLayer              |
| --full-diff  | 显示完整 diff 而非摘要            |                      |
| --json       | 输出 JSON 格式                    |                      |

### 示例

```bash
# 查看 ID 地区最近 10 个版本的发布记录和 diff
python skills/config-release-history/scripts/fetch_release_history.py item_prerank_live_id

# 查看 PH 地区最近 5 个版本，只看 ABLayer 相关的变更
python skills/config-release-history/scripts/fetch_release_history.py item_prerank_live_ph --limit 5 --key-filter ABLayer

# 查看 PH 地区最近 3 个版本的完整 diff
python skills/config-release-history/scripts/fetch_release_history.py item_prerank_live_ph --limit 3 --full-diff

# 输出 JSON 格式以便进一步处理
python skills/config-release-history/scripts/fetch_release_history.py item_prerank_live_id --json
```

## 输出格式

脚本默认输出人类可读的发布记录摘要：

```
=== 发布记录: item_prerank_live_id ===
共 328 个版本，显示最近 10 个

--- Version 378 (当前生效) ---
发布时间: 2026-02-24 15:17:34
状态: FULL

  与上一版本 (v377) 的差异:
  [变更] ABLayer/sch.qp-layer10:
    + "new_bucket_id_01": { ... }
    - "old_bucket_id_99": { ... }

--- Version 377 ---
发布时间: 2026-02-24 15:11:38
状态: FINISHED

  与上一版本 (v376) 的差异:
  [变更] Predictor:
    ...
```

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
- 配置项的值通常为 JSON 字符串，diff 会按 JSON 格式化后比较以减少噪音。
- 大型配置的 diff 可能较长，默认截断显示，使用 `--full-diff` 查看完整内容。
