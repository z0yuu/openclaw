#!/usr/bin/env python3
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
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(SKILL_ROOT, ".env"))
    load_dotenv(os.path.expanduser("~/.openclaw/workspace/.env"))
except ImportError:
    pass

from lib.ab_client import PlatformAPIClient, CacheManager, get_default_metrics
from lib.analysis import format_ab_summary, extract_metric_lifts


def fetch_metrics(
    experiment_id: int,
    project_id: int = None,
    metrics: list = None,
    control: str = "",
    treatments: list = None,
    dates: list = None,
    regions: list = None,
    use_cache: bool = True,
) -> dict:
    if project_id is None:
        project_id = int(os.getenv("AB_PROJECT_ID", "27"))
    cache_dir = os.path.join(SKILL_ROOT, ".cache")
    cache = CacheManager(cache_dir=cache_dir, ttl=300)
    cache_key = f"ab_metrics_{project_id}_{experiment_id}_{metrics}_{dates}"
    if use_cache:
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
        control=control,
        treatments=treatments,
        metrics=metrics or get_default_metrics(),
        dates=dates,
        **kwargs,
    )
    if result:
        result["experiment_id"] = experiment_id
        result["project_id"] = project_id
        result["formatted_text"] = format_ab_summary(result, experiment_id)
        result["lifts"] = extract_metric_lifts(result)
        if use_cache:
            cache.set(cache_key, result)
    return result or {}


def main():
    parser = argparse.ArgumentParser(description="获取 AB 实验指标")
    parser.add_argument("experiment_id", type=int, help="实验 ID")
    parser.add_argument("project_id", type=int, nargs="?", default=None, help="项目 ID")
    parser.add_argument("--metrics", type=str, default=None, help="指标列表，逗号分隔")
    parser.add_argument("--control", type=str, default="", help="对照组 ID")
    parser.add_argument("--treatments", type=str, default=None, help="实验组 ID，逗号分隔")
    parser.add_argument("--dates", type=str, default=None, help="日期范围 start,end")
    parser.add_argument("--regions", type=str, default=None, help="地区，逗号分隔")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--no-cache", action="store_true", help="不使用缓存")
    args = parser.parse_args()

    metrics = args.metrics.split(",") if args.metrics else None
    treatments = args.treatments.split(",") if args.treatments else None
    regions = args.regions.split(",") if args.regions else None
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
        use_cache=not args.no_cache,
    )
    if not result:
        print("获取数据失败", file=sys.stderr)
        sys.exit(1)
    if args.json:
        out = {k: v for k, v in result.items() if k != "raw"}
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(result.get("formatted_text", "无数据"))


if __name__ == "__main__":
    main()
