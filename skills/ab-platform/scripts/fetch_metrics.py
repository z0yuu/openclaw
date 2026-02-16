#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AB 指标查询（ab-platform skill）
从 Shopee AB Report Open API 获取单实验指标并格式化输出。
"""

import argparse
import json
import os
import sys

# Skill 根目录 = scripts 的上一级
SKILL_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# 需要把 skill 根目录与其 lib/ 都加入 sys.path，兼容从任意 cwd 运行
for p in [SKILL_ROOT, os.path.join(SKILL_ROOT, "lib")]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.expanduser("~/.openclaw/.env"))
    load_dotenv(os.path.join(SKILL_ROOT, ".env"))
except ImportError:
    pass

from ab_client import PlatformAPIClient, CacheManager, get_default_metrics
from analysis import format_ab_summary, extract_metric_lifts, get_grouped_summary


def _load_defaults():
    cfg_path = os.path.join(SKILL_ROOT, "defaults.json")
    if not os.path.exists(cfg_path):
        return {}
    try:
        with open(cfg_path, "r") as f:
            return json.load(f).get("ab_platform", {})
    except Exception:
        return {}


def fetch_metrics(
    experiment_id=None,
    project_id=None,
    metrics=None,
    control="",
    treatments=None,
    dates=None,
    regions=None,
    dims=None,
    normalization=None,
    use_cache=True,
    token=None,
):
    defaults = _load_defaults()

    if experiment_id is None:
        experiment_id = int(defaults.get("experiment", {}).get("id"))

    if project_id is None:
        project_id = int(defaults.get("project_id") or os.getenv("AB_PROJECT_ID", "27"))
    cache_dir = os.path.join(SKILL_ROOT, ".cache")
    cache = CacheManager(cache_dir=cache_dir, ttl=300)
    cache_key = "ab_metrics_{}_{}_{}_{}".format(project_id, experiment_id, metrics, dates)
    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            return cached

    client = PlatformAPIClient(token=token)

    if not control:
        control_groups = defaults.get("control_groups") or []
        if control_groups:
            parts = []
            for x in control_groups:
                for p in str(x).split(","):
                    p = p.strip()
                    if p:
                        parts.append(p)
            control = ",".join(parts) if parts else ""

    if not treatments:
        treatment_groups = defaults.get("treatment_groups") or []
        if treatment_groups:
            treatments = []
            for x in treatment_groups:
                for p in str(x).split(","):
                    p = p.strip()
                    if p:
                        treatments.append(p)

    if not regions:
        regions = defaults.get("regions") or []

    if not dims:
        dims = defaults.get("dims") or []

    if not normalization:
        normalization = defaults.get("normalization") or None

    if not metrics:
        metrics = defaults.get("metrics") or get_default_metrics()

    # 去掉 control/treatments 中可能的前后空格，避免 ClickHouse TYPE_MISMATCH
    if control:
        control = ",".join(s.strip() for s in str(control).split(",") if s.strip())
    if treatments:
        treatments = [str(t).strip() for t in treatments if str(t).strip()]

    call_kwargs = {}
    if regions:
        call_kwargs["regions"] = regions
    if dims:
        call_kwargs["dims"] = dims

    call_kwargs["template_name"] = defaults.get("template_name") or "One Page - Search Core Metric"
    call_kwargs["template_group_name"] = defaults.get("template_group_name") or "Rollout Checklist"

    params = {
        "project_id": project_id,
        "experiment_id": experiment_id,
        "control": control,
        "treatments": treatments,
        "metrics": metrics,
        "dates": dates,
        "normalization": normalization,
    }
    params.update(call_kwargs)

    result = client.get_ab_metrics(**params)
    if result:
        result["experiment_id"] = experiment_id
        result["project_id"] = project_id
        result["formatted_text"] = format_ab_summary(result, experiment_id)
        result["lifts"] = extract_metric_lifts(result)
        grouped = get_grouped_summary(result)
        result["by_group"] = grouped.get("by_group", [])
        result["overall_treatment"] = grouped.get("overall_treatment")
        if use_cache:
            cache.set(cache_key, result)
    return result or {}


def main():
    parser = argparse.ArgumentParser(description="获取 AB 实验指标")
    parser.add_argument("experiment_id", type=int, nargs="?", default=None, help="实验 ID（可选：不填则读 defaults.json）")
    parser.add_argument("project_id", type=int, nargs="?", default=None, help="项目 ID（可选）")
    parser.add_argument("--metrics", type=str, default=None, help="指标列表，逗号分隔")
    parser.add_argument("--control", type=str, default="", help="对照组 ID")
    parser.add_argument("--treatments", type=str, default=None, help="实验组 ID，逗号分隔")
    parser.add_argument("--dates", type=str, default=None, help="日期范围 start,end")
    parser.add_argument("--regions", type=str, default=None, help="地区，逗号分隔")
    parser.add_argument("--dims", type=str, default=None, help="维度列表，逗号分隔")
    parser.add_argument("--normalization", type=str, default=None, help="归一化方式（如 control）")
    parser.add_argument("--token", type=str, default=None, help="AB API Token（不传则用环境变量 AB_API_TOKEN）")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--no-cache", action="store_true", help="不使用缓存")
    args = parser.parse_args()

    metrics = [m.strip() for m in args.metrics.split(",")] if args.metrics else None
    treatments = [t.strip() for t in args.treatments.split(",") if t.strip()] if args.treatments else None
    regions = [r.strip() for r in args.regions.split(",") if r.strip()] if args.regions else None
    dims = [d.strip() for d in args.dims.split(",") if d.strip()] if args.dims else None
    dates = None
    if args.dates:
        parts = args.dates.split(",")
        if len(parts) == 2:
            dates = [{"time_start": parts[0].strip(), "time_end": parts[1].strip()}]

    result = fetch_metrics(
        experiment_id=args.experiment_id,
        project_id=args.project_id,
        metrics=metrics,
        control=args.control,
        treatments=treatments,
        dates=dates,
        regions=regions,
        dims=dims,
        normalization=args.normalization,
        use_cache=not args.no_cache,
        token=args.token,
    )
    if not result:
        sys.stderr.write("获取数据失败\n")
        sys.exit(1)
    if (not result.get("columns")) and (not result.get("body")) and (not result.get("relative")):
        sys.stderr.write("获取数据失败（返回为空）\n")
        sys.exit(1)
    if args.json:
        out = {k: v for k, v in result.items() if k != "raw"}
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(result.get("formatted_text", "无数据"))


if __name__ == "__main__":
    main()
