#!/usr/bin/env python3
"""
PHASE 3 PERFORMANCE BASELINE TESTING
Agent Exo-Suit V5.0 - Phase 3 Development

This script establishes performance baselines for Phase 3 development,
measuring current file processing speed, memory usage, and GPU utilization.
"""

import os
import time
import psutil
import torch
import json
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PerformanceBaseline:
    """Performance baseline testing for Phase 3 development."""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {},
            'gpu_info': {},
            'baseline_tests': {},
            'performance_metrics': {}
        }
        
    def get_system_info(self):
        """Gather system information."""
        logger.info("Gathering system information...")
        
        # CPU Information
        cpu_info = {
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            'cpu_percent': psutil.cpu_percent(interval=1)
        }
        
        # Memory Information
        memory = psutil.virtual_memory()
        memory_info = {
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'percent_used': memory.percent
        }
        
        # Disk Information
        disk = psutil.disk_usage('/')
        disk_info = {
            'total_gb': round(disk.total / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'percent_used': round((disk.used / disk.total) * 100, 2)
        }
        
        self.results['system_info'] = {
            'cpu': cpu_info,
            'memory': memory_info,
            'disk': disk_info,
            'platform': os.name,
            'python_version': "{}.{}.{}".format(os.sys.version_info.major, os.sys.version_info.minor, os.sys.version_info.micro)
        }
        
        logger.info("System: {} CPUs, {}GB RAM, {}GB Disk".format(cpu_info['cpu_count'], memory_info['total_gb'], disk_info['total_gb']))
        
    def get_gpu_info(self):
        """Gather GPU information."""
        logger.info("Gathering GPU information...")
        
        gpu_info = {}
        
        # Check PyTorch CUDA
        if torch.cuda.is_available():
            gpu_info['pytorch_cuda'] = {
                'available': True,
                'version': torch.version.cuda,
                'device_count': torch.cuda.device_count(),
                'current_device': torch.cuda.current_device(),
                'device_name': torch.cuda.get_device_name(0),
                'device_capability': torch.cuda.get_device_capability(0),
                'memory_allocated_gb': round(torch.cuda.memory_allocated(0) / (1024**3), 3),
                'memory_reserved_gb': round(torch.cuda.memory_reserved(0) / (1024**3), 3),
                'max_memory_gb': round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
            }
            logger.info("PyTorch CUDA: {} with {}GB VRAM".format(gpu_info['pytorch_cuda']['device_name'], gpu_info['pytorch_cuda']['max_memory_gb']))
        else:
            gpu_info['pytorch_cuda'] = {'available': False}
            logger.warning("PyTorch CUDA not available")
        
        # Check NVIDIA SMI (if available)
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu', '--format=csv,noheader,nounits'], 
                                 capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        parts = line.split(', ')
                        if len(parts) >= 6:
                            gpu_info['nvidia_smi'] = {
                                'name': parts[0],
                                'memory_total_mb': int(parts[1]),
                                'memory_used_mb': int(parts[2]),
                                'memory_free_mb': int(parts[3]),
                                'utilization_percent': int(parts[4]),
                                'temperature_celsius': int(parts[5])
                            }
                            logger.info("NVIDIA SMI: {}, {}MB VRAM".format(gpu_info['nvidia_smi']['name'], gpu_info['nvidia_smi']['memory_total_mb']))
        except Exception as e:
            logger.warning("Could not get NVIDIA SMI info: {}".format(e))
        
        self.results['gpu_info'] = gpu_info
        
    def test_file_processing_baseline(self):
        """Test baseline file processing performance."""
        logger.info("Testing baseline file processing performance...")
        
        # Create test files
        test_dir = Path("test_performance_files")
        test_dir.mkdir(exist_ok=True)
        
        # Generate test files of different sizes
        file_sizes = [1, 10, 100, 1000]  # KB
        test_files = []
        
        for size_kb in file_sizes:
            filename = test_dir / "test_{}kb.txt".format(size_kb)
            content = "A" * (size_kb * 1024)
            with open(filename, 'w') as f:
                f.write(content)
            test_files.append(filename)
        
        # Test file reading performance
        read_times = {}
        for filename in test_files:
            size_kb = filename.stem.split('_')[1].replace('kb', '')
            
            # Test multiple reads for accuracy
            times = []
            for _ in range(5):
                start_time = time.time()
                with open(filename, 'r') as f:
                    content = f.read()
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = sum(times) / len(times)
            read_times["{}kb".format(size_kb)] = {
                'avg_time_ms': round(avg_time * 1000, 3),
                'speed_mb_per_sec': round((int(size_kb) / 1024) / avg_time, 2),
                'individual_times_ms': [round(t * 1000, 3) for t in times]
            }
        
        # Test file counting performance
        start_time = time.time()
        file_count = 0
        for root, dirs, files in os.walk("."):
            file_count += len(files)
        end_time = time.time()
        
        file_count_time = (end_time - start_time) * 1000
        
        # Test directory scanning performance
        start_time = time.time()
        dir_count = 0
        for root, dirs, files in os.walk("."):
            dir_count += len(dirs)
        end_time = time.time()
        
        dir_scan_time = (end_time - start_time) * 1000
        
        self.results['baseline_tests'] = {
            'file_reading': read_times,
            'file_counting': {
                'total_files': file_count,
                'time_ms': round(file_count_time, 3),
                'files_per_second': round(file_count / (file_count_time / 1000), 2)
            },
            'directory_scanning': {
                'total_dirs': dir_count,
                'time_ms': round(dir_scan_time, 3),
                'dirs_per_second': round(dir_count / (dir_scan_time / 1000), 2)
            }
        }
        
        # Cleanup test files
        for filename in test_files:
            filename.unlink()
        test_dir.rmdir()
        
        logger.info("Baseline test complete: {} files found in {:.3f}ms".format(file_count, file_count_time))
        
    def test_memory_operations(self):
        """Test memory operation performance."""
        logger.info("Testing memory operation performance...")
        
        # Test memory allocation
        start_time = time.time()
        test_data = []
        for i in range(1000):
            test_data.append([i] * 1000)
        allocation_time = (time.time() - start_time) * 1000
        
        # Test memory access
        start_time = time.time()
        total = 0
        for row in test_data:
            total += sum(row)
        access_time = (time.time() - start_time) * 1000
        
        # Test memory cleanup
        start_time = time.time()
        del test_data
        cleanup_time = (time.time() - start_time) * 1000
        
        self.results['performance_metrics']['memory_operations'] = {
            'allocation_time_ms': round(allocation_time, 3),
            'access_time_ms': round(access_time, 3),
            'cleanup_time_ms': round(cleanup_time, 3),
            'total_memory_operations_ms': round(allocation_time + access_time + cleanup_time, 3)
        }
        
        logger.info("Memory operations: allocation={:.3f}ms, access={:.3f}ms, cleanup={:.3f}ms".format(allocation_time, access_time, cleanup_time))
        
    def test_gpu_operations(self):
        """Test GPU operation performance."""
        logger.info("Testing GPU operation performance...")
        
        if not torch.cuda.is_available():
            logger.warning("GPU not available for testing")
            self.results['performance_metrics']['gpu_operations'] = {'available': False}
            return
        
        try:
            device = torch.device('cuda:0')
            
            # Test GPU memory allocation
            start_time = time.time()
            tensor = torch.randn(1000, 1000, device=device)
            allocation_time = (time.time() - start_time) * 1000
            
            # Test GPU computation
            start_time = time.time()
            result = torch.mm(tensor, tensor)
            computation_time = (time.time() - start_time) * 1000
            
            # Test CPU-GPU transfer
            start_time = time.time()
            cpu_tensor = result.cpu()
            transfer_time = (time.time() - start_time) * 1000
            
            # Test GPU memory cleanup
            start_time = time.time()
            del tensor, result, cpu_tensor
            torch.cuda.empty_cache()
            cleanup_time = (time.time() - start_time) * 1000
            
            self.results['performance_metrics']['gpu_operations'] = {
                'available': True,
                'allocation_time_ms': round(allocation_time, 3),
                'computation_time_ms': round(computation_time, 3),
                'transfer_time_ms': round(transfer_time, 3),
                'cleanup_time_ms': round(cleanup_time, 3),
                'total_gpu_operations_ms': round(allocation_time + computation_time + transfer_time + cleanup_time, 3)
            }
            
            logger.info("GPU operations: allocation={:.3f}ms, computation={:.3f}ms, transfer={:.3f}ms".format(allocation_time, computation_time, transfer_time))
            
        except Exception as e:
            logger.error("GPU testing failed: {}".format(e))
            self.results['performance_metrics']['gpu_operations'] = {'available': False, 'error': str(e)}
    
    def run_all_tests(self):
        """Run all performance baseline tests."""
        logger.info("Starting Phase 3 Performance Baseline Testing...")
        
        try:
            self.get_system_info()
            self.get_gpu_info()
            self.test_file_processing_baseline()
            self.test_memory_operations()
            self.test_gpu_operations()
            
            # Calculate overall performance score
            self.calculate_performance_score()
            
            logger.info("Performance baseline testing completed successfully!")
            return True
            
        except Exception as e:
            logger.error("Performance baseline testing failed: {}".format(e))
            return False
    
    def calculate_performance_score(self):
        """Calculate overall performance score."""
        logger.info("Calculating performance score...")
        
        # Base score starts at 100
        score = 100
        
        # File processing performance
        if 'baseline_tests' in self.results:
            file_counting = self.results['baseline_tests']['file_counting']
            files_per_sec = file_counting['files_per_second']
            
            # Target: 1000+ files/sec
            if files_per_sec >= 1000:
                score += 50  # Excellent
            elif files_per_sec >= 500:
                score += 25  # Good
            elif files_per_sec >= 100:
                score += 10  # Acceptable
            else:
                score -= 20  # Poor
        
        # GPU utilization
        if 'gpu_info' in self.results and 'pytorch_cuda' in self.results['gpu_info']:
            if self.results['gpu_info']['pytorch_cuda']['available']:
                score += 20  # GPU available
            else:
                score -= 30  # No GPU
        
        # Memory efficiency
        if 'system_info' in self.results:
            memory_used = self.results['system_info']['memory']['percent_used']
            if memory_used < 50:
                score += 15  # Good memory efficiency
            elif memory_used < 80:
                score += 5   # Acceptable memory usage
            else:
                score -= 10  # High memory usage
        
        self.results['performance_score'] = max(0, min(200, score))  # Clamp between 0-200
        
        logger.info("Performance Score: {}/200".format(self.results['performance_score']))
    
    def save_results(self, filename="phase3_performance_baseline.json"):
        """Save test results to JSON file."""
        output_dir = Path("ops/test_output/phase3_performance")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / filename
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info("Results saved to: {}".format(output_file))
        return output_file
    
    def print_summary(self):
        """Print test results summary."""
        print("\n" + "="*80)
        print("PHASE 3 PERFORMANCE BASELINE RESULTS")
        print("="*80)
        
        # System Info
        if 'system_info' in self.results:
            sys_info = self.results['system_info']
            print("System: {} CPUs, {}GB RAM".format(sys_info['cpu']['cpu_count'], sys_info['memory']['total_gb']))
            print("Platform: {}, Python: {}".format(sys_info['platform'], sys_info['python_version']))
        
        # GPU Info
        if 'gpu_info' in self.results and 'pytorch_cuda' in self.results['gpu_info']:
            gpu_info = self.results['gpu_info']['pytorch_cuda']
            if gpu_info['available']:
                print("GPU: {} ({}GB VRAM)".format(gpu_info['device_name'], gpu_info['max_memory_gb']))
                print("CUDA: {}".format(gpu_info['version']))
            else:
                print("GPU: Not available")
        
        # Performance Metrics
        if 'baseline_tests' in self.results:
            file_counting = self.results['baseline_tests']['file_counting']
            print("File Processing: {} files/sec".format(file_counting['files_per_second']))
        
        if 'performance_score' in self.results:
            print("Performance Score: {}/200".format(self.results['performance_score']))
        
        print("="*80)

def main():
    """Main execution function."""
    print("PHASE 3 PERFORMANCE BASELINE TESTING - Agent Exo-Suit V5.0")
    print("="*80)
    
    # Create and run performance baseline
    baseline = PerformanceBaseline()
    
    if baseline.run_all_tests():
        # Save results
        output_file = baseline.save_results()
        
        # Print summary
        baseline.print_summary()
        
        print("\nPerformance baseline testing completed successfully!")
        print("Results saved to: {}".format(output_file))
        print("Ready for Phase 3 development!")
        
    else:
        print("\nPerformance baseline testing failed!")
        print("Please check the logs for details.")

if __name__ == "__main__":
    main()
