---
name: sra-ego-job-kanban
description: >
  Fetches EGO running job statistics (total count, queuing count, queuing duration) from the EGO Platform Job Kanban Grafana dashboard (EGO 运行任务看板统计).
  TRIGGER when: user wants running job stats, job kanban, queuing count/duration, "运行任务统计", "看板", "排队数", "排队时长", "running job count", "job queuing".
  DO NOT TRIGGER when: user wants job failure diagnosis, training metrics (AUC/gAUC), job submission, or local compile/run.
category: platform
tags: [ego, job, grafana, monitoring]
---

# EGO Running Job Kanban (EGO 运行任务看板统计)

## Scope and constraints

- **Data scope**: All data is from the **Ego SG Environment** (Ego Sg Env / Ego SG 环境). **Train job only** — release job data is not included (仅包含 train job，不包含 release job).
- **Data source**: Grafana dashboard **EGO Platform Job Kan Ban** (`ego-platform-job-kan-ban`). The skill pulls three block areas via Grafana API:
  1. **Running Job Count** (3 panels): running job count by dimension (运行任务数量).
  2. **Running Job Queuing in Soc** (4 panels): queuing count and duration in Soc (Soc 排队数量、排队时长).
  3. **Running Job Queuing in PS** (4 panels): queuing count and duration in PS (PS 排队数量、排队时长).
- **Output structure**:
  - **Part 1 — Running job count**: nested by platform → tenant → project (三层嵌套).
  - **Part 2 — Queuing**: two sub-parts (排队情况)
    - **Soc queuing**: tenant → project (排队数量、排队时长).
    - **PS queuing**: tenant → project (排队数量、排队时长).
- **Full fetch, filter on output**: When querying Grafana, **do not narrow by tenant/project**; always fetch full data (URL keeps `var-tenant=All&var-project=All`; script replaces `{tenant:sqlstring}` etc. with `1=1` so the query returns all rows). **Output-only filters** (Grafana request stays full): `--tenant` / `--project` (keep only listed values), **`--exclude-tenant`** (remove listed tenants from `blocks_raw` and `structured`). **Default** (no `--exclude-tenant` flag): exclude tenant **`mp_search_recommendation_ads.ego`** from output; pass **`--exclude-tenant`** with no values to keep all tenants in the summary. The skill applies the same defaults when presenting results.
- **User prompt shorthand → dashboard tenant keys**: Users often name business lines in short form. Map to **`--tenant`** values used under platform **`All`** in **Running Job Count** and **PS queuing** (short keys):
  - **ads** / **广告** → **`paidads`**
  - **rcmd** / **推荐** → **`recommendation`**
  - **search** / **搜索** → **`search`**
    **Soc queuing** panels often label tenants with **full** names (e.g. **`mp_search_recommendation_ads.paidads`** for the paidads line). To filter output for **both** running count and Soc for one business line, pass **both** the short key and the matching full Soc tenant when applicable (example: `--tenant paidads mp_search_recommendation_ads.paidads`).

## Output data semantics

**输出数据说明** — how to read `structured` fields:

- **Running job count**（运行任务数量）: **Instantaneous** at query time — a snapshot for “now”, **not** an average over the `from`–`to` window.
- **Soc / PS queuing — count and duration**（Soc/PS 排队数量、排队时长）: **Averages over the selected `from`–`to` range** (per-series mean aligned with Grafana panel **Mean**).
- **Queuing duration caveat**（排队时长参考性）: Treat **queuing duration as reference only**. Low-priority jobs can keep yielding to high-priority jobs, which may **inflate** average wait time over the window.

---

## Prerequisites and resources

- Environment variable **GRAFANA_API_TOKEN** (Grafana Bearer token) must be set. See [scripts/README.md](scripts/README.md).
- **Python 版本**：此 skill 的脚本按 **Python 3.9+** 使用；**不要用 Python 3.8**。原因：`scripts/get_job_kanban.py` 使用了 `tuple[str, ...]`、`dict | None`、`list[...]` 等较新 typing 语法，在 3.8 上会直接报 `TypeError: 'type' object is not subscriptable`。
- **Script**: **`scripts/get_job_kanban.py`** in this skill directory. Run from the **skill root** (`sra-ego-job-kanban`): `python3 scripts/get_job_kanban.py --url <full URL>` (requires **`httpx`** — see [scripts/README.md](scripts/README.md)).
- **Default dashboard URL** (overridable):  
  `https://monitoring.infra.sz.shopee.io/grafana/d/Xm1zlmcDz/ego-platform-job-kan-ban?var-cluster=kube-ego-manager-sg-ops4-live&var-namespace=live&var-env=live&var-tenant=All&var-project=All&var-zone=All&from=now-6h&to=now&orgId=38`

