# 📖 USER_GUIDE.md - Agent Exo-Suit V3.0 Daily Operations

**Document Type:** User Guide & Daily Operations  
**Version:** V3.0 "Monster-Mode"  
**Last Updated:** January 2025  
**Target Audience:** Developers, DevOps engineers, system administrators

---

## 🎯 **User Guide Overview**

This guide covers the **daily operations and practical usage** of the Agent Exo-Suit V3.0 system. Learn how to use the system effectively, understand common workflows, and master the command-line interface for maximum productivity.

---

## 🚀 **Getting Started - First Time Setup**

### **Quick First Run**
```powershell
# 1. Navigate to project directory
cd "C:\My Projects\Agent Exo-Suit"

# 2. Activate virtual environment (if using Python features)
gpu_rag_env\Scripts\activate

# 3. Run full system activation
.\go-big.ps1

# 4. Verify system health
.\ops\drift-gate.ps1
```

### **Expected First Run Output**
```
🔥 Exo-Suit armed. Open Cursor and follow COMMAND_QUEUE.md
[20:26:42] Building context package...
[20:26:45] Context package complete
[20:26:46] No drift detected
[20:26:47] System health: EXCELLENT
```

---

## 📋 **Daily Operations Workflow**

### **Morning Startup Routine**
```powershell
# 1. Check system status
.\ops\drift-gate.ps1

# 2. Run health scan
.\ops\placeholder-scan.ps1

# 3. Activate performance mode (if needed)
.\AgentExoSuitV3.ps1

# 4. Check GPU status (if available)
.\ops\gpu-monitor.ps1
```

### **Development Workflow**
```powershell
# 1. Start development session
.\go-big.ps1

# 2. Monitor for drift during development
.\ops\drift-gate.ps1 -json

# 3. Check health before commits
.\ops\placeholder-scan.ps1

# 4. Generate context for large changes
.\ops\make-pack.ps1 "C:\My Projects\Agent Exo-Suit" "C:\My Projects\Agent Exo-Suit\context\_latest"
```

### **End-of-Day Routine**
```powershell
# 1. Final drift check
.\ops\drift-gate.ps1

# 2. Health summary
.\ops\Project-Health-Scanner.ps1 "C:\My Projects\Agent Exo-Suit" "C:\My Projects\Agent Exo-Suit\context\_latest"

# 3. Restore normal performance (if needed)
.\AgentExoSuitV3.ps1 -Restore
```

---

## ⚡ **Essential Commands Reference**

### **🚀 System Activation Commands**

#### **Full System Activation**
```powershell
.\go-big.ps1                    # Complete system activation
.\go-big.ps1 -skipTests         # Skip test execution
```

**What it does:**
- Activates Ultimate Performance power plan
- Creates RAM-disk scratch directory
- Builds context package
- Runs RAG brain initialization
- Executes lint swarm
- Generates diagrams
- Runs sentinel pack

#### **Performance Mode Commands**
```powershell
.\AgentExoSuitV3.ps1            # Activate performance mode
.\AgentExoSuitV3.ps1 -Restore   # Restore normal settings
.\AgentExoSuitV3.ps1 -SkipGpu   # Skip GPU operations
```

**What it does:**
- Activates Ultimate Performance power plan
- Optimizes registry settings
- Configures network adapters
- Manages GPU settings
- Creates scratch directories

### **🔍 Monitoring & Health Commands**

#### **Drift Detection**
```powershell
.\ops\drift-gate.ps1            # Basic drift check
.\ops\drift-gate.ps1 -json      # JSON output for automation
```

**Output Examples:**
```
No drift detected.                    # Clean state
UNCOMMITTED: M README.md             # Modified file
UNTRACKED: new_file.txt              # New untracked file
```

#### **Health Scanning**
```powershell
.\ops\placeholder-scan.ps1           # Quick health scan
.\ops\Project-Health-Scanner.ps1 "C:\My Projects\Agent Exo-Suit" "C:\My Projects\Agent Exo-Suit\context\_latest"
```

**Output Examples:**
```
SCAN COMPLETE
5 BLOCK | 2 WARN | 6 INFO

Sev File                        Line Text
--- ----                        ---- ----
B   README.md                     77 - TODO: Update examples
W   config.py                    42 - FIXME: Add validation
I   utils.py                     15 - NOTE: Performance optimization
```

#### **GPU Monitoring**
```powershell
.\ops\gpu-monitor.ps1              # Real-time GPU status
.\ops\gpu-accelerator.ps1          # GPU optimization
```

**Output Examples:**
```
GPU: NVIDIA RTX 4070
Memory: 8.0 GB / 12.0 GB (67%)
Utilization: 45%
Temperature: 68°C
Power: 180W / 200W
```

### **🧠 RAG & Context Commands**

