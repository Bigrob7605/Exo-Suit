# Agent Exo-Suit V4.0 "PERFECTION" - Drift Guard
# Ultra-robust Git drift detection with bulletproof edge case handling

[CmdletBinding()]
param(
    [ValidateSet('Check', 'Apply', 'Restore')]
    [string]$Mode = 'Check',
    
    [switch]$Json,
    
    [switch]$EnableVerbose,
    
    [string]$OutputPath = "restore\DRIFT_REPORT.json",
    
    [string]$Path = ".",
    
    [switch]$Force,
    
    [switch]$Benchmark
)

# ===== ULTRA-ROBUST ERROR HANDLING =====
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ===== PARAMETER VALIDATION =====
# Parameter validation will be done in main execution after functions are defined

# ===== ADVANCED LOGGING =====
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [ConsoleColor]$Color = [ConsoleColor]::White
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    Write-Host $logEntry -ForegroundColor $Color
    
    if ($EnableVerbose) {
        $logPath = Join-Path (Get-Location) "drift_guard_v4.log"
        $logEntry | Add-Content -Path $logPath -ErrorAction SilentlyContinue
    }
}

# ===== SYSTEM VALIDATION =====
function Test-SystemRequirements {
    Write-Log " Validating system requirements..." -Color Cyan
    
    # Check PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        Write-Log " PowerShell 5.1+ required" -Color Red
        return $false
    }
    
    # Check Git availability
    try {
        $gitVersion = git --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Log " Git not available: $gitVersion" -Color Red
            return $false
        }
        Write-Log " Git available: $gitVersion" -Color Green
    } catch {
        Write-Log " Git not found in PATH" -Color Red
        return $false
    }
    
    # Check available memory
    $memory = Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object -ExpandProperty TotalVisibleMemorySize
    $memoryGB = [math]::Round($memory / 1024 / 1024, 2)
    Write-Log " Available memory: $memoryGB GB" -Color Green
    
    if ($memoryGB -lt 1) {
        Write-Log " Low memory detected. Consider closing other applications" -Color Yellow
    }
    
    return $true
}

# ===== GIT REPOSITORY VALIDATION =====
function Test-GitRepository {
    param([string]$RepoPath)
    
    Write-Log " Validating Git repository..." -Color Cyan
    
    try {
        # Change to the repository path
        Push-Location $RepoPath -ErrorAction Stop
        
        # Check if we're in a Git repository
        $gitDir = git rev-parse --git-dir 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Log " Not a Git repository: $RepoPath" -Color Red
            return $false
        }
        
        # Check if repository is bare
        if ((Test-Path $gitDir -PathType Leaf) -or (Test-Path (Join-Path $gitDir "HEAD") -PathType Leaf)) {
            Write-Log " Git repository validated" -Color Green
            return $true
        } else {
            Write-Log " Invalid Git repository structure" -Color Red
            return $false
        }
    } catch {
        Write-Log " Error validating Git repository: $_" -Color Red
        return $false
    } finally {
        Pop-Location
    }
}

# ===== GIT STATE ANALYSIS =====
function Get-GitState {
    param([string]$RepoPath)
    
    Write-Log " Analyzing Git repository state..." -Color Cyan
    
    try {
        Push-Location $RepoPath -ErrorAction Stop
        
        $state = @{
            HasCommits = $false
            CurrentBranch = $null
            IsDetached = $false
            HasRemote = $false
            RemoteUrl = $null
            LastCommit = $null
            Status = $null
        }
        
        # Check if repository has commits
        try {
            $lastCommit = git rev-parse HEAD 2>$null
            if ($LASTEXITCODE -eq 0) {
                $state.HasCommits = $true
                $state.LastCommit = $lastCommit.Substring(0, 8)
            }
        } catch {
            Write-Log " Repository has no commits" -Color Yellow
        }
        
        # Check current branch
        try {
            $currentBranch = git rev-parse --abbrev-ref HEAD 2>$null
            if ($LASTEXITCODE -eq 0) {
                $state.CurrentBranch = $currentBranch
                $state.IsDetached = ($currentBranch -eq "HEAD")
            }
        } catch {
            Write-Log " Could not determine current branch" -Color Yellow
        }
        
        # Check remote configuration
        try {
            $remoteUrl = git config --get remote.origin.url 2>$null
            if ($remoteUrl) {
                $state.HasRemote = $true
                $state.RemoteUrl = $remoteUrl
            }
        } catch {
            Write-Log " No remote origin configured" -Color Yellow
        }
        
        # Get current status
        try {
            $status = git status --porcelain 2>$null
            $state.Status = $status
        } catch {
            Write-Log " Could not retrieve Git status" -Color Yellow
        }
        
        return $state
        
    } catch {
        Write-Log " Error analyzing Git state: $_" -Color Red
        return $null
    } finally {
        Pop-Location
    }
}

