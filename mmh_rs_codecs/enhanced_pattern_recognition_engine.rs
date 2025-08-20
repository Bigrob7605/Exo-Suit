// Enhanced Pattern Recognition Engine for MMH-RS Universal Compression Champion
// Phase 2: Advanced Pattern Recognition & Compression Strategy Matrix
// Integrated with Silesia Corpus validation results + Simple Animated Spinner

use std::collections::HashMap;
use std::fs::File;
use std::io::{self, Read, Write};
use std::path::Path;
use std::time::{Duration, Instant};
use std::thread;
use std::sync::{Arc, Mutex, atomic::{AtomicBool, Ordering}};

/// Simple animated spinner for MMH-RS operations
pub struct MMHRSSpinner {
    running: Arc<AtomicBool>,
    message: String,
}

impl MMHRSSpinner {
    pub fn new(message: &str) -> Self {
        Self {
            running: Arc::new(AtomicBool::new(false)),
            message: message.to_string(),
        }
    }

    pub fn start(&self) {
        self.running.store(true, Ordering::Relaxed);
        let running = Arc::clone(&self.running);
        let message = self.message.clone();

        thread::spawn(move || {
            let frames = vec!["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"];
            let mut frame_idx = 0;
            
            while running.load(Ordering::Relaxed) {
                print!("\r\x1B[K"); // Clear line
                print!("{} {}", frames[frame_idx % frames.len()], message);
                io::stdout().flush().unwrap();
                
                frame_idx += 1;
                thread::sleep(Duration::from_millis(100));
            }
            
            // Clear the line when done
            print!("\r\x1B[K");
            io::stdout().flush().unwrap();
        });
    }

    pub fn stop(&self) {
        self.running.store(false, Ordering::Relaxed);
        thread::sleep(Duration::from_millis(50)); // Give time to clean up
    }

    pub fn finish_with_message(&self, message: &str) {
        self.stop();
        println!("✅ {}", message);
    }
}

/// Real-time progress tracking for MMH-RS operations
#[derive(Debug, Clone)]
pub struct MMHRSProgress {
    start_time: Instant,
    current_operation: String,
    current_file: String,
    total_files: usize,
    processed_files: usize,
    current_file_progress: f64, // 0.0 to 1.0
    animation_frame: usize,
    is_working: bool,
}

impl MMHRSProgress {
    pub fn new(total_files: usize) -> Self {
        Self {
            start_time: Instant::now(),
            current_operation: "Initializing MMH-RS...".to_string(),
            current_file: String::new(),
            total_files,
            processed_files: 0,
            current_file_progress: 0.0,
            animation_frame: 0,
            is_working: false,
        }
    }

    pub fn update_operation(&mut self, operation: &str) {
        self.current_operation = operation.to_string();
        self.is_working = true;
    }

    pub fn update_file(&mut self, filename: &str) {
        self.current_file = filename.to_string();
        self.current_file_progress = 0.0;
        self.is_working = true;
    }

    pub fn update_file_progress(&mut self, progress: f64) {
        self.current_file_progress = progress;
    }

    pub fn file_completed(&mut self) {
        self.processed_files += 1;
        self.current_file_progress = 1.0;
        self.is_working = false;
    }

    pub fn display_progress(&mut self) {
        self.animation_frame += 1;
        
        // Clear the entire line and move cursor back
        print!("\r\x1B[K");
        
        // Overall progress bar (files completed)
        let overall_width = 20;
        let overall_progress = (self.processed_files as f64 / self.total_files as f64) * overall_width as f64;
        
        let mut overall_bar = String::new();
        for i in 0..overall_width {
            if i < overall_progress as usize {
                overall_bar.push_str("█");
            } else {
                overall_bar.push_str("░");
            }
        }
        
        // Current file progress bar with MMH-RS branding
        let file_width = 25;
        let file_progress = self.current_file_progress * file_width as f64;
        
        let mut file_bar = String::new();
        for i in 0..file_width {
            if i < file_progress as usize {
                // MMH-RS animated pattern
                let pattern_char = match (i + self.animation_frame) % 4 {
                    0 => "█",
                    1 => "▓",
                    2 => "▒",
                    _ => "░",
                };
                file_bar.push_str(pattern_char);
            } else {
                file_bar.push_str("░");
            }
        }
        
        // MMH-RS branded spinner
        let spinner = if self.is_working {
            match self.animation_frame % 4 {
                0 => "⠋",
                1 => "⠙",
                2 => "⠹",
                _ => "⠸",
            }
        } else {
            "⏸"
        };
        
        // File progress
        let file_progress_text = format!("[{}/{}]", self.processed_files, self.total_files);
        
        // Time estimate
        let elapsed = self.start_time.elapsed();
        let elapsed_secs = elapsed.as_secs_f64();
        let eta = if self.processed_files > 0 {
            let avg_time = elapsed_secs / self.processed_files as f64;
            let remaining = (self.total_files - self.processed_files) as f64 * avg_time;
            format!("ETA: {:.1}s", remaining)
        } else {
            "ETA: calculating...".to_string()
        };
        
        // Display MMH-RS progress with branding
        print!("{} MMH-RS: {} | File: {} | {} | {} | {} | {}", 
            spinner, overall_bar, file_bar, file_progress_text, self.current_operation, self.current_file, eta);
        
        io::stdout().flush().unwrap();
    }

