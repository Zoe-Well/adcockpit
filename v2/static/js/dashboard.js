// AdCockpit v2 — Dashboard data loading
let tablePage = 0, tableSort = 'roi', tableAsc = true;
const PAGE_SIZE = 5;

async function loadDashboard(tab) {
  const el = document.getElementById('dashContent');
  if (tab === 'optimize') {
    try {
      const r = await fetch('/api/campaigns/all');
      const d = await r.json();
      const threshold = 2.0;
      const below = d.below_threshold || [];
      el.innerHTML = renderMetrics(d, below.length, threshold) + renderChart(d.plans, threshold) +
        renderAlerts(below) + renderTable(d.plans, threshold);
    } catch (e) { el.innerHTML = '<p style="padding:16px;color:var(--text-2);">数据加载失败，请检查后端服务</p>'; }
  } else if (tab === 'create') {
    el.innerHTML = `<div style="padding:16px;"><h4>投放管理中心</h4><p style="color:var(--text-2);font-size:12px;">在左侧对话面板点击"新建计划"创建投放计划。</p></div>`;
  } else if (tab === 'content') {
    try {
      const r = await fetch('/api/content/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ platform: 'douyin', top_n: 3, template_id: 'summer_promo' }) });
      const d = await r.json();
      el.innerHTML = `<div style="padding:16px;"><h4>内容生产</h4>${d.scripts.map((s, i) => `<div style="font-size:12px;color:var(--text-2);padding:8px;margin:4px 0;background:var(--card);border:1px solid var(--border);border-radius:6px);"><b>脚本 ${i+1}</b>：${s.substring(0,100)}...</div>`).join('')}</div>`;
    } catch (e) { el.innerHTML = '<p style="padding:16px;">加载失败</p>'; }
  } else {
    el.innerHTML = `<div style="padding:16px;"><h4>${tab}</h4><p style="color:var(--text-2);font-size:12px;">此功能即将上线。</p></div>`;
  }
}

function renderMetrics(d, belowCount, threshold) {
  const roiHl = d.avg_roi < threshold;
  return `<div class="metrics-grid">
    <div class="metric-card${roiHl ? ' alert' : ''}"><div class="metric-label">整体 ROI</div><div class="metric-value${roiHl ? ' red' : ''}">${d.avg_roi.toFixed(2)}</div><div class="metric-sub${roiHl ? ' down' : ' up'}">${roiHl ? '低于阈值' : '正常'} ${threshold}</div></div>
    <div class="metric-card"><div class="metric-label">总消耗</div><div class="metric-value">${d.total_cost.toLocaleString()}</div><div class="metric-sub up">${d.count} 条计划</div></div>
    <div class="metric-card"><div class="metric-label">活跃计划</div><div class="metric-value">${d.count}</div><div class="metric-sub up">${belowCount} 条需关注</div></div>
  </div>`;
}

function renderChart(plans, threshold) {
  const maxRoi = Math.max(4, ...plans.map(p => p.roi));
  const bars = plans.map(p => {
    const h = Math.max(6, (p.roi / maxRoi) * 100);
    const cls = p.roi < threshold ? 'low' : '';
    return `<div class="chart-bar ${cls}" style="height:${h}px"><div class="val">${p.roi.toFixed(1)}</div><div class="lbl">${p.id}</div></div>`;
  }).join('');
  const thrPos = (threshold / maxRoi) * 100 + 20;
  return `<div class="chart-box"><h4>各计划 ROI 对比（阈值 ${threshold}）</h4><div class="chart-bars" style="height:120px">${bars}<div class="chart-threshold" style="bottom:${thrPos}px"></div></div></div>`;
}

function renderAlerts(below) {
  if (!below || below.length === 0) return '';
  return below.slice(0, 2).map(p => {
    const sev = p.roi < 1.2 ? '严重偏低' : p.roi < 1.5 ? '持续下滑' : '略低于阈值';
    const cls = p.roi < 1.5 ? '' : ' warn';
    return `<div class="alert-item${cls}"><div style="font-size:16px;">&#9888;</div><div><div style="font-size:12px;font-weight:600;">${p.id} — ROI ${sev}</div><div style="font-size:11px;color:var(--text-2);margin-top:2px;">${p._platform === 'douyin' ? '抖音' : '腾讯'} · 消耗 ¥${(p.cost||0).toLocaleString()} · ROI ${p.roi}</div></div></div>`;
  }).join('');
}

function renderTable(allPlans, threshold) {
  const total = allPlans.length;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const start = tablePage * PAGE_SIZE;
  const page = allPlans.slice(start, start + PAGE_SIZE);
  const rows = page.map(p => {
    const roiLo = p.roi < threshold;
    return `<tr><td>${p.id}</td><td>${(p.name||p.id).substring(0,10)}</td><td>${p._platform === 'douyin' ? '抖音' : '腾讯'}</td><td>${(p.cost||0).toLocaleString()}</td><td class="${roiLo ? 'roi-lo' : ''}">${p.roi.toFixed(2)}</td><td>${p.cpa||0}</td><td>${((p.ctr||0)*100).toFixed(1)}%</td><td>${p.bid||0}</td><td class="status-ok">${p.status||'active'}</td></tr>`;
  }).join('');
  return `<div class="table-box"><h4>投放计划明细（第 ${tablePage+1}/${totalPages} 页 · 共 ${total} 条）</h4>
    <table><tr><th>ID</th><th>计划名称</th><th>平台</th><th>消耗</th><th>ROI</th><th>CPA</th><th>CTR</th><th>出价</th><th>状态</th></tr>${rows}</table>
    <div class="pagination"><button onclick="tablePage=Math.max(0,tablePage-1);loadDashboard('optimize')" ${tablePage===0?'disabled':''}>‹ 上一页</button><span>第 ${tablePage+1}/${totalPages} 页</span><button onclick="tablePage=Math.min(${totalPages-1},tablePage+1);loadDashboard('optimize')" ${tablePage>=totalPages-1?'disabled':''}>下一页 ›</button></div></div>`;
}
