#!/usr/bin/env python3
"""
测试脚本 - 验证推荐系统论文收集器Skill功能
"""

import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def test_components():
    """测试各个组件"""
    print("🧪 开始测试推荐系统论文收集器组件...")
    
    # 测试搜索组件
    try:
        from search_arxiv import ArXivSearcher
        searcher = ArXivSearcher()
        print("✅ arXiv搜索组件加载成功")
    except Exception as e:
        print(f"❌ arXiv搜索组件加载失败: {e}")
        return False
    
    # 测试提取组件
    try:
        from extract_paper_info import PaperInfoExtractor
        extractor = PaperInfoExtractor()
        print("✅ 论文信息提取组件加载成功")
    except Exception as e:
        print(f"❌ 论文信息提取组件加载失败: {e}")
        return False
    
    # 测试写入组件
    try:
        from write_to_sheets import GoogleSheetsWriter
        writer = GoogleSheetsWriter()
        print("✅ Google Sheets写入组件加载成功")
    except Exception as e:
        print(f"❌ Google Sheets写入组件加载失败: {e}")
        return False
    
    # 测试主程序
    try:
        from main import RecommendationPaperCollector
        collector = RecommendationPaperCollector()
        print("✅ 主程序组件加载成功")
    except Exception as e:
        print(f"❌ 主程序组件加载失败: {e}")
        return False
    
    return True

def test_config_files():
    """测试配置文件"""
    print("\n📁 检查配置文件...")
    
    required_files = [
        "defaults.json",
        "search_arxiv.py",
        "extract_paper_info.py",
        "write_to_sheets.py",
        "main.py",
        "README.md"
    ]
    
    all_ok = True
    for file in required_files:
        path = os.path.join(current_dir, file)
        if os.path.exists(path):
            print(f"✅ {file} 存在")
        else:
            print(f"❌ {file} 缺失")
            all_ok = False
    
    return all_ok

def test_sample_data():
    """测试样本数据处理"""
    print("\n📊 测试样本数据处理...")
    
    from extract_paper_info import PaperInfoExtractor
    
    # 创建样本数据
    sample_paper = {
        "title": "Test Paper: A Novel Approach for Recommendation Systems",
        "authors": ["Author One", "Author Two", "Author Three"],
        "published": "2026-03-19",
        "arxiv_id": "2603.19000v1",
        "summary": "This paper proposes a novel approach for recommendation systems that combines multiple techniques to improve accuracy and efficiency.",
        "categories": ["cs.IR", "cs.LG"],
        "pdf_url": "https://arxiv.org/pdf/2603.19000v1"
    }
    
    extractor = PaperInfoExtractor()
    
    try:
        # 测试内容概括提取
        summary = extractor.extract_content_summary(sample_paper)
        print(f"✅ 内容概括提取: {summary[:50]}...")
        
        # 测试亮点做法提取
        highlights = extractor.extract_highlights(sample_paper)
        print(f"✅ 亮点做法提取: {highlights[:50]}...")
        
        # 测试图片说明提取
        image_desc = extractor.extract_image_description(sample_paper)
        print(f"✅ 图片说明提取: {image_desc[:50]}...")
        
        # 测试完整格式化
        formatted = extractor.format_paper_data(sample_paper, 1)
        print(f"✅ 数据格式化: 共{len(formatted)}个字段")
        
        return True
        
    except Exception as e:
        print(f"❌ 样本数据处理失败: {e}")
        return False

def test_google_sheets_connection():
    """测试Google Sheets连接"""
    print("\n🔗 测试Google Sheets连接...")
    
    from write_to_sheets import GoogleSheetsWriter
    
    writer = GoogleSheetsWriter()
    
    try:
        # 测试凭据获取
        creds = writer.get_credentials()
        if creds:
            print("✅ Google API凭证获取成功")
        else:
            print("⚠️  Google API凭证未找到，需要配置")
            return True  # 这不是致命错误
            
        # 测试ID提取
        test_url = "https://docs.google.com/spreadsheets/d/1TW-NubPwQCrhVvV1maV4KQRYfjoJ39e1V_L_Tx6oPrQ/edit"
        sheet_id = writer.extract_spreadsheet_id(test_url)
        if sheet_id:
            print(f"✅ Spreadsheet ID提取成功: {sheet_id}")
        else:
            print("❌ Spreadsheet ID提取失败")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Google Sheets连接测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 推荐系统论文收集器 - 功能测试")
    print("=" * 60)
    
    tests = [
        ("组件加载测试", test_components),
        ("配置文件测试", test_config_files),
        ("样本数据处理测试", test_sample_data),
        ("Google Sheets连接测试", test_google_sheets_connection),
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
        print("\n🎉 所有测试通过！Skill已准备就绪")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 项测试失败，请检查配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())