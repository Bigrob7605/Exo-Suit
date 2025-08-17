#!/usr/bin/env python3
"""
Kai Core MMH Integration
========================

Integration of MMH-RS (Meta-Math Holograph) with Kai Core.
Provides recursive symbolic compression, memory palace encoding,
agent genome system, and universal inference engine capabilities.
"""

import os
import sys
import json
import hashlib
import tempfile
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import logging

# Import the comprehensive MMH-RS wrapper
from .mmh_rs_wrapper import (
    MMHRSEngine,
    MMHConfig,
    SeedInfo,
    AgentGenome,
    CodecType,
    FECType,
    SafetyLevel,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MMHIntegration:
    """
    MMH Integration for Kai Core.

    Provides recursive symbolic compression, memory palace encoding,
    agent genome system, and universal inference engine capabilities.
    """

    def __init__(self, toolbox_path: str):
        """
        Initialize MMH integration.

        Args:
            toolbox_path: Path to the toolbox root
        """
        self.toolbox_path = toolbox_path

        # Initialize MMH-RS engine
        self.mmh_engine = MMHRSEngine(toolbox_path)

        # Load configuration
        self.config = self._load_config()

        logger.info("MMH Integration initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load MMH configuration."""
        config_file = os.path.join(self.toolbox_path, "kai_core", "mmh_config.json")

        default_config = {
            "mmh_enabled": True,
            "agent_evolution": True,
            "recursive_audit": True,
            "cross_domain_reasoning": True,
            "compression_level": 3,
            "codec": "zstd",
            "fec_type": "raptorq",
            "dedup_enabled": True,
            "redundancy": 1.5,
        }

        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                return {**default_config, **config}
        except FileNotFoundError:
            # Create default config
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, "w") as f:
                json.dump(default_config, f, indent=2)
            return default_config

    def fold_data(self, data: Union[str, bytes, Dict[str, Any]], name: str) -> str:
        """
        Fold data into an MMH seed using recursive symbolic compression.

        Args:
            data: Data to compress (string, bytes, or dict)
            name: Name for the seed

        Returns:
            Seed hash that can be used to reconstruct the data
        """
        return self.mmh_engine.fold(data, name)

    def unfold_data(self, seed: str) -> Union[str, bytes, Dict[str, Any]]:
        """
        Unfold data from an MMH seed.

        Args:
            seed: Seed hash to reconstruct data from

        Returns:
            Reconstructed data
        """
        return self.mmh_engine.unfold(seed)

    def verify_data(self, seed: str, data: Union[str, bytes, Dict[str, Any]]) -> bool:
        """
        Verify integrity of a seed against data.

        Args:
            seed: Seed hash to verify
            data: Data to verify against

        Returns:
            True if verification passes
        """
        return self.mmh_engine.verify(seed, data)

    def get_seed_info(self, seed: str) -> SeedInfo:
        """
        Get information about a seed.

        Args:
            seed: Seed hash to get info for

        Returns:
            Seed information
        """
        return self.mmh_engine.info(seed)

    def register_agent(self, genome: AgentGenome) -> str:
        """
        Register an agent genome in the MMH system.

        Args:
            genome: Agent genome to register

        Returns:
            Registration hash
        """
        return self.mmh_engine.register_agent(genome)

    def register_agent_genome(self, agent_name: str, description: str) -> AgentGenome:
        """
        Register an agent genome by name and description.

        Args:
            agent_name: Name of the agent
            description: Description of the agent

        Returns:
            Agent genome object
        """
        genome = AgentGenome(
            name=agent_name,
            description=description,
            instructions=f"Agent {agent_name}: {description}",
            tools=[],
            handoffs=[],
            safety_level=SafetyLevel.SAFE,
            model_settings={},
        )

        # Register the genome
        self.mmh_engine.register_agent(genome)

        return genome

    def get_agent_genome(self, agent_name: str) -> Optional[AgentGenome]:
        """
        Get a registered agent genome.

        Args:
            agent_name: Name of the agent

        Returns:
            Agent genome if found
        """
        return self.mmh_engine.get_agent_genome(agent_name)

    def evolve_agent(self, agent_name: str, mutations: Dict[str, Any]) -> str:
        """
        Evolve an agent genome with mutations.

        Args:
            agent_name: Name of the agent to evolve
            mutations: Mutations to apply

        Returns:
            New seed hash for the evolved agent
        """
        return self.mmh_engine.evolve_agent(agent_name, mutations)

    def cross_domain_reasoning(
        self,
        source_insights: Dict[str, Any],
        target_domain: str,
        source_domain: str = None,
    ) -> Dict[str, Any]:
        """
        Apply cross-domain reasoning using MMH symbolic compression.

        Args:
            source_insights: Insights from source domain
            target_domain: Target domain to apply insights to
            source_domain: Source domain name (optional)

        Returns:
            Cross-domain insights
        """
        # Add source domain to insights if provided
        if source_domain:
            source_insights = {
                **source_insights,
                "source_domain": source_domain,
                "target_domain": target_domain,
                "timestamp": datetime.now().isoformat(),
            }

        return self.mmh_engine.cross_domain_reasoning(source_insights, target_domain)

    def create_audit_chain(
        self, operation_name: str, operation_data: Dict[str, Any]
    ) -> str:
        """
        Create an immutable audit chain for an operation.

        Args:
            operation_name: Name of the operation
            operation_data: Data about the operation

        Returns:
            Audit chain hash
        """
        full_data = {
            "operation_name": operation_name,
            "operation_data": operation_data,
            "timestamp": datetime.now().isoformat(),
        }
        return self.mmh_engine.create_audit_chain(full_data)

    def get_status(self) -> Dict[str, Any]:
        """Get MMH integration status."""
        mmh_status = self.mmh_engine.get_status()

        return {
            "mmh_enabled": self.config.get("mmh_enabled", True),
            "agent_evolution": self.config.get("agent_evolution", True),
            "recursive_audit": self.config.get("recursive_audit", True),
            "cross_domain_reasoning": self.config.get("cross_domain_reasoning", True),
            "seeds_cached": mmh_status["seeds_cached"],
            "agents_registered": mmh_status["agents_registered"],
            "config": mmh_status["config"],
            "directories": mmh_status["directories"],
        }

    def benchmark_compression(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Benchmark MMH compression performance.

        Args:
            test_data: Test data to benchmark

        Returns:
            Benchmark results
        """
        start_time = time.time()

        # Test folding
        seed = self.fold_data(test_data, "benchmark_test")
        fold_time = time.time() - start_time

        # Test unfolding
        start_time = time.time()
        unfolded_data = self.unfold_data(seed)
        unfold_time = time.time() - start_time

        # Get seed info
        seed_info = self.get_seed_info(seed)

        # Verify integrity
        verification_passed = self.verify_data(seed, test_data)

        return {
            "seed": seed,
            "fold_time": fold_time,
            "unfold_time": unfold_time,
            "total_time": fold_time + unfold_time,
            "compression_ratio": seed_info.compression_ratio,
            "original_size": seed_info.original_size,
            "compressed_size": seed_info.compressed_size,
            "verification_passed": verification_passed,
            "data_integrity": unfolded_data == test_data,
        }

    def test_mmh_functionality(self) -> Dict[str, Any]:
        """
        Test MMH functionality with comprehensive tests.

        Returns:
            Test results
        """
        test_results = {
            "fold_unfold": False,
            "agent_registration": False,
            "agent_evolution": False,
            "cross_domain_reasoning": False,
            "audit_chain": False,
            "verification": False,
            "compression_benchmark": False,
        }

        try:
            # Test 1: Fold/Unfold
            test_data = {"test": "data", "number": 42, "list": [1, 2, 3]}
            seed = self.fold_data(test_data, "test_functionality")
            unfolded_data = self.unfold_data(seed)
            test_results["fold_unfold"] = unfolded_data == test_data

            # Test 2: Agent Registration
            genome = AgentGenome(
                name="test_agent",
                description="Test agent for MMH functionality",
                instructions="Test instructions",
                tools=[{"name": "test_tool", "description": "Test tool"}],
                safety_level=SafetyLevel.SAFE,
            )
            agent_seed = self.register_agent(genome)
            retrieved_genome = self.get_agent_genome("test_agent")
            test_results["agent_registration"] = retrieved_genome is not None

            # Test 3: Agent Evolution
            mutations = {"description": "Evolved test agent"}
            evolved_seed = self.evolve_agent("test_agent", mutations)
            test_results["agent_evolution"] = evolved_seed != agent_seed

            # Test 4: Cross-Domain Reasoning
            source_insights = {
                "domain": "physics",
                "methods": ["matched_filter", "snr_analysis"],
                "applications": ["gravitational_waves"],
            }
            cross_domain_result = self.cross_domain_reasoning(
                source_insights, "seismology"
            )
            test_results["cross_domain_reasoning"] = (
                "adapted_methods" in cross_domain_result
            )

            # Test 5: Audit Chain
            audit_data = {"operation": "test", "data": test_data}
            audit_chain = self.create_audit_chain(audit_data)
            test_results["audit_chain"] = len(audit_chain) > 0

            # Test 6: Verification
            verification_passed = self.verify_data(seed, test_data)
            test_results["verification"] = verification_passed

            # Test 7: Compression Benchmark
            benchmark_result = self.benchmark_compression(test_data)
            test_results["compression_benchmark"] = benchmark_result[
                "verification_passed"
            ]

        except Exception as e:
            logger.error(f"MMH functionality test failed: {e}")

        return test_results

    def get_comprehensive_status(self) -> Dict[str, Any]:
        """
        Get comprehensive MMH status including functionality tests.

        Returns:
            Comprehensive status information
        """
        status = self.get_status()
        functionality_tests = self.test_mmh_functionality()

        return {
            **status,
            "functionality_tests": functionality_tests,
            "all_tests_passed": all(functionality_tests.values()),
            "test_summary": {
                "passed": sum(functionality_tests.values()),
                "total": len(functionality_tests),
                "success_rate": sum(functionality_tests.values())
                / len(functionality_tests)
                * 100,
            },
        }
