// Universal Compression Engine for MMH-RS
// Phase 1: Foundation & Core Architecture Integration

use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::time::Instant;
use std::fs;

mod universal_file_detector;
mod adaptive_sampling_system;

use universal_file_detector::{UniversalFileDetector, FileTypeInfo, FileCategory};
use adaptive_sampling_system::{AdaptiveSamplingSystem, SamplingResult};

/// Configuration for the universal compression engine
#[derive(Debug, Clone)]
pub struct UniversalCompressionConfig {
    pub max_file_size_mb: usize,
    pub max_memory_mb: usize,
    pub enable_streaming: bool,
    pub sample_size_mb: usize,
    pub compression_threshold: f64,
    pub detailed_reporting: bool,
}

impl Default for UniversalCompressionConfig {
    fn default() -> Self {
        Self {
            max_file_size_mb: 1000, // 1GB
            max_memory_mb: 100,     // 100MB
            enable_streaming: true,
            sample_size_mb: 10,     // 10MB
            compression_threshold: 0.3, // 30% compression potential
            detailed_reporting: true,
        }
    }
}

/// Analysis result for a single file
#[derive(Debug, Clone)]
pub struct FileAnalysisResult {
    pub file_path: String,
    pub file_size: u64,
    pub file_type: Option<FileTypeInfo>,
    pub compression_potential: f64,
    pub sampling_result: Option<SamplingResult>,
    pub analysis_time_ms: u64,
    pub memory_used: usize,
    pub recommendations: Vec<String>,
}

/// Directory analysis result
#[derive(Debug, Clone)]
pub struct DirectoryAnalysisResult {
    pub directory_path: String,
    pub total_files: usize,
    pub total_size: u64,
    pub file_types: HashMap<FileCategory, usize>,
    pub compression_potential_by_type: HashMap<FileCategory, f64>,
    pub top_compression_candidates: Vec<FileAnalysisResult>,
    pub analysis_time_ms: u64,
    pub memory_peak: usize,
}

/// Universal compression engine
pub struct UniversalCompressionEngine {
    config: UniversalCompressionConfig,
    file_detector: UniversalFileDetector,
    sampling_system: AdaptiveSamplingSystem,
}

impl UniversalCompressionEngine {
    pub fn new(config: UniversalCompressionConfig) -> Self {
        Self {
            file_detector: UniversalFileDetector::new(),
            sampling_system: AdaptiveSamplingSystem::new(),
            config,
        }
    }

    /// Analyze a single file for compression potential
    pub fn analyze_file(&self, file_path: &Path) -> Result<FileAnalysisResult, Box<dyn std::error::Error>> {
        let start_time = Instant::now();
        
        // Check file size
        let metadata = fs::metadata(file_path)?;
        let file_size = metadata.len();
        
        if file_size > (self.config.max_file_size_mb * 1024 * 1024) as u64 {
            return Err(format!("File too large: {} MB (max: {} MB)", 
                file_size / (1024 * 1024), self.config.max_file_size_mb).into());
        }

        // Detect file type
        let file_type = self.file_detector.detect_file_type(file_path)?;
        let compression_potential = self.file_detector.analyze_compression_potential(file_path)?;
        
        // Sample file if compression potential is above threshold
        let sampling_result = if compression_potential >= self.config.compression_threshold {
            if file_size > (self.config.sample_size_mb * 1024 * 1024) as u64 && self.config.enable_streaming {
                // Use streaming for large files
                let file_info = file_type.clone().unwrap_or_else(|| self.create_default_file_info(file_path));
                Some(self.sampling_system.stream_sample_large_file(
                    file_path, 
                    &file_info, 
                    self.config.max_memory_mb
                )?)
            } else {
                // Use standard sampling for smaller files
                if let Some(ref info) = file_type {
                    Some(self.sampling_system.sample_file(file_path, info)?)
                } else {
                    None
                }
            }
        } else {
            None
        };

        let analysis_time = start_time.elapsed().as_millis() as u64;
        let memory_used = sampling_result.as_ref().map(|r| r.memory_used).unwrap_or(0);
        
        // Generate recommendations
        let recommendations = self.generate_recommendations(&file_type, compression_potential, file_size);

        Ok(FileAnalysisResult {
            file_path: file_path.to_string_lossy().to_string(),
            file_size,
            file_type,
            compression_potential,
            sampling_result,
            analysis_time_ms: analysis_time,
            memory_used,
            recommendations,
        })
    }

