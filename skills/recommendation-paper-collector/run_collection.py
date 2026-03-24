#!/usr/bin/env python3
"""
运行推荐系统论文收集任务
专门用于整理过去一周pretrain相关的推荐系统论文
"""

import sys
import os
from main import RecommendationPaperCollector


def main():
    """运行论文收集任务"""
    print("=" * 70)
    print("🤖 推荐系统论文收集器 - Pretrain专题")
    print("=" * 70)
    
    # 创建收集器
    collector = RecommendationPaperCollector()
    
    # 更新配置，专注于pretrain
    collector.config["keywords"] = [
        "pretrain", "pretraining", "pre-train", "pre-training",
        "recommendation", "recommender", 
        "large language model", "LLM",
        "foundation model", "transfer learning"
    ]
    
    # 运行收集任务
    print("\n🔍 搜索参数:")
    print(f"   时间范围: 最近{collector.config['days_back']}天")
    print(f"   搜索分类: {', '.join(collector.config['search_categories'])}")
    print(f"   关键词: {', '.join(collector.config['keywords'][:5])}...")
    print(f"   最大论文数: {collector.config['max_papers']}")
    
    print("\n🔄 开始收集论文...")
    
    result = collector.run(
        days_back=7,          # 过去一周
        max_papers=15,        # 最多15篇
        sheet_url="https://docs.google.com/spreadsheets/d/1TW-NubPwQCrhVvV1maV4KQRYfjoJ39e1V_L_Tx6oPrQ",
        sheet_name="推荐系统热点论文",
        clear_first=True      # 清空后重新写入
    )
    
    print("\n" + "=" * 70)
    
    if result["success"]:
        stats = result["stats"]
        print("🎉 任务成功完成!")
        print(f"📊 统计数据:")
        print(f"   搜索论文: {stats['total_searched']}篇")
        print(f"   相关论文: {stats['relevant_found']}篇")
        print(f"   处理论文: {stats['processed']}篇")
        print(f"   写入论文: {stats['written']}篇")
        print(f"⏱️  总耗时: {result.get('duration_seconds', 0):.1f}秒")
        
        if result.get("sheet_url"):
            print(f"🔗 查看结果: {result['sheet_url']}")
    else:
        print("❌ 任务失败!")
        print(f"错误信息: {result.get('error', '未知错误')}")
    
    print("=" * 70)
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())