    pub fn final_display(&self) {
        let total_time = self.start_time.elapsed();
        println!("\n\n🎉 MMH-RS Enhanced Pattern Recognition completed in {:.2}s!", total_time.as_secs_f64());
        println!("📊 Processed {} files successfully", self.processed_files);
        println!("⚡ Average time per file: {:.2}s", 
            total_time.as_secs_f64() / self.processed_files as f64);
        println!("🚀 MMH-RS System: Ready for production deployment!");
    }
}

/// Enhanced pattern types based on Silesia Corpus analysis
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum EnhancedPatternType {
    // High compression patterns (from Silesia results)
    DatabasePatterns,      // nci: 11.80x, xml: 8.36x
    TextPatterns,          // dickens: 2.78x, webster: 3.42x
    BinaryPatterns,        // mozilla: 2.77x, samba: 4.34x
    MixedContent,          // reymont: 3.56x, osdb: 2.88x
    
    // Low compression patterns
    AlreadyCompressed,     // x-ray: 1.40x, sao: 1.36x
    RandomData,            // High entropy, low compression
    EncryptedData,         // Encrypted content
    
    // Structural patterns
    RepetitiveSequences,   // LZ77 opportunities
    NullPadding,           // RLE opportunities
    StructuredData,        // Regular intervals
    HeaderTrailer,         // File headers/trailers
}

/// Enhanced pattern information with Silesia-based insights
#[derive(Debug, Clone)]
pub struct EnhancedPatternInfo {
    pub pattern_type: EnhancedPatternType,
    pub frequency: usize,
    pub size: usize,
    pub compression_ratio: f64,
    pub confidence: f64,
    pub locations: Vec<usize>,
    pub silesia_baseline: Option<f64>, // Compression ratio from Silesia Corpus
    pub metadata: HashMap<String, String>,
}

/// Enhanced compression strategy with real-world performance data
#[derive(Debug, Clone)]
pub struct EnhancedCompressionStrategy {
    pub primary_algorithm: String,
    pub secondary_algorithm: Option<String>,
    pub estimated_ratio: f64,
    pub confidence: f64,
    pub reasoning: Vec<String>,
    pub parameters: HashMap<String, String>,
    pub silesia_comparison: Option<f64>, // How this compares to Silesia results
    pub performance_notes: Vec<String>,
}

/// Enhanced pattern analysis result
#[derive(Debug, Clone)]
pub struct EnhancedPatternAnalysisResult {
    pub file_path: String,
    pub file_size: u64,
    pub patterns_found: Vec<EnhancedPatternInfo>,
    pub recommended_strategy: EnhancedCompressionStrategy,
    pub analysis_time: u128,
    pub memory_used: usize,
    pub silesia_benchmark: Option<SilesiaBenchmark>,
}

/// Silesia Corpus benchmark data
#[derive(Debug, Clone)]
pub struct SilesiaBenchmark {
    pub best_ratio: f64,
    pub best_method: String,
    pub average_ratio: f64,
    pub performance_notes: Vec<String>,
}

/// Enhanced configuration for pattern recognition
#[derive(Debug, Clone)]
pub struct EnhancedPatternRecognitionConfig {
    pub min_pattern_size: usize,
    pub max_pattern_size: usize,
    pub min_frequency: usize,
    pub confidence_threshold: f64,
    pub max_patterns_per_file: usize,
    pub memory_limit_mb: usize,
    pub enable_deep_analysis: bool,
    pub use_silesia_baselines: bool,
    pub performance_threshold: f64, // Minimum compression ratio to consider
}

/// Enhanced pattern template with Silesia insights
#[derive(Debug, Clone)]
struct EnhancedPatternTemplate {
    signature: Vec<u8>,
    min_size: usize,
    max_size: usize,
    expected_compression: f64,
    algorithm_suggestions: Vec<String>,
    silesia_examples: Vec<String>, // Example files from Silesia Corpus
    compression_notes: String,
}

impl Default for EnhancedPatternRecognitionConfig {
    fn default() -> Self {
        Self {
            min_pattern_size: 8,
            max_pattern_size: 1024,
            min_frequency: 3,
            confidence_threshold: 0.7,
            max_patterns_per_file: 20,
            memory_limit_mb: 100,
            enable_deep_analysis: true,
            use_silesia_baselines: true,
            performance_threshold: 1.5, // Only consider patterns with 1.5x+ compression
        }
    }
}

/// Enhanced pattern recognition engine
pub struct EnhancedPatternRecognitionEngine {
    config: EnhancedPatternRecognitionConfig,
    pattern_database: HashMap<EnhancedPatternType, EnhancedPatternTemplate>,
    silesia_baselines: HashMap<String, SilesiaBenchmark>,
}

impl EnhancedPatternRecognitionEngine {
    /// Create a new enhanced pattern recognition engine
    pub fn new(config: EnhancedPatternRecognitionConfig) -> Self {
        let mut engine = Self {
            config,
            pattern_database: HashMap::new(),
            silesia_baselines: HashMap::new(),
        };
        engine.initialize_pattern_database();
        engine.initialize_silesia_baselines();
        engine
    }
    
