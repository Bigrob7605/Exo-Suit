#Requires -Version 5.1
param(
    [switch]$NoColor,
    [string]$OutDir = 'restore'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ------------------------- helpers ---------------------------------
filter Green  { if (-not $NoColor) { Write-Host $_ -ForegroundColor Green } else { Write-Host $_ } }
filter Yellow { if (-not $NoColor) { Write-Host $_ -ForegroundColor Yellow } else { Write-Host $_ } }
filter Red    { if (-not $NoColor) { Write-Host $_ -ForegroundColor Red }   else { Write-Host $_ } }

# fast mkdir -Force
if (-not (Test-Path $OutDir)) { $null = New-Item -ItemType Directory -Path $OutDir }

# ------------------------- YAML loader -----------------------------
function Import-SpecMap {
    param($Path = 'ops/specmap.yaml')

    # 1. Try the real module (fast & accurate)
    if (Get-Module -List powershell-yaml) {
        Import-Module powershell-yaml -ea Stop
        return Get-Content $Path -Raw | ConvertFrom-Yaml
    }

    # 2. Robust regex fallback
    $raw = Get-Content $Path -Raw
    $spec = @{ spec = @() }
    $rxId   = '^\s*-\s*id\s*:\s*(.+)'
    $rxDoc  = '^\s*doc\s*:\s*(.+)'
    $rxCode = '^\s*code\s*:\s*$'
    $rxTest = '^\s*tests\s*:\s*$'
    $rxItem = '^\s*-\s*(.+)'

    $current = $null
    $section = $null
    foreach ($line in $raw -split "`r?`n") {
        if ($line -match $rxId) {
            $current = @{ id = $matches[1].Trim(); doc = ''; code = @(); tests = @() }
            $spec.spec += $current
            $section = $null
            continue
        }
        if (-not $current) { continue }

        if ($line -match $rxDoc ) { $current.doc = $matches[1].Trim(); continue }
        if ($line -match $rxCode) { $section = 'code';  continue }
        if ($line -match $rxTest) { $section = 'tests'; continue }

        if ($section -and ($line -match $rxItem)) {
            $current.$section += $matches[1].Trim()
        }
    }
    return $spec
}

# ------------------------- glob engine -----------------------------
function Expand-Glob {
    param([string]$Pattern)

    # Convert traditional globs to PS syntax, but keep ** cross-platform
    $pat = $Pattern -replace '\\', '/'
    $pat = $pat -replace '\*\*', '**'
    $pat = $pat -replace '(?<!/)\*(?!\*)', '*'
    # Use built-in -Filter for speed, but allow advanced wildcards
    $files = @(Get-ChildItem -Path . -Recurse -File -ErrorAction SilentlyContinue)
    $files | Where-Object {
        $_.FullName -replace '\\','/' -like ($pat -replace '\*\*','*')
    } | Select-Object -ExpandProperty FullName
}

# ------------------------- main ------------------------------------
try   { $yaml = Import-SpecMap }
catch {
    Write-Warning "YAML unreadable, using fallback spec"
    $yaml = @{
        spec = @(
            @{
                id    = 'exo-suit-core'
                doc   = 'README.md#exo-suit'
                code  = @('ops/**', 'rag/**', 'mermaid/**')
                tests = @('test_*.py', '*_test.py')
            }
        )
    }
}

$gaps = @()
$allFiles = @(Get-ChildItem -Recurse -File | Select-Object -ExpandProperty FullName)

foreach ($entry in $yaml.spec) {
    $codeFiles = $entry.code  | ForEach-Object { Expand-Glob $_ }
    $testFiles = $entry.tests | ForEach-Object { Expand-Glob $_ }

    if (-not $codeFiles) {
        $gaps += [pscustomobject]@{
            id       = $entry.id
            type     = 'CODE_MISSING'
            doc      = $entry.doc
            pattern  = $entry.code -join ', '
            samples  = @()
            expected = $entry.code
        }
    }
    if (-not $testFiles) {
        $gaps += [pscustomobject]@{
            id       = $entry.id
            type     = 'TEST_MISSING'
            doc      = $entry.doc
            pattern  = $entry.tests -join ', '
            samples  = @()
            expected = $entry.tests
        }
    }

    # enrich existing entries with counts & samples
    $gaps | Where-Object { $_.id -eq $entry.id } | ForEach-Object {
        if ($_.type -eq 'CODE_MISSING') {
            $_.samples = $codeFiles | Select-Object -First 5
        }
        if ($_.type -eq 'TEST_MISSING') {
            $_.samples = $testFiles | Select-Object -First 5
        }
    }
}

# ------------------------- output ----------------------------------
$outFile = Join-Path $OutDir 'SPECMAP_REPORT.json'
$gaps | ConvertTo-Json -Depth 5 | Out-File $outFile -Encoding utf8

if ($gaps.Count) {
    $gaps | Group-Object type | ForEach-Object {
        $color = if ($_.Name -eq 'CODE_MISSING') { 'Red' } else { 'Yellow' }
        & $color "$($_.Count) $($_.Name.ToLower()) gap(s)"
    }
    Red "Details written to $outFile"
} else {
    Green "Spec map clean."
}
