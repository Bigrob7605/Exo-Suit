param([switch]$strict)

$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
New-Item -ItemType Directory -Force -Path 'restore' | Out-Null

# Patterns (tight, no false positives on common hashes)
$rules = @(
  @{name='AWS_ACCESS_KEY_ID';   rx='AKIA[0-9A-Z]{16}'},
  @{name='AWS_SECRET_ACCESS_KEY';rx='(?i)aws.?secret.?access.?key[^a-zA-Z0-9]{0,3}([A-Za-z0-9/+=]{40})'},
  @{name='GCP_SERVICE_KEY';     rx='"type":\s*"service_account"'},
  @{name='PRIVATE_KEY';         rx='-----BEGIN (RSA|EC|OPENSSH|DSA) PRIVATE KEY-----'},
  @{name='JWT';                  rx='eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}'},
  @{name='SLACK_TOKEN';         rx='xox[baprs]-[A-Za-z0-9\-]{10,}'},
  @{name='GITHUB_TOKEN';        rx='ghp_[A-Za-z0-9]{36,}'},
  @{name='.ENV_ASSIGN';         rx='(?im)^[A-Z0-9_]{3,}\s*=\s*[^#\s].{8,}$'}
)

$exclude = @(
  'node_modules','dist','build','target','bin','obj','__pycache__',
  '.git','context','rag','restore','telemetry','cache','gpu_rag_env'
)

$files = Get-ChildItem -Recurse -File | Where-Object {
  $p = $_.FullName.ToLower()
  -not ($exclude | Where-Object { $p -like "*\$_*" })
}

$hits = @()
foreach ($f in $files) {
  try {
    $txt = Get-Content -Raw -Encoding UTF8 -EA Stop $f.FullName
    if (-not $txt) { continue }
  } catch { continue }
  foreach ($r in $rules) {
    if (-not $r.rx) { continue }
    $m = [regex]::Matches($txt, $r.rx)
    foreach ($x in $m) {
      $hits += [pscustomobject]@{
        file = $f.FullName
        rule = $r.name
        sample = $x.Value.Substring(0, [math]::Min($x.Value.Length, 60))
        severity = if ($r.name -eq '.ENV_ASSIGN') { 'WARN' } else { 'BLOCK' }
      }
    }
  }
}

$path = 'restore/SECRETS_REPORT.json'
$hits | ConvertTo-Json -Depth 4 | Out-File $path -Encoding utf8
if ($hits.Count -gt 0) {
  $blocks = @($hits | Where-Object severity -eq 'BLOCK')
  if ($blocks.Count -gt 0 -or $strict) {
    Write-Error "Secrets found. See $path"
    exit 3
  } else {
    Write-Warning "Secrets WARN found. See $path"
  }
} else {
  Write-Host "Secrets scan clean."
}
