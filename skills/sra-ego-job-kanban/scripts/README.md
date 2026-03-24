# sra-ego-job-kanban scripts

Fetches running job count and queuing stats from the **EGO Platform Job Kan Ban** Grafana dashboard (EGO 运行任务看板).  
**Note:** Data is from the **Ego SG environment** (Ego Sg Env / Ego SG 环境) only. **Train job only** — release job data is not fetched (仅包含 train job，不获取 release job；脚本会过滤 release 列并跳过仅 release 的 panel).  
Run from the **skill root** (`sra-ego-job-kanban/`): `python3 scripts/get_job_kanban.py ...`.

## Environment and token

- **Python 版本**：**必须使用 Python 3.9+**；**不要用 Python 3.8**。本脚本使用了 `tuple[str, ...]`、`dict | None`、`list[...]` 等语法，在 3.8 上会直接报 `TypeError: 'type' object is not subscriptable`。
- **Grafana token**: Must be set via the **`GRAFANA_API_TOKEN`** environment variable. Do not hardcode the token in the script or SKILL.
- **Dependencies**: `httpx`; run `pip install -r scripts/requirements.txt` (recommend using a venv under `scripts/`).

### `ModuleNotFoundError: No module named 'httpx'`

Your `python3` is the system interpreter without deps. Fix one of:

```bash
cd sra-ego-job-kanban
python3 -m pip install -r scripts/requirements.txt
python3 scripts/get_job_kanban.py --out-file result.json
```

Or use a venv (recommended):

```bash
cd sra-ego-job-kanban
python3 -m venv scripts/.venv
scripts/.venv/bin/pip install -r scripts/requirements.txt
export GRAFANA_API_TOKEN="..."   # your token
scripts/.venv/bin/python scripts/get_job_kanban.py --out-file result.json
```

## get_job_kanban.py

- **Full fetch, filter on output**: Requests to Grafana do not narrow by tenant/project (kept as All) so full data is fetched. To restrict by tenant or project, use **`--tenant T1 T2`** and/or **`--project P1 P2`** to filter the output only (查全量、输出时过滤). **User shorthand** (e.g. ads/广告 → `paidads`, rcmd/推荐 → `recommendation`, search/搜索 → `search`) and **Soc full tenant names** are documented in [SKILL.md](../SKILL.md) (Running Job Count / PS use short keys; Soc often uses `mp_search_recommendation_ads.*`).
- **Defaults**: Time range **`now-6h` → `now`** (default URL and URL parsing fallback). Output excludes tenant **`mp_search_recommendation_ads.ego`** unless you pass **`--exclude-tenant`** with **no** tenant names (that clears the default exclusion). Passing **`--exclude-tenant A B`** replaces the default list with exactly `A`, `B`, …
- **Arguments**: `--url` (optional, default SG live dashboard), `--from` / `--to` (time range), `--tenant` / `--project` (optional, multi-value, output filter), **`--exclude-tenant`** (see defaults above), `--out-file` (write JSON), **`--omit-blocks-raw`** (omit `blocks_raw` from JSON; use with default summary output; ignored with `--no-summary`), `--list-blocks` (list blocks and panel counts), `--no-summary` (raw panel data only). Token is only read from **GRAFANA_API_TOKEN**.
- **Blocks**: Running Job Count, Running Job Queuing in Soc, Running Job Queuing in PS.
- **Output**: JSON with `data_scope`, `source_url`, **`panel_errors`**, **`filter_by`** (usually includes default `exclude_tenant` unless cleared), `blocks_raw` (per-panel columns/rows per block), `structured` (running job count platform→tenant→project; Soc/PS queuing tenant→project with `queuing_count`, `queuing_duration`).

### Output data semantics

**输出数据说明** — field meanings:

- **`structured.running_job_count`**: **Instantaneous** snapshot at query time (运行任务数量 — 当前时刻瞬时值), not an average over `from`–`to`.
- **`structured.queuing_soc` / `structured.queuing_ps`**: **Queuing count** and **queuing duration** are **averages over `from`–`to`** (aligned with Grafana panel **Mean** per series; Soc/PS 排队数量、排队时长为时间范围内平均值).
- **Queuing duration**: **Reference only** — low-priority jobs may repeatedly yield to high-priority jobs, which can **lengthen** average queue duration in the window (排队时长仅作参考：低优持续让路高优可能拉高平均排队时长).

### Examples

```bash
export GRAFANA_API_TOKEN="your-grafana-bearer-token"

# Default URL (SG live, last 6h; output excludes mp_search_recommendation_ads.ego)
python3 scripts/get_job_kanban.py

# Include all tenants in output (disable default --exclude-tenant)
python3 scripts/get_job_kanban.py --exclude-tenant

# Custom URL and output file (e.g. last 24h)
python3 scripts/get_job_kanban.py --url "https://monitoring.infra.sz.shopee.io/grafana/d/Xm1zlmcDz/ego-platform-job-kan-ban?var-cluster=kube-ego-manager-sg-ops4-live&var-namespace=live&var-env=live&var-tenant=All&var-project=All&var-zone=All&from=now-24h&to=now&orgId=38" --out-file result.json

# List the three blocks and panel counts
python3 scripts/get_job_kanban.py --list-blocks

# Full fetch, then filter output by tenant/project
python3 scripts/get_job_kanban.py --tenant my-tenant --project proj-a proj-b --out-file filtered.json

# Drop specific tenants only (replaces default exclude list)
python3 scripts/get_job_kanban.py --exclude-tenant some.tenant other.tenant --out-file result.json
```

### If you get HTTP 401/403/500

Ensure `GRAFANA_API_TOKEN` is valid for the org (e.g. orgId=38) and has query permission for the datasource. Compare with the browser Network tab for `/api/ds/query` on the same dashboard if needed.

### Running Job Queuing in Soc — empty rows

If **Soc** panels have columns but **rows** are empty, Grafana may have no data in that time range (e.g. no queuing in the default 6h window). Try `--from now-7d` or `--from now-24h`.

### Running Job Queuing in PS — HTTP 400/422 (VictoriaMetrics)

The PS backend is **VictoriaMetrics** (or compatible). VM rejects PromQL where **`\.` appears inside the `=~ "..."` string** (`cannot parse string literal` / **422**). The script expands multi-value variables with **`[.]` for literal dots** (e.g. `marketplace[.]mpi`) instead of `\.`. If 422 persists, check the error body from Grafana and datasource health.

### Soc / PS data notes

- **Queuing numbers**: Aimed to match Grafana panel legend **Mean** per series over **`from`–`to`** (from raw `/api/ds/query` frames when possible). **Running job count** in `structured` is **instantaneous**, not this average — see [Output data semantics](#output-data-semantics) above.
- **Soc**: Tenant names may differ from Running Job Count; both are kept as returned by the dashboard.
- **PS**: If all PS panels fail with 422, `queuing_ps` may be empty until the PromQL/datasource issue is resolved.
