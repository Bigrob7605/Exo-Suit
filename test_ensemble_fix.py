#!/usr/bin/env python3
"""
Simple test to check if ensemble endpoint is working
"""

import requests
import time

def test_ensemble_endpoint():
    """Test the ensemble endpoint directly"""
    print("Testing ensemble endpoint...")
    
    try:
        # Test with a simple prompt
        response = requests.post(
            "http://localhost:5000/api/ensemble",
            json={"prompt": "Hello, this is a test"},
            timeout=15  # 15 second timeout
        )
        
        if response.status_code == 200:
            print("✅ Ensemble endpoint working!")
            print(f"Response: {response.text[:200]}...")
            return True
        else:
            print(f"❌ Ensemble endpoint returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Ensemble endpoint timed out (still hanging)")
        return False
    except Exception as e:
        print(f"❌ Error testing ensemble endpoint: {e}")
        return False

if __name__ == "__main__":
    print("Simple Ensemble Endpoint Test")
    print("=" * 40)
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    success = test_ensemble_endpoint()
    
    if success:
        print("\n🎉 SUCCESS: Ensemble endpoint is working!")
    else:
        print("\n💥 FAILED: Ensemble endpoint still has issues")
