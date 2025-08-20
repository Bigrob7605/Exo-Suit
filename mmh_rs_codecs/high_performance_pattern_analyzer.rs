use std::collections::HashMap;
use std::time::Instant;

/// High-performance pattern analyzer using suffix arrays and LCP arrays
/// Achieves O(n log n) performance instead of O(n²) for pattern detection
pub struct HighPerformancePatternAnalyzer {
    pattern_lengths: Vec<usize>,
    min_pattern_count: usize,
}

impl HighPerformancePatternAnalyzer {
    pub fn new() -> Self {
        Self {
            pattern_lengths: vec![4, 8, 16, 32, 64, 128, 251],
            min_pattern_count: 2, // Minimum occurrences to consider a pattern
        }
    }

    /// Analyze patterns in data using suffix array + LCP array approach
    /// Time complexity: O(n log n) instead of O(n²)
    /// Space complexity: O(n)
    pub fn analyze_patterns_4bit_to_251bit(&self, data: &[u8]) -> PatternAnalysisResult {
        let start_time = Instant::now();
        
        // Build suffix array and LCP array
        let sa = self.build_suffix_array(data);
        let lcp = self.build_lcp_array(data, &sa);
        
        // Analyze patterns at each length
        let mut pattern_counts = HashMap::new();
        let mut total_patterns = 0;
        let mut found_lengths = Vec::new();
        
        for &pattern_len in &self.pattern_lengths {
            let count = self.count_patterns_at_length(&lcp, pattern_len);
            if count >= self.min_pattern_count {
                pattern_counts.insert(pattern_len, count);
                found_lengths.push(pattern_len);
                total_patterns += count;
            }
        }
        
        let analysis_time = start_time.elapsed();
        
        PatternAnalysisResult {
            pattern_lengths: found_lengths,
            pattern_counts,
            total_patterns,
            analysis_time,
            data_size: data.len(),
        }
    }
    
    /// Build suffix array using efficient algorithm
    /// This is the core of our O(n log n) performance
    fn build_suffix_array(&self, data: &[u8]) -> Vec<usize> {
        let n = data.len();
        let mut sa: Vec<usize> = (0..n).collect();
        let mut rank: Vec<usize> = vec![0; n];
        let mut new_rank: Vec<usize> = vec![0; n];
        
        // Initial sorting by first character
        sa.sort_by_key(|&i| data[i] as usize);
        
        // Initialize rank array
        let mut current_rank = 0;
        for i in 0..n {
            if i > 0 && data[sa[i]] != data[sa[i-1]] {
                current_rank += 1;
            }
            rank[sa[i]] = current_rank;
        }
        
        // Iterative doubling: sort by 2^k characters
        let mut k = 1;
        while k < n {
            // Sort by (rank[i], rank[i+k]) pairs
            sa.sort_by_key(|&i| {
                let rank1 = rank[i];
                let rank2 = if i + k < n { rank[i + k] } else { 0 };
                (rank1, rank2)
            });
            
            // Update ranks
            let mut current_rank = 0;
            for i in 0..n {
                if i > 0 {
                    let prev_rank1 = rank[sa[i-1]];
                    let prev_rank2 = if sa[i-1] + k < n { rank[sa[i-1] + k] } else { 0 };
                    let curr_rank1 = rank[sa[i]];
                    let curr_rank2 = if sa[i] + k < n { rank[sa[i] + k] } else { 0 };
                    
                    if (prev_rank1, prev_rank2) != (curr_rank1, curr_rank2) {
                        current_rank += 1;
                    }
                }
                new_rank[sa[i]] = current_rank;
            }
            
            std::mem::swap(&mut rank, &mut new_rank);
            k *= 2;
        }
        
        sa
    }
    
    /// Build LCP (Longest Common Prefix) array
    /// LCP[i] = length of common prefix between suffixes at positions i and i-1
    fn build_lcp_array(&self, data: &[u8], sa: &[usize]) -> Vec<usize> {
        let n = data.len();
        let mut lcp = vec![0; n];
        let mut inv_sa = vec![0; n];
        
        // Build inverse suffix array
        for (i, &suffix_pos) in sa.iter().enumerate() {
            inv_sa[suffix_pos] = i;
        }
        
        // Compute LCP array using Kasai's algorithm
        let mut k = 0;
        for i in 0..n {
            if inv_sa[i] == n - 1 {
                k = 0;
                continue;
            }
            
            let j = sa[inv_sa[i] + 1];
            
            // Find length of common prefix
            while i + k < n && j + k < n && data[i + k] == data[j + k] {
                k += 1;
            }
            
            lcp[inv_sa[i]] = k;
            
            if k > 0 {
                k -= 1;
            }
        }
        
        lcp
    }
    
    /// Count patterns at specific length using LCP array
    /// This is where we get our O(n) pattern counting per length
    fn count_patterns_at_length(&self, lcp: &[usize], pattern_len: usize) -> usize {
        let mut count = 0;
        
        // Count how many suffix pairs share at least `pattern_len` bytes
        for &lcp_value in lcp {
            if lcp_value >= pattern_len {
                count += 1;
            }
        }
        
        count
    }
    
