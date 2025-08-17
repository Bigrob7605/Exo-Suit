#!/usr/bin/env python3
"""
LAYERED SCANNING SYSTEM - Agent Exo-Suit V5.0
Comprehensive project scanning through multiple layers to catch ALL issues.
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
        logging.FileHandler('logs/LAYERED_SCANNING_SYSTEM.log'),
        logging.StreamHandler()
    ]
)

class LayeredScanningSystem:
    def __init__(self):
        self.project_root = Path(".")
        self.logs_dir = Path("logs")
        self.reports_dir = Path("reports")
        self.scan_dir = Path("scan_results")
        
        # Create necessary directories
        self.logs_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        self.scan_dir.mkdir(exist_ok=True)
        
        # Project boundary detection (reuse from VisionGap Engine)
        self.project_boundaries = self._detect_project_boundaries()
        self.main_project_name = self._identify_main_project()
        self.toolbox_identifiers = self._identify_toolbox_system()
        
        # Scanning results storage
        self.scan_results = {
            'layer1_unicode': {},
            'layer2_content_quality': {},
            'layer3_legacy_systems': {},
            'layer4_architecture': {},
            'layer5_performance': {}
        }
        
        # Visual progress indicator system
        self.progress_active = False
        self.progress_thread = None
        
        logging.info("Initializing LAYERED SCANNING SYSTEM")
        logging.info("Mission: Comprehensive project scanning through multiple layers")
        logging.info(f"Main Project: {self.main_project_name}")
        logging.info(f"Toolbox Excluded: {self.toolbox_identifiers['name']}")
    
    def _start_progress_indicator(self, layer_name: str):
        """Start the cool visual progress indicator"""
        self.progress_active = True
        self.progress_thread = threading.Thread(target=self._progress_animation, args=(layer_name,), daemon=True)
        self.progress_thread.start()
        logging.info(f"Visual progress indicator started for {layer_name}")
    
    def _stop_progress_indicator(self):
        """Stop the visual progress indicator"""
        self.progress_active = False
        if self.progress_thread:
            self.progress_thread.join(timeout=1)
        print("\n")  # Clean line break
        logging.info("Visual progress indicator stopped")
    
    def _progress_animation(self, layer_name: str):
        """Cool animated progress indicator with green dots and patterns"""
        import sys
        
        # Cool animation patterns
        patterns = [
            "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏",  # Spinning dots
            "▌▀▐▄",                          # Block patterns
            "◢◣◤◥",                          # Triangle patterns
            "▁▂▃▄▅▆▇█",                      # Bar patterns
            "●○◐◑◒◓",                        # Circle patterns
        ]
        
        pattern = patterns[0]  # Start with spinning dots
        pattern_index = 0
        char_index = 0
        
        while self.progress_active:
            try:
                # Create the animated line
                current_char = pattern[char_index]
                status_line = f"\r[SCAN] {layer_name} Scanning... {current_char} "
                
                # Add file count info if available
                if hasattr(self, 'current_files_scanned'):
                    status_line += f"[Files: {self.current_files_scanned}] "
                
                # Add cool pattern transitions
                if char_index == len(pattern) - 1:
                    char_index = 0
                    pattern_index = (pattern_index + 1) % len(patterns)
                    pattern = patterns[pattern_index]
                else:
                    char_index += 1
                
                # Print with flush to ensure real-time updates
                print(status_line, end='', flush=True)
                
                # Sleep for smooth animation
                time.sleep(0.1)
                
            except Exception as e:
                # Fallback to simple dots if animation fails
                print(f"\r[SCAN] {layer_name} Scanning... *", end='', flush=True)
                time.sleep(0.2)
    
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
    
    def _identify_toolbox_system(self) -> Dict[str, Any]:
        """Identify toolbox system"""
        return {
            'name': 'Universal Open Science Toolbox With Kai',
            'excluded_from_analysis': True
        }
    
    def _is_toolbox_file(self, file_path: Path) -> bool:
        """Check if file is part of toolbox system"""
        file_str = str(file_path)
        for excluded_dir in self.project_boundaries['excluded_directories']:
            if excluded_dir in file_str:
                return True
        return False
    
    def run_layer1_unicode_scan(self) -> Dict[str, Any]:
        """Layer 1: Unicode/Emoji Scanner"""
        logging.info("LAYER 1: Starting Unicode/Emoji Scanner...")
        
        # Start visual progress indicator
        self._start_progress_indicator("Unicode/Emoji")
        
        scan_results = {
            'files_scanned': 0,
            'files_with_unicode': 0,
            'files_with_emojis': 0,
            'unicode_issues': [],
            'clean_files': [],
            'total_issues_found': 0
        }
        
        # Scan all text-based files
        text_extensions = ['.md', '.txt', '.py', '.js', '.json', '.yaml', '.yml', '.ini', '.conf', '.ps1', '.bat', '.sh']
        
        for ext in text_extensions:
            files = list(self.project_root.rglob(f"*{ext}"))
            for file_path in files:
                if self._is_toolbox_file(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    scan_results['files_scanned'] += 1
                    self.current_files_scanned = scan_results['files_scanned']
                    
                    # Check for Unicode issues
                    unicode_issues = []
                    emoji_issues = []
                    
                    for i, char in enumerate(content):
                        if ord(char) > 127:  # Non-ASCII character
                            unicode_issues.append({
                                'position': i,
                                'character': char,
                                'unicode_code': ord(char),
                                'line': content[:i].count('\n') + 1
                            })
                            
                            # Check if it's an emoji
                            if 0x1F600 <= ord(char) <= 0x1F64F or 0x1F300 <= ord(char) <= 0x1F5FF:
                                emoji_issues.append({
                                    'position': i,
                                    'character': char,
                                    'line': content[:i].count('\n') + 1
                                })
                    
                    if unicode_issues:
                        scan_results['files_with_unicode'] += 1
                        scan_results['unicode_issues'].append({
                            'file': str(file_path),
                            'issues': unicode_issues,
                            'emoji_count': len(emoji_issues),
                            'total_unicode': len(unicode_issues)
                        })
                        scan_results['total_issues_found'] += len(unicode_issues)
                        
                        if emoji_issues:
                            scan_results['files_with_emojis'] += 1
                    else:
                        scan_results['clean_files'].append(str(file_path))
                        
                except Exception as e:
                    logging.warning(f"Could not scan {file_path}: {e}")
                    continue
        
        # Stop visual progress indicator
        self._stop_progress_indicator()
        
        logging.info(f"Layer 1 Complete: {scan_results['files_scanned']} files scanned")
        logging.info(f"Files with Unicode: {scan_results['files_with_unicode']}")
        logging.info(f"Files with Emojis: {scan_results['files_with_emojis']}")
        logging.info(f"Total Issues: {scan_results['total_issues_found']}")
        
        self.scan_results['layer1_unicode'] = scan_results
        return scan_results
    
    def run_layer2_content_quality_scan(self) -> Dict[str, Any]:
        """Layer 2: Content Quality Scanner"""
        logging.info("LAYER 2: Starting Content Quality Scanner...")
        
        # Start visual progress indicator
        self._start_progress_indicator("Content Quality")
        
        scan_results = {
            'files_scanned': 0,
            'placeholder_markers': [],
            'todo_items': [],
            'fixme_items': [],
            'broken_links': [],
            'incomplete_sections': [],
            'total_issues_found': 0
        }
        
        # Content quality patterns
        placeholder_patterns = [
            r'PLACEHOLDER', r'FILL_IN', r'ADD_HERE', r'COMPLETE_THIS',
            r'TO_BE_IMPLEMENTED', r'NOT_IMPLEMENTED', r'STUB'
        ]
        
        todo_patterns = [
            r'TODO[:\\s]', r'FIXME[:\\s]', r'BUG[:\\s]', r'HACK[:\\s]',
            r'XXX[:\\s]', r'NOTE[:\\s]', r'REVIEW[:\\s]'
        ]
        
        # Scan text files for content quality issues
        text_extensions = ['.md', '.txt', '.py', '.js', '.json', '.yaml', '.yml']
        
        for ext in text_extensions:
            files = list(self.project_root.rglob(f"*{ext}"))
            for file_path in files:
                if self._is_toolbox_file(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    scan_results['files_scanned'] += 1
                    self.current_files_scanned = scan_results['files_scanned']
                    
                    # Check for placeholder markers
                    for pattern in placeholder_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            scan_results['placeholder_markers'].append({
                                'file': str(file_path),
                                'pattern': pattern,
                                'position': match.start(),
                                'line': content[:match.start()].count('\n') + 1,
                                'context': content[max(0, match.start()-20):match.end()+20]
                            })
                            scan_results['total_issues_found'] += 1
                    
                    # Check for TODO items
                    for pattern in todo_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            # Extract the TODO content
                            line_start = content.rfind('\n', 0, match.start()) + 1
                            line_end = content.find('\n', match.end())
                            if line_end == -1:
                                line_end = len(content)
                            todo_line = content[line_start:line_end].strip()
                            
                            scan_results['todo_items'].append({
                                'file': str(file_path),
                                'type': pattern.replace('[:\\\\s]', '').strip(),
                                'position': match.start(),
                                'line': content[:match.start()].count('\n') + 1,
                                'content': todo_line
                            })
                            scan_results['total_issues_found'] += 1
                    
                    # Check for incomplete sections (very short content)
                    if len(content.strip()) < 50 and ext == '.md':
                        scan_results['incomplete_sections'].append({
                            'file': str(file_path),
                            'content_length': len(content.strip()),
                            'content_preview': content.strip()[:100]
                        })
                        scan_results['total_issues_found'] += 1
                        
                except Exception as e:
                    logging.warning(f"Could not scan {file_path}: {e}")
                    continue
        
        # Stop visual progress indicator
        self._stop_progress_indicator()
        
        logging.info(f"Layer 2 Complete: {scan_results['files_scanned']} files scanned")
        logging.info(f"Placeholder Markers: {len(scan_results['placeholder_markers'])}")
        logging.info(f"TODO Items: {len(scan_results['todo_items'])}")
        logging.info(f"Total Issues: {scan_results['total_issues_found']}")
        
        self.scan_results['layer2_content_quality'] = scan_results
        return scan_results
    
    def run_comprehensive_scan(self):
        """Run all scanning layers sequentially"""
        logging.info("STARTING COMPREHENSIVE LAYERED SCANNING")
        
        # Layer 1: Unicode/Emoji Scanner
        layer1_results = self.run_layer1_unicode_scan()
        
        # Layer 2: Content Quality Scanner
        layer2_results = self.run_layer2_content_quality_scan()
        
        # Generate comprehensive report
        self._generate_comprehensive_scan_report()
        
        logging.info("COMPREHENSIVE LAYERED SCANNING COMPLETE")
        return self.scan_results
    
    def _generate_comprehensive_scan_report(self):
        """Generate comprehensive scanning report"""
        logging.info("Generating comprehensive scanning report...")
        
        report_content = f"""# COMPREHENSIVE LAYERED SCANNING REPORT - Agent Exo-Suit V5.0

