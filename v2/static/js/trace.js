// AdCockpit v2 — Trace Board animation
const traceScenes = {
  optimize: {
    flow: ['意图识别', '数据拉取', '数据拉取', '智能分析', '策略生成', '执行操作', '报告生成'],
    steps: [
      { title: '意图识别 — 任务规划', desc: '识别为投放优化意图，拆解为 6 个子任务。数据将并行拉取以节省时间。', result: '' },
      { title: '数据拉取 — 抖音', desc: '拉取抖音近 7 天消耗最高的 5 条计划，涵盖消耗金额、ROI、出价等指标。', result: '5 条计划 · 数据拉取完成' },
      { title: '数据拉取 — 腾讯广告', desc: '拉取腾讯广告近 7 天消耗最高的 5 条计划。数据已与抖音侧合并。', result: '5 条计划 · 数据拉取完成' },
      { title: '智能分析 — 异常检测', desc: '分析全部计划，筛选 ROI 低于阈值的计划，标注严重程度，其余标记为健康。', result: '低于阈值的计划已高亮' },
      { title: '策略生成 — 优化方案', desc: '针对不达标计划生成优化建议：降价 + 必要时降预算。具体由数据和出价综合计算。', result: '降价 + 降预算 · 预计改善整体 ROI' },
      { title: '执行操作 — 等待确认', desc: '优化请求已提交，等待执行完成。', result: '执行中…' },
      { title: '报告生成 — 完成', desc: '优化报告已生成，可在右侧仪表盘查看详情。', result: '优化完成' },
    ]
  },
  create: {
    flow: ['参数配置', '数据提交', '执行操作', '报告生成'],
    steps: [
      { title: '参数配置 — 接收需求', desc: '已接收投放计划参数。正在提交到广告平台。', result: '参数验证通过' },
      { title: '数据提交 — 平台审核', desc: '已提交至广告平台。审核中…', result: '审核通过' },
      { title: '执行操作 — 等待确认', desc: '计划待确认上线。', result: '等待确认' },
      { title: '报告生成', desc: '计划已上线。', result: '创建成功' },
    ]
  }
};

function buildDefaultTrace(scene) {
  const cfg = traceScenes[scene] || traceScenes.optimize;
  const ft = document.getElementById('flowTracker');
  ft.innerHTML = cfg.flow.map((label, i) => {
    const dotCls = i === 0 ? 'done' : '';
    const lineCls = i > 0 && i <= 1 ? 'done' : '';
    const line = i > 0 ? `<div class="flow-line ${lineCls}"></div>` : '';
    return `${line}<div class="flow-node"><div class="flow-dot ${dotCls}">${dotCls === 'done' ? '✓' : ''}</div><div class="flow-label">${label}</div></div>`;
  }).join('');

  const sc = document.getElementById('stepCards');
  sc.innerHTML = cfg.steps.map((s, i) => {
    const cls = i === 0 ? 'done' : '';
    return `<div class="step-card ${cls}"><div class="step-icon ${cls}">${cls === 'done' ? '✓' : ''}</div><div class="step-body"><div class="step-title">${s.title}</div><div class="step-desc">${i === 0 ? s.desc : ''}</div></div></div>`;
  }).join('');
}

function animateTrace(scene, callback) {
  const cfg = traceScenes[scene] || traceScenes.optimize;
  const nodes = cfg.flow;
  const steps = cfg.steps;

  // Reset
  buildDefaultTrace(scene);

  let frame = 0;
  const totalFrames = nodes.length * 3;

  const interval = setInterval(() => {
    const nodeIdx = Math.min(Math.floor(frame / 3), nodes.length - 1);
    const prog = (frame % 3) / 3;

    // Update flow tracker
    const dots = document.querySelectorAll('#flowTracker .flow-dot');
    const lines = document.querySelectorAll('#flowTracker .flow-line');
    dots.forEach((dot, i) => {
      dot.className = 'flow-dot';
      dot.textContent = '';
      if (i < nodeIdx) { dot.classList.add('done'); dot.textContent = '✓'; }
      else if (i === nodeIdx && prog < 0.8) { dot.classList.add('active'); dot.textContent = '⋯'; }
      else if (i === nodeIdx) { dot.classList.add('wait'); dot.textContent = '!'; }
    });
    lines.forEach((line, i) => {
      if (i < nodeIdx) line.classList.add('done');
      else line.classList.remove('done');
    });

    // Update step cards
    const cards = document.querySelectorAll('#stepCards .step-card');
    cards.forEach((card, i) => {
      card.className = 'step-card';
      const icon = card.querySelector('.step-icon');
      icon.className = 'step-icon';
      icon.textContent = '';
      const descEl = card.querySelector('.step-desc');

      if (i < nodeIdx) {
        card.classList.add('done'); icon.classList.add('done'); icon.textContent = '✓';
        descEl.textContent = steps[i].desc;
      } else if (i === nodeIdx) {
        if (prog < 0.8) { card.classList.add('running'); icon.classList.add('running'); icon.textContent = '⋯'; }
        else { card.classList.add('waiting'); icon.classList.add('waiting'); icon.textContent = '!'; }
        const chars = Math.max(3, Math.floor(steps[i].desc.length * Math.min(prog * 1.5, 1)));
        descEl.textContent = steps[i].desc.substring(0, chars) + (prog < 0.8 ? '▌' : '');
      } else {
        descEl.textContent = '';
      }
    });

    frame++;
    if (frame >= totalFrames) {
      clearInterval(interval);
      if (callback) callback();
    }
  }, 150);
}
