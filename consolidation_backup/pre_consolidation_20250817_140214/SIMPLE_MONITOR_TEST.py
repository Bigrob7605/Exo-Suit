#!/usr/bin/env python3
"""
Simple Monitor Test - Debug version
"""
import os, time, json
from datetime import datetime

def now():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def main():
    print("Simple Monitor Test")
    print(f"Time: {now()}")
    
    try:
        import psutil
        print("psutil OK")
        
        # Test basic system info
        cpu = psutil.cpu_percent(interval=None)
        vm = psutil.virtual_memory()
        print(f"CPU: {cpu}%")
        print(f"Memory: {vm.percent}%")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("Test complete")

if __name__ == "__main__":
    main()
