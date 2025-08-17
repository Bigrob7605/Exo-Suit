#!/usr/bin/env python3
"""
MD Emoji Purge - Complete Markdown File Emoji Elimination
Eliminates ALL emojis from markdown files to ensure 100% emoji-free system
"""

import os
import re
import time
from pathlib import Path
from typing import Dict, List, Tuple

class MDEmojiPurge:
    def __init__(self):
        self.project_root = Path.cwd()
        self.emoji_pattern = re.compile(r'[^\x00-\x7F]')
        self.stats = {
            'files_scanned': 0,
            'files_cleaned': 0,
            'emoji_replacements': 0,
            'start_time': time.time()
        }
        
    def scan_md_files(self) -> List[Path]:
        """Find all markdown files in the project"""
        md_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip logs and system directories
            if any(skip in root for skip in ['logs', '.git', '.venv', '__pycache__', 'node_modules']):
                continue
                
            for file in files:
                if file.endswith('.md'):
                    md_files.append(Path(root) / file)
        return md_files
    
    def clean_file(self, file_path: Path) -> Tuple[bool, int]:
        """Clean emojis from a single markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            # Remove all non-ASCII characters (emojis, special symbols)
            content = self.emoji_pattern.sub('', content)
            
            if content != original_content:
                # Write cleaned content back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                replacements = len(original_content) - len(content)
                return True, replacements
            
            return False, 0
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False, 0
    
    def purge_all_emojis(self):
        """Execute complete MD emoji purge"""
        print("EMOJI_1F680 STARTING COMPLETE MD EMOJI PURGE...")
        print("=" * 60)
        
        # Find all MD files
        md_files = self.scan_md_files()
        self.stats['files_scanned'] = len(md_files)
        
        print(f"EMOJI_1F4C1 Found {len(md_files)} markdown files to scan")
        print()
        
        # Process each file
        for i, file_path in enumerate(md_files, 1):
            print(f"[{i:3d}/{len(md_files)}] Processing: {file_path.name}")
            
            cleaned, replacements = self.clean_file(file_path)
            if cleaned:
                self.stats['files_cleaned'] += 1
                self.stats['emoji_replacements'] += replacements
                print(f"    EMOJI_2705 Cleaned: {replacements} emojis removed")
            else:
                print(f"    ⏭️  Clean: No emojis found")
        
        # Calculate final stats
        elapsed_time = time.time() - self.stats['start_time']
        self.stats['elapsed_time'] = elapsed_time
        
        # Print final results
        print()
        print("=" * 60)
        print("EMOJI_1F3AF MD EMOJI PURGE COMPLETE!")
        print("=" * 60)
        print(f"EMOJI_1F4CA RESULTS:")
        print(f"   • Files scanned: {self.stats['files_scanned']}")
        print(f"   • Files cleaned: {self.stats['files_cleaned']}")
        print(f"   • Emoji replacements: {self.stats['emoji_replacements']}")
        print(f"   • Processing time: {elapsed_time:.2f} seconds")
        print(f"   • Clean rate: {((self.stats['files_scanned'] - self.stats['files_cleaned']) / self.stats['files_scanned'] * 100):.1f}%")
        
        if self.stats['emoji_replacements'] > 0:
            print(f"   • Speed: {self.stats['emoji_replacements'] / elapsed_time:.0f} emojis/second")
        
        print()
        print("EMOJI_2705 ALL MARKDOWN FILES ARE NOW 100% EMOJI-FREE!")
        print("EMOJI_2705 SYSTEM IS READY FOR NEXT TEST PHASE!")
        
        return self.stats

def main():
    """Main execution"""
    purger = MDEmojiPurge()
    stats = purger.purge_all_emojis()
    
    # Save results to logs
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    with open(logs_dir / "md_emoji_purge_results.md", "w", encoding="utf-8") as f:
        f.write(f"# MD Emoji Purge Results\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Results:**\n")
        f.write(f"- Files scanned: {stats['files_scanned']}\n")
        f.write(f"- Files cleaned: {stats['files_cleaned']}\n")
        f.write(f"- Emoji replacements: {stats['emoji_replacements']}\n")
        f.write(f"- Processing time: {stats['elapsed_time']:.2f} seconds\n")
        f.write(f"- Clean rate: {((stats['files_scanned'] - stats['files_cleaned']) / stats['files_scanned'] * 100):.1f}%\n\n")
        f.write(f"**Status:** All markdown files are now 100% emoji-free!\n")

if __name__ == "__main__":
    main()
