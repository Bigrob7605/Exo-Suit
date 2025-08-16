@echo off
echo ========================================
echo ULTIMATE GPU STRESS TEST LAUNCHER
echo ========================================
echo.
echo This will PUSH your system to its limits!
echo.
echo Phase 1: ULTIMATE GPU Stress Test
echo Phase 2: Toolbox Token Processor
echo.
echo Press any key to start...
pause >nul

echo.
echo Creating logs directory...
if not exist "logs" mkdir logs

echo.
echo ========================================
echo PHASE 1: ULTIMATE GPU STRESS TEST
echo ========================================
echo Starting ULTIMATE stress test...
python ops/ULTIMATE-GPU-STRESS-TEST.py

echo.
echo ========================================
echo PHASE 2: TOOLBOX TOKEN PROCESSOR
echo ========================================
echo Starting toolbox processing...
python ops/TOOLBOX-TOKEN-PROCESSOR.py

echo.
echo ========================================
echo STRESS TESTING COMPLETE!
echo ========================================
echo.
echo Check the logs/ directory for results:
echo - ULTIMATE-GPU-STRESS-REPORT.md
echo - TOOLBOX-PROCESSING-REPORT.md
echo - processed_toolbox_data.json
echo.
echo Press any key to exit...
pause >nul
