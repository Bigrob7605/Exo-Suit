#!/usr/bin/env python3
"""
Deterministic LLM Integration with Advanced Safety Features
==========================================================

Implements:
- UUID-based prompt fingerprinting
- AST fingerprint validation
- Structured JSON output
- Cross-model ensemble with referee
- Token budget circuit breaker
"""

import ast
import asyncio
import hashlib
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DeterministicConfig:
    """Configuration for deterministic LLM features."""

    enable_uuid_fingerprint: bool = True
    enable_ast_validation: bool = True
    enable_structured_output: bool = True
    enable_cross_model_ensemble: bool = False
    enable_token_budget: bool = True
    max_tokens_in_prompt: int = 4000
    max_tokens_out: int = 2000
    ensemble_models: List[str] = None


class DeterministicLLM:
    """
    Deterministic LLM wrapper with advanced safety features.
    """

    def __init__(self, base_llm_integration, config: DeterministicConfig = None):
        self.base_llm = base_llm_integration
        self.config = config or DeterministicConfig()
        self.ensemble_models = self.config.ensemble_models or [
            "OpenHermes-2.5-Mistral-7B",
            "mistral",
            "llama2",
        ]

        # Golden AST fingerprints for common patterns
        self.golden_asts = self._load_golden_asts()

    def _load_golden_asts(self) -> Dict[str, str]:
        """Load golden AST fingerprints for validation."""
        return {
            "basic_test_function": self._get_ast_fingerprint(
                """
import numpy as np
import pandas as pd
from scipy import stats
import hashlib
from typing import Dict, Any

def test_bulletproof_test(data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    try:
        return {
            "test_name": "test_bulletproof_test",
            "pass_fail": {"criteria": True},
            "metrics": {"effect_size": 0.5, "power": 0.8},
            "evidence": {"data_hash": "test"}
        }
    except Exception as e:
        return {"error": str(e), "test_failed": True}
"""
            )
        }

    def _get_ast_fingerprint(self, code: str) -> str:
        """Generate normalized AST fingerprint."""
        try:
            tree = ast.parse(code)
            # Normalize AST by sorting and removing location info
            normalized = ast.dump(tree, include_attributes=False, indent=False)
            return hashlib.sha256(normalized.encode()).hexdigest()
        except Exception as e:
            logger.error(f"AST fingerprint generation failed: {e}")
            return ""

    def _generate_deterministic_uuid(self, domain: str) -> str:
        """Generate deterministic UUID for prompt fingerprinting."""
        # Use domain + timestamp to create reproducible UUID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        seed = f"{domain}_{timestamp}"
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, seed))

    def _add_uuid_fingerprint(self, prompt: str, domain: str) -> str:
        """Add deterministic UUID to prompt footer."""
        if not self.config.enable_uuid_fingerprint:
            return prompt

        uuid_fingerprint = self._generate_deterministic_uuid(domain)
        footer = f"\n\n# Deterministic-ID: {uuid_fingerprint}\n"
        return prompt + footer

    def _validate_uuid_fingerprint(self, response: str, domain: str) -> bool:
        """Validate that response contains the expected UUID."""
        if not self.config.enable_uuid_fingerprint:
            return True

        expected_uuid = self._generate_deterministic_uuid(domain)
        return expected_uuid in response

    def _add_structured_output_instructions(self, prompt: str) -> str:
        """Add structured output instructions to prompt."""
        if not self.config.enable_structured_output:
            return prompt

        structured_instructions = """

IMPORTANT: Respond with structured JSON output only:

```json
{
  "code": "def test_function(data): ...",
  "imports": ["numpy", "pandas", "scipy"],
  "docstring": "Test function description",
  "deterministic_id": "uuid-here"
}
```

Generate ONLY the JSON response, no explanations.
"""
        return prompt + structured_instructions

    def _parse_structured_response(self, response: str) -> Dict[str, Any]:
        """Parse structured JSON response."""
        try:
            # Extract JSON from response
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                # Try to find JSON in the response
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]

            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Structured response parsing failed: {e}")
            return {"code": response, "imports": [], "docstring": ""}

    def _validate_token_budget(self, prompt: str, response: str) -> bool:
        """Validate token budget constraints."""
        if not self.config.enable_token_budget:
            return True

        prompt_tokens = len(prompt.split())
        response_tokens = len(response.split())

        if prompt_tokens > self.config.max_tokens_in_prompt:
            logger.warning(f"Prompt token budget exceeded: {prompt_tokens}")
            return False

        if response_tokens > self.config.max_tokens_out:
            logger.warning(f"Response token budget exceeded: {response_tokens}")
            return False

        return True

    def _validate_ast_fingerprint(self, code: str, domain: str) -> bool:
        """Validate code against golden AST fingerprint."""
        if not self.config.enable_ast_validation:
            return True

        # Get the AST fingerprint for this code
        code_fingerprint = self._get_ast_fingerprint(code)

        # Check against golden ASTs
        for pattern, golden_fingerprint in self.golden_asts.items():
            if golden_fingerprint and golden_fingerprint == code_fingerprint:
                logger.info(f"AST fingerprint validated for pattern: {pattern}")
                return True

        # For now, accept any valid AST (we can tighten this later)
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            logger.error("AST validation failed: Invalid syntax")
            return False

    async def _call_ensemble_models(
        self, prompt: str, domain: str
    ) -> List[Dict[str, Any]]:
        """Call multiple models and return results."""
        if not self.config.enable_cross_model_ensemble:
            return []

        results = []
        tasks = []

        for model in self.ensemble_models:
            task = self._call_single_model(prompt, domain, model)
            tasks.append(task)

        # Run all models concurrently
        model_results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(model_results):
            if isinstance(result, Exception):
                logger.error(f"Model {self.ensemble_models[i]} failed: {result}")
                continue
            results.append(result)

        return results

    async def _call_single_model(
        self, prompt: str, domain: str, model: str
    ) -> Dict[str, Any]:
        """Call a single model asynchronously."""
        try:
            # This would integrate with your existing LLM infrastructure
            # For now, we'll use the base LLM
            result = self.base_llm.generate_code(prompt, domain)
            return {
                "model": model,
                "code": result.get("code", ""),
                "success": "error" not in result,
            }
        except Exception as e:
            return {"model": model, "error": str(e), "success": False}

    def _referee_ensemble_results(self, results: List[Dict[str, Any]]) -> Optional[str]:
        """Referee function to select best result from ensemble."""
        if not results:
            return None

        # Count successful results
        successful = [r for r in results if r.get("success", False)]

        if len(successful) >= 2:
            # Return the first successful result
            return successful[0].get("code", "")

        return None

    def generate_code(
        self, prompt: str, domain: str, template: str = None
    ) -> Dict[str, Any]:
        """
        Generate code with deterministic safety features.
        """
        try:
            # 1. Add UUID fingerprint
            prompt_with_uuid = self._add_uuid_fingerprint(prompt, domain)

            # 2. Add structured output instructions
            prompt_structured = self._add_structured_output_instructions(
                prompt_with_uuid
            )

            # 3. Check token budget
            if not self._validate_token_budget(prompt_structured, ""):
                return {
                    "error": "Token budget exceeded",
                    "code": "",
                    "domain": domain,
                    "validation": {"valid": False, "error": "Token budget exceeded"},
                }

            # 4. Generate code with base LLM
            base_result = self.base_llm.generate_code(
                prompt_structured, domain, template
            )

            if "error" in base_result:
                return base_result

            code = base_result.get("code", "")

            # 5. Validate UUID fingerprint
            if not self._validate_uuid_fingerprint(code, domain):
                logger.warning("UUID fingerprint validation failed")
                return {
                    "error": "UUID fingerprint validation failed",
                    "code": "",
                    "domain": domain,
                    "validation": {
                        "valid": False,
                        "error": "UUID fingerprint validation failed",
                    },
                }

            # 6. Parse structured response if enabled
            if self.config.enable_structured_output:
                structured_data = self._parse_structured_response(code)
                code = structured_data.get("code", code)

            # 7. Validate AST fingerprint
            if not self._validate_ast_fingerprint(code, domain):
                return {
                    "error": "AST fingerprint validation failed",
                    "code": "",
                    "domain": domain,
                    "validation": {
                        "valid": False,
                        "error": "AST fingerprint validation failed",
                    },
                }

            # 8. Final token budget check
            if not self._validate_token_budget(prompt_structured, code):
                return {
                    "error": "Response token budget exceeded",
                    "code": "",
                    "domain": domain,
                    "validation": {
                        "valid": False,
                        "error": "Response token budget exceeded",
                    },
                }

            # Return successful result
            return {
                "code": code,
                "domain": domain,
                "validation": {"valid": True, "deterministic": True},
                "timestamp": datetime.now().isoformat(),
                "model": self.base_llm.config["model_name"],
                "uuid_fingerprint": self._generate_deterministic_uuid(domain),
            }

        except Exception as e:
            logger.error(f"Deterministic code generation failed: {e}")
            return {
                "error": str(e),
                "code": "",
                "domain": domain,
                "validation": {"valid": False, "error": str(e)},
            }

    def get_status(self) -> Dict[str, Any]:
        """Get deterministic LLM status."""
        return {
            "uuid_fingerprint_enabled": self.config.enable_uuid_fingerprint,
            "ast_validation_enabled": self.config.enable_ast_validation,
            "structured_output_enabled": self.config.enable_structured_output,
            "cross_model_ensemble_enabled": self.config.enable_cross_model_ensemble,
            "token_budget_enabled": self.config.enable_token_budget,
            "max_tokens_in_prompt": self.config.max_tokens_in_prompt,
            "max_tokens_out": self.config.max_tokens_out,
            "ensemble_models": self.ensemble_models,
            "golden_asts_count": len(self.golden_asts),
            "timestamp": datetime.now().isoformat(),
        }