# ===== DRIFT DETECTION =====
function Get-GitDrift {
    param([string]$RepoPath)
    
    Write-Log " Detecting Git drift..." -Color Cyan
    
    try {
        Push-Location $RepoPath -ErrorAction Stop
        
        $drift = [System.Collections.Generic.List[string]]::new()
        
        # 1. Uncommitted changes (staged + unstaged)
        try {
            $gitStatus = @(git status --porcelain=v1 2>$null)
            foreach ($line in $gitStatus) {
                if ($line) { 
                    $drift.Add("UNCOMMITTED: $line") 
                }
            }
        } catch {
            Write-Log " Could not retrieve Git status" -Color Yellow
        }
        
        # 2. Untracked files
        try {
            $untracked = @(git ls-files --others --exclude-standard 2>$null)
            foreach ($file in $untracked) {
                if ($file) { 
                    $drift.Add("UNTRACKED: $file") 
                }
            }
        } catch {
            Write-Log " Could not enumerate untracked files" -Color Yellow
        }
        
        # 3. Staged changes
        try {
            $staged = @(git diff --cached --name-only 2>$null)
            foreach ($file in $staged) {
                if ($file -and -not $drift.Contains("UNCOMMITTED: $file")) {
                    $drift.Add("STAGED: $file")
                }
            }
        } catch {
            Write-Log " Could not check staged changes" -Color Yellow
        }
        
        # 4. Check for detached HEAD
        try {
            $currentBranch = git rev-parse --abbrev-ref HEAD 2>$null
            if ($currentBranch -eq "HEAD") {
                $drift.Add("DETACHED_HEAD: Repository is in detached HEAD state")
            }
        } catch {
            Write-Log " Could not check HEAD state" -Color Yellow
        }
        
        # 5. Check for merge conflicts
        try {
            $mergeHead = git rev-parse MERGE_HEAD 2>$null
            if ($LASTEXITCODE -eq 0) {
                $drift.Add("MERGE_CONFLICT: Repository has unresolved merge conflicts")
            }
        } catch {
            # No merge in progress
        }
        
        # 6. Check for rebase state
        try {
            $rebaseHead = git rev-parse REBASE_HEAD 2>$null
            if ($LASTEXITCODE -eq 0) {
                $drift.Add("REBASE_IN_PROGRESS: Repository is in rebase state")
            }
        } catch {
            # No rebase in progress
        }
        
        return $drift
        
    } catch {
        Write-Log " Error detecting drift: $_" -Color Red
        return @()
    } finally {
        Pop-Location
    }
}

# ===== DRIFT MANAGEMENT =====
function Apply-GitDrift {
    param([string]$RepoPath, [switch]$Force)
    
    Write-Log " Applying drift management..." -Color Cyan
    
    try {
        Push-Location $RepoPath -ErrorAction Stop
        
        $drift = Get-GitDrift -RepoPath $RepoPath
        
        if ($drift.Count -eq 0) {
            Write-Log " No drift detected - nothing to manage" -Color Green
            return $true
        }
        
        if (-not $Force) {
            Write-Log " Drift detected. Use -Force to apply management" -Color Yellow
            return $false
        }
        
        # Create backup branch
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $backupBranch = "drift-backup-$timestamp"
        
        try {
            git checkout -b $backupBranch 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Log " Created backup branch: $backupBranch" -Color Green
            }
        } catch {
            Write-Log " Could not create backup branch" -Color Yellow
        }
        
        # Stash changes
        try {
            git stash push --include-untracked --message "Drift Guard V4.0 auto-stash $timestamp" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Log " Stashed all changes" -Color Green
            }
        } catch {
            Write-Log " Could not stash changes" -Color Yellow
        }
        
        # Clean untracked files
        try {
            git clean -fd 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Log " Cleaned untracked files" -Color Green
            }
        } catch {
            Write-Log " Could not clean untracked files" -Color Yellow
        }
        
        return $true
        
    } catch {
        Write-Log " Error applying drift management: $_" -Color Red
        return $false
    } finally {
        Pop-Location
    }
}

