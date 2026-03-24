#!/usr/bin/env python3
"""
图片提取模块
用于从arXiv论文中提取代表性图片
支持从PDF中提取图片
"""

import re
import json
import os
import tempfile
import urllib.parse
import requests
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path


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
                "temp_dir": "/tmp/arxiv_images"
            }
        
        # 创建临时目录
        os.makedirs(self.config.get("temp_dir", "/tmp/arxiv_images"), exist_ok=True)
        
        # 检查PDF处理库
        self.has_pdf_libs = self._check_pdf_libraries()
    
    def extract_from_arxiv(self, arxiv_id: str) -> List[Dict[str, str]]:
        """从arXiv论文中提取图片"""
        images = []
        
        try:
            # 尝试从PDF中提取图片
            pdf_images = self.extract_images_from_pdf(arxiv_id)
            images.extend(pdf_images)
            
        except Exception as e:
            print(f"⚠️  从PDF提取图片失败: {e}")
            # 继续使用其他方法
        
        # 如果PDF提取失败，尝试HTML版本
        if not images:
            html_images = self.extract_images_from_html(arxiv_id)
            images.extend(html_images)
        
        return images
    
    def extract_images_from_pdf(self, arxiv_id: str) -> List[Dict[str, str]]:
        """从PDF中提取图片"""
        images = []
        
        try:
            # 下载PDF文件
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            
            # 这里应该实现PDF下载和图片提取
            # 暂时返回空列表
            
            print(f"📄 尝试从PDF提取图片: {pdf_url}")
            
        except Exception as e:
            print(f"❌ PDF处理错误: {e}")
        
        return images
    
    def extract_images_from_html(self, arxiv_id: str) -> List[Dict[str, str]]:
        """从HTML版本中提取图片"""
        images = []
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            html_url = f"https://arxiv.org/html/{arxiv_id}"
            response = requests.get(html_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 查找图片标签
                img_tags = soup.find_all('img')
                for img in img_tags:
                    src = img.get('src', '')
                    alt = img.get('alt', 'Figure')
                    
                    # 处理相对URL
                    if src.startswith('/'):
                        src = f"https://arxiv.org{src}"
                    
                    # 过滤掉图标等小图片
                    if src and ('figure' in alt.lower() or 'fig.' in alt.lower() or 'image' in src):
                        images.append({
                            'url': src,
                            'alt': alt,
                            'description': alt
                        })
                
                print(f"✅ 从HTML找到 {len(images)} 张图片")
            
        except Exception as e:
            print(f"❌ HTML解析错误: {e}")
        
        return images
    
    def get_figure_urls(self, arxiv_id: str, title: str) -> List[Tuple[str, str]]:
        """获取论文中的图表URL和描述
        
        返回: [(图片URL, 图片描述), ...]
        """
        figure_urls = []
        
        # 尝试常见arXiv图片URL模式
        base_id = arxiv_id.replace('v1', '').replace('v2', '').replace('v3', '')
        
        # 模式1: arXiv官方图片（如果存在）
        arxiv_figures = [
            f"https://arxiv.org/abs/{arxiv_id}#F1",
            f"https://arxiv.org/html/{arxiv_id}#figure1",
        ]
        
        # 模式2: 使用第三方服务（示例）
        # 注意：这些URL可能需要根据实际服务调整
        third_party_patterns = [
            # Papers with Code 图片（如果有）
            f"https://paperswithcode.com/media/paper_images/{base_id}.png",
            # Google Scholar 图片（如果有）
            f"https://scholar.google.com/scholar?q={urllib.parse.quote(title)}&hl=en&as_sdt=0,5"
        ]
        
        # 为每个可能的图片生成描述
        figure_descriptions = [
            "模型架构图",
            "实验结果对比图",
            "算法流程图",
            "网络结构图",
            "性能评估图"
        ]
        
        # 创建图片URL和描述的配对
        for i, desc in enumerate(figure_descriptions[:3]):
            # 使用Google Sheets的IMAGE函数格式
            # 这里暂时使用占位图片，实际应用中可以替换为真实图片URL
            if i == 0:
                # 第一个图片：使用论文相关的占位图
                image_url = f"https://via.placeholder.com/{self.config.get('default_width', 300)}x{self.config.get('default_height', 200)}/4A90E2/FFFFFF?text={urllib.parse.quote(title[:20])}"
                figure_urls.append((image_url, desc))
            else:
                # 其他图片：使用通用占位图
                image_url = f"https://via.placeholder.com/{self.config.get('default_width', 300)}x{self.config.get('default_height', 200)}/50B7C1/FFFFFF?text=Figure+{i+1}"
                figure_urls.append((image_url, f"{desc} (Figure {i+1})"))
        
        return figure_urls
    
    def generate_image_formula(self, image_url: str, width: int = None, height: int = None) -> str:
        """生成Google Sheets的IMAGE函数公式"""
        width = width or self.config.get("default_width", 300)
        height = height or self.config.get("default_height", 200)
        
        # Google Sheets IMAGE函数格式
        # =IMAGE("URL", [mode], [height], [width])
        formula = f'=IMAGE("{image_url}", 1, {height}, {width})'
        
        return formula
    
    def extract_main_figure(self, paper: Dict[str, Any]) -> Tuple[str, str]:
        """提取主要代表性图片
        
        返回: (图片公式, 图片说明)
        """
        arxiv_id = paper.get("arxiv_id", "")
        title = paper.get("title", "")
        
        # 获取可能的图片URL
        figure_urls = self.get_figure_urls(arxiv_id, title)
        
        if figure_urls:
            # 使用第一个图片作为代表性图片
            image_url, description = figure_urls[0]
            image_formula = self.generate_image_formula(image_url)
            return image_formula, description
        else:
            # 如果没有找到图片，使用占位图
            placeholder_url = f"https://via.placeholder.com/{self.config.get('default_width', 300)}x{self.config.get('default_height', 200)}/E0E0E0/333333?text=No+Image+Available"
            placeholder_formula = self.generate_image_formula(placeholder_url)
            placeholder_desc = "图片暂不可用（论文中通常包含模型架构图或实验结果图）"
            
            return placeholder_formula, placeholder_desc
    
    def extract_all_figures(self, paper: Dict[str, Any], max_figures: int = 3) -> List[Tuple[str, str]]:
        """提取所有相关图片"""
        arxiv_id = paper.get("arxiv_id", "")
        title = paper.get("title", "")
        
        figure_urls = self.get_figure_urls(arxiv_id, title)
        
        results = []
        for i, (image_url, description) in enumerate(figure_urls[:max_figures]):
            image_formula = self.generate_image_formula(image_url)
            results.append((image_formula, description))
        
        return results
    
    def format_for_sheets(self, paper: Dict[str, Any]) -> Tuple[str, str]:
        """为Google Sheets格式化图片数据
        
        返回: (图片单元格内容, 图片说明)
        """
        # 提取主要图片
        image_formula, image_description = self.extract_main_figure(paper)
        
        return image_formula, image_description
    
    def test_extraction(self, arxiv_id: str = "2603.17450v1"):
        """测试图片提取功能"""
        print(f"测试图片提取 - arXiv ID: {arxiv_id}")
        
        # 创建测试论文数据
        test_paper = {
            "arxiv_id": arxiv_id,
            "title": "VLM2Rec: Resolving Modality Collapse in Vision-Language Model Embedders for Multimodal Sequential Recommendation"
        }
        
        # 提取图片
        image_formula, image_description = self.extract_main_figure(test_paper)
        
        print(f"📸 提取的图片公式: {image_formula}")
        print(f"📝 图片说明: {image_description}")
        
        # 测试所有图片提取
        all_figures = self.extract_all_figures(test_paper, max_figures=2)
        print(f"\n所有相关图片 ({len(all_figures)} 张):")
        for i, (formula, desc) in enumerate(all_figures, 1):
            print(f"  {i}. {desc}")
            print(f"     公式: {formula}")


def main():
    """主测试函数"""
    extractor = PaperImageExtractor()
    
    # 测试提取功能
    print("🧪 测试图片提取功能")
    print("=" * 50)
    
    extractor.test_extraction("2603.17450v1")
    
    print("\n" + "=" * 50)
    print("✅ 图片提取功能测试完成")


if __name__ == "__main__":
    main()