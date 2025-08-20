// Universal Compression Champion - MMH-RS Multi-Format Analyzer
use std::collections::{HashMap, HashSet};
use std::time::{Instant, Duration};
use std::fs;
use std::path::{Path, PathBuf};
use std::env;

/// Configuration for the universal compression analyzer
#[derive(Debug, Clone)]
pub struct UniversalAnalyzerConfig {
    pub min_pattern_length: usize,
    pub max_pattern_length: usize,
    pub threshold: f64,
    pub max_file_size_mb: usize,
    pub target_compression_potential: f64,
    pub sample_size_mb: usize,
    pub supported_extensions: Vec<String>,
}

impl Default for UniversalAnalyzerConfig {
    fn default() -> Self {
        Self {
            min_pattern_length: 4,
            max_pattern_length: 251,
            threshold: 0.03,
            max_file_size_mb: 500,
            target_compression_potential: 8000.0,
            sample_size_mb: 10,
            supported_extensions: vec![
                // Executables and binaries
                "exe".to_string(), "dll".to_string(), "so".to_string(), "dylib".to_string(), "bin".to_string(), "obj".to_string(), "o".to_string(), "a".to_string(), "lib".to_string(),
                // Debug and symbol files
                "pdb".to_string(), "dbg".to_string(), "map".to_string(), "sym".to_string(),
                // Archives and compressed files
                "zip".to_string(), "rar".to_string(), "7z".to_string(), "tar".to_string(), "gz".to_string(), "bz2".to_string(), "xz".to_string(), "lzma".to_string(),
                // Media files
                "mp3".to_string(), "mp4".to_string(), "avi".to_string(), "mkv".to_string(), "jpg".to_string(), "png".to_string(), "gif".to_string(), "bmp".to_string(), "tiff".to_string(),
                // Document files
                "pdf".to_string(), "doc".to_string(), "docx".to_string(), "xls".to_string(), "xlsx".to_string(), "ppt".to_string(), "pptx".to_string(),
                // Source code and text
                "cpp".to_string(), "c".to_string(), "h".to_string(), "rs".to_string(), "py".to_string(), "js".to_string(), "html".to_string(), "css".to_string(), "xml".to_string(), "json".to_string(),
                // Database files
                "db".to_string(), "sqlite".to_string(), "mdb".to_string(), "accdb".to_string(),
                // Virtual machine files
                "vmdk".to_string(), "vdi".to_string(), "vhd".to_string(), "iso".to_string(),
                // Log files
                "log".to_string(), "txt".to_string(), "csv".to_string(),
                // Custom MMH-RS formats
                "mmh".to_string(), "mmhrs".to_string(), "compressed".to_string()
            ],
        }
    }
}

/// Universal file information for discovery
#[derive(Debug, Clone)]
pub struct UniversalFileInfo {
    pub path: PathBuf,
    pub size_mb: f64,
    pub file_type: FileType,
    pub estimated_potential: f64,
    pub extension: String,
}

/// File type classification
#[derive(Debug, Clone, PartialEq)]
pub enum FileType {
    Executable,
    DebugSymbol,
    Archive,
    Media,
    Document,
    SourceCode,
    Database,
    VirtualMachine,
    Log,
    Custom,
    Unknown,
}

/// Core compression analysis results
#[derive(Debug, Clone)]
pub struct CompressionAnalysis {
    pub file_info: UniversalFileInfo,
    pub compression_metrics: CompressionMetrics,
    pub file_specific_metrics: FileSpecificMetrics,
    pub processing_time: Duration,
    pub recommended_strategy: CompressionStrategy,
}

/// Compression-related metrics (universal)
#[derive(Debug, Clone)]
pub struct CompressionMetrics {
    pub compression_potential: f64,
    pub pattern_complexity: f64,
    pub entropy: f64,
    pub estimated_ratio: f64,
    pub pattern_count: usize,
    pub repetition_ratio: f64,
    pub structural_similarity: f64,
}

/// File-specific metrics for different types
#[derive(Debug, Clone)]
pub struct FileSpecificMetrics {
    pub file_type: FileType,
    pub format_specific_data: FormatSpecificData,
    pub compression_characteristics: CompressionCharacteristics,
}

