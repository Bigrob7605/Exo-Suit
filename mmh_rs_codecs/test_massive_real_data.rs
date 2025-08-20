// Massive Real Data Analysis Test for Enhanced Pattern Analyzer
// This tests our enhanced system on 500MB+ of actual files to demonstrate real-world performance

use std::collections::{HashMap, HashSet};
use std::time::{Instant, Duration};
use std::fs;
use std::path::{Path, PathBuf};
use std::env;

/// Real-world massive data analysis structure
#[derive(Debug, Clone)]
pub struct MassiveDataAnalysis {
    pub filename: String,
    pub file_path: String,
    pub file_size: usize,
    pub file_type: String,
    pub patterns_found: usize,
    pub compression_potential: f64,
    pub pattern_complexity: f64,
    pub compression_ratio_estimate: f64,
    pub processing_time: Duration,
    pub recommended_strategy: String,
    pub entropy_analysis: f64,
    pub pattern_distribution: Vec<(usize, usize)>, // (length, count)
    pub memory_usage_mb: f64,
}

/// Enhanced pattern analyzer for massive real data testing
pub struct MassiveDataPatternAnalyzer {
    min_pattern_length: usize,
    max_pattern_length: usize,
    threshold: f64,
    adaptive_threshold: bool,
    max_file_size_mb: usize,
    sample_large_files: bool,
}

impl MassiveDataPatternAnalyzer {
    pub fn new() -> Self {
        Self {
            min_pattern_length: 4,
            max_pattern_length: 251,
            threshold: 0.1,
            adaptive_threshold: false,
            max_file_size_mb: 100, // Skip files larger than 100MB
            sample_large_files: true, // Sample large files instead of full analysis
        }
    }
    
    pub fn with_adaptive_threshold(mut self) -> Self {
        self.adaptive_threshold = true;
        self
    }
    
    pub fn with_max_file_size(mut self, max_mb: usize) -> Self {
        self.max_file_size_mb = max_mb;
        self
    }
    
    /// Analyze massive real file data with comprehensive metrics
    pub fn analyze_massive_file(&self, filepath: &str) -> Result<MassiveDataAnalysis, String> {
        let start = Instant::now();
        
        // Get file metadata
        let metadata = fs::metadata(filepath)
            .map_err(|e| format!("Failed to get metadata: {}", e))?;
        
        let file_size = metadata.len() as usize;
        let file_size_mb = file_size as f64 / 1_048_576.0;
        
        // Skip extremely large files
        if file_size_mb > self.max_file_size_mb as f64 {
            return Err(format!("File too large: {:.2} MB (max: {} MB)", file_size_mb, self.max_file_size_mb));
        }
        
        let filename = Path::new(filepath)
            .file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .to_string();
        
        let file_type = self.determine_file_type(&filename, file_size);
        
        // Read file data (with sampling for large files)
        let data = if self.sample_large_files && file_size_mb > 10.0 {
            self.sample_large_file(filepath, file_size)?
        } else {
            fs::read(filepath)
                .map_err(|e| format!("Failed to read file: {}", e))?
        };
        
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
        
        // Estimate memory usage
        let memory_usage_mb = (data.len() + pattern_distribution_vec.len() * 16) as f64 / 1_048_576.0;
        
        Ok(MassiveDataAnalysis {
            filename,
            file_path: filepath.to_string(),
            file_size,
            file_type,
            patterns_found: pattern_lengths.len(),
            compression_potential,
            pattern_complexity,
            compression_ratio_estimate,
            processing_time: start.elapsed(),
            recommended_strategy,
            entropy_analysis,
            pattern_distribution: pattern_distribution_vec,
            memory_usage_mb,
        })
    }
    
    /// Sample large files to avoid memory issues
    fn sample_large_file(&self, filepath: &str, total_size: usize) -> Result<Vec<u8>, String> {
        let sample_size = 10 * 1024 * 1024; // 10MB sample
        let mut file = fs::File::open(filepath)
            .map_err(|e| format!("Failed to open file: {}", e))?;
        
        let mut buffer = vec![0u8; sample_size.min(total_size)];
        let bytes_read = std::io::Read::read(&mut file, &mut buffer)
            .map_err(|e| format!("Failed to read sample: {}", e))?;
        
        buffer.truncate(bytes_read);
        Ok(buffer)
    }
    
