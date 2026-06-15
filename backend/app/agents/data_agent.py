"""Data Agent — fetches platform data via Mock functions."""
import concurrent.futures
from datetime import datetime
from typing import Dict, Any
from agents.state import AgentState, PlatformData
from tools.mock_functions import get_top_campaigns


def data_agent_node(state: AgentState) -> Dict[str, Any]:
    """Execute all pending fetch_data tasks in the task graph.

    Fetches data from mock platform APIs in parallel using ThreadPoolExecutor.
    """
    tasks = [t for t in state.get("task_graph", []) if t["type"] == "fetch_data" and t["status"] == "pending"]
    platform_data = list(state.get("platform_data", []))
    updated_tasks = list(state["task_graph"])
    error_log = list(state.get("error_log", []))

    def fetch_single(task):
        tid = task["id"]
        platform = task.get("platform", "unknown")
        params = task.get("params", {})
        endpoint = params.get("endpoint", "get_top_campaigns")

        try:
            if platform == "douyin":
                data = get_top_campaigns(platform="douyin", days=params.get("days", 7),
                                         metric=params.get("metric", "cost"),
                                         top_n=params.get("top_n", 5))
            elif platform == "tencent":
                data = get_top_campaigns(platform="tencent", days=params.get("days", 7),
                                         metric=params.get("metric", "cost"),
                                         top_n=params.get("top_n", 5))
            elif platform == "xiaohongshu":
                data = [{"id": "X001", "name": "小红书计划-A", "cost": 5000, "roi": 2.0}]
            else:
                data = []

            pd_entry = PlatformData(
                platform=platform,
                endpoint=endpoint,
                data=data,
                fetched_at=datetime.now().isoformat(),
                error=None,
            )
            # Update task status
            for t in updated_tasks:
                if t["id"] == tid:
                    t["status"] = "done"
            return pd_entry, None
        except Exception as e:
            err_entry = {"task_id": tid, "platform": platform, "error": str(e), "time": datetime.now().isoformat()}
            pd_entry = PlatformData(
                platform=platform, endpoint=endpoint, data=[],
                fetched_at=datetime.now().isoformat(), error=str(e),
            )
            for t in updated_tasks:
                if t["id"] == tid:
                    t["status"] = "failed"
            return pd_entry, err_entry

    # Execute in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(fetch_single, t) for t in tasks]
        for future in concurrent.futures.as_completed(futures):
            pd_entry, err_entry = future.result()
            if pd_entry:
                platform_data.append(pd_entry)
            if err_entry:
                error_log.append(err_entry)

    return {
        "platform_data": platform_data,
        "task_graph": updated_tasks,
        "error_log": error_log,
    }
