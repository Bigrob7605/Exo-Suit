use std::path::Path;
use std::fs;

// Include our enhanced pattern recognition engine
mod enhanced_pattern_recognition_engine;
use enhanced_pattern_recognition_engine::*;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Simple Enhanced Pattern Recognition Test");
    println!("======================================");
    
    // Create enhanced pattern recognition engine
    let config = EnhancedPatternRecognitionConfig::default();
    let engine = EnhancedPatternRecognitionEngine::new(config);
    
    println!("Enhanced engine created successfully!");
    println!("Configuration:");
    println!("   Min pattern size: {} bytes", config.min_pattern_size);
    println!("   Max pattern size: {} bytes", config.max_pattern_size);
    println!("   Performance threshold: {:.1}x", config.performance_threshold);
    println!("   Silesia baselines: {}", config.use_silesia_baselines);
    println!();
    
    // Test on a few Silesia files
    let silesia_dir = Path::new("silesia_corpus");
    if !silesia_dir.exists() {
        println!("Silesia Corpus directory not found");
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
    
    println!("Found {} Silesia Corpus files", files.len());
    println!();
    
    // Test on first 3 files to avoid overwhelming output
    let test_files = files.iter().take(3).collect::<Vec<_>>();
    
    for (i, file_path) in test_files.iter().enumerate() {
        println!("Testing file {}/{}: {}", i + 1, test_files.len(), file_path.file_name().unwrap().to_string_lossy());
        
        match engine.analyze_file(file_path) {
            Ok(result) => {
                println!("   File size: {:.2} MB", result.file_size as f64 / (1024.0 * 1024.0));
                println!("   Analysis time: {} ms", result.analysis_time);
                println!("   Memory used: {:.2} MB", result.memory_used as f64 / (1024.0 * 1024.0));
                println!("   Patterns found: {}", result.patterns_found.len());
                
                if let Some(ref benchmark) = result.silesia_benchmark {
                    println!("   Silesia Benchmark: {:.1}x average", benchmark.average_ratio);
                }
                
                println!("   Primary algorithm: {}", result.recommended_strategy.primary_algorithm);
                println!("   Estimated ratio: {:.1}x", result.recommended_strategy.estimated_ratio);
                println!("   Confidence: {:.1}%", result.recommended_strategy.confidence * 100.0);
                println!();
            }
            Err(e) => {
                println!("   Analysis failed: {}", e);
                println!();
            }
        }
    }
    
    println!("Simple test completed successfully!");
    Ok(())
}