    /// Determine file type based on extension and size
    fn determine_file_type(&self, filename: &str, size: usize) -> String {
        let ext = Path::new(filename)
            .extension()
            .and_then(|e| e.to_str())
            .unwrap_or("unknown")
            .to_lowercase();
        
        match ext.as_str() {
            "txt" | "md" | "log" => "Text Document".to_string(),
            "rs" | "py" | "js" | "ts" | "java" | "cpp" | "c" | "h" => "Source Code".to_string(),
            "json" | "xml" | "yaml" | "toml" | "ini" => "Configuration".to_string(),
            "jpg" | "jpeg" | "png" | "gif" | "bmp" => "Image".to_string(),
            "mp4" | "avi" | "mov" | "mkv" => "Video".to_string(),
            "mp3" | "wav" | "flac" => "Audio".to_string(),
            "pdf" => "PDF Document".to_string(),
            "zip" | "rar" | "7z" => "Archive".to_string(),
            "exe" | "dll" | "so" | "dylib" => "Binary".to_string(),
            "db" | "sqlite" => "Database".to_string(),
            _ => {
                if size > 10 * 1024 * 1024 { // > 10MB
                    "Large Binary".to_string()
                } else {
                    "Unknown".to_string()
                }
            }
        }
    }
    
    /// Find files to analyze in a directory tree
    pub fn find_files_to_analyze(&self, root_path: &str, target_size_mb: usize) -> Result<Vec<String>, String> {
        let mut files = Vec::new();
        let mut total_size = 0u64;
        let target_size = target_size_mb as u64 * 1024 * 1024;
        
        self.walk_directory(root_path, &mut files, &mut total_size, target_size)?;
        
        Ok(files)
    }
    
    /// Recursively walk directory to find files
    fn walk_directory(&self, path: &str, files: &mut Vec<String>, total_size: &mut u64, target_size: u64) -> Result<(), String> {
        let entries = fs::read_dir(path)
            .map_err(|e| format!("Failed to read directory {}: {}", path, e))?;
        
        for entry in entries {
            let entry = entry.map_err(|e| format!("Failed to read entry: {}", e))?;
            let path_buf = entry.path();
            let path_str = path_buf.to_string_lossy();
            
            if path_buf.is_file() {
                if let Ok(metadata) = fs::metadata(&path_buf) {
                    let file_size = metadata.len();
                    
                    // Skip if we've reached target size
                    if *total_size >= target_size {
                        break;
                    }
                    
                    // Skip extremely large files
                    if file_size > self.max_file_size_mb as u64 * 1024 * 1024 {
                        continue;
                    }
                    
                    files.push(path_str.to_string());
                    *total_size += file_size;
                }
            } else if path_buf.is_dir() {
                // Skip common directories that won't have useful data
                let dir_name = path_buf.file_name().unwrap_or_default().to_string_lossy();
                if !dir_name.starts_with('.') && 
                   dir_name != "target" && 
                   dir_name != "node_modules" && 
                   dir_name != ".git" {
                    self.walk_directory(&path_str, files, total_size, target_size)?;
                }
            }
        }
        
        Ok(())
    }
    
    /// Analyze multiple files for comparison
    pub fn analyze_multiple_files(&self, filepaths: &[String]) -> Result<Vec<MassiveDataAnalysis>, String> {
        let mut results = Vec::new();
        let total_files = filepaths.len();
        
        println!("📁 Analyzing {} files with enhanced pattern analyzer...", total_files);
        println!("   Using adaptive threshold for optimal performance\n");
        
        for (i, filepath) in filepaths.iter().enumerate() {
            print!("   [{}/{}] Analyzing: {}... ", i + 1, total_files, 
                   Path::new(filepath).file_name().unwrap_or_default().to_string_lossy());
            
            match self.analyze_massive_file(filepath) {
                Ok(analysis) => {
                    let file_size_mb = analysis.file_size as f64 / 1_048_576.0;
                    let patterns_found = analysis.patterns_found;
                    results.push(analysis);
                    println!("✅ Done ({:.2} MB, {} patterns)", file_size_mb, patterns_found);
                }
                Err(e) => {
                    println!("❌ Failed: {}", e);
                }
            }
        }
        
        Ok(results)
    }
    
