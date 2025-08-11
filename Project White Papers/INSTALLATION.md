# INSTALLATION.md - Agent Exo-Suit V4.0 "Perfection" Installation Guide

**Version:** V4.0 "Perfection"  
**Last Updated:** January 2025  
**Status:** Production Ready - Full V4 Feature Set  
**Target Audience:** AI developers, system administrators, security professionals, enterprise teams

---

## **OVERVIEW**

This comprehensive installation guide covers the complete setup of **Agent Exo-Suit V4.0 "Perfection"**, an enterprise-grade AI agent development and management platform that provides GPU acceleration, intelligent context management, comprehensive security scanning, and advanced project health monitoring.

### **What You'll Get**
- **GPU-Accelerated RAG System**: Hybrid CPU+GPU processing with FAISS vector search
- **Comprehensive Security Suite**: Emoji detection, drift protection, vulnerability scanning
- **Advanced Monitoring**: Real-time GPU monitoring, power management, health scanning
- **Multi-language Support**: Python, JavaScript, C#, Java, Go, Rust, and more
- **Enterprise Features**: Target uptime goals, graceful error handling, comprehensive logging

---

## **SYSTEM REQUIREMENTS**

### **Hardware Requirements**
- **CPU**: 4+ cores recommended (8+ for optimal performance)
- **RAM**: 8GB+ (16GB+ for optimal performance)
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)
  - RTX 4000 series (RTX 4060, 4070, 4080, 4090)
  - GTX series (GTX 1660, RTX 2000, RTX 3000)
  - Tesla series (T4, V100, A100)
- **Storage**: SSD recommended for faster I/O
- **Network**: Internet connection for package downloads

### **Software Requirements**
- **Operating System**: Windows 10/11, Linux, macOS
- **Python**: 3.8+ (3.13+ recommended with CPU fallback for some packages)
- **PowerShell**: 7.0+ (Windows)
- **Git**: 2.0+ (for drift detection)
- **CUDA**: 11.8+ (for GPU acceleration)

### **Dependencies**
- **Core ML**: torch, transformers, sentence-transformers
- **Vector Search**: faiss-cpu/faiss-gpu
- **Data Processing**: numpy, pandas, scikit-learn
- **Utilities**: tqdm, colorama, filelock
- **Visualization**: mermaid, matplotlib

---

## **INSTALLATION METHODS**

### **Method 1: Quick Start (Recommended)**

#### **Step 1: Clone Repository**
```bash
git clone <repository-url>
cd "Agent Exo-Suit"
```

#### **Step 2: Run Auto-Setup**
```powershell
# Windows PowerShell
.\AgentExoSuitV4.ps1 -FullSystem

# Or use the go-big script
.\go-big.ps1
```

#### **Step 3: Verify Installation**
```powershell
# Test all components
.\Cleanup\Testing_Tools\test-runner.ps1
```

### **Method 2: Manual Installation**

#### **Step 1: Environment Setup**
```bash
# Create virtual environment
python -m venv gpu_rag_env
source gpu_rag_env/bin/activate  # Linux/macOS
# or
gpu_rag_env\Scripts\activate     # Windows
```

#### **Step 2: Install Core Dependencies**
```bash
# Install base requirements
pip install -r rag\requirements_hybrid_v4.txt

# For GPU acceleration (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For GPU FAISS (optional)
pip install faiss-gpu
```

#### **Step 3: Install Additional Dependencies**
```bash
# Install specialized packages
pip install sentence-transformers
pip install transformers
pip install numpy pandas scikit-learn
pip install tqdm colorama filelock
pip install mermaid matplotlib
```

---

## **COMPONENT-SPECIFIC SETUP**

### **1. GPU-RAG-V4.0 System Setup**

#### **GPU Environment Setup**
```powershell
# Run GPU RAG setup
.\ops\GPU-RAG-V4.ps1 -Mode Setup

# Verify GPU detection
.\ops\GPU-RAG-V4.ps1 -Mode Test
```

#### **Configuration File**
Create `rag\hybrid_config_v4.yaml`:
```yaml
# Device Configuration
device:
  primary: "auto"  # auto, cuda, cpu
  hybrid_mode: true
  load_balancing: "dynamic"

# RAM Disk Configuration
ram_disk:
  enabled: true
  size_gb: 4
  cleanup_interval: 100

# Memory Management
memory:
  system_threshold: 0.8
  gpu_threshold: 0.85
  cleanup_aggressive: true

# Performance Optimization
performance:
  mixed_precision: true
  warmup_batches: 3
  prefetch_factor: 2
```

