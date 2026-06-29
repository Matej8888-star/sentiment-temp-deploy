# -*- coding: utf-8 -*-
"""
=========================================================
报告生成器 - 飞书推送格式
=========================================================
职责：
  1. 将分析结果格式化为飞书消息
  2. 支持多种格式：简单/完整/紧凑
  3. 与现有飞书推送（CC Connect）对接

设计原则：
  - 纯函数，无状态
  - 返回字符串，由调用方决定如何推送
  - 兼容现有飞书消息格式

版本: 1.0.0
=========================================================
"""

from typing import Dict, Any, List

# =========================================================
# 格式模板
# =========================================================

SIMPLE_TEMPLATE = """📊 **{name}({code}) 舆情简报**

📅 分析日期：{date}
📈 情绪评分：**{score}/100** | 风险等级：**{risk_level}**
🎯 趋势判断：**{trend}** | 置信度：**{confidence}**

💡 核心结论：{conclusion}

⚠️ 风险提醒：
{risk_alerts}

📋 战法兼容：
{strategy_compat}

---
💬 {summary}
"""

FULL_TEMPLATE = """📊 **{name}({code}) 舆情简报** | 详细版

📅 分析日期：{date}
📈 情绪评分：**{score}/100** | 风险等级：**{risk_level}**
🎯 趋势判断：**{trend}** | 置信度：**{confidence}**

━━━━━━━━━━━━━━━━━━━━━
💡 核心结论
━━━━━━━━━━━━━━━━━━━━━
{conclusion}

空仓者：{advice_no_position}
持仓者：{advice_has_position}

━━━━━━━━━━━━━━━━━━━━━
📈 技术面速览
━━━━━━━━━━━━━━━━━━━━━
• 均线形态：{ma_alignment}
• 乖离率(MA5)：{bias_ma5}% | 状态：{bias_status}
• 量比：{volume_ratio} | {volume_status}
• 换手率：{turnover_rate}%

━━━━━━━━━━━━━━━━━━━━━
⚠️ 风险提醒
━━━━━━━━━━━━━━━━━━━━━
{all_risks}

━━━━━━━━━━━━━━━━━━━━━
📋 战法兼容性
━━━━━━━━━━━━━━━━━━━━━
• VCP：{vcp_status}
• OneTwo：{onetwo_status}
• Chokepoint：{chokepoint_status}
{strategy_notes}

━━━━━━━━━━━━━━━━━━━━━
📰 舆情摘要
━━━━━━━━━━━━━━━━━━━━━
{sentiment_summary}

━━━━━━━━━━━━━━━━━━━━━
💬 综合摘要
━━━━━━━━━━━━━━━━━━━━━
{summary}

---
🤖 数据来源：{data_source}
⚡ 版本：v{version}
"""

COMPACT_TEMPLATE = "{emoji}[{name}]评分:{score}|风险:{risk_level}|{conclusion}"

# =========================================================
# Emoji 映射
# =========================================================

RISK_LEVEL_EMOJI = {
    "safe": "🟢",
    "caution": "🟡",
    "warning": "🟠",
    "danger": "🔴"
}

TREND_EMOJI = {
    "强烈看多": "📈📈",
    "看多": "📈",
    "震荡": "↔️",
    "看空": "📉",
    "强烈看空": "📉📉"
}

STRATEGY_STATUS = {
    True: "✅ 兼容",
    False: "❌ 不兼容"
}

# =========================================================
# 核心函数
# =========================================================

def format_simple(result: Dict[str, Any]) -> str:
    """
    简单格式（适合手机快速浏览）
    
    Args:
        result: 分析结果字典
        
    Returns:
        格式化字符串
    """
    code = result.get("code", "")
    name = result.get("name", code)
    
    # 风险提醒
    risk_check = result.get("risk_check", {})
    tech_risks = risk_check.get("technical_risks", [])
    sent_risks = risk_check.get("sentiment_risks", [])
    all_risks = tech_risks + sent_risks
    
    if all_risks:
        risk_text = "\n".join(f"• {r}" for r in all_risks[:3])
    else:
        risk_text = "• 暂无显著风险"
    
    # 战法兼容
    dashboard = result.get("dashboard", {})
    alignment = dashboard.get("alignment_with_strategies", {})
    
    compat_lines = []
    if alignment.get("vcp_compatible"):
        compat_lines.append("• VCP ✅")
    if alignment.get("one_two_compatible"):
        compat_lines.append("• OneTwo ✅")
    if alignment.get("chokepoint_compatible"):
        compat_lines.append("• Chokepoint ✅")
    
    if not compat_lines:
        compat_lines.append("• 与主要战法均不兼容，建议观望")
    
    return SIMPLE_TEMPLATE.format(
        name=name,
        code=code,
        date=result.get("_timestamp", ""),
        score=result.get("sentiment_score", 50),
        risk_level=risk_check.get("overall_level", "unknown"),
        trend=result.get("trend_prediction", "震荡"),
        confidence=result.get("confidence_level", "中"),
        conclusion=_get_core_conclusion(result),
        risk_alerts=risk_text,
        strategy_compat="\n".join(compat_lines),
        summary=result.get("analysis_summary", "")[:200]
    )


