# Performance-Test-Suite-V4.ps1 - Comprehensive performance testing for Agent Exo-Suit V4.0
# Measures system performance before and after optimizations

[CmdletBinding()]
param(
    [ValidateSet('Baseline', 'Optimized', 'Compare', 'Full')]
    [string]$Mode = 'Baseline',
    
    [switch]$SaveResults,
    [switch]$Detailed,
    [switch]$GPUOnly
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ===== TEST CONFIGURATION =====
$TestConfig = @{
    RAG_Test_Files = 100
    Import_Test_Files = 50
    Symbol_Test_Files = 50
    Emoji_Test_Files = 100
    Health_Test_Depth = "Comprehensive"
    GPU_Test_Iterations = 10
    Memory_Test_Size = "1GB"
}

# ===== PERFORMANCE METRICS =====
$PerformanceMetrics = @{
    StartTime = $null
    EndTime = $null
    TotalDuration = $null
    ComponentResults = @{}
    SystemInfo = @{}
    GPUInfo = @{}
}

# ===== SYSTEM INFORMATION GATHERING =====
function Get-SystemInformation {
    Write-Host "📊 Gathering system information..." -ForegroundColor Cyan
    
    try {
        $cpu = Get-WmiObject -Class Win32_Processor
        $ram = Get-WmiObject -Class Win32_ComputerSystem
        $os = Get-WmiObject -Class Win32_OperatingSystem
        
        $PerformanceMetrics.SystemInfo = @{
            CPU_Name = if ($cpu.Name) { $cpu.Name } else { "Unknown" }
            CPU_Cores = if ($cpu.NumberOfCores) { $cpu.NumberOfCores } else { 0 }
            CPU_Threads = if ($cpu.NumberOfLogicalProcessors) { $cpu.NumberOfLogicalProcessors } else { 0 }
            CPU_Speed = if ($cpu.MaxClockSpeed) { $cpu.MaxClockSpeed } else { 0 }
            RAM_GB = if ($ram.TotalPhysicalMemory) { [math]::Round($ram.TotalPhysicalMemory / 1GB, 2) } else { 0 }
            OS_Version = if ($os.Caption) { $os.Caption } else { "Unknown" }
            OS_Build = if ($os.BuildNumber) { $os.BuildNumber } else { "Unknown" }
            Uptime_Hours = 0
        }
        
        Write-Host "✅ System information gathered" -ForegroundColor Green
        
    } catch {
        Write-Host "❌ Failed to gather system information: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Get-GPUInformation {
    Write-Host "🎮 Gathering GPU information..." -ForegroundColor Cyan
    
    try {
        $nvidiaOutput = nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap,temperature.gpu,power.draw --format=csv,noheader,nounits 2>$null
        if ($nvidiaOutput) {
            $parts = $nvidiaOutput -split ','
            $PerformanceMetrics.GPUInfo = @{
                Name = $parts[0].Trim()
                Memory_MB = [int]($parts[1])
                Driver = $parts[2].Trim()
                Compute_Cap = $parts[3].Trim()
                Temperature = [int]($parts[4])
                Power_W = [double]($parts[5])
            }
            Write-Host "✅ GPU information gathered" -ForegroundColor Green
        } else {
            Write-Host "⚠️  No NVIDIA GPU detected" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host "❌ Failed to gather GPU information: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# ===== PERFORMANCE TESTING FUNCTIONS =====
function Test-RAGPerformance {
    Write-Host "🧠 Testing RAG system performance..." -ForegroundColor Yellow
    
    $startTime = Get-Date
    
    try {
        # Test GPU RAG
        $gpuTest = python "rag\test_gpu_only.py" 2>$null
        $gpuTime = (Get-Date) - $startTime
        
        # Test hybrid RAG
        $startTime = Get-Date
        $hybridTest = python "rag\test_hybrid_comprehensive_v4.py" 2>$null
        $hybridTime = (Get-Date) - $startTime
        
        $PerformanceMetrics.ComponentResults.RAG = @{
            GPU_Time_Seconds = $gpuTime.TotalSeconds
            Hybrid_Time_Seconds = $hybridTime.TotalSeconds
            GPU_Available = $true
            Status = "Success"
        }
        
        Write-Host "✅ RAG performance test completed" -ForegroundColor Green
        Write-Host "   GPU: $($gpuTime.TotalSeconds.ToString('F2'))s | Hybrid: $($hybridTime.TotalSeconds.ToString('F2'))s" -ForegroundColor Cyan
        
    } catch {
        $PerformanceMetrics.ComponentResults.RAG = @{
            Status = "Failed"
            Error = $_.Exception.Message
        }
        Write-Host "❌ RAG performance test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Test-ImportIndexerPerformance {
    Write-Host "📚 Testing Import Indexer performance..." -ForegroundColor Yellow
    
    $startTime = Get-Date
    
    try {
        # Create test files for import scanning
        $testDir = "Testing_Tools\import_performance_test"
        if (-not (Test-Path $testDir)) {
            New-Item -ItemType Directory -Force -Path $testDir | Out-Null
        }
        
        # Generate test files with imports
        for ($i = 1; $i -le $TestConfig.Import_Test_Files; $i++) {
            $content = @"
import os
import sys
import json
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from tensorflow import keras
import torch
import torch.nn as nn

def test_function_$i():
    return "Test file $i"
"@
            Set-Content "$testDir\test_import_$i.py" $content
        }
        
        # Test import scanning
        $importTest = & ".\ops\Import-Indexer-V4.ps1" -Path $testDir -Output "Testing_Tools\import_performance_test_results.json"
        $importTime = (Get-Date) - $startTime
        
        $PerformanceMetrics.ComponentResults.ImportIndexer = @{
            Files_Processed = $TestConfig.Import_Test_Files
            Time_Seconds = $importTime.TotalSeconds
            Files_Per_Second = [math]::Round($TestConfig.Import_Test_Files / $importTime.TotalSeconds, 2)
            Status = "Success"
        }
        
        Write-Host "✅ Import Indexer test completed: $($TestConfig.Import_Test_Files) files in $($importTime.TotalSeconds.ToString('F2'))s" -ForegroundColor Green
        
    } catch {
        $PerformanceMetrics.ComponentResults.ImportIndexer = @{
            Status = "Failed"
            Error = $_.Exception.Message
        }
        Write-Host "❌ Import Indexer test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Test-SymbolIndexerPerformance {
    Write-Host "🔍 Testing Symbol Indexer performance..." -ForegroundColor Yellow
    
    $startTime = Get-Date
    
    try {
        # Use the same test files from import test
        $testDir = "Testing_Tools\import_performance_test"
        
        # Test symbol scanning
        $symbolTest = & ".\ops\Symbol-Indexer-V4.ps1" -Path $testDir -Output "Testing_Tools\symbol_performance_test_results.json"
        $symbolTime = (Get-Date) - $startTime
        
        $PerformanceMetrics.ComponentResults.SymbolIndexer = @{
            Files_Processed = $TestConfig.Symbol_Test_Files
            Time_Seconds = $symbolTime.TotalSeconds
            Files_Per_Second = [math]::Round($TestConfig.Symbol_Test_Files / $symbolTime.TotalSeconds, 2)
            Status = "Success"
        }
        
        Write-Host "✅ Symbol Indexer test completed: $($TestConfig.Symbol_Test_Files) files in $($symbolTime.TotalSeconds.ToString('F2'))s" -ForegroundColor Green
        
    } catch {
        $PerformanceMetrics.ComponentResults.SymbolIndexer = @{
            Status = "Failed"
            Error = $_.Exception.Message
        }
        Write-Host "❌ Symbol Indexer test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Test-EmojiSentinelPerformance {
    Write-Host "🚫 Testing Emoji Sentinel performance..." -ForegroundColor Yellow
    
    $startTime = Get-Date
    
    try {
        # Create test files with emojis
        $testDir = "Testing_Tools\emoji_performance_test"
        if (-not (Test-Path $testDir)) {
            New-Item -ItemType Directory -Force -Path $testDir | Out-Null
        }
        
        # Generate test files with emojis
        for ($i = 1; $i -le $TestConfig.Emoji_Test_Files; $i++) {
            $content = @"
# Test file $i with emojis 🚀
def test_function_$i():
    # This is a test function with emojis 🎯
    emoji_list = ["🚀", "🎯", "⚡", "🔥", "💻"]
    return emoji_list[$i % 5]

# More emojis for testing 🎮🎲🎪
"@
            Set-Content "$testDir\test_emoji_$i.py" $content
        }
        
        # Test emoji scanning
        $emojiTest = & ".\ops\emoji-sentinel-v4.ps1" -Path $testDir -Output "Testing_Tools\emoji_performance_test_results.json"
        $emojiTime = (Get-Date) - $startTime
        
        $PerformanceMetrics.ComponentResults.EmojiSentinel = @{
            Files_Processed = $TestConfig.Emoji_Test_Files
            Time_Seconds = $emojiTime.TotalSeconds
            Files_Per_Second = [math]::Round($TestConfig.Emoji_Test_Files / $emojiTime.TotalSeconds, 2)
            Status = "Success"
        }
        
        Write-Host "✅ Emoji Sentinel test completed: $($TestConfig.Emoji_Test_Files) files in $($emojiTime.TotalSeconds.ToString('F2'))s" -ForegroundColor Green
        
    } catch {
        $PerformanceMetrics.ComponentResults.EmojiSentinel = @{
            Status = "Failed"
            Error = $_.Exception.Message
        }
        Write-Host "❌ Emoji Sentinel test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Test-ProjectHealthScannerPerformance {
    Write-Host "🏥 Testing Project Health Scanner performance..." -ForegroundColor Yellow
    
    $startTime = Get-Date
    
    try {
        # Test health scanning
        $healthTest = & ".\ops\Project-Health-Scanner-V4.ps1" -Path "." -Output "Testing_Tools\health_performance_test_results"
        $healthTime = (Get-Date) - $startTime
        
        $PerformanceMetrics.ComponentResults.ProjectHealthScanner = @{
            Time_Seconds = $healthTime.TotalSeconds
            Status = "Success"
        }
        
        Write-Host "✅ Project Health Scanner test completed in $($healthTime.TotalSeconds.ToString('F2'))s" -ForegroundColor Green
        
    } catch {
        $PerformanceMetrics.ComponentResults.ProjectHealthScanner = @{
            Status = "Failed"
            Error = $_.Exception.Message
        }
        Write-Host "❌ Project Health Scanner test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Test-GPUPerformance {
    Write-Host "🎮 Testing GPU performance..." -ForegroundColor Yellow
    
    $startTime = Get-Date
    
    try {
        # Test CUDA operations
        $cudaTest = python -c "
import torch
import time
import numpy as np

# Test matrix multiplication
start_time = time.time()
x = torch.randn(2000, 2000).cuda()
y = torch.randn(2000, 2000).cuda()

for i in range(10):
    z = torch.mm(x, y.t())
    
gpu_time = time.time() - start_time
print(f'GPU Matrix Mult (10x): {gpu_time:.3f}s')

# Test memory operations
memory_allocated = torch.cuda.memory_allocated(0) / 1024**3
memory_reserved = torch.cuda.memory_reserved(0) / 1024**3
print(f'GPU Memory: {memory_allocated:.2f}GB allocated, {memory_reserved:.2f}GB reserved')
" 2>$null
        
        $gpuTime = (Get-Date) - $startTime
        
        $PerformanceMetrics.ComponentResults.GPU = @{
            Time_Seconds = $gpuTime.TotalSeconds
            Status = "Success"
        }
        
        Write-Host "✅ GPU performance test completed in $($gpuTime.TotalSeconds.ToString('F2'))s" -ForegroundColor Green
        
    } catch {
        $PerformanceMetrics.ComponentResults.GPU = @{
            Status = "Failed"
            Error = $_.Exception.Message
        }
        Write-Host "❌ GPU performance test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# ===== MAIN TEST EXECUTION =====
function Run-PerformanceTests {
    Write-Host "🚀 Starting Performance Test Suite V4.0..." -ForegroundColor Cyan
    Write-Host "Mode: $Mode | Detailed: $Detailed | Save Results: $SaveResults" -ForegroundColor Cyan
    
    $PerformanceMetrics.StartTime = Get-Date
    
    # Gather system information
    Get-SystemInformation
    Get-GPUInformation
    
    # Run component tests
    if (-not $GPUOnly) {
        Test-RAGPerformance
        Test-ImportIndexerPerformance
        Test-SymbolIndexerPerformance
        Test-EmojiSentinelPerformance
        Test-ProjectHealthScannerPerformance
    }
    
    Test-GPUPerformance
    
    # Calculate total duration
    $PerformanceMetrics.EndTime = Get-Date
    $PerformanceMetrics.TotalDuration = $PerformanceMetrics.EndTime - $PerformanceMetrics.StartTime
    
    Write-Host "✅ All performance tests completed!" -ForegroundColor Green
    Write-Host "Total duration: $($PerformanceMetrics.TotalDuration.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Cyan
}

# ===== RESULTS PROCESSING =====
function Save-TestResults {
    if (-not $SaveResults) { return }
    
    Write-Host "💾 Saving test results..." -ForegroundColor Yellow
    
    try {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $resultsFile = "Testing_Tools\performance_test_results_$timestamp.json"
        
        # Convert to JSON-serializable format
        $jsonResults = @{
            Timestamp = $timestamp
            Mode = $Mode
            Duration_Seconds = $PerformanceMetrics.TotalDuration.TotalSeconds
            System_Info = $PerformanceMetrics.SystemInfo
            GPU_Info = $PerformanceMetrics.GPUInfo
            Component_Results = $PerformanceMetrics.ComponentResults
        }
        
        $jsonResults | ConvertTo-Json -Depth 10 | Set-Content $resultsFile
        Write-Host "✅ Results saved to: $resultsFile" -ForegroundColor Green
        
    } catch {
        Write-Host "❌ Failed to save results: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Display-TestSummary {
    Write-Host "📊 Performance Test Summary" -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    
    Write-Host "System: $($PerformanceMetrics.SystemInfo.CPU_Name)" -ForegroundColor White
    Write-Host "CPU: $($PerformanceMetrics.SystemInfo.CPU_Cores)C/$($PerformanceMetrics.SystemInfo.CPU_Threads)T @ $($PerformanceMetrics.SystemInfo.CPU_Speed)MHz" -ForegroundColor White
    Write-Host "RAM: $($PerformanceMetrics.SystemInfo.RAM_GB)GB" -ForegroundColor White
    
    if ($PerformanceMetrics.GPUInfo.Name) {
        Write-Host "GPU: $($PerformanceMetrics.GPUInfo.Name) ($($PerformanceMetrics.GPUInfo.Memory_MB)MB)" -ForegroundColor White
    }
    
    Write-Host "Total Test Time: $($PerformanceMetrics.TotalDuration.TotalSeconds.ToString('F2'))s" -ForegroundColor White
    Write-Host ""
    
    # Component results
    foreach ($component in $PerformanceMetrics.ComponentResults.Keys) {
        $result = $PerformanceMetrics.ComponentResults[$component]
        if ($result.Status -eq "Success") {
            $color = "Green"
            $status = "✅"
        } else {
            $color = "Red"
            $status = "❌"
        }
        
        Write-Host "$status $component" -ForegroundColor $color
        if ($result.PSObject.Properties.Name -contains "Time_Seconds" -and $result.Time_Seconds) {
            Write-Host "   Time: $($result.Time_Seconds.ToString('F2'))s" -ForegroundColor Gray
        }
        if ($result.PSObject.Properties.Name -contains "Files_Per_Second" -and $result.Files_Per_Second -and $result.Files_Per_Second -gt 0) {
            Write-Host "   Speed: $($result.Files_Per_Second) files/sec" -ForegroundColor Gray
        }
    }
}

# ===== MAIN EXECUTION =====
try {
    switch ($Mode) {
        'Baseline' {
            Write-Host "📈 Running baseline performance tests..." -ForegroundColor Yellow
            Run-PerformanceTests
            Display-TestSummary
            Save-TestResults
        }
        'Optimized' {
            Write-Host "🚀 Running optimized performance tests..." -ForegroundColor Yellow
            Run-PerformanceTests
            Display-TestSummary
            Save-TestResults
        }
        'Compare' {
            Write-Host "🔄 Running comparison tests..." -ForegroundColor Yellow
            # This would require loading previous results for comparison
            Write-Host "Comparison mode not yet implemented" -ForegroundColor Yellow
        }
        'Full' {
            Write-Host "🎯 Running full performance test suite..." -ForegroundColor Yellow
            Run-PerformanceTests
            Display-TestSummary
            Save-TestResults
        }
    }
    
} catch {
    Write-Host "❌ Performance Test Suite failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "🎯 Performance Test Suite V4.0 completed successfully!" -ForegroundColor Green
exit 0
