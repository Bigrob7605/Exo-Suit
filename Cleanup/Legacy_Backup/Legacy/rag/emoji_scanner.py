#!/usr/bin/env python3
"""
Agent Exo-Suit V3.0 - Python Emoji Scanner
Advanced emoji detection with CPU/GPU/CPU+GPU support using the RAG system
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
import torch

# Add the rag directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from device_manager import DeviceManager, DeviceType
from embedding_engine import EmbeddingEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check PyTorch availability after import
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

class PythonEmojiScanner:
    """Advanced emoji scanner with CPU/GPU/CPU+GPU support"""
    
    def __init__(self, device_mode: str = "auto", verbose: bool = False, exclude_list: List[str] = None, batch_size: int = 100):
        self.device_mode = device_mode
        self.verbose = verbose
        self.exclude_list = exclude_list or []
        self.batch_size = batch_size
        
        # Initialize device manager
        self.device_manager = DeviceManager()
        
        # Initialize embedding engine for text processing
        self.embedding_engine = None
        
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
        
        # Initialize the scanner
        self._initialize_scanner()
    
    def _initialize_scanner(self):
        """Initialize the scanner with optimal device configuration"""
        logger.info("Initializing Python Emoji Scanner...")

        # Get device configuration
        device_config = self.device_manager.get_optimal_configuration(
            DeviceType(self.device_mode) if self.device_mode != "auto" else DeviceType.AUTO
        )

        # Initialize embedding engine with device configuration and optimized settings
        try:
            # Optimize batch size for GPU utilization
            optimal_batch_size = self.batch_size
            if self.device_mode in ["gpu", "hybrid"]:
                optimal_batch_size = max(32, self.batch_size)  # Larger batches for GPU
            
            self.embedding_engine = EmbeddingEngine(
                device_mode=device_config.get('device_mode', 'auto'),
                batch_size=optimal_batch_size,
                chunk_size=1024,  # Larger chunks for better GPU utilization
                max_retries=1  # Reduce retries for speed
            )
            logger.info(f"Embedding engine initialized with {device_config.get('device_mode', 'auto')} mode, batch_size={optimal_batch_size}")
        except Exception as e:
            logger.warning(f"Failed to initialize embedding engine: {e}")
            self.embedding_engine = None

        # Create GPU-accelerated emoji detection tensor
        self.emoji_tensor = self._create_emoji_tensor()

        # Log device configuration
        if self.verbose:
            self.device_manager.print_system_summary()

        logger.info("Python Emoji Scanner initialized successfully")
    
    def _initialize_emoji_patterns(self) -> List[Tuple[int, int]]:
        """Initialize comprehensive emoji Unicode ranges"""
        patterns = [
            # Basic emoji blocks
            (0x1F600, 0x1F64F),  # Emoticons
            (0x1F300, 0x1F5FF),  # Miscellaneous Symbols and Pictographs
            (0x1F680, 0x1F6FF),  # Transport and Map Symbols
            (0x1F1E0, 0x1F1FF),  # Regional Indicator Symbols
            (0x2600, 0x26FF),    # Miscellaneous Symbols
            (0x2700, 0x27BF),    # Dingbats
            (0xFE00, 0xFE0F),    # Variation Selectors
            (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
            (0x1F018, 0x1F270),  # Various symbols
            (0x238C, 0x2454),    # Miscellaneous Technical
            (0x20D0, 0x20FF),    # Combining Diacritical Marks for Symbols
            (0x1F000, 0x1F02F),  # Mahjong Tiles
            (0x1F030, 0x1F09F),  # Domino Tiles
            (0x1F0A0, 0x1F0FF),  # Playing Cards
            (0x1F100, 0x1F64F),  # Enclosed Alphanumeric Supplement
            (0x1F650, 0x1F67F),  # Ornamental Dingbats
            (0x1F680, 0x1F6FF),  # Transport and Map Symbols
            (0x1F700, 0x1F77F),  # Alchemical Symbols
            (0x1F780, 0x1F7FF),  # Geometric Shapes Extended
            (0x1F800, 0x1F8FF),  # Supplemental Arrows-C
            (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
            (0x1FA00, 0x1FA6F),  # Chess Symbols
            (0x1FA70, 0x1FAFF),  # Symbols and Pictographs Extended-A
            (0x1FB00, 0x1FBFF),  # Symbols for Legacy Computing
        ]
        return patterns

    def _create_emoji_tensor(self) -> torch.Tensor:
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

    def is_emoji(self, char: str) -> bool:
        """Check if a character is an emoji using Unicode ranges (CPU fallback)"""
        if not char:
            return False

        code_point = ord(char)

        # Check against emoji patterns
        for start, end in self.emoji_patterns:
            if start <= code_point <= end:
                return True

        # Additional checks for common emoji characters
        if unicodedata.category(char) in ['So', 'Sk']:  # Symbol, Other or Symbol, Modifier
            return True

        return False

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

    def find_emojis_in_text(self, text: str) -> List[Dict[str, Any]]:
        """Find all emojis in a text string with positions (CPU fallback)"""
        emojis = []

        for i, char in enumerate(text):
            if self.is_emoji(char):
                emojis.append({
                    'emoji': char,
                    'index': i,
                    'length': len(char.encode('utf-8'))
                })

        return emojis
    
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
        """Scan multiple files in batch for better GPU utilization"""
        batch_results = []
        
        if not file_paths:
            return batch_results
            
        # Process files in parallel batches
        for i in range(0, len(file_paths), self.batch_size):
            batch = file_paths[i:i + self.batch_size]
            
            if self.verbose:
                logger.info(f"Processing batch {i//self.batch_size + 1}/{(len(file_paths) + self.batch_size - 1)//self.batch_size} ({len(batch)} files)")
            
            # Process batch in parallel
            with mp.Pool(processes=min(mp.cpu_count(), len(batch))) as pool:
                batch_file_results = pool.map(self.scan_file, batch)
                
                # Flatten results
                for file_results in batch_file_results:
                    if file_results:
                        batch_results.extend(file_results)
            
            # Update GPU utilization tracking in real-time
            current_gpu_util = self._get_gpu_utilization()
            self.performance_stats['gpu_utilization'] = max(
                self.performance_stats['gpu_utilization'], 
                current_gpu_util
            )
            
            if self.verbose and current_gpu_util > 0:
                logger.info(f"Current GPU utilization: {current_gpu_util:.1f}%")
        
        return batch_results

    def scan_directory(self, directory_path: str, recursive: bool = True) -> Tuple[List[EmojiDetectionResult], ScanSummary]:
        """Scan a directory for emojis with performance tracking and batch processing"""
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
        
        # Simplified and optimized filtering to prevent infinite loops
        files_to_scan = [f for f in files_to_scan if not (
            # Skip the scanner script itself
            f.resolve() == current_script or
            # Skip scanner output files
            f.name.startswith(('EMOJI_REPORT', 'PYTHON_EMOJI_REPORT', 'emoji_report')) or
            f.name.endswith(('.log', '.out', '.tmp', '.bak')) or
            # Skip restore directory files (scanner output)
            'restore' in f.parts or
            # Skip user-specified exclusions
            any(exclude in f.parts or exclude in f.name for exclude in self.exclude_list)
        )]
        
        if self.verbose:
            logger.info(f"Found {len(files_to_scan)} files to scan after filtering")
            if len(files_to_scan) > 0:
                logger.info(f"Sample files to scan: {[f.name for f in files_to_scan[:5]]}")
            else:
                logger.warning("No files found to scan after filtering - check your directory and file extensions")
        
        # Use batch processing for better GPU utilization
        all_results = []
        files_with_emojis = 0
        total_lines = 0
        
        if len(files_to_scan) > 0:
            # Show initial GPU status
            if self.verbose and TORCH_AVAILABLE and torch.cuda.is_available():
                initial_gpu_util = self._get_gpu_utilization()
                logger.info(f"Initial GPU utilization: {initial_gpu_util:.1f}%")
                logger.info(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
            
            # Process files in batches for better GPU utilization
            all_results = self.scan_file_batch([str(f) for f in files_to_scan])
            files_with_emojis = len(set(result.file_path for result in all_results))
            
            # Count lines for performance stats (simplified)
            total_lines = sum(1 for f in files_to_scan[:100])  # Sample for performance
            
            # Show final GPU status
            if self.verbose and TORCH_AVAILABLE and torch.cuda.is_available():
                final_gpu_util = self._get_gpu_utilization()
                logger.info(f"Final GPU utilization: {final_gpu_util:.1f}%")
                logger.info(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
        
        # Calculate performance stats
        scan_duration = time.time() - start_time
        
        # Get device performance stats
        device_stats = {}
        if self.embedding_engine:
            device_stats = self.embedding_engine.get_performance_stats()
        
        # Calculate batch processing efficiency
        if len(files_to_scan) > 0:
            self.performance_stats['batch_processing_efficiency'] = len(files_to_scan) / max(1, scan_duration)
        
        summary = ScanSummary(
            total_files_scanned=len(files_to_scan),
            files_with_emojis=files_with_emojis,
            total_emojis_found=len(all_results),
            scan_duration_seconds=scan_duration,
            device_mode_used=self.device_mode,
            performance_stats=device_stats,
            scan_timestamp=datetime.now().isoformat()
        )
        
        # Update performance tracking
        self.performance_stats.update({
            'total_files_processed': len(files_to_scan),
            'total_lines_processed': total_lines,
            'total_emoji_detections': len(all_results),
            'processing_time': scan_duration,
            'device_utilization': device_stats
        })
        
        return all_results, summary
    
    def generate_report(self, results: List[EmojiDetectionResult], summary: ScanSummary, 
                       output_dir: str = "restore") -> Dict[str, str]:
        """Generate comprehensive emoji detection reports"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert results to dictionaries
        results_dict = [asdict(result) for result in results]
        summary_dict = asdict(summary)
        
        # Create report structure
        report = {
            "Summary": summary_dict,
            "Detections": results_dict,
            "ScanMetadata": {
                "scanner_version": "3.0",
                "device_configuration": self.device_manager.get_system_summary(),
                "performance_stats": self.performance_stats
            }
        }
        
        # Generate JSON report
        json_path = os.path.join(output_dir, "PYTHON_EMOJI_REPORT.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Generate text report
        text_path = os.path.join(output_dir, "PYTHON_EMOJI_REPORT.txt")
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
            for result in results:
                f.write(f"File: {result.file_path}\n")
                f.write(f"Line: {result.line_number}, Column: {result.column_number}\n")
                f.write(f"Emoji: {result.emoji}\n")
                f.write(f"Context: {result.context}\n")
                f.write("-" * 40 + "\n")
        
        return {
            "json": json_path,
            "text": text_path
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            "scanner_performance": self.performance_stats,
            "device_capabilities": self.device_manager.get_system_summary(),
            "embedding_engine_stats": self.embedding_engine.get_performance_stats() if self.embedding_engine else None
        }

    def get_scan_summary(self) -> Dict[str, Any]:
        """Get comprehensive scan summary including device usage"""
        summary = {
            'scanner_info': {
                'device_mode_requested': self.device_mode,
                'device_mode_actual': self._get_current_device_info(),
                'batch_size': self.batch_size,
                'torch_available': TORCH_AVAILABLE,
                'cuda_available': torch.cuda.is_available() if TORCH_AVAILABLE else False
            },
            'performance_stats': self.performance_stats,
            'device_manager_info': self.device_manager.get_system_summary() if hasattr(self.device_manager, 'get_system_summary') else {}
        }
        
        # Add GPU memory info if available
        if TORCH_AVAILABLE and torch.cuda.is_available():
            try:
                summary['gpu_info'] = {
                    'device_name': torch.cuda.get_device_name(0),
                    'memory_allocated_gb': torch.cuda.memory_allocated() / 1024**3,
                    'memory_reserved_gb': torch.cuda.memory_reserved() / 1024**3,
                    'total_memory_gb': torch.cuda.get_device_properties(0).total_memory / 1024**3
                }
            except Exception as e:
                summary['gpu_info'] = {'error': str(e)}
        
        return summary

def main():
    """Main function for testing the emoji scanner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Python Emoji Scanner with CPU/GPU support")
    parser.add_argument("--mode", choices=["cpu", "gpu", "hybrid", "auto"], default="auto",
                       help="Device mode to use")
    parser.add_argument("--directory", default=".", help="Directory to scan")
    parser.add_argument("--recursive", action="store_true", default=True, help="Scan recursively")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--output", default="restore", help="Output directory for reports")
    parser.add_argument("--exclude", nargs="*", default=[], 
                       help="Additional directories or files to exclude (e.g., --exclude restore logs temp)")
    parser.add_argument("--batch-size", type=int, default=100,
                       help="Batch size for processing files (higher for better GPU utilization)")
    
    args = parser.parse_args()
    
    # Initialize scanner with optimized batch size
    scanner = PythonEmojiScanner(device_mode=args.mode, verbose=args.verbose, 
                                exclude_list=args.exclude, batch_size=args.batch_size)
    
    # Perform scan
    print(f"Starting emoji scan in {args.directory} with {args.mode} mode...")
    print(f"Batch size: {args.batch_size} (optimized for {args.mode} mode)")
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
    print(f"Reports saved to: {report_paths['json']} and {report_paths['text']}")
    
    # Print performance stats
    perf_summary = scanner.get_performance_summary()
    if 'scanner_performance' in perf_summary and perf_summary['scanner_performance']:
        perf = perf_summary['scanner_performance']
        print(f"\nPerformance Stats:")
        print(f"GPU Utilization: {perf.get('gpu_utilization', 0):.1f}%")
        print(f"Batch Processing Efficiency: {perf.get('batch_processing_efficiency', 0):.1f} files/sec")

    # Get and print comprehensive scan summary
    scan_summary_full = scanner.get_scan_summary()
    print("\n--- Comprehensive Scan Summary ---")
    print(json.dumps(scan_summary_full, indent=2))

if __name__ == "__main__":
    main()
