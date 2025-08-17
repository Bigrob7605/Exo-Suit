#!/usr/bin/env python3
"""
Simple test script for CHAOSE_ENGINE
"""

import sys
import os

# Add ops directory to path
sys.path.append('ops')

try:
    from CHAOSE_ENGINE import ChaosEngine
    print("CHAOSE_ENGINE imported successfully!")
    
    # Initialize chaos engine
    chaos = ChaosEngine()
    print("Chaos engine initialized!")
    
    # Start chaos at low level for testing
    print("Starting chaos engineering at LOW level...")
    chaos.start_chaos('low')
    
    # Run for a few cycles
    import time
    for i in range(5):
        time.sleep(2)
        print(f"Cycle {i+1}: {chaos.failure_count} failures, {chaos.recovery_count} recoveries")
    
    # Stop chaos
    print("Stopping chaos engine...")
    chaos.stop_chaos()
    
    print("Test complete!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
