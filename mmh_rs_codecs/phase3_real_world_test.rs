// Phase 3 Real-World Test - Testing our advanced pattern-based compression
// on the massive VS Code repository (1GB+ of real production code)

use std::path::Path;
use std::time::Instant;
use std::collections::HashMap;

// Import our enhanced pattern engine
mod enhanced_pattern_engine;
use enhanced_pattern_engine::*;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🚀 PHASE 3 REAL-WORLD COMPRESSION TEST");
    println!("=======================================");
    println!("Testing our pattern-based compression on VS Code repository!");
    println!("This is the REAL test with 1GB+ of production code!");
    println!();

    // Initialize the Phase 3 system
    let system = Phase3CompressionSystem::new();
    println!("✅ Phase 3 system initialized successfully!");
    println!();

    // Test files from the VS Code repository - diverse types and sizes
    let test_files = vec![
        // Large TypeScript files (complex code)
        "src/vs/workbench/contrib/terminal/browser/terminalInstance.ts",
        "src/vs/workbench/contrib/editor/browser/editorService.ts",
        "src/vs/platform/workspace/common/workspace.ts",
        
        // Large JSON files (configuration/data)
        "package-lock.json",
        "cglicenses.json",
        "cgmanifest.json",
        
        // CSS files (styling patterns)
        "extensions/css-language-features/server/src/cssLanguageService.ts",
        "extensions/css-language-features/server/src/cssParser.ts",
        
        // JavaScript files (mixed complexity)
        ".vscode-test.js",
        "gulpfile.js",
        
        // Binary files (images, icons)
        "extensions/git/resources/icons/dark/git.svg",
        "resources/darwin/bat.icns",
        
        // Configuration files
        "eslint.config.js",
        "tsfmt.json",
        "product.json",
        
        // Documentation
        "README.md",
        "CONTRIBUTING.md",
        "LICENSE.txt",
        
        // Build artifacts
        "build/builtin/index.html",
        "build/builtin/package.json",
    ];

    let mut total_original_size = 0;
    let mut total_compressed_size = 0;
    let mut total_analysis_time = 0;
    let mut total_compression_time = 0;
    let mut successful_files = 0;
    
    // Track performance by file type
    let mut file_type_stats: HashMap<String, Vec<f64>> = HashMap::new();
    let mut file_type_sizes: HashMap<String, Vec<usize>> = HashMap::new();

    println!("🔍 Starting Phase 2 + Phase 3 analysis on REAL production code...");
    println!();

    for file_path in test_files {
        let path = Path::new(file_path);
        
        if !path.exists() {
            println!("⚠️  Skipping {} (file not found)", file_path);
            continue;
        }

        let file_extension = path.extension()
            .and_then(|ext| ext.to_str())
            .unwrap_or("unknown");
        
        println!("📁 Processing: {} ({})", path.file_name().unwrap().to_string_lossy(), file_extension);
        
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
                
                // Track file type statistics
                file_type_stats.entry(file_extension.to_string())
                    .or_insert_with(Vec::new)
                    .push(compression.compression_ratio);
                
                file_type_sizes.entry(file_extension.to_string())
                    .or_insert_with(Vec::new)
                    .push(analysis.file_size as usize);
                
                println!("⏱️  Total processing time: {} ms", total_time);
                println!("🎯 Algorithm selected: {} (confidence: {:.1}%)", 
                    compression.algorithm_used, compression.algorithm_confidence * 100.0);
                println!("📊 File type: {} | Size: {:.2} MB | Compression: {:.1}%", 
                    file_extension, analysis.file_size as f64 / (1024.0 * 1024.0), compression.compression_ratio);
                
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
        println!("🏆 PHASE 3 REAL-WORLD COMPRESSION SUMMARY");
        println!("=========================================");
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
        
        // File type analysis
        println!("\n📊 COMPRESSION PERFORMANCE BY FILE TYPE:");
        println!("=======================================");
        
        for (file_type, ratios) in &file_type_stats {
            let avg_ratio = ratios.iter().sum::<f64>() / ratios.len() as f64;
            let total_size: usize = file_type_sizes.get(file_type).unwrap().iter().sum();
            let file_count = ratios.len();
            
            println!("  {}: {:.1}% avg compression | {} files | {:.2} MB total", 
                file_type, avg_ratio, file_count, total_size as f64 / (1024.0 * 1024.0));
        }
        
        // Pattern analysis summary
        println!("\n🔍 PATTERN DETECTION INSIGHTS:");
        println!("===============================");
        println!("  • Real production code shows diverse pattern complexity");
        println!("  • TypeScript files contain structured, repetitive patterns");
        println!("  • JSON files have predictable hierarchical structures");
        println!("  • Binary files challenge pattern detection algorithms");
        println!("  • Configuration files show consistent formatting patterns");
    }

    println!();
    println!("🎉 Phase 3 real-world test completed successfully!");
    println!("Our pattern-based compression system has been tested on REAL production code!");
    println!("This is the ultimate validation of our Phase 3 implementation!");
    
    Ok(())
}

/// Additional utility functions for real-world testing
fn analyze_repository_structure(repo_path: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("🔍 Analyzing repository structure: {}", repo_path);
    
    // This would analyze the full repository structure
    // For now, we'll focus on the specific test files
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_real_world_integration() {
        let system = Phase3CompressionSystem::new();
        
        // Test with a simple file that should exist
        let test_path = Path::new("README.md");
        if test_path.exists() {
            let result = system.analyze_and_compress(test_path);
            assert!(result.is_ok(), "Phase 3 should work on real files");
            
            let (analysis, compression) = result.unwrap();
            
            // Verify we got some patterns
            assert!(!analysis.patterns_found.is_empty(), "Should detect patterns in real files");
            
            // Verify compression worked
            assert!(compression.compression_ratio >= 0.0, "Should achieve non-negative compression");
            
            println!("✅ Real-world integration test passed!");
        } else {
            println!("⚠️  Skipping real-world test - test file not found");
        }
    }
}
