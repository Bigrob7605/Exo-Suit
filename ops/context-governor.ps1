# 🧠 GPU-Optimized Context Governor for Agent Exo-Suit V2.1 "Indestructible"
# Intelligent context management with GPU acceleration and token budget control

[CmdletBinding()]
param(
    [string]$Root = $PWD.Path,
    [string]$Query = "",
    [int]$MaxTokens = 128000,
    [int]$TopK = 60,
    [string]$Model = "all-MiniLM-L6-v2",
    [switch]$Force,
    [switch]$Benchmark,
    [switch]$Interactive,
    [switch]$UseGPU = $true
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ===== CONTEXT GOVERNOR INITIALIZATION =====
Write-Host "🧠 GPU-Optimized Context Governor Initialization..." -ForegroundColor Cyan

# Check for GPU environment
$venvPath = Join-Path $Root "gpu_rag_env"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Host "⚠️ GPU-RAG environment not found. Creating..." -ForegroundColor Yellow
    & "$Root\ops\gpu-accelerator.ps1" -InstallDeps -Force
}

# Activate environment
& $activateScript

# ===== GPU-OPTIMIZED CONTEXT MANAGEMENT =====
Write-Host "📊 Building GPU-optimized context management system..." -ForegroundColor Cyan

$contextGovernor = @"
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
import hashlib

