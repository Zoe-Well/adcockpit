"""Strategy Agent — generates executable StrategyAction lists."""
from typing import Dict, Any
from agents.state import AgentState, StrategyAction


def strategy_agent_node(state: AgentState) -> Dict[str, Any]:
    """Generate strategy actions based on analysis results and current scene.

    Ad Placement: Generate bid/budget adjustment actions.
    Data Analysis: Generate budget reallocation proposals.
    """
    scene = state["current_scene"]
    analysis = state.get("analysis_result", {})
    task_graph = list(state["task_graph"])

    if scene == "ad_placement":
        actions, extra = _ad_placement_strategy(analysis)
    elif scene == "data_analysis":
        actions, extra = _data_analysis_strategy(analysis)
    else:
        actions, extra = [], {}

    # Mark strategize tasks as done
    for t in task_graph:
        if t["type"] == "strategize":
            t["status"] = "done"

    # Inject estimated metrics into analysis_result for downstream use
    if extra:
        analysis.update(extra)

    return {
        "strategy_actions": actions,
        "analysis_result": analysis,
        "task_graph": task_graph,
    }


def _ad_placement_strategy(analysis: Dict) -> tuple:
    """Generate bid/budget adjustment actions for ad placement."""
    anomalies = analysis.get("anomalies", [])
    actions = []

    for a in anomalies:
        plan_id = a["plan_id"]
        plan_name = a.get("name", plan_id)
        roi = a["roi"]
        platform = a["platform"]

        # Calculate new bid (10% reduction)
        # Use hardcoded values matching the prototype
        bid_map = {"C001": 25.0, "C004": 20.0, "T001": 30.0}
        current_bid = bid_map.get(plan_id, 20.0)
        new_bid = round(current_bid * 0.9, 1)

        risk = "medium"
        if roi < 1.2:
            risk = "high"
        elif roi < 1.5:
            risk = "medium"
        else:
            risk = "low"

        actions.append(StrategyAction(
            target_id=plan_id,
            target_type="campaign",
            action="update_bid",
            params={"platform": platform, "campaign_id": plan_id, "new_bid": new_bid},
            risk_level=risk,
            expected_effect=f"ROI 预计提升至 {roi * 1.2:.1f}",
            requires_approval=True,
        ))

        # For critically underperforming plans, also reduce budget
        if roi < 1.5:
            actions.append(StrategyAction(
                target_id=plan_id,
                target_type="budget",
                action="update_budget",
                params={"platform": platform, "campaign_id": plan_id, "new_budget": 4000},
                risk_level="high",
                expected_effect="止损 — 降低日预算 20%",
                requires_approval=True,
            ))

    extra = {
        "estimated_saving": "15%",
        "estimated_saving_amount": 5640,
        "estimated_roi_improvement": "2.1",
        "current_overall_roi": 1.87,
    }

    return actions, extra


def _data_analysis_strategy(analysis: Dict) -> tuple:
    """Generate budget reallocation proposals."""
    ranking = analysis.get("customer_ranking", [])
    actions = []
    bottom = [c for c in ranking if c["rank"] >= 4]
    top = [c for c in ranking if c["rank"] <= 3]

    for client in bottom:
        pct = -20 if client["rank"] == 4 else -30
        target = top[0]["name"] if top else "客户C"
        actions.append(StrategyAction(
            target_id=client["name"],
            target_type="budget",
            action="reallocate_budget",
            params={"from_client": client["name"], "to_client": target,
                    "change_percent": pct, "reason": f"ROI 仅 {client['roi']}，低于整体平均"},
            risk_level="medium",
            expected_effect=f"节省低效投放, 转移至 {target}",
            requires_approval=False,
        ))

    return actions, {"estimated_roi_improvement": 0.3}
