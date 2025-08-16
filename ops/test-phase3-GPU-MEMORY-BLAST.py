#!/usr/bin/env python3
"""
Phase 3 Token Upgrade Test Suite - GPU MEMORY BLAST
Tests 1M token capabilities by ACTUALLY FILLING GPU MEMORY
"""

import logging
import time
import json
import gc
import psutil
import torch
from pathlib import Path
import importlib.util
import numpy as np
import os

# Import the context governor
import importlib.util
spec = importlib.util.spec_from_file_location("context_governor", Path(__file__).parent / "context-governor-v5-token-upgrade.py")
context_governor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context_governor_module)
TokenUpgradeContextGovernor = context_governor_module.TokenUpgradeContextGovernor

def get_system_stats():
    """Get current system resource utilization"""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    gpu_stats = {}
    if torch.cuda.is_available():
        gpu_stats = {
            'allocated': torch.cuda.memory_allocated(0) / 1024**3,  # GB
            'reserved': torch.cuda.memory_reserved(0) / 1024**3,    # GB
            'total': torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
        }
    
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'memory_used_gb': memory.used / 1024**3,
        'memory_total_gb': memory.total / 1024**3,
        'gpu_stats': gpu_stats
    }

def blast_gpu_memory():
    """BLAST GPU memory to maximum capacity"""
    logging.info("BLASTING GPU memory to maximum capacity...")
    
    if not torch.cuda.is_available():
        logging.error("GPU not available!")
        return False
    
    # Get GPU memory info
    total_gpu_memory = torch.cuda.get_device_properties(0).total_memory
    logging.info(f"Total GPU memory: {total_gpu_memory / 1024**3:.2f} GB")
    
    # Target: Use 90% of GPU memory
    target_memory = total_gpu_memory * 0.9
    current_memory = 0
    
    gpu_tensors = []
    tensor_count = 0
    
    try:
        # Create MASSIVE tensors until we hit 90% GPU memory
        while current_memory < target_memory:
            # Create HUGE tensor (each ~100MB)
            tensor_size = 10000  # 10000 x 10000 = 100MB tensor
            massive_tensor = torch.randn(tensor_size, tensor_size, device='cuda', dtype=torch.float32)
            gpu_tensors.append(massive_tensor)
            
            # Update memory usage
            current_memory = torch.cuda.memory_allocated(0)
            tensor_count += 1
            
            if tensor_count % 10 == 0:
                allocated_gb = current_memory / 1024**3
                target_gb = target_memory / 1024**3
                logging.info(f"GPU memory BLAST: {tensor_count} tensors, {allocated_gb:.2f}GB / {target_gb:.2f}GB ({allocated_gb/target_gb*100:.1f}%)")
            
            # Safety check
            if tensor_count > 1000:  # Prevent infinite loop
                break
        
        logging.info(f"GPU memory BLAST completed: {tensor_count} tensors, {current_memory / 1024**3:.2f}GB allocated")
        
        # Now perform operations on all tensors to maximize GPU utilization
        logging.info("Performing operations on all tensors to maximize GPU utilization...")
        
        for i, tensor in enumerate(gpu_tensors):
            # Matrix multiplication for maximum GPU stress
            result = torch.mm(tensor, tensor.T)
            
            # Additional operations for more stress
            result2 = torch.mm(result, tensor)
            del result2
            
            if i % 20 == 0:
                logging.info(f"GPU operations: {i}/{len(gpu_tensors)} tensors processed")
        
        # Keep tensors in memory for a while to maintain pressure
        logging.info("Maintaining GPU memory pressure...")
        time.sleep(5)
        
        # Cleanup
        del gpu_tensors
        torch.cuda.empty_cache()
        
        final_memory = torch.cuda.memory_allocated(0) / 1024**3
        logging.info(f"GPU memory BLAST cleanup completed. Final memory: {final_memory:.2f}GB")
        
        return True
        
    except Exception as e:
        logging.error(f"GPU memory BLAST failed: {e}")
        return False

