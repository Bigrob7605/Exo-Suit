#!/usr/bin/env python3
"""
LEGACY FILE PROTECTION SYSTEM
Prevents agents from accidentally using or deleting legacy V1/V2/V3/V4 files
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Set

class LegacyFileProtection:
    """Protects legacy files from accidental deletion or misuse"""
    
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.legacy_dir = self.workspace_root / "legacy"
        self.ops_dir = self.workspace_root / "ops"
        
        # Core V5 files that must never be deleted
        self.critical_v5_files = {
            'PHOENIX_RECOVERY_SYSTEM_V5.py',
            'ADVANCED_INTEGRATION_LAYER_V5.py',
            'VISIONGAP_ENGINE.py',
            'SYSTEM_HEALTH_VALIDATOR.py',
            'REAL_EMOJI_CLEANUP.py',
            'V5_CONSOLIDATION_MASTER.py',
            'V5_CONSOLIDATION_ENGINE.py'
        }
        
        # Legacy file patterns that should be protected
        self.legacy_patterns = [
            '*V1*', '*V2*', '*V3*', '*V4*',
            '*legacy*', '*old*', '*backup*',
            '*test*', '*demo*', '*example*'
        ]
        
        # Create legacy directory if it doesn't exist
        self.legacy_dir.mkdir(exist_ok=True)
        
        print("Legacy File Protection System initialized")
        print(f"  Workspace: {self.workspace_root}")
        print(f"  Legacy Directory: {self.legacy_dir}")
        print(f"  Critical V5 Files: {len(self.critical_v5_files)}")
    
    def scan_for_legacy_files(self) -> Dict[str, List[Path]]:
        """Scan for legacy files that should be protected"""
        legacy_files = {
            'v1_files': [],
            'v2_files': [],
            'v3_files': [],
            'v4_files': [],
            'other_legacy': []
        }
        
        # Scan ops directory for legacy files
        for file_path in self.ops_dir.rglob("*"):
            if file_path.is_file():
                filename = file_path.name.lower()
                
                if 'v1' in filename:
                    legacy_files['v1_files'].append(file_path)
                elif 'v2' in filename:
                    legacy_files['v2_files'].append(file_path)
                elif 'v3' in filename:
                    legacy_files['v3_files'].append(file_path)
                elif 'v4' in filename:
                    legacy_files['v4_files'].append(file_path)
                elif any(pattern in filename for pattern in ['legacy', 'old', 'backup', 'test', 'demo']):
                    legacy_files['other_legacy'].append(file_path)
        
        return legacy_files
    
    def move_legacy_to_safe_location(self) -> Dict[str, int]:
        """Move legacy files to safe location without deleting them"""
        results = {
            'moved': 0,
            'skipped': 0,
            'errors': 0
        }
        
        legacy_files = self.scan_for_legacy_files()
        
        for category, files in legacy_files.items():
            for file_path in files:
                try:
                    # Skip if it's a critical V5 file
                    if file_path.name in self.critical_v5_files:
                        results['skipped'] += 1
                        continue
                    
                    # Create category subdirectory
                    category_dir = self.legacy_dir / category
                    category_dir.mkdir(exist_ok=True)
                    
                    # Move file to legacy directory
                    dest_path = category_dir / file_path.name
                    if not dest_path.exists():
                        shutil.move(str(file_path), str(dest_path))
                        results['moved'] += 1
                        print(f"MOVED: {file_path.name} -> {dest_path}")
                    else:
                        results['skipped'] += 1
                        
                except Exception as e:
                    print(f"ERROR moving {file_path.name}: {e}")
                    results['errors'] += 1
        
        return results
    
    def create_legacy_access_guard(self) -> str:
        """Create a guard file that prevents legacy file access"""
        guard_content = '''# LEGACY FILE ACCESS GUARD
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
'''
        
        guard_file = self.workspace_root / "legacy_access_guard.py"
        with open(guard_file, 'w') as f:
            f.write(guard_content)
        
        return str(guard_file)
    
    def create_restore_script(self) -> str:
        """Create a script to restore files from legacy directory"""
        restore_content = '''#!/usr/bin/env python3
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
'''
        
        restore_file = self.workspace_root / "restore_legacy_files.py"
        with open(restore_file, 'w') as f:
            f.write(restore_content)
        
        return str(restore_file)
    
    def run_protection(self) -> Dict[str, any]:
        """Run the complete legacy file protection system"""
        print("Running Legacy File Protection System...")
        
        # 1. Scan for legacy files
        print("\n1. Scanning for legacy files...")
        legacy_files = self.scan_for_legacy_files()
        
        total_legacy = sum(len(files) for files in legacy_files.values())
        print(f"Found {total_legacy} legacy files")
        
        # 2. Move legacy files to safe location
        print("\n2. Moving legacy files to safe location...")
        move_results = self.move_legacy_to_safe_location()
        
        # 3. Create access guard
        print("\n3. Creating legacy access guard...")
        guard_file = self.create_legacy_access_guard()
        
        # 4. Create restore script
        print("\n4. Creating restore script...")
        restore_file = self.create_restore_script()
        
        # 5. Summary
        print("\n" + "="*50)
        print("LEGACY FILE PROTECTION COMPLETE")
        print("="*50)
        print(f"Legacy files found: {total_legacy}")
        print(f"Files moved: {move_results['moved']}")
        print(f"Files skipped: {move_results['skipped']}")
        print(f"Errors: {move_results['errors']}")
        print(f"Access guard: {guard_file}")
        print(f"Restore script: {restore_file}")
        print("\nLegacy files are now protected and cannot be accidentally used")
        print("Use restore_legacy_files.py if you need to reference them")
        
        return {
            'legacy_files_found': total_legacy,
            'files_moved': move_results['moved'],
            'files_skipped': move_results['skipped'],
            'errors': move_results['errors'],
            'guard_file': guard_file,
            'restore_file': restore_file
        }

def main():
    """Main entry point"""
    protection = LegacyFileProtection()
    results = protection.run_protection()
    return results

if __name__ == "__main__":
    main()
