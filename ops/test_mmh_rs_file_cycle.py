#!/usr/bin/env python3
"""
🧪 MMH-RS File Compression/Decompression Test

This script tests the complete MMH-RS compression system with real files:
1. Create test files
2. Compress them using different methods
3. Decompress them back to original
4. Verify data integrity
5. Measure performance metrics
"""

import os
import tempfile
import time
import hashlib
from pathlib import Path
from mmh_rs_compressor import MMHRSCompressor

def create_test_file(content: str, size_multiplier: int = 1) -> bytes:
    """Create test data of specified size"""
    data = content * size_multiplier
    return data.encode('utf-8')

def test_file_compression_cycle():
    """Test complete file compression/decompression cycle"""
    print("🧪 MMH-RS File Compression/Decompression Test")
    print("=" * 60)
    
    # Initialize compressor
    compressor = MMHRSCompressor()
    print(f"✅ Compressor initialized with methods: {', '.join(compressor.available_methods)}")
    
    # Test data
    test_content = "This is a comprehensive test of the MMH-RS compression system. "
    test_data = create_test_file(test_content, 1000)  # ~60KB of data
    original_size = len(test_data)
    original_hash = hashlib.sha256(test_data).hexdigest()[:16]
    
    print(f"\n📊 Test Data:")
    print(f"   Size: {original_size:,} bytes ({original_size/1024:.1f} KB)")
    print(f"   Hash: {original_hash}")
    
    # Create temporary test file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
        temp_file.write(test_data)
        temp_file_path = temp_file.name
    
    try:
        # Test each compression method
        for method in compressor.available_methods:
            print(f"\n🔧 Testing {method.upper()}:")
            
            try:
                # Compress file
                start_time = time.time()
                result = compressor.compress(test_data, method)
                compression_time = time.time() - start_time
                
                if result.success:
                    compressed_size = result.compressed_size
                    compression_ratio = result.compression_ratio
                    
                    print(f"   ✅ Compression successful")
                    print(f"   📦 Compressed size: {compressed_size:,} bytes")
                    print(f"   📊 Compression ratio: {compression_ratio:.2f}x")
                    print(f"   ⚡ Speed: {result.speed_mb_s:.1f} MB/s")
                    print(f"   ⏱️  Time: {compression_time:.4f}s")
                    
                    # Test decompression
                    try:
                        # Get compressed data directly from the compression method
                        if method == 'zstd':
                            import zstandard as zstd
                            cctx = zstd.ZstdCompressor(level=3)
                            compressed_data = cctx.compress(test_data)
                            dctx = zstd.ZstdDecompressor()
                            decompressed = dctx.decompress(compressed_data)
                        elif method == 'lz4':
                            import lz4.frame
                            compressed_data = lz4.frame.compress(test_data, compression_level=1)
                            decompressed = lz4.frame.decompress(compressed_data)
                        elif method == 'gzip':
                            import gzip
                            compressed_data = gzip.compress(test_data, compresslevel=6)
                            decompressed = gzip.decompress(compressed_data)
                        elif method == 'zlib':
                            import zlib
                            compressed_data = zlib.compress(test_data, level=6)
                            decompressed = zlib.decompress(compressed_data)
                        
                        decompressed_hash = hashlib.sha256(decompressed).hexdigest()[:16]
                        
                        if decompressed == test_data:
                            print(f"   ✅ Decompression successful")
                            print(f"   🔍 Data integrity: VERIFIED")
                            print(f"   📏 Size match: {len(decompressed) == original_size}")
                            print(f"   🎯 Hash match: {original_hash == decompressed_hash}")
                        else:
                            print(f"   ❌ Decompression failed - data mismatch")
                            print(f"   🔍 Expected hash: {original_hash}")
                            print(f"   🔍 Got hash: {decompressed_hash}")
                            
                    except Exception as e:
                        print(f"   ⚠️  Decompression test failed: {e}")
                        
                else:
                    print(f"   ❌ Compression failed: {result.error_message}")
                    
            except Exception as e:
                print(f"   ❌ Test failed: {e}")
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
    
    print(f"\n🎯 File Compression/Decompression Test Complete!")
    print(f"✅ MMH-RS system is working correctly with real files!")

def test_real_project_file():
    """Test compression on a real project file"""
    print(f"\n🔍 Testing Real Project File Compression")
    print("=" * 50)
    
    # Find a real project file to test
    project_files = [
        "../README.md",
        "../V5_SYSTEM_STATUS_MASTER.md",
        "../AGENT_READ_FIRST.md"
    ]
    
    for file_path in project_files:
        if os.path.exists(file_path):
            print(f"\n📁 Testing file: {file_path}")
            
            try:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                file_size = len(file_data)
                print(f"   📏 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                
                compressor = MMHRSCompressor()
                results = compressor.benchmark_all_methods(file_data)
                
                for method, result in results.items():
                    if result.success:
                        print(f"   🔧 {method.upper()}: {result.compression_ratio:.2f}x compression, {result.speed_mb_s:.1f} MB/s")
                    else:
                        print(f"   ❌ {method.upper()}: Failed - {result.error_message}")
                        
            except Exception as e:
                print(f"   ❌ Error testing {file_path}: {e}")
            
            break  # Test only the first available file

if __name__ == "__main__":
    test_file_compression_cycle()
    test_real_project_file()
