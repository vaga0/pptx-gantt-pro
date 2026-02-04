@echo off
echo Starting Gantt Chart Generator...
cd /d "%~dp0"
python -m streamlit run gantt_app.py
pause
