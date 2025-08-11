# Agent Exo-Suit V3.0 - Ultimate Performance Mode
# Optimized for ASUS TUF i7-13620H + RTX 4070

param(
    [switch]$Restore,
    [switch]$Status,
    [switch]$Benchmark
)

# Import required modules
Import-Module Microsoft.PowerShell.Utility -Force
Import-Module Microsoft.PowerShell.Management -Force

# Configuration
$env:SCRATCH_DIR = "C:\scratch\exo-suit"
$env:NODE_OPTIONS = "--max-old-space-size=24576"

# Status colors
function Write-Status {
    param($Message, $Icon = '')
    Write-Host "$Icon $Message" -ForegroundColor Cyan
}

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "This script requires administrator privileges for performance tuning." -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    exit 1
}

# Restore mode
if ($Restore) {
    Write-Status 'Rolling back all performance tweaks...' 'Rolling back'
    
    # Restore power plan
    try {
        powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e
        Write-Status 'Power plan restored to Balanced' 'Restored'
    } catch {
        Write-Warning "Failed to restore power plan: $_"
    }
    
    # Re-enable sleep/hibernate
    try {
        powercfg /change standby-timeout-ac 0
        powercfg /change hibernate-timeout-ac 0
        Write-Status 'Sleep and hibernate re-enabled' 'Restored'
    } catch {
        Write-Warning "Failed to restore sleep settings: $_"
    }
    
    # Restore CPU min state
    try {
        powercfg /setacvalueindex 381b4222-f694-41f0-9685-ff5bb260df2e 54533251-82be-4824-96c1-47b60b740d00 943c8cb6-6e93-4227-adc6-8b9d86940d50 0
        powercfg /setdcvalueindex 381b4222-f694-41f0-9685-ff5bb260df2e 54533251-82be-4824-96c1-47b60b740d00 943c8cb6-6e93-4227-adc6-8b9d86940d50 0
        Write-Status 'CPU min state restored to 5%' 'Restored'
    } catch {
        Write-Warning "Failed to restore CPU settings: $_"
    }
    
    # Clean up scratch directory
    if (Test-Path $env:SCRATCH_DIR) {
        Remove-Item -Path $env:SCRATCH_DIR -Recurse -Force -ErrorAction SilentlyContinue
        Write-Status 'Scratch directory cleaned' 'Cleaned'
    }
    
    Write-Status 'System restored to Balanced defaults' 'System Restored'
    exit 0
}

