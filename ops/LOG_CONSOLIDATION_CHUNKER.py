#!/usr/bin/env python3
"""
LOG CONSOLIDATION AND CHUNKING SYSTEM
Consolidates all project logs and reports into manageable work chunks
Agents can pick chunks based on their token limits and mark progress
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import re

class LogConsolidationChunker:
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.reports_dir = self.workspace_root / "reports"
        self.logs_dir = self.workspace_root / "logs"
        self.consolidation_dir = self.workspace_root / "consolidated_work"
        self.consolidation_dir.mkdir(exist_ok=True)
        
        # Work chunk definitions based on token limits
        self.token_chunk_sizes = {
            'small': 1000,      # Small agents: 1K tokens
            'medium': 5000,     # Medium agents: 5K tokens  
            'large': 15000,     # Large agents: 15K tokens
            'xlarge': 50000,    # XLarge agents: 50K tokens
            'unlimited': 100000 # Unlimited agents: 100K+ tokens
        }
        
        # Consolidation results
        self.consolidated_data = {}
        self.work_chunks = {}
        self.progress_tracker = {}
        
    def run_consolidation(self):
        """Execute the complete log consolidation and chunking process"""
        print("=== LOG CONSOLIDATION AND CHUNKING SYSTEM ===")
        print("Phase 1: Consolidating All Reports and Logs")
        print("Phase 2: Creating Work Chunks by Token Limits")
        print("Phase 3: Generating Master Task List")
        print("Phase 4: Setting Up Progress Tracking")
        print()
        
        # Phase 1: Consolidate all available data
        self._consolidate_all_data()
        
        # Phase 2: Create work chunks for different agent sizes
        self._create_work_chunks()
        
        # Phase 3: Generate master task list
        self._generate_master_task_list()
        
        # Phase 4: Set up progress tracking
        self._setup_progress_tracking()
        
        print("=== CONSOLIDATION COMPLETE ===")
        return self.work_chunks
    
    def _consolidate_all_data(self):
        """Consolidate all reports, logs, and analysis data"""
        print("Consolidating all project data...")
        
        self.consolidated_data = {
            'consolidation_timestamp': datetime.now().isoformat(),
            'reports': {},
            'logs': {},
            'analysis_results': {},
            'project_status': {},
            'critical_issues': []
        }
        
        # Consolidate reports
        self._consolidate_reports()
        
        # Consolidate logs
        self._consolidate_logs()
        
        # Consolidate analysis results
        self._consolidate_analysis_results()
        
        # Extract critical issues
        self._extract_critical_issues()
        
        print(f"Consolidated data from {len(self.consolidated_data['reports'])} reports and {len(self.consolidated_data['logs'])} log files")
    
    def _consolidate_reports(self):
        """Consolidate all generated reports"""
        if not self.reports_dir.exists():
            print("No reports directory found")
            return
        
        report_files = list(self.reports_dir.glob("*.md")) + list(self.reports_dir.glob("*.json"))
        
        for report_file in report_files:
            try:
                if report_file.suffix == '.md':
                    with open(report_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Extract key information from markdown
                    summary = self._extract_markdown_summary(content)
                    self.consolidated_data['reports'][report_file.stem] = {
                        'type': 'markdown',
                        'file_path': str(report_file),
                        'summary': summary,
                        'size': len(content),
                        'last_modified': datetime.fromtimestamp(report_file.stat().st_mtime).isoformat()
                    }
                
                elif report_file.suffix == '.json':
                    with open(report_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self.consolidated_data['reports'][report_file.stem] = {
                        'type': 'json',
                        'file_path': str(report_file),
                        'data': data,
                        'size': len(str(data)),
                        'last_modified': datetime.fromtimestamp(report_file.stat().st_mtime).isoformat()
                    }
                    
            except Exception as e:
                print(f"Error consolidating {report_file}: {e}")
                continue
    
    def _consolidate_logs(self):
        """Consolidate all log files"""
        if not self.logs_dir.exists():
            print("No logs directory found")
            return
        
        log_files = list(self.logs_dir.rglob("*.log")) + list(self.logs_dir.rglob("*.txt"))
        
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract key log information
                log_summary = self._extract_log_summary(content)
                self.consolidated_data['logs'][log_file.stem] = {
                    'file_path': str(log_file),
                    'summary': log_summary,
                    'size': len(content),
                    'last_modified': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
                }
                
            except Exception as e:
                print(f"Error consolidating log {log_file}: {e}")
                continue
    
    def _consolidate_analysis_results(self):
        """Consolidate analysis results from various sources"""
        # Look for analysis results in the consolidated data
        analysis_sources = [
            'PHOENIX_REPORT',
            'COMPREHENSIVE_SCALABLE_SCANNING_REPORT',
            'VISION_GAP_ANALYSIS_REPORT',
            'PROJECT_TRIAGE_REPORT'
        ]
        
        for source in analysis_sources:
            if source in self.consolidated_data['reports']:
                report_data = self.consolidated_data['reports'][source]
                
                if source == 'PHOENIX_REPORT':
                    self.consolidated_data['analysis_results']['phoenix_analysis'] = {
                        'health_score': self._extract_health_score(report_data),
                        'critical_issues': self._extract_phoenix_issues(report_data),
                        'repair_roadmap': self._extract_repair_roadmap(report_data)
                    }
                
                elif source == 'COMPREHENSIVE_SCALABLE_SCANNING_REPORT':
                    self.consolidated_data['analysis_results']['scanning_analysis'] = {
                        'files_scanned': self._extract_scan_metrics(report_data),
                        'unicode_issues': self._extract_unicode_issues(report_data),
                        'content_issues': self._extract_content_issues(report_data)
                    }
                
                elif source == 'VISION_GAP_ANALYSIS_REPORT':
                    self.consolidated_data['analysis_results']['vision_gap_analysis'] = {
                        'vision_strength': self._extract_vision_metrics(report_data),
                        'gaps_identified': self._extract_gap_metrics(report_data),
                        'alignment_score': self._extract_alignment_score(report_data)
                    }
    
    def _extract_critical_issues(self):
        """Extract and prioritize critical issues from all sources"""
        critical_issues = []
        
        # Extract from Phoenix Report
        if 'phoenix_analysis' in self.consolidated_data['analysis_results']:
            phoenix_issues = self.consolidated_data['analysis_results']['phoenix_analysis']['critical_issues']
            for issue in phoenix_issues:
                critical_issues.append({
                    'source': 'Phoenix Report',
                    'type': issue.get('type', 'Unknown'),
                    'severity': issue.get('severity', 'Unknown'),
                    'description': issue.get('description', 'No description'),
                    'priority': issue.get('priority', 999),
                    'estimated_time': issue.get('estimated_time', 'Unknown'),
                    'resources': issue.get('resources', 'Unknown')
                })
        
        # Extract from scanning analysis
        if 'scanning_analysis' in self.consolidated_data['analysis_results']:
            scan_analysis = self.consolidated_data['analysis_results']['scanning_analysis']
            
            if scan_analysis.get('unicode_issues', 0) > 0:
                critical_issues.append({
                    'source': 'Scanning Analysis',
                    'type': 'Unicode/Encoding Issues',
                    'severity': 'HIGH',
                    'description': f"{scan_analysis['unicode_issues']:,} Unicode/emoji issues found",
                    'priority': 1,
                    'estimated_time': '2-4 hours',
                    'resources': 'Text editor, regex tools'
                })
            
            if scan_analysis.get('content_issues', 0) > 0:
                critical_issues.append({
                    'source': 'Scanning Analysis',
                    'type': 'Content Quality Issues',
                    'severity': 'MEDIUM',
                    'description': f"{scan_analysis['content_issues']:,} placeholder/TODO items found",
                    'priority': 2,
                    'estimated_time': '1-2 days',
                    'resources': 'Content review, documentation'
                })
        
        # Sort by priority
        critical_issues.sort(key=lambda x: x['priority'])
        self.consolidated_data['critical_issues'] = critical_issues
    
    def _create_work_chunks(self):
        """Create work chunks for different agent token limits"""
        print("Creating work chunks for different agent sizes...")
        
        self.work_chunks = {
            'small': [],      # 1K token agents
            'medium': [],     # 5K token agents
            'large': [],      # 15K token agents
            'xlarge': [],     # 50K token agents
            'unlimited': []   # 100K+ token agents
        }
        
        # Create chunks based on critical issues
        self._create_issue_based_chunks()
        
        # Create chunks based on file types
        self._create_file_based_chunks()
        
        # Create chunks based on project areas
        self._create_area_based_chunks()
        
        # Create chunks based on repair phases
        self._create_phase_based_chunks()
        
        print(f"Created {sum(len(chunks) for chunks in self.work_chunks.values())} total work chunks")
    
    def _create_issue_based_chunks(self):
        """Create chunks based on critical issues"""
        for issue in self.consolidated_data['critical_issues']:
            # Small chunks: Individual issue descriptions
            self.work_chunks['small'].append({
                'id': f"issue_{issue['type'].lower().replace(' ', '_')}",
                'type': 'critical_issue',
                'title': f"Fix {issue['type']}",
                'description': issue['description'],
                'estimated_tokens': 800,
                'priority': issue['priority'],
                'estimated_time': issue['estimated_time'],
                'resources': issue['resources'],
                'status': 'pending'
            })
            
            # Medium chunks: Issue + context
            self.work_chunks['medium'].append({
                'id': f"issue_context_{issue['type'].lower().replace(' ', '_')}",
                'type': 'critical_issue_with_context',
                'title': f"Fix {issue['type']} with Context",
                'description': f"{issue['description']}\n\nSource: {issue['source']}\nSeverity: {issue['severity']}",
                'estimated_tokens': 3000,
                'priority': issue['priority'],
                'estimated_time': issue['estimated_time'],
                'resources': issue['resources'],
                'status': 'pending'
            })
    
    def _create_file_based_chunks(self):
        """Create chunks based on file types and sizes"""
        # Group files by type and size
        file_groups = {
            'markdown_files': [],
            'python_files': [],
            'configuration_files': [],
            'documentation_files': []
        }
        
        for report_name, report_data in self.consolidated_data['reports'].items():
            if report_data['type'] == 'markdown':
                file_groups['markdown_files'].append(report_data)
            elif report_data['type'] == 'json':
                file_groups['configuration_files'].append(report_data)
        
        # Create chunks for markdown files
        if file_groups['markdown_files']:
            self.work_chunks['small'].append({
                'id': 'markdown_cleanup_small',
                'type': 'file_cleanup',
                'title': 'Clean Small Markdown Files',
                'description': 'Clean up formatting and remove issues from small markdown files',
                'estimated_tokens': 1000,
                'priority': 3,
                'estimated_time': '30 minutes',
                'resources': 'Text editor',
                'status': 'pending'
            })
            
            self.work_chunks['large'].append({
                'id': 'markdown_cleanup_large',
                'type': 'file_cleanup_comprehensive',
                'title': 'Comprehensive Markdown Cleanup',
                'description': 'Clean up all markdown files with comprehensive formatting and content review',
                'estimated_tokens': 12000,
                'priority': 3,
                'estimated_time': '2-3 hours',
                'resources': 'Text editor, markdown linter',
                'status': 'pending'
            })
    
    def _create_area_based_chunks(self):
        """Create chunks based on project areas"""
        project_areas = [
            'core_documentation',
            'source_code',
            'testing_framework',
            'configuration_files',
            'build_system'
        ]
        
        for area in project_areas:
            self.work_chunks['medium'].append({
                'id': f'area_review_{area}',
                'type': 'area_review',
                'title': f'Review {area.replace("_", " ").title()}',
                'description': f'Comprehensive review and cleanup of {area.replace("_", " ")}',
                'estimated_tokens': 4000,
                'priority': 4,
                'estimated_time': '1-2 hours',
                'resources': 'Code editor, documentation tools',
                'status': 'pending'
            })
    
    def _create_phase_based_chunks(self):
        """Create chunks based on repair phases"""
        repair_phases = [
            'phase_1_foundation',
            'phase_2_vision_implementation',
            'phase_3_advanced_features',
            'phase_4_integration_testing'
        ]
        
        for phase in repair_phases:
            self.work_chunks['xlarge'].append({
                'id': f'phase_{phase}',
                'type': 'phase_implementation',
                'title': f'Implement {phase.replace("_", " ").title()}',
                'description': f'Complete implementation of {phase.replace("_", " ")} including all components and testing',
                'estimated_tokens': 35000,
                'priority': 5,
                'estimated_time': '1-2 weeks',
                'resources': 'Development team, testing environment',
                'status': 'pending'
            })
            
            self.work_chunks['unlimited'].append({
                'id': f'phase_{phase}_comprehensive',
                'type': 'phase_implementation_comprehensive',
                'title': f'Comprehensive {phase.replace("_", " ").title()} Implementation',
                'description': f'Complete implementation of {phase.replace("_", " ")} with full documentation, testing, and validation',
                'estimated_tokens': 80000,
                'priority': 5,
                'estimated_time': '2-3 weeks',
                'resources': 'Full development team, comprehensive testing',
                'status': 'pending'
            })
    
    def _generate_master_task_list(self):
        """Generate a master task list for agents to pick from"""
        print("Generating master task list...")
        
        master_list = {
            'generated': datetime.now().isoformat(),
            'total_chunks': sum(len(chunks) for chunks in self.work_chunks.values()),
            'chunks_by_size': {size: len(chunks) for size, chunks in self.work_chunks.items()},
            'priority_distribution': self._calculate_priority_distribution(),
            'estimated_total_time': self._calculate_total_estimated_time(),
            'work_chunks': self.work_chunks
        }
        
        # Save master task list
        master_list_path = self.consolidation_dir / "MASTER_TASK_LIST.json"
        with open(master_list_path, 'w', encoding='utf-8') as f:
            json.dump(master_list, f, indent=2, ensure_ascii=False)
        
        # Generate human-readable task list
        self._generate_human_readable_task_list(master_list)
        
        print(f"Master task list generated: {master_list_path}")
    
    def _generate_human_readable_task_list(self, master_list):
        """Generate a human-readable version of the task list"""
        task_list_content = f"""# MASTER TASK LIST - Agent Exo-Suit V5.0 Project Healing

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## EXECUTIVE SUMMARY

