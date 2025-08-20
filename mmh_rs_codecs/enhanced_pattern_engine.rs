// Enhanced Pattern Recognition Engine for MMH-RS Universal Compression Champion
// Phase 2 ULTRA: Advanced Pattern Recognition with ML-inspired techniques

use std::collections::HashMap;
use std::fs::File;
use std::io::Read;
use std::path::Path;
use std::time::Instant;

/// Advanced pattern types with ML-inspired classification
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum PatternType {
    // Structural patterns
    RepetitiveSequences,
    NullPadding,
    StructuredData,
    HeaderTrailer,
    
    // Content patterns
    TextPatterns,
    BinaryPatterns,
    CompressedData,
    RandomData,
    
    // Algorithm-specific patterns
    LZ77Patterns,
    RLEPatterns,
    DictionaryPatterns,
    DeltaPatterns,
    
    // NEW: Advanced ML-inspired patterns
    PeriodicPatterns,       // Patterns that repeat at regular intervals
    GradientPatterns,       // Gradual changes in data
    ClusterPatterns,        // Data that clusters around certain values
    MarkovPatterns,         // Patterns following Markov chain properties
}

/// Enhanced pattern information with confidence scoring
#[derive(Debug, Clone)]
pub struct PatternInfo {
    pub pattern_type: PatternType,
    pub frequency: usize,
    pub size: usize,
    pub compression_ratio: f64,
    pub confidence: f64,
    pub locations: Vec<usize>,
    pub metadata: HashMap<String, String>,
    
    // NEW: Advanced metrics
    pub entropy: f64,              // Local entropy of pattern
    pub predictability: f64,       // How predictable is this pattern
    pub spatial_distribution: f64, // How evenly distributed across file
    pub compression_gain: f64,     // Actual bytes saved estimate
    pub algorithm_fitness: HashMap<String, f64>, // Algorithm compatibility scores
}

/// Multi-algorithm compression strategy
#[derive(Debug, Clone)]
pub struct CompressionStrategy {
    pub primary_algorithm: String,
    pub secondary_algorithm: Option<String>,
    pub preprocessing_steps: Vec<String>,
    pub estimated_ratio: f64,
    pub confidence: f64,
    pub reasoning: Vec<String>,
    pub parameters: HashMap<String, String>,
    
    // NEW: Advanced strategy features
    pub multi_pass_enabled: bool,
    pub adaptive_parameters: HashMap<String, (f64, f64)>, // (min, max) ranges
    pub performance_prediction: PerformancePrediction,
}

/// Performance prediction for compression
#[derive(Debug, Clone)]
pub struct PerformancePrediction {
    pub compression_time_ms: u64,
    pub decompression_time_ms: u64,
    pub memory_usage_mb: f64,
    pub cpu_intensity: f64, // 0.0 to 1.0
}

/// Enhanced analysis result with ML insights
#[derive(Debug, Clone)]
pub struct PatternAnalysisResult {
    pub file_path: String,
    pub file_size: u64,
    pub patterns_found: Vec<PatternInfo>,
    pub recommended_strategy: CompressionStrategy,
    pub analysis_time: u128,
    pub memory_used: usize,
    
    // NEW: Advanced analysis metrics
    pub file_entropy: f64,
    pub pattern_coverage: f64,      // Percentage of file covered by patterns
    pub complexity_score: f64,      // Overall file complexity (0-1)
    pub frequency_spectrum: Vec<(u8, usize)>, // Byte frequency analysis
}

/// Enhanced configuration with ML parameters
#[derive(Debug, Clone)]
pub struct PatternRecognitionConfig {
    pub min_pattern_size: usize,
    pub max_pattern_size: usize,
    pub min_frequency: usize,
    pub confidence_threshold: f64,
    pub max_patterns_per_file: usize,
    pub memory_limit_mb: usize,
    pub enable_deep_analysis: bool,
    
    // NEW: Advanced configuration
    pub block_size: usize,          // For block-based analysis
    pub overlap_factor: f64,        // Block overlap for pattern detection
    pub entropy_window_size: usize, // Window for entropy calculation
    pub similarity_threshold: f64,  // Minimum similarity for clustering
    pub adaptive_thresholds: bool,  // Dynamically adjust thresholds
    pub ml_pattern_detection: bool, // Enable ML-inspired techniques
}

impl Default for PatternRecognitionConfig {
    fn default() -> Self {
        Self {
            min_pattern_size: 4,
            max_pattern_size: 128,
            min_frequency: 2,
            confidence_threshold: 0.6,
            max_patterns_per_file: 10,
            memory_limit_mb: 50,
            enable_deep_analysis: true,
            
            // Advanced defaults - optimized for speed
            block_size: 1024,
            overlap_factor: 0.1,
            entropy_window_size: 64,
            similarity_threshold: 0.7,
            adaptive_thresholds: false, // Disabled for speed
            ml_pattern_detection: true,
        }
    }
}

/// Enhanced pattern recognition engine with ML capabilities
pub struct PatternRecognitionEngine {
    config: PatternRecognitionConfig,
    pattern_database: HashMap<PatternType, PatternTemplate>,
}

#[derive(Debug, Clone)]
struct PatternTemplate {
    signature: Vec<u8>,
    min_size: usize,
    max_size: usize,
    expected_compression: f64,
    algorithm_suggestions: Vec<String>,
    
    // NEW: Enhanced template features
    entropy_range: (f64, f64),
    complexity_weight: f64,
    detection_function: String, // Name of detection function to use
}

impl PatternRecognitionEngine {
    pub fn new(config: PatternRecognitionConfig) -> Self {
        let mut engine = Self {
            config,
            pattern_database: HashMap::new(),
        };
        engine.initialize_enhanced_pattern_database();
        engine
    }
    
