// Working PDB Champion Analyzer - Avoiding Problematic Byte Strings
use std::collections::{HashMap, HashSet};
use std::time::{Instant, Duration};
use std::fs;
use std::path::{Path, PathBuf};
use std::env;

/// Configuration for the PDB analyzer
#[derive(Debug, Clone)]
pub struct PDBAnalyzerConfig {
    pub min_pattern_length: usize,
    pub max_pattern_length: usize,
    pub threshold: f64,
    pub max_file_size_mb: usize,
    pub target_compression_potential: f64,
    pub sample_size_mb: usize,
}

impl Default for PDBAnalyzerConfig {
    fn default() -> Self {
        Self {
            min_pattern_length: 4,
            max_pattern_length: 251,
            threshold: 0.03,
            max_file_size_mb: 500,
            target_compression_potential: 8000.0,
            sample_size_mb: 10,
        }
    }
}

/// Lightweight PDB file information for discovery
#[derive(Debug, Clone)]
pub struct PDBFileInfo {
    pub path: PathBuf,
    pub size_mb: f64,
    pub estimated_potential: f64,
}

/// Core PDB analysis results
#[derive(Debug, Clone)]
pub struct PDBAnalysis {
    pub file_info: PDBFileInfo,
    pub compression_metrics: CompressionMetrics,
    pub pdb_metrics: PDBMetrics,
    pub processing_time: Duration,
    pub recommended_strategy: CompressionStrategy,
}

/// Compression-related metrics
#[derive(Debug, Clone)]
pub struct CompressionMetrics {
    pub compression_potential: f64,
    pub pattern_complexity: f64,
    pub entropy: f64,
    pub estimated_ratio: f64,
    pub pattern_count: usize,
}

/// PDB-specific metrics
#[derive(Debug, Clone)]
pub struct PDBMetrics {
    pub version: PDBVersion,
    pub page_size: u32,
    pub stream_count: u32,
    pub estimated_symbol_data: usize,
    pub estimated_debug_data: usize,
    pub estimated_string_data: usize,
    pub has_type_info: bool,
}

/// PDB version enum
#[derive(Debug, Clone, PartialEq)]
pub enum PDBVersion {
    MSF70,
    PDB20,
    Unknown,
}

/// Compression strategy recommendation
#[derive(Debug, Clone)]
pub enum CompressionStrategy {
    Champion { techniques: Vec<String> },
    HighPerformance { primary: String, secondary: String },
    Standard { technique: String },
    Basic { reason: String },
}

/// Efficient pattern analysis using sampling for large files
#[derive(Debug)]
struct PatternAnalyzer {
    config: PDBAnalyzerConfig,
}

impl PatternAnalyzer {
    fn new(config: PDBAnalyzerConfig) -> Self {
        Self { config }
    }

    /// Analyze patterns in data, using sampling for large datasets
    fn analyze_patterns(&self, data: &[u8]) -> CompressionMetrics {
        let sample_data = self.get_sample_data(data);
        let entropy = self.calculate_entropy(&sample_data);
        
        let (pattern_count, compression_potential) = self.detect_patterns_efficiently(&sample_data);
        let pattern_complexity = self.estimate_complexity(&sample_data);
        let estimated_ratio = self.estimate_compression_ratio(compression_potential, entropy);

        CompressionMetrics {
            compression_potential,
            pattern_complexity,
            entropy,
            estimated_ratio,
            pattern_count,
        }
    }

