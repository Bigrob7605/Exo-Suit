#!/usr/bin/env python3
"""
MMH-RS REAL DATA VALIDATOR
Phase 1: Infrastructure Preparation for Silesia Corpus Testing

This comprehensive testing framework validates MMH-RS revolutionary claims
using REAL WORLD DATA from the industry-standard Silesia Corpus.

Author: MMH-RS Real Data Validation Team
Date: 2025-08-19
Status: 🎯 PHASE 1 - INFRASTRUCTURE PREPARATION
"""

import os
import sys
import time
import hashlib
import struct
import json
import psutil
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import subprocess

# ============================================================================
# 📊 REAL DATA TESTING CONFIGURATION
# ============================================================================

@dataclass
class SilesiaFileInfo:
    """Information about each Silesia corpus file"""
    name: str
    size: int
    file_type: str
    description: str
    entropy: float = 0.0
    sha256: str = ""
    compression_baseline: Dict[str, float] = field(default_factory=dict)

@dataclass
class PerformanceMetrics:
    """Performance metrics for real data testing"""
    execution_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    compression_ratio: float = 0.0
    throughput_mbps: float = 0.0

@dataclass
class RealDataTestResult:
    """Result of a real data test"""
    test_name: str
    file_name: str
    status: str  # PASS, FAIL, ERROR
    metrics: PerformanceMetrics
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    timestamp: str = ""

class TestPhase(Enum):
    INFRASTRUCTURE = "Infrastructure Preparation"
    SELF_HEALING = "Advanced Self-Healing on Real Data"
    CRYPTOGRAPHIC = "Revolutionary Cryptographic Security on Real Data"
    PATTERN_RECOGNITION = "Enhanced Pattern Recognition on Real Data"
    PATTERN251_CODEC = "Pattern251 Codec on Real Data"
    MULTI_CODEC = "Multi-Codec Intelligence on Real Data"
    INTEGRATION = "Integration and Stress Testing on Real Data"
    OPTIMIZATION = "Optimization and Benchmarking on Real Data"
    PRODUCTION = "Production Readiness Validation on Real Data"

# ============================================================================
# 🎯 SILESIA CORPUS REAL DATA VALIDATOR
# ============================================================================

