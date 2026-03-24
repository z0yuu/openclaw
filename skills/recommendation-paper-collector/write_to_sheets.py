#!/usr/bin/env python3
"""
Google Sheets写入模块
将论文数据写入指定的Google Sheets文档
"""

import json
import re
import os
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleSheetsWriter:
    def __init__(self, config_path: str = None):
        """初始化写入器"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "google_credentials": {
                    "token_path": "/root/agent/token.json",
                    "client_secret_path": "/root/agent/google.json"
                },
                "default_sheet_url": "https://docs.google.com/spreadsheets/d/1TW-NubPwQCrhVvV1maV4KQRYfjoJ39e1V_L_Tx6oPrQ",
                "sheet_name": "推荐系统热点论文",
                "fields": [
                    "序号", "论文标题", "作者", "发表时间", "arXiv ID",
                    "内容概括", "亮点做法", "代表性图片说明", "论文链接", "分类"
                ]
            }
    
    def get_credentials(self) -> Optional[Credentials]:
        """获取Google API凭据"""
        try:
            token_path = self.config["google_credentials"]["token_path"]
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            # 刷新过期的token
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                # 保存刷新后的token
                with open(token_path, 'w') as f:
                    json.dump(json.loads(creds.to_json()), f, indent=2)
            
            return creds
            
        except Exception as e:
            print(f"获取凭据失败: {e}")
            return None
    
    def extract_spreadsheet_id(self, url: str) -> Optional[str]:
        """从URL中提取spreadsheet ID"""
        patterns = [
            r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
            r'document/d/([a-zA-Z0-9-_]+)',
            r'key=([a-zA-Z0-9-_]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def create_sheets_service(self) -> Optional[Any]:
        """创建Google Sheets服务"""
        creds = self.get_credentials()
        if not creds:
            return None
        
        try:
            service = build('sheets', 'v4', credentials=creds)
            return service
        except Exception as e:
            print(f"创建Sheets服务失败: {e}")
            return None
    
    def prepare_header_row(self) -> List[str]:
        """准备表头行"""
        fields = self.config["fields"]
        return fields
    
    def prepare_data_rows(self, papers: List[Dict[str, Any]]) -> List[List[str]]:
        """准备数据行"""
        rows = []
        for i, paper in enumerate(papers, 1):
            if isinstance(paper, list) and len(paper) >= 10:
                # 已经是格式化好的行
                rows.append(paper)
            elif isinstance(paper, dict):
                # 获取图片信息
                image_info = paper.get("image_description", "")
                
                # 检查是否是图片URL或需要转换为IMAGE公式
                image_cell = self._process_image_cell(image_info, paper.get("arxiv_id", ""))
                
                # 需要格式化的数据
                # 处理图片说明
                image_description = paper.get("image_description", "")
                if not image_description and "image_description" in paper:
                    image_description = "模型架构图或实验结果图"
                
                row = [
                    str(i),  # 序号
                    paper.get("title", ""),
                    paper.get("authors", ""),
                    paper.get("published", ""),
                    paper.get("arxiv_id", ""),
                    paper.get("summary", "")[:500],
                    paper.get("highlights", ""),
                    image_cell,  # 图片单元格（IMAGE公式）
                    image_description,  # 图片说明
                    paper.get("pdf_url", "").replace("pdf", "abs") if paper.get("pdf_url") else "",
                    ", ".join(paper.get("categories", []))
                ]
                rows.append(row)
        
        return rows
    
    def _process_image_cell(self, image_info: str, arxiv_id: str) -> str:
        """处理图片单元格内容"""
        # 检查是否已经是IMAGE公式
        if image_info.startswith("=IMAGE("):
            return image_info
        
        # 检查是否是URL
        if image_info.startswith("http://") or image_info.startswith("https://"):
            # 如果是图片URL，包装成IMAGE公式
            if any(image_info.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                return f'=IMAGE("{image_info}")'
        
        # 检查是否包含图片URL
        import re
        url_pattern = r'https?://[^\s<>"]+?\.(?:png|jpg|jpeg|gif|webp)'
        urls = re.findall(url_pattern, image_info, re.IGNORECASE)
        if urls:
            return f'=IMAGE("{urls[0]}")'
        
        # 如果没有图片URL，使用arXiv的默认图标
        if arxiv_id:
            # arXiv图标URL格式
            clean_id = arxiv_id.replace('v1', '').replace('v2', '').replace('v3', '')
            if len(clean_id) >= 4:
                icon_url = f"https://arxiv.org/icon/{clean_id[:4]}/{clean_id}/icon.png"
                return f'=IMAGE("{icon_url}")'
        
        # 返回原始信息
        return image_info
    
    def write_to_sheets(self, papers: List[Dict[str, Any]], 
                       sheet_url: Optional[str] = None,
                       sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """将论文数据写入Google Sheets"""
        
        # 确定参数
        sheet_url = sheet_url or self.config["default_sheet_url"]
        sheet_name = sheet_name or self.config["sheet_name"]
        
        # 提取spreadsheet ID
        spreadsheet_id = self.extract_spreadsheet_id(sheet_url)
        if not spreadsheet_id:
            return {"success": False, "error": f"无法从URL提取spreadsheet ID: {sheet_url}"}
        
        # 创建服务
        service = self.create_sheets_service()
        if not service:
            return {"success": False, "error": "无法创建Google Sheets服务"}
        
        # 准备数据
        header_row = self.prepare_header_row()
        data_rows = self.prepare_data_rows(papers)
        all_rows = [header_row] + data_rows
        
        # 确定写入范围
        num_rows = len(all_rows)
        num_cols = len(header_row)
        col_letter = chr(ord('A') + num_cols - 1) if num_cols <= 26 else 'Z'
        range_name = f"{sheet_name}!A1:{col_letter}{num_rows}"
        
        try:
            # 写入数据
            body = {'values': all_rows}
            
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            return {
                "success": True,
                "updated_cells": result.get('updatedCells'),
                "updated_range": result.get('updatedRange'),
                "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}",
                "num_papers": len(papers)
            }
            
        except HttpError as e:
            error_details = e.error_details if hasattr(e, 'error_details') else str(e)
            return {"success": False, "error": f"HTTP错误: {error_details}"}
        except Exception as e:
            return {"success": False, "error": f"写入错误: {e}"}
    
    def clear_sheet(self, sheet_url: Optional[str] = None,
                   sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """清空工作表"""
        sheet_url = sheet_url or self.config["default_sheet_url"]
        sheet_name = sheet_name or self.config["sheet_name"]
        
        spreadsheet_id = self.extract_spreadsheet_id(sheet_url)
        if not spreadsheet_id:
            return {"success": False, "error": f"无法从URL提取spreadsheet ID: {sheet_url}"}
        
        service = self.create_sheets_service()
        if not service:
            return {"success": False, "error": "无法创建Google Sheets服务"}
        
        try:
            # 清空整个工作表
            range_name = f"{sheet_name}!A1:Z1000"
            result = service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            return {"success": True, "message": f"已清空工作表: {sheet_name}"}
            
        except Exception as e:
            return {"success": False, "error": f"清空错误: {e}"}
    
    def append_to_sheet(self, papers: List[Dict[str, Any]],
                       sheet_url: Optional[str] = None,
                       sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """追加数据到工作表"""
        sheet_url = sheet_url or self.config["default_sheet_url"]
        sheet_name = sheet_name or self.config["sheet_name"]
        
        spreadsheet_id = self.extract_spreadsheet_id(sheet_url)
        if not spreadsheet_id:
            return {"success": False, "error": f"无法从URL提取spreadsheet ID: {sheet_url}"}
        
        service = self.create_sheets_service()
        if not service:
            return {"success": False, "error": "无法创建Google Sheets服务"}
        
        try:
            # 首先读取现有数据，找到最后一行
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A:A"
            ).execute()
            
            values = result.get('values', [])
            start_row = len(values) + 1
            
            # 准备要追加的数据
            data_rows = self.prepare_data_rows(papers)
            
            # 追加数据
            body = {'values': data_rows}
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A{start_row}",
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            return {
                "success": True,
                "updated_cells": result.get('updatedCells'),
                "updated_range": result.get('updatedRange'),
                "start_row": start_row,
                "num_papers": len(papers)
            }
            
        except Exception as e:
            return {"success": False, "error": f"追加错误: {e}"}


def main():
    """测试函数"""
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
    from extract_paper_info import PaperInfoExtractor
    
    # 测试数据
    test_papers = [
        {
            "title": "VLM2Rec: Resolving Modality Collapse in Vision-Language Model Embedders for Multimodal Sequential Recommendation",
            "authors": ["Junyoung Kim", "Woojoo Kim", "Jaehyung Lim", "Dongha Kim", "Hwanjo Yu"],
            "published": "2026-03-18",
            "arxiv_id": "2603.17450v1",
            "summary": "Sequential Recommendation (SR) in multimodal settings typically relies on small frozen pretrained encoders, which limits semantic capacity and prevents Collaborative Filtering (CF) signals from being fully integrated into item representations.",
            "highlights": "1. 多模态编码器设计\n2. 模态崩溃问题解决\n3. 性能显著提升",
            "image_description": "VLM2Rec框架架构图",
            "pdf_url": "https://arxiv.org/pdf/2603.17450v1",
            "categories": ["cs.IR", "cs.AI"]
        }
    ]
    
    # 提取信息
    extractor = PaperInfoExtractor()
    formatted_papers = []
    for i, paper in enumerate(test_papers, 1):
        formatted_papers.append(extractor.format_paper_data(paper, i))
    
    # 写入测试
    writer = GoogleSheetsWriter()
    print("测试Google Sheets写入...")
    
    # 测试写入
    result = writer.write_to_sheets(formatted_papers)
    
    if result["success"]:
        print(f"✅ 写入成功!")
        print(f"   更新单元格: {result.get('updated_cells')}")
        print(f"   更新范围: {result.get('updated_range')}")
        print(f"   论文数量: {result.get('num_papers')}")
        print(f"   表格链接: {result.get('spreadsheet_url')}")
    else:
        print(f"❌ 写入失败: {result.get('error')}")


if __name__ == "__main__":
    main()