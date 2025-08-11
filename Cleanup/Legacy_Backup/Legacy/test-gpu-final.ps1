# Agent Exo-Suit V4.0 - Final GPU Test Script
# Comprehensive GPU testing with detailed reporting

Write-Host "=== Agent Exo-Suit V4.0 - Final GPU Test ===" -ForegroundColor Green
Write-Host "Testing GPU acceleration for RTX 4070..." -ForegroundColor Yellow

# Test 1: Basic PyTorch CUDA Detection
Write-Host "`n[1/5] Testing PyTorch CUDA Support..." -ForegroundColor Cyan
$test1 = python -c "
import torch
print('TORCH_VERSION:' + torch.__version__)
print('CUDA_AVAILABLE:' + str(torch.cuda.is_available()))
if torch.cuda.is_available():
    print('CUDA_VERSION:' + torch.version.cuda)
    print('GPU_DEVICE:' + torch.cuda.get_device_name(0))
    print('GPU_MEMORY:' + str(torch.cuda.get_device_properties(0).total_memory / 1024**3))
else:
    print('CUDA_VERSION:None')
    print('GPU_DEVICE:None')
    print('GPU_MEMORY:None')
"

if ($test1 -match "CUDA_AVAILABLE:True") {
    Write-Host "✅ PyTorch CUDA Support: WORKING" -ForegroundColor Green
    $torch_version = ($test1 | Select-String "TORCH_VERSION:").ToString().Split(":")[1]
    $cuda_version = ($test1 | Select-String "CUDA_VERSION:").ToString().Split(":")[1]
    $gpu_device = ($test1 | Select-String "GPU_DEVICE:").ToString().Split(":")[1]
    $gpu_memory = ($test1 | Select-String "GPU_MEMORY:").ToString().Split(":")[1]
    Write-Host "   PyTorch: $torch_version" -ForegroundColor White
    Write-Host "   CUDA: $cuda_version" -ForegroundColor White
    Write-Host "   Device: $gpu_device" -ForegroundColor White
    Write-Host "   Memory: $gpu_memory GB" -ForegroundColor White
} else {
    Write-Host "❌ PyTorch CUDA Support: FAILED" -ForegroundColor Red
    Write-Host "   CUDA not available - check PyTorch installation" -ForegroundColor Yellow
}

# Test 2: GPU Tensor Operations
Write-Host "`n[2/5] Testing GPU Tensor Operations..." -ForegroundColor Cyan
$test2 = python -c "
import torch
try:
    x = torch.randn(1000, 1000).cuda()
    y = torch.randn(1000, 1000).cuda()
    z = torch.mm(x, y)
    print('TENSOR_SHAPE:' + str(z.shape))
    print('GPU_MEMORY_ALLOCATED:' + str(torch.cuda.memory_allocated() / 1024**2))
    print('GPU_MEMORY_CACHED:' + str(torch.cuda.memory_reserved() / 1024**2))
    print('STATUS:SUCCESS')
except Exception as e:
    print('STATUS:FAILED')
    print('ERROR:' + str(e))
"

if ($test2 -match "STATUS:SUCCESS") {
    Write-Host "✅ GPU Tensor Operations: WORKING" -ForegroundColor Green
    $tensor_shape = ($test2 | Select-String "TENSOR_SHAPE:").ToString().Split(":")[1]
    $memory_allocated = ($test2 | Select-String "GPU_MEMORY_ALLOCATED:").ToString().Split(":")[1]
    $memory_cached = ($test2 | Select-String "GPU_MEMORY_CACHED:").ToString().Split(":")[1]
    Write-Host "   Matrix Multiplication: $tensor_shape" -ForegroundColor White
    Write-Host "   Memory Allocated: $memory_allocated MB" -ForegroundColor White
    Write-Host "   Memory Cached: $memory_cached MB" -ForegroundColor White
} else {
    Write-Host "❌ GPU Tensor Operations: FAILED" -ForegroundColor Red
    $error_msg = ($test2 | Select-String "ERROR:").ToString().Split(":")[1]
    Write-Host "   Error: $error_msg" -ForegroundColor Yellow
}

