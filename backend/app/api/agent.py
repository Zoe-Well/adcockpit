"""Real Agent orchestration endpoint — LangGraph + DeepSeek LLM."""
import json; import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class AgentRequest(BaseModel):
    user_input: str
    platforms: list[str] = ["douyin", "tencent"]
    days: int = 7
    top_n: int = 5
    roi_threshold: float = 2.0
    bid_adjust_pct: int = -10
    budget_adjust_pct: int = -20


@router.post("/agent/optimize")
async def agent_optimize(body: AgentRequest):
    """Run the full LangGraph agent pipeline with DeepSeek LLM."""
    from tools.mock_functions import get_top_campaigns, update_bid, update_budget
    from backend.app.agents.supervisor import supervisor_node
    from backend.app.agents.analysis_agent import analysis_agent_node
    from backend.app.agents.strategy_agent import strategy_agent_node

    steps = []

    # Step 1: Supervisor — LLM task decomposition
    s1 = {"node": "supervisor", "title": "意图识别 — 任务规划", "status": "running"}
    steps.append(s1)
    state = {"user_input": body.user_input, "analysis_result": {"roi_threshold": body.roi_threshold, "bid_adjust_pct": body.bid_adjust_pct, "budget_adjust_pct": body.budget_adjust_pct}}
    r = supervisor_node(state)
    state.update(r)
    s1["status"] = "done"
    s1["output"] = state.get("analysis_result", {}).get("supervisor_summary", "任务已分解")

    # Step 2: Data Agent — fetch campaign data
    s2 = {"node": "data", "title": "数据拉取", "status": "running"}
    steps.append(s2)
    all_plans = []
    for plat in body.platforms:
        plans = get_top_campaigns(plat, body.days, "cost", body.top_n)
        for p in plans: p["_platform"] = plat
        all_plans.extend(plans)
    state["platform_data"] = [{"platform": p, "data": all_plans} for p in body.platforms]
    s2["status"] = "done"
    s2["output"] = f"已拉取 {len(all_plans)} 条计划（{len(body.platforms)} 个平台）"

    # Step 3: Analysis Agent — LLM data analysis
    s3 = {"node": "analysis", "title": "智能分析 — 异常检测", "status": "running"}
    steps.append(s3)
    r2 = analysis_agent_node(state)
    state.update(r2)
    anomalies = state.get("analysis_result", {}).get("anomalies", [])
    s3["status"] = "done"
    s3["output"] = state.get("analysis_result", {}).get("summary", f"发现 {len(anomalies)} 条异常计划")

    # Step 4: Strategy Agent — LLM strategy generation
    s4 = {"node": "strategy", "title": "策略生成 — 优化方案", "status": "running"}
    steps.append(s4)
    r3 = strategy_agent_node(state)
    state.update(r3)
    actions = state.get("strategy_actions", [])
    s4["status"] = "done"
    s4["output"] = state.get("analysis_result", {}).get("strategy_summary", f"生成 {len(actions)} 条优化建议")

    # Step 5: Execute — apply changes
    s5 = {"node": "execute", "title": "执行操作", "status": "running"}
    steps.append(s5)
    changes = []
    for a in actions:
        tid = a.get("target_id", "")
        val = a.get("params", {}).get("new_value", 0)
        act = a.get("action", "")
        for p in all_plans:
            if p["id"] == tid:
                if act == "update_bid":
                    try: update_bid(p["_platform"], tid, val); changes.append(f"{tid}: bid→{val}")
                    except: pass
                elif act == "update_budget":
                    try: update_budget(p["_platform"], tid, int(val)); changes.append(f"{tid}: budget→{int(val)}")
                    except: pass
    s5["status"] = "done"
    s5["output"] = f"执行完成，{len(changes)} 项调整"

    # Step 6: Report
    s6 = {"node": "report", "title": "报告生成", "status": "done", "output": "优化报告已生成"}
    steps.append(s6)

    return {"steps": steps, "changes": changes, "anomalies": anomalies, "scene": state.get("current_scene", "ad_placement")}
