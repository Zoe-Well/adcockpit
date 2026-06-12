"""AdCockpit Streamlit main entry — three-column conversational cockpit."""
from datetime import datetime
import streamlit as st
import requests
from ui.theme import inject_custom_css


def _load_campaign_data():
    """Query mock platform APIs and store results in session_state."""
    from tools.mock_data import DOUYIN_PLANS, TENCENT_PLANS, DASHBOARD_METRICS
    from tools.mock_functions import get_top_campaigns

    if "campaign_data" not in st.session_state or st.session_state.get("_reload_data"):
        st.session_state._reload_data = False
        try:
            douyin = get_top_campaigns("douyin", days=7, metric="cost", top_n=5)
            tencent = get_top_campaigns("tencent", days=7, metric="cost", top_n=5)
        except Exception:
            # Fallback to raw mock data if random exception fires
            douyin = list(DOUYIN_PLANS)
            tencent = list(TENCENT_PLANS)

        all_plans = []
        for p in douyin:
            p["_platform"] = "douyin"
            all_plans.append(p)
        for p in tencent:
            p["_platform"] = "tencent"
            all_plans.append(p)

        # Merge user-created campaigns
        created = st.session_state.get("_created_campaigns", [])
        for c in created:
            # Avoid duplicates
            if not any(p["id"] == c["id"] for p in all_plans):
                all_plans.append(c)

        total_cost = sum(p["cost"] for p in all_plans)
        avg_roi = round(sum(p["roi"] for p in all_plans) / len(all_plans), 2)
        avg_cpa = round(sum(p.get("cpa", 0) for p in all_plans) / len(all_plans), 1)
        avg_ctr = round(sum(p.get("ctr", 0) for p in all_plans) / len(all_plans) * 100, 1)
        avg_cvr = round(sum(p.get("cvr", 0) for p in all_plans) / len(all_plans) * 100, 1)
        below_threshold = [p for p in all_plans if p["roi"] < 2.0]

        st.session_state.campaign_data = {
            "douyin": douyin,
            "tencent": tencent,
            "all_plans": all_plans,
            "total_cost": total_cost,
            "avg_roi": avg_roi,
            "avg_cpa": avg_cpa,
            "avg_ctr": avg_ctr,
            "avg_cvr": avg_cvr,
            "below_threshold": below_threshold,
            "active_count": len(all_plans),
            "loaded_at": datetime.now().isoformat(),
        }

        # Note: trace_events are now generated in chat_panel on user action,
        # not here. This keeps the trace board reactive to actual user operations.


