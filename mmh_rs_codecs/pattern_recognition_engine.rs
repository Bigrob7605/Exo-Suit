// Pattern Recognition Engine for MMH-RS Universal Compression Champion
// Phase 2: Advanced Pattern Recognition & Compression Strategy Matrix

use std::collections::HashMap;
use std::fs::File;
use std::io::Read;
use std::path::Path;
use std::time::Instant;

/// Represents different types of patterns found in data
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum PatternType {
    // Structural patterns
    RepetitiveSequences,    // Repeated byte sequences
    NullPadding,            // Blocks of null bytes
    StructuredData,         // Regular data structures
    HeaderTrailer,          // File headers and trailers
    
    // Content patterns
    TextPatterns,           // Repetitive text content
    BinaryPatterns,         // Binary data patterns
    CompressedData,         // Already compressed content
    RandomData,             // High entropy random data
    
    // Algorithm-specific patterns
    LZ77Patterns,           // LZ77 compression opportunities
    RLEPatterns,            // Run-length encoding opportunities
    DictionaryPatterns,     // Dictionary-based compression
    DeltaPatterns,          // Delta encoding opportunities
}

/// Detailed pattern information
#[derive(Debug, Clone)]
pub struct PatternInfo {
    pub pattern_type: PatternType,
    pub frequency: usize,           // How often this pattern occurs
    pub size: usize,                // Size of the pattern
    pub compression_ratio: f64,     // Estimated compression ratio
    pub confidence: f64,            // Confidence in this pattern (0.0-1.0)
    pub locations: Vec<usize>,      // Where this pattern appears
    pub metadata: HashMap<String, String>, // Additional pattern details
}

/// Compression strategy recommendation
#[derive(Debug, Clone)]
pub struct CompressionStrategy {
    pub primary_algorithm: String,
    pub secondary_algorithm: Option<String>,
    pub estimated_ratio: f64,
    pub confidence: f64,
    pub reasoning: Vec<String>,
    pub parameters: HashMap<String, String>,
}

/// Pattern recognition analysis result
#[derive(Debug, Clone)]
pub struct PatternAnalysisResult {
    pub file_path: String,
    pub file_size: u64,
    pub patterns_found: Vec<PatternInfo>,
    pub recommended_strategy: CompressionStrategy,
    pub analysis_time: u128,
    pub memory_used: usize,
}

/// Main pattern recognition engine
pub struct PatternRecognitionEngine {
    config: PatternRecognitionConfig,
    pattern_database: HashMap<PatternType, PatternTemplate>,
}

/// Configuration for pattern recognition
#[derive(Debug, Clone)]
pub struct PatternRecognitionConfig {
    pub min_pattern_size: usize,
    pub max_pattern_size: usize,
    pub min_frequency: usize,
    pub confidence_threshold: f64,
    pub max_patterns_per_file: usize,
    pub memory_limit_mb: usize,
    pub enable_deep_analysis: bool,
}

/// Pattern template for recognition
#[derive(Debug, Clone)]
struct PatternTemplate {
    signature: Vec<u8>,
    min_size: usize,
    max_size: usize,
    expected_compression: f64,
    algorithm_suggestions: Vec<String>,
}

impl Default for PatternRecognitionConfig {
    fn default() -> Self {
        Self {
            min_pattern_size: 8,
            max_pattern_size: 1024,
            min_frequency: 3,
            confidence_threshold: 0.7,
            max_patterns_per_file: 20,
            memory_limit_mb: 100,
            enable_deep_analysis: true,
        }
    }
}

impl PatternRecognitionEngine {
    /// Create a new pattern recognition engine
    pub fn new(config: PatternRecognitionConfig) -> Self {
        let mut engine = Self {
            config,
            pattern_database: HashMap::new(),
        };
        engine.initialize_pattern_database();
        engine
    }
    
