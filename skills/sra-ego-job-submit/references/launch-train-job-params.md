# 创建作业参数说明（train_job.py create）

本 skill 通过 **scripts/train_job.py** 的 **create** 子命令提交 EGO 训练作业。该子命令接收一个 **body** 参数（完整创建作业请求的 JSON 字符串），脚本解析后转发给 EGO 创建作业 API。

**文档分工**：流程、必要/可选信息、模版与覆盖规则、关键约定见 [SKILL.md](../SKILL.md)。本文档仅定义 create 的 body 参数内容（请求体字段）、默认值、`training_job_type` 枚举及常见错误与处理。

**阅读时机**：调用 **train_job.py create** 前须阅读本文档并按其中格式组装 body。

---

## 脚本子命令参数（train_job.py create）

| 参数         | 类型   | 必填 | 说明                                                               |
| ------------ | ------ | ---- | ------------------------------------------------------------------ |
| `body`       | string | 是   | 完整创建作业请求体，为下方「请求体字段」所组成对象的 JSON 字符串。 |
| `--base_url` | string | 否   | EGO API 基地址，不传则使用环境变量 EGO_BASE_URL 或默认值。         |

**调用方式**（工作目录为 skill 根目录）：`python scripts/train_job.py create '<body_json>'`。若 JSON 过长可先写入临时文件再执行：`python scripts/train_job.py create "$(cat /tmp/body.json)"`。

---

## 请求体字段（body 解析后的 JSON 对象）

以下为 **body** 解析后的 JSON 对象中可用字段，与 EGO 创建作业 API 一一对应。

### 必填字段

| 字段                 | 类型    | 说明                                                                      |
| -------------------- | ------- | ------------------------------------------------------------------------- |
| `related_model_id`   | integer | 模型 ID，必填。                                                           |
| `related_version_id` | integer | 模型版本 ID，必填。                                                       |
| `job_name`           | string  | 作业名称，必填；长度 2–50 字符，符合命名规范。                            |
| `training_job_type`  | string  | 训练作业类型枚举，必填；不传或空时默认为 `"21"`（训练启动）。见下方枚举。 |
| `job_priority`       | integer | 作业优先级，必填。                                                        |

### 基础信息

| 字段                     | 类型    | 说明                                                                                         |
| ------------------------ | ------- | -------------------------------------------------------------------------------------------- |
| `tenant_id`              | string  | 租户 ID，可选；须与流程中**模型记录**（model.py get）取得的 tenant_id 一致。                 |
| `project_id`             | string  | 项目 ID，可选；须与流程中**模型记录**（model.py get）取得的 project_id 一致。                |
| `zone`                   | string  | 区域，可选；按 **utils_api.py project_quota** 在有资源的 zone 提交，SG 默认 `offline-sg12`。 |
| `description`            | string  | 作业描述，可选。                                                                             |
| `offline_half_precision` | boolean | 离线半精度，可选。                                                                           |
| `online_half_precision`  | boolean | 在线半精度，可选。                                                                           |
| `use_new_io`             | boolean | 是否使用新 IO，可选。                                                                        |
| `skip_sandbox`           | boolean | 是否跳过沙箱，可选。                                                                         |
| `pending_over_time`      | integer | 排队超时时间，非必填；不填时默认 **300**。                                                   |
| `pending_over_time_unit` | string  | 排队超时时间单位，非必填；不填时默认 **minutes**。                                           |

### 配置文件（数组，非字符串）

通过 **scripts/utils_api.py upload** 上传本地文件后得到 USS 路径，在 body 中以 **数组** 形式传入。每项为对象，**`uss_path` 与 `file_name` 必填**。

| 字段                    | 类型  | 说明                                                          |
| ----------------------- | ----- | ------------------------------------------------------------- |
| `config_files`          | array | 配置文件列表，必填；**训练任务必传**（如 ego-learner.yaml）。 |
| `flag_file`             | array | 标志文件列表，可选。                                          |
| `data_converter`        | array | 数据转换器文件列表，可选（如 converter.py）。                 |
| `validation_config`     | array | 验证配置文件列表，可选。                                      |
| `initialization_script` | array | 初始化脚本列表，可选。                                        |

