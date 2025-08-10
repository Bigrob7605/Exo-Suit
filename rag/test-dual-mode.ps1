<#
  PowerShell wrapper for CPU+GPU dual-mode RAG system testing
  Tests: CPU-only, GPU-only, and CPU+GPU hybrid modes with performance benchmarking
#>
param(
    [switch]$SkipEmbedding,
    [switch]$SkipRetrieval,
    [switch]$SkipBenchmarks,
    [switch]$Quick,
    [switch]$Verbose
)

$ErrorActionPreference = 'Stop'

Write-Host "🚀 Agent Exo-Suit V3.0 - Dual-Mode RAG System Test Suite" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan

# Quick mode overrides
if ($Quick) {
    Write-Host "⚡ Quick mode enabled - running essential tests only" -ForegroundColor Yellow
    $SkipBenchmarks = $true
}

# Check Python environment
Write-Host "🐍 Checking Python environment..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not available or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if test script exists
$testScript = Join-Path $PSScriptRoot "test_dual_mode.py"
if (-not (Test-Path $testScript)) {
    Write-Host "❌ Test script not found: $testScript" -ForegroundColor Red
    exit 1
}

# Build test command
$testArgs = @()

if ($SkipEmbedding) {
    $testArgs += "--skip-embedding"
    Write-Host "⏭️ Skipping embedding tests" -ForegroundColor Yellow
}

if ($SkipRetrieval) {
    $testArgs += "--skip-retrieval"
    Write-Host "⏭️ Skipping retrieval tests" -ForegroundColor Yellow
}

if ($SkipBenchmarks) {
    $testArgs += "--skip-benchmarks"
    Write-Host "⏭️ Skipping performance benchmarks" -ForegroundColor Yellow
}

# Run the test suite
Write-Host "🧪 Starting dual-mode test suite..." -ForegroundColor Cyan
Write-Host "  Command: python test_dual_mode.py $($testArgs -join ' ')" -ForegroundColor DarkGray

try {
    $startTime = Get-Date
    
    # Run tests
    $result = python $testScript @testArgs
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    if ($result -eq 0) {
        Write-Host "✅ Test suite completed successfully!" -ForegroundColor Green
        Write-Host "⏱️ Total duration: $($duration.ToString('mm\:ss'))" -ForegroundColor Cyan
        
        # Check for test report
        $reportFile = Join-Path $PSScriptRoot "dual_mode_test_report.json"
        if (Test-Path $reportFile) {
            Write-Host "📋 Test report generated: $reportFile" -ForegroundColor Green
            
            # Display summary if verbose
            if ($Verbose) {
                try {
                    $report = Get-Content $reportFile | ConvertFrom-Json
                    Write-Host "`n📊 Test Summary:" -ForegroundColor Cyan
                    Write-Host "  Total Tests: $($report.summary.total_tests)" -ForegroundColor White
                    Write-Host "  Successful: $($report.summary.successful_tests)" -ForegroundColor Green
                    Write-Host "  Failed: $($report.summary.total_tests - $report.summary.successful_tests)" -ForegroundColor Red
                    
                    if ($report.summary.device_modes_working) {
                        Write-Host "  Working Modes: $($report.summary.device_modes_working -join ', ')" -ForegroundColor Green
                    }
                } catch {
                    Write-Host "⚠️ Could not parse test report" -ForegroundColor Yellow
                }
            }
        }
        
    } else {
        Write-Host "❌ Test suite failed with exit code: $result" -ForegroundColor Red
        exit $result
    }
    
} catch {
    Write-Host "❌ Test suite execution failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n🎉 Dual-Mode Test Suite Completed!" -ForegroundColor Green
Write-Host "===============================================================" -ForegroundColor Cyan

# Check for any generated files
Write-Host "`n📁 Generated Files:" -ForegroundColor Cyan
$generatedFiles = @(
    "dual_mode_test_report.json",
    "index.faiss",
    "meta.jsonl",
    "context_topk.jsonl"
)

foreach ($file in $generatedFiles) {
    $filePath = Join-Path $PSScriptRoot $file
    if (Test-Path $filePath) {
        $fileSize = (Get-Item $filePath).Length / 1KB
        Write-Host "  ✅ $file ($($fileSize.ToString('F1')) KB)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file (not found)" -ForegroundColor Red
    }
}

Write-Host "`n🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review test report for detailed results" -ForegroundColor White
Write-Host "  2. Check generated index and metadata files" -ForegroundColor White
Write-Host "  3. Run individual tests if needed:" -ForegroundColor White
Write-Host "     - CPU-only: .\embed.ps1 -CPU" -ForegroundColor DarkGray
Write-Host "     - GPU-only: .\embed.ps1 -GPU" -ForegroundColor DarkGray
Write-Host "     - Hybrid: .\embed.ps1 -Hybrid" -ForegroundColor DarkGray
Write-Host "     - Auto: .\embed.ps1" -ForegroundColor DarkGray
