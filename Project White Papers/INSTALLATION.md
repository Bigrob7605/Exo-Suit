# 🚀 INSTALLATION.md - Agent Exo-Suit V3.0 Setup Guide

**Document Type:** Installation & Setup  
**Version:** V3.0 "Monster-Mode"  
**Last Updated:** January 2025  
**Target Audience:** System administrators, developers, DevOps engineers

---

## 🎯 **Installation Overview**

This guide covers the complete installation and setup of the Agent Exo-Suit V3.0 system, from prerequisites to first-time configuration. The system is designed for high-performance development environments with optional GPU acceleration.

---

## 📋 **Prerequisites**

### **Hardware Requirements**

#### **Minimum Requirements**
- **CPU**: Intel i5-8th gen or AMD Ryzen 5 3000 series
- **RAM**: 16GB DDR4
- **Storage**: 256GB SSD (SATA or NVMe)
- **Network**: 100Mbps internet connection

#### **Recommended Requirements**
- **CPU**: Intel i7-13620H or AMD Ryzen 7 5000 series
- **RAM**: 32GB DDR4/DDR5
- **Storage**: 1TB+ NVMe SSD
- **GPU**: NVIDIA RTX 3060+ or AMD RX 6600+ (optional)
- **Network**: 1Gbps+ internet connection

#### **Optimal Performance (Your Setup)**
- **CPU**: Intel i7-13620H ✅
- **GPU**: NVIDIA RTX 4070 ✅
- **RAM**: 32GB+ DDR5 ✅
- **Storage**: NVMe SSD ✅

### **Software Requirements**

#### **Operating System**
- **Windows**: 10 (1903+) or 11 (21H2+)
- **macOS**: 12.0+ (Monterey)
- **Linux**: Ubuntu 20.04+, CentOS 8+, RHEL 8+

#### **PowerShell**
- **Windows**: PowerShell 7.0+ (PowerShell Core)
- **macOS/Linux**: PowerShell Core 7.0+
- **Installation**: `winget install Microsoft.PowerShell` (Windows)

#### **Python Environment**
- **Version**: Python 3.8+
- **Package Manager**: pip 20.0+
- **Virtual Environment**: venv or conda

#### **Optional Dependencies**
- **ripgrep**: For advanced symbol indexing
- **CUDA Toolkit**: For GPU acceleration (NVIDIA)
- **ROCm**: For GPU acceleration (AMD)

---

## 🚀 **Installation Steps**

### **Step 1: System Preparation**

#### **Windows Setup**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Install-Module -Name PSReadLine -Force
```

#### **PowerShell Core Installation**
```powershell
# Windows (winget)
winget install Microsoft.PowerShell

# Windows (Chocolatey)
choco install powershell-core

# macOS (Homebrew)
brew install powershell

# Linux (Ubuntu/Debian)
wget -q "https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb"
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y powershell
```

### **Step 2: Python Environment Setup**

#### **Python Installation**
```bash
# Windows (winget)
winget install Python.Python.3.11

# macOS (Homebrew)
brew install python@3.11

# Linux (Ubuntu/Debian)
sudo apt-get install python3.11 python3.11-venv python3.11-pip
```

#### **Virtual Environment Creation**
```bash
# Create virtual environment
python -m venv gpu_rag_env

# Activate (Windows)
gpu_rag_env\Scripts\activate

# Activate (macOS/Linux)
source gpu_rag_env/bin/activate
```

### **Step 3: Agent Exo-Suit Installation**

#### **Clone Repository**
```bash
git clone https://github.com/your-org/agent-exo-suit.git
cd agent-exo-suit
```

#### **Download Release Bundle**
```bash
# Download latest release
curl -L -o agent-exo-suit-v3.0.zip https://github.com/your-org/agent-exo-suit/releases/latest/download/agent-exo-suit-v3.0.zip

# Extract
Expand-Archive -Path agent-exo-suit-v3.0.zip -DestinationPath .
```

### **Step 4: Dependencies Installation**

#### **Python Dependencies**
```bash
# Activate virtual environment first
pip install -r requirements.txt

# Core dependencies
pip install sentence-transformers faiss-cpu torch torchvision

# GPU support (NVIDIA)
pip install faiss-gpu torch torchvision --index-url https://download.pytorch.org/whl/cu118

# GPU support (AMD)
pip install faiss-gpu torch torchvision --index-url https://download.pytorch.org/whl/rocm5.4
```

#### **System Dependencies**

##### **ripgrep Installation**
```bash
# Windows (Chocolatey)
choco install ripgrep

# Windows (Scoop)
scoop install ripgrep

# macOS (Homebrew)
brew install ripgrep

# Linux (Ubuntu/Debian)
sudo apt-get install ripgrep
```

##### **CUDA Toolkit (NVIDIA GPU)**
```bash
# Windows
# Download from: https://developer.nvidia.com/cuda-downloads

# Linux (Ubuntu)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get install cuda
```

---

## ⚙️ **Configuration**

### **Environment Variables Setup**

#### **Create .env File**
```bash
# Create environment file
New-Item -Path .env -ItemType File

# Add configuration
@"
# Cache and Performance
CACHE_DRIVE=C:
GPU_MODE=true
MAX_TOKENS=128000
PERFORMANCE_MODE=ultimate

# RAG Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
FAISS_INDEX_TYPE=IVF100,SQ8
VECTOR_DIMENSION=384

