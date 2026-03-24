#!/usr/bin/env python3
"""
EGO Platform Job Kanban — 从 Grafana 拉取运行任务数量与排队统计，并输出嵌套结构。

区块：Running Job Count、Running Job Queuing in Soc、Running Job Queuing in PS。
JSON：blocks_raw（可用 --omit-blocks-raw 省略）、structured、panel_errors、filter_by（与 CLI 过滤参数对应）。
排队：Soc/PS 优先按原始 query 帧逐序列计算均值，对齐面板图例 Mean（非 Mean/Last/Max 混算，非 min 行数截断后的宽表均值）。
依赖：httpx（requirements.txt）。Token 仅环境变量 GRAFANA_API_TOKEN。
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from urllib.parse import parse_qs, urlparse

try:
    import httpx
except ModuleNotFoundError as e:
    if e.name != "httpx":
        raise
    print(
        "Error: httpx is not installed. From the skill root (sra-ego-job-kanban/), run one of:\n"
        "  python3 -m pip install -r scripts/requirements.txt\n"
        "  python3 -m venv scripts/.venv && scripts/.venv/bin/pip install -r scripts/requirements.txt\n"
        "Then use: scripts/.venv/bin/python scripts/get_job_kanban.py ...",
        file=sys.stderr,
    )
    raise SystemExit(1) from e

# 看板三个区块标题（与 Grafana 中 row title 一致）
BLOCK_RUNNING_COUNT = "Running Job Count"
BLOCK_QUEUING_SOC = "Running Job Queuing in Soc"
BLOCK_QUEUING_PS = "Running Job Queuing in PS"
BLOCK_TITLES = [BLOCK_RUNNING_COUNT, BLOCK_QUEUING_SOC, BLOCK_QUEUING_PS]

# Fallback: known Prometheus DS uid and id for PS when cluster=kube-ego-manager-sg-ops4-live (from dashboard/curl)
PS_CLUSTER_OPS4_LIVE_UID = "zLSLhCfHk"
PS_DATASOURCE_ID = 15131

# PS panel exprs use: $env, $cluster, $tenant, $project, $zone (substituted from URL/dashboard vars).
# Soc panel exprs use: $project, $zone.

NON_VAR_PARAMS = ("from", "to", "orgId")


def _prom_label_regex_esc(s: str) -> str:
    """Escape for VictoriaMetrics/Prometheus label regex inside =~ \"...\" (see build_ds_query_body)."""
    return str(s).replace("\\", "\\\\").replace("|", "\\|").replace(".", "[.]")


DEFAULT_RELATIVE_FROM = "now-6h"

DEFAULT_EXCLUDE_TENANTS: tuple[str, ...] = ("mp_search_recommendation_ads.ego",)

DEFAULT_DASHBOARD_URL = (
    "https://monitoring.infra.sz.shopee.io/grafana/d/Xm1zlmcDz/ego-platform-job-kan-ban"
    "?var-cluster=kube-ego-manager-sg-ops4-live&var-namespace=live&var-env=live"
    f"&var-tenant=All&var-project=All&var-zone=All&from={DEFAULT_RELATIVE_FROM}&to=now&orgId=38"
)


def parse_relative_time(s: str) -> int:
    """将 Grafana 相对时间如 now、now-6h 转为毫秒时间戳。"""
    s = (s or "").strip()
    now = datetime.now(timezone.utc)
    if s == "now":
        return int(now.timestamp() * 1000)
    m = re.match(r"now-(\d+)([smhd])", s, re.I)
    if not m:
        raise ValueError(f"Unsupported time format: {s!r}")
    num, unit = int(m.group(1)), m.group(2).lower()
    if unit == "s":
        delta = timedelta(seconds=num)
    elif unit == "m":
        delta = timedelta(minutes=num)
    elif unit == "h":
        delta = timedelta(hours=num)
    else:
        delta = timedelta(days=num)
    t = now - delta
    return int(t.timestamp() * 1000)


def parse_url(url: str) -> dict:
    """从完整 URL 解析 base、UID、orgId、query 参数。"""
    parsed = urlparse(url)
    path = (parsed.path or "").rstrip("/")
    parts = [p for p in path.split("/") if p]
    uid = ""
    for i, part in enumerate(parts):
        if part == "d" and i + 1 < len(parts):
            uid = parts[i + 1]
            break
    if not uid:
        for part in parts:
            if len(part) == 9 and (part.startswith("B") or part.startswith("X")):
                uid = part
                break
    if not uid:
        for part in parts:
            if len(part) >= 8 and part.replace("-", "").isalnum():
                uid = part
                break
    if not uid:
        raise ValueError(f"Could not find dashboard UID in path: {path}")

    base_path = "/" + parts[0] if parts else ""
    base = f"{parsed.scheme}://{parsed.netloc}{base_path}".rstrip("/")
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    out = {}
    for k, v in query_params.items():
        v = [x for x in v if x is not None and str(x).strip() != ""]
        if not v:
            continue
        out[k] = v[0] if len(v) == 1 else v

    org_id = out.get("orgId") or "1"
    from_ts = out.get("from", DEFAULT_RELATIVE_FROM)
    to_ts = out.get("to", "now")
    if isinstance(from_ts, list):
        from_ts = from_ts[0]
    if isinstance(to_ts, list):
        to_ts = to_ts[0]
    from_ms = parse_relative_time(str(from_ts))
    to_ms = parse_relative_time(str(to_ts))

    return {
        "base": base,
        "uid": uid,
        "org_id": org_id,
        "query_params": out,
        "from_ms": from_ms,
        "to_ms": to_ms,
    }


def get_dashboard(
    client: httpx.Client, base: str, uid: str, org_id: str, token: str, query_params: dict | None = None
) -> dict:
    """GET /api/dashboards/uid/:uid。"""
    url = f"{base}/api/dashboards/uid/{uid}"
    params = None
    if query_params:
        params = {}
        for k, v in query_params.items():
            if isinstance(v, list):
                params[k] = ",".join(str(x) for x in v)
            else:
                params[k] = v
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Grafana-Org-Id": str(org_id),
    }
    resp = client.get(url, params=params, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    if "dashboard" not in data:
        raise ValueError("Dashboard response missing 'dashboard' key")
    return data["dashboard"]


def get_datasources(client: httpx.Client, base: str, org_id: str, token: str) -> list:
    """GET /api/datasources。"""
    url = f"{base}/api/datasources"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Grafana-Org-Id": str(org_id),
    }
    resp = client.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_datasource_by_name(client: httpx.Client, base: str, org_id: str, token: str, name: str) -> dict | None:
    """GET /api/datasources/name/:name。"""
    if not name or not isinstance(name, str):
        return None
    url = f"{base}/api/datasources/name/{name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Grafana-Org-Id": str(org_id),
    }
    try:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def get_datasource_by_uid(client: httpx.Client, base: str, org_id: str, token: str, uid: str) -> dict | None:
    """GET /api/datasources/uid/:uid。"""
    if not uid or not isinstance(uid, str) or (uid.startswith("${") and uid.endswith("}")):
        return None
    url = f"{base}/api/datasources/uid/{uid}"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Grafana-Org-Id": str(org_id),
    }
    try:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def resolve_datasource(ds, query_params: dict, name_to_ds: dict) -> dict | None:
    """将 panel 的 datasource 解析为 { type, uid, id? }。"""
    if isinstance(ds, dict):
        uid = ds.get("uid")
        if uid and isinstance(uid, str):
            if uid.startswith("${") and uid.endswith("}"):
                var_name = uid[2:-1].strip()
                name = query_params.get(var_name) or query_params.get("var-" + var_name)
                if isinstance(name, list):
                    name = name[0] if name else None
                if name and name in name_to_ds:
                    return name_to_ds[name]
                if name:
                    for _key, info in name_to_ds.items():
                        if not isinstance(info, dict):
                            continue
                        n, u = str(info.get("name") or ""), str(info.get("uid") or "")
                        if name == n or name == u or (name in n) or (name in u) or name == _key or (name in str(_key)):
                            return info
            elif uid in name_to_ds:
                return name_to_ds[uid]
        return ds
    if isinstance(ds, str) and ds in name_to_ds:
        return name_to_ds[ds]
    return None


