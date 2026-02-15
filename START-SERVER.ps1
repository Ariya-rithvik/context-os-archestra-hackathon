#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ContextOS MCP Server Startup Script
    
.DESCRIPTION
    Starts the ContextOS MCP Server on port 8000.
    Communicates with Archestra via SSE (Server-Sent Events)

.EXAMPLE
    .\START-SERVER.ps1
#>

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════╗"
Write-Host "║     ⚡ ContextOS MCP Server Launcher              ║"
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

# Start MCP Server
Write-Host ""
Write-Host "🚀 Starting MCP Server..." -ForegroundColor Cyan
Write-Host ""
Write-Host "────────────────────────────────────────────────────"
Write-Host ""

$serverScript = Join-Path $PSScriptRoot "server.py"
python $serverScript

# If we get here, the server was stopped
Write-Host ""
Write-Host "────────────────────────────────────────────────────"
Write-Host ""
Write-Host "🛑 Server stopped." -ForegroundColor Yellow
Write-Host ""
