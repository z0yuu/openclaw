# Checkpoint API

Checkpoint list APIs.

**Status codes**: category=**16**, success `9916100`; failure `9916`+ error code (e.g. 9916101 unauthorized, 9916103 not found, 9916107 bad request).

---

## Environment and Authentication

### Environment

| Environment | Domain                                | Notes                          |
| ----------- | ------------------------------------- | ------------------------------ |
| **SG**      | `https://ego-portal.mlp.shopee.io`    | Singapore environment, default |
| **US**      | `https://ego-portal.mlp.us.shopee.io` | United States environment      |

All API paths use the prefix `/api/ego/portal`. The scripts in this skill use environment variable `EGO_BASE_URL` to select the base URL. If it is unset, the default is SG. In curl examples, replace `$BASE_URL` with the domain above or with your `EGO_BASE_URL`.

### Authentication

- Method: Cookie `userID` = access token
- Token source: environment variable `USER_ID_OPENAPI` must be set before calling the scripts
- curl examples:
  - `-H "Cookie: userID=$USER_ID_OPENAPI"`
  - `-b "userID=$USER_ID_OPENAPI"`

---

## 1. Get Checkpoint List

- **Path**: `GET /api/ego/portal/model/{model_id}/version/{version_id}/checkpoints`
- **Description**: Paginated query of Checkpoints under a given model version. Supports job_id, checkpoint_id, checkpoint_name, only_mine, verbose (returns checkpoint_path, related_job_s3_path).

### Request Parameters

