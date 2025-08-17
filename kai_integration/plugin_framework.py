#!/usr/bin/env python3
"""
Kai Core V8+ Plugin Framework
Extensibility system for custom modules
"""

import asyncio
import json
import yaml
from typing import Dict, List, Optional, Any
from enum import Enum
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime

class PluginType(Enum):
    PARADOX_MODULE = "paradox_module"
    SEED_GENERATOR = "seed_generator"
    GUARD_RAIL_EXTENSION = "guard_rail_extension"
    SIM_KERNEL = "sim_kernel"

class PluginStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    LOADING = "loading"

class BasePlugin(ABC):
    """
    Abstract base class for all Kai Core plugins
    """
    
    def __init__(self, name: str, version: str, plugin_type: PluginType):
        self.name = name
        self.version = version
        self.plugin_type = plugin_type
        self.status = PluginStatus.INACTIVE
        self.config = {}
        self.mythgraph = None  # MythGraph integration
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize plugin"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """Shutdown plugin"""
        pass
    
    @abstractmethod
    async def execute(self, data: Dict) -> Dict:
        """Execute plugin functionality"""
        pass
    
    def load_config(self, config_path: str) -> bool:
        """Load plugin configuration"""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            return True
        except Exception as e:
            print(f"Failed to load config for {self.name}: {e}")
            return False
    
    async def log_to_mythgraph(self, event_data: Dict):
        """Log event to MythGraph"""
        if self.mythgraph:
            await self.mythgraph.add_entry("plugin_event", {
                "plugin": self.name,
                "event": event_data,
                "timestamp": datetime.utcnow().isoformat()
            })

class ParadoxModulePlugin(BasePlugin):
    """
    Plugin for custom paradox resolution modules
    """
    
    def __init__(self, name: str, version: str):
        super().__init__(name, version, PluginType.PARADOX_MODULE)
        self.paradox_patterns = []
        self.resolution_methods = []
    
    async def initialize(self) -> bool:
        """Initialize paradox module"""
        try:
            # Load paradox patterns from config
            self.paradox_patterns = self.config.get("paradox_patterns", [])
            self.resolution_methods = self.config.get("resolution_methods", [])
            
            self.status = PluginStatus.ACTIVE
            await self.log_to_mythgraph({"action": "initialized"})
            return True
        except Exception as e:
            self.status = PluginStatus.ERROR
            await self.log_to_mythgraph({"action": "initialization_failed", "error": str(e)})
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown paradox module"""
        try:
            self.status = PluginStatus.INACTIVE
            await self.log_to_mythgraph({"action": "shutdown"})
            return True
        except Exception as e:
            await self.log_to_mythgraph({"action": "shutdown_failed", "error": str(e)})
            return False
    
    async def execute(self, data: Dict) -> Dict:
        """Execute paradox resolution"""
        paradox_text = data.get("paradox_text", "")
        
        # Check if this plugin can handle the paradox
        if not self.can_handle_paradox(paradox_text):
            return {"handled": False, "reason": "Paradox not supported"}
        
        # Apply custom resolution logic
        result = await self.resolve_paradox(paradox_text, data)
        
        await self.log_to_mythgraph({
            "action": "paradox_resolved",
            "paradox": paradox_text,
            "result": result
        })
        
        return result
    
    def can_handle_paradox(self, paradox_text: str) -> bool:
        """Check if plugin can handle this paradox"""
        for pattern in self.paradox_patterns:
            if pattern.lower() in paradox_text.lower():
                return True
        return False
    
    async def resolve_paradox(self, paradox_text: str, context: Dict) -> Dict:
        """Custom paradox resolution logic"""
        # This would be implemented by the plugin developer
        return {
            "handled": True,
            "method": "custom_resolution",
            "confidence": 0.85,
            "resolution": "Paradox contained using custom method"
        }

