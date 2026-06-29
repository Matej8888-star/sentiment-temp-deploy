# -*- coding: utf-8 -*-
"""
=========================================================
舆情分析模块 (Sentiment Analysis)
=========================================================
从 DSA (daily_stock_analysis) 提取优化
集成到现有量化系统，提供舆情分析 + 风险预警能力

核心组件:
  - analyzer.py: 主入口，股票舆情分析
  - prompts.py: LLM Prompt 模板
  - risk_rules.py: 硬编码风险规则库
  - reporter.py: 报告生成器（飞书格式）

使用方式:
    from src.sentiment_analysis import SentimentAnalyzer
    
    analyzer = SentimentAnalyzer()
    if analyzer.is_enabled():
        result = analyzer.analyze("600519", "贵州茅台")
        print(result["sentiment_score"])
        print(result["risk_level"])

配置: config/sentiment.yaml
  - enabled: false (默认关闭，验证通过后设为 true)
  
版本: 1.0.0
=========================================================
"""

__version__ = "1.0.0"

# 便捷导入
from .analyzer import SentimentAnalyzer, analyze_stock, analyze_portfolio
from .reporter import (
    format_simple,
    format_full,
    format_compact,
    format_batch,
    build_feishu_message,
    quick_report,
    daily_batch_report
)
from .risk_rules import comprehensive_risk_check

__all__ = [
    # 分析器
    "SentimentAnalyzer",
    "analyze_stock",
    "analyze_portfolio",
    # 报告
    "format_simple",
    "format_full",
    "format_compact",
    "format_batch",
    "build_feishu_message",
    "quick_report",
    "daily_batch_report",
    # 风险规则
    "comprehensive_risk_check",
]
