#Requires -Version 5.1
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
function LoadJson([string]$Path) {
    if (-not (Test-Path $Path)) { return @() }
    try   { return Get-Content $Path -Raw -Encoding UTF8 | ConvertFrom-Json -ErrorAction Stop }
    catch { Write-Warning "Invalid JSON: $Path"; return @() }
}

function AgeBadge([int]$AgeSec) {
    if ($AgeSec -le 0) { return '<span style="color:#2ed573;font-weight:600">just now</span>' }
    $color = if ($AgeSec -ge 86400) { '#ff4757' }
             elseif ($AgeSec -ge 3600) { '#ffa502' }
             else { '#2ed573' }
    $ago = switch ($AgeSec) {
        { $_ -ge 86400 } { '{0:n1} d' -f ($_ / 86400) }
        { $_ -ge 3600 }  { '{0:n1} h' -f ($_ / 3600) }
        { $_ -ge 60 }    { '{0:n1} m' -f ($_ / 60) }
        default          { '{0}s' -f $_ }
    }
    return "<span style='color:$color;font-weight:600'>$ago ago</span>"
}

function JsonTable($Object, [int]$Take = 10) {
    $rows = @($Object | Select-Object -First $Take)
    if (-not $rows) { return '<em>None</em>' }
    [System.Text.StringBuilder]$sb = [System.Text.StringBuilder]::new()
    [void]$sb.Append('<table><thead><tr><th>Key</th><th>Value</th></tr></thead><tbody>')
    foreach ($row in $rows) {
        foreach ($prop in $row.PSObject.Properties) {
            $key   = [System.Security.SecurityElement]::Escape($prop.Name)
            $value = [System.Security.SecurityElement]::Escape($prop.Value -is [array] ?
                                                                ($prop.Value -join ', ') :
                                                                "$($prop.Value)")
            [void]$sb.Append("<tr><td>$key</td><td>$value</td></tr>")
        }
    }
    [void]$sb.Append('</tbody></table>')
    return $sb.ToString()
}

# -----------------------------------------------------------------------------
# Data
# -----------------------------------------------------------------------------
$place = LoadJson "$PSScriptRoot/../context/_latest/placeholders.json"
$drift = LoadJson "$PSScriptRoot/../restore/DRIFT_REPORT.json"
$secr  = LoadJson "$PSScriptRoot/../restore/SECRETS_REPORT.json"
$bin   = LoadJson "$PSScriptRoot/../restore/BINARY_GUARD.json"
$lock  = LoadJson "$PSScriptRoot/../context/_latest/lock_age.json"
$own   = LoadJson "$PSScriptRoot/../context/_latest/ownership.json"

# -----------------------------------------------------------------------------
# Metrics
# -----------------------------------------------------------------------------
[int]$block = if ($place) { ($place | Where-Object Severity -eq 'BLOCK').Count } else { 0 }
[int]$warn  = if ($place) { ($place | Where-Object Severity -eq 'WARN').Count } else { 0 }
[int]$info  = if ($place) { ($place | Where-Object Severity -eq 'INFO').Count } else { 0 }

[int]$lockAge = if ($lock -and $lock.AgeDays) {
    [int]($lock.AgeDays * 86400)
} else { -1 }

# -----------------------------------------------------------------------------
# HTML
# -----------------------------------------------------------------------------
$html = @"
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="color-scheme" content="dark">
  <title>Exo-Suit Dashboard</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3EROBOT%3C/text%3E%3C/svg%3E">
  <style>
    :root{
      --bg:#0b0f14; --bg2:#121820; --bg3:#0f141b;
      --border:#1f2a36; --text:#e6eef6; --accent:#8ad3ff;
      --red:#ff4757; --orange:#ffa502; --green:#2ed573;
      font-family:system-ui,"Segoe UI",Roboto,Arial;
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
    pre{background:var(--bg3);padding:12px;border-radius:8px;overflow:auto;font-size:13px;font-family:Consolas,"Courier New",monospace}
    ::-webkit-scrollbar{width:8px;height:8px}
    ::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
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
      <div><span class="label">Drift</span><br><span class="value">$(if ($drift) { $drift.Count } else { 0 })</span></div>
      <div><span class="label">Secrets</span><br><span class="value">$(if ($secr) { $secr.Count } else { 0 })</span></div>
      <div><span class="label">Binary</span><br><span class="value">$(if ($bin) { $bin.Count } else { 0 })</span></div>
    </div>
  </div>

  <!-- Lock age -->
  <div class="card">
    <h2>Lock file age</h2>
    $(if ($lockAge -ge 0) { "<p>Last write $(AgeBadge $lockAge)</p>" } else { "<p>No lock file found</p>" })
    <pre>$($lock | ConvertTo-Json -Depth 100)</pre>
  </div>

  <!-- Ownership -->
  <div class="card">
    <h2>Ownership</h2>
    <pre>$($own | ConvertTo-Json -Depth 100)</pre>
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

# Atomic write
$tmp = "$PSScriptRoot/../restore/dashboard.html.tmp"
$html | Out-File -FilePath $tmp -Encoding utf8
Move-Item -Path $tmp -Destination "$PSScriptRoot/../restore/dashboard.html" -Force
Write-Host "Dashboard updated  restore/dashboard.html"
