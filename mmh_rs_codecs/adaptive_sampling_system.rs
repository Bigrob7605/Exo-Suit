// Adaptive Sampling Strategy System for MMH-RS
// Phase 1.2: Adaptive Sampling Strategy System

use std::collections::HashMap;
use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::path::Path;
use crate::universal_file_detector::{FileCategory, FileTypeInfo};

/// Sampling strategy configuration
#[derive(Debug, Clone)]
pub struct SamplingStrategy {
    pub name: String,
    pub description: String,
    pub sample_points: Vec<SamplePoint>,
    pub buffer_size: usize,
    pub max_memory_mb: usize,
}

/// Individual sample point definition
#[derive(Debug, Clone)]
pub struct SamplePoint {
    pub offset: SampleOffset,
    pub size: usize,
    pub description: String,
}

/// Sample offset specification
#[derive(Debug, Clone)]
pub enum SampleOffset {
    Absolute(usize),           // Fixed byte offset
    Percentage(f64),           // Percentage of file size
    FromStart(usize),          // Offset from start
    FromEnd(usize),            // Offset from end
    Random(usize, usize),      // Random range (min, max)
}

/// Sampling result
#[derive(Debug, Clone)]
pub struct SamplingResult {
    pub file_path: String,
    pub file_size: u64,
    pub file_category: FileCategory,
    pub samples: Vec<SampleData>,
    pub total_samples_size: usize,
    pub memory_used: usize,
    pub sampling_time_ms: u64,
}

/// Individual sample data
#[derive(Debug, Clone)]
pub struct SampleData {
    pub offset: u64,
    pub size: usize,
    pub data: Vec<u8>,
    pub description: String,
    pub entropy: f64,
}

/// Adaptive sampling system
pub struct AdaptiveSamplingSystem {
    strategies: HashMap<FileCategory, SamplingStrategy>,
    default_strategy: SamplingStrategy,
}

impl AdaptiveSamplingSystem {
    pub fn new() -> Self {
        let mut system = Self {
            strategies: HashMap::new(),
            default_strategy: SamplingStrategy::default(),
        };
        system.initialize_strategies();
        system
    }

    /// Initialize file-type specific sampling strategies
    fn initialize_strategies(&mut self) {
        // Executable files: Header + Middle + Footer strategy
        let executable_strategy = SamplingStrategy {
            name: "Executable Sampling".to_string(),
            description: "Header (1KB) + Middle (1KB) + Footer (1KB) for PE/ELF/MachO files".to_string(),
            sample_points: vec![
                SamplePoint {
                    offset: SampleOffset::FromStart(0),
                    size: 1024,
                    description: "Header - Import tables, section headers".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.5),
                    size: 1024,
                    description: "Middle - Code sections, data patterns".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::FromEnd(1024),
                    size: 1024,
                    description: "Footer - Relocation tables, debug info".to_string(),
                },
            ],
            buffer_size: 1024,
            max_memory_mb: 10,
        };
        self.strategies.insert(FileCategory::Executable, executable_strategy);

