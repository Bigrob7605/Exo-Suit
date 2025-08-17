# Agent Exo-Suit V5.0 "Builder of Dreams" - Smart Log Manager
# Purpose: Manage log files with master/test separation to preserve raw data
# Version: 5.0.0
# Date: August 12, 2025

param(
    [Parameter(Mandatory=$false)]
    [string]$Operation = "setup",
    
    [Parameter(Mandatory=$false)]
    [string]$MasterLogPath = ".\logs\master",
    
    [Parameter(Mandatory=$false)]
    [string]$TestLogPath = ".\logs\test",
    
    [Parameter(Mandatory=$false)]
    [string]$ArchivePath = ".\logs\archive",
    
    [Parameter(Mandatory=$false)]
    [switch]$VerboseOutput
)

# Initialize logging
$LogStartTime = Get-Date
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Agent Exo-Suit V5.0 'Builder of Dreams' - Smart Log Manager Starting..." -ForegroundColor Green

# Function to create directory structure
function Initialize-LogStructure {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Initializing log directory structure..." -ForegroundColor Yellow
    
    # Create master logs directory (NEVER SCANNED during tests)
    if (-not (Test-Path $MasterLogPath)) {
        New-Item -ItemType Directory -Path $MasterLogPath -Force | Out-Null
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Created master logs directory: $MasterLogPath" -ForegroundColor Green
    }
    
    # Create test logs directory (scanned during tests)
    if (-not (Test-Path $TestLogPath)) {
        New-Item -ItemType Directory -Path $TestLogPath -Force | Out-Null
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Created test logs directory: $TestLogPath" -ForegroundColor Green
    }
    
    # Create archive directory
    if (-not (Test-Path $ArchivePath)) {
        New-Item -ItemType Directory -Path $ArchivePath -Force | Out-Null
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Created archive directory: $ArchivePath" -ForegroundColor Green
    }
    
    # Create .gitignore files to prevent accidental commits
    $MasterGitignore = Join-Path $MasterLogPath ".gitignore"
    if (-not (Test-Path $MasterGitignore)) {
        "*" | Out-File -FilePath $MasterGitignore -Encoding UTF8
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Created .gitignore in master logs directory" -ForegroundColor Green
    }
    
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Log directory structure initialized successfully" -ForegroundColor Green
}

# Function to move existing logs to master directory
function Move-ExistingLogsToMaster {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Moving existing logs to master directory..." -ForegroundColor Yellow
    
    # Find all log files in the project
    $LogFiles = Get-ChildItem -Path ".\" -Recurse -Include "*.log", "*.txt", "*_report.json", "*_scan.json" | Where-Object { $_.FullName -notlike "*\logs\*" -and $_.FullName -notlike "*\node_modules\*" -and $_.FullName -notlike "*\.git\*" }
    
    $MovedCount = 0
    foreach ($LogFile in $LogFiles) {
        $Destination = Join-Path $MasterLogPath $LogFile.Name
        if (-not (Test-Path $Destination)) {
            Move-Item -Path $LogFile.FullName -Destination $Destination -Force
            $MovedCount++
            if ($VerboseOutput) {
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Moved: $($LogFile.Name)" -ForegroundColor Cyan
            }
        }
    }
    
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Moved $MovedCount existing log files to master directory" -ForegroundColor Green
}

# Function to create log management configuration
function Create-LogConfig {
    $ConfigPath = ".\logs\log-config.json"
    $Config = @{
        MasterLogPath = $MasterLogPath
        TestLogPath = $TestLogPath
        ArchivePath = $ArchivePath
        MasterLogsNeverScanned = $true
        TestLogsScannedDuringTests = $true
        ArchiveRetentionDays = 30
        MaxLogSizeMB = 100
        CompressionEnabled = $true
        LastUpdated = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    }
    
    $Config | ConvertTo-Json -Depth 3 | Out-File -FilePath $ConfigPath -Encoding UTF8
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Created log configuration: $ConfigPath" -ForegroundColor Green
}

# Function to create log management documentation
function Create-LogDocumentation {
    $DocPath = ".\logs\README.md"
    $Documentation = @"
# Smart Log Management System - Agent Exo-Suit V5.0

**Purpose**: Separate master logs from test logs to preserve raw data integrity

## Directory Structure

### Master Logs (`./logs/master/`)
- **NEVER SCANNED** during any test operations
- Contains raw, unmodified log data
- Preserves historical information and system state
- Protected by .gitignore to prevent accidental commits

### Test Logs (`./logs/test/`)
- **SCANNED** during test operations
- Contains logs generated during current test sessions
- Can be processed, analyzed, and modified
- Temporary storage for active testing

### Archive (`./logs/archive/`)
- Long-term storage for completed test sessions
- Compressed and organized by date
- Retention policy: 30 days

## Usage Protocol

1. **Before Tests**: Ensure master logs are in `./logs/master/`
2. **During Tests**: Generate logs to `./logs/test/`
3. **After Tests**: Archive test logs to `./logs/archive/`
4. **Never Modify**: Master logs remain untouched for historical reference

## Benefits

- **Data Integrity**: Raw logs preserved for analysis
- **Test Isolation**: Test logs separate from historical data
- **Performance**: Only relevant logs scanned during operations
- **Compliance**: Maintains audit trail and system history

"@
    
    $Documentation | Out-File -FilePath $DocPath -Encoding UTF8
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Created log management documentation: $DocPath" -ForegroundColor Green
}

# Function to show log status
function Show-LogStatus {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Current Log Status:" -ForegroundColor Yellow
    
    $MasterLogs = Get-ChildItem -Path $MasterLogPath -File | Measure-Object
    $TestLogs = Get-ChildItem -Path $TestLogPath -File | Measure-Object
    $ArchiveLogs = Get-ChildItem -Path $ArchivePath -File | Measure-Object
    
    Write-Host "  Master Logs: $($MasterLogs.Count) files (NEVER SCANNED)" -ForegroundColor Green
    Write-Host "  Test Logs: $($TestLogs.Count) files (scanned during tests)" -ForegroundColor Yellow
    Write-Host "  Archive: $($ArchiveLogs.Count) files" -ForegroundColor Cyan
    
    # Show master log sizes
    $MasterSize = (Get-ChildItem -Path $MasterLogPath -Recurse -File | Measure-Object -Property Length -Sum).Sum
    $MasterSizeMB = [math]::Round($MasterSize / 1MB, 2)
    Write-Host "  Master Logs Total Size: $MasterSizeMB MB" -ForegroundColor Green
}

# Main execution
try {
    switch ($Operation.ToLower()) {
        "setup" {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Setting up smart log management system..." -ForegroundColor Green
            Initialize-LogStructure
            Move-ExistingLogsToMaster
            Create-LogConfig
            Create-LogDocumentation
            Show-LogStatus
        }
        "status" {
            Show-LogStatus
        }
        "cleanup" {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Cleaning up test logs..." -ForegroundColor Yellow
            Get-ChildItem -Path $TestLogPath -File | Remove-Item -Force
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Test logs cleaned up" -ForegroundColor Green
        }
        default {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [ERROR] Unknown operation: $Operation" -ForegroundColor Red
            Write-Host "Valid operations: setup, status, cleanup" -ForegroundColor Yellow
            exit 1
        }
    }
    
    $ExecutionTime = (Get-Date) - $LogStartTime
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] Smart Log Manager completed in $($ExecutionTime.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Green
    
} catch {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [ERROR] Smart Log Manager failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
