#!/usr/bin/env python3
"""
DeepSpeed ZeRO-Infinity Training Script with GDS Optimization
Optimized for RTX 4070 Laptop with 8GB VRAM + 64GB RAM + 4TB NVMe
"""

import os
import torch
import deepspeed
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import load_dataset
import psutil
import GPUtil
from datetime import datetime
import json
from gds_optimizer import GDSOptimizer

def print_system_info():
    """Display current system resource usage"""
    print("=" * 60)
    print("SYSTEM RESOURCE STATUS")
    print("=" * 60)
    
    # GPU Info
    gpus = GPUtil.getGPUs()
    for i, gpu in enumerate(gpus):
        print(f"GPU {i}: {gpu.name}")
        print(f"  Memory: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB ({gpu.memoryUtil*100:.1f}%)")
        print(f"  Temperature: {gpu.temperature}°C")
        print(f"  Load: {gpu.load*100:.1f}%")
    
    # RAM Info
    ram = psutil.virtual_memory()
    print(f"RAM: {ram.used // (1024**3)}GB / {ram.total // (1024**3)}GB ({ram.percent:.1f}%)")
    
    # Disk Info
    disk = psutil.disk_usage('/')
    print(f"Disk: {disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB ({disk.percent:.1f}%)")
    print("=" * 60)

def create_model_and_tokenizer(model_name="microsoft/DialoGPT-medium", use_gds=True):
    """Create model and tokenizer with GDS optimization for RTX 4070"""
    print(f"Loading model: {model_name}")
    
    # Initialize GDS optimizer if enabled
    gds_optimizer = None
    if use_gds:
        try:
            gds_optimizer = GDSOptimizer(staging_buffer_gb=8, num_streams=4)
            print("GDS optimizer initialized successfully")
        except Exception as e:
            print(f"GDS optimizer failed to initialize: {e}")
            print("Falling back to standard loading")
            gds_optimizer = None
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model with optimal settings for 8GB VRAM
    if gds_optimizer and gds_optimizer.gds_supported:
        print("Using GDS-optimized model loading...")
        # Use GDS for model loading
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,  # Use FP16 to save memory
            low_cpu_mem_usage=True,
            device_map="auto"
        )
        
        # Optimize model transfer to GPU
        for param in model.parameters():
            if param.device.type == 'cpu':
                param.data = gds_optimizer.optimize_transfer(param.data)
    else:
        print("Using standard model loading...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,  # Use FP16 to save memory
            low_cpu_mem_usage=True,
            device_map="auto"
        )
    
    print(f"Model loaded with {model.num_parameters():,} parameters")
    
    # Clean up GDS optimizer
    if gds_optimizer:
        gds_optimizer.cleanup()
    
    return model, tokenizer

def prepare_dataset(tokenizer, max_length=512):
    """Prepare a sample dataset for training"""
    print("Preparing dataset...")
    
    # Load a small dataset for demonstration
    dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
    
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=max_length,
            return_tensors="pt"
        )
    
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names
    )
    
    print(f"Dataset prepared: {len(tokenized_dataset)} samples")
    return tokenized_dataset

def train_with_deepspeed(model, tokenizer, dataset, config_path="deepspeed_config.json"):
    """Train the model using DeepSpeed ZeRO-Infinity with GDS optimization"""
    print("Starting DeepSpeed ZeRO-Infinity training with GDS optimization...")
    
    # Training arguments optimized for your system
    training_args = TrainingArguments(
        output_dir="./output",
        per_device_train_batch_size=2,  # Small batch size for 8GB VRAM
        gradient_accumulation_steps=4,  # Effective batch size = 2 * 4 = 8
        learning_rate=5e-5,
        num_train_epochs=1,
        logging_steps=10,
        save_steps=500,
        save_total_limit=2,
        prediction_loss_only=True,
        remove_unused_columns=False,
        dataloader_pin_memory=True,
        dataloader_num_workers=2,  # Optimal for your CPU
        deepspeed=config_path,
        fp16=True,
        report_to="tensorboard"
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=data_collator,
        tokenizer=tokenizer
    )
    
    # Train the model
    print("Training started...")
    trainer.train()
    
    # Save the final model
    trainer.save_model("./final_model")
    print("Training completed! Model saved to ./final_model")

def benchmark_gds_performance():
    """Benchmark GDS performance before training"""
    print("\n" + "="*60)
    print("GDS PERFORMANCE BENCHMARK")
    print("="*60)
    
    try:
        gds_optimizer = GDSOptimizer(staging_buffer_gb=8, num_streams=4)
        
        # Benchmark PCIe bandwidth
        bandwidth = gds_optimizer.benchmark_pcie_bandwidth(test_size_gb=1.0)
        
        # Test double buffering
        buffer1, buffer2 = gds_optimizer.create_double_buffer()
        print("Double buffering test passed")
        
        # Cleanup
        gds_optimizer.cleanup()
        
        print(f"\nGDS Benchmark Results:")
        print(f"  PCIe Bandwidth: {bandwidth:.1f} GB/s")
        print(f"  Target Bandwidth: 16.0 GB/s")
        print(f"  Efficiency: {(bandwidth/16.0)*100:.1f}%")
        
        return bandwidth
        
    except Exception as e:
        print(f"GDS benchmark failed: {e}")
        return 0.0

def main():
    """Main training function with GDS optimization"""
    print("DeepSpeed ZeRO-Infinity Training Setup with GDS Optimization")
    print("Optimized for RTX 4070 Laptop (8GB VRAM + 64GB RAM + 4TB NVMe)")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if DeepSpeed is available
    try:
        import deepspeed
        print(f"DeepSpeed version: {deepspeed.__version__}")
    except ImportError:
        print("ERROR: DeepSpeed not installed. Run: pip install deepspeed")
        return
    
    # Display initial system status
    print_system_info()
    
    # Benchmark GDS performance
    gds_bandwidth = benchmark_gds_performance()
    
    # Create model and tokenizer with GDS optimization
    use_gds = gds_bandwidth > 8.0  # Use GDS if bandwidth > 8 GB/s
    model, tokenizer = create_model_and_tokenizer(use_gds=use_gds)
    
    # Prepare dataset
    dataset = prepare_dataset(tokenizer)
    
    # Train with DeepSpeed
    train_with_deepspeed(model, tokenizer, dataset)
    
    # Final system status
    print("\nFinal system status:")
    print_system_info()
    
    print("\nTraining completed successfully!")
    print("Check the ./output directory for logs and checkpoints")
    print("Check the ./final_model directory for the trained model")
    
    if gds_bandwidth > 0:
        print(f"\nGDS Performance Summary:")
        print(f"  Measured bandwidth: {gds_bandwidth:.1f} GB/s")
        print(f"  GDS optimization: {'Enabled' if use_gds else 'Disabled'}")

if __name__ == "__main__":
    main()
