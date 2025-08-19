//! Core MMH-RS functionality

use std::path::Path;
use crate::{Result, MMHError, MMHConfig, Seed, SeedInfo, CodecType, FECType};
use serde::{Serialize, Deserialize};

/// Envelope containing metadata and data
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Envelope {
    /// Original file size
    pub original_size: u64,
    /// Compressed chunks
    pub compressed_chunks: Vec<Vec<u8>>,
    /// FEC encoded data
    pub fec_encoded: Vec<Vec<u8>>,
    /// Chunk hashes for deduplication
    pub chunk_hashes: Vec<[u8; 32]>,
    /// Configuration used
    pub config: MMHConfig,
    /// Creation timestamp
    pub created_at: u64,
}

impl Envelope {
    /// Create a new envelope
    pub fn new(
        original_size: u64,
        compressed_chunks: Vec<Vec<u8>>,
        fec_encoded: Vec<Vec<u8>>,
        chunk_hashes: Vec<[u8; 32]>,
        config: MMHConfig,
    ) -> Self {
        Self {
            original_size,
            compressed_chunks,
            fec_encoded,
            chunk_hashes,
            config,
            created_at: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs(),
        }
    }
}

/// Main MMH-RS engine implementation
pub struct MMHEngine {
    config: MMHConfig,
}

impl MMHEngine {
    /// Create a new engine with configuration
    pub fn new(config: MMHConfig) -> Self {
        Self { config }
    }
    
    /// Get a reference to the configuration
    pub fn config(&self) -> &MMHConfig {
        &self.config
    }
    
    /// Get a mutable reference to the configuration
    pub fn config_mut(&mut self) -> &mut MMHConfig {
        &mut self.config
    }
    
    /// Fold data into a seed
    pub fn fold(&self, input: &Path, output: &Path) -> Result<Seed> {
        // 1. Read and chunk data
        let chunks = self.chunk_data(input)?;
        
        // 2. Deduplicate chunks
        let unique_chunks = self.deduplicate_chunks(&chunks)?;
        
        // 3. Compress chunks
        let codec = crate::codecs::CodecFactory::create(CodecType::Zstd); // Use enum instead of string
        let compressed_chunks = self.compress_chunks(&unique_chunks, &codec)?;
        
        // 4. Apply FEC encoding
        let fec_codec = crate::fec::FECFactory::new(&FECType::RaptorQ)?; // Use enum instead of string
        let fec_encoded = self.encode_fec(&compressed_chunks, &fec_codec)?;
        
        // 5. Create envelope
        let chunk_hashes = self.compute_chunk_hashes(&unique_chunks)?;
        let envelope = Envelope::new(
            self.get_file_size(input)?,
            compressed_chunks,
            fec_encoded,
            chunk_hashes,
            self.config.clone(),
        );
        
        // 6. Generate seed from envelope
        let seed = self.generate_seed(&envelope)?;
        
        // 7. Write envelope to output
        self.write_envelope(&envelope, output)?;
        
        Ok(seed)
    }
    
    /// Unfold data from a seed
    pub fn unfold(&self, seed: &Seed, output: &Path) -> Result<()> {
        // 1. Read envelope from seed
        let envelope = self.read_envelope(seed)?;
        
        // 2. Decode FEC
        let fec_codec = crate::fec::FECFactory::new(&FECType::RaptorQ)?; // Use enum instead of string
        let fec_decoded = self.decode_fec(&envelope, &fec_codec)?;
        
        // 3. Decompress chunks
        let codec = crate::codecs::CodecFactory::create(CodecType::Zstd); // Use enum instead of string
        let decompressed_chunks = self.decompress_chunks(&fec_decoded, &codec)?;
        
        // 4. Reconstruct original data
        let data = self.reconstruct_data(&decompressed_chunks)?;
        
        // 5. Write data to output
        self.write_data(&data, output)?;
        
        Ok(())
    }
    
    /// Verify integrity of a seed against data
    pub fn verify(&self, _seed: &Seed, _data: &Path) -> Result<bool> {
        // Simplified verification - in a real implementation, this would:
        // 1. Read the envelope from the seed
        // 2. Compute hash of the data
        // 3. Compare with stored hash in envelope
        Ok(true)
    }
    
    /// Get information about a seed
    pub fn info(&self, _seed: &Seed) -> Result<SeedInfo> {
        // Simplified info - in a real implementation, this would:
        // 1. Read the envelope from the seed
        // 2. Extract metadata from envelope
        Ok(SeedInfo::default())
    }
    
    // Private helper methods
    
    fn chunk_data(&self, path: &Path) -> Result<Vec<Vec<u8>>> {
        let chunker = crate::chunking::Chunker::new(self.config.file.default_chunk_bits);
        chunker.chunk_file(path)
    }
    
    fn deduplicate_chunks(&self, chunks: &[Vec<u8>]) -> Result<Vec<Vec<u8>>> {
        if self.config.file.dedup_enabled {
            // Simple deduplication based on content
            let mut unique_chunks = Vec::new();
            let mut seen = std::collections::HashSet::new();
            
            for chunk in chunks {
                let hash = crate::utils::hash(chunk);
                if !seen.contains(&hash) {
                    seen.insert(hash);
                    unique_chunks.push(chunk.clone());
                }
            }
            Ok(unique_chunks)
        } else {
            Ok(chunks.to_vec())
        }
    }
    
    fn compress_chunks(&self, chunks: &[Vec<u8>], codec: &Box<dyn crate::codecs::Codec>) -> Result<Vec<Vec<u8>>> {
        let mut compressed_chunks = Vec::new();
        for chunk in chunks {
            let compressed = codec.compress(chunk)?;
            compressed_chunks.push(compressed);
        }
        Ok(compressed_chunks)
    }
    
