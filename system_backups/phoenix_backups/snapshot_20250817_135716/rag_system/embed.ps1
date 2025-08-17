<#
  Builds FAISS index of source + docs with full CPU+GPU dual-mode support
  Supports: CPU-only, GPU-only, and CPU+GPU hybrid modes
#>
param(
    [switch]$GPU,
    [switch]$CPU,
    [switch]$Hybrid,
    [switch]$Force,
    [string]$Model = "all-MiniLM-L6-v2",
    [int]$ChunkSize = 512,
    [int]$Overlap = 50
)

$ErrorActionPreference = 'Stop'

Write-Host " Agent Exo-Suit V3.0 - Dual-Mode RAG Index Builder" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Load environment variables
$envFile = Join-Path $PSScriptRoot "dual_mode.env"
if (Test-Path $envFile) {
    Write-Host " Loading dual-mode environment configuration..." -ForegroundColor Yellow
    Get-Content $envFile | Where-Object { $_ -match '^[^#].*=' } | ForEach-Object {
        $key, $value = $_ -split '=', 2
        Set-Variable -Name $key -Value $value -Scope Global
        Write-Host "  $key = $value" -ForegroundColor DarkGray
    }
} else {
    Write-Host " Dual-mode config not found, using defaults" -ForegroundColor Yellow
}

# Device mode detection and configuration
$deviceMode = "auto"
if ($GPU) {
    $deviceMode = "gpu"
    Write-Host " Forcing GPU-only mode" -ForegroundColor Green
} elseif ($CPU) {
    $deviceMode = "cpu"
    Write-Host " Forcing CPU-only mode" -ForegroundColor Green
} elseif ($Hybrid) {
    $deviceMode = "hybrid"
    Write-Host " Forcing hybrid CPU+GPU mode" -ForegroundColor Green
} else {
    Write-Host " Auto-detecting optimal device configuration..." -ForegroundColor Yellow
}

# Check Python and dependencies
Write-Host " Checking Python environment..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Python: $pythonVersion" -ForegroundColor Green
    
    # Check for required packages
    $requiredPackages = @("torch", "faiss-cpu", "sentence-transformers", "numpy")
    foreach ($package in $requiredPackages) {
        try {
            $result = python -c "import $package; print('OK')" 2>&1
            if ($result -eq "OK") {
                Write-Host "   $package" -ForegroundColor Green
            } else {
                Write-Host "   $package (partial)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "   $package" -ForegroundColor Red
        }
    }
} catch {
    Write-Host " Python not available or not in PATH" -ForegroundColor Red
    exit 1
}

# GPU detection
Write-Host " Detecting GPU capabilities..." -ForegroundColor Yellow
try {
    $gpuInfo = python -c "
import torch
if torch.cuda.is_available():
    print(f'CUDA Available: {torch.cuda.is_available()}')
    print(f'GPU Count: {torch.cuda.device_count()}')
    for i in range(torch.cuda.device_count()):
        name = torch.cuda.get_device_name(i)
        memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
        print(f'GPU {i}: {name} ({memory:.1f} GB)')
else:
    print('CUDA Not Available')
" 2>&1
    
    if ($gpuInfo -match "CUDA Available: True") {
        Write-Host "   GPU acceleration available" -ForegroundColor Green
        $gpuAvailable = $true
    } else {
        Write-Host "   GPU acceleration not available" -ForegroundColor Yellow
        $gpuAvailable = $false
    }
    
    # Display GPU info
    $gpuInfo | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
    
} catch {
    Write-Host "   GPU detection failed" -ForegroundColor Yellow
    $gpuAvailable = $false
}

# CPU detection
Write-Host " Detecting CPU capabilities..." -ForegroundColor Yellow
try {
    $cpuInfo = python -c "
import multiprocessing as mp
print(f'CPU Cores: {mp.cpu_count()}')
" 2>&1
    
    Write-Host "  $cpuInfo" -ForegroundColor Green
    
} catch {
    Write-Host "   CPU detection failed" -ForegroundColor Yellow
}

