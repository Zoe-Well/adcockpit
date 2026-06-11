"""Left Chat Panel — scene tags, messages, approval, input."""
import streamlit as st
import requests


def render_chat_panel():
    # Init active_tab if missing
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "optimize"

    # ---- All 6 buttons: mutually exclusive via active_tab ----
    all_tabs = [
        ("optimize", "🎯 优化", "ad_placement", "投放优化"),
        ("create",   "📊 投放", "ad_placement", "投放管理"),
        ("content",  "🎬 内容", "content",       "内容生产"),
        ("ecommerce","🛒 电商", "ecommerce",     "电商场控"),
        ("data_analysis","📈 数据","data_analysis","数据分析"),
        ("diagnosis","🔧 诊断", "diagnosis",     "故障诊断"),
    ]
    cols = st.columns(6)
    for i, (tab_key, label, scene, display) in enumerate(all_tabs):
        with cols[i]:
            active = st.session_state.active_tab == tab_key
            if st.button(label, key=f"tab_{tab_key}",
                         type="primary" if active else "secondary",
                         use_container_width=True):
                st.session_state.active_tab = tab_key
                st.session_state.current_scene = scene
                st.session_state.current_scene_display = display
                st.session_state._show_create_form = (tab_key == "create")
                st.session_state.show_param_card = False
                # Clear trace_events when switching tabs (fresh state per tab)
                st.session_state.trace_events = []
                if tab_key == "optimize":
                    st.session_state._reload_data = True
                st.rerun()

    # Status line
    cd = st.session_state.get("campaign_data")
    if cd and cd.get("all_plans"):
        below = len(cd["below_threshold"])
        st.caption(f"✅ {cd['active_count']} 条计划 | ROI {cd['avg_roi']:.2f} | {below} 条不达标 | {st.session_state.current_scene_display}")
    else:
        st.caption(f"点击上方标签切换功能 | 当前: {st.session_state.current_scene_display}")

    # ---- Campaign Creation Form (shown when active_tab == "create") ----
    if st.session_state.get("_show_create_form", False):
        with st.form("create_campaign_form"):
            plat = st.selectbox("投放平台", ["douyin", "tencent"], format_func=lambda x: "抖音" if x == "douyin" else "腾讯广告")
            cname = st.text_input("计划名称", placeholder="例如：618大促-主推款")
            c1, c2 = st.columns(2)
            with c1:
                budget = st.number_input("日预算 (¥)", min_value=500, max_value=50000, value=5000, step=500)
            with c2:
                bid = st.number_input("出价 (¥)", min_value=5.0, max_value=200.0, value=25.0, step=5.0)
            t1, t2 = st.columns(2)
            with t1:
                gender = st.selectbox("性别定向", ["all", "male", "female"])
            with t2:
                age = st.selectbox("年龄定向", ["18-45", "18-24", "25-35", "36-50", "50+"])
            interests = st.multiselect("兴趣标签", ["购物", "直播", "美妆", "服饰", "3C数码", "食品", "母婴", "运动"], default=["购物", "直播"])
            submitted = st.form_submit_button("🚀 创建投放计划", use_container_width=True)
            if submitted:
                if not cname.strip():
                    st.error("请输入计划名称")
                else:
                    try:
                        from tools.mock_functions import create_campaign
                        new_camp = create_campaign(plat, cname.strip(), budget, bid, {"gender": gender, "age_range": age, "interests": interests})
                        # Store in session
                        created = st.session_state.get("_created_campaigns", [])
                        created.append(new_camp)
                        st.session_state._created_campaigns = created
                        st.session_state._reload_data = True
                        st.session_state.chat_messages.append({"role": "agent", "content": f"🚀 新投放计划已创建！\n\n📋 **{new_camp['name']}** ({new_camp['id']})\n• 平台: {'抖音' if plat == 'douyin' else '腾讯广告'}\n• 日预算: ¥{budget:,}\n• 出价: ¥{bid}\n• 状态: {new_camp['status']}\n\n计划已加入投放列表，点击「📋 查询计划」可刷新数据。"})
                        st.success(f"✅ 计划 {new_camp['id']} 创建成功！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"创建失败: {e}")

    # ---- Messages (single HTML block with fixed height for scrollable area) ----
    msgs_html = '<div style="max-height:60vh;overflow-y:auto;padding:0 4px;">'
    for msg in st.session_state.chat_messages:
        role = msg["role"]
        content = msg.get("content", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        if role == "user":
            msgs_html += f'<div class="chat-msg user"><div class="avatar">王</div><div class="bubble">{content}</div></div>'
        else:
            msgs_html += f'<div class="chat-msg agent"><div class="avatar">AI</div><div class="bubble">{content}</div></div>'

    # Approval card inline
    pending = st.session_state.get("approval_pending")
    if pending and isinstance(pending, list) and len(pending) > 0:
        msgs_html += '<div class="approval-card"><div class="ac-title">🛑 待确认 — 调价策略</div>'
        for a in pending:
            target = a.get("target_id", "?")
            act = a.get("action", "?")
            params = a.get("params", {})
            risk = a.get("risk_level", "medium")
            rc = {"low": "var(--success)", "medium": "var(--warning)", "high": "var(--danger)"}.get(risk, "")
            if act == "update_bid":
                desc = f"降价至 ¥{params.get('new_bid', '?')}"
            elif act == "update_budget":
                desc = f"降预算至 ¥{params.get('new_budget', '?')}"
            else:
                desc = str(params)
            msgs_html += f'<div class="ac-row"><span>{target}</span><span>{desc}</span><span style="color:{rc}">{risk.upper()}</span></div>'
        msgs_html += '</div>'
    msgs_html += '</div>'
    st.markdown(msgs_html, unsafe_allow_html=True)

    # Approval buttons (outside scrollable area)
    if pending and isinstance(pending, list) and len(pending) > 0:
        ca, cb = st.columns(2)
        with ca:
            if st.button("✅ 确认", key="ap_ok", use_container_width=True):
                try:
                    requests.post(f"http://localhost:8000/approve/{st.session_state.session_id}", timeout=10)
                except: pass
                st.session_state.approval_pending = None
                # Actually execute optimizations
                from ui.panels.trace_board import _execute_optimizations
                changes = _execute_optimizations()
                # Update trace
                from datetime import datetime
                ts = datetime.now().isoformat()
                events = st.session_state.get("trace_events", [])
                events = [e for e in events if e["node"] not in ("execute", "report")]
                events.append({"node":"execute","event":"step_complete","ts":ts})
                events.append({"node":"report","event":"step_complete","ts":ts})
                st.session_state.trace_events = events
                st.session_state._reload_data = True
                feishu_url = st.session_state.get("_last_feishu_url", "")
                url_line = f"\n\n📄 [查看飞书报告]({feishu_url})" if feishu_url else "\n\n📄 优化报告已生成（配置 FEISHU_APP_ID 后自动同步飞书文档）"
                st.session_state.chat_messages.append({"role": "agent", "content": f"✅ 已确认，调价操作已执行！\n\n📊 共调整 {len(changes)} 项：\n" + "\n".join(f"• {c[0]} {c[1]}: {c[2]}" for c in changes) + url_line + "\n\n右侧仪表盘数据已更新。"})
                st.rerun()
        with cb:
            if st.button("✕ 取消", key="ap_no", use_container_width=True):
                try:
                    requests.post(f"http://localhost:8000/reject/{st.session_state.session_id}", timeout=10)
                except: pass
                st.session_state.approval_pending = None
                from datetime import datetime
                ts = datetime.now().isoformat()
                events = st.session_state.get("trace_events", [])
                events = [e for e in events if e["node"] not in ("execute", "report")]
                events.append({"node":"execute","event":"step_complete","ts":ts})
                events.append({"node":"report","event":"step_error","ts":ts})
                st.session_state.trace_events = events
                st.session_state.chat_messages.append({"role": "agent", "content": "✕ 操作已取消，计划保持原状。"})
                st.rerun()

    # ---- Parameter Confirmation Card ----
    if st.session_state.get("show_param_card", False):
        biz_scene = st.session_state.get("_biz_scene", "ad_placement")
        if biz_scene == "content":
            _render_content_param_card()
        else:
            _render_optimize_param_card()

    # ---- Input ----
    st.markdown("<hr style='border-color:var(--border);margin:6px 12px;'>", unsafe_allow_html=True)
    ph_dict = {
        "ad_placement": "例如：检查最近7天抖音Top5，ROI<2.5的计划，降价15%…",
        "content": "分析高点击视频共性，生成带货脚本…",
        "ecommerce": "查库存+补货+发券+催单话术…",
        "data_analysis": "拉取多平台数据，按客户汇总排名…",
        "diagnosis": "排查计划为什么没量，自动恢复…",
    }
    ph = ph_dict.get(st.session_state.current_scene, "描述你的需求，系统将自动推荐参数…")
    ci, cb2 = st.columns([5, 1])
    with ci:
        inp = st.text_input("msg", key="chat_input", placeholder=ph, label_visibility="collapsed")
    with cb2:
        if st.button("发送 ➤", key="send_btn", use_container_width=True):
            if inp.strip():
                txt = inp.strip()
                st.session_state.chat_messages.append({"role": "user", "content": txt})

                # Intent classification
                is_biz = _is_business_intent(txt)
                is_conv = _is_conversational_intent(txt)

                if is_conv and not is_biz:
                    st.session_state.show_param_card = False
                    st.session_state.chat_messages.append({
                        "role": "agent",
                        "content": _get_conversational_reply(txt),
                    })
                elif is_biz:
                    # Determine which business scene
                    scene = _detect_biz_scene(txt)
                    st.session_state._biz_scene = scene
                    st.session_state.show_param_card = True
                    # Auto-switch to the correct tab
                    scene_tab_map = {
                        "ad_placement": ("optimize", "ad_placement", "投放优化"),
                        "content": ("content", "content", "内容生产"),
                        "ecommerce": ("ecommerce", "ecommerce", "电商场控"),
                        "data_analysis": ("data_analysis", "data_analysis", "数据分析"),
                        "diagnosis": ("diagnosis", "diagnosis", "故障诊断"),
                    }
                    tab, cur_scene, display = scene_tab_map.get(scene, ("optimize", "ad_placement", "投放优化"))
                    st.session_state.active_tab = tab
                    st.session_state.current_scene = cur_scene
                    st.session_state.current_scene_display = display

                    if scene == "content":
                        st.session_state.chat_messages.append({
                            "role": "agent",
                            "content": "🤖 收到！我判断这是一个**内容生产**需求。\n\n已自动切换到内容生产模式。下方是参数面板，你可以调整平台、时间范围、模板等参数，然后点击「🚀 开始生产」执行。"
                        })
                    elif scene == "ad_placement":
                        st.session_state.chat_messages.append({
                            "role": "agent",
                            "content": f"🤖 收到！我判断这是一个**投放优化**需求。\n\n已自动切换到投放优化模式。下方是优化参数面板，你可以自由调整各平台的查询范围、ROI 阈值和调整比例，然后点击「🚀 开始优化」执行。\n\n💡 **提示**：你也可以在输入框直接描述更具体的条件，比如「只查抖音」或「ROI<1.5 才调」。"
                        })
                    else:
                        st.session_state.chat_messages.append({
                            "role": "agent",
                            "content": f"🤖 收到！我判断这是一个**{display}**需求。\n\n已自动切换到对应模式。请在参数面板中调整设置后执行。"
                        })
                else:
                    # Neither conversational nor business — ask for clarification
                    st.session_state.show_param_card = False
                    st.session_state.chat_messages.append({
                        "role": "agent",
                        "content": "🤔 抱歉，我不太确定你的需求。\n\n我可以帮你的方面包括：\n• 📊 **广告投放分析**：检查 ROI、自动调价、优化预算\n• 🎬 **内容生产**：分析素材表现、生成带货脚本\n• 🛒 **直播场控**：查库存、发优惠券、催单话术\n• 📈 **数据分析**：跨平台报表、客户排名、预算建议\n• 🔧 **故障诊断**：排查计划异常、自动恢复\n\n请更具体地描述你的需求，比如「检查最近7天抖音消耗Top5中ROI<2的计划」。",
                    })
                st.rerun()


# ====== Intent classification helpers ======

def _is_conversational_intent(text: str) -> bool:
    """Check if input is casual conversation or question, NOT a command."""
    t = text.lower()

    # Question patterns (even with business words, these are conversational)
    question_patterns = [
        "你能", "你会", "你可以", "你是什么", "你是谁", "你叫什么",
        "怎么", "如何", "能帮我", "能干嘛", "能做什么",
        "有什么", "介绍一下", "什么是", "是什么意思", "为什么",
        "怎样", "哪里", "哪个", "什么",
    ]
    if any(kw in t for kw in question_patterns):
        return True

    # Pure greetings/small talk
    conv = [
        "你好", "嗨", "hello", "hi", "hey", "早上好", "下午好", "晚上好",
        "谢谢", "感谢", "再见", "拜拜",
        "帮助", "help", "你的功能", "功能介绍",
        "你的名字", "你是ai", "你是人工", "谁开发的", "谁做的",
        "天气", "笑话", "讲个故事", "今天几号", "现在几点",
        "在吗", "在不在", "测试", "test", "ok", "知道了",
    ]
    return any(kw in t for kw in conv)


def _is_business_intent(text: str) -> bool:
    """Check if input is a clear business command (action + target)."""
    t = text.lower()

    # Action verbs that indicate a command/request
    action_verbs = [
        "检查", "拉取", "查询", "优化", "帮我看看", "帮我查", "帮我",
        "分析", "排查", "诊断", "生成", "创建", "调整", "修改",
        "降价", "提价", "调价", "执行", "运行",
    ]
    # Business targets
    biz_targets = [
        "roi", "计划", "消耗", "投放", "广告", "出价", "预算",
        "素材", "脚本", "视频", "ctr", "点击率", "转化", "cvr",
        "直播", "库存", "优惠券", "场控", "补货",
        "报表", "客户", "排名", "数据", "ppt",
        "故障", "没量", "审核", "拒绝",
    ]

    has_action = any(kw in t for kw in action_verbs)
    has_target = any(kw in t for kw in biz_targets)

    # Must have BOTH action verb AND business target to be a business request
    # Single keywords without command structure do NOT trigger business mode
    return has_action and has_target and len(t) > 3


def _detect_biz_scene(text: str) -> str:
    """Detect which business scene the input belongs to."""
    t = text.lower()
    if any(kw in t for kw in ["素材","脚本","视频","内容","混剪","ctr","点击率","创意"]):
        return "content"
    if any(kw in t for kw in ["直播","库存","优惠券","场控","补货","催单"]):
        return "ecommerce"
    if any(kw in t for kw in ["报表","预算","客户","ppt","排名","汇总"]):
        return "data_analysis"
    if any(kw in t for kw in ["排查","诊断","故障","没量","恢复","审核","拒绝"]):
        return "diagnosis"
    return "ad_placement"


def _render_optimize_param_card():
    """Render the optimization parameter card."""
    params = st.session_state.optim_params
    st.markdown("""<div style="font-size:12px;font-weight:600;color:var(--text-secondary);padding:8px 12px 4px 12px;">⚙️ 优化参数 — 可调整后执行</div>""", unsafe_allow_html=True)
    with st.container():
        p1, p2 = st.columns(2)
        with p1:
            platforms = st.multiselect("投放平台", ["douyin", "tencent", "kuaishou", "xiaohongshu"],
                                       default=params.get("platforms", ["douyin", "tencent"]),
                                       format_func=lambda x: {"douyin":"抖音","tencent":"腾讯","kuaishou":"快手","xiaohongshu":"小红书"}.get(x,x))
            days = st.slider("回溯天数", 1, 30, params.get("days", 7))
            top_n = st.slider("拉取计划数 (每平台)", 1, 20, params.get("top_n", 5))
        with p2:
            roi_threshold = st.slider("ROI 健康线", 0.5, 5.0, params.get("roi_threshold", 2.0), 0.1)
            bid_adj = st.slider("出价调整 (%)", -50, 50, params.get("bid_adjust_pct", -10))
            budget_adj = st.slider("预算调整 (%)", -50, 50, params.get("budget_adjust_pct", -20))
        risk_confirm = st.select_slider("需确认的风险等级", ["low","medium","high"],
                                        value=params.get("risk_confirm", "medium"),
                                        help="低于此等级的操作自动执行，达到此等级需人工确认")
        c1, c2, c3 = st.columns([1.5, 1, 3])
        with c1:
            if st.button("🚀 开始优化", key="btn_run_optimize", use_container_width=True, type="primary"):
                st.session_state.optim_params = {
                    "platforms": platforms, "days": days, "top_n": top_n,
                    "roi_threshold": roi_threshold, "bid_adjust_pct": bid_adj,
                    "budget_adjust_pct": budget_adj, "risk_confirm": risk_confirm,
                }
                st.session_state.show_param_card = False
                st.session_state._reload_data = True
                st.session_state.trace_events = []
                st.session_state._trace_animating = True
                st.session_state._trace_step = 0
                st.session_state.chat_messages.append({"role": "agent", "content": f"🚀 开始优化！参数：{len(platforms)}平台/{days}天/Top{top_n}/ROI<{roi_threshold}/出价{bid_adj:+d}%"})
                st.rerun()
        with c2:
            if st.button("↩ 取消", key="btn_cancel_optimize", use_container_width=True):
                st.session_state.show_param_card = False
                st.session_state.chat_messages.append({"role": "agent", "content": "已取消。你可以重新输入指令或调整参数。"})
                st.rerun()
        st.caption(f"📋 计划查询 {len(platforms)} 个平台 · 各拉取 Top{top_n} · {days}天内 · ROI<{roi_threshold} 触发告警")


def _render_content_param_card():
    """Render the content production parameter card."""
    params = st.session_state.content_params
    st.markdown("""<div style="font-size:12px;font-weight:600;color:var(--text-secondary);padding:8px 12px 4px 12px;">✏️ 内容生产参数 — 可调整后执行</div>""", unsafe_allow_html=True)
    with st.container():
        p1, p2 = st.columns(2)
        with p1:
            platform = st.selectbox("投放平台", ["douyin", "tencent"],
                                     index=0 if params.get("platform","douyin")=="douyin" else 1,
                                     format_func=lambda x: "抖音" if x=="douyin" else "腾讯广告")
            date = st.selectbox("数据日期", ["yesterday", "last_3d", "last_7d"],
                                index=["yesterday","last_3d","last_7d"].index(params.get("date","yesterday")),
                                format_func=lambda x: {"yesterday":"昨日","last_3d":"近3天","last_7d":"近7天"}.get(x,x))
            top_n = st.slider("高点击素材数", 1, 10, params.get("top_n", 3))
        with p2:
            worst_n = st.slider("低点击素材数", 1, 10, params.get("worst_n", 3))
            template = st.selectbox("脚本模板", ["summer_promo", "flash_sale", "product_review"],
                                    index=["summer_promo","flash_sale","product_review"].index(params.get("template_id","summer_promo")),
                                    format_func=lambda x: {"summer_promo":"夏季促销","flash_sale":"闪购秒杀","product_review":"产品测评"}.get(x,x))
            auto_pub = st.checkbox("自动发布到飞书", value=params.get("auto_publish", True))
        c1, c2, c3 = st.columns([1.5, 1, 3])
        with c1:
            if st.button("🚀 开始生产", key="btn_run_content", use_container_width=True, type="primary"):
                st.session_state.content_params = {
                    "platform": platform, "date": date, "top_n": top_n,
                    "worst_n": worst_n, "template_id": template, "auto_publish": auto_pub,
                }
                st.session_state.show_param_card = False
                st.session_state._biz_scene = "content"

                # Generate scripts + publish to Feishu (with retry for mock failures)
                from tools.mock_functions import generate_script
                scripts = []
                for i in range(top_n):
                    ok = False
                    for attempt in range(5):
                        try:
                            s = generate_script(template_id=template, params={"product_name": f"爆款商品-{chr(65+i)}"})
                            scripts.append(s)
                            ok = True
                            break
                        except Exception:
                            pass
                    if not ok:
                        scripts.append(f"[脚本{chr(65+i)}生成失败]")

                from tools.feishu_client import publish_scripts
                try:
                    results = publish_scripts(scripts, platform, template)
                    urls = [r.get("url", "") for r in results]
                    mock = results[0].get("mock", True) if results else True
                    via = "真实飞书文档" if not mock else "Demo模拟"
                    url_str = "\n".join(f"📄 脚本{i+1}: {u}" for i, u in enumerate(urls))
                    st.session_state.chat_messages.append({
                        "role": "agent",
                        "content": f"✏️ 开始内容生产！{platform}/{date}/Top{top_n}/模板{template}\n\n✅ 已生成 {len(scripts)} 条脚本并发布到{via}：\n\n{url_str}"
                    })
                except Exception as e:
                    err = str(e)[:200]
                    # Mock errors are not real Feishu errors — just retry
                    if "暂不可用" in err or "请稍后" in err:
                        st.session_state.chat_messages.append({
                            "role": "agent",
                            "content": f"✏️ 开始内容生产！{platform}/{date}/Top{top_n}/模板{template}\n\n⚠️ 网络波动，请重试一次（这只是 Demo 的随机模拟，不是真实错误）"
                        })
                    else:
                        st.session_state.chat_messages.append({
                            "role": "agent",
                            "content": f"✏️ 开始内容生产！{platform}/{date}/Top{top_n}/模板{template}\n\n⚠️ 飞书发布失败：{err}"
                        })

                # Start animation
                st.session_state.trace_events = []
                st.session_state._trace_animating = True
                st.session_state._trace_step = 0
                st.rerun()
        with c2:
            if st.button("↩ 取消", key="btn_cancel_content", use_container_width=True):
                st.session_state.show_param_card = False
                st.session_state.chat_messages.append({"role": "agent", "content": "已取消。"})
                st.rerun()
        st.caption(f"📋 {platform} · {date} · 高CTR Top{top_n} + 低CTR Bot{worst_n} · 模板{template}")


def _get_conversational_reply(text: str) -> str:
    t = text.lower()
    if any(kw in t for kw in ["你好", "hello", "hi", "嗨", "早上好", "下午好", "晚上好", "在吗", "在不在"]):
        return "👋 你好！我是 **AdCockpit AI 优化师**，一个数字营销对话驾驶舱。\n\n有什么我可以帮你的吗？你可以直接描述需求，比如：\n• 检查抖音和腾讯广告的投放效果\n• 分析素材的点击率表现\n• 查看直播间的库存和转化情况"
    if any(kw in t for kw in ["你是谁", "你是什么", "你叫什么", "你是"]):
        return "我是 **AdCockpit**，一个 AI 数字营销对话驾驶舱。\n\n我背后有 **8 个 AI Agent** 协作工作，覆盖广告投放优化、内容生产、电商场控和数据分析四大场景。你只需要用自然语言告诉我需求，我会自动拆解任务并执行。"
    if any(kw in t for kw in ["能做什么", "有什么能力", "能干嘛", "你的功能", "功能介绍", "帮助", "help", "怎么用", "如何使用"]):
        return "我可以帮你完成以下工作：\n\n📊 **广告投放优化**：检查多平台 ROI、自动调价/降预算、异常告警\n🎬 **内容生产**：分析素材表现、提取爆款特征、AI 生成带货脚本\n🛒 **直播场控**：实时库存监控、自动补货、发放优惠券、生成催单话术\n📈 **数据分析**：跨平台聚合报表、客户排名、预算建议、PPT 提纲\n🔧 **故障诊断**：排查计划异常、自动根因分析、自动恢复\n\n你只需要在输入框描述需求，比如「检查最近7天抖音Top5计划的ROI」。"
    if any(kw in t for kw in ["谢谢", "感谢"]):
        return "不客气！有需要随时找我。😊"
    if any(kw in t for kw in ["再见", "拜拜"]):
        return "再见！祝你投放效果越来越好 🚀"
    return f"你好！我收到了你的消息，但不太确定具体需要什么帮助。\n\n我是 AdCockpit AI 优化师，可以帮你做广告投放分析、内容生产、直播场控和数据分析。请更具体地描述你的需求吧！"
