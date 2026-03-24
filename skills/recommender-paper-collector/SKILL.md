---
name: recommender-paper-collector
description: 搜索、整理并汇总近期推荐系统/搜索/生成式检索及可迁移到搜索场景的LLM结构优化论文到Google Sheets。当用户需要收集 recommender、retrieval、ranking、latent reasoning、generative，或“可落地到搜索的LLM结构改造（含注意力机制、loss设计、生成式建模）”相关论文时使用。支持从arXiv搜索论文，生成中文标题/中文摘要/工程化亮点，并自动写入指定Google Sheets。
---

# Recommender Paper Collector

本技能用于自动化收集、整理和汇总近期推荐系统/搜索系统相关论文，重点覆盖推荐、检索、排序、生成式检索，以及可迁移到电商搜索场景的LLM结构优化研究（如路由、记忆、推理增强、重排蒸馏等）。

## 核心功能

### 1. 论文搜索与过滤

- 从arXiv API搜索最新论文
- 按时间范围过滤（默认最近7天）
- 按类别过滤（cs.IR, cs.LG, cs.AI）
- **关键词智能匹配**：严格筛选推荐系统核心论文
- **查重检查**：先读取目标Google Sheet，检查arXiv ID列是否有重复，忽略已存在的论文

**论文筛选标准（严格）：**

必须满足以下条件之一：

1. **标题明确包含推荐系统关键词**：
   - recommender system, recommendation, collaborative filtering
   - sequential recommendation, session-based recommendation
   - user-item, rating prediction, click prediction

2. **标题明确包含搜索系统关键词**：
   - search, retrieval, query, document retrieval
   - passage retrieval, learning to rank, dense retrieval
   - information retrieval, semantic search

3. **标题明确包含广告系统关键词**：
   - advertising, ad ranking, ad recommendation
   - click-through rate, CTR, CVR
   - bid optimization, ad targeting

4. **生成式搜广推**：
   - generative retrieval, generative recommendation
   - LLM for recommendation, LLM for search

5. **可迁移到搜索/推荐的LLM结构优化**：
   - MoE路由优化、长上下文记忆机制、检索增强推理、奖励建模/对齐策略
   - query rewrite、reranker蒸馏、multi-stage retrieval、reasoning-aware retrieval

6. **LLM机制层改造（可落地搜推优先）**：
   - 注意力机制：sparse attention、linear attention、grouped-query attention、long-context attention
   - loss设计：contrastive loss、pairwise/listwise ranking loss、distillation loss、alignment/regularization loss
   - 生成式建模：decoder-only生成检索、生成式重排、生成式query改写、生成式用户意图建模

**排除条件（自动跳过）**：

- 与搜广推无关且不可迁移的纯理论研究
- 与业务场景无直接关系的跨学科论文（量子、天文、纯生物等）
- 仅报告模型规模/榜单分数，缺乏可复用方法细节的论文
- 仅有“注意力/loss/生成式”术语但无搜索或推荐迁移路径的论文

**判断优先级**：标题 > 摘要 > 类别

### 2. 数据提取与整理

- 提取论文元数据（标题、作者、日期、arXiv ID）
- 生成**机制标签（新增，放在前列）**：如 检索 / 推荐系统 / 排序重排 / 注意力机制 / Loss设计 / 生成式 / RAG / 蒸馏 / 图建模 / 长上下文记忆 / MoE路由 / 评测基准
- 生成**中文标题（新增）**
- 生成**中文摘要（新增，2-4行要点）**
- 识别方法亮点和创新点，准确、详细描述论文核心方法
- **核心方法细节强化（强制）**：必须写清模块设计、数据流、训练目标、关键超参、复杂度/延迟影响、上线风险
- **关键代码片段**：亮点做法中包含核心算法的关键代码（伪代码或简化实现）
- 输出“是否可迁移到电商搜索”结论（是/否 + 简短理由）

### 3. Google Sheets自动化

