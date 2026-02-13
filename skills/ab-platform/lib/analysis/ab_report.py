"""
AB 报告解析（ab-platform skill 内嵌）
"""

from typing import Dict, List

DIMENSION_COLUMNS = {
    "group_prefix", "group_name", "abtest_group",
    "abtest_region", "abtest_date",
}


def get_metric_columns(columns: List[str]) -> List[str]:
    return [c for c in columns if c not in DIMENSION_COLUMNS]


def format_lift(lift_value: float) -> str:
    pct = lift_value * 100
    sign = "+" if pct > 0 else ""
    return f"{sign}{pct:.2f}%"


def format_ab_summary(parsed_data: Dict, experiment_id: int = 0) -> str:
    if not parsed_data or "columns" not in parsed_data:
        return "无数据"
    columns = parsed_data["columns"]
    body = parsed_data.get("body", [])
    relative = parsed_data.get("relative", [])
    metric_cols = get_metric_columns(columns)
    lines = []
    if experiment_id:
        lines.append(f"实验 {experiment_id} 指标概览")
        lines.append("=" * 50)
    lines.append("\n【各组指标值】")
    for row in body:
        group = row.get("group_prefix", row.get("group_name", "Unknown"))
        lines.append(f"\n  {group}:")
        for metric in metric_cols:
            if metric in row:
                lines.append(f"    {metric}: {row[metric]}")
    if relative:
        lines.append("\n【相对提升（vs Control）】")
        for row in relative:
            group = row.get("group_prefix", row.get("group_name", "Unknown"))
            if "control" in group.lower():
                continue
            lines.append(f"\n  {group}:")
            for metric in metric_cols:
                if metric in row:
                    try:
                        lines.append(f"    {metric}: {format_lift(float(row[metric]))}")
                    except (ValueError, TypeError):
                        lines.append(f"    {metric}: {row[metric]}")
    return "\n".join(lines)


def extract_metric_lifts(parsed_data: Dict) -> Dict[str, Dict[str, float]]:
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
