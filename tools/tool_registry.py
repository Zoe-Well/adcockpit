"""Tool registry — LangChain @tool decorator per constitution v1.0 requirement.

All Agent tools MUST use @tool decorator (LangChain 1.2.3+).
Fallback to plain function if langchain not installed.
"""
from typing import List, Dict, Any, Callable, Optional

from tools.mock_functions import (
    get_top_campaigns, get_campaign_detail, update_bid, update_budget,
    get_plan_status, replace_creative, resubmit_plan, get_platform_report,
    get_top_creatives, analyze_video_frames, generate_script, publish_to_feishu,
    get_product_stock, update_stock, create_coupon, get_live_metrics, send_live_script,
    get_multi_platform_report, generate_budget_proposal, generate_ppt_outline,
    send_feishu_notification, log_to_erp, save_user_preference, load_user_preference,
)

try:
    from langchain.tools import tool as langchain_tool
    _HAS_LANGCHAIN = True
except ImportError:
    _HAS_LANGCHAIN = False


def _wrap(func: Callable, name: str, description: str):
    """Wrap a mock function as a tool, using @tool if available."""
    if _HAS_LANGCHAIN:
        return langchain_tool(name=name, description=description)(func)
    return {"name": name, "description": description, "func": func}


# ===== Ad Placement Tools (8) =====
get_top_campaigns_tool = _wrap(
    get_top_campaigns, "get_top_campaigns",
    "获取指定平台按指标排名的Top N广告计划。Args: platform(douyin|tencent), days, metric(cost|roi), top_n")
get_campaign_detail_tool = _wrap(
    get_campaign_detail, "get_campaign_detail", "获取单个广告计划的详细信息")
update_bid_tool = _wrap(
    update_bid, "update_bid", "更新广告计划出价")
update_budget_tool = _wrap(
    update_budget, "update_budget", "更新广告计划日预算")
get_plan_status_tool = _wrap(
    get_plan_status, "get_plan_status", "获取计划状态（含审核状态）")
replace_creative_tool = _wrap(
    replace_creative, "replace_creative", "替换计划素材并重新提交审核")
resubmit_plan_tool = _wrap(
    resubmit_plan, "resubmit_plan", "重新提交审核")
get_platform_report_tool = _wrap(
    get_platform_report, "get_platform_report", "获取平台报表数据")

AD_TOOLS = [
    get_top_campaigns_tool, get_campaign_detail_tool, update_bid_tool,
    update_budget_tool, get_plan_status_tool, replace_creative_tool,
    resubmit_plan_tool, get_platform_report_tool,
]

# ===== Content Tools (4) =====
get_top_creatives_tool = _wrap(
    get_top_creatives, "get_top_creatives", "获取高/低点击率素材")
analyze_video_frames_tool = _wrap(
    analyze_video_frames, "analyze_video_frames", "多模态视频帧分析")
generate_script_tool = _wrap(
    generate_script, "generate_script", "基于模板生成口播脚本")
publish_to_feishu_tool = _wrap(
    publish_to_feishu, "publish_to_feishu", "发布内容到飞书知识库")

CONTENT_TOOLS = [get_top_creatives_tool, analyze_video_frames_tool, generate_script_tool, publish_to_feishu_tool]

# ===== Ecommerce Tools (5) =====
get_product_stock_tool = _wrap(
    get_product_stock, "get_product_stock", "查询商品库存")
update_stock_tool = _wrap(
    update_stock, "update_stock", "增加商品库存")
create_coupon_tool = _wrap(
    create_coupon, "create_coupon", "创建优惠券")
get_live_metrics_tool = _wrap(
    get_live_metrics, "get_live_metrics", "获取直播间实时指标")
send_live_script_tool = _wrap(
    send_live_script, "send_live_script", "推送话术到中控台")

ECOM_TOOLS = [get_product_stock_tool, update_stock_tool, create_coupon_tool,
              get_live_metrics_tool, send_live_script_tool]

# ===== Data Analysis Tools (3) =====
get_multi_platform_report_tool = _wrap(
    get_multi_platform_report, "get_multi_platform_report", "多平台聚合报表")
generate_budget_proposal_tool = _wrap(
    generate_budget_proposal, "generate_budget_proposal", "生成预算分配建议")
generate_ppt_outline_tool = _wrap(
    generate_ppt_outline, "generate_ppt_outline", "生成PPT提纲")

DATA_TOOLS = [get_multi_platform_report_tool, generate_budget_proposal_tool, generate_ppt_outline_tool]

# ===== Notification Tools (4) =====
send_feishu_notification_tool = _wrap(
    send_feishu_notification, "send_feishu_notification", "发送飞书通知")
log_to_erp_tool = _wrap(
    log_to_erp, "log_to_erp", "记录事件到ERP日志")
save_user_preference_tool = _wrap(
    save_user_preference, "save_user_preference", "保存用户偏好（长期记忆）")
load_user_preference_tool = _wrap(
    load_user_preference, "load_user_preference", "加载用户偏好（长期记忆）")

NOTIFY_TOOLS = [send_feishu_notification_tool, log_to_erp_tool, save_user_preference_tool, load_user_preference_tool]

ALL_TOOLS = AD_TOOLS + CONTENT_TOOLS + ECOM_TOOLS + DATA_TOOLS + NOTIFY_TOOLS
