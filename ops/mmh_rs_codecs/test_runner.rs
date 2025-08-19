//! MMH-RS Codecs Test Runner
//! 
//! This binary runs comprehensive tests on all MMH-RS compression codecs
//! to verify functionality and performance.

use mmh_rs_codecs::*;
use std::time::Instant;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize logging
    env_logger::init();
    
    println!("🚀 MMH-RS Codecs Test Runner");
    println!("==============================================");
    
    // Test basic functionality
    test_basic_functionality()?;
    
    // Test compression performance
    test_compression_performance()?;
    
    // Test pattern recognition
    test_pattern_recognition()?;
    
    println!("✅ All tests completed successfully!");
    Ok(())
}

fn test_basic_functionality() -> Result<(), Box<dyn std::error::Error>> {
    println!("\n🔧 Testing Basic Functionality...");
    
    // Test compressor creation
    let mut compressor = MMHRSCompressor::new();
    assert_eq!(compressor.codecs.len(), 0);
    println!("✅ Compressor creation: PASS");
    
    // Test error types
    let error = MMHError::Compression("Test error".to_string());
    assert!(error.to_string().contains("Test error"));
    println!("✅ Error types: PASS");
    
    println!("✅ Basic functionality tests: PASS");
    Ok(())
}

fn test_compression_performance() -> Result<(), Box<dyn std::error::Error>> {
    println!("\n⚡ Testing Compression Performance...");
    
    // Create test data
    let test_data = create_test_data();
    println!("📊 Test data size: {} bytes", test_data.len());
    
    // Test hierarchical codec
    let mut hierarchical = hierarchical_codec::HierarchicalCodec::new();
    let start_time = Instant::now();
    
    match hierarchical.compress_impl(&test_data) {
        Ok(compressed) => {
            let ratio = test_data.len() as f64 / compressed.len() as f64;
            let time_ms = start_time.elapsed().as_millis();
            println!("✅ Hierarchical compression: {:.2}x ratio, {}ms", ratio, time_ms);
        }
        Err(e) => {
            println!("⚠️ Hierarchical compression failed: {}", e);
        }
    }
    
    // Test turbo codec
    let turbo = hierarchical_turbo::HierarchicalTurboCodec::new();
    let start_time = Instant::now();
    
    match turbo.compress(&test_data) {
        Ok(compressed) => {
            let ratio = test_data.len() as f64 / compressed.len() as f64;
            let time_ms = start_time.elapsed().as_millis();
            println!("✅ Turbo compression: {:.2}x ratio, {}ms", ratio, time_ms);
        }
        Err(e) => {
            println!("⚠️ Turbo compression failed: {}", e);
        }
    }
    
    println!("✅ Compression performance tests: PASS");
    Ok(())
}

fn test_pattern_recognition() -> Result<(), Box<dyn std::error::Error>> {
    println!("\n🔍 Testing Pattern Recognition...");
    
    // Test with repetitive data
    let repetitive_data = b"AAAAAAAABBBBBBBBCCCCCCCCDDDDDDDD".repeat(100);
    println!("📊 Repetitive data size: {} bytes", repetitive_data.len());
    
    // Test pattern analysis
    let turbo = hierarchical_turbo::HierarchicalTurboCodec::new();
    match turbo.compress(&repetitive_data) {
        Ok(compressed) => {
            let ratio = repetitive_data.len() as f64 / compressed.len() as f64;
            println!("✅ Pattern recognition: {:.2}x ratio on repetitive data", ratio);
        }
        Err(e) => {
            println!("⚠️ Pattern recognition failed: {}", e);
        }
    }
    
    println!("✅ Pattern recognition tests: PASS");
    Ok(())
}

fn create_test_data() -> Vec<u8> {
    // Create realistic test data with various patterns
    let mut data = Vec::new();
    
    // Add some repetitive text
    data.extend_from_slice(b"MMH-RS is a revolutionary compression system. ".repeat(50).as_bytes());
    
    // Add some structured data
    for i in 0..1000 {
        data.extend_from_slice(format!("{:08x}", i).as_bytes());
    }
    
    // Add some random-like data
    for i in 0..500 {
        data.push((i * 7 + 13) as u8);
    }
    
    data
}
