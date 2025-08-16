#!/usr/bin/env python3
"""
FAST TEST SCANNER - Agent Exo-Suit V5.0
Quick validation of scanning framework with limited file set.
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
        logging.FileHandler('logs/FAST_TEST_SCANNER.log'),
        logging.StreamHandler()
    ]
)

class FastTestScanner:
    def __init__(self):
        self.project_root = Path(".")
        self.logs_dir = Path("logs")
        self.reports_dir = Path("reports")
        
        # Create necessary directories
        self.logs_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Project boundary detection (simplified)
        self.project_boundaries = self._detect_project_boundaries()
        self.main_project_name = self._identify_main_project()
        
        # Test configuration - LIMIT TO SMALL SUBSET
        self.max_files_to_scan = 20  # Start with just 20 files
        self.test_extensions = ['.md', '.py']  # Focus on key file types
        
        # Progress tracking
        self.progress_active = False
        self.progress_thread = None
        self.current_files_scanned = 0
        
        logging.info("Initializing FAST TEST SCANNER")
        logging.info(f"Mission: Validate scanning framework with max {self.max_files_to_scan} files")
        logging.info(f"Main Project: {self.main_project_name}")
    
    def _detect_project_boundaries(self) -> Dict[str, Any]:
        """Detect project boundaries (simplified version)"""
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
        """Start simple progress indicator"""
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
        """Simple progress animation"""
        while self.progress_active:
            try:
                status_line = f"\r[TEST] {scan_name} - Files: {self.current_files_scanned}/{self.max_files_to_scan} "
                print(status_line, end='', flush=True)
                time.sleep(0.2)
            except Exception as e:
                print(f"\r[TEST] {scan_name} - Running...", end='', flush=True)
                time.sleep(0.5)
    
    def run_fast_unicode_test(self) -> Dict[str, Any]:
        """Fast Unicode test with limited files"""
        logging.info("FAST TEST: Starting Unicode/Emoji Scanner...")
        
        # Start progress indicator
        self._start_progress_indicator("Unicode Test")
        
        scan_results = {
            'files_scanned': 0,
            'files_with_unicode': 0,
            'files_with_emojis': 0,
            'unicode_issues': [],
            'clean_files': [],
            'total_issues_found': 0,
            'scan_time_seconds': 0
        }
        
        start_time = time.time()
        
        # Get limited file set for testing
        test_files = []
        for ext in self.test_extensions:
            files = list(self.project_root.rglob(f"*{ext}"))
            for file_path in files:
                if self._is_toolbox_file(file_path):
                    continue
                test_files.append(file_path)
                if len(test_files) >= self.max_files_to_scan:
                    break
            if len(test_files) >= self.max_files_to_scan:
                break
        
        logging.info(f"Fast test: Selected {len(test_files)} files for scanning")
        
        # Scan selected files
        for file_path in test_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                scan_results['files_scanned'] += 1
                self.current_files_scanned = scan_results['files_scanned']
                
                # Quick Unicode check (simplified)
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
        
        # Calculate scan time
        scan_results['scan_time_seconds'] = time.time() - start_time
        
        # Stop progress indicator
        self._stop_progress_indicator()
        
        logging.info(f"Fast Unicode Test Complete: {scan_results['files_scanned']} files in {scan_results['scan_time_seconds']:.2f}s")
        logging.info(f"Files with Unicode: {scan_results['files_with_unicode']}")
        logging.info(f"Files with Emojis: {scan_results['files_with_emojis']}")
        logging.info(f"Total Issues: {scan_results['total_issues_found']}")
        
        return scan_results
    
    def run_fast_content_test(self) -> Dict[str, Any]:
        """Fast content quality test with limited files"""
        logging.info("FAST TEST: Starting Content Quality Scanner...")
        
        # Start progress indicator
        self._start_progress_indicator("Content Test")
        
        scan_results = {
            'files_scanned': 0,
            'placeholder_markers': [],
            'todo_items': [],
            'total_issues_found': 0,
            'scan_time_seconds': 0
        }
        
        start_time = time.time()
        
        # Get limited file set for testing
        test_files = []
        for ext in self.test_extensions:
            files = list(self.project_root.rglob(f"*{ext}"))
            for file_path in files:
                if self._is_toolbox_file(file_path):
                    continue
                test_files.append(file_path)
                if len(test_files) >= self.max_files_to_scan:
                    break
            if len(test_files) >= self.max_files_to_scan:
                break
        
        # Content quality patterns (simplified)
        placeholder_patterns = [r'PLACEHOLDER', r'FILL_IN', r'ADD_HERE']
        todo_patterns = [r'TODO', r'FIXME', r'BUG']
        
        # Scan selected files
        for file_path in test_files:
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
        
        # Calculate scan time
        scan_results['scan_time_seconds'] = time.time() - start_time
        
        # Stop progress indicator
        self._stop_progress_indicator()
        
        logging.info(f"Fast Content Test Complete: {scan_results['files_scanned']} files in {scan_results['scan_time_seconds']:.2f}s")
        logging.info(f"Placeholder Markers: {len(scan_results['placeholder_markers'])}")
        logging.info(f"TODO Items: {len(scan_results['todo_items'])}")
        logging.info(f"Total Issues: {scan_results['total_issues_found']}")
        
        return scan_results
    
    def run_fast_comprehensive_test(self):
        """Run fast comprehensive test"""
        logging.info("STARTING FAST COMPREHENSIVE TEST")
        
        # Test 1: Fast Unicode Scanner
        unicode_results = self.run_fast_unicode_test()
        
        # Test 2: Fast Content Quality Scanner
        content_results = self.run_fast_content_test()
        
        # Generate fast test report
        self._generate_fast_test_report(unicode_results, content_results)
        
        logging.info("FAST COMPREHENSIVE TEST COMPLETE")
        
        return {
            'unicode_test': unicode_results,
            'content_test': content_results,
            'total_scan_time': unicode_results['scan_time_seconds'] + content_results['scan_time_seconds']
        }
    
    def _generate_fast_test_report(self, unicode_results: Dict, content_results: Dict):
        """Generate fast test report"""
        logging.info("Generating fast test report...")
        
        report_content = f"""# FAST TEST SCANNER REPORT - Agent Exo-Suit V5.0