### 镜像

| 字段            | 类型   | 说明                                            |
| --------------- | ------ | ----------------------------------------------- |
| `train_image`   | string | 训练镜像，可选。                                |
| `compile_image` | string | 编译镜像，默认与train_image取值保持一致，可选。 |

### 资源配置（对象，非字符串）

WC、Worker、Sample Server 等使用 **Resource** 结构，字段：`replicas`（副本数）、`cpu`（核数）、`memory`（GB）、`gpuType`（如 `"A30"`）、`mig_gpu`（如 `"1"`）。**GPU 以 gpuType + mig_gpu 为主**，`gpu` 已废弃。在 body 中直接为 **对象**，勿再包一层 JSON 字符串。

| 字段                     | 类型    | 说明                                                                                                                                                                               |
| ------------------------ | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `is_colocate`            | boolean | 是否 Worker、Sample Server 在同一实例共存，可选。                                                                                                                                  |
| `wc_resource`            | object  | WC 资源配置，默认 `{"replicas": 1, "cpu": 8, "memory": 60}`，可选。                                                                                                                |
| `worker_resource`        | object  | Worker 资源配置；默认 `{"replicas": 8, "cpu": 10, "memory": 40}`；GPU Worker 须按 Gpu Unit 设置 `cpu`、`memory`、`gpuType`（`"A30"` 或 `"A100"`）、`mig_gpu`（默认 `"1"`），可选。 |
| `sample_server_resource` | object  | Sample Server 资源配置；默认 `{"replicas": 4, "cpu": 8, "memory": 40}`，可选。                                                                                                     |

**worker_resource 示例**：

- CPU Worker：`{"replicas": 8, "cpu": 10, "memory": 40}`
- GPU Worker（gpuType 与 mig_gpu 需同时指定）：`{"replicas": 8, "cpu": 30, "memory": 248, "gpuType": "A30", "mig_gpu": "1"}`

**默认值速查**（SKILL 无模版时以本表为准）：

| 字段 / 项              | 默认值                                     |
| ---------------------- | ------------------------------------------ |
| job_priority           | 5                                          |
| zone（SG）             | offline-sg12                               |
| pending_over_time      | 300                                        |
| pending_over_time_unit | minutes                                    |
| wc_resource            | `{"replicas": 1, "cpu": 8, "memory": 60}`  |
| worker_resource（CPU） | `{"replicas": 8, "cpu": 10, "memory": 40}` |
| sample_server_resource | `{"replicas": 4, "cpu": 8, "memory": 40}`  |
| training_job_type      | "21"（train）                              |

### Checkpoint

| 字段                         | 类型      | 说明                                 |
| ---------------------------- | --------- | ------------------------------------ |
| `checkpoint_id`              | integer   | 从选定的 checkpoint 增量训练，可选。 |
| `filter_nn`                  | boolean   | 是否过滤 NN，可选。                  |
| `load_slot_mode`             | integer   | 加载 slot 模式，可选。               |
| `slot_ids`                   | string    | slot ID 列表，可选。                 |
| `clear_nn_grads`             | boolean   | 是否清空 NN 梯度，可选。             |
| `load_grads_slot_mode`       | integer   | 加载梯度 slot 模式，可选。           |
| `grads_slot_ids`             | string    | 梯度 slot ID 列表，可选。            |
| `greedy_loading_mode`        | boolean   | 是否贪婪加载，可选。                 |
| `user_define_hdfs_path`      | string    | 用户自定义 HDFS 路径，可选。         |
| `user_define_hdfs_prefix`    | string    | 用户自定义 HDFS 前缀，可选。         |
| `user_define_filter_nn`      | boolean   | 用户自定义是否过滤 NN，可选。        |
| `user_define_load_slot_mode` | integer   | 用户自定义加载 slot 模式，可选。     |
| `user_define_slot_ids`       | string    | 用户自定义 slot ID 列表，可选。      |
| `user_define_ue_slot_ids`    | string    | 用户自定义 UE slot ID 列表，可选。   |
| `nn_checkpoint_ids`          | integer[] | NN checkpoint ID 列表，可选。        |

