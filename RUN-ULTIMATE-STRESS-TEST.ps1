#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ULTIMATE GPU STRESS TEST LAUNCHER - Phase 3 Token Upgrade
    
.DESCRIPTION
    This script will PUSH your system to its absolute limits and find the perfect 1M token balance.
    It runs both the ULTIMATE GPU stress test and the toolbox token processor.
    
.NOTES
    Author: Agent Exo-Suit V5.0
    Version: 1.0
    Date: 2025-08-13
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ULTIMATE GPU STRESS TEST LAUNCHER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will PUSH your system to its limits!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Phase 1: ULTIMATE GPU Stress Test" -ForegroundColor Green
Write-Host "Phase 2: Toolbox Token Processor" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to start..." -ForegroundColor White
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "Creating logs directory..." -ForegroundColor Blue
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    Write-Host "Logs directory created." -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PHASE 1: ULTIMATE GPU STRESS TEST" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting ULTIMATE stress test..." -ForegroundColor Green

try {
    $startTime = Get-Date
    python ops/ULTIMATE-GPU-STRESS-TEST.py
    $phase1Duration = (Get-Date) - $startTime
    Write-Host "Phase 1 completed in $($phase1Duration.TotalSeconds.ToString('F1')) seconds" -ForegroundColor Green
} catch {
    Write-Host "Phase 1 failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PHASE 2: TOOLBOX TOKEN PROCESSOR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting toolbox processing..." -ForegroundColor Green

try {
    $startTime = Get-Date
    python ops/TOOLBOX-TOKEN-PROCESSOR.py
    $phase2Duration = (Get-Date) - $startTime
    Write-Host "Phase 2 completed in $($phase2Duration.TotalSeconds.ToString('F1')) seconds" -ForegroundColor Green
} catch {
    Write-Host "Phase 2 failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$totalDuration = $phase1Duration + $phase2Duration

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STRESS TESTING COMPLETE!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total Duration: $($totalDuration.TotalSeconds.ToString('F1')) seconds" -ForegroundColor Yellow
Write-Host ""
Write-Host "Check the logs/ directory for results:" -ForegroundColor White
Write-Host "- ULTIMATE-GPU-STRESS-REPORT.md" -ForegroundColor Gray
Write-Host "- TOOLBOX-PROCESSING-REPORT.md" -ForegroundColor Gray
Write-Host "- processed_toolbox_data.json" -ForegroundColor Gray
Write-Host ""

# Check if reports were generated
$reports = @(
    "logs/ULTIMATE-GPU-STRESS-REPORT.md",
    "logs/TOOLBOX-PROCESSING-REPORT.md",
    "logs/processed_toolbox_data.json"
)

Write-Host "Generated Reports:" -ForegroundColor Blue
foreach ($report in $reports) {
    if (Test-Path $report) {
        $size = (Get-Item $report).Length
        $sizeKB = [math]::Round($size / 1KB, 2)
        Write-Host " $report ($sizeKB KB)" -ForegroundColor Green
    } else {
        Write-Host " $report (MISSING)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor White
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
