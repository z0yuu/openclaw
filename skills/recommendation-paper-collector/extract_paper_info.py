#!/usr/bin/env python3
"""
论文信息提取模块
从arXiv论文数据中提取和格式化关键信息
"""

import re
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class PaperInfoExtractor:
    def __init__(self, config_path: str = None):
        """初始化提取器"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "translation": {"enabled": True, "target_language": "zh"},
                "format_options": {
                    "truncate_summary": True,
                    "max_summary_length": 500,
                    "include_images": True,
                    "image_width": 300,
                    "image_height": 200
                }
            }
        
        # 尝试导入增强版图片提取器（支持PDF图片提取）
        try:
            from extract_images import EnhancedPaperImageExtractor
            self.image_extractor = EnhancedPaperImageExtractor(config_path)
            self.has_image_extractor = True
            print("✅ 使用增强版图片提取器（支持PDF图片提取）")
        except ImportError as e:
            print(f"⚠️  增强版图片提取器导入失败: {e}")
            # 尝试旧版图片提取器
            try:
                from extract_images import PaperImageExtractor
                self.image_extractor = PaperImageExtractor(config_path)
                self.has_image_extractor = True
                print("✅ 使用旧版图片提取器")
            except ImportError:
                self.has_image_extractor = False
                print("⚠️  所有图片提取器都不可用，将使用文本描述代替图片")
    
    def extract_content_summary(self, paper: Dict[str, Any]) -> str:
        """提取内容概括"""
        summary = paper.get("summary", "")
        
        # 清理摘要文本
        summary = re.sub(r'\s+', ' ', summary).strip()
        
        if self.config["translation"]["enabled"]:
            # 这里可以调用翻译API，暂时使用简单处理
            target_lang = self.config["translation"]["target_language"]
            if target_lang == "zh":
                # 简化处理：截取并添加中文说明
                if self.config["format_options"]["truncate_summary"]:
                    max_len = self.config["format_options"]["max_summary_length"]
                    if len(summary) > max_len:
                        summary = summary[:max_len] + "..."
                
                # 简单翻译示例（实际应使用翻译API）
                summary_zh = f"该论文研究了{self._extract_topic(paper)}。主要内容包括：{self._extract_main_points(summary)}"
                return summary_zh
        
        # 返回原始摘要
        if self.config["format_options"]["truncate_summary"]:
            max_len = self.config["format_options"]["max_summary_length"]
            if len(summary) > max_len:
                summary = summary[:max_len] + "..."
        
        return summary
    
    def extract_highlights(self, paper: Dict[str, Any]) -> str:
        """提取亮点做法"""
        title = paper.get("title", "").lower()
        summary = paper.get("summary", "").lower()
        
        highlights = []
        
        # 根据常见模式提取亮点
        patterns = [
            (r"(propose|introduce|present).*?(framework|model|method|approach)", "提出新框架/模型"),
            (r"(novel|new|innovative).*?(technique|algorithm)", "创新技术/算法"),
            (r"(achieve|improve).*?(performance|accuracy|result)", "性能提升"),
            (r"(solve|address).*?(problem|challenge|issue)", "解决问题"),
            (r"(combine|integrate).*?(multiple|different)", "多方法融合"),
            (r"(first|pioneering).*?(work|study)", "首创性工作"),
        ]
        
        for pattern, description in patterns:
            if re.search(pattern, title) or re.search(pattern, summary):
                highlights.append(description)
        
        # 如果自动提取不足，使用基于分类的亮点
        if len(highlights) < 2:
            categories = paper.get("categories", [])
            if any(cat.startswith("cs.IR") for cat in categories):
                highlights.append("信息检索与推荐系统方法")
            if any(cat.startswith("cs.LG") for cat in categories):
                highlights.append("机器学习算法应用")
            if any(cat.startswith("cs.AI") for cat in categories):
                highlights.append("人工智能技术集成")
        
        # 格式化亮点
        if highlights:
            if self.config["translation"]["enabled"]:
                return "\n".join([f"{i+1}. {h}" for i, h in enumerate(highlights)])
            else:
                return "; ".join(highlights)
        else:
            return "该论文提出了创新的推荐系统方法。"
    
    def extract_image_description(self, paper: Dict[str, Any]) -> str:
        """提取代表性图片说明或图片URL"""
        title = paper.get("title", "")
        categories = paper.get("categories", [])
        arxiv_id = paper.get("arxiv_id", "")
        
        # 检查配置：是否启用图片URL
        include_images = self.config.get("format_options", {}).get("include_images", True)
        image_mode = self.config.get("format_options", {}).get("image_mode", "url")  # url 或 description
        
        if image_mode == "url" and include_images and arxiv_id:
            # 返回图片URL - 使用arXiv的图片服务
            # arXiv图片URL格式: https://arxiv.org/html/{arxiv_id}v1/eg1.png
            # 或者从PDF中提取第一张图片
            image_url = self._get_paper_image_url(arxiv_id, paper)
            return image_url or self._generate_image_description(title, categories, paper)
        else:
            # 返回文字描述
            return self._generate_image_description(title, categories, paper)
    
    def _generate_image_description(self, title: str, categories: List[str], paper: Dict[str, Any]) -> str:
        """生成图片文字描述"""
        desc_parts = []
        
        # 基于标题关键词
        title_lower = title.lower()
        if any(word in title_lower for word in ["vlm", "vision-language", "multimodal"]):
            desc_parts.append("多模态模型架构图")
        elif any(word in title_lower for word in ["federated", "distributed", "privacy"]):
            desc_parts.append("联邦学习框架图")
        elif any(word in title_lower for word in ["sequential", "temporal", "time"]):
            desc_parts.append("时序建模图")
        elif any(word in title_lower for word in ["graph", "network", "relation"]):
            desc_parts.append("图神经网络架构")
        elif any(word in title_lower for word in ["pretrain", "pre-training", "transfer"]):
            desc_parts.append("预训练框架图")
        else:
            desc_parts.append("模型架构图")
        
        # 基于分类
        if any(cat.startswith("cs.CV") for cat in categories):
            desc_parts.append("视觉特征提取")
        if any(cat.startswith("cs.CL") for cat in categories):
            desc_parts.append("自然语言处理模块")
        if any(cat.startswith("cs.SI") for cat in categories):
            desc_parts.append("社交网络分析")
        
        # 添加通用部分
        desc_parts.append("实验结果对比图")
        
        # 生成描述
        if self.config.get("translation", {}).get("enabled", True):
            description = f"{'、'.join(desc_parts)}，展示{self._extract_model_name(title)}的核心组件和性能表现"
        else:
            description = f"{', '.join(desc_parts)} showing the core components and performance of {self._extract_model_name(title)}"
        
        # 添加PDF链接提示
        pdf_url = paper.get("pdf_url", "")
        if pdf_url and self.config.get("format_options", {}).get("include_images", True):
            description += f"（可通过 {pdf_url} 查看原图）"
        
        return description
    
    def _get_paper_image_url(self, arxiv_id: str, paper: Dict[str, Any]) -> str:
        """获取论文图片URL"""
        # 方法1：尝试获取arXiv的HTML版本中的图片
        # 有些论文有HTML版本，包含图片
        try:
            # 移除版本号
            clean_id = arxiv_id.replace('v1', '').replace('v2', '').replace('v3', '')
            
            # 尝试不同的图片URL模式
            image_urls = [
                f"https://arxiv.org/html/{arxiv_id}v1/eg1.png",
                f"https://arxiv.org/html/{clean_id}v1/eg1.png",
                f"https://arxiv.org/html/{arxiv_id}/eg1.png",
                # arXiv图片服务的另一种格式
                f"https://static.arxiv.org/static/{arxiv_id[:4]}/{arxiv_id}/eg1.png",
            ]
            
            # 检查哪个URL可用（这里简化处理，返回第一个）
            # 在实际实现中，可能需要下载PDF并提取图片
            return image_urls[0]
            
        except Exception:
            pass
        
        # 方法2：如果无法获取图片URL，返回包含图片链接的描述
        pdf_url = paper.get("pdf_url", "")
        if pdf_url:
            return f"=IMAGE(\"https://arxiv.org/icon/{arxiv_id[:4]}/{arxiv_id}/icon.png\")"
        
        return ""
    
    def format_paper_data(self, paper: Dict[str, Any], index: int) -> List[str]:
        """格式化论文数据为表格行"""
        
        # 提取图片信息
        if self.has_image_extractor and self.config["format_options"]["include_images"]:
            try:
                # 使用新的图片提取器接口
                image_formula, image_description = self.image_extractor.extract_for_paper(paper)
            except Exception as e:
                print(f"⚠️  图片提取失败: {e}")
                image_formula = ""
                image_description = self.extract_image_description(paper)
        else:
            image_formula = ""
            image_description = self.extract_image_description(paper)
        
        return [
            str(index),  # 序号
            paper.get("title", ""),  # 论文标题
            ", ".join(paper.get("authors", [])),  # 作者
            paper.get("published", ""),  # 发表时间
            paper.get("arxiv_id", ""),  # arXiv ID
            self.extract_content_summary(paper),  # 内容概括
            self.extract_highlights(paper),  # 亮点做法
            image_formula,  # 代表性图片（IMAGE公式）
            image_description,  # 图片说明
            paper.get("pdf_url", "").replace("pdf", "abs"),  # 论文链接
            ", ".join(paper.get("categories", []))  # 分类
        ]
    
    def _extract_topic(self, paper: Dict[str, Any]) -> str:
        """提取论文主题"""
        title = paper.get("title", "").lower()
        
        topics = {
            "recommendation": "推荐系统",
            "recommender": "推荐算法",
            "pretrain": "预训练方法",
            "multimodal": "多模态推荐",
            "federated": "联邦学习推荐",
            "sequential": "顺序推荐",
            "collaborative filtering": "协同过滤",
            "personalization": "个性化推荐",
            "retrieval": "检索增强推荐"
        }
        
        for eng, zh in topics.items():
            if eng in title:
                return zh
        
        return "推荐系统技术"
    
    def _extract_main_points(self, summary: str) -> str:
        """提取主要观点"""
        # 简单提取前3个句子
        sentences = re.split(r'[.!?]+', summary)
        main_points = sentences[:3]
        return "；".join([s.strip() for s in main_points if s.strip()])
    
    def _extract_model_name(self, title: str) -> str:
        """从标题中提取模型名称"""
        # 查找可能的大写缩写或特定模式
        patterns = [
            r'([A-Z]{2,})',  # 大写缩写如VLM、LLM
            r'([A-Z][a-z]+-[A-Z][a-z]+)',  # 连字符名称
            r'([A-Z][a-z]+[A-Z][a-z]+)',  # 驼峰名称
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, title)
            if matches:
                return matches[0]
        
        # 提取第一个有意义的单词
        words = title.split()
        for word in words:
            if len(word) > 3 and word[0].isupper():
                return word
        
        return "该模型"


def main():
    """测试函数"""
    import os
    
    # 测试数据
    test_paper = {
        "title": "VLM2Rec: Resolving Modality Collapse in Vision-Language Model Embedders for Multimodal Sequential Recommendation",
        "authors": ["Junyoung Kim", "Woojoo Kim", "Jaehyung Lim", "Dongha Kim", "Hwanjo Yu"],
        "published": "2026-03-18",
        "arxiv_id": "2603.17450v1",
        "summary": "Sequential Recommendation (SR) in multimodal settings typically relies on small frozen pretrained encoders, which limits semantic capacity and prevents Collaborative Filtering (CF) signals from being fully integrated into item representations. Inspired by the recent success of Large Language Models (LLMs) as high-capacity embedders, we investigate the use of Vision-Language Models (VLMs) as CF-aware multimodal encoders for SR.",
        "categories": ["cs.IR", "cs.AI"],
        "pdf_url": "https://arxiv.org/pdf/2603.17450v1"
    }
    
    extractor = PaperInfoExtractor()
    
    print("测试论文信息提取:")
    print(f"标题: {test_paper['title']}")
    print(f"内容概括: {extractor.extract_content_summary(test_paper)}")
    print(f"亮点做法:\n{extractor.extract_highlights(test_paper)}")
    print(f"图片说明: {extractor.extract_image_description(test_paper)}")
    
    formatted = extractor.format_paper_data(test_paper, 1)
    print(f"\n格式化数据:")
    for i, field in enumerate(formatted):
        print(f"{i}. {field}")


if __name__ == "__main__":
    main()