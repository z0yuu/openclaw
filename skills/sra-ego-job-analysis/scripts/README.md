# sra-ego-train-job-analysis scripts

位于 **skill/sra-ego-train-job-analysis/scripts/**（EGO 训练效果指标对比）。工作目录为 **skill 根目录**（sra-ego-train-job-analysis/）时调用：`python scripts/<脚本> ...`。

## Python 版本要求

- **必须使用 Python 3.9+**。
- **不要用 Python 3.8**：本目录脚本使用了 `dict[str, str]`、`list[str]`、`dict | None` 等较新的 typing 语法；在 3.8 上会报 `TypeError: 'type' object is not subscriptable`。
- 如果系统默认 `python3` 还是 3.8，先显式切到 3.9+ 再执行本 skill，避免再踩一次。

## EGO API 脚本（步骤 1～6）

- **train_job.py**：`list`（按 job_name 等）、`get <job_id>`，对应 references/train_job.md。
- **model.py**：`list`（按 model_name、scope 等）、`get <model_id>`，对应 references/model.md。
- **model_version.py**：`list <model_id>`（按 version_name 等）、`get <model_id> <version_id>`，对应 references/model_version.md。
- **\_common.py**：上述脚本共用认证与 HTTP，勿删。环境变量 **USER_ID_OPENAPI**（必填）；**EGO_BASE_URL**（可选）。依赖：`httpx`。

示例（工作目录 = skill 根目录）：

```bash
export USER_ID_OPENAPI=your_token
python scripts/train_job.py list --job_name "my-job"
python scripts/train_job.py get 123
python scripts/model.py list --model_name "my-model" --scope 2
python scripts/model.py get 10
python scripts/model_version.py list 10 --version_name "v1"
python scripts/model_version.py get 10 1
```

---

## get_train_auc.py（步骤 7）

- **入参**：上层传入已组装好所有 URL 参数的完整 Grafana dashboard link（`--url`），脚本从中解析 base、UID、orgId 及全部查询变量（URL 中仅 `orgId`、`from`、`to` 非模板变量，其余为 var-\*）。
- **区块**：`--block versioned`（默认）/ `job` / `both`，对应 Versioned-level、Job-level Model Performance Comparison 或两个都拉取。
- **默认**：只获取 "Auc Per Day"、"gAUC Per Day" 两个 panel。
- **可选**：`--all-panels` 获取该区块下所有 panel；`--panels "Title1" "Title2"` 指定 panel。
- **输出**：JSON（按 panel 分组，每 panel 含 `columns`、`rows`，列名带 labels 时格式为 `name {key="value", ...}`）或 table。

### 环境与依赖

在 **scripts** 目录下创建 venv 并安装依赖（推荐）：

```bash
cd skill/sra-ego-train-job-analysis/scripts
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 使用

```bash
export GRAFANA_API_TOKEN="your-grafana-bearer-token"

# 在 scripts 目录下执行
cd skill/sra-ego-train-job-analysis/scripts
python get_train_auc.py --url "https://monitoring.infra.sz.shopee.io/grafana/d/B6FNSQHVz/ego-train-v1-multiple-models-comparison?orgId=38&var-model_names=product-rank-v3&var-model_versions=prd-i-uni-l2&var-job_names=All&var-rounds=All&var-targets=TW_pp_direct_pcr_7d&var-targets=TW_pp_shop_pcr_7d&var-mysql_datasource=EGO-Train-MySQL&from=now-90d&to=now&var-tag=None&var-xgauc_path=gauc.int64_user_id&var-job_types=train"

# 使用 venv 中的 Python
.venv/bin/python get_train_auc.py --url "<同上>" ...

# 输出到当前目录 result.json
python get_train_auc.py --url "<同上>" --out-file result.json

# 仅拉取 Job-level 区块并落盘
.venv/bin/python get_train_auc.py --url "<同上>" --block job --out-file result_job.json

# 列出 dashboard 中所有区块及 panel 数量（排查用）
.venv/bin/python get_train_auc.py --url "<同上>" --list-blocks
```

### 选项

| 选项                 | 说明                                                       |
| -------------------- | ---------------------------------------------------------- |
| `--url`              | 必填。完整 dashboard URL（含所有 var-\*、from、to）        |
| `--token`            | Grafana Bearer token，不传则用环境变量 `GRAFANA_API_TOKEN` |
| `--block`            | 区块：`versioned`（默认）、`job`、`both`                   |
| `--all-panels`       | 拉取该区块下所有 panel                                     |
| `--panels TITLE ...` | 只拉取指定标题的 panel                                     |
| `--from` / `--to`    | 覆盖 URL 中的时间范围（如 `now-7d`、`now`）                |
| `--output`           | `json`（默认）或 `table`                                   |
| `--out-file`         | 写入文件路径，不传则打印到 stdout                          |
| `--list-blocks`      | 仅列出 dashboard 中所有 row 区块标题及 panel 数量后退出    |
| `--verbose`          | 打印关键请求与 All 解析信息                                |
| `--debug`            | 打印简要步骤与各 panel 行列数，便于排查                    |

### 若出现 HTTP 500 "Query data error"

1. 用 `--verbose`、`--debug` 查看请求与 panel 结果摘要。
2. 与浏览器打开同一 dashboard 时 Network 里对 `/api/ds/query` 的 POST 对比（body、headers）。
3. 查看 Grafana/MySQL 日志中的具体报错；确认 `GRAFANA_API_TOKEN` 在该 org 下有该 datasource 的查询权限。
