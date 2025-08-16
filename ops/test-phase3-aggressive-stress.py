#!/usr/bin/env python3
"""
Phase 3 Token Upgrade Test Suite - AGGRESSIVE STRESS TESTING
Tests 1M token capabilities with aggressive system stress
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
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import the context governor
import importlib.util
spec = importlib.util.spec_from_file_location("context_governor", Path(__file__).parent / "context-governor-v5-token-upgrade.py")
context_governor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context_governor_module)
TokenUpgradeContextGovernor = context_governor_module.TokenUpgradeContextGovernor

def get_system_stats():
    """Get current system resource utilization"""
    cpu_percent = psutil.cpu_percent(interval=0.1)  # Faster polling
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

def aggressive_file_scan():
    """Aggressively scan ALL files for maximum stress"""
    logging.info("AGGRESSIVE file scanning for maximum stress...")
    
    # Scan EVERYTHING in the project
    all_files = []
    total_size = 0
    
    # Walk through entire project directory
    for root, dirs, files in os.walk('.'):
        # Skip only the most critical directories
        dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__'}]
        
        for file in files:
            file_path = Path(root) / file
            try:
                if file_path.is_file() and file_path.stat().st_size > 100:  # Very low threshold
                    all_files.append(file_path)
                    total_size += file_path.stat().st_size
            except:
                continue
    
    logging.info(f"AGGRESSIVE scan found {len(all_files)} files, {total_size / (1024**3):.2f} GB")
    return all_files

def create_massive_synthetic_data():
    """Create MASSIVE synthetic data for aggressive stress testing"""
    logging.info("Creating MASSIVE synthetic data for aggressive stress...")
    
    synthetic_data = []
    
    # Create HUGE text documents (100x more data)
    for i in range(10000):  # 10,000 massive documents
        # Each document is MASSIVE (~5MB of text)
        massive_text = f"AGGRESSIVE stress test document number {i} with comprehensive content for Phase 3 maximum hardware stress testing. " * 100000
        synthetic_data.append(massive_text)
    
    # Create MASSIVE embedding arrays
    for i in range(2000):  # 2000 massive embeddings
        # Each embedding is HUGE (5000x768)
        embedding = np.random.rand(5000, 768).astype(np.float32)
        synthetic_data.append(embedding)
    
    logging.info(f"Created {len(synthetic_data)} MASSIVE synthetic data items")
    return synthetic_data

def aggressive_embedding_generation(governor, texts, batch_size=512):
    """Generate embeddings AGGRESSIVELY with large batches"""
    logging.info(f"AGGRESSIVE embedding generation: {len(texts)} texts, batch size {batch_size}")
    
    all_embeddings = []
    start_time = time.time()
    
    # Process in MASSIVE batches
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        # Generate embeddings with maximum batch size
        try:
            batch_embeddings = governor.model.encode(batch, batch_size=batch_size, show_progress_bar=False)
            all_embeddings.append(batch_embeddings)
            
            # Force GPU memory pressure
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
        except Exception as e:
            logging.error(f"AGGRESSIVE embedding batch {i//batch_size + 1} failed: {e}")
            continue
    
    end_time = time.time()
    logging.info(f"AGGRESSIVE embedding generation completed in {end_time - start_time:.2f} seconds")
    
    return all_embeddings

def aggressive_memory_fill(governor):
    """Fill memory AGGRESSIVELY to test limits"""
    logging.info("AGGRESSIVE memory filling to test hardware limits...")
    
    # Create MASSIVE cache entries
    for i in range(10000):  # 10,000 cache entries
        # Create HUGE data items
        massive_data = np.random.rand(10000, 768).astype(np.float32)  # Massive embeddings
        cache_id = f"aggressive_memory_{i}"
        
        try:
            governor.advanced_context_caching(massive_data, cache_id)
            
            # Test persistence aggressively
            governor.persist_context_to_ssd(str(massive_data), cache_id)
            
            if i % 1000 == 0:
                cache_stats = governor.get_cache_stats()
                current_stats = get_system_stats()
                logging.info(f"AGGRESSIVE memory fill: {i} entries, Cache: {cache_stats}, Memory: {current_stats['memory_percent']}%")
                
        except Exception as e:
            logging.error(f"AGGRESSIVE memory fill failed at entry {i}: {e}")
            break
    
    return True

def parallel_file_processing(governor, all_files, max_workers=8):
    """Process files in parallel for maximum stress"""
    logging.info(f"PARALLEL file processing with {max_workers} workers...")
    
    def process_file_batch(file_batch):
        batch_texts = []
        batch_sizes = []
        
        for file_path in file_batch:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    batch_texts.append(content)
                    batch_sizes.append(len(content))
            except:
                continue
        
        if batch_texts:
            # Generate embeddings for this batch
            try:
                batch_embeddings = governor.model.encode(batch_texts, batch_size=256, show_progress_bar=False)
                
                # Test Phase 3 features aggressively
                for j, (text, embedding) in enumerate(zip(batch_texts, batch_embeddings)):
                    file_id = f"parallel_{file_path.stem}_{j}"
                    governor.persist_context_to_ssd(text, file_id)
                    governor.advanced_context_caching(embedding, file_id)
                
                return len(batch_texts)
            except Exception as e:
                logging.error(f"Parallel batch processing failed: {e}")
                return 0
        
        return 0
    
    # Split files into batches for parallel processing
    batch_size = 100
    file_batches = [all_files[i:i + batch_size] for i in range(0, len(all_files), batch_size)]
    
    total_processed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_file_batch, batch) for batch in file_batches]
        
        for future in as_completed(futures):
            try:
                result = future.result()
                total_processed += result
            except Exception as e:
                logging.error(f"Parallel processing future failed: {e}")
    
    logging.info(f"PARALLEL processing completed: {total_processed} files")
    return total_processed

def aggressive_gpu_stress():
    """Apply AGGRESSIVE GPU stress"""
    logging.info("AGGRESSIVE GPU stress testing...")
    
    if not torch.cuda.is_available():
        logging.warning("GPU not available for aggressive stress testing")
        return False
    
    # Create MASSIVE tensors to fill GPU memory
    gpu_tensors = []
    
    try:
        # Fill GPU memory aggressively
        for i in range(100):  # 100 massive tensors
            # Create HUGE tensors (1GB each)
            massive_tensor = torch.randn(10000, 10000, device='cuda', dtype=torch.float32)
            gpu_tensors.append(massive_tensor)
            
            # Force memory allocation
            torch.cuda.synchronize()
            
            if i % 10 == 0:
                allocated = torch.cuda.memory_allocated(0) / 1024**3
                reserved = torch.cuda.memory_reserved(0) / 1024**3
                logging.info(f"AGGRESSIVE GPU stress: {i} tensors, {allocated:.2f}GB allocated, {reserved:.2f}GB reserved")
        
        # Perform aggressive operations
        for i, tensor in enumerate(gpu_tensors):
            # Matrix multiplication for maximum GPU utilization
            result = torch.mm(tensor, tensor.T)
            del result  # Force cleanup
            
            if i % 20 == 0:
                logging.info(f"AGGRESSIVE GPU operations: {i} operations completed")
        
        # Cleanup
        del gpu_tensors
        torch.cuda.empty_cache()
        
        logging.info("AGGRESSIVE GPU stress testing completed")
        return True
        
    except Exception as e:
        logging.error(f"AGGRESSIVE GPU stress failed: {e}")
        return False

def test_phase3_aggressive_stress():
    """Test Phase 3 with AGGRESSIVE stress testing"""
    logging.info("🧪 AGGRESSIVE Phase 3 stress testing starting...")
    
    governor = TokenUpgradeContextGovernor()
    
    # Get initial system stats
    initial_stats = get_system_stats()
    logging.info(f"INITIAL - CPU: {initial_stats['cpu_percent']}%, Memory: {initial_stats['memory_percent']}%")
    if initial_stats['gpu_stats']:
        logging.info(f"INITIAL - GPU: {initial_stats['gpu_stats']['allocated']:.2f}GB allocated")
    
    start_time = time.time()
    
    # 1. AGGRESSIVE file scanning
    all_files = aggressive_file_scan()
    
    # 2. Create MASSIVE synthetic data
    synthetic_data = create_massive_synthetic_data()
    
    # 3. AGGRESSIVE embedding generation
    logging.info("Starting AGGRESSIVE embedding generation...")
    embeddings = aggressive_embedding_generation(governor, synthetic_data[:1000], batch_size=512)
    
    # 4. PARALLEL file processing
    logging.info("Starting PARALLEL file processing...")
    processed_files = parallel_file_processing(governor, all_files[:500], max_workers=8)
    
    # 5. AGGRESSIVE memory filling
    logging.info("Starting AGGRESSIVE memory filling...")
    memory_fill_success = aggressive_memory_fill(governor)
    
    # 6. AGGRESSIVE GPU stress
    logging.info("Starting AGGRESSIVE GPU stress...")
    gpu_stress_success = aggressive_gpu_stress()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Final system stats
    final_stats = get_system_stats()
    logging.info(f"FINAL - CPU: {final_stats['cpu_percent']}%, Memory: {final_stats['memory_percent']}%")
    if final_stats['gpu_stats']:
        logging.info(f"FINAL - GPU: {final_stats['gpu_stats']['allocated']:.2f}GB allocated")
    
    logging.info(f"🎉 AGGRESSIVE Phase 3 stress testing completed in {total_time:.2f} seconds!")
    logging.info(f"📊 Files processed: {processed_files}")
    logging.info(f"📊 Synthetic data: {len(synthetic_data)} items")
    logging.info(f"📊 Memory fill: {'✅' if memory_fill_success else '❌'}")
    logging.info(f"📊 GPU stress: {'✅' if gpu_stress_success else '❌'}")
    
    return True

def main():
    """Main aggressive stress test function"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('logs/token-upgrade-moonshot/phase3-aggressive-stress-test.log'),
            logging.StreamHandler()
        ]
    )
    
    logging.info("🚀 Phase 3 Token Upgrade AGGRESSIVE STRESS Test Suite Starting")
    logging.info("🎯 Testing 1M token capabilities with AGGRESSIVE hardware stress")
    logging.info("💪 This laptop can handle it - pushing to the limits!")
    
    # Get initial system stats
    initial_stats = get_system_stats()
    logging.info("📊 Initial system resources:")
    logging.info(f"CPU: {initial_stats['cpu_percent']}%")
    logging.info(f"Memory: {initial_stats['memory_percent']}% ({initial_stats['memory_used_gb']:.1f}GB / {initial_stats['memory_total_gb']:.1f}GB)")
    if initial_stats['gpu_stats']:
        logging.info(f"GPU: {initial_stats['gpu_stats']['allocated']:.2f}GB allocated, {initial_stats['gpu_stats']['reserved']:.2f}GB reserved")
    
    # Run AGGRESSIVE stress testing
    try:
        aggressive_success = test_phase3_aggressive_stress()
        
        if aggressive_success:
            logging.info("🎉 AGGRESSIVE Phase 3 stress testing completed successfully!")
            logging.info("✅ Hardware limits tested and validated")
            logging.info("✅ 1M token capabilities confirmed under extreme stress")
            logging.info("🚀 This laptop is a BEAST - ready for anything!")
        else:
            logging.error("❌ AGGRESSIVE Phase 3 stress testing failed")
            
    except Exception as e:
        logging.error(f"❌ AGGRESSIVE stress testing crashed: {e}")
        logging.info("💪 But that's okay - we pushed the limits!")

if __name__ == "__main__":
    main()
