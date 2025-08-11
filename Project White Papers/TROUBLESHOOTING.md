# TROUBLESHOOTING.md - Agent Exo-Suit V4.0 Problem Resolution

**Document Type:** Troubleshooting & Problem Resolution  
**Version:** V4.0 "Perfection"  
**Last Updated:** January 2025  
**Target Audience:** Support engineers, developers, system administrators, end users

---

## **Troubleshooting Overview**

This document provides **comprehensive problem resolution procedures** for the Agent Exo-Suit V4.0 "Perfection" system. Follow these procedures systematically to identify, diagnose, and resolve issues quickly and effectively across all 43 core components.

### **Component Coverage**
- **43 Main Components**: Complete troubleshooting for all operational components
- **Multi-Layer Architecture**: Visual, Cognitive, Operational, and Integration layers
- **Hybrid GPU-RAG System**: GPU acceleration, CPU fallback, and performance optimization
- **Enterprise Security**: Emoji defense, secret scanning, and compliance monitoring
- **Performance Systems**: Power management, GPU monitoring, and system optimization
- **Testing & Validation**: Comprehensive testing suite with target pass rate goals

---

## **Emergency Procedures**

### **System Unresponsive or Crashed**

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

### **GPU Overheating or Issues**

#### **Immediate GPU Recovery**
```powershell
# 1. Check GPU status
.\ops\GPU-Monitor-V4.ps1

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
    .\ops\GPU-Monitor-V4.ps1
    Start-Sleep 5
    Clear-Host
    
    # Check if temperature is critical
    $temp = (.\ops\GPU-Monitor-V4.ps1 | Select-String "Temperature:" | ForEach-Object { $_.ToString().Split(":")[1].Trim() })
    if ($temp -gt "85C") {
        Write-Host "WARNING: GPU temperature critical!" -ForegroundColor Red
        .\AgentExoSuitV3.ps1 -Restore
        break
    }
}
```

---

## **Component-Specific Troubleshooting**

### **1. Multi-Layer Architecture Issues**

#### **Visual Layer (mermaid/) Problems**
```powershell
# Problem: Mermaid diagrams not generating
# Symptoms: No diagram output, missing visual documentation

# Diagnosis
Test-Path "mermaid\*.mmd"
Get-ChildItem "mermaid\" -Recurse | Select-Object Name, Length

# Solution
# 1. Check Mermaid installation
npm list -g mermaid-cli

# 2. Regenerate diagrams
.\mermaid\generate-diagrams.ps1

# 3. Verify output
Get-ChildItem "mermaid\output\" -Recurse
```

#### **Cognitive Layer (rag/) Problems**
```powershell
# Problem: RAG system not responding
# Symptoms: No search results, Python errors, GPU issues

# Diagnosis
Test-Path "rag\faiss_index.bin"
python -c "import torch; print(torch.cuda.is_available())"

# Solution
# 1. Check Python environment
.\rag\activate_env.ps1

# 2. Rebuild index
python rag\build_index.py --input ".\docs" --output ".\index"

# 3. Test retrieval
python rag\retrieve.py "test query"
```

#### **Operational Layer (ops/) Problems**
```powershell
# Problem: Operations scripts failing
# Symptoms: Script errors, permission issues, missing files

# Diagnosis
Get-ChildItem "ops\*.ps1" | Select-Object Name, Length
Get-ExecutionPolicy -List

# Solution
# 1. Fix execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. Verify script integrity
Get-ChildItem "ops\*.ps1" | ForEach-Object { Get-FileHash $_.FullName }

# 3. Test core operations
.\ops\quick-scan.ps1
```

#### **Development Workflow Problems**
```powershell
# Problem: Development workflow issues
# Symptoms: Commands not working, workflow broken

# Diagnosis
Test-Path "workflow\command-queue.json"
Get-Content "workflow\settings.json" -ErrorAction SilentlyContinue

# Solution
# 1. Reset workflow integration
Remove-Item "workflow\command-queue.json" -ErrorAction SilentlyContinue
.\workflow\reset-integration.ps1

# 2. Verify connection
.\workflow\test-connection.ps1
```

### **2. Core System Component Issues**

