#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Agent Exo-Suit V3.0 - Python Emoji Scanner Launcher
    Launches the Python-based emoji scanner with CPU/GPU/CPU+GPU support

.DESCRIPTION
    This script launches the Python emoji scanner with different device modes:
    - CPU: CPU-only processing
    - GPU: GPU-only processing (if available)
    - Hybrid: CPU+GPU combined processing
    - Auto: Automatic device selection

.PARAMETER Mode
    Device mode to use: cpu, gpu, hybrid, or auto (default: auto)

.PARAMETER Directory
    Directory to scan (default: current directory)

.PARAMETER Recursive
    Scan recursively through subdirectories (default: true)

.PARAMETER Verbose
    Enable verbose output

.PARAMETER Output
    Output directory for reports (default: restore)

.EXAMPLE
    .\emoji-sentinel-python.ps1 -Mode cpu
    .\emoji-sentinel-python.ps1 -Mode gpu -Verbose
    .\emoji-sentinel-python.ps1 -Mode hybrid -Directory "C:\Projects" -Recursive

.NOTES
    Requires Python 3.7+ and the RAG system dependencies
#>

param(
    [Parameter(Position=0)]
    [ValidateSet("cpu", "gpu", "hybrid", "auto")]
    [string]$Mode = "auto",
    
    [Parameter(Position=1)]
    [string]$Directory = ".",
    
    [switch]$Recursive,
    
    [switch]$Verbose,
    
    [string]$Output = "restore"
)

# Script configuration
$ScriptName = "Python Emoji Scanner Launcher"
$ScriptVersion = "3.0"
$PythonScript = "rag\emoji_scanner.py"

# Color configuration
$Colors = @{
    Info = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Header = "Magenta"
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Write-Header {
    param([string]$Title)
    Write-Host "`n" + "="*60 -ForegroundColor $Colors.Header
    Write-Host " $Title" -ForegroundColor $Colors.Header
    Write-Host "="*60 -ForegroundColor $Colors.Header
}

function Write-Section {
    param([string]$Title)
    Write-Host "`n--- $Title ---" -ForegroundColor $Colors.Info
}

function Test-PythonEnvironment {
    <#
    .SYNOPSIS
        Test if Python environment is properly configured
    #>
    Write-Section "Testing Python Environment"
    
    # Check if Python is available
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput " Python found: $pythonVersion" "Success"
        } else {
            throw "Python not found or not accessible"
        }
    } catch {
        Write-ColorOutput " Python not available: $($_.Exception.Message)" "Error"
        return $false
    }
    
    # Check if required Python script exists
    if (-not (Test-Path $PythonScript)) {
        Write-ColorOutput " Python emoji scanner script not found: $PythonScript" "Error"
        return $false
    }
    
    Write-ColorOutput " Python emoji scanner script found" "Success"
    
    # Check if rag directory exists
    if (-not (Test-Path "rag")) {
        Write-ColorOutput " RAG system directory not found" "Error"
        return $false
    }
    
    Write-ColorOutput " RAG system directory found" "Success"
    
    return $true
}

function Test-DeviceMode {
    <#
    .SYNOPSIS
        Test if the specified device mode is supported
    #>
    param([string]$Mode)
    
    Write-Section "Testing Device Mode: $Mode"
    
    try {
        # Test the device mode by running a quick Python check
        $testCommand = "python -c `"from rag.device_manager import DeviceManager; dm = DeviceManager(); print('Device manager initialized successfully')`""
        $testResult = Invoke-Expression $testCommand 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput " Device manager initialized successfully" "Success"
        } else {
            Write-ColorOutput " Device manager test failed: $testResult" "Warning"
        }
    } catch {
        Write-ColorOutput " Device manager test failed: $($_.Exception.Message)" "Warning"
    }
    
    # Additional mode-specific checks
    switch ($Mode) {
        "gpu" {
            try {
                $gpuTest = "python -c `"import torch; print('CUDA available:', torch.cuda.is_available())`""
                $gpuResult = Invoke-Expression $gpuTest 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-ColorOutput " GPU test completed: $gpuResult" "Success"
                }
            } catch {
                Write-ColorOutput " GPU test failed, will fallback to CPU" "Warning"
            }
        }
        "hybrid" {
            Write-ColorOutput " Hybrid mode will automatically select best available devices" "Info"
        }
        "auto" {
            Write-ColorOutput " Auto mode will detect and select optimal device configuration" "Info"
        }
    }
    
    return $true
}