class SeedGeneratorPlugin(BasePlugin):
    """
    Plugin for custom seed generation
    """
    
    def __init__(self, name: str, version: str):
        super().__init__(name, version, PluginType.SEED_GENERATOR)
        self.seed_templates = []
        self.generation_rules = []
    
    async def initialize(self) -> bool:
        """Initialize seed generator"""
        try:
            self.seed_templates = self.config.get("seed_templates", [])
            self.generation_rules = self.config.get("generation_rules", [])
            
            self.status = PluginStatus.ACTIVE
            await self.log_to_mythgraph({"action": "initialized"})
            return True
        except Exception as e:
            self.status = PluginStatus.ERROR
            await self.log_to_mythgraph({"action": "initialization_failed", "error": str(e)})
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown seed generator"""
        try:
            self.status = PluginStatus.INACTIVE
            await self.log_to_mythgraph({"action": "shutdown"})
            return True
        except Exception as e:
            await self.log_to_mythgraph({"action": "shutdown_failed", "error": str(e)})
            return False
    
    async def execute(self, data: Dict) -> Dict:
        """Generate custom seed"""
        seed_type = data.get("seed_type", "default")
        parameters = data.get("parameters", {})
        
        # Generate seed based on type and parameters
        seed = await self.generate_seed(seed_type, parameters)
        
        await self.log_to_mythgraph({
            "action": "seed_generated",
            "seed_type": seed_type,
            "seed": seed
        })
        
        return {
            "generated": True,
            "seed": seed,
            "type": seed_type
        }
    
    async def generate_seed(self, seed_type: str, parameters: Dict) -> str:
        """Generate seed based on type and parameters"""
        # This would be implemented by the plugin developer
        return f"Custom seed for {seed_type} with parameters {parameters}"

class GuardRailExtensionPlugin(BasePlugin):
    """
    Plugin for custom guard-rail extensions
    """
    
    def __init__(self, name: str, version: str):
        super().__init__(name, version, PluginType.GUARD_RAIL_EXTENSION)
        self.safety_rules = []
        self.risk_patterns = []
    
    async def initialize(self) -> bool:
        """Initialize guard-rail extension"""
        try:
            self.safety_rules = self.config.get("safety_rules", [])
            self.risk_patterns = self.config.get("risk_patterns", [])
            
            self.status = PluginStatus.ACTIVE
            await self.log_to_mythgraph({"action": "initialized"})
            return True
        except Exception as e:
            self.status = PluginStatus.ERROR
            await self.log_to_mythgraph({"action": "initialization_failed", "error": str(e)})
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown guard-rail extension"""
        try:
            self.status = PluginStatus.INACTIVE
            await self.log_to_mythgraph({"action": "shutdown"})
            return True
        except Exception as e:
            await self.log_to_mythgraph({"action": "shutdown_failed", "error": str(e)})
            return False
    
    async def execute(self, data: Dict) -> Dict:
        """Execute custom safety check"""
        request_content = data.get("content", "")
        
        # Apply custom safety rules
        safety_result = await self.check_safety(request_content)
        
        await self.log_to_mythgraph({
            "action": "safety_check",
            "content": request_content,
            "result": safety_result
        })
        
        return safety_result
    
    async def check_safety(self, content: str) -> Dict:
        """Check content safety using custom rules"""
        # This would be implemented by the plugin developer
        return {
            "safe": True,
            "risk_level": "none",
            "reason": "Custom safety check passed"
        }

