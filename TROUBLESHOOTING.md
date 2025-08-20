# 🔧 Agent Exo-Suit V5.0 Troubleshooting Guide

## 🎯 **Quick Start Troubleshooting**

### **System Won't Start**
1. **Check Python Version**: Ensure Python 3.8+ is installed
2. **Verify Dependencies**: Run `pip install -r requirements.txt`
3. **Check GPU Drivers**: Ensure NVIDIA drivers are up to date
4. **Verify File Permissions**: Ensure you have read/write access

### **Performance Issues**
1. **Check GPU Usage**: Monitor with `nvidia-smi`
2. **Verify Memory**: Ensure sufficient RAM (16GB+ recommended)
3. **Check Disk Space**: Ensure adequate free space
4. **Monitor CPU Usage**: Check for background processes

---

## 🚨 **Common Error Messages & Solutions**

### **"Module Not Found" Errors**

#### **Error**: `ModuleNotFoundError: No module named 'torch'`
**Solution**: Install PyTorch
```bash
pip install torch torchvision torchaudio
```

#### **Error**: `ModuleNotFoundError: No module named 'transformers'`
**Solution**: Install Transformers
```bash
pip install transformers
```

#### **Error**: `ModuleNotFoundError: No module named 'numpy'`
**Solution**: Install NumPy
```bash
pip install numpy
```

### **GPU-Related Errors**

#### **Error**: `CUDA out of memory`
**Solutions**:
1. **Reduce batch size** in configuration
2. **Close other GPU applications**
3. **Restart the system**
4. **Check GPU memory usage**: `nvidia-smi`

#### **Error**: `CUDA driver version is insufficient`
**Solution**: Update NVIDIA drivers
```bash
# Windows: Download from NVIDIA website
# Linux: sudo apt update && sudo apt upgrade nvidia-driver
```

#### **Error**: `No CUDA-capable device found`
**Solutions**:
1. **Verify GPU installation**: `nvidia-smi`
2. **Check CUDA installation**: `nvcc --version`
3. **Install CUDA toolkit** if missing

### **Permission Errors**

#### **Error**: `Permission denied: [file_path]`
**Solutions**:
1. **Run as administrator** (Windows)
2. **Use sudo** (Linux/Mac)
3. **Check file permissions**: `ls -la [file_path]`
4. **Change ownership**: `chown [user] [file_path]`

#### **Error**: `Access denied to [directory]`
**Solutions**:
1. **Check directory permissions**
2. **Verify user access rights**
3. **Use absolute paths**
4. **Run with elevated privileges**

---

## 🔍 **Performance Troubleshooting**

### **Slow Compression Performance**

#### **Symptoms**:
- Compression taking longer than expected
- Low files per second processing
- High CPU/GPU usage

#### **Diagnostic Steps**:
1. **Check system resources**:
   ```bash
   # CPU usage
   top
   
   # Memory usage
   free -h
   
   # GPU usage
   nvidia-smi
   ```

2. **Verify file sizes**:
   ```bash
   # Check file sizes
   ls -lh [file_path]
   
   # Monitor processing
   tail -f [log_file]
   ```

3. **Check compression strategy**:
   ```python
   # Verify strategy selection
   from mmh_rs_codecs import analyze_patterns
   result = analyze_patterns("file_path")
   print(f"Recommended strategy: {result['recommended_strategy']}")
   ```

#### **Solutions**:
1. **Use appropriate compression strategy**:
   - **Neural**: Best for complex patterns
   - **Pattern**: Best for repetitive content
   - **Hybrid**: Best for mixed content
   - **Auto**: Let system choose

2. **Optimize system resources**:
   - Close unnecessary applications
   - Ensure adequate cooling
   - Check for background processes

3. **Update configuration**:
   ```python
   # Optimize for performance
   config = {
       "batch_size": 64,
       "gpu_memory_fraction": 0.8,
       "compression_strategy": "auto"
   }
   ```

### **Memory Issues**

#### **Symptoms**:
- Out of memory errors
- System slowdowns
- Application crashes

#### **Diagnostic Steps**:
1. **Check memory usage**:
   ```bash
   # Linux/Mac
   free -h
   
   # Windows
   tasklist /fi "imagename eq python.exe"
   ```

2. **Monitor memory allocation**:
   ```python
   import psutil
   process = psutil.Process()
   print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
   ```

#### **Solutions**:
1. **Reduce batch sizes**
2. **Use memory-efficient strategies**
3. **Close other applications**
4. **Restart the system**

---

## 🛡️ **Security Troubleshooting**

### **Localhost Access Issues**

#### **Error**: `Connection refused on localhost`
**Solutions**:
1. **Check if service is running**:
   ```bash
   # Check port usage
   netstat -an | grep 8000
   
   # Check process
   ps aux | grep python
   ```

2. **Verify firewall settings**:
   ```bash
   # Windows: Check Windows Defender
   # Linux: sudo ufw status
   # Mac: System Preferences > Security & Privacy
   ```