#### **Environment Variables**
```bash
# Set CUDA device
export CUDA_VISIBLE_DEVICES=0

# Memory optimization
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

# Performance tuning
export OMP_NUM_THREADS=8
```

**Windows PowerShell equivalent:**
```powershell
# Set CUDA device
$env:CUDA_VISIBLE_DEVICES = "0"

# Memory optimization
$env:PYTORCH_CUDA_ALLOC_CONF = "max_split_size_mb:128"

# Performance tuning
$env:OMP_NUM_THREADS = "8"
```

### **2. Emoji Sentinel V4.0 Setup**

#### **Basic Setup**
```powershell
# Test emoji detection
.\ops\emoji-sentinel-v4.ps1 -Path "test-directory"

# Set environment variables
$env:EMOJI_SCAN_DIR = "C:\Your\Scan\Directory"
$env:EMOJI_CACHE_DIR = "C:\Your\Cache\Directory"
```

#### **Configuration Options**
```powershell
# Advanced scanning options
.\ops\emoji-sentinel-v4.ps1 -Path "test-directory" -Verbose -Json -Remove
```

### **3. Context Governor V4.0 Setup**

#### **Python Environment**
```bash
# Install context management dependencies
pip install sentence-transformers torch numpy

# Test context governor
python -c "
from ops.context_governor import ContextGovernor
governor = ContextGovernor()
print('Context Governor initialized successfully')
"
```

#### **Configuration**
```python
# Context governor configuration
config = {
    'model_name': 'all-MiniLM-L6-v2',
    'chunk_size': 512,
    'chunk_overlap': 50,
    'device': 'auto',
    'max_tokens': 8192
}
```

### **4. Drift Guard V4.0 Setup**

#### **Git Repository Setup**
```bash
# Initialize Git repository (if not already done)
git init
git add .
git commit -m "Initial commit"

# Test drift detection
.\ops\Drift-Guard-V4.ps1 -Path "."
```

#### **Configuration**
```powershell
# Set drift detection parameters
$env:DRIFT_CHECK_INTERVAL = "300"  # 5 minutes
$env:DRIFT_ALERT_ENABLED = "true"
```

### **5. Project Health Scanner V4.0 Setup**

#### **System Requirements Check**
```powershell
# Run health scanner
.\ops\Project-Health-Scanner-V4.ps1 -ProjectPath "." -OutputPath "restore"

# Check system requirements
.\ops\Project-Health-Scanner-V4.ps1 -Mode SystemCheck
```

#### **Configuration**
```yaml
# Health scanner configuration
health_scanner:
  system_check: true
  dependency_scan: true
  performance_analysis: true
  security_scan: true
  output_formats: ["json", "html", "txt"]
```

### **6. Security Scanner V4.0 Setup**

#### **Secret Detection Setup**
```powershell
# Run security scan
.\ops\Scan-Secrets-V4.ps1 -Root "." -Verbose

# Configure scan patterns
$env:SECRET_PATTERNS = "aws_key,api_key,database_password"
```

#### **Configuration**
```yaml
# Security scanner configuration
security_scanner:
  secret_patterns:
    - aws_key
    - api_key
    - database_password
    - private_key
  file_extensions:
    - .py, .js, .java, .cs, .go, .rs
  exclude_patterns:
    - node_modules/
    - .git/
    - __pycache__/
```

### **7. Import Indexer V4.0 Setup**

#### **Language-Specific Setup**
```bash
# Python dependencies
pip install ast astunparse

# JavaScript dependencies
npm install -g @babel/parser @babel/traverse

# C# dependencies
dotnet tool install -g Microsoft.CodeAnalysis.CSharp
```

#### **Configuration**
```powershell
# Run import indexer
.\ops\Import-Indexer-V4.ps1 -Path "test-directory" -Verbose

# Configure language support
$env:SUPPORTED_LANGUAGES = "python,javascript,typescript,csharp,java,go,rust"
```

### **8. Symbol Indexer V4.0 Setup**

#### **Symbol Analysis Setup**
```bash
# Install symbol analysis tools
pip install ast astunparse jedi

# Test symbol indexing
python -c "
from ops.symbol_indexer import SymbolIndexer
indexer = SymbolIndexer()
print('Symbol Indexer initialized successfully')
"
```

#### **Configuration**
```powershell
# Run symbol indexer
.\ops\Symbol-Indexer-V4.ps1 -Path "test-directory" -Verbose

# Configure symbol types
$env:SYMBOL_TYPES = "function,class,variable,constant,enum,interface"
```

### **9. Power Management V4.0 Setup**

