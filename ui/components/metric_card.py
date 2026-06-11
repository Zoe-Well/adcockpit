"""Reusable MetricCard component."""
import streamlit as st


def metric_card(label: str, value: str, sub_text: str = "", sub_trend: str = "",
                highlight: bool = False):
    """Render a metric card matching the HTML prototype's .metric-card style.

    Args:
        label: Uppercase label text (e.g., "⚠️ 整体 ROI").
        value: Large value text (e.g., "1.87").
        sub_text: Trend/subtitle text (e.g., "▼ 0.23 vs 昨日").
        sub_trend: "up" = green, "down" = red, "warn" = yellow.
        highlight: If True, apply red border (.metric-hl).
    """
    cls = "metric-card metric-hl" if highlight else "metric-card"
    sub_cls = f"metric-sub {sub_trend}" if sub_trend else "metric-sub"

    st.markdown(f"""
    <div class="{cls}">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      <div class="{sub_cls}">{sub_text}</div>
    </div>
    """, unsafe_allow_html=True)
