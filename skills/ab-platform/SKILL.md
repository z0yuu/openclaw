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
- 用户未指定的参数（实验 ID、项目 ID、地区、对照组、实验组等）一律从 `skills/ab-platform/defaults.json` 读取，不要自行编造。

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

所有脚本使用**绝对路径**调用，无需关心当前工作目录。

### 1. 指标查询

```bash
python /root/agent/skills/ab-platform/scripts/fetch_metrics.py <experiment_id> [project_id] [options]
```

| 参数          | 说明                   | 示例                  |
| ------------- | ---------------------- | --------------------- |
| experiment_id | 实验 ID                | 15367                 |
| project_id    | 项目 ID（可选）        | 27                    |
| --metrics     | 指标列表，逗号分隔     | order_cnt,gmv         |
| --control     | 对照组 ID              | 82930                 |
| --treatments  | 实验组 ID，逗号分隔    | 82944,82945           |
| --dates       | 日期范围 start,end     | 2026-02-01,2026-02-10 |
| --regions     | 地区，逗号分隔         | TW,ID                 |
| --json        | 输出 JSON              |                       |
| --absolute    | 同时显示绝对值         |                       |
| --cache       | 启用缓存（默认不缓存） |                       |

示例：

```bash
python /root/agent/skills/ab-platform/scripts/fetch_metrics.py 15367
python /root/agent/skills/ab-platform/scripts/fetch_metrics.py 15367 27 --metrics=order_cnt,gmv --json
```

### 2. 多实验对比

```bash
python /root/agent/skills/ab-platform/scripts/compare.py <exp_id1>,<exp_id2>,... [options]
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
python /root/agent/skills/ab-platform/scripts/compare.py 15367,15368
python /root/agent/skills/ab-platform/scripts/compare.py 15367,15368,15369 --metrics=gmv --sort-by=gmv --json
```

## 默认配置（必读：用户不说就用这些值，不要再问）

脚本会自动从 `/root/agent/skills/ab-platform/defaults.json` 读取以下默认值。**用户没有明确指定的参数直接用默认值运行，不要反问用户**。

| 参数                | 默认值                                                                                                                                              |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| experiment_id       | **6850**（实验名: vector in coarse ranking）                                                                                                        |
| project_id          | **27**                                                                                                                                              |
| regions             | **ID**                                                                                                                                              |
| metrics             | **从 defaults.json 的 metrics 字段读取（当前: order_cnt, gmv, gmv_995, ads_revenue_usd, abtest_region, gmv_per_uu, order_per_uu, gmv_per_uu_995）** |
| control_groups      | **31430, 31438**                                                                                                                                    |
| treatment_groups    | **31421, 31425**                                                                                                                                    |
| normalization       | **control**                                                                                                                                         |
| template_name       | One Page - Search Core Metric                                                                                                                       |
| template_group_name | (org+ads) by card                                                                                                                                   |
| dims                | abtest_group, abtest_region, abtest_date                                                                                                            |
| show_absolute       | **false**（默认只显示相对提升百分比）                                                                                                               |

### 调用规则

1. 用户说"帮我看看实验数据"→ **直接运行** `python /root/agent/skills/ab-platform/scripts/fetch_metrics.py`，不需要传任何参数，脚本自动使用上表默认值。
2. 用户说"看看前天的数据"→ 只需加 `--dates=2026-02-23,2026-02-23`，其余用默认值。
3. 用户说"看实验 15367"→ 只需 `python /root/agent/skills/ab-platform/scripts/fetch_metrics.py 15367`，其余用默认值。
4. 用户**显式指定**的参数会覆盖默认值。
5. **绝不要反问用户"实验 ID 是什么"或"要哪些指标"**——直接用默认值运行。

### 运行示例

```bash
# 最常用：不传任何参数，全部用默认值
python /root/agent/skills/ab-platform/scripts/fetch_metrics.py

# 指定日期范围
python /root/agent/skills/ab-platform/scripts/fetch_metrics.py --dates=2026-02-23,2026-02-23

# 指定其他实验
python /root/agent/skills/ab-platform/scripts/fetch_metrics.py 15367

# 需要绝对值时加 --absolute
python /root/agent/skills/ab-platform/scripts/fetch_metrics.py --absolute
```

## 默认输出格式

- **默认只显示相对提升百分比**（Treatment vs Control 的 lift），不显示绝对值，不显示 Control 组数据。
- 输出分两部分：
  1. **汇总（全部天数）** — 所有天数合计后的相对提升。
  2. **分天统计** — 每天各实验组相对 Control 的提升百分比。
