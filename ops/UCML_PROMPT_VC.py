#!/usr/bin/env python3
"""
🚀 UCML PROMPT VERSION CONTROL SYSTEM v1.0 - "GIT FOR PROMPTS"

UCML Prompt VC provides:
- Prompt-to-glyph conversion engine
- Prompt drift detection and analysis
- Merge conflict resolution for prompts
- Prompt lineage tracking with MythGraph
- Prompt optimization suggestions
- Team collaboration features

This system will revolutionize prompt management with UCML compression!
"""

import asyncio
import json
import hashlib
import time
import struct
import math
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass
import logging
import numpy as np
from pathlib import Path
import difflib
import re
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptStatus(Enum):
    """Prompt version control status"""
    UNTRACKED = "untracked"
    MODIFIED = "modified"
    STAGED = "staged"
    COMMITTED = "committed"
    MERGED = "merged"
    CONFLICT = "conflict"

class PromptType(Enum):
    """Types of prompts"""
    SYSTEM = "system"           # System instructions
    USER = "user"               # User queries
    ASSISTANT = "assistant"     # AI responses
    FUNCTION = "function"       # Function calls
    TOOL = "tool"               # Tool usage
    COMPOSITE = "composite"     # Multi-part prompts

class MergeStrategy(Enum):
    """Merge conflict resolution strategies"""
    AUTO_MERGE = "auto_merge"      # Automatic conflict resolution
    MANUAL_RESOLVE = "manual"       # Manual conflict resolution
    KEEP_THEIRS = "keep_theirs"    # Keep incoming changes
    KEEP_OURS = "keep_ours"        # Keep current changes
    INTERACTIVE = "interactive"     # Interactive resolution

@dataclass
class PromptVersion:
    """Represents a version of a prompt"""
    prompt_id: str
    content: str
    version_hash: str
    parent_hash: Optional[str]
    author: str
    timestamp: datetime
    message: str
    prompt_type: PromptType
    metadata: Dict[str, Any]
    ucml_glyph: Optional[str] = None
    drift_score: float = 0.0

@dataclass
class PromptBranch:
    """Represents a branch of prompt development"""
    branch_name: str
    head_hash: str
    base_hash: str
    created_at: datetime
    author: str
    description: str
    is_main: bool = False

@dataclass
class MergeConflict:
    """Represents a merge conflict between prompt versions"""
    conflict_id: str
    prompt_id: str
    our_version: PromptVersion
    their_version: PromptVersion
    base_version: PromptVersion
    conflict_type: str
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

@dataclass
class DriftAnalysis:
    """Analysis of prompt drift over time"""
    prompt_id: str
    base_version: str
    current_version: str
    drift_score: float
    drift_factors: List[str]
    semantic_changes: List[str]
    structural_changes: List[str]
    recommendations: List[str]

