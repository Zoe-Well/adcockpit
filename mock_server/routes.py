"""Mock API routes simulating real platform endpoints.

All endpoints return data from tools/mock_data.py to ensure consistency.
Each endpoint includes simulated latency (100-500ms) and periodic errors.
"""
import random
import time
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from tools.mock_data import (
    DOUYIN_PLANS, TENCENT_PLANS, CREATIVES, PRODUCTS,
    LIVE_METRICS, CLIENT_DATA, DASHBOARD_METRICS, REPORT_SUMMARY,
)

router = APIRouter()

# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------
class UpdateBidRequest(BaseModel):
    new_bid: float

class UpdateBudgetRequest(BaseModel):
    new_budget: float

class ReplaceCreativeRequest(BaseModel):
    new_video_id: str

class PublishRequest(BaseModel):
    repo: str
    files: list[dict]

class UpdateStockRequest(BaseModel):
    add_amount: int

class CreateCouponRequest(BaseModel):
    discount: float
    channel: str = "live_comment"
    total: int = 500


# ---------------------------------------------------------------------------
# ===== 巨量引擎 (Douyin) =====
# ---------------------------------------------------------------------------
@router.get("/api/douyin/campaigns/top", tags=["巨量引擎"])
async def douyin_get_top_campaigns(
    days: int = Query(7), top_n: int = Query(5)):
    """Get top N campaigns on Douyin."""
    time.sleep(random.uniform(0.1, 0.5))
    _maybe_error()
    plans = sorted(DOUYIN_PLANS, key=lambda x: x["cost"], reverse=True)
    return {"code": 0, "message": "ok", "data": plans[:top_n]}

@router.get("/api/douyin/campaigns/{campaign_id}", tags=["巨量引擎"])
async def douyin_get_campaign_detail(campaign_id: str):
    """Get campaign detail."""
    time.sleep(random.uniform(0.1, 0.3))
    for p in DOUYIN_PLANS:
        if p["id"] == campaign_id:
            return {"code": 0, "message": "ok", "data": p}
    raise HTTPException(404, f"Campaign {campaign_id} not found")

@router.post("/api/douyin/campaigns/{campaign_id}/bid", tags=["巨量引擎"])
async def douyin_update_bid(campaign_id: str, body: UpdateBidRequest):
    """Update campaign bid."""
    time.sleep(random.uniform(0.1, 0.4))
    _maybe_error()
    return {"code": 0, "message": "ok", "data": {"campaign_id": campaign_id, "new_bid": body.new_bid}}

@router.post("/api/douyin/campaigns/{campaign_id}/budget", tags=["巨量引擎"])
async def douyin_update_budget(campaign_id: str, body: UpdateBudgetRequest):
    """Update campaign budget."""
    time.sleep(random.uniform(0.1, 0.4))
    return {"code": 0, "message": "ok", "data": {"campaign_id": campaign_id, "new_budget": body.new_budget}}

@router.get("/api/douyin/plans/{plan_id}/status", tags=["巨量引擎"])
async def douyin_get_plan_status(plan_id: str):
    """Get plan status with review info."""
    time.sleep(random.uniform(0.1, 0.3))
    if plan_id == "12345":
        return {"code": 0, "message": "ok", "data": {"plan_id": "12345", "status": "rejected", "review_status": "素材虚假承诺", "rejection_reason": "素材内容涉及虚假承诺"}}
    for p in DOUYIN_PLANS:
        if p["id"] == plan_id:
            return {"code": 0, "message": "ok", "data": {"plan_id": plan_id, "status": p["status"], "review_status": p.get("review_status", "approved")}}
    raise HTTPException(404)

@router.post("/api/douyin/plans/{plan_id}/creative", tags=["巨量引擎"])
async def douyin_replace_creative(plan_id: str, body: ReplaceCreativeRequest):
    """Replace plan creative."""
    time.sleep(random.uniform(0.1, 0.5))
    _maybe_error()
    return {"code": 0, "message": "ok", "data": {"plan_id": plan_id, "new_video_id": body.new_video_id, "review_id": f"RV-{random.randint(100,999)}"}}

@router.post("/api/douyin/plans/{plan_id}/resubmit", tags=["巨量引擎"])
async def douyin_resubmit_plan(plan_id: str):
    """Resubmit plan for review."""
    time.sleep(random.uniform(0.1, 0.3))
    return {"code": 0, "message": "ok", "data": {"plan_id": plan_id, "new_status": "pending_review"}}

@router.get("/api/douyin/report", tags=["巨量引擎"])
async def douyin_report(start_date: str, end_date: str):
    """Get platform report."""
    time.sleep(random.uniform(0.2, 0.8))
    return {"code": 0, "message": "ok", "data": {"platform": "douyin", "rows": DOUYIN_PLANS, "total_cost": sum(p["cost"] for p in DOUYIN_PLANS)}}