# Determine final device configuration
if ($deviceMode -eq "auto") {
    if ($gpuAvailable -and $gpuAvailable) {
        $deviceMode = "hybrid"
        Write-Host " Auto-selected: Hybrid CPU+GPU mode" -ForegroundColor Green
    } elseif ($gpuAvailable) {
        $deviceMode = "gpu"
        Write-Host " Auto-selected: GPU-only mode" -ForegroundColor Green
    } else {
        $deviceMode = "cpu"
        Write-Host " Auto-selected: CPU-only mode" -ForegroundColor Green
    }
}

# Build file list
Write-Host " Building file list..." -ForegroundColor Yellow
$tmp = Join-Path $env:TEMP "rag_files.txt"

# Enhanced file discovery with exclusions
$excludePatterns = @(
    "node_modules", "target", "__pycache__", "dist", "build", 
    ".venv", "venv", "env", ".git", ".vscode", "*.pyc",
    "*.log", "*.tmp", "*.cache", "*.lock"
)

$includePatterns = @("*.py", "*.js", "*.ts", "*.md", "*.txt", "*.yml", "*.yaml", "*.json", "*.xml", "*.html", "*.css")

Write-Host "  Including: $($includePatterns -join ', ')" -ForegroundColor DarkGray
Write-Host "  Excluding: $($excludePatterns -join ', ')" -ForegroundColor DarkGray

try {
    $files = Get-ChildItem -Recurse -File -Include $includePatterns | 
             Where-Object { 
                 $exclude = $false
                 foreach ($pattern in $excludePatterns) {
                     if ($_.FullName -match [regex]::Escape($pattern) -or 
                         $_.FullName -match $pattern) {
                         $exclude = $true
                         break
                     }
                 }
                 -not $exclude
             } | 
             ForEach-Object { $_.FullName }
    
    $files | Out-File $tmp -Encoding UTF8
    Write-Host "   Found $($files.Count) files" -ForegroundColor Green
    
} catch {
    Write-Host "   File discovery failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Build command with device mode
$buildArgs = @(
    "--filelist", $tmp
)

switch ($deviceMode) {
    "gpu" { $buildArgs += "--gpu" }
    "cpu" { $buildArgs += "--cpu" }
    "hybrid" { $buildArgs += "--hybrid" }
}

Write-Host " Building RAG index with $deviceMode mode..." -ForegroundColor Cyan
Write-Host "  Command: python build_index.py $($buildArgs -join ' ')" -ForegroundColor DarkGray

try {
    $startTime = Get-Date
    
    # Run the build process
    $result = python "$PSScriptRoot\build_index.py" @buildArgs
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    if ($result -eq 0) {
        Write-Host " RAG index build completed successfully!" -ForegroundColor Green
        Write-Host " Duration: $($duration.ToString('mm\:ss'))" -ForegroundColor Cyan
        
        # Check output files
        $indexFile = Join-Path $PSScriptRoot "index.faiss"
        $metaFile = Join-Path $PSScriptRoot "meta.jsonl"
        
        if (Test-Path $indexFile) {
            $indexSize = (Get-Item $indexFile).Length / 1MB
            Write-Host " Index size: $($indexSize.ToString('F2')) MB" -ForegroundColor Cyan
        }
        
        if (Test-Path $metaFile) {
            $metaLines = (Get-Content $metaFile | Measure-Object -Line).Lines
            Write-Host " Metadata entries: $metaLines" -ForegroundColor Cyan
        }
        
    } else {
        Write-Host " RAG index build failed with exit code: $result" -ForegroundColor Red
        exit $result
    }
    
} catch {
    Write-Host " Build process failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    # Cleanup
    if (Test-Path $tmp) {
        Remove-Item $tmp -Force
        Write-Host " Temporary files cleaned up" -ForegroundColor DarkGray
    }
}

Write-Host " Dual-Mode RAG Index Builder completed!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
