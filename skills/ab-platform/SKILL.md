---
name: ab-platform
description: 查询 Shopee 内部 AB 实验平台指标、对比多实验、查看趋势与显著性。当用户提到「实验指标」「AB 数据」「对比实验」「实验 15367」等时使用。
metadata:
  openclaw:
    emoji: "📊"
    requires:
      env: ["AB_API_TOKEN"]
    primaryEnv: "AB_API_TOKEN"
---

# AB 实验平台查询

从 Shopee AB Report Open API 获取实验指标、多实验对比，并格式化为可读结果。适用于产品/数据同学快速查实验表现。

## 何时使用

- 用户问「实验 xxx 的指标」「看看实验 15367」「AB 实验数据」→ 使用 **指标查询**。
- 用户问「对比实验 A 和 B」「哪个实验更好」→ 使用 **对比**。
- 需要指定项目、日期范围、地区、指标列表时，从用户意图中解析或使用默认值。

## 环境变量

| 变量                    | 必需 | 说明                             |
| ----------------------- | ---- | -------------------------------- |
| `AB_API_TOKEN`          | 是   | AB 平台 API Token                |
| `AB_PROJECT_ID`         | 否   | 默认项目 ID，默认 27             |
| `AB_API_ENV`            | 否   | live / staging / test，默认 live |
| `AB_CLIENT_SERVER_NAME` | 否   | 请求头 X-Client-Server-Name      |
| `AB_OPERATOR`           | 否   | 操作者标识                       |
| `AB_API_TIMEOUT`        | 否   | 请求超时秒数，默认 30            |

配置示例：

```bash
export AB_API_TOKEN="your_token"
export AB_PROJECT_ID="27"
```

## 能力一览

| 能力       | 脚本                       | 说明                  |
| ---------- | -------------------------- | --------------------- |
| 指标查询   | `scripts/fetch_metrics.py` | 单实验指标 + 相对提升 |
| 多实验对比 | `scripts/compare.py`       | 多实验指标对比与排序  |

## 工具用法

脚本需在 **skill 所在目录的上一级**（即 `skills/` 所在的工作区根或 agent 根）运行，或确保 `skills/ab-platform` 为当前目录的父级，以便正确解析 `lib`。

### 1. 指标查询

```bash
python skills/ab-platform/scripts/fetch_metrics.py <experiment_id> [project_id] [options]
```

| 参数          | 说明                | 示例                  |
| ------------- | ------------------- | --------------------- |
| experiment_id | 实验 ID             | 15367                 |
| project_id    | 项目 ID（可选）     | 27                    |
| --metrics     | 指标列表，逗号分隔  | order_cnt,gmv         |
| --control     | 对照组 ID           | 82930                 |
| --treatments  | 实验组 ID，逗号分隔 | 82944,82945           |
| --dates       | 日期范围 start,end  | 2026-02-01,2026-02-10 |
| --regions     | 地区，逗号分隔      | TW,ID                 |
| --json        | 输出 JSON           |                       |
| --no-cache    | 不使用缓存          |                       |

示例：

```bash
python skills/ab-platform/scripts/fetch_metrics.py 15367
python skills/ab-platform/scripts/fetch_metrics.py 15367 27 --metrics=order_cnt,gmv --json
```

### 2. 多实验对比

```bash
python skills/ab-platform/scripts/compare.py <exp_id1>,<exp_id2>,... [options]
```

| 参数           | 说明                                | 示例          |
| -------------- | ----------------------------------- | ------------- |
| experiment_ids | 实验 ID 列表，逗号分隔（至少 2 个） | 15367,15368   |
| --project-id   | 项目 ID                             | 27            |
| --metrics      | 对比指标                            | order_cnt,gmv |
| --sort-by      | 排序依据指标                        | gmv           |
| --json         | 输出 JSON                           |               |

示例：

```bash
python skills/ab-platform/scripts/compare.py 15367,15368
python skills/ab-platform/scripts/compare.py 15367,15368,15369 --metrics=gmv --sort-by=gmv --json
```

## defaults.json 默认配置（可选，但推荐）

除环境变量外，本 skill 支持用 `defaults.json` 存放“团队常用默认配置”，便于不传参时直接查询。

- 位置：`skills/ab-platform/defaults.json`
- 读取逻辑：
  - `scripts/fetch_metrics.py`：当 `experiment_id` 未传、`--control/--treatments` 未传时，会从 defaults.json 读取。
  - `template_group_name`：若 defaults.json 配了 `template_group_name`，脚本会带到 API 请求中。

运行示例：

```bash
# 不传 experiment_id：自动使用 defaults.json 的 experiment.id
python skills/ab-platform/scripts/fetch_metrics.py

# 仍可覆盖默认值
python skills/ab-platform/scripts/fetch_metrics.py 15367 --control=82930 --treatments=82944,82945
```

## 默认指标

未指定 `--metrics` 时使用默认指标：order_cnt, gmv, gmv_995, gmv_995_v2, nmv, ads_load, ads_revenue_usd, bad_query_rate。可在 `lib/ab_client/default_metrics.py` 中修改。

## 缓存

指标结果会缓存在 skill 目录下的 `.cache` 中，减少重复请求。使用 `--no-cache` 可跳过缓存。

## 代码结构

```
skills/ab-platform/
├── SKILL.md                 # 本说明
├── lib/
│   ├── ab_client/           # AB 平台 API 客户端
│   │   ├── platform_api.py  # 请求与轮询
│   │   ├── cache.py         # 本地缓存
│   │   └── default_metrics.py
│   └── analysis/            # 解析与对比
│       ├── ab_report.py     # 格式化、lift 提取
│       └── comparison.py    # 多实验对比
└── scripts/
    ├── fetch_metrics.py     # 指标查询入口
    └── compare.py           # 对比入口
```

逻辑集中在 `lib`，脚本仅做参数解析与调用，便于维护和扩展（如后续增加 significance、trend）。
