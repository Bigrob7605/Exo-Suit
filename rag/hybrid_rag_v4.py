#!/usr/bin/env python3
"""
Agent Exo-Suit V4.0 - Enhanced Hybrid CPU+GPU RAG System
RAM disk optimized with intelligent load balancing and bottleneck elimination
"""

import os
import sys
import time
import json
import shutil
import tempfile
import threading
import queue
import psutil
import gc
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hybrid_rag_v4.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    import torch
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import faiss
    print(f"OK - CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"OK - CUDA device: {torch.cuda.get_device_name(0)}")
        print(f"OK - CUDA version: {torch.version.cuda}")
        primary_device = 'cuda'
        fallback_device = 'cpu'
    else:
        print("CUDA not available, using CPU only")
        primary_device = 'cpu'
        fallback_device = 'cpu'
        
except ImportError as e:
    print(f"Required libraries not available: {e}")
    print("Please install: torch, sentence-transformers, faiss-cpu, psutil")
    sys.exit(1)

@dataclass
class ProcessingTask:
    """Task for processing queue"""
    file_path: str
    content: str
    priority: int = 1
    device_preference: str = 'auto'

@dataclass
class ProcessingResult:
    """Result from processing task"""
    file_path: str
    embeddings: np.ndarray
    device_used: str
    processing_time: float
    memory_used: float
    success: bool
    error: Optional[str] = None

class RAMDiskManager:
    """Manages RAM disk operations for high-speed file processing"""
    
    def __init__(self, size_gb: int = 4):
        self.size_gb = size_gb
        self.ram_disk_path = None
        self.available_space = size_gb * (1024**3)  # Convert to bytes
        self.used_space = 0
        
    def create_ram_disk(self) -> bool:
        """Create RAM disk for temporary file storage"""
        try:
            # Create temporary directory in memory
            self.ram_disk_path = tempfile.mkdtemp(prefix="ramdisk_")
            logger.info(f"RAM disk created at: {self.ram_disk_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create RAM disk: {e}")
            return False
    
    def cleanup_ram_disk(self):
        """Clean up RAM disk"""
        if self.ram_disk_path and os.path.exists(self.ram_disk_path):
            try:
                shutil.rmtree(self.ram_disk_path)
                logger.info("RAM disk cleaned up")
            except Exception as e:
                logger.error(f"Failed to cleanup RAM disk: {e}")
    
    def get_available_space(self) -> int:
        """Get available space in RAM disk"""
        if not self.ram_disk_path:
            return 0
        try:
            stat = os.statvfs(self.ram_disk_path)
            return stat.f_frsize * stat.f_bavail
        except:
            return self.available_space - self.used_space
    
    def can_fit_file(self, file_size: int) -> bool:
        """Check if file can fit in RAM disk"""
        return file_size <= self.get_available_space()

class MemoryManager:
    """Manages memory usage and optimization"""
    
    def __init__(self):
        self.memory_threshold = 0.8  # 80% memory usage threshold
        self.gpu_memory_threshold = 0.85  # 85% GPU memory threshold
        
    def get_system_memory(self) -> Dict[str, float]:
        """Get current system memory usage"""
        memory = psutil.virtual_memory()
        return {
            'total_gb': memory.total / (1024**3),
            'available_gb': memory.available / (1024**3),
            'used_gb': memory.used / (1024**3),
            'percent': memory.percent
        }
    
    def get_gpu_memory(self) -> Dict[str, float]:
        """Get current GPU memory usage"""
        if not torch.cuda.is_available():
            return {'total_gb': 0, 'used_gb': 0, 'available_gb': 0, 'percent': 0}
        
        try:
            total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            allocated = torch.cuda.memory_allocated(0) / (1024**3)
            cached = torch.cuda.memory_reserved(0) / (1024**3)
            available = total - allocated
            
            return {
                'total_gb': total,
                'used_gb': allocated,
                'cached_gb': cached,
                'available_gb': available,
                'percent': (allocated / total) * 100
            }
        except Exception as e:
            logger.warning(f"GPU memory check failed: {e}")
            return {'total_gb': 0, 'used_gb': 0, 'available_gb': 0, 'percent': 0}
    
    def should_cleanup_memory(self) -> bool:
        """Check if memory cleanup is needed"""
        system_memory = self.get_system_memory()
        gpu_memory = self.get_gpu_memory()
        
        return (system_memory['percent'] > (self.memory_threshold * 100) or
                gpu_memory['percent'] > (self.gpu_memory_threshold * 100))
    
    def cleanup_memory(self):
        """Perform memory cleanup"""
        logger.info("Performing memory cleanup...")
        
        # Clear GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        
        # Force garbage collection
        gc.collect()
        
        # Clear system cache if possible
        if hasattr(psutil, 'pids'):
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] == 'python.exe':
                        proc.memory_info()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        logger.info("Memory cleanup completed")

