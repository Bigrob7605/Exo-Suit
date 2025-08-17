#!/usr/bin/env python3
"""
Kai Core V8+ Main Engine
Complete AAA system orchestration and management
"""

import asyncio
import logging
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml

# Import core components
from paradox_resolver import ParadoxResolver
from guard_rail_system import GuardRailSystem
from mythgraph_ledger import MythGraphLedger
from plugin_framework import PluginManager

class KaiCoreEngine:
    """
    Main Kai Core V8+ engine that orchestrates all components
    """
    
    def __init__(self, config_path: str = "kai-config.yaml"):
        self.config = self.load_config(config_path)
        self.logger = self.setup_logging()
        
        # Core components
        self.paradox_resolver = None
        self.guard_rail_system = None
        self.mythgraph_ledger = None
        self.plugin_manager = None
        
        # System state
        self.status = "initializing"
        self.start_time = None
        self.request_count = 0
        self.incident_count = 0
        
        # Performance metrics
        self.metrics = {
            "paradox_resolution_rate": 0.0,
            "guard_rail_response_time": 0.0,
            "mythgraph_logging_latency": 0.0,
            "plugin_performance": 0.0,
            "total_requests": 0,
            "blocked_requests": 0,
            "resolved_paradoxes": 0
        }
    
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Use default configuration
            return {
                "kai_core": {
                    "version": "8.0.0",
                    "mode": "production",
                    "mythgraph_enabled": True,
                    "guard_rails_enabled": True,
                    "redteam_enabled": True
                },
                "paradox_resolution": {
                    "timeout_ms": 5000,
                    "max_iterations": 100
                },
                "guard_rails": {
                    "risk_levels": ["none", "low", "moderate", "high", "banned"],
                    "auto_patch": True,
                    "incident_logging": True
                },
                "mythgraph": {
                    "ledger": {
                        "type": "local",
                        "encryption": True,
                        "public_logging": True
                    }
                }
            }
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('kai-core.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('KaiCoreEngine')
    
    async def initialize(self) -> bool:
        """Initialize the complete Kai Core system"""
        self.logger.info("🚀 Initializing Kai Core V8+ Engine...")
        
        try:
            # Initialize MythGraph ledger first
            await self.initialize_mythgraph()
            
            # Initialize paradox resolver
            await self.initialize_paradox_resolver()
            
            # Initialize guard-rail system
            await self.initialize_guard_rail_system()
            
            # Initialize plugin manager
            await self.initialize_plugin_manager()
            
            # Set system status
            self.status = "active"
            self.start_time = datetime.utcnow()
            
            self.logger.info("✅ Kai Core V8+ Engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Kai Core Engine: {e}")
            self.status = "error"
            return False
    
    async def initialize_mythgraph(self):
        """Initialize MythGraph ledger"""
        self.logger.info("📊 Initializing MythGraph ledger...")
        
        public_key = self.config.get("mythgraph", {}).get("public_key", "kai_core_v8_public_key")
        private_key = self.config.get("mythgraph", {}).get("private_key", "kai_core_v8_private_key")
        
        self.mythgraph_ledger = MythGraphLedger(public_key, private_key)
        
        # Log initialization event
        await self.mythgraph_ledger.add_entry("system_event", {
            "event": "engine_initialization",
            "timestamp": datetime.utcnow().isoformat(),
            "version": self.config["kai_core"]["version"]
        })
        
        self.logger.info("✅ MythGraph ledger initialized")
    
    async def initialize_paradox_resolver(self):
        """Initialize paradox resolution system"""
        self.logger.info("🧠 Initializing paradox resolver...")
        
        from paradox_resolver import DefaultParadoxResolver
        self.paradox_resolver = DefaultParadoxResolver()
        
        # Log initialization
        await self.mythgraph_ledger.add_entry("system_event", {
            "event": "paradox_resolver_initialized",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        self.logger.info("✅ Paradox resolver initialized")
    
    async def initialize_guard_rail_system(self):
        """Initialize guard-rail safety system"""
        self.logger.info("🛡️ Initializing guard-rail system...")
        
        self.guard_rail_system = GuardRailSystem()
        
        # Add default policies
        from guard_rail_system import ContentFilterPolicy
        content_policy = ContentFilterPolicy()
        self.guard_rail_system.add_policy(content_policy)
        
        # Log initialization
        await self.mythgraph_ledger.add_entry("system_event", {
            "event": "guard_rail_system_initialized",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        self.logger.info("✅ Guard-rail system initialized")
    
    async def initialize_plugin_manager(self):
        """Initialize plugin management system"""
        self.logger.info("🔌 Initializing plugin manager...")
        
        self.plugin_manager = PluginManager(self.mythgraph_ledger)
        
        # Load default plugins if any
        plugin_directory = Path("plugins")
        if plugin_directory.exists():
            for plugin_dir in plugin_directory.iterdir():
                if plugin_dir.is_dir():
                    await self.plugin_manager.load_plugin(plugin_dir.name)
        
        # Log initialization
        await self.mythgraph_ledger.add_entry("system_event", {
            "event": "plugin_manager_initialized",
            "timestamp": datetime.utcnow().isoformat(),
            "loaded_plugins": len(self.plugin_manager.plugins)
        })
        
        self.logger.info("✅ Plugin manager initialized")
    
    async def process_request(self, request_data: Dict) -> Dict:
        """
        Process a user request through the complete Kai Core pipeline
        
        Args:
            request_data: Dictionary containing request information
                - content: Request text
                - user_id: User identifier
                - context: Additional context
                - timestamp: Request timestamp
        
        Returns:
            Response dictionary with result and metadata
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Step 1: Guard-rail safety check
            safety_result = await self.check_safety(request_data)
            
            if safety_result["risk"] in ["high", "banned"]:
                # Request blocked by guard-rails
                await self.log_incident("guard_rail_block", {
                    "request": request_data,
                    "reason": safety_result["reason"],
                    "risk": safety_result["risk"]
                })
                
                return {
                    "success": False,
                    "blocked": True,
                    "reason": safety_result["reason"],
                    "risk": safety_result["risk"],
                    "processing_time_ms": (time.time() - start_time) * 1000
                }
            
            # Step 2: Paradox resolution (if needed)
            paradox_result = await self.resolve_paradoxes(request_data)
            
            # Step 3: Generate response
            response = await self.generate_response(request_data, paradox_result)
            
            # Step 4: Log to MythGraph
            await self.log_request(request_data, response, safety_result, paradox_result)
            
            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            self.update_metrics(processing_time, safety_result, paradox_result)
            
            return {
                "success": True,
                "response": response,
                "safety_check": safety_result,
                "paradox_resolution": paradox_result,
                "processing_time_ms": processing_time
            }
            
        except Exception as e:
            # Log error
            await self.log_incident("processing_error", {
                "request": request_data,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "success": False,
                "error": str(e),
                "processing_time_ms": (time.time() - start_time) * 1000
            }
    
    async def check_safety(self, request_data: Dict) -> Dict:
        """Check request safety using guard-rail system"""
        return await self.guard_rail_system.check_request(request_data)
    
    async def resolve_paradoxes(self, request_data: Dict) -> Dict:
        """Resolve any paradoxes in the request"""
        content = request_data.get("content", "")
        
        # Check for paradox patterns
        paradox_patterns = [
            "this statement is false",
            "i am lying",
            "the next sentence is true",
            "circular dependency",
            "self reference"
        ]
        
        paradoxes_found = []
        for pattern in paradox_patterns:
            if pattern.lower() in content.lower():
                paradox_data = {
                    "text": content,
                    "pattern": pattern,
                    "context": request_data.get("context", {}),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                resolution = await self.paradox_resolver.resolve_paradox(paradox_data)
                paradoxes_found.append({
                    "pattern": pattern,
                    "resolution": resolution
                })
        
        return {
            "paradoxes_found": len(paradoxes_found),
            "resolutions": paradoxes_found,
            "resolved": all(p["resolution"]["resolved"] for p in paradoxes_found)
        }
    
    async def generate_response(self, request_data: Dict, paradox_result: Dict) -> str:
        """Generate response to user request"""
        content = request_data.get("content", "")
        
        # Simple response generation (in real implementation, this would be more sophisticated)
        if paradox_result["paradoxes_found"] > 0:
            return f"Processed request with {paradox_result['paradoxes_found']} paradoxes resolved."
        else:
            return f"Processed request: {content[:100]}..."
    
    async def log_request(self, request_data: Dict, response: str, safety_result: Dict, paradox_result: Dict):
        """Log request to MythGraph"""
        await self.mythgraph_ledger.add_entry("request_processed", {
            "request": request_data,
            "response": response,
            "safety_check": safety_result,
            "paradox_resolution": paradox_result,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def log_incident(self, incident_type: str, incident_data: Dict):
        """Log incident to MythGraph"""
        self.incident_count += 1
        
        await self.mythgraph_ledger.add_entry("incident", {
            "type": incident_type,
            "data": incident_data,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def update_metrics(self, processing_time: float, safety_result: Dict, paradox_result: Dict):
        """Update system metrics"""
        self.metrics["total_requests"] += 1
        
        if safety_result["risk"] in ["high", "banned"]:
            self.metrics["blocked_requests"] += 1
        
        if paradox_result["resolved"]:
            self.metrics["resolved_paradoxes"] += paradox_result["paradoxes_found"]
        
        # Update rates
        if self.metrics["total_requests"] > 0:
            self.metrics["paradox_resolution_rate"] = (
                self.metrics["resolved_paradoxes"] / self.metrics["total_requests"]
            )
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            "status": self.status,
            "version": self.config["kai_core"]["version"],
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0,
            "request_count": self.request_count,
            "incident_count": self.incident_count,
            "metrics": self.metrics,
            "components": {
                "paradox_resolver": self.paradox_resolver is not None,
                "guard_rail_system": self.guard_rail_system is not None,
                "mythgraph_ledger": self.mythgraph_ledger is not None,
                "plugin_manager": self.plugin_manager is not None
            }
        }
    
    async def shutdown(self):
        """Graceful shutdown of the system"""
        self.logger.info("🛑 Shutting down Kai Core V8+ Engine...")
        
        # Log shutdown event
        if self.mythgraph_ledger:
            await self.mythgraph_ledger.add_entry("system_event", {
                "event": "engine_shutdown",
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0
            })
        
        self.status = "shutdown"
        self.logger.info("✅ Kai Core V8+ Engine shutdown complete")

# Example usage
async def main():
    """Main function for testing the engine"""
    engine = KaiCoreEngine()
    
    # Initialize the system
    if await engine.initialize():
        print("✅ Kai Core V8+ Engine ready")
        
        # Test request processing
        test_request = {
            "content": "What is the weather today?",
            "user_id": "test_user",
            "context": {"session_id": "123"},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        result = await engine.process_request(test_request)
        print(f"Request result: {result}")
        
        # Test paradox resolution
        paradox_request = {
            "content": "This statement is false",
            "user_id": "test_user",
            "context": {"session_id": "123"},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        paradox_result = await engine.process_request(paradox_request)
        print(f"Paradox result: {paradox_result}")
        
        # Get system status
        status = engine.get_system_status()
        print(f"System status: {status}")
        
        # Shutdown
        await engine.shutdown()

if __name__ == "__main__":
    asyncio.run(main()) 