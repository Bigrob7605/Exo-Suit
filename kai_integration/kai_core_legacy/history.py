#!/usr/bin/env python3
"""
Kai Core Change History
Tracks all changes and challenges for immutable audit trail
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class ChangeHistory:
    """
    Tracks all Kai Core changes and challenges for immutable audit trail
    """

    def __init__(self, history_file: str):
        self.history_file = history_file
        self.history = self._load_history()

    def _load_history(self) -> Dict[str, Any]:
        """Load existing history from file"""
        try:
            with open(self.history_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Create new history structure
            return {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "changes": [],
                "challenges": [],
                "cycles": [],
                "metrics": {
                    "total_changes": 0,
                    "successful_tests": 0,
                    "failed_tests": 0,
                    "total_challenges": 0,
                    "cycles_completed": 0,
                },
            }

    def _save_history(self):
        """Save history to file"""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def log_change(self, change_entry: Dict[str, Any]):
        """Log a change to the history"""
        # Add timestamp if not present
        if "timestamp" not in change_entry:
            change_entry["timestamp"] = datetime.now().isoformat()

        # Add to changes list
        self.history["changes"].append(change_entry)

        # Update metrics
        self.history["metrics"]["total_changes"] += 1
        if change_entry.get("test_passed", False):
            self.history["metrics"]["successful_tests"] += 1
        else:
            self.history["metrics"]["failed_tests"] += 1

        # Save to file
        self._save_history()

    def log_challenge(self, challenge_entry: Dict[str, Any]):
        """Log a challenge to the history"""
        # Add timestamp if not present
        if "timestamp" not in challenge_entry:
            challenge_entry["timestamp"] = datetime.now().isoformat()

        # Add to challenges list
        self.history["challenges"].append(challenge_entry)

        # Update metrics
        self.history["metrics"]["total_challenges"] += 1

        # Save to file
        self._save_history()

    def log_cycle(self, cycle_entry: Dict[str, Any]):
        """Log a complete cycle to the history"""
        # Add timestamp if not present
        if "timestamp" not in cycle_entry:
            cycle_entry["timestamp"] = datetime.now().isoformat()

        # Add to cycles list
        self.history["cycles"].append(cycle_entry)

        # Update metrics
        self.history["metrics"]["cycles_completed"] += 1

        # Save to file
        self._save_history()

    def get_last_cycle_time(self) -> Optional[str]:
        """Get timestamp of last cycle"""
        if self.history["cycles"]:
            return self.history["cycles"][-1]["timestamp"]
        return None

    def get_total_changes(self) -> int:
        """Get total number of changes"""
        return self.history["metrics"]["total_changes"]

    def get_successful_tests(self) -> int:
        """Get number of successful tests"""
        return self.history["metrics"]["successful_tests"]

    def get_failed_tests(self) -> int:
        """Get number of failed tests"""
        return self.history["metrics"]["failed_tests"]

    def get_pending_reviews(self) -> int:
        """Get number of pending reviews"""
        pending = 0
        for change in self.history["changes"]:
            if change.get("status") == "pending_review":
                pending += 1
        return pending

    def get_changes(self) -> List[Dict[str, Any]]:
        """Get all changes"""
        return self.history["changes"]

    def add_change(self, change_record: Dict[str, Any]):
        """Add a change record to history"""
        self.log_change(change_record)

    def get_changes_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get all changes for a specific domain"""
        domain_changes = []
        for change in self.history["changes"]:
            gap = change.get("gap_addressed", {})
            if gap.get("domain") == domain:
                domain_changes.append(change)
        return domain_changes

    def get_challenges_by_type(self, challenge_type: str) -> List[Dict[str, Any]]:
        """Get all challenges of a specific type"""
        type_challenges = []
        for challenge in self.history["challenges"]:
            if challenge.get("challenge_type") == challenge_type:
                type_challenges.append(challenge)
        return type_challenges

    def get_recent_changes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent changes"""
        return self.history["changes"][-limit:]

    def get_recent_challenges(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent challenges"""
        return self.history["challenges"][-limit:]

    def get_cycle_summary(self) -> Dict[str, Any]:
        """Get summary of all cycles"""
        if not self.history["cycles"]:
            return {"status": "no_cycles"}

        total_gaps_addressed = 0
        successful_changes = 0
        failed_changes = 0

        for cycle in self.history["cycles"]:
            results = cycle.get("results", [])
            total_gaps_addressed += len(results)

            for result in results:
                if result.get("test_passed", False):
                    successful_changes += 1
                else:
                    failed_changes += 1

        return {
            "total_cycles": len(self.history["cycles"]),
            "total_gaps_addressed": total_gaps_addressed,
            "successful_changes": successful_changes,
            "failed_changes": failed_changes,
            "success_rate": successful_changes / max(total_gaps_addressed, 1),
        }

    def export_audit_report(self, output_path: str = None) -> str:
        """Export comprehensive audit report"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                os.path.dirname(self.history_file), f"kai_core_audit_{timestamp}.json"
            )

        audit_report = {
            "audit_timestamp": datetime.now().isoformat(),
            "history_summary": {
                "total_changes": self.get_total_changes(),
                "successful_tests": self.get_successful_tests(),
                "failed_tests": self.get_failed_tests(),
                "total_challenges": self.history["metrics"]["total_challenges"],
                "cycles_completed": self.history["metrics"]["cycles_completed"],
            },
            "recent_changes": self.get_recent_changes(20),
            "recent_challenges": self.get_recent_challenges(20),
            "cycle_summary": self.get_cycle_summary(),
            "domain_breakdown": self._get_domain_breakdown(),
            "challenge_breakdown": self._get_challenge_breakdown(),
        }

        with open(output_path, "w") as f:
            json.dump(audit_report, f, indent=2)

        return output_path

    def _get_domain_breakdown(self) -> Dict[str, Any]:
        """Get breakdown of changes by domain"""
        domain_stats = {}

        for change in self.history["changes"]:
            gap = change.get("gap_addressed", {})
            domain = gap.get("domain", "unknown")

            if domain not in domain_stats:
                domain_stats[domain] = {
                    "total_changes": 0,
                    "successful_tests": 0,
                    "failed_tests": 0,
                }

            domain_stats[domain]["total_changes"] += 1
            if change.get("test_passed", False):
                domain_stats[domain]["successful_tests"] += 1
            else:
                domain_stats[domain]["failed_tests"] += 1

        return domain_stats

    def _get_challenge_breakdown(self) -> Dict[str, Any]:
        """Get breakdown of challenges by type"""
        challenge_stats = {}

        for challenge in self.history["challenges"]:
            challenge_type = challenge.get("challenge_type", "unknown")

            if challenge_type not in challenge_stats:
                challenge_stats[challenge_type] = {
                    "total_challenges": 0,
                    "expected_failures": 0,
                    "unexpected_failures": 0,
                }

            challenge_stats[challenge_type]["total_challenges"] += 1

            # This would need to be updated based on actual challenge results
            # For now, we'll just count them
            challenge_stats[challenge_type]["expected_failures"] += 1

        return challenge_stats

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        total_changes = self.get_total_changes()
        successful_tests = self.get_successful_tests()
        failed_tests = self.get_failed_tests()

        if total_changes == 0:
            success_rate = 0.0
        else:
            success_rate = successful_tests / total_changes

        return {
            "status": "healthy" if success_rate > 0.8 else "needs_attention",
            "success_rate": success_rate,
            "total_changes": total_changes,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "total_challenges": self.history["metrics"]["total_challenges"],
            "cycles_completed": self.history["metrics"]["cycles_completed"],
            "last_cycle": self.get_last_cycle_time(),
            "pending_reviews": self.get_pending_reviews(),
        }
