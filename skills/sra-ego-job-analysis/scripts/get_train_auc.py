#!/usr/bin/env python3
"""
EGO 训练效果指标对比：从 Grafana 拉取指定区块下的 Panel 数据（默认 Auc Per Day、gAUC Per Day），
输出结构清晰的 JSON 或表格。

支持区块：Versioned-level Model Performance Comparison（默认）、Job-level Model Performance Comparison。
入参：上层传入已组装好所有 URL 参数的完整 link（--url）。
依赖：见同目录 requirements.txt（pip install -r requirements.txt）
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from urllib.parse import parse_qs, urlparse

import httpx

# 支持的区块标题与默认 panel
BLOCK_VERSIONED = "Versioned-level Model Performance Comparison"
BLOCK_JOB = "Job-level Model Performance Comparison"
ALLOWED_BLOCK_TITLES = (BLOCK_VERSIONED, BLOCK_JOB)
BLOCK_CHOICES = ("versioned", "job", "both")
DEFAULT_PANEL_TITLES = ["Auc Per Day", "gAUC Per Day"]

# URL 中仅此三个参数不是模板变量（不以 var- 开头）；其余均为 var- 开头的模板变量
NON_VAR_PARAMS = ("from", "to", "orgId")

# 无 datasource API 权限时使用的写死配置；实际使用哪个由 URL 中 var-mysql_datasource 决定
FALLBACK_DATASOURCE_BY_NAME: dict[str, dict] = {
    "EGO-Train-MySQL": {"id": 4741, "uid": "NMEBgCI4z", "type": "mysql"},
    "EGO-Train-US-MySQL": {"id": 7924, "uid": "Y0mMNCISz", "type": "mysql"},
}


def parse_relative_time(s: str) -> int:
    """将 Grafana 相对时间如 now、now-90d 转为毫秒时间戳。"""
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
    else:  # d
        delta = timedelta(days=num)
    t = now - delta
    return int(t.timestamp() * 1000)


def parse_url(url: str):
    """从完整 URL 解析 base、UID、orgId、query 参数（多值保留为列表）。"""
    parsed = urlparse(url)
    path = (parsed.path or "").rstrip("/")
    # 路径形如 /grafana/d/B6FNSQHVz/ego-train-v1-multiple-models-comparison，Grafana 可能挂在子路径
    parts = [p for p in path.split("/") if p]
    uid = ""
    for part in parts:
        if len(part) == 9 and part.startswith("B"):  # UID 约定长度
            uid = part
            break
    if not uid:
        raise ValueError(f"Could not find dashboard UID in path: {path}")
    # base 需包含 Grafana 子路径，如 https://host/grafana
    base_path = "/" + parts[0] if parts else ""
    base = f"{parsed.scheme}://{parsed.netloc}{base_path}".rstrip("/")

    # query: parse_qs 返回每个 key 对应列表
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    # 单值取第一个，多值保持列表
    params_single = {}
    params_multi = {}
    for k, v in query_params.items():
        v = [x for x in v if x is not None and str(x).strip() != ""]
        if not v:
            continue
        if k in NON_VAR_PARAMS:
            params_single[k] = v[0] if len(v) == 1 else v
        else:
            # 其余均为模板变量（Grafana 里为 var- 开头）
            params_multi[k] = v if len(v) > 1 else v

    # 合并，单值优先取第一个
    def first_or_list(arr):
        return arr[0] if len(arr) == 1 else arr

    out = {k: first_or_list(v) for k, v in query_params.items() if v}
    out.update(params_single)
    for k, v in params_multi.items():
        out[k] = v

    org_id = out.get("orgId") or "1"
    from_ts = out.get("from", "now-90d")
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


def get_datasources(base: str, org_id: str, token: str) -> list:
    """GET /api/datasources 用于按名称解析 datasource UID。"""
    url = f"{base}/api/datasources"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Grafana-Org-Id": str(org_id),
    }
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()


def get_datasource_by_uid(base: str, org_id: str, token: str, uid: str) -> dict | None:
    """GET /api/datasources/uid/:uid，在无列表权限时用 UID 拉取单个 datasource（含 id）。"""
    if not uid or not isinstance(uid, str) or (uid.startswith("${") and uid.endswith("}")):
        return None
    url = f"{base}/api/datasources/uid/{uid}"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Grafana-Org-Id": str(org_id),
    }
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return None


def get_datasource_by_name(base: str, org_id: str, token: str, name: str) -> dict | None:
    """GET /api/datasources/name/:name，用名称拉取 datasource（当 panel 使用变量如 ${mysql_datasource} 且值为名称时）。"""
    if not name or not isinstance(name, str):
        return None
    url = f"{base}/api/datasources/name/{name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Grafana-Org-Id": str(org_id),
    }
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return None


def resolve_datasource(ds: dict | str, query_params: dict, name_to_ds: dict) -> dict | None:
    """将 panel 的 datasource（可能为变量名或 ref）解析为 { type, uid, id? }。name_to_ds 的 key 可以是名称或 uid。"""
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
            elif uid in name_to_ds:
                return name_to_ds[uid]
        return ds
    if isinstance(ds, str):
        if ds in name_to_ds:
            return name_to_ds[ds]
    return None


def get_dashboard(
    base: str, uid: str, org_id: str, token: str, query_params: dict | None = None, verbose: bool = False
) -> dict:
    """GET /api/dashboards/uid/:uid，可选传入 query_params 作为 query string 以应用模板变量。"""
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
    if verbose:
        print(f"[verbose] GET dashboard params={list(params.keys()) if params else None}", file=sys.stderr)
    with httpx.Client(timeout=60.0) as client:
        resp = client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    if "dashboard" not in data:
        raise ValueError("Dashboard response missing 'dashboard' key")
    return data["dashboard"]


def fetch_variable_options(
    base: str,
    org_id: str,
    token: str,
    var_def: dict,
    query_params: dict,
    from_ms: int,
    to_ms: int,
    name_to_ds: dict,
    verbose: bool = False,
    debug: bool = False,
) -> list:
    """执行变量的 query（POST /api/ds/query），返回选项值列表。变量为 type=query 且含 query/definition 时有效。"""
    var_type = (var_def.get("type") or "").lower()
    if var_type != "query":
        return []

    # 变量 SQL：Grafana 可能用 query、definition 或 rawQuery
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
            "raw": {"from": str(query_params.get("from", "now-90d")), "to": str(query_params.get("to", "now"))},
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
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(url, params=params, json=body, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return []

    # 从 results.A.frames[0] 取第一列的值
    results = data.get("results") or {}
    ref_data = results.get("A") or {}
    frames = ref_data.get("frames") or []
    if not frames:
        return []

    values = []
    for frame in frames:
        schema = frame.get("schema") or {}
        fields = schema.get("fields") or []
        data_vals = frame.get("data") or {}
        col_vals = data_vals.get("values") or []
        if not fields or not col_vals:
            continue
        # 第一列的所有行
        first_col = col_vals[0]
        for v in first_col:
            if v is None:
                continue
            s = str(v).strip()
            if s and s not in ("__all", "$__all", ""):
                values.append(v)
    return values


def resolve_all_from_dashboard(
    dashboard: dict,
    query_params: dict,
    name_to_ds: dict,
    base: str,
    org_id: str,
    token: str,
    from_ms: int,
    to_ms: int,
    verbose: bool = False,
    debug: bool = False,
) -> dict:
    """将 URL 里值为 All 的变量从 dashboard 的 templating 展开为实际选项值列表：优先用 API 返回的 options，否则执行变量的 query 获取。"""
    tlist = dashboard.get("templating")
    if isinstance(tlist, list):
        var_list = tlist
    else:
        var_list = (tlist or {}).get("list", [])

    # 变量名 -> 该变量所有选项的 value 列表（排除 __all / All 占位）
    name_to_options: dict[str, list] = {}
    for var in var_list:
        name = var.get("name")
        if not name:
            continue
        options = var.get("options") or []
        values = []
        for o in options:
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
        # 模板变量名：Grafana URL 为 var-xxx，取 xxx
        var_name = k.replace("var-", "", 1) if k.startswith("var-") else k
        is_all = False
        if v == "All" or v == "$__all":
            is_all = True
        elif isinstance(v, list) and len(v) == 1 and (v[0] == "All" or v[0] == "$__all"):
            is_all = True
        elif isinstance(v, list) and all(x in ("All", "$__all") for x in v):
            is_all = True
        if is_all and var_name in name_to_options:
            out[k] = name_to_options[var_name]
            if verbose:
                print(f"[verbose] Resolved {k}=All -> {len(out[k])} values (dashboard options)", file=sys.stderr)
        elif is_all and var_name not in name_to_options:
            # 通过执行变量的 query 获取实际选项列表（不写死）
            var_def = next((v for v in var_list if v.get("name") == var_name), None)
            if var_def:
                opts = fetch_variable_options(
                    base, org_id, token, var_def, query_params, from_ms, to_ms, name_to_ds, verbose, debug
                )
                if opts:
                    out[k] = opts
                    if verbose:
                        print(f"[verbose] Resolved {k}=All -> {len(opts)} values (variable query)", file=sys.stderr)
                elif debug:
                    print(f"[debug] {k}=All: variable query returned no options", file=sys.stderr)
            elif debug:
                print(f"[debug] {k}=All: no var definition in dashboard", file=sys.stderr)

    return out


def fill_missing_vars_from_dashboard(
    dashboard: dict,
    query_params: dict,
    verbose: bool = False,
    debug: bool = False,
) -> None:
    """当 ds/query 需要某变量（如 job_types、xgauc_path）而 URL 未传时，从 dashboard 的 templating 解析当前值或选项并填入 query_params，避免查询报错。"""
    tlist = dashboard.get("templating")
    if isinstance(tlist, list):
        var_list = tlist
    else:
        var_list = (tlist or {}).get("list", [])

    for var in var_list:
        name = var.get("name")
        if not name:
            continue
        key = f"var-{name}" if not name.startswith("var-") else name
        var_name = name.replace("var-", "", 1) if name.startswith("var-") else name
        # 已存在且非空则跳过
        existing = query_params.get(key) or query_params.get(var_name)
        if existing is not None and existing != "" and (not isinstance(existing, list) or len(existing) > 0):
            continue

        value = None
        current = var.get("current")
        if isinstance(current, dict):
            value = current.get("value")
        elif current is not None:
            value = current
        if value is None or value == "" or value == "$__all" or value == "__all":
            options = var.get("options") or []
            for o in options:
                v = o.get("value")
                if v is not None:
                    s = str(v)
                    if s not in ("", "__all", "$__all"):
                        value = v
                        break
        if value is not None:
            query_params[key] = value
            if verbose:
                print(f"[verbose] Filled missing {key!r} from dashboard templating -> {value!r}", file=sys.stderr)
        elif debug:
            print(f"[debug] Dashboard var {name!r}: no current/option to fill", file=sys.stderr)


def find_block_panels(dashboard: dict, block_title: str) -> list:
    """在 dashboard.panels 中找到 title 为 block_title 的 row，返回其下的 panel 列表。
    支持两种 Grafana 结构：1) 嵌套在 row.panels 中；2) 扁平数组里紧跟在该 row 之后的项（直到下一个 row）。"""
    panels = dashboard.get("panels") or []
    for idx, p in enumerate(panels):
        if p.get("type") != "row" or (p.get("title") or "").strip() != block_title:
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


def resolve_block_titles(block_arg: str) -> list[str]:
    """将 --block 参数解析为区块标题列表。"""
    choice = (block_arg or "versioned").strip().lower()
    if choice == "versioned":
        return [BLOCK_VERSIONED]
    if choice == "job":
        return [BLOCK_JOB]
    if choice == "both":
        return [BLOCK_VERSIONED, BLOCK_JOB]
    # 允许直接传完整标题（兼容）
    if choice == BLOCK_VERSIONED.lower():
        return [BLOCK_VERSIONED]
    if choice == BLOCK_JOB.lower():
        return [BLOCK_JOB]
    return [BLOCK_VERSIONED]


def filter_panels(block_panels: list, default_titles: list, all_panels: bool, panel_titles: list | None) -> list:
    """根据默认/--all-panels/--panels 筛选要请求的 panel 列表。默认标题匹配不区分大小写。"""
    if all_panels:
        return block_panels
    if panel_titles:
        titles_set = {t.strip() for t in panel_titles if t and str(t).strip()}
        return [p for p in block_panels if (p.get("title") or "").strip() in titles_set]
    titles_set_lower = {t.lower() for t in default_titles}
    return [p for p in block_panels if (p.get("title") or "").strip().lower() in titles_set_lower]


def get_datasource_uid(panel: dict, dashboard: dict) -> tuple[str, str]:
    """返回 (datasource_uid, ds_type)。panel.datasource 可能是 ref 或对象。"""
    ds = panel.get("datasource")
    if isinstance(ds, dict):
        uid = ds.get("uid") or ""
        ds_type = (ds.get("type") or "mysql").lower()
        return uid, ds_type
    if isinstance(ds, str):
        # 可能是 "MySQL" 或 uid，尝试从 dashboard 取
        return ds, "mysql"
    return "", "mysql"


def _sql_escape_single(s: str) -> str:
    """单引号转义，用于 SQL 字面量。"""
    return "'" + str(s).replace("\\", "\\\\").replace("'", "''") + "'"


def _ms_to_iso(ms: int) -> str:
    """毫秒时间戳转 ISO8601，供 body.range。"""
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:23] + "Z"


# 作为 JSON path 等片段替换、不加引号的变量（仅做单引号转义）
_UNQUOTED_SQL_VARS = {"xgauc_path"}


def _substitute_sql_macros(raw_sql: str, from_ms: int, to_ms: int, query_params: dict) -> str:
    """只替换 rawSql 中的 $var；保留 $__unixEpochFilter 由后端根据 from/to 展开（与浏览器一致）。"""
    if not raw_sql or not isinstance(raw_sql, str):
        return raw_sql
    sql = raw_sql
    # 不替换 $__unixEpochFilter，由后端根据 from/to 展开（与浏览器行为一致）
    for k, v in query_params.items():
        if k in NON_VAR_PARAMS:
            continue
        var_name = k.replace("var-", "", 1) if k.startswith("var-") else k
        if var_name in _UNQUOTED_SQL_VARS:
            # 用于 json path 等：只做单引号转义，不加外层引号
            raw_val = str(v).replace("'", "''") if not isinstance(v, list) else ",".join(str(x).replace("'", "''") for x in v)
            literal = raw_val
        elif isinstance(v, list):
            literal = ",".join(_sql_escape_single(x) for x in v)
        else:
            literal = _sql_escape_single(v)
        for pattern_name in [var_name, k]:
            sql = re.sub(r"\$\{" + re.escape(pattern_name) + r"\}", literal, sql)
            sql = re.sub(r"\$" + re.escape(pattern_name) + r"\b", literal, sql)
    return sql


def build_ds_query_body(
    panel: dict,
    from_ms: int,
    to_ms: int,
    query_params: dict,
    name_to_ds: dict | None = None,
    debug: bool = False,
) -> dict:
    """从 panel 的 targets 构建 POST /api/ds/query 的 body。"""
    name_to_ds = name_to_ds or {}
    ds_resolved = resolve_datasource(panel.get("datasource"), query_params, name_to_ds)
    if not ds_resolved:
        ds_resolved = panel.get("datasource")

    targets = panel.get("targets") or []
    if not targets:
        return {"queries": [], "from": str(from_ms), "to": str(to_ms)}

    queries = []
    for i, t in enumerate(targets):
        if isinstance(t, str):
            q = {"refId": "A", "rawSql": t}
        else:
            q = dict(t)
        if "refId" not in q:
            q["refId"] = "A" if i == 0 else chr(ord("A") + i)
        if "rawSql" in q and q["rawSql"]:
            q["rawSql"] = _substitute_sql_macros(q["rawSql"], from_ms, to_ms, query_params)
        q.setdefault("datasource", ds_resolved)
        q.setdefault("intervalMs", 10800000)
        q.setdefault("maxDataPoints", 820)
        if isinstance(ds_resolved, dict) and ds_resolved.get("id") is not None:
            q["datasourceId"] = int(ds_resolved["id"])
        queries.append(q)

    body = {
        "queries": queries,
        "from": str(from_ms),
        "to": str(to_ms),
        "range": {
            "from": _ms_to_iso(from_ms),
            "to": _ms_to_iso(to_ms),
            "raw": {
                "from": str(query_params.get("from", "now-90d")),
                "to": str(query_params.get("to", "now")),
            },
        },
    }
    return body


def query_panel_data(
    base: str,
    org_id: str,
    token: str,
    panel: dict,
    from_ms: int,
    to_ms: int,
    query_params: dict,
    name_to_ds: dict,
    verbose: bool,
    debug: bool = False,
) -> dict:
    """对单个 panel 调用 POST /api/ds/query，返回解析后的数据结构。"""
    _, ds_type = get_datasource_uid(panel, {})
    body = build_ds_query_body(panel, from_ms, to_ms, query_params, name_to_ds, debug=debug)
    if not body["queries"]:
        return {"columns": [], "rows": []}

    url = f"{base}/api/ds/query"
    params = {"ds_type": ds_type, "requestId": f"Q{panel.get('id', 0)}"}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Grafana-Org-Id": str(org_id),
    }
    if verbose:
        print(f"[verbose] POST {url}", file=sys.stderr)

    with httpx.Client(timeout=120.0) as client:
        resp = client.post(url, params=params, json=body, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    result = frames_to_structured(data, panel.get("title") or "unknown")
    if debug:
        rows = result.get("rows") or []
        print(f"[debug] Panel {panel.get('title') or '?'}: {len(result.get('columns') or [])} cols, {len(rows)} rows", file=sys.stderr)
    return result


def _field_display_name(f: dict) -> str:
    """从 Grafana field 生成列名：name + labels（若有），格式与表格一致 weighted_auc {key="value", ...}。"""
    name = f.get("name") or f.get("displayName") or "unknown"
    labels = f.get("labels")
    if labels and isinstance(labels, dict):
        parts = ", ".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        name = f"{name} {{{parts}}}"
    return name


def frames_to_structured(response: dict, panel_title: str) -> dict:
    """将 Grafana 返回的 results/frames 转为 { columns, rows } 结构；列名含 labels 时格式为 name {key="value", ...}。"""
    columns = []
    rows = []

    # 新格式: { "results": { "A": { "frames": [ { "schema": { "fields": [...] }, "data": { "values": [...] } } ] } } }
    results = response.get("results") or {}
    for ref_id, ref_data in results.items():
        frames = ref_data.get("frames") or []
        for frame in frames:
            schema = frame.get("schema") or {}
            fields = schema.get("fields") or []
            data = frame.get("data") or {}
            values = data.get("values") or []

            if not fields:
                continue
            for f in fields:
                columns.append(_field_display_name(f))
            if values:
                n_cols = len(fields)
                n_rows = len(values[0]) if values else 0
                for r in range(n_rows):
                    row = []
                    for c in range(n_cols):
                        row.append(values[c][r] if c < len(values) and r < len(values[c]) else None)
                    rows.append(row)

    # 若为旧格式或无 results，尝试直接 frames
    if not columns and not rows:
        frames = response.get("frames") or []
        for frame in frames:
            schema = frame.get("schema") or {}
            fields = schema.get("fields") or []
            data = frame.get("data") or {}
            values = data.get("values") or []
            if not fields:
                continue
            for f in fields:
                columns.append(_field_display_name(f))
            if values:
                n_cols = len(fields)
                n_rows = len(values[0]) if values else 0
                for r in range(n_rows):
                    row = []
                    for c in range(n_cols):
                        row.append(values[c][r] if c < len(values) and r < len(values[c]) else None)
                    rows.append(row)

    return {"columns": columns, "rows": rows}


def format_json(panels_data: dict) -> str:
    """输出 JSON：按 panel 标题分组，每 panel 统一 { columns, rows }。"""
    out = {}
    for title, data in panels_data.items():
        out[title] = {"columns": data.get("columns", []), "rows": data.get("rows", [])}
    return json.dumps(out, indent=2, ensure_ascii=False)


def format_table(panels_data: dict) -> str:
    """输出表格：每个 panel 一段，## Title + 表头 + 行。"""
    lines = []
    for title, data in panels_data.items():
        lines.append(f"## {title}")
        cols = data.get("columns") or []
        rows = data.get("rows") or []
        if cols:
            lines.append("\t".join(str(c) for c in cols))
        for row in rows:
            lines.append("\t".join(str(x) for x in row))
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="EGO 训练效果指标对比：从 Grafana 拉取指定区块（Versioned-level / Job-level Model Performance Comparison）Panel 数据。"
    )
    parser.add_argument("--url", required=True, help="已组装好所有 URL 参数的完整 Grafana dashboard link")
    parser.add_argument("--token", default=os.environ.get("GRAFANA_API_TOKEN"), help="Grafana Bearer token（建议用环境变量 GRAFANA_API_TOKEN）")
    parser.add_argument(
        "--block",
        choices=BLOCK_CHOICES,
        default="versioned",
        help="拉取的区块：versioned=Versioned-level（默认）, job=Job-level, both=两个区块",
    )
    parser.add_argument("--all-panels", action="store_true", help="获取该区块下所有 panel")
    parser.add_argument("--panels", nargs="*", metavar="TITLE", help="只获取指定标题的 panel")
    parser.add_argument("--from", dest="from_", metavar="TIME", help="覆盖 URL 中的 from，如 now-7d")
    parser.add_argument("--to", metavar="TIME", help="覆盖 URL 中的 to，如 now")
    parser.add_argument("--output", choices=("json", "table"), default="json", help="输出格式")
    parser.add_argument("--out-file", metavar="PATH", help="写入文件，不传则 stdout")
    parser.add_argument("--list-blocks", action="store_true", help="仅列出 dashboard 中所有 row 区块标题后退出（用于确认 --block job 对应名称）")
    parser.add_argument("--verbose", action="store_true", help="打印请求信息便于排查")
    parser.add_argument("--debug", action="store_true", help="打印简要步骤信息与 panel 行列数，便于排查")
    args = parser.parse_args()

    if not args.token or not str(args.token).strip():
        print("Error: GRAFANA_API_TOKEN environment variable or --token is required.", file=sys.stderr)
        return 1

    try:
        parsed = parse_url(args.url)
    except Exception as e:
        print(f"Error: Failed to parse URL: {e}", file=sys.stderr)
        return 1

    if args.debug:
        print(f"[debug] Parsed: base={parsed['base']}, uid={parsed['uid']}, orgId={parsed['org_id']}", file=sys.stderr)

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

    try:
        dashboard = get_dashboard(base, uid, org_id, args.token, query_params, args.verbose)
    except httpx.HTTPStatusError as e:
        print(f"Error: Dashboard request failed HTTP {e.response.status_code}: {e.response.text[:500]}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: Failed to get dashboard: {e}", file=sys.stderr)
        return 1

    if args.list_blocks:
        panels = dashboard.get("panels") or []
        rows_with_counts: list[tuple[str, int]] = []
        for p in panels:
            if p.get("type") == "row":
                title = (p.get("title") or "").strip()
                count = len(find_block_panels(dashboard, title))
                rows_with_counts.append((title, count))
        if not rows_with_counts:
            print("No row blocks found in dashboard.", file=sys.stderr)
            return 0
        for title, num_panels in rows_with_counts:
            print(f"{num_panels}\t{title}")
        return 0

    if args.debug:
        tlist = dashboard.get("templating")
        var_list = tlist if isinstance(tlist, list) else (tlist or {}).get("list", [])
        print(f"[debug] Dashboard: {len(var_list)} template vars", file=sys.stderr)

    try:
        datasources = get_datasources(base, org_id, args.token)
        name_to_ds = {}
        for d in datasources:
            if d.get("name") and d.get("uid"):
                name_to_ds[d["name"]] = {
                    "id": d.get("id"),
                    "uid": d["uid"],
                    "type": d.get("type") or "mysql",
                }
    except Exception as e:
        if args.verbose:
            print(f"[verbose] Could not fetch datasources: {e}", file=sys.stderr)
        name_to_ds = {}

    block_titles = resolve_block_titles(args.block)
    # 收集 (block_title, panel)，多区块时输出 key 用 "BlockTitle / PanelTitle" 区分
    selected_with_block: list[tuple[str, dict]] = []
    for block_title in block_titles:
        block_panels = find_block_panels(dashboard, block_title)
        if not block_panels:
            if args.block != "both" or args.verbose:
                print(f"[verbose] Block row '{block_title}' not found or has no panels.", file=sys.stderr)
            continue
        filtered = filter_panels(block_panels, DEFAULT_PANEL_TITLES, args.all_panels, args.panels)
        for panel in filtered:
            selected_with_block.append((block_title, panel))

    if not selected_with_block:
        print(
            "Warning: No panels in selected block(s). Writing empty result. "
            "Use --list-blocks to see row titles and panel counts.",
            file=sys.stderr,
        )
        panels_data = {}

    # 当无法列出 datasources（如 403）时，用 panel 的 datasource UID 或变量值（名称）逐个拉取以拿到 id
    if not name_to_ds:
        for _block_title, panel in selected_with_block:
            ds = panel.get("datasource")
            if isinstance(ds, dict):
                u = ds.get("uid")
                if u and isinstance(u, str):
                    if u.startswith("${") and u.endswith("}"):
                        var_name = u[2:-1].strip()
                        name = query_params.get(var_name) or query_params.get("var-" + var_name)
                        if isinstance(name, list):
                            name = name[0] if name else None
                        if name and name not in name_to_ds:
                            info = get_datasource_by_name(base, org_id, args.token, str(name))
                            if info:
                                name_to_ds[name] = {
                                    "id": info.get("id"),
                                    "uid": info.get("uid"),
                                    "type": info.get("type") or "mysql",
                                }
                                if args.verbose:
                                    print(f"[verbose] Fetched datasource by name {name!r} -> id={info.get('id')}", file=sys.stderr)
                            else:
                                # 无 API 权限时使用脚本内写死的 datasource 配置
                                if name in FALLBACK_DATASOURCE_BY_NAME:
                                    name_to_ds[name] = dict(FALLBACK_DATASOURCE_BY_NAME[name])
                                    if args.verbose:
                                        print(f"[verbose] Using fallback datasource for {name!r} -> id={name_to_ds[name].get('id')}", file=sys.stderr)
                    elif u not in name_to_ds:
                        info = get_datasource_by_uid(base, org_id, args.token, u)
                        if info:
                            name_to_ds[u] = {
                                "id": info.get("id"),
                                "uid": info.get("uid", u),
                                "type": info.get("type") or "mysql",
                            }
                            if args.verbose:
                                print(f"[verbose] Fetched datasource by uid {u!r} -> id={info.get('id')}", file=sys.stderr)

    # URL 里为 All 的 var-* 变量：优先用 dashboard 返回的 options，否则执行变量 query 获取实际取值列表
    resolved_params = resolve_all_from_dashboard(
        dashboard,
        query_params,
        name_to_ds,
        base,
        org_id,
        args.token,
        from_ms,
        to_ms,
        args.verbose,
        args.debug,
    )
    # ds/query 所需但 URL 未传的变量（如 job_types、xgauc_path）：从 dashboard templating 解析并填充
    fill_missing_vars_from_dashboard(dashboard, resolved_params, args.verbose, args.debug)

    use_block_prefix = len(block_titles) > 1
    panels_data = {}
    for block_title, panel in selected_with_block:
        panel_title = (panel.get("title") or "unknown").strip()
        data_key = f"{block_title} / {panel_title}" if use_block_prefix else panel_title
        try:
            data = query_panel_data(
                base,
                org_id,
                args.token,
                panel,
                from_ms,
                to_ms,
                resolved_params,
                name_to_ds,
                args.verbose,
                debug=args.debug,
            )
            panels_data[data_key] = data
        except httpx.HTTPStatusError as e:
            body_preview = (e.response.text or "")[:500]
            print(f"Error: Panel '{data_key}' query failed HTTP {e.response.status_code}: {body_preview}", file=sys.stderr)
            if e.response.status_code == 500:
                try:
                    err_json = e.response.json()
                    if isinstance(err_json, dict) and err_json.get("error"):
                        print(f"  Server error: {err_json.get('error')}", file=sys.stderr)
                    if args.debug:
                        print(f"[debug] Full response: {e.response.text}", file=sys.stderr)
                except Exception:
                    if args.debug:
                        print(f"[debug] Full response: {e.response.text}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error: Panel '{data_key}' failed: {e}", file=sys.stderr)
            return 1

    if args.output == "json":
        out_text = format_json(panels_data)
    else:
        out_text = format_table(panels_data)

    if args.out_file:
        with open(args.out_file, "w", encoding="utf-8") as f:
            f.write(out_text)
    else:
        print(out_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