    fn initialize_enhanced_pattern_database(&mut self) {
        // Enhanced pattern templates with ML characteristics
        
        self.pattern_database.insert(PatternType::PeriodicPatterns, PatternTemplate {
            signature: vec![],
            min_size: 8,
            max_size: 64,
            expected_compression: 0.85,
            algorithm_suggestions: vec!["LZ77".to_string(), "Custom-Periodic".to_string()],
            entropy_range: (2.0, 6.0),
            complexity_weight: 0.8,
            detection_function: "detect_periodic_patterns".to_string(),
        });
        
        self.pattern_database.insert(PatternType::ClusterPatterns, PatternTemplate {
            signature: vec![],
            min_size: 16,
            max_size: 128,
            expected_compression: 0.70,
            algorithm_suggestions: vec!["Dictionary".to_string(), "Huffman".to_string()],
            entropy_range: (1.0, 5.0),
            complexity_weight: 0.7,
            detection_function: "detect_cluster_patterns".to_string(),
        });
        
        // Add existing patterns with enhancements...
        self.pattern_database.insert(PatternType::RepetitiveSequences, PatternTemplate {
            signature: vec![],
            min_size: 4,
            max_size: 32,
            expected_compression: 0.8,
            algorithm_suggestions: vec!["LZ77".to_string(), "RLE".to_string()],
            entropy_range: (0.0, 4.0),
            complexity_weight: 0.9,
            detection_function: "detect_repetitive_sequences".to_string(),
        });
        
        self.pattern_database.insert(PatternType::NullPadding, PatternTemplate {
            signature: vec![0x00],
            min_size: 8,
            max_size: 1024,
            expected_compression: 0.95,
            algorithm_suggestions: vec!["RLE".to_string(), "Null-Compressor".to_string()],
            entropy_range: (0.0, 0.1),
            complexity_weight: 1.0,
            detection_function: "detect_null_padding".to_string(),
        });
    }
    
    /// Enhanced file analysis with optimized ML techniques
    pub fn analyze_file(&self, file_path: &Path) -> Result<PatternAnalysisResult, Box<dyn std::error::Error>> {
        let start_time = Instant::now();
        let mut file = File::open(file_path)?;
        let metadata = file.metadata()?;
        let file_size = metadata.len();
        
        // Limit file size for speed (process max 1MB for large files)
        let max_analysis_size = 1024 * 1024; // 1MB
        let analysis_size = (file_size as usize).min(max_analysis_size);
        
        let mut buffer = vec![0u8; analysis_size];
        file.read_exact(&mut buffer)?;
        let memory_used = buffer.len();
        
        // Quick global metrics
        let file_entropy = self.calculate_entropy(&buffer);
        let frequency_spectrum = self.generate_frequency_spectrum(&buffer);
        
        // Fast pattern recognition
        let patterns = self.fast_pattern_recognition(&buffer)?;
        
        // Calculate pattern coverage
        let pattern_coverage = self.calculate_pattern_coverage(&patterns, file_size);
        
        // Calculate complexity score
        let complexity_score = self.calculate_complexity_score(&buffer, &patterns);
        
        // Generate enhanced compression strategy
        let strategy = self.generate_enhanced_compression_strategy(&patterns, &buffer, file_size)?;
        
        let analysis_time = start_time.elapsed().as_millis();
        
        Ok(PatternAnalysisResult {
            file_path: file_path.to_string_lossy().to_string(),
            file_size,
            patterns_found: patterns,
            recommended_strategy: strategy,
            analysis_time,
            memory_used,
            file_entropy,
            pattern_coverage,
            complexity_score,
            frequency_spectrum,
        })
    }
    
    /// Fast pattern recognition optimized for speed
    fn fast_pattern_recognition(&self, data: &[u8]) -> Result<Vec<PatternInfo>, Box<dyn std::error::Error>> {
        let mut patterns = Vec::new();
        
        // Quick null padding check (fastest)
        if let Some(null_padding) = self.detect_fast_null_padding(data)? {
            patterns.push(null_padding);
        }
        
        // Quick repetitive sequences (limited scope for speed)
        if let Some(repetitive) = self.detect_fast_repetitive_sequences(data)? {
            patterns.push(repetitive);
        }
        
        // Quick periodic patterns (limited range)
        if let Some(periodic) = self.detect_fast_periodic_patterns(data)? {
            patterns.push(periodic);
        }
        
        // Quick cluster analysis
        if let Some(cluster) = self.detect_fast_cluster_patterns(data)? {
            patterns.push(cluster);
        }
        
        // Limit patterns for performance
        if patterns.len() > self.config.max_patterns_per_file {
            patterns.truncate(self.config.max_patterns_per_file);
        }
        
        Ok(patterns)
    }
    
    /// Fast null padding detection
    fn detect_fast_null_padding(&self, data: &[u8]) -> Result<Option<PatternInfo>, Box<dyn std::error::Error>> {
        let null_count = data.iter().filter(|&&b| b == 0x00).count();
        
        if null_count < self.config.min_pattern_size {
            return Ok(None);
        }
        
        let null_ratio = null_count as f64 / data.len() as f64;
        
        if null_ratio > 0.1 {
            let compression_ratio = 0.95;
            let confidence = null_ratio.min(0.9);
            
            let mut metadata = HashMap::new();
            metadata.insert("null_ratio".to_string(), format!("{:.3}", null_ratio));
            
            let mut algorithm_fitness = HashMap::new();
            algorithm_fitness.insert("RLE".to_string(), confidence);
            algorithm_fitness.insert("LZ77".to_string(), confidence * 0.8);
            
            Ok(Some(PatternInfo {
                pattern_type: PatternType::NullPadding,
                frequency: 1,
                size: null_count,
                compression_ratio,
                confidence,
                locations: vec![0],
                metadata,
                entropy: 0.0,
                predictability: 1.0,
                spatial_distribution: 0.8,
                compression_gain: null_count as f64 * compression_ratio,
                algorithm_fitness,
            }))
        } else {
            Ok(None)
        }
    }
    
