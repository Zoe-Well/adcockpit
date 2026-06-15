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

业务场景：
- ad_placement: 分析/优化广告投放 ROI、出价、消耗、计划
- content: 生成带货脚本、分析素材、生产内容
- create: 新建广告计划、创建投放
- ecommerce: 直播、库存、优惠券
- data_analysis: 报表、客户排名、预算、PPT
- diagnosis: 排查故障、诊断、恢复

reply 要求（始终友好具体）：
- 业务类：告知用户你识别到什么意图，下方有什么参数面板，用户可以怎么调整，点击什么按钮执行。例如"识别到你想优化广告投放。下方是优化参数面板，你可以调整平台、ROI阈值等参数，调整后点击「开始优化」我会为你执行。"
- 对话类：根据上下文友好回复
- 只输出 JSON"""


@router.post("/intent/classify")
async def classify(body: IntentRequest):
    try:
        msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in body.history[-6:]:
            role = "assistant" if m["role"] == "agent" else "user"
            msgs.append({"role": role, "content": m["content"][:200]})
        msgs.append({"role": "user", "content": body.user_input})
        r = client.chat.completions.create(
            model="deepseek-chat", messages=msgs, temperature=0.1, max_tokens=300,
        )
        import json, re
        text = r.choices[0].message.content.strip()
        # Strip markdown code fences and any text outside JSON
        if "```" in text:
            m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
            if m: text = m.group(1).strip()
        # Try to extract just the JSON object
        m2 = re.search(r'\{.*\}', text, re.DOTALL)
        if m2: text = m2.group(0)
        result = json.loads(text)
        print(f"[LLM OK] input='{body.user_input[:30]}' → type={result.get('type')} scene={result.get('scene')}")
        return result
    except Exception as e:
        print(f"[LLM FAIL] input='{body.user_input[:30]}' error={str(e)[:80]}")
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

    # Vague business hints — give helpful suggestions
    if any(k in t for k in ["优化", "调价", "投放", "广告"]):
        return {"type":"conversational","scene":"","reply":"你是想优化广告投放效果吗？可以试试说「检查最近7天抖音和腾讯消耗Top5中ROI<2的计划」。也可以说「新建广告计划」来创建投放，或「生成带货脚本」来生产内容。"}
    if any(k in t for k in ["素材", "内容", "脚本"]):
        return {"type":"conversational","scene":"","reply":"你是想做内容相关的工作吗？可以试试说「分析抖音最近的素材点击率」或「生成3条夏季促销带货脚本」。"}
    if any(k in t for k in ["直播", "库存", "优惠券"]):
        return {"type":"conversational","scene":"","reply":"你想管理直播间吗？可以试试说「查看直播库存并补货」或「创建优惠券发给直播间」。"}
    if any(k in t for k in ["报表", "数据", "排名"]):
        return {"type":"conversational","scene":"","reply":"你想做数据分析吗？可以试试说「拉取本月抖音和腾讯广告的客户消耗排名」或「生成预算分配建议」。"}

    # Truly unclear
    return {"type":"conversational","scene":"","reply":"抱歉，我不太确定你的需求。我可以帮你：投放优化、内容生产、直播场控、数据分析、故障诊断。请更具体地描述一下，比如「检查最近7天抖音消耗Top5中ROI<2的计划」。"}