def find_block_panels(dashboard: dict, block_title: str) -> list:
    """Find the row with title matching block_title (case-insensitive) and return its panels."""
    panels = dashboard.get("panels") or []
    want = (block_title or "").strip().lower()
    for idx, p in enumerate(panels):
        if p.get("type") != "row":
            continue
        row_title = (p.get("title") or "").strip().lower()
        if row_title != want:
            continue
        nested = p.get("panels") or []
        if nested:
            return nested
        out = []
        for i in range(idx + 1, len(panels)):
            next_p = panels[i]
            if next_p.get("type") == "row":
                break
            out.append(next_p)
        return out
    return []


def _sql_escape_single(s: str) -> str:
    return "'" + str(s).replace("\\", "\\\\").replace("'", "''") + "'"


def _ms_to_iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:23] + "Z"


def _substitute_sql_macros(raw_sql: str, from_ms: int, to_ms: int, query_params: dict) -> str:
    """Expand ${var} in panel MySQL rawSql the same way Grafana does for /api/ds/query.

    This is not parsing SQL from collapsed/hidden dashboard rows; it only substitutes
    template variables into explicit panel targets.
    """
    if not raw_sql or not isinstance(raw_sql, str):
        return raw_sql
    sql = raw_sql
    # ${var:sqlstring} / {var:sqlstring}: when value is a list (e.g. expanded All), use 'a','b','c'; when All not expanded use 1=1
    for k, v in query_params.items():
        if k in NON_VAR_PARAMS:
            continue
        var_name = k.replace("var-", "", 1) if k.startswith("var-") else k
        if isinstance(v, list) and len(v) > 0 and not (len(v) == 1 and v[0] in ("All", "$__all")):
            literal = ",".join(_sql_escape_single(x) for x in v)
            for pattern in [rf"\$\{{{re.escape(var_name)}:[^}}]+\}}", rf"\{{{re.escape(var_name)}:[^}}]+\}}"]:
                sql = re.sub(pattern, literal, sql)
        elif v == "All" or v == "$__all" or (isinstance(v, list) and len(v) == 1 and v[0] in ("All", "$__all")):
            for pattern in [rf"\$\{{{re.escape(var_name)}:[^}}]+\}}", rf"\{{{re.escape(var_name)}:[^}}]+\}}"]:
                sql = re.sub(pattern, "1=1", sql)
    for k, v in query_params.items():
        if k in NON_VAR_PARAMS:
            continue
        var_name = k.replace("var-", "", 1) if k.startswith("var-") else k
        if isinstance(v, list):
            literal = ",".join(_sql_escape_single(x) for x in v)
        else:
            literal = _sql_escape_single(v)
        for pattern_name in [var_name, k]:
            sql = re.sub(r"\$\{" + re.escape(pattern_name) + r"\}", literal, sql)
            sql = re.sub(r"\$" + re.escape(pattern_name) + r"\b", literal, sql)
    # Replace any remaining ${...} with 1=1; avoid invalid "IN (1=1)" by replacing whole "IN (${...})" with "1=1"
    sql = re.sub(r"\bIN\s*\(\s*\$\{[^}]+\}\s*\)", "1=1", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\$\{[^}]+\}", "1=1", sql)
    return sql


def build_ds_query_body(
    panel: dict, from_ms: int, to_ms: int, query_params: dict, name_to_ds: dict, skip_sql_substitution: bool = False
) -> dict:
    """从 panel targets 构建 POST /api/ds/query body。skip_sql_substitution=True 时不替换变量，直接使用 panel 原始 query（用于 500 重试）。"""
    ds_resolved = resolve_datasource(panel.get("datasource"), query_params, name_to_ds)
    if not ds_resolved:
        ds_resolved = panel.get("datasource")
    if isinstance(ds_resolved, dict) and (ds_resolved.get("uid") or "").startswith("${"):
        cluster_val = query_params.get("cluster") or query_params.get("var-cluster")
        if isinstance(cluster_val, list):
            cluster_val = cluster_val[0] if cluster_val else None
        if str(cluster_val or "") == "kube-ego-manager-sg-ops4-live":
            ds_resolved = {"type": "prometheus", "uid": PS_CLUSTER_OPS4_LIVE_UID, "id": None}

    targets = panel.get("targets") or []
    # Grafana: target.hide skips the query in the UI; do not POST hidden queries.
    visible_targets = [t for t in targets if not (isinstance(t, dict) and t.get("hide"))]
    if not visible_targets:
        return {"queries": [], "from": str(from_ms), "to": str(to_ms)}

    queries = []
    for i, t in enumerate(visible_targets):
        q = dict(t) if isinstance(t, dict) else {"refId": "A", "rawSql": t}
        if "refId" not in q:
            q["refId"] = "A" if i == 0 else chr(ord("A") + i)
        if q.get("rawSql") and not skip_sql_substitution:
            q["rawSql"] = _substitute_sql_macros(q["rawSql"], from_ms, to_ms, query_params)
        if q.get("expr") and isinstance(q["expr"], str) and not skip_sql_substitution:
            for k, v in query_params.items():
                if k in NON_VAR_PARAMS:
                    continue
                var_name = k.replace("var-", "", 1) if k.startswith("var-") else k
                if isinstance(v, list) and len(v) == 1 and str(v[0]) not in ("All", "$__all"):
                    val = str(v[0])
                elif isinstance(v, list) and len(v) > 1:
                    val = "(" + "|".join(_prom_label_regex_esc(x) for x in v) + ")"
                else:
                    val = ",".join(str(x) for x in v) if isinstance(v, list) else str(v)
                    if val in ("All", "$__all", ""):
                        val = ".*"
                # ${var}, ${var:regex} and $var (single value = literal e.g. server_env="live", multi = regex)
                q["expr"] = re.sub(r"\$\{" + re.escape(var_name) + r"(?::[^}]*)?\}", val, q["expr"])
                q["expr"] = re.sub(r"\$" + re.escape(var_name) + r"\b", val, q["expr"])
            q["expr"] = re.sub(r"\$\{[^}]+\}", ".*", q["expr"])
        if isinstance(ds_resolved, dict):
            q["datasource"] = {"type": ds_resolved.get("type") or "prometheus", "uid": ds_resolved.get("uid")}
        else:
            q.setdefault("datasource", ds_resolved)
        q.setdefault("intervalMs", 60000)
        q.setdefault("maxDataPoints", 1888)
        if isinstance(ds_resolved, dict) and ds_resolved.get("id") is not None:
            q["datasourceId"] = int(ds_resolved["id"])
        elif isinstance(ds_resolved, dict) and ds_resolved.get("uid") == PS_CLUSTER_OPS4_LIVE_UID:
            q["datasourceId"] = PS_DATASOURCE_ID
        if q.get("expr"):
            q.setdefault("exemplar", True)
            q.setdefault("queryType", "timeSeriesQuery")
            q.setdefault("instant", False)
            q.setdefault("hide", False)
            q.setdefault("legendFormat", "{{tenant_name}}")
            if "requestId" not in q:
                q["requestId"] = f"{panel.get('id', 0)}{q.get('refId', 'A')}"
            q.setdefault("utcOffsetSec", 28800)
            q.setdefault("interval", "")
        queries.append(q)

    return {
        "queries": queries,
        "from": str(from_ms),
        "to": str(to_ms),
        "range": {
            "from": _ms_to_iso(from_ms),
            "to": _ms_to_iso(to_ms),
            "raw": {"from": str(query_params.get("from", DEFAULT_RELATIVE_FROM)), "to": str(query_params.get("to", "now"))},
        },
    }


def _field_display_name(f: dict) -> str:
    name = f.get("name") or f.get("displayName") or "unknown"
    labels = f.get("labels")
    if labels and isinstance(labels, dict):
        parts = ", ".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        name = f"{name} {{{parts}}}"
    return name


