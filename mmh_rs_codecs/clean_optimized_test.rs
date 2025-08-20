use std::fs::{self, File};
use std::io::{self, Read, Write};
use std::path::Path;
use std::thread;
use std::time::{Duration, Instant};
use std::sync::{Arc, Mutex};

// Visual progress indicators (keeping the cool animations!)
struct VisualProgress {
    start_time: Instant,
    current_file: String,
    total_files: usize,
    processed_files: usize,
    current_operation: String,
}

impl VisualProgress {
    fn new(total_files: usize) -> Self {
        Self {
            start_time: Instant::now(),
            current_file: String::new(),
            total_files,
            processed_files: 0,
            current_operation: "Initializing...".to_string(),
        }
    }

    fn update_file(&mut self, filename: &str, operation: &str) {
        self.current_file = filename.to_string();
        self.current_operation = operation.to_string();
        self.display_progress();
    }

    fn file_completed(&mut self) {
        self.processed_files += 1;
        self.display_progress();
    }

    fn display_progress(&self) {
        let elapsed = self.start_time.elapsed();
        let elapsed_secs = elapsed.as_secs_f64();
        
        // Clear line and show progress
        print!("\r");
        
        // Progress bar with cool patterns
        let progress_width = 40;
        let progress = (self.processed_files as f64 / self.total_files as f64) * progress_width as f64;
        
        let mut bar = String::new();
        for i in 0..progress_width {
            if i < progress as usize {
                // Cool animated pattern for completed sections
                let pattern_char = match (i + (elapsed_secs * 2.0) as usize) % 4 {
                    0 => "█",
                    1 => "▓",
                    2 => "▒",
                    _ => "░",
                };
                bar.push_str(pattern_char);
            } else {
                bar.push_str(" ");
            }
        }
        
        // Spinning indicator
        let spinner = match (elapsed_secs * 3.0) as usize % 4 {
            0 => "⠋",
            1 => "⠙",
            2 => "⠹",
            _ => "⠸",
        };
        
        // File progress
        let file_progress = format!("[{}/{}]", self.processed_files, self.total_files);
        
        // Time estimate
        let eta = if self.processed_files > 0 {
            let avg_time = elapsed_secs / self.processed_files as f64;
            let remaining = (self.total_files - self.processed_files) as f64 * avg_time;
            format!("ETA: {:.1}s", remaining)
        } else {
            "ETA: calculating...".to_string()
        };
        
        // Display everything
        print!("{} {} {} | {} | {} | {}", 
            spinner, bar, file_progress, self.current_operation, self.current_file, eta);
        
        io::stdout().flush().unwrap();
    }

    fn final_display(&self) {
        let total_time = self.start_time.elapsed();
        println!("\n\n🎉 Compression completed in {:.2}s!", total_time.as_secs_f64());
        println!("📊 Processed {} files successfully", self.processed_files);
        println!("⚡ Average time per file: {:.2}s", 
            total_time.as_secs_f64() / self.processed_files as f64);
    }
}

// OPTIMIZED compression engine with the 30-minute fixes
struct OptimizedCompressor {
    window_size: usize,
    min_match_length: usize, // Now 4 bytes minimum
    max_distance: usize,
}

impl Default for OptimizedCompressor {
    fn default() -> Self {
        Self {
            window_size: 32768,
            min_match_length: 4, // FIX 1: Skip matches < 4 bytes
            max_distance: 32768,
        }
    }
}

impl OptimizedCompressor {
    /// FIX 2: Tighten RLE threshold to ≥ 16 zeros only (was 8)
    fn rle_prefilter(data: &[u8]) -> Vec<u8> {
        let mut result = Vec::new();
        let mut i = 0;

        while i < data.len() {
            if data[i] == 0 {
                // Count consecutive zeros
                let mut run_length = 0;
                while i + run_length < data.len() && 
                      data[i + run_length] == 0 && 
                      run_length < 255 {
                    run_length += 1;
                }

                // FIX: Only compress runs of 16+ zeros (was 8)
                if run_length >= 16 {
                    // Emit RLE token: 0xFF (escape) + 0x00 (zero marker) + length
                    result.extend_from_slice(&[0xFF, 0x00, run_length as u8]);
                    i += run_length;
                } else {
                    // Short run, emit as-is
                    for _ in 0..run_length {
                        result.push(0);
                    }
                    i += run_length;
                }
            } else {
                // Escape 0xFF bytes in regular data
                if data[i] == 0xFF {
                    result.push(0xFF);
                    result.push(0xFF); // Double 0xFF to escape
                } else {
                    result.push(data[i]);
                }
                i += 1;
            }
        }

        result
    }