    /// Initialize the pattern recognition database
    fn initialize_pattern_database(&mut self) {
        // Repetitive sequence patterns
        self.pattern_database.insert(PatternType::RepetitiveSequences, PatternTemplate {
            signature: vec![], // Dynamic detection
            min_size: 8,
            max_size: 256,
            expected_compression: 0.8,
            algorithm_suggestions: vec!["LZ77".to_string(), "LZ78".to_string()],
        });
        
        // Null padding patterns
        self.pattern_database.insert(PatternType::NullPadding, PatternTemplate {
            signature: vec![0x00],
            min_size: 16,
            max_size: 1024,
            expected_compression: 0.95,
            algorithm_suggestions: vec!["RLE".to_string(), "LZ77".to_string()],
        });
        
        // Structured data patterns
        self.pattern_database.insert(PatternType::StructuredData, PatternTemplate {
            signature: vec![],
            min_size: 32,
            max_size: 512,
            expected_compression: 0.6,
            algorithm_suggestions: vec!["Dictionary".to_string(), "Delta".to_string()],
        });
        
        // Text patterns
        self.pattern_database.insert(PatternType::TextPatterns, PatternTemplate {
            signature: vec![],
            min_size: 16,
            max_size: 256,
            expected_compression: 0.7,
            algorithm_suggestions: vec!["LZ77".to_string(), "Huffman".to_string()],
        });
        
        // Binary patterns
        self.pattern_database.insert(PatternType::BinaryPatterns, PatternTemplate {
            signature: vec![],
            min_size: 8,
            max_size: 128,
            expected_compression: 0.5,
            algorithm_suggestions: vec!["LZ77".to_string(), "Dictionary".to_string()],
        });
    }
    
    /// Analyze a file for compression patterns
    pub fn analyze_file(&self, file_path: &Path) -> Result<PatternAnalysisResult, Box<dyn std::error::Error>> {
        let start_time = Instant::now();
        let mut file = File::open(file_path)?;
        let metadata = file.metadata()?;
        let file_size = metadata.len();
        
        println!("🔍 Analyzing patterns in: {}", file_path.file_name().unwrap().to_string_lossy());
        
        // Read file content for analysis
        let mut buffer = Vec::new();
        file.read_to_end(&mut buffer)?;
        let memory_used = buffer.len();
        
        // Perform pattern recognition
        let patterns = self.recognize_patterns(&buffer)?;
        
        // Generate compression strategy
        let strategy = self.generate_compression_strategy(&patterns, file_size)?;
        
        let analysis_time = start_time.elapsed().as_millis();
        
        Ok(PatternAnalysisResult {
            file_path: file_path.to_string_lossy().to_string(),
            file_size,
            patterns_found: patterns,
            recommended_strategy: strategy,
            analysis_time,
            memory_used,
        })
    }
    
    /// Recognize patterns in data
    pub fn recognize_patterns(&self, data: &[u8]) -> Result<Vec<PatternInfo>, Box<dyn std::error::Error>> {
        let mut patterns = Vec::new();
        
        // 1. Detect repetitive sequences
        if let Some(repetitive) = self.detect_repetitive_sequences(data)? {
            patterns.push(repetitive);
        }
        
        // 2. Detect null padding
        if let Some(null_padding) = self.detect_null_padding(data)? {
            patterns.push(null_padding);
        }
        
        // 3. Detect structured data
        if let Some(structured) = self.detect_structured_data(data)? {
            patterns.push(structured);
        }
        
        // 4. Detect text patterns
        if let Some(text) = self.detect_text_patterns(data)? {
            patterns.push(text);
        }
        
        // 5. Detect binary patterns
        if let Some(binary) = self.detect_binary_patterns(data)? {
            patterns.push(binary);
        }
        
        // Limit patterns based on configuration
        if patterns.len() > self.config.max_patterns_per_file {
            patterns.truncate(self.config.max_patterns_per_file);
        }
        
        Ok(patterns)
    }
    
    /// Detect repetitive byte sequences
    fn detect_repetitive_sequences(&self, data: &[u8]) -> Result<Option<PatternInfo>, Box<dyn std::error::Error>> {
        let mut sequences = HashMap::new();
        
        // Look for sequences of different sizes
        for size in self.config.min_pattern_size..=self.config.max_pattern_size.min(data.len() / 2) {
            for start in 0..=data.len() - size {
                let sequence = &data[start..start + size];
                let count = sequences.entry(sequence.to_vec()).or_insert(0);
                *count += 1;
            }
        }
        
        // Find the most frequent sequence
        let mut best_sequence = None;
        let mut best_frequency = 0;
        
        for (sequence, frequency) in sequences {
            if frequency >= self.config.min_frequency && frequency > best_frequency {
                best_sequence = Some((sequence, frequency));
                best_frequency = frequency;
            }
        }
        
        if let Some((sequence, frequency)) = best_sequence {
            let compression_ratio = self.estimate_compression_ratio(&sequence, frequency);
            let confidence = (frequency as f64 / (data.len() as f64 / sequence.len() as f64)).min(1.0);
            
            Ok(Some(PatternInfo {
                pattern_type: PatternType::RepetitiveSequences,
                frequency,
                size: sequence.len(),
                compression_ratio,
                confidence,
                locations: vec![0], // Simplified for now
                metadata: HashMap::new(),
            }))
        } else {
            Ok(None)
        }
    }
    
