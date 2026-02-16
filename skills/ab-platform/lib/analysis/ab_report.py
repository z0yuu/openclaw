# -*- coding: utf-8 -*-
"""
AB 报告解析（ab-platform skill 内嵌）
兼容 Python 2.7.18 / Python 3.x
"""

from __future__ import absolute_import, division, unicode_literals

DIMENSION_COLUMNS = {
    "group_prefix", "group_name", "abtest_group",
    "abtest_region", "abtest_date",
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


def _is_control_row(row):
    prefix = (row.get("group_prefix") or "").lower()
    return "control" in prefix


def _aggregate_metrics(rows, metric_cols):
    """对多行按指标列求和，返回 {metric: sum}；非数值列不纳入（避免 mock 等出现 metric: 0）"""
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


def group_body_by_experiment_group(body, metric_cols):
    """
    按实验组拆分 body 行：优先用 abtest_group，缺失时用 group_prefix/group_name（兼容 mock 等）。
    返回: [
      {"group_key": "Control (82930)", "is_control": True, "abtest_group": "82930", "rows": [...], "agg": {...}},
      ...
    ]
    """
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
        if gid == "_":
            label = rows[0].get("group_prefix") or rows[0].get("group_name") or "Unknown"
        elif gid.isdigit() or (gid and gid.lstrip("-").isdigit()):
            label = "Control (%s)" % gid if is_control else "Treatment (%s)" % gid
        else:
            label = gid
        result.append({
            "group_key": label,
            "abtest_group": gid if gid != "_" else "",
            "is_control": is_control,
            "rows": rows,
            "agg": _aggregate_metrics(rows, metric_cols),
        })
    # Control 放最前
    result.sort(key=lambda x: (x["is_control"], x["abtest_group"]), reverse=True)
    return result


def format_ab_summary(parsed_data, experiment_id=0):
    if not parsed_data or "columns" not in parsed_data:
        return "无数据"
    columns = parsed_data["columns"]
    body = parsed_data.get("body", [])
    relative = parsed_data.get("relative", [])
    metric_cols = get_metric_columns(columns)
    lines = []
    if experiment_id:
        lines.append("实验 %s 指标概览" % experiment_id)
        lines.append("=" * 50)

    # 按实验组拆分
    groups = group_body_by_experiment_group(body, metric_cols)
    control_group = next((g for g in groups if g["is_control"]), None)
    control_agg = control_group["agg"] if control_group else {}

    def _fmt_agg(val):
        try:
            f = float(val)
            if f >= 1e4 or f <= -1e4:
                return "%.2f" % f
            return "%.6g" % f if isinstance(val, float) else str(val)
        except (TypeError, ValueError):
            return str(val)

    lines.append("\n【按实验组】")
    for g in groups:
        lines.append("\n  %s（汇总）:" % g["group_key"])
        for metric in metric_cols:
            if metric in g["agg"]:
                val = g["agg"][metric]
                lines.append("    %s: %s" % (metric, _fmt_agg(val)))
        if not g["is_control"] and control_agg:
            lifts = _compute_lift(g["agg"], control_agg, metric_cols)
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

    # 总体 Treatment：所有 treatment 组汇总
    treatment_groups = [g for g in groups if not g["is_control"]]
    if treatment_groups and control_agg:
        lines.append("\n【总体 Treatment（所有实验组汇总）】")
        total_treatment_agg = {}
        for metric in metric_cols:
            total_treatment_agg[metric] = sum(g["agg"].get(metric, 0) for g in treatment_groups)
        lines.append("  汇总指标:")
        for metric in metric_cols:
            if metric in total_treatment_agg:
                val = total_treatment_agg[metric]
                lines.append("    %s: %s" % (metric, _fmt_agg(val)))
        lifts = _compute_lift(total_treatment_agg, control_agg, metric_cols)
        lines.append("  相对 Control 提升:")
        for metric in metric_cols:
            if metric in lifts:
                lines.append("    %s: %s" % (metric, format_lift(lifts[metric])))

    return "\n".join(lines)


def get_grouped_summary(parsed_data):
    """
    返回按实验组拆分及总体 Treatment 的结构化数据。
    用于 JSON 输出或后续逻辑。
    """
    if not parsed_data or "columns" not in parsed_data:
        return {"by_group": [], "overall_treatment": None}
    columns = parsed_data.get("columns", [])
    body = parsed_data.get("body", [])
    metric_cols = get_metric_columns(columns)
    groups = group_body_by_experiment_group(body, metric_cols)
    control_group = next((g for g in groups if g["is_control"]), None)
    control_agg = control_group["agg"] if control_group else {}

    by_group = []
    for g in groups:
        item = {
            "group_key": g["group_key"],
            "abtest_group": g["abtest_group"],
            "is_control": g["is_control"],
            "agg": g["agg"],
            "lift_vs_control": None,
        }
        if not g["is_control"] and control_agg:
            item["lift_vs_control"] = _compute_lift(g["agg"], control_agg, metric_cols)
        by_group.append(item)

    overall_treatment = None
    treatment_groups = [g for g in groups if not g["is_control"]]
    if treatment_groups and control_agg:
        total_agg = {}
        for metric in metric_cols:
            total_agg[metric] = sum(g["agg"].get(metric, 0) for g in treatment_groups)
        overall_treatment = {
            "agg": total_agg,
            "lift_vs_control": _compute_lift(total_agg, control_agg, metric_cols),
        }

    return {"by_group": by_group, "overall_treatment": overall_treatment}


def extract_metric_lifts(parsed_data):
    if not parsed_data:
        return {}
    columns = parsed_data.get("columns", [])
    relative = parsed_data.get("relative", [])
    metric_cols = get_metric_columns(columns)
    result = {}
    for row in relative:
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
            result[group] = lifts
    return result