**Total Work Chunks**: {master_list['total_chunks']}
**Estimated Total Time**: {master_list['estimated_total_time']}
**Priority Distribution**: {master_list['priority_distribution']}

## WORK CHUNKS BY AGENT SIZE

### Small Agents (1K tokens) - {len(master_list['work_chunks']['small'])} chunks
"""
        
        for chunk in master_list['work_chunks']['small']:
            task_list_content += f"""
**{chunk['title']}**
- ID: {chunk['id']}
- Type: {chunk['type']}
- Priority: {chunk['priority']}
- Estimated Time: {chunk['estimated_time']}
- Status: {chunk['status']}
- Description: {chunk['description']}

"""
        
        task_list_content += f"""
### Medium Agents (5K tokens) - {len(master_list['work_chunks']['medium'])} chunks
"""
        
        for chunk in master_list['work_chunks']['medium']:
            task_list_content += f"""
**{chunk['title']}**
- ID: {chunk['id']}
- Type: {chunk['type']}
- Priority: {chunk['priority']}
- Estimated Time: {chunk['estimated_time']}
- Status: {chunk['status']}
- Description: {chunk['description']}

"""
        
        task_list_content += f"""
### Large Agents (15K tokens) - {len(master_list['work_chunks']['large'])} chunks
"""
        
        for chunk in master_list['work_chunks']['large']:
            task_list_content += f"""
