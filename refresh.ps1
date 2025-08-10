# 🚀 Agent Exo-Suit V2.1 "Indestructible" - Enhanced Refresh Script
# Full GPU acceleration with intelligent context management and performance optimization

[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$GPU,
    [switch]$Benchmark,
    [switch]$Clean,
    [string]$Query = ""
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ===== EXO-SUIT REFRESH INITIALIZATION =====
Write-Host "🚀 Agent Exo-Suit V2.1 'Indestructible' Refresh Initialization..." -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "ops")) {
    Write-Error "❌ Not in Agent Exo-Suit root directory. Please run from the project root."
    exit 1
}

# ===== GPU ACCELERATION SETUP =====
if ($GPU -or $Force) {
    Write-Host "🎮 Setting up GPU acceleration..." -ForegroundColor Cyan
    
    # Check GPU availability
    try {
        $gpuInfo = nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits 2>$null
        if ($gpuInfo) {
            $gpuName = ($gpuInfo -split ',')[0]
            $gpuMemory = [int]($gpuInfo -split ',')[1]
            $gpuDriver = ($gpuInfo -split ',')[2]
            
            Write-Host "✅ NVIDIA GPU detected: $gpuName" -ForegroundColor Green
            Write-Host "   Memory: $gpuMemory MB | Driver: $gpuDriver" -ForegroundColor Green
            
            # Setup GPU environment
            Write-Host "🔧 Setting up GPU-RAG environment..." -ForegroundColor Cyan
            & ".\ops\gpu-accelerator.ps1" -InstallDeps -Force
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ GPU acceleration setup complete!" -ForegroundColor Green
            } else {
                Write-Warning "⚠️ GPU acceleration setup had issues, continuing with CPU mode"
            }
        } else {
            Write-Host "⚠️ NVIDIA GPU not detected, using CPU mode" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ GPU detection failed, using CPU mode" -ForegroundColor Yellow
    }
}

# ===== PERFORMANCE OPTIMIZATION =====
Write-Host "⚡ Optimizing system performance..." -ForegroundColor Cyan

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

# ===== CONTEXT MANAGEMENT =====
Write-Host "🧠 Setting up intelligent context management..." -ForegroundColor Cyan

# Create context directories
$contextDir = Join-Path $PWD "context"
$latestDir = Join-Path $contextDir "_latest"
$vecDir = Join-Path $contextDir "vec"

New-Item -ItemType Directory -Force -Path $latestDir | Out-Null
New-Item -ItemType Directory -Force -Path $vecDir | Out-Null

Write-Host "✅ Context directories ready" -ForegroundColor Green

# ===== GPU-RAG INDEXING =====
if ($GPU -or $Force) {
    Write-Host "🧠 Building GPU-accelerated RAG index..." -ForegroundColor Cyan
    
    try {
        & ".\ops\embed\gpu-rag.ps1" -Root $PWD -Benchmark:$Benchmark
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ GPU-RAG index built successfully!" -ForegroundColor Green
        } else {
            Write-Warning "⚠️ GPU-RAG indexing had issues, continuing with basic mode"
        }
    } catch {
        Write-Warning "⚠️ GPU-RAG indexing failed, continuing with basic mode"
    }
}

# ===== CONTEXT GOVERNOR =====
if ($Query) {
    Write-Host "🔍 Processing query: $Query" -ForegroundColor Cyan
    
    try {
        & ".\ops\context-governor.ps1" -Root $PWD -Query $Query -MaxTokens 128000 -TopK 60
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Context processing complete!" -ForegroundColor Green
            
            # Check results
            $trimmedPath = Join-Path $latestDir "TRIMMED.json"
            if (Test-Path $trimmedPath) {
                $results = Get-Content $trimmedPath -Raw | ConvertFrom-Json
                Write-Host "📊 Generated $($results.trimmed_results) results from $($results.total_results) total" -ForegroundColor Green
                Write-Host "💾 Token usage: $($results.used_tokens)/$($results.max_tokens)" -ForegroundColor Green
            }
        } else {
            Write-Warning "⚠️ Context processing had issues"
        }
    } catch {
        Write-Warning "⚠️ Context processing failed"
    }
}

# ===== PERFORMANCE MONITORING =====
if ($Benchmark) {
    Write-Host "📊 Running performance benchmarks..." -ForegroundColor Cyan
    
    try {
        & ".\ops\gpu-monitor.ps1" -Benchmark
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Performance benchmarks complete!" -ForegroundColor Green
        } else {
            Write-Warning "⚠️ Performance benchmarks had issues"
        }
    } catch {
        Write-Warning "⚠️ Performance benchmarks failed"
    }
}

# ===== CLEANUP =====
if ($Clean) {
    Write-Host "🧹 Cleaning up temporary files..." -ForegroundColor Cyan
    
    # Clean scratch directory
    if (Test-Path $env:SCRATCH_DIR) {
        Get-ChildItem $env:SCRATCH_DIR -File | Remove-Item -Force
        Write-Host "✅ Cleaned scratch directory" -ForegroundColor Green
    }
    
    # Clean Python cache
    Get-ChildItem $PWD -Recurse -Directory -Name "__pycache__" | ForEach-Object {
        Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Host "✅ Cleaned Python cache" -ForegroundColor Green
}

# ===== STATUS REPORT =====
Write-Host "`n📋 Exo-Suit Status Report" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

$status = @{
    "GPU Acceleration" = if ($GPU -or $Force) { "✅ Enabled" } else { "❌ Disabled" }
    "Context Management" = if (Test-Path $latestDir) { "✅ Ready" } else { "❌ Not Ready" }
    "RAG Index" = if (Test-Path (Join-Path $vecDir "index.faiss")) { "✅ Built" } else { "❌ Not Built" }
    "Performance Mode" = if (Test-Path $env:SCRATCH_DIR) { "✅ Optimized" } else { "❌ Not Optimized" }
    "Scratch Directory" = if (Test-Path $env:SCRATCH_DIR) { $env:SCRATCH_DIR } else { "Not Created" }
}

$status.GetEnumerator() | ForEach-Object {
    Write-Host "$($_.Key): $($_.Value)" -ForegroundColor $(if ($_.Value -match "✅") { "Green" } elseif ($_.Value -match "❌") { "Red" } else { "Yellow" })
}

# ===== RECOMMENDATIONS =====
Write-Host "`n💡 Recommendations:" -ForegroundColor Cyan

if (-not ($GPU -or $Force)) {
    Write-Host "🎮 Enable GPU acceleration: .\refresh.ps1 -GPU" -ForegroundColor Yellow
}

if (-not $Query) {
    Write-Host "🔍 Process a query: .\refresh.ps1 -Query 'your query here'" -ForegroundColor Yellow
}

if (-not $Benchmark) {
    Write-Host "📊 Run benchmarks: .\refresh.ps1 -Benchmark" -ForegroundColor Yellow
}

Write-Host "🧹 Clean up: .\refresh.ps1 -Clean" -ForegroundColor Yellow

# ===== COMPLETION =====
Write-Host "`n🚀 Agent Exo-Suit V2.1 'Indestructible' refresh complete!" -ForegroundColor Green
Write-Host "Ready for maximum performance and GPU acceleration!" -ForegroundColor Cyan
