#!/usr/bin/env python3
"""
arXiv论文图片提取器
集成PDF内容提取skill，从arXiv论文PDF中提取代表性图片
"""

import os
import json
import tempfile
import requests
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class ArXivImageExtractor:
    def __init__(self, config_path: str = None):
        """初始化arXiv图片提取器"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "temp_dir": "/tmp/arxiv_images",
                "download_timeout": 30,
                "max_file_size_mb": 50,
                "image_extraction": {
                    "min_width": 100,
                    "min_height": 100,
                    "dedupe": True
                }
            }
        
        # 确保临时目录存在
        os.makedirs(self.config["temp_dir"], exist_ok=True)
        
        # 尝试导入PDF图片提取器
        try:
            from pdf_image_extractor import extract_images
            self.extract_images_func = extract_images
            self.has_pdf_extractor = True
            print("✅ PDF图片提取器加载成功")
        except ImportError as e:
            print(f"⚠️  PDF图片提取器加载失败: {e}")
            self.has_pdf_extractor = False
    
    def download_arxiv_pdf(self, arxiv_id: str) -> Optional[str]:
        """下载arXiv论文PDF到临时文件"""
        try:
            # 构建PDF URL
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            
            print(f"📥 下载PDF: {pdf_url}")
            
            # 下载PDF
            response = requests.get(
                pdf_url, 
                timeout=self.config["download_timeout"],
                stream=True
            )
            
            if response.status_code != 200:
                print(f"❌ 下载失败: HTTP {response.status_code}")
                return None
            
            # 检查文件大小
            content_length = response.headers.get('content-length')
            if content_length:
                file_size_mb = int(content_length) / (1024 * 1024)
                if file_size_mb > self.config["max_file_size_mb"]:
                    print(f"⚠️  文件过大: {file_size_mb:.1f}MB > {self.config['max_file_size_mb']}MB")
                    return None
            
            # 保存到临时文件
            temp_file = os.path.join(self.config["temp_dir"], f"{arxiv_id}.pdf")
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ PDF下载完成: {temp_file}")
            return temp_file
            
        except Exception as e:
            print(f"❌ PDF下载错误: {e}")
            return None
    
    def extract_images_from_pdf(self, pdf_path: str, arxiv_id: str) -> List[Dict]:
        """从PDF中提取图片"""
        if not self.has_pdf_extractor:
            print("❌ PDF提取器不可用")
            return []
        
        try:
            # 创建输出目录
            output_dir = os.path.join(self.config["temp_dir"], arxiv_id)
            
            # 调用PDF图片提取器
            result = self.extract_images_func(
                pdf_path=pdf_path,
                output_dir=output_dir,
                pages="all",
                config=self.config["image_extraction"]
            )
            
            # 解析提取结果
            images = []
            if isinstance(result, dict) and "pages" in result:
                for page_info in result["pages"]:
                    for item in page_info.get("items", []):
                        image_info = {
                            "file_path": item.get("file", ""),
                            "width": item.get("width", 0),
                            "height": item.get("height", 0),
                            "page": page_info.get("page", 0),
                            "arxiv_id": arxiv_id
                        }
                        images.append(image_info)
            
            print(f"✅ 从PDF提取到 {len(images)} 张图片")
            return images
            
        except Exception as e:
            print(f"❌ 图片提取失败: {e}")
            return []
    
    def select_representative_image(self, images: List[Dict]) -> Optional[Dict]:
        """选择代表性图片"""
        if not images:
            return None
        
        # 优先选择宽度和高度都较大的图片（可能是图表）
        filtered_images = [img for img in images 
                         if img.get("width", 0) >= 300 and img.get("height", 0) >= 200]
        
        if filtered_images:
            # 选择第一页的图片（通常是模型架构图）
            first_page_images = [img for img in filtered_images if img.get("page", 0) == 1]
            if first_page_images:
                return first_page_images[0]
            # 否则选择最大的图片
            return max(filtered_images, key=lambda x: x.get("width", 0) * x.get("height", 0))
        
        # 如果没有符合条件的，返回第一张图片
        return images[0]
    
    def upload_image_to_cloud(self, image_path: str) -> Optional[str]:
        """上传图片到云端并返回URL（模拟函数）"""
        # 在实际应用中，这里应该将图片上传到云存储（如Google Cloud Storage、AWS S3等）
        # 并返回可公开访问的URL
        
        # 目前返回一个占位URL
        print(f"📤 图片需要上传: {image_path}")
        return None
    
    def get_image_formula(self, image_url: str, width: int = 300, height: int = 200) -> str:
        """生成Google Sheets的IMAGE函数公式"""
        if not image_url:
            # 如果没有图片URL，使用占位图
            placeholder_url = f"https://via.placeholder.com/{width}x{height}/E0E0E0/333333?text=No+Image"
            return f'=IMAGE("{placeholder_url}", 1, {height}, {width})'
        
        # 使用实际的图片URL
        return f'=IMAGE("{image_url}", 1, {height}, {width})'
    
    def extract_for_paper(self, arxiv_id: str, title: str = "") -> Tuple[str, str]:
        """为论文提取代表性图片
        
        返回: (图片公式, 图片说明)
        """
        print(f"🖼️  为论文提取图片: {arxiv_id}")
        
        # 1. 下载PDF
        pdf_path = self.download_arxiv_pdf(arxiv_id)
        if not pdf_path:
            print(f"⚠️  无法下载PDF，使用占位图")
            placeholder_formula = self.get_image_formula(None)
            description = "图片暂不可用（需要从论文PDF中提取）"
            return placeholder_formula, description
        
        # 2. 提取图片
        images = self.extract_images_from_pdf(pdf_path, arxiv_id)
        
        # 3. 选择代表性图片
        if images:
            selected_image = self.select_representative_image(images)
            
            if selected_image:
                image_path = selected_image.get("file_path", "")
                
                # 在实际应用中，这里应该上传图片并获取URL
                # image_url = self.upload_image_to_cloud(image_path)
                
                # 暂时使用本地文件路径（需要转换为可访问的URL）
                # 这里简化处理，使用占位图
                image_url = None
                
                # 生成图片说明
                page_num = selected_image.get("page", 0)
                description = f"论文第{page_num}页的图表"
                
                # 生成公式
                width = selected_image.get("width", 300)
                height = selected_image.get("height", 200)
                image_formula = self.get_image_formula(image_url, width, height)
                
                print(f"✅ 提取到代表性图片: {description}")
                return image_formula, description
        
        # 4. 如果没有提取到图片，使用占位图
        print(f"⚠️  未提取到图片，使用占位图")
        placeholder_formula = self.get_image_formula(None)
        description = f"{title[:20]}... 的模型架构图（从PDF提取失败）"
        
        return placeholder_formula, description
    
    def cleanup_temp_files(self, arxiv_id: str = None):
        """清理临时文件"""
        if arxiv_id:
            # 清理特定论文的文件
            pattern = os.path.join(self.config["temp_dir"], f"{arxiv_id}*")
            os.system(f"rm -rf {pattern}")
        else:
            # 清理所有临时文件（保留一定时间）
            pass
    
    def test_extraction(self, arxiv_id: str = "2603.17450v1"):
        """测试图片提取功能"""
        print(f"🧪 测试arXiv图片提取 - arXiv ID: {arxiv_id}")
        print("=" * 50)
        
        image_formula, description = self.extract_for_paper(arxiv_id, "Test Paper Title")
        
        print(f"\n📊 提取结果:")
        print(f"   图片公式: {image_formula}")
        print(f"   图片说明: {description}")
        
        # 清理临时文件
        self.cleanup_temp_files(arxiv_id)
        
        print("\n✅ 测试完成")


def main():
    """主函数"""
    extractor = ArXivImageExtractor()
    
    # 测试提取
    extractor.test_extraction("2603.17450v1")


if __name__ == "__main__":
    main()