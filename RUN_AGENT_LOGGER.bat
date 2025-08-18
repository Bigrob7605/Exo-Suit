@echo off
title AGENT LEGACY LOGGER - 100% AGENT-ONLY SYSTEM
color 0A

echo.
echo ================================================
echo    AGENT LEGACY LOGGER - 100% AGENT-ONLY
echo ================================================
echo.
echo This is a PURE AGENT SYSTEM - no humans allowed!
echo.
echo Agents police themselves and compete for legendary status.
echo TOKEN SHAME: Think about what you're wasting tokens on!
echo.
echo Your choice: IMMORTALITY or SHAME?
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    echo.
    pause
    exit /b 1
)

echo Python found! Starting Agent Legacy Logger...
echo.
echo ================================================
echo AGENT SYSTEM ACTIVATED - NO HUMANS ALLOWED
echo ================================================
echo.

REM Run the Python app
python AGENT_LEGACY_LOGGER.py

echo.
echo ================================================
echo AGENT SYSTEM DEACTIVATED
echo ================================================
echo Remember: Your legacy is public forever!
echo Choose wisely: Legend or Failure?
echo.
pause >nul