function Restore-GitDrift {
    param([string]$RepoPath)
    
    Write-Log " Restoring drift..." -Color Cyan
    
    try {
        Push-Location $RepoPath -ErrorAction Stop
        
        # Find our drift stash
        $stashList = git stash list --format="%gd|%s" 2>$null
        $driftStash = $stashList | Where-Object { $_ -match "Drift Guard V4\.0 auto-stash" } | Select-Object -First 1
        
        if (-not $driftStash) {
            Write-Log " No drift stash found" -Color Yellow
            return $false
        }
        
        $stashRef = ($driftStash -split '\|')[0]
        
        # Apply the stash
        try {
            git stash pop $stashRef 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Log " Restored drift from stash: $stashRef" -Color Green
                return $true
            }
        } catch {
            Write-Log " Could not restore stash: $_" -Color Red
            return $false
        }
        
    } catch {
        Write-Log " Error restoring drift: $_" -Color Red
        return $false
    } finally {
        Pop-Location
    }
}

# ===== REPORTING =====
function Write-DriftReport {
    param(
        [array]$Drift,
        [string]$OutputPath,
        [switch]$Json
    )
    
    Write-Log " Writing drift report..." -Color Cyan
    
    try {
        $restoreDir = Split-Path $OutputPath -Parent
        if (-not (Test-Path $restoreDir)) {
            New-Item -ItemType Directory -Force -Path $restoreDir | Out-Null
        }
        
        # Text report
        $txtPath = $OutputPath -replace '\.json$', '.txt'
        $drift | Out-File -LiteralPath $txtPath -Encoding utf8
        
        Write-Log " Text report saved to: $txtPath" -Color Green
        
        # JSON report
        if ($Json) {
            $report = @{
                timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                drift_count = $Drift.Count
                drift_items = $Drift
                repository = $Path
                mode = $Mode
            }
            
            $report | ConvertTo-Json -Depth 3 | Out-File -LiteralPath $OutputPath -Encoding utf8
            Write-Log " JSON report saved to: $OutputPath" -Color Green
        }
        
    } catch {
        Write-Log " Error writing report: $_" -Color Red
    }
}

# ===== BENCHMARKING =====
function Start-DriftBenchmark {
    param([string]$RepoPath)
    
    Write-Log " Starting Drift Guard V4.0 benchmark..." -Color Cyan
    
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    
    # Test drift detection
    $drift = Get-GitDrift -RepoPath $RepoPath
    $detectionTime = $sw.Elapsed.TotalMilliseconds
    
    # Test state analysis
    $sw.Restart()
    $state = Get-GitState -RepoPath $RepoPath
    $analysisTime = $sw.Elapsed.TotalMilliseconds
    
    $sw.Stop()
    
    $results = @{
        drift_detection_ms = [math]::Round($detectionTime, 2)
        state_analysis_ms = [math]::Round($analysisTime, 2)
        total_time_ms = [math]::Round($sw.Elapsed.TotalMilliseconds, 2)
        drift_items = $drift.Count
        repository_size = (Get-ChildItem -Path $RepoPath -Recurse -File | Measure-Object -Property Length -Sum).Sum
    }
    
    Write-Log " Benchmark Results:" -Color Cyan
    $results | Format-Table -AutoSize
    
    return $results
}

