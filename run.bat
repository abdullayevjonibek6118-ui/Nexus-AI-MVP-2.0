@echo off
echo ===================================================
echo     Nexus AI MVP - One-Click Launcher
echo ===================================================

cd /d "%~dp0"

echo [1/4] Checking Python Environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.10+ and add it to PATH.
    pause
    exit /b
)

if not exist "backend\venv" (
    echo [2/4] Creating Virtual Environment...
    cd backend
    python -m venv venv
    cd ..
) else (
    echo [2/4] Virtual Environment exists.
)

echo [3/4] Installing Dependencies...
call backend\venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy alembic pydantic python-jose[cryptography] passlib[bcrypt] python-multipart requests
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b
)

echo [4/4] Starting Services...
start "Nexus AI Backend" cmd /k "cd backend && call venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"
start "Nexus AI Frontend" cmd /k "npx -y http-server frontend -p 3000 --cors -c-1"

echo.
echo SUCCESS! 
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000/docs
echo.
echo Press any key to stop servers...
pause
taskkill /F /IM node.exe
taskkill /F /IM uvicorn.exe
taskkill /F /IM python.exe
