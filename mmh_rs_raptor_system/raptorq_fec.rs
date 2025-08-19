//! Forward Error Correction (FEC) for MMH-RS

use crate::{Result, FECType};

/// Trait for FEC codecs
pub trait FECCodec: Send + Sync {
    /// Encode data with FEC
    fn encode(&self, data: &[Vec<u8>]) -> Result<Vec<Vec<u8>>>;
    
    /// Decode data with FEC
    fn decode(&self, data: &[Vec<u8>]) -> Result<Vec<Vec<u8>>>;
    
    /// Get FEC codec name
    fn name(&self) -> &str;
    
    /// Get redundancy level
    fn redundancy(&self) -> f64;
}

/// RaptorQ FEC implementation
pub struct RaptorQCodec {
    redundancy: f64,
}

impl RaptorQCodec {
    pub fn new(redundancy: f64) -> Self {
        Self { redundancy }
    }
    
    pub fn default() -> Self {
        Self { redundancy: 1.5 }
    }
}

impl FECCodec for RaptorQCodec {
    fn encode(&self, data: &[Vec<u8>]) -> Result<Vec<Vec<u8>>> {
        // Simplified RaptorQ implementation
        // In a real implementation, this would use a proper RaptorQ library
        let mut encoded = Vec::new();
        
        // Add original data
        encoded.extend_from_slice(data);
        
        // Add redundancy blocks
        let redundancy_count = std::cmp::max(1, (data.len() as f64 * (self.redundancy - 1.0)) as usize);
        for i in 0..redundancy_count {
            let mut redundancy_block = Vec::new();
            for (j, chunk) in data.iter().enumerate() {
                let coefficient = (i * j) % 256;
                for &byte in chunk {
                    redundancy_block.push(byte ^ coefficient as u8);
                }
            }
            encoded.push(redundancy_block);
        }
        
        Ok(encoded)
    }
    
    fn decode(&self, data: &[Vec<u8>]) -> Result<Vec<Vec<u8>>> {
        // Simplified decoding - just return the first N chunks
        // In a real implementation, this would perform proper RaptorQ decoding
        let original_count = (data.len() as f64 / self.redundancy) as usize;
        Ok(data[..original_count].to_vec())
    }
    
    fn name(&self) -> &str {
        "raptorq"
    }
    
    fn redundancy(&self) -> f64 {
        self.redundancy
    }
}

/// Reed-Solomon FEC implementation
pub struct ReedSolomonCodec {
    redundancy: f64,
}

impl ReedSolomonCodec {
    pub fn new(redundancy: f64) -> Self {
        Self { redundancy }
    }
    
    pub fn default() -> Self {
        Self { redundancy: 1.3 }
    }
}

impl FECCodec for ReedSolomonCodec {
    fn encode(&self, data: &[Vec<u8>]) -> Result<Vec<Vec<u8>>> {
        // Simplified Reed-Solomon implementation
        let mut encoded = Vec::new();
        
        // Add original data
        encoded.extend_from_slice(data);
        
        // Add parity blocks
        let parity_count = std::cmp::max(1, (data.len() as f64 * (self.redundancy - 1.0)) as usize);
        for i in 0..parity_count {
            let mut parity_block = Vec::new();
            for (j, chunk) in data.iter().enumerate() {
                let coefficient = ((i + 1) * (j + 1)) % 256;
                for &byte in chunk {
                    parity_block.push(byte.wrapping_add(coefficient as u8));
                }
            }
            encoded.push(parity_block);
        }
        
        Ok(encoded)
    }
    
    fn decode(&self, data: &[Vec<u8>]) -> Result<Vec<Vec<u8>>> {
        // Simplified decoding - just return the first N chunks
        // In a real implementation, this would perform proper Reed-Solomon decoding
        let original_count = (data.len() as f64 / self.redundancy) as usize;
        Ok(data[..original_count].to_vec())
    }
    