class UCMLPromptVC:
    """UCML-powered Prompt Version Control System"""
    
    def __init__(self):
        self.prompts: Dict[str, PromptVersion] = {}
        self.branches: Dict[str, PromptBranch] = {}
        self.conflicts: Dict[str, MergeConflict] = {}
        self.drift_history: Dict[str, List[DriftAnalysis]] = {}
        self.ucml_engine = None  # Will be connected to UCML Core Engine
        self.mythgraph = None    # Will be connected to MythGraph Integration
        
        # Initialize default branch
        self._initialize_default_branch()
    
    def _initialize_default_branch(self):
        """Initialize the main branch"""
        main_branch = PromptBranch(
            branch_name="main",
            head_hash="",
            base_hash="",
            created_at=datetime.now(timezone.utc),
            author="system",
            description="Main prompt development branch",
            is_main=True
        )
        self.branches["main"] = main_branch
    
    async def connect_ucml_engine(self, ucml_engine):
        """Connect to UCML Core Engine"""
        self.ucml_engine = ucml_engine
        logger.info("Connected to UCML Core Engine")
    
    async def connect_mythgraph(self, mythgraph):
        """Connect to MythGraph Integration"""
        self.mythgraph = mythgraph
        logger.info("Connected to MythGraph Integration")
    
    def _generate_prompt_hash(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate hash for prompt content and metadata"""
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        metadata_str = json.dumps(metadata, sort_keys=True)
        metadata_hash = hashlib.sha256(metadata_str.encode()).hexdigest()
        combined = f"{content_hash}:{metadata_hash}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    async def create_prompt(self, content: str, prompt_type: PromptType, 
                           author: str, message: str = "", 
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new prompt and track it"""
        if metadata is None:
            metadata = {}
        
        prompt_id = str(hash(content + str(time.time())))
        version_hash = self._generate_prompt_hash(content, metadata)
        
        # Create prompt version
        prompt_version = PromptVersion(
            prompt_id=prompt_id,
            content=content,
            version_hash=version_hash,
            parent_hash=None,
            author=author,
            timestamp=datetime.now(timezone.utc),
            message=message,
            prompt_type=prompt_type,
            metadata=metadata
        )
        
        # Generate UCML glyph if engine is available
        if self.ucml_engine:
            try:
                # Convert prompt to UCML glyph
                glyph_data = await self._prompt_to_glyph(content, prompt_type, metadata)
                prompt_version.ucml_glyph = glyph_data["glyph_id"]
                logger.info(f"Generated UCML glyph: {glyph_data['glyph_id']}")
            except Exception as e:
                logger.warning(f"Failed to generate UCML glyph: {e}")
        
        # Store prompt
        self.prompts[prompt_id] = prompt_version
        
        # Update main branch
        if "main" in self.branches:
            self.branches["main"].head_hash = version_hash
        
        # Add to MythGraph if available
        if self.mythgraph:
            try:
                await self._add_prompt_to_mythgraph(prompt_version)
            except Exception as e:
                logger.warning(f"Failed to add to MythGraph: {e}")
        
        logger.info(f"Created prompt {prompt_id} with version {version_hash}")
        return prompt_id
    
    async def _prompt_to_glyph(self, content: str, prompt_type: PromptType, 
                               metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Convert prompt to UCML glyph using Core Engine"""
        if not self.ucml_engine:
            raise RuntimeError("UCML Engine not connected")
        
        # Create glyph data structure
        glyph_data = {
            "type": "prompt",
            "content": content,
            "prompt_type": prompt_type.value,
            "metadata": metadata,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Use UCML Core Engine to create glyph
        # This would integrate with the actual UCML glyph creation system
        glyph_id = f"prompt_{hash(content)}"
        
        return {
            "glyph_id": glyph_id,
            "compression_ratio": len(content) / 3,  # 3-byte TriGlyph
            "glyph_type": "triglyph"
        }
    
    async def _add_prompt_to_mythgraph(self, prompt_version: PromptVersion):
        """Add prompt to MythGraph for lineage tracking"""
        if not self.mythgraph:
            return
        
        # Create MythGraph entry
        entry_data = {
            "type": "prompt_version",
            "prompt_id": prompt_version.prompt_id,
            "version_hash": prompt_version.version_hash,
            "content_hash": hashlib.sha256(prompt_version.content.encode()).hexdigest(),
            "author": prompt_version.author,
            "timestamp": prompt_version.timestamp.isoformat(),
            "ucml_glyph": prompt_version.ucml_glyph
        }
        
        await self.mythgraph.add_glyph_to_mythgraph(entry_data)
    
    async def update_prompt(self, prompt_id: str, new_content: str, 
                           author: str, message: str = "", 
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Update an existing prompt with new version"""
        if prompt_id not in self.prompts:
            raise ValueError(f"Prompt {prompt_id} not found")
        
        old_version = self.prompts[prompt_id]
        if metadata is None:
            metadata = old_version.metadata.copy()
        
        # Generate new version hash
        new_version_hash = self._generate_prompt_hash(new_content, metadata)
        
        # Create new version
        new_version = PromptVersion(
            prompt_id=prompt_id,
            content=new_content,
            version_hash=new_version_hash,
            parent_hash=old_version.version_hash,
            author=author,
            timestamp=datetime.now(timezone.utc),
            message=message,
            prompt_type=old_version.prompt_type,
            metadata=metadata
        )
        
        # Calculate drift score
        drift_score = await self._calculate_drift_score(old_version, new_version)
        new_version.drift_score = drift_score
        
        # Generate UCML glyph
        if self.ucml_engine:
            try:
                glyph_data = await self._prompt_to_glyph(new_content, old_version.prompt_type, metadata)
                new_version.ucml_glyph = glyph_data["glyph_id"]
            except Exception as e:
                logger.warning(f"Failed to generate UCML glyph: {e}")
        
        # Store new version
        self.prompts[prompt_id] = new_version
        
        # Update branch
        if "main" in self.branches:
            self.branches["main"].head_hash = new_version_hash
        
        # Add to MythGraph
        if self.mythgraph:
            try:
                await self._add_prompt_to_mythgraph(new_version)
            except Exception as e:
                logger.warning(f"Failed to add to MythGraph: {e}")
        
        logger.info(f"Updated prompt {prompt_id} to version {new_version_hash}")
        return prompt_id
    
    async def _calculate_drift_score(self, old_version: PromptVersion, 
                                   new_version: PromptVersion) -> float:
        """Calculate drift score between two prompt versions"""
        # Simple similarity-based drift calculation
        # In production, this would use more sophisticated NLP analysis
        
        # Content similarity
        content_similarity = difflib.SequenceMatcher(
            None, old_version.content, new_version.content
        ).ratio()
        
        # Metadata similarity
        metadata_similarity = 1.0
        if old_version.metadata and new_version.metadata:
            old_keys = set(old_version.metadata.keys())
            new_keys = set(new_version.metadata.keys())
            if old_keys or new_keys:
                intersection = len(old_keys.intersection(new_keys))
                union = len(old_keys.union(new_keys))
                metadata_similarity = intersection / union if union > 0 else 1.0
        
        # Calculate drift score (0 = no drift, 1 = complete drift)
        drift_score = 1.0 - (content_similarity * 0.7 + metadata_similarity * 0.3)
        
        return max(0.0, min(1.0, drift_score))
    
    async def create_branch(self, branch_name: str, base_hash: str, 
                           author: str, description: str = "") -> str:
        """Create a new branch from a specific version"""
        if branch_name in self.branches:
            raise ValueError(f"Branch {branch_name} already exists")
        
        # Verify base hash exists
        base_exists = any(p.version_hash == base_hash for p in self.prompts.values())
        if not base_exists:
            raise ValueError(f"Base version {base_hash} not found")
        
        # Create branch
        branch = PromptBranch(
            branch_name=branch_name,
            head_hash=base_hash,
            base_hash=base_hash,
            created_at=datetime.now(timezone.utc),
            author=author,
            description=description
        )
        
        self.branches[branch_name] = branch
        logger.info(f"Created branch {branch_name} from {base_hash}")
        return branch_name
    
    async def merge_branches(self, source_branch: str, target_branch: str, 
                            strategy: MergeStrategy = MergeStrategy.AUTO_MERGE) -> Dict[str, Any]:
        """Merge one branch into another"""
        if source_branch not in self.branches:
            raise ValueError(f"Source branch {source_branch} not found")
        if target_branch not in self.branches:
            raise ValueError(f"Target branch {target_branch} not found")
        
        source = self.branches[source_branch]
        target = self.branches[target_branch]
        
        # Find common ancestor
        common_ancestor = await self._find_common_ancestor(source.head_hash, target.head_hash)
        
        # Check for conflicts
        conflicts = await self._detect_merge_conflicts(source.head_hash, target.head_hash, common_ancestor)
        
        if conflicts and strategy != MergeStrategy.AUTO_MERGE:
            # Create conflict records
            for conflict in conflicts:
                self.conflicts[conflict.conflict_id] = conflict
            
            return {
                "status": "conflict",
                "conflicts": [c.conflict_id for c in conflicts],
                "message": f"Merge conflicts detected. Resolve manually or use auto-merge strategy."
            }
        
        # Perform merge
        if strategy == MergeStrategy.AUTO_MERGE:
            result = await self._auto_merge_branches(source_branch, target_branch, conflicts)
        elif strategy == MergeStrategy.KEEP_THEIRS:
            result = await self._merge_keep_theirs(source_branch, target_branch)
        elif strategy == MergeStrategy.KEEP_OURS:
            result = await self._merge_keep_ours(source_branch, target_branch)
        else:
            raise ValueError(f"Unsupported merge strategy: {strategy}")
        
        logger.info(f"Merged {source_branch} into {target_branch}")
        return result
    
    async def _find_common_ancestor(self, hash1: str, hash2: str) -> Optional[str]:
        """Find common ancestor of two version hashes"""
        # Simple implementation - in production would use proper DAG traversal
        ancestors1 = set()
        ancestors2 = set()
        
        # Build ancestor sets
        current1 = hash1
        current2 = hash2
        
        while current1:
            ancestors1.add(current1)
            current1 = next((p.parent_hash for p in self.prompts.values() if p.version_hash == current1), None)
        
        while current2:
            if current2 in ancestors1:
                return current2
            ancestors2.add(current2)
            current2 = next((p.parent_hash for p in self.prompts.values() if p.version_hash == current2), None)
        
        return None
    
    async def _detect_merge_conflicts(self, hash1: str, hash2: str, 
                                    common_ancestor: Optional[str]) -> List[MergeConflict]:
        """Detect merge conflicts between two versions"""
        conflicts = []
        
        # Get versions
        version1 = next((p for p in self.prompts.values() if p.version_hash == hash1), None)
        version2 = next((p for p in self.prompts.values() if p.version_hash == hash2), None)
        base_version = next((p for p in self.prompts.values() if p.version_hash == common_ancestor), None) if common_ancestor else None
        
        if not version1 or not version2:
            return conflicts
        
        # Check for content conflicts
        if version1.content != version2.content:
            conflict = MergeConflict(
                conflict_id=f"conflict_{hash1}_{hash2}",
                prompt_id=version1.prompt_id,
                our_version=version1,
                their_version=version2,
                base_version=base_version or version1,
                conflict_type="content_conflict"
            )
            conflicts.append(conflict)
        
        # Check for metadata conflicts
        if version1.metadata != version2.metadata:
            conflict = MergeConflict(
                conflict_id=f"conflict_meta_{hash1}_{hash2}",
                prompt_id=version1.prompt_id,
                our_version=version1,
                their_version=version2,
                base_version=base_version or version1,
                conflict_type="metadata_conflict"
            )
            conflicts.append(conflict)
        
        return conflicts
    
    async def _auto_merge_branches(self, source_branch: str, target_branch: str, 
                                  conflicts: List[MergeConflict]) -> Dict[str, Any]:
        """Automatically merge branches, resolving conflicts"""
        source = self.branches[source_branch]
        target = self.branches[target_branch]
        
        # For auto-merge, we'll take the source branch content
        # In production, this would use more sophisticated conflict resolution
        
        # Update target branch head
        target.head_hash = source.head_hash
        
        # Create merge commit
        merge_message = f"Merged {source_branch} into {target_branch}"
        
        return {
            "status": "success",
            "message": merge_message,
            "target_branch": target_branch,
            "new_head": source.head_hash
        }
    
    async def _merge_keep_theirs(self, source_branch: str, target_branch: str) -> Dict[str, Any]:
        """Merge keeping source branch changes"""
        source = self.branches[source_branch]
        target = self.branches[target_branch]
        
        target.head_hash = source.head_hash
        
        return {
            "status": "success",
            "message": f"Kept {source_branch} changes in {target_branch}",
            "target_branch": target_branch,
            "new_head": source.head_hash
        }
    
    async def _merge_keep_ours(self, source_branch: str, target_branch: str) -> Dict[str, Any]:
        """Merge keeping target branch changes"""
        # No changes needed - keep current target branch
        return {
            "status": "success",
            "message": f"Kept {target_branch} changes unchanged",
            "target_branch": target_branch,
            "new_head": self.branches[target_branch].head_hash
        }
    
    async def resolve_conflict(self, conflict_id: str, resolution: str, 
                             resolved_by: str) -> bool:
        """Resolve a merge conflict"""
        if conflict_id not in self.conflicts:
            return False
        
        conflict = self.conflicts[conflict_id]
        conflict.resolution = resolution
        conflict.resolved_by = resolved_by
        conflict.resolved_at = datetime.now(timezone.utc)
        
        # Remove from active conflicts
        del self.conflicts[conflict_id]
        
        logger.info(f"Resolved conflict {conflict_id} by {resolved_by}")
        return True
    
    async def analyze_drift(self, prompt_id: str, base_version: str = None) -> DriftAnalysis:
        """Analyze drift for a specific prompt"""
        if prompt_id not in self.prompts:
            raise ValueError(f"Prompt {prompt_id} not found")
        
        current_version = self.prompts[prompt_id]
        
        if base_version is None:
            # Find earliest version
            base_version = current_version
            while base_version.parent_hash:
                parent = next((p for p in self.prompts.values() if p.version_hash == base_version.parent_hash), None)
                if parent:
                    base_version = parent
                else:
                    break
        
        # Calculate drift
        drift_score = await self._calculate_drift_score(base_version, current_version)
        
        # Analyze changes
        drift_factors = []
        semantic_changes = []
        structural_changes = []
        
        if base_version.content != current_version.content:
            drift_factors.append("content_modification")
            
            # Simple change analysis
            if len(current_version.content) > len(base_version.content):
                structural_changes.append("content_expansion")
            elif len(current_version.content) < len(base_version.content):
                structural_changes.append("content_reduction")
            
            # Check for semantic changes (simplified)
            if "system" in current_version.content.lower() and "system" not in base_version.content.lower():
                semantic_changes.append("system_instruction_addition")
            if "function" in current_version.content.lower() and "function" not in base_version.content.lower():
                semantic_changes.append("function_capability_addition")
        
        if base_version.metadata != current_version.metadata:
            drift_factors.append("metadata_modification")
        
        # Generate recommendations
        recommendations = []
        if drift_score > 0.7:
            recommendations.append("High drift detected - consider reviewing prompt purpose")
        if "content_expansion" in structural_changes:
            recommendations.append("Content expanded significantly - verify prompt efficiency")
        if "system_instruction_addition" in semantic_changes:
            recommendations.append("System instructions added - ensure consistency")
        
        analysis = DriftAnalysis(
            prompt_id=prompt_id,
            base_version=base_version.version_hash,
            current_version=current_version.version_hash,
            drift_score=drift_score,
            drift_factors=drift_factors,
            semantic_changes=semantic_changes,
            structural_changes=structural_changes,
            recommendations=recommendations
        )
        
        # Store in history
        if prompt_id not in self.drift_history:
            self.drift_history[prompt_id] = []
        self.drift_history[prompt_id].append(analysis)
        
        return analysis
    
    async def get_prompt_history(self, prompt_id: str) -> List[PromptVersion]:
        """Get complete history of a prompt"""
        if prompt_id not in self.prompts:
            return []
        
        history = []
        current = self.prompts[prompt_id]
        
        while current:
            history.append(current)
            if current.parent_hash:
                current = next((p for p in self.prompts.values() if p.version_hash == current.parent_hash), None)
            else:
                break
        
        return list(reversed(history))
    
    async def get_branch_status(self) -> Dict[str, Any]:
        """Get status of all branches"""
        status = {}
        for branch_name, branch in self.branches.items():
            status[branch_name] = {
                "head_hash": branch.head_hash,
                "base_hash": branch.base_hash,
                "created_at": branch.created_at.isoformat(),
                "author": branch.author,
                "description": branch.description,
                "is_main": branch.is_main,
                "ahead_count": 0,  # Would calculate in production
                "behind_count": 0   # Would calculate in production
            }
        return status
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        main_branch = self.branches.get("main")
        main_branch_hash = main_branch.head_hash if main_branch else ""
        
        return {
            "total_prompts": len(self.prompts),
            "total_branches": len(self.branches),
            "active_conflicts": len(self.conflicts),
            "drift_analyses": sum(len(analyses) for analyses in self.drift_history.values()),
            "ucml_connected": self.ucml_engine is not None,
            "mythgraph_connected": self.mythgraph is not None,
            "main_branch": main_branch_hash
        }
    
    async def export_data(self) -> Dict[str, Any]:
        """Export all system data"""
        return {
            "prompts": {pid: {
                "content": p.content,
                "version_hash": p.version_hash,
                "parent_hash": p.parent_hash,
                "author": p.author,
                "timestamp": p.timestamp.isoformat(),
                "message": p.message,
                "prompt_type": p.prompt_type.value,
                "metadata": p.metadata,
                "ucml_glyph": p.ucml_glyph,
                "drift_score": p.drift_score
            } for pid, p in self.prompts.items()},
            "branches": {bname: {
                "head_hash": b.head_hash,
                "base_hash": b.base_hash,
                "created_at": b.created_at.isoformat(),
                "author": b.author,
                "description": b.description,
                "is_main": b.is_main
            } for bname, b in self.branches.items()},
            "conflicts": {cid: {
                "prompt_id": c.prompt_id,
                "our_version": c.our_version.version_hash,
                "their_version": c.their_version.version_hash,
                "base_version": c.base_version.version_hash,
                "conflict_type": c.conflict_type,
                "resolution": c.resolution,
                "resolved_by": c.resolved_by,
                "resolved_at": c.resolved_at.isoformat() if c.resolved_at else None
            } for cid, c in self.conflicts.items()},
            "drift_history": {pid: [{
                "base_version": a.base_version,
                "current_version": a.current_version,
                "drift_score": a.drift_score,
                "drift_factors": a.drift_factors,
                "semantic_changes": a.semantic_changes,
                "structural_changes": a.structural_changes,
                "recommendations": a.recommendations
            } for a in analyses] for pid, analyses in self.drift_history.items()}
        }

async def run_prompt_vc_demo():
    """Demonstrate UCML Prompt Version Control System"""
    print("🚀 UCML PROMPT VERSION CONTROL SYSTEM DEMO")
    print("=" * 60)
    
    # Initialize system
    vc_system = UCMLPromptVC()
    
    print("\n📝 Creating initial prompts...")
    
    # Create system prompt
    system_prompt_id = await vc_system.create_prompt(
        content="You are a helpful AI assistant that follows instructions carefully.",
        prompt_type=PromptType.SYSTEM,
        author="developer",
        message="Initial system prompt",
        metadata={"version": "1.0", "category": "system"}
    )
    
    # Create user prompt
    user_prompt_id = await vc_system.create_prompt(
        content="Explain quantum computing in simple terms.",
        prompt_type=PromptType.USER,
        author="user",
        message="Initial user query",
        metadata={"topic": "quantum_computing", "complexity": "beginner"}
    )
    
    print(f"✅ Created system prompt: {system_prompt_id}")
    print(f"✅ Created user prompt: {user_prompt_id}")
    
    print("\n🔄 Updating prompts...")
    
    # Update system prompt
    await vc_system.update_prompt(
        system_prompt_id,
        "You are a helpful AI assistant that follows instructions carefully and provides accurate information.",
        author="developer",
        message="Enhanced system prompt with accuracy requirement",
        metadata={"version": "1.1", "category": "system"}
    )
    
    # Update user prompt
    await vc_system.update_prompt(
        user_prompt_id,
        "Explain quantum computing in simple terms with examples.",
        author="user",
        message="Added request for examples",
        metadata={"topic": "quantum_computing", "complexity": "beginner", "examples": True}
    )
    
    print("✅ Updated both prompts")
    
    print("\n🌿 Creating development branch...")
    
    # Create feature branch
    await vc_system.create_branch(
        "feature/advanced-prompts",
        base_hash=vc_system.prompts[system_prompt_id].version_hash,
        author="developer",
        description="Branch for advanced prompt features"
    )
    
    print("✅ Created feature branch")
    
    print("\n📊 Analyzing prompt drift...")
    
    # Analyze drift
    drift_analysis = await vc_system.analyze_drift(system_prompt_id)
    print(f"   Drift Score: {drift_analysis.drift_score:.2f}")
    print(f"   Drift Factors: {', '.join(drift_analysis.drift_factors)}")
    print(f"   Recommendations: {', '.join(drift_analysis.recommendations)}")
    
    print("\n📋 Getting system status...")
    
    # Get status
    status = await vc_system.get_system_status()
    print(f"   Total Prompts: {status['total_prompts']}")
    print(f"   Total Branches: {status['total_branches']}")
    print(f"   Active Conflicts: {status['active_conflicts']}")
    print(f"   UCML Connected: {status['ucml_connected']}")
    
    print("\n📚 Getting prompt history...")
    
    # Get history
    history = await vc_system.get_prompt_history(system_prompt_id)
    print(f"   System prompt has {len(history)} versions:")
    for i, version in enumerate(history):
        print(f"     v{i+1}: {version.message} (by {version.author})")
    
    print("\n🎯 UCML Prompt Version Control System Demo Complete!")
    print("   Ready for integration with UCML Core Engine and MythGraph!")

if __name__ == "__main__":
    asyncio.run(run_prompt_vc_demo())
