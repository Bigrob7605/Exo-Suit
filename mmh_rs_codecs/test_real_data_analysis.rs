// Real Data Analysis Test for Enhanced Pattern Analyzer
// This tests our enhanced system on actual files to demonstrate real-world performance

use std::collections::{HashMap, HashSet};
use std::time::{Instant, Duration};
use std::fs;
use std::path::Path;

/// Real-world test data structure
#[derive(Debug, Clone)]
pub struct RealDataAnalysis {
    pub filename: String,
    pub file_size: usize,
    pub patterns_found: usize,
    pub compression_potential: f64,
    pub pattern_complexity: f64,
    pub compression_ratio_estimate: f64,
    pub processing_time: Duration,
    pub recommended_strategy: String,
    pub entropy_analysis: f64,
    pub pattern_distribution: Vec<(usize, usize)>, // (length, count)
}

/// Enhanced pattern analyzer for real data testing
pub struct RealDataPatternAnalyzer {
    min_pattern_length: usize,
    max_pattern_length: usize,
    threshold: f64,
    adaptive_threshold: bool,
}

impl RealDataPatternAnalyzer {
    pub fn new() -> Self {
        Self {
            min_pattern_length: 4,
            max_pattern_length: 251,
            threshold: 0.1,
            adaptive_threshold: false,
        }
    }
    
    pub fn with_adaptive_threshold(mut self) -> Self {
        self.adaptive_threshold = true;
        self
    }
    
    /// Analyze real file data with comprehensive metrics
    pub fn analyze_real_file(&self, filepath: &str) -> Result<RealDataAnalysis, String> {
        let start = Instant::now();
        
        // Read file data
        let data = fs::read(filepath)
            .map_err(|e| format!("Failed to read file: {}", e))?;
        
        let file_size = data.len();
        let filename = Path::new(filepath)
            .file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .to_string();
        
        // Calculate adaptive threshold if enabled
        let effective_threshold = if self.adaptive_threshold {
            self.calculate_adaptive_threshold(&data)
        } else {
            self.threshold
        };
        
        // Analyze patterns with detailed tracking
        let mut pattern_lengths = Vec::new();
        let mut pattern_frequencies = Vec::new();
        let mut total_bytes_covered = 0;
        let mut pattern_distribution = HashMap::new();
        
        // Analyze patterns of different lengths
        for length in self.min_pattern_length..=self.max_pattern_length.min(data.len() / 2) {
            let (patterns, bytes_covered) = self.find_patterns_with_coverage(&data, length);
            
            if !patterns.is_empty() {
                let frequency = bytes_covered as f64 / data.len() as f64;
                
                // Only include patterns that meet the threshold
                if frequency >= effective_threshold {
                    pattern_lengths.push(length);
                    pattern_frequencies.push(frequency);
                    total_bytes_covered += bytes_covered;
                    
                    // Track pattern distribution
                    pattern_distribution.insert(length, patterns.len());
                }
            }
        }
        
        // Calculate comprehensive metrics
        let entropy_analysis = self.calculate_data_entropy(&data);
        let compression_potential = total_bytes_covered as f64 / data.len() as f64;
        let pattern_complexity = self.calculate_pattern_complexity(&data);
        let compression_ratio_estimate = self.estimate_compression_ratio(&pattern_frequencies, pattern_complexity);
        
        // Determine recommended strategy
        let recommended_strategy = self.determine_strategy_description(
            pattern_lengths.len(),
            compression_potential,
            pattern_complexity,
            entropy_analysis
        );
        
        // Convert pattern distribution to sorted vector
        let mut pattern_distribution_vec: Vec<(usize, usize)> = pattern_distribution.into_iter().collect();
        pattern_distribution_vec.sort_by_key(|&(length, _)| length);
        
        Ok(RealDataAnalysis {
            filename,
            file_size,
            patterns_found: pattern_lengths.len(),
            compression_potential,
            pattern_complexity,
            compression_ratio_estimate,
            processing_time: start.elapsed(),
            recommended_strategy,
            entropy_analysis,
            pattern_distribution: pattern_distribution_vec,
        })
    }
    
    /// Analyze multiple files for comparison
    pub fn analyze_multiple_files(&self, filepaths: &[&str]) -> Result<Vec<RealDataAnalysis>, String> {
        let mut results = Vec::new();
        
        for filepath in filepaths {
            match self.analyze_real_file(filepath) {
                Ok(analysis) => results.push(analysis),
                Err(e) => eprintln!("Warning: Failed to analyze {}: {}", filepath, e),
            }
        }
        
        Ok(results)
    }
    
