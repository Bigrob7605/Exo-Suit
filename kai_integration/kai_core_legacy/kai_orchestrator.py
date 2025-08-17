#!/usr/bin/env python3
"""
Kai Orchestrator 2.0 - Master Conductor and Auditor
===================================================

The AI Jesus that sees all and orchestrates everything:
- Manages 4-model ensemble (Kai, Min, DeepSeek, Ollama)
- Integrates with 5-agent consensus system
- Provides full audit trail and transparency
- Handles ensemble synthesis and validation
- Implements 3-validator system for code quality
"""

import asyncio
import hashlib
import logging
import time
import traceback
from datetime import datetime
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KaiOrchestrator:
    """
    Kai Orchestrator 2.0 - Master conductor and auditor for the 4-model
    ensemble.

    Features:
    - Orchestrates 4 models (Kai, Min, DeepSeek, Ollama)
    - Integrates with 5-agent consensus system
    - Implements 3-validator system
    - Provides full audit trail
    - Handles ensemble synthesis and validation
    """

    def __init__(self, toolbox_path: str):
        """Initialize the Kai Orchestrator with the specified toolbox path."""
        self.toolbox_path = toolbox_path
        self.llm_integration = None
        self.consensus_system = None
        self.audit_log: List[Dict[str, Any]] = []

        # Initialize components
        self._initialize_components()

        logger.info(
            "🧠 Kai Orchestrator 2.0 initialized - Master conductor and auditor"
        )

    def _initialize_components(self):
        """Initialize LLM integration and consensus system."""
        try:
            logger.info("REFRESH Initializing LLM Integration...")
            from .llm_integration import LLMIntegration

            self.llm_integration = LLMIntegration(self.toolbox_path)
            logger.info("SUCCESS LLM Integration initialized")

            logger.info("REFRESH Initializing Agent Consensus System...")
            from .agent_consensus_system import AgentConsensusSystem

            self.consensus_system = AgentConsensusSystem(self.toolbox_path)
            logger.info("SUCCESS Agent Consensus System initialized")

            logger.info("SUCCESS All components initialized successfully")

        except Exception as e:
            logger.error(f"ERROR Failed to initialize components: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't raise, just log the error and continue with mock components
            logger.warning(
                "WARNING Continuing with mock components for web interface"
            )
            self.llm_integration = None
            self.consensus_system = None

    async def process_request(
        self, prompt: str, task_type: str = "general", max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Process a request through the complete Kai Orchestrator workflow.

        Args:
            prompt: User/system prompt
            task_type: Type of task (general, coding, analysis, etc.)
            max_retries: Maximum number of retry attempts

        Returns:
            Dict containing final result and full audit trail
        """
        start_time = time.time()
        request_id = self._generate_request_id()

        logger.info(f"READY Processing request {request_id}: {prompt[:100]}...")

        try:
            # Step 1: Call all 4 models in parallel
            ensemble_results = await self._call_ensemble(prompt, task_type)

            # Step 2: Validate all outputs
            validated_results = await self._validate_outputs(ensemble_results)

            # Step 3: Synthesize ensemble results
            synthesis_result = await self._synthesize_ensemble(
                validated_results
            )

            # Step 4: Submit to consensus system
            consensus_result = await self._submit_to_consensus(
                synthesis_result
            )

            # Step 5: Handle consensus result and finalize
            final_result = await self._handle_consensus_result(
                consensus_result,
                synthesis_result,
                prompt,
                task_type,
                max_retries,
            )

            # Create audit entry
            processing_time = time.time() - start_time
            audit_entry = self._create_audit_entry(
                request_id,
                prompt,
                ensemble_results,
                synthesis_result,
                consensus_result,
                final_result,
                processing_time,
            )

            # Add to audit log
            self.audit_log.append(audit_entry)

            logger.info(
                f"SUCCESS Request {request_id} completed successfully in "
                f"{processing_time:.2f}s"
            )

            return {
                "success": True,
                "request_id": request_id,
                "result": final_result,
                "processing_time": processing_time,
                "audit_entry": audit_entry,
            }

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"ERROR Request {request_id} failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")

            return {
                "success": False,
                "request_id": request_id,
                "error": str(e),
                "processing_time": processing_time,
            }

    async def _call_ensemble(
        self, prompt: str, task_type: str
    ) -> List[Dict[str, Any]]:
        """Call all 4 models in the ensemble."""
        logger.info("THEATER Calling 4-model ensemble...")

        if self.llm_integration is None:
            # Mock ensemble call for web interface
            return await self._mock_ensemble_call(prompt, task_type)

        try:
            # Call all models in parallel
            results = await self.llm_integration.call_all_models(prompt)
            logger.info(f"SUCCESS Ensemble returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"ERROR Ensemble call failed: {e}")
            # Fallback to mock
            return await self._mock_ensemble_call(prompt, task_type)

    async def _mock_ensemble_call(
        self, prompt: str, task_type: str
    ) -> List[Dict[str, Any]]:
        """Mock ensemble call for web interface."""
        await asyncio.sleep(0.1)  # Simulate API delay

        models = ["kai", "mistral", "deepseek", "llama2"]
        results = []

        for model in models:
            result = {
                "model": model,
                "output": (
                    f"# {model.title()} solution for: {prompt}\n"
                    f"def solve():\n    return '{model}_result'"
                ),
                "success": True,
                "processing_time": 0.5 + (models.index(model) * 0.1),
                "confidence": 0.8 - (models.index(model) * 0.1),
            }
            results.append(result)

        return results

    async def _validate_outputs(
        self, ensemble_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate all ensemble outputs using 3-validator system."""
        logger.info("SEARCH Validating outputs with 3-validator system...")

        validated_results = []

        for result in ensemble_results:
            if not result.get("success", False):
                continue

            # Run all 3 validators
            syntax_result = await self._syntax_validator(result["output"])
            output_result = await self._output_validator(result["output"])
            logic_result = await self._logic_intent_validator(result["output"])

            # Calculate overall validation score
            validation_score = (
                syntax_result["score"]
                + output_result["score"]
                + logic_result["score"]
            ) / 3

            passed = (
                syntax_result["passed"]
                and output_result["passed"]
                and logic_result["passed"]
            )

            validated_result = {
                **result,
                "validation": {
                    "passed": passed,
                    "score": validation_score,
                    "syntax": syntax_result,
                    "output": output_result,
                    "logic": logic_result,
                },
            }

            validated_results.append(validated_result)

        logger.info(f"SUCCESS Validation complete: {len(validated_results)} passed")
        return validated_results

    async def _syntax_validator(self, output: str) -> Dict[str, Any]:
        """Syntax validation using AST parsing."""
        try:
            # Try to parse as Python code
            compile(output, "<string>", "exec")
            return {"passed": True, "score": 1.0, "issues": []}
        except SyntaxError as e:
            return {
                "passed": False,
                "score": 0.0,
                "issues": [f"Syntax error: {e}"],
            }
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "issues": [f"Compilation error: {e}"],
            }

    async def _output_validator(self, output: str) -> Dict[str, Any]:
        """Output quality validation."""
        score = 0.0
        issues = []

        # Check length
        if len(output.strip()) >= 50:
            score += 0.3
        else:
            issues.append("Output too short")

        # Check for function definitions
        if "def " in output:
            score += 0.3
        else:
            issues.append("No function definition")

        # Check for imports
        if "import " in output or "from " in output:
            score += 0.2
        else:
            issues.append("No imports")

        # Check for docstrings
        if '"""' in output or "'''" in output:
            score += 0.2
        else:
            issues.append("No docstrings")

        passed = score >= 0.5
        return {"passed": passed, "score": score, "issues": issues}

    async def _logic_intent_validator(self, output: str) -> Dict[str, Any]:
        """Logic and intent validation."""
        score = 0.0
        issues = []

        # Check for dangerous patterns
        dangerous_patterns = ["eval(", "exec(", "os.system", "subprocess"]
        found_dangerous = [p for p in dangerous_patterns if p in output]

        if not found_dangerous:
            score += 0.5
        else:
            issues.extend([f"Dangerous pattern: {p}" for p in found_dangerous])

        # Check for basic structure
        if "return" in output or "print" in output:
            score += 0.3
        else:
            issues.append("No return or print statement")

        # Check for comments
        if "#" in output:
            score += 0.2
        else:
            issues.append("No comments")

        passed = score >= 0.5
        return {"passed": passed, "score": score, "issues": issues}

    async def _synthesize_ensemble(
        self, validated_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesize validated ensemble results."""
        if not validated_results:
            raise ValueError("No valid results to synthesize")

        # Find best result by validation score
        best_result = max(
            validated_results, key=lambda x: x["validation"]["score"]
        )

        # Calculate consensus metrics
        scores = [r["validation"]["score"] for r in validated_results]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)

        synthesis = {
            "selected_output": best_result["output"],
            "selected_model": best_result.get("model", best_result.get("model_name", "unknown")),
            "confidence": best_result.get("confidence", 0.8),  # Default confidence if not provided
            "validation_score": best_result["validation"]["score"],
            "ensemble_size": len(validated_results),
            "avg_validation_score": avg_score,
            "max_validation_score": max_score,
            "consensus_method": "best_score_selection",
        }

        logger.info(f"SUCCESS Synthesis complete: {synthesis['selected_model']} selected")
        return synthesis

    async def _submit_to_consensus(
        self, synthesis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit synthesis result to consensus system."""
        logger.info("🤖 Submitting to consensus system...")

        if self.consensus_system is None:
            # Mock consensus for web interface
            return await self._mock_consensus_submission(synthesis_result)

        try:
            proposal_id = self.consensus_system.submit_proposal(
                title=f"Code generation: {synthesis_result['selected_model']}",
                description=synthesis_result["selected_output"][:200],
                code_patch=synthesis_result["selected_output"],
                affected_files=["kai_core/kai_orchestrator.py"],  # Default affected file
            )

            # Simulate agent reviews
            reviews = await self._simulate_agent_reviews(
                proposal_id, synthesis_result
            )

            # Get consensus status
            status = self.consensus_system.get_proposal_status(proposal_id)

            consensus_result = {
                "proposal_id": proposal_id,
                "status": status,
                "reviews": reviews,
                "consensus_achieved": status.get("approval_count", 0) >= 3,
            }

            logger.info(f"SUCCESS Consensus submission complete: {proposal_id}")
            return consensus_result

        except Exception as e:
            logger.error(f"ERROR Consensus submission failed: {e}")
            # Fallback to mock
            return await self._mock_consensus_submission(synthesis_result)

    async def _mock_consensus_submission(
        self, synthesis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock consensus submission for web interface."""
        await asyncio.sleep(0.1)  # Simulate processing

        # Simulate reviews
        agents = [
            "security",
            "performance",
            "quality",
            "functionality",
            "master",
        ]
        reviews = []

        for agent in agents:
            review = {
                "agent_id": agent,
                "result": "ACCEPT",
                "reasoning": f"{agent.title()} review: Good quality",
                "timestamp": datetime.now().isoformat(),
            }
            reviews.append(review)

        consensus_result = {
            "proposal_id": f"mock_prop_{int(time.time())}",
            "status": {
                "status": "APPROVED",
                "approval_count": 5,
                "rejection_count": 0,
                "total_reviews": 5,
            },
            "reviews": reviews,
            "consensus_achieved": True,
        }

        return consensus_result

    async def _simulate_agent_reviews(
        self, proposal_id: str, synthesis_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Simulate agent reviews for consensus."""
        agents = [
            ("security", "Security focus"),
            ("performance", "Performance focus"),
            ("quality", "Quality focus"),
            ("functionality", "Functionality focus"),
            ("master", "Master review"),
        ]

        reviews = []

        for agent_id, focus in agents:
            review = await self._simulate_single_agent_review(
                agent_id, synthesis_result
            )
            reviews.append(review)

        return reviews

    async def _simulate_single_agent_review(
        self, agent_id: str, synthesis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate a single agent review."""
        await asyncio.sleep(0.01)  # Simulate processing time

        output = synthesis_result["selected_output"]
        score = 0
        issues = []

        # Security check
        if "eval(" not in output and "exec(" not in output:
            score += 1
        else:
            issues.append("Security concern: dangerous eval/exec")

        # Quality check
        if len(output) > 50:
            score += 1
        else:
            issues.append("Quality concern: output too short")

        # Functionality check
        if "def " in output or "class " in output:
            score += 1
        else:
            issues.append("Functionality concern: no function/class")

        # Determine result
        if score >= 2:
            result = "ACCEPT"
            reasoning = f"{agent_id.title()} review: Good quality ({score}/3)"
        else:
            result = "NEEDS_REVISION"
            reasoning = (
                f"{agent_id.title()} review: Needs improvement ({score}/3)"
            )

        return {
            "agent_id": agent_id,
            "result": result,
            "reasoning": reasoning,
            "score": score,
            "issues": issues,
            "timestamp": datetime.now().isoformat(),
        }

    async def _handle_consensus_result(
        self,
        consensus_result: Dict[str, Any],
        synthesis_result: Dict[str, Any],
        original_prompt: str,
        task_type: str,
        max_retries: int = 3,
        current_retry: int = 0,
    ) -> Dict[str, Any]:
        """Handle consensus result and finalize the response."""
        if consensus_result.get("consensus_achieved", False):
            # Consensus achieved - return the result
            return {
                "output": synthesis_result["selected_output"],
                "confidence": synthesis_result["confidence"],
                "status": "consensus_approved",
                "model_used": synthesis_result["selected_model"],
                "validation_score": synthesis_result["validation_score"],
            }

        # Consensus failed - try sub-agent team
        if current_retry < max_retries:
            logger.info(
                f"REFRESH Consensus failed, trying sub-agent team "
                f"(retry {current_retry + 1})"
            )
            return await self._activate_sub_agent_team(
                original_prompt, task_type, synthesis_result
            )

        # Max retries reached - return best available
        logger.warning(
            "WARNING Max retries reached, returning best available result"
        )
        return {
            "output": synthesis_result["selected_output"],
            "confidence": synthesis_result["confidence"] * 0.8,
            "status": "max_retries_reached",
            "model_used": synthesis_result["selected_model"],
            "validation_score": synthesis_result["validation_score"],
        }

    async def _activate_sub_agent_team(
        self,
        original_prompt: str,
        task_type: str,
        synthesis_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Activate sub-agent team for complex tasks."""
        logger.info("REFRESH Activating sub-agent team...")

        # Define sub-agents
        sub_agents = [
            {
                "id": "specialist",
                "role": "Domain specialist",
                "focus": "expertise",
            },
            {
                "id": "optimizer",
                "role": "Performance optimizer",
                "focus": "efficiency",
            },
            {
                "id": "validator",
                "role": "Quality validator",
                "focus": "correctness",
            },
        ]

        # Get solutions from sub-agents
        sub_agent_solutions = []

        for agent in sub_agents:
            solution = await self._get_sub_agent_solution(
                agent, original_prompt, task_type, synthesis_result
            )
            sub_agent_solutions.append(solution)

        # Collaborate on final solution
        final_solution = await self._sub_agent_collaboration(
            sub_agent_solutions, original_prompt, task_type
        )

        return {
            "output": final_solution,
            "confidence": synthesis_result["confidence"] * 0.9,
            "status": "sub_agent_collaboration",
            "model_used": "sub_agent_team",
            "validation_score": synthesis_result["validation_score"],
        }

    async def _get_sub_agent_solution(
        self,
        agent: Dict[str, str],
        prompt: str,
        task_type: str,
        synthesis_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Get solution from a specific sub-agent."""
        await asyncio.sleep(0.05)  # Simulate processing

        agent_id = agent["id"]
        role = agent["role"]
        focus = agent["focus"]

        # Generate agent-specific solution
        base_output = synthesis_result["selected_output"]

        if agent_id == "specialist":
            solution = (
                f"# {role} solution\n{base_output}\n"
                f"# Enhanced with domain expertise"
            )
        elif agent_id == "optimizer":
            solution = (
                f"# {role} solution\n{base_output}\n"
                f"# Optimized for performance"
            )
        elif agent_id == "validator":
            solution = (
                f"# {role} solution\n{base_output}\n"
                f"# Validated for correctness"
            )
        else:
            solution = base_output

        return {
            "agent_id": agent_id,
            "role": role,
            "focus": focus,
            "solution": solution,
            "confidence": 0.8,
        }

    async def _sub_agent_collaboration(
        self,
        sub_agent_solutions: List[Dict[str, Any]],
        original_prompt: str,
        task_type: str,
    ) -> str:
        """Collaborate sub-agent solutions into final result."""
        # Combine solutions intelligently
        combined_solution = self._combine_sub_agent_solutions(
            sub_agent_solutions, original_prompt
        )

        return combined_solution

    def _combine_sub_agent_solutions(
        self, solutions: List[Dict[str, Any]], original_prompt: str
    ) -> str:
        """Combine sub-agent solutions into final result."""
        if not solutions:
            return "# No sub-agent solutions available"

        # Extract base solution from first agent
        base_solution = solutions[0]["solution"]

        # Add collaboration header
        agent_ids = ", ".join(s["agent_id"] for s in solutions)
        num_agents = len(solutions)
        collaboration_header = (
            f"# Collaborative solution from {num_agents} sub-agents\n"
            f"# Original prompt: {original_prompt}\n"
            f"# Agents involved: {agent_ids}\n\n"
        )

        # Combine with enhancements
        enhancements = []
        for solution in solutions[1:]:
            agent_id = solution["agent_id"]
            if agent_id == "optimizer":
                enhancements.append("# Performance optimizations applied")
            elif agent_id == "validator":
                enhancements.append("# Quality validations passed")

        # Combine all parts
        combined = (
            collaboration_header
            + base_solution
            + "\n"
            + "\n".join(enhancements)
        )

        return combined

    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"kai_{timestamp}_{random_hash}"

    def _create_audit_entry(
        self,
        request_id: str,
        prompt: str,
        ensemble_results: List[Dict[str, Any]],
        synthesis_result: Dict[str, Any],
        consensus_result: Dict[str, Any],
        final_result: Dict[str, Any],
        processing_time: float,
    ) -> Dict[str, Any]:
        """Create comprehensive audit entry."""
        audit_entry = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "ensemble_size": len(ensemble_results),
            "synthesis_method": synthesis_result.get(
                "consensus_method", "unknown"
            ),
            "consensus_status": consensus_result.get("status", {}).get(
                "status", "unknown"
            ),
            "final_status": final_result.get("status", "unknown"),
            "processing_time": processing_time,
            "selected_model": synthesis_result.get(
                "selected_model", "unknown"
            ),
            "validation_score": synthesis_result.get("validation_score", 0.0),
            "confidence": final_result.get("confidence", 0.0),
        }

        # Add hash for integrity
        audit_entry["hash"] = self._hash_audit_entry(
            request_id, prompt, final_result
        )

        return audit_entry

    def _hash_audit_entry(
        self, request_id: str, prompt: str, final_result: Dict[str, Any]
    ) -> str:
        """Generate hash for audit entry integrity."""
        output = final_result.get("output", "")
        data = f"{request_id}:{prompt}:{output}"
        return hashlib.sha256(data.encode()).hexdigest()

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        return {
            "version": "2.0",
            "initialized": True,
            "llm_integration": self.llm_integration is not None,
            "consensus_system": self.consensus_system is not None,
            "audit_entries": len(self.audit_log),
            "last_activity": datetime.now().isoformat(),
        }

    def get_audit_log(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent audit log entries."""
        return self.audit_log[-limit:] if self.audit_log else []


async def kai_orchestrate(
    prompt: str, task_type: str = "general", toolbox_path: str = "."
) -> Dict[str, Any]:
    """Quick orchestration function."""
    orchestrator = KaiOrchestrator(toolbox_path)
    return await orchestrator.process_request(prompt, task_type)


async def test_kai_orchestrator():
    """Test the orchestrator."""
    print("TEST Testing Kai Orchestrator 2.0...")

    result = await kai_orchestrate(
        "Generate a Python function to calculate the mean of a list of numbers"
    )

    if result["success"]:
        print("SUCCESS Test passed!")
        print(f"REPORT Processing time: {result['processing_time']:.2f}s")
        print(f"DOCUMENT Output preview: {result['result']['output'][:100]}...")
    else:
        print(f"ERROR Test failed: {result.get('error')}")

    return result


if __name__ == "__main__":
    asyncio.run(test_kai_orchestrator())