#### **Context Management**
```powershell
.\ops\make-pack.ps1 "C:\My Projects\Agent Exo-Suit" "C:\My Projects\Agent Exo-Suit\context\_latest"
.\ops\context-governor.ps1 -maxTokens 128000
```

**What it generates:**
- `ownership.json` - File ownership mapping
- `lock_age.json` - Dependency freshness
- `placeholders.json` - Development markers
- `symbols.json` - Symbol index (if ripgrep available)

#### **RAG Operations**
```powershell
.\rag\embed.ps1                    # Build FAISS index
python rag\retrieve.py "query"     # Search context
```

**Output Examples:**
```
Building FAISS index...
Documents indexed: 1,247
Index size: 1.2 GB
Query: "authentication system"
Results: 5 relevant documents found
```

### **🎨 Visualization Commands**

#### **Diagram Generation**
```powershell
.\mermaid\generate-maps.ps1        # Generate all diagrams
python mermaid\dep2mmd.py          # Convert dependencies to Mermaid
```

**Generated Files:**
- `dependency-map.md` - Project dependency visualization
- `architecture.md` - System architecture diagram
- `flow-diagram.md` - Data flow visualization

---

## 🔄 **Common Workflows & Use Cases**

### **🆕 New Project Setup**

#### **Scenario**: Setting up Agent Exo-Suit for a new project
```powershell
# 1. Clone or download Agent Exo-Suit
git clone https://github.com/your-org/agent-exo-suit.git new-project
cd new-project

# 2. Configure project-specific settings
Edit-Item ".env"
# Add: PROJECT_NAME="New Project"
# Add: PROJECT_PATH="C:\path\to\new-project"

# 3. Set up ownership mapping
Edit-Item "OWNERS.md"
# Add project-specific ownership rules

# 4. Run initial setup
.\go-big.ps1

# 5. Verify setup
.\ops\drift-gate.ps1
.\ops\placeholder-scan.ps1
```

### **🐛 Debugging & Troubleshooting**

#### **Scenario**: System is running slowly or showing errors
```powershell
# 1. Check system health
.\ops\Project-Health-Scanner.ps1 "C:\My Projects\Agent Exo-Suit" "C:\My Projects\Agent Exo-Suit\context\_latest"

# 2. Check for drift
.\ops\drift-gate.ps1 -json

# 3. Monitor resource usage
.\ops\gpu-monitor.ps1
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10

# 4. Check logs
Get-Content "context\_latest\*.log" -Tail 50

# 5. Restart system if needed
.\go-big.ps1
```

### **📊 Performance Optimization**

#### **Scenario**: Need maximum performance for intensive development
```powershell
# 1. Activate performance mode
.\AgentExoSuitV3.ps1

# 2. Verify performance settings
powercfg -list
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl" -Name "Win32PrioritySeparation"

# 3. Monitor performance
.\ops\gpu-monitor.ps1
Get-Counter "\Processor(_Total)\% Processor Time" -SampleInterval 1 -MaxSamples 10

# 4. Run intensive operations
.\go-big.ps1

# 5. Restore normal settings when done
.\AgentExoSuitV3.ps1 -Restore
```

### **🔍 Code Quality & Review**

#### **Scenario**: Preparing code for review or deployment
```powershell
# 1. Check for blocking issues
.\ops\placeholder-scan.ps1

# 2. Run quality checks
.\ops\quick-scan.ps1

# 3. Generate context for reviewers
.\ops\make-pack.ps1 "C:\My Projects\Agent Exo-Suit" "C:\My Projects\Agent Exo-Suit\context\_latest"

# 4. Check drift status
.\ops\drift-gate.ps1

# 5. Generate documentation
.\mermaid\generate-maps.ps1
```

---

## 📊 **Understanding Output & Reports**

### **📈 Health Scan Results**

#### **Severity Levels**
```
B (BLOCK)   - Critical issues requiring immediate attention
W (WARN)    - Important issues needing review
I (INFO)    - Informational items for tracking
```

#### **Example Health Report**
```
SCAN COMPLETE
5 BLOCK | 2 WARN | 6 INFO

Sev File                        Line Text
--- ----                        ---- ----
B   AGENT_EXO_SUIT_STATUS.md      77 - `archive/FINAL_ISSUE_RESOLUTION_SUMMARY.md` - Hardcoded responses
B   EXO_SUIT_V2_TEST_RESULTS.md   43 - **HARDCODED responses** in WSGI server
W   EXO_SUIT_V2_TEST_RESULTS.md   49 - **STUB implementations** in recovery documentation
I   README.md                    109 "Pattern": "TODO"
```

**Interpretation:**
- **5 BLOCK items**: Historical documentation issues (expected)
- **2 WARN items**: Development markers needing review
- **6 INFO items**: Tracking items for monitoring

### **📊 Drift Detection Reports**