    /// Fast repetitive sequence detection (limited scope)
    fn detect_fast_repetitive_sequences(&self, data: &[u8]) -> Result<Option<PatternInfo>, Box<dyn std::error::Error>> {
        if data.len() < 16 {
            return Ok(None);
        }
        
        let mut best_pattern = None;
        let mut best_score = 0.0;
        
        // Test only small patterns for speed (4-16 bytes)
        for size in 4..=16.min(data.len() / 4) {
            let mut pattern_counts = HashMap::new();
            
            // Sample every 4th position for speed
            for start in (0..=(data.len() - size)).step_by(4) {
                let pattern = &data[start..start + size];
                *pattern_counts.entry(pattern.to_vec()).or_insert(0) += 1;
            }
            
            for (pattern, count) in pattern_counts {
                if count >= 2 {
                    let score = (count as f64) * (size as f64).ln();
                    if score > best_score {
                        best_score = score;
                        best_pattern = Some((pattern, count));
                    }
                }
            }
        }
        
        if let Some((pattern, frequency)) = best_pattern {
            let entropy = self.calculate_entropy(&pattern);
            let compression_ratio = 0.8 - (entropy / 8.0) * 0.3;
            let confidence = (best_score / 20.0).min(0.9);
            
            let mut metadata = HashMap::new();
            metadata.insert("pattern_entropy".to_string(), format!("{:.3}", entropy));
            
            let mut algorithm_fitness = HashMap::new();
            algorithm_fitness.insert("LZ77".to_string(), confidence);
            algorithm_fitness.insert("RLE".to_string(), if pattern.len() <= 4 { confidence } else { confidence * 0.5 });
            
            Ok(Some(PatternInfo {
                pattern_type: PatternType::RepetitiveSequences,
                frequency,
                size: pattern.len(),
                compression_ratio,
                confidence,
                locations: vec![0],
                metadata,
                entropy,
                predictability: confidence,
                spatial_distribution: 0.7,
                compression_gain: (pattern.len() * frequency) as f64 * compression_ratio,
                algorithm_fitness,
            }))
        } else {
            Ok(None)
        }
    }
    
    /// Fast periodic pattern detection
    fn detect_fast_periodic_patterns(&self, data: &[u8]) -> Result<Option<PatternInfo>, Box<dyn std::error::Error>> {
        if data.len() < 32 {
            return Ok(None);
        }
        
        let mut best_period = 0;
        let mut best_correlation = 0.0;
        
        // Test only small periods for speed (4-32)
        for period in 4..=32.min(data.len() / 4) {
            let mut matches = 0;
            let mut total = 0;
            
            // Sample every 8th position for speed
            for i in (0..(data.len() - period)).step_by(8) {
                if i + period < data.len() {
                    if data[i] == data[i + period] {
                        matches += 1;
                    }
                    total += 1;
                }
            }
            
            if total > 0 {
                let correlation = matches as f64 / total as f64;
                if correlation > best_correlation && correlation > 0.5 {
                    best_correlation = correlation;
                    best_period = period;
                }
            }
        }
        
        if best_period > 0 && best_correlation > 0.5 {
            let compression_ratio = 0.85 * best_correlation;
            
            let mut metadata = HashMap::new();
            metadata.insert("period".to_string(), best_period.to_string());
            metadata.insert("correlation".to_string(), format!("{:.3}", best_correlation));
            
            let mut algorithm_fitness = HashMap::new();
            algorithm_fitness.insert("LZ77".to_string(), best_correlation);
            algorithm_fitness.insert("Custom-Periodic".to_string(), best_correlation * 1.1);
            
            Ok(Some(PatternInfo {
                pattern_type: PatternType::PeriodicPatterns,
                frequency: data.len() / best_period,
                size: best_period,
                compression_ratio,
                confidence: best_correlation,
                locations: vec![0],
                metadata,
                entropy: self.calculate_entropy(&data[0..best_period.min(data.len())]),
                predictability: best_correlation,
                spatial_distribution: 1.0,
                compression_gain: (data.len() as f64 * compression_ratio),
                algorithm_fitness,
            }))
        } else {
            Ok(None)
        }
    }
    
    /// Fast cluster pattern detection
    fn detect_fast_cluster_patterns(&self, data: &[u8]) -> Result<Option<PatternInfo>, Box<dyn std::error::Error>> {
        let mut value_counts = [0usize; 256];
        
        for &byte in data {
            value_counts[byte as usize] += 1;
        }
        
        // Find top values
        let threshold = data.len() / 20; // 5% threshold
        let dominant_count = value_counts.iter().filter(|&&count| count > threshold).count();
        
        if dominant_count >= 2 && dominant_count <= 16 {
            let total_dominant: usize = value_counts.iter()
                .filter(|&&count| count > threshold)
                .sum();
            
            let cluster_ratio = total_dominant as f64 / data.len() as f64;
            
            if cluster_ratio > 0.5 {
                let compression_ratio = 0.7 * cluster_ratio;
                
                let mut metadata = HashMap::new();
                metadata.insert("cluster_count".to_string(), dominant_count.to_string());
                metadata.insert("cluster_ratio".to_string(), format!("{:.3}", cluster_ratio));
                
                let mut algorithm_fitness = HashMap::new();
                algorithm_fitness.insert("Dictionary".to_string(), cluster_ratio);
                algorithm_fitness.insert("Huffman".to_string(), cluster_ratio * 0.9);
                
                Ok(Some(PatternInfo {
                    pattern_type: PatternType::ClusterPatterns,
                    frequency: dominant_count,
                    size: total_dominant / dominant_count,
                    compression_ratio,
                    confidence: cluster_ratio,
                    locations: vec![0],
                    metadata,
                    entropy: self.calculate_entropy(data),
                    predictability: cluster_ratio,
                    spatial_distribution: 0.8,
                    compression_gain: (data.len() as f64 * compression_ratio),
                    algorithm_fitness,
                }))
            } else {
                Ok(None)
            }
        } else {
            Ok(None)
        }
    }
    
    /// Fast entropy calculation
    fn calculate_entropy(&self, data: &[u8]) -> f64 {
        if data.is_empty() {
            return 0.0;
        }
        
        let mut counts = [0usize; 256];
        for &byte in data {
            counts[byte as usize] += 1;
        }
        
        let len = data.len() as f64;
        let mut entropy = 0.0;
        
        for &count in &counts {
            if count > 0 {
                let p = count as f64 / len;
                entropy -= p * p.log2();
            }
        }
        
        entropy
    }
    
    /// Generate frequency spectrum
    fn generate_frequency_spectrum(&self, data: &[u8]) -> Vec<(u8, usize)> {
        let mut counts = [0usize; 256];
        for &byte in data {
            counts[byte as usize] += 1;
        }
        
        let mut spectrum: Vec<(u8, usize)> = (0..=255u8)
            .map(|i| (i, counts[i as usize]))
            .filter(|(_, count)| *count > 0)
            .collect();
        
        spectrum.sort_by(|a, b| b.1.cmp(&a.1));
        spectrum.truncate(20); // Top 20 most frequent bytes
        spectrum
    }
    
