#!/usr/bin/env python3
"""
Enhanced Pattern Recognition Engine Test Script
Tests the new Rust-based pattern recognition engine on Silesia Corpus files
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

def run_rust_test():
    """Run the enhanced pattern recognition engine test"""
    print("🚀 ENHANCED PATTERN RECOGNITION ENGINE TEST")
    print("=" * 80)
    print("Testing intelligent pattern recognition on Silesia Corpus files")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists("mmh_rs_codecs"):
        print("❌ Error: mmh_rs_codecs directory not found")
        print("Please run this script from the project root directory")
        return False
    
    # Check if Silesia Corpus exists
    silesia_dir = Path("silesia_corpus")
    if not silesia_dir.exists():
        print("❌ Error: silesia_corpus directory not found")
        print("Please download and extract the Silesia Corpus first")
        return False
    
    # Get Silesia files
    silesia_files = list(silesia_dir.glob("*"))
    silesia_files = [f for f in silesia_files if f.is_file() and f.stat().st_size > 0]
    
    if not silesia_files:
        print("❌ Error: No files found in silesia_corpus directory")
        return False
    
    print(f"📁 Found {len(silesia_files)} files in Silesia Corpus")
    print(f"📊 Total dataset size: {sum(f.stat().st_size for f in silesia_files) / (1024*1024):.2f} MB")
    print()
    
    # Create a simple Rust test program
    test_program = create_test_program()
    
    # Write test program to file
    test_file = Path("mmh_rs_codecs/test_enhanced_patterns.rs")
    with open(test_file, 'w') as f:
        f.write(test_program)
    
    print("🔧 Created enhanced pattern recognition test program")
    
    # Try to compile and run
    try:
        print("🔨 Compiling enhanced pattern recognition test...")
        result = subprocess.run(
            ["cargo", "run", "--bin", "test_enhanced_patterns"],
            cwd="mmh_rs_codecs",
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Enhanced pattern recognition test completed successfully!")
            print("\n📊 Test Results:")
            print(result.stdout)
            
            # Save results
            save_test_results(result.stdout, silesia_files)
            return True
        else:
            print("❌ Enhanced pattern recognition test failed!")
            print("\n🔍 Compilation Errors:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out after 60 seconds")
        return False
    except FileNotFoundError:
        print("❌ Cargo not found. Please install Rust and Cargo")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_test_program():
    """Create a Rust test program for enhanced pattern recognition"""
    return '''
use std::path::Path;
use enhanced_pattern_recognition_engine::*;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🔍 Enhanced Pattern Recognition Engine Test");
    println!("=" * 60);
    
    // Create enhanced pattern recognition engine
    let config = EnhancedPatternRecognitionConfig::default();
    let engine = EnhancedPatternRecognitionEngine::new(config);
    
    println!("✅ Enhanced engine created with configuration:");
    println!("   Min pattern size: {} bytes", config.min_pattern_size);
    println!("   Max pattern size: {} bytes", config.max_pattern_size);
    println!("   Performance threshold: {:.1}x", config.performance_threshold);
    println!("   Silesia baselines: {}", config.use_silesia_baselines);
    println!();
    
    // Test on Silesia Corpus files
    let silesia_dir = Path::new("silesia_corpus");
    if !silesia_dir.exists() {
        println!("❌ Silesia Corpus directory not found");
        return Ok(());
    }
    
    let mut files = Vec::new();
    for entry in std::fs::read_dir(silesia_dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.is_file() {
            files.push(path);
        }
    }
    
    println!("📁 Testing on {} Silesia Corpus files", files.len());
    println!();
    
    let mut total_analysis_time = 0;
    let mut total_memory_used = 0;
    let mut successful_analyses = 0;
    
    for (i, file_path) in files.iter().enumerate() {
        println!("🔧 Testing {}/{}: {}", i + 1, files.len(), file_path.file_name().unwrap().to_string_lossy());
        
        match engine.analyze_file(file_path) {
            Ok(result) => {
                successful_analyses += 1;
                total_analysis_time += result.analysis_time;
                total_memory_used += result.memory_used;
                
                // Display results
                display_enhanced_pattern_analysis(&result);
                
                // Performance summary
                println!("   ⚡ Performance: {}ms, {:.2}MB memory", 
                    result.analysis_time, 
                    result.memory_used as f64 / (1024.0 * 1024.0));
                
                if let Some(ref benchmark) = result.silesia_benchmark {
                    println!("   📊 Silesia Benchmark: {:.1}x average", benchmark.average_ratio);
                }
                
                println!();
            }
            Err(e) => {
                println!("   ❌ Analysis failed: {}", e);
                println!();
            }
        }
    }
    
    // Summary
    println!("📊 ENHANCED PATTERN RECOGNITION TEST SUMMARY");
    println!("=" * 60);
    println!("✅ Successful analyses: {}/{}", successful_analyses, files.len());
    println!("⏱️  Total analysis time: {} ms", total_analysis_time);
    println!("🧠 Total memory used: {:.2} MB", total_memory_used as f64 / (1024.0 * 1024.0));
    
    if successful_analyses > 0 {
        println!("📈 Average analysis time: {:.1} ms per file", 
            total_analysis_time as f64 / successful_analyses as f64);
        println!("💾 Average memory usage: {:.2} MB per file", 
            (total_memory_used as f64 / successful_analyses as f64) / (1024.0 * 1024.0));
    }
    
    println!();
    println!("🎯 Enhanced Pattern Recognition Engine Test Complete!");
    
    Ok(())
}
'''

def save_test_results(output, silesia_files):
    """Save test results to a JSON file"""
    results = {
        "test_type": "Enhanced Pattern Recognition Engine",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "silesia_files": [f.name for f in silesia_files],
        "total_files": len(silesia_files),
        "output": output
    }
    
    output_file = "enhanced_pattern_recognition_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Test results saved to: {output_file}")

def main():
    """Main function"""
    print("🎯 MMH-RS Enhanced Pattern Recognition Engine Test")
    print("Testing intelligent pattern recognition with Silesia Corpus validation")
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        return False
    
    # Run the enhanced pattern recognition test
    success = run_rust_test()
    
    if success:
        print("🎉 Enhanced Pattern Recognition Engine test completed successfully!")
        print("🚀 Ready for Phase 2 implementation!")
    else:
        print("❌ Enhanced Pattern Recognition Engine test failed")
        print("🔧 Please check the errors and try again")
    
    return success

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if Rust is installed
    try:
        result = subprocess.run(["rustc", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Rust: {result.stdout.strip()}")
        else:
            print("❌ Rust not found or not working")
            return False
    except FileNotFoundError:
        print("❌ Rust not found. Please install Rust from https://rustup.rs/")
        return False
    
    # Check if Cargo is installed
    try:
        result = subprocess.run(["cargo", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Cargo: {result.stdout.strip()}")
        else:
            print("❌ Cargo not found or not working")
            return False
    except FileNotFoundError:
        print("❌ Cargo not found. Please install Rust and Cargo")
        return False
    
    # Check if mmh_rs_codecs directory exists
    if not os.path.exists("mmh_rs_codecs"):
        print("❌ mmh_rs_codecs directory not found")
        return False
    else:
        print("✅ mmh_rs_codecs directory found")
    
    # Check if Cargo.toml exists
    if not os.path.exists("mmh_rs_codecs/Cargo.toml"):
        print("❌ Cargo.toml not found in mmh_rs_codecs")
        return False
    else:
        print("✅ Cargo.toml found")
    
    # Check if Silesia Corpus exists
    if not os.path.exists("silesia_corpus"):
        print("❌ silesia_corpus directory not found")
        print("Please download and extract the Silesia Corpus first")
        return False
    else:
        print("✅ silesia_corpus directory found")
    
    print("✅ All prerequisites met!")
    print()
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