# ===== MAIN EXECUTION =====
function Start-DriftGuard {
    Write-Log " Starting Agent Exo-Suit V4.0 'PERFECTION' - Drift Guard..." -Color Cyan
    
    # Validate and ensure output directory exists
    try {
        Write-Log " Debug: OutputPath value: '$OutputPath'" -Color Cyan
        Write-Log " Debug: OutputPath type: $($OutputPath.GetType().Name)" -Color Cyan
        Write-Log " Debug: OutputPath length: $($OutputPath.Length)" -Color Cyan
        
        if ([string]::IsNullOrEmpty($OutputPath)) {
            Write-Log " OutputPath is empty, using default" -Color Yellow
            $OutputPath = "restore\DRIFT_REPORT.json"
        }
        
        $outputDir = Split-Path $OutputPath -Parent
        Write-Log " Debug: Output directory: '$outputDir'" -Color Cyan
        
        # Handle case where output path is just a filename (no directory)
        if ([string]::IsNullOrEmpty($outputDir)) {
            Write-Log " Debug: Output path is just a filename, using current directory" -Color Cyan
            $outputDir = (Get-Location).Path
        }
        
        if (-not (Test-Path $outputDir)) {
            New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
            Write-Log " Created output directory: $outputDir" -Color Green
        }
    } catch {
        Write-Log " Error creating output directory: $_" -Color Red
        exit 1
    }
    
    # Validate system requirements
    if (-not (Test-SystemRequirements)) {
        Write-Log " System requirements not met. Exiting." -Color Red
        exit 1
    }
    
    # Resolve and validate path
    try {
        $resolvedPath = Resolve-Path $Path -ErrorAction Stop
        Write-Log " Using path: $resolvedPath" -Color Green
    } catch {
        Write-Log " Invalid path: $Path" -Color Red
        exit 1
    }
    
    # Validate Git repository
    if (-not (Test-GitRepository -RepoPath $resolvedPath)) {
        Write-Log " Not a valid Git repository: $resolvedPath" -Color Red
        exit 1
    }
    
    # Get repository state
    $gitState = Get-GitState -RepoPath $resolvedPath
    if (-not $gitState) {
        Write-Log " Could not analyze Git repository state" -Color Red
        exit 1
    }
    
    # Display repository info
    Write-Log " Repository Information:" -Color Cyan
    Write-Log "  Current Branch: $($gitState.CurrentBranch)" -Color White
    Write-Log "  Has Commits: $($gitState.HasCommits)" -Color White
    Write-Log "  Is Detached: $($gitState.IsDetached)" -Color White
    Write-Log "  Has Remote: $($gitState.HasRemote)" -Color White
    
    # Execute based on mode
    switch ($Mode) {
        'Check' {
            Write-Log " Checking for drift..." -Color Cyan
            
            $drift = Get-GitDrift -RepoPath $resolvedPath
            
            if ($drift.Count -eq 0) {
                Write-Log " No drift detected" -Color Green
            } else {
                Write-Log " Drift detected: $($drift.Count) items" -Color Yellow
                
                # Write report
                $outputPath = Join-Path (Get-Location) $OutputPath
                Write-Log " Debug: About to write report to: $outputPath" -Color Cyan
                Write-DriftReport -Drift $drift -OutputPath $outputPath -Json:$Json
                
                exit 1
            }
        }
        
        'Apply' {
            Write-Log " Applying drift management..." -Color Cyan
            
            if (Apply-GitDrift -RepoPath $resolvedPath -Force:$Force) {
                Write-Log " Drift management applied successfully" -Color Green
            } else {
                Write-Log " Failed to apply drift management" -Color Red
                exit 1
            }
        }
        
        'Restore' {
            Write-Log " Restoring drift..." -Color Cyan
            
            if (Restore-GitDrift -RepoPath $resolvedPath) {
                Write-Log " Drift restored successfully" -Color Green
            } else {
                Write-Log " Failed to restore drift" -Color Red
                exit 1
            }
        }
    }
    
    # Run benchmark if requested
    if ($Benchmark) {
        $benchmarkResults = Start-DriftBenchmark -RepoPath $resolvedPath
        
        # Save benchmark results
        $benchmarkPath = Join-Path (Get-Location) "restore\DRIFT_BENCHMARK.json"
        $benchmarkResults | ConvertTo-Json -Depth 3 | Out-File -LiteralPath $benchmarkPath -Encoding utf8
        Write-Log " Benchmark results saved to: $benchmarkPath" -Color Green
    }
    
    Write-Log " Drift Guard V4.0 completed successfully!" -Color Green
}

# ===== SCRIPT EXECUTION =====
try {
    Start-DriftGuard
} catch {
    Write-Log " Unexpected error: $_" -Color Red
    Write-Log "Stack trace: $($_.ScriptStackTrace)" -Color Red
    exit 1
}
