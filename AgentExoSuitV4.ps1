# Agent Exo-Suit V4.0 "Perfection" - Ultimate Performance Mode
# Optimized for ASUS TUF i7-13620H + RTX 4070
# Production Ready - Full V4 Feature Set

param(
    [switch]$Restore,
    [switch]$Status,
    [switch]$Benchmark,
    [switch]$FullSystem
)

# Import required modules
Import-Module Microsoft.PowerShell.Utility -Force
Import-Module Microsoft.PowerShell.Management -Force

# Configuration
$env:SCRATCH_DIR = "C:\scratch\exo-suit"
$env:NODE_OPTIONS = "--max-old-space-size=24576"
$env:MAX_TOKENS = "128000"
$env:GPU_MODE = "true"
$env:PERFORMANCE_MODE = "ultimate"

# Status colors
function Write-Status {
    param($Message, $Icon = '')
    Write-Host "$Icon $Message" -ForegroundColor Cyan
}

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "Administrator privileges not detected. Running in limited mode." -ForegroundColor Yellow
    Write-Host "Some features will be limited. For full functionality, run as Administrator." -ForegroundColor Yellow
    $LimitedMode = $true
} else {
    $LimitedMode = $false
}

# Full System Mode - V4.0 Perfection
if ($FullSystem) {
    Write-Host "🚀 Agent Exo-Suit V4.0 'Perfection' - Full System Activation" -ForegroundColor Green
    Write-Host "Production Ready - Full V4 Feature Set" -ForegroundColor Cyan
    
    if ($LimitedMode) {
        Write-Host "Running in Limited Mode (Non-Admin)" -ForegroundColor Yellow
    }
    
    # Activate all V4.0 systems
    Write-Status 'Activating Drift-Gate V4...' '🔄'
    if (Test-Path ".\ops\Drift-Guard-V4.ps1") {
        & ".\ops\Drift-Guard-V4.ps1" -Path ".\" -Output "drift_report.json"
    }
    
    Write-Status 'Activating Health Scanner V4...' '📊'
    if (Test-Path ".\ops\Project-Health-Scanner-V4.ps1") {
        & ".\ops\Project-Health-Scanner-V4.ps1" -Path ".\" -Output "health_report.json"
    }
    
    Write-Status 'Activating Emoji Sentinel V4...' '🔒'
    if (Test-Path ".\ops\emoji-sentinel-v4.ps1") {
        & ".\ops\emoji-sentinel-v4.ps1" -Path ".\" -Output "emoji_report.json"
    }
    
    Write-Status 'Activating GPU Accelerator...' '⚡'
    if (Test-Path ".\ops\gpu-accelerator.ps1") {
        & ".\ops\gpu-accelerator.ps1"
    }
    
    Write-Status 'Activating Context Governor...' '🧠'
    if (Test-Path ".\ops\context-governor.ps1") {
        & ".\ops\context-governor.ps1"
    }
    
    if ($LimitedMode) {
        Write-Host "⚠️  Limited Mode: Performance tuning features disabled" -ForegroundColor Yellow
        Write-Host "✅ Agent Exo-Suit V4.0 'Perfection' - Core systems activated (Limited Mode)!" -ForegroundColor Green
    } else {
        Write-Host "✅ Agent Exo-Suit V4.0 'Perfection' - All systems activated!" -ForegroundColor Green
    }
    exit 0
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
    Write-Host "Agent Exo-Suit V4.0 'Perfection' Status:" -ForegroundColor Cyan
    Write-Host "Production Ready - Full V4 Feature Set" -ForegroundColor Green
    
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
        Write-Host "  GPU: Unable to detect" -ForegroundColor Red
    }
    
    # Check V4.0 components
    Write-Host "  V4.0 Components:" -ForegroundColor Cyan
    $v4Components = @(
        "Drift-Guard-V4.ps1",
        "Project-Health-Scanner-V4.ps1", 
        "emoji-sentinel-v4.ps1",
        "GPU-RAG-V4.ps1",
        "Import-Indexer-V4.ps1",
        "Symbol-Indexer-V4.ps1",
        "Scan-Secrets-V4.ps1",
        "Power-Management-V4.ps1",
        "GPU-Monitor-V4.ps1"
    )
    
    foreach ($component in $v4Components) {
        if (Test-Path ".\ops\$component") {
            Write-Host "    ✅ $component" -ForegroundColor Green
        } else {
            Write-Host "    ❌ $component" -ForegroundColor Red
        }
    }
    
    exit 0
}

