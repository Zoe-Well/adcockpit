"""Analysis Agent — LLM-powered campaign data analysis."""
import json, sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from openai import OpenAI
from backend.app.core.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

def analysis_agent_node(state: dict) -> dict:
    plans = state.get("platform_data", [])
    threshold = state.get("analysis_result", {}).get("roi_threshold", 2.0)
    plan_list = []
    for pd in plans:
        for p in pd.get("data", []):
            plan_list.append(f"{p.get('id','?')}({pd.get('platform','?')}): ROI={p.get('roi',0)}, cost={p.get('cost',0)}, bid={p.get('bid',0)}")
    data_text = "\n".join(plan_list[:15])
    try:
        r = client.chat.completions.create(model="deepseek-chat",
            messages=[{"role":"system","content":f"你是广告数据分析师。分析投放计划，ROI阈值={threshold}。返回JSON：{{\"anomalies\":[{{\"id\":\"\",\"roi\":0,\"issue\":\"\"}}],\"summary\":\"\"}}"},
                      {"role":"user","content":data_text}], temperature=0.3, max_tokens=500)
        result = json.loads(r.choices[0].message.content.strip().replace("```json","").replace("```",""))
        return {"analysis_result": {**state.get("analysis_result",{}), **result, "analysis_summary": result.get("summary","")}}
    except: return {"analysis_result": state.get("analysis_result",{})}
