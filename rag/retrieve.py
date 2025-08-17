# Agent Exo-Suit V4.0 - Advanced RAG Retriever
# Dual-mode CPU+GPU retrieval with intelligent fallback

import os
import sys
import json
import time
import logging
import argparse
import faiss
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# GPU imports with fallback
GPU_AVAILABLE = False
try:
    import torch
    from sentence_transformers import SentenceTransformer
    GPU_AVAILABLE = True
    logger.info("GPU libraries available")
except ImportError as e:
    logger.warning(f"GPU libraries not available: {e}")
    GPU_AVAILABLE = False

# CPU fallback imports
try:
    import numpy as np
    logger.info("CPU libraries available")
except ImportError as e:
    logger.error(f"Critical: numpy not available: {e}")
    sys.exit(1)

class DualModeRAGRetrieverV4:
    """Advanced RAG retriever V4.0 with CPU+GPU dual-mode support and enhanced performance"""
    
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
        logger.info("Detecting available devices...")
        
        # GPU detection
        if GPU_AVAILABLE and self.use_gpu:
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                logger.info(f"Found {gpu_count} CUDA device(s)")
                
                for i in range(gpu_count):
                    gpu_name = torch.cuda.get_device_name(i)
                    gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                    logger.info(f"  GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
                
                self.gpu_device = 'cuda:0'  # Use primary GPU
                self.available_devices.append(('gpu', self.gpu_device))
                logger.info(f"GPU mode enabled: {self.gpu_device}")
            else:
                logger.warning("CUDA not available")
        
        # CPU detection
        if self.use_cpu:
            import multiprocessing as mp
            cpu_count = mp.cpu_count()
            logger.info(f"CPU cores available: {cpu_count}")
            self.available_devices.append(('cpu', self.cpu_device))
            logger.info(f"CPU mode enabled: {cpu_count} cores")
        
        # Hybrid mode validation
        if self.hybrid_mode and len(self.available_devices) >= 2:
            logger.info("Hybrid CPU+GPU mode enabled")
        elif len(self.available_devices) == 1:
            device_type, device = self.available_devices[0]
            logger.info(f"Single device mode: {device_type.upper()} ({device})")
        else:
            logger.error("No devices available")
            sys.exit(1)
    
    def setup_models(self):
        """Initialize models for all available devices"""
        self.models = {}
        
        for device_type, device in self.available_devices:
            try:
                logger.info(f"Loading model for {device_type}: {device}")
                
                if device_type == 'gpu':
                    # GPU model with optimizations
                    model = SentenceTransformer(self.embedding_model, device=device)
                    model = model.to(device)
                    
                    # Warm up GPU
                    dummy_input = ["GPU warmup test"]
                    _ = model.encode(dummy_input, device=device)
                    
                    logger.info("GPU model loaded and warmed up")
                    
                else:
                    # CPU model
                    model = SentenceTransformer(self.embedding_model, device=device)
                    logger.info("CPU model loaded")
                
                self.models[device_type] = model
                
            except Exception as e:
                logger.error(f"Failed to load model for {device_type}: {e}")
                if device_type == 'gpu':
                    logger.info("Falling back to CPU-only mode")
                    self.use_gpu = False
                    self.hybrid_mode = False
                    self.available_devices = [('cpu', self.cpu_device)]
                    self.setup_models()  # Retry with CPU only
                    return
                else:
                    raise e
    
    def load_index_and_metadata(self):
        """Load FAISS index and metadata"""
        logger.info("Loading RAG index and metadata...")
        
        # Check if index exists
        if not os.path.exists(self.index_path):
            logger.error(f"Index not found at {self.index_path}")
            logger.info("Run embed.ps1 first to build the index.")
            sys.exit(1)
        
        if not os.path.exists(self.meta_path):
            logger.error(f"Metadata not found at {self.meta_path}")
            logger.info("Run embed.ps1 first to build the metadata.")
            sys.exit(1)
        
        try:
            # Load FAISS index
            logger.info("Loading FAISS index...")
            self.index = faiss.read_index(self.index_path)
            logger.info(f"Index loaded: {self.index.ntotal} vectors")
            
            # Load metadata
            logger.info("Loading metadata...")
            with open(self.meta_path, 'r', encoding='utf-8') as f:
                self.metadata = [json.loads(line) for line in f if line.strip()]
            logger.info(f"Metadata loaded: {len(self.metadata)} entries")
            
        except Exception as e:
            logger.error(f"Failed to load index/metadata: {e}")
            sys.exit(1)
    
    def encode_query_hybrid(self, query: str) -> np.ndarray:
        """Encode query using optimal available device"""
        logger.info(f"Encoding query: {query}")
        
        # Strategy: Use GPU if available, otherwise CPU
        if 'gpu' in self.models:
            logger.info("Using GPU for query encoding")
            device = self.gpu_device
            model = self.models['gpu']
        else:
            logger.info("Using CPU for query encoding")
            device = self.cpu_device
            model = self.models['cpu']
        
        try:
            query_emb = model.encode(
                [query], 
                normalize_embeddings=True,
                convert_to_numpy=True,
                device=device
            )
            logger.info("Query encoded successfully")
            return query_emb
            
        except Exception as e:
            logger.warning(f"Query encoding failed: {e}")
            # Fallback to CPU if GPU failed
            if 'cpu' in self.models and device != self.cpu_device:
                logger.info("Falling back to CPU encoding")
                return self.models['cpu'].encode(
                    [query], 
                    normalize_embeddings=True,
                    convert_to_numpy=True
                )
            else:
                raise e
    
    def search_index_hybrid(self, query_emb: np.ndarray, topk: int) -> Tuple[np.ndarray, np.ndarray]:
        """Search index using optimal available device"""
        logger.info(f"Searching for top {topk} results...")
        
        # Strategy: Use GPU-accelerated search if available
        if 'gpu' in self.models:
            try:
                logger.info("Attempting GPU-accelerated search")
                from faiss_gpu_compat import faiss_gpu
                
                if faiss_gpu.has_gpu_resources():
                    res = faiss_gpu.create_gpu_resources()
                    if res:
                        gpu_index = faiss_gpu.index_cpu_to_gpu(res, 0, self.index)
                        scores, indices = gpu_index.search(query_emb, topk)
                        logger.info("GPU search completed")
                        return scores, indices
                    else:
                        logger.info("GPU resources not available, using CPU search")
                else:
                    logger.info("GPU FAISS features not available, using CPU search")
                    
            except Exception as e:
                logger.warning(f"GPU search failed: {e}")
                logger.info("Falling back to CPU search")
        
        # CPU search
        logger.info("Using CPU search")
        scores, indices = self.index.search(query_emb, topk)
        logger.info("CPU search completed")
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
            logger.info(f"Retrieved {len(results)} results in {elapsed_time:.3f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
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
        logger.info(f"Saving results to {output_path}")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for result in results:
                    f.write(json.dumps(result) + '\n')
            
            logger.info(f"Results saved: {len(results)} entries")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            return None
    
    def display_results_summary(self, results: List[Dict]):
        """Display a summary of retrieval results"""
        if not results:
            logger.warning("No results to display")
            return
        
        logger.info("\nRetrieval Results Summary:")
        logger.info("=" * 50)
        
        # Top results
        logger.info("Top 5 Results:")
        for i, result in enumerate(results[:5], 1):
            path = result.get('path', 'Unknown')
            score = result.get('score', 0)
            relevance = result.get('relevance', 'Unknown')
            logger.info(f"  {i}. {path}")
            logger.info(f"     Score: {score:.4f} | Relevance: {relevance}")
        
        # Statistics
        if len(results) > 5:
            logger.info(f"\nAdditional Results: {len(results) - 5} more")
        
        # Score distribution
        scores = [r.get('score', 0) for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        
        logger.info(f"\nScore Statistics:")
        logger.info(f"  Average: {avg_score:.4f}")
        logger.info(f"  Maximum: {max_score:.4f}")
        logger.info(f"  Minimum: {min_score:.4f}")
        
        # File type distribution
        file_types = {}
        for result in results:
            path = result.get('path', '')
            if path:
                ext = os.path.splitext(path)[1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1
        
        if file_types:
            logger.info(f"\nFile Type Distribution:")
            for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {ext}: {count} files")


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
    retriever = DualModeRAGRetrieverV4(config)
    
    # Perform retrieval
    results = retriever.retrieve_documents(args.query, args.topk)
    
    if results:
        # Save results
        output_path = args.output or 'rag/context_topk.jsonl'
        saved_path = retriever.save_results(results, output_path)
        
        # Display summary
        retriever.display_results_summary(results)
        
        if saved_path:
            logger.info(f"\nRetrieval completed successfully!")
            logger.info(f"Results saved to: {saved_path}")
            return 0
        else:
            logger.warning("\nRetrieval completed but failed to save results")
            return 1
    else:
        logger.error("\nRetrieval failed - no results returned")
        return 1


if __name__ == '__main__':
    sys.exit(main())
