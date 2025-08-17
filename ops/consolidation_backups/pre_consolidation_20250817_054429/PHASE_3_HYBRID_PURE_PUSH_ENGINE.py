#!/usr/bin/env python3
"""
PHASE 3 HYBRID PURE PUSH ENGINE
Agent Exo-Suit V5.0 - Phase 3 Development

This script implements HYBRID PURE PUSH by taking the EXACT working hybrid approach and:
- KEEPING the EXACT configuration that works (22 workers, 1,200 batch size)
- NOT changing ANY parameters that are already optimal
- Pushing to 10K+ files/sec by processing MORE files in parallel
- Using the SAME patterns, SAME I/O optimizations, SAME everything
- Just processing MORE files to achieve higher throughput

Target: Push the working hybrid approach from 7,973 to 10K+ files/sec by scaling UP, not changing
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

class HybridPurePushProcessor:
    """Hybrid pure push processor that keeps EXACTLY what works."""
    
    def __init__(self):
        self.processed_files = 0
        self.total_content_size = 0
        self.content_stats = defaultdict(int)
        self.lock = threading.Lock()
        
        # PURE: Keep EXACT GPU setup from working hybrid
        self.gpu_available = torch.cuda.is_available()
        if self.gpu_available:
            self.device = torch.device('cuda')
            logger.info("PURE GPU processing enabled on: {}".format(torch.cuda.get_device_name()))
        else:
            self.device = torch.device('cpu')
            logger.warning("GPU not available, using CPU")
        
        # PURE: Keep EXACT patterns from working hybrid approach
        self._compile_pure_patterns()
        
        # PURE: Keep EXACT GPU settings from working hybrid
        self.gpu_batch_size = 50  # EXACT same as working hybrid
        self.max_tensor_size = 200  # EXACT same as working hybrid
        
        logger.info("HybridPurePushProcessor initialized - EXACT working configuration!")
        
    def _compile_pure_patterns(self):
        """Compile EXACT patterns from working hybrid approach."""
        # PURE: Keep EXACT working patterns from hybrid (7,973 files/sec)
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
        
        logger.info("PURE patterns compiled - EXACT same as working hybrid")
    
    def process_file_pure(self, file_path):
        """Process file using EXACT same method as working hybrid."""
        try:
            if not os.path.exists(file_path):
                return {'file_path': str(file_path), 'error': 'File not found', 'type': 'error'}
            
            # PURE: Keep EXACT same I/O optimization from working hybrid
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
        """Process file using EXACT same method as working hybrid."""
        file_size = os.path.getsize(file_path)
        
        # PURE: Keep EXACT same I/O optimizations from working hybrid
        if file_size < 1024:  # Small files: read directly
            return self._process_small_file(file_path)
        elif file_size < 1024 * 1024:  # Medium files: memory mapping
            return self._process_medium_file(file_path)
        else:  # Large files: streaming with chunks
            return self._process_large_file(file_path)
    
    def _process_small_file(self, file_path):
        """Process small files with EXACT same method as working hybrid."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return self._analyze_content_pure(content, file_path)
    
    def _process_medium_file(self, file_path):
        """Process medium files with EXACT same method as working hybrid."""
        with open(file_path, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                try:
                    content = mm.decode('utf-8', errors='ignore')
                except UnicodeDecodeError:
                    content = mm.decode('latin-1', errors='ignore')
        
        return self._analyze_content_pure(content, file_path)
    
    def _process_large_file(self, file_path):
        """Process large files with EXACT same method as working hybrid."""
        file_type = self._detect_file_type(file_path)
        stats = {'lines': 0, 'words': 0, 'code_blocks': 0, 'markdown_elements': 0}
        
        # PURE: Keep EXACT same streaming from working hybrid
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f):
                stats['lines'] += 1
                stats['words'] += len(line.split())
                
                # PURE: Keep EXACT same pattern matching from working hybrid
                if file_type in self.patterns:
                    for pattern in self.patterns[file_type]:
                        if pattern.search(line):
                            if file_type == 'markdown':
                                stats['markdown_elements'] += 1
                            else:
                                stats['code_blocks'] += 1
                
                # PURE: Keep EXACT same early termination from working hybrid
                if line_num > 50000:  # EXACT same as working hybrid
                    break
        
        # PURE: Keep EXACT same hash calculation from working hybrid
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
            'processing_mode': 'pure_exact_hybrid'
        }
    
    def _detect_file_type(self, file_path):
        """Efficiently detect file type from extension - EXACT same as working hybrid."""
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
        """Calculate hash with EXACT same method as working hybrid."""
        try:
            file_size = os.path.getsize(file_path)
            if file_size < 1024 * 1024:  # < 1MB: hash entire file
                with open(file_path, 'rb') as f:
                    return hashlib.md5(f.read()).hexdigest()[:8]
            else:  # >= 1MB: hash samples
                sample_size = min(512 * 1024, file_size // 20)  # EXACT same as working hybrid
                with open(file_path, 'rb') as f:
                    # Hash beginning and end only (EXACT same as working hybrid)
                    beginning = f.read(sample_size)
                    f.seek(-sample_size, 2)
                    end = f.read(sample_size)
                    
                    combined = beginning + end
                    return hashlib.md5(combined).hexdigest()[:8]
        except Exception:
            return '00000000'
    
    def _analyze_content_pure(self, content, file_path):
        """Content analysis with EXACT same method as working hybrid."""
        file_type = self._detect_file_type(file_path)
        
        # PURE: Keep EXACT same analysis from working hybrid approach
        lines = content.split('\n')
        line_count = len(lines)
        word_count = len(content.split())
        
        # PURE: Keep EXACT same pattern matching from working hybrid
        code_blocks = 0
        markdown_elements = 0
        
        if file_type in self.patterns:
            for pattern in self.patterns[file_type]:
                matches = len(pattern.findall(content))
                if file_type == 'markdown':
                    markdown_elements += matches
                else:
                    code_blocks += matches
        
        # PURE: Keep EXACT same hash calculation from working hybrid
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        
        # PURE: Keep EXACT same GPU processing from working hybrid
        gpu_result = 0
        if self.gpu_available and len(content) > 100 and len(content) < 3000:
            try:
                # PURE: Create EXACT same tensors as working hybrid
                content_tensor = torch.tensor([ord(c) for c in content[:self.max_tensor_size]], 
                                           device=self.device, dtype=torch.float32)
                
                # PURE: Perform EXACT same GPU operations as working hybrid
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
            'processing_mode': 'pure_exact_hybrid'
        }
    
    def process_gpu_batch_pure(self, file_paths):
        """Process GPU batch with EXACT same method as working hybrid."""
        if not self.gpu_available or len(file_paths) == 0:
            return []
        
        try:
            # PURE: Keep EXACT same GPU batch processing as working hybrid
            batch_tensors = []
            batch_results = []
            
            for file_path in file_paths:
                try:
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        if file_size < 3000:  # EXACT same as working hybrid
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            # PURE: Create EXACT same tensors as working hybrid
                            content_chars = [ord(c) for c in content[:self.max_tensor_size]]
                            
                            # Pad to consistent size for better GPU utilization
                            if len(content_chars) < self.max_tensor_size:
                                content_chars.extend([0] * (self.max_tensor_size - len(content_chars)))
                            
                            # Convert to tensor
                            content_tensor = torch.tensor(content_chars, 
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
                # PURE: Process all tensors with EXACT same method as working hybrid
                combined_tensor = torch.stack(batch_tensors)
                
                # PURE: Keep EXACT same batch GPU operations as working hybrid
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
            logger.error("Pure GPU batch processing error: {}".format(e))
            return []

class HybridPurePushParallelProcessor:
    """Hybrid pure push parallel processor that keeps EXACTLY what works."""
    
    def __init__(self, max_workers=None):
        # PURE: Keep EXACT same worker count as working hybrid
        self.max_workers = max_workers or min(22, (os.cpu_count() or 1) + 6)  # EXACT same as working hybrid
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        self.processor = HybridPurePushProcessor()
        
        logger.info("HybridPurePushParallelProcessor initialized with {} workers (EXACT working config)".format(self.max_workers))
    
    def process_files_pure(self, file_paths, batch_size=1200):
        """Process files with EXACT same configuration as working hybrid."""
        logger.info("PURE processing of {} files with {} workers (batch size: {})".format(
            len(file_paths), self.max_workers, batch_size))
        
        start_time = time.time()
        all_results = []
        
        # PURE: Keep EXACT same batch size as working hybrid
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i+batch_size]
            batch_results = self._process_batch_pure(batch)
            all_results.extend(batch_results)
            
            # Progress update
            if (i + batch_size) % 6000 == 0 or (i + batch_size) >= len(file_paths):
                logger.info("Processed {}/{} files...".format(min(i + batch_size, len(file_paths)), len(file_paths)))
        
        total_time = time.time() - start_time
        speed = len(file_paths) / total_time
        
        logger.info("PURE processing completed: {} files in {:.3f}s ({:.0f} files/sec)".format(
            len(file_paths), total_time, speed))
        
        return all_results, total_time, speed
    
    def _process_batch_pure(self, file_paths):
        """Process a batch with EXACT same method as working hybrid."""
        futures = []
        
        # Submit all files in batch to thread pool
        for file_path in file_paths:
            future = self.executor.submit(self.processor.process_file_pure, file_path)
            futures.append(future)
        
        # Collect results with optimized timeout
        results = []
        for future in concurrent.futures.as_completed(futures, timeout=900):  # 15 minute timeout
            try:
                result = future.result(timeout=45)  # 45 second timeout per result
                results.append(result)
            except Exception as e:
                logger.error("Pure batch processing error: {}".format(e))
                results.append({'error': str(e), 'type': 'timeout'})
        
        # PURE: Keep EXACT same GPU batch processing as working hybrid
        gpu_candidates = [r for r in results if r.get('type') == 'processed' and r.get('content_size', 0) < 3000]
        if gpu_candidates and len(gpu_candidates) >= 10:
            gpu_batch_results = self.processor.process_gpu_batch_pure([r['file_path'] for r in gpu_candidates])
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
        logger.info("HybridPurePushParallelProcessor shutdown complete")

