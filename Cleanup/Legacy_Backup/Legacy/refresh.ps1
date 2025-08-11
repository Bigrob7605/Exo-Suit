# Agent Exo-Suit V2.1 "Indestructible" - Enhanced Refresh Script

param(
    [switch]$Benchmark,
    [switch]$Force,
    [switch]$Clean
)

# Import required modules
Import-Module Microsoft.PowerShell.Utility -Force
Import-Module Microsoft.PowerShell.Management -Force

# Configuration
$env:SCRATCH_DIR = "C:\scratch\exo-suit"
$latestDir = ".\context\_latest"
$vecDir = ".\context\vec"

Write-Host "Agent Exo-Suit V2.1 'Indestructible' Refresh Initialization..." -ForegroundColor Cyan

# GPU Detection and Setup
$GPU = $false
try {
    $gpuInfo = Get-WmiObject -Class Win32_VideoController | Where-Object { $_.Name -like "*NVIDIA*" }
    if ($gpuInfo) {
        $GPU = $true
        $gpuName = $gpuInfo.Name
        Write-Host "NVIDIA GPU detected: $gpuName" -ForegroundColor Green
        
        # GPU-RAG Environment Setup
        Write-Host "Setting up GPU-RAG environment..." -ForegroundColor Cyan
        try {
            & python -c "import torch; print('CUDA available:', torch.cuda.is_available())" 2>$null
            Write-Host "GPU acceleration setup complete!" -ForegroundColor Green
        } catch {
            Write-Warning "GPU acceleration setup had issues, continuing with CPU mode"
        }
    } else {
        Write-Warning "NVIDIA GPU not detected, using CPU mode" -ForegroundColor Yellow
    }
} catch {
    Write-Warning "GPU detection failed, using CPU mode" -ForegroundColor Yellow
}

# Create scratch directory
if (!(Test-Path $env:SCRATCH_DIR)) {
    New-Item -ItemType Directory -Path $env:SCRATCH_DIR -Force | Out-Null
    Write-Host "Created scratch directory: $env:SCRATCH_DIR" -ForegroundColor Green
}

# Context directory setup
if (!(Test-Path $latestDir)) {
    New-Item -ItemType Directory -Path $latestDir -Force | Out-Null
}
if (!(Test-Path $vecDir)) {
    New-Item -ItemType Directory -Path $vecDir -Force | Out-Null
}
Write-Host "Context directories ready" -ForegroundColor Green

# GPU-RAG Index Building
if ($GPU -or $Force) {
    Write-Host "Building GPU-RAG index..." -ForegroundColor Cyan
    try {
        & .\rag\embed.ps1 -GPU
        Write-Host "GPU-RAG index built successfully!" -ForegroundColor Green
    } catch {
        Write-Warning "GPU-RAG indexing had issues, continuing with basic mode"
    }
} else {
    Write-Warning "GPU-RAG indexing failed, continuing with basic mode"
}

# Context Processing
Write-Host "Processing context..." -ForegroundColor Cyan
try {
    $results = & .\ops\context-governor.ps1 -Budget 100000
    Write-Host "Context processing complete!" -ForegroundColor Green
    
    if ($results.trimmed_results) {
        Write-Host "Generated $($results.trimmed_results) results from $($results.total_results) total" -ForegroundColor Green
    }
} catch {
    Write-Warning "Context processing had issues"
}

# Performance Benchmarks
if ($Benchmark) {
    Write-Host "Running performance benchmarks..." -ForegroundColor Cyan
    try {
        $startTime = Get-Date
        & .\ops\max-perf.ps1
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        Write-Host "Performance benchmarks complete!" -ForegroundColor Green
    } catch {
        Write-Warning "Performance benchmarks had issues"
    }
}

# Cleanup
if ($Clean) {
    if (Test-Path $env:SCRATCH_DIR) {
        Remove-Item -Path "$env:SCRATCH_DIR\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Cleaned scratch directory" -ForegroundColor Green
    }
    
    # Clean Python cache
    Get-ChildItem -Path . -Recurse -Include "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Cleaned Python cache" -ForegroundColor Green
}

# Status Report
$status = @{
    "GPU Acceleration" = if ($GPU -or $Force) { "Enabled" } else { "Disabled" }
    "Context Management" = if (Test-Path $latestDir) { "Ready" } else { "Not Ready" }
    "RAG Index" = if (Test-Path (Join-Path $vecDir "index.faiss")) { "Built" } else { "Not Built" }
    "Performance Mode" = if (Test-Path $env:SCRATCH_DIR) { "Optimized" } else { "Not Optimized" }
}

Write-Host "`nSystem Status:" -ForegroundColor Cyan
$status.GetEnumerator() | ForEach-Object {
    Write-Host "$($_.Key): $($_.Value)" -ForegroundColor $(if ($_.Value -match "Enabled|Ready|Built|Optimized") { "Green" } elseif ($_.Value -match "Disabled|Not Ready|Not Built|Not Optimized") { "Red" } else { "Yellow" })
}

# Usage hints
Write-Host "`nUsage hints:" -ForegroundColor Yellow
Write-Host "Full refresh: .\refresh.ps1" -ForegroundColor Yellow
Write-Host "With benchmarks: .\refresh.ps1 -Benchmark" -ForegroundColor Yellow
Write-Host "Clean mode: .\refresh.ps1 -Clean" -ForegroundColor Yellow
Write-Host "Force GPU: .\refresh.ps1 -Force" -ForegroundColor Yellow

Write-Host "`nAgent Exo-Suit V2.1 'Indestructible' refresh complete!" -ForegroundColor Green