function Start-EmojiScan {
    <#
    .SYNOPSIS
        Start the emoji scanning process
    #>
    param(
        [string]$Mode,
        [string]$Directory,
        [bool]$Recursive,
        [bool]$Verbose,
        [string]$Output
    )
    
    Write-Section "Starting Emoji Scan"
    Write-ColorOutput "Mode: $Mode" "Info"
    Write-ColorOutput "Directory: $Directory" "Info"
    Write-ColorOutput "Recursive: $Recursive" "Info"
    Write-ColorOutput "Verbose: $Verbose" "Info"
    Write-ColorOutput "Output: $Output" "Info"
    
    # Build Python command
    $pythonArgs = @(
        $PythonScript,
        "--mode", $Mode,
        "--directory", $Directory,
        "--output", $Output
    )
    
    if ($Recursive) {
        $pythonArgs += "--recursive"
    }
    
    if ($Verbose) {
        $pythonArgs += "--verbose"
    }
    
    $pythonCommand = "python " + ($pythonArgs -join " ")
    
    Write-ColorOutput "Executing: $pythonCommand" "Info"
    Write-Host ""
    
    # Execute Python script
    try {
        $startTime = Get-Date
        Invoke-Expression $pythonCommand
        
        $endTime = Get-Date
        $duration = $endTime - $startTime
        
        Write-Host ""
        Write-ColorOutput " Emoji scan completed successfully in $($duration.TotalSeconds.ToString('F2')) seconds" "Success"
        
        # Check for generated reports
        $jsonReport = Join-Path $Output "PYTHON_EMOJI_REPORT.json"
        $textReport = Join-Path $Output "PYTHON_EMOJI_REPORT.txt"
        
        if (Test-Path $jsonReport) {
            Write-ColorOutput " JSON report generated: $jsonReport" "Success"
        }
        
        if (Test-Path $textReport) {
            Write-ColorOutput " Text report generated: $textReport" "Success"
        }
        
    } catch {
        Write-ColorOutput " Emoji scan failed: $($_.Exception.Message)" "Error"
        return $false
    }
    
    return $true
}

function Show-PerformanceComparison {
    <#
    .SYNOPSIS
        Show performance comparison between different modes
    #>
    Write-Section "Performance Comparison"
    
    $reports = @(
        @{ Name = "PowerShell Scanner"; Path = "restore\EMOJI_REPORT.json" },
        @{ Name = "Python CPU Mode"; Path = "restore\PYTHON_EMOJI_REPORT.json" }
    )
    
    $results = @()
    
    foreach ($report in $reports) {
        if (Test-Path $report.Path) {
            try {
                $content = Get-Content $report.Path -Raw | ConvertFrom-Json
                $summary = $content.Summary
                
                $result = [PSCustomObject]@{
                    Scanner = $report.Name
                    FilesScanned = $summary.total_files_scanned
                    EmojisFound = $summary.total_emojis_found
                    Duration = $summary.scan_duration_seconds
                    DeviceMode = $summary.device_mode_used
                }
                
                $results += $result
                
            } catch {
                Write-ColorOutput " Could not read report: $($report.Path)" "Warning"
            }
        }
    }
    
    if ($results.Count -gt 0) {
        $results | Format-Table -AutoSize
    }
}

# Main execution
Write-Header "$ScriptName v$ScriptVersion"

try {
    # Test environment
    if (-not (Test-PythonEnvironment)) {
        Write-ColorOutput "Environment test failed. Please check Python installation and dependencies." "Error"
        exit 1
    }
    
    # Test device mode
    if (-not (Test-DeviceMode -Mode $Mode)) {
        Write-ColorOutput "Device mode test failed. Proceeding with caution." "Warning"
    }
    
    # Start emoji scan
    $scanSuccess = Start-EmojiScan -Mode $Mode -Directory $Directory -Recursive $Recursive -Verbose $Verbose -Output $Output
    
    if ($scanSuccess) {
        Write-Header "Scan Completed Successfully"
        
        # Show performance comparison
        Show-PerformanceComparison
        
        Write-ColorOutput "`nAll reports have been generated in the '$Output' directory." "Success"
        Write-ColorOutput "You can now analyze the results and proceed with emoji cleanup if needed." "Info"
        
    } else {
        Write-ColorOutput "`nScan failed. Please check the error messages above." "Error"
        exit 1
    }
    
} catch {
    Write-ColorOutput "`nUnexpected error: $($_.Exception.Message)" "Error"
    Write-ColorOutput "Stack trace: $($_.ScriptStackTrace)" "Error"
    exit 1
}

Write-Header "Script Execution Complete"
