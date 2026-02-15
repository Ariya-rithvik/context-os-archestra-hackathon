@echo off
REM ContextOS MCP Server Startup (Windows)
setlocal enabledelayedexpansion

echo.
echo ======================================================
echo     ⚡ ContextOS MCP Server Launcher
echo ======================================================
echo.

REM Check Python
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.10+
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set "PYTHON_VER=%%i"
echo ✅ Found: %PYTHON_VER%

REM Install dependencies
echo.
echo 📦 Installing dependencies...
pip install -q -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Some dependencies had warnings, continuing...
) else (
    echo ✅ Dependencies installed
)

REM Start server
echo.
echo 🚀 Starting MCP Server...
echo.
echo ──────────────────────────────────────────────────
echo.

python server.py

echo.
echo ──────────────────────────────────────────────────
echo.
echo 🛑 Server stopped.
echo.
pause
