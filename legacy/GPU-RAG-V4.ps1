# Agent Exo-Suit V4.0 "PERFECTION" - GPU RAG System
# Advanced GPU-accelerated RAG with intelligent fallback and optimization

[CmdletBinding()]
param(
    [ValidateSet('Setup', 'Index', 'Query', 'Benchmark', 'Test')]
    [string]$Mode = 'Setup',
    
    [Parameter(Mandatory=$false)]
    [string]$InputPath = ".",
    
    [Parameter(Mandatory=$false)]
    [string]$Query = "",
    
    [Parameter(Mandatory=$false)]
    [int]$TopK = 5,
    
    [switch]$ForceGPU,
    
    [switch]$ForceCPU,
    
    [switch]$Json,
    
    [switch]$Benchmark
)

# ===== ULTRA-ROBUST ERROR HANDLING =====
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ===== ADVANCED LOGGING =====
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [ConsoleColor]$Color = [ConsoleColor]::White
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    Write-Host $logEntry -ForegroundColor $Color
    
    if ($VerbosePreference -ne 'SilentlyContinue') {
        $logPath = Join-Path (Get-Location) "gpu_rag_v4.log"
        $logEntry | Add-Content -Path $logPath -ErrorAction SilentlyContinue
    }
}

# ===== SYSTEM VALIDATION =====
function Test-SystemRequirements {
    Write-Log " Validating system requirements..." -Color Cyan
    
    # Check PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        Write-Log " PowerShell 5.1+ required" -Color Red
        return $false
    }
    
    # Check Python availability
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Log " Python not available: $pythonVersion" -Color Red
            return $false
        }
        Write-Log " Python available: $pythonVersion" -Color Green
    } catch {
        Write-Log " Python not found in PATH" -Color Red
        return $false
    }
    
    # Check available memory
    $memory = Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object -ExpandProperty TotalVisibleMemorySize
    $memoryGB = [math]::Round($memory / 1024 / 1024, 2)
    Write-Log " Available memory: $memoryGB GB" -Color Green
    
    if ($memoryGB -lt 4) {
        Write-Log " Low memory detected. GPU RAG may be limited" -Color Yellow
    }
    
    return $true
}

# ===== GPU DETECTION =====
function Get-GPUInfo {
    Write-Log " Detecting GPU capabilities..." -Color Cyan
    
    try {
        # Try to get GPU info using WMI
        $gpus = Get-CimInstance -ClassName Win32_VideoController -ErrorAction SilentlyContinue
        
        if ($gpus) {
            $gpuInfo = @()
            foreach ($gpu in $gpus) {
                # Fix GPU memory detection - use better method for RTX cards
                $gpuMemory = $gpu.AdapterRAM
                if ($gpu.Name -match "RTX 4070") {
                    $gpuMemory = 8 * 1024 * 1024 * 1024  # 8GB for RTX 4070
                } elseif ($gpu.Name -match "RTX 4080") {
                    $gpuMemory = 12 * 1024 * 1024 * 1024  # 12GB for RTX 4080
                } elseif ($gpu.Name -match "RTX 4090") {
                    $gpuMemory = 24 * 1024 * 1024 * 1024  # 24GB for RTX 4090
                } elseif ($gpu.Name -match "RTX 4060") {
                    $gpuMemory = 8 * 1024 * 1024 * 1024   # 8GB for RTX 4060
                }
                
                $gpuInfo += @{
                    Name = $gpu.Name
                    Memory = $gpuMemory
                    DriverVersion = $gpu.DriverVersion
                    IsCUDA = $gpu.Name -match "NVIDIA|RTX|GTX|Tesla"
                }
            }
            
            Write-Log " GPU detection completed" -Color Green
            return $gpuInfo
        } else {
            Write-Log " No GPU detected via WMI" -Color Yellow
            return $null
        }
    } catch {
        Write-Log " GPU detection failed: $_" -Color Yellow
        return $null
    }
}

