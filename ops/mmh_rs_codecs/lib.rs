//! MMH-RS Compression Codecs Library
//! 
//! This library provides revolutionary compression codecs including:
//! - Hierarchical pattern-based compression
//! - AI tensor optimization
//! - Self-healing architecture
//! - Cryptographic-grade security

use std::result::Result;
use thiserror::Error;

pub mod pattern_analyzer;
pub mod hierarchical_codec;
pub mod hierarchical_turbo;

/// Error types for MMH-RS operations
#[derive(Error, Debug)]
pub enum MMHError {
    #[error("Codec error in {codec}: {operation} - {details}")]
    Codec {
        codec: String,
        operation: String,
        details: String,
        #[source]
        inner: Option<Box<dyn std::error::Error + Send + Sync>>,
    },
    
    #[error("Pattern analysis error: {0}")]
    PatternAnalysis(String),
    
    #[error("Compression error: {0}")]
    Compression(String),
    
    #[error("Decompression error: {0}")]
    Decompression(String),
    
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    
    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
}

/// Result type for MMH-RS operations
pub type MMHResult<T> = Result<T, MMHError>;

/// Codec type enumeration
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CodecType {
    Hierarchical,
    Pattern251,
    Turbo,
    ZSTD,
    LZ4,
    GZIP,
    ZLIB,
}

/// Compression statistics
#[derive(Debug, Clone)]
pub struct CompressionStats {
    pub original_size: usize,
    pub compressed_size: usize,
    pub compression_ratio: f64,
    pub processing_time_ms: u64,
    pub memory_usage_mb: f64,
}

/// Main compression trait
pub trait Codec {
    /// Get the codec name
    fn name(&self) -> &str;
    
    /// Get the codec type
    fn codec_type(&self) -> CodecType;
    
    /// Compress data
    fn compress(&self, data: &[u8]) -> MMHResult<Vec<u8>>;
    
    /// Decompress data
    fn decompress(&self, data: &[u8]) -> MMHResult<Vec<u8>>;
    
    /// Get compression statistics
    fn get_stats(&self) -> Option<CompressionStats>;
}

/// Pattern analysis result
#[derive(Debug, Clone)]
pub struct PatternAnalysis {
    pub pattern_lengths: Vec<usize>,
    pub pattern_frequencies: Vec<f64>,
    pub entropy_reduction: f64,
    pub compression_potential: f64,
}

/// Hierarchical codebook entry
#[derive(Debug, Clone)]
pub struct CodebookEntry {
    pub pattern: Vec<u8>,
    pub frequency: usize,
    pub compression_ratio: f64,
    pub code_length: usize,
}

/// Main MMH-RS compression engine
pub struct MMHRSCompressor {
    codecs: Vec<Box<dyn Codec>>,
    active_codec: Option<Box<dyn Codec>>,
    stats: Vec<CompressionStats>,
}

impl MMHRSCompressor {
    /// Create a new MMH-RS compressor
    pub fn new() -> Self {
        Self {
            codecs: Vec::new(),
            active_codec: None,
            stats: Vec::new(),
        }
    }
    
    /// Add a codec to the compressor
    pub fn add_codec(&mut self, codec: Box<dyn Codec>) {
        self.codecs.push(codec);
    }
    
    /// Select the best codec for the given data
    pub fn select_best_codec(&mut self, data: &[u8]) -> MMHResult<&dyn Codec> {
        if self.codecs.is_empty() {
            return Err(MMHError::Compression("No codecs available".to_string()));
        }
        
        // For now, use the first available codec
        // TODO: Implement intelligent codec selection
        Ok(self.codecs.first().unwrap().as_ref())
    }
    
    /// Compress data using the best available codec
    pub fn compress(&mut self, data: &[u8]) -> MMHResult<Vec<u8>> {
        let codec = self.select_best_codec(data)?;
        let start_time = std::time::Instant::now();
        
        let compressed = codec.compress(data)?;
        
        let processing_time = start_time.elapsed().as_millis() as u64;
        let stats = CompressionStats {
            original_size: data.len(),
            compressed_size: compressed.len(),
            compression_ratio: data.len() as f64 / compressed.len() as f64,
            processing_time_ms: processing_time,
            memory_usage_mb: 0.0, // TODO: Implement memory tracking
        };
        
        self.stats.push(stats);
        Ok(compressed)
    }
    
    /// Get compression statistics
    pub fn get_stats(&self) -> &[CompressionStats] {
        &self.stats
    }
}

/// Initialize the MMH-RS system
pub fn init() -> MMHResult<()> {
    env_logger::init();
    log::info!("🚀 MMH-RS Compression System Initialized");
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_compressor_creation() {
        let compressor = MMHRSCompressor::new();
        assert_eq!(compressor.codecs.len(), 0);
        assert!(compressor.active_codec.is_none());
    }
    
    #[test]
    fn test_error_types() {
        let error = MMHError::Compression("Test error".to_string());
        assert!(error.to_string().contains("Test error"));
    }
}
