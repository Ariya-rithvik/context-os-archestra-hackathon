@echo off
REM ContextOS Telegram Bot Launcher (Windows)
setlocal enabledelayedexpansion

echo.
echo ======================================================
echo     ⚡ ContextOS Telegram Bot Launcher
echo     The Universal Input Node
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

REM Check Telegram token
echo.
echo 🔑 Checking Telegram Bot Token...
if "%TELEGRAM_BOT_TOKEN%"=="" (
    echo ❌ TELEGRAM_BOT_TOKEN not set!
    echo.
    echo Setup:
    echo   1. Go to https://t.me/botfather
    echo   2. Type /newbot and follow instructions
    echo   3. Copy your bot token
    echo   4. Run:
    echo      set TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE
    echo   5. Then run this script again
    echo.
    pause
    exit /b 1
)
for /f "tokens=1-3 delims=:" %%a in ("%TELEGRAM_BOT_TOKEN%") do (
    echo ✅ Token found: %%a:%%b...
)

REM Install dependencies
echo.
echo 📦 Installing dependencies...
pip install -q -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Some dependencies had warnings, continuing...
) else (
    echo ✅ Dependencies installed
)

REM Start bot
echo.
echo 🚀 Starting Telegram Bot...
echo.
echo ──────────────────────────────────────────────────
echo.

python telegram_bot.py

echo.
echo ──────────────────────────────────────────────────
echo.
echo 🛑 Bot stopped.
echo.
pause
