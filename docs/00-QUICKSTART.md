# 🚀 Quick Start Guide - Agent Exo-Suit V5.0

**Get up and running in under 2 minutes with this simple guide.**

---

## 📋 **What You'll Get**

- ✅ **Local AI agent platform** running on your machine
- ✅ **26 operational tools** ready for immediate use
- ✅ **Web interface** accessible at `http://127.0.0.1:8001`
- ✅ **Maximum security** with localhost-only access
- ✅ **MMH-RS compression** with GPU acceleration

---

## 🔧 **Step 1: System Check**

**Verify you have the minimum requirements:**

```bash
# Check Python version (3.8+ required)
python --version

# Check PowerShell version (7.0+ on Windows)
pwsh --version

# Check available memory (16GB+ recommended)
# Windows: Check Task Manager
# macOS/Linux: free -h
```

**✅ If all checks pass, continue to Step 2**

---

## 📥 **Step 2: Download & Setup**

```bash
# Clone the repository
git clone https://github.com/Bigrob7605/Exo-Suit.git

# Navigate to the project directory
cd Exo-Suit

# Install Python dependencies
pip install -r requirements.txt
```

**✅ Repository downloaded and dependencies installed**

---

## 🚀 **Step 3: Start the System**

```bash
# Start the local server with maximum security
python local-security-config.py

# The system will start and show:
# - Security configuration status
# - Server startup information
# - Access URL (http://127.0.0.1:8001)
```

**✅ System is now running and secure**

---

## 🌐 **Step 4: Access the Web Interface**

1. **Open your browser**
2. **Navigate to**: `http://127.0.0.1:8001`
3. **You'll see**: The Agent Exo-Suit V5.0 dashboard
4. **Available sections**:
   - **Tools**: 26 operational tools ready to use
   - **Performance**: Real-time metrics and status
   - **Security**: Security configuration and status
   - **Documentation**: Comprehensive guides and references

**✅ Web interface is accessible and functional**

---

## 🛠️ **Step 5: Try Your First Tool**

**Test the system with a simple operation:**

```bash
# In a new terminal, test the system health checker
python ops/System_Health_Checker_V5.py

# This will show:
# - System status
# - Available resources
# - Tool health
# - Security status
```

**✅ First tool successfully executed**

---

## 🎯 **What's Next?**

### **Immediate Actions**
- **Explore the web interface** at `http://127.0.0.1:8001`
- **Try different tools** from the 26 available options
- **Check the documentation** for detailed usage instructions

### **Common Use Cases**
- **Code Security**: Scan your projects for vulnerabilities
- **File Compression**: Use MMH-RS compression on large datasets
- **AI Development**: Build and test AI agent workflows
- **Performance Monitoring**: Track system performance and optimization

### **Getting Help**
- **Documentation**: Comprehensive guides in the `docs/` folder
- **Tool Examples**: See `ops/` folder for all available tools
- **System Status**: Check `V5_SYSTEM_STATUS.md` for current status

---

## 🚨 **Troubleshooting**

### **Common Issues**

**Port already in use:**
```bash
# Use a different port
python local-security-config.py --port 8002
```

**Python dependencies missing:**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

**Permission denied:**
```bash
# On Windows, run PowerShell as Administrator
# On macOS/Linux, check file permissions
```

### **Still Having Issues?**

1. **Check the logs** in the terminal where you started the server
2. **Verify system requirements** match the minimum specifications
3. **Check the troubleshooting guide** in `docs/04-OPERATIONS/troubleshooting.md`

---

## 🎉 **You're Ready!**

**Agent Exo-Suit V5.0 is now running on your machine with:**
- ✅ **26 operational tools** ready for immediate use
- ✅ **Maximum security** protecting your system
- ✅ **Web interface** accessible and functional
- ✅ **Real compression technology** with GPU acceleration

**Start building AI agents, securing codebases, and optimizing performance!**

---

**Need more help?** Check the [main documentation](../README.md) or explore the [tools directory](../ops/).
