# -*- coding: utf-8 -*-
"""
AB 报告解析（ab-platform skill 内嵌）
兼容 Python 2.7.18 / Python 3.x
"""

from __future__ import absolute_import, division, unicode_literals

DIMENSION_COLUMNS = {
    "group_prefix", "group_name", "abtest_group",
    "abtest_region", "abtest_date", "card_type", "sort_type",
}


def get_metric_columns(columns):
    return [c for c in columns if c not in DIMENSION_COLUMNS]


def format_lift(lift_value):
    pct = lift_value * 100
    sign = "+" if pct > 0 else ""
    return "%s%.2f%%" % (sign, pct)


def _row_label(row):
    """构建行标签：group + 可选的日期/地区维度"""
    group = row.get("group_prefix", row.get("group_name", "Unknown"))
    date = row.get("abtest_date", "")
    region = row.get("abtest_region", "")
    parts = [group]
    if region:
        parts.append(region)
    if date:
        parts.append(date)
    return " | ".join(parts)


def _fmt_val(val):
    try:
        f = float(val)
        if f >= 1e4 or f <= -1e4:
            return "%.2f" % f
        return "%.6g" % f if isinstance(val, float) else str(val)
    except (TypeError, ValueError):
        return str(val)


def _is_control_row(row):
    prefix = (row.get("group_prefix") or "").lower()
    return "control" in prefix


def _aggregate_metrics(rows, metric_cols):
    """对多行按指标列求和，返回 {metric: sum}"""
    agg = {}
    for metric in metric_cols:
        total = 0
        got = False
        for row in rows:
            try:
                v = row.get(metric)
                if v is None or v == "":
                    continue
                total += float(v)
                got = True
            except (ValueError, TypeError):
                pass
        if got:
            agg[metric] = total
    return agg


def _compute_lift(treatment_agg, control_agg, metric_cols):
    """计算 treatment 相对 control 的提升比例，(t - c) / c"""
    lifts = {}
    for metric in metric_cols:
        c = control_agg.get(metric) or 0
        t = treatment_agg.get(metric) or 0
        if c and c != 0:
            lifts[metric] = (t - c) / c
        else:
            lifts[metric] = 0.0
    return lifts


def _build_relative_map(relative_rows, metric_cols):
    """
    从 API 返回的 relative 行构建 {abtest_group: {metric: float}} 查找表。
    API 的 relative 值是平台原生计算的 lift，比从 body 重算更准确。
    """
    rmap = {}
    for row in (relative_rows or []):
        gid = (row.get("abtest_group") or "").strip()
        if not gid:
            continue
        if _is_control_row(row):
            continue
        lifts = {}
        for metric in metric_cols:
            v = row.get(metric)
            if v is None or v == "":
                continue
            try:
                lifts[metric] = float(v)
            except (ValueError, TypeError):
                pass
        if lifts:
            rmap[gid] = lifts
    return rmap


def _get_lift_for_group(group, control_agg, metric_cols, relative_map):
    """优先用 API relative 预计算 lift；无则从绝对值计算"""
    gid = group.get("abtest_group", "")
    api_lifts = relative_map.get(gid) if relative_map else None
    if api_lifts:
        result = {}
        for metric in metric_cols:
            if metric in api_lifts:
                result[metric] = api_lifts[metric]
        if result:
            return result
    return _compute_lift(group["agg"], control_agg, metric_cols)


