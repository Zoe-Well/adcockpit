"""24 Mock functions for AdCockpit — 10% business exception, 5% network exception."""
import random
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from tools.mock_data import (
    DOUYIN_PLANS, TENCENT_PLANS, CREATIVES, PRODUCTS, LIVE_METRICS,
    CLIENT_DATA, DASHBOARD_METRICS, REPORT_SUMMARY
)

# ---------------------------------------------------------------------------
# Exception classes
# ---------------------------------------------------------------------------

class MockBusinessError(Exception):
    """Business-level mock error (10% probability)."""
    pass

class MockNetworkError(Exception):
    """Network-level mock error (5% probability)."""
    pass

class AdPlatformTimeout(MockNetworkError): pass
class InvalidMetricError(MockBusinessError): pass
class CampaignNotFound(MockBusinessError): pass
class BidOutOfRange(MockBusinessError): pass
class AccountInsufficientBalance(MockBusinessError): pass
class BudgetBelowMinimum(MockBusinessError): pass
class PlanNotFound(MockBusinessError): pass
class CreativeNotFound(MockBusinessError): pass
class ReviewRejected(MockBusinessError): pass
class ResubmitLimitExceeded(MockBusinessError): pass
class ReportTimeout(MockNetworkError): pass
class PartialDataAvailable(MockBusinessError): pass
class CreativeDataNotReady(MockBusinessError): pass
class VideoUnavailable(MockBusinessError): pass
class FrameAnalysisTimeout(MockNetworkError): pass
class TemplateNotFound(MockBusinessError): pass
class FeishuAuthExpired(MockBusinessError): pass
class UploadFailed(MockNetworkError): pass
class ProductNotFound(MockBusinessError): pass
class ERPTimeout(MockNetworkError): pass
class StockUpdateRejected(MockBusinessError): pass
class CouponLimitExceeded(MockBusinessError): pass
class DiscountOutOfRange(MockBusinessError): pass
class LiveRoomOffline(MockBusinessError): pass
class PartialPlatformFailure(MockBusinessError): pass
class InsufficientData(MockBusinessError): pass
class FeishuRateLimit(MockBusinessError): pass
class ERPUnavailable(MockNetworkError): pass

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _maybe_fail():
    """Randomly trigger exceptions: 10% business, 5% network, 85% success."""
    time.sleep(random.uniform(0.1, 1.5))
    r = random.random()
    if r < 0.05:
        raise MockNetworkError("服务暂不可用，请稍后重试")
    if r < 0.15:
        raise MockBusinessError("业务处理异常，请检查参数后重试")

def _find_plan(platform: str, plan_id: str) -> Optional[Dict]:
    """Find a plan by platform and ID. Returns ORIGINAL reference so modifications persist."""
    plans = DOUYIN_PLANS if platform == "douyin" else TENCENT_PLANS
    for p in plans:
        if p["id"] == plan_id:
            return p  # Return original, NOT copy — so update_bid/update_budget take effect
    return None

# ---------------------------------------------------------------------------
# 一、广告投放域 (Ad Placement Domain) — 8 functions
# ---------------------------------------------------------------------------

def get_top_campaigns(platform: str, days: int, metric: str, top_n: int) -> List[Dict[str, Any]]:
    """Get top N campaigns by metric from the specified platform.

    Args:
        platform: Platform name ("douyin" or "tencent").
        days: Number of days to look back.
        metric: Metric to rank by ("cost", "roi").
        top_n: Number of top campaigns to return.

    Returns:
        List of campaign dicts sorted by metric descending.

    Raises:
        AdPlatformTimeout: Network timeout (5%).
        InvalidMetricError: Unsupported metric (10%).
    """
    _maybe_fail()

    if metric not in ("cost", "roi"):
        raise InvalidMetricError(f"不支持的排序指标: {metric}")

    if platform == "douyin":
        plans = [dict(p) for p in DOUYIN_PLANS]
    elif platform == "tencent":
        plans = [dict(p) for p in TENCENT_PLANS]
    else:
        raise InvalidMetricError(f"不支持的平台: {platform}")

    plans.sort(key=lambda x: x.get(metric, 0), reverse=True)
    return plans[:top_n]


