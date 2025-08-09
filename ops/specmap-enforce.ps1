$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
New-Item -ItemType Directory -Force -Path 'restore' | Out-Null

function Glob($pattern) {
  $pattern = $pattern -replace '\\','/'
  $pattern = $pattern -replace '\*\*','(.+?)' -replace '\*','([^/]+?)'
  $rx = '^' + [regex]::Escape($pattern).Replace('\(\.\+\?\)','(.+?)').Replace('\(\[\^/\]\+\?\)','([^/]+?)') + '$'
  $rx = $rx.Replace('\/','[\\/]')
  $files = Get-ChildItem -Recurse -File | % FullName
  return $files | Where-Object { $_ -replace '\\','/' -match $rx }
}

# Try to load YAML, fallback to simple parsing if module not available
$yaml = $null
try {
  $map = (Get-Content 'ops/specmap.yaml' -Raw)
  if (Get-Command ConvertFrom-Yaml -EA SilentlyContinue) {
    $yaml = ConvertFrom-Yaml $map
  } else {
    # Simple fallback parser for basic YAML structure
    $yaml = @{ spec = @() }
    $currentSpec = $null
    foreach ($line in $map -split "`n") {
      $line = $line.Trim()
      if ($line -match '^- id: (.+)') {
        $currentSpec = @{ id = $matches[1]; code = @(); tests = @() }
        $yaml.spec += $currentSpec
      } elseif ($line -match '^\s*doc:\s*(.+)') {
        $currentSpec.doc = $matches[1]
      } elseif ($line -match '^\s*code:\s*$') {
        # Code section starts
      } elseif ($line -match '^\s*-\s*(.+)' -and $currentSpec) {
        $currentSpec.code += $matches[1]
      } elseif ($line -match '^\s*tests:\s*$') {
        # Tests section starts
      } elseif ($line -match '^\s*-\s*(.+)' -and $currentSpec) {
        if ($currentSpec.code.Count -gt 0) {
          $currentSpec.tests += $matches[1]
        }
      }
    }
  }
} catch {
  Write-Warning "Failed to parse specmap.yaml, using default structure"
  $yaml = @{ 
    spec = @(
      @{ id = "exo-suit-core"; doc = "README.md#exo-suit"; code = @("ops/**", "rag/**", "mermaid/**"); tests = @("test_*.py", "*_test.py") }
    )
  }
}

if (-not $yaml) { throw "Failed to parse specmap.yaml" }

$gaps = @()
foreach ($entry in $yaml.spec) {
  $codeHits = @()
  foreach ($c in $entry.code) { $codeHits += Glob $c }
  $testHits = @()
  foreach ($t in $entry.tests) { $testHits += Glob $t }
  if ($codeHits.Count -eq 0) {
    $gaps += [pscustomobject]@{ id=$entry.id; type='CODE_MISSING'; doc=$entry.doc; pattern=($entry.code -join ', ') }
  }
  if ($testHits.Count -eq 0) {
    $gaps += [pscustomobject]@{ id=$entry.id; type='TEST_MISSING'; doc=$entry.doc; pattern=($entry.tests -join ', ') }
  }
}

$path = 'restore/SPECMAP_REPORT.json'
$gaps | ConvertTo-Json -Depth 4 | Out-File $path -Encoding utf8

if ($gaps.Count -gt 0) {
  Write-Warning "Spec gaps found. See $path"
} else {
  Write-Host "Spec map clean."
}
