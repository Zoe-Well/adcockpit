# Quickstart: AdCockpit v2.0

**Feature**: 001-adcockpit-system-spec
**Date**: 2026-06-13

## Prerequisites

- Docker + Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.11+ (for local backend dev)
- Redis (for Celery broker + session)

## One-Command Start (Docker)

```bash
docker compose up
```

Opens `http://localhost:3000` (frontend) and `http://localhost:8000` (backend).

## Local Dev Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload
```

### Celery Worker

```bash
cd backend
celery -A app.tasks worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Redis (required for session + Celery)

```bash
redis-server
```

### Chroma (for RAG)

```bash
chroma run --path ./chroma_data
```

## Environment Variables (.env)

```bash
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
REDIS_URL=redis://localhost:6379
CHROMA_HOST=localhost
CHROMA_PORT=8001
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
```

## Verification

1. Open `http://localhost:3000` — three-column cockpit renders
2. Type "检查最近7天抖音ROI" in chat → agent responds with parameter card
3. Click "开始优化" → Trace Board animates → Dashboard updates
4. Type "你好" → conversational reply, no parameter card
