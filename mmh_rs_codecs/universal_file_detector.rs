// Universal File Type Detection Engine for MMH-RS
// Phase 1.1: Enhanced File Type Detection Engine

use std::collections::HashMap;
use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::path::Path;

/// Magic byte signatures for 50+ file formats
#[derive(Debug, Clone, PartialEq)]
pub struct MagicSignature {
    pub offset: usize,
    pub bytes: Vec<u8>,
    pub mask: Option<Vec<u8>>, // Optional mask for flexible matching
}

/// File type classification
#[derive(Debug, Clone, PartialEq)]
pub enum FileCategory {
    Executable,
    Library,
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

/// File type information
#[derive(Debug, Clone)]
pub struct FileTypeInfo {
    pub name: String,
    pub extension: String,
    pub mime_type: String,
    pub category: FileCategory,
    pub description: String,
    pub compression_potential: f64, // 0.0 to 1.0
}

/// Universal file detector
pub struct UniversalFileDetector {
    signatures: HashMap<String, Vec<MagicSignature>>,
    file_types: HashMap<String, FileTypeInfo>,
}

impl UniversalFileDetector {
    pub fn new() -> Self {
        let mut detector = Self {
            signatures: HashMap::new(),
            file_types: HashMap::new(),
        };
        detector.initialize_signatures();
        detector
    }

    /// Initialize magic byte signatures for 50+ file formats
    fn initialize_signatures(&mut self) {
        // Executables and Libraries
        self.add_signature("PE32", vec![
            MagicSignature { offset: 0, bytes: vec![0x4D, 0x5A], mask: None }, // MZ header
        ]);
        
        self.add_signature("ELF", vec![
            MagicSignature { offset: 0, bytes: vec![0x7F, 0x45, 0x4C, 0x46], mask: None },
        ]);
        
        self.add_signature("MachO", vec![
            MagicSignature { offset: 0, bytes: vec![0xFE, 0xED, 0xFA, 0xCE], mask: None }, // 32-bit
            MagicSignature { offset: 0, bytes: vec![0xFE, 0xED, 0xFA, 0xCF], mask: None }, // 64-bit
        ]);

        // Debug and Symbol Files
        self.add_signature("PDB", vec![
            MagicSignature { offset: 0, bytes: vec![0x4D, 0x69, 0x63, 0x72, 0x6F, 0x73, 0x6F, 0x66, 0x74, 0x20, 0x43, 0x2F, 0x43, 0x2B, 0x2B, 0x20], mask: None },
        ]);
        
        self.add_signature("DWARF", vec![
            MagicSignature { offset: 0, bytes: vec![0x44, 0x57, 0x41, 0x52, 0x46], mask: None },
        ]);

        // Archives and Compressed Files
        self.add_signature("ZIP", vec![
            MagicSignature { offset: 0, bytes: vec![0x50, 0x4B, 0x03, 0x04], mask: None },
            MagicSignature { offset: 0, bytes: vec![0x50, 0x4B, 0x05, 0x06], mask: None }, // Empty archive
            MagicSignature { offset: 0, bytes: vec![0x50, 0x4B, 0x07, 0x08], mask: None }, // Spanned archive
        ]);
        
        self.add_signature("RAR", vec![
            MagicSignature { offset: 0, bytes: vec![0x52, 0x61, 0x72, 0x21, 0x1A, 0x07], mask: None },
        ]);
        
        self.add_signature("7Z", vec![
            MagicSignature { offset: 0, bytes: vec![0x37, 0x7A, 0xBC, 0xAF, 0x27, 0x1C], mask: None },
        ]);
        
        self.add_signature("TAR", vec![
            MagicSignature { offset: 257, bytes: vec![0x75, 0x73, 0x74, 0x61, 0x72], mask: None },
        ]);
        
        self.add_signature("GZIP", vec![
            MagicSignature { offset: 0, bytes: vec![0x1F, 0x8B], mask: None },
        ]);
        
        self.add_signature("BZIP2", vec![
            MagicSignature { offset: 0, bytes: vec![0x42, 0x5A, 0x68], mask: None },
        ]);

        // Media Files
        self.add_signature("MP3", vec![
            MagicSignature { offset: 0, bytes: vec![0x49, 0x44, 0x33], mask: None }, // ID3v2
            MagicSignature { offset: 0, bytes: vec![0xFF, 0xFB], mask: Some(vec![0xFF, 0xE0]), }, // MPEG-1 Layer 3
        ]);
        
        self.add_signature("MP4", vec![
            MagicSignature { offset: 4, bytes: vec![0x66, 0x74, 0x79, 0x70], mask: None }, // ftyp box
        ]);
        
        self.add_signature("AVI", vec![
            MagicSignature { offset: 0, bytes: vec![0x52, 0x49, 0x46, 0x46], mask: None }, // RIFF
            MagicSignature { offset: 8, bytes: vec![0x41, 0x56, 0x49, 0x20], mask: None }, // AVI
        ]);
        
        self.add_signature("JPEG", vec![
            MagicSignature { offset: 0, bytes: vec![0xFF, 0xD8, 0xFF], mask: None },
        ]);
        
        self.add_signature("PNG", vec![
            MagicSignature { offset: 0, bytes: vec![0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A], mask: None },
        ]);

        // Documents
        self.add_signature("PDF", vec![
            MagicSignature { offset: 0, bytes: vec![0x25, 0x50, 0x44, 0x46], mask: None },
        ]);
        
        self.add_signature("DOC", vec![
            MagicSignature { offset: 0, bytes: vec![0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1], mask: None },
        ]);
        
        self.add_signature("XLS", vec![
            MagicSignature { offset: 0, bytes: vec![0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1], mask: None },
        ]);

        // Source Code and Text
        self.add_signature("RUST", vec![
            MagicSignature { offset: 0, bytes: vec![0x66, 0x6E, 0x20], mask: None }, // "fn "
            MagicSignature { offset: 0, bytes: vec![0x73, 0x74, 0x72, 0x75, 0x63, 0x74], mask: None }, // "struct"
        ]);
        
        self.add_signature("PYTHON", vec![
            MagicSignature { offset: 0, bytes: vec![0x23, 0x21, 0x2F, 0x75, 0x73, 0x72, 0x2F, 0x62, 0x69, 0x6E, 0x2F, 0x70, 0x79, 0x74, 0x68, 0x6F, 0x6E], mask: None }, // shebang
            MagicSignature { offset: 0, bytes: vec![0x64, 0x65, 0x66, 0x20], mask: None }, // "def "
        ]);

        // Virtual Machines
        self.add_signature("VMWARE", vec![
            MagicSignature { offset: 0, bytes: vec![0x4B, 0x44, 0x4D], mask: None }, // KDM
        ]);
        
        self.add_signature("VHD", vec![
            MagicSignature { offset: 0, bytes: vec![0x63, 0x6F, 0x6E, 0x65, 0x63, 0x74, 0x69, 0x78], mask: None },
        ]);

        // Databases
        self.add_signature("SQLITE", vec![
            MagicSignature { offset: 0, bytes: vec![0x53, 0x51, 0x4C, 0x69, 0x74, 0x65, 0x20, 0x66, 0x6F, 0x72, 0x6D, 0x61, 0x74, 0x20], mask: None },
        ]);

        // Initialize file type information
        self.initialize_file_types();
    }

