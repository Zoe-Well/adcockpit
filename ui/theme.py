"""Custom CSS — replicates adcockpit-prototype.html dark theme."""
import streamlit as st


def inject_custom_css():
    st.markdown("""
<style>
:root {
  --bg-primary: #0f1117;
  --bg-secondary: #1a1d27;
  --bg-tertiary: #242836;
  --border: #2a2e3a;
  --text-primary: #e8eaed;
  --text-secondary: #9aa0b0;
  --text-muted: #5f6570;
  --accent: #4c6ef5;
  --success: #51cf66;
  --warning: #fcc419;
  --danger: #ff6b6b;
  --info: #22b8cf;
}

#MainMenu, footer, .stDeployButton, .stApp > header { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
.stApp, .stMainBlockContainer { background: var(--bg-primary) !important; }
.block-container { padding: 0 !important; max-width: none !important; }

/* Top bar */
.topbar {
  height: 44px; background: var(--bg-secondary); border-bottom: 1px solid var(--border);
  display: flex; align-items: center; padding: 0 16px; gap: 12px; margin-bottom: 8px;
}
.topbar .logo { font-size: 15px; font-weight: 700; background: linear-gradient(135deg, var(--accent), #845ef7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.topbar .badge { font-size: 10px; padding: 2px 8px; border-radius: 10px; background: rgba(76,110,245,0.15); color: var(--accent); }

/* Columns */
.stHorizontalBlock { gap: 0 !important; }
[data-testid="stHorizontalBlock"] > .stColumn:not(:last-child) { border-right: 1px solid var(--border) !important; }
  font-size: 12px; font-weight: 600; letter-spacing: 0.5px;
  color: var(--text-secondary); padding: 8px 12px;
  background: var(--bg-secondary); border-bottom: 1px solid var(--border);
  text-transform: uppercase;
}

/* ===== Chat ===== */
.chat-msg { display: flex; gap: 10px; padding: 8px 12px; }
.chat-msg.user { flex-direction: row-reverse; }
.chat-msg .avatar { width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 600; }
.chat-msg.agent .avatar { background: var(--accent); color: #fff; }
.chat-msg.user  .avatar { background: var(--bg-tertiary); color: var(--text-secondary); }
.chat-msg .bubble { max-width: 85%; padding: 10px 14px; border-radius: 10px; font-size: 14px; line-height: 1.6; }
.chat-msg.agent .bubble { background: var(--bg-tertiary); color: var(--text-primary); border-top-left-radius: 3px; }
.chat-msg.user  .bubble { background: var(--accent); color: #fff; border-top-right-radius: 3px; }

/* ===== Approval ===== */
.approval-card { background: var(--bg-tertiary); border: 1px solid var(--warning); border-radius: 8px; padding: 14px; margin: 8px 12px; }
.approval-card .ac-title { font-size: 15px; font-weight: 600; color: var(--warning); margin-bottom: 10px; }
.approval-card .ac-row { display: flex; justify-content: space-between; font-size: 14px; padding: 6px 0; border-bottom: 1px solid var(--border); }
.approval-card .ac-row:last-child { border-bottom: none; }

/* ===== DAG ===== */
.dag-bar { background: var(--bg-secondary); border-radius: 8px; padding: 8px 10px; display: flex; align-items: center; gap: 5px; font-size: 10px; color: var(--text-secondary); margin: 0 8px 8px 8px; }
.dag-node { padding: 2px 6px; border-radius: 3px; font-weight: 500; font-size: 9px; }
.dag-node.supervisor { background: rgba(76,110,245,0.2); color: var(--accent); }
.dag-node.data { background: rgba(34,184,207,0.2); color: var(--info); }
.dag-node.analysis { background: rgba(252,196,25,0.2); color: var(--warning); }
.dag-node.strategy { background: rgba(132,94,247,0.2); color: #845ef7; }
.dag-node.execute { background: rgba(81,207,102,0.2); color: var(--success); }
.dag-node.report { background: rgba(255,107,107,0.2); color: var(--danger); }
.dag-arrow { color: var(--text-muted); }

/* ===== Step cards ===== */
.step-card { background: var(--bg-secondary); border-radius: 8px; border-left: 3px solid var(--border); padding: 10px 12px; display: flex; gap: 10px; margin: 0 8px 6px 8px; }
.step-card.status-done    { border-left-color: var(--success); }
.step-card.status-running { border-left-color: var(--accent); }
.step-card.status-waiting { border-left-color: var(--warning); }
.step-card.status-failed  { border-left-color: var(--danger); }
.step-card.status-pending { opacity: 0.5; }
.step-icon { width: 28px; height: 28px; border-radius: 6px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 14px; }
.step-icon.done    { background: rgba(81,207,102,0.15); }
.step-icon.running { background: rgba(76,110,245,0.15); }
.step-icon.waiting { background: rgba(252,196,25,0.15); }
.step-icon.failed  { background: rgba(255,107,107,0.15); }
.step-icon.pending { background: var(--bg-tertiary); }
.step-title { font-size: 12px; font-weight: 600; margin-bottom: 2px; }
.step-desc { font-size: 11px; color: var(--text-secondary); line-height: 1.4; }

/* ===== Dashboard ===== */
.metrics-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 0 12px 12px 12px; }
.metric-card { background: var(--bg-secondary); border-radius: 8px; padding: 14px; border: 1px solid var(--border); }
.metric-card .metric-label { font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 6px; }
.metric-card .metric-value { font-size: 26px; font-weight: 700; color: var(--text-primary); }
.metric-card .metric-sub { font-size: 12px; margin-top: 4px; }
.metric-sub.up   { color: var(--success); }
.metric-sub.down { color: var(--danger); }
.metric-sub.warn { color: var(--warning); }
.metric-hl { border-color: var(--danger) !important; background: rgba(255,107,107,0.06) !important; }
.metric-hl .metric-value { color: var(--danger) !important; }

.chart-card { background: var(--bg-secondary); border-radius: 8px; border: 1px solid var(--border); padding: 16px; margin: 0 12px 12px 12px; }
.chart-title { font-size: 13px; color: var(--text-secondary); margin-bottom: 10px; font-weight: 600; }
.chart-placeholder { display: flex; align-items: flex-end; gap: 6px; height: 130px; padding-bottom: 20px; }
.chart-bar { flex: 1; border-radius: 3px 3px 0 0; position: relative; background: linear-gradient(180deg, var(--accent), rgba(76,110,245,0.3)); min-width: 22px; }
.chart-bar.low { background: linear-gradient(180deg, var(--danger), rgba(255,107,107,0.3)); }
.chart-bar .bar-label { position: absolute; bottom: -18px; left: 50%; transform: translateX(-50%); font-size: 9px; color: var(--text-muted); }
.chart-bar .bar-val { position: absolute; top: -16px; left: 50%; transform: translateX(-50%); font-size: 9px; font-weight: 600; color: var(--text-primary); }

.alert-list { margin: 0 12px 12px 12px; }
.alert-item { background: var(--bg-secondary); border-radius: 6px; padding: 12px 14px; display: flex; align-items: center; gap: 10px; border-left: 3px solid var(--danger); margin-bottom: 6px; }
.alert-item.warn { border-left-color: var(--warning); }
.alert-title { font-size: 13px; font-weight: 600; }
.alert-detail { font-size: 12px; color: var(--text-muted); margin-top: 2px; }

.report-summary { background: var(--bg-secondary); border-radius: 8px; border: 1px solid var(--border); padding: 16px; margin: 0 12px 12px 12px; }
.rs-title { font-size: 14px; font-weight: 600; margin-bottom: 10px; }
.rs-row { display: flex; justify-content: space-between; font-size: 13px; padding: 5px 0; color: var(--text-secondary); }
</style>
""", unsafe_allow_html=True)
