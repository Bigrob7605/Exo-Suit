#!/usr/bin/env python3
"""
Comprehensive test script for CPU+GPU dual-mode RAG system.
Tests: CPU-only, GPU-only, and CPU+GPU hybrid modes with performance benchmarking.
"""
import os
import sys
import time
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Fix Windows console encoding issues
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def run_command(cmd: List[str], description: str) -> Tuple[bool, str, float]:
    """Run a command and return success status, output, and duration"""
    print(f"[BUILD] {description}...")
    print(f"  Command: {' '.join(cmd)}")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=Path(__file__).parent,
            timeout=300  # 5 minute timeout
        )
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"  [OK] Success ({duration:.2f}s)")
            return True, result.stdout, duration
        else:
            print(f"  [FAIL] Failed ({duration:.2f}s)")
            print(f"    Error: {result.stderr}")
            return False, result.stderr, duration
            
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        print(f"  [TIMEOUT] Timeout after {duration:.2f}s")
        return False, "Command timed out", duration
    except Exception as e:
        duration = time.time() - start_time
        print(f"  [ERROR] Exception: {e}")
        return False, str(e), duration

def test_device_detection() -> Dict[str, bool]:
    """Test device detection capabilities"""
    print("[TEST] Testing Device Detection")
    print("=" * 40)
    
    devices = {}
    
    # Test Python environment
    success, output, duration = run_command(
        ["python", "--version"], 
        "Python version check"
    )
    devices['python'] = success
    
    # Test GPU detection
    success, output, duration = run_command(
        ["python", "-c", "import torch; print('CUDA:', torch.cuda.is_available())"], 
        "GPU detection"
    )
    devices['gpu'] = success and "CUDA: True" in output
    
    # Test CPU detection
    success, output, duration = run_command(
        ["python", "-c", "import multiprocessing as mp; print('CPU cores:', mp.cpu_count())"], 
        "CPU detection"
    )
    devices['cpu'] = success
    
    # Test required packages
    packages = ['torch', 'faiss-cpu', 'sentence-transformers', 'numpy']
    for package in packages:
        success, output, duration = run_command(
            ["python", "-c", f"import {package}; print('OK')"], 
            f"Package check: {package}"
        )
        devices[f'package_{package}'] = success
    
    return devices

def test_embedding_modes() -> Dict[str, Dict]:
    """Test different embedding modes"""
    print("\n[TEST] Testing Embedding Modes")
    print("=" * 40)
    
    results = {}
    
    # Test CPU-only mode
    print("\n[CPU] Testing CPU-only mode...")
    success, output, duration = run_command(
        [".\\embed.ps1", "-CPU"], 
        "CPU-only embedding"
    )
    results['cpu_only'] = {
        'success': success,
        'output': output,
        'duration': duration
    }
    
    # Test GPU-only mode (if available)
    print("\n[GPU] Testing GPU-only mode...")
    success, output, duration = run_command(
        [".\\embed.ps1", "-GPU"], 
        "GPU-only embedding"
    )
    results['gpu_only'] = {
        'success': success,
        'output': output,
        'duration': duration
    }
    
    # Test hybrid mode (if both available)
    print("\n[HYBRID] Testing hybrid CPU+GPU mode...")
    success, output, duration = run_command(
        [".\\embed.ps1", "-Hybrid"], 
        "Hybrid CPU+GPU embedding"
    )
    results['hybrid'] = {
        'success': success,
        'output': output,
        'duration': duration
    }
    
    # Test auto-detection mode
    print("\n[AUTO] Testing auto-detection mode...")
    success, output, duration = run_command(
        [".\\embed.ps1"], 
        "Auto-detection embedding"
    )
    results['auto'] = {
        'success': success,
        'output': output,
        'duration': duration
    }
    
    return results

def test_retrieval_modes() -> Dict[str, Dict]:
    """Test different retrieval modes"""
    print("\n[TEST] Testing Retrieval Modes")
    print("=" * 40)
    
    # Check if index exists
    index_file = Path("index.faiss")
    if not index_file.exists():
        print("[WARNING] No index found. Skipping retrieval tests.")
        return {}
    
    results = {}
    test_query = "GPU acceleration and performance optimization"
    
    # Test CPU-only retrieval
    print("\n[CPU] Testing CPU-only retrieval...")
    success, output, duration = run_command(
        ["python", "retrieve.py", "--query", test_query, "--cpu", "--topk", "10"], 
        "CPU-only retrieval"
    )
    results['cpu_retrieval'] = {
        'success': success,
        'output': output,
        'duration': duration
    }
    
    # Test GPU-only retrieval
    print("\n[GPU] Testing GPU-only retrieval...")
    success, output, duration = run_command(
        ["python", "retrieve.py", "--query", test_query, "--gpu", "--topk", "10"], 
        "GPU-only retrieval"
    )
    results['gpu_retrieval'] = {
        'success': success,
        'output': output,
        'duration': duration
    }
    
    # Test hybrid retrieval
    print("\n[HYBRID] Testing hybrid retrieval...")
    success, output, duration = run_command(
        ["python", "retrieve.py", "--query", test_query, "--hybrid", "--topk", "10"], 
        "Hybrid retrieval"
    )
    results['hybrid_retrieval'] = {
        'success': success,
        'output': output,
        'duration': duration
    }
    
    return results

