#!/usr/bin/env python3
"""
Kai Core V8+ MythGraph Ledger
Transparency and audit trail system
"""

import asyncio
import hashlib
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class MythGraphEntry:
    """
    Individual entry in the MythGraph ledger
    """
    
    def __init__(self, entry_type: str, data: Dict, timestamp: Optional[str] = None):
        self.entry_type = entry_type
        self.data = data
        self.timestamp = timestamp or datetime.utcnow().isoformat()
        self.hash = None
        self.signature = None
        self.previous_hash = None
    
    def calculate_hash(self, previous_hash: Optional[str] = None) -> str:
        """Calculate cryptographic hash of entry"""
        self.previous_hash = previous_hash
        
        # Create hashable data
        hash_data = {
            "entry_type": self.entry_type,
            "data": self.data,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash
        }
        
        # Calculate SHA-256 hash
        hash_string = json.dumps(hash_data, sort_keys=True)
        self.hash = hashlib.sha256(hash_string.encode()).hexdigest()
        
        return self.hash
    
    def sign_entry(self, private_key: str) -> str:
        """Sign entry with private key"""
        if not self.hash:
            self.calculate_hash()
        
        # In a real implementation, use proper cryptographic signing
        # This is a simplified version for demonstration
        signature_data = f"{self.hash}:{private_key}"
        self.signature = hashlib.sha256(signature_data.encode()).hexdigest()
        
        return self.signature
    
    def verify_signature(self, public_key: str) -> bool:
        """Verify entry signature"""
        if not self.signature:
            return False
        
        # In a real implementation, use proper cryptographic verification
        # This is a simplified version for demonstration
        expected_signature = hashlib.sha256(f"{self.hash}:{public_key}".encode()).hexdigest()
        return self.signature == expected_signature
    
    def to_dict(self) -> Dict:
        """Convert entry to dictionary"""
        return {
            "entry_type": self.entry_type,
            "data": self.data,
            "timestamp": self.timestamp,
            "hash": self.hash,
            "signature": self.signature,
            "previous_hash": self.previous_hash
        }