    /// Get sample data for analysis
    fn get_sample_data<'a>(&self, data: &'a [u8]) -> &'a [u8] {
        let max_sample_size = self.config.sample_size_mb * 1024 * 1024;
        if data.len() <= max_sample_size {
            data
        } else {
            &data[..max_sample_size.min(data.len())]
        }
    }

    /// Efficient pattern detection using rolling hash
    fn detect_patterns_efficiently(&self, data: &[u8]) -> (usize, f64) {
        let mut total_pattern_coverage = 0usize;
        let mut unique_patterns = 0usize;
        
        let lengths_to_check = vec![4, 8, 16, 32, 64];
        
        for &length in &lengths_to_check {
            if length > data.len() / 4 { continue; }
            
            let mut pattern_counts = HashMap::new();
            
            for window in data.windows(length) {
                *pattern_counts.entry(window.to_vec()).or_insert(0) += 1;
            }
            
            for (pattern, count) in pattern_counts {
                if count > 1 {
                    let coverage = pattern.len() * count;
                    let coverage_ratio = coverage as f64 / data.len() as f64;
                    
                    if coverage_ratio >= self.config.threshold {
                        total_pattern_coverage += coverage;
                        unique_patterns += 1;
                    }
                }
            }
        }
        
        let compression_potential = (total_pattern_coverage as f64 / data.len() as f64) * 10000.0;
        (unique_patterns, compression_potential)
    }

    /// Efficient entropy calculation
    fn calculate_entropy(&self, data: &[u8]) -> f64 {
        let mut counts = [0u32; 256];
        for &byte in data {
            counts[byte as usize] += 1;
        }
        
        let len = data.len() as f64;
        counts.iter()
            .filter(|&&count| count > 0)
            .map(|&count| {
                let prob = count as f64 / len;
                -prob * prob.log2()
            })
            .sum()
    }

    /// Estimate pattern complexity using a simpler method
    fn estimate_complexity(&self, data: &[u8]) -> f64 {
        if data.len() < 100 {
            return 1.0;
        }
        
        let sample_size = data.len().min(4096);
        let sample = &data[..sample_size];
        let unique_bytes = sample.iter().collect::<HashSet<_>>().len();
        
        unique_bytes as f64 / sample.len() as f64
    }

    /// Estimate compression ratio
    fn estimate_compression_ratio(&self, potential: f64, entropy: f64) -> f64 {
        let entropy_factor = (8.0 - entropy) / 8.0;
        let potential_factor = (potential / 10000.0).min(1.0);
        
        let estimated_compression = entropy_factor * 0.4 + potential_factor * 0.6;
        (1.0 - estimated_compression).max(0.1).min(0.9)
    }
}

/// PDB-specific parser for extracting metadata
struct PDBParser;

impl PDBParser {
    /// Parse PDB header information efficiently
    fn parse_header(data: &[u8]) -> PDBMetrics {
        let version = Self::detect_version(data);
        let (page_size, stream_count) = Self::extract_basic_info(data);
        
        let estimated_symbol_data = Self::estimate_symbol_size(data, page_size);
        let estimated_debug_data = Self::estimate_debug_size(data);
        let estimated_string_data = Self::estimate_string_size(data);
        let has_type_info = Self::has_type_information(data);

        PDBMetrics {
            version,
            page_size,
            stream_count,
            estimated_symbol_data,
            estimated_debug_data,
            estimated_string_data,
            has_type_info,
        }
    }

    fn detect_version(data: &[u8]) -> PDBVersion {
        if data.len() < 32 {
            return PDBVersion::Unknown;
        }

        if data.starts_with(b"Microsoft C/C++ MSF 7.00") {
            PDBVersion::MSF70
        } else if data.len() > 0x1000 && 
                  data.get(0x1000..0x1004).map_or(false, |slice| slice == [0xE0, 0xE0, 0xE0, 0xE0]) {
            PDBVersion::PDB20
        } else {
            PDBVersion::Unknown
        }
    }

    fn extract_basic_info(data: &[u8]) -> (u32, u32) {
        let page_size = if data.len() > 0x23 {
            u32::from_le_bytes([data[0x20], data[0x21], data[0x22], data[0x23]])
        } else {
            4096
        };

        let stream_count = if data.len() > 0x2B {
            u32::from_le_bytes([data[0x28], data[0x29], data[0x2A], data[0x2B]])
        } else {
            0
        };

        (page_size, stream_count)
    }

    fn estimate_symbol_size(data: &[u8], page_size: u32) -> usize {
        let symbol_stream_size = page_size as usize * 2;
        symbol_stream_size.min(data.len() / 4)
    }

    fn estimate_debug_size(data: &[u8]) -> usize {
        let mut debug_size = 0;
        
        // Use individual byte string literals instead of vectors to avoid compilation issues
        let debug_marker = b"DEBUG";
        let rsds_marker = b"RSDS";
        let nb10_marker = b"NB10";
        let pdb_marker = b"PDB";
        
        for window in data.windows(debug_marker.len()) {
            if window == debug_marker {
                debug_size += 1024;
            }
        }
        
        for window in data.windows(rsds_marker.len()) {
            if window == rsds_marker {
                debug_size += 1024;
            }
        }
        
        for window in data.windows(nb10_marker.len()) {
            if window == nb10_marker {
                debug_size += 1024;
            }
        }
        
        for window in data.windows(pdb_marker.len()) {
            if window == pdb_marker {
                debug_size += 1024;
            }
        }
        
        debug_size.min(data.len() / 3)
    }

