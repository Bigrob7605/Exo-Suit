#!/usr/bin/env python3
"""
Agent Exo-Suit V5.1 – Ultra-Fast RAM-First Emoji Scanner
- Load files into RAM first, then process in VRAM
- Batch processing for maximum throughput
- Zero disk I/O during scanning
- Target: 1000+ files/sec
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import time
import unicodedata
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import mmap
import tempfile
import shutil

import torch

# --------------------------------------------------------------------------- #
# Logging                                                                     #
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("emoji-scanner")

# --------------------------------------------------------------------------- #
# Device detection                                                            #
# --------------------------------------------------------------------------- #
_CUDA_AVAILABLE = torch.cuda.is_available()
_DEVICE: torch.device = torch.device("cuda:0" if _CUDA_AVAILABLE else "cpu")
log.info(f"Torch device -> {_DEVICE} ({torch.cuda.get_device_name(0) if _CUDA_AVAILABLE else 'CPU'})")

# --------------------------------------------------------------------------- #
# Data models                                                                 #
# --------------------------------------------------------------------------- #
@dataclass
class EmojiResult:
    file_path: str
    line_number: int
    column_number: int
    emoji: str
    context: str
    file_extension: str
    detection_time: str

@dataclass
class ScanSummary:
    total_files_scanned: int
    files_with_emojis: int
    total_emojis_found: int
    scan_duration_seconds: float
    device_mode_used: str
    scan_timestamp: str
    ram_load_time: float
    vram_process_time: float

# --------------------------------------------------------------------------- #
# Unicode ranges covering all modern emoji                                    #
# --------------------------------------------------------------------------- #
_EMOJI_CODE_POINTS: torch.Tensor | None = None
if _DEVICE.type == "cuda":
    # Build once on GPU – < 0.5 MB
    ranges = [
        (0x1F600, 0x1F64F),
        (0x1F300, 0x1F5FF),
        (0x1F680, 0x1F6FF),
        (0x1F1E0, 0x1F1FF),
        (0x2600, 0x26FF),
        (0x2700, 0x27BF),
        (0xFE00, 0xFE0F),
        (0x1F900, 0x1F9FF),
        (0x1F018, 0x1F270),
    ]
    _EMOJI_CODE_POINTS = torch.tensor(
        [cp for start, end in ranges for cp in range(start, end + 1)],
        dtype=torch.int32,
        device=_DEVICE,
    )
    del ranges  # free host memory

# --------------------------------------------------------------------------- #
# RAM-First File Loader                                                      #
# --------------------------------------------------------------------------- #
class RAMFileLoader:
    """Loads files into RAM for ultra-fast processing"""
    
    def __init__(self, max_ram_gb: float = 8.0):
        self.max_ram_bytes = int(max_ram_gb * 1024 * 1024 * 1024)
        self.ram_files: Dict[str, bytes] = {}
        self.total_loaded = 0
        
    def load_files_to_ram(self, file_paths: List[Path], verbose: bool = False) -> Dict[str, bytes]:
        """Load multiple files into RAM simultaneously"""
        start_time = time.perf_counter()
        
        if verbose:
            log.info(f"Loading {len(file_paths)} files into RAM...")
        
        # Filter files by size and load into RAM
        for file_path in file_paths:
            try:
                file_size = file_path.stat().st_size
                if file_size > 10 * 1024 * 1024:  # Skip > 10MB
                    if verbose:
                        log.warning(f"Skipping large file: {file_path.name} ({file_size / 1024 / 1024:.1f} MB)")
                    continue
                    
                if self.total_loaded + file_size > self.max_ram_bytes:
                    if verbose:
                        log.warning(f"RAM limit reached ({self.max_ram_bytes / 1024 / 1024 / 1024:.1f} GB)")
                    break
                
                # Load file into RAM
                with open(file_path, 'rb') as f:
                    content = f.read()
                    self.ram_files[str(file_path)] = content
                    self.total_loaded += file_size
                    
            except Exception as e:
                if verbose:
                    log.warning(f"Failed to load {file_path}: {e}")
                continue
        
        load_time = time.perf_counter() - start_time
        if verbose:
            log.info(f"RAM loading complete: {len(self.ram_files)} files, {self.total_loaded / 1024 / 1024:.1f} MB in {load_time:.2f}s")
        
        return self.ram_files
    
    def get_file_content(self, file_path: str) -> Optional[bytes]:
        """Get file content from RAM"""
        return self.ram_files.get(file_path)
    
    def clear_ram(self):
        """Clear RAM cache"""
        self.ram_files.clear()
        self.total_loaded = 0

# --------------------------------------------------------------------------- #
# Core scanner                                                                #
# --------------------------------------------------------------------------- #
class EmojiScanner:
    _SUPPORTED = {
        ".ps1", ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss",
        ".md", ".txt", ".json", ".xml", ".yaml", ".yml", ".ini", ".cfg", ".conf",
        ".log", ".csv", ".sql", ".sh", ".bat", ".cmd", ".vbs", ".java", ".cpp",
        ".c", ".h", ".hpp", ".cs", ".php", ".rb", ".go", ".rs", ".swift", ".kt",
        ".scala", ".r", ".m", ".pl", ".lua",
    }

    def __init__(
        self,
        *,
        exclude: List[str] | None = None,
        verbose: bool = False,
        max_ram_gb: float = 8.0,
    ):
        self.exclude: list[str] = exclude or []
        self.verbose = verbose
        self.ram_loader = RAMFileLoader(max_ram_gb=max_ram_gb)

    # --------------------------------------------------------------------- #
    # Emoji detection                                                       #
    # --------------------------------------------------------------------- #
    @staticmethod
    def _is_emoji(char: str) -> bool:
        """Check if character is a real emoji - FIXED VERSION"""
        code = ord(char)
        
        # Skip valid code characters that are NOT emojis
        if code in [96, 124, 45]:  # ` (backtick), | (pipe), - (hyphen)
            return False
        
        # Skip box-drawing characters
        if 0x2500 <= code <= 0x257F:  # Box-drawing Unicode block
            return False
        
        # Skip common punctuation that might be confused with emojis
        if code in [33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 46, 47, 58, 59, 60, 61, 62, 63, 64]:
            return False
        
        if _EMOJI_CODE_POINTS is not None:
            # GPU lookup for real emojis only
            return bool((_EMOJI_CODE_POINTS == code).any())
        
        # CPU fallback - only real emojis
        if unicodedata.category(char) in {"So", "Sk"}:
            # Additional check: must be in actual emoji ranges
            return any(
                start <= code <= end
                for start, end in [
                    (0x1F600, 0x1F64F),  # Emoticons
                    (0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs
                    (0x1F680, 0x1F6FF),  # Transport and Map Symbols
                    (0x1F1E0, 0x1F1FF),  # Regional Indicator Symbols
                    (0x2600, 0x26FF),    # Misc Symbols
                    (0x2700, 0x27BF),    # Dingbats
                    (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
                ]
            )
        
        return False

    # --------------------------------------------------------------------- #
    # RAM-based file scanning                                               #
    # --------------------------------------------------------------------- #
    def _scan_ram_file(self, file_path: str, content: bytes) -> List[EmojiResult]:
        """Scan file content from RAM - OPTIMIZED FOR FULL VRAM USAGE"""
        results: List[EmojiResult] = []
        
        try:
            # Decode content
            text = content.decode('utf-8', errors='ignore')
            
            # OPTIMIZATION: Process entire file at once in VRAM
            if _EMOJI_CODE_POINTS is not None and self.device.type == "cuda":
                # Convert entire text to GPU tensor for batch processing
                text_codes = torch.tensor([ord(c) for c in text], device=self.device, dtype=torch.int32)
                
                # Batch emoji detection using GPU tensor operations
                # This uses the full VRAM capacity like our successful approach
                emoji_mask = torch.isin(text_codes, _EMOJI_CODE_POINTS)
                emoji_positions = torch.where(emoji_mask)[0]
                
                # Convert positions back to line/column
                for pos in emoji_positions:
                    char_pos = pos.item()
                    char = text[char_pos]
                    
                    # Calculate line and column from position
                    line_num = 1
                    col_num = 1
                    for i in range(char_pos):
                        if text[i] == '\n':
                            line_num += 1
                            col_num = 1
                        else:
                            col_num += 1
                    
                    # Get context
                    start = max(0, char_pos - 21)
                    end = min(len(text), char_pos + 20)
                    context = text[start:end].replace('\n', ' ').strip()
                    
                    results.append(
                        EmojiResult(
                            file_path=file_path,
                            line_number=line_num,
                            column_number=col_num,
                            emoji=char,
                            context=context,
                            file_extension=Path(file_path).suffix,
                            detection_time=datetime.now().isoformat(timespec="seconds"),
                        )
                    )
                
                # Clear GPU memory immediately
                del text_codes, emoji_mask, emoji_positions
                torch.cuda.empty_cache()
                
            else:
                # CPU fallback - process line by line
                for line_num, line in enumerate(text.splitlines(), 1):
                    for col, char in enumerate(line, 1):
                        if self._is_emoji(char):
                            start = max(0, col - 21)
                            end = min(len(line), col + 20)
                            results.append(
                                EmojiResult(
                                    file_path=file_path,
                                    line_number=line_num,
                                    column_number=col,
                                    emoji=char,
                                    context=line[start:end].strip(),
                                    file_extension=Path(file_path).suffix,
                                    detection_time=datetime.now().isoformat(timespec="seconds"),
                                )
                            )
        except Exception as e:
            if self.verbose:
                log.warning(f"Error scanning {file_path}: {e}")
        
        return results

    def scan_directory(
        self, directory: str, *, recursive: bool = True
    ) -> Tuple[List[EmojiResult], ScanSummary]:
        start = time.perf_counter()
        root = Path(directory).expanduser().resolve()
        current_script = Path(__file__).resolve()

        # Collect file paths
        files = (
            list(root.rglob("*"))
            if recursive
            else list(root.iterdir())
        )
        files = [
            f
            for f in files
            if (
                f.is_file()
                and f.suffix.lower() in self._SUPPORTED
                and f.resolve() != current_script
                and not any(exc in str(f) for exc in self.exclude)
                and not f.name.startswith("EMOJI_REPORT")
                and not f.name.endswith((".log", ".out", ".tmp", ".bak"))
            )
        ]

        if self.verbose:
            log.info(f"Files to scan: {len(files)}")

        # Phase 1: Load files into RAM
        ram_start = time.perf_counter()
        ram_files = self.ram_loader.load_files_to_ram(files, verbose=self.verbose)
        ram_load_time = time.perf_counter() - ram_start

        # Phase 2: Process files from RAM
        vram_start = time.perf_counter()
        results: List[EmojiResult] = []
        
        # MASSIVE VRAM OPTIMIZATION: Batch ALL files together
        if _EMOJI_CODE_POINTS is not None and _DEVICE.type == "cuda":
            if self.verbose:
                log.info("Using MASSIVE VRAM optimization - batching all files together!")
            
            # Combine all file contents into one giant text
            all_text = ""
            file_boundaries = []  # Track where each file starts
            
            for file_path in ram_files:
                content = ram_files[file_path]
                text = content.decode('utf-8', errors='ignore')
                file_boundaries.append((file_path, len(all_text), len(text)))
                all_text += text + "\n"  # Add separator
            
            if self.verbose:
                log.info(f"Combined text length: {len(all_text):,} characters")
                log.info(f"Creating giant GPU tensor...")
            
            # Create massive GPU tensor for all text
            all_codes = torch.tensor([ord(c) for c in all_text], device=_DEVICE, dtype=torch.int32)
            
            if self.verbose:
                log.info(f"GPU tensor created: {all_codes.shape[0]:,} elements")
                log.info(f"GPU memory usage: {all_codes.element_size() * all_codes.numel() / 1024 / 1024:.1f} MB")
            
            # Batch emoji detection on entire dataset
            emoji_mask = torch.isin(all_codes, _EMOJI_CODE_POINTS)
            emoji_positions = torch.where(emoji_mask)[0]
            
            if self.verbose:
                log.info(f"Found {emoji_positions.shape[0]} emojis in batch")
            
            # Process all emojis at once
            for pos in emoji_positions:
                char_pos = pos.item()
                char = all_text[char_pos]
                
                # Find which file this emoji belongs to
                file_path = None
                file_start = 0
                for fp, start, length in file_boundaries:
                    if start <= char_pos < start + length:
                        file_path = fp
                        file_start = start
                        break
                
                if file_path:
                    # Calculate line and column within the file
                    file_text = all_text[file_start:file_start + length]
                    relative_pos = char_pos - file_start
                    
                    line_num = 1
                    col_num = 1
                    for i in range(relative_pos):
                        if file_text[i] == '\n':
                            line_num += 1
                            col_num = 1
                        else:
                            col_num += 1
                    
                    # Get context
                    start = max(file_start, char_pos - 21)
                    end = min(file_start + length, char_pos + 20)
                    context = all_text[start:end].replace('\n', ' ').strip()
                    
                    results.append(
                        EmojiResult(
                            file_path=file_path,
                            line_number=line_num,
                            column_number=col_num,
                            emoji=char,
                            context=context,
                            file_extension=Path(file_path).suffix,
                            detection_time=datetime.now().isoformat(timespec="seconds"),
                        )
                    )
            
            # Massive cleanup
            del all_codes, emoji_mask, emoji_positions, all_text
            torch.cuda.empty_cache()
            
            if self.verbose:
                log.info("MASSIVE VRAM optimization complete!")
                
        else:
            # Fallback: Process files individually
            for file_path in ram_files:
                if self.verbose:
                    log.info(f"  Scanning: {file_path}")
                content = ram_files[file_path]
                results.extend(self._scan_ram_file(file_path, content))
        
        vram_process_time = time.perf_counter() - vram_start
        total_duration = time.perf_counter() - start

        # Store file count before cleanup
        files_scanned = len(ram_files)

        # Cleanup RAM
        self.ram_loader.clear_ram()

        # Fix timing calculation
        if total_duration < 0:
            total_duration = ram_load_time + vram_process_time

        # Calculate files with emojis correctly
        files_with_emojis = len(set(r.file_path for r in results)) if results else 0

        summary = ScanSummary(
            total_files_scanned=files_scanned,  # Use stored count
            files_with_emojis=files_with_emojis,
            total_emojis_found=len(results),
            scan_duration_seconds=round(total_duration, 2),
            device_mode_used=str(_DEVICE),
            scan_timestamp=datetime.now().isoformat(timespec="seconds"),
            ram_load_time=round(ram_load_time, 2),
            vram_process_time=round(vram_process_time, 2),
        )
        return results, summary

    # --------------------------------------------------------------------- #
    # Report generation                                                     #
    # --------------------------------------------------------------------- #
    @staticmethod
    def generate_report(
        results: List[EmojiResult], summary: ScanSummary, out_dir: str = "."
    ) -> Dict[str, str]:
        os.makedirs(out_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON
        json_path = os.path.join(out_dir, f"EMOJI_REPORT_{ts}.json")
        with open(json_path, "w", encoding="utf-8") as fp:
            json.dump(
                {"summary": asdict(summary), "detections": [asdict(r) for r in results]},
                fp,
                indent=2,
                ensure_ascii=False,
            )

        # TXT
        txt_path = os.path.join(out_dir, f"EMOJI_REPORT_{ts}.txt")
        with open(txt_path, "w", encoding="utf-8") as fp:
            fp.write("Emoji Scan Report\n")
            fp.write("=" * 50 + "\n\n")
            fp.write(f"Files scanned : {summary.total_files_scanned}\n")
            fp.write(f"Emojis found  : {summary.total_emojis_found}\n")
            fp.write(f"Total duration: {summary.scan_duration_seconds}s\n")
            fp.write(f"RAM load time : {summary.ram_load_time}s\n")
            fp.write(f"VRAM process  : {summary.vram_process_time}s\n")
            fp.write(f"Device        : {summary.device_mode_used}\n\n")

            for hit in results:
                fp.write(
                    f"{hit.file_path}:{hit.line_number}:{hit.column_number}  "
                    f"{hit.emoji!r}  {hit.context}\n"
                )

        return {"json": json_path, "txt": txt_path}


# --------------------------------------------------------------------------- #
# CLI                                                                         #
# --------------------------------------------------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser(description="Ultra-fast RAM-first emoji scanner")
    parser.add_argument("--mode", choices=["cpu", "gpu", "auto"], default="auto")
    parser.add_argument("--directory", default=".")
    parser.add_argument("-r", "--recursive", action="store_true", default=True)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--output", default=".")
    parser.add_argument("--exclude", nargs="*", default=[])
    parser.add_argument("--max-ram", type=float, default=8.0, help="Max RAM usage in GB")
    args = parser.parse_args()

    # Enforce CPU if user explicitly asked for it
    global _DEVICE, _CUDA_AVAILABLE, _EMOJI_CODE_POINTS
    if args.mode == "cpu":
        _DEVICE = torch.device("cpu")
        _CUDA_AVAILABLE = False
        _EMOJI_CODE_POINTS = None
    elif args.mode == "gpu" and not _CUDA_AVAILABLE:
        raise SystemExit("CUDA requested but not available!")

    scanner = EmojiScanner(exclude=args.exclude, verbose=args.verbose, max_ram_gb=args.max_ram)
    results, summary = scanner.scan_directory(args.directory, recursive=args.recursive)

    reports = scanner.generate_report(results, summary, args.output)

    print("\nScan complete!")
    print(f"Files scanned : {summary.total_files_scanned}")
    print(f"Emojis found  : {summary.total_emojis_found}")
    print(f"Total duration: {summary.scan_duration_seconds}s")
    print(f"RAM load time : {summary.ram_load_time}s")
    print(f"VRAM process  : {summary.vram_process_time}s")
    print(f"Device used   : {summary.device_mode_used}")
    print(f"Performance   : {summary.total_files_scanned / summary.scan_duration_seconds:.1f} files/sec")
    print(f"JSON report   : {reports['json']}")
    print(f"TXT report    : {reports['txt']}")


if __name__ == "__main__":
    main()