### 其他

| 字段                         | 类型    | 说明                                                                               |
| ---------------------------- | ------- | ---------------------------------------------------------------------------------- |
| `use_git_config`             | boolean | 是否使用 Git 配置，可选。                                                          |
| `git_path`                   | string  | Git 仓库路径，可选。                                                               |
| `branch`                     | string  | 分支名，可选。                                                                     |
| `commit_id`                  | string  | 提交 ID，可选。                                                                    |
| `username`                   | string  | Git 用户名，可选。                                                                 |
| `token`                      | string  | Git 鉴权 token，可选。                                                             |
| `git_path_prefix`            | string  | Git 路径前缀，可选。                                                               |
| `generate_validation_config` | boolean | 未传 `validation_config` 时是否拷贝 ego-learner.yaml 为 online-export.yaml，可选。 |

---

## training_job_type 枚举（常用）

| 值   | 说明                                  |
| ---- | ------------------------------------- |
| "21" | train：常规离线训练（默认）。         |
| "22" | ego-lite：EGO Lite 轻量训练。         |
| "23" | evaluation：评估（模型/Checkpoint）。 |
| "24" | feature evaluation：特征评估。        |
| "25" | online evaluation：在线评估。         |
| "26" | tensor evaluation：Tensor 评估。      |

---

## 使用注意

- **流程与关键约定**（tenant_id/project_id 来源、config_files 上传、zone、Resource、模版覆盖等）见 [SKILL.md](../SKILL.md)，此处不重复。
- **job_priority**：必传；无模版时默认 5。
- **config_files 等**：须先通过 **scripts/utils_api.py upload** 上传本地文件，将返回的 uss_path、file_name 组成数组填入 body 的 config_files、flag_file、data_converter、initialization_script 等。
- **body 格式**：body 为**整份请求对象的 JSON 字符串**；`config_files`、`wc_resource`、`worker_resource`、`sample_server_resource` 为对象/数组，勿二次 JSON 序列化。
- **Resource**：GPU 须同时指定 `mig_gpu` 与 `gpuType`。
- **zone**：无模版时须与 **utils_api.py project_quota** 有剩余配额的 zone 一致；使用模版时见 SKILL 5.1。

---

## 常见错误与处理（Job 状态码 category 14）

| 情况 / code                 | 可能原因                                  | 建议                                                                                                                                 |
| --------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| 9914101 未授权              | Token 无效或未传                          | 检查环境变量 **USER_ID_OPENAPI**，确认 Cookie 鉴权有效。                                                                             |
| 9914102 禁止                | 无权限操作该项目/作业                     | 确认 tenant_id、project_id 来自流程第 3 步**模型记录**，且该 tenant/project 在用户权限内（见 SKILL 权限校验）。                      |
| 9914103 未找到              | 资源不存在（如 model/version/checkpoint） | 确认 related_model_id、related_version_id、checkpoint_id 等为有效 ID。                                                               |
| 9914107 错误请求            | 参数格式或内容错误                        | 检查 body 是否为整份 JSON 字符串；config_files、wc_resource、worker_resource 是否为对象/数组（非二次 JSON 字符串）；必填项是否齐全。 |
| 9914108 参数必填            | 缺少必填字段                              | 补全 job_name、training_job_type、job_priority、config_files（至少一项含 uss_path、file_name）等。                                   |
| job_name 无效（如长度不符） | job_name 非 2–50 字符或不符合命名规范     | 将 job_name 改为 2–50 字符内且符合规范。                                                                                             |
| create 的 body 非法 JSON    | body 含未转义引号、换行或非 JSON 语法     | 确保 body 为合法 JSON 字符串；命令行传入时用单引号包裹或通过 `"$(cat file.json)"` 传入文件内容。                                     |
| 调度/资源失败               | zone 无配额或 Resource 不合规             | 用 **utils_api.py project_quota** 选有剩余配额的 zone；GPU 同时传 mig_gpu 与 gpuType。                                               |