def group_body_by_experiment_group(body, metric_cols, bucket_map=None, control_group_ids=None):
    """
    按实验组拆分 body 行。
    不过滤任何个体桶行——所有桶（包括控制桶个体）都会出现在结果中，
    通过 is_control_bucket 标记区分。
    """
    if bucket_map is None:
        bucket_map = {}
    _ctrl_ids = set(str(x) for x in (control_group_ids or []))
    by_group = {}
    for row in body:
        gid = (row.get("abtest_group") or "").strip()
        if not gid:
            gid = (row.get("group_prefix") or row.get("group_name") or "").strip() or "_"
        if gid not in by_group:
            by_group[gid] = []
        by_group[gid].append(row)

    result = []
    for gid, rows in by_group.items():
        if not rows:
            continue
        is_control = _is_control_row(rows[0])
        is_control_bucket = (not is_control) and (gid in _ctrl_ids)
        bucket_name = bucket_map.get(gid, "")
        if gid == "_":
            label = rows[0].get("group_prefix") or rows[0].get("group_name") or "Unknown"
        elif gid.isdigit() or (gid and gid.lstrip("-").isdigit()):
            if bucket_name:
                label = "%s (%s)" % (bucket_name, gid)
            else:
                label = "Control (%s)" % gid if is_control else "Treatment (%s)" % gid
        elif ";" in gid and bucket_map:
            parts = [p.strip() for p in gid.split(";") if p.strip()]
            mapped = [bucket_map.get(p, p) for p in parts]
            bucket_name = ";".join(mapped)
            label = "%s (%s)" % (bucket_name, gid)
        else:
            label = gid
        result.append({
            "group_key": label,
            "abtest_group": gid if gid != "_" else "",
            "bucket_name": bucket_name,
            "is_control": is_control,
            "is_control_bucket": is_control_bucket,
            "rows": rows,
            "agg": _aggregate_metrics(rows, metric_cols),
        })
    # Control 放最前
    result.sort(key=lambda x: (x["is_control"], x["abtest_group"]), reverse=True)
    return result


def format_ab_summary(parsed_data, experiment_id=0, bucket_map=None, control_group_ids=None):
    if not parsed_data or "columns" not in parsed_data:
        return "无数据"
    columns = parsed_data["columns"]
    body = parsed_data.get("body", [])
    relative = parsed_data.get("relative", [])
    metric_cols = get_metric_columns(columns)
    relative_map = _build_relative_map(relative, metric_cols)

    lines = []
    if experiment_id:
        lines.append("实验 %s 指标概览" % experiment_id)
        lines.append("=" * 50)

    groups = group_body_by_experiment_group(body, metric_cols, bucket_map=bucket_map,
                                           control_group_ids=control_group_ids)
    control_group = next((g for g in groups if g["is_control"]), None)
    control_agg = control_group["agg"] if control_group else {}

    lines.append("\n【按实验组】")
    for g in groups:
        lines.append("\n  %s（汇总）:" % g["group_key"])
        for metric in metric_cols:
            if metric in g["agg"]:
                val = g["agg"][metric]
                lines.append("    %s: %s" % (metric, _fmt_val(val)))
        if not g["is_control"] and control_agg:
            lifts = _get_lift_for_group(g, control_agg, metric_cols, relative_map)
            lines.append("    相对 Control:")
            for metric in metric_cols:
                if metric in lifts:
                    lines.append("      %s: %s" % (metric, format_lift(lifts[metric])))
        lines.append("  明细（按日期/地区）:")
        for row in g["rows"]:
            lines.append("    %s" % _row_label(row))
            for metric in metric_cols:
                if metric in row:
                    lines.append("      %s: %s" % (metric, row[metric]))

    # 总体 Treatment：只包含真正的实验组（排除控制桶个体）
    real_treatments = [g for g in groups if not g["is_control"] and not g.get("is_control_bucket")]
    if real_treatments and control_agg:
        lines.append("\n【总体 Treatment（实验组汇总，不含对照桶）】")
        total_treatment_agg = {}
        for metric in metric_cols:
            total_treatment_agg[metric] = sum(g["agg"].get(metric, 0) for g in real_treatments)
        lines.append("  汇总指标:")
        for metric in metric_cols:
            if metric in total_treatment_agg:
                val = total_treatment_agg[metric]
                lines.append("    %s: %s" % (metric, _fmt_val(val)))
        lifts = _compute_lift(total_treatment_agg, control_agg, metric_cols)
        lines.append("  相对 Control 提升:")
        for metric in metric_cols:
            if metric in lifts:
                lines.append("    %s: %s" % (metric, format_lift(lifts[metric])))

    return "\n".join(lines)


