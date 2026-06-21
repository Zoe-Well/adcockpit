"""Strategy Agent — LLM-powered optimization strategy generation."""
import json, sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from openai import OpenAI
from backend.app.core.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

def strategy_agent_node(state: dict) -> dict:
    anomalies = state.get("analysis_result", {}).get("anomalies", [])
    if not anomalies: return {"strategy_actions": [], "analysis_result": state.get("analysis_result",{})}
    anom_text = "\n".join(f"{a.get('id','?')}: ROI={a.get('roi',0)}, issue={a.get('issue','?')}" for a in anomalies)
    try:
        r = client.chat.completions.create(model="deepseek-chat",
            messages=[{"role":"system","content":"你是广告优化策略师。对异常计划生成优化建议。返回JSON：{\"actions\":[{\"target_id\":\"\",\"action\":\"update_bid|update_budget\",\"value\":0,\"reason\":\"\"}],\"summary\":\"\"}"},
                      {"role":"user","content":anom_text}], temperature=0.3, max_tokens=500)
        result = json.loads(r.choices[0].message.content.strip().replace("```json","").replace("```",""))
        actions = []
        for a in result.get("actions",[]):
            actions.append({"target_id":a["target_id"],"action":a["action"],"params":{"new_value":a["value"]},"risk_level":"medium","expected_effect":a.get("reason",""),"requires_approval":True})
        return {"strategy_actions":actions,"analysis_result":{**state.get("analysis_result",{}),"strategy_summary":result.get("summary","")}}
    except: return {"strategy_actions":[],"analysis_result":state.get("analysis_result",{})}
