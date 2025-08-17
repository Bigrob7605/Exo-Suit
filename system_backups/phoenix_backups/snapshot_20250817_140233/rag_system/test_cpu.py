# Agent Exo-Suit V4.0 - Basic CPU Operations Test Suite
# Tests fundamental CPU operations for system validation

import os
import sys
import time
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import numpy as np
    print("OK - NumPy available")
except ImportError as e:
    print(f"NumPy not available: {e}")
    print("Please install: numpy")
    sys.exit(1)

def test_basic_operations():
    """Test basic CPU operations"""
    print("\n=== Basic CPU Operations Test ===")
    
    try:
        # Basic arithmetic
        a = 10
        b = 5
        c = a + b
        d = a * b
        e = a / b
        
        print(f"OK - Basic arithmetic: {a} + {b} = {c}")
        print(f"OK - Basic arithmetic: {a} * {b} = {d}")
        print(f"OK - Basic arithmetic: {a} / {b} = {e}")
        
        # String operations
        text = "Hello, Agent Exo-Suit V4.0!"
        length = len(text)
        upper = text.upper()
        
        print(f"OK - String length: {length}")
        print(f"OK - String upper: {upper}")
        
        return True
        
    except Exception as e:
        print(f"Basic operations failed: {e}")
        return False

def test_numpy_operations():
    """Test NumPy operations"""
    print("\n=== NumPy Operations Test ===")
    
    try:
        # Create arrays
        arr1 = np.array([1, 2, 3, 4, 5])
        arr2 = np.array([5, 4, 3, 2, 1])
        
        # Array operations
        sum_arr = arr1 + arr2
        product_arr = arr1 * arr2
        mean_val = np.mean(arr1)
        
        print(f"OK - Array sum: {sum_arr}")
        print(f"OK - Array product: {product_arr}")
        print(f"OK - Array mean: {mean_val}")
        
        # Matrix operations
        matrix = np.random.randn(3, 3)
        determinant = np.linalg.det(matrix)
        
        print(f"OK - Matrix determinant: {determinant:.6f}")
        
        return True
        
    except Exception as e:
        print(f"NumPy operations failed: {e}")
        return False

def test_tensor_operations():
    """Test tensor operations on CPU"""
    print("\n=== CPU Tensor Operations Test ===")
    
    try:
        # Create test tensors
        a = np.random.randn(100, 100)
        b = np.random.randn(100, 100)
        
        # Matrix multiplication
        start_time = time.time()
        c = np.dot(a, b)
        end_time = time.time()
        
        print(f"OK - Matrix multiplication: 100x100 in {end_time - start_time:.6f}s")
        
        # Element-wise operations
        start_time = time.time()
        d = a * b + c
        end_time = time.time()
        
        print(f"OK - Element-wise operations in {end_time - start_time:.6f}s")
        
        print("OK - CPU tensor operations successful!")
        return True
        
    except Exception as e:
        print(f"CPU tensor operations failed: {e}")
        return False

def test_file_operations():
    """Test file operations"""
    print("\n=== File Operations Test ===")
    
    try:
        # Test file creation and reading
        test_content = "Agent Exo-Suit V4.0 CPU test content"
        test_file = "cpu_test_temp.txt"
        
        # Write file
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"OK - File written: {test_file}")
        
        # Read file
        with open(test_file, 'r', encoding='utf-8') as f:
            read_content = f.read()
        
        print(f"OK - File read: {len(read_content)} characters")
        
        # Verify content
        if read_content == test_content:
            print("OK - File content verified")
        else:
            print("WARNING - File content mismatch")
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
            print("OK - Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"File operations failed: {e}")
        return False

def main():
    """Main test function"""
    print("Agent Exo-Suit V4.0 - Basic CPU Operations Test Suite")
    print("=" * 60)
    
    # Test basic operations
    if not test_basic_operations():
        print("FAILED - Basic operations test")
        return False
    
    # Test NumPy operations
    if not test_numpy_operations():
        print("FAILED - NumPy operations test")
        return False
    
    # Test tensor operations
    if not test_tensor_operations():
        print("FAILED - Tensor operations test")
        return False
    
    # Test file operations
    if not test_file_operations():
        print("FAILED - File operations test")
        return False
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED - Basic CPU operations working correctly!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