| Parameter       | Type   | Required | Description                                                                                            |
| --------------- | ------ | -------- | ------------------------------------------------------------------------------------------------------ |
| model_id        | int64  | Yes      | Path                                                                                                   |
| version_id      | int64  | Yes      | Path (when 0 is passed, first result's model_version_id may be used for reverse lookup)                |
| current         | int64  | No       | Page number, default 1                                                                                 |
| pageSize        | int64  | No       | Page size, default 10                                                                                  |
| order           | string | No       | ascend / descend, default descend                                                                      |
| orderBy         | string | No       | checkpoint_id, size, feature_num, mf_feature_num, related_job_name, create_time, default checkpoint_id |
| job_id          | int64  | No       | Filter by associated job ID                                                                            |
| checkpoint_id   | int64  | No       | Filter by Checkpoint ID                                                                                |
| checkpoint_name | string | No       | Filter by name                                                                                         |
| only_mine       | bool   | No       | Only Checkpoints created by current user                                                               |
| verbose         | bool   | No       | Return checkpoint_path, related_job_s3_path                                                            |

### Response

- Success: `data.data` is the Checkpoint list, `data.info` contains current, pageSize, total. Each item includes checkpoint_id, checkpoint_name, checkpoint_path (when verbose), related_job_id, related_job_name, related_job_s3_path (when verbose), feature_num, mf_feature_num, size, checkpoint_type, create_time, can_release, can_delete, can_evaluate, trash_status, delete_time, etc.

### Example

```bash
curl -X GET "$BASE_URL/api/ego/portal/model/1/version/2/checkpoints?current=1&pageSize=10&orderBy=checkpoint_id&order=descend" \
  -H "Cookie: userID=$USER_ID_OPENAPI" -H "Content-Type: application/json"
```

---

## 2. Checkpoint Management List (list_v3)

- **Path**: `POST /api/ego/portal/checkpoint/management`
- **Description**: List API for the Checkpoint management page. Supports multiple display modes (flat list, grouped by creator, grouped by model, personal list, trash list), and returns tenant/project quota info.

### list_type Description

| list_type | Description                                                                  |
| --------- | ---------------------------------------------------------------------------- |
| 0         | Flat list of Checkpoints (pagination at checkpoint level)                    |
| 1         | Grouped by creator                                                           |
| 2         | Grouped by model                                                             |
| 3         | Personal Checkpoint list (only under model versions created by current user) |
| 4         | Checkpoints in trash (recoverable, within 24 hours)                          |

### Request Parameters

| Parameter       | Type   | Required | Description                                                    |
| --------------- | ------ | -------- | -------------------------------------------------------------- |
| tenant_id       | string | Yes      | Tenant ID                                                      |
| project_id      | string | No       | Project ID; pass "ALL" to skip project filter                  |
| list_type       | int    | Yes      | 0/1/2/3/4, see table above                                     |
| current         | int64  | No       | Page number, default 1                                         |
| pageSize        | int64  | No       | Page size, default 10, max 100                                 |
| ckpt_size_min   | int64  | No       | Checkpoint size lower bound (MB), effective when list_type=0/3 |
| ckpt_size_max   | int64  | No       | Checkpoint size upper bound (MB), effective when list_type=0/3 |
| creator         | string | No       | Creator filter (list_type=1: name fuzzy match)                 |
| model_id        | int64  | No       | Model ID (list_type=2 filter)                                  |
| model_name      | string | No       | Model name (list_type=2 filter)                                |
| checkpoint_id   | int64  | No       | Filter by Checkpoint ID                                        |
| checkpoint_name | string | No       | Checkpoint name filter (fuzzy)                                 |

### Response

- **data**: Array of `CkptManagementData`. list_type=0/3/4: flat checkpoint list; list_type=1: grouped by creator (with `children` as model/version/checkpoint hierarchy); list_type=2: grouped by model (with `children` as version/checkpoint hierarchy).
- **info**: Pagination (current, pageSize, total).
- **tenant_total / tenant_used / tenant_proportion**: Tenant total quota (MB), used (MB), usage ratio (%).
- **project_total / project_used / project_proportion**: When project_id is provided, returns project-level quota and usage.

Each `CkptManagementData` includes: checkpoint_id, checkpoint_name, checkpoint_link, creator, model_id, model_name, model_version_id, model_version_name, job_id, job_name, size (MB), related_serving, create_time (ms), can_delete; in trash flow: trash_status, delete_time; list_type=4: can_recover.

### Example

```bash
# Personal Checkpoint list (list_type=3)
curl -X POST "$BASE_URL/api/ego/portal/checkpoint/management" \
  -H "Cookie: userID=$USER_ID_OPENAPI" -H "Content-Type: application/json" \
  -d '{"tenant_id":"<tenant_id>","list_type":3,"current":1,"pageSize":10}'

# Grouped by model (list_type=2)
curl -X POST "$BASE_URL/api/ego/portal/checkpoint/management" \
  -H "Cookie: userID=$USER_ID_OPENAPI" -H "Content-Type: application/json" \
  -d '{"tenant_id":"<tenant_id>","list_type":2,"current":1,"pageSize":10}'
```

### Notes

- Only includes offline Checkpoints with status succeeded/cleared (list_type=4: trash records within 24 hours, status completed).
- When list_type=3, only returns checkpoints under model versions where the current user is the creator.
- Time fields are millisecond timestamps; size is in MB.

---

## 3. Get Single Checkpoint Detail

- **Path**: `GET /api/ego/portal/checkpoint`
- **Description**: Query a single Checkpoint by Checkpoint ID. Returns detailed info including related job, model, and model version.

### Request Parameters

| Parameter     | Type  | Required | Description           |
| ------------- | ----- | -------- | --------------------- |
| checkpoint_id | int64 | Yes      | Checkpoint ID (Query) |

### Response

- Success: `data` is a single Checkpoint detail object with checkpoint_id, checkpoint_name, checkpoint_path, related_job_id, feature_num, mf_feature_num, size (MB), create_time (millisecond timestamp), model_id, model_version_id, checkpoint_resource, checkpoint_sync_type, can_sync, job_id, sample_timestamp, etc.

### Example

```bash
curl -X GET "$BASE_URL/api/ego/portal/checkpoint?checkpoint_id=100" \
  -H "Cookie: userID=$USER_ID_OPENAPI" -H "Content-Type: application/json"
```

**Note**: The user must have view permission on the Checkpoint and its related job and model version. If the Checkpoint does not exist or access is denied, the API returns the corresponding error code (e.g. 9916103 resource not found).

---

## 4. Sample date (样本日期) from checkpoint_name

Users care which **sample date** a checkpoint corresponds to. The API may return `sample_timestamp` in the single-checkpoint detail; in addition, `checkpoint_name` often embeds the sample date as a segment between `#` delimiters.

### Patterns

Formats vary; common ones:

- `#YYYY-MM-DD/HH#` — date and hour, e.g. **2026-01-28/00** (`ckpt#...#2026-01-28/00#6104721`).
- `#YYYY-MM-DD#` — date only, e.g. **2026-03-12**.

### Parsing

- Regex to match both: `#(\d{4}-\d{2}-\d{2}(?:/\d{2})?)#` — captures `YYYY-MM-DD` or `YYYY-MM-DD/HH`.
- When returning checkpoint info to the user, always include a **sample date (样本日期)** field: use the parsed value when present, otherwise "—" or "N/A".

---

**Note**: Only Checkpoints with status succeeded/cleared are returned; time fields are millisecond timestamps.
