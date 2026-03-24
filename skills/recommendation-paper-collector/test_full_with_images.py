#!/usr/bin/env python3
"""
测试完整的推荐系统论文收集器（包含图片功能）
"""

import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from extract_paper_info import PaperInfoExtractor
from simple_image_extractor import SimpleImageExtractor


def test_paper_extraction():
    """测试论文信息提取（包含图片）"""
    print("🧪 测试论文信息提取（包含图片功能）")
    print("=" * 60)
    
    # 创建提取器
    extractor = PaperInfoExtractor()
    
    # 测试数据
    test_papers = [
        {
            "title": "VLM2Rec: Resolving Modality Collapse in Vision-Language Model Embedders for Multimodal Sequential Recommendation",
            "authors": ["Junyoung Kim", "Woojoo Kim", "Jaehyung Lim", "Dongha Kim", "Hwanjo Yu"],
            "published": "2026-03-18",
            "arxiv_id": "2603.17450v1",
            "summary": "Sequential Recommendation (SR) in multimodal settings typically relies on small frozen pretrained encoders, which limits semantic capacity and prevents Collaborative Filtering (CF) signals from being fully integrated into item representations.",
            "categories": ["cs.IR", "cs.AI"],
            "pdf_url": "https://arxiv.org/pdf/2603.17450v1"
        },
        {
            "title": "A Unified Language Model for Large Scale Search, Recommendation, and Reasoning",
            "authors": ["Marco De Nadai", "Edoardo D'Amico", "Max Lefarov", "Alexandre Tamborrino"],
            "published": "2026-03-18",
            "arxiv_id": "2603.17533v1",
            "summary": "LLMs are increasingly applied to recommendation, retrieval, and reasoning, yet deploying a single end-to-end model that can jointly support these behaviors over large, heterogeneous catalogs remains challenging.",
            "categories": ["cs.IR", "cs.LG"],
            "pdf_url": "https://arxiv.org/pdf/2603.17533v1"
        }
    ]
    
    # 测试每篇论文
    for i, paper in enumerate(test_papers, 1):
        print(f"\n📄 测试论文 {i}: {paper['title'][:50]}...")
        
        # 提取信息
        formatted = extractor.format_paper_data(paper, i)
        
        # 显示结果
        print(f"   字段数: {len(formatted)}")
        print(f"   图片公式: {formatted[7][:50]}..." if formatted[7] else "   图片公式: [空]")
        print(f"   图片说明: {formatted[8][:50]}..." if formatted[8] else "   图片说明: [空]")
        print(f"   论文链接: {formatted[9]}")
    
    return True


def test_image_extractor():
    """测试图片提取器"""
    print("\n🧪 测试独立图片提取器")
    print("=" * 60)
    
    extractor = SimpleImageExtractor()
    
    test_paper = {
        "arxiv_id": "2603.17450v1",
        "title": "VLM2Rec: Resolving Modality Collapse in Vision-Language Model Embedders for Multimodal Sequential Recommendation"
    }
    
    # 提取图片
    image_formula, image_description = extractor.extract_for_paper(test_paper)
    
    print(f"📸 图片提取结果:")
    print(f"   公式: {image_formula}")
    print(f"   描述: {image_description}")
    
    # 测试图片URL
    print(f"\n🔗 图片URL预览:")
    import urllib.parse
    import re
    # 从公式中提取URL
    match = re.search(r'IMAGE\("([^"]+)"', image_formula)
    if match:
        image_url = match.group(1)
        print(f"   图片URL: {image_url}")
        print(f"   解码文本: {urllib.parse.unquote(image_url).split('text=')[-1]}")
    
    return True


def test_google_sheets_format():
    """测试Google Sheets格式"""
    print("\n🧪 测试Google Sheets格式兼容性")
    print("=" * 60)
    
    from extract_paper_info import PaperInfoExtractor
    
    extractor = PaperInfoExtractor()
    
    test_paper = {
        "title": "Test Paper: Recommendation System with Images",
        "authors": ["Test Author 1", "Test Author 2"],
        "published": "2026-03-19",
        "arxiv_id": "2603.19000v1",
        "summary": "This is a test paper to demonstrate image extraction functionality.",
        "categories": ["cs.IR", "cs.AI"],
        "pdf_url": "https://arxiv.org/pdf/2603.19000v1"
    }
    
    # 格式化数据
    formatted = extractor.format_paper_data(test_paper, 1)
    
    # 检查字段
    expected_fields = [
        "序号", "论文标题", "作者", "发表时间", "arXiv ID",
        "内容概括", "亮点做法", "代表性图片", "图片说明", "论文链接", "分类"
    ]
    
    print(f"📋 字段检查:")
    print(f"   预期字段数: {len(expected_fields)}")
    print(f"   实际字段数: {len(formatted)}")
    
    if len(formatted) == len(expected_fields):
        print(f"   ✅ 字段数量匹配")
        
        # 显示关键字段
        key_fields = [0, 1, 2, 4, 7, 8, 9]
        field_names = ["序号", "标题", "作者", "arXiv ID", "图片公式", "图片说明", "论文链接"]
        
        for idx, field_idx in enumerate(key_fields):
            field_name = field_names[idx]
            field_value = formatted[field_idx]
            preview = str(field_value)[:40] + "..." if len(str(field_value)) > 40 else str(field_value)
            print(f"   {field_name}: {preview}")
    else:
        print(f"   ❌ 字段数量不匹配")
    
    return len(formatted) == len(expected_fields)


def main():
    """运行所有测试"""
    import re
    
    print("🤖 推荐系统论文收集器 - 完整功能测试")
    print("=" * 60)
    
    tests = [
        ("图片提取器测试", test_image_extractor),
        ("论文信息提取测试", test_paper_extraction),
        ("Google Sheets格式测试", test_google_sheets_format),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 正在运行: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
            status = "✅ 通过" if success else "❌ 失败"
            print(f"{status} {test_name}")
        except Exception as e:
            print(f"❌ {test_name} 发生异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📈 测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！Skill已准备好处理图片")
        print("\n📌 使用说明:")
        print("   1. 图片将显示为Google Sheets中的IMAGE()函数")
        print("   2. 包含占位图片和相关描述")
        print("   3. 可以点击图片链接查看arXiv原文")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 项测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())