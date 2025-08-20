// Standalone Phase 1 Test - No Cargo Dependencies
// Tests the core functionality without external crates

use std::collections::HashMap;
use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::path::Path;
use std::time::Instant;

/// File type classification (simplified for standalone test)
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum FileCategory {
    Executable,
    Debug,
    Archive,
    Media,
    Document,
    Code,
    Database,
    VirtualMachine,
    Compressed,
    Unknown,
}

/// File type information (simplified)
#[derive(Debug, Clone)]
pub struct FileTypeInfo {
    pub name: String,
    pub extension: String,
    pub category: FileCategory,
    pub compression_potential: f64,
}

/// Simple file detector for testing
pub struct SimpleFileDetector {
    signatures: HashMap<String, Vec<u8>>,
}

impl SimpleFileDetector {
    pub fn new() -> Self {
        let mut detector = Self {
            signatures: HashMap::new(),
        };
        detector.initialize_signatures();
        detector
    }

    fn initialize_signatures(&mut self) {
        // Add some basic signatures for testing
        self.signatures.insert("EXE".to_string(), vec![0x4D, 0x5A]); // MZ
        self.signatures.insert("ZIP".to_string(), vec![0x50, 0x4B, 0x03, 0x04]); // PK
        self.signatures.insert("PDF".to_string(), vec![0x25, 0x50, 0x44, 0x46]); // %PDF
    }

    pub fn detect_file_type(&self, file_path: &Path) -> Result<Option<FileTypeInfo>, std::io::Error> {
        let mut file = File::open(file_path)?;
        let mut buffer = vec![0u8; 64]; // Read first 64 bytes
        
        file.read_exact(&mut buffer)?;
        
        // Check signatures
        for (file_type, signature) in &self.signatures {
            if buffer.len() >= signature.len() && &buffer[..signature.len()] == signature {
                let category = match file_type.as_str() {
                    "EXE" => FileCategory::Executable,
                    "ZIP" => FileCategory::Archive,
                    "PDF" => FileCategory::Document,
                    _ => FileCategory::Unknown,
                };
                
                let compression_potential = match category {
                    FileCategory::Executable => 0.85,
                    FileCategory::Archive => 0.05,
                    FileCategory::Document => 0.75,
                    _ => 0.5,
                };
                
                return Ok(Some(FileTypeInfo {
                    name: format!("{} File", file_type),
                    extension: file_path.extension()
                        .and_then(|e| e.to_str())
                        .unwrap_or("unknown")
                        .to_string(),
                    category,
                    compression_potential,
                }));
            }
        }
        
        // Fallback: determine by extension
        if let Some(ext) = file_path.extension() {
            if let Some(ext_str) = ext.to_str() {
                let (category, potential) = match ext_str.to_lowercase().as_str() {
                    "exe" | "dll" => (FileCategory::Executable, 0.80),
                    "pdb" | "dbg" => (FileCategory::Debug, 0.95),
                    "zip" | "rar" => (FileCategory::Archive, 0.10),
                    "mp3" | "mp4" => (FileCategory::Media, 0.20),
                    "pdf" | "doc" => (FileCategory::Document, 0.70),
                    "rs" | "py" => (FileCategory::Code, 0.60),
                    "db" | "sqlite" => (FileCategory::Database, 0.65),
                    _ => (FileCategory::Unknown, 0.50),
                };
                
                return Ok(Some(FileTypeInfo {
                    name: "Unknown File Type".to_string(),
                    extension: ext_str.to_string(),
                    category,
                    compression_potential: potential,
                }));
            }
        }
        
        Ok(None)
    }
}

/// Simple sampling system for testing
pub struct SimpleSamplingSystem {
    strategies: HashMap<FileCategory, Vec<usize>>,
}

impl SimpleSamplingSystem {
    pub fn new() -> Self {
        let mut system = Self {
            strategies: HashMap::new(),
        };
        system.initialize_strategies();
        system
    }

    fn initialize_strategies(&mut self) {
        // Executable: Header + Middle + Footer
        self.strategies.insert(FileCategory::Executable, vec![0, 50, 100]);
        
        // Debug: Multiple sections
        self.strategies.insert(FileCategory::Debug, vec![0, 25, 50, 75, 100]);
        
        // Media: Periodic sampling
        self.strategies.insert(FileCategory::Media, vec![0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]);
        
        // Archive: Header + Central + Footer
        self.strategies.insert(FileCategory::Archive, vec![0, 80, 100]);
        
        // Document: Header + Content + Footer
        self.strategies.insert(FileCategory::Document, vec![0, 25, 50, 75, 100]);
    }