**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**Project**: {self.project_root.name}
**System**: Agent Exo-Suit V5.0 Layered Scanning System

## EXECUTIVE SUMMARY

Comprehensive layered scanning completed to identify ALL issues before repair phase.

## LAYER 1: UNICODE/EMOJI SCANNER RESULTS

**Files Scanned**: {self.scan_results['layer1_unicode']['files_scanned']}
**Files with Unicode Issues**: {self.scan_results['layer1_unicode']['files_with_unicode']}
**Files with Emojis**: {self.scan_results['layer1_unicode']['files_with_emojis']}
**Total Unicode Issues**: {self.scan_results['layer1_unicode']['total_issues_found']}

### Unicode Issues Found
"""
        
        for issue in self.scan_results['layer1_unicode']['unicode_issues']:
            report_content += f"""
**File**: {issue['file']}
- Unicode Issues: {issue['total_unicode']}
- Emoji Issues: {issue['emoji_count']}
"""
        
        report_content += f"""
## LAYER 2: CONTENT QUALITY SCANNER RESULTS

**Files Scanned**: {self.scan_results['layer2_content_quality']['files_scanned']}
**Placeholder Markers**: {len(self.scan_results['layer2_content_quality']['placeholder_markers'])}
**TODO Items**: {len(self.scan_results['layer2_content_quality']['todo_items'])}
**Total Issues**: {self.scan_results['layer2_content_quality']['total_issues_found']}

