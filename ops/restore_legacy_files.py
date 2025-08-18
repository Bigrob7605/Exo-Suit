#!/usr/bin/env python3
"""
LEGACY FILE RESTORE SCRIPT
Restores legacy files from safe location if needed for reference
"""

import shutil
from pathlib import Path

def restore_legacy_files():
    """Restore legacy files from safe location"""
    legacy_dir = Path("legacy")
    ops_dir = Path("ops")
    
    if not legacy_dir.exists():
        print("No legacy directory found")
        return
    
    restored = 0
    for category_dir in legacy_dir.iterdir():
        if category_dir.is_dir():
            for file_path in category_dir.iterdir():
                if file_path.is_file():
                    dest_path = ops_dir / file_path.name
                    if not dest_path.exists():
                        shutil.copy2(str(file_path), str(dest_path))
                        restored += 1
                        print(f"RESTORED: {file_path.name}")
    
    print(f"Restored {restored} legacy files")

if __name__ == "__main__":
    restore_legacy_files()