- **桶名映射**：输出自动将数字 bucket ID（如 31421）映射为 `bucket_name.txt` 中的桶名（如 `bucket_id_00`），格式为 `bucket_id_00 (31421)`，方便快速识别。
- 若需要同时查看绝对值，传 `--absolute` 参数。
- JSON 模式 (`--json`) 额外包含 `daily_lifts`（分天结构化数据）和 `bucket_map`（桶名→数字 ID 完整映射表）。

### 桶号映射（必读）

完整映射表保存在 `/root/agent/skills/ab-platform/bucket_name.txt`，格式为 `bucket_id_XX\t数字ID`。当前映射：

| 桶名         | 数字 ID | 默认角色  |
| ------------ | ------- | --------- |
| bucket_id_00 | 31421   | treatment |
| bucket_id_01 | 31422   | —         |
| bucket_id_02 | 31423   | —         |
| bucket_id_03 | 31424   | —         |
| bucket_id_04 | 31425   | treatment |
| bucket_id_05 | 31426   | —         |
| bucket_id_06 | 31427   | —         |
| bucket_id_07 | 31428   | —         |
| bucket_id_08 | 31429   | —         |
| bucket_id_09 | 31430   | control   |
| bucket_id_10 | 31431   | —         |
| bucket_id_11 | 31432   | —         |
| bucket_id_12 | 31433   | —         |
| bucket_id_13 | 31434   | —         |
| bucket_id_14 | 31435   | —         |
| bucket_id_15 | 31436   | —         |
| bucket_id_16 | 31437   | —         |
| bucket_id_17 | 31438   | control   |
| bucket_id_18 | 29633   | —         |
| bucket_id_19 | 29632   | —         |

#### 用户提到桶号时的转换规则

用户可能用口语化方式提到桶，例如「03号桶」「04桶」「桶03和桶04」「bucket 03」等。**必须按以下规则解析**：

1. 提取用户说的数字部分（如"03号桶"→ `03`，"4号桶"→ `04`，"桶17"→ `17`）
2. 补零到两位，拼成 `bucket_id_XX`（如 `03` → `bucket_id_03`，`4` → `bucket_id_04`）
3. 查上表得到数字 ID（如 `bucket_id_03` → `31424`，`bucket_id_04` → `31425`）
4. 将数字 ID 传给脚本的 `--treatments` 或 `--control` 参数

**示例**：

- 用户说「查03号桶和04号桶的数据」→ `bucket_id_03=31424`、`bucket_id_04=31425` 作为 treatment，对照组用默认 control → 运行：
  ```bash
  python /root/agent/skills/ab-platform/scripts/fetch_metrics.py --treatments=31424,31425 --control=31430,31438
  ```
- 用户说「看看17号桶」→ `bucket_id_17=31438` 作为 treatment，对照组用默认 control → 运行：
  ```bash
  python /root/agent/skills/ab-platform/scripts/fetch_metrics.py --treatments=31438 --control=31430,31438
  ```
- 用户说「用09桶做对照看03桶」→ 明确指定了对照组，用 `bucket_id_09=31430` 做 control → 运行：
  ```bash
  python /root/agent/skills/ab-platform/scripts/fetch_metrics.py --treatments=31424 --control=31430
  ```

**注意**：

- 用户指定了特定桶时，将这些桶作为 `--treatments`，**对照组仍使用默认的两个 control 桶（31430, 31438）**，除非用户明确指定了其他对照组。
- 未指定的参数（实验 ID、指标等）仍用默认值。

### 呈现结果时必须包含桶名

向用户展示结果时，**必须保留脚本输出中的桶名（bucket name）**，不要只显示数字 ID。

**展示规则**：

- 每个桶的结果旁边都要标注桶名，格式：`bucket_id_03 (31424)`
- 不要省略桶名只写数字 ID
- 汇总结果时也要说明包含了哪些桶

## 默认指标

由 `defaults.json` 的 `metrics` 字段决定。**不要硬编码指标列表，始终让脚本自己从 defaults.json 读取**。运行时不传 `--metrics` 参数即可。

## 缓存

默认**不使用缓存**，每次直接请求 API。传 `--cache` 可启用本地缓存（缓存在 `.cache/` 目录，TTL 300 秒）。

## 运行环境

脚本兼容 **Python 2.7.18** 与 **Python 3.x**，可任选其一运行（如 `python2.7 scripts/...` 或 `python3 scripts/...`）。

## 代码结构

```
skills/ab-platform/
├── SKILL.md                 # 本说明
├── defaults.json            # 默认配置（用户未指定参数时使用）
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
