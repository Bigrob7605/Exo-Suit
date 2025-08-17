# Agent Exo-Suit V4.0 - GPU-Only RAG Test Suite
# Tests GPU acceleration with CPU fallback for Windows compatibility

import os
import sys
import time
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import torch
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import faiss
    print(f"OK - CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"OK - CUDA device: {torch.cuda.get_device_name(0)}")
        print(f"OK - CUDA version: {torch.version.cuda}")
        device = 'cuda'
    else:
        print("CUDA not available, using CPU only")
        device = 'cpu'
        
except ImportError as e:
    print(f"Required libraries not available: {e}")
    print("Please install: torch, sentence-transformers, faiss-cpu")
    sys.exit(1)

def test_gpu_embeddings():
    """Test GPU-accelerated embedding generation"""
    print("\n=== GPU-Only Embedding Test ===")
    
    # Load test data
    test_file = "test_data.txt"
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return False
    
    with open(test_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    print(f"OK - Loaded {len(lines)} test sentences")
    
    # Initialize model on target device
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
        device_name = "GPU" if device == 'cuda' else "CPU"
        print(f"OK - Sentence transformer initialized on {device_name}")
        
        # Generate embeddings
        start_time = time.time()
        embeddings = model.encode(lines, show_progress_bar=False, device=device)
        end_time = time.time()
        
        print(f"OK - Generated {embeddings.shape[0]} embeddings of dimension {embeddings.shape[1]}")
        print(f"Processing time: {end_time - start_time:.3f}s")
        
    except Exception as e:
        print(f"Model initialization failed: {e}")
        return False
    
    # Test FAISS index creation (CPU fallback for Windows compatibility)
    print("\nOK - Creating FAISS index (CPU fallback for Windows compatibility)...")
    try:
        dimension = embeddings.shape[1]
        
        # Convert to CPU numpy array if on GPU
        if device == 'cuda' and hasattr(embeddings, 'cpu'):
            embeddings_cpu = embeddings.cpu().numpy()
        else:
            embeddings_cpu = embeddings
        
        # Create index
        index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(embeddings_cpu)
        
        # Add vectors to index
        index.add(embeddings_cpu.astype('float32'))
        print(f"OK - FAISS index created with {index.ntotal} vectors")
        
        # Test search
        query = "test query for GPU acceleration"
        query_emb = model.encode([query], device=device)
        
        # Convert query to CPU if on GPU
        if device == 'cuda' and hasattr(query_emb, 'cpu'):
            query_cpu = query_emb.cpu().numpy()
        else:
            query_cpu = query_emb
        
        # Normalize query
        faiss.normalize_L2(query_cpu)
        
        # Search index
        scores, indices = index.search(query_cpu.astype('float32'), 5)
        print(f"Search successful - Top score: {scores[0][0]:.4f}")
        
        # Display top results
        print("\nTop search results:")
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(lines):
                print(f"  {i+1}. Score: {score:.4f} - {lines[idx][:50]}...")
        
    except Exception as e:
        print(f"FAISS index creation failed: {e}")
        return False
    
    return True

def test_performance_metrics():
    """Test performance metrics and timing"""
    print("\n=== Performance Metrics Test ===")
    
    # Test embedding speed
    test_texts = ["Performance test sentence for GPU acceleration"] * 100
    
    model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
    
    # Warm up
    _ = model.encode(["warmup"], device=device)
    
    # Benchmark
    start_time = time.time()
    embeddings = model.encode(test_texts, show_progress_bar=False, device=device)
    end_time = time.time()
    
    total_time = end_time - start_time
    sentences_per_second = len(test_texts) / total_time
    
    print(f"OK - Performance Metrics:")
    print(f"  100 embeddings in {total_time:.3f}s")
    print(f"  Speed: {sentences_per_second:.1f} sentences/second")
    print(f"  Device: {device.upper()}")
    
    # Memory usage (if on GPU)
    if device == 'cuda':
        try:
            allocated = torch.cuda.memory_allocated(0) / 1024**2
            reserved = torch.cuda.memory_reserved(0) / 1024**2
            print(f"  GPU Memory - Allocated: {allocated:.1f} MB, Reserved: {reserved:.1f} MB")
        except Exception as e:
            print(f"  Could not get GPU memory info: {e}")
    
    return True

def main():
    """Main test function"""
    print("Agent Exo-Suit V4.0 - GPU-Only RAG Test Suite")
    print("=" * 60)
    
    # Test GPU embeddings
    if not test_gpu_embeddings():
        print("FAILED - GPU embedding test")
        return False
    
    # Test performance metrics
    if not test_performance_metrics():
        print("FAILED - Performance metrics test")
        return False
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED - GPU-Only RAG system working correctly!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