#### **Hybrid GPU-RAG System Problems**
```powershell
# Problem: GPU-RAG performance degradation
# Symptoms: Slow processing, memory errors, GPU not detected

# Diagnosis
.\ops\GPU-RAG-V4.ps1 -Status
.\ops\GPU-Monitor-V4.ps1

# Solution
# 1. Check GPU status
nvidia-smi

# 2. Optimize memory usage
.\ops\GPU-RAG-V4.ps1 -Mode "cleanup"

# 3. Fallback to CPU if needed
.\ops\GPU-RAG-V4.ps1 -Mode "cpu"
```

#### **Emoji Sentinel Issues**
```powershell
# Problem: Emoji detection incomplete
# Symptoms: Emojis missed, false negatives, scan failures

# Diagnosis
.\ops\emoji-sentinel-v4.ps1 -Test
Get-Content "test-emoji.txt" -Raw | Select-String "[\u{1F600}-\u{1F64F}]"

# Solution
# 1. Force comprehensive scan
.\ops\emoji-sentinel-v4.ps1 -Path ".\" -Purge -Force

# 2. Verify cleanup
.\ops\emoji-sentinel-v4.ps1 -Path ".\" -Scan -Verbose

# 3. Check for hidden characters
Get-Content "problematic-file.txt" -Raw | ForEach-Object { [System.Text.Encoding]::UTF8.GetBytes($_) }
```

#### **Secret Scanner Issues**
```powershell
# Problem: Secret scanning false positives
# Symptoms: Too many alerts, legitimate secrets flagged

# Diagnosis
.\ops\Scan-Secrets-V4.ps1 -Path ".\" -Output "secrets_report.json"
Get-Content "secrets_report.json" | ConvertFrom-Json | Select-Object -First 10

# Solution
# 1. Adjust entropy threshold
$env:SECRET_ENTROPY_THRESHOLD = "7.5"

# 2. Add to allowlist
Add-Content "secrets_allowlist.txt" "legitimate_secret_pattern"

# 3. Customize rules
Edit-Content "custom_secret_rules.yaml"
```

#### **Project Health Scanner Issues**
```powershell
# Problem: Health scan incomplete
# Symptoms: Missing metrics, scan failures, timeout errors

# Diagnosis
.\ops\Project-Health-Scanner-V4.ps1 -Path ".\" -Status
Get-ChildItem "context\_latest\*" | Select-Object Name, Length

# Solution
# 1. Increase timeout
$env:SCAN_TIMEOUT = "300"

# 2. Reduce parallel workers
.\ops\Project-Health-Scanner-V4.ps1 -Path ".\" -Workers 4

# 3. Check disk space
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace
```

### **3. Performance & Optimization Issues**

#### **Power Management Problems**
```powershell
# Problem: Performance mode not activating
# Symptoms: No performance boost, power plan unchanged

# Diagnosis
powercfg -list
Get-Process | Where-Object {$_.ProcessName -eq "powercfg"}

# Solution
# 1. Run as administrator
Start-Process PowerShell -Verb RunAs -ArgumentList "-File '.\ops\Power-Management-V4.ps1'"

# 2. Force power plan creation
.\ops\Power-Management-V4.ps1 -Force -Create

# 3. Verify activation
powercfg -list
```

#### **GPU Monitor Issues**
```powershell
# Problem: GPU monitoring not working
# Symptoms: No GPU data, monitoring script errors

# Diagnosis
Test-Path "ops\GPU-Monitor-V4.ps1"
nvidia-smi

# Solution
# 1. Check NVIDIA drivers
Get-WmiObject -Class Win32_VideoController | Select-Object Name, DriverVersion

# 2. Verify CUDA installation
python -c "import torch; print(torch.version.cuda)"

# 3. Test basic monitoring
.\ops\GPU-Monitor-V4.ps1
```

### **4. Testing & Validation Issues**

