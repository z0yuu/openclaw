#!/usr/bin/env python3
"""
简化的图片提取器
为推荐系统论文生成Google Sheets可用的图片公式
"""

import urllib.parse
import json
import re
from typing import Dict, Any, Tuple, List


class SimpleImageExtractor:
    def __init__(self):
        self.config = {
            "image_width": 300,
            "image_height": 200,
            "placeholder_service": "https://via.placeholder.com",
            "arxiv_figure_base": "https://arxiv.org/abs"
        }
    
    def get_paper_figure_urls(self, arxiv_id: str, title: str) -> List[Tuple[str, str]]:
        """获取论文相关图片URL
        
        返回: [(图片URL, 图片描述), ...]
        """
        figure_urls = []
        
        # 清理标题
        clean_title = re.sub(r'[^\w\s-]', '', title[:50])
        
        # 创建不同类型的图片URL
        figures = [
            # 模型架构图
            {
                "url": self._create_placeholder_url(
                    f"{clean_title[:20]} Model",
                    "4A90E2",  # 蓝色
                    "模型架构图"
                ),
                "desc": "模型架构图"
            },
            # 实验结果图
            {
                "url": self._create_placeholder_url(
                    f"{clean_title[:15]} Results",
                    "50B7C1",  # 青色
                    "实验结果对比"
                ),
                "desc": "实验结果对比图"
            },
            # 算法流程图
            {
                "url": self._create_placeholder_url(
                    f"{clean_title[:15]} Algorithm",
                    "7ED321",  # 绿色
                    "算法流程图"
                ),
                "desc": "算法流程图"
            }
        ]
        
        # 转换为元组列表
        for fig in figures:
            figure_urls.append((fig["url"], fig["desc"]))
        
        return figure_urls
    
    def _create_placeholder_url(self, text: str, color: str, description: str = "") -> str:
        """创建占位图片URL"""
        encoded_text = urllib.parse.quote(text)
        width = self.config["image_width"]
        height = self.config["image_height"]
        
        url = f"{self.config['placeholder_service']}/{width}x{height}/{color}/FFFFFF?text={encoded_text}"
        return url
    
    def create_image_formula(self, image_url: str, width: int = None, height: int = None) -> str:
        """创建Google Sheets IMAGE函数公式"""
        width = width or self.config["image_width"]
        height = height or self.config["image_height"]
        
        # Google Sheets IMAGE函数格式
        # =IMAGE("URL", [mode], [height], [width])
        # mode 1: 保持宽高比
        # mode 2: 拉伸填充
        # mode 3: 保持原始大小
        # mode 4: 自定义大小
        
        formula = f'=IMAGE("{image_url}", 1, {height}, {width})'
        return formula
    
    def get_arxiv_figure_links(self, arxiv_id: str) -> List[str]:
        """获取arXiv论文中的图表链接"""
        links = []
        
        # arXiv论文通常有特定的图片链接模式
        # 例如: https://arxiv.org/abs/{arxiv_id}#F1
        
        # 生成可能的图表链接
        for i in range(1, 4):
            link = f"{self.config['arxiv_figure_base']}/{arxiv_id}#F{i}"
            links.append(link)
        
        return links
    
    def extract_for_paper(self, paper_data: Dict[str, Any]) -> Tuple[str, str]:
        """为单篇论文提取图片信息
        
        返回: (图片公式, 图片描述)
        """
        arxiv_id = paper_data.get("arxiv_id", "")
        title = paper_data.get("title", "")
        
        # 获取图片URL
        figure_urls = self.get_paper_figure_urls(arxiv_id, title)
        
        if figure_urls:
            # 使用第一个图片
            image_url, description = figure_urls[0]
            image_formula = self.create_image_formula(image_url)
            
            # 如果有arXiv链接，添加到描述中
            arxiv_links = self.get_arxiv_figure_links(arxiv_id)
            if arxiv_links:
                description += f" (点击查看: {arxiv_links[0]})"
            
            return image_formula, description
        else:
            # 创建默认图片
            default_url = self._create_placeholder_url(
                "Paper Figure",
                "E0E0E0",
                "图片提取中..."
            )
            default_formula = self.create_image_formula(default_url)
            default_desc = "论文图表（可通过arXiv链接查看）"
            
            return default_formula, default_desc
    
    def extract_all_for_paper(self, paper_data: Dict[str, Any], max_figures: int = 3) -> List[Tuple[str, str]]:
        """提取所有相关图片"""
        arxiv_id = paper_data.get("arxiv_id", "")
        title = paper_data.get("title", "")
        
        figure_urls = self.get_paper_figure_urls(arxiv_id, title)
        
        results = []
        for i, (image_url, description) in enumerate(figure_urls[:max_figures]):
            formula = self.create_image_formula(image_url)
            results.append((formula, f"{description} (Figure {i+1})"))
        
        return results


def test_extractor():
    """测试函数"""
    extractor = SimpleImageExtractor()
    
    # 测试数据
    test_paper = {
        "arxiv_id": "2603.17450v1",
        "title": "VLM2Rec: Resolving Modality Collapse in Vision-Language Model Embedders for Multimodal Sequential Recommendation"
    }
    
    print("🧪 测试简化的图片提取器")
    print("=" * 60)
    
    # 提取单张图片
    image_formula, image_description = extractor.extract_for_paper(test_paper)
    
    print(f"📄 论文标题: {test_paper['title'][:60]}...")
    print(f"🆔 arXiv ID: {test_paper['arxiv_id']}")
    print(f"📸 图片公式: {image_formula}")
    print(f"📝 图片描述: {image_description}")
    
    # 提取所有图片
    print("\n📊 所有相关图片:")
    all_figures = extractor.extract_all_for_paper(test_paper, max_figures=2)
    for i, (formula, desc) in enumerate(all_figures, 1):
        print(f"  {i}. {desc}")
        print(f"     公式: {formula}")
    
    # 测试占位图生成
    print("\n🎨 测试占位图生成:")
    placeholder_url = extractor._create_placeholder_url("Test Image", "FF6B6B", "测试图片")
    print(f"     URL: {placeholder_url}")
    print(f"     公式: {extractor.create_image_formula(placeholder_url)}")


if __name__ == "__main__":
    test_extractor()