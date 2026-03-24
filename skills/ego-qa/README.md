# EGO 知识库问答（ego-qa）

通过本地索引定位 + Confluence REST API 在线读取内容，回答 EGO 平台相关问题。

## 目录结构

```
skill/ego-qa/
├── SKILL.md                          # Skill 定义（工作流 + 直读表）
├── README.md                         # 本文件
├── references/                       # 本地索引文件（Grep 检索用）
│   ├── kb-faq.md                     # FAQ 路由索引
│   ├── kb-index.md                   # 文档摘要索引
│   ├── kb-heading-index.md           # 大文档章节索引
│   ├── kb-index-meetings.md          # 会议纪要索引
│   ├── kb-confluence-map.json        # 文件名 → Confluence pageId 映射
│   └── prd-version-map.md            # PRD 版本映射
└── scripts/                          # Confluence CLI + 索引生成脚本
    ├── fetch_confluence.py           # Confluence REST API CLI（查询用）
    └── refresh_indexes.py            # 在线刷新全部索引（从 Confluence 拉取）
```

## 快速开始

### 1. 安装依赖

```bash
pip install httpx
```

### 2. 配置环境变量

```bash
# ── 查询（fetch_confluence.py）──
# 用户名密码即可；如果同时配置了 TOKEN 则自动优先使用 TOKEN
export CONFLUENCE_USERNAME="your-email"
export CONFLUENCE_PASSWORD="your-password"

# ── 刷新索引（refresh_indexes.py）──
# 必须提供 Personal Access Token，搜索/列表 API 仅 PAT 有权限
export CONFLUENCE_TOKEN="your-personal-access-token"

# 可选
export CONFLUENCE_BASE_URL="https://confluence.shopee.io"  # 默认值，可省略
```

| 场景     | 所需变量                            | 说明                                          |
| -------- | ----------------------------------- | --------------------------------------------- |
| 日常查询 | `USERNAME` + `PASSWORD`（最低要求） | 按 page_id 读取页面，username/password 足够   |
| 日常查询 | `TOKEN`（可选，若提供则优先）       | 有 TOKEN 时自动使用，无需额外配置             |
| 刷新索引 | `TOKEN`（**必须**）                 | `--discover` 需要搜索/列表 API，仅 PAT 有权限 |

> PAT 获取方式：登录 Confluence → 右上角头像 → Settings → Personal Access Tokens → 创建。

### 3. 配置 Skill

将 `skill/ego-qa/SKILL.md` 添加到 Cursor Agent Skills（Settings → Features → Agent Skills → Add）。

### 4. 验证

```bash
python3 skill/ego-qa/scripts/fetch_confluence.py get_page --page_id 834605511 --max_chars 2000
```

## 刷新索引

> **前提**：需要设置 `CONFLUENCE_TOKEN`（PAT），username/password 无权限执行搜索/列表 API。

当 Confluence 上有新增或更新文档时，运行以下命令刷新全部索引文件：

```bash
# 基于现有 map 刷新索引
python3 skill/ego-qa/scripts/refresh_indexes.py

# 先发现两个 EGO 根页面下的新页面，再刷新索引
python3 skill/ego-qa/scripts/refresh_indexes.py --discover

# 指定并发数（默认 5）
python3 skill/ego-qa/scripts/refresh_indexes.py --concurrency 10
```

脚本会从 `kb-confluence-map.json` 中的页面列表出发，通过 Confluence API 拉取每个页面的最新内容，重新生成四个索引文件（kb-index.md、kb-index-meetings.md、kb-heading-index.md、kb-faq.md）。

`--discover` 模式仅在以下两个 EGO 根页面下查找新页面（不会扫描整个 MLP 空间）：

- **Ego** (page_id=621646772): https://confluence.shopee.io/display/MLP/Ego
- **EGO.** (page_id=1079221126): https://confluence.shopee.io/pages/viewpage.action?pageId=1079221126

## 工作原理

1. **本地 Grep 索引** → 快速定位目标文档（kb-faq / kb-index / kb-heading-index）
2. **fetch_confluence.py 在线读取** → 通过 Confluence REST API 获取最新页面内容
3. **结构化回答** → 附带 Confluence 来源链接
