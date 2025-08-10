# 🚨 TROUBLESHOOTING.md - Agent Exo-Suit V3.0 Problem Resolution

**Document Type:** Troubleshooting & Problem Resolution  
**Version:** V3.0 "Monster-Mode"  
**Last Updated:** January 2025  
**Target Audience:** Support engineers, developers, system administrators, end users

---

## 🎯 **Troubleshooting Overview**

This document provides **comprehensive problem resolution procedures** for the Agent Exo-Suit V3.0 system. Follow these procedures systematically to identify, diagnose, and resolve issues quickly and effectively.

---

## 🚨 **Emergency Procedures**

### **🆘 System Unresponsive or Crashed**

#### **Immediate Response**
```powershell
# 1. Force stop all processes
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*powershell*"} | Stop-Process -Force

# 2. Restore normal power plan
powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e

# 3. Clean up scratch directories
Remove-Item -Path "$env:TEMP\exocache" -Recurse -Force -ErrorAction SilentlyContinue

# 4. Restart system
.\go-big.ps1
```

#### **If System Won't Start**
```powershell
# 1. Check system resources
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10
Get-Counter "\Memory\Available MBytes" -SampleInterval 1 -MaxSamples 1

# 2. Check disk space
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace

# 3. Check event logs
Get-EventLog -LogName Application -Newest 20 | Where-Object {$_.EntryType -eq "Error"}
```

### **🔥 GPU Overheating or Issues**

#### **Immediate GPU Recovery**
```powershell
# 1. Check GPU status
.\ops\gpu-monitor.ps1

# 2. Restore normal GPU settings
.\AgentExoSuitV3.ps1 -Restore

# 3. Check system temperature
Get-WmiObject -Class MSAcpi_ThermalZoneTemperature -Namespace "root/wmi" | Select-Object CurrentTemperature

# 4. If severe, restart with GPU disabled
.\go-big.ps1 -SkipGpu
```

#### **GPU Temperature Monitoring**
```powershell
# Continuous GPU monitoring
while ($true) {
    .\ops\gpu-monitor.ps1
    Start-Sleep 5
    Clear-Host
    
    # Check if temperature is critical
    $temp = (.\ops\gpu-monitor.ps1 | Select-String "Temperature:" | ForEach-Object { $_.ToString().Split(":")[1].Trim() })
    if ($temp -gt "85°C") {
        Write-Host "WARNING: GPU temperature critical!" -ForegroundColor Red
        .\AgentExoSuitV3.ps1 -Restore
        break
    }
}
```

---

## 🔍 **Systematic Problem Diagnosis**

### **1️⃣ Problem Classification Matrix**

#### **Issue Categories**
```markdown
## Problem Classification
**CRITICAL:** System down, data loss, security breach
**HIGH:** Core functionality broken, performance severely degraded
**MEDIUM:** Non-critical features broken, usability impacted
**LOW:** Minor issues, cosmetic problems, performance slightly degraded
```

#### **Symptom-Based Diagnosis**
```markdown
## Common Symptoms & Causes
**System won't start** → Resource exhaustion, corrupted files, permission issues
**Commands fail** → Execution policy, missing dependencies, path issues
**Performance slow** → Resource contention, memory leaks, GPU issues
**Errors appear** → Configuration issues, missing files, permission problems
**Drift detected** → Uncommitted changes, untracked files, git issues
```

### **2️⃣ Diagnostic Command Sequence**

#### **Basic System Check**
```powershell
# 1. Check system status
.\ops\drift-gate.ps1

# 2. Run health scan
.\ops\placeholder-scan.ps1

# 3. Check system resources
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10 ProcessName, WorkingSet, CPU
Get-Counter "\Processor(_Total)\% Processor Time", "\Memory\Available MBytes" -SampleInterval 1 -MaxSamples 1

# 4. Check disk space
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace

# 5. Check event logs
Get-EventLog -LogName Application -Newest 20 | Where-Object {$_.EntryType -eq "Error"}
```

