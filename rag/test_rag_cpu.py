# Agent Exo-Suit V4.0 - CPU-Only RAG Test Suite
# Tests CPU-based RAG operations for reliability and compatibility

import os
import sys
import time
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import faiss
    print("OK - CPU libraries available")
except ImportError as e:
    print(f"Required libraries not available: {e}")
    print("Please install: sentence-transformers, faiss-cpu, numpy")
    sys.exit(1)

def test_cpu_embeddings():
    """Test CPU-based embedding generation"""
    print("\n=== CPU-Only Embedding Test ===")
    
    # Load test data
    test_file = "test_data.txt"
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return False
    
    with open(test_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    print(f"OK - Loaded {len(lines)} test sentences")
    
    # Initialize model on CPU
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        print("OK - Sentence transformer initialized on CPU")
        
        # Generate embeddings
        start_time = time.time()
        embeddings = model.encode(lines, show_progress_bar=False, device='cpu')
        end_time = time.time()
        
        print(f"OK - Generated {embeddings.shape[0]} embeddings of dimension {embeddings.shape[1]}")
        print(f"Processing time: {end_time - start_time:.3f}s")
        
    except Exception as e:
        print(f"Model initialization failed: {e}")
        return False
    
    # Test FAISS index creation
    print("\nOK - Creating FAISS index...")
    try:
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add vectors to index
        index.add(embeddings.astype('float32'))
        print(f"OK - FAISS index created with {index.ntotal} vectors")
        
        # Test search
        query = "test query for CPU processing"
        query_emb = model.encode([query], device='cpu')
        
        # Normalize query
        faiss.normalize_L2(query_emb)
        
        # Search index
        scores, indices = index.search(query_emb.astype('float32'), 5)
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
    test_texts = ["Performance test sentence for CPU processing"] * 100
    
    model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
    
    # Warm up
    _ = model.encode(["warmup"], device='cpu')
    
    # Benchmark
    start_time = time.time()
    embeddings = model.encode(test_texts, show_progress_bar=False, device='cpu')
    end_time = time.time()
    
    total_time = end_time - start_time
    sentences_per_second = len(test_texts) / total_time
    
    print(f"OK - Performance Metrics:")
    print(f"  100 embeddings in {total_time:.3f}s")
    print(f"  Speed: {sentences_per_second:.1f} sentences/second")
    print(f"  Device: CPU")
    
    # CPU info
    try:
        import multiprocessing as mp
        cpu_count = mp.cpu_count()
        print(f"  CPU Cores: {cpu_count}")
    except Exception as e:
        print(f"  Could not get CPU info: {e}")
    
    return True

def test_tensor_operations():
    """Test basic tensor operations on CPU"""
    print("\n=== CPU Tensor Operations Test ===")
    
    try:
        # Create test tensors
        a = np.random.randn(100, 100)
        b = np.random.randn(100, 100)
        
        # Matrix multiplication
        start_time = time.time()
        c = np.dot(a, b)
        end_time = time.time()
        
        print(f"OK - Matrix multiplication: 100x100 in {end_time - start_time:.6f}s")
        
        # Element-wise operations
        start_time = time.time()
        d = a * b + c
        end_time = time.time()
        
        print(f"OK - Element-wise operations in {end_time - start_time:.6f}s")
        
        print("OK - CPU tensor operations successful!")
        return True
        
    except Exception as e:
        print(f"CPU tensor operations failed: {e}")
        return False

def main():
    """Main test function"""
    print("Agent Exo-Suit V4.0 - CPU-Only RAG Test Suite")
    print("=" * 60)
    
    # Test CPU embeddings
    if not test_cpu_embeddings():
        print("FAILED - CPU embedding test")
        return False
    
    # Test performance metrics
    if not test_performance_metrics():
        print("FAILED - Performance metrics test")
        return False
    
    # Test tensor operations
    if not test_tensor_operations():
        print("FAILED - Tensor operations test")
        return False
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED - CPU-Only RAG system working correctly!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