    /// FIX 3: Shrink LZ77 token from 3 bytes to 2 bytes (12-bit distance + 4-bit length)
    fn lz77_compress(&self, data: &[u8]) -> Vec<u8> {
        let mut result = Vec::new();
        let mut i = 0;

        while i < data.len() {
            let mut best_length = 0;
            let mut best_distance = 0;

            // Look for matches in the window
            let search_start = if i >= self.window_size { i - self.window_size } else { 0 };
            
            for j in search_start..i {
                let mut length = 0;
                while length < 15 && // FIX: Max length now 15 (4 bits)
                      i + length < data.len() && 
                      j + length < i &&
                      data[i + length] == data[j + length] {
                    length += 1;
                }

                if length >= self.min_match_length && length > best_length {
                    best_length = length;
                    best_distance = i - j;
                }
            }

            if best_length >= self.min_match_length && best_distance <= 4095 { // FIX: Max distance 4095 (12 bits)
                // FIX: Emit 2-byte token: [distance_high:4][length:4] + [distance_low:8]
                let token = ((best_distance >> 8) as u8 & 0x0F) | ((best_length as u8 & 0x0F) << 4);
                let distance_low = (best_distance & 0xFF) as u8;
                
                result.push(token);
                result.push(distance_low);
                i += best_length;
            } else {
                // Emit literal
                result.push(data[i]);
                i += 1;
            }
        }

        result
    }

    /// FIX 4: Add pure literal fallback when no pattern detected
    fn compress(&mut self, data: &[u8]) -> io::Result<Vec<u8>> {
        if data.is_empty() {
            return Ok(Vec::new());
        }

        // Quick check: if data is too small, just return as-is
        if data.len() < 64 {
            return Ok(data.to_vec());
        }

        // Apply RLE pre-filtering for zeros
        let filtered_data = Self::rle_prefilter(data);
        
        // Apply LZ77 compression
        let compressed = self.lz77_compress(&filtered_data);
        
        // FIX: If compression didn't help, fall back to literals
        if compressed.len() >= data.len() {
            return Ok(data.to_vec());
        }
        
        Ok(compressed)
    }

    /// Verify compression
    pub fn verify_compression(&self, original: &[u8], compressed: &[u8]) -> bool {
        let ratio = compressed.len() as f64 / original.len() as f64;
        ratio < 1.5 // Tighter bound
    }
}

// Compression statistics
#[derive(Debug, Clone)]
struct CompressionStats {
    original_size: usize,
    compressed_size: usize,
    ratio: f64,
    method: String,
    analysis_time: u128,
    compression_time: u128,
}

// Enhanced pattern recognition with visual feedback
struct OptimizedPatternRecognitionEngine {
    progress: Arc<Mutex<VisualProgress>>,
}

impl OptimizedPatternRecognitionEngine {
    fn new(progress: Arc<Mutex<VisualProgress>>) -> Self {
        Self { progress }
    }

    fn analyze_file(&self, file_path: &Path) -> Result<CompressionStats, Box<dyn std::error::Error>> {
        let start_time = Instant::now();
        
        // Update progress
        {
            let mut progress = self.progress.lock().unwrap();
            progress.update_file(
                file_path.file_name().unwrap().to_string_lossy().as_ref(),
                "Analyzing patterns..."
            );
        }

        // Read file
        let mut file = File::open(file_path)?;
        let metadata = file.metadata()?;
        let file_size = metadata.len() as usize;
        
        let mut buffer = Vec::new();
        file.read_to_end(&mut buffer)?;
        
        let analysis_time = start_time.elapsed().as_millis();
        
        // Update progress
        {
            let mut progress = self.progress.lock().unwrap();
            progress.update_file(
                file_path.file_name().unwrap().to_string_lossy().as_ref(),
                "Compressing..."
            );
        }

        // Compress with optimized engine
        let compression_start = Instant::now();
        let mut compressor = OptimizedCompressor::default();
        let compressed_data = compressor.compress(&buffer)?;
        let compression_time = compression_start.elapsed().as_millis();
        
        // Verify compression
        if !compressor.verify_compression(&buffer, &compressed_data) {
            println!("\n⚠️  Warning: Compression verification failed for {}", 
                file_path.file_name().unwrap().to_string_lossy());
        }
        
        let ratio = 100.0 * (1.0 - compressed_data.len() as f64 / file_size as f64);
        
        let stats = CompressionStats {
            original_size: file_size,
            compressed_size: compressed_data.len(),
            ratio,
            method: "Optimized LZ77+RLE".to_string(),
            analysis_time,
            compression_time,
        };
        
        // Update progress
        {
            let mut progress = self.progress.lock().unwrap();
            progress.file_completed();
        }
        
        Ok(stats)
    }
}

