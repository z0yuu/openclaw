# sra-ego-permissions scripts

Fetches Ego user permissions and resource configuration via Python calls to the portal and SOC API; no MCP dependency.

## Environment

- **USER_ID_OPENAPI** (required): Ego access token (Cookie `userID`).
- **EGO_BASE_URL** (optional): Portal base URL. Default SG: `https://ego-portal.mlp.shopee.io`. When `--zone us` is used, US is used: `https://ego-portal.mlp.us.shopee.io`; other zones use SG.
- Recommended: use a venv under `scripts/` and install deps with `pip install -r requirements.txt`.

## get_ego_user_info.py

Fetches and merges: portal config, project_info/mapping, SOC quota, framework_versions; optionally filters by zone/tenant/project and outputs JSON.

### Usage

```bash
export USER_ID_OPENAPI="your-ego-token"

# Full (no zone/project filter)
python get_ego_user_info.py

# With tenant and/or project (repeatable)
python get_ego_user_info.py --tenant "tenant-a" --project "proj-a" --project "proj-b"

# Single zone: my/sg/us (only one when custom)
python get_ego_user_info.py --zone my

# Output to file
python get_ego_user_info.py --out result.json

# Portal base URL (default SG)
python get_ego_user_info.py --base-url https://ego-portal.mlp.us.shopee.io
```

### Options

| Option       | Description                                                                                        |
| ------------ | -------------------------------------------------------------------------------------------------- |
| `--base-url` | Override portal base URL (otherwise from EGO_BASE_URL / zone: default SG, US when `--zone us`)     |
| `--zone`     | Optional. Default: my, sg and us (3 zones); when set, **only one** (my/sg/us); `us` uses US portal |
| `--tenant`   | Repeatable. Keep only these tenants (tenant_id or tenant_name)                                     |
| `--project`  | Repeatable. Keep only these projects (id or name)                                                  |
| `--out`      | Output JSON file path; if omitted, print to stdout                                                 |
| `--verbose`  | Print step logs to stderr                                                                          |

### Output structure

Field order: user_info → train_official_images (if single zone) → train_job_types → tenants → gpu_packages.

- `user_info`: only `user_id`, `email`
- `train_official_images`: only when a single zone is selected; only `name`, `image`; omitted when multiple zones
- `train_job_types`: from portal config (original `offline_training_job_type`)
- `tenants`: each project's `quota` with exclusiveQuotaItems, sharedQuotaItems; each item has `zone` and cpu/memory/gpu
- `gpu_packages`: fixed value per card/zone (A30: sg9-a, offline-sg12; A100, L40S: us1); not from portal; CPU/memory in GPU packages are not counted toward exclusive/shared quota
