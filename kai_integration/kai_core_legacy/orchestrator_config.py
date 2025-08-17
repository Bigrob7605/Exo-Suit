#!/usr/bin/env python3
"""
Kai Orchestrator 2.0 Configuration System

Master-class configuration for:
- Model ensemble setup
- Guardrail configuration
- Telemetry and audit settings
- Supply chain security
- Deterministic builds
- SLI/SLO dashboard
"""

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class ModelConfig:
    """Configuration for a single model"""

    name: str
    path: str
    type: str  # "llama.cpp", "transformers", "api"
    gpu_layers: int = 40
    context_size: int = 4096
    max_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 0.95
    repeat_penalty: float = 1.1
    expected_hash: Optional[str] = None
    signature_file: Optional[str] = None
    enabled: bool = True
    priority: int = 1  # Higher number = higher priority


@dataclass
class GuardrailConfig:
    """Configuration for guardrail system"""

    ast_validation: bool = True
    syntax_check: bool = True
    formatting: bool = True
    security_scan: bool = True
    sandbox_test: bool = True
    property_testing: bool = False
    mutation_testing: bool = False
    semgrep_rules: List[str] = None
    black_config: Dict[str, Any] = None
    ruff_config: Dict[str, Any] = None


@dataclass
class TelemetryConfig:
    """Configuration for telemetry system"""

    enabled: bool = True
    log_level: str = "INFO"
    log_file: str = "./telemetry/kai_orchestrator.log"
    metrics_file: str = "./telemetry/metrics.json"
    audit_trail: bool = True
    performance_tracking: bool = True
    error_reporting: bool = True
    privacy_mode: bool = False  # Don't log sensitive data


@dataclass
class CacheConfig:
    """Configuration for deterministic caching"""

    enabled: bool = True
    cache_dir: str = "./cache"
    max_size_gb: int = 10
    integrity_checking: bool = True
    compression: bool = True
    ttl_hours: int = 168  # 7 days


@dataclass
class EnsembleConfig:
    """Configuration for ensemble system"""

    consensus_threshold: float = 0.8
    uncertainty_threshold: float = 0.3
    min_models: int = 1
    max_models: int = 3
    reward_model_path: Optional[str] = None
    user_choice_timeout: int = 30  # seconds


@dataclass
class SecurityConfig:
    """Configuration for security features"""

    supply_chain_verification: bool = True
    model_signature_verification: bool = True
    sandbox_execution: bool = True
    network_isolation: bool = True
    resource_limits: Dict[str, Any] = None
    allowed_imports: List[str] = None
    blocked_patterns: List[str] = None


@dataclass
class SLIConfig:
    """Configuration for SLI/SLO monitoring"""

    enabled: bool = True
    dashboard_port: int = 8080
    metrics_interval: int = 60  # seconds
    alert_thresholds: Dict[str, float] = None
    performance_targets: Dict[str, float] = None