    /// Initialize the enhanced pattern recognition database
    fn initialize_pattern_database(&mut self) {
        // Database patterns (highest compression from Silesia)
        self.pattern_database.insert(EnhancedPatternType::DatabasePatterns, EnhancedPatternTemplate {
            signature: vec![],
            min_size: 32,
            max_size: 1024,
            expected_compression: 10.0, // Based on nci: 11.80x, xml: 8.36x
            algorithm_suggestions: vec!["ZSTD".to_string(), "LZ77".to_string(), "Dictionary".to_string()],
            silesia_examples: vec!["nci".to_string(), "xml".to_string()],
            compression_notes: "Database files show highest compression potential".to_string(),
        });
        
        // Text patterns (good compression from Silesia)
        self.pattern_database.insert(EnhancedPatternType::TextPatterns, EnhancedPatternTemplate {
            signature: vec![],
            min_size: 16,
            max_size: 512,
            expected_compression: 3.0, // Based on dickens: 2.78x, webster: 3.42x
            algorithm_suggestions: vec!["ZSTD".to_string(), "LZ77".to_string(), "Huffman".to_string()],
            silesia_examples: vec!["dickens".to_string(), "webster".to_string(), "reymont".to_string()],
            compression_notes: "Text files compress well with LZ77 and Huffman".to_string(),
        });
        
        // Binary patterns (moderate compression from Silesia)
        self.pattern_database.insert(EnhancedPatternType::BinaryPatterns, EnhancedPatternTemplate {
            signature: vec![],
            min_size: 8,
            max_size: 256,
            expected_compression: 2.5, // Based on mozilla: 2.77x, samba: 4.34x
            algorithm_suggestions: vec!["ZSTD".to_string(), "LZ77".to_string(), "Dictionary".to_string()],
            silesia_examples: vec!["mozilla".to_string(), "samba".to_string(), "osdb".to_string()],
            compression_notes: "Binary files show moderate compression potential".to_string(),
        });
        
        // Mixed content patterns
        self.pattern_database.insert(EnhancedPatternType::MixedContent, EnhancedPatternTemplate {
            signature: vec![],
            min_size: 16,
            max_size: 512,
            expected_compression: 2.0, // Based on mixed content files
            algorithm_suggestions: vec!["ZSTD".to_string(), "LZ77".to_string()],
            silesia_examples: vec!["mr".to_string(), "ooffice".to_string()],
            compression_notes: "Mixed content requires adaptive compression".to_string(),
        });
        
        // Low compression patterns
        self.pattern_database.insert(EnhancedPatternType::AlreadyCompressed, EnhancedPatternTemplate {
            signature: vec![],
            min_size: 8,
            max_size: 128,
            expected_compression: 1.3, // Based on x-ray: 1.40x, sao: 1.36x
            algorithm_suggestions: vec!["Skip".to_string(), "Minimal".to_string()],
            silesia_examples: vec!["x-ray".to_string(), "sao".to_string()],
            compression_notes: "Already compressed files show minimal gains".to_string(),
        });
        
        // Structural patterns
        self.pattern_database.insert(EnhancedPatternType::RepetitiveSequences, EnhancedPatternTemplate {
            signature: vec![],
            min_size: 8,
            max_size: 256,
            expected_compression: 0.8,
            algorithm_suggestions: vec!["LZ77".to_string(), "LZ78".to_string()],
            silesia_examples: vec![],
            compression_notes: "Repetitive sequences compress well with LZ algorithms".to_string(),
        });
        
        self.pattern_database.insert(EnhancedPatternType::NullPadding, EnhancedPatternTemplate {
            signature: vec![0x00],
            min_size: 16,
            max_size: 1024,
            expected_compression: 0.95,
            algorithm_suggestions: vec!["RLE".to_string(), "LZ77".to_string()],
            silesia_examples: vec![],
            compression_notes: "Null padding compresses extremely well with RLE".to_string(),
        });
    }
    
    /// Initialize Silesia Corpus baseline data
    fn initialize_silesia_baselines(&mut self) {
        // Database files (highest compression)
        self.silesia_baselines.insert("database".to_string(), SilesiaBenchmark {
            best_ratio: 11.80,
            best_method: "ZSTD".to_string(),
            average_ratio: 10.08,
            performance_notes: vec![
                "Database files show exceptional compression".to_string(),
                "ZSTD provides best overall performance".to_string(),
                "XML and NCI files compress extremely well".to_string(),
            ],
        });
        
        // Text files (good compression)
        self.silesia_baselines.insert("text".to_string(), SilesiaBenchmark {
            best_ratio: 3.56,
            best_method: "ZLIB".to_string(),
            average_ratio: 3.03,
            performance_notes: vec![
                "Text files compress well with all methods".to_string(),
                "ZLIB and ZSTD provide similar results".to_string(),
                "Language-specific optimizations possible".to_string(),
            ],
        });
        
        // Binary files (moderate compression)
        self.silesia_baselines.insert("binary".to_string(), SilesiaBenchmark {
            best_ratio: 4.34,
            best_method: "ZSTD".to_string(),
            average_ratio: 3.56,
            performance_notes: vec![
                "Binary files show moderate compression".to_string(),
                "ZSTD provides best speed/compression balance".to_string(),
                "LZ4 offers fastest processing".to_string(),
            ],
        });
        
        // Mixed content (variable compression)
        self.silesia_baselines.insert("mixed".to_string(), SilesiaBenchmark {
            best_ratio: 2.88,
            best_method: "ZSTD".to_string(),
            average_ratio: 2.45,
            performance_notes: vec![
                "Mixed content requires adaptive strategies".to_string(),
                "ZSTD handles diverse content well".to_string(),
                "Content-aware selection improves results".to_string(),
            ],
        });
    }
    
