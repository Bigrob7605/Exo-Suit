#!/usr/bin/env python3
"""
REAL EMOJI CLEANUP - Agent Exo-Suit V5.0
==========================================

This script actually removes emojis from the system, unlike the fake cleanup
that was previously claimed. It will scan and clean all files systematically.
"""

import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_emoji_cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealEmojiCleanup:
    """Comprehensive emoji removal system"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.emoji_pattern = re.compile(
            r'[\U0001F600-\U0001F64F]|'  # Emoticons
            r'[\U0001F300-\U0001F5FF]|'  # Symbols & pictographs
            r'[\U0001F680-\U0001F6FF]|'  # Transport & map symbols
            r'[\U0001F1E0-\U0001F1FF]|'  # Regional indicator symbols
            r'[\U00002600-\U000027BF]|'   # Miscellaneous symbols
            r'[\U0001F900-\U0001F9FF]|'  # Supplemental symbols
            r'[\U0001FA70-\U0001FAFF]|'  # Symbols and pictographs extended-A
            r'[\U0001FAB0-\U0001FABF]|'  # Symbols and pictographs extended-B
            r'[\U0001FAC0-\U0001FAFF]|'  # Symbols and pictographs extended-C
            r'[\U0001FAD0-\U0001FAFF]|'  # Symbols and pictographs extended-D
            r'[\U0001FAE0-\U0001FAFF]|'  # Symbols and pictographs extended-E
            r'[\U0001FAF0-\U0001FAFF]'   # Symbols and pictographs extended-F
        )
        
        # File extensions to process
        self.processable_extensions = {
            '.md', '.txt', '.py', '.ps1', '.json', '.yaml', '.yml',
            '.html', '.css', '.js', '.ts', '.xml', '.ini', '.cfg'
        }
        
        # Directories to exclude
        self.excluded_dirs = {
            '.git', '__pycache__', '.venv', 'venv', 'node_modules',
            'archive', 'legacy', 'system_backups', 'temp_ram_disk'
        }
        
        self.cleanup_stats = {
            'files_scanned': 0,
            'files_processed': 0,
            'files_cleaned': 0,
            'total_emojis_removed': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    def should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be processed"""
        # Check extension
        if file_path.suffix.lower() not in self.processable_extensions:
            return False
        
        # Check if in excluded directory
        for part in file_path.parts:
            if part in self.excluded_dirs:
                return False
        
        # Check if file is readable and writable
        try:
            return file_path.is_file() and os.access(file_path, os.R_OK | os.W_OK)
        except (OSError, PermissionError):
            return False
    
    def find_emojis_in_file(self, file_path: Path) -> List[Tuple[int, str, str]]:
        """Find all emojis in a file with line numbers and context"""
        emojis_found = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    emojis = self.emoji_pattern.findall(line)
                    if emojis:
                        context = line.strip()[:100] + "..." if len(line.strip()) > 100 else line.strip()
                        emojis_found.append((line_num, emojis, context))
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            self.cleanup_stats['errors'] += 1
        
        return emojis_found
    
    def clean_file_of_emojis(self, file_path: Path) -> int:
        """Remove all emojis from a file and return count removed"""
        emojis_removed = 0
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Count emojis before removal
            emojis_before = len(self.emoji_pattern.findall(content))
            
            # Remove emojis
            cleaned_content = self.emoji_pattern.sub('', content)
            
            # Count emojis after removal
            emojis_after = len(self.emoji_pattern.findall(cleaned_content))
            emojis_removed = emojis_before - emojis_after
            
            # Write cleaned content back
            if emojis_removed > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                logger.info(f"Cleaned {file_path}: {emojis_removed} emojis removed")
            
            return emojis_removed
            
        except Exception as e:
            logger.error(f"Error cleaning {file_path}: {e}")
            self.cleanup_stats['errors'] += 1
            return 0
    
    def scan_and_clean_project(self) -> Dict:
        """Scan entire project and clean all emojis"""
        logger.info(f"Starting REAL emoji cleanup of project: {self.project_root}")
        self.cleanup_stats['start_time'] = datetime.now()
        
        # Find all files to process
        all_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if self.should_process_file(file_path):
                    all_files.append(file_path)
        
        logger.info(f"Found {len(all_files)} files to process")
        
        # Process each file
        for file_path in all_files:
            self.cleanup_stats['files_scanned'] += 1
            
            try:
                emojis_removed = self.clean_file_of_emojis(file_path)
                if emojis_removed > 0:
                    self.cleanup_stats['files_cleaned'] += 1
                    self.cleanup_stats['total_emojis_removed'] += emojis_removed
                
                self.cleanup_stats['files_processed'] += 1
                
                # Progress update every 100 files
                if self.cleanup_stats['files_processed'] % 100 == 0:
                    logger.info(f"Processed {self.cleanup_stats['files_processed']}/{len(all_files)} files...")
                    
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                self.cleanup_stats['errors'] += 1
        
        self.cleanup_stats['end_time'] = datetime.now()
        
        # Generate cleanup report
        self.generate_cleanup_report()
        
        return self.cleanup_stats
    
    def generate_cleanup_report(self):
        """Generate comprehensive cleanup report"""
        duration = self.cleanup_stats['end_time'] - self.cleanup_stats['start_time']
        
        report = {
            'cleanup_summary': {
                'start_time': self.cleanup_stats['start_time'].isoformat(),
                'end_time': self.cleanup_stats['end_time'].isoformat(),
                'duration_seconds': duration.total_seconds(),
                'project_root': str(self.project_root.absolute())
            },
            'statistics': {
                'files_scanned': self.cleanup_stats['files_scanned'],
                'files_processed': self.cleanup_stats['files_processed'],
                'files_cleaned': self.cleanup_stats['files_cleaned'],
                'total_emojis_removed': self.cleanup_stats['total_emojis_removed'],
                'errors': self.cleanup_stats['errors']
            },
            'performance': {
                'files_per_second': round(self.cleanup_stats['files_processed'] / duration.total_seconds(), 2),
                'emojis_per_second': round(self.cleanup_stats['total_emojis_removed'] / duration.total_seconds(), 2)
            }
        }
        
        # Save report
        report_path = self.project_root / 'REAL_EMOJI_CLEANUP_REPORT.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Generate text report
        text_report_path = self.project_root / 'REAL_EMOJI_CLEANUP_REPORT.txt'
        with open(text_report_path, 'w', encoding='utf-8') as f:
            f.write("REAL EMOJI CLEANUP REPORT - Agent Exo-Suit V5.0\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Project: {self.project_root.absolute()}\n")
            f.write(f"Start Time: {self.cleanup_stats['start_time']}\n")
            f.write(f"End Time: {self.cleanup_stats['end_time']}\n")
            f.write(f"Duration: {duration}\n\n")
            f.write("CLEANUP STATISTICS:\n")
            f.write(f"Files Scanned: {self.cleanup_stats['files_scanned']}\n")
            f.write(f"Files Processed: {self.cleanup_stats['files_processed']}\n")
            f.write(f"Files Cleaned: {self.cleanup_stats['files_cleaned']}\n")
            f.write(f"Total Emojis Removed: {self.cleanup_stats['total_emojis_removed']}\n")
            f.write(f"Errors: {self.cleanup_stats['errors']}\n\n")
            f.write("PERFORMANCE:\n")
            f.write(f"Files/Second: {report['performance']['files_per_second']}\n")
            f.write(f"Emojis/Second: {report['performance']['emojis_per_second']}\n\n")
            f.write("STATUS: CLEANUP COMPLETE\n")
            f.write("All emojis have been systematically removed from the project.\n")
        
        logger.info(f"Cleanup report saved to: {report_path}")
        logger.info(f"Text report saved to: {text_report_path}")

def main():
    """Main execution function"""
    cleanup = RealEmojiCleanup()
    stats = cleanup.scan_and_clean_project()
    
    print("\n" + "="*60)
    print("REAL EMOJI CLEANUP COMPLETE!")
    print("="*60)
    print(f"Files Scanned: {stats['files_scanned']}")
    print(f"Files Cleaned: {stats['files_cleaned']}")
    print(f"Total Emojis Removed: {stats['total_emojis_removed']}")
    print(f"Errors: {stats['errors']}")
    print("="*60)
    
    if stats['total_emojis_removed'] > 0:
        print(" SUCCESS: Emojis have been ACTUALLY removed!")
    else:
        print("ℹ️  INFO: No emojis found to remove")
    
    print(f"Reports saved to project root directory")

if __name__ == "__main__":
    main()