    /// Generate comprehensive analysis report
    pub fn generate_analysis_report(&self, analyses: &[RealDataAnalysis]) -> String {
        let mut report = String::new();
        
        report.push_str("🔍 ENHANCED PATTERN ANALYZER - REAL DATA ANALYSIS REPORT\n");
        report.push_str(&"=".repeat(70));
        report.push_str("\n\n");
        
        // Summary statistics
        let total_files = analyses.len();
        let total_size: usize = analyses.iter().map(|a| a.file_size).sum();
        let avg_compression_potential: f64 = analyses.iter().map(|a| a.compression_potential).sum::<f64>() / total_files as f64;
        let avg_complexity: f64 = analyses.iter().map(|a| a.pattern_complexity).sum::<f64>() / total_files as f64;
        let total_processing_time: Duration = analyses.iter().map(|a| a.processing_time).sum();
        
        report.push_str(&format!("📊 SUMMARY STATISTICS:\n"));
        report.push_str(&format!("   Files analyzed: {}\n", total_files));
        report.push_str(&format!("   Total data size: {:.2} MB\n", total_size as f64 / 1_048_576.0));
        report.push_str(&format!("   Average compression potential: {:.3}\n", avg_compression_potential));
        report.push_str(&format!("   Average pattern complexity: {:.3}\n", avg_complexity));
        report.push_str(&format!("   Total processing time: {:?}\n", total_processing_time));
        report.push_str(&format!("   Average processing time: {:?}\n", total_processing_time / total_files as u32));
        report.push_str("\n");
        
        // Individual file analysis
        report.push_str("📁 INDIVIDUAL FILE ANALYSIS:\n");
        report.push_str(&"-".repeat(70));
        report.push_str("\n");
        
        for (i, analysis) in analyses.iter().enumerate() {
            report.push_str(&format!("{}. {}\n", i + 1, analysis.filename));
            report.push_str(&format!("   Size: {:.2} MB\n", analysis.file_size as f64 / 1_048_576.0));
            report.push_str(&format!("   Patterns found: {}\n", analysis.patterns_found));
            report.push_str(&format!("   Compression potential: {:.3}\n", analysis.compression_potential));
            report.push_str(&format!("   Pattern complexity: {:.3}\n", analysis.pattern_complexity));
            report.push_str(&format!("   Compression ratio estimate: {:.3}\n", analysis.compression_ratio_estimate));
            report.push_str(&format!("   Entropy: {:.3}\n", analysis.entropy_analysis));
            report.push_str(&format!("   Processing time: {:?}\n", analysis.processing_time));
            report.push_str(&format!("   Recommended strategy: {}\n", analysis.recommended_strategy));
            
            // Pattern distribution (top 5)
            if !analysis.pattern_distribution.is_empty() {
                report.push_str("   Top pattern lengths: ");
                let top_patterns: Vec<String> = analysis.pattern_distribution
                    .iter()
                    .take(5)
                    .map(|(length, count)| format!("{}b({})", length, count))
                    .collect();
                report.push_str(&top_patterns.join(", "));
                report.push_str("\n");
            }
            report.push_str("\n");
        }
        
        // Performance insights
        report.push_str("🚀 PERFORMANCE INSIGHTS:\n");
        report.push_str(&"-".repeat(70));
        report.push_str("\n");
        
        let best_compression = analyses.iter()
            .max_by(|a, b| a.compression_potential.partial_cmp(&b.compression_potential).unwrap())
            .unwrap();
        
        let worst_compression = analyses.iter()
            .min_by(|a, b| a.compression_potential.partial_cmp(&b.compression_potential).unwrap())
            .unwrap();
        
        let fastest_processing = analyses.iter()
            .min_by(|a, b| a.processing_time.cmp(&b.processing_time))
            .unwrap();
        
        report.push_str(&format!("🏆 Best compression candidate: {} ({:.3})\n", 
            best_compression.filename, best_compression.compression_potential));
        report.push_str(&format!("📉 Worst compression candidate: {} ({:.3})\n", 
            worst_compression.filename, worst_compression.compression_potential));
        report.push_str(&format!("⚡ Fastest processing: {} ({:?})\n", 
            fastest_processing.filename, fastest_processing.processing_time));
        
        // Strategy recommendations
        report.push_str("\n🎯 STRATEGY RECOMMENDATIONS:\n");
        report.push_str(&"-".repeat(70));
        report.push_str("\n");
        
        let mut strategy_counts = HashMap::new();
        for analysis in analyses {
            *strategy_counts.entry(analysis.recommended_strategy.clone()).or_insert(0) += 1;
        }
        
        for (strategy, count) in strategy_counts {
            report.push_str(&format!("   {}: {} files\n", strategy, count));
        }
        
        report
    }
    
    // Helper methods (same as before)
    fn find_patterns_with_coverage(&self, data: &[u8], length: usize) -> (HashMap<Vec<u8>, usize>, usize) {
        let mut patterns = HashMap::new();
        let mut bytes_covered = 0;
        
        for i in 0..=(data.len().saturating_sub(length)) {
            let pattern = data[i..i + length].to_vec();
            *patterns.entry(pattern).or_insert(0) += 1;
        }
        
        patterns.retain(|pattern, count| {
            if *count > 1 {
                bytes_covered += pattern.len() * (*count);
                true
            } else {
                false
            }
        });
        
        (patterns, bytes_covered)
    }
    
