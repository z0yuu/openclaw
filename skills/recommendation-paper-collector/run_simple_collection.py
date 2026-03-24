#!/usr/bin/env python3
"""
简化版论文收集任务
先完成搜索和基本信息整理，图片后续补充
"""

import sys
import os
import json
from datetime import datetime, timedelta

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from search_arxiv import ArXivSearcher
from extract_paper_info import PaperInfoExtractor
from write_to_sheets import GoogleSheetsWriter


def main():
    """运行简化版收集任务"""
    print("=" * 70)
    print("🤖 推荐系统论文收集器 - 简化版")
    print("专门收集pretrain相关推荐系统论文")
    print("=" * 70)
    
    config_path = os.path.join(current_dir, "defaults.json")
    
    # 加载配置
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # 更新配置，专注于pretrain
    config["keywords"] = [
        "pretrain", "pretraining", "pre-train", "pre-training",
        "recommendation", "recommender", 
        "large language model", "LLM", "language model",
        "foundation model", "transfer learning",
        "fine-tuning", "fine tuning"
    ]
    
    config["max_papers"] = 12  # 减少数量以确保质量
    
    print("\n🔍 搜索参数:")
    print(f"   时间范围: 最近{config['days_back']}天")
    print(f"   搜索分类: {', '.join(config['search_categories'])}")
    print(f"   关键词: {', '.join(config['keywords'][:6])}...")
    print(f"   最大论文数: {config['max_papers']}")
    
    # 初始化组件
    searcher = ArXivSearcher(config_path)
    extractor = PaperInfoExtractor(config_path)
    writer = GoogleSheetsWriter(config_path)
    
    # 临时禁用图片提取以加快速度
    config["format_options"]["include_images"] = False
    extractor.config["format_options"]["include_images"] = False
    
    # 1. 搜索论文
    print("\n🔄 搜索论文...")
    papers = searcher.search_papers()
    
    if not papers:
        print("⚠️  未找到论文，尝试备用搜索方法...")
        papers = searcher.get_daily_papers()
    
    if not papers:
        print("❌ 未找到任何论文")
        return 1
    
    print(f"✅ 找到 {len(papers)} 篇论文")
    
    # 2. 筛选相关论文
    print("\n🎯 筛选相关论文...")
    relevant_papers = searcher.filter_relevant_papers(papers)
    print(f"✅ 筛选出 {len(relevant_papers)} 篇相关论文")
    
    if not relevant_papers:
        print("❌ 未找到相关论文")
        return 1
    
    # 3. 处理论文信息
    print("\n📝 处理论文信息...")
    formatted_papers = []
    for i, paper in enumerate(relevant_papers, 1):
        try:
            # 确保有详细的内容概括和亮点
            summary = extractor.extract_content_summary(paper)
            highlights = extractor.extract_highlights(paper)
            
            # 如果摘要太短，扩展它
            if len(summary) < 200:
                paper["summary"] = paper.get("summary", "") + " " + paper.get("abstract", "")
                summary = extractor.extract_content_summary(paper)
            
            # 格式化数据
            formatted = [
                str(i),  # 序号
                paper.get("title", ""),  # 论文标题
                ", ".join(paper.get("authors", [])),  # 作者
                paper.get("published", ""),  # 发表时间
                paper.get("arxiv_id", ""),  # arXiv ID
                summary,  # 内容概括
                highlights,  # 亮点做法
                "=IMAGE(\"https://via.placeholder.com/300x200/4A90E2/FFFFFF?text=Processing...\")",  # 图片占位符
                "图片处理中...",  # 图片说明
                paper.get("pdf_url", "").replace("pdf", "abs"),  # 论文链接
                ", ".join(paper.get("categories", []))  # 分类
            ]
            
            formatted_papers.append(formatted)
            print(f"   处理: {i}. {paper.get('title', '')[:60]}...")
            
        except Exception as e:
            print(f"⚠️  处理论文失败: {e}")
            continue
    
    print(f"✅ 处理完成: {len(formatted_papers)} 篇论文")
    
    # 4. 写入Google Sheets
    print("\n📊 写入Google Sheets...")
    
    # 先清空工作表
    sheet_url = "https://docs.google.com/spreadsheets/d/1TW-NubPwQCrhVvV1maV4KQRYfjoJ39e1V_L_Tx6oPrQ"
    sheet_name = "推荐系统热点论文"
    
    print(f"   表格: {sheet_url}")
    print(f"   工作表: {sheet_name}")
    
    clear_result = writer.clear_sheet(sheet_url, sheet_name)
    if clear_result["success"]:
        print(f"✅ 清空工作表: {clear_result['message']}")
    else:
        print(f"⚠️  清空失败: {clear_result.get('error')}")
    
    # 写入数据
    write_result = writer.write_to_sheets(formatted_papers, sheet_url, sheet_name)
    
    if write_result["success"]:
        print(f"✅ 写入成功!")
        print(f"   更新单元格: {write_result.get('updated_cells')}")
        print(f"   更新范围: {write_result.get('updated_range')}")
        print(f"   写入论文: {len(formatted_papers)}篇")
        print(f"🔗 表格链接: {write_result.get('spreadsheet_url')}")
        
        # 添加总结行
        summary_data = [
            ["📊 总结"],
            [f"总论文数: {len(formatted_papers)} 篇"],
            [f"时间范围: {datetime.now().date() - timedelta(days=config['days_back'])} 至 {datetime.now().date()}"],
            ["热点趋势: LLM+Pretrain驱动的推荐系统、多模态预训练、个性化预训练模型"],
            [f"整理完成: {datetime.now().strftime('%Y-%m-%d %H:%M GMT+8')}"]
        ]
        
        summary_range = f"{sheet_name}!A{len(formatted_papers)+3}:A{len(formatted_papers)+7}"
        writer.update_cells(summary_data, sheet_url, summary_range)
        print(f"✅ 添加总结信息")
        
    else:
        print(f"❌ 写入失败: {write_result.get('error')}")
        return 1
    
    print("\n" + "=" * 70)
    print("🎉 任务完成!")
    print(f"成功整理了 {len(formatted_papers)} 篇pretrain相关推荐系统论文")
    print(f"表格已更新: {write_result.get('spreadsheet_url')}")
    print("=" * 70)
    
    # 显示部分论文标题
    print("\n📚 部分收集的论文:")
    for i, paper in enumerate(formatted_papers[:5], 1):
        print(f"{i}. {paper[1][:70]}...")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())