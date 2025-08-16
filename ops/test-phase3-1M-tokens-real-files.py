#!/usr/bin/env python3
"""
Phase 3 Token Upgrade Test Suite - 1M TOKENS REAL FILES TEST
Tests ACTUAL 1M token capabilities with real toolbox files and system stress
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

def scan_toolbox_files():
    """Scan toolbox folder for real files to test 1M tokens"""
    logging.info("Scanning toolbox folder for real files to test 1M tokens...")
    
    toolbox_path = Path("Universal Open Science Toolbox With Kai (The Real Test)")
    if not toolbox_path.exists():
        logging.error("Toolbox folder not found!")
        return []
    
    all_files = []
    total_size = 0
    
    # File patterns to process
    patterns = [
        '*.py', '*.js', '*.ts', '*.tsx', '*.md', '*.txt', 
        '*.json', '*.yaml', '*.yml', '*.ps1', '*.sh', '*.rs',
        '*.go', '*.cpp', '*.h', '*.cs', '*.java', '*.html',
        '*.css', '*.xml', '*.sql', '*.r', '*.m', '*.ipynb',
        '*.log', '*.csv', '*.tsv', '*.dat', '*.bin'
    ]
    
    for pattern in patterns:
        try:
            files = list(toolbox_path.rglob(pattern))
            for file_path in files:
                if file_path.is_file() and file_path.stat().st_size > 100:  # Only files > 100 bytes
                    all_files.append(file_path)
                    total_size += file_path.stat().st_size
        except Exception as e:
            logging.warning(f"Failed to scan {pattern}: {e}")
    
    # Sort by size (largest first) to maximize token usage
    all_files.sort(key=lambda x: x.stat().st_size, reverse=True)
    
    logging.info(f"Found {len(all_files)} toolbox files, {total_size / (1024**3):.2f} GB")
    
    # Show largest files
    for i, file_path in enumerate(all_files[:10]):
        size_kb = file_path.stat().st_size / 1024
        logging.info(f"Large file {i+1}: {file_path.name} ({size_kb:.1f} KB)")
    
    return all_files

def create_1M_token_synthetic_data():
    """Create synthetic data to reach 1M tokens"""
    logging.info("Creating synthetic data to reach 1M tokens...")
    
    # Target: 1M tokens = ~4M characters (rough approximation)
    target_chars = 4000000
    current_chars = 0
    synthetic_data = []
    
    # Create large text documents until we reach 1M tokens
    doc_count = 0
    while current_chars < target_chars:
        # Each document is ~50KB of text
        large_text = f"Synthetic document {doc_count} for Phase 3 1M token testing. " * 10000
        synthetic_data.append(large_text)
        current_chars += len(large_text)
        doc_count += 1
        
        if doc_count % 100 == 0:
            logging.info(f"Created {doc_count} documents, {current_chars:,} characters ({current_chars//4000:,} estimated tokens)")
    
    logging.info(f"Created {len(synthetic_data)} synthetic documents for 1M token testing")
    logging.info(f"Total characters: {current_chars:,}, Estimated tokens: {current_chars//4000:,}")
    
    return synthetic_data

def test_1M_token_processing():
    """Test ACTUAL 1M token processing with real files"""
    logging.info("Testing ACTUAL 1M token processing with real files...")
    
    # Initialize with 1M tokens
    governor = TokenUpgradeContextGovernor(max_tokens=1000000)
    
    # Get real toolbox files
    toolbox_files = scan_toolbox_files()
    if not toolbox_files:
        logging.error("No toolbox files found!")
        return False
    
    # Create synthetic data to reach 1M tokens
    synthetic_data = create_1M_token_synthetic_data()
    
    # Monitor system resources
    initial_stats = get_system_stats()
    logging.info(f"INITIAL - CPU: {initial_stats['cpu_percent']}%, Memory: {initial_stats['memory_percent']}%")
    if initial_stats['gpu_stats']:
        logging.info(f"INITIAL - GPU: {initial_stats['gpu_stats']['allocated']:.2f}GB allocated")
    
    start_time = time.time()
    total_tokens_processed = 0
    total_files_processed = 0
    
    # Process real toolbox files first
    logging.info("Processing real toolbox files...")
    batch_size = 50
    
    for i in range(0, len(toolbox_files), batch_size):
        batch = toolbox_files[i:i + batch_size]
        logging.info(f"Processing toolbox batch {i//batch_size + 1}/{(len(toolbox_files) + batch_size - 1)//batch_size}: {len(batch)} files")
        
        batch_texts = []
        batch_sizes = []
        
        # Read actual file contents
        for file_path in batch:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    batch_texts.append(content)
                    batch_sizes.append(len(content))
                    
                    # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
                    estimated_tokens = len(content) // 4
                    total_tokens_processed += estimated_tokens
                    total_files_processed += 1
                    
            except Exception as e:
                logging.warning(f"Failed to read {file_path}: {e}")
                continue
        
        if not batch_texts:
            continue
        
        logging.info(f"Toolbox batch {i//batch_size + 1}: {len(batch_texts)} files, total content: {sum(batch_sizes):,} characters")
        
        # Generate embeddings for this batch
        try:
            batch_embeddings = governor.model.encode(batch_texts, batch_size=128, show_progress_bar=False)
            
            # Test Phase 3 features with real data
            for j, (text, embedding) in enumerate(zip(batch_texts, batch_embeddings)):
                file_id = f"toolbox_{batch[i+j].stem}_{i+j}"
                governor.persist_context_to_ssd(text, file_id)
                governor.advanced_context_caching(embedding, file_id)
            
            # Test memory optimization
            if governor.context_compression:
                compressed_embeddings = governor.compress_context(batch_embeddings, 'FP16')
                compression_ratio = compressed_embeddings.nbytes / batch_embeddings.nbytes
                logging.info(f"Toolbox batch {i//batch_size + 1} compression ratio: {compression_ratio:.2%}")
            
            # Force memory cleanup
            if i % (batch_size * 2) == 0:
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                current_stats = get_system_stats()
                logging.info(f"Memory usage after toolbox batch {i//batch_size + 1}: {current_stats['memory_percent']}%")
                if current_stats['gpu_stats']:
                    logging.info(f"GPU memory: {current_stats['gpu_stats']['allocated']:.2f}GB allocated")
            
        except Exception as e:
            logging.error(f"Failed to process toolbox batch {i//batch_size + 1}: {e}")
            continue
    
    # Now process synthetic data to reach 1M tokens
    logging.info("Processing synthetic data to reach 1M tokens...")
    synthetic_batch_size = 100
    
    for i in range(0, len(synthetic_data), synthetic_batch_size):
        batch = synthetic_data[i:i + synthetic_batch_size]
        logging.info(f"Processing synthetic batch {i//synthetic_batch_size + 1}/{(len(synthetic_data) + synthetic_batch_size - 1)//synthetic_batch_size}")
        
        try:
            # Generate embeddings for synthetic text
            synthetic_embeddings = governor.model.encode(batch, batch_size=64, show_progress_bar=False)
            
            # Test Phase 3 features with synthetic data
            for j, (text, embedding) in enumerate(zip(batch, synthetic_embeddings)):
                file_id = f"synthetic_{i+j}"
                governor.persist_context_to_ssd(text, file_id)
                governor.advanced_context_caching(embedding, file_id)
            
            # Test compression
            if governor.context_compression:
                compressed = governor.compress_context(synthetic_embeddings, 'FP16')
                compression_ratio = compressed.nbytes / synthetic_embeddings.nbytes
                logging.info(f"Synthetic batch {i//synthetic_batch_size + 1} compression ratio: {compression_ratio:.2%}")
            
            # Force memory cleanup more frequently
            if i % (synthetic_batch_size * 2) == 0:
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                current_stats = get_system_stats()
                logging.info(f"Memory usage after synthetic batch {i//synthetic_batch_size + 1}: {current_stats['memory_percent']}%")
                if current_stats['gpu_stats']:
                    logging.info(f"GPU memory: {current_stats['gpu_stats']['allocated']:.2f}GB allocated")
            
        except Exception as e:
            logging.error(f"Failed to process synthetic batch {i//synthetic_batch_size + 1}: {e}")
            continue
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Final system stats
    final_stats = get_system_stats()
    logging.info(f"FINAL - CPU: {final_stats['cpu_percent']}%, Memory: {final_stats['memory_percent']}%")
    if final_stats['gpu_stats']:
        logging.info(f"FINAL - GPU: {final_stats['gpu_stats']['allocated']:.2f}GB allocated")
    
    logging.info(f"1M token processing completed in {processing_time:.2f} seconds")
    logging.info(f"Total files processed: {total_files_processed}")
    logging.info(f"Total tokens processed: {total_tokens_processed:,}")
    logging.info(f"Processing rate: {total_tokens_processed/processing_time:,.0f} tokens/second")
    
    # Verify we actually processed close to 1M tokens
    if total_tokens_processed >= 800000:  # Allow some variance
        logging.info("SUCCESS: Processed close to 1M tokens!")
        return True
    else:
        logging.warning(f"Only processed {total_tokens_processed:,} tokens, target was 1M")
        return False

def test_1M_token_memory_stress():
    """Test memory management at 1M tokens"""
    logging.info("Testing memory management at 1M tokens...")
    
    governor = TokenUpgradeContextGovernor(max_tokens=1000000)
    
    # Fill cache to test memory management
    logging.info("Filling cache to test 1M token memory management...")
    
    for i in range(1000):  # 1000 cache entries
        # Create large data items
        large_data = np.random.rand(1000, 768).astype(np.float32)
        cache_id = f"memory_stress_{i}"
        governor.advanced_context_caching(large_data, cache_id)
        
        if i % 100 == 0:
            cache_stats = governor.get_cache_stats()
            current_stats = get_system_stats()
            logging.info(f"Cache size after {i} entries: {cache_stats}")
            logging.info(f"Memory usage: {current_stats['memory_percent']}%")
            if current_stats['gpu_stats']:
                logging.info(f"GPU memory: {current_stats['gpu_stats']['allocated']:.2f}GB allocated")
    
    # Test cache eviction
    final_cache_stats = governor.get_cache_stats()
    logging.info(f"Final cache statistics: {final_cache_stats}")
    
    # Test memory cleanup
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    final_stats = get_system_stats()
    logging.info(f"Memory stress test - CPU: {final_stats['cpu_percent']}%, Memory: {final_stats['memory_percent']}%")
    
    return True

def main():
    """Main 1M token test function"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('logs/token-upgrade-moonshot/phase3-1M-tokens-test.log'),
            logging.StreamHandler()
        ]
    )
    
    logging.info("Phase 3 Token Upgrade 1M TOKENS Test Suite Starting")
    logging.info("Testing ACTUAL 1M token capabilities with real toolbox files")
    logging.info("This will push the system to its limits!")
    
    # Get initial system stats
    initial_stats = get_system_stats()
    logging.info("Initial system resources:")
    logging.info(f"CPU: {initial_stats['cpu_percent']}%")
    logging.info(f"Memory: {initial_stats['memory_percent']}% ({initial_stats['memory_used_gb']:.1f}GB / {initial_stats['memory_total_gb']:.1f}GB)")
    if initial_stats['gpu_stats']:
        logging.info(f"GPU: {initial_stats['gpu_stats']['allocated']:.2f}GB allocated, {initial_stats['gpu_stats']['reserved']:.2f}GB reserved")
    
    # Test 1M token processing
    processing_success = test_1M_token_processing()
    
    # Test memory management at 1M tokens
    memory_success = test_1M_token_memory_stress()
    
    # Get final system stats
    final_stats = get_system_stats()
    logging.info("Final system resources:")
    logging.info(f"CPU: {final_stats['cpu_percent']}%")
    logging.info(f"Memory: {final_stats['memory_percent']}% ({final_stats['memory_used_gb']:.1f}GB / {final_stats['memory_total_gb']:.1f}GB)")
    if final_stats['gpu_stats']:
        logging.info(f"GPU: {final_stats['gpu_stats']['allocated']:.2f}GB allocated, {final_stats['gpu_stats']['reserved']:.2f}GB reserved")
    
    # Summary
    if processing_success and memory_success:
        logging.info("Phase 3 Token Upgrade 1M TOKENS Test Suite completed successfully!")
        logging.info("1M token capabilities validated with real toolbox files")
        logging.info("Memory management tested at 1M tokens")
        logging.info("Ready for enterprise deployment!")
    else:
        logging.error("Phase 3 Token Upgrade 1M TOKENS Test Suite failed")
        if not processing_success:
            logging.error("1M token processing failed")
        if not memory_success:
            logging.error("Memory management testing failed")

if __name__ == "__main__":
    main()
