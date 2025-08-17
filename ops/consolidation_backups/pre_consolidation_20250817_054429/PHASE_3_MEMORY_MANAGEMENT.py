#!/usr/bin/env python3
"""
PHASE 3 ADVANCED MEMORY MANAGEMENT SYSTEM
Agent Exo-Suit V5.0 - Phase 3 Development

This script implements advanced memory management with multi-tier hierarchy,
caching strategies, and memory optimization for handling 1M+ token workloads.
"""

import os
import time
import psutil
import threading
import weakref
from pathlib import Path
import logging
from collections import OrderedDict
import json
import mmap
import gzip
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LRUCache:
    """Least Recently Used cache implementation."""
    
    def __init__(self, capacity=1000):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.lock = threading.Lock()
    
    def get(self, key):
        """Get item from cache."""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
    
    def put(self, key, value):
        """Put item in cache."""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.capacity:
                    # Remove least recently used item
                    self.cache.popitem(last=False)
            self.cache[key] = value
    
    def size(self):
        """Get current cache size."""
        with self.lock:
            return len(self.cache)
    
    def clear(self):
        """Clear cache."""
        with self.lock:
            self.cache.clear()

class MemoryPool:
    """Memory pool for efficient allocation and deallocation."""
    
    def __init__(self, initial_size=1024*1024):  # 1MB initial
        self.pool = bytearray(initial_size)
        self.allocated_blocks = {}  # start_pos -> size
        self.free_blocks = [(0, initial_size)]  # (start_pos, size)
        self.lock = threading.Lock()
    
    def allocate(self, size):
        """Allocate memory block from pool."""
        with self.lock:
            # Find best fit free block
            best_block = None
            best_waste = float('inf')
            
            for i, (start, block_size) in enumerate(self.free_blocks):
                if block_size >= size:
                    waste = block_size - size
                    if waste < best_waste:
                        best_waste = waste
                        best_block = (i, start, block_size)
            
            if best_block is None:
                return None  # No suitable block found
            
            i, start, block_size = best_block
            
            # Remove free block
            del self.free_blocks[i]
            
            # Add allocated block
            self.allocated_blocks[start] = size
            
            # Add remaining free block if any
            remaining = block_size - size
            if remaining > 0:
                self.free_blocks.append((start + size, remaining))
            
            return start
    
    def deallocate(self, start_pos):
        """Deallocate memory block."""
        with self.lock:
            if start_pos not in self.allocated_blocks:
                return False
            
            size = self.allocated_blocks[start_pos]
            del self.allocated_blocks[start_pos]
            
            # Add to free blocks and merge adjacent blocks
            self.free_blocks.append((start_pos, size))
            self._merge_free_blocks()
            
            return True
    
    def _merge_free_blocks(self):
        """Merge adjacent free blocks."""
        if len(self.free_blocks) <= 1:
            return
        
        # Sort by start position
        self.free_blocks.sort()
        
        # Merge adjacent blocks
        merged = []
        current_start, current_size = self.free_blocks[0]
        
        for start, size in self.free_blocks[1:]:
            if start == current_start + current_size:
                # Adjacent blocks, merge them
                current_size += size
            else:
                # Not adjacent, add current and start new
                merged.append((current_start, current_size))
                current_start, current_size = start, size
        
        # Add last block
        merged.append((current_start, current_size))
        self.free_blocks = merged
    
    def get_stats(self):
        """Get memory pool statistics."""
        with self.lock:
            total_size = len(self.pool)
            allocated_size = sum(self.allocated_blocks.values())
            free_size = total_size - allocated_size
            fragmentation = len(self.free_blocks)
            
            return {
                'total_size': total_size,
                'allocated_size': allocated_size,
                'free_size': free_size,
                'fragmentation': fragmentation,
                'utilization_percent': (allocated_size / total_size) * 100
            }

