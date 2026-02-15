#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ContextOS Telegram Bot Launcher
    
.DESCRIPTION
    Starts the Telegram bot for the Semantic-RPC Bridge.
    
.NOTES
    Requires: TELEGRAM_BOT_TOKEN environment variable set
    Get token: https://t.me/botfather → /newbot
    
.EXAMPLE
    $env:TELEGRAM_BOT_TOKEN = "123456:ABCDEFGhijklmnop"
    .\START-TELEGRAM.ps1
#>

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════╗"
Write-Host "║     ⚡ ContextOS Telegram Bot Launcher            ║"
Write:Host "║     The Universal Input Node                       ║"
Write-Host "╚════════════════════════════════════════════════════╝"
Write-Host ""

# Check Python
Write-Host "🔍 Checking Python installation..." -ForegroundColor Cyan
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}
$pythonVersion = python --version
Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green

# Check Telegram token
Write-Host ""
Write-Host "🔑 Checking Telegram Bot Token..." -ForegroundColor Cyan
$token = $env:TELEGRAM_BOT_TOKEN
if (-not $token) {
    Write-Host "❌ TELEGRAM_BOT_TOKEN not set!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Setup:" -ForegroundColor Yellow
    Write-Host "  1. Go to https://t.me/botfather" -ForegroundColor Gray
    Write-Host "  2. Type /newbot and follow instructions" -ForegroundColor Gray
    Write-Host "  3. Copy your bot token" -ForegroundColor Gray
    Write-Host "  4. Run this in PowerShell:" -ForegroundColor Gray
    Write-Host "     `$env:TELEGRAM_BOT_TOKEN = 'YOUR_TOKEN_HERE'" -ForegroundColor Magenta
    Write-Host "  5. Then run this script again" -ForegroundColor Gray
    Write-Host ""
    exit 1
}
Write-Host "✅ Token found: $($token.Substring(0, 20))..." -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "📦 Installing/verifying dependencies..." -ForegroundColor Cyan
$reqFile = Join-Path $PSScriptRoot "requirements.txt"
if (Test-Path $reqFile) {
    pip install -q -r $reqFile 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Some dependencies may have warnings (continuing...)" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ requirements.txt not found" -ForegroundColor Red
    exit 1
}

# Start bot
Write-Host ""
Write-Host "🚀 Starting Telegram Bot..." -ForegroundColor Cyan
Write-Host ""
Write-Host "────────────────────────────────────────────────────"
Write-Host ""

$botScript = Join-Path $PSScriptRoot "telegram_bot.py"
python $botScript

# If we get here, the bot was stopped
Write-Host ""
Write-Host "────────────────────────────────────────────────────"
Write-Host ""
Write-Host "🛑 Bot stopped." -ForegroundColor Yellow
Write-Host ""
