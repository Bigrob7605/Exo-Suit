#!/usr/bin/env python3
"""
Retrieve relevant documents using FAISS index.
"""
import os
import json
import faiss
import numpy as np
import argparse
from sentence_transformers import SentenceTransformer


def load_config():
    """Load configuration from .env file."""
    config = {}
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    return config


def main():
    """Main function to retrieve documents."""
    parser = argparse.ArgumentParser(description='Retrieve documents using FAISS index')
    parser.add_argument('--query', required=True, help='Search query')
    parser.add_argument('--topk', type=int, default=60, help='Number of top results to return')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Set defaults if not in config
    embedding_model = config.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    index_path = config.get('FAISS_INDEX_PATH', 'rag/index.faiss')
    meta_path = config.get('RAG_META_PATH', 'rag/meta.jsonl')
    
    # Check if index exists
    if not os.path.exists(index_path):
        print(f"Error: Index not found at {index_path}")
        print("Run embed.ps1 first to build the index.")
        return 1
    
    if not os.path.exists(meta_path):
        print(f"Error: Metadata not found at {meta_path}")
        print("Run embed.ps1 first to build the metadata.")
        return 1
    
    try:
        # Load embedding model
        print(f"Loading embedding model: {embedding_model}")
        model = SentenceTransformer(embedding_model)
        
        # Load FAISS index
        print("Loading FAISS index...")
        index = faiss.read_index(index_path)
        
        # Load metadata
        print("Loading metadata...")
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = [json.loads(line) for line in f if line.strip()]
        
        # Encode query
        print(f"Encoding query: {args.query}")
        query_emb = model.encode([args.query], normalize_embeddings=True)
        
        # Search index
        print(f"Searching for top {args.topk} results...")
        scores, indices = index.search(query_emb, args.topk)
        
        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(meta):
                result = meta[idx].copy()
                result['score'] = float(score)
                results.append(result)
        
        # Save results to context file
        output_path = 'rag/context_topk.jsonl'
        print(f"Saving results to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result) + '\n')
        
        print(f"✅ Retrieved {len(results)} results")
        print(f"Top result: {results[0]['path']} (score: {results[0]['score']:.4f})")
        
        return 0
        
    except Exception as e:
        print(f"Error during retrieval: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
