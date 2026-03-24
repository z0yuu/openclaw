#!/usr/bin/env python3
"""
arXiv论文PDF图片提取模块
基于 skill-pdf-content-extractor 的图片提取功能
"""

import os
import json
import tempfile
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import requests
import fitz  # PyMuPDF


class ArXivPDFImageExtractor:
    """arXiv论文PDF图片提取器"""
    
    def __init__(self, config_path: str = None):
        """初始化提取器"""
        self.config = {
            "min_width": 100,      # 最小图片宽度
            "min_height": 100,     # 最小图片高度
            "deduplicate": True,   # 去重
            "max_images": 5,       # 最多提取图片数
            "output_dir": "/tmp/arxiv_images",  # 输出目录
            "image_formats": ["png", "jpg", "jpeg", "gif"]
        }
        
        # 创建输出目录
        os.makedirs(self.config["output_dir"], exist_ok=True)
    
    def download_pdf(self, arxiv_id: str) -> Optional[str]:
        """下载arXiv论文PDF到临时文件"""
        try:
            # 构建PDF URL
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            
            print(f"📥 下载PDF: {pdf_url}")
            
            # 下载PDF
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
        
        try:
            # 打开PDF文档
            doc = fitz.open(pdf_path)
            
            print(f"📄 处理PDF: {pdf_path}, 共 {len(doc)} 页")
            
            seen_hashes = set()
            image_index = 0
            
            # 遍历所有页面
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # 获取页面中的所有图片
                img_list = page.get_images(full=True)
                
                for img_index, img in enumerate(img_list, 1):
                    xref = img[0]
                    
                    try:
                        # 提取图片
                        base_image = doc.extract_image(xref)
                        image_data = base_image.get("image")
                        ext = base_image.get("ext", "png")
                        width = base_image.get("width", 0)
                        height = base_image.get("height", 0)
                        
                        # 过滤小图片
                        if width < self.config["min_width"] or height < self.config["min_height"]:
                            continue
                        
                        # 计算图片哈希值用于去重
                        img_hash = hashlib.sha256(image_data).hexdigest()
                        if self.config["deduplicate"] and img_hash in seen_hashes:
                            continue
                        
                        seen_hashes.add(img_hash)
                        image_index += 1
                        
                        # 保存图片
                        img_filename = f"{arxiv_id}_p{page_num+1}_img{image_index}.{ext}"
                        img_path = os.path.join(self.config["output_dir"], img_filename)
                        
                        with open(img_path, 'wb') as f:
                            f.write(image_data)
                        
                        # 创建图片信息记录
                        image_info = {
                            "arxiv_id": arxiv_id,
                            "page": page_num + 1,
                            "index": image_index,
                            "filename": img_filename,
                            "path": img_path,
                            "url": None,  # 本地文件没有URL
                            "width": width,
                            "height": height,
                            "format": ext,
                            "hash": img_hash,
                            "description": f"Figure {image_index} from page {page_num + 1}"
                        }
                        
                        images.append(image_info)
                        print(f"🖼️  提取图片: {img_filename} ({width}x{height})")
                        
                        # 限制最大图片数量
                        if len(images) >= self.config["max_images"]:
                            break
                            
                    except Exception as e:
                        print(f"⚠️  提取图片失败 (xref={xref}): {e}")
                        continue
                
                if len(images) >= self.config["max_images"]:
                    break
            
            doc.close()
            print(f"✅ 从PDF提取了 {len(images)} 张图片")
            
        except Exception as e:
            print(f"❌ PDF处理失败: {e}")
        
        return images
    
    def get_main_figure(self, arxiv_id: str) -> Tuple[Optional[str], str]:
        """获取主要代表性图片
        
        返回: (图片路径或URL, 图片描述)
        """
        try:
            # 1. 下载PDF
            pdf_path = self.download_pdf(arxiv_id)
            if not pdf_path:
                return None, "无法下载PDF文件"
            
            # 2. 提取图片
            images = self.extract_images_from_pdf(pdf_path, arxiv_id)
            
            if not images:
                return None, "论文中未找到图片"
            
            # 3. 选择最有代表性的图片
            # 优先选择第一页的图片，或者最大尺寸的图片
            main_image = images[0]
            for img in images:
                if img["page"] == 1:  # 第一页的图片通常是模型架构图
                    main_image = img
                    break
                elif img["width"] * img["height"] > main_image["width"] * main_image["height"]:
                    main_image = img
            
            # 4. 生成图片描述
            description = f"Figure {main_image['index']} from page {main_image['page']} ({main_image['width']}x{main_image['height']})"
            
            return main_image["path"], description
            
        except Exception as e:
            print(f"❌ 获取主要图片失败: {e}")
            return None, f"图片提取失败: {str(e)}"
    
    def generate_image_formula(self, image_path: str, description: str = "") -> str:
        """生成Google Sheets的IMAGE函数公式
        
        由于Google Sheets的IMAGE函数需要公开可访问的URL，
        而本地图片无法直接使用，这里提供一个解决方案：
        1. 将图片上传到临时公共存储
        2. 使用IMAGE函数引用
        由于目前没有公共存储，先返回占位符
        """
        if image_path and os.path.exists(image_path):
            # 在实际应用中，这里应该将图片上传到公共存储
            # 并返回 =IMAGE("公共URL") 格式
            return f'=HYPERLINK("file://{image_path}", "查看图片")'
        else:
            # 返回占位符
            return "=IMAGE(\"https://via.placeholder.com/300x200/E0E0E0/333333?text=Image+Not+Available\")"
    
    def extract_for_sheets(self, arxiv_id: str, title: str) -> Tuple[str, str]:
        """为Google Sheets提取图片信息
        
        返回: (图片单元格内容, 图片说明)
        """
        try:
            # 获取主要图片
            image_path, description = self.get_main_figure(arxiv_id)
            
            if image_path:
                # 生成Google Sheets公式
                formula = self.generate_image_formula(image_path, description)
                return formula, description
            else:
                # 使用占位图
                placeholder_formula = '=IMAGE("https://via.placeholder.com/300x200/E0E0E0/333333?text=No+Image+Available")'
                placeholder_desc = f"{title[:30]}... (图片暂不可用)"
                return placeholder_formula, placeholder_desc
                
        except Exception as e:
            print(f"❌ 图片提取错误: {e}")
            # 返回错误占位符
            error_formula = '=IMAGE("https://via.placeholder.com/300x200/FF9999/FFFFFF?text=Image+Error")'
            error_desc = f"图片提取失败: {str(e)[:50]}"
            return error_formula, error_desc
    
    def cleanup(self):
        """清理临时文件"""
        try:
            import shutil
            # 清理临时目录
            for item in os.listdir("/tmp"):
                if item.startswith("arxiv_pdf_"):
                    shutil.rmtree(os.path.join("/tmp", item))
            print("🧹 清理临时文件完成")
        except Exception as e:
            print(f"⚠️  清理失败: {e}")


def test_extraction():
    """测试函数"""
    extractor = ArXivPDFImageExtractor()
    
    print("🧪 测试arXiv论文图片提取")
    print("=" * 50)
    
    # 测试arxiv ID
    test_arxiv_id = "2603.17450v1"
    test_title = "VLM2Rec: Resolving Modality Collapse..."
    
    print(f"测试论文: {test_title}")
    print(f"arXiv ID: {test_arxiv_id}")
    
    # 提取图片信息
    formula, description = extractor.extract_for_sheets(test_arxiv_id, test_title)
    
    print(f"\n📸 提取结果:")
    print(f"公式: {formula}")
    print(f"描述: {description}")
    
    # 清理
    extractor.cleanup()
    
    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_extraction()