# Implementation Plan: AdCockpit v2.0

**Branch**: `001-adcockpit-system-spec` | **Date**: 2026-06-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-adcockpit-system-spec/spec.md`

## Summary

Complete rewrite of AdCockpit with a production-grade full-stack architecture:
**React 18 + shadcn/ui + Tailwind CSS** frontend, **FastAPI + LangGraph + DeepSeek** backend,
**Celery + Redis** async task queue, **Chroma** vector DB for RAG long-term memory.
The front-to-back WebSocket streaming enables real-time display of Agent thinking processes.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, LangGraph 1.0+, LangChain 1.2+, DeepSeek, Celery, Redis, Chroma, React 18, shadcn/ui, Tailwind CSS
**Storage**: Redis (short-term session, TTL 1h), Chroma (long-term RAG embeddings)
**Testing**: pytest + pytest-asyncio (backend), Vitest + React Testing Library (frontend)
**Target Platform**: Web browser (1920×1080), Docker Compose deployment
**Project Type**: Web app (React SPA + FastAPI REST/WS + Celery Worker)
**Performance Goals**: Agent startup <3s, WebSocket latency <500ms, RAG retrieval <1s
**Constraints**: 95% AI-generated code, Docker Compose one-command start
**Scale/Scope**: 10 concurrent users, 8 agent nodes, 24 tools, 4 business domains

## Constitution Check

| Principle | Requirement | Status |
|-----------|-------------|--------|
| I. 三栏驾驶舱 | 30% Chat / 28% Trace / 42% Dashboard | ✅ PASS — React shadcn/ui 组件实现 |
| II. Multi-Agent | LangGraph StateGraph + HITL | ✅ PASS |
| III. 四大业务域 | Ad / Content / Ecommerce / Data | ✅ PASS |
| IV. AI-First + 生产级 | React+shadcn+Tailwind / FastAPI+LangGraph+DeepSeek / Celery+Redis / Chroma+RAG | ✅ PASS |
| V. Mock-First | 24 Mock 函数保留 | ✅ PASS |

## Project Structure

```
adcockpit/
├── frontend/                # React 18 + shadcn/ui + Tailwind
│   ├── src/
│   │   ├── components/      # UI components
│   │   │   ├── chat/        # ChatPanel, ChatInput, ChatBubble, ApprovalCard
│   │   │   ├── trace/       # FlowTracker, StepCard, TraceBoard
│   │   │   ├── dashboard/   # MetricCard, ChartWidget, CampaignTable, AlertList
│   │   │   └── ui/          # shadcn/ui primitives
│   │   ├── hooks/           # useWebSocket, useAgent, useCampaigns
│   │   ├── lib/             # API client, utils
│   │   ├── pages/           # App layout (sidebar + 3 columns)
│   │   └── types/           # TypeScript type definitions
│   ├── package.json
│   └── tailwind.config.ts
│
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI routes
│   │   │   ├── chat.py      # Chat + intent endpoints
│   │   │   ├── campaigns.py # Campaign CRUD + optimize
│   │   │   ├── content.py   # Content generation + Feishu
│   │   │   └── ws.py        # WebSocket handler
│   │   ├── agents/          # LangGraph agent nodes (8 agents)
│   │   │   ├── graph.py     # StateGraph builder
│   │   │   ├── supervisor.py
│   │   │   ├── data_agent.py
│   │   │   ├── analysis_agent.py
│   │   │   ├── strategy_agent.py
│   │   │   ├── content_agent.py
│   │   │   ├── ecommerce_agent.py
│   │   │   ├── execute_agent.py
│   │   │   └── report_agent.py
│   │   ├── tools/           # 24 Mock tools + Feishu client
│   │   ├── memory/          # Redis session + Chroma RAG
│   │   ├── tasks/           # Celery task definitions
│   │   └── core/            # Config, settings
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml       # frontend + backend + redis + celery + chroma
└── .env
```

## Implementation Stages

### Stage 1: Backend Core (FastAPI + LangGraph + DeepSeek)
- LangGraph StateGraph with 8 agent nodes
- DeepSeek model integration via langchain-openai
- FastAPI REST endpoints (/api/campaigns, /api/content, /api/intent)
- 24 Mock tools migrated + Feishu client

### Stage 2: Celery + Redis + WebSocket
- Celery task queue for async agent execution
- Redis session storage (TTL 1h)
- WebSocket endpoint for real-time agent thinking push
- Task status polling + result retrieval

### Stage 3: Chroma Vector DB + RAG
- Chroma collection for historical optimization records
- DeepSeek embeddings for document indexing
- RAG retrieval in Strategy Agent and Report Agent

### Stage 4: React Frontend
- shadcn/ui component library setup
- Three-column layout (Chat / Trace / Dashboard)
- WebSocket stream rendering (FlowTracker + StepCard animation)
- Metric cards, bar charts, paginated tables

### Stage 5: Docker Compose + Testing
- Docker Compose one-command start
- Backend pytest + frontend Vitest
- End-to-end scenario testing
