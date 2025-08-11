[CmdletBinding(SupportsShouldProcess)]
param(
    [ValidateSet('Check', 'Apply', 'Restore')]
    [string]$Mode = 'Check',

    [switch]$Json
)

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
function Invoke-GitCommand {
    param([string]$Command)
    try   { & git @($Command.Split(' ')) 2>$null }
    catch { Write-Warning "git $Command failed"; $null }
}

function Out-DriftReport {
    param(
        [string]$Dir = '.git-drift',
        [array]$Data
    )
    if (-not (Test-Path $Dir)) {
        New-Item -ItemType Directory -Path $Dir -Force | Out-Null
    }
    $txt = Join-Path $Dir 'DRIFT_REPORT.txt'
    $Data | Out-File $txt -Encoding utf8
    if ($Json) {
        $Data | ConvertTo-Json | Out-File (Join-Path $Dir 'DRIFT_REPORT.json') -Encoding utf8
    }
    Write-Host "Drift report saved to: $txt" -ForegroundColor Yellow
}

# ------------------------------------------------------------------
# Detect drift
# ------------------------------------------------------------------
$drift = @()

if (-not (Test-Path '.git')) {
    Write-Host 'Not in a git repository  skipping drift detection.' -ForegroundColor Yellow
    return
}

# Uncommitted changes
$gitStatus = Invoke-GitCommand 'status --porcelain'
if ($gitStatus) {
    $drift += $gitStatus | ForEach-Object { "UNCOMMITTED: $_" }
}

# Untracked files
$untracked = Invoke-GitCommand 'ls-files --others --exclude-standard'
if ($untracked) {
    $drift += $untracked | ForEach-Object { "UNTRACKED: $_" }
}

# ------------------------------------------------------------------
# Act on drift
# ------------------------------------------------------------------
switch ($Mode) {
    'Check' {
        if ($drift.Count) {
            Write-Host "Drift detected: $($drift.Count) items" -ForegroundColor Yellow
            Out-DriftReport -Data $drift
        }
        else {
            Write-Host 'No drift detected.' -ForegroundColor Green
        }
    }

    'Apply' {
        if (-not $drift.Count) {
            Write-Host 'Nothing to stash  working tree is clean.' -ForegroundColor Green
            return
        }

        Out-DriftReport -Data $drift   # snapshot before wiping
        if ($PSCmdlet.ShouldProcess('working tree', 'stash + clean')) {
            Invoke-GitCommand 'stash push --include-untracked -m "Git-Drift auto-stash"'
            Invoke-GitCommand 'clean -fd'
            Write-Host 'Working tree reset to HEAD  drift stashed.' -ForegroundColor Cyan
        }
    }

    'Restore' {
        $stashList = Invoke-GitCommand 'stash list'
        if (-not $stashList -or -not ($stashList | Where-Object { $_ -match 'Git-Drift auto-stash' })) {
            Write-Host 'No Git-Drift stash found.' -ForegroundColor Yellow
            return
        }
        if ($PSCmdlet.ShouldProcess('most recent Git-Drift stash', 'pop')) {
            Invoke-GitCommand 'stash pop'
            Write-Host 'Last Git-Drift stash reapplied.' -ForegroundColor Cyan
        }
    }
}
