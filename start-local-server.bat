@echo off
REM Legacy Local HTTP Server Startup Script for Exo-Suit V5.0
REM ⚠️  DEPRECATED: This script is replaced by start-secure-local-server.bat

echo ⚠️  DEPRECATED SCRIPT - MIGRATION REQUIRED
echo =============================================
echo.
echo This script has been replaced by the secure local server.
echo Please use the new secure version for maximum security.
echo.

echo 🚀 MIGRATING TO SECURE SERVER...
echo.

REM Check if secure server script exists
if exist "start-secure-local-server.bat" (
    echo ✅ Secure server script found
    echo    Starting secure local server...
    echo.
    
    REM Start the secure server instead
    call start-secure-local-server.bat
    goto :end
) else (
    echo ❌ Secure server script not found
    echo    Please ensure start-secure-local-server.bat exists
    echo.
    
    REM Fallback to basic server with security warning
    echo ⚠️  FALLBACK: Starting basic server (less secure)
    echo    This server allows external access - use with caution!
    echo.
    
    REM Change to script directory
    cd /d "%~dp0"
    
    REM Start basic Python HTTP server
    echo 🚨 SECURITY WARNING: Basic server allows external access!
    echo    Consider using start-secure-local-server.bat instead
    echo.
    echo Starting basic HTTP server on port 8000...
    echo Open your browser and go to: http://localhost:8000
    echo Press Ctrl+C to stop
    echo.
    
    python -m http.server 8000
    
    if errorlevel 1 (
        echo.
        echo ❌ Error: Python not found or HTTP server failed to start
        echo Make sure Python is installed and in your PATH
        pause
    )
)

:end
pause