def get_campaign_detail(platform: str, campaign_id: str) -> Dict[str, Any]:
    """Get detailed info for a single campaign.

    Args:
        platform: Platform name.
        campaign_id: Campaign ID.

    Returns:
        Campaign detail dict.

    Raises:
        CampaignNotFound: Campaign doesn't exist (10%).
    """
    _maybe_fail()

    plan = _find_plan(platform, campaign_id)
    if plan is None:
        raise CampaignNotFound(f"计划 {campaign_id} 不存在于 {platform} 平台")
    return plan


def update_bid(platform: str, campaign_id: str, new_bid: float) -> Dict[str, Any]:
    """Update the bid price for a campaign.

    Args:
        platform: Platform name.
        campaign_id: Campaign ID.
        new_bid: New bid amount in CNY.

    Returns:
        {"success": True, "new_bid": ..., "campaign_id": ...}

    Raises:
        CampaignNotFound, BidOutOfRange, AccountInsufficientBalance
    """
    _maybe_fail()

    plan = _find_plan(platform, campaign_id)
    if plan is None:
        raise CampaignNotFound(f"计划 {campaign_id} 不存在")

    if new_bid <= 0 or new_bid > 200:
        raise BidOutOfRange(f"出价 {new_bid} 超出允许范围 (0-200]")

    if random.random() < 0.05:
        raise AccountInsufficientBalance("账户余额不足，无法调整出价")

    plan["bid"] = new_bid
    return {"success": True, "campaign_id": campaign_id, "new_bid": new_bid}


def update_budget(platform: str, campaign_id: str, new_budget: float) -> Dict[str, Any]:
    """Update the daily budget for a campaign.

    Args:
        platform: Platform name.
        campaign_id: Campaign ID.
        new_budget: New daily budget in CNY.

    Returns:
        {"success": True, "new_budget": ..., "campaign_id": ...}

    Raises:
        CampaignNotFound, BudgetBelowMinimum
    """
    _maybe_fail()

    plan = _find_plan(platform, campaign_id)
    if plan is None:
        raise CampaignNotFound(f"计划 {campaign_id} 不存在")

    if new_budget < 500:
        raise BudgetBelowMinimum(f"预算 {new_budget} 低于最低限额 500 元")

    plan["budget"] = new_budget
    return {"success": True, "campaign_id": campaign_id, "new_budget": new_budget}


def get_plan_status(platform: str, plan_id: str) -> Dict[str, Any]:
    """Get the full status of a plan including review status.

    Args:
        platform: Platform name.
        plan_id: Plan ID.

    Returns:
        Plan status dict.

    Raises:
        PlanNotFound
    """
    _maybe_fail()

    plan = _find_plan(platform, plan_id)
    if plan is None:
        raise PlanNotFound(f"计划 {plan_id} 不存在于 {platform}")

    # For scenario 5, return specific status for plan 12345
    if plan_id == "12345":
        return {
            "plan_id": "12345",
            "platform": platform,
            "status": "rejected",
            "review_status": "素材虚假承诺",
            "bid": 25.0,
            "budget": 5000,
            "rejection_reason": "素材内容涉及虚假承诺，请修改后重新提交",
            "creative_ids": ["V001", "V002"],
        }

    return {
        "plan_id": plan["id"],
        "platform": platform,
        "status": plan["status"],
        "review_status": plan.get("review_status", "approved"),
        "bid": plan["bid"],
        "budget": plan["budget"],
    }


def replace_creative(platform: str, plan_id: str, new_video_id: str) -> Dict[str, Any]:
    """Replace a creative and resubmit for review.

    Args:
        platform: Platform name.
        plan_id: Plan ID.
        new_video_id: New creative/video ID.

    Returns:
        {"success": True, "review_id": "RV-..."}

    Raises:
        CreativeNotFound, ReviewRejected
    """
    _maybe_fail()

    if random.random() < 0.1:
        raise CreativeNotFound(f"备用素材 {new_video_id} 不存在")

    if random.random() < 0.05:
        raise ReviewRejected("备用素材审核不通过")

    return {"success": True, "plan_id": plan_id, "new_video_id": new_video_id, "review_id": f"RV-{random.randint(100, 999)}"}


def resubmit_plan(platform: str, plan_id: str) -> Dict[str, Any]:
    """Resubmit a plan for review.

    Args:
        platform: Platform name.
        plan_id: Plan ID.

    Returns:
        {"success": True, "new_status": "pending_review"}

    Raises:
        ResubmitLimitExceeded
    """
    _maybe_fail()

    if random.random() < 0.05:
        raise ResubmitLimitExceeded("今日重新提交次数已达上限")

    return {"success": True, "plan_id": plan_id, "new_status": "pending_review"}


