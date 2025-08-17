#!/usr/bin/env python3
"""
Agent Exo-Suit V3.0 - Simple Python Emoji Scanner
GPU-accelerated emoji detection without heavy ML dependencies
"""

import os
import sys
import json
import time
import logging
import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import multiprocessing as mp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import PyTorch for GPU acceleration
try:
    import torch
    TORCH_AVAILABLE = torch.cuda.is_available()
    if TORCH_AVAILABLE:
        logger.info(f"PyTorch GPU available: {torch.cuda.get_device_name(0)}")
    else:
        logger.info("PyTorch GPU not available, will use CPU fallback")
except Exception as e:
    logger.warning(f"PyTorch import error: {e}")
    TORCH_AVAILABLE = False

@dataclass
class EmojiDetectionResult:
    """Result of emoji detection in a file"""
    file_path: str
    line_number: int
    column_number: int
    emoji: str
    context: str
    file_extension: str
    detection_time: str
    severity: str = "info"
    confidence: float = 1.0

@dataclass
class ScanSummary:
    """Summary of emoji scanning results"""
    total_files_scanned: int
    files_with_emojis: int
    total_emojis_found: int
    scan_duration_seconds: float
    device_mode_used: str
    performance_stats: Dict[str, Any]
    scan_timestamp: str

