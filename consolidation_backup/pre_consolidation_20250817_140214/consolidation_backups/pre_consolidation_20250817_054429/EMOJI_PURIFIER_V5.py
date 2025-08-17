#!/usr/bin/env python3
"""
Agent Exo-Suit V5.0 - Emoji Purifier
Simple emoji detection and removal from codebase
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import unicodedata

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

def scan_file_for_emojis(file_path: str) -> List[Dict]:
    """Scan a single file for emojis"""
    results = []
    
    try:
        # Skip if file is too large (>10MB)
        if os.path.getsize(file_path) > 10 * 1024 * 1024:
            return results
            
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for col_num, char in enumerate(line):
                if is_emoji(char):
                    # Get context (surrounding text)
                    start = max(0, col_num - 20)
                    end = min(len(line), col_num + 20)
                    context = line[start:end]
                    
                    results.append({
                        'file_path': file_path,
                        'line_number': line_num,
                        'column_number': col_num + 1,
                        'emoji': char,
                        'context': context,
                        'line_content': line
                    })
                    
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
        
    return results

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

def scan_directory(directory: str, extensions: List[str] = None) -> List[Dict]:
    """Scan directory for emojis in files"""
    if extensions is None:
        extensions = ['.py', '.ps1', '.md', '.txt', '.json', '.yml', '.yaml', '.js', '.html', '.css']
    
    all_results = []
    total_files = 0
    scanned_files = 0
    
    # First count total files
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv', 'archive', 'system_backups', 'testing_artifacts']]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                total_files += 1
    
    print(f"Found {total_files} files to scan...")
    
    # Now scan files
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv', 'archive', 'system_backups', 'testing_artifacts']]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                scanned_files += 1
                
                if scanned_files % 100 == 0:
                    print(f"Progress: {scanned_files}/{total_files} files scanned...")
                
                results = scan_file_for_emojis(file_path)
                all_results.extend(results)
                
    return all_results

def main():
    """Main emoji scanning and purifying function"""
    print("AGENT EXO-SUIT V5.0 - EMOJI PURIFIER")
    print("=" * 50)
    
    # Look for the test data directory specifically
    test_data_dir = "Test Data Only (DO NOT PUSH TO REPO - DO NOT USE MD FILES AS EXO-SUIT PROJECT FILES)"
    
    if os.path.exists(test_data_dir):
        print(f"Found test data directory: {test_data_dir}")
        scan_dir = test_data_dir
    else:
        print("Test data directory not found, scanning current directory")
        scan_dir = os.getcwd()
    
    print(f"Scanning directory: {scan_dir}")
    
    # Scan for emojis
    print("\nScanning for emojis...")
    results = scan_directory(scan_dir)
    
    if not results:
        print("No emojis found! Codebase is clean.")
        return
    
    # Display results
    print(f"\nFound {len(results)} emojis in {len(set(r['file_path'] for r in results))} files:")
    print("-" * 50)
    
    files_with_emojis = {}
    for result in results:
        file_path = result['file_path']
        if file_path not in files_with_emojis:
            files_with_emojis[file_path] = []
        files_with_emojis[file_path].append(result)
    
    for file_path, file_results in files_with_emojis.items():
        print(f"\nFile: {file_path} ({len(file_results)} emojis):")
        for result in file_results[:5]:  # Show first 5
            print(f"  Line {result['line_number']}:{result['column_number']} - '{result['emoji']}' - {result['context']}")
        if len(file_results) > 5:
            print(f"  ... and {len(file_results) - 5} more")
    
    # Ask for confirmation to remove
    print(f"\nFound {len(results)} emojis total")
    response = input("Do you want to remove ALL emojis? (yes/no): ").lower().strip()
    
    if response in ['yes', 'y']:
        print("\nRemoving emojis...")
        total_removed = 0
        files_processed = 0
        
        for file_path in files_with_emojis.keys():
            emoji_count, backup_path = remove_emojis_from_file(file_path)
            if emoji_count > 0:
                print(f"  {file_path}: Removed {emoji_count} emojis (backup: {backup_path})")
                total_removed += emoji_count
                files_processed += 1
        
        print(f"\nEMOJI PURIFICATION COMPLETE!")
        print(f"  Files processed: {files_processed}")
        print(f"  Total emojis removed: {total_removed}")
        print(f"  Backups created with .emoji_backup extension")
        
    else:
        print("Emoji removal cancelled.")

if __name__ == "__main__":
    main()
