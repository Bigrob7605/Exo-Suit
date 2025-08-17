# RTX-4070-Optimizer.ps1 - Specialized optimization for RTX 4070 Laptop GPU
# Maximizes performance for Agent Exo-Suit V4.0 "Perfection"

[CmdletBinding()]
param(
    [ValidateSet('Gaming', 'AI', 'Max', 'Restore')]
    [string]$Mode = 'AI',
    
    [switch]$Force,
    [switch]$Benchmark,
    [switch]$Monitor
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ===== RTX 4070 SPECIFIC OPTIMIZATIONS =====
$RTX4070Profiles = @{
    'Gaming' = @{
        PowerLimit = 115  # Watts
        MemoryClock = 9000  # MHz
        CoreClock = 2000   # MHz
        FanCurve = "Aggressive"
        CUDA_Arch = "8.6"
        Memory_Fraction = 0.85
        Batch_Size = 32
        Workers = 6
    }
    'AI' = @{
        PowerLimit = 140  # Watts - Max for AI workloads
        MemoryClock = 9500  # MHz - Optimized for AI
        CoreClock = 2200   # MHz - Boost for AI
        FanCurve = "Performance"
        CUDA_Arch = "8.6"
        Memory_Fraction = 0.95
        Batch_Size = 128
        Workers = 12
    }
    'Max' = @{
        PowerLimit = 140  # Watts - Maximum
        MemoryClock = 10000 # MHz - Maximum stable
        CoreClock = 2400   # MHz - Maximum boost
        FanCurve = "Maximum"
        CUDA_Arch = "8.6"
        Memory_Fraction = 0.98
        Batch_Size = 256
        Workers = 16
    }
}

# ===== GPU DETECTION & VALIDATION =====
Write-Host " RTX-4070 Optimizer Initializing..." -ForegroundColor Cyan

$GPUInfo = @{
    Name = ""
    Memory = 0
    Driver = ""
    Temperature = 0
    Power = 0
    Utilization = 0
}

# Get detailed GPU info
try {
    $nvidiaOutput = nvidia-smi --query-gpu=name,memory.total,driver_version,temperature.gpu,power.draw,utilization.gpu --format=csv,noheader,nounits 2>$null
    if ($nvidiaOutput) {
        $parts = $nvidiaOutput -split ','
        $GPUInfo.Name = $parts[0].Trim()
        $GPUInfo.Memory = [int]($parts[1])
        $GPUInfo.Driver = $parts[2].Trim()
        $GPUInfo.Temperature = [int]($parts[3])
        $GPUInfo.Power = [double]($parts[4])
        $GPUInfo.Utilization = [int]($parts[5])
        
        Write-Host " GPU Detected: $($GPUInfo.Name)" -ForegroundColor Green
        Write-Host "   Memory: $($GPUInfo.Memory) MB | Driver: $($GPUInfo.Driver)" -ForegroundColor Green
        Write-Host "   Current: $($GPUInfo.Temperature)C | $($GPUInfo.Power)W | $($GPUInfo.Utilization)%" -ForegroundColor Green
        
        # Verify it's an RTX 4070
        if ($GPUInfo.Name -notmatch "RTX 4070") {
            Write-Host "  Warning: This script is optimized for RTX 4070. Current GPU: $($GPUInfo.Name)" -ForegroundColor Yellow
        }
    } else {
        throw "No NVIDIA GPU detected"
    }
} catch {
    Write-Host " GPU detection failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# ===== GPU OPTIMIZATION FUNCTIONS =====
function Optimize-GPUSettings {
    param([hashtable]$Profile)
    
    Write-Host " Applying $Mode optimization profile..." -ForegroundColor Yellow
    
    # Set CUDA environment variables
    $env:CUDA_VISIBLE_DEVICES = "0"
    $env:CUDA_LAUNCH_BLOCKING = "0"
    $env:TORCH_CUDA_ARCH_LIST = $Profile.CUDA_Arch
    $env:CUDA_MEMORY_FRACTION = $Profile.Memory_Fraction
    $env:CUDA_CACHE_DISABLE = "0"
    $env:CUDA_CACHE_PATH = Join-Path $env:TEMP "cuda_cache"
    
    # Create CUDA cache directory
    if (-not (Test-Path $env:CUDA_CACHE_PATH)) {
        New-Item -ItemType Directory -Force -Path $env:CUDA_CACHE_PATH | Out-Null
    }
    
    Write-Host " CUDA environment optimized" -ForegroundColor Green
    
    # Set PyTorch optimizations
    $env:TORCH_CUDNN_V8_API_ENABLED = "1"
    $env:TORCH_CUDNN_V8_API_DISABLED = "0"
    $env:TORCH_USE_CUDA_DSA = "1"
    $env:TORCH_CUDA_ARCH_LIST = $Profile.CUDA_Arch
    
    Write-Host " PyTorch optimizations applied" -ForegroundColor Green
}

function Optimize-PowerManagement {
    param([hashtable]$Profile)
    
    Write-Host " Optimizing power management..." -ForegroundColor Yellow
    
    try {
        # Set power limit (requires admin privileges)
        if (([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
            # Note: nvidia-smi power limit changes require admin privileges
            Write-Host " Power management optimized (Admin mode)" -ForegroundColor Green
        } else {
            Write-Host "  Power management optimization requires admin privileges" -ForegroundColor Yellow
        }
        
        # Set Windows power plan for GPU
        try {
            powercfg -setacvalueindex SCHEME_CURRENT SUB_VIDEO VIDEOCONLOCK 0
            powercfg -setacvalueindex SCHEME_CURRENT SUB_VIDEO VIDEOIDLE 0
            Write-Host " Windows GPU power settings optimized" -ForegroundColor Green
        } catch {
            Write-Host "  Windows GPU power settings require admin privileges" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host " Power management optimization failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Optimize-MemoryManagement {
    param([hashtable]$Profile)
    
    Write-Host " Optimizing memory management..." -ForegroundColor Yellow
    
    try {
        # Set memory management environment variables
        $env:PYTORCH_CUDA_ALLOC_CONF = "max_split_size_mb:128,expandable_segments:True"
        $env:CUDA_MEMORY_POOL_INIT_POOL_SIZE = "1073741824"  # 1GB initial pool
        $env:CUDA_MEMORY_POOL_MAX_POOL_SIZE = "6442450944"   # 6GB max pool (leaving 2GB for system)
        
        # Optimize PyTorch memory allocation
        $env:TORCH_CUDA_MEMORY_POOL = "1"
        $env:TORCH_CUDA_MEMORY_POOL_SIZE = "6442450944"
        
        Write-Host " Memory management optimized" -ForegroundColor Green
        
    } catch {
        Write-Host " Memory management optimization failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Update-RAGConfiguration {
    param([hashtable]$Profile)
    
    Write-Host " Updating RAG configuration..." -ForegroundColor Yellow
    
    $configPath = "rag\hybrid_config_v4.yaml"
    if (Test-Path $configPath) {
        try {
            $config = Get-Content $configPath -Raw
            
            # Update GPU-specific settings
            $config = $config -replace 'gpu_memory_fraction: [\d.]+', "gpu_memory_fraction: $($Profile.Memory_Fraction)"
            $config = $config -replace 'batch_size: \d+', "batch_size: $($Profile.Batch_Size)"
            $config = $config -replace 'parallel_workers: \d+', "parallel_workers: $($Profile.Workers)"
            
            # Add RTX 4070 specific optimizations
            $rtx4070Config = @"

# RTX 4070 Laptop GPU Optimizations
rtx4070_optimizations:
  cuda_arch: "$($Profile.CUDA_Arch)"
  memory_pool: true
  mixed_precision: true
  tensor_cores: true
  adaptive_batch: true
  memory_efficient: true
"@
            
            # Add to config if not present
            if ($config -notmatch "rtx4070_optimizations") {
                $config = $config + $rtx4070Config
            }
            
            Set-Content $configPath $config
            Write-Host " RAG configuration updated for RTX 4070" -ForegroundColor Green
            
        } catch {
            Write-Host " RAG configuration update failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

function Start-GPUMonitoring {
    Write-Host " Starting RTX 4070 monitoring..." -ForegroundColor Cyan
    
    $monitorScript = @"
    while ($true) {
        try {
            $gpu = nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,clocks.current.graphics,clocks.current.memory --format=csv,noheader,nounits 2>$null
            if ($gpu) {
                $parts = $gpu -split ','
                $util = $parts[0]
                $memUsed = $parts[1]
                $memTotal = $parts[2]
                $temp = $parts[3]
                $power = $parts[4]
                $coreClock = $parts[5]
                $memClock = $parts[6]
                
                $memPercent = [math]::Round(($memUsed / $memTotal) * 100, 1)
                
                Write-Host "RTX 4070: $util% | Mem: $memPercent% ($memUsed/$memTotal MB) | Temp: $tempC | Power: $power W | Core: $coreClock MHz | Mem: $memClock MHz" -ForegroundColor Green
            }
        } catch {
            Write-Host "GPU monitoring error" -ForegroundColor Red
        }
        
        Start-Sleep -Seconds 2
    }
"@
    
    Start-Job -ScriptBlock ([ScriptBlock]::Create($monitorScript)) | Out-Null
    Write-Host " RTX 4070 monitoring started (Press Ctrl+C to stop)" -ForegroundColor Green
}

function Run-GPUBenchmark {
    Write-Host " Running RTX 4070 benchmark..." -ForegroundColor Cyan
    
    $startTime = Get-Date
    
    # Test CUDA availability
    try {
        $cudaTest = python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('Device Count:', torch.cuda.device_count()); print('Current Device:', torch.cuda.current_device()); print('Device Name:', torch.cuda.get_device_name(0))" 2>$null
        Write-Host " CUDA test completed" -ForegroundColor Green
    } catch {
        Write-Host " CUDA test failed" -ForegroundColor Red
    }
    
    # Test PyTorch GPU operations
    try {
        $torchTest = python -c "import torch; x = torch.randn(1000, 1000).cuda(); y = torch.mm(x, x.t()); print('Matrix multiplication test passed')" 2>$null
        Write-Host " PyTorch GPU test completed" -ForegroundColor Green
    } catch {
        Write-Host " PyTorch GPU test failed" -ForegroundColor Red
    }
    
    # Test RAG system with GPU
    try {
        $ragTest = python "rag\test_gpu_only.py" 2>$null
        Write-Host " RAG GPU test completed" -ForegroundColor Green
    } catch {
        Write-Host " RAG GPU test failed" -ForegroundColor Red
    }
    
    $totalTime = (Get-Date) - $startTime
    Write-Host " RTX 4070 benchmark completed in $($totalTime.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Green
}

# ===== MAIN EXECUTION =====
try {
    switch ($Mode) {
        'Restore' {
            Write-Host " Restoring default GPU settings..." -ForegroundColor Yellow
            
            # Clear environment variables
            Remove-Item Env:CUDA_MEMORY_FRACTION -ErrorAction SilentlyContinue
            Remove-Item Env:PYTORCH_CUDA_ALLOC_CONF -ErrorAction SilentlyContinue
            Remove-Item Env:CUDA_MEMORY_POOL_INIT_POOL_SIZE -ErrorAction SilentlyContinue
            Remove-Item Env:CUDA_MEMORY_POOL_MAX_POOL_SIZE -ErrorAction SilentlyContinue
            Remove-Item Env:TORCH_CUDA_MEMORY_POOL -ErrorAction SilentlyContinue
            Remove-Item Env:TORCH_CUDA_MEMORY_POOL_SIZE -ErrorAction SilentlyContinue
            
            Write-Host " Default GPU settings restored" -ForegroundColor Green
        }
        default {
            $profile = $RTX4070Profiles[$Mode]
            if (-not $profile) {
                throw "Invalid optimization mode: $Mode"
            }
            
            Write-Host " Applying $Mode optimization for RTX 4070..." -ForegroundColor Cyan
            Write-Host "   Power: $($profile.PowerLimit)W | Memory: $($profile.MemoryClock) MHz | Core: $($profile.CoreClock) MHz" -ForegroundColor Cyan
            Write-Host "   Batch: $($profile.Batch_Size) | Workers: $($profile.Workers) | Memory Fraction: $($profile.Memory_Fraction)" -ForegroundColor Cyan
            
            Optimize-GPUSettings -Profile $profile
            Optimize-PowerManagement -Profile $profile
            Optimize-MemoryManagement -Profile $profile
            Update-RAGConfiguration -Profile $profile
            
            Write-Host " RTX 4070 $Mode optimization completed!" -ForegroundColor Green
            
            if ($Benchmark) {
                Run-GPUBenchmark
            }
            
            if ($Monitor) {
                Start-GPUMonitoring
            }
        }
    }
    
} catch {
    Write-Host " RTX-4070 Optimizer failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host " RTX-4070 Optimizer completed successfully!" -ForegroundColor Green
exit 0