#### **Administrator Setup**
```powershell
# Run as Administrator
Start-Process PowerShell -Verb RunAs -ArgumentList "-File", "ops\Power-Management-V4.ps1"

# Test power management
.\ops\Power-Management-V4.ps1 -Mode Test
```

#### **Configuration**
```yaml
# Power management configuration
power_management:
  performance_mode: true
  registry_tuning: true
  service_optimization: true
  process_priority: "high"
  memory_optimization: true
```

### **10. GPU Monitor V4.0 Setup**

#### **GPU Monitoring Setup**
```powershell
# Test GPU monitoring
.\ops\GPU-Monitor-V4.ps1 -Mode Test

# Start continuous monitoring
.\ops\GPU-Monitor-V4.ps1 -Mode Monitor -Interval 5
```

#### **Configuration**
```yaml
# GPU monitor configuration
gpu_monitor:
  monitoring_interval: 5
  temperature_threshold: 80
  memory_threshold: 0.9
  alert_enabled: true
  log_enabled: true
```

---

## **TESTING & VALIDATION**

### **Comprehensive Test Suite**
```powershell
# Run all tests
.\Cleanup\Testing_Tools\test-runner.ps1

# Individual component tests
.\Cleanup\Testing_Tools\quick-test.ps1
```

### **Component-Specific Tests**
```powershell
# Test GPU RAG system
.\ops\GPU-RAG-V4.ps1 -Mode Test

# Test emoji sentinel
.\ops\emoji-sentinel-v4.ps1 -Path "test-emoji-pack"

# Test drift guard
.\ops\Drift-Guard-V4.ps1 -Path "test-emoji-pack"

# Test context governor
python -c "from ops.context_governor import test_context_governor; test_context_governor()"

# Test health scanner
.\ops\Project-Health-Scanner-V4.ps1 -ProjectPath "test-emoji-pack" -OutputPath "restore"

# Test security scanner
.\ops\Scan-Secrets-V4.ps1 -Root "test-emoji-pack"

# Test import indexer
.\ops\Import-Indexer-V4.ps1 -Path "test-emoji-pack"

# Test symbol indexer
.\ops\Symbol-Indexer-V4.ps1 -Path "test-emoji-pack"

# Test power management
.\ops\Power-Management-V4.ps1

# Test GPU monitor
.\ops\GPU-Monitor-V4.ps1
```

### **Performance Benchmarks**
```powershell
# Run GPU RAG benchmark
.\ops\GPU-RAG-V4.ps1 -Mode Benchmark

# Run hybrid RAG benchmark
cd rag
python test_hybrid_comprehensive_v4.py
```

---

## **CONFIGURATION OPTIONS**

### **Global Configuration**
Create `config.yaml` in the root directory:
```yaml
# Global configuration
global:
  log_level: "INFO"
  output_directory: "restore"
  cache_directory: "cache"
  temp_directory: "temp"

# Component configuration
components:
  gpu_rag:
    enabled: true
    model_name: "all-MiniLM-L6-v2"
    batch_size: 32
    device: "auto"
  
  emoji_sentinel:
    enabled: true
    remove_emojis: true
    log_emojis: true
    cache_enabled: true
  
  drift_guard:
    enabled: true
    check_interval: 300
    alert_enabled: true
  
  context_governor:
    enabled: true
    chunk_size: 512
    chunk_overlap: 50
    max_tokens: 8192
  
  health_scanner:
    enabled: true
    system_check: true
    dependency_scan: true
    performance_analysis: true
  
  security_scanner:
    enabled: true
    secret_patterns: ["aws_key", "api_key", "database_password"]
    exclude_patterns: ["node_modules/", ".git/"]
  
  import_indexer:
    enabled: true
    supported_languages: ["python", "javascript", "typescript", "csharp", "java", "go", "rust"]
  
  symbol_indexer:
    enabled: true
    symbol_types: ["function", "class", "variable", "constant", "enum", "interface"]
  
  power_management:
    enabled: true
    performance_mode: true
    registry_tuning: true
  
  gpu_monitor:
    enabled: true
    monitoring_interval: 5
    temperature_threshold: 80
    memory_threshold: 0.9
```

### **Environment Variables**

