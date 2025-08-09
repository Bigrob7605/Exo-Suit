<#
  Single entry point: max-perf → build → scan → test → Cursor-ready
#>
param([switch]$skipTests)

$ErrorActionPreference='Stop'; Set-StrictMode -Version Latest

# --- lock CPU to max ---
$guid = 'e9a42b02-d5df-448d-aa00-03f14749eb61' # Ultimate Performance
try {
    powercfg -duplicatescheme $guid | Out-Null
    powercfg -setactive $guid
    powercfg /change -standby-timeout-ac 0
    powercfg /change -hibernate-timeout-ac 0
} catch {
    Write-Host "Power scheme configuration failed, continuing..." -ForegroundColor Yellow
}

# --- RAM-disk scratch (optional) ---
$cacheDrive = "C:"
if (Test-Path ".env") {
    $envContent = Get-Content .env
    $cacheLine = $envContent | Where-Object { $_ -match '^CACHE_DRIVE=' }
    if ($cacheLine) {
        $cacheDrive = $cacheLine.Split('=')[1]
    }
}
$cache = Join-Path $cacheDrive "exocache"
New-Item -ItemType Directory -Force $cache | Out-Null
$env:TEMP = $env:TMP = $cache

# --- build & scan ---
.\ops\make-pack.ps1   $PSScriptRoot "$PSScriptRoot\context\_latest"
.\ops\index-symbols.ps1
.\ops\index-imports.ps1
.\ops\placeholder-scan.ps1
.\ops\drift-gate.ps1 -json

# --- RAG brain ---
.\rag\embed.ps1
.\ops\context-governor.ps1 -maxTokens 128000

# --- lint swarm (parallel & safe) ---
$lint = @(
  { if (Test-Path package.json) { npm run lint --silent 2>$null } },
  { if (Get-Command ruff -EA SilentlyContinue)   { ruff check --fix } },
  { if (Test-Path Cargo.toml) { cargo clippy -q } }
)
$lint | % { Start-Job $_ } | Wait-Job | Receive-Job

if (-not $skipTests) {
  $tests = @(
    { if (Test-Path package.json) { npm test --silent } },
    { if (Get-ChildItem *_test.py -Recurse) { pytest -q } },
    { if (Test-Path Cargo.toml) { cargo test -q } }
  )
  $tests | % { Start-Job $_ } | Wait-Job | Receive-Job
}

# --- diagrams ---
.\mermaid\generate-maps.ps1

# --- Sentinel Pack (v2.2 additions) ---
.\ops\sentinel-secrets.ps1
.\ops\sentinel-binaries.ps1 -maxSizeMB 75
.\ops\specmap-enforce.ps1
.\ops\dashboard.ps1

Write-Host "🔥 Exo-Suit armed. Open Cursor and follow COMMAND_QUEUE.md" -ForegroundColor Cyan
