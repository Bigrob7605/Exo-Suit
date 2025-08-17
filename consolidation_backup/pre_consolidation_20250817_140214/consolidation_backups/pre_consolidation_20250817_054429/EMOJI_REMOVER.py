#!/usr/bin/env python3
"""
Agent Exo-Suit V5.0 - Emoji Remover
Removes all emojis found by the emoji scanner
"""

import os
import re
import json
import unicodedata
from pathlib import Path
from typing import List, Dict, Tuple

def is_emoji(char: str) -> bool:
    """Check if a character is an emoji"""
    try:
        # Check if character is in emoji Unicode ranges
        if unicodedata.category(char) in ['So', 'Sk']:
            return True
        
        # Common emoji Unicode ranges
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
        
        code_point = ord(char)
        for start, end in emoji_ranges:
            if start <= code_point <= end:
                return True
                
        return False
    except:
        return False

def remove_emojis_from_file(file_path: str) -> Tuple[int, str]:
    """Remove emojis from a file and return count removed and backup path"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        original_content = content
        emoji_count = 0
        
        # Remove emojis character by character
        cleaned_content = ""
        for char in content:
            if is_emoji(char):
                emoji_count += 1
            else:
                cleaned_content += char
        
        if emoji_count > 0:
            # Create backup
            backup_path = f"{file_path}.emoji_backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write cleaned content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
                
        return emoji_count, backup_path if emoji_count > 0 else ""
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0, ""

def process_emoji_report(report_path: str = "PYTHON_EMOJI_REPORT.json"):
    """Process the emoji report and remove all emojis"""
    if not os.path.exists(report_path):
        print(f"Emoji report not found: {report_path}")
        return
    
    print("AGENT EXO-SUIT V5.0 - EMOJI REMOVER")
    print("=" * 50)
    
    # Load the emoji report
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
    except Exception as e:
        print(f"Error loading emoji report: {e}")
        return
    
    # Extract emoji detections
    if 'Detections' not in report_data:
        print("No emoji detections found in report")
        return
    
    detections = report_data['Detections']
    print(f"Found {len(detections)} emoji detections in report")
    
    # Group by file
    files_with_emojis = {}
    for detection in detections:
        file_path = detection['file_path']
        if file_path not in files_with_emojis:
            files_with_emojis[file_path] = []
        files_with_emojis[file_path].append(detection)
    
    print(f"Files with emojis: {len(files_with_emojis)}")
    
    # Ask for confirmation
    response = input(f"\nRemove {len(detections)} emojis from {len(files_with_emojis)} files? (yes/no): ").lower().strip()
    
    if response not in ['yes', 'y']:
        print("Emoji removal cancelled.")
        return
    
    # Process files
    print("\nRemoving emojis...")
    total_removed = 0
    files_processed = 0
    
    for file_path, file_detections in files_with_emojis.items():
        if os.path.exists(file_path):
            emoji_count, backup_path = remove_emojis_from_file(file_path)
            if emoji_count > 0:
                print(f"  {file_path}: Removed {emoji_count} emojis (backup: {backup_path})")
                total_removed += emoji_count
                files_processed += 1
        else:
            print(f"  {file_path}: File not found, skipping")
    
    print(f"\nEMOJI REMOVAL COMPLETE!")
    print(f"  Files processed: {files_processed}")
    print(f"  Total emojis removed: {total_removed}")
    print(f"  Backups created with .emoji_backup extension")

def main():
    """Main function"""
    process_emoji_report()

if __name__ == "__main__":
    main()
