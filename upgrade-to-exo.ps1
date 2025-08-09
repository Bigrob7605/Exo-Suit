# upgrade-to-exo.ps1
$ErrorActionPreference='Stop'; Set-StrictMode -Version Latest

# --- sanity checks ---
@('python','git','pwsh') | % { if (-not (Get-Command $_ -EA SilentlyContinue)) { throw "$_ missing" } }

# --- dirs ---
'mermaid','rag','restore','context\_latest' | % { New-Item -ItemType Directory -Force $_ | Out-Null }

# --- Python stack ---
python -m pip install --upgrade pip wheel
$gpu = [bool](Get-Command nvidia-smi -EA SilentlyContinue)
$torchUrl = $gpu ? 'https://download.pytorch.org/whl/cu121' : 'https://download.pytorch.org/whl/cpu'
pip install torch --index-url $torchUrl -q
pip install ($gpu ? 'faiss-gpu' : 'faiss-cpu') -q
pip install sentence-transformers psutil numpy mermaid-py -q

# --- ripgrep ---
if (-not (Get-Command rg -EA SilentlyContinue)) {
  Write-Host "Install ripgrep for 10× faster indexing ↗ https://github.com/BurntSushi/ripgrep/releases" -ForegroundColor Yellow
}

# --- env ---
@"
EMBEDDING_MODEL=all-MiniLM-L6-v2
FAISS_INDEX_PATH=rag/index.faiss
RAG_META_PATH=rag/meta.jsonl
CACHE_DRIVE=C:
CHUNK_TOKENS=800
CHUNK_OVERLAP=120
TOPK=60
"@ | Out-File '.env' -Encoding utf8

Write-Host "✅ Exo-Suit v2.1 bootstrap complete. Run .\go-big.ps1" -ForegroundColor Green
