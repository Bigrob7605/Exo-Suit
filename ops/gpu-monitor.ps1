#  GPU Performance Monitor for Agent Exo-Suit V2.1 "Indestructible"
# Real-time GPU monitoring with performance optimization and alerts

[CmdletBinding()]
param(
    [switch]$Continuous,
    [switch]$Benchmark,
    [switch]$Optimize,
    [int]$Interval = 5,
    [switch]$Alert
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ===== GPU MONITOR INITIALIZATION =====
Write-Host " GPU Performance Monitor Initialization..." -ForegroundColor Cyan

# Check for NVIDIA GPU
$gpuAvailable = $false
try {
    $nvidiaOutput = nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap --format=csv,noheader,nounits 2>$null
    if ($nvidiaOutput) {
        $gpuAvailable = $true
        $gpuName = ($nvidiaOutput -split ',')[0]
        $gpuMemory = [int]($nvidiaOutput -split ',')[1]
        $gpuDriver = ($nvidiaOutput -split ',')[2]
        $gpuCompute = ($nvidiaOutput -split ',')[3]
        
        Write-Host " NVIDIA GPU detected: $gpuName" -ForegroundColor Green
        Write-Host "   Memory: $gpuMemory MB | Driver: $gpuDriver | Compute: $gpuCompute" -ForegroundColor Green
    }
} catch {
    Write-Host " NVIDIA GPU not detected or nvidia-smi not available" -ForegroundColor Red
    exit 1
}

# ===== GPU PERFORMANCE MONITORING =====
function Get-GPUMetrics {
    param([switch]$Detailed)
    
    try {
        if ($Detailed) {
            # Detailed metrics
            $metrics = nvidia-smi --query-gpu=timestamp,name,utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu,power.draw,clocks.current.graphics,clocks.current.memory --format=csv,noheader,nounits
        } else {
            # Basic metrics
            $metrics = nvidia-smi --query-gpu=utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu,power.draw --format=csv,noheader,nounits
        }
        
        if ($metrics) {
            $values = $metrics -split ','
            return @{
                GPU_Util = [int]$values[0]
                Mem_Util = [int]$values[1]
                Mem_Used = [int]$values[2]
                Mem_Total = [int]$values[3]
                Temp = [int]$values[4]
                Power = [double]$values[5]
                Timestamp = Get-Date -Format "HH:mm:ss"
            }
        }
    } catch {
        Write-Warning "Failed to get GPU metrics: $($_.Exception.Message)"
        return $null
    }
}

function Show-GPUMetrics {
    param($metrics)
    
    if (-not $metrics) { return }
    
    # Color coding based on utilization
    $gpuColor = if ($metrics.GPU_Util -gt 80) { "Red" } elseif ($metrics.GPU_Util -gt 50) { "Yellow" } else { "Green" }
    $memColor = if ($metrics.Mem_Util -gt 80) { "Red" } elseif ($metrics.Mem_Util -gt 50) { "Yellow" } else { "Green" }
    $tempColor = if ($metrics.Temp -gt 80) { "Red" } elseif ($metrics.Temp -gt 70) { "Yellow" } else { "Green" }
    
    Write-Host "`n GPU Performance Metrics - $($metrics.Timestamp)" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    
    Write-Host "  GPU Utilization: $($metrics.GPU_Util)%" -ForegroundColor $gpuColor
    Write-Host " Memory Usage: $($metrics.Mem_Used) MB / $($metrics.Mem_Total) MB ($($metrics.Mem_Util)%)" -ForegroundColor $memColor
    Write-Host "  Temperature: $($metrics.Temp)C" -ForegroundColor $tempColor
    Write-Host " Power Draw: $($metrics.Power) W" -ForegroundColor White
    
    # Performance indicators
    $memEfficiency = ($metrics.Mem_Used / $metrics.Mem_Total) * 100
    Write-Host " Memory Efficiency: $($memEfficiency.ToString('F1'))%" -ForegroundColor $(if ($memEfficiency -gt 80) { "Green" } else { "Yellow" })
}

function Start-ContinuousMonitoring {
    param([int]$IntervalSeconds)
    
    Write-Host " Starting continuous GPU monitoring (interval: $IntervalSeconds seconds)" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
    
    try {
        while ($true) {
            Clear-Host
            $metrics = Get-GPUMetrics
            Show-GPUMetrics $metrics
            
            # Performance alerts
            if ($Alert) {
                if ($metrics.GPU_Util -gt 90) {
                    Write-Host " HIGH GPU UTILIZATION: $($metrics.GPU_Util)%" -ForegroundColor Red -BackgroundColor White
                }
                if ($metrics.Temp -gt 85) {
                    Write-Host " HIGH TEMPERATURE: $($metrics.Temp)C" -ForegroundColor Red -BackgroundColor White
                }
                if ($metrics.Mem_Util -gt 90) {
                    Write-Host " HIGH MEMORY USAGE: $($metrics.Mem_Util)%" -ForegroundColor Red -BackgroundColor White
                }
            }
            
            Start-Sleep -Seconds $IntervalSeconds
        }
    } catch {
        Write-Host "`n  Monitoring stopped" -ForegroundColor Yellow
    }
}

function Start-GPUBenchmark {
    Write-Host " Starting GPU benchmark..." -ForegroundColor Cyan
    
    $benchmarkScript = @"
import time
import torch
import numpy as np

def run_gpu_benchmark():
    print(" GPU Benchmark Suite")
    print("=" * 50)
    
    if not torch.cuda.is_available():
        print(" CUDA not available")
        return False
    
    device = torch.device('cuda')
    print(f" CUDA available: {torch.cuda.get_device_name(0)}")
    print(f" GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # Memory allocation test
    print("\\n Memory Allocation Test")
    torch.cuda.empty_cache()
    start_mem = torch.cuda.memory_allocated(0)
    
    # Allocate tensors of increasing size
    sizes = [1000, 2000, 4000, 8000]
    for size in sizes:
        try:
            tensor = torch.randn(size, size, device=device)
            current_mem = torch.cuda.memory_allocated(0)
            allocated = (current_mem - start_mem) / 1024**2
            print(f"   {size}x{size}: {allocated:.1f} MB allocated")
            del tensor
            torch.cuda.empty_cache()
        except RuntimeError as e:
            print(f"   {size}x{size}: Failed - {e}")
            break
    
    # Matrix multiplication benchmark
    print("\\n Matrix Multiplication Benchmark")
    test_sizes = [1000, 2000, 4000]
    
    for size in test_sizes:
        try:
            a = torch.randn(size, size, device=device)
            b = torch.randn(size, size, device=device)
            
            # Warmup
            for _ in range(5):
                _ = torch.mm(a, b)
            torch.cuda.synchronize()
            
            # Benchmark
            start_time = time.time()
            for _ in range(10):
                result = torch.mm(a, b)
            torch.cuda.synchronize()
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 10 * 1000
            print(f"   {size}x{size}: {avg_time:.2f} ms average")
            
            del a, b, result
            torch.cuda.empty_cache()
            
        except RuntimeError as e:
            print(f"   {size}x{size}: Failed - {e}")
            break
    
    # Memory bandwidth test
    print("\\n Memory Bandwidth Test")
    try:
        size = 4000
        a = torch.randn(size, size, device=device)
        b = torch.randn(size, size, device=device)
        
        # Measure copy operations
        start_time = time.time()
        for _ in range(100):
            c = a.clone()
        torch.cuda.synchronize()
        end_time = time.time()
        
        copy_time = (end_time - start_time) / 100 * 1000
        print(f"   Memory copy: {copy_time:.2f} ms average")
        
        del a, b, c
        torch.cuda.empty_cache()
        
    except RuntimeError as e:
        print(f"   Memory bandwidth test failed: {e}")
    
    print("\\n GPU benchmark complete!")
    return True

if __name__ == '__main__':
    run_gpu_benchmark()
"@
    
    $benchmarkPath = Join-Path $env:TEMP "gpu_benchmark.py"
    $benchmarkScript | Out-File $benchmarkPath -Encoding utf8
    
    python $benchmarkPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host " GPU benchmark completed successfully!" -ForegroundColor Green
    } else {
        Write-Warning "GPU benchmark failed"
    }
}

function Optimize-GPUSettings {
    Write-Host " Optimizing GPU settings..." -ForegroundColor Cyan
    
    # Check current power management
    try {
        $powerInfo = nvidia-smi -q -d POWER 2>$null | Select-String "Power Management"
        if ($powerInfo -match "Adaptive") {
            Write-Host "  Power management is set to Adaptive" -ForegroundColor Yellow
            Write-Host " Consider setting to Prefer Maximum Performance for better performance" -ForegroundColor Cyan
        } else {
            Write-Host " Power management optimized" -ForegroundColor Green
        }
    } catch {
        Write-Warning "Could not check power management settings"
    }
    
    # Check memory allocation
    try {
        $memInfo = nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits
        if ($memInfo) {
            $values = $memInfo -split ','
            $used = [int]$values[0]
            $total = [int]$values[1]
            $usage = ($used / $total) * 100
            
            if ($usage -gt 80) {
                Write-Host "  High memory usage: $($usage.ToString('F1'))%" -ForegroundColor Yellow
                Write-Host " Consider closing unnecessary applications or reducing batch sizes" -ForegroundColor Cyan
            } else {
                Write-Host " Memory usage optimal: $($usage.ToString('F1'))%" -ForegroundColor Green
            }
        }
    } catch {
        Write-Warning "Could not check memory usage"
    }
    
    # Performance recommendations
    Write-Host "`n Performance Optimization Recommendations:" -ForegroundColor Cyan
    
    if ($gpuMemory -lt 8000) {
        Write-Host " GPU Memory: Consider using smaller batch sizes for large models" -ForegroundColor Yellow
    }
    
    Write-Host " For AI workloads: Use mixed precision (FP16) when possible" -ForegroundColor Green
    Write-Host " For training: Enable gradient accumulation for large models" -ForegroundColor Green
    Write-Host "  Temperature: Keep GPU below 85C for optimal performance" -ForegroundColor Green
    
    Write-Host "`n GPU optimization analysis complete!" -ForegroundColor Green
}

# ===== MAIN EXECUTION =====
if ($Continuous) {
    Start-ContinuousMonitoring -IntervalSeconds $Interval
} elseif ($Benchmark) {
    Start-GPUBenchmark
} elseif ($Optimize) {
    Optimize-GPUSettings
} else {
    # Single metrics display
    $metrics = Get-GPUMetrics
    Show-GPUMetrics $metrics
    
    Write-Host "`n Usage:" -ForegroundColor Cyan
    Write-Host "   -Continuous: Start continuous monitoring" -ForegroundColor White
    Write-Host "   -Benchmark: Run GPU performance tests" -ForegroundColor White
    Write-Host "   -Optimize: Get optimization recommendations" -ForegroundColor White
    Write-Host "   -Alert: Enable performance alerts" -ForegroundColor White
}

Write-Host "`n GPU Performance Monitor ready!" -ForegroundColor Green
