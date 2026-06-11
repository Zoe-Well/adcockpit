"""Feishu (Lark) Document API Client — real API + mock fallback.

Configure via .env:
  FEISHU_APP_ID=xxx
  FEISHU_APP_SECRET=xxx
  FEISHU_FOLDER_TOKEN=xxx  (optional, parent folder for created docs)

Without credentials, falls back to mock responses.
"""
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

import requests
from dotenv import load_dotenv

# Load from .env first, then .env.example as fallback
# Use absolute paths relative to this file to work regardless of CWD
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_BASE_DIR, ".env"))
if not os.getenv("FEISHU_APP_ID"):
    load_dotenv(os.path.join(_BASE_DIR, ".env.example"))

FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
FEISHU_FOLDER_TOKEN = os.getenv("FEISHU_FOLDER_TOKEN", "")

BASE_URL = "https://open.feishu.cn/open-apis"

# In-memory token cache
_token_cache: Dict[str, Any] = {}


def _is_configured() -> bool:
    """Check if real Feishu credentials are available."""
    return bool(FEISHU_APP_ID and FEISHU_APP_SECRET)


def _get_tenant_token() -> Optional[str]:
    """Get Feishu tenant access token, cached for 1 hour."""
    if not _is_configured():
        return None

    cached = _token_cache.get("tenant_token")
    if cached and cached.get("expires_at", 0) > time.time():
        return cached["token"]

    try:
        resp = requests.post(
            f"{BASE_URL}/auth/v3/tenant_access_token/internal",
            json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
            timeout=10,
        )
        data = resp.json()
        if data.get("code") == 0:
            token = data["tenant_access_token"]
            _token_cache["tenant_token"] = {
                "token": token,
                "expires_at": time.time() + data.get("expire", 3600) - 300,
            }
            return token
    except Exception:
        pass
    return None


# ====== Public API ======

def create_document(title: str, content: str, folder_token: str = "") -> Dict[str, Any]:
    """Create a Feishu document with the given title and content.

    Returns dict with url and doc_id on success.
    Falls back to mock if no credentials configured.
    """
    token = _get_tenant_token()

    if token:
        return _create_document_real(token, title, content, folder_token)
    else:
        return _create_document_mock(title, content)


def _create_document_real(token: str, title: str, content: str, folder_token: str = "") -> Dict[str, Any]:
    """Create a real Feishu document via docx API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    create_body = {"title": title}
    if folder_token:
        create_body["folder_token"] = folder_token

    resp = requests.post(
        f"{BASE_URL}/docx/v1/documents",
        headers=headers,
        json=create_body,
        timeout=15,
    )
    data = resp.json()

    if data.get("code") != 0:
        return _create_document_mock(title, content, f"API error: {data.get('msg')}")

    doc_id = data["data"]["document"]["document_id"]
    doc_url = f"https://bytedance.feishu.cn/docx/{doc_id}"

    # Add content
    try:
        blocks = _text_to_blocks(content)
        requests.post(
            f"{BASE_URL}/docx/v1/documents/{doc_id}/blocks/batch_create",
            headers=headers,
            json={"document_id": doc_id, "blocks": blocks},
            timeout=15,
        )
    except Exception:
        pass

    return {
        "success": True,
        "doc_id": doc_id,
        "url": doc_url,
        "title": title,
        "folder_token": folder_token or "(root)",
        "created_at": datetime.now().isoformat(),
    }


def _create_document_mock(title: str, content: str, note: str = "") -> Dict[str, Any]:
    """Mock document creation for demo/fallback."""
    doc_id = f"doc_{datetime.now().strftime('%m%d%H%M%S')}"
    url = f"https://bytedance.feishu.cn/docx/{doc_id}"

    # Store mock docs in memory for reference
    if "_mock_docs" not in globals():
        # Track created docs so we can show them
        pass

    return {
        "success": True,
        "doc_id": doc_id,
        "url": url,
        "title": title,
        "created_at": datetime.now().isoformat(),
        "mock": True,
        "note": note or "(Demo模式 · 配置FEISHU_APP_ID和FEISHU_APP_SECRET后接入真实飞书)",
        "content_preview": content[:200] + "..." if len(content) > 200 else content,
    }


def _text_to_blocks(text: str) -> List[Dict]:
    """Convert plain text with markdown-ish formatting to Feishu doc blocks."""
    blocks = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        if line.startswith("## "):
            blocks.append({
                "block_type": 3,  # heading2
                "heading2": {
                    "elements": [{"text_run": {"content": line[3:]}}],
                    "style": {},
                }
            })
        elif line.startswith("# "):
            blocks.append({
                "block_type": 2,  # heading1
                "heading1": {
                    "elements": [{"text_run": {"content": line[2:]}}],
                    "style": {},
                }
            })
        elif line.startswith("- ") or line.startswith("• "):
            blocks.append({
                "block_type": 5,  # bullet
                "bullet": {
                    "elements": [{"text_run": {"content": line[2:]}}],
                    "style": {},
                }
            })
        else:
            blocks.append({
                "block_type": 4,  # text
                "text": {
                    "elements": [{"text_run": {"content": line}}],
                    "style": {},
                }
            })
    return blocks


def publish_optimization_report(summary_rows: List[tuple], actions: List[str],
                                 estimated_saving: str = "¥5,640/天 (15%)",
                                 roi_improvement: str = "1.87 → 2.1") -> Dict[str, Any]:
    """Generate and publish an optimization report to Feishu."""
    title = f"AdCockpit 投放优化报告 — {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    content = f"# AdCockpit 投放优化报告\n\n"
    content += f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    content += f"## 优化概要\n\n"
    for label, value in summary_rows:
        content += f"- {label}：{value}\n"
    content += f"\n## 执行操作\n\n"
    for act in actions:
        content += f"- ✅ {act}\n"
    content += f"\n## 优化效果预估\n\n"
    content += f"- **预计节省消耗**：{estimated_saving}\n"
    content += f"- **预计 ROI 提升**：{roi_improvement}\n"
    content += f"- **下次复查建议**：48 小时后\n\n"
    content += f"---\n*本报告由 AdCockpit AI 自动生成*"

    return create_document(title, content)


def publish_scripts(scripts: List[str], platform: str = "douyin",
                    template: str = "summer_promo") -> List[Dict[str, Any]]:
    """Publish generated scripts to Feishu as a document."""
    results = []

    # Create one document per script
    for i, script in enumerate(scripts):
        title = f"带货脚本-{chr(65+i)} — {platform} {template} {datetime.now().strftime('%m%d%H%M')}"

        content = f"# 带货口播脚本 {chr(65+i)}\n\n"
        content += f"**平台**：{'抖音' if platform == 'douyin' else '腾讯广告'}\n"
        content += f"**模板**：{template}\n"
        content += f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        content += f"## 脚本内容\n\n"
        content += f"{script}\n\n"
        content += f"---\n*本脚本由 AdCockpit AI 基于爆款分析自动生成*"

        result = create_document(title, content)
        result["script_index"] = i + 1
        results.append(result)

    return results
