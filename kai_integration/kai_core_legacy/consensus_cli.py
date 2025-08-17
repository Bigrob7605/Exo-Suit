#!/usr/bin/env python3
"""
5 Agent Consensus CLI
=====================

Command-line interface for managing the 5 Agent Consensus self-evolution protocol.
Allows viewing proposals, submitting reviews, and approving changes.
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from kai_core.agent_consensus_system import ReviewResult, consensus_system


def print_proposal(proposal: Dict[str, Any], detailed: bool = False):
    """Print proposal information."""
    print(f"\nCHECKLIST PROPOSAL: {proposal['title']}")
    print(f"   ID: {proposal['proposal_id']}")
    print(f"   Status: {proposal['status']}")
    print(f"   Risk Level: {proposal['risk_level']}")
    print(f"   Submitted: {proposal['submitted_at']}")
    print(f"   By: {proposal['submitted_by']}")
    print(f"   Impact: {proposal['estimated_impact']}")

    if detailed:
        print(f"\nDOCUMENT Description: {proposal['description']}")
        print(f"FOLDER Affected Files: {', '.join(proposal['affected_files'])}")

        if proposal["reviews"]:
            print(f"\nSEARCH Reviews ({len(proposal['reviews'])}/5):")
            for review in proposal["reviews"]:
                result_emoji = (
                    "SUCCESS"
                    if review["result"] == "ACCEPT"
                    else "ERROR" if review["result"] == "REJECT" else "WARNING"
                )
                print(
                    f"   {result_emoji} {review['agent_name']} ({review['agent_id']})"
                )
                print(f"      Confidence: {review['confidence']}")
                print(f"      Reasoning: {review['reasoning'][:100]}...")
        else:
            print("\nSEARCH No reviews submitted yet")


def list_proposals(args):
    """List all proposals."""
    status_filter = args.status if hasattr(args, "status") else None
    proposals = consensus_system.list_proposals(status_filter=status_filter)

    if not proposals:
        print("📭 No proposals found")
        return

    print(f"\nCHECKLIST Found {len(proposals)} proposal(s):")
    for proposal in proposals:
        print_proposal(proposal, detailed=args.detailed)


def show_proposal(args):
    """Show detailed information about a specific proposal."""
    proposal = consensus_system.get_proposal_status(args.proposal_id)
    if not proposal:
        print(f"ERROR Proposal {args.proposal_id} not found")
        return

    print_proposal(proposal, detailed=True)


def submit_review(args):
    """Submit a review for a proposal."""
    # Validate result
    try:
        result = ReviewResult(args.result.upper())
    except ValueError:
        print(
            f"ERROR Invalid result: {args.result}. Must be ACCEPT, REJECT, or NEEDS_REVISION"
        )
        return

    # Submit review
    success = consensus_system.review_proposal(
        proposal_id=args.proposal_id,
        agent_id=args.agent_id,
        result=result,
        reasoning=args.reasoning,
        confidence=args.confidence,
        security_analysis=args.security_analysis or "",
        performance_analysis=args.performance_analysis or "",
        bug_analysis=args.bug_analysis or "",
    )

    if success:
        print(f"SUCCESS Review submitted successfully for proposal {args.proposal_id}")
    else:
        print(f"ERROR Failed to submit review for proposal {args.proposal_id}")


def approve_proposal(args):
    """Approve a proposal that has reached consensus."""
    success = consensus_system.approve_proposal(args.proposal_id)

    if success:
        print(f"SUCCESS Proposal {args.proposal_id} approved and merged successfully")
    else:
        print(f"ERROR Failed to approve proposal {args.proposal_id}")


def system_status(args):
    """Show consensus system status."""
    status = consensus_system.get_system_status()

    print("\nSEARCH CONSENSUS SYSTEM STATUS")
    print("=" * 40)
    print(f"Total Proposals: {status['total_proposals']}")
    print(f"Pending: {status['pending']}")
    print(f"Under Review: {status['under_review']}")
    print(f"Approved: {status['approved']}")
    print(f"Rejected: {status['rejected']}")
    print(f"Merged: {status['merged']}")
    print(f"Active Agents: {status['active_agents']}")
    print(f"Consensus Rule: {status['consensus_rule']}")
    print(f"System Healthy: {'SUCCESS' if status['system_healthy'] else 'ERROR'}")


def list_agents(args):
    """List all consensus agents."""
    agents = consensus_system.agents

    print("\n🤖 CONSENSUS AGENTS")
    print("=" * 30)
    for agent in agents:
        agent_type_emoji = (
            "🤖"
            if agent["type"] == "automated"
            else "👤" if agent["type"] == "human" else "💻"
        )
        print(f"{agent_type_emoji} {agent['name']} ({agent['id']})")
        print(f"   Type: {agent['type']}")
        print(f"   Focus: {', '.join(agent['focus'])}")
        print(f"   Trust Score: {agent['trust_score']}")
        print(f"   Description: {agent['description']}")
        print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="5 Agent Consensus System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python consensus_cli.py list
  python consensus_cli.py list --status UNDER_REVIEW --detailed
  python consensus_cli.py show <proposal_id>
  python consensus_cli.py review <proposal_id> <agent_id> ACCEPT "Looks good"
  python consensus_cli.py approve <proposal_id>
  python consensus_cli.py status
  python consensus_cli.py agents
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List proposals
    list_parser = subparsers.add_parser("list", help="List proposals")
    list_parser.add_argument(
        "--status",
        choices=["PENDING", "UNDER_REVIEW", "APPROVED", "REJECTED", "MERGED"],
        help="Filter by status",
    )
    list_parser.add_argument(
        "--detailed", action="store_true", help="Show detailed information"
    )
    list_parser.set_defaults(func=list_proposals)

    # Show proposal
    show_parser = subparsers.add_parser(
        "show", help="Show detailed proposal information"
    )
    show_parser.add_argument("proposal_id", help="Proposal ID")
    show_parser.set_defaults(func=show_proposal)

    # Submit review
    review_parser = subparsers.add_parser(
        "review", help="Submit a review for a proposal"
    )
    review_parser.add_argument("proposal_id", help="Proposal ID")
    review_parser.add_argument("agent_id", help="Agent ID")
    review_parser.add_argument(
        "result", choices=["ACCEPT", "REJECT", "NEEDS_REVISION"], help="Review result"
    )
    review_parser.add_argument("reasoning", help="Review reasoning")
    review_parser.add_argument(
        "--confidence", type=float, default=0.8, help="Confidence level (0.0-1.0)"
    )
    review_parser.add_argument("--security-analysis", help="Security analysis")
    review_parser.add_argument("--performance-analysis", help="Performance analysis")
    review_parser.add_argument("--bug-analysis", help="Bug analysis")
    review_parser.set_defaults(func=submit_review)

    # Approve proposal
    approve_parser = subparsers.add_parser(
        "approve", help="Approve a proposal that has reached consensus"
    )
    approve_parser.add_argument("proposal_id", help="Proposal ID")
    approve_parser.set_defaults(func=approve_proposal)

    # System status
    status_parser = subparsers.add_parser("status", help="Show system status")
    status_parser.set_defaults(func=system_status)

    # List agents
    agents_parser = subparsers.add_parser("agents", help="List consensus agents")
    agents_parser.set_defaults(func=list_agents)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        args.func(args)
    except Exception as e:
        print(f"ERROR Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
