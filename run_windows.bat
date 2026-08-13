@echo off
cd /d "%~dp0"
echo Installing (first run only)...
python -m pip install -r requirements.txt
echo Starting the MI ^& Accelerate app...
python -m streamlit run streamlit_app.py
pause
