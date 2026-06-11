"""Reusable ChartWidget component — bar chart matching prototype."""
import streamlit as st


def chart_widget(title: str, bars: list, threshold: float = 2.0, max_val: float = 4.0):
    """Render a bar chart matching prototype's .chart-placeholder style.

    Args:
        title: Chart title string.
        bars: List of {"label": str, "value": float, "highlight": bool}.
        threshold: Draw dashed line at this value.
        max_val: Maximum value for scaling bar heights.
    """
    bar_html = []
    for b in bars:
        height = max(6, (b["value"] / max_val) * 110)
        cls = "chart-bar low" if b.get("highlight") else "chart-bar"
        bar_html.append(
            f'<div class="{cls}" style="height:{height:.0f}px;">'
            f'<span class="bar-val">{b["value"]:.1f}</span>'
            f'<span class="bar-label">{b["label"]}</span>'
            f'</div>'
        )

    threshold_bottom = (threshold / max_val) * 110 + 24

    st.markdown(f"""
    <div class="chart-card">
      <div class="chart-title">{title}</div>
      <div class="chart-placeholder" style="position:relative;">
        {"".join(bar_html)}
        <div style="position:absolute;bottom:{threshold_bottom:.0f}px;left:0;right:0;border-top:1px dashed var(--danger);z-index:5;" title="ROI={threshold} 阈值"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)
