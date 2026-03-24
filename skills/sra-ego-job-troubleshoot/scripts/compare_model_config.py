#!/usr/bin/env python3
"""Compare two model_config.readable files and emit structured differences.

This helper intentionally stops at fact extraction:
- slot-group membership and optimizer layout
- dnn_slices membership and optimizer layout
- per-slot presence / absence on each side

Root-cause judgment stays in the calling skill.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _parse_scalar(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    if raw in {"true", "false"}:
        return raw == "true"
    try:
        return int(raw)
    except ValueError:
        return raw


def _append_value(dst: dict[str, Any], key: str, value: Any) -> None:
    if key not in dst:
        dst[key] = value
        return
    existing = dst[key]
    if isinstance(existing, list):
        existing.append(value)
        return
    dst[key] = [existing, value]


def parse_textproto(path: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[dict[str, Any]] = [root]

    with open(path, "r", encoding="utf-8") as f:
        for lineno, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue
            if line.endswith("{"):
                key = line[:-1].strip()
                if not key:
                    raise ValueError(f"{path}:{lineno}: malformed block line")
                new_obj: dict[str, Any] = {}
                _append_value(stack[-1], key, new_obj)
                stack.append(new_obj)
                continue
            if line == "}":
                if len(stack) == 1:
                    raise ValueError(f"{path}:{lineno}: unexpected closing brace")
                stack.pop()
                continue
            if ":" not in line:
                raise ValueError(f"{path}:{lineno}: malformed scalar line: {line}")
            key, raw_value = line.split(":", 1)
            _append_value(stack[-1], key.strip(), _parse_scalar(raw_value))

    if len(stack) != 1:
        raise ValueError(f"{path}: unclosed block(s) in model_config.readable")
    return root


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_opt_params(params: Any) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for item in _as_list(params):
        if not isinstance(item, dict):
            continue
        key = item.get("key")
        val = item.get("value")
        if isinstance(key, str):
            out[key] = val
    return dict(sorted(out.items()))


def _normalize_optimizer(optimizer: dict[str, Any]) -> dict[str, Any]:
    return {
        "dim": optimizer.get("dim"),
        "optimizer": optimizer.get("optimizer"),
        "opt_params": _normalize_opt_params(optimizer.get("opt_params")),
    }


def _normalize_slot_block(block: dict[str, Any]) -> dict[str, Any]:
    slots = [int(v) for v in _as_list(block.get("slots"))]
    optimizers = [_normalize_optimizer(it) for it in _as_list(block.get("optimizers")) if isinstance(it, dict)]
    return {
        "slots": slots,
        "dim": block.get("dim"),
        "optimizer_num_used_on_creation": block.get("optimizer_num_used_on_creation"),
        "optimizers": optimizers,
    }


def _normalize_dnn_slice(block: dict[str, Any]) -> dict[str, Any]:
    optimizer_raw = block.get("optimizer")
    optimizer = _normalize_optimizer(optimizer_raw) if isinstance(optimizer_raw, dict) else None
    return {
        "slice_id": block.get("slice_id"),
        "shard_id": block.get("shard_id"),
        "optimizer": optimizer,
    }


def _slot_signature(block: dict[str, Any]) -> tuple[int, ...]:
    return tuple(sorted(int(v) for v in block["slots"]))


def _slot_map(blocks: list[dict[str, Any]]) -> dict[int, list[int]]:
    out: dict[int, list[int]] = {}
    for block in blocks:
        slots = [int(v) for v in block["slots"]]
        for slot in slots:
            out.setdefault(slot, []).extend(s for s in slots if s != slot)
    for slot, peers in out.items():
        out[slot] = sorted(set(peers))
    return dict(sorted(out.items()))


def _group_diff(current: dict[str, Any], checkpoint: dict[str, Any]) -> dict[str, Any]:
    if current == checkpoint:
        return {}
    diff: dict[str, Any] = {}
    for key in sorted(set(current) | set(checkpoint)):
        if current.get(key) != checkpoint.get(key):
            diff[key] = {
                "current": current.get(key),
                "checkpoint": checkpoint.get(key),
            }
    return diff


def compare_model_config(current_path: str, checkpoint_path: str) -> dict[str, Any]:
    current_root = parse_textproto(current_path)
    checkpoint_root = parse_textproto(checkpoint_path)

    current_slot_blocks = [_normalize_slot_block(b) for b in _as_list(current_root.get("slots")) if isinstance(b, dict)]
    checkpoint_slot_blocks = [_normalize_slot_block(b) for b in _as_list(checkpoint_root.get("slots")) if isinstance(b, dict)]
    current_dnn_slices = [_normalize_dnn_slice(b) for b in _as_list(current_root.get("dnn_slices")) if isinstance(b, dict)]
    checkpoint_dnn_slices = [_normalize_dnn_slice(b) for b in _as_list(checkpoint_root.get("dnn_slices")) if isinstance(b, dict)]

    current_slot_block_map = {_slot_signature(block): block for block in current_slot_blocks}
    checkpoint_slot_block_map = {_slot_signature(block): block for block in checkpoint_slot_blocks}
    shared_slot_sigs = sorted(set(current_slot_block_map) & set(checkpoint_slot_block_map))

    current_slot_ids = sorted({slot for block in current_slot_blocks for slot in block["slots"]})
    checkpoint_slot_ids = sorted({slot for block in checkpoint_slot_blocks for slot in block["slots"]})

    current_dnn_map = {
        int(block["slice_id"]): block
        for block in current_dnn_slices
        if isinstance(block.get("slice_id"), int)
    }
    checkpoint_dnn_map = {
        int(block["slice_id"]): block
        for block in checkpoint_dnn_slices
        if isinstance(block.get("slice_id"), int)
    }
    shared_slice_ids = sorted(set(current_dnn_map) & set(checkpoint_dnn_map))

    shared_slot_blocks: list[dict[str, Any]] = []
    mismatched_shared_slot_blocks: list[dict[str, Any]] = []
    for sig in shared_slot_sigs:
        current_block = current_slot_block_map[sig]
        checkpoint_block = checkpoint_slot_block_map[sig]
        item = {
            "slots": list(sig),
            "same_structure": current_block == checkpoint_block,
            "differences": _group_diff(current_block, checkpoint_block),
        }
        shared_slot_blocks.append(item)
        if not item["same_structure"]:
            mismatched_shared_slot_blocks.append(item)

    shared_dnn_slices: list[dict[str, Any]] = []
    mismatched_shared_dnn_slices: list[dict[str, Any]] = []
    for slice_id in shared_slice_ids:
        current_slice = current_dnn_map[slice_id]
        checkpoint_slice = checkpoint_dnn_map[slice_id]
        item = {
            "slice_id": slice_id,
            "same_structure": current_slice == checkpoint_slice,
            "differences": _group_diff(current_slice, checkpoint_slice),
        }
        shared_dnn_slices.append(item)
        if not item["same_structure"]:
            mismatched_shared_dnn_slices.append(item)

    current_only_slot_ids = sorted(set(current_slot_ids) - set(checkpoint_slot_ids))
    checkpoint_only_slot_ids = sorted(set(checkpoint_slot_ids) - set(current_slot_ids))
    current_only_slice_ids = sorted(set(current_dnn_map) - set(checkpoint_dnn_map))
    checkpoint_only_slice_ids = sorted(set(checkpoint_dnn_map) - set(current_dnn_map))

    return {
        "current_file": str(Path(current_path)),
        "checkpoint_file": str(Path(checkpoint_path)),
        "slot_groups": {
            "current_slot_ids": current_slot_ids,
            "checkpoint_slot_ids": checkpoint_slot_ids,
            "current_only_slot_ids": current_only_slot_ids,
            "checkpoint_only_slot_ids": checkpoint_only_slot_ids,
            "current_slot_peer_map": _slot_map(current_slot_blocks),
            "checkpoint_slot_peer_map": _slot_map(checkpoint_slot_blocks),
            "current_only_blocks": [
                current_slot_block_map[sig] for sig in sorted(set(current_slot_block_map) - set(checkpoint_slot_block_map))
            ],
            "checkpoint_only_blocks": [
                checkpoint_slot_block_map[sig]
                for sig in sorted(set(checkpoint_slot_block_map) - set(current_slot_block_map))
            ],
            "shared_blocks": shared_slot_blocks,
            "mismatched_shared_blocks": mismatched_shared_slot_blocks,
        },
        "dnn_slices": {
            "current_slice_ids": sorted(current_dnn_map),
            "checkpoint_slice_ids": sorted(checkpoint_dnn_map),
            "current_only_slice_ids": current_only_slice_ids,
            "checkpoint_only_slice_ids": checkpoint_only_slice_ids,
            "shared_slices": shared_dnn_slices,
            "mismatched_shared_slices": mismatched_shared_dnn_slices,
        },
        "summary": {
            "current_slot_count": len(current_slot_ids),
            "checkpoint_slot_count": len(checkpoint_slot_ids),
            "current_only_slot_count": len(current_only_slot_ids),
            "checkpoint_only_slot_count": len(checkpoint_only_slot_ids),
            "mismatched_shared_slot_block_count": len(mismatched_shared_slot_blocks),
            "current_dnn_slice_count": len(current_dnn_map),
            "checkpoint_dnn_slice_count": len(checkpoint_dnn_map),
            "current_only_dnn_slice_count": len(current_only_slice_ids),
            "checkpoint_only_dnn_slice_count": len(checkpoint_only_slice_ids),
            "mismatched_shared_dnn_slice_count": len(mismatched_shared_dnn_slices),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare current-job and checkpoint-source model_config.readable files"
    )
    parser.add_argument("--current", required=True, help="path to current job compile model_config.readable")
    parser.add_argument("--checkpoint", required=True, help="path to checkpoint-source model_config.readable")
    parser.add_argument("--output", default="", help="optional output JSON path")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = compare_model_config(args.current, args.checkpoint)
    except (OSError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    text = json.dumps(result, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
            f.write("\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