    fn estimate_string_size(data: &[u8]) -> usize {
        let mut string_bytes = 0;
        let mut in_string = false;
        let mut current_length = 0;

        for &byte in data.iter().take(data.len().min(100000)) {
            if byte >= 32 && byte <= 126 {
                if !in_string {
                    in_string = true;
                    current_length = 1;
                } else {
                    current_length += 1;
                }
            } else {
                if in_string && current_length > 3 {
                    string_bytes += current_length;
                }
                in_string = false;
                current_length = 0;
            }
        }

        string_bytes * 10
    }

    fn has_type_information(data: &[u8]) -> bool {
        // Use individual byte string literals instead of vectors to avoid compilation issues
        let type_marker = b"TYPE";
        let lf_marker = b"LF_";
        let tpi_marker = b"TPI";
        
        data.windows(type_marker.len()).any(|window| window == type_marker) ||
        data.windows(lf_marker.len()).any(|window| window == lf_marker) ||
        data.windows(tpi_marker.len()).any(|window| window == tpi_marker)
    }
}

/// Strategy selector for compression recommendations
struct StrategySelector;

impl StrategySelector {
    fn select_strategy(metrics: &CompressionMetrics, pdb_metrics: &PDBMetrics) -> CompressionStrategy {
        let potential = metrics.compression_potential;
        let complexity = metrics.pattern_complexity;
        let has_substantial_data = pdb_metrics.estimated_symbol_data > 100_000 || 
                                   pdb_metrics.estimated_debug_data > 100_000;

        match potential {
            p if p >= 8000.0 => CompressionStrategy::Champion {
                techniques: Self::champion_techniques(pdb_metrics, complexity),
            },
            p if p >= 5000.0 => CompressionStrategy::HighPerformance {
                primary: "Dictionary + LZ77 Hybrid".to_string(),
                secondary: if has_substantial_data { "Stream Deduplication" } else { "Pattern Matching" }.to_string(),
            },
            p if p >= 1000.0 => CompressionStrategy::Standard {
                technique: if complexity < 0.5 { "Pattern-based LZ77" } else { "Entropy-based" }.to_string(),
            },
            _ => CompressionStrategy::Basic {
                reason: "Low pattern density, minimal compression benefit".to_string(),
            },
        }
    }

    fn champion_techniques(pdb_metrics: &PDBMetrics, complexity: f64) -> Vec<String> {
        let mut techniques = Vec::new();
        
        if pdb_metrics.estimated_symbol_data > 500_000 {
            techniques.push("Symbol Dictionary Compression".to_string());
        }
        if pdb_metrics.estimated_string_data > 100_000 {
            techniques.push("String Table BWT + Dictionary".to_string());
        }
        if pdb_metrics.estimated_debug_data > 1_000_000 {
            techniques.push("Debug Info Delta Compression".to_string());
        }
        if pdb_metrics.stream_count > 5 {
            techniques.push("Cross-Stream Deduplication".to_string());
        }
        if complexity < 0.3 {
            techniques.push("Advanced Pattern Dictionary".to_string());
        }

        if techniques.is_empty() {
            techniques.push("Multi-Stage Hybrid Compression".to_string());
        }

        techniques
    }
}

/// Main PDB Champion Analyzer
pub struct PDBChampionAnalyzer {
    config: PDBAnalyzerConfig,
    pattern_analyzer: PatternAnalyzer,
}

impl PDBChampionAnalyzer {
    pub fn new() -> Self {
        let config = PDBAnalyzerConfig::default();
        let pattern_analyzer = PatternAnalyzer::new(config.clone());
        
        Self {
            config,
            pattern_analyzer,
        }
    }

    pub fn with_config(config: PDBAnalyzerConfig) -> Self {
        let pattern_analyzer = PatternAnalyzer::new(config.clone());
        Self {
            config,
            pattern_analyzer,
        }
    }

    /// Discover PDB files efficiently
    pub fn discover_pdb_files(&self, root_path: &str) -> Result<Vec<PDBFileInfo>, Box<dyn std::error::Error>> {
        let mut pdb_files = Vec::new();
        self.scan_directory(Path::new(root_path), &mut pdb_files)?;
        
        pdb_files.sort_by(|a, b| b.estimated_potential.partial_cmp(&a.estimated_potential).unwrap());
        
        Ok(pdb_files)
    }