### Content Quality Issues Found
"""
        
        if self.scan_results['layer2_content_quality']['placeholder_markers']:
            report_content += "#### Placeholder Markers\n"
            for marker in self.scan_results['layer2_content_quality']['placeholder_markers']:
                report_content += f"- **{marker['file']}** (Line {marker['line']}): {marker['pattern']}\n"
        
        if self.scan_results['layer2_content_quality']['todo_items']:
            report_content += "#### TODO Items\n"
            for todo in self.scan_results['layer2_content_quality']['todo_items']:
                report_content += f"- **{todo['file']}** (Line {todo['line']}): {todo['type']} - {todo['content']}\n"
        
        report_content += f"""
## NEXT STEPS

1. **Address Unicode Issues**: Clean all emoji and non-ASCII characters
2. **Complete Placeholder Content**: Fill in all placeholder markers
3. **Resolve TODO Items**: Implement or remove all TODO markers
4. **Prepare for Repair Phase**: Use this report for comprehensive project healing

## CONCLUSION

Layered scanning has identified {self.scan_results['layer1_unicode']['total_issues_found'] + self.scan_results['layer2_content_quality']['total_issues_found']} total issues that must be addressed before repair phase.

**Ready for comprehensive project healing!**

---
**Generated by**: Agent Exo-Suit V5.0 Layered Scanning System
**System Status**: SCANNING COMPLETE
**Mission**: Identify ALL issues for repair phase preparation
"""
        
        # Save report
        report_path = self.reports_dir / "COMPREHENSIVE_LAYERED_SCANNING_REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logging.info(f"Comprehensive scanning report saved to: {report_path}")

def main():
    """Main execution function"""
    try:
        # Initialize and run Layered Scanning System
        scanning_system = LayeredScanningSystem()
        results = scanning_system.run_comprehensive_scan()
        
        logging.info("Layered Scanning System execution completed successfully")
        
    except KeyboardInterrupt:
        logging.info("Layered scanning interrupted by user")
    except Exception as e:
        logging.error(f"Layered scanning failed with error: {e}")
        raise

if __name__ == "__main__":
    main()