#### **Advanced Diagnostics**
```powershell
# 1. Comprehensive health check
.\ops\Project-Health-Scanner.ps1 "C:\My Projects\Agent Exo-Suit" "C:\My Projects\Agent Exo-Suit\context\_latest"

# 2. GPU diagnostics (if applicable)
.\ops\gpu-monitor.ps1
.\ops\gpu-accelerator.ps1

# 3. Performance diagnostics
Measure-Command { .\ops\placeholder-scan.ps1 }
Measure-Command { .\ops\drift-gate.ps1 }

# 4. Context diagnostics
Get-ChildItem "context\_latest\*" -Recurse | Select-Object Name, Length, LastWriteTime
```

---

## 🐛 **Common Issues & Solutions**

### **1️⃣ PowerShell Execution Issues**

#### **Problem: Execution Policy Error**
```powershell
# Error Message
# "Cannot run script due to execution policy"

# Solution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify
Get-ExecutionPolicy -List
```

#### **Problem: Permission Denied**
```powershell
# Error Message
# "Access denied" or "Insufficient privileges"

# Solution
Start-Process PowerShell -Verb RunAs

# Alternative: Check current user
whoami
Get-LocalGroupMember -Group "Administrators"
```

#### **Problem: Script Not Found**
```powershell
# Error Message
# "The term '.\script.ps1' is not recognized"

# Solution
# Check current directory
Get-Location
Get-ChildItem -Name "*.ps1"

# Navigate to correct directory
Set-Location "C:\My Projects\Agent Exo-Suit"
```

### **2️⃣ System Resource Issues**

#### **Problem: Out of Memory**
```powershell
# Symptoms
# - Commands fail with memory errors
# - System becomes unresponsive
# - PowerShell crashes

# Diagnosis
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10
Get-Counter "\Memory\Available MBytes" -SampleInterval 1 -MaxSamples 1

# Solution
# 1. Stop unnecessary processes
Get-Process | Where-Object {$_.WorkingSet -gt 1GB} | Stop-Process -Force

# 2. Clear memory
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()

# 3. Restart system if needed
.\go-big.ps1
```

#### **Problem: High CPU Usage**
```powershell
# Symptoms
# - System becomes slow
# - Commands take long time
# - High fan noise

# Diagnosis
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
Get-Counter "\Processor(_Total)\% Processor Time" -SampleInterval 5 -MaxSamples 12

# Solution
# 1. Identify high-CPU processes
Get-Process | Where-Object {$_.CPU -gt 50} | Stop-Process -Force

# 2. Check for runaway processes
Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.CPU -gt 80}

# 3. Restart if needed
.\go-big.ps1
```

#### **Problem: Disk Space Exhaustion**
```powershell
# Symptoms
# - File operations fail
# - System becomes slow
# - Error messages about disk space

# Diagnosis
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace
Get-ChildItem -Path "$env:TEMP" -Recurse | Measure-Object -Property Length -Sum

# Solution
# 1. Clean temporary files
Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue

# 2. Clean scratch directories
Remove-Item -Path "$env:TEMP\exocache" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Clean context files
Remove-Item -Path "context\_latest\*.tmp" -Force -ErrorAction SilentlyContinue
```

### **3️⃣ Configuration Issues**

#### **Problem: Missing Environment Variables**
```powershell
# Symptoms
# - Commands fail with configuration errors
# - Default values used instead of custom settings
# - Path-related errors

# Diagnosis
Get-ChildItem Env: | Where-Object {$_.Name -like "*EXO*" -or $_.Name -like "*AGENT*"}
Get-Content ".env" -ErrorAction SilentlyContinue

# Solution
# 1. Check .env file
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# 2. Set default values
$env:MAX_TOKENS = "128000"
$env:GPU_MODE = "true"
$env:PERFORMANCE_MODE = "ultimate"
```

