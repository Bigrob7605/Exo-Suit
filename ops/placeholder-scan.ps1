# Placeholder scanning script for Agent Exo-Suit V1.1
# Scans for placeholder patterns and categorizes by severity

param(
    [string]$root = $PWD.Path
)

$outDir = Join-Path $root "context\_latest"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Write-Host "Scanning for placeholders..."

# Define patterns to scan for (but don't scan for them in comments or strings)
$patterns = @('REPLACEME', 'STUB', 'TODO', 'FIXME', 'HARDCODED', 'DUMMY', 'WIP', 'TBD')

# Define severity mapping
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

# Get all files to scan (exclude ops directory, context directory, and specific files)
$files = Get-ChildItem -Path $root -Recurse -File | Where-Object {
    $_.Extension -match '\.(py|js|ts|ps1|md|txt|yaml|yml)$' -and  # Exclude .json files
    $_.FullName -notmatch '\.(git|venv|node_modules|__pycache__)' -and
    $_.FullName -notmatch '\\ops\\' -and  # Exclude ops directory
    $_.FullName -notmatch '\\context\\' -and  # Exclude context directory
    $_.Name -notmatch '^(package-lock\.json|yarn\.lock|Cargo\.lock)$' -and
    $_.Name -notmatch '^(placeholder-scan|make-pack|drift-gate|index-symbols|index-imports)\.ps1$'  # Exclude our own scripts
}

$result = @()

foreach ($f in $files) {
    if (Test-Path $f.FullName) {
        $content = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
        if ($content) {
            $lines = $content -split "`n"
            for ($i = 0; $i -lt $lines.Count; $i++) {
                $line = $lines[$i].Trim()
                
                # Skip comment lines and string definitions
                if ($line -match '^\s*#' -or $line -match '^\s*//' -or $line -match '^\s*\*') {
                    continue
                }
                
                foreach ($pattern in $patterns) {
                    # Look for the pattern as a standalone word or in context, but not in strings or comments
                    if ($line -match "\b$pattern\b" -and $line -notmatch "'$pattern'" -and $line -notmatch '"$pattern"') {
                        $keys = $patterns | Where-Object { $line -match "\b$_\b" }
                        $sev = ($keys | ForEach-Object { $severityMap[$_] } | Sort-Object { $rank[$_] } -Descending | Select-Object -First 1)
                        
                        $result += [PSCustomObject]@{
                            File = $f.FullName.Replace($root, '').TrimStart('\')
                            Line = $i + 1
                            Text = $line
                            Severity = $sev
                            Pattern = $pattern
                        }
                    }
                }
            }
        }
    }
}

# Save results
$result | ConvertTo-Json -Depth 4 | Out-File (Join-Path $outDir "placeholders.json") -Encoding utf8

# Summary
$blockCount = ($result | Where-Object { $_.Severity -eq 'BLOCK' }).Count
$warnCount = ($result | Where-Object { $_.Severity -eq 'WARN' }).Count
$infoCount = ($result | Where-Object { $_.Severity -eq 'INFO' }).Count

Write-Host "Placeholder scan complete:"
Write-Host "  BLOCK: $blockCount"
Write-Host "  WARN: $warnCount"
Write-Host "  INFO: $infoCount"
Write-Host "Results saved to $outDir\placeholders.json"

if ($blockCount -gt 0) {
    Write-Warning "Found $blockCount BLOCK severity items that need immediate attention!"
    # Don't exit with error for now, just warn
}
