#!/usr/bin/env python3
"""
Regression Testing System for Kai Core
=====================================

Implements:
- Prompt versioning with Git
- Diff-driven regression tests
- AST comparison
- Golden test result validation
"""

import ast
import hashlib
import json
import logging
import os
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of a regression test."""

    prompt_hash: str
    code_ast: str
    execution_success: bool
    execution_output: str
    timestamp: str
    domain: str


@dataclass
class RegressionTest:
    """A regression test case."""

    prompt: str
    expected_ast: str
    expected_output: str
    domain: str
    test_id: str


class RegressionTester:
    """
    Regression testing system for prompt versioning and validation.
    """

    def __init__(self, toolbox_path: str):
        self.toolbox_path = toolbox_path
        self.test_results_dir = os.path.join(
            toolbox_path, "kai_core", "regression_tests"
        )
        self.golden_results_dir = os.path.join(
            toolbox_path, "kai_core", "golden_results"
        )

        # Ensure directories exist
        os.makedirs(self.test_results_dir, exist_ok=True)
        os.makedirs(self.golden_results_dir, exist_ok=True)

        # Load golden results
        self.golden_results = self._load_golden_results()

    def _load_golden_results(self) -> Dict[str, RegressionTest]:
        """Load golden test results."""
        golden_results = {}

        golden_file = os.path.join(self.golden_results_dir, "golden_results.json")
        if os.path.exists(golden_file):
            try:
                with open(golden_file, "r") as f:
                    data = json.load(f)
                    for test_id, test_data in data.items():
                        golden_results[test_id] = RegressionTest(
                            prompt=test_data["prompt"],
                            expected_ast=test_data["expected_ast"],
                            expected_output=test_data["expected_output"],
                            domain=test_data["domain"],
                            test_id=test_id,
                        )
            except Exception as e:
                logger.error(f"Failed to load golden results: {e}")

        return golden_results

    def _save_golden_results(self):
        """Save golden test results."""
        golden_file = os.path.join(self.golden_results_dir, "golden_results.json")

        data = {}
        for test_id, test in self.golden_results.items():
            data[test_id] = {
                "prompt": test.prompt,
                "expected_ast": test.expected_ast,
                "expected_output": test.expected_output,
                "domain": test.domain,
            }

        with open(golden_file, "w") as f:
            json.dump(data, f, indent=2)

    def _get_prompt_hash(self, prompt: str) -> str:
        """Generate hash for prompt."""
        return hashlib.sha256(prompt.encode()).hexdigest()

    def _get_ast_fingerprint(self, code: str) -> str:
        """Generate AST fingerprint for code."""
        try:
            tree = ast.parse(code)
            normalized = ast.dump(tree, include_attributes=False, indent=False)
            return hashlib.sha256(normalized.encode()).hexdigest()
        except Exception as e:
            logger.error(f"AST fingerprint generation failed: {e}")
            return ""

    def _execute_code_safely(self, code: str) -> Tuple[bool, str]:
        """Execute code safely and return success status and output."""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(code)
                temp_file = f.name

            # Execute code
            result = subprocess.run(
                [
                    "python",
                    "-c",
                    f"exec(open(r'{temp_file}', encoding='utf-8').read())",
                ],
                shell=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Clean up
            os.unlink(temp_file)

            return result.returncode == 0, result.stdout + result.stderr

        except Exception as e:
            return False, str(e)

    def add_golden_test(self, prompt: str, code: str, domain: str) -> str:
        """Add a golden test case."""
        test_id = f"{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Generate AST fingerprint
        ast_fingerprint = self._get_ast_fingerprint(code)

        # Execute code to get expected output
        success, output = self._execute_code_safely(code)

        # Create golden test
        golden_test = RegressionTest(
            prompt=prompt,
            expected_ast=ast_fingerprint,
            expected_output=output if success else "",
            domain=domain,
            test_id=test_id,
        )

        self.golden_results[test_id] = golden_test
        self._save_golden_results()

        logger.info(f"Added golden test: {test_id}")
        return test_id

    def run_regression_test(
        self, prompt: str, code: str, domain: str
    ) -> Dict[str, Any]:
        """Run regression test against golden results."""
        prompt_hash = self._get_prompt_hash(prompt)
        code_ast = self._get_ast_fingerprint(code)

        # Execute code
        execution_success, execution_output = self._execute_code_safely(code)

        # Find matching golden tests
        matching_tests = []
        for test_id, golden_test in self.golden_results.items():
            if golden_test.domain == domain:
                matching_tests.append((test_id, golden_test))

        results = {
            "prompt_hash": prompt_hash,
            "code_ast": code_ast,
            "execution_success": execution_success,
            "execution_output": execution_output,
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "matching_golden_tests": len(matching_tests),
            "ast_matches": [],
            "output_matches": [],
            "overall_success": True,
        }

        # Compare with golden tests
        for test_id, golden_test in matching_tests:
            ast_match = code_ast == golden_test.expected_ast
            output_match = execution_output == golden_test.expected_output

            results["ast_matches"].append({"test_id": test_id, "match": ast_match})

            results["output_matches"].append(
                {"test_id": test_id, "match": output_match}
            )

            if not ast_match or not output_match:
                results["overall_success"] = False

        # Save test result
        self._save_test_result(results)

        return results

    def _save_test_result(self, result: Dict[str, Any]):
        """Save test result to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = os.path.join(
            self.test_results_dir, f"test_result_{timestamp}.json"
        )

        with open(result_file, "w") as f:
            json.dump(result, f, indent=2)

    def run_diff_regression_tests(
        self, old_prompt: str, new_prompt: str, domain: str
    ) -> Dict[str, Any]:
        """Run regression tests comparing old vs new prompts."""
        logger.info(f"Running diff regression tests for domain: {domain}")

        # Find golden tests for this domain
        domain_tests = [
            test for test in self.golden_results.values() if test.domain == domain
        ]

        if not domain_tests:
            logger.warning(f"No golden tests found for domain: {domain}")
            return {"success": False, "error": "No golden tests found"}

        results = {
            "old_prompt_hash": self._get_prompt_hash(old_prompt),
            "new_prompt_hash": self._get_prompt_hash(new_prompt),
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "tests_run": len(domain_tests),
            "tests_passed": 0,
            "tests_failed": 0,
            "detailed_results": [],
        }

        # Run tests with both prompts
        for test in domain_tests:
            # Test with old prompt
            old_result = self.run_regression_test(old_prompt, test.prompt, domain)

            # Test with new prompt
            new_result = self.run_regression_test(new_prompt, test.prompt, domain)

            # Compare results
            test_passed = (
                old_result["overall_success"]
                and new_result["overall_success"]
                and old_result["code_ast"] == new_result["code_ast"]
            )

            if test_passed:
                results["tests_passed"] += 1
            else:
                results["tests_failed"] += 1

            results["detailed_results"].append(
                {
                    "test_id": test.test_id,
                    "passed": test_passed,
                    "old_ast": old_result["code_ast"],
                    "new_ast": new_result["code_ast"],
                    "ast_changed": old_result["code_ast"] != new_result["code_ast"],
                }
            )

        results["success"] = results["tests_failed"] == 0

        return results

    def get_regression_stats(self) -> Dict[str, Any]:
        """Get regression testing statistics."""
        return {
            "golden_tests_count": len(self.golden_results),
            "domains_covered": list(
                set(test.domain for test in self.golden_results.values())
            ),
            "latest_test_results": self._get_latest_test_results(),
            "timestamp": datetime.now().isoformat(),
        }

    def _get_latest_test_results(self) -> List[Dict[str, Any]]:
        """Get latest test results."""
        results = []

        if os.path.exists(self.test_results_dir):
            for filename in os.listdir(self.test_results_dir):
                if filename.startswith("test_result_") and filename.endswith(".json"):
                    filepath = os.path.join(self.test_results_dir, filename)
                    try:
                        with open(filepath, "r") as f:
                            result = json.load(f)
                            results.append(result)
                    except Exception as e:
                        logger.error(f"Failed to load test result {filename}: {e}")

        # Sort by timestamp and return latest 10
        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return results[:10]
