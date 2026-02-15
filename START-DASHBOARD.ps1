#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ContextOS Dashboard Startup Script
    
.DESCRIPTION
    Starts the ContextOS Chat Dashboard on port 5050.
    Provides a rich UI for testing the semantic router.

.EXAMPLE
    .\START-DASHBOARD.ps1
#>

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════╗"
Write-Host "║     ⚡ ContextOS Dashboard Launcher               ║"
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

# Check dependencies
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

# Start Dashboard
Write-Host ""
Write-Host "🚀 Starting Dashboard..." -ForegroundColor Cyan
Write-Host ""
Write-Host "────────────────────────────────────────────────────"
Write-Host ""

$dashboardScript = Join-Path $PSScriptRoot "dashboard.py"
python $dashboardScript

# If we get here, the server was stopped
Write-Host ""
Write-Host "────────────────────────────────────────────────────"
Write-Host ""
Write-Host "🛑 Dashboard stopped." -ForegroundColor Yellow
Write-Host ""
