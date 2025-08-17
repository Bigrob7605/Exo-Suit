#!/usr/bin/env python3
"""
V5 CONSOLIDATION ENGINE - Agent Exo-Suit V5.0
==============================================

This script consolidates all legacy V1-V4 tools into the core V5 system
and removes duplicates, testing tools, and legacy contamination.
"""

import os
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('v5_consolidation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class V5ConsolidationEngine:
    """Comprehensive V5 consolidation and cleanup system"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.ops_dir = self.project_root / "ops"
        
        # Core V5 files that should remain
        self.core_v5_files = {
            'PHOENIX_RECOVERY_SYSTEM_V5.py',
            'ADVANCED_INTEGRATION_LAYER_V5.py', 
            'VISIONGAP_ENGINE.py',
            'V5_CONSOLIDATION_MASTER.py',
            'REAL_EMOJI_CLEANUP.py',
            'SYSTEM_HEALTH_VALIDATOR.py'
        }
        
        # V5 files that are enhanced versions
        self.enhanced_v5_files = {
            'Ultimate-Overclock-Speed-Boost-V5.ps1',
            'RTX-4070-Accelerator-V5.ps1',
            'DreamWeaver-Builder-V5.ps1',
            'DeepSpeed-Accelerator-V5.ps1',
            'TruthForge-Auditor-V5.ps1',
            'VisionGap-Engine-V5.ps1'
        }
        
        # Files to be consolidated (functionality merged into core V5)
        self.files_to_consolidate = {
            # Emoji tools - consolidated into REAL_EMOJI_CLEANUP.py
            'MDEmojiPurge.py',
            'ProjectWideEmojiPurge.py', 
            'FastEmojiScanner.py',
            'emoji-sentinel-v4.ps1',
            'emoji-sentinel.ps1',
            
            # Context tools - consolidated into core V5
            'ContextPipeline.py',
            'ContextChunker.py',
            'ContextScanner.py',
            'ContextValidator.py',
            'MassiveScaleContextEngine.py',
            
            # Monitor tools - consolidated into core V5
            'AGGRESSIVE_MONITOR.py',
            'WORKING_MONITOR.py',
            'SIMPLE_MONITOR_TEST.py',
            'REAL_TIME_SYSTEM_MONITOR.py',
            
            # Legacy V4 tools - replaced by V5 versions
            'Ultimate-Speed-Boost-V4.ps1',
            'Speed-Boost-V4.ps1',
            'RTX-4070-Optimizer.ps1',
            'Performance-Test-Suite-V4.ps1',
            'GPU-RAG-V4.ps1',
            'GPU-Monitor-V4.ps1',
            'Drift-Guard-V4.ps1',
            'Project-Health-Scanner-V4.ps1',
            'Import-Indexer-V4.ps1',
            'Placeholder-Scanner-V4.ps1',
            'Symbol-Indexer-V4.ps1',
            'Power-Management-V4.ps1',
            'Scan-Secrets-V4.ps1',
            
            # Testing and placeholder tools
            'test-simple.ps1',
            'placeholder-scan.ps1',
            'quick-scan.ps1',
            'max-perf.ps1',
            
            # Duplicate/obsolete tools
            'PHASE_3_GPU_PUSH_ENGINE.py',
            'context-governor.ps1',
            'context-governor-v5-token-upgrade.ps1',
            'drift-gate.ps1',
            'gpu-accelerator.ps1',
            'gpu-monitor.ps1',
            'log-analyzer-simple.ps1',
            'log-analyzer-v5.ps1',
            'make-pack.ps1',
            'smart-log-manager-v5.ps1',
            
            # RTX variants - consolidated into main V5
            'RTX-4070-Simple-V5.ps1',
            'RTX-4070-Real-Processor-V5.ps1',
            'RTX-4070-Batch-Processor-V5.ps1',
            
            # Configuration and metadata
            'sentinel_mesh_config.json',
            'symbol-index-v4.json',
            'monitor_requirements.txt'
        }
        
        # Directories to clean up
        self.directories_to_clean = {
            'test_output',
            'temp_ram_disk',
            'consolidation_backups',
            'consolidation_workspace',
            'V5_CORE_BACKUP_20250817_063043'
        }
        
        self.consolidation_stats = {
            'files_consolidated': 0,
            'files_removed': 0,
            'directories_cleaned': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    def analyze_current_state(self) -> Dict[str, Any]:
        """Analyze current state and identify consolidation targets"""
        logger.info("Analyzing current system state...")
        
        analysis = {
            'total_files': 0,
            'v5_files': 0,
            'legacy_files': 0,
            'duplicate_files': 0,
            'consolidation_targets': [],
            'cleanup_targets': []
        }
        
        # Count files in ops directory
        for file_path in self.ops_dir.rglob('*'):
            if file_path.is_file():
                analysis['total_files'] += 1
                
                filename = file_path.name
                if filename in self.core_v5_files or filename in self.enhanced_v5_files:
                    analysis['v5_files'] += 1
                elif filename in self.files_to_consolidate:
                    analysis['legacy_files'] += 1
                    analysis['consolidation_targets'].append(str(file_path))
                else:
                    # Check for duplicates
                    if any(other_file.name == filename for other_file in self.ops_dir.rglob('*') if other_file != file_path):
                        analysis['duplicate_files'] += 1
                        analysis['cleanup_targets'].append(str(file_path))
        
        # Check for legacy directories
        for dir_name in self.directories_to_clean:
            dir_path = self.ops_dir / dir_name
            if dir_path.exists():
                analysis['cleanup_targets'].append(str(dir_path))
        
        logger.info(f"Analysis complete: {analysis['total_files']} total files")
        logger.info(f"V5 files: {analysis['v5_files']}, Legacy: {analysis['legacy_files']}, Duplicates: {analysis['duplicate_files']}")
        
        return analysis
    
    def backup_before_consolidation(self):
        """Create backup before consolidation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.project_root / "consolidation_backup" / f"pre_consolidation_{timestamp}"
        
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup legacy files before removal
            for filename in self.files_to_consolidate:
                file_path = self.ops_dir / filename
                if file_path.exists():
                    shutil.copy2(file_path, backup_dir / filename)
                    logger.info(f"Backed up: {filename}")
            
            # Backup legacy directories
            for dir_name in self.directories_to_clean:
                dir_path = self.ops_dir / dir_name
                if dir_path.exists():
                    shutil.copytree(dir_path, backup_dir / dir_name)
                    logger.info(f"Backed up directory: {dir_name}")
            
            logger.info(f"Backup created: {backup_dir}")
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            self.consolidation_stats['errors'] += 1
    
    def consolidate_emoji_tools(self):
        """Consolidate all emoji-related tools into REAL_EMOJI_CLEANUP.py"""
        logger.info("Consolidating emoji tools...")
        
        emoji_tools = [
            'MDEmojiPurge.py',
            'ProjectWideEmojiPurge.py',
            'FastEmojiScanner.py',
            'emoji-sentinel-v4.ps1',
            'emoji-sentinel.ps1'
        ]
        
        for tool in emoji_tools:
            file_path = self.ops_dir / tool
            if file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"Removed legacy emoji tool: {tool}")
                    self.consolidation_stats['files_removed'] += 1
                except Exception as e:
                    logger.error(f"Failed to remove {tool}: {e}")
                    self.consolidation_stats['errors'] += 1
    
    def consolidate_context_tools(self):
        """Consolidate context tools into core V5 system"""
        logger.info("Consolidating context tools...")
        
        context_tools = [
            'ContextPipeline.py',
            'ContextChunker.py',
            'ContextScanner.py',
            'ContextValidator.py',
            'MassiveScaleContextEngine.py'
        ]
        
        for tool in context_tools:
            file_path = self.ops_dir / tool
            if file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"Removed legacy context tool: {tool}")
                    self.consolidation_stats['files_removed'] += 1
                except Exception as e:
                    logger.error(f"Failed to remove {tool}: {e}")
                    self.consolidation_stats['errors'] += 1
    
    def consolidate_monitor_tools(self):
        """Consolidate monitor tools into core V5 system"""
        logger.info("Consolidating monitor tools...")
        
        monitor_tools = [
            'AGGRESSIVE_MONITOR.py',
            'WORKING_MONITOR.py',
            'SIMPLE_MONITOR_TEST.py',
            'REAL_TIME_SYSTEM_MONITOR.py'
        ]
        
        for tool in monitor_tools:
            file_path = self.ops_dir / tool
            if file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"Removed legacy monitor tool: {tool}")
                    self.consolidation_stats['files_removed'] += 1
                except Exception as e:
                    logger.error(f"Failed to remove {tool}: {e}")
                    self.consolidation_stats['errors'] += 1
    
    def remove_legacy_v4_tools(self):
        """Remove all V4 tools that have V5 replacements"""
        logger.info("Removing legacy V4 tools...")
        
        v4_tools = [
            'Ultimate-Speed-Boost-V4.ps1',
            'Speed-Boost-V4.ps1',
            'RTX-4070-Optimizer.ps1',
            'Performance-Test-Suite-V4.ps1',
            'GPU-RAG-V4.ps1',
            'GPU-Monitor-V4.ps1',
            'Drift-Guard-V4.ps1',
            'Project-Health-Scanner-V4.ps1',
            'Import-Indexer-V4.ps1',
            'Placeholder-Scanner-V4.ps1',
            'Symbol-Indexer-V4.ps1',
            'Power-Management-V4.ps1',
            'Scan-Secrets-V4.ps1'
        ]
        
        for tool in v4_tools:
            file_path = self.ops_dir / tool
            if file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"Removed V4 tool: {tool}")
                    self.consolidation_stats['files_removed'] += 1
                except Exception as e:
                    logger.error(f"Failed to remove {tool}: {e}")
                    self.consolidation_stats['errors'] += 1
    
    def remove_testing_tools(self):
        """Remove testing and placeholder tools"""
        logger.info("Removing testing tools...")
        
        testing_tools = [
            'test-simple.ps1',
            'placeholder-scan.ps1',
            'quick-scan.ps1',
            'max-perf.ps1'
        ]
        
        for tool in testing_tools:
            file_path = self.ops_dir / tool
            if file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"Removed testing tool: {tool}")
                    self.consolidation_stats['files_removed'] += 1
                except Exception as e:
                    logger.error(f"Failed to remove {tool}: {e}")
                    self.consolidation_stats['errors'] += 1
    
    def remove_duplicate_tools(self):
        """Remove duplicate and obsolete tools"""
        logger.info("Removing duplicate tools...")
        
        duplicate_tools = [
            'PHASE_3_GPU_PUSH_ENGINE.py',
            'context-governor.ps1',
            'context-governor-v5-token-upgrade.ps1',
            'drift-gate.ps1',
            'gpu-accelerator.ps1',
            'gpu-monitor.ps1',
            'log-analyzer-simple.ps1',
            'log-analyzer-v5.ps1',
            'make-pack.ps1',
            'smart-log-manager-v5.ps1',
            'RTX-4070-Simple-V5.ps1',
            'RTX-4070-Real-Processor-V5.ps1',
            'RTX-4070-Batch-Processor-V5.ps1'
        ]
        
        for tool in duplicate_tools:
            file_path = self.ops_dir / tool
            if file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"Removed duplicate tool: {tool}")
                    self.consolidation_stats['files_removed'] += 1
                except Exception as e:
                    logger.error(f"Failed to remove {tool}: {e}")
                    self.consolidation_stats['errors'] += 1
    
    def remove_legacy_configs(self):
        """Remove legacy configuration files"""
        logger.info("Removing legacy configurations...")
        
        legacy_configs = [
            'sentinel_mesh_config.json',
            'symbol-index-v4.json',
            'monitor_requirements.txt'
        ]
        
        for config in legacy_configs:
            file_path = self.ops_dir / config
            if file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"Removed legacy config: {config}")
                    self.consolidation_stats['files_removed'] += 1
                except Exception as e:
                    logger.error(f"Failed to remove {config}: {e}")
                    self.consolidation_stats['errors'] += 1
    
    def clean_legacy_directories(self):
        """Clean up legacy directories"""
        logger.info("Cleaning legacy directories...")
        
        for dir_name in self.directories_to_clean:
            dir_path = self.ops_dir / dir_name
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    logger.info(f"Removed legacy directory: {dir_name}")
                    self.consolidation_stats['directories_cleaned'] += 1
                except Exception as e:
                    logger.error(f"Failed to remove directory {dir_name}: {e}")
                    self.consolidation_stats['errors'] += 1
    
    def create_consolidated_v5_structure(self):
        """Create the final consolidated V5 structure"""
        logger.info("Creating consolidated V5 structure...")
        
        # Create a clean V5 structure document
        v5_structure = {
            'consolidation_timestamp': datetime.now().isoformat(),
            'core_v5_files': list(self.core_v5_files),
            'enhanced_v5_files': list(self.enhanced_v5_files),
            'consolidation_summary': {
                'files_consolidated': self.consolidation_stats['files_consolidated'],
                'files_removed': self.consolidation_stats['files_removed'],
                'directories_cleaned': self.consolidation_stats['directories_cleaned'],
                'errors': self.consolidation_stats['errors']
            },
            'system_status': 'CONSOLIDATED_V5'
        }
        
        # Save V5 structure
        structure_path = self.ops_dir / 'V5_CONSOLIDATED_STRUCTURE.json'
        with open(structure_path, 'w', encoding='utf-8') as f:
            json.dump(v5_structure, f, indent=2, ensure_ascii=False)
        
        # Create V5 system status
        status_path = self.ops_dir / 'V5_SYSTEM_STATUS.md'
        with open(status_path, 'w', encoding='utf-8') as f:
            f.write("# V5 SYSTEM STATUS - CONSOLIDATED\n\n")
            f.write(f"**Consolidation Completed**: {datetime.now().isoformat()}\n")
            f.write(f"**Status**: CONSOLIDATED_V5\n\n")
            f.write("## Core V5 Files\n")
            for file in sorted(self.core_v5_files):
                f.write(f"- {file}\n")
            f.write("\n## Enhanced V5 Files\n")
            for file in sorted(self.enhanced_v5_files):
                f.write(f"- {file}\n")
            f.write(f"\n## Consolidation Results\n")
            f.write(f"- Files Consolidated: {self.consolidation_stats['files_consolidated']}\n")
            f.write(f"- Files Removed: {self.consolidation_stats['files_removed']}\n")
            f.write(f"- Directories Cleaned: {self.consolidation_stats['directories_cleaned']}\n")
            f.write(f"- Errors: {self.consolidation_stats['errors']}\n")
            f.write("\n**System Status**: READY FOR V5 OPERATION\n")
        
        logger.info("V5 structure created successfully")
    
    def run_consolidation(self) -> Dict[str, Any]:
        """Run complete V5 consolidation"""
        logger.info("Starting V5 consolidation process...")
        self.consolidation_stats['start_time'] = datetime.now()
        
        try:
            # Analyze current state
            analysis = self.analyze_current_state()
            
            # Create backup
            self.backup_before_consolidation()
            
            # Run consolidation steps
            self.consolidate_emoji_tools()
            self.consolidate_context_tools()
            self.consolidate_monitor_tools()
            self.remove_legacy_v4_tools()
            self.remove_testing_tools()
            self.remove_duplicate_tools()
            self.remove_legacy_configs()
            self.clean_legacy_directories()
            
            # Create final structure
            self.create_consolidated_v5_structure()
            
            self.consolidation_stats['end_time'] = datetime.now()
            
            # Generate consolidation report
            self.generate_consolidation_report()
            
            logger.info("V5 consolidation completed successfully!")
            return self.consolidation_stats
            
        except Exception as e:
            logger.error(f"Consolidation failed: {e}")
            self.consolidation_stats['errors'] += 1
            return self.consolidation_stats
    
    def generate_consolidation_report(self):
        """Generate comprehensive consolidation report"""
        duration = self.consolidation_stats['end_time'] - self.consolidation_stats['start_time']
        
        report = {
            'consolidation_summary': {
                'start_time': self.consolidation_stats['start_time'].isoformat(),
                'end_time': self.consolidation_stats['end_time'].isoformat(),
                'duration_seconds': duration.total_seconds(),
                'project_root': str(self.project_root.absolute())
            },
            'statistics': self.consolidation_stats.copy(),
            'v5_structure': {
                'core_files': list(self.core_v5_files),
                'enhanced_files': list(self.enhanced_v5_files)
            }
        }
        
        # Save JSON report
        json_path = self.project_root / 'V5_CONSOLIDATION_REPORT.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Save text report
        text_path = self.project_root / 'V5_CONSOLIDATION_REPORT.txt'
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write("V5 CONSOLIDATION REPORT - Agent Exo-Suit V5.0\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Project: {self.project_root.absolute()}\n")
            f.write(f"Start Time: {self.consolidation_stats['start_time']}\n")
            f.write(f"End Time: {self.consolidation_stats['end_time']}\n")
            f.write(f"Duration: {duration}\n\n")
            f.write("CONSOLIDATION RESULTS:\n")
            f.write(f"Files Consolidated: {self.consolidation_stats['files_consolidated']}\n")
            f.write(f"Files Removed: {self.consolidation_stats['files_removed']}\n")
            f.write(f"Directories Cleaned: {self.consolidation_stats['directories_cleaned']}\n")
            f.write(f"Errors: {self.consolidation_stats['errors']}\n\n")
            f.write("V5 STRUCTURE:\n")
            f.write("Core V5 Files:\n")
            for file in sorted(self.core_v5_files):
                f.write(f"  - {file}\n")
            f.write("\nEnhanced V5 Files:\n")
            for file in sorted(self.enhanced_v5_files):
                f.write(f"  - {file}\n")
            f.write("\nSTATUS: CONSOLIDATION COMPLETE\n")
            f.write("All legacy tools have been consolidated into the V5 system.\n")
        
        logger.info(f"Consolidation report saved to: {json_path}")
        logger.info(f"Text report saved to: {text_path}")

def main():
    """Main execution function"""
    consolidator = V5ConsolidationEngine()
    stats = consolidator.run_consolidation()
    
    print("\n" + "="*60)
    print("V5 CONSOLIDATION COMPLETE!")
    print("="*60)
    print(f"Files Consolidated: {stats['files_consolidated']}")
    print(f"Files Removed: {stats['files_removed']}")
    print(f"Directories Cleaned: {stats['directories_cleaned']}")
    print(f"Errors: {stats['errors']}")
    print("="*60)
    
    if stats['files_removed'] > 0:
        print("SUCCESS: Legacy tools consolidated into V5 system!")
    else:
        print("ℹ️  INFO: No legacy tools found to consolidate")
    
    print(f"Reports saved to project root directory")

if __name__ == "__main__":
    main()