def _frame_to_columns_rows(frame: dict) -> tuple[list, list]:
    """Extract (columns, rows) from one Grafana frame. Handles: schema+data.values; data.values as dict; top-level fields[].values; schema.fields[].values (values per field). For (Time, Value) frames with no labels on Value, use frame name so multiple series get distinct keys."""
    schema = frame.get("schema") or {}
    fields = schema.get("fields") or []
    if not fields:
        raw_fields = frame.get("fields") or []
        if raw_fields:
            cols = [str(f.get("name") or f.get("displayName") or "unknown") for f in raw_fields]
            vals = []
            for f in raw_fields:
                v = f.get("values")
                if v is not None and isinstance(v, list):
                    vals.append(v)
                else:
                    vals.append([])
            if vals:
                n_rows = max(len(v) for v in vals) if vals else 0
                rows = [[vals[c][r] if r < len(vals[c]) else None for c in range(len(vals))] for r in range(n_rows)]
                return cols, rows
        return [], []
    columns = [_field_display_name(f) for f in fields]
    # So multiple (Time, Value) frames get distinct keys: use frame name when Value field has no labels
    def _col_norm(c):
        s = (str(c) if c else "").strip().lower()
        return s.split("{")[0].strip() if "{" in s else s
    if len(columns) == 2 and _col_norm(columns[0]) == "time" and _col_norm(columns[1]) == "value":
        if not (fields[1].get("labels") and isinstance(fields[1]["labels"], dict)):
            meta = frame.get("meta") or {}
            custom = meta.get("custom") or {}
            frame_name = (
                frame.get("name")
                or custom.get("displayName")
                or custom.get("seriesName")
                or meta.get("displayName")
            )
            if frame_name and str(frame_name).strip():
                columns = [columns[0], f'Value {{tenant_name="{frame_name}"}}']
    data = frame.get("data") or {}
    col_vals = data.get("values")
    if col_vals is None:
        col_vals = []
    if isinstance(col_vals, dict):
        col_vals = [col_vals.get(str(i)) or col_vals.get(i) or [] for i in range(len(fields))]
    if not isinstance(col_vals, list):
        col_vals = []
    if not col_vals or len(col_vals) == 0:
        col_vals = [f.get("values") or [] for f in fields]
        if not isinstance(col_vals[0], list):
            col_vals = []
    if col_vals and len(col_vals) > 0:
        n_cols = min(len(fields), len(col_vals))
        n_rows = max(len(col_vals[c]) for c in range(n_cols)) if n_cols else 0
        rows = [[col_vals[c][r] if c < len(col_vals) and r < len(col_vals[c]) else None for c in range(n_cols)] for r in range(n_rows)]
        return columns, rows
    return columns, []


def _series_to_rows(series_list: list) -> tuple[list, list]:
    """Legacy format: list of { name, points: [[ts, val], ...] } or { datapoints: [[val, ts], ...] }. Returns (columns, rows)."""
    if not series_list:
        return ["Time", "Value"], []
    rows = []
    for s in series_list:
        points = s.get("points") or s.get("datapoints") or []
        for p in points:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                ts, val = p[0], p[1]
                rows.append([ts, val])
            else:
                rows.append([None, p])
    return ["Time", "Value"], rows


def _merge_timeseries_frames(all_rows_by_columns_key: dict) -> dict:
    """When multiple frames are each (Time + single Value column), merge into one wide table so all tenants/series appear. Returns merged entry or None."""
    ts_frames = []
    for key, data in all_rows_by_columns_key.items():
        cols = data["columns"]
        rows = data["rows"]
        if len(cols) != 2 or not rows:
            continue
        if _normalize_col(cols[0]) != "time":
            continue
        ts_frames.append({"columns": cols, "rows": rows})
    if len(ts_frames) < 2:
        return None
    # Build wide: [Time, Val1, Val2, ...]; align rows by index (use min length to avoid index error)
    time_col = "Time"
    merged_cols = [time_col]
    for f in ts_frames:
        merged_cols.append(f["columns"][1])
    n_rows = min(len(f["rows"]) for f in ts_frames)
    merged_rows = []
    for i in range(n_rows):
        row = []
        t = ts_frames[0]["rows"][i][0] if i < len(ts_frames[0]["rows"]) else None
        row.append(t)
        for f in ts_frames:
            rws = f["rows"]
            v = rws[i][1] if i < len(rws) and len(rws[i]) > 1 else None
            row.append(v)
        merged_rows.append(row)
    return {"columns": merged_cols, "rows": merged_rows}


def _is_plain_timeseries(columns: list) -> bool:
    """True only if columns are exactly [Time, Value] with no {labels} in the value column name.

    If Value carries Grafana labels (e.g. Value {tenant_name="x"}), must be False so frames merge
    via _merge_timeseries_frames; otherwise all such frames are misrouted to plain_ts_frames and
    min(row count) can become 0 when an exemplar/empty frame is included.
    """
    if not columns or len(columns) != 2:
        return False
    if "{" in str(columns[1]):
        return False
    c0 = (str(columns[0]) or "").strip().lower()
    if "{" in c0:
        c0 = c0.split("{")[0].strip()
    c1 = (str(columns[1]) or "").strip().lower()
    return c0 == "time" and c1 == "value"


def frames_to_structured(response: dict) -> dict:
    """Convert Grafana results/frames to { columns, rows }. Supports frames API and legacy series/datapoints. Merges multiple time-series frames (one series per frame) into one wide table."""
    results = response.get("results") or {}
    best_columns = []
    best_rows = []
    first_frame_columns = []
    all_rows_by_columns_key = {}
    plain_ts_frames = []
    for ref_data in results.values():
        if ref_data.get("error"):
            continue
        for frame in ref_data.get("frames") or []:
            meta = (frame.get("schema") or {}).get("meta") or {}
            if (meta.get("custom") or {}).get("resultType") == "exemplar":
                continue
            columns, rows = _frame_to_columns_rows(frame)
            if not columns:
                continue
            if not first_frame_columns:
                first_frame_columns = columns
            if _is_plain_timeseries(columns):
                plain_ts_frames.append({"columns": columns, "rows": rows, "frame": frame})
                continue
            key = tuple(columns)
            if key not in all_rows_by_columns_key:
                all_rows_by_columns_key[key] = {"columns": columns, "rows": []}
            all_rows_by_columns_key[key]["rows"].extend(rows)
        series = ref_data.get("series") or ref_data.get("tables")
        if series:
            cols, rows = _series_to_rows(series if isinstance(series, list) else [series])
            if not first_frame_columns:
                first_frame_columns = cols
            key = tuple(cols)
            if key not in all_rows_by_columns_key:
                all_rows_by_columns_key[key] = {"columns": cols, "rows": []}
            all_rows_by_columns_key[key]["rows"].extend(rows)
    non_empty_plain = [item for item in plain_ts_frames if item.get("rows")]
    if len(non_empty_plain) >= 2:
        merged_cols = ["Time"]
        for i, item in enumerate(non_empty_plain):
            name = (item.get("frame") or {}).get("name") or (item.get("frame") or {}).get("meta", {}).get("custom", {}).get("displayName")
            merged_cols.append(f'Value {{tenant_name="{name}"}}' if name and str(name).strip() else f"Value_{i}")
        n_rows = min(len(item["rows"]) for item in non_empty_plain)
        merged_rows = []
        for i in range(n_rows):
            row = [non_empty_plain[0]["rows"][i][0]]
            for item in non_empty_plain:
                rws = item["rows"]
                row.append(rws[i][1] if i < len(rws) and len(rws[i]) > 1 else None)
            merged_rows.append(row)
        all_rows_by_columns_key[tuple(merged_cols)] = {"columns": merged_cols, "rows": merged_rows}
    elif len(non_empty_plain) == 1:
        item = non_empty_plain[0]
        key = tuple(item["columns"])
        all_rows_by_columns_key[key] = {"columns": item["columns"], "rows": list(item["rows"])}
    elif len(plain_ts_frames) == 1:
        item = plain_ts_frames[0]
        key = tuple(item["columns"])
        all_rows_by_columns_key[key] = {"columns": item["columns"], "rows": list(item["rows"])}
    merged = _merge_timeseries_frames(all_rows_by_columns_key)
    if merged:
        all_rows_by_columns_key[tuple(merged["columns"])] = merged
    # Prefer wide merged time series (Time + N value columns) over a single series that has +1 row
    if merged and len(merged["columns"]) > 2:
        best_columns = merged["columns"]
        best_rows = merged["rows"]
    else:
        for key, data in all_rows_by_columns_key.items():
            rws = data["rows"]
            if len(rws) > len(best_rows):
                best_columns = data["columns"]
                best_rows = rws
    if not best_columns and first_frame_columns:
        best_columns = first_frame_columns
    return {"columns": best_columns, "rows": best_rows}


