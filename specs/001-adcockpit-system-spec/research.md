# Research Notes: AdCockpit v2.0

**Feature**: 001-adcockpit-system-spec
**Date**: 2026-06-13

## Decision 1: React + shadcn/ui vs Streamlit

**Decision**: React 18 + shadcn/ui + Tailwind CSS.
**Rationale**: Constitution v2.0 mandates production-grade architecture. React with shadcn/ui
provides full control over UI rendering (necessary for the three-column cockpit), streaming
WebSocket support, and enterprise component quality.
**Alternatives**: Streamlit (v1 — lacked pixel-level control), Vue (less ecosystem for shadcn).

## Decision 2: Celery + Redis for Async Tasks

**Decision**: Celery with Redis broker.
**Rationale**: Agent execution can take 10-60s. HTTP request must return immediately,
agent runs in Celery worker, WebSocket pushes progress. Redis serves dual role as
Celery broker + session short-term memory.
**Alternatives**: RQ (simpler but less mature), Dramatiq.

## Decision 3: Chroma for RAG Long-Term Memory

**Decision**: Chroma vector database, DeepSeek embeddings.
**Rationale**: Lightweight, Python-native, no separate server needed (embedded mode).
Stores historical optimization records, campaign templates, and diagnostic cases.
**Alternatives**: Pinecone (cloud-only), Weaviate (heavier), FAISS (file-based).

## Decision 4: WebSocket for Real-Time Agent Streaming

**Decision**: FastAPI WebSocket, one connection per session.
**Rationale**: Full-duplex, low latency. Each agent step emits a JSON message
`{type, node, content, ts}`. Frontend renders progressively.
**Alternatives**: SSE (one-way), polling (latency).

## Decision 5: DeepSeek Model Integration

**Decision**: DeepSeek-v3 via langchain-openai compatible endpoint.
**Rationale**: Cost-effective, Chinese-optimized, supports Function Calling.
Endpoint: `https://api.deepseek.com/v1` (OpenAI-compatible).
**Alternatives**: GPT-4o (more expensive), Claude (via Anthropic API).

## Decision 6: Docker Compose Deployment

**Decision**: Single `docker-compose.yml` for all services.
**Rationale**: One-command start (`docker compose up`), consistent environment,
isolated dependencies. Services: frontend, backend, celery-worker, redis, chroma.