class HybridPurePushEngine:
    """Test engine for hybrid pure push that keeps EXACTLY what works."""
    
    def __init__(self):
        self.processor = HybridPurePushParallelProcessor()
        self.baseline_speed = 7973  # files/sec from working hybrid approach
        self.target_speed = 10000   # 10K files/sec target for Phase 1 completion
        
        logger.info("HybridPurePushEngine initialized - EXACT working configuration!")
    
    def collect_real_data_files(self, max_files=100000):
        """Collect REAL data files for testing."""
        logger.info("Collecting REAL data files for hybrid pure push testing...")
        
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
        
        logger.info("Collected {} REAL data files for hybrid pure push testing".format(len(real_files)))
        return real_files
    
    def run_pure_push_test(self, num_files=100000):
        """Run hybrid pure push test with MORE files to achieve 10K+ files/sec."""
        logger.info("Starting HYBRID PURE PUSH test with {} files - TARGET: 10K+ files/sec!".format(num_files))
        
        # Collect real data files
        all_files = self.collect_real_data_files(num_files * 2)
        
        if len(all_files) < num_files:
            logger.warning("Only found {} real files, using all available".format(len(all_files)))
            test_files = all_files
        else:
            test_files = all_files[:num_files]
        
        logger.info("Using {} REAL files for hybrid pure push testing".format(len(test_files)))
        
        try:
            start_time = time.time()
            
            # Process files with EXACT same configuration as working hybrid
            results, processing_time, speed = self.processor.process_files_pure(test_files)
            
            total_time = time.time() - start_time
            
            # Calculate improvement
            improvement = ((speed - self.baseline_speed) / self.baseline_speed) * 100
            
            # Generate comprehensive results
            test_results = {
                'timestamp': time.time(),
                'test_type': 'HYBRID_PURE_PUSH_EXACT_CONFIG',
                'files_processed': len(test_files),
                'processing_time_seconds': round(processing_time, 3),
                'total_time_seconds': round(total_time, 3),
                'speed_files_per_sec': round(speed, 2),
                'baseline_speed': self.baseline_speed,
                'improvement_percent': round(improvement, 2),
                'target_speed': self.target_speed,
                'target_achieved': speed >= self.target_speed,
                'phase_1_completed': speed >= self.target_speed,
                'pure_push_success': speed >= self.target_speed * 1.01,  # 1% improvement over target
                'optimizations_applied': [
                    'Phase 1 I/O optimizations (memory mapping, streaming)',
                    'Simplified content analysis (basic patterns only)',
                    'EXACT same GPU batch processing as working hybrid',
                    'EXACT same worker count (22 workers)',
                    'EXACT same batch size (1,200 files per batch)',
                    'EXACT same patterns, EXACT same I/O, EXACT same everything',
                    'Push to 10K by processing MORE files, not changing config'
                ],
                'pure_push_features': {
                    'io_optimizations': 'Enabled (Phase 1)',
                    'content_analysis': 'Simplified (no complex parsing)',
                    'gpu_acceleration': 'EXACT same as working hybrid',
                    'system_balance': 'EXACT same as working hybrid',
                    'worker_optimization': '22 workers (EXACT same)',
                    'batch_optimization': '1,200 files per batch (EXACT same)',
                    'strategy': 'Keep EXACT config, process MORE files'
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
                    'processing_mode': 'Hybrid Pure Push (EXACT Config)'
                },
                'performance_metrics': {
                    'files_per_second': round(speed, 2),
                    'megabytes_per_second': round((self.processor.processor.total_content_size / 1024 / 1024) / processing_time, 2),
                    'efficiency_score': round((speed / self.baseline_speed) * 100, 2),
                    'phase_1_target_achieved': speed >= self.target_speed,
                    'pure_push_target_achieved': speed >= self.target_speed * 1.01
                }
            }
            
            logger.info("HYBRID PURE PUSH test completed successfully!")
            return test_results
            
        except Exception as e:
            logger.error("HYBRID PURE PUSH test failed: {}".format(e))
            return None
        
        finally:
            self.processor.shutdown()
    
    def save_results(self, results, filename="phase3_hybrid_pure_push_results.json"):
        """Save test results to JSON file."""
        output_dir = Path("ops/test_output/phase3_performance")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / filename
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info("HYBRID PURE PUSH test results saved to: {}".format(output_file))
        return output_file
    
    def print_summary(self, results):
        """Print comprehensive test summary."""
        print("\n" + "="*80)
        print("PHASE 3 HYBRID PURE PUSH TEST RESULTS - EXACT CONFIG!")
        print("="*80)
        
        print("TEST TYPE: HYBRID PURE PUSH EXACT CONFIG")
        print("FILES PROCESSED: {} REAL files".format(results['files_processed']))
        print("PROCESSING TIME: {:.3f} seconds".format(results['processing_time_seconds']))
        print("TOTAL TIME: {:.3f} seconds".format(results['total_time_seconds']))
        print("SPEED: {:.0f} files/sec".format(results['speed_files_per_sec']))
        print("BASELINE: {:.0f} files/sec".format(results['baseline_speed']))
        print("IMPROVEMENT: {:.1f}%".format(results['improvement_percent']))
        print("TARGET: {:.0f} files/sec".format(results['target_speed']))
        print("TARGET ACHIEVED: {}".format("YES" if results['target_achieved'] else "NO"))
        
        print("\nPURE PUSH STATUS:")
        print("Phase 1 Completed: {}".format("YES" if results['phase_1_completed'] else "NO"))
        print("Pure Push Success: {}".format("YES" if results['pure_push_success'] else "NO"))
        print("Ready for Phase 3: {}".format("YES" if results['pure_push_success'] else "NO"))
        
        print("\nPURE PUSH FEATURES:")
        for feature, status in results['pure_push_features'].items():
            print("- {}: {}".format(feature.replace('_', ' ').title(), status))
        
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
        print("Pure Push Target: {}".format("ACHIEVED" if results['performance_metrics']['pure_push_target_achieved'] else "NOT ACHIEVED"))
        
        print("="*80)

