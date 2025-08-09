# 🚀 Agent Exo-Suit V2.0 Command Queue - Cognitive Layer

**Version:** 2.0 "Monster-Mode"  
**Date:** August 9, 2025  
**Status:** 🎯 **COGNITIVE SUBSYSTEM READY**

---

## 🧠 Cognitive Layer Workflow

### **Step 0: Context Loading** (NEW)
- Load `context/_task/task_context.md` - GPU-RAG assembled context
- Load `context/_latest/context_summary.json` - Context metadata
- Load `context/_latest/ownership.json` - File ownership mapping
- **Prefer RAG-assembled context first** - Most relevant chunks
- **Respect token budget** - Stay within budget limits

### **Step 0.5: Persona Activation** (NEW)
- **Developer Persona:** Focus on code, tests, documentation
- **Scientist Persona:** Focus on data, analysis, research
- **DevOps Persona:** Focus on deployment, infrastructure, CI/CD
- **UI Persona:** Focus on frontend, user experience, design
- **Load persona-specific context filters** and quality gates

### **Step 1: Drift Detection** (Enhanced)
- Run `.\ops\drift-gate.ps1 -json`
- Check `restore\DRIFT_REPORT.json` for changes
- **Stop if drift detected** - Reconcile before proceeding
- **Document drift in PLAN.md** - Track all changes

### **Step 2: Block Detection** (Enhanced)
- Load `context/_latest/placeholders.json`
- **If Severity == BLOCK:** Stop and open "remove-blockers" task
- **List all BLOCK items** with file paths and line numbers
- **Do not write code** until BLOCK items resolved or waived
- **Update PLAN.md** with blocker resolution plan

### **Step 2.5: Quick Scan** (NEW)
- Run `.\ops\quick-scan.ps1` - Parallel static analysis
- **If lint fails:** Fix issues first, no code writes until green
- **Run in parallel:** ESLint, Ruff, Pyright, Cargo Clippy
- **Fail-fast:** Stop on first error, don't debug AI-generated lint fixes

### **Step 3: Context Assembly** (Enhanced)
- Use `.\ops\context\assemble.ps1 -query "your task" -persona developer -budgetTokens 12000`
- **GPU-RAG powered:** Laser-focused context retrieval
- **Ownership-aware:** Prioritize AI-owned files
- **Budget-controlled:** Respect token limits
- **Persona-filtered:** Load appropriate file types

### **Step 4: Patch Forge** (Enhanced)
- Run `.\ops\patch-forge.ps1` - Create AI branch
- **One branch per feature:** `ai/YYYYMMDD-HHMM-username`
- **Automatic drift check:** Ensures clean starting point
- **Ready for changes:** Safe environment for AI work

### **Step 5: Implementation** (Enhanced)
- **Follow task context:** Use assembled context from Step 3
- **Respect ownership:** Route diffs to appropriate owners
- **Write tests first:** Contract enforcement
- **Document changes:** Update PLAN.md with progress

### **Step 6: Quality Gates** (Enhanced)
- **Run test swarm:** `.\ops\test-swarm.ps1`
- **Contract enforcement:** Tests pass before implementation
- **Parallel execution:** Multiple test runners
- **Fail-fast:** Stop on first failure

### **Step 7: Commit & Patch** (Enhanced)
- Run `.\ops\patch-forge.ps1 -commit` - Commit changes
- Run `.\ops\patch-forge.ps1 -diff` - Generate patch
- **Review patch:** Check `restore\AI_PATCH.diff`
- **Owner pings:** Automatic diff routing for non-AI owners
- **Human gate:** Manual review before merge

---

## 🛡️ Safety Protocols (V2.0 Enhanced)

### **Context Governor**
- **Token budget enforcement:** Never exceed budget limits
- **RAG prioritization:** Use GPU-RAG scores for context selection
- **Ownership routing:** Automatic diff routing to file owners
- **Drift detection:** Automatic detection and reporting

### **Quality Gates**
- **Block detection:** Stop on BLOCK severity items
- **Lint enforcement:** Fail-fast on static analysis
- **Test contracts:** Write tests before implementation
- **Patch review:** Human gate before merge

### **Performance Optimization**
- **Max-Perf mode:** Ultimate Performance power plan
- **GPU acceleration:** CUDA-powered RAG indexing
- **Parallel processing:** Multi-threaded scanning and testing
- **Scratch directories:** NVMe-optimized temp storage

---

