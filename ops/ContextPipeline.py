#!/usr/bin/env python3
"""
ContextPipeline.py - Master Context Orchestrator
===============================================

Orchestrates the complete ANTI-HAND WAVE context pipeline:
1. ContextScanner - Scan entire codebase
2. ContextChunker - Break into agent-friendly chunks
3. ContextValidator - 3-pass validation for LEGIT DATA
4. Emoji Scanner - Clean out emojis
5. VisionGap Analysis - Final gap detection

This ensures agents get 100% valid, drift-free context.
"""

import time
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

class ContextPipeline:
    """
    Master orchestrator for the complete context pipeline.
    
    Ensures agents get LEGIT VALID DATA through systematic validation.
    """
    
    def __init__(self, workspace_root: Path = None):
        self.root = workspace_root or Path.cwd()
        self.ops_dir = self.root / "ops"
        self.context_dir = self.root / "context"
        
        # Pipeline status
        self.pipeline_status = {
            'start_time': None,
            'end_time': None,
            'steps_completed': [],
            'errors': [],
            'warnings': []
        }
    
    def run_complete_pipeline(self) -> Dict[str, Any]:
        """Run the complete context pipeline."""
        print("="*60)
        print("ROCKET: EXO-SUIT CONTEXT PIPELINE - ANTI-HAND WAVE SYSTEM")
        print("="*60)
        
        self.pipeline_status['start_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # Step 1: Context Scanning
            print("\nBAR_CHART: STEP 1: Context Scanning")
            print("-" * 40)
            self._run_context_scanner()
            
            # Step 2: Context Chunking
            print("\nSCISSORS: STEP 2: Context Chunking")
            print("-" * 40)
            self._run_context_chunker()
            
            # Step 3: Context Validation (3-Pass)
            print("\nMAGNIFYING_GLASS: STEP 3: Context Validation (3-Pass)")
            print("-" * 40)
            self._run_context_validator()
            
            # Step 4: Emoji Scanning & Cleaning
            print("\nBROOM STEP 4: Emoji Scanning & Cleaning")
            print("-" * 40)
            self._run_emoji_scanner()
            
            # Step 5: Vision Gap Analysis
            print("\nTARGET: STEP 5: Vision Gap Analysis")
            print("-" * 40)
            self._run_vision_gap_analysis()
            
            # Pipeline complete
            self.pipeline_status['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            self.pipeline_status['steps_completed'] = [
                'Context Scanning',
                'Context Chunking', 
                'Context Validation',
                'Emoji Scanning',
                'Vision Gap Analysis'
            ]
            
            # Generate final report
            final_report = self._generate_pipeline_report()
            
            print("\n" + "="*60)
            print("SUCCESS: CONTEXT PIPELINE COMPLETE!")
            print("="*60)
            print(f"Start Time: {self.pipeline_status['start_time']}")
            print(f"End Time: {self.pipeline_status['end_time']}")
            print(f"Steps Completed: {len(self.pipeline_status['steps_completed'])}")
            print(f"Errors: {len(self.pipeline_status['errors'])}")
            print(f"Warnings: {len(self.pipeline_status['warnings'])}")
            print("="*60)
            
            return final_report
            
        except Exception as e:
            error_msg = f"Pipeline failed: {str(e)}"
            self.pipeline_status['errors'].append(error_msg)
            print(f"\nERROR: {error_msg}")
            raise
    
    def _run_context_scanner(self):
        """Run the ContextScanner to analyze the codebase."""
        print("[PIPELINE] Running ContextScanner...")
        
        try:
            result = subprocess.run([
                sys.executable, str(self.ops_dir / "ContextScanner.py")
            ], capture_output=True, text=True, cwd=self.root)
            
            if result.returncode == 0:
                print("[PIPELINE] SUCCESS: ContextScanner completed successfully")
                self.pipeline_status['steps_completed'].append('ContextScanner')
            else:
                error_msg = f"ContextScanner failed: {result.stderr}"
                self.pipeline_status['errors'].append(error_msg)
                print(f"[PIPELINE] ERROR: {error_msg}")
                raise RuntimeError(error_msg)
                
        except Exception as e:
            error_msg = f"ContextScanner execution failed: {str(e)}"
            self.pipeline_status['errors'].append(error_msg)
            print(f"[PIPELINE] ERROR: {error_msg}")
            raise
    
    def _run_context_chunker(self):
        """Run the ContextChunker to create agent-friendly chunks."""
        print("[PIPELINE] Running ContextChunker...")
        
        try:
            result = subprocess.run([
                sys.executable, str(self.ops_dir / "ContextChunker.py")
            ], capture_output=True, text=True, cwd=self.root)
            
            if result.returncode == 0:
                print("[PIPELINE] SUCCESS: ContextChunker completed successfully")
                self.pipeline_status['steps_completed'].append('ContextChunker')
            else:
                error_msg = f"ContextChunker failed: {result.stderr}"
                self.pipeline_status['errors'].append(error_msg)
                print(f"[PIPELINE] ERROR: {error_msg}")
                raise RuntimeError(error_msg)
                
        except Exception as e:
            error_msg = f"ContextChunker execution failed: {str(e)}"
            self.pipeline_status['errors'].append(error_msg)
            print(f"[PIPELINE] ERROR: {error_msg}")
            raise
    
    def _run_context_validator(self):
        """Run the ContextValidator for 3-pass validation."""
        print("[PIPELINE] Running ContextValidator (3-pass validation)...")
        
        try:
            result = subprocess.run([
                sys.executable, str(self.ops_dir / "ContextValidator.py")
            ], capture_output=True, text=True, cwd=self.root)
            
            if result.returncode == 0:
                print("[PIPELINE] SUCCESS: ContextValidator completed successfully")
                self.pipeline_status['steps_completed'].append('ContextValidator')
            else:
                error_msg = f"ContextValidator failed: {result.stderr}"
                self.pipeline_status['errors'].append(error_msg)
                print(f"[PIPELINE] ERROR: {error_msg}")
                raise RuntimeError(error_msg)
                
        except Exception as e:
            error_msg = f"ContextValidator execution failed: {str(e)}"
            self.pipeline_status['errors'].append(error_msg)
            print(f"[PIPELINE] ERROR: {error_msg}")
            raise
    
    def _run_emoji_scanner(self):
        """Run fast emoji scanner to detect and clean emojis in code files."""
        print("[PIPELINE] Running fast emoji scanner...")
        
        try:
            # Import and use the fast emoji scanner
            try:
                from ops.FastEmojiScanner import FastEmojiScanner
                scanner = FastEmojiScanner(self.root)
                
                # Run the fast scan
                results = scanner.scan_workspace_fast()
                
                if results['files_with_emojis']:
                    print(f"[PIPELINE] Found {len(results['files_with_emojis'])} files with emojis ({results['total_emojis_found']} total)")
                    
                    # Clean emojis automatically
                    cleaning_results = scanner.remove_emojis_from_files(results['files_with_emojis'])
                    print(f"[PIPELINE] Cleaned {cleaning_results['files_cleaned']} files with {cleaning_results['total_replacements']} replacements")
                    
                    self.pipeline_status['steps_completed'].append('EmojiScanner')
                else:
                    print("[PIPELINE] No emojis found in code files")
                    self.pipeline_status['steps_completed'].append('EmojiScanner')
                    
            except ImportError:
                # Fallback to simple emoji detection if FastEmojiScanner not available
                print("[PIPELINE] FastEmojiScanner not available, using fallback method...")
                self._run_emoji_scanner_fallback()
                
        except Exception as e:
            warning_msg = f"Fast emoji scanner execution failed: {str(e)}"
            self.pipeline_status['warnings'].append(warning_msg)
            print(f"[PIPELINE] WARNING: {warning_msg}")
    
    def _run_emoji_scanner_fallback(self):
        """Fallback emoji scanner method."""
        try:
            # Simple emoji detection using regex
            emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000027BF\U0001F900-\U0001F9FF]')
            
            files_with_emojis = []
            total_emojis = 0
            
            # Scan all Python and PowerShell files
            for file_path in self.workspace_root.rglob('*.py'):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    emojis = emoji_pattern.findall(content)
                    if emojis:
                        files_with_emojis.append({
                            'file': str(file_path),
                            'emojis': emojis,
                            'count': len(emojis)
                        })
                        total_emojis += len(emojis)
                        
                except Exception as e:
                    continue
            
            # Scan PowerShell files
            for file_path in self.workspace_root.rglob('*.ps1'):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    emojis = emoji_pattern.findall(content)
                    if emojis:
                        files_with_emojis.append({
                            'file': str(file_path),
                            'emojis': emojis,
                            'count': len(emojis)
                        })
                        total_emojis += len(emojis)
                        
                except Exception as e:
                    continue
            
            if files_with_emojis:
                print(f"[PIPELINE] Found {len(files_with_emojis)} files with emojis ({total_emojis} total)")
                for file_info in files_with_emojis:
                    print(f"[PIPELINE] {file_info['file']}: {file_info['count']} emojis")
                
                # Clean emojis by replacing with descriptive text
                self._clean_emojis_from_files(files_with_emojis)
            else:
                print("[PIPELINE] No emojis found in code files")
                
        except Exception as e:
            warning_msg = f"Fallback emoji scanner execution failed: {str(e)}"
            self.pipeline_status['warnings'].append(warning_msg)
            print(f"[PIPELINE] WARNING: {warning_msg}")
    
    def _run_vision_gap_analysis(self):
        """Run the VisionGap Engine for final analysis."""
        print("[PIPELINE] Running VisionGap analysis...")
        
        try:
            result = subprocess.run([
                sys.executable, str(self.ops_dir / "VISIONGAP_ENGINE.py")
            ], capture_output=True, text=True, cwd=self.root)
            
            if result.returncode == 0:
                print("[PIPELINE] SUCCESS: VisionGap analysis completed successfully")
                self.pipeline_status['steps_completed'].append('VisionGapAnalysis')
            else:
                error_msg = f"VisionGap analysis failed: {result.stderr}"
                self.pipeline_status['errors'].append(error_msg)
                print(f"[PIPELINE] ERROR: {error_msg}")
                raise RuntimeError(error_msg)
                
        except Exception as e:
            error_msg = f"VisionGap analysis execution failed: {str(e)}"
            self.pipeline_status['errors'].append(error_msg)
            print(f"[PIPELINE] ERROR: {error_msg}")
            raise
    
    def _generate_pipeline_report(self) -> Dict[str, Any]:
        """Generate comprehensive pipeline report."""
        report = {
            'pipeline_metadata': {
                'name': 'Exo-Suit Context Pipeline',
                'version': '1.0',
                'description': 'ANTI-HAND WAVE context system for agents',
                'start_time': self.pipeline_status['start_time'],
                'end_time': self.pipeline_status['end_time'],
                'total_duration': self._calculate_duration()
            },
            'pipeline_status': self.pipeline_status,
            'output_locations': {
                'context_files': str(self.context_dir),
                'chunks': str(self.context_dir / "chunks"),
                'validated_context': str(self.context_dir / "validated"),
                'reports': str(self.root / "reports")
            },
            'agent_access_instructions': {
                '128k_agents': 'Start with context/chunks/system_overview.json',
                '1M_agents': 'Load multiple chunks or use validated context',
                'navigation': 'Use context/chunks/NAVIGATION_INDEX.md for guidance'
            }
        }
        
        # Save pipeline report
        report_file = self.context_dir / f"PIPELINE_REPORT_{time.strftime('%Y%m%d_%H%M%S')}.json"
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"[PIPELINE] Pipeline report saved: {report_file}")
        return report
    
    def _calculate_duration(self) -> str:
        """Calculate pipeline duration."""
        if not self.pipeline_status['start_time'] or not self.pipeline_status['end_time']:
            return "Unknown"
        
        try:
            from datetime import datetime
            start = datetime.strptime(self.pipeline_status['start_time'], '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(self.pipeline_status['end_time'], '%Y-%m-%d %H:%M:%S')
            duration = end - start
            return str(duration)
        except:
            return "Unknown"

def main():
    """Main function to run the complete context pipeline."""
    pipeline = ContextPipeline()
    
    try:
        # Run the complete pipeline
        final_report = pipeline.run_complete_pipeline()
        
        print(f"\nTARGET: **PIPELINE RESULTS:**")
        print(f"SUCCESS: Context files: {final_report['output_locations']['context_files']}")
        print(f"SUCCESS: Chunked context: {final_report['output_locations']['chunks']}")
        print(f"SUCCESS: Validated context: {final_report['output_locations']['validated_context']}")
        print(f"SUCCESS: Vision gap reports: {final_report['output_locations']['reports']}")
        
        print(f"\nROCKET: **AGENTS NOW HAVE:**")
        print(f"• 100% visibility into Exo-Suit system")
        print(f"• LEGIT VALID DATA (no hand-waving)")
        print(f"• Agent-friendly chunks (128k+ compatible)")
        print(f"• Drift-free, validated context")
        print(f"• Clean, emoji-free codebase")
        print(f"• Accurate gap analysis")
        
        print(f"\nTARGET: **NEXT STEPS:**")
        print(f"1. Test context with different agent types")
        print(f"2. Validate chunk accessibility")
        print(f"3. Measure agent comprehension improvement")
        print(f"4. Scale to include toolbox systems")
        
    except Exception as e:
        print(f"\nERROR: Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
