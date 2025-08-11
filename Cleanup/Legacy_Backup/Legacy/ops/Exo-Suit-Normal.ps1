#
# Normal-Mode Script  Exo-Suit V2.0  Kimi Edition                 
# Drops the AI nitro tune and brings the rig back to daily-driver mode. 
#
#Requires -RunAsAdministrator

param(
    [switch]$Quiet = $false
)

if (-not $Quiet) {
    Write-Host " Exo-Suit V2.0  Back to Balanced Mode" -ForegroundColor Cyan
    Write-Host ("=" * 52)
}

# ---------- Helper to run PowerCfg with error capture ----------
function Invoke-PowerCfg([string]$ArgsStr) {
    $code = (Start-Process -FilePath "powercfg.exe" -ArgumentList $ArgsStr -Wait -NoNewWindow -PassThru).ExitCode
    if ($code -ne 0) { throw "powercfg exited with code $code" }
}

# ---------- 1. Balanced GUID (Microsoft default) ----------
$balanced = "381b4222-f694-41f0-9685-ff5bb260df2e"

try {
    Invoke-PowerCfg "-setactive $balanced"
    if (-not $Quiet) { Write-Host " Balanced power plan activated" -ForegroundColor Green }
} catch {
    Write-Warning " Could not switch to balanced plan: $_"
}

# ---------- 2. Sleep timers ----------
try {
    Invoke-PowerCfg "-change -standby-timeout-ac 30"
    Invoke-PowerCfg "-change -hibernate-timeout-ac 180"
    if (-not $Quiet) { Write-Host " Sleep timers restored (30 / 180 min)" -ForegroundColor Green }
} catch {
    Write-Warning " Could not set sleep timers: $_"
}

# ---------- 3. Disk timeouts ----------
try {
    Invoke-PowerCfg "-change -disk-timeout-ac 0"
    Invoke-PowerCfg "-change -disk-timeout-dc 0"
    if (-not $Quiet) { Write-Host " Disk idle timeouts disabled" -ForegroundColor Green }
} catch {
    Write-Warning " Could not set disk timeouts: $_"
}

# ---------- 4. CPU limits ----------
try {
    Invoke-PowerCfg "-change -processor-min-state-ac 5"
    Invoke-PowerCfg "-change -processor-min-state-dc 5"
    Invoke-PowerCfg "-change -processor-max-state-ac 100"
    Invoke-PowerCfg "-change -processor-max-state-dc 100"
    if (-not $Quiet) { Write-Host " CPU floors/ceilings reset (5 %  100 %)" -ForegroundColor Green }
} catch {
    Write-Warning " Could not reset CPU states: $_"
}

# ---------- 5. Optional: re-enable Speed Shift (if it was off) ----------
try {
    Invoke-PowerCfg "-setacvalueindex scheme_current sub_processor PERFBOOSTMODE 1"
    Invoke-PowerCfg "-setdcvalueindex scheme_current sub_processor PERFBOOSTMODE 1"
    if (-not $Quiet) { Write-Host " Intel Speed Shift / AMD CPB re-enabled" -ForegroundColor Green }
} catch {
    Write-Warning " Could not tweak boost policy: $_"
}

# ---------- 6. Optional: re-enable Core Parking ----------
try {
    Invoke-PowerCfg "-setacvalueindex scheme_current sub_processor CPMINCORES 0"
    Invoke-PowerCfg "-setdcvalueindex scheme_current sub_processor CPMINCORES 0"
    Invoke-PowerCfg "-setacvalueindex scheme_current sub_processor CPMAXCORES 100"
    Invoke-PowerCfg "-setdcvalueindex scheme_current sub_processor CPMAXCORES 100"
    if (-not $Quiet) { Write-Host " Core parking unlocked" -ForegroundColor Green }
} catch {
    Write-Warning " Could not reset core parking: $_"
}

if (-not $Quiet) {
    Write-Host ("-" * 52) -ForegroundColor DarkGray
    Write-Host " Exo-Suit back to street-legal specs  enjoy the chill ride!" -ForegroundColor Cyan
}
