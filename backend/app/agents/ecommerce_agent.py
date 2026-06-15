"""Ecommerce Agent — generates ecommerce operations (stock, coupons, scripts)."""
from typing import Dict, Any
from agents.state import AgentState, StrategyAction
from tools.mock_functions import generate_script


def ecommerce_agent_node(state: AgentState) -> Dict[str, Any]:
    """Generate ecommerce actions: stock updates, coupons, and anchor scripts."""
    analysis = state.get("analysis_result", {})
    task_graph = list(state["task_graph"])
    stock_gaps = analysis.get("stock_gap", [])

    actions = []

    for product in stock_gaps:
        pid = product.get("id", "A")
        stock = product.get("stock", 32)

        if stock < 50:
            actions.append(StrategyAction(
                target_id=pid,
                target_type="product",
                action="update_stock",
                params={"product_id": pid, "add_amount": 200},
                risk_level="medium",
                expected_effect=f"库存 {stock} → {stock + 200}",
                requires_approval=True,
            ))

    # Always create a coupon for ecommerce scenarios
    actions.append(StrategyAction(
        target_id="A",
        target_type="coupon",
        action="create_coupon",
        params={"product_id": "A", "discount": 10.0, "channel": "live_comment", "total": 500},
        risk_level="low",
        expected_effect="发放 10 元优惠券 500 张，刺激转化",
        requires_approval=False,
    ))

    # Generate anchor script
    script = generate_script(
        template_id="summer_promo",
        params={"product_name": "爆款T恤", "discount": "10", "stock": "200", "cta_text": "赶紧点击小黄车下单"},
    )
    actions.append(StrategyAction(
        target_id="A",
        target_type="script",
        action="send_live_script",
        params={"room_id": "ROOM-001", "script": script, "target": "main_screen"},
        risk_level="low",
        expected_effect="推送催单话术到主播中控屏",
        requires_approval=False,
    ))

    for t in task_graph:
        if t["type"] == "strategize":
            t["status"] = "done"

    return {"strategy_actions": actions, "task_graph": task_graph}
