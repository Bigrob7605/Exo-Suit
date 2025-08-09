# dashboard.ps1 – Exo-Suit Dashboard v2
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
New-Item -ItemType Directory -Force -Path 'restore' | Out-Null

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
function LoadJson($p) {
    if (Test-Path $p) {
        try { return @(Get-Content $p -Raw | ConvertFrom-Json) }
        catch { return @() }
    }
    return @()
}

function AgeBadge($ageSec) {
    if ($ageSec -ge 86400) { $color = '#ff4757' }
    elseif ($ageSec -ge 3600) { $color = '#ffa502' }
    else { $color = '#2ed573' }
    $ago = switch ($ageSec) {
        { $_ -ge 86400 } { '{0:n1} d' -f ($_ / 86400) }
        { $_ -ge 3600 }  { '{0:n1} h' -f ($_ / 3600) }
        { $_ -ge 60 }    { '{0:n1} m' -f ($_ / 60) }
        default          { '{0}s' -f $_ }
    }
    return "<span style='color:$color;font-weight:600'>$ago</span>"
}

function JsonTable($obj, $take = 10) {
    $rows = @($obj | Select-Object -First $take)
    if (-not $rows) { return '<em>None</em>' }
    $html = foreach ($row in $rows) {
        $row.PSObject.Properties | ForEach-Object {
            "<tr><td>$($_.Name)</td><td>$($_.Value)</td></tr>"
        }
    }
    return "<table><thead><tr><th>Key</th><th>Value</th></tr></thead><tbody>$($html -join '')</tbody></table>"
}

# ------------------------------------------------------------------
# Load data
# ------------------------------------------------------------------
$place = LoadJson 'context/_latest/placeholders.json'
$drift = LoadJson 'restore/DRIFT_REPORT.json'
$secr  = LoadJson 'restore/SECRETS_REPORT.json'
$bin   = LoadJson 'restore/BINARY_GUARD.json'
$lock  = LoadJson 'context/_latest/lock_age.json'
$own   = LoadJson 'context/_latest/ownership.json'

# ------------------------------------------------------------------
# Metrics
# ------------------------------------------------------------------
$block = @($place | Where-Object Severity -eq 'BLOCK').Count
$warn  = @($place | Where-Object Severity -eq 'WARN').Count
$info  = @($place | Where-Object Severity -eq 'INFO').Count

$lockAge = if ($lock -and $lock.LastWrite) { [int]([datetime]::UtcNow - [datetime]$lock.LastWrite).TotalSeconds } else { $null }

# ------------------------------------------------------------------
# HTML
# ------------------------------------------------------------------
$html = @"
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Exo-Suit Dashboard</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{
  --bg:#0b0f14; --bg2:#121820; --bg3:#0f141b;
  --border:#1f2a36; --text:#e6eef6; --accent:#8ad3ff;
  --red:#ff4757; --orange:#ffa502; --green:#2ed573;
  font-family:system-ui,Segoe UI,Roboto,Arial;
}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);padding:24px;line-height:1.4}
h1{margin-bottom:24px;font-size:28px}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:16px;margin:12px 0}
.card h2{font-size:20px;margin-bottom:12px}
.kv{display:flex;gap:12px;flex-wrap:wrap}
.kv>div{background:var(--bg3);border:1px solid var(--border);border-radius:10px;padding:12px 16px}
.kv .label{font-size:.9em;opacity:.7}
.kv .value{font-size:20px;font-weight:600}
table{width:100%;border-collapse:collapse}
th,td{padding:6px 8px;border-bottom:1px solid var(--border);text-align:left}
th{font-weight:600}
pre{background:var(--bg3);padding:12px;border-radius:8px;overflow:auto;font-size:13px}
</style>
</head>
<body>
<h1>Exo-Suit Dashboard</h1>

<!-- Status -->
<div class="card">
  <h2>Status</h2>
  <div class="kv">
    <div><span class="label">BLOCK</span><br><span class="value" style="color:var(--red)">$block</span></div>
    <div><span class="label">WARN</span><br><span class="value" style="color:var(--orange)">$warn</span></div>
    <div><span class="label">INFO</span><br><span class="value">$info</span></div>
    <div><span class="label">Drift</span><br><span class="value">$($drift.Count)</span></div>
    <div><span class="label">Secrets</span><br><span class="value">$($secr.Count)</span></div>
    <div><span class="label">Binary</span><br><span class="value">$($bin.Count)</span></div>
  </div>
</div>

<!-- Lock age -->
<div class="card">
  <h2>Lock file age</h2>
  $( if ($lockAge) { "<p>Last write $(AgeBadge $lockAge) ago</p>" } else { "<p>No lock file found</p>" } )
  <pre>$($lock | ConvertTo-Json -Depth 4)</pre>
</div>

<!-- Ownership -->
<div class="card">
  <h2>Ownership</h2>
  <pre>$($own | ConvertTo-Json -Depth 4)</pre>
</div>

<!-- Secrets -->
<div class="card">
  <h2>Secrets (top 10)</h2>
  $(JsonTable $secr)
</div>

<!-- Binary Guard -->
<div class="card">
  <h2>Binary Guard (top 10)</h2>
  $(JsonTable $bin)
</div>

</body>
</html>
"@

$html | Out-File 'restore/dashboard.html' -Encoding utf8
Write-Host "Dashboard updated → restore/dashboard.html"
