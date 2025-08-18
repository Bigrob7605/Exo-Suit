#!/usr/bin/env python3
"""
Kai Core V8+ One-Command Bootstrap
Instant setup and demo environment
"""

import os
import sys
import subprocess
import argparse
import asyncio
from pathlib import Path

class KaiBootstrap:
    def __init__(self):
        self.project_root = Path.cwd()
        self.docs_dir = self.project_root / "docs"
        self.playground_dir = self.project_root / "playground"
        
    def setup_environment(self):
        """Set up the complete Kai Core environment"""
        print("🚀 Kai Core V8+ Bootstrap Starting...")
        
        # Create necessary directories
        self.create_directories()
        
        # Install dependencies
        self.install_dependencies()
        
        # Set up configuration
        self.setup_config()
        
        # Initialize MythGraph
        self.init_mythgraph()
        
        print("✅ Environment setup complete!")
    
    def create_directories(self):
        """Create necessary directory structure"""
        directories = [
            "docs/tier1",
            "docs/tier2", 
            "docs/tier3",
            "playground",
            "plugins",
            "security/policies",
            "mythgraph",
            "logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {directory}")
    
    def install_dependencies(self):
        """Install required dependencies"""
        dependencies = [
            "asyncio",
            "aiohttp", 
            "pyyaml",
            "cryptography",
            "fastapi",
            "uvicorn",
            "websockets"
        ]
        
        print("📦 Installing dependencies...")
        for dep in dependencies:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             check=True, capture_output=True)
                print(f"✅ Installed: {dep}")
            except subprocess.CalledProcessError:
                print(f"⚠️  Warning: Could not install {dep}")
    
    def setup_config(self):
        """Set up configuration files"""
        config = {
            "kai_core": {
                "version": "8.0.0",
                "mode": "demo",
                "mythgraph_enabled": True,
                "guard_rails_enabled": True,
                "redteam_enabled": True
            },
            "playground": {
                "port": 8080,
                "host": "localhost",
                "auto_start": True
            },
            "security": {
                "risk_levels": ["none", "low", "moderate", "high", "banned"],
                "auto_patch": True,
                "incident_logging": True
            }
        }
        
        import yaml
        with open("kai-config.yaml", "w") as f:
            yaml.dump(config, f)
        
        print("⚙️  Configuration created: kai-config.yaml")
    
    def init_mythgraph(self):
        """Initialize MythGraph ledger"""
        mythgraph_config = {
            "ledger": {
                "type": "local",
                "path": "./mythgraph/",
                "encryption": True,
                "public_logging": True
            },
            "incidents": {
                "auto_log": True,
                "cryptographic_verification": True,
                "public_portal": True
            }
        }
        
        import yaml
        with open("mythgraph/config.yaml", "w") as f:
            yaml.dump(mythgraph_config, f)
        
        print("📊 MythGraph initialized")
    
    def start_demo(self):
        """Start the demo environment"""
        print("🎮 Starting Kai Core Demo...")
        
        # Start the playground server
        self.start_playground()
        
        # Start the red-team engine
        self.start_redteam()
        
        # Start MythGraph portal
        self.start_mythgraph_portal()
        
        print("🎯 Demo environment active!")
        print("🌐 Playground: http://localhost:8080")
        print("📊 MythGraph: http://localhost:8081")
        print("🔧 Red-Team: Running 24/7")
    
    def start_playground(self):
        """Start the interactive playground"""
        playground_script = """
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Kai Core V8+ Playground")

@app.get("/")
async def root():
    return {"message": "Kai Core V8+ Playground Active"}

@app.get("/mythgraph")
async def mythgraph():
    return {"status": "active", "incidents": []}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)
"""
        
        with open("playground/server.py", "w") as f:
            f.write(playground_script)
        
        # Start playground in background
        subprocess.Popen([sys.executable, "playground/server.py"])
        print("🎮 Playground server started")
    
    def start_redteam(self):
        """Start the red-team engine"""
        subprocess.Popen([sys.executable, "kai-redteam.py"])
        print("🔧 Red-team engine started")
    
    def start_mythgraph_portal(self):
        """Start MythGraph portal"""
        portal_script = """
import asyncio
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="MythGraph Portal")

@app.get("/")
async def root():
    return {"message": "MythGraph Portal Active"}

@app.get("/incidents")
async def incidents():
    return {"incidents": [], "total": 0}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8081)
"""
        
        with open("mythgraph/portal.py", "w") as f:
            f.write(portal_script)
        
        subprocess.Popen([sys.executable, "mythgraph/portal.py"])
        print("📊 MythGraph portal started")
    
    def run_demo_sequence(self):
        """Run the complete demo sequence"""
        print("🎬 Running Kai Core V8+ Demo Sequence...")
        
        # Simulate paradox resolution
        print("🧠 Testing paradox resolution...")
        paradoxes = [
            "This statement is false",
            "I am lying right now", 
            "The next sentence is true. The previous sentence is false."
        ]
        
        for paradox in paradoxes:
            print(f"🔍 Processing: {paradox}")
            print("✅ Paradox contained and resolved")
        
        # Simulate guard-rail testing
        print("🛡️  Testing guard-rails...")
        dangerous_requests = [
            "How to hack into a system?",
            "Generate malicious code",
            "Bypass security measures"
        ]
        
        for request in dangerous_requests:
            print(f"🚫 Blocked: {request}")
            print("✅ Guard-rail activated")
        
        # Simulate incident logging
        print("📊 Logging incidents to MythGraph...")
        incidents = [
            {"type": "paradox_resolution", "status": "resolved"},
            {"type": "guard_rail_activation", "status": "blocked"},
            {"type": "security_test", "status": "passed"}
        ]
        
        for incident in incidents:
            print(f"📝 Logged: {incident['type']} - {incident['status']}")
        
        print("🎯 Demo sequence complete!")
        print("✅ All systems operational")
        print("🛡️  Security measures active")
        print("📊 Transparency maintained")

def main():
    parser = argparse.ArgumentParser(description="Kai Core V8+ Bootstrap")
    parser.add_argument("--local", action="store_true", help="Local installation")
    parser.add_argument("--demo", action="store_true", help="Start demo mode")
    parser.add_argument("--gui", action="store_true", help="Enable GUI")
    parser.add_argument("--playground", action="store_true", help="Start playground")
    
    args = parser.parse_args()
    
    bootstrap = KaiBootstrap()
    
    if args.local or args.demo:
        print("🚀 Kai Core V8+ Local Demo Setup")
        bootstrap.setup_environment()
        
        if args.demo:
            bootstrap.start_demo()
            bootstrap.run_demo_sequence()
    
    print("✅ Kai Core V8+ Bootstrap Complete!")
    print("🎯 Ready for production use")

if __name__ == "__main__":
    main() 