#### **Drift Status Types**
```
No drift detected.              # Clean state - no action needed
UNCOMMITTED: M file.txt        # Modified file - review changes
UNTRACKED: new_file.txt        # New file - decide to track or ignore
DELETED: old_file.txt          # Deleted file - verify intentional
```

#### **Example Drift Report**
```
UNCOMMITTED:  M README.md
UNCOMMITTED:  M ops/placeholder-scan.ps1
UNTRACKED: AgentExoSuitV3.ps1
UNTRACKED: ops/Exo-Suit-Normal.ps1
```

**Action Required:**
- **Modified files**: Review changes, commit if appropriate
- **Untracked files**: Decide to add to git or add to .gitignore
- **Deleted files**: Verify deletion was intentional

### **🎯 Context Package Contents**

#### **Generated Files**
```
context/_latest/
├── ownership.json              # File ownership mapping
├── lock_age.json              # Dependency freshness
├── placeholders.json           # Development markers
├── symbols.json               # Symbol index (if ripgrep available)
└── imports.json               # Import tracking (if ripgrep available)
```

#### **Example ownership.json**
```json
[
  {
    "Path": "ops/",
    "Owner": "AI"
  },
  {
    "Path": "docs/",
    "Owner": "Rob"
  },
  {
    "Path": "web_interface/",
    "Owner": "AI"
  }
]
```

---

## 🔧 **Configuration & Customization**

### **⚙️ Environment Variables**

#### **Performance Configuration**
```bash
# .env file
CACHE_DRIVE=C:                    # Cache directory location
GPU_MODE=true                     # Enable GPU acceleration
MAX_TOKENS=128000                # Context token limit
PERFORMANCE_MODE=ultimate         # Power plan setting
```

#### **RAG Configuration**
```bash
# .env file
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Embedding model
FAISS_INDEX_TYPE=IVF100,SQ8       # FAISS index type
VECTOR_DIMENSION=384              # Vector dimensions
```

### **📝 Ownership Configuration**

#### **OWNERS.md Format**
```markdown
# Project Ownership

## File Ownership

* ops/                    | AI
* cursor/                 | AI
* docs/                   | Rob
* web_interface/          | AI
* tests/                  | AI
* validation/             | AI
```

#### **Customization Options**
- **Path patterns**: Use glob patterns for directory matching
- **Owner names**: Any text identifier for ownership
- **Multiple owners**: Use comma-separated lists
- **Exclusions**: Use `!` prefix for excluded paths

### **🔍 Pattern Customization**

#### **Custom Placeholder Patterns**
```powershell
# Edit ops/placeholder-scan.ps1
$patterns = @{
    'BLOCK' = @('CRITICAL:', 'BLOCKER:', 'STOP:')
    'WARN'  = @('WARNING:', 'ATTENTION:', 'REVIEW:')
    'INFO'  = @('NOTE:', 'INFO:', 'HINT:')
}
```

#### **File Exclusions**
```powershell
# Edit ops/placeholder-scan.ps1
$excludePatterns = @(
    '*.log',
    '*.tmp',
    'node_modules/*',
    '.git/*',
    'gpu_rag_env/*'
)
```

---

## 🚨 **Emergency Procedures**

### **🆘 System Recovery**

#### **Scenario**: System is unresponsive or corrupted
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

#### **Scenario**: GPU issues or overheating
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

### **🔄 Data Recovery**

#### **Scenario**: Context files corrupted or missing
```powershell
# 1. Check backup files
Get-ChildItem "restore\*" -Recurse | Sort-Object LastWriteTime -Descending

# 2. Restore from backup
Copy-Item "restore\DRIFT_REPORT.json" "context\_latest\"
Copy-Item "restore\health_scan\*" "context\_latest\"

# 3. Regenerate context
.\ops\make-pack.ps1 "C:\My Projects\Agent Exo-Suit" "C:\My Projects\Agent Exo-Suit\context\_latest"

# 4. Verify recovery
.\ops\drift-gate.ps1
.\ops\placeholder-scan.ps1
```

---

## 📚 **Advanced Usage Patterns**

### **🔗 Integration with Other Tools**

#### **Cursor Integration**
```powershell
# Copy command queue to Cursor
Copy-Item "cursor\COMMAND_QUEUE.md" "$env:USERPROFILE\.cursor\"

# Set up Cursor profile
@"
# Agent Exo-Suit V3.0 Integration
Set-Location "C:\My Projects\Agent Exo-Suit"
Import-Module "C:\My Projects\Agent Exo-Suit\ops\Exo-Suit-Normal.ps1"
"@ | Out-File -FilePath "$env:USERPROFILE\.cursor\profile.ps1" -Encoding UTF8
```

