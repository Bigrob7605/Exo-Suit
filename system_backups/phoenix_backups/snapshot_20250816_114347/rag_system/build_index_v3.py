#!/usr/bin/env python3
"""
Agent Exo-Suit V3.0 - RAG Index Builder
Robust RAG index building with CPU/GPU support and comprehensive error handling
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import glob

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our custom modules
try:
    from device_manager import DeviceManager
    from text_processor import TextProcessor
    from embedding_engine import EmbeddingEngine
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure all required modules are in the same directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_build.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RAGIndexBuilder:
    """Comprehensive RAG index builder with device management and error handling"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize components
        self.device_manager = None
        self.text_processor = None
        self.embedding_engine = None
        
        # Processing state
        self.processed_files = []
        self.failed_files = []
        self.total_chunks = 0
        self.start_time = None
        
        # Initialize the system
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize all system components"""
        logger.info("Initializing RAG Index Builder V3.0...")
        
        try:
            # Initialize device manager
            logger.info("Initializing device manager...")
            self.device_manager = DeviceManager(self.config)
            
            # Print system capabilities
            self.device_manager.print_system_summary()
            
            # Validate requirements
            requirements_ok, missing_packages = self.device_manager.validate_requirements()
            if not requirements_ok:
                logger.warning(f"Missing packages: {missing_packages}")
                logger.warning("Some features may not work properly")
            
            # Get optimal configuration
            device_config = self.device_manager.get_optimal_configuration()
            logger.info(f"Using device configuration: {device_config['mode']}")
            
            # Initialize text processor
            logger.info("Initializing text processor...")
            self.text_processor = TextProcessor(
                chunk_size=self.config.get('chunk_size', 512),
                chunk_overlap=self.config.get('chunk_overlap', 50),
                remove_emojis=self.config.get('remove_emojis', True),
                normalize_unicode=self.config.get('normalize_unicode', True)
            )
            
            # Initialize embedding engine
            logger.info("Initializing embedding engine...")
            self.embedding_engine = EmbeddingEngine(
                model_name=self.config.get('model_name', 'all-MiniLM-L6-v2'),
                device_mode=device_config['mode'],
                batch_size=device_config.get('batch_size', 32),
                fallback_strategy=device_config.get('fallback_strategy', 'cpu_fallback')
            )
            
            logger.info("System initialization completed successfully")
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            raise
    
    def discover_files(self, source_paths: List[str], 
                      file_patterns: Optional[List[str]] = None) -> List[str]:
        """Discover files to process"""
        if file_patterns is None:
            file_patterns = [
                '**/*.py', '**/*.md', '**/*.txt', '**/*.json', '**/*.yaml', '**/*.yml',
                '**/*.ps1', '**/*.sh', '**/*.js', '**/*.ts', '**/*.html', '**/*.css',
                '**/*.java', '**/*.cpp', '**/*.c', '**/*.h', '**/*.cs', '**/*.php'
            ]
        
        discovered_files = []
        
        for source_path in source_paths:
            if not os.path.exists(source_path):
                logger.warning(f"Source path does not exist: {source_path}")
                continue
            
            if os.path.isfile(source_path):
                discovered_files.append(source_path)
            elif os.path.isdir(source_path):
                for pattern in file_patterns:
                    pattern_path = os.path.join(source_path, pattern)
                    files = glob.glob(pattern_path, recursive=True)
                    discovered_files.extend(files)
        
        # Remove duplicates and filter out non-text files
        discovered_files = list(set(discovered_files))
        discovered_files = [f for f in discovered_files if self._is_text_file(f)]
        
        logger.info(f"Discovered {len(discovered_files)} files to process")
        return discovered_files
    
    def _is_text_file(self, file_path: str) -> bool:
        """Check if file is a text file that can be processed"""
        try:
            # Check file size (skip very large files)
            if os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10MB
                return False
            
            # Check file extension
            text_extensions = {
                '.py', '.md', '.txt', '.json', '.yaml', '.yml', '.xml', '.ini', '.cfg',
                '.ps1', '.sh', '.bash', '.zsh', '.js', '.ts', '.jsx', '.tsx', '.html',
                '.css', '.scss', '.less', '.java', '.cpp', '.c', '.h', '.hpp', '.cs',
                '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala'
            }
            
            file_ext = Path(file_path).suffix.lower()
            if file_ext in text_extensions:
                return True
            
            # Try to read first few bytes to check if it's text
            try:
                with open(file_path, 'rb') as f:
                    sample = f.read(1024)
                    # Check if it's mostly text (printable ASCII/UTF-8)
                    text_chars = sum(1 for b in sample if 32 <= b <= 126 or b in [9, 10, 13])
                    return text_chars / len(sample) > 0.7
            except:
                return False
                
        except Exception:
            return False
    
    def process_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Process files and generate chunks"""
        logger.info(f"Processing {len(file_paths)} files...")
        
        self.start_time = time.time()
        all_chunks = []
        
        # Process files in batches
        batch_size = 10  # Process 10 files at a time
        for i in range(0, len(file_paths), batch_size):
            batch_files = file_paths[i:i + batch_size]
            batch_start = time.time()
            
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(file_paths) + batch_size - 1)//batch_size}")
            
            try:
                # Process batch
                batch_chunks = self.text_processor.process_files_batch(batch_files)
                all_chunks.extend(batch_chunks)
                
                # Update progress
                self.total_chunks += len(batch_chunks)
                batch_time = time.time() - batch_start
                
                logger.info(f"Batch completed: {len(batch_chunks)} chunks in {batch_time:.2f}s")
                
                # Track processed files
                for file_path in batch_files:
                    if any(chunk['file_path'] == file_path for chunk in batch_chunks):
                        self.processed_files.append(file_path)
                    else:
                        self.failed_files.append(file_path)
                
            except Exception as e:
                logger.error(f"Batch processing failed: {e}")
                # Mark all files in batch as failed
                self.failed_files.extend(batch_files)
        
        logger.info(f"File processing completed: {len(self.processed_files)} successful, {len(self.failed_files)} failed")
        logger.info(f"Total chunks generated: {self.total_chunks}")
        
        return all_chunks
    
    def build_index(self, chunks: List[Dict[str, Any]], 
                   output_dir: str = "rag") -> Dict[str, str]:
        """Build FAISS index from chunks"""
        logger.info("Building FAISS index...")
        
        if not chunks:
            raise ValueError("No chunks provided for index building")
        
        try:
            # Extract text content
            texts = [chunk['chunk_text'] for chunk in chunks]
            
            # Generate embeddings
            logger.info("Generating embeddings...")
            embeddings = self.embedding_engine.generate_embeddings(texts)
            
            # Create FAISS index
            logger.info("Creating FAISS index...")
            index = self.embedding_engine.create_faiss_index(embeddings)
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Save index
            index_path = os.path.join(output_dir, "index.faiss")
            self.embedding_engine.save_index(index, index_path)
            
            # Save metadata
            metadata_path = os.path.join(output_dir, "meta.jsonl")
            self._save_metadata(chunks, metadata_path)
            
            # Save processing report
            report_path = os.path.join(output_dir, "build_report.json")
            self._save_build_report(report_path)
            
            logger.info("Index building completed successfully")
            
            return {
                'index_path': index_path,
                'metadata_path': metadata_path,
                'report_path': report_path
            }
            
        except Exception as e:
            logger.error(f"Index building failed: {e}")
            raise
    
    def _save_metadata(self, chunks: List[Dict[str, Any]], output_path: str):
        """Save chunk metadata to JSONL file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for chunk in chunks:
                    # Clean chunk data for JSON serialization
                    clean_chunk = {
                        'file_path': chunk['file_path'],
                        'file_type': chunk['file_type'],
                        'file_extension': chunk['file_extension'],
                        'chunk_index': chunk['chunk_index'],
                        'chunk_text': chunk['chunk_text'],
                        'chunk_size': chunk['chunk_size'],
                        'file_size': chunk['file_size'],
                        'total_chunks': chunk['total_chunks']
                    }
                    f.write(json.dumps(clean_chunk, ensure_ascii=False) + '\n')
            
            logger.info(f"Metadata saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            raise
    
    def _save_build_report(self, output_path: str):
        """Save comprehensive build report"""
        try:
            total_time = time.time() - self.start_time if self.start_time else 0
            
            # Get processing stats
            processing_stats = self.text_processor.get_processing_stats([])  # Will be updated with actual chunks
            
            # Get embedding stats
            embedding_stats = self.embedding_engine.get_performance_stats()
            
            # Get device info
            device_summary = self.device_manager.get_system_summary()
            
            report = {
                'build_info': {
                    'version': '3.0',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'total_time_seconds': total_time,
                    'status': 'completed'
                },
                'file_processing': {
                    'total_files': len(self.processed_files) + len(self.failed_files),
                    'successful_files': len(self.processed_files),
                    'failed_files': len(self.failed_files),
                    'total_chunks': self.total_chunks,
                    'processing_stats': processing_stats
                },
                'embedding': {
                    'model_used': self.embedding_engine.model_name,
                    'device_used': embedding_stats['device_used'],
                    'total_embeddings': embedding_stats['total_embeddings'],
                    'total_time': embedding_stats['total_time'],
                    'avg_time_per_embedding': embedding_stats['avg_time_per_embedding'],
                    'fallbacks_used': embedding_stats['fallbacks_used']
                },
                'system_capabilities': device_summary,
                'configuration': {
                    'chunk_size': self.text_processor.chunk_size,
                    'chunk_overlap': self.text_processor.chunk_overlap,
                    'batch_size': self.embedding_engine.batch_size,
                    'device_mode': self.embedding_engine.device_mode
                },
                'processed_files': self.processed_files,
                'failed_files': self.failed_files
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Build report saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save build report: {e}")
    
    def run_full_pipeline(self, source_paths: List[str], 
                         output_dir: str = "rag") -> Dict[str, str]:
        """Run the complete RAG index building pipeline"""
        logger.info("Starting RAG index building pipeline...")
        
        try:
            # Discover files
            file_paths = self.discover_files(source_paths)
            
            if not file_paths:
                raise ValueError("No files discovered to process")
            
            # Process files
            chunks = self.process_files(file_paths)
            
            if not chunks:
                raise ValueError("No chunks generated from file processing")
            
            # Build index
            output_paths = self.build_index(chunks, output_dir)
            
            # Print summary
            self._print_summary()
            
            return output_paths
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
    
    def _print_summary(self):
        """Print build summary"""
        total_time = time.time() - self.start_time if self.start_time else 0
        
        print("\n" + "="*60)
        print("AGENT EXO-SUIT V3.0 - RAG INDEX BUILD COMPLETE")
        print("="*60)
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Files processed: {len(self.processed_files)}")
        print(f"Files failed: {len(self.failed_files)}")
        print(f"Total chunks: {self.total_chunks}")
        print(f"Device used: {self.embedding_engine.device_type}")
        print(f"Model: {self.embedding_engine.model_name}")
        
        if self.failed_files:
            print(f"\nFailed files:")
            for failed_file in self.failed_files[:5]:  # Show first 5
                print(f"  - {failed_file}")
            if len(self.failed_files) > 5:
                print(f"  ... and {len(self.failed_files) - 5} more")
        
        print("="*60)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Build RAG index with CPU/GPU support')
    parser.add_argument('--source', nargs='+', required=True, 
                       help='Source paths to scan for files')
    parser.add_argument('--output', default='rag', 
                       help='Output directory for index and metadata')
    parser.add_argument('--chunk-size', type=int, default=512,
                       help='Chunk size for text processing')
    parser.add_argument('--chunk-overlap', type=int, default=50,
                       help='Chunk overlap for text processing')
    parser.add_argument('--model', default='all-MiniLM-L6-v2',
                       help='Sentence transformer model to use')
    parser.add_argument('--device', choices=['auto', 'cpu', 'gpu', 'hybrid'], default='auto',
                       help='Device mode for processing')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for embedding generation')
    
    args = parser.parse_args()
    
    try:
        # Create configuration
        config = {
            'chunk_size': args.chunk_size,
            'chunk_overlap': args.chunk_overlap,
            'model_name': args.model,
            'device_mode': args.device,
            'batch_size': args.batch_size,
            'remove_emojis': True,
            'normalize_unicode': True
        }
        
        # Create builder
        builder = RAGIndexBuilder(config)
        
        # Run pipeline
        output_paths = builder.run_full_pipeline(args.source, args.output)
        
        print(f"\nOK - RAG index built successfully!")
        print(f"Index: {output_paths['index_path']}")
        print(f"Metadata: {output_paths['metadata_path']}")
        print(f"Report: {output_paths['report_path']}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Build failed: {e}")
        print(f"\nFAILED - RAG index build failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