    /// Detect null padding patterns
    fn detect_null_padding(&self, data: &[u8]) -> Result<Option<PatternInfo>, Box<dyn std::error::Error>> {
        let mut null_blocks = Vec::new();
        let mut current_block_start = None;
        
        for (i, &byte) in data.iter().enumerate() {
            if byte == 0x00 {
                if current_block_start.is_none() {
                    current_block_start = Some(i);
                }
            } else {
                if let Some(start) = current_block_start {
                    let block_size = i - start;
                    if block_size >= self.config.min_pattern_size {
                        null_blocks.push((start, block_size));
                    }
                    current_block_start = None;
                }
            }
        }
        
        // Handle block at end of file
        if let Some(start) = current_block_start {
            let block_size = data.len() - start;
            if block_size >= self.config.min_pattern_size {
                null_blocks.push((start, block_size));
            }
        }
        
        if null_blocks.is_empty() {
            return Ok(None);
        }
        
        // Calculate total null padding
        let total_null_bytes: usize = null_blocks.iter().map(|(_, size)| size).sum();
        let compression_ratio = total_null_bytes as f64 / data.len() as f64;
        let confidence = if compression_ratio > 0.1 { 0.9 } else { 0.5 };
        
        Ok(Some(PatternInfo {
            pattern_type: PatternType::NullPadding,
            frequency: null_blocks.len(),
            size: total_null_bytes,
            compression_ratio,
            confidence,
            locations: null_blocks.iter().map(|(start, _)| *start).collect(),
            metadata: HashMap::new(),
        }))
    }
    
    /// Detect structured data patterns
    fn detect_structured_data(&self, data: &[u8]) -> Result<Option<PatternInfo>, Box<dyn std::error::Error>> {
        // Look for regular intervals and repeated structures
        let mut structure_scores = Vec::new();
        
        for interval in 16..=256 {
            if interval > data.len() / 4 {
                break;
            }
            
            let mut score = 0.0;
            let mut comparisons = 0;
            
            for offset in 0..interval {
                let mut similarity = 0.0;
                let mut count = 0;
                
                for i in (offset..data.len() - interval).step_by(interval) {
                    if i + interval < data.len() {
                        let bytes1 = &data[i..i + interval];
                        let bytes2 = &data[i + interval..i + 2 * interval];
                        
                        let matches = bytes1.iter().zip(bytes2.iter())
                            .filter(|(a, b)| a == b)
                            .count();
                        
                        similarity += matches as f64 / interval as f64;
                        count += 1;
                    }
                }
                
                if count > 0 {
                    score += similarity / count as f64;
                    comparisons += 1;
                }
            }
            
            if comparisons > 0 {
                structure_scores.push((interval, score / comparisons as f64));
            }
        }
        
        // Find the best structure
        if let Some((best_interval, best_score)) = structure_scores.iter()
            .filter(|(_, score)| *score > 0.6)
            .max_by(|(_, a), (_, b)| a.partial_cmp(b).unwrap()) {
            
            let compression_ratio = 0.6; // Structured data typically compresses moderately
            let confidence = best_score.min(1.0);
            
            Ok(Some(PatternInfo {
                pattern_type: PatternType::StructuredData,
                frequency: (data.len() / best_interval).max(1),
                size: *best_interval,
                compression_ratio,
                confidence,
                locations: vec![0],
                metadata: HashMap::new(),
            }))
        } else {
            Ok(None)
        }
    }
    