    /// Analyze a file for enhanced compression patterns with SIMPLE SPINNER
    pub fn analyze_file_with_spinner(&self, file_path: &Path) -> Result<EnhancedPatternAnalysisResult, Box<dyn std::error::Error>> {
        let start_time = Instant::now();
        
        // Start spinner for file analysis
        let spinner = MMHRSSpinner::new("Analyzing file patterns...");
        spinner.start();
        
        let mut file = File::open(file_path)?;
        let metadata = file.metadata()?;
        let file_size = metadata.len();
        
        // Read file content
        let mut buffer = Vec::new();
        file.read_to_end(&mut buffer)?;
        let memory_used = buffer.len();
        
        // Update spinner message
        spinner.stop();
        let spinner = MMHRSSpinner::new("Detecting patterns...");
        spinner.start();
        
        // Perform enhanced pattern recognition
        let patterns = self.recognize_enhanced_patterns(&buffer)?;
        
        // Update spinner message
        spinner.stop();
        let spinner = MMHRSSpinner::new("Generating compression strategy...");
        spinner.start();
        
        // Generate enhanced compression strategy
        let strategy = self.generate_enhanced_compression_strategy(&patterns, file_size)?;
        
        // Get Silesia benchmark if applicable
        let silesia_benchmark = self.get_silesia_benchmark(&patterns);
        
        let analysis_time = start_time.elapsed().as_millis();
        
        // Finish with success message
        spinner.finish_with_message(&format!("Analysis complete for {} in {}ms", 
            file_path.file_name().unwrap().to_string_lossy(), analysis_time));
        
        Ok(EnhancedPatternAnalysisResult {
            file_path: file_path.to_string_lossy().to_string(),
            file_size,
            patterns_found: patterns,
            recommended_strategy: strategy,
            analysis_time,
            memory_used,
            silesia_benchmark,
        })
    }
    
    /// Analyze a file for enhanced compression patterns with REAL-TIME ANIMATION
    pub fn analyze_file(&self, file_path: &Path, progress: Option<Arc<Mutex<MMHRSProgress>>>) -> Result<EnhancedPatternAnalysisResult, Box<dyn std::error::Error>> {
        let start_time = Instant::now();
        
        // Update progress if available
        if let Some(progress) = &progress {
            let mut prog = progress.lock().unwrap();
            prog.update_file(file_path.file_name().unwrap().to_string_lossy().as_ref());
            prog.update_operation("Analyzing patterns...");
            prog.display_progress();
        }
        
        let mut file = File::open(file_path)?;
        let metadata = file.metadata()?;
        let file_size = metadata.len();
        
        // Read file content for analysis with progress updates
        let mut buffer = Vec::new();
        let chunk_size = 1024 * 1024; // 1MB chunks
        let mut bytes_read = 0;
        
        loop {
            let mut chunk = vec![0u8; chunk_size.min(file_size as usize - bytes_read)];
            let n = file.read(&mut chunk)?;
            if n == 0 { break; }
            
            buffer.extend_from_slice(&chunk[..n]);
            bytes_read += n;
            
            // Update progress during file reading
            if let Some(progress) = &progress {
                let mut prog = progress.lock().unwrap();
                prog.update_file_progress(bytes_read as f64 / file_size as f64 * 0.3); // Reading is 30% of work
                prog.display_progress();
            }
            
            // Small delay to show progress
            thread::sleep(Duration::from_millis(10));
        }
        
        let memory_used = buffer.len();
        
        // Update progress for pattern recognition
        if let Some(progress) = &progress {
            let mut prog = progress.lock().unwrap();
            prog.update_operation("Recognizing patterns...");
            prog.update_file_progress(0.3); // Start pattern recognition at 30%
            prog.display_progress();
        }
        
        // Perform enhanced pattern recognition with progress updates
        let patterns = self.recognize_enhanced_patterns_with_progress(&buffer, &progress)?;
        
        // Update progress for strategy generation
        if let Some(progress) = &progress {
            let mut prog = progress.lock().unwrap();
            prog.update_operation("Generating strategy...");
            prog.update_file_progress(0.7); // Strategy generation at 70%
            prog.display_progress();
        }
        
        // Generate enhanced compression strategy
        let strategy = self.generate_enhanced_compression_strategy(&patterns, file_size)?;
        
        // Get Silesia benchmark if applicable
        let silesia_benchmark = self.get_silesia_benchmark(&patterns);
        
        let analysis_time = start_time.elapsed().as_millis();
        
        // Mark file as completed
        if let Some(progress) = &progress {
            let mut prog = progress.lock().unwrap();
            prog.file_completed();
            prog.display_progress();
        }
        
        Ok(EnhancedPatternAnalysisResult {
            file_path: file_path.to_string_lossy().to_string(),
            file_size,
            patterns_found: patterns,
            recommended_strategy: strategy,
            analysis_time,
            memory_used,
            silesia_benchmark,
        })
    }
    