# Test 3: RAG System GPU Test
Write-Host "`n[3/5] Testing RAG System GPU Integration..." -ForegroundColor Cyan
$test3 = python -c "
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    model = model.to('cuda')
    texts = ['This is a test sentence for GPU acceleration.']
    embeddings = model.encode(texts)
    print('EMBEDDING_SHAPE:' + str(embeddings.shape))
    print('MODEL_DEVICE:' + str(next(model.parameters()).device))
    print('STATUS:SUCCESS')
except Exception as e:
    print('STATUS:FAILED')
    print('ERROR:' + str(e))
"

if ($test3 -match "STATUS:SUCCESS") {
    Write-Host "✅ RAG System GPU Integration: WORKING" -ForegroundColor Green
    $embedding_shape = ($test3 | Select-String "EMBEDDING_SHAPE:").ToString().Split(":")[1]
    $model_device = ($test3 | Select-String "MODEL_DEVICE:").ToString().Split(":")[1]
    Write-Host "   Embeddings: $embedding_shape" -ForegroundColor White
    Write-Host "   Model Device: $model_device" -ForegroundColor White
} else {
    Write-Host "❌ RAG System GPU Integration: FAILED" -ForegroundColor Red
    $error_msg = ($test3 | Select-String "ERROR:").ToString().Split(":")[1]
    Write-Host "   Error: $error_msg" -ForegroundColor Yellow
}

# Test 4: Performance Comparison (GPU vs CPU)
Write-Host "`n[4/5] Testing GPU vs CPU Performance..." -ForegroundColor Cyan
$test4 = python -c "
import time
import torch

try:
    size = 2000
    x_cpu = torch.randn(size, size)
    y_cpu = torch.randn(size, size)
    
    # CPU timing
    start = time.time()
    z_cpu = torch.mm(x_cpu, y_cpu)
    cpu_time = time.time() - start
    
    # GPU timing
    x_gpu = x_cpu.cuda()
    y_gpu = y_cpu.cuda()
    
    start = time.time()
    z_gpu = torch.mm(x_gpu, y_gpu)
    gpu_time = time.time() - start
    
    speedup = cpu_time / gpu_time
    
    print('CPU_TIME:' + str(cpu_time))
    print('GPU_TIME:' + str(gpu_time))
    print('SPEEDUP:' + str(speedup))
    print('STATUS:SUCCESS')
except Exception as e:
    print('STATUS:FAILED')
    print('ERROR:' + str(e))
"

if ($test4 -match "STATUS:SUCCESS") {
    Write-Host "✅ GPU vs CPU Performance: WORKING" -ForegroundColor Green
    $cpu_time = ($test4 | Select-String "CPU_TIME:").ToString().Split(":")[1]
    $gpu_time = ($test4 | Select-String "GPU_TIME:").ToString().Split(":")[1]
    $speedup = ($test4 | Select-String "SPEEDUP:").ToString().Split(":")[1]
    Write-Host "   CPU Time: $cpu_time seconds" -ForegroundColor White
    Write-Host "   GPU Time: $gpu_time seconds" -ForegroundColor White
    Write-Host "   Speedup: $speedup x" -ForegroundColor White
    
    if ([double]$speedup -gt 2.0) {
        Write-Host "   Performance: EXCELLENT (>2x speedup)" -ForegroundColor Green
    } elseif ([double]$speedup -gt 1.5) {
        Write-Host "   Performance: GOOD (>1.5x speedup)" -ForegroundColor Yellow
    } else {
        Write-Host "   Performance: POOR (<1.5x speedup)" -ForegroundColor Red
    }
} else {
    Write-Host "❌ GPU vs CPU Performance: FAILED" -ForegroundColor Red
    $error_msg = ($test4 | Select-String "ERROR:").ToString().Split(":")[1]
    Write-Host "   Error: $error_msg" -ForegroundColor Yellow
}

# Test 5: System Integration Test
Write-Host "`n[5/5] Testing System Integration..." -ForegroundColor Cyan
$test5 = python -c "
import os
import sys
import torch

