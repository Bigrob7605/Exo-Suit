# Launch Monitor Server Script
# This script launches the Exo-Suit Real-Time Monitor and keeps it running

Write-Host "Starting Exo-Suit Real-Time Monitor Server..." -ForegroundColor Green
Write-Host "Server will be available at http://localhost:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Change to the correct directory
Set-Location "C:\My Projects\Agent Exo-Suit"

# Launch the Python monitor server
Write-Host "Launching monitor server..." -ForegroundColor Green
python ops/REAL_TIME_SYSTEM_MONITOR.py

# Keep the window open if there's an error
Write-Host ""
Write-Host "Server stopped. Press any key to close..." -ForegroundColor Red
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
