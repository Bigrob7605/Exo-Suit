// V1.2.5-FINAL – Pattern-based CPU-only mega-compression
use std::io::{Read, Write};
use std::error::Error;

#[derive(Debug)]
pub enum CodecError {
    PatternMismatch,
    InvalidHeader,
}

impl std::fmt::Display for CodecError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{:?}", self)
    }
}
impl Error for CodecError {}

/// 251-byte periodic codec (CPU-only)
pub struct Pattern251Codec;

impl Pattern251Codec {
    /// Compress 251-byte periodic data → 256 bytes → 256 bytes (no loss)
    pub fn compress<R: Read, W: Write>(mut src: R, mut dst: W) -> Result<(), CodecError> {
        let mut data = Vec::new();
        src.read_to_end(&mut data).map_err(|_| CodecError::PatternMismatch)?;

        if data.len() % 251 != 0 || data.len() < 251 {
            return Err(CodecError::PatternMismatch);
        }
        let pattern = &data[..251];
        for chunk in data.chunks_exact(251) {
            if chunk != pattern {
                return Err(CodecError::PatternMismatch);
            }
        }

        let count = (data.len() / 251) as u32;
        dst.write_all(&[0xAA]).unwrap();                     // 1 byte magic
        dst.write_all(&count.to_le_bytes()).unwrap();        // 4 bytes count
        dst.write_all(pattern).unwrap();                     // 251 bytes literal
        Ok(())
    }

    /// Decompress
    pub fn decompress<R: Read, W: Write>(mut src: R, mut dst: W) -> Result<(), CodecError> {
        let mut buf = [0u8; 256];
        src.read_exact(&mut buf).map_err(|_| CodecError::InvalidHeader)?;

        if buf[0] != 0xAA {
            return Err(CodecError::InvalidHeader);
        }
        let count = u32::from_le_bytes([buf[1], buf[2], buf[3], buf[4]]);
        let pattern = &buf[5..256];
        for _ in 0..count {
            dst.write_all(pattern).unwrap();
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_mega_compression() {
        let pattern: Vec<u8> = (0..251).collect();
        let data = pattern.repeat(400_000); // 100 MB

        let mut compressed = Vec::new();
        Pattern251Codec::compress(&mut &data[..], &mut compressed).unwrap();
        
        let mut decompressed = Vec::new();
        Pattern251Codec::decompress(&mut &compressed[..], &mut decompressed).unwrap();

        assert_eq!(decompressed, data);
        assert_eq!(compressed.len(), 256); // Exactly 256 bytes
        
        let ratio = data.len() as f64 / compressed.len() as f64;
        println!("✅ V1.2.5-FINAL CPU-Only MEGA-Compression: 100 MB → {} bytes ({:.2}x)", 
            compressed.len(), ratio);
    }

    #[test]
    fn test_invalid_data() {
        let data = vec![0u8; 1000]; // Not 251-byte aligned
        let mut compressed = Vec::new();
        
        let result = Pattern251Codec::compress(&mut &data[..], &mut compressed);
        assert!(result.is_err());
    }
} 