    /// Calculate pattern coverage
    fn calculate_pattern_coverage(&self, patterns: &[PatternInfo], file_size: u64) -> f64 {
        if patterns.is_empty() {
            return 0.0;
        }
        
        let total_pattern_bytes: f64 = patterns.iter()
            .map(|p| (p.size * p.frequency) as f64)
            .sum();
        
        (total_pattern_bytes / file_size as f64).min(1.0)
    }
    
    /// Calculate complexity score
    fn calculate_complexity_score(&self, data: &[u8], patterns: &[PatternInfo]) -> f64 {
        let entropy = self.calculate_entropy(data);
        let pattern_factor = if patterns.is_empty() { 1.0 } else { 1.0 / patterns.len() as f64 };
        
        (entropy / 8.0 + pattern_factor) / 2.0
    }
    
    /// Generate enhanced compression strategy
    fn generate_enhanced_compression_strategy(
        &self,
        patterns: &[PatternInfo],
        data: &[u8],
        file_size: u64,
    ) -> Result<CompressionStrategy, Box<dyn std::error::Error>> {
        
        if patterns.is_empty() {
            return Ok(CompressionStrategy {
                primary_algorithm: "LZ77".to_string(),
                secondary_algorithm: Some("Huffman".to_string()),
                preprocessing_steps: vec![],
                estimated_ratio: 0.5,
                confidence: 0.3,
                reasoning: vec!["No specific patterns detected - using generic compression".to_string()],
                parameters: HashMap::new(),
                multi_pass_enabled: false,
                adaptive_parameters: HashMap::new(),
                performance_prediction: PerformancePrediction {
                    compression_time_ms: (file_size / 1024 / 1024) * 100, // ~100ms per MB
                    decompression_time_ms: (file_size / 1024 / 1024) * 50,  // ~50ms per MB
                    memory_usage_mb: (file_size as f64 / 1024.0 / 1024.0 * 1.5), // 1.5x file size
                    cpu_intensity: 0.7,
                },
            });
        }
        
        // Find the best pattern
        let best_pattern = patterns.iter()
            .max_by(|a, b| (a.compression_ratio * a.confidence).partial_cmp(&(b.compression_ratio * b.confidence)).unwrap())
            .unwrap();
        
        // Determine primary algorithm
        let primary_algorithm = match best_pattern.pattern_type {
            PatternType::NullPadding => "RLE",
            PatternType::RepetitiveSequences => "LZ77",
            PatternType::PeriodicPatterns => "LZ77",
            PatternType::ClusterPatterns => "Dictionary",
            _ => "LZ77",
        };
        
        // Determine secondary algorithm
        let secondary_algorithm = match primary_algorithm {
            "RLE" => Some("LZ77".to_string()),
            "LZ77" => Some("Huffman".to_string()),
            "Dictionary" => Some("Huffman".to_string()),
            _ => None,
        };
        
        // Generate reasoning
        let mut reasoning = Vec::new();
        reasoning.push(format!("Detected {:?} pattern with {:.1}% confidence", 
            best_pattern.pattern_type, best_pattern.confidence * 100.0));
        reasoning.push(format!("Pattern covers {:.1}% of file with {:.1}% compression potential", 
            (best_pattern.size * best_pattern.frequency) as f64 / file_size as f64 * 100.0,
            best_pattern.compression_ratio * 100.0));
        
        // Set parameters
        let mut parameters = HashMap::new();
        parameters.insert("window_size".to_string(), "32768".to_string());
        parameters.insert("min_match_length".to_string(), "3".to_string());
        
        // Performance prediction
        let file_mb = file_size as f64 / 1024.0 / 1024.0;
        let complexity_factor = self.calculate_entropy(data) / 8.0;
        
        let performance_prediction = PerformancePrediction {
            compression_time_ms: (file_mb * 150.0 * complexity_factor) as u64,
            decompression_time_ms: (file_mb * 75.0) as u64,
            memory_usage_mb: file_mb * 2.0,
            cpu_intensity: complexity_factor,
        };
        
        Ok(CompressionStrategy {
            primary_algorithm: primary_algorithm.to_string(),
            secondary_algorithm,
            preprocessing_steps: vec![],
            estimated_ratio: best_pattern.compression_ratio,
            confidence: best_pattern.confidence,
            reasoning,
            parameters,
            multi_pass_enabled: patterns.len() > 2,
            adaptive_parameters: HashMap::new(),
            performance_prediction,
        })
    }
}

/// Display enhanced pattern analysis results
pub fn display_enhanced_pattern_analysis(result: &PatternAnalysisResult) {
    println!("\n🔍 Enhanced Pattern Analysis: {}", 
        std::path::Path::new(&result.file_path).file_name().unwrap().to_string_lossy());
    println!("📏 File Size: {:.2} MB", result.file_size as f64 / (1024.0 * 1024.0));
    println!("⏱️  Analysis Time: {} ms", result.analysis_time);
    println!("🧠 Memory Used: {:.2} MB", result.memory_used as f64 / (1024.0 * 1024.0));
    println!("📊 File Entropy: {:.2} bits", result.file_entropy);
    println!("🎯 Pattern Coverage: {:.1}%", result.pattern_coverage * 100.0);
    println!("🧮 Complexity Score: {:.2}/1.0", result.complexity_score);
    
    if !result.patterns_found.is_empty() {
        println!("\n🔍 Patterns Found ({}):", result.patterns_found.len());
        for (i, pattern) in result.patterns_found.iter().enumerate() {
            println!("  {}. {:?}", i + 1, pattern.pattern_type);
            println!("     • Size: {} bytes, Frequency: {}, Entropy: {:.2}", 
                pattern.size, pattern.frequency, pattern.entropy);
            println!("     • Compression: {:.1}%, Confidence: {:.1}%, Gain: {:.0} bytes", 
                pattern.compression_ratio * 100.0, pattern.confidence * 100.0, pattern.compression_gain);
            
            if !pattern.algorithm_fitness.is_empty() {
                println!("     • Algorithm Fitness:");
                for (alg, fitness) in &pattern.algorithm_fitness {
                    println!("       - {}: {:.1}%", alg, fitness * 100.0);
                }
            }
        }
    } else {
        println!("\n🔍 No significant patterns detected");
    }
    
    println!("\n🎯 Recommended Strategy:");
    println!("  Primary: {} (confidence: {:.1}%)", 
        result.recommended_strategy.primary_algorithm, 
        result.recommended_strategy.confidence * 100.0);
    if let Some(ref secondary) = result.recommended_strategy.secondary_algorithm {
        println!("  Secondary: {}", secondary);
    }
    println!("  Estimated Compression: {:.1}%", 
        result.recommended_strategy.estimated_ratio * 100.0);
    
    println!("  Performance Prediction:");
    println!("    • Compression Time: {} ms", result.recommended_strategy.performance_prediction.compression_time_ms);
    println!("    • Memory Usage: {:.1} MB", result.recommended_strategy.performance_prediction.memory_usage_mb);
    println!("    • CPU Intensity: {:.1}%", result.recommended_strategy.performance_prediction.cpu_intensity * 100.0);
    
    if !result.recommended_strategy.reasoning.is_empty() {
        println!("\n💡 Reasoning:");
        for reason in &result.recommended_strategy.reasoning {
            println!("  → {}", reason);
        }
    }
    
    if !result.frequency_spectrum.is_empty() {
        println!("\n📈 Top Byte Frequencies:");
        for (i, (byte, count)) in result.frequency_spectrum.iter().enumerate().take(5) {
            println!("  {}. 0x{:02X}: {} occurrences ({:.1}%)", 
                i + 1, byte, count, *count as f64 / result.memory_used as f64 * 100.0);
        }
    }
}