- 自动写入Google Sheets文档
- 处理OAuth 2.0认证
- 格式化表格数据
- **固定可读性布局（默认）**：写入后直接可读，不依赖人工拖拽调列宽/行高
  - 冻结首行（表头）
  - 全列启用自动换行 + 顶部对齐
  - 默认列宽偏紧凑：核心方法列 `900px`，摘要列 `380px`（不再输出英文概要列）
  - **写入后按文本量动态调行高**（避免大面积空白）：根据“核心方法+摘要”的行数分段设置行高（如 220/320/420/520）
- 避免重复记录

## 工作流程

### 稳定检索规范（防止每次结果不一致，必须执行）

> 目标：同一天、同关键词、同类别下，多次执行结果一致（允许 arXiv 新增版本号带来的极小差异）。

1. **固定检索窗口**
   - 必须使用 `published` 精确日期过滤（如 `2026-03-17`）
   - 不要用“最近7天”替代精确日期任务

2. **固定排序与分页**
   - 固定 `sortBy=submittedDate&sortOrder=descending`
   - 必须分页拉取（建议 `max_results=200`），直到覆盖目标日期
   - 禁止只取第一页就下结论

3. **固定类别与关键词集合**
   - 类别固定：`cs.IR, cs.LG, cs.AI`
   - 关键词分组固定：
     - recommender组：recommendation / recommender / collaborative / sequential recommendation
     - retrieval组：retrieval / search / ranking / rerank / query
     - generative+reasoning组：generative retrieval / generative recommendation / latent reasoning / reasoning-intensive retrieval
     - LLM结构迁移组：MoE routing / long-context memory / KV cache optimization / reasoning policy / distillation for reranker
     - 机制层关键词组：attention mechanism / sparse attention / linear attention / GQA / loss reweighting / ranking loss / distillation loss / generative ranking

4. **先全量后筛选**
   - 先拿到“目标日期+类别”的全量候选
   - 再按关键词与业务相关性打分筛选
   - 严禁边拉取边主观删减，避免漏论文

5. **去重与版本统一**
   - 以 `arXiv ID(不含vN)` 去重（如 `2603.17205`）
   - 同一论文保留最高版本号用于链接展示

6. **结果可复现输出**
   - 在结果中保留：查询时间、query字符串、分页范围、候选总数、入选总数
   - 写入sheet前先做ID查重，避免“看起来每次不一样”其实是重复写入/遗漏

### 数据格式化规范（必须遵循）

**核心方法列换行规范（最重要）：**

> ⚠️ **写入Google Sheets时，必须使用 `\n` 换行符！**
>
> 在Python字符串中写 `\n`，不要写 `\\n` 或 literal 换行

**格式要求：**

1. **使用换行符 `\n` 分隔不同章节**（在Python字符串中正确使用）
2. **每个主要部分使用【】包裹作为标题**
3. **列表项使用数字+点号+空格格式**
4. **每个主要模块之间用 `\n\n` 分隔（空行）**

**标题/摘要换行规范：**

- **中文标题**：尽量保持术语准确（如 retrieval→检索，rerank→重排，alignment→对齐）
- **中文摘要**：多个要点用 `\n` 分隔，每个要点单独一行（建议2-4行）

**示例：**

```python
# 中文摘要示例
summary = (
    "提出AlignUSER框架，通过世界模型学习LLM代理来评估推荐系统。\n"
    "解决了离线指标与真实用户行为之间的差距问题。\n"
    "核心贡献：世界模型+反事实轨迹+策略学习"
)

# （已移除英文概要列，不再生成 english_summary）
```

**正确的格式示例（在Python代码中这样写）：**

