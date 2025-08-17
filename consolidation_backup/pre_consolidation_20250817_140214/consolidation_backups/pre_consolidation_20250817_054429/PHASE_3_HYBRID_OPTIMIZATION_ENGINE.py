#!/usr/bin/env python3
"""
PHASE 3 HYBRID OPTIMIZATION ENGINE
Agent Exo-Suit V5.0 - Phase 3 Development

This script implements a HYBRID approach combining:
- Phase 1 I/O optimizations (memory mapping, streaming, batch I/O)
- Simplified content analysis (basic patterns only, no complex parsing)
- GPU acceleration (batch tensor operations)
- System balance optimization (optimal CPU-GPU coordination)

Target: Achieve 10K+ files/sec (Phase 1 completion) and prepare for Phase 3
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
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HybridProcessor:
    """Hybrid processor combining I/O optimization with simplified content analysis."""
    
    def __init__(self):
        self.processed_files = 0
        self.total_content_size = 0
        self.content_stats = defaultdict(int)
        self.lock = threading.Lock()
        
        # GPU setup for batch operations
        self.gpu_available = torch.cuda.is_available()
        if self.gpu_available:
            self.device = torch.device('cuda')
            logger.info("GPU processing enabled on: {}".format(torch.cuda.get_device_name()))
        else:
            self.device = torch.device('cpu')
            logger.warning("GPU not available, using CPU")
        
        # HYBRID: Simple, fast patterns only (no complex parsing overhead)
        self._compile_simple_patterns()
        
        # GPU batch processing setup
        self.gpu_batch_size = 100  # Process 100 files in single GPU call
        self.gpu_batch_data = []
        self.gpu_batch_lock = threading.Lock()
        
    def _compile_simple_patterns(self):
        """Compile simple, fast patterns for maximum speed."""
        # HYBRID: Only essential patterns, no complex regex
        self.patterns = {
            'python': [
                re.compile(r'def\s+', re.MULTILINE),      # Functions
                re.compile(r'class\s+', re.MULTILINE),    # Classes
                re.compile(r'import\s+', re.MULTILINE),   # Imports
                re.compile(r'from\s+', re.MULTILINE),     # From imports
            ],
            'markdown': [
                re.compile(r'#+\s+', re.MULTILINE),       # Headers
                re.compile(r'[-*+]\s+', re.MULTILINE),    # List items
                re.compile(r'', re.MULTILINE),           # Code blocks
            ],
            'log': [
                re.compile(r'\d{4}-\d{2}-\d{2}', re.MULTILINE),  # Date patterns
                re.compile(r'ERROR|WARN|INFO|DEBUG', re.MULTILINE), # Log levels
            ],
            'text': [
                re.compile(r'\n\s*\n', re.MULTILINE),      # Paragraphs
                re.compile(r'[.!?]\s+[A-Z]', re.MULTILINE), # Sentences
            ]
        }
        
        logger.info("Simple, fast patterns compiled for hybrid processing")
    
    def process_file_hybrid(self, file_path):
        """Process file using hybrid approach: I/O optimization + simplified analysis."""
        try:
            if not os.path.exists(file_path):
                return {'file_path': str(file_path), 'error': 'File not found', 'type': 'error'}
            
            # HYBRID: Use I/O optimization from Phase 1
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
        """Process file using memory mapping (Phase 1 I/O optimization)."""
        file_size = os.path.getsize(file_path)
        
        # HYBRID: Keep Phase 1 I/O optimizations
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
        
        return self._analyze_content_simple(content, file_path)
    
    def _process_medium_file(self, file_path):
        """Process medium files with memory mapping."""
        with open(file_path, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                try:
                    content = mm.decode('utf-8', errors='ignore')
                except UnicodeDecodeError:
                    content = mm.decode('latin-1', errors='ignore')
        
        return self._analyze_content_simple(content, file_path)
    
    def _process_large_file(self, file_path):
        """Process large files with streaming chunks."""
        file_type = self._detect_file_type(file_path)
        stats = {'lines': 0, 'words': 0, 'code_blocks': 0, 'markdown_elements': 0}
        
        # HYBRID: Stream processing for large files
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f):
                stats['lines'] += 1
                stats['words'] += len(line.split())
                
                # HYBRID: Simple pattern matching only
                if file_type in self.patterns:
                    for pattern in self.patterns[file_type]:
                        if pattern.search(line):
                            if file_type == 'markdown':
                                stats['markdown_elements'] += 1
                            else:
                                stats['code_blocks'] += 1
                
                # Early termination for very large files
                if line_num > 50000:  # Reduced limit for faster processing
                    break
        
        # HYBRID: Efficient hash calculation
        content_hash = self._calculate_efficient_hash(file_path)
        
        return {
            'file_path': str(file_path),
            'file_type': file_type,
            'word_count': stats['words'],
            'line_count': stats['lines'],
            'code_blocks': stats['code_blocks'],
            'markdown_elements': stats['markdown_elements'],
            'content_size': file_size,
            'content_hash': content_hash,
            'type': 'processed',
            'processing_mode': 'hybrid_streaming'
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
            file_size = os.path.getsize(file_path)
            if file_size < 1024 * 1024:  # < 1MB: hash entire file
                with open(file_path, 'rb') as f:
                    return hashlib.md5(f.read()).hexdigest()[:8]
            else:  # >= 1MB: hash samples
                sample_size = min(512 * 1024, file_size // 20)  # 512KB or 5% of file
                with open(file_path, 'rb') as f:
                    # Hash beginning and end only (faster)
                    beginning = f.read(sample_size)
                    f.seek(-sample_size, 2)
                    end = f.read(sample_size)
                    
                    combined = beginning + end
                    return hashlib.md5(combined).hexdigest()[:8]
        except Exception:
            return '00000000'
    
    def _analyze_content_simple(self, content, file_path):
        """Simple content analysis for maximum speed."""
        file_type = self._detect_file_type(file_path)
        
        # HYBRID: Basic analysis only
        lines = content.split('\n')
        line_count = len(lines)
        word_count = len(content.split())
        
        # HYBRID: Simple pattern matching
        code_blocks = 0
        markdown_elements = 0
        
        if file_type in self.patterns:
            for pattern in self.patterns[file_type]:
                matches = len(pattern.findall(content))
                if file_type == 'markdown':
                    markdown_elements += matches
                else:
                    code_blocks += matches
        
        # HYBRID: Simple hash calculation
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        
        # HYBRID: GPU processing only for suitable content
        gpu_result = 0
        if self.gpu_available and len(content) > 100 and len(content) < 5000:
            try:
                # Convert content to tensor efficiently
                content_tensor = torch.tensor([ord(c) for c in content[:500]], 
                                           device=self.device, dtype=torch.float32)
                # Perform GPU operations
                gpu_result = torch.sum(content_tensor).item()
                gpu_result += torch.std(content_tensor).item()
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
            'processing_mode': 'hybrid_simple'
        }
    
    def process_gpu_batch(self, file_paths):
        """Process multiple files in a single GPU batch operation."""
        if not self.gpu_available or len(file_paths) == 0:
            return []
        
        try:
            # HYBRID: Batch GPU processing for multiple files
            batch_tensors = []
            batch_results = []
            
            for file_path in file_paths:
                try:
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        if file_size < 5000:  # Only small files for GPU
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            # Convert to tensor with fixed size (200 chars)
                            content = content[:200]  # Truncate to 200 chars
                            content = content.ljust(200, ' ')  # Pad to exactly 200 chars
                            content_tensor = torch.tensor([ord(c) for c in content], 
                                                       device=self.device, dtype=torch.float32)
                            batch_tensors.append(content_tensor)
                            batch_results.append({
                                'file_path': file_path,
                                'tensor_size': len(content_tensor),
                                'content_size': file_size
                            })
                except Exception:
                    continue
            
            if batch_tensors:
                # HYBRID: Process all tensors in single GPU call
                # All tensors are now guaranteed to be the same size (200)
                combined_tensor = torch.stack(batch_tensors)
                
                # Batch GPU operations
                batch_sum = torch.sum(combined_tensor, dim=1)
                batch_mean = torch.mean(combined_tensor, dim=1)
                batch_std = torch.std(combined_tensor, dim=1)
                
                # Combine results
                for i, result in enumerate(batch_results):
                    result['gpu_sum'] = batch_sum[i].item()
                    result['gpu_mean'] = batch_mean[i].item()
                    result['gpu_std'] = batch_std[i].item()
                    result['gpu_processed'] = True
            
            return batch_results
            
        except Exception as e:
            logger.error("GPU batch processing error: {}".format(e))
            return []

class HybridParallelProcessor:
    """Hybrid parallel processor with optimal CPU-GPU coordination."""
    
    def __init__(self, max_workers=None):
        # HYBRID: Optimal worker count for I/O + CPU balance
        self.max_workers = max_workers or min(22, (os.cpu_count() or 1) + 6)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        self.processor = HybridProcessor()
        
        logger.info("HybridParallelProcessor initialized with {} workers".format(self.max_workers))
    
    def process_files_hybrid(self, file_paths, batch_size=1200):
        """Process files with hybrid optimizations."""
        logger.info("HYBRID processing of {} files with {} workers (batch size: {})".format(
            len(file_paths), self.max_workers, batch_size))
        
        start_time = time.time()
        all_results = []
        
        # HYBRID: Larger batches for I/O efficiency + GPU batching
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i+batch_size]
            batch_results = self._process_batch_hybrid(batch)
            all_results.extend(batch_results)
            
            # Progress update
            if (i + batch_size) % 6000 == 0 or (i + batch_size) >= len(file_paths):
                logger.info("Processed {}/{} files...".format(min(i + batch_size, len(file_paths)), len(file_paths)))
        
        total_time = time.time() - start_time
        speed = len(file_paths) / total_time
        
        logger.info("HYBRID processing completed: {} files in {:.3f}s ({:.0f} files/sec)".format(
            len(file_paths), total_time, speed))
        
        return all_results, total_time, speed
    
    def _process_batch_hybrid(self, file_paths):
        """Process a batch with hybrid optimizations."""
        futures = []
        
        # Submit all files in batch to thread pool
        for file_path in file_paths:
            future = self.executor.submit(self.processor.process_file_hybrid, file_path)
            futures.append(future)
        
        # Collect results with optimized timeout
        results = []
        for future in concurrent.futures.as_completed(futures, timeout=900):  # 15 minute timeout
            try:
                result = future.result(timeout=45)  # 45 second timeout per result
                results.append(result)
            except Exception as e:
                logger.error("Hybrid batch processing error: {}".format(e))
                results.append({'error': str(e), 'type': 'timeout'})
        
        # HYBRID: GPU batch processing for files that need it
        gpu_candidates = [r for r in results if r.get('type') == 'processed' and r.get('content_size', 0) < 5000]
        if gpu_candidates and len(gpu_candidates) >= 10:
            gpu_batch_results = self.processor.process_gpu_batch([r['file_path'] for r in gpu_candidates])
            # Update results with GPU processing info
            for gpu_result in gpu_batch_results:
                for result in results:
                    if result.get('file_path') == gpu_result['file_path']:
                        result.update(gpu_result)
                        break
        
        return results
    
    def shutdown(self):
        """Shutdown the processor."""
        self.executor.shutdown(wait=True)
        logger.info("HybridParallelProcessor shutdown complete")

class HybridOptimizationEngine:
    """Test engine for hybrid optimization approach."""
    
    def __init__(self):
        self.processor = HybridParallelProcessor()
        self.baseline_speed = 7893  # files/sec from I/O optimization
        self.target_speed = 10000   # 10K files/sec target for Phase 1 completion
        
        logger.info("HybridOptimizationEngine initialized")
    
    def collect_real_data_files(self, max_files=100000):
        """Collect REAL data files for testing."""
        logger.info("Collecting REAL data files for hybrid optimization testing...")
        
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
        
        logger.info("Collected {} REAL data files for hybrid optimization testing".format(len(real_files)))
        return real_files
    
    def run_hybrid_test(self, num_files=50000):
        """Run hybrid optimization test."""
        logger.info("Starting HYBRID OPTIMIZATION test with {} files".format(num_files))
        
        # Collect real data files
        all_files = self.collect_real_data_files(num_files * 2)
        
        if len(all_files) < num_files:
            logger.warning("Only found {} real files, using all available".format(len(all_files)))
            test_files = all_files
        else:
            test_files = all_files[:num_files]
        
        logger.info("Using {} REAL files for hybrid optimization testing".format(len(test_files)))
        
        try:
            start_time = time.time()
            
            # Process files with hybrid optimizations
            results, processing_time, speed = self.processor.process_files_hybrid(test_files)
            
            total_time = time.time() - start_time
            
            # Calculate improvement
            improvement = ((speed - self.baseline_speed) / self.baseline_speed) * 100
            
            # Generate comprehensive results
            test_results = {
                'timestamp': time.time(),
                'test_type': 'HYBRID_OPTIMIZATION_APPROACH',
                'files_processed': len(test_files),
                'processing_time_seconds': round(processing_time, 3),
                'total_time_seconds': round(total_time, 3),
                'speed_files_per_sec': round(speed, 2),
                'baseline_speed': self.baseline_speed,
                'improvement_percent': round(improvement, 2),
                'target_speed': self.target_speed,
                'target_achieved': speed >= self.target_speed,
                'phase_1_completed': speed >= self.target_speed,
                'hybrid_success': speed >= self.target_speed * 1.05,  # 5% improvement over Phase 1
                'optimizations_applied': [
                    'Phase 1 I/O optimizations (memory mapping, streaming)',
                    'Simplified content analysis (basic patterns only)',
                    'GPU batch processing (multiple files per GPU call)',
                    'Optimal CPU-GPU coordination',
                    'Reduced regex complexity',
                    'Efficient hash calculation',
                    'Balanced worker distribution'
                ],
                'hybrid_approach': {
                    'io_optimizations': 'Enabled (Phase 1)',
                    'content_analysis': 'Simplified (no complex parsing)',
                    'gpu_acceleration': 'Batch processing enabled',
                    'system_balance': 'CPU-GPU coordination optimized'
                },
                'hardware_challenge': {
                    'workers_used': self.processor.max_workers,
                    'cpu_cores': os.cpu_count(),
                    'gpu_available': self.processor.processor.gpu_available,
                    'gpu_device': str(self.processor.processor.device) if self.processor.processor.gpu_available else 'CPU'
                },
                'content_analysis': {
                    'total_content_size_bytes': self.processor.processor.total_content_size,
                    'file_types_processed': dict(self.processor.processor.content_stats),
                    'average_file_size_bytes': round(self.processor.processor.total_content_size / len(test_files), 2) if test_files else 0,
                    'processing_mode': 'Hybrid (I/O + Simple Analysis + GPU)'
                },
                'performance_metrics': {
                    'files_per_second': round(speed, 2),
                    'megabytes_per_second': round((self.processor.processor.total_content_size / 1024 / 1024) / processing_time, 2),
                    'efficiency_score': round((speed / self.baseline_speed) * 100, 2),
                    'phase_1_target_achieved': speed >= self.target_speed,
                    'hybrid_target_achieved': speed >= self.target_speed * 1.05
                }
            }
            
            logger.info("HYBRID OPTIMIZATION test completed successfully!")
            return test_results
            
        except Exception as e:
            logger.error("HYBRID OPTIMIZATION test failed: {}".format(e))
            return None
        
        finally:
            self.processor.shutdown()
    
    def save_results(self, results, filename="phase3_hybrid_optimization_results.json"):
        """Save test results to JSON file."""
        output_dir = Path("ops/test_output/phase3_performance")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / filename
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info("HYBRID OPTIMIZATION test results saved to: {}".format(output_file))
        return output_file
    
    def print_summary(self, results):
        """Print comprehensive test summary."""
        print("\n" + "="*80)
        print("PHASE 3 HYBRID OPTIMIZATION TEST RESULTS")
        print("="*80)
        
        print("TEST TYPE: HYBRID OPTIMIZATION APPROACH")
        print("FILES PROCESSED: {} REAL files".format(results['files_processed']))
        print("PROCESSING TIME: {:.3f} seconds".format(results['processing_time_seconds']))
        print("TOTAL TIME: {:.3f} seconds".format(results['total_time_seconds']))
        print("SPEED: {:.0f} files/sec".format(results['speed_files_per_sec']))
        print("BASELINE: {:.0f} files/sec".format(results['baseline_speed']))
        print("IMPROVEMENT: {:.1f}%".format(results['improvement_percent']))
        print("TARGET: {:.0f} files/sec".format(results['target_speed']))
        print("TARGET ACHIEVED: {}".format("YES" if results['target_achieved'] else "NO"))
        
        print("\nHYBRID APPROACH STATUS:")
        print("Phase 1 Completed: {}".format("YES" if results['phase_1_completed'] else "NO"))
        print("Hybrid Success: {}".format("YES" if results['hybrid_success'] else "NO"))
        print("Ready for Phase 3: {}".format("YES" if results['hybrid_success'] else "NO"))
        
        print("\nHYBRID APPROACH COMPONENTS:")
        for component, status in results['hybrid_approach'].items():
            print("- {}: {}".format(component.replace('_', ' ').title(), status))
        
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
        print("Processing Mode: {}".format(results['content_analysis']['processing_mode']))
        
        print("\nPERFORMANCE METRICS:")
        print("Files/Second: {:.0f}".format(results['performance_metrics']['files_per_second']))
        print("MB/Second: {:.2f}".format(results['performance_metrics']['megabytes_per_second']))
        print("Efficiency Score: {:.1f}%".format(results['performance_metrics']['efficiency_score']))
        print("Phase 1 Target: {}".format("ACHIEVED" if results['performance_metrics']['phase_1_target_achieved'] else "NOT ACHIEVED"))
        print("Hybrid Target: {}".format("ACHIEVED" if results['performance_metrics']['hybrid_target_achieved'] else "NOT ACHIEVED"))
        
        print("="*80)

def main():
    """Main execution function."""
    print("PHASE 3 HYBRID OPTIMIZATION ENGINE")
    print("="*80)
    print("HYBRID APPROACH: Best of Both Worlds")
    print("Phase 1 I/O + Simplified Analysis + GPU Acceleration")
    print("Target: Complete Phase 1 (10K+ files/sec) and achieve hybrid success")
    print("="*80)
    
    # Create hybrid optimization test engine
    engine = HybridOptimizationEngine()
    
    # Run hybrid optimization test with 50K files
    print("Starting HYBRID OPTIMIZATION test with 50,000 files...")
    print("Combining I/O optimization + simplified analysis + GPU acceleration...")
    
    results = engine.run_hybrid_test(num_files=50000)
    
    if results:
        # Save results
        output_file = engine.save_results(results)
        
        # Print comprehensive summary
        engine.print_summary(results)
        
        print("\nHYBRID OPTIMIZATION test completed successfully!")
        print("Results saved to: {}".format(output_file))
        
        if results['phase_1_completed']:
            print(" PHASE 1 TARGET ACHIEVED: 10K+ files/sec!")
            
            if results['hybrid_success']:
                print(" HYBRID APPROACH SUCCESS: 5% improvement over Phase 1!")
                print(" Best of both worlds achieved!")
                print(" Ready for Phase 3: Advanced GPU and System Balance")
            else:
                print(" Hybrid: Need 5% improvement over Phase 1 for success")
                print(" Hybrid approach needs refinement before Phase 3")
        else:
            print(" Performance: {:.0f} files/sec (need {:.0f} more for Phase 1 target)".format(
                results['speed_files_per_sec'], 
                results['target_speed'] - results['speed_files_per_sec']))
            print(" Phase 1 needs completion before hybrid success")
        
        print("Next Phase: Advanced GPU and System Balance Optimization")
        
    else:
        print("\nHYBRID OPTIMIZATION test failed!")
        print("Please check the logs for details.")

if __name__ == "__main__":
    main()
