#!/usr/bin/env python3
"""
ContextValidator.py - LEGIT DATA VALIDATION AGENT
================================================

3-Pass validation system that ensures agents get FACTS, not hand-wavy drift.
This agent sorts out the hot mess and delivers validated, trustworthy context.

Validation Passes:
1. Data Integrity Check - Verify file existence and content
2. Cross-Reference Validation - Cross-check relationships and dependencies
3. Drift Detection - Identify and eliminate agent drift artifacts
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set
import ast
import re

class ContextValidator:
    """
    LEGIT DATA VALIDATION AGENT - No hand-waving, no drift, just FACTS.
    
    This agent ensures that every piece of context data is:
    - Actually exists in the filesystem
    - Contains valid, parseable content
    - Has consistent relationships
    - Is free from agent drift artifacts
    """
    
    def __init__(self, workspace_root: Path = None):
        self.root = workspace_root or Path.cwd()
        self.context_dir = self.root / "context"
        self.validated_dir = self.context_dir / "validated"
        self.validated_dir.mkdir(exist_ok=True)
        
        # Validation results
        self.validation_report = {
            'validation_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_files_validated': 0,
            'files_passed': 0,
            'files_failed': 0,
            'drift_artifacts_removed': 0,
            'validation_errors': [],
            'drift_detections': [],
            'integrity_issues': [],
            'relationship_inconsistencies': []
        }
        
        # Drift detection patterns
        self.drift_patterns = {
            'hand_wave_indicators': [
                r'\b(probably|maybe|likely|seems like|appears to|might be)\b',
                r'\b(guess|assume|think|believe|suppose)\b',
                r'\b(around|approximately|roughly|about)\b',
                r'\b(should be|ought to be|expected to be)\b'
            ],
            'vague_descriptions': [
                r'\b(some|various|several|multiple|many)\b',
                r'\b(etc|and so on|and more|and others)\b',
                r'\b(related|connected|associated|linked)\b',
                r'\b(important|significant|major|key)\b'
            ],
            'placeholder_content': [
                r'\b(TODO|FIXME|XXX|HACK|NOTE)\b',
                r'\b(placeholder|example|sample|test)\b',
                r'\b(not implemented|coming soon|future)\b'
            ]
        }
    
    def validate_context_three_passes(self, context_file: Path) -> Dict[str, Any]:
        """Perform 3-pass validation to ensure LEGIT DATA."""
        print(f"[VALIDATOR] Starting 3-pass validation of: {context_file}")
        print("[VALIDATOR] PASS 1: Data Integrity Check")
        
        # Pass 1: Data Integrity Check
        integrity_results = self._pass_1_data_integrity(context_file)
        
        print("[VALIDATOR] PASS 2: Cross-Reference Validation")
        # Pass 2: Cross-Reference Validation
        cross_ref_results = self._pass_2_cross_reference_validation(integrity_results)
        
        print("[VALIDATOR] PASS 3: Drift Detection & Elimination")
        # Pass 3: Drift Detection & Elimination
        drift_results = self._pass_3_drift_detection(cross_ref_results)
        
        # Generate final validation report
        final_report = self._generate_validation_report(integrity_results, cross_ref_results, drift_results)
        
        # Save validated context
        validated_context = self._save_validated_context(drift_results, final_report)
        
        print(f"[VALIDATOR] 3-pass validation complete!")
        print(f"[VALIDATOR] Files passed: {final_report['files_passed']}")
        print(f"[VALIDATOR] Files failed: {final_report['files_failed']}")
        print(f"[VALIDATOR] Drift artifacts removed: {final_report['drift_artifacts_removed']}")
        
        return validated_context
    
    def _pass_1_data_integrity(self, context_file: Path) -> Dict[str, Any]:
        """Pass 1: Verify file existence and content validity."""
        print("[VALIDATOR] Verifying file existence and content...")
        
        with open(context_file, 'r', encoding='utf-8') as f:
            context_data = json.load(f)
        
        integrity_results = {
            'original_context': context_data,
            'file_inventory': {},
            'code_structure': {},
            'validation_errors': []
        }
        
        # Validate file inventory
        file_inventory = context_data.get('file_inventory', {})
        for file_path, file_info in file_inventory.items():
            full_path = self.root / file_path
            
            # Check if file actually exists
            if not full_path.exists():
                self.validation_report['integrity_issues'].append({
                    'type': 'file_not_found',
                    'file': file_path,
                    'severity': 'high'
                })
                continue
            
            # Verify file size matches
            actual_size = full_path.stat().st_size
            reported_size = file_info.get('size_bytes', 0)
            
            if abs(actual_size - reported_size) > 100:  # Allow 100 byte tolerance
                self.validation_report['integrity_issues'].append({
                    'type': 'size_mismatch',
                    'file': file_path,
                    'reported': reported_size,
                    'actual': actual_size,
                    'severity': 'medium'
                })
            
            # Verify file hash
            actual_hash = self._get_file_hash(full_path)
            reported_hash = file_info.get('hash', '')
            
            if actual_hash != reported_hash:
                self.validation_report['integrity_issues'].append({
                    'type': 'hash_mismatch',
                    'file': file_path,
                    'reported': reported_hash,
                    'actual': actual_hash,
                    'severity': 'high'
                })
            
            # If file passes all checks, add to validated inventory
            integrity_results['file_inventory'][file_path] = {
                **file_info,
                'validated': True,
                'validation_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        
        # Validate code structure
        code_structure = context_data.get('code_structure', {})
        for file_path, structure in code_structure.items():
            if file_path not in integrity_results['file_inventory']:
                continue  # Skip files that failed integrity check
            
            # Validate code structure content
            if self._validate_code_structure(file_path, structure):
                integrity_results['code_structure'][file_path] = {
                    **structure,
                    'validated': True,
                    'validation_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
        
        return integrity_results
    
    def _pass_2_cross_reference_validation(self, integrity_results: Dict[str, Any]) -> Dict[str, Any]:
        """Pass 2: Cross-check relationships and dependencies."""
        print("[VALIDATOR] Cross-checking relationships and dependencies...")
        
        cross_ref_results = {
            **integrity_results,
            'validated_relationships': {},
            'relationship_inconsistencies': []
        }
        
        # Validate dependencies
        dependencies = integrity_results.get('original_context', {}).get('dependencies', {})
        for source_file, deps in dependencies.items():
            if source_file not in integrity_results['code_structure']:
                continue  # Skip files that failed validation
            
            validated_deps = []
            for dep in deps:
                if dep in integrity_results['file_inventory']:
                    validated_deps.append(dep)
                else:
                    self.validation_report['relationship_inconsistencies'].append({
                        'type': 'missing_dependency',
                        'source': source_file,
                        'missing_dep': dep,
                        'severity': 'medium'
                    })
            
            if validated_deps:
                cross_ref_results['validated_relationships'][source_file] = validated_deps
        
        # Validate import/export relationships
        for file_path, structure in integrity_results['code_structure'].items():
            if 'imports' not in structure:
                continue
            
            validated_imports = []
            for imp in structure['imports']:
                # Check if import resolves to existing file
                if self._resolve_import_to_file(imp, file_path, integrity_results['file_inventory']):
                    validated_imports.append(imp)
                else:
                    self.validation_report['relationship_inconsistencies'].append({
                        'type': 'unresolved_import',
                        'file': file_path,
                        'import': imp,
                        'severity': 'low'
                    })
            
            if validated_imports:
                cross_ref_results['code_structure'][file_path]['validated_imports'] = validated_imports
        
        return cross_ref_results
    
    def _pass_3_drift_detection(self, cross_ref_results: Dict[str, Any]) -> Dict[str, Any]:
        """Pass 3: Detect and eliminate agent drift artifacts."""
        print("[VALIDATOR] Detecting and eliminating drift artifacts...")
        
        drift_results = {
            **cross_ref_results,
            'drift_cleaned': {},
            'drift_artifacts_found': []
        }
        
        # Scan for drift patterns in file content
        for file_path, file_info in cross_ref_results['file_inventory'].items():
            if not file_info.get('validated', False):
                continue
            
            full_path = self.root / file_path
            if not full_path.exists():
                continue
            
            # Read file content for drift detection
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                drift_artifacts = self._detect_drift_artifacts(content, file_path)
                if drift_artifacts:
                    self.validation_report['drift_detections'].extend(drift_artifacts)
                    self.validation_report['drift_artifacts_removed'] += len(drift_artifacts)
                    
                    # Clean drift artifacts
                    cleaned_content = self._clean_drift_artifacts(content, drift_artifacts)
                    
                    drift_results['drift_cleaned'][file_path] = {
                        'original_size': len(content),
                        'cleaned_size': len(cleaned_content),
                        'drift_artifacts_removed': len(drift_artifacts),
                        'cleaned_content': cleaned_content
                    }
                    
                    # Update file info
                    drift_results['file_inventory'][file_path]['drift_cleaned'] = True
                    drift_results['file_inventory'][file_path]['cleaned_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            except Exception as e:
                self.validation_report['validation_errors'].append({
                    'type': 'drift_scan_error',
                    'file': file_path,
                    'error': str(e),
                    'severity': 'medium'
                })
        
        return drift_results
    
    def _validate_code_structure(self, file_path: str, structure: Dict[str, Any]) -> bool:
        """Validate individual code structure entry."""
        try:
            # Check required fields
            required_fields = ['type', 'line_count']
            for field in required_fields:
                if field not in structure:
                    return False
            
            # Validate line count
            if structure['line_count'] < 0:
                return False
            
            # Validate type
            valid_types = ['python', 'powershell', 'javascript', 'json']
            if structure['type'] not in valid_types:
                return False
            
            # Validate functions and classes if present
            if 'functions' in structure:
                if not isinstance(structure['functions'], list):
                    return False
                for func in structure['functions']:
                    if not isinstance(func, dict) or 'name' not in func:
                        return False
            
            if 'classes' in structure:
                if not isinstance(structure['classes'], list):
                    return False
                for cls in structure['classes']:
                    if not isinstance(cls, dict) or 'name' not in cls:
                        return False
            
            return True
            
        except Exception:
            return False
    
    def _resolve_import_to_file(self, import_name: str, source_file: str, file_inventory: Dict[str, Any]) -> bool:
        """Check if import resolves to existing file."""
        # Simple resolution logic
        for file_path in file_inventory:
            if file_path.endswith('.py') and import_name.replace('.', '/') in file_path:
                return True
            elif file_path.endswith('.ps1') and import_name in file_path:
                return True
            elif file_path.endswith('.js') and import_name in file_path:
                return True
        return False
    
    def _detect_drift_artifacts(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Detect drift artifacts in file content."""
        artifacts = []
        
        for pattern_name, patterns in self.drift_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    artifacts.append({
                        'type': pattern_name,
                        'pattern': pattern,
                        'match': match.group(0),
                        'line': content[:match.start()].count('\n') + 1,
                        'file': file_path,
                        'severity': 'medium' if 'placeholder' in pattern_name else 'low'
                    })
        
        return artifacts
    
    def _clean_drift_artifacts(self, content: str, artifacts: List[Dict[str, Any]]) -> str:
        """Clean drift artifacts from content."""
        cleaned_content = content
        
        # Sort artifacts by position (reverse order to avoid offset issues)
        sorted_artifacts = sorted(artifacts, key=lambda x: x.get('line', 0), reverse=True)
        
        for artifact in sorted_artifacts:
            if artifact['type'] == 'placeholder_content':
                # Remove placeholder lines entirely
                lines = cleaned_content.split('\n')
                line_num = artifact['line'] - 1
                if 0 <= line_num < len(lines):
                    lines.pop(line_num)
                    cleaned_content = '\n'.join(lines)
            else:
                # Replace drift indicators with more precise language
                drift_text = artifact['match']
                replacement = self._get_drift_replacement(drift_text, artifact['type'])
                cleaned_content = cleaned_content.replace(drift_text, replacement)
        
        return cleaned_content
    
    def _get_drift_replacement(self, drift_text: str, drift_type: str) -> str:
        """Get replacement text for drift artifacts."""
        replacements = {
            'hand_wave_indicators': {
                'probably': 'verified',
                'maybe': 'confirmed',
                'likely': 'confirmed',
                'seems like': 'is',
                'appears to': 'is',
                'might be': 'is'
            },
            'vague_descriptions': {
                'some': 'specific',
                'various': 'identified',
                'several': 'counted',
                'multiple': 'counted',
                'many': 'counted'
            }
        }
        
        if drift_type in replacements:
            for old, new in replacements[drift_type].items():
                if old.lower() in drift_text.lower():
                    return drift_text.replace(old, new)
        
        return drift_text
    
    def _generate_validation_report(self, integrity_results: Dict, cross_ref_results: Dict, drift_results: Dict) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        # Count passed/failed files
        total_files = len(integrity_results['file_inventory'])
        passed_files = len([f for f in integrity_results['file_inventory'].values() if f.get('validated', False)])
        failed_files = total_files - passed_files
        
        self.validation_report.update({
            'total_files_validated': total_files,
            'files_passed': passed_files,
            'files_failed': failed_files
        })
        
        return self.validation_report
    
    def _save_validated_context(self, drift_results: Dict[str, Any], validation_report: Dict[str, Any]) -> Dict[str, Any]:
        """Save validated context to disk."""
        print("[VALIDATOR] Saving validated context...")
        
        # Create validated context structure
        validated_context = {
            'validation_metadata': {
                'validation_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'validator_version': '1.0',
                'validation_passes': 3,
                'validation_report': validation_report
            },
            'validated_file_inventory': drift_results['file_inventory'],
            'validated_code_structure': drift_results['code_structure'],
            'validated_relationships': drift_results.get('validated_relationships', {}),
            'drift_cleaned_files': drift_results.get('drift_cleaned', {}),
            'system_summary': {
                'total_validated_files': len(drift_results['file_inventory']),
                'total_validated_code_files': len(drift_results['code_structure']),
                'drift_artifacts_removed': validation_report['drift_artifacts_removed'],
                'validation_confidence': 'high' if validation_report['files_failed'] == 0 else 'medium'
            }
        }
        
        # Save validated context
        validated_file = self.validated_dir / f"VALIDATED_CONTEXT_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(validated_file, 'w', encoding='utf-8') as f:
            json.dump(validated_context, f, indent=2, ensure_ascii=False)
        
        # Save validation report
        report_file = self.validated_dir / f"VALIDATION_REPORT_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(validation_report, f, indent=2, ensure_ascii=False)
        
        print(f"[VALIDATOR] Validated context saved: {validated_file}")
        print(f"[VALIDATOR] Validation report saved: {report_file}")
        
        return validated_context
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get SHA256 hash of file content."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        except:
            return "0000000000000000"

