// AdCockpit v2 — Main app logic
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('header-time').textContent = new Date().toLocaleString('zh-CN');
  // Sidebar nav
  document.querySelectorAll('.sidebar-item[data-tab]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sidebar-item[data-tab]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const tab = btn.dataset.tab;
      loadDashboard(tab);
      buildDefaultTrace(tab);
      document.getElementById('paramCardContainer').innerHTML = '';
    });
  });
  // Default: load optimize dashboard
  loadDashboard('optimize');
  buildDefaultTrace('optimize');
});

async function sendMessage() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;
  appendChat('user', text);
  input.value = '';

  try {
    const r = await fetch('/api/intent/classify', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_input: text })
    });
    const d = await r.json();
    if (d.type === 'business') {
      appendChat('ai', d.reply || '收到。下方是优化参数，可调整后执行。');
      showParamCard(d.scene);
    } else {
      appendChat('ai', d.reply);
    }
  } catch (e) {
    appendChat('ai', '系统暂时不可用，请稍后重试。');
  }
}

function appendChat(role, content) {
  const el = document.getElementById('chatMsgs');
  const div = document.createElement('div');
  div.className = `chat-msg ${role === 'user' ? 'user' : 'ai'}`;
  div.innerHTML = `<div class="avatar">${role === 'user' ? '王' : 'AI'}</div><div class="bubble">${content.replace(/\n/g, '<br>')}</div>`;
  el.appendChild(div);
  el.scrollTop = el.scrollHeight;
}

function showParamCard(scene) {
  const c = document.getElementById('paramCardContainer');
  if (scene === 'ad_placement' || scene === 'optimize') {
    c.innerHTML = `<div class="param-card" style="display:block;"><h4>优化参数设置</h4>
      <div class="param-row">
        <div><label>投放平台</label><select id="p_platforms" multiple><option value="douyin" selected>抖音</option><option value="tencent" selected>腾讯</option></select></div>
        <div><label>时间范围</label><select id="p_days"><option value="7" selected>近 7 天</option><option value="3">近 3 天</option><option value="30">近 30 天</option></select></div>
        <div><label>拉取计划数</label><input type="number" id="p_topn" value="5"></div>
        <div><label>ROI 阈值</label><input type="number" id="p_threshold" value="2.0" step="0.1"></div>
        <div><label>出价调整 %</label><input type="number" id="p_bid" value="-10"></div>
        <div><label>预算调整 %</label><input type="number" id="p_budget" value="-20"></div>
      </div>
      <div class="param-btns">
        <button class="btn-primary" onclick="runOptimize()">开始优化</button>
        <button class="btn-secondary" onclick="document.getElementById('paramCardContainer').innerHTML=''">取消</button>
      </div></div>`;
  } else {
    c.innerHTML = `<div class="param-card" style="display:block;"><h4>${scene} 功能开发中</h4><p style="font-size:12px;color:var(--text-2);">该场景的参数面板即将上线。</p>
      <div class="param-btns"><button class="btn-secondary" onclick="document.getElementById('paramCardContainer').innerHTML=''">关闭</button></div></div>`;
  }
}

async function runOptimize() {
  const platforms = ['douyin', 'tencent']; // simplified
  const days = parseInt(document.getElementById('p_days').value);
  const top_n = parseInt(document.getElementById('p_topn').value);
  const roi_threshold = parseFloat(document.getElementById('p_threshold').value);
  const bid_adjust_pct = parseInt(document.getElementById('p_bid').value);
  const budget_adjust_pct = parseInt(document.getElementById('p_budget').value);

  document.getElementById('paramCardContainer').innerHTML = '';
  appendChat('ai', `开始优化：${platforms.length}平台/${days}天/Top${top_n}/ROI<${roi_threshold}/出价${bid_adjust_pct}%`);

  // Animate trace first
  animateTrace('optimize', async () => {
    // Then execute
    try {
      const r = await fetch('/api/campaigns/optimize', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platforms, days, top_n, roi_threshold, bid_adjust_pct, budget_adjust_pct })
      });
      const d = await r.json();
      appendChat('ai', `优化完成！共调整 ${d.changes.length} 项：\n${d.changes.map(c => '• ' + c).join('\n')}`);
      loadDashboard('optimize');
    } catch (e) {
      appendChat('ai', '优化请求失败，请重试。');
    }
  });
}
