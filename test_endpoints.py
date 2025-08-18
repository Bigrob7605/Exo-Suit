#!/usr/bin/env python3
"""
Test script for Universal Open Science Toolbox endpoints
"""

import requests
import json

def test_endpoints():
    """Test all available endpoints"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 TESTING UNIVERSAL OPEN SCIENCE TOOLBOX ENDPOINTS")
    print("=" * 60)
    
    # Test 1: Status endpoint
    print("\n🔍 Test 1: Status Endpoint")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status', 'unknown')}")
            print(f"✅ Version: {data.get('version', 'unknown')}")
            print(f"✅ Message: {data.get('message', 'unknown')}")
            print(f"✅ Agents: {len(data.get('agents', []))} available")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
    
    # Test 2: Health endpoint
    print("\n🔍 Test 2: Health Endpoint")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data.get('status', 'unknown')}")
            print(f"✅ Components: {len(data.get('components', {}))} operational")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test 3: Metrics endpoint
    print("\n🔍 Test 3: Metrics Endpoint")
    try:
        response = requests.get(f"{base_url}/api/metrics")
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('metrics', {})
            print(f"✅ Active Agents: {metrics.get('active_agents', 'unknown')}")
            print(f"✅ Available Tools: {metrics.get('available_tools', 'unknown')}")
            print(f"✅ Success Rate: {metrics.get('success_rate', 'unknown')}%")
        else:
            print(f"❌ Metrics endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Metrics endpoint error: {e}")
    
    # Test 4: Ensemble endpoint
    print("\n🔍 Test 4: Ensemble Endpoint")
    try:
        payload = {
            "prompt": "Analyze the current system status and provide a summary",
            "task_type": "general"
        }
        response = requests.post(f"{base_url}/api/ensemble", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ensemble Status: {data.get('status', 'unknown')}")
            print(f"✅ Message: {data.get('message', 'unknown')}")
            print(f"✅ Confidence: {data.get('confidence_score', 'unknown')}")
        else:
            print(f"❌ Ensemble endpoint failed: {response.status_code}")
            print(f"❌ Response: {response.text}")
    except Exception as e:
        print(f"❌ Ensemble endpoint error: {e}")
    
    # Test 5: Agent Chat endpoint
    print("\n🔍 Test 5: Agent Chat Endpoint")
    try:
        payload = {
            "agent_id": "sage",
            "message": "Hello, can you help me with a scientific problem?"
        }
        response = requests.post(f"{base_url}/api/agent_chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent ID: {data.get('agent_id', 'unknown')}")
            print(f"✅ Response: {data.get('response', 'unknown')[:100]}...")
            print(f"✅ Confidence: {data.get('confidence', 'unknown')}")
        else:
            print(f"❌ Agent Chat endpoint failed: {response.status_code}")
            print(f"❌ Response: {response.text}")
    except Exception as e:
        print(f"❌ Agent Chat endpoint error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 ENDPOINT TESTING COMPLETE")

if __name__ == "__main__":
    test_endpoints()