# System Configuration
LOG_LEVEL=INFO
PARALLEL_WORKERS=4
ENABLE_MONITORING=true
"@ | Out-File -FilePath .env -Encoding UTF8
```

#### **PowerShell Profile Configuration**
```powershell
# Edit PowerShell profile
notepad $PROFILE

# Add to profile
@"
# Agent Exo-Suit V3.0
Set-Location "C:\My Projects\Agent Exo-Suit"
Import-Module "C:\My Projects\Agent Exo-Suit\ops\Exo-Suit-Normal.ps1"
"@
```

### **Power Plan Configuration**

#### **Ultimate Performance Plan**
```powershell
# Create Ultimate Performance plan
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61

# Set as active
powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61

# Configure settings
powercfg -change -standby-timeout-ac 0
powercfg -change -hibernate-timeout-ac 0
powercfg -change -disk-timeout-ac 20
powercfg -change -processor-min-state-ac 100
powercfg -change -processor-max-state-ac 100
```

---

## 🧪 **Verification & Testing**

### **System Health Check**
```powershell
# Run comprehensive health scan
.\ops\Project-Health-Scanner.ps1 "C:\My Projects\Agent Exo-Suit" "C:\My Projects\Agent Exo-Suit\context\_latest"

# Check drift status
.\ops\drift-gate.ps1

# Run placeholder scan
.\ops\placeholder-scan.ps1
```

### **GPU Acceleration Test**
```powershell
# Test GPU availability
.\ops\gpu-monitor.ps1

# Test RAG performance
.\rag\embed.ps1

# Performance benchmark
.\ops\max-perf.ps1
```

### **Expected Results**
- **Health Scan**: All systems operational
- **Drift Detection**: No drift detected
- **GPU Test**: CUDA/ROCm available (if GPU present)
- **Performance**: 3-5x speedup in RAG operations

---

## 🔧 **Troubleshooting Installation**

### **Common Issues**

#### **PowerShell Execution Policy**
```powershell
# Error: Cannot run script due to execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **Python Path Issues**
```powershell
# Add Python to PATH
$env:PATH += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\Scripts"
$env:PATH += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311"
```

#### **CUDA Installation Issues**
```bash
# Verify CUDA installation
nvcc --version
nvidia-smi

# Check PyTorch CUDA support
python -c "import torch; print(torch.cuda.is_available())"
```

#### **Permission Denied Errors**
```powershell
# Run as Administrator
Start-Process PowerShell -Verb RunAs

# Check file permissions
Get-Acl "C:\My Projects\Agent Exo-Suit" | Format-List
```

### **Performance Issues**

#### **Slow RAG Operations**
```powershell
# Check GPU utilization
.\ops\gpu-monitor.ps1

# Verify FAISS index
python -c "import faiss; print(faiss.get_num_gpus())"
```

#### **Memory Issues**
```powershell
# Check memory usage
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10

# Adjust token limits
$env:MAX_TOKENS = "64000"
```

---

## 📊 **Installation Validation Checklist**

### **✅ Pre-Installation**
- [ ] System meets minimum requirements
- [ ] PowerShell 7.0+ installed
- [ ] Python 3.8+ installed
- [ ] Git client available
- [ ] Administrator privileges available

### **✅ Core Installation**
- [ ] Repository cloned/downloaded
- [ ] Virtual environment created
- [ ] Python dependencies installed
- [ ] System dependencies installed
- [ ] Environment variables configured

### **✅ GPU Acceleration (Optional)**
- [ ] CUDA toolkit installed (NVIDIA)
- [ ] ROCm installed (AMD)
- [ ] PyTorch with GPU support
- [ ] FAISS with GPU support
- [ ] GPU drivers updated

### **✅ Configuration**
- [ ] .env file created
- [ ] PowerShell profile updated
- [ ] Power plan configured
- [ ] Path variables set
- [ ] Permissions configured

### **✅ Verification**
- [ ] Health scan passes
- [ ] Drift detection works
- [ ] GPU acceleration functional
- [ ] Performance benchmarks pass
- [ ] All scripts executable

---

## 🚀 **Post-Installation Setup**

### **First-Time Configuration**
```powershell
# Run full system activation
.\go-big.ps1

# Configure ownership mapping
Edit-Item "OWNERS.md"

# Set up monitoring
.\ops\dashboard.ps1
```

### **Integration with Development Tools**
```powershell
# Cursor integration
Copy-Item "cursor\COMMAND_QUEUE.md" "$env:USERPROFILE\.cursor\"

# VS Code integration
code --install-extension ms-vscode.powershell
```

### **Automated Startup**
```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File 'C:\My Projects\Agent Exo-Suit\go-big.ps1'"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "Agent Exo-Suit Startup" -Action $action -Trigger $trigger
```

---

## 📞 **Support & Next Steps**

### **Getting Help**
1. **Check logs**: `context/_latest/` directory
2. **Run diagnostics**: `.\ops\Project-Health-Scanner.ps1`
3. **Review documentation**: Other MD files in this bundle

### **Next Steps**
1. **Read [USER_GUIDE.md](USER_GUIDE.md)** - Daily operations
2. **Review [TECHNICAL_SPECS.md](TECHNICAL_SPECS.md)** - System architecture
3. **Test with [QA_TESTING.md](QA_TESTING.md)** - Validation procedures
4. **Troubleshoot with [TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Problem resolution

---

**🎉 Installation complete! Your Agent Exo-Suit V3.0 is ready for production use.**
