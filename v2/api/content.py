"""Content Production API — generate scripts, publish to Feishu."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()


class GenerateRequest(BaseModel):
    platform: str = "douyin"
    top_n: int = 3
    template_id: str = "summer_promo"


class PublishRequest(BaseModel):
    scripts: List[str]
    platform: str = "douyin"
    template_id: str = "summer_promo"


@router.post("/content/generate")
async def generate_scripts(body: GenerateRequest):
    """Generate scripts without publishing."""
    from tools.mock_functions import generate_script

    scripts = []
    for i in range(body.top_n):
        for _ in range(5):
            try:
                s = generate_script(template_id=body.template_id,
                                    params={"product_name": f"爆款商品-{chr(65+i)}"})
                scripts.append(s)
                break
            except Exception:
                pass
        else:
            scripts.append(f"[脚本{chr(65+i)}生成失败]")

    return {"scripts": scripts, "count": len(scripts)}


@router.post("/content/publish")
async def publish_scripts_endpoint(body: PublishRequest):
    """Publish scripts to Feishu."""
    from tools.feishu_client import publish_scripts

    try:
        results = publish_scripts(body.scripts, body.platform, body.template_id)
        urls = [r.get("url", "") for r in results]
        return {"urls": urls, "success": True}
    except Exception as e:
        return {"urls": [], "success": False, "error": str(e)[:200]}
