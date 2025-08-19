# Start Local HTTP Server for Exo-Suit Modular Webpage
Write-Host "Starting Local HTTP Server for Exo-Suit Modular Webpage..." -ForegroundColor Green
Write-Host ""
Write-Host "This will start a simple HTTP server on port 8000" -ForegroundColor Yellow
Write-Host "Open your browser and go to: http://localhost:8000/index-modular.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Start Python HTTP server
try {
    python -m http.server 8000
} catch {
    Write-Host "Error: Python not found or HTTP server failed to start" -ForegroundColor Red
    Write-Host "Make sure Python is installed and in your PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to continue"
}