#### **Problem: Path Configuration Issues**
```powershell
# Symptoms
# - File not found errors
# - Wrong directories accessed
# - Permission errors

# Diagnosis
$env:PATH -split ";" | Where-Object { $_ -like "*exo*" -or $_ -like "*agent*" }
Get-Location
Test-Path "C:\My Projects\Agent Exo-Suit"

# Solution
# 1. Set correct working directory
Set-Location "C:\My Projects\Agent Exo-Suit"

# 2. Add project to PATH
$env:PATH += ";C:\My Projects\Agent Exo-Suit"

# 3. Verify paths
Test-Path "ops\drift-gate.ps1"
Test-Path "AgentExoSuitV3.ps1"
```

### **4️⃣ GPU-Related Issues**

#### **Problem: GPU Not Detected**
```powershell
# Symptoms
# - GPU commands fail
# - No GPU acceleration
# - Performance degradation

# Diagnosis
# 1. Check CUDA installation
python -c "import torch; print(torch.cuda.is_available())"

# 2. Check GPU drivers
nvidia-smi

# 3. Check GPU monitor
.\ops\gpu-monitor.ps1

# Solution
# 1. Install CUDA toolkit
# Download from NVIDIA website

# 2. Update GPU drivers
# Use device manager or NVIDIA GeForce Experience

# 3. Verify installation
python -c "import torch; print(torch.cuda.device_count())"
```

#### **Problem: GPU Overheating**
```powershell
# Symptoms
# - High GPU temperature
# - Performance throttling
# - System instability

# Diagnosis
.\ops\gpu-monitor.ps1

# Solution
# 1. Immediate: Restore normal settings
.\AgentExoSuitV3.ps1 -Restore

# 2. Check cooling
# Ensure proper airflow, clean dust

# 3. Adjust GPU settings
.\ops\gpu-accelerator.ps1 -Conservative
```

### **5️⃣ RAG System Issues**

#### **Problem: FAISS Index Build Fails**
```powershell
# Symptoms
# - Index building errors
# - Python exceptions
# - Memory errors

# Diagnosis
# 1. Check Python environment
python --version
pip list | Select-String "faiss\|torch\|transformers"

# 2. Check available memory
Get-Counter "\Memory\Available MBytes" -SampleInterval 1 -MaxSamples 1

# 3. Check disk space
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace

# Solution
# 1. Activate virtual environment
gpu_rag_env\Scripts\activate

# 2. Install missing packages
pip install faiss-cpu torch transformers sentence-transformers

# 3. Reduce index size
# Edit rag/build_index.py to use smaller model
```

#### **Problem: Context Retrieval Fails**
```powershell
# Symptoms
# - No search results
# - Python errors
# - Empty responses

# Diagnosis
# 1. Check index file
Test-Path "rag\faiss_index.bin"
Get-ChildItem "rag\*" | Select-Object Name, Length

# 2. Check context files
Test-Path "context\_latest\placeholders.json"
Get-Content "context\_latest\placeholders.json" | Select-Object -First 5

# Solution
# 1. Rebuild index
.\rag\embed.ps1

# 2. Regenerate context
.\ops\make-pack.ps1 "C:\My Projects\Agent Exo-Suit" "C:\My Projects\Agent Exo-Suit\context\_latest"

# 3. Test retrieval
python rag\retrieve.py "test query"
```

---

## 🔄 **Recovery Procedures**

### **1️⃣ System Recovery**

#### **Complete System Reset**
```powershell
# 1. Stop all processes
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*powershell*"} | Stop-Process -Force

# 2. Restore normal settings
.\AgentExoSuitV3.ps1 -Restore

# 3. Clean up temporary files
Remove-Item -Path "$env:TEMP\exocache" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "context\_latest\*.tmp" -Force -ErrorAction SilentlyContinue

# 4. Restart system
.\go-big.ps1

# 5. Verify recovery
.\ops\drift-gate.ps1
.\ops\placeholder-scan.ps1
```

