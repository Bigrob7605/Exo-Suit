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
        for name in ["AgentExoSuitV4.ps1", "AgentExoSuitV3.ps1", "1M_TOKEN_UPGRADE_GAME_PLAN.md"]:
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
# Entry Point
###############################################################################
def main():
    engine = VisionGapEngine()
    dreams = engine.read_dreams()
    impl = engine.scan_implementation()
    gaps = engine.detect_gaps(dreams, impl)
    engine.generate_report(dreams, impl, gaps)
    print("VisionGap analysis complete.")

if __name__ == "__main__":
    main()
