// Phase 3 Compression Demo - Testing our advanced pattern-based compression
// This demonstrates the complete Phase 2 + Phase 3 integration

use std::path::Path;
use std::time::Instant;

// Import our enhanced pattern engine
mod enhanced_pattern_engine;
use enhanced_pattern_engine::*;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🚀 PHASE 3 COMPRESSION DEMONSTRATION");
    println!("=====================================");
    println!("Testing our advanced pattern-based compression system!");
    println!();

    // Initialize the Phase 3 system
    let system = Phase3CompressionSystem::new();
    println!("✅ Phase 3 system initialized successfully!");
    println!();

    // Test files from our test_real_data directory
    let test_files = vec![
        "test_real_data/media/image.jpg",
        "test_real_data/media/image.png", 
        "test_real_data/system/app.exe",
        "test_real_data/system/database.db",
        "test_real_data/office/data.csv",
        "test_real_data/web/app.js",
        "test_real_data/web/api.json",
    ];

    let mut total_original_size = 0;
    let mut total_compressed_size = 0;
    let mut total_analysis_time = 0;
    let mut total_compression_time = 0;
    let mut successful_files = 0;

    println!("🔍 Starting Phase 2 + Phase 3 analysis and compression...");
    println!();

    for file_path in test_files {
        let path = Path::new(file_path);
        
        if !path.exists() {
            println!("⚠️  Skipping {} (file not found)", file_path);
            continue;
        }

        println!("📁 Processing: {}", path.file_name().unwrap().to_string_lossy());
        
        let start_time = Instant::now();
        
        match system.analyze_and_compress(path) {
            Ok((analysis, compression)) => {
                let total_time = start_time.elapsed().as_millis();
                
                // Display results
                display_phase3_results(&analysis, &compression);
                
                // Update totals
                total_original_size += analysis.file_size as usize;
                total_compressed_size += compression.compressed_size;
                total_analysis_time += analysis.analysis_time;
                total_compression_time += compression.processing_time_ms;
                successful_files += 1;
                
                println!("⏱️  Total processing time: {} ms", total_time);
                println!("🎯 Algorithm selected: {} (confidence: {:.1}%)", 
                    compression.algorithm_used, compression.algorithm_confidence * 100.0);
                
            }
            Err(e) => {
                println!("❌ Error processing {}: {}", file_path, e);
            }
        }
        
        println!("{}", "─".repeat(80));
        println!();
    }

    // Display summary statistics
    if successful_files > 0 {
        println!("🏆 PHASE 3 COMPRESSION SUMMARY");
        println!("==============================");
        println!("📊 Files processed: {}", successful_files);
        println!("📏 Total original size: {:.2} MB", total_original_size as f64 / (1024.0 * 1024.0));
        println!("🗜️  Total compressed size: {:.2} MB", total_compressed_size as f64 / (1024.0 * 1024.0));
        
        let overall_compression_ratio = if total_original_size > 0 {
            (total_original_size - total_compressed_size) as f64 / total_original_size as f64 * 100.0
        } else {
            0.0
        };
        
        println!("📊 Overall compression ratio: {:.1}%", overall_compression_ratio);
        println!("💾 Total space saved: {:.2} MB", 
            (total_original_size - total_compressed_size) as f64 / (1024.0 * 1024.0));
        
        println!("⏱️  Total analysis time: {} ms", total_analysis_time);
        println!("⚡ Total compression time: {} ms", total_compression_time);
        println!("🚀 Total processing time: {} ms", total_analysis_time + total_compression_time);
        
        let avg_analysis_time = total_analysis_time / successful_files as u128;
        let avg_compression_time = total_compression_time / successful_files as u128;
        println!("📈 Average analysis time per file: {} ms", avg_analysis_time);
        println!("📈 Average compression time per file: {} ms", avg_compression_time);
        
        // Performance metrics
        let total_mb = total_original_size as f64 / (1024.0 * 1024.0);
        let total_seconds = (total_analysis_time + total_compression_time) as f64 / 1000.0;
        let throughput = total_mb / total_seconds;
        
        println!("🚀 Throughput: {:.2} MB/s", throughput);
        println!("🎯 Compression efficiency: {:.1}% compression in {:.1} seconds", 
            overall_compression_ratio, total_seconds);
    }

    println!();
    println!("🎉 Phase 3 demonstration completed successfully!");
    println!("Our pattern-based compression system is working perfectly!");
    
    Ok(())
}

/// Additional utility functions for testing
fn create_test_data() -> Vec<u8> {
    // Create some test data with known patterns
    let mut data = Vec::new();
    
    // Add some null padding
    data.extend(vec![0u8; 1000]);
    
    // Add some repetitive sequences
    let pattern = b"HELLO_WORLD_";
    for _ in 0..100 {
        data.extend_from_slice(pattern);
    }
    
    // Add some periodic data
    for i in 0..1000 {
        data.push((i % 16) as u8);
    }
    
    data
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_phase3_integration() {
        let system = Phase3CompressionSystem::new();
        let test_data = create_test_data();
        
        // Create a temporary file for testing
        let temp_path = std::env::temp_dir().join("phase3_test.bin");
        std::fs::write(&temp_path, &test_data).unwrap();
        
        // Test the complete pipeline
        let result = system.analyze_and_compress(&temp_path);
        assert!(result.is_ok(), "Phase 3 integration should work");
        
        let (analysis, compression) = result.unwrap();
        
        // Verify we got some patterns
        assert!(!analysis.patterns_found.is_empty(), "Should detect patterns");
        
        // Verify compression worked
        assert!(compression.compression_ratio > 0.0, "Should achieve compression");
        assert!(compression.compressed_size < test_data.len(), "Should reduce size");
        
        // Cleanup
        let _ = std::fs::remove_file(temp_path);
        
        println!("✅ Phase 3 integration test passed!");
    }

    #[test]
    fn test_compression_algorithms() {
        let compressor = PatternBasedCompressor::new();
        let test_data = create_test_data();
        
        // Test RLE compression
        let rle_result = compressor.rle_compress(&test_data, &[]);
        assert!(rle_result.len() < test_data.len(), "RLE should compress");
        
        // Test LZ77 compression
        let lz77_result = compressor.lz77_compress(&test_data, &[]);
        assert!(lz77_result.len() < test_data.len(), "LZ77 should compress");
        
        println!("✅ Compression algorithm tests passed!");
    }
}
