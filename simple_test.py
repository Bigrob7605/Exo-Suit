#!/usr/bin/env python3
print("Testing CHAOSE_ENGINE...")

try:
    import sys
    sys.path.append('ops')
    
    from CHAOSE_ENGINE import ChaosEngine
    print("SUCCESS: ChaosEngine imported!")
    
    # Create instance
    chaos = ChaosEngine()
    print("SUCCESS: ChaosEngine instance created!")
    
    print("Chaos engine test completed successfully!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
