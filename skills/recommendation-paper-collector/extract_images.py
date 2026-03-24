#!/usr/bin/env python3
"""
增强版图片提取模块
集成PDF图片提取功能
"""

import re
import json
import os
import tempfile
import urllib.parse
import requests
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("⚠️  PyMuPDF不可用，PDF图片提取功能受限")


class EnhancedPaperImageExtractor:
    def __init__(self, config_path: str = None):
        """初始化图片提取器"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "image_sources": {
                    "arxiv_pdf": True,
                    "arxiv_html": True,
                    "placeholder": True
                },
                "image_formats": ["png", "jpg", "jpeg", "gif", "svg"],
                "default_width": 300,
                "default_height": 200,
                "pdf_extraction": {
                    "enabled": True,
                    "min_width": 100,
                    "min_height": 100,
                    "max_images": 3,
                    "output_dir": "/tmp/arxiv_images"
                }
            }
        
        # 创建输出目录
        os.makedirs(self.config["pdf_extraction"]["output_dir"], exist_ok=True)
    
    def download_arxiv_pdf(self, arxiv_id: str) -> Optional[str]:
        """下载arXiv论文PDF"""
        try:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            
            print(f"📥 下载arXiv PDF: {pdf_url}")
            
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            # 保存到临时文件
            temp_dir = tempfile.mkdtemp(prefix="arxiv_pdf_")
            pdf_path = os.path.join(temp_dir, f"{arxiv_id}.pdf")
            
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ PDF下载成功: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            print(f"❌ PDF下载失败: {e}")
            return None
    
    def extract_images_from_pdf(self, pdf_path: str, arxiv_id: str) -> List[Dict[str, Any]]:
        """从PDF中提取图片"""
        images = []
        
        if not HAS_PYMUPDF:
            print("⚠️  PyMuPDF未安装，无法提取PDF图片")
            return images
        
        try:
            doc = fitz.open(pdf_path)
            pdf_config = self.config["pdf_extraction"]
            
            print(f"📄 处理PDF: {pdf_path}, 共 {len(doc)} 页")
            
            seen_hashes = set()
            image_count = 0
            
            for page_num in range(len(doc)):
                if image_count >= pdf_config["max_images"]:
                    break
                    
                page = doc.load_page(page_num)
                img_list = page.get_images(full=True)
                
                for img_index, img in enumerate(img_list, 1):
                    xref = img[0]
                    
                    try:
                        base_image = doc.extract_image(xref)
                        image_data = base_image.get("image")
                        ext = base_image.get("ext", "png")
                        width = base_image.get("width", 0)
                        height = base_image.get("height", 0)
                        
                        # 过滤小图片
                        min_w = pdf_config["min_width"]
                        min_h = pdf_config["min_height"]
                        if width < min_w or height < min_h:
                            continue
                        
                        # 去重
                        img_hash = hashlib.sha256(image_data).hexdigest()
                        if img_hash in seen_hashes:
                            continue
                        
                        seen_hashes.add(img_hash)
                        image_count += 1
                        
                        # 保存图片
                        img_filename = f"{arxiv_id}_p{page_num+1}_img{image_count}.{ext}"
                        img_path = os.path.join(pdf_config["output_dir"], img_filename)
                        
                        with open(img_path, 'wb') as f:
                            f.write(image_data)
                        
                        # 创建图片记录
                        image_info = {
                            "arxiv_id": arxiv_id,
                            "page": page_num + 1,
                            "index": image_count,
                            "filename": img_filename,
                            "path": img_path,
                            "width": width,
                            "height": height,
                            "format": ext,
                            "hash": img_hash,
                            "description": f"Figure {image_count} from page {page_num + 1} ({width}x{height})",
                            "type": "pdf_extracted"
                        }
                        
                        images.append(image_info)
                        print(f"🖼️  提取PDF图片: {img_filename}")
                        
                        if image_count >= pdf_config["max_images"]:
                            break
                            
                    except Exception as e:
                        print(f"⚠️  提取图片失败: {e}")
                        continue
                
                if image_count >= pdf_config["max_images"]:
                    break
            
            doc.close()
            print(f"✅ 从PDF提取了 {len(images)} 张图片")
            
        except Exception as e:
            print(f"❌ PDF处理失败: {e}")
        
        return images
    
    def get_figure_urls(self, arxiv_id: str, title: str) -> List[Tuple[str, str]]:
        """获取论文中的图表URL和描述"""
        figure_info = []
        
        # 1. 尝试从PDF提取图片
        if self.config["image_sources"]["arxiv_pdf"] and HAS_PYMUPDF:
            try:
                pdf_path = self.download_arxiv_pdf(arxiv_id)
                if pdf_path:
                    pdf_images = self.extract_images_from_pdf(pdf_path, arxiv_id)
                    
                    for img in pdf_images:
                        # 由于本地图片无法直接在Google Sheets中显示
                        # 我们使用占位图+超链接的方式
                        placeholder_url = self.create_placeholder_image(title, img["description"])
                        formula = self.generate_image_formula(placeholder_url)
                        figure_info.append((formula, img["description"]))
                        
                        # 清理临时文件
                        os.remove(pdf_path)
                        os.rmdir(os.path.dirname(pdf_path))
                        
                        # 只取第一张图片
                        break
            except Exception as e:
                print(f"⚠️  PDF提取失败: {e}")
        
        # 2. 如果PDF提取失败，使用占位图
        if not figure_info and self.config["image_sources"]["placeholder"]:
            placeholder_url = self.create_placeholder_image(title, "Model Architecture")
            formula = self.generate_image_formula(placeholder_url)
            figure_info.append((formula, "模型架构图（图片提取中）"))
        
        return figure_info
    
    def create_placeholder_image(self, title: str, description: str) -> str:
        """创建占位图片URL"""
        # 使用via.placeholder.com生成占位图
        width = self.config["default_width"]
        height = self.config["default_height"]
        
        # 简化的标题文本
        short_title = title[:30].replace(":", "").replace(" ", "+")
        short_desc = description[:20].replace(" ", "+")
        
        placeholder_url = (
            f"https://via.placeholder.com/{width}x{height}/4A90E2/FFFFFF"
            f"?text={urllib.parse.quote(short_title + '%0A' + short_desc)}"
        )
        
        return placeholder_url
    
    def generate_image_formula(self, image_url: str, width: int = None, height: int = None) -> str:
        """生成Google Sheets的IMAGE函数公式"""
        width = width or self.config["default_width"]
        height = height or self.config["default_height"]
        
        # Google Sheets IMAGE函数格式
        # =IMAGE("URL", [mode], [height], [width])
        formula = f'=IMAGE("{image_url}", 1, {height}, {width})'
        
        return formula
    
    def extract_main_figure(self, paper: Dict[str, Any]) -> Tuple[str, str]:
        """提取主要代表性图片"""
        arxiv_id = paper.get("arxiv_id", "")
        title = paper.get("title", "")
        
        # 获取图片信息
        figure_info = self.get_figure_urls(arxiv_id, title)
        
        if figure_info:
            # 使用第一个图片
            image_formula, description = figure_info[0]
            return image_formula, description
        else:
            # 使用默认占位图
            placeholder_url = self.create_placeholder_image(title, "Figure Not Available")
            placeholder_formula = self.generate_image_formula(placeholder_url)
            placeholder_desc = "图片暂不可用（论文中通常包含模型架构图）"
            
            return placeholder_formula, placeholder_desc
    
    def format_for_sheets(self, paper: Dict[str, Any]) -> Tuple[str, str]:
        """为Google Sheets格式化图片数据"""
        return self.extract_main_figure(paper)
    
    def test_extraction(self, arxiv_id: str = "2603.17450v1"):
        """测试图片提取功能"""
        print(f"🧪 测试增强版图片提取 - arXiv ID: {arxiv_id}")
        
        test_paper = {
            "arxiv_id": arxiv_id,
            "title": "VLM2Rec: Resolving Modality Collapse in Vision-Language Model Embedders"
        }
        
        # 提取图片
        image_formula, image_description = self.extract_main_figure(test_paper)
        
        print(f"📸 提取的图片公式: {image_formula}")
        print(f"📝 图片说明: {image_description}")
        
        # 测试PDF提取（如果有）
        if HAS_PYMUPDF:
            print(f"\n📄 PDF提取能力: 可用")
        else:
            print(f"\n📄 PDF提取能力: 不可用（需要安装PyMuPDF）")


def main():
    """主测试函数"""
    extractor = EnhancedPaperImageExtractor()
    
    print("🧪 测试增强版图片提取功能")
    print("=" * 60)
    
    extractor.test_extraction("2603.17450v1")
    
    print("\n" + "=" * 60)
    print("✅ 增强版图片提取功能测试完成")
    
    # 提供安装建议
    if not HAS_PYMUPDF:
        print("\n💡 安装建议:")
        print("pip install PyMuPDF")
        print("或")
        print("pip install fitz")


if __name__ == "__main__":
    main()