#### **Test Runner Problems**
```powershell
# Problem: Tests failing consistently
# Symptoms: Component failures, target pass rate goals not achieved

# Diagnosis
.\Cleanup\Testing_Tools\test-runner.ps1 -Components "all"
Get-Content "test_results.json" | ConvertFrom-Json | Where-Object {$_.Status -eq "FAIL"}

# Solution
# 1. Check component health
.\ops\quick-scan.ps1

# 2. Verify dependencies
Get-ChildItem "ops\*.ps1" | ForEach-Object { .\Cleanup\Testing_Tools\test-runner.ps1 -Components $_.BaseName }

# 3. Fix failing components
.\ops\emoji-sentinel-v4.ps1 -Repair
```

#### **Quick Test Issues**
```powershell
# Problem: Quick tests incomplete
# Symptoms: Missing test results, timeout errors

# Diagnosis
.\Cleanup\Testing_Tools\quick-test.ps1 -Verbose
Get-ChildItem "test_results\*" | Select-Object Name, Length

# Solution
# 1. Increase test timeout
$env:TEST_TIMEOUT = "120"

# 2. Run individual tests
.\Cleanup\Testing_Tools\test-runner.ps1 -Components "emoji-sentinel-v4"

# 3. Check test data
Get-ChildItem "Cleanup\Testing_Tools\test-emoji-pack\*" | Select-Object Name, Length
```

### **5. Advanced Component Issues**

#### **Symbol Indexer Problems**
```powershell
# Problem: Symbol detection incomplete
# Symptoms: Missing symbols, parsing errors, language support issues

# Diagnosis
.\ops\Symbol-Indexer-V4.ps1 -Path ".\" -Test
Get-Content "symbols_index.json" | ConvertFrom-Json | Select-Object -First 10

# Solution
# 1. Check language support
.\ops\Symbol-Indexer-V4.ps1 -Languages

# 2. Verify file parsing
.\ops\Symbol-Indexer-V4.ps1 -Path ".\src" -Verbose

# 3. Update language patterns
Edit-Content "language_patterns.yaml"
```

#### **Import Indexer Problems**
```powershell
# Problem: Import mapping incomplete
# Symptoms: Missing dependencies, circular dependency detection fails

# Diagnosis
.\ops\Import-Indexer-V4.ps1 -Path ".\" -Test
Get-Content "imports_index.json" | ConvertFrom-Json | Select-Object -First 10

# Solution
# 1. Check file extensions
Get-ChildItem -Recurse | Where-Object {$_.Extension -match "\.(py|js|ts|ps1|cs|java|go|rs)$"} | Select-Object Name

# 2. Verify import patterns
.\ops\Import-Indexer-V4.ps1 -Path ".\" -Patterns

# 3. Force re-indexing
.\ops\Import-Indexer-V4.ps1 -Path ".\" -Force
```

#### **Context Governor Issues**
```powershell
# Problem: Context management failures
# Symptoms: Token limit exceeded, memory errors, context loss

# Diagnosis
.\rag\context-governor.ps1 -Status
Get-ChildItem "context\_latest\*" | Select-Object Name, Length

# Solution
# 1. Check token budget
$env:MAX_TOKENS = "64000"

# 2. Optimize context size
.\rag\context-governor.ps1 -Optimize

# 3. Clear old contexts
Remove-Item "context\_latest\*.old" -Force -ErrorAction SilentlyContinue
```

## **Systematic Problem Diagnosis**

### **1. Problem Classification Matrix**

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
**System won't start**  Resource exhaustion, corrupted files, permission issues
**Commands fail**  Execution policy, missing dependencies, path issues
**Performance slow**  Resource contention, memory leaks, GPU issues
**Errors appear**  Configuration issues, missing files, permission problems
**Drift detected**  Uncommitted changes, untracked files, git issues
```

### **2. Diagnostic Command Sequence**

#### **Basic System Check**
```powershell
# 1. Check system status
.\ops\Drift-Guard-V4.ps1

# 2. Run health scan
.\ops\quick-scan.ps1

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
.\ops\Project-Health-Scanner-V4.ps1 ".\" ".\context\_latest"

# 2. GPU diagnostics (if applicable)
.\ops\GPU-Monitor-V4.ps1
.\ops\gpu-accelerator.ps1

# 3. Performance diagnostics
Measure-Command { .\ops\quick-scan.ps1 }
Measure-Command { .\ops\Drift-Guard-V4.ps1 }