// ============================================================================
// 🚀 PHASE 3: ADVANCED PATTERN-BASED COMPRESSION FRAMEWORK
// ============================================================================

/// Phase 3: Compression result with detailed metrics
#[derive(Debug, Clone)]
pub struct CompressionResult {
    pub original_size: usize,
    pub compressed_size: usize,
    pub compression_ratio: f64,
    pub algorithm_used: String,
    pub processing_time_ms: u128,
    pub pattern_efficiency: f64,
    pub compression_gain_bytes: usize,
    pub algorithm_confidence: f64,
}

/// Phase 3: Pattern-based compressor that integrates with Phase 2 analysis
#[derive(Debug, Clone)]
pub struct PatternBasedCompressor {
    pub entropy_threshold: f64,
    pub min_pattern_confidence: f64,
    pub adaptive_strategy: bool,
    pub enable_hybrid_compression: bool,
    pub max_compression_time_ms: u128,
}

impl PatternBasedCompressor {
    pub fn new() -> Self {
        Self {
            entropy_threshold: 2.0,
            min_pattern_confidence: 0.7,
            adaptive_strategy: true,
            enable_hybrid_compression: true,
            max_compression_time_ms: 1000, // 1 second max per file
        }
    }

    /// Main compression function that uses Phase 2 pattern analysis
    pub fn compress_with_patterns(&self, data: &[u8], patterns: &[PatternInfo]) -> CompressionResult {
        let start_time = std::time::Instant::now();
        let original_size = data.len();
        
        // Select optimal algorithm based on pattern analysis
        let algorithm = self.select_optimal_algorithm(patterns);
        
        let compressed_data = match algorithm.as_str() {
            "RLE" => self.rle_compress(data, patterns),
            "LZ77" => self.lz77_compress(data, patterns),
            "Custom-Periodic" => self.periodic_compress(data, patterns),
            "Dictionary" => self.dictionary_compress(data, patterns),
            "Hybrid" => self.hybrid_compress(data, patterns),
            _ => self.adaptive_compress(data, patterns),
        };
        
        let compressed_size = compressed_data.len();
        let compression_ratio = if original_size > 0 && compressed_size <= original_size {
            (original_size - compressed_size) as f64 / original_size as f64 * 100.0
        } else if compressed_size > original_size {
            -((compressed_size - original_size) as f64 / original_size as f64 * 100.0)
        } else {
            0.0
        };
        let processing_time = start_time.elapsed().as_millis();
        let compression_gain_bytes = if compressed_size <= original_size {
            original_size.saturating_sub(compressed_size) // Use saturating_sub to prevent overflow
        } else {
            0
        };
        
        CompressionResult {
            original_size,
            compressed_size,
            compression_ratio,
            algorithm_used: algorithm.clone(),
            processing_time_ms: processing_time,
            pattern_efficiency: self.calculate_pattern_efficiency(patterns),
            compression_gain_bytes,
            algorithm_confidence: self.calculate_algorithm_confidence(patterns, &algorithm),
        }
    }

    /// Intelligent algorithm selection based on Phase 2 pattern analysis
    fn select_optimal_algorithm(&self, patterns: &[PatternInfo]) -> String {
        if patterns.is_empty() {
            return "LZ77".to_string(); // Default fallback
        }
        
        let mut algorithm_scores = HashMap::new();
        
        for pattern in patterns {
            match pattern.pattern_type {
                PatternType::NullPadding => {
                    *algorithm_scores.entry("RLE".to_string()).or_insert(0.0) += pattern.confidence * 1.2;
                }
                PatternType::RepetitiveSequences => {
                    *algorithm_scores.entry("RLE".to_string()).or_insert(0.0) += pattern.confidence * 1.1;
                    *algorithm_scores.entry("LZ77".to_string()).or_insert(0.0) += pattern.confidence * 1.0;
                }
                PatternType::PeriodicPatterns => {
                    if pattern.confidence > 0.9 {
                        *algorithm_scores.entry("Custom-Periodic".to_string()).or_insert(0.0) += pattern.confidence * 1.5;
                    }
                    *algorithm_scores.entry("LZ77".to_string()).or_insert(0.0) += pattern.confidence * 1.1;
                }
                PatternType::ClusterPatterns => {
                    *algorithm_scores.entry("Dictionary".to_string()).or_insert(0.0) += pattern.confidence * 1.3;
                    *algorithm_scores.entry("LZ77".to_string()).or_insert(0.0) += pattern.confidence * 1.0;
                }
                _ => {
                    *algorithm_scores.entry("LZ77".to_string()).or_insert(0.0) += pattern.confidence * 0.8;
                }
            }
        }
        
        // Select algorithm with highest score, default to adaptive
        algorithm_scores.iter()
            .max_by(|a, b| a.1.partial_cmp(b.1).unwrap())
            .map(|(alg, _)| alg.clone())
            .unwrap_or_else(|| "Adaptive".to_string())
    }

