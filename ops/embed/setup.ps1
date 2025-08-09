# GPU-RAG Setup Script for Agent Exo-Suit V2.0
# Creates virtual environment and installs sentence-transformers + FAISS

param(
    [string]$root = $PWD.Path,
    [switch]$force
)

Write-Host "🧠 Setting up GPU-RAG for Agent Exo-Suit V2.0..."

# Check for CUDA/GPU support
$cudaAvailable = $false
try {
    $cudaVersion = nvidia-smi 2>$null | Select-String "CUDA Version"
    if ($cudaVersion) {
        $cudaAvailable = $true
        Write-Host "✅ CUDA detected: $($cudaVersion.ToString())"
    }
} catch {
    Write-Host "⚠️ CUDA not detected - using CPU mode"
}

# Create virtual environment
$venvPath = Join-Path $root "rag_env"
if (Test-Path $venvPath) {
    if ($force) {
        Write-Host "Removing existing RAG environment..."
        Remove-Item $venvPath -Recurse -Force
    } else {
        Write-Host "RAG environment already exists. Use -force to recreate."
        exit 0
    }
}

Write-Host "Creating RAG virtual environment..."
python -m venv $venvPath

# Activate environment and install packages
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
    
    Write-Host "Installing sentence-transformers..."
    pip install sentence-transformers
    
    Write-Host "Installing FAISS..."
    if ($cudaAvailable) {
        Write-Host "Installing FAISS with CUDA support..."
        pip install faiss-gpu
    } else {
        Write-Host "Installing FAISS for CPU..."
        pip install faiss-cpu
    }
    
    Write-Host "Installing additional dependencies..."
    pip install numpy pandas scikit-learn
    
    # Install development dependencies
    pip install jupyter ipykernel
    
    Write-Host "✅ GPU-RAG setup complete!"
    Write-Host "Virtual environment: $venvPath"
    Write-Host "Activate with: & '$activateScript'"
    
} else {
    Write-Error "Failed to create virtual environment"
    exit 1
}
