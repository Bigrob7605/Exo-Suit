#!/usr/bin/env python3
"""
Setup script for DeepSpeed ZeRO-Infinity on RTX 4070 Laptop
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✓ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required packages"""
    print("\n" + "="*60)
    print("INSTALLING DEPENDENCIES")
    print("="*60)
    
    # Upgrade pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install PyTorch with CUDA support
    if not run_command("pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118", "Installing PyTorch with CUDA 11.8"):
        return False
    
    # Install DeepSpeed
    if not run_command("pip install deepspeed", "Installing DeepSpeed"):
        return False
    
    # Install other dependencies
    if not run_command("pip install transformers datasets accelerate", "Installing Hugging Face libraries"):
        return False
    
    if not run_command("pip install psutil GPUtil tensorboard", "Installing utility libraries"):
        return False
    
    return True

def verify_installation():
    """Verify that DeepSpeed is working correctly"""
    print("\n" + "="*60)
    print("VERIFYING INSTALLATION")
    print("="*60)
    
    try:
        import torch
        print(f"✓ PyTorch version: {torch.__version__}")
        print(f"✓ CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"✓ CUDA version: {torch.version.cuda}")
            print(f"✓ GPU count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
    except ImportError as e:
        print(f"✗ PyTorch import failed: {e}")
        return False
    
    try:
        import deepspeed
        print(f"✓ DeepSpeed version: {deepspeed.__version__}")
        
        # Test DeepSpeed initialization
        engine = deepspeed.init_distributed()
        print("✓ DeepSpeed distributed initialization successful")
        
    except ImportError as e:
        print(f"✗ DeepSpeed import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ DeepSpeed test failed: {e}")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    
    directories = ["output", "final_model", "logs", "checkpoints"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def main():
    """Main setup function"""
    print("DeepSpeed ZeRO-Infinity Setup for RTX 4070 Laptop")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        print("\nSetup failed: Python version incompatible")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\nSetup failed: Dependency installation failed")
        return False
    
    # Verify installation
    if not verify_installation():
        print("\nSetup failed: Installation verification failed")
        return False
    
    # Create directories
    create_directories()
    
    print("\n" + "="*60)
    print("SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\nYou can now run the training script:")
    print("python train_model.py")
    print("\nOr test DeepSpeed directly:")
    print("deepspeed --num_gpus=1 train_model.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