    /// Analyze an entire directory for compression opportunities
    pub fn analyze_directory(&self, dir_path: &Path) -> Result<DirectoryAnalysisResult, Box<dyn std::error::Error>> {
        let start_time = Instant::now();
        let mut total_files = 0;
        let mut total_size = 0;
        let mut file_types: HashMap<FileCategory, usize> = HashMap::new();
        let mut compression_potential_by_type: HashMap<FileCategory, Vec<f64>> = HashMap::new();
        let mut all_results: Vec<FileAnalysisResult> = Vec::new();
        let mut memory_peak = 0;

        // Recursively scan directory
        for entry in fs::read_dir(dir_path)? {
            let entry = entry?;
            let path = entry.path();
            
            if path.is_file() {
                match self.analyze_file(&path) {
                    Ok(result) => {
                        total_files += 1;
                        total_size += result.file_size;
                        memory_peak = memory_peak.max(result.memory_used);
                        
                        if let Some(ref file_type) = result.file_type {
                            *file_types.entry(file_type.category.clone()).or_insert(0) += 1;
                            compression_potential_by_type
                                .entry(file_type.category.clone())
                                .or_insert_with(Vec::new)
                                .push(result.compression_potential);
                        }
                        
                        all_results.push(result);
                    }
                    Err(e) => {
                        eprintln!("Error analyzing {}: {}", path.display(), e);
                        continue;
                    }
                }
            }
        }

        // Calculate average compression potential by type
        let mut avg_compression_by_type: HashMap<FileCategory, f64> = HashMap::new();
        for (category, potentials) in &compression_potential_by_type {
            let avg = potentials.iter().sum::<f64>() / potentials.len() as f64;
            avg_compression_by_type.insert(category.clone(), avg);
        }

        // Sort by compression potential to find top candidates
        all_results.sort_by(|a, b| b.compression_potential.partial_cmp(&a.compression_potential).unwrap());
        let top_candidates = all_results.into_iter().take(10).collect();

        let analysis_time = start_time.elapsed().as_millis() as u64;

        Ok(DirectoryAnalysisResult {
            directory_path: dir_path.to_string_lossy().to_string(),
            total_files,
            total_size,
            file_types,
            compression_potential_by_type: avg_compression_by_type,
            top_compression_candidates: top_candidates,
            analysis_time_ms: analysis_time,
            memory_peak,
        })
    }

    /// Create default file info for unknown file types
    fn create_default_file_info(&self, file_path: &Path) -> FileTypeInfo {
        let category = if let Some(ext) = file_path.extension() {
            if let Some(ext_str) = ext.to_str() {
                self.file_detector.get_category_by_extension(ext_str)
            } else {
                FileCategory::Unknown
            }
        } else {
            FileCategory::Unknown
        };

        FileTypeInfo {
            name: "Unknown File Type".to_string(),
            extension: file_path.extension()
                .and_then(|e| e.to_str())
                .unwrap_or("unknown")
                .to_string(),
            mime_type: "application/octet-stream".to_string(),
            category,
            description: "File type not recognized".to_string(),
            compression_potential: self.file_detector.get_default_compression_potential(category),
        }
    }