    /// Recognize enhanced patterns in data with progress tracking
    pub fn recognize_enhanced_patterns_with_progress(&self, data: &[u8], progress: &Option<Arc<Mutex<MMHRSProgress>>>) -> Result<Vec<EnhancedPatternInfo>, Box<dyn std::error::Error>> {
        let mut patterns = Vec::new();
        let total_pattern_types = 8; // Total number of pattern detection functions
        let mut completed_patterns = 0;
        
        // 1. Detect database patterns (highest priority)
        if let Some(database) = self.detect_database_patterns(data)? {
            patterns.push(database);
        }
        completed_patterns += 1;
        self.update_pattern_progress(progress, completed_patterns, total_pattern_types, 0.3, 0.5);
        
        // 2. Detect text patterns
        if let Some(text) = self.detect_enhanced_text_patterns(data)? {
            patterns.push(text);
        }
        completed_patterns += 1;
        self.update_pattern_progress(progress, completed_patterns, total_pattern_types, 0.3, 0.5);
        
        // 3. Detect binary patterns
        if let Some(binary) = self.detect_enhanced_binary_patterns(data)? {
            patterns.push(binary);
        }
        completed_patterns += 1;
        self.update_pattern_progress(progress, completed_patterns, total_pattern_types, 0.3, 0.5);
        
        // 4. Detect mixed content patterns
        if let Some(mixed) = self.detect_mixed_content_patterns(data)? {
            patterns.push(mixed);
        }
        completed_patterns += 1;
        self.update_pattern_progress(progress, completed_patterns, total_pattern_types, 0.3, 0.5);
        
        // 5. Detect already compressed patterns
        if let Some(compressed) = self.detect_already_compressed_patterns(data)? {
            patterns.push(compressed);
        }
        completed_patterns += 1;
        self.update_pattern_progress(progress, completed_patterns, total_pattern_types, 0.3, 0.5);
        
        // 6. Detect structural patterns
        if let Some(repetitive) = self.detect_repetitive_sequences(data)? {
            patterns.push(repetitive);
        }
        completed_patterns += 1;
        self.update_pattern_progress(progress, completed_patterns, total_pattern_types, 0.3, 0.5);
        
        if let Some(null_padding) = self.detect_null_padding(data)? {
            patterns.push(null_padding);
        }
        completed_patterns += 1;
        self.update_pattern_progress(progress, completed_patterns, total_pattern_types, 0.3, 0.5);
        
        // Limit patterns based on configuration
        if patterns.len() > self.config.max_patterns_per_file {
            patterns.truncate(self.config.max_patterns_per_file);
        }
        
        Ok(patterns)
    }
    
    /// Update pattern recognition progress
    fn update_pattern_progress(&self, progress: &Option<Arc<Mutex<MMHRSProgress>>>, completed: usize, total: usize, start_progress: f64, end_progress: f64) {
        if let Some(progress) = progress {
            let mut prog = progress.lock().unwrap();
            let pattern_progress = start_progress + (completed as f64 / total as f64) * (end_progress - start_progress);
            prog.update_file_progress(pattern_progress);
            prog.display_progress();
        }
        
        // Small delay to show progress
        thread::sleep(Duration::from_millis(25));
    }
    
    /// Detect database patterns (highest compression potential)
    fn detect_database_patterns(&self, data: &[u8]) -> Result<Option<EnhancedPatternInfo>, Box<dyn std::error::Error>> {
        // Look for database-specific patterns
        let mut database_indicators = 0;
        
        // Check for structured data patterns
        if self.has_regular_structure(data) {
            database_indicators += 1;
        }
        
        // Check for repeated field patterns
        if self.has_repeated_fields(data) {
            database_indicators += 1;
        }
        
        // Check for numeric sequences
        if self.has_numeric_sequences(data) {
            database_indicators += 1;
        }
        
        if database_indicators >= 2 {
            let compression_ratio = 10.0; // Based on Silesia nci: 11.80x, xml: 8.36x
            let confidence = 0.9;
            
            Ok(Some(EnhancedPatternInfo {
                pattern_type: EnhancedPatternType::DatabasePatterns,
                frequency: 1,
                size: data.len(),
                compression_ratio,
                confidence,
                locations: vec![0],
                silesia_baseline: Some(10.08), // Average from Silesia database files
                metadata: HashMap::new(),
            }))
        } else {
            Ok(None)
        }
    }
    