**{chunk['title']}**
- ID: {chunk['id']}
- Type: {chunk['type']}
- Priority: {chunk['priority']}
- Estimated Time: {chunk['estimated_time']}
- Status: {chunk['status']}
- Description: {chunk['description']}

"""
        
        task_list_content += f"""
### XLarge Agents (50K tokens) - {len(master_list['work_chunks']['xlarge'])} chunks
"""
        
        for chunk in master_list['work_chunks']['xlarge']:
            task_list_content += f"""
**{chunk['title']}**
- ID: {chunk['id']}
- Type: {chunk['type']}
- Priority: {chunk['priority']}
- Estimated Time: {chunk['estimated_time']}
- Status: {chunk['status']}
- Description: {chunk['description']}

"""
        
        task_list_content += f"""
### Unlimited Agents (100K+ tokens) - {len(master_list['work_chunks']['unlimited'])} chunks
"""
        
        for chunk in master_list['work_chunks']['unlimited']:
            task_list_content += f"""
**{chunk['title']}**
- ID: {chunk['id']}
- Type: {chunk['type']}
- Priority: {chunk['priority']}
- Estimated Time: {chunk['estimated_time']}
- Status: {chunk['status']}
- Description: {chunk['description']}

"""
        
        task_list_content += f"""
## HOW TO USE THIS TASK LIST