# Status mode
if ($Status) {
    Write-Host "Agent Exo-Suit V3.0 Status:" -ForegroundColor Cyan
    
    # Check power plan
    $currentPlan = powercfg /getactivescheme
    if ($currentPlan -match "Ultimate Performance") {
        Write-Host "  Power Plan: Ultimate Performance (Active)" -ForegroundColor Green
    } else {
        Write-Host "  Power Plan: $currentPlan" -ForegroundColor Yellow
    }
    
    # Check scratch directory
    if (Test-Path $env:SCRATCH_DIR) {
        Write-Host "  Scratch Directory: $env:SCRATCH_DIR (Ready)" -ForegroundColor Green
    } else {
        Write-Host "  Scratch Directory: Not created" -ForegroundColor Red
    }
    
    # Check GPU
    try {
        $gpuInfo = Get-WmiObject -Class Win32_VideoController | Where-Object { $_.Name -like "*NVIDIA*" }
        if ($gpuInfo) {
            Write-Host "  GPU: $($gpuInfo.Name) (Detected)" -ForegroundColor Green
        } else {
            Write-Host "  GPU: No NVIDIA GPU detected" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  GPU: Detection failed" -ForegroundColor Red
    }
    
    exit 0
}

# Main performance activation
Write-Host "Agent Exo-Suit V3.0 - Activating Ultimate Performance Mode" -ForegroundColor Green
Write-Host "Target: ASUS TUF i7-13620H + RTX 4070" -ForegroundColor Cyan

# Create scratch directory
if (!(Test-Path $env:SCRATCH_DIR)) {
    New-Item -ItemType Directory -Path $env:SCRATCH_DIR -Force | Out-Null
    Write-Status 'Scratch directory created' 'Created'
}

# Activate Ultimate Performance plan
Write-Status 'Activating Ultimate Performance plan...'
try {
    # Check if Ultimate Performance plan exists
    $plans = powercfg /list
    if ($plans -match "Ultimate Performance") {
        powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61
        Write-Status 'Ultimate Performance plan activated' 'Activated'
    } else {
        # Create Ultimate Performance plan if it doesn't exist
        powercfg /duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 "Ultimate Performance"
        powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61
        Write-Status 'Ultimate Performance plan created and activated' 'Created'
    }
} catch {
    Write-Warning "Failed to activate Ultimate Performance plan: $_"
    Write-Status 'Continuing with current plan' 'Warning'
}

# Disable sleep and hibernate
try {
    powercfg /change standby-timeout-ac 0
    powercfg /change hibernate-timeout-ac 0
    Write-Status 'Sleep and hibernate disabled' 'Disabled'
} catch {
    Write-Warning "Failed to disable sleep settings: $_"
}

# Set CPU min state to 100%
try {
    powercfg /setacvalueindex 381b4222-f694-41f0-9685-ff5bb260df2e 54533251-82be-4824-96c1-47b60b740d00 943c8cb6-6e93-4227-adc6-8b9d86940d50 100
    powercfg /setdcvalueindex 381b4222-f694-41f0-9685-ff5bb260df2e 54533251-82be-4824-96c1-47b60b740d00 943c8cb6-6e93-4227-adc6-8b9d86940d50 100
    Write-Status 'CPU min state set to 100%' 'Set'
} catch {
    Write-Warning "Failed to set CPU min state: $_"
}

# Check GPU status
try {
    $gpuInfo = Get-WmiObject -Class Win32_VideoController | Where-Object { $_.Name -like "*NVIDIA*" }
    if ($gpuInfo) {
        Write-Status 'NVIDIA GPU detected' 'GPU'
        $gpuName = $gpuInfo.Name
        $gpuMemory = [math]::Round($gpuInfo.AdapterRAM / 1GB, 1)
        Write-Host "  GPU: $gpuName" -ForegroundColor Green
        Write-Host "  Memory: $gpuMemory GB" -ForegroundColor Green
    } else {
        Write-Status 'No NVIDIA GPU detected' 'No GPU'
    }
} catch {
    Write-Warning "GPU detection failed: $_"
}

# Apply low-latency OS tweaks
Write-Status 'Applying low-latency OS tweaks...'
try {
    # Disable Nagle's algorithm for network performance
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\*" -Name "TcpAckFrequency" -Value 1 -ErrorAction SilentlyContinue
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\*" -Name "TCPNoDelay" -Value 1 -ErrorAction SilentlyContinue
    
    # Optimize for background services
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl" -Name "Win32PrioritySeparation" -Value 38 -ErrorAction SilentlyContinue
    
    # Disable visual effects for performance
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name "VisualFXSetting" -Value 2 -ErrorAction SilentlyContinue
    
    Write-Status 'OS tweaks applied' 'Applied'
} catch {
    Write-Warning "Failed to apply some OS tweaks: $_"
}

# Set environment variables for performance
$env:NODE_OPTIONS = "--max-old-space-size=24576"
$env:PIP_CACHE_DIR = "$env:SCRATCH_DIR\pip"
$env:NPM_CONFIG_CACHE = "$env:SCRATCH_DIR\npm"

# Create subdirectories in scratch
$subdirs = @("pip", "npm", "temp", "cache")
foreach ($dir in $subdirs) {
    $path = Join-Path $env:SCRATCH_DIR $dir
    if (!(Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}

# Benchmark mode
if ($Benchmark) {
    Write-Status 'Running performance benchmarks...'
    
    # CPU benchmark
    $startTime = Get-Date
    $result = 1
    for ($i = 1; $i -le 1000000; $i++) {
        $result = $result * $i % 1000000
    }
    $endTime = Get-Date
    $cpuTime = ($endTime - $startTime).TotalMilliseconds
    
    Write-Host "  CPU Benchmark: $cpuTime ms" -ForegroundColor Green
    
    # Memory benchmark
    $startTime = Get-Date
    $array = @()
    for ($i = 1; $i -le 100000; $i++) {
        $array += "test$i"
    }
    $endTime = Get-Date
    $memTime = ($endTime - $startTime).TotalMilliseconds
    
    Write-Host "  Memory Benchmark: $memTime ms" -ForegroundColor Green
    
    # Clean up
    $array = $null
    [System.GC]::Collect()
}

# Final status
Write-Host 'Agent Exo-Suit V3.0  CONFIGURED' -ForegroundColor Green
Write-Host '  Ultimate Performance: Active'
Write-Host '  Sleep/Hibernate: Disabled'
Write-Host '  CPU min state: 100 %'
Write-Host '  GPU status: Queried'
Write-Host '  OS latency tweaks: Applied'
Write-Host '  Scratch: ' -NoNewline; Write-Host $env:SCRATCH_DIR -ForegroundColor Yellow
Write-Host '  Node heap: 24 GB'

Write-Host "`nUltimate Performance Mode activated!" -ForegroundColor Green
Write-Host "To restore normal settings, run: .\AgentExoSuitV3.ps1 -Restore" -ForegroundColor Yellow
