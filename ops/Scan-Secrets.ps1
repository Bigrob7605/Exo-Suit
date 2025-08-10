<#
.SYNOPSIS
  Fast, parallel secret scanner with SARIF/JUnit output.
.EXAMPLE
  .\Scan-Secrets.ps1 -Strict
#>
[CmdletBinding()]
param(
  [switch]$Strict,
  [string]$Root = (Get-Location),
  [string]$OutDir = "$Root\restore",
  [ValidateSet('sarif','legacy','junit','auto')]
  [string]$Format = 'auto'          # auto = legacy JSON for back-compat
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ----------------------------- CONFIG ---------------------------------
$maxFileSize   = 1MB
$maxMatches    = 50                # per rule / file
$entropyThresh = 4.2               # Shannon entropy for generic secrets
$regexTimeout  = [timespan]::FromSeconds(2)

$rules = @(
  @{ name='AWS_ACCESS_KEY_ID';     rx='^AKIA[0-9A-Z]{16}$' },
  @{ name='AWS_SECRET_ACCESS_KEY'; rx='(?is)aws_secret_access_key.{0,10}([A-Za-z0-9/+=]{40})'; entropy=4.5 },
  @{ name='GCP_SA_KEY';            rx='(?is)"type"\s*:\s*"service_account"' },
  @{ name='RSA_PRIVATE_KEY';       rx='-----BEGIN RSA PRIVATE KEY----' },
  @{ name='EC_PRIVATE_KEY';        rx='-----BEGIN EC PRIVATE KEY----' },
  @{ name='OPENSSH_PRIVATE_KEY';   rx='-----BEGIN OPENSSH PRIVATE KEY----' },
  @{ name='DSA_PRIVATE_KEY';       rx='-----BEGIN DSA PRIVATE KEY----' },
  @{ name='JWT';                   rx='^eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$' },
  @{ name='SLACK_TOKEN';           rx='^xox[baprs]-[A-Za-z0-9-]+$' },
  @{ name='GITHUB_CLASSIC';        rx='^ghp_[A-Za-z0-9]{36,}$' },
  @{ name='GITHUB_FINE';           rx='^github_pat_[A-Za-z0-9_]{36,}$' },
  @{ name='ENV_GENERIC';           rx='(?im)^[A-Z_]{3,}\s*=\s*([A-Za-z0-9/+=]{20,})$'; entropy=$entropyThresh }
)

$excludeDir = @(
  'node_modules','dist','build','target','bin','obj','__pycache__',
  '.git','restore','context','rag','telemetry','cache'
)

$excludeExt = @('.dll','.exe','.png','.jpg','.gif','.ico','.zip','.tar','.gz','.mo','.so')

$allowList = @{
  # literal substrings that suppress a finding
  'ENV_GENERIC' = @('EXAMPLE', 'PLACEHOLDER', 'YOUR_SECRET_HERE')
}
# ----------------------------------------------------------------------

# ---------- helpers ----------
function Get-ShannonEntropy([string]$s){
  if(!$s){return 0}
  $freq = @{}
  foreach($c in $s.ToCharArray()){ $freq[$c]++ }
  $len = $s.Length
  $entropy = 0
  foreach($v in $freq.Values){
    $p = $v/$len
    $entropy -= $p * [Math]::Log($p,2)
  }
  $entropy
}

function Test-AllowList($rule,$value){
  foreach($pat in $allowList[$rule]){ if($value.Contains($pat)){ return $true } }
  $false
}

# ---------- parallel scan ----------
$jobs = [System.Collections.Concurrent.ConcurrentBag[psobject]]::new()

$scan = {
  param($file,$rules,$opts)
  $list = [System.Collections.Generic.List[psobject]]::new()
  try{
    if($file.Length -gt $opts.maxFileSize){ return }
    $txt = [IO.File]::ReadAllText($file.FullName)
    foreach($r in $rules){
      $rx = [regex]::new($r.rx, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase, $opts.regexTimeout)
      $ms = $rx.Matches($txt)
      for($i=0;$i -lt [Math]::Min($ms.Count,$opts.maxMatches);$i++){
        $m = $ms[$i]
        $secret = if($m.Groups.Count -gt 1){$m.Groups[1].Value} else {$m.Value}
        if($r.entropy -and (Get-ShannonEntropy $secret) -lt $r.entropy){ continue }
        if(Test-AllowList $r.name $secret){ continue }
        $list.Add([pscustomobject]@{
          File     = $file.FullName
          Rule     = $r.name
          Sample   = $secret.Substring(0,[Math]::Min($secret.Length,60))
          Severity = if($r.name -eq 'ENV_GENERIC'){'WARN'}else{'BLOCK'}
          Line     = ($txt.Substring(0,$m.Index) -split "`n").Count
          Entropy  = (Get-ShannonEntropy $secret)
        })
      }
    }
  }catch{}
  ,$list
}

# ---------- gather files ----------
$files = Get-ChildItem -LiteralPath $Root -Recurse -File | Where-Object {
  $_.Extension -notin $excludeExt -and
  ($_.FullName -split '\\' | Where-Object { $_ -in $excludeDir }).Count -eq 0
}

# ---------- runspace pool ----------
$pool = [runspacefactory]::CreateRunspacePool(1,[Environment]::ProcessorCount)
$pool.Open()
$tasks = foreach($f in $files){
  $ps = [powershell]::Create().AddScript($scan).AddArgument($f).AddArgument($rules).AddArgument(@{
      maxFileSize=$maxFileSize;maxMatches=$maxMatches;regexTimeout=$regexTimeout
  })
  $ps.RunspacePool = $pool
  @{ ps=$ps; ar=$ps.BeginInvoke() }
}
$hits = foreach($t in $tasks){
  $t.ps.EndInvoke($t.ar) | ForEach-Object { $_ }
  $t.ps.Dispose()
}
$pool.Close()

# ---------- output ----------
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
switch($Format){
  'legacy' {
    $outFile = "$OutDir\SECRETS_REPORT.json"
    $hits | Select-Object File,Rule,Sample,Severity | ConvertTo-Json -Depth 4 | Out-File $outFile -Encoding utf8
    break
  }
  'sarif' {
    $outFile = "$OutDir\secrets.sarif"
    $sarif = @{
      version = "2.1.0"
      $schema = "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json"
      runs = @(@{
        tool = @{ driver = @{ name = "secrets-scanner"; version = "2.0" } }
        results = foreach($h in $hits){
          @{
            ruleId = $h.Rule
            level  = if($h.Severity -eq 'BLOCK'){'error'}else{'warning'}
            message = @{ text = "Secret detected: $($h.Sample)" }
            locations = @(@{
              physicalLocation = @{ artifactLocation = @{ uri = [uri]$h.File }; region = @{ startLine = $h.Line } }
            })
          }
        }
      })
    }
    $sarif | ConvertTo-Json -Depth 10 | Out-File $outFile -Encoding utf8
    break
  }
  'junit' {
    $outFile = "$OutDir\secrets.junit.xml"
    $cases = $hits | Group-Object Rule | ForEach-Object {
      "<testcase name='$($_.Name)'><failure>Found $($_.Count) hits</failure></testcase>"
    }
    $xml = @"
<testsuites>
  <testsuite name="secrets" tests="$($hits.Count)" failures="$($hits.Count)">
    $($cases -join "`n")
  </testsuite>
</testsuites>
"@
    $xml | Out-File $outFile -Encoding utf8
    break
  }
  default {
    $outFile = "$OutDir\SECRETS_REPORT.json"
    $hits | Select-Object File,Rule,Sample,Severity | ConvertTo-Json -Depth 4 | Out-File $outFile -Encoding utf8
  }
}

# ---------- summary ----------
$blocks = $hits | Where-Object Severity -eq 'BLOCK'
if($blocks.Count -or $Strict){
  Write-Error "Secrets found. Report → $outFile"
  exit 3
}elseif($hits.Count){
  Write-Warning "Secrets WARN found. Report → $outFile"
}else{
  Write-Host "Secrets scan clean."
}
