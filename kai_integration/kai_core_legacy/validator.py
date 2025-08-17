#!/usr/bin/env python3
"""
Kai Core Code Validator
Validates generated code for safety, syntax, and functionality
"""

import ast
import os
import subprocess
import tempfile
from enum import Enum
from typing import Any, Dict, List


class ValidationLevel(Enum):
    SYNTAX = "syntax"
    SAFETY = "safety"
    FUNCTIONALITY = "functionality"
    SECURITY = "security"


class CodeValidator:
    """
    Validates generated code using multiple layers of checks
    """

    def __init__(self, toolbox_path: str):
        self.toolbox_path = toolbox_path
        self.safety_patterns = self._load_safety_patterns()
        self.security_patterns = self._load_security_patterns()

    def _load_safety_patterns(self) -> List[str]:
        """Load patterns that indicate unsafe code"""
        return [
            r"os\.system\(",
            r"subprocess\.call\(",
            r"eval\(",
            r"exec\(",
            r"__import__\(",
            r"open\(",
            r"file\(",
            r"input\(",
            r"raw_input\(",
            r"compile\(",
            r"reload\(",
            r"del\s+\w+\[",
            r"globals\(",
            r"locals\(",
            r"vars\(",
            r"dir\(",
            r"type\(",
            r"isinstance\(",
            r"issubclass\(",
            r"getattr\(",
            r"setattr\(",
            r"hasattr\(",
            r"delattr\(",
            r"property\(",
            r"super\(",
            r"__\w+__",
            r"import\s+\*",
            r"from\s+\w+\s+import\s+\*",
        ]

    def _load_security_patterns(self) -> List[str]:
        """Load patterns that indicate security risks"""
        return [
            r"password",
            r"secret",
            r"key",
            r"token",
            r"auth",
            r"login",
            r"admin",
            r"root",
            r"sudo",
            r"chmod",
            r"chown",
            r"rm\s+-rf",
            r"format\s+",
            r"delete\s+",
            r"remove\s+",
            r"unlink",
            r"unset",
            r"clear",
            r"reset",
            r"shutdown",
            r"reboot",
            r"halt",
            r"kill",
            r"terminate",
            r"abort",
            r"exit",
            r"quit",
        ]

    def validate_syntax(self, code: str) -> Dict[str, Any]:
        """Validate code syntax"""
        try:
            ast.parse(code)
            return {"valid": True, "error": None, "level": ValidationLevel.SYNTAX.value}
        except SyntaxError as e:
            return {
                "valid": False,
                "error": str(e),
                "level": ValidationLevel.SYNTAX.value,
            }

    def validate_safety(self, code: str) -> Dict[str, Any]:
        """Validate code for safety concerns"""
        import re

        issues = []
        for pattern in self.safety_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                issues.append(
                    {"pattern": pattern, "matches": len(matches), "severity": "high"}
                )

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "level": ValidationLevel.SAFETY.value,
            "risk_score": len(issues) * 10,
        }

    def validate_security(self, code: str) -> Dict[str, Any]:
        """Validate code for security risks"""
        import re

        risks = []
        for pattern in self.security_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                risks.append(
                    {"pattern": pattern, "matches": len(matches), "severity": "medium"}
                )

        return {
            "valid": len(risks) == 0,
            "risks": risks,
            "level": ValidationLevel.SECURITY.value,
            "risk_score": len(risks) * 5,
        }

    def validate_functionality(self, code: str) -> Dict[str, Any]:
        """Validate code for basic functionality"""
        checks = {
            "has_function": "def " in code,
            "has_return": "return" in code,
            "has_imports": "import " in code or "from " in code,
            "has_error_handling": "try:" in code and "except" in code,
            "has_docstring": '"""' in code or "'''" in code,
            "has_type_hints": "->" in code,
            "has_hash_validation": "hashlib" in code,
            "has_numpy": "numpy" in code or "np." in code,
        }

        valid = all(checks.values())

        return {
            "valid": valid,
            "checks": checks,
            "level": ValidationLevel.FUNCTIONALITY.value,
            "score": sum(checks.values()) / len(checks),
        }

    def run_test_validation(self, code: str) -> Dict[str, Any]:
        """Run the generated code in a safe environment"""
        try:
            # Create temporary test file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_file = f.name

            # Run with timeout
            result = subprocess.run(
                ["python", "-c", f"import {temp_file}"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Clean up
            os.unlink(temp_file)

            return {
                "valid": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else None,
                "output": result.stdout,
            }

        except subprocess.TimeoutExpired:
            return {"valid": False, "error": "Test timed out", "output": None}
        except Exception as e:
            return {"valid": False, "error": str(e), "output": None}

    def comprehensive_validation(self, code: str) -> Dict[str, Any]:
        """Run comprehensive validation on generated code"""
        results = {
            "syntax": self.validate_syntax(code),
            "safety": self.validate_safety(code),
            "security": self.validate_security(code),
            "functionality": self.validate_functionality(code),
            "test_run": self.run_test_validation(code),
        }

        # Overall validation result
        all_valid = all(result.get("valid", False) for result in results.values())

        # Calculate risk score
        risk_score = results["safety"].get("risk_score", 0) + results["security"].get(
            "risk_score", 0
        )

        return {
            "overall_valid": all_valid,
            "risk_score": risk_score,
            "results": results,
            "recommendations": self._generate_recommendations(results),
        }

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        if not results["syntax"]["valid"]:
            recommendations.append("Fix syntax errors before proceeding")

        if not results["safety"]["valid"]:
            recommendations.append("Remove unsafe code patterns")

        if not results["security"]["valid"]:
            recommendations.append("Review security-sensitive code")

        if not results["functionality"]["valid"]:
            recommendations.append("Add missing functionality components")

        if not results["test_run"]["valid"]:
            recommendations.append("Fix runtime errors in test execution")

        if results["safety"].get("risk_score", 0) > 20:
            recommendations.append("High safety risk - review carefully")

        if results["security"].get("risk_score", 0) > 10:
            recommendations.append("Security concerns detected")

        return recommendations
