#!/usr/bin/env python3
"""
Retrieve relevant documents using FAISS index with full CPU+GPU dual-mode support.
Supports: CPU-only, GPU-only, and CPU+GPU hybrid modes.
"""
import os
import json
import argparse
import time
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

class DualModeRAGRetriever:
    """Advanced RAG retriever with CPU+GPU dual-mode support"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.embedding_model = config.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.index_path = config.get('FAISS_INDEX_PATH', 'rag/index.faiss')
        self.meta_path = config.get('RAG_META_PATH', 'rag/meta.jsonl')
        
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
        self.load_index_and_metadata()
    
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
            import multiprocessing as mp
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
    
    def load_index_and_metadata(self):
        """Load FAISS index and metadata"""
        print("📚 Loading RAG index and metadata...")
        
        # Check if index exists
        if not os.path.exists(self.index_path):
            print(f"❌ Index not found at {self.index_path}")
            print("Run embed.ps1 first to build the index.")
            exit(1)
        
        if not os.path.exists(self.meta_path):
            print(f"❌ Metadata not found at {self.meta_path}")
            print("Run embed.ps1 first to build the metadata.")
            exit(1)
        
        try:
            # Load FAISS index
            print("🔨 Loading FAISS index...")
            self.index = faiss.read_index(self.index_path)
            print(f"✅ Index loaded: {self.index.ntotal} vectors")
            
            # Load metadata
            print("📋 Loading metadata...")
            with open(self.meta_path, 'r', encoding='utf-8') as f:
                self.metadata = [json.loads(line) for line in f if line.strip()]
            print(f"✅ Metadata loaded: {len(self.metadata)} entries")
            
        except Exception as e:
            print(f"❌ Failed to load index/metadata: {e}")
            exit(1)
    
    def encode_query_hybrid(self, query: str) -> np.ndarray:
        """Encode query using optimal available device"""
        print(f"🧠 Encoding query: {query}")
        
        # Strategy: Use GPU if available, otherwise CPU
        if 'gpu' in self.models:
            print("🚀 Using GPU for query encoding")
            device = self.gpu_device
            model = self.models['gpu']
        else:
            print("🖥️ Using CPU for query encoding")
            device = self.cpu_device
            model = self.models['cpu']
        
        try:
            query_emb = model.encode(
                [query], 
                normalize_embeddings=True,
                convert_to_numpy=True,
                device=device
            )
            print(f"✅ Query encoded successfully")
            return query_emb
            
        except Exception as e:
            print(f"⚠️ Query encoding failed: {e}")
            # Fallback to CPU if GPU failed
            if 'cpu' in self.models and device != self.cpu_device:
                print("🔄 Falling back to CPU encoding")
                return self.models['cpu'].encode(
                    [query], 
                    normalize_embeddings=True,
                    convert_to_numpy=True
                )
            else:
                raise e
    
    def search_index_hybrid(self, query_emb: np.ndarray, topk: int) -> Tuple[np.ndarray, np.ndarray]:
        """Search index using optimal available device"""
        print(f"🔍 Searching for top {topk} results...")
        
        # Strategy: Use GPU-accelerated search if available
        if 'gpu' in self.models and hasattr(faiss, 'StandardGpuResources'):
            try:
                print("🚀 Using GPU-accelerated search")
                res = faiss.StandardGpuResources()
                gpu_index = faiss.index_cpu_to_gpu(res, 0, self.index)
                
                scores, indices = gpu_index.search(query_emb, topk)
                print("✅ GPU search completed")
                return scores, indices
                
            except Exception as e:
                print(f"⚠️ GPU search failed: {e}")
                print("🔄 Falling back to CPU search")
        
        # CPU search
        print("🖥️ Using CPU search")
        scores, indices = self.index.search(query_emb, topk)
        print("✅ CPU search completed")
        return scores, indices
    
    def retrieve_documents(self, query: str, topk: int = 60) -> List[Dict]:
        """Main retrieval pipeline"""
        try:
            start_time = time.time()
            
            # Encode query
            query_emb = self.encode_query_hybrid(query)
            
            # Search index
            scores, indices = self.search_index_hybrid(query_emb, topk)
            
            # Format results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.metadata):
                    result = self.metadata[idx].copy()
                    result['score'] = float(score)
                    result['relevance'] = self._score_to_relevance(score)
                    results.append(result)
            
            elapsed_time = time.time() - start_time
            print(f"✅ Retrieved {len(results)} results in {elapsed_time:.3f}s")
            
            return results
            
        except Exception as e:
            print(f"❌ Retrieval failed: {e}")
            return []
    
    def _score_to_relevance(self, score: float) -> str:
        """Convert similarity score to human-readable relevance"""
        if score >= 0.8:
            return "Very High"
        elif score >= 0.6:
            return "High"
        elif score >= 0.4:
            return "Medium"
        elif score >= 0.2:
            return "Low"
        else:
            return "Very Low"
    
    def save_results(self, results: List[Dict], output_path: str = 'rag/context_topk.jsonl'):
        """Save retrieval results to file"""
        print(f"💾 Saving results to {output_path}")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for result in results:
                    f.write(json.dumps(result) + '\n')
            
            print(f"✅ Results saved: {len(results)} entries")
            return output_path
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            return None
    
    def display_results_summary(self, results: List[Dict]):
        """Display a summary of retrieval results"""
        if not results:
            print("❌ No results to display")
            return
        
        print("\n📊 Retrieval Results Summary:")
        print("=" * 50)
        
        # Top results
        print(f"🏆 Top 5 Results:")
        for i, result in enumerate(results[:5], 1):
            path = result.get('path', 'Unknown')
            score = result.get('score', 0)
            relevance = result.get('relevance', 'Unknown')
            print(f"  {i}. {path}")
            print(f"     Score: {score:.4f} | Relevance: {relevance}")
        
        # Statistics
        if len(results) > 5:
            print(f"\n📈 Additional Results: {len(results) - 5} more")
        
        # Score distribution
        scores = [r.get('score', 0) for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        
        print(f"\n📊 Score Statistics:")
        print(f"  Average: {avg_score:.4f}")
        print(f"  Maximum: {max_score:.4f}")
        print(f"  Minimum: {min_score:.4f}")
        
        # File type distribution
        file_types = {}
        for result in results:
            path = result.get('path', '')
            if path:
                ext = os.path.splitext(path)[1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1
        
        if file_types:
            print(f"\n📁 File Type Distribution:")
            for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {ext}: {count} files")


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
    parser = argparse.ArgumentParser(description='Retrieve documents with CPU+GPU dual-mode support')
    parser.add_argument('--query', required=True, help='Search query')
    parser.add_argument('--topk', type=int, default=60, help='Number of top results to return')
    parser.add_argument('--gpu', action='store_true', help='Force GPU mode')
    parser.add_argument('--cpu', action='store_true', help='Force CPU mode')
    parser.add_argument('--hybrid', action='store_true', help='Force hybrid CPU+GPU mode')
    parser.add_argument('--output', help='Output file path for results')
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
    
    # Initialize retriever
    retriever = DualModeRAGRetriever(config)
    
    # Perform retrieval
    results = retriever.retrieve_documents(args.query, args.topk)
    
    if results:
        # Save results
        output_path = args.output or 'rag/context_topk.jsonl'
        saved_path = retriever.save_results(results, output_path)
        
        # Display summary
        retriever.display_results_summary(results)
        
        if saved_path:
            print(f"\n🎉 Retrieval completed successfully!")
            print(f"📁 Results saved to: {saved_path}")
            return 0
        else:
            print("\n⚠️ Retrieval completed but failed to save results")
            return 1
    else:
        print("\n❌ Retrieval failed - no results returned")
        return 1


if __name__ == '__main__':
    exit(main())