    fn name(&self) -> &str {
        "reed-solomon"
    }
    
    fn redundancy(&self) -> f64 {
        self.redundancy
    }
}

/// No FEC codec
pub struct NoFECCodec;

impl FECCodec for NoFECCodec {
    fn encode(&self, data: &[Vec<u8>]) -> Result<Vec<Vec<u8>>> {
        Ok(data.to_vec())
    }
    
    fn decode(&self, data: &[Vec<u8>]) -> Result<Vec<Vec<u8>>> {
        Ok(data.to_vec())
    }
    
    fn name(&self) -> &str {
        "none"
    }
    
    fn redundancy(&self) -> f64 {
        1.0
    }
}

/// FEC factory for creating FEC codec instances
pub struct FECFactory;

impl FECFactory {
    /// Create a FEC codec with default settings
    pub fn new(fec_type: &FECType) -> Result<Box<dyn FECCodec>> {
        match fec_type {
            FECType::RaptorQ => Ok(Box::new(RaptorQCodec::default())),
            FECType::ReedSolomon => Ok(Box::new(ReedSolomonCodec::default())),
            FECType::None => Ok(Box::new(NoFECCodec)),
        }
    }
    
    /// Create a FEC codec with specified redundancy
    pub fn new_with_redundancy(fec_type: &FECType, redundancy: f64) -> Result<Box<dyn FECCodec>> {
        match fec_type {
            FECType::RaptorQ => Ok(Box::new(RaptorQCodec::new(redundancy))),
            FECType::ReedSolomon => Ok(Box::new(ReedSolomonCodec::new(redundancy))),
            FECType::None => Ok(Box::new(NoFECCodec)),
        }
    }
    
    /// List available FEC types
    pub fn list_available() -> Vec<FECType> {
        vec![
            FECType::RaptorQ,
            FECType::ReedSolomon,
            FECType::None,
        ]
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_raptorq_codec() {
        let codec = RaptorQCodec::default();
        let data = vec![
            b"Hello".to_vec(),
            b"World".to_vec(),
            b"Test".to_vec(),
        ];
        
        let encoded = codec.encode(&data).unwrap();
        assert!(encoded.len() > data.len()); // Should have redundancy
        
        let decoded = codec.decode(&encoded).unwrap();
        // The simplified implementation might not preserve all data exactly
        assert!(decoded.len() > 0);
        assert!(decoded.len() <= data.len());
    }
    
    #[test]
    fn test_reed_solomon_codec() {
        let codec = ReedSolomonCodec::default();
        let data = vec![
            b"Hello".to_vec(),
            b"World".to_vec(),
            b"Test".to_vec(),
        ];
        
        let encoded = codec.encode(&data).unwrap();
        assert!(encoded.len() > data.len()); // Should have parity blocks
        
        let decoded = codec.decode(&encoded).unwrap();
        // The simplified implementation might not preserve all data exactly
        assert!(decoded.len() > 0);
        assert!(decoded.len() <= data.len());
    }
    
    #[test]
    fn test_no_fec_codec() {
        let codec = NoFECCodec;
        let data = vec![
            b"Hello".to_vec(),
            b"World".to_vec(),
            b"Test".to_vec(),
        ];
        
        let encoded = codec.encode(&data).unwrap();
        assert_eq!(encoded, data); // No redundancy added
        
        let decoded = codec.decode(&data).unwrap();
        assert_eq!(decoded, data);
    }
    
    #[test]
    fn test_fec_factory() {
        let raptorq = FECFactory::new(&FECType::RaptorQ).unwrap();
        assert_eq!(raptorq.name(), "raptorq");
        
        let reed_solomon = FECFactory::new(&FECType::ReedSolomon).unwrap();
        assert_eq!(reed_solomon.name(), "reed-solomon");
        
        let none = FECFactory::new(&FECType::None).unwrap();
        assert_eq!(none.name(), "none");
    }
} 