def get_grouped_summary(parsed_data, bucket_map=None, control_group_ids=None):
    """
    返回按实验组拆分及总体 Treatment 的结构化数据。
    """
    if not parsed_data or "columns" not in parsed_data:
        return {"by_group": [], "overall_treatment": None}
    columns = parsed_data.get("columns", [])
    body = parsed_data.get("body", [])
    relative = parsed_data.get("relative", [])
    metric_cols = get_metric_columns(columns)
    relative_map = _build_relative_map(relative, metric_cols)

    groups = group_body_by_experiment_group(body, metric_cols, bucket_map=bucket_map,
                                           control_group_ids=control_group_ids)
    control_group = next((g for g in groups if g["is_control"]), None)
    control_agg = control_group["agg"] if control_group else {}

    by_group = []
    for g in groups:
        item = {
            "group_key": g["group_key"],
            "abtest_group": g["abtest_group"],
            "bucket_name": g.get("bucket_name", ""),
            "is_control": g["is_control"],
            "is_control_bucket": g.get("is_control_bucket", False),
            "agg": g["agg"],
            "lift_vs_control": None,
        }
        if not g["is_control"] and control_agg:
            item["lift_vs_control"] = _get_lift_for_group(g, control_agg, metric_cols, relative_map)
        by_group.append(item)

    overall_treatment = None
    real_treatments = [g for g in groups if not g["is_control"] and not g.get("is_control_bucket")]
    if real_treatments and control_agg:
        total_agg = {}
        for metric in metric_cols:
            total_agg[metric] = sum(g["agg"].get(metric, 0) for g in real_treatments)
        overall_treatment = {
            "agg": total_agg,
            "lift_vs_control": _compute_lift(total_agg, control_agg, metric_cols),
        }

    return {"by_group": by_group, "overall_treatment": overall_treatment}


def format_lift_report(parsed_data, experiment_id=0, show_absolute=False,
                       bucket_map=None, control_group_ids=None):
    """
    默认输出格式：只显示相对 Control 的提升百分比，显示所有桶（含控制桶个体）。
    包含【汇总（全部天数）】和【分天统计】两部分。
    """
    if not parsed_data or "columns" not in parsed_data:
        return "无数据"
    columns = parsed_data["columns"]
    body = parsed_data.get("body", [])
    relative = parsed_data.get("relative", [])
    metric_cols = get_metric_columns(columns)
    relative_map = _build_relative_map(relative, metric_cols)

    lines = []
    if experiment_id:
        lines.append("实验 %s 指标概览" % experiment_id)
        lines.append("=" * 50)

    _grp_kwargs = dict(bucket_map=bucket_map, control_group_ids=control_group_ids)
    groups = group_body_by_experiment_group(body, metric_cols, **_grp_kwargs)
    control_group = next((g for g in groups if g["is_control"]), None)
    individual_groups = [g for g in groups if not g["is_control"]]

    if not control_group:
        lines.append("未找到对照组数据")
        return "\n".join(lines)

    control_agg = control_group["agg"]

    # ── 汇总（全部天数）──
    lines.append("\n【汇总（全部天数）】相对 Control 提升")

    for tg in individual_groups:
        lifts = _get_lift_for_group(tg, control_agg, metric_cols, relative_map)
        tag = " [对照桶]" if tg.get("is_control_bucket") else ""
        lines.append("\n  %s%s:" % (tg["group_key"], tag))
        for metric in metric_cols:
            if metric in lifts:
                if show_absolute:
                    lines.append("    %s: %s (%s)" % (
                        metric, _fmt_val(tg["agg"].get(metric, 0)), format_lift(lifts[metric])))
                else:
                    lines.append("    %s: %s" % (metric, format_lift(lifts[metric])))

    # ── 分天统计 ──
    all_dates = sorted(set(
        (row.get("abtest_date") or "").strip()
        for row in body if (row.get("abtest_date") or "").strip()
    ))

    if all_dates:
        lines.append("\n【分天统计】相对 Control 提升")
        for date in all_dates:
            date_rows = [r for r in body if (r.get("abtest_date") or "").strip() == date]
            date_relative = [r for r in relative if (r.get("abtest_date") or "").strip() == date]
            date_relative_map = _build_relative_map(date_relative, metric_cols)
            date_groups = group_body_by_experiment_group(date_rows, metric_cols, **_grp_kwargs)
            date_control = next((g for g in date_groups if g["is_control"]), None)
            if not date_control:
                lines.append("\n  %s: (无对照组数据)" % date)
                continue
            date_control_agg = date_control["agg"]
            date_individuals = [g for g in date_groups if not g["is_control"]]
            if not date_individuals:
                continue

            lines.append("\n  %s:" % date)

            for tg in date_individuals:
                lifts = _get_lift_for_group(tg, date_control_agg, metric_cols, date_relative_map)
                tag = " [对照桶]" if tg.get("is_control_bucket") else ""
                lift_strs = []
                for metric in metric_cols:
                    if metric in lifts:
                        if show_absolute:
                            lift_strs.append("%s: %s (%s)" % (
                                metric, _fmt_val(tg["agg"].get(metric, 0)), format_lift(lifts[metric])))
                        else:
                            lift_strs.append("%s: %s" % (metric, format_lift(lifts[metric])))
                if lift_strs:
                    lines.append("    %s%s:  %s" % (tg["group_key"], tag, "  ".join(lift_strs)))

    return "\n".join(lines)


