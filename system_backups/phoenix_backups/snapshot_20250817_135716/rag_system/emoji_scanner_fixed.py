#!/usr/bin/env python3
"""
Agent Exo-Suit V5.0 - Fixed Emoji Scanner
Eliminates multiprocessing overhead and reuses GPU instances for maximum performance
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
import torch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check PyTorch availability once at import
try:
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

class FixedEmojiScanner:
    """High-performance emoji scanner without multiprocessing overhead"""
    
    def __init__(self, device_mode: str = "auto", verbose: bool = False, exclude_list: List[str] = None, batch_size: int = 100):
        self.device_mode = device_mode
        self.verbose = verbose
        self.exclude_list = exclude_list or []
        self.batch_size = batch_size
        
        # Initialize GPU emoji detection tensor once
        self.emoji_tensor = None
        self.device = None
        self._initialize_gpu_emoji_detection()
        
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
    
    def _initialize_gpu_emoji_detection(self):
        """Initialize GPU emoji detection tensor once"""
        if self.device_mode == "cpu":
            logger.info("CPU mode forced by user")
            self.device = torch.device('cpu')
            self.emoji_tensor = None
            return
            
        if TORCH_AVAILABLE and torch.cuda.is_available():
            try:
                self.device = torch.device('cuda:0')
                logger.info("Initializing GPU emoji detection...")
                
                # Create emoji detection tensor on GPU
                emoji_chars = self._get_emoji_unicode_chars()
                self.emoji_tensor = torch.tensor(emoji_chars, device=self.device, dtype=torch.int32)
                
                logger.info(f"Created GPU emoji tensor with {len(emoji_chars)} code points on {self.device}")
                
                # Test GPU memory allocation
                test_tensor = torch.zeros(1000, device=self.device)
                gpu_memory = torch.cuda.memory_allocated() / 1024**3
                logger.info(f"GPU memory test successful: {gpu_memory:.3f} GB allocated")
                del test_tensor
                torch.cuda.empty_cache()
                
            except Exception as e:
                logger.warning(f"GPU initialization failed: {e}, falling back to CPU")
                self.device = torch.device('cpu')
                self.emoji_tensor = None
        else:
            logger.info("Using CPU emoji detection")
            self.device = torch.device('cpu')
            self.emoji_tensor = None
    
    def _get_emoji_unicode_chars(self) -> List[int]:
        """Get list of emoji Unicode code points"""
        emoji_ranges = [
            (0x1F600, 0x1F64F),  # Emoticons
            (0x1F300, 0x1F5FF),  # Miscellaneous Symbols and Pictographs
            (0x1F680, 0x1F6FF),  # Transport and Map Symbols
            (0x1F1E0, 0x1F1FF),  # Regional Indicator Symbols
            (0x2600, 0x26FF),    # Miscellaneous Symbols
            (0x2700, 0x27BF),    # Dingbats
            (0xFE00, 0xFE0F),    # Variation Selectors
            (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
            (0x1F018, 0x1F270),  # Various symbols
        ]
        
        emoji_chars = []
        for start, end in emoji_ranges:
            emoji_chars.extend(range(start, end + 1))
        
        return emoji_chars
    
    def find_emojis_in_text_gpu(self, text: str, emoji_tensor: torch.Tensor) -> List[Dict[str, Any]]:
        """Find emojis in text using GPU acceleration - FIXED VERSION"""
        if not text or emoji_tensor is None:
            return []
        
        try:
            # Process text in chunks to avoid memory issues
            chunk_size = 1000  # Process 1000 characters at a time
            matches = []
            
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                
                # Convert chunk to Unicode code points
                text_codes = torch.tensor([ord(c) for c in chunk], device=self.device, dtype=torch.int32)
                
                # Use efficient GPU operations - find all matches at once
                # Create a mask for each character in the chunk
                mask = torch.zeros(len(chunk), dtype=torch.bool, device=self.device)
                
                # Check each character against emoji tensor efficiently
                for j, code in enumerate(text_codes):
                    # Use torch.any for efficient comparison
                    if torch.any(emoji_tensor == code):
                        mask[j] = True
                
                # Get indices where emojis were found
                emoji_indices = torch.where(mask)[0]
                
                # Convert back to Python and add to matches
                for idx in emoji_indices:
                    global_idx = i + idx.item()
                    matches.append({
                        'emoji': text[global_idx],
                        'index': global_idx
                    })
                
                # Clear GPU memory for this chunk
                del text_codes, mask, emoji_indices
                torch.cuda.empty_cache()
            
            return matches
            
        except Exception as e:
            logger.warning(f"GPU emoji detection failed: {e}, falling back to CPU")
            return self.find_emojis_in_text(text)
    
    def find_emojis_in_text(self, text: str) -> List[Dict[str, Any]]:
        """Find emojis in text using CPU fallback"""
        if not text:
            return []
        
        matches = []
        for i, char in enumerate(text):
            if self._is_emoji(char):
                matches.append({
                    'emoji': char,
                    'index': i
                })
        
        return matches
    
    def _is_emoji(self, char: str) -> bool:
        """Check if a character is an emoji using CPU"""
        try:
            if unicodedata.category(char) in ['So', 'Sk']:
                return True
            
            code_point = ord(char)
            emoji_ranges = [
                (0x1F600, 0x1F64F), (0x1F300, 0x1F5FF), (0x1F680, 0x1F6FF),
                (0x1F1E0, 0x1F1FF), (0x2600, 0x26FF), (0x2700, 0x27BF),
                (0xFE00, 0xFE0F), (0x1F900, 0x1F9FF), (0x1F018, 0x1F270)
            ]
            
            for start, end in emoji_ranges:
                if start <= code_point <= end:
                    return True
            
            return False
        except:
            return False
    
    def scan_file(self, file_path: str) -> List[EmojiDetectionResult]:
        """Scan a single file for emojis with timeout protection"""
        results = []
        
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return results
            
            # Check file size - skip very large files that might cause hanging
            file_size = file_path_obj.stat().st_size
            if file_size > 10 * 1024 * 1024:  # Skip files > 10MB
                if self.verbose:
                    logger.warning(f"Skipping large file {file_path} ({file_size / 1024 / 1024:.1f} MB)")
                return results
            
            # Read file content with timeout protection
            start_time = time.time()
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            if self.verbose:
                logger.info(f"Processing {file_path} ({len(lines)} lines, {file_size / 1024:.1f} KB)")
            
            # Process each line for emojis with progress tracking
            for line_num, line in enumerate(lines, 1):
                # Check for timeout every 100 lines
                if line_num % 100 == 0:
                    elapsed = time.time() - start_time
                    if elapsed > 30:  # 30 second timeout per file
                        logger.warning(f"Timeout processing {file_path}, stopping at line {line_num}")
                        break
                
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
            
            if self.verbose:
                elapsed = time.time() - start_time
                logger.info(f"Completed {file_path} in {elapsed:.2f}s, found {len(results)} emojis")
            
        except Exception as e:
            if self.verbose:
                logger.error(f"Error scanning file {file_path}: {e}")
        
        return results
    
    def scan_directory(self, directory_path: str, recursive: bool = True) -> Tuple[List[EmojiDetectionResult], ScanSummary]:
        """Scan a directory for emojis with high performance"""
        start_time = time.time()
        
        # Find all files to scan
        files_to_scan = []
        directory = Path(directory_path)
        
        if recursive:
            for ext in self.supported_extensions:
                files_to_scan.extend(directory.rglob(f"*{ext}"))
        else:
            for ext in self.supported_extensions:
                files_to_scan.extend(directory.glob(f"*{ext}"))
        
        # Get current script path to exclude it
        current_script = Path(__file__).resolve()
        
        # Filter files
        files_to_scan = [f for f in files_to_scan if not (
            f.resolve() == current_script or
            f.name.startswith(('EMOJI_REPORT', 'PYTHON_EMOJI_REPORT', 'emoji_report')) or
            f.name.endswith(('.log', '.out', '.tmp', '.bak')) or
            'restore' in f.parts or
            any(exclude in f.parts or exclude in f.name for exclude in self.exclude_list)
        )]
        
        if self.verbose:
            logger.info(f"Found {len(files_to_scan)} files to scan after filtering")
            if len(files_to_scan) > 0:
                logger.info(f"Sample files to scan: {[f.name for f in files_to_scan[:5]]}")
        
        # Process files sequentially but efficiently
        all_results = []
        files_with_emojis = 0
        total_lines = 0
        
        if len(files_to_scan) > 0:
            # Show initial GPU status
            if self.verbose and TORCH_AVAILABLE and torch.cuda.is_available():
                initial_gpu_util = torch.cuda.memory_allocated() / 1024**3
                logger.info(f"Initial GPU memory allocated: {initial_gpu_util:.2f} GB")
            
            # Process files efficiently
            for i, file_path in enumerate(files_to_scan):
                if self.verbose and i % 100 == 0:
                    logger.info(f"Processing file {i+1}/{len(files_to_scan)}: {file_path.name}")
                
                file_results = self.scan_file(str(file_path))
                if file_results:
                    all_results.extend(file_results)
                    files_with_emojis += 1
                
                # Count lines for performance stats
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        total_lines += sum(1 for _ in f)
                except:
                    pass
            
            # Show final GPU status
            if self.verbose and TORCH_AVAILABLE and torch.cuda.is_available():
                final_gpu_util = torch.cuda.memory_allocated() / 1024**3
                logger.info(f"Final GPU memory allocated: {final_gpu_util:.2f} GB")
        
        # Calculate performance stats
        scan_duration = time.time() - start_time
        
        # Update performance stats
        self.performance_stats.update({
            'total_files_processed': len(files_to_scan),
            'total_lines_processed': total_lines,
            'total_emoji_detections': len(all_results),
            'processing_time': scan_duration,
            'batch_processing_efficiency': len(files_to_scan) / max(1, scan_duration)
        })
        
        summary = ScanSummary(
            total_files_scanned=len(files_to_scan),
            files_with_emojis=files_with_emojis,
            total_emojis_found=len(all_results),
            scan_duration_seconds=scan_duration,
            device_mode_used=self._get_current_device_info(),
            performance_stats=self.performance_stats,
            scan_timestamp=datetime.now().isoformat()
        )
        
        return all_results, summary
    
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
    
    def generate_report(self, results: List[EmojiDetectionResult], summary: ScanSummary, output_dir: str = "restore") -> Dict[str, str]:
        """Generate emoji detection report"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate JSON report
        json_path = os.path.join(output_dir, f"PYTHON_EMOJI_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "Summary": asdict(summary),
                "Detections": [asdict(result) for result in results]
            }, f, indent=2, ensure_ascii=False)
        
        # Generate text report
        text_path = os.path.join(output_dir, f"PYTHON_EMOJI_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write("PYTHON EMOJI SCANNER REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write("SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Files Scanned: {summary.total_files_scanned}\n")
            f.write(f"Files with Emojis: {summary.files_with_emojis}\n")
            f.write(f"Total Emojis Found: {summary.total_emojis_found}\n")
            f.write(f"Scan Duration: {summary.scan_duration_seconds:.2f} seconds\n")
            f.write(f"Device Mode: {summary.device_mode_used}\n")
            f.write(f"Scan Timestamp: {summary.scan_timestamp}\n\n")
            
            f.write("DETECTIONS\n")
            f.write("-" * 20 + "\n")
            
            # Group by file
            files_with_emojis = {}
            for result in results:
                if result.file_path not in files_with_emojis:
                    files_with_emojis[result.file_path] = []
                files_with_emojis[result.file_path].append(result)
            
            for file_path, file_results in files_with_emojis.items():
                f.write(f"File: {file_path}\n")
                for result in file_results:
                    f.write(f"Line: {result.line_number}, Column: {result.column_number}\n")
                    f.write(f"Emoji: {result.emoji}\n")
                    f.write(f"Context: {result.context}\n")
                    f.write("-" * 40 + "\n")
                f.write("\n")
        
        return {
            "json": json_path,
            "text": text_path
        }

def main():
    """Main function for testing the fixed emoji scanner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fixed Python Emoji Scanner with GPU acceleration")
    parser.add_argument("--mode", choices=["cpu", "gpu", "auto"], default="auto",
                       help="Device mode to use")
    parser.add_argument("--directory", default=".", help="Directory to scan")
    parser.add_argument("--recursive", action="store_true", default=True, help="Scan recursively")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--output", default="restore", help="Output directory for reports")
    parser.add_argument("--exclude", nargs="*", default=[], 
                       help="Additional directories or files to exclude")
    parser.add_argument("--batch-size", type=int, default=100,
                       help="Batch size for processing files")
    
    args = parser.parse_args()
    
    # Initialize scanner
    scanner = FixedEmojiScanner(device_mode=args.mode, verbose=args.verbose, 
                               exclude_list=args.exclude, batch_size=args.batch_size)
    
    # Perform scan
    print(f"Starting fixed emoji scan in {args.directory} with {args.mode} mode...")
    print(f"Batch size: {args.batch_size}")
    if args.exclude:
        print(f"Excluding: {', '.join(args.exclude)}")
    
    results, summary = scanner.scan_directory(args.directory, recursive=args.recursive)
    
    # Generate reports
    report_paths = scanner.generate_report(results, summary, args.output)
    
    # Print summary
    print(f"\nScan Complete!")
    print(f"Files Scanned: {summary.total_files_scanned}")
    print(f"Files with Emojis: {summary.files_with_emojis}")
    print(f"Total Emojis Found: {summary.total_emojis_found}")
    print(f"Scan Duration: {summary.scan_duration_seconds:.2f} seconds")
    print(f"Device Mode Used: {summary.device_mode_used}")
    print(f"Performance: {summary.performance_stats['batch_processing_efficiency']:.1f} files/sec")
    print(f"Reports saved to: {report_paths['json']} and {report_paths['text']}")

if __name__ == "__main__":
    main()
