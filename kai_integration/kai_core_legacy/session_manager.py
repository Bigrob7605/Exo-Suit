"""
Session Manager for persistent conversation context
"""

from datetime import datetime
from typing import Dict, Any

class SessionManager:
    """Manages conversation sessions and context."""
    
    def __init__(self):
        self.sessions = {}
    
    def get_session_context(self, session_id: str, agent_id: str) -> Dict[str, Any]:
        """Get session context for an agent."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        
        if agent_id not in self.sessions[session_id]:
            self.sessions[session_id][agent_id] = {
                'messages': [],
                'interaction_count': 0,
                'last_interaction': None
            }
        
        return self.sessions[session_id][agent_id]
    
    def update_session(self, session_id: str, agent_id: str, user_message: str, agent_response: str):
        """Update session with new interaction."""
        context = self.get_session_context(session_id, agent_id)
        
        # Add messages to history
        context['messages'].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        context['messages'].append({
            'role': 'agent',
            'content': agent_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update interaction count
        context['interaction_count'] += 1
        context['last_interaction'] = datetime.now().isoformat()
        
        # Keep only last 10 messages to prevent memory bloat
        if len(context['messages']) > 10:
            context['messages'] = context['messages'][-10:]
    
    def get_session_history(self, session_id: str, agent_id: str) -> list:
        """Get conversation history for a session."""
        context = self.get_session_context(session_id, agent_id)
        return context.get('messages', [])
    
    def clear_session(self, session_id: str, agent_id: str = None):
        """Clear session data."""
        if agent_id:
            if session_id in self.sessions and agent_id in self.sessions[session_id]:
                del self.sessions[session_id][agent_id]
        else:
            if session_id in self.sessions:
                del self.sessions[session_id]