def init_session():
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"demo-{datetime.now().strftime('%m%d-%H%M')}"
    defaults = {
        "trace_events": [],
        "chat_messages": [
            {"role": "agent", "content": "👋 你好，我是 AdCockpit AI 优化师。\n\n"
             "我可以帮你：\n• 跨平台广告投放分析与自动优化\n• 投后素材分析 & AI 内容生产\n"
             "• 直播间实时场控与电商闭环\n• 多平台数据聚合与预算建议\n• 全链路故障诊断与自动恢复\n\n"
             "请描述你的需求，或点击场景标签快速开始。"}
        ],
        "approval_pending": None,
        "current_scene": "ad_placement",
        "current_scene_display": "投放优化",
        "api_status": "disconnected",
        "_reload_data": True,
        "optim_params": {
            "platforms": ["douyin", "tencent"],
            "days": 7,
            "top_n": 5,
            "roi_threshold": 2.0,
            "bid_adjust_pct": -10,
            "budget_adjust_pct": -20,
            "risk_confirm": "medium",  # low/medium/high — risk level requiring confirmation
        },
        "show_param_card": False,  # toggle parameter confirmation card
        "content_params": {
            "platform": "douyin",
            "date": "yesterday",
            "top_n": 3,
            "worst_n": 3,
            "template_id": "summer_promo",
            "auto_publish": True,
        },
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def main():
    st.set_page_config(layout="wide", page_title="AdCockpit", page_icon="⚡")
    inject_custom_css()
    init_session()
    _load_campaign_data()

    # ---- Top Bar ----
    st.markdown(f"""
    <div class="topbar">
      <span class="logo">⚡ AdCockpit</span>
      <span class="badge">Demo v1.0</span>
      <span style="font-size:12px;color:var(--text-secondary);">数字营销 AI 对话驾驶舱</span>
      <span style="margin-left:auto;font-size:11px;color:var(--text-muted);">
        🟢 系统正常 &nbsp;|&nbsp; 场景: <strong>{st.session_state.current_scene_display}</strong>
      </span>
    </div>
    """, unsafe_allow_html=True)

    # ---- Three-column layout ----
    left, center, right = st.columns([0.32, 0.26, 0.42], gap="small")

    with left:
        st.markdown('<div class="col-header">💬 对话面板 — Chat Panel</div>', unsafe_allow_html=True)
        from ui.panels.chat_panel import render_chat_panel
        render_chat_panel()

    with center:
        st.markdown('<div class="col-header">🔗 Agent 编排与执行追踪 — Trace Board</div>', unsafe_allow_html=True)
        from ui.panels.trace_board import render_trace_board
        render_trace_board()

    with right:
        st.markdown(f'<div class="col-header">📊 数据洞察仪表盘 — Insight Dashboard &nbsp;<span style="font-size:9px;color:var(--text-muted);font-weight:400);">{st.session_state.current_scene_display} · {st.session_state.active_tab}</span></div>', unsafe_allow_html=True)
        from ui.panels.dashboard import render_dashboard
        render_dashboard()

    # ---- Streaming animation: nodes light up + text types out ----
    if st.session_state.get("_trace_animating", False):
        import time as _time
        step = st.session_state.get("_trace_step", 0)
        events = st.session_state.get("trace_events", [])
        ts = datetime.now().isoformat()

        # Node order depends on scene
        biz_scene = st.session_state.get("_biz_scene", "ad_placement")
        if biz_scene == "content":
            node_order = ["supervisor", "data", "analysis", "content", "execute", "report"]
        elif biz_scene == "create":
            node_order = ["supervisor", "data", "execute", "report"]
        else:
            node_order = ["supervisor", "data", "data_2", "analysis", "strategy", "execute", "report"]
        # Each node gets multiple frames for typing animation
        TYPING_FRAMES_PER_NODE = 3  # frames of incremental text reveal per node
        total_frames = len(node_order) * TYPING_FRAMES_PER_NODE + 1  # +1 for final settle

        # Determine which node is currently "active"
        active_node_idx = min(step // TYPING_FRAMES_PER_NODE, len(node_order) - 1)
        typing_progress = (step % TYPING_FRAMES_PER_NODE) / TYPING_FRAMES_PER_NODE  # 0.0 to ~1.0

        # Build events based on current frame
        new_events = []
        for i, node in enumerate(node_order):
            if i < active_node_idx:
                # Already completed
                node_event = "step_complete" if node != "execute" else "approval_required"
                if node == "report" and active_node_idx < len(node_order) - 1:
                    node_event = "step_pending"
                elif node == "report":
                    node_event = "step_complete"
                new_events.append({"node": node, "event": node_event, "ts": ts})
            elif i == active_node_idx:
                # Currently running/typing
                if typing_progress < 0.8:
                    new_events.append({"node": node, "event": "step_start" if node != "execute" else "step_start", "ts": ts})
                else:
                    node_event = "step_complete" if node != "execute" else "approval_required"
                    new_events.append({"node": node, "event": node_event, "ts": ts})
            # else: pending, no event

        # Replace events
        for e in new_events:
            events = [ev for ev in events if ev["node"] != e["node"]]
            events.append(e)
        st.session_state.trace_events = events
        st.session_state._trace_step = step + 1

        # Store typing progress for trace_board to use
        st.session_state._typing_progress = typing_progress
        st.session_state._active_node = node_order[active_node_idx] if active_node_idx < len(node_order) else None

        if step < total_frames:
            _time.sleep(0.15)  # faster frames for smoother typing feel
            st.rerun()
        else:
            st.session_state._trace_animating = False
            st.session_state._trace_step = 0
            st.session_state._typing_progress = 1.0
            st.session_state._active_node = None

            # Create: leave execute as waiting, report as pending
            if biz_scene == "create":
                ts = datetime.now().isoformat()
                events = st.session_state.get("trace_events", [])
                for node in node_order:
                    if node in ("execute", "report"):
                        evt = "approval_required" if node == "execute" else "step_pending"
                    else:
                        evt = "step_complete"
                    events = [e for e in events if e["node"] != node]
                    events.append({"node": node, "event": evt, "ts": ts})
                st.session_state.trace_events = events
            # Content: leave execute as waiting, report as pending
            elif biz_scene == "content":
                ts = datetime.now().isoformat()
                events = st.session_state.get("trace_events", [])
                # Ensure execute/report stay in approval/pending state
                for e in events:
                    if e["node"] == "execute":
                        e["event"] = "approval_required"
                    if e["node"] == "report":
                        e["event"] = "step_pending"
                # If execute/report not in events, add them
                if not any(e["node"] == "execute" for e in events):
                    events.append({"node":"execute","event":"approval_required","ts":ts})
                if not any(e["node"] == "report" for e in events):
                    events.append({"node":"report","event":"step_pending","ts":ts})
                st.session_state.trace_events = events
            # Ad placement: show approval card
            elif not st.session_state.get("approval_pending"):
                st.session_state.approval_pending = [
                    {"target_id":"C001","action":"update_bid","params":{"new_bid":22.5},"risk_level":"medium"},
                    {"target_id":"T001","action":"update_bid","params":{"new_bid":27.0},"risk_level":"medium"},
                    {"target_id":"T001","action":"update_budget","params":{"new_budget":4000},"risk_level":"high"},
                    {"target_id":"C004","action":"update_bid","params":{"new_bid":18.0},"risk_level":"low"},
                ]


def _execute_content_and_publish():
    """Execute content production and publish scripts to Feishu."""
    from datetime import datetime
    from tools.mock_functions import generate_script

    params = st.session_state.get("content_params", {})
    platform = params.get("platform", "douyin")
    template = params.get("template_id", "summer_promo")
    top_n = params.get("top_n", 3)

    # Generate scripts (with retry for mock failures)
    scripts = []
    for i in range(top_n):
        for attempt in range(3):
            try:
                script = generate_script(
                    template_id=template,
                    params={"product_name": f"爆款商品-{chr(65+i)}"}
                )
                scripts.append(script)
                break
            except Exception:
                if attempt == 2:
                    scripts.append(f"[脚本{i+1}生成失败，请重试]")

    # Publish to Feishu
    urls = []
    from tools.feishu_client import publish_scripts as _publish
    try:
        results = _publish(scripts, platform, template)
        urls = [r.get("url", "") for r in results]
        mock = results[0].get("mock", True) if results else True
        via = "真实飞书文档" if not mock else "Demo模拟"
        url_str = "\n".join(f"📄 脚本{i+1}: {u}" for i, u in enumerate(urls))
        st.session_state.chat_messages.append({
            "role": "agent",
            "content": f"✏️ 内容生产完成！已生成 {len(scripts)} 条脚本并发布到{via}：\n\n{url_str}"
        })
    except Exception as e:
        st.session_state.chat_messages.append({
            "role": "agent",
            "content": f"✏️ 脚本已生成，但发布飞书时出错：{str(e)[:150]}"
        })

    # Mark trace as complete
    ts = datetime.now().isoformat()
    st.session_state.trace_events = [
        {"node":"supervisor","event":"step_complete","ts":ts},
        {"node":"data","event":"step_complete","ts":ts},
        {"node":"analysis","event":"step_complete","ts":ts},
        {"node":"content","event":"step_complete","ts":ts},
        {"node":"execute","event":"step_complete","ts":ts},
        {"node":"report","event":"step_complete","ts":ts},
    ]


if __name__ == "__main__":
    main()