/// Format-specific data for different file types
#[derive(Debug, Clone)]
pub enum FormatSpecificData {
    Executable {
        entry_points: usize,
        sections: usize,
        imports: usize,
        exports: usize,
    },
    Media {
        codec_type: String,
        bit_depth: u8,
        channels: u8,
        sample_rate: u32,
    },
    Archive {
        compression_method: String,
        file_count: usize,
        compression_level: u8,
    },
    Document {
        page_count: usize,
        embedded_objects: usize,
        text_ratio: f64,
    },
    SourceCode {
        language: String,
        function_count: usize,
        comment_ratio: f64,
    },
    Database {
        table_count: usize,
        index_count: usize,
        data_types: Vec<String>,
    },
    Generic {
        magic_bytes: Vec<u8>,
        header_size: usize,
        footer_size: usize,
    },
}

/// Compression characteristics
#[derive(Debug, Clone)]
pub struct CompressionCharacteristics {
    pub is_already_compressed: bool,
    pub compression_friendly: bool,
    pub has_redundant_data: bool,
    pub structural_patterns: bool,
    pub entropy_distribution: EntropyProfile,
}

/// Entropy profile analysis
#[derive(Debug, Clone)]
pub enum EntropyProfile {
    LowEntropy { value: f64, reason: String },
    MediumEntropy { value: f64, distribution: String },
    HighEntropy { value: f64, randomness: String },
    MixedEntropy { low_regions: f64, high_regions: f64 },
}

/// Enhanced compression strategy recommendation
#[derive(Debug, Clone)]
pub enum CompressionStrategy {
    Champion { 
        techniques: Vec<String>,
        expected_ratio: f64,
        mmh_rs_codec: String,
    },
    HighPerformance { 
        primary: String, 
        secondary: String,
        expected_ratio: f64,
    },
    Standard { 
        technique: String,
        expected_ratio: f64,
    },
    Basic { 
        reason: String,
        expected_ratio: f64,
    },
    AlreadyCompressed { 
        reason: String,
        alternative: String,
    },
}

/// Universal pattern analysis using sampling for large files
#[derive(Debug)]
struct UniversalPatternAnalyzer {
    config: UniversalAnalyzerConfig,
}

impl UniversalPatternAnalyzer {
    fn new(config: UniversalAnalyzerConfig) -> Self {
        Self { config }
    }