    /// Detect text patterns
    fn detect_text_patterns(&self, data: &[u8]) -> Result<Option<PatternInfo>, Box<dyn std::error::Error>> {
        let text_bytes: usize = data.iter()
            .filter(|&&b| b.is_ascii_alphabetic() || b.is_ascii_whitespace() || b.is_ascii_punctuation())
            .count();
        
        let text_ratio = text_bytes as f64 / data.len() as f64;
        
        if text_ratio > 0.7 {
            // Look for repeated text patterns
            let mut text_patterns = HashMap::new();
            
            for size in 8..=64 {
                for start in 0..=data.len() - size {
                    let slice = &data[start..start + size];
                    if slice.iter().all(|&b| b.is_ascii()) {
                        let count = text_patterns.entry(slice.to_vec()).or_insert(0);
                        *count += 1;
                    }
                }
            }
            
            let best_pattern = text_patterns.iter()
                .filter(|(_, &count)| count >= self.config.min_frequency)
                .max_by(|(_, a), (_, b)| a.cmp(b));
            
            if let Some((pattern, frequency)) = best_pattern {
                let compression_ratio = 0.7; // Text typically compresses well
                let confidence = text_ratio;
                
                Ok(Some(PatternInfo {
                    pattern_type: PatternType::TextPatterns,
                    frequency: *frequency,
                    size: pattern.len(),
                    compression_ratio,
                    confidence,
                    locations: vec![0],
                    metadata: HashMap::new(),
                }))
            } else {
                Ok(None)
            }
        } else {
            Ok(None)
        }
    }
    
    /// Detect binary patterns
    fn detect_binary_patterns(&self, data: &[u8]) -> Result<Option<PatternInfo>, Box<dyn std::error::Error>> {
        // Look for repeated binary sequences
        let mut binary_patterns = HashMap::new();
        
        for size in 4..=32 {
            for start in 0..=data.len() - size {
                let slice = &data[start..start + size];
                let count = binary_patterns.entry(slice.to_vec()).or_insert(0);
                *count += 1;
            }
        }
        
        let best_pattern = binary_patterns.iter()
            .filter(|(_, &count)| count >= self.config.min_frequency)
            .max_by(|(_, a), (_, b)| a.cmp(b));
        
        if let Some((pattern, frequency)) = best_pattern {
            let compression_ratio = 0.5; // Binary patterns compress moderately
            let confidence = (*frequency as f64 / (data.len() as f64 / pattern.len() as f64)).min(1.0);
            
            Ok(Some(PatternInfo {
                pattern_type: PatternType::BinaryPatterns,
                frequency: *frequency,
                size: pattern.len(),
                compression_ratio,
                confidence,
                locations: vec![0],
                metadata: HashMap::new(),
            }))
        } else {
            Ok(None)
        }
    }
    
    /// Estimate compression ratio for a pattern
    fn estimate_compression_ratio(&self, pattern: &[u8], frequency: usize) -> f64 {
        let pattern_size = pattern.len();
        let total_size = pattern_size * frequency;
        
        if total_size == 0 {
            return 0.0;
        }
        
        // Estimate based on pattern characteristics
        let base_ratio = match pattern_size {
            1..=4 => 0.9,    // Very small patterns compress extremely well
            5..=16 => 0.8,   // Small patterns compress very well
            17..=64 => 0.7,  // Medium patterns compress well
            65..=256 => 0.6, // Large patterns compress moderately
            _ => 0.4,         // Very large patterns compress poorly
        };
        
        // Adjust based on frequency
        let frequency_factor = (frequency as f64).min(100.0) / 100.0;
        
        base_ratio * frequency_factor
    }
    
