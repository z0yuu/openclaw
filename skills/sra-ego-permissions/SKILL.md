---
name: sra-ego-permissions
description: >
  Fetches a user's personal permissions, resources, and configuration on Ego platform (Ego 平台): tenants (租户), projects (项目), quota, train official images (训练镜像). All API calls go through scripts; no MCP.
  TRIGGER when: user asks for Ego permissions, Ego resources, Ego config, tenant/project list, quota by project, train official images, or "Ego 权限"/"Ego 资源配置"/"租户"/"项目配额".
  DO NOT TRIGGER when: general ML platform or training questions unrelated to Ego portal permissions or resource lookup.
category: platform
tags: [ego, user, permission]
---

# Ego User Permissions and Resources (Ego 用户权限与资源配置)

Fetches the current user's permissions, resources, and configuration on **Ego platform (Ego 平台)** — tenants (租户), projects (项目), quota, and train official images (训练镜像). All API calls are done via Python scripts under `scripts/`; no MCP.

## Prerequisites

- Environment variable **USER_ID_OPENAPI** (Ego access token / EGO 访问令牌) must be set.

## Execution Flow

### 1. Gather user input

**Always ask the user** and **strongly suggest** they specify zone, tenant, and/or project to narrow scope and speed up fetching.

- **zone** (optional): Default fetches **my**, **sg** and **us** (3 zones). When customizing, **only one** is allowed: `my` (offline-sg12), `sg` (sg9-a), `us` (us1).
- **tenant** (optional): One or more (tenant_id or tenant_name). If not specified, use all tenants from portal config; otherwise filter `tenants` to the selected list.
- **project** (optional): One or more (project_id or project_name). If not specified, use all projects from portal config; otherwise filter each tenant's `projects` to the selected list.

### 2. Fetch portal config and filter

- Request: `GET {BASE_URL}/api/ego/portal/config`, Header: `Cookie: userID={USER_ID_OPENAPI}`.
- Filter the JSON: keep only `train_job_types` (from portal field `offline_training_job_type`), `tenants`, `user_info`; remove all `auth_type` inside **tenants**.
- **user_info**: keep only `user_id`, `email`.
- **gpu_packages**: not from portal; use a fixed value per card/zone (A30: sg9-a, offline-sg12; A100, L40S: us1); CPU/memory in GPU packages are not counted toward exclusive/shared quota.
- If user selected tenants: keep only matching tenants in `tenants` (by tenant_id or tenant_name).
- If user selected projects: keep only matching projects under each tenant's `projects` (by project_id or project_name).

### 3. Fetch Ego–Soc project ID mapping

- Request: `GET {BASE_URL}/api/ego/portal/project_info/mapping`, Header: `Cookie: userID={USER_ID_OPENAPI}`.
- Filter response: keep only `tenant` (ego_tenant_id/name, soc_tenant_id) and `project` (ego_project_id/name, soc_project_id). Used to map Ego project to Soc project id for quota lookup.

### 4. Fetch SOC quota and normalize

- For each project from step 2, get `soc_project_id` from step 3 mapping.
- Request: `GET https://soc.shopee.io/api/quota/v2/projects/{soc_project_id}/quota?resourceType=offline` (no zone param). Headers: `Authorization: Bearer {user_info.user_id}`, `additional-user-identity: {user_info.email}` (from step 2 `user_info`). SOC may throttle; **retry after a few seconds**, **max 3 retries** per project.
- Normalize and **filter by user-selected zone or default zones** (drop unselected zones):
  - Keep only `projectName`; rename `quotaItems` to `exclusiveQuotaItems`; include `sharedQuotaItems` if present.
  - In both (exclusiveQuotaItems, sharedQuotaItems) keep `zone`; rename `cCpu` → `cpu` (unit/quota/request/remain), `cMemory` → `memory`; for GPU array elements add key `productModel.shortName` with (unit/quota/request/remain).
  - If for any resource `request > quota`, set `request = quota`, `remain = 0`.

### 5. Fetch train framework versions (images) — only when a single zone is selected

- **When** the user selected exactly one zone: request `GET {BASE_URL}/api/ego/portal/framework_versions`, Header: `Cookie: userID={USER_ID_OPENAPI}`.
- Take only the `framework_versions` array; **each item keep only `name`, `image`**; output under key **train_official_images**.
- **When** multiple zones (or default): do not request; do **not** include **train_official_images** in the output.

### 6. Output

Merge and output (JSON or script stdout) in this order: **user_info** → **train_official_images** (if single zone) → **train_job_types** → **tenants** → **gpu_packages**.

- **user_info**
- **train_official_images** (only when a single zone is selected; omitted when multiple zones)
- **train_job_types**
- **tenants** (each tenant → projects; merge step 4 quota by `projectName` into the corresponding project)
- **gpu_packages**: Fixed per-card, per-zone cpu/memory (A30, A100, L40S); CPU/memory in GPU packages are not counted toward exclusive/shared quota.

## Conventions

- All requests go through `scripts/get_ego_user_info.py`; no MCP.
- **EGO_BASE_URL** (portal URL): Set via env `EGO_BASE_URL` if needed. Default: **SG** `https://ego-portal.mlp.shopee.io`. When user selects zone: **us1 → US** `https://ego-portal.mlp.us.shopee.io`, **my/sg → SG**.

## Script usage

Run from the **skill root** (the directory containing `scripts/`):

```bash
export USER_ID_OPENAPI="your-ego-token"

# Full (no zone/project filter)
python scripts/get_ego_user_info.py

# With tenant and/or project (repeatable)
python scripts/get_ego_user_info.py --tenant "tenant-a" --project "proj-a" --project "proj-b"

# Single zone (only one when custom; first wins if multiple)
python scripts/get_ego_user_info.py --zone my

# Output to file
python scripts/get_ego_user_info.py --out result.json
```

Options: `--base-url`, `--zone`, `--tenant`, `--project`, `--out`. See [scripts/README.md](scripts/README.md).

## Python 版本

- 此 skill 的 Python 脚本最低按 **Python 3.10+** 使用。
- 依据：PEP 585 built-in generics without postponed annotations；PEP 604 union syntax (X | Y)。
- 若系统默认 `python3` 低于该版本，请先切到对应版本后再执行，避免语法错误或直接运行失败。
