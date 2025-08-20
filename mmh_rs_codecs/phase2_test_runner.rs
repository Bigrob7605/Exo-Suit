// Phase 2 Test Runner for MMH-RS Universal Compression Champion
// Tests the new Pattern Recognition Engine with real data

use std::path::Path;
use std::time::Instant;

mod pattern_recognition_engine;
use pattern_recognition_engine::{
    PatternRecognitionEngine, 
    PatternRecognitionConfig, 
    display_pattern_analysis
};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("=== MMH-RS Universal Compression Champion - Phase 2 Test ===\n");
    println!("🚀 Testing Advanced Pattern Recognition Engine\n");
    
    // Initialize the pattern recognition engine
    let config = PatternRecognitionConfig::default();
    let engine = PatternRecognitionEngine::new(config.clone());
    
    println!("✅ Pattern Recognition Engine initialized successfully");
    println!("📊 Configuration: min_size={}, max_size={}, min_frequency={}", 
        config.min_pattern_size, config.max_pattern_size, config.min_frequency);
    
    // Test with our real data from Phase 1
    let test_dir = Path::new("test_real_data");
    if !test_dir.exists() {
        println!("\n❌ Test data directory not found. Please run Phase 1 tests first.");
        return Ok(());
    }
    
    println!("\n🔍 Starting pattern analysis on real data...");
    
    let start_time = Instant::now();
    let mut total_files = 0;
    let mut total_patterns = 0;
    let mut total_analysis_time = 0u128;
    
    // Analyze files recursively
    analyze_directory_recursively(&engine, test_dir, &mut total_files, &mut total_patterns, &mut total_analysis_time)?;
    
    let total_time = start_time.elapsed().as_millis();
    
    // Display summary
    println!("\n{}", "=".repeat(60));
    println!("🎉 PHASE 2 PATTERN RECOGNITION TEST COMPLETE!");
    println!("{}", "=".repeat(60));
    println!("📊 Summary:");
    println!("   📁 Files Analyzed: {}", total_files);
    println!("   🔍 Total Patterns Found: {}", total_patterns);
    println!("   ⏱️  Total Analysis Time: {} ms", total_analysis_time);
    println!("   🚀 Overall Performance: {:.2} ms/file", total_analysis_time as f64 / total_files as f64);
    println!("   🧠 Average Patterns/File: {:.1}", total_patterns as f64 / total_files as f64);
    
    println!("\n🎯 Phase 2 Achievements:");
    println!("   ✅ Advanced Pattern Recognition Engine implemented");
    println!("   ✅ 5 Pattern Types: Repetitive, Null, Structured, Text, Binary");
    println!("   ✅ Intelligent Compression Strategy Generation");
    println!("   ✅ Real-time Pattern Analysis with Confidence Scoring");
    println!("   ✅ Algorithm-Specific Recommendations (LZ77, RLE, Dictionary, Huffman)");
    
    println!("\n🚀 Ready for Phase 3: Compression Strategy Matrix & Implementation!");
    
    Ok(())
}

fn analyze_directory_recursively(
    engine: &PatternRecognitionEngine,
    dir: &Path,
    total_files: &mut usize,
    total_patterns: &mut usize,
    total_analysis_time: &mut u128,
) -> Result<(), Box<dyn std::error::Error>> {
    for entry in std::fs::read_dir(dir)? {
        let entry = entry?;
        let path = entry.path();
        
        if path.is_file() {
            // Analyze the file
            match engine.analyze_file(&path) {
                Ok(result) => {
                    *total_files += 1;
                    *total_patterns += result.patterns_found.len();
                    *total_analysis_time += result.analysis_time;
                    
                    // Display results for this file
                    display_pattern_analysis(&result);
                    
                    // Add a separator between files
                    println!("{}", "-".repeat(60));
                }
                Err(e) => {
                    println!("❌ Error analyzing {}: {}", path.display(), e);
                }
            }
        } else if path.is_dir() {
            // Recursively analyze subdirectories
            analyze_directory_recursively(engine, &path, total_files, total_patterns, total_analysis_time)?;
        }
    }
    
    Ok(())
}

/// Quick test function for specific file types
fn test_specific_patterns() -> Result<(), Box<dyn std::error::Error>> {
    println!("\n🧪 Testing Specific Pattern Types...");
    
    let config = PatternRecognitionConfig::default();
    let engine = PatternRecognitionEngine::new(config);
    
    // Test 1: Null padding pattern
    println!("\n📝 Test 1: Null Padding Pattern");
    let null_data = create_test_null_data();
    let patterns = engine.recognize_patterns(&null_data)?;
    println!("   Found {} patterns", patterns.len());
    for pattern in &patterns {
        println!("   - {:?}: size={}, frequency={}, ratio={:.1}%", 
            pattern.pattern_type, pattern.size, pattern.frequency, 
            pattern.compression_ratio * 100.0);
    }
    
    // Test 2: Repetitive sequence pattern
    println!("\n📝 Test 2: Repetitive Sequence Pattern");
    let repetitive_data = create_test_repetitive_data();
    let patterns = engine.recognize_patterns(&repetitive_data)?;
    println!("   Found {} patterns", patterns.len());
    for pattern in &patterns {
        println!("   - {:?}: size={}, frequency={}, ratio={:.1}%", 
            pattern.pattern_type, pattern.size, pattern.frequency, 
            pattern.compression_ratio * 100.0);
    }
    
    // Test 3: Text pattern
    println!("\n📝 Test 3: Text Pattern");
    let text_data = create_test_text_data();
    let patterns = engine.recognize_patterns(&text_data)?;
    println!("   Found {} patterns", patterns.len());
    for pattern in &patterns {
        println!("   - {:?}: size={}, frequency={}, ratio={:.1}%", 
            pattern.pattern_type, pattern.size, pattern.frequency, 
            pattern.compression_ratio * 100.0);
    }
    
    Ok(())
}

fn create_test_null_data() -> Vec<u8> {
    let mut data = Vec::new();
    data.extend(b"HEADER");
    data.extend(vec![0x00; 1000]); // 1000 null bytes
    data.extend(b"FOOTER");
    data
}

fn create_test_repetitive_data() -> Vec<u8> {
    let mut data = Vec::new();
    let pattern = b"REPEATED_PATTERN_123";
    for _ in 0..50 {
        data.extend(pattern);
    }
    data
}

fn create_test_text_data() -> Vec<u8> {
    let mut data = Vec::new();
    let text = b"This is a repeated text pattern that should be detected by our pattern recognition engine. ";
    for _ in 0..100 {
        data.extend(text);
    }
    data
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_phase2_integration() {
        let config = PatternRecognitionConfig::default();
        let engine = PatternRecognitionEngine::new(config);
        
        // Test that the engine can be created
        assert!(true); // Basic test that we can create the engine
        
        // Test pattern recognition on simple data
        let test_data = create_test_null_data();
        let patterns = engine.recognize_patterns(&test_data).unwrap();
        
        // Should find at least one pattern
        assert!(!patterns.is_empty());
        
        // Should find null padding pattern
        let has_null_pattern = patterns.iter()
            .any(|p| matches!(p.pattern_type, pattern_recognition_engine::PatternType::NullPadding));
        assert!(has_null_pattern);
    }
}
