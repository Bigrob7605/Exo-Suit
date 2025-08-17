#!/usr/bin/env python3
"""
Agent Exo-Suit V3.0 - Embedding Engine
Robust embedding generation with CPU/GPU support and fallback strategies
"""

import os
import sys
import time
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import ML libraries with fallback handling
try:
    import torch
    TORCH_AVAILABLE = True
    logger.info("PyTorch available")
except ImportError as e:
    logger.warning(f"PyTorch not available: {e}")
    TORCH_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    logger.info("Sentence Transformers available")
except ImportError as e:
    logger.warning(f"Sentence Transformers not available: {e}")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
    logger.info("FAISS available")
except ImportError as e:
    logger.warning(f"FAISS not available: {e}")
    FAISS_AVAILABLE = False

class EmbeddingEngine:
    """Advanced embedding engine with CPU/GPU support and fallback strategies"""
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 device_mode: str = "auto",
                 chunk_size: int = 512,
                 batch_size: int = 32,
                 max_retries: int = 3,
                 fallback_strategy: str = "cpu_fallback"):
        
        self.model_name = model_name
        self.device_mode = device_mode
        self.chunk_size = chunk_size
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.fallback_strategy = fallback_strategy
        
        # Device configuration
        self.device = None
        self.device_type = None
        self.model = None
        
        # Performance tracking
        self.embedding_stats = {
            'total_embeddings': 0,
            'total_time': 0.0,
            'avg_time_per_embedding': 0.0,
            'device_used': None,
            'fallbacks_used': 0
        }
        
        # Initialize the engine
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the embedding engine with optimal device configuration"""
        logger.info("Initializing embedding engine...")
        
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise RuntimeError("Sentence Transformers not available. Please install required packages.")
        
        # Determine device configuration
        self._configure_device()
        
        # Load the model
        self._load_model()
        
        logger.info(f"Embedding engine initialized with {self.device_type} device: {self.device}")
    
    def _configure_device(self):
        """Configure optimal device for embedding"""
        if self.device_mode == "auto":
            self.device_mode = self._auto_detect_device()
        
        if self.device_mode == "gpu" and TORCH_AVAILABLE:
            if torch.cuda.is_available():
                self.device = "cuda:0"
                self.device_type = "GPU"
                logger.info("GPU mode enabled")
            else:
                logger.warning("GPU requested but CUDA not available, falling back to CPU")
                self.device_mode = "cpu"
                self.device = "cpu"
                self.device_type = "CPU"
        elif self.device_mode == "cpu":
            self.device = "cpu"
            self.device_type = "CPU"
            logger.info("CPU mode enabled")
        elif self.device_mode == "hybrid" and TORCH_AVAILABLE:
            if torch.cuda.is_available():
                self.device = "cuda:0"
                self.device_type = "HYBRID_GPU"
                logger.info("Hybrid mode enabled (GPU primary)")
            else:
                self.device = "cpu"
                self.device_type = "HYBRID_CPU"
                logger.info("Hybrid mode enabled (CPU primary)")
        else:
            # Fallback to CPU
            self.device = "cpu"
            self.device_type = "CPU"
            logger.info("Fallback to CPU mode")
    
    def _auto_detect_device(self) -> str:
        """Auto-detect optimal device configuration"""
        if not TORCH_AVAILABLE:
            return "cpu"
        
        if torch.cuda.is_available():
            # Check GPU memory and capabilities
            try:
                gpu_props = torch.cuda.get_device_properties(0)
                gpu_memory = gpu_props.total_memory / (1024**3)  # GB
                
                if gpu_memory >= 4.0:  # 4GB+ GPU
                    logger.info(f"Auto-detected GPU: {gpu_props.name} ({gpu_memory:.1f}GB)")
                    return "gpu"
                else:
                    logger.info(f"GPU memory too low ({gpu_memory:.1f}GB), using CPU")
                    return "cpu"
            except Exception as e:
                logger.warning(f"GPU detection failed: {e}, using CPU")
                return "cpu"
        else:
            logger.info("No CUDA GPU available, using CPU")
            return "cpu"
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            
            # Load model with device specification
            self.model = SentenceTransformer(self.model_name, device=self.device)
            
            # Warm up the model
            self._warmup_model()
            
            logger.info(f"Model loaded successfully on {self.device_type}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            
            # Try fallback strategies
            if self.fallback_strategy == "cpu_fallback" and self.device != "cpu":
                logger.info("Attempting CPU fallback...")
                self.device = "cpu"
                self.device_type = "CPU_FALLBACK"
                self.model = SentenceTransformer(self.model_name, device="cpu")
                self._warmup_model()
                logger.info("CPU fallback successful")
            else:
                raise RuntimeError(f"Model loading failed and no fallback available: {e}")
    
    def _warmup_model(self):
        """Warm up the model for optimal performance"""
        try:
            logger.info("Warming up model...")
            
            # Create dummy input
            dummy_texts = ["Model warmup text for optimal performance."] * 3
            
            # Generate embeddings
            with torch.no_grad() if TORCH_AVAILABLE else nullcontext():
                _ = self.model.encode(dummy_texts, show_progress_bar=False)
            
            logger.info("Model warmup completed")
            
        except Exception as e:
            logger.warning(f"Model warmup failed: {e}")
    
    def generate_embeddings(self, texts: List[str], 
                           show_progress: bool = True) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        if not texts:
            return np.array([])
        
        start_time = time.time()
        total_texts = len(texts)
        
        logger.info(f"Generating embeddings for {total_texts} texts using {self.device_type}")
        
        try:
            # Process in batches for memory efficiency
            all_embeddings = []
            
            for i in range(0, total_texts, self.batch_size):
                batch_texts = texts[i:i + self.batch_size]
                batch_start = time.time()
                
                try:
                    # Generate embeddings for batch
                    batch_embeddings = self._encode_batch(batch_texts)
                    all_embeddings.append(batch_embeddings)
                    
                    batch_time = time.time() - batch_start
                    logger.debug(f"Batch {i//self.batch_size + 1}: {len(batch_texts)} texts in {batch_time:.3f}s")
                    
                except Exception as e:
                    logger.error(f"Batch {i//self.batch_size + 1} failed: {e}")
                    
                    # Try fallback for this batch
                    fallback_embeddings = self._fallback_encode_batch(batch_texts)
                    if fallback_embeddings is not None:
                        all_embeddings.append(fallback_embeddings)
                        self.embedding_stats['fallbacks_used'] += 1
                    else:
                        # Create zero embeddings for failed batch
                        logger.warning(f"Creating zero embeddings for failed batch")
                        zero_embeddings = np.zeros((len(batch_texts), 384))  # Default dimension
                        all_embeddings.append(zero_embeddings)
            
            # Combine all embeddings
            if all_embeddings:
                final_embeddings = np.vstack(all_embeddings)
            else:
                final_embeddings = np.array([])
            
            # Update statistics
            total_time = time.time() - start_time
            self.embedding_stats['total_embeddings'] += total_texts
            self.embedding_stats['total_time'] += total_time
            self.embedding_stats['avg_time_per_embedding'] = (
                self.embedding_stats['total_time'] / self.embedding_stats['total_embeddings']
            )
            self.embedding_stats['device_used'] = self.device_type
            
            logger.info(f"Embeddings generated: {final_embeddings.shape} in {total_time:.3f}s")
            logger.info(f"Average time per embedding: {self.embedding_stats['avg_time_per_embedding']:.6f}s")
            
            return final_embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    def _encode_batch(self, texts: List[str]) -> np.ndarray:
        """Encode a batch of texts"""
        try:
            with torch.no_grad() if TORCH_AVAILABLE else nullcontext():
                embeddings = self.model.encode(
                    texts,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
            return embeddings
            
        except Exception as e:
            logger.error(f"Batch encoding failed: {e}")
            raise
    
    def _fallback_encode_batch(self, texts: List[str]) -> Optional[np.ndarray]:
        """Fallback encoding when primary method fails"""
        try:
            if self.device != "cpu" and self.fallback_strategy == "cpu_fallback":
                logger.info("Attempting CPU fallback for batch...")
                
                # Create temporary CPU model
                cpu_model = SentenceTransformer(self.model_name, device="cpu")
                
                # Encode with CPU
                embeddings = cpu_model.encode(
                    texts,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
                
                # Clean up
                del cpu_model
                
                logger.info("CPU fallback successful for batch")
                return embeddings
                
        except Exception as e:
            logger.error(f"CPU fallback failed: {e}")
        
        return None
    
    def create_faiss_index(self, embeddings: np.ndarray, 
                          index_type: str = "auto") -> Any:
        """Create FAISS index from embeddings"""
        if not FAISS_AVAILABLE:
            raise RuntimeError("FAISS not available. Please install required packages.")
        
        if embeddings.size == 0:
            raise ValueError("No embeddings provided")
        
        dimension = embeddings.shape[1]
        logger.info(f"Creating FAISS index for {embeddings.shape[0]} vectors of dimension {dimension}")
        
        try:
            # Determine optimal index type
            if index_type == "auto":
                if embeddings.shape[0] < 1000:
                    index_type = "flat"
                else:
                    index_type = "ivf"
            
            # Create index based on type
            if index_type == "flat":
                index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
                logger.info("Using FlatIP index for small dataset")
            elif index_type == "ivf":
                nlist = min(100, embeddings.shape[0] // 10)  # Number of clusters
                quantizer = faiss.IndexFlatIP(dimension)
                index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_INNER_PRODUCT)
                logger.info(f"Using IVF index with {nlist} clusters")
            else:
                index = faiss.IndexFlatIP(dimension)
                logger.info("Using default FlatIP index")
            
            # Add vectors to index
            if index_type == "ivf":
                # Train the index first
                index.train(embeddings.astype('float32'))
                logger.info("IVF index trained")
            
            # Add vectors
            index.add(embeddings.astype('float32'))
            logger.info(f"Added {index.ntotal} vectors to index")
            
            return index
            
        except Exception as e:
            logger.error(f"FAISS index creation failed: {e}")
            raise
    
    def save_index(self, index: Any, output_path: str) -> str:
        """Save FAISS index to file"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save index
            faiss.write_index(index, output_path)
            
            # Get file size
            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            
            logger.info(f"Index saved to: {output_path} ({file_size:.2f} MB)")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get embedding performance statistics"""
        return self.embedding_stats.copy()
    
    def reset_stats(self):
        """Reset performance statistics"""
        self.embedding_stats = {
            'total_embeddings': 0,
            'total_time': 0.0,
            'avg_time_per_embedding': 0.0,
            'device_used': None,
            'fallbacks_used': 0
        }


class nullcontext:
    """Context manager that does nothing (for when torch is not available)"""
    def __enter__(self):
        return None
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


def main():
    """Test the embedding engine"""
    print("Testing Embedding Engine...")
    
    # Test texts
    test_texts = [
        "This is a test sentence for embedding generation.",
        "Another test sentence to verify the system works.",
        "Testing the embedding engine with multiple sentences.",
        "Verifying CPU and GPU support with fallback strategies.",
        "Final test sentence for comprehensive validation."
    ]
    
    try:
        # Create engine
        engine = EmbeddingEngine(
            model_name="all-MiniLM-L6-v2",
            device_mode="auto",
            batch_size=2
        )
        
        # Generate embeddings
        embeddings = engine.generate_embeddings(test_texts)
        
        print(f"Generated embeddings shape: {embeddings.shape}")
        print(f"Embedding sample: {embeddings[0][:5]}")
        
        # Create FAISS index
        index = engine.create_faiss_index(embeddings)
        print(f"FAISS index created with {index.ntotal} vectors")
        
        # Get performance stats
        stats = engine.get_performance_stats()
        print(f"Performance stats: {stats}")
        
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    main()
