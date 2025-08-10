#!/usr/bin/env python3
"""
Test if required packages are installed.
"""
import importlib


def test_package(package_name):
    """Test if a package can be imported."""
    try:
        importlib.import_module(package_name)
        print(f"✅ {package_name} installed")
        return True
    except ImportError:
        print(f"❌ {package_name} not installed")
        return False


def main():
    """Test all required packages."""
    packages = [
        'sentence_transformers',
        'faiss',
        'numpy'
    ]
    
    print("🔍 Testing required packages...")
    print()
    
    all_installed = True
    for package in packages:
        if not test_package(package):
            all_installed = False
    
    print()
    if all_installed:
        print("🎉 All required packages are installed!")
        return 0
    else:
        print("⚠️  Some packages are missing. Install them with:")
        print("   pip install sentence-transformers faiss-cpu numpy")
        return 1


if __name__ == '__main__':
    exit(main())