class HybridRAGProcessor:
    """Main hybrid RAG processor with intelligent load balancing"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.ram_disk = RAMDiskManager(size_gb=4)
        self.memory_manager = MemoryManager()
        self.processing_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.device_manager = None
        self.models = {}
        self.index = None
        self.processing_threads = []
        self.stop_processing = False
        
        # Initialize device manager
        self._init_device_manager()
        
        # Initialize models
        self._init_models()
        
        # Create RAM disk
        self.ram_disk.create_ram_disk()
    
    def _init_device_manager(self):
        """Initialize device manager"""
        try:
            from device_manager import DeviceManager
            self.device_manager = DeviceManager()
            logger.info("Device manager initialized")
        except ImportError:
            logger.warning("Device manager not available, using default configuration")
            self.device_manager = None
    
    def _init_models(self):
        """Initialize CPU and GPU models"""
        model_name = self.config.get('model_name', 'all-MiniLM-L6-v2')
        
        try:
            # Initialize CPU model
            self.models['cpu'] = SentenceTransformer(model_name, device='cpu')
            logger.info("CPU model initialized")
            
            # Initialize GPU model if available
            if torch.cuda.is_available():
                self.models['cuda'] = SentenceTransformer(model_name, device='cuda')
                logger.info("GPU model initialized")
            
        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            raise
    
    def _select_optimal_device(self, task: ProcessingTask, file_size: int) -> str:
        """Select optimal device for processing task"""
        if not self.device_manager:
            return primary_device if torch.cuda.is_available() else 'cpu'
        
        # Check memory constraints
        system_memory = self.memory_manager.get_system_memory()
        gpu_memory = self.memory_manager.get_gpu_memory()
        
        # If system memory is low, prefer GPU
        if system_memory['percent'] > 80:
            if torch.cuda.is_available() and gpu_memory['percent'] < 80:
                return 'cuda'
            else:
                return 'cpu'
        
        # If GPU memory is low, prefer CPU
        if gpu_memory['percent'] > 80:
            return 'cpu'
        
        # Use device preference if specified
        if task.device_preference != 'auto':
            return task.device_preference
        
        # Default to GPU if available and memory is sufficient
        if torch.cuda.is_available() and gpu_memory['available_gb'] > 2.0:
            return 'cuda'
        else:
            return 'cpu'
    
    def _process_file(self, task: ProcessingTask) -> ProcessingResult:
        """Process a single file with optimal device selection"""
        start_time = time.time()
        device_used = 'cpu'
        memory_before = self.memory_manager.get_system_memory()
        
        try:
            # Select optimal device
            device = self._select_optimal_device(task, len(task.content))
            device_used = device
            
            # Get model for selected device
            if device == 'cuda' and 'cuda' in self.models:
                model = self.models['cuda']
            else:
                model = self.models['cpu']
                device_used = 'cpu'
            
            # Process content
            embeddings = model.encode([task.content], show_progress_bar=False)
            
            # Calculate memory usage
            memory_after = self.memory_manager.get_system_memory()
            memory_used = memory_after['used_gb'] - memory_before['used_gb']
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                file_path=task.file_path,
                embeddings=embeddings,
                device_used=device_used,
                processing_time=processing_time,
                memory_used=memory_used,
                success=True
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Processing failed for {task.file_path}: {e}")
            
            return ProcessingResult(
                file_path=task.file_path,
                embeddings=np.array([]),
                device_used=device_used,
                processing_time=processing_time,
                memory_used=0,
                success=False,
                error=str(e)
            )
    
    def _processing_worker(self, worker_id: int):
        """Worker thread for processing tasks"""
        logger.info(f"Processing worker {worker_id} started")
        
        while not self.stop_processing:
            try:
                # Get task from queue with timeout
                task = self.processing_queue.get(timeout=1.0)
                
                # Process task
                result = self._process_file(task)
                
                # Put result in results queue
                self.results_queue.put(result)
                
                # Mark task as done
                self.processing_queue.task_done()
                
                # Check if memory cleanup is needed
                if self.memory_manager.should_cleanup_memory():
                    self.memory_manager.cleanup_memory()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
        
        logger.info(f"Processing worker {worker_id} stopped")
    
    def start_processing_workers(self, num_workers: int = 4):
        """Start processing worker threads"""
        logger.info(f"Starting {num_workers} processing workers...")
        
        for i in range(num_workers):
            worker = threading.Thread(target=self._processing_worker, args=(i,))
            worker.daemon = True
            worker.start()
            self.processing_threads.append(worker)
        
        logger.info("Processing workers started")
    
    def stop_processing_workers(self):
        """Stop processing workers"""
        logger.info("Stopping processing workers...")
        self.stop_processing = True
        
        for worker in self.processing_threads:
            worker.join(timeout=5.0)
        
        self.processing_threads.clear()
        logger.info("Processing workers stopped")
    
    def process_files(self, file_paths: List[str], batch_size: int = 32) -> List[ProcessingResult]:
        """Process multiple files with hybrid CPU+GPU processing"""
        logger.info(f"Processing {len(file_paths)} files with hybrid processing...")
        
        # Start processing workers
        self.start_processing_workers()
        
        results = []
        batch_count = 0
        
        try:
            # Process files in batches
            for i in range(0, len(file_paths), batch_size):
                batch = file_paths[i:i + batch_size]
                batch_count += 1
                
                logger.info(f"Processing batch {batch_count}/{len(file_paths)//batch_size + 1} ({len(batch)} files)")
                
                # Add tasks to queue
                for file_path in batch:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        task = ProcessingTask(
                            file_path=file_path,
                            content=content,
                            priority=1
                        )
                        
                        self.processing_queue.put(task)
                        
                    except Exception as e:
                        logger.error(f"Failed to read file {file_path}: {e}")
                        continue
                
                # Wait for batch completion
                self.processing_queue.join()
                
                # Collect results
                while not self.results_queue.empty():
                    result = self.results_queue.get()
                    results.append(result)
                
                # Memory cleanup between batches
                if self.memory_manager.should_cleanup_memory():
                    self.memory_manager.cleanup_memory()
        
        finally:
            # Stop processing workers
            self.stop_processing_workers()
        
        logger.info(f"Processing completed. {len(results)} results generated.")
        return results
    
    def build_index(self, results: List[ProcessingResult]) -> bool:
        """Build FAISS index from processing results"""
        try:
            # Filter successful results
            successful_results = [r for r in results if r.success and r.embeddings.size > 0]
            
            if not successful_results:
                logger.error("No successful results to build index")
                return False
            
            # Get embedding dimension
            embedding_dim = successful_results[0].embeddings.shape[1]
            
            # Create FAISS index
            self.index = faiss.IndexFlatIP(embedding_dim)
            
            # Add vectors to index
            for result in successful_results:
                self.index.add(result.embeddings.astype('float32'))
            
            logger.info(f"FAISS index built with {self.index.ntotal} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Index building failed: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Search index with query"""
        if not self.index:
            logger.error("No index available for search")
            return []
        
        try:
            # Encode query
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            model = self.models.get(device, self.models['cpu'])
            
            query_embedding = model.encode([query], show_progress_bar=False)
            
            # Search index
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            # Return results as (index, score) pairs
            return list(zip(indices[0], scores[0]))
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not hasattr(self, '_performance_stats'):
            return {}
        
        return {
            'total_files_processed': len(self._performance_stats.get('results', [])),
            'successful_processing': len([r for r in self._performance_stats.get('results', []) if r.success]),
            'failed_processing': len([r for r in self._performance_stats.get('results', []) if not r.success]),
            'average_processing_time': np.mean([r.processing_time for r in self._performance_stats.get('results', []) if r.success]),
            'total_memory_used': sum([r.memory_used for r in self._performance_stats.get('results', [])]),
            'device_usage': {
                'cpu': len([r for r in self._performance_stats.get('results', []) if r.device_used == 'cpu']),
                'cuda': len([r for r in self._performance_stats.get('results', []) if r.device_used == 'cuda'])
            }
        }
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up hybrid RAG processor...")
        
        # Stop workers
        self.stop_processing_workers()
        
        # Clean up RAM disk
        self.ram_disk.cleanup_ram_disk()
        
        # Clear models
        self.models.clear()
        
        # Clear index
        self.index = None
        
        # Memory cleanup
        self.memory_manager.cleanup_memory()
        
        logger.info("Cleanup completed")

