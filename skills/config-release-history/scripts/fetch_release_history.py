#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
实验配置平台发布记录查询（config-release-history skill）
从 Shopee Config Platform（通过 OpsGW）获取历史发布记录并计算 diff。
兼容 Python 2.7.18 / Python 3.x
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import codecs
import datetime
import difflib
import json
import os
import socket
import sys

if sys.version_info[0] < 3:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr)

try:
    string_types = (str, unicode)
except NameError:
    string_types = (str,)

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

OPSGW_SOCKET = "/tmp/opsgw_caller_agent.sock"
PRODUCT_ID = "569e5052-9ee7-11ee-afc9-9292fa2d06e8"
DEFAULT_PROJECT = "search_rankservice"
DEFAULT_ZONE = "global"
PAGE_SIZE = 100
MAX_DIFF_LINES = 40


# ---------------------------------------------------------------------------
# Network helpers
# ---------------------------------------------------------------------------

def build_url(project, namespace, zone, page_token=None):
    url = (
        "http://localhost/openapi/v2/projects/{project}"
        "/envs/live/namespaces/{namespace}/zones/{zone}/states"
    ).format(project=project, namespace=namespace, zone=zone)
    if page_token:
        url += "?page_token={0}".format(page_token)
    return url


def http_get_via_unix_socket(socket_path, url):
    """Send an HTTP GET through a UNIX domain socket and return the response body."""
    parsed = urlparse(url)
    path = parsed.path
    if parsed.query:
        path += "?" + parsed.query

    request_lines = [
        "GET {path} HTTP/1.1".format(path=path),
        "Host: {0}".format(PRODUCT_ID),
        "X-Opsgw-Caller-Agent-Product: {0}".format(PRODUCT_ID),
        "X-Opsgw-Caller-Agent-Forwarding-Bu: shopee",
        "X-Opsgw-Caller-Agent-Forwarding-Env: live",
        "Connection: close",
        "",
        "",
    ]
    raw_request = "\r\n".join(request_lines).encode("utf-8")

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(60)
    sock.connect(socket_path)
    sock.sendall(raw_request)

    chunks = []
    while True:
        chunk = sock.recv(65536)
        if not chunk:
            break
        chunks.append(chunk)
    sock.close()

    raw_response = b"".join(chunks)
    header_end = raw_response.find(b"\r\n\r\n")
    if header_end == -1:
        raise RuntimeError("Invalid HTTP response: no header/body separator")

    headers_raw = raw_response[:header_end].decode("utf-8", "replace")
    status_line = headers_raw.split("\r\n")[0]
    if "200" not in status_line:
        raise RuntimeError("HTTP error: {0}".format(status_line))

    body = raw_response[header_end + 4:]

    if b"Transfer-Encoding: chunked" in raw_response[:header_end]:
        body = _decode_chunked(body)

    return body.decode("utf-8")


def _decode_chunked(data):
    """Decode HTTP chunked transfer encoding."""
    result = bytearray()
    idx = 0
    while idx < len(data):
        line_end = data.find(b"\r\n", idx)
        if line_end == -1:
            break
        size_str = data[idx:line_end].decode("ascii").strip()
        if not size_str:
            idx = line_end + 2
            continue
        chunk_size = int(size_str, 16)
        if chunk_size == 0:
            break
        chunk_start = line_end + 2
        result.extend(data[chunk_start : chunk_start + chunk_size])
        idx = chunk_start + chunk_size + 2
    return bytes(result)


def fetch_states(project, namespace, zone, max_versions):
    """Fetch namespace states with pagination."""
    all_states = []
    page_token = None
    total_size = None

    while len(all_states) < max_versions:
        url = build_url(project, namespace, zone, page_token)
        body = http_get_via_unix_socket(OPSGW_SOCKET, url)
        data = json.loads(body)

        states = data.get("namespace_states", data.get("states", []))
        if not states:
            break

        all_states.extend(states)
        if total_size is None:
            total_size = data.get("total_size", len(states))

        page_token = data.get("next_page_token")
        if not page_token:
            break

    return all_states[:max_versions], total_size or len(all_states)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def format_timestamp(ts):
    if isinstance(ts, string_types):
        ts = int(ts)
    if not ts:
        return "N/A"
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def try_parse_json(text):
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return None


