#!/usr/bin/env python3
"""
Debug Repair Process - Test V5's repair capabilities step by step
"""

import sys
import os
from pathlib import Path

# Add ops directory to path
sys.path.append('ops')

def debug_repair():
    """Debug the repair process step by step"""
    print("🔍 DEBUGGING V5 REPAIR PROCESS")
    print("=" * 50)
    
    try:
        # Step 1: Import Phoenix system
        print("Step 1: Importing Phoenix system...")
        from PHOENIX_RECOVERY_SYSTEM_V5 import PhoenixRecoverySystem
        print("✓ Phoenix system imported successfully")
        
        # Step 2: Initialize Phoenix system
        print("\nStep 2: Initializing Phoenix system...")
        phoenix = PhoenixRecoverySystem()
        print("✓ Phoenix system initialized successfully")
        
        # Step 3: Create repair strategy
        print("\nStep 3: Creating repair strategy...")
        strategy = phoenix.create_intelligent_repair_strategy('test_corruption_scenario')
        print(f"✓ Strategy created: {strategy}")
        
        # Step 4: Execute repairs
        print("\nStep 4: Executing repairs...")
        result = phoenix.execute_intelligent_repairs('test_corruption_scenario', strategy)
        print(f"✓ Repair result: {result}")
        
        # Step 5: Check if files were actually modified
        print("\nStep 5: Checking file modifications...")
        test_dir = Path('test_corruption_scenario')
        for py_file in test_dir.rglob("*.py"):
            print(f"  • {py_file.name}: {py_file.stat().st_size} bytes")
            # Check for backup files
            backup_file = py_file.with_suffix('.py.backup')
            if backup_file.exists():
                print(f"    ✓ Backup created: {backup_file.name}")
            else:
                print(f"    ✗ No backup created")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_repair()
