# LEGACY FILE ACCESS GUARD
# This file prevents agents from accidentally accessing legacy files
# Legacy files are for reference and scraping only - NOT for production use

import os
import sys
from pathlib import Path

def block_legacy_access():
    """Block access to legacy files"""
    legacy_patterns = ['*V1*', '*V2*', '*V3*', '*V4*', '*legacy*']
    
    for pattern in legacy_patterns:
        for file_path in Path('.').rglob(pattern):
            if file_path.is_file():
                print(f"BLOCKED: Access to legacy file {file_path}")
                print("Legacy files are for reference only - not for production use")
                return False
    
    return True

# Block legacy access on import
if not block_legacy_access():
    sys.exit(1)
