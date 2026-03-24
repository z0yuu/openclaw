# Model API

Model related APIs: list and detail.

**Status codes**: category=**12**, success `9912100`; failure `9912`+ error code (e.g. 9912101 unauthorized, 9912102 forbidden, 9912103 not found, 9912107 bad request, 9912108 required parameter missing).

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

- [1. Get Model List](#1-get-model-list)
- [2. Get Model Detail](#2-get-model-detail)

---

## 1. Get Model List

- **Path**: `GET /api/ego/portal/models`
- **Description**: Paginated query. Supports scope, orderBy/order, model_id, model_name, project, create_time_start/end, creator.

### Request Parameters

| Parameter         | Type   | Required | Description                                  |
| ----------------- | ------ | -------- | -------------------------------------------- |
| current           | int64  | Yes      | Page number ≥1                               |
| pageSize          | int64  | Yes      | Page size ≥1                                 |
| orderBy           | string | No       | model_id, model_name, create_time, creator   |
| order             | string | No       | ascend / descend                             |
| scope             | int64  | No       | 1-all (within permitted projects) 2-personal |
| model_id          | int64  | No       | Model ID                                     |
| model_name        | string | No       | Model name (fuzzy)                           |
| project           | string | No       | Project name or project ID                   |
| create_time_start | int64  | No       | Create time start (seconds)                  |
| create_time_end   | int64  | No       | Create time end (seconds)                    |
| creator           | string | No       | Creator email                                |

### Response

- Success: `data.data` is the model list, `data.info` contains current, pageSize, total. Model object: model_id, model_name, description, tenant_id, project_id, creator, is_private, auth_users, create_time, can_edit, can_delete, can_move.

### Example

```bash
curl -X GET "$BASE_URL/api/ego/portal/models?current=1&pageSize=10&orderBy=model_id&order=descend&scope=1" \
  -H "Cookie: userID=$USER_ID_OPENAPI" -H "Content-Type: application/json"
```

---

## 2. Get Model Detail

- **Path**: `GET /api/ego/portal/model/{model_id}`
- **Description**: Returns the specified model detail.

### Request Parameters

| Parameter | Type  | Required | Description |
| --------- | ----- | -------- | ----------- |
| model_id  | int64 | Yes      | Path        |

### Response

- Success: `data.model_info` includes model_id, model_name, description, tenant_name, tenant_id, project_name, project_id, creator, create_time (second-level timestamp).

### Example

```bash
curl -X GET "$BASE_URL/api/ego/portal/model/1" \
  -H "Cookie: userID=$USER_ID_OPENAPI" -H "Content-Type: application/json"
```