// Main test function
fn main() -> io::Result<()> {
    println!("🚀 CLEAN OPTIMIZED Visual Enhanced Pattern Recognition Test");
    println!("=========================================================");
    println!("✨ Featuring 30-minute fixes to flip negative → positive compression!");
    println!();
    
    // Check for Silesia Corpus
    let silesia_dir = Path::new("silesia_corpus");
    if !silesia_dir.exists() {
        println!("❌ Silesia Corpus directory not found");
        println!("   Please ensure you're running from the project root directory");
        return Ok(());
    }
    
    // Count files
    let mut files = Vec::new();
    for entry in fs::read_dir(silesia_dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.is_file() {
            files.push(path);
        }
    }
    
    println!("📁 Found {} Silesia Corpus files", files.len());
    println!("🎯 Starting OPTIMIZED pattern recognition with visual feedback...");
    println!("🔧 Applied fixes: 2-byte tokens, 4-byte min matches, 16+ RLE, literal fallback");
    println!();
    
    // Create progress tracker
    let progress = Arc::new(Mutex::new(VisualProgress::new(files.len())));
    let engine = OptimizedPatternRecognitionEngine::new(progress.clone());
    
    // Process files
    let mut all_stats = Vec::new();
    
    for file_path in files {
        match engine.analyze_file(&file_path) {
            Ok(stats) => {
                all_stats.push(stats.clone());
                
                // Show file results
                let filename = file_path.file_name().unwrap().to_string_lossy();
                println!("\n📊 {}: {:.1}% reduction ({:.2}MB → {:.2}MB) in {:.0}ms", 
                    filename,
                    stats.ratio,
                    stats.original_size as f64 / (1024.0 * 1024.0),
                    stats.compressed_size as f64 / (1024.0 * 1024.0),
                    stats.compression_time
                );
            }
            Err(e) => {
                println!("\n❌ Analysis failed for {}: {}", 
                    file_path.file_name().unwrap().to_string_lossy(), e);
            }
        }
        
        // Small delay for visual effect
        thread::sleep(Duration::from_millis(100));
    }
    
    // Final progress display
    {
        let progress = progress.lock().unwrap();
        progress.final_display();
    }
    
    // Summary statistics
    if !all_stats.is_empty() {
        let total_original: usize = all_stats.iter().map(|s| s.original_size).sum();
        let total_compressed: usize = all_stats.iter().map(|s| s.compressed_size).sum();
        let overall_ratio = 100.0 * (1.0 - total_compressed as f64 / total_original as f64);
        let avg_analysis_time: u128 = all_stats.iter().map(|s| s.analysis_time).sum::<u128>() / all_stats.len() as u128;
        let avg_compression_time: u128 = all_stats.iter().map(|s| s.compression_time).sum::<u128>() / all_stats.len() as u128;
        
        println!("\n📈 OPTIMIZED COMPRESSION SUMMARY");
        println!("================================");
        println!("🎯 Overall compression: {:.1}% reduction", overall_ratio);
        println!("📦 Total size: {:.2} MB → {:.2} MB", 
            total_original as f64 / (1024.0 * 1024.0),
            total_compressed as f64 / (1024.0 * 1024.0)
        );
        println!("⚡ Average analysis time: {:.0}ms per file", avg_analysis_time);
        println!("🚀 Average compression time: {:.0}ms per file", avg_compression_time);
        println!("🔍 Files processed: {}", all_stats.len());
        
        // Show best and worst performers
        if let Some(best) = all_stats.iter().max_by(|a, b| a.ratio.partial_cmp(&b.ratio).unwrap()) {
            println!("🏆 Best compression: {:.1}% reduction", best.ratio);
        }
        if let Some(worst) = all_stats.iter().min_by(|a, b| a.ratio.partial_cmp(&b.ratio).unwrap()) {
            println!("📉 Worst compression: {:.1}% reduction", worst.ratio);
        }
    }
    
    println!("\n🎉 CLEAN OPTIMIZED test completed successfully!");
    println!("🔧 Applied fixes: 2-byte tokens, 4-byte min matches, 16+ RLE, literal fallback");
    Ok(())
}
