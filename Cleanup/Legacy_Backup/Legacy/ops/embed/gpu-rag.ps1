#  GPU-RAG System for Agent Exo-Suit V2.1 "Indestructible"
# CUDA-accelerated retrieval augmented generation with intelligent context management

[CmdletBinding()]
param(
    [string]$Root = $PWD.Path,
    [string]$Query = "",
    [int]$TopK = 60,
    [int]$MaxTokens = 128000,
    [string]$Model = "all-MiniLM-L6-v2",
    [switch]$Force,
    [switch]$Benchmark,
    [switch]$Interactive
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ===== GPU-RAG INITIALIZATION =====
Write-Host " GPU-RAG System Initialization..." -ForegroundColor Cyan

# Check for GPU environment
$venvPath = Join-Path $Root "gpu_rag_env"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Host " GPU-RAG environment not found. Creating..." -ForegroundColor Yellow
    & "$Root\ops\gpu-accelerator.ps1" -InstallDeps -Force
}

# Activate environment
& $activateScript

# ===== GPU-OPTIMIZED EMBEDDING PIPELINE =====
Write-Host " Building GPU-optimized embedding pipeline..." -ForegroundColor Cyan

$embedPipeline = @"
import os
import json
import numpy as np
import torch
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path
import re
from typing import List, Dict, Tuple
import time