#### **VS Code Integration**
```powershell
# Install PowerShell extension
code --install-extension ms-vscode.powershell

# Set up VS Code tasks
@"
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Exo-Suit Health Check",
            "type": "shell",
            "command": "powershell",
            "args": [".\\ops\\drift-gate.ps1"],
            "group": "build"
        }
    ]
}
"@ | Out-File -FilePath ".vscode\tasks.json" -Encoding UTF8
```

### **🤖 Automation & Scripting**

#### **Scheduled Health Checks**
```powershell
# Create scheduled task for hourly health checks
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File 'C:\My Projects\Agent Exo-Suit\ops\drift-gate.ps1'"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)
Register-ScheduledTask -TaskName "Exo-Suit Health Check" -Action $action -Trigger $trigger
```

#### **CI/CD Integration**
```yaml
# GitHub Actions example
- name: Exo-Suit Health Check
  run: |
    .\ops\drift-gate.ps1
    if (Test-Path "restore\DRIFT_REPORT.json") {
      echo "Drift detected!"
      exit 1
    }
```

---

## 📊 **Performance Monitoring & Optimization**

### **📈 Performance Metrics**

#### **Key Performance Indicators**
```powershell
# Monitor system performance
Get-Counter "\Processor(_Total)\% Processor Time", "\Memory\Available MBytes", "\PhysicalDisk(_Total)\% Disk Time" -SampleInterval 5 -MaxSamples 12

# Monitor GPU performance
.\ops\gpu-monitor.ps1

# Monitor memory usage
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10 ProcessName, WorkingSet, CPU
```

#### **Performance Benchmarks**
```powershell
# Run performance benchmark
Measure-Command { .\ops\placeholder-scan.ps1 }

# Compare with baseline
$baseline = 2.5  # seconds
$current = (Measure-Command { .\ops\placeholder-scan.ps1 }).TotalSeconds
$improvement = (($baseline - $current) / $baseline) * 100
Write-Host "Performance improvement: $([math]::Round($improvement, 1))%"
```

### **🔧 Performance Tuning**

#### **Memory Optimization**
```powershell
# Adjust token limits for memory constraints
$env:MAX_TOKENS = "64000"

# Monitor memory usage
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Select-Object ProcessName, WorkingSet, CPU
```

#### **GPU Optimization**
```powershell
# Optimize GPU settings
.\ops\gpu-accelerator.ps1

# Monitor GPU utilization
while ($true) {
    .\ops\gpu-monitor.ps1
    Start-Sleep 5
    Clear-Host
}
```

---

## 📞 **Getting Help & Support**

### **🔍 Self-Help Resources**

#### **Check System Status**
```powershell
# 1. System health
.\ops\Project-Health-Scanner.ps1 "C:\My Projects\Agent Exo-Suit" "C:\My Projects\Agent Exo-Suit\context\_latest"

# 2. Drift status
.\ops\drift-gate.ps1

# 3. Log files
Get-ChildItem "context\_latest\*.log" -ErrorAction SilentlyContinue | Get-Content -Tail 100
```

#### **Review Documentation**
- **[INSTALLATION.md](INSTALLATION.md)** - Setup and configuration
- **[TECHNICAL_SPECS.md](TECHNICAL_SPECS.md)** - System architecture
- **[QA_TESTING.md](QA_TESTING.md)** - Testing procedures
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Problem resolution

### **🚨 Common Issues & Solutions**

#### **PowerShell Execution Policy**
```powershell
# Error: Cannot run script due to execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **Permission Denied**
```powershell
# Error: Access denied
Start-Process PowerShell -Verb RunAs
```

#### **GPU Not Detected**
```powershell
# Check CUDA installation
python -c "import torch; print(torch.cuda.is_available())"

# Verify GPU drivers
nvidia-smi
```

---

## 🎯 **Best Practices & Tips**

### **💡 Daily Operations Tips**

1. **Start with health check**: Always verify system health before intensive work
2. **Monitor drift**: Check for drift after major changes
3. **Use performance mode**: Activate performance mode for intensive development
4. **Regular maintenance**: Run full scans weekly
5. **Backup context**: Keep context files backed up

### **🚀 Performance Tips**

1. **GPU acceleration**: Always use GPU mode when available
2. **Parallel processing**: Use parallel workers for large codebases
3. **Caching**: Leverage scratch directories for temporary files
4. **Resource monitoring**: Monitor system resources during heavy operations
5. **Optimization**: Use performance mode for intensive tasks

### **🛡️ Safety Tips**

1. **Backup before changes**: Always backup before major modifications
2. **Test in isolation**: Test new configurations in isolated environments
3. **Monitor logs**: Regularly check log files for issues
4. **Gradual changes**: Make changes incrementally to identify issues
5. **Rollback plan**: Always have a rollback strategy

---

**📖 User guide complete! You're now ready to use the Agent Exo-Suit V3.0 effectively for daily development operations.**
