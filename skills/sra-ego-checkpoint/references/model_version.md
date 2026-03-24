# Model Version API

Model Version related APIs: list and detail.

**Status codes**: category=**13**, success `9913100`; failure `9913`+ error code (e.g. 9913101 unauthorized, 9913103 not found, 9913107 bad request).

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

## Table of Contents

- [1. Get Version List](#1-get-version-list)
- [2. Get Version Detail](#2-get-version-detail)

---

## 1. Get Version List

- **Path**: `GET /api/ego/portal/model/{model_id}/versions`
- **Description**: Paginated query of versions under a given model. Supports version_id, version_name, create_time_start/end, creator, orderBy/order.

### Request Parameters

| Parameter         | Type   | Required | Description                                        |
| ----------------- | ------ | -------- | -------------------------------------------------- |
| model_id          | int64  | Yes      | Path                                               |
| current           | int64  | Yes      | Page number, default 1                             |
| pageSize          | int64  | Yes      | Page size, default 10                              |
| orderBy           | string | No       | id, create_time, version_name, version_id, creator |
| order             | string | No       | ascend / descend                                   |
| version_id        | int64  | No       | Version ID                                         |
| version_name      | string | No       | Version name                                       |
| create_time_start | int64  | No       | Create time start (ms)                             |
| create_time_end   | int64  | No       | Create time end (ms)                               |
| creator           | string | No       | Creator email                                      |

### Response

- Success: `data.data` is the version list, `data.info` is pagination. Each item includes version_id, model_id, version_name, version_type (normal/baseline), entry_file_name, creator, create_time, code_file, use_git_config, can_edit, can_delete, can_checkpoint, etc.

### Example

```bash
curl -X GET "$BASE_URL/api/ego/portal/model/10/versions?current=1&pageSize=10&orderBy=id&order=descend" \
  -H "Cookie: userID=$USER_ID_OPENAPI" -H "Content-Type: application/json"
```

---

## 2. Get Version Detail

- **Path**: `GET /api/ego/portal/model/{model_id}/version/{version_id}`
- **Description**: Returns version detail, including code files, Git config, permissions and capabilities.

### Request Parameters

| Parameter  | Type  | Required | Description |
| ---------- | ----- | -------- | ----------- |
| model_id   | int64 | Yes      | Path        |
| version_id | int64 | Yes      | Path        |

### Response

- Success: data includes version_id, model_id, version_name, version_type, entry_file_name, description, use_git_config, git_config, code_file, creator, create_time, etc.

### Example

```bash
curl -X GET "$BASE_URL/api/ego/portal/model/10/version/1" \
  -H "Cookie: userID=$USER_ID_OPENAPI" -H "Content-Type: application/json"
```