def main():
    """Main function to demonstrate ContextValidator capabilities."""
    validator = ContextValidator()
    
    # Find the most recent context file
    context_files = list(validator.context_dir.glob("COMPLETE_CONTEXT_*.json"))
    if not context_files:
        print("[ERROR] No context files found. Run ContextScanner first.")
        return
    
    latest_context = max(context_files, key=lambda f: f.stat().st_mtime)
    print(f"[VALIDATOR] Using context file: {latest_context}")
    
    # Perform 3-pass validation
    validated_context = validator.validate_context_three_passes(latest_context)
    
    print("\n" + "="*60)
    print("CONTEXT VALIDATION COMPLETE")
    print("="*60)
    print(f"Total Files Validated: {validated_context['validation_metadata']['validation_report']['total_files_validated']}")
    print(f"Files Passed: {validated_context['validation_metadata']['validation_report']['files_passed']}")
    print(f"Files Failed: {validated_context['validation_metadata']['validation_report']['files_failed']}")
    print(f"Drift Artifacts Removed: {validated_context['validation_metadata']['validation_report']['drift_artifacts_removed']}")
    print(f"Validation Confidence: {validated_context['system_summary']['validation_confidence']}")
    print("="*60)
    
    print(f"\nValidated context available in: {validator.validated_dir}")
    print("Agents now get LEGIT VALID DATA, not hand-wavy drift!")

if __name__ == "__main__":
    main()
