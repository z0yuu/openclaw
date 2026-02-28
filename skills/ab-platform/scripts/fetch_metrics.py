#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AB 指标查询（ab-platform skill）
从 Shopee AB Report Open API 获取单实验指标并格式化输出。
兼容 Python 2.7.18 / Python 3.x
"""

from __future__ import absolute_import, division, print_function

import argparse
import io
import json
import os
import sys

# Python 2: 让 sys.stdout 能输出 UTF-8（否则 print(unicode) 报 ascii 编码错误）
if sys.version_info[0] < 3:
    sys.stdout = io.open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False)
    sys.stderr = io.open(sys.stderr.fileno(), mode="w", encoding="utf-8", closefd=False)

# Skill 根目录 = scripts 的上一级
SKILL_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# 需要把 skill 根目录与其 lib/ 都加入 sys.path，兼容从任意 cwd 运行
for p in [SKILL_ROOT, os.path.join(SKILL_ROOT, "lib")]:
    if p not in sys.path:
        sys.path.insert(0, p)


def _load_env_file(path):
    """不依赖 dotenv：手动读 .env 并写入 os.environ，供 Python 2 或无 dotenv 时使用"""
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
# Python 2 常未安装 python-dotenv，用回退加载保证 token 等从 ~/.openclaw/.env 读入
_load_env_file(os.path.expanduser("~/.openclaw/.env"))
_load_env_file(os.path.join(SKILL_ROOT, ".env"))

from ab_client import PlatformAPIClient, CacheManager, get_default_metrics
from analysis import (
    format_ab_summary, format_lift_report, get_daily_lift_summary,
    extract_metric_lifts, get_grouped_summary, DIMENSION_COLUMNS,
)


def _load_defaults():
    cfg_path = os.path.join(SKILL_ROOT, "defaults.json")
    if not os.path.exists(cfg_path):
        return {}
    try:
        with open(cfg_path, "r") as f:
            return json.load(f).get("ab_platform", {})
    except Exception:
        return {}


def _load_bucket_map():
    """从 bucket_name.txt 加载 {numeric_id: bucket_name} 映射"""
    path = os.path.join(SKILL_ROOT, "bucket_name.txt")
    mapping = {}
    if not os.path.exists(path):
        return mapping
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    bucket_name = parts[0].strip()
                    numeric_id = parts[1].strip()
                    mapping[numeric_id] = bucket_name
    except Exception:
        pass
    return mapping


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
    card_type=None,
    sort_type=None,
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
                for p in str(x).replace(";", ",").split(","):
                    p = p.strip()
                    if p:
                        parts.append(p)
            control = ";".join(parts) if parts else ""

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

    if not card_type:
        card_type = defaults.get("card_type") or None

    if not sort_type:
        sort_type = defaults.get("sort_type") or None

    if not metrics:
        metrics = defaults.get("metrics") or get_default_metrics()

    if control:
        control = ";".join(s.strip() for s in str(control).replace(",", ";").split(";") if s.strip())
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

    if result and card_type:
        ct = card_type.strip().lower()
        for key in ("body", "relative"):
            rows = result.get(key)
            if rows:
                result[key] = [r for r in rows if str(r.get("card_type", "")).strip().lower() == ct]

    if result and sort_type:
        st = sort_type.strip().lower()
        for key in ("body", "relative"):
            rows = result.get(key)
            if rows:
                result[key] = [r for r in rows if str(r.get("sort_type", "")).strip().lower() == st]

    if result:
        result["experiment_id"] = experiment_id
        result["project_id"] = project_id
        _bmap = _load_bucket_map()
        _ctrl_ids = defaults.get("control_groups") or []
        result["formatted_text"] = format_ab_summary(result, experiment_id,
                                                     bucket_map=_bmap, control_group_ids=_ctrl_ids)
        result["lifts"] = extract_metric_lifts(result)
        grouped = get_grouped_summary(result, bucket_map=_bmap, control_group_ids=_ctrl_ids)
        result["by_group"] = [g for g in grouped.get("by_group", []) if not g.get("is_control")]
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
    parser.add_argument("--region", type=str, default=None, help="地区（单值，等同 --regions 的简写）")
    parser.add_argument("--dims", type=str, default=None, help="维度列表，逗号分隔")
    parser.add_argument("--normalization", type=str, default=None, help="归一化方式（如 control）")
    parser.add_argument("--token", type=str, default=None, help="AB API Token（不传则用环境变量 AB_API_TOKEN）")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--absolute", action="store_true", help="同时显示绝对值（默认只显示相对提升百分比）")
    parser.add_argument("--card-type", type=str, default=None, help="卡片类型过滤（如 allcard, item 等，默认读 defaults.json）")
    parser.add_argument("--sort-type", type=str, default=None, help="排序类型过滤（如 __ALL__, relevancy 等，默认读 defaults.json）")
    parser.add_argument("--cache", action="store_true", help="启用缓存（默认不缓存）")
    args = parser.parse_args()

    metrics = [m.strip() for m in args.metrics.split(",")] if args.metrics else None
    treatments = [t.strip() for t in args.treatments.split(",") if t.strip()] if args.treatments else None
    regions_str = args.regions or args.region
    regions = [r.strip() for r in regions_str.split(",") if r.strip()] if regions_str else None
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
        use_cache=args.cache,
        token=args.token,
        card_type=args.card_type,
        sort_type=args.sort_type,
    )
    if not result:
        sys.stderr.write("获取数据失败\n")
        sys.exit(1)
    if (not result.get("columns")) and (not result.get("body")) and (not result.get("relative")):
        sys.stderr.write("获取数据失败（返回为空）\n")
        sys.exit(1)
    bucket_map = _load_bucket_map()
    defaults = _load_defaults()
    ctrl_ids = defaults.get("control_groups") or []
    _fmt_kwargs = dict(bucket_map=bucket_map, control_group_ids=ctrl_ids)
    if args.json:
        out = dict((k, v) for k, v in result.items() if k != "raw")
        out["bucket_map"] = bucket_map
        out["daily_lifts"] = get_daily_lift_summary(result, **_fmt_kwargs)
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        text = format_lift_report(result, experiment_id=result.get("experiment_id", 0),
                                  show_absolute=args.absolute, **_fmt_kwargs)
        print(text)


if __name__ == "__main__":
    main()
