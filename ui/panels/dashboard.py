"""Right Dashboard — scene-adaptive via active_tab, reads campaign_data."""
import streamlit as st


# ====== Helpers ======

def _metric_grid(cards: list) -> str:
    html = '<div class="metrics-row">'
    for c in cards:
        hl = " metric-hl" if c.get("highlight") else ""
        trend = c.get("trend", "")
        sub_cls = f"metric-sub {trend}" if trend else "metric-sub"
        html += f'<div class="metric-card{hl}"><div class="metric-label">{c["label"]}</div><div class="metric-value">{c["value"]}</div><div class="{sub_cls}">{c.get("sub","")}</div></div>'
    html += '</div>'
    return html


def _chart(title: str, bars: list, threshold: float = 2.0, max_val: float = 4.0) -> str:
    parts = []
    for b in bars:
        h = max(6, (b["value"] / max_val) * 110)
        cls = "chart-bar low" if b.get("highlight") else "chart-bar"
        parts.append(f'<div class="{cls}" style="height:{h:.0f}px;"><span class="bar-val">{b["value"]:.1f}</span><span class="bar-label">{b["label"]}</span></div>')
    tb = (threshold / max_val) * 110 + 24
    return f'''<div class="chart-card"><div class="chart-title">{title}</div><div class="chart-placeholder" style="position:relative;">{"".join(parts)}<div style="position:absolute;bottom:{tb:.0f}px;left:0;right:0;border-top:1px dashed var(--danger);z-index:5;" title="ROI={threshold}"></div></div></div>'''


def _alerts(alerts: list) -> str:
    html = '<div class="alert-list">'
    for a in alerts:
        cls = "alert-item" if a.get("border") == "danger" else "alert-item warn"
        html += f'<div class="{cls}"><span style="font-size:18px;">{a["icon"]}</span><div><div class="alert-title">{a["title"]}</div><div class="alert-detail">{a["detail"]}</div></div></div>'
    html += '</div>'
    return html


def _report(title: str, rows: list) -> str:
    r = ""
    for label, value in rows:
        clr = ""
        if "条" in str(value) and "不达标" in label: clr = 'style="color:var(--danger);"'
        elif "¥" in str(value) or "→" in str(value): clr = 'style="color:var(--success);"'
        r += f'<div class="rs-row"><span>{label}</span><span {clr}>{value}</span></div>'
    return f'<div class="report-summary"><div class="rs-title">{title}</div>{r}</div>'


def _threshold() -> float:
    """Get current ROI threshold from user params."""
    return st.session_state.get("optim_params", {}).get("roi_threshold", 2.0)


def _get_data() -> dict:
    cd = st.session_state.get("campaign_data")
    if cd: return cd
    return {"all_plans":[],"total_cost":37600,"avg_roi":1.87,"avg_cpa":38.5,"avg_ctr":3.8,"avg_cvr":4.2,"active_count":10,"below_threshold":[]}


# ====== Campaign Table ======
TABLE_COLS = [("ID","id",60),("名称","name",120),("平台","platform",50),("消耗¥","cost",70),("ROI","roi",55),("CPA¥","cpa",55),("CTR%","ctr_pct",50),("CVR%","cvr_pct",50),("出价¥","bid",55),("预算¥","budget",65),("状态","status",55)]

def _norm(plans):
    out=[]
    for p in plans:
        out.append({"id":p["id"],"name":p.get("name",p["id"]),"platform":"抖音" if p.get("_platform")=="douyin" else "腾讯","cost":p.get("cost",0),"roi":p.get("roi",0),"cpa":p.get("cpa",0),"ctr_pct":round(p.get("ctr",0)*100,1),"cvr_pct":round(p.get("cvr",0)*100,1),"bid":p.get("bid",0),"budget":p.get("budget",0),"status":p.get("status","active")})
    return out

