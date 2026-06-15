"""Supervisor Agent — LLM-powered task decomposition."""
import json; import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from openai import OpenAI
from backend.app.core.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

SYSTEM = """你是 AdCockpit 的任务调度器。分析用户输入并返回 JSON：
{"scene":"ad_placement|content|create|ecommerce|data_analysis|diagnosis","summary":"一句话概括","tasks":["步骤1","步骤2",...]}"""

def supervisor_node(state: dict) -> dict:
    try:
        r = client.chat.completions.create(model="deepseek-chat",
            messages=[{"role":"system","content":SYSTEM},{"role":"user","content":state.get("user_input","")}],
            temperature=0.2, max_tokens=400)
        d = json.loads(r.choices[0].message.content.strip())
        return {"current_scene": d.get("scene","ad_placement"), "analysis_result": {"supervisor_summary":d.get("summary",""), "tasks":d.get("tasks",[])}}
    except: return {"current_scene":"ad_placement"}
