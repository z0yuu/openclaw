#!/usr/bin/env python3
"""Summarize smart tune result by local logs + ES correction.

Workflow:
1) List all files under /job/{job_id}/ego_tune_{smart_tune_job_id}
2) Download all files to local work dir
3) Focus on files whose names include cpu_config_tune / gpu_config_tune
4) Extract prev_learner_config, learner_config, resources, resources_delta
5) Run fixed ego-tune-kit image test_es_client.py to correct summary
6) Output final JSON summary
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from ego_api_common import EgoApiError, get_ego_tune_dir_files, get_ego_tune_log_content

ES_IMAGE = "harbor.shopeemobile.com/mlp-ego/ego-tune-kit:V1.0-dev-8053e182-sg-20260305204540"
ES_SCRIPT = "/workspace/ego-train-diag-tune/ego_tune/es_client/test_es_client.py"


def _is_non_empty(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, str):
        return v.strip() != ""
    if isinstance(v, (list, dict, tuple, set)):
        return len(v) > 0
    return True


def _sanitize_rel_path(name: str) -> str:
    cleaned = name.strip().replace("\\", "/")
    cleaned = re.sub(r"/+", "/", cleaned)
    cleaned = cleaned.lstrip("/")
    # Avoid parent traversal.
    parts = [p for p in cleaned.split("/") if p not in ("", ".", "..")]
    return "/".join(parts) if parts else "unnamed.log"


def _extract_file_names(obj: Any) -> list[str]:
    out: list[str] = []

    def walk(x: Any) -> None:
        if isinstance(x, str):
            s = x.strip()
            if not s:
                return
            # Keep paths / filenames; skip obvious non-file phrases.
            if "/" in s or "." in s:
                out.append(s)
            return
        if isinstance(x, list):
            for e in x:
                walk(e)
            return
        if isinstance(x, dict):
            for k in ("file_name", "name", "path", "log_file_name", "filePath"):
                v = x.get(k)
                if isinstance(v, str) and v.strip():
                    out.append(v.strip())
            for v in x.values():
                walk(v)

    if isinstance(obj, dict) and "data" in obj:
        walk(obj["data"])
    else:
        walk(obj)

    dedup: list[str] = []
    seen = set()
    for n in out:
        key = n.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        dedup.append(key)
    return dedup


def _extract_key_values(obj: Any, key: str) -> list[Any]:
    out: list[Any] = []

    def walk(x: Any) -> None:
        if isinstance(x, dict):
            for k, v in x.items():
                if k == key:
                    out.append(v)
                walk(v)
        elif isinstance(x, list):
            for e in x:
                walk(e)

    walk(obj)
    return out


def _try_parse_json(text: str) -> Any | None:
    text = (text or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting the largest JSON object/array block.
    for left, right in (("{", "}"), ("[", "]")):
        l = text.find(left)
        r = text.rfind(right)
        if l >= 0 and r > l:
            candidate = text[l : r + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
    return None


def _merge_latest(values: list[Any]) -> Any:
    for v in reversed(values):
        if _is_non_empty(v):
            return v
    return None


def _summarize_config_changes(prev_cfg: Any, new_cfg: Any) -> dict[str, Any]:
    if not isinstance(prev_cfg, dict) or not _is_non_empty(prev_cfg):
        return {"changes": [], "note": "prev_learner_config is empty; skip config diff"}
    if not isinstance(new_cfg, dict) or not _is_non_empty(new_cfg):
        return {"changes": [], "note": "learner_config is empty; skip config diff"}

    changes: list[dict[str, Any]] = []
    for k in sorted(set(prev_cfg.keys()) & set(new_cfg.keys())):
        old_v = prev_cfg.get(k)
        new_v = new_cfg.get(k)
        if old_v != new_v:
            changes.append({"key": k, "old_value": old_v, "new_value": new_v})
    return {"changes": changes}


def _summarize_resource_changes(resources: Any, delta: Any) -> dict[str, Any]:
    if not _is_non_empty(delta):
        return {"changes": [], "note": "resources_delta is empty; skip resource diff"}

    if isinstance(delta, dict):
        items: list[dict[str, Any]] = []
        for k, dv in delta.items():
            latest = resources.get(k) if isinstance(resources, dict) else None
            items.append({"resource": k, "delta": dv, "latest_value": latest})
        return {"changes": items}

    return {"changes": [{"resource": "<raw>", "delta": delta, "latest_value": resources}]}


def _extract_text_blobs(obj: Any) -> list[str]:
    out: list[str] = []

    def walk(x: Any) -> None:
        if isinstance(x, str):
            s = x.strip()
            if s:
                out.append(s)
            return
        if isinstance(x, list):
            for e in x:
                walk(e)
            return
        if isinstance(x, dict):
            for v in x.values():
                walk(v)

    walk(obj)
    return out


def _summarize_motivation(log_sources: list[Any]) -> list[str]:
    texts: list[str] = []
    for src in log_sources:
        texts.extend(_extract_text_blobs(src))
    merged = "\n".join(texts).lower()

    hints: list[str] = []
    rules = [
        ("data starvation", "数据供给不足（data starvation）导致训练线程喂数不稳定。"),
        ("get_batch_latency", "batch 获取延迟偏高，说明 I/O 或取数链路存在瓶颈。"),
        ("training_pass_batch_queue_size", "training_pass_batch_queue_size 多次见底，GPU 存在等待数据现象。"),
        ("memory_resident_sample_count_limit", "样本常驻内存触顶，可能触发磁盘缓存回退，影响吞吐。"),
        ("mpi barrier", "出现 MPI barrier 等待，存在慢 worker 拖尾。"),
        ("remote_io_threads", "建议提升 remote_io_threads 以改善 worker 侧取数并发。"),
        ("sample_server_num", "建议调整 sample_server_num 以缓解数据供给瓶颈。"),
        ("gpu_contexts_num", "建议调优 gpu_contexts_num / gpu_sessions_num 以降低上下文争用。"),
    ]
    for kw, msg in rules:
        if kw in merged:
            hints.append(msg)
    return hints[:8]


def _build_detailed_motivation_text(
    *,
    job_id: int,
    smart_tune_job_id: int,
    cluster: str,
    motivation: list[str],
    config_summary: dict[str, Any],
    resource_summary: dict[str, Any],
    es_parsed: Any,
) -> str:
    lines: list[str] = []
    lines.append(f"Smart Tune Detailed Motivation")
    lines.append(f"job_id={job_id}, smart_tune_job_id={smart_tune_job_id}, cluster={cluster}")
    lines.append("")

    lines.append("1) 调参动机（从 smart tune 日志与 ES 输出提炼）")
    if motivation:
        for i, m in enumerate(motivation, start=1):
            lines.append(f"{i}. {m}")
    else:
        lines.append("- 未提取到明确动机关键词。")
    lines.append("")

    # Evidence from ES parsed payload
    lines.append("2) 关键证据快照")
    if isinstance(es_parsed, dict):
        worker0 = (((es_parsed.get("pod_resource_usage") or {}).get("worker-0")) or {})
        gpu_active = worker0.get("gpu_active_stats") or {}
        gpu_all = worker0.get("gpu_util_stats") or {}
        max_gpu_mem = worker0.get("max_gpu_mem_util_ratio")
        if gpu_all:
            lines.append(f"- worker-0 平均 GPU 利用率(mean): {gpu_all.get('mean')}")
        if gpu_active:
            lines.append(f"- worker-0 活跃区间平均 GPU 利用率: {gpu_active.get('mean')}")
        if max_gpu_mem is not None:
            lines.append(f"- worker-0 最大 GPU 显存利用率: {max_gpu_mem}%")

        tune_log = es_parsed.get("tune_log") or {}
        worker_gpu = ((((tune_log.get("worker-0") or {}).get("GPU")) or {}))
        report_text = str(worker_gpu.get("report") or "")
        if report_text:
            for kw in (
                "data starvation",
                "get_batch_latency",
                "training_pass_batch_queue_size",
                "mpi barrier",
                "memory_resident_sample_count_limit",
            ):
                if kw.lower() in report_text.lower():
                    lines.append(f"- 日志报告中出现关键词: {kw}")
    else:
        lines.append("- ES 结果不可用，无法补充证据快照。")
    lines.append("")

    lines.append("3) 训练配置变化（同 key 对比）")
    cfg_changes = (config_summary or {}).get("changes") or []
    if cfg_changes:
        for c in cfg_changes:
            key = c.get("key")
            old_v = c.get("old_value")
            new_v = c.get("new_value")
            lines.append(f"- key={key}")
            lines.append(f"  old: {old_v}")
            lines.append(f"  new: {new_v}")
    else:
        note = (config_summary or {}).get("note")
        lines.append(f"- 无配置变化。{note or ''}".strip())
    lines.append("")

    lines.append("4) 资源变化（delta + 最新值）")
    res_changes = (resource_summary or {}).get("changes") or []
    if res_changes:
        for c in res_changes:
            r = c.get("resource")
            d = c.get("delta")
            lv = c.get("latest_value")
            lines.append(f"- resource={r}, delta={d}, latest={lv}")
    else:
        note = (resource_summary or {}).get("note")
        lines.append(f"- 无资源变化。{note or ''}".strip())
    lines.append("")

    lines.append("5) 变化背后的解释（面向执行）")
    lines.append("- 若报告显示数据供给不足与 get_batch_latency 偏高，通常优先提升取数并发和 sample server 供给能力。")
    lines.append("- 若队列频繁见底，说明训练线程存在等待数据，配置调整目标是缩短数据等待时间。")
    lines.append("- 若出现 MPI barrier 等待，说明存在慢 worker 拖尾，需同时关注 I/O 与分布式同步效率。")
    lines.append("- 本次资源变化集中在 ss，说明调参策略偏向提升样本服务侧吞吐与稳定性。")
    lines.append("")

    return "\n".join(lines)


def _run_es_correction(cluster: str, smart_tune_job_id: int, work_dir: Path) -> dict[str, Any]:
    stdout_path = work_dir / "es_correction_stdout.txt"
    stderr_path = work_dir / "es_correction_stderr.txt"
    base_cmd = [
        "docker",
        "run",
        "--rm",
        ES_IMAGE,
        "python",
        ES_SCRIPT,
        "--region",
        cluster,
        "--ego_tune_job_id",
        str(smart_tune_job_id),
    ]
    # Prefer sudo docker first.
    try:
        proc = subprocess.run(["sudo", "-n"] + base_cmd, text=True, capture_output=True, check=False)
        used = "sudo_docker"
    except FileNotFoundError:
        proc = None
        used = "none"
    except Exception as e:  # pragma: no cover
        return {"ran": False, "error": str(e)}

    # Fallback to plain docker if sudo path is unavailable or denied.
    if proc is None or (
        proc.returncode != 0
        and ("a password is required" in (proc.stderr or "").lower() or "not allowed" in (proc.stderr or "").lower())
    ):
        try:
            proc = subprocess.run(base_cmd, text=True, capture_output=True, check=False)
            used = "docker"
        except FileNotFoundError:
            return {"ran": False, "error": "docker not found"}
        except Exception as e:  # pragma: no cover
            return {"ran": False, "error": str(e)}

    stdout_path.write_text(proc.stdout or "", encoding="utf-8")
    stderr_path.write_text(proc.stderr or "", encoding="utf-8")

    parsed = _try_parse_json(proc.stdout or "")
    return {
        "ran": True,
        "executor": used,
        "exit_code": proc.returncode,
        "stdout_file": str(stdout_path),
        "stderr_file": str(stderr_path),
        "parsed": parsed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize smart tune result with ES correction")
    parser.add_argument("--job-id", type=int, required=True)
    parser.add_argument("--smart-tune-job-id", type=int, required=True)
    parser.add_argument("--cluster", type=str, required=True)
    parser.add_argument("--work-dir", type=str, required=True)
    parser.add_argument("--base-url", type=str)
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()

    work_dir = Path(args.work_dir).resolve()
    logs_dir = work_dir / "smart_tune_logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    try:
        listing = get_ego_tune_dir_files(
            args.job_id,
            args.smart_tune_job_id,
            base_url=args.base_url,
            timeout=args.timeout,
        )
    except EgoApiError as e:
        print(f"Error: failed to list smart tune directory files: {e}", file=sys.stderr)
        return 1

    listing_path = work_dir / "ego_tune_dir_listing.json"
    listing_path.write_text(json.dumps(listing, ensure_ascii=False, indent=2), encoding="utf-8")

    file_names = _extract_file_names(listing)
    download_errors: list[dict[str, str]] = []
    focused_files: list[str] = []
    local_focused_data: list[Any] = []

    for name in file_names:
        rel = _sanitize_rel_path(name)
        if not rel:
            continue
        out_path = logs_dir / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            content = get_ego_tune_log_content(
                args.job_id,
                args.smart_tune_job_id,
                rel,
                base_url=args.base_url,
                timeout=args.timeout,
            )
            out_path.write_text(content, encoding="utf-8")
        except EgoApiError as e:
            download_errors.append({"file": rel, "error": str(e)})
            continue

        low = Path(rel).name.lower()
        if "cpu_config_tune" in low or "gpu_config_tune" in low:
            focused_files.append(str(out_path))
            parsed = _try_parse_json(content)
            if parsed is not None:
                local_focused_data.append(parsed)

    # Aggregate local extracted fields.
    prev_candidates: list[Any] = []
    learner_candidates: list[Any] = []
    resources_candidates: list[Any] = []
    delta_candidates: list[Any] = []
    for obj in local_focused_data:
        prev_candidates.extend(_extract_key_values(obj, "prev_learner_config"))
        learner_candidates.extend(_extract_key_values(obj, "learner_config"))
        resources_candidates.extend(_extract_key_values(obj, "resources"))
        delta_candidates.extend(_extract_key_values(obj, "resources_delta"))

    local_prev = _merge_latest(prev_candidates)
    local_learner = _merge_latest(learner_candidates)
    local_resources = _merge_latest(resources_candidates)
    local_delta = _merge_latest(delta_candidates)

    es = _run_es_correction(args.cluster, args.smart_tune_job_id, work_dir)
    es_prev = es_learner = es_resources = es_delta = None
    if es.get("ran") and isinstance(es.get("parsed"), (dict, list)):
        parsed = es["parsed"]
        es_prev = _merge_latest(_extract_key_values(parsed, "prev_learner_config"))
        es_learner = _merge_latest(_extract_key_values(parsed, "learner_config"))
        es_resources = _merge_latest(_extract_key_values(parsed, "resources"))
        es_delta = _merge_latest(_extract_key_values(parsed, "resources_delta"))

    # ES correction takes precedence when non-empty.
    final_prev = es_prev if _is_non_empty(es_prev) else local_prev
    final_learner = es_learner if _is_non_empty(es_learner) else local_learner
    final_resources = es_resources if _is_non_empty(es_resources) else local_resources
    final_delta = es_delta if _is_non_empty(es_delta) else local_delta

    config_summary = _summarize_config_changes(final_prev, final_learner)
    resource_summary = _summarize_resource_changes(final_resources, final_delta)
    motivation = _summarize_motivation([local_focused_data, es.get("parsed")])

    summary = {
        "job_id": args.job_id,
        "smart_tune_job_id": args.smart_tune_job_id,
        "cluster": args.cluster,
        "log_pull": {
            "listing_file": str(listing_path),
            "local_logs_dir": str(logs_dir),
            "total_listed_files": len(file_names),
            "focused_files": focused_files,
            "download_errors": download_errors,
        },
        "es_correction": es,
        "final_summary": {
            "training_config_changes": config_summary,
            "resource_changes": resource_summary,
            "tuning_motivation": motivation,
        },
    }

    detail_text = _build_detailed_motivation_text(
        job_id=args.job_id,
        smart_tune_job_id=args.smart_tune_job_id,
        cluster=args.cluster,
        motivation=motivation,
        config_summary=config_summary,
        resource_summary=resource_summary,
        es_parsed=es.get("parsed"),
    )
    detail_txt_path = work_dir / "tuning_motivation_detail.txt"
    detail_txt_path.write_text(detail_text, encoding="utf-8")
    summary["final_summary"]["tuning_motivation_detail_file"] = str(detail_txt_path)

    output_json = work_dir / "smart_tune_summary.json"
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    summary["summary_json"] = str(output_json)

    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
