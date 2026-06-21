"""LangGraph Agent graph — dynamic orchestration with dict state."""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from langgraph.graph import StateGraph, START, END
    from langgraph.checkpoint.memory import MemorySaver
    _OK = True
except ImportError:
    _OK = False

from backend.app.agents.supervisor import supervisor_node
from backend.app.agents.analysis_agent import analysis_agent_node
from backend.app.agents.strategy_agent import strategy_agent_node


def route_after_supervisor(state: dict) -> str:
    return "data_agent"

def route_after_analysis(state: dict) -> str:
    scene = state.get("current_scene", "ad_placement")
    return {"ad_placement":"strategy_agent","content":"strategy_agent","data_analysis":"strategy_agent","diagnosis":"strategy_agent"}.get(scene,"strategy_agent")


def data_agent_node(state: dict) -> dict:
    """Data Agent — fetch campaign data from Mock functions."""
    from tools.mock_functions import get_top_campaigns
    params = state.get("analysis_result", {})
    platforms = params.get("platforms", ["douyin","tencent"])
    days = params.get("days", 7); top_n = params.get("top_n", 5)
    all_plans = []
    for plat in platforms:
        for _ in range(3):
            try:
                plans = get_top_campaigns(plat, days, "cost", top_n)
                for p in plans: p["_platform"] = plat
                all_plans.extend(plans); break
            except: pass
    return {"platform_data": [{"platform":p,"data":all_plans} for p in platforms]}


def execute_agent_node(state: dict) -> dict:
    """Execute Agent — apply optimization changes."""
    from tools.mock_functions import update_bid, update_budget
    actions = state.get("strategy_actions", [])
    all_plans = []
    for pd in state.get("platform_data", []):
        all_plans.extend(pd.get("data", []))
    changes = []
    for a in actions:
        tid = a.get("target_id",""); val = a.get("params",{}).get("new_value",0)
        act = a.get("action","")
        for p in all_plans:
            if p["id"] == tid:
                try:
                    if act=="update_bid": update_bid(p["_platform"],tid,val); changes.append(f"{tid}: bid→{val}")
                    elif act=="update_budget": update_budget(p["_platform"],tid,int(val)); changes.append(f"{tid}: budget→{int(val)}")
                except: pass
    return {"execution_results": [{"status":"done","changes":len(changes)}], "analysis_result": {**state.get("analysis_result",{}), "changes":changes}}


def report_agent_node(state: dict) -> dict:
    return {"report": {"summary": "Agent 编排执行完成", "changes": state.get("analysis_result",{}).get("changes",[])}}


def build_graph():
    if not _OK: return None
    builder = StateGraph(dict)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("data_agent", data_agent_node)
    builder.add_node("analysis_agent", analysis_agent_node)
    builder.add_node("strategy_agent", strategy_agent_node)
    builder.add_node("execute_agent", execute_agent_node)
    builder.add_node("report_agent", report_agent_node)
    builder.add_edge(START, "supervisor")
    builder.add_edge("supervisor", "data_agent")
    builder.add_edge("data_agent", "analysis_agent")
    builder.add_conditional_edges("analysis_agent", route_after_analysis, {"strategy_agent":"strategy_agent"})
    builder.add_edge("strategy_agent", "execute_agent")
    builder.add_edge("execute_agent", "report_agent")
    builder.add_edge("report_agent", END)
    return builder.compile(checkpointer=MemorySaver())

app = build_graph()