    /// Detect enhanced text patterns
    fn detect_enhanced_text_patterns(&self, data: &[u8]) -> Result<Option<EnhancedPatternInfo>, Box<dyn std::error::Error>> {
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
                let compression_ratio = 3.0; // Based on Silesia text files
                let confidence = text_ratio;
                
                Ok(Some(EnhancedPatternInfo {
                    pattern_type: EnhancedPatternType::TextPatterns,
                    frequency: *frequency,
                    size: pattern.len(),
                    compression_ratio,
                    confidence,
                    locations: vec![0],
                    silesia_baseline: Some(3.03), // Average from Silesia text files
                    metadata: HashMap::new(),
                }))
            } else {
                Ok(None)
            }
        } else {
            Ok(None)
        }
    }
    
    /// Detect enhanced binary patterns
    fn detect_enhanced_binary_patterns(&self, data: &[u8]) -> Result<Option<EnhancedPatternInfo>, Box<dyn std::error::Error>> {
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
            let compression_ratio = 2.5; // Based on Silesia binary files
            let confidence = (*frequency as f64 / (data.len() as f64 / pattern.len() as f64)).min(1.0);
            
            Ok(Some(EnhancedPatternInfo {
                pattern_type: EnhancedPatternType::BinaryPatterns,
                frequency: *frequency,
                size: pattern.len(),
                compression_ratio,
                confidence,
                locations: vec![0],
                silesia_baseline: Some(3.56), // Average from Silesia binary files
                metadata: HashMap::new(),
            }))
        } else {
            Ok(None)
        }
    }
    
    /// Detect mixed content patterns
    fn detect_mixed_content_patterns(&self, data: &[u8]) -> Result<Option<EnhancedPatternInfo>, Box<dyn std::error::Error>> {
        let text_bytes: usize = data.iter()
            .filter(|&&b| b.is_ascii_alphabetic() || b.is_ascii_whitespace() || b.is_ascii_punctuation())
            .count();
        
        let text_ratio = text_bytes as f64 / data.len() as f64;
        
        // Mixed content has text ratio between 0.3 and 0.7
        if text_ratio >= 0.3 && text_ratio <= 0.7 {
            let compression_ratio = 2.0; // Based on Silesia mixed content files
            let confidence = 0.7;
            
            Ok(Some(EnhancedPatternInfo {
                pattern_type: EnhancedPatternType::MixedContent,
                frequency: 1,
                size: data.len(),
                compression_ratio,
                confidence,
                locations: vec![0],
                silesia_baseline: Some(2.45), // Average from Silesia mixed content files
                metadata: HashMap::new(),
            }))
        } else {
            Ok(None)
        }
    }
    
    /// Detect already compressed patterns
    fn detect_already_compressed_patterns(&self, data: &[u8]) -> Result<Option<EnhancedPatternInfo>, Box<dyn std::error::Error>> {
        // Check for high entropy (already compressed)
        let entropy = self.calculate_entropy(data);
        
        if entropy > 7.5 { // High entropy indicates already compressed
            let compression_ratio = 1.3; // Based on Silesia already compressed files
            let confidence = 0.8;
            
            Ok(Some(EnhancedPatternInfo {
                pattern_type: EnhancedPatternType::AlreadyCompressed,
                frequency: 1,
                size: data.len(),
                compression_ratio,
                confidence,
                locations: vec![0],
                silesia_baseline: Some(1.38), // Average from Silesia already compressed files
                metadata: HashMap::new(),
            }))
        } else {
            Ok(None)
        }
    }
    
    /// Detect repetitive sequences
    fn detect_repetitive_sequences(&self, data: &[u8]) -> Result<Option<EnhancedPatternInfo>, Box<dyn std::error::Error>> {
        let mut sequences = HashMap::new();
        
        for size in self.config.min_pattern_size..=self.config.max_pattern_size.min(data.len() / 2) {
            for start in 0..=data.len() - size {
                let sequence = &data[start..start + size];
                let count = sequences.entry(sequence.to_vec()).or_insert(0);
                *count += 1;
            }
        }
        
        let mut best_sequence = None;
        let mut best_frequency = 0;
        
        for (sequence, frequency) in sequences {
            if frequency >= self.config.min_frequency && frequency > best_frequency {
                best_sequence = Some((sequence, frequency));
                best_frequency = frequency;
            }
        }
        
        if let Some((sequence, frequency)) = best_sequence {
            let compression_ratio = 0.8;
            let confidence = (frequency as f64 / (data.len() as f64 / sequence.len() as f64)).min(1.0);
            
            Ok(Some(EnhancedPatternInfo {
                pattern_type: EnhancedPatternType::RepetitiveSequences,
                frequency,
                size: sequence.len(),
                compression_ratio,
                confidence,
                locations: vec![0],
                silesia_baseline: None,
                metadata: HashMap::new(),
            }))
        } else {
            Ok(None)
        }
    }
    
    /// Detect null padding
    fn detect_null_padding(&self, data: &[u8]) -> Result<Option<EnhancedPatternInfo>, Box<dyn std::error::Error>> {
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
        
        if let Some(start) = current_block_start {
            let block_size = data.len() - start;
            if block_size >= self.config.min_pattern_size {
                null_blocks.push((start, block_size));
            }
        }
        
        if null_blocks.is_empty() {
            return Ok(None);
        }
        
        let total_null_bytes: usize = null_blocks.iter().map(|(_, size)| size).sum();
        let compression_ratio = total_null_bytes as f64 / data.len() as f64;
        let confidence = if compression_ratio > 0.1 { 0.9 } else { 0.5 };
        
        Ok(Some(EnhancedPatternInfo {
            pattern_type: EnhancedPatternType::NullPadding,
            frequency: null_blocks.len(),
            size: total_null_bytes,
            compression_ratio,
            confidence,
            locations: null_blocks.iter().map(|(start, _)| *start).collect(),
            silesia_baseline: None,
            metadata: HashMap::new(),
        }))
    }
    
    /// Helper methods for pattern detection
    fn has_regular_structure(&self, data: &[u8]) -> bool {
        // Check for regular intervals in data
        if data.len() < 64 {
            return false;
        }
        
        for interval in 16..=64 {
            if interval > data.len() / 4 {
                break;
            }
            
            let mut regular_count = 0;
            let mut total_checks = 0;
            
            for i in (0..data.len() - interval).step_by(interval) {
                if i + interval < data.len() {
                    total_checks += 1;
                    // Check if there's some regularity
                    if data[i] == data[i + interval] || 
                       (data[i] as i32 - data[i + interval] as i32).abs() < 10 {
                        regular_count += 1;
                    }
                }
            }
            
            if total_checks > 0 && (regular_count as f64 / total_checks as f64) > 0.6 {
                return true;
            }
        }
        
        false
    }
    
    fn has_repeated_fields(&self, data: &[u8]) -> bool {
        // Look for repeated field-like structures
        if data.len() < 32 {
            return false;
        }
        
        let mut field_counts = HashMap::new();
        
        for field_size in 4..=16 {
            for start in 0..=data.len() - field_size {
                let field = &data[start..start + field_size];
                let count = field_counts.entry(field.to_vec()).or_insert(0);
                *count += 1;
            }
        }
        
        // Check if any field appears multiple times
        field_counts.values().any(|&count| count >= 3)
    }
    
    fn has_numeric_sequences(&self, data: &[u8]) -> bool {
        // Look for numeric sequences (ASCII digits)
        let mut digit_sequences = 0;
        let mut total_sequences = 0;
        
        for chunk in data.chunks(8) {
            if chunk.len() == 8 {
                total_sequences += 1;
                if chunk.iter().all(|&b| b.is_ascii_digit()) {
                    digit_sequences += 1;
                }
            }
        }
        
        total_sequences > 0 && (digit_sequences as f64 / total_sequences as f64) > 0.3
    }
    
    fn calculate_entropy(&self, data: &[u8]) -> f64 {
        if data.is_empty() {
            return 0.0;
        }
        
        let mut byte_counts = [0u32; 256];
        for &byte in data {
            byte_counts[byte as usize] += 1;
        }
        
        let len = data.len() as f64;
        let mut entropy = 0.0;
        
        for &count in byte_counts.iter() {
            if count > 0 {
                let probability = count as f64 / len;
                entropy -= probability * probability.log2();
            }
        }
        
        entropy
    }
    
    /// Generate enhanced compression strategy
    fn generate_enhanced_compression_strategy(&self, patterns: &[EnhancedPatternInfo], file_size: u64) -> Result<EnhancedCompressionStrategy, Box<dyn std::error::Error>> {
        if patterns.is_empty() {
            return Ok(EnhancedCompressionStrategy {
                primary_algorithm: "ZSTD".to_string(),
                secondary_algorithm: None,
                estimated_ratio: 2.0,
                confidence: 0.3,
                reasoning: vec!["No specific patterns detected, using default ZSTD".to_string()],
                parameters: HashMap::new(),
                silesia_comparison: None,
                performance_notes: vec!["Default strategy for unknown content".to_string()],
            });
        }
        
        // Find the best pattern
        let best_pattern = patterns.iter()
            .max_by(|a, b| a.compression_ratio.partial_cmp(&b.compression_ratio).unwrap())
            .unwrap();
        
        // Determine primary algorithm based on pattern type and Silesia results
        let (primary_algorithm, estimated_ratio) = match best_pattern.pattern_type {
            EnhancedPatternType::DatabasePatterns => ("ZSTD", best_pattern.compression_ratio),
            EnhancedPatternType::TextPatterns => ("ZSTD", best_pattern.compression_ratio),
            EnhancedPatternType::BinaryPatterns => ("ZSTD", best_pattern.compression_ratio),
            EnhancedPatternType::MixedContent => ("ZSTD", best_pattern.compression_ratio),
            EnhancedPatternType::AlreadyCompressed => ("Skip", 1.0),
            EnhancedPatternType::RepetitiveSequences => ("LZ77", best_pattern.compression_ratio),
            EnhancedPatternType::NullPadding => ("RLE", best_pattern.compression_ratio),
            _ => ("ZSTD", best_pattern.compression_ratio),
        };
        
        // Determine secondary algorithm
        let secondary_algorithm = match primary_algorithm {
            "ZSTD" => Some("LZ77".to_string()),
            "LZ77" => Some("Huffman".to_string()),
            "RLE" => Some("LZ77".to_string()),
            _ => None,
        };
        
        // Generate reasoning
        let mut reasoning = Vec::new();
        reasoning.push(format!("Detected {:?} pattern with {:.1}% confidence", 
            best_pattern.pattern_type, best_pattern.confidence * 100.0));
        reasoning.push(format!("Pattern size: {} bytes, frequency: {}", 
            best_pattern.size, best_pattern.frequency));
        reasoning.push(format!("Estimated compression ratio: {:.1}x", 
            best_pattern.compression_ratio));
        
        if let Some(baseline) = best_pattern.silesia_baseline {
            reasoning.push(format!("Silesia Corpus baseline: {:.1}x average", baseline));
        }
        
        // Set parameters
        let mut parameters = HashMap::new();
        parameters.insert("window_size".to_string(), "32768".to_string());
        parameters.insert("min_match_length".to_string(), "3".to_string());
        parameters.insert("max_match_length".to_string(), "258".to_string());
        
        // Performance notes
        let mut performance_notes = Vec::new();
        if let Some(baseline) = best_pattern.silesia_baseline {
            if best_pattern.compression_ratio > baseline {
                performance_notes.push(format!("Expected to exceed Silesia baseline of {:.1}x", baseline));
            } else {
                performance_notes.push(format!("Targeting Silesia baseline of {:.1}x", baseline));
            }
        }
        
        performance_notes.push("ZSTD provides best speed/compression balance".to_string());
        
        Ok(EnhancedCompressionStrategy {
            primary_algorithm: primary_algorithm.to_string(),
            secondary_algorithm,
            estimated_ratio,
            confidence: best_pattern.confidence,
            reasoning,
            parameters,
            silesia_comparison: best_pattern.silesia_baseline,
            performance_notes,
        })
    }
    
    /// Get Silesia benchmark for patterns
    fn get_silesia_benchmark(&self, patterns: &[EnhancedPatternInfo]) -> Option<SilesiaBenchmark> {
        if patterns.is_empty() {
            return None;
        }
        
        // Find the best pattern and get its category
        let best_pattern = patterns.iter()
            .max_by(|a, b| a.compression_ratio.partial_cmp(&b.compression_ratio).unwrap())
            .unwrap();
        
        let category = match best_pattern.pattern_type {
            EnhancedPatternType::DatabasePatterns => "database",
            EnhancedPatternType::TextPatterns => "text",
            EnhancedPatternType::BinaryPatterns => "binary",
            EnhancedPatternType::MixedContent => "mixed",
            _ => return None,
        };
        
        self.silesia_baselines.get(category).cloned()
    }
}