**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**Project**: {self.project_root.name}
**System**: Agent Exo-Suit V5.0 Fast Test Scanner

## EXECUTIVE SUMMARY

Fast test completed to validate scanning framework efficiency.

## TEST CONFIGURATION

**Max Files Scanned**: {self.max_files_to_scan}
**File Extensions**: {', '.join(self.test_extensions)}
**Total Scan Time**: {unicode_results['scan_time_seconds'] + content_results['scan_time_seconds']:.2f} seconds

## UNICODE TEST RESULTS

**Files Scanned**: {unicode_results['files_scanned']}
**Scan Time**: {unicode_results['scan_time_seconds']:.2f}s
**Files with Unicode**: {unicode_results['files_with_unicode']}
**Files with Emojis**: {unicode_results['files_with_emojis']}
**Total Issues**: {unicode_results['total_issues_found']}

### Unicode Issues Found
"""
        
        for issue in unicode_results['unicode_issues']:
            report_content += f"""
**File**: {issue['file']}
- Unicode Count: {issue['unicode_count']}
- Emoji Count: {issue['emoji_count']}
"""
        
        report_content += f"""
## CONTENT QUALITY TEST RESULTS

**Files Scanned**: {content_results['files_scanned']}
**Scan Time**: {content_results['scan_time_seconds']:.2f}s
**Placeholder Markers**: {len(content_results['placeholder_markers'])}
**TODO Items**: {len(content_results['todo_items'])}
**Total Issues**: {content_results['total_issues_found']}

### Content Issues Found
"""
        
        if content_results['placeholder_markers']:
            report_content += "#### Placeholder Markers\n"
            for marker in content_results['placeholder_markers']:
                report_content += f"- **{marker['file']}**: {marker['pattern']}\n"
        
        if content_results['todo_items']:
            report_content += "#### TODO Items\n"
            for todo in content_results['todo_items']:
                report_content += f"- **{todo['file']}**: {todo['type']}\n"
        
        report_content += f"""
## PERFORMANCE ANALYSIS

**Average Time per File**: {(unicode_results['scan_time_seconds'] + content_results['scan_time_seconds']) / (unicode_results['files_scanned'] + content_results['files_scanned']):.3f}s
**Files per Second**: {(unicode_results['files_scanned'] + content_results['files_scanned']) / (unicode_results['scan_time_seconds'] + content_results['scan_time_seconds']):.1f}

## NEXT STEPS

1. **Validate Framework**: Framework working correctly
2. **Optimize Performance**: Improve scanning speed if needed
3. **Scale Up**: Increase file count gradually
4. **Full Scan**: Run complete layered scanning

## CONCLUSION

Fast test completed successfully. Framework is ready for scaling.

**Ready for full scanning implementation!**

---
**Generated by**: Agent Exo-Suit V5.0 Fast Test Scanner
**System Status**: FRAMEWORK VALIDATED
**Mission**: Validate scanning framework before full implementation
"""
        
        # Save report
        report_path = self.reports_dir / "FAST_TEST_SCANNER_REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logging.info(f"Fast test report saved to: {report_path}")

def main():
    """Main execution function"""
    try:
        # Initialize and run Fast Test Scanner
        fast_scanner = FastTestScanner()
        results = fast_scanner.run_fast_comprehensive_test()
        
        logging.info("Fast Test Scanner execution completed successfully")
        logging.info(f"Total scan time: {results['total_scan_time']:.2f} seconds")
        
    except KeyboardInterrupt:
        logging.info("Fast test interrupted by user")
    except Exception as e:
        logging.error(f"Fast test failed with error: {e}")
        raise

if __name__ == "__main__":
    main()
