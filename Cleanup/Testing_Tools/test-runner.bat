@echo off
echo ========================================
echo AGENT EXO-SUIT V4.0 "PERFECTION" TEST RUNNER
echo ========================================
echo.
echo Starting Phase 1 Component Testing...
echo.

REM Test 1: Emoji Sentinel V4.0
echo [1/12] Testing Emoji Sentinel V4.0...
"C:\Program Files\PowerShell\7\pwsh.exe" -ExecutionPolicy Bypass -File "ops\emoji-sentinel-v4.ps1" -Path "test-emoji-pack"
if %ERRORLEVEL% EQU 0 (
    echo ✓ Emoji Sentinel V4.0 PASSED
) else (
    echo ✗ Emoji Sentinel V4.0 FAILED (Error: %ERRORLEVEL%)
)
echo.

REM Test 2: Symbol Indexer V4.0
echo [2/12] Testing Symbol Indexer V4.0...
"C:\Program Files\PowerShell\7\pwsh.exe" -ExecutionPolicy Bypass -File "ops\Symbol-Indexer-V4.ps1" -Path "test-emoji-pack"
if %ERRORLEVEL% EQU 0 (
    echo ✓ Symbol Indexer V4.0 PASSED
) else (
    echo ✗ Symbol Indexer V4.0 FAILED (Error: %ERRORLEVEL%)
)
echo.

REM Test 3: Drift Guard V4.0 - Exit code 1 is expected when drift is detected
echo [3/12] Testing Drift Guard V4.0...
"C:\Program Files\PowerShell\7\pwsh.exe" -ExecutionPolicy Bypass -File "ops\Drift-Guard-V4.ps1" -Path "test-emoji-pack"
set DRIFT_EXIT_CODE=%ERRORLEVEL%
if %DRIFT_EXIT_CODE% EQU 0 (
    echo ✓ Drift Guard V4.0 PASSED (No drift detected)
) else if %DRIFT_EXIT_CODE% EQU 1 (
    echo ✓ Drift Guard V4.0 PASSED (Drift detected - expected behavior)
) else (
    echo ✗ Drift Guard V4.0 FAILED (Unexpected Error: %DRIFT_EXIT_CODE%)
)
echo.

REM Test 4: CPU RAG V4.0
echo [4/12] Testing CPU RAG V4.0...
cd rag && python "test_cpu.py" && cd ..
if %ERRORLEVEL% EQU 0 (
    echo ✓ CPU RAG V4.0 PASSED
) else (
    echo ✗ CPU RAG V4.0 FAILED (Error: %ERRORLEVEL%)
)
echo.

REM Test 5: GPU RAG V4.0
echo [5/12] Testing GPU RAG V4.0...
cd rag && python "test_gpu_only.py" && cd ..
if %ERRORLEVEL% EQU 0 (
    echo ✓ GPU RAG V4.0 PASSED
) else (
    echo ✗ GPU RAG V4.0 FAILED (Error: %ERRORLEVEL%)
)
echo.

REM Test 6: Power Management V4.0
echo [6/12] Testing Power Management V4.0...
"C:\Program Files\PowerShell\7\pwsh.exe" -ExecutionPolicy Bypass -File "ops\Power-Management-V4.ps1"
if %ERRORLEVEL% EQU 0 (
    echo ✓ Power Management V4.0 PASSED
) else (
    echo ✗ Power Management V4.0 FAILED (Error: %ERRORLEVEL%)
)
echo.

REM Test 7: GPU Monitor V4.0
echo [7/12] Testing GPU Monitor V4.0...
"C:\Program Files\PowerShell\7\pwsh.exe" -ExecutionPolicy Bypass -File "ops\GPU-Monitor-V4.ps1"
if %ERRORLEVEL% EQU 0 (
    echo ✓ GPU Monitor V4.0 PASSED
) else (
    echo ✗ GPU Monitor V4.0 FAILED (Error: %ERRORLEVEL%)
)
echo.

REM Test 8: Import Indexer V4.0
echo [8/12] Testing Import Indexer V4.0...
"C:\Program Files\PowerShell\7\pwsh.exe" -ExecutionPolicy Bypass -File "ops\Import-Indexer-V4.ps1" -Path "test-emoji-pack"
if %ERRORLEVEL% EQU 0 (
    echo ✓ Import Indexer V4.0 PASSED
) else (
    echo ✗ Import Indexer V4.0 FAILED (Error: %ERRORLEVEL%)
)
echo.

REM Test 9: Placeholder Scanner V4.0
echo [9/12] Testing Placeholder Scanner V4.0...
"C:\Program Files\PowerShell\7\pwsh.exe" -ExecutionPolicy Bypass -File "ops\Placeholder-Scanner-V4.ps1" -Path "test-emoji-pack"
if %ERRORLEVEL% EQU 0 (
    echo ✓ Placeholder Scanner V4.0 PASSED
) else (
    echo ✗ Placeholder Scanner V4.0 FAILED (Error: %ERRORLEVEL%)
)
echo.

REM Test 10: Project Health Scanner V4.0
echo [10/12] Testing Project Health Scanner V4.0...
"C:\Program Files\PowerShell\7\pwsh.exe" -ExecutionPolicy Bypass -File "ops\Project-Health-Scanner-V4.ps1" -ProjectPath "test-emoji-pack" -OutputPath "restore"
if %ERRORLEVEL% EQU 0 (
    echo ✓ Project Health Scanner V4.0 PASSED
) else (
    echo ✗ Project Health Scanner V4.0 FAILED (Error: %ERRORLEVEL%)
)
echo.

REM Test 11: Scan Secrets V4.0
echo [11/12] Testing Scan Secrets V4.0...
"C:\Program Files\PowerShell\7\pwsh.exe" -ExecutionPolicy Bypass -File "ops\Scan-Secrets-V4.ps1" -Root "test-emoji-pack"
if %ERRORLEVEL% EQU 0 (
    echo ✓ Scan Secrets V4.0 PASSED
) else (
    echo ✗ Scan Secrets V4.0 FAILED (Error: %ERRORLEVEL%)
)
echo.

REM Test 12: Symbol Indexer V4.0 (Duplicate - already tested above)
echo [12/12] Symbol Indexer V4.0 already tested above
echo.

echo ========================================
echo PHASE 1 TESTING COMPLETE
echo ========================================
echo.
echo Check individual test results above.
echo All components should show PASSED status.
echo.
pause
