"""REST API routes for AdCockpit."""
import json
import uuid
import asyncio
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()


# ----- Request/Response Models -----
class ExecuteRequest(BaseModel):
    user_input: str
    session_id: Optional[str] = None


class ExecuteResponse(BaseModel):
    session_id: str
    status: str
    current_scene: str
    task_graph: list = []


class ApprovalResponse(BaseModel):
    session_id: str
    status: str
    message: str = ""


# ----- In-memory state store (Demo) -----
# Stores latest AgentState per session for GET /session/{sid}/state
SESSION_STATES: dict = {}


def _resolve_sse_manager(request: Request):
    """Get SSEManager from app state."""
    return request.app.state.sse_manager


def _run_graph(session_id: str, user_input: str, sse_manager) -> dict:
    """Run the LangGraph agent graph with SSE event streaming.

    This is a synchronous wrapper that runs the async graph execution
    in a thread and emits SSE events for each step.

    Returns the final AgentState dict.
    """
    # Build initial state
    from agents.state import AgentState
    from agents.supervisor import supervisor_node
    from agents.data_agent import data_agent_node
    from agents.analysis_agent import analysis_agent_node
    from agents.strategy_agent import strategy_agent_node
    from agents.content_agent import content_agent_node
    from agents.ecommerce_agent import ecommerce_agent_node
    from agents.execute_agent import execute_agent_node
    from agents.report_agent import report_agent_node

    start_time = datetime.now().isoformat()

    # === Supervisor ===
    sse_manager.emit_sync(session_id, "step_start", {"node": "supervisor", "ts": datetime.now().isoformat()})
    state: AgentState = {
        "user_input": user_input,
        "task_graph": [],
        "platform_data": [],
        "analysis_result": {},
        "strategy_actions": [],
        "execution_results": [],
        "report": {},
        "pending_approval": None,
        "conversation_history": [],
        "error_log": [],
        "session_id": session_id,
        "current_scene": "ad_placement",
    }
    result = supervisor_node(state)
    state.update(result)
    sse_manager.emit_sync(session_id, "step_complete", {
        "node": "supervisor", "status": "done", "scene": state["current_scene"],
        "task_count": len(state["task_graph"]), "ts": datetime.now().isoformat(),
    })

    # === Data Agent ===
    sse_manager.emit_sync(session_id, "step_start", {"node": "data_agent", "ts": datetime.now().isoformat()})
    result = data_agent_node(state)
    state.update(result)
    for pd in state.get("platform_data", []):
        sse_manager.emit_sync(session_id, "step_update", {
            "node": "data_agent", "status": "running", "platform": pd["platform"],
            "tool": pd["endpoint"], "ts": datetime.now().isoformat(),
        })
    sse_manager.emit_sync(session_id, "step_complete", {
        "node": "data_agent", "status": "done", "platform_count": len(state.get("platform_data", [])),
        "ts": datetime.now().isoformat(),
    })

    # === Analysis Agent ===
    sse_manager.emit_sync(session_id, "step_start", {"node": "analysis_agent", "ts": datetime.now().isoformat()})
    result = analysis_agent_node(state)
    state.update(result)
    sse_manager.emit_sync(session_id, "step_complete", {
        "node": "analysis_agent", "status": "done",
        "anomaly_count": len(state.get("analysis_result", {}).get("anomalies", [])),
        "ts": datetime.now().isoformat(),
    })

    # === Route: Strategy / Content / Ecommerce ===
    scene = state["current_scene"]
    if scene in ("ad_placement", "data_analysis"):
        sse_manager.emit_sync(session_id, "step_start", {"node": "strategy_agent", "ts": datetime.now().isoformat()})
        result = strategy_agent_node(state)
        state.update(result)
        sse_manager.emit_sync(session_id, "step_complete", {
            "node": "strategy_agent", "status": "done",
            "action_count": len(state.get("strategy_actions", [])),
            "ts": datetime.now().isoformat(),
        })
    elif scene == "content":
        sse_manager.emit_sync(session_id, "step_start", {"node": "content_agent", "ts": datetime.now().isoformat()})
        result = content_agent_node(state)
        state.update(result)
        sse_manager.emit_sync(session_id, "step_complete", {
            "node": "content_agent", "status": "done", "ts": datetime.now().isoformat(),
        })
    elif scene == "ecommerce":
        sse_manager.emit_sync(session_id, "step_start", {"node": "ecommerce_agent", "ts": datetime.now().isoformat()})
        result = ecommerce_agent_node(state)
        state.update(result)
        sse_manager.emit_sync(session_id, "step_complete", {
            "node": "ecommerce_agent", "status": "done", "ts": datetime.now().isoformat(),
        })

    # === Execute Agent (with approval check) ===
    pending = state.get("pending_approval")
    if pending:
        sse_manager.emit_sync(session_id, "approval_required", {
            "actions": pending,
            "ts": datetime.now().isoformat(),
        })
        # Store state for later resume
        SESSION_STATES[session_id] = dict(state)
        return state

    sse_manager.emit_sync(session_id, "step_start", {"node": "execute_agent", "ts": datetime.now().isoformat()})
    result = execute_agent_node(state)
    state.update(result)
    sse_manager.emit_sync(session_id, "step_complete", {
        "node": "execute_agent", "status": "done",
        "results": len(state.get("execution_results", [])),
        "ts": datetime.now().isoformat(),
    })

    # === Report Agent ===
    sse_manager.emit_sync(session_id, "step_start", {"node": "report_agent", "ts": datetime.now().isoformat()})
    result = report_agent_node(state)
    state.update(result)
    sse_manager.emit_sync(session_id, "step_complete", {
        "node": "report_agent", "status": "done", "ts": datetime.now().isoformat(),
    })

    # === Complete ===
    sse_manager.emit_sync(session_id, "execution_complete", {
        "session_id": session_id,
        "summary": state.get("report", {}).get("summary", []),
        "ts": datetime.now().isoformat(),
    })

    SESSION_STATES[session_id] = dict(state)
    return state


