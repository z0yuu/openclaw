#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AB 多实验对比（ab-platform skill）
兼容 Python 2.7.18 / Python 3.x
"""

from __future__ import absolute_import, division, print_function

import argparse
import io
import json
import os
import sys

# Python 2: 让 sys.stdout 能输出 UTF-8
if sys.version_info[0] < 3:
    sys.stdout = io.open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False)
    sys.stderr = io.open(sys.stderr.fileno(), mode="w", encoding="utf-8", closefd=False)

SKILL_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)
lib_path = os.path.join(SKILL_ROOT, "lib")
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)


def _load_env_file(path):
    """不依赖 dotenv：手动读 .env 并写入 os.environ（Python 2 或无 dotenv 时回退）"""
    if not path or not os.path.isfile(path):
        return
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k:
                        os.environ[k] = v
    except Exception:
        pass


try:
    from dotenv import load_dotenv
    load_dotenv(os.path.expanduser("~/.openclaw/.env"))
    load_dotenv(os.path.join(SKILL_ROOT, ".env"))
except ImportError:
    pass
_load_env_file(os.path.expanduser("~/.openclaw/.env"))
_load_env_file(os.path.join(SKILL_ROOT, ".env"))

from ab_client import PlatformAPIClient, CacheManager, get_default_metrics
from analysis import extract_metric_lifts, format_lift, get_metric_columns
from analysis.comparison import ComparisonAnalyzer


def fetch_metrics_for_experiment(experiment_id, project_id=None, metrics=None, dates=None, regions=None, token=None):
    if project_id is None:
        project_id = int(os.getenv("AB_PROJECT_ID", "27"))
    cache = CacheManager(cache_dir=os.path.join(SKILL_ROOT, ".cache"), ttl=300)
    cache_key = "ab_metrics_{}_{}_{}_{}".format(project_id, experiment_id, metrics, dates)
    cached = cache.get(cache_key)
    if cached:
        return cached

    client = PlatformAPIClient(token=token)
    kwargs = {}
    if regions:
        kwargs["regions"] = regions
    result = client.get_ab_metrics(
        project_id=project_id,
        experiment_id=experiment_id,
        metrics=metrics or get_default_metrics(),
        dates=dates,
        **kwargs
    )
    if result:
        result["experiment_id"] = experiment_id
        result["project_id"] = project_id
        result["lifts"] = extract_metric_lifts(result)
        cache.set(cache_key, result)
    return result


def compare_experiments(experiment_ids, project_id=None, metrics=None, sort_by=None, dates=None, regions=None, token=None):
    results = []
    for exp_id in experiment_ids:
        data = fetch_metrics_for_experiment(exp_id, project_id, metrics, dates, regions, token=token)
        if data:
            results.append({"experiment_id": exp_id, "data": data})
        else:
            sys.stderr.write("警告: 实验 %s 获取数据失败\n" % exp_id)

    if len(results) < 2:
        return {"error": "需要至少2个实验的有效数据"}

    comparison = ComparisonAnalyzer.compare_ab_results(results)
    first_data = results[0]["data"]
    columns = first_data.get("columns", [])
    metric_cols = metrics if metrics else get_metric_columns(columns)

    lines = ["实验对比（共 %s 个实验）" % len(results), "=" * 60]
    header = "%10s" % "实验ID"
    for m in metric_cols:
        header += "  %15s" % m
    lines.append(header)
    lines.append("-" * len(header))

    for r in results:
        exp_id = r["experiment_id"]
        lifts = r["data"].get("lifts", {})
        row = "%10s" % exp_id
        for m in metric_cols:
            found = False
            for _gn, group_lifts in lifts.items():
                if m in group_lifts:
                    row += "  %15s" % format_lift(group_lifts[m])
                    found = True
                    break
            if not found:
                row += "  %15s" % "N/A"
        lines.append(row)

    if sort_by and sort_by in metric_cols:
        lines.append("\n按 %s 排序:" % sort_by)
        sort_data = []
        for r in results:
            lifts = r["data"].get("lifts", {})
            for _gn, group_lifts in lifts.items():
                if sort_by in group_lifts:
                    sort_data.append((r["experiment_id"], group_lifts[sort_by]))
                    break
        sort_data.sort(key=lambda x: x[1], reverse=True)
        for i, (exp_id, lift) in enumerate(sort_data):
            lines.append("  %s. 实验 %s: %s" % (i + 1, exp_id, format_lift(lift)))

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
    parser.add_argument("--token", type=str, default=None, help="AB API Token（不传则用环境变量 AB_API_TOKEN）")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    exp_ids = [int(x.strip()) for x in args.experiment_ids.split(",")]
    metrics = [m.strip() for m in args.metrics.split(",")] if args.metrics else None
    if len(exp_ids) < 2:
        sys.stderr.write("错误: 需要至少 2 个实验 ID\n")
        sys.exit(1)

    result = compare_experiments(
        experiment_ids=exp_ids,
        project_id=args.project_id,
        metrics=metrics,
        sort_by=args.sort_by,
        token=args.token,
    )
    if "error" in result:
        sys.stderr.write("错误: %s\n" % result["error"])
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
