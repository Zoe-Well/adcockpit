@echo off
cd /d "%~dp0"
set PYTHONPATH=.
streamlit run ui/app.py
