"""AdCockpit v2 — rendered via st.html() for full control matching prototype."""
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="AdCockpit")

# Read the prototype HTML
with open("adcockpit-v2-prototype.html", "r", encoding="utf-8") as f:
    html = f.read()

# Render it full-screen
components.html(html, height=1000, scrolling=True)