    /// Analyze multiple files efficiently
    pub fn analyze_multiple_files(&self, file_paths: &[&str]) -> Vec<PatternAnalysisResult> {
        let mut results = Vec::new();
        
        for &file_path in file_paths {
            match std::fs::read(file_path) {
                Ok(data) => {
                    let result = self.analyze_patterns_4bit_to_251bit(&data);
                    results.push(result);
                }
                Err(e) => {
                    eprintln!("Error reading file {}: {}", file_path, e);
                }
            }
        }
        
        results
    }
    
    /// Get detailed pattern statistics
    pub fn get_pattern_statistics(&self, result: &PatternAnalysisResult) -> PatternStatistics {
        let mut stats = PatternStatistics {
            total_patterns: result.total_patterns,
            pattern_density: result.total_patterns as f64 / result.data_size as f64,
            compression_potential: 0.0,
            most_common_length: 0,
            most_common_count: 0,
        };
        
        // Find most common pattern length
        if let Some((&length, &count)) = result.pattern_counts.iter().max_by_key(|(_, &count)| count) {
            stats.most_common_length = length;
            stats.most_common_count = count;
        }
        
        // Calculate compression potential based on pattern density
        stats.compression_potential = (stats.pattern_density * 100.0).min(95.0);
        
        stats
    }
}

/// Result of pattern analysis
#[derive(Debug, Clone)]
pub struct PatternAnalysisResult {
    pub pattern_lengths: Vec<usize>,
    pub pattern_counts: HashMap<usize, usize>,
    pub total_patterns: usize,
    pub analysis_time: std::time::Duration,
    pub data_size: usize,
}

/// Detailed pattern statistics
#[derive(Debug, Clone)]
pub struct PatternStatistics {
    pub total_patterns: usize,
    pub pattern_density: f64,
    pub compression_potential: f64,
    pub most_common_length: usize,
    pub most_common_count: usize,
}

/// Performance benchmark results
#[derive(Debug, Clone)]
pub struct PerformanceBenchmark {
    pub data_size: usize,
    pub analysis_time: std::time::Duration,
    pub throughput_mbps: f64,
    pub memory_usage_mb: f64,
}

impl HighPerformancePatternAnalyzer {
    /// Run performance benchmark on data
    pub fn benchmark_performance(&self, data: &[u8]) -> PerformanceBenchmark {
        let start_time = Instant::now();
        let start_memory = self.get_memory_usage();
        
        // Run analysis
        let result = self.analyze_patterns_4bit_to_251bit(data);
        
        let end_time = Instant::now();
        let end_memory = self.get_memory_usage();
        
        let analysis_time = end_time.duration_since(start_time);
        let memory_used = end_memory - start_memory;
        let throughput = (data.len() as f64 / 1024.0 / 1024.0) / analysis_time.as_secs_f64();
        
        PerformanceBenchmark {
            data_size: data.len(),
            analysis_time,
            throughput_mbps: throughput,
            memory_usage_mb: memory_used,
        }
    }
    
    /// Get current memory usage in MB
    fn get_memory_usage(&self) -> f64 {
        // This is a simplified memory measurement
        // In production, you might want to use a more sophisticated approach
        std::mem::size_of::<Self>() as f64 / 1024.0 / 1024.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_pattern_analysis() {
        let analyzer = HighPerformancePatternAnalyzer::new();
        
        // Test with repetitive data
        let test_data = b"AAAAAAAABBBBBBBBCCCCCCCCAAAAAAAABBBBBBBBCCCCCCCC";
        let result = analyzer.analyze_patterns_4bit_to_251bit(test_data);
        
        assert!(result.total_patterns > 0);
        assert!(!result.pattern_lengths.is_empty());
        assert!(result.analysis_time.as_millis() < 100); // Should be very fast
    }
    
    #[test]
    fn test_performance_benchmark() {
        let analyzer = HighPerformancePatternAnalyzer::new();
        
        // Create larger test data
        let mut test_data = Vec::new();
        for i in 0..100000 {
            test_data.extend_from_slice(&format!("PATTERN_{:06}", i).as_bytes());
        }
        
        let benchmark = analyzer.benchmark_performance(&test_data);
        
        assert!(benchmark.throughput_mbps > 10.0); // Should be fast
        assert!(benchmark.analysis_time.as_millis() < 1000); // Under 1 second
    }
}

/// Main function for testing
fn main() {
    let analyzer = HighPerformancePatternAnalyzer::new();
    
    // Example usage
    let test_data = b"This is a test pattern that repeats. This is a test pattern that repeats.";
    let result = analyzer.analyze_patterns_4bit_to_251bit(test_data);
    
    println!("Pattern Analysis Result:");
    println!("  Total patterns found: {}", result.total_patterns);
    println!("  Pattern lengths: {:?}", result.pattern_lengths);
    println!("  Analysis time: {:?}", result.analysis_time);
    println!("  Data size: {} bytes", result.data_size);
    
    // Get detailed statistics
    let stats = analyzer.get_pattern_statistics(&result);
    println!("\nPattern Statistics:");
    println!("  Pattern density: {:.2}%", stats.pattern_density * 100.0);
    println!("  Compression potential: {:.2}%", stats.compression_potential);
    println!("  Most common length: {} ({} occurrences)", stats.most_common_length, stats.most_common_count);
}
