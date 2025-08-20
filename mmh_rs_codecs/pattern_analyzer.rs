//! Pattern analysis module for MMH-RS compression system
//! 
//! This module provides advanced pattern recognition and analysis
//! for optimal compression strategy selection.

use crate::{MMHResult, PatternAnalysis, MMHError};
use std::collections::{HashMap, HashSet};
use std::time::{Instant, Duration};

/// Enhanced pattern analysis with additional metrics
#[derive(Debug, Clone)]
pub struct EnhancedPatternAnalysis {
    pub pattern_lengths: Vec<usize>,
    pub pattern_frequencies: Vec<f64>,
    pub entropy_reduction: f64,
    pub compression_potential: f64,
    pub pattern_complexity: f64,
    pub compression_ratio_estimate: f64,
    pub processing_time: Duration,
}

/// Performance metrics for pattern analysis
#[derive(Debug, Default)]
pub struct AnalysisMetrics {
    pub patterns_found: usize,
    pub bytes_processed: usize,
    pub processing_time: Duration,
    pub unique_patterns: usize,
}

/// Compression strategy recommendations
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum CompressionStrategy {
    DictionaryBased { dict_size: usize },
    LZ77Variant { window_size: usize },
    Hybrid { dict_size: usize, window_size: usize },
    Standard,
}

/// Pattern analyzer for identifying optimal compression strategies
#[derive(Clone)]
pub struct PatternAnalyzer {
    min_pattern_length: usize,
    max_pattern_length: usize,
    threshold: f64,
    adaptive_threshold: bool,
}

impl PatternAnalyzer {
    /// Create a new pattern analyzer
    pub fn new() -> Self {
        Self {
            min_pattern_length: 4,
            max_pattern_length: 251,
            threshold: 0.1,
            adaptive_threshold: false,
        }
    }
    
    /// Create a pattern analyzer with custom parameters
    pub fn with_params(min_length: usize, max_length: usize, threshold: f64) -> Self {
        Self {
            min_pattern_length: min_length,
            max_pattern_length: max_length,
            threshold: threshold,
            adaptive_threshold: false,
        }
    }
    
    /// Enable adaptive threshold adjustment
    pub fn with_adaptive_threshold(mut self) -> Self {
        self.adaptive_threshold = true;
        self
    }
    
    /// Enhanced analysis with additional metrics
    pub fn analyze_enhanced(&self, data: &[u8]) -> MMHResult<EnhancedPatternAnalysis> {
        let start = Instant::now();
        
        if data.is_empty() {
            return Err(MMHError::PatternAnalysis("Empty data provided".to_string()));
        }
        
        let mut pattern_lengths = Vec::new();
        let mut pattern_frequencies = Vec::new();
        let mut total_bytes_covered = 0;
        let mut unique_patterns_count = 0;
        
        // Calculate adaptive threshold if enabled
        let effective_threshold = if self.adaptive_threshold {
            self.calculate_adaptive_threshold(data)
        } else {
            self.threshold
        };
        
        // Analyze patterns of different lengths
        for length in self.min_pattern_length..=self.max_pattern_length.min(data.len() / 2) {
            let (patterns, bytes_covered) = self.find_patterns_with_coverage(data, length);
            
            if !patterns.is_empty() {
                let frequency = bytes_covered as f64 / data.len() as f64;
                
                // Only include patterns that meet the threshold
                if frequency >= effective_threshold {
                    pattern_lengths.push(length);
                    pattern_frequencies.push(frequency);
                    total_bytes_covered += bytes_covered;
                    unique_patterns_count += patterns.len();
                }
            }
        }
        
        let entropy_reduction = self.calculate_entropy_reduction(data, &pattern_frequencies);
        let compression_potential = total_bytes_covered as f64 / data.len() as f64;
        let pattern_complexity = self.calculate_pattern_complexity(data);
        let compression_ratio_estimate = self.estimate_compression_ratio(&pattern_frequencies, pattern_complexity);
        
        Ok(EnhancedPatternAnalysis {
            pattern_lengths,
            pattern_frequencies,
            entropy_reduction,
            compression_potential,
            pattern_complexity,
            compression_ratio_estimate,
            processing_time: start.elapsed(),
        })
    }
    