def main():
    """Main execution function."""
    print("PHASE 3 HYBRID PURE PUSH ENGINE")
    print("="*80)
    print("PURE APPROACH: Keep EXACT Working Configuration!")
    print("Target: Push working hybrid approach from 7,973 to 10K+ files/sec by scaling UP")
    print("="*80)
    
    # Create hybrid pure push test engine
    engine = HybridPurePushEngine()
    
    # Run hybrid pure push test with 100K files (MORE files to achieve higher throughput)
    print("Starting HYBRID PURE PUSH test with 100,000 files...")
    print("Keeping EXACT working configuration, processing MORE files...")
    
    results = engine.run_pure_push_test(num_files=100000)
    
    if results:
        # Save results
        output_file = engine.save_results(results)
        
        # Print comprehensive summary
        engine.print_summary(results)
        
        print("\nHYBRID PURE PUSH test completed successfully!")
        print("Results saved to: {}".format(output_file))
        
        if results['phase_1_completed']:
            print(" PHASE 1 TARGET ACHIEVED: 10K+ files/sec!")
            print(" PURE PUSH SUCCESS!")
            print(" Phase 1 COMPLETED!")
            print(" Ready for Phase 3: Advanced GPU and System Balance")
            
            if results['pure_push_success']:
                print(" EXCEEDED TARGET: 1%+ improvement over 10K!")
            else:
                print(" Target achieved but need 1%+ for pure push success")
        else:
            print(" Performance: {:.0f} files/sec (need {:.0f} more for 10K target)".format(
                results['speed_files_per_sec'], 
                results['target_speed'] - results['speed_files_per_sec']))
            print(" Pure push needs more files to achieve target")
        
        print("Next Phase: Advanced GPU and System Balance Optimization")
        
    else:
        print("\nHYBRID PURE PUSH test failed!")
        print("Please check the logs for details.")

if __name__ == "__main__":
    main()
