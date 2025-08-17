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
