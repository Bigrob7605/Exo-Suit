#!/usr/bin/env python3
"""
MMH-RS COMPRESSION TEST ON REAL SILESIA CORPUS

This script tests our MMH-RS compression system on the real Silesia Corpus,
a diverse dataset containing PDF, HTML, source code, binaries, DB dumps, and images.
This gives us real-world compression performance data.
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

# Import our MMH-RS compressor
try:
    from mmh_rs_compressor import MMHRSCompressor
except ImportError:
    print("❌ MMH-RS compressor not found. Please ensure mmh_rs_compressor.py is available.")
    sys.exit(1)

@dataclass
class SilesiaTestResult:
    """Result of testing a Silesia Corpus file"""
    file_name: str
    file_size: int
    compression_results: Dict[str, Any]
    best_compression: str
    best_ratio: float
    best_speed: float

class SilesiaCorpusTester:
    """Test MMH-RS compression on Silesia Corpus files"""
    
    def __init__(self):
        self.silesia_path = Path("silesia_corpus")
        self.compressor = MMHRSCompressor()
        self.results = []
        
    def get_silesia_files(self) -> List[Path]:
        """Get all files from the Silesia Corpus"""
        files = []
        for file_path in self.silesia_path.iterdir():
            if file_path.is_file():
                files.append(file_path)
        
        # Sort by size (largest first)
        files.sort(key=lambda x: x.stat().st_size, reverse=True)
        return files
    
    def test_file_compression(self, file_path: Path) -> SilesiaTestResult:
        """Test compression on a single Silesia file"""
        print(f"\n🔧 Testing: {file_path.name}")
        
        file_size = file_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        print(f"   📁 File size: {size_mb:.2f} MB ({file_size:,} bytes)")
        
        # Read the file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Test all available compression methods
        compression_results = {}
        best_ratio = 0
        best_method = ""
        best_speed = 0
        
        print(f"   📦 Testing compression methods...")
        
        for method in self.compressor.available_methods:
            try:
                print(f"      Testing {method.upper()}...", end=" ")
                
                # Compress the file
                start_time = time.time()
                result = self.compressor.compress(file_data, method)
                compression_time = time.time() - start_time
                
                if result.success:
                    compression_results[method] = {
                        'compressed_size': result.compressed_size,
                        'compression_ratio': result.compression_ratio,
                        'speed_mb_s': result.speed_mb_s,
                        'processing_time': compression_time,
                        'space_saved_mb': (file_size - result.compressed_size) / (1024 * 1024)
                    }
                    
                    print(f"✅ {result.compression_ratio:.2f}x compression, {result.speed_mb_s:.1f} MB/s")
                    
                    # Track best performance
                    if result.compression_ratio > best_ratio:
                        best_ratio = result.compression_ratio
                        best_method = method
                        best_speed = result.speed_mb_s
                else:
                    print(f"❌ Failed: {result.error_message}")
                    compression_results[method] = {
                        'error': result.error_message
                    }
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                compression_results[method] = {
                    'error': str(e)
                }
        
        return SilesiaTestResult(
            file_name=file_path.name,
            file_size=file_size,
            compression_results=compression_results,
            best_compression=best_method,
            best_ratio=best_ratio,
            best_speed=best_speed
        )
    
    def run_comprehensive_test(self):
        """Run comprehensive compression test on all Silesia files"""
        print("🚀 MMH-RS COMPRESSION TEST ON REAL SILESIA CORPUS")
        print("=" * 80)
        print("Testing real-world compression performance on diverse dataset")
        print()
        
        # Get Silesia files
        files = self.get_silesia_files()
        print(f"📁 Found {len(files)} files in Silesia Corpus")
        
        total_original_size = sum(f.stat().st_size for f in files)
        total_original_mb = total_original_size / (1024 * 1024)
        print(f"📊 Total dataset size: {total_original_mb:.2f} MB")
        print()
        
        # Test each file
        for file_path in files:
            result = self.test_file_compression(file_path)
            self.results.append(result)
        
        # Generate comprehensive report
        self.print_comprehensive_report()
        
        # Save results
        self.save_test_results()
    
    def print_comprehensive_report(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE SILESIA CORPUS COMPRESSION REPORT")
        print("=" * 80)
        
        # Overall statistics
        total_files = len(self.results)
        total_original_size = sum(r.file_size for r in self.results)
        total_original_mb = total_original_size / (1024 * 1024)
        
        print(f"\n📁 OVERVIEW:")
        print(f"   Files tested: {total_files}")
        print(f"   Total original size: {total_original_mb:.2f} MB")
        
        # Performance by file
        print(f"\n📈 COMPRESSION PERFORMANCE BY FILE:")
        print("-" * 80)
        print(f"{'File Name':<15} {'Size (MB)':<10} {'Best Method':<8} {'Ratio':<8} {'Speed (MB/s)':<12}")
        print("-" * 80)
        
        for result in self.results:
            size_mb = result.file_size / (1024 * 1024)
            print(f"{result.file_name:<15} {size_mb:<10.2f} {result.best_compression:<8} {result.best_ratio:<8.2f} {result.best_speed:<12.1f}")
        
        # Method performance summary
        print(f"\n🔧 COMPRESSION METHOD PERFORMANCE:")
        print("-" * 50)
        
        methods = ['zstd', 'lz4', 'gzip', 'zlib']
        for method in methods:
            successful_tests = [r for r in self.results if method in r.compression_results and 'error' not in r.compression_results[method]]
            
            if successful_tests:
                avg_ratio = sum(r.compression_results[method]['compression_ratio'] for r in successful_tests) / len(successful_tests)
                avg_speed = sum(r.compression_results[method]['speed_mb_s'] for r in successful_tests) / len(successful_tests)
                total_compressed = sum(r.compression_results[method]['compressed_size'] for r in successful_tests)
                total_original = sum(r.file_size for r in successful_tests)
                overall_ratio = total_original / total_compressed if total_compressed > 0 else 0
                
                print(f"   {method.upper():6}: {avg_ratio:.2f}x avg, {overall_ratio:.2f}x overall, {avg_speed:.1f} MB/s avg")
        
        # File type insights
        print(f"\n💡 COMPRESSION INSIGHTS:")
        print("-" * 50)
        
        # Find best and worst compressing files
        best_compressing = max(self.results, key=lambda x: x.best_ratio)
        worst_compressing = min(self.results, key=lambda x: x.best_ratio)
        
        print(f"   Best compressing file: {best_compressing.file_name} ({best_compressing.best_ratio:.2f}x)")
        print(f"   Worst compressing file: {worst_compressing.file_name} ({worst_compressing.best_ratio:.2f}x)")
        
        # Size vs compression correlation
        large_files = [r for r in self.results if r.file_size > 10 * 1024 * 1024]  # >10MB
        small_files = [r for r in self.results if r.file_size < 10 * 1024 * 1024]  # <10MB
        
        if large_files and small_files:
            large_avg_ratio = sum(r.best_ratio for r in large_files) / len(large_files)
            small_avg_ratio = sum(r.best_ratio for r in small_files) / len(small_files)
            
            print(f"   Large files (>10MB) avg ratio: {large_avg_ratio:.2f}x")
            print(f"   Small files (<10MB) avg ratio: {small_avg_ratio:.2f}x")
    
    def save_test_results(self, output_file: str = "silesia_corpus_test_results.json"):
        """Save test results to JSON file"""
        results_data = {
            'test_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'dataset': 'Silesia Corpus',
            'total_files': len(self.results),
            'total_original_size': sum(r.file_size for r in self.results),
            'results': [
                {
                    'file_name': r.file_name,
                    'file_size': r.file_size,
                    'compression_results': r.compression_results,
                    'best_compression': r.best_compression,
                    'best_ratio': r.best_ratio,
                    'best_speed': r.best_speed
                }
                for r in self.results
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n💾 Test results saved to: {output_file}")
        print(f"✅ Comprehensive Silesia Corpus compression test complete!")

def main():
    """Main test execution"""
    tester = SilesiaCorpusTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