    /// Original analyze method for backward compatibility
    pub fn analyze(&self, data: &[u8]) -> MMHResult<PatternAnalysis> {
        let enhanced = self.analyze_enhanced(data)?;
        Ok(PatternAnalysis {
            pattern_lengths: enhanced.pattern_lengths,
            pattern_frequencies: enhanced.pattern_frequencies,
            entropy_reduction: enhanced.entropy_reduction,
            compression_potential: enhanced.compression_potential,
        })
    }
    
    /// Analyze with detailed metrics
    pub fn analyze_with_metrics(&self, data: &[u8]) -> MMHResult<(PatternAnalysis, AnalysisMetrics)> {
        let enhanced = self.analyze_enhanced(data)?;
        
        let analysis = PatternAnalysis {
            pattern_lengths: enhanced.pattern_lengths.clone(),
            pattern_frequencies: enhanced.pattern_frequencies.clone(),
            entropy_reduction: enhanced.entropy_reduction,
            compression_potential: enhanced.compression_potential,
        };
        
        let metrics = AnalysisMetrics {
            patterns_found: enhanced.pattern_lengths.len(),
            bytes_processed: data.len(),
            processing_time: enhanced.processing_time,
            unique_patterns: enhanced.pattern_lengths.iter().zip(&enhanced.pattern_frequencies).count(),
        };
        
        Ok((analysis, metrics))
    }
    
