"""
AB Platform API Proxy for Samaritan Bot.

Receives simplified slot values from COTA Form executer,
constructs the full AB API request with proper headers,
and returns formatted results.

Runs on port 5009.
"""

import json
import asyncio
import aiohttp
import os
import re
from datetime import datetime, timedelta
from sanic import Sanic, Request, text
from sanic.response import json as json_response

app = Sanic("ab_proxy")

# ============================================================
# Short-lived response cache to prevent duplicate upstream calls.
# COTA's dialogue loop can trigger the same executer request many
# times in a single turn.  We cache by request-body hash for 60s.
# ============================================================
_response_cache: dict[str, tuple[float, dict]] = {}  # hash -> (timestamp, response_json)
CACHE_TTL_SECONDS = 60


def _cache_key(params: dict) -> str:
    """Deterministic hash of the request params for cache lookup."""
    import hashlib
    canonical = json.dumps(params, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def _cache_get(key: str) -> dict | None:
    """Return cached response if still valid, else None."""
    entry = _response_cache.get(key)
    if entry is None:
        return None
    ts, resp = entry
    if datetime.now().timestamp() - ts > CACHE_TTL_SECONDS:
        _response_cache.pop(key, None)
        return None
    return resp


def _cache_set(key: str, resp: dict) -> None:
    """Store a response in cache with current timestamp."""
    _response_cache[key] = (datetime.now().timestamp(), resp)
    # Evict old entries to prevent unbounded growth
    cutoff = datetime.now().timestamp() - CACHE_TTL_SECONDS * 2
    stale = [k for k, (ts, _) in _response_cache.items() if ts < cutoff]
    for k in stale:
        _response_cache.pop(k, None)


def _is_truthy(value) -> bool:
    """Parse common truthy values from bool/int/string."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "on"}


def _should_disable_cache(request: Request, params: dict) -> bool:
    """Return True when cache should be bypassed for this request."""
    if _is_truthy(os.getenv("AB_PROXY_DISABLE_CACHE", "0")):
        return True
    if _is_truthy(request.headers.get("X-Debug-No-Cache", "")):
        return True
    for key in ("no_cache", "_no_cache", "debug_no_cache", "_debug_no_cache"):
        if _is_truthy(params.get(key)):
            return True
    return False


# AB Platform configuration
AB_API_URL = "https://httpgateway.abtest.shopee.io/request_spex"
AB_TOKEN = os.getenv("AB_PLATFORM_TOKEN", "8E3679F4485D337E81AF86E5A9804B9D")
AB_CLIENT_SERVER_NAME = "Search_ItemSearch_mixrank_Report"
AB_DES_NAMESPACE_KEY = "content_intelligence.experiment_platform.abtest_admin_analysis.open_get_summary_key"
AB_DES_NAMESPACE_RESULT = "content_intelligence.experiment_platform.abtest_admin_analysis.open_get_summary_result"
INTERNAL_PROXY_TOKEN = os.getenv("SAMARITAN_INTERNAL_TOKEN", "samaritan-internal-token")
INTERNAL_PROXY_AUTH_HEADER = "X-Samaritan-Internal-Token"

# Default values for Search team
DEFAULT_PROJECT_ID = 27
DEFAULT_TEMPLATE_NAME = "One Page - Search Core Metric"
DEFAULT_TEMPLATE_GROUP_NAME = os.getenv("AB_TEMPLATE_GROUP_NAME", "(org+ads)  by card")
FALLBACK_TEMPLATE_GROUP_NAME = os.getenv("AB_TEMPLATE_GROUP_FALLBACK", "Rollout Checklist")
DEFAULT_TEMPLATE_GROUP_TYPE = 1
DEFAULT_NORMALIZATION = "control"
DEFAULT_METRICS = ["order_cnt", "gmv", "gmv_995", "ads_revenue_usd", "order_per_uu", "gmv_per_uu", "gmv_per_uu_995"]
DEFAULT_DIMS = ["abtest_group", "abtest_region", "abtest_date"]
CARD_TYPE_DIM = "card_type"
SORT_TYPE_DIM = "sort_type"
DEFAULT_CARD_TYPE = "allcard"
DEFAULT_SORT_TYPE = "__ALL__"
DEFAULT_CONTROL_BY_EXPERIMENT = {
    6850: "31430;31438",
}
RESULT_POLL_MAX_ATTEMPTS = int(os.getenv("AB_RESULT_POLL_MAX_ATTEMPTS", "6"))
RESULT_POLL_INTERVAL_SECONDS = int(os.getenv("AB_RESULT_POLL_INTERVAL_SECONDS", "3"))
MAX_ROWS_IN_RESPONSE = 20
ENABLE_LOCAL_CONTROL_SYNTHESIS = _is_truthy(os.getenv("AB_ENABLE_LOCAL_CONTROL_SYNTHESIS", "0"))
_DIR = os.path.dirname(os.path.abspath(__file__))
BUCKET_MAPPING_CANDIDATE_PATHS = [
    os.path.join(os.path.dirname(_DIR), "Bucket_mapping.txt"),
    os.path.join(_DIR, "Bucket_mapping.txt"),
]


def get_default_dates():
    """Return default date range: 7 days ago to yesterday."""
    yesterday = datetime.now() - timedelta(days=1)
    week_ago = yesterday - timedelta(days=6)
    return week_ago.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d")


def _split_slot_values(value) -> list[str]:
    """Normalize slot values that may arrive as CSV string, JSON list string, or list."""
    if value is None:
        return []

    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]

    value_str = str(value).strip()
    if not value_str:
        return []

    # Handle values like '["82944","82945"]'
    if value_str.startswith("[") and value_str.endswith("]"):
        try:
            parsed = json.loads(value_str)
            if isinstance(parsed, list):
                return [str(v).strip() for v in parsed if str(v).strip()]
        except json.JSONDecodeError:
            pass

    return [v.strip() for v in value_str.split(",") if v.strip()]


def _load_bucket_mapping() -> dict[str, str]:
    """Load bucket aliases from Bucket_mapping.txt (if present)."""
    mapping: dict[str, str] = {}
    for path in BUCKET_MAPPING_CANDIDATE_PATHS:
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue

                    key = ""
                    value = ""
                    if "=" in line:
                        key, value = line.split("=", 1)
                    elif ":" in line:
                        key, value = line.split(":", 1)
                    else:
                        parts = line.split()
                        if len(parts) >= 2:
                            key, value = parts[0], parts[1]

                    key = key.strip()
                    value = value.strip()
                    if not key or not value:
                        continue

                    mapping[key.lower()] = value
        except Exception as e:
            print(f"[AB Proxy] Failed to load bucket mapping from {path}: {e}")

    return mapping


def _resolve_bucket_aliases(values: list[str], alias_mapping: dict[str, str]) -> list[str]:
    """Resolve bucket aliases such as bucket_id_09 to numeric bucket IDs."""
    resolved: list[str] = []
    for value in values:
        token = str(value).strip()
        if not token:
            continue
        if token.isdigit():
            resolved.append(token)
            continue
        mapped = alias_mapping.get(token.lower())
        resolved.append(mapped if mapped else token)
    return resolved


def _normalize_control_group(value) -> str:
    """
    Normalize control group input.

    AB API expects:
    - non-combine: "1613"
    - combine: "1613;1773"
    """
    if value is None:
        return ""

    if isinstance(value, list):
        parts = [str(v).strip() for v in value if str(v).strip()]
        return ";".join(parts) if len(parts) > 1 else (parts[0] if parts else "")

    text_value = str(value).strip()
    if not text_value:
        return ""

    # Keep semicolon format as-is for combine groups.
    if ";" in text_value:
        return ";".join([p.strip() for p in text_value.split(";") if p.strip()])

    # Support accidental separators from NL extraction such as "," or "&".
    if "," in text_value or "&" in text_value:
        normalized = text_value.replace("&", ",")
        parts = [p.strip() for p in normalized.split(",") if p.strip()]
        return ";".join(parts) if len(parts) > 1 else (parts[0] if parts else "")

    return text_value


def _parse_row(columns: list[str], row: str) -> dict[str, str]:
    """Parse a || separated row into a dict keyed by column names."""
    values = row.split("||")
    return {col: (values[i] if i < len(values) else "") for i, col in enumerate(columns)}


def _identify_dim_and_metric_columns(columns: list[str]) -> tuple[list[str], list[str]]:
    """Split columns into dimension columns and metric columns."""
    known_dims = {"abtest_group", "abtest_region", "abtest_date", "card_type", "sort_type", "group", "region", "date"}
    dims = [c for c in columns if c.lower() in known_dims]
    metrics = [c for c in columns if c.lower() not in known_dims]
    return dims, metrics


def _card_type_matches(value: str, expected: str) -> bool:
    """Match card_type robustly across template-specific naming."""
    v = str(value or "").strip().lower()
    e = str(expected or "").strip().lower()
    if not e:
        return True
    if e in ("allcard", "all_card", "all"):
        # Strict all-card mode: keep only the explicit allcard bucket.
        return v in {"allcard", "all_card", "all"}
    return v == e


def _sort_type_matches(value: str, expected: str) -> bool:
    """Match sort_type; default __ALL__ should match all/all-like labels only."""
    v = str(value or "").strip().lower()
    e = str(expected or "").strip().lower()
    if not e:
        return True
    if e in ("__all__", "all"):
        return v in {"__all__", "all"}
    return v == e


def _fmt_change(val_str: str) -> str:
    """Format a relative change value as a readable percentage string."""
    if not val_str or val_str.strip() in ("", "-", "N/A", "nan", "null"):
        return "-"
    try:
        num = float(val_str)
        if num == 0:
            return "0%"
        sign = "+" if num > 0 else ""
        # Keep original precision if it looks intentional, otherwise trim
        return f"{sign}{val_str}%"
    except (ValueError, TypeError):
        return val_str


def _fmt_number(val_str: str) -> str:
    """Best-effort formatting of numeric strings for readability (add thousand separators)."""
    if not val_str or val_str.strip() in ("", "-", "N/A", "nan", "null"):
        return "-"
    try:
        num = float(val_str)
        if num == int(num) and "." not in val_str:
            return f"{int(num):,}"
        # Preserve original decimal places
        return f"{num:,.{_decimal_places(val_str)}f}"
    except (ValueError, TypeError):
        return val_str


def _decimal_places(val_str: str) -> int:
    """Count decimal places in a string representation of a number."""
    if "." in val_str:
        return len(val_str.rstrip("0").split(".")[-1]) or 1
    return 0


def _dim_context_str(row: dict[str, str], dims: list[str]) -> str:
    """Build a compact dimension context label, omitting the noisy abtest_ prefix."""
    parts = []
    for d in dims:
        val = row.get(d, "")
        if not val:
            continue
        # Clean up column name for display
        short_name = d.replace("abtest_", "")
        parts.append(f"{short_name}={val}")
    return ", ".join(parts)


def _build_dim_key(row: dict[str, str], dims: list[str], exclude: str = "abtest_group") -> tuple:
    """Build a hashable dimension key for grouping, excluding group column."""
    return tuple(row.get(d, "") for d in dims if d != exclude)


def format_ab_results(
    result_data: dict,
    request_body: dict,
    key_info: dict,
    poll_attempts: int,
    card_type_filter: str = DEFAULT_CARD_TYPE,
    sort_type_filter: str = DEFAULT_SORT_TYPE,
) -> str:
    """Format AB result payload into a readable comparison table.

    Output format (example for single date + single region):

        AB Report | Exp 6850
        2026-02-10 | MY
        Control: 31430;31438 | Treatment: 31424

        Metric            Control     Treatment   Change
        ------------------------------------------------
        order_cnt          12,345        12,400   +0.45%
        gmv             67,890.50     68,000.00   +0.16%
        ads_revenue_usd  1,234.56      1,230.00   -0.37%

    For multiple dates/regions, groups data by dimension.
    For multiple treatments, adds extra treatment columns.
    """
    try:
        output_lines: list[str] = []
        exp_id = request_body.get("experiment_id")
        date_range = request_body.get("dates", [{}])[0]
        date_start = date_range.get("time_start", "")
        date_end = date_range.get("time_end", "")
        regions = request_body.get("regions", [])
        control = request_body.get("control", "")
        treatments = request_body.get("treatments", [])

        # --- Compact header ---
        date_str = date_start if date_start == date_end else f"{date_start} to {date_end}"
        region_str = ",".join(regions) if regions else "ALL"
        treat_str = ", ".join(treatments)

        output_lines.append(f"AB Report | Exp {exp_id}")
        output_lines.append(f"{date_str} | {region_str}")
        output_lines.append(f"Control: {control} | Treatment: {treat_str}")

        retcode = result_data.get("retcode")
        msg = result_data.get("msg")
        if retcode not in (0, "0", None):
            output_lines.append(f"API warning: retcode={retcode}, msg={msg}")

        payload = result_data.get("data")
        if not isinstance(payload, dict):
            output_lines.append("")
            output_lines.append("No data returned.")
            return "\n".join(output_lines)

        header = payload.get("header", "")
        columns = header.split("||") if isinstance(header, str) and header else []
        body_rows_raw = payload.get("body", []) if isinstance(payload.get("body"), list) else []
        relative_rows_raw = payload.get("relative", []) if isinstance(payload.get("relative"), list) else []
        control_indexes = payload.get("control_group_indexes", [])
        if isinstance(control_indexes, list):
            control_indexes = [int(i) for i in control_indexes]
        else:
            control_indexes = []

        if not columns or not body_rows_raw:
            output_lines.append("")
            output_lines.append("No data rows returned.")
            return "\n".join(output_lines)

        dims, metrics = _identify_dim_and_metric_columns(columns)

        # Parse all rows
        raw_row_count = len(body_rows_raw)
        body_parsed = [_parse_row(columns, r) for r in body_rows_raw]
        rel_parsed = [_parse_row(columns, r) for r in relative_rows_raw]

        # Default card_type behavior: keep only target card_type rows when present.
        # This keeps output aligned with the "card_type=allcard" expectation.
        ct_filter = str(card_type_filter or DEFAULT_CARD_TYPE).strip().lower()
        if ct_filter and any(c.lower() == "card_type" for c in columns):
            keep_indexes = []
            for i, brow in enumerate(body_parsed):
                if _card_type_matches(brow.get("card_type", ""), ct_filter):
                    keep_indexes.append(i)

            # For all-card mode, allow "__ALL__*" as pragmatic fallback because
            # some templates expose no literal "allcard" row.
            if not keep_indexes and ct_filter in ("allcard", "all_card", "all"):
                for i, brow in enumerate(body_parsed):
                    v = str(brow.get("card_type", "")).strip().lower()
                    if v.startswith("__all__"):
                        keep_indexes.append(i)

            if keep_indexes:
                body_rows_raw = [body_rows_raw[i] for i in keep_indexes]
                relative_rows_raw = [
                    relative_rows_raw[i] if i < len(relative_rows_raw) else ""
                    for i in keep_indexes
                ]
                body_parsed = [body_parsed[i] for i in keep_indexes]
                rel_parsed = [
                    rel_parsed[i] if i < len(rel_parsed) else {}
                    for i in keep_indexes
                ]
                if isinstance(control_indexes, list):
                    old_to_new = {old_i: new_i for new_i, old_i in enumerate(keep_indexes)}
                    control_indexes = [old_to_new[i] for i in control_indexes if i in old_to_new]
            else:
                # Never fall back to full-card_type output when filter was requested.
                body_rows_raw = []
                relative_rows_raw = []
                body_parsed = []
                rel_parsed = []
                control_indexes = []
        if ct_filter and any(c.lower() == "card_type" for c in columns):
            print(f"[AB Proxy] card_type filter: '{ct_filter}' rows {raw_row_count} -> {len(body_rows_raw)}")

        st_filter = str(sort_type_filter or "").strip().lower()
        if st_filter and any(c.lower() == "sort_type" for c in columns):
            pre_rows = len(body_rows_raw)
            keep_indexes = []
            for i, brow in enumerate(body_parsed):
                if _sort_type_matches(brow.get("sort_type", ""), st_filter):
                    keep_indexes.append(i)
            if keep_indexes:
                body_rows_raw = [body_rows_raw[i] for i in keep_indexes]
                relative_rows_raw = [
                    relative_rows_raw[i] if i < len(relative_rows_raw) else ""
                    for i in keep_indexes
                ]
                body_parsed = [body_parsed[i] for i in keep_indexes]
                rel_parsed = [
                    rel_parsed[i] if i < len(rel_parsed) else {}
                    for i in keep_indexes
                ]
                if isinstance(control_indexes, list):
                    old_to_new = {old_i: new_i for new_i, old_i in enumerate(keep_indexes)}
                    control_indexes = [old_to_new[i] for i in control_indexes if i in old_to_new]
            else:
                body_rows_raw = []
                relative_rows_raw = []
                body_parsed = []
                rel_parsed = []
                control_indexes = []
            print(f"[AB Proxy] sort_type filter: '{st_filter}' rows {pre_rows} -> {len(body_rows_raw)}")

        # Group rows by non-group dimensions (date, region) to build comparison tables.
        # Each dimension-group gets one table with Control + Treatment(s) side by side.
        from collections import OrderedDict

        DimGroupEntry = dict  # {"body": parsed_row, "rel": parsed_row, "group_id": str}
        dim_groups: OrderedDict[tuple, dict[str, list[DimGroupEntry]]] = OrderedDict()

        for idx, brow in enumerate(body_parsed):
            dim_key = _build_dim_key(brow, dims, exclude="abtest_group")
            if dim_key not in dim_groups:
                dim_groups[dim_key] = {"control": [], "treatment": []}

            rrow = rel_parsed[idx] if idx < len(rel_parsed) else {}
            entry: DimGroupEntry = {
                "body": brow,
                "rel": rrow,
                "group_id": brow.get("abtest_group", ""),
            }
            if idx in control_indexes:
                dim_groups[dim_key]["control"].append(entry)
            else:
                dim_groups[dim_key]["treatment"].append(entry)

        # The AB API returns individual control buckets (e.g. 31430, 31438) as
        # "treatment" rows alongside the actual treatment bucket.  We must
        # always separate them so the output only shows the real treatments.
        control_bucket_ids = set()
        raw_control = control.replace(" ", "")
        for cid in raw_control.split(";"):
            cid = cid.strip()
            if cid:
                control_bucket_ids.add(cid)

        for dim_key, grp in dim_groups.items():
            ctrl_list = grp["control"]
            treat_list = grp["treatment"]

            if control_bucket_ids and treat_list:
                real_treats = []
                ctrl_bucket_rows = []
                for t in treat_list:
                    gid = t["group_id"]
                    if gid in control_bucket_ids:
                        ctrl_bucket_rows.append(t)
                    else:
                        real_treats.append(t)

                grp["treatment"] = real_treats
                treat_list = real_treats

                # When control row is missing (e.g., control_group_indexes is empty)
                # or aggregate control metrics are empty, synthesize control from
                # individual control bucket rows and compute treatment relative diff.
                ctrl_values_empty = (
                    (not ctrl_list)
                    or all(
                        not ctrl_list[0]["body"].get(m, "").strip()
                        or ctrl_list[0]["body"].get(m, "").strip() == "-"
                        for m in metrics
                    )
                )

                if ctrl_values_empty and ctrl_bucket_rows and ENABLE_LOCAL_CONTROL_SYNTHESIS:
                    agg_body: dict[str, str] = dict(ctrl_bucket_rows[0]["body"])
                    for m in metrics:
                        vals = []
                        for cb in ctrl_bucket_rows:
                            raw_val = cb["body"].get(m, "").strip()
                            if raw_val and raw_val != "-":
                                try:
                                    vals.append(float(raw_val))
                                except ValueError:
                                    pass
                        agg_body[m] = str(sum(vals) / len(vals)) if vals else ""

                    for rt in real_treats:
                        new_rel = dict(rt["rel"])
                        for m in metrics:
                            ctrl_num_str = agg_body.get(m, "").strip()
                            treat_num_str = rt["body"].get(m, "").strip()
                            if ctrl_num_str and treat_num_str and ctrl_num_str != "-" and treat_num_str != "-":
                                try:
                                    c = float(ctrl_num_str)
                                    t = float(treat_num_str)
                                    new_rel[m] = str((t - c) / c) if c != 0 else ""
                                except (ValueError, ZeroDivisionError):
                                    pass
                        rt["rel"] = new_rel

                    agg_entry = {
                        "body": agg_body,
                        "rel": {},
                        "group_id": ctrl_list[0]["group_id"] if ctrl_list else "control",
                    }
                    grp["control"] = [agg_entry]
                    ctrl_list = grp["control"]
                elif ctrl_values_empty and ctrl_bucket_rows and not ENABLE_LOCAL_CONTROL_SYNTHESIS:
                    print("[AB Proxy] Skip local control synthesis (AB_ENABLE_LOCAL_CONTROL_SYNTHESIS=0)")

        # Determine whether we need per-group sub-headers
        # (skip if only one dimension group — info is already in the main header)
        multi_groups = len(dim_groups) > 1

        for dim_key, grp in dim_groups.items():
            ctrl_list = grp["control"]
            treat_list = grp["treatment"]

            if not ctrl_list and not treat_list:
                continue

            # Sub-header for this dimension group (only if multiple groups)
            if multi_groups:
                # Build a readable dimension label
                non_group_dims = [d for d in dims if d != "abtest_group"]
                dim_label_parts = []
                sample_row = (ctrl_list or treat_list)[0]["body"]
                for d in non_group_dims:
                    val = sample_row.get(d, "")
                    if val:
                        dim_label_parts.append(val)
                output_lines.append("")
                output_lines.append(f"[ {' | '.join(dim_label_parts)} ]")

            # === Simple case: 1 control group, 1 treatment group ===
            if len(ctrl_list) <= 1 and len(treat_list) == 1:
                ctrl_body = ctrl_list[0]["body"] if ctrl_list else {}
                treat_body = treat_list[0]["body"]
                treat_rel = treat_list[0]["rel"]

                # Find max metric name length for alignment
                max_name = max((len(m) for m in metrics), default=10)
                col_w = 14  # width for value columns

                header_line = f"{'Metric':<{max_name}}  {'Control':>{col_w}}  {'Treatment':>{col_w}}  {'Change':>10}"
                sep = "-" * len(header_line)

                output_lines.append("")
                output_lines.append(header_line)
                output_lines.append(sep)

                for m in metrics:
                    ctrl_val = _fmt_number(ctrl_body.get(m, "")) if ctrl_body else "-"
                    treat_val = _fmt_number(treat_body.get(m, ""))
                    change = _fmt_change(treat_rel.get(m, ""))
                    output_lines.append(
                        f"{m:<{max_name}}  {ctrl_val:>{col_w}}  {treat_val:>{col_w}}  {change:>10}"
                    )

            # === Multi-treatment case ===
            elif treat_list:
                max_name = max((len(m) for m in metrics), default=10)
                col_w = 14

                # Build column headers: Control, then each treatment by group_id
                col_headers = ["Control"]
                for t in treat_list:
                    gid = t["group_id"]
                    col_headers.append(f"T-{gid}" if gid else "Treatment")

                header_parts = [f"{'Metric':<{max_name}}"]
                header_parts.extend(f"{h:>{col_w}}" for h in col_headers)
                header_parts.append(f"{'Change':>10}")
                header_line = "  ".join(header_parts)
                sep = "-" * len(header_line)

                output_lines.append("")
                output_lines.append(header_line)
                output_lines.append(sep)

                ctrl_body = ctrl_list[0]["body"] if ctrl_list else {}

                for m in metrics:
                    parts = [f"{m:<{max_name}}"]
                    ctrl_val = _fmt_number(ctrl_body.get(m, "")) if ctrl_body else "-"
                    parts.append(f"{ctrl_val:>{col_w}}")

                    # Treatment values + collect changes
                    changes = []
                    for t in treat_list:
                        t_val = _fmt_number(t["body"].get(m, ""))
                        parts.append(f"{t_val:>{col_w}}")
                        changes.append(_fmt_change(t["rel"].get(m, "")))

                    # Show change(s) — if single treatment, single change; else comma-separated
                    change_str = changes[0] if len(changes) == 1 else ",".join(changes)
                    parts.append(f"{change_str:>10}")
                    output_lines.append("  ".join(parts))

            # Edge case: only control rows, no treatment
            elif ctrl_list and not treat_list:
                output_lines.append("")
                output_lines.append("(Only control data found, no treatment rows)")
                for m in metrics:
                    for c in ctrl_list:
                        val = _fmt_number(c["body"].get(m, ""))
                        output_lines.append(f"  {m}: {val}")

        # Truncation warning
        total_rows_shown = sum(
            len(g["control"]) + len(g["treatment"]) for g in dim_groups.values()
        )
        if len(body_rows_raw) > MAX_ROWS_IN_RESPONSE:
            output_lines.append(
                f"\n... showing {total_rows_shown} of {len(body_rows_raw)} rows"
            )

        return "\n".join(output_lines)

    except Exception as e:
        return f"Error formatting results: {str(e)}\nRaw data: {json.dumps(result_data, ensure_ascii=False)[:2000]}"


def _build_ab_headers(experiment_id: int, namespace: str) -> dict:
    return {
        "X-Client-Server-Name": AB_CLIENT_SERVER_NAME,
        "X-Des-Namespace": namespace,
        "X-Token": AB_TOKEN,
        "X-Request-Id": f"samaritan-{experiment_id}-{namespace.split('.')[-1]}-{int(datetime.now().timestamp())}",
        "Content-Type": "application/json",
    }


def _is_template_group_not_exists(result: dict) -> bool:
    """Return True when AB API says template group is unavailable."""
    msg = str(result.get("msg", "")).lower()
    return "template group name not exists" in msg


def _result_has_data(formatted: str) -> bool:
    """Return False if the formatted result has no useful metric data (all dashes or no rows)."""
    if not formatted:
        return False
    for marker in ("No data returned", "No data rows returned", "still running", "error", "failed"):
        if marker.lower() in formatted.lower():
            return False
    lines = formatted.splitlines()
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Metric") and "Change" in stripped:
            in_table = True
            continue
        if in_table and re.fullmatch(r"-{5,}", stripped):
            continue
        if in_table and stripped:
            parts = [p for p in re.split(r"\s{2,}", stripped) if p]
            if len(parts) >= 2:
                values = parts[1:]
                if any(v.strip() not in ("", "-") for v in values):
                    return True
    return False


async def _call_ab_api(session: aiohttp.ClientSession, namespace: str, request_body: dict, experiment_id: int) -> tuple[int, dict]:
    """Call AB API for the given namespace and return (http_status, payload)."""
    headers = _build_ab_headers(experiment_id, namespace)
    async with session.post(
        AB_API_URL,
        headers=headers,
        json=request_body,
        timeout=aiohttp.ClientTimeout(total=30),
    ) as response:
        if response.status == 200:
            return response.status, await response.json()
        return response.status, {"error_text": await response.text()}


def _extract_unique_card_types(result_payload: dict) -> list[str]:
    """Extract sorted unique card_type values from AB result payload."""
    data = (result_payload or {}).get("data") or {}
    header = data.get("header", "")
    body_rows = data.get("body") or []
    if not isinstance(header, str) or not header or not isinstance(body_rows, list):
        return []
    cols = header.split("||")
    if "card_type" not in cols:
        return []
    idx = cols.index("card_type")
    values: set[str] = set()
    for row in body_rows:
        parts = str(row).split("||")
        if idx < len(parts):
            val = str(parts[idx]).strip()
            if val:
                values.add(val)
    return sorted(values)


@app.post("/ab_report")
async def fetch_ab_report(request: Request):
    """
    Endpoint called by COTA Form executer.

    Expects slot values as JSON body:
    {
        "experiment_id": "15367",
        "date_start": "2026-02-01",
        "date_end": "2026-02-10",
        "regions": "TW",
        "control": "82930",
        "treatments": "82944"
    }
    """
    try:
        incoming_token = request.headers.get(INTERNAL_PROXY_AUTH_HEADER, "")
        if incoming_token != INTERNAL_PROXY_TOKEN:
            return json_response({"result": "Unauthorized"}, status=401)
        if not AB_TOKEN:
            return json_response({"result": "Missing AB platform token: set AB_PLATFORM_TOKEN"})
        params = request.json or {}
        print(f"[AB Proxy] Received request: {json.dumps(params, ensure_ascii=False)}")
        disable_cache = _should_disable_cache(request, params)
        if disable_cache:
            print("[AB Proxy] Cache BYPASS enabled for this request")

        # --- Deduplication cache: return cached result for identical requests ---
        ck = _cache_key(params)
        if not disable_cache:
            cached = _cache_get(ck)
            if cached is not None:
                print(f"[AB Proxy] Cache HIT — returning cached response (skipping upstream API call)")
                return json_response(cached)

        # Extract and validate required fields
        experiment_id = params.get("experiment_id", "")
        if not experiment_id:
            return json_response({"result": "Error: experiment_id is required"})

        experiment_id = int(str(experiment_id).strip())

        # Parse dates with defaults
        default_start, default_end = get_default_dates()
        date_start = params.get("date_start", "").strip()
        date_end = params.get("date_end", "").strip()

        if not date_start or date_start.lower() in ("default", "默认", ""):
            date_start = default_start
        if not date_end or date_end.lower() in ("default", "默认", ""):
            date_end = default_end

        # Date granularity:
        # - default: if querying a range, aggregate across date (remove abtest_date from dims)
        # - optional override: split_by_date/by_date=true to keep daily breakdown
        split_by_date = _is_truthy(params.get("split_by_date", False)) or _is_truthy(params.get("by_date", False))
        if date_start == date_end or split_by_date:
            dims = list(DEFAULT_DIMS)
        else:
            dims = [d for d in DEFAULT_DIMS if d != "abtest_date"]

        # Parse regions
        regions_str = str(params.get("regions", "")).strip()
        if not regions_str or regions_str.lower() in ("all", "全部", ""):
            # AB API expects explicit ALL marker; empty list returns business error.
            regions = ["ALL"]
        else:
            regions = [r.upper() for r in _split_slot_values(regions_str)]

        template_group_name = str(
            params.get("template_group_name", DEFAULT_TEMPLATE_GROUP_NAME)
        ).strip() or DEFAULT_TEMPLATE_GROUP_NAME
        is_by_card_template = "by card" in template_group_name.lower()

        # card_type:
        # - For "by card" templates, always include card_type dimension so
        #   allcard filtering aligns with page behavior and SQL expectation.
        # - For other templates, include card_type only when caller requests
        #   a specific non-allcard slice.
        card_type = str(params.get("card_type", DEFAULT_CARD_TYPE)).strip() or DEFAULT_CARD_TYPE
        if is_by_card_template or card_type.lower() not in ("allcard", "all_card", "all"):
            dims.append(CARD_TYPE_DIM)
        sort_type = str(params.get("sort_type", DEFAULT_SORT_TYPE)).strip() or DEFAULT_SORT_TYPE
        # To match page behavior, include sort_type dimension when explicitly specified
        # (including "__ALL__"), then filter rows in formatter.
        if sort_type:
            dims.append(SORT_TYPE_DIM)

        # Parse control and treatments
        alias_mapping = _load_bucket_mapping()

        control_raw = _normalize_control_group(params.get("control", ""))
        if not control_raw:
            default_control = DEFAULT_CONTROL_BY_EXPERIMENT.get(experiment_id, "")
            if default_control:
                control_raw = default_control
                print(f"[AB Proxy] control missing, fallback to default for exp {experiment_id}: {control_raw}")
        control_parts = [p.strip() for p in control_raw.split(";") if p.strip()]
        control_parts = _resolve_bucket_aliases(control_parts, alias_mapping)
        control = ";".join(control_parts)

        treatments = _split_slot_values(params.get("treatments", ""))
        treatments = _resolve_bucket_aliases(treatments, alias_mapping)
        # Stabilize treatment ordering to avoid AB backend order-sensitive empty results
        # for the same bucket set (observed in production for exp 6850).
        # Use numeric ascending order after alias resolution.
        try:
            treatments = sorted(
                list(dict.fromkeys(treatments)),
                key=lambda x: int(x) if str(x).isdigit() else 10**18,
            )
        except Exception:
            # Keep original order if any unexpected token appears.
            pass

        if not control or not treatments:
            return json_response({
                "result": "Error: Both control and treatment bucket IDs are required."
            })

        unresolved_buckets = [x for x in control_parts + treatments if not str(x).isdigit()]
        if unresolved_buckets:
            return json_response({
                "result": (
                    "Error: Unresolved bucket IDs/aliases: "
                    f"{', '.join(unresolved_buckets)}. "
                    "Please provide numeric bucket IDs or define aliases in Bucket_mapping.txt."
                )
            })

        metrics_input = _split_slot_values(params.get("metrics", ""))
        if metrics_input:
            metrics = []
            for metric in metrics_input:
                metric_norm = metric.strip()
                if not metric_norm:
                    continue
                if not re.fullmatch(r"[A-Za-z0-9_]+", metric_norm):
                    return json_response({
                        "result": f"Error: Invalid metric name '{metric_norm}'. Use letters/numbers/underscore only."
                    })
                if metric_norm not in metrics:
                    metrics.append(metric_norm)
        else:
            metrics = DEFAULT_METRICS

        # Build AB API request body
        request_body = {
            "project_id": DEFAULT_PROJECT_ID,
            "experiment_id": experiment_id,
            "operator": "samaritan.bot",
            "template_name": DEFAULT_TEMPLATE_NAME,
            "template_group_name": template_group_name,
            "template_group_type": DEFAULT_TEMPLATE_GROUP_TYPE,
            "dates": [
                {
                    "time_start": date_start,
                    "time_end": date_end
                }
            ],
            "regions": regions,
            "control": control,
            "treatments": treatments,
            "normalization": DEFAULT_NORMALIZATION,
            "metrics": metrics,
            "dims": dims
        }

        print(f"[AB Proxy] === Built API request ===")
        print(f"[AB Proxy]   experiment_id: {experiment_id} (type={type(experiment_id).__name__})")
        print(f"[AB Proxy]   dates: {date_start} to {date_end}")
        print(f"[AB Proxy]   regions: {regions}")
        print(f"[AB Proxy]   control: '{control}' (from raw='{params.get('control', '')}')")
        print(f"[AB Proxy]   treatments: {treatments} (from raw='{params.get('treatments', '')}')")
        print(f"[AB Proxy]   metrics: {metrics} (from raw='{params.get('metrics', '')}')")
        print(f"[AB Proxy]   card_type: {card_type}")
        print(f"[AB Proxy]   sort_type: {sort_type}")
        print(f"[AB Proxy]   dims: {dims} (split_by_date={split_by_date})")
        print(f"[AB Proxy]   Full body: {json.dumps(request_body, ensure_ascii=False)}")

        async with aiohttp.ClientSession() as session:
            # Step 1: open_get_summary_key
            key_status, key_result = await _call_ab_api(
                session=session,
                namespace=AB_DES_NAMESPACE_KEY,
                request_body=request_body,
                experiment_id=experiment_id,
            )

            if key_status != 200:
                error_text = key_result.get("error_text", "")
                print(f"[AB Proxy] Key API error: {key_status} - {error_text[:500]}")
                return json_response({
                    "result": f"AB API key request failed (status {key_status}): {error_text[:500]}"
                })

            print("[AB Proxy] Key API response status: 200")
            print(
                f"[AB Proxy] Key API business status: retcode={key_result.get('retcode')}, "
                f"msg={key_result.get('msg', '')}, template_group_name={request_body.get('template_group_name')}"
            )
            if (
                key_result.get("retcode") not in (0, "0", None)
                and _is_template_group_not_exists(key_result)
                and request_body.get("template_group_name") != FALLBACK_TEMPLATE_GROUP_NAME
            ):
                # Fallback for experiments that don't have the preferred default template group.
                print(
                    f"[AB Proxy] Template group '{request_body.get('template_group_name')}' unavailable. "
                    f"Retry with '{FALLBACK_TEMPLATE_GROUP_NAME}'."
                )
                request_body["template_group_name"] = FALLBACK_TEMPLATE_GROUP_NAME
                key_status, key_result = await _call_ab_api(
                    session=session,
                    namespace=AB_DES_NAMESPACE_KEY,
                    request_body=request_body,
                    experiment_id=experiment_id,
                )
                if key_status != 200:
                    error_text = key_result.get("error_text", "")
                    return json_response({
                        "result": f"AB API key request failed (status {key_status}): {error_text[:500]}"
                    })

            if key_result.get("retcode") not in (0, "0", None):
                return json_response({
                    "result": (
                        f"AB API key request business error: retcode={key_result.get('retcode')}, "
                        f"msg={key_result.get('msg', 'unknown')}"
                    )
                })

            key_info = key_result.get("key_info")
            if not isinstance(key_info, dict):
                return json_response({"result": "AB API key response missing key_info."})

            # Step 2: poll open_get_summary_result with key_info
            result_request_body = dict(request_body)
            result_request_body["key_info"] = key_info

            final_result = None
            final_key_info = key_info
            poll_attempts = 0

            for attempt in range(1, RESULT_POLL_MAX_ATTEMPTS + 1):
                poll_attempts = attempt
                result_status, result_payload = await _call_ab_api(
                    session=session,
                    namespace=AB_DES_NAMESPACE_RESULT,
                    request_body=result_request_body,
                    experiment_id=experiment_id,
                )

                if result_status != 200:
                    error_text = result_payload.get("error_text", "")
                    return json_response({
                        "result": f"AB API result request failed (status {result_status}): {error_text[:500]}"
                    })

                if result_payload.get("retcode") not in (0, "0", None):
                    return json_response({
                        "result": (
                            f"AB API result request business error: retcode={result_payload.get('retcode')}, "
                            f"msg={result_payload.get('msg', 'unknown')}"
                        )
                    })

                loop_key_info = result_payload.get("key_info")
                if isinstance(loop_key_info, dict):
                    final_key_info = loop_key_info
                    result_request_body["key_info"] = loop_key_info

                status = final_key_info.get("status")
                print(
                    f"[AB Proxy] Poll attempt {attempt}/{RESULT_POLL_MAX_ATTEMPTS}: "
                    f"status={status}, msg={final_key_info.get('msg', '')}"
                )
                if status == 3:
                    final_result = result_payload
                    break
                if status == 2:
                    fail_msg = final_key_info.get("msg") or result_payload.get("msg") or "unknown"
                    return json_response({"result": f"AB report query failed: {fail_msg}"})

                await asyncio.sleep(RESULT_POLL_INTERVAL_SECONDS)

            if final_result is None:
                query_key = final_key_info.get("single_data_query_key")
                return json_response({
                    "result": (
                        f"AB report query is still running after {poll_attempts} attempts. "
                        f"query_key={query_key}"
                    )
                })

            # Debug: dump raw response structure (null-safe)
            _dbg_data = final_result.get("data") or {}
            _dbg_header = _dbg_data.get("header", "")
            _dbg_body = _dbg_data.get("body") or []
            _dbg_rel = _dbg_data.get("relative") or []
            _dbg_ctrl_idx = _dbg_data.get("control_group_indexes")
            print(f"[AB Proxy] DEBUG header: {_dbg_header}")
            print(f"[AB Proxy] DEBUG control_group_indexes: {_dbg_ctrl_idx}")
            print(f"[AB Proxy] DEBUG body rows ({len(_dbg_body)}):")
            for _i, _r in enumerate(_dbg_body[:6]):
                print(f"[AB Proxy]   row[{_i}]: {_r}")
            print(f"[AB Proxy] DEBUG relative rows ({len(_dbg_rel)}):")
            for _i, _r in enumerate(_dbg_rel[:6]):
                print(f"[AB Proxy]   rel[{_i}]: {_r}")

            formatted = format_ab_results(
                final_result,
                request_body,
                final_key_info,
                poll_attempts,
                card_type_filter=card_type,
                sort_type_filter=sort_type,
            )
            resp = {"result": formatted}
            if (not disable_cache) and _result_has_data(formatted):
                _cache_set(ck, resp)
                print(f"[AB Proxy] Result cached (key={ck[:12]}...)")
            else:
                print(f"[AB Proxy] Skip cache (bypass or no metric data)")
            return json_response(resp)

    except ValueError as e:
        print(f"[AB Proxy] ValueError: {str(e)}")
        return json_response({"result": f"Invalid parameter: {str(e)}"})
    except Exception as e:
        print(f"[AB Proxy] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return json_response({"result": f"Proxy error: {str(e)}"})


@app.post("/card_types")
async def fetch_card_types(request: Request):
    """Return available card_type options for the given AB query scope."""
    try:
        if not AB_TOKEN:
            return json_response({"error": "Missing AB platform token: set AB_PLATFORM_TOKEN"})
        params = request.json or {}

        experiment_id = params.get("experiment_id", "")
        if not experiment_id:
            return json_response({"error": "experiment_id is required"})
        experiment_id = int(str(experiment_id).strip())

        default_start, default_end = get_default_dates()
        date_start = str(params.get("date_start", "")).strip() or default_start
        date_end = str(params.get("date_end", "")).strip() or default_end

        regions_str = str(params.get("regions", "")).strip()
        if not regions_str or regions_str.lower() in ("all", "全部", ""):
            regions = ["ALL"]
        else:
            regions = [r.upper() for r in _split_slot_values(regions_str)]

        alias_mapping = _load_bucket_mapping()
        control_raw = _normalize_control_group(params.get("control", ""))
        if not control_raw:
            control_raw = DEFAULT_CONTROL_BY_EXPERIMENT.get(experiment_id, "")
        control_parts = _resolve_bucket_aliases([p.strip() for p in control_raw.split(";") if p.strip()], alias_mapping)
        control = ";".join(control_parts)

        treatments = _resolve_bucket_aliases(_split_slot_values(params.get("treatments", "")), alias_mapping)
        if not control or not treatments:
            return json_response({"error": "Both control and treatments are required"})

        request_body = {
            "project_id": DEFAULT_PROJECT_ID,
            "experiment_id": experiment_id,
            "operator": "samaritan.bot",
            "template_name": DEFAULT_TEMPLATE_NAME,
            "template_group_name": str(params.get("template_group_name", DEFAULT_TEMPLATE_GROUP_NAME)).strip() or DEFAULT_TEMPLATE_GROUP_NAME,
            "template_group_type": DEFAULT_TEMPLATE_GROUP_TYPE,
            "dates": [{"time_start": date_start, "time_end": date_end}],
            "regions": regions,
            "control": control,
            "treatments": treatments,
            "normalization": DEFAULT_NORMALIZATION,
            # Keep one light metric; goal is to discover dimensions.
            "metrics": [DEFAULT_METRICS[0]],
            "dims": ["abtest_group", "abtest_region", "card_type", "abtest_date"],
        }

        async with aiohttp.ClientSession() as session:
            key_status, key_result = await _call_ab_api(
                session=session,
                namespace=AB_DES_NAMESPACE_KEY,
                request_body=request_body,
                experiment_id=experiment_id,
            )
            if key_status != 200:
                return json_response({"error": f"AB key request failed (status={key_status})"})
            if key_result.get("retcode") not in (0, "0", None):
                return json_response({"error": f"AB key business error: {key_result.get('msg', 'unknown')}"})

            key_info = key_result.get("key_info")
            if not isinstance(key_info, dict):
                return json_response({"error": "AB key response missing key_info"})

            result_request_body = dict(request_body)
            result_request_body["key_info"] = key_info
            final_result = None
            for _ in range(RESULT_POLL_MAX_ATTEMPTS):
                result_status, result_payload = await _call_ab_api(
                    session=session,
                    namespace=AB_DES_NAMESPACE_RESULT,
                    request_body=result_request_body,
                    experiment_id=experiment_id,
                )
                if result_status != 200:
                    return json_response({"error": f"AB result request failed (status={result_status})"})
                if result_payload.get("retcode") not in (0, "0", None):
                    return json_response({"error": f"AB result business error: {result_payload.get('msg', 'unknown')}"})

                loop_key_info = result_payload.get("key_info")
                if isinstance(loop_key_info, dict):
                    result_request_body["key_info"] = loop_key_info
                    if loop_key_info.get("status") == 3:
                        final_result = result_payload
                        break
                    if loop_key_info.get("status") == 2:
                        return json_response({"error": f"AB report query failed: {loop_key_info.get('msg', 'unknown')}"})
                await asyncio.sleep(RESULT_POLL_INTERVAL_SECONDS)

            if final_result is None:
                return json_response({"error": "AB report query still running"})

        card_types = _extract_unique_card_types(final_result)
        return json_response({
            "experiment_id": experiment_id,
            "date_start": date_start,
            "date_end": date_end,
            "regions": regions,
            "template_group_name": request_body["template_group_name"],
            "card_types": card_types,
            "count": len(card_types),
        })
    except Exception as e:
        return json_response({"error": f"card_types proxy error: {str(e)}"})


@app.get("/health")
async def health(request: Request):
    return json_response({"status": "ok", "service": "ab_proxy"})


@app.post("/cache/clear")
async def clear_cache(request: Request):
    """Clear in-memory response cache for debugging."""
    size_before = len(_response_cache)
    _response_cache.clear()
    return json_response({"status": "ok", "cleared": size_before})


if __name__ == "__main__":
    print("Starting AB Proxy Server...")
    print(f"Listening on: 0.0.0.0:5009")
    print(f"AB API endpoint: {AB_API_URL}")
    print(f"AB key namespace: {AB_DES_NAMESPACE_KEY}")
    print(f"AB result namespace: {AB_DES_NAMESPACE_RESULT}")
    app.run(
        host="0.0.0.0",
        port=5009,
        debug=False,
        access_log=True,
        auto_reload=False
    )