#### **Context Recovery**
```powershell
# 1. Check backup files
Get-ChildItem "restore\*" -Recurse | Sort-Object LastWriteTime -Descending

# 2. Restore from backup
if (Test-Path "restore\DRIFT_REPORT.json") {
    Copy-Item "restore\DRIFT_REPORT.json" "context\_latest\"
}
if (Test-Path "restore\health_scan") {
    Copy-Item "restore\health_scan\*" "context\_latest\" -Recurse
}

# 3. Regenerate context
.\ops\make-pack.ps1 "C:\My Projects\Agent Exo-Suit" "C:\My Projects\Agent Exo-Suit\context\_latest"

# 4. Verify recovery
.\ops\drift-gate.ps1
.\ops\placeholder-scan.ps1
```

### **2️⃣ Performance Recovery**

#### **Performance Mode Recovery**
```powershell
# 1. Check current power plan
powercfg -list

# 2. Restore normal settings
.\AgentExoSuitV3.ps1 -Restore

# 3. Verify restoration
powercfg -list

# 4. Test normal operation
.\ops\placeholder-scan.ps1

# 5. Reactivate performance mode if needed
.\AgentExoSuitV3.ps1
```

#### **GPU Recovery**
```powershell
# 1. Check GPU status
.\ops\gpu-monitor.ps1

# 2. Restore normal GPU settings
.\AgentExoSuitV3.ps1 -Restore

# 3. Test GPU functionality
python -c "import torch; print(torch.cuda.is_available())"

# 4. Reactivate GPU acceleration if needed
.\ops\gpu-accelerator.ps1
```

---

## 🔧 **Advanced Debugging**

### **1️⃣ PowerShell Debugging**

#### **Enable Debug Mode**
```powershell
# 1. Enable verbose output
$VerbosePreference = "Continue"

# 2. Enable debug mode
$DebugPreference = "Continue"

# 3. Enable strict mode
Set-StrictMode -Version Latest

# 4. Run command with debugging
.\ops\drift-gate.ps1 -Verbose -Debug
```

#### **Step-by-Step Execution**
```powershell
# 1. Set breakpoints
Set-PSBreakpoint -Script "ops\drift-gate.ps1" -Line 10

# 2. Run with step-through
.\ops\drift-gate.ps1 -Step

# 3. Check variables
Get-Variable | Where-Object {$_.Name -like "*drift*"}

# 4. Check call stack
Get-PSCallStack
```

### **2️⃣ Python Debugging**

#### **Python Debug Mode**
```python
# 1. Add debug statements
import logging
logging.basicConfig(level=logging.DEBUG)

# 2. Use pdb debugger
import pdb
pdb.set_trace()

# 3. Add print statements
print(f"DEBUG: Variable value = {variable}")

# 4. Check exceptions
try:
    # Your code here
    pass
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
```

#### **Memory Profiling**
```python
# 1. Install memory profiler
# pip install memory-profiler

# 2. Profile memory usage
from memory_profiler import profile

@profile
def your_function():
    # Your code here
    pass

# 3. Run with profiling
# python -m memory_profiler your_script.py
```

---

## 📊 **Performance Troubleshooting**

### **1️⃣ Performance Bottleneck Identification**

#### **System Performance Analysis**
```powershell
# 1. Monitor system resources
Get-Counter "\Processor(_Total)\% Processor Time", "\Memory\Available MBytes", "\PhysicalDisk(_Total)\% Disk Time" -SampleInterval 5 -MaxSamples 12

# 2. Identify high-usage processes
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10 ProcessName, WorkingSet, CPU

# 3. Check disk I/O
Get-Counter "\PhysicalDisk(_Total)\% Disk Time", "\PhysicalDisk(_Total)\Avg. Disk Queue Length" -SampleInterval 5 -MaxSamples 12

# 4. Check network I/O
Get-Counter "\Network Interface(*)\Bytes Total/sec" -SampleInterval 5 -MaxSamples 12
```