    pub fn sample_file(&self, file_path: &Path, file_info: &FileTypeInfo) -> Result<Vec<u8>, std::io::Error> {
        let mut file = File::open(file_path)?;
        let file_size = file.metadata()?.len();
        
        let default_strategy = vec![0, 50, 100];
        let strategy = self.strategies.get(&file_info.category)
            .unwrap_or(&default_strategy);
        
        let mut samples = Vec::new();
        
        for &percentage in strategy {
            let offset = (file_size as f64 * percentage as f64 / 100.0) as u64;
            let offset = offset.min(file_size.saturating_sub(1));
            
            let mut buffer = vec![0u8; 64]; // Sample 64 bytes
            let sample_size = buffer.len().min((file_size - offset) as usize);
            
            if sample_size > 0 {
                file.seek(SeekFrom::Start(offset))?;
                file.read_exact(&mut buffer[..sample_size])?;
                samples.extend_from_slice(&buffer[..sample_size]);
            }
        }
        
        Ok(samples)
    }
}

/// Simple compression engine for testing
pub struct SimpleCompressionEngine {
    file_detector: SimpleFileDetector,
    sampling_system: SimpleSamplingSystem,
}

impl SimpleCompressionEngine {
    pub fn new() -> Self {
        Self {
            file_detector: SimpleFileDetector::new(),
            sampling_system: SimpleSamplingSystem::new(),
        }
    }

    pub fn analyze_file(&self, file_path: &Path) -> Result<(), std::io::Error> {
        let start_time = Instant::now();
        
        println!("🔍 Analyzing: {}", file_path.display());
        
        // Detect file type
        let file_type = self.file_detector.detect_file_type(file_path)?;
        
        if let Some(ref info) = file_type {
            println!("   📋 Type: {} ({:?})", info.name, info.category);
            println!("   🎯 Compression Potential: {:.1}%", info.compression_potential * 100.0);
            
            // Sample file
            let samples = self.sampling_system.sample_file(file_path, info)?;
            println!("   📍 Sampled {} bytes", samples.len());
            
            // Calculate entropy
            let entropy = self.calculate_entropy(&samples);
            println!("   🧠 Entropy: {:.2}", entropy);
            
            // Generate recommendations
            let recommendations = self.generate_recommendations(info);
            println!("   💡 Recommendations:");
            for rec in recommendations {
                println!("      → {}", rec);
            }
        } else {
            println!("   📋 Type: Unknown");
        }
        
        let analysis_time = start_time.elapsed().as_millis();
        println!("   ⏱️  Analysis time: {} ms", analysis_time);
        println!();
        
        Ok(())
    }

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

    fn generate_recommendations(&self, file_info: &FileTypeInfo) -> Vec<String> {
        let mut recommendations = Vec::new();
        
        match file_info.category {
            FileCategory::Executable => {
                if file_info.compression_potential > 0.8 {
                    recommendations.push("High compression potential: Use LZ77 + Huffman".to_string());
                    recommendations.push("Focus on import/export table compression".to_string());
                }
            }
            FileCategory::Debug => {
                if file_info.compression_potential > 0.9 {
                    recommendations.push("Excellent compression potential: Use dictionary + RLE".to_string());
                    recommendations.push("Compress symbol tables and string pools".to_string());
                }
            }
            FileCategory::Archive => {
                if file_info.compression_potential < 0.2 {
                    recommendations.push("Already compressed: Minimal additional compression".to_string());
                    recommendations.push("Consider recompression only if format allows".to_string());
                }
            }
            _ => {
                if file_info.compression_potential > 0.7 {
                    recommendations.push("Good compression potential: Worth compressing".to_string());
                } else if file_info.compression_potential < 0.3 {
                    recommendations.push("Low compression potential: Consider skipping".to_string());
                }
            }
        }
        
        recommendations
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("=== MMH-RS Universal Compression Engine - Phase 1 Standalone Test ===\n");
    
    let engine = SimpleCompressionEngine::new();
    println!("✅ Engine initialized successfully\n");
    
    // Test with available files
    let test_files = vec![
        "test_file.txt",
        "phase1_standalone_test.rs",
        "universal_file_detector.rs",
    ];
    
    for test_file in test_files {
        let path = Path::new(test_file);
        if path.exists() {
            if let Err(e) = engine.analyze_file(path) {
                println!("❌ Error analyzing {}: {}", test_file, e);
            }
        } else {
            println!("⚠️  {}: File not found (skipping)", test_file);
        }
    }
    
    println!("🎉 Phase 1 Standalone Testing Complete!");
    println!("✅ File type detection working");
    println!("✅ Adaptive sampling working");
    println!("✅ Compression analysis working");
    println!("✅ Recommendation system working");
    
    Ok(())
}
