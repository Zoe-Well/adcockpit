"""Test keyword_fallback — the last line of defense when DeepSeek LLM is down.

Run:  pytest tests/unit/test_intent.py -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.api.intent import keyword_fallback


def test_create_scene_by_keyword_toufang():
    """#1: "广告投放" (投放 alone) → create, NOT ad_placement"""
    r = keyword_fallback("广告投放")
    assert r["type"] == "business", f"Expected business, got {r['type']}"
    assert r["scene"] == "create", f"Expected create, got {r['scene']}"


def test_create_scene_new_campaign():
    """#2: "新建一个抖音广告计划" → create"""
    r = keyword_fallback("新建一个抖音广告计划")
    assert r["type"] == "business"
    assert r["scene"] == "create"


def test_ad_placement_optimize():
    """#3: "优化ROI" → ad_placement"""
    r = keyword_fallback("优化ROI")
    assert r["type"] == "business"
    assert r["scene"] == "ad_placement"


def test_ad_placement_with_toufang_combined():
    """#4: "投放优化" (投放 + 优化 together) → ad_placement, NOT create"""
    r = keyword_fallback("投放优化")
    assert r["type"] == "business"
    assert r["scene"] == "ad_placement"


def test_content_script_generation():
    """#5: "生成带货脚本" → content"""
    r = keyword_fallback("生成带货脚本")
    assert r["type"] == "business"
    assert r["scene"] == "content"


def test_ecommerce_livestream():
    """#6: "直播补货" → ecommerce"""
    r = keyword_fallback("直播补货")
    assert r["type"] == "business"
    assert r["scene"] == "ecommerce"


def test_diagnosis_troubleshoot():
    """#7: "排查故障" → diagnosis"""
    r = keyword_fallback("排查故障")
    assert r["type"] == "business"
    assert r["scene"] == "diagnosis"


def test_data_analysis_ranking():
    """#8: "客户排名" → data_analysis"""
    r = keyword_fallback("客户排名")
    assert r["type"] == "business"
    assert r["scene"] == "data_analysis"


def test_conversational_greeting():
    """#9: Greetings should NOT trigger business intents"""
    r = keyword_fallback("你好")
    assert r["type"] == "conversational"
    assert r["scene"] == ""


def test_conversational_unclear():
    """#10: Totally unclear input → conversational with guidance"""
    r = keyword_fallback("asdfghjkl")
    assert r["type"] == "conversational"
    assert "抱歉" in r["reply"] or "帮助" in r["reply"] or "需求" in r["reply"]
