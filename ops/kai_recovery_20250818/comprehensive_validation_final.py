#!/usr/bin/env python3
"""
Comprehensive System Validation Test
Tests all V1 and V2 endpoints, agents, and features
"""

import requests
import json
import time

def test_v1_endpoints():
    """Test all V1 endpoints."""
    base_url = "http://localhost:5000"
    
    v1_tests = [
        ("/api/status", "GET", "V1 Status"),
        ("/api/metrics", "GET", "V1 Metrics"),
        ("/api/ensemble", "POST", "V1 Ensemble", {"prompt": "Test ensemble"}),
        ("/api/agent_chat", "POST", "V1 Agent Chat", {"agent_id": "human_reviewer", "message": "Hello"}),
        ("/api/visualize_data", "POST", "V1 Visualization", {"type": "quantum"})
    ]
    
    results = []
    
    for endpoint, method, description, *data in v1_tests:
        print(f"Testing V1: {description}")
        
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}")
            else:
                response = requests.post(f"{base_url}{endpoint}", json=data[0] if data else {})
            
            if response.status_code == 200:
                results.append({"test": description, "status": "PASS"})
                print(f"✅ {description}: PASS")
            else:
                results.append({"test": description, "status": "FAIL", "error": response.text})
                print(f"❌ {description}: FAIL")
                
        except Exception as e:
            results.append({"test": description, "status": "FAIL", "error": str(e)})
            print(f"❌ {description}: FAIL - {e}")
    
    return results

def test_v2_endpoints():
    """Test all V2 endpoints."""
    base_url = "http://localhost:5000"
    v2_headers = {"X-V2-Features": "enabled"}
    
    v2_tests = [
        ("/api/status", "GET", "V2 Status"),
        ("/api/events", "GET", "V2 Events"),
        ("/api/memory/prune", "POST", "V2 Memory Prune", {}),
        ("/api/health", "GET", "V2 Health"),
        ("/api/visualize_data", "POST", "V2 Headless Visualization", {"type": "quantum"})
    ]
    
    results = []
    
    for endpoint, method, description, *data in v2_tests:
        print(f"Testing V2: {description}")
        
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", headers=v2_headers)
            else:
                response = requests.post(f"{base_url}{endpoint}", 
                                      json=data[0] if data else {}, headers=v2_headers)
            
            if response.status_code == 200:
                v2_active = response.headers.get("X-V2-Active", "false")
                if v2_active == "true":
                    results.append({"test": description, "status": "PASS"})
                    print(f"✅ {description}: PASS (V2 Active)")
                else:
                    results.append({"test": description, "status": "FAIL", "error": "V2 not active"})
                    print(f"❌ {description}: FAIL (V2 not active)")
            else:
                results.append({"test": description, "status": "FAIL", "error": response.text})
                print(f"❌ {description}: FAIL")
                
        except Exception as e:
            results.append({"test": description, "status": "FAIL", "error": str(e)})
            print(f"❌ {description}: FAIL - {e}")
    
    return results

def test_never_repeat_personality():
    """Test never-repeat personality system."""
    base_url = "http://localhost:5000"
    agent_id = "human_reviewer"
    
    responses = []
    
    for i in range(5):
        response = requests.post(f"{base_url}/api/agent_chat", 
                               json={"agent_id": agent_id, "message": "Hello"})
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("agent_response", {}).get("response", "")
            responses.append(response_text)
            print(f"Response {i+1}: {response_text[:50]}...")
        else:
            print(f"❌ Agent chat failed: {response.text}")
            return False
    
    unique_responses = len(set(responses))
    total_responses = len(responses)
    
    print(f"Unique responses: {unique_responses}/{total_responses}")
    
    if unique_responses == total_responses:
        print("🎉 BULLETPROOF NEVER-REPEAT SYSTEM: ACHIEVED")
        return True
    else:
        print("❌ NEVER-REPEAT SYSTEM: NEEDS FIXING")
        return False

if __name__ == "__main__":
    print("=== COMPREHENSIVE SYSTEM VALIDATION ===")
    
    # Test V1 endpoints
    print("\n--- V1 ENDPOINTS ---")
    v1_results = test_v1_endpoints()
    
    # Test V2 endpoints
    print("\n--- V2 ENDPOINTS ---")
    v2_results = test_v2_endpoints()
    
    # Test never-repeat personality
    print("\n--- NEVER-REPEAT PERSONALITY ---")
    personality_result = test_never_repeat_personality()
    
    # Summary
    v1_passed = sum(1 for r in v1_results if r["status"] == "PASS")
    v2_passed = sum(1 for r in v2_results if r["status"] == "PASS")
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"V1 Endpoints: {v1_passed}/{len(v1_results)} PASSED")
    print(f"V2 Endpoints: {v2_passed}/{len(v2_results)} PASSED")
    print(f"Never-Repeat: {'PASS' if personality_result else 'FAIL'}")
    
    if v1_passed == len(v1_results) and v2_passed == len(v2_results) and personality_result:
        print("🎉 COMPREHENSIVE VALIDATION: ALL SYSTEMS BULLETPROOF")
    else:
        print("❌ COMPREHENSIVE VALIDATION: SOME SYSTEMS FAILED")