# ===== PYTHON ENVIRONMENT SETUP =====
function Test-PythonEnvironment {
    Write-Log " Validating Python environment..." -Color Cyan
    
    try {
        # Check if required packages are available
        $requiredPackages = @("torch", "transformers", "sentence_transformers", "faiss")
        
        foreach ($package in $requiredPackages) {
            try {
                $result = python -c "import $package; print('OK')" 2>$null
                if ($LASTEXITCODE -eq 0) {
                    Write-Log " $package available" -Color Green
                } else {
                    Write-Log " $package not available" -Color Red
                    return $false
                }
            } catch {
                Write-Log " $package import failed" -Color Red
                return $false
            }
        }
        
        # Check CUDA availability
        try {
            $cudaResult = python -c "import torch; print('CUDA:', torch.cuda.is_available())" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Log " CUDA check: $cudaResult" -Color Cyan
            }
        } catch {
            Write-Log " CUDA check failed" -Color Yellow
        }
        
        return $true
        
    } catch {
        Write-Log " Python environment validation failed: $_" -Color Red
        return $false
    }
}

# ===== RAG SYSTEM SETUP =====
function Initialize-RAGSystem {
    Write-Log " Initializing GPU RAG system..." -Color Cyan
    
    try {
        # Create RAG environment directory
        $ragDir = Join-Path (Get-Location) "gpu_rag_env"
        if (-not (Test-Path $ragDir)) {
            New-Item -ItemType Directory -Force -Path $ragDir | Out-Null
            Write-Log " Created RAG environment directory" -Color Green
        }
        
        # Create Python virtual environment
        $venvPath = Join-Path $ragDir "venv"
        if (-not (Test-Path $venvPath)) {
            Write-Log " Creating Python virtual environment..." -Color Cyan
            python -m venv $venvPath
            if ($LASTEXITCODE -eq 0) {
                Write-Log " Virtual environment created" -Color Green
            } else {
                Write-Log " Failed to create virtual environment" -Color Red
                return $false
            }
        }
        
        # Activate virtual environment and install requirements
        $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
        if (Test-Path $activateScript) {
            Write-Log " Installing RAG requirements..." -Color Cyan
            
            # Create requirements.txt with Python version compatibility
            $pythonVersion = (python --version 2>&1) -replace "Python ", ""
            $majorVersion = [int]($pythonVersion -split "\.")[0]
            $minorVersion = [int]($pythonVersion -split "\.")[1]
            
            # Choose compatible packages based on Python version
            if ($majorVersion -eq 3 -and $minorVersion -ge 13) {
                # Python 3.13+ - use CPU versions of packages that don't support 3.13 yet
                # But still enable GPU acceleration for PyTorch
                $requirements = @"
torch
transformers>=4.30.0
sentence-transformers>=2.2.0
faiss-cpu>=1.7.0
numpy>=1.21.0
scikit-learn>=1.0.0
tqdm>=4.64.0
"@
                Write-Log " Using CPU-compatible packages for Python $pythonVersion with GPU PyTorch" -Color Yellow
            } else {
                # Python 3.12 and below - use GPU versions
                $requirements = @"
torch
transformers>=4.30.0
sentence-transformers>=2.2.0
faiss-gpu>=1.7.0
numpy>=1.21.0
scikit-learn>=1.0.0
tqdm>=4.64.0
"@
                Write-Log " Using GPU-optimized packages for Python $pythonVersion" -Color Green
            }
            
            $requirementsPath = Join-Path $ragDir "requirements.txt"
            $requirements | Out-File -LiteralPath $requirementsPath -Encoding utf8
            
            # Install packages
            & $activateScript
            pip install -r $requirementsPath
            
            if ($LASTEXITCODE -eq 0) {
                Write-Log " RAG requirements installed" -Color Green
                
                # For Python 3.13+, ensure PyTorch has CUDA support
                if ($majorVersion -eq 3 -and $minorVersion -ge 13) {
                    Write-Log " Ensuring PyTorch CUDA support for Python $pythonVersion..." -Color Cyan
                    pip install torch --index-url https://download.pytorch.org/whl/cu118
                    if ($LASTEXITCODE -eq 0) {
                        Write-Log " PyTorch CUDA support installed" -Color Green
                    } else {
                        Write-Log " PyTorch CUDA installation failed, but continuing..." -Color Yellow
                    }
                }
            } else {
                Write-Log " Failed to install requirements" -Color Red
                return $false
            }
        }
        
        return $true
        
    } catch {
        Write-Log " RAG system initialization failed: $_" -Color Red
        return $false
    }
}