# ----- Optimization & Content endpoints -----

class OptimizeRequest(BaseModel):
    session_id: str
    platforms: list = ["douyin", "tencent"]
    days: int = 7
    top_n: int = 5
    roi_threshold: float = 2.0
    bid_adjust_pct: int = -10
    budget_adjust_pct: int = -20
    risk_confirm: str = "medium"


@router.post("/optimize")
async def optimize(request: Request, body: OptimizeRequest):
    """Run optimization with parameters, return results + Feishu URL."""
    import sys; sys.path.insert(0, ".")
    from tools.mock_functions import get_top_campaigns, update_bid, update_budget
    from tools.feishu_client import publish_optimization_report

    sse = _resolve_sse_manager(request)
    sid = body.session_id
    sse.create_session(sid)

    ts = datetime.now().isoformat()
    # Streaming events
    for node in ["supervisor", "data", "data_2", "analysis", "strategy"]:
        sse.emit_sync(sid, "step_start", {"node": node, "ts": ts})
        sse.emit_sync(sid, "step_complete", {"node": node, "status": "done", "ts": ts})

    # Fetch and analyze
    all_plans = []
    for plat in body.platforms:
        plans = get_top_campaigns(plat, body.days, "cost", body.top_n)
        for p in plans:
            p["_platform"] = plat
        all_plans.extend(plans)

    below = [p for p in all_plans if p["roi"] < body.roi_threshold]
    changes = []

    # Execute optimizations
    for p in below:
        old_bid = p.get("bid", 0)
        new_bid = round(old_bid * (1 + body.bid_adjust_pct / 100.0), 1)
        update_bid(p.get("_platform", "douyin"), p["id"], new_bid)
        changes.append(f"{p['id']}: 出价 {old_bid}->{new_bid}")
        if p["roi"] < body.roi_threshold * 0.75:
            old_budget = p.get("budget", 0)
            new_budget = round(old_budget * (1 + body.budget_adjust_pct / 100.0))
            update_budget(p.get("_platform", "douyin"), p["id"], new_budget)
            changes.append(f"{p['id']}: 预算 {old_budget}->{new_budget}")

    # Publish report
    try:
        rows = [("分析计划", f"{len(all_plans)}条"), ("不达标", f"{len(below)}条"),
                ("调整项", f"{len(changes)}项")]
        report = publish_optimization_report(rows, changes)
        feishu_url = report.get("url", "")
    except Exception:
        feishu_url = ""

    sse.emit_sync(sid, "step_start", {"node": "execute", "ts": ts})
    sse.emit_sync(sid, "step_complete", {"node": "execute", "status": "done", "ts": ts})
    sse.emit_sync(sid, "step_start", {"node": "report", "ts": ts})
    sse.emit_sync(sid, "step_complete", {"node": "report", "status": "done", "ts": ts})
    sse.emit_sync(sid, "execution_complete", {"session_id": sid, "ts": ts})

    return {
        "session_id": sid, "status": "completed",
        "changes": changes, "below_count": len(below),
        "feishu_url": feishu_url,
    }


class ContentRequest(BaseModel):
    session_id: str
    platform: str = "douyin"
    date: str = "yesterday"
    top_n: int = 3
    worst_n: int = 3
    template_id: str = "summer_promo"
    auto_publish: bool = True


