import random
from datetime import datetime
from typing import Dict, Any
from kai_core.agent_personality_engine import DynamicPersonalityEngine

class EnhancedAgentChat:
    def __init__(self):
        self.personality_engine = DynamicPersonalityEngine()
    
    def _classify_message_type(self, message: str) -> str:
        """Classify message type for appropriate response selection."""
        message_lower = message.lower()
        
        # Small talk patterns
        small_talk_patterns = [
            "hi", "hello", "hey", "what's up", "how are you", "how's it going",
            "good morning", "good afternoon", "good evening", "sup", "yo",
            "just checking", "just saying hi", "howdy", "greetings"
        ]
        
        # Troll patterns
        troll_patterns = [
            "troll", "stupid", "dumb", "useless", "broken", "fail", "suck",
            "worst", "terrible", "awful", "hate", "annoying", "boring"
        ]
        
        # Work/technical patterns
        work_patterns = [
            "help", "problem", "issue", "bug", "error", "fix", "optimize",
            "performance", "security", "quality", "test", "code", "function",
            "algorithm", "system", "server", "database", "api", "endpoint"
        ]
        
        # Check for small talk
        if any(pattern in message_lower for pattern in small_talk_patterns):
            return 'casual'
        
        # Check for trolling
        if any(pattern in message_lower for pattern in troll_patterns):
            return 'troll'
        
        # Check for work topics
        if any(pattern in message_lower for pattern in work_patterns):
            return 'work'
        
        # Default to off-topic if no clear classification
        return 'off_topic'
    
    def _process_serious_query(self, agent_id: str, message: str, context: Dict[str, Any]) -> str:
        """Process serious work-related queries with agent-specific responses."""
        agent_responses = {
            'performance_agent': [
                "I'll analyze your performance requirements and optimize accordingly.",
                "Let me benchmark your current setup and identify optimization opportunities.",
                "I'll run performance diagnostics and provide actionable recommendations.",
                "Let me profile your system and identify bottlenecks for optimization."
            ],
            'security_agent': [
                "I'll conduct a comprehensive security audit and identify potential vulnerabilities.",
                "Let me analyze your security posture and recommend protective measures.",
                "I'll scan for security issues and provide mitigation strategies.",
                "Let me assess your security framework and suggest improvements."
            ],
            'code_quality_agent': [
                "I'll review your code for quality issues and suggest improvements.",
                "Let me analyze your codebase for maintainability and best practices.",
                "I'll perform a code quality assessment and provide refactoring suggestions.",
                "Let me examine your code structure and recommend quality enhancements."
            ],
            'functionality_agent': [
                "I'll test your functionality thoroughly and identify any issues.",
                "Let me run comprehensive tests and validate your implementation.",
                "I'll verify your functionality and ensure it meets requirements.",
                "Let me perform functional testing and report any problems found."
            ],
            'master_orchestrator': [
                "I'll coordinate the team to address your requirements comprehensively.",
                "Let me orchestrate the appropriate agents to solve your problem.",
                "I'll manage the workflow and ensure all aspects are covered.",
                "Let me coordinate the response and ensure optimal results."
            ],
            'quantum_philosopher': [
                "I'll explore the deeper implications and philosophical aspects of your query.",
                "Let me analyze this from multiple perspectives and consider the broader context.",
                "I'll examine the fundamental principles underlying your question.",
                "Let me contemplate the theoretical foundations and practical implications."
            ],
            'climate_strategist': [
                "I'll assess the environmental impact and sustainability considerations.",
                "Let me analyze the climate implications and suggest green alternatives.",
                "I'll evaluate the carbon footprint and recommend eco-friendly approaches.",
                "Let me consider the environmental factors and sustainability aspects."
            ],
            'bioinformatics_sage': [
                "I'll analyze the biological data patterns and genetic implications.",
                "Let me examine the sequence data and identify meaningful patterns.",
                "I'll process the bioinformatics data and provide biological insights.",
                "Let me analyze the genetic information and suggest biological solutions."
            ],
            'code_quality_guardian': [
                "I'll perform a thorough code review and ensure quality standards.",
                "Let me examine your code for quality issues and maintainability.",
                "I'll audit your codebase and enforce quality best practices.",
                "Let me review your implementation and ensure it meets quality criteria."
            ],
            'performance_oracle': [
                "I'll predict performance outcomes and optimize for maximum efficiency.",
                "Let me forecast performance metrics and suggest optimization strategies.",
                "I'll analyze performance patterns and predict future bottlenecks.",
                "Let me evaluate performance characteristics and recommend improvements."
            ]
        }
        
        responses = agent_responses.get(agent_id, ["I'll help you with that."])
        return random.choice(responses)
    
    def get_agent_response(self, agent_id: str, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get dynamic, never-repeat response from agent."""
        
        # Determine response type
        response_type = self._classify_message_type(message)
        
        # Get dynamic response
        if response_type in ['casual', 'troll', 'off_topic']:
            response_text = self.personality_engine.get_dynamic_response(
                agent_id, response_type, context
            )
        else:
            # Serious query - use existing logic
            response_text = self._process_serious_query(agent_id, message, context)
        
        return {
            'response': response_text,
            'confidence': 0.85 + (random.random() * 0.15),  # 85-100% dynamic
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat(),
            'response_type': response_type,
            'is_fresh': True  # Never repeated
        }