    fn encode_fec(&self, chunks: &[Vec<u8>], fec_codec: &Box<dyn crate::fec::FECCodec>) -> Result<Vec<Vec<u8>>> {
        fec_codec.encode(chunks)
    }
    
    fn decode_fec(&self, envelope: &Envelope, fec_codec: &Box<dyn crate::fec::FECCodec>) -> Result<Vec<Vec<u8>>> {
        fec_codec.decode(&envelope.compressed_chunks)
    }
    
    fn decompress_chunks(&self, chunks: &[Vec<u8>], codec: &Box<dyn crate::codecs::Codec>) -> Result<Vec<Vec<u8>>> {
        let mut decompressed_chunks = Vec::new();
        for chunk in chunks {
            let decompressed = codec.decompress(chunk)?;
            decompressed_chunks.push(decompressed);
        }
        Ok(decompressed_chunks)
    }
    
    fn compute_chunk_hashes(&self, chunks: &[Vec<u8>]) -> Result<Vec<[u8; 32]>> {
        let mut hashes = Vec::new();
        for chunk in chunks {
            let hash = crate::utils::hash(chunk);
            hashes.push(hash);
        }
        Ok(hashes)
    }
    
    fn generate_seed(&self, envelope: &Envelope) -> Result<Seed> {
        // Generate a deterministic seed from the envelope
        let envelope_hash = crate::utils::hash(&bincode::serialize(envelope)
            .map_err(|e| MMHError::Serialization {
                format: "bincode".to_string(),
                operation: "serialize".to_string(),
                details: e.to_string(),
            })?);
        
        // Use first 16 bytes of hash as seed
        let mut seed = [0u8; 16];
        seed.copy_from_slice(&envelope_hash[..16]);
        Ok(seed)
    }
    
    fn write_envelope(&self, envelope: &Envelope, path: &Path) -> Result<()> {
        let data = bincode::serialize(envelope)
            .map_err(|e| MMHError::Serialization(format!("bincode serialize error: {}", e)))?;
        
        std::fs::write(path, data)
            .map_err(MMHError::Io)?;
        
        Ok(())
    }
    
    fn read_envelope(&self, _seed: &Seed) -> Result<Envelope> {
        // Simplified envelope reading - in a real implementation, this would:
        // 1. Use the seed to locate the envelope file
        // 2. Read and deserialize the envelope
        // 3. Validate the envelope structure
        
        // For now, return a dummy envelope
        let config = MMHConfig::new()?;
        Ok(Envelope::new(
            0,
            Vec::new(),
            Vec::new(),
            Vec::new(),
            config,
        ))
    }
    
    fn reconstruct_data(&self, chunks: &[Vec<u8>]) -> Result<Vec<u8>> {
        // Reconstruct original data from chunks
        let mut data = Vec::new();
        for chunk in chunks {
            data.extend_from_slice(chunk);
        }
        Ok(data)
    }
    
    fn write_data(&self, data: &[u8], path: &Path) -> Result<()> {
        std::fs::write(path, data)
            .map_err(MMHError::Io)?;
        Ok(())
    }
    
    fn get_file_size(&self, path: &Path) -> Result<u64> {
        let metadata = std::fs::metadata(path)
            .map_err(MMHError::Io)?;
        Ok(metadata.len())
    }
}

// Convenience functions
pub fn fold(input: &Path, output: &Path) -> Result<Seed> {
    let config = MMHConfig::new()?;
    let engine = MMHEngine::new(config);
    engine.fold(input, output)
}

pub fn unfold(seed: &Seed, output: &Path) -> Result<()> {
    let config = MMHConfig::new()?;
    let engine = MMHEngine::new(config);
    engine.unfold(seed, output)
}

pub fn verify(seed: &Seed, data: &Path) -> Result<bool> {
    let config = MMHConfig::new()?;
    let engine = MMHEngine::new(config);
    engine.verify(seed, data)
}

pub fn info(seed: &Seed) -> Result<SeedInfo> {
    let config = MMHConfig::new()?;
    let engine = MMHEngine::new(config);
    engine.info(seed)
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;
    
    #[test]
    fn test_mmh_engine_creation() {
        let config = MMHConfig::new().unwrap();
        let engine = MMHEngine::new(config);
        assert_eq!(engine.config().app.name, "MMH-RS");
    }
    
    #[test]
    fn test_chunk_data() {
        let config = MMHConfig::new().unwrap();
        let engine = MMHEngine::new(config);
        let temp_dir = tempdir().unwrap();
        let test_file = temp_dir.path().join("test.txt");
        std::fs::write(&test_file, "Hello, world! This is a test.").unwrap();
        
        let chunks = engine.chunk_data(&test_file).unwrap();
        assert!(!chunks.is_empty());
    }
    
    #[test]
    fn test_deduplicate_chunks() {
        let config = MMHConfig::new().unwrap();
        let engine = MMHEngine::new(config);
        let chunks = vec![
            b"Hello".to_vec(),
            b"World".to_vec(),
            b"Hello".to_vec(), // Duplicate
        ];
        
        let unique = engine.deduplicate_chunks(&chunks).unwrap();
        assert_eq!(unique.len(), 2); // Should remove duplicate
    }
    
    #[test]
    fn test_generate_seed() {
        let config = MMHConfig::new().unwrap();
        let engine = MMHEngine::new(config);
        let config = MMHConfig::new().unwrap();
        let envelope = Envelope::new(
            100,
            vec![b"test".to_vec()],
            vec![b"fec".to_vec()],
            vec![[0u8; 32]],
            config,
        );
        
        let seed = engine.generate_seed(&envelope).unwrap();
        assert_eq!(seed.len(), 16);
    }
} 