class GPUEmbeddingPipeline:
    def __init__(self, model_name='$Model', device='auto'):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.index = None
        self.documents = []
        self.setup_model()
    
    def setup_model(self):
        """Initialize sentence transformer with GPU optimization"""
        print(f" Loading model: {self.model_name}")
        
        # Auto-detect device
        if self.device == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        print(f" Using device: {self.device}")
        
        # Load model with optimizations
        self.model = SentenceTransformer(self.model_name, device=self.device)
        
        # Move to GPU if available
        if self.device == 'cuda':
            self.model = self.model.to('cuda')
            print(f" Model moved to GPU: {torch.cuda.get_device_name(0)}")
            print(f" GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks with smart boundaries"""
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
        
        return chunks
    
    def extract_code_blocks(self, content: str) -> str:
        """Extract and clean code blocks from markdown"""
        # Remove markdown code block markers
        content = re.sub(r'```[\w]*\n', '', content)
        content = re.sub(r'```\n', '', content)
        return content
    
    def process_file(self, file_path: Path, chunk_size: int = 512, overlap: int = 50) -> List[Dict]:
        """Process a single file and return chunks"""
        try:
            # Skip binary files
            if file_path.stat().st_size > 1000000:  # 1MB limit
                return []
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return []
            
            # Extract code blocks for markdown files
            if file_path.suffix.lower() == '.md':
                content = self.extract_code_blocks(content)
            
            # Chunk the content
            chunks = self.chunk_text(content, chunk_size, overlap)
            
            file_chunks = []
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    doc = {
                        'file': str(file_path.relative_to(Path('$Root'))),
                        'chunk': i,
                        'content': chunk,
                        'type': file_path.suffix.lower(),
                        'size': len(chunk),
                        'path': str(file_path)
                    }
                    file_chunks.append(doc)
            
            return file_chunks
            
        except Exception as e:
            print(f" Error processing {file_path}: {e}")
            return []
    
    def build_index(self, root_path: str, chunk_size: int = 512, overlap: int = 50):
        """Build FAISS index from files"""
        root = Path(root_path)
        
        # File patterns to process
        patterns = [
            '*.py', '*.js', '*.ts', '*.tsx', '*.md', '*.txt', 
            '*.json', '*.yaml', '*.yml', '*.ps1', '*.sh', '*.rs',
            '*.go', '*.cpp', '*.h', '*.cs', '*.java'
        ]
        
        print(" Scanning files...")
        all_files = []
        for pattern in patterns:
            files = list(root.rglob(pattern))
            all_files.extend(files)
        
        # Filter out unwanted directories
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'rag_env', 'gpu_rag_env', '.sandboxes'}
        all_files = [f for f in all_files if not any(exclude in str(f) for exclude in exclude_dirs)]
        
        print(f" Found {len(all_files)} files to process")
        
        # Process files in batches for memory efficiency
        batch_size = 100
        all_chunks = []
        
        for i in range(0, len(all_files), batch_size):
            batch = all_files[i:i + batch_size]
            print(f" Processing batch {i//batch_size + 1}/{(len(all_files) + batch_size - 1)//batch_size}")
            
            for file_path in batch:
                if file_path.is_file():
                    chunks = self.process_file(file_path, chunk_size, overlap)
                    all_chunks.extend(chunks)
        
        if not all_chunks:
            print(" No documents to embed!")
            return
        
        print(f" Total chunks: {len(all_chunks)}")
        
        # Generate embeddings
        print(" Generating embeddings...")
        texts = [doc['content'] for doc in all_chunks]
        
        start_time = time.time()
        embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=32)
        end_time = time.time()
        
        print(f" Embeddings generated in {(end_time - start_time):.2f} seconds")
        
        # Convert to float32 for FAISS
        embeddings = embeddings.astype(np.float32)
        
        # Build FAISS index
        print(" Building FAISS index...")
        dimension = embeddings.shape[1]
        
        # Use GPU index if available
        if self.device == 'cuda' and faiss.get_num_gpus() > 0:
            print(" Using GPU-accelerated FAISS")
            self.index = faiss.IndexFlatIP(dimension)
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
        else:
            print(" Using CPU FAISS")
            self.index = faiss.IndexFlatIP(dimension)
        
        # Add vectors to index
        self.index.add(embeddings)
        self.documents = all_chunks
        
        print(f" Index built with {len(all_chunks)} documents")
        print(f" Embedding dimension: {dimension}")
        
        return embeddings
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search for similar documents"""
        if self.index is None:
            print(" Index not built. Run build_index() first.")
            return []
        
        # Encode query
        query_embedding = self.model.encode([query])
        query_embedding = query_embedding.astype(np.float32)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc['score'] = float(score)
                doc['rank'] = i + 1
                results.append(doc)
        
        return results
    
    def save_index(self, output_dir: str):
        """Save index and metadata"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        try:
            faiss.write_index(self.index, str(output_path / 'index.faiss'))
        except Exception as e:
            print(f" Standard save failed: {e}")
            # Try alternative save method
            try:
                import pickle
                with open(output_path / 'index.pkl', 'wb') as f:
                    pickle.dump(self.index, f)
                print(f" Index saved as pickle")
            except Exception as e2:
                print(f" Alternative save failed: {e2}")
                return False
        
        # Save metadata
        metadata = {
            'model': self.model_name,
            'device': self.device,
            'documents': self.documents,
            'created': str(np.datetime64('now')),
            'total_chunks': len(self.documents)
        }
        
        with open(output_path / 'index.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f" Index saved to {output_path}")
    
    def load_index(self, index_path: str):
        """Load existing index"""
        index_path = Path(index_path)
        
        if not (index_path / 'index.faiss').exists():
            print(f" Index file not found: {index_path / 'index.faiss'}")
            return False
        
        # Load FAISS index
        self.index = faiss.read_index(str(index_path / 'index.faiss'))
        
        # Load metadata
        with open(index_path / 'index.json', 'r') as f:
            metadata = json.load(f)
        
        self.documents = metadata['documents']
        print(f" Index loaded: {len(self.documents)} documents")
        return True

def main():
    pipeline = GPUEmbeddingPipeline()
    
    # Build or load index
    index_path = Path('$Root') / 'context' / 'vec'
    
    if index_path.exists() and (index_path / 'index.faiss').exists():
        print(" Loading existing index...")
        pipeline.load_index(str(index_path))
    else:
        print(" Building new index...")
        pipeline.build_index('$Root')
        pipeline.save_index(str(index_path))
    
    # Interactive mode
    if '$Interactive' == 'True':
        print("\\n Interactive mode. Type 'quit' to exit.")
        while True:
            query = input("\\n Query: ").strip()
            if query.lower() == 'quit':
                break
            
            if query:
                results = pipeline.search(query, $TopK)
                print(f"\\n Top {len(results)} results:")
                for i, result in enumerate(results[:5]):  # Show top 5
                    print(f"{i+1}. {result['file']} (Score: {result['score']:.3f})")
                    print(f"   {result['content'][:200]}...")
    
    # Benchmark mode
    elif '$Benchmark' == 'True':
        print("\\n Running benchmarks...")
        
        # Test queries
        test_queries = [
            "GPU acceleration",
            "CUDA support",
            "performance optimization",
            "machine learning",
            "code generation"
        ]
        
        for query in test_queries:
            start_time = time.time()
            results = pipeline.search(query, 10)
            end_time = time.time()
            
            print(f"\\n Query: '{query}'")
            print(f"  Search time: {(end_time - start_time)*1000:.2f} ms")
            print(f" Results: {len(results)} documents")
            if results:
                print(f" Top result: {results[0]['file']} (Score: {results[0]['score']:.3f})")
    
    # Single query mode
    elif Query:
        results = pipeline.search(Query, TopK)
        print(f"\\n Top {len(results)} results for: '{Query}'")
        
        # Save results to context
        context_dir = Path('$Root') / 'context' / '_latest'
        context_dir.mkdir(parents=True, exist_ok=True)
        
        # Trim results to fit token budget
        total_tokens = 0
        trimmed_results = []
        
        for result in results:
            # Rough token estimation (1 token  4 characters)
            estimated_tokens = len(result['content']) // 4
            if total_tokens + estimated_tokens <= MaxTokens:
                trimmed_results.append(result)
                total_tokens += estimated_tokens
            else:
                break
        
        # Save trimmed results
        output_data = {
            'query': Query,
            'total_results': len(results),
            'trimmed_results': len(trimmed_results),
            'max_tokens': MaxTokens,
            'used_tokens': total_tokens,
            'results': trimmed_results,
            'timestamp': str(np.datetime64('now'))
        }
        
        with open(context_dir / 'TRIMMED.json', 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f" Trimmed results saved to {context_dir / 'TRIMMED.json'}")
        print(f" Token usage: {total_tokens}/{MaxTokens}")
        
        # Display top results
        for i, result in enumerate(trimmed_results[:10]):
            print(f"\\n{i+1}. {result['file']} (Score: {result['score']:.3f})")
            print(f"   {result['content'][:300]}...")

if __name__ == '__main__':
    main()
"@

# Save and run the GPU-RAG pipeline
$pipelinePath = Join-Path $env:TEMP "gpu_rag_pipeline.py"
$embedPipeline | Out-File $pipelinePath -Encoding utf8

# ===== EXECUTE GPU-RAG PIPELINE =====
Write-Host " Executing GPU-RAG pipeline..." -ForegroundColor Cyan

if ($Query) {
    Write-Host " Query: $Query" -ForegroundColor Green
    Write-Host " Top-K: $TopK" -ForegroundColor Green
    Write-Host " Max Tokens: $MaxTokens" -ForegroundColor Green
}

python $pipelinePath

if ($LASTEXITCODE -eq 0) {
    Write-Host " GPU-RAG pipeline completed successfully!" -ForegroundColor Green
    
    # Check if results were generated
    $trimmedPath = Join-Path $Root "context\_latest\TRIMMED.json"
    if (Test-Path $trimmedPath) {
        $results = Get-Content $trimmedPath -Raw | ConvertFrom-Json
        Write-Host " Generated $($results.trimmed_results) results from $($results.total_results) total" -ForegroundColor Green
        Write-Host " Token usage: $($results.used_tokens)/$($results.max_tokens)" -ForegroundColor Green
    }
} else {
    Write-Error "GPU-RAG pipeline failed"
    exit 1
}

Write-Host "`n GPU-RAG system ready!" -ForegroundColor Green