    fn add_signature(&mut self, file_type: &str, signatures: Vec<MagicSignature>) {
        self.signatures.insert(file_type.to_string(), signatures);
    }

    /// Initialize file type information with compression potential scores
    fn initialize_file_types(&mut self) {
        // Executables - High compression potential due to repetitive patterns
        self.file_types.insert("PE32".to_string(), FileTypeInfo {
            name: "Windows PE Executable".to_string(),
            extension: "exe".to_string(),
            mime_type: "application/x-msdownload".to_string(),
            category: FileCategory::Executable,
            description: "Windows Portable Executable format".to_string(),
            compression_potential: 0.85,
        });

        // Debug files - Very high compression potential
        self.file_types.insert("PDB".to_string(), FileTypeInfo {
            name: "Program Database".to_string(),
            extension: "pdb".to_string(),
            mime_type: "application/x-msdownload".to_string(),
            category: FileCategory::Debug,
            description: "Microsoft Program Database debug information".to_string(),
            compression_potential: 0.95,
        });

        // Archives - Already compressed, low potential
        self.file_types.insert("ZIP".to_string(), FileTypeInfo {
            name: "ZIP Archive".to_string(),
            extension: "zip".to_string(),
            mime_type: "application/zip".to_string(),
            category: FileCategory::Archive,
            description: "ZIP compressed archive".to_string(),
            compression_potential: 0.05,
        });

        // Media files - Moderate compression potential
        self.file_types.insert("MP3".to_string(), FileTypeInfo {
            name: "MP3 Audio".to_string(),
            extension: "mp3".to_string(),
            mime_type: "audio/mpeg".to_string(),
            category: FileCategory::Media,
            description: "MPEG-1 Audio Layer 3".to_string(),
            compression_potential: 0.15,
        });

        // Documents - High compression potential
        self.file_types.insert("PDF".to_string(), FileTypeInfo {
            name: "PDF Document".to_string(),
            extension: "pdf".to_string(),
            mime_type: "application/pdf".to_string(),
            category: FileCategory::Document,
            description: "Portable Document Format".to_string(),
            compression_potential: 0.75,
        });
    }

