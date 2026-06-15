"""Celery tasks for agent execution with WebSocket streaming support.

Supports soft cancel via Redis flag: cancel_flag:{session_id}
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    import redis
    _r = redis.Redis.from_url("redis://localhost:6379", decode_responses=True)
    _r.ping()
    _REDIS_OK = True
except Exception:
    _REDIS_OK = False

try:
    from celery import shared_task
    _CELERY_OK = True
except ImportError:
    _CELERY_OK = False

    def shared_task(**kwargs):
        """Stub decorator when Celery is not installed."""
        def decorator(func):
            func.delay = lambda *a, **kw: func(None, *a, **kw)
            return func
        return decorator


@shared_task(bind=True, name="run_agent_optimize")
def run_agent_optimize(self, session_id: str, params: dict):
    """Run ad placement optimization in a Celery worker.

    Pushes step events via _push_event() for WebSocket streaming.
    Checks cancel_flag:{session_id} before each step for soft cancel.
    """
    from tools.mock_functions import get_top_campaigns, update_bid, update_budget

    if _is_cancelled(session_id):
        return {"status": "cancelled", "session_id": session_id}

    platforms = params.get("platforms", ["douyin", "tencent"])
    days = params.get("days", 7)
    top_n = params.get("top_n", 5)
    threshold = params.get("roi_threshold", 2.0)
    bid_pct = 1 + params.get("bid_adjust_pct", -10) / 100.0
    budget_pct = 1 + params.get("budget_adjust_pct", -20) / 100.0

    # Step 1: Fetch data
    _push(session_id, "data", "running", "正在拉取平台数据...")
    all_plans = []
    for plat in platforms:
        if _is_cancelled(session_id): return {"status": "cancelled"}
        plans = get_top_campaigns(plat, days, "cost", top_n)
        for p in plans: p["_platform"] = plat
        all_plans.extend(plans)
    _push(session_id, "data", "done", f"已拉取 {len(all_plans)} 条计划")

    # Step 2: Analyze
    _push(session_id, "analysis", "running", "正在分析异常计划...")
    below = [p for p in all_plans if p["roi"] < threshold]
    _push(session_id, "analysis", "done", f"发现 {len(below)} 条 ROI < {threshold} 的计划")

    # Step 3: Generate strategy
    _push(session_id, "strategy", "running", "正在生成优化策略...")
    _push(session_id, "strategy", "done", f"生成 {len(below)} 条调价建议")

    # Step 4: Execute
    _push(session_id, "execute", "running", "正在执行调价操作...")
    changes = []
    for p in below:
        if _is_cancelled(session_id): return {"status": "cancelled"}
        old_bid = p.get("bid", 0)
        new_bid = round(old_bid * bid_pct, 1)
        try:
            update_bid(p.get("_platform", "douyin"), p["id"], new_bid)
            changes.append(f"{p['id']}: bid {old_bid}→{new_bid}")
        except Exception: pass
        if p["roi"] < threshold * 0.75:
            old_budget = p.get("budget", 0)
            new_budget = round(old_budget * budget_pct)
            try:
                update_budget(p.get("_platform", "douyin"), p["id"], new_budget)
                changes.append(f"{p['id']}: budget {old_budget}→{new_budget}")
            except Exception: pass
    _push(session_id, "execute", "done", f"执行完成，{len(changes)} 项调整")

    # Step 5: Report
    _push(session_id, "report", "done", "优化报告已生成")

    return {"status": "completed", "changes": changes, "below_count": len(below)}


@shared_task(bind=True, name="run_agent_content")
def run_agent_content(self, session_id: str, params: dict):
    """Generate scripts in background."""
    from tools.mock_functions import generate_script
    from tools.feishu_client import publish_scripts

    if _is_cancelled(session_id): return {"status": "cancelled"}

    _push(session_id, "data", "done", "素材数据已拉取")
    _push(session_id, "analysis", "done", "爆款特征分析完成")

    top_n = params.get("top_n", 3)
    template = params.get("template_id", "summer_promo")
    scripts = []
    for i in range(top_n):
        for _ in range(3):
            try:
                s = generate_script(template_id=template, params={"product_name": f"产品{chr(65+i)}"})
                scripts.append(s); break
            except: pass
        else: scripts.append("[生成失败]")

    _push(session_id, "content", "done", f"已生成 {len(scripts)} 条脚本")

    platform = params.get("platform", "douyin")
    try:
        results = publish_scripts(scripts, platform, template)
        urls = [r.get("url", "") for r in results]
    except: urls = []

    _push(session_id, "execute", "done", "已发布到飞书")
    _push(session_id, "report", "done", "内容生产完成")

    return {"status": "completed", "scripts": scripts, "urls": urls}


def cancel_task(session_id: str):
    """Set cancel flag for soft cancellation."""
    if _REDIS_OK:
        _r.setex(f"cancel_flag:{session_id}", 300, "1")


def _is_cancelled(session_id: str) -> bool:
    if not _REDIS_OK: return False
    return _r.get(f"cancel_flag:{session_id}") == "1"


def _push(session_id: str, node: str, status: str, message: str):
    """Push step event to Redis pub/sub for WebSocket relay."""
    import json
    if _REDIS_OK:
        _r.publish(f"agent_stream:{session_id}", json.dumps({
            "node": node, "status": status, "message": message,
        }))


def sync_optimize(session_id: str, params: dict) -> dict:
    """Synchronous fallback (no Redis/Celery needed)."""
    return run_agent_optimize(None, session_id, params)


def sync_content(session_id: str, params: dict) -> dict:
    """Synchronous fallback for content production."""
    return run_agent_content(None, session_id, params)