def _render_table(all_plans):
    plans=_norm(all_plans)
    for k in ["campaign_sort","campaign_sort_asc","campaign_page"]:
        if k not in st.session_state: st.session_state[k]="roi" if k=="campaign_sort" else (True if k=="campaign_sort_asc" else 0)
    sk,sa=st.session_state.campaign_sort,st.session_state.campaign_sort_asc
    if sk in ("cost","cpa","ctr_pct","cvr_pct","bid","budget"): plans.sort(key=lambda x:x.get(sk,0),reverse=not sa)
    elif sk=="roi": plans.sort(key=lambda x:x["roi"],reverse=not sa)
    else: plans.sort(key=lambda x:str(x.get(sk,"")),reverse=sa)
    ps,tp=5,max(1,(len(plans)+4)//5)
    pg=min(st.session_state.campaign_page,tp-1)
    s,e=pg*ps,pg*ps+ps
    sc1,sc2,sc3=st.columns([2.5,1.5,2])
    with sc1: st.caption(f"📋 投放计划明细 · 第 {pg+1}/{tp} 页 · 共 {len(plans)} 条")
    with sc2:
        opts=["roi","cost","cpa","ctr_pct","cvr_pct","bid","budget","id","name","platform","status"]
        labs={"roi":"ROI","cost":"消耗","cpa":"CPA","ctr_pct":"CTR","cvr_pct":"CVR","bid":"出价","budget":"预算","id":"ID","name":"名称","platform":"平台","status":"状态"}
        ns=st.selectbox("排序",opts,index=opts.index(sk),format_func=lambda x:labs.get(x,x),key="sort_sel",label_visibility="collapsed")
        if ns!=sk: st.session_state.campaign_sort=ns; st.session_state.campaign_sort_asc=(ns not in ("cost","cpa","ctr_pct","cvr_pct","bid","budget")); st.rerun()
    with sc3:
        if st.button("↑ 升序" if sa else "↓ 降序",key="toggle_asc",use_container_width=True): st.session_state.campaign_sort_asc=not sa; st.rerun()
    html='<div style="margin:0 12px;font-size:10px;"><table style="width:100%;border-collapse:collapse;">'
    html+='<tr style="background:var(--bg-tertiary);color:var(--text-secondary);">'
    for label,key,w in TABLE_COLS:
        arrow=""
        if key==sk: arrow=" ▲" if sa else " ▼"
        html+=f'<th style="padding:5px 4px;text-align:left;width:{w}px;">{label}{arrow}</th>'
    html+='</tr>'
    for i,p in enumerate(plans[s:e]):
        thr=_threshold(); hl=p["roi"]<thr
        bg="var(--bg-secondary)" if i%2==0 else "var(--bg-primary)"
        rc="color:#ff6b6b;font-weight:700;" if hl else ""
        html+=f'<tr style="background:{bg};">'
        html+=f'<td style="padding:4px;">{p["id"]}</td><td style="padding:4px;">{p["name"][:12]}</td><td style="padding:4px;">{p["platform"]}</td>'
        html+=f'<td style="padding:4px;">¥{p["cost"]:,}</td><td style="padding:4px;{rc}">{p["roi"]:.2f}</td><td style="padding:4px;">¥{p["cpa"]}</td>'
        html+=f'<td style="padding:4px;">{p["ctr_pct"]}%</td><td style="padding:4px;">{p["cvr_pct"]}%</td>'
        html+=f'<td style="padding:4px;">¥{p["bid"]}</td><td style="padding:4px;">¥{p["budget"]:,}</td>'
        sc="var(--success)" if p["status"]=="active" else "var(--warning)"
        html+=f'<td style="padding:4px;color:{sc};">{p["status"]}</td></tr>'
    html+='</table></div>'
    st.markdown(html,unsafe_allow_html=True)
    pc1,pc2=st.columns([1,1])
    with pc1:
        if st.button("◀ 上一页",key="prev_pg",disabled=(pg==0),use_container_width=True): st.session_state.campaign_page=max(0,pg-1); st.rerun()
    with pc2:
        if st.button("下一页 ▶",key="next_pg",disabled=(pg>=tp-1),use_container_width=True): st.session_state.campaign_page=min(tp-1,pg+1); st.rerun()


# =========================================================================
def render_dashboard():
    tab = st.session_state.get("active_tab", "optimize")
    cd = _get_data()

    # ====== 优化 ======
    if tab == "optimize":
        all_plans = cd.get("all_plans", [])
        thr = _threshold()
        below = [p for p in all_plans if p["roi"] < thr] if all_plans else []
        avg_roi = cd["avg_roi"]
        r_hl = avg_roi < thr

        cards = [
            {"label":"⚠️ 整体 ROI","value":f"{avg_roi:.2f}","sub":f"{'⚠️' if r_hl else '✅'} 健康线 {thr}","trend":"down" if r_hl else "up","highlight":r_hl},
            {"label":"💰 总消耗","value":f"¥{cd['total_cost']:,}","sub":f"{cd['active_count']} 条计划","trend":"up"},
            {"label":"🎯 平均 CPA","value":f"¥{cd['avg_cpa']}","sub":"≈ 持平","trend":"warn"},
            {"label":"📋 活跃计划","value":str(cd["active_count"]),"sub":f"{len(below)} 条需关注","trend":"up"},
            {"label":"👆 平均 CTR","value":f"{cd['avg_ctr']:.1f}%","sub":"实时","trend":"up"},
            {"label":"🔄 平均 CVR","value":f"{cd['avg_cvr']:.1f}%","sub":"实时","trend":"down"},
        ]
        html = _metric_grid(cards)
        if all_plans:
            bars = [{"label":p["id"],"value":p["roi"],"highlight":p["roi"]<thr} for p in all_plans]
        else:
            bars = [{"label":"C001","value":1.5,"highlight":True},{"label":"C002","value":2.3},{"label":"C003","value":3.1}]
        html += _chart(f"📊 各计划 ROI 对比（阈值 {thr}）", bars, threshold=thr, max_val=4.0)

        if all_plans: _render_table(all_plans)

        if below:
            sev_map = {"critical":("🔴","danger"),"high":("🟠","danger"),"medium":("🟡","warn")}
            al = []
            for p in sorted(below, key=lambda x:x["roi"]):
                sev = "critical" if p["roi"]<thr*0.6 else ("high" if p["roi"]<thr*0.75 else "medium")
                icon,border = sev_map[sev]
                al.append({"icon":icon,"title":f"计划 {p['id']} — ROI {p['roi']}","detail":f"{p.get('_platform','?')} · 消耗 ¥{p['cost']:,} · ROI {p['roi']}","border":border})
            html += _alerts(al)

        rows = [
            ("分析计划数",f"{cd['active_count']} 条"),
            ("不达标计划",f"{len(below)} 条（ROI < {thr}）"),
            ("建议调价",f"{len(below)} 条降价 {abs(p.get('bid_adjust_pct',-10))}%"),
            ("建议降预算",f"{sum(1 for p in below if p['roi']<thr*0.75)} 条降 {abs(p.get('budget_adjust_pct',-20))}%"),
            ("预计节省","¥5,640/天（15%）"),
            ("ROI 预计提升",f"{avg_roi:.2f} → {min(avg_roi*1.12,5.0):.1f}"),
        ]
        html += _report("📋 优化报告预览", rows)
        st.markdown(html, unsafe_allow_html=True)

    # ====== 投放 ======
    elif tab == "create":
        st.markdown("""<div style="padding:12px;font-size:13px;color:var(--text-secondary);line-height:1.6;">
        📊 <b>投放管理中心</b><br><br>
        在此创建新的广告投放计划。点击「🚀 新建」表单填写平台、预算、出价和定向信息，提交后计划将加入投放列表。<br><br>
        💡 <b>提示</b>：新建计划默认状态为 active，初始消耗/ROI/CTR/CVR 均为 0，数据将在投放后由平台回传。
        </div>""", unsafe_allow_html=True)

        # Show created campaigns
        created = st.session_state.get("_created_campaigns", [])
        all_plans = cd.get("all_plans", [])
        user_plans = [p for p in all_plans if p.get("id","").startswith(("C","T")) and p not in [
            {"id":"C001"},{"id":"C002"},{"id":"C003"},{"id":"C004"},{"id":"C005"},
            {"id":"T001"},{"id":"T002"},{"id":"T003"},{"id":"T004"},{"id":"T005"},
        ]]
        if created:
            cards = [
                {"label":"📋 已创建计划","value":str(len(created)),"sub":"本次会话","trend":"up"},
                {"label":"💰 总预算","value":f"¥{sum(c.get('budget',0) for c in created):,}","sub":"日预算合计","trend":"up"},
                {"label":"🎯 平均出价","value":f"¥{sum(c.get('bid',0) for c in created)//max(len(created),1):.0f}","sub":"","trend":"warn"},
                {"label":"✅ 活跃","value":str(sum(1 for c in created if c.get('status')=='active')),"sub":"","trend":"up"},
            ]
            st.markdown(_metric_grid(cards), unsafe_allow_html=True)
            if created:
                _render_table(created)
        else:
            st.info("👆 暂无创建记录。在左侧面板点击「🚀 新建」创建你的第一条投放计划。")

    # ====== 内容 ======
    elif tab == "content":
        cards = [
            {"label":"🎬 分析素材数","value":"6","sub":"抖音昨日数据","trend":"up"},
            {"label":"📈 高 CTR 素材","value":"3","sub":"CTR 4.9%-6.8%","trend":"up"},
            {"label":"📉 低 CTR 素材","value":"3","sub":"CTR 1.2%-1.8%","trend":"down"},
            {"label":"✏️ 生成脚本","value":"3","sub":"夏季促销模板","trend":"up"},
        ]
        html = _metric_grid(cards)

        # Top creatives mini-table
        html += '<div class="chart-card" style="margin:0 12px 12px 12px;"><div class="chart-title">🏆 高点击率素材 TOP 3</div>'
        html += '<div style="display:flex;gap:10px;">'
        for i, (ctr, name) in enumerate([(0.068,"夏季促销口播-A"),(0.055,"爆款返场混剪-B"),(0.049,"新品首发开箱-C")]):
            html += f'<div style="flex:1;background:var(--bg-tertiary);border-radius:6px;padding:10px;text-align:center;"><div style="font-size:20px;font-weight:700;color:var(--success);">{ctr*100:.1f}%</div><div style="font-size:11px;color:var(--text-secondary);margin-top:4px;">{name}</div><div style="font-size:10px;color:var(--text-muted);">完播率 {[82,78,75][i]}%</div></div>'
        html += '</div></div>'

        # Low CTR
        html += '<div class="chart-card" style="margin:0 12px 12px 12px;"><div class="chart-title">⚠️ 低点击率素材 BOTTOM 3</div>'
        html += '<div style="display:flex;gap:10px;">'
        for ctr, name in [(0.018,"品牌宣传片-D"),(0.015,"长视频讲解-F"),(0.012,"静态图文-E")]:
            html += f'<div style="flex:1;background:var(--bg-tertiary);border-radius:6px;padding:10px;text-align:center;"><div style="font-size:20px;font-weight:700;color:var(--danger);">{ctr*100:.1f}%</div><div style="font-size:11px;color:var(--text-secondary);margin-top:4px;">{name}</div></div>'
        html += '</div></div>'

        # Analysis insights
        html += '<div class="report-summary" style="margin:0 12px 12px 12px;"><div class="rs-title">🔍 爆款共性分析</div>'
        insights = ["前 3 秒出现价格锚点或产品特写","主播语速偏快（>200字/分），制造紧迫感","BGM 为当前热门卡点曲目","视频时长控制在 15-30 秒"]
        for ins in insights:
            html += f'<div class="rs-row"><span>{ins}</span><span style="color:var(--success);">✓</span></div>'
        html += '</div>'

        # Scripts
        html += '<div class="report-summary" style="margin:0 12px 12px 12px;"><div class="rs-title">✏️ AI 生成脚本预览（3条）</div>'
        scripts = [
            "🔥 夏天到了！爆款T恤限时优惠，10元立减券已发放！库存已补，现在下单立减10元，只剩最后200件，手慢无！点击下方小黄车，赶紧下单别犹豫！",
            "⚡ 闪购通知！新品连衣裙正在秒杀！原价199，现在只需179！库存告急，还剩150件，点击下方链接抢购！",
            "📦 刚收到爆款商品-新品首发，实测分享！面料舒适透气，夏天穿不闷汗。版型显瘦，不挑身材。今日活动价，性价比无敌。真的绝了，赶紧下单别犹豫！",
        ]
        for i, s in enumerate(scripts):
            html += f'<div style="font-size:12px;color:var(--text-secondary);padding:8px;margin:4px 0;background:var(--bg-primary);border-radius:4px;"><b>脚本 {i+1}</b>：{s[:80]}...</div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
        st.caption("💡 脚本已自动发布到飞书内容库，可在飞书中查看和编辑完整内容。")

    # ====== 电商 ======
    elif tab == "ecommerce":
        cards = [
            {"label":"👥 在线人数","value":"2,000","sub":"↑ 5% vs 上时段","trend":"up"},
            {"label":"📦 商品A库存","value":"32 件","sub":"⚠️ 低于 50 件警戒线","trend":"down","highlight":True},
            {"label":"💰 累计 GMV","value":"¥85,000","sub":"转化率 3.0%","trend":"up"},
            {"label":"🎫 优惠券发放","value":"0/500","sub":"10元无门槛","trend":"warn"},
        ]
        html = _metric_grid(cards)

        # Stock gauge
        html += '<div class="chart-card" style="margin:0 12px 12px 12px;"><div class="chart-title">📦 商品库存状态</div>'
        html += '<div style="display:flex;gap:12px;">'
        for pid, name, stock, status in [("A","爆款T恤",32,"low_stock"),("B","新品连衣裙",200,"on_sale")]:
            color = "var(--danger)" if status=="low_stock" else "var(--success)"
            bar_w = min(stock/200*100, 100)
            html += f'<div style="flex:1;"><div style="font-size:13px;font-weight:600;margin-bottom:4px;">{name} ({pid})</div>'
            html += f'<div style="background:var(--bg-primary);border-radius:4px;height:20px;"><div style="background:{color};width:{bar_w}%;height:100%;border-radius:4px;transition:width 0.5s;"></div></div>'
            html += f'<div style="font-size:12px;color:{color};margin-top:2px;">{stock} 件 {"⚠️ 低库存" if status=="low_stock" else "✅ 正常"}</div></div>'
        html += '</div></div>'

        # Live metrics + coupon
        html += '<div class="chart-card" style="margin:0 12px 12px 12px;"><div class="chart-title">🎫 优惠券领取进度</div>'
        html += '<div style="background:var(--bg-primary);border-radius:4px;height:16px;margin:8px 0;"><div style="background:var(--accent);width:0%;height:100%;border-radius:4px;"></div></div>'
        html += '<div style="font-size:12px;color:var(--text-muted);">已领取 0 / 500 张 · 刚发放，等待用户领取</div></div>'

        # Suggested actions
        html += '<div class="report-summary" style="margin:0 12px 12px 12px;"><div class="rs-title">🛒 建议操作</div>'
        actions = [("补货","商品 A 库存 32 件，建议追加 200 件","high"),("发券","创建 10 元无门槛优惠券 ×500 张","medium"),("催单","生成主播催单话术推送到中控屏","low")]
        for act,desc,risk in actions:
            rc = {"high":"var(--danger)","medium":"var(--warning)","low":"var(--success)"}.get(risk,"")
            html += f'<div class="rs-row"><span>{act}</span><span style="color:{rc};">{desc}</span></div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

    # ====== 数据 ======
    elif tab == "data_analysis":
        cards = [
            {"label":"📊 覆盖客户","value":"5","sub":"3 平台（抖音+腾讯+小红书）","trend":"up"},
            {"label":"🏆 最佳 ROI","value":"3.2","sub":"客户C","trend":"up"},
            {"label":"⚠️ 最差 ROI","value":"1.2","sub":"客户D","trend":"down","highlight":True},
            {"label":"💰 总消耗","value":"¥236,000","sub":"本月","trend":"up"},
        ]
        html = _metric_grid(cards)

        bars = [
            {"label":"客户C","value":3.2},{"label":"客户E","value":2.8},{"label":"客户B","value":2.2},
            {"label":"客户A","value":1.5,"highlight":True},{"label":"客户D","value":1.2,"highlight":True},
        ]
        html += _chart("📊 各客户 ROI 排名（按平台汇总）", bars, threshold=_threshold(), max_val=4.0)

        # Budget proposal table
        html += '<div class="report-summary" style="margin:0 12px 12px 12px;"><div class="rs-title">💡 预算再分配建议</div>'
        proposals = [
            ("客户A → 客户C","-20% (¥10,000)","ROI 1.5→3.2 转移","medium"),
            ("客户D → 客户E","-30% (¥15,000)","ROI 1.2→2.8 转移","high"),
        ]
        for src,amt,reason,risk in proposals:
            rc = {"high":"var(--danger)","medium":"var(--warning)"}.get(risk,"")
            html += f'<div class="rs-row"><span>{src}</span><span style="color:{rc};">{amt} · {reason}</span></div>'
        html += '<div class="rs-row"><span>预计整体 ROI 提升</span><span style="color:var(--success);">+0.3</span></div></div>'

        # PPT outline
        html += '<div class="report-summary" style="margin:0 12px 12px 12px;"><div class="rs-title">📋 PPT 提纲（4页）</div>'
        slides = [("1","数据概览","KPI 卡片：消耗/ROI/CPA"),("2","客户 ROI 排名","柱状图：Top3/Bottom2"),("3","预算再分配建议","表格：调整方案+理由"),("4","下周行动建议","重点关注+测试计划")]
        for num,title,content in slides:
            html += f'<div class="rs-row"><span>P{num}. {title}</span><span>{content}</span></div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
        if st.button("📋 复制 PPT 提纲", key="copy_ppt"):
            st.success("✅ 已复制！")

    # ====== 诊断 ======
    elif tab == "diagnosis":
        cards = [
            {"label":"🔍 诊断状态","value":"审核拒绝","sub":"素材虚假承诺","trend":"down","highlight":True},
            {"label":"📋 计划 ID","value":"12345","sub":"抖音平台","trend":"warn"},
            {"label":"⏱️ 被拒时长","value":"3 小时","sub":"今日 9:32","trend":"down"},
            {"label":"🔄 恢复操作","value":"3 项","sub":"替换+重提审+通知","trend":"up"},
        ]
        html = _metric_grid(cards)

        # Root cause card
        html += '<div class="chart-card" style="margin:0 12px 12px 12px;border-left:3px solid var(--danger);"><div class="chart-title">🔴 根因分析</div>'
        html += '<div style="font-size:13px;color:var(--text-primary);">素材内容涉及虚假承诺，触发平台审核规则</div>'
        html += '<div style="font-size:12px;color:var(--text-muted);margin-top:4px;">审核拒绝时间：2026-06-09 09:32 · 审核编号：RV-2026-0609-001</div></div>'

        # Recovery log timeline
        html += '<div class="chart-card" style="margin:0 12px 12px 12px;"><div class="chart-title">📋 自动恢复操作日志</div>'
        steps = [
            ("✅","素材替换","替换为备用视频 backup_001","09:32:15"),
            ("✅","重新提交审核","计划进入审核队列","09:32:18"),
            ("✅","飞书通知","已通知优化师小王","09:32:20"),
        ]
        for icon,title,desc,time in steps:
            html += f'<div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--border);">'
            html += f'<span style="font-size:18px;">{icon}</span><div style="flex:1;"><div style="font-size:13px;font-weight:600;">{title}</div><div style="font-size:11px;color:var(--text-muted);">{desc}</div></div>'
            html += f'<span style="font-size:11px;color:var(--text-muted);">{time}</span></div>'
        html += '</div>'

        html += '<div class="report-summary" style="margin:0 12px 12px 12px;"><div class="rs-title">✅ 恢复结果</div>'
        html += '<div class="rs-row"><span>当前状态</span><span style="color:var(--warning);">审核中（预计 30 分钟内恢复投放）</span></div>'
        html += '<div class="rs-row"><span>处理耗时</span><span>从发现到恢复 &lt; 5 秒</span></div>'
        html += '<div class="rs-row"><span>人工干预</span><span>无需（自动恢复）</span></div></div>'
        st.markdown(html, unsafe_allow_html=True)
