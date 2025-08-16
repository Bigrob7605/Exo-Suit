#!/usr/bin/env python3
"""
ULTIMATE GPU STRESS TEST - Phase 3 Token Upgrade
This script will PUSH your system to its absolute limits and find the perfect 1M token balance.
"""

import os
import sys
import json
import time
import logging
import psutil
import threading
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

# Configure aggressive logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/ULTIMATE-GPU-STRESS-TEST.log'),
        logging.StreamHandler()
    ]
)

# GPU imports
try:
    import torch
    import faiss
    from sentence_transformers import SentenceTransformer
    GPU_AVAILABLE = True
    logging.info("GPU acceleration enabled for ULTIMATE stress test")
except ImportError as e:
    logging.error(f"GPU libraries not available: {e}")
    exit(1)

class UltimateGPUStressTest:
    def __init__(self):
        self.toolbox_path = Path("Universal Open Science Toolbox With Kai (The Real Test)")
        self.max_tokens = 1000000  # 1M tokens
        self.gpu_memory_target = 0.95  # Target 95% GPU memory usage
        self.batch_size = 1000  # Start with 1000 files per batch
        self.current_tokens = 0
        self.gpu_memory_usage = 0
        self.performance_data = []
        
        # Initialize GPU
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.gpu_props = torch.cuda.get_device_properties(0) if torch.cuda.is_available() else None
        
        logging.info(f"Initializing ULTIMATE GPU Stress Test")
        logging.info(f"Target: {self.max_tokens:,} tokens")
        logging.info(f"GPU Memory Target: {self.gpu_memory_target*100:.1f}%")
        logging.info(f"Device: {self.device}")
        
        if self.gpu_props:
            logging.info(f"GPU: {self.gpu_props.name}")
            logging.info(f"GPU Memory: {self.gpu_props.total_memory / 1024**3:.1f} GB")
    
    def get_system_resources(self):
        """Get current system resource usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        if torch.cuda.is_available():
            gpu_allocated = torch.cuda.memory_allocated(0) / 1024**3
            gpu_reserved = torch.cuda.memory_reserved(0) / 1024**3
            gpu_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            gpu_usage = (gpu_allocated / gpu_total) * 100
        else:
            gpu_allocated = gpu_reserved = gpu_total = gpu_usage = 0
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_gb': memory.used / 1024**3,
            'memory_total_gb': memory.total / 1024**3,
            'gpu_allocated_gb': gpu_allocated,
            'gpu_reserved_gb': gpu_reserved,
            'gpu_total_gb': gpu_total,
            'gpu_usage_percent': gpu_usage
        }
    
    def log_system_status(self, phase=""):
        """Log current system status"""
        resources = self.get_system_resources()
        
        logging.info(f"{'='*60}")
        logging.info(f"SYSTEM STATUS - {phase}")
        logging.info(f"{'='*60}")
        logging.info(f"CPU: {resources['cpu_percent']:.1f}%")
        logging.info(f"Memory: {resources['memory_percent']:.1f}% ({resources['memory_used_gb']:.1f}GB / {resources['memory_total_gb']:.1f}GB)")
        logging.info(f"GPU: {resources['gpu_allocated_gb']:.2f}GB allocated, {resources['gpu_reserved_gb']:.2f}GB reserved")
        logging.info(f"GPU Usage: {resources['gpu_usage_percent']:.1f}% of {resources['gpu_total_gb']:.1f}GB")
        logging.info(f"Current Tokens: {self.current_tokens:,}")
        logging.info(f"Token Target: {self.max_tokens:,}")
        logging.info(f"{'='*60}")
        
        return resources
    
    def scan_toolbox_files(self):
        """Scan the entire toolbox for files to process"""
        logging.info("Scanning toolbox for files...")
        
        file_types = ['.py', '.md', '.txt', '.json', '.yaml', '.yml', '.html', '.css', '.js']
        files = []
        
        for file_type in file_types:
            pattern = f"**/*{file_type}"
            found_files = list(self.toolbox_path.rglob(pattern))
            files.extend(found_files)
        
        logging.info(f"Found {len(files)} files to process")
        return files
    
    def estimate_tokens_for_file(self, file_path: Path) -> int:
        """Estimate token count for a file"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Rough estimate: 1 token ≈ 4 characters
                    return len(content) // 4
        except Exception as e:
            logging.warning(f"Could not read {file_path}: {e}")
        
        return 0
    
    def create_memory_intensive_tensors(self, target_gb: float):
        """Create tensors to fill GPU memory to target usage"""
        logging.info(f"Creating memory-intensive tensors to reach {target_gb:.2f}GB GPU usage")
        
        # Calculate how much memory we need to allocate
        current_allocated = torch.cuda.memory_allocated(0) / 1024**3
        target_allocated = target_gb
        memory_to_add_gb = target_allocated - current_allocated
        
        if memory_to_add_gb <= 0:
            logging.info("GPU memory already at target level")
            return
        
        # Create tensors in chunks to avoid OOM
        chunk_size_gb = 0.5  # 500MB chunks
        tensors = []
        
        while torch.cuda.memory_allocated(0) / 1024**3 < target_allocated:
            try:
                # Create a tensor that uses approximately chunk_size_gb
                # Float32: 4 bytes per element
                elements_needed = int((chunk_size_gb * 1024**3) / 4)
                dim = int(np.sqrt(elements_needed))
                
                tensor = torch.randn(dim, dim, dtype=torch.float32, device=self.device)
                tensors.append(tensor)
                
                current_gb = torch.cuda.memory_allocated(0) / 1024**3
                logging.info(f"Created tensor: {dim}x{dim} = {current_gb:.2f}GB allocated")
                
                if current_gb >= target_allocated:
                    break
                    
            except torch.cuda.OutOfMemoryError:
                logging.warning("GPU OOM - stopping tensor creation")
                break
            except Exception as e:
                logging.error(f"Error creating tensor: {e}")
                break
        
        logging.info(f"Created {len(tensors)} tensors")
        return tensors
    
    def process_files_in_batches(self, files: List[Path]):
        """Process files in batches to build up token count"""
        logging.info(f"Processing {len(files)} files in batches of {self.batch_size}")
        
        batches = [files[i:i + self.batch_size] for i in range(0, len(files), self.batch_size)]
        
        for batch_num, batch in enumerate(batches):
            logging.info(f"Processing batch {batch_num + 1}/{len(batches)} ({len(batch)} files)")
            
            batch_tokens = 0
            for file_path in batch:
                tokens = self.estimate_tokens_for_file(file_path)
                batch_tokens += tokens
                self.current_tokens += tokens
                
                # Log progress every 100 files
                if self.current_tokens % 10000 < tokens:
                    self.log_system_status(f"Batch {batch_num + 1}")
            
            # Check if we've reached our token target
            if self.current_tokens >= self.max_tokens:
                logging.info(f"Reached token target: {self.current_tokens:,} tokens")
                break
            
            # Small delay to prevent overwhelming the system
            time.sleep(0.1)
        
        logging.info(f"File processing complete. Total tokens: {self.current_tokens:,}")
    
    def run_stress_test(self):
        """Run the ultimate GPU stress test"""
        logging.info("🚀 STARTING ULTIMATE GPU STRESS TEST 🚀")
        
        # Initial system status
        self.log_system_status("INITIAL")
        
        # Phase 1: Scan toolbox
        files = self.scan_toolbox_files()
        
        # Phase 2: Process files to build token count
        self.process_files_in_batches(files)
        
        # Phase 3: Fill GPU memory to target usage
        target_gb = self.gpu_memory_target * self.gpu_props.total_memory / 1024**3
        tensors = self.create_memory_intensive_tensors(target_gb)
        
        # Phase 4: Monitor performance under stress
        logging.info("Monitoring performance under maximum stress...")
        start_time = time.time()
        
        for i in range(60):  # Monitor for 60 seconds
            resources = self.log_system_status(f"STRESS MONITORING {i+1}/60")
            self.performance_data.append({
                'timestamp': time.time(),
                'resources': resources,
                'current_tokens': self.current_tokens
            })
            
            # Check if we're maintaining target GPU usage
            if resources['gpu_usage_percent'] < (self.gpu_memory_target * 100 * 0.9):
                logging.warning(f"GPU usage dropped below 90% of target: {resources['gpu_usage_percent']:.1f}%")
                # Create more tensors to maintain pressure
                self.create_memory_intensive_tensors(target_gb)
            
            time.sleep(1)
        
        # Phase 5: Cleanup and results
        logging.info("Cleaning up GPU memory...")
        if 'tensors' in locals():
            del tensors
        torch.cuda.empty_cache()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Final system status
        self.log_system_status("FINAL")
        
        # Generate performance report
        self.generate_performance_report(duration)
        
        logging.info("🎯 ULTIMATE GPU STRESS TEST COMPLETE 🎯")
    
    def generate_performance_report(self, duration: float):
        """Generate comprehensive performance report"""
        report_path = Path("logs/ULTIMATE-GPU-STRESS-REPORT.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write("# ULTIMATE GPU STRESS TEST REPORT\n\n")
            f.write(f"**Test Duration:** {duration:.1f} seconds\n")
            f.write(f"**Final Token Count:** {self.current_tokens:,}\n")
            f.write(f"**Target Tokens:** {self.max_tokens:,}\n")
            f.write(f"**Token Achievement:** {(self.current_tokens/self.max_tokens)*100:.1f}%\n\n")
            
            f.write("## Performance Data\n\n")
            for data_point in self.performance_data[-10:]:  # Last 10 data points
                f.write(f"- **{data_point['timestamp']:.1f}s:** ")
                f.write(f"GPU: {data_point['resources']['gpu_usage_percent']:.1f}%, ")
                f.write(f"CPU: {data_point['resources']['cpu_percent']:.1f}%, ")
                f.write(f"Memory: {data_point['resources']['memory_percent']:.1f}%\n")
            
            f.write(f"\n## System Capabilities\n\n")
            f.write(f"- **Maximum Tokens Processed:** {self.current_tokens:,}\n")
            f.write(f"- **GPU Memory Utilization:** {self.gpu_memory_target*100:.1f}%\n")
            f.write(f"- **Processing Duration:** {duration:.1f} seconds\n")
            f.write(f"- **Performance Rating:** {'EXCELLENT' if self.current_tokens >= self.max_tokens else 'GOOD'}\n")
        
        logging.info(f"Performance report saved to: {report_path}")

def main():
    """Main execution function"""
    try:
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Initialize and run stress test
        stress_test = UltimateGPUStressTest()
        stress_test.run_stress_test()
        
    except KeyboardInterrupt:
        logging.info("Test interrupted by user")
    except Exception as e:
        logging.error(f"Test failed with error: {e}")
        raise

if __name__ == "__main__":
    main()
