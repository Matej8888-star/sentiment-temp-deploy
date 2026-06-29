# 舆情分析模块集成指南

## 概述

从 DSA (daily_stock_analysis) 提取的舆情分析模块，集成到你的量化系统中。

**核心能力：**
- AI 舆情分析（LLM 驱动）
- 硬编码风险规则（高位放量、缩量阴跌、乖离率警戒等）
- 战法兼容性评估（VCP / OneTwo / Chokepoint）
- 飞书推送集成

## 文件清单

```
sentiment_integration/
├── config/
│   └── sentiment.yaml          # 配置文件（enabled: false 默认关闭）
├── src/
│   └── sentiment_analysis/
│       ├── __init__.py         # 模块入口
│       ├── prompts.py          # LLM Prompt 模板
│       ├── risk_rules.py       # 风险规则库
│       ├── analyzer.py         # 核心分析器
│       └── reporter.py         # 报告生成器
├── tests/
│   └── test_sentiment_analysis.py  # 测试文件
└── INTEGRATION_GUIDE.md        # 本文件
```

## 集成步骤

### Step 1: 复制文件到项目

将以下文件复制到你的量化系统对应位置：

```bash
# 1. 配置文件
cp config/sentiment.yaml /path/to/your/project/config/

# 2. 源代码
cp -r src/sentiment_analysis /path/to/your/project/src/

# 3. 测试文件
cp tests/test_sentiment_analysis.py /path/to/your/project/tests/
```

### Step 2: 安装依赖

```bash
pip install pyyaml

# 如果需要 LLM 功能（可选）
pip install litellm
```

### Step 3: 配置

编辑 `config/sentiment.yaml`：

```yaml
# 开启模块
enabled: true

# 配置 LLM（如果使用 AI 分析）
llm:
  model: "gemini/gemini-2.0-flash"  # 你的模型
  api_key: ""                        # 从环境变量读取，或在此填写

# 配置数据源（复用现有）
data_source:
  primary: "qmt"      # 你的主数据源
  fallback: "baostock"
```

### Step 4: 在现有代码中调用

**方式一：在 DataOps 任务中添加**

```python
from src.sentiment_analysis import SentimentAnalyzer, daily_batch_report

# 初始化（配置决定enabled状态）
analyzer = SentimentAnalyzer()

if analyzer.is_enabled():
    # 分析持仓组合
    results = analyzer.analyze_portfolio(portfolio)
    
    # 生成飞书消息
    message = daily_batch_report(results)
    
    # 推送到飞书（复用你现有的 CC Connect）
    send_to_feishu(message)
```

**方式二：独立定时任务**

```python
# scripts/daily_sentiment.py
from src.sentiment_analysis import SentimentAnalyzer, daily_batch_report
from your_project.feishu import send_to_feishu  # 你的飞书推送

def main():
    analyzer = SentimentAnalyzer()
    
    if not analyzer.is_enabled():
        print("舆情分析未启用，跳过")
        return
    
    # 从系统读取持仓
    portfolio = load_portfolio()  # 你的持仓读取逻辑
    
    # 分析
    results = analyzer.analyze_portfolio(portfolio)
    
    # 推送
    if results:
        message = daily_batch_report(results)
        send_to_feishu(message)

if __name__ == "__main__":
    main()
```

**方式三：在回测前做舆情过滤**

```python
from src.sentiment_analysis import analyze_stock

# 回测前检查舆情
for code in watchlist:
    result = analyze_stock(code)
    if result and result.get("risk_level") == "danger":
        print(f"{code} 风险等级过高，跳过")
        continue
    
    # 执行回测
    run_backtest(code)
```

### Step 5: 添加到定时任务

Windows 任务计划（与你现有任务一致）：

```powershell
# 添加到每日 15:35 执行
$action = New-ScheduledTaskAction -Execute "python" -Argument "scripts/daily_sentiment.py"
$trigger = New-ScheduledTaskTrigger -Daily -At "15:35"
Register-ScheduledTask -TaskName "StockMonitor_Sentiment" -Action $action -Trigger $trigger
```

## 回退方案

**任何时候，将 `config/sentiment.yaml` 中的 `enabled` 设为 `false` 即可完全关闭模块，不影响现有系统任何功能。**

```yaml
enabled: false
```

## 配置说明

### enabled (bool)
- `false` (默认): 模块关闭，所有方法返回 None
- `true`: 模块启用

### llm.model (str)
- 空字符串: 仅使用硬编码风险规则（无 AI 分析）
- `"gemini/gemini-2.0-flash"`: Google Gemini
- `"openai/gpt-4o"`: OpenAI GPT-4o
- 其他 LiteLLM 支持的模型

### llm.api_key (str)
- 空字符串: 从环境变量读取 (`GEMINI_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`)
- 或填写实际 API Key

### risk_rules (dict)
- 所有阈值可配置，详见 `sentiment.yaml` 注释

## 测试

```bash
# 运行测试
pytest tests/test_sentiment_analysis.py -v

# 预期结果：
# - 禁用状态测试通过
# - Prompt 组装测试通过
# - 风险规则测试通过
# - 报告生成测试通过
# - 模拟 LLM 集成测试通过
```

## 与现有系统的边界

| 模块 | 舆情分析模块 | 现有系统 |
|------|-------------|---------|
| 数据源 | 复用（QMT/baostock/JQData） | 不变 |
| 飞书推送 | 复用（CC Connect） | 不变 |
| 持仓管理 | 读取（只读） | 不变 |
| 战法执行 | 兼容性评估（只读） | 不变 |
| 回测引擎 | 可调用（可选） | 不变 |
| 数据库 | 不操作 | 不变 |

**零侵入原则：** 舆情分析模块只读取数据，不写入任何现有系统的数据库或文件。

## 升级路径

### v1.0 -> v1.1（可选）
- 添加新闻抓取功能（从财经网站获取舆情）
- 添加板块/概念排名抓取

### v1.1 -> v1.2（可选）
- 添加舆情历史回测
- 添加舆情因子到回测引擎

### 回退到 v0（完全移除）
1. 删除 `src/sentiment_analysis/` 目录
2. 删除 `config/sentiment.yaml`
3. 删除调用代码
4. 完成，不影响任何现有功能