/// Display enhanced pattern analysis results
pub fn display_enhanced_pattern_analysis(result: &EnhancedPatternAnalysisResult) {
    println!("\n🔍 Enhanced Pattern Analysis Results for: {}", result.file_path);
    println!("📏 File Size: {:.2} MB", result.file_size as f64 / (1024.0 * 1024.0));
    println!("⏱️  Analysis Time: {} ms", result.analysis_time);
    println!("🧠 Memory Used: {:.2} MB", result.memory_used as f64 / (1024.0 * 1024.0));
    
    println!("\n📊 Enhanced Patterns Found: {} patterns", result.patterns_found.len());
    for (i, pattern) in result.patterns_found.iter().enumerate() {
        println!("  {}. {:?}", i + 1, pattern.pattern_type);
        println!("     Size: {} bytes, Frequency: {}", pattern.size, pattern.frequency);
        println!("     Compression Ratio: {:.1}x, Confidence: {:.1}%", 
            pattern.compression_ratio, pattern.confidence * 100.0);
        
        if let Some(baseline) = pattern.silesia_baseline {
            println!("     Silesia Baseline: {:.1}x average", baseline);
        }
    }
    
    println!("\n🎯 Enhanced Compression Strategy:");
    println!("  Primary Algorithm: {}", result.recommended_strategy.primary_algorithm);
    if let Some(ref secondary) = result.recommended_strategy.secondary_algorithm {
        println!("  Secondary Algorithm: {}", secondary);
    }
    println!("  Estimated Compression Ratio: {:.1}x", 
        result.recommended_strategy.estimated_ratio);
    println!("  Confidence: {:.1}%", result.recommended_strategy.confidence * 100.0);
    
    if let Some(comparison) = result.recommended_strategy.silesia_comparison {
        println!("  Silesia Comparison: {:.1}x baseline", comparison);
    }
    
    println!("\n💡 Reasoning:");
    for reason in &result.recommended_strategy.reasoning {
        println!("  → {}", reason);
    }
    
    println!("\n🚀 Performance Notes:");
    for note in &result.recommended_strategy.performance_notes {
        println!("  → {}", note);
    }
    
    if let Some(ref benchmark) = result.silesia_benchmark {
        println!("\n📊 Silesia Corpus Benchmark:");
        println!("  Best Ratio: {:.1}x with {}", benchmark.best_ratio, benchmark.best_method);
        println!("  Average Ratio: {:.1}x", benchmark.average_ratio);
        println!("  Notes:");
        for note in &benchmark.performance_notes {
            println!("    → {}", note);
        }
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
    fn test_enhanced_engine_creation() {
        let config = EnhancedPatternRecognitionConfig::default();
        let engine = EnhancedPatternRecognitionEngine::new(config);
        assert!(!engine.pattern_database.is_empty());
        assert!(!engine.silesia_baselines.is_empty());
    }
    
    #[test]
    fn test_database_pattern_detection() {
        let config = EnhancedPatternRecognitionConfig::default();
        let engine = EnhancedPatternRecognitionEngine::new(config);
        
        // Create test data with database-like patterns
        let mut test_data = Vec::new();
        for i in 0..100 {
            test_data.extend_from_slice(&format!("{:08}", i).as_bytes());
        }
        
        let patterns = engine.recognize_enhanced_patterns_with_progress(&test_data, &None).unwrap();
        let database_pattern = patterns.iter().find(|p| matches!(p.pattern_type, EnhancedPatternType::DatabasePatterns));
        
        assert!(database_pattern.is_some());
        if let Some(pattern) = database_pattern {
            assert!(pattern.compression_ratio >= 10.0);
            assert!(pattern.silesia_baseline.is_some());
        }
    }
    
    #[test]
    fn test_entropy_calculation() {
        let config = EnhancedPatternRecognitionConfig::default();
        let engine = EnhancedPatternRecognitionEngine::new(config);
        
        // Low entropy data (repetitive)
        let low_entropy = vec![0x00; 100];
        let low_entropy_value = engine.calculate_entropy(&low_entropy);
        assert!(low_entropy_value < 2.0);
        
        // High entropy data (random)
        let high_entropy: Vec<u8> = (0..100).map(|i| (i * 7) % 256).collect();
        let high_entropy_value = engine.calculate_entropy(&high_entropy);
        assert!(high_entropy_value > 7.0);
    }
}
