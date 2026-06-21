"""Intent classification API — powered by DeepSeek."""
from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from backend.app.core.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

router = APIRouter()

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


class IntentRequest(BaseModel):
    user_input: str
    history: list[dict] = []


SYSTEM_PROMPT = """你是 AdCockpit 的意图分类器。根据用户输入返回 JSON：{"type":"business|conversational","scene":"ad_placement|content|create|ecommerce|data_analysis|diagnosis|","reply":"友好且具体的回复（始终必填）"}

业务场景（严格按关键词区分，不要混淆）：
- create: 【新建/创建/投放/上线】广告计划。用户说"投放"、"发布计划"、"新建计划"、"上线"、"创建一个广告"、"投放一个新计划"、"帮我投广告" → 都属于 create
- ad_placement: 【优化/分析/调整/检查】已有广告。用户说"优化"、"调价"、"ROI太低"、"检查投放效果"、"分析计划"、"降低出价"、"调整预算" → 才属于 ad_placement
- content: 【生成/写/创作】脚本或【分析/拆解】素材。用户说"生成脚本"、"写带货文案"、"分析素材点击率"、"爆款特征" → content
- ecommerce: 【直播/库存/优惠券/发券/补货/催单】→ ecommerce
- data_analysis: 【报表/排名/预算分配/PPT/数据汇总】→ data_analysis
- diagnosis: 【故障/排查/诊断/恢复/异常/出问题了】→ diagnosis

关键区分规则：
1. "投放"单独出现 = create（新建并投放）
2. "投放优化"或"优化投放" = ad_placement
3. 只有明确提到"优化/调整/分析/检查"已有计划时才是 ad_placement
4. 不确定时优先选 create（因为用户通常是想开始投放）

reply 要求（始终友好具体）：
- create: 告知用户识别到想新建投放计划，下方有表单可填平台/名称/预算/出价
- ad_placement: 告知识别到优化意图，下方参数面板可调 ROI阈值/出价等
- content: 告知识别到内容生产意图，可选平台/模板/数量
- 只输出 JSON"""


@router.post("/intent/classify")
async def classify(body: IntentRequest):
    import json, re, time
    for attempt in range(3):
        try:
            msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in body.history[-6:]:
                role = "assistant" if m["role"] == "agent" else "user"
                msgs.append({"role": role, "content": m["content"][:200]})
            msgs.append({"role": "user", "content": body.user_input})
            r = client.chat.completions.create(
                model="deepseek-chat", messages=msgs, temperature=0.1, max_tokens=300,
            )
            text = r.choices[0].message.content.strip()
            if "```" in text:
                m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
                if m: text = m.group(1).strip()
            m2 = re.search(r'\{.*\}', text, re.DOTALL)
            if m2: text = m2.group(0)
            result = json.loads(text)
            print(f"[LLM OK] input='{body.user_input[:30]}' → type={result.get('type')} scene={result.get('scene')}")
            return result
        except Exception as e:
            err = str(e)[:80]
            print(f"[LLM RETRY {attempt+1}/3] input='{body.user_input[:30]}' error={err}")
            if attempt < 2: time.sleep(1)
    return keyword_fallback(body.user_input)


