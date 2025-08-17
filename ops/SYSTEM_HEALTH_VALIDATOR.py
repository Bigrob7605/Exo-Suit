#!/usr/bin/env python3
"""
SYSTEM HEALTH VALIDATOR - Agent Exo-Suit V5.0
==============================================

This script provides honest, accurate validation of the system's actual
capabilities, replacing the broken validation systems.
"""

import os
import sys
import json
import time
import psutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_health_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemHealthValidator:
    """Comprehensive system health validation"""
    
    def __init__(self):
        self.project_root = Path('.')
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {},
            'project_analysis': {},
            'component_health': {},
            'performance_metrics': {},
            'validation_score': 0,
            'issues_found': [],
            'recommendations': []
        }
    
    def validate_system_info(self) -> Dict[str, Any]:
        """Validate basic system information"""
        try:
            system_info = {
                'python_version': sys.version,
                'platform': sys.platform,
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
                'disk_usage': {}
            }
            
            # Check disk usage for main drives
            if sys.platform == 'win32':
                # Windows: Check available drives more safely
                import string
                for drive_letter in string.ascii_uppercase:
                    drive = f"{drive_letter}:"
                    try:
                        if os.path.exists(drive):
                            disk = psutil.disk_usage(drive)
                            system_info['disk_usage'][drive] = {
                                'total_gb': round(disk.total / (1024**3), 2),
                                'free_gb': round(disk.free / (1024**3), 2),
                                'used_percent': disk.percent
                            }
                    except (OSError, FileNotFoundError, PermissionError) as e:
                        logger.warning(f"Could not access drive {drive}: {e}")
                        continue
            else:
                # Unix/Linux: Check root directory
                try:
                    disk = psutil.disk_usage('/')
                    system_info['disk_usage']['/'] = {
                        'total_gb': round(disk.total / (1024**3), 2),
                        'free_gb': round(disk.free / (1024**3), 2),
                        'used_percent': disk.percent
                    }
                except (OSError, FileNotFoundError) as e:
                    logger.warning(f"Could not access root directory: {e}")
                    pass
            
            self.validation_results['system_info'] = system_info
            return system_info
            
        except Exception as e:
            logger.error(f"Error validating system info: {e}")
            # Return basic info even if disk usage fails
            basic_info = {
                'python_version': sys.version,
                'platform': sys.platform,
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
                'disk_usage': {},
                'error': str(e)
            }
            self.validation_results['system_info'] = basic_info
            return basic_info
    
    def validate_project_structure(self) -> Dict[str, Any]:
        """Validate project structure and identify key components"""
        try:
            project_analysis = {
                'total_files': 0,
                'total_directories': 0,
                'file_types': {},
                'key_components': [],
                'missing_components': [],
                'project_size_mb': 0
            }
            
            # Count files and directories
            for root, dirs, files in os.walk(self.project_root):
                project_analysis['total_directories'] += len(dirs)
                project_analysis['total_files'] += len(files)
                
                # Categorize files by type
                for file in files:
                    ext = Path(file).suffix.lower()
                    project_analysis['file_types'][ext] = project_analysis['file_types'].get(ext, 0) + 1
                
                # Calculate project size
                for file in files:
                    try:
                        file_path = Path(root) / file
                        if file_path.is_file():
                            project_analysis['project_size_mb'] += file_path.stat().st_size / (1024 * 1024)
                    except (OSError, PermissionError):
                        continue
            
            # Identify key components
            key_files = [
                'README.md', 'AGENT_STATUS.md', 'requirements.txt',
                'ops/', 'context/', 'config/'
            ]
            
            for component in key_files:
                if (self.project_root / component).exists():
                    project_analysis['key_components'].append(component)
                else:
                    project_analysis['missing_components'].append(component)
            
            self.validation_results['project_analysis'] = project_analysis
            return project_analysis
            
        except Exception as e:
            logger.error(f"Error validating project structure: {e}")
            return {}
    
    def validate_component_health(self) -> Dict[str, Any]:
        """Validate the health of key system components"""
        try:
            component_health = {
                'python_scripts': {},
                'powershell_scripts': {},
                'configuration_files': {},
                'overall_health': 'unknown'
            }
            
            # Check Python scripts
            python_scripts = list(self.project_root.rglob('*.py'))
            for script in python_scripts[:10]:  # Check first 10 scripts
                try:
                    with open(script, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Basic syntax check
                        compile(content, str(script), 'exec')
                        component_health['python_scripts'][str(script)] = 'valid'
                except Exception as e:
                    component_health['python_scripts'][str(script)] = f'invalid: {str(e)}'
            
            # Check PowerShell scripts
            ps_scripts = list(self.project_root.rglob('*.ps1'))
            for script in ps_scripts[:10]:  # Check first 10 scripts
                try:
                    with open(script, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Basic content validation
                        if content.strip() and not content.startswith('\x00'):
                            component_health['powershell_scripts'][str(script)] = 'valid'
                        else:
                            component_health['powershell_scripts'][str(script)] = 'empty_or_corrupted'
                except Exception as e:
                    component_health['powershell_scripts'][str(script)] = f'error: {str(e)}'
            
            # Check configuration files
            config_files = list(self.project_root.rglob('*.json')) + list(self.project_root.rglob('*.yaml')) + list(self.project_root.rglob('*.yml'))
            for config in config_files[:10]:  # Check first 10 configs
                try:
                    with open(config, 'r', encoding='utf-8') as f:
                        if config.suffix == '.json':
                            json.load(f)
                        component_health['configuration_files'][str(config)] = 'valid'
                except Exception as e:
                    component_health['configuration_files'][str(config)] = f'invalid: {str(e)}'
            
            # Determine overall health
            valid_components = sum(1 for comp_type in component_health.values() if isinstance(comp_type, dict) 
                                 for status in comp_type.values() if status == 'valid')
            total_components = sum(len(comp_type) for comp_type in component_health.values() if isinstance(comp_type, dict))
            
            if total_components > 0:
                health_percentage = (valid_components / total_components) * 100
                if health_percentage >= 80:
                    component_health['overall_health'] = 'excellent'
                elif health_percentage >= 60:
                    component_health['overall_health'] = 'good'
                elif health_percentage >= 40:
                    component_health['overall_health'] = 'fair'
                else:
                    component_health['overall_health'] = 'poor'
            else:
                component_health['overall_health'] = 'unknown'
            
            self.validation_results['component_health'] = component_health
            return component_health
            
        except Exception as e:
            logger.error(f"Error validating component health: {e}")
            return {}
    
    def validate_performance_metrics(self) -> Dict[str, Any]:
        """Validate system performance capabilities"""
        try:
            performance_metrics = {
                'file_processing_test': {},
                'memory_usage': {},
                'cpu_usage': {},
                'disk_io': {}
            }
            
            # Test file processing performance
            start_time = time.time()
            test_files = list(self.project_root.rglob('*.py'))[:1000]  # Test with up to 1000 Python files
            file_count = len(test_files)
            
            if file_count > 0:
                # Simulate file processing
                for file_path in test_files:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            # Basic content analysis
                            lines = content.count('\n')
                            chars = len(content)
                    except Exception:
                        continue
                
                end_time = time.time()
                duration = end_time - start_time
                files_per_second = file_count / duration if duration > 0 else 0
                
                performance_metrics['file_processing_test'] = {
                    'files_processed': file_count,
                    'duration_seconds': round(duration, 2),
                    'files_per_second': round(files_per_second, 2),
                    'status': 'completed'
                }
            else:
                performance_metrics['file_processing_test'] = {
                    'status': 'no_test_files_found'
                }
            
            # Memory usage
            memory = psutil.virtual_memory()
            performance_metrics['memory_usage'] = {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_percent': memory.percent,
                'status': 'healthy' if memory.percent < 90 else 'warning'
            }
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            performance_metrics['cpu_usage'] = {
                'current_percent': cpu_percent,
                'status': 'healthy' if cpu_percent < 80 else 'warning'
            }
            
            self.validation_results['performance_metrics'] = performance_metrics
            return performance_metrics
            
        except Exception as e:
            logger.error(f"Error validating performance metrics: {e}")
            return {}
    
    def calculate_validation_score(self) -> int:
        """Calculate overall validation score"""
        try:
            score = 0
            max_score = 100
            
            # System info validation (20 points)
            if self.validation_results['system_info']:
                score += 20
            
            # Project structure validation (25 points)
            project_analysis = self.validation_results['project_analysis']
            if project_analysis.get('total_files', 0) > 0:
                score += 10
            if project_analysis.get('key_components'):
                score += 10
            if len(project_analysis.get('missing_components', [])) == 0:
                score += 5
            
            # Component health validation (30 points)
            component_health = self.validation_results['component_health']
            if component_health.get('overall_health') == 'excellent':
                score += 30
            elif component_health.get('overall_health') == 'good':
                score += 25
            elif component_health.get('overall_health') == 'fair':
                score += 20
            elif component_health.get('overall_health') == 'poor':
                score += 10
            
            # Performance validation (25 points)
            performance = self.validation_results['performance_metrics']
            if performance.get('file_processing_test', {}).get('status') == 'completed':
                score += 15
                # Bonus points for good performance
                fps = performance['file_processing_test'].get('files_per_second', 0)
                if fps > 1000:
                    score += 10
                elif fps > 100:
                    score += 5
            
            if performance.get('memory_usage', {}).get('status') == 'healthy':
                score += 10
            
            self.validation_results['validation_score'] = min(score, max_score)
            return self.validation_results['validation_score']
            
        except Exception as e:
            logger.error(f"Error calculating validation score: {e}")
            return 0
    
    def generate_issues_and_recommendations(self):
        """Generate issues list and recommendations"""
        issues = []
        recommendations = []
        
        # Check for missing components
        missing_components = self.validation_results['project_analysis'].get('missing_components', [])
        if missing_components:
            issues.append(f"Missing key components: {', '.join(missing_components)}")
            recommendations.append("Create or restore missing key components")
        
        # Check component health
        component_health = self.validation_results['component_health']
        if component_health.get('overall_health') in ['poor', 'unknown']:
            issues.append("Component health is poor or unknown")
            recommendations.append("Investigate and fix component issues")
        
        # Check performance
        performance = self.validation_results['performance_metrics']
        if performance.get('memory_usage', {}).get('status') == 'warning':
            issues.append("High memory usage detected")
            recommendations.append("Optimize memory usage or increase available memory")
        
        if performance.get('cpu_usage', {}).get('status') == 'warning':
            issues.append("High CPU usage detected")
            recommendations.append("Investigate CPU-intensive processes")
        
        # Check file processing
        file_test = performance.get('file_processing_test', {})
        if file_test.get('status') != 'completed':
            issues.append("File processing test failed")
            recommendations.append("Fix file processing capabilities")
        
        self.validation_results['issues_found'] = issues
        self.validation_results['recommendations'] = recommendations
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete system validation"""
        logger.info("Starting comprehensive system health validation...")
        
        # Run all validation steps
        self.validate_system_info()
        self.validate_project_structure()
        self.validate_component_health()
        self.validate_performance_metrics()
        
        # Calculate score and generate recommendations
        score = self.calculate_validation_score()
        self.generate_issues_and_recommendations()
        
        # Generate validation report
        self.generate_validation_report()
        
        logger.info(f"Validation complete. Score: {score}/100")
        return self.validation_results
    
    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        try:
            # JSON report
            json_path = self.project_root / 'SYSTEM_HEALTH_VALIDATION_REPORT.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
            
            # Text report
            text_path = self.project_root / 'SYSTEM_HEALTH_VALIDATION_REPORT.txt'
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write("SYSTEM HEALTH VALIDATION REPORT - Agent Exo-Suit V5.0\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"Validation Timestamp: {self.validation_results['timestamp']}\n")
                f.write(f"Overall Score: {self.validation_results['validation_score']}/100\n\n")
                
                f.write("SYSTEM INFORMATION:\n")
                f.write("-" * 30 + "\n")
                for key, value in self.validation_results['system_info'].items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")
                
                f.write("PROJECT ANALYSIS:\n")
                f.write("-" * 30 + "\n")
                project = self.validation_results['project_analysis']
                f.write(f"Total Files: {project.get('total_files', 0):,}\n")
                f.write(f"Total Directories: {project.get('total_directories', 0):,}\n")
                f.write(f"Project Size: {project.get('project_size_mb', 0):.2f} MB\n")
                f.write(f"Key Components: {len(project.get('key_components', []))}\n")
                f.write(f"Missing Components: {len(project.get('missing_components', []))}\n\n")
                
                f.write("COMPONENT HEALTH:\n")
                f.write("-" * 30 + "\n")
                health = self.validation_results['component_health']
                f.write(f"Overall Health: {health.get('overall_health', 'unknown')}\n")
                f.write(f"Python Scripts: {len(health.get('python_scripts', {}))}\n")
                f.write(f"PowerShell Scripts: {len(health.get('powershell_scripts', {}))}\n")
                f.write(f"Configuration Files: {len(health.get('configuration_files', {}))}\n\n")
                
                f.write("PERFORMANCE METRICS:\n")
                f.write("-" * 30 + "\n")
                perf = self.validation_results['performance_metrics']
                file_test = perf.get('file_processing_test', {})
                if file_test.get('status') == 'completed':
                    f.write(f"File Processing: {file_test.get('files_per_second', 0):.2f} files/sec\n")
                else:
                    f.write(f"File Processing: {file_test.get('status', 'unknown')}\n")
                
                memory = perf.get('memory_usage', {})
                f.write(f"Memory Usage: {memory.get('used_percent', 0):.1f}%\n")
                f.write(f"CPU Usage: {perf.get('cpu_usage', {}).get('current_percent', 0):.1f}%\n\n")
                
                f.write("ISSUES FOUND:\n")
                f.write("-" * 30 + "\n")
                for issue in self.validation_results['issues_found']:
                    f.write(f"• {issue}\n")
                f.write("\n")
                
                f.write("RECOMMENDATIONS:\n")
                f.write("-" * 30 + "\n")
                for rec in self.validation_results['recommendations']:
                    f.write(f"• {rec}\n")
                f.write("\n")
                
                f.write("VALIDATION STATUS: COMPLETE\n")
                f.write(f"Report generated: {datetime.now().isoformat()}\n")
            
            logger.info(f"Validation report saved to: {json_path}")
            logger.info(f"Text report saved to: {text_path}")
            
        except Exception as e:
            logger.error(f"Error generating validation report: {e}")

def main():
    """Main execution function"""
    validator = SystemHealthValidator()
    results = validator.run_full_validation()
    
    print("\n" + "="*70)
    print("SYSTEM HEALTH VALIDATION COMPLETE!")
    print("="*70)
    print(f"Overall Score: {results['validation_score']}/100")
    print(f"Files Found: {results['project_analysis'].get('total_files', 0):,}")
    print(f"Component Health: {results['component_health'].get('overall_health', 'unknown')}")
    print(f"Issues Found: {len(results['issues_found'])}")
    print("="*70)
    
    if results['issues_found']:
        print("\nISSUES IDENTIFIED:")
        for issue in results['issues_found']:
            print(f"• {issue}")
    
    if results['recommendations']:
        print("\nRECOMMENDATIONS:")
        for rec in results['recommendations']:
            print(f"• {rec}")
    
    print(f"\nDetailed reports saved to project root directory")

if __name__ == "__main__":
    main()
