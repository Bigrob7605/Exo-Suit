# Index symbols script for Agent Exo-Suit
# Uses ripgrep to index symbols across the codebase

param(
    [string]$root = $PWD.Path
)

$outDir = Join-Path $root "context\_latest"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Write-Host "Indexing symbols..."

# Index function definitions
$functions = @()
if (Get-Command rg -ErrorAction SilentlyContinue) {
    $functions = rg --type py --type js --type ts --type ps1 -n "^\s*(def|function)\s+(\w+)" $root | ForEach-Object {
        $line = $_.Split(':', 3)
        if ($line.Length -ge 3) {
            [PSCustomObject]@{
                File = $line[0]
                Line = $line[1]
                Function = $line[2].Trim()
            }
        }
    }
}

# Index class definitions
$classes = @()
if (Get-Command rg -ErrorAction SilentlyContinue) {
    $classes = rg --type py --type js --type ts -n "^\s*class\s+(\w+)" $root | ForEach-Object {
        $line = $_.Split(':', 3)
        if ($line.Length -ge 3) {
            [PSCustomObject]@{
                File = $line[0]
                Line = $line[1]
                Class = $line[2].Trim()
            }
        }
    }
}

# Combine results
$symbols = @{
    Functions = $functions
    Classes = $classes
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

# Save to JSON
$symbols | ConvertTo-Json -Depth 4 | Out-File (Join-Path $outDir "symbols.json") -Encoding utf8
Write-Host "Symbols indexed and saved to $outDir\symbols.json"
