#!/usr/bin/env python3
"""
Build FAISS index for RAG system with full CPU+GPU dual-mode support.
Supports: CPU-only, GPU-only, and CPU+GPU hybrid modes.
"""
import os
import json
import argparse
import pathlib
import time
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Dict, Tuple, Optional
import numpy as np

# GPU/CPU detection and imports
try:
    import torch
    import faiss
    from sentence_transformers import SentenceTransformer
    GPU_AVAILABLE = True
    print("🚀 GPU libraries detected")
except ImportError as e:
    print(f"⚠️ GPU libraries not available: {e}")
    GPU_AVAILABLE = False

# CPU fallback imports
try:
    import numpy as np
    print("✅ CPU libraries available")
except ImportError as e:
    print(f"❌ Critical: numpy not available: {e}")
    exit(1)

class DualModeRAGBuilder:
    """Advanced RAG builder with CPU+GPU dual-mode support"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.embedding_model = config.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.chunk_tokens = int(config.get('CHUNK_TOKENS', 512))
        self.overlap = int(config.get('CHUNK_OVERLAP', 50))
        self.faiss_index_path = config.get('FAISS_INDEX_PATH', 'rag/index.faiss')
        self.rag_meta_path = config.get('RAG_META_PATH', 'rag/meta.jsonl')
        
        # Device configuration
        self.use_gpu = config.get('USE_GPU', 'true').lower() == 'true'
        self.use_cpu = config.get('USE_CPU', 'true').lower() == 'true'
        self.hybrid_mode = config.get('HYBRID_MODE', 'true').lower() == 'true'
        
        # Device detection
        self.gpu_device = None
        self.cpu_device = 'cpu'
        self.available_devices = []
        
        self.setup_devices()
        self.setup_models()
    
    def setup_devices(self):
        """Detect and configure available devices"""
        print("🔍 Detecting available devices...")
        
        # GPU detection
        if GPU_AVAILABLE and self.use_gpu:
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                print(f"🎮 Found {gpu_count} CUDA device(s)")
                
                for i in range(gpu_count):
                    gpu_name = torch.cuda.get_device_name(i)
                    gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                    print(f"  GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
                
                self.gpu_device = 'cuda:0'  # Use primary GPU
                self.available_devices.append(('gpu', self.gpu_device))
                print(f"✅ GPU mode enabled: {self.gpu_device}")
            else:
                print("⚠️ CUDA not available")
        
        # CPU detection
        if self.use_cpu:
            cpu_count = mp.cpu_count()
            print(f"🖥️ CPU cores available: {cpu_count}")
            self.available_devices.append(('cpu', self.cpu_device))
            print(f"✅ CPU mode enabled: {cpu_count} cores")
        
        # Hybrid mode validation
        if self.hybrid_mode and len(self.available_devices) >= 2:
            print("🚀 Hybrid CPU+GPU mode enabled")
        elif len(self.available_devices) == 1:
            device_type, device = self.available_devices[0]
            print(f"🎯 Single device mode: {device_type.upper()} ({device})")
        else:
            print("❌ No devices available")
            exit(1)
    
    def setup_models(self):
        """Initialize models for all available devices"""
        self.models = {}
        
        for device_type, device in self.available_devices:
            try:
                print(f"🔧 Loading model for {device_type}: {device}")
                
                if device_type == 'gpu':
                    # GPU model with optimizations
                    model = SentenceTransformer(self.embedding_model, device=device)
                    model = model.to(device)
                    
                    # Warm up GPU
                    dummy_input = ["GPU warmup test"]
                    _ = model.encode(dummy_input, device=device)
                    
                    print(f"✅ GPU model loaded and warmed up")
                    
                else:
                    # CPU model
                    model = SentenceTransformer(self.embedding_model, device=device)
                    print(f"✅ CPU model loaded")
                
                self.models[device_type] = model
                
            except Exception as e:
                print(f"⚠️ Failed to load model for {device_type}: {e}")
                continue
        
        if not self.models:
            print("❌ No models loaded successfully")
            exit(1)
    
    def chunks(self, text: str, n: int, ov: int) -> List[str]:
        """Split text into overlapping chunks with semantic boundaries"""
        words = text.split()
        step = n - ov
        chunks = []
        
        for i in range(0, len(words), step):
            chunk = ' '.join(words[i:i+n])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def process_file_chunk(self, args: Tuple) -> Optional[Dict]:
        """Process a single file chunk (for parallel processing)"""
        file_path, chunk_index, chunk_text = args
        
        try:
            return {
                "path": file_path,
                "chunk": chunk_index,
                "text": chunk_text,
                "tokens": len(chunk_text.split())
            }
        except Exception as e:
            print(f"⚠️ Error processing chunk {chunk_index} from {file_path}: {e}")
            return None
    
    def process_files_parallel(self, file_paths: List[str]) -> Tuple[List[str], List[Dict]]:
        """Process files in parallel using available devices"""
        print(f"📁 Processing {len(file_paths)} files...")
        
        all_texts = []
        all_meta = []
        
        # Process files in batches
        batch_size = 10
        for i in range(0, len(file_paths), batch_size):
            batch_paths = file_paths[i:i + batch_size]
            print(f"  Processing batch {i//batch_size + 1}/{(len(file_paths) + batch_size - 1)//batch_size}")
            
            for file_path in batch_paths:
                try:
                    if not os.path.exists(file_path):
                        print(f"⚠️ File not found: {file_path}")
                        continue
                    
                    # Skip large files
                    if os.path.getsize(file_path) > 1000000:  # 1MB limit
                        print(f"⚠️ Skipping large file: {file_path}")
                        continue
                    
                    with open(file_path, encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if not content.strip():
                        continue
                    
                    # Generate chunks
                    chunks = self.chunks(content, self.chunk_tokens, self.overlap)
                    
                    for chunk_index, chunk in enumerate(chunks):
                        all_texts.append(chunk)
                        all_meta.append({
                            "path": file_path,
                            "chunk": chunk_index,
                            "tokens": len(chunk.split())
                        })
                        
                except Exception as e:
                    print(f"⚠️ Error processing {file_path}: {e}")
                    continue
        
        print(f"✅ Generated {len(all_texts)} chunks from {len(file_paths)} files")
        return all_texts, all_meta
    
    def encode_embeddings_hybrid(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using hybrid CPU+GPU processing"""
        if not texts:
            return np.array([])
        
        print(f"🧠 Generating embeddings for {len(texts)} chunks...")
        start_time = time.time()
        
        # Strategy: Use GPU for large batches, CPU for smaller ones
        if len(self.available_devices) >= 2 and len(texts) > 100:
            # Hybrid mode: GPU for main batch, CPU for remainder
            gpu_batch_size = min(1000, len(texts) // 2)
            cpu_batch_size = len(texts) - gpu_batch_size
            
            print(f"🚀 GPU processing {gpu_batch_size} chunks")
            gpu_texts = texts[:gpu_batch_size]
            gpu_embeddings = self.models['gpu'].encode(
                gpu_texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=True
            ).astype('float32')
            
            if cpu_batch_size > 0:
                print(f"🖥️ CPU processing {cpu_batch_size} chunks")
                cpu_texts = texts[gpu_batch_size:]
                cpu_embeddings = self.models['cpu'].encode(
                    cpu_texts,
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                    show_progress_bar=True
                ).astype('float32')
                
                # Combine embeddings
                all_embeddings = np.vstack([gpu_embeddings, cpu_embeddings])
            else:
                all_embeddings = gpu_embeddings
                
        elif 'gpu' in self.models:
            # GPU-only mode
            print(f"🚀 GPU-only processing {len(texts)} chunks")
            all_embeddings = self.models['gpu'].encode(
                texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=True
            ).astype('float32')
            
        else:
            # CPU-only mode
            print(f"🖥️ CPU-only processing {len(texts)} chunks")
            all_embeddings = self.models['cpu'].encode(
                texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=True
            ).astype('float32')
        
        elapsed_time = time.time() - start_time
        print(f"✅ Embeddings generated in {elapsed_time:.2f}s")
        print(f"📊 Embedding shape: {all_embeddings.shape}")
        
        return all_embeddings
    
    def build_faiss_index(self, embeddings: np.ndarray) -> str:
        """Build and save FAISS index"""
        if embeddings.size == 0:
            print("❌ No embeddings to index")
            return ""
        
        print("🔨 Building FAISS index...")
        start_time = time.time()
        
        # Create index based on embedding dimension
        dimension = embeddings.shape[1]
        
        # Use GPU-accelerated index if available
        if 'gpu' in self.models and faiss.get_num_gpus() > 0:
            print("🚀 Creating GPU-accelerated FAISS index")
            # Create CPU index first, then move to GPU
            index = faiss.IndexFlatIP(dimension)
            index.add(embeddings)
            
            # Convert to GPU index if possible
            try:
                res = faiss.StandardGpuResources()
                gpu_index = faiss.index_cpu_to_gpu(res, 0, index)
                print("✅ GPU index created successfully")
                index = gpu_index
            except Exception as e:
                print(f"⚠️ GPU index conversion failed, using CPU: {e}")
        else:
            print("🖥️ Creating CPU FAISS index")
            index = faiss.IndexFlatIP(dimension)
            index.add(embeddings)
        
        # Save index
        print(f"💾 Saving index to {self.faiss_index_path}")
        faiss.write_index(index, self.faiss_index_path)
        
        elapsed_time = time.time() - start_time
        print(f"✅ Index built in {elapsed_time:.2f}s")
        
        return self.faiss_index_path
    
    def save_metadata(self, metadata: List[Dict]) -> str:
        """Save metadata to JSONL file"""
        print(f"💾 Saving metadata to {self.rag_meta_path}")
        
        with open(self.rag_meta_path, 'w', encoding='utf-8') as f:
            for item in metadata:
                f.write(json.dumps(item) + '\n')
        
        print(f"✅ Metadata saved: {len(metadata)} items")
        return self.rag_meta_path
    
    def run(self, file_paths: List[str]) -> int:
        """Main execution pipeline"""
        try:
            # Process files
            texts, metadata = self.process_files_parallel(file_paths)
            
            if not texts:
                print("❌ No text chunks generated")
                return 1
            
            # Generate embeddings
            embeddings = self.encode_embeddings_hybrid(texts)
            
            # Build index
            index_path = self.build_faiss_index(embeddings)
            
            # Save metadata
            meta_path = self.save_metadata(metadata)
            
            # Summary
            print("\n🎉 RAG Index Build Complete!")
            print(f"📁 Files processed: {len(file_paths)}")
            print(f"🧩 Chunks generated: {len(texts)}")
            print(f"🧠 Embeddings: {embeddings.shape}")
            print(f"💾 Index saved: {index_path}")
            print(f"📋 Metadata saved: {meta_path}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return 1


def load_config():
    """Load configuration from .env file"""
    config = {}
    env_file = '.env'
    
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value
    
    return config


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Build FAISS index with CPU+GPU dual-mode support')
    parser.add_argument('--filelist', required=True, help='File containing list of files to index')
    parser.add_argument('--gpu', action='store_true', help='Force GPU mode')
    parser.add_argument('--cpu', action='store_true', help='Force CPU mode')
    parser.add_argument('--hybrid', action='store_true', help='Force hybrid CPU+GPU mode')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Override config with command line args
    if args.gpu:
        config['USE_GPU'] = 'true'
        config['USE_CPU'] = 'false'
        config['HYBRID_MODE'] = 'false'
    elif args.cpu:
        config['USE_GPU'] = 'false'
        config['USE_CPU'] = 'true'
        config['HYBRID_MODE'] = 'false'
    elif args.hybrid:
        config['USE_GPU'] = 'true'
        config['USE_CPU'] = 'true'
        config['HYBRID_MODE'] = 'true'
    
    # Read file list
    if not os.path.exists(args.filelist):
        print(f"❌ File list not found: {args.filelist}")
        return 1
    
    with open(args.filelist, 'r', encoding='utf-8') as f:
        paths = [line.strip() for line in f if line.strip()]
    
    if not paths:
        print("❌ No files in file list")
        return 1
    
    # Initialize and run builder
    builder = DualModeRAGBuilder(config)
    return builder.run(paths)


if __name__ == '__main__':
    exit(main())
