# -*- coding: utf-8 -*-
"""
多实验对比分析（ab-platform skill 内嵌）
兼容 Python 2.7.18 / Python 3.x
"""

from __future__ import absolute_import, division

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class ComparisonAnalyzer(object):
    @staticmethod
    def compare_ab_results(results, metric_names=None):
        if not results:
            return {"error": "没有实验数据"}
        comparison_table = []
        dim_cols = {"group_prefix", "group_name", "abtest_group", "abtest_region", "abtest_date"}
        for exp_result in results:
            exp_id = exp_result.get("experiment_id", "unknown")
            data = exp_result.get("data", {})
            relative = data.get("relative", [])
            columns = data.get("columns", [])
            for rel_row in relative:
                prefix = (rel_row.get("group_prefix") or "").lower()
                name = rel_row.get("group_prefix", "")
                if prefix.startswith("treatment") or name != "Control Group":
                    row_data = {"experiment_id": exp_id}
                    target_metrics = metric_names or [c for c in columns if c not in dim_cols]
                    for metric in target_metrics:
                        if metric in rel_row:
                            try:
                                row_data["%s_lift" % metric] = float(rel_row[metric])
                            except (ValueError, TypeError):
                                row_data["%s_lift" % metric] = rel_row[metric]
                    comparison_table.append(row_data)
        return {"comparison_table": comparison_table, "experiment_count": len(results)}

    @staticmethod
    def rank_experiments(
        experiments_data,
        metric_name="conversion_rate",
        metric_key="lift",
    ):
        ranked = []
        for exp in experiments_data:
            exp_id = exp.get("id", "unknown")
            ab_metrics = exp.get("ab_metrics", {})
            metric_data = ab_metrics.get(metric_name, {})
            if isinstance(metric_data, dict):
                value = metric_data.get(metric_key, 0)
                p_value = metric_data.get("p_value", 1.0)
                ranked.append({"experiment_id": exp_id, "value": value, "p_value": p_value, "data": exp})
        ranked.sort(key=lambda x: (x["p_value"] >= 0.05, -x["value"]))
        return ranked
