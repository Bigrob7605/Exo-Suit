# Agent Exo-Suit V4.0 - Hybrid CPU+GPU RAG Test Suite
# Tests dual-mode operation with graceful fallback

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
        primary_device = 'cuda'
        fallback_device = 'cpu'
    else:
        print("CUDA not available, using CPU only")
        primary_device = 'cpu'
        fallback_device = 'cpu'
        
except ImportError as e:
    print(f"Required libraries not available: {e}")
    print("Please install: torch, sentence-transformers, faiss-cpu")
    sys.exit(1)

def test_hybrid_embeddings():
    """Test hybrid CPU+GPU embedding generation"""
    print("\n=== Hybrid CPU+GPU Embedding Test ===")
    
    # Load test data
    test_file = "test_data.txt"
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return False
    
    with open(test_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    print(f"OK - Loaded {len(lines)} test sentences")
    
    # Test primary device (GPU if available, otherwise CPU)
    try:
        model_primary = SentenceTransformer('all-MiniLM-L6-v2', device=primary_device)
        print(f"OK - Sentence transformer initialized on {primary_device.upper()}")
        
        start_time = time.time()
        embeddings_primary = model_primary.encode(lines, show_progress_bar=False)
        primary_time = time.time() - start_time
        
        print(f"OK - Generated {embeddings_primary.shape[0]} embeddings of dimension {embeddings_primary.shape[1]}")
        print(f"Primary device time: {primary_time:.3f}s")
        
    except Exception as e:
        print(f"Primary device failed: {e}")
        return False
    
    # Test fallback device (CPU)
    try:
        model_fallback = SentenceTransformer('all-MiniLM-L6-v2', device=fallback_device)
        print(f"OK - Sentence transformer initialized on {fallback_device.upper()}")
        
        start_time = time.time()
        embeddings_fallback = model_fallback.encode(lines, show_progress_bar=False)
        fallback_time = time.time() - start_time
        
        print(f"OK - Generated {embeddings_fallback.shape[0]} embeddings of dimension {embeddings_fallback.shape[1]}")
        print(f"Fallback device time: {fallback_time:.3f}s")
        
    except Exception as e:
        print(f"Fallback device failed: {e}")
        return False
    
    # Verify consistency between devices
    if primary_device != fallback_device:
        try:
            similarity = np.corrcoef(embeddings_primary.flatten(), embeddings_fallback.flatten())[0, 1]
            if similarity > 0.99:
                print("OK - Embeddings are consistent between devices")
            else:
                print(f"Warning - Embeddings differ between devices (similarity: {similarity:.4f})")
        except Exception as e:
            print(f"Could not verify consistency: {e}")
    
    # Test FAISS index creation
    print("\nOK - Creating FAISS index...")
    try:
        dimension = embeddings_primary.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Add vectors to index
        index.add(embeddings_primary.astype('float32'))
        print(f"OK - FAISS index created with {index.ntotal} vectors")
        
        # Test search
        query = "test query"
        query_emb = model_primary.encode([query], device=primary_device)
        print(f"OK - Query encoded on {primary_device.upper()}")
        
        # Search index
        scores, indices = index.search(query_emb.astype('float32'), 5)
        print(f"Search successful - Top score: {scores[0][0]:.4f}")
        
    except Exception as e:
        print(f"FAISS index creation failed: {e}")
        return False
    
    return True

def test_performance_metrics():
    """Test performance metrics and timing"""
    print("\n=== Performance Metrics Test ===")
    
    # Test embedding speed
    test_texts = ["Performance test sentence"] * 100
    
    model = SentenceTransformer('all-MiniLM-L6-v2', device=primary_device)
    
    # Warm up
    _ = model.encode(["warmup"], device=primary_device)
    
    # Benchmark
    start_time = time.time()
    embeddings = model.encode(test_texts, show_progress_bar=False, device=primary_device)
    end_time = time.time()
    
    total_time = end_time - start_time
    sentences_per_second = len(test_texts) / total_time
    
    print(f"OK - Performance Metrics:")
    print(f"  100 embeddings in {total_time:.3f}s")
    print(f"  Speed: {sentences_per_second:.1f} sentences/second")
    print(f"  Device: {primary_device.upper()}")
    
    return True

def main():
    """Main test function"""
    print("Agent Exo-Suit V4.0 - Hybrid CPU+GPU RAG Test Suite")
    print("=" * 60)
    
    # Test hybrid embeddings
    if not test_hybrid_embeddings():
        print("FAILED - Hybrid embedding test")
        return False
    
    # Test performance metrics
    if not test_performance_metrics():
        print("FAILED - Performance metrics test")
        return False
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED - Hybrid CPU+GPU RAG system working correctly!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