# ---------------------------------------------------------------------------
# ===== 腾讯广告 =====
# ---------------------------------------------------------------------------
@router.get("/api/tencent/campaigns/top", tags=["腾讯广告"])
async def tencent_get_top_campaigns(days: int = 7, top_n: int = 5):
    """Get top N campaigns on Tencent Ads."""
    time.sleep(random.uniform(0.1, 0.5))
    _maybe_error()
    plans = sorted(TENCENT_PLANS, key=lambda x: x["cost"], reverse=True)
    return {"code": 0, "message": "ok", "data": plans[:top_n]}

@router.get("/api/tencent/campaigns/{campaign_id}", tags=["腾讯广告"])
async def tencent_get_campaign_detail(campaign_id: str):
    """Get campaign detail."""
    for p in TENCENT_PLANS:
        if p["id"] == campaign_id:
            return {"code": 0, "message": "ok", "data": p}
    raise HTTPException(404)

@router.post("/api/tencent/campaigns/{campaign_id}/bid", tags=["腾讯广告"])
async def tencent_update_bid(campaign_id: str, body: UpdateBidRequest):
    """Update campaign bid."""
    time.sleep(random.uniform(0.1, 0.4))
    _maybe_error()
    return {"code": 0, "message": "ok", "data": {"campaign_id": campaign_id, "new_bid": body.new_bid}}

# ---------------------------------------------------------------------------
# ===== 小红书聚光 =====
# ---------------------------------------------------------------------------
@router.get("/api/xiaohongshu/report", tags=["小红书聚光"])
async def xiaohongshu_report(start_date: str, end_date: str):
    """Get Xiaohongshu report."""
    time.sleep(random.uniform(0.1, 0.5))
    _maybe_error()
    return {"code": 0, "message": "ok", "data": {"platform": "xiaohongshu", "rows": [], "total_cost": 25000}}

# ---------------------------------------------------------------------------
# ===== 内容 & 飞书 =====
# ---------------------------------------------------------------------------
@router.get("/api/creatives/top", tags=["内容平台"])
async def get_top_creatives(date: str = "2026-06-08", top_n: int = 3, worst_n: int = 3):
    """Get top and worst creatives."""
    time.sleep(random.uniform(0.1, 0.5))
    creatives = sorted(CREATIVES, key=lambda x: x["ctr"], reverse=True)
    return {"code": 0, "message": "ok", "data": {"top": creatives[:top_n], "worst": list(reversed(creatives[-worst_n:]))}}

@router.post("/api/feishu/publish", tags=["飞书"])
async def feishu_publish(body: PublishRequest):
    """Publish to Feishu knowledge base."""
    time.sleep(random.uniform(0.2, 0.6))
    _maybe_error()
    return {"code": 0, "message": "ok", "data": {"urls": [f"https://feishu.cn/doc/{body.repo}/{f['name']}" for f in body.files]}}

# ---------------------------------------------------------------------------
# ===== ERP / 电商 =====
# ---------------------------------------------------------------------------
@router.get("/api/products/{product_id}/stock", tags=["电商ERP"])
async def get_product_stock(product_id: str):
    """Get product stock."""
    for p in PRODUCTS:
        if p["id"] == product_id:
            return {"code": 0, "message": "ok", "data": p}
    raise HTTPException(404)

@router.post("/api/products/{product_id}/stock", tags=["电商ERP"])
async def update_product_stock(product_id: str, body: UpdateStockRequest):
    """Add stock to product."""
    time.sleep(random.uniform(0.3, 1.0))
    _maybe_error()
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    new_stock = (product["stock"] if product else 0) + body.add_amount
    return {"code": 0, "message": "ok", "data": {"product_id": product_id, "new_stock": new_stock, "added": body.add_amount}}

@router.post("/api/coupons", tags=["电商ERP"])
async def create_coupon(body: CreateCouponRequest):
    """Create discount coupon."""
    time.sleep(random.uniform(0.1, 0.4))
    _maybe_error()
    coupon_id = f"CP{random.randint(100,999)}"
    return {"code": 0, "message": "ok", "data": {"coupon_id": coupon_id, "discount": body.discount, "claimed": 0, "total": body.total}}

@router.get("/api/live/{room_id}/metrics", tags=["直播"])
async def get_live_metrics(room_id: str):
    """Get real-time livestream metrics."""
    return {"code": 0, "message": "ok", "data": dict(LIVE_METRICS, room_id=room_id)}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _maybe_error():
    """Simulate periodic API errors."""
    r = random.random()
    if r < 0.05:
        raise HTTPException(503, "服务暂不可用")
    if r < 0.15:
        raise HTTPException(500, "服务器内部异常")
