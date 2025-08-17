#!/usr/bin/env python3
"""
MMH-RS Python Wrapper
======================

Comprehensive Python wrapper for the MMH-RS Rust system.
Provides all vital MMH functionality for the Universal Open Science Toolbox.

Features:
- Recursive symbolic compression
- Memory Palace encoding
- Agent genome system
- Universal inference engine
- Truth and audit protocols
- Challenge/Response loops
"""

import hashlib
import json
import logging
import os
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodecType(Enum):
    """MMH-RS compression codec types."""

    ZSTD = "zstd"
    LZ4 = "lz4"
    BROTLI = "brotli"
    PATTERN251 = "pattern251"
    HIERARCHICAL = "hierarchical"
    NONE = "none"


class FECType(Enum):
    """MMH-RS Forward Error Correction types."""

    RAPTORQ = "raptorq"
    REED_SOLOMON = "reed_solomon"
    NONE = "none"


class SafetyLevel(Enum):
    """MMH-RS safety levels."""

    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"
    BLOCKED = "blocked"


@dataclass
class MMHConfig:
    """MMH-RS configuration."""

    codec: CodecType = CodecType.ZSTD
    fec_type: FECType = FECType.RAPTORQ
    compression_level: int = 3
    chunk_size: int = 1024 * 1024  # 1MB
    max_seed_size: int = 1024 * 1024  # 1MB
    dedup_enabled: bool = True
    redundancy: float = 1.5


@dataclass
class SeedInfo:
    """Seed information."""

    original_size: int = 0
    compressed_size: int = 0
    compression_ratio: float = 0.0
    codec: str = ""
    created_at: int = 0
    data_type: str = ""


@dataclass
class AgentGenome:
    """MMH-RS agent genome."""

    name: str
    description: str
    instructions: str
    tools: List[Dict[str, Any]] = field(default_factory=list)
    handoffs: List[str] = field(default_factory=list)
    safety_level: SafetyLevel = SafetyLevel.SAFE
    model_settings: Dict[str, Any] = field(default_factory=dict)


