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


def format_timestamp(ts):
    if isinstance(ts, string_types):
        ts = int(ts)
    if not ts:
        return "N/A"
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def try_format_json(text):
    """Try to parse and pretty-print JSON for cleaner diffs."""
    try:
        obj = json.loads(text)
        return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True)
    except (ValueError, TypeError):
        return text


def compute_diff(old_items, new_items, key_filter=None, full_diff=False):
    """Compute diff between two versions' items."""
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
            diff = diff[2:]  # skip --- and +++ header lines

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


TYPE_LABELS = {"added": "新增", "removed": "删除", "changed": "变更"}


def print_text_report(states, total_size, namespace, key_filter, full_diff):
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
            changes = compute_diff(old_items, new_items, key_filter, full_diff)

            if changes:
                older_ver = older.get("version", "?")
                print("")
                print("  与上一版本 (v{0}) 的差异:".format(older_ver))
                for c in changes:
                    print("  [{0}] {1}:".format(TYPE_LABELS[c["type"]], c["key"]))
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


def build_json_report(states, total_size, namespace, key_filter, full_diff):
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
            changes = compute_diff(old_items, new_items, key_filter, full_diff)
            record["changes"] = [
                {"key": c["key"], "type": c["type"], "diff": c["diff_lines"]}
                for c in changes
            ]
        records.append(record)

    return {
        "namespace": namespace,
        "total_versions": total_size,
        "displayed_versions": len(states),
        "records": records,
    }


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
        help="只显示 key 名包含此字符串的变更",
    )
    parser.add_argument(
        "--full-diff", action="store_true", help="显示完整 diff，不截断"
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
            display_states, total_size, args.namespace, args.key_filter, args.full_diff
        )
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_text_report(
            display_states, total_size, args.namespace, args.key_filter, args.full_diff
        )


if __name__ == "__main__":
    main()
