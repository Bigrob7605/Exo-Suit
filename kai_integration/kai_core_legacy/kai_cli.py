#!/usr/bin/env python3
"""
Kai CLI - Command Line Interface for Kai Orchestrator 2.0
========================================================

CLI interface for the 3-model ensemble + 5-agent consensus system.
"""

import argparse
import asyncio
import os

# Import Kai components
import sys
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kai_core.kai_orchestrator import KaiOrchestrator


class KaiCLI:
    """Command line interface for Kai Orchestrator 2.0."""

    def __init__(self, toolbox_path: str = "."):
        self.toolbox_path = toolbox_path
        self.orchestrator = None

    async def initialize(self):
        """Initialize the orchestrator."""
        try:
            self.orchestrator = KaiOrchestrator(self.toolbox_path)
            print("🧠 Kai Orchestrator 2.0 initialized successfully")
            return True
        except Exception as e:
            print(f"ERROR Failed to initialize Kai Orchestrator: {e}")
            return False

    async def run_ensemble(
        self,
        prompt: str,
        task_type: str = "general",
        explain: bool = False,
        trace: bool = False,
    ) -> Dict[str, Any]:
        """Run ensemble mode with optional explain and trace."""
        if not self.orchestrator:
            if not await self.initialize():
                return {"success": False, "error": "Failed to initialize orchestrator"}

        print(f"READY Running ensemble mode with prompt: {prompt[:100]}...")

        try:
            result = await self.orchestrator.process_request(prompt, task_type)

            if result["success"]:
                print("SUCCESS Ensemble processing completed successfully")

                if explain:
                    self._explain_result(result)

                if trace:
                    self._trace_result(result)

                return result
            else:
                print(
                    f"ERROR Ensemble processing failed: {result.get('error', 'Unknown error')}"
                )
                return result

        except Exception as e:
            print(f"ERROR Ensemble processing error: {e}")
            return {"success": False, "error": str(e)}

    def _explain_result(self, result: Dict[str, Any]):
        """Explain the ensemble and consensus results."""
        print("\nREPORT EXPLANATION:")
        print("=" * 50)

        # Ensemble results
        ensemble_results = result.get("ensemble_results", [])
        print(f"THEATER Ensemble Results ({len(ensemble_results)}/3 models):")
        for i, model_result in enumerate(ensemble_results, 1):
            model_name = model_result.get("model_name", "unknown")
            success = model_result.get("success", False)
            processing_time = model_result.get("processing_time", 0)
            status = "SUCCESS" if success else "ERROR"
            print(f"  {i}. {model_name}: {status} ({processing_time:.2f}s)")

        # Synthesis result
        synthesis = result.get("result", {})
        if synthesis:
            method = synthesis.get("method", "unknown")
            confidence = synthesis.get("confidence", 0)
            selected_model = synthesis.get("selected_model", "unknown")
            print(f"\n🎼 Synthesis Method: {method}")
            print(f"   Confidence: {confidence:.2f}")
            print(f"   Selected Model: {selected_model}")

        # Consensus results
        consensus_result = result.get("consensus_result", {})
        if consensus_result:
            agent_reviews = consensus_result.get("agent_reviews", [])
            print(f"\n🤝 5-Agent Consensus Results:")
            for review in agent_reviews:
                agent_id = review.get("agent_id", "unknown")
                result_status = review.get("result", "UNKNOWN")
                reasoning = review.get("reasoning", "No reasoning provided")
                status_icon = "SUCCESS" if result_status == "ACCEPT" else "ERROR"
                print(f"  {agent_id}: {status_icon} {result_status} - {reasoning}")

        # Show Sub-Agent system if used
        synthesis = result.get("result", {})
        if synthesis.get("sub_agent_used", False):
            print(f"\nREADY 3 Sub-Agent Team Results:")
            print(
                "   Sub-Agents: Solution Architect + Domain Specialist + Quality Engineer"
            )
            print(f"   Collaboration Method: {synthesis.get('method', 'unknown')}")
            print(f"   Sub-Agent Votes: {synthesis.get('sub_agent_votes', 0)}/3")
            print("   SUCCESS No Omega loops! Sub-Agents collaborated successfully!")

        print("=" * 50)

    def _trace_result(self, result: Dict[str, Any]):
        """Show full trace of the processing."""
        print("\nSEARCH FULL TRACE:")
        print("=" * 50)

        # Request info
        request_id = result.get("request_id", "unknown")
        processing_time = result.get("processing_time", 0)
        print(f"Request ID: {request_id}")
        print(f"Processing Time: {processing_time:.2f}s")

        # Ensemble results detail
        ensemble_results = result.get("ensemble_results", [])
        print(f"\nEnsemble Results Detail:")
        for model_result in ensemble_results:
            model_name = model_result.get("model_name", "unknown")
            output = model_result.get("output", "")
            validation = model_result.get("validation", {})

            print(f"\n  Model: {model_name}")
            print(f"  Output: {output[:200]}...")
            print(f"  Validation: {validation}")

        # Synthesis detail
        synthesis = result.get("result", {})
        if synthesis:
            print(f"\nSynthesis Detail:")
            print(f"  Method: {synthesis.get('method', 'unknown')}")
            print(f"  Confidence: {synthesis.get('confidence', 0)}")
            print(f"  Final Output: {synthesis.get('final_output', '')[:200]}...")

        # Consensus detail
        consensus_result = result.get("consensus_result", {})
        if consensus_result:
            print(f"\nConsensus Detail:")
            print(f"  Proposal ID: {consensus_result.get('proposal_id', 'unknown')}")
            print(
                f"  Status: {consensus_result.get('consensus_status', {}).get('status', 'unknown')}"
            )

        print("=" * 50)

    async def show_status(self):
        """Show system status."""
        if not self.orchestrator:
            if not await self.initialize():
                return

        status = self.orchestrator.get_status()

        print("REPORT KAI ORCHESTRATOR 2.0 STATUS:")
        print("=" * 40)
        print(f"Version: {status.get('orchestrator_version', 'unknown')}")
        print(f"Ensemble Mode: {status.get('ensemble_mode', 'disabled')}")
        print(f"Models Available: {status.get('models_available', 0)}/3")
        print(
            f"Consensus System: {'SUCCESS Active' if status.get('consensus_system_active') else 'ERROR Inactive'}"
        )
        print(f"Audit Entries: {status.get('audit_entries', 0)}")
        print(f"Timestamp: {status.get('timestamp', 'unknown')}")

        # Show ensemble model status
        if self.orchestrator.llm_integration:
            ensemble_status = self.orchestrator.llm_integration.get_ensemble_status()
            print(f"\nTHEATER Ensemble Models:")
            for model_name, model_info in ensemble_status.get("models", {}).items():
                status_icon = "SUCCESS" if model_info.get("available", False) else "ERROR"
                print(
                    f"  {model_name}: {status_icon} {model_info.get('type', 'unknown')}"
                )

        print("=" * 40)

    async def show_audit_log(self, limit: int = 5):
        """Show recent audit log."""
        if not self.orchestrator:
            if not await self.initialize():
                return

        audit_entries = self.orchestrator.get_audit_log(limit)

        print(f"CHECKLIST RECENT AUDIT LOG (Last {len(audit_entries)} entries):")
        print("=" * 50)

        for i, entry in enumerate(audit_entries, 1):
            request_id = entry.get("request_id", "unknown")
            timestamp = entry.get("timestamp", "unknown")
            prompt = entry.get("prompt", "")[:50]
            processing_time = entry.get("processing_time", 0)

            print(f"{i}. {request_id}")
            print(f"   Time: {timestamp}")
            print(f"   Prompt: {prompt}...")
            print(f"   Duration: {processing_time:.2f}s")
            print()

        print("=" * 50)


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Kai Orchestrator 2.0 CLI")
    parser.add_argument(
        "--ensemble",
        action="store_true",
        help="Run in ensemble mode (3-model ensemble)",
    )
    parser.add_argument(
        "--explain", action="store_true", help="Show model votes and agent review votes"
    )
    parser.add_argument(
        "--trace", action="store_true", help="Output full workflow for audit"
    )
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--audit", action="store_true", help="Show recent audit log")
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of audit entries to show (default: 5)",
    )
    parser.add_argument(
        "--task-type",
        default="general",
        help="Task type (general, coding, analysis, etc.)",
    )
    parser.add_argument("prompt", nargs="?", type=str, help="User/system prompt")

    args = parser.parse_args()

    cli = KaiCLI()

    try:
        if args.status:
            await cli.show_status()
            return

        if args.audit:
            await cli.show_audit_log(args.limit)
            return

        if not args.prompt:
            print("ERROR Error: Prompt is required for ensemble mode")
            print("Usage: python kai_cli.py --ensemble 'Your prompt here'")
            return

        if args.ensemble:
            result = await cli.run_ensemble(
                args.prompt,
                task_type=args.task_type,
                explain=args.explain,
                trace=args.trace,
            )

            if result["success"]:
                # Check multiple possible locations for final output
                # The result structure is nested due to recursive calls
                final_output = None

                # Try to find the final output in the nested structure
                if "result" in result and isinstance(result["result"], dict):
                    nested_result = result["result"]
                    if "result" in nested_result and isinstance(
                        nested_result["result"], dict
                    ):
                        # Double nested
                        final_output = nested_result["result"].get("final_output")
                    else:
                        # Single nested
                        final_output = nested_result.get("final_output")

                if not final_output:
                    final_output = result.get("final_output", "No output available")

                print(f"\nSUCCESS Final Result: {final_output}")
            else:
                print(f"\nERROR Failed: {result.get('error', 'Unknown error')}")
        else:
            print("ERROR Error: --ensemble flag is required")
            print("Usage: python kai_cli.py --ensemble 'Your prompt here'")

    except KeyboardInterrupt:
        print("\nSTOP  Interrupted by user")
    except Exception as e:
        print(f"ERROR Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