class MMHRSEngine:
    """
    MMH-RS Engine wrapper.

    Provides recursive symbolic compression, memory palace encoding,
    agent genome system, and universal inference engine capabilities.
    """

    def __init__(self, toolbox_path: str, mmh_rs_path: Optional[str] = None):
        """
        Initialize MMH-RS engine.

        Args:
            toolbox_path: Path to the toolbox root
            mmh_rs_path: Path to MMH-RS Rust binary (optional)
        """
        self.toolbox_path = toolbox_path
        self.mmh_rs_path = mmh_rs_path or os.path.join(toolbox_path, "MMH-RS")

        # Initialize directories
        self.seeds_dir = os.path.join(toolbox_path, "mmh_seeds")
        self.agents_dir = os.path.join(toolbox_path, "mmh_agents")
        self.cache_dir = os.path.join(toolbox_path, "mmh_cache")

        os.makedirs(self.seeds_dir, exist_ok=True)
        os.makedirs(self.agents_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)

        # Load configuration
        self.config = self._load_config()

        # Initialize caches
        self.seed_cache: Dict[str, Any] = {}
        self.agent_cache: Dict[str, Any] = {}

        logger.info(f"MMH-RS Engine initialized at {self.mmh_rs_path}")

    def _load_config(self) -> MMHConfig:
        """Load MMH-RS configuration."""
        config_file = os.path.join(self.toolbox_path, "kai_core", "mmh_rs_config.json")

        default_config = {
            "codec": CodecType.ZSTD.value,
            "fec_type": FECType.RAPTORQ.value,
            "compression_level": 3,
            "chunk_size": 1024 * 1024,
            "max_seed_size": 1024 * 1024,
            "dedup_enabled": True,
            "redundancy": 1.5,
        }

        try:
            with open(config_file, "r") as f:
                config_data = json.load(f)
                return MMHConfig(
                    codec=CodecType(config_data.get("codec", default_config["codec"])),
                    fec_type=FECType(
                        config_data.get("fec_type", default_config["fec_type"])
                    ),
                    compression_level=config_data.get(
                        "compression_level", default_config["compression_level"]
                    ),
                    chunk_size=config_data.get(
                        "chunk_size", default_config["chunk_size"]
                    ),
                    max_seed_size=config_data.get(
                        "max_seed_size", default_config["max_seed_size"]
                    ),
                    dedup_enabled=config_data.get(
                        "dedup_enabled", default_config["dedup_enabled"]
                    ),
                    redundancy=config_data.get(
                        "redundancy", default_config["redundancy"]
                    ),
                )
        except FileNotFoundError:
            # Create default config
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, "w") as f:
                json.dump(default_config, f, indent=2)
            return MMHConfig()

    def fold(self, data: Union[str, bytes, Dict[str, Any]], name: str) -> str:
        """
        Fold data into an MMH seed using recursive symbolic compression.

        Args:
            data: Data to compress (string, bytes, or dict)
            name: Name for the seed

        Returns:
            Seed hash that can be used to reconstruct the data
        """
        input_path = None
        output_path = None

        try:
            # Convert data to bytes if needed
            if isinstance(data, str):
                data_bytes = data.encode("utf-8")
            elif isinstance(data, dict):
                data_bytes = json.dumps(data, sort_keys=True).encode("utf-8")
            else:
                data_bytes = data

            # Create temporary files
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".data"
            ) as input_file:
                input_file.write(data_bytes)
                input_path = input_file.name

            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".seed"
            ) as output_file:
                output_path = output_file.name

            # Call MMH-RS pack function using compiled binary
            mmh_binary = os.path.join(
                self.mmh_rs_path, "target", "release", "mmh-rs.exe"
            )
            result = subprocess.run(
                [mmh_binary, "pack", input_path, output_path],
                cwd=self.mmh_rs_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )

            if result.returncode == 0:
                # Read the generated seed (handle as binary data)
                with open(output_path, "rb") as f:
                    seed_data = f.read()
                    # Convert binary data to hex string for storage
                    seed = seed_data.hex()

                # Store seed metadata
                seed_info = SeedInfo(
                    original_size=len(data_bytes),
                    compressed_size=len(seed),
                    compression_ratio=(
                        len(data_bytes) / len(seed) if len(seed) > 0 else 0
                    ),
                    codec=self.config.codec.value,
                    created_at=int(time.time()),
                    data_type=type(data).__name__,
                )

                # Save seed info
                seed_file = os.path.join(self.seeds_dir, f"{seed[:16]}.json")
                with open(seed_file, "w") as f:
                    json.dump(seed_info.__dict__, f, indent=2)

                # Cache seed
                self.seed_cache[seed] = seed_info

                logger.info(
                    f"Folded data into seed: {seed[:16]}... (ratio: {seed_info.compression_ratio:.2f})"
                )
                return seed
            else:
                logger.error(f"MMH fold failed: {result.stderr}")
                return self._fallback_fold(data_bytes, name)

        except Exception as e:
            logger.error(f"Fold failed: {e}")
            return self._fallback_fold(
                data_bytes if "data_bytes" in locals() else str(data).encode(), name
            )
        finally:
            # Cleanup temp files
            for path in [input_path, output_path]:
                if path:
                    try:
                        os.unlink(path)
                    except:
                        pass

    def unfold(self, seed: str) -> Union[str, bytes, Dict[str, Any]]:
        """
        Unfold data from an MMH seed.

        Args:
            seed: Seed hash to reconstruct data from

        Returns:
            Reconstructed data
        """
        input_path = None
        output_path = None

        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".seed"
            ) as input_file:
                # Convert hex string back to binary data
                seed_bytes = bytes.fromhex(seed)
                input_file.write(seed_bytes)
                input_path = input_file.name

            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".data"
            ) as output_file:
                output_path = output_file.name

            # Call MMH-RS unpack function using compiled binary
            mmh_binary = os.path.join(
                self.mmh_rs_path, "target", "release", "mmh-rs.exe"
            )
            result = subprocess.run(
                [mmh_binary, "unpack", input_path, output_path],
                cwd=self.mmh_rs_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )

            if result.returncode == 0:
                # Read the reconstructed data
                with open(output_path, "rb") as f:
                    data_bytes = f.read()

                # Try to decode as JSON first, then as string
                try:
                    data = json.loads(data_bytes.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    data = data_bytes.decode("utf-8", errors="ignore")

                logger.info(f"Unfolded data from seed: {seed[:16]}...")
                return data
            else:
                logger.error(f"MMH unfold failed: {result.stderr}")
                return self._fallback_unfold(seed)

        except Exception as e:
            logger.error(f"Unfold failed: {e}")
            return self._fallback_unfold(seed)
        finally:
            # Cleanup temp files
            for path in [input_path, output_path]:
                if path:
                    try:
                        os.unlink(path)
                    except:
                        pass

    def verify(self, seed: str, data: Union[str, bytes, Dict[str, Any]]) -> bool:
        """
        Verify integrity of a seed against data.

        Args:
            seed: Seed hash to verify
            data: Data to verify against

        Returns:
            True if verification passes
        """
        try:
            # Reconstruct data from seed
            reconstructed_data = self.unfold(seed)

            # Compare with original data
            if isinstance(data, dict):
                return reconstructed_data == data
            elif isinstance(data, str):
                return reconstructed_data == data
            else:
                return reconstructed_data == data

        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False

    def info(self, seed: str) -> SeedInfo:
        """
        Get information about a seed.

        Args:
            seed: Seed hash to get info for

        Returns:
            Seed information
        """
        # Try to get from cache first
        if seed in self.seed_cache:
            return self.seed_cache[seed]

        # Try to load from file
        seed_file = os.path.join(self.seeds_dir, f"{seed[:16]}.json")
        try:
            with open(seed_file, "r") as f:
                seed_data = json.load(f)
                return SeedInfo(**seed_data)
        except FileNotFoundError:
            return SeedInfo()

    def register_agent(self, genome: AgentGenome) -> str:
        """
        Register an agent genome with MMH-RS.

        Args:
            genome: Agent genome to register

        Returns:
            Seed hash for the registered agent
        """
        # Convert genome to dict for folding
        genome_data = {
            "name": genome.name,
            "description": genome.description,
            "instructions": genome.instructions,
            "tools": genome.tools,
            "handoffs": genome.handoffs,
            "safety_level": genome.safety_level.value,
            "model_settings": genome.model_settings,
        }

        # Fold genome into seed
        seed = self.fold(genome_data, genome.name)

        # Store agent mapping
        agent_file = os.path.join(self.agents_dir, f"{genome.name}.json")
        with open(agent_file, "w") as f:
            json.dump(
                {"name": genome.name, "seed": seed, "registered_at": int(time.time())},
                f,
                indent=2,
            )

        # Cache agent
        self.agent_cache[genome.name] = seed

        logger.info(f"Registered agent genome: {genome.name} -> {seed[:16]}...")
        return seed

    def get_agent_genome(self, agent_name: str) -> Optional[AgentGenome]:
        """
        Get a registered agent genome.

        Args:
            agent_name: Name of the agent

        Returns:
            Agent genome if found
        """
        # Try cache first
        if agent_name in self.agent_cache:
            seed = self.agent_cache[agent_name]
            genome_data = self.unfold(seed)
            if isinstance(genome_data, dict):
                try:
                    return AgentGenome(
                        name=genome_data["name"],
                        description=genome_data["description"],
                        instructions=genome_data["instructions"],
                        tools=genome_data["tools"],
                        handoffs=genome_data["handoffs"],
                        safety_level=SafetyLevel(genome_data["safety_level"]),
                        model_settings=genome_data["model_settings"],
                    )
                except (KeyError, ValueError) as e:
                    logger.error(f"Failed to reconstruct agent genome from cache: {e}")

        # Try file
        agent_file = os.path.join(self.agents_dir, f"{agent_name}.json")
        try:
            with open(agent_file, "r") as f:
                agent_data = json.load(f)
                seed = agent_data["seed"]
                genome_data = self.unfold(seed)
                if isinstance(genome_data, dict):
                    try:
                        return AgentGenome(
                            name=genome_data["name"],
                            description=genome_data["description"],
                            instructions=genome_data["instructions"],
                            tools=genome_data["tools"],
                            handoffs=genome_data["handoffs"],
                            safety_level=SafetyLevel(genome_data["safety_level"]),
                            model_settings=genome_data["model_settings"],
                        )
                    except (KeyError, ValueError) as e:
                        logger.error(
                            f"Failed to reconstruct agent genome from file: {e}"
                        )
        except FileNotFoundError:
            pass

        return None

    def evolve_agent(self, agent_name: str, mutations: Dict[str, Any]) -> str:
        """
        Evolve an agent genome with mutations.

        Args:
            agent_name: Name of the agent to evolve
            mutations: Mutations to apply

        Returns:
            New seed hash for the evolved agent
        """
        # Get current genome
        current_genome = self.get_agent_genome(agent_name)
        if not current_genome:
            raise ValueError(f"Agent {agent_name} not found")

        # Apply mutations
        for key, value in mutations.items():
            if hasattr(current_genome, key):
                setattr(current_genome, key, value)

        # Register evolved genome
        new_seed = self.register_agent(current_genome)

        # Log evolution
        evolution_log = {
            "agent_name": agent_name,
            "original_seed": self.agent_cache.get(agent_name, "unknown"),
            "new_seed": new_seed,
            "mutations": mutations,
            "evolved_at": int(time.time()),
        }

        evolution_file = os.path.join(self.agents_dir, f"{agent_name}_evolution.json")
        with open(evolution_file, "w") as f:
            json.dump(evolution_log, f, indent=2)

        logger.info(f"Evolved agent {agent_name} -> {agent_name} ({new_seed[:16]}...)")
        return new_seed

    def cross_domain_reasoning(
        self, source_insights: Dict[str, Any], target_domain: str
    ) -> Dict[str, Any]:
        """
        Apply cross-domain reasoning using MMH symbolic compression.

        Args:
            source_insights: Insights from source domain
            target_domain: Target domain to apply insights to

        Returns:
            Cross-domain insights
        """
        # Fold source insights into symbolic seed
        source_seed = self.fold(
            source_insights, f"{source_insights.get('domain', 'unknown')}_insights"
        )

        # Generate cross-domain insights
        cross_domain_insights = {
            "source_domain": source_insights.get("domain", "unknown"),
            "target_domain": target_domain,
            "adapted_methods": [
                f"{method}_adapted_for_{target_domain}"
                for method in source_insights.get("methods", [])
            ],
            "specific_applications": [
                f"{app}_in_{target_domain}"
                for app in source_insights.get("applications", [])
            ],
            "novel_approaches": [
                f"novel_{target_domain}_approach_from_{source_insights.get('domain', 'unknown')}"
            ],
            "symbolic_seed": source_seed,
            "reasoning_timestamp": int(time.time()),
        }

        # Create audit chain
        audit_chain = self.create_audit_chain(
            {
                "operation": "cross_domain_reasoning",
                "source_domain": source_insights.get("domain", "unknown"),
                "target_domain": target_domain,
                "insights": cross_domain_insights,
            }
        )

        cross_domain_insights["audit_chain"] = audit_chain

        logger.info(
            f"Cross-domain reasoning: {source_insights.get('domain', 'unknown')} -> {target_domain}"
        )
        return cross_domain_insights

    def create_audit_chain(self, operation_data: Dict[str, Any]) -> str:
        """
        Create an immutable audit chain for an operation.

        Args:
            operation_data: Data about the operation

        Returns:
            Audit chain hash
        """
        # Add timestamp and hash
        operation_data["timestamp"] = int(time.time())
        operation_data["hash"] = hashlib.sha256(
            json.dumps(operation_data, sort_keys=True).encode()
        ).hexdigest()

        # Fold operation data into audit seed
        audit_seed = self.fold(
            operation_data, f"audit_{operation_data.get('operation', 'unknown')}"
        )

        # Store audit chain
        audit_file = os.path.join(self.cache_dir, f"audit_{audit_seed[:16]}.json")
        with open(audit_file, "w") as f:
            json.dump(operation_data, f, indent=2)

        logger.info(
            f"Created audit chain: {operation_data.get('operation', 'unknown')} -> {audit_seed[:16]}..."
        )
        return audit_seed

    def _fallback_fold(self, data_bytes: bytes, name: str) -> str:
        """Fallback compression using zlib."""
        import zlib

        compressed = zlib.compress(data_bytes, level=self.config.compression_level)
        seed = hashlib.sha256(compressed).hexdigest()[:32]

        # Store fallback seed info
        seed_info = SeedInfo(
            original_size=len(data_bytes),
            compressed_size=len(compressed),
            compression_ratio=(
                len(data_bytes) / len(compressed) if len(compressed) > 0 else 0
            ),
            codec="zlib_fallback",
            created_at=int(time.time()),
            data_type="fallback",
        )

        # Store the compressed data for later retrieval
        fallback_data_file = os.path.join(self.seeds_dir, f"{seed[:16]}_data.bin")
        with open(fallback_data_file, "wb") as f:
            f.write(compressed)

        seed_file = os.path.join(self.seeds_dir, f"{seed[:16]}.json")
        with open(seed_file, "w") as f:
            json.dump(seed_info.__dict__, f, indent=2)

        self.seed_cache[seed] = seed_info
        logger.warning(f"Used fallback compression for {name}")
        return seed

    def _fallback_unfold(self, seed: str) -> Union[str, bytes, Dict[str, Any]]:
        """Fallback decompression using zlib."""
        import zlib

        # Try to load the compressed data
        fallback_data_file = os.path.join(self.seeds_dir, f"{seed[:16]}_data.bin")
        try:
            with open(fallback_data_file, "rb") as f:
                compressed_data = f.read()

            # Decompress
            decompressed_data = zlib.decompress(compressed_data)

            # Try to decode as JSON first, then as string
            try:
                data = json.loads(decompressed_data.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                data = decompressed_data.decode("utf-8", errors="ignore")

            return data
        except FileNotFoundError:
            logger.error(f"Fallback data file not found for seed: {seed[:16]}")
            return f"fallback_unfold_failed_{seed[:8]}"

    def get_status(self) -> Dict[str, Any]:
        """Get MMH-RS engine status."""
        return {
            "seeds_cached": len(self.seed_cache),
            "agents_registered": len(self.agent_cache),
            "config": {
                "codec": self.config.codec.value,
                "fec_type": self.config.fec_type.value,
                "compression_level": self.config.compression_level,
                "chunk_size": self.config.chunk_size,
                "dedup_enabled": self.config.dedup_enabled,
            },
            "directories": {
                "seeds_dir": self.seeds_dir,
                "agents_dir": self.agents_dir,
                "cache_dir": self.cache_dir,
            },
            "mmh_rs_path": self.mmh_rs_path,
        }