class PluginManager:
    """
    Plugin management system
    """
    
    def __init__(self, mythgraph):
        self.plugins: Dict[str, BasePlugin] = {}
        self.mythgraph = mythgraph
        self.plugin_directory = Path("plugins")
        self.plugin_directory.mkdir(exist_ok=True)
    
    async def load_plugin(self, plugin_name: str) -> bool:
        """Load plugin by name"""
        try:
            plugin_path = self.plugin_directory / plugin_name
            
            if not plugin_path.exists():
                print(f"Plugin directory not found: {plugin_path}")
                return False
            
            # Load plugin configuration
            config_path = plugin_path / "config.yaml"
            if not config_path.exists():
                print(f"Plugin config not found: {config_path}")
                return False
            
            # Determine plugin type from config
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            plugin_type_str = config.get("plugin_type", "paradox_module")
            plugin_type = PluginType(plugin_type_str)
            
            # Create plugin instance based on type
            if plugin_type == PluginType.PARADOX_MODULE:
                plugin = ParadoxModulePlugin(plugin_name, config.get("version", "1.0.0"))
            elif plugin_type == PluginType.SEED_GENERATOR:
                plugin = SeedGeneratorPlugin(plugin_name, config.get("version", "1.0.0"))
            elif plugin_type == PluginType.GUARD_RAIL_EXTENSION:
                plugin = GuardRailExtensionPlugin(plugin_name, config.get("version", "1.0.0"))
            else:
                print(f"Unsupported plugin type: {plugin_type}")
                return False
            
            # Set MythGraph integration
            plugin.mythgraph = self.mythgraph
            
            # Load configuration
            if not plugin.load_config(str(config_path)):
                return False
            
            # Initialize plugin
            if await plugin.initialize():
                self.plugins[plugin_name] = plugin
                print(f"✅ Loaded plugin: {plugin_name}")
                return True
            else:
                print(f"❌ Failed to initialize plugin: {plugin_name}")
                return False
                
        except Exception as e:
            print(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload plugin by name"""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            if await plugin.shutdown():
                del self.plugins[plugin_name]
                print(f"✅ Unloaded plugin: {plugin_name}")
                return True
            else:
                print(f"❌ Failed to unload plugin: {plugin_name}")
                return False
        else:
            print(f"Plugin not found: {plugin_name}")
            return False
    
    async def execute_plugin(self, plugin_name: str, data: Dict) -> Dict:
        """Execute plugin with data"""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            return await plugin.execute(data)
        else:
            return {"error": f"Plugin {plugin_name} not found"}
    
    def list_plugins(self) -> List[Dict]:
        """List all loaded plugins"""
        return [
            {
                "name": name,
                "type": plugin.plugin_type.value,
                "version": plugin.version,
                "status": plugin.status.value
            }
            for name, plugin in self.plugins.items()
        ]
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict]:
        """Get detailed plugin information"""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            return {
                "name": plugin.name,
                "type": plugin.plugin_type.value,
                "version": plugin.version,
                "status": plugin.status.value,
                "config": plugin.config
            }
        return None
    
    async def reload_plugin(self, plugin_name: str) -> bool:
        """Reload plugin"""
        # Unload first
        if await self.unload_plugin(plugin_name):
            # Load again
            return await self.load_plugin(plugin_name)
        return False
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[str]:
        """Get plugin names by type"""
        return [
            name for name, plugin in self.plugins.items()
            if plugin.plugin_type == plugin_type
        ]

# Example usage
async def test_plugin_framework():
    """Test the plugin framework"""
    # Create a mock MythGraph for testing
    class MockMythGraph:
        async def add_entry(self, entry_type: str, data: Dict):
            print(f"MYTHGRAPH: {entry_type} - {data}")
    
    mythgraph = MockMythGraph()
    plugin_manager = PluginManager(mythgraph)
    
    # Create a sample plugin configuration
    sample_plugin_dir = Path("plugins/sample_paradox_plugin")
    sample_plugin_dir.mkdir(parents=True, exist_ok=True)
    
    sample_config = {
        "plugin_type": "paradox_module",
        "version": "1.0.0",
        "paradox_patterns": [
            "custom paradox pattern",
            "another pattern"
        ],
        "resolution_methods": [
            "custom_resolution",
            "advanced_containment"
        ]
    }
    
    with open(sample_plugin_dir / "config.yaml", 'w') as f:
        yaml.dump(sample_config, f)
    
    # Load the plugin
    success = await plugin_manager.load_plugin("sample_paradox_plugin")
    print(f"Plugin load success: {success}")
    
    # List plugins
    plugins = plugin_manager.list_plugins()
    print(f"Loaded plugins: {plugins}")
    
    # Execute plugin
    test_data = {
        "paradox_text": "This is a custom paradox pattern",
        "context": {"depth": 1}
    }
    
    result = await plugin_manager.execute_plugin("sample_paradox_plugin", test_data)
    print(f"Plugin execution result: {result}")
    
    # Unload plugin
    await plugin_manager.unload_plugin("sample_paradox_plugin")

if __name__ == "__main__":
    asyncio.run(test_plugin_framework()) 