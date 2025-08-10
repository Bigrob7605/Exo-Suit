<#
.SYNOPSIS
  Parallel, AST-smart placeholder scanner for Agent Exo-Suit V1.2
.DESCRIPTION
  Scans a codebase for placeholder tokens, categorizes by severity,
  and produces JSON, console and markdown reports. 100 % backward
  compatible with V1.1.
.PARAMETER root
  Folder to scan (defaults to $PWD).
.PARAMETER markdown
  Emit extra markdown summary to context\_latest\placeholders.md
.PARAMETER failOn
  Comma-separated list of severities that should return non-zero exit code.
  Example: -failOn "BLOCK,WARN"
.EXAMPLE
  .\placeholder-scan.ps1 -root ..\myRepo -markdown -failOn "BLOCK"
#>
[CmdletBinding()]
param(
    [string]$root = $PWD.Path,
    [switch]$markdown,
    [string]$failOn = "BLOCK"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# -----------------------------------------------
# 0. House-keeping
# -----------------------------------------------
$outDir  = Join-Path $root "context\_latest"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

# Severity mapping & rank
$severityMap = @{
    'REPLACEME' = 'BLOCK'
    'STUB'      = 'WARN'
    'TODO'      = 'INFO'
    'FIXME'     = 'WARN'
    'HARDCODED' = 'BLOCK'
    'DUMMY'     = 'WARN'
    'WIP'       = 'INFO'
    'TBD'       = 'INFO'
}
$rank = @{ 'BLOCK'=3; 'WARN'=2; 'INFO'=1 }

# Read optional overrides
$overrideFile = Join-Path $root "severity-overrides.json"
$overrides = @{}
if (Test-Path $overrideFile) {
    $overrides = Get-Content $overrideFile -Raw | ConvertFrom-Json -AsHashtable
}

# Patterns to look for (single regex for speed)
$patternWords = $severityMap.Keys -join '|'
$patternRegex = "\b($patternWords)\b"

# File globs to scan
$include = @('*.py','*.js','*.ts','*.ps1','*.md','*.txt','*.yaml','*.yml')
$exclude = @(
    '*/.git/*','*/venv/*','*/.venv/*','*/gpu_rag_env/*','*/node_modules/*','*/__pycache__/*',
    '*/ops/*','*/context/*','*/.sandboxes/*',
    '*package-lock.json','*yarn.lock','*Cargo.lock',
    '*placeholder-scan*','*make-pack*','*drift-gate*','*index-*'
)

# -----------------------------------------------
# 1. Build file list (fast, memory friendly)
# -----------------------------------------------
Write-Host "Building file list..." -NoNewline
$files = Get-ChildItem -Path $root -Recurse -File -Include $include |
         Where-Object {
             $path = $_.FullName.Replace('\','/')
             -not ($exclude | Where-Object { $path -like $_ })
         }
Write-Host " $($files.Count) files"

# -----------------------------------------------
# 2. Parallel scan
# -----------------------------------------------
$scan = {
    param($file, $root, $patternRegex, $severityMap, $rank, $overrides)

    function IsInStringOrComment($line, $lang) {
        switch ($lang) {
            'py'   { return $line -match '^\s*#' }
            'js'   { return $line -match '^\s*//' -or $line -match '^\s*\*' }
            'ts'   { return $line -match '^\s*//' -or $line -match '^\s*\*' }
            'ps1'  { return $line -match '^\s*#' }
            default { return $false }
        }
    }

    $results = @()
    $lang = $file.Extension.Substring(1).ToLower()
    $lines  = [System.IO.File]::ReadAllLines($file.FullName)

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        if (IsInStringOrComment $line $lang) { continue }

        if ($line -match $patternRegex) {
            $keys = $Matches[1..($Matches.Count-1)] | Select-Object -Unique
            $sev  = ($keys | ForEach-Object { $severityMap[$_] } |
                     Sort-Object { $rank[$_] } -Descending |
                     Select-Object -First 1)

            # Override?
            $overrideKey = "$($file.FullName):$($i+1)"
            if ($overrides.ContainsKey($overrideKey)) { $sev = $overrides[$overrideKey] }

            $results += [PSCustomObject]@{
                File     = $file.FullName.Substring($root.Length).TrimStart('\','/')
                Line     = $i + 1
                Text     = $line.Trim()
                Severity = $sev
                Pattern  = $keys -join ','
            }
        }
    }
    return $results
}

Write-Host "Scanning (parallel)..."
# Use compatible parallel processing for PowerShell 5.1
$runspacePool = [runspacefactory]::CreateRunspacePool(1, [Environment]::ProcessorCount)
$runspacePool.Open()

$jobs = @()
foreach ($file in $files) {
    $ps = [powershell]::Create().AddScript($scan).AddArgument($file).AddArgument($root).AddArgument($patternRegex).AddArgument($severityMap).AddArgument($rank).AddArgument($overrides)
    $ps.RunspacePool = $runspacePool
    $jobs += @{
        PowerShell = $ps
        Handle = $ps.BeginInvoke()
    }
}

# Wait for all jobs to complete
$result = @()
foreach ($job in $jobs) {
    $result += $job.PowerShell.EndInvoke($job.Handle)
    $job.PowerShell.Dispose()
}
$runspacePool.Close()

# Flatten
$result = $result | ForEach-Object { $_ }

# -----------------------------------------------
# 3. Output
# -----------------------------------------------
$result | ConvertTo-Json -Depth 4 | Out-File (Join-Path $outDir "placeholders.json") -Encoding utf8

# Console table
$summary = $result | Group-Object Severity
$blockCount = ($summary | Where-Object Name -eq 'BLOCK').Count
$warnCount  = ($summary | Where-Object Name -eq 'WARN').Count
$infoCount  = ($summary | Where-Object Name -eq 'INFO').Count

Write-Host "`nSCAN COMPLETE"
Write-Host ("{0} BLOCK | {1} WARN | {2} INFO" -f $blockCount,$warnCount,$infoCount)

if ($result) {
    $result | Sort-Object Severity,File,Line |
              Format-Table @{N='Sev';E={$_.Severity.Substring(0,1)}},
                           @{N='File';E={$_.File.Substring(0,[Math]::Min(60,$_.File.Length))}},
                           Line, @{N='Text';E={$_.Text.Substring(0,[Math]::Min(60,$_.Text.Length))}} -AutoSize
}

# Markdown summary
if ($markdown) {
    $mdPath = Join-Path $outDir "placeholders.md"
    @"
# Placeholder Scan Report
*Generated $(Get-Date -Format 'yyyy-MM-dd HH:mm')*

| Severity | Count |
|----------|-------|
| **BLOCK** | $blockCount |
| **WARN**  | $warnCount |
| **INFO**  | $infoCount |

"@
    $result | Sort-Object Severity,File,Line |
              ForEach-Object {
                  "| $($_.Severity) | $($_.File):$($_.Line) | ``$($_.Text)`` |"
              } | Out-File $mdPath -Append
    Write-Host "Markdown report -> $mdPath"
}

# -----------------------------------------------
# 4. Exit code
# -----------------------------------------------
$shouldFail = ($failOn -split ',').Trim() | Where-Object { $_ -in 'BLOCK','WARN','INFO' }
if ($shouldFail | Where-Object { $_ -eq 'BLOCK' -and $blockCount -gt 0 }) { exit 1 }
if ($shouldFail | Where-Object { $_ -eq 'WARN'  -and $warnCount  -gt 0 }) { exit 1 }
if ($shouldFail | Where-Object { $_ -eq 'INFO'  -and $infoCount  -gt 0 }) { exit 1 }
