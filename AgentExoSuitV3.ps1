#requires -RunAsAdministrator
# Agent Exo-Suit V3.0 – Max-Perf & AI-Optimized
# Author: Your Name (with ❤ from Kimi)

[CmdletBinding()]
param(
    [switch]$Restore,
    [switch]$SkipGpu,          # Skip nvidia-smi calls if you know you don't have NVIDIA
    [switch]$SkipNetworkTweaks # Skip TCP/NetAdapter tuning
)

$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'

# ------------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------------
function Write-Status([string]$msg, [string]$icon = '⚡') {
    Write-Host "$icon $msg" -ForegroundColor Cyan
}

function Invoke-WithRetry([scriptblock]$action) {
    $attempt = 0
    while ($true) {
        try { return & $action }
        catch {
            $attempt++
            if ($attempt -gt 2) { throw }
            Start-Sleep 1
        }
    }
}

# ------------------------------------------------------------------
# Roll-back registry path store
# ------------------------------------------------------------------
$BACKUP_REG = 'HKCU:\SOFTWARE\AgentExoSuitV3'

function Backup-RegistryValue([string]$Path, [string]$Name) {
    $current = Get-ItemProperty -Path $Path -Name $Name -EA 0 | Select-Object -ExpandProperty $Name -EA 0
    if ($null -ne $current) {
        New-Item -Path $BACKUP_REG -Force | Out-Null
        Set-ItemProperty -Path $BACKUP_REG -Name "$Path\$Name" -Value $current
    }
}

function Restore-RegistryValue([string]$Path, [string]$Name) {
    $value = Get-ItemProperty -Path $BACKUP_REG -Name "$Path\$Name" -EA 0 | Select-Object -ExpandProperty "$Path\$Name" -EA 0
    if ($null -ne $value) {
        Set-ItemProperty -Path $Path -Name $Name -Value $value
    } else {
        Remove-ItemProperty -Path $Path -Name $Name -EA 0
    }
}

# ------------------------------------------------------------------
# Rollback / Restore
# ------------------------------------------------------------------
if ($Restore) {
    Write-Status '🔄 Rolling back all performance tweaks...' '🛠️'

    # Power plan
    Invoke-WithRetry { powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e } | Out-Null
    Invoke-WithRetry {
        powercfg -change -standby-timeout-ac 30
        powercfg -change -hibernate-timeout-ac 180
        powercfg -change -disk-timeout-ac 20
        powercfg -change -processor-min-state-ac 5
        powercfg -change -processor-min-state-dc 5
    } | Out-Null

    # Registry tweaks rollback
    Restore-RegistryValue 'HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl' 'Win32PrioritySeparation'
    Restore-RegistryValue 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\*' 'TcpAckFrequency'
    Restore-RegistryValue 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\*' 'TCPNoDelay'
    Restore-RegistryValue 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile' 'NetworkThrottlingIndex'
    Restore-RegistryValue 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile' 'SystemResponsiveness'

    # Scratch dir
    Remove-Item -Path $env:SCRATCH_DIR -Recurse -Force -EA 0

    Write-Status '✅ System restored to Balanced defaults' '🟢'
    exit 0
}

# ------------------------------------------------------------------
# Elevated check
# ------------------------------------------------------------------
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning 'Administrator rights required. Re-run as admin.'
    exit 1
}

# ------------------------------------------------------------------
# 1. Ultimate Performance plan
# ------------------------------------------------------------------
Write-Status '🚀 Activating Ultimate Performance plan...'
$ultimateGuid = (powercfg -list | Select-String 'Ultimate Performance' | % { ($_ -split '\s+')[3] })
if (-not $ultimateGuid) {
    $out = powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61
    $ultimateGuid = ($out -split '\s+')[-1]
    powercfg -changename $ultimateGuid 'Ultimate Performance' 'Agent Exo-Suit V3.0'
}
powercfg -setactive $ultimateGuid

# Disable sleep/hibernate
powercfg -change -standby-timeout-ac 0
powercfg -change -hibernate-timeout-ac 0
powercfg -change -disk-timeout-ac 0
powercfg -change -processor-min-state-ac 100
powercfg -change -processor-min-state-dc 100

