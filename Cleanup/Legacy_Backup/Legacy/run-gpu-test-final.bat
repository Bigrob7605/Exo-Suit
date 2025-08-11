@echo off
echo ========================================
echo Agent Exo-Suit V4.0 - GPU Test Runner
echo ========================================
echo.
echo Running comprehensive GPU test...
echo.

cd /d "C:\My Projects\Agent Exo-Suit"
powershell -ExecutionPolicy Bypass -File "test-gpu-final.ps1"

echo.
echo ========================================
echo GPU Test Complete!
echo ========================================
echo.
echo Check the results above for any issues.
echo If all tests show ✅, GPU is working!
echo.
pause