try:
    print('PYTHON_PATH:' + sys.executable)
    print('WORKING_DIR:' + os.getcwd())
    print('CUDA_STATUS:' + str(torch.cuda.is_available()))
    print('GPU_COUNT:' + str(torch.cuda.device_count()))
    print('ENV_ACTIVATED:' + str('rag_env' in sys.executable))
    print('STATUS:SUCCESS')
except Exception as e:
    print('STATUS:FAILED')
    print('ERROR:' + str(e))
"

if ($test5 -match "STATUS:SUCCESS") {
    Write-Host "✅ System Integration: WORKING" -ForegroundColor Green
    $python_path = ($test5 | Select-String "PYTHON_PATH:").ToString().Split(":")[1]
    $working_dir = ($test5 | Select-String "WORKING_DIR:").ToString().Split(":")[1]
    $cuda_status = ($test5 | Select-String "CUDA_STATUS:").ToString().Split(":")[1]
    $gpu_count = ($test5 | Select-String "GPU_COUNT:").ToString().Split(":")[1]
    $env_activated = ($test5 | Select-String "ENV_ACTIVATED:").ToString().Split(":")[1]
    
    Write-Host "   Python: $python_path" -ForegroundColor White
    Write-Host "   Working Directory: $working_dir" -ForegroundColor White
    Write-Host "   CUDA Status: $cuda_status" -ForegroundColor White
    Write-Host "   GPU Count: $gpu_count" -ForegroundColor White
    Write-Host "   Environment: $env_activated" -ForegroundColor White
} else {
    Write-Host "❌ System Integration: FAILED" -ForegroundColor Red
    $error_msg = ($test5 | Select-String "ERROR:").ToString().Split(":")[1]
    Write-Host "   Error: $error_msg" -ForegroundColor Yellow
}

# Final Summary
Write-Host "`n=== GPU TEST SUMMARY ===" -ForegroundColor Green
Write-Host "All GPU tests completed. Check results above for any issues." -ForegroundColor Yellow

# Count successes and failures
$success_count = 0
$failure_count = 0

if ($test1 -match "CUDA_AVAILABLE:True") { $success_count++ } else { $failure_count++ }
if ($test2 -match "STATUS:SUCCESS") { $success_count++ } else { $failure_count++ }
if ($test3 -match "STATUS:SUCCESS") { $success_count++ } else { $failure_count++ }
if ($test4 -match "STATUS:SUCCESS") { $success_count++ } else { $failure_count++ }
if ($test5 -match "STATUS:SUCCESS") { $success_count++ } else { $failure_count++ }

Write-Host "`nTest Results: $success_count/5 tests PASSED" -ForegroundColor Green
if ($failure_count -gt 0) {
    Write-Host "Failed Tests: $failure_count" -ForegroundColor Red
    Write-Host "GPU functionality is NOT 100% - review failed tests above" -ForegroundColor Yellow
} else {
    Write-Host "🎉 ALL TESTS PASSED! GPU functionality is 100% operational!" -ForegroundColor Green
}

Write-Host "`n=== NEXT STEPS ===" -ForegroundColor Cyan
if ($failure_count -eq 0) {
    Write-Host "✅ GPU system is fully operational!" -ForegroundColor Green
    Write-Host "   - Run .\go-big.ps1 to test full system integration" -ForegroundColor White
    Write-Host "   - Test .\AgentExoSuitV3.ps1 for performance mode" -ForegroundColor White
    Write-Host "   - Monitor GPU performance during operations" -ForegroundColor White
} else {
    Write-Host "⚠️  GPU system needs attention:" -ForegroundColor Yellow
    Write-Host "   - Review failed tests above" -ForegroundColor White
    Write-Host "   - Check GPU drivers and CUDA installation" -ForegroundColor White
    Write-Host "   - Verify Python environment configuration" -ForegroundColor White
    Write-Host "   - Re-run tests after fixing issues" -ForegroundColor White
}

Write-Host "`n=== GPU TEST COMPLETE ===" -ForegroundColor Green