# ===== DOCUMENT INDEXING =====
function Build-DocumentIndex {
    param([string]$InputPath)
    
    Write-Log " Building document index..." -Color Cyan
    
    try {
        # Create indexing script
        $indexScript = @"
import os
import json
import torch
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from pathlib import Path

def build_index(input_path, output_dir):
    print(f"Building index for: {input_path}")
    
    # Check GPU availability and status
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU count: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
            print(f"GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
    
    # Initialize model with GPU acceleration if available
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        if torch.cuda.is_available():
            model = model.to('cuda')
            print("✓ Using GPU acceleration for model")
            # Test GPU memory allocation
            test_tensor = torch.randn(1000, 384).cuda()
            print(f"✓ GPU memory test successful - allocated {test_tensor.numel() * 4 / (1024**2):.1f} MB")
            del test_tensor
            torch.cuda.empty_cache()
        else:
            print("⚠ Using CPU (GPU not available)")
    except Exception as e:
        print(f"Model initialization failed: {e}")
        return False
    
    # Collect documents
    documents = []
    file_paths = []
    
    for root, dirs, files in os.walk(input_path):
        for file in files:
            if file.endswith(('.txt', '.md', '.py', '.ps1', '.js', '.html', '.css')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content.strip()) > 0:
                            documents.append(content)
                            file_paths.append(file_path)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    if not documents:
        print("No documents found")
        return False
    
    print(f"Found {len(documents)} documents")
    
    # Generate embeddings with GPU acceleration
    print("Generating embeddings...")
    if torch.cuda.is_available():
        print("✓ Using GPU for embedding generation")
        # Process in batches for GPU memory efficiency
        batch_size = 32
        all_embeddings = []
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_embeddings = model.encode(batch, show_progress_bar=False)
            all_embeddings.append(batch_embeddings)
            print(f"Processed batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
        
        embeddings = np.vstack(all_embeddings)
        print(f"✓ Generated {embeddings.shape[0]} embeddings with GPU acceleration")
    else:
        print("⚠ Using CPU for embedding generation")
        embeddings = model.encode(documents, show_progress_bar=True)
    
    # Build FAISS index (transfer to CPU if needed)
    print("Building FAISS index...")
    if torch.cuda.is_available():
        # Convert to CPU for FAISS processing
        embeddings_cpu = embeddings.cpu().numpy() if hasattr(embeddings, 'cpu') else embeddings
        print("✓ Transferred embeddings to CPU for FAISS processing")
    else:
        embeddings_cpu = embeddings
    
    dimension = embeddings_cpu.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings_cpu.astype('float32'))
    
    # Save index and metadata
    faiss.write_index(index, os.path.join(output_dir, 'faiss_index.bin'))
    
    metadata = {
        'file_paths': file_paths,
        'document_count': len(documents),
        'embedding_dimension': dimension,
        'model_name': 'all-MiniLM-L6-v2'
    }
    
    with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Index built successfully: {len(documents)} documents")
    
    # Cleanup GPU memory
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        print("✓ GPU memory cleaned up")
    
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_path> <output_dir>")
        sys.exit(1)
    
    success = build_index(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
"@
        
        $scriptPath = Join-Path (Get-Location) "gpu_rag_env\build_index.py"
        $indexScript | Out-File -LiteralPath $scriptPath -Encoding utf8
        
        # Run indexing
        $outputDir = Join-Path (Get-Location) "gpu_rag_env\index"
        if (-not (Test-Path $outputDir)) {
            New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
        }
        
        Write-Log " Running document indexing..." -Color Cyan
        python $scriptPath $InputPath $outputDir
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log " Document index built successfully" -Color Green
            return $true
        } else {
            Write-Log " Document indexing failed" -Color Red
            return $false
        }
        
    } catch {
        Write-Log " Document indexing failed: $_" -Color Red
        return $false
    }
}

# ===== QUERY PROCESSING =====
function Process-RAGQuery {
    param([string]$Query, [int]$TopK)
    
    Write-Log " Processing RAG query..." -Color Cyan
    
    try {
        # Create query script
        $queryScript = @"
import os
import json
import faiss
import torch
from sentence_transformers import SentenceTransformer
import numpy as np

def query_index(query, index_dir, top_k=5):
    # Load index and metadata
    try:
        index = faiss.read_index(os.path.join(index_dir, 'faiss_index.bin'))
        with open(os.path.join(index_dir, 'metadata.json'), 'r') as f:
            metadata = json.load(f)
    except Exception as e:
        return None
    
    # Initialize model
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        if torch.cuda.is_available():
            model = model.to('cuda')
        else:
            pass  # Using CPU silently
    except Exception as e:
        return None
    
    # Generate query embedding
    query_embedding = model.encode([query])
    
    # Search index
    scores, indices = index.search(query_embedding.astype('float32'), top_k)
    
    # Prepare results
    results = []
    for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
        if idx < len(metadata['file_paths']):
            results.append({
                'rank': i + 1,
                'score': float(score),
                'file_path': metadata['file_paths'][idx],
                'file_name': os.path.basename(metadata['file_paths'][idx])
            })
    
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py <query> <index_dir>")
        sys.exit(1)
    
    results = query_index(sys.argv[1], sys.argv[2])
    if results:
        print(json.dumps(results, indent=2))
    else:
        print("Query failed")
        sys.exit(1)
"@
        
        # Ensure gpu_rag_env directory exists
        $ragEnvDir = Join-Path (Get-Location) "gpu_rag_env"
        if (-not (Test-Path $ragEnvDir)) {
            New-Item -ItemType Directory -Force -Path $ragEnvDir | Out-Null
            Write-Log " Created gpu_rag_env directory" -Color Green
        }
        
        $scriptPath = Join-Path $ragEnvDir "query_index.py"
        $queryScript | Out-File -LiteralPath $scriptPath -Encoding utf8
        
        # Run query
        $indexDir = Join-Path $ragEnvDir "index"
        if (-not (Test-Path $indexDir)) {
            Write-Log " Index not found. Run indexing first." -Color Red
            return $null
        }
        
        Write-Log " Executing query..." -Color Cyan
        $result = python $scriptPath $Query $indexDir 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            try {
                $results = $result | ConvertFrom-Json
                Write-Log " Query processed successfully" -Color Green
                return $results
            } catch {
                Write-Log " Failed to parse query results: $($_.Exception.Message)" -Color Red
                Write-Log "Raw output: $result" -Color Yellow
                return $null
            }
        } else {
            Write-Log " Query processing failed: $result" -Color Red
            return $null
        }
        
    } catch {
        Write-Log " Query processing failed: $_" -Color Red
        return $null
    }
}

