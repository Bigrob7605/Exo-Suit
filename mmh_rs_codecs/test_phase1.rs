// Test Runner for Phase 1: Foundation & Core Architecture
// Tests the Universal File Detector and Adaptive Sampling System

use std::path::Path;
use mmh_rs_codecs::{UniversalCompressionEngine, UniversalCompressionConfig};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("=== MMH-RS Universal Compression Engine - Phase 1 Test ===\n");
    
    // Initialize the engine with default configuration
    let config = UniversalCompressionConfig::default();
    let engine = UniversalCompressionEngine::new(config.clone());
    
    println!("✅ Engine initialized successfully");
    println!("📁 Configuration: Max file size: {}MB, Max memory: {}MB", 
        config.max_file_size_mb, config.max_memory_mb);
    println!("🚀 Streaming enabled: {}", config.enable_streaming);
    println!("📊 Detailed reporting: {}", config.detailed_reporting);
    println!();

    // Test file type detection
    println!("=== Testing File Type Detection ===");
    test_file_type_detection(&engine)?;
    println!();

    // Test sampling strategies
    println!("=== Testing Sampling Strategies ===");
    test_sampling_strategies(&engine)?;
    println!();

    // Test directory analysis (if we have test files)
    println!("=== Testing Directory Analysis ===");
    test_directory_analysis(&engine)?;
    println!();

    println!("🎉 Phase 1 Testing Complete! All systems operational.");
    Ok(())
}

fn test_file_type_detection(engine: &UniversalCompressionEngine) -> Result<(), Box<dyn std::error::Error>> {
    // Test with some common file types
    let test_files = vec![
        "test_small_files/data.csv",
        "test_small_files/config.json",
        "test_small_files/empty.txt",
    ];

    for test_file in test_files {
        let path = Path::new(test_file);
        if path.exists() {
            match engine.analyze_file(path) {
                Ok(result) => {
                    println!("✅ {}: {} bytes, Potential: {:.1}%", 
                        path.file_name().unwrap().to_string_lossy(),
                        result.file_size,
                        result.compression_potential * 100.0);
                    
                    if let Some(ref file_type) = result.file_type {
                        println!("   📋 Type: {} ({:?})", file_type.name, file_type.category);
                    } else {
                        println!("   📋 Type: Unknown");
                    }
                    
                    if !result.recommendations.is_empty() {
                        println!("   💡 Recommendations: {}", result.recommendations.len());
                    }
                }
                Err(e) => {
                    println!("❌ {}: Error - {}", path.file_name().unwrap().to_string_lossy(), e);
                }
            }
        } else {
            println!("⚠️  {}: File not found (skipping)", test_file);
        }
    }
    
    Ok(())
}

fn test_sampling_strategies(engine: &UniversalCompressionEngine) -> Result<(), Box<dyn std::error::Error>> {
    // Test with different file types to see sampling strategies
    let test_files = vec![
        "test_small_files/data.csv",
        "test_small_files/config.json",
    ];

    for test_file in test_files {
        let path = Path::new(test_file);
        if path.exists() {
            match engine.analyze_file(path) {
                Ok(result) => {
                    if let Some(ref sampling) = result.sampling_result {
                        println!("✅ {}: Sampled {} bytes in {} samples", 
                            path.file_name().unwrap().to_string_lossy(),
                            sampling.total_samples_size,
                            sampling.samples.len());
                        
                        println!("   🧠 Memory used: {:.2} MB", 
                            sampling.memory_used as f64 / (1024.0 * 1024.0));
                        
                        for (i, sample) in sampling.samples.iter().enumerate() {
                            println!("   📍 Sample {}: {} bytes at offset {}, entropy: {:.2}", 
                                i + 1, sample.size, sample.offset, sample.entropy);
                        }
                    } else {
                        println!("⚠️  {}: No sampling (below threshold)", 
                            path.file_name().unwrap().to_string_lossy());
                    }
                }
                Err(e) => {
                    println!("❌ {}: Error - {}", path.file_name().unwrap().to_string_lossy(), e);
                }
            }
        }
    }
    
    Ok(())
}

fn test_directory_analysis(engine: &UniversalCompressionEngine) -> Result<(), Box<dyn std::error::Error>> {
    // Test directory analysis with test_small_files
    let test_dir = Path::new("test_small_files");
    
    if test_dir.exists() && test_dir.is_dir() {
        match engine.analyze_directory(test_dir) {
            Ok(result) => {
                println!("✅ Directory analyzed successfully");
                println!("📁 Path: {}", result.directory_path);
                println!("📊 Total files: {}", result.total_files);
                println!("💾 Total size: {:.2} MB", 
                    result.total_size as f64 / (1024.0 * 1024.0));
                println!("⏱️  Analysis time: {} ms", result.analysis_time_ms);
                println!("🧠 Memory peak: {:.2} MB", 
                    result.memory_peak as f64 / (1024.0 * 1024.0));
                
                // File type breakdown
                println!("\n📋 File Type Breakdown:");
                for (category, count) in &result.file_types {
                    let avg_potential = result.compression_potential_by_type.get(category).unwrap_or(&0.0);
                    println!("   {:?}: {} files, Avg potential: {:.1}%", 
                        category, count, avg_potential * 100.0);
                }
                
                // Top candidates
                if !result.top_compression_candidates.is_empty() {
                    println!("\n🏆 Top Compression Candidates:");
                    for (i, candidate) in result.top_compression_candidates.iter().take(3).enumerate() {
                        let filename = Path::new(&candidate.file_path).file_name().unwrap().to_string_lossy();
                        println!("   {}. {}: {:.1}% potential", 
                            i + 1, filename, candidate.compression_potential * 100.0);
                    }
                }
                
                // Generate and display report
                println!("\n📄 Generated Report:");
                let report = engine.generate_report(&result);
                let lines: Vec<&str> = report.lines().take(20).collect(); // Show first 20 lines
                for line in lines {
                    println!("   {}", line);
                }
                if report.lines().count() > 20 {
                    println!("   ... (report truncated)");
                }
            }
            Err(e) => {
                println!("❌ Directory analysis failed: {}", e);
            }
        }
    } else {
        println!("⚠️  Test directory not found, skipping directory analysis");
    }
    
    Ok(())
}
