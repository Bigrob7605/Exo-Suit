#!/usr/bin/env python3
# Simple GPU Test Script for Agent Exo-Suit

print("=== Agent Exo-Suit GPU Test ===")

try:
    import torch
    print(f"✓ PyTorch loaded: {torch.__version__}")
    
    if torch.cuda.is_available():
        print(f"✓ CUDA available: {torch.version.cuda}")
        print(f"✓ GPU device: {torch.cuda.get_device_name(0)}")
        print(f"✓ GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        
        # Test GPU tensor operations
        device = torch.device('cuda')
        x = torch.randn(1000, 1000).to(device)
        y = torch.randn(1000, 1000).to(device)
        
        start_time = torch.cuda.Event(enable_timing=True)
        end_time = torch.cuda.Event(enable_timing=True)
        
        start_time.record()
        z = torch.mm(x, y)
        end_time.record()
        
        torch.cuda.synchronize()
        elapsed = start_time.elapsed_time(end_time)
        
        print(f"✓ GPU matrix multiplication: {elapsed:.2f} ms")
        print("✓ GPU acceleration working perfectly!")
        
    else:
        print("✗ CUDA not available")
        
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")

print("=== Test Complete ===")