@router.post("/content")
async def content_produce(request: Request, body: ContentRequest):
    """Generate scripts and publish to Feishu, return URLs."""
    import sys; sys.path.insert(0, ".")
    from tools.mock_functions import generate_script
    from tools.feishu_client import publish_scripts

    sse = _resolve_sse_manager(request)
    sid = body.session_id
    sse.create_session(sid)
    ts = datetime.now().isoformat()

    for node in ["supervisor", "data", "analysis", "content"]:
        sse.emit_sync(sid, "step_start", {"node": node, "ts": ts})
        sse.emit_sync(sid, "step_complete", {"node": node, "status": "done", "ts": ts})

    scripts = []
    for i in range(body.top_n):
        for _ in range(3):
            try:
                s = generate_script(template_id=body.template_id, params={"product_name": f"爆款商品-{chr(65+i)}"})
                scripts.append(s)
                break
            except Exception:
                pass
        else:
            scripts.append(f"[生成失败]")

    urls = []
    if body.auto_publish:
        try:
            results = publish_scripts(scripts, body.platform, body.template_id)
            urls = [r.get("url", "") for r in results]
        except Exception:
            pass

    sse.emit_sync(sid, "step_start", {"node": "execute", "ts": ts})
    sse.emit_sync(sid, "step_complete", {"node": "execute", "status": "done", "ts": ts})
    sse.emit_sync(sid, "step_start", {"node": "report", "ts": ts})
    sse.emit_sync(sid, "step_complete", {"node": "report", "status": "done", "ts": ts})
    sse.emit_sync(sid, "execution_complete", {"session_id": sid, "ts": ts})

    return {
        "session_id": sid, "status": "completed",
        "scripts": scripts, "urls": urls,
    }


# ----- Routes -----
@router.post("/execute", response_model=ExecuteResponse)
async def execute(request: Request, body: ExecuteRequest):
    """Trigger Agent graph execution."""
    session_id = body.session_id or f"demo-{datetime.now().strftime('%m%d-%H%M%S')}"
    sse_manager = _resolve_sse_manager(request)
    sse_manager.create_session(session_id)

    # Run graph synchronously in thread
    state = await asyncio.to_thread(_run_graph, session_id, body.user_input, sse_manager)

    return ExecuteResponse(
        session_id=session_id,
        status="awaiting_approval" if state.get("pending_approval") else "completed",
        current_scene=state.get("current_scene", "ad_placement"),
        task_graph=state.get("task_graph", []),
    )


@router.post("/approve/{session_id}", response_model=ApprovalResponse)
async def approve(request: Request, session_id: str):
    """Approve pending actions and resume graph execution."""
    sse_manager = _resolve_sse_manager(request)
    state = SESSION_STATES.pop(session_id, None)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found or no pending approval")

    # Clear pending and execute
    actions = state.pop("pending_approval", [])
    state["pending_approval"] = None

    from agents.execute_agent import execute_actions
    results = execute_actions(actions, state)
    state["execution_results"] = results

    sse_manager.emit_sync(session_id, "step_complete", {
        "node": "execute_agent", "status": "done",
        "approved_count": len([r for r in results if r["status"] == "success"]),
        "ts": datetime.now().isoformat(),
    })

    # Run report
    from agents.report_agent import report_agent_node
    sse_manager.emit_sync(session_id, "step_start", {"node": "report_agent", "ts": datetime.now().isoformat()})
    result = report_agent_node(state)
    state.update(result)
    sse_manager.emit_sync(session_id, "step_complete", {
        "node": "report_agent", "status": "done", "ts": datetime.now().isoformat(),
    })

    sse_manager.emit_sync(session_id, "execution_complete", {
        "session_id": session_id,
        "summary": state.get("report", {}).get("summary", []),
        "ts": datetime.now().isoformat(),
    })

    SESSION_STATES[session_id] = state
    return ApprovalResponse(session_id=session_id, status="completed",
                            message=f"Approved {len(actions)} actions, execution complete")


@router.post("/reject/{session_id}", response_model=ApprovalResponse)
async def reject(request: Request, session_id: str):
    """Reject pending actions and skip execution."""
    sse_manager = _resolve_sse_manager(request)
    state = SESSION_STATES.pop(session_id, None)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found or no pending approval")

    actions = state.pop("pending_approval", [])
    state["pending_approval"] = None

    # Mark all as cancelled
    from agents.state import ExecutionResult
    for a in actions:
        state["execution_results"].append(ExecutionResult(
            action=a, status="cancelled", response=None, error="User rejected",
            retry_count=0, executed_at=datetime.now().isoformat(),
        ))

    sse_manager.emit_sync(session_id, "step_complete", {
        "node": "execute_agent", "status": "cancelled",
        "cancelled_count": len(actions), "ts": datetime.now().isoformat(),
    })

    SESSION_STATES[session_id] = state
    return ApprovalResponse(session_id=session_id, status="cancelled",
                            message=f"Rejected {len(actions)} actions")


@router.get("/session/{session_id}/state")
async def get_session_state(request: Request, session_id: str):
    """Get current AgentState snapshot for a session."""
    state = SESSION_STATES.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    # Convert non-serializable fields
    safe = {
        "session_id": state.get("session_id"),
        "current_scene": state.get("current_scene"),
        "execution_results": [dict(r) for r in state.get("execution_results", [])],
        "pending_approval": state.get("pending_approval"),
        "report": state.get("report", {}),
    }
    return safe


@router.get("/stream/{session_id}")
async def stream_events(request: Request, session_id: str):
    """SSE endpoint for real-time agent execution events."""
    sse_manager = _resolve_sse_manager(request)
    return StreamingResponse(
        sse_manager.stream(session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
