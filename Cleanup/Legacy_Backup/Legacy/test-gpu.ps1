# Agent Exo-Suit GPU Test Script
Write-Host "=== Agent Exo-Suit GPU Test ===" -ForegroundColor Green

# Test Python GPU support
Write-Host "Testing Python GPU support..." -ForegroundColor Yellow

$pythonOutput = & ".\rag_env\Scripts\python.exe" -c "
import torch
print('PyTorch version:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('CUDA version:', torch.version.cuda)
    print('GPU device:', torch.cuda.get_device_name(0))
    print('GPU memory:', torch.cuda.get_device_properties(0).total_memory / 1024**3, 'GB')
else:
    print('CUDA not available')
"

Write-Host "Python Output:" -ForegroundColor Cyan
$pythonOutput | ForEach-Object { Write-Host $_ }

# Test GPU tensor operations
Write-Host "`nTesting GPU tensor operations..." -ForegroundColor Yellow

$gpuTestOutput = & ".\rag_env\Scripts\python.exe" -c "
import torch
import time

if torch.cuda.is_available():
    device = torch.device('cuda')
    print('Testing GPU matrix multiplication...')
    
    # Create large tensors on GPU
    x = torch.randn(2000, 2000).to(device)
    y = torch.randn(2000, 2000).to(device)
    
    # Warm up GPU
    for _ in range(3):
        _ = torch.mm(x, y)
    
    torch.cuda.synchronize()
    
    # Time the operation
    start_time = time.time()
    z = torch.mm(x, y)
    torch.cuda.synchronize()
    end_time = time.time()
    
    elapsed = (end_time - start_time) * 1000
    print(f'GPU matrix multiplication (2000x2000): {elapsed:.2f} ms')
    print('GPU acceleration working perfectly!')
else:
    print('CUDA not available for tensor operations')
"

Write-Host "GPU Test Output:" -ForegroundColor Cyan
$gpuTestOutput | ForEach-Object { Write-Host $_ }

Write-Host "`n=== GPU Test Complete ===" -ForegroundColor Green
