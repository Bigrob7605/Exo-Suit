# Agent Exo-Suit V4.0 - GPU Support Installation Script
# Installs proper CUDA-enabled PyTorch and GPU FAISS

Write-Host "=== Agent Exo-Suit V4.0 - GPU Support Installation ===" -ForegroundColor Green
Write-Host "Installing GPU acceleration for RTX 4070..." -ForegroundColor Yellow

# Check if we're in the right environment
if (-not (Test-Path "rag_env\Scripts\python.exe")) {
    Write-Host "ERROR: rag_env not found. Please run upgrade-to-exo.ps1 first." -ForegroundColor Red
    exit 1
}

# Activate the environment
Write-Host "Activating Python environment..." -ForegroundColor Cyan
& "rag_env\Scripts\Activate.ps1"

# Install PyTorch with CUDA support
Write-Host "Installing PyTorch with CUDA 11.8 support..." -ForegroundColor Yellow
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install GPU FAISS
Write-Host "Installing GPU FAISS..." -ForegroundColor Yellow
pip install faiss-gpu

# Install additional GPU packages
Write-Host "Installing GPU monitoring tools..." -ForegroundColor Yellow
pip install nvidia-ml-py3

# Verify installation
Write-Host "Verifying GPU support..." -ForegroundColor Cyan
python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU device: {torch.cuda.get_device_name(0)}')
    print(f'GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
else:
    print('CUDA not available - check installation')
"

Write-Host "=== GPU Installation Complete ===" -ForegroundColor Green
Write-Host "Run .\rag\test_gpu_only.py to test GPU acceleration" -ForegroundColor Yellow