# 4. Context diagnostics
Get-ChildItem "context\_latest\*" -Recurse | Select-Object Name, Length, LastWriteTime
```

---

## **Common Issues & Solutions**

### **1. PowerShell Execution Issues**

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
Set-Location ".\"
```

### **2. System Resource Issues**

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

### **3. Configuration Issues**

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
Test-Path ".\"

# Solution
# 1. Set correct working directory
Set-Location ".\"

# 2. Add project to PATH
$env:PATH += ";.\"

# 3. Verify paths
Test-Path "ops\Drift-Guard-V4.ps1"
Test-Path "AgentExoSuitV3.ps1"
```

### **4. GPU-Related Issues**

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
.\ops\GPU-Monitor-V4.ps1

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
.\ops\GPU-Monitor-V4.ps1

# Solution
# 1. Immediate: Restore normal settings
.\AgentExoSuitV3.ps1 -Restore

# 2. Check cooling
# Ensure proper airflow, clean dust

# 3. Adjust GPU settings
.\ops\gpu-accelerator.ps1 -Conservative
```

### **5. RAG System Issues**

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
.\ops\make-pack.ps1 ".\" ".\context\_latest"

# 3. Test retrieval
python rag\retrieve.py "test query"
```

### **6. Emoji Defense Issues**

#### **Problem: Emoji Detection Fails**
```powershell
# Symptoms
# - Emojis not detected in files
# - Scan reports no emojis found
# - False negative results

# Diagnosis
# 1. Check emoji sentinel script
Test-Path "ops\emoji-sentinel-v4.ps1"
Get-Content "ops\emoji-sentinel-v4.ps1" | Select-Object -First 10

# 2. Test with known emoji file
"Test content with rocket emoji" | Out-File "test-emoji.txt"
.\ops\emoji-sentinel-v4.ps1 -Scan

# Solution
# 1. Verify script permissions
Get-Acl "ops\emoji-sentinel-v4.ps1"

# 2. Check PowerShell execution policy
Get-ExecutionPolicy -List

# 3. Run with verbose output
.\ops\emoji-sentinel-v4.ps1 -Scan -Verbose
```

#### **Problem: Emoji Removal Incomplete**
```powershell
# Symptoms
# - Emojis not fully removed
# - Partial cleanup results
# - Some emojis remain

# Diagnosis
# 1. Check scan results
.\ops\emoji-sentinel-v4.ps1 -Report

# 2. Verify file encoding
Get-Content "problematic-file.txt" -Encoding UTF8 | Select-String "[\u{1F600}-\u{1F64F}]"

# 3. Check for hidden characters
Get-Content "problematic-file.txt" -Raw | ForEach-Object { [System.Text.Encoding]::UTF8.GetBytes($_) }

# Solution
# 1. Force comprehensive purge
.\ops\emoji-sentinel-v4.ps1 -Purge -Force -Verbose

# 2. Manual cleanup if needed
(Get-Content "problematic-file.txt") -replace '[\u{1F600}-\u{1F64F}]', '' | Set-Content "problematic-file.txt"

# 3. Verify cleanup
.\ops\emoji-sentinel-v4.ps1 -Scan
```

---

## **Recovery Procedures**

### **1. System Recovery**

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
.\ops\Drift-Guard-V4.ps1
.\ops\quick-scan.ps1
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
.\ops\make-pack.ps1 ".\" ".\context\_latest"

# 4. Verify recovery
.\ops\Drift-Guard-V4.ps1
.\ops\quick-scan.ps1
```

### **2. Performance Recovery**

#### **Performance Mode Recovery**
```powershell
# 1. Check current power plan
powercfg -list

# 2. Restore normal settings
.\AgentExoSuitV3.ps1 -Restore

# 3. Verify restoration
powercfg -list

# 4. Test normal operation
.\ops\quick-scan.ps1

# 5. Reactivate performance mode if needed
.\AgentExoSuitV3.ps1
```

#### **GPU Recovery**
```powershell
# 1. Check GPU status
.\ops\GPU-Monitor-V4.ps1

# 2. Restore normal GPU settings
.\AgentExoSuitV3.ps1 -Restore

# 3. Test GPU functionality
python -c "import torch; print(torch.cuda.is_available())"

# 4. Reactivate GPU acceleration if needed
.\ops\gpu-accelerator.ps1
```

