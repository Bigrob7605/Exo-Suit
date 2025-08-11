# Index imports script for Agent Exo-Suit
# Uses ripgrep to index imports across the codebase

param(
    [string]$root = $PWD.Path
)

$outDir = Join-Path $root "context\_latest"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Write-Host "Indexing imports..."

# Index Python imports
$pythonImports = @()
if (Get-Command rg -ErrorAction SilentlyContinue) {
    $pythonImports = rg --type py -n "^\s*(import|from)\s+(\w+)" $root | ForEach-Object {
        $line = $_.Split(':', 3)
        if ($line.Length -ge 3) {
            [PSCustomObject]@{
                File = $line[0]
                Line = $line[1]
                Import = $line[2].Trim()
            }
        }
    }
}

# Index JavaScript/TypeScript imports
$jsImports = @()
if (Get-Command rg -ErrorAction SilentlyContinue) {
    $jsImports = rg --type js --type ts -n "^\s*(import|require)" $root | ForEach-Object {
        $line = $_.Split(':', 3)
        if ($line.Length -ge 3) {
            [PSCustomObject]@{
                File = $line[0]
                Line = $line[1]
                Import = $line[2].Trim()
            }
        }
    }
}

# Index PowerShell imports
$psImports = @()
if (Get-Command rg -ErrorAction SilentlyContinue) {
    $psImports = rg --type ps1 -n "^\s*(Import-Module|\.\s*)" $root | ForEach-Object {
        $line = $_.Split(':', 3)
        if ($line.Length -ge 3) {
            [PSCustomObject]@{
                File = $line[0]
                Line = $line[1]
                Import = $line[2].Trim()
            }
        }
    }
}

# Combine results
$imports = @{
    Python = $pythonImports
    JavaScript = $jsImports
    PowerShell = $psImports
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

# Save to JSON
$imports | ConvertTo-Json -Depth 4 | Out-File (Join-Path $outDir "imports.json") -Encoding utf8
Write-Host "Imports indexed and saved to $outDir\imports.json"
