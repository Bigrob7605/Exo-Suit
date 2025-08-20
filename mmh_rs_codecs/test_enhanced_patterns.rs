use std::path::Path;
use enhanced_pattern_recognition_engine::*;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Enhanced Pattern Recognition Engine Test");
    println!("======================================");
    
    // Create enhanced pattern recognition engine
    let config = EnhancedPatternRecognitionConfig::default();
    let engine = EnhancedPatternRecognitionEngine::new(config);
    
    println!("Enhanced engine created with configuration:");
    println!("   Min pattern size: {} bytes", config.min_pattern_size);
    println!("   Max pattern size: {} bytes", config.max_pattern_size);
    println!("   Performance threshold: {:.1}x", config.performance_threshold);
    println!("   Silesia baselines: {}", config.use_silesia_baselines);
    println!();
    
    // Test on Silesia Corpus files
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
    
    println!("Testing on {} Silesia Corpus files", files.len());
    println!();
    
    let mut total_analysis_time = 0;
    let mut total_memory_used = 0;
    let mut successful_analyses = 0;
    
    for (i, file_path) in files.iter().enumerate() {
        println!("Testing {}/{}: {}", i + 1, files.len(), file_path.file_name().unwrap().to_string_lossy());
        
        match engine.analyze_file(file_path) {
            Ok(result) => {
                successful_analyses += 1;
                total_analysis_time += result.analysis_time;
                total_memory_used += result.memory_used;
                
                // Display results
                display_enhanced_pattern_analysis(&result);
                
                // Performance summary
                println!("   Performance: {}ms, {:.2}MB memory", 
                    result.analysis_time, 
                    result.memory_used as f64 / (1024.0 * 1024.0));
                
                if let Some(ref benchmark) = result.silesia_benchmark {
                    println!("   Silesia Benchmark: {:.1}x average", benchmark.average_ratio);
                }
                
                println!();
            }
            Err(e) => {
                println!("   Analysis failed: {}", e);
                println!();
            }
        }
    }
    
    // Summary
    println!("ENHANCED PATTERN RECOGNITION TEST SUMMARY");
    println!("=========================================");
    println!("Successful analyses: {}/{}", successful_analyses, files.len());
    println!("Total analysis time: {} ms", total_analysis_time);
    println!("Total memory used: {:.2} MB", total_memory_used as f64 / (1024.0 * 1024.0));
    
    if successful_analyses > 0 {
        println!("Average analysis time: {:.1} ms per file", 
            total_analysis_time as f64 / successful_analyses as f64);
        println!("Average memory usage: {:.2} MB per file", 
            (total_memory_used as f64 / successful_analyses as f64) / (1024.0 * 1024.0));
    }
    
    println!();
    println!("Enhanced Pattern Recognition Engine Test Complete!");
    
    Ok(())
}
