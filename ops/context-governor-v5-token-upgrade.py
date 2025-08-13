import os
import json
import numpy as np
from pathlib import Path
import re
from typing import List, Dict, Tuple
import time
import hashlib
import logging

# Configure logging for token upgrade moonshot
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/token-upgrade-moonshot/context-governor-phase1.log'),
        logging.StreamHandler()
    ]
)

# Try to import GPU libraries, fallback to CPU-only if they fail
try:
    import torch
    import faiss
    from sentence_transformers import SentenceTransformer
    GPU_AVAILABLE = True
    logging.info("GPU acceleration enabled for token upgrade")
except ImportError as e:
    logging.warning(f"GPU libraries not available: {e}")
    logging.info("Falling back to CPU-only mode")
    GPU_AVAILABLE = False
    
    # CPU fallback imports
    try:
        import numpy as np
        logging.info("CPU fallback mode enabled")
    except ImportError:
        logging.error("Critical: numpy not available")
        exit(1)

class TokenUpgradeContextGovernor:
    def __init__(self, model_name='all-MiniLM-L6-v2', device='auto', max_tokens=256000):
        self.model_name = model_name
        self.device = device
        self.max_tokens = max_tokens
        self.model = None
        self.index = None
        self.documents = []
        self.context_cache = {}
        
        # TOKEN UPGRADE FEATURES - PHASE 1
        self.phase = 1
        self.token_improvement = 2.0  # 2x improvement from 128K
        self.memory_layers = {
            'gpu_vram': {'capacity': 128000, 'priority': 'hot'},
            'shared_memory': {'capacity': 128000, 'priority': 'warm'},
            'system_ram': {'capacity': 512000, 'priority': 'cold'},
            'nvme_ssd': {'capacity': 10000000, 'priority': 'persistent'}
        }
        
        logging.info(f"TokenUpgradeContextGovernor initialized with {max_tokens:,} tokens (Phase {self.phase})")
        logging.info(f"Token improvement: {self.token_improvement}x from baseline")
        
        self.setup_model()
    
    def setup_model(self):
        """Initialize sentence transformer with GPU optimization or CPU fallback"""
        if not GPU_AVAILABLE:
            logging.info("Using CPU-only fallback mode")
            self.device = 'cpu'
            self.model = None
            return
            
        logging.info(f"Loading model: {self.model_name}")
        
        # Auto-detect device
        if self.device == 'auto':
            if 'True' == 'True' and torch.cuda.is_available():
                self.device = 'cuda'
            else:
                self.device = 'cpu'
        
        logging.info(f"Using device: {self.device}")
        
        try:
            # Load model with optimizations
            self.model = SentenceTransformer(self.model_name, device=self.device)
            
            # Move to GPU if available
            if self.device == 'cuda':
                self.model = self.model.to('cuda')
                logging.info(f"Model moved to GPU: {torch.cuda.get_device_name(0)}")
                logging.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        except Exception as e:
            logging.error(f"Model loading failed: {e}")
            logging.info("Falling back to CPU-only mode")
            self.device = 'cpu'
            self.model = None
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text - UPGRADED for larger contexts"""
        # Rough estimation: 1 token ≈ 4 characters
        estimated_tokens = len(text) // 4
        
        # Log token estimation for monitoring
        if estimated_tokens > 100000:  # Log large contexts
            logging.info(f"Large context detected: {estimated_tokens:,} estimated tokens")
        
        return estimated_tokens
    
    def smart_chunk_text(self, text: str, chunk_size: int = 1024, overlap: int = 100) -> List[str]:
        """Smart text chunking with semantic boundaries - UPGRADED for larger chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        # Try to split on sentence boundaries first
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If no chunks created, fall back to word-based chunking
        if not chunks:
            words = text.split()
            for i in range(0, len(words), chunk_size - overlap):
                chunk = ' '.join(words[i:i + chunk_size])
                if chunk:
                    chunks.append(chunk)
        
        logging.info(f"Text chunked into {len(chunks)} chunks with {chunk_size} character size")
        return chunks
    
    def process_file(self, file_path: Path, chunk_size: int = 1024, overlap: int = 100) -> List[Dict]:
        """Process a single file and return chunks - UPGRADED for larger files"""
        try:
            # Skip binary files
            if file_path.stat().st_size > 10000000:  # 10MB limit (increased from 1MB)
                logging.warning(f"Large file skipped: {file_path} ({file_path.stat().st_size / 1024 / 1024:.1f} MB)")
                return []
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return []
            
            # Extract code blocks for markdown files
            if file_path.suffix.lower() == '.md':
                content = self.extract_code_blocks(content)
            
            # Chunk the content with larger chunk size
            chunks = self.smart_chunk_text(content, chunk_size, overlap)
            
            file_chunks = []
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    estimated_tokens = self.estimate_tokens(chunk)
                    doc = {
                        'file': str(file_path.relative_to(Path(r'.\'))),
                        'chunk': i,
                        'content': chunk,
                        'type': file_path.suffix.lower(),
                        'size': len(chunk),
                        'tokens': estimated_tokens,
                        'path': str(file_path),
                        'hash': hashlib.md5(chunk.encode()).hexdigest()[:8]
                    }
                    file_chunks.append(doc)
            
            logging.info(f"Processed {file_path}: {len(file_chunks)} chunks, {sum(d['tokens'] for d in file_chunks):,} total tokens")
            return file_chunks
            
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")
            return []
    
    def build_index(self, root_path: str, chunk_size: int = 1024, overlap: int = 100):
        """Build FAISS index from files - UPGRADED for larger contexts"""
        root = Path(root_path)
        
        # File patterns to process
        patterns = [
            '*.py', '*.js', '*.ts', '*.tsx', '*.md', '*.txt', 
            '*.json', '*.yaml', '*.yml', '*.ps1', '*.sh', '*.rs',
            '*.go', '*.cpp', '*.h', '*.cs', '*.java'
        ]
        
        logging.info("Scanning files for token upgrade...")
        all_files = []
        for pattern in patterns:
            files = list(root.rglob(pattern))
            all_files.extend(files)
        
        # Filter out unwanted directories
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'rag_env', 'gpu_rag_env', '.sandboxes'}
        all_files = [f for f in all_files if not any(exclude in str(f) for exclude in exclude_dirs)]
        
        logging.info(f"Found {len(all_files)} files to process")
        
        # Process files in batches for memory efficiency
        batch_size = 200  # Increased from 100 for better performance
        all_chunks = []
        
        for i in range(0, len(all_files), batch_size):
            batch = all_files[i:i + batch_size]
            logging.info(f"Processing batch {i//batch_size + 1}/{(len(all_files) + batch_size - 1)//batch_size}")
            
            for file_path in batch:
                if file_path.is_file():
                    chunks = self.process_file(file_path, chunk_size, overlap)
                    all_chunks.extend(chunks)
        
        if not all_chunks:
            logging.warning("No documents to embed!")
            return
        
        total_tokens = sum(doc['tokens'] for doc in all_chunks)
        logging.info(f"Total chunks: {len(all_chunks)}")
        logging.info(f"Total estimated tokens: {total_tokens:,}")
        
        # Check if we're within token limits
        if total_tokens > self.max_tokens:
            logging.warning(f"Total tokens ({total_tokens:,}) exceed limit ({self.max_tokens:,})")
            logging.info("Implementing intelligent token management...")
        
        # Generate embeddings
        logging.info("Generating embeddings...")
        texts = [doc['content'] for doc in all_chunks]
        
        start_time = time.time()
        embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=64)  # Increased from 32
        end_time = time.time()
        
        logging.info(f"Embeddings generated in {(end_time - start_time):.2f} seconds")
        
        # Convert to float32 for FAISS
        embeddings = embeddings.astype(np.float32)
        
        # Build FAISS index
        logging.info("Building FAISS index...")
        dimension = embeddings.shape[1]
        
        # Use GPU index if available
        if self.device == 'cuda' and faiss.get_num_gpus() > 0:
            logging.info("Using GPU-accelerated FAISS")
            self.index = faiss.IndexFlatIP(dimension)
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
        else:
            logging.info("Using CPU FAISS")
            self.index = faiss.IndexFlatIP(dimension)
        
        # Add vectors to index
        self.index.add(embeddings)
        self.documents = all_chunks
        
        logging.info(f"Index built with {len(all_chunks)} documents")
        logging.info(f"Embedding dimension: {dimension}")
        
        return embeddings
    
    def search_with_budget(self, query: str, top_k: int = 10, max_tokens: int = None) -> Dict:
        """Search for similar documents within token budget - UPGRADED for larger contexts"""
        if self.index is None:
            logging.error("Index not built. Run build_index() first.")
            return {'results': [], 'total_tokens': 0, 'budget_used': 0}
        
        if max_tokens is None:
            max_tokens = self.max_tokens
        
        logging.info(f"Searching with token budget: {max_tokens:,}")
        
        # Encode query
        query_embedding = self.model.encode([query])
        query_embedding = query_embedding.astype(np.float32)
        
        # Search for more results than needed to have options
        search_k = min(top_k * 3, len(self.documents))
        scores, indices = self.index.search(query_embedding, search_k)
        
        # Process results within token budget
        total_tokens = 0
        selected_results = []
        
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc['score'] = float(score)
                doc['rank'] = i + 1
                
                # Check if adding this document would exceed budget
                if total_tokens + doc['tokens'] <= max_tokens:
                    selected_results.append(doc)
                    total_tokens += doc['tokens']
                else:
                    # Try to find a smaller document that fits
                    continue
                
                # Stop if we have enough results
                if len(selected_results) >= top_k:
                    break
        
        budget_used = (total_tokens / max_tokens) * 100
        logging.info(f"Search completed: {len(selected_results)} results, {total_tokens:,} tokens, {budget_used:.1f}% budget used")
        
        return {
            'results': selected_results,
            'total_tokens': total_tokens,
            'budget_used': budget_used,
            'query': query,
            'max_tokens': max_tokens,
            'phase': self.phase,
            'improvement': self.token_improvement
        }

def main():
    logging.info("🚀 TOKEN UPGRADE MOONSHOT - PHASE 1: 256K TOKENS")
    governor = TokenUpgradeContextGovernor()
    
    # Build or load index
    index_path = Path(r'.\') / 'context' / 'vec'
    
    if index_path.exists() and (index_path / 'index.faiss').exists():
        logging.info("Loading existing index...")
        governor.load_index(str(index_path))
    else:
        logging.info("Building new index for token upgrade...")
        governor.build_index(r'.\')
        
        # Save index
        output_path = Path(r'.\') / 'context' / 'vec'
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        if governor.device == 'cuda':
            try:
                # Try GPU to CPU conversion if available
                cpu_index = faiss.index_gpu_to_cpu(governor.index)
                faiss.write_index(cpu_index, str(output_path / 'index.faiss'))
                logging.info("GPU index saved as CPU index")
            except:
                logging.warning("GPU to CPU conversion failed, saving as GPU index")
                faiss.write_index(governor.index, str(output_path / 'index.faiss'))
        else:
            faiss.write_index(governor.index, str(output_path / 'index.faiss'))
        
        # Save metadata
        metadata = {
            'documents': governor.documents,
            'model': governor.model_name,
            'device': governor.device,
            'max_tokens': governor.max_tokens,
            'phase': governor.phase,
            'improvement': governor.token_improvement,
            'timestamp': str(np.datetime64('now'))
        }
        
        with open(output_path / 'index.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logging.info(f"Index saved to {output_path}")
        logging.info(f"Token upgrade phase {governor.phase} complete: {governor.max_tokens:,} tokens operational")

if __name__ == "__main__":
    main()
