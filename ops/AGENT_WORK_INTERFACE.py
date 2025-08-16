#!/usr/bin/env python3
"""
AGENT WORK INTERFACE
Simple interface for agents to pick work chunks and mark progress
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class AgentWorkInterface:
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.consolidation_dir = self.workspace_root / "consolidated_work"
        self.task_list_path = self.consolidation_dir / "MASTER_TASK_LIST.json"
        self.progress_path = self.consolidation_dir / "PROGRESS_TRACKER.json"
        
        # Load current data
        self.load_data()
    
    def load_data(self):
        """Load task list and progress data"""
        try:
            with open(self.task_list_path, 'r', encoding='utf-8') as f:
                self.task_list = json.load(f)
        except FileNotFoundError:
            print("No task list found. Run LOG_CONSOLIDATION_CHUNKER.py first.")
            self.task_list = {}
        
        try:
            with open(self.progress_path, 'r', encoding='utf-8') as f:
                self.progress = json.load(f)
        except FileNotFoundError:
            self.progress = {
                'created': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'completed_chunks': [],
                'in_progress_chunks': [],
                'blocked_chunks': [],
                'failed_chunks': [],
                'completion_stats': {
                    'total_completed': 0,
                    'total_in_progress': 0,
                    'total_blocked': 0,
                    'total_failed': 0
                }
            }
    
    def show_available_chunks(self, agent_size: str = None):
        """Show available work chunks, optionally filtered by agent size"""
        if not self.task_list:
            print("No work chunks available.")
            return
        
        print(f"=== AVAILABLE WORK CHUNKS ===")
        print(f"Total chunks: {self.task_list.get('total_chunks', 0)}")
        print(f"Priority distribution: {self.task_list.get('priority_distribution', {})}")
        print()
        
        if agent_size:
            if agent_size in self.task_list.get('work_chunks', {}):
                chunks = self.task_list['work_chunks'][agent_size]
                print(f"Chunks for {agent_size} agents ({len(chunks)} available):")
                for i, chunk in enumerate(chunks, 1):
                    status = self.get_chunk_status(chunk['id'])
                    print(f"{i}. [{status.upper()}] {chunk['title']}")
                    print(f"   Priority: {chunk['priority']}, Time: {chunk['estimated_time']}")
                    print(f"   Tokens: {chunk.get('estimated_tokens', 'Unknown')}")
                    print(f"   Description: {chunk['description'][:100]}...")
                    print()
            else:
                print(f"No chunks available for {agent_size} agents.")
        else:
            # Show all chunks by size
            for size, chunks in self.task_list.get('work_chunks', {}).items():
                print(f"{size.upper()} agents ({len(chunks)} chunks):")
                for i, chunk in enumerate(chunks, 1):
                    status = self.get_chunk_status(chunk['id'])
                    print(f"  {i}. [{status.upper()}] {chunk['title']}")
                print()
    
    def get_chunk_status(self, chunk_id: str) -> str:
        """Get current status of a work chunk"""
        if chunk_id in self.progress['completed_chunks']:
            return 'completed'
        elif chunk_id in self.progress['in_progress_chunks']:
            return 'in_progress'
        elif chunk_id in self.progress['blocked_chunks']:
            return 'blocked'
        elif chunk_id in self.progress['failed_chunks']:
            return 'failed'
        else:
            return 'pending'
    
    def pick_work_chunk(self, agent_size: str, chunk_index: int = None):
        """Pick a work chunk for the agent to work on"""
        if agent_size not in self.task_list.get('work_chunks', {}):
            print(f"No work chunks available for {agent_size} agents.")
            return None
        
        chunks = self.task_list['work_chunks'][agent_size]
        available_chunks = [c for c in chunks if self.get_chunk_status(c['id']) == 'pending']
        
        if not available_chunks:
            print(f"No pending chunks available for {agent_size} agents.")
            return None
        
        if chunk_index is None:
            # Show available chunks and let agent pick
            print(f"Available pending chunks for {agent_size} agents:")
            for i, chunk in enumerate(available_chunks, 1):
                print(f"{i}. {chunk['title']} (Priority: {chunk['priority']})")
            
            try:
                choice = int(input(f"Pick a chunk (1-{len(available_chunks)}): "))
                if 1 <= choice <= len(available_chunks):
                    selected_chunk = available_chunks[choice - 1]
                else:
                    print("Invalid choice.")
                    return None
            except ValueError:
                print("Invalid input.")
                return None
        else:
            if 1 <= chunk_index <= len(available_chunks):
                selected_chunk = available_chunks[chunk_index - 1]
            else:
                print(f"Invalid chunk index. Available: 1-{len(available_chunks)}")
                return None
        
        # Mark chunk as in progress
        self.mark_chunk_status(selected_chunk['id'], 'in_progress')
        
        print(f"\n=== SELECTED WORK CHUNK ===")
        print(f"Title: {selected_chunk['title']}")
        print(f"ID: {selected_chunk['id']}")
        print(f"Type: {selected_chunk['type']}")
        print(f"Priority: {selected_chunk['priority']}")
        print(f"Estimated Time: {selected_chunk['estimated_time']}")
        print(f"Estimated Tokens: {selected_chunk.get('estimated_tokens', 'Unknown')}")
        print(f"Description: {selected_chunk['description']}")
        print(f"Status: in_progress")
        
        return selected_chunk
    
    def mark_chunk_status(self, chunk_id: str, status: str):
        """Mark a work chunk with a new status"""
        # Remove from all status lists first
        for status_list in ['completed_chunks', 'in_progress_chunks', 'blocked_chunks', 'failed_chunks']:
            if chunk_id in self.progress[status_list]:
                self.progress[status_list].remove(chunk_id)
        
        # Add to appropriate status list
        if status == 'completed':
            self.progress['completed_chunks'].append(chunk_id)
        elif status == 'in_progress':
            self.progress['in_progress_chunks'].append(chunk_id)
        elif status == 'blocked':
            self.progress['blocked_chunks'].append(chunk_id)
        elif status == 'failed':
            self.progress['failed_chunks'].append(chunk_id)
        
        # Update completion stats
        self.progress['completion_stats'] = {
            'total_completed': len(self.progress['completed_chunks']),
            'total_in_progress': len(self.progress['in_progress_chunks']),
            'total_blocked': len(self.progress['blocked_chunks']),
            'total_failed': len(self.progress['failed_chunks'])
        }
        
        self.progress['last_updated'] = datetime.now().isoformat()
        
        # Save progress
        self.save_progress()
        
        print(f"Chunk {chunk_id} marked as {status}")
    
    def complete_chunk(self, chunk_id: str, completion_notes: str = ""):
        """Mark a chunk as completed with optional notes"""
        self.mark_chunk_status(chunk_id, 'completed')
        
        # Add completion notes if provided
        if completion_notes:
            if 'completion_notes' not in self.progress:
                self.progress['completion_notes'] = {}
            self.progress['completion_notes'][chunk_id] = {
                'completed_at': datetime.now().isoformat(),
                'notes': completion_notes
            }
            self.save_progress()
        
        print(f"Chunk {chunk_id} marked as completed!")
        self.show_progress_summary()
    
    def show_progress_summary(self):
        """Show current progress summary"""
        print(f"\n=== PROGRESS SUMMARY ===")
        stats = self.progress['completion_stats']
        total_chunks = sum(stats.values())
        
        if total_chunks > 0:
            completion_rate = (stats['total_completed'] / total_chunks) * 100
            print(f"Completion Rate: {completion_rate:.1f}%")
        else:
            completion_rate = 0
        
        print(f"Completed: {stats['total_completed']}")
        print(f"In Progress: {stats['total_in_progress']}")
        print(f"Blocked: {stats['total_blocked']}")
        print(f"Failed: {stats['total_failed']}")
        print(f"Total Active: {total_chunks}")
        
        if stats['total_completed'] > 0:
            print(f"\nRecently completed chunks:")
            for chunk_id in self.progress['completed_chunks'][-5:]:  # Last 5
                print(f"  - {chunk_id}")
    
    def save_progress(self):
        """Save progress data to file"""
        with open(self.progress_path, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)
    
    def get_agent_size_from_tokens(self, token_limit: int) -> str:
        """Determine agent size based on token limit"""
        if token_limit <= 1000:
            return 'small'
        elif token_limit <= 5000:
            return 'medium'
        elif token_limit <= 15000:
            return 'large'
        elif token_limit <= 50000:
            return 'xlarge'
        else:
            return 'unlimited'

def main():
    """Main interface for agents"""
    interface = AgentWorkInterface()
    
    print("=== AGENT WORK INTERFACE ===")
    print("Welcome to the Exo-Suit V5.0 Project Healing System!")
    print()
    
    # Get agent token limit
    try:
        token_limit = int(input("Enter your token limit (e.g., 1000, 5000, 15000): "))
        agent_size = interface.get_agent_size_from_tokens(token_limit)
        print(f"Agent size determined: {agent_size}")
    except ValueError:
        print("Invalid token limit. Using 'medium' size.")
        agent_size = 'medium'
    
    print()
    
    while True:
        print("\n=== MAIN MENU ===")
        print("1. Show available work chunks")
        print("2. Pick a work chunk")
        print("3. Mark chunk as completed")
        print("4. Show progress summary")
        print("5. Exit")
        
        try:
            choice = input("\nChoose an option (1-5): ")
            
            if choice == '1':
                interface.show_available_chunks(agent_size)
            
            elif choice == '2':
                chunk = interface.pick_work_chunk(agent_size)
                if chunk:
                    print(f"\nYou can now work on: {chunk['title']}")
            
            elif choice == '3':
                if interface.progress['in_progress_chunks']:
                    print("Chunks currently in progress:")
                    for i, chunk_id in enumerate(interface.progress['in_progress_chunks'], 1):
                        print(f"{i}. {chunk_id}")
                    
                    try:
                        chunk_choice = int(input("Which chunk did you complete? (enter number): "))
                        if 1 <= chunk_choice <= len(interface.progress['in_progress_chunks']):
                            chunk_id = interface.progress['in_progress_chunks'][chunk_choice - 1]
                            notes = input("Add completion notes (optional): ")
                            interface.complete_chunk(chunk_id, notes)
                        else:
                            print("Invalid choice.")
                    except ValueError:
                        print("Invalid input.")
                else:
                    print("No chunks currently in progress.")
            
            elif choice == '4':
                interface.show_progress_summary()
            
            elif choice == '5':
                print("Thank you for helping heal the Exo-Suit project!")
                break
            
            else:
                print("Invalid choice. Please enter 1-5.")
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