def keyword_fallback(user_input: str) -> dict:
    """Helpful keyword fallback if DeepSeek fails."""
    t = user_input.lower()

    # Greetings
    if any(k in t for k in ["你好", "hi", "hello", "嗨", "早", "在吗"]):
        return {"type":"conversational","scene":"","reply":"你好！我是 AdCockpit AI 优化师。我可以帮你做广告投放优化、内容生产、直播场控、数据分析、故障诊断。有什么可以帮你的？"}

    # Identity
    if any(k in t for k in ["你是谁", "你是什么", "你叫", "你的名字"]):
        return {"type":"conversational","scene":"","reply":"我是 AdCockpit，一个 AI 数字营销驾驶舱。背后有 8 个 AI Agent 协作，覆盖投放优化、内容生产、电商场控和数据分析。"}

    # Capability
    if any(k in t for k in ["功能", "能做什么", "可以做什么", "有什么能力", "你会", "帮助", "help", "怎么用", "使用", "介绍"]):
        return {"type":"conversational","scene":"","reply":"我可以帮你：\n1. 广告投放优化 — 检查多平台 ROI、自动调价/降预算\n2. 内容生产 — 分析素材、提取爆款特征、AI 生成带货脚本\n3. 直播场控 — 实时库存监控、发券、催单话术\n4. 数据分析 — 跨平台报表、客户排名、PPT 提纲\n5. 故障诊断 — 排查异常、根因分析、自动恢复\n\n直接在对话框描述需求，比如「检查最近7天抖音Top5的ROI」。"}

    # Thanks/bye
    if any(k in t for k in ["谢谢", "感谢", "再见", "拜拜"]):
        return {"type":"conversational","scene":"","reply":"不客气！有需要随时找我。"}

    # ── Business intent keyword routing ──
    # create — 新建/创建/投放/上线
    if any(k in t for k in ["新建", "创建", "投放", "上线", "发布计划", "投广告", "创建一个"]):
        if any(k in t for k in ["优化", "调价", "调整", "ROI", "分析"]):
            return {"type":"business","scene":"ad_placement","reply":"识别到你想优化广告投放效果。下方是优化参数面板，你可以调整平台、ROI阈值、出价比例等参数，调整后点击「开始优化」我会为你执行。"}
        return {"type":"business","scene":"create","reply":"识别到你想新建广告投放计划。请在下方表单填写平台、计划名称、日预算和出价，填写后点击「提交投放计划」我会为你创建并投放。"}
    # ad_placement — 优化/调价/分析/检查
    if any(k in t for k in ["优化", "调价", "调整", "检查投放", "分析计划", "ROI", "出价高", "消耗大", "降预算"]):
        return {"type":"business","scene":"ad_placement","reply":"识别到你想优化广告投放效果。下方是优化参数面板，你可以调整平台、ROI阈值、出价比例等参数，调整后点击「开始优化」我会为你执行。"}
    # content
    if any(k in t for k in ["素材", "脚本", "文案", "带货", "爆款", "内容"]):
        return {"type":"business","scene":"content","reply":"识别到你想做内容生产。下方是内容生产参数面板，你可以选择平台、模板和生成数量，调整后点击「预览脚本」我会为你生成。"}
    # ecommerce
    if any(k in t for k in ["直播", "库存", "优惠券", "发券", "补货", "催单"]):
        return {"type":"business","scene":"ecommerce","reply":"识别到直播场控需求。我支持库存查询与补货、优惠券创建与发放、催单话术推送。请具体描述你的需求。"}
    # data_analysis
    if any(k in t for k in ["报表", "排名", "PPT", "数据汇总", "预算分配", "客户分析"]):
        return {"type":"business","scene":"data_analysis","reply":"识别到数据分析需求。我支持跨平台数据聚合、客户排名、预算建议和 PPT 提纲生成。请具体描述你的需求。"}
    # diagnosis
    if any(k in t for k in ["故障", "排查", "诊断", "恢复", "出问题", "异常", "报错"]):
        return {"type":"business","scene":"diagnosis","reply":"识别到故障诊断需求。我支持计划状态查询、根因分析和自动恢复。请具体描述你遇到的问题。"}
    # Generic "广告" hint — treat as business intent, guide to create
    if any(k in t for k in ["广告"]):
        return {"type":"business","scene":"create","reply":"你是想新建广告投放计划吗？请在下方表单填写平台、计划名称、日预算和出价。如果有已投放在跑的计划，也可以输入「优化投放ROI」来诊断和调价。"}

    # "计划" alone → likely wants to see or manage campaigns → ad_placement
    if any(k in t for k in ["计划", "投放计划", "我的计划", "所有计划", "查看计划", "列出计划", "管理计划", "计划列表"]):
        return {"type":"business","scene":"ad_placement","reply":"识别到你想查看投放计划。下方是优化参数面板，你也可以直接查看右侧仪表盘的计划明细表。如果想调整出价或预算，点击「开始优化」即可。"}

    # Truly unclear
    return {"type":"conversational","scene":"","reply":"抱歉，我不太确定你的需求。你可以试试：①「新建广告计划」创建投放 ②「优化投放ROI」诊断调价 ③「生成带货脚本」生产内容 ④「查看所有计划」浏览数据。请更具体地描述一下。"}