    fn scan_directory(&self, dir: &Path, files: &mut Vec<PDBFileInfo>) -> Result<(), Box<dyn std::error::Error>> {
        if !dir.is_dir() {
            return Ok(());
        }

        for entry in fs::read_dir(dir)? {
            let entry = entry?;
            let path = entry.path();

            if path.is_file() && self.is_pdb_file(&path) {
                if let Ok(metadata) = fs::metadata(&path) {
                    let size_bytes = metadata.len();
                    let size_mb = size_bytes as f64 / 1_048_576.0;

                    if size_mb > self.config.max_file_size_mb as f64 || size_mb < 0.1 {
                        continue;
                    }

                    let estimated_potential = (size_mb * 100.0).min(10000.0);

                    files.push(PDBFileInfo {
                        path,
                        size_mb,
                        estimated_potential,
                    });
                }
            } else if path.is_dir() {
                let dir_name = path.file_name()
                    .and_then(|n| n.to_str())
                    .unwrap_or("");
                
                if !dir_name.starts_with('.') && 
                   !["target", "node_modules", ".git", "tmp", "temp"].contains(&dir_name) {
                    self.scan_directory(&path, files)?;
                }
            }
        }

        Ok(())
    }

    fn is_pdb_file(&self, path: &Path) -> bool {
        path.extension()
            .and_then(|ext| ext.to_str())
            .map_or(false, |ext| ext.to_lowercase() == "pdb")
    }

    /// Analyze a single PDB file
    pub fn analyze_pdb(&self, file_info: &PDBFileInfo) -> Result<PDBAnalysis, Box<dyn std::error::Error>> {
        let start_time = Instant::now();
        
        let data = fs::read(&file_info.path)?;
        
        let compression_metrics = self.pattern_analyzer.analyze_patterns(&data);
        let pdb_metrics = PDBParser::parse_header(&data);
        let recommended_strategy = StrategySelector::select_strategy(&compression_metrics, &pdb_metrics);
        
        Ok(PDBAnalysis {
            file_info: file_info.clone(),
            compression_metrics,
            pdb_metrics,
            processing_time: start_time.elapsed(),
            recommended_strategy,
        })
    }

    /// Analyze multiple PDB files with progress reporting
    pub fn analyze_multiple(&self, files: &[PDBFileInfo]) -> Vec<Result<PDBAnalysis, Box<dyn std::error::Error>>> {
        println!("Analyzing {} PDB files...", files.len());
        
        files.iter().enumerate().map(|(i, file_info)| {
            print!("\r[{:3}/{:3}] Analyzing {}...", 
                   i + 1, files.len(), 
                   file_info.path.file_name().unwrap_or_default().to_string_lossy());
            std::io::Write::flush(&mut std::io::stdout()).ok();
            
            self.analyze_pdb(file_info)
        }).collect()
    }

