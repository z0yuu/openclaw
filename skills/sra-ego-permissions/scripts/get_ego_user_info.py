#!/usr/bin/env python3
"""
Fetch Ego user permissions, resources, and config: tenants/projects, portal config,
project_info_mapping, SOC quota, framework_versions. Merge and output JSON.

Prerequisite: env USER_ID_OPENAPI (Ego access token) set.

Usage:
  python get_ego_user_info.py [--base-url URL] [--zone my|sg|us] [--tenant ID_OR_NAME ...] [--project ID_OR_NAME ...] [--out FILE]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from urllib.parse import urlencode

import httpx

SOC_QUOTA_RETRY_MAX = 3
SOC_QUOTA_RETRY_DELAY_SEC = 4

# EGO_BASE_URL: SG default; when user selects zone, us1 → US, others → SG
BASE_URL_SG = "https://ego-portal.mlp.shopee.io"
BASE_URL_US = "https://ego-portal.mlp.us.shopee.io"
DEFAULT_BASE_URL = BASE_URL_SG
SOC_BASE_URL = "https://soc.shopee.io"
ZONE_MAP = {"my": "offline-sg12", "sg": "sg9-a", "us": "us1"}

# Fixed gpu_packages (not from portal config): per-card, per-zone cpu/memory
DEFAULT_GPU_PACKAGES = {
    "A30": [
        {"zone": "sg9-a", "cpu": 68, "memory": 497},
        {"zone": "offline-sg12", "cpu": 30, "memory": 248},
    ],
    "A100": [
        {"zone": "us1", "cpu": 15, "memory": 250},
    ],
    "L40S": [
        {"zone": "us1", "cpu": 23, "memory": 250},
    ],
}


def remove_auth_type(obj):
    """Recursively remove 'auth_type' keys from dict/list."""
    if isinstance(obj, dict):
        return {k: remove_auth_type(v) for k, v in obj.items() if k != "auth_type"}
    if isinstance(obj, list):
        return [remove_auth_type(x) for x in obj]
    return obj


def filter_tenants(tenants, selected_tenants):
    """Keep only tenants whose id or name is in selected_tenants (case-insensitive match)."""
    if not selected_tenants:
        return tenants
    selected = {s.strip().lower() for s in selected_tenants if s}
    if not selected:
        return tenants
    return [
        t
        for t in tenants
        if (t.get("tenant_id") or "").strip().lower() in selected
        or (t.get("tenant_name") or "").strip().lower() in selected
    ]


def filter_tenant_projects(tenants, selected_projects):
    """Keep only projects whose id or name is in selected_projects (case-insensitive match)."""
    if not selected_projects:
        return tenants
    selected = {p.strip().lower() for p in selected_projects if p}
    if not selected:
        return tenants
    out = []
    for t in tenants:
        projs = t.get("projects") or []
        kept = [
            p
            for p in projs
            if (p.get("project_id") or "").strip().lower() in selected
            or (p.get("project_name") or "").strip().lower() in selected
        ]
        out.append({**t, "projects": kept})
    return out


def fetch_portal_config(base_url: str, cookie: str) -> dict:
    """GET portal config; strip auth_type only from tenants; return data subset."""
    url = f"{base_url.rstrip('/')}/api/ego/portal/config"
    r = httpx.get(url, headers={"Cookie": f"userID={cookie}"}, timeout=30.0)
    r.raise_for_status()
    raw = r.json()
    data = raw.get("data") or {}
    tenants = data.get("tenants")
    if tenants is not None:
        tenants = remove_auth_type(tenants)
    return {
        "train_job_types": data.get("offline_training_job_type"),
        "tenants": tenants,
        "user_info": data.get("user_info"),
    }


def fetch_project_mapping(base_url: str, cookie: str) -> dict:
    """GET project_info/mapping: Ego <-> Soc tenant/project IDs."""
    url = f"{base_url.rstrip('/')}/api/ego/portal/project_info/mapping"
    r = httpx.get(url, headers={"Cookie": f"userID={cookie}"}, timeout=30.0)
    r.raise_for_status()
    raw = r.json()
    data = raw.get("data") or raw
    return {
        "tenant": data.get("tenant") or data.get("tenants") or [],
        "project": data.get("project") or data.get("projects") or [],
    }


def _sub_quota(obj: dict) -> dict:
    """Extract only unit/quota/request/remain from a dict."""
    if not isinstance(obj, dict):
        return {}
    return {k: obj.get(k) for k in ("unit", "quota", "request", "remain") if k in obj}


def _norm_quota_item(item: dict) -> dict:
    """Extract zone, cpu (cCpu), memory (cMemory); GPU array: each element key=productModel.shortName, value=unit/quota/request/remain."""
    out = {}
    if not isinstance(item, dict):
        return out
    zone = (item.get("zone") or item.get("zoneId") or item.get("zone_id") or "").strip()
    if zone:
        out["zone"] = zone
    # cCpu -> cpu (unit/quota/request/remain)
    ccpu = item.get("cCpu")
    if isinstance(ccpu, dict):
        out["cpu"] = _sub_quota(ccpu)
    elif ccpu is not None:
        out["cpu"] = ccpu
    # cMemory -> memory (unit/quota/request/remain)
    cmem = item.get("cMemory")
    if isinstance(cmem, dict):
        out["memory"] = _sub_quota(cmem)
    elif cmem is not None:
        out["memory"] = cmem
    # GPU: array of elements -> dict keyed by productModel.shortName, value = (unit/quota/request/remain)
    gpu_arr = item.get("gpu") or item.get("gpuList") or item.get("gpus")
    if isinstance(gpu_arr, list):
        gpu_out = {}
        for el in gpu_arr:
            if not isinstance(el, dict):
                continue
            pm = el.get("productModel") or el.get("product_model")
            short = "gpu"
            if isinstance(pm, dict):
                short = (pm.get("shortName") or pm.get("short_name") or "gpu").strip() or "gpu"
            gpu_out[short] = _sub_quota(el)
        if gpu_out:
            out["gpu"] = gpu_out
    # Single GPU object (productModel on item)
    else:
        pm = item.get("productModel") or item.get("product_model")
        if isinstance(pm, dict):
            short = pm.get("shortName") or pm.get("short_name") or "gpu"
            gpu_val = _sub_quota(item) or _sub_quota(pm)
            if gpu_val:
                out[short] = gpu_val
    return out


def _cap_request_remain(item: dict) -> dict:
    """If request > quota, set request=quota and remain=0 for numeric fields. Handles nested dicts (e.g. gpu)."""
    for k, v in list(item.items()):
        if not isinstance(v, dict):
            continue
        # Nested dict of resources (e.g. gpu: { "A100": {quota, request, remain} })
        if "quota" not in v and "request" not in v:
            item[k] = {k2: _cap_one_resource(v2) if isinstance(v2, dict) else v2 for k2, v2 in v.items()}
            continue
        item[k] = _cap_one_resource(v)
    return item


def _cap_one_resource(v: dict) -> dict:
    """Cap request/remain for a single resource dict."""
    q, rq = v.get("quota"), v.get("request")
    if isinstance(q, (int, float)) and isinstance(rq, (int, float)) and rq > q:
        return {**v, "request": q, "remain": 0}
    return v


def _filter_quota_by_zones(quota_data: dict, allowed_zones: list[str]) -> dict:
    """Filter quota response to only keep zones in allowed_zones (offline-sg12, sg9-a, us1)."""
    if not allowed_zones:
        return quota_data
    allowed = set(allowed_zones)
    out = dict(quota_data)
    # If top-level keys are zone names, keep only allowed
    for key in ("exclusiveQuotaItems", "sharedQuotaItems", "quotaItems"):
        items = out.get(key)
        if not isinstance(items, list):
            continue
        filtered = []
        for it in items:
            if not isinstance(it, dict):
                filtered.append(it)
                continue
            zone = (it.get("zone") or it.get("zoneId") or it.get("zone_id") or "").strip()
            if zone in allowed or not zone:
                filtered.append(it)
        out[key] = filtered
    # If data is keyed by zone (e.g. {"offline-sg12": {...}, "sg9-a": {...}})
    for z in list(out.keys()):
        if z in ("projectName", "project_name", "exclusiveQuotaItems", "sharedQuotaItems", "quotaItems"):
            continue
        if z not in allowed and isinstance(out.get(z), (dict, list)):
            out.pop(z, None)
    return out


def transform_soc_quota_response(data: dict, allowed_zones: list[str] | None = None) -> dict:
    """Keep projectName; quotaItems -> exclusiveQuotaItems; sharedQuotaItems if present; normalize; cap request/remain; filter by zone."""
    out = {"projectName": data.get("projectName") or data.get("project_name")}
    # quotaItems -> exclusiveQuotaItems
    items = data.get("quotaItems") or data.get("quota_items") or []
    if isinstance(items, dict):
        items = list(items.values()) if items else []
    exclusive = [_norm_quota_item(x) for x in items]
    exclusive = [_cap_request_remain(x) for x in exclusive]
    out["exclusiveQuotaItems"] = exclusive
    # sharedQuotaItems: only if API returned it; same request/quota cap as exclusive
    shared = data.get("sharedQuotaItems") or data.get("shared_quota_items") or data.get("sharedQuota")
    if shared is not None:
        if isinstance(shared, dict):
            shared = list(shared.values()) if shared else []
        shared = [_norm_quota_item(x) for x in shared]
        out["sharedQuotaItems"] = [_cap_request_remain(x) for x in shared]
    if allowed_zones:
        out = _filter_quota_by_zones(out, allowed_zones)
    return out


def fetch_soc_quota(
    soc_project_id: str,
    user_id: str,
    user_email: str,
    zones: list[str] | None,
) -> dict | None:
    """GET SOC quota for project (no zone param); filter by zones. Retry up to 3 times with delay on QPS/errors."""
    params = {"resourceType": "offline"}
    url = f"{SOC_BASE_URL}/api/quota/v2/projects/{soc_project_id}/quota?{urlencode(params)}"
    headers = {
        "Authorization": f"Bearer {user_id}",
        "additional-user-identity": user_email or "",
    }
    last_err = None
    for attempt in range(SOC_QUOTA_RETRY_MAX):
        try:
            r = httpx.get(url, headers=headers, timeout=30.0)
            r.raise_for_status()
            resp = r.json()
            raw = resp.get("data")
            # SOC API returns data as array of quota records; take first for this project
            if isinstance(raw, list) and len(raw) > 0:
                data = raw[0]
            elif isinstance(raw, dict):
                data = raw
            else:
                data = {}
            return transform_soc_quota_response(data, allowed_zones=zones)
        except Exception as e:
            last_err = e
            if attempt < SOC_QUOTA_RETRY_MAX - 1:
                time.sleep(SOC_QUOTA_RETRY_DELAY_SEC)
    sys.stderr.write(f"Warning: SOC quota for project {soc_project_id} failed after {SOC_QUOTA_RETRY_MAX} attempts: {last_err}\n")
    return None


def fetch_framework_versions(base_url: str, cookie: str) -> list:
    """GET framework_versions, return list (for key train_official_images)."""
    url = f"{base_url.rstrip('/')}/api/ego/portal/framework_versions"
    r = httpx.get(url, headers={"Cookie": f"userID={cookie}"}, timeout=30.0)
    r.raise_for_status()
    raw = r.json()
    data = raw.get("data") or raw
    return data.get("framework_versions") or []


def build_ego_to_soc_project(mapping: dict) -> dict:
    """Map ego_project_id -> soc_project_id and ego project_name -> soc_project_id."""
    by_id = {}
    by_name = {}
    for p in mapping.get("project") or []:
        ego_id = (p.get("ego_project_id") or p.get("EgoProjectID") or "").strip()
        ego_name = (p.get("ego_project_name") or p.get("EgoProjectName") or "").strip()
        soc_id = (p.get("soc_project_id") or p.get("SocProjectID") or "").strip()
        if soc_id:
            if ego_id:
                by_id[ego_id] = soc_id
            if ego_name:
                by_name[ego_name.strip().lower()] = soc_id
    return {"by_id": by_id, "by_name": by_name}


def merge_quota_into_tenants(tenants: list, quota_by_project_name: dict) -> list:
    """Add quota (by projectName) into each project in tenants."""
    out = []
    for t in tenants:
        projs = []
        for p in t.get("projects") or []:
            name = (p.get("project_name") or p.get("project_id") or "").strip()
            key = name.lower() if name else name
            quota = quota_by_project_name.get(key) or quota_by_project_name.get(name)
            projs.append({**p, "quota": quota})
        out.append({**t, "projects": projs})
    return out


def main():
    parser = argparse.ArgumentParser(description="Fetch Ego user permissions and config")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Ego portal base URL")
    parser.add_argument("--zone", action="append", dest="zones", help="Zone: my, sg, us (repeatable)")
    parser.add_argument("--tenant", action="append", dest="tenants", help="Tenant id or name to filter (repeatable)")
    parser.add_argument("--project", action="append", dest="projects", help="Project id or name to filter (repeatable)")
    parser.add_argument("--out", dest="out_file", help="Write JSON to file")
    parser.add_argument("--verbose", action="store_true", help="Print progress")
    args = parser.parse_args()

    token = os.environ.get("USER_ID_OPENAPI", "").strip()
    if not token:
        sys.stderr.write("Error: USER_ID_OPENAPI not set\n")
        sys.exit(1)

    # EGO_BASE_URL overrides; else --base-url; when default SG and zone us → US
    base = os.environ.get("EGO_BASE_URL", "").strip()
    if base:
        base = base.rstrip("/")
    else:
        base = args.base_url.rstrip("/")
        if base == BASE_URL_SG and args.zones:
            if "us" in [z.strip().lower() for z in args.zones]:
                base = BASE_URL_US

    # Default zones: my, sg, us (3 zones); when custom (--zone passed), only one zone allowed
    zones_raw = [z.strip().lower() for z in (args.zones or []) if z.strip()]
    if not zones_raw:
        zones_soc = [ZONE_MAP["my"], ZONE_MAP["sg"], ZONE_MAP["us"]]
    else:
        valid = [ZONE_MAP[z] for z in zones_raw if z in ZONE_MAP]
        zones_soc = [valid[0]] if valid else [ZONE_MAP["my"], ZONE_MAP["sg"], ZONE_MAP["us"]]

    if args.verbose:
        print("Step 1: Fetch portal config...", file=sys.stderr)
    config = fetch_portal_config(base, token)
    tenants = config.get("tenants") or []
    if args.tenants:
        tenants = filter_tenants(tenants, args.tenants)
    if args.projects:
        tenants = filter_tenant_projects(tenants, args.projects)
    config["tenants"] = tenants

    if args.verbose:
        print("Step 2: Fetch project_info/mapping...", file=sys.stderr)
    mapping = fetch_project_mapping(base, token)
    ego2soc = build_ego_to_soc_project(mapping)

    user_info = config.get("user_info") or {}
    user_id = user_info.get("user_id") or user_info.get("userId") or ""
    user_email = user_info.get("email") or user_info.get("Email") or ""

    quota_by_project_name = {}
    for t in tenants:
        for p in t.get("projects") or []:
            ego_id = (p.get("project_id") or "").strip()
            ego_name = (p.get("project_name") or "").strip()
            soc_id = ego2soc["by_id"].get(ego_id) or ego2soc["by_name"].get(ego_name.lower()) if ego_name else None
            if not soc_id:
                continue
            if args.verbose:
                print(f"  Quota for project {ego_name or ego_id} (soc={soc_id})...", file=sys.stderr)
            quota = fetch_soc_quota(soc_id, user_id, user_email, zones_soc if zones_soc else None)
            if quota:
                pname = quota.get("projectName") or ego_name or ego_id
                for k in (pname, (pname or "").lower(), ego_name, (ego_name or "").lower(), ego_id, (ego_id or "").lower()):
                    if k is not None and k != "":
                        quota_by_project_name[k] = quota

    single_zone = len(zones_soc) == 1
    train_official_images = []
    if single_zone:
        if args.verbose:
            print("Step 3: Fetch framework_versions...", file=sys.stderr)
        train_official_images = fetch_framework_versions(base, token)

    tenants_merged = merge_quota_into_tenants(tenants, quota_by_project_name)

    # user_info: only user_id, email
    ui = config.get("user_info") or {}
    user_info_out = {
        "user_id": ui.get("user_id") or ui.get("userId") or "",
        "email": ui.get("email") or ui.get("Email") or "",
    }
    # train_official_images: only when a single zone is selected; omit when multiple zones
    train_official_images_out = [
        {"name": x.get("name", ""), "image": x.get("image", "")}
        for x in (train_official_images or [])
        if isinstance(x, dict)
    ] if single_zone else []
    # gpu_packages: fixed value (not from portal config)
    gpu_packages_out = DEFAULT_GPU_PACKAGES

    result = {
        "user_info": user_info_out,
        "train_job_types": config.get("train_job_types"),
        "tenants": tenants_merged,
        "gpu_packages": gpu_packages_out,
    }
    if single_zone:
        result = {
            "user_info": user_info_out,
            "train_official_images": train_official_images_out,
            "train_job_types": config.get("train_job_types"),
            "tenants": tenants_merged,
            "gpu_packages": gpu_packages_out,
        }

    out_json = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out_file:
        with open(args.out_file, "w", encoding="utf-8") as f:
            f.write(out_json)
        if args.verbose:
            print(f"Wrote {args.out_file}", file=sys.stderr)
    else:
        print(out_json)


if __name__ == "__main__":
    main()
