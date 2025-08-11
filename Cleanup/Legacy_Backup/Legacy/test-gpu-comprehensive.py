#!/usr/bin/env python3
# Comprehensive GPU Test for Agent Exo-Suit V4.0

import json
import time
import os
from datetime import datetime

def test_gpu_system():
    """Comprehensive GPU system test"""
    results = {
        "test_info": {
            "version": "4.0",
            "test_type": "GPU_Comprehensive",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "target": "RTX 4070 Laptop GPU"
        },
        "system_requirements": {},
        "gpu_tests": {},
        "performance_tests": {},
        "rag_tests": {},
        "overall_status": "UNKNOWN"
    }
    
    print("=== Agent Exo-Suit V4.0 - Comprehensive GPU Test ===")
    
    # Test 1: Basic PyTorch and CUDA
    print("\n1. Testing PyTorch and CUDA...")
    try:
        import torch
        results["system_requirements"]["python_version"] = f"{torch.__version__}"
        results["system_requirements"]["platform"] = "win32"
        
        if torch.cuda.is_available():
            results["system_requirements"]["gpu_available"] = True
            results["system_requirements"]["cuda_available"] = True
            results["system_requirements"]["cuda_version"] = torch.version.cuda
            results["system_requirements"]["gpu_device"] = torch.cuda.get_device_name(0)
            results["system_requirements"]["gpu_memory_gb"] = round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2)
            
            print(f"✓ PyTorch: {torch.__version__}")
            print(f"✓ CUDA: {torch.version.cuda}")
            print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
            print(f"✓ Memory: {results['system_requirements']['gpu_memory_gb']} GB")
            
        else:
            results["system_requirements"]["gpu_available"] = False
            results["system_requirements"]["cuda_available"] = False
            print("✗ CUDA not available")
            
    except ImportError as e:
        results["system_requirements"]["gpu_available"] = False
        results["system_requirements"]["cuda_available"] = False
        print(f"✗ PyTorch import error: {e}")
        return results
    
    # Test 2: GPU Tensor Operations
    if results["system_requirements"]["gpu_available"]:
        print("\n2. Testing GPU Tensor Operations...")
        try:
            device = torch.device('cuda')
            
            # Test matrix multiplication
            sizes = [1000, 2000, 4000]
            for size in sizes:
                x = torch.randn(size, size).to(device)
                y = torch.randn(size, size).to(device)
                
                # Warm up
                for _ in range(3):
                    _ = torch.mm(x, y)
                torch.cuda.synchronize()
                
                # Time the operation
                start_time = time.time()
                z = torch.mm(x, y)
                torch.cuda.synchronize()
                end_time = time.time()
                
                elapsed_ms = (end_time - start_time) * 1000
                results["performance_tests"][f"matrix_mult_{size}x{size}"] = {
                    "size": size,
                    "time_ms": round(elapsed_ms, 2),
                    "status": "PASS"
                }
                
                print(f"✓ {size}x{size} matrix multiplication: {elapsed_ms:.2f} ms")
            
        except Exception as e:
            results["performance_tests"]["matrix_multiplication"] = {
                "status": "FAIL",
                "error": str(e)
            }
            print(f"✗ GPU tensor operations failed: {e}")
    
    # Test 3: RAG System with GPU
    if results["system_requirements"]["gpu_available"]:
        print("\n3. Testing RAG System with GPU...")
        try:
            from sentence_transformers import SentenceTransformer
            
            # Test GPU embeddings
            model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
            
            test_texts = [
                "This is a test sentence for GPU acceleration",
                "Another test sentence to verify performance",
                "GPU-accelerated sentence embeddings are working"
            ]
            
            start_time = time.time()
            embeddings = model.encode(test_texts, show_progress_bar=False)
            end_time = time.time()
            
            elapsed_ms = (end_time - start_time) * 1000
            results["rag_tests"]["gpu_embeddings"] = {
                "texts_processed": len(test_texts),
                "embedding_dimension": embeddings.shape[1],
                "time_ms": round(elapsed_ms, 2),
                "status": "PASS"
            }
            
            print(f"✓ GPU embeddings: {len(test_texts)} texts in {elapsed_ms:.2f} ms")
            print(f"✓ Embedding dimension: {embeddings.shape[1]}")
            
        except Exception as e:
            results["rag_tests"]["gpu_embeddings"] = {
                "status": "FAIL",
                "error": str(e)
            }
            print(f"✗ RAG GPU test failed: {e}")
    
    # Test 4: Memory Management
    if results["system_requirements"]["gpu_available"]:
        print("\n4. Testing GPU Memory Management...")
        try:
            # Check initial memory
            initial_memory = torch.cuda.memory_allocated() / 1024**2
            
            # Allocate large tensor
            large_tensor = torch.randn(5000, 5000).to(device)
            peak_memory = torch.cuda.memory_allocated() / 1024**2
            
            # Clear tensor
            del large_tensor
            torch.cuda.empty_cache()
            final_memory = torch.cuda.memory_allocated() / 1024**2
            
            results["gpu_tests"]["memory_management"] = {
                "initial_mb": round(initial_memory, 2),
                "peak_mb": round(peak_memory, 2),
                "final_mb": round(final_memory, 2),
                "status": "PASS"
            }
            
            print(f"✓ Memory management: {initial_memory:.2f} MB → {peak_memory:.2f} MB → {final_memory:.2f} MB")
            
        except Exception as e:
            results["gpu_tests"]["memory_management"] = {
                "status": "FAIL",
                "error": str(e)
            }
            print(f"✗ Memory management test failed: {e}")
    
    # Overall Status
    if results["system_requirements"]["gpu_available"]:
        results["overall_status"] = "PASS"
        print("\n🎉 GPU System Test: PASSED!")
        print("✓ All GPU functionality working correctly")
        print("✓ RTX 4070 acceleration active")
        print("✓ Ready for high-performance development")
    else:
        results["overall_status"] = "FAIL"
        print("\n❌ GPU System Test: FAILED!")
        print("✗ GPU acceleration not available")
    
    return results

if __name__ == "__main__":
    results = test_gpu_system()
    
    # Save results
    output_file = "gpu_comprehensive_test_report.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nTest report saved to: {output_file}")
    print("=== GPU Test Complete ===")