class MythGraphLedger:
    """
    MythGraph ledger implementation
    """
    
    def __init__(self, public_key: str, private_key: str):
        self.entries: List[MythGraphEntry] = []
        self.public_key = public_key
        self.private_key = private_key
        self.ledger_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        self.storage_path = Path("mythgraph")
        self.storage_path.mkdir(exist_ok=True)
    
    def initialize(self):
        """Initialize the MythGraph ledger system"""
        try:
            # Create storage directory if it doesn't exist
            self.storage_path.mkdir(exist_ok=True)
            
            # Initialize with a genesis entry
            genesis_entry = MythGraphEntry("system_initialization", {
                "message": "MythGraph Ledger initialized",
                "timestamp": "2025-01-17T00:00:00Z"
            })
            
            # Add to entries list
            self.entries.append(genesis_entry)
            
            # Update ledger hash
            self.update_ledger_hash()
            
            return True
        except Exception as e:
            print(f"MythGraph initialization failed: {e}")
            return False
    
    def log_event(self, event_type: str, message: str) -> str:
        """
        Log an event to the MythGraph ledger
        
        Args:
            event_type: Type of event (e.g., 'repair_strategy_creation', 'paradox_detected')
            message: Event message
        
        Returns:
            Entry hash of the logged event
        """
        try:
            # Create event entry
            event_entry = MythGraphEntry(event_type, {
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Add to entries list
            self.entries.append(event_entry)
            
            # Update ledger hash
            self.update_ledger_hash()
            
            return event_entry.hash if event_entry.hash else "event_logged"
            
        except Exception as e:
            print(f"Event logging failed: {e}")
            return "logging_failed"
    
    async def add_entry(self, entry_type: str, data: Dict) -> str:
        """
        Add entry to ledger
        
        Args:
            entry_type: Type of entry (incident, paradox, guard_rail, etc.)
            data: Entry data
        
        Returns:
            Entry hash
        """
        # Create new entry
        entry = MythGraphEntry(entry_type, data)
        
        # Calculate hash with previous entry hash
        previous_hash = self.ledger_hash if self.entries else None
        entry_hash = entry.calculate_hash(previous_hash)
        
        # Sign entry
        entry.sign_entry(self.private_key)
        
        # Add to ledger
        self.entries.append(entry)
        
        # Update ledger hash
        self.update_ledger_hash()
        
        # Persist to storage
        await self.persist_entry(entry)
        
        # Log to console for transparency
        print(f"MYTHGRAPH: {entry_hash} - {entry_type} - {data.get('reason', 'Unknown')}")
        
        return entry_hash
    
    def update_ledger_hash(self):
        """Update the ledger hash with all entries"""
        ledger_data = json.dumps([entry.to_dict() for entry in self.entries], sort_keys=True)
        self.ledger_hash = hashlib.sha256(ledger_data.encode()).hexdigest()
    
    async def persist_entry(self, entry: MythGraphEntry):
        """Persist entry to storage"""
        try:
            # Save individual entry
            entry_file = self.storage_path / f"{entry.hash}.json"
            with open(entry_file, 'w') as f:
                json.dump(entry.to_dict(), f, indent=2)
            
            # Update ledger index
            await self.update_ledger_index()
            
        except Exception as e:
            print(f"Failed to persist entry: {e}")
    
    async def update_ledger_index(self):
        """Update ledger index file"""
        try:
            index_data = {
                "ledger_hash": self.ledger_hash,
                "entry_count": len(self.entries),
                "last_updated": datetime.utcnow().isoformat(),
                "entries": [
                    {
                        "hash": entry.hash,
                        "type": entry.entry_type,
                        "timestamp": entry.timestamp
                    }
                    for entry in self.entries
                ]
            }
            
            index_file = self.storage_path / "ledger_index.json"
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to update ledger index: {e}")
    
    def verify_entry(self, entry_hash: str) -> bool:
        """Verify entry hash is in ledger"""
        for entry in self.entries:
            if entry.hash == entry_hash:
                return entry.verify_signature(self.public_key)
        return False
    
    def get_entry_by_hash(self, entry_hash: str) -> Optional[MythGraphEntry]:
        """Get entry by hash"""
        for entry in self.entries:
            if entry.hash == entry_hash:
                return entry
        return None
    
    def get_recent_entries(self, limit: int = 10) -> List[MythGraphEntry]:
        """Get recent entries"""
        return self.entries[-limit:] if self.entries else []
    
    def get_entries_by_type(self, entry_type: str) -> List[MythGraphEntry]:
        """Get entries by type"""
        return [entry for entry in self.entries if entry.entry_type == entry_type]
    
    def get_statistics(self) -> Dict:
        """Get ledger statistics"""
        total_entries = len(self.entries)
        entry_types = {}
        
        for entry in self.entries:
            entry_type = entry.entry_type
            entry_types[entry_type] = entry_types.get(entry_type, 0) + 1
        
        return {
            "total_entries": total_entries,
            "entry_types": entry_types,
            "ledger_hash": self.ledger_hash,
            "last_updated": datetime.utcnow().isoformat(),
            "verification_enabled": True
        }
    
    def export_ledger(self, format: str = "json") -> str:
        """Export ledger in specified format"""
        if format == "json":
            return json.dumps({
                "ledger_hash": self.ledger_hash,
                "entry_count": len(self.entries),
                "entries": [entry.to_dict() for entry in self.entries]
            }, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def load_from_storage(self):
        """Load entries from storage"""
        try:
            index_file = self.storage_path / "ledger_index.json"
            if index_file.exists():
                with open(index_file, 'r') as f:
                    index_data = json.load(f)
                
                # Load individual entries
                for entry_info in index_data.get("entries", []):
                    entry_file = self.storage_path / f"{entry_info['hash']}.json"
                    if entry_file.exists():
                        with open(entry_file, 'r') as f:
                            entry_data = json.load(f)
                        
                        entry = MythGraphEntry(
                            entry_data["entry_type"],
                            entry_data["data"],
                            entry_data["timestamp"]
                        )
                        entry.hash = entry_data["hash"]
                        entry.signature = entry_data["signature"]
                        entry.previous_hash = entry_data["previous_hash"]
                        
                        self.entries.append(entry)
                
                # Update ledger hash
                self.update_ledger_hash()
                
        except Exception as e:
            print(f"Failed to load from storage: {e}")
    
    async def verify_ledger_integrity(self) -> Dict:
        """Verify ledger integrity"""
        verification_results = {
            "total_entries": len(self.entries),
            "verified_entries": 0,
            "failed_verifications": 0,
            "errors": []
        }
        
        for entry in self.entries:
            try:
                if entry.verify_signature(self.public_key):
                    verification_results["verified_entries"] += 1
                else:
                    verification_results["failed_verifications"] += 1
                    verification_results["errors"].append(f"Invalid signature for entry {entry.hash}")
            except Exception as e:
                verification_results["failed_verifications"] += 1
                verification_results["errors"].append(f"Verification error for entry {entry.hash}: {e}")
        
        verification_results["integrity_score"] = (
            verification_results["verified_entries"] / verification_results["total_entries"]
            if verification_results["total_entries"] > 0 else 0.0
        )
        
        return verification_results

# Example usage
async def test_mythgraph_ledger():
    """Test the MythGraph ledger"""
    ledger = MythGraphLedger("kai_core_v8_public_key", "kai_core_v8_private_key")
    
    # Add some test entries
    test_entries = [
        {
            "type": "system_event",
            "data": {
                "event": "engine_startup",
                "version": "8.0.0",
                "timestamp": datetime.utcnow().isoformat()
            }
        },
        {
            "type": "incident",
            "data": {
                "incident_type": "guard_rail_block",
                "reason": "Harmful content detected",
                "risk_level": "banned"
            }
        },
        {
            "type": "paradox_resolution",
            "data": {
                "paradox_text": "This statement is false",
                "resolution_method": "containment",
                "confidence": 0.95
            }
        }
    ]
    
    for entry_info in test_entries:
        hash_value = await ledger.add_entry(entry_info["type"], entry_info["data"])
        print(f"Added entry: {entry_info['type']} -> {hash_value}")
    
    # Get statistics
    stats = ledger.get_statistics()
    print(f"Ledger statistics: {stats}")
    
    # Verify integrity
    integrity = await ledger.verify_ledger_integrity()
    print(f"Integrity check: {integrity}")
    
    # Export ledger
    exported = ledger.export_ledger("json")
    print(f"Exported ledger length: {len(exported)} characters")

if __name__ == "__main__":
    asyncio.run(test_mythgraph_ledger()) 