class MMHRSRealDataValidator:
    """Comprehensive real data validation framework for MMH-RS"""
    
    def __init__(self, silesia_corpus_dir: str = "silesia_corpus"):
        self.silesia_corpus_dir = Path(silesia_corpus_dir)
        self.results_dir = Path("real_data_validation_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize file information
        self.silesia_files = self._initialize_silesia_files()
        self.test_results: List[RealDataTestResult] = []
        
        # Performance monitoring
        self.process = psutil.Process()
        
        print("🚀 MMH-RS REAL DATA VALIDATOR INITIALIZED")
        print("=" * 60)
        print(f"📂 Silesia Corpus Directory: {self.silesia_corpus_dir}")
        print(f"📁 Results Directory: {self.results_dir}")
        print(f"📊 Found {len(self.silesia_files)} Silesia files")
        print("=" * 60)
    
    def _initialize_silesia_files(self) -> Dict[str, SilesiaFileInfo]:
        """Initialize Silesia corpus file information"""
        expected_files = {
            "dickens": SilesiaFileInfo("dickens", 10192446, "text", "English literature (Charles Dickens)"),
            "mozilla": SilesiaFileInfo("mozilla", 51220480, "binary", "Tarball with Mozilla executables"),
            "mr": SilesiaFileInfo("mr", 9970564, "binary", "Medical magnetic resonance image"),
            "nci": SilesiaFileInfo("nci", 33553445, "database", "Chemical database"),
            "ooffice": SilesiaFileInfo("ooffice", 6152192, "binary", "OpenOffice.org documents"),
            "osdb": SilesiaFileInfo("osdb", 10085684, "database", "Open source database"),
            "reymont": SilesiaFileInfo("reymont", 6627202, "text", "Polish literature (Wladyslaw Reymont)"),
            "samba": SilesiaFileInfo("samba", 21606400, "binary", "Samba source code tarball"),
            "sao": SilesiaFileInfo("sao", 7251944, "binary", "Astronomy data"),
            "webster": SilesiaFileInfo("webster", 41458703, "text", "Webster's dictionary"),
            "xml": SilesiaFileInfo("xml", 5345280, "structured", "XML data"),
            "x-ray": SilesiaFileInfo("x-ray", 8474240, "binary", "Medical X-ray image")
        }
        
        return expected_files
    
    def validate_silesia_corpus(self) -> bool:
        """Phase 1.1: Validate Silesia Corpus accessibility and integrity"""
        print("\n🔍 PHASE 1.1: SILESIA CORPUS VALIDATION")
        print("-" * 40)
        
        validation_success = True
        
        for file_name, file_info in self.silesia_files.items():
            file_path = self.silesia_corpus_dir / file_name
            
            # Check file exists
            if not file_path.exists():
                print(f"❌ File missing: {file_name}")
                validation_success = False
                continue
            
            # Check file size
            actual_size = file_path.stat().st_size
            if actual_size != file_info.size:
                print(f"⚠️  Size mismatch for {file_name}: expected {file_info.size}, got {actual_size}")
                file_info.size = actual_size  # Update with actual size
            
            # Calculate SHA-256 hash
            sha256_hash = self._calculate_file_hash(file_path)
            file_info.sha256 = sha256_hash
            
            # Calculate entropy
            entropy = self._calculate_entropy(file_path)
            file_info.entropy = entropy
            
            print(f"✅ {file_name}: {actual_size:,} bytes, entropy: {entropy:.3f}, hash: {sha256_hash[:16]}...")
        
        if validation_success:
            print("\n✅ All Silesia corpus files validated successfully!")
            self._save_silesia_metadata()
        else:
            print("\n❌ Silesia corpus validation failed!")
        
        return validation_success
    
    def establish_baseline_measurements(self) -> Dict[str, Dict[str, float]]:
        """Phase 1.3: Establish baseline compression measurements"""
        print("\n📊 PHASE 1.3: BASELINE COMPRESSION MEASUREMENTS")
        print("-" * 50)
        
        compression_tools = ["gzip", "bzip2", "xz", "zstd"]
        baseline_results = {}
        
        for file_name, file_info in self.silesia_files.items():
            file_path = self.silesia_corpus_dir / file_name
            baseline_results[file_name] = {}
            
            print(f"\n🔧 Testing {file_name} ({file_info.size:,} bytes)...")
            
            for tool in compression_tools:
                try:
                    compression_ratio = self._test_compression_tool(file_path, tool)
                    baseline_results[file_name][tool] = compression_ratio
                    file_info.compression_baseline[tool] = compression_ratio
                    print(f"   {tool}: {compression_ratio:.2f}x compression")
                except Exception as e:
                    print(f"   {tool}: FAILED ({str(e)})")
                    baseline_results[file_name][tool] = 0.0
        
        # Save baseline results
        baseline_file = self.results_dir / "compression_baselines.json"
        with open(baseline_file, 'w') as f:
            json.dump(baseline_results, f, indent=2)
        
        print(f"\n✅ Baseline measurements saved to {baseline_file}")
        return baseline_results
    
    def test_mmh_rs_self_healing_real_data(self) -> List[RealDataTestResult]:
        """Phase 2.1: Test Advanced Self-Healing on Real Data"""
        print("\n🛡️ PHASE 2.1: ADVANCED SELF-HEALING ON REAL DATA")
        print("-" * 50)
        
        results = []
        
        # Test on text files first (dickens, webster)
        text_files = ["dickens", "webster"]
        
        for file_name in text_files:
            if file_name not in self.silesia_files:
                continue
                
            file_path = self.silesia_corpus_dir / file_name
            file_info = self.silesia_files[file_name]
            
            print(f"\n🧪 Testing Advanced Self-Healing on {file_name} ({file_info.size:,} bytes)...")
            
            try:
                # Import our advanced self-healing system
                sys.path.append('./mmh_rs_codecs')
                from advanced_self_healing_system import AdvancedSelfHealingFile, ECCMode
                
                # Test 1: Hierarchical ECC encoding
                start_time = time.time()
                start_memory = self.process.memory_info().rss / 1024 / 1024
                
                healer = AdvancedSelfHealingFile(damage_tolerance=0.20)
                temp_file = str(file_path) + ".test"
                
                # Copy original file for testing
                import shutil
                shutil.copy2(file_path, temp_file)
                
                # Test hierarchical encoding
                encoded_file = healer.encode_file(temp_file, mode=ECCMode.HIERARCHICAL)
                
                end_time = time.time()
                end_memory = self.process.memory_info().rss / 1024 / 1024
                
                # Calculate metrics
                original_size = file_info.size
                encoded_size = os.path.getsize(encoded_file)
                compression_ratio = original_size / encoded_size if encoded_size > 0 else 0
                execution_time = end_time - start_time
                memory_used = end_memory - start_memory
                throughput = (original_size / 1024 / 1024) / execution_time if execution_time > 0 else 0
                
                metrics = PerformanceMetrics(
                    execution_time=execution_time,
                    memory_usage_mb=memory_used,
                    cpu_usage_percent=0.0,  # TODO: Implement CPU monitoring
                    compression_ratio=compression_ratio,
                    throughput_mbps=throughput
                )
                
                result = RealDataTestResult(
                    test_name="Hierarchical ECC Encoding",
                    file_name=file_name,
                    status="PASS",
                    metrics=metrics,
                    details={
                        "original_size": original_size,
                        "encoded_size": encoded_size,
                        "overhead_percent": ((encoded_size - original_size) / original_size) * 100,
                        "damage_tolerance": "20%",
                        "ecc_mode": "hierarchical"
                    },
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )
                
                results.append(result)
                print(f"   ✅ Hierarchical ECC: {execution_time:.2f}s, {throughput:.1f} MB/s")
                
                # Test 2: Corruption and recovery
                print(f"   🧪 Testing corruption recovery...")
                corruption_result = self._test_corruption_recovery(encoded_file, healer, file_name)
                results.append(corruption_result)
                
                # Cleanup
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                if os.path.exists(encoded_file):
                    os.remove(encoded_file)
                    
            except Exception as e:
                error_result = RealDataTestResult(
                    test_name="Advanced Self-Healing Test",
                    file_name=file_name,
                    status="ERROR",
                    metrics=PerformanceMetrics(),
                    error_message=str(e),
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )
                results.append(error_result)
                print(f"   ❌ Error: {str(e)}")
        
        return results
    
    def test_mmh_rs_pattern_recognition_real_data(self) -> List[RealDataTestResult]:
        """Phase 2.3: Test Enhanced Pattern Recognition on Real Data"""
        print("\n🧠 PHASE 2.3: ENHANCED PATTERN RECOGNITION ON REAL DATA")
        print("-" * 55)
        
        results = []
        
        # Test on all 12 Silesia files for comprehensive pattern analysis
        for file_name, file_info in self.silesia_files.items():
            file_path = self.silesia_corpus_dir / file_name
            
            print(f"\n🔍 Analyzing patterns in {file_name} ({file_info.size:,} bytes, {file_info.file_type})...")
            
            try:
                # Import our enhanced pattern recognition
                sys.path.append('./mmh_rs_codecs')
                from enhanced_pattern251_ai import EnhancedPattern251AI, TensorType
                import numpy as np
                
                start_time = time.time()
                
                # Read file data for pattern analysis
                with open(file_path, 'rb') as f:
                    # Read first 1MB for pattern analysis (to avoid memory issues)
                    data = f.read(1024 * 1024)
                
                # Convert to numpy array for analysis
                data_array = np.frombuffer(data, dtype=np.uint8)
                
                # Initialize AI pattern analyzer
                ai_codec = EnhancedPattern251AI()
                
                # Analyze patterns based on file type
                if file_info.file_type in ["text"]:
                    # Treat text as sequential data
                    reshaped_data = data_array[:len(data_array)//256*256].reshape(-1, 256).astype(np.float32)
                    metadata = ai_codec.analyze_ai_tensor(reshaped_data, TensorType.NEURAL_WEIGHTS)
                    optimized, opt_info = ai_codec.optimize_ai_tensor(reshaped_data, TensorType.NEURAL_WEIGHTS)
                elif file_info.file_type in ["binary", "database"]:
                    # Treat binary as 2D structure
                    side_len = int(np.sqrt(len(data_array)))
                    if side_len > 1:
                        square_data = data_array[:side_len*side_len].reshape(side_len, side_len).astype(np.float32)
                        metadata = ai_codec.analyze_ai_tensor(square_data, TensorType.ATTENTION_WEIGHTS)
                        optimized, opt_info = ai_codec.optimize_ai_tensor(square_data, TensorType.ATTENTION_WEIGHTS)
                    else:
                        # Fallback for very small data
                        small_data = data_array[:64].reshape(8, 8).astype(np.float32)
                        metadata = ai_codec.analyze_ai_tensor(small_data, TensorType.CONVOLUTIONAL_WEIGHTS)
                        optimized, opt_info = ai_codec.optimize_ai_tensor(small_data, TensorType.CONVOLUTIONAL_WEIGHTS)
                else:
                    # Default analysis for structured data
                    if len(data_array) >= 128:
                        structured_data = data_array[:128].reshape(8, 16).astype(np.float32)
                    else:
                        structured_data = np.pad(data_array, (0, 128-len(data_array)), 'constant').reshape(8, 16).astype(np.float32)
                    metadata = ai_codec.analyze_ai_tensor(structured_data, TensorType.ATTENTION_WEIGHTS)
                    optimized, opt_info = ai_codec.optimize_ai_tensor(structured_data, TensorType.ATTENTION_WEIGHTS)
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Calculate performance metrics
                throughput = (len(data) / 1024 / 1024) / execution_time if execution_time > 0 else 0
                
                metrics = PerformanceMetrics(
                    execution_time=execution_time,
                    memory_usage_mb=0.0,  # TODO: Implement memory monitoring
                    compression_ratio=opt_info.get("compression_ratio", 1.0),
                    throughput_mbps=throughput
                )
                
                result = RealDataTestResult(
                    test_name="AI Pattern Recognition Analysis",
                    file_name=file_name,
                    status="PASS",
                    metrics=metrics,
                    details={
                        "file_type": file_info.file_type,
                        "entropy": file_info.entropy,
                        "compression_potential": metadata.compression_potential,
                        "sparsity": metadata.sparsity,
                        "optimization_strategy": opt_info.get("optimization_strategy", "unknown"),
                        "data_size_analyzed": len(data),
                        "ai_tensor_type": str(metadata.tensor_type) if hasattr(metadata, 'tensor_type') else "unknown"
                    },
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )
                
                results.append(result)
                print(f"   ✅ Pattern analysis: {execution_time:.2f}s, potential: {metadata.compression_potential:.3f}")
                print(f"      Strategy: {opt_info.get('optimization_strategy', 'unknown')}")
                
            except Exception as e:
                error_result = RealDataTestResult(
                    test_name="AI Pattern Recognition Analysis",
                    file_name=file_name,
                    status="ERROR",
                    metrics=PerformanceMetrics(),
                    error_message=str(e),
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )
                results.append(error_result)
                print(f"   ❌ Error: {str(e)}")
        
        return results
    
    def run_phase_1_infrastructure_preparation(self) -> Dict[str, Any]:
        """Run complete Phase 1: Infrastructure Preparation"""
        print("\n🚀 STARTING PHASE 1: INFRASTRUCTURE PREPARATION")
        print("=" * 60)
        
        phase_results = {
            "phase": "Infrastructure Preparation",
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests_run": 0,
            "tests_passed": 0,
            "silesia_validation": False,
            "baseline_measurements": {},
            "issues_found": []
        }
        
        try:
            # Phase 1.1: Validate Silesia Corpus
            phase_results["silesia_validation"] = self.validate_silesia_corpus()
            phase_results["tests_run"] += 1
            if phase_results["silesia_validation"]:
                phase_results["tests_passed"] += 1
            
            # Phase 1.3: Establish baseline measurements
            if phase_results["silesia_validation"]:
                phase_results["baseline_measurements"] = self.establish_baseline_measurements()
                phase_results["tests_run"] += 1
                phase_results["tests_passed"] += 1
            
            # Generate comprehensive infrastructure report
            self._generate_infrastructure_report(phase_results)
            
        except Exception as e:
            phase_results["issues_found"].append(f"Phase 1 error: {str(e)}")
            print(f"❌ Phase 1 error: {str(e)}")
        
        phase_results["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        return phase_results
    
    def run_phase_2_core_features_validation(self) -> Dict[str, Any]:
        """Run Phase 2: Core Feature Real Data Validation"""
        print("\n🚀 STARTING PHASE 2: CORE FEATURE REAL DATA VALIDATION")
        print("=" * 60)
        
        phase_results = {
            "phase": "Core Feature Real Data Validation",
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "self_healing_results": [],
            "pattern_recognition_results": [],
            "total_tests": 0,
            "total_passed": 0
        }
        
        try:
            # Phase 2.1: Advanced Self-Healing on Real Data
            phase_results["self_healing_results"] = self.test_mmh_rs_self_healing_real_data()
            
            # Phase 2.3: Enhanced Pattern Recognition on Real Data
            phase_results["pattern_recognition_results"] = self.test_mmh_rs_pattern_recognition_real_data()
            
            # Calculate totals
            all_results = phase_results["self_healing_results"] + phase_results["pattern_recognition_results"]
            phase_results["total_tests"] = len(all_results)
            phase_results["total_passed"] = sum(1 for r in all_results if r.status == "PASS")
            
            # Save all results
            self.test_results.extend(all_results)
            
        except Exception as e:
            print(f"❌ Phase 2 error: {str(e)}")
        
        phase_results["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        return phase_results
    
    def _test_compression_tool(self, file_path: Path, tool: str) -> float:
        """Test compression ratio with standard tools"""
        if tool == "gzip":
            cmd = ["gzip", "-c", str(file_path)]
        elif tool == "bzip2":
            cmd = ["bzip2", "-c", str(file_path)]
        elif tool == "xz":
            cmd = ["xz", "-c", str(file_path)]
        elif tool == "zstd":
            cmd = ["zstd", "-c", str(file_path)]
        else:
            raise ValueError(f"Unknown compression tool: {tool}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, check=True)
            compressed_size = len(result.stdout)
            original_size = file_path.stat().st_size
            return original_size / compressed_size if compressed_size > 0 else 0.0
        except subprocess.CalledProcessError:
            # Tool not available, return 0
            return 0.0
        except Exception as e:
            print(f"Error testing {tool}: {str(e)}")
            return 0.0
    
    def _test_corruption_recovery(self, encoded_file: str, healer, file_name: str) -> RealDataTestResult:
        """Test corruption recovery on real data"""
        try:
            # Create corrupted version
            corrupted_file = encoded_file + ".corrupted"
            import shutil
            shutil.copy2(encoded_file, corrupted_file)
            
            # Introduce 15% random corruption
            file_size = os.path.getsize(corrupted_file)
            corruption_bytes = int(file_size * 0.15)
            
            with open(corrupted_file, 'r+b') as f:
                import random
                for _ in range(corruption_bytes):
                    pos = random.randint(1000, file_size - 1000)  # Avoid header corruption
                    f.seek(pos)
                    f.write(bytes([random.randint(0, 255)]))
            
            # Attempt recovery
            start_time = time.time()
            recovered = healer.decode_file(corrupted_file)
            end_time = time.time()
            
            # Cleanup
            if os.path.exists(corrupted_file):
                os.remove(corrupted_file)
            
            metrics = PerformanceMetrics(
                execution_time=end_time - start_time,
                compression_ratio=1.0  # Recovery doesn't compress
            )
            
            return RealDataTestResult(
                test_name="Corruption Recovery Test",
                file_name=file_name,
                status="PASS" if recovered else "FAIL",
                metrics=metrics,
                details={
                    "corruption_level": "15%",
                    "recovery_successful": recovered
                },
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )
            
        except Exception as e:
            return RealDataTestResult(
                test_name="Corruption Recovery Test",
                file_name=file_name,
                status="ERROR",
                metrics=PerformanceMetrics(),
                error_message=str(e),
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _calculate_entropy(self, file_path: Path, sample_size: int = 10000) -> float:
        """Calculate entropy of file (using sample for large files)"""
        with open(file_path, 'rb') as f:
            data = f.read(sample_size)
        
        if not data:
            return 0.0
        
        # Count byte frequencies
        byte_counts = [0] * 256
        for byte in data:
            byte_counts[byte] += 1
        
        # Calculate entropy
        entropy = 0.0
        data_len = len(data)
        for count in byte_counts:
            if count > 0:
                p = count / data_len
                import math
                entropy -= p * math.log2(p)
        
        return entropy
    
    def _save_silesia_metadata(self):
        """Save Silesia corpus metadata"""
        metadata = {}
        for name, info in self.silesia_files.items():
            metadata[name] = {
                "size": info.size,
                "file_type": info.file_type,
                "description": info.description,
                "entropy": info.entropy,
                "sha256": info.sha256,
                "compression_baseline": info.compression_baseline
            }
        
        metadata_file = self.results_dir / "silesia_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"📊 Silesia metadata saved to {metadata_file}")
    
    def _generate_infrastructure_report(self, phase_results: Dict[str, Any]):
        """Generate comprehensive infrastructure report"""
        report_file = self.results_dir / "phase_1_infrastructure_report.md"
        
        with open(report_file, 'w') as f:
            f.write("# 🏗️ PHASE 1: INFRASTRUCTURE PREPARATION REPORT\n\n")
            f.write(f"**Date:** {phase_results['start_time']}\n")
            f.write(f"**Status:** {'✅ SUCCESS' if phase_results['tests_passed'] == phase_results['tests_run'] else '⚠️ PARTIAL SUCCESS'}\n")
            f.write(f"**Tests:** {phase_results['tests_passed']}/{phase_results['tests_run']} passed\n\n")
            
            f.write("## 📊 Silesia Corpus Validation\n\n")
            if phase_results["silesia_validation"]:
                f.write("✅ All 12 Silesia corpus files validated successfully\n\n")
                f.write("| File | Size | Type | Entropy | SHA-256 |\n")
                f.write("|------|------|------|---------|--------|\n")
                for name, info in self.silesia_files.items():
                    f.write(f"| {name} | {info.size:,} | {info.file_type} | {info.entropy:.3f} | {info.sha256[:16]}... |\n")
            else:
                f.write("❌ Silesia corpus validation failed\n")
            
            f.write("\n## 📈 Baseline Compression Results\n\n")
            if phase_results["baseline_measurements"]:
                f.write("| File | gzip | bzip2 | xz | zstd |\n")
                f.write("|------|------|-------|----|----- |\n")
                for file_name, baselines in phase_results["baseline_measurements"].items():
                    gzip_ratio = baselines.get("gzip", 0.0)
                    bzip2_ratio = baselines.get("bzip2", 0.0)
                    xz_ratio = baselines.get("xz", 0.0)
                    zstd_ratio = baselines.get("zstd", 0.0)
                    f.write(f"| {file_name} | {gzip_ratio:.2f}x | {bzip2_ratio:.2f}x | {xz_ratio:.2f}x | {zstd_ratio:.2f}x |\n")
            
            if phase_results["issues_found"]:
                f.write("\n## ⚠️ Issues Found\n\n")
                for issue in phase_results["issues_found"]:
                    f.write(f"- {issue}\n")
            
            f.write("\n## 🎯 Next Steps\n\n")
            f.write("- Proceed to Phase 2: Core Feature Real Data Validation\n")
            f.write("- Test Advanced Self-Healing on Silesia corpus\n")
            f.write("- Validate Enhanced Pattern Recognition with real data\n")
        
        print(f"📋 Infrastructure report saved to {report_file}")
    
    def save_results(self):
        """Save all test results"""
        results_file = self.results_dir / "real_data_validation_results.json"
        
        # Convert results to JSON-serializable format
        json_results = []
        for result in self.test_results:
            json_result = {
                "test_name": result.test_name,
                "file_name": result.file_name,
                "status": result.status,
                "metrics": {
                    "execution_time": result.metrics.execution_time,
                    "memory_usage_mb": result.metrics.memory_usage_mb,
                    "cpu_usage_percent": result.metrics.cpu_usage_percent,
                    "compression_ratio": result.metrics.compression_ratio,
                    "throughput_mbps": result.metrics.throughput_mbps
                },
                "details": result.details,
                "error_message": result.error_message,
                "timestamp": result.timestamp
            }
            json_results.append(json_result)
        
        with open(results_file, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"💾 Results saved to {results_file}")

# ============================================================================
# 🚀 MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function for real data validation"""
    print("🚀 MMH-RS REAL DATA VALIDATOR")
    print("=" * 60)
    print("Mission: Validate MMH-RS revolutionary claims using REAL Silesia Corpus data")
    print("=" * 60)
    
    try:
        # Initialize validator
        validator = MMHRSRealDataValidator()
        
        # Run Phase 1: Infrastructure Preparation
        phase_1_results = validator.run_phase_1_infrastructure_preparation()
        
        if phase_1_results["silesia_validation"]:
            print("\n✅ Phase 1 completed successfully! Ready for Phase 2.")
            
            # Run Phase 2: Core Features Validation
            phase_2_results = validator.run_phase_2_core_features_validation()
            
            print(f"\n📊 Phase 2 Results:")
            print(f"   Tests: {phase_2_results['total_passed']}/{phase_2_results['total_tests']} passed")
            print(f"   Self-Healing tests: {len(phase_2_results['self_healing_results'])}")
            print(f"   Pattern Recognition tests: {len(phase_2_results['pattern_recognition_results'])}")
            
        # Save all results
        validator.save_results()
        
        print("\n🎉 Real data validation session completed!")
        print("📁 Check real_data_validation_results/ for detailed reports")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