def format_full(result: Dict[str, Any]) -> str:
    """
    完整格式（适合 PC 端详细查看）
    
    Args:
        result: 分析结果字典
        
    Returns:
        格式化字符串
    """
    code = result.get("code", "")
    name = result.get("name", code)
    dashboard = result.get("dashboard", {})
    core = dashboard.get("core_conclusion", {})
    data_perspective = dashboard.get("data_perspective", {})
    price_pos = data_perspective.get("price_position", {})
    vol_analysis = data_perspective.get("volume_analysis", {})
    risk_check = result.get("risk_check", {})
    alignment = dashboard.get("alignment_with_strategies", {})
    
    # 持仓建议
    pos_advice = core.get("position_advice", {})
    
    # 风险汇总
    tech_risks = risk_check.get("technical_risks", [])
    sent_risks = risk_check.get("sentiment_risks", [])
    all_risks = tech_risks + sent_risks
    
    if all_risks:
        risk_text = "\n".join(f"• {r}" for r in all_risks)
    else:
        risk_text = "• 暂无显著风险"
    
    return FULL_TEMPLATE.format(
        name=name,
        code=code,
        date=result.get("_timestamp", ""),
        score=result.get("sentiment_score", 50),
        risk_level=risk_check.get("overall_level", "unknown"),
        trend=result.get("trend_prediction", "震荡"),
        confidence=result.get("confidence_level", "中"),
        conclusion=_get_core_conclusion(result),
        advice_no_position=pos_advice.get("no_position", "观望"),
        advice_has_position=pos_advice.get("has_position", "持有"),
        ma_alignment=data_perspective.get("trend_status", {}).get("ma_alignment", "未知"),
        bias_ma5=price_pos.get("bias_ma5", "N/A"),
        bias_status=price_pos.get("bias_status", "未知"),
        volume_ratio=vol_analysis.get("volume_ratio", "N/A"),
        volume_status=vol_analysis.get("volume_status", "未知"),
        turnover_rate=vol_analysis.get("turnover_rate", "N/A"),
        all_risks=risk_text,
        vcp_status=STRATEGY_STATUS.get(alignment.get("vcp_compatible"), "❓"),
        onetwo_status=STRATEGY_STATUS.get(alignment.get("one_two_compatible"), "❓"),
        chokepoint_status=STRATEGY_STATUS.get(alignment.get("chokepoint_compatible"), "❓"),
        strategy_notes=f"\n💡 {alignment.get('notes', '')}" if alignment.get("notes") else "",
        sentiment_summary=dashboard.get("intelligence", {}).get("sentiment_summary", "暂无"),
        summary=result.get("analysis_summary", "")[:300],
        data_source=result.get("_source", "sentiment_analysis"),
        version=result.get("_version", "1.0.0")
    )


def format_compact(result: Dict[str, Any]) -> str:
    """
    紧凑格式（适合多股票批量推送，一行一条）
    
    Args:
        result: 分析结果字典
        
    Returns:
        单行字符串
    """
    code = result.get("code", "")
    name = result.get("name", code)
    score = result.get("sentiment_score", 50)
    risk_level = result.get("risk_check", {}).get("overall_level", "unknown")
    conclusion = _get_core_conclusion(result)[:30]
    
    emoji = RISK_LEVEL_EMOJI.get(risk_level, "⚪")
    
    return COMPACT_TEMPLATE.format(
        emoji=emoji,
        name=name,
        score=score,
        risk_level=risk_level,
        conclusion=conclusion
    )


def format_batch(
    results: List[Dict[str, Any]],
    format_type: str = "compact"
) -> str:
    """
    批量格式化多个股票的分析结果
    
    Args:
        results: 分析结果列表
        format_type: 格式类型 compact/simple/full
        
    Returns:
        格式化字符串
    """
    if not results:
        return "📊 舆情简报：暂无数据"
    
    if format_type == "compact":
        lines = [format_compact(r) for r in results]
        return "📊 **持仓舆情简报**\n\n" + "\n".join(lines)
    
    elif format_type == "simple":
        sections = [format_simple(r) for r in results]
        return "\n\n---\n\n".join(sections)
    
    else:  # full
        sections = [format_full(r) for r in results]
        return "\n\n" + "=" * 40 + "\n\n".join(sections)


# =========================================================
# 辅助函数
# =========================================================

def _get_core_conclusion(result: Dict[str, Any]) -> str:
    """获取核心结论（一句话）"""
    dashboard = result.get("dashboard", {})
    core = dashboard.get("core_conclusion", {})
    
    if core and core.get("one_sentence"):
        return core["one_sentence"]
    
    return result.get("analysis_summary", "暂无结论")[:50]


def build_feishu_message(
    results: List[Dict[str, Any]],
    format_type: str = "simple",
    title: str = "📊 每日舆情简报"
) -> str:
    """
    构建飞书消息（兼容现有 CC Connect 格式）
    
    Args:
        results: 分析结果列表
        format_type: 格式类型
        title: 消息标题
        
    Returns:
        飞书消息文本
    """
    body = format_batch(results, format_type)
    
    return f"""{title}

{body}

---
⏰ 生成时间：{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}
🤖 来源：舆情分析模块 v1.0.0
⚠️ 仅供参考，不构成投资建议
"""


# =========================================================
# 便捷函数
# =========================================================

def quick_report(result: Dict[str, Any]) -> str:
    """
    快速生成单只股票报告
    
    使用方式:
        report = quick_report(analyzer.analyze("600519"))
        send_to_feishu(report)
    """
    return format_simple(result)


def daily_batch_report(results: List[Dict[str, Any]]) -> str:
    """
    生成每日批量报告
    
    使用方式:
        results = analyzer.analyze_portfolio(portfolio)
        report = daily_batch_report(results)
        send_to_feishu(report)
    """
    return build_feishu_message(results, format_type="compact")
