"""Content Agent — generates scripts and publishes content."""
from typing import Dict, Any
from agents.state import AgentState, StrategyAction
from tools.mock_functions import generate_script


def content_agent_node(state: AgentState) -> Dict[str, Any]:
    """Generate scripts based on creative insights for content scenarios."""
    analysis = state.get("analysis_result", {})
    task_graph = list(state["task_graph"])
    insights = analysis.get("creative_insights", {})
    features = insights.get("common_features", ["前3秒价格锚点", "快语速", "热门BGM"])

    actions = []
    for i in range(3):
        script = generate_script(
            template_id="summer_promo",
            params={
                "product_name": f"爆款商品-{chr(65+i)}",
                "discount": str(10 + i * 5),
                "stock": str(200 - i * 50),
                "cta_text": "赶紧下单别犹豫",
            },
        )
        actions.append(StrategyAction(
            target_id=f"script_{i+1}",
            target_type="script",
            action="publish_to_feishu",
            params={"script_content": script, "repo": "内容库", "file_name": f"带货脚本-{chr(65+i)}.md"},
            risk_level="low",
            expected_effect="发布新脚本到飞书内容库",
            requires_approval=False,
        ))

    for t in task_graph:
        if t["type"] == "strategize":
            t["status"] = "done"

    return {"strategy_actions": actions, "task_graph": task_graph}
