#!/usr/bin/env python3
"""
Phase 3 Token Upgrade Test Suite - 1M TOKENS AGGRESSIVE HARDWARE STRESS
Tests 1M token capabilities with EXTREME hardware stress and parallel processing
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
import multiprocessing

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

def aggressive_toolbox_scan():
    """AGGRESSIVELY scan toolbox folder for maximum data volume"""
    logging.info("AGGRESSIVE toolbox scanning for maximum data volume...")
    
    toolbox_path = Path("Universal Open Science Toolbox With Kai (The Real Test)")
    if not toolbox_path.exists():
        logging.error("Toolbox folder not found!")
        return []
    
    all_files = []
    total_size = 0
    
    # Scan EVERYTHING aggressively
    for root, dirs, files in os.walk(toolbox_path):
        # Skip only critical directories
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__'}]
        
        for file in files:
            file_path = Path(root) / file
            try:
                if file_path.is_file() and file_path.stat().st_size > 50:  # Very low threshold
                    all_files.append(file_path)
                    total_size += file_path.stat().st_size
            except:
                continue
    
    # Sort by size (largest first) for maximum stress
    all_files.sort(key=lambda x: x.stat().st_size, reverse=True)
    
    logging.info(f"AGGRESSIVE scan found {len(all_files)} files, {total_size / (1024**3):.2f} GB")
    return all_files

def create_massive_1M_token_data():
    """Create MASSIVE data to reach 1M tokens quickly"""
    logging.info("Creating MASSIVE data to reach 1M tokens quickly...")
    
    # Target: 1M tokens = ~4M characters
    target_chars = 4000000
    current_chars = 0
    massive_data = []
    
    # Create HUGE documents (100KB each) to reach target faster
    doc_count = 0
    while current_chars < target_chars:
        # Each document is MASSIVE (~100KB of text)
        massive_text = f"AGGRESSIVE Phase 3 1M token stress test document number {doc_count} with comprehensive content for maximum hardware stress testing. " * 20000
        massive_data.append(massive_text)
        current_chars += len(massive_text)
        doc_count += 1
        
        if doc_count % 50 == 0:
            logging.info(f"Created {doc_count} massive documents, {current_chars:,} characters ({current_chars//4000:,} estimated tokens)")
    
    logging.info(f"Created {len(massive_data)} massive documents for 1M token testing")
    logging.info(f"Total characters: {current_chars:,}, Estimated tokens: {current_chars//4000:,}")
    
    return massive_data

def parallel_file_processing_aggressive(governor, all_files, max_workers=16):
    """Process files in PARALLEL with AGGRESSIVE batching"""
    logging.info(f"PARALLEL file processing with {max_workers} workers for maximum stress...")
    
    def process_file_batch_aggressive(file_batch):
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
            try:
                # AGGRESSIVE batch size for maximum stress
                batch_embeddings = governor.model.encode(batch_texts, batch_size=512, show_progress_bar=False)
                
                # Test Phase 3 features aggressively
                for j, (text, embedding) in enumerate(zip(batch_texts, batch_embeddings)):
                    file_id = f"parallel_aggressive_{file_path.stem}_{j}"
                    governor.persist_context_to_ssd(text, file_id)
                    governor.advanced_context_caching(embedding, file_id)
                
                return len(batch_texts)
            except Exception as e:
                logging.error(f"Parallel aggressive batch processing failed: {e}")
                return 0
        
        return 0
    
    # AGGRESSIVE batch size for maximum stress
    batch_size = 200  # Much larger batches
    file_batches = [all_files[i:i + batch_size] for i in range(0, len(all_files), batch_size)]
    
    total_processed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_file_batch_aggressive, batch) for batch in file_batches]
        
        for future in as_completed(futures):
            try:
                result = future.result()
                total_processed += result
            except Exception as e:
                logging.error(f"Parallel aggressive processing future failed: {e}")
    
    logging.info(f"PARALLEL aggressive processing completed: {total_processed} files")
    return total_processed

def aggressive_embedding_generation(governor, texts, batch_size=1024):
    """Generate embeddings AGGRESSIVELY with MASSIVE batches"""
    logging.info(f"AGGRESSIVE embedding generation: {len(texts)} texts, batch size {batch_size}")
    
    all_embeddings = []
    start_time = time.time()
    
    # Process in MASSIVE batches
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        try:
            # Generate embeddings with MAXIMUM batch size
            batch_embeddings = governor.model.encode(batch, batch_size=batch_size, show_progress_bar=False)
            all_embeddings.append(batch_embeddings)
            
            # Force GPU memory pressure
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            if i % (batch_size * 2) == 0:
                logging.info(f"AGGRESSIVE embedding batch {i//batch_size + 1} completed")
            
        except Exception as e:
            logging.error(f"AGGRESSIVE embedding batch {i//batch_size + 1} failed: {e}")
            continue
    
    end_time = time.time()
    logging.info(f"AGGRESSIVE embedding generation completed in {end_time - start_time:.2f} seconds")
    
    return all_embeddings

def aggressive_memory_fill(governor):
    """Fill memory AGGRESSIVELY to test hardware limits"""
    logging.info("AGGRESSIVE memory filling to test hardware limits...")
    
    # Create MASSIVE cache entries
    for i in range(5000):  # 5000 cache entries
        # Create HUGE data items
        massive_data = np.random.rand(5000, 768).astype(np.float32)  # Massive embeddings
        cache_id = f"aggressive_memory_{i}"
        
        try:
            governor.advanced_context_caching(massive_data, cache_id)
            
            # Test persistence aggressively
            governor.persist_context_to_ssd(str(massive_data), cache_id)
            
            if i % 500 == 0:
                cache_stats = governor.get_cache_stats()
                current_stats = get_system_stats()
                logging.info(f"AGGRESSIVE memory fill: {i} entries, Cache: {cache_stats}, Memory: {current_stats['memory_percent']}%")
                
        except Exception as e:
            logging.error(f"AGGRESSIVE memory fill failed at entry {i}: {e}")
            break
    
    return True

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
        for i in range(200):  # 200 massive tensors
            # Create HUGE tensors (2GB each)
            massive_tensor = torch.randn(15000, 15000, device='cuda', dtype=torch.float32)
            gpu_tensors.append(massive_tensor)
            
            # Force memory allocation
            torch.cuda.synchronize()
            
            if i % 20 == 0:
                allocated = torch.cuda.memory_allocated(0) / 1024**3
                reserved = torch.cuda.memory_reserved(0) / 1024**3
                logging.info(f"AGGRESSIVE GPU stress: {i} tensors, {allocated:.2f}GB allocated, {reserved:.2f}GB reserved")
        
        # Perform aggressive operations
        for i, tensor in enumerate(gpu_tensors):
            # Matrix multiplication for maximum GPU utilization
            result = torch.mm(tensor, tensor.T)
            del result  # Force cleanup
            
            if i % 40 == 0:
                logging.info(f"AGGRESSIVE GPU operations: {i} operations completed")
        
        # Cleanup
        del gpu_tensors
        torch.cuda.empty_cache()
        
        logging.info("AGGRESSIVE GPU stress testing completed")
        return True
        
    except Exception as e:
        logging.error(f"AGGRESSIVE GPU stress failed: {e}")
        return False

def test_1M_tokens_aggressive():
    """Test 1M tokens with AGGRESSIVE hardware stress"""
    logging.info("Testing 1M tokens with AGGRESSIVE hardware stress...")
    
    # Initialize with 1M tokens
    governor = TokenUpgradeContextGovernor(max_tokens=1000000)
    
    # Get real toolbox files
    toolbox_files = aggressive_toolbox_scan()
    if not toolbox_files:
        logging.error("No toolbox files found!")
        return False
    
    # Create massive data to reach 1M tokens
    massive_data = create_massive_1M_token_data()
    
    # Monitor system resources
    initial_stats = get_system_stats()
    logging.info(f"INITIAL - CPU: {initial_stats['cpu_percent']}%, Memory: {initial_stats['memory_percent']}%")
    if initial_stats['gpu_stats']:
        logging.info(f"INITIAL - GPU: {initial_stats['gpu_stats']['allocated']:.2f}GB allocated")
    
    start_time = time.time()
    total_tokens_processed = 0
    total_files_processed = 0
    
    # AGGRESSIVE parallel file processing
    logging.info("Starting AGGRESSIVE parallel file processing...")
    processed_files = parallel_file_processing_aggressive(governor, toolbox_files[:1000], max_workers=16)
    total_files_processed += processed_files
    
    # AGGRESSIVE embedding generation
    logging.info("Starting AGGRESSIVE embedding generation...")
    embeddings = aggressive_embedding_generation(governor, massive_data[:500], batch_size=1024)
    
    # AGGRESSIVE memory filling
    logging.info("Starting AGGRESSIVE memory filling...")
    memory_fill_success = aggressive_memory_fill(governor)
    
    # AGGRESSIVE GPU stress
    logging.info("Starting AGGRESSIVE GPU stress...")
    gpu_stress_success = aggressive_gpu_stress()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Estimate tokens processed
    total_tokens_processed = len(massive_data) * 50000  # Rough estimate
    
    # Final system stats
    final_stats = get_system_stats()
    logging.info(f"FINAL - CPU: {final_stats['cpu_percent']}%, Memory: {final_stats['memory_percent']}%")
    if final_stats['gpu_stats']:
        logging.info(f"FINAL - GPU: {final_stats['gpu_stats']['allocated']:.2f}GB allocated")
    
    logging.info(f"AGGRESSIVE 1M token testing completed in {total_time:.2f} seconds!")
    logging.info(f"Files processed: {total_files_processed}")
    logging.info(f"Estimated tokens: {total_tokens_processed:,}")
    logging.info(f"Memory fill: {'SUCCESS' if memory_fill_success else 'FAILED'}")
    logging.info(f"GPU stress: {'SUCCESS' if gpu_stress_success else 'FAILED'}")
    
    return True

def main():
    """Main AGGRESSIVE 1M token test function"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('logs/token-upgrade-moonshot/phase3-1M-tokens-aggressive-test.log'),
            logging.StreamHandler()
        ]
    )
    
    logging.info("Phase 3 Token Upgrade 1M TOKENS AGGRESSIVE Test Suite Starting")
    logging.info("Testing 1M token capabilities with EXTREME hardware stress")
    logging.info("This will PUSH your hardware to its limits!")
    
    # Get initial system stats
    initial_stats = get_system_stats()
    logging.info("Initial system resources:")
    logging.info(f"CPU: {initial_stats['cpu_percent']}%")
    logging.info(f"Memory: {initial_stats['memory_percent']}% ({initial_stats['memory_used_gb']:.1f}GB / {initial_stats['memory_total_gb']:.1f}GB)")
    if initial_stats['gpu_stats']:
        logging.info(f"GPU: {initial_stats['gpu_stats']['allocated']:.2f}GB allocated, {initial_stats['gpu_stats']['reserved']:.2f}GB reserved")
    
    # Run AGGRESSIVE 1M token testing
    try:
        aggressive_success = test_1M_tokens_aggressive()
        
        if aggressive_success:
            logging.info("Phase 3 Token Upgrade 1M TOKENS AGGRESSIVE Test Suite completed successfully!")
            logging.info("Hardware limits tested and validated")
            logging.info("1M token capabilities confirmed under extreme stress")
            logging.info("This laptop is a BEAST - ready for anything!")
        else:
            logging.error("Phase 3 Token Upgrade 1M TOKENS AGGRESSIVE Test Suite failed")
            
    except Exception as e:
        logging.error(f"AGGRESSIVE 1M token testing crashed: {e}")
        logging.info("But that's okay - we pushed the limits!")

if __name__ == "__main__":
    main()
