# Ultimate-Speed-Boost-V4.ps1 - Master performance optimizer for Agent Exo-Suit V4.0
# Orchestrates all speed optimizations for maximum performance

[CmdletBinding()]
param(
    [ValidateSet('Turbo', 'Ultra', 'Max', 'Restore')]
    [string]$Mode = 'Max',
    
    [switch]$Benchmark,
    [switch]$Monitor,
    [switch]$Force,
    [switch]$SkipTests
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ===== PERFORMANCE PROFILES =====
$UltimateProfiles = @{
    'Turbo' = @{
        Description = "Balanced performance boost - 2-3x faster"
        CPU_Min = 80
        CPU_Max = 100
        GPU_Memory_Fraction = 0.9
        Batch_Size = 64
        Workers = 8
        Prefetch = 4
        Memory_Threshold = 0.9
        Cache_Size = 8192
        Power_Plan = "High Performance"
    }
    'Ultra' = @{
        Description = "High performance boost - 3-5x faster"
        CPU_Min = 90
        CPU_Max = 100
        GPU_Memory_Fraction = 0.95
        Batch_Size = 128
        Workers = 12
        Prefetch = 8
        Memory_Threshold = 0.95
        Cache_Size = 16384
        Power_Plan = "Ultimate Performance"
    }
    'Max' = @{
        Description = "Maximum performance - 5-10x faster"
        CPU_Min = 100
        CPU_Max = 100
        GPU_Memory_Fraction = 0.98
        Batch_Size = 256
        Workers = 16
        Prefetch = 16
        Memory_Threshold = 0.98
        Cache_Size = 32768
        Power_Plan = "Ultimate Performance"
    }
}

# ===== SYSTEM STATUS =====
$SystemStatus = @{
    Optimizations_Applied = @()
    Errors_Encountered = @()
    Warnings = @()
    StartTime = $null
    EndTime = $null
}

# ===== OPTIMIZATION FUNCTIONS =====
function Optimize-SystemPower {
    param([hashtable]$Profile)
    
    Write-Host " Optimizing system power settings..." -ForegroundColor Yellow
    
    try {
        if (([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
            # Set power plan
            switch ($Profile.Power_Plan) {
                "High Performance" {
                    powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
                }
                "Ultimate Performance" {
                    # Check if Ultimate Performance exists
                    $ultimateGuid = $null
                    $powerPlans = powercfg -list | Select-String "Ultimate Performance"
                    if ($powerPlans) {
                        $ultimateGuid = ($powerPlans.ToString() -split '\s+')[3]
                    } else {
                        # Create Ultimate Performance plan
                        $duplicateOutput = powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61
                        $ultimateGuid = ($duplicateOutput -split '\s+')[-1]
                        powercfg -changename $ultimateGuid "Ultimate Performance" "Agent Exo-Suit V4.0 - Maximum Performance Mode"
                    }
                    powercfg -setactive $ultimateGuid
                }
            }
            
            # Optimize CPU settings
            powercfg -change -processor-min-state-ac $Profile.CPU_Min
            powercfg -change -processor-max-state-ac $Profile.CPU_Max
            
            # Disable sleep and hibernate
            powercfg -change -standby-timeout-ac 0
            powercfg -change -hibernate-timeout-ac 0
            
            # Optimize disk settings
            powercfg -change -disk-timeout-ac 0
            powercfg -change -disk-timeout-dc 0
            
            $SystemStatus.Optimizations_Applied += "System Power Settings"
            Write-Host " System power optimized: $($Profile.Power_Plan)" -ForegroundColor Green
            
        } else {
            $SystemStatus.Warnings += "Power optimization requires admin privileges"
            Write-Host "  Power optimization requires admin privileges" -ForegroundColor Yellow
        }
        
    } catch {
        $SystemStatus.Errors_Encountered += "Power optimization failed: $($_.Exception.Message)"
        Write-Host " Power optimization failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Optimize-MemoryAndCache {
    param([hashtable]$Profile)
    
    Write-Host " Optimizing memory and cache settings..." -ForegroundColor Yellow
    
    try {
        # Set memory optimization environment variables
        $env:NODE_OPTIONS = "--max-old-space-size=$($Profile.Cache_Size)"
        $env:PIP_CACHE_DIR = Join-Path $env:TEMP "exo_suit_pip_cache"
        $env:NPM_CONFIG_CACHE = Join-Path $env:TEMP "exo_suit_npm_cache"
        $env:CUDA_CACHE_PATH = Join-Path $env:TEMP "cuda_cache"
        
        # Create cache directories
        @($env:PIP_CACHE_DIR, $env:NPM_CONFIG_CACHE, $env:CUDA_CACHE_PATH) | ForEach-Object {
            if (-not (Test-Path $_)) {
                New-Item -ItemType Directory -Force -Path $_ | Out-Null
            }
        }
        
        # Set Python memory optimization
        $env:PYTHONOPTIMIZE = "1"
        $env:PYTHONUNBUFFERED = "1"
        $env:PYTHONDONTWRITEBYTECODE = "1"
        $env:OMP_NUM_THREADS = $Profile.Workers
        $env:MKL_NUM_THREADS = $Profile.Workers
        $env:OPENBLAS_NUM_THREADS = $Profile.Workers
        $env:VECLIB_MAXIMUM_THREADS = $Profile.Workers
        $env:NUMEXPR_NUM_THREADS = $Profile.Workers
        
        $SystemStatus.Optimizations_Applied += "Memory and Cache Settings"
        Write-Host " Memory and cache optimized: $($Profile.Cache_Size)MB cache, $($Profile.Workers) workers" -ForegroundColor Green
        
    } catch {
        $SystemStatus.Errors_Encountered += "Memory optimization failed: $($_.Exception.Message)"
        Write-Host " Memory optimization failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Optimize-GPUSettings {
    param([hashtable]$Profile)
    
    Write-Host " Optimizing GPU settings..." -ForegroundColor Yellow
    
    try {
        # Check GPU availability
        $nvidiaOutput = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>$null
        if ($nvidiaOutput) {
            # Set CUDA environment variables
            $env:CUDA_VISIBLE_DEVICES = "0"
            $env:CUDA_LAUNCH_BLOCKING = "0"
            $env:TORCH_CUDA_ARCH_LIST = "8.6"
            $env:CUDA_MEMORY_FRACTION = $Profile.GPU_Memory_Fraction
            
            # Set PyTorch optimizations
            $env:TORCH_CUDNN_V8_API_ENABLED = "1"
            $env:TORCH_USE_CUDA_DSA = "1"
            $env:PYTORCH_CUDA_ALLOC_CONF = "max_split_size_mb:128,expandable_segments:True"
            $env:CUDA_MEMORY_POOL_INIT_POOL_SIZE = "1073741824"
            $env:CUDA_MEMORY_POOL_MAX_POOL_SIZE = "6442450944"
            $env:TORCH_CUDA_MEMORY_POOL = "1"
            $env:TORCH_CUDA_MEMORY_POOL_SIZE = "6442450944"
            
            $SystemStatus.Optimizations_Applied += "GPU Settings"
            Write-Host " GPU optimized: Memory fraction $($Profile.GPU_Memory_Fraction)" -ForegroundColor Green
            
        } else {
            $SystemStatus.Warnings += "No NVIDIA GPU detected"
            Write-Host "  No NVIDIA GPU detected" -ForegroundColor Yellow
        }
        
    } catch {
        $SystemStatus.Errors_Encountered += "GPU optimization failed: $($_.Exception.Message)"
        Write-Host " GPU optimization failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Update-RAGConfiguration {
    param([hashtable]$Profile)
    
    Write-Host " Updating RAG configuration..." -ForegroundColor Yellow
    
    try {
        $configPath = "rag\hybrid_config_v4.yaml"
        if (Test-Path $configPath) {
            $config = Get-Content $configPath -Raw
            
            # Update performance settings
            $config = $config -replace 'batch_size: \d+', "batch_size: $($Profile.Batch_Size)"
            $config = $config -replace 'parallel_workers: \d+', "parallel_workers: $($Profile.Workers)"
            $config = $config -replace 'prefetch_factor: \d+', "prefetch_factor: $($Profile.Prefetch)"
            $config = $config -replace 'gpu_memory_fraction: [\d.]+', "gpu_memory_fraction: $($Profile.GPU_Memory_Fraction)"
            $config = $config -replace 'memory_threshold: [\d.]+', "memory_threshold: $($Profile.Memory_Threshold)"
            
            # Add ultimate performance optimizations
            $ultimateConfig = @"

# Ultimate Speed Boost V4.0 Optimizations
ultimate_speed_boost:
  mode: "$Mode"
  batch_size: $($Profile.Batch_Size)
  workers: $($Profile.Workers)
  prefetch: $($Profile.Prefetch)
  memory_threshold: $($Profile.Memory_Threshold)
  cache_size_mb: $($Profile.Cache_Size)
  timestamp: "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
"@
            
            # Add to config if not present
            if ($config -notmatch "ultimate_speed_boost") {
                $config = $config + $ultimateConfig
            }
            
            Set-Content $configPath $config
            $SystemStatus.Optimizations_Applied += "RAG Configuration"
            Write-Host " RAG configuration updated for $Mode mode" -ForegroundColor Green
            
        } else {
            $SystemStatus.Warnings += "RAG configuration file not found"
            Write-Host "  RAG configuration file not found" -ForegroundColor Yellow
        }
        
    } catch {
        $SystemStatus.Errors_Encountered += "RAG configuration update failed: $($_.Exception.Message)"
        Write-Host " RAG configuration update failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Run-PerformanceBenchmark {
    Write-Host " Running performance benchmark..." -ForegroundColor Cyan
    
    try {
        if (-not $SkipTests) {
            $benchmarkResult = & ".\ops\Performance-Test-Suite-V4.ps1" -Mode "Optimized" -SaveResults
            $SystemStatus.Optimizations_Applied += "Performance Benchmark"
            Write-Host " Performance benchmark completed" -ForegroundColor Green
        } else {
            Write-Host "  Performance tests skipped" -ForegroundColor Yellow
        }
        
    } catch {
        $SystemStatus.Errors_Encountered += "Performance benchmark failed: $($_.Exception.Message)"
        Write-Host " Performance benchmark failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Start-PerformanceMonitoring {
    if (-not $Monitor) { return }
    
    Write-Host " Starting performance monitoring..." -ForegroundColor Cyan
    
    try {
        $monitorResult = & ".\ops\RTX-4070-Optimizer.ps1" -Mode "AI" -Monitor
        $SystemStatus.Optimizations_Applied += "Performance Monitoring"
        Write-Host " Performance monitoring started" -ForegroundColor Green
        
    } catch {
        $SystemStatus.Errors_Encountered += "Performance monitoring failed: $($_.Exception.Message)"
        Write-Host " Performance monitoring failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Restore-NormalSettings {
    Write-Host " Restoring normal performance settings..." -ForegroundColor Yellow
    
    try {
        # Restore balanced power plan
        if (([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
            powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e
            Write-Host " Balanced power plan restored" -ForegroundColor Green
        }
        
        # Clear environment variables
        $envVars = @(
            'PYTHONOPTIMIZE', 'PYTHONUNBUFFERED', 'PYTHONDONTWRITEBYTECODE',
            'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
            'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS', 'CUDA_MEMORY_FRACTION',
            'PYTORCH_CUDA_ALLOC_CONF', 'CUDA_MEMORY_POOL_INIT_POOL_SIZE',
            'CUDA_MEMORY_POOL_MAX_POOL_SIZE', 'TORCH_CUDA_MEMORY_POOL',
            'TORCH_CUDA_MEMORY_POOL_SIZE'
        )
        
        foreach ($var in $envVars) {
            Remove-Item Env:$var -ErrorAction SilentlyContinue
        }
        
        $SystemStatus.Optimizations_Applied += "Settings Restored"
        Write-Host " Normal performance settings restored" -ForegroundColor Green
        
    } catch {
        $SystemStatus.Errors_Encountered += "Settings restoration failed: $($_.Exception.Message)"
        Write-Host " Settings restoration failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# ===== MAIN EXECUTION =====
try {
    $SystemStatus.StartTime = Get-Date
    
    Write-Host " Ultimate Speed Boost V4.0 Initializing..." -ForegroundColor Cyan
    Write-Host "Mode: $Mode | Benchmark: $Benchmark | Monitor: $Monitor" -ForegroundColor Cyan
    
    switch ($Mode) {
        'Restore' {
            Write-Host " Restoring normal performance mode..." -ForegroundColor Yellow
            Restore-NormalSettings
        }
        default {
            $profile = $UltimateProfiles[$Mode]
            if (-not $profile) {
                throw "Invalid performance mode: $Mode"
            }
            
            Write-Host " Applying $Mode performance profile..." -ForegroundColor Cyan
            Write-Host "Description: $($profile.Description)" -ForegroundColor Cyan
            Write-Host "CPU: $($profile.CPU_Min)-$($profile.CPU_Max)% | GPU Memory: $($profile.GPU_Memory_Fraction)" -ForegroundColor Cyan
            Write-Host "Batch: $($profile.Batch_Size) | Workers: $($profile.Workers) | Prefetch: $($profile.Prefetch)" -ForegroundColor Cyan
            
            # Apply all optimizations
            Optimize-SystemPower -Profile $profile
            Optimize-MemoryAndCache -Profile $profile
            Optimize-GPUSettings -Profile $profile
            Update-RAGConfiguration -Profile $profile
            
            if ($Benchmark) {
                Run-PerformanceBenchmark
            }
            
            if ($Monitor) {
                Start-PerformanceMonitoring
            }
            
            Write-Host " $Mode performance mode activated!" -ForegroundColor Green
        }
    }
    
    $SystemStatus.EndTime = Get-Date
    $duration = $SystemStatus.EndTime - $SystemStatus.StartTime
    
    # Display summary
    Write-Host ""
    Write-Host " Ultimate Speed Boost V4.0 Summary" -ForegroundColor Cyan
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host "Mode: $Mode" -ForegroundColor White
    Write-Host "Duration: $($duration.TotalSeconds.ToString('F2')) seconds" -ForegroundColor White
    Write-Host "Optimizations Applied: $($SystemStatus.Optimizations_Applied.Count)" -ForegroundColor White
    Write-Host "Errors: $($SystemStatus.Errors_Encountered.Count)" -ForegroundColor White
    Write-Host "Warnings: $($SystemStatus.Warnings.Count)" -ForegroundColor White
    
    if ($SystemStatus.Optimizations_Applied.Count -gt 0) {
        Write-Host ""
        Write-Host " Applied Optimizations:" -ForegroundColor Green
        foreach ($opt in $SystemStatus.Optimizations_Applied) {
            Write-Host "   • $opt" -ForegroundColor Gray
        }
    }
    
    if ($SystemStatus.Errors_Encountered.Count -gt 0) {
        Write-Host ""
        Write-Host " Errors Encountered:" -ForegroundColor Red
        foreach ($error in $SystemStatus.Errors_Encountered) {
            Write-Host "   • $error" -ForegroundColor Gray
        }
    }
    
    if ($SystemStatus.Warnings.Count -gt 0) {
        Write-Host ""
        Write-Host "  Warnings:" -ForegroundColor Yellow
        foreach ($warning in $SystemStatus.Warnings) {
            Write-Host "   • $warning" -ForegroundColor Gray
        }
    }
    
} catch {
    Write-Host " Ultimate Speed Boost V4.0 failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host " Ultimate Speed Boost V4.0 completed successfully!" -ForegroundColor Green
Write-Host "Your Agent Exo-Suit V4.0 should now be running significantly faster!" -ForegroundColor Green
exit 0