3. **Check service configuration**:
   ```python
   # Ensure localhost binding
   app.run(host='127.0.0.1', port=8000)
   ```

### **Authentication Issues**

#### **Error**: `Invalid API key`
**Solutions**:
1. **Check API key format**:
   ```bash
   # Verify key in headers
   Authorization: Bearer YOUR_API_KEY
   ```

2. **Regenerate API key** if needed
3. **Check key permissions**
4. **Verify key expiration**

---

## 🔧 **System-Specific Troubleshooting**

### **Windows Issues**

#### **PowerShell Execution Policy**
**Error**: `Execution policy prevents running scripts`
**Solution**:
```powershell
# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or for specific script
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

#### **Path Issues**
**Error**: `'python' is not recognized`
**Solutions**:
1. **Add Python to PATH**:
   - System Properties > Environment Variables
   - Add Python installation directory to PATH

2. **Use full path**:
   ```cmd
   C:\Python39\python.exe script.py
   ```

3. **Use py launcher**:
   ```cmd
   py script.py
   ```

### **Linux Issues**

#### **Package Dependencies**
**Error**: `Shared library not found`
**Solutions**:
```bash
# Install missing libraries
sudo apt-get update
sudo apt-get install libcudnn8 libcudnn8-dev

# Check library paths
ldconfig -p | grep cuda
```

#### **Permission Issues**
**Error**: `Permission denied`
**Solutions**:
```bash
# Make script executable
chmod +x script.py

# Run with sudo if needed
sudo python3 script.py
```

### **macOS Issues**

#### **Homebrew Dependencies**
**Error**: `Library not found`
**Solutions**:
```bash
# Install dependencies
brew install cuda

# Update PATH
echo 'export PATH="/usr/local/cuda/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

---

## 📊 **Diagnostic Tools**

### **System Health Check**
```python
from ops.SYSTEM_HEALTH_VALIDATOR import SystemHealthValidator

# Run comprehensive health check
validator = SystemHealthValidator()
health_report = validator.run_full_health_check()
print(health_report)
```

### **Performance Monitoring**
```python
from ops.VISIONGAP_ENGINE import VisionGapEngine

# Monitor system performance
engine = VisionGapEngine()
metrics = engine.get_performance_metrics()
print(f"Files per second: {metrics['files_per_second']}")
```

### **Log Analysis**
```bash
# Check recent logs
tail -n 100 logs/system.log

# Search for errors
grep -i "error\|exception\|fail" logs/system.log

# Monitor real-time logs
tail -f logs/system.log
```

---

## 🚀 **Performance Optimization**

### **GPU Optimization**
1. **Monitor GPU usage**: `nvidia-smi -l 1`
2. **Optimize memory allocation**:
   ```python
   import torch
   torch.cuda.empty_cache()
   ```
3. **Use appropriate batch sizes**
4. **Enable mixed precision** if supported

### **Memory Optimization**
1. **Use generators** for large datasets
2. **Implement lazy loading**
3. **Clear unused variables**
4. **Use memory-efficient data structures**

### **CPU Optimization**
1. **Use multiprocessing** for CPU-intensive tasks
2. **Optimize algorithms** and data structures
3. **Profile code** to identify bottlenecks
4. **Use appropriate data types**

---

## 📞 **Getting Help**

### **Self-Service Resources**
1. **Documentation**: Check this guide and other docs
2. **Logs**: Review system logs for error details
3. **Configuration**: Verify settings and parameters
4. **System Requirements**: Ensure minimum requirements met

### **Community Support**
1. **GitHub Issues**: Report bugs and request features
2. **Discussions**: Ask questions and share solutions
3. **Documentation**: Contribute improvements
4. **Code Examples**: Share working solutions

### **Escalation Process**
1. **Document the issue** with logs and steps
2. **Check known issues** in documentation
3. **Search existing solutions** in community
4. **Create detailed issue report** if needed

---

## 📋 **Troubleshooting Checklist**

### **Before Starting**
- [ ] System meets minimum requirements
- [ ] All dependencies installed
- [ ] GPU drivers up to date
- [ ] Sufficient disk space
- [ ] Proper permissions

### **When Issues Occur**
- [ ] Check error messages carefully
- [ ] Review system logs
- [ ] Verify configuration settings
- [ ] Test with simple examples
- [ ] Check system resources

### **After Resolution**
- [ ] Document the solution
- [ ] Update configuration if needed
- [ ] Test similar scenarios
- [ ] Share solution with community
- [ ] Prevent future occurrences

---

## 🎯 **Next Steps**

1. **Use this guide** for common issues
2. **Check system logs** for detailed error information
3. **Verify configuration** matches requirements
4. **Test with simple examples** to isolate issues
5. **Seek community help** for complex problems

---

**Troubleshooting Guide Created**: August 20, 2025  
**Status**: Phase 2 Implementation 🚀  
**Target**: 100% World Release Ready 🏆