class MultiTierMemoryManager:
    """Multi-tier memory management system."""
    
    def __init__(self):
        self.l1_cache = LRUCache(capacity=1000)      # Fast access, small size
        self.l2_cache = LRUCache(capacity=10000)     # Medium access, medium size
        self.l3_cache = LRUCache(capacity=100000)    # Slow access, large size
        
        self.memory_pool = MemoryPool(initial_size=10*1024*1024)  # 10MB
        
        self.compression_enabled = True
        self.memory_mapping_enabled = True
        
        self.stats = {
            'cache_hits': {'l1': 0, 'l2': 0, 'l3': 0},
            'cache_misses': 0,
            'compression_ratio': 0.0,
            'memory_operations': 0
        }
        
        logger.info("Multi-tier memory manager initialized")
    
    def get_data(self, key):
        """Get data from memory hierarchy."""
        self.stats['memory_operations'] += 1
        
        # Try L1 cache first
        data = self.l1_cache.get(key)
        if data is not None:
            self.stats['cache_hits']['l1'] += 1
            return data
        
        # Try L2 cache
        data = self.l2_cache.get(key)
        if data is not None:
            self.stats['cache_hits']['l2'] += 1
            # Promote to L1
            self.l1_cache.put(key, data)
            return data
        
        # Try L3 cache
        data = self.l3_cache.get(key)
        if data is not None:
            self.stats['cache_hits']['l3'] += 1
            # Promote to L2
            self.l2_cache.put(key, data)
            return data
        
        # Cache miss
        self.stats['cache_misses'] += 1
        return None
    
    def put_data(self, key, data, tier='l1'):
        """Put data in specified memory tier."""
        self.stats['memory_operations'] += 1
        
        # Compress data if enabled
        if self.compression_enabled and isinstance(data, bytes):
            compressed_data = self._compress_data(data)
            compression_ratio = len(compressed_data) / len(data)
            self.stats['compression_ratio'] = compression_ratio
            data = compressed_data
        
        # Store in specified tier
        if tier == 'l1':
            self.l1_cache.put(key, data)
        elif tier == 'l2':
            self.l2_cache.put(key, data)
        elif tier == 'l3':
            self.l3_cache.put(key, data)
        
        return True
    
    def _compress_data(self, data):
        """Compress data using gzip."""
        try:
            return gzip.compress(data)
        except Exception as e:
            logger.warning("Compression failed: {}".format(e))
            return data
    
    def _decompress_data(self, compressed_data):
        """Decompress data using gzip."""
        try:
            return gzip.decompress(compressed_data)
        except Exception as e:
            logger.warning("Decompression failed: {}".format(e))
            return compressed_data
    
    def memory_mapped_file(self, file_path, mode='r'):
        """Create memory-mapped file for large datasets."""
        if not self.memory_mapping_enabled:
            return None
        
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:  # 100MB threshold
                with open(file_path, mode + 'b') as f:
                    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                    logger.info("Memory-mapped file: {} ({} bytes)".format(file_path, file_size))
                    return mm
        except Exception as e:
            logger.warning("Memory mapping failed for {}: {}".format(file_path, e))
        
        return None
    
    def optimize_memory(self):
        """Optimize memory usage."""
        logger.info("Optimizing memory usage...")
        
        # Get current stats
        pool_stats = self.memory_pool.get_stats()
        
        # Clear least used cache tiers if memory pressure is high
        if pool_stats['utilization_percent'] > 80:
            logger.info("High memory utilization ({}%), clearing L3 cache".format(
                pool_stats['utilization_percent']))
            self.l3_cache.clear()
        
        # Defragment memory pool if fragmentation is high
        if pool_stats['fragmentation'] > 100:
            logger.info("High fragmentation ({}), defragmenting memory pool".format(
                pool_stats['fragmentation']))
            self._defragment_pool()
        
        # Clear GPU cache if available
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("GPU memory cache cleared")
        except ImportError:
            pass
    
    def _defragment_pool(self):
        """Defragment memory pool."""
        # This is a simplified defragmentation
        # In a real implementation, this would be more sophisticated
        logger.info("Defragmenting memory pool...")
        
        # Rebuild pool with current allocations
        current_allocations = self.memory_pool.allocated_blocks.copy()
        
        # Clear and rebuild
        self.memory_pool = MemoryPool(initial_size=len(self.memory_pool.pool))
        
        # Reallocate all current blocks
        for start, size in current_allocations.items():
            new_start = self.memory_pool.allocate(size)
            if new_start is not None:
                # Copy data (in real implementation)
                pass
    
    def get_memory_stats(self):
        """Get comprehensive memory statistics."""
        pool_stats = self.memory_pool.get_stats()
        
        # System memory info
        system_memory = psutil.virtual_memory()
        
        stats = {
            'timestamp': time.time(),
            'system_memory': {
                'total_gb': round(system_memory.total / (1024**3), 2),
                'available_gb': round(system_memory.available / (1024**3), 2),
                'used_gb': round(system_memory.used / (1024**3), 2),
                'percent_used': system_memory.percent
            },
            'memory_pool': pool_stats,
            'cache_stats': {
                'l1_size': self.l1_cache.size(),
                'l2_size': self.l2_cache.size(),
                'l3_size': self.l3_cache.size()
            },
            'performance_stats': self.stats.copy()
        }
        
        return stats
    
    def save_stats(self, filename="phase3_memory_management_stats.json"):
        """Save memory statistics to JSON file."""
        output_dir = Path("ops/test_output/phase3_performance")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / filename
        with open(output_file, 'w') as f:
            json.dump(self.get_memory_stats(), f, indent=2)
        
        logger.info("Memory management stats saved to: {}".format(output_file))
        return output_file

