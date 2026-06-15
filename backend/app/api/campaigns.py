"""Campaign REST API — with JSON file persistence."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# ---- Persistence helpers ----
def _load_plans():
    """Load plans from JSON files, fallback to mock_data defaults."""
    from backend.app.memory.local_store import load_plans
    from tools.mock_data import DOUYIN_PLANS, TENCENT_PLANS

    douyin = load_plans("douyin")
    tencent = load_plans("tencent")

    # If JSON files are empty, seed with defaults
    if not douyin:
        douyin = [dict(p) for p in DOUYIN_PLANS]
        _save_plans_now("douyin", douyin)
    if not tencent:
        tencent = [dict(p) for p in TENCENT_PLANS]
        _save_plans_now("tencent", tencent)

    return douyin, tencent


def _save_plans_now(platform: str, plans: list):
    """Save plans to JSON immediately."""
    from backend.app.memory.local_store import save_plans
    save_plans(platform, plans)
    # Also sync back to in-memory mock_data
    from tools import mock_data
    if platform == "douyin":
        mock_data.DOUYIN_PLANS.clear()
        mock_data.DOUYIN_PLANS.extend(plans)
    else:
        mock_data.TENCENT_PLANS.clear()
        mock_data.TENCENT_PLANS.extend(plans)


# ---- Models ----
class OptimizeRequest(BaseModel):
    platforms: list[str] = ["douyin", "tencent"]
    days: int = 7
    top_n: int = 5
    roi_threshold: float = 2.0
    bid_adjust_pct: int = -10
    budget_adjust_pct: int = -20


class CreateRequest(BaseModel):
    platform: str
    name: str
    budget: float
    bid: float
    targeting: dict = {}


# ---- Routes ----
@router.get("/campaigns")
async def get_campaigns(platform: str = "douyin", days: int = 7, top_n: int = 5):
    douyin, tencent = _load_plans()
    plans = douyin if platform == "douyin" else tencent
    plans = sorted(plans, key=lambda p: p.get("cost", 0), reverse=True)[:top_n]
    for p in plans: p["_platform"] = platform
    return {"plans": plans, "count": len(plans)}


@router.get("/campaigns/all")
async def get_all():
    douyin, tencent = _load_plans()
    all_p = []
    for p in douyin: p["_platform"] = "douyin"; all_p.append(p)
    for p in tencent: p["_platform"] = "tencent"; all_p.append(p)
    tc = sum(p.get("cost", 0) for p in all_p)
    ar = round(sum(p.get("roi", 0) for p in all_p) / max(len(all_p), 1), 2)
    bw = [p for p in all_p if p.get("roi", 0) < 2.0]
    return {"plans": all_p, "total_cost": tc, "avg_roi": ar, "below_threshold": bw, "count": len(all_p)}


@router.post("/campaigns/optimize")
async def optimize(body: OptimizeRequest):
    douyin, tencent = _load_plans()
    bf = 1 + body.bid_adjust_pct / 100.0
    bdf = 1 + body.budget_adjust_pct / 100.0

    all_p = []
    for plat in body.platforms:
        plans = douyin if plat == "douyin" else tencent
        top = sorted(plans, key=lambda p: p.get("cost", 0), reverse=True)[:body.top_n]
        for p in top: p["_platform"] = plat
        all_p.extend(top)

    below = [p for p in all_p if p["roi"] < body.roi_threshold]
    changes = []
    for p in below:
        ob = p.get("bid", 0); nb = round(ob * bf, 1)
        p["bid"] = nb; changes.append(f"{p['id']}: bid {ob}->{nb}")
        if p["roi"] < body.roi_threshold * 0.75:
            obu = p.get("budget", 0); nbu = round(obu * bdf)
            p["budget"] = nbu; changes.append(f"{p['id']}: budget {obu}->{nbu}")

    # Persist to JSON files
    _save_plans_now("douyin", douyin)
    _save_plans_now("tencent", tencent)

    # Save optimization history
    from backend.app.memory.local_store import save_optimization_record
    save_optimization_record({
        "changes": changes, "below_count": len(below), "total_plans": len(all_p),
        "params": body.model_dump(),
    })

    # Persist updated campaigns — save from source (DOUYIN_PLANS/TENCENT_PLANS)
    from backend.app.memory.local_store import save_plans
    from tools.mock_data import DOUYIN_PLANS, TENCENT_PLANS
    if "douyin" in body.platforms:
        save_plans("douyin", list(DOUYIN_PLANS))
    if "tencent" in body.platforms:
        save_plans("tencent", list(TENCENT_PLANS))

    return {"session_id": "", "status": "completed", "changes": changes,
            "below_count": len(below), "total_plans": len(all_p)}


@router.post("/campaigns/create")
async def create(body: CreateRequest):
    douyin, tencent = _load_plans()
    import random
    new_id = f"{'C' if body.platform == 'douyin' else 'T'}{random.randint(100, 999)}"
    campaign = {
        "id": new_id, "name": body.name, "cost": 0, "roi": 0, "bid": body.bid,
        "budget": body.budget, "status": "active", "review_status": "approved",
        "ctr": 0, "cvr": 0, "cpa": 0, "_platform": body.platform, "targeting": body.targeting,
    }
    if body.platform == "douyin":
        douyin.append(campaign)
        _save_plans_now("douyin", douyin)
    else:
        tencent.append(campaign)
        _save_plans_now("tencent", tencent)
    return {"campaign": campaign, "success": True}
