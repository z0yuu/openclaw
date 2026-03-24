#!/usr/bin/env python3
"""
arXiv论文搜索模块
用于搜索推荐系统相关的最新论文
"""

import arxiv
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any


class ArXivSearcher:
    def __init__(self, config_path: str = None):
        """初始化搜索器"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            # 默认配置
            self.config = {
                "search_categories": ["cs.IR", "cs.LG", "cs.AI"],
                "days_back": 7,
                "max_papers": 20,
                "keywords": [
                    "recommendation", "recommender", "pretrain", "pretraining",
                    "multimodal", "federated", "sequential", "retrieval",
                    "collaborative filtering", "personalization"
                ]
            }
        
    def build_search_query(self) -> str:
        """构建搜索查询字符串"""
        categories = self.config["search_categories"]
        keywords = self.config["keywords"]
        
        # 构建分类查询
        cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
        
        # 构建关键词查询
        keyword_query = " OR ".join([f'all:"{kw}"' for kw in keywords])
        
        # 构建时间查询
        days_back = self.config["days_back"]
        date_limit = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")
        
        # 组合查询
        query = f"({cat_query}) AND ({keyword_query}) AND submittedDate:[{date_limit} TO *]"
        
        return query
    
    def search_papers(self) -> List[Dict[str, Any]]:
        """搜索论文"""
        query = self.build_search_query()
        max_results = self.config["max_papers"]
        
        print(f"搜索查询: {query}")
        print(f"最大结果数: {max_results}")
        
        # 使用arxiv客户端搜索
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        papers = []
        try:
            for result in client.results(search):
                paper = {
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "published": result.published.strftime("%Y-%m-%d"),
                    "updated": result.updated.strftime("%Y-%m-%d") if result.updated else None,
                    "arxiv_id": result.entry_id.split('/')[-1],
                    "summary": result.summary,
                    "categories": result.categories,
                    "pdf_url": result.pdf_url,
                    "primary_category": result.primary_category
                }
                papers.append(paper)
                print(f"找到论文: {paper['title'][:50]}...")
                
        except Exception as e:
            print(f"搜索错误: {e}")
            # 返回空列表，允许其他搜索方法
            
        return papers
    
    def filter_relevant_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """筛选与推荐系统相关的论文"""
        relevant_keywords = [
            "recommendation", "recommender", "recommending",
            "collaborative filtering", "CF",
            "personalization", "personalized",
            "sequential recommendation", "multimodal recommendation",
            "federated recommendation", "pretrain", "pre-train"
        ]
        
        relevant_papers = []
        for paper in papers:
            title = paper["title"].lower()
            summary = paper["summary"].lower()
            
            # 检查标题或摘要中是否包含关键词
            for keyword in relevant_keywords:
                if keyword in title or keyword in summary:
                    relevant_papers.append(paper)
                    break
        
        print(f"原始论文数: {len(papers)}, 相关论文数: {len(relevant_papers)}")
        return relevant_papers
    
    def get_daily_papers(self, categories: List[str] = None) -> List[Dict[str, Any]]:
        """获取每日最新论文（备用方法）"""
        if categories is None:
            categories = self.config["search_categories"]
        
        papers = []
        try:
            import sys
            sys.path.append('/root/agent/skills/arxiv-paper')
            from arxiv_paper_skill import get_daily_latest
            
            # 调用arxiv-paper skill的每日论文函数
            for category in categories:
                category_papers = get_daily_latest(category, days=1)
                papers.extend(category_papers)
                
        except ImportError:
            print("无法导入arxiv-paper skill，使用备用搜索方法")
            papers = self.search_papers()
        
        return papers


def main():
    """测试函数"""
    searcher = ArXivSearcher()
    
    print("开始搜索推荐系统论文...")
    papers = searcher.search_papers()
    
    if not papers:
        print("使用备用方法搜索...")
        papers = searcher.get_daily_papers()
    
    relevant_papers = searcher.filter_relevant_papers(papers)
    
    print(f"\n搜索结果:")
    print(f"总共找到 {len(papers)} 篇论文")
    print(f"其中 {len(relevant_papers)} 篇与推荐系统相关")
    
    if relevant_papers:
        print("\n前5篇相关论文:")
        for i, paper in enumerate(relevant_papers[:5], 1):
            print(f"{i}. {paper['title']}")
            print(f"   作者: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
            print(f"   时间: {paper['published']}")
            print(f"   arXiv ID: {paper['arxiv_id']}")
            print()


if __name__ == "__main__":
    main()