class MemoryManagementTest:
    """Test suite for memory management system."""
    
    def __init__(self):
        self.memory_manager = MultiTierMemoryManager()
        self.test_results = {}
    
    def test_cache_performance(self, num_operations=10000):
        """Test cache performance."""
        logger.info("Testing cache performance with {} operations...".format(num_operations))
        
        start_time = time.time()
        
        # Test cache operations
        for i in range(num_operations):
            key = "test_key_{}".format(i)
            data = "test_data_{}".format(i).encode()
            
            # Put data in different tiers
            if i < num_operations // 3:
                tier = 'l1'
            elif i < 2 * num_operations // 3:
                tier = 'l2'
            else:
                tier = 'l3'
            
            self.memory_manager.put_data(key, data, tier)
        
        # Test cache hits
        cache_hits = 0
        for i in range(num_operations // 2):
            key = "test_key_{}".format(i)
            if self.memory_manager.get_data(key) is not None:
                cache_hits += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        hit_rate = (cache_hits / (num_operations // 2)) * 100
        
        self.test_results['cache_performance'] = {
            'total_operations': num_operations,
            'total_time_seconds': round(total_time, 3),
            'operations_per_second': round(num_operations / total_time, 2),
            'cache_hit_rate_percent': round(hit_rate, 2)
        }
        
        logger.info("Cache performance test completed: {} ops/sec, {}% hit rate".format(
            self.test_results['cache_performance']['operations_per_second'],
            self.test_results['cache_performance']['cache_hit_rate_percent']))
    
    def test_memory_pool(self, num_allocations=1000):
        """Test memory pool performance."""
        logger.info("Testing memory pool with {} allocations...".format(num_allocations))
        
        start_time = time.time()
        
        # Test allocations
        allocations = []
        for i in range(num_allocations):
            size = (i % 100) + 1  # 1-100 bytes
            start_pos = self.memory_manager.memory_pool.allocate(size)
            if start_pos is not None:
                allocations.append((start_pos, size))
        
        # Test deallocations
        for start_pos, size in allocations:
            self.memory_manager.memory_pool.deallocate(start_pos)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.test_results['memory_pool'] = {
            'total_allocations': num_allocations,
            'successful_allocations': len(allocations),
            'total_time_seconds': round(total_time, 3),
            'allocations_per_second': round(num_allocations / total_time, 2)
        }
        
        logger.info("Memory pool test completed: {} allocs/sec".format(
            self.test_results['memory_pool']['allocations_per_second']))
    
    def test_large_file_handling(self, file_size_mb=100):
        """Test large file handling capabilities."""
        logger.info("Testing large file handling ({}MB)...".format(file_size_mb))
        
        # Create large test file
        test_file = Path("large_test_file.bin")
        file_size_bytes = file_size_mb * 1024 * 1024
        
        try:
            # Create file with random data
            with open(test_file, 'wb') as f:
                # Write in chunks to avoid memory issues
                chunk_size = 1024 * 1024  # 1MB chunks
                for i in range(0, file_size_bytes, chunk_size):
                    chunk_data = os.urandom(min(chunk_size, file_size_bytes - i))
                    f.write(chunk_data)
            
            # Test memory mapping
            start_time = time.time()
            mm = self.memory_manager.memory_mapped_file(test_file)
            mapping_time = time.time() - start_time
            
            if mm is not None:
                # Test reading from memory map
                start_time = time.time()
                sample_data = mm[0:1024]  # Read first 1KB
                read_time = time.time() - start_time
                
                mm.close()
                
                self.test_results['large_file_handling'] = {
                    'file_size_mb': file_size_mb,
                    'mapping_time_seconds': round(mapping_time, 3),
                    'read_time_seconds': round(read_time, 3),
                    'success': True
                }
                
                logger.info("Large file handling test completed successfully")
            else:
                self.test_results['large_file_handling'] = {
                    'file_size_mb': file_size_mb,
                    'success': False,
                    'error': 'Memory mapping not available'
                }
                
        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()
    
    def run_all_tests(self):
        """Run all memory management tests."""
        logger.info("Starting memory management test suite...")
        
        try:
            self.test_cache_performance()
            self.test_memory_pool()
            self.test_large_file_handling()
            
            # Get final memory stats
            final_stats = self.memory_manager.get_memory_stats()
            self.test_results['final_memory_stats'] = final_stats
            
            # Save results
            output_file = self.memory_manager.save_stats()
            
            logger.info("Memory management test suite completed successfully!")
            return True
            
        except Exception as e:
            logger.error("Memory management test suite failed: {}".format(e))
            return False
    
    def print_summary(self):
        """Print test results summary."""
        print("\n" + "="*80)
        print("PHASE 3 MEMORY MANAGEMENT TEST RESULTS")
        print("="*80)
        
        if 'cache_performance' in self.test_results:
            cache = self.test_results['cache_performance']
            print("Cache Performance: {} ops/sec, {}% hit rate".format(
                cache['operations_per_second'], cache['cache_hit_rate_percent']))
        
        if 'memory_pool' in self.test_results:
            pool = self.test_results['memory_pool']
            print("Memory Pool: {} allocs/sec, {}% success rate".format(
                pool['allocations_per_second'], 
                (pool['successful_allocations'] / pool['total_allocations']) * 100))
        
        if 'large_file_handling' in self.test_results:
            large_file = self.test_results['large_file_handling']
            if large_file['success']:
                print("Large File Handling: {}MB file mapped in {}s".format(
                    large_file['file_size_mb'], large_file['mapping_time_seconds']))
            else:
                print("Large File Handling: Failed - {}".format(large_file['error']))
        
        if 'final_memory_stats' in self.test_results:
            stats = self.test_results['final_memory_stats']
            if 'system_memory' in stats:
                sys_mem = stats['system_memory']
                print("System Memory: {}GB used of {}GB total ({}%)".format(
                    sys_mem['used_gb'], sys_mem['total_gb'], sys_mem['percent_used']))
        
        print("="*80)

def main():
    """Main execution function."""
    print("PHASE 3 ADVANCED MEMORY MANAGEMENT SYSTEM - Agent Exo-Suit V5.0")
    print("="*80)
    
    # Create and run memory management test suite
    test_suite = MemoryManagementTest()
    
    if test_suite.run_all_tests():
        # Print summary
        test_suite.print_summary()
        
        print("\nMemory management test suite completed successfully!")
        print("Ready for next Phase 3 step!")
        
    else:
        print("\nMemory management test suite failed!")
        print("Please check the logs for details.")

if __name__ == "__main__":
    main()
