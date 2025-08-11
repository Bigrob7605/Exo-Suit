# Context Assembly Script for Agent Exo-Suit V2.0
# Uses GPU-RAG to pull relevant chunks for specific tasks

param(
    [Parameter(Mandatory=$true)]
    [string]$query,
    
    [string]$root = $PWD.Path,
    [int]$budgetTokens = 12000,
    [int]$topK = 30,
    [string]$persona = "developer"
)

Write-Host " Assembling context for: '$query'"

# Check for RAG environment and index
$venvPath = Join-Path $root "rag_env"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Error "RAG environment not found. Run embed/setup.ps1 first."
    exit 1
}

# Check for index
$vecDir = Join-Path $root "context\vec"
$indexPath = Join-Path $vecDir "index.faiss"
$metadataPath = Join-Path $vecDir "index.json"

if (-not (Test-Path $indexPath) -or -not (Test-Path $metadataPath)) {
    Write-Error "FAISS index not found. Run embed/index.ps1 first."
    exit 1
}

# Activate environment
& $activateScript

# Create task context directory
$taskDir = Join-Path $root "context\_task"
New-Item -ItemType Directory -Force -Path $taskDir | Out-Null

# Python script for context assembly
$assembleScript = @"
import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path
import re
from datetime import datetime

def load_index(index_path, metadata_path):
    """Load FAISS index and metadata"""
    index = faiss.read_index(index_path)
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    return index, metadata

def search_index(query, index, metadata, model, top_k=$topK):
    """Search index for relevant chunks"""
    # Encode query
    query_embedding = model.encode([query])
    query_embedding = query_embedding.astype(np.float32)
    
    # Search index
    scores, indices = index.search(query_embedding, top_k)
    
    # Get relevant documents
    relevant_docs = []
    for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
        if idx < len(metadata['documents']):
            doc = metadata['documents'][idx].copy()
            doc['relevance_score'] = float(score)
            relevant_docs.append(doc)
    
    return relevant_docs

def prioritize_by_ownership(docs, ownership_path):
    """Prioritize documents by ownership"""
    if not os.path.exists(ownership_path):
        return docs
    
    try:
        with open(ownership_path, 'r') as f:
            ownership = json.load(f)
        
        # Create ownership map
        ownership_map = {item['Path']: item['Owner'] for item in ownership}
        
        # Score documents by ownership
        for doc in docs:
            doc_path = Path(doc['file'])
            doc['ownership_score'] = 0
            
            for owned_path, owner in ownership_map.items():
                if str(doc_path).startswith(str(owned_path)):
                    doc['ownership_score'] = 1 if owner == 'AI' else 0.5
                    break
        
        # Sort by ownership score (AI-owned first)
        docs.sort(key=lambda x: x.get('ownership_score', 0), reverse=True)
        
    except Exception as e:
        print(f"Warning: Could not load ownership data: {e}")
    
    return docs

def estimate_tokens(text):
    """Rough token estimation"""
    return len(text.split()) * 1.3  # Approximate token count

def assemble_context(docs, budget_tokens=$budgetTokens, persona='$persona'):
    """Assemble context within token budget"""
    context_parts = []
    total_tokens = 0
    
    # Persona-specific filters
    persona_filters = {
        'developer': ['*.py', '*.js', '*.ts', '*.tsx', '*.ps1', '*.sh'],
        'scientist': ['*.py', '*.md', '*.txt', '*.json', '*.yaml'],
        'devops': ['*.yaml', '*.yml', '*.json', '*.ps1', '*.sh', '*.md'],
        'ui': ['*.js', '*.ts', '*.tsx', '*.css', '*.html', '*.md']
    }
    
    allowed_extensions = persona_filters.get(persona, ['*'])
    
    for doc in docs:
        # Check if file type is allowed for persona
        if allowed_extensions != ['*']:
            doc_ext = Path(doc['file']).suffix.lower()
            if not any(doc_ext.endswith(ext.replace('*', '')) for ext in allowed_extensions):
                continue
        
        # Estimate tokens for this chunk
        chunk_tokens = estimate_tokens(doc['content'])
        
        if total_tokens + chunk_tokens > budget_tokens:
            break
        
        # Create context entry
        context_entry = f"""--- {doc['file']} (chunk {doc['chunk']}, score: {doc['relevance_score']:.3f}) ---
{doc['content']}

"""
        
        context_parts.append(context_entry)
        total_tokens += chunk_tokens
    
    return '\n'.join(context_parts), total_tokens

def main():
    print("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Loading FAISS index...")
    index, metadata = load_index('$indexPath', '$metadataPath')
    
    print("Searching for relevant chunks...")
    relevant_docs = search_index('$query', index, metadata, model)
    
    print(f"Found {len(relevant_docs)} relevant chunks")
    
    # Prioritize by ownership
    ownership_path = '$root/context/_latest/ownership.json'
    relevant_docs = prioritize_by_ownership(relevant_docs, ownership_path)
    
    # Assemble context
    print("Assembling context...")
    context_content, total_tokens = assemble_context(relevant_docs, $budgetTokens, '$persona')
    
    # Create task context file
    task_dir = Path('$taskDir')
    task_context_path = task_dir / 'task_context.md'
    
    header = f"""# Task Context: $query

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Persona:** $persona
**Token Budget:** {total_tokens:.0f}/$budgetTokens
**Relevant Chunks:** {len(relevant_docs)}

## Relevant Code and Documentation

"""
    
    with open(task_context_path, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write(context_content)
    
    # Create summary
    summary = {
        'query': '$query',
        'persona': '$persona',
        'total_tokens': total_tokens,
        'budget_tokens': $budgetTokens,
        'chunks_used': len(relevant_docs),
        'generated': datetime.now().isoformat(),
        'context_file': str(task_context_path)
    }
    
    with open(task_dir / 'context_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f" Context assembled! ({total_tokens:.0f} tokens)")
    print(f"Context file: {task_context_path}")
    print(f"Summary: {task_dir / 'context_summary.json'}")

if __name__ == '__main__':
    main()
"@

# Save and run the assembly script
$assembleScriptPath = Join-Path $taskDir "assemble_script.py"
$assembleScript | Out-File $assembleScriptPath -Encoding utf8

Write-Host "Running context assembly..."
python $assembleScriptPath

if ($LASTEXITCODE -eq 0) {
    Write-Host " Context assembly complete!"
    Write-Host "Task context: $taskDir\task_context.md"
} else {
    Write-Error "Context assembly failed"
    exit 1
}
