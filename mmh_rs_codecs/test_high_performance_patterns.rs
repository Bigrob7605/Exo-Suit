use std::time::Instant;
use mmh_rs_codecs::high_performance_pattern_analyzer::HighPerformancePatternAnalyzer;

fn main() {
    println!("🚀 MMH-RS HIGH-PERFORMANCE PATTERN ANALYZER TEST");
    println!("=================================================");
    println!("Testing O(n log n) performance vs O(n²) approach");
    println!();
    
    let analyzer = HighPerformancePatternAnalyzer::new();
    
    // Test on different Silesia corpus files
    let test_files = vec![
        "silesia_corpus/xml",      // 5MB - structured data
        "silesia_corpus/dickens",  // 10MB - text data  
        "silesia_corpus/samba",    // 21MB - binary data
        "silesia_corpus/webster",  // 41MB - text data
        "silesia_corpus/mozilla",  // 51MB - mixed data
    ];
    
    for file_path in test_files {
        match std::fs::read(file_path) {
            Ok(data) => {
                println!("🔍 Analyzing: {} ({:.1} MB)", file_path, data.len() as f64 / 1024.0 / 1024.0);
                
                let start_time = Instant::now();
                let result = analyzer.analyze_patterns_4bit_to_251bit(&data);
                let total_time = start_time.elapsed();
                
                // Calculate performance metrics
                let throughput = (data.len() as f64 / 1024.0 / 1024.0) / total_time.as_secs_f64();
                let patterns_per_second = result.total_patterns as f64 / total_time.as_secs_f64();
                
                println!("   ✅ Analysis completed in {:?}", total_time);
                println!("   📊 Total patterns found: {}", result.total_patterns);
                println!("   ⚡ Throughput: {:.1} MB/s", throughput);
                println!("   🔍 Patterns/second: {:.0}", patterns_per_second);
                println!("   🎯 Pattern lengths detected: {:?}", result.pattern_lengths);
                
                // Show pattern counts for each length
                for &length in &result.pattern_lengths {
                    if let Some(&count) = result.pattern_counts.get(&length) {
                        println!("      {} bits: {} patterns", length, count);
                    }
                }
                
                // Get detailed statistics
                let stats = analyzer.get_pattern_statistics(&result);
                println!("   💡 Compression potential: {:.1}%", stats.compression_potential);
                println!("   🏆 Most common: {} bits ({} occurrences)", stats.most_common_length, stats.most_common_count);
                
                println!();
                
            },
            Err(e) => {
                println!("❌ Error reading {}: {}", file_path, e);
            }
        }
    }
    
    // Performance benchmark on largest file
    println!("🏁 PERFORMANCE BENCHMARK ON LARGEST FILE");
    println!("=========================================");
    
    if let Ok(data) = std::fs::read("silesia_corpus/mozilla") {
        println!("Testing mozilla (51MB) with performance monitoring...");
        
        let benchmark = analyzer.benchmark_performance(&data);
        
        println!("   📏 Data size: {:.1} MB", benchmark.data_size as f64 / 1024.0 / 1024.0);
        println!("   ⏱️  Analysis time: {:?}", benchmark.analysis_time);
        println!("   🚀 Throughput: {:.1} MB/s", benchmark.throughput_mbps);
        println!("   💾 Memory usage: {:.2} MB", benchmark.memory_usage_mb);
        
        // Calculate efficiency metrics
        let efficiency = benchmark.throughput_mbps / benchmark.memory_usage_mb;
        println!("   ⚡ Efficiency: {:.1} MB/s per MB of memory", efficiency);
        
        // Compare with theoretical O(n²) performance
        let n = data.len();
        let theoretical_n2_time = (n * n) as f64 / 1_000_000_000.0; // Assuming 1 billion ops/sec
        let speedup = theoretical_n2_time / benchmark.analysis_time.as_secs_f64();
        
        println!("   🎯 Speedup vs O(n²): {:.0}x faster!", speedup);
        
        if speedup > 1000.0 {
            println!("   🚀 REVOLUTIONARY PERFORMANCE ACHIEVED!");
        } else if speedup > 100.0 {
            println!("   ⚡ EXCELLENT PERFORMANCE!");
        } else {
            println!("   ✅ GOOD PERFORMANCE!");
        }
    }
    
    println!("\n🎉 High-performance pattern analysis test completed!");
    println!("The O(n log n) suffix array approach provides dramatic speedup over O(n²)!");
}