def fetch_variable_options(
    client: httpx.Client,
    base: str,
    org_id: str,
    token: str,
    var_def: dict,
    query_params: dict,
    from_ms: int,
    to_ms: int,
    name_to_ds: dict,
) -> list:
    """Run the variable's query (POST /api/ds/query) and return the list of option values. Used when dashboard API does not return options."""
    var_type = (var_def.get("type") or "").lower()
    if var_type != "query":
        return []
    raw_sql = var_def.get("query") or var_def.get("definition") or var_def.get("rawQuery")
    if isinstance(raw_sql, dict):
        raw_sql = raw_sql.get("query") or raw_sql.get("rawSql") or raw_sql.get("definition") or ""
    if not raw_sql or not isinstance(raw_sql, str) or not raw_sql.strip():
        return []
    ds = var_def.get("datasource")
    ds_resolved = resolve_datasource(ds, query_params, name_to_ds) if ds else None
    if not ds_resolved and isinstance(ds, dict):
        ds_resolved = ds
    if not ds_resolved:
        return []
    sql = _substitute_sql_macros(raw_sql.strip(), from_ms, to_ms, query_params)
    body = {
        "queries": [
            {
                "refId": "A",
                "rawSql": sql,
                "datasource": ds_resolved,
                "format": "table",
                "intervalMs": 10800000,
                "maxDataPoints": 820,
            }
        ],
        "from": str(from_ms),
        "to": str(to_ms),
        "range": {
            "from": _ms_to_iso(from_ms),
            "to": _ms_to_iso(to_ms),
            "raw": {"from": str(query_params.get("from", DEFAULT_RELATIVE_FROM)), "to": str(query_params.get("to", "now"))},
        },
    }
    if isinstance(ds_resolved, dict) and ds_resolved.get("id") is not None:
        body["queries"][0]["datasourceId"] = int(ds_resolved["id"])
    url = f"{base}/api/ds/query"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Grafana-Org-Id": str(org_id),
    }
    ds_type = (ds_resolved.get("type") or "mysql").lower() if isinstance(ds_resolved, dict) else "mysql"
    params = {"ds_type": ds_type, "requestId": "var-options"}
    try:
        resp = client.post(url, params=params, json=body, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []
    results = data.get("results") or {}
    ref_data = results.get("A") or {}
    frames = ref_data.get("frames") or []
    values = []
    for frame in frames:
        fields = (frame.get("schema") or {}).get("fields") or []
        col_vals = (frame.get("data") or {}).get("values") or []
        if not fields or not col_vals:
            continue
        for v in col_vals[0]:
            if v is None:
                continue
            s = str(v).strip()
            if s and s not in ("__all", "$__all", ""):
                values.append(v)
    return values


def resolve_all_from_dashboard(
    client: httpx.Client,
    dashboard: dict,
    query_params: dict,
    base: str,
    org_id: str,
    token: str,
    from_ms: int,
    to_ms: int,
    name_to_ds: dict,
) -> dict:
    """Expand URL vars that are All into full option list (from dashboard options or variable query)."""
    tlist = dashboard.get("templating")
    var_list = tlist if isinstance(tlist, list) else (tlist or {}).get("list", [])
    name_to_options = {}
    for var in var_list:
        name = var.get("name")
        if not name:
            continue
        values = []
        for o in var.get("options") or []:
            v = o.get("value")
            if v is None:
                continue
            s = str(v)
            if s in ("__all", "$__all", ""):
                continue
            values.append(v)
        if values:
            name_to_options[name] = values

    out = dict(query_params)
    for k, v in list(out.items()):
        if k in NON_VAR_PARAMS:
            continue
        var_name = k.replace("var-", "", 1) if k.startswith("var-") else k
        is_all = v == "All" or v == "$__all" or (isinstance(v, list) and len(v) == 1 and v[0] in ("All", "$__all"))
        if is_all and var_name in name_to_options:
            out[k] = name_to_options[var_name]
        elif is_all and var_name not in name_to_options:
            var_def = next((x for x in var_list if x.get("name") == var_name), None)
            if var_def:
                opts = fetch_variable_options(
                    client, base, org_id, token, var_def, out, from_ms, to_ms, name_to_ds
                )
                if opts:
                    out[k] = opts
    return out


def fill_missing_vars_from_dashboard(dashboard: dict, query_params: dict) -> None:
    """从 dashboard templating 填充 URL 未传的变量。"""
    tlist = dashboard.get("templating")
    var_list = tlist if isinstance(tlist, list) else (tlist or {}).get("list", [])
    for var in var_list:
        name = var.get("name")
        if not name:
            continue
        key = f"var-{name}" if not name.startswith("var-") else name
        existing = query_params.get(key) or query_params.get(name.replace("var-", "", 1))
        if existing is not None and existing != "" and (not isinstance(existing, list) or len(existing) > 0):
            continue
        value = None
        current = var.get("current")
        if isinstance(current, dict):
            value = current.get("value")
        elif current is not None:
            value = current
        if value is None or value == "" or value == "$__all" or value == "__all":
            for o in var.get("options") or []:
                v = o.get("value")
                if v is not None and str(v) not in ("", "__all", "$__all"):
                    value = v
                    break
        if value is not None:
            query_params[key] = value


def query_panel_data(
    client: httpx.Client,
    base: str,
    org_id: str,
    token: str,
    panel: dict,
    from_ms: int,
    to_ms: int,
    query_params: dict,
    name_to_ds: dict,
    skip_sql_substitution: bool = False,
) -> dict:
    """对单个 panel 调用 POST /api/ds/query。skip_sql_substitution=True 时使用 panel 原始 query 不替换变量。"""
    body = build_ds_query_body(panel, from_ms, to_ms, query_params, name_to_ds, skip_sql_substitution)
    if not body["queries"]:
        return {"columns": [], "rows": [], "raw": None}
    q0 = body["queries"][0]
    ds_obj = q0.get("datasource")
    if (
        q0.get("datasourceId") is None
        and isinstance(ds_obj, dict)
        and ds_obj.get("uid") == PS_CLUSTER_OPS4_LIVE_UID
    ):
        info = get_datasource_by_uid(client, base, org_id, token, PS_CLUSTER_OPS4_LIVE_UID)
        if info and info.get("id") is not None:
            q0["datasourceId"] = int(info["id"])
        else:
            q0["datasourceId"] = PS_DATASOURCE_ID
    ds_resolved = q0.get("datasource")
    if isinstance(ds_resolved, dict) and ds_resolved.get("type"):
        ds_type = (ds_resolved.get("type") or "mysql").lower()
    else:
        ds = panel.get("datasource")
        ds_type = "mysql"
        if isinstance(ds, dict):
            ds_type = (ds.get("type") or "mysql").lower()
    url = f"{base}/api/ds/query"
    params = {"ds_type": ds_type, "requestId": f"Q{panel.get('id', 0)}"}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Grafana-Org-Id": str(org_id),
    }
    resp = client.post(url, params=params, json=body, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    structured = frames_to_structured(data)
    return {"columns": structured["columns"], "rows": structured["rows"], "raw": data}


def _per_series_means_from_ds_query_response(response: dict) -> tuple[list, list] | None:
    """Match Grafana panel legend **Mean**: for each series, arithmetic mean of that series' points only.

    Unlike merging multi-frame tables with min(row_count) (which truncates longer series), each frame
    or each value column is averaged independently over its own timestamps.
    """
    if not response:
        return None
    col_means: list[tuple[str, float]] = []

    def _append_means_for_columns_rows(columns: list, rows: list) -> None:
        if not columns or not rows:
            return
        time_idx = -1
        for i, c in enumerate(columns):
            if _normalize_col(c) == "time":
                time_idx = i
                break
        if time_idx < 0:
            return
        for vidx in range(len(columns)):
            if vidx == time_idx:
                continue
            cname = str(columns[vidx])
            if "job_id=" in cname.lower() or _parse_labels_from_column(cname).get("job_id"):
                continue
            vals: list[float] = []
            for row in rows:
                if vidx < len(row) and row[vidx] is not None:
                    try:
                        vals.append(float(row[vidx]))
                    except (TypeError, ValueError):
                        pass
            if vals:
                col_means.append((columns[vidx], sum(vals) / len(vals)))

    results = response.get("results") or {}
    for ref_data in results.values():
        if ref_data.get("error"):
            continue
        frames_list = ref_data.get("frames") or []
        for frame in frames_list:
            meta = (frame.get("schema") or {}).get("meta") or {}
            if (meta.get("custom") or {}).get("resultType") == "exemplar":
                continue
            columns, rows = _frame_to_columns_rows(frame)
            _append_means_for_columns_rows(columns, rows)
        if not frames_list:
            series = ref_data.get("series") or ref_data.get("tables")
            if series:
                cols, srs = _series_to_rows(series if isinstance(series, list) else [series])
                _append_means_for_columns_rows(cols, srs)

    if not col_means:
        return None
    cols_out = [t[0] for t in col_means]
    return cols_out, [[t[1] for t in col_means]]


def _queuing_soc_ps_to_grafana_legend_mean(
    raw_response: dict | None, columns: list, rows: list
) -> tuple[list, list]:
    """Soc/PS: prefer per-series means from raw query JSON (Grafana legend Mean); else table column-wise mean."""
    if raw_response:
        per = _per_series_means_from_ds_query_response(raw_response)
        if per is not None:
            return per
    return _soc_timeseries_to_avg(columns, rows)


def _normalize_col(s: str) -> str:
    """列名规范化：去掉 {labels}、转小写、去空格。"""
    if not s:
        return ""
    s = str(s).strip()
    if "{" in s:
        s = s.split("{")[0].strip()
    return s.lower().replace(" ", "_")


def _soc_timeseries_to_avg(columns: list, rows: list) -> tuple[list, list]:
    """Fallback: column-wise mean on an already-wide table (wrong if table was built with min-row merge)."""
    if not columns or not rows:
        return columns, rows
    time_idx = -1
    for i, c in enumerate(columns):
        if _normalize_col(c) == "time":
            time_idx = i
            break
    if time_idx < 0 and len(rows) <= 1:
        return columns, rows
    if time_idx >= 0:
        new_cols = [c for i, c in enumerate(columns) if i != time_idx]
        avgs = []
        for c_idx in range(len(columns)):
            if c_idx == time_idx:
                continue
            vals = []
            for row in rows:
                if c_idx < len(row) and row[c_idx] is not None:
                    try:
                        vals.append(float(row[c_idx]))
                    except (TypeError, ValueError):
                        pass
            avgs.append(sum(vals) / len(vals) if vals else 0)
        return new_cols, [avgs]
    avgs = []
    for c_idx in range(len(columns)):
        vals = []
        for row in rows:
            if c_idx < len(row) and row[c_idx] is not None:
                try:
                    vals.append(float(row[c_idx]))
                except (TypeError, ValueError):
                    pass
        avgs.append(sum(vals) / len(vals) if vals else 0)
    return columns, [avgs]


def _drop_release_columns(columns: list, rows: list) -> tuple[list, list]:
    """去掉列名中含 release 的列及其对应数据，只保留 train 等非 release job 数据。"""
    drop = [i for i, c in enumerate(columns) if "release" in _normalize_col(c)]
    if not drop:
        return columns, rows
    keep = [i for i in range(len(columns)) if i not in drop]
    new_cols = [columns[i] for i in keep]
    new_rows = [[v for i, v in enumerate(row) if i not in drop] for row in rows]
    return new_cols, new_rows


def _drop_per_job_series_columns(columns: list, rows: list) -> tuple[list, list]:
    """Drop Prometheus wide-table columns whose labels include job_id (one series per job).

    Grafana names fields like: Value {__name__=\"job_life_cycle_seconds\", job_id=\"...\", ...}.
    Those explode JSON size; kanban summaries only need tenant/project-level series.
    """
    if not columns or len(columns) <= 1 or not rows:
        return columns, rows
    drop_idx: list[int] = []
    for i, col in enumerate(columns):
        if i == 0:
            continue
        s = str(col)
        if "{" not in s or "}" not in s:
            continue
        labels = _parse_labels_from_column(s)
        if labels.get("job_id") or "job_id=" in s.lower():
            drop_idx.append(i)
    if not drop_idx:
        return columns, rows
    keep = [i for i in range(len(columns)) if i not in drop_idx]
    new_cols = [columns[i] for i in keep]
    new_rows = [[row[i] if i < len(row) else None for i in keep] for row in rows]
    return new_cols, new_rows


def _norm_token_matches_column(n: str, c_lower: str) -> bool:
    """Match normalized column token n to candidate c_lower: exact or underscore-bounded substring (avoids discount~count, timestamp~time)."""
    if n == c_lower:
        return True
    if not c_lower:
        return False
    if n.startswith(c_lower + "_"):
        return True
    if f"_{c_lower}_" in n:
        return True
    if n.endswith(c_lower) and (len(n) == len(c_lower) or n[len(n) - len(c_lower) - 1] == "_"):
        return True
    return False


def _find_col_index(columns: list, *candidates: str, exclude: tuple[str, ...] = ()) -> int:
    """在 columns 中按规范化名匹配，返回第一个匹配下标；若 exclude 非空则跳过列名包含其中任一的列。未找到 -1。"""
    norm = [_normalize_col(c) for c in columns]
    for cand in candidates:
        c_lower = cand.lower().replace(" ", "_")
        for i, n in enumerate(norm):
            if exclude and any(x in n for x in exclude):
                continue
            if _norm_token_matches_column(n, c_lower):
                return i
    return -1


def _parse_labels_from_column(col_name: str) -> dict:
    """Parse Grafana-style labels from column name, e.g. 'train_count {tenant="x"}' or 'train_count {project="p", tenant="t"}'. Returns dict of label key -> value."""
    out = {}
    if "{" not in col_name or "}" not in col_name:
        return out
    brace = col_name[col_name.index("{"): col_name.index("}") + 1]
    for part in re.findall(r'(\w+)\s*=\s*"([^"]*)"', brace):
        out[part[0].lower()] = part[1]
    return out


def _build_running_count_nested(panels_data: list[dict]) -> dict:
    """
    Build platform -> tenant -> project nested structure from Running Job Count panels.
    Supports (1) long format: columns tenant, project, train_count; (2) wide format: columns like train_count {tenant="x"} or train_count {project="p", tenant="t"}.
    """
    result = {}
    for data in panels_data:
        cols = data.get("columns") or []
        rows = data.get("rows") or []
        if not cols or not rows:
            continue
        # Wide format: value columns have labels (e.g. train_count {tenant="x"} or {project="p", tenant="t"})
        for c_idx, col in enumerate(cols):
            labels = _parse_labels_from_column(col)
            if not labels:
                continue
            tenant = labels.get("tenant", "All")
            project = labels.get("project", "All")
            for row in rows:
                if c_idx >= len(row):
                    continue
                try:
                    count_val = int(float(row[c_idx])) if row[c_idx] is not None else 0
                except (TypeError, ValueError):
                    count_val = 0
                result.setdefault("All", {})
                result["All"].setdefault(tenant, {})
                result["All"][tenant].setdefault(project, 0)
                result["All"][tenant][project] += count_val
        # Long format: separate columns for platform, tenant, project, count
        i_platform = _find_col_index(cols, "platform", "Platform")
        i_tenant = _find_col_index(cols, "tenant", "Tenant")
        i_project = _find_col_index(cols, "project", "Project")
        i_count = -1
        for name in ("running_train_count", "train_count", "count", "value", "running_count", "running job count", "total", "num", "cnt"):
            i_count = _find_col_index(cols, name, exclude=("release",))
            if i_count >= 0:
                break
        if i_count < 0 and cols:
            i_count = len(cols) - 1
        if i_tenant >= 0 or i_project >= 0 or i_platform >= 0:
            for row in rows:
                platform = str(row[i_platform]) if i_platform >= 0 and i_platform < len(row) else "All"
                tenant = str(row[i_tenant]) if i_tenant >= 0 and i_tenant < len(row) else "All"
                project = str(row[i_project]) if i_project >= 0 and i_project < len(row) else "All"
                try:
                    count_val = int(float(row[i_count])) if i_count >= 0 and i_count < len(row) and row[i_count] is not None else 0
                except (TypeError, ValueError):
                    count_val = 0
                result.setdefault(platform, {})
                result[platform].setdefault(tenant, {})
                result[platform][tenant].setdefault(project, 0)
                result[platform][tenant][project] += count_val
        elif i_count >= 0 and not any(_parse_labels_from_column(c) for c in cols):
            for row in rows:
                try:
                    count_val = int(float(row[i_count])) if i_count < len(row) and row[i_count] is not None else 0
                except (TypeError, ValueError):
                    count_val = 0
                result.setdefault("All", {})
                result["All"].setdefault("All", {})
                result["All"]["All"].setdefault("All", 0)
                result["All"]["All"]["All"] += count_val
    return result


def _build_queuing_nested(panels_data: list[dict]) -> dict:
    """
    Merge Queuing panels into platform -> tenant -> project (same nesting as running_job_count).
    Output: { "All": { tenant: { project: { queuing_count, queuing_duration } } } }.
    Supports: (1) long format columns tenant, project, count, duration; (2) wide format with labels in column names;
    (3) Time+Value only (no tenant/project): use panel_title to decide count vs duration, put under All/All.
    Soc/PS: 排队面板在入库前已压成单行，数值对齐 Grafana 图例 **Mean**（每条序列自己的时间范围内算术平均，见 _queuing_soc_ps_to_grafana_legend_mean）。
    """
    result = {"All": {}}
    inner = result["All"]
    for data in panels_data:
        cols = data.get("columns") or []
        rows = data.get("rows") or []
        title = (data.get("panel_title") or "").lower()
        is_minutes = "minute" in title or "duration" in title
        if not cols:
            continue
        i_tenant = _find_col_index(cols, "tenant", "Tenant")
        i_project = _find_col_index(cols, "project", "Project")
        i_count = _find_col_index(cols, "count", "queuing_count", "queuing count", "num", "cnt", "value")
        i_duration = _find_col_index(cols, "duration", "queuing_duration", "queuing duration", "time", "avg_duration")
        if i_count < 0:
            i_count = len(cols) - 2 if len(cols) >= 2 else 0
        if i_duration < 0:
            i_duration = len(cols) - 1 if len(cols) >= 1 else 0
        if not rows:
            continue
        # Wide format: value columns have labels (e.g. Value {tenant_name=...}); use avg per column
        labeled = [(i, _parse_labels_from_column(c)) for i, c in enumerate(cols) if _parse_labels_from_column(c)]
        if labeled:
            for c_idx, labels in labeled:
                tenant = labels.get("tenant_name") or labels.get("tenant") or "All"
                project = labels.get("project_name") or labels.get("project") or "All"
                vals = []
                for row in rows:
                    if c_idx < len(row) and row[c_idx] is not None:
                        try:
                            vals.append(float(row[c_idx]))
                        except (TypeError, ValueError):
                            pass
                avg_val = sum(vals) / len(vals) if vals else 0
                inner.setdefault(tenant, {})
                inner[tenant].setdefault(project, {"queuing_count": 0, "queuing_duration": None})
                if is_minutes:
                    inner[tenant][project]["queuing_duration"] = (inner[tenant][project]["queuing_duration"] or 0) + avg_val
                else:
                    inner[tenant][project]["queuing_count"] += round(avg_val)
            continue
        # Multiple value columns without labels (e.g. Value_0, Value_1 from merged plain frames): one series per column
        if len(cols) >= 2 and not any(_parse_labels_from_column(c) for c in cols):
            for c_idx in range(1, len(cols)):
                col_name = str(cols[c_idx]) if c_idx < len(cols) else f"Value_{c_idx}"
                vals = []
                for row in rows:
                    if c_idx < len(row) and row[c_idx] is not None:
                        try:
                            vals.append(float(row[c_idx]))
                        except (TypeError, ValueError):
                            pass
                avg_val = sum(vals) / len(vals) if vals else 0
                inner.setdefault(col_name, {})
                inner[col_name].setdefault("All", {"queuing_count": 0, "queuing_duration": None})
                if is_minutes:
                    inner[col_name]["All"]["queuing_duration"] = (inner[col_name]["All"]["queuing_duration"] or 0) + avg_val
                else:
                    inner[col_name]["All"]["queuing_count"] += round(avg_val)
            continue
        if i_tenant < 0 and i_project < 0:
            # Soc Queuing: 每条数据取 avg，不保留时间戳；多行时用均值
            vals = []
            for row in rows:
                try:
                    val = float(row[i_count]) if i_count < len(row) and row[i_count] is not None else 0
                except (TypeError, ValueError):
                    val = 0
                vals.append(val)
            if vals:
                inner.setdefault("All", {})
                inner["All"].setdefault("All", {"queuing_count": 0, "queuing_duration": None})
                avg_val = sum(vals) / len(vals)
                if is_minutes:
                    inner["All"]["All"]["queuing_duration"] = avg_val
                else:
                    inner["All"]["All"]["queuing_count"] = round(avg_val)
            continue
        for row in rows:
            tenant = str(row[i_tenant]) if i_tenant >= 0 and i_tenant < len(row) else "All"
            project = str(row[i_project]) if i_project >= 0 and i_project < len(row) else "All"
            try:
                c = int(float(row[i_count])) if i_count >= 0 and i_count < len(row) and row[i_count] is not None else 0
            except (TypeError, ValueError):
                c = 0
            try:
                d = row[i_duration] if i_duration >= 0 and i_duration < len(row) else None
                if d is not None:
                    d = float(d)
            except (TypeError, ValueError):
                d = None
            inner.setdefault(tenant, {})
            inner[tenant].setdefault(project, {"queuing_count": 0, "queuing_duration": None})
            inner[tenant][project]["queuing_count"] += c
            if d is not None:
                if inner[tenant][project]["queuing_duration"] is None:
                    inner[tenant][project]["queuing_duration"] = 0
                inner[tenant][project]["queuing_duration"] += d
    return result


def build_structured_summary(blocks_raw: dict) -> dict:
    """从各区块原始 panel 数据生成结构化摘要。"""
    running = blocks_raw.get(BLOCK_RUNNING_COUNT) or []
    soc = blocks_raw.get(BLOCK_QUEUING_SOC) or []
    ps = blocks_raw.get(BLOCK_QUEUING_PS) or []

    return {
        "running_job_count": _build_running_count_nested(running),
        "queuing_soc": _build_queuing_nested(soc),
        "queuing_ps": _build_queuing_nested(ps),
    }


def _filter_nested_by_tenant_project(data: dict, tenant_filter: list | None, project_filter: list | None, level: str) -> dict:
    """level in ('running_job_count', 'queuing'): both are platform->tenant->project (queuing has platform 'All')."""
    if not tenant_filter and not project_filter:
        return data
    out = {}
    for platform, tenants in data.items():
        out[platform] = {}
        for tenant, projects in tenants.items():
            if tenant_filter and tenant not in tenant_filter:
                continue
            out[platform][tenant] = {p: v for p, v in projects.items() if (not project_filter or p in project_filter)}
        if out[platform]:
            out[platform] = {k: v for k, v in out[platform].items() if v}
    out = {k: v for k, v in out.items() if v}
    return out


def _exclude_tenants_from_blocks_raw(blocks_raw: dict, exclude_tenants: set[str] | None) -> dict:
    """Remove rows/columns tied to given tenant names (exact match on tenant / tenant_name labels)."""
    if not exclude_tenants:
        return blocks_raw
    ex = {str(x) for x in exclude_tenants if x is not None and str(x).strip()}
    if not ex:
        return blocks_raw
    filtered: dict = {}
    for block_title, panels in blocks_raw.items():
        filtered[block_title] = []
        for p in panels:
            cols = p.get("columns") or []
            rows = p.get("rows") or []
            i_tenant = _find_col_index(cols, "tenant", "Tenant")
            if i_tenant >= 0:
                new_rows = []
                for row in rows:
                    if i_tenant < len(row) and str(row[i_tenant]) in ex:
                        continue
                    new_rows.append(list(row))
                filtered[block_title].append({"panel_title": p["panel_title"], "columns": list(cols), "rows": new_rows})
                continue
            drop_idx: list[int] = []
            for i, col in enumerate(cols):
                lab = _parse_labels_from_column(str(col))
                t = lab.get("tenant_name") or lab.get("tenant")
                if t and str(t) in ex:
                    drop_idx.append(i)
            if not drop_idx:
                filtered[block_title].append({"panel_title": p["panel_title"], "columns": list(cols), "rows": [list(r) for r in rows]})
                continue
            keep = [i for i in range(len(cols)) if i not in drop_idx]
            new_cols = [cols[i] for i in keep]
            new_rows = [[row[i] if i < len(row) else None for i in keep] for row in rows]
            filtered[block_title].append({"panel_title": p["panel_title"], "columns": new_cols, "rows": new_rows})
    return filtered


def _filter_blocks_raw(
    blocks_raw: dict, tenant_filter: list | None, project_filter: list | None
) -> dict:
    """按 tenant/project 列过滤 blocks_raw 中各 panel 的 rows。"""
    if not tenant_filter and not project_filter:
        return blocks_raw
    filtered = {}
    for block_title, panels in blocks_raw.items():
        filtered[block_title] = []
        for p in panels:
            cols = p.get("columns") or []
            rows = p.get("rows") or []
            i_tenant = _find_col_index(cols, "tenant", "Tenant")
            i_project = _find_col_index(cols, "project", "Project")
            if i_tenant < 0 and i_project < 0:
                filtered[block_title].append(p)
                continue
            new_rows = []
            for row in rows:
                if i_tenant >= 0 and i_tenant < len(row) and tenant_filter and str(row[i_tenant]) not in tenant_filter:
                    continue
                if i_project >= 0 and i_project < len(row) and project_filter and str(row[i_project]) not in project_filter:
                    continue
                new_rows.append(row)
            filtered[block_title].append({"panel_title": p["panel_title"], "columns": cols, "rows": new_rows})
    return filtered


def main() -> int:
    parser = argparse.ArgumentParser(
        description="EGO Platform Job Kanban — 从 Grafana 拉取运行任务数量与排队统计，输出嵌套结构。"
    )
    parser.add_argument("--url", default=DEFAULT_DASHBOARD_URL, help="完整 Grafana dashboard URL（默认 SG live 看板）")
    parser.add_argument("--from", dest="from_", metavar="TIME", help="覆盖 URL 的 from，如 now-6h")
    parser.add_argument("--to", metavar="TIME", help="覆盖 URL 的 to，如 now")
    parser.add_argument("--tenant", nargs="*", metavar="T", help="输出时只保留这些 tenant，不传则不过滤")
    parser.add_argument("--project", nargs="*", metavar="P", help="输出时只保留这些 project，不传则不过滤")
    parser.add_argument(
        "--exclude-tenant",
        nargs="*",
        metavar="T",
        default=None,
        help=(
            "输出时剔除这些 tenant；省略本参数时默认剔除 "
            + ", ".join(DEFAULT_EXCLUDE_TENANTS)
            + "。仅写 --exclude-tenant 且不带值则不做剔除。"
        ),
    )
    parser.add_argument("--out-file", metavar="PATH", help="写入 JSON 文件，不传则 stdout")
    parser.add_argument(
        "--omit-blocks-raw",
        action="store_true",
        help="输出 JSON 不包含 blocks_raw（需与结构化摘要同用；与 --no-summary 并用时忽略本项并保留 blocks_raw）",
    )
    parser.add_argument("--list-blocks", action="store_true", help="仅列出三个区块及其 panel 数量后退出")
    parser.add_argument("--no-summary", action="store_true", help="不输出结构化摘要，仅原始 panel 数据")
    args = parser.parse_args()

    token = os.environ.get("GRAFANA_API_TOKEN") or ""
    if not token or not str(token).strip():
        print("Error: GRAFANA_API_TOKEN environment variable is required.", file=sys.stderr)
        return 1

    try:
        parsed = parse_url(args.url)
    except Exception as e:
        print(f"Error: Failed to parse URL: {e}", file=sys.stderr)
        return 1

    base = parsed["base"]
    uid = parsed["uid"]
    org_id = parsed["org_id"]
    query_params = parsed["query_params"]
    from_ms = parsed["from_ms"]
    to_ms = parsed["to_ms"]
    if getattr(args, "from_", None):
        try:
            from_ms = parse_relative_time(args.from_)
        except ValueError as e:
            print(f"Error: Invalid --from: {e}", file=sys.stderr)
            return 1
    if args.to:
        try:
            to_ms = parse_relative_time(args.to)
        except ValueError as e:
            print(f"Error: Invalid --to: {e}", file=sys.stderr)
            return 1

    with httpx.Client(timeout=120.0) as client:
        try:
            dashboard = get_dashboard(client, base, uid, org_id, token, query_params)
        except httpx.HTTPStatusError as e:
            print(f"Error: Dashboard request failed HTTP {e.response.status_code}: {e.response.text[:500]}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error: Failed to get dashboard: {e}", file=sys.stderr)
            return 1

        if args.list_blocks:
            for block_title in BLOCK_TITLES:
                panels = find_block_panels(dashboard, block_title)
                print(f"{len(panels)}\t{block_title}")
            return 0

        try:
            datasources = get_datasources(client, base, org_id, token)
            name_to_ds = {}
            for d in datasources:
                if not d.get("uid"):
                    continue
                info = {"id": d.get("id"), "uid": d["uid"], "type": d.get("type") or "mysql", "name": d.get("name")}
                name_to_ds[d["uid"]] = info
                if d.get("name"):
                    name_to_ds[d["name"]] = info
        except Exception:
            name_to_ds = {}
            datasources = []

        tlist = dashboard.get("templating")
        var_list = tlist if isinstance(tlist, list) else (tlist or {}).get("list", [])
        var_name_to_options = {v.get("name"): (v.get("options") or []) for v in (var_list or []) if v.get("name")}

        for block_title in BLOCK_TITLES:
            for panel in find_block_panels(dashboard, block_title):
                ds = panel.get("datasource")
                if isinstance(ds, dict):
                    u = ds.get("uid")
                    if u and isinstance(u, str) and u.startswith("${") and u.endswith("}"):
                        var_name = u[2:-1].strip()
                        name = query_params.get(var_name) or query_params.get("var-" + var_name)
                        if isinstance(name, list):
                            name = name[0] if name else None
                        if name and name not in name_to_ds:
                            lookup_key = name
                            opts = var_name_to_options.get(var_name) or []
                            for o in opts:
                                if str(o.get("text") or "") == str(name) or str(o.get("value") or "") == str(name):
                                    lookup_key = o.get("value") or name
                                    break
                            if lookup_key in name_to_ds:
                                name_to_ds[name] = name_to_ds[lookup_key]
                                info = name_to_ds[name]
                            else:
                                info = get_datasource_by_name(client, base, org_id, token, str(name)) or get_datasource_by_uid(client, base, org_id, token, str(name)) or (name_to_ds.get(lookup_key) if lookup_key != name else None)
                            panel_type = (ds.get("type") or "prometheus").lower()
                            if not info and datasources:
                                name_norm = (name or "").replace("_", "-").lower()
                                name_s = str(name or "")
                                candidates = [
                                    d for d in datasources
                                    if d.get("uid")
                                    and (
                                        d.get("name") == name
                                        or d.get("uid") == name
                                        or (name_s and name_s in (d.get("name") or ""))
                                        or (name_s and name_s in (d.get("uid") or ""))
                                        or (d.get("name") or "").replace("_", "-").lower() == name_norm
                                        or (d.get("uid") or "").replace("_", "-").lower() == name_norm
                                        or (var_name == "cluster" and (name_s in (d.get("name") or "") or (d.get("name") or "") in name_s or name_s in (d.get("uid") or "")))
                                    )
                                ]
                                for d in candidates:
                                    if (d.get("type") or "").lower() == panel_type:
                                        info = d
                                        break
                                if not info and candidates:
                                    info = candidates[0]
                            if not info and var_name == "cluster" and str(name or "") == "kube-ego-manager-sg-ops4-live":
                                info = get_datasource_by_uid(client, base, org_id, token, PS_CLUSTER_OPS4_LIVE_UID)
                            if info:
                                name_to_ds[name] = {"id": info.get("id"), "uid": info.get("uid"), "type": info.get("type") or "mysql", "name": info.get("name")}
                                if info.get("uid") and info["uid"] not in name_to_ds:
                                    name_to_ds[info["uid"]] = name_to_ds[name]
                    elif u and u not in name_to_ds:
                        info = get_datasource_by_uid(client, base, org_id, token, u)
                        if info:
                            name_to_ds[u] = {"id": info.get("id"), "uid": info.get("uid", u), "type": info.get("type") or "mysql"}
                elif isinstance(ds, str) and ds.strip() and ds not in name_to_ds:
                    info = get_datasource_by_uid(client, base, org_id, token, ds) or get_datasource_by_name(client, base, org_id, token, ds)
                    if info:
                        name_to_ds[ds] = {"id": info.get("id"), "uid": info.get("uid", ds), "type": info.get("type") or "mysql"}
                        if info.get("name") and info["name"] not in name_to_ds:
                            name_to_ds[info["name"]] = name_to_ds[ds]
                        if info.get("uid") and info["uid"] not in name_to_ds:
                            name_to_ds[info["uid"]] = name_to_ds[ds]

        resolved_params = resolve_all_from_dashboard(
            client, dashboard, query_params, base, org_id, token, from_ms, to_ms, name_to_ds
        )
        fill_missing_vars_from_dashboard(dashboard, resolved_params)

        blocks_raw = {title: [] for title in BLOCK_TITLES}
        panels_by_block = {}
        for block_title in BLOCK_TITLES:
            panels_by_block[block_title] = find_block_panels(dashboard, block_title)

        panel_errors = []
        for block_title in BLOCK_TITLES:
            for panel in panels_by_block[block_title]:
                title = (panel.get("title") or "unknown").strip()
                if "release" in title.lower() and "train" not in title.lower():
                    continue
                try:
                    data = query_panel_data(
                        client, base, org_id, token, panel, from_ms, to_ms, resolved_params, name_to_ds,
                    )
                    raw = data.get("raw")
                    cols, rows = _drop_release_columns(data["columns"], data["rows"])
                    cols, rows = _drop_per_job_series_columns(cols, rows)
                    if block_title in (BLOCK_QUEUING_SOC, BLOCK_QUEUING_PS):
                        cols, rows = _queuing_soc_ps_to_grafana_legend_mean(raw, cols, rows)
                    blocks_raw[block_title].append({"panel_title": title, "columns": cols, "rows": rows})
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 500:
                        try:
                            data = query_panel_data(
                                client, base, org_id, token, panel, from_ms, to_ms, resolved_params, name_to_ds,
                                skip_sql_substitution=True,
                            )
                            raw = data.get("raw")
                            cols, rows = _drop_release_columns(data["columns"], data["rows"])
                            cols, rows = _drop_per_job_series_columns(cols, rows)
                            if block_title in (BLOCK_QUEUING_SOC, BLOCK_QUEUING_PS):
                                cols, rows = _queuing_soc_ps_to_grafana_legend_mean(raw, cols, rows)
                            blocks_raw[block_title].append({"panel_title": title, "columns": cols, "rows": rows})
                        except Exception:
                            err_msg = f"Panel '{block_title} / {title}' HTTP 500: {(e.response.text or '')[:200]}"
                            panel_errors.append(err_msg)
                            print(f"Error: {err_msg}", file=sys.stderr)
                    else:
                        err_msg = f"Panel '{block_title} / {title}' HTTP {e.response.status_code}: {(e.response.text or '')[:200]}"
                        panel_errors.append(err_msg)
                        print(f"Error: {err_msg}", file=sys.stderr)
                except Exception as e:
                    err_msg = f"Panel '{block_title} / {title}' failed: {e}"
                    panel_errors.append(err_msg)
                    print(f"Error: {err_msg}", file=sys.stderr)

    tenant_filter = None
    if getattr(args, "tenant", None) and len(args.tenant) > 0:
        tenant_filter = args.tenant
    project_filter = None
    if getattr(args, "project", None) and len(args.project) > 0:
        project_filter = args.project
    exclude_tenants: set[str] | None = None
    if args.exclude_tenant is None:
        exclude_tenants = set(DEFAULT_EXCLUDE_TENANTS)
    elif len(args.exclude_tenant) > 0:
        exclude_tenants = set(args.exclude_tenant)

    prep = {
        block: [{"panel_title": p["panel_title"], "columns": p["columns"], "rows": p["rows"]} for p in blocks_raw[block]]
        for block in BLOCK_TITLES
    }
    if exclude_tenants:
        prep = _exclude_tenants_from_blocks_raw(prep, exclude_tenants)
    prep = _filter_blocks_raw(prep, tenant_filter, project_filter)

    filter_by: dict | None = None
    if tenant_filter or project_filter or exclude_tenants:
        filter_by = {}
        if tenant_filter:
            filter_by["tenant"] = tenant_filter
        if project_filter:
            filter_by["project"] = project_filter
        if exclude_tenants:
            filter_by["exclude_tenant"] = sorted(exclude_tenants)

    output = {
        "data_scope": "Ego SG environment (Ego sg env)",
        "source_url": args.url,
        "panel_errors": panel_errors,
        "filter_by": filter_by,
    }
    include_blocks_raw = not args.omit_blocks_raw or args.no_summary
    if args.omit_blocks_raw and args.no_summary:
        print(
            "Warning: --omit-blocks-raw ignored with --no-summary (output would be empty of panel data).",
            file=sys.stderr,
        )
    if include_blocks_raw:
        output["blocks_raw"] = prep
    if not args.no_summary:
        structured = build_structured_summary(
            {block: [{"panel_title": p.get("panel_title"), "columns": p["columns"], "rows": p["rows"]} for p in prep[block]] for block in BLOCK_TITLES}
        )
        if tenant_filter or project_filter:
            structured["running_job_count"] = _filter_nested_by_tenant_project(
                structured["running_job_count"], tenant_filter, project_filter, "running_job_count"
            )
            structured["queuing_soc"] = _filter_nested_by_tenant_project(
                structured["queuing_soc"], tenant_filter, project_filter, "queuing"
            )
            structured["queuing_ps"] = _filter_nested_by_tenant_project(
                structured["queuing_ps"], tenant_filter, project_filter, "queuing"
            )
        output["structured"] = structured

    out_text = json.dumps(output, indent=2, ensure_ascii=False)
    if args.out_file:
        with open(args.out_file, "w", encoding="utf-8") as f:
            f.write(out_text)
    else:
        print(out_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