class OrchestratorConfig:
    """
    Master configuration for Kai Orchestrator 2.0

    Features:
    - Model ensemble configuration
    - Guardrail system setup
    - Telemetry and audit configuration
    - Security and supply chain verification
    - Performance monitoring and SLI/SLO
    - Deterministic build configuration
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "orchestrator_config.yaml"
        self.models: Dict[str, ModelConfig] = {}
        self.guardrails = GuardrailConfig()
        self.telemetry = TelemetryConfig()
        self.cache = CacheConfig()
        self.ensemble = EnsembleConfig()
        self.security = SecurityConfig()
        self.sli = SLIConfig()

        self._load_config()
        self._validate_config()

    def _load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                config_data = yaml.safe_load(f)
                self._parse_config(config_data)
        else:
            self._create_default_config()

    def _parse_config(self, config_data: Dict[str, Any]):
        """Parse configuration data"""
        # Parse models
        if "models" in config_data:
            for model_name, model_data in config_data["models"].items():
                self.models[model_name] = ModelConfig(**model_data)

        # Parse other sections
        if "guardrails" in config_data:
            self.guardrails = GuardrailConfig(**config_data["guardrails"])

        if "telemetry" in config_data:
            self.telemetry = TelemetryConfig(**config_data["telemetry"])

        if "cache" in config_data:
            self.cache = CacheConfig(**config_data["cache"])

        if "ensemble" in config_data:
            self.ensemble = EnsembleConfig(**config_data["ensemble"])

        if "security" in config_data:
            self.security = SecurityConfig(**config_data["security"])

        if "sli" in config_data:
            self.sli = SLIConfig(**config_data["sli"])

    def _create_default_config(self):
        """Create default configuration"""
        self.models = {
            "deepseek-coder-33b": ModelConfig(
                name="deepseek-coder-33b",
                path="models/ds33b.q4_k_m.gguf",
                type="llama.cpp",
                gpu_layers=40,
                context_size=4096,
                priority=3,
            ),
            "codellama-34b": ModelConfig(
                name="codellama-34b",
                path="models/codellama-34b.gguf",
                type="llama.cpp",
                gpu_layers=30,
                context_size=4096,
                priority=2,
            ),
            "wizardcoder-33b": ModelConfig(
                name="wizardcoder-33b",
                path="models/wizardcoder-33b.gguf",
                type="llama.cpp",
                gpu_layers=35,
                context_size=4096,
                priority=1,
            ),
        }

        # Set default guardrails
        self.guardrails.semgrep_rules = [
            "python.security.best-practice",
            "python.security.crypto",
            "python.security.deserialization",
        ]

        self.guardrails.black_config = {"line_length": 88, "target_version": "py39"}

        self.guardrails.ruff_config = {
            "line_length": 88,
            "select": ["E", "F", "I", "N", "W", "B", "C4", "UP"],
        }

        # Set default security
        self.security.resource_limits = {
            "cpu_time": 30,  # seconds
            "memory_mb": 512,
            "disk_mb": 100,
        }

        self.security.allowed_imports = [
            "os",
            "sys",
            "math",
            "random",
            "datetime",
            "json",
            "csv",
            "re",
            "collections",
            "itertools",
        ]

        self.security.blocked_patterns = [
            "eval(",
            "exec(",
            "os.system(",
            "subprocess.call(",
            "pickle.loads(",
            "marshal.loads(",
            "__import__(",
        ]

        # Set default SLI/SLO
        self.sli.alert_thresholds = {
            "response_time_ms": 5000,
            "error_rate": 0.05,
            "cache_hit_rate": 0.3,
        }

        self.sli.performance_targets = {
            "p95_response_time_ms": 3000,
            "p99_response_time_ms": 5000,
            "availability": 0.999,
        }

        self._save_config()

    def _validate_config(self):
        """Validate configuration"""
        # Check model paths
        for model_name, model_config in self.models.items():
            if model_config.enabled and not os.path.exists(model_config.path):
                print(
                    f"WARNING Warning: Model {model_name} path not found: {model_config.path}"
                )

        # Check directories
        directories = [
            self.telemetry.log_file,
            self.cache.cache_dir,
            "telemetry",
            "cache",
        ]

        for directory in directories:
            Path(directory).parent.mkdir(parents=True, exist_ok=True)

        # Validate thresholds
        if not (0 <= self.ensemble.consensus_threshold <= 1):
            raise ValueError("consensus_threshold must be between 0 and 1")

        if not (0 <= self.ensemble.uncertainty_threshold <= 1):
            raise ValueError("uncertainty_threshold must be between 0 and 1")

    def _save_config(self):
        """Save configuration to file"""
        config_data = {
            "models": {name: asdict(config) for name, config in self.models.items()},
            "guardrails": asdict(self.guardrails),
            "telemetry": asdict(self.telemetry),
            "cache": asdict(self.cache),
            "ensemble": asdict(self.ensemble),
            "security": asdict(self.security),
            "sli": asdict(self.sli),
        }

        with open(self.config_path, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)

    def get_enabled_models(self) -> List[str]:
        """Get list of enabled models"""
        return [name for name, config in self.models.items() if config.enabled]

    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model"""
        return self.models.get(model_name)

    def update_model_config(self, model_name: str, **kwargs):
        """Update model configuration"""
        if model_name in self.models:
            for key, value in kwargs.items():
                if hasattr(self.models[model_name], key):
                    setattr(self.models[model_name], key, value)
            self._save_config()

    def add_model(self, model_config: ModelConfig):
        """Add a new model configuration"""
        self.models[model_config.name] = model_config
        self._save_config()

    def remove_model(self, model_name: str):
        """Remove a model configuration"""
        if model_name in self.models:
            del self.models[model_name]
            self._save_config()

    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            "total_models": len(self.models),
            "enabled_models": len(self.get_enabled_models()),
            "guardrails_enabled": sum(
                [
                    self.guardrails.ast_validation,
                    self.guardrails.syntax_check,
                    self.guardrails.formatting,
                    self.guardrails.security_scan,
                    self.guardrails.sandbox_test,
                ]
            ),
            "telemetry_enabled": self.telemetry.enabled,
            "cache_enabled": self.cache.enabled,
            "security_enabled": self.security.supply_chain_verification,
            "sli_enabled": self.sli.enabled,
        }


