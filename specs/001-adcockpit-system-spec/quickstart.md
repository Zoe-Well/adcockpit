# Quickstart: AdCockpit

**Feature**: 001-adcockpit-system-spec
**Date**: 2026-06-09

## Prerequisites

- Python 3.11+
- pip

## Setup

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt
```

## Run

```bash
# Start the FastAPI backend (LangGraph + SSE)
uvicorn api.main:app --reload --port 8000

# In a separate terminal, start the Streamlit frontend
streamlit run ui/app.py
```

Open `http://localhost:8501` in browser (1920×1080 recommended).

## Validation Scenarios

### Scenario 1: 跨平台广告投放优化 (MVP)

1. Open AdCockpit in browser
2. In the left chat panel, type: "检查最近7天在抖音和腾讯广告上，消耗排名Top5的计划里哪些ROI低于2，对不达标的计划自动降价10%，然后生成一份今日优化报告"
3. **Verify**:
   - Center panel shows DAG task bar with Supervisor→Data→Analysis→Strategy→Execute→Report
   - Data Agent steps appear in parallel (抖音 + 腾讯)
   - Analysis Agent highlights 3 plans with ROI < 2
   - Right dashboard shows 6 metric cards (ROI 1.87 red, Cost ¥37,600, CPA ¥38.5, Active 10, CTR 3.8%, CVR 4.2%)
   - ROI bar chart shows C001(1.5), T001(1.2), C004(1.8) in red bars
   - Left panel shows approval card with 4 actions
   - Click "确认执行" → Execute step runs → Report generated
   - Right panel shows report summary (saving ¥5,640/day, ROI→2.1)

### Scenario 2: 投后素材分析

1. Click "内容生产" scene tag, or type: "把昨天抖音上CTR最高和最低的3条视频找出来，分析爆款共性，生成3条新脚本，发布到飞书内容库"
2. **Verify**: Content dashboard view in right panel with video previews and script editor

### Scenario 3: 直播间场控

1. Type: "当前直播间在线2000人，商品A点击率高但转化率下跌。帮我查库存，低于50件自动补200件，创建限时10元优惠券，给主播生成催单话术"
2. **Verify**: Ecommerce dashboard with stock indicator (red→green), coupon progress bar, live script preview

### Scenario 4: 数据分析

1. Type: "拉取本月所有客户在抖音、腾讯、小红书的消耗、ROI、CPA，按客户汇总，找回报率最高3个最低2个客户，生成预算建议和PPT提纲"
2. **Verify**: Data dashboard with bar chart, customer ranking, PPT outline

### Scenario 5: 故障诊断

1. Type: "帮我排查计划12345为什么没量，出价问题就提价5%，审核被拒就通知我并替换备选视频"
2. **Verify**: Diagnosis dashboard with root cause card, recovery action log

## Run Tests

```bash
# Run all scenario tests
pytest tests/scenarios/ -v

# Run specific scenario
pytest tests/scenarios/test_scenario_1_ad_placement.py -v

# Run with coverage
pytest tests/scenarios/ -v --cov=tools --cov=agents
```

## Expected Test Output

Each scenario test asserts:
- AgentState transitions match expected path
- SSE events emitted in correct order (Supervisor→Data→...→Report)
- Mock data values match prototype (C001 ROI=1.5, T001 ROI=1.2, etc.)
- HITL interrupt fires when `requires_approval=True`
- Error paths handle 10% business / 5% network exception probabilities
