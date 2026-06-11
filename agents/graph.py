"""AdCockpit Multi-Agent Graph — LangGraph 1.0+ functional API per constitution.

Uses create_agent + middleware pattern (LangChain 1.2.3 + LangGraph 1.0.10).
Fallback: direct node calls when LangGraph not installed (demo mode).
"""
from agents.state import AgentState

try:
    from langgraph.graph import StateGraph, START, END
    from langgraph.checkpoint.memory import MemorySaver
    _LANGGRAPH_AVAILABLE = True
except ImportError:
    _LANGGRAPH_AVAILABLE = False

try:
    from langchain.agents import create_agent
    _LANGCHAIN_AGENT_AVAILABLE = True
except ImportError:
    _LANGCHAIN_AGENT_AVAILABLE = False

from agents.supervisor import supervisor_node
from agents.data_agent import data_agent_node
from agents.analysis_agent import analysis_agent_node
from agents.strategy_agent import strategy_agent_node
from agents.content_agent import content_agent_node
from agents.ecommerce_agent import ecommerce_agent_node
from agents.execute_agent import execute_agent_node
from agents.report_agent import report_agent_node


def route_after_analysis(state: AgentState) -> str:
    """Conditional edge: route to appropriate agent based on scene."""
    scene = state.get("current_scene", "ad_placement")
    routing = {
        "ad_placement": "strategy_agent",
        "content": "content_agent",
        "ecommerce": "ecommerce_agent",
        "data_analysis": "strategy_agent",
        "diagnosis": "strategy_agent",
    }
    return routing.get(scene, "strategy_agent")


def build_graph():
    """Construct and compile the AdCockpit LangGraph StateGraph.

    Uses LangGraph 1.0+ StateGraph API with MemorySaver for HITL support.
    """
    if not _LANGGRAPH_AVAILABLE:
        return None

    builder = StateGraph(AgentState)

    # Add all 8 agent nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("data_agent", data_agent_node)
    builder.add_node("analysis_agent", analysis_agent_node)
    builder.add_node("strategy_agent", strategy_agent_node)
    builder.add_node("content_agent", content_agent_node)
    builder.add_node("ecommerce_agent", ecommerce_agent_node)
    builder.add_node("execute_agent", execute_agent_node)
    builder.add_node("report_agent", report_agent_node)

    # Build edges: START → supervisor → data_agent → analysis_agent
    builder.add_edge(START, "supervisor")
    builder.add_edge("supervisor", "data_agent")
    builder.add_edge("data_agent", "analysis_agent")

    # Conditional routing from analysis based on scene
    builder.add_conditional_edges(
        "analysis_agent",
        route_after_analysis,
        {
            "strategy_agent": "strategy_agent",
            "content_agent": "content_agent",
            "ecommerce_agent": "ecommerce_agent",
        }
    )

    # All decision paths flow to execute → report → END
    builder.add_edge("strategy_agent", "execute_agent")
    builder.add_edge("content_agent", "execute_agent")
    builder.add_edge("ecommerce_agent", "execute_agent")
    builder.add_edge("execute_agent", "report_agent")
    builder.add_edge("report_agent", END)

    # Compile with MemorySaver for HITL interrupt support
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


# Module-level compiled graph instance
# Falls back to None if LangGraph not installed; routes.py uses direct node calls
app = build_graph()
