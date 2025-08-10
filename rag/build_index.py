#!/usr/bin/env python3
"""
Build FAISS index for RAG system.
"""
import os
import json
import faiss
import numpy as np
import argparse
import pathlib
from sentence_transformers import SentenceTransformer
from textwrap import wrap


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


def chunks(text, n, ov):
    """Split text into overlapping chunks."""
    words = text.split()
    step = n - ov
    for i in range(0, len(words), step):
        yield ' '.join(words[i:i+n])


def main():
    """Main function to build FAISS index."""
    parser = argparse.ArgumentParser(description='Build FAISS index for RAG system')
    parser.add_argument('--filelist', required=True, help='File containing list of files to index')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Set defaults if not in config
    embedding_model = config.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    chunk_tokens = int(config.get('CHUNK_TOKENS', 512))
    overlap = int(config.get('CHUNK_OVERLAP', 50))
    faiss_index_path = config.get('FAISS_INDEX_PATH', 'rag/index.faiss')
    rag_meta_path = config.get('RAG_META_PATH', 'rag/meta.jsonl')
    
    print(f"Loading embedding model: {embedding_model}")
    model = SentenceTransformer(embedding_model)
    
    # Read file list
    if not os.path.exists(args.filelist):
        print(f"Error: File list {args.filelist} not found")
        return 1
    
    with open(args.filelist, 'r', encoding='utf-8') as f:
        paths = [line.strip() for line in f if line.strip()]
    
    texts, meta = [], []
    
    print(f"Processing {len(paths)} files...")
    for path in paths:
        try:
            if not os.path.exists(path):
                print(f"Warning: File {path} not found, skipping")
                continue
                
            with open(path, encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            for i, chunk in enumerate(chunks(content, chunk_tokens, overlap)):
                texts.append(chunk)
                meta.append({"path": path, "chunk": i})
                
        except Exception as e:
            print(f"Warning: Error processing {path}: {e}")
            continue
    
    if not texts:
        print("Error: No text chunks generated")
        return 1
    
    print(f"Generating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(
        texts, 
        normalize_embeddings=True, 
        convert_to_numpy=True
    ).astype('float32')
    
    # Create and populate FAISS index
    print("Building FAISS index...")
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    
    # Save index and metadata
    print(f"Saving index to {faiss_index_path}")
    faiss.write_index(index, faiss_index_path)
    
    print(f"Saving metadata to {rag_meta_path}")
    with open(rag_meta_path, 'w', encoding='utf-8') as f:
        for item in meta:
            f.write(json.dumps(item) + '\n')
    
    print(f"✅ Indexed {len(texts)} chunks from {len(paths)} files")
    print(f"Index dimension: {embeddings.shape[1]}")
    return 0


if __name__ == '__main__':
    exit(main())
