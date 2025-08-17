#!/usr/bin/env python3
"""
Agent Exo-Suit V3.0 - Device Manager
Comprehensive device detection, configuration, and management for CPU/GPU/CPU+GPU modes
"""

import os
import sys
import platform
import subprocess
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeviceType(Enum):
    """Supported device types"""
    CPU = "cpu"
    GPU = "gpu"
    HYBRID = "hybrid"
    AUTO = "auto"

@dataclass
class DeviceInfo:
    """Device information container"""
    device_type: DeviceType
    name: str
    memory_gb: Optional[float] = None
    cores: Optional[int] = None
    available: bool = True
    fallback_available: bool = False
    performance_score: float = 0.0

@dataclass
class SystemCapabilities:
    """System capabilities summary"""
    cpu_info: DeviceInfo
    gpu_info: Optional[DeviceInfo] = None
    hybrid_available: bool = False
    recommended_mode: DeviceType = DeviceType.CPU
    fallback_strategy: str = "cpu_only"

class DeviceManager:
    """Comprehensive device management for RAG system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.cpu_info = None
        self.gpu_info = None
        self.system_capabilities = None
        
        # Initialize device detection
        self._detect_devices()
        self._analyze_capabilities()
    
    def _detect_devices(self):
        """Detect available CPU and GPU devices"""
        logger.info("Detecting system devices...")
        
        # CPU detection
        self.cpu_info = self._detect_cpu()
        
        # GPU detection
        self.gpu_info = self._detect_gpu()
        
        logger.info(f"Device detection complete - CPU: {self.cpu_info.available}, GPU: {self.gpu_info.available if self.gpu_info else False}")
    
    def _detect_cpu(self) -> DeviceInfo:
        """Detect CPU capabilities"""
        try:
            import multiprocessing as mp
            
            # Get CPU core count
            cpu_count = mp.cpu_count()
            
            # Get CPU architecture
            arch = platform.machine()
            processor = platform.processor()
            
            # Estimate performance score based on cores and architecture
            performance_score = min(cpu_count / 8.0, 1.0)  # Normalize to 8+ cores
            
            # Check for advanced CPU features
            advanced_features = self._check_cpu_features()
            if advanced_features:
                performance_score *= 1.2  # Boost for advanced features
            
            cpu_info = DeviceInfo(
                device_type=DeviceType.CPU,
                name=f"{processor} ({arch})",
                cores=cpu_count,
                available=True,
                fallback_available=True,
                performance_score=performance_score
            )
            
            logger.info(f"CPU detected: {cpu_info.name} with {cpu_info.cores} cores")
            return cpu_info
            
        except Exception as e:
            logger.warning(f"CPU detection failed: {e}")
            return DeviceInfo(
                device_type=DeviceType.CPU,
                name="Unknown CPU",
                available=False,
                fallback_available=False
            )
    
    def _detect_gpu(self) -> Optional[DeviceInfo]:
        """Detect GPU capabilities"""
        try:
            import torch
            
            if not torch.cuda.is_available():
                logger.info("CUDA not available")
                return None
            
            # Get GPU information
            gpu_count = torch.cuda.device_count()
            if gpu_count == 0:
                logger.info("No CUDA devices found")
                return None
            
            # Use primary GPU
            primary_gpu = 0
            gpu_name = torch.cuda.get_device_name(primary_gpu)
            gpu_props = torch.cuda.get_device_properties(primary_gpu)
            
            # Calculate memory in GB
            memory_gb = gpu_props.total_memory / (1024**3)
            
            # Calculate performance score based on memory and compute capability
            compute_cap = gpu_props.major + gpu_props.minor / 10.0
            performance_score = min(memory_gb / 8.0, 1.0) * min(compute_cap / 8.0, 1.0)
            
            # Check for advanced GPU features
            advanced_features = self._check_gpu_features()
            if advanced_features:
                performance_score *= 1.3  # Boost for advanced features
            
            gpu_info = DeviceInfo(
                device_type=DeviceType.GPU,
                name=gpu_name,
                memory_gb=memory_gb,
                available=True,
                fallback_available=True,
                performance_score=performance_score
            )
            
            logger.info(f"GPU detected: {gpu_info.name} with {gpu_info.memory_gb:.1f}GB VRAM")
            return gpu_info
            
        except ImportError:
            logger.info("PyTorch not available for GPU detection")
            return None
        except Exception as e:
            logger.warning(f"GPU detection failed: {e}")
            return None
    
    def _check_cpu_features(self) -> bool:
        """Check for advanced CPU features"""
        try:
            # Check for AVX2 support (common in modern CPUs)
            if platform.machine() == 'x86_64':
                # This is a simplified check - in production you'd use CPUID
                return True
            return False
        except:
            return False
    
    def _check_gpu_features(self) -> bool:
        """Check for advanced GPU features"""
        try:
            import torch
            if torch.cuda.is_available():
                # Check for Tensor Cores (Volta+ architecture)
                gpu_props = torch.cuda.get_device_properties(0)
                return gpu_props.major >= 7  # Volta and newer
            return False
        except:
            return False
    
    def _analyze_capabilities(self):
        """Analyze system capabilities and determine optimal configuration"""
        logger.info("Analyzing system capabilities...")
        
        # Determine hybrid availability
        hybrid_available = (
            self.cpu_info and self.cpu_info.available and
            self.gpu_info and self.gpu_info.available
        )
        
        # Determine recommended mode
        if hybrid_available:
            # Compare performance scores
            if self.gpu_info.performance_score > self.cpu_info.performance_score * 1.5:
                recommended_mode = DeviceType.GPU
            elif self.gpu_info.performance_score > self.cpu_info.performance_score:
                recommended_mode = DeviceType.HYBRID
            else:
                recommended_mode = DeviceType.CPU
        elif self.gpu_info and self.gpu_info.available:
            recommended_mode = DeviceType.GPU
        else:
            recommended_mode = DeviceType.CPU
        
        # Determine fallback strategy
        if hybrid_available:
            fallback_strategy = "gpu_to_cpu"
        elif self.gpu_info and self.gpu_info.available:
            fallback_strategy = "gpu_to_cpu"
        else:
            fallback_strategy = "cpu_only"
        
        self.system_capabilities = SystemCapabilities(
            cpu_info=self.cpu_info,
            gpu_info=self.gpu_info,
            hybrid_available=hybrid_available,
            recommended_mode=recommended_mode,
            fallback_strategy=fallback_strategy
        )
        
        logger.info(f"System analysis complete - Recommended mode: {recommended_mode.value}")
    
    def get_optimal_configuration(self, mode: DeviceType = DeviceType.AUTO) -> Dict[str, Any]:
        """Get optimal configuration for specified mode"""
        if mode == DeviceType.AUTO:
            mode = self.system_capabilities.recommended_mode
        
        config = {
            'mode': mode.value,
            'device_type': mode.value,
            'fallback_strategy': self.system_capabilities.fallback_strategy,
            'performance_optimizations': {}
        }
        
        if mode == DeviceType.CPU:
            config.update(self._get_cpu_config())
        elif mode == DeviceType.GPU:
            config.update(self._get_gpu_config())
        elif mode == DeviceType.HYBRID:
            config.update(self._get_hybrid_config())
        
        return config
    
    def _get_cpu_config(self) -> Dict[str, Any]:
        """Get CPU-optimized configuration"""
        return {
            'device': 'cpu',
            'num_workers': min(self.cpu_info.cores, 8),  # Cap at 8 workers
            'chunk_size': 512,
            'batch_size': 32,
            'use_mkl': True,
            'memory_mapping': True
        }
    
    def _get_gpu_config(self) -> Dict[str, Any]:
        """Get GPU-optimized configuration"""
        if not self.gpu_info:
            return self._get_cpu_config()
        
        return {
            'device': 'cuda:0',
            'memory_fraction': 0.8,
            'mixed_precision': True,
            'chunk_size': 1024,
            'batch_size': 64,
            'warmup_batches': 3
        }
    
    def _get_hybrid_config(self) -> Dict[str, Any]:
        """Get hybrid CPU+GPU configuration"""
        cpu_config = self._get_cpu_config()
        gpu_config = self._get_gpu_config()
        
        return {
            'cpu_config': cpu_config,
            'gpu_config': gpu_config,
            'gpu_threshold': 0.6,  # Use GPU for queries above this threshold
            'cpu_fallback_threshold': 0.3,
            'parallel_processing': True,
            'load_balancing': 'dynamic'
        }
    
    def validate_requirements(self) -> Tuple[bool, List[str]]:
        """Validate that all required packages are available"""
        required_packages = [
            'torch',
            'numpy',
            'sentence_transformers',
            'faiss'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        return len(missing_packages) == 0, missing_packages
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive system summary"""
        return {
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'machine': platform.machine(),
                'processor': platform.processor()
            },
            'devices': {
                'cpu': {
                    'available': self.cpu_info.available if self.cpu_info else False,
                    'name': self.cpu_info.name if self.cpu_info else 'Unknown',
                    'cores': self.cpu_info.cores if self.cpu_info else 0,
                    'performance_score': self.cpu_info.performance_score if self.cpu_info else 0.0
                },
                'gpu': {
                    'available': self.gpu_info.available if self.gpu_info else False,
                    'name': self.gpu_info.name if self.gpu_info else 'None',
                    'memory_gb': self.gpu_info.memory_gb if self.gpu_info else 0.0,
                    'performance_score': self.gpu_info.performance_score if self.gpu_info else 0.0
                }
            },
            'capabilities': {
                'hybrid_available': self.system_capabilities.hybrid_available,
                'recommended_mode': self.system_capabilities.recommended_mode.value,
                'fallback_strategy': self.system_capabilities.fallback_strategy
            },
            'requirements': {
                'all_available': self.validate_requirements()[0],
                'missing_packages': self.validate_requirements()[1]
            }
        }
    
    def print_system_summary(self):
        """Print formatted system summary"""
        summary = self.get_system_summary()
        
        print("\n" + "="*60)
        print("AGENT EXO-SUIT V3.0 - SYSTEM CAPABILITIES")
        print("="*60)
        
        # Platform info
        print(f"Platform: {summary['platform']['system']} {summary['platform']['release']}")
        print(f"Architecture: {summary['platform']['machine']}")
        print(f"Processor: {summary['platform']['processor']}")
        
        # Device info
        print(f"\nCPU: {summary['devices']['cpu']['name']}")
        print(f"  Cores: {summary['devices']['cpu']['cores']}")
        print(f"  Performance Score: {summary['devices']['cpu']['performance_score']:.2f}")
        
        if summary['devices']['gpu']['available']:
            print(f"\nGPU: {summary['devices']['gpu']['name']}")
            print(f"  Memory: {summary['devices']['gpu']['memory_gb']:.1f} GB")
            print(f"  Performance Score: {summary['devices']['gpu']['performance_score']:.2f}")
        else:
            print("\nGPU: Not available")
        
        # Capabilities
        print(f"\nCapabilities:")
        print(f"  Hybrid Mode: {'Available' if summary['capabilities']['hybrid_available'] else 'Not Available'}")
        print(f"  Recommended Mode: {summary['capabilities']['recommended_mode'].upper()}")
        print(f"  Fallback Strategy: {summary['capabilities']['fallback_strategy']}")
        
        # Requirements
        print(f"\nRequirements:")
        if summary['requirements']['all_available']:
            print("  OK - All required packages available")
        else:
            print(f"  FAILED - Missing packages: {', '.join(summary['requirements']['missing_packages'])}")
        
        print("="*60)


def main():
    """Test the device manager"""
    print("Testing Device Manager...")
    
    # Create device manager
    manager = DeviceManager()
    
    # Print system summary
    manager.print_system_summary()
    
    # Get optimal configuration for different modes
    print("\nOptimal Configurations:")
    for mode in [DeviceType.CPU, DeviceType.GPU, DeviceType.HYBRID]:
        if mode == DeviceType.HYBRID and not manager.system_capabilities.hybrid_available:
            continue
        config = manager.get_optimal_configuration(mode)
        print(f"\n{mode.value.upper()} Mode:")
        for key, value in config.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
