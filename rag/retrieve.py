import os, json, faiss, numpy as np, argparse
from sentence_transformers import SentenceTransformer

def load_config():
    cfg = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    cfg[key] = value
    return cfg

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--query', required=True)
    ap.add_argument('--topk', type=int, default=60)
    args = ap.parse_args()
    
    cfg = load_config()
    model = SentenceTransformer(cfg.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2'))
    index_path = cfg.get('FAISS_INDEX_PATH', 'rag/index.faiss')
    meta_path = cfg.get('RAG_META_PATH', 'rag/meta.jsonl')
    
    if not os.path.exists(index_path):
        print("Index not found. Run embed.ps1 first.")
        return
    
    # Load index and metadata
    index = faiss.read_index(index_path)
    meta = [json.loads(l) for l in open(meta_path)]
    
    # Encode query
    query_emb = model.encode([args.query], normalize_embeddings=True)
    
    # Search
    scores, indices = index.search(query_emb, args.topk)
    
    # Format results
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(meta):
            result = meta[idx].copy()
            result['score'] = float(score)
            results.append(result)
    
    # Save to context file
    with open('rag/context_topk.jsonl', 'w') as f:
        for r in results:
            f.write(json.dumps(r) + '\n')
    
    print(f"Retrieved {len(results)} results")

if __name__ == '__main__':
    main()
