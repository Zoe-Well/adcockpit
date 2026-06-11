# Research Notes: AdCockpit Implementation

**Feature**: 001-adcockpit-system-spec
**Date**: 2026-06-09

## Decision 1: Streamlit Three-Column Layout with Custom CSS

**Decision**: Use `st.columns([0.25, 0.40, 0.35])` for the three-column layout,
combined with `st.markdown("""<style>...</style>""", unsafe_allow_html=True)` for
deep custom CSS (dark theme, metric cards, step cards, chat bubbles).

**Rationale**: Streamlit natively supports multi-column layouts but its default
theme is light/clean. To precisely replicate the HTML prototype's dark control-panel
aesthetic (background `#0f1117`, accent `#4c6ef5`, status colors), CSS injection
via `unsafe_allow_html=True` is the most practical approach without ejecting to
a custom frontend framework.

**Alternatives considered**:
- Gradio: Better for ML demos but less flexible for complex multi-panel layouts.
- Custom React SPA + FastAPI: Higher fidelity but violates Constitution Principle IV
  (Streamlit-first). Rejected for Demo scope.
- Streamlit custom component (React-based): Possible but adds build complexity;
  CSS injection achieves 90%+ fidelity with zero build step.

## Decision 2: WebSocket via `streamlit-websocket` or asyncio loop

**Decision**: Use two layers — FastAPI WebSocket endpoint (`/ws/{session_id}`) for
LangGraph state streaming, and a long-polling fallback in Streamlit via
`st.rerun()` + `time.sleep()` trigger pattern. The LangGraph `astream_events()`
API emits step-level events that map 1:1 to TraceBoard step cards.

**Rationale**: Streamlit does not natively support persistent WebSocket connections
from the browser. The recommended pattern: LangGraph runs on FastAPI (separate
thread/process), streams events to a shared queue, and Streamlit polls the queue
via a lightweight REST endpoint or an embedded WebSocket client in the backend.

**Alternatives considered**:
- `streamlit-ws` component: Exists but immature; risk of breaking on Streamlit updates.
- Pure FastAPI + Jinja2 templates: Better WebSocket support but violates Streamlit-first
  constraint.
- SSE (Server-Sent Events): Simpler than WebSocket, sufficient for one-way state push.
  **Chosen as primary mechanism** — LangGraph → SSE → Streamlit `st.session_state` polling.

## Decision 3: Mock Data Architecture

**Decision**: All 24 Mock functions defined in a single `tools/mock_functions.py`
module, organized by domain (`# Ad Placement`, `# Content`, `# Ecommerce`,
`# Data Analysis`, `# Notification`). Each function uses `random.random()` to
trigger exceptions at configured probabilities (10% business, 5% network).
Mock data constants (plan names, ROI values, etc.) defined in `tools/mock_data.py`
to guarantee consistency with the HTML prototype.

**Rationale**: Centralized mock data seed allows the prototype HTML, Streamlit UI,
and pytest suites to reference identical values. Single-file tool organization
keeps the codebase AI-coding-friendly (one file per concept).

**Mock Data Inventory (from prototype)**:
```
douyin_plans = [
  {id:"C001", name:"夏季促销-A", cost:15200, roi:1.5, bid:25.0},
  {id:"C002", name:"新品首发-B", cost:14100, roi:2.3, bid:30.0},
  {id:"C003", name:"爆款返场-C", cost:12800, roi:3.1, bid:22.0},
  {id:"C004", name:"品牌日-D",   cost:9600,  roi:1.8, bid:20.0},
  {id:"C005", name:"直播引流-E", cost:8800,  roi:2.5, bid:18.0},
]
tencent_plans = [
  {id:"T001", name:"618大促",   cost:12800, roi:1.2, bid:30.0},
  {id:"T002", name:"会员日",    cost:11000, roi:2.8, bid:28.0},
  {id:"T003", name:"达人种草",  cost:9500,  roi:3.5, bid:24.0},
  {id:"T004", name:"品宣视频",  cost:8200,  roi:2.1, bid:21.0},
  {id:"T005", name:"直播切片",  cost:7600,  roi:2.6, bid:19.0},
]
```

## Decision 4: LangGraph StateGraph Structure

**Decision**: Implement the full AgentState TypedDict as defined in the spec.
Use `add_node()` for all 8 agents. Use `add_conditional_edges()` from Supervisor
to route to the correct downstream agent based on `current_scene`. Use
`add_edge()` for linear chains (Data→Analysis→Strategy→Execute→Report).
Implement Human-in-the-loop via `interrupt()` before Execute node when
`requires_approval` is True.

**Rationale**: LangGraph's `interrupt()` and `Command(resume=...)` provide
first-class HITL support. The DAG topology matches the spec's Agent协作图 exactly.

## Decision 5: SSE (Server-Sent Events) for Real-Time Streaming

**Decision**: Use `sse-starlette` on FastAPI to emit step-level events.
Streamlit runs a background thread that connects to the SSE endpoint and
writes events into `st.session_state["trace_events"]`.

**Event format**:
```json
{"event": "step_update", "data": {"node": "data_agent", "status": "running", "tool": "get_top_campaigns", "platform": "douyin", "ts": "2026-06-09T10:00:02"}}
```

**Rationale**: SSE is simpler than WebSocket for one-directional state push,
natively supported by FastAPI, and sufficient for this Demo's needs.

## Decision 6: Testing Strategy

**Decision**: Use `pytest` with `pytest-asyncio` for async tests. Each of the 5
user scenarios gets a dedicated test module under `tests/scenarios/`. Mock LLM
calls via `unittest.mock.patch` to avoid actual API costs. SSE events are captured
via `httpx.AsyncClient` streaming. Test assertions verify: (a) correct AgentState
transitions, (b) SSE events emitted in expected order, (c) Mock data matches prototype.
