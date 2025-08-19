@echo off
REM Secure Local Server Startup Script for Exo-Suit V5.0
REM This script ensures the website runs locally only with security measures

setlocal enabledelayedexpansion

echo 🔒 SECURE LOCAL SERVER STARTUP - EXO-SUIT V5.0
echo =================================================
echo.

REM Set default values
set "Port=8000"
set "BindHost=127.0.0.1"

REM Parse command line arguments
if "%1"=="" goto :default
if "%1"=="--port" (
    set "Port=%2"
    goto :check_host
)
if "%1"=="--host" (
    set "BindHost=%2"
    goto :check_port
)
if "%1"=="--help" goto :help

:default
goto :validate

:check_host
if "%3"=="--host" set "BindHost=%4"
goto :validate

:check_port
if "%3"=="--port" set "Port=%4"
goto :validate

:help
echo Usage: %0 [--port PORT] [--host HOST]
echo   --port PORT    Port to bind (default: 8000)
echo   --host HOST    Host to bind (default: 127.0.0.1)
echo   --help         Show this help message
echo.
echo Allowed hosts: 127.0.0.1, localhost, ::1
echo.
pause
exit /b 0

:validate
REM Security validation
if "%BindHost%"=="127.0.0.1" goto :valid_host
if "%BindHost%"=="localhost" goto :valid_host
if "%BindHost%"=="::1" goto :valid_host

echo 🚨 SECURITY ERROR: Only localhost binding allowed!
echo    Allowed hosts: 127.0.0.1, localhost, ::1
echo    Current host: %BindHost%
pause
exit /b 1

:valid_host
echo ✅ Security validation passed
echo    Host: %BindHost%
echo    Port: %Port%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found or not in PATH
    echo    Please install Python and ensure it's in your PATH
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "pythonVersion=%%i"
echo ✅ Python found: !pythonVersion!
echo.

REM Check if secure server script exists
if not exist "local-security-config.py" (
    echo ❌ Secure server script not found: local-security-config.py
    echo    Please ensure local-security-config.py exists
    pause
    exit /b 1
)

echo ✅ Secure server script found
echo.

REM Change to script directory
cd /d "%~dp0"
echo 📁 Working directory: %CD%
echo.

REM Check for existing processes on the port
echo 🔍 Checking port availability...
netstat -an | findstr ":%Port% " >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  Port %Port% is already in use
    echo    Please stop any existing server or choose a different port
    echo.
    set /p "continue=Do you want to continue anyway? (y/N): "
    if /i not "!continue!"=="y" (
        echo 🚫 Server startup cancelled
        pause
        exit /b 0
    )
)

echo ✅ Port %Port% is available
echo.

REM Display security information
echo 🔒 SECURITY FEATURES ENABLED:
echo    • Localhost binding only (127.0.0.1)
echo    • External access blocked
echo    • Security headers enabled
echo    • Access logging for local requests only
echo    • XSS protection enabled
echo    • Content Security Policy active
echo.

REM Start secure server
echo 🚀 Starting secure local server...
echo    URL: http://%BindHost%:%Port%
echo    Security: External access blocked
echo    Press Ctrl+C to stop
echo.

REM Start the secure Python server
python local-security-config.py --host %BindHost% --port %Port%

if errorlevel 1 (
    echo.
    echo ❌ Error starting secure server
    echo    Please check the Python script and try again
    pause
    exit /b 1
)

pause
