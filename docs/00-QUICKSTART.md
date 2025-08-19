# 🚀 **Quick Start - Exo-Suit V5.0**

## **🎯 30-Second Setup**

**Get Exo-Suit V5.0 running in under 2 minutes** with this quick start guide. The system provides enterprise-grade AI agent development with maximum security by default.

---

## **⚡ System Requirements**

- **Python**: 3.8+ (3.13 recommended)
- **GPU**: NVIDIA RTX series (RTX 4070+ recommended)
- **Memory**: 16GB RAM minimum, 32GB+ recommended
- **Storage**: 10GB free space

---

## **🚀 Quick Start (2 Minutes)**

### **Step 1: Clone Repository**
```bash
git clone https://github.com/Bigrob7605/Exo-Suit.git
cd Exo-Suit
```

### **Step 2: Start Secure Server**
```bash
python local-security-config.py
```

**Result**: Server running on `http://127.0.0.1:8000` with maximum security

### **Step 3: Access Website**
Open browser to: `http://127.0.0.1:8000/index.html`

---

## **✅ What You Get**

- **21/43 Tools Operational** (49% complete)
- **Performance**: 207-3.7K files/second
- **Compression**: 3.37x average (ZSTD), 2.16x average (LZ4)
- **Security**: Localhost-only, external access blocked
- **Architecture**: Modular, enterprise-ready platform

---

## **🔒 Security Features (Active by Default)**

- **Localhost-only access** - External access blocked
- **Comprehensive security headers** - XSS, CSRF protection
- **Access logging** - All activity tracked
- **Bulletproof protection** - Multi-layer security system

---

## **🎯 Next Steps**

### **For Development**
- **[System Overview →](01-ARCHITECTURE/system-overview.md)**: Technical specifications
- **[Performance Benchmarks →](02-PERFORMANCE/benchmarks.md)**: Performance metrics
- **[Security Suite →](03-SECURITY/security-suite.md)**: Security features
- **[Operations Guide →](04-OPERATIONS/maintenance.md)**: Maintenance procedures

### **For Customization**
- **Components**: Add new components to `components/` directory
- **Styling**: Customize CSS in `assets/css/core.css`
- **Security**: Modify `local-security-config.py` for custom settings

---

## **🛠️ Troubleshooting**

### **Server Won't Start**
```bash
# Kill existing processes
taskkill /f /im python.exe

# Use different port
python local-security-config.py --port 9000
```

### **Website Not Loading**
- Verify server is running: `netstat -an | findstr :8000`
- Check browser console for errors
- Ensure all component files exist

---

## **🔗 Quick Links**

- **[Live Demo](https://bigrob7605.github.io/Exo-Suit/)**: See it in action
- **[GitHub Repository](https://github.com/Bigrob7605/Exo-Suit)**: Source code
- **[White Papers](Project%20White%20Papers/)**: V5.0 specifications

---

**Status**: ✅ **READY FOR DEVELOPMENT** | **21/43 Tools Operational** | **Maximum Security Active**

---

*[System Overview →](01-ARCHITECTURE/system-overview.md) | [Performance Benchmarks →](02-PERFORMANCE/benchmarks.md) | [Security Suite →](03-SECURITY/security-suite.md) | [Operations Guide →](04-OPERATIONS/maintenance.md)*