    /// Generate comprehensive report
    pub fn generate_report(&self, analyses: &[PDBAnalysis]) -> String {
        let mut report = String::new();
        
        report.push_str("PDB CHAMPION ANALYSIS REPORT\n");
        report.push_str(&"=".repeat(80));
        report.push_str("\n\n");

        let total_files = analyses.len();
        let total_size_mb: f64 = analyses.iter()
            .map(|a| a.file_info.size_mb)
            .sum();
        let avg_compression: f64 = analyses.iter()
            .map(|a| a.compression_metrics.compression_potential)
            .sum::<f64>() / total_files as f64;
        let total_time: Duration = analyses.iter().map(|a| a.processing_time).sum();

        report.push_str(&format!("SUMMARY:\n"));
        report.push_str(&format!("   Files analyzed: {}\n", total_files));
        report.push_str(&format!("   Total size: {:.2} MB\n", total_size_mb));
        report.push_str(&format!("   Average compression potential: {:.0}\n", avg_compression));
        report.push_str(&format!("   Processing time: {:?}\n", total_time));
        report.push_str(&format!("   Speed: {:.2} MB/s\n\n", total_size_mb / total_time.as_secs_f64()));

        let mut ranked: Vec<_> = analyses.iter().collect();
        ranked.sort_by(|a, b| b.compression_metrics.compression_potential
                              .partial_cmp(&a.compression_metrics.compression_potential)
                              .unwrap());

        report.push_str("TOP COMPRESSION CANDIDATES:\n");
        report.push_str(&"-".repeat(80));
        report.push_str("\n");

        for (i, analysis) in ranked.iter().take(10).enumerate() {
            let medal = if i == 0 {
                "1st".to_string()
            } else if i == 1 {
                "2nd".to_string()
            } else if i == 2 {
                "3rd".to_string()
            } else {
                format!("{}th", i + 1)
            };

            report.push_str(&format!("{} {}. {} ({:.0} potential, {:.2} MB)\n",
                medal, i + 1,
                analysis.file_info.path.file_name().unwrap_or_default().to_string_lossy(),
                analysis.compression_metrics.compression_potential,
                analysis.file_info.size_mb));
            
            report.push_str(&format!("   Strategy: {:?}\n", analysis.recommended_strategy));
            report.push_str(&format!("   Entropy: {:.2}, Patterns: {}\n\n", 
                analysis.compression_metrics.entropy,
                analysis.compression_metrics.pattern_count));
        }

        let mut strategy_counts = HashMap::new();
        for analysis in analyses {
            let strategy_name = match &analysis.recommended_strategy {
                CompressionStrategy::Champion { .. } => "Champion",
                CompressionStrategy::HighPerformance { .. } => "High Performance",
                CompressionStrategy::Standard { .. } => "Standard",
                CompressionStrategy::Basic { .. } => "Basic",
            };
            *strategy_counts.entry(strategy_name).or_insert(0) += 1;
        }

        report.push_str("STRATEGY DISTRIBUTION:\n");
        report.push_str(&"-".repeat(80));
        report.push_str("\n");
        for (strategy, count) in strategy_counts {
            let percentage = (count as f64 / total_files as f64) * 100.0;
            report.push_str(&format!("   {}: {} files ({:.1}%)\n", strategy, count, percentage));
        }

        report
    }
}

impl Default for PDBChampionAnalyzer {
    fn default() -> Self {
        Self::new()
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("PDB CHAMPION ANALYZER - Working Version");
    println!("{}", "=".repeat(70));
    
    let analyzer = PDBChampionAnalyzer::new();
    
    let current_dir = env::current_dir()?;
    let current_dir_str = current_dir.to_string_lossy();
    
    println!("\nDiscovering PDB files in: {}", current_dir_str);
    
    let pdb_files = analyzer.discover_pdb_files(&current_dir_str)?;
    
    if pdb_files.is_empty() {
        println!("No PDB files found");
        println!("Try running from a directory with compiled projects");
        return Ok(());
    }
    
    println!("Found {} PDB files", pdb_files.len());
    
    let files_to_analyze = &pdb_files[..pdb_files.len().min(20)];
    let results = analyzer.analyze_multiple(files_to_analyze);
    
    let successful_analyses: Vec<PDBAnalysis> = results.into_iter()
        .filter_map(|r| r.ok())
        .collect();
    
    println!("\nSuccessfully analyzed {} files", successful_analyses.len());
    
    if !successful_analyses.is_empty() {
        let report = analyzer.generate_report(&successful_analyses);
        println!("\n{}", report);
        
        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)?
            .as_secs();
        let report_filename = format!("pdb_analysis_report_{}.txt", timestamp);
        fs::write(&report_filename, &report)?;
        println!("Report saved to: {}", report_filename);
    }
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_config_creation() {
        let config = PDBAnalyzerConfig::default();
        assert_eq!(config.min_pattern_length, 4);
        assert_eq!(config.target_compression_potential, 8000.0);
    }

    #[test]
    fn test_pdb_version_detection() {
        let msf_data = b"Microsoft C/C++ MSF 7.00\x0D\x0A\x1A\x44\x53\x00\x00\x00";
        let version = PDBParser::detect_version(msf_data);
        assert_eq!(version, PDBVersion::MSF70);
    }

    #[test]
    fn test_pattern_analyzer() {
        let config = PDBAnalyzerConfig::default();
        let analyzer = PatternAnalyzer::new(config);
        
        let test_data = b"ABCABCABCDEFDEFDEF";
        let metrics = analyzer.analyze_patterns(test_data);
        
        assert!(metrics.compression_potential > 0.0);
        assert!(metrics.entropy > 0.0);
    }
}
