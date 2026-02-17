@echo off
REM Activate the virtual environment, install opencv-python, and run Streamlit app
cd /d "%~dp0.."
call attendance_app\.venv\Scripts\activate
pip install opencv-python
streamlit run attendance_app/app.py
pause
