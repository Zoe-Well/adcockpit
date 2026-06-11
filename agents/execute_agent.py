"""Execute Agent — runs StrategyActions with retry and HITL approval."""
import time
from datetime import datetime
from typing import Dict, Any, List
from agents.state import AgentState, StrategyAction, ExecutionResult
from tools.mock_functions import (
    update_bid, update_budget, update_stock, create_coupon,
    publish_to_feishu, send_live_script, replace_creative, resubmit_plan,
    send_feishu_notification, MockBusinessError, MockNetworkError,
)


# Action → function mapping
ACTION_MAP = {
    "update_bid": update_bid,
    "update_budget": update_budget,
    "update_stock": update_stock,
    "create_coupon": create_coupon,
    "publish_to_feishu": publish_to_feishu,
    "send_live_script": send_live_script,
    "replace_creative": replace_creative,
    "resubmit_plan": resubmit_plan,
    "send_feishu_notification": send_feishu_notification,
}


def execute_agent_node(state: AgentState) -> Dict[str, Any]:
    """Execute all strategy actions, handling approvals and retries."""
    actions = state.get("strategy_actions", [])
    task_graph = list(state["task_graph"])

    # Check if any actions require approval
    pending = [a for a in actions if a.get("requires_approval", False)]
    if pending:
        # Check if already approved (resumed via Command)
        # For sync mode, put into pending_approval and return
        if not state.get("_approval_resolved"):
            return {
                "pending_approval": pending,
                "strategy_actions": actions,
            }

    # Execute all actions
    results = execute_actions(actions, state)

    for t in task_graph:
        if t["type"] == "execute":
            t["status"] = "done"

    return {
        "execution_results": results,
        "pending_approval": None,
        "task_graph": task_graph,
    }


def execute_actions(actions: List[StrategyAction], state: Dict = None) -> List[ExecutionResult]:
    """Execute a list of StrategyActions with retry logic.

    Args:
        actions: List of actions to execute.
        state: Optional AgentState dict for context.

    Returns:
        List of ExecutionResult dicts.
    """
    results = []

    for action in actions:
        action_name = action.get("action", "")
        params = action.get("params", {})
        func = ACTION_MAP.get(action_name)

        if func is None:
            results.append(ExecutionResult(
                action=action,
                status="failed",
                response=None,
                error=f"Unknown action: {action_name}",
                retry_count=0,
                executed_at=datetime.now().isoformat(),
            ))
            continue

        # Execute with retry (max 3)
        last_error = None
        for attempt in range(3):
            try:
                # Extract positional args from params
                response = func(**params)
                results.append(ExecutionResult(
                    action=action,
                    status="success",
                    response=response,
                    error=None,
                    retry_count=attempt,
                    executed_at=datetime.now().isoformat(),
                ))
                last_error = None
                break
            except MockNetworkError as e:
                last_error = str(e)
                time.sleep(1.0 * (attempt + 1))  # exponential-ish backoff
            except MockBusinessError as e:
                last_error = str(e)
                break  # Don't retry business errors
            except Exception as e:
                last_error = str(e)
                break

        if last_error:
            results.append(ExecutionResult(
                action=action,
                status="failed",
                response=None,
                error=last_error,
                retry_count=3,
                executed_at=datetime.now().isoformat(),
            ))

    return results
