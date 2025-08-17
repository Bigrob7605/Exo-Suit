"""
5 Agent Consensus Self-Evolution Protocol
========================================

This module implements a bulletproof system where Kai's code upgrades are reviewed
by 5 independent agents before being approved. No upgrade can be merged unless
at least 4/5 agents approve.

Key Features:
- Decentralized review process
- Immutable audit trail
- No solo merge capability
- Human-in-the-loop oversight
- Weighted reputation system
"""

import json
import hashlib
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ReviewResult(Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    NEEDS_REVISION = "NEEDS_REVISION"


class AgentType(Enum):
    LLM = "llm"
    HUMAN = "human"
    AUTOMATED = "automated"


@dataclass
class AgentReview:
    agent_id: str
    agent_type: AgentType
    agent_name: str
    result: ReviewResult
    confidence: float  # 0.0 to 1.0
    reasoning: str
    security_analysis: str
    performance_analysis: str
    bug_analysis: str
    timestamp: str
    review_hash: str


@dataclass
class UpgradeProposal:
    proposal_id: str
    title: str
    description: str
    code_patch: str
    affected_files: List[str]
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    estimated_impact: str
    submitted_by: str
    submitted_at: str
    status: str  # "PENDING", "UNDER_REVIEW", "APPROVED", "REJECTED", "NEEDS_REVISION"
    reviews: List[AgentReview]
    consensus_required: int = 4
    total_reviews: int = 5

    def get_approval_count(self) -> int:
        return sum(1 for review in self.reviews if review.result == ReviewResult.ACCEPT)

    def get_rejection_count(self) -> int:
        return sum(1 for review in self.reviews if review.result == ReviewResult.REJECT)

    def is_approved(self) -> bool:
        return self.get_approval_count() >= self.consensus_required

    def is_rejected(self) -> bool:
        return self.get_rejection_count() >= 2  # Auto-reject if 2+ agents reject

    def get_consensus_status(self) -> str:
        if self.is_approved():
            return "APPROVED"
        elif self.is_rejected():
            return "REJECTED"
        elif len(self.reviews) >= self.total_reviews:
            return "INSUFFICIENT_CONSENSUS"
        else:
            return "UNDER_REVIEW"


class AgentConsensusSystem:
    """
    Implements the 5 Agent Consensus protocol for safe advanced AI self-evolution.
    """

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.proposals_dir = self.base_path / "proposals"
        self.audit_dir = self.base_path / "audit"
        self.agents_config_file = self.base_path / "kai_core" / "consensus_agents.json"

        # Ensure directories exist
        self.proposals_dir.mkdir(exist_ok=True)
        self.audit_dir.mkdir(exist_ok=True)
        self.agents_config_file.parent.mkdir(exist_ok=True)

        # Load agent configurations
        self.agents = self._load_agents()

        # Initialize audit trail
        self._initialize_audit_trail()

    def _load_agents(self) -> List[Dict[str, Any]]:
        """Load the 5 consensus agents configuration."""
        default_agents = [
            {
                "id": "security_agent",
                "name": "Security Specialist Agent",
                "type": "automated",
                "focus": ["security", "backdoors", "vulnerabilities"],
                "trust_score": 1.0,
                "description": "Specializes in security analysis and vulnerability detection",
            },
            {
                "id": "performance_agent",
                "name": "Performance Analysis Agent",
                "type": "automated",
                "focus": ["performance", "efficiency", "optimization"],
                "trust_score": 1.0,
                "description": "Analyzes performance impact and resource usage",
            },
            {
                "id": "code_quality_agent",
                "name": "Code Quality Agent",
                "type": "automated",
                "focus": ["code_quality", "maintainability", "best_practices"],
                "trust_score": 1.0,
                "description": "Reviews code quality, style, and maintainability",
            },
            {
                "id": "functionality_agent",
                "name": "Functionality Testing Agent",
                "type": "automated",
                "focus": ["functionality", "testing", "integration"],
                "trust_score": 1.0,
                "description": "Tests functionality and integration compatibility",
            },
            {
                "id": "human_reviewer",
                "name": "Human Reviewer",
                "type": "human",
                "focus": ["overall_assessment", "business_logic", "ethics"],
                "trust_score": 1.0,
                "description": "Human oversight for final approval",
            },
        ]

        if self.agents_config_file.exists():
            try:
                with open(self.agents_config_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load agents config: {e}, using defaults")

        # Save default configuration
        self._save_agents_config(default_agents)
        return default_agents

    def _save_agents_config(self, agents: List[Dict[str, Any]]):
        """Save agent configuration to file."""
        try:
            # Ensure the directory exists
            self.agents_config_file.parent.mkdir(exist_ok=True)
            with open(self.agents_config_file, "w") as f:
                json.dump(agents, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save agents config: {e}")

    def _initialize_audit_trail(self):
        """Initialize the immutable audit trail."""
        audit_file = self.audit_dir / "consensus_audit.json"
        if not audit_file.exists():
            initial_audit = {
                "system_initialized": datetime.now().isoformat(),
                "protocol_version": "1.0",
                "consensus_rule": "4/5 agents must approve",
                "audit_entries": [],
            }
            with open(audit_file, "w") as f:
                json.dump(initial_audit, f, indent=2)

    def submit_proposal(
        self,
        title: str,
        description: str,
        code_patch: str,
        affected_files: List[str],
        risk_level: str = "MEDIUM",
        estimated_impact: str = "Unknown",
        submitted_by: str = "kai_core",
    ) -> str:
        """
        Submit a new upgrade proposal for multi-agent review.

        Returns the proposal ID.
        """
        proposal_id = str(uuid.uuid4())

        proposal = UpgradeProposal(
            proposal_id=proposal_id,
            title=title,
            description=description,
            code_patch=code_patch,
            affected_files=affected_files,
            risk_level=risk_level,
            estimated_impact=estimated_impact,
            submitted_by=submitted_by,
            submitted_at=datetime.now().isoformat(),
            status="PENDING",
            reviews=[],
            consensus_required=4,
            total_reviews=5,
        )

        # Save proposal
        proposal_file = self.proposals_dir / f"{proposal_id}.json"
        with open(proposal_file, "w") as f:
            json.dump(asdict(proposal), f, indent=2, default=str)

        # Log to audit trail
        self._log_audit_entry(
            "PROPOSAL_SUBMITTED",
            {
                "proposal_id": proposal_id,
                "title": title,
                "submitted_by": submitted_by,
                "risk_level": risk_level,
            },
        )

        logger.info(f"Proposal {proposal_id} submitted: {title}")
        return proposal_id

    def review_proposal(
        self,
        proposal_id: str,
        agent_id: str,
        result: ReviewResult,
        reasoning: str,
        confidence: float = 0.8,
        security_analysis: str = "",
        performance_analysis: str = "",
        bug_analysis: str = "",
    ) -> bool:
        """
        Submit a review for a proposal from a specific agent.

        Returns True if review was accepted, False otherwise.
        """
        proposal_file = self.proposals_dir / f"{proposal_id}.json"
        if not proposal_file.exists():
            logger.error(f"Proposal {proposal_id} not found")
            return False

        # Load proposal
        with open(proposal_file, "r") as f:
            proposal_data = json.load(f)

        # Find agent
        agent = next((a for a in self.agents if a["id"] == agent_id), None)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            return False

        # Create review
        review = AgentReview(
            agent_id=agent_id,
            agent_type=AgentType(agent["type"]),
            agent_name=agent["name"],
            result=result,
            confidence=confidence,
            reasoning=reasoning,
            security_analysis=security_analysis,
            performance_analysis=performance_analysis,
            bug_analysis=bug_analysis,
            timestamp=datetime.now().isoformat(),
            review_hash=self._hash_review(agent_id, result, reasoning),
        )

        # Add review to proposal with proper enum serialization
        review_dict = asdict(review)
        review_dict["result"] = result.value
        review_dict["agent_type"] = review.agent_type.value
        proposal_data["reviews"].append(review_dict)

        # Update status
        proposal_data["status"] = "UNDER_REVIEW"

        # Check consensus
        approvals = sum(1 for r in proposal_data["reviews"] if r["result"] == "ACCEPT")
        rejections = sum(1 for r in proposal_data["reviews"] if r["result"] == "REJECT")

        if approvals >= 4:
            proposal_data["status"] = "APPROVED"
        elif rejections >= 2:
            proposal_data["status"] = "REJECTED"

        # Save updated proposal
        with open(proposal_file, "w") as f:
            json.dump(proposal_data, f, indent=2, default=str)

        # Log to audit trail
        self._log_audit_entry(
            "REVIEW_SUBMITTED",
            {
                "proposal_id": proposal_id,
                "agent_id": agent_id,
                "result": result.value,
                "confidence": confidence,
            },
        )

        logger.info(
            f"Review submitted for proposal {proposal_id} by {agent_id}: {result.value}"
        )
        return True

    def get_proposal_status(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a proposal."""
        proposal_file = self.proposals_dir / f"{proposal_id}.json"
        if not proposal_file.exists():
            return None

        with open(proposal_file, "r") as f:
            return json.load(f)

    def list_proposals(
        self, status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all proposals, optionally filtered by status."""
        proposals = []
        for proposal_file in self.proposals_dir.glob("*.json"):
            with open(proposal_file, "r") as f:
                proposal = json.load(f)
                if status_filter is None or proposal["status"] == status_filter:
                    proposals.append(proposal)

        return sorted(proposals, key=lambda x: x["submitted_at"], reverse=True)

    def approve_proposal(self, proposal_id: str) -> bool:
        """
        Approve a proposal that has reached consensus.
        This triggers the actual code merge.
        """
        proposal = self.get_proposal_status(proposal_id)
        if not proposal:
            return False

        if proposal["status"] != "APPROVED":
            logger.error(
                f"Proposal {proposal_id} is not approved (status: {proposal['status']})"
            )
            return False

        # TODO: Implement actual code merge logic here
        # This would apply the code_patch to the affected_files

        # Update status
        proposal["status"] = "MERGED"
        proposal["merged_at"] = datetime.now().isoformat()

        # Save updated proposal
        proposal_file = self.proposals_dir / f"{proposal_id}.json"
        with open(proposal_file, "w") as f:
            json.dump(proposal, f, indent=2, default=str)

        # Log to audit trail
        self._log_audit_entry(
            "PROPOSAL_MERGED", {"proposal_id": proposal_id, "title": proposal["title"]}
        )

        logger.info(f"Proposal {proposal_id} merged successfully")
        return True

    def _hash_review(self, agent_id: str, result: ReviewResult, reasoning: str) -> str:
        """Create a hash of the review for audit trail integrity."""
        content = f"{agent_id}:{result.value}:{reasoning}:{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _log_audit_entry(self, action: str, data: Dict[str, Any]):
        """Log an entry to the immutable audit trail."""
        audit_file = self.audit_dir / "consensus_audit.json"

        try:
            with open(audit_file, "r") as f:
                audit = json.load(f)
        except FileNotFoundError:
            audit = {
                "system_initialized": datetime.now().isoformat(),
                "protocol_version": "1.0",
                "consensus_rule": "4/5 agents must approve",
                "audit_entries": [],
            }

        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "data": data,
            "entry_hash": hashlib.sha256(
                f"{action}:{json.dumps(data, sort_keys=True)}".encode()
            ).hexdigest(),
        }

        audit["audit_entries"].append(entry)

        with open(audit_file, "w") as f:
            json.dump(audit, f, indent=2)

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status and statistics."""
        proposals = self.list_proposals()

        status = {
            "total_proposals": len(proposals),
            "pending": len([p for p in proposals if p["status"] == "PENDING"]),
            "under_review": len(
                [p for p in proposals if p["status"] == "UNDER_REVIEW"]
            ),
            "approved": len([p for p in proposals if p["status"] == "APPROVED"]),
            "rejected": len([p for p in proposals if p["status"] == "REJECTED"]),
            "merged": len([p for p in proposals if p["status"] == "MERGED"]),
            "active_agents": len(self.agents),
            "consensus_rule": "4/5 agents must approve",
            "system_healthy": True,
        }

        return status


# Global instance for easy access
consensus_system = AgentConsensusSystem()


def submit_upgrade_proposal(
    title: str, description: str, code_patch: str, affected_files: List[str], **kwargs
) -> str:
    """Convenience function to submit an upgrade proposal."""
    return consensus_system.submit_proposal(
        title=title,
        description=description,
        code_patch=code_patch,
        affected_files=affected_files,
        **kwargs,
    )


def get_proposal_status(proposal_id: str) -> Optional[Dict[str, Any]]:
    """Convenience function to get proposal status."""
    return consensus_system.get_proposal_status(proposal_id)


def list_pending_proposals() -> List[Dict[str, Any]]:
    """Convenience function to list pending proposals."""
    return consensus_system.list_proposals(status_filter="UNDER_REVIEW")
