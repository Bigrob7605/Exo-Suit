#!/usr/bin/env python3
"""
Test if required packages are installed for Agent Exo-Suit
"""

import importlib
import sys

def test_package(package_name):
    """Test if a package can be imported"""
    try:
        importlib.import_module(package_name)
        print(f"Installed: {package_name}")
        return True
    except ImportError:
        print(f"Missing: {package_name}")
        return False

def main():
    """Test all required packages"""
    required_packages = [
        'sentence_transformers',
        'faiss',
        'numpy',
        'torch',
        'transformers',
        'scikit-learn'
    ]
    
    print("Testing required packages for Agent Exo-Suit...")
    print("=" * 50)
    
    installed_count = 0
    for package in required_packages:
        if test_package(package):
            installed_count += 1
    
    print("=" * 50)
    if installed_count == len(required_packages):
        print("All required packages are installed!")
        return 0
    else:
        print("Some packages are missing. Install them with:")
        print("pip install sentence-transformers faiss-cpu numpy torch transformers scikit-learn")
        return 1

if __name__ == "__main__":
    sys.exit(main())