提交失败时，根据返回的 code 与 message 对照上表，并结合「使用注意」给出可执行修改建议。

---

## 调用示例

将下方「请求体对象」序列化为 **一行或带转义的 JSON 字符串** 作为 **body** 传入 **train_job.py create**。

**说明**：示例中 `dump_url` 为 USS 文件地址（与门户 EGO_BASE_URL 无关）；创建作业时 config_files 每项至少含 `uss_path`、`file_name` 即可（通常由 **utils_api.py upload** 返回）。任务详情页链接使用 EGO_BASE_URL（SG：`https://ego-portal.mlp.shopee.io`，US：`https://ego-portal.mlp.us.shopee.io`），见 [SKILL.md](../SKILL.md) 输出格式。

**命令行示例**（工作目录为 skill 根目录）：`python scripts/train_job.py create '{"training_job_type":"21","job_name":"my-job",...}'`

**请求体对象（序列化后作为 body）：**

```json
{
  "training_job_type": "21",
  "job_name": "cvr-base",
  "description": "base",
  "job_priority": 1,
  "skip_sandbox": false,
  "project_id": "7a7308a7-2ee5-4cc6-910c-984282c4655a",
  "related_model_id": 10100,
  "related_version_id": 76242,
  "use_git_config": false,
  "config_files": [
    {
      "uss_path": "search/search_algo/jobs/38788816/config/ego-learner.yaml",
      "file_name": "ego-learner.yaml",
      "type": "",
      "md5": "",
      "dump_url": "https://ego-sg.uss.shopee.io/api/v4/91025041/ego-offline-training/search/search_algo/jobs/38788816/config/ego-learner.yaml",
      "status": "done"
    }
  ],
  "data_converter": [
    {
      "uss_path": "search/search_algo/jobs/38788816/config/converter.py",
      "file_name": "converter.py",
      "type": "",
      "md5": "",
      "dump_url": "https://ego-sg.uss.shopee.io/api/v4/91025041/ego-offline-training/search/search_algo/jobs/38788816/config/converter.py",
      "status": "done"
    }
  ],
  "flag_file": [
    {
      "uss_path": "search/search_algo/jobs/38788816/config/flags.txt",
      "file_name": "flags.txt",
      "type": "",
      "md5": "",
      "dump_url": "https://ego-sg.uss.shopee.io/api/v4/91025041/ego-offline-training/search/search_algo/jobs/38788816/config/flags.txt",
      "status": "done"
    }
  ],
  "train_version": "v0.0.0",
  "train_image": "harbor.shopeemobile.com/mlp-ego/ego-train-runtime:V1.8.2-fix_lua_pool-tf2-sg-20250617062713",
  "compile_image": "harbor.shopeemobile.com/mlp-ego/ego-train-runtime:V1.8.2-fix_lua_pool-tf2-sg-20250617062713",
  "zone": "offline-sg12",
  "is_colocate": false,
  "worker_resource": {
    "replicas": 4,
    "gpuType": "A30",
    "mig_gpu": "1",
    "cpu": 30,
    "memory": 200
  },
  "sample_server_resource": {
    "replicas": 24,
    "cpu": 15,
    "memory": 45
  },
  "wc_resource": {
    "replicas": 1,
    "cpu": 8,
    "memory": 40
  },
  "pending_over_time": 6000,
  "pending_over_time_unit": "minutes",
  "offline_half_precision": true,
  "online_half_precision": false,
  "use_new_io": true,
  "generate_validation_config": false,
  "checkpoint_id": 5973590,
  "user_define_filter_nn": false,
  "user_define_load_slot_mode": 0
}
```

**脚本调用**：将上述对象序列化为一行 JSON 字符串，作为 **train_job.py create** 的 body 参数传入。