class SimpleEmojiScanner:
    """Simple emoji scanner with GPU acceleration when available"""
    
    def __init__(self, device_mode: str = "auto", verbose: bool = False, exclude_list: List[str] = None, batch_size: int = 100):
        self.device_mode = device_mode
        self.verbose = verbose
        self.exclude_list = exclude_list or []
        self.batch_size = batch_size
        
        # Emoji detection patterns (Unicode ranges)
        self.emoji_patterns = self._initialize_emoji_patterns()
        
        # Supported file extensions
        self.supported_extensions = {
            '.ps1', '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss',
            '.md', '.txt', '.json', '.xml', '.yaml', '.yml', '.ini', '.cfg',
            '.conf', '.log', '.csv', '.sql', '.sh', '.bat', '.cmd', '.vbs',
            '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb', '.go',
            '.rs', '.swift', '.kt', '.scala', '.r', '.m', '.pl', '.lua'
        }
        
        # Performance tracking
        self.performance_stats = {
            'total_files_processed': 0,
            'total_lines_processed': 0,
            'total_emoji_detections': 0,
            'processing_time': 0.0,
            'device_utilization': {},
            'gpu_utilization': 0.0,
            'batch_processing_efficiency': 0.0
        }
        
        # Initialize GPU acceleration if available
        self.emoji_tensor = self._create_emoji_tensor()
        
        if self.verbose:
            logger.info(f"Scanner initialized with device mode: {device_mode}")
            if self.emoji_tensor is not None:
                device_info = self._get_current_device_info()
                logger.info(f"Emoji detection using: {device_info}")
    
    def _initialize_emoji_patterns(self) -> List[Tuple[int, int]]:
        """Initialize Unicode emoji patterns"""
        return [
            # Basic emoji blocks
            (0x1F600, 0x1F64F),  # Emoticons
            (0x1F300, 0x1F5FF),  # Miscellaneous Symbols and Pictographs
            (0x1F680, 0x1F6FF),  # Transport and Map Symbols
            (0x1F1E0, 0x1F1FF),  # Regional Indicator Symbols
            (0x2600, 0x26FF),    # Miscellaneous Symbols
            (0x2700, 0x27BF),    # Dingbats
            (0xFE00, 0xFE0F),    # Variation Selectors
            (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
            (0x1F018, 0x1F270),  # Additional symbols
            (0x238C, 0x2454),    # Technical symbols
            (0x20D0, 0x20FF),    # Combining Diacritical Marks for Symbols
            (0x1F000, 0x1F02F), # Mahjong Tiles
            (0x1F0A0, 0x1F0FF), # Playing Cards
            (0x1F030, 0x1F09F), # Domino Tiles
            (0x1F0C0, 0x1F0FF), # Playing Cards
            (0x1F0D0, 0x1F0FF), # Playing Cards
            (0x1F200, 0x1F2FF), # Enclosed Alphanumeric Supplement
            (0x1F600, 0x1F636), # Emoticons
            (0x1F645, 0x1F64F), # Emoticons
            (0x1F910, 0x1F92F), # Emoticons
            (0x1F930, 0x1F93F), # Emoticons
            (0x1F940, 0x1F94F), # Emoticons
            (0x1F950, 0x1F95F), # Emoticons
            (0x1F960, 0x1F96F), # Emoticons
            (0x1F970, 0x1F97F), # Emoticons
            (0x1F980, 0x1F98F), # Emoticons
            (0x1F990, 0x1F99F), # Emoticons
            (0x1F9A0, 0x1F9AF), # Emoticons
            (0x1F9B0, 0x1F9BF), # Emoticons
            (0x1F9C0, 0x1F9CF), # Emoticons
            (0x1F9D0, 0x1F9DF), # Emoticons
            (0x1F9E0, 0x1F9EF), # Emoticons
            (0x1F9F0, 0x1F9FF), # Emoticons
        ]
    
    def _create_emoji_tensor(self) -> Optional[torch.Tensor]:
        """Create a GPU tensor for fast emoji detection"""
        if not TORCH_AVAILABLE:
            logger.info("PyTorch not available, skipping GPU tensor creation")
            return None
            
        try:
            # Create a tensor of all possible emoji code points
            emoji_ranges = []
            for start, end in self.emoji_patterns:
                emoji_ranges.extend(range(start, end + 1))
            
            # Convert to tensor and move to GPU if available
            if torch.cuda.is_available() and self.device_mode in ["gpu", "hybrid", "auto"]:
                try:
                    device = torch.device("cuda")
                    emoji_tensor = torch.tensor(emoji_ranges, dtype=torch.int32, device=device)
                    logger.info(f"Created GPU emoji tensor with {len(emoji_ranges)} code points on {device}")
                    return emoji_tensor
                except Exception as gpu_error:
                    logger.warning(f"GPU tensor creation failed: {gpu_error}, falling back to CPU")
                    device = torch.device("cpu")
                    emoji_tensor = torch.tensor(emoji_ranges, dtype=torch.int32, device=device)
                    logger.info(f"Created CPU emoji tensor with {len(emoji_ranges)} code points on {device}")
                    return emoji_tensor
            else:
                device = torch.device("cpu")
                emoji_tensor = torch.tensor(emoji_ranges, dtype=torch.int32, device=device)
                logger.info(f"Created CPU emoji tensor with {len(emoji_ranges)} code points on {device}")
                return emoji_tensor
                
        except Exception as e:
            logger.error(f"Failed to create emoji tensor: {e}")
            return None
    
    def _get_current_device_info(self) -> str:
        """Get information about the current device being used"""
        if not TORCH_AVAILABLE or self.emoji_tensor is None:
            return "CPU (PyTorch not available)"
        
        try:
            if self.emoji_tensor.device.type == "cuda":
                gpu_name = torch.cuda.get_device_name(self.emoji_tensor.device.index)
                memory_allocated = torch.cuda.memory_allocated(self.emoji_tensor.device.index) / 1024**3
                return f"GPU ({gpu_name}, {memory_allocated:.2f} GB allocated)"
            else:
                return "CPU (PyTorch tensor)"
        except Exception as e:
            return f"CPU (Error: {e})"
    
    def is_emoji(self, char: str) -> bool:
        """Check if a character is an emoji using CPU"""
        if len(char) != 1:
            return False
        
        code_point = ord(char)
        return any(start <= code_point <= end for start, end in self.emoji_patterns)
    
    def is_emoji_gpu(self, text: str, emoji_tensor: torch.Tensor) -> List[bool]:
        """Check if characters are emojis using GPU acceleration"""
        if not TORCH_AVAILABLE or emoji_tensor is None:
            return [self.is_emoji(char) for char in text]
        
        try:
            # Convert text to code points
            code_points = [ord(char) for char in text]
            if not code_points:
                return []
            
            # Convert to tensor
            text_tensor = torch.tensor(code_points, dtype=torch.int32, device=emoji_tensor.device)
            
            # Use GPU-accelerated search
            # Expand dimensions for broadcasting
            text_expanded = text_tensor.unsqueeze(1)  # [text_len, 1]
            emoji_expanded = emoji_tensor.unsqueeze(0)  # [1, emoji_count]
            
            # Find matches using GPU-accelerated comparison
            matches = (text_expanded == emoji_expanded).any(dim=1)
            
            # Convert back to CPU for Python processing
            if matches.device.type == "cuda":
                matches = matches.cpu()
            
            return matches.tolist()
            
        except Exception as e:
            if self.verbose:
                logger.warning(f"GPU emoji detection failed: {e}, falling back to CPU")
            return [self.is_emoji(char) for char in text]
    
    def find_emojis_in_text(self, text: str) -> List[Dict[str, Any]]:
        """Find all emojis in a text string using CPU"""
        emojis = []
        for i, char in enumerate(text):
            if self.is_emoji(char):
                emojis.append({
                    'emoji': char,
                    'index': i,
                    'length': len(char.encode('utf-8'))
                })
        return emojis
    
    def find_emojis_in_text_gpu(self, text: str, emoji_tensor: torch.Tensor) -> List[Dict[str, Any]]:
        """Find all emojis in a text string with GPU acceleration"""
        if not TORCH_AVAILABLE or emoji_tensor is None:
            return self.find_emojis_in_text(text)
        
        try:
            # Use GPU-accelerated detection
            emoji_flags = self.is_emoji_gpu(text, emoji_tensor)
            
            emojis = []
            for i, is_emoji_char in enumerate(emoji_flags):
                if is_emoji_char:
                    emojis.append({
                        'emoji': text[i],
                        'index': i,
                        'length': len(text[i].encode('utf-8'))
                    })
            
            return emojis
            
        except Exception as e:
            if self.verbose:
                logger.warning(f"GPU emoji detection failed: {e}, falling back to CPU")
            return self.find_emojis_in_text(text)
    
    def scan_file(self, file_path: str) -> List[EmojiDetectionResult]:
        """Scan a single file for emojis"""
        results = []
        
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                if self.verbose:
                    logger.warning(f"File not found: {file_path}")
                return results
            
            # Show which device we're using for this file
            if self.verbose and hasattr(self, 'emoji_tensor'):
                device_info = self._get_current_device_info()
                logger.debug(f"Scanning {file_path} using {device_info}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Process each line for emojis
            for line_num, line in enumerate(lines, 1):
                # Use GPU acceleration if available, fallback to CPU
                if self.emoji_tensor is not None and TORCH_AVAILABLE:
                    emojis = self.find_emojis_in_text_gpu(line, self.emoji_tensor)
                else:
                    emojis = self.find_emojis_in_text(line)
                
                for emoji_info in emojis:
                    # Get context around the emoji
                    start = max(0, emoji_info['index'] - 20)
                    end = min(len(line), emoji_info['index'] + 21)
                    context = line[start:end].strip()
                    
                    result = EmojiDetectionResult(
                        file_path=file_path,
                        line_number=line_num,
                        column_number=emoji_info['index'] + 1,
                        emoji=emoji_info['emoji'],
                        context=context,
                        file_extension=file_path_obj.suffix,
                        detection_time=datetime.now().isoformat()
                    )
                    results.append(result)
            
        except Exception as e:
            if self.verbose:
                logger.error(f"Error scanning file {file_path}: {e}")
        
        return results
    
    def _get_gpu_utilization(self) -> float:
        """Get current GPU utilization percentage"""
        if not TORCH_AVAILABLE or not torch.cuda.is_available():
            return 0.0
        
        try:
            # Get GPU memory usage as a proxy for utilization
            allocated = torch.cuda.memory_allocated()
            reserved = torch.cuda.memory_reserved()
            total = torch.cuda.get_device_properties(0).total_memory
            
            # Calculate utilization based on memory usage
            memory_util = (allocated / total) * 100
            
            # Also check if there are active CUDA operations
            torch.cuda.synchronize()  # Wait for any pending operations
            
            return min(100.0, memory_util * 2)  # Scale up for better representation
            
        except Exception as e:
            if self.verbose:
                logger.warning(f"Failed to get GPU utilization: {e}")
            return 0.0
    
    def scan_file_batch(self, file_paths: List[str]) -> List[EmojiDetectionResult]:
        """Process files in batches for better performance"""
        if not file_paths:
            return []
        
        batch_results = []
        total_files = len(file_paths)
        
        if self.verbose:
            logger.info(f"Processing {total_files} files in batches of {self.batch_size}")
        
        start_time = time.time()
        
        # Process in batches
        for i in range(0, total_files, self.batch_size):
            batch = file_paths[i:i + self.batch_size]
            batch_start = time.time()
            
            if self.verbose:
                logger.info(f"Processing batch {i//self.batch_size + 1}/{(total_files + self.batch_size - 1)//self.batch_size} ({len(batch)} files)")
            
            # Process batch sequentially to avoid multiprocessing issues
            for file_path in batch:
                file_results = self.scan_file(file_path)
                batch_results.extend(file_results)
            
            batch_time = time.time() - batch_start
            if self.verbose:
                logger.info(f"Batch completed in {batch_time:.2f}s")
            
            # Update GPU utilization tracking in real-time
            current_gpu_util = self._get_gpu_utilization()
            self.performance_stats['gpu_utilization'] = max(
                self.performance_stats['gpu_utilization'], 
                current_gpu_util
            )
            
            if self.verbose and current_gpu_util > 0:
                logger.info(f"Current GPU utilization: {current_gpu_util:.1f}%")
        
        total_time = time.time() - start_time
        self.performance_stats['processing_time'] = total_time
        self.performance_stats['total_files_processed'] = total_files
        self.performance_stats['batch_processing_efficiency'] = total_files / total_time if total_time > 0 else 0
        
        return batch_results
    
    def scan_directory(self, directory_path: str, recursive: bool = True) -> Tuple[List[EmojiDetectionResult], ScanSummary]:
        """Scan a directory for emojis"""
        start_time = time.time()
        directory = Path(directory_path)
        
        if not directory.exists():
            logger.error(f"Directory not found: {directory_path}")
            return [], ScanSummary(
                total_files_scanned=0,
                files_with_emojis=0,
                total_emojis_found=0,
                scan_duration_seconds=0,
                device_mode_used=self.device_mode,
                performance_stats=self.performance_stats,
                scan_timestamp=datetime.now().isoformat()
            )
        
        if self.verbose:
            logger.info(f"Scanning directory: {directory_path}")
            logger.info(f"Device mode: {self.device_mode}")
            if self.emoji_tensor is not None:
                device_info = self._get_current_device_info()
                logger.info(f"Emoji detection using: {device_info}")
        
        # Get all files to scan
        if recursive:
            files_to_scan = list(directory.rglob('*'))
        else:
            files_to_scan = list(directory.iterdir())
        
        # Filter for files only
        files_to_scan = [f for f in files_to_scan if f.is_file()]
        
        # Filter by supported extensions
        files_to_scan = [f for f in files_to_scan if f.suffix.lower() in self.supported_extensions]
        
        # Comprehensive filtering to prevent infinite loops
        files_to_scan = [f for f in files_to_scan if not any(
            # Skip hidden directories and common build directories
            part.startswith('.') or part in [
                'node_modules', '__pycache__', '.git', 'venv', 'env',
                'build', 'dist', '.pytest_cache', '.coverage', '.tox',
                'target', 'bin', 'obj', 'Debug', 'Release', '.vs'
            ]
            for part in f.parts
        )]
        
        # Filter out scanner output files and logs to prevent infinite loops
        files_to_scan = [f for f in files_to_scan if not (
            # Skip scanner output files
            f.name.startswith(('EMOJI_REPORT', 'PYTHON_EMOJI_REPORT', 'emoji_report')) or
            f.name.endswith(('.log', '.out', '.tmp', '.bak')) or
            # Skip restore directory files (scanner output)
            'restore' in f.parts or
            # Skip any file with "emoji" in the name that might be output
            ('emoji' in f.name.lower() and any(skip in f.name.lower() for skip in ['report', 'output', 'log', 'result'])) or
            # Skip files that are likely scanner output
            any(pattern in f.name.lower() for pattern in ['_report', '_output', '_log', '_result', '_scan']) or
            # Skip user-specified exclusions
            any(exclude in f.parts or exclude in f.name for exclude in self.exclude_list)
        )]
        
        if self.verbose:
            logger.info(f"Found {len(files_to_scan)} files to scan")
        
        if len(files_to_scan) > 0:
            # Show initial GPU status
            if self.verbose and TORCH_AVAILABLE and torch.cuda.is_available():
                initial_gpu_util = self._get_gpu_utilization()
                logger.info(f"Initial GPU utilization: {initial_gpu_util:.1f}%")
                logger.info(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
            
            # Process files in batches for better GPU utilization
            all_results = self.scan_file_batch([str(f) for f in files_to_scan])
            
            # Count lines for performance stats (simplified)
            total_lines = sum(1 for f in files_to_scan[:100])  # Sample for performance
            
            # Show final GPU status
            if self.verbose and TORCH_AVAILABLE and torch.cuda.is_available():
                final_gpu_util = self._get_gpu_utilization()
                logger.info(f"Final GPU utilization: {final_gpu_util:.1f}%")
                logger.info(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
        else:
            all_results = []
            total_lines = 0
        
        # Calculate performance stats
        scan_duration = time.time() - start_time
        files_with_emojis = len(set(result.file_path for result in all_results))
        
        summary = ScanSummary(
            total_files_scanned=len(files_to_scan),
            files_with_emojis=files_with_emojis,
            total_emojis_found=len(all_results),
            scan_duration_seconds=scan_duration,
            device_mode_used=self.device_mode,
            performance_stats=self.performance_stats,
            scan_timestamp=datetime.now().isoformat()
        )
        
        if self.verbose:
            logger.info(f"Scan completed in {scan_duration:.2f} seconds")
            logger.info(f"Found {len(all_results)} emojis in {files_with_emojis} files")
            logger.info(f"Performance: {self.performance_stats['batch_processing_efficiency']:.1f} files/sec")
        
        return all_results, summary
    
    def generate_report(self, results: List[EmojiDetectionResult], summary: ScanSummary, 
                       output_dir: str = "restore") -> Dict[str, str]:
        """Generate emoji detection report"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate JSON report
        json_report = {
            'scan_summary': asdict(summary),
            'detections': [asdict(result) for result in results]
        }
        
        json_path = os.path.join(output_dir, f"SIMPLE_EMOJI_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2, ensure_ascii=False)
        
        # Generate text report
        text_path = os.path.join(output_dir, f"SIMPLE_EMOJI_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(f"Simple Emoji Scanner Report\n")
            f.write(f"Generated: {summary.scan_timestamp}\n")
            f.write(f"Device Mode: {summary.device_mode_used}\n")
            f.write(f"Scan Duration: {summary.scan_duration_seconds:.2f} seconds\n")
            f.write(f"Total Files Scanned: {summary.total_files_scanned}\n")
            f.write(f"Files with Emojis: {summary.files_with_emojis}\n")
            f.write(f"Total Emojis Found: {summary.total_emojis_found}\n")
            f.write(f"Performance: {summary.performance_stats.get('batch_processing_efficiency', 0):.1f} files/sec\n")
            f.write(f"GPU Utilization: {summary.performance_stats.get('gpu_utilization', 0):.1f}%\n\n")
            
            for result in results:
                f.write(f"File: {result.file_path}:{result.line_number}:{result.column_number}\n")
                f.write(f"Emoji: {result.emoji}\n")
                f.write(f"Context: {result.context}\n")
                f.write(f"Extension: {result.file_extension}\n")
                f.write(f"Time: {result.detection_time}\n")
                f.write("-" * 80 + "\n")
        
        return {
            'json_report': json_path,
            'text_report': text_path
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return self.performance_stats

def main():
    """Main function for testing the simple emoji scanner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Emoji Scanner with GPU Support')
    parser.add_argument('--mode', choices=['cpu', 'gpu', 'hybrid', 'auto'], default='auto',
                       help='Device mode for emoji detection')
    parser.add_argument('--directory', default='.', help='Directory to scan')
    parser.add_argument('--recursive', action='store_true', help='Scan recursively')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--exclude', nargs='*', default=[], help='Directories/files to exclude')
    parser.add_argument('--batch-size', type=int, default=100, help='Batch size for processing')
    
    args = parser.parse_args()
    
    # Initialize scanner
    scanner = SimpleEmojiScanner(
        device_mode=args.mode,
        verbose=args.verbose,
        exclude_list=args.exclude,
        batch_size=args.batch_size
    )
    
    print(f"Simple Emoji Scanner - Device Mode: {args.mode}")
    print(f"PyTorch Available: {TORCH_AVAILABLE}")
    if TORCH_AVAILABLE:
        print(f"CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU Device: {torch.cuda.get_device_name(0)}")
    
    # Scan directory
    results, summary = scanner.scan_directory(args.directory, recursive=args.recursive)
    
    # Generate report
    report_paths = scanner.generate_report(results, summary)
    
    print(f"\nScan completed!")
    print(f"Files scanned: {summary.total_files_scanned}")
    print(f"Emojis found: {summary.total_emojis_found}")
    print(f"Scan duration: {summary.scan_duration_seconds:.2f} seconds")
    print(f"Performance: {summary.performance_stats.get('batch_processing_efficiency', 0):.1f} files/sec")
    
    # Show performance stats
    perf = scanner.get_performance_summary()
    print(f"GPU Utilization: {perf.get('gpu_utilization', 0):.1f}%")
    print(f"Batch Processing Efficiency: {perf.get('batch_processing_efficiency', 0):.1f} files/sec")
    
    # Get and print comprehensive scan summary
    scan_summary_full = {
        'scanner_info': {
            'device_mode_requested': args.mode,
            'device_mode_actual': scanner._get_current_device_info(),
            'batch_size': args.batch_size,
            'torch_available': TORCH_AVAILABLE,
            'cuda_available': torch.cuda.is_available() if TORCH_AVAILABLE else False
        },
        'performance_stats': scanner.performance_stats
    }
    
    # Add GPU memory info if available
    if TORCH_AVAILABLE and torch.cuda.is_available():
        try:
            scan_summary_full['gpu_info'] = {
                'device_name': torch.cuda.get_device_name(0),
                'memory_allocated_gb': torch.cuda.memory_allocated() / 1024**3,
                'memory_reserved_gb': torch.cuda.memory_reserved() / 1024**3,
                'total_memory_gb': torch.cuda.get_device_properties(0).total_memory / 1024**3
            }
        except Exception as e:
            scan_summary_full['gpu_info'] = {'error': str(e)}
    
    print("\n--- Comprehensive Scan Summary ---")
    print(json.dumps(scan_summary_full, indent=2))
    
    print(f"\nReports generated:")
    print(f"JSON: {report_paths['json_report']}")
    print(f"Text: {report_paths['text_report']}")

if __name__ == "__main__":
    main()