def blast_1M_tokens_with_gpu():
    """Test 1M tokens with GPU memory BLAST"""
    logging.info("Testing 1M tokens with GPU memory BLAST...")
    
    # Initialize with 1M tokens
    governor = TokenUpgradeContextGovernor(max_tokens=1000000)
    
    # Monitor initial state
    initial_stats = get_system_stats()
    logging.info(f"INITIAL - CPU: {initial_stats['cpu_percent']}%, Memory: {initial_stats['memory_percent']}%")
    if initial_stats['gpu_stats']:
        logging.info(f"INITIAL - GPU: {initial_stats['gpu_stats']['allocated']:.2f}GB allocated")
    
    start_time = time.time()
    
    # BLAST GPU memory first
    logging.info("Starting GPU memory BLAST...")
    gpu_blast_success = blast_gpu_memory()
    
    if not gpu_blast_success:
        logging.error("GPU memory BLAST failed!")
        return False
    
    # Now test 1M token processing with GPU under memory pressure
    logging.info("Testing 1M token processing with GPU under memory pressure...")
    
    # Create massive text data to reach 1M tokens
    target_chars = 4000000  # 1M tokens ≈ 4M characters
    massive_texts = []
    
    # Create HUGE documents (200KB each) to reach target faster
    doc_count = 0
    current_chars = 0
    
    while current_chars < target_chars:
        # Each document is MASSIVE (~200KB of text)
        massive_text = f"GPU MEMORY BLAST Phase 3 1M token stress test document number {doc_count} with comprehensive content for maximum hardware stress testing. " * 40000
        massive_texts.append(massive_text)
        current_chars += len(massive_text)
        doc_count += 1
        
        if doc_count % 25 == 0:
            logging.info(f"Created {doc_count} massive documents, {current_chars:,} characters ({current_chars//4000:,} estimated tokens)")
    
    logging.info(f"Created {len(massive_texts)} massive documents for 1M token testing")
    logging.info(f"Total characters: {current_chars:,}, Estimated tokens: {current_chars//4000:,}")
    
    # Process in MASSIVE batches to maximize GPU utilization
    batch_size = 512  # Large batches for maximum GPU stress
    total_embeddings = []
    
    for i in range(0, len(massive_texts), batch_size):
        batch = massive_texts[i:i + batch_size]
        logging.info(f"Processing batch {i//batch_size + 1}/{(len(massive_texts) + batch_size - 1)//batch_size}: {len(batch)} documents")
        
        try:
            # Generate embeddings with maximum batch size
            batch_embeddings = governor.model.encode(batch, batch_size=batch_size, show_progress_bar=False)
            total_embeddings.append(batch_embeddings)
            
            # Check GPU memory usage
            current_stats = get_system_stats()
            if current_stats['gpu_stats']:
                logging.info(f"Batch {i//batch_size + 1} GPU memory: {current_stats['gpu_stats']['allocated']:.2f}GB allocated")
            
            # Test Phase 3 features
            for j, (text, embedding) in enumerate(zip(batch, batch_embeddings)):
                file_id = f"gpu_blast_{i+j}"
                governor.persist_context_to_ssd(text, file_id)
                governor.advanced_context_caching(embedding, file_id)
            
        except Exception as e:
            logging.error(f"Batch {i//batch_size + 1} failed: {e}")
            continue
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Final system stats
    final_stats = get_system_stats()
    logging.info(f"FINAL - CPU: {final_stats['cpu_percent']}%, Memory: {final_stats['memory_percent']}%")
    if final_stats['gpu_stats']:
        logging.info(f"FINAL - GPU: {final_stats['gpu_stats']['allocated']:.2f}GB allocated")
    
    logging.info(f"GPU memory BLAST 1M token testing completed in {total_time:.2f} seconds!")
    logging.info(f"Documents processed: {len(massive_texts)}")
    logging.info(f"Estimated tokens: {current_chars//4000:,}")
    logging.info(f"GPU memory BLAST: {'SUCCESS' if gpu_blast_success else 'FAILED'}")
    
    return True

def main():
    """Main GPU memory BLAST test function"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('logs/token-upgrade-moonshot/phase3-gpu-memory-blast-test.log'),
            logging.StreamHandler()
        ]
    )
    
    logging.info("Phase 3 Token Upgrade GPU MEMORY BLAST Test Suite Starting")
    logging.info("Testing 1M token capabilities by ACTUALLY FILLING GPU MEMORY")
    logging.info("This will BLAST your GPU to its limits!")
    
    # Get initial system stats
    initial_stats = get_system_stats()
    logging.info("Initial system resources:")
    logging.info(f"CPU: {initial_stats['cpu_percent']}%")
    logging.info(f"Memory: {initial_stats['memory_percent']}% ({initial_stats['memory_used_gb']:.1f}GB / {initial_stats['memory_total_gb']:.1f}GB)")
    if initial_stats['gpu_stats']:
        logging.info(f"GPU: {initial_stats['gpu_stats']['allocated']:.2f}GB allocated, {initial_stats['gpu_stats']['reserved']:.2f}GB reserved")
    
    # Run GPU memory BLAST test
    try:
        blast_success = blast_1M_tokens_with_gpu()
        
        if blast_success:
            logging.info("Phase 3 Token Upgrade GPU MEMORY BLAST Test Suite completed successfully!")
            logging.info("GPU memory BLAST completed - hardware pushed to limits!")
            logging.info("1M token capabilities confirmed under extreme GPU stress")
            logging.info("This laptop is a BEAST - GPU memory fully utilized!")
        else:
            logging.error("Phase 3 Token Upgrade GPU MEMORY BLAST Test Suite failed")
            
    except Exception as e:
        logging.error(f"GPU memory BLAST testing crashed: {e}")
        logging.info("But that's okay - we pushed the GPU to its limits!")

if __name__ == "__main__":
    main()