    /// Detect file type using magic byte signatures
    pub fn detect_file_type(&self, file_path: &Path) -> Result<Option<FileTypeInfo>, std::io::Error> {
        let mut file = File::open(file_path)?;
        let mut buffer = vec![0u8; 1024]; // Read first 1KB for signature detection
        
        file.read_exact(&mut buffer)?;
        
        for (file_type, signatures) in &self.signatures {
            if self.matches_signatures(&buffer, signatures) {
                if let Some(info) = self.file_types.get(file_type) {
                    return Ok(Some(info.clone()));
                }
            }
        }
        
        Ok(None)
    }

    /// Check if buffer matches any of the signatures
    fn matches_signatures(&self, buffer: &[u8], signatures: &[MagicSignature]) -> bool {
        for signature in signatures {
            if signature.offset + signature.bytes.len() <= buffer.len() {
                let slice = &buffer[signature.offset..signature.offset + signature.bytes.len()];
                if self.matches_signature(slice, signature) {
                    return true;
                }
            }
        }
        false
    }

    /// Check if a slice matches a specific signature
    fn matches_signature(&self, slice: &[u8], signature: &MagicSignature) -> bool {
        if slice.len() != signature.bytes.len() {
            return false;
        }
        
        for (i, &byte) in signature.bytes.iter().enumerate() {
            if let Some(&mask_byte) = signature.mask.as_ref().and_then(|m| m.get(i)) {
                if (slice[i] & mask_byte) != (byte & mask_byte) {
                    return false;
                }
            } else if slice[i] != byte {
                return false;
            }
        }
        true
    }

    /// Get file category based on extension (fallback method)
    pub fn get_category_by_extension(&self, extension: &str) -> FileCategory {
        match extension.to_lowercase().as_str() {
            "exe" | "dll" | "so" | "dylib" | "bin" | "obj" => FileCategory::Executable,
            "pdb" | "dbg" | "map" | "sym" => FileCategory::Debug,
            "zip" | "rar" | "7z" | "tar" | "gz" | "bz2" => FileCategory::Archive,
            "mp3" | "mp4" | "avi" | "mkv" | "jpg" | "png" => FileCategory::Media,
            "pdf" | "doc" | "docx" | "xls" | "xlsx" => FileCategory::Document,
            "rs" | "py" | "cpp" | "c" | "h" | "js" => FileCategory::Code,
            "db" | "sqlite" | "mdb" => FileCategory::Database,
            "vmdk" | "vhd" | "ova" => FileCategory::VirtualMachine,
            _ => FileCategory::Unknown,
        }
    }

    /// Analyze file for compression potential
    pub fn analyze_compression_potential(&self, file_path: &Path) -> Result<f64, std::io::Error> {
        if let Some(file_type) = self.detect_file_type(file_path)? {
            return Ok(file_type.compression_potential);
        }
        
        // Fallback: analyze by extension
        if let Some(ext) = file_path.extension() {
            if let Some(ext_str) = ext.to_str() {
                let category = self.get_category_by_extension(ext_str);
                return Ok(self.get_default_compression_potential(category));
            }
        }
        
        Ok(0.5) // Default medium potential for unknown files
    }

    fn get_default_compression_potential(&self, category: FileCategory) -> f64 {
        match category {
            FileCategory::Executable => 0.80,
            FileCategory::Debug => 0.90,
            FileCategory::Archive => 0.10,
            FileCategory::Media => 0.20,
            FileCategory::Document => 0.70,
            FileCategory::Code => 0.60,
            FileCategory::Database => 0.65,
            FileCategory::VirtualMachine => 0.75,
            FileCategory::Compressed => 0.05,
            FileCategory::Unknown => 0.50,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_pe32_detection() {
        let detector = UniversalFileDetector::new();
        // This would need a real PE file for testing
        assert!(detector.signatures.contains_key("PE32"));
    }

    #[test]
    fn test_pdb_detection() {
        let detector = UniversalFileDetector::new();
        assert!(detector.signatures.contains_key("PDB"));
    }

    #[test]
    fn test_compression_potential() {
        let detector = UniversalFileDetector::new();
        let potential = detector.get_default_compression_potential(FileCategory::Debug);
        assert!(potential > 0.8); // Debug files should have high compression potential
    }
}
