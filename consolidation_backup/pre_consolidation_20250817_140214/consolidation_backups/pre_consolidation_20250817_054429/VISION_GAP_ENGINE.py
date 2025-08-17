#!/usr/bin/env python3
"""
VISION GAP ENGINE - Reads markdown files and identifies gaps
This is the core engine that makes the VisionGap system work
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

class VisionGapEngine:
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.task_checklist = self.workspace_root / "AGENT_TASK_CHECKLIST.md"
        self.vision_gap_data = self.workspace_root / "vision_gap_data"
        self.output_dir = self.workspace_root / "vision_gap_reports"
        self.output_dir.mkdir(exist_ok=True)
        
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
    
    def scan_project_gaps(self):
        """Main function to scan the entire project for gaps"""
        print(" VISION GAP ENGINE - Scanning Project for Gaps")
        print("=" * 60)
        
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
        
        # 2. Scan markdown files for content gaps
        print(" Scanning Markdown Files for Content Gaps...")
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
        """Scan markdown files for content gaps and missing information"""
        content_gaps = {
            'files_scanned': 0,
            'gaps_found': 0,
            'gap_details': [],
            'missing_sections': [],
            'incomplete_content': []
        }
        
        # Scan all markdown files in the project
        md_files = list(self.workspace_root.rglob("*.md"))
        content_gaps['files_scanned'] = len(md_files)
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                file_gaps = self._analyze_file_content(md_file, content)
                if file_gaps:
                    content_gaps['gaps_found'] += len(file_gaps)
                    content_gaps['gap_details'].extend(file_gaps)
                    
            except Exception as e:
                print(f"Error scanning {md_file}: {e}")
        
        return content_gaps
    
    def _analyze_file_content(self, file_path: Path, content: str) -> List[Dict]:
        """Analyze a single file for content gaps"""
        gaps = []
        
        # Check for truly empty sections (section header followed immediately by next section or end)
        # More accurate pattern: section header followed by only whitespace/newlines until next section
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
        
        # Check for incomplete content with improved quality assessment
        sections = re.split(r'##\s+', content, flags=re.MULTILINE)
        for i, section in enumerate(sections[1:], 1):  # Skip first empty section
            section_content = section.strip()
            section_title = section.split('\n')[0].strip()
            
            # Improved gap detection with quality assessment
            if len(section_content) < 50:  # Extremely short section (likely empty)
                # Check if it's actually empty or just concise
                if not self._has_meaningful_content(section_content):
                    gaps.append({
                        'type': 'empty_section',
                        'file': str(file_path),
                        'section': section_title,
                        'content_length': len(section_content),
                        'severity': 'medium',
                        'description': f'Section "{section_title}" appears to be empty or have minimal meaningful content'
                    })
            elif len(section_content) < 200:  # Short section - needs quality assessment
                # Only flag if content quality is poor
                if not self._has_meaningful_content(section_content):
                    gaps.append({
                        'type': 'incomplete_section',
                        'file': str(file_path),
                        'section': section_title,
                        'content_length': len(section_content),
                        'severity': 'low',
                        'description': f'Section "{section_title}" has limited content and may need expansion'
                    })
        
        return gaps
    
    def _has_meaningful_content(self, content: str) -> bool:
        """Assess if content has meaningful information beyond just formatting"""
        if not content or len(content.strip()) == 0:
            return False
        
        # Remove common formatting elements
        clean_content = re.sub(r'[#*_`\-\[\]()]', '', content)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # Check for meaningful content patterns
        meaningful_patterns = [
            r'\b\w{3,}\b',  # Words with 3+ characters
            r'\d+',         # Numbers
            r'[A-Z][a-z]+', # Proper nouns
            r'\b(?:the|and|or|but|for|with|from|to|in|on|at|by)\b',  # Common words
        ]
        
        # Count meaningful elements
        meaningful_count = 0
        for pattern in meaningful_patterns:
            meaningful_count += len(re.findall(pattern, clean_content))
        
        # Content is meaningful if it has sufficient meaningful elements
        return meaningful_count >= 3 and len(clean_content) >= 20
    
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
        
        md_files = list(self.workspace_root.rglob("*.md"))
        
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
                print(f"Error scanning {md_file}: {e}")
        
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
            'total_gaps_identified': total_gaps,
            'project_completion_rate': task_comp.get('completion_rate', 0),
            'project_progress_rate': task_comp.get('progress_rate', 0),
            'files_with_gaps': content_gaps.get('files_scanned', 0),
            'critical_gaps': len([g for g in content_gaps.get('gap_details', []) if g.get('severity') == 'high']),
            'overall_status': self._determine_overall_status(gaps)
        }
    
    def _determine_overall_status(self, gaps: Dict) -> str:
        """Determine overall project status based on gaps"""
        task_comp = gaps['task_completion']
        completion_rate = task_comp.get('completion_rate', 0)
        
        if completion_rate >= 90:
            return "EXCELLENT - Near completion"
        elif completion_rate >= 75:
            return "GOOD - Strong progress"
        elif completion_rate >= 50:
            return "FAIR - Moderate progress"
        elif completion_rate >= 25:
            return "POOR - Limited progress"
        else:
            return "CRITICAL - Minimal progress"
    
    def _save_gap_report(self, gaps: Dict):
        """Save the gap analysis report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.output_dir / f"vision_gap_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(self._format_gap_report(gaps))
        
        print(f" Gap report saved: {report_file}")
    
    def _format_gap_report(self, gaps: Dict) -> str:
        """Format the gap analysis as a markdown report"""
        report = f"""# VISION GAP ANALYSIS REPORT

**Generated**: {gaps['scan_timestamp']}  
**Engine**: VisionGap Engine V1.0  
**Status**: {gaps['summary']['overall_status']}  

---

## EXECUTIVE SUMMARY

**Total Gaps Identified**: {gaps['summary']['total_gaps_identified']}  
**Project Completion Rate**: {gaps['summary']['project_completion_rate']:.1f}%  
**Project Progress Rate**: {gaps['summary']['project_progress_rate']:.1f}%  
**Overall Status**: {gaps['summary']['overall_status']}  

---

## TASK COMPLETION ANALYSIS

**Total Tasks**: {gaps['task_completion']['total_tasks']}  
**Completed**: {gaps['task_completion']['completed_tasks']}  
**In Progress**: {gaps['task_completion']['in_progress_tasks']}  
**Pending**: {gaps['task_completion']['pending_tasks']}  
**Blocked**: {gaps['task_completion']['blocked_tasks']}  
**Empty Agent Notes**: {gaps['task_completion']['empty_agent_notes']}  

---

## CONTENT GAPS

**Files Scanned**: {gaps['content_gaps']['files_scanned']}  
**Gaps Found**: {gaps['content_gaps']['gaps_found']}  

"""
        
        # Add gap details
        if gaps['content_gaps']['gap_details']:
            report += "### Gap Details\n"
            for gap in gaps['content_gaps']['gap_details'][:10]:  # Limit to first 10
                report += f"- **{gap['type'].replace('_', ' ').title()}**: {gap['description']}\n"
            if len(gaps['content_gaps']['gap_details']) > 10:
                report += f"- ... and {len(gaps['content_gaps']['gap_details']) - 10} more gaps\n"
        
        report += "\n---\n"
        
        # Add implementation gaps
        report += f"## IMPLEMENTATION GAPS\n\n"
        report += f"**Missing Implementations**: {gaps['implementation_gaps']['missing_implementations']}  \n"
        report += f"**Documentation Mismatches**: {gaps['implementation_gaps']['documentation_mismatches']}  \n"
        
        # Add recommendations
        report += "\n---\n## RECOMMENDATIONS\n\n"
        for rec in gaps['recommendations']:
            report += f"{rec}\n"
        
        report += "\n---\n"
        report += "*Report generated by VisionGap Engine - Making the impossible inevitable*"
        
        return report

def main():
    """Main function for command line usage"""
    engine = VisionGapEngine()
    gaps = engine.scan_project_gaps()
    
    print("\n" + "=" * 60)
    print(" VISION GAP ANALYSIS RESULTS")
    print("=" * 60)
    print(f"Total Gaps: {gaps['summary']['total_gaps_identified']}")
    print(f"Completion Rate: {gaps['summary']['project_completion_rate']:.1f}%")
    print(f"Overall Status: {gaps['summary']['overall_status']}")
    print(f"Report saved to: {engine.output_dir}")

if __name__ == "__main__":
    main()