    /// Generate comprehensive analysis report
    pub fn generate_massive_analysis_report(&self, analyses: &[MassiveDataAnalysis]) -> String {
        let mut report = String::new();
        
        report.push_str("🔍 ENHANCED PATTERN ANALYZER - MASSIVE REAL DATA ANALYSIS REPORT\n");
        report.push_str(&"=".repeat(80));
        report.push_str("\n\n");
        
        // Summary statistics
        let total_files = analyses.len();
        let total_size: usize = analyses.iter().map(|a| a.file_size).sum();
        let total_size_mb = total_size as f64 / 1_048_576.0;
        let avg_compression_potential: f64 = analyses.iter().map(|a| a.compression_potential).sum::<f64>() / total_files as f64;
        let avg_complexity: f64 = analyses.iter().map(|a| a.pattern_complexity).sum::<f64>() / total_files as f64;
        let total_processing_time: Duration = analyses.iter().map(|a| a.processing_time).sum();
        let total_memory_usage: f64 = analyses.iter().map(|a| a.memory_usage_mb).sum();
        
        report.push_str(&format!("📊 SUMMARY STATISTICS:\n"));
        report.push_str(&format!("   Files analyzed: {}\n", total_files));
        report.push_str(&format!("   Total data size: {:.2} MB\n", total_size_mb));
        report.push_str(&format!("   Average compression potential: {:.3}\n", avg_compression_potential));
        report.push_str(&format!("   Average pattern complexity: {:.3}\n", avg_complexity));
        report.push_str(&format!("   Total processing time: {:?}\n", total_processing_time));
        report.push_str(&format!("   Average processing time: {:?}\n", total_processing_time / total_files as u32));
        report.push_str(&format!("   Total memory usage: {:.2} MB\n", total_memory_usage));
        report.push_str(&format!("   Processing speed: {:.2} MB/s\n", 
            total_size_mb / total_processing_time.as_secs_f64()));
        report.push_str("\n");
        
        // File type analysis
        report.push_str("📁 FILE TYPE ANALYSIS:\n");
        report.push_str(&"-".repeat(80));
        report.push_str("\n");
        
        let mut type_stats: HashMap<String, (usize, usize, f64)> = HashMap::new();
        for analysis in analyses {
            let entry = type_stats.entry(analysis.file_type.clone()).or_insert((0, 0, 0.0));
            entry.0 += 1;
            entry.1 += analysis.file_size;
            entry.2 += analysis.compression_potential;
        }
        
        for (file_type, (count, total_size, total_potential)) in type_stats {
            let avg_potential = total_potential / count as f64;
            report.push_str(&format!("   {}: {} files, {:.2} MB, avg potential: {:.3}\n", 
                file_type, count, total_size as f64 / 1_048_576.0, avg_potential));
        }
        report.push_str("\n");
        
        // Top performers
        report.push_str("🏆 TOP PERFORMERS:\n");
        report.push_str(&"-".repeat(80));
        report.push_str("\n");
        
        // Best compression
        let best_compression = analyses.iter()
            .max_by(|a, b| a.compression_potential.partial_cmp(&b.compression_potential).unwrap())
            .unwrap();
        
        // Worst compression
        let worst_compression = analyses.iter()
            .min_by(|a, b| a.compression_potential.partial_cmp(&b.compression_potential).unwrap())
            .unwrap();
        
        // Fastest processing
        let fastest_processing = analyses.iter()
            .min_by(|a, b| a.processing_time.cmp(&b.processing_time))
            .unwrap();
        
        // Largest file
        let largest_file = analyses.iter()
            .max_by(|a, b| a.file_size.cmp(&b.file_size))
            .unwrap();
        
        report.push_str(&format!("🏆 Best compression: {} ({:.3}) - {:.2} MB\n", 
            best_compression.filename, best_compression.compression_potential, 
            best_compression.file_size as f64 / 1_048_576.0));
        report.push_str(&format!("📉 Worst compression: {} ({:.3}) - {:.2} MB\n", 
            worst_compression.filename, worst_compression.compression_potential,
            worst_compression.file_size as f64 / 1_048_576.0));
        report.push_str(&format!("⚡ Fastest processing: {} ({:?}) - {:.2} MB\n", 
            fastest_processing.filename, fastest_processing.processing_time,
            fastest_processing.file_size as f64 / 1_048_576.0));
        report.push_str(&format!("📏 Largest file: {} - {:.2} MB\n", 
            largest_file.filename, largest_file.file_size as f64 / 1_048_576.0));
        report.push_str("\n");
        
        // Strategy recommendations
        report.push_str("🎯 STRATEGY RECOMMENDATIONS:\n");
        report.push_str(&"-".repeat(80));
        report.push_str("\n");
        
        let mut strategy_counts = HashMap::new();
        for analysis in analyses {
            *strategy_counts.entry(analysis.recommended_strategy.clone()).or_insert(0) += 1;
        }
        
        for (strategy, count) in strategy_counts {
            let percentage = (count as f64 / total_files as f64) * 100.0;
            report.push_str(&format!("   {}: {} files ({:.1}%)\n", strategy, count, percentage));
        }
        
        // Detailed file analysis (first 20 files)
        let detailed_count = analyses.len().min(20);
        report.push_str(&format!("\n📋 DETAILED ANALYSIS (First {} files):\n", detailed_count));
        report.push_str(&"-".repeat(80));
        report.push_str("\n");
        
        for (i, analysis) in analyses.iter().take(detailed_count).enumerate() {
            report.push_str(&format!("{}. {}\n", i + 1, analysis.filename));
            report.push_str(&format!("   Type: {}, Size: {:.2} MB\n", 
                analysis.file_type, analysis.file_size as f64 / 1_048_576.0));
            report.push_str(&format!("   Patterns: {}, Potential: {:.3}, Complexity: {:.3}\n", 
                analysis.patterns_found, analysis.compression_potential, analysis.pattern_complexity));
            report.push_str(&format!("   Strategy: {}, Time: {:?}, Memory: {:.2} MB\n", 
                analysis.recommended_strategy, analysis.processing_time, analysis.memory_usage_mb));
            
            // Top 3 pattern lengths
            if !analysis.pattern_distribution.is_empty() {
                report.push_str("   Top patterns: ");
                let top_patterns: Vec<String> = analysis.pattern_distribution
                    .iter()
                    .take(3)
                    .map(|(length, count)| format!("{}b({})", length, count))
                    .collect();
                report.push_str(&top_patterns.join(", "));
                report.push_str("\n");
            }
            report.push_str("\n");
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
    println!("🚀 ENHANCED PATTERN ANALYZER - MASSIVE REAL DATA TESTING");
    println!("{}", "=".repeat(70));
    
    // Create analyzer with adaptive threshold and large file support
    let analyzer = MassiveDataPatternAnalyzer::new()
        .with_adaptive_threshold()
        .with_max_file_size(100); // Skip files > 100MB
    
    // Target: 500MB of real data
    let target_size_mb = 500;
    println!("\n🎯 Target: Analyze {} MB of real data", target_size_mb);
    println!("   Starting from current directory and subdirectories\n");
    
    // Find files to analyze
    let current_dir = env::current_dir()
        .unwrap_or_else(|_| PathBuf::from("."))
        .to_string_lossy()
        .to_string();
    
    println!("🔍 Scanning directory tree for files...");
    match analyzer.find_files_to_analyze(&current_dir, target_size_mb) {
        Ok(files) => {
            println!("✅ Found {} files totaling {:.2} MB", files.len(), 
                     files.iter().map(|f| fs::metadata(f).map(|m| m.len()).unwrap_or(0)).sum::<u64>() as f64 / 1_048_576.0);
            
            if files.is_empty() {
                println!("❌ No files found to analyze");
                return;
            }
            
            // Analyze all files
            match analyzer.analyze_multiple_files(&files) {
                Ok(analyses) => {
                    if analyses.is_empty() {
                        println!("❌ No files were successfully analyzed");
                        return;
                    }
                    
                    // Generate comprehensive report
                    let report = analyzer.generate_massive_analysis_report(&analyses);
                    println!("\n{}", report);
                    
                    // Save report to file
                                         let report_filename = format!("massive_real_data_analysis_{}.txt", 
                         std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs());
                    
                    if let Err(e) = fs::write(&report_filename, &report) {
                        eprintln!("Warning: Could not save report: {}", e);
                    } else {
                        println!("📄 Detailed report saved to: {}", report_filename);
                    }
                    
                    // Performance summary
                    println!("\n🎯 MASSIVE DATA ANALYSIS COMPLETE!");
                    let total_size: usize = analyses.iter().map(|a| a.file_size).sum();
                    let total_time: Duration = analyses.iter().map(|a| a.processing_time).sum();
                    let avg_compression = analyses.iter().map(|a| a.compression_potential).sum::<f64>() / analyses.len() as f64;
                    
                    println!("   📊 Total data processed: {:.2} MB", total_size as f64 / 1_048_576.0);
                    println!("   ⚡ Total processing time: {:?}", total_time);
                    println!("   🎯 Average compression potential: {:.3}", avg_compression);
                    println!("   🚀 Processing speed: {:.2} MB/s", 
                        (total_size as f64 / 1_048_576.0) / total_time.as_secs_f64());
                    println!("   📁 Files successfully analyzed: {}", analyses.len());
                    
                }
                Err(e) => {
                    eprintln!("❌ Analysis failed: {}", e);
                }
            }
        }
        Err(e) => {
            eprintln!("❌ Failed to find files: {}", e);
        }
    }
    
    println!("\n🎉 Massive real data analysis complete!");
}