def try_format_json(text):
    try:
        obj = json.loads(text)
        return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True)
    except (ValueError, TypeError):
        return text


def _canon(obj):
    """Canonical JSON string for comparison."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Bucket-level analysis (ABLayer + Predictor cross-reference)
# ---------------------------------------------------------------------------

def _extract_predictor_names_from_dag(dag_list):
    """Extract individual predictor names from a predictor_dag list (list of '-> ' chains)."""
    names = []
    for chain in dag_list:
        if isinstance(chain, string_types):
            for part in chain.split("->"):
                name = part.strip()
                if name:
                    names.append(name)
    return names


def _diff_bucket(old_bucket, new_bucket):
    """Compare two bucket dicts, return list of field-level changes."""
    changes = []
    all_fields = sorted(set(list(old_bucket.keys()) + list(new_bucket.keys())))
    for field in all_fields:
        old_val = old_bucket.get(field)
        new_val = new_bucket.get(field)
        if _canon(old_val) != _canon(new_val):
            changes.append({
                "field": field,
                "old": old_val,
                "new": new_val,
            })
    return changes


def _diff_predictor_list(old_list, new_list):
    """Compare two predictor lists (list of dicts with 'name'), return structured changes."""
    old_by_name = {}
    new_by_name = {}
    for item in old_list:
        if isinstance(item, dict) and "name" in item:
            old_by_name[item["name"]] = item
    for item in new_list:
        if isinstance(item, dict) and "name" in item:
            new_by_name[item["name"]] = item

    old_names = set(old_by_name.keys())
    new_names = set(new_by_name.keys())
    added = sorted(new_names - old_names)
    removed = sorted(old_names - new_names)
    modified = []
    for name in sorted(old_names & new_names):
        if _canon(old_by_name[name]) != _canon(new_by_name[name]):
            modified.append(name)

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "old_by_name": old_by_name,
        "new_by_name": new_by_name,
    }


def _find_buckets_referencing(ablayer_dict, predictor_names):
    """Find all buckets whose predictor_dag references any of the given predictor names."""
    affected = {}
    for bucket_name, bucket_cfg in ablayer_dict.items():
        if not isinstance(bucket_cfg, dict):
            continue
        dag_list = bucket_cfg.get("predictor_dag", [])
        if not isinstance(dag_list, list):
            continue
        dag_predictors = set(_extract_predictor_names_from_dag(dag_list))
        matched = dag_predictors & predictor_names
        if matched:
            affected[bucket_name] = sorted(matched)
    return affected


def compute_smart_diff(old_items, new_items):
    """Compute a bucket-centric diff between two versions."""
    result = {
        "has_changes": False,
        "bucket_changes": [],
        "predictor_changes": None,
        "affected_buckets": [],
        "other_key_changes": [],
    }

    ablayer_key = None
    predictor_key = None
    for key in set(list(old_items.keys()) + list(new_items.keys())):
        kl = key.lower()
        if "ablayer" in kl:
            ablayer_key = key
        elif "predictor" in kl:
            predictor_key = key

    # --- ABLayer bucket analysis ---
    old_ablayer_raw = old_items.get(ablayer_key, {}).get("text_value", "") if ablayer_key else ""
    new_ablayer_raw = new_items.get(ablayer_key, {}).get("text_value", "") if ablayer_key else ""
    old_ablayer = try_parse_json(old_ablayer_raw) if old_ablayer_raw else {}
    new_ablayer = try_parse_json(new_ablayer_raw) if new_ablayer_raw else {}
    if not isinstance(old_ablayer, dict):
        old_ablayer = {}
    if not isinstance(new_ablayer, dict):
        new_ablayer = {}

    dag_changed_buckets = set()
    all_buckets = sorted(set(list(old_ablayer.keys()) + list(new_ablayer.keys())))
    for bucket_name in all_buckets:
        old_bk = old_ablayer.get(bucket_name, {})
        new_bk = new_ablayer.get(bucket_name, {})
        if _canon(old_bk) == _canon(new_bk):
            continue
        dag_changed_buckets.add(bucket_name)
        if bucket_name not in old_ablayer:
            result["bucket_changes"].append({
                "bucket": bucket_name,
                "change_type": "added",
                "field_changes": [],
            })
        elif bucket_name not in new_ablayer:
            result["bucket_changes"].append({
                "bucket": bucket_name,
                "change_type": "removed",
                "field_changes": [],
            })
        else:
            field_changes = _diff_bucket(old_bk, new_bk)
            result["bucket_changes"].append({
                "bucket": bucket_name,
                "change_type": "modified",
                "field_changes": field_changes,
            })

    # --- Predictor analysis ---
    old_pred_raw = old_items.get(predictor_key, {}).get("text_value", "") if predictor_key else ""
    new_pred_raw = new_items.get(predictor_key, {}).get("text_value", "") if predictor_key else ""
    old_pred_list = try_parse_json(old_pred_raw) if old_pred_raw else []
    new_pred_list = try_parse_json(new_pred_raw) if new_pred_raw else []
    if not isinstance(old_pred_list, list):
        old_pred_list = []
    if not isinstance(new_pred_list, list):
        new_pred_list = []

    pred_diff = _diff_predictor_list(old_pred_list, new_pred_list)
    if pred_diff["added"] or pred_diff["removed"] or pred_diff["modified"]:
        result["predictor_changes"] = pred_diff

    # --- Cross-reference: find buckets affected by predictor changes ---
    changed_pred_names = set(
        pred_diff["added"] + pred_diff["removed"] + pred_diff["modified"]
    )
    if changed_pred_names:
        ref_ablayer = new_ablayer if new_ablayer else old_ablayer
        pred_affected = _find_buckets_referencing(ref_ablayer, changed_pred_names)
        for bucket_name in sorted(pred_affected.keys()):
            if bucket_name not in dag_changed_buckets:
                result["affected_buckets"].append({
                    "bucket": bucket_name,
                    "reason": "predictor_changed",
                    "matched_predictors": pred_affected[bucket_name],
                })

    # --- Other keys (non ABLayer/Predictor) ---
    handled_keys = set()
    if ablayer_key:
        handled_keys.add(ablayer_key)
    if predictor_key:
        handled_keys.add(predictor_key)
    for key in sorted(set(list(old_items.keys()) + list(new_items.keys()))):
        if key in handled_keys:
            continue
        old_val = old_items.get(key, {}).get("text_value", "")
        new_val = new_items.get(key, {}).get("text_value", "")
        if old_val != new_val:
            result["other_key_changes"].append(key)

    result["has_changes"] = bool(
        result["bucket_changes"]
        or result["predictor_changes"]
        or result["affected_buckets"]
        or result["other_key_changes"]
    )

    return result


# ---------------------------------------------------------------------------
# Raw diff (legacy, available via --raw-diff)
# ---------------------------------------------------------------------------

def compute_diff(old_items, new_items, key_filter=None, full_diff=False):
    """Compute raw unified diff between two versions' items."""
    all_keys = sorted(set(old_items.keys()) | set(new_items.keys()))
    if key_filter:
        kf_lower = key_filter.lower()
        all_keys = [k for k in all_keys if kf_lower in k.lower()]

    changes = []
    for key in all_keys:
        old_val = old_items.get(key, {}).get("text_value", "")
        new_val = new_items.get(key, {}).get("text_value", "")

        old_formatted = try_format_json(old_val)
        new_formatted = try_format_json(new_val)

        if old_formatted == new_formatted:
            continue

        if key not in old_items:
            entry = {"key": key, "type": "added", "diff_lines": []}
            new_lines = new_formatted.splitlines()
            if full_diff or len(new_lines) <= MAX_DIFF_LINES:
                entry["diff_lines"] = ["+ " + l for l in new_lines]
            else:
                half = MAX_DIFF_LINES // 2
                entry["diff_lines"] = (
                    ["+ " + l for l in new_lines[:half]]
                    + ["  ... ({0} 行省略，使用 --full-diff 查看) ...".format(len(new_lines) - MAX_DIFF_LINES)]
                    + ["+ " + l for l in new_lines[-half:]]
                )
            changes.append(entry)
        elif key not in new_items:
            entry = {"key": key, "type": "removed", "diff_lines": []}
            old_lines = old_formatted.splitlines()
            if full_diff or len(old_lines) <= MAX_DIFF_LINES:
                entry["diff_lines"] = ["- " + l for l in old_lines]
            else:
                entry["diff_lines"] = [
                    "  ({0} 行已删除)".format(len(old_lines))
                ]
            changes.append(entry)
        else:
            old_lines = old_formatted.splitlines()
            new_lines = new_formatted.splitlines()
            diff = list(
                difflib.unified_diff(old_lines, new_lines, lineterm="", n=3)
            )
            if not diff:
                continue
            diff = diff[2:]

            entry = {"key": key, "type": "changed", "diff_lines": []}
            if full_diff or len(diff) <= MAX_DIFF_LINES:
                entry["diff_lines"] = diff
            else:
                half = MAX_DIFF_LINES // 2
                entry["diff_lines"] = (
                    diff[:half]
                    + ["  ... ({0} 行省略，使用 --full-diff 查看) ...".format(len(diff) - MAX_DIFF_LINES)]
                    + diff[-half:]
                )
            changes.append(entry)

    return changes


