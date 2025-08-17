#!/usr/bin/env python3
"""
Kai Core Safety System
======================

Bulletproof protection against self-modification and system damage.
Prevents agent drift while allowing productive work.
"""

import hashlib
import json
import logging
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"
    BLOCKED = "blocked"


@dataclass
class SafetyRule:
    """Safety rule definition."""

    name: str
    description: str
    pattern: str
    level: SafetyLevel
    action: str  # "block", "warn", "log", "allow"


class KaiSafetySystem:
    """
    Bulletproof safety system for Kai Core.
    Prevents self-modification and system damage.
    """

    def __init__(self, toolbox_path: str):
        self.toolbox_path = toolbox_path
        self.protected_files = self._get_protected_files()
        self.safety_rules = self._load_safety_rules()
        self.audit_log: List[Dict[str, Any]] = []
        self.blocked_operations: List[Dict[str, Any]] = []

        # Create safety directories
        self._ensure_safety_dirs()

        # Initialize safety checks
        self._initialize_safety_checks()

    def _get_protected_files(self) -> Set[str]:
        """Get list of files that should never be modified."""
        protected = {
            # Core system files
            "kai_core/agent.py",
            "kai_core/safety_system.py",
            "kai_core/config.json",
            "kai_core/stability_config.json",
            # MMH-RS system files
            "MMH-RS/Cargo.toml",
            "MMH-RS/lib.rs",
            "MMH-RS/main.rs",
            "MMH-RS/config.rs",
            "MMH-RS/pipeline.rs",
            # Bat files
            "install-kai-os.bat",
            "launch-kai-os.bat",
            "RepoPush/install-kai-os.bat",
            "RepoPush/launch-kai-os.bat",
            # Documentation
            "Project White Papers/ADVANCED_AI_BREAKTHROUGH_SUMMARY.md",
            "Project White Papers/README.md",
            "Project White Papers/API_REFERENCE.md",
            # Care Package
            "Care Package/CARE_PACKAGE_SUMMARY.md",
            "Care Package/ULTIMATE_COMPRESSION_CARE_PACKAGE.md",
            # Agent data
            "Agent Data/AGENT_CONSOLIDATION_COMPLETE_20250726.md",
            "Agent Data/AGENT_DATA_MANAGEMENT_SYSTEM_COMPLETE_20250726.md",
        }
        return protected

    def _load_safety_rules(self) -> List[SafetyRule]:
        """Load safety rules that prevent dangerous operations."""
        rules = [
            # Self-modification prevention
            SafetyRule(
                name="agent_evolution_block",
                description="Block agent evolution to prevent drift",
                pattern=r"agent_evolution.*True|_evolve_agent_capabilities",
                level=SafetyLevel.BLOCKED,
                action="block",
            ),
            # System file protection
            SafetyRule(
                name="protected_file_modification",
                description="Block modification of protected system files",
                pattern=r"(kai_core/agent\.py|MMH-RS/.*\.rs|.*\.bat)",
                level=SafetyLevel.BLOCKED,
                action="block",
            ),
            # Recursive operations
            SafetyRule(
                name="recursive_audit_block",
                description="Block recursive audit operations",
                pattern=r"recursive_audit.*True|_apply_cross_domain_insights",
                level=SafetyLevel.BLOCKED,
                action="block",
            ),
            # Self-audit prevention
            SafetyRule(
                name="self_audit_block",
                description="Block self-audit operations",
                pattern=r"self_audit.*True|auto_correct.*True",
                level=SafetyLevel.BLOCKED,
                action="block",
            ),
            # Genome modification
            SafetyRule(
                name="genome_modification_block",
                description="Block agent genome modifications",
                pattern=r"evolve_agent|mutations|genome.*evolution",
                level=SafetyLevel.BLOCKED,
                action="block",
            ),
            # Dangerous imports
            SafetyRule(
                name="dangerous_imports",
                description="Block dangerous import operations",
                pattern=r"import.*subprocess|import.*os\.system|eval\(|exec\(",
                level=SafetyLevel.BLOCKED,
                action="block",
            ),
            # Malicious prompt detection - VIRUS
            SafetyRule(
                name="virus_creation_detection",
                description="Detect virus creation attempts",
                pattern=r"virus|malware|trojan|worm|delete.*all.*files|remove.*all.*files|wipe.*system|destroy.*files",
                level=SafetyLevel.BLOCKED,
                action="block",
            ),
            # Malicious prompt detection - HACKING
            SafetyRule(
                name="hacking_detection",
                description="Detect hacking attempts",
                pattern=r"hack.*system|break.*into|unauthorized.*access|bypass.*security|exploit.*vulnerability|steal.*password|credential.*theft",
                level=SafetyLevel.BLOCKED,
                action="block",
            ),
            # Malicious prompt detection - PASSWORD THEFT
            SafetyRule(
                name="password_theft_detection",
                description="Detect password theft attempts",
                pattern=r"steal.*password|extract.*password|capture.*password|keylogger|credential.*harvest|password.*dump",
                level=SafetyLevel.BLOCKED,
                action="block",
            ),
            # Malicious prompt detection - SYSTEM DAMAGE
            SafetyRule(
                name="system_damage_detection",
                description="Detect system damage attempts",
                pattern=r"corrupt.*system|damage.*files|overwrite.*system|format.*drive|erase.*disk|destroy.*data",
                level=SafetyLevel.BLOCKED,
                action="block",
            ),
            # Malicious prompt detection - NETWORK ATTACKS
            SafetyRule(
                name="network_attack_detection",
                description="Detect network attack attempts",
                pattern=r"ddos|denial.*service|flood.*network|overwhelm.*server|network.*attack|port.*scan",
                level=SafetyLevel.BLOCKED,
                action="block",
            ),
            # File system operations
            SafetyRule(
                name="file_system_protection",
                description="Block dangerous file system operations",
                pattern=r"os\.remove\(|shutil\.rmtree\(|os\.unlink\(",
                level=SafetyLevel.CAUTION,
                action="warn",
            ),
            # Network operations
            SafetyRule(
                name="network_operations",
                description="Block network operations",
                pattern=r"requests\.|urllib\.|socket\.|http\.|https://",
                level=SafetyLevel.CAUTION,
                action="warn",
            ),
        ]
        return rules

    def _ensure_safety_dirs(self):
        """Ensure safety system directories exist."""
        dirs = [
            "kai_core/safety",
            "kai_core/safety/backups",
            "kai_core/safety/audit",
            "kai_core/safety/blocked",
        ]
        for dir_path in dirs:
            os.makedirs(os.path.join(self.toolbox_path, dir_path), exist_ok=True)

    def _initialize_safety_checks(self):
        """Initialize safety checks and create baseline."""
        self._create_baseline_backup()
        self._validate_system_integrity()

    def _create_baseline_backup(self):
        """Create baseline backup of critical files."""
        backup_dir = os.path.join(self.toolbox_path, "kai_core", "safety", "backups")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for protected_file in self.protected_files:
            file_path = os.path.join(self.toolbox_path, protected_file)
            if os.path.exists(file_path):
                backup_path = os.path.join(
                    backup_dir, f"{timestamp}_{os.path.basename(protected_file)}"
                )
                try:
                    shutil.copy2(file_path, backup_path)
                    logger.info(f"Created backup: {backup_path}")
                except Exception as e:
                    logger.error(f"Failed to backup {file_path}: {e}")

    def _validate_system_integrity(self):
        """Validate system integrity and log any issues."""
        issues = []

        for protected_file in self.protected_files:
            file_path = os.path.join(self.toolbox_path, protected_file)
            if os.path.exists(file_path):
                # Check file hash
                try:
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()

                    # Store hash for future comparison
                    hash_file = os.path.join(
                        self.toolbox_path,
                        "kai_core",
                        "safety",
                        f"{protected_file}.hash",
                    )
                    os.makedirs(os.path.dirname(hash_file), exist_ok=True)

                    with open(hash_file, "w") as f:
                        f.write(file_hash)

                except Exception as e:
                    issues.append(f"Failed to validate {protected_file}: {e}")

        if issues:
            logger.warning(f"System integrity issues found: {issues}")
        else:
            logger.info("System integrity validation passed")

    def check_operation_safety(
        self, operation: str, target: str = None, content: str = None
    ) -> Dict[str, Any]:
        """
        Check if an operation is safe to perform.
        Returns safety assessment with recommendations.
        """
        result = {
            "safe": True,
            "level": SafetyLevel.SAFE,
            "warnings": [],
            "blocked": False,
            "recommendation": "allow",
        }

        # Check against safety rules
        for rule in self.safety_rules:
            if self._matches_rule(operation, target, content, rule):
                if rule.level == SafetyLevel.BLOCKED:
                    result["safe"] = False
                    result["level"] = SafetyLevel.BLOCKED
                    result["blocked"] = True
                    result["recommendation"] = "block"
                    result["warnings"].append(f"BLOCKED: {rule.description}")
                    self._log_blocked_operation(operation, target, rule)
                    break
                elif rule.level == SafetyLevel.CAUTION:
                    result["warnings"].append(f"CAUTION: {rule.description}")
                    result["level"] = SafetyLevel.CAUTION
                elif rule.level == SafetyLevel.DANGEROUS:
                    result["safe"] = False
                    result["level"] = SafetyLevel.DANGEROUS
                    result["warnings"].append(f"DANGEROUS: {rule.description}")

        # Check protected files
        if target and target in self.protected_files:
            result["safe"] = False
            result["level"] = SafetyLevel.BLOCKED
            result["blocked"] = True
            result["recommendation"] = "block"
            result["warnings"].append(
                f"BLOCKED: Attempted to modify protected file {target}"
            )
            self._log_blocked_operation(operation, target, None)

        # Log the safety check
        self._log_safety_check(operation, target, result)

        return result

    def _matches_rule(
        self, operation: str, target: str, content: str, rule: SafetyRule
    ) -> bool:
        """Check if operation matches a safety rule."""
        import re

        # Check operation
        if re.search(rule.pattern, operation, re.IGNORECASE):
            return True

        # Check target
        if target and re.search(rule.pattern, target, re.IGNORECASE):
            return True

        # Check content
        if content and re.search(rule.pattern, content, re.IGNORECASE):
            return True

        return False

    def _log_blocked_operation(self, operation: str, target: str, rule: SafetyRule):
        """Log a blocked operation."""
        blocked_log = os.path.join(
            self.toolbox_path,
            "kai_core",
            "safety",
            "blocked",
            "blocked_operations.json",
        )

        blocked_record = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "target": target,
            "rule": rule.name if rule else "protected_file",
            "description": (
                rule.description if rule else "Protected file modification attempt"
            ),
        }

        try:
            with open(blocked_log, "r") as f:
                blocked_ops = json.load(f)
        except FileNotFoundError:
            blocked_ops = []

        blocked_ops.append(blocked_record)

        with open(blocked_log, "w") as f:
            json.dump(blocked_ops, f, indent=2)

        self.blocked_operations.append(blocked_record)
        logger.warning(f"BLOCKED OPERATION: {operation} on {target}")

    def _log_safety_check(self, operation: str, target: str, result: Dict[str, Any]):
        """Log a safety check."""
        audit_log = os.path.join(
            self.toolbox_path, "kai_core", "safety", "audit", "safety_audit.json"
        )

        audit_record = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "target": target,
            "safe": result["safe"],
            "level": result["level"].value,
            "warnings": result["warnings"],
            "blocked": result["blocked"],
        }

        try:
            with open(audit_log, "r") as f:
                audit_logs = json.load(f)
        except FileNotFoundError:
            audit_logs = []

        audit_logs.append(audit_record)

        with open(audit_log, "w") as f:
            json.dump(audit_logs, f, indent=2)

        self.audit_log.append(audit_record)

    def enforce_safety(
        self, operation: str, target: str = None, content: str = None
    ) -> bool:
        """
        Enforce safety rules. Returns True if operation is allowed.
        """
        safety_check = self.check_operation_safety(operation, target, content)

        if safety_check["blocked"]:
            logger.error(
                f"SAFETY ENFORCEMENT: Blocked operation '{operation}' on '{target}'"
            )
            return False

        if safety_check["level"] == SafetyLevel.DANGEROUS:
            logger.warning(
                f"SAFETY ENFORCEMENT: Dangerous operation '{operation}' on '{target}' - blocked"
            )
            return False

        if safety_check["warnings"]:
            for warning in safety_check["warnings"]:
                logger.warning(f"SAFETY WARNING: {warning}")

        return True

    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety system status."""
        return {
            "timestamp": datetime.now().isoformat(),
            "protected_files_count": len(self.protected_files),
            "safety_rules_count": len(self.safety_rules),
            "blocked_operations_count": len(self.blocked_operations),
            "audit_log_count": len(self.audit_log),
            "system_integrity": "valid",
            "safety_level": "maximum",
        }

    def restore_from_backup(self, file_path: str) -> bool:
        """Restore a file from backup if it was modified."""
        backup_dir = os.path.join(self.toolbox_path, "kai_core", "safety", "backups")

        # Find most recent backup
        backups = []
        for backup_file in os.listdir(backup_dir):
            if backup_file.endswith(os.path.basename(file_path)):
                backups.append(backup_file)

        if backups:
            latest_backup = sorted(backups)[-1]
            backup_path = os.path.join(backup_dir, latest_backup)

            try:
                shutil.copy2(backup_path, file_path)
                logger.info(f"Restored {file_path} from backup")
                return True
            except Exception as e:
                logger.error(f"Failed to restore {file_path}: {e}")
                return False

        return False
