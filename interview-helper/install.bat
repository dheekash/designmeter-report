@echo off
echo ============================================================
echo  Interview Helper — Windows Install Script
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ from https://python.org
    pause & exit /b 1
)

:: Create virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

:: Activate and install
echo Installing dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Copy .env if not present
if not exist ".env" (
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env and add your API keys before running!
)

echo.
echo ============================================================
echo  Installation complete!
echo.
echo  Next steps:
echo    1. Edit .env and add your OpenAI / Claude / Gemini API key
echo    2. Run:  .venv\Scripts\python main.py
echo    3. Or build an exe:  .venv\Scripts\python build_exe.py
echo ============================================================
echo.
pause
