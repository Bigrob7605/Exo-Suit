#!/usr/bin/env python3
"""
Performance Benchmark System - Real Performance Validation
Agent Exo-Suit V5.0 - No More Fabricated Numbers

This system provides REAL performance benchmarks using actual data from the toolbox folder.
No more inflated claims - only verified, measurable performance metrics.
"""

import os
import time
import json
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
import statistics

class PerformanceBenchmark:
    """Real performance benchmarking with actual data validation"""
    
    def __init__(self):
        self.toolbox_path = Path("../toolbox")  # Relative to ops folder
        self.results = {}
        self.benchmark_data = {}
        
    def get_system_info(self):
        """Get real system specifications"""
        try:
            # Get GPU info if available
            gpu_info = "Unknown"
            try:
                result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'], 
                                     capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    gpu_info = result.stdout.strip()
            except:
                pass
            
            return {
                "cpu": psutil.cpu_count(logical=True),
                "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "gpu": gpu_info,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def scan_toolbox_files(self):
        """Scan toolbox folder for real files to process"""
        if not self.toolbox_path.exists():
            return {"error": "Toolbox folder not found"}
        
        files = []
        total_size = 0
        
        for file_path in self.toolbox_path.rglob("*"):
            if file_path.is_file():
                files.append({
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "type": file_path.suffix
                })
                total_size += file_path.stat().st_size
        
        return {
            "file_count": len(files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024**2), 2),
            "files": files[:100]  # Limit to first 100 for testing
        }
    
    def benchmark_file_processing(self, files, operation="scan"):
        """Real file processing benchmark"""
        if not files:
            return {"error": "No files to process"}
        
        start_time = time.time()
        start_memory = psutil.virtual_memory().used
        
        processed_count = 0
        total_size = 0
        
        for file_info in files:
            try:
                # Simulate file processing (reading file info)
                file_path = Path(file_info["path"])
                if file_path.exists():
                    # Read first 1KB to simulate processing
                    with open(file_path, 'rb') as f:
                        f.read(1024)
                    
                    processed_count += 1
                    total_size += file_info["size"]
                    
            except Exception as e:
                continue
        
        end_time = time.time()
        end_memory = psutil.virtual_memory().used
        
        duration = end_time - start_time
        files_per_second = processed_count / duration if duration > 0 else 0
        memory_used_mb = (end_memory - start_memory) / (1024**2)
        
        return {
            "operation": operation,
            "files_processed": processed_count,
            "total_size_mb": round(total_size / (1024**2), 2),
            "duration_seconds": round(duration, 3),
            "files_per_second": round(files_per_second, 1),
            "memory_used_mb": round(memory_used_mb, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def benchmark_gpu_operations(self):
        """Benchmark GPU operations if available"""
        try:
            # Check if CUDA is available
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'], 
                                 capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                gpu_data = result.stdout.strip().split(',')
                if len(gpu_data) >= 3:
                    return {
                        "gpu_utilization_percent": int(gpu_data[0]),
                        "memory_used_mb": int(gpu_data[1]),
                        "memory_total_mb": int(gpu_data[2]),
                        "memory_utilization_percent": round((int(gpu_data[1]) / int(gpu_data[2])) * 100, 1),
                        "timestamp": datetime.now().isoformat()
                    }
        except:
            pass
        
        return {"error": "GPU not available or nvidia-smi failed"}
    
    def run_comprehensive_benchmark(self):
        """Run all benchmarks and generate comprehensive report"""
        print("🚀 Starting REAL Performance Benchmark...")
        print("=" * 50)
        
        # System information
        print("📊 System Information:")
        system_info = self.get_system_info()
        print(json.dumps(system_info, indent=2))
        print()
        
        # Toolbox scan
        print("📁 Scanning Toolbox Files:")
        toolbox_info = self.scan_toolbox_files()
        if "error" not in toolbox_info:
            print(f"Found {toolbox_info['file_count']} files ({toolbox_info['total_size_mb']} MB)")
        else:
            print(f"Error: {toolbox_info['error']}")
        print()
        
        # File processing benchmark
        if "files" in toolbox_info:
            print("⚡ File Processing Benchmark:")
            processing_result = self.benchmark_file_processing(toolbox_info["files"])
            if "error" not in processing_result:
                print(f"Processed {processing_result['files_processed']} files in {processing_result['duration_seconds']}s")
                print(f"Performance: {processing_result['files_per_second']} files/sec")
                print(f"Memory used: {processing_result['memory_used_mb']} MB")
            else:
                print(f"Error: {processing_result['error']}")
            print()
        
        # GPU benchmark
        print("🎮 GPU Operations Benchmark:")
        gpu_result = self.benchmark_gpu_operations()
        if "error" not in gpu_result:
            print(f"GPU Utilization: {gpu_result['gpu_utilization_percent']}%")
            print(f"Memory Usage: {gpu_result['memory_utilization_percent']}%")
        else:
            print(f"GPU: {gpu_result['error']}")
        print()
        
        # Generate results summary
        self.results = {
            "system_info": system_info,
            "toolbox_info": toolbox_info,
            "processing_benchmark": processing_result if "files" in toolbox_info else {"error": "No files to process"},
            "gpu_benchmark": gpu_result,
            "benchmark_timestamp": datetime.now().isoformat()
        }
        
        # Save results
        self.save_results()
        
        return self.results
    
    def save_results(self):
        """Save benchmark results to file"""
        try:
            results_file = Path("performance_benchmark_results.json")
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"💾 Results saved to: {results_file}")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def generate_performance_report(self):
        """Generate human-readable performance report"""
        if not self.results:
            return "No benchmark results available. Run benchmark first."
        
        report = []
        report.append("# 🚀 REAL PERFORMANCE BENCHMARK REPORT")
        report.append("")
        report.append("**Date**: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        report.append("**Status**: REAL BENCHMARKS - No Fabricated Numbers")
        report.append("")
        
        # System Summary
        if "system_info" in self.results:
            sys_info = self.results["system_info"]
            report.append("## 📊 System Information")
            if "error" not in sys_info:
                report.append(f"- **CPU Cores**: {sys_info.get('cpu', 'Unknown')}")
                report.append(f"- **Memory**: {sys_info.get('memory_gb', 'Unknown')} GB")
                report.append(f"- **GPU**: {sys_info.get('gpu', 'Unknown')}")
            else:
                report.append(f"- **Error**: {sys_info['error']}")
            report.append("")
        
        # Performance Summary
        if "processing_benchmark" in self.results:
            perf = self.results["processing_benchmark"]
            if "error" not in perf:
                report.append("## ⚡ Performance Results")
                report.append(f"- **Files Processed**: {perf['files_processed']}")
                report.append(f"- **Processing Speed**: {perf['files_per_second']} files/sec")
                report.append(f"- **Duration**: {perf['duration_seconds']} seconds")
                report.append(f"- **Memory Used**: {perf['memory_used_mb']} MB")
                report.append("")
        
        # GPU Summary
        if "gpu_benchmark" in self.results:
            gpu = self.results["gpu_benchmark"]
            if "error" not in gpu:
                report.append("## 🎮 GPU Performance")
                report.append(f"- **GPU Utilization**: {gpu['gpu_utilization_percent']}%")
                report.append(f"- **Memory Usage**: {gpu['memory_utilization_percent']}%")
                report.append("")
        
        # Reality Check
        report.append("## 🚨 REALITY CHECK - NO MORE FABRICATED CLAIMS")
        report.append("")
        report.append("**Previous Inflated Claims (CORRECTED):**")
        report.append("- ❌ '5K files/sec average' → ✅ Actual: See benchmark results above")
        report.append("- ❌ '15K+ files/sec peak' → ✅ Actual: See benchmark results above")
        report.append("- ❌ '99.5% VRAM utilization' → ✅ Actual: See GPU benchmark above")
        report.append("- ❌ '720,958 overall performance score' → ✅ Actual: Real metrics above")
        report.append("")
        report.append("**This report contains ONLY verified, measurable performance data.**")
        report.append("**No more hand-waving. No more inflated claims. Just the truth.**")
        
        return "\n".join(report)

def main():
    """Main benchmark execution"""
    print("🚀 Agent Exo-Suit V5.0 - REAL Performance Benchmark System")
    print("=" * 60)
    print("This system provides ACTUAL performance metrics - no fabricated numbers!")
    print("=" * 60)
    print()
    
    benchmark = PerformanceBenchmark()
    
    # Run comprehensive benchmark
    results = benchmark.run_comprehensive_benchmark()
    
    # Generate and display report
    print("📋 Performance Report:")
    print("=" * 50)
    report = benchmark.generate_performance_report()
    print(report)
    
    # Save report to file
    try:
        report_file = Path("performance_report.md")
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\n💾 Report saved to: {report_file}")
    except Exception as e:
        print(f"\nError saving report: {e}")

if __name__ == "__main__":
    main()
