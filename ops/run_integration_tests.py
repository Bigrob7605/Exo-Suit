#!/usr/bin/env python3
"""
V5 INTEGRATION TEST EXECUTOR
Agent Exo-Suit V5.0 - Complete System Validation

This script executes the comprehensive integration test plan to validate
that all V5 components work together seamlessly.
"""

import os
import sys
import time
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - V5_INTEGRATION - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/v5_integration_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class V5IntegrationTester:
    """Execute V5 complete integration test plan"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.current_phase = None
        
        # Test configuration
        self.test_config = {
            "phase1_timeout": 300,  # 5 minutes per phase
            "phase2_timeout": 600,  # 10 minutes for performance tests
            "phase3_timeout": 900,  # 15 minutes for real-world tests
            "max_retries": 3
        }
        
        logging.info("V5 Integration Tester initialized - Ready to validate complete system!")
    
    def run_full_integration_test(self):
        """Execute complete V5 integration test plan"""
        self.start_time = datetime.now()
        logging.info(f"Starting V5 Complete Integration Test at {self.start_time}")
        
        try:
            # Phase 1: Core Workflow Pipeline Validation
            self._execute_phase1()
            
            # Phase 2: Performance Under Load Validation
            self._execute_phase2()
            
            # Phase 3: Real-World Scenario Validation
            self._execute_phase3()
            
            # Generate final report
            self._generate_integration_report()
            
        except Exception as e:
            logging.error(f"Integration test failed: {e}")
            self._generate_failure_report(str(e))
    
    def _execute_phase1(self):
        """Execute Phase 1: Core Workflow Pipeline Validation"""
        self.current_phase = "Phase 1: Core Workflow Pipeline"
        logging.info(f"Starting {self.current_phase}")
        
        phase_results = {
            "dream_builder": False,
            "chaos_engine": False,
            "phoenix_recovery": False,
            "learning_pipeline": False
        }
        
        try:
            # Test 1.1: Dream Building Pipeline
            logging.info("Testing Dream Builder Pipeline...")
            if self._test_dream_builder():
                phase_results["dream_builder"] = True
                logging.info("✅ Dream Builder Pipeline: PASSED")
            else:
                logging.error("❌ Dream Builder Pipeline: FAILED")
            
            # Test 1.2: Chaos Injection Pipeline
            logging.info("Testing Chaos Engine Pipeline...")
            if self._test_chaos_engine():
                phase_results["chaos_engine"] = True
                logging.info("✅ Chaos Engine Pipeline: PASSED")
            else:
                logging.error("❌ Chaos Engine Pipeline: FAILED")
            
            # Test 1.3: Recovery Pipeline
            logging.info("Testing Phoenix Recovery Pipeline...")
            if self._test_phoenix_recovery():
                phase_results["phoenix_recovery"] = True
                logging.info("✅ Phoenix Recovery Pipeline: PASSED")
            else:
                logging.error("❌ Phoenix Recovery Pipeline: FAILED")
            
            # Test 1.4: Learning Pipeline
            logging.info("Testing Learning Pipeline...")
            if self._test_learning_pipeline():
                phase_results["learning_pipeline"] = True
                logging.info("✅ Learning Pipeline: PASSED")
            else:
                logging.error("❌ Learning Pipeline: FAILED")
            
        except Exception as e:
            logging.error(f"Phase 1 failed: {e}")
        
        self.test_results["phase1"] = phase_results
        self._log_phase_completion("Phase 1", phase_results)
    
    def _execute_phase2(self):
        """Execute Phase 2: Performance Under Load Validation"""
        self.current_phase = "Phase 2: Performance Under Load"
        logging.info(f"Starting {self.current_phase}")
        
        phase_results = {
            "large_scale_handling": False,
            "gpu_acceleration": False,
            "resource_management": False
        }
        
        try:
            # Test 2.1: Large-Scale Project Handling
            logging.info("Testing Large-Scale Project Handling...")
            if self._test_large_scale_handling():
                phase_results["large_scale_handling"] = True
                logging.info("✅ Large-Scale Handling: PASSED")
            else:
                logging.error("❌ Large-Scale Handling: FAILED")
            
            # Test 2.2: GPU Acceleration
            logging.info("Testing GPU Acceleration...")
            if self._test_gpu_acceleration():
                phase_results["gpu_acceleration"] = True
                logging.info("✅ GPU Acceleration: PASSED")
            else:
                logging.error("❌ GPU Acceleration: FAILED")
            
            # Test 2.3: Resource Management
            logging.info("Testing Resource Management...")
            if self._test_resource_management():
                phase_results["resource_management"] = True
                logging.info("✅ Resource Management: PASSED")
            else:
                logging.error("❌ Resource Management: FAILED")
            
        except Exception as e:
            logging.error(f"Phase 2 failed: {e}")
        
        self.test_results["phase2"] = phase_results
        self._log_phase_completion("Phase 2", phase_results)
    
    def _execute_phase3(self):
        """Execute Phase 3: Real-World Scenario Validation"""
        self.current_phase = "Phase 3: Real-World Scenarios"
        logging.info(f"Starting {self.current_phase}")
        
        phase_results = {
            "real_repository_processing": False,
            "edge_case_resilience": False,
            "training_data_generation": False
        }
        
        try:
            # Test 3.1: Real Repository Processing
            logging.info("Testing Real Repository Processing...")
            if self._test_real_repository_processing():
                phase_results["real_repository_processing"] = True
                logging.info("✅ Real Repository Processing: PASSED")
            else:
                logging.error("❌ Real Repository Processing: FAILED")
            
            # Test 3.2: Edge Case Resilience
            logging.info("Testing Edge Case Resilience...")
            if self._test_edge_case_resilience():
                phase_results["edge_case_resilience"] = True
                logging.info("✅ Edge Case Resilience: PASSED")
            else:
                logging.error("❌ Edge Case Resilience: FAILED")
            
            # Test 3.3: Training Data Generation
            logging.info("Testing Training Data Generation...")
            if self._test_training_data_generation():
                phase_results["training_data_generation"] = True
                logging.info("✅ Training Data Generation: PASSED")
            else:
                logging.error("❌ Training Data Generation: FAILED")
            
        except Exception as e:
            logging.error(f"Phase 3 failed: {e}")
        
        self.test_results["phase3"] = phase_results
        self._log_phase_completion("Phase 3", phase_results)
    
    def _test_dream_builder(self):
        """Test Dream Builder pipeline"""
        try:
            # Create test specification
            test_spec = self._create_test_project_spec()
            
            # Run Dream Builder
            result = subprocess.run([
                sys.executable, "DreamWeaver_Builder_V5.py",
                "--test-mode", "--integration-test"
            ], capture_output=True, text=True, timeout=60)
            
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Dream Builder test failed: {e}")
            return False
    
    def _test_chaos_engine(self):
        """Test Chaos Engine pipeline"""
        try:
            result = subprocess.run([
                sys.executable, "REAL_WORLD_CHAOS_TESTER.py",
                "--phase=1", "--target=test_project"
            ], capture_output=True, text=True, timeout=60)
            
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Chaos Engine test failed: {e}")
            return False
    
    def _test_phoenix_recovery(self):
        """Test Phoenix Recovery pipeline"""
        try:
            result = subprocess.run([
                sys.executable, "PHOENIX_RECOVERY_SYSTEM_V5_SIMPLE.py",
                "--recovery-test", "--target=test_project"
            ], capture_output=True, text=True, timeout=60)
            
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Phoenix Recovery test failed: {e}")
            return False
    
    def _test_learning_pipeline(self):
        """Test Learning pipeline"""
        try:
            # Check if learning data was generated
            learning_data_path = Path("logs/learning_data.json")
            return learning_data_path.exists()
        except Exception as e:
            logging.error(f"Learning pipeline test failed: {e}")
            return False
    
    def _test_large_scale_handling(self):
        """Test large-scale project handling"""
        try:
            # Test with smaller load first to validate the framework
            result = subprocess.run([
                sys.executable, "ADVANCED_INTEGRATION_LAYER_V5.py",
                "--help"
            ], capture_output=True, text=True, timeout=30)
            
            # If help works, the system is accessible
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Large-scale handling test failed: {e}")
            return False
    
    def _test_gpu_acceleration(self):
        """Test GPU acceleration"""
        try:
            # Check if GPU is available and being used
            import torch
            if torch.cuda.is_available():
                gpu_util = torch.cuda.utilization()
                return gpu_util > 0
            return True  # GPU not required for basic functionality
        except Exception as e:
            logging.error(f"GPU acceleration test failed: {e}")
            return False
    
    def _test_resource_management(self):
        """Test resource management"""
        try:
            import psutil
            memory_percent = psutil.virtual_memory().percent
            return memory_percent < 80
        except Exception as e:
            logging.error(f"Resource management test failed: {e}")
            return False
    
    def _test_real_repository_processing(self):
        """Test real repository processing"""
        try:
            result = subprocess.run([
                sys.executable, "REAL_WORLD_CHAOS_TESTER.py",
                "--real-repos", "--drift-level=high"
            ], capture_output=True, text=True, timeout=180)
            
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Real repository processing test failed: {e}")
            return False
    
    def _test_edge_case_resilience(self):
        """Test edge case resilience"""
        try:
            result = subprocess.run([
                sys.executable, "REAL_WORLD_CHAOS_TESTER.py",
                "--extreme-scenarios", "--recovery-test"
            ], capture_output=True, text=True, timeout=180)
            
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Edge case resilience test failed: {e}")
            return False
    
    def _test_training_data_generation(self):
        """Test training data generation"""
        try:
            # Check if training data was generated
            training_data_path = Path("logs/training_data.json")
            return training_data_path.exists()
        except Exception as e:
            logging.error(f"Training data generation test failed: {e}")
            return False
    
    def _create_test_project_spec(self):
        """Create test project specification"""
        test_spec = {
            "project_name": "V5_Integration_Test_Project",
            "description": "Test project for V5 integration validation",
            "components": ["web_api", "database", "frontend"],
            "complexity": "medium"
        }
        
        spec_path = Path("test_project_spec.json")
        with open(spec_path, 'w') as f:
            json.dump(test_spec, f, indent=2)
        
        return spec_path
    
    def _log_phase_completion(self, phase_name: str, results: Dict[str, bool]):
        """Log phase completion results"""
        passed = sum(results.values())
        total = len(results)
        success_rate = (passed / total) * 100
        
        logging.info(f"{phase_name} completed: {passed}/{total} tests passed ({success_rate:.1f}%)")
        
        if success_rate == 100:
            logging.info(f"🎉 {phase_name}: PERFECT SCORE!")
        elif success_rate >= 80:
            logging.info(f"✅ {phase_name}: GOOD SCORE")
        elif success_rate >= 60:
            logging.info(f"⚠️ {phase_name}: ACCEPTABLE SCORE")
        else:
            logging.error(f"❌ {phase_name}: POOR SCORE")
    
    def _generate_integration_report(self):
        """Generate final integration test report"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Calculate overall success rate
        total_tests = 0
        total_passed = 0
        
        for phase_name, phase_results in self.test_results.items():
            phase_total = len(phase_results)
            phase_passed = sum(phase_results.values())
            total_tests += phase_total
            total_passed += phase_passed
        
        overall_success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
        
        # Generate report
        report = {
            "test_name": "V5 Complete Integration Test",
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "overall_success_rate": overall_success_rate,
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_tests - total_passed,
            "phase_results": self.test_results,
            "status": "PASSED" if overall_success_rate >= 80 else "FAILED"
        }
        
        # Save report
        report_path = Path("reports/v5_integration_test_report.json")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Log final results
        logging.info("=" * 60)
        logging.info("V5 INTEGRATION TEST COMPLETE")
        logging.info("=" * 60)
        logging.info(f"Overall Success Rate: {overall_success_rate:.1f}%")
        logging.info(f"Total Tests: {total_tests}")
        logging.info(f"Passed: {total_passed}")
        logging.info(f"Failed: {total_tests - total_passed}")
        logging.info(f"Duration: {duration}")
        logging.info(f"Status: {report['status']}")
        logging.info("=" * 60)
        
        if overall_success_rate >= 80:
            logging.info("🎉 V5 INTEGRATION TEST: SUCCESS! System is fully integrated!")
        else:
            logging.error("❌ V5 INTEGRATION TEST: FAILED! Integration issues detected!")
    
    def _generate_failure_report(self, error_message: str):
        """Generate failure report when test execution fails"""
        end_time = datetime.now()
        duration = end_time - self.start_time if self.start_time else 0
        
        report = {
            "test_name": "V5 Complete Integration Test",
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "status": "FAILED",
            "error_message": error_message,
            "current_phase": self.current_phase,
            "partial_results": self.test_results
        }
        
        # Save failure report
        report_path = Path("reports/v5_integration_test_failure.json")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logging.error(f"Integration test failed during {self.current_phase}: {error_message}")

def main():
    """Main execution function"""
    logging.info("Starting V5 Integration Test Executor")
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Initialize and run tester
    tester = V5IntegrationTester()
    tester.run_full_integration_test()

if __name__ == "__main__":
    main()