#### **Command Performance Analysis**
```powershell
# 1. Measure command execution time
$startTime = Get-Date
.\ops\placeholder-scan.ps1
$endTime = Get-Date
$executionTime = ($endTime - $startTime).TotalSeconds
Write-Host "Execution time: $executionTime seconds"

# 2. Compare with baseline
$baseline = 2.5  # seconds
$performance = (($baseline - $executionTime) / $baseline) * 100
Write-Host "Performance: $([math]::Round($performance, 1))%"

# 3. Profile specific operations
Measure-Command { Get-ChildItem -Recurse | Measure-Object | Select-Object Count }
```

### **2️⃣ Performance Optimization**

#### **Memory Optimization**
```powershell
# 1. Check memory usage patterns
Get-Process | Where-Object {$_.WorkingSet -gt 100MB} | Select-Object ProcessName, WorkingSet, CPU

# 2. Optimize token limits
$env:MAX_TOKENS = "64000"  # Reduce for memory-constrained systems

# 3. Clear memory caches
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()

# 4. Monitor memory leaks
$initialMemory = (Get-Process -Id $PID).WorkingSet
# ... run operations ...
$finalMemory = (Get-Process -Id $PID).WorkingSet
$memoryIncrease = ($finalMemory - $initialMemory) / 1MB
Write-Host "Memory increase: $([math]::Round($memoryIncrease, 2)) MB"
```

#### **GPU Optimization**
```powershell
# 1. Check GPU utilization
.\ops\gpu-monitor.ps1

# 2. Optimize GPU settings
.\ops\gpu-accelerator.ps1

# 3. Monitor GPU temperature
while ($true) {
    $temp = (.\ops\gpu-monitor.ps1 | Select-String "Temperature:" | ForEach-Object { $_.ToString().Split(":")[1].Trim() })
    Write-Host "GPU Temperature: $temp"
    Start-Sleep 10
    
    if ($temp -gt "80°C") {
        Write-Host "WARNING: GPU temperature high!" -ForegroundColor Yellow
    }
}
```

---

## 📚 **Troubleshooting Resources**

### **Documentation References**
- **[INSTALLATION.md](INSTALLATION.md)** - Setup and configuration
- **[TECHNICAL_SPECS.md](TECHNICAL_SPECS.md)** - System architecture
- **[USER_GUIDE.md](USER_GUIDE.md)** - Daily operations
- **[QA_TESTING.md](QA_TESTING.md)** - Testing procedures

### **External Resources**
- **Microsoft PowerShell**: Official PowerShell documentation
- **Python Documentation**: Python language and library docs
- **CUDA Documentation**: NVIDIA GPU computing docs
- **FAISS Documentation**: Facebook AI similarity search docs

### **Community Support**
- **GitHub Issues**: Project issue tracking
- **Stack Overflow**: Programming Q&A
- **PowerShell Community**: PowerShell-specific help
- **Python Community**: Python-specific help

---

## 🎯 **Troubleshooting Success Criteria**

### **Problem Resolution Checklist**
- [ ] **Issue Identified**: Problem clearly defined
- [ ] **Root Cause Found**: Underlying cause determined
- [ ] **Solution Implemented**: Fix applied successfully
- [ ] **System Restored**: Full functionality restored
- [ ] **Testing Completed**: Solution verified with tests
- [ ] **Documentation Updated**: Procedures documented
- [ ] **Prevention Measures**: Steps to prevent recurrence

### **Recovery Validation**
- [ ] **System Health**: All health checks pass
- [ ] **Drift Status**: No drift detected
- [ ] **Performance**: Performance within acceptable range
- [ ] **Functionality**: All core functions working
- [ ] **Stability**: System stable for extended period
- [ ] **Documentation**: Recovery procedures documented

---

**🚨 Troubleshooting guide complete. Follow these procedures systematically to resolve issues quickly and restore system functionality.**
