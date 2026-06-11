"""Reusable ReportSummary component."""
import streamlit as st
import pyperclip


def report_summary(title: str, rows: list):
    """Render a report summary section matching prototype's .report-summary style.

    Args:
        title: Report title (e.g., "📋 优化报告预览").
        rows: List of (label, value) tuples.
    """
    rows_html = []
    for label, value in rows:
        color = ""
        if isinstance(value, str) and "3 条" in value:
            color = 'style="color:var(--danger);"'
        elif isinstance(value, str) and ("节省" in value or "提升" in value or "+" in value):
            color = 'style="color:var(--success);"'
        rows_html.append(
            f'<div class="rs-row"><span>{label}</span><span {color}>{value}</span></div>'
        )

    report_text = "\n".join(f"{label}: {value}" for label, value in rows)

    st.markdown(f"""
    <div class="report-summary">
      <div class="rs-title">{title}</div>
      {"".join(rows_html)}
    </div>
    """, unsafe_allow_html=True)

    if st.button("📋 一键复制报告", key="copy_report"):
        try:
            pyperclip.copy(report_text)
            st.success("✅ 已复制！")
        except Exception:
            st.info(report_text)