**Linux/macOS:**
```bash
# Core environment variables
export EXO_SUIT_LOG_LEVEL="INFO"
export EXO_SUIT_OUTPUT_DIR="restore"
export EXO_SUIT_CACHE_DIR="cache"
export EXO_SUIT_TEMP_DIR="temp"

# GPU RAG environment variables
export CUDA_VISIBLE_DEVICES="0"
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128"
export OMP_NUM_THREADS="8"

# Emoji Sentinel environment variables
export EMOJI_SCAN_DIR="/path/to/scan/directory"
export EMOJI_CACHE_DIR="/path/to/cache/directory"
export EMOJI_REMOVE_ENABLED="true"

# Drift Guard environment variables
export DRIFT_CHECK_INTERVAL="300"
export DRIFT_ALERT_ENABLED="true"

# Context Governor environment variables
export CONTEXT_CHUNK_SIZE="512"
export CONTEXT_CHUNK_OVERLAP="50"
export CONTEXT_MAX_TOKENS="8192"

# Health Scanner environment variables
export HEALTH_SYSTEM_CHECK="true"
export HEALTH_DEPENDENCY_SCAN="true"
export HEALTH_PERFORMANCE_ANALYSIS="true"

# Security Scanner environment variables
export SECRET_PATTERNS="aws_key,api_key,database_password"
export SECRET_EXCLUDE_PATTERNS="node_modules/,.git/"

# Import Indexer environment variables
export SUPPORTED_LANGUAGES="python,javascript,typescript,csharp,java,go,rust"

# Symbol Indexer environment variables
export SYMBOL_TYPES="function,class,variable,constant,enum,interface"

# Power Management environment variables
export POWER_PERFORMANCE_MODE="true"
export POWER_REGISTRY_TUNING="true"

# GPU Monitor environment variables
export GPU_MONITOR_INTERVAL="5"
export GPU_TEMPERATURE_THRESHOLD="80"
export GPU_MEMORY_THRESHOLD="0.9"
```

**Windows PowerShell:**
```powershell
# Core environment variables
$env:EXO_SUIT_LOG_LEVEL = "INFO"
$env:EXO_SUIT_OUTPUT_DIR = "restore"
$env:EXO_SUIT_CACHE_DIR = "cache"
$env:EXO_SUIT_TEMP_DIR = "temp"

# GPU RAG environment variables
$env:CUDA_VISIBLE_DEVICES = "0"
$env:PYTORCH_CUDA_ALLOC_CONF = "max_split_size_mb:128"
$env:OMP_NUM_THREADS = "8"

# Emoji Sentinel environment variables
$env:EMOJI_SCAN_DIR = "C:\Your\Scan\Directory"
$env:EMOJI_CACHE_DIR = "C:\Your\Cache\Directory"
$env:EMOJI_REMOVE_ENABLED = "true"

# Drift Guard environment variables
$env:DRIFT_CHECK_INTERVAL = "300"
$env:DRIFT_ALERT_ENABLED = "true"

# Context Governor environment variables
$env:CONTEXT_CHUNK_SIZE = "512"
$env:CONTEXT_CHUNK_OVERLAP = "50"
$env:CONTEXT_MAX_TOKENS = "8192"

# Health Scanner environment variables
$env:HEALTH_SYSTEM_CHECK = "true"
$env:HEALTH_DEPENDENCY_SCAN = "true"
$env:HEALTH_PERFORMANCE_ANALYSIS = "true"

# Security Scanner environment variables
$env:SECRET_PATTERNS = "aws_key,api_key,database_password"
$env:SECRET_EXCLUDE_PATTERNS = "node_modules/,.git/"

# Import Indexer environment variables
$env:SUPPORTED_LANGUAGES = "python,javascript,typescript,csharp,java,go,rust"

# Symbol Indexer environment variables
$env:SYMBOL_TYPES = "function,class,variable,constant,enum,interface"

# Power Management environment variables
$env:POWER_PERFORMANCE_MODE = "true"
$env:POWER_REGISTRY_TUNING = "true"

# GPU Monitor environment variables
$env:GPU_MONITOR_INTERVAL = "5"
$env:GPU_TEMPERATURE_THRESHOLD = "80"
$env:GPU_MEMORY_THRESHOLD = "0.9"
```

---

## **TROUBLESHOOTING**

### **Common Installation Issues**

#### **1. Python Environment Issues**
```bash
# Check Python version
python --version

# Verify virtual environment
which python  # Linux/macOS
where python  # Windows

# Recreate virtual environment
rm -rf gpu_rag_env
python -m venv gpu_rag_env
source gpu_rag_env/bin/activate  # Linux/macOS
# or
gpu_rag_env\Scripts\activate     # Windows
```

#### **2. CUDA Installation Issues**
```bash
# Check CUDA installation
nvcc --version

# Check PyTorch CUDA support
python -c "import torch; print('CUDA:', torch.cuda.is_available())"

# Reinstall PyTorch with CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### **3. Package Installation Issues**
```bash
# Upgrade pip
pip install --upgrade pip