def get_platform_report(platform: str, start_date: str, end_date: str,
                        dimensions: List[str], metrics: List[str]) -> Dict[str, Any]:
    """Get aggregated platform report.

    Args:
        platform: Platform name.
        start_date: Start date (YYYY-MM-DD).
        end_date: End date (YYYY-MM-DD).
        dimensions: Group-by dimensions.
        metrics: Metrics to fetch.

    Returns:
        Report data dict with rows list.

    Raises:
        ReportTimeout, PartialDataAvailable
    """
    _maybe_fail()

    if random.random() < 0.05:
        raise ReportTimeout(f"{platform} 报表服务超时")

    if random.random() < 0.05:
        raise PartialDataAvailable(f"{platform} 部分数据不可用")

    plans = DOUYIN_PLANS if platform == "douyin" else TENCENT_PLANS
    rows = [{"date": start_date, "campaign_id": p["id"], "cost": p["cost"], "roi": p["roi"]} for p in plans]
    return {"platform": platform, "rows": rows, "total_cost": sum(r["cost"] for r in rows)}


def create_campaign(platform: str, name: str, budget: float, bid: float,
                    targeting: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create a new ad campaign on the specified platform.

    Args:
        platform: Platform name ("douyin" or "tencent").
        name: Campaign name.
        budget: Daily budget in CNY (min 500, max 50000).
        bid: Bid price in CNY (min 5, max 200).
        targeting: Optional targeting dict {"gender","age_range","interests"}.

    Returns:
        New campaign dict with generated ID.

    Raises:
        InvalidMetricError, BudgetBelowMinimum, BidOutOfRange
    """
    _maybe_fail()

    if platform not in ("douyin", "tencent"):
        raise InvalidMetricError(f"不支持的平台: {platform}")

    if budget < 500:
        raise BudgetBelowMinimum(f"预算 ¥{budget} 低于最低限额 500 元")
    if budget > 50000:
        raise BudgetBelowMinimum(f"预算 ¥{budget} 超过最高限额 50000 元")
    if bid < 5 or bid > 200:
        raise BidOutOfRange(f"出价 ¥{bid} 超出允许范围 5-200 元")

    if targeting is None:
        targeting = {"gender": "all", "age_range": "18-45", "interests": ["购物", "直播"]}

    counter = random.randint(100, 999)
    prefix = "C" if platform == "douyin" else "T"
    new_id = f"{prefix}{counter}"

    campaign = {
        "id": new_id,
        "name": name,
        "platform": platform,
        "cost": 0.0,
        "roi": 0.0,
        "bid": bid,
        "budget": budget,
        "status": "active",
        "review_status": "approved",
        "ctr": 0.0,
        "cvr": 0.0,
        "cpa": 0.0,
        "targeting": targeting,
        "created_at": datetime.now().isoformat(),
        "_platform": platform,
    }

    # Add to in-memory store so get_top_campaigns returns it too
    if platform == "douyin":
        DOUYIN_PLANS.append(campaign)
    else:
        TENCENT_PLANS.append(campaign)

    return campaign


# ---------------------------------------------------------------------------
# 二、内容生产域 (Content Production Domain) — 4 functions
# ---------------------------------------------------------------------------

def get_top_creatives(platform: str, metric: str, date: str,
                      top_n: int, worst_n: int) -> List[Dict[str, Any]]:
    """Get top and worst N creatives by metric.

    Args:
        platform: Platform name.
        metric: Metric to sort by ("ctr").
        date: Date string (YYYY-MM-DD).
        top_n: Number of top performers.
        worst_n: Number of worst performers.

    Returns:
        List of creative dicts — top N first, then worst N.

    Raises:
        CreativeDataNotReady
    """
    _maybe_fail()

    if random.random() < 0.05:
        raise CreativeDataNotReady(f"{date} 的素材数据尚未生成，请稍后再试")

    creatives = [dict(c) for c in CREATIVES]
    creatives.sort(key=lambda x: x.get(metric, 0), reverse=True)

    top = creatives[:top_n]
    worst = list(reversed(creatives[-worst_n:]))
    return top + worst


def analyze_video_frames(video_url: str) -> Dict[str, Any]:
    """Multimodal video frame analysis.

    Args:
        video_url: URL of the video to analyze.

    Returns:
        Frame analysis result dict.

    Raises:
        VideoUnavailable, FrameAnalysisTimeout
    """
    _maybe_fail()

    if random.random() < 0.05:
        raise VideoUnavailable(f"视频 {video_url} 不可访问")

    if random.random() < 0.05:
        raise FrameAnalysisTimeout("多模态帧分析超时，视频时长过长")

    return {
        "video_url": video_url,
        "duration_seconds": 28,
        "key_frames": [
            {"ts": 0, "objects": ["product"], "text": "", "scene": "opening_hook"},
            {"ts": 3, "objects": ["price_tag", "product"], "text": "仅需99", "scene": "price_anchor"},
            {"ts": 15, "objects": ["product", "model"], "text": "", "scene": "product_demo"},
            {"ts": 25, "objects": ["cta_button"], "text": "点击购买", "scene": "cta"},
        ],
        "insights": {
            "has_price_anchor_3s": True,
            "speech_rate": "fast",
            "bgm_type": "trending_pop",
            "optimal_duration": "15-30s",
        }
    }


def generate_script(template_id: str, params: Dict[str, Any]) -> str:
    """Generate a livestream/ecommerce script based on a template.

    Args:
        template_id: Template identifier.
        params: Template parameters.

    Returns:
        Generated script text.

    Raises:
        TemplateNotFound
    """
    _maybe_fail()

    templates = {
        "summer_promo": "🔥 夏天到了！{product_name}限时优惠，{discount}元立减券已发放！\n库存已补，现在下单立减{discount}元，只剩最后{stock}件，手慢无！\n点击下方小黄车，{cta_text}！",
        "flash_sale": "⚡ 闪购通知！{product_name}正在秒杀！\n原价{original_price}，现在只需{promo_price}！\n库存告急，还剩{stock}件，{cta_text}！",
        "product_review": "📦 刚收到{product_name}，实测分享！\n{feature_1}\n{feature_2}\n{feature_3}\n真的绝了，{cta_text}！",
    }

    if template_id not in templates:
        raise TemplateNotFound(f"模板 {template_id} 不存在")

    template = templates[template_id]
    defaults = {
        "product_name": "爆款T恤",
        "discount": "10",
        "stock": "200",
        "cta_text": "赶紧下单别犹豫",
        "original_price": "99",
        "promo_price": "89",
        "feature_1": "面料舒适透气，夏天穿不闷汗",
        "feature_2": "版型显瘦，不挑身材",
        "feature_3": "今日活动价，性价比无敌",
    }
    defaults.update(params)
    return template.format(**defaults)


def publish_to_feishu(repo: str, files: List[Dict[str, str]]) -> Dict[str, Any]:
    """Publish content to Feishu knowledge base (real API or mock fallback).

    Args:
        repo: Target repository name.
        files: List of {"name": ..., "content": ...} dicts.

    Returns:
        {"success": True, "urls": [...]}

    Raises:
        FeishuAuthExpired, UploadFailed
    """
    _maybe_fail()

    if random.random() < 0.05:
        raise FeishuAuthExpired("飞书授权已过期，请重新登录")

    if random.random() < 0.05:
        raise UploadFailed("上传失败，请检查网络连接")

    # Try real Feishu API first (graceful fallback to mock)
    from tools.feishu_client import publish_scripts
    try:
        scripts = [f.get("content", "") for f in files]
        if scripts:
            results = publish_scripts(scripts)
            urls = [r.get("url", "") for r in results]
            return {"success": True, "repo": repo, "urls": urls, "file_count": len(files), "via": "feishu_api"}
    except Exception:
        pass

    # Fallback mock
    urls = [f"https://feishu.cn/doc/{repo}/{f['name']}" for f in files]
    return {"success": True, "repo": repo, "urls": urls, "file_count": len(files), "via": "mock"}


# ---------------------------------------------------------------------------
# 三、电商闭环域 (E-commerce Closed Loop Domain) — 5 functions
# ---------------------------------------------------------------------------

def get_product_stock(product_id: str) -> Dict[str, Any]:
    """Get product stock information.

    Args:
        product_id: Product ID.

    Returns:
        Stock info dict.

    Raises:
        ProductNotFound
    """
    _maybe_fail()

    for p in PRODUCTS:
        if p["id"] == product_id:
            return dict(p)

    raise ProductNotFound(f"商品 {product_id} 不存在")


def update_stock(product_id: str, add_amount: int) -> Dict[str, Any]:
    """Add stock to a product.

    Args:
        product_id: Product ID.
        add_amount: Amount to add.

    Returns:
        {"success": True, "new_stock": ...}

    Raises:
        ERPTimeout, StockUpdateRejected
    """
    _maybe_fail()

    if random.random() < 0.05:
        raise ERPTimeout("ERP 系统超时，补货操作失败")

    if random.random() < 0.05:
        raise StockUpdateRejected("仓库拒绝补货请求：商品已下架")

    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    new_stock = (product["stock"] if product else 0) + add_amount
    return {"success": True, "product_id": product_id, "new_stock": new_stock, "added": add_amount}


def create_coupon(product_id: str, discount: float, channel: str, total: int) -> Dict[str, Any]:
    """Create a discount coupon.

    Args:
        product_id: Product ID.
        discount: Discount amount in CNY.
        channel: Distribution channel ("live_comment").
        total: Total number of coupons.

    Returns:
        Coupon info dict.

    Raises:
        CouponLimitExceeded, DiscountOutOfRange
    """
    _maybe_fail()

    if discount <= 0 or discount > 100:
        raise DiscountOutOfRange(f"优惠金额 {discount} 超出允许范围")

    if random.random() < 0.05:
        raise CouponLimitExceeded("今日优惠券创建数量已达上限")

    coupon_id = f"CP{random.randint(100, 999)}"
    return {
        "coupon_id": coupon_id,
        "product_id": product_id,
        "discount": discount,
        "channel": channel,
        "claimed": 0,
        "total": total,
        "code": f"LIVE{discount:.0f}",
    }


def get_live_metrics(room_id: str) -> Dict[str, Any]:
    """Get real-time livestream metrics.

    Args:
        room_id: Livestream room ID.

    Returns:
        Live metrics dict.

    Raises:
        LiveRoomOffline
    """
    _maybe_fail()

    if random.random() < 0.05:
        raise LiveRoomOffline(f"直播间 {room_id} 已下播")

    return dict(LIVE_METRICS, room_id=room_id)


def send_live_script(room_id: str, script: str, target: str) -> Dict[str, Any]:
    """Push a script to the livestream control panel.

    Args:
        room_id: Livestream room ID.
        script: Script text.
        target: Delivery target ("main_screen", "popup", "teleprompter").

    Returns:
        {"success": True, "delivered_to": ...}

    Raises:
        LiveRoomOffline
    """
    _maybe_fail()

    if random.random() < 0.05:
        raise LiveRoomOffline(f"直播间 {room_id} 已下架或已关闭")

    return {"success": True, "room_id": room_id, "delivered_to": target, "script_length": len(script)}


# ---------------------------------------------------------------------------
# 四、数据分析域 (Data Analysis Domain) — 3 functions
# ---------------------------------------------------------------------------

def get_multi_platform_report(platforms: List[str], start_date: str, end_date: str,
                               group_by: str) -> Dict[str, Any]:
    """Get aggregated report across multiple platforms.

    Args:
        platforms: List of platform names.
        start_date: Start date.
        end_date: End date.
        group_by: Grouping key ("client").

    Returns:
        Aggregated report dict.

    Raises:
        PartialPlatformFailure
    """
    _maybe_fail()

    failed_platforms = []
    groups = []

    for client in CLIENT_DATA:
        total_cost = 0
        total_roi_sum = 0
        total_cpa_sum = 0
        platform_count = 0

        for plat in platforms:
            if plat in client["platforms"]:
                pd = client["platforms"][plat]
                if random.random() < 0.05:
                    failed_platforms.append(f"{client['name']}/{plat}")
                    continue
                total_cost += pd["cost"]
                total_roi_sum += pd["roi"]
                total_cpa_sum += pd["cpa"]
                platform_count += 1

        if platform_count > 0:
            groups.append({
                "name": client["name"],
                "cost": total_cost,
                "roi": round(total_roi_sum / platform_count, 2),
                "cpa": round(total_cpa_sum / platform_count, 1),
            })

    result = {"groups": groups, "start_date": start_date, "end_date": end_date}
    if failed_platforms:
        result["warnings"] = f"部分平台数据缺失: {', '.join(failed_platforms)}"
    return result


def generate_budget_proposal(current_allocation: Dict[str, Any],
                              constraints: Dict[str, Any]) -> Dict[str, Any]:
    """Generate budget reallocation proposal.

    Args:
        current_allocation: Current budget allocation per client.
        constraints: Constraints for the proposal.

    Returns:
        Proposal dict with reallocation recommendations.

    Raises:
        InsufficientData
    """
    _maybe_fail()

    if not current_allocation:
        raise InsufficientData("预算数据不足，无法生成建议")

    return {
        "proposal": [
            {"client": "客户A", "change": "-20%", "amount": -10000, "reason": "ROI 仅 1.5，远低于整体平均", "transfer_to": "客户C"},
            {"client": "客户D", "change": "-30%", "amount": -15000, "reason": "ROI 仅 1.2，持续下滑 3 周", "transfer_to": "客户E"},
            {"client": "客户C", "change": "+35%", "amount": 15000, "reason": "ROI 3.2，回报率最高，建议加大投入"},
            {"client": "客户E", "change": "+25%", "amount": 10000, "reason": "ROI 2.8，增长趋势良好"},
        ],
        "estimated_roi_improvement": 0.3,
    }


def generate_ppt_outline(title: str, data: Dict[str, Any], template: str) -> Dict[str, Any]:
    """Generate a PPT outline from data.

    Args:
        title: Presentation title.
        data: Data to include in the outline.
        template: Template name.

    Returns:
        PPT outline dict with slides.

    Raises:
        TemplateNotFound
    """
    _maybe_fail()

    if template not in ("monthly_report", "client_proposal", "optimization_summary"):
        raise TemplateNotFound(f"PPT 模板 {template} 不存在")

    return {
        "title": title,
        "slides": [
            {"number": 1, "title": "数据概览", "bullets": ["整体消耗 ¥{total_cost}", "平均 ROI {avg_roi}", "平均 CPA ¥{avg_cpa}"], "chart_type": "kpi_cards"},
            {"number": 2, "title": "客户 ROI 排名", "bullets": ["Top 3: 客户C(3.2), 客户E(2.8), 客户B(2.2)", "Bottom 2: 客户D(1.2), 客户A(1.5)"], "chart_type": "bar"},
            {"number": 3, "title": "预算再分配建议", "bullets": ["客户A: -20% → 客户C", "客户D: -30% → 客户E", "预计整体 ROI 提升 0.3"], "chart_type": "table"},
            {"number": 4, "title": "下周行动建议", "bullets": ["重点关注客户D投放策略调整", "客户C加大预算至 ROI 拐点", "新增小红书投放测试"], "chart_type": "text"},
        ],
        "template": template,
    }


# ---------------------------------------------------------------------------
# 五、通知与系统域 (Notification & System Domain) — 4 functions
# ---------------------------------------------------------------------------

def send_feishu_notification(user_id: str, title: str, content: str,
                              priority: str = "normal") -> Dict[str, Any]:
    """Send a Feishu notification to a user.

    Args:
        user_id: Target user ID.
        title: Notification title.
        content: Notification body.
        priority: "low", "normal", "high".

    Returns:
        {"success": True, "msg_id": "..."}

    Raises:
        FeishuRateLimit
    """
    _maybe_fail()

    if random.random() < 0.05:
        raise FeishuRateLimit("飞书消息发送频率超限")

    return {"success": True, "user_id": user_id, "msg_id": f"msg_{random.randint(1000, 9999)}", "priority": priority}


def log_to_erp(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Log an event to the ERP system.

    Args:
        event_type: Event type string.
        payload: Event payload.

    Returns:
        {"success": True, "log_id": "..."}

    Raises:
        ERPUnavailable
    """
    _maybe_fail()

    if random.random() < 0.05:
        raise ERPUnavailable("ERP 系统不可用")

    return {"success": True, "log_id": f"ERP-{random.randint(1000, 9999)}", "event_type": event_type}


# In-memory preference store
_PREFERENCES: Dict[str, Dict[str, Any]] = {}


def save_user_preference(session_id: str, key: str, value: Any) -> Dict[str, Any]:
    """Save a user preference (long-term memory).

    Args:
        session_id: Session identifier.
        key: Preference key.
        value: Preference value.

    Returns:
        {"success": True}
    """
    if session_id not in _PREFERENCES:
        _PREFERENCES[session_id] = {}
    _PREFERENCES[session_id][key] = value
    return {"success": True, "key": key}


def load_user_preference(session_id: str, key: str) -> Optional[Any]:
    """Load a user preference (long-term memory).

    Args:
        session_id: Session identifier.
        key: Preference key.

    Returns:
        Preference value or None.
    """
    prefs = _PREFERENCES.get(session_id, {})
    return {"key": key, "value": prefs.get(key)}
