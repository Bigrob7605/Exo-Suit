# Max-Perf Script for Agent Exo-Suit V2.0
# Enables Ultimate Performance mode and optimizes system for AI work

param(
    [switch]$restore = $false
)

Write-Host " Configuring system performance for Agent Exo-Suit V2.0..."

if ($restore) {
    Write-Host " Restoring normal performance mode..."
    
    # Restore balanced power plan
    powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e
    
    # Re-enable sleep timers
    powercfg -change -standby-timeout-ac 30
    powercfg -change -hibernate-timeout-ac 180
    
    Write-Host " Normal performance mode restored"
    exit 0
}

# Check if running as administrator
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "This script requires administrator privileges for power management changes."
    Write-Warning "Running in limited mode..."
}

Write-Host " Enabling Ultimate Performance mode..."

# Enable Ultimate Performance power plan
try {
    # Check if Ultimate Performance exists
    $ultimateGuid = $null
    $powerPlans = powercfg -list | Select-String "Ultimate Performance"
    
    if ($powerPlans) {
        $ultimateGuid = ($powerPlans.ToString() -split '\s+')[3]
        Write-Host "Found existing Ultimate Performance plan: $ultimateGuid"
    } else {
        # Create Ultimate Performance plan
        Write-Host "Creating Ultimate Performance power plan..."
        $duplicateOutput = powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61
        $ultimateGuid = ($duplicateOutput -split '\s+')[-1]
        powercfg -changename $ultimateGuid "Ultimate Performance" "Agent Exo-Suit V2.0 - Maximum Performance Mode"
    }
    
    # Set as active plan
    powercfg -setactive $ultimateGuid
    Write-Host " Ultimate Performance mode activated"
    
} catch {
    Write-Warning "Could not set Ultimate Performance mode: $($_.Exception.Message)"
}

# Disable sleep and hibernate
Write-Host " Disabling sleep and hibernate..."
try {
    powercfg -change -standby-timeout-ac 0
    powercfg -change -hibernate-timeout-ac 0
    Write-Host " Sleep and hibernate disabled"
} catch {
    Write-Warning "Could not disable sleep timers: $($_.Exception.Message)"
}

# Optimize disk performance
Write-Host " Optimizing disk performance..."
try {
    # Set disk timeout to never
    powercfg -change -disk-timeout-ac 0
    powercfg -change -disk-timeout-dc 0
    Write-Host " Disk timeout optimized"
} catch {
    Write-Warning "Could not optimize disk settings: $($_.Exception.Message)"
}

# Optimize CPU performance
Write-Host " Optimizing CPU performance..."
try {
    # Set CPU min state to 100%
    powercfg -change -processor-min-state-ac 100
    powercfg -change -processor-min-state-dc 100
    Write-Host " CPU performance optimized"
} catch {
    Write-Warning "Could not optimize CPU settings: $($_.Exception.Message)"
}

# Check GPU status
Write-Host " Checking GPU status..."
try {
    $gpuInfo = nvidia-smi --query-gpu=name,driver_version,temperature.gpu,utilization.gpu --format=csv,noheader,nounits 2>$null
    if ($gpuInfo) {
        Write-Host " GPU detected: $gpuInfo"
    } else {
        Write-Host " NVIDIA GPU not detected or nvidia-smi not available"
    }
} catch {
    Write-Host " Could not check GPU status"
}

# Set environment variables for performance
Write-Host " Setting performance environment variables..."
$env:SCRATCH_DIR = "D:\scratch"
$env:NODE_OPTIONS = "--max-old-space-size=12288"
$env:PIP_CACHE_DIR = "$env:SCRATCH_DIR\pip"
$env:NPM_CONFIG_CACHE = "$env:SCRATCH_DIR\npm"

# Create scratch directory if it doesn't exist
if (-not (Test-Path $env:SCRATCH_DIR)) {
    Write-Host "Creating scratch directory: $env:SCRATCH_DIR"
    try {
        New-Item -ItemType Directory -Force -Path $env:SCRATCH_DIR | Out-Null
    } catch {
        Write-Warning "Could not create scratch directory. Using temporary directory."
        $env:SCRATCH_DIR = $env:TEMP
    }
}

# Performance summary
Write-Host ""
Write-Host " Performance Configuration Summary:"
Write-Host "   Ultimate Performance mode: Active"
Write-Host "   Sleep/Hibernate: Disabled"
Write-Host "   Disk timeout: Optimized"
Write-Host "   CPU performance: Maximized"
Write-Host "   Scratch directory: $env:SCRATCH_DIR"
Write-Host "   Node.js memory: 12GB"
Write-Host ""
Write-Host " System optimized for Agent Exo-Suit V2.0!"
Write-Host "Run './ops/normal-perf.ps1' to restore normal settings when done."
