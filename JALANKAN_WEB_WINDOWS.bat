@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel% equ 0 (
  py -3 -m streamlit run web_app.py
) else (
  python -m streamlit run web_app.py
)
pause
