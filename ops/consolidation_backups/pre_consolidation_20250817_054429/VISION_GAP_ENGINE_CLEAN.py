#!/usr/bin/env python3
"""
VISION GAP ENGINE - CLEAN VERSION - Reads markdown files and identifies gaps
This version excludes archive directories and focuses only on active core files
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

class VisionGapEngineClean:
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.task_checklist = self.workspace_root / "AGENT_TASK_CHECKLIST.md"
        self.output_dir = self.workspace_root / "vision_gap_reports"
        self.output_dir.mkdir(exist_ok=True)
        
        # Directories to exclude from scanning (archive and obsolete files)
        self.exclude_dirs = {
            'archive',
            '.git',
            '.venv',
            'node_modules',
            '__pycache__',
            '.pytest_cache'
        }
        
        # Gap detection patterns
        self.gap_patterns = {
            'incomplete_tasks': r'\[ \]',  # Unchecked tasks
            'in_progress': r'\[\]',      # Tasks in progress
            'completed': r'\[\]',        # Completed tasks
            'blocked': r'\[\]',          # Blocked tasks
            'missing_content': r'Agent Notes:\s*$',  # Empty agent notes
            'todo_patterns': r'(TODO|FIXME|BUG|HACK)',  # Common todo patterns
            'unimplemented_features': r'(not implemented|coming soon|planned)',  # Unimplemented features
        }
    
    def should_scan_directory(self, path: Path) -> bool:
        """Check if a directory should be scanned (exclude archive and system dirs)"""
        for exclude_dir in self.exclude_dirs:
            if exclude_dir in path.parts:
                return False
        return True
    
    def get_active_markdown_files(self) -> List[Path]:
        """Get only active markdown files, excluding archive and system directories"""
        active_files = []
        
        for md_file in self.workspace_root.rglob("*.md"):
            if self.should_scan_directory(md_file.parent):
                active_files.append(md_file)
        
        return active_files
    
    def scan_project_gaps(self):
        """Main function to scan the active project for gaps"""
        print(" VISION GAP ENGINE - CLEAN VERSION - Scanning Active Project for Gaps")
        print("=" * 70)
        
        gaps = {
            'scan_timestamp': datetime.now().isoformat(),
            'task_completion': {},
            'content_gaps': {},
            'implementation_gaps': {},
            'recommendations': [],
            'summary': {}
        }
        
        # 1. Scan task checklist for completion gaps
        print(" Scanning Task Checklist...")
        gaps['task_completion'] = self._scan_task_checklist()
        
        # 2. Scan active markdown files for content gaps
        print(" Scanning Active Markdown Files for Content Gaps...")
        gaps['content_gaps'] = self._scan_content_gaps()
        
        # 3. Scan for implementation gaps
        print(" Scanning for Implementation Gaps...")
        gaps['implementation_gaps'] = self._scan_implementation_gaps()
        
        # 4. Generate recommendations
        print(" Generating Recommendations...")
        gaps['recommendations'] = self._generate_recommendations(gaps)
        
        # 5. Create summary
        gaps['summary'] = self._create_gap_summary(gaps)
        
        # 6. Save report
        self._save_gap_report(gaps)
        
        print(" Vision Gap Analysis Complete!")
        return gaps
    
    def _scan_task_checklist(self) -> Dict:
        """Scan the main task checklist for completion status"""
        if not self.task_checklist.exists():
            return {'error': 'Task checklist not found'}
        
        with open(self.task_checklist, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count different task states
        total_tasks = len(re.findall(r'\[ \]|\[\]|\[\]|\[\]', content))
        pending_tasks = len(re.findall(r'\[ \]', content))
        in_progress = len(re.findall(r'\[\]', content))
        completed_tasks = len(re.findall(r'\[\]', content))
        blocked_tasks = len(re.findall(r'\[\]', content))
        
        # Find empty agent notes (potential gaps)
        empty_notes = len(re.findall(r'Agent Notes:\s*$', content, re.MULTILINE))
        
        return {
            'total_tasks': total_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress,
            'completed_tasks': completed_tasks,
            'blocked_tasks': blocked_tasks,
            'empty_agent_notes': empty_notes,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'progress_rate': ((completed_tasks + in_progress) / total_tasks * 100) if total_tasks > 0 else 0
        }
    
    def _scan_content_gaps(self) -> Dict:
        """Scan active markdown files for content gaps and missing information"""
        content_gaps = {
            'files_scanned': 0,
            'gaps_found': 0,
            'gap_details': [],
            'missing_sections': [],
            'incomplete_content': []
        }
        
        # Scan only active markdown files (exclude archive)
        md_files = self.get_active_markdown_files()
        content_gaps['files_scanned'] = len(md_files)
        
        print(f"    Scanning {len(md_files)} active markdown files...")
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                file_gaps = self._analyze_file_content(md_file, content)
                if file_gaps:
                    content_gaps['gaps_found'] += len(file_gaps)
                    content_gaps['gap_details'].extend(file_gaps)
                    
            except Exception as e:
                print(f"    Error scanning {md_file}: {e}")
        
        return content_gaps
    
    def _analyze_file_content(self, file_path: Path, content: str) -> List[Dict]:
        """Analyze a single file for content gaps"""
        gaps = []
        
        # Check for truly empty sections (section header followed immediately by next section or end)
        empty_sections = re.findall(r'##\s+(.+)$\s*(?=\n##|\n#|\Z)', content, re.MULTILINE | re.DOTALL)
        for section in empty_sections:
            # Verify it's actually empty by checking if there's content between this section and the next
            section_pattern = r'##\s+' + re.escape(section) + r'\s*(?:\n(?!##|\n#|\Z).*)*\n(?=##|#|\Z)'
            section_match = re.search(section_pattern, content, re.MULTILINE | re.DOTALL)
            if section_match:
                section_content = section_match.group(0)
                # Remove the header and check if there's actual content
                content_only = re.sub(r'##\s+.*?\n', '', section_content, flags=re.MULTILINE)
                if len(content_only.strip()) < 50:  # Very minimal content
                    gaps.append({
                        'type': 'empty_section',
                        'file': str(file_path),
                        'section': section,
                        'severity': 'medium',
                        'description': f'Section "{section}" has minimal content ({len(content_only.strip())} chars)'
                    })
        
        # Check for TODO patterns
        todos = re.findall(r'(TODO|FIXME|BUG|HACK)[:\s]+(.+)', content, re.IGNORECASE)
        for todo_type, description in todos:
            gaps.append({
                'type': 'todo_item',
                'file': str(file_path),
                'todo_type': todo_type,
                'description': description.strip(),
                'severity': 'high' if todo_type in ['BUG', 'FIXME'] else 'medium'
            })
        
        # Check for incomplete content (very short sections)
        sections = re.split(r'##\s+', content, flags=re.MULTILINE)
        for i, section in enumerate(sections[1:], 1):  # Skip first empty section
            if len(section.strip()) < 100:  # Very short section
                section_title = section.split('\n')[0].strip()
                gaps.append({
                    'type': 'incomplete_section',
                    'file': str(file_path),
                    'section': section_title,
                    'content_length': len(section.strip()),
                    'severity': 'low',
                    'description': f'Section "{section_title}" has minimal content ({len(section.strip())} chars)'
                })
        
        return gaps
    
    def _scan_implementation_gaps(self) -> Dict:
        """Scan for gaps between documentation and implementation"""
        implementation_gaps = {
            'missing_implementations': 0,
            'documentation_mismatches': 0,
            'gap_details': []
        }
        
        # Look for common implementation gap patterns with context
        gap_patterns = [
            (r'\b(?:not implemented|coming soon|planned|future)\b', 'feature_not_implemented'),
            (r'\b(?:placeholder|stub|dummy)\b', 'implementation_stub'),
            (r'\b(?:error|exception|fail)\b(?!\s+handling|\s+recovery)', 'implementation_error'),
            (r'\b(?:broken|doesn\'t work|fails)\b(?!\s+gracefully|\s+with\s+recovery)', 'broken_implementation')
        ]
        
        # Scan only active markdown files
        md_files = self.get_active_markdown_files()
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for pattern, gap_type in gap_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Get context around the match to verify it's actually a gap
                        match_start = content.lower().find(match.lower())
                        if match_start != -1:
                            # Get 100 characters before and after for context
                            context_start = max(0, match_start - 100)
                            context_end = min(len(content), match_start + len(match) + 100)
                            context = content[context_start:context_end]
                            
                            # Skip if it's in a code block or if it's just normal documentation
                            if not self._is_in_code_block(context, match_start - context_start):
                                # Only count if it's not in a positive context
                                if not self._is_positive_context(context, match):
                                    implementation_gaps['missing_implementations'] += 1
                                    implementation_gaps['gap_details'].append({
                                        'type': gap_type,
                                        'file': str(md_file),
                                        'pattern_match': match,
                                        'context': context.strip(),
                                        'severity': 'high' if gap_type in ['broken_implementation', 'implementation_error'] else 'medium'
                                    })
                        
            except Exception as e:
                print(f"    Error scanning {md_file}: {e}")
        
        return implementation_gaps
    
    def _is_in_code_block(self, context: str, match_pos: int) -> bool:
        """Check if the match is inside a code block"""
        # Count backticks before the match position
        backticks_before = context[:match_pos].count('')
        # If odd number of backticks before, we're in a code block
        return backticks_before % 2 == 1
    
    def _is_positive_context(self, context: str, match: str) -> bool:
        """Check if the context suggests this is not actually a gap"""
        positive_indicators = [
            'successfully', 'working', 'operational', 'complete', 'finished',
            'achieved', 'implemented', 'resolved', 'fixed', 'handled'
        ]
        
        context_lower = context.lower()
        for indicator in positive_indicators:
            if indicator in context_lower:
                return True
        
        return False
    
    def _generate_recommendations(self, gaps: Dict) -> List[str]:
        """Generate actionable recommendations based on gaps found"""
        recommendations = []
        
        # Task completion recommendations
        task_comp = gaps['task_completion']
        if task_comp.get('completion_rate', 0) < 50:
            recommendations.append(" CRITICAL: Project completion rate below 50%. Focus on completing core tasks first.")
        
        if task_comp.get('empty_agent_notes', 0) > 0:
            recommendations.append(f" Found {task_comp['empty_agent_notes']} tasks with empty agent notes. Agents should document their work.")
        
        if task_comp.get('blocked_tasks', 0) > 0:
            recommendations.append(f" Found {task_comp['blocked_tasks']} blocked tasks. Review and resolve blockers immediately.")
        
        # Content gap recommendations
        content_gaps = gaps['content_gaps']
        if content_gaps.get('gaps_found', 0) > 0:
            recommendations.append(f" Found {content_gaps['gaps_found']} content gaps. Prioritize filling missing documentation.")
        
        # Implementation gap recommendations
        impl_gaps = gaps['implementation_gaps']
        if impl_gaps.get('missing_implementations', 0) > 0:
            recommendations.append(f" Found {impl_gaps['missing_implementations']} implementation gaps. Focus on completing core functionality.")
        
        # General recommendations
        if not recommendations:
            recommendations.append(" No critical gaps detected. Continue with current development plan.")
        else:
            recommendations.append(" Prioritize gaps by severity: High > Medium > Low")
            recommendations.append(" Update task checklist as work progresses")
            recommendations.append(" Run gap analysis regularly to track progress")
        
        return recommendations
    
    def _create_gap_summary(self, gaps: Dict) -> Dict:
        """Create a summary of all gaps found"""
        task_comp = gaps['task_completion']
        content_gaps = gaps['content_gaps']
        impl_gaps = gaps['implementation_gaps']
        
        total_gaps = (
            content_gaps.get('gaps_found', 0) + 
            impl_gaps.get('missing_implementations', 0) +
            impl_gaps.get('documentation_mismatches', 0)
        )
        
        return {
            'total_gaps': total_gaps,
            'completion_rate': task_comp.get('completion_rate', 0),
            'progress_rate': task_comp.get('progress_rate', 0),
            'files_scanned': content_gaps.get('files_scanned', 0),
            'overall_status': self._determine_overall_status(gaps)
        }
    
    def _determine_overall_status(self, gaps: Dict) -> str:
        """Determine overall project status based on gaps"""
        task_comp = gaps['task_completion']
        content_gaps = gaps['content_gaps']
        
        completion_rate = task_comp.get('completion_rate', 0)
        total_gaps = content_gaps.get('gaps_found', 0)
        
        if completion_rate >= 90 and total_gaps <= 5:
            return "EXCELLENT - High completion, minimal gaps"
        elif completion_rate >= 75 and total_gaps <= 15:
            return "GOOD - Solid progress, manageable gaps"
        elif completion_rate >= 50 and total_gaps <= 30:
            return "FAIR - Moderate progress, some gaps"
        else:
            return "NEEDS IMPROVEMENT - Low completion, many gaps"
    
    def _save_gap_report(self, gaps: Dict):
        """Save the gap analysis report to a markdown file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"vision_gap_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(self._generate_report_content(gaps))
        
        print(f" Gap report saved: {report_file}")
        return report_file
    
    def _generate_report_content(self, gaps: Dict) -> str:
        """Generate the markdown content for the gap report"""
        summary = gaps['summary']
        task_comp = gaps['task_completion']
        content_gaps = gaps['content_gaps']
        impl_gaps = gaps['implementation_gaps']
        
        report = f"""# VISION GAP ANALYSIS REPORT - CLEAN VERSION

**Generated**: {gaps['scan_timestamp']}  
**Engine**: VisionGap Engine Clean V1.0  
**Status**: {summary['overall_status']}  

---

## EXECUTIVE SUMMARY

**Total Gaps Identified**: {summary['total_gaps']}  
**Project Completion Rate**: {summary['completion_rate']:.1f}%  
**Project Progress Rate**: {summary['progress_rate']:.1f}%  
**Overall Status**: {summary['overall_status']}  

---

## TASK COMPLETION ANALYSIS

**Total Tasks**: {task_comp.get('total_tasks', 0)}  
**Completed**: {task_comp.get('completed_tasks', 0)}  
**In Progress**: {task_comp.get('in_progress_tasks', 0)}  
**Pending**: {task_comp.get('pending_tasks', 0)}  
**Blocked**: {task_comp.get('blocked_tasks', 0)}  
**Empty Agent Notes**: {task_comp.get('empty_agent_notes', 0)}  

---

## CONTENT GAPS

**Files Scanned**: {content_gaps.get('files_scanned', 0)}  
**Gaps Found**: {content_gaps.get('gaps_found', 0)}  

"""
        
        if content_gaps.get('gap_details'):
            report += "### Gap Details\n"
            for gap in content_gaps['gap_details'][:10]:  # Show first 10 gaps
                report += f"- **{gap['type'].title()}**: {gap['description']}\n"
            if len(content_gaps['gap_details']) > 10:
                report += f"- ... and {len(content_gaps['gap_details']) - 10} more gaps\n"
        
        report += f"""
---

## IMPLEMENTATION GAPS

**Missing Implementations**: {impl_gaps.get('missing_implementations', 0)}  
**Documentation Mismatches**: {impl_gaps.get('documentation_mismatches', 0)}  

---

## RECOMMENDATIONS

"""
        
        for rec in gaps['recommendations']:
            report += f"{rec}\n"
        
        report += f"""
---

## CLEAN SCAN SUMMARY

**This scan focused only on ACTIVE core files, excluding archive and obsolete directories.**
**The results represent the true current state of the operational system.**

---
*Report generated by VisionGap Engine Clean - Making the impossible inevitable*
"""
        
        return report

def main():
    """Main entry point"""
    engine = VisionGapEngineClean()
    gaps = engine.scan_project_gaps()
    
    # Print summary
    summary = gaps['summary']
    print("\n" + "=" * 60)
    print(" VISION GAP ANALYSIS RESULTS")
    print("=" * 60)
    print(f"Total Gaps: {summary['total_gaps']}")
    print(f"Completion Rate: {summary['completion_rate']:.1f}%")
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Report saved to: {engine.output_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