# ---------------------------------------------------------------------------
# Text output
# ---------------------------------------------------------------------------

def _format_dag_value(val):
    """Format a predictor_dag or other field value for display."""
    if isinstance(val, list):
        if len(val) == 1 and isinstance(val[0], string_types):
            return val[0]
        return json.dumps(val, ensure_ascii=False)
    if isinstance(val, string_types):
        return val
    return json.dumps(val, ensure_ascii=False)


def print_smart_report(states, total_size, namespace):
    print("")
    print("=" * 60)
    print("  发布记录: {0}".format(namespace))
    print("  共 {0} 个版本，显示最近 {1} 个".format(total_size, len(states)))
    print("=" * 60)
    print("")

    for i, state in enumerate(states):
        version = state.get("version", "?")
        status = state.get("status", "?")
        update_time = format_timestamp(state.get("update_time", 0))
        create_time = format_timestamp(state.get("create_time", 0))

        label = " (当前生效)" if i == 0 and status == "FULL" else ""
        print("--- Version {0}{1} ---".format(version, label))
        print("  发布时间: {0}  (创建: {1})".format(update_time, create_time))
        print("  状态: {0}".format(status))

        if i < len(states) - 1:
            older = states[i + 1]
            old_items = older.get("full_spec", {}).get("items", {})
            new_items = state.get("full_spec", {}).get("items", {})
            diff = compute_smart_diff(old_items, new_items)
            older_ver = older.get("version", "?")

            if not diff["has_changes"]:
                print("")
                print("  (与上一版本 v{0} 相比无变化)".format(older_ver))
            else:
                print("")
                print("  与上一版本 (v{0}) 的差异:".format(older_ver))

                if diff["bucket_changes"]:
                    print("")
                    print("  [DAG 变更] 直接修改的实验桶 ({0} 个):".format(len(diff["bucket_changes"])))
                    for bc in diff["bucket_changes"]:
                        if bc["change_type"] == "added":
                            print("    {0}: 新增桶".format(bc["bucket"]))
                        elif bc["change_type"] == "removed":
                            print("    {0}: 已删除".format(bc["bucket"]))
                        else:
                            changed_fields = [fc["field"] for fc in bc["field_changes"]]
                            print("    {0}: 变更字段 {1}".format(
                                bc["bucket"], ", ".join(changed_fields)))
                            for fc in bc["field_changes"]:
                                old_str = _format_dag_value(fc["old"])
                                new_str = _format_dag_value(fc["new"])
                                print("      {0}:".format(fc["field"]))
                                print("        旧: {0}".format(old_str))
                                print("        新: {0}".format(new_str))

                if diff["predictor_changes"]:
                    pc = diff["predictor_changes"]
                    print("")
                    total_pred_changes = len(pc["added"]) + len(pc["removed"]) + len(pc["modified"])
                    print("  [Predictor 变更] ({0} 个):".format(total_pred_changes))
                    for name in pc["added"]:
                        pred = pc["new_by_name"].get(name, {})
                        ptype = pred.get("type", "")
                        expr = pred.get("expr", "")
                        desc = ptype
                        if expr:
                            desc += ", expr={0}".format(
                                expr if len(expr) <= 80 else expr[:77] + "...")
                        print("    + {0} ({1})".format(name, desc))
                    for name in pc["removed"]:
                        print("    - {0}".format(name))
                    for name in pc["modified"]:
                        old_pred = pc["old_by_name"].get(name, {})
                        new_pred = pc["new_by_name"].get(name, {})
                        changed_attrs = []
                        all_attrs = sorted(set(
                            list(old_pred.keys()) + list(new_pred.keys())))
                        for attr in all_attrs:
                            if _canon(old_pred.get(attr)) != _canon(new_pred.get(attr)):
                                changed_attrs.append(attr)
                        print("    ~ {0} (变更: {1})".format(name, ", ".join(changed_attrs)))

                if diff["affected_buckets"]:
                    print("")
                    print("  [Predictor 关联] 因 Predictor 变更而受影响的桶 ({0} 个):".format(
                        len(diff["affected_buckets"])))
                    for ab in diff["affected_buckets"]:
                        print("    {0}: 引用了变更的 predictor {1}".format(
                            ab["bucket"], ", ".join(ab["matched_predictors"])))

                # --- Summary: all affected buckets ---
                all_affected = []
                for bc in diff["bucket_changes"]:
                    all_affected.append((bc["bucket"], "DAG 直接变更"))
                for ab in diff["affected_buckets"]:
                    all_affected.append((ab["bucket"], "Predictor 关联"))
                if all_affected:
                    print("")
                    print("  ** 所有受影响的实验桶汇总 ({0} 个): {1}".format(
                        len(all_affected),
                        ", ".join(b[0] for b in all_affected)))

                if diff["other_key_changes"]:
                    print("")
                    print("  [其他] 变更的 key: {0}".format(
                        ", ".join(diff["other_key_changes"])))

        print("")


