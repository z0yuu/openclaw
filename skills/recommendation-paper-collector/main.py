#!/usr/bin/env python3
"""
推荐系统论文收集器 - 主程序
整合搜索、提取和写入功能
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any
from datetime import datetime


# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 导入自定义模块
from search_arxiv import ArXivSearcher
from extract_paper_info import PaperInfoExtractor
from write_to_sheets import GoogleSheetsWriter


class RecommendationPaperCollector:
    """推荐系统论文收集器主类"""
    
    def __init__(self, config_path: str = None):
        """初始化收集器"""
        self.config_path = config_path or os.path.join(current_dir, "defaults.json")
        
        # 加载配置
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {}
        
        # 初始化组件
        self.searcher = ArXivSearcher(self.config_path)
        self.extractor = PaperInfoExtractor(self.config_path)
        self.writer = GoogleSheetsWriter(self.config_path)
        
        # 统计数据
        self.stats = {
            "total_searched": 0,
            "relevant_found": 0,
            "processed": 0,
            "written": 0,
            "start_time": datetime.now(),
            "end_time": None
        }
    
    def collect_papers(self, days_back: int = None, max_papers: int = None) -> List[Dict[str, Any]]:
        """收集论文"""
        print(f"🔄 开始收集推荐系统论文...")
        
        # 更新配置参数
        if days_back:
            self.searcher.config["days_back"] = days_back
        if max_papers:
            self.searcher.config["max_papers"] = max_papers
        
        # 搜索论文
        print(f"📊 搜索参数:")
        print(f"   时间范围: 最近{self.searcher.config['days_back']}天")
        print(f"   最大数量: {self.searcher.config['max_papers']}篇")
        print(f"   搜索分类: {', '.join(self.searcher.config['search_categories'])}")
        
        papers = self.searcher.search_papers()
        self.stats["total_searched"] = len(papers)
        
        if not papers:
            print(f"⚠️  未找到论文，尝试备用搜索方法...")
            papers = self.searcher.get_daily_papers()
            self.stats["total_searched"] = len(papers)
        
        # 筛选相关论文
        relevant_papers = self.searcher.filter_relevant_papers(papers)
        self.stats["relevant_found"] = len(relevant_papers)
        
        print(f"✅ 搜索完成:")
        print(f"   总共找到: {self.stats['total_searched']}篇论文")
        print(f"   相关论文: {self.stats['relevant_found']}篇")
        
        return relevant_papers
    
    def process_papers(self, papers: List[Dict[str, Any]]) -> List[List[str]]:
        """处理论文数据"""
        print(f"🔄 开始处理论文信息...")
        
        formatted_papers = []
        for i, paper in enumerate(papers, 1):
            try:
                formatted = self.extractor.format_paper_data(paper, i)
                formatted_papers.append(formatted)
                
                # 显示进度
                if i % 5 == 0 or i == len(papers):
                    print(f"   已处理: {i}/{len(papers)}篇")
                    
            except Exception as e:
                print(f"⚠️  处理论文失败: {paper.get('title', '未知标题')[:50]}... - 错误: {e}")
                continue
        
        self.stats["processed"] = len(formatted_papers)
        print(f"✅ 处理完成: {self.stats['processed']}篇论文已格式化")
        
        return formatted_papers
    
    def write_papers(self, papers: List[List[str]], 
                    sheet_url: str = None, 
                    sheet_name: str = None,
                    clear_first: bool = False) -> Dict[str, Any]:
        """写入论文到Google Sheets"""
        print(f"🔄 开始写入Google Sheets...")
        
        # 确定目标表格
        sheet_url = sheet_url or self.config.get("default_sheet_url")
        sheet_name = sheet_name or self.config.get("sheet_name", "推荐系统热点论文")
        
        print(f"📋 目标表格:")
        print(f"   表格链接: {sheet_url}")
        print(f"   工作表名: {sheet_name}")
        
        # 如果需要先清空
        if clear_first:
            print(f"🧹 清空现有工作表...")
            clear_result = self.writer.clear_sheet(sheet_url, sheet_name)
            if clear_result["success"]:
                print(f"✅ {clear_result['message']}")
            else:
                print(f"⚠️  清空失败: {clear_result.get('error')}")
        
        # 写入数据
        write_result = self.writer.write_to_sheets(papers, sheet_url, sheet_name)
        
        if write_result["success"]:
            self.stats["written"] = write_result.get("num_papers", 0)
            self.stats["end_time"] = datetime.now()
            
            print(f"✅ 写入成功!")
            print(f"   更新单元格: {write_result.get('updated_cells')}")
            print(f"   更新范围: {write_result.get('updated_range')}")
            print(f"   写入论文: {self.stats['written']}篇")
            print(f"🔗 表格链接: {write_result.get('spreadsheet_url')}")
        else:
            print(f"❌ 写入失败: {write_result.get('error')}")
        
        return write_result
    
    def run(self, days_back: int = None, max_papers: int = None,
           sheet_url: str = None, sheet_name: str = None,
           clear_first: bool = False) -> Dict[str, Any]:
        """运行完整的收集流程"""
        print("=" * 60)
        print("🤖 推荐系统论文收集器 v1.0")
        print("=" * 60)
        
        try:
            # 1. 收集论文
            raw_papers = self.collect_papers(days_back, max_papers)
            
            if not raw_papers:
                return {
                    "success": False,
                    "error": "未找到相关论文",
                    "stats": self.stats
                }
            
            # 2. 处理论文
            formatted_papers = self.process_papers(raw_papers)
            
            if not formatted_papers:
                return {
                    "success": False,
                    "error": "论文处理失败",
                    "stats": self.stats
                }
            
            # 3. 写入Google Sheets
            write_result = self.write_papers(formatted_papers, sheet_url, sheet_name, clear_first)
            
            # 计算耗时
            duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
            
            # 生成总结报告
            report = {
                "success": write_result["success"],
                "stats": self.stats,
                "duration_seconds": duration,
                "sheet_url": write_result.get("spreadsheet_url"),
                "timestamp": datetime.now().isoformat()
            }
            
            if write_result["success"]:
                print("\n" + "=" * 60)
                print("📈 任务完成报告")
                print("=" * 60)
                print(f"✅ 成功收集并整理了 {self.stats['written']} 篇推荐系统论文")
                print(f"⏱️  总耗时: {duration:.1f}秒")
                print(f"📊 效率: {self.stats['written']/duration:.1f} 篇/秒")
                print(f"🔗 查看结果: {write_result.get('spreadsheet_url')}")
                print("=" * 60)
            
            return report
            
        except Exception as e:
            print(f"❌ 运行过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "stats": self.stats
            }


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='推荐系统论文收集器')
    
    parser.add_argument('--days', type=int, default=7,
                       help='搜索最近多少天的论文（默认: 7）')
    parser.add_argument('--max', type=int, default=20,
                       help='最大论文数量（默认: 20）')
    parser.add_argument('--url', type=str,
                       help='Google Sheets链接（默认使用配置文件中的链接）')
    parser.add_argument('--sheet', type=str, default='推荐系统热点论文',
                       help='工作表名称（默认: 推荐系统热点论文）')
    parser.add_argument('--clear', action='store_true',
                       help='清空现有工作表内容')
    parser.add_argument('--config', type=str,
                       help='配置文件路径')
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    # 创建收集器
    collector = RecommendationPaperCollector(args.config)
    
    # 运行收集任务
    result = collector.run(
        days_back=args.days,
        max_papers=args.max,
        sheet_url=args.url,
        sheet_name=args.sheet,
        clear_first=args.clear
    )
    
    # 返回结果代码
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()