    /// Enhanced RLE with pattern-aware optimization
    fn rle_compress(&self, data: &[u8], patterns: &[PatternInfo]) -> Vec<u8> {
        let mut compressed = Vec::new();
        let mut i = 0;
        
        // Use null pattern information to optimize RLE
        let null_patterns: Vec<_> = patterns.iter()
            .filter(|p| matches!(p.pattern_type, PatternType::NullPadding))
            .collect();
        
        while i < data.len() {
            let current_byte = data[i];
            let mut count = 1;
            
            // Count consecutive bytes with enhanced detection
            while i + count < data.len() && data[i + count] == current_byte && count < 65535 {
                count += 1;
            }
            
            // Enhanced encoding for known null patterns and long runs
            if count >= 4 || (count >= 2 && self.is_in_null_pattern(i, &null_patterns)) {
                if count <= 255 {
                    // Standard RLE encoding for medium runs
                    compressed.push(0xFF); // Escape byte for RLE
                    compressed.push(count as u8);
                    compressed.push(current_byte);
                } else {
                    // Extended RLE encoding for very long runs
                    compressed.push(0xFE); // Extended escape byte
                    compressed.extend_from_slice(&(count as u16).to_le_bytes());
                    compressed.push(current_byte);
                }
            } else if count == 1 {
                // Single byte - encode directly unless it's an escape character
                if current_byte == 0xFF || current_byte == 0xFE {
                    compressed.push(0xFD); // Single byte escape
                    compressed.push(current_byte);
                } else {
                    compressed.push(current_byte);
                }
            } else {
                // Short runs (2-3 bytes) - copy directly for efficiency
                for _ in 0..count {
                    compressed.push(current_byte);
                }
            }
            
            i += count;
        }
        
        compressed
    }

    /// Enhanced LZ77 with pattern-aware window sizing
    fn lz77_compress(&self, data: &[u8], patterns: &[PatternInfo]) -> Vec<u8> {
        let mut compressed = Vec::new();
        let window_size = self.calculate_optimal_window_size(patterns);
        let lookahead_size = 255; // Extended lookahead for better compression
        
        let mut i = 0;
        while i < data.len() {
            let mut best_match = (0, 0); // (distance, length)
            let search_start = if i >= window_size { i - window_size } else { 0 };
            
            // Find the longest match in the sliding window with enhanced search
            for j in search_start..i {
                let mut match_length = 0;
                while match_length < lookahead_size
                    && i + match_length < data.len()
                    && j + match_length < i
                    && data[j + match_length] == data[i + match_length] {
                    match_length += 1;
                }
                
                if match_length > best_match.1 {
                    best_match = (i - j, match_length);
                }
            }
            
            // Enhanced encoding with variable-length encoding for better compression
            if best_match.1 >= 4 {
                // Encode as (distance, length) with extended length support
                compressed.extend_from_slice(&(best_match.0 as u16).to_le_bytes());
                if best_match.1 <= 255 {
                    compressed.push(best_match.1 as u8);
                } else {
                    compressed.push(0xFF); // Extended length marker
                    compressed.extend_from_slice(&(best_match.1 as u16).to_le_bytes());
                }
                i += best_match.1;
            } else if best_match.1 >= 3 {
                // Standard encoding for medium matches
                compressed.extend_from_slice(&(best_match.0 as u16).to_le_bytes());
                compressed.push(best_match.1 as u8);
                i += best_match.1;
            } else {
                // Encode as literal with run-length optimization
                let mut literal_count = 1;
                while i + literal_count < data.len() 
                    && literal_count < 255 
                    && data[i + literal_count] == data[i] {
                    literal_count += 1;
                }
                
                if literal_count >= 3 {
                    // RLE encoding for repeated literals
                    compressed.push(0x00); // RLE literal marker
                    compressed.push(literal_count as u8);
                    compressed.push(data[i]);
                    i += literal_count;
                } else {
                    // Standard literal encoding
                    compressed.push(0x01); // Literal marker
                    compressed.push(literal_count as u8);
                    for k in 0..literal_count {
                        compressed.push(data[i + k]);
                    }
                    i += literal_count;
                }
            }
        }
        
        compressed
    }

    /// Custom periodic compression for highly periodic data
    fn periodic_compress(&self, data: &[u8], patterns: &[PatternInfo]) -> Vec<u8> {
        let periodic_patterns: Vec<_> = patterns.iter()
            .filter(|p| matches!(p.pattern_type, PatternType::PeriodicPatterns))
            .collect();
        
        if let Some(pattern) = periodic_patterns.first() {
            if let Some(period) = self.extract_period_from_metadata(&pattern.metadata) {
                return self.compress_with_period(data, period);
            }
        }
        
        // Fallback to LZ77 if no clear period found
        self.lz77_compress(data, patterns)
    }

    /// Dictionary compression for cluster patterns
    fn dictionary_compress(&self, data: &[u8], patterns: &[PatternInfo]) -> Vec<u8> {
        let mut dictionary = HashMap::new();
        let mut compressed = Vec::new();
        let mut dict_index = 0u16;
        
        // Build dictionary from cluster patterns
        for pattern in patterns.iter().filter(|p| matches!(p.pattern_type, PatternType::ClusterPatterns)) {
            if let Some(dominant_value) = self.extract_dominant_value(&pattern.metadata) {
                dictionary.insert(vec![dominant_value], dict_index);
                dict_index += 1;
            }
        }
        
        // Compress using dictionary
        let mut i = 0;
        while i < data.len() {
            let mut best_match_len = 0;
            let mut best_match_index = 0u16;
            
            // Find longest dictionary match
            for (dict_entry, &index) in &dictionary {
                if i + dict_entry.len() <= data.len() {
                    if &data[i..i + dict_entry.len()] == dict_entry && dict_entry.len() > best_match_len {
                        best_match_len = dict_entry.len();
                        best_match_index = index;
                    }
                }
            }
            
            if best_match_len > 0 {
                compressed.extend_from_slice(&best_match_index.to_le_bytes());
                i += best_match_len;
            } else {
                compressed.extend_from_slice(&0xFFFFu16.to_le_bytes()); // Literal marker
                compressed.push(data[i]);
                i += 1;
            }
        }
        
        compressed
    }

