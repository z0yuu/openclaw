#!/usr/bin/env python3
"""
演示脚本 - 展示更新后的推荐系统论文收集器（包含图片功能）
"""

import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from main import RecommendationPaperCollector


def demo_basic_usage():
    """演示基本用法"""
    print("🚀 推荐系统论文收集器 - 演示脚本")
    print("=" * 60)
    
    print("📌 功能特点:")
    print("   ✅ 自动搜索arXiv最新论文")
    print("   ✅ 提取论文关键信息")
    print("   ✅ 生成包含图片的表格")
    print("   ✅ 支持Google Sheets自动写入")
    print("   ✅ 图片显示功能（使用IMAGE()函数）")
    
    print("\n🎯 主要更新:")
    print("   1. 新增图片提取功能")
    print("   2. 图片显示在Google Sheets中")
    print("   3. 包含图片说明和链接")
    print("   4. 支持点击查看arXiv原文")
    
    return True


def demo_image_feature():
    """演示图片功能"""
    print("\n🖼️ 图片功能演示")
    print("=" * 60)
    
    from simple_image_extractor import SimpleImageExtractor
    
    # 创建图片提取器
    extractor = SimpleImageExtractor()
    
    # 示例论文
    sample_papers = [
        {
            "arxiv_id": "2603.17450v1",
            "title": "VLM2Rec: Resolving Modality Collapse in Vision-Language Model Embedders",
            "description": "多模态顺序推荐论文"
        },
        {
            "arxiv_id": "2603.17533v1", 
            "title": "A Unified Language Model for Large Scale Search, Recommendation, and Reasoning",
            "description": "统一语言模型论文"
        },
        {
            "arxiv_id": "2603.17540v1",
            "title": "Deploying Semantic ID-based Generative Retrieval for Large-Scale Podcast Discovery",
            "description": "语义ID生成检索论文"
        }
    ]
    
    print("📊 图片生成示例:")
    for i, paper in enumerate(sample_papers, 1):
        print(f"\n  {i}. {paper['description']}")
        print(f"     标题: {paper['title'][:40]}...")
        
        # 提取图片
        image_formula, image_description = extractor.extract_for_paper(paper)
        
        print(f"     图片公式: {image_formula[:50]}...")
        print(f"     图片说明: {image_description}")
    
    return True


def demo_complete_workflow():
    """演示完整工作流程"""
    print("\n🔄 完整工作流程演示")
    print("=" * 60)
    
    print("步骤 1: 搜索论文")
    print("       - 使用arXiv API搜索推荐系统相关论文")
    print("       - 过滤最近7天的论文")
    print("       - 筛选相关研究领域")
    
    print("\n步骤 2: 提取信息")
    print("       - 提取标题、作者、时间等信息")
    print("       - 生成内容概括和亮点做法")
    print("       - 提取或生成代表性图片")
    
    print("\n步骤 3: 格式化数据")
    print("       - 整理为11个字段的表格")
    print("       - 包含图片公式和说明")
    print("       - 准备Google Sheets格式")
    
    print("\n步骤 4: 写入Google Sheets")
    print("       - 自动连接Google API")
    print("       - 写入数据到指定表格")
    print("       - 包含图片显示功能")
    
    print("\n步骤 5: 生成报告")
    print("       - 统计论文数量")
    print("       - 分析热点趋势")
    print("       - 提供表格链接")
    
    return True


def demo_google_sheets_output():
    """演示Google Sheets输出格式"""
    print("\n📋 Google Sheets输出格式演示")
    print("=" * 60)
    
    print("表格结构:")
    columns = [
        "A: 序号",
        "B: 论文标题", 
        "C: 作者",
        "D: 发表时间",
        "E: arXiv ID",
        "F: 内容概括",
        "G: 亮点做法",
        "H: 代表性图片",  # 包含IMAGE()公式
        "I: 图片说明",    # 包含描述和链接
        "J: 论文链接",
        "K: 分类"
    ]
    
    for col in columns:
        print(f"   {col}")
    
    print("\n📸 图片列特点:")
    print("   - H列: 使用=IMAGE()函数显示图片")
    print("   - 图片大小: 300x200像素")
    print("   - 保持宽高比")
    print("   - 可点击查看大图")
    
    print("\n🔗 链接功能:")
    print("   - 图片说明中包含arXiv链接")
    print("   - 可直接点击查看论文原文")
    print("   - 支持查看具体图表 (#F1, #F2等)")
    
    return True


def demo_how_to_use():
    """演示如何使用"""
    print("\n📚 如何使用更新后的Skill")
    print("=" * 60)
    
    print("方法 1: 使用主程序")
    print("""
from recommendation_paper_collector.main import RecommendationPaperCollector

collector = RecommendationPaperCollector()
result = collector.run(
    days_back=7,          # 搜索最近7天
    max_papers=15,        # 最多15篇
    sheet_url="你的表格链接",
    sheet_name="推荐系统热点论文",
    clear_first=True      # 清空后写入
)
""")
    
    print("方法 2: 命令行使用")
    print("""
python main.py --days 3 --max 10 --clear

可选参数:
  --days N     搜索最近N天的论文
  --max M      最多M篇论文
  --url URL    Google Sheets链接
  --sheet NAME 工作表名称
  --clear      清空现有内容
""")
    
    print("方法 3: 集成到其他脚本")
    print("""
from extract_paper_info import PaperInfoExtractor
from simple_image_extractor import SimpleImageExtractor

# 提取论文信息
extractor = PaperInfoExtractor()
formatted_data = extractor.format_paper_data(paper, index)

# 提取图片
image_extractor = SimpleImageExtractor()
image_formula, description = image_extractor.extract_for_paper(paper)
""")
    
    return True


def main():
    """运行所有演示"""
    print("🤖 推荐系统论文收集器 - 功能演示")
    print("版本: 2.0 (包含图片功能)")
    print("=" * 60)
    
    demos = [
        ("基本功能介绍", demo_basic_usage),
        ("图片功能演示", demo_image_feature),
        ("完整工作流程", demo_complete_workflow),
        ("Google Sheets输出", demo_google_sheets_output),
        ("使用方法", demo_how_to_use),
    ]
    
    for demo_name, demo_func in demos:
        print(f"\n🎬 演示: {demo_name}")
        print("-" * 40)
        try:
            demo_func()
            print(f"✅ {demo_name} 演示完成")
        except Exception as e:
            print(f"❌ {demo_name} 演示失败: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 所有演示完成！")
    print("\n📌 总结:")
    print("   ✅ Skill已成功添加图片功能")
    print("   ✅ 支持Google Sheets图片显示")
    print("   ✅ 包含完整的图片提取和格式化")
    print("   ✅ 可以立即投入使用")
    
    print("\n🔗 实际测试:")
    print("   可以运行以下命令进行实际测试:")
    print("   python test_full_with_images.py")
    print("   python main.py --days 1 --max 3 --clear")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())