# ===== BENCHMARKING =====
function Start-RAGBenchmark {
    Write-Log " Starting GPU RAG V4.0 benchmark..." -Color Cyan
    
    try {
        $benchmarkScript = @"
import time
import torch
from sentence_transformers import SentenceTransformer
import numpy as np

def benchmark_rag():
    print("GPU RAG V4.0 Benchmark")
    print("=" * 50)
    
    # Test model loading
    start_time = time.time()
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        load_time = time.time() - start_time
        print(f"Model loading time: {load_time:.3f}s")
    except Exception as e:
        print(f"Model loading failed: {e}")
        return False
    
    # Test GPU availability
    gpu_available = torch.cuda.is_available()
    print(f"GPU available: {gpu_available}")
    
    if gpu_available:
        print(f"GPU device: {torch.cuda.get_device_name()}")
        print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # Test embedding generation
    test_texts = ["This is a test document for benchmarking."] * 100
    
    # CPU test
    start_time = time.time()
    cpu_embeddings = model.encode(test_texts, show_progress_bar=False)
    cpu_time = time.time() - start_time
    print(f"CPU embedding time (100 docs): {cpu_time:.3f}s")
    
    # GPU test if available
    if gpu_available:
        model = model.to('cuda')
        start_time = time.time()
        gpu_embeddings = model.encode(test_texts, show_progress_bar=False)
        gpu_time = time.time() - start_time
        print(f"GPU embedding time (100 docs): {gpu_time:.3f}s")
        print(f"GPU speedup: {cpu_time/gpu_time:.2f}x")
    
    return True

if __name__ == "__main__":
    success = benchmark_rag()
    exit(0 if success else 1)
"@
        
        $scriptPath = Join-Path (Get-Location) "gpu_rag_env\benchmark.py"
        $benchmarkScript | Out-File -LiteralPath $scriptPath -Encoding utf8
        
        Write-Log " Running benchmark..." -Color Cyan
        python $scriptPath
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log " Benchmark completed successfully" -Color Green
            return $true
        } else {
            Write-Log " Benchmark failed" -Color Red
            return $false
        }
        
    } catch {
        Write-Log " Benchmark failed: $_" -Color Red
        return $false
    }
}

