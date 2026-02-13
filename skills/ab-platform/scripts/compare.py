#!/usr/bin/env python3
"""
AB 多实验对比（ab-platform skill）
"""

import argparse
import json
import os
import sys

SKILL_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(SKILL_ROOT, ".env"))
    load_dotenv(os.path.expanduser("~/.openclaw/workspace/.env"))
except ImportError:
    pass

from lib.ab_client import PlatformAPIClient, CacheManager, get_default_metrics
from lib.analysis import extract_metric_lifts, format_lift, get_metric_columns
from lib.analysis.comparison import ComparisonAnalyzer


def fetch_metrics_for_experiment(experiment_id, project_id=None, metrics=None, dates=None, regions=None):
    if project_id is None:
        project_id = int(os.getenv("AB_PROJECT_ID", "27"))
    cache = CacheManager(cache_dir=os.path.join(SKILL_ROOT, ".cache"), ttl=300)
    cache_key = f"ab_metrics_{project_id}_{experiment_id}_{metrics}_{dates}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    client = PlatformAPIClient()
    kwargs = {}
    if regions:
        kwargs["regions"] = regions
    result = client.get_ab_metrics(
        project_id=project_id,
        experiment_id=experiment_id,
        metrics=metrics or get_default_metrics(),
        dates=dates,
        **kwargs,
    )
    if result:
        result["experiment_id"] = experiment_id
        result["project_id"] = project_id
        result["lifts"] = extract_metric_lifts(result)
        cache.set(cache_key, result)
    return result


def compare_experiments(experiment_ids, project_id=None, metrics=None, sort_by=None, dates=None, regions=None):
    results = []
    for exp_id in experiment_ids:
        data = fetch_metrics_for_experiment(exp_id, project_id, metrics, dates, regions)
        if data:
            results.append({"experiment_id": exp_id, "data": data})
        else:
            print(f"警告: 实验 {exp_id} 获取数据失败", file=sys.stderr)

    if len(results) < 2:
        return {"error": "需要至少2个实验的有效数据"}

    comparison = ComparisonAnalyzer.compare_ab_results(results)
    first_data = results[0]["data"]
    columns = first_data.get("columns", [])
    metric_cols = metrics if metrics else get_metric_columns(columns)

    lines = [f"实验对比（共 {len(results)} 个实验）", "=" * 60]
    header = f"{'实验ID':>10}"
    for m in metric_cols:
        header += f"  {m:>15}"
    lines.append(header)
    lines.append("-" * len(header))

    for r in results:
        exp_id = r["experiment_id"]
        lifts = r["data"].get("lifts", {})
        row = f"{exp_id:>10}"
        for m in metric_cols:
            found = False
            for _gn, group_lifts in lifts.items():
                if m in group_lifts:
                    row += f"  {format_lift(group_lifts[m]):>15}"
                    found = True
                    break
            if not found:
                row += f"  {'N/A':>15}"
        lines.append(row)

    if sort_by and sort_by in metric_cols:
        lines.append(f"\n按 {sort_by} 排序:")
        sort_data = []
        for r in results:
            lifts = r["data"].get("lifts", {})
            for _gn, group_lifts in lifts.items():
                if sort_by in group_lifts:
                    sort_data.append((r["experiment_id"], group_lifts[sort_by]))
                    break
        sort_data.sort(key=lambda x: x[1], reverse=True)
        for i, (exp_id, lift) in enumerate(sort_data, 1):
            lines.append(f"  {i}. 实验 {exp_id}: {format_lift(lift)}")

    return {
        "experiment_ids": experiment_ids,
        "results": results,
        "comparison": comparison,
        "formatted_text": "\n".join(lines),
    }


def main():
    parser = argparse.ArgumentParser(description="对比多个 AB 实验")
    parser.add_argument("experiment_ids", type=str, help="实验 ID 列表，逗号分隔")
    parser.add_argument("--project-id", type=int, default=None, help="项目 ID")
    parser.add_argument("--metrics", type=str, default=None, help="指标列表，逗号分隔")
    parser.add_argument("--sort-by", type=str, default=None, help="排序指标")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    exp_ids = [int(x.strip()) for x in args.experiment_ids.split(",")]
    metrics = args.metrics.split(",") if args.metrics else None
    if len(exp_ids) < 2:
        print("错误: 需要至少 2 个实验 ID", file=sys.stderr)
        sys.exit(1)

    result = compare_experiments(
        experiment_ids=exp_ids,
        project_id=args.project_id,
        metrics=metrics,
        sort_by=args.sort_by,
    )
    if "error" in result:
        print(f"错误: {result['error']}", file=sys.stderr)
        sys.exit(1)
    if args.json:
        print(json.dumps({
            "experiment_ids": result["experiment_ids"],
            "comparison": result["comparison"],
        }, ensure_ascii=False, indent=2))
    else:
        print(result.get("formatted_text", "无数据"))


if __name__ == "__main__":
    main()
