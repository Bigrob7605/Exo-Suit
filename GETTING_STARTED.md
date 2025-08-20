# 🚀 Getting Started - Agent Exo-Suit V5.0

**Simple, focused guide to get you up and running in minutes.**

---

## 🎯 **What You're Getting**

**Agent Exo-Suit V5.0** is a local AI agent development platform with:
- **26 operational tools** ready for immediate use
- **Local security** - everything runs on your machine
- **Real compression technology** - MMH-RS with verified performance
- **Web interface** for easy tool management

---

## ⚡ **Quick Start (3 Steps)**

### **Step 1: Check Requirements**
```bash
# Verify Python 3.8+
python --version

# Verify PowerShell 7.0+ (Windows)
pwsh --version
```

**Need to install?** [Python Download](https://python.org) | [PowerShell 7](https://github.com/PowerShell/PowerShell/releases)

### **Step 2: Download & Setup**
```bash
# Get the project
git clone https://github.com/Bigrob7605/Exo-Suit.git
cd Exo-Suit

# Install dependencies
pip install -r requirements.txt
```

### **Step 3: Start & Use**
```bash
# Start the system
python local-security-config.py

# Open browser to: http://127.0.0.1:8001
```

**✅ You're ready!** The web interface shows all 26 tools.

---

## 🛠️ **Try Your First Tool**

**Test the system health checker:**
```bash
python ops/System_Health_Checker_V5.py
```

**This will show:**
- System status and health
- Available resources
- Tool status
- Security configuration

---

## 🌐 **Web Interface Tour**

**Access**: `http://127.0.0.1:8001`

**What you'll see:**
- **Tools Section**: All 26 operational tools
- **Performance**: Real-time metrics and status
- **Security**: Security configuration and status
- **Documentation**: Guides and references

---

## 🔧 **Common First Tasks**

### **1. Security Scan**
```bash
python ops/Code_Scanner_V5.py --path ./my-project
```

### **2. File Compression**
```bash
python ops/File_Processor_V5.py --input ./large-file.txt --compression mmh-rs
```

### **3. Performance Check**
```bash
python ops/Performance_Monitor_V5.py
```

---

## 📚 **Next Steps**

- **Explore tools**: See [Tools Overview](docs/05-TOOLS/tools-overview.md)
- **Read docs**: Check [Complete Documentation](README.md)
- **Join community**: Visit [GitHub Discussions](https://github.com/Bigrob7605/Exo-Suit/discussions)

---

## 🚨 **Need Help?**

**Common issues:**
- **Port in use**: Use `--port 8002` when starting
- **Dependencies**: Run `pip install -r requirements.txt --force-reinstall`
- **Permissions**: Run PowerShell as Administrator (Windows)

**Still stuck?** Check the [troubleshooting guide](docs/04-OPERATIONS/troubleshooting.md)

---

## 🎉 **You're All Set!**

**Agent Exo-Suit V5.0 is running with:**
- ✅ **26 tools** ready for immediate use
- ✅ **Maximum security** protecting your system
- ✅ **Web interface** accessible and functional
- ✅ **Real compression technology** with GPU acceleration

**Start building AI agents, securing codebases, and optimizing performance!**

---

**Questions?** Check the [FAQ section](README.md#-faq) or [create an issue](https://github.com/Bigrob7605/Exo-Suit/issues) on GitHub.