```python
core_method = (
    "【框架/模型结构】\n"
    "1. 模块名称：具体功能描述\n"
    "2. 模块名称：具体功能描述\n\n"
    "【Loss函数设计】\n"
    "- Loss名称：计算方式\n"
    "- Loss名称：计算方式\n\n"
    "【训练策略】\n"
    "- 配置1：具体数值\n"
    "- 配置2：具体数值\n\n"
    "【实验结果与可复现细节】\n"
    "- 关键指标：...\n"
    "- 训练/推理资源：...\n"
    "- 复现注意事项：..."
)
```

> 💡 **关键点**：用 `\n` 而不是实际的换行，这样写入Google Sheets后会正确显示多行

**写入时的技术处理：**

```python
# 在写入Google Sheets前进行格式化
def format_cell_content(text):
    """格式化单元格内容，确保换行正确显示"""
    # 确保使用 \n 换行
    formatted = text.replace('\n\n', '\n').replace('\r\n', '\n')
    # Google Sheets会自动处理换行显示
    return formatted
```

**Google Sheets列设置（增强可读性默认值）：**

- **核心方法列**：启用"文本自动换行" + 顶部对齐，列宽 `900px`
- **摘要列**：列宽 `380px`
- **其他文本列**：统一启用自动换行
- **行高**：按文本量动态设置，避免空白过多（建议分段：`220/320/420/520px`）
- **表头**：冻结首行（便于滚动阅读）

**必须包含以下内容（电商搜索工程师视角，强制）：**

1. **【要解决的问题】**
   - 明确论文针对的痛点（如：召回覆盖不足、相关性差、长尾冷启动、多模态匹配、推理延迟高）
   - 说明该问题在电商搜索链路中属于：Query理解 / 召回 / 粗排 / 精排 / 重排 / 生成式答案

2. **【模型结构与数据流】**
   - 用 1-2-3 步骤写清输入→编码→交互→输出
   - 必须写关键模块名（例如 MoE Router、Cross-Attention、Dual-Encoder、Reranker、Diffusion Head）
   - 必须写训练目标（至少列出主 Loss + 辅助 Loss）

3. **【关键公式/伪代码】**
   - 至少给 1 段核心公式或伪代码，解释“比基线强在哪里”
   - 不允许只写“详见原文”

4. **【关键超参与工程约束】**
   - 至少写 3 个可执行参数（如 embedding dim、topK、temperature、负采样比、学习率、batch size）
   - 必须补充复杂度或资源代价（训练时长、显存、在线延迟/QPS影响）

5. **【对电商搜索的直接帮助】（最关键）**
   - 必须回答 4 个问题：
     - 可迁移到哪一层？（召回/粗排/精排/重排/Query改写）
     - 改造成本多大？（低/中/高 + 原因）
     - 预期收益指标是什么？（CTR/CVR/GMV/ATC/NDCG/Recall）
     - 风险点是什么？（时延、稳定性、偏置、线上分布漂移）

6. **【上线建议】**
   - 给出最小可落地方案（MVP）与 A/B 测试建议（实验桶、观察周期、护栏指标）

---

**示例格式（在Python中写入时）：**