# ------------------------------------------------------------------
# 2. GPU check (NVIDIA & AMD)
# ------------------------------------------------------------------
if (-not $SkipGpu) {
    Write-Status '🎮 Querying GPUs...'
    try {
        if (Get-Command nvidia-smi -EA 0) {
            nvidia-smi --query-gpu=name,driver_version,temperature.gpu,utilization.gpu --format=csv,noheader,nounits | ForEach-Object {
                Write-Status "NVIDIA GPU: $_"
            }
        } else {
            Write-Status 'No NVIDIA driver found, skipping nvidia-smi'
        }

        # AMD via ROCm-smi (if installed)
        if (Get-Command rocm-smi -EA 0) {
            rocm-smi --showproductname --showtemp --showuse | Where-Object { $_ -match 'GPU\[' } | ForEach-Object {
                Write-Status "AMD GPU: $_"
            }
        }
    } catch {
        Write-Warning 'GPU status check failed.'
    }
}

# ------------------------------------------------------------------
# 3. Registry & OS tweaks
# ------------------------------------------------------------------
Write-Status '🔧 Applying low-latency OS tweaks...'

# CPU scheduling
Backup-RegistryValue 'HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl' 'Win32PrioritySeparation'
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl' -Name 'Win32PrioritySeparation' -Value 38

# Network
if (-not $SkipNetworkTweaks) {
    Get-NetAdapter -Physical | ForEach-Object {
        $guid = $_.InterfaceGuid
        $key  = "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\$guid"
        Backup-RegistryValue $key 'TcpAckFrequency'
        Backup-RegistryValue $key 'TCPNoDelay'
        Set-ItemProperty -Path $key -Name 'TcpAckFrequency' -Value 1 -Type DWord
        Set-ItemProperty -Path $key -Name 'TCPNoDelay' -Value 1 -Type DWord
        Write-Status "Low-latency network applied to $($_.Name)"
    }

    # Multimedia class scheduler
    Backup-RegistryValue 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile' 'NetworkThrottlingIndex'
    Backup-RegistryValue 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile' 'SystemResponsiveness'
    Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile' -Name 'NetworkThrottlingIndex' -Value 0xffffffff -Type DWord
    Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile' -Name 'SystemResponsiveness' -Value 0 -Type DWord
}

# ------------------------------------------------------------------
# 4. Scratch & env variables
# ------------------------------------------------------------------
$env:SCRATCH_DIR = 'D:\scratch'
$env:NODE_OPTIONS = '--max-old-space-size=24576'   # 24 GB heap
$env:PIP_CACHE_DIR = "$env:SCRATCH_DIR\pip"
$env:NPM_CONFIG_CACHE = "$env:SCRATCH_DIR\npm"
$env:HF_HOME = "$env:SCRATCH_DIR\huggingface"

if (-not (Test-Path $env:SCRATCH_DIR)) {
    New-Item -ItemType Directory -Force -Path $env:SCRATCH_DIR | Out-Null
}

# ------------------------------------------------------------------
# 5. Summary
# ------------------------------------------------------------------
Write-Host ''
Write-Host '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' -ForegroundColor Green
Write-Host '🎯 Agent Exo-Suit V3.0 – CONFIGURED' -ForegroundColor Green
Write-Host '  ✅ Ultimate Performance: Active'
Write-Host '  ✅ Sleep/Hibernate: Disabled'
Write-Host '  ✅ CPU min state: 100 %'
Write-Host '  ✅ GPU status: Queried'
Write-Host '  ✅ OS latency tweaks: Applied'
Write-Host '  ✅ Scratch: ' -NoNewline; Write-Host $env:SCRATCH_DIR -ForegroundColor Yellow
Write-Host '  ✅ Node heap: 24 GB'
Write-Host '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' -ForegroundColor Green
Write-Host ''
Write-Host 'To restore default settings:' -ForegroundColor Magenta
Write-Host '  .\AgentExoSuitV3.ps1 -Restore' -ForegroundColor Magenta