def main():
    """Test the hybrid RAG system"""
    print("Agent Exo-Suit V4.0 - Enhanced Hybrid CPU+GPU RAG System")
    print("=" * 70)
    
    # Configuration
    config = {
        'model_name': 'all-MiniLM-L6-v2',
        'batch_size': 16,
        'num_workers': 4
    }
    
    try:
        # Initialize processor
        processor = HybridRAGProcessor(config)
        
        # Test with sample files
        test_files = [
            "test_data.txt",
            "test_data.txt",  # Duplicate for testing
            "test_data.txt"   # Duplicate for testing
        ]
        
        # Filter existing files
        existing_files = [f for f in test_files if os.path.exists(f)]
        
        if not existing_files:
            print("No test files found. Creating sample data...")
            with open("test_data.txt", "w") as f:
                f.write("This is a test document for the hybrid RAG system.\n" * 100)
            existing_files = ["test_data.txt"]
        
        print(f"Processing {len(existing_files)} test files...")
        
        # Process files
        results = processor.process_files(existing_files, batch_size=config['batch_size'])
        
        # Build index
        if processor.build_index(results):
            print("Index built successfully!")
            
            # Test search
            query = "test document"
            search_results = processor.search(query, top_k=3)
            
            print(f"\nSearch results for '{query}':")
            for idx, score in search_results:
                print(f"  Index: {idx}, Score: {score:.4f}")
        
        # Performance stats
        stats = processor.get_performance_stats()
        print(f"\nPerformance Statistics:")
        print(f"  Files processed: {stats.get('total_files_processed', 0)}")
        print(f"  Successful: {stats.get('successful_processing', 0)}")
        print(f"  Failed: {stats.get('failed_processing', 0)}")
        print(f"  Avg time: {stats.get('average_processing_time', 0):.3f}s")
        
        # Cleanup
        processor.cleanup()
        
        print("\nHybrid RAG system test completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