    fn calculate_data_entropy(&self, data: &[u8]) -> f64 {
        let mut byte_counts = [0u32; 256];
        for &byte in data {
            byte_counts[byte as usize] += 1;
        }
        
        let data_len = data.len() as f64;
        byte_counts
            .iter()
            .filter(|&&count| count > 0)
            .map(|&count| {
                let prob = count as f64 / data_len;
                -prob * prob.log2()
            })
            .sum()
    }
    
    fn calculate_pattern_complexity(&self, data: &[u8]) -> f64 {
        let mut unique_patterns = HashSet::new();
        let mut total_patterns = 0;
        
        let sample_size = data.len().min(4096);
        let step = if data.len() > sample_size { data.len() / sample_size } else { 1 };
        
        for length in self.min_pattern_length..=self.max_pattern_length.min(sample_size / 2) {
            for i in (0..=(data.len() - length)).step_by(step) {
                let pattern = &data[i..i + length];
                unique_patterns.insert(pattern);
                total_patterns += 1;
            }
        }
        
        if total_patterns == 0 {
            return 1.0;
        }
        
        unique_patterns.len() as f64 / total_patterns as f64
    }
    
    fn estimate_compression_ratio(&self, frequencies: &[f64], complexity: f64) -> f64 {
        if frequencies.is_empty() {
            return 1.0;
        }
        
        let max_frequency = frequencies.iter().cloned().fold(0.0f64, f64::max);
        let avg_frequency = frequencies.iter().sum::<f64>() / frequencies.len() as f64;
        
        let base_ratio = 1.0 - (avg_frequency * 0.7 + max_frequency * 0.3);
        let complexity_factor = 0.5 + complexity * 0.5;
        
        (base_ratio * complexity_factor).max(0.1).min(1.0)
    }
    
    fn calculate_adaptive_threshold(&self, data: &[u8]) -> f64 {
        let entropy = self.calculate_data_entropy(data);
        let size_factor = (data.len() as f64).log2() / 20.0;
        let entropy_factor = entropy / 8.0;
        
        let adaptive = self.threshold * (1.0 + size_factor * 0.5 - entropy_factor * 0.3);
        adaptive.max(0.01).min(0.5)
    }
    
    fn determine_strategy_description(&self, pattern_count: usize, compression_potential: f64, 
                                   complexity: f64, entropy: f64) -> String {
        if compression_potential > 0.7 && complexity < 0.3 {
            "Dictionary-Based (High Repetition)".to_string()
        } else if compression_potential > 0.5 || pattern_count > 20 {
            "Hybrid (Balanced)".to_string()
        } else if compression_potential > 0.3 && entropy < 6.0 {
            "LZ77 Variant (Moderate Patterns)".to_string()
        } else if entropy > 7.5 {
            "Standard (High Entropy)".to_string()
        } else {
            "Standard (Low Patterns)".to_string()
        }
    }
}

fn main() {
    println!("🚀 ENHANCED PATTERN ANALYZER - REAL DATA TESTING");
    println!("{}", "=".repeat(60));
    
    // Create analyzer with adaptive threshold
    let analyzer = RealDataPatternAnalyzer::new().with_adaptive_threshold();
    
    // Test files to analyze (common file types)
    let test_files = [
        "Cargo.toml",                    // Configuration file (text)
        "lib.rs",                        // Rust source code
        "pattern_analyzer.rs",           // Our enhanced analyzer
        "hierarchical_codec.rs",         // Another Rust module
    ];
    
    println!("\n📁 Analyzing {} files with enhanced pattern analyzer...", test_files.len());
    println!("   Using adaptive threshold for optimal performance\n");
    
    // Analyze all files
    match analyzer.analyze_multiple_files(&test_files) {
        Ok(analyses) => {
            // Generate comprehensive report
            let report = analyzer.generate_analysis_report(&analyses);
            println!("{}", report);
            
            // Save report to file
            if let Err(e) = fs::write("real_data_analysis_report.txt", &report) {
                eprintln!("Warning: Could not save report: {}", e);
            } else {
                println!("📄 Detailed report saved to: real_data_analysis_report.txt");
            }
            
            // Performance summary
            println!("\n🎯 KEY INSIGHTS:");
            let total_size: usize = analyses.iter().map(|a| a.file_size).sum();
            let total_time: Duration = analyses.iter().map(|a| a.processing_time).sum();
            let avg_compression = analyses.iter().map(|a| a.compression_potential).sum::<f64>() / analyses.len() as f64;
            
            println!("   📊 Total data processed: {:.2} MB", total_size as f64 / 1_048_576.0);
            println!("   ⚡ Total processing time: {:?}", total_time);
            println!("   🎯 Average compression potential: {:.3}", avg_compression);
            println!("   🚀 Processing speed: {:.2} MB/s", 
                (total_size as f64 / 1_048_576.0) / total_time.as_secs_f64());
            
        }
        Err(e) => {
            eprintln!("❌ Analysis failed: {}", e);
        }
    }
    
    println!("\n🎉 Real data analysis complete! Check the report for detailed insights.");
}
