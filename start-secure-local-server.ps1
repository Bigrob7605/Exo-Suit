# Secure Local Server Startup Script for Exo-Suit V5.0
# This script ensures the website runs locally only with security measures

param(
    [int]$Port = 8000,
    [string]$BindHost = "127.0.0.1"
)

Write-Host "🔒 SECURE LOCAL SERVER STARTUP - EXO-SUIT V5.0" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Security validation
if ($BindHost -notin @("127.0.0.1", "localhost", "::1")) {
    Write-Host "🚨 SECURITY ERROR: Only localhost binding allowed!" -ForegroundColor Red
    Write-Host "   Allowed hosts: 127.0.0.1, localhost, ::1" -ForegroundColor Yellow
    Write-Host "   Current host: $BindHost" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Security validation passed" -ForegroundColor Green
Write-Host "   Host: $BindHost" -ForegroundColor White
Write-Host "   Port: $Port" -ForegroundColor White
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found or not in PATH" -ForegroundColor Red
    Write-Host "   Please install Python and ensure it's in your PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to continue"
    exit 1
}

# Check if secure server script exists
$secureServerPath = Join-Path $PSScriptRoot "local-security-config.py"
if (-not (Test-Path $secureServerPath)) {
    Write-Host "❌ Secure server script not found: $secureServerPath" -ForegroundColor Red
    Write-Host "   Please ensure local-security-config.py exists" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Secure server script found" -ForegroundColor Green
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot
Write-Host "📁 Working directory: $PWD" -ForegroundColor Yellow
Write-Host ""

# Check for existing processes on the port
Write-Host "🔍 Checking port availability..." -ForegroundColor Yellow
$existingProcess = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($existingProcess) {
    Write-Host "⚠️  Port $Port is already in use by:" -ForegroundColor Yellow
    $existingProcess | ForEach-Object {
        $process = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
        Write-Host "   PID: $($_.OwningProcess) - $($process.ProcessName)" -ForegroundColor Yellow
    }
    Write-Host ""
    $continue = Read-Host "Do you want to continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Host "🚫 Server startup cancelled" -ForegroundColor Red
        exit 0
    }
}

Write-Host "✅ Port $Port is available" -ForegroundColor Green
Write-Host ""

# Display security information
Write-Host "🔒 SECURITY FEATURES ENABLED:" -ForegroundColor Cyan
Write-Host "   • Localhost binding only (127.0.0.1)" -ForegroundColor White
Write-Host "   • External access blocked" -ForegroundColor White
Write-Host "   • Security headers enabled" -ForegroundColor White
Write-Host "   • Access logging for local requests only" -ForegroundColor White
Write-Host "   • XSS protection enabled" -ForegroundColor White
Write-Host "   • Content Security Policy active" -ForegroundColor White
Write-Host ""

# Start secure server
Write-Host "🚀 Starting secure local server..." -ForegroundColor Green
Write-Host "   URL: http://$BindHost`:$Port" -ForegroundColor Cyan
Write-Host "   Security: External access blocked" -ForegroundColor Green
Write-Host "   Press Ctrl+C to stop" -ForegroundColor Red
Write-Host ""

try {
    # Start the secure Python server
    python local-security-config.py --host $BindHost --port $Port
} catch {
    Write-Host "❌ Error starting secure server: $_" -ForegroundColor Red
    Write-Host "   Please check the Python script and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to continue"
    exit 1
}