    /// Find repeating patterns with byte coverage calculation
    fn find_patterns_with_coverage(&self, data: &[u8], length: usize) -> (HashMap<Vec<u8>, usize>, usize) {
        let mut patterns = HashMap::new();
        let mut bytes_covered = 0;
        
        // Use sliding window instead of chunks for better pattern detection
        for i in 0..=(data.len().saturating_sub(length)) {
            let pattern = data[i..i + length].to_vec();
            *patterns.entry(pattern).or_insert(0) += 1;
        }
        
        // Calculate bytes covered by patterns that appear multiple times
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
    
    /// Find repeating patterns of a specific length (legacy method for compatibility)
    fn find_patterns(&self, data: &[u8], length: usize) -> HashMap<Vec<u8>, usize> {
        let (patterns, _) = self.find_patterns_with_coverage(data, length);
        patterns
    }
    
    /// Calculate entropy reduction based on pattern frequency
    fn calculate_entropy_reduction(&self, data: &[u8], frequencies: &[f64]) -> f64 {
        if frequencies.is_empty() || data.is_empty() {
            return 0.0;
        }
        
        // Calculate original entropy
        let mut byte_counts = [0u32; 256];
        for &byte in data {
            byte_counts[byte as usize] += 1;
        }
        
        let data_len = data.len() as f64;
        let original_entropy: f64 = byte_counts
            .iter()
            .filter(|&&count| count > 0)
            .map(|&count| {
                let prob = count as f64 / data_len;
                -prob * prob.log2()
            })
            .sum();
        
        // Estimate entropy reduction based on pattern coverage
        let max_frequency = frequencies.iter().cloned().fold(0.0f64, f64::max);
        let entropy_reduction = original_entropy * max_frequency;
        
        entropy_reduction.min(original_entropy).max(0.0)
    }
    
    /// Calculate compression potential based on pattern analysis
    fn calculate_compression_potential(&self, frequencies: &[f64]) -> f64 {
        if frequencies.is_empty() {
            return 0.0;
        }
        
        // Use maximum frequency as potential indicator
        let max_frequency = frequencies.iter().cloned().fold(0.0f64, f64::max);
        
        // Apply diminishing returns curve
        let potential = 1.0 - (-2.0 * max_frequency).exp();
        
        potential.min(1.0).max(0.0)
    }
    
    /// Calculate adaptive threshold based on data characteristics
    fn calculate_adaptive_threshold(&self, data: &[u8]) -> f64 {
        let entropy = self.calculate_data_entropy(data);
        let size_factor = (data.len() as f64).log2() / 20.0;
        let entropy_factor = entropy / 8.0; // Normalize to 0-1 range
        
        let adaptive = self.threshold * (1.0 + size_factor * 0.5 - entropy_factor * 0.3);
        adaptive.max(0.01).min(0.5) // Reasonable bounds
    }
    
    /// Calculate data entropy
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
    
    /// Calculate pattern complexity using simplified Kolmogorov complexity estimate
    fn calculate_pattern_complexity(&self, data: &[u8]) -> f64 {
        let mut unique_patterns = HashSet::new();
        let mut total_patterns = 0;
        
        // Sample patterns to avoid performance issues on large data
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
    
    /// Estimate compression ratio based on pattern analysis
    fn estimate_compression_ratio(&self, frequencies: &[f64], complexity: f64) -> f64 {
        if frequencies.is_empty() {
            return 1.0;
        }
        
        let max_frequency = frequencies.iter().cloned().fold(0.0f64, f64::max);
        let avg_frequency = frequencies.iter().sum::<f64>() / frequencies.len() as f64;
        
        // Estimate compression ratio: lower complexity and higher frequency = better compression
        let base_ratio = 1.0 - (avg_frequency * 0.7 + max_frequency * 0.3);
        let complexity_factor = 0.5 + complexity * 0.5; // More complex = worse compression
        
        (base_ratio * complexity_factor).max(0.1).min(1.0)
    }
    
    /// Get recommended codec based on pattern analysis
    pub fn recommend_codec(&self, analysis: &PatternAnalysis) -> crate::CodecType {
        // Check if we have long patterns with high frequency
        let has_long_patterns = analysis.pattern_lengths.iter().any(|&len| len > 100);
        let max_frequency = analysis.pattern_frequencies.iter().cloned().fold(0.0f64, f64::max);
        
        if has_long_patterns && analysis.compression_potential > 0.7 {
            return crate::CodecType::Pattern251;
        }
        
        if analysis.compression_potential > 0.6 || max_frequency > 0.5 {
            return crate::CodecType::Hierarchical;
        }
        
        if analysis.compression_potential > 0.3 || max_frequency > 0.3 {
            return crate::CodecType::Turbo;
        }
        
        // Default to standard compression
        crate::CodecType::ZSTD
    }
    
    /// Determine optimal compression strategy
    pub fn determine_strategy(&self, analysis: &PatternAnalysis) -> CompressionStrategy {
        let has_long_patterns = analysis.pattern_lengths.iter().any(|&len| len > 64);
        let max_frequency = analysis.pattern_frequencies.iter().cloned().fold(0.0f64, f64::max);
        let avg_pattern_length = if analysis.pattern_lengths.is_empty() {
            0.0
        } else {
            analysis.pattern_lengths.iter().sum::<usize>() as f64 / analysis.pattern_lengths.len() as f64
        };
        
        match (has_long_patterns, analysis.compression_potential, max_frequency) {
            (true, potential, _) if potential > 0.7 => {
                CompressionStrategy::DictionaryBased {
                    dict_size: (avg_pattern_length * 100.0) as usize,
                }
            }
            (_, potential, freq) if potential > 0.5 || freq > 0.6 => {
                CompressionStrategy::Hybrid {
                    dict_size: (avg_pattern_length * 50.0) as usize,
                    window_size: 32768,
                }
            }
            (_, potential, _) if potential > 0.3 => {
                CompressionStrategy::LZ77Variant {
                    window_size: if avg_pattern_length > 32.0 { 65536 } else { 32768 },
                }
            }
            _ => CompressionStrategy::Standard,
        }
    }
    
    /// Get recommended codec based on pattern analysis (enhanced)
    pub fn recommend_codec_enhanced(&self, analysis: &PatternAnalysis) -> crate::CodecType {
        let strategy = self.determine_strategy(analysis);
        
        match strategy {
            CompressionStrategy::DictionaryBased { .. } => crate::CodecType::Pattern251,
            CompressionStrategy::Hybrid { .. } => crate::CodecType::Hierarchical,
            CompressionStrategy::LZ77Variant { .. } => crate::CodecType::Turbo,
            CompressionStrategy::Standard => crate::CodecType::ZSTD,
        }
    }
    
    /// Determine optimal compression level
    fn determine_compression_level(&self, analysis: &PatternAnalysis) -> u8 {
        if analysis.compression_potential > 0.8 {
            9 // Maximum compression for highly repetitive data
        } else if analysis.compression_potential > 0.5 {
            6 // Balanced compression
        } else if analysis.compression_potential > 0.2 {
            3 // Fast compression
        } else {
            1 // Minimal compression overhead
        }
    }
    
    /// Get detailed pattern statistics for debugging
    pub fn get_pattern_stats(&self, data: &[u8]) -> MMHResult<HashMap<usize, usize>> {
        if data.is_empty() {
            return Err(MMHError::PatternAnalysis("Empty data provided".to_string()));
        }
        
        let mut stats = HashMap::new();
        
        for length in self.min_pattern_length..=self.max_pattern_length.min(data.len() / 2) {
            let patterns = self.find_patterns(data, length);
            if !patterns.is_empty() {
                stats.insert(length, patterns.len());
            }
        }
        
        Ok(stats)
    }
    
    /// Legacy method for compatibility with hierarchical_codec
    pub fn analyze_data(&self, data: &[u8]) -> MMHResult<PatternAnalysis> {
        self.analyze(data)
    }
    
    /// Legacy method for compatibility with hierarchical_codec
    pub fn generate_codebook(&self, _pattern_table: &PatternAnalysis) -> MMHResult<()> {
        // This is a placeholder for compatibility
        // The actual codebook generation is handled by the hierarchical codec
        Ok(())
    }
    
    /// Legacy method for compatibility with hierarchical_codec
    pub fn print_analysis(&self, _pattern_table: &PatternAnalysis) -> Result<(), Box<dyn std::error::Error>> {
        // This is a placeholder for compatibility
        // The actual printing is handled by the hierarchical codec
        Ok(())
    }
}

impl Default for PatternAnalyzer {
    fn default() -> Self {
        Self::new()
    }
}

// Helper trait for analysis extensions
pub trait PatternAnalysisExt {
    fn has_repeating_long_patterns(&self) -> bool;
    fn has_frequent_short_patterns(&self) -> bool;
    fn has_high_entropy(&self) -> bool;
    fn optimal_dictionary_size(&self) -> usize;
}

impl PatternAnalysisExt for PatternAnalysis {
    fn has_repeating_long_patterns(&self) -> bool {
        self.pattern_lengths.iter().any(|&len| len > 100)
    }
    
    fn has_frequent_short_patterns(&self) -> bool {
        self.pattern_frequencies.iter().any(|&freq| freq > 0.3) &&
        self.pattern_lengths.iter().any(|&len| len < 20)
    }
    
    fn has_high_entropy(&self) -> bool {
        self.entropy_reduction < 1.0 && self.compression_potential < 0.3
    }
    
    fn optimal_dictionary_size(&self) -> usize {
        let avg_length = if self.pattern_lengths.is_empty() {
            32
        } else {
            self.pattern_lengths.iter().sum::<usize>() / self.pattern_lengths.len()
        };
        
        (avg_length * self.pattern_lengths.len()).min(65536).max(1024)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_pattern_analyzer_creation() {
        let analyzer = PatternAnalyzer::new();
        assert_eq!(analyzer.min_pattern_length, 4);
        assert_eq!(analyzer.max_pattern_length, 251);
        assert_eq!(analyzer.threshold, 0.1);
    }
    
    #[test]
    fn test_pattern_analyzer_with_params() {
        let analyzer = PatternAnalyzer::with_params(8, 128, 0.2);
        assert_eq!(analyzer.min_pattern_length, 8);
        assert_eq!(analyzer.max_pattern_length, 128);
        assert_eq!(analyzer.threshold, 0.2);
    }
    
    #[test]
    fn test_analyze_empty_data() {
        let analyzer = PatternAnalyzer::new();
        let result = analyzer.analyze(b"");
        assert!(result.is_err());
    }
    
    #[test]
    fn test_analyze_simple_data() {
        let analyzer = PatternAnalyzer::new();
        let data = b"AAAABBBBAAAABBBB"; // Clear repeating pattern
        let result = analyzer.analyze(data);
        assert!(result.is_ok());
        
        let analysis = result.unwrap();
        assert!(analysis.compression_potential > 0.0);
    }
    
    #[test]
    fn test_analyze_no_patterns() {
        let analyzer = PatternAnalyzer::new();
        let data = b"ABCDEFGHIJK"; // No repeating patterns
        let result = analyzer.analyze(data);
        assert!(result.is_ok());
        
        let analysis = result.unwrap();
        assert_eq!(analysis.compression_potential, 0.0);
    }
    
    #[test]
    fn test_pattern_coverage() {
        let analyzer = PatternAnalyzer::new();
        let data = b"TESTTEST"; // 50% pattern coverage
        let (patterns, coverage) = analyzer.find_patterns_with_coverage(data, 4);
        
        assert!(!patterns.is_empty());
        assert!(coverage > 0);
    }
    
    #[test]
    fn test_codec_recommendation() {
        let analyzer = PatternAnalyzer::new();
        
        // High compression potential
        let high_analysis = PatternAnalysis {
            pattern_lengths: vec![100, 200],
            pattern_frequencies: vec![0.8, 0.7],
            entropy_reduction: 2.0,
            compression_potential: 0.8,
        };
        assert_eq!(analyzer.recommend_codec(&high_analysis), crate::CodecType::Pattern251);
        
        // Medium compression potential
        let med_analysis = PatternAnalysis {
            pattern_lengths: vec![50],
            pattern_frequencies: vec![0.5],
            entropy_reduction: 1.0,
            compression_potential: 0.5,
        };
        assert_eq!(analyzer.recommend_codec(&med_analysis), crate::CodecType::Hierarchical);
        
        // Low compression potential
        let low_analysis = PatternAnalysis {
            pattern_lengths: vec![10],
            pattern_frequencies: vec![0.2],
            entropy_reduction: 0.5,
            compression_potential: 0.2,
        };
        assert_eq!(analyzer.recommend_codec(&low_analysis), crate::CodecType::ZSTD);
    }
    
    #[test]
    fn test_enhanced_analysis() {
        let analyzer = PatternAnalyzer::new();
        let data = b"AAAABBBBAAAABBBBCCCCDDDDCCCCDDDD";
        let enhanced = analyzer.analyze_enhanced(data).unwrap();
        
        assert!(enhanced.compression_potential > 0.0);
        assert!(enhanced.pattern_complexity >= 0.0);
        assert!(enhanced.compression_ratio_estimate > 0.0);
        assert!(enhanced.processing_time > Duration::from_nanos(0));
    }
    
    #[test]
    fn test_adaptive_threshold() {
        let analyzer = PatternAnalyzer::new().with_adaptive_threshold();
        let data = b"RANDOMDATAWITHNOPATTERNS";
        let result = analyzer.analyze(data);
        assert!(result.is_ok());
    }
    
    #[test]
    fn test_compression_strategy() {
        let analyzer = PatternAnalyzer::new();
        
        // High repetition data
        let analysis = PatternAnalysis {
            pattern_lengths: vec![100, 200],
            pattern_frequencies: vec![0.8, 0.7],
            entropy_reduction: 2.0,
            compression_potential: 0.8,
        };
        
        let strategy = analyzer.determine_strategy(&analysis);
        match strategy {
            CompressionStrategy::DictionaryBased { .. } => (),
            _ => panic!("Expected DictionaryBased strategy"),
        }
    }
    
    #[test]
    fn test_metrics() {
        let analyzer = PatternAnalyzer::new();
        let data = b"TESTTEST";
        let (analysis, metrics) = analyzer.analyze_with_metrics(data).unwrap();
        
        assert_eq!(metrics.bytes_processed, data.len());
        assert!(metrics.processing_time > Duration::from_nanos(0));
    }
    
    #[test]
    fn test_pattern_analysis_ext() {
        let analysis = PatternAnalysis {
            pattern_lengths: vec![150, 200],
            pattern_frequencies: vec![0.8, 0.7],
            entropy_reduction: 2.0,
            compression_potential: 0.8,
        };
        
        assert!(analysis.has_repeating_long_patterns());
        assert!(!analysis.has_high_entropy());
    }
}