# Install packages individually
pip install torch
pip install transformers
pip install sentence-transformers
pip install faiss-cpu  # or faiss-gpu
```

#### **4. Permission Issues**
```powershell
# Run as Administrator (Windows)
Start-Process PowerShell -Verb RunAs

# Check file permissions
Get-Acl "path\to\file" | Format-List
```

#### **5. Path Issues**
```powershell
# Check PATH environment variable
$env:PATH -split ';'

# Add current directory to PATH
$env:PATH += ";$PWD"

# Check if scripts are executable
Get-ChildItem -Path "ops" -Filter "*.ps1" | Get-Acl
```

### **Component-Specific Issues**

#### **GPU-RAG Issues**
```bash
# Check GPU memory
nvidia-smi

# Test GPU functionality
python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU count: {torch.cuda.device_count()}')
    print(f'GPU name: {torch.cuda.get_device_name(0)}')
    print(f'GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
"
```

#### **Emoji Sentinel Issues**
```powershell
# Check file encoding
Get-Content "file.txt" -Encoding UTF8

# Test emoji detection
$testString = "Test string with emoji "
$hasEmoji = $testString -match "[\u{1F600}-\u{1F64F}]"
Write-Host "Has emoji: $hasEmoji"
```

#### **Drift Guard Issues**
```bash
# Check Git repository
git status
git log --oneline -5

# Verify Git configuration
git config --list

# Test Git functionality
git rev-parse HEAD
git rev-parse --abbrev-ref HEAD
```

---

## **PERFORMANCE OPTIMIZATION**

### **GPU Optimization**
```yaml
# GPU optimization configuration
gpu_optimization:
  mixed_precision: true
  memory_fraction: 0.8
  batch_size: 64
  num_workers: 4
  prefetch_factor: 2
```

### **Memory Optimization**
```yaml
# Memory optimization configuration
memory_optimization:
  cleanup_aggressive: true
  cleanup_interval: 100
  memory_threshold: 0.8
  gpu_memory_threshold: 0.85
```

### **Performance Tuning**
```yaml
# Performance tuning configuration
performance_tuning:
  warmup_batches: 3
  prefetch_factor: 2
  num_workers: 8
  batch_size: 64
  mixed_precision: true
```

---

## **POST-INSTALLATION**

### **Verification Checklist**
- [ ] All components installed successfully
- [ ] GPU acceleration working (if applicable)
- [ ] All tests passing
- [ ] Configuration files created
- [ ] Environment variables set
- [ ] Performance benchmarks completed
- [ ] Documentation reviewed

### **Next Steps**
1. **Read the User Guide**: Learn how to use all components
2. **Review Technical Specs**: Understand system architecture
3. **Run Performance Tests**: Benchmark your system
4. **Configure Alerts**: Set up monitoring and notifications
5. **Join Community**: Connect with other users

### **Support Resources**
- **Documentation**: Complete technical documentation
- **Community**: User forums and discussions
- **Issues**: Bug reports and feature requests
- **Support**: Direct technical support

---

## **GETTING STARTED**

### **Quick Start Commands**
```powershell
# 1. Setup the system
.\AgentExoSuitV4.ps1 -FullSystem

# 2. Test all components
.\Cleanup\Testing_Tools\test-runner.ps1

# 3. Run GPU RAG benchmark
.\ops\GPU-RAG-V4.ps1 -Mode Benchmark

# 4. Scan for emojis
.\ops\emoji-sentinel-v4.ps1 -Path "your-project"

# 5. Check project health
.\ops\Project-Health-Scanner-V4.ps1 -ProjectPath "your-project" -OutputPath "restore"

# 6. Monitor GPU
.\ops\GPU-Monitor-V4.ps1 -Mode Monitor
```

### **First Project Setup**
```powershell
# 1. Create project directory
mkdir my-project
cd my-project

# 2. Initialize Git repository
git init
git add .
git commit -m "Initial commit"

# 3. Run comprehensive scan
.\ops\Project-Health-Scanner-V4.ps1 -ProjectPath "." -OutputPath "restore"

# 4. Build RAG index
.\ops\GPU-RAG-V4.ps1 -Mode Index -InputPath "."

# 5. Query the index
.\ops\GPU-RAG-V4.ps1 -Mode Query -Query "your search query" -TopK 5
```

---

**Congratulations! You've successfully installed Agent Exo-Suit V4.0 "Perfection". You now have access to the most advanced AI agent development and management platform available, with GPU acceleration, comprehensive security scanning, and intelligent project management. Start exploring the possibilities!**

*Last Updated: January 2025*  
*Version: V4.0 "Perfection"*  
*Status: Production Ready - Full V4 Feature Set*
