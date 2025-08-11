# GPU-RAG Indexing Script for Agent Exo-Suit V2.0
# Embeds source code, docs, and tests into FAISS index

param(
    [string]$root = $PWD.Path,
    [string]$model = "all-MiniLM-L6-v2",
    [int]$chunkSize = 512,
    [int]$overlap = 50
)

Write-Host " Building GPU-RAG index for Agent Exo-Suit V2.0..."

# Check for RAG environment
$venvPath = Join-Path $root "rag_env"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Error "RAG environment not found. Run setup.ps1 first."
    exit 1
}

# Activate environment
& $activateScript

# Create context directory
$contextDir = Join-Path $root "context"
$vecDir = Join-Path $contextDir "vec"
New-Item -ItemType Directory -Force -Path $vecDir | Out-Null

# Python script for embedding
$embedScript = @"
import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path
import re

def chunk_text(text, chunk_size=$chunkSize, overlap=$overlap):
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    start = 0
    
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start = max(0, end - overlap)
        if start >= len(words):
            break
    
    return chunks

def extract_code_blocks(content):
    """Extract code blocks from markdown and other files"""
    # Remove markdown code blocks but keep content
    content = re.sub(r'```[\w]*\n', '', content)
    content = re.sub(r'```\n', '', content)
    return content

def process_file(file_path, model, index_data):
    """Process a single file and add to index"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Skip binary or very large files
        if len(content) > 1000000:  # 1MB limit
            return
        
        # Extract code blocks
        content = extract_code_blocks(content)
        
        # Skip empty files
        if not content.strip():
            return
        
        # Chunk the content
        chunks = chunk_text(content)
        
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                # Create document entry
                doc = {
                    'file': str(file_path),
                    'chunk': i,
                    'content': chunk,
                    'type': file_path.suffix.lower()
                }
                
                index_data['documents'].append(doc)
                
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    print("Loading sentence transformer model...")
    model = SentenceTransformer('$model')
    
    # File patterns to process
    patterns = [
        '*.py', '*.js', '*.ts', '*.tsx', '*.md', '*.txt', 
        '*.json', '*.yaml', '*.yml', '*.ps1', '*.sh'
    ]
    
    root_path = Path('$root')
    index_data = {'documents': [], 'metadata': {
        'model': '$model',
        'chunk_size': $chunkSize,
        'overlap': $overlap,
        'created': str(np.datetime64('now'))
    }}
    
    print("Scanning files...")
    total_files = 0
    
    for pattern in patterns:
        files = list(root_path.rglob(pattern))
        for file_path in files:
            # Skip certain directories
            if any(skip in str(file_path) for skip in ['.git', 'node_modules', '__pycache__', '.venv', 'rag_env']):
                continue
            
            if file_path.is_file():
                process_file(file_path, model, index_data)
                total_files += 1
                if total_files % 100 == 0:
                    print(f"Processed {total_files} files...")
    
    print(f"Total files processed: {total_files}")
    print(f"Total chunks: {len(index_data['documents'])}")
    
    if not index_data['documents']:
        print("No documents to embed!")
        return
    
    print("Generating embeddings...")
    texts = [doc['content'] for doc in index_data['documents']]
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Convert to float32 for FAISS
    embeddings = embeddings.astype(np.float32)
    
    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
    
    # Add vectors to index
    index.add(embeddings)
    
    # Save index and metadata
    vec_dir = Path('$vecDir')
    faiss.write_index(index, str(vec_dir / 'index.faiss'))
    
    with open(vec_dir / 'index.json', 'w') as f:
        json.dump(index_data, f, indent=2)
    
    print(f" Index saved to {vec_dir}")
    print(f"Index size: {len(index_data['documents'])} documents")
    print(f"Embedding dimension: {dimension}")

if __name__ == '__main__':
    main()
"@

# Save and run the embedding script
$embedScriptPath = Join-Path $vecDir "embed_script.py"
$embedScript | Out-File $embedScriptPath -Encoding utf8

Write-Host "Running embedding process..."
python $embedScriptPath

if ($LASTEXITCODE -eq 0) {
    Write-Host " GPU-RAG index complete!"
    Write-Host "Index location: $vecDir"
} else {
    Write-Error "Embedding process failed"
    exit 1
}