    /// Analyze patterns in any data type
    fn analyze_patterns(&self, data: &[u8]) -> CompressionMetrics {
        let sample_data = self.get_sample_data(data);
        let entropy = self.calculate_entropy(&sample_data);
        
        let (pattern_count, compression_potential) = self.detect_patterns_efficiently(&sample_data);
        let pattern_complexity = self.estimate_complexity(&sample_data);
        let repetition_ratio = self.calculate_repetition_ratio(&sample_data);
        let structural_similarity = self.analyze_structural_similarity(&sample_data);
        let estimated_ratio = self.estimate_compression_ratio(compression_potential, entropy, repetition_ratio);

        CompressionMetrics {
            compression_potential,
            pattern_complexity,
            entropy,
            estimated_ratio,
            pattern_count,
            repetition_ratio,
            structural_similarity,
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

    /// Enhanced pattern detection for universal use
    fn detect_patterns_efficiently(&self, data: &[u8]) -> (usize, f64) {
        let mut total_pattern_coverage = 0usize;
        let mut unique_patterns = 0usize;
        
        // Adaptive pattern length detection based on data size
        let lengths_to_check = if data.len() < 1024 {
            vec![4, 8, 16]
        } else if data.len() < 1024 * 1024 {
            vec![4, 8, 16, 32, 64]
        } else {
            vec![4, 8, 16, 32, 64, 128, 256]
        };
        
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

    /// Calculate repetition ratio (how much data repeats)
    fn calculate_repetition_ratio(&self, data: &[u8]) -> f64 {
        if data.len() < 100 { return 0.0; }
        
        let mut repeated_bytes = 0usize;
        let mut total_bytes = 0usize;
        
        // Check for byte-level repetition
        for window_size in [1, 2, 4, 8] {
            if window_size > data.len() / 2 { continue; }
            
            let mut window_counts = HashMap::new();
            for window in data.windows(window_size) {
                *window_counts.entry(window.to_vec()).or_insert(0) += 1;
                total_bytes += 1;
            }
            
            for (_, count) in window_counts {
                if count > 1 {
                    repeated_bytes += count - 1;
                }
            }
        }
        
        if total_bytes == 0 { 0.0 } else { repeated_bytes as f64 / total_bytes as f64 }
    }

    /// Analyze structural similarity in data
    fn analyze_structural_similarity(&self, data: &[u8]) -> f64 {
        if data.len() < 100 { return 0.0; }
        
        let mut similarity_score = 0.0;
        let sample_size = data.len().min(4096);
        let sample = &data[..sample_size];
        
        // Check for structural patterns like headers, footers, repeated structures
        let header_size = 64.min(sample.len() / 4);
        let footer_size = 64.min(sample.len() / 4);
        
        if sample.len() > header_size + footer_size {
            let header = &sample[..header_size];
            let footer = &sample[sample.len() - footer_size..];
            
            // Check if header/footer patterns repeat
            let header_patterns = self.find_patterns(header);
            let footer_patterns = self.find_patterns(footer);
            
            similarity_score += (header_patterns + footer_patterns) as f64 / 2.0;
        }
        
        similarity_score.min(1.0)
    }

    /// Find patterns in a data slice
    fn find_patterns(&self, data: &[u8]) -> usize {
        let mut pattern_count = 0;
        let mut seen_patterns = HashSet::new();
        
        for length in [2, 4, 8] {
            if length > data.len() / 2 { continue; }
            
            for window in data.windows(length) {
                if seen_patterns.contains(window) {
                    pattern_count += 1;
                } else {
                    seen_patterns.insert(window.to_vec());
                }
            }
        }
        
        pattern_count
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

    /// Enhanced compression ratio estimation
    fn estimate_compression_ratio(&self, potential: f64, entropy: f64, repetition: f64) -> f64 {
        let entropy_factor = (8.0 - entropy) / 8.0;
        let potential_factor = (potential / 10000.0).min(1.0);
        let repetition_factor = repetition.min(1.0);
        
        let estimated_compression = entropy_factor * 0.3 + potential_factor * 0.4 + repetition_factor * 0.3;
        (1.0 - estimated_compression).max(0.1).min(0.9)
    }
}

/// Universal file type detector and analyzer
struct UniversalFileAnalyzer;

impl UniversalFileAnalyzer {
    /// Detect file type and extract format-specific information
    fn analyze_file(data: &[u8], extension: &str) -> (FileType, FormatSpecificData) {
        let file_type = Self::detect_file_type(data, extension);
        let format_data = Self::extract_format_data(data, &file_type);
        
        (file_type, format_data)
    }

    /// Detect file type based on magic bytes and extension
    fn detect_file_type(data: &[u8], extension: &str) -> FileType {
        if data.len() < 8 { return FileType::Unknown; }
        
        // Check magic bytes for common formats
        match data {
            // Executables
            [0x4D, 0x5A, ..] => FileType::Executable, // MZ header
            [0x7F, 0x45, 0x4C, 0x46, ..] => FileType::Executable, // ELF header
            [0xFE, 0xED, 0xFA, 0xCE, ..] => FileType::Executable, // Mach-O header
            
            // Archives
            [0x50, 0x4B, 0x03, 0x04, ..] => FileType::Archive, // ZIP
            [0x52, 0x61, 0x72, 0x21, ..] => FileType::Archive, // RAR
            [0x37, 0x7A, 0xBC, 0xAF, ..] => FileType::Archive, // 7Z
            
            // Media files
            [0xFF, 0xFB, ..] | [0xFF, 0xF3, ..] => FileType::Media, // MP3
            [0x00, 0x00, 0x00, 0x18, 0x66, 0x74, 0x79, 0x70, ..] => FileType::Media, // MP4
            
            // Documents
            [0x25, 0x50, 0x44, 0x46, ..] => FileType::Document, // PDF
            [0xD0, 0xCF, 0x11, 0xE0, ..] => FileType::Document, // Office documents
            
            // Source code (text-based, check extension)
            _ if Self::is_text_file(extension) => FileType::SourceCode,
            
            // Debug symbols
            _ if extension == "pdb" => FileType::DebugSymbol,
            
            _ => FileType::Unknown,
        }
    }

    /// Check if file is text-based
    fn is_text_file(extension: &str) -> bool {
        let text_extensions = [
            "txt", "md", "py", "rs", "cpp", "c", "h", "js", "html", "css", 
            "xml", "json", "yaml", "toml", "ini", "cfg", "conf", "log"
        ];
        text_extensions.contains(&extension.to_lowercase().as_str())
    }

    /// Extract format-specific data
    fn extract_format_data(data: &[u8], file_type: &FileType) -> FormatSpecificData {
        match file_type {
            FileType::Executable => Self::analyze_executable(data),
            FileType::Media => Self::analyze_media(data),
            FileType::Archive => Self::analyze_archive(data),
            FileType::Document => Self::analyze_document(data),
            FileType::SourceCode => Self::analyze_source_code(data),
            FileType::Database => Self::analyze_database(data),
            _ => FormatSpecificData::Generic {
                magic_bytes: data.iter().take(8).cloned().collect(),
                header_size: data.len().min(64),
                footer_size: data.len().min(32),
            },
        }
    }

    /// Analyze executable files
    fn analyze_executable(data: &[u8]) -> FormatSpecificData {
        let entry_points = if data.len() > 0x3C {
            let pe_offset = u32::from_le_bytes([data[0x3C], data[0x3D], data[0x3E], data[0x3F]]);
            if pe_offset < data.len() as u32 && pe_offset > 0x3C {
                1 // PE files typically have one entry point
            } else {
                0
            }
        } else {
            0
        };

        FormatSpecificData::Executable {
            entry_points,
            sections: 0, // Would need more complex parsing
            imports: 0,
            exports: 0,
        }
    }

    /// Analyze media files
    fn analyze_media(data: &[u8]) -> FormatSpecificData {
        FormatSpecificData::Media {
            codec_type: "Unknown".to_string(),
            bit_depth: 8,
            channels: 1,
            sample_rate: 44100,
        }
    }

    /// Analyze archive files
    fn analyze_archive(data: &[u8]) -> FormatSpecificData {
        FormatSpecificData::Archive {
            compression_method: "Unknown".to_string(),
            file_count: 0,
            compression_level: 0,
        }
    }

    /// Analyze document files
    fn analyze_document(data: &[u8]) -> FormatSpecificData {
        FormatSpecificData::Document {
            page_count: 0,
            embedded_objects: 0,
            text_ratio: 0.5,
        }
    }

    /// Analyze source code files
    fn analyze_source_code(data: &[u8]) -> FormatSpecificData {
        let text_content = String::from_utf8_lossy(data);
        let lines: Vec<&str> = text_content.lines().collect();
        let comment_lines = lines.iter()
            .filter(|line| line.trim().starts_with("//") || line.trim().starts_with("/*") || line.trim().starts_with("#"))
            .count();
        
        let comment_ratio = if lines.is_empty() { 0.0 } else { comment_lines as f64 / lines.len() as f64 };
        
        FormatSpecificData::SourceCode {
            language: "Unknown".to_string(),
            function_count: 0,
            comment_ratio,
        }
    }

    /// Analyze database files
    fn analyze_database(data: &[u8]) -> FormatSpecificData {
        FormatSpecificData::Database {
            table_count: 0,
            index_count: 0,
            data_types: vec![],
        }
    }
}

/// Enhanced strategy selector for universal compression
struct UniversalStrategySelector;

impl UniversalStrategySelector {
    fn select_strategy(metrics: &CompressionMetrics, file_metrics: &FileSpecificMetrics) -> CompressionStrategy {
        let potential = metrics.compression_potential;
        let complexity = metrics.pattern_complexity;
        let repetition = metrics.repetition_ratio;
        let entropy = metrics.entropy;
        
        // Check if already compressed
        if Self::is_already_compressed(file_metrics) {
            return CompressionStrategy::AlreadyCompressed {
                reason: "File appears to be already compressed".to_string(),
                alternative: "Consider recompression with different algorithm".to_string(),
            };
        }

        match potential {
            p if p >= 8000.0 => CompressionStrategy::Champion {
                techniques: Self::champion_techniques(file_metrics, complexity, repetition),
                expected_ratio: metrics.estimated_ratio,
                mmh_rs_codec: Self::select_mmh_rs_codec(file_metrics, complexity),
            },
            p if p >= 5000.0 => CompressionStrategy::HighPerformance {
                primary: "Dictionary + LZ77 Hybrid".to_string(),
                secondary: "Pattern Matching".to_string(),
                expected_ratio: metrics.estimated_ratio,
            },
            p if p >= 1000.0 => CompressionStrategy::Standard {
                technique: if complexity < 0.5 { "Pattern-based LZ77" } else { "Entropy-based" }.to_string(),
                expected_ratio: metrics.estimated_ratio,
            },
            _ => CompressionStrategy::Basic {
                reason: "Low pattern density, minimal compression benefit".to_string(),
                expected_ratio: metrics.estimated_ratio,
            },
        }
    }

    /// Check if file is already compressed
    fn is_already_compressed(file_metrics: &FileSpecificMetrics) -> bool {
        match &file_metrics.format_specific_data {
            FormatSpecificData::Archive { .. } => true,
            FormatSpecificData::Media { .. } => true,
            _ => false,
        }
    }

    /// Select appropriate MMH-RS codec
    fn select_mmh_rs_codec(file_metrics: &FileSpecificMetrics, complexity: f64) -> String {
        match &file_metrics.format_specific_data {
            FormatSpecificData::Executable { .. } => "Hierarchical Turbo".to_string(),
            FormatSpecificData::SourceCode { .. } => "Pattern Analyzer".to_string(),
            FormatSpecificData::Media { .. } => "Entropy Optimized".to_string(),
            FormatSpecificData::Document { .. } => "Structural Compressor".to_string(),
            _ => "Universal Codec".to_string(),
        }
    }

    /// Generate champion techniques for universal files
    fn champion_techniques(file_metrics: &FileSpecificMetrics, complexity: f64, repetition: f64) -> Vec<String> {
        let mut techniques = Vec::new();
        
        match &file_metrics.format_specific_data {
            FormatSpecificData::Executable { .. } => {
                techniques.push("Symbol Table Compression".to_string());
                techniques.push("Cross-Section Deduplication".to_string());
                techniques.push("Import/Export Optimization".to_string());
            },
            FormatSpecificData::SourceCode { .. } => {
                techniques.push("Token Dictionary".to_string());
                techniques.push("Function Pattern Matching".to_string());
                techniques.push("Comment/Whitespace Optimization".to_string());
            },
            FormatSpecificData::Media { .. } => {
                techniques.push("Frame Delta Compression".to_string());
                techniques.push("Codec-Aware Optimization".to_string());
                techniques.push("Metadata Compression".to_string());
            },
            FormatSpecificData::Document { .. } => {
                techniques.push("Structural Pattern Matching".to_string());
                techniques.push("Font/Image Deduplication".to_string());
                techniques.push("Metadata Compression".to_string());
            },
            _ => {
                if repetition > 0.3 {
                    techniques.push("Repetition Elimination".to_string());
                }
                if complexity < 0.4 {
                    techniques.push("Pattern Dictionary".to_string());
                }
                techniques.push("Universal Pattern Matching".to_string());
            },
        }

        if techniques.is_empty() {
            techniques.push("Multi-Stage Hybrid Compression".to_string());
        }

        techniques
    }
}

/// Main Universal Compression Champion Analyzer
pub struct UniversalCompressionChampion {
    config: UniversalAnalyzerConfig,
    pattern_analyzer: UniversalPatternAnalyzer,
}

impl UniversalCompressionChampion {
    pub fn new() -> Self {
        let config = UniversalAnalyzerConfig::default();
        let pattern_analyzer = UniversalPatternAnalyzer::new(config.clone());
        
        Self {
            config,
            pattern_analyzer,
        }
    }

    pub fn with_config(config: UniversalAnalyzerConfig) -> Self {
        let pattern_analyzer = UniversalPatternAnalyzer::new(config.clone());
        Self {
            config,
            pattern_analyzer,
        }
    }

    /// Discover files for analysis
    pub fn discover_files(&self, root_path: &str) -> Result<Vec<UniversalFileInfo>, Box<dyn std::error::Error>> {
        let mut files = Vec::new();
        self.scan_directory(Path::new(root_path), &mut files)?;
        
        files.sort_by(|a, b| b.estimated_potential.partial_cmp(&a.estimated_potential).unwrap());
        
        Ok(files)
    }

    fn scan_directory(&self, dir: &Path, files: &mut Vec<UniversalFileInfo>) -> Result<(), Box<dyn std::error::Error>> {
        if !dir.is_dir() {
            return Ok(());
        }

        for entry in fs::read_dir(dir)? {
            let entry = entry?;
            let path = entry.path();

            if path.is_file() && self.is_supported_file(&path) {
                if let Ok(metadata) = fs::metadata(&path) {
                    let size_bytes = metadata.len();
                    let size_mb = size_bytes as f64 / 1_048_576.0;

                    if size_mb > self.config.max_file_size_mb as f64 || size_mb < 0.01 {
                        continue;
                    }

                    let extension = path.extension()
                        .and_then(|ext| ext.to_str())
                        .unwrap_or("unknown")
                        .to_string();

                    let estimated_potential = Self::estimate_potential_by_type(&extension, size_mb);

                    files.push(UniversalFileInfo {
                        path,
                        size_mb,
                        file_type: FileType::Unknown, // Will be determined during analysis
                        estimated_potential,
                        extension,
                    });
                }
            } else if path.is_dir() {
                let dir_name = path.file_name()
                    .and_then(|n| n.to_str())
                    .unwrap_or("");
                
                if !dir_name.starts_with('.') && 
                   !["target", "node_modules", ".git", "tmp", "temp", "bin", "obj"].contains(&dir_name) {
                    self.scan_directory(&path, files)?;
                }
            }
        }

        Ok(())
    }

    fn is_supported_file(&self, path: &Path) -> bool {
        if let Some(extension) = path.extension() {
            if let Some(ext_str) = extension.to_str() {
                return self.config.supported_extensions.contains(&ext_str.to_lowercase());
            }
        }
        false
    }

    /// Estimate compression potential based on file type
    fn estimate_potential_by_type(extension: &str, size_mb: f64) -> f64 {
        let base_potential = match extension.to_lowercase().as_str() {
            // High compression potential
            "exe" | "dll" | "pdb" | "obj" => 8000.0,
            "cpp" | "c" | "h" | "rs" | "py" => 7000.0,
            "txt" | "log" | "csv" => 6000.0,
            
            // Medium compression potential
            "pdf" | "doc" | "docx" => 5000.0,
            "mp3" | "mp4" | "avi" => 4000.0,
            "jpg" | "png" | "gif" => 3000.0,
            
            // Low compression potential (already compressed)
            "zip" | "rar" | "7z" | "gz" => 1000.0,
            
            _ => 4000.0, // Default
        };
        
        // Adjust by size (larger files often have more compression potential)
        (base_potential * (size_mb / 10.0).min(2.0)).min(10000.0)
    }

    /// Analyze a single file
    pub fn analyze_file(&self, file_info: &UniversalFileInfo) -> Result<CompressionAnalysis, Box<dyn std::error::Error>> {
        let start_time = Instant::now();
        
        let data = fs::read(&file_info.path)?;
        
        let compression_metrics = self.pattern_analyzer.analyze_patterns(&data);
        let (file_type, format_data) = UniversalFileAnalyzer::analyze_file(&data, &file_info.extension);
        
        let compression_characteristics = Self::analyze_compression_characteristics(&data, &file_type);
        let file_specific_metrics = FileSpecificMetrics {
            file_type: file_type.clone(),
            format_specific_data: format_data,
            compression_characteristics,
        };
        
        let recommended_strategy = UniversalStrategySelector::select_strategy(&compression_metrics, &file_specific_metrics);
        
        Ok(CompressionAnalysis {
            file_info: UniversalFileInfo {
                file_type,
                ..file_info.clone()
            },
            compression_metrics,
            file_specific_metrics,
            processing_time: start_time.elapsed(),
            recommended_strategy,
        })
    }

    /// Analyze compression characteristics
    fn analyze_compression_characteristics(data: &[u8], file_type: &FileType) -> CompressionCharacteristics {
        let entropy = Self::calculate_entropy(data);
        let entropy_profile = Self::classify_entropy(entropy);
        
        CompressionCharacteristics {
            is_already_compressed: matches!(file_type, FileType::Archive | FileType::Media),
            compression_friendly: entropy < 6.0,
            has_redundant_data: Self::has_redundant_data(data),
            structural_patterns: Self::has_structural_patterns(data),
            entropy_distribution: entropy_profile,
        }
    }

    /// Calculate entropy
    fn calculate_entropy(data: &[u8]) -> f64 {
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

    /// Classify entropy profile
    fn classify_entropy(entropy: f64) -> EntropyProfile {
        match entropy {
            e if e < 3.0 => EntropyProfile::LowEntropy { value: e, reason: "Highly structured data".to_string() },
            e if e < 5.0 => EntropyProfile::MediumEntropy { value: e, distribution: "Mixed patterns".to_string() },
            e if e < 7.0 => EntropyProfile::HighEntropy { value: e, randomness: "Random-like data".to_string() },
            _ => EntropyProfile::MixedEntropy { low_regions: 0.3, high_regions: 0.7 },
        }
    }

    /// Check for redundant data
    fn has_redundant_data(data: &[u8]) -> bool {
        if data.len() < 100 { return false; }
        
        let sample_size = data.len().min(4096);
        let sample = &data[..sample_size];
        
        // Check for repeated patterns
        let mut pattern_counts = HashMap::new();
        for window in sample.windows(8) {
            *pattern_counts.entry(window.to_vec()).or_insert(0) += 1;
        }
        
        pattern_counts.values().any(|&count| count > 2)
    }

    /// Check for structural patterns
    fn has_structural_patterns(data: &[u8]) -> bool {
        if data.len() < 100 { return false; }
        
        // Check for repeated headers, footers, or structural markers
        let header_size = 32.min(data.len() / 4);
        let header = &data[..header_size];
        
        // Look for this header pattern elsewhere in the data
        data.windows(header_size).any(|window| window == header)
    }

    /// Analyze multiple files with progress reporting
    pub fn analyze_multiple(&self, files: &[UniversalFileInfo]) -> Vec<Result<CompressionAnalysis, Box<dyn std::error::Error>>> {
        println!("Analyzing {} files for compression potential...", files.len());
        
        files.iter().enumerate().map(|(i, file_info)| {
            print!("\r[{:3}/{:3}] Analyzing {}...", 
                   i + 1, files.len(), 
                   file_info.path.file_name().unwrap_or_default().to_string_lossy());
            std::io::Write::flush(&mut std::io::stdout()).ok();
            
            self.analyze_file(file_info)
        }).collect()
    }

    /// Generate comprehensive universal report
    pub fn generate_report(&self, analyses: &[CompressionAnalysis]) -> String {
        let mut report = String::new();
        
        report.push_str("UNIVERSAL COMPRESSION CHAMPION REPORT - MMH-RS\n");
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

        // File type distribution
        let mut type_counts = HashMap::new();
        for analysis in analyses {
            let type_name = format!("{:?}", analysis.file_info.file_type);
            *type_counts.entry(type_name).or_insert(0) += 1;
        }

        report.push_str("FILE TYPE DISTRIBUTION:\n");
        report.push_str(&"-".repeat(80));
        report.push_str("\n");
        for (file_type, count) in type_counts {
            let percentage = (count as f64 / total_files as f64) * 100.0;
            report.push_str(&format!("   {}: {} files ({:.1}%)\n", file_type, count, percentage));
        }
        report.push_str("\n");

        // Top compression candidates
        let mut ranked: Vec<_> = analyses.iter().collect();
        ranked.sort_by(|a, b| b.compression_metrics.compression_potential
                              .partial_cmp(&a.compression_metrics.compression_potential)
                              .unwrap());

        report.push_str("TOP COMPRESSION CANDIDATES:\n");
        report.push_str(&"-".repeat(80));
        report.push_str("\n");

        for (i, analysis) in ranked.iter().take(15).enumerate() {
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
            
            report.push_str(&format!("   Type: {:?}, Extension: {}\n", 
                analysis.file_info.file_type, analysis.file_info.extension));
            report.push_str(&format!("   Strategy: {:?}\n", analysis.recommended_strategy));
            report.push_str(&format!("   Entropy: {:.2}, Patterns: {}, Repetition: {:.2}\n\n", 
                analysis.compression_metrics.entropy,
                analysis.compression_metrics.pattern_count,
                analysis.compression_metrics.repetition_ratio));
        }

        // Strategy distribution
        let mut strategy_counts = HashMap::new();
        for analysis in analyses {
            let strategy_name = match &analysis.recommended_strategy {
                CompressionStrategy::Champion { .. } => "Champion",
                CompressionStrategy::HighPerformance { .. } => "High Performance",
                CompressionStrategy::Standard { .. } => "Standard",
                CompressionStrategy::Basic { .. } => "Basic",
                CompressionStrategy::AlreadyCompressed { .. } => "Already Compressed",
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

        // MMH-RS recommendations
        report.push_str("\nMMH-RS COMPRESSION RECOMMENDATIONS:\n");
        report.push_str(&"-".repeat(80));
        report.push_str("\n");
        
        let champion_files: Vec<_> = analyses.iter()
            .filter(|a| matches!(a.recommended_strategy, CompressionStrategy::Champion { .. }))
            .collect();
        
        if !champion_files.is_empty() {
            report.push_str(&format!("🏆 {} files are CHAMPION candidates for MMH-RS compression:\n", champion_files.len()));
            for analysis in champion_files.iter().take(5) {
                if let CompressionStrategy::Champion { mmh_rs_codec, expected_ratio, .. } = &analysis.recommended_strategy {
                    report.push_str(&format!("   • {}: Use {} codec, expected ratio: {:.2}\n",
                        analysis.file_info.path.file_name().unwrap_or_default().to_string_lossy(),
                        mmh_rs_codec, expected_ratio));
                }
            }
        }

        report
    }
}

impl Default for UniversalCompressionChampion {
    fn default() -> Self {
        Self::new()
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("UNIVERSAL COMPRESSION CHAMPION - MMH-RS Multi-Format Analyzer");
    println!("{}", "=".repeat(80));
    
    let analyzer = UniversalCompressionChampion::new();
    
    let current_dir = env::current_dir()?;
    let current_dir_str = current_dir.to_string_lossy();
    
    println!("\nDiscovering files for compression analysis in: {}", current_dir_str);
    
    let files = analyzer.discover_files(&current_dir_str)?;
    
    if files.is_empty() {
        println!("No supported files found");
        println!("Supported extensions: {}", analyzer.config.supported_extensions.join(", "));
        return Ok(());
    }
    
    println!("Found {} supported files", files.len());
    
    let files_to_analyze = &files[..files.len().min(50)]; // Limit to 50 files for demo
    let results = analyzer.analyze_multiple(files_to_analyze);
    
    let successful_analyses: Vec<CompressionAnalysis> = results.into_iter()
        .filter_map(|r| r.ok())
        .collect();
    
    println!("\nSuccessfully analyzed {} files", successful_analyses.len());
    
    if !successful_analyses.is_empty() {
        let report = analyzer.generate_report(&successful_analyses);
        println!("\n{}", report);
        
        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)?
            .as_secs();
        let report_filename = format!("universal_compression_report_{}.txt", timestamp);
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
        let config = UniversalAnalyzerConfig::default();
        assert_eq!(config.min_pattern_length, 4);
        assert_eq!(config.target_compression_potential, 8000.0);
        assert!(!config.supported_extensions.is_empty());
    }

    #[test]
    fn test_file_type_detection() {
        let exe_data = [0x4D, 0x5A, 0x90, 0x00, 0x03, 0x00, 0x00, 0x00];
        let (file_type, _) = UniversalFileAnalyzer::analyze_file(&exe_data, "exe");
        assert_eq!(file_type, FileType::Executable);
    }

    #[test]
    fn test_pattern_analyzer() {
        let config = UniversalAnalyzerConfig::default();
        let analyzer = UniversalPatternAnalyzer::new(config);
        
        let test_data = b"ABCABCABCDEFDEFDEF";
        let metrics = analyzer.analyze_patterns(test_data);
        
        assert!(metrics.compression_potential > 0.0);
        assert!(metrics.entropy > 0.0);
        assert!(metrics.repetition_ratio > 0.0);
    }
}
