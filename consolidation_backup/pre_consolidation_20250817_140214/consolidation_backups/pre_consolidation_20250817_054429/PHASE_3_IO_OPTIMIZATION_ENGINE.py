#!/usr/bin/env python3
"""
PHASE 3 I/O OPTIMIZATION ENGINE
Agent Exo-Suit V5.0 - Phase 3 Development

This script implements Phase 1 optimization focusing on:
- Memory-mapped file I/O for faster reading
- Streaming processing to reduce memory pressure
- Batch I/O operations for parallel file access
- Optimized encoding handling

Target: Achieve 10K+ files/sec (20x improvement over current 462 files/sec)
"""

import os
import time
import threading
import concurrent.futures
from pathlib import Path
import logging
import json
import hashlib
import re
import mmap
from collections import defaultdict
import psutil
import torch
import numpy as np
from io import BytesIO
import gzip
import bz2
import lzma

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedIOProcessor:
    """I/O optimized processor using memory mapping and streaming."""
    
    def __init__(self):
        self.processed_files = 0
        self.total_content_size = 0
        self.content_stats = defaultdict(int)
        self.lock = threading.Lock()
        
        # GPU setup for optimized processing
        self.gpu_available = torch.cuda.is_available()
        if self.gpu_available:
            self.device = torch.device('cuda')
            logger.info("GPU processing enabled on: {}".format(torch.cuda.get_device_name()))
        else:
            self.device = torch.device('cpu')
            logger.warning("GPU not available, using CPU")
        
        # Pre-compile regex patterns for faster matching
        self._compile_regex_patterns()
        
    def _compile_regex_patterns(self):
        """Pre-compile all regex patterns for maximum performance."""
        self.patterns = {
            'markdown': [
                re.compile(r'#+\s+', re.MULTILINE),           # Headers
                re.compile(r'-\s+', re.MULTILINE),            # List items
                re.compile(r'', re.MULTILINE),               # Inline code
                re.compile(r'', re.MULTILINE),              # Code blocks
                re.compile(r'\[.*?\]\(.*?\)', re.MULTILINE),   # Links
                re.compile(r'\*\*.*?\*\*', re.MULTILINE),      # Bold text
                re.compile(r'\*.*?\*', re.MULTILINE),          # Italic text
                re.compile(r'!\[.*?\]\(.*?\)', re.MULTILINE),  # Images
                re.compile(r'\|.*?\|', re.MULTILINE),          # Table rows
                re.compile(r'\s*>\s*', re.MULTILINE),         # Blockquotes
            ],
            'python': [
                re.compile(r'def\s+', re.MULTILINE),          # Functions
                re.compile(r'class\s+', re.MULTILINE),        # Classes
                re.compile(r'import\s+', re.MULTILINE),       # Imports
                re.compile(r'from\s+', re.MULTILINE),         # From imports
                re.compile(r'async\s+def\s+', re.MULTILINE),  # Async functions
                re.compile(r'@\w+', re.MULTILINE),            # Decorators
                re.compile(r'\s*if\s+', re.MULTILINE),        # If statements
                re.compile(r'\s*for\s+', re.MULTILINE),       # For loops
                re.compile(r'\s*while\s+', re.MULTILINE),     # While loops
                re.compile(r'\s*try\s*:', re.MULTILINE),      # Try blocks
                re.compile(r'\s*except\s+', re.MULTILINE),    # Except blocks
                re.compile(r'\s*finally\s*:', re.MULTILINE),  # Finally blocks
                re.compile(r'\s*with\s+', re.MULTILINE),      # With statements
                re.compile(r'\s*yield\s+', re.MULTILINE),     # Yield statements
                re.compile(r'\s*return\s+', re.MULTILINE),    # Return statements
            ],
            'log': [
                re.compile(r'\d{4}-\d{2}-\d{2}', re.MULTILINE),           # Date patterns
                re.compile(r'\d{2}:\d{2}:\d{2}', re.MULTILINE),            # Time patterns
                re.compile(r'ERROR|WARN|INFO|DEBUG|FATAL', re.MULTILINE),   # Log levels
                re.compile(r'\[.*?\]', re.MULTILINE),                       # Bracket content
                re.compile(r'\{.*?\}', re.MULTILINE),                       # Brace content
            ],
            'text': [
                re.compile(r'\n\s*\n', re.MULTILINE),                       # Paragraphs
                re.compile(r'[.!?]\s+[A-Z]', re.MULTILINE),                # Sentences
                re.compile(r'\b\w{10,}\b', re.MULTILINE),                   # Long words
                re.compile(r'[A-Z][a-z]+', re.MULTILINE),                   # Capitalized words
                re.compile(r'\d+', re.MULTILINE),                           # Numbers
            ]
        }
        
        logger.info("Regex patterns pre-compiled for maximum performance")
    
    def process_file_optimized(self, file_path):
        """Process file using optimized I/O operations."""
        try:
            if not os.path.exists(file_path):
                return {'file_path': str(file_path), 'error': 'File not found', 'type': 'error'}
            
            # OPTIMIZATION 1: Memory-mapped file reading
            result = self._process_with_memory_mapping(file_path)
            
            # Update global stats safely
            with self.lock:
                self.processed_files += 1
                self.total_content_size += result.get('content_size', 0)
                self.content_stats[result['file_type']] += 1
            
            return result
            
        except Exception as e:
            return {'file_path': str(file_path), 'error': str(e), 'type': 'error'}
    
    def _process_with_memory_mapping(self, file_path):
        """Process file using memory mapping for optimal I/O performance."""
        file_size = os.path.getsize(file_path)
        
        # OPTIMIZATION 2: Handle different file sizes optimally
        if file_size < 1024:  # Small files: read directly
            return self._process_small_file(file_path)
        elif file_size < 1024 * 1024:  # Medium files: memory mapping
            return self._process_medium_file(file_path)
        else:  # Large files: streaming with chunks
            return self._process_large_file(file_path)
    
    def _process_small_file(self, file_path):
        """Process small files with direct reading."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return self._analyze_content_optimized(content, file_path)
    
    def _process_medium_file(self, file_path):
        """Process medium files with memory mapping."""
        with open(file_path, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                # OPTIMIZATION 3: Decode only what we need
                try:
                    content = mm.decode('utf-8', errors='ignore')
                except UnicodeDecodeError:
                    # Fallback to binary processing
                    content = mm.decode('latin-1', errors='ignore')
        
        return self._analyze_content_optimized(content, file_path)
    
    def _process_large_file(self, file_path):
        """Process large files with streaming chunks."""
        file_type = self._detect_file_type(file_path)
        stats = {'lines': 0, 'words': 0, 'code_blocks': 0, 'markdown_elements': 0}
        
        # OPTIMIZATION 4: Stream processing for large files
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f):
                stats['lines'] += 1
                stats['words'] += len(line.split())
                
                # Process line for patterns (only if needed)
                if file_type in self.patterns:
                    for pattern in self.patterns[file_type]:
                        if pattern.search(line):
                            if file_type == 'markdown':
                                stats['markdown_elements'] += 1
                            else:
                                stats['code_blocks'] += 1
                
                # OPTIMIZATION 5: Early termination for very large files
                if line_num > 100000:  # Limit processing for extremely large files
                    break
        
        # Calculate content hash efficiently
        content_hash = self._calculate_efficient_hash(file_path)
        
        return {
            'file_path': str(file_path),
            'file_type': file_type,
            'word_count': stats['words'],
            'line_count': stats['lines'],
            'code_blocks': stats['code_blocks'],
            'markdown_elements': stats['markdown_elements'],
            'content_size': os.path.getsize(file_path),
            'content_hash': content_hash,
            'type': 'processed',
            'processing_mode': 'streaming'
        }
    
    def _detect_file_type(self, file_path):
        """Efficiently detect file type from extension."""
        ext = file_path.lower().split('.')[-1]
        if ext in ['md', 'markdown']:
            return 'markdown'
        elif ext == 'py':
            return 'python'
        elif ext == 'json':
            return 'json'
        elif ext in ['log', 'txt']:
            return 'log' if ext == 'log' else 'text'
        else:
            return 'unknown'
    
    def _calculate_efficient_hash(self, file_path):
        """Calculate hash efficiently without loading entire file."""
        try:
            # OPTIMIZATION 6: Sample-based hashing for large files
            file_size = os.path.getsize(file_path)
            if file_size < 1024 * 1024:  # < 1MB: hash entire file
                with open(file_path, 'rb') as f:
                    return hashlib.md5(f.read()).hexdigest()[:8]
            else:  # >= 1MB: hash samples
                sample_size = min(1024 * 1024, file_size // 10)  # 1MB or 10% of file
                with open(file_path, 'rb') as f:
                    # Hash beginning, middle, and end
                    beginning = f.read(sample_size)
                    f.seek(file_size // 2)
                    middle = f.read(sample_size)
                    f.seek(-sample_size, 2)
                    end = f.read(sample_size)
                    
                    combined = beginning + middle + end
                    return hashlib.md5(combined).hexdigest()[:8]
        except Exception:
            return '00000000'
    
    def _analyze_content_optimized(self, content, file_path):
        """Analyze content using pre-compiled patterns for maximum speed."""
        file_type = self._detect_file_type(file_path)
        
        # OPTIMIZATION 7: Efficient content analysis
        lines = content.split('\n')
        line_count = len(lines)
        word_count = len(content.split())
        
        # Use pre-compiled patterns for faster matching
        code_blocks = 0
        markdown_elements = 0
        
        if file_type in self.patterns:
            for pattern in self.patterns[file_type]:
                matches = len(pattern.findall(content))
                if file_type == 'markdown':
                    markdown_elements += matches
                else:
                    code_blocks += matches
        
        # OPTIMIZATION 8: Efficient hash calculation
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        
        # OPTIMIZATION 9: GPU processing only for suitable content
        gpu_result = 0
        if self.gpu_available and len(content) > 100 and len(content) < 10000:
            try:
                # Convert content to tensor efficiently
                content_tensor = torch.tensor([ord(c) for c in content[:1000]], 
                                           device=self.device, dtype=torch.float32)
                # Perform GPU operations
                gpu_result = torch.sum(content_tensor).item()
                gpu_result += torch.std(content_tensor).item()
                gpu_result += torch.mean(content_tensor).item()
            except Exception:
                gpu_result = 0
        
        return {
            'file_path': str(file_path),
            'file_type': file_type,
            'word_count': word_count,
            'line_count': line_count,
            'code_blocks': code_blocks,
            'markdown_elements': markdown_elements,
            'content_size': len(content),
            'content_hash': content_hash,
            'gpu_result': gpu_result,
            'type': 'processed',
            'processing_mode': 'memory_mapped'
        }

class OptimizedIOParallelProcessor:
    """Parallel processor with I/O optimizations."""
    
    def __init__(self, max_workers=None):
        # OPTIMIZATION 10: Optimal worker count based on I/O characteristics
        self.max_workers = max_workers or min(24, (os.cpu_count() or 1) + 8)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        self.processor = OptimizedIOProcessor()
        
        logger.info("OptimizedIOParallelProcessor initialized with {} workers".format(self.max_workers))
    
    def process_files_optimized(self, file_paths, batch_size=1000):
        """Process files with I/O optimizations."""
        logger.info("I/O OPTIMIZED processing of {} files with {} workers (batch size: {})".format(
            len(file_paths), self.max_workers, batch_size))
        
        start_time = time.time()
        all_results = []
        
        # OPTIMIZATION 11: Larger batches for I/O efficiency
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i+batch_size]
            batch_results = self._process_batch_optimized(batch)
            all_results.extend(batch_results)
            
            # Progress update
            if (i + batch_size) % 5000 == 0 or (i + batch_size) >= len(file_paths):
                logger.info("Processed {}/{} files...".format(min(i + batch_size, len(file_paths)), len(file_paths)))
        
        total_time = time.time() - start_time
        speed = len(file_paths) / total_time
        
        logger.info("I/O OPTIMIZED processing completed: {} files in {:.3f}s ({:.0f} files/sec)".format(
            len(file_paths), total_time, speed))
        
        return all_results, total_time, speed
    
    def _process_batch_optimized(self, file_paths):
        """Process a batch with I/O optimizations."""
        futures = []
        
        # Submit all files in batch to thread pool
        for file_path in file_paths:
            future = self.executor.submit(self.processor.process_file_optimized, file_path)
            futures.append(future)
        
        # Collect results with optimized timeout
        results = []
        for future in concurrent.futures.as_completed(futures, timeout=900):  # 15 minute timeout
            try:
                result = future.result(timeout=45)  # 45 second timeout per result
                results.append(result)
            except Exception as e:
                logger.error("Optimized batch processing error: {}".format(e))
                results.append({'error': str(e), 'type': 'timeout'})
        
        return results
    
    def shutdown(self):
        """Shutdown the processor."""
        self.executor.shutdown(wait=True)
        logger.info("OptimizedIOParallelProcessor shutdown complete")

class IOOptimizationTestEngine:
    """Test engine for I/O optimization phase."""
    
    def __init__(self):
        self.processor = OptimizedIOParallelProcessor()
        self.baseline_speed = 462  # files/sec from real data test
        self.target_speed = 10000  # 10K files/sec target for this phase
        
        logger.info("IOOptimizationTestEngine initialized")
    
    def collect_real_data_files(self, max_files=100000):
        """Collect REAL data files for testing."""
        logger.info("Collecting REAL data files for I/O optimization testing...")
        
        real_files = []
        search_paths = [
            "archive/testing_artifacts/Universal Open Science Toolbox With Kai (The Real Test)",
            "archive/obsolete_md_files/Cleanup - Old MD Files",
            "archive/testing_artifacts",
            "archive/obsolete_md_files"
        ]
        
        for search_path in search_paths:
            if os.path.exists(search_path):
                logger.info("Scanning: {}".format(search_path))
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if file.endswith(('.md', '.py', '.json', '.log', '.txt', '.csv')):
                            file_path = os.path.join(root, file)
                            real_files.append(file_path)
                            
                            if len(real_files) >= max_files:
                                break
                    if len(real_files) >= max_files:
                        break
            if len(real_files) >= max_files:
                break
        
        logger.info("Collected {} REAL data files for I/O optimization testing".format(len(real_files)))
        return real_files
    
    def run_io_optimization_test(self, num_files=50000):
        """Run I/O optimization test."""
        logger.info("Starting I/O OPTIMIZATION test with {} files".format(num_files))
        
        # Collect real data files
        all_files = self.collect_real_data_files(num_files * 2)
        
        if len(all_files) < num_files:
            logger.warning("Only found {} real files, using all available".format(len(all_files)))
            test_files = all_files
        else:
            test_files = all_files[:num_files]
        
        logger.info("Using {} REAL files for I/O optimization testing".format(len(test_files)))
        
        try:
            start_time = time.time()
            
            # Process files with I/O optimizations
            results, processing_time, speed = self.processor.process_files_optimized(test_files)
            
            total_time = time.time() - start_time
            
            # Calculate improvement
            improvement = ((speed - self.baseline_speed) / self.baseline_speed) * 100
            
            # Generate comprehensive results
            test_results = {
                'timestamp': time.time(),
                'test_type': 'IO_OPTIMIZATION_PHASE_1',
                'files_processed': len(test_files),
                'processing_time_seconds': round(processing_time, 3),
                'total_time_seconds': round(total_time, 3),
                'speed_files_per_sec': round(speed, 2),
                'baseline_speed': self.baseline_speed,
                'improvement_percent': round(improvement, 2),
                'target_speed': self.target_speed,
                'target_achieved': speed >= self.target_speed,
                'phase_1_success': speed >= self.target_speed,
                'optimizations_applied': [
                    'Memory-mapped file I/O',
                    'Pre-compiled regex patterns',
                    'Streaming processing for large files',
                    'Efficient hash calculation',
                    'Optimized worker distribution',
                    'Batch I/O operations'
                ],
                'hardware_challenge': {
                    'workers_used': self.processor.max_workers,
                    'cpu_cores': os.cpu_count(),
                    'gpu_available': self.processor.processor.gpu_available,
                    'gpu_device': str(self.processor.processor.device) if self.processor.processor.gpu_available else 'CPU'
                },
                'content_analysis': {
                    'total_content_size_bytes': self.processor.processor.total_content_size,
                    'file_types_processed': dict(self.processor.processor.content_stats),
                    'average_file_size_bytes': round(self.processor.processor.total_content_size / len(test_files), 2) if test_files else 0
                },
                'performance_metrics': {
                    'files_per_second': round(speed, 2),
                    'megabytes_per_second': round((self.processor.processor.total_content_size / 1024 / 1024) / processing_time, 2),
                    'efficiency_score': round((speed / self.baseline_speed) * 100, 2),
                    'phase_1_target_achieved': speed >= self.target_speed
                }
            }
            
            logger.info("I/O OPTIMIZATION test completed successfully!")
            return test_results
            
        except Exception as e:
            logger.error("I/O OPTIMIZATION test failed: {}".format(e))
            return None
        
        finally:
            self.processor.shutdown()
    
    def save_results(self, results, filename="phase3_io_optimization_results.json"):
        """Save test results to JSON file."""
        output_dir = Path("ops/test_output/phase3_performance")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / filename
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info("I/O OPTIMIZATION test results saved to: {}".format(output_file))
        return output_file
    
    def print_summary(self, results):
        """Print comprehensive test summary."""
        print("\n" + "="*80)
        print("PHASE 3 I/O OPTIMIZATION TEST RESULTS")
        print("="*80)
        
        print("TEST TYPE: I/O OPTIMIZATION PHASE 1")
        print("FILES PROCESSED: {} REAL files".format(results['files_processed']))
        print("PROCESSING TIME: {:.3f} seconds".format(results['processing_time_seconds']))
        print("TOTAL TIME: {:.3f} seconds".format(results['total_time_seconds']))
        print("SPEED: {:.0f} files/sec".format(results['speed_files_per_sec']))
        print("BASELINE: {:.0f} files/sec".format(results['baseline_speed']))
        print("IMPROVEMENT: {:.1f}%".format(results['improvement_percent']))
        print("TARGET: {:.0f} files/sec".format(results['target_speed']))
        print("TARGET ACHIEVED: {}".format("YES" if results['target_achieved'] else "NO"))
        
        print("\nPHASE 1 STATUS:")
        print("Phase 1 Success: {}".format("YES" if results['phase_1_success'] else "NO"))
        print("Ready for Phase 2: {}".format("YES" if results['phase_1_success'] else "NO"))
        
        print("\nOPTIMIZATIONS APPLIED:")
        for opt in results['optimizations_applied']:
            print("- {}".format(opt))
        
        print("\nHARDWARE CHALLENGE:")
        print("Workers Used: {}".format(results['hardware_challenge']['workers_used']))
        print("CPU Cores: {}".format(results['hardware_challenge']['cpu_cores']))
        print("GPU Available: {}".format(results['hardware_challenge']['gpu_available']))
        print("GPU Device: {}".format(results['hardware_challenge']['gpu_device']))
        
        print("\nCONTENT ANALYSIS:")
        print("Total Content Size: {:.2f} MB".format(results['content_analysis']['total_content_size_bytes'] / 1024 / 1024))
        print("Average File Size: {:.2f} KB".format(results['content_analysis']['average_file_size_bytes'] / 1024))
        print("File Types: {}".format(dict(results['content_analysis']['file_types_processed'])))
        
        print("\nPERFORMANCE METRICS:")
        print("Files/Second: {:.0f}".format(results['performance_metrics']['files_per_second']))
        print("MB/Second: {:.2f}".format(results['performance_metrics']['megabytes_per_second']))
        print("Efficiency Score: {:.1f}%".format(results['performance_metrics']['efficiency_score']))
        print("Phase 1 Target: {}".format("ACHIEVED" if results['performance_metrics']['phase_1_target_achieved'] else "NOT ACHIEVED"))
        
        print("="*80)

def main():
    """Main execution function."""
    print("PHASE 3 I/O OPTIMIZATION ENGINE")
    print("="*80)
    print("Phase 1: I/O Optimization Implementation")
    print("Target: 10K+ files/sec (20x improvement over current 462 files/sec)")
    print("="*80)
    
    # Create I/O optimization test engine
    engine = IOOptimizationTestEngine()
    
    # Run I/O optimization test with 50K files
    print("Starting I/O OPTIMIZATION test with 50,000 files...")
    print("Applying memory mapping, streaming, and batch I/O optimizations...")
    
    results = engine.run_io_optimization_test(num_files=50000)
    
    if results:
        # Save results
        output_file = engine.save_results(results)
        
        # Print comprehensive summary
        engine.print_summary(results)
        
        print("\nI/O OPTIMIZATION test completed successfully!")
        print("Results saved to: {}".format(output_file))
        
        if results['phase_1_success']:
            print(" PHASE 1 TARGET ACHIEVED: 10K+ files/sec!")
            print(" Ready for Phase 2: Content Analysis Optimization")
        else:
            print(" Performance: {:.0f} files/sec (need {:.0f} more for Phase 1 target)".format(
                results['speed_files_per_sec'], 
                results['target_speed'] - results['speed_files_per_sec']))
            print(" Phase 1 needs more optimization before Phase 2")
        
        print("Next Phase: Content Analysis Optimization")
        
    else:
        print("\nI/O OPTIMIZATION test failed!")
        print("Please check the logs for details.")

if __name__ == "__main__":
    main()