        // Debug files: Comprehensive sampling
        let debug_strategy = SamplingStrategy {
            name: "Debug File Sampling".to_string(),
            description: "Header + Symbol tables + Debug sections for PDB/DWARF files".to_string(),
            sample_points: vec![
                SamplePoint {
                    offset: SampleOffset::FromStart(0),
                    size: 2048,
                    description: "Header - File signature, version info".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.25),
                    size: 1024,
                    description: "Symbol table section".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.5),
                    size: 1024,
                    description: "Debug information section".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.75),
                    size: 1024,
                    description: "Type information section".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::FromEnd(2048),
                    size: 2048,
                    description: "Footer - Index tables, string pools".to_string(),
                },
            ],
            buffer_size: 2048,
            max_memory_mb: 20,
        };
        self.strategies.insert(FileCategory::Debug, debug_strategy);

        // Media files: Periodic sampling
        let media_strategy = SamplingStrategy {
            name: "Media File Sampling".to_string(),
            description: "Periodic samples every 10% of file size for audio/video files".to_string(),
            sample_points: vec![
                SamplePoint {
                    offset: SampleOffset::FromStart(0),
                    size: 1024,
                    description: "Header - Format info, metadata".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.1),
                    size: 512,
                    description: "10% - Frame data sample".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.2),
                    size: 512,
                    description: "20% - Frame data sample".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.3),
                    size: 512,
                    description: "30% - Frame data sample".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.4),
                    size: 512,
                    description: "40% - Frame data sample".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.5),
                    size: 512,
                    description: "50% - Frame data sample".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.6),
                    size: 512,
                    description: "60% - Frame data sample".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.7),
                    size: 512,
                    description: "70% - Frame data sample".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.8),
                    size: 512,
                    description: "80% - Frame data sample".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.9),
                    size: 512,
                    description: "90% - Frame data sample".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::FromEnd(1024),
                    size: 1024,
                    description: "Footer - Index tables, metadata".to_string(),
                },
            ],
            buffer_size: 1024,
            max_memory_mb: 15,
        };
        self.strategies.insert(FileCategory::Media, media_strategy);

        // Archive files: Header + Central directory + Footer
        let archive_strategy = SamplingStrategy {
            name: "Archive Sampling".to_string(),
            description: "Header + Central directory + Footer for ZIP/RAR/7Z files".to_string(),
            sample_points: vec![
                SamplePoint {
                    offset: SampleOffset::FromStart(0),
                    size: 1024,
                    description: "Header - Archive format, compression method".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.8),
                    size: 2048,
                    description: "Central directory - File list, metadata".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::FromEnd(1024),
                    size: 1024,
                    description: "Footer - Archive end marker, checksums".to_string(),
                },
            ],
            buffer_size: 2048,
            max_memory_mb: 10,
        };
        self.strategies.insert(FileCategory::Archive, archive_strategy);

        // Document files: Header + Content + Footer
        let document_strategy = SamplingStrategy {
            name: "Document Sampling".to_string(),
            description: "Header + Content samples + Footer for PDF/DOC/XLS files".to_string(),
            sample_points: vec![
                SamplePoint {
                    offset: SampleOffset::FromStart(0),
                    size: 2048,
                    description: "Header - Document format, metadata".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.25),
                    size: 1024,
                    description: "Content sample 1".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.5),
                    size: 1024,
                    description: "Content sample 2".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.75),
                    size: 1024,
                    description: "Content sample 3".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::FromEnd(2048),
                    size: 2048,
                    description: "Footer - Index tables, metadata".to_string(),
                },
            ],
            buffer_size: 2048,
            max_memory_mb: 15,
        };
        self.strategies.insert(FileCategory::Document, document_strategy);

        // Database files: Header + Index + Data
        let database_strategy = SamplingStrategy {
            name: "Database Sampling".to_string(),
            description: "Header + Index samples + Data samples for database files".to_string(),
            sample_points: vec![
                SamplePoint {
                    offset: SampleOffset::FromStart(0),
                    size: 2048,
                    description: "Header - Database format, schema info".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.2),
                    size: 1024,
                    description: "Index structure sample".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.4),
                    size: 1024,
                    description: "Data structure sample 1".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.6),
                    size: 1024,
                    description: "Data structure sample 2".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.8),
                    size: 1024,
                    description: "Index structure sample 2".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::FromEnd(2048),
                    size: 2048,
                    description: "Footer - Transaction logs, metadata".to_string(),
                },
            ],
            buffer_size: 2048,
            max_memory_mb: 20,
        };
        self.strategies.insert(FileCategory::Database, database_strategy);
    }

    /// Get sampling strategy for a file category
    pub fn get_strategy(&self, category: &FileCategory) -> &SamplingStrategy {
        self.strategies.get(category).unwrap_or(&self.default_strategy)
    }

    /// Sample file using adaptive strategy
    pub fn sample_file(&self, file_path: &Path, file_info: &FileTypeInfo) -> Result<SamplingResult, std::io::Error> {
        let start_time = std::time::Instant::now();
        let strategy = self.get_strategy(&file_info.category);
        
        let mut file = File::open(file_path)?;
        let file_size = file.metadata()?.len();
        
        let mut samples = Vec::new();
        let mut total_samples_size = 0;
        let mut memory_used = 0;
        
        for sample_point in &strategy.sample_points {
            let offset = self.calculate_offset(&sample_point.offset, file_size);
            let size = sample_point.size.min((file_size - offset) as usize);
            
            if size > 0 {
                let mut buffer = vec![0u8; size];
                file.seek(SeekFrom::Start(offset))?;
                file.read_exact(&mut buffer)?;
                
                let entropy = self.calculate_entropy(&buffer);
                let sample_data = SampleData {
                    offset,
                    size,
                    data: buffer.clone(),
                    description: sample_point.description.clone(),
                    entropy,
                };
                
                samples.push(sample_data);
                total_samples_size += size;
                memory_used = memory_used.max(samples.len() * strategy.buffer_size);
            }
        }
        
        let sampling_time = start_time.elapsed().as_millis() as u64;
        
        Ok(SamplingResult {
            file_path: file_path.to_string_lossy().to_string(),
            file_size,
            file_category: file_info.category.clone(),
            samples,
            total_samples_size,
            memory_used,
            sampling_time_ms: sampling_time,
        })
    }

    /// Calculate actual offset from sample point specification
    fn calculate_offset(&self, offset_spec: &SampleOffset, file_size: u64) -> u64 {
        match offset_spec {
            SampleOffset::Absolute(offset) => *offset as u64,
            SampleOffset::Percentage(percent) => {
                let offset = (file_size as f64 * percent) as u64;
                offset.min(file_size.saturating_sub(1))
            }
            SampleOffset::FromStart(offset) => *offset as u64,
            SampleOffset::FromEnd(offset) => {
                if *offset as u64 >= file_size {
                    0
                } else {
                    file_size - *offset as u64
                }
            }
            SampleOffset::Random(min, max) => {
                let min = *min as u64;
                let max = max.min(&(file_size - 1)) as u64;
                if min >= max {
                    min
                } else {
                    min + (rand::random::<u64>() % (max - min))
                }
            }
        }
    }

    /// Calculate entropy of a data buffer
    fn calculate_entropy(&self, data: &[u8]) -> f64 {
        if data.is_empty() {
            return 0.0;
        }
        
        let mut byte_counts = [0u32; 256];
        for &byte in data {
            byte_counts[byte as usize] += 1;
        }
        
        let data_len = data.len() as f64;
        let mut entropy = 0.0;
        
        for &count in &byte_counts {
            if count > 0 {
                let probability = count as f64 / data_len;
                entropy -= probability * probability.log2();
            }
        }
        
        entropy
    }

    /// Stream sample large files (>100MB) to avoid memory issues
    pub fn stream_sample_large_file(&self, file_path: &Path, file_info: &FileTypeInfo, max_memory_mb: usize) -> Result<SamplingResult, std::io::Error> {
        let strategy = self.get_strategy(&file_info.category);
        let max_memory_bytes = max_memory_mb * 1024 * 1024;
        
        // For large files, use sliding window approach
        let mut file = File::open(file_path)?;
        let file_size = file.metadata()?.len();
        
        let mut samples = Vec::new();
        let mut total_samples_size = 0;
        let mut memory_used = 0;
        
        // Use fewer, larger samples for large files
        let adjusted_strategy = self.create_large_file_strategy(strategy, file_size, max_memory_bytes);
        
        for sample_point in &adjusted_strategy.sample_points {
            let offset = self.calculate_offset(&sample_point.offset, file_size);
            let size = sample_point.size.min((file_size - offset) as usize);
            
            if size > 0 {
                let mut buffer = vec![0u8; size];
                file.seek(SeekFrom::Start(offset))?;
                file.read_exact(&mut buffer)?;
                
                let entropy = self.calculate_entropy(&buffer);
                let sample_data = SampleData {
                    offset,
                    size,
                    data: buffer.clone(),
                    description: sample_point.description.clone(),
                    entropy,
                };
                
                samples.push(sample_data);
                total_samples_size += size;
                memory_used = memory_used.max(samples.len() * strategy.buffer_size);
                
                // Check memory limit
                if memory_used > max_memory_bytes {
                    break;
                }
            }
        }
        
        Ok(SamplingResult {
            file_path: file_path.to_string_lossy().to_string(),
            file_size,
            file_category: file_info.category.clone(),
            samples,
            total_samples_size,
            memory_used,
            sampling_time_ms: 0, // Not measured for streaming
        })
    }

    /// Create optimized strategy for large files
    fn create_large_file_strategy(&self, base_strategy: &SamplingStrategy, file_size: u64, max_memory: usize) -> SamplingStrategy {
        let mut large_file_strategy = base_strategy.clone();
        
        // Reduce sample sizes for large files
        for sample_point in &mut large_file_strategy.sample_points {
            sample_point.size = sample_point.size.min(max_memory / 10); // Use at most 10% of max memory per sample
        }
        
        large_file_strategy.max_memory_mb = max_memory / (1024 * 1024);
        large_file_strategy
    }
}

