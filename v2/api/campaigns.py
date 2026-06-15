"""Campaign API — query, optimize, create."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class OptimizeRequest(BaseModel):
    platforms: List[str] = ["douyin", "tencent"]
    days: int = 7
    top_n: int = 5
    roi_threshold: float = 2.0
    bid_adjust_pct: int = -10
    budget_adjust_pct: int = -20
    risk_confirm: str = "medium"


class CreateRequest(BaseModel):
    platform: str
    name: str
    budget: float
    bid: float
    targeting: dict = {}


@router.get("/campaigns")
async def get_campaigns(platform: str = "douyin", days: int = 7, top_n: int = 5):
    """Get top campaigns from a platform."""
    from tools.mock_functions import get_top_campaigns

    plans = get_top_campaigns(platform, days, "cost", top_n)
    for p in plans:
        p["_platform"] = platform

    total_cost = sum(p.get("cost", 0) for p in plans)
    avg_roi = round(sum(p.get("roi", 0) for p in plans) / max(len(plans), 1), 2)
    below = [p for p in plans if p.get("roi", 0) < 2.0]

    return {
        "plans": plans,
        "total_cost": total_cost,
        "avg_roi": avg_roi,
        "below_threshold": below,
        "count": len(plans),
    }


@router.get("/campaigns/all")
async def get_all_campaigns():
    """Get all campaigns from both platforms."""
    from tools.mock_functions import get_top_campaigns

    douyin = get_top_campaigns("douyin", 30, "cost", 20)
    tencent = get_top_campaigns("tencent", 30, "cost", 20)
    for p in douyin:
        p["_platform"] = "douyin"
    for p in tencent:
        p["_platform"] = "tencent"

    all_plans = douyin + tencent
    total_cost = sum(p.get("cost", 0) for p in all_plans)
    avg_roi = round(sum(p.get("roi", 0) for p in all_plans) / max(len(all_plans), 1), 2)
    below = [p for p in all_plans if p.get("roi", 0) < 2.0]

    return {
        "plans": all_plans,
        "total_cost": total_cost,
        "avg_roi": avg_roi,
        "below_threshold": below,
        "count": len(all_plans),
    }


@router.post("/campaigns/optimize")
async def optimize_campaigns(body: OptimizeRequest):
    """Run campaign optimization."""
    from tools.mock_functions import get_top_campaigns, update_bid, update_budget

    bid_factor = 1 + body.bid_adjust_pct / 100.0
    budget_factor = 1 + body.budget_adjust_pct / 100.0

    all_plans = []
    for plat in body.platforms:
        plans = get_top_campaigns(plat, body.days, "cost", body.top_n)
        for p in plans:
            p["_platform"] = plat
        all_plans.extend(plans)

    below = [p for p in all_plans if p["roi"] < body.roi_threshold]
    changes = []

    for p in below:
        old_bid = p.get("bid", 0)
        new_bid = round(old_bid * bid_factor, 1)
        try:
            update_bid(p.get("_platform", "douyin"), p["id"], new_bid)
            changes.append(f"{p['id']}: bid {old_bid}→{new_bid}")
        except Exception:
            pass
        if p["roi"] < body.roi_threshold * 0.75:
            old_budget = p.get("budget", 0)
            new_budget = round(old_budget * budget_factor)
            try:
                update_budget(p.get("_platform", "douyin"), p["id"], new_budget)
                changes.append(f"{p['id']}: budget {old_budget}→{new_budget}")
            except Exception:
                pass

    return {
        "changes": changes,
        "below_count": len(below),
        "total_plans": len(all_plans),
    }


@router.post("/campaigns/create")
async def create_campaign(body: CreateRequest):
    """Create a new campaign."""
    from tools.mock_functions import create_campaign

    new_camp = create_campaign(body.platform, body.name, body.budget, body.bid, body.targeting)
    return {"campaign": new_camp, "success": True}
