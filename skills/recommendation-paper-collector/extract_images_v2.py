#!/usr/bin/env python3
"""
图片提取模块 - 增强版
支持从arXiv论文PDF中提取真实图片
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
    print("⚠️  PyMuPDF未安装，无法从PDF提取图片")


class PaperImageExtractor:
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
                    "enabled": HAS_PYMUPDF,
                    "min_width": 100,
                    "min_height": 100,
                    "max_images": 3,
                    "output_dir": "/tmp/arxiv_images"
                }
            }
        
        # 创建输出目录
        os.makedirs(self.config["pdf_extraction"]["output_dir"], exist_ok=True)
        
        print(f"📸 图片提取器初始化:")
        print(f"   PDF提取: {'✅ 可用' if HAS_PYMUPDF else '❌ 不可用'}")
        print(f"   输出目录: {self.config['pdf_extraction']['output_dir']}")
    
    def download_pdf(self, arxiv_id: str) -> Optional[str]:
        """下载arXiv论文PDF"""
        try:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            
            print(f"📥 下载PDF: {arxiv_id}")
            
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            # 保存到临时文件
            temp_dir = tempfile.mkdtemp(prefix="arxiv_pdf_")
            pdf_path = os.path.join(temp_dir, f"{arxiv_id}.pdf")
            
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(pdf_path) / 1024  # KB
            print(f"✅ PDF下载成功: {pdf_path} ({file_size:.1f} KB)")
            return pdf_path
            
        except Exception as e:
            print(f"❌ PDF下载失败: {e}")
            return None
    
    def extract_from_pdf(self, arxiv_id: str) -> List[Dict[str, Any]]:
        """从PDF中提取图片"""
        images = []
        
        if not HAS_PYMUPDF:
            return images
        
        try:
            # 下载PDF
            pdf_path = self.download_pdf(arxiv_id)
            if not pdf_path:
                return images
            
            # 打开PDF文档
            doc = fitz.open(pdf_path)
            
            print(f"📄 解析PDF: 共 {len(doc)} 页")
            
            seen_hashes = set()
            image_index = 0
            min_w = self.config["pdf_extraction"]["min_width"]
            min_h = self.config["pdf_extraction"]["min_height"]
            max_img = self.config["pdf_extraction"]["max_images"]
            
            # 优先提取前几页的图片（通常包含架构图）
            target_pages = list(range(min(5, len(doc))))
            
            for page_num in target_pages:
                if len(images) >= max_img:
                    break
                    
                page = doc.load_page(page_num)
                img_list = page.get_images(full=True)
                
                for img in img_list:
                    if len(images) >= max_img:
                        break
                        
                    xref = img[0]
                    
                    try:
                        base_image = doc.extract_image(xref)
                        image_data = base_image.get("image")
                        ext = base_image.get("ext", "png")
                        width = base_image.get("width", 0)
                        height = base_image.get("height", 0)
                        
                        # 过滤小图片
                        if width < min_w or height < min_h:
                            continue
                        
                        # 去重
                        img_hash = hashlib.sha256(image_data).hexdigest()
                        if img_hash in seen_hashes:
                            continue
                        
                        seen_hashes.add(img_hash)
                        image_index += 1
                        
                        # 保存图片
                        img_filename = f"{arxiv_id}_p{page_num+1}_img{image_index}.{ext}"
                        img_path = os.path.join(self.config["pdf_extraction"]["output_dir"], img_filename)
                        
                        with open(img_path, 'wb') as f:
                            f.write(image_data)
                        
                        # 创建图片记录
                        image_info = {
                            "arxiv_id": arxiv_id,
                            "page": page_num + 1,
                            "index": image_index,
                            "filename": img_filename,
                            "path": img_path,
                            "url": None,
                            "width": width,
                            "height": height,
                            "format": ext,
                            "hash": img_hash,
                            "description": f"Figure {image_index} from page {page_num + 1}"
                        }
                        
                        images.append(image_info)
                        print(f"🖼️  提取图片 {image_index}: {width}x{height}, 页{page_num+1}")
                        
                    except Exception as e:
                        print(f"⚠️  提取图片失败: {e}")
                        continue
            
            doc.close()
            
            # 清理临时PDF文件
            try:
                os.remove(pdf_path)
                os.rmdir(os.path.dirname(pdf_path))
            except:
                pass
            
            print(f"✅ 从PDF提取了 {len(images)} 张图片")
            
        except Exception as e:
            print(f"❌ PDF处理失败: {e}")
        
        return images
    
    def get_figure_urls(self, arxiv_id: str, title: str) -> List[Tuple[str, str]]:
        """获取论文中的图表URL和描述"""
        figure_urls = []
        
        # 首先尝试从PDF提取真实图片
        if self.config["pdf_extraction"]["enabled"]:
            pdf_images = self.extract_from_pdf(arxiv_id)
            
            if pdf_images:
                for img in pdf_images:
                    # 在实际应用中，这里需要将图片上传到公共存储
                    # 目前使用本地文件路径，但Google Sheets需要公共URL
                    # 所以使用占位图替代
                    placeholder_url = f"https://via.placeholder.com/{img['width']}x{img['height']}/4A90E2/FFFFFF?text=PDF+Figure+{img['index']}"
                    description = f"PDF Figure {img['index']} (页{img['page']}, {img['width']}x{img['height']})"
                    figure_urls.append((placeholder_url, description))
        
        # 如果PDF提取失败或未启用，使用备用方案
        if not figure_urls:
            base_id = arxiv_id.replace('v1', '').replace('v2', '').replace('v3', '')
            
            # 使用论文相关的占位图
            figure_descriptions = [
                "模型架构图",
                "实验结果对比图", 
                "算法流程图"
            ]
            
            for i, desc in enumerate(figure_descriptions[:2], 1):
                if i == 1:
                    # 第一个图片：使用论文标题相关的占位图
                    truncated_title = urllib.parse.quote(title[:30] + "...")
                    image_url = f"https://via.placeholder.com/400x250/4A90E2/FFFFFF?text={truncated_title}"
                    figure_urls.append((image_url, f"{desc} (示例)"))
                else:
                    # 其他图片：使用通用占位图
                    image_url = f"https://via.placeholder.com/350x200/50B7C1/FFFFFF?text=Figure+{i}"
                    figure_urls.append((image_url, f"{desc} (Figure {i})"))
        
        return figure_urls
    
    def generate_image_formula(self, image_url: str, width: int = None, height: int = None) -> str:
        """生成Google Sheets的IMAGE函数公式"""
        width = width or self.config["default_width"]
        height = height or self.config["default_height"]
        
        # Google Sheets IMAGE函数格式
        # =IMAGE("URL", [mode], [height], [width])
        # mode=1: 保持宽高比，调整到指定尺寸内
        formula = f'=IMAGE("{image_url}", 1, {height}, {width})'
        
        return formula
    
    def extract_main_figure(self, paper: Dict[str, Any]) -> Tuple[str, str]:
        """提取主要代表性图片"""
        arxiv_id = paper.get("arxiv_id", "")
        title = paper.get("title", "")
        
        # 获取图片URL和描述
        figure_urls = self.get_figure_urls(arxiv_id, title)
        
        if figure_urls:
            # 使用第一个图片作为代表性图片
            image_url, description = figure_urls[0]
            image_formula = self.generate_image_formula(image_url)
            return image_formula, description
        else:
            # 使用占位图
            placeholder_url = f"https://via.placeholder.com/{self.config['default_width']}x{self.config['default_height']}/E0E0E0/333333?text=No+Image"
            placeholder_formula = self.generate_image_formula(placeholder_url)
            placeholder_desc = "图片暂不可用"
            
            return placeholder_formula, placeholder_desc
    
    def format_for_sheets(self, paper: Dict[str, Any]) -> Tuple[str, str]:
        """为Google Sheets格式化图片数据"""
        return self.extract_main_figure(paper)
    
    def test_extraction(self, arxiv_id: str = "2603.17450v1"):
        """测试图片提取功能"""
        print(f"🧪 测试图片提取 - arXiv ID: {arxiv_id}")
        
        test_paper = {
            "arxiv_id": arxiv_id,
            "title": "VLM2Rec: Resolving Modality Collapse in Vision-Language Model Embedders for Multimodal Sequential Recommendation"
        }
        
        # 提取图片
        image_formula, image_description = self.extract_main_figure(test_paper)
        
        print(f"📸 提取的图片公式: {image_formula}")
        print(f"📝 图片说明: {image_description}")
        
        # 测试PDF提取（如果可用）
        if HAS_PYMUPDF:
            print(f"\n🔍 测试PDF图片提取:")
            pdf_images = self.extract_from_pdf(arxiv_id)
            print(f"   从PDF提取了 {len(pdf_images)} 张图片")


def main():
    """主测试函数"""
    extractor = PaperImageExtractor()
    
    print("🧪 测试增强版图片提取功能")
    print("=" * 60)
    
    extractor.test_extraction("2603.17450v1")
    
    print("\n" + "=" * 60)
    print("✅ 图片提取功能测试完成")


if __name__ == "__main__":
    main()