#!/usr/bin/env python3
"""
演示脚本 - 展示增强版推荐系统论文收集器（支持PDF图片提取）
"""

import os
import sys
import json

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def demo_pdf_image_extraction():
    """演示PDF图片提取功能"""
    print("🎬 演示：增强版推荐系统论文收集器")
    print("=" * 60)
    
    # 测试PDF提取能力
    try:
        import fitz
        print("✅ PyMuPDF (fitz) 已安装，支持PDF图片提取")
    except ImportError:
        print("⚠️  PyMuPDF 未安装，PDF图片提取功能受限")
        print("   请安装: pip install PyMuPDF")
    
    print("\n📊 测试论文处理流程:")
    
    # 创建测试论文数据
    test_paper = {
        "title": "VLM2Rec: Resolving Modality Collapse in Vision-Language Model Embedders for Multimodal Sequential Recommendation",
        "authors": ["Junyoung Kim", "Woojoo Kim", "Jaehyung Lim", "Dongha Kim", "Hwanjo Yu"],
        "published": "2026-03-18",
        "arxiv_id": "2603.17450v1",
        "summary": "Sequential Recommendation (SR) in multimodal settings typically relies on small frozen pretrained encoders...",
        "categories": ["cs.IR", "cs.AI"],
        "pdf_url": "https://arxiv.org/pdf/2603.17450v1"
    }
    
    # 导入论文信息提取器
    from extract_paper_info import PaperInfoExtractor
    
    # 创建提取器
    extractor = PaperInfoExtractor()
    
    # 提取和格式化论文信息
    print("\n📝 提取论文信息:")
    formatted_data = extractor.format_paper_data(test_paper, 1)
    
    # 显示提取结果
    fields = [
        "序号", "论文标题", "作者", "发表时间", "arXiv ID",
        "内容概括", "亮点做法", "代表性图片", "图片说明", "论文链接", "分类"
    ]
    
    print("\n📋 格式化后的数据:")
    for i, (field, value) in enumerate(zip(fields, formatted_data)):
        if field == "代表性图片" and value and value.startswith("=IMAGE"):
            print(f"  {field}: {value[:50]}...")
        elif field == "图片说明":
            print(f"  {field}: {value}")
        elif field in ["内容概括", "亮点做法"]:
            print(f"  {field}: {value[:50]}...")
        else:
            print(f"  {field}: {value}")
    
    # 测试图片提取器
    print("\n📸 测试图片提取器:")
    if extractor.has_image_extractor:
        try:
            # 直接测试图片提取
            from extract_images import EnhancedPaperImageExtractor
            img_extractor = EnhancedPaperImageExtractor()
            
            formula, description = img_extractor.extract_main_figure(test_paper)
            print(f"  图片公式: {formula[:60]}...")
            print(f"  图片说明: {description}")
            
        except Exception as e:
            print(f"  ❌ 图片提取测试失败: {e}")
    else:
        print("  ⚠️  图片提取器不可用")
    
    print("\n" + "=" * 60)
    print("✅ 演示完成")
    print("\n💡 功能亮点:")
    print("1. 📄 支持从arXiv PDF直接提取图片")
    print("2. 🖼️  自动生成Google Sheets IMAGE函数公式")
    print("3. 📊 完整的论文信息提取和格式化")
    print("4. 🔗 智能图片说明生成")
    
    return formatted_data

def test_google_sheets_integration():
    """测试Google Sheets集成"""
    print("\n🔗 测试Google Sheets集成:")
    
    try:
        from write_to_sheets import GoogleSheetsWriter
        
        # 创建写入器
        writer = GoogleSheetsWriter()
        
        # 测试凭据
        creds = writer.get_credentials()
        if creds:
            print("✅ Google API凭证有效")
        else:
            print("⚠️  Google API凭证需要配置")
        
        # 测试URL解析
        test_url = "https://docs.google.com/spreadsheets/d/1TW-NubPwQCrhVvV1maV4KQRYfjoJ39e1V_L_Tx6oPrQ/edit"
        sheet_id = writer.extract_spreadsheet_id(test_url)
        if sheet_id:
            print(f"✅ Spreadsheet ID提取成功: {sheet_id}")
        
    except Exception as e:
        print(f"❌ Google Sheets测试失败: {e}")

def main():
    """主函数"""
    print("🤖 增强版推荐系统论文收集器演示")
    print("版本: 1.1.0 (支持PDF图片提取)")
    print("=" * 60)
    
    # 演示PDF图片提取
    demo_pdf_image_extraction()
    
    # 测试Google Sheets集成
    test_google_sheets_integration()
    
    print("\n" + "=" * 60)
    print("🎯 使用建议:")
    print("1. 安装依赖: pip install PyMuPDF google-auth google-api-python-client")
    print("2. 配置Google API凭证")
    print("3. 运行: python main.py --days 7 --max 10 --clear")
    print("4. 查看Google Sheets结果")
    
    print("\n🚀 开始使用:")
    print("cd /root/agent/skills/recommendation-paper-collector")
    print("python main.py --help")


if __name__ == "__main__":
    main()