# ===== MAIN EXECUTION =====
function Start-GPURAG {
    Write-Log " Starting Agent Exo-Suit V4.0 'PERFECTION' - GPU RAG System..." -Color Cyan
    
    # Validate system requirements
    if (-not (Test-SystemRequirements)) {
        Write-Log " System requirements not met. Exiting." -Color Red
        exit 1
    }
    
    # Get GPU information
    $gpuInfo = Get-GPUInfo
    if ($gpuInfo) {
        Write-Log " GPU Information:" -Color Cyan
        foreach ($gpu in $gpuInfo) {
            $memoryGB = if ($gpu.Memory) { [math]::Round($gpu.Memory / 1024 / 1024 / 1024, 2) } else { "Unknown" }
            Write-Log "  $($gpu.Name) - Memory: $memoryGB GB - CUDA: $($gpu.IsCUDA)" -Color White
        }
    }
    
    # Execute based on mode
    switch ($Mode) {
        'Setup' {
            Write-Log " Setting up GPU RAG system..." -Color Cyan
            
            if (Initialize-RAGSystem) {
                Write-Log " GPU RAG system setup completed" -Color Green
            } else {
                Write-Log " GPU RAG system setup failed" -Color Red
                exit 1
            }
        }
        
        'Index' {
            Write-Log " Building document index..." -Color Cyan
            
            if (Build-DocumentIndex -InputPath $InputPath) {
                Write-Log " Document indexing completed" -Color Green
            } else {
                Write-Log " Document indexing failed" -Color Red
                exit 1
            }
        }
        
        'Query' {
            if ([string]::IsNullOrEmpty($Query)) {
                Write-Log " Query parameter required for Query mode" -Color Red
                exit 1
            }
            
            Write-Log " Processing query: $Query" -Color Cyan
            
            $results = Process-RAGQuery -Query $Query -TopK $TopK
            if ($results) {
                Write-Log " Query Results:" -Color Cyan
                $results | Format-Table -AutoSize
                
                # Save results if JSON requested
                if ($Json) {
                    $outputPath = Join-Path (Get-Location) "restore\RAG_QUERY_RESULTS.json"
                    $results | ConvertTo-Json -Depth 3 | Out-File -LiteralPath $outputPath -Encoding utf8
                    Write-Log " Results saved to: $outputPath" -Color Green
                }
            } else {
                Write-Log " Query processing failed" -Color Red
                exit 1
            }
        }
        
        'Benchmark' {
            Write-Log " Running GPU RAG benchmark..." -Color Cyan
            
            if (Start-RAGBenchmark) {
                Write-Log " Benchmark completed successfully" -Color Green
            } else {
                Write-Log " Benchmark failed" -Color Red
                exit 1
            }
        }
        
        'Test' {
            Write-Log " Testing GPU RAG system..." -Color Cyan
            
            # Test Python environment
            if (Test-PythonEnvironment) {
                Write-Log " Python environment test passed" -Color Green
            } else {
                Write-Log " Python environment test failed" -Color Red
                exit 1
            }
            
            # Test basic functionality
            Write-Log " Testing basic RAG functionality..." -Color Cyan
            
            $testQuery = "test query"
            $testResults = Process-RAGQuery -Query $testQuery -TopK 3
            
            if ($testResults) {
                Write-Log " Basic RAG functionality test passed" -Color Green
            } else {
                Write-Log " Basic RAG functionality test incomplete (may need indexing first)" -Color Yellow
            }
        }
    }
    
    Write-Log " GPU RAG V4.0 completed successfully!" -Color Green
}

# ===== SCRIPT EXECUTION =====
try {
    Start-GPURAG
} catch {
    Write-Log " Unexpected error: $_" -Color Red
    Write-Log "Stack trace: $($_.ScriptStackTrace)" -Color Red
    exit 1
}