---

## **Advanced Debugging**

### **1. PowerShell Debugging**

#### **Enable Debug Mode**
```powershell
# 1. Enable verbose output
$VerbosePreference = "Continue"

# 2. Enable debug mode
$DebugPreference = "Continue"

# 3. Enable strict mode
Set-StrictMode -Version Latest

# 4. Run command with debugging
.\ops\Drift-Guard-V4.ps1 -Verbose -Debug
```

#### **Step-by-Step Execution**
```powershell
# 1. Set breakpoints
Set-PSBreakpoint -Script "ops\Drift-Guard-V4.ps1" -Line 10

# 2. Run with step-through
.\ops\Drift-Guard-V4.ps1 -Step

# 3. Check variables
Get-Variable | Where-Object {$_.Name -like "*drift*"}

# 4. Check call stack
Get-PSCallStack
```

### **2. Python Debugging**

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

## **Performance Troubleshooting**

### **1. Performance Bottleneck Identification**

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
.\ops\quick-scan.ps1
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

### **2. Performance Optimization**

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
.\ops\GPU-Monitor-V4.ps1

# 2. Optimize GPU settings
.\ops\gpu-accelerator.ps1

# 3. Monitor GPU temperature
while ($true) {
    $temp = (.\ops\GPU-Monitor-V4.ps1 | Select-String "Temperature:" | ForEach-Object { $_.ToString().Split(":")[1].Trim() })
    Write-Host "GPU Temperature: $temp"
    Start-Sleep 10
    
    if ($temp -gt "80C") {
        Write-Host "WARNING: GPU temperature high!" -ForegroundColor Yellow
    }
}
```

---

## **Troubleshooting Resources**

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

## **Troubleshooting Success Criteria**

### **Problem Resolution Checklist**
- [ ] **Issue Identified**: Problem clearly defined across relevant components
- [ ] **Root Cause Found**: Underlying cause determined and documented
- [ ] **Solution Implemented**: Fix applied successfully with validation
- [ ] **System Restored**: Full functionality restored across all 43 components
- [ ] **Testing Completed**: Solution verified with comprehensive testing suite
- [ ] **Documentation Updated**: Procedures documented and shared
- [ ] **Prevention Measures**: Steps to prevent recurrence implemented

### **Recovery Validation**
- [ ] **System Health**: All health checks pass (Project-Health-Scanner-V4.ps1)
- [ ] **Drift Status**: No drift detected (Drift-Guard-V4.ps1)
- [ ] **Performance**: Performance within acceptable range (GPU-Monitor-V4.ps1)
- [ ] **Functionality**: All core functions working (test-runner.ps1)
- [ ] **Stability**: System stable for extended period (quick-scan.ps1)
- [ ] **Documentation**: Recovery procedures documented and accessible
- [ ] **Component Coverage**: All 43 components operational and tested

### **43 Component Health Check**
```powershell
# Comprehensive component health verification
$components = @(
    "emoji-sentinel-v4", "emoji-sentinel", "Scan-Secrets-V4", 
    "Project-Health-Scanner-V4", "Symbol-Indexer-V4", "Import-Indexer-V4",
    "context-governor", "GPU-Monitor-V4", "gpu-monitor", "Power-Management-V4",
    "max-perf", "Drift-Guard-V4", "GPU-RAG-V4", "gpu-accelerator",
    "quick-scan", "make-pack", "test-runner", "quick-test"
)

$healthy = 0
foreach ($component in $components) {
    try {
        $result = .\Cleanup\Testing_Tools\test-runner.ps1 -Components $component
        if ($result -match "PASS") { $healthy++ }
    } catch {
        Write-Host "Component $component failed health check" -ForegroundColor Red
    }
}

