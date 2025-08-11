#!/usr/bin/env python3
"""
Agent Exo-Suit V3.0 - Text Processor
Robust text processing with Unicode handling, emoji removal, and intelligent chunking
"""

import os
import re
import unicodedata
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import chardet

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextProcessor:
    """Advanced text processing with Unicode and emoji handling"""
    
    def __init__(self, 
                 chunk_size: int = 512,
                 chunk_overlap: int = 50,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 remove_emojis: bool = True,
                 normalize_unicode: bool = True,
                 preserve_code_structure: bool = True):
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_file_size = max_file_size
        self.remove_emojis = remove_emojis
        self.normalize_unicode = normalize_unicode
        self.preserve_code_structure = preserve_code_structure
        
        # Emoji patterns (comprehensive Unicode emoji ranges)
        self.emoji_patterns = self._compile_emoji_patterns()
        
        # Code file extensions
        self.code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.less',
            '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs',
            '.swift', '.kt', '.scala', '.ps1', '.sh', '.bash', '.zsh', '.fish'
        }
        
        # Documentation file extensions
        self.doc_extensions = {
            '.md', '.txt', '.rst', '.tex', '.adoc', '.wiki'
        }
        
        # Configuration file extensions
        self.config_extensions = {
            '.json', '.yaml', '.yml', '.xml', '.ini', '.cfg', '.conf', '.toml'
        }
    
    def _compile_emoji_patterns(self) -> List[re.Pattern]:
        """Compile comprehensive emoji detection patterns"""
        patterns = []
        
        # Basic emoji patterns
        emoji_ranges = [
            # Emoticons
            r'[\U0001F600-\U0001F64F]',  # Emoticons
            r'[\U0001F300-\U0001F5FF]',  # Miscellaneous Symbols and Pictographs
            r'[\U0001F680-\U0001F6FF]',  # Transport and Map Symbols
            r'[\U0001F1E0-\U0001F1FF]',  # Regional Indicator Symbols
            r'[\U00002600-\U000027BF]',  # Miscellaneous Symbols
            r'[\U0001F900-\U0001F9FF]',  # Supplemental Symbols and Pictographs
            r'[\U0001F018-\U0001F270]',  # Various symbols
            r'[\U0001F300-\U0001F5FF]',  # Miscellaneous Symbols and Pictographs
            r'[\U0001F600-\U0001F64F]',  # Emoticons
            r'[\U0001F680-\U0001F6FF]',  # Transport and Map Symbols
            r'[\U0001F1E0-\U0001F1FF]',  # Regional Indicator Symbols
            r'[\U00002600-\U000027BF]',  # Miscellaneous Symbols
            r'[\U0001F900-\U0001F9FF]',  # Supplemental Symbols and Pictographs
            r'[\U0001F018-\U0001F270]',  # Various symbols
            r'[\U0001F300-\U0001F5FF]',  # Miscellaneous Symbols and Pictographs
            r'[\U0001F600-\U0001F64F]',  # Emoticons
            r'[\U0001F680-\U0001F6FF]',  # Transport and Map Symbols
            r'[\U0001F1E0-\U0001F1FF]',  # Regional Indicator Symbols
            r'[\U00002600-\U000027BF]',  # Miscellaneous Symbols
            r'[\U0001F900-\U0001F9FF]',  # Supplemental Symbols and Pictographs
            r'[\U0001F018-\U0001F270]',  # Various symbols
        ]
        
        # Compile patterns
        for pattern in emoji_ranges:
            try:
                compiled = re.compile(pattern, re.UNICODE)
                patterns.append(compiled)
            except Exception as e:
                logger.warning(f"Failed to compile emoji pattern {pattern}: {e}")
        
        return patterns
    
    def detect_encoding(self, file_path: str) -> Tuple[str, float]:
        """Detect file encoding with confidence score"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB for detection
                result = chardet.detect(raw_data)
                return result['encoding'], result['confidence']
        except Exception as e:
            logger.warning(f"Encoding detection failed for {file_path}: {e}")
            return 'utf-8', 0.0
    
    def read_file_safely(self, file_path: str) -> Optional[str]:
        """Read file content with robust encoding handling"""
        try:
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                logger.warning(f"File too large: {file_path} ({file_size / 1024 / 1024:.1f}MB)")
                return None
            
            # Detect encoding
            encoding, confidence = self.detect_encoding(file_path)
            
            # Try detected encoding first
            if confidence > 0.7:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    logger.debug(f"Successfully read {file_path} with {encoding} encoding")
                    return content
                except UnicodeDecodeError:
                    logger.debug(f"Detected encoding {encoding} failed, trying fallbacks")
            
            # Fallback encodings
            fallback_encodings = ['utf-8', 'cp1252', 'latin-1', 'iso-8859-1']
            
            for fallback_encoding in fallback_encodings:
                try:
                    with open(file_path, 'r', encoding=fallback_encoding) as f:
                        content = f.read()
                    logger.debug(f"Successfully read {file_path} with {fallback_encoding} encoding")
                    return content
                except UnicodeDecodeError:
                    continue
            
            # Last resort: read as bytes and decode with errors='ignore'
            try:
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='ignore')
                logger.warning(f"Read {file_path} with lossy decoding")
                return content
            except Exception as e:
                logger.error(f"Failed to read {file_path}: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return None
    
    def clean_text(self, text: str, file_extension: str = '') -> str:
        """Clean text by removing emojis and normalizing Unicode"""
        if not text:
            return text
        
        cleaned_text = text
        
        # Remove emojis if requested
        if self.remove_emojis:
            cleaned_text = self._remove_emojis(cleaned_text)
        
        # Normalize Unicode if requested
        if self.normalize_unicode:
            cleaned_text = self._normalize_unicode(cleaned_text)
        
        # Preserve code structure for code files
        if self.preserve_code_structure and file_extension.lower() in self.code_extensions:
            cleaned_text = self._preserve_code_structure(cleaned_text)
        
        return cleaned_text
    
    def _remove_emojis(self, text: str) -> str:
        """Remove emojis from text"""
        if not text:
            return text
        
        # Apply all emoji patterns
        for pattern in self.emoji_patterns:
            text = pattern.sub('', text)
        
        # Additional emoji removal for edge cases
        # Remove emoji modifiers and combining characters
        text = re.sub(r'[\U0001F3FB-\U0001F3FF]', '', text)  # Skin tone modifiers
        text = re.sub(r'[\U0000200D]', '', text)  # Zero width joiner
        text = re.sub(r'[\U0000FE0F]', '', text)  # Variation selector
        
        return text
    
    def _normalize_unicode(self, text: str) -> str:
        """Normalize Unicode characters"""
        if not text:
            return text
        
        # Normalize to NFC form (most compatible)
        text = unicodedata.normalize('NFC', text)
        
        # Replace common problematic characters
        replacements = {
            '\u2018': "'",  # Left single quotation mark
            '\u2019': "'",  # Right single quotation mark
            '\u201C': '"',  # Left double quotation mark
            '\u201D': '"',  # Right double quotation mark
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u2026': '...', # Horizontal ellipsis
            '\u00A0': ' ',  # Non-breaking space
            '\u00B0': ' degrees',  # Degree sign
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _preserve_code_structure(self, text: str) -> str:
        """Preserve important code structure elements"""
        if not text:
            return text
        
        # Preserve function and class definitions
        # Preserve import statements
        # Preserve comments
        # Preserve string literals
        
        # This is a simplified version - in production you'd use proper parsing
        return text
    
    def chunk_text(self, text: str, file_extension: str = '') -> List[str]:
        """Split text into overlapping chunks with intelligent boundaries"""
        if not text:
            return []
        
        # Clean text first
        cleaned_text = self.clean_text(text, file_extension)
        
        if len(cleaned_text) <= self.chunk_size:
            return [cleaned_text]
        
        chunks = []
        start = 0
        
        while start < len(cleaned_text):
            end = start + self.chunk_size
            
            # Try to find a good break point
            if end < len(cleaned_text):
                # Look for sentence boundaries
                sentence_breaks = ['.', '!', '?', '\n\n', '\n']
                best_break = end
                
                for break_char in sentence_breaks:
                    # Look backwards from end for a good break point
                    for i in range(end, max(start + self.chunk_size // 2, start), -1):
                        if cleaned_text[i:i+len(break_char)] == break_char:
                            best_break = i + len(break_char)
                            break
                    if best_break != end:
                        break
                
                # If no good break found, look for word boundaries
                if best_break == end:
                    for i in range(end, max(start + self.chunk_size // 2, start), -1):
                        if cleaned_text[i].isspace():
                            best_break = i + 1
                            break
                
                end = best_break
            
            # Extract chunk
            chunk = cleaned_text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
            # Ensure we don't get stuck in infinite loop
            if start >= len(cleaned_text) - self.chunk_overlap:
                # Add remaining text as final chunk
                remaining = cleaned_text[start:].strip()
                if remaining:
                    chunks.append(remaining)
                break
        
        return chunks
    
    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a single file and return chunks with metadata"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                return []
            
            # Read file content
            content = self.read_file_safely(file_path)
            if content is None:
                return []
            
            # Get file information
            file_stats = os.stat(file_path)
            file_extension = Path(file_path).suffix.lower()
            
            # Determine file type
            if file_extension in self.code_extensions:
                file_type = 'code'
            elif file_extension in self.doc_extensions:
                file_type = 'documentation'
            elif file_extension in self.config_extensions:
                file_type = 'configuration'
            else:
                file_type = 'other'
            
            # Chunk the text
            chunks = self.chunk_text(content, file_extension)
            
            # Create metadata for each chunk
            file_chunks = []
            for chunk_index, chunk in enumerate(chunks):
                try:
                    chunk_data = {
                        'file_path': file_path,
                        'file_type': file_type,
                        'file_extension': file_extension,
                        'chunk_index': chunk_index,
                        'chunk_text': chunk,
                        'chunk_size': len(chunk),
                        'file_size': file_stats.st_size,
                        'total_chunks': len(chunks),
                        'processing_info': {
                            'emojis_removed': self.remove_emojis,
                            'unicode_normalized': self.normalize_unicode,
                            'code_structure_preserved': self.preserve_code_structure
                        }
                    }
                    file_chunks.append(chunk_data)
                except Exception as e:
                    logger.error(f"Error processing chunk {chunk_index} from {file_path}: {e}")
                    continue
            
            logger.info(f"Processed {file_path}: {len(chunks)} chunks")
            return file_chunks
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return []
    
    def process_files_batch(self, file_paths: List[str], 
                           max_workers: Optional[int] = None) -> List[Dict[str, Any]]:
        """Process multiple files in batch"""
        import multiprocessing as mp
        
        if max_workers is None:
            max_workers = min(mp.cpu_count(), 8)
        
        logger.info(f"Processing {len(file_paths)} files with {max_workers} workers")
        
        all_chunks = []
        
        # Process files in parallel if multiple workers
        if max_workers > 1 and len(file_paths) > 1:
            try:
                with mp.Pool(max_workers) as pool:
                    results = pool.map(self.process_file, file_paths)
                
                for result in results:
                    all_chunks.extend(result)
                    
            except Exception as e:
                logger.warning(f"Parallel processing failed, falling back to sequential: {e}")
                # Fallback to sequential processing
                for file_path in file_paths:
                    chunks = self.process_file(file_path)
                    all_chunks.extend(chunks)
        else:
            # Sequential processing
            for file_path in file_paths:
                chunks = self.process_file(file_path)
                all_chunks.extend(chunks)
        
        logger.info(f"Total chunks generated: {len(all_chunks)}")
        return all_chunks
    
    def get_processing_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about processed chunks"""
        if not chunks:
            return {}
        
        stats = {
            'total_chunks': len(chunks),
            'total_files': len(set(chunk['file_path'] for chunk in chunks)),
            'file_types': {},
            'extensions': {},
            'chunk_sizes': [],
            'total_text_length': 0
        }
        
        for chunk in chunks:
            # File types
            file_type = chunk.get('file_type', 'unknown')
            stats['file_types'][file_type] = stats['file_types'].get(file_type, 0) + 1
            
            # Extensions
            ext = chunk.get('file_extension', 'unknown')
            stats['extensions'][ext] = stats['extensions'].get(ext, 0) + 1
            
            # Chunk sizes
            chunk_size = chunk.get('chunk_size', 0)
            stats['chunk_sizes'].append(chunk_size)
            stats['total_text_length'] += chunk_size
        
        # Calculate averages
        if stats['chunk_sizes']:
            stats['avg_chunk_size'] = sum(stats['chunk_sizes']) / len(stats['chunk_sizes'])
            stats['min_chunk_size'] = min(stats['chunk_sizes'])
            stats['max_chunk_size'] = max(stats['chunk_sizes'])
        
        return stats


def main():
    """Test the text processor"""
    print("Testing Text Processor...")
    
    # Create processor
    processor = TextProcessor(
        chunk_size=512,
        chunk_overlap=50,
        remove_emojis=True,
        normalize_unicode=True
    )
    
    # Test text cleaning
            test_text = "Hello! This is a test with Unicode characters "
    cleaned = processor.clean_text(test_text)
    print(f"Original: {test_text}")
    print(f"Cleaned: {cleaned}")
    
    # Test chunking
    long_text = "This is a long text. " * 100
    chunks = processor.chunk_text(long_text)
    print(f"\nGenerated {len(chunks)} chunks")
    print(f"First chunk: {chunks[0][:100]}...")
    
    # Test file processing (if test file exists)
    test_file = "test-file.txt"
    if os.path.exists(test_file):
        chunks = processor.process_file(test_file)
        print(f"\nProcessed test file: {len(chunks)} chunks")
        
        stats = processor.get_processing_stats(chunks)
        print(f"Processing stats: {stats}")


if __name__ == "__main__":
    main()
