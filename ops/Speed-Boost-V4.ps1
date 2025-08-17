# Speed-Boost-V4.ps1 - Agent Exo-Suit V4.0 "Perfection" Performance Optimizer
# Comprehensive speed optimization system for maximum performance

[CmdletBinding()]
param(
    [ValidateSet('Turbo', 'Ultra', 'Max', 'Restore')]
    [string]$Mode = 'Turbo',
    
    [switch]$Force,
    [switch]$Benchmark,
    [switch]$Monitor
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ===== PERFORMANCE PROFILES =====
$PerformanceProfiles = @{
    'Turbo' = @{
        CPU_Min = 80
        CPU_Max = 100
        GPU_Memory_Fraction = 0.9
        Batch_Size = 64
        Workers = 8
        Prefetch = 4
        Memory_Threshold = 0.9
        Cache_Size = 8192
    }
    'Ultra' = @{
        CPU_Min = 90
        CPU_Max = 100
        GPU_Memory_Fraction = 0.95
        Batch_Size = 128
        Workers = 12
        Prefetch = 8
        Memory_Threshold = 0.95
        Cache_Size = 16384
    }
    'Max' = @{
        CPU_Min = 100
        CPU_Max = 100
        GPU_Memory_Fraction = 0.98
        Batch_Size = 256
        Workers = 16
        Prefetch = 16
        Memory_Threshold = 0.98
        Cache_Size = 32768
    }
}

# ===== SYSTEM DETECTION =====
Write-Host " Speed-Boost-V4.0 Initializing..." -ForegroundColor Cyan

$SystemInfo = @{
    CPU_Cores = (Get-WmiObject -Class Win32_Processor).NumberOfCores
    CPU_Threads = (Get-WmiObject -Class Win32_Processor).NumberOfLogicalProcessors
    RAM_GB = [math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
    GPU_Available = $false
    GPU_Memory = 0
    CUDA_Available = $false
}

# Detect GPU
try {
    $nvidiaOutput = nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits 2>$null
    if ($nvidiaOutput) {
        $SystemInfo.GPU_Available = $true
        $SystemInfo.GPU_Memory = [int]($nvidiaOutput -split ',')[1]
        $SystemInfo.CUDA_Available = $true
        Write-Host " NVIDIA GPU detected: $($nvidiaOutput -split ',')[0]" -ForegroundColor Green
        Write-Host "   Memory: $($SystemInfo.GPU_Memory) MB | Driver: $($nvidiaOutput -split ',')[2]" -ForegroundColor Green
    }
} catch {
    Write-Host "  NVIDIA GPU not detected" -ForegroundColor Yellow
}

Write-Host " System Specs: $($SystemInfo.CPU_Cores)C/$($SystemInfo.CPU_Threads)T | $($SystemInfo.RAM_GB)GB RAM" -ForegroundColor Cyan

# ===== PERFORMANCE OPTIMIZATION =====
function Optimize-SystemPerformance {
    param([hashtable]$Profile)
    
    Write-Host " Applying $Mode performance profile..." -ForegroundColor Yellow
    
    # CPU Optimization
    try {
        if ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator") {
            powercfg -change -processor-min-state-ac $Profile.CPU_Min
            powercfg -change -processor-max-state-ac $Profile.CPU_Max
            Write-Host " CPU optimized: Min $($Profile.CPU_Min)%, Max $($Profile.CPU_Max)%" -ForegroundColor Green
        } else {
            Write-Host "  CPU optimization requires admin privileges" -ForegroundColor Yellow
        }
    } catch {
        Write-Host " CPU optimization failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Memory Optimization
    try {
        $env:NODE_OPTIONS = "--max-old-space-size=$($Profile.Cache_Size)"
        $env:PIP_CACHE_DIR = Join-Path $env:TEMP "exo_suit_pip_cache"
        $env:NPM_CONFIG_CACHE = Join-Path $env:TEMP "exo_suit_npm_cache"
        
        # Create cache directories
        @($env:PIP_CACHE_DIR, $env:NPM_CONFIG_CACHE) | ForEach-Object {
            if (-not (Test-Path $_)) {
                New-Item -ItemType Directory -Force -Path $_ | Out-Null
            }
        }
        
        Write-Host " Memory cache optimized: $($Profile.Cache_Size)MB" -ForegroundColor Green
    } catch {
        Write-Host " Memory optimization failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # GPU Optimization
    if ($SystemInfo.GPU_Available) {
        try {
            $env:CUDA_VISIBLE_DEVICES = "0"
            $env:CUDA_LAUNCH_BLOCKING = "0"
            $env:TORCH_CUDA_ARCH_LIST = "8.6"
            $env:CUDA_MEMORY_FRACTION = $Profile.GPU_Memory_Fraction
            
            Write-Host " GPU optimized: Memory fraction $($Profile.GPU_Memory_Fraction)" -ForegroundColor Green
        } catch {
            Write-Host " GPU optimization failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# ===== RAG SYSTEM OPTIMIZATION =====
function Optimize-RAGSystem {
    param([hashtable]$Profile)
    
    Write-Host " Optimizing RAG system..." -ForegroundColor Yellow
    
    # Update hybrid config
    $configPath = "rag\hybrid_config_v4.yaml"
    if (Test-Path $configPath) {
        try {
            $config = Get-Content $configPath -Raw
            $config = $config -replace 'batch_size: \d+', "batch_size: $($Profile.Batch_Size)"
            $config = $config -replace 'parallel_workers: \d+', "parallel_workers: $($Profile.Workers)"
            $config = $config -replace 'prefetch_factor: \d+', "prefetch_factor: $($Profile.Prefetch)"
            $config = $config -replace 'gpu_memory_fraction: [\d.]+', "gpu_memory_fraction: $($Profile.GPU_Memory_Fraction)"
            $config = $config -replace 'memory_threshold: [\d.]+', "memory_threshold: $($Profile.Memory_Threshold)"
            
            Set-Content $configPath $config
            Write-Host " RAG config optimized for $Mode mode" -ForegroundColor Green
        } catch {
            Write-Host " RAG config update failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# ===== PYTHON ENVIRONMENT OPTIMIZATION =====
function Optimize-PythonEnvironment {
    param([hashtable]$Profile)
    
    Write-Host " Optimizing Python environment..." -ForegroundColor Yellow
    
    try {
        # Set environment variables for Python performance
        $env:PYTHONOPTIMIZE = "1"
        $env:PYTHONUNBUFFERED = "1"
        $env:PYTHONDONTWRITEBYTECODE = "1"
        $env:OMP_NUM_THREADS = $Profile.Workers
        $env:MKL_NUM_THREADS = $Profile.Workers
        $env:OPENBLAS_NUM_THREADS = $Profile.Workers
        $env:VECLIB_MAXIMUM_THREADS = $Profile.Workers
        $env:NUMEXPR_NUM_THREADS = $Profile.Workers
        
        Write-Host " Python environment optimized" -ForegroundColor Green
    } catch {
        Write-Host " Python optimization failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# ===== PERFORMANCE MONITORING =====
function Start-PerformanceMonitoring {
    Write-Host " Starting performance monitoring..." -ForegroundColor Cyan
    
    $monitorScript = @"
    while ($true) {
        $cpu = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples[0].CookedValue
        $ram = (Get-Counter '\Memory\Available MBytes').CounterSamples[0].CookedValue
        $ramTotal = [math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1MB, 0)
        $ramUsed = $ramTotal - $ram
        $ramPercent = [math]::Round(($ramUsed / $ramTotal) * 100, 1)
        
        if ($SystemInfo.GPU_Available) {
            try {
                $gpu = nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits 2>$null
                if ($gpu) {
                    $gpuParts = $gpu -split ','
                    $gpuUtil = $gpuParts[0]
                    $gpuMemUsed = $gpuParts[1]
                    $gpuMemTotal = $gpuParts[2]
                    $gpuTemp = $gpuParts[3]
                    Write-Host "CPU: $([math]::Round($cpu,1))% | RAM: $ramPercent% | GPU: $gpuUtil% | GPU Mem: $gpuMemUsed/$gpuMemTotal MB | Temp: $gpuTempC" -ForegroundColor Green
                }
            } catch {
                Write-Host "CPU: $([math]::Round($cpu,1))% | RAM: $ramPercent% | GPU: Error" -ForegroundColor Yellow
            }
        } else {
            Write-Host "CPU: $([math]::Round($cpu,1))% | RAM: $ramPercent%" -ForegroundColor Green
        }
        
        Start-Sleep -Seconds 2
    }
"@
    
    Start-Job -ScriptBlock ([ScriptBlock]::Create($monitorScript)) | Out-Null
    Write-Host " Performance monitoring started (Press Ctrl+C to stop)" -ForegroundColor Green
}

# ===== PERFORMANCE BENCHMARKING =====
function Run-PerformanceBenchmark {
    Write-Host " Running performance benchmark..." -ForegroundColor Cyan
    
    $startTime = Get-Date
    
    # Test RAG system performance
    try {
        $ragTest = python "rag\test_hybrid_comprehensive_v4.py" 2>$null
        $ragTime = (Get-Date) - $startTime
        Write-Host " RAG benchmark completed in $($ragTime.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Green
    } catch {
        Write-Host " RAG benchmark failed" -ForegroundColor Red
    }
    
    # Test GPU performance
    if ($SystemInfo.GPU_Available) {
        try {
            $gpuTest = python -c "import torch; print('GPU Memory:', torch.cuda.get_device_properties(0).total_memory / 1024**3, 'GB')" 2>$null
            Write-Host " GPU benchmark completed" -ForegroundColor Green
        } catch {
            Write-Host " GPU benchmark failed" -ForegroundColor Red
        }
    }
}

# ===== MAIN EXECUTION =====
try {
    switch ($Mode) {
        'Restore' {
            Write-Host " Restoring normal performance mode..." -ForegroundColor Yellow
            
            # Restore balanced power plan
            try {
                powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e
                Write-Host " Balanced power plan restored" -ForegroundColor Green
            } catch {
                Write-Host "  Could not restore power plan" -ForegroundColor Yellow
            }
            
            # Clear environment variables
            Remove-Item Env:PYTHONOPTIMIZE -ErrorAction SilentlyContinue
            Remove-Item Env:PYTHONUNBUFFERED -ErrorAction SilentlyContinue
            Remove-Item Env:PYTHONDONTWRITEBYTECODE -ErrorAction SilentlyContinue
            Remove-Item Env:OMP_NUM_THREADS -ErrorAction SilentlyContinue
            Remove-Item Env:MKL_NUM_THREADS -ErrorAction SilentlyContinue
            Remove-Item Env:OPENBLAS_NUM_THREADS -ErrorAction SilentlyContinue
            Remove-Item Env:VECLIB_MAXIMUM_THREADS -ErrorAction SilentlyContinue
            Remove-Item Env:NUMEXPR_NUM_THREADS -ErrorAction SilentlyContinue
            
            Write-Host " Normal performance mode restored" -ForegroundColor Green
        }
        default {
            $profile = $PerformanceProfiles[$Mode]
            if (-not $profile) {
                throw "Invalid performance mode: $Mode"
            }
            
            Write-Host " Applying $Mode performance profile..." -ForegroundColor Cyan
            Write-Host "   Batch Size: $($profile.Batch_Size) | Workers: $($profile.Workers) | Prefetch: $($profile.Prefetch)" -ForegroundColor Cyan
            
            Optimize-SystemPerformance -Profile $profile
            Optimize-RAGSystem -Profile $profile
            Optimize-PythonEnvironment -Profile $profile
            
            Write-Host " $Mode performance mode activated!" -ForegroundColor Green
            
            if ($Benchmark) {
                Run-PerformanceBenchmark
            }
            
            if ($Monitor) {
                Start-PerformanceMonitoring
            }
        }
    }
    
} catch {
    Write-Host " Speed-Boost-V4.0 failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host " Speed-Boost-V4.0 completed successfully!" -ForegroundColor Green
exit 0