```python
core_method = (
    "【要解决的问题】\n"
    "- 痛点：多模态检索中图文模态失衡，导致长尾商品召回质量下降。\n"
    "- 所在链路：召回 + 精排特征构建。\n\n"
    "【模型结构与数据流】\n"
    "1. 输入：query文本、商品标题、商品主图、用户行为序列。\n"
    "2. 编码：VLM双塔编码 + 序列建模层，得到q_emb和item_emb。\n"
    "3. 对齐：弱模态惩罚对比学习，抑制单模态主导训练。\n"
    "4. 输出：用于ANN召回与精排特征拼接的统一向量。\n"
    "5. Loss：L = L_main(InfoNCE) + λ1*L_weak_modal + λ2*L_topology。\n\n"
    "【关键公式/伪代码】\n"
    "score(q,i)=cos(f_q(q), f_i(i));\n"
    "if grad_ratio < τ: apply weak-modality penalty\n"
    "L_total = L_ctr + λ*L_contrastive\n\n"
    "【关键超参与工程约束】\n"
    "- dim=1024, topK=200, temperature=0.05, neg_ratio=1:50\n"
    "- 训练：8*A100, 24h；在线新增延迟约+6ms（P95）\n"
    "- ANN索引内存增加约18%，需评估召回机容量\n\n"
    "【对电商搜索的直接帮助】\n"
    "- 可迁移层：召回（主）、精排（辅）\n"
    "- 改造成本：中（需重训多模态向量 + 更新ANN索引）\n"
    "- 预期收益：Recall@200 +2~4%，长尾query CTR +1~2%\n"
    "- 风险点：高峰期时延抖动、商品图质量差导致收益不稳\n\n"
    "【上线建议】\n"
    "- MVP：先在女装/3C两个高流量类目灰度10%流量\n"
    "- A/B：观察7~14天，护栏指标含GMV、CVR、P95时延、无结果率\n\n"
    "【实验结果与可复现细节】\n"
    "- 关键指标：...\n"
    "- 训练/推理资源：...\n"
    "- 复现注意事项：..."
)
```

