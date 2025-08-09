import os, json, faiss, numpy as np, argparse, pathlib
from sentence_transformers import SentenceTransformer
from textwrap import wrap

cfg = {k: v for k, v in (l.strip().split('=',1) for l in open('.env') if '=' in l)}
model = SentenceTransformer(cfg['EMBEDDING_MODEL'])
chunk_tokens = int(cfg['CHUNK_TOKENS'])
overlap = int(cfg['CHUNK_OVERLAP'])

def chunks(text, n, ov):
    words = text.split()
    step = n - ov
    for i in range(0, len(words), step):
        yield ' '.join(words[i:i+n])

ap = argparse.ArgumentParser(); ap.add_argument('--filelist', required=True)
args = ap.parse_args()
paths = [l.strip() for l in open(args.filelist) if l.strip()]

texts, meta = [], []
for p in paths:
    try:
        for i, c in enumerate(chunks(open(p, encoding='utf-8', errors='ignore').read(), chunk_tokens, overlap)):
            texts.append(c); meta.append({"path": p, "chunk": i})
    except Exception: continue

emb = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True).astype('float32')
index = faiss.IndexFlatIP(emb.shape[1]); index.add(emb)

faiss.write_index(index, cfg['FAISS_INDEX_PATH'])
with open(cfg['RAG_META_PATH'], 'w', encoding='utf-8') as f:
    for m in meta: f.write(json.dumps(m) + '\n')

print(f"Indexed {len(texts)} chunks from {len(paths)} files.")
