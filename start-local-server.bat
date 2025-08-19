@echo off
echo Starting Local HTTP Server for Exo-Suit Modular Webpage...
echo.
echo This will start a simple HTTP server on port 8000
echo Open your browser and go to: http://localhost:8000/index-modular.html
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
python -m http.server 8000

pause
