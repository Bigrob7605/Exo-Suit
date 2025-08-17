#!/usr/bin/env python3
"""
ContextChunker.py - Smart Context Chunking System
================================================

Breaks down massive context files into digestible chunks that ANY agent can read with ease.
This enables 128k agents to access 1M+ token context through intelligent chunking.

Key Features:
- Smart chunking by functionality and size
- Agent-friendly navigation system
- Context indexing and search
- Progressive disclosure (start small, expand as needed)
"""

import json
import time
import math
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib

class ContextChunker:
    """
    Smart context chunking system for agent accessibility.
    
    Converts massive context files into:
    1. Overview chunks (summary, architecture)
    2. Functional chunks (core systems, toolbox, etc.)
    3. Detailed chunks (specific components)
    4. Navigation index for easy access
    """
    
    def __init__(self, context_dir: Path = None):
        self.context_dir = context_dir or Path("context")
        self.chunks_dir = self.context_dir / "chunks"
        self.chunks_dir.mkdir(exist_ok=True)
        
        # Chunking strategy
        self.max_chunk_size = 100000  # ~100k tokens per chunk
        self.overview_chunk_size = 50000  # Smaller overview chunks
        
        # Chunk categories
        self.chunk_categories = {
            'overview': 'System Overview & Architecture',
            'core_systems': 'V5 Core Systems',
            'legacy_integration': 'Legacy V1-V4 Integration',
            'toolbox': 'Toolbox Systems',
            'dependencies': 'Dependencies & Relationships',
            'code_samples': 'Code Samples & Functions',
            'configuration': 'Configuration & Environment',
            'documentation': 'Documentation & Guides'
        }
    
    def chunk_context_file(self, context_file: Path) -> Dict[str, Any]:
        """Break down massive context file into digestible chunks."""
        print(f"[INFO] Starting context chunking of: {context_file}")
        
        # Load context data
        with open(context_file, 'r', encoding='utf-8') as f:
            context_data = json.load(f)
        
        # Phase 1: Create overview chunks
        overview_chunks = self._create_overview_chunks(context_data)
        
        # Phase 2: Create functional chunks
        functional_chunks = self._create_functional_chunks(context_data)
        
        # Phase 3: Create detailed chunks
        detailed_chunks = self._create_detailed_chunks(context_data)
        
        # Phase 4: Create navigation index
        navigation_index = self._create_navigation_index(
            overview_chunks, functional_chunks, detailed_chunks
        )
        
        # Phase 5: Save all chunks
        self._save_chunks(overview_chunks, functional_chunks, detailed_chunks, navigation_index)
        
        print(f"[INFO] Context chunking complete. Created {len(overview_chunks) + len(functional_chunks) + len(detailed_chunks)} chunks.")
        return navigation_index
    
    def _create_overview_chunks(self, context_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Create high-level overview chunks."""
        print("[INFO] Creating overview chunks...")
        
        chunks = {}
        
        # System Overview Chunk
        system_overview = {
            'chunk_type': 'overview',
            'chunk_id': 'system_overview',
            'title': 'Exo-Suit V5 System Overview',
            'description': 'High-level system architecture and statistics',
            'content': {
                'scan_timestamp': context_data.get('scan_timestamp'),
                'workspace_root': context_data.get('workspace_root'),
                'file_statistics': context_data.get('file_statistics'),
                'code_statistics': context_data.get('code_statistics'),
                'system_overview': context_data.get('system_overview')
            },
            'estimated_tokens': self._estimate_tokens(context_data.get('file_statistics', {})),
            'related_chunks': ['core_systems', 'legacy_integration', 'toolbox']
        }
        chunks['system_overview'] = system_overview
        
        # Architecture Overview Chunk
        architecture_overview = {
            'chunk_type': 'overview',
            'chunk_id': 'architecture_overview',
            'title': 'System Architecture & Design',
            'description': 'High-level system design and component relationships',
            'content': {
                'core_components': [
                    'VisionGap Engine - Gap analysis and project alignment',
                    'GPU Push Engine - GPU acceleration and RAG capabilities',
                    'V5 Consolidation Master - System orchestration',
                    'Phoenix Recovery System - System recovery and health',
                    'Advanced Integration Layer - Legacy system integration'
                ],
                'system_layers': [
                    'Visual Layer - Mermaid diagrams and visualization',
                    'Cognitive Layer - RAG engine and AI processing',
                    'Operational Layer - Core operational scripts',
                    'Integration Layer - Cursor IDE integration'
                ]
            },
            'estimated_tokens': 2000,
            'related_chunks': ['core_systems', 'dependencies']
        }
        chunks['architecture_overview'] = architecture_overview
        
        return chunks
    
    def _create_functional_chunks(self, context_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Create functional system chunks."""
        print("[INFO] Creating functional chunks...")
        
        chunks = {}
        
        # Core Systems Chunk
        core_systems = context_data.get('relationships', {}).get('core_systems', [])
        if core_systems:
            core_chunk = {
                'chunk_type': 'core_systems',
                'chunk_id': 'v5_core_systems',
                'title': 'V5 Core Systems',
                'description': 'Main V5 operational systems and their capabilities',
                'content': {
                    'core_files': core_systems[:20],  # First 20 core files
                    'total_core_files': len(core_systems),
                    'key_systems': [
                        'VISIONGAP_ENGINE.py - Project vision analysis',
                        'PHASE_3_GPU_PUSH_ENGINE.py - GPU acceleration',
                        'V5_CONSOLIDATION_MASTER.py - System orchestration',
                        'PHOENIX_RECOVERY_SYSTEM_V5.py - Recovery systems',
                        'ADVANCED_INTEGRATION_LAYER_V5.py - Legacy integration'
                    ]
                },
                'estimated_tokens': self._estimate_tokens(core_systems),
                'related_chunks': ['system_overview', 'code_samples']
            }
            chunks['v5_core_systems'] = core_chunk
        
        # Legacy Integration Chunk
        legacy_files = [f for f in context_data.get('file_inventory', {}) 
                       if f.endswith('.ps1') and 'V4' in f]
        if legacy_files:
            legacy_chunk = {
                'chunk_type': 'legacy_integration',
                'chunk_id': 'legacy_v1_v4_systems',
                'title': 'Legacy V1-V4 Systems',
                'description': 'Legacy PowerShell systems being integrated into V5',
                'content': {
                    'legacy_files': legacy_files[:30],  # First 30 legacy files
                    'total_legacy_files': len(legacy_files),
                    'key_legacy_systems': [
                        'GPU-RAG-V4.ps1 - GPU-accelerated RAG system',
                        'gpu-accelerator.ps1 - GPU optimization',
                        'AgentExoSuitV4.ps1 - Main system controller',
                        'emoji-sentinel-v4.ps1 - Emoji detection',
                        'Scan-Secrets-V4.ps1 - Security scanning'
                    ]
                },
                'estimated_tokens': self._estimate_tokens(legacy_files),
                'related_chunks': ['v5_core_systems', 'dependencies']
            }
            chunks['legacy_v1_v4_systems'] = legacy_chunk
        
        return chunks
    
    def _create_detailed_chunks(self, context_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Create detailed component chunks."""
        print("[INFO] Creating detailed chunks...")
        
        chunks = {}
        
        # Code Structure Chunk
        code_structure = context_data.get('code_structure', {})
        if code_structure:
            # Split code structure into manageable chunks
            code_files = list(code_structure.keys())
            chunk_size = 50  # 50 files per chunk
            
            for i in range(0, len(code_files), chunk_size):
                chunk_files = code_files[i:i + chunk_size]
                chunk_id = f'code_structure_{i//chunk_size + 1}'
                
                chunk_data = {
                    'chunk_type': 'code_samples',
                    'chunk_id': chunk_id,
                    'title': f'Code Structure Analysis - Part {i//chunk_size + 1}',
                    'description': f'Code analysis for files {i+1}-{min(i+chunk_size, len(code_files))}',
                    'content': {
                        'files_analyzed': chunk_files,
                        'structure_data': {f: code_structure[f] for f in chunk_files if f in code_structure}
                    },
                    'estimated_tokens': self._estimate_tokens(chunk_files),
                    'related_chunks': ['v5_core_systems', 'legacy_v1_v4_systems']
                }
                chunks[chunk_id] = chunk_data
        
        # Dependencies Chunk
        dependencies = context_data.get('dependencies', {})
        if dependencies:
            deps_chunk = {
                'chunk_type': 'dependencies',
                'chunk_id': 'system_dependencies',
                'title': 'System Dependencies & Relationships',
                'description': 'Import/export relationships and system dependencies',
                'content': {
                    'dependency_map': dependencies,
                    'total_dependencies': len(dependencies)
                },
                'estimated_tokens': self._estimate_tokens(dependencies),
                'related_chunks': ['v5_core_systems', 'architecture_overview']
            }
            chunks['system_dependencies'] = deps_chunk
        
        return chunks
    
    def _create_navigation_index(self, overview_chunks: Dict, functional_chunks: Dict, 
                                detailed_chunks: Dict) -> Dict[str, Any]:
        """Create navigation index for easy chunk access."""
        print("[INFO] Creating navigation index...")
        
        navigation = {
            'index_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_chunks': len(overview_chunks) + len(functional_chunks) + len(detailed_chunks),
            'chunk_categories': self.chunk_categories,
            'recommended_reading_order': [
                'system_overview',
                'architecture_overview',
                'v5_core_systems',
                'legacy_v1_v4_systems',
                'system_dependencies'
            ],
            'chunks_by_category': {
                'overview': list(overview_chunks.keys()),
                'core_systems': [k for k, v in functional_chunks.items() if v['chunk_type'] == 'core_systems'],
                'legacy_integration': [k for k, v in functional_chunks.items() if v['chunk_type'] == 'legacy_integration'],
                'code_samples': [k for k, v in detailed_chunks.items() if v['chunk_type'] == 'code_samples'],
                'dependencies': [k for k, v in detailed_chunks.items() if v['chunk_type'] == 'dependencies']
            },
            'chunk_details': {
                **overview_chunks,
                **functional_chunks,
                **detailed_chunks
            }
        }
        
        return navigation
    
    def _save_chunks(self, overview_chunks: Dict, functional_chunks: Dict, 
                     detailed_chunks: Dict, navigation_index: Dict[str, Any]):
        """Save all chunks to disk."""
        print("[INFO] Saving chunks to disk...")
        
        # Save individual chunks
        all_chunks = {**overview_chunks, **functional_chunks, **detailed_chunks}
        
        for chunk_id, chunk_data in all_chunks.items():
            chunk_file = self.chunks_dir / f"{chunk_id}.json"
            with open(chunk_file, 'w', encoding='utf-8') as f:
                json.dump(chunk_data, f, indent=2, ensure_ascii=False)
            print(f"[INFO] Saved chunk: {chunk_file}")
        
        # Save navigation index
        nav_file = self.chunks_dir / "NAVIGATION_INDEX.json"
        with open(nav_file, 'w', encoding='utf-8') as f:
            json.dump(navigation_index, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Saved navigation index: {nav_file}")
        
        # Create human-readable index
        self._create_human_readable_index(navigation_index)
    
    def _create_human_readable_index(self, navigation_index: Dict[str, Any]):
        """Create human-readable index for easy navigation."""
        # Safely get chunk details with fallbacks
        chunk_details = navigation_index.get('chunk_details', {})
        
        # Get chunk titles safely
        system_overview_title = chunk_details.get('system_overview', {}).get('title', 'System Overview')
        architecture_title = chunk_details.get('architecture_overview', {}).get('title', 'Architecture Overview')
        v5_core_title = chunk_details.get('v5_core_systems', {}).get('title', 'V5 Core Systems')
        legacy_title = chunk_details.get('legacy_v1_v4_systems', {}).get('title', 'Legacy V1-V4 Systems')
        deps_title = chunk_details.get('system_dependencies', {}).get('title', 'System Dependencies')
        
        index_md = f"""# Exo-Suit V5 Context Navigation Index

Generated: {navigation_index['index_timestamp']}
Total Chunks: {navigation_index['total_chunks']}

## ROCKET: **Recommended Reading Order**

1. **{system_overview_title}** - Start here for system overview
2. **{architecture_title}** - Understand system design
3. **{v5_core_title}** - Core V5 systems
4. **{legacy_title}** - Legacy integration
5. **{deps_title}** - System relationships

## FOLDER **Chunks by Category**

### **Overview Chunks**
{self._format_chunk_list(navigation_index['chunks_by_category']['overview'], chunk_details)}

### **Core Systems**
{self._format_chunk_list(navigation_index['chunks_by_category']['core_systems'], chunk_details)}

### **Legacy Integration**
{self._format_chunk_list(navigation_index['chunks_by_category']['legacy_integration'], chunk_details)}

### **Code Samples**
{self._format_chunk_list(navigation_index['chunks_by_category']['code_samples'], chunk_details)}

### **Dependencies**
{self._format_chunk_list(navigation_index['chunks_by_category']['dependencies'], chunk_details)}

## TARGET: **Usage Instructions**

**For 128k Agents:**
- Start with `system_overview.json` for basic understanding
- Use `architecture_overview.json` for system design
- Access specific chunks as needed

**For Larger Context Agents:**
- Load multiple chunks simultaneously
- Use navigation index for targeted access
- Combine chunks for comprehensive analysis

## MAGNIFYING_GLASS: **Chunk Details**

Each chunk contains:
- Clear title and description
- Estimated token count
- Related chunks for navigation
- Structured content for easy parsing

---
*Generated by ContextChunker.py - Making massive context accessible to all agents*
"""
        
        index_file = self.chunks_dir / "NAVIGATION_INDEX.md"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_md)
        
        print(f"[INFO] Created human-readable index: {index_file}")
    
    def _format_chunk_list(self, chunk_ids: List[str], chunk_details: Dict[str, Any]) -> str:
        """Format chunk list for markdown."""
        if not chunk_ids:
            return "- No chunks in this category"
        
        formatted = []
        for chunk_id in chunk_ids:
            if chunk_id in chunk_details:
                chunk = chunk_details[chunk_id]
                formatted.append(f"- **{chunk['title']}** (`{chunk_id}.json`) - {chunk['description']}")
        
        return '\n'.join(formatted)
    
    def _estimate_tokens(self, content: Any) -> int:
        """Estimate token count for content."""
        if isinstance(content, str):
            return len(content.split()) * 1.3  # Rough estimate: words * 1.3
        elif isinstance(content, (list, dict)):
            return len(str(content).split()) * 1.3
        else:
            return 1000  # Default estimate
    
    def get_chunk_for_agent(self, agent_context_limit: int, chunk_type: str = None) -> Dict[str, Any]:
        """Get appropriate chunk for agent based on context limit."""
        nav_file = self.chunks_dir / "NAVIGATION_INDEX.json"
        
        if not nav_file.exists():
            raise FileNotFoundError("Navigation index not found. Run chunking first.")
        
        with open(nav_file, 'r', encoding='utf-8') as f:
            navigation = json.load(f)
        
        # Find chunks that fit within agent's context limit
        suitable_chunks = []
        
        for chunk_id, chunk_data in navigation['chunk_details'].items():
            if chunk_type and chunk_data['chunk_type'] != chunk_type:
                continue
            
            if chunk_data['estimated_tokens'] <= agent_context_limit:
                suitable_chunks.append((chunk_id, chunk_data))
        
        if not suitable_chunks:
            # If no chunks fit, return the smallest overview chunk
            overview_chunks = [c for c in suitable_chunks if c[1]['chunk_type'] == 'overview']
            if overview_chunks:
                return min(overview_chunks, key=lambda x: x[1]['estimated_tokens'])[1]
            else:
                raise ValueError("No suitable chunks found for agent context limit")
        
        # Return the largest chunk that fits
        return max(suitable_chunks, key=lambda x: x[1]['estimated_tokens'])[1]

def main():
    """Main function to demonstrate ContextChunker capabilities."""
    chunker = ContextChunker()
    
    # Find the most recent context file
    context_files = list(chunker.context_dir.glob("COMPLETE_CONTEXT_*.json"))
    if not context_files:
        print("[ERROR] No context files found. Run ContextScanner first.")
        return
    
    latest_context = max(context_files, key=lambda f: f.stat().st_mtime)
    print(f"[INFO] Using context file: {latest_context}")
    
    # Chunk the context
    navigation_index = chunker.chunk_context_file(latest_context)
    
    print("\n" + "="*60)
    print("CONTEXT CHUNKING COMPLETE")
    print("="*60)
    print(f"Total Chunks Created: {navigation_index['total_chunks']}")
    print(f"Chunks Directory: {chunker.chunks_dir}")
    print(f"Navigation Index: {chunker.chunks_dir / 'NAVIGATION_INDEX.json'}")
    print("="*60)
    
    # Demonstrate agent access
    print("\n**Agent Access Examples:**")
    
    # 128k agent example
    try:
        chunk_128k = chunker.get_chunk_for_agent(128000, 'overview')
        print(f"128k Agent: {chunk_128k['title']} ({chunk_128k['estimated_tokens']} tokens)")
    except Exception as e:
        print(f"128k Agent: {e}")
    
    # 1M agent example
    try:
        chunk_1m = chunker.get_chunk_for_agent(1000000, 'core_systems')
        print(f"1M Agent: {chunk_1m['title']} ({chunk_1m['estimated_tokens']} tokens)")
    except Exception as e:
        print(f"1M Agent: {e}")
    
    print(f"\nComplete chunked context available in: {chunker.chunks_dir}")
    print("Any agent can now access the full Exo-Suit context!")

if __name__ == "__main__":
    main()
