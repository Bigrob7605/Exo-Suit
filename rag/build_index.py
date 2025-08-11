#!/usr/bin/env python3
"""
Agent Exo-Suit V3.0 - Dual-Mode RAG Index Builder
Supports both CPU and GPU modes with automatic fallback
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import torch
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import faiss
    TORCH_AVAILABLE = True
except ImportError as e:
    print(f"GPU libraries not available: {e}")
    TORCH_AVAILABLE = False

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import faiss
    CPU_AVAILABLE = True
except ImportError as e:
    print(f"CPU libraries not available: {e}")
    CPU_AVAILABLE = False

if not TORCH_AVAILABLE and not CPU_AVAILABLE:
    print("No RAG libraries available. Please install required packages.")
    sys.exit(1)

class DualModeRAGBuilder:
    """Dual-mode RAG index builder with CPU/GPU support"""
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 chunk_size: int = 512,
                 chunk_overlap: int = 50,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 device: Optional[str] = None):
        
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_file_size = max_file_size
        self.device = device
        self.model = None
        self.gpu_device = None
        self.cpu_count = os.cpu_count()
        
        # Auto-detect device if not specified
        if self.device is None:
            self.device = self._auto_detect_device()
        
        # Initialize model
        self._initialize_model()
    
    def _auto_detect_device(self) -> str:
        """Auto-detect optimal device configuration"""
        if TORCH_AVAILABLE and torch.cuda.is_available():
            self.gpu_device = torch.cuda.get_device_name(0)
            if self.gpu_device:
                print(f"GPU mode enabled: {self.gpu_device}")
                return "cuda"
            else:
                print("CUDA not available")
        
        if CPU_AVAILABLE:
            print(f"CPU mode enabled: {self.cpu_count} cores")
            return "cpu"
        
        return "cpu"
    
    def _initialize_model(self):
        """Initialize the sentence transformer model"""
        device_type = "GPU" if self.device == "cuda" else "CPU"
        device = self.device if self.device else "cpu"
        
        print(f"Single device mode: {device_type.upper()} ({device})")
        
        try:
            print(f"Loading model for {device_type}: {device}")
            self.model = SentenceTransformer(self.model_name, device=device)
            
            if self.device == "cuda":
                # Warm up GPU
                dummy_text = ["GPU warmup text"]
                _ = self.model.encode(dummy_text)
                print(f"GPU model loaded and warmed up")
            else:
                print(f"CPU model loaded")
                
        except Exception as e:
            print(f"Failed to load model for {device_type}: {e}")
            # Fallback to CPU if GPU fails
            if self.device == "cuda" and CPU_AVAILABLE:
                print("Falling back to CPU mode")
                self.device = "cpu"
                self.model = SentenceTransformer(self.model_name, device="cpu")
            else:
                raise
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
            # Ensure we don't get stuck in infinite loop
            if start >= len(text) - self.chunk_overlap:
                break
        
        return chunks
    
    def _process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a single file and return chunks with metadata"""
        try:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return []
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                print(f"Skipping large file: {file_path}")
                return []
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Split into chunks
            chunks = self._chunk_text(content)
            
            # Create metadata for each chunk
            file_chunks = []
            for chunk_index, chunk in enumerate(chunks):
                try:
                    chunk_data = {
                        'file_path': file_path,
                        'chunk_index': chunk_index,
                        'chunk_text': chunk,
                        'chunk_size': len(chunk),
                        'file_size': file_size,
                        'file_extension': Path(file_path).suffix,
                        'total_chunks': len(chunks)
                    }
                    file_chunks.append(chunk_data)
                except Exception as e:
                    print(f"Error processing chunk {chunk_index} from {file_path}: {e}")
                    continue
            
            return file_chunks
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return []
    
    def build_index(self, 
                   file_paths: List[str], 
                   output_dir: str = "context/vec",
                   index_name: str = "index") -> Dict[str, Any]:
        """Build the RAG index from file paths"""
        
        print(f"Processing {len(file_paths)} files...")
        
        # Process all files
        all_chunks = []
        for file_path in file_paths:
            chunks = self._process_file(file_path)
            all_chunks.extend(chunks)
        
        print(f"Generated {len(all_chunks)} chunks from {len(file_paths)} files")
        
        if not all_chunks:
            print("No chunks generated. Exiting.")
            return {}
        
        # Extract text for embedding
        all_texts = [chunk['chunk_text'] for chunk in all_chunks]
        
        # Generate embeddings
        print(f"Generating embeddings using {self.device.upper()}...")
        start_time = time.time()
        
        try:
            all_embeddings = self.model.encode(all_texts, show_progress_bar=True)
            elapsed_time = time.time() - start_time
            print(f"Embeddings generated in {elapsed_time:.2f}s")
            print(f"Embedding shape: {all_embeddings.shape}")
        except Exception as e:
            print(f"Embedding generation failed: {e}")
            return {}
        
        # Create FAISS index
        print("Creating FAISS index...")
        dimension = all_embeddings.shape[1]
        
        if self.device == "cuda":
            # GPU index
            try:
                res = faiss.StandardGpuResources()
                index = faiss.IndexFlatIP(dimension)
                gpu_index = faiss.index_cpu_to_gpu(res, 0, index)
                gpu_index.add(all_embeddings.astype('float32'))
                
                # Convert back to CPU for saving
                index = faiss.index_gpu_to_cpu(gpu_index)
                print("GPU index created successfully")
            except Exception as e:
                print(f"GPU index conversion failed, using CPU: {e}")
                index = faiss.IndexFlatIP(dimension)
                index.add(all_embeddings.astype('float32'))
        else:
            # CPU index
            index = faiss.IndexFlatIP(dimension)
            index.add(all_embeddings.astype('float32'))
        
        # Save index
        os.makedirs(output_dir, exist_ok=True)
        index_path = os.path.join(output_dir, f"{index_name}.faiss")
        faiss.write_index(index, index_path)
        
        # Save metadata
        metadata_path = os.path.join(output_dir, f"{index_name}_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, indent=2, ensure_ascii=False)
        
        # Save embeddings info
        info_path = os.path.join(output_dir, f"{index_name}_info.json")
        info = {
            'model_name': self.model_name,
            'device_used': self.device,
            'total_files': len(file_paths),
            'total_chunks': len(all_chunks),
            'embedding_dimension': dimension,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'build_time': elapsed_time,
            'index_size_mb': os.path.getsize(index_path) / (1024 * 1024)
        }
        
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2)
        
        print(f"Index built in {elapsed_time:.2f}s")
        print(f"Index saved to: {index_path}")
        print(f"Metadata saved: {len(all_chunks)} items")
        print(f"Info saved to: {info_path}")
        
        return {
            'index_path': index_path,
            'metadata_path': metadata_path,
            'info_path': info_path,
            'total_chunks': len(all_chunks),
            'embedding_dimension': dimension,
            'build_time': elapsed_time
        }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Dual-Mode RAG Index Builder")
    parser.add_argument("--input", "-i", required=True, help="Input directory or file list")
    parser.add_argument("--output", "-o", default="context/vec", help="Output directory")
    parser.add_argument("--model", "-m", default="all-MiniLM-L6-v2", help="Model name")
    parser.add_argument("--device", "-d", choices=["cpu", "cuda", "auto"], default="auto", help="Device to use")
    parser.add_argument("--chunk-size", "-c", type=int, default=512, help="Chunk size")
    parser.add_argument("--chunk-overlap", "-l", type=int, default=50, help="Chunk overlap")
    parser.add_argument("--max-file-size", "-s", type=int, default=10*1024*1024, help="Max file size in bytes")
    
    args = parser.parse_args()
    
    # Determine device
    if args.device == "auto":
        device = None
    else:
        device = args.device
    
    # Get file paths
    if os.path.isdir(args.input):
        # Input is a directory
        file_paths = []
        for root, dirs, files in os.walk(args.input):
            for file in files:
                if file.endswith(('.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.json', '.xml', '.yaml', '.yml')):
                    file_paths.append(os.path.join(root, file))
    else:
        # Input is a file list
        with open(args.input, 'r') as f:
            file_paths = [line.strip() for line in f if line.strip()]
    
    if not file_paths:
        print("No files found to process")
        return 1
    
    # Build index
    builder = DualModeRAGBuilder(
        model_name=args.model,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        max_file_size=args.max_file_size,
        device=device
    )
    
    try:
        result = builder.build_index(file_paths, args.output)
        if result:
            print("\nRAG Index Build Complete!")
            return 0
        else:
            print("Index building failed")
            return 1
    except Exception as e:
        print(f"Error building index: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