    /// Hybrid compression that combines multiple algorithms for maximum efficiency
    fn hybrid_compress(&self, data: &[u8], patterns: &[PatternInfo]) -> Vec<u8> {
        let mut best_compression = Vec::new();
        let mut best_ratio = 0.0;
        
        // Try different algorithm combinations
        let algorithms = vec![
            ("RLE", self.rle_compress(data, patterns)),
            ("LZ77", self.lz77_compress(data, patterns)),
            ("Dictionary", self.dictionary_compress(data, patterns)),
        ];
        
        for (_name, compressed) in algorithms {
            let ratio = if data.len() > 0 {
                (data.len() - compressed.len()) as f64 / data.len() as f64
            } else {
                0.0
            };
            
            if ratio > best_ratio {
                best_ratio = ratio;
                best_compression = compressed;
            }
        }
        
        // If no single algorithm is effective, try cascaded compression
        if best_ratio < 0.1 && data.len() > 1024 {
            let mut cascaded = data.to_vec();
            
            // Apply RLE first, then LZ77
            cascaded = self.rle_compress(&cascaded, patterns);
            cascaded = self.lz77_compress(&cascaded, patterns);
            
            let cascaded_ratio = if data.len() > 0 {
                (data.len() - cascaded.len()) as f64 / data.len() as f64
            } else {
                0.0
            };
            
            if cascaded_ratio > best_ratio {
                best_compression = cascaded;
            }
        }
        
        best_compression
    }

    /// Adaptive compression that dynamically selects the best algorithm
    fn adaptive_compress(&self, data: &[u8], patterns: &[PatternInfo]) -> Vec<u8> {
        // Real-time pattern analysis for dynamic algorithm selection
        let mut dynamic_patterns = patterns.to_vec();
        
        // Analyze data characteristics on-the-fly
        let entropy = self.calculate_entropy(data);
        let null_ratio = data.iter().filter(|&&b| b == 0).count() as f64 / data.len() as f64;
        let repetition_ratio = self.calculate_repetition_ratio(data);
        
        // Add dynamic patterns based on real-time analysis
        if null_ratio > 0.3 {
            dynamic_patterns.push(PatternInfo {
                pattern_type: PatternType::NullPadding,
                size: (data.len() as f64 * null_ratio) as usize,
                frequency: (data.len() as f64 * null_ratio) as usize,
                confidence: 0.9,
                locations: vec![0],
                metadata: HashMap::new(),
                compression_ratio: 0.8,
                entropy: 0.0,
                predictability: 0.9,
                spatial_distribution: 1.0,
                compression_gain: (data.len() as f64 * null_ratio * 0.8) as f64,
                algorithm_fitness: HashMap::new(),
            });
        }
        
        if repetition_ratio > 0.4 {
            dynamic_patterns.push(PatternInfo {
                pattern_type: PatternType::RepetitiveSequences,
                size: (data.len() as f64 * repetition_ratio) as usize,
                frequency: (data.len() as f64 * repetition_ratio) as usize,
                confidence: 0.85,
                locations: vec![0],
                metadata: HashMap::new(),
                compression_ratio: 0.7,
                entropy: 0.0,
                predictability: 0.8,
                spatial_distribution: 0.9,
                compression_gain: (data.len() as f64 * repetition_ratio * 0.7) as f64,
                algorithm_fitness: HashMap::new(),
            });
        }
        
        // Select algorithm based on dynamic analysis
        if entropy < 4.0 && null_ratio > 0.2 {
            // Low entropy with null patterns - use RLE
            self.rle_compress(data, &dynamic_patterns)
        } else if repetition_ratio > 0.3 {
            // High repetition - use LZ77
            self.lz77_compress(data, &dynamic_patterns)
        } else if entropy > 6.0 {
            // High entropy - use hybrid approach
            self.hybrid_compress(data, &dynamic_patterns)
        } else {
            // Balanced approach - use hybrid
            self.hybrid_compress(data, &dynamic_patterns)
        }
    }
    
    /// Calculate repetition ratio in data
    fn calculate_repetition_ratio(&self, data: &[u8]) -> f64 {
        if data.len() < 2 {
            return 0.0;
        }
        
        let mut repeated_bytes = 0;
        for i in 1..data.len() {
            if data[i] == data[i-1] {
                repeated_bytes += 1;
            }
        }
        
        repeated_bytes as f64 / (data.len() - 1) as f64
    }
    
    /// Calculate entropy of data
    fn calculate_entropy(&self, data: &[u8]) -> f64 {
        if data.is_empty() {
            return 0.0;
        }
        
        let mut byte_counts = HashMap::new();
        for &byte in data {
            *byte_counts.entry(byte).or_insert(0) += 1;
        }
        
        let data_len = data.len() as f64;
        let mut entropy = 0.0;
        
        for count in byte_counts.values() {
            let probability = *count as f64 / data_len;
            if probability > 0.0 {
                entropy -= probability * probability.log2();
            }
        }
        
        entropy
    }

    // Helper functions for pattern analysis
    fn calculate_optimal_window_size(&self, patterns: &[PatternInfo]) -> usize {
        let base_window = 4096;
        if patterns.is_empty() {
            return base_window;
        }
        
        let pattern_factor = patterns.iter()
            .map(|p| p.confidence)
            .fold(0.0, |acc, conf| acc + conf) / patterns.len() as f64;
        
        (base_window as f64 * (1.0 + pattern_factor)).min(32768.0) as usize
    }

    fn is_in_null_pattern(&self, position: usize, null_patterns: &[&PatternInfo]) -> bool {
        null_patterns.iter().any(|pattern| {
            pattern.locations.iter().any(|&loc| {
                position >= loc && position < loc + pattern.size
            })
        })
    }

    fn extract_period_from_metadata(&self, metadata: &HashMap<String, String>) -> Option<usize> {
        // Parse period from metadata
        metadata.get("period")
            .and_then(|s| s.parse().ok())
    }

    fn extract_dominant_value(&self, metadata: &HashMap<String, String>) -> Option<u8> {
        // Parse dominant value from metadata
        metadata.get("dominant_value")
            .and_then(|s| s.parse().ok())
    }

    fn compress_with_period(&self, data: &[u8], period: usize) -> Vec<u8> {
        let mut compressed = Vec::new();
        
        // Store the period
        compressed.extend_from_slice(&(period as u32).to_le_bytes());
        
        // Store the template
        if data.len() >= period {
            compressed.extend_from_slice(&data[0..period]);
        }
        
        // Store differences from the template
        let mut i = period;
        while i < data.len() {
            let template_index = i % period;
            if template_index < data.len() && data[i] != data[template_index] {
                compressed.extend_from_slice(&(i as u32).to_le_bytes());
                compressed.push(data[i]);
            }
            i += 1;
        }
        
        compressed
    }