def benchmark_performance() -> Dict[str, float]:
    """Run performance benchmarks"""
    print("\n[BENCHMARK] Performance Benchmarking")
    print("=" * 40)
    
    benchmarks = {}
    
    # Test with different batch sizes
    batch_sizes = [10, 50, 100]
    
    for batch_size in batch_sizes:
        print(f"\n[BATCH] Benchmarking batch size: {batch_size}")
        
        # CPU benchmark
        success, output, duration = run_command(
            ["python", "retrieve.py", "--query", "test query", "--cpu", "--topk", str(batch_size)], 
            f"CPU benchmark ({batch_size} results)"
        )
        if success:
            benchmarks[f'cpu_batch_{batch_size}'] = duration
        
        # GPU benchmark (if available)
        success, output, duration = run_command(
            ["python", "retrieve.py", "--query", "test query", "--gpu", "--topk", str(batch_size)], 
            f"GPU benchmark ({batch_size} results)"
        )
        if success:
            benchmarks[f'gpu_batch_{batch_size}'] = duration
    
    return benchmarks

def generate_test_report(devices: Dict[str, bool], 
                        embedding_results: Dict[str, Dict],
                        retrieval_results: Dict[str, Dict],
                        benchmarks: Dict[str, float]) -> str:
    """Generate comprehensive test report"""
    print("\n[REPORT] Generating Test Report")
    print("=" * 40)
    
    report = {
        "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "system_info": {
            "python_available": devices.get('python', False),
            "gpu_available": devices.get('gpu', False),
            "cpu_available": devices.get('cpu', False),
            "packages_available": {
                k.replace('package_', ''): v 
                for k, v in devices.items() 
                if k.startswith('package_')
            }
        },
        "embedding_tests": embedding_results,
        "retrieval_tests": retrieval_results,
        "performance_benchmarks": benchmarks,
        "summary": {
            "total_tests": len(embedding_results) + len(retrieval_results),
            "successful_tests": sum(1 for r in embedding_results.values() if r['success']) + 
                              sum(1 for r in retrieval_results.values() if r['success']),
            "device_modes_working": []
        }
    }
    
    # Determine which device modes are working
    if devices.get('gpu', False):
        if any(r['success'] for r in embedding_results.values() if 'gpu' in r.get('output', '')):
            report['summary']['device_modes_working'].append('GPU')
    if devices.get('cpu', False):
        if any(r['success'] for r in embedding_results.values() if 'cpu' in r.get('output', '')):
            report['summary']['device_modes_working'].append('CPU')
    if len(report['summary']['device_modes_working']) >= 2:
        report['summary']['device_modes_working'].append('Hybrid')
    
    # Save report
    report_file = "dual_mode_test_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"[OK] Test report saved to: {report_file}")
    return report_file

def display_test_summary(report_file: str):
    """Display test summary"""
    print("\n[SUMMARY] Test Summary")
    print("=" * 40)
    
    with open(report_file, 'r') as f:
        report = json.load(f)
    
    print(f"[DATE] Test Date: {report['test_timestamp']}")
    print(f"[TESTS] Total Tests: {report['summary']['total_tests']}")
    print(f"[OK] Successful: {report['summary']['successful_tests']}")
    print(f"[FAIL] Failed: {report['summary']['total_tests'] - report['summary']['successful_tests']}")
    
    print(f"\n[DEVICES] Device Modes Working:")
    for mode in report['summary']['device_modes_working']:
        print(f"  [OK] {mode}")
    
    print(f"\n[BENCHMARKS] Performance Benchmarks:")
    for benchmark, duration in report['performance_benchmarks'].items():
        print(f"  {benchmark}: {duration:.3f}s")
    
    print(f"\n[REPORT] Full report: {report_file}")

def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description='Test CPU+GPU dual-mode RAG system')
    parser.add_argument('--skip-embedding', action='store_true', help='Skip embedding tests')
    parser.add_argument('--skip-retrieval', action='store_true', help='Skip retrieval tests')
    parser.add_argument('--skip-benchmarks', action='store_true', help='Skip performance benchmarks')
    args = parser.parse_args()
    
    print("[TEST] Agent Exo-Suit V3.0 - Dual-Mode RAG System Test")
    print("=" * 60)
    
    # Test device detection
    devices = test_device_detection()
    
    # Test embedding modes
    embedding_results = {}
    if not args.skip_embedding:
        embedding_results = test_embedding_modes()
    
    # Test retrieval modes
    retrieval_results = {}
    if not args.skip_retrieval:
        retrieval_results = test_retrieval_modes()
    
    # Run performance benchmarks
    benchmarks = {}
    if not args.skip_benchmarks:
        benchmarks = benchmark_performance()
    
    # Generate and display report
    report_file = generate_test_report(devices, embedding_results, retrieval_results, benchmarks)
    display_test_summary(report_file)
    
    print("\n[SUCCESS] Test Suite Completed!")
    print("Check the test report for detailed results and performance metrics.")

if __name__ == '__main__':
    exit(main())
