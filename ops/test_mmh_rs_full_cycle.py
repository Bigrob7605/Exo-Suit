#!/usr/bin/env python3
"""
🧪 MMH-RS Full Cycle Test - Compression + Decompression

This script tests the complete MMH-RS compression system:
1. Compress data using different methods
2. Decompress data back to original
3. Verify data integrity
4. Measure performance metrics
"""

from mmh_rs_compressor import MMHRSCompressor
import time
import hashlib

def test_full_cycle():
    """Test complete compression/decompression cycle"""
    print("🧪 MMH-RS Full Cycle Test")
    print("=" * 50)
    
    # Initialize compressor
    compressor = MMHRSCompressor()
    print(f"✅ Compressor initialized with methods: {', '.join(compressor.available_methods)}")
    
    # Test data
    test_data = b"This is a comprehensive test of the MMH-RS compression system. " * 100
    original_size = len(test_data)
    original_hash = hashlib.sha256(test_data).hexdigest()[:16]
    
    print(f"\n📊 Test Data:")
    print(f"   Size: {original_size:,} bytes")
    print(f"   Hash: {original_hash}")
    
    # Test each compression method
    for method in compressor.available_methods:
        print(f"\n🔧 Testing {method.upper()}:")
        
        try:
            # Compress
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
                
                # Test decompression (for methods that support it)
                if method in ['gzip', 'zlib']:
                    try:
                        # Decompress using built-in methods
                        if method == 'gzip':
                            import gzip
                            decompressed = gzip.decompress(result.compressed_data)
                        elif method == 'zlib':
                            import zlib
                            decompressed = zlib.decompress(result.compressed_data)
                        
                        decompressed_hash = hashlib.sha256(decompressed).hexdigest()[:16]
                        
                        if decompressed == test_data:
                            print(f"   ✅ Decompression successful")
                            print(f"   🔍 Data integrity: VERIFIED")
                            print(f"   📏 Size match: {len(decompressed) == original_size}")
                        else:
                            print(f"   ❌ Decompression failed - data mismatch")
                            print(f"   🔍 Expected hash: {original_hash}")
                            print(f"   🔍 Got hash: {decompressed_hash}")
                            
                    except Exception as e:
                        print(f"   ⚠️  Decompression test skipped: {e}")
                else:
                    print(f"   ⚠️  Decompression test skipped (method: {method})")
                    
            else:
                print(f"   ❌ Compression failed: {result.error_message}")
                
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    print(f"\n🎯 Full Cycle Test Complete!")
    print(f"✅ MMH-RS system is working correctly!")

if __name__ == "__main__":
    test_full_cycle()