    fn calculate_pattern_efficiency(&self, patterns: &[PatternInfo]) -> f64 {
        if patterns.is_empty() {
            return 0.0;
        }
        
        patterns.iter()
            .map(|p| p.confidence)
            .fold(0.0, |acc, conf| acc + conf) / patterns.len() as f64
    }

    fn calculate_algorithm_confidence(&self, patterns: &[PatternInfo], algorithm: &str) -> f64 {
        if patterns.is_empty() {
            return 0.5; // Default confidence
        }
        
        let mut total_confidence = 0.0;
        let mut count = 0;
        
        for pattern in patterns {
            if let Some(fitness) = pattern.algorithm_fitness.get(algorithm) {
                total_confidence += *fitness;
                count += 1;
            }
        }
        
        if count > 0 {
            total_confidence / count as f64
        } else {
            0.5
        }
    }
}

/// Phase 3: Integrated compression and analysis system
pub struct Phase3CompressionSystem {
    pattern_engine: PatternRecognitionEngine,
    compressor: PatternBasedCompressor,
}

impl Phase3CompressionSystem {
    pub fn new() -> Self {
        let config = PatternRecognitionConfig::default();
        Self {
            pattern_engine: PatternRecognitionEngine::new(config),
            compressor: PatternBasedCompressor::new(),
        }
    }

    /// Complete Phase 3 workflow: analyze + compress
    pub fn analyze_and_compress(&self, file_path: &Path) -> Result<(PatternAnalysisResult, CompressionResult), Box<dyn std::error::Error>> {
        // Phase 2: Pattern analysis
        let analysis = self.pattern_engine.analyze_file(file_path)?;
        
        // Read file data for compression
        let mut file = File::open(file_path)?;
        let mut data = Vec::new();
        file.read_to_end(&mut data)?;
        
        // Phase 3: Compression based on patterns
        let compression = self.compressor.compress_with_patterns(&data, &analysis.patterns_found);
        
        Ok((analysis, compression))
    }

    /// Batch process multiple files
    pub fn batch_process(&self, file_paths: &[&Path]) -> Result<Vec<(PatternAnalysisResult, CompressionResult)>, Box<dyn std::error::Error>> {
        let mut results = Vec::new();
        
        for file_path in file_paths {
            match self.analyze_and_compress(file_path) {
                Ok(result) => results.push(result),
                Err(e) => eprintln!("Error processing {}: {}", file_path.display(), e),
            }
        }
        
        Ok(results)
    }
}

/// Display Phase 3 compression results
pub fn display_phase3_results(analysis: &PatternAnalysisResult, compression: &CompressionResult) {
    println!("\n🚀 PHASE 3 COMPRESSION RESULTS");
    println!("=================================");
    println!("📁 File: {}", std::path::Path::new(&analysis.file_path).file_name().unwrap().to_string_lossy());
    println!("📏 Original Size: {:.2} MB", analysis.file_size as f64 / (1024.0 * 1024.0));
    println!("🗜️  Compressed Size: {:.2} MB", compression.compressed_size as f64 / (1024.0 * 1024.0));
    println!("📊 Compression Ratio: {:.1}%", compression.compression_ratio);
    println!("💾 Space Saved: {:.2} MB", compression.compression_gain_bytes as f64 / (1024.0 * 1024.0));
    println!("⚡ Algorithm Used: {} (confidence: {:.1}%)", 
        compression.algorithm_used, compression.algorithm_confidence * 100.0);
    println!("⏱️  Processing Time: {} ms", compression.processing_time_ms);
    println!("🎯 Pattern Efficiency: {:.1}%", compression.pattern_efficiency * 100.0);
    
    println!("\n🔍 Phase 2 Pattern Analysis:");
    display_enhanced_pattern_analysis(analysis);
}

// ============================================================================
// 🧪 TESTING FRAMEWORK FOR PHASE 3
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::Path;

    #[test]
    fn test_compression_pipeline() {
        let compressor = PatternBasedCompressor::new();
        let test_data = vec![0u8; 1000]; // Simple null data for testing
        
        let patterns = vec![
            PatternInfo {
                pattern_type: PatternType::NullPadding,
                frequency: 1,
                size: 1000,
                compression_ratio: 0.95,
                confidence: 0.95,
                locations: vec![0],
                metadata: {
                    let mut m = HashMap::new();
                    m.insert("null_ratio".to_string(), "0.95".to_string());
                    m
                },
                entropy: 0.0,
                predictability: 1.0,
                spatial_distribution: 0.8,
                compression_gain: 950.0,
                algorithm_fitness: {
                    let mut m = HashMap::new();
                    m.insert("RLE".to_string(), 0.95);
                    m
                },
            }
        ];
        
        let result = compressor.compress_with_patterns(&test_data, &patterns);
        
        assert!(result.compression_ratio > 80.0, "Expected high compression ratio for null data");
        assert_eq!(result.algorithm_used, "RLE");
        println!("Test passed: {:?}", result);
    }

    #[test]
    fn test_algorithm_selection() {
        let compressor = PatternBasedCompressor::new();
        
        // Test periodic pattern
        let periodic_patterns = vec![
            PatternInfo {
                pattern_type: PatternType::PeriodicPatterns,
                frequency: 10,
                size: 16,
                compression_ratio: 0.85,
                confidence: 0.95,
                locations: vec![0],
                metadata: {
                    let mut m = HashMap::new();
                    m.insert("period".to_string(), "16".to_string());
                    m
                },
                entropy: 3.0,
                predictability: 0.95,
                spatial_distribution: 1.0,
                compression_gain: 136.0,
                algorithm_fitness: HashMap::new(),
            }
        ];
        
        let algorithm = compressor.select_optimal_algorithm(&periodic_patterns);
        assert_eq!(algorithm, "Custom-Periodic");
    }
}

/// Main function for Phase 3 demonstration
fn main() {
    println!("🚀 Phase 3: Advanced Pattern-Based Compression Framework");
    println!("Ready for integration with Phase 2 pattern analysis!");
    
    // Example usage
    let _system = Phase3CompressionSystem::new();
    println!("Phase 3 system initialized successfully!");
    
    // Test compressor
    let compressor = PatternBasedCompressor::new();
    println!("Compressor initialized with adaptive strategy: {}", compressor.adaptive_strategy);
}
