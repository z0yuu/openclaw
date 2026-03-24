---
name: arxiv-paper
description: "搜索 arXiv 论文、获取每日最新论文、查询研究者学术画像。当用户提到「找论文」「搜论文」「最新论文」「arxiv」「学术搜索」「研究者」「学者画像」「Google Scholar」时使用。"
metadata:
  openclaw:
    emoji: "📄"
    requires:
      bins: ["python3"]
---

# arXiv 论文搜索与研究者画像

通过 arXiv API、Google Scholar、Semantic Scholar 搜索学术论文和查询研究者信息。无需 API key。

## 功能一览

| 功能         | 说明                                                   |
| ------------ | ------------------------------------------------------ |
| 关键词搜论文 | 按关键词在 arXiv 上搜索论文                            |
| 每日最新论文 | 按学科分类获取最近 24h/48h 的新论文                    |
| 研究者画像   | 查询研究者的 Google Scholar 主页、论文、引用、合作者等 |

## 功能 1: 搜索论文

按关键词搜索 arXiv 论文，支持限定时间范围。

```bash
python3 /root/agent/skills/arxiv-paper/scripts/arxiv_search.py search "QUERY" --max N --days D --format FORMAT
```

参数:

- `QUERY`: 搜索关键词（英文效果最佳），如 `"large language model"`, `"diffusion model image generation"`
- `--max N`: 最多返回 N 篇（默认 10）
- `--days D`: 只返回最近 D 天的论文（可选，不填则不限时间）
- `--format`: `json`（默认）或 `markdown`（适合直接展示给用户）

示例:

```bash
# 搜索最近7天的 LLM 相关论文，最多10篇，markdown格式
python3 /root/agent/skills/arxiv-paper/scripts/arxiv_search.py search "large language model" --max 10 --days 7 --format markdown

# 搜索 diffusion model 论文，不限时间
python3 /root/agent/skills/arxiv-paper/scripts/arxiv_search.py search "diffusion model" --max 5 --format markdown

# 搜索推荐系统论文，JSON格式用于进一步处理
python3 /root/agent/skills/arxiv-paper/scripts/arxiv_search.py search "recommendation system" --max 20 --format json
```

## 功能 2: 每日最新论文

按 arXiv 学科分类获取最近提交的论文。

```bash
python3 /root/agent/skills/arxiv-paper/scripts/arxiv_search.py daily --categories CAT1 CAT2 --max N --hours H --format FORMAT
```

参数:

- `--categories`: arXiv 分类代码（必填），多个用空格分隔
- `--max N`: 每个分类最多返回 N 篇（默认 30）
- `--hours H`: 获取最近 H 小时内的论文（默认 24）
- `--format`: `json` 或 `markdown`

常用 arXiv 分类:

| 代码    | 领域           |
| ------- | -------------- |
| cs.AI   | 人工智能       |
| cs.CL   | 计算语言学/NLP |
| cs.CV   | 计算机视觉     |
| cs.LG   | 机器学习       |
| cs.IR   | 信息检索       |
| cs.CR   | 密码学与安全   |
| cs.SE   | 软件工程       |
| cs.RO   | 机器人学       |
| stat.ML | 统计机器学习   |
| eess.SP | 信号处理       |

完整分类列表: https://arxiv.org/category_taxonomy

示例:

```bash
# 获取最近24小时 AI + NLP 最新论文
python3 /root/agent/skills/arxiv-paper/scripts/arxiv_search.py daily --categories cs.AI cs.CL --max 20 --format markdown

# 获取最近48小时机器学习论文
python3 /root/agent/skills/arxiv-paper/scripts/arxiv_search.py daily --categories cs.LG stat.ML --hours 48 --format markdown
```

## 功能 3: 研究者学术画像

查询研究者的学术信息，包括 Google Scholar 主页、研究兴趣、高引论文、最新论文、合作者、Semantic Scholar 统计等。

```bash
python3 /root/agent/skills/arxiv-paper/scripts/researcher_profile.py "NAME" --org "ORG" --scholar-url "URL" --format FORMAT
```

参数:

- `NAME`: 研究者姓名（英文，必填）
- `--org`: 所属机构（可选，提高匹配精度）
- `--scholar-url`: 直接提供 Google Scholar 主页 URL（可选，最精确）
- `--format`: `json` 或 `markdown`

示例:

```bash
# 查询 Yann LeCun 的学术画像
python3 /root/agent/skills/arxiv-paper/scripts/researcher_profile.py "Yann LeCun" --format markdown

# 指定机构提高精度
python3 /root/agent/skills/arxiv-paper/scripts/researcher_profile.py "Wei Wang" --org "UCLA" --format markdown

# 直接提供 Scholar URL
python3 /root/agent/skills/arxiv-paper/scripts/researcher_profile.py "Kaiming He" --scholar-url "https://scholar.google.com/citations?user=DhtAFkwAAAAJ" --format markdown
```

## 注意事项

- arXiv API 有速率限制，脚本已内置 3 秒间隔和重试机制
- Google Scholar 可能会限制频繁请求，如遇到问题可稍后重试
- 搜索关键词用英文效果最佳
- 首次使用需确保已安装 `arxiv` Python 包: `pip install arxiv`

## Python 版本

- 此 skill 的 Python 脚本最低按 **Python 3.10+** 使用。
- 依据：PEP 585 built-in generics without postponed annotations；PEP 604 union syntax (X | Y)。
- 若系统默认 `python3` 低于该版本，请先切到对应版本后再执行，避免语法错误或直接运行失败。
