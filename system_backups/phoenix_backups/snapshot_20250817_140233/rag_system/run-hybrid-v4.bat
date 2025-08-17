@echo off
REM Agent Exo-Suit V4.0 - Enhanced Hybrid CPU+GPU RAG System
REM Windows Batch File Runner

echo.
echo ================================================================
echo    Agent Exo-Suit V4.0 - Enhanced Hybrid CPU+GPU RAG System
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "hybrid_rag_v4.py" (
    echo ERROR: hybrid_rag_v4.py not found
    echo Please run this script from the rag/ directory
    pause
    exit /b 1
)

REM Show menu
echo Available modes:
echo 1. Test - Run comprehensive test suite
echo 2. Build - Build RAG index from documents
echo 3. Search - Search existing index
echo 4. Benchmark - Performance benchmark
echo 5. Monitor - System resource monitoring
echo.

set /p choice="Select mode (1-5): "

REM Execute based on choice
if "%choice%"=="1" (
    echo Running comprehensive test suite...
    python test_hybrid_comprehensive_v4.py
) else if "%choice%"=="2" (
    set /p input_dir="Input directory (default: .): "
    if "%input_dir%"=="" set input_dir=.
    set /p batch_size="Batch size (default: 32): "
    if "%batch_size%"=="" set batch_size=32
    echo Building RAG index from %input_dir% with batch size %batch_size%...
    python hybrid_rag_v4.py --mode build --input "%input_dir%" --batch-size %batch_size%
) else if "%choice%"=="3" (
    set /p query="Search query: "
    if "%query%"=="" (
        echo ERROR: Query is required for search mode
        pause
        exit /b 1
    )
    set /p top_k="Top K results (default: 5): "
    if "%top_k%"=="" set top_k=5
    echo Searching for: %query%
    python hybrid_rag_v4.py --mode search --query "%query%" --top-k %top_k%
) else if "%choice%"=="4" (
    echo Running performance benchmark...
    python test_hybrid_comprehensive_v4.py --benchmark
) else if "%choice%"=="5" (
    echo Starting system resource monitoring...
    echo Press Ctrl+C to stop monitoring
    python -c "import psutil, time; print('Monitoring started...'); [print(f'CPU: {psutil.cpu_percent()}%% | Memory: {psutil.virtual_memory().percent}%%') or time.sleep(2) for _ in iter(int, 1)]"
) else (
    echo Invalid choice: %choice%
    echo Please select 1-5
    pause
    exit /b 1
)

echo.
echo Operation completed!
pause
