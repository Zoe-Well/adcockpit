"""Center Trace Board — flow tracker + step cards, business-friendly."""
import streamlit as st


def render_trace_board():
    scene = st.session_state.current_scene
    trace = st.session_state.get("trace_events", [])
    has_run = len(trace) > 0  # True after user clicked "查询"

    # Build status map from trace events
    status_map = {}
    for e in trace:
        node = e.get("node", "")
        evt = e.get("event", "")
        if evt == "step_complete":
            status_map[node] = "done"
        elif evt == "step_start":
            status_map.setdefault(node, "running")
        elif evt == "approval_required":
            status_map["execute"] = "waiting"
        elif evt == "step_error":
            status_map[node] = "failed"

    # ---- Flow Tracker (horizontal visual pipeline) ----
    flow_configs = {
        "ad_placement":  ["任务规划","数据拉取","数据拉取","智能分析","策略建议","执行操作","报告生成"],
        "content":       ["任务规划","数据拉取","智能分析","内容生产","执行操作","报告生成"],
        "ecommerce":     ["任务规划","数据拉取","智能分析","电商运营","执行操作","报告生成"],
        "data_analysis": ["任务规划","数据拉取","数据拉取","数据拉取","智能分析","策略建议","报告生成"],
        "diagnosis":     ["任务规划","数据拉取","智能分析","策略建议","执行操作","报告生成"],
    }
    flow_nodes = flow_configs.get(scene, flow_configs["ad_placement"])
    # Map flow index to internal node key
    flow_keys = {
        "ad_placement":  ["supervisor","data","data_2","analysis","strategy","execute","report"],
        "content":       ["supervisor","data","analysis","content","execute","report"],
        "ecommerce":     ["supervisor","data","analysis","ecommerce","execute","report"],
        "data_analysis": ["supervisor","data","data_2","data_3","analysis","strategy","report"],
        "diagnosis":     ["supervisor","data","analysis","strategy","execute","report"],
    }
    keys = flow_keys.get(scene, flow_keys["ad_placement"])

    # Render flow tracker HTML
    flow_html = '<div style="display:flex;align-items:center;justify-content:center;padding:10px 8px;gap:0;margin:0 8px 6px 8px;">'
    for i, label in enumerate(flow_nodes):
        key = keys[i] if i < len(keys) else ""
        sts = status_map.get(key, None)  # None = not started
        if sts == "done":
            dot = '<span style="display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:50%;background:var(--success);color:#000;font-size:10px;font-weight:700;">✓</span>'
            text_color = "var(--success)"
        elif sts == "running":
            dot = '<span style="display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:50%;background:var(--accent);color:#fff;font-size:12px;" class="spin">⟳</span>'
            text_color = "var(--accent)"
        elif sts == "waiting":
            dot = '<span style="display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:50%;background:var(--warning);color:#000;font-size:10px;font-weight:700;">!</span>'
            text_color = "var(--warning)"
        elif sts == "failed":
            dot = '<span style="display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:50%;background:var(--danger);color:#fff;font-size:10px;font-weight:700;">✕</span>'
            text_color = "var(--danger)"
        else:
            # Not started — neutral
            dot = '<span style="display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:50%;background:var(--border);color:var(--text-muted);font-size:10px;">—</span>'
            text_color = "var(--text-muted)"

        # Connector line between nodes
        if i > 0:
            prev_key = keys[i-1] if i-1 < len(keys) else ""
            prev_sts = status_map.get(prev_key, None)
            line_color = "var(--success)" if prev_sts == "done" else "var(--border)"
            flow_html += f'<div style="flex:0 0 auto;width:16px;height:2px;background:{line_color};margin:0 1px;"></div>'

        flow_html += f'<div style="display:flex;flex-direction:column;align-items:center;gap:3px;flex:0 0 auto;">{dot}<span style="font-size:9px;color:{text_color};white-space:nowrap;">{label}</span></div>'

    flow_html += '</div>'
    st.markdown(flow_html, unsafe_allow_html=True)

    # ---- Step Cards ----
    steps = _get_steps_for_scene(scene)
    icons = {"done":"✅","running":"🔄","waiting":"⏸️","failed":"❌","pending":"⏳"}
    icm = {"done":"done","running":"running","waiting":"waiting","failed":"failed","pending":"pending"}

    active_node = st.session_state.get("_active_node", None)
    typing_progress = st.session_state.get("_typing_progress", 0.0)

    for step in steps:
        node = step.get("node","")
        if has_run:
            sts = status_map.get(node, "pending")
        else:
            sts = "pending"

        # Typing effect: partial text for active node, full for done, none for pending
        full_desc = step.get("desc","")
        full_result = step.get("result","")
        if sts in ("done", "waiting") or (active_node and node != active_node and sts == "done"):
            desc = full_desc
            result_text = full_result
        elif node == active_node and typing_progress > 0:
            # Show partial text based on typing progress
            char_count = max(10, int(len(full_desc) * min(typing_progress * 1.5, 1.0)))
            desc = full_desc[:char_count] + ("▌" if typing_progress < 0.8 else "")
            result_text = ""
        elif sts == "running" and node != active_node:
            desc = full_desc[:20] + "..."
            result_text = ""
        else:
            desc = ""
            result_text = ""

        icon, icon_cls = icons.get(sts,"⏳"), icm.get(sts,"pending")
        spin = 'class="spin"' if sts == "running" else ""

        result_html = ""
        if result_text:
            result_html = f'<div style="margin-top:6px;padding:6px 8px;background:var(--bg-primary);border-radius:4px;font-size:11px;color:var(--text-secondary);">📌 {result_text}</div>'

        st.markdown(f"""
        <div class="step-card status-{sts}">
          <div class="step-icon {icon_cls}"><span {spin}>{icon}</span></div>
          <div class="step-body">
            <div class="step-title">{step["title"]}<span style="font-size:11px;color:var(--text-muted);margin-left:8px;">{step.get("time","")}</span></div>
            <div class="step-desc">{desc}</div>
            {result_html}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Inline confirm/reject buttons for waiting execute step
        if sts == "waiting" and step.get("node") == "execute":
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                if st.button("✅ 确认执行", key="tr_approve", use_container_width=True, type="primary"):
                    from datetime import datetime
                    # Actually execute the optimization actions
                    _execute_optimizations()
                    ts = datetime.now().isoformat()
                    events = st.session_state.get("trace_events", [])
                    events = [e for e in events if e["node"] not in ("execute", "report")]
                    events.append({"node":"execute","event":"step_complete","ts":ts})
                    events.append({"node":"report","event":"step_complete","ts":ts})
                    st.session_state.trace_events = events
                    st.session_state.approval_pending = None
                    st.session_state._reload_data = True  # refresh dashboard
                    st.rerun()
            with c2:
                if st.button("✕ 取消", key="tr_reject", use_container_width=True):
                    from datetime import datetime
                    ts = datetime.now().isoformat()
                    events = st.session_state.get("trace_events", [])
                    events = [e for e in events if e["node"] not in ("execute", "report")]
                    events.append({"node":"execute","event":"step_complete","ts":ts})
                    events.append({"node":"report","event":"step_error","ts":ts})
                    st.session_state.trace_events = events
                    st.session_state.approval_pending = None
                    st.rerun()

    # Hint when no action taken yet
    if not has_run:
        st.caption("💡 在左侧对话面板输入需求 → 调整参数 → 点击「🚀 开始优化」")


def _get_steps_for_scene(scene: str) -> list:
    p = st.session_state.get("optim_params", {})
    platforms = p.get("platforms", ["douyin", "tencent"])
    days = p.get("days", 7)
    top_n = p.get("top_n", 5)
    threshold = p.get("roi_threshold", 2.0)
    bid_adj = p.get("bid_adjust_pct", -10)
    budget_adj = p.get("budget_adjust_pct", -20)
    risk = p.get("risk_confirm", "medium")
    plat_names = {"douyin":"抖音","tencent":"腾讯广告","kuaishou":"快手","xiaohongshu":"小红书"}
    plat_list = "、".join(plat_names.get(x,x) for x in platforms)

    if scene == "ad_placement":
        steps = [
            {"node":"supervisor","title":"任务规划 — 理解需求","desc":f"识别到您想优化广告投放效果。已拆解为 6 个步骤，{plat_list}数据将并行拉取以节省时间。","result":None,"time":""},
        ]
        # Dynamic data steps per platform
        for i, plat in enumerate(platforms[:3]):  # Max 3 platforms shown
            name = plat_names.get(plat, plat)
            node_key = f"data_{i}" if i > 0 else "data"
            steps.append({
                "node": node_key,
                "title": f"数据拉取 — {name}平台",
                "desc": f"已获取{name}近 {days} 天消耗最高的 {top_n} 条广告计划。涵盖消耗金额、ROI、出价等关键指标。",
                "result": f"共 {top_n} 条计划 · 数据拉取完成",
                "time": "",
            })
        steps += [
            {"node":"analysis","title":"智能分析 — 异常检测","desc":f"已对全部计划逐一分析。筛选 ROI 低于 {threshold} 健康线的计划，标注严重程度（严重/偏高/关注），其余表现正常的计划标记为健康。","result":f"⚠️ ROI<{threshold} 的计划已高亮 · 可在右侧仪表盘查看详情","time":""},
            {"node":"strategy","title":"策略建议 — 生成优化方案","desc":f"针对不达标计划生成优化建议：ROI 偏低的计划建议降价 {abs(bid_adj)}%；ROI 严重偏低的额外建议削减预算 {abs(budget_adj)}%。具体调整由 AI 结合历史数据和当前出价综合计算。","result":f"降价 {abs(bid_adj)}% + 必要时降预算 {abs(budget_adj)}% · 预计可改善整体 ROI","time":""},
            {"node":"execute","title":"执行操作 — 等待您的确认","desc":f"风险等级 ≥ {risk} 的操作需要您确认后执行。低于此等级的操作将自动执行。请查看左侧确认卡片，点击「确认」或「取消」。","result":f"🛑 等待审批 · 风险阈值: {risk}","time":""},
            {"node":"report","title":"报告生成 — 等待上游完成","desc":"确认执行后将自动汇总本次优化的完整报告，包括操作记录、节省金额预估和后续监控建议。","result":None,"time":""},
        ]
        return steps
    elif scene == "content":
        return [
            {"node":"supervisor","title":"任务规划 — 理解需求","desc":"识别到您想基于投放数据优化素材内容。已拆解为 5 个步骤：拉取素材 → 分析爆款特征 → 生成新脚本 → 发布到飞书 → 输出报告。","result":None,"time":""},
            {"node":"data","title":"数据拉取 — 抖音素材","desc":"已获取昨日抖音上表现最好和最差的素材各 3 条。高点击率素材集中在 4.9%-6.8%，低点击率素材仅为 1.2%-1.8%。","result":"高 CTR 素材 3 条（平均 5.7%）· 低 CTR 素材 3 条（平均 1.5%）","time":""},
            {"node":"analysis","title":"智能分析 — 爆款特征提取","desc":"AI 自动分析了高点击视频的共性：① 开头 3 秒内出现价格信息或产品特写 ② 主播语速偏快、有紧迫感 ③ 背景音乐为当前热门卡点曲目 ④ 视频时长控制在 15-30 秒。","result":"4 个爆款特征 · 低点击视频普遍开头平淡、语速过慢","time":""},
            {"node":"content","title":"内容生产 — 脚本创作","desc":"基于爆款特征，使用「夏季促销」模板生成了 3 条带货口播脚本。每条脚本包含开场钩子、价格锚点、产品卖点和下单引导，风格匹配抖音快节奏带货。","result":"3 条脚本已生成 · 可在右侧仪表盘预览和微调","time":""},
            {"node":"execute","title":"执行操作 — 发布到飞书","desc":"已自动将 3 条脚本上传到飞书内容库，供团队查看和使用。此类内容发布为低风险操作，无需额外审批。","result":"✅ 全部上传成功 · 3 个飞书文档链接已生成","time":""},
            {"node":"report","title":"报告生成 — 完成","desc":"内容生产流程已全部完成。右侧仪表盘展示了脚本预览区和修改入口，您可以直接编辑后重新发布。","result":"✅ 流程完成 · 爆款模板已保存，下次可直接复用","time":""},
        ]
    elif scene == "ecommerce":
        return [
            {"node":"supervisor","title":"任务规划 — 理解需求","desc":"识别到直播间的紧急运营需求，已标记为高优先级。拆解为 5 个步骤：查库存 → 分析缺口 → 制定策略 → 执行操作 → 汇总报告。","result":None,"time":""},
            {"node":"data","title":"数据拉取 — 库存与直播指标","desc":"已查询商品 A 的库存和直播间实时数据。商品 A 当前库存仅 32 件（低于 50 件警戒线），直播间在线 2,000 人但转化率较昨日下降 0.5%。","result":"⚠️ 库存告急：仅剩 32 件 · 直播间 2,000 人在线 · 转化率下滑","time":""},
            {"node":"analysis","title":"智能分析 — 库存缺口评估","desc":"商品 A 库存严重不足，若不补货预计 15 分钟内售罄，将造成约 ¥3,200 的潜在损失。同时转化率下降可通过优惠券刺激挽回。","result":"库存缺口 168 件 · 预计潜在损失 ¥3,200 · 建议立即补货 200 件","time":""},
            {"node":"ecommerce","title":"电商运营 — 策略制定","desc":"制定了 3 项操作：① 追加库存 200 件（需确认）② 发放 10 元无门槛优惠券 500 张 ③ 生成主播催单话术推送到中控屏。","result":"补货+200 · 发券-10元×500张 · 催单话术已生成","time":""},
            {"node":"execute","title":"执行操作 — 补货+发券+推话术","desc":"优惠券已自动发放到直播间评论区，催单话术已推送至主播中控屏。库存补货需要您确认后执行（涉及 ERP 系统操作）。","result":"✅ 优惠券已发放 · ✅ 话术已推送 · 🛑 补货等待确认","time":""},
            {"node":"report","title":"报告生成 — 运营汇总","desc":"本次场控预计带来 GMV 增量约 ¥5,000。操作记录已同步到 ERP 系统，可在右侧仪表盘查看优惠券领取进度。","result":None,"time":""},
        ]
    elif scene == "data_analysis":
        return [
            {"node":"supervisor","title":"任务规划 — 理解需求","desc":"识别到您需要跨平台数据分析报告。拆解为 6 个步骤，抖音、腾讯、小红书三平台数据将同时拉取以提升效率。","result":None,"time":""},
            {"node":"data","title":"数据拉取 — 抖音平台报表","desc":"已拉取本月抖音平台的客户消耗、ROI、CPA 数据。覆盖 5 个客户，数据完整无缺失。","result":"5 个客户数据完整 · 总消耗 ¥108,000","time":""},
            {"node":"data_2","title":"数据拉取 — 腾讯广告报表","desc":"已拉取本月腾讯广告平台的客户数据。5 个客户的数据均已获取。","result":"5 个客户数据完整 · 总消耗 ¥77,000","time":""},
            {"node":"data_3","title":"数据拉取 — 小红书报表","desc":"已拉取本月小红书平台数据。部分客户的 CPA 字段暂未回传（平台数据延迟），已标注但不影响整体分析。","result":"⚠️ 部分 CPA 缺失（平台延迟）· 总消耗 ¥51,000 · 已降级处理","time":""},
            {"node":"analysis","title":"智能分析 — 客户维度排名","desc":"三平台数据按客户汇总后排名：🏆 回报率最高的前 3 名是客户C（ROI 3.2）、客户E（2.8）、客户B（2.2）；⚠️ 需关注的是客户A（1.5）和客户D（1.2）。","result":"Top3: 客户C/E/B · Bottom2: 客户A/D · 整体 ROI 2.14","time":""},
            {"node":"strategy","title":"策略建议 — 预算再分配","desc":"建议将低效客户的预算向高回报客户倾斜：客户A 削减 20% → 转移至客户C；客户D 削减 30% → 转移至客户E。预计整体 ROI 可提升 0.3。","result":"2 项预算调整建议 · 预计 ROI +0.3 · 无需审批，可直接参考","time":""},
            {"node":"report","title":"报告生成 — PPT 提纲","desc":"已自动生成 4 页 PPT 提纲：数据概览、客户排名图表、预算建议表格、下周行动计划。可在右侧仪表盘查看和复制使用。","result":"✅ PPT 提纲已生成 · 4 页 · 含图表 2 张 · 可直接用于客户提案","time":""},
        ]
    elif scene == "diagnosis":
        return [
            {"node":"supervisor","title":"任务规划 — 理解需求","desc":"识别到您需要排查广告计划异常。拆解为 5 个自动诊断步骤，将依次检查计划状态、定位根因并自动执行恢复操作。","result":None,"time":""},
            {"node":"data","title":"数据拉取 — 计划状态查询","desc":"已查询计划 12345 的完整状态。该计划目前处于「审核拒绝」状态，拒绝原因是：素材内容涉及虚假承诺。审核时间为今天上午 9:32。","result":"🔴 计划 12345 · 审核拒绝 · 原因：素材虚假承诺 · 已被拒 3 小时","time":""},
            {"node":"analysis","title":"智能分析 — 根因定位","desc":"已确认根因：素材内容触发平台审核规则。这是导致计划无消耗的直接原因。系统判定此问题可自动恢复——通过替换备用素材并重新提交审核。","result":"根因：审核拒绝 · 可自动恢复 · 建议：替换素材+重提审+通知负责人","time":""},
            {"node":"strategy","title":"策略建议 — 恢复方案","desc":"自动生成恢复方案：① 将违规素材替换为备用视频 backup_001 ② 重新提交平台审核 ③ 发送飞书通知给优化师小王，告知处理结果。","result":"3 项恢复操作 · 均为低风险，将自动执行","time":""},
            {"node":"execute","title":"执行操作 — 自动恢复","desc":"已自动完成素材替换、重新提交审核、并发送飞书通知给小王。计划 12345 现已进入审核队列，预计 30 分钟内恢复投放。","result":"✅ 素材已替换 ✅ 已重新提交审核 ✅ 飞书通知已发送给小王","time":""},
            {"node":"report","title":"报告生成 — 诊断报告","desc":"故障诊断与恢复流程全部完成。从发现问题到自动恢复全程耗时不到 5 秒，无需人工干预。操作日志已完整记录，可随时追溯。","result":"✅ 自动恢复完成 · 计划已进入审核队列 · 全过程可追溯","time":""},
        ]
    return []


def _execute_optimizations():
    """Actually call mock functions to update campaign bids and budgets."""
    from tools.mock_data import DOUYIN_PLANS, TENCENT_PLANS

    p = st.session_state.get("optim_params", {})
    threshold = p.get("roi_threshold", 2.0)
    bid_pct = 1 + p.get("bid_adjust_pct", -10) / 100.0  # e.g. 0.9 for -10%
    budget_pct = 1 + p.get("budget_adjust_pct", -20) / 100.0  # e.g. 0.8 for -20%

    all_plans = list(DOUYIN_PLANS) + list(TENCENT_PLANS)
    changes = []

    for plan in all_plans:
        if plan["roi"] < threshold and plan["roi"] > 0:
            old_bid = plan.get("bid", 0)
            old_budget = plan.get("budget", 0)
            plan["bid"] = round(old_bid * bid_pct, 1)
            changes.append((plan["id"], "出价", f"¥{old_bid}→¥{plan['bid']}"))

            # Also cut budget for severely underperforming plans
            if plan["roi"] < 1.5 and old_budget > 0:
                plan["budget"] = round(old_budget * budget_pct)
                changes.append((plan["id"], "预算", f"¥{old_budget}→¥{plan['budget']}"))

    # Reload campaign data to reflect changes
    st.session_state._reload_data = True

    # Publish report to Feishu
    try:
        from tools.feishu_client import publish_optimization_report
        rows = [
            ("分析计划数", f"{len(all_plans)} 条"),
            ("不达标计划", f"{len(changes)} 项调整"),
            ("预计节省", "¥5,640/天 (15%)"),
            ("ROI 提升", "预计 +12%"),
        ]
        action_strs = [f"{c[0]}：{c[1]} {c[2]}" for c in changes]
        result = publish_optimization_report(rows, action_strs)
        st.session_state._last_feishu_url = result.get("url", "")
    except Exception:
        st.session_state._last_feishu_url = ""

    return changes
