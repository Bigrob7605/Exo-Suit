#!/usr/bin/env python3
"""
Performance Test Script for DeepSpeed ZeRO-Infinity
Tests memory usage, training speed, and system resource utilization
"""

import torch
import deepspeed
import time
import psutil
import GPUtil
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import os
from datetime import datetime

class PerformanceMonitor:
    """Monitor system performance during training"""
    
    def __init__(self):
        self.start_time = None
        self.gpu_usage = []
        self.ram_usage = []
        self.disk_usage = []
        
    def start_monitoring(self):
        """Start monitoring"""
        self.start_time = time.time()
        print("Performance monitoring started...")
        
    def record_metrics(self):
        """Record current system metrics"""
        # GPU metrics
        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            self.gpu_usage.append({
                'timestamp': time.time() - self.start_time,
                'memory_used': gpu.memoryUsed,
                'memory_total': gpu.memoryTotal,
                'utilization': gpu.load * 100,
                'temperature': gpu.temperature
            })
        
        # RAM metrics
        ram = psutil.virtual_memory()
        self.ram_usage.append({
            'timestamp': time.time() - self.start_time,
            'used_gb': ram.used / (1024**3),
            'total_gb': ram.total / (1024**3),
            'percent': ram.percent
        })
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        self.disk_usage.append({
            'timestamp': time.time() - self.start_time,
            'used_gb': disk.used / (1024**3),
            'total_gb': disk.total / (1024**3),
            'percent': disk.percent
        })
    
    def print_current_status(self):
        """Print current system status"""
        gpus = GPUtil.getGPUs()
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"\n{'='*60}")
        print("CURRENT SYSTEM STATUS")
        print(f"{'='*60}")
        
        for i, gpu in enumerate(gpus):
            print(f"GPU {i}: {gpu.name}")
            print(f"  Memory: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB ({gpu.memoryUtil*100:.1f}%)")
            print(f"  Utilization: {gpu.load*100:.1f}%")
            print(f"  Temperature: {gpu.temperature}°C")
        
        print(f"RAM: {ram.used // (1024**3)}GB / {ram.total // (1024**3)}GB ({ram.percent:.1f}%)")
        print(f"Disk: {disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB ({disk.percent:.1f}%)")
        print(f"{'='*60}")
    
    def save_report(self, filename="performance_report.json"):
        """Save performance report to file"""
        report = {
            'test_date': datetime.now().isoformat(),
            'system_info': {
                'gpu_count': len(self.gpu_usage),
                'total_ram_gb': psutil.virtual_memory().total / (1024**3),
                'total_disk_gb': psutil.disk_usage('/').total / (1024**3)
            },
            'gpu_usage': self.gpu_usage,
            'ram_usage': self.ram_usage,
            'disk_usage': self.disk_usage,
            'test_duration': time.time() - self.start_time if self.start_time else 0
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Performance report saved to: {filename}")

def test_model_loading():
    """Test model loading performance"""
    print("\n" + "="*60)
    print("TESTING MODEL LOADING PERFORMANCE")
    print("="*60)
    
    start_time = time.time()
    
    # Load a medium-sized model
    model_name = "microsoft/DialoGPT-medium"
    print(f"Loading model: {model_name}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True
    )
    
    load_time = time.time() - start_time
    print(f"Model loaded in {load_time:.2f} seconds")
    print(f"Model parameters: {model.num_parameters():,}")
    
    return model, tokenizer, load_time

def test_deepspeed_initialization(model, config_path="deepspeed_config.json"):
    """Test DeepSpeed initialization performance"""
    print("\n" + "="*60)
    print("TESTING DEEPSPEED INITIALIZATION")
    print("="*60)
    
    start_time = time.time()
    
    # Initialize DeepSpeed engine
    print("Initializing DeepSpeed engine...")
    
    # Create a dummy input for the model
    dummy_input = torch.randint(0, 1000, (1, 128)).to(model.device)
    
    # Initialize DeepSpeed
    engine, _, _, _ = deepspeed.initialize(
        model=model,
        model_parameters=model.parameters(),
        config=config_path
    )
    
    init_time = time.time() - start_time
    print(f"DeepSpeed initialized in {init_time:.2f} seconds")
    
    return engine, init_time

def test_training_step(engine, tokenizer, num_steps=10):
    """Test training step performance"""
    print(f"\n{'='*60}")
    print(f"TESTING TRAINING STEP PERFORMANCE ({num_steps} steps)")
    print(f"{'='*60}")
    
    # Create dummy training data
    batch_size = 2
    seq_length = 128
    
    dummy_inputs = torch.randint(0, tokenizer.vocab_size, (batch_size, seq_length))
    dummy_labels = dummy_inputs.clone()
    
    # Move to GPU
    device = next(engine.parameters()).device
    dummy_inputs = dummy_inputs.to(device)
    dummy_labels = dummy_labels.to(device)
    
    step_times = []
    
    print("Running training steps...")
    for step in range(num_steps):
        step_start = time.time()
        
        # Forward pass
        outputs = engine(dummy_inputs, labels=dummy_labels)
        loss = outputs.loss
        
        # Backward pass
        engine.backward(loss)
        engine.step()
        
        step_time = time.time() - step_start
        step_times.append(step_time)
        
        print(f"Step {step+1}/{num_steps}: Loss = {loss.item():.4f}, Time = {step_time:.3f}s")
    
    avg_step_time = sum(step_times) / len(step_times)
    print(f"\nAverage step time: {avg_step_time:.3f} seconds")
    print(f"Steps per second: {1/avg_step_time:.2f}")
    
    return step_times, avg_step_time

def main():
    """Main performance test function"""
    print("DeepSpeed ZeRO-Infinity Performance Test")
    print("Optimized for RTX 4070 Laptop")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize performance monitor
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    try:
        # Test 1: Model loading
        model, tokenizer, load_time = test_model_loading()
        monitor.record_metrics()
        
        # Test 2: DeepSpeed initialization
        engine, init_time = test_deepspeed_initialization(model)
        monitor.record_metrics()
        
        # Test 3: Training steps
        step_times, avg_step_time = test_training_step(engine, tokenizer, num_steps=5)
        monitor.record_metrics()
        
        # Final status
        monitor.print_current_status()
        
        # Save performance report
        monitor.save_report()
        
        # Summary
        print(f"\n{'='*60}")
        print("PERFORMANCE TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Model loading time: {load_time:.2f}s")
        print(f"DeepSpeed init time: {init_time:.2f}s")
        print(f"Average training step: {avg_step_time:.3f}s")
        print(f"Training throughput: {1/avg_step_time:.2f} steps/second")
        
        print(f"\nPerformance test completed successfully!")
        print("Check performance_report.json for detailed metrics")
        
    except Exception as e:
        print(f"Performance test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if 'engine' in locals():
            del engine
        if 'model' in locals():
            del model
        torch.cuda.empty_cache()

if __name__ == "__main__":
    main()
