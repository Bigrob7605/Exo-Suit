# 🚀 GPU Accelerator for Agent Exo-Suit V2.1 "Indestructible"
# Full CUDA acceleration with fallback to CPU for maximum performance

[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$Benchmark,
    [switch]$InstallDeps,
    [string]$Model = "all-MiniLM-L6-v2"
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ===== GPU DETECTION & VALIDATION =====
Write-Host "🎮 GPU Accelerator Initialization..." -ForegroundColor Cyan

$gpuInfo = @{
    CUDA = $false
    GPU = $false
    Memory = 0
    Driver = ""
    Compute = ""
}

# Check NVIDIA GPU
try {
    $nvidiaOutput = nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap --format=csv,noheader,nounits 2>$null
    if ($nvidiaOutput) {
        $gpuInfo.GPU = $true
        $gpuInfo.Driver = ($nvidiaOutput -split ',')[2]
        $gpuInfo.Memory = [int]($nvidiaOutput -split ',')[1]
        $gpuInfo.Compute = ($nvidiaOutput -split ',')[3]
        Write-Host "✅ NVIDIA GPU detected: $($nvidiaOutput -split ',')[0]" -ForegroundColor Green
        Write-Host "   Memory: $($gpuInfo.Memory) MB | Driver: $($gpuInfo.Driver) | Compute: $($gpuInfo.Compute)" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ NVIDIA GPU not detected" -ForegroundColor Yellow
}

# Check CUDA availability
try {
    $cudaVersion = nvidia-smi 2>$null | Select-String "CUDA Version"
    if ($cudaVersion) {
        $gpuInfo.CUDA = $true
        Write-Host "✅ CUDA detected: $($cudaVersion.ToString())" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ CUDA not detected" -ForegroundColor Yellow
}

# Check PyTorch CUDA support
try {
    $torchCuda = python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A')" 2>$null
    if ($torchCuda -match "CUDA available: True") {
        Write-Host "✅ PyTorch CUDA support confirmed" -ForegroundColor Green
    } else {
        Write-Host "⚠️ PyTorch CUDA support not available" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ PyTorch not installed or CUDA support unavailable" -ForegroundColor Yellow
}

# ===== ENVIRONMENT OPTIMIZATION =====
Write-Host "🔧 Optimizing environment for GPU acceleration..." -ForegroundColor Cyan

# Set CUDA environment variables
$env:CUDA_VISIBLE_DEVICES = "0"
$env:CUDA_LAUNCH_BLOCKING = "1"
$env:TORCH_CUDA_ARCH_LIST = "8.6"  # RTX 4070 architecture

# Set performance environment variables
$env:SCRATCH_DIR = Join-Path $env:TEMP "exo_suit_scratch"
$env:NODE_OPTIONS = "--max-old-space-size=12288"
$env:PIP_CACHE_DIR = Join-Path $env:SCRATCH_DIR "pip"
$env:NPM_CONFIG_CACHE = Join-Path $env:SCRATCH_DIR "npm"

# Create scratch directory if it doesn't exist
if (-not (Test-Path $env:SCRATCH_DIR)) {
    New-Item -ItemType Directory -Force -Path $env:SCRATCH_DIR | Out-Null
    Write-Host "✅ Created scratch directory: $env:SCRATCH_DIR" -ForegroundColor Green
}

# ===== GPU-OPTIMIZED RAG SETUP =====
if ($InstallDeps) {
    Write-Host "📦 Installing GPU-optimized dependencies..." -ForegroundColor Cyan
    
    # Create virtual environment
    $venvPath = Join-Path $PWD "gpu_rag_env"
    if ((Test-Path $venvPath) -and (-not $Force)) {
        Write-Host "Virtual environment exists. Use -Force to recreate." -ForegroundColor Yellow
    } else {
        if (Test-Path $venvPath) {
            Remove-Item $venvPath -Recurse -Force
        }
        
        python -m venv $venvPath
        $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
        
        if (Test-Path $activateScript) {
            & $activateScript
            
            Write-Host "Installing PyTorch with CUDA support..." -ForegroundColor Cyan
            if ($gpuInfo.CUDA) {
                pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
            } else {
                pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
            }
            
            Write-Host "Installing sentence-transformers..." -ForegroundColor Cyan
            pip install sentence-transformers
            
            Write-Host "Installing FAISS..." -ForegroundColor Cyan
            if ($gpuInfo.CUDA) {
                pip install faiss-gpu
            } else {
                pip install faiss-cpu
            }
            
            Write-Host "Installing additional dependencies..." -ForegroundColor Cyan
            pip install numpy pandas scikit-learn transformers accelerate
            
            Write-Host "✅ GPU-RAG environment setup complete!" -ForegroundColor Green
        }
    }
}

# ===== GPU BENCHMARKING =====
if ($Benchmark) {
    Write-Host "📊 Running GPU benchmarks..." -ForegroundColor Cyan
    
    $benchmarkScript = @"
import time
import torch
import numpy as np
from sentence_transformers import SentenceTransformer

def benchmark_gpu():
    print("🚀 GPU Benchmark Suite")
    print("=" * 50)
    
    # Check CUDA availability
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")
    
    if cuda_available:
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        print(f"CUDA Version: {torch.version.cuda}")
        
        # Memory benchmark
        torch.cuda.empty_cache()
        start_mem = torch.cuda.memory_allocated(0)
        
        # Create test tensors
        test_tensor = torch.randn(1000, 1000, device='cuda')
        end_mem = torch.cuda.memory_allocated(0)
        
        print(f"Memory Usage: {(end_mem - start_mem) / 1024**2:.1f} MB")
        
        # Matrix multiplication benchmark
        start_time = time.time()
        for _ in range(100):
            result = torch.mm(test_tensor, test_tensor.T)
        torch.cuda.synchronize()
        end_time = time.time()
        
        print(f"Matrix Mult (100x): {(end_time - start_time)*1000:.1f} ms")
        
        # Cleanup
        del test_tensor, result
        torch.cuda.empty_cache()
    
    # Sentence transformer benchmark
    print("\\n📝 Sentence Transformer Benchmark")
    model = SentenceTransformer('$Model')
    
    test_texts = ["This is a test sentence for benchmarking."] * 100
    
    if cuda_available:
        model = model.to('cuda')
        print("Model moved to GPU")
    
    start_time = time.time()
    embeddings = model.encode(test_texts, show_progress_bar=False)
    end_time = time.time()
    
    print(f"100 embeddings: {(end_time - start_time)*1000:.1f} ms")
    print(f"Embedding shape: {embeddings.shape}")
    
    return cuda_available

if __name__ == '__main__':
    benchmark_gpu()
"@
    
    $benchmarkPath = Join-Path $env:SCRATCH_DIR "gpu_benchmark.py"
    $benchmarkScript | Out-File $benchmarkPath -Encoding utf8
    
    Write-Host "Running GPU benchmark..." -ForegroundColor Cyan
    python $benchmarkPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ GPU benchmark complete!" -ForegroundColor Green
    } else {
        Write-Warning "GPU benchmark failed"
    }
}

# ===== GPU STATUS REPORT =====
Write-Host "📋 GPU Acceleration Status Report" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

$status = @{
    "NVIDIA GPU" = if ($gpuInfo.GPU) { "✅ Available" } else { "❌ Not Detected" }
    "CUDA Support" = if ($gpuInfo.CUDA) { "✅ Available" } else { "❌ Not Available" }
    "PyTorch CUDA" = if ($torchCuda -match "CUDA available: True") { "✅ Available" } else { "❌ Not Available" }
    "GPU Memory" = if ($gpuInfo.Memory -gt 0) { "$($gpuInfo.Memory) MB" } else { "Unknown" }
    "Driver Version" = if ($gpuInfo.Driver) { $gpuInfo.Driver } else { "Unknown" }
    "Compute Capability" = if ($gpuInfo.Compute) { $gpuInfo.Compute } else { "Unknown" }
}

$status.GetEnumerator() | ForEach-Object {
    Write-Host "$($_.Key): $($_.Value)" -ForegroundColor $(if ($_.Value -match "✅") { "Green" } elseif ($_.Value -match "❌") { "Red" } else { "Yellow" })
}

# ===== RECOMMENDATIONS =====
Write-Host "`n💡 Recommendations:" -ForegroundColor Cyan

if (-not $gpuInfo.GPU) {
    Write-Host "❌ Install NVIDIA drivers and GPU" -ForegroundColor Red
} elseif (-not $gpuInfo.CUDA) {
    Write-Host "❌ Install CUDA toolkit" -ForegroundColor Red
} elseif ($torchCuda -notmatch "CUDA available: True") {
    Write-Host "❌ Reinstall PyTorch with CUDA support" -ForegroundColor Red
    Write-Host "   Run: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118" -ForegroundColor Yellow
} else {
    Write-Host "✅ GPU acceleration fully operational!" -ForegroundColor Green
    Write-Host "   Run with -Benchmark to test performance" -ForegroundColor Cyan
}

Write-Host "`n🚀 GPU Accelerator initialization complete!" -ForegroundColor Green
