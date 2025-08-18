@echo off
:: ============================================================
::  MMH-RS Enhanced Human Launcher  v2.1  (10-DOCULOCK SYNCED)
::  Universal Digital DNA Format - Version 1.2.5
:: ============================================================
::  • 10-DOCULOCK System Compliant
::  • Future-Ready Versioning System
::  • Real AI Data Integration
::  • Enhanced Local Testing
::  • Core-Specific Operations
:: ============================================================

setlocal EnableExtensions EnableDelayedExpansion
title MMH-RS Enhanced Launcher v2.1 - 10-DOCULOCK System
pushd "%~dp0"

:: ---------- ANSI colour support ----------
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
    set "ESC=%%b"
)
set "BOLD=%ESC%[1m"
set "RESET=%ESC%[0m"
set "RED=%ESC%[91m"
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "BLUE=%ESC%[94m"
set "CYAN=%ESC%[96m"
set "MAGENTA=%ESC%[95m"

:: ---------- Utility functions ----------
:PAUSE_MSG
if not "%~1"=="" echo(
echo %GREEN%✔ %~1%RESET%
pause >nul
goto :eof

:INVALID_CHOICE
echo(
echo %RED%✖ Invalid choice, please try again.%RESET%
timeout /t 2 >nul
goto :eof

:: ---------- Cargo sanity check ----------
where cargo >nul 2>&1 || (
    echo %RED%Cargo/Rust not found in PATH.%RESET%
    echo %YELLOW%Install it from https://rustup.rs then re-run.%RESET%
    pause
    exit /b 1
)

:: ---------- Main menu ----------
:MAIN_MENU
cls
echo(
echo %CYAN%┌────────────────────────────────────────────────────────────┐%RESET%
echo %CYAN%│%RESET% %BOLD%MMH-RS Enhanced Launcher v2.1%RESET%                    %CYAN%│%RESET%
echo %CYAN%│%RESET% Universal Digital DNA Format - Version 1.2.5          %CYAN%│%RESET%
echo %CYAN%│%RESET% 10-DOCULOCK System Compliant                          %CYAN%│%RESET%
echo %CYAN%├────────────────────────────────────────────────────────────┤%RESET%
echo %CYAN%│%RESET% %BOLD%🎯 Select Launch Option:%RESET%                             %CYAN%│%RESET%
echo %CYAN%│%RESET%                                                            %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%1%RESET%. 🚀 Interactive Menu (3-Core System)              %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%2%RESET%. ⚡ Quick System Test (100 MB Validation)         %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%3%RESET%. 🔧 Comprehensive System Test (Full Validation)   %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%4%RESET%. 📊 7-Tier Benchmark System (50MB → 32GB)         %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%5%RESET%. 🤖 Agent System (6 Options)                      %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%6%RESET%. 🧪 Real AI Tensor Testing                        %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%7%RESET%. 🗂️  File Operations (Pack/Unpack/Verify)         %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%8%RESET%. 🎛️  Custom Command (Direct CLI Access)           %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%9%RESET%. ℹ️  System Information                            %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%10%RESET%. 📖 About MMH-RS (10-DOCULOCK System)            %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%11%RESET%. 🔄 Core-Specific Operations                     %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%0%RESET%. 🚪 Exit                                            %CYAN%│%RESET%
echo %CYAN%├────────────────────────────────────────────────────────────┤%RESET%
echo %CYAN%│%RESET% %YELLOW%💡 Tip: Press Ctrl+C at any time to abort operations%RESET%  %CYAN%│%RESET%
echo %CYAN%│%RESET% %YELLOW%📚 10-DOCULOCK System: 5 PDFs + 5 MDs = 10 Documents%RESET% %CYAN%│%RESET%
echo %CYAN%└────────────────────────────────────────────────────────────┘%RESET%
set /p choice=%BOLD%Enter your choice:%RESET% || goto MAIN_MENU
choice /c 1234567890a /n /m "" >nul 2>nul || goto INVALID_CHOICE
if "%choice%"=="a" set choice=10
if "%choice%"=="0" set choice=12
goto OPTION_%choice%

:OPTION_1
echo(
echo %GREEN%🚀 Starting MMH-RS Interactive Menu (3-Core System)...%RESET%
cargo run --release
call :PAUSE_MSG "Interactive menu closed."
goto MAIN_MENU

:OPTION_2
echo(
echo %GREEN%⚡ Running Quick System Test (100 MB Validation)...%RESET%
cargo run --release -- --quick-system-test
call :PAUSE_MSG "Quick test finished."
goto MAIN_MENU

:OPTION_3
echo(
echo %GREEN%🔧 Running Comprehensive System Test (Full Validation)...%RESET%
cargo run --release -- --comprehensive-system-test
call :PAUSE_MSG "Comprehensive test finished."
goto MAIN_MENU

:OPTION_4
echo(
echo %GREEN%📊 Launching 7-Tier Benchmark System...%RESET%
echo %YELLOW%Available tiers: Smoke(50MB) → Tier1(100MB) → Tier2(1GB) → Tier3(2GB) → Tier4(4GB) → Tier5(8GB) → Tier6(16GB) → Tier7(32GB)%RESET%
cargo run --release
call :PAUSE_MSG "Benchmark system closed."
goto MAIN_MENU

:OPTION_5
echo(
echo %GREEN%🤖 Launching Agent System...%RESET%
cargo run --release
call :PAUSE_MSG "Agent system closed."
goto MAIN_MENU

:OPTION_6
echo(
echo %GREEN%🧪 Launching Real AI Tensor Testing...%RESET%
echo %YELLOW%Testing with real safetensors files from test_data/ and cores/core1_cpu_hdd/real_tensors/%RESET%
cargo run --release
call :PAUSE_MSG "Real AI tensor testing closed."
goto MAIN_MENU

:OPTION_7
call :FILE_MENU
goto MAIN_MENU

:OPTION_8
echo(
echo %GREEN%🎛️  Custom Command Access%RESET%
set /p custom_cmd=%BOLD%Enter MMH-RS command:%RESET% 
cargo run --release %custom_cmd%
call :PAUSE_MSG "Custom command finished."
goto MAIN_MENU

:OPTION_9
echo(
echo %GREEN%ℹ️  System Information%RESET%
cargo run --release -- --cpu-hdd
call :PAUSE_MSG "System info displayed."
goto MAIN_MENU

:OPTION_10
echo(
echo %GREEN%📖 About MMH-RS (10-DOCULOCK System)%RESET%
cargo run --release -- --about
call :PAUSE_MSG "About info displayed."
goto MAIN_MENU

:OPTION_11
call :CORE_SPECIFIC_MENU
goto MAIN_MENU

:OPTION_12
echo(
echo %GREEN%👋 Thank you for using MMH-RS Enhanced Launcher!%RESET%
echo %GREEN%🚀 Universal Digital DNA Format - v2.1%RESET%
echo %GREEN%📚 10-DOCULOCK System - Never more than 10 documents!%RESET%
timeout 2 >nul
exit /b 0

:: ---------- Core-specific operations sub-menu ----------
:CORE_SPECIFIC_MENU
cls
echo(
echo %CYAN%┌────────────────────────────────────────────────────────────┐%RESET%
echo %CYAN%│%RESET% %BOLD%🔄 Core-Specific Operations%RESET%                           %CYAN%│%RESET%
echo %CYAN%├────────────────────────────────────────────────────────────┤%RESET%
echo %CYAN%│%RESET% %GREEN%1%RESET%. 🖥️  Core 1 (CPU+HDD) - V1.2.5 STABLE ✅         %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%2%RESET%. 🎮 Core 2 (GPU+HDD) - V2.0 MEGA-BOOST 🚀        %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%3%RESET%. 🔄 Core 3 (GPU+CPU+HDD) - V3.0 Future 🚧        %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%4%RESET%. 📊 Run Core 1 Python Benchmarks Directly         %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%5%RESET%. 🧪 Run Core 1 Real Tensor System Directly        %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%6%RESET%. 🔍 Check Available Test Files                   %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%0%RESET%. 🔙 Back to Main Menu                             %CYAN%│%RESET%
echo %CYAN%└────────────────────────────────────────────────────────────┘%RESET%
set /p core_choice=%BOLD%Enter your choice:%RESET% || goto CORE_SPECIFIC_MENU
choice /c 1234560 /n /m "" >nul 2>nul || goto INVALID_CHOICE
goto CORE_%core_choice%

:CORE_1
echo(
echo %GREEN%🖥️  Launching Core 1 (CPU+HDD) - V1.2.5 STABLE ✅%RESET%
cargo run --release -- --cpu-hdd
call :PAUSE_MSG "Core 1 operations finished."
goto CORE_SPECIFIC_MENU

:CORE_2
echo(
echo %GREEN%🎮 Launching Core 2 (GPU+HDD) - V2.0 MEGA-BOOST 🚀%RESET%
cargo run --release -- --gpu-hdd
call :PAUSE_MSG "Core 2 operations finished."
goto CORE_SPECIFIC_MENU

:CORE_3
echo(
echo %GREEN%🔄 Launching Core 3 (GPU+CPU+HDD) - V3.0 Future 🚧%RESET%
cargo run --release -- --gpu-cpu-hdd
call :PAUSE_MSG "Core 3 operations finished."
goto CORE_SPECIFIC_MENU

:CORE_4
echo(
echo %GREEN%📊 Running Core 1 Python Benchmarks Directly...%RESET%
echo %YELLOW%Available commands: smoke, tier1, tier2, tier3, tier4, tier5, tier6, tier7, all%RESET%
set /p benchmark_cmd=%BOLD%Enter benchmark command (e.g., smoke, tier1, all):%RESET% 
python cores/core1_cpu_hdd/core1_benchmark_system.py %benchmark_cmd%
call :PAUSE_MSG "Core 1 benchmarks finished."
goto CORE_SPECIFIC_MENU

:CORE_5
echo(
echo %GREEN%🧪 Running Core 1 Real Tensor System Directly...%RESET%
echo %YELLOW%Available commands: info, create_smoke_test_file, create_tier_test_files%RESET%
set /p tensor_cmd=%BOLD%Enter tensor command:%RESET% 
python cores/core1_cpu_hdd/core1_real_tensor_system.py %tensor_cmd%
call :PAUSE_MSG "Core 1 real tensor operations finished."
goto CORE_SPECIFIC_MENU

:CORE_6
echo(
echo %GREEN%🔍 Checking Available Test Files...%RESET%
echo %CYAN%📁 test_data/ directory:%RESET%
dir test_data\*.safetensors 2>nul || echo %RED%No safetensors files found in test_data/%RESET%
echo.
echo %CYAN%📁 cores/core1_cpu_hdd/real_tensors/ directory:%RESET%
dir cores\core1_cpu_hdd\real_tensors\*.safetensors 2>nul || echo %RED%No safetensors files found in real_tensors/%RESET%
echo.
echo %YELLOW%💡 Ready for testing with real AI tensor data!%RESET%
call :PAUSE_MSG "File check completed."
goto CORE_SPECIFIC_MENU

:CORE_0
goto :eof

:: ---------- File-operations sub-menu ----------
:FILE_MENU
cls
echo(
echo %CYAN%┌────────────────────────────────────────────────────────────┐%RESET%
echo %CYAN%│%RESET% %BOLD%🗂️  File Operations Menu%RESET%                             %CYAN%│%RESET%
echo %CYAN%├────────────────────────────────────────────────────────────┤%RESET%
echo %CYAN%│%RESET% %GREEN%1%RESET%. 📦 Pack File                                        %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%2%RESET%. 📤 Unpack File                                      %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%3%RESET%. ✅ Verify File Integrity                            %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%4%RESET%. 🧪 Generate Test Data                               %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%5%RESET%. 🔍 Quick File Test (Use Available Files)           %CYAN%│%RESET%
echo %CYAN%│%RESET% %GREEN%0%RESET%. 🔙 Back to Main Menu                                %CYAN%│%RESET%
echo %CYAN%└────────────────────────────────────────────────────────────┘%RESET%
set /p file_choice=%BOLD%Enter your choice:%RESET% || goto FILE_MENU
choice /c 123450 /n /m "" >nul 2>nul || goto INVALID_CHOICE
goto FILE_%file_choice%

:FILE_1
set /p input_file=%BOLD%Input file path:%RESET% 
set /p output_file=%BOLD%Output file path:%RESET% 
cargo run --release -- pack "%input_file%" "%output_file%"
call :PAUSE_MSG "Pack operation complete."
goto FILE_MENU

:FILE_2
set /p input_file=%BOLD%Input file path:%RESET% 
set /p output_file=%BOLD%Output file path:%RESET% 
cargo run --release -- unpack "%input_file%" "%output_file%"
call :PAUSE_MSG "Unpack operation complete."
goto FILE_MENU

:FILE_3
set /p original=%BOLD%Original file path:%RESET% 
set /p restored=%BOLD%Restored file path:%RESET% 
cargo run --release -- verify "%original%" "%restored%"
call :PAUSE_MSG "Verify operation complete."
goto FILE_MENU

:FILE_4
set /p output_file=%BOLD%Output file path:%RESET% 
set /p size_mb=%BOLD%Size in MB:%RESET% 
cargo run --release -- gen "%output_file%" %size_mb%
call :PAUSE_MSG "Test data generated."
goto FILE_MENU

:FILE_5
echo(
echo %GREEN%🔍 Quick File Test with Available Files%RESET%
echo %YELLOW%This will test with files from test_data/ and real_tensors/%RESET%
echo.
echo %CYAN%Available test files:%RESET%
dir test_data\*.safetensors 2>nul || echo %RED%No files in test_data/%RESET%
dir cores\core1_cpu_hdd\real_tensors\*.safetensors 2>nul || echo %RED%No files in real_tensors/%RESET%
echo.
set /p test_file=%BOLD%Enter file path to test (or press Enter for default):%RESET% 
if "%test_file%"=="" set test_file=test_data\test_100mb.safetensors
if exist "%test_file%" (
    echo %GREEN%Testing with: %test_file%%RESET%
    set output_file=%test_file%.mmh
    cargo run --release -- pack "%test_file%" "%output_file%"
    echo.
    echo %GREEN%Unpacking for verification...%RESET%
    set restored_file=%test_file%.restored.safetensors
    cargo run --release -- unpack "%output_file%" "%restored_file%"
    echo.
    echo %GREEN%Verifying integrity...%RESET%
    cargo run --release -- verify "%test_file%" "%restored_file%"
    echo.
    echo %GREEN%✅ Quick file test completed!%RESET%
) else (
    echo %RED%❌ File not found: %test_file%%RESET%
)
call :PAUSE_MSG "Quick file test finished."
goto FILE_MENU

:FILE_0
goto :eof 