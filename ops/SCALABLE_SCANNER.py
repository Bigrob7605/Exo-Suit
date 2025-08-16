#!/usr/bin/env python3
"""
SCALABLE SCANNER - Agent Exo-Suit V5.0
Efficient full project scanning based on validated framework.
"""

import os
import sys
import json
import time
import logging
import re
import threading
from pathlib import Path
from typing import List, Dict, Any, Tuple, Set
import hashlib
from collections import defaultdict

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/SCALABLE_SCANNER.log'),
        logging.StreamHandler()
    ]
)

class ScalableScanner:
    def __init__(self):
        self.project_root = Path(".")
        self.logs_dir = Path("logs")
        self.reports_dir = Path("reports")
        
        # Create necessary directories
        self.logs_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Project boundary detection
        self.project_boundaries = self._detect_project_boundaries()
        self.main_project_name = self._identify_main_project()
        
        # Scanning configuration - OPTIMIZED FOR PERFORMANCE
        self.scan_extensions = ['.md', '.py', '.js', '.json', '.yaml', '.yml', '.txt', '.ps1']
        self.batch_size = 50  # Process files in batches for better performance
        
        # Progress tracking
        self.progress_active = False
        self.progress_thread = None
        self.current_files_scanned = 0
        self.total_files_found = 0
        
        # Results storage
        self.scan_results = {
            'unicode_scan': {},
            'content_scan': {},
            'performance_metrics': {}
        }
        
        logging.info("Initializing SCALABLE SCANNER")
        logging.info(f"Mission: Efficient full project scanning with batch processing")
        logging.info(f"Main Project: {self.main_project_name}")
        logging.info(f"Batch Size: {self.batch_size} files per batch")
    
    def _detect_project_boundaries(self) -> Dict[str, Any]:
        """Detect project boundaries"""
        boundaries = {
            'excluded_directories': [
                'Universal Open Science Toolbox With Kai (The Real Test)',
                'Testing_Tools', 'Cleanup - Testing Data'
            ]
        }
        return boundaries
    
    def _identify_main_project(self) -> str:
        """Identify main project"""
        if (self.project_root / "AgentExoSuitV4.ps1").exists():
            return "Agent Exo-Suit V5.0"
        return "Agent Exo-Suit"
    
    def _is_toolbox_file(self, file_path: Path) -> bool:
        """Check if file is part of toolbox system"""
        file_str = str(file_path)
        for excluded_dir in self.project_boundaries['excluded_directories']:
            if excluded_dir in file_str:
                return True
        return False
    
    def _start_progress_indicator(self, scan_name: str):
        """Start progress indicator"""
        self.progress_active = True
        self.progress_thread = threading.Thread(target=self._progress_animation, args=(scan_name,), daemon=True)
        self.progress_thread.start()
        logging.info(f"Progress indicator started for {scan_name}")
    
    def _stop_progress_indicator(self):
        """Stop progress indicator"""
        self.progress_active = False
        if self.progress_thread:
            self.progress_thread.join(timeout=1)
        print("\n")  # Clean line break
        logging.info("Progress indicator stopped")
    
    def _progress_animation(self, scan_name: str):
        """Progress animation with batch information"""
        while self.progress_active:
            try:
                if self.total_files_found > 0:
                    progress_percent = (self.current_files_scanned / self.total_files_found) * 100
                    status_line = f"\r[SCAN] {scan_name} - Progress: {self.current_files_scanned}/{self.total_files_found} ({progress_percent:.1f}%) "
                else:
                    status_line = f"\r[SCAN] {scan_name} - Files: {self.current_files_scanned} "
                
                print(status_line, end='', flush=True)
                time.sleep(0.2)
            except Exception as e:
                print(f"\r[SCAN] {scan_name} - Running...", end='', flush=True)
                time.sleep(0.5)
    
    def _get_all_scannable_files(self) -> List[Path]:
        """Get all scannable files efficiently"""
        logging.info("Discovering all scannable files...")
        
        all_files = []
        for ext in self.scan_extensions:
            files = list(self.project_root.rglob(f"*{ext}"))
            for file_path in files:
                if not self._is_toolbox_file(file_path):
                    all_files.append(file_path)
        
        # Sort files for consistent processing
        all_files.sort(key=lambda x: str(x))
        
        logging.info(f"Found {len(all_files)} scannable files")
        return all_files
    
    def run_unicode_scan(self) -> Dict[str, Any]:
        """Run Unicode/Emoji scan with batch processing"""
        logging.info("Starting Unicode/Emoji Scanner with batch processing...")
        
        # Start progress indicator
        self._start_progress_indicator("Unicode Scan")
        
        scan_results = {
            'files_scanned': 0,
            'files_with_unicode': 0,
            'files_with_emojis': 0,
            'unicode_issues': [],
            'clean_files': [],
            'total_issues_found': 0,
            'scan_time_seconds': 0,
            'performance_metrics': {}
        }
        
        start_time = time.time()
        
        # Get all files
        all_files = self._get_all_scannable_files()
        self.total_files_found = len(all_files)
        
        # Process in batches
        batch_count = 0
        for i in range(0, len(all_files), self.batch_size):
            batch_count += 1
            batch_files = all_files[i:i + self.batch_size]
            batch_start_time = time.time()
            
            logging.info(f"Processing batch {batch_count}: {len(batch_files)} files")
            
            # Process batch
            for file_path in batch_files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    scan_results['files_scanned'] += 1
                    self.current_files_scanned = scan_results['files_scanned']
                    
                    # Quick Unicode check (optimized)
                    unicode_count = 0
                    emoji_count = 0
                    
                    for char in content:
                        if ord(char) > 127:  # Non-ASCII character
                            unicode_count += 1
                            # Check if it's an emoji
                            if 0x1F600 <= ord(char) <= 0x1F64F or 0x1F300 <= ord(char) <= 0x1F5FF:
                                emoji_count += 1
                    
                    if unicode_count > 0:
                        scan_results['files_with_unicode'] += 1
                        scan_results['unicode_issues'].append({
                            'file': str(file_path),
                            'unicode_count': unicode_count,
                            'emoji_count': emoji_count
                        })
                        scan_results['total_issues_found'] += unicode_count
                        
                        if emoji_count > 0:
                            scan_results['files_with_emojis'] += 1
                    else:
                        scan_results['clean_files'].append(str(file_path))
                        
                except Exception as e:
                    logging.warning(f"Could not scan {file_path}: {e}")
                    continue
            
            # Batch performance metrics
            batch_time = time.time() - batch_start_time
            batch_rate = len(batch_files) / batch_time if batch_time > 0 else 0
            logging.info(f"Batch {batch_count} completed in {batch_time:.2f}s ({batch_rate:.1f} files/sec)")
        
        # Calculate overall scan time
        scan_results['scan_time_seconds'] = time.time() - start_time
        
        # Performance metrics
        scan_results['performance_metrics'] = {
            'total_time': scan_results['scan_time_seconds'],
            'files_per_second': scan_results['files_scanned'] / scan_results['scan_time_seconds'] if scan_results['scan_time_seconds'] > 0 else 0,
            'average_time_per_file': scan_results['scan_time_seconds'] / scan_results['files_scanned'] if scan_results['files_scanned'] > 0 else 0,
            'batch_count': batch_count,
            'batch_size': self.batch_size
        }
        
        # Stop progress indicator
        self._stop_progress_indicator()
        
        logging.info(f"Unicode Scan Complete: {scan_results['files_scanned']} files in {scan_results['scan_time_seconds']:.2f}s")
        logging.info(f"Files with Unicode: {scan_results['files_with_unicode']}")
        logging.info(f"Files with Emojis: {scan_results['files_with_emojis']}")
        logging.info(f"Total Issues: {scan_results['total_issues_found']}")
        logging.info(f"Performance: {scan_results['performance_metrics']['files_per_second']:.1f} files/sec")
        
        self.scan_results['unicode_scan'] = scan_results
        return scan_results
    
    def run_content_scan(self) -> Dict[str, Any]:
        """Run content quality scan with batch processing"""
        logging.info("Starting Content Quality Scanner with batch processing...")
        
        # Start progress indicator
        self._start_progress_indicator("Content Scan")
        
        scan_results = {
            'files_scanned': 0,
            'placeholder_markers': [],
            'todo_items': [],
            'total_issues_found': 0,
            'scan_time_seconds': 0,
            'performance_metrics': {}
        }
        
        start_time = time.time()
        
        # Get all files
        all_files = self._get_all_scannable_files()
        self.total_files_found = len(all_files)
        self.current_files_scanned = 0
        
        # Content quality patterns
        placeholder_patterns = [r'PLACEHOLDER', r'FILL_IN', r'ADD_HERE', r'COMPLETE_THIS']
        todo_patterns = [r'TODO', r'FIXME', r'BUG', r'HACK', r'XXX', r'NOTE', r'REVIEW']
        
        # Process in batches
        batch_count = 0
        for i in range(0, len(all_files), self.batch_size):
            batch_count += 1
            batch_files = all_files[i:i + self.batch_size]
            batch_start_time = time.time()
            
            logging.info(f"Processing batch {batch_count}: {len(batch_files)} files")
            
            # Process batch
            for file_path in batch_files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    scan_results['files_scanned'] += 1
                    self.current_files_scanned = scan_results['files_scanned']
                    
                    # Check for placeholder markers
                    for pattern in placeholder_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            scan_results['placeholder_markers'].append({
                                'file': str(file_path),
                                'pattern': pattern
                            })
                            scan_results['total_issues_found'] += 1
                    
                    # Check for TODO items
                    for pattern in todo_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            scan_results['todo_items'].append({
                                'file': str(file_path),
                                'type': pattern
                            })
                            scan_results['total_issues_found'] += 1
                            
                except Exception as e:
                    logging.warning(f"Could not scan {file_path}: {e}")
                    continue
            
            # Batch performance metrics
            batch_time = time.time() - batch_start_time
            batch_rate = len(batch_files) / batch_time if batch_time > 0 else 0
            logging.info(f"Batch {batch_count} completed in {batch_time:.2f}s ({batch_rate:.1f} files/sec)")
        
        # Calculate overall scan time
        scan_results['scan_time_seconds'] = time.time() - start_time
        
        # Performance metrics
        scan_results['performance_metrics'] = {
            'total_time': scan_results['scan_time_seconds'],
            'files_per_second': scan_results['files_scanned'] / scan_results['scan_time_seconds'] if scan_results['scan_time_seconds'] > 0 else 0,
            'average_time_per_file': scan_results['scan_time_seconds'] / scan_results['files_scanned'] if scan_results['files_scanned'] > 0 else 0,
            'batch_count': batch_count,
            'batch_size': self.batch_size
        }
        
        # Stop progress indicator
        self._stop_progress_indicator()
        
        logging.info(f"Content Scan Complete: {scan_results['files_scanned']} files in {scan_results['scan_time_seconds']:.2f}s")
        logging.info(f"Placeholder Markers: {len(scan_results['placeholder_markers'])}")
        logging.info(f"TODO Items: {len(scan_results['todo_items'])}")
        logging.info(f"Total Issues: {scan_results['total_issues_found']}")
        logging.info(f"Performance: {scan_results['performance_metrics']['files_per_second']:.1f} files/sec")
        
        self.scan_results['content_scan'] = scan_results
        return scan_results
    
    def run_comprehensive_scan(self):
        """Run comprehensive scanning"""
        logging.info("STARTING COMPREHENSIVE SCALABLE SCANNING")
        
        # Scan 1: Unicode/Emoji Scanner
        unicode_results = self.run_unicode_scan()
        
        # Scan 2: Content Quality Scanner
        content_results = self.run_content_scan()
        
        # Generate comprehensive report
        self._generate_comprehensive_report(unicode_results, content_results)
        
        logging.info("COMPREHENSIVE SCALABLE SCANNING COMPLETE")
        
        return {
            'unicode_scan': unicode_results,
            'content_scan': content_results,
            'total_scan_time': unicode_results['scan_time_seconds'] + content_results['scan_time_seconds']
        }
    
    def _generate_comprehensive_report(self, unicode_results: Dict, content_results: Dict):
        """Generate comprehensive scanning report"""
        logging.info("Generating comprehensive scanning report...")
        
        report_content = f"""# COMPREHENSIVE SCALABLE SCANNING REPORT - Agent Exo-Suit V5.0

**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**Project**: {self.project_root.name}
**System**: Agent Exo-Suit V5.0 Scalable Scanner

## EXECUTIVE SUMMARY

Comprehensive scalable scanning completed with batch processing for optimal performance.

## SCANNING CONFIGURATION

**File Extensions**: {', '.join(self.scan_extensions)}
**Batch Size**: {self.batch_size} files per batch
**Total Scan Time**: {unicode_results['scan_time_seconds'] + content_results['scan_time_seconds']:.2f} seconds

## UNICODE SCAN RESULTS

**Files Scanned**: {unicode_results['files_scanned']}
**Scan Time**: {unicode_results['scan_time_seconds']:.2f}s
**Files with Unicode**: {unicode_results['files_with_unicode']}
**Files with Emojis**: {unicode_results['files_with_emojis']}
**Total Issues**: {unicode_results['total_issues_found']}
**Performance**: {unicode_results['performance_metrics']['files_per_second']:.1f} files/sec

### Unicode Issues Summary
- **Files with Unicode**: {unicode_results['files_with_unicode']} out of {unicode_results['files_scanned']} ({unicode_results['files_with_unicode']/unicode_results['files_scanned']*100:.1f}%)
- **Files with Emojis**: {unicode_results['files_with_emojis']} out of {unicode_results['files_scanned']} ({unicode_results['files_with_emojis']/unicode_results['files_scanned']*100:.1f}%)
- **Average Issues per File**: {unicode_results['total_issues_found']/unicode_results['files_scanned']:.1f} if unicode_results['files_scanned'] > 0 else 0

## CONTENT QUALITY SCAN RESULTS

**Files Scanned**: {content_results['files_scanned']}
**Scan Time**: {content_results['scan_time_seconds']:.2f}s
**Placeholder Markers**: {len(content_results['placeholder_markers'])}
**TODO Items**: {len(content_results['todo_items'])}
**Total Issues**: {content_results['total_issues_found']}
**Performance**: {content_results['performance_metrics']['files_per_second']:.1f} files/sec

### Content Issues Summary
- **Files with Placeholders**: {len(content_results['placeholder_markers'])} out of {content_results['files_scanned']}
- **Files with TODOs**: {len(content_results['todo_items'])} out of {content_results['files_scanned']}

## PERFORMANCE ANALYSIS

**Overall Performance**: {(unicode_results['files_scanned'] + content_results['files_scanned']) / (unicode_results['scan_time_seconds'] + content_results['scan_time_seconds']):.1f} files/sec
**Total Files Processed**: {unicode_results['files_scanned'] + content_results['files_scanned']}
**Total Issues Found**: {unicode_results['total_issues_found'] + content_results['total_issues_found']}

## NEXT STEPS

1. **Address Unicode Issues**: Clean all emoji and non-ASCII characters
2. **Complete Placeholder Content**: Fill in all placeholder markers
3. **Resolve TODO Items**: Implement or remove all TODO markers
4. **Prepare for Repair Phase**: Use this report for comprehensive project healing

## CONCLUSION

Scalable scanning completed successfully with excellent performance.

**Ready for comprehensive project healing!**

---
**Generated by**: Agent Exo-Suit V5.0 Scalable Scanner
**System Status**: SCANNING COMPLETE
**Mission**: Efficient full project scanning with batch processing
"""
        
        # Save report
        report_path = self.reports_dir / "COMPREHENSIVE_SCALABLE_SCANNING_REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logging.info(f"Comprehensive report saved to: {report_path}")

def main():
    """Main execution function"""
    try:
        # Initialize and run Scalable Scanner
        scalable_scanner = ScalableScanner()
        results = scalable_scanner.run_comprehensive_scan()
        
        logging.info("Scalable Scanner execution completed successfully")
        logging.info(f"Total scan time: {results['total_scan_time']:.2f} seconds")
        
    except KeyboardInterrupt:
        logging.info("Scalable scanning interrupted by user")
    except Exception as e:
        logging.error(f"Scalable scanning failed with error: {e}")
        raise

if __name__ == "__main__":
    main()
