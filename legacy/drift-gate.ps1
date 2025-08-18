param(
    [string]$mode = "check",
    [switch]$json
)

# Initialize drift array
$drift = @()

# Check if we're in a git repository
if (Test-Path ".git") {
    # Check for uncommitted changes
    try {
        $gitStatus = git status --porcelain 2>$null
        if ($gitStatus) {
            $drift += $gitStatus | ForEach-Object { "UNCOMMITTED: $_" }
        }
    } catch {
        Write-Warning "Failed to check git status"
    }

    # Check for untracked files
    try {
        $untracked = git ls-files --others --exclude-standard 2>$null
        if ($untracked) {
            $drift += $untracked | ForEach-Object { "UNTRACKED: $_" }
        }
    } catch {
        Write-Warning "Failed to check untracked files"
    }
} else {
    Write-Host "Not in a git repository - skipping drift detection" -ForegroundColor Yellow
}

if ($mode -eq "check") {
    if ($drift.Count -gt 0) {
        New-Item -ItemType Directory -Force -Path "restore" | Out-Null
        $txt = "restore\DRIFT_REPORT.txt"
        $drift | Out-File $txt -Encoding utf8
        if ($json) { 
            $drift | ConvertTo-Json | Out-File "restore\DRIFT_REPORT.json" -Encoding utf8 
        }
        Write-Host "Drift detected: $($drift.Count) items" -ForegroundColor Yellow
        Write-Host "Drift report saved to: $txt" -ForegroundColor Yellow
    } else { 
        Write-Host "No drift detected." -ForegroundColor Green
    }
}
