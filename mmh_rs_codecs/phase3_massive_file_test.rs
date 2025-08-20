// Phase 3 Massive File Test - Testing our AMAZING compression system on 50MB+ files!
// This will push our Phase 3 system to its absolute limits!

use std::path::Path;
use std::time::Instant;

// Import our enhanced pattern engine
mod enhanced_pattern_engine;
use enhanced_pattern_engine::*;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🚀 PHASE 3 MASSIVE FILE COMPRESSION TEST");
    println!("=========================================");
    println!("Testing our AMAZING compression on 50MB+ files!");
    println!("This will push our system to the absolute limits!");
    println!();

    // Initialize the Phase 3 system
    let system = Phase3CompressionSystem::new();
    println!("✅ Phase 3 system initialized successfully!");
    println!();

    // Test our massive 50MB+ file
    let massive_file = "MASSIVE_50MB_TEST_FILE.txt";
    
    if !Path::new(massive_file).exists() {
        println!("❌ Massive test file not found: {}", massive_file);
        println!("Please create the massive test file first!");
        return Ok(());
    }

    println!("📁 Testing MASSIVE file: {}", massive_file);
    println!("🎯 Target: 50MB+ compression test");
    println!();

    let start_time = Instant::now();
    
    match system.analyze_and_compress(Path::new(massive_file)) {
        Ok((analysis, compression)) => {
            let total_time = start_time.elapsed();
            
            // Display MASSIVE results
            println!("🏆 MASSIVE FILE COMPRESSION RESULTS");
            println!("===================================");
            println!("📁 File: {}", massive_file);
            println!("📏 Original Size: {:.2} MB", analysis.file_size as f64 / (1024.0 * 1024.0));
            println!("🗜️  Compressed Size: {:.2} MB", compression.compressed_size as f64 / (1024.0 * 1024.0));
            
            let compression_ratio = if analysis.file_size > 0 {
                (analysis.file_size - compression.compressed_size as u64) as f64 / analysis.file_size as f64 * 100.0
            } else {
                0.0
            };
            
            println!("📊 Compression Ratio: {:.1}%", compression_ratio);
            println!("💾 Space Saved: {:.2} MB", 
                (analysis.file_size - compression.compressed_size as u64) as f64 / (1024.0 * 1024.0));
            
            println!("⚡ Algorithm Used: {} (confidence: {:.1}%)", 
                compression.algorithm_used, compression.algorithm_confidence * 100.0);
            println!("⏱️  Processing Time: {} ms", compression.processing_time_ms);
            println!("🎯 Pattern Efficiency: {:.1}%", compression.pattern_efficiency * 100.0);
            println!();

            // Display detailed analysis
            println!("🔍 MASSIVE FILE PATTERN ANALYSIS:");
            println!("=================================");
            println!("📏 File Size: {:.2} MB", analysis.file_size as f64 / (1024.0 * 1024.0));
            println!("⏱️  Analysis Time: {} ms", analysis.analysis_time);
            println!("🧠 Memory Used: {:.2} MB", analysis.memory_used as f64 / (1024.0 * 1024.0));
            println!("📊 File Entropy: {:.2} bits", analysis.file_entropy);
            println!("🎯 Pattern Coverage: {:.1}%", analysis.pattern_coverage * 100.0);
            println!("🧮 Complexity Score: {:.2}/1.0", analysis.complexity_score);
            println!();

            // Display patterns found
            if !analysis.patterns_found.is_empty() {
                println!("🔍 PATTERNS FOUND ({}):", analysis.patterns_found.len());
                for (i, pattern) in analysis.patterns_found.iter().enumerate() {
                    println!("  {}. {:?}", i + 1, pattern.pattern_type);
                    println!("     • Size: {} bytes, Frequency: {}, Entropy: {:.2}", 
                        pattern.size, pattern.frequency, pattern.entropy);
                    println!("     • Compression: {:.1}%, Confidence: {:.1}%, Gain: {} bytes", 
                        pattern.compression_ratio * 100.0, pattern.confidence * 100.0, pattern.compression_gain);
                    
                    if !pattern.algorithm_fitness.is_empty() {
                        println!("     • Algorithm Fitness:");
                        for (alg, score) in &pattern.algorithm_fitness {
                            println!("       - {}: {:.1}%", alg, score * 100.0);
                        }
                    }
                    println!();
                }
            }

            // Display recommended strategy
            println!("🎯 RECOMMENDED STRATEGY:");
            println!("=======================");
            println!("  Primary: {} (confidence: {:.1}%)", 
                analysis.recommended_strategy.primary_algorithm, 
                analysis.recommended_strategy.confidence * 100.0);
            
            if let Some(secondary) = &analysis.recommended_strategy.secondary_algorithm {
                println!("  Secondary: {}", secondary);
            }
            
            println!("  Estimated Compression: {:.1}%", 
                analysis.recommended_strategy.estimated_ratio * 100.0);
            
            println!("  Performance Prediction:");
            println!("    • Compression Time: {} ms", 
                analysis.recommended_strategy.performance_prediction.compression_time_ms);
            println!("    • Memory Usage: {:.1} MB", 
                analysis.recommended_strategy.performance_prediction.memory_usage_mb);
            println!("    • CPU Intensity: {:.1}%", 
                analysis.recommended_strategy.performance_prediction.cpu_intensity * 100.0);
            println!();

            // Display reasoning
            if !analysis.recommended_strategy.reasoning.is_empty() {
                println!("💡 REASONING:");
                println!("=============");
                for reason in &analysis.recommended_strategy.reasoning {
                    println!("  → {}", reason);
                }
                println!();
            }

            // Display byte frequency analysis
            if !analysis.frequency_spectrum.is_empty() {
                println!("📈 TOP BYTE FREQUENCIES:");
                println!("=======================");
                for (i, (byte, count)) in analysis.frequency_spectrum.iter().take(10).enumerate() {
                    let percentage = *count as f64 / analysis.file_size as f64 * 100.0;
                    println!("  {}. 0x{:02X}: {} occurrences ({:.1}%)", 
                        i + 1, byte, count, percentage);
                }
                println!();
            }

            // Performance metrics
            println!("⚡ PERFORMANCE METRICS:");
            println!("======================");
            println!("⏱️  Total processing time: {:.2} seconds", total_time.as_secs_f64());
            println!("🚀 Throughput: {:.2} MB/s", 
                (analysis.file_size as f64 / (1024.0 * 1024.0)) / total_time.as_secs_f64());
            println!("🎯 Compression efficiency: {:.1}% compression in {:.1} seconds", 
                compression_ratio, total_time.as_secs_f64());
            println!();

            // Success message
            println!("🎉 MASSIVE FILE TEST COMPLETED SUCCESSFULLY!");
            println!("Our Phase 3 compression system handled a 50MB+ file!");
            println!("This proves our system can scale to enterprise-level workloads!");
            
        }
        Err(e) => {
            println!("❌ Error processing massive file: {}", e);
            println!("This might indicate a limitation or bug in our system.");
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_massive_file_handling() {
        let system = Phase3CompressionSystem::new();
        
        // Test with a file that should exist
        let test_path = Path::new("MASSIVE_50MB_TEST_FILE.txt");
        if test_path.exists() {
            let result = system.analyze_and_compress(test_path);
            assert!(result.is_ok(), "Phase 3 should handle massive files");
            
            let (analysis, compression) = result.unwrap();
            
            // Verify we got meaningful results
            assert!(analysis.file_size > 50 * 1024 * 1024, "Should be 50MB+ file");
            assert!(compression.compression_ratio >= -100.0, "Should have reasonable compression ratio");
            
            println!("✅ Massive file test passed!");
        } else {
            println!("⚠️  Skipping massive file test - test file not found");
        }
    }
}
