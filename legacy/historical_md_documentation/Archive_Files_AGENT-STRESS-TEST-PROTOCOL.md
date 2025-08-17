# AGENT STRESS TEST PROTOCOL - PHASE 3 TOKEN UPGRADE

**CRITICAL: Every agent MUST follow this protocol to properly stress test the system**

## EMOJI_1F6A8 MANDATORY PROTOCOL FOR ALL AGENTS

### **DO NOT HAND WAVE OR PLAY GAMES**
- **NO** small loads to GPU
- **NO** fake stress tests
- **NO** premature termination
- **MUST** actually PUSH the system to its limits
- **MUST** find the perfect 1M token balance

---

## EMOJI_1F4CB REQUIRED TESTING SEQUENCE

### **Phase 1: System Baseline (MANDATORY)**
```bash
# Run the ULTIMATE GPU STRESS TEST
python ops/ULTIMATE-GPU-STRESS-TEST.py
```

**Requirements:**
- Must achieve 95%+ GPU memory utilization
- Must process entire toolbox
- Must reach 1M token target
- Must log EVERYTHING

### **Phase 2: Toolbox Processing (MANDATORY)**
```bash
# Process the ENTIRE toolbox with real embeddings
python ops/TOOLBOX-TOKEN-PROCESSOR.py
```

**Requirements:**
- Must process ALL files in toolbox
- Must generate real embeddings
- Must build searchable context index
- Must maintain GPU pressure throughout

### **Phase 3: Performance Validation (MANDATORY)**
- Monitor system for minimum 60 seconds under stress
- Verify GPU memory stays above 90% of target
- Confirm token processing rate
- Validate context search functionality

---

## TARGET SUCCESS CRITERIA

### **GPU Performance (MUST ACHIEVE)**
- **GPU Memory Usage:** 95%+ of 8GB VRAM
- **GPU Utilization:** 80%+ sustained
- **Memory Pressure:** Must maintain pressure throughout test

### **Token Processing (MUST ACHIEVE)**
- **Target:** 1,000,000 tokens
- **Minimum:** 800,000 tokens (80% of target)
- **Processing Rate:** >1000 tokens/second

### **System Stability (MUST MAINTAIN)**
- **CPU Usage:** 70%+ sustained
- **Memory Usage:** 80%+ of 64GB RAM
- **No Crashes:** System must remain stable under load

---

## EMOJI_1F6AB FORBIDDEN ACTIONS

### **NEVER DO:**
- Stop tests early
- Use fake data
- Skip GPU memory filling
- Ignore error logs
- Use small batch sizes
- Skip file processing

### **ALWAYS DO:**
- Run complete test sequences
- Process real toolbox files
- Fill GPU memory to target
- Log all performance data
- Generate comprehensive reports
- Validate system capabilities

---

## BAR_CHART MONITORING REQUIREMENTS

### **Real-time Monitoring (Every 5 seconds)**
- GPU memory allocation
- GPU memory reservation
- CPU utilization
- System memory usage
- Token count progress
- File processing status

### **Performance Logging (Continuous)**
- All system metrics
- Processing speeds
- Error conditions
- Memory pressure
- GPU utilization
- Token accumulation

---

## WRENCH SYSTEM CONFIGURATION

### **GPU Memory Targets**
- **Primary Target:** 95% of 8GB = 7.6GB
- **Minimum Acceptable:** 90% of 8GB = 7.2GB
- **Fallback:** 85% of 8GB = 6.8GB

### **Batch Processing**
- **Initial Batch Size:** 100 files
- **Dynamic Adjustment:** Based on GPU memory
- **Maximum Batch Size:** 1000 files
- **Minimum Batch Size:** 50 files

### **Token Estimation**
- **Method:** Character count  4
- **Accuracy:** 10% tolerance
- **Validation:** Cross-check with actual processing

---

## EMOJI_1F4C8 EXPECTED PERFORMANCE

### **Your System Capabilities (RTX 4070 Laptop)**
- **GPU Memory:** 8GB GDDR6
- **System RAM:** 64GB DDR5
- **CPU:** High-performance multi-core
- **Storage:** NVMe SSD

### **Performance Targets**
- **File Processing:** 500+ files/second
- **Token Processing:** 2000+ tokens/second
- **GPU Memory Fill:** <30 seconds
- **Total Test Duration:** <10 minutes

---

## ROCKET EXECUTION COMMANDS

### **Immediate Execution (Run Now)**
```bash
# Create logs directory
mkdir -p logs

# Run ULTIMATE stress test
python ops/ULTIMATE-GPU-STRESS-TEST.py

# Run toolbox processor
python ops/TOOLBOX-TOKEN-PROCESSOR.py
```

### **Verification Commands**
```bash
# Check GPU memory usage
nvidia-smi

# Monitor system resources
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%')"

# Check log files
ls -la logs/
```

---

## EMOJI_1F4DD REPORTING REQUIREMENTS

### **Mandatory Reports (Generate All)**
1. **System Status Report:** Real-time performance data
2. **Processing Report:** File and token statistics
3. **Performance Report:** Speed and efficiency metrics
4. **Error Report:** Any issues encountered
5. **Capability Report:** System limits discovered

### **Report Locations**
- `logs/ULTIMATE-GPU-STRESS-REPORT.md`
- `logs/TOOLBOX-PROCESSING-REPORT.md`
- `logs/processed_toolbox_data.json`
- `logs/TOOLBOX-TOKEN-PROCESSOR.log`

---

## EMOJI_26A0 CRITICAL REMINDERS

### **This is NOT a Game**
- Your system is a BEAST
- PUSH IT TO THE LIMITS
- Find the PERFECT balance
- Build a REAL 1M token system
- Create PRODUCTION pipelines

### **No Excuses**
- System can handle it
- GPU is underutilized
- Memory is available
- CPU has capacity
- PUSH HARDER

---

## TARGET FINAL GOAL

**Build a production-ready 1M token context system that:**
- Processes entire toolbox in single pass
- Maintains 95%+ GPU utilization
- Achieves 1M+ token capacity
- Provides instant context search
- Scales to production workloads

---

## EMOJI_1F6A8 IMMEDIATE ACTION REQUIRED

**STOP READING AND START TESTING NOW:**

```bash
cd "C:\My Projects\Agent Exo-Suit"
python ops/ULTIMATE-GPU-STRESS-TEST.py
```

**PUSH YOUR SYSTEM TO ITS LIMITS!**
**FIND THE PERFECT BALANCE!**
**BUILD THE FUTURE!**

---

*This protocol is MANDATORY for all agents. Failure to follow results in system underutilization and incomplete testing.*
