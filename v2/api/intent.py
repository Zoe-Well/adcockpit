"""Intent Classification API."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class IntentRequest(BaseModel):
    user_input: str


@router.post("/intent/classify")
async def classify_intent(body: IntentRequest):
    """Classify user input as conversational or business intent."""
    t = body.user_input.lower()

    # Conversational patterns
    conv_patterns = [
        "你好", "嗨", "hello", "hi", "hey", "早上好", "下午好", "晚上好",
        "谢谢", "感谢", "再见", "拜拜", "你是谁", "你是什么", "你叫什么",
        "你能", "你会", "你可以", "怎么", "如何",
        "能帮我", "能干嘛", "能做什么", "有什么", "介绍一下",
        "什么是", "是什么意思", "为什么", "怎样", "哪里", "哪个", "什么",
        "在吗", "在不在", "测试", "test",
    ]
    is_conv = any(kw in t for kw in conv_patterns)

    # Business keywords
    action_verbs = [
        "检查", "拉取", "查询", "优化", "帮我看看", "帮我查", "帮我",
        "分析", "排查", "诊断", "生成", "创建", "调整", "修改",
        "降价", "提价", "调价", "执行", "运行",
    ]
    biz_targets = [
        "roi", "计划", "消耗", "投放", "广告", "出价", "预算",
        "素材", "脚本", "视频", "ctr", "点击率", "转化", "cvr",
        "直播", "库存", "优惠券", "场控", "补货",
        "报表", "客户", "排名", "数据", "ppt",
        "故障", "没量", "审核", "拒绝",
    ]
    has_action = any(kw in t for kw in action_verbs)
    has_target = any(kw in t for kw in biz_targets)
    is_biz = has_action and has_target and len(t) > 3

    # Scene detection
    scene = "ad_placement"
    if is_biz:
        if any(kw in t for kw in ["素材", "脚本", "视频", "内容", "混剪", "ctr", "点击率", "创意"]):
            scene = "content"
        elif any(kw in t for kw in ["直播", "库存", "优惠券", "场控", "补货", "催单"]):
            scene = "ecommerce"
        elif any(kw in t for kw in ["报表", "预算", "客户", "ppt", "排名", "汇总"]):
            scene = "data_analysis"
        elif any(kw in t for kw in ["排查", "诊断", "故障", "没量", "恢复", "审核", "拒绝"]):
            scene = "diagnosis"

    # Reply for conversational
    reply = ""
    if is_conv and not is_biz:
        if any(kw in t for kw in ["你好", "hello", "hi", "嗨", "在吗"]):
            reply = "你好！我是 AdCockpit AI 优化师。我可以帮你完成广告投放优化、内容生产、直播监控、数据分析和故障诊断。有什么可以帮你的？"
        elif any(kw in t for kw in ["你是谁", "你是什么"]):
            reply = "我是 AdCockpit，一个 AI 数字营销驾驶舱。我背后有 8 个 AI Agent 协作工作，覆盖广告投放优化、内容生产、电商场控和数据分析。"
        elif any(kw in t for kw in ["能做什么", "有什么能力", "帮助", "怎么用", "功能"]):
            reply = "我可以帮你：广告投放优化（检查 ROI、自动调价）、内容生产（分析素材、生成脚本）、直播场控（查库存、发券、催单话术）、数据分析（跨平台报表、预算建议）、故障诊断（自动排查恢复）。"
        elif any(kw in t for kw in ["谢谢", "感谢"]):
            reply = "不客气！有需要随时找我。"
        else:
            reply = "你好！我不太确定你的需求。你可以试试说「检查抖音和腾讯最近7天的ROI」或「分析素材点击率」。"
    elif not is_biz:
        reply = "抱歉，我不太确定你的需求。我是 AdCockpit AI 优化师，可以帮你做投放优化、内容生产、直播监控和数据分析。请更具体地描述你的需求，比如「检查最近7天抖音消耗Top5中ROI<2的计划」。"

    return {
        "type": "business" if is_biz else "conversational",
        "scene": scene,
        "reply": reply,
    }