impl Default for SamplingStrategy {
    fn default() -> Self {
        Self {
            name: "Default Sampling".to_string(),
            description: "Basic sampling strategy for unknown file types".to_string(),
            sample_points: vec![
                SamplePoint {
                    offset: SampleOffset::FromStart(0),
                    size: 1024,
                    description: "Header sample".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::Percentage(0.5),
                    size: 1024,
                    description: "Middle sample".to_string(),
                },
                SamplePoint {
                    offset: SampleOffset::FromEnd(1024),
                    size: 1024,
                    description: "Footer sample".to_string(),
                },
            ],
            buffer_size: 1024,
            max_memory_mb: 10,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_strategy_creation() {
        let system = AdaptiveSamplingSystem::new();
        assert!(system.strategies.contains_key(&FileCategory::Executable));
        assert!(system.strategies.contains_key(&FileCategory::Debug));
        assert!(system.strategies.contains_key(&FileCategory::Media));
    }

    #[test]
    fn test_offset_calculation() {
        let system = AdaptiveSamplingSystem::new();
        let file_size = 1000;
        
        let absolute = SampleOffset::Absolute(100);
        assert_eq!(system.calculate_offset(&absolute, file_size), 100);
        
        let percentage = SampleOffset::Percentage(0.5);
        assert_eq!(system.calculate_offset(&percentage, file_size), 500);
        
        let from_end = SampleOffset::FromEnd(100);
        assert_eq!(system.calculate_offset(&from_end, file_size), 900);
    }

    #[test]
    fn test_entropy_calculation() {
        let system = AdaptiveSamplingSystem::new();
        
        // Test with uniform data (high entropy)
        let uniform_data = vec![0, 1, 2, 3, 4, 5, 6, 7];
        let entropy = system.calculate_entropy(&uniform_data);
        assert!(entropy > 2.0); // Should be close to 3.0 for 8 unique values
        
        // Test with repeated data (low entropy)
        let repeated_data = vec![0, 0, 0, 0, 0, 0, 0, 0];
        let entropy = system.calculate_entropy(&repeated_data);
        assert_eq!(entropy, 0.0); // No entropy for single value
    }
}