---

## Execution flow

### Step 1 — Resolve Grafana URL and time range

- If the user does not specify a URL, use the default above (cluster/namespace/env may be adjusted per user).
- Default time range is **`from=now-6h&to=now`**; user may override with `--from` / `--to`.

### Step 2 — Fetch kanban data

- Run **`python3 scripts/get_job_kanban.py --url <full URL>`** (optional: `--from`, `--to`, `--out-file`, **`--exclude-tenant`**, **`--omit-blocks-raw`**). By default the script uses **`now-6h` → `now`** and excludes tenant **`mp_search_recommendation_ads.ego`** from `blocks_raw` / `structured` (Grafana queries remain full-scope). Use **`--exclude-tenant`** with no following names to disable that default exclusion. If the user specified tenant or project, add **`--tenant T1 T2`** and/or **`--project P1 P2`** to filter output; the Grafana request still fetches full data. Use **`--omit-blocks-raw`** when the consumer only needs **`structured`** / metadata and wants a smaller file (not compatible with **`--no-summary`**).
- The script fetches all panels in the three blocks and outputs JSON including:
  - **`blocks_raw`**: per-block panel tables (columns/rows); omitted if **`--omit-blocks-raw`** (summary mode only),
  - **`structured`**: running job count (platform → tenant → project), Soc queuing (tenant → project: count + duration), PS queuing (tenant → project: count + duration),
  - **`panel_errors`**: failed panels (empty if all succeed),
  - **`filter_by`**: includes default **`exclude_tenant`** (`mp_search_recommendation_ads.ego`) unless cleared with bare **`--exclude-tenant`**; also records `--tenant` / `--project` / explicit `--exclude-tenant` lists when given (`null` only when no filters apply).

### Step 3 — Present results

- Output must include:
  - **Data source**: full Grafana dashboard link.
  - **Output semantics** (brief): running job count = **instantaneous**; Soc/PS queuing count and duration = **`from`–`to` averages**; queuing duration **reference-only** (priority yielding can stretch averages) — see [Output data semantics](#output-data-semantics).
  - **Running job count**: nested by platform → tenant → project (with totals / per-level summary).
  - **Soc queuing**: tenant → project, each with queuing count and duration.
  - **PS queuing**: tenant → project, each with queuing count and duration.
  - If **`panel_errors`** is non-empty, report those messages and still return any successful blocks/`structured` data.

---

## Conventions

- **Script only**: Call only **scripts/get_job_kanban.py**. Grafana token is provided only via the **GRAFANA_API_TOKEN** environment variable; **do not hardcode the token** in SKILL.md or the script.
- **Column inference**: The script infers structure from panel column names (e.g. platform, tenant, project, count, duration, queuing_count). If the dashboard changes column names, update the script’s column mapping.
- **Soc / PS queuing values**: Aimed to match Grafana panel legend **Mean** — per series, arithmetic mean of that series’ points over **`from`–`to`** (from raw `/api/ds/query` frames when possible). **Running job count** is **not** averaged that way; see [Output data semantics](#output-data-semantics). Not an average of Mean/Last/Max; not based on merging series with truncated row counts.
- **Prometheus wide columns**: Grafana may return one column per time series with a long name like `Value {__name__="...", job_id="...", ...}` (full label set). Those **per-job** columns are **dropped** from `blocks_raw` so JSON stays small; summaries use tenant/project-level series only.
- **Hidden queries**: Panel targets with Grafana **`hide: true`** are **not** sent to `/api/ds/query` (same as skipping hidden queries in the UI). SQL variable substitution in the script applies only to **panel `rawSql`** for datasource queries (template expansion), not to “collapsed row” or closed-view scraping.

---

## Errors and boundaries

- **GRAFANA_API_TOKEN not set**: Before step 2, tell the user to set it or prompt to set the variable and retry.
- **Grafana request fails** (e.g. 401/403/500): Report the error and stop; do not fabricate data.
- **Panel has no data or unexpected columns**: That panel may be omitted or marked “unparsed” in the structured summary; raw data is still kept in the output.