def print_raw_report(states, total_size, namespace, key_filter, full_diff):
    print("")
    print("=" * 60)
    print("  发布记录 (raw diff): {0}".format(namespace))
    print("  共 {0} 个版本，显示最近 {1} 个".format(total_size, len(states)))
    print("=" * 60)
    print("")

    type_labels = {"added": "新增", "removed": "删除", "changed": "变更"}
    for i, state in enumerate(states):
        version = state.get("version", "?")
        status = state.get("status", "?")
        update_time = format_timestamp(state.get("update_time", 0))
        create_time = format_timestamp(state.get("create_time", 0))

        label = " (当前生效)" if i == 0 and status == "FULL" else ""
        print("--- Version {0}{1} ---".format(version, label))
        print("  发布时间: {0}  (创建: {1})".format(update_time, create_time))
        print("  状态: {0}".format(status))

        if i < len(states) - 1:
            older = states[i + 1]
            old_items = older.get("full_spec", {}).get("items", {})
            new_items = state.get("full_spec", {}).get("items", {})
            changes = compute_diff(old_items, new_items, key_filter, full_diff)

            if changes:
                older_ver = older.get("version", "?")
                print("")
                print("  与上一版本 (v{0}) 的差异:".format(older_ver))
                for c in changes:
                    print("  [{0}] {1}:".format(type_labels[c["type"]], c["key"]))
                    for line in c["diff_lines"]:
                        print("    {0}".format(line))
            else:
                if key_filter:
                    print("")
                    print("  (与上一版本相比，匹配 '{0}' 的 key 无变化)".format(key_filter))
                else:
                    print("")
                    print("  (与上一版本相比无变化)")

        print("")


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------

