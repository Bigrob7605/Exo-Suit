// MMH-RS Universal Compression Engine Library
// Phase 2: Advanced Pattern Recognition & Compression Strategy Matrix

pub mod universal_file_detector;
pub mod adaptive_sampling_system;
pub mod universal_compression_engine;
pub mod pattern_recognition_engine;
pub mod enhanced_pattern_recognition_engine;
pub mod high_performance_pattern_analyzer;

// Re-export main types for easy access
pub use universal_compression_engine::{
    UniversalCompressionEngine,
    UniversalCompressionConfig,
    FileAnalysisResult,
    DirectoryAnalysisResult,
};

pub use universal_file_detector::{
    UniversalFileDetector,
    FileTypeInfo,
    FileCategory,
    MagicSignature,
};

pub use adaptive_sampling_system::{
    AdaptiveSamplingSystem,
    SamplingStrategy,
    SamplingResult,
    SampleData,
    SamplePoint,
    SampleOffset,
};

pub use enhanced_pattern_recognition_engine::{
    EnhancedPatternRecognitionEngine,
    EnhancedPatternRecognitionConfig,
    EnhancedPatternAnalysisResult,
    EnhancedPatternInfo,
    EnhancedPatternType,
    EnhancedCompressionStrategy,
    SilesiaBenchmark,
    display_enhanced_pattern_analysis,
};
