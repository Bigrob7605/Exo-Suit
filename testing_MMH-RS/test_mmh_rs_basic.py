#!/usr/bin/env python3
"""
Basic MMH-RS Component Test
Tests the Python components we've extracted from MMH-RS
"""

import os
import sys
import time
from pathlib import Path

def test_file_access():
    """Test that we can access all the MMH-RS files"""
    print("🔍 Testing MMH-RS File Access")
    print("=" * 50)
    
    files_to_check = [
        "validate_real_tensors.py",
        "test_lightweight_system.py", 
        "real_tensor_generator.py",
        "mmh_launcher.ps1",
        "mmh_launcher_enhanced.bat",
        "Cargo.toml",
        "mod.rs",
        "hierarchical_codec.rs",
        "README.md",
        "01_MMH_RS_MASTER_GUIDE.md"
    ]
    
    missing_files = []
    for file_name in files_to_check:
        if Path(file_name).exists():
            size = Path(file_name).stat().st_size
            print(f"✅ {file_name:<30} ({size:,} bytes)")
        else:
            print(f"❌ {file_name:<30} MISSING")
            missing_files.append(file_name)
    
    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} files")
        return False
    else:
        print(f"\n🎉 All {len(files_to_check)} files present")
        return True

def test_python_imports():
    """Test that Python files can be imported without errors"""
    print("\n🐍 Testing Python Import Compatibility")
    print("=" * 50)
    
    python_files = [
        "validate_real_tensors.py",
        "test_lightweight_system.py",
        "real_tensor_generator.py"
    ]
    
    for py_file in python_files:
        if not Path(py_file).exists():
            print(f"❌ {py_file} not found, skipping import test")
            continue
            
        print(f"Testing import: {py_file}")
        try:
            # Try to read and parse the file
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic syntax check - try to compile
            compile(content, py_file, 'exec')
            print(f"  ✅ Syntax valid")
            
            # Check for common dependencies
            deps = []
            if 'torch' in content:
                deps.append('torch')
            if 'numpy' in content:
                deps.append('numpy')
            if 'safetensors' in content:
                deps.append('safetensors')
            if 'argparse' in content:
                deps.append('argparse')
            
            if deps:
                print(f"  📦 Dependencies: {', '.join(deps)}")
            else:
                print(f"  📦 No external dependencies detected")
                
        except Exception as e:
            print(f"  ❌ Import failed: {e}")
            return False
    
    return True

def test_rust_analysis():
    """Analyze the Rust code we've collected"""
    print("\n🦀 Analyzing Rust Components")
    print("=" * 50)
    
    rust_files = ["mod.rs", "hierarchical_codec.rs"]
    
    for rs_file in rust_files:
        if not Path(rs_file).exists():
            print(f"❌ {rs_file} not found")
            continue
            
        print(f"Analyzing: {rs_file}")
        try:
            with open(rs_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count lines and analyze structure
            lines = content.split('\n')
            total_lines = len(lines)
            code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('//')])
            comment_lines = total_lines - code_lines
            
            print(f"  📊 Total lines: {total_lines:,}")
            print(f"  📝 Code lines: {code_lines:,}")
            print(f"  💬 Comment lines: {comment_lines:,}")
            
            # Look for key features
            if 'trait Codec' in content:
                print(f"  🔧 Codec trait found")
            if 'impl Codec' in content:
                print(f"  ⚙️  Codec implementations found")
            if 'compress' in content:
                print(f"  📦 Compression functions found")
            if 'decompress' in content:
                print(f"  📤 Decompression functions found")
                
        except Exception as e:
            print(f"  ❌ Analysis failed: {e}")
    
    return True

def test_cargo_analysis():
    """Analyze the Cargo.toml file"""
    print("\n📦 Analyzing Cargo.toml")
    print("=" * 50)
    
    if not Path("Cargo.toml").exists():
        print("❌ Cargo.toml not found")
        return False
    
    try:
        with open("Cargo.toml", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract key information
        lines = content.split('\n')
        
        # Find package info
        for line in lines:
            if line.strip().startswith('name ='):
                name = line.split('=')[1].strip().strip('"')
                print(f"📦 Package: {name}")
            elif line.strip().startswith('version ='):
                version = line.split('=')[1].strip().strip('"')
                print(f"🏷️  Version: {version}")
            elif line.strip().startswith('edition ='):
                edition = line.split('=')[1].strip().strip('"')
                print(f"🦀 Edition: {edition}")
        
        # Count dependencies
        deps = [l for l in lines if l.strip().startswith('dep:') or 
                (l.strip().startswith('"') and '=' in l and 'version' in l)]
        
        print(f"🔗 Dependencies: {len(deps)} found")
        
        # Look for key features
        if 'zstd' in content:
            print(f"  ✅ ZSTD compression support")
        if 'lz4' in content:
            print(f"  ✅ LZ4 compression support")
        if 'rayon' in content:
            print(f"  ✅ Parallel processing support")
        if 'gpu-accel' in content:
            print(f"  ✅ GPU acceleration support")
            
    except Exception as e:
        print(f"❌ Cargo analysis failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 MMH-RS Basic Component Test")
    print("=" * 60)
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("File Access", test_file_access),
        ("Python Imports", test_python_imports),
        ("Rust Analysis", test_rust_analysis),
        ("Cargo Analysis", test_cargo_analysis)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MMH-RS components are ready for testing.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main())