def build_json_report(states, total_size, namespace, raw_diff, key_filter, full_diff):
    records = []
    for i, state in enumerate(states):
        record = {
            "version": state.get("version"),
            "status": state.get("status"),
            "update_time": format_timestamp(state.get("update_time", 0)),
            "create_time": format_timestamp(state.get("create_time", 0)),
            "is_current": i == 0 and state.get("status") == "FULL",
        }
        if i < len(states) - 1:
            older = states[i + 1]
            old_items = older.get("full_spec", {}).get("items", {})
            new_items = state.get("full_spec", {}).get("items", {})

            if raw_diff:
                changes = compute_diff(old_items, new_items, key_filter, full_diff)
                record["changes"] = [
                    {"key": c["key"], "type": c["type"], "diff": c["diff_lines"]}
                    for c in changes
                ]
            else:
                diff = compute_smart_diff(old_items, new_items)
                record["has_changes"] = diff["has_changes"]
                record["bucket_changes"] = []
                for bc in diff["bucket_changes"]:
                    entry = {
                        "bucket": bc["bucket"],
                        "change_type": bc["change_type"],
                    }
                    if bc["field_changes"]:
                        entry["field_changes"] = [
                            {
                                "field": fc["field"],
                                "old": _format_dag_value(fc["old"]),
                                "new": _format_dag_value(fc["new"]),
                            }
                            for fc in bc["field_changes"]
                        ]
                    record["bucket_changes"].append(entry)
                if diff["predictor_changes"]:
                    pc = diff["predictor_changes"]
                    record["predictor_changes"] = {
                        "added": pc["added"],
                        "removed": pc["removed"],
                        "modified": pc["modified"],
                    }
                if diff["affected_buckets"]:
                    record["affected_buckets"] = [
                        {
                            "bucket": ab["bucket"],
                            "reason": ab["reason"],
                            "matched_predictors": ab["matched_predictors"],
                        }
                        for ab in diff["affected_buckets"]
                    ]
                all_affected = (
                    [bc["bucket"] for bc in diff["bucket_changes"]]
                    + [ab["bucket"] for ab in diff["affected_buckets"]]
                )
                if all_affected:
                    record["all_affected_buckets"] = all_affected
                if diff["other_key_changes"]:
                    record["other_key_changes"] = diff["other_key_changes"]
        records.append(record)

    return {
        "namespace": namespace,
        "total_versions": total_size,
        "displayed_versions": len(states),
        "records": records,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="查询 Shopee Config Platform 历史发布记录"
    )
    parser.add_argument("namespace", help="配置 namespace，如 item_prerank_live_id")
    parser.add_argument(
        "--project", default=DEFAULT_PROJECT,
        help="项目名（默认 {0}）".format(DEFAULT_PROJECT),
    )
    parser.add_argument(
        "--zone", default=DEFAULT_ZONE,
        help="zone（默认 {0}）".format(DEFAULT_ZONE),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="最多显示版本数（默认 10）",
    )
    parser.add_argument(
        "--key-filter",
        default=None,
        help="(仅 --raw-diff 模式) 只显示 key 名包含此字符串的变更",
    )
    parser.add_argument(
        "--full-diff", action="store_true",
        help="(仅 --raw-diff 模式) 显示完整 diff，不截断",
    )
    parser.add_argument(
        "--raw-diff", action="store_true",
        help="使用原始 unified diff 模式（默认使用桶级别智能分析）",
    )
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")

    args = parser.parse_args()

    need_extra = args.limit + 1
    states, total_size = fetch_states(
        args.project, args.namespace, args.zone, need_extra
    )

    if not states:
        print("错误: namespace '{0}' 未返回任何版本数据".format(args.namespace), file=sys.stderr)
        sys.exit(1)

    display_states = states[: args.limit]

    if args.json:
        report = build_json_report(
            display_states, total_size, args.namespace,
            args.raw_diff, args.key_filter, args.full_diff,
        )
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.raw_diff:
        print_raw_report(
            display_states, total_size, args.namespace, args.key_filter, args.full_diff
        )
    else:
        print_smart_report(display_states, total_size, args.namespace)


if __name__ == "__main__":
    main()