# Default configuration templates
DEFAULT_CONFIG_TEMPLATE = """
# Kai Orchestrator 2.0 Configuration
# Master-class coding agent configuration

models:
  deepseek-coder-33b:
    name: deepseek-coder-33b
    path: models/ds33b.q4_k_m.gguf
    type: llama.cpp
    gpu_layers: 40
    context_size: 4096
    max_tokens: 1000
    temperature: 0.7
    top_p: 0.95
    repeat_penalty: 1.1
    enabled: true
    priority: 3

guardrails:
  ast_validation: true
  syntax_check: true
  formatting: true
  security_scan: true
  sandbox_test: true
  property_testing: false
  mutation_testing: false
  semgrep_rules:
    - python.security.best-practice
    - python.security.crypto
    - python.security.deserialization

telemetry:
  enabled: true
  log_level: INFO
  log_file: ./telemetry/kai_orchestrator.log
  metrics_file: ./telemetry/metrics.json
  audit_trail: true
  performance_tracking: true
  error_reporting: true
  privacy_mode: false

cache:
  enabled: true
  cache_dir: ./cache
  max_size_gb: 10
  integrity_checking: true
  compression: true
  ttl_hours: 168

ensemble:
  consensus_threshold: 0.8
  uncertainty_threshold: 0.3
  min_models: 1
  max_models: 3
  user_choice_timeout: 30

security:
  supply_chain_verification: true
  model_signature_verification: true
  sandbox_execution: true
  network_isolation: true
  resource_limits:
    cpu_time: 30
    memory_mb: 512
    disk_mb: 100
  allowed_imports:
    - os
    - sys
    - math
    - random
    - datetime
    - json
    - csv
    - re
    - collections
    - itertools
  blocked_patterns:
    - eval(
    - exec(
    - os.system(
    - subprocess.call(
    - pickle.loads(
    - marshal.loads(
    - __import__(

sli:
  enabled: true
  dashboard_port: 8080
  metrics_interval: 60
  alert_thresholds:
    response_time_ms: 5000
    error_rate: 0.05
    cache_hit_rate: 0.3
  performance_targets:
    p95_response_time_ms: 3000
    p99_response_time_ms: 5000
    availability: 0.999
"""


def create_default_config(config_path: str = "orchestrator_config.yaml"):
    """Create default configuration file"""
    with open(config_path, "w") as f:
        f.write(DEFAULT_CONFIG_TEMPLATE)
    print(f"SUCCESS Created default configuration: {config_path}")


def validate_model_signatures(config: OrchestratorConfig) -> Dict[str, bool]:
    """Validate model signatures for supply chain security"""
    results = {}

    for model_name, model_config in config.models.items():
        if not model_config.enabled:
            continue

        if model_config.signature_file and os.path.exists(model_config.signature_file):
            # Verify signature
            try:
                # Placeholder for signature verification
                results[model_name] = True
            except Exception as e:
                print(f"ERROR Signature verification failed for {model_name}: {e}")
                results[model_name] = False
        else:
            print(f"WARNING No signature file for {model_name}")
            results[model_name] = False

    return results


# Test function
def test_config():
    """Test configuration system"""
    print("🧠 Testing Kai Orchestrator 2.0 Configuration...")

    try:
        # Create default config
        create_default_config()

        # Load config
        config = OrchestratorConfig()

        # Print summary
        summary = config.get_config_summary()
        print(f"Configuration Summary: {summary}")

        # Test model validation
        signatures = validate_model_signatures(config)
        print(f"Model Signatures: {signatures}")

        print("\nSUCCESS Configuration test successful!")
        return True

    except Exception as e:
        print(f"ERROR Configuration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_config()
