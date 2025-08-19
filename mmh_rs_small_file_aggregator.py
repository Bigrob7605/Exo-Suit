#!/usr/bin/env python3
"""
🚀 MMH-RS SMALL FILE AGGREGATOR - BYPASS SMALL FILE TAX

This system aggregates small files into a single bundle before compression,
bypassing the inefficiency of compressing many small files individually.

Strategy:
1. Collect all small files (< threshold size)
2. Bundle them into a single aggregated file
3. Compress the aggregated bundle with MMH-RS
4. Achieve real compression ratios on the bundle
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
import logging

# Import the MMH-RS compressor
from mmh_rs_compressor import MMHRSCompressor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FileInfo:
    """Information about a file to be aggregated"""
    path: str
    size: int
    hash: str
    content: bytes

@dataclass
class AggregationResult:
    """Result of file aggregation and compression"""
    total_files: int
    total_size: int
    aggregated_size: int
    compressed_size: int
    compression_ratio: float
    processing_time: float
    success: bool
    error_message: Optional[str] = None

class SmallFileAggregator:
    """Aggregates small files to bypass compression inefficiency"""
    
    def __init__(self, max_file_size: int = 1024, compression_method: str = 'zstd'):
        """
        Initialize the aggregator
        
        Args:
            max_file_size: Maximum size (bytes) for a file to be considered "small"
            compression_method: MMH-RS compression method to use
        """
        self.max_file_size = max_file_size
        self.compression_method = compression_method
        self.mmh_compressor = MMHRSCompressor()
        
        logger.info(f"Small File Aggregator initialized with max_file_size={max_file_size} bytes")
        logger.info(f"Using MMH-RS compression method: {compression_method}")
    
    def scan_directory(self, directory_path: Union[str, Path]) -> List[FileInfo]:
        """Scan directory for small files to aggregate"""
        directory = Path(directory_path)
        small_files = []
        
        logger.info(f"Scanning directory: {directory}")
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.stat().st_size <= self.max_file_size:
                try:
                    content = file_path.read_bytes()
                    file_hash = hashlib.sha256(content).hexdigest()
                    
                    file_info = FileInfo(
                        path=str(file_path.relative_to(directory)),
                        size=len(content),
                        hash=file_hash,
                        content=content
                    )
                    small_files.append(file_info)
                    
                    logger.debug(f"Found small file: {file_info.path} ({file_info.size} bytes)")
                    
                except Exception as e:
                    logger.warning(f"Could not read file {file_path}: {e}")
        
        logger.info(f"Found {len(small_files)} small files to aggregate")
        return small_files
    
    def create_aggregated_bundle(self, files: List[FileInfo]) -> bytes:
        """Create a single bundle containing all small files"""
        bundle_data = {
            'metadata': {
                'version': '1.0',
                'created_at': time.time(),
                'total_files': len(files),
                'compression_method': self.compression_method
            },
            'files': []
        }
        
        # Add file information and content
        for file_info in files:
            bundle_data['files'].append({
                'path': file_info.path,
                'size': file_info.size,
                'hash': file_info.hash,
                'content': file_info.content.hex()  # Convert bytes to hex string
            })
        
        # Convert to JSON and encode
        bundle_json = json.dumps(bundle_data, indent=2)
        bundle_bytes = bundle_json.encode('utf-8')
        
        logger.info(f"Created aggregated bundle: {len(bundle_bytes)} bytes")
        return bundle_bytes
    
    def compress_bundle(self, bundle_data: bytes) -> AggregationResult:
        """Compress the aggregated bundle using MMH-RS"""
        start_time = time.time()
        
        try:
            # Compress using MMH-RS
            compression_result = self.mmh_compressor.compress(bundle_data, self.compression_method)
            
            if not compression_result.success:
                return AggregationResult(
                    total_files=0,
                    total_size=0,
                    aggregated_size=len(bundle_data),
                    compressed_size=len(bundle_data),
                    compression_ratio=1.0,
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message=compression_result.error_message
                )
            
            processing_time = time.time() - start_time
            
            return AggregationResult(
                total_files=0,  # Will be set by caller
                total_size=0,   # Will be set by caller
                aggregated_size=len(bundle_data),
                compressed_size=compression_result.compressed_size,
                compression_ratio=compression_result.compression_ratio,
                processing_time=processing_time,
                success=True
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return AggregationResult(
                total_files=0,
                total_size=0,
                aggregated_size=len(bundle_data),
                compressed_size=len(bundle_data),
                compression_ratio=1.0,
                processing_time=processing_time,
                success=False,
                error_message=str(e)
            )
    
    def aggregate_and_compress(self, directory_path: Union[str, Path]) -> AggregationResult:
        """Main method: scan, aggregate, and compress small files"""
        start_time = time.time()
        
        try:
            # Step 1: Scan for small files
            small_files = self.scan_directory(directory_path)
            
            if not small_files:
                return AggregationResult(
                    total_files=0,
                    total_size=0,
                    aggregated_size=0,
                    compressed_size=0,
                    compression_ratio=1.0,
                    processing_time=time.time() - start_time,
                    success=True,
                    error_message="No small files found to aggregate"
                )
            
            # Step 2: Create aggregated bundle
            bundle_data = self.create_aggregated_bundle(small_files)
            
            # Step 3: Compress the bundle
            compression_result = self.compress_bundle(bundle_data)
            
            # Update with file information
            compression_result.total_files = len(small_files)
            compression_result.total_size = sum(f.size for f in small_files)
            
            total_time = time.time() - start_time
            compression_result.processing_time = total_time
            
            logger.info(f"Small file aggregation complete:")
            logger.info(f"  Files processed: {compression_result.total_files}")
            logger.info(f"  Total original size: {compression_result.total_size} bytes")
            logger.info(f"  Bundle size: {compression_result.aggregated_size} bytes")
            logger.info(f"  Compressed size: {compression_result.compressed_size} bytes")
            logger.info(f"  Compression ratio: {compression_result.compression_ratio:.2f}x")
            logger.info(f"  Processing time: {compression_result.processing_time:.3f}s")
            
            return compression_result
            
        except Exception as e:
            total_time = time.time() - start_time
            return AggregationResult(
                total_files=0,
                total_size=0,
                aggregated_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                processing_time=total_time,
                success=False,
                error_message=str(e)
            )
    
    def save_compressed_bundle(self, directory_path: Union[str, Path], 
                             output_path: Optional[Union[str, Path]] = None) -> str:
        """Save the compressed bundle to disk"""
        if output_path is None:
            timestamp = int(time.time())
            output_path = f"mmh_rs_bundle_{timestamp}.mmh"
        
        try:
            # Perform aggregation and compression
            result = self.aggregate_and_compress(directory_path)
            
            if not result.success:
                raise Exception(f"Aggregation failed: {result.error_message}")
            
            # Create the bundle data
            small_files = self.scan_directory(directory_path)
            bundle_data = self.create_aggregated_bundle(small_files)
            
            # Compress and save
            compressed_data = self.mmh_compressor.compress(bundle_data, self.compression_method)
            
            if not compressed_data.success:
                raise Exception(f"Compression failed: {compressed_data.error_message}")
            
            # Save compressed bundle
            with open(output_path, 'wb') as f:
                f.write(compressed_data.compressed_data)
            
            logger.info(f"Compressed bundle saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to save compressed bundle: {e}")
            raise

def main():
    """Demo the small file aggregator"""
    print("🚀 MMH-RS SMALL FILE AGGREGATOR - BYPASS SMALL FILE TAX")
    print("=" * 70)
    
    # Initialize aggregator
    aggregator = SmallFileAggregator(max_file_size=1024, compression_method='zstd')
    
    # Test with current directory
    current_dir = Path('.')
    
    print(f"Scanning directory: {current_dir.absolute()}")
    print(f"Max file size: {aggregator.max_file_size} bytes")
    print(f"Compression method: {aggregator.compression_method}")
    print()
    
    # Perform aggregation and compression
    result = aggregator.aggregate_and_compress(current_dir)
    
    if result.success:
        print("✅ SMALL FILE AGGREGATION SUCCESSFUL!")
        print("-" * 50)
        print(f"Files processed: {result.total_files}")
        print(f"Total original size: {result.total_size:,} bytes")
        print(f"Bundle size: {result.aggregated_size:,} bytes")
        print(f"Compressed size: {result.compressed_size:,} bytes")
        print(f"Compression ratio: {result.compression_ratio:.2f}x")
        print(f"Processing time: {result.processing_time:.3f}s")
        
        if result.compression_ratio > 1.0:
            print(f"🎉 REAL COMPRESSION ACHIEVED: {result.compression_ratio:.2f}x")
        else:
            print(f"⚠️ No compression achieved (ratio: {result.compression_ratio:.2f}x)")
    else:
        print("❌ AGGREGATION FAILED!")
        print(f"Error: {result.error_message}")

if __name__ == "__main__":
    main()
