---
name: sra-ego-gitlab-ci
description: >
  Triggers GitLab CI deploy jobs for ego-train-v1 repo on a specified branch (ego-train-v1 CI 触发). Checks latest commit build status before triggering; supports retry on failure.
  TRIGGER when: user wants to trigger CI, build docker image, deploy, or run pipeline for ego-train-v1, or mentions "触发 CI", "构建镜像", "部署", "run pipeline".
  DO NOT TRIGGER when: local compile/run, notebook, submitting training job, job troubleshooting, or metric analysis.
category: platform
tags: [ego, train, ci]
---

# GitLab CI Trigger for ego-train-v1

通过 GitLab API 为 `ego-train-v1` 的指定开发分支触发 CI deploy job，构建 Docker image。

**限定仓库**：`gitlab@git.garena.com:shopee/MLP/EGO/ego-train-v1.git`

## 前置条件

- 环境变量 **GITLAB_PRIVATE_TOKEN** 已设置（GitLab PAT，需 `api` scope）
- `ego-train-v1` 的 `.gitlab-ci.yml` deploy job 已改用 `rules` 语法（支持 `CI_PIPELINE_SOURCE == "api"`）

执行前检查：

```bash
echo "${GITLAB_PRIVATE_TOKEN:?GITLAB_PRIVATE_TOKEN is not set}"
```

若未设置，提示用户在 `https://git.garena.com/-/profile/personal_access_tokens` 创建 PAT（scope: `api`），然后 `export GITLAB_PRIVATE_TOKEN=<token>`。

## 流程

### 1. 收集参数

使用 AskQuestion 收集：

**分支名**（必填，禁止 master/main）：默认使用用户本地 ego-train-v1 仓库当前分支。在 workspace 中查找包含 remote `git.garena.com:shopee/MLP/EGO/ego-train-v1` 的 git 仓库目录，然后获取当前分支：

```bash
git -C <ego-train-v1-repo-path> branch --show-current
```

其中 `<ego-train-v1-repo-path>` 需要动态确定，不可写死。

**Deploy job**（多选，默认 `deploy-tf-all-job`）：

- `deploy-tf-all-job`
- `deploy-tf1-job`
- `deploy-tf2-job`
- `deploy-torch-job`

**最大重试次数**（可选，默认 3）：job 执行失败时自动重试的上限。

### 2. 执行脚本

脚本路径：`scripts/trigger_ci.sh`（相对于本 SKILL.md）

```bash
bash "<SKILL_DIR>/scripts/trigger_ci.sh" --branch <branch> --jobs <job1,job2,...> [--max-retries <n>]
```

`<SKILL_DIR>` 为本 SKILL.md 所在目录的绝对路径。

脚本自动完成：

1. 查询分支最新 commit
2. 检查该 commit 已有的 pipeline：
   - 目标 job 全部 **success** → 直接输出 image 并结束（无需进入步骤 3）
   - 目标 job 正在 **running/pending** → 输出 pipeline URL，**不重复触发，退出脚本**
3. 若无已有构建，创建新 pipeline，等待 manual job 出现，逐个触发（play），输出 pipeline URL 后退出脚本

**注意**：脚本默认不等待 job 完成，触发后即退出。等待需配合 `--wait` 参数（见步骤 3）。

### 3. 触发后的交互处理

无论是检测到已有构建正在运行（步骤 2），还是新触发了 pipeline（步骤 2），脚本都会输出 pipeline URL 后退出。此时必须使用 AskQuestion 询问用户下一步操作：

- **自动轮询**：重新执行脚本并附加 `--wait` 参数，脚本会等待目标 job 完成（失败时自动重试，最多 `--max-retries` 次），并提取 image 地址。
- **手动查看**：仅输出 Pipeline URL，由用户自行前往 GitLab 页面查看进度。

若用户选择自动轮询，直接重跑脚本（参数与步骤 2 一致，额外加 `--wait`）：

```bash
bash "<SKILL_DIR>/scripts/trigger_ci.sh" --branch <branch> --jobs <job1,job2,...> [--max-retries <n>] --wait
```

### 4. 输出

将脚本输出转述给用户，重点包括：

- **Image 地址**：从 job 日志中提取实际 push 的 image（仅包含 tag 中含**当前 commit short_sha** 的镜像，避免混入日志里其他 commit 的镜像；每个 job 可能产出多个 image，如 sg/us 多 region）
- **Pipeline URL**：GitLab pipeline 页面链接
- **各 Job 状态**：成功/失败
- 若已有构建命中，告知「该 commit 已有成功的构建，无需重新触发」
- 若用户选择手动查看，告知 pipeline 当前状态（已有构建正在进行 / 已触发新构建）并给出 pipeline URL
- 若有 job 在重试后仍失败，列出失败的 job 名称

## 错误处理

- **GITLAB_PRIVATE_TOKEN 未设置**：提示创建和配置 PAT
- **分支为 master/main**：拒绝执行，提示切换到 feature/dev 分支
- **分支不存在**：检查分支名拼写，确认已 push 到远端
- **Pipeline 创建失败**：权限不足或 CI 配置问题，检查 `.gitlab-ci.yml` rules
- **Job 未出现（超时）**：CI 配置可能缺少 `CI_PIPELINE_SOURCE == "api"` 规则
- **Job 失败超过重试上限**：输出失败 job 名称，建议用户查看 GitLab job 日志排查
