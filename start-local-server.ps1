# Legacy Local HTTP Server Startup Script for Exo-Suit V5.0
# ⚠️  DEPRECATED: This script is replaced by start-secure-local-server.ps1

Write-Host "⚠️  DEPRECATED SCRIPT - MIGRATION REQUIRED" -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "This script has been replaced by the secure local server." -ForegroundColor Red
Write-Host "Please use the new secure version for maximum security." -ForegroundColor Green
Write-Host ""

Write-Host "🚀 MIGRATING TO SECURE SERVER..." -ForegroundColor Cyan
Write-Host ""

# Check if secure server script exists
$secureServerPath = Join-Path $PSScriptRoot "start-secure-local-server.ps1"
if (Test-Path $secureServerPath) {
    Write-Host "✅ Secure server script found" -ForegroundColor Green
    Write-Host "   Starting secure local server..." -ForegroundColor White
    Write-Host ""
    
    # Start the secure server instead
    & $secureServerPath
} else {
    Write-Host "❌ Secure server script not found" -ForegroundColor Red
    Write-Host "   Please ensure start-secure-local-server.ps1 exists" -ForegroundColor Yellow
    Write-Host ""
    
    # Fallback to basic server with security warning
    Write-Host "⚠️  FALLBACK: Starting basic server (less secure)" -ForegroundColor Yellow
    Write-Host "   This server allows external access - use with caution!" -ForegroundColor Red
    Write-Host ""
    
    # Change to script directory
    Set-Location $PSScriptRoot
    
    # Start basic Python HTTP server
    try {
        Write-Host "🚨 SECURITY WARNING: Basic server allows external access!" -ForegroundColor Red
        Write-Host "   Consider using start-secure-local-server.ps1 instead" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Starting basic HTTP server on port 8000..." -ForegroundColor Green
        Write-Host "Open your browser and go to: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Red
        Write-Host ""
        
        python -m http.server 8000
    } catch {
        Write-Host "❌ Error: Python not found or HTTP server failed to start" -ForegroundColor Red
        Write-Host "Make sure Python is installed and in your PATH" -ForegroundColor Yellow
        Read-Host "Press Enter to continue"
    }
}