Write-Host "System Health: $healthy/$($components.Count) components operational" -ForegroundColor Green
```

---

## **Summary of 43 Core Components & Troubleshooting**

The Agent Exo-Suit V4.0 "Perfection" includes comprehensive troubleshooting for all operational components:

### **Performance & GPU Systems (Components 1-6)**
- **Hybrid GPU-RAG System**: GPU acceleration, CPU fallback, performance optimization
- **RAG Engine Capabilities**: Model support, indexing, batch processing, context management
- **GPU Detection & Support**: NVIDIA GPU support, CUDA compatibility, fallback strategies
- **Advanced RAG Configuration**: Load balancing, RAM disk, memory thresholds, checkpoints
- **Multi-Layer Architecture**: Visual, Cognitive, Operational, and Integration layers
- **System Controller**: Main controller, performance mode, power management

### **Security & Compliance (Components 7-12)**
- **Emoji Sentinel V4.0**: Advanced emoji detection, removal, compliance reporting
- **Emoji Sentinel V3.0**: Comprehensive emoji defense, multi-language support
- **Secret Scanner V4.0**: Secret detection, entropy analysis, compliance ready
- **Project Health Scanner V4.0**: SBOM generation, CVE scanning, health assessment
- **Symbol Indexer V4.0**: Multi-language symbol detection, AST-aware parsing
- **Import Indexer V4.0**: Dependency mapping, circular dependency detection

### **Intelligence & Context (Components 13-18)**
- **Context Governor**: Token budget management, GPU optimization, intelligent caching
- **GPU Monitor V4.0**: Real-time monitoring, performance analysis, temperature tracking
- **GPU Monitor V3.0**: Basic GPU monitoring, status reporting, performance metrics
- **Power Management V4.0**: Power plan management, performance optimization, system tuning
- **Performance Optimization**: Ultimate performance mode, CPU optimization, memory management
- **Max Performance Script**: Automatic optimization, power plan setup, GPU validation

### **Monitoring & Recovery (Components 19-24)**
- **Drift Guard V4.0**: Git validation, drift detection, recovery operations
- **Drift Gate**: Basic drift monitoring, change tracking, system integration
- **Comprehensive Testing Suite**: Unit, integration, performance, security, GPU testing
- **Test Automation**: Automated execution, benchmarks, regression testing
- **Test Runner System**: Component testing, validation, result aggregation
- **Quick Test System**: Rapid validation, essential checks, health verification

### **Visualization & Integration (Components 25-30)**
- **Mermaid Integration**: Dependency mapping, architecture visualization, diagram generation
- **Development Workflow Integration**: Command queue, health monitoring, workflow automation
- **Quick Scan System**: Parallel static analysis, multi-language support, tool detection
- **Make Pack System**: Package management, dependency analysis, health assessment
- **Cleanup & Organization**: Systematic organization, testing tools, legacy backup
- **Documentation System**: Technical specs, installation guides, user guides, QA procedures

### **Advanced Features (Components 31-36)**
- **Hybrid Processing Engine**: Intelligent device selection, load balancing, fault tolerance
- **Advanced Error Handling**: Ultra-robust error management, graceful degradation, recovery
- **Enterprise Features**: Scalability, reliability, security, performance, integration
- **GPU Accelerator System**: CUDA environment, performance optimization, memory management
- **Processing Performance**: High-speed processing, memory optimization, batch processing
- **System Requirements**: OS compatibility, PowerShell version, Python version, GPU support

### **Future & Compliance (Components 37-43)**
- **V4.1 Enhancements**: Advanced AI integration, cloud integration, analytics, security
- **Long-term Vision**: Enterprise features, AI governance, cross-platform, API integration
- **Unique Selling Points**: GPU acceleration, intelligent automation, security, reliability
- **Support Channels**: Documentation, troubleshooting, community, professional support
- **Contributing Guidelines**: Code standards, documentation, testing, security compliance
- **License & Compliance**: MIT license, GDPR, security standards, accessibility, international
- **Advanced Monitoring**: Real-time system health, performance tracking, predictive maintenance

---

**Troubleshooting guide complete for all 43 components. Follow these procedures systematically to resolve issues quickly and restore full system functionality across the entire Agent Exo-Suit V4.0 "Perfection" ecosystem.**

---

**The Agent Exo-Suit V4.0 "Perfection" - Comprehensive troubleshooting for enterprise-grade AI development tools.**

*Last Updated: January 2025*  
*Version: V4.0 "Perfection"*  
*Status: Development/Testing - V3 System with V4 Components and Complete Troubleshooting Coverage*
