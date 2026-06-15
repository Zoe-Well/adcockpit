"""Content production API."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class GenerateRequest(BaseModel):
    platform: str = "douyin"
    top_n: int = 3
    template_id: str = "summer_promo"


class PublishRequest(BaseModel):
    scripts: list[str]
    platform: str = "douyin"
    template_id: str = "summer_promo"


@router.post("/content/generate")
async def generate(body: GenerateRequest):
    from openai import OpenAI
    from backend.app.core.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    styles = {"summer_promo":"夏季促销快节奏带货","flash_sale":"闪购秒杀紧迫感","product_review":"产品测评真实体验"}
    style = styles.get(body.template_id, "带货口播")
    scripts = []
    for i in range(body.top_n):
        try:
            r = client.chat.completions.create(model="deepseek-chat",
                messages=[{"role":"system","content":f"你是抖音带货脚本专家，生成{style}脚本。80-150字，包含开场钩子+产品卖点+价格优势+紧迫感+下单引导。每次不同。"},
                          {"role":"user","content":f"为产品{chr(65+i)}生成带货脚本"}],
                temperature=0.9, max_tokens=300)
            scripts.append(r.choices[0].message.content.strip())
        except Exception:
            scripts.append(f"[产品{chr(65+i)}生成失败]")
    return {"scripts": scripts}


@router.post("/content/publish")
async def publish(body: PublishRequest):
    """Publish all scripts to a single shared Feishu document."""
    from tools.feishu_client import create_document
    from datetime import datetime
    try:
        content = f"# 带货脚本合集\n\n**平台**: {body.platform}\n**模板**: {body.template_id}\n**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n\n"
        for i, s in enumerate(body.scripts):
            content += f"## 脚本 {i+1}\n\n{s}\n\n---\n\n"
        result = create_document(f"带货脚本-{body.template_id}-{datetime.now().strftime('%m%d%H%M')}", content)
        return {"url": result.get("url", ""), "success": True}
    except Exception as e:
        return {"url": "", "success": False, "error": str(e)[:200]}
