# Quickstart: AdCockpit v1.0

**Feature**: 001-adcockpit-system-spec
**Date**: 2026-06-11

## Prerequisites

- Python 3.9+
- pip

## Setup

```bash
# Install dependencies
pip install streamlit requests python-dotenv
```

## Run (single command)

```bash
cd f:/IQA代码/Demo2
set PYTHONPATH=.
streamlit run ui/app.py
```

Open `http://localhost:8501` in browser (1920×1080 recommended).

## Optional: Feishu Integration

Copy `.env.example` to `.env` and fill in your Feishu app credentials:

```bash
FEISHU_APP_ID=cli_xxxxxxxx
FEISHU_APP_SECRET=xxxxxxxx
FEISHU_FOLDER_TOKEN=        # Optional
```

Without credentials, Feishu publishing falls back to mock mode (generates demo links).

## Architecture

```
Streamlit (8501) ──直接调用──→ Mock Functions + Feishu Client
```

No separate backend needed. Optimization, content production, and Feishu publishing all run directly within the Streamlit process.

## Six Tabs

| Tab | Scene | Function |
|-----|-------|----------|
| 🎯 优化 | ad_placement | Query campaigns → set ROI threshold → streaming animation → approve → execute optimization → Feishu report |
| 📊 投放 | create | Fill form → submit → streaming animation → confirm → campaign goes live |
| 🎬 内容 | content | Set params → preview scripts → streaming animation → confirm → publish to Feishu |
| 🛒 电商 | ecommerce | View live metrics, stock, coupons |
| 📈 数据 | data_analysis | Client ranking, budget proposals, PPT outline |
| 🔧 诊断 | diagnosis | Root cause analysis, recovery log |

## Key Files

| Layer | Files |
|-------|-------|
| UI | `ui/app.py` (main), `ui/panels/chat_panel.py`, `ui/panels/dashboard.py`, `ui/panels/trace_board.py`, `ui/theme.py` |
| Tools | `tools/mock_functions.py` (24 mock functions), `tools/mock_data.py` (seed data), `tools/feishu_client.py` (Feishu API) |
| Agents | `agents/supervisor.py` (intent classification), `agents/state.py` (TypedDict) |
| API | `api/` (FastAPI - optional, for content publishing to Feishu) |
| Mock Server | `mock_server/` (standalone mock REST API - optional) |
