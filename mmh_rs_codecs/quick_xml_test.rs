use std::collections::HashMap;
use std::time::Instant;

// Simplified test of just the Enhanced RLE + LZ77 compression
struct EnhancedRleLz77Hybrid {
    window_size: usize,
    look_ahead_size: usize,
    min_match_length: usize,
}

impl EnhancedRleLz77Hybrid {
    pub fn new() -> Self {
        Self {
            window_size: 64 * 1024,
            look_ahead_size: 16 * 1024,
            min_match_length: 4,
        }
    }
    
    pub fn compress(&self, data: &[u8]) -> Vec<u8> {
        let mut compressed = Vec::new();
        let mut i = 0;
        
        while i < data.len() {
            // RLE for repeated characters
            let rle_count = self.count_repeated_chars(&data[i..]);
            if rle_count >= 3 {
                compressed.push(0xFF); // RLE marker
                compressed.push(data[i]);
                compressed.push(rle_count as u8);
                i += rle_count;
                continue;
            }
            
            // LZ77 for longer matches
            if let Some((offset, length)) = self.find_longest_match_improved(data, i) {
                if length >= self.min_match_length {
                    compressed.push(0xFE); // LZ77 marker
                    compressed.extend_from_slice(&(offset as u16).to_le_bytes());
                    compressed.push(length as u8);
                    i += length;
                    continue;
                }
            }
            
            // Literal byte
            compressed.push(data[i]);
            i += 1;
        }
        
        compressed
    }
    
    pub fn decompress(&self, src: &[u8]) -> Result<Vec<u8>, &'static str> {
        let mut out = Vec::new();
        let mut i = 0;

        while i < src.len() {
            match src.get(i) {
                Some(&0xFF) => {                        // RLE
                    if i + 2 >= src.len() { return Err("truncated RLE"); }
                    let byte   = src[i + 1];
                    let count  = src[i + 2] as usize;
                    out.extend(std::iter::repeat(byte).take(count));
                    i += 3;
                }
                Some(&0xFE) => {                        // LZ77
                    if i + 3 >= src.len() { return Err("truncated LZ77"); }
                    let offset = u16::from_le_bytes([src[i + 1], src[i + 2]]) as usize;
                    let length = src[i + 3] as usize;
                    let start  = out.len().checked_sub(offset)
                        .ok_or("invalid LZ77 offset")?;
                    let slice  = &out[start..out.len().min(start + length)];
                    let temp_slice = slice.to_vec();
                    out.extend_from_slice(&temp_slice);
                    i += 4;
                }
                Some(&b) => {                           // literal
                    out.push(b);
                    i += 1;
                }
                None => return Err("out of bounds"),
            }
        }
        Ok(out)
    }
    
    fn count_repeated_chars(&self, data: &[u8]) -> usize {
        if data.is_empty() { return 0; }
        let first = data[0];
        data.iter().take_while(|&&b| b == first).count()
    }
    
    fn find_longest_match_improved(&self, data: &[u8], current_pos: usize) -> Option<(usize, usize)> {
        if current_pos == 0 { return None; }
        
        let window_start = if current_pos > self.window_size { current_pos - self.window_size } else { 0 };
        let look_ahead_end = std::cmp::min(current_pos + self.look_ahead_size, data.len());
        
        let mut best_match = None;
        let mut best_length = 0;
        
        for search_pos in (window_start..current_pos).rev() {
            let mut match_length = 0;
            
            while current_pos + match_length < look_ahead_end 
                && search_pos + match_length < current_pos 
                && data[search_pos + match_length] == data[current_pos + match_length] {
                match_length += 1;
            }
            
            if match_length >= self.min_match_length && match_length > best_length {
                let offset = current_pos - search_pos;
                best_length = match_length;
                best_match = Some((offset, match_length));
                
                if match_length >= 64 { break; }
            }
        }
        
        best_match
    }
}

fn main() {
    println!("🧪 QUICK XML LOSSESS COMPRESSION TEST");
    println!("=====================================");
    
    // Test 1: Simple XML sample
    let sample_xml = r#"<?xml version="1.0"?>
<root>
    <element>test</element>
    <element>test</element>
    <element>test</element>
</root>"#.as_bytes();
    
    println!("📝 Testing with sample XML ({} bytes)", sample_xml.len());
    
    let compressor = EnhancedRleLz77Hybrid::new();
    let start_time = Instant::now();
    
    let compressed = compressor.compress(sample_xml);
    let compression_time = start_time.elapsed();
    
    println!("✅ Compression completed in {:?}", compression_time);
    println!("📊 Original size: {} bytes", sample_xml.len());
    println!("📊 Compressed size: {} bytes", compressed.len());
    println!("📊 Compression ratio: {:.2}x", sample_xml.len() as f64 / compressed.len() as f64);
    
    // Test decompression
    match compressor.decompress(&compressed) {
        Ok(decompressed) => {
            if sample_xml == decompressed {
                println!("✅ LOSSLESS COMPRESSION VERIFIED!");
                println!("🔍 Round-trip test: PASSED");
            } else {
                println!("❌ LOSSLESS COMPRESSION FAILED!");
                println!("🔍 Round-trip test: FAILED");
            }
        },
        Err(e) => {
            println!("❌ Decompression failed: {}", e);
        }
    }
    
    // Test 2: Try with small portion of real XML if available
    println!("\n🔍 Testing with real XML data...");
    match std::fs::read("../silesia_corpus/xml") {
        Ok(xml_data) => {
            let small_xml = &xml_data[..std::cmp::min(1024, xml_data.len())]; // First 1KB
            println!("📝 Testing with real XML sample ({} bytes)", small_xml.len());
            
            let compressed = compressor.compress(small_xml);
            let ratio = small_xml.len() as f64 / compressed.len() as f64;
            
            println!("📊 Compression ratio: {:.2}x", ratio);
            
            match compressor.decompress(&compressed) {
                Ok(decompressed) => {
                    if small_xml == decompressed {
                        println!("✅ REAL XML: LOSSLESS COMPRESSION VERIFIED!");
                    } else {
                        println!("❌ REAL XML: LOSSLESS COMPRESSION FAILED!");
                    }
                },
                Err(e) => {
                    println!("❌ Real XML decompression failed: {}", e);
                }
            }
        },
        Err(e) => {
            println!("⚠️  Real XML file not found: {}", e);
        }
    }
    
    println!("\n🎯 TEST COMPLETED!");
}