    /// Generate compression strategy based on patterns
    fn generate_compression_strategy(&self, patterns: &[PatternInfo], file_size: u64) -> Result<CompressionStrategy, Box<dyn std::error::Error>> {
        if patterns.is_empty() {
            return Ok(CompressionStrategy {
                primary_algorithm: "Generic".to_string(),
                secondary_algorithm: None,
                estimated_ratio: 0.5,
                confidence: 0.3,
                reasoning: vec!["No specific patterns detected".to_string()],
                parameters: HashMap::new(),
            });
        }
        
        // Find the best pattern
        let best_pattern = patterns.iter()
            .max_by(|a, b| a.compression_ratio.partial_cmp(&b.compression_ratio).unwrap())
            .unwrap();
        
        // Determine primary algorithm
        let primary_algorithm = match best_pattern.pattern_type {
            PatternType::RepetitiveSequences => "LZ77",
            PatternType::NullPadding => "RLE",
            PatternType::StructuredData => "Dictionary",
            PatternType::TextPatterns => "LZ77",
            PatternType::BinaryPatterns => "LZ77",
            _ => "Generic",
        };
        
        // Determine secondary algorithm
        let secondary_algorithm = match primary_algorithm {
            "LZ77" => Some("Huffman".to_string()),
            "RLE" => Some("LZ77".to_string()),
            "Dictionary" => Some("Huffman".to_string()),
            _ => None,
        };
        
        // Generate reasoning
        let mut reasoning = Vec::new();
        reasoning.push(format!("Detected {:?} pattern with {:.1}% confidence", 
            best_pattern.pattern_type, best_pattern.confidence * 100.0));
        reasoning.push(format!("Pattern size: {} bytes, frequency: {}", 
            best_pattern.size, best_pattern.frequency));
        reasoning.push(format!("Estimated compression ratio: {:.1}%", 
            best_pattern.compression_ratio * 100.0));
        
        // Set parameters
        let mut parameters = HashMap::new();
        parameters.insert("window_size".to_string(), "32768".to_string());
        parameters.insert("min_match_length".to_string(), "3".to_string());
        parameters.insert("max_match_length".to_string(), "258".to_string());
        
        Ok(CompressionStrategy {
            primary_algorithm: primary_algorithm.to_string(),
            secondary_algorithm,
            estimated_ratio: best_pattern.compression_ratio,
            confidence: best_pattern.confidence,
            reasoning,
            parameters,
        })
    }
}

/// Display pattern analysis results
pub fn display_pattern_analysis(result: &PatternAnalysisResult) {
    println!("\n🔍 Pattern Analysis Results for: {}", result.file_path);
    println!("📏 File Size: {:.2} MB", result.file_size as f64 / (1024.0 * 1024.0));
    println!("⏱️  Analysis Time: {} ms", result.analysis_time);
    println!("🧠 Memory Used: {:.2} MB", result.memory_used as f64 / (1024.0 * 1024.0));
    
    println!("\n📊 Patterns Found: {} patterns", result.patterns_found.len());
    for (i, pattern) in result.patterns_found.iter().enumerate() {
        println!("  {}. {:?}", i + 1, pattern.pattern_type);
        println!("     Size: {} bytes, Frequency: {}", pattern.size, pattern.frequency);
        println!("     Compression Ratio: {:.1}%, Confidence: {:.1}%", 
            pattern.compression_ratio * 100.0, pattern.confidence * 100.0);
    }
    
    println!("\n🎯 Recommended Compression Strategy:");
    println!("  Primary Algorithm: {}", result.recommended_strategy.primary_algorithm);
    if let Some(ref secondary) = result.recommended_strategy.secondary_algorithm {
        println!("  Secondary Algorithm: {}", secondary);
    }
    println!("  Estimated Compression Ratio: {:.1}%", 
        result.recommended_strategy.estimated_ratio * 100.0);
    println!("  Confidence: {:.1}%", result.recommended_strategy.confidence * 100.0);
    
    println!("\n💡 Reasoning:");
    for reason in &result.recommended_strategy.reasoning {
        println!("  → {}", reason);
    }
    
    if !result.recommended_strategy.parameters.is_empty() {
        println!("\n⚙️  Parameters:");
        for (key, value) in &result.recommended_strategy.parameters {
            println!("  {}: {}", key, value);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_pattern_recognition_engine_creation() {
        let config = PatternRecognitionConfig::default();
        let engine = PatternRecognitionEngine::new(config);
        assert!(!engine.pattern_database.is_empty());
    }
    
    #[test]
    fn test_null_padding_detection() {
        let config = PatternRecognitionConfig::default();
        let engine = PatternRecognitionEngine::new(config);
        
        // Create test data with null padding
        let mut test_data = vec![0x01, 0x02, 0x03];
        test_data.extend(vec![0x00; 100]); // 100 null bytes
        test_data.extend(vec![0x04, 0x05, 0x06]);
        
        let patterns = engine.recognize_patterns(&test_data).unwrap();
        let null_pattern = patterns.iter().find(|p| matches!(p.pattern_type, PatternType::NullPadding));
        
        assert!(null_pattern.is_some());
        if let Some(pattern) = null_pattern {
            assert!(pattern.size >= 100);
            assert!(pattern.compression_ratio > 0.8);
        }
    }
}