## 🎯 Persona-Specific Workflows

### **Developer Persona**
```
Context Focus: Code, tests, documentation
Quality Gates: Linting, unit tests, code review
File Types: .py, .js, .ts, .ps1, .sh, .md
```

### **Scientist Persona**
```
Context Focus: Data, analysis, research, documentation
Quality Gates: Data validation, statistical tests, reproducibility
File Types: .py, .md, .txt, .json, .yaml, .ipynb
```

### **DevOps Persona**
```
Context Focus: Deployment, infrastructure, CI/CD
Quality Gates: Security scanning, deployment validation
File Types: .yaml, .yml, .json, .ps1, .sh, .md
```

### **UI Persona**
```
Context Focus: Frontend, user experience, design
Quality Gates: Accessibility, responsive design, user testing
File Types: .js, .ts, .tsx, .css, .html, .md
```

---

## 🚀 Advanced Features (V2.0)

### **GPU-RAG Context Brain**
- **Sentence-transformers:** Advanced embedding models
- **FAISS indexing:** High-performance similarity search
- **Context assembly:** Intelligent chunk selection
- **Budget control:** Token-aware context management

### **Max-Perf Optimization**
- **Ultimate Performance:** Maximum power plan
- **GPU acceleration:** CUDA-optimized operations
- **Scratch directories:** NVMe-optimized storage
- **Memory optimization:** 12GB Node.js heap

### **Parallel Processing**
- **Multi-linter shock team:** Parallel static analysis
- **Test swarm:** Parallel test execution
- **Context indexing:** Parallel file processing
- **Performance monitoring:** Real-time metrics

### **Safety & Governance**
- **Owner ping auto-diffs:** Automatic routing
- **Block severity gates:** Automatic stopping
- **Patch forge:** Reversible, auditable edits
- **Drift detection:** Automatic change tracking

---

## 📊 Monitoring & Analytics

### **Performance Metrics**
- **Context assembly time:** Target < 30 seconds
- **RAG indexing speed:** Target < 5 minutes for large repos
- **Parallel processing efficiency:** Target > 80% CPU utilization
- **Memory usage:** Target < 500MB for large contexts

### **Quality Metrics**
- **Lint pass rate:** Target 100%
- **Test pass rate:** Target 100%
- **Block item count:** Target < 10
- **Drift detection accuracy:** Target 100%

### **User Experience**
- **Context relevance score:** Target > 0.8
- **Token budget utilization:** Target > 80%
- **Patch review time:** Target < 5 minutes
- **System responsiveness:** Target < 2 seconds

---

## 🎯 Quick Reference

### **Essential Commands**
```powershell
# Full orchestration
.\go-big.ps1 -query "your task description" -persona developer

# Context assembly only
.\ops\context\assemble.ps1 -query "your task" -persona developer -budgetTokens 12000

# Patch management
.\ops\patch-forge.ps1                    # Create AI branch
.\ops\patch-forge.ps1 -commit            # Commit changes
.\ops\patch-forge.ps1 -diff              # Generate patch

# Quality checks
.\ops\quick-scan.ps1                     # Parallel linting
.\ops\drift-gate.ps1 -json               # Drift detection

# Performance
.\ops\max-perf.ps1                       # Enable Max-Perf
.\ops\normal-perf.ps1                    # Restore normal
```

### **Context Loading**
```powershell
# Load task context
Get-Content "context/_task/task_context.md"

# Load ownership mapping
Get-Content "context/_latest/ownership.json" | ConvertFrom-Json

# Load placeholder scan
Get-Content "context/_latest/placeholders.json" | ConvertFrom-Json | Where-Object { $_.Severity -eq "BLOCK" }
```

---

## 🎉 Success Criteria

### **V2.0 Goals**
- ✅ **Cognitive context:** GPU-RAG powered context assembly
- ✅ **Performance optimization:** Max-Perf mode and parallel processing
- ✅ **Quality gates:** Automatic linting and testing
- ✅ **Safety protocols:** Owner routing and drift detection
- ✅ **User experience:** One-click "Go Big" orchestration

### **Next Milestones**
- 🔄 **LSIF integration:** Cross-language symbol graph
- 🔄 **Visual maps:** Mermaid diagram generation
- 🔄 **Enhanced telemetry:** HTML dashboard
- 🔄 **RAM disk:** Ultra-fast caching

---

**Agent Exo-Suit V2.0 "Monster-Mode" - Cognitive Layer Ready! 🧠**
