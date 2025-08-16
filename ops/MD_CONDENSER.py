#!/usr/bin/env python3
"""
MD CONDENSER - Convert large logs/data into VisionGap Engine compatible markdown
Any agent can use this to create manageable markdown files under 2MB
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class MDCondenser:
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.output_dir = self.workspace_root / "vision_gap_data"
        self.output_dir.mkdir(exist_ok=True)
        
        # File size limits for different agent types
        self.size_limits = {
            'small': 1024 * 10,      # 10KB for small agents
            'medium': 1024 * 100,    # 100KB for medium agents
            'large': 1024 * 500,     # 500KB for large agents
            'xlarge': 1024 * 1024,   # 1MB for xlarge agents
            'unlimited': 1024 * 2048 # 2MB for unlimited agents
        }
    
    def condense_file_to_md(self, file_path: str, agent_size: str = 'medium', target_size: int = None):
        """Condense any file into a markdown summary for VisionGap Engine"""
        if not target_size:
            target_size = self.size_limits.get(agent_size, self.size_limits['medium'])
        
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return None
        
        print(f"Condensing {file_path} to markdown (target: {target_size/1024:.1f}KB)")
        
        # Read file content
        try:
            if file_path.suffix.lower() == '.json':
                content = self._condense_json_file(file_path, target_size)
            elif file_path.suffix.lower() in ['.txt', '.log']:
                content = self._condense_text_file(file_path, target_size)
            elif file_path.suffix.lower() == '.md':
                content = self._condense_markdown_file(file_path, target_size)
            else:
                content = self._condense_generic_file(file_path, target_size)
        except Exception as e:
            print(f"Error condensing file: {e}")
            return None
        
        # Create markdown output
        output_filename = f"condensed_{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        output_path = self.output_dir / output_filename
        
        markdown_content = self._create_markdown_summary(file_path, content, agent_size)
        
        # Check size and trim if needed
        while len(markdown_content.encode('utf-8')) > target_size:
            markdown_content = self._trim_content(markdown_content, target_size)
        
        # Write output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        final_size = len(markdown_content.encode('utf-8'))
        print(f"✅ Condensed to {output_path} ({final_size/1024:.1f}KB)")
        
        return str(output_path)
    
    def _condense_json_file(self, file_path: Path, target_size: int) -> Dict:
        """Condense JSON files intelligently"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract key information
        condensed = {
            'file_info': {
                'original_path': str(file_path),
                'original_size': file_path.stat().st_size,
                'condensed_at': datetime.now().isoformat()
            },
            'summary': {},
            'key_data': {}
        }
        
        # Create intelligent summary based on content
        if isinstance(data, dict):
            condensed['summary'] = {
                'type': 'json_object',
                'keys': list(data.keys()),
                'total_keys': len(data.keys())
            }
            
            # Extract key data (limit to fit target size)
            for key, value in data.items():
                if len(str(condensed)) < target_size * 0.8:  # Leave room for markdown
                    condensed['key_data'][key] = self._summarize_value(value)
        
        return condensed
    
    def _condense_text_file(self, file_path: Path, target_size: int) -> Dict:
        """Condense text/log files intelligently"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        condensed = {
            'file_info': {
                'original_path': str(file_path),
                'original_size': file_path.stat().st_size,
                'total_lines': len(lines),
                'condensed_at': datetime.now().isoformat()
            },
            'summary': {
                'type': 'text_file',
                'first_lines': lines[:10],
                'last_lines': lines[-10:] if len(lines) > 20 else [],
                'key_patterns': self._extract_key_patterns(content)
            }
        }
        
        return condensed
    
    def _condense_markdown_file(self, file_path: Path, target_size: int) -> Dict:
        """Condense markdown files intelligently"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Extract headers and key sections
        headers = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
        sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        
        condensed = {
            'file_info': {
                'original_path': str(file_path),
                'original_size': file_path.stat().st_size,
                'condensed_at': datetime.now().isoformat()
            },
            'summary': {
                'type': 'markdown_file',
                'main_title': headers[0] if headers else 'Untitled',
                'sections': sections[:20],  # Limit sections
                'total_sections': len(sections)
            }
        }
        
        return condensed
    
    def _condense_generic_file(self, file_path: Path, target_size: int) -> Dict:
        """Condense any other file type"""
        file_size = file_path.stat().st_size
        
        condensed = {
            'file_info': {
                'original_path': str(file_path),
                'original_size': file_size,
                'file_type': file_path.suffix,
                'condensed_at': datetime.now().isoformat()
            },
            'summary': {
                'type': 'generic_file',
                'size_category': self._categorize_size(file_size)
            }
        }
        
        return condensed
    
    def _summarize_value(self, value) -> Any:
        """Create a summary of a value that fits size constraints"""
        if isinstance(value, str):
            return value[:200] + "..." if len(value) > 200 else value
        elif isinstance(value, (list, tuple)):
            return f"List with {len(value)} items: {str(value[:5])}"
        elif isinstance(value, dict):
            return f"Dict with {len(value)} keys: {list(value.keys())[:5]}"
        else:
            return str(value)[:100]
    
    def _extract_key_patterns(self, content: str) -> List[str]:
        """Extract key patterns from text content"""
        patterns = []
        
        # Look for common patterns
        if 'ERROR' in content.upper():
            patterns.append('Contains error messages')
        if 'WARNING' in content.upper():
            patterns.append('Contains warnings')
        if 'INFO' in content.upper():
            patterns.append('Contains info messages')
        if 'DEBUG' in content.upper():
            patterns.append('Contains debug output')
        
        return patterns[:5]  # Limit patterns
    
    def _categorize_size(self, size_bytes: int) -> str:
        """Categorize file size"""
        if size_bytes < 1024:
            return "tiny"
        elif size_bytes < 1024 * 1024:
            return "small"
        elif size_bytes < 10 * 1024 * 1024:
            return "medium"
        else:
            return "large"
    
    def _create_markdown_summary(self, file_path: Path, content: Dict, agent_size: str) -> str:
        """Create markdown summary from condensed content"""
        md = f"""# Condensed Summary: {file_path.name}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Agent Size**: {agent_size.upper()}  
**Original File**: {file_path}  
**Original Size**: {file_path.stat().st_size / 1024:.1f}KB  

---

## File Information
- **Path**: `{content['file_info']['original_path']}`
- **Original Size**: {content['file_info']['original_size'] / 1024:.1f}KB
- **Condensed At**: {content['file_info']['condensed_at']}

## Summary
- **Type**: {content['summary']['type']}
"""
        
        # Add type-specific content
        if content['summary']['type'] == 'json_object':
            md += f"- **Total Keys**: {content['summary']['total_keys']}\n"
            md += f"- **Key Names**: {', '.join(content['summary']['keys'][:10])}\n"
        elif content['summary']['type'] == 'text_file':
            md += f"- **Total Lines**: {content['summary']['total_lines']}\n"
            md += f"- **Key Patterns**: {', '.join(content['summary']['key_patterns'])}\n"
        elif content['summary']['type'] == 'markdown_file':
            md += f"- **Main Title**: {content['summary']['main_title']}\n"
            md += f"- **Total Sections**: {content['summary']['total_sections']}\n"
        
        md += "\n## Key Data\n"
        
        # Add key data if available
        if 'key_data' in content:
            for key, value in content['key_data'].items():
                md += f"### {key}\n```\n{value}\n```\n\n"
        
        md += "---\n*This condensed summary was created for VisionGap Engine compatibility*"
        
        return md
    
    def _trim_content(self, content: str, target_size: int) -> str:
        """Trim content to fit target size"""
        # Simple trimming - remove sections from the end
        sections = content.split('\n## ')
        if len(sections) > 1:
            return '\n## '.join(sections[:-1]) + "\n---\n*Content trimmed to fit size limit*"
        return content[:target_size] + "\n*Content trimmed to fit size limit*"
    
    def condense_directory(self, dir_path: str, agent_size: str = 'medium'):
        """Condense all files in a directory"""
        dir_path = Path(dir_path)
        if not dir_path.exists() or not dir_path.is_dir():
            print(f"Directory not found: {dir_path}")
            return
        
        print(f"Condensing directory: {dir_path}")
        
        condensed_files = []
        for file_path in dir_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.json', '.txt', '.log', '.md']:
                try:
                    output = self.condense_file_to_md(str(file_path), agent_size)
                    if output:
                        condensed_files.append(output)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        print(f"✅ Condensed {len(condensed_files)} files")
        return condensed_files

def main():
    """Main function for command line usage"""
    import sys
    
    condenser = MDCondenser()
    
    if len(sys.argv) < 2:
        print("Usage: python MD_CONDENSER.py <file_or_directory> [agent_size]")
        print("Agent sizes: small, medium, large, xlarge, unlimited")
        print("Example: python MD_CONDENSER.py logs/ medium")
        return
    
    target = sys.argv[1]
    agent_size = sys.argv[2] if len(sys.argv) > 2 else 'medium'
    
    if Path(target).is_file():
        condenser.condense_file_to_md(target, agent_size)
    elif Path(target).is_dir():
        condenser.condense_directory(target, agent_size)
    else:
        print(f"Target not found: {target}")

if __name__ == "__main__":
    main()
