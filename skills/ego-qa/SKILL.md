---
name: ego-qa
description: EGO平台知识库问答。通过本地索引定位 + Confluence REST API 在线读取内容回答问题。
---

# EGO 知识库问答

回答必须有知识库依据，禁止编造。

KB_REF=skill/ego-qa/references
CONFLUENCE_MAP=skill/ego-qa/references/kb-confluence-map.json
FETCH=skill/ego-qa/scripts/fetch_confluence.py

认证：查询时提供 `CONFLUENCE_USERNAME` + `CONFLUENCE_PASSWORD` 即可；若用户已配置 `CONFLUENCE_TOKEN`（PAT）则自动优先使用。
索引刷新脚本 `refresh_indexes.py` 必须提供 `CONFLUENCE_TOKEN`（PAT），因搜索/列表 API 需要 PAT 权限。

## 能力边界

**仅知识问答**。遇到以下场景告知用户使用对应 Skill：

- 任务失败排查 → `job-troubleshooter`
- 效果指标分析 → `job-analysis`
- 创建/修改任务 → `launch-train-job`

## 直读表（关键词 → pageId）

| 关键词                            | pageId     | 备用 title                        |
| --------------------------------- | ---------- | --------------------------------- |
| model/version/版本/改名           | 1967739942 | About Model and Version           |
| training job/训练任务             | 1967740302 | About Training Job                |
| 架构/design/architecture          | 621646854  | (Old)Ego Design                   |
| online learning/在线学习          | 2727653884 | Online Learning                   |
| notebook                          | 2121024178 | About Notebook                    |
| portal/用户手册                   | 1867028188 | EGO Portal User Manual            |
| PS/parameter server               | 1493949532 | PS Model Load User Manual         |
| predictor/推理/部署               | 791023201  | EgoPredictor User Manual          |
| GPU/显卡/调优                     | 2664613148 | GPU任务调优指南                   |
| 限流/rate limit                   | 1261103361 | EgoPS限流规则                     |
| FAQ/常见问题                      | 834605511  | Ego FAQ                           |
| checkpoint/ckpt/管理              | 1967741313 | About Management                  |
| release/inferencing/上线          | 1967741147 | About Inferencing                 |
| ego-learner/learner配置           | 1547770091 | config module ego-learner yaml    |
| 日志/log/debug                    | 1456382199 | User Debug Manual                 |
| 准入/淘汰/evict/admission         | 758757789  | feature admission and elimination |
| converter/数据转换/cpp converter  | 1661460157 | How to use cpp converter          |
| period/周期训练/periodic training | 2727653775 | Period Rule                       |
| sample_server/SS/数据供给/IO      | 1988573192 | EgoTrainV1 IO module update       |
| guardian/调度/负载均衡            | 1649983748 | Ego Predictor Guardian            |
| half precision/半精度/fp16        | 1844467568 | EGO Half-Precision Introduction   |
| compile/编译/本地编译             | 1585290947 | How to compile model manually     |
| ego-lite/egolite                  | 2434817506 | ego-lite                          |
| benchmark/性能测试/压测           | 1647664445 | Benchmark tool                    |
| OOM/内存/显存/性能追查            | 2822082410 | EGO 性能追查流程                  |
| script/脚本/API/shell脚本         | 1867028188 | Scripts for using EgoPortal API   |

## 工作流程（严格 2 turn）

**Turn 1**（一次并行请求）：

1. 直读表命中 → `Shell: python ${FETCH} get_page --page_id xxx --max_chars 8000` + 3 Grep 索引
2. 未命中 → 仅 3 Grep 索引

Grep（搜索本地索引文件）：

- Grep `${KB_REF}/kb-faq.md` pattern="关键词" -i head_limit=3
- Grep `${KB_REF}/kb-heading-index.md` pattern="关键词" -i head_limit=3
- Grep `${KB_REF}/kb-index.md` pattern="关键词" -i head_limit=3
  会议/周报→额外 Grep `${KB_REF}/kb-index-meetings.md`。

**Turn 2**：

- 信息充足 → 直接回答
- 不足 → 从 Grep 结果中找到文件名 → 查 map 获取 page_id → `Shell: python ${FETCH} get_page --page_id xxx` 补读 1-2 篇 → 必须回答
- **禁止 Turn 2 做 Grep，禁止超 2 turn**

### 文件名 → pageId 查找

Grep 结果中的文件名需转换为 Confluence 页面：

1. Grep `${CONFLUENCE_MAP}` pattern="文件名关键部分" head_limit=3 → 从结果中提取 page_id
2. 有 page_id → `Shell: python ${FETCH} get_page --page_id xxx`
3. 无 page_id 但有 title → `Shell: python ${FETCH} get_page --title "xxx"`
4. 都没有 → `Shell: python ${FETCH} search --query "关键词"`

## 回答规则

- 禁止编造/照搬，结构化呈现
- 末尾附来源，格式：`**来源：** [页面标题](Confluence链接)`，直接用文档名称作为超链接文本，多源逐条列出
- 禁止把自身训练知识混入回答，多源/推断回答需逐条溯源
- 问题不清晰时先追问，给 2-3 个方向供选择
- 找不到说"知识库中暂未找到"，说明已搜索范围

## Python 版本

- 此 skill 的 Python 脚本最低按 **Python 3.10+** 使用。
- 依据：PEP 585 built-in generics without postponed annotations；PEP 604 union syntax (X | Y)。
- 若系统默认 `python3` 低于该版本，请先切到对应版本后再执行，避免语法错误或直接运行失败。
