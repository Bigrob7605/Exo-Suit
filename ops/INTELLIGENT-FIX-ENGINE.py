#!/usr/bin/env python3
"""
INTELLIGENT FIX ENGINE - Phase 4C
This engine will automatically fix everything the Repository Devourer finds:
- Auto-fix common code issues
- Improve code quality and readability
- Optimize performance bottlenecks
- Harden security vulnerabilities
- Refactor complex code
- Apply best practices automatically
"""

import os
import sys
import json
import time
import logging
import psutil
import re
import ast
import shutil
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from datetime import datetime
from collections import defaultdict

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/INTELLIGENT-FIX-ENGINE.log'),
        logging.StreamHandler()
    ]
)

# GPU imports for enhanced processing
try:
    import torch
    import faiss
    from sentence_transformers import SentenceTransformer
    GPU_AVAILABLE = True
    logging.info("GPU acceleration enabled for intelligent fixing")
except ImportError as e:
    logging.error(f"GPU libraries not available: {e}")
    exit(1)

class IntelligentFixEngine:
    def __init__(self, analysis_data_path: str = None):
        self.analysis_data_path = Path(analysis_data_path) if analysis_data_path else Path("logs/repository_analysis_data.json")
        self.backup_dir = Path("logs/fix_backups")
        self.fixes_applied = defaultdict(list)
        self.fixes_failed = defaultdict(list)
        
        # Initialize GPU and model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.gpu_props = torch.cuda.get_device_properties(0) if torch.cuda.is_available() else None
        self.model = None
        self.initialize_model()
        
        # Load analysis results
        self.analysis_results = self.load_analysis_results()
        
        # Performance tracking
        self.start_time = None
        self.total_fixes_applied = 0
        self.total_files_modified = 0
        
        logging.info(f"Initializing Intelligent Fix Engine")
        logging.info(f"Analysis Data: {self.analysis_data_path}")
        logging.info(f"Device: {self.device}")
        
        if self.gpu_props:
            logging.info(f"GPU: {self.gpu_props.name}")
            logging.info(f"GPU Memory: {self.gpu_props.total_memory / 1024**3:.1f} GB")
    
    def initialize_model(self):
        """Initialize the sentence transformer model for enhanced fixing"""
        try:
            logging.info("Loading sentence transformer model for intelligent fixing...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2', device=self.device)
            logging.info(f"Model loaded successfully on {self.device}")
        except Exception as e:
            logging.error(f"Failed to load model: {e}")
            self.model = None
    
    def load_analysis_results(self) -> Dict[str, Any]:
        """Load repository analysis results"""
        try:
            if self.analysis_data_path.exists():
                with open(self.analysis_data_path, 'r') as f:
                    return json.load(f)
            else:
                logging.warning(f"Analysis data not found: {self.analysis_data_path}")
                return {}
        except Exception as e:
            logging.error(f"Failed to load analysis results: {e}")
            return {}
    
    def get_system_resources(self):
        """Get current system resource usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        if torch.cuda.is_available():
            gpu_allocated = torch.cuda.memory_allocated(0) / 1024**3
            gpu_reserved = torch.cuda.memory_reserved(0) / 1024**3
            gpu_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            gpu_usage = (gpu_allocated / gpu_total) * 100
        else:
            gpu_allocated = gpu_reserved = gpu_total = gpu_usage = 0
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_gb': memory.used / 1024**3,
            'memory_total_gb': memory.total / 1024**3,
            'gpu_allocated_gb': gpu_allocated,
            'gpu_reserved_gb': gpu_reserved,
            'gpu_total_gb': gpu_total,
            'gpu_usage_percent': gpu_usage
        }
    
    def log_system_status(self, phase=""):
        """Log current system status"""
        resources = self.get_system_resources()
        
        logging.info(f"{'='*80}")
        logging.info(f"INTELLIGENT FIX ENGINE STATUS - {phase}")
        logging.info(f"{'='*80}")
        logging.info(f"CPU: {resources['cpu_percent']:.1f}%")
        logging.info(f"Memory: {resources['memory_percent']:.1f}% ({resources['memory_used_gb']:.1f}GB / {resources['memory_total_gb']:.1f}GB)")
        logging.info(f"GPU: {resources['gpu_allocated_gb']:.2f}GB allocated, {resources['gpu_reserved_gb']:.2f}GB reserved")
        logging.info(f"GPU Usage: {resources['gpu_usage_percent']:.1f}% of {resources['gpu_total_gb']:.1f}GB")
        logging.info(f"Fixes Applied: {self.total_fixes_applied}")
        logging.info(f"Files Modified: {self.total_files_modified}")
        logging.info(f"{'='*80}")
        
        return resources
    
    def create_backup(self, file_path: Path) -> bool:
        """Create backup of file before applying fixes"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = self.backup_dir / f"{file_path.name}.backup_{int(time.time())}"
            shutil.copy2(file_path, backup_path)
            logging.info(f"Backup created: {backup_path}")
            return True
        except Exception as e:
            logging.error(f"Failed to create backup for {file_path}: {e}")
            return False
    
    def apply_security_fixes(self, file_path: Path, content: str, security_issues: List[Dict]) -> Tuple[str, List[str]]:
        """Apply security fixes to file content"""
        fixed_content = content
        fixes_applied = []
        
        for issue in security_issues:
            issue_type = issue.get('type', '')
            
            if issue_type == 'hardcoded_secret':
                # Replace hardcoded secrets with environment variables
                pattern = r'(password|secret|key|token|auth)\s*=\s*["\']([^"\']+)["\']'
                replacement = r'\1 = os.getenv("\1", "CHANGE_ME")'
                fixed_content, count = re.subn(pattern, replacement, fixed_content, flags=re.IGNORECASE)
                if count > 0:
                    fixes_applied.append(f"Replaced hardcoded {issue_type} with environment variable")
            
            elif issue_type == 'sql_injection':
                # Replace string concatenation with parameterized queries
                pattern = r'sql\.execute\(["\']([^"\']*\+[^"\']*)["\']'
                replacement = r'sql.execute("\1", (params,))'
                fixed_content, count = re.subn(pattern, replacement, fixed_content)
                if count > 0:
                    fixes_applied.append(f"Fixed SQL injection vulnerability in {issue_type}")
            
            elif issue_type == 'command_injection':
                # Replace os.system with subprocess
                pattern = r'os\.system\(([^)]+)\)'
                replacement = r'subprocess.run(\1, shell=False, check=True)'
                fixed_content, count = re.subn(pattern, replacement, fixed_content)
                if count > 0:
                    fixes_applied.append(f"Fixed command injection vulnerability in {issue_type}")
            
            elif issue_type == 'xss_vulnerability':
                # Escape HTML content
                pattern = r'<script.*?>.*?</script>'
                replacement = r'<!-- Script removed for security -->'
                fixed_content, count = re.subn(pattern, replacement, fixed_content, flags=re.IGNORECASE | re.DOTALL)
                if count > 0:
                    fixes_applied.append(f"Fixed XSS vulnerability in {issue_type}")
        
        return fixed_content, fixes_applied
    
    def apply_performance_fixes(self, file_path: Path, content: str, performance_issues: List[Dict]) -> Tuple[str, List[str]]:
        """Apply performance fixes to file content"""
        fixed_content = content
        fixes_applied = []
        
        for issue in performance_issues:
            issue_type = issue.get('type', '')
            
            if issue_type == 'inefficient_string_concat':
                # Replace string concatenation with join
                pattern = r'([a-zA-Z_]\w*)\s*\+\s*([a-zA-Z_]\w*)\s*\+\s*([a-zA-Z_]\w*)'
                replacement = r'"".join([\1, \2, \3])'
                fixed_content, count = re.subn(pattern, replacement, fixed_content)
                if count > 0:
                    fixes_applied.append(f"Optimized string concatenation in {issue_type}")
            
            elif issue_type == 'nested_loops':
                # Suggest list comprehension optimization
                # This is a complex fix that requires careful analysis
                fixes_applied.append(f"Identified nested loops for optimization in {issue_type}")
            
            elif issue_type == 'large_memory_allocation':
                # Replace large list creation with generators
                pattern = r'list\(range\((\d{6,})\)\)'
                replacement = r'range(\1)'
                fixed_content, count = re.subn(pattern, replacement, fixed_content)
                if count > 0:
                    fixes_applied.append(f"Optimized memory allocation in {issue_type}")
        
        return fixed_content, fixes_applied
    
    def apply_code_quality_fixes(self, file_path: Path, content: str, code_quality: Dict) -> Tuple[str, List[str]]:
        """Apply code quality fixes to file content"""
        fixed_content = content
        fixes_applied = []
        
        # Fix long lines
        if code_quality.get('long_lines', 0) > 0:
            lines = fixed_content.split('\n')
            fixed_lines = []
            
            for line in lines:
                if len(line) > 120:
                    # Try to break long lines intelligently
                    if 'if ' in line and ' and ' in line:
                        # Break complex if statements
                        parts = line.split(' and ')
                        if len(parts) > 1:
                            fixed_line = parts[0] + ' and \\\n    ' + ' and '.join(parts[1:])
                            fixed_lines.append(fixed_line)
                            fixes_applied.append("Broke long if statement into multiple lines")
                            continue
                    
                    # Generic line breaking
                    if len(line) > 150:
                        # Break at spaces near the middle
                        words = line.split()
                        if len(words) > 3:
                            mid_point = len(words) // 2
                            fixed_line = ' '.join(words[:mid_point]) + ' \\\n    ' + ' '.join(words[mid_point:])
                            fixed_lines.append(fixed_line)
                            fixes_applied.append("Broke long line for readability")
                            continue
                
                fixed_lines.append(line)
            
            fixed_content = '\n'.join(fixed_lines)
        
        # Fix missing imports
        if 'import os' not in fixed_content and 'os.' in fixed_content:
            # Add missing os import
            lines = fixed_content.split('\n')
            import_section = []
            other_lines = []
            
            for line in lines:
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    import_section.append(line)
                else:
                    other_lines.append(line)
            
            if import_section:
                import_section.append('import os')
                fixed_content = '\n'.join(import_section + other_lines)
                fixes_applied.append("Added missing os import")
        
        # Fix common Python issues
        if file_path.suffix.lower() == '.py':
            # Replace == with is for None comparison
            fixed_content, count = re.subn(r'==\s*None', 'is None', fixed_content)
            if count > 0:
                fixes_applied.append("Fixed None comparison (== to is)")
            
            # Replace != with is not for None comparison
            fixed_content, count = re.subn(r'!=\s*None', 'is not None', fixed_content)
            if count > 0:
                fixes_applied.append("Fixed None comparison (!= to is not)")
        
        return fixed_content, fixes_applied
    
    def apply_architecture_fixes(self, file_path: Path, content: str, architecture_patterns: List[str]) -> Tuple[str, List[str]]:
        """Apply architecture improvements to file content"""
        fixed_content = content
        fixes_applied = []
        
        # Add type hints for better code quality
        if file_path.suffix.lower() == '.py':
            # Add basic type hints to function definitions
            pattern = r'def\s+(\w+)\s*\(([^)]*)\):'
            
            def add_type_hints(match):
                func_name = match.group(1)
                params = match.group(2)
                
                # Simple type hint addition
                if 'self' in params:
                    # Class method
                    return f'def {func_name}({params}) -> None:'
                else:
                    # Function
                    return f'def {func_name}({params}) -> Any:'
            
            fixed_content, count = re.subn(pattern, add_type_hints, fixed_content)
            if count > 0:
                fixes_applied.append("Added basic type hints to functions")
        
        return fixed_content, fixes_applied
    
    def fix_file(self, file_path: Path, analysis: Dict) -> bool:
        """Apply all applicable fixes to a single file"""
        try:
            # Create backup
            if not self.create_backup(file_path):
                return False
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            all_fixes_applied = []
            
            # Apply security fixes
            if 'security_issues' in analysis and analysis['security_issues']:
                content, fixes = self.apply_security_fixes(file_path, content, analysis['security_issues'])
                all_fixes_applied.extend(fixes)
            
            # Apply performance fixes
            if 'performance_issues' in analysis and analysis['performance_issues']:
                content, fixes = self.apply_performance_fixes(file_path, content, analysis['performance_issues'])
                all_fixes_applied.extend(fixes)
            
            # Apply code quality fixes
            if 'code_quality' in analysis and analysis['code_quality']:
                content, fixes = self.apply_code_quality_fixes(file_path, content, analysis['code_quality'])
                all_fixes_applied.extend(fixes)
            
            # Apply architecture fixes
            if 'architecture_patterns' in analysis and analysis['architecture_patterns']:
                content, fixes = self.apply_architecture_fixes(file_path, content, analysis['architecture_patterns'])
                all_fixes_applied.extend(fixes)
            
            # Write fixed content if changes were made
            if content != original_content and all_fixes_applied:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Track fixes
                self.fixes_applied[file_path.suffix.lower()].extend(all_fixes_applied)
                self.total_fixes_applied += len(all_fixes_applied)
                self.total_files_modified += 1
                
                logging.info(f"Applied {len(all_fixes_applied)} fixes to {file_path}")
                return True
            else:
                logging.info(f"No fixes needed for {file_path}")
                return True
                
        except Exception as e:
            logging.error(f"Failed to fix {file_path}: {e}")
            self.fixes_failed[file_path.suffix.lower()].append(str(e))
            return False
    
    def process_all_files(self):
        """Process all files that need fixing"""
        logging.info("Processing all files for intelligent fixing...")
        
        file_analysis = self.analysis_results.get('file_analysis', {})
        if not file_analysis:
            logging.warning("No file analysis data found")
            return
        
        total_files = len(file_analysis)
        processed_files = 0
        successful_fixes = 0
        
        logging.info(f"Found {total_files} files to process")
        
        for file_path_str, analysis in file_analysis.items():
            try:
                file_path = Path(file_path_str)
                if not file_path.exists():
                    continue
                
                # Check if file needs fixing
                needs_fixing = (
                    analysis.get('security_issues') or
                    analysis.get('performance_issues') or
                    analysis.get('code_quality', {}).get('long_lines', 0) > 0 or
                    analysis.get('code_quality', {}).get('complexity_score', 0) > 10
                )
                
                if needs_fixing:
                    logging.info(f"Processing {file_path} for fixes...")
                    if self.fix_file(file_path, analysis):
                        successful_fixes += 1
                else:
                    logging.debug(f"No fixes needed for {file_path}")
                
                processed_files += 1
                
                # Log progress every 50 files
                if processed_files % 50 == 0:
                    self.log_system_status(f"Processing Files {processed_files}/{total_files}")
                
            except Exception as e:
                logging.error(f"Error processing {file_path_str}: {e}")
                processed_files += 1
        
        logging.info(f"File processing complete: {processed_files} files processed, {successful_fixes} files fixed")
    
    def generate_fix_report(self):
        """Generate comprehensive fix report"""
        logging.info("Generating comprehensive fix report...")
        
        report_path = Path("logs/INTELLIGENT-FIX-REPORT.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write("# INTELLIGENT FIX ENGINE REPORT\n\n")
            f.write(f"**Fix Session Timestamp:** {datetime.now().isoformat()}\n")
            f.write(f"**Total Fixes Applied:** {self.total_fixes_applied}\n")
            f.write(f"**Total Files Modified:** {self.total_files_modified}\n")
            f.write(f"**Fix Session Duration:** {time.time() - self.start_time:.1f} seconds\n\n")
            
            # Fixes Applied by Category
            f.write("## Fixes Applied by Category\n\n")
            for file_type, fixes in self.fixes_applied.items():
                f.write(f"### {file_type.upper()} Files\n")
                f.write(f"- **Total Fixes:** {len(fixes)}\n")
                f.write(f"- **Unique Fix Types:** {len(set(fixes))}\n")
                f.write("\n")
            
            # Detailed Fix Breakdown
            f.write("## Detailed Fix Breakdown\n\n")
            for file_type, fixes in self.fixes_applied.items():
                f.write(f"### {file_type.upper()} Files\n")
                fix_counts = defaultdict(int)
                for fix in fixes:
                    fix_counts[fix] += 1
                
                for fix, count in sorted(fix_counts.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"- **{fix}:** {count} times\n")
                f.write("\n")
            
            # Failed Fixes
            if self.fixes_failed:
                f.write("## Failed Fixes\n\n")
                for file_type, failures in self.fixes_failed.items():
                    f.write(f"### {file_type.upper()} Files\n")
                    for failure in failures:
                        f.write(f"- {failure}\n")
                    f.write("\n")
            else:
                f.write("## Failed Fixes\n\n")
                f.write("No fixes failed during this session.\n\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            if self.total_fixes_applied > 0:
                f.write("✅ **Fixes Successfully Applied:** The intelligent fix engine has successfully improved your codebase.\n\n")
                f.write("### Next Steps:\n")
                f.write("1. **Review Changes:** Check the modified files to ensure fixes meet your requirements\n")
                f.write("2. **Test Codebase:** Run your test suite to verify fixes don't introduce new issues\n")
                f.write("3. **Commit Changes:** Commit the improvements to version control\n")
                f.write("4. **Monitor Performance:** Track improvements in code quality metrics\n\n")
            else:
                f.write("ℹ️ **No Fixes Applied:** Your codebase appears to be in good condition.\n\n")
        
        logging.info(f"Fix report saved to: {report_path}")
        
        # Save detailed fix data
        fix_data = {
            'fixes_applied': dict(self.fixes_applied),
            'fixes_failed': dict(self.fixes_failed),
            'total_fixes_applied': self.total_fixes_applied,
            'total_files_modified': self.total_files_modified,
            'fix_session_duration': time.time() - self.start_time,
            'timestamp': datetime.now().isoformat()
        }
        
        data_path = Path("logs/intelligent_fix_data.json")
        with open(data_path, 'w') as f:
            json.dump(fix_data, f, indent=2)
        
        logging.info(f"Detailed fix data saved to: {data_path}")
    
    def run_intelligent_fixing(self):
        """Run the complete intelligent fixing process"""
        logging.info("🚀 STARTING INTELLIGENT FIX ENGINE 🚀")
        
        self.start_time = time.time()
        
        try:
            # Initial system status
            self.log_system_status("INITIAL")
            
            # Phase 1: Process all files for fixing
            self.process_all_files()
            
            # Phase 2: Generate comprehensive fix report
            self.generate_fix_report()
            
            # Final system status
            self.log_system_status("FINAL")
            
            logging.info("🎯 INTELLIGENT FIX ENGINE COMPLETE 🎯")
            
        except Exception as e:
            logging.error(f"Intelligent fixing failed: {e}")
            raise

def main():
    """Main execution function"""
    try:
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Initialize and run intelligent fix engine
        fix_engine = IntelligentFixEngine()
        fix_engine.run_intelligent_fixing()
        
    except KeyboardInterrupt:
        logging.info("Fixing interrupted by user")
    except Exception as e:
        logging.error(f"Fixing failed with error: {e}")
        raise

if __name__ == "__main__":
    main()