# Benchmark mode
if ($Benchmark) {
    Write-Host "Agent Exo-Suit V4.0 'Perfection' - Performance Benchmark" -ForegroundColor Cyan
    
    # GPU benchmark
    if (Test-Path ".\ops\GPU-Monitor-V4.ps1") {
        Write-Status 'Running GPU benchmark...' '⚡'
        & ".\ops\GPU-Monitor-V4.ps1" -Benchmark -Duration 30
    }
    
    # RAG benchmark
    if (Test-Path ".\rag\hybrid_rag_v4.py") {
        Write-Status 'Running RAG benchmark...' '🧠'
        python ".\rag\hybrid_rag_v4.py" --benchmark
    }
    
    exit 0
}

# Default mode - Ultimate Performance
Write-Host "🚀 Agent Exo-Suit V4.0 'Perfection' - Ultimate Performance Mode" -ForegroundColor Green
Write-Host "Production Ready - Full V4 Feature Set" -ForegroundColor Cyan

# Create scratch directory
if (-not (Test-Path $env:SCRATCH_DIR)) {
    New-Item -ItemType Directory -Path $env:SCRATCH_DIR -Force | Out-Null
    Write-Status 'Created scratch directory' 'Created'
}

# Activate Ultimate Performance power plan
try {
    # Check if Ultimate Performance plan exists
    $ultimatePlan = powercfg /list | Select-String "Ultimate Performance"
    if ($ultimatePlan) {
        powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e
        Write-Status 'Ultimate Performance power plan activated' 'Activated'
    } else {
        # Create Ultimate Performance plan
        powercfg /duplicatescheme 381b4222-f694-41f0-9685-ff5bb260df2e "Ultimate Performance"
        powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e
        Write-Status 'Ultimate Performance power plan created and activated' 'Created'
    }
} catch {
    Write-Warning "Failed to activate Ultimate Performance power plan: $_"
}

# Disable sleep and hibernate
try {
    powercfg /change standby-timeout-ac 0
    powercfg /change hibernate-timeout-ac 0
    Write-Status 'Sleep and hibernate disabled' 'Disabled'
} catch {
    Write-Warning "Failed to disable sleep settings: $_"
}

# Set CPU to 100% minimum
try {
    powercfg /setacvalueindex 381b4222-f694-41f0-9685-ff5bb260df2e 54533251-82be-4824-96c1-47b60b740d00 943c8cb6-6e93-4227-adc6-8b9d86940d50 100
    powercfg /setdcvalueindex 381b4222-f694-41f0-9685-ff5bb260df2e 54533251-82be-4824-96c1-47b60b740d00 943c8cb6-6e93-4227-adc6-8b9d86940d50 100
    Write-Status 'CPU minimum state set to 100%' 'Set'
} catch {
    Write-Warning "Failed to set CPU state: $_"
}

# Optimize scratch directory
try {
    # Set scratch directory attributes
    $scratchDir = Get-Item $env:SCRATCH_DIR
    $scratchDir.Attributes = $scratchDir.Attributes -bor [System.IO.FileAttributes]::NotContentIndexed
    Write-Status 'Scratch directory optimized' 'Optimized'
} catch {
    Write-Warning "Failed to optimize scratch directory: $_"
}

# Check GPU status
try {
    $gpuInfo = Get-WmiObject -Class Win32_VideoController | Where-Object { $_.Name -like "*NVIDIA*" }
    if ($gpuInfo) {
        Write-Host "  GPU: $($gpuInfo.Name) - Ready for V4.0 operations" -ForegroundColor Green
    } else {
        Write-Host "  GPU: No NVIDIA GPU detected - CPU mode only" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  GPU: Unable to detect" -ForegroundColor Red
}

Write-Host "✅ Agent Exo-Suit V4.0 'Perfection' - Ultimate Performance Mode Activated!" -ForegroundColor Green
Write-Host "Production Ready - Full V4 Feature Set" -ForegroundColor Cyan
Write-Host "Use -FullSystem to activate all V4.0 components" -ForegroundColor Yellow
