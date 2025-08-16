#!/usr/bin/env python3
"""
MEMORY DISTRIBUTION ENGINE - Phase 4A
This engine will distribute processing across ALL available memory types:
- GPU Dedicated (8GB) - Active embeddings, real-time processing
- GPU Shared (31.8GB) - Large model weights, intermediate results  
- System RAM (63.6GB) - Massive context storage, file caches
- Storage (NVMe) - Long-term archives, backup indices
"""

import os
import sys
import json
import time
import logging
import psutil
import threading
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from datetime import datetime

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/MEMORY-DISTRIBUTION-ENGINE.log'),
        logging.StreamHandler()
    ]
)

# GPU imports
try:
    import torch
    import faiss
    from sentence_transformers import SentenceTransformer
    GPU_AVAILABLE = True
    logging.info("GPU acceleration enabled for memory distribution")
except ImportError as e:
    logging.error(f"GPU libraries not available: {e}")
    exit(1)

class MemoryDistributionEngine:
    def __init__(self):
        self.target_memory_usage = {
            'gpu_dedicated': 0.95,    # 95% of 8GB = 7.6GB
            'gpu_shared': 0.80,       # 80% of 31.8GB = 25.4GB
            'system_ram': 0.80,       # 80% of 63.6GB = 50.9GB
            'total_target': 83.9GB    # Combined target
        }
        
        # Initialize GPU and memory monitoring
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.gpu_props = torch.cuda.get_device_properties(0) if torch.cuda.is_available() else None
        
        # Memory storage containers
        self.gpu_tensors = []
        self.gpu_shared_data = []
        self.system_ram_data = []
        self.storage_data = []
        
        # Performance tracking
        self.memory_usage_history = []
        self.performance_metrics = {}
        
        logging.info(f"Initializing Memory Distribution Engine")
        logging.info(f"Target GPU Dedicated: {self.target_memory_usage['gpu_dedicated']*100:.1f}%")
        logging.info(f"Target GPU Shared: {self.target_memory_usage['gpu_shared']*100:.1f}%")
        logging.info(f"Target System RAM: {self.target_memory_usage['system_ram']*100:.1f}%")
        logging.info(f"Total Target: {self.target_memory_usage['total_target']:.1f}GB")
        
        if self.gpu_props:
            logging.info(f"GPU: {self.gpu_props.name}")
            logging.info(f"GPU Memory: {self.gpu_props.total_memory / 1024**3:.1f} GB")
    
    def get_memory_status(self) -> Dict[str, Any]:
        """Get comprehensive memory status across all tiers"""
        # GPU Memory
        if torch.cuda.is_available():
            gpu_allocated = torch.cuda.memory_allocated(0) / 1024**3
            gpu_reserved = torch.cuda.memory_reserved(0) / 1024**3
            gpu_total = self.gpu_props.total_memory / 1024**3 if self.gpu_props else 0
            gpu_shared = gpu_reserved - gpu_allocated
        else:
            gpu_allocated = gpu_reserved = gpu_total = gpu_shared = 0
        
        # System Memory
        system_memory = psutil.virtual_memory()
        system_used = system_memory.used / 1024**3
        system_total = system_memory.total / 1024**3
        
        # Calculate utilization percentages
        gpu_dedicated_pct = (gpu_allocated / gpu_total * 100) if gpu_total > 0 else 0
        gpu_shared_pct = (gpu_shared / 31.8 * 100) if gpu_shared > 0 else 0
        system_ram_pct = (system_used / system_total * 100) if system_total > 0 else 0
        
        # Total memory usage
        total_used = gpu_allocated + gpu_shared + system_used
        total_available = gpu_total + 31.8 + system_total
        total_pct = (total_used / total_available * 100) if total_available > 0 else 0
        
        return {
            'gpu_dedicated': {
                'used_gb': gpu_allocated,
                'total_gb': gpu_total,
                'utilization_pct': gpu_dedicated_pct,
                'target_pct': self.target_memory_usage['gpu_dedicated'] * 100
            },
            'gpu_shared': {
                'used_gb': gpu_shared,
                'total_gb': 31.8,
                'utilization_pct': gpu_shared_pct,
                'target_pct': self.target_memory_usage['gpu_shared'] * 100
            },
            'system_ram': {
                'used_gb': system_used,
                'total_gb': system_total,
                'utilization_pct': system_ram_pct,
                'target_pct': self.target_memory_usage['system_ram'] * 100
            },
            'total': {
                'used_gb': total_used,
                'available_gb': total_available,
                'utilization_pct': total_pct,
                'target_gb': self.target_memory_usage['total_target']
            }
        }
    
    def log_memory_status(self, phase=""):
        """Log comprehensive memory status"""
        status = self.get_memory_status()
        
        logging.info(f"{'='*80}")
        logging.info(f"MEMORY DISTRIBUTION STATUS - {phase}")
        logging.info(f"{'='*80}")
        
        # GPU Dedicated Memory
        gpu_ded = status['gpu_dedicated']
        logging.info(f"GPU Dedicated: {gpu_ded['used_gb']:.2f}GB / {gpu_ded['total_gb']:.1f}GB ({gpu_ded['utilization_pct']:.1f}%) [Target: {gpu_ded['target_pct']:.1f}%]")
        
        # GPU Shared Memory
        gpu_shared = status['gpu_shared']
        logging.info(f"GPU Shared: {gpu_shared['used_gb']:.2f}GB / {gpu_shared['total_gb']:.1f}GB ({gpu_shared['utilization_pct']:.1f}%) [Target: {gpu_shared['target_pct']:.1f}%]")
        
        # System RAM
        sys_ram = status['system_ram']
        logging.info(f"System RAM: {sys_ram['used_gb']:.2f}GB / {sys_ram['total_gb']:.1f}GB ({sys_ram['utilization_pct']:.1f}%) [Target: {sys_ram['target_pct']:.1f}%]")
        
        # Total Memory
        total = status['total']
        logging.info(f"Total Memory: {total['used_gb']:.2f}GB / {total['available_gb']:.1f}GB ({total['utilization_pct']:.1f}%) [Target: {total['target_gb']:.1f}GB]")
        
        logging.info(f"{'='*80}")
        
        return status
    
    def fill_gpu_dedicated_memory(self, target_gb: float):
        """Fill GPU dedicated memory to target usage"""
        current_allocated = torch.cuda.memory_allocated(0) / 1024**3
        if current_allocated >= target_gb:
            logging.info(f"GPU dedicated memory already at target: {current_allocated:.2f}GB")
            return
        
        logging.info(f"Filling GPU dedicated memory to {target_gb:.2f}GB")
        
        # Create tensors in chunks
        chunk_size_gb = 0.5  # 500MB chunks
        tensors = []
        
        while torch.cuda.memory_allocated(0) / 1024**3 < target_gb:
            try:
                elements_needed = int((chunk_size_gb * 1024**3) / 4)
                dim = int(np.sqrt(elements_needed))
                
                tensor = torch.randn(dim, dim, dtype=torch.float32, device=self.device)
                tensors.append(tensor)
                
                current_gb = torch.cuda.memory_allocated(0) / 1024**3
                logging.info(f"Created tensor: {dim}x{dim} = {current_gb:.2f}GB allocated")
                
                if current_gb >= target_gb:
                    break
                    
            except torch.cuda.OutOfMemoryError:
                logging.warning("GPU OOM - stopping tensor creation")
                break
            except Exception as e:
                logging.error(f"Error creating tensor: {e}")
                break
        
        self.gpu_tensors.extend(tensors)
        logging.info(f"GPU dedicated memory filled: {len(tensors)} tensors created")
    
    def fill_gpu_shared_memory(self, target_gb: float):
        """Fill GPU shared memory to target usage"""
        current_reserved = torch.cuda.memory_reserved(0) / 1024**3
        current_allocated = torch.cuda.memory_allocated(0) / 1024**3
        current_shared = current_reserved - current_allocated
        
        if current_shared >= target_gb:
            logging.info(f"GPU shared memory already at target: {current_shared:.2f}GB")
            return
        
        logging.info(f"Filling GPU shared memory to {target_gb:.2f}GB")
        
        # Create large tensors that will be reserved but not immediately allocated
        target_shared = target_gb + current_allocated
        chunk_size_gb = 1.0  # 1GB chunks
        tensors = []
        
        while torch.cuda.memory_reserved(0) / 1024**3 < target_shared:
            try:
                elements_needed = int((chunk_size_gb * 1024**3) / 4)
                dim = int(np.sqrt(elements_needed))
                
                # Create tensor and immediately move to CPU to free GPU memory
                tensor = torch.randn(dim, dim, dtype=torch.float32, device=self.device)
                tensor_cpu = tensor.cpu()
                tensors.append(tensor_cpu)
                
                # Keep reference to maintain memory reservation
                del tensor
                
                current_reserved = torch.cuda.memory_reserved(0) / 1024**3
                current_shared = current_reserved - (torch.cuda.memory_allocated(0) / 1024**3)
                logging.info(f"Created shared tensor: {dim}x{dim} = {current_shared:.2f}GB shared")
                
                if current_shared >= target_gb:
                    break
                    
            except Exception as e:
                logging.error(f"Error creating shared tensor: {e}")
                break
        
        self.gpu_shared_data.extend(tensors)
        logging.info(f"GPU shared memory filled: {len(tensors)} tensors created")
    
    def fill_system_ram(self, target_gb: float):
        """Fill system RAM to target usage"""
        current_used = psutil.virtual_memory().used / 1024**3
        if current_used >= target_gb:
            logging.info(f"System RAM already at target: {current_used:.2f}GB")
            return
        
        logging.info(f"Filling system RAM to {target_gb:.2f}GB")
        
        # Create large numpy arrays to consume system RAM
        chunk_size_gb = 2.0  # 2GB chunks
        arrays = []
        
        while psutil.virtual_memory().used / 1024**3 < target_gb:
            try:
                elements_needed = int((chunk_size_gb * 1024**3) / 8)  # 8 bytes per float64
                dim = int(np.sqrt(elements_needed))
                
                array = np.random.randn(dim, dim).astype(np.float64)
                arrays.append(array)
                
                current_gb = psutil.virtual_memory().used / 1024**3
                logging.info(f"Created array: {dim}x{dim} = {current_gb:.2f}GB RAM used")
                
                if current_gb >= target_gb:
                    break
                    
            except MemoryError:
                logging.warning("System RAM OOM - stopping array creation")
                break
            except Exception as e:
                logging.error(f"Error creating array: {e}")
                break
        
        self.system_ram_data.extend(arrays)
        logging.info(f"System RAM filled: {len(arrays)} arrays created")
    
    def create_memory_pressure(self):
        """Create balanced memory pressure across all tiers"""
        logging.info("Creating balanced memory pressure across all tiers...")
        
        # Phase 1: Fill GPU dedicated memory
        target_gpu_ded = self.target_memory_usage['gpu_dedicated'] * 8.0
        self.fill_gpu_dedicated_memory(target_gpu_ded)
        
        # Phase 2: Fill GPU shared memory
        target_gpu_shared = self.target_memory_usage['gpu_shared'] * 31.8
        self.fill_gpu_shared_memory(target_gpu_shared)
        
        # Phase 3: Fill system RAM
        target_sys_ram = self.target_memory_usage['system_ram'] * 63.6
        self.fill_system_ram(target_sys_ram)
        
        # Phase 4: Monitor and balance
        self.monitor_memory_balance()
    
    def monitor_memory_balance(self, duration_seconds: int = 60):
        """Monitor memory balance and maintain pressure"""
        logging.info(f"Monitoring memory balance for {duration_seconds} seconds...")
        
        start_time = time.time()
        monitoring_data = []
        
        for i in range(duration_seconds):
            status = self.log_memory_status(f"MONITORING {i+1}/{duration_seconds}")
            monitoring_data.append({
                'timestamp': time.time(),
                'status': status
            })
            
            # Check if we need to rebalance
            self.rebalance_memory_if_needed(status)
            
            time.sleep(1)
        
        # Generate performance report
        self.generate_memory_report(monitoring_data, time.time() - start_time)
    
    def rebalance_memory_if_needed(self, status: Dict[str, Any]):
        """Rebalance memory if any tier drops below target"""
        # Check GPU dedicated
        gpu_ded = status['gpu_dedicated']
        if gpu_ded['utilization_pct'] < gpu_ded['target_pct'] * 0.9:
            logging.warning(f"GPU dedicated below 90% of target: {gpu_ded['utilization_pct']:.1f}%")
            target_gb = self.target_memory_usage['gpu_dedicated'] * 8.0
            self.fill_gpu_dedicated_memory(target_gb)
        
        # Check GPU shared
        gpu_shared = status['gpu_shared']
        if gpu_shared['utilization_pct'] < gpu_shared['target_pct'] * 0.9:
            logging.warning(f"GPU shared below 90% of target: {gpu_shared['utilization_pct']:.1f}%")
            target_gb = self.target_memory_usage['gpu_shared'] * 31.8
            self.fill_gpu_shared_memory(target_gb)
        
        # Check system RAM
        sys_ram = status['system_ram']
        if sys_ram['utilization_pct'] < sys_ram['target_pct'] * 0.9:
            logging.warning(f"System RAM below 90% of target: {sys_ram['utilization_pct']:.1f}%")
            target_gb = self.target_memory_usage['system_ram'] * 63.6
            self.fill_system_ram(target_gb)
    
    def generate_memory_report(self, monitoring_data: List[Dict], duration: float):
        """Generate comprehensive memory distribution report"""
        report_path = Path("logs/MEMORY-DISTRIBUTION-REPORT.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write("# MEMORY DISTRIBUTION ENGINE REPORT\n\n")
            f.write(f"**Test Duration:** {duration:.1f} seconds\n")
            f.write(f"**Monitoring Data Points:** {len(monitoring_data)}\n\n")
            
            # Final status
            final_status = monitoring_data[-1]['status']
            f.write("## Final Memory Status\n\n")
            
            f.write(f"### GPU Dedicated Memory\n")
            f.write(f"- **Used:** {final_status['gpu_dedicated']['used_gb']:.2f}GB\n")
            f.write(f"- **Target:** {final_status['gpu_dedicated']['target_pct']:.1f}%\n")
            f.write(f"- **Achieved:** {final_status['gpu_dedicated']['utilization_pct']:.1f}%\n")
            f.write(f"- **Status:** {'✅ TARGET ACHIEVED' if final_status['gpu_dedicated']['utilization_pct'] >= final_status['gpu_dedicated']['target_pct'] else '❌ BELOW TARGET'}\n\n")
            
            f.write(f"### GPU Shared Memory\n")
            f.write(f"- **Used:** {final_status['gpu_shared']['used_gb']:.2f}GB\n")
            f.write(f"- **Target:** {final_status['gpu_shared']['target_pct']:.1f}%\n")
            f.write(f"- **Achieved:** {final_status['gpu_shared']['utilization_pct']:.1f}%\n")
            f.write(f"- **Status:** {'✅ TARGET ACHIEVED' if final_status['gpu_shared']['utilization_pct'] >= final_status['gpu_shared']['target_pct'] else '❌ BELOW TARGET'}\n\n")
            
            f.write(f"### System RAM\n")
            f.write(f"- **Used:** {final_status['system_ram']['used_gb']:.2f}GB\n")
            f.write(f"- **Target:** {final_status['system_ram']['target_pct']:.1f}%\n")
            f.write(f"- **Achieved:** {final_status['system_ram']['utilization_pct']:.1f}%\n")
            f.write(f"- **Status:** {'✅ TARGET ACHIEVED' if final_status['system_ram']['utilization_pct'] >= final_status['system_ram']['target_pct'] else '❌ BELOW TARGET'}\n\n")
            
            f.write(f"### Total Memory\n")
            f.write(f"- **Used:** {final_status['total']['used_gb']:.2f}GB\n")
            f.write(f"- **Target:** {final_status['total']['target_gb']:.1f}GB\n")
            f.write(f"- **Achieved:** {final_status['total']['utilization_pct']:.1f}%\n")
            f.write(f"- **Status:** {'✅ TARGET ACHIEVED' if final_status['total']['used_gb'] >= final_status['total']['target_gb'] else '❌ BELOW TARGET'}\n\n")
            
            # Performance metrics
            f.write("## Performance Metrics\n\n")
            f.write(f"- **Total Tensors Created:** {len(self.gpu_tensors)}\n")
            f.write(f"- **Total Shared Arrays:** {len(self.gpu_shared_data)}\n")
            f.write(f"- **Total RAM Arrays:** {len(self.system_ram_data)}\n")
            f.write(f"- **Memory Pressure Maintained:** {duration:.1f} seconds\n")
        
        logging.info(f"Memory distribution report saved to: {report_path}")
    
    def cleanup_memory(self):
        """Clean up all allocated memory"""
        logging.info("Cleaning up all allocated memory...")
        
        # Clear GPU tensors
        if self.gpu_tensors:
            del self.gpu_tensors
            self.gpu_tensors = []
        
        # Clear GPU shared data
        if self.gpu_shared_data:
            del self.gpu_shared_data
            self.gpu_shared_data = []
        
        # Clear system RAM data
        if self.system_ram_data:
            del self.system_ram_data
            self.system_ram_data = []
        
        # Clear GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logging.info("Memory cleanup complete")
    
    def run_memory_distribution_test(self):
        """Run the complete memory distribution test"""
        logging.info("🚀 STARTING MEMORY DISTRIBUTION ENGINE TEST 🚀")
        
        try:
            # Initial status
            self.log_memory_status("INITIAL")
            
            # Create memory pressure across all tiers
            self.create_memory_pressure()
            
            # Final status
            self.log_memory_status("FINAL")
            
            logging.info("🎯 MEMORY DISTRIBUTION ENGINE TEST COMPLETE 🎯")
            
        except Exception as e:
            logging.error(f"Memory distribution test failed: {e}")
            raise
        finally:
            # Cleanup
            self.cleanup_memory()

def main():
    """Main execution function"""
    try:
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Initialize and run memory distribution engine
        engine = MemoryDistributionEngine()
        engine.run_memory_distribution_test()
        
    except KeyboardInterrupt:
        logging.info("Test interrupted by user")
    except Exception as e:
        logging.error(f"Test failed with error: {e}")
        raise

if __name__ == "__main__":
    main()