class GPUContextGovernor:
    def __init__(self, model_name='$Model', device='auto', max_tokens=$MaxTokens):
        self.model_name = model_name
        self.device = device
        self.max_tokens = max_tokens
        self.model = None
        self.index = None
        self.documents = []
        self.context_cache = {}
        self.setup_model()
    
    def setup_model(self):
        """Initialize sentence transformer with GPU optimization"""
        print(f"🚀 Loading model: {self.model_name}")
        
        # Auto-detect device
        if self.device == 'auto':
            if '$UseGPU' == 'True' and torch.cuda.is_available():
                self.device = 'cuda'
            else:
                self.device = 'cpu'
        
        print(f"📱 Using device: {self.device}")
        
        # Load model with optimizations
        self.model = SentenceTransformer(self.model_name, device=self.device)
        
        # Move to GPU if available
        if self.device == 'cuda':
            self.model = self.model.to('cuda')
            print(f"✅ Model moved to GPU: {torch.cuda.get_device_name(0)}")
            print(f"🎮 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def smart_chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Smart text chunking with semantic boundaries"""
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
            chunks = self.smart_chunk_text(content, chunk_size, overlap)
            
            file_chunks = []
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    doc = {
                        'file': str(file_path.relative_to(Path('$Root'))),
                        'chunk': i,
                        'content': chunk,
                        'type': file_path.suffix.lower(),
                        'size': len(chunk),
                        'tokens': self.estimate_tokens(chunk),
                        'path': str(file_path),
                        'hash': hashlib.md5(chunk.encode()).hexdigest()[:8]
                    }
                    file_chunks.append(doc)
            
            return file_chunks
            
        except Exception as e:
            print(f"⚠️ Error processing {file_path}: {e}")
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
        
        print("🔍 Scanning files...")
        all_files = []
        for pattern in patterns:
            files = list(root.rglob(pattern))
            all_files.extend(files)
        
        # Filter out unwanted directories
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'rag_env', 'gpu_rag_env', '.sandboxes'}
        all_files = [f for f in all_files if not any(exclude in str(f) for exclude in exclude_dirs)]
        
        print(f"📁 Found {len(all_files)} files to process")
        
        # Process files in batches for memory efficiency
        batch_size = 100
        all_chunks = []
        
        for i in range(0, len(all_files), batch_size):
            batch = all_files[i:i + batch_size]
            print(f"📦 Processing batch {i//batch_size + 1}/{(len(all_files) + batch_size - 1)//batch_size}")
            
            for file_path in batch:
                if file_path.is_file():
                    chunks = self.process_file(file_path, chunk_size, overlap)
                    all_chunks.extend(chunks)
        
        if not all_chunks:
            print("❌ No documents to embed!")
            return
        
        print(f"📊 Total chunks: {len(all_chunks)}")
        total_tokens = sum(doc['tokens'] for doc in all_chunks)
        print(f"💾 Total estimated tokens: {total_tokens:,}")
        
        # Generate embeddings
        print("🧠 Generating embeddings...")
        texts = [doc['content'] for doc in all_chunks]
        
        start_time = time.time()
        embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=32)
        end_time = time.time()
        
        print(f"⚡ Embeddings generated in {(end_time - start_time):.2f} seconds")
        
        # Convert to float32 for FAISS
        embeddings = embeddings.astype(np.float32)
        
        # Build FAISS index
        print("🔧 Building FAISS index...")
        dimension = embeddings.shape[1]
        
        # Use GPU index if available
        if self.device == 'cuda' and faiss.get_num_gpus() > 0:
            print("🎮 Using GPU-accelerated FAISS")
            self.index = faiss.IndexFlatIP(dimension)
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
        else:
            print("💻 Using CPU FAISS")
            self.index = faiss.IndexFlatIP(dimension)
        
        # Add vectors to index
        self.index.add(embeddings)
        self.documents = all_chunks
        
        print(f"✅ Index built with {len(all_chunks)} documents")
        print(f"📏 Embedding dimension: {dimension}")
        
        return embeddings
    
    def search_with_budget(self, query: str, top_k: int = 10, max_tokens: int = None) -> Dict:
        """Search for similar documents within token budget"""
        if self.index is None:
            print("❌ Index not built. Run build_index() first.")
            return {'results': [], 'total_tokens': 0, 'budget_used': 0}
        
        if max_tokens is None:
            max_tokens = self.max_tokens
        
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
        
        return {
            'results': selected_results,
            'total_tokens': total_tokens,
            'budget_used': (total_tokens / max_tokens) * 100,
            'query': query,
            'max_tokens': max_tokens
        }
    
    def intelligent_context_assembly(self, query: str, max_tokens: int = None) -> Dict:
        """Intelligently assemble context based on query relevance and token budget"""
        if max_tokens is None:
            max_tokens = self.max_tokens
        
        print(f"🧠 Intelligent context assembly for: '{query}'")
        print(f"💾 Token budget: {max_tokens:,}")
        
        # First pass: get high-relevance results
        high_relevance = self.search_with_budget(query, top_k=20, max_tokens=max_tokens)
        
        if not high_relevance['results']:
            return high_relevance
        
        # Second pass: diversify results by file type and content
        diversified_results = self.diversify_results(high_relevance['results'], max_tokens)
        
        # Final pass: optimize for token efficiency
        optimized_results = self.optimize_token_efficiency(diversified_results, max_tokens)
        
        return optimized_results
    
    def diversify_results(self, results: List[Dict], max_tokens: int) -> List[Dict]:
        """Diversify results by file type and content"""
        if not results:
            return results
        
        # Group by file type
        by_type = {}
        for result in results:
            file_type = result['type']
            if file_type not in by_type:
                by_type[file_type] = []
            by_type[file_type].append(result)
        
        # Select diverse results
        diversified = []
        total_tokens = 0
        
        # Prioritize different file types
        priority_types = ['.py', '.md', '.js', '.ts', '.json', '.yaml', '.ps1', '.sh']
        
        for file_type in priority_types:
            if file_type in by_type and total_tokens < max_tokens:
                # Take top results from this file type
                type_results = sorted(by_type[file_type], key=lambda x: x['score'], reverse=True)
                for result in type_results:
                    if total_tokens + result['tokens'] <= max_tokens:
                        diversified.append(result)
                        total_tokens += result['tokens']
                    else:
                        break
        
        return diversified
    
    def optimize_token_efficiency(self, results: List[Dict], max_tokens: int) -> List[Dict]:
        """Optimize results for maximum information density within token budget"""
        if not results:
            return results
        
        # Sort by score per token (information density)
        for result in results:
            result['efficiency'] = result['score'] / max(result['tokens'], 1)
        
        # Sort by efficiency
        results.sort(key=lambda x: x['efficiency'], reverse=True)
        
        # Select most efficient results within budget
        optimized = []
        total_tokens = 0
        
        for result in results:
            if total_tokens + result['tokens'] <= max_tokens:
                optimized.append(result)
                total_tokens += result['tokens']
            else:
                break
        
        return optimized
    
    def save_context(self, context_data: Dict, output_dir: str):
        """Save context data to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save TRIMMED.json for Cursor consumption
        trimmed_data = {
            'query': context_data['query'],
            'total_results': len(context_data['results']),
            'max_tokens': context_data['max_tokens'],
            'used_tokens': context_data['total_tokens'],
            'budget_used_percent': context_data['budget_used'],
            'results': context_data['results'],
            'timestamp': str(np.datetime64('now')),
            'model': self.model_name,
            'device': self.device
        }
        
        with open(output_path / 'TRIMMED.json', 'w') as f:
            json.dump(trimmed_data, f, indent=2)
        
        # Save detailed context
        with open(output_path / 'CONTEXT_DETAILED.json', 'w') as f:
            json.dump(context_data, f, indent=2)
        
        print(f"💾 Context saved to {output_path}")
        print(f"📊 Budget usage: {context_data['budget_used']:.1f}%")
    
    def load_index(self, index_path: str):
        """Load existing index"""
        index_path = Path(index_path)
        
        if not (index_path / 'index.faiss').exists():
            print(f"❌ Index file not found: {index_path / 'index.faiss'}")
            return False
        
        # Load FAISS index
        self.index = faiss.read_index(str(index_path / 'index.faiss'))
        
        # Load metadata
        with open(index_path / 'index.json', 'r') as f:
            metadata = json.load(f)
        
        self.documents = metadata['documents']
        print(f"✅ Index loaded: {len(self.documents)} documents")
        return True

def main():
    governor = GPUContextGovernor()
    
    # Build or load index
    index_path = Path('$Root') / 'context' / 'vec'
    
    if index_path.exists() and (index_path / 'index.faiss').exists():
        print("📂 Loading existing index...")
        governor.load_index(str(index_path))
    else:
        print("🔨 Building new index...")
        governor.build_index('$Root')
        
        # Save index
        output_path = Path('$Root') / 'context' / 'vec'
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        if governor.device == 'cuda':
            cpu_index = faiss.index_gpu_to_cpu(governor.index)
            faiss.write_index(cpu_index, str(output_path / 'index.faiss'))
        else:
            faiss.write_index(governor.index, str(output_path / 'index.faiss'))
        
        # Save metadata
        metadata = {
            'model': governor.model_name,
            'device': governor.device,
            'documents': governor.documents,
            'created': str(np.datetime64('now')),
            'total_chunks': len(governor.documents)
        }
        
        with open(output_path / 'index.json', 'w') as f:
            json.dump(metadata, f, indent=2)
    
    # Interactive mode
    if '$Interactive' == 'True':
        print("\\n💬 Interactive mode. Type 'quit' to exit.")
        while True:
            query = input("\\n🔍 Query: ").strip()
            if query.lower() == 'quit':
                break
            
            if query:
                context = governor.intelligent_context_assembly(query, $MaxTokens)
                print(f"\\n📋 Context assembled: {len(context['results'])} results")
                print(f"💾 Token usage: {context['total_tokens']:,}/{context['max_tokens']:,} ({context['budget_used']:.1f}%)")
                
                # Save context
                context_dir = Path('$Root') / 'context' / '_latest'
                governor.save_context(context, str(context_dir))
    
    # Benchmark mode
    elif '$Benchmark' == 'True':
        print("\\n📊 Running context governor benchmarks...")
        
        # Test queries
        test_queries = [
            "GPU acceleration and CUDA support",
            "performance optimization techniques",
            "machine learning and AI models",
            "code generation and analysis",
            "system architecture and design"
        ]
        
        for query in test_queries:
            print(f"\\n🔍 Testing: '{query}'")
            start_time = time.time()
            context = governor.intelligent_context_assembly(query, $MaxTokens)
            end_time = time.time()
            
            print(f"⏱️  Assembly time: {(end_time - start_time)*1000:.2f} ms")
            print(f"📊 Results: {len(context['results'])} documents")
            print(f"💾 Token usage: {context['total_tokens']:,}/{context['max_tokens']:,} ({context['budget_used']:.1f}%)")
    
    # Single query mode
    elif '$Query':
        print(f"🔍 Processing query: '$Query'")
        context = governor.intelligent_context_assembly('$Query', $MaxTokens)
        
        # Save context
        context_dir = Path('$Root') / 'context' / '_latest'
        governor.save_context(context, str(context_dir))
        
        print(f"\\n📋 Context assembled successfully!")
        print(f"📊 Results: {len(context['results'])} documents")
        print(f"💾 Token usage: {context['total_tokens']:,}/{context['max_tokens']:,} ({context['budget_used']:.1f}%)")
        
        # Display top results
        for i, result in enumerate(context['results'][:5]):
            print(f"\\n{i+1}. {result['file']} (Score: {result['score']:.3f}, Tokens: {result['tokens']})")
            print(f"   {result['content'][:200]}...")

if __name__ == '__main__':
    main()
"@

# Save and run the context governor
$governorPath = Join-Path $env:TEMP "context_governor.py"
$contextGovernor | Out-File $governorPath -Encoding utf8

# ===== EXECUTE CONTEXT GOVERNOR =====
Write-Host "🚀 Executing GPU-Optimized Context Governor..." -ForegroundColor Cyan

if ($Query) {
    Write-Host "🔍 Query: $Query" -ForegroundColor Green
    Write-Host "📊 Top-K: $TopK" -ForegroundColor Green
    Write-Host "💾 Max Tokens: $MaxTokens" -ForegroundColor Green
    Write-Host "🎮 GPU Mode: $UseGPU" -ForegroundColor Green
}

python $governorPath

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Context Governor completed successfully!" -ForegroundColor Green
    
    # Check if context was generated
    $trimmedPath = Join-Path $Root "context\_latest\TRIMMED.json"
    if (Test-Path $trimmedPath) {
        $context = Get-Content $trimmedPath -Raw | ConvertFrom-Json
        Write-Host "📊 Generated $($context.total_results) results" -ForegroundColor Green
        Write-Host "💾 Token usage: $($context.used_tokens)/$($context.max_tokens) ($($context.budget_used_percent)%)" -ForegroundColor Green
    }
} else {
    Write-Error "Context Governor failed"
    exit 1
}

Write-Host "`n🧠 GPU-Optimized Context Governor ready!" -ForegroundColor Green
