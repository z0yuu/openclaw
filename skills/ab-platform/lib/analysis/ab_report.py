# -*- coding: utf-8 -*-
"""
AB 报告解析（ab-platform skill 内嵌）
"""

# typing (py3.5+) not required; keep runtime compatible

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
    lines.append("\n【各组指标值】")
    for row in body:
        label = _row_label(row)
        lines.append("\n  %s:" % label)
        for metric in metric_cols:
            if metric in row:
                lines.append("    %s: %s" % (metric, row[metric]))
    if relative:
        lines.append("\n【相对提升（vs Control）】")
        for row in relative:
            group = row.get("group_prefix", row.get("group_name", "Unknown"))
            if "control" in group.lower():
                continue
            label = _row_label(row)
            lines.append("\n  %s:" % label)
            for metric in metric_cols:
                if metric in row:
                    try:
                        lines.append("    %s: %s" % (metric, format_lift(float(row[metric]))))
                    except (ValueError, TypeError):
                        lines.append("    %s: %s" % (metric, row[metric]))
    return "\n".join(lines)


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
