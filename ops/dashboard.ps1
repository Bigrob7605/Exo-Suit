$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
New-Item -ItemType Directory -Force -Path 'restore' | Out-Null

function LoadJson($p) { 
  if (Test-Path $p) { 
    try {
      $content = Get-Content $p -Raw | ConvertFrom-Json
      if ($content -is [array]) { return $content } else { return @() }
    } catch {
      return @()
    }
  } else { 
    return @() 
  } 
}

# Ensure all variables are arrays
$place = @(LoadJson 'context/_latest/placeholders.json')
$drift = @(LoadJson 'restore/DRIFT_REPORT.json')
$secr  = @(LoadJson 'restore/SECRETS_REPORT.json')
$bin   = @(LoadJson 'restore/BINARY_GUARD.json')
$lock  = @(LoadJson 'context/_latest/lock_age.json')
$own   = @(LoadJson 'context/_latest/ownership.json')

$block = ($place | Where-Object { $_.Severity -eq 'BLOCK' }).Count
$warn  = ($place | Where-Object { $_.Severity -eq 'WARN' }).Count
$info  = ($place | Where-Object { $_.Severity -eq 'INFO' }).Count

$html = @"
<!doctype html><html><head><meta charset="utf-8">
<title>Exo-Suit Dashboard</title>
<style>
body{font-family:system-ui,Segoe UI,Roboto,Arial;margin:24px;background:#0b0f14;color:#e6eef6}
.card{background:#121820;border:1px solid #1f2a36;border-radius:12px;padding:16px;margin:12px 0}
.h{font-size:20px;margin:0 0 8px}
.kv{display:flex;gap:16px;flex-wrap:wrap}
.kv div{background:#0f141b;border:1px solid #1c2632;border-radius:10px;padding:12px 16px}
pre{white-space:pre-wrap;background:#0f141b;padding:12px;border-radius:8px;border:1px solid #1c2632}
a{color:#8ad3ff}
</style></head><body>
<h1>Exo-Suit Dashboard</h1>
<div class="card"><div class="h">Status</div>
<div class="kv">
<div><b>BLOCK</b><br>$block</div>
<div><b>WARN</b><br>$warn</div>
<div><b>INFO</b><br>$info</div>
<div><b>Drift</b><br>$($drift.Count)</div>
<div><b>Secrets</b><br>$($secr.Count)</div>
<div><b>Binaries</b><br>$($bin.Count)</div>
</div></div>

<div class="card"><div class="h">Lock file age</div><pre>$( $lock | ConvertTo-Json -Depth 4 )</pre></div>
<div class="card"><div class="h">Ownership</div><pre>$( $own  | ConvertTo-Json -Depth 4 )</pre></div>
<div class="card"><div class="h">Secrets (top 10)</div><pre>$( $secr | Select-Object -First 10 | ConvertTo-Json -Depth 4 )</pre></div>
<div class="card"><div class="h">Binary Guard (top 10)</div><pre>$( $bin  | Select-Object -First 10 | ConvertTo-Json -Depth 4 )</pre></div>
</body></html>
"@
$html | Out-File 'restore/dashboard.html' -Encoding utf8
Write-Host "Dashboard at restore/dashboard.html"