1. **Choose Your Size**: Pick chunks that match your token limit
2. **Pick by Priority**: Start with Priority 1 (Critical) items
3. **Mark Progress**: Update status as you complete chunks
4. **Report Completion**: Document what you accomplished

## STATUS CODES

- **pending**: Not started
- **in_progress**: Currently being worked on
- **completed**: Finished successfully
- **blocked**: Cannot proceed due to dependencies
- **failed**: Attempted but failed

---
*Generated by Log Consolidation and Chunking System*
*Exo-Suit V5.0 - Builder of Dreams*
"""
        
        # Save human-readable task list
        task_list_path = self.consolidation_dir / "MASTER_TASK_LIST.md"
        with open(task_list_path, 'w', encoding='utf-8') as f:
            f.write(task_list_content)
        
        print(f"Human-readable task list generated: {task_list_path}")
    
    def _setup_progress_tracking(self):
        """Set up progress tracking system"""
        print("Setting up progress tracking...")
        
        progress_file = self.consolidation_dir / "PROGRESS_TRACKER.json"
        
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                self.progress_tracker = json.load(f)
        else:
            self.progress_tracker = {
                'created': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'completed_chunks': [],
                'in_progress_chunks': [],
                'blocked_chunks': [],
                'failed_chunks': [],
                'completion_stats': {
                    'total_completed': 0,
                    'total_in_progress': 0,
                    'total_blocked': 0,
                    'total_failed': 0
                }
            }
        
        # Save initial progress tracker
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress_tracker, f, indent=2, ensure_ascii=False)
        
        print(f"Progress tracking set up: {progress_file}")
    
    def _calculate_priority_distribution(self):
        """Calculate distribution of priorities across all chunks"""
        priority_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for size_chunks in self.work_chunks.values():
            for chunk in size_chunks:
                priority = chunk.get('priority', 5)
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return priority_counts
    
    def _calculate_total_estimated_time(self):
        """Calculate total estimated time for all chunks"""
        total_time = 0
        
        for size_chunks in self.work_chunks.values():
            for chunk in size_chunks:
                time_str = chunk.get('estimated_time', '0')
                # Simple time parsing (could be enhanced)
                if 'hour' in time_str.lower():
                    total_time += 1
                elif 'day' in time_str.lower():
                    total_time += 8  # 8 hours per day
                elif 'week' in time_str.lower():
                    total_time += 40  # 40 hours per week
        
        return f"{total_time} hours"
    
    def _extract_markdown_summary(self, content: str) -> str:
        """Extract summary from markdown content"""
        lines = content.split('\n')
        summary_lines = []
        
        for line in lines[:20]:  # First 20 lines
            if line.strip() and not line.startswith('#'):
                summary_lines.append(line.strip())
                if len(' '.join(summary_lines)) > 200:
                    break
        
        return ' '.join(summary_lines)[:200] + ('...' if len(' '.join(summary_lines)) > 200 else '')
    
    def _extract_log_summary(self, content: str) -> str:
        """Extract summary from log content"""
        lines = content.split('\n')
        error_lines = [line for line in lines if 'ERROR' in line or 'WARNING' in line]
        
        if error_lines:
            return f"Log contains {len(error_lines)} errors/warnings. Last: {error_lines[-1][:100]}"
        else:
            return f"Log contains {len(lines)} lines, no errors found"
    
    def _extract_health_score(self, report_data: Dict) -> str:
        """Extract health score from report data"""
        if report_data['type'] == 'markdown':
            content = report_data['summary']
            # Look for health score pattern
            match = re.search(r'Health Score[:\s]*(\d+)/100', content, re.IGNORECASE)
            if match:
                return match.group(1)
        return 'Unknown'
    
    def _extract_phoenix_issues(self, report_data: Dict) -> List[Dict]:
        """Extract issues from Phoenix report"""
        # This would need to be enhanced based on actual Phoenix report structure
        return []
    
    def _extract_repair_roadmap(self, report_data: Dict) -> Dict:
        """Extract repair roadmap from Phoenix report"""
        # This would need to be enhanced based on actual Phoenix report structure
        return {}
    
    def _extract_scan_metrics(self, report_data: Dict) -> int:
        """Extract scanning metrics from report"""
        if report_data['type'] == 'markdown':
            content = report_data['summary']
            # Look for files scanned pattern
            match = re.search(r'(\d+(?:,\d+)*)\s*files?\s*scanned', content, re.IGNORECASE)
            if match:
                return int(match.group(1).replace(',', ''))
        return 0
    
    def _extract_unicode_issues(self, report_data: Dict) -> int:
        """Extract Unicode issues count from report"""
        if report_data['type'] == 'markdown':
            content = report_data['summary']
            # Look for Unicode issues pattern
            match = re.search(r'(\d+(?:,\d+)*)\s*unicode', content, re.IGNORECASE)
            if match:
                return int(match.group(1).replace(',', ''))
        return 0
    
    def _extract_content_issues(self, report_data: Dict) -> int:
        """Extract content issues count from report"""
        if report_data['type'] == 'markdown':
            content = report_data['summary']
            # Look for content issues pattern
            match = re.search(r'(\d+(?:,\d+)*)\s*content', content, re.IGNORECASE)
            if match:
                return int(match.group(1).replace(',', ''))
        return 0
    
    def _extract_vision_metrics(self, report_data: Dict) -> Dict:
        """Extract vision metrics from report"""
        # This would need to be enhanced based on actual vision gap report structure
        return {}
    
    def _extract_gap_metrics(self, report_data: Dict) -> Dict:
        """Extract gap metrics from report"""
        # This would need to be enhanced based on actual vision gap report structure
        return {}
    
    def _extract_alignment_score(self, report_data: Dict) -> str:
        """Extract alignment score from report"""
        if report_data['type'] == 'markdown':
            content = report_data['summary']
            # Look for alignment score pattern
            match = re.search(r'alignment[:\s]*(\d+)/100', content, re.IGNORECASE)
            if match:
                return match.group(1)
        return 'Unknown'

def main():
    """Main execution function"""
    chunker = LogConsolidationChunker()
    work_chunks = chunker.run_consolidation()
    
    print("\n=== CONSOLIDATION COMPLETE ===")
    print(f"Total work chunks created: {sum(len(chunks) for chunks in work_chunks.values())}")
    print(f"Chunks by size:")
    for size, chunks in work_chunks.items():
        print(f"  {size}: {len(chunks)} chunks")
    print(f"Consolidated work directory: {chunker.consolidation_dir}")
    
    return work_chunks

if __name__ == "__main__":
    main()