    /// Generate compression recommendations based on analysis
    fn generate_recommendations(&self, file_type: &Option<FileTypeInfo>, compression_potential: f64, file_size: u64) -> Vec<String> {
        let mut recommendations = Vec::new();

        if let Some(ref info) = file_type {
            match info.category {
                FileCategory::Executable => {
                    if compression_potential > 0.8 {
                        recommendations.push("High compression potential: Use LZ77 + Huffman combination".to_string());
                        recommendations.push("Focus on import/export table compression".to_string());
                    }
                }
                FileCategory::Debug => {
                    if compression_potential > 0.9 {
                        recommendations.push("Excellent compression potential: Use dictionary + RLE combination".to_string());
                        recommendations.push("Compress symbol tables and string pools".to_string());
                    }
                }
                FileCategory::Archive => {
                    if compression_potential < 0.2 {
                        recommendations.push("Already compressed: Minimal additional compression possible".to_string());
                        recommendations.push("Consider recompression only if format allows".to_string());
                    }
                }
                FileCategory::Media => {
                    if compression_potential > 0.3 {
                        recommendations.push("Moderate compression: Use delta encoding + LZ77".to_string());
                        recommendations.push("Focus on frame header compression".to_string());
                    }
                }
                FileCategory::Document => {
                    if compression_potential > 0.7 {
                        recommendations.push("Good compression potential: Use LZ77 + Huffman".to_string());
                        recommendations.push("Compress text content and metadata".to_string());
                    }
                }
                _ => {}
            }
        }

        // Size-based recommendations
        if file_size > 100 * 1024 * 1024 { // 100MB
            recommendations.push("Large file: Use streaming compression to manage memory".to_string());
            recommendations.push("Consider chunked processing for better performance".to_string());
        }

        // Compression potential recommendations
        if compression_potential > 0.8 {
            recommendations.push("Very high compression potential: Prioritize this file".to_string());
        } else if compression_potential > 0.5 {
            recommendations.push("Good compression potential: Worth compressing".to_string());
        } else if compression_potential < 0.2 {
            recommendations.push("Low compression potential: Consider skipping".to_string());
        }

        recommendations
    }

    /// Generate comprehensive analysis report
    pub fn generate_report(&self, dir_result: &DirectoryAnalysisResult) -> String {
        let mut report = String::new();
        
        report.push_str(&format!("=== MMH-RS Universal Compression Analysis Report ===\n\n"));
        report.push_str(&format!("Directory: {}\n", dir_result.directory_path));
        report.push_str(&format!("Analysis Time: {} ms\n", dir_result.analysis_time_ms));
        report.push_str(&format!("Total Files: {}\n", dir_result.total_files));
        report.push_str(&format!("Total Size: {:.2} MB\n", dir_result.total_size as f64 / (1024.0 * 1024.0)));
        report.push_str(&format!("Memory Peak: {:.2} MB\n\n", dir_result.memory_peak as f64 / (1024.0 * 1024.0)));

        // File type breakdown
        report.push_str("=== File Type Breakdown ===\n");
        for (category, count) in &dir_result.file_types {
            let avg_potential = dir_result.compression_potential_by_type.get(category).unwrap_or(&0.0);
            report.push_str(&format!("{:?}: {} files, Avg Compression Potential: {:.1}%\n", 
                category, count, avg_potential * 100.0));
        }
        report.push_str("\n");

        // Top compression candidates
        report.push_str("=== Top Compression Candidates ===\n");
        for (i, result) in dir_result.top_compression_candidates.iter().enumerate() {
            report.push_str(&format!("{}. {} ({:.2} MB) - Potential: {:.1}%\n", 
                i + 1, 
                std::path::Path::new(&result.file_path).file_name().unwrap().to_string_lossy(),
                result.file_size as f64 / (1024.0 * 1024.0),
                result.compression_potential * 100.0));
            
            if self.config.detailed_reporting {
                for recommendation in &result.recommendations {
                    report.push_str(&format!("   → {}\n", recommendation));
                }
            }
        }

        // Summary recommendations
        report.push_str("\n=== Summary Recommendations ===\n");
        let high_potential_count = dir_result.top_compression_candidates.iter()
            .filter(|r| r.compression_potential > 0.7)
            .count();
        
        if high_potential_count > 0 {
            report.push_str(&format!("• {} files have high compression potential (>70%)\n", high_potential_count));
            report.push_str("• Focus on these files for maximum space savings\n");
        }
        
        let total_potential_savings: f64 = dir_result.top_compression_candidates.iter()
            .map(|r| r.file_size as f64 * r.compression_potential)
            .sum();
        
        report.push_str(&format!("• Estimated total compression savings: {:.2} MB\n", 
            total_potential_savings / (1024.0 * 1024.0)));

        report
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_engine_creation() {
        let config = UniversalCompressionConfig::default();
        let engine = UniversalCompressionEngine::new(config);
        assert_eq!(engine.config.max_file_size_mb, 1000);
        assert_eq!(engine.config.max_memory_mb, 100);
    }

    #[test]
    fn test_default_config() {
        let config = UniversalCompressionConfig::default();
        assert!(config.enable_streaming);
        assert!(config.detailed_reporting);
        assert_eq!(config.compression_threshold, 0.3);
    }
}
