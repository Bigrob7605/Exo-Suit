#Requires -Version 5.1
[CmdletBinding()]
param(
    [switch]$NoColor,
    [string]$OutDir = 'restore',
    [string]$SpecMap = 'ops/specmap.yaml'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ------------------------------------------------------------------
# region helpers
function Write-Colored {
    param(
        [Parameter(ValueFromPipeline)][string]$Text,
        [ValidateSet('Green','Yellow','Red')][string]$Color = 'Green'
    )
    process {
        if ($NoColor) { Write-Host $Text }
        else          { Write-Host $Text -ForegroundColor $Color }
    }
}

function Resolve-FullPath {
    param([string]$Path)
    $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path)
}

function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}
# endregion helpers

# ------------------------------------------------------------------
# region YAML loader
function Import-SpecMap {
    [CmdletBinding()]
    param(
        [string]$Path
    )

    # 1. Fast path via powershell-yaml module
    if (Get-Module -Name powershell-yaml -ListAvailable) {
        Import-Module powershell-yaml -ErrorAction Stop
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Yaml
    }

    # 2. Ultra-light parser for the exact subset we care about
    $raw = Get-Content -LiteralPath $Path -Raw
    $spec = @{ spec = @() }

    $rxId   = '^\s*-\s*id\s*:\s*(?<id>.+)'
    $rxDoc  = '^\s*doc\s*:\s*(?<doc>.+)'
    $rxCode = '^\s*code\s*:\s*$'
    $rxTest = '^\s*tests\s*:\s*$'
    $rxItem = '^\s*-\s*(?<item>.+)'

    $current = $null
    $section = $null

    switch -Regex ($raw -split '\r?\n') {
        $rxId   {
            $current = @{
                id    = $matches['id'].Trim()
                doc   = ''
                code  = [System.Collections.Generic.List[string]]::new()
                tests = [System.Collections.Generic.List[string]]::new()
            }
            $spec.spec.Add($current)
            $section = $null
            continue
        }
        { -not $current } { continue }

        $rxDoc  { $current.doc = $matches['doc'].Trim(); continue }
        $rxCode { $section = 'code'; continue }
        $rxTest { $section = 'tests'; continue }

        { $section -and ($_ -match $rxItem) } {
            $current.$section.Add($matches['item'].Trim())
        }
    }

    $spec
}
# endregion YAML loader

# ------------------------------------------------------------------
# region glob engine
function Expand-Glob {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Pattern
    )

    # Convert forward slashes to native separators
    $Pattern = $Pattern.Replace('/', [System.IO.Path]::DirectorySeparatorChar)

    # Handle ** (recursive) manually because -Recurse is slow
    if ($Pattern.Contains('**')) {
        $base = ($Pattern -split '\*\*')[0].TrimEnd([System.IO.Path]::DirectorySeparatorChar)
        if (-not [string]::IsNullOrWhiteSpace($base) -and (Test-Path $base)) {
            $remaining = $Pattern.Substring($base.Length).TrimStart([System.IO.Path]::DirectorySeparatorChar)
            $remaining = $remaining -replace '\*\*', '*'
            $files = Get-ChildItem -LiteralPath $base -Recurse -File -ErrorAction SilentlyContinue
        } else {
            $files = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue
            $remaining = $Pattern -replace '\*\*', '*'
        }
    } else {
        $files = Get-ChildItem -LiteralPath . -Recurse -File -ErrorAction SilentlyContinue
        $remaining = $Pattern
    }

    $files |
        Where-Object { $_.FullName -like "*$remaining" } |
        Select-Object -ExpandProperty FullName
}
# endregion glob engine

# ------------------------------------------------------------------
# region main
try {
    $OutDir = Resolve-FullPath $OutDir
    Ensure-Directory $OutDir

    $SpecMap = Resolve-FullPath $SpecMap
    if (-not (Test-Path $SpecMap)) {
        throw "Specmap file not found: $SpecMap"
    }

    Write-Host "Loading spec map: $SpecMap"
    $yaml = Import-SpecMap -Path $SpecMap
} catch {
    Write-Warning "YAML unreadable or missing, using fallback spec: $_"
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

$gaps = [System.Collections.Generic.List[pscustomobject]]::new()

foreach ($entry in $yaml.spec) {
    Write-Verbose "Processing spec id: $($entry.id)"

    $codeFiles = [System.Collections.Generic.List[string]]::new()
    $testFiles = [System.Collections.Generic.List[string]]::new()

    foreach ($pattern in $entry.code)  { $codeFiles.AddRange([string[]](Expand-Glob $pattern)) }
    foreach ($pattern in $entry.tests) { $testFiles.AddRange([string[]](Expand-Glob $pattern)) }

    if (-not $codeFiles.Count) {
        $gaps.Add([pscustomobject]@{
            PSTypeName = 'SpecMap.Gap'
            id       = $entry.id
            type     = 'CODE_MISSING'
            doc      = $entry.doc
            pattern  = $entry.code -join ', '
            samples  = @()
            expected = $entry.code
        })
    }

    if (-not $testFiles.Count) {
        $gaps.Add([pscustomobject]@{
            PSTypeName = 'SpecMap.Gap'
            id       = $entry.id
            type     = 'TEST_MISSING'
            doc      = $entry.doc
            pattern  = $entry.tests -join ', '
            samples  = @()
            expected = $entry.tests
        })
    }

    # Enrich existing entries with counts & samples
    foreach ($gap in $gaps.Where({ $_.id -eq $entry.id })) {
        if ($gap.type -eq 'CODE_MISSING') {
            $gap.samples = $codeFiles | Select-Object -First 5
        } elseif ($gap.type -eq 'TEST_MISSING') {
            $gap.samples = $testFiles | Select-Object -First 5
        }
    }
}

# ------------------------------------------------------------------
# region output
$outFile = Join-Path $OutDir 'SPECMAP_REPORT.json'
$gaps | ConvertTo-Json -Depth 5 | Out-File -LiteralPath $outFile -Encoding utf8

if ($gaps.Count) {
    $gaps | Group-Object type | ForEach-Object {
        switch ($_.Name) {
            'CODE_MISSING' { $_.Count | Write-Colored -Color Red   }
            'TEST_MISSING' { $_.Count | Write-Colored -Color Yellow }
        }
        "$($_.Count) $($_.Name.ToLower()) gap(s)" | Write-Colored -Color $_.Name
    }
    "Details written to $outFile" | Write-Colored -Color Red
} else {
    'Spec map clean.' | Write-Colored -Color Green
}
# endregion output