> ⚠️ **禁止**：
>
> - 不要用 `\\n`，这会显示为 literal `\n` 而不是换行
> - 不要用三引号 ''' 或 """ 包裹多行，然后用 replace 处理
> - 直接在Python字符串中使用 `\n` 换行符

### 快速启动命令

**开始前必做：查重检查**

```bash
# 读取Google Sheet已有数据，检查arXiv ID是否已存在
python3 /root/.openclaw/workspace/google_sheets_fetcher.py "https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}" "工作表1!E:E"
```

如果有重复：

- 比对已有论文的arXiv ID
- 如果论文已存在，跳过该论文
- 只添加不重复的新论文

```bash
# 完整工作流：搜索+处理+写入
python3 scripts/full_workflow.py --days 7 --spreadsheet-id <YOUR_SPREADSHEET_ID>

# 分步执行
python3 scripts/search_papers.py --days 7 --categories cs.IR,cs.LG,cs.AI
python3 scripts/process_papers.py --input papers.json
python3 scripts/write_to_sheets.py --input processed_papers.json --sheet-name "推荐系统论文"
```

### 详细步骤

#### 步骤1：搜索论文

```bash
python3 scripts/search_papers.py \
  --days 7 \
  --categories cs.IR,cs.LG,cs.AI \
  --keywords "recommender system,recommendation,collaborative filtering,multimodal" \
  --output papers.json
```

#### 步骤2：处理论文数据

```bash
python3 scripts/process_papers.py \
  --input papers.json \
  --lang zh \
  --include-abstract \
  --output processed_papers.json
```

#### 步骤3：写入Google Sheets

```bash
python3 scripts/write_to_sheets.py \
  --spreadsheet-id "1TW-NubPwQCrhVvV1maV4KQRYfjoJ39e1V_L_Tx6oPrQ" \
  --sheet-name "推荐系统论文" \
  --input processed_papers.json \
  --start-row 1
```

## 配置说明

### Google Sheets配置

所有Google Sheets操作使用统一配置：

- **OAuth Token**: `/root/agent/token.json`
- **Client Secrets**: `/root/agent/google.json`
- **权限范围**: `https://www.googleapis.com/auth/spreadsheets`

### 默认参数

- **搜索天数**: 7天
- **arXiv类别**: cs.IR, cs.LG, cs.AI
- **输出列顺序（默认）**: 序号、论文标题、摘要、机制标签、核心方法、作者、日期、论文地址、arXiv ID、类别、检索配置
- **中文摘要**: 默认生成中文摘要
- **换行处理**: 所有文本列（摘要、核心方法）都使用 `\n` 换行符

### 自定义配置

创建`config.json`文件进行自定义：

```json
{
  "search": {
    "default_days": 7,
    "categories": ["cs.IR", "cs.LG", "cs.AI"],
    "keywords": [
      "recommender system",
      "recommendation",
      "collaborative filtering",
      "multimodal",
      "sequential recommendation",
      "pretrain",
      "pre-training",
      "attention mechanism",
      "sparse attention",
      "linear attention",
      "grouped-query attention",
      "ranking loss",
      "distillation loss",
      "generative retrieval",
      "generative ranking"
    ]
  },
  "sheets": {
    "default_sheet_name": "推荐系统论文",
    "header_row": [
      "序号",
      "论文标题",
      "摘要",
      "机制标签",
      "核心方法",
      "作者",
      "日期",
      "论文地址",
      "arXiv ID",
      "类别",
      "检索配置"
    ],
    "column_widths": {
      "核心方法列": 400,
      "其他列": "自动"
    },
    "row_height": "自适应",
    "enable_text_wrap": true,
    "date_format": "YYYY-MM-DD"
  }
}
```

## 使用示例

### 示例1：收集近期推荐系统论文

用户说："帮我收集最近一周的推荐系统论文"

```bash
python3 scripts/full_workflow.py --days 7
```

### 示例2：更新到指定Google Sheets

用户说："把这些论文更新到Google Sheets文档"

```bash
python3 scripts/write_to_sheets.py \
  --spreadsheet-id "1TW-NubPwQCrhVvV1maV4KQRYfjoJ39e1V_L_Tx6oPrQ" \
  --input processed_papers.json
```

### 示例3：搜索特定主题论文

用户说："帮我找多模态推荐相关的论文"

```bash
python3 scripts/search_papers.py \
  --days 14 \
  --keywords "multimodal recommendation,vision-language,visual recommendation"
```

## 脚本说明

### 主要脚本文件

#### `scripts/search_papers.py`

- 功能：从arXiv搜索论文
- 参数：
  - `--days`: 搜索天数（默认7）
  - `--categories`: arXiv类别（默认cs.IR,cs.LG,cs.AI）
  - `--keywords`: 关键词过滤
  - `--output`: 输出文件（默认papers.json）

#### `scripts/process_papers.py`

- 功能：处理原始论文数据，生成结构化信息
- 参数：
  - `--input`: 输入文件
  - `--lang`: 语言（zh/en，默认zh）
  - `--include-abstract`: 是否包含摘要
  - `--output`: 输出文件（默认processed_papers.json）

#### `scripts/write_to_sheets.py`

- 功能：写入Google Sheets
- 参数：
  - `--spreadsheet-id`: Google Sheets ID（必须）
  - `--sheet-name`: 工作表名称
  - `--input`: 输入文件
  - `--start-row`: 起始行（默认1）

#### `scripts/full_workflow.py`

- 功能：完整工作流（搜索+处理+写入）
- 参数：整合所有脚本参数

## 故障排除

### 常见问题

#### 1. Google Sheets认证失败

```bash
# 检查token文件
ls -la /root/agent/token.json /root/agent/google.json

# 测试连接
python3 scripts/test_connection.py
```

#### 2. arXiv搜索无结果

- 增加搜索天数：`--days 14`
- 扩大类别范围：`--categories cs.IR,cs.LG,cs.AI,cs.CV`
- 添加更多关键词：`--keywords "recommendation system"`

#### 3. 数据写入格式错误

- 检查日期格式是否为"YYYY-MM-DD"
- 验证JSON文件结构
- 检查表头列数匹配

### 调试命令

```bash
# 详细日志模式
python3 scripts/search_papers.py --verbose --debug

# 只测试不写入
python3 scripts/write_to_sheets.py --dry-run --input test_data.json

# 验证数据格式
python3 scripts/validate_data.py --input processed_papers.json
```

## 参考文件

详细API文档和示例请参阅：

- [API参考](references/api_reference.md)：arXiv API和Google Sheets API详细文档
- [配置示例](references/config_examples.md)：完整配置示例和模板
- [工作流程](references/workflow_guide.md)：详细步骤和决策流程图

## 更新记录

- v2.2 (2026-03-20):
  - **布局改为紧凑版**：核心方法列 `900px`、摘要列 `380px`
  - **行高改为动态分段**：写入后按文本长度自动设为 `220/320/420/520px`，减少空白
  - **要求**：先完成数据写入，再按实际文本量批量调整行高

- v2.1 (2026-03-20):
  - **移除英文概要列**：默认输出不再包含英文摘要/英文概要
  - **核心方法加强（强制）**：要求更细节、更丰富，必须覆盖模块设计、数据流、训练目标、关键超参、资源代价、上线风险
  - **默认顺序保持阅读优先**：`序号、论文标题、摘要、机制标签、核心方法` 固定前五列

- v2.0 (2026-03-20):
  - **列顺序调整（按阅读优先级）**：固定前五列为`序号、论文标题、摘要、机制标签、核心方法`
  - **后续列放宽**：作者、日期、链接、arXiv ID、类别、检索配置可后置
  - **目标**：首屏快速浏览“是什么论文 + 做了什么 + 用了什么机制 + 新方法细节”

- v1.9 (2026-03-20):
  - **可读性布局升级**：新增“固定可读性布局（默认）”，写入后无需手动调列宽/行高
  - **默认尺寸统一**：核心方法列 980px、摘要 420px、数据行高 520px
  - **显示增强**：要求冻结首行、全列自动换行、顶部对齐

- v1.8 (2026-03-20):
  - **列顺序调整**：`arXiv ID` 与 `类别` 统一移动到最后两列
  - **前置信息优化**：前部优先展示机制标签、标题、中文摘要与核心方法，便于快速阅读

- v1.7 (2026-03-20):
  - **扩展纳入范围**：允许收录可迁移到搜索的LLM机制层论文（注意力机制、loss设计、生成式建模）
  - **新增机制标签**：要求输出“机制标签”列，并放在前列
  - **新增中文展示**：标题与摘要支持中文列
  - **稳定检索固化**：固定类别+排序+分页+日期过滤，提升结果一致性

- v1.6 (2026-03-19):
  - **调整列顺序**：类别放到最前面，便于快速筛选
  - **新增摘要和英文概要换行规范**：所有文本列都使用 `\n` 换行
  - **严格论文筛选标准**：明确推荐系统核心论文定义，排除纯LLM/MoE/量化研究
  - **关键词优先级**：标题 > 摘要 > 类别

- v1.5 (2026-03-19):
  - 强调 `\n` 换行符的正确使用方式（不是 `\\n`）
  - 新增Python代码示例，明确展示换行写法
  - 添加"禁止"事项说明，避免常见错误

- v1.4 (2026-03-19):
  - 新增文本换行处理规范，确保Google Sheets可读性
  - 优化核心方法列格式：使用【】包裹章节标题
  - 更新列宽设置：核心方法列400px（自动换行）
  - 新增row_height自适应设置

- v1.3 (2026-03-19):
  - 新增"关键技术英文概括"列：从论文Method/Introduction提取原文
  - 更新亮点做法格式示例

- v1.2 (2026-03-19):
  - 新增查重检查：搜索前先检查Google Sheet
  - 新增英文摘要列：从论文原文提取Abstract

- v1.1 (2026-03-19):
  - 新增亮点做法格式要求（必须包含关键代码）
  - 新增列宽行高调整（做法列900px，行高400px）
  - 移除图片列

- v1.0 (2026-03-19): 初始版本
  - 基础arXiv搜索功能
  - Google Sheets写入功能
  - 中文摘要生成
  - 完整工作流脚本

---

**维护提示**：定期更新config.json中的关键词列表以覆盖最新研究方向。

## Python 版本

- 此 skill 的 Python 脚本按 **Python 3.8+** 使用。
- 当前脚本静态扫描未发现要求 3.9+/3.10+ 的语法，可按 3.8 基线处理。