def get_daily_lift_summary(parsed_data, bucket_map=None, control_group_ids=None):
    """
    返回分天结构化数据，用于 JSON 输出。
    """
    if not parsed_data or "columns" not in parsed_data:
        return []
    columns = parsed_data["columns"]
    body = parsed_data.get("body", [])
    relative = parsed_data.get("relative", [])
    metric_cols = get_metric_columns(columns)
    _grp_kwargs = dict(bucket_map=bucket_map, control_group_ids=control_group_ids)

    all_dates = sorted(set(
        (row.get("abtest_date") or "").strip()
        for row in body if (row.get("abtest_date") or "").strip()
    ))

    daily = []
    for date in all_dates:
        date_rows = [r for r in body if (r.get("abtest_date") or "").strip() == date]
        date_relative = [r for r in relative if (r.get("abtest_date") or "").strip() == date]
        date_relative_map = _build_relative_map(date_relative, metric_cols)
        date_groups = group_body_by_experiment_group(date_rows, metric_cols, **_grp_kwargs)
        date_control = next((g for g in date_groups if g["is_control"]), None)
        if not date_control:
            continue
        date_control_agg = date_control["agg"]
        date_individuals = [g for g in date_groups if not g["is_control"]]
        day_lifts = []
        for tg in date_individuals:
            lifts = _get_lift_for_group(tg, date_control_agg, metric_cols, date_relative_map)
            day_lifts.append({
                "group": tg["group_key"],
                "abtest_group": tg["abtest_group"],
                "bucket_name": tg.get("bucket_name", ""),
                "is_control_bucket": tg.get("is_control_bucket", False),
                "lift_vs_control": lifts,
            })
        daily.append({"date": date, "lifts": day_lifts})
    return daily


def extract_metric_lifts(parsed_data):
    if not parsed_data:
        return {}
    columns = parsed_data.get("columns", [])
    relative = parsed_data.get("relative", [])
    metric_cols = get_metric_columns(columns)
    result = {}
    for row in relative:
        gid = (row.get("abtest_group") or "").strip()
        group = row.get("group_prefix", row.get("group_name", "Unknown"))
        if "control" in group.lower():
            continue
        lifts = {}
        for metric in metric_cols:
            if metric in row:
                try:
                    lifts[metric] = float(row[metric])
                except (ValueError, TypeError):
                    pass
        if lifts:
            key = gid if gid else group
            result[key] = lifts
    return result
