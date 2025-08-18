#!/usr/bin/env python3
"""
Kai Core V8+ Guard-Rail Safety System
Multi-layer safety framework for request validation
"""

import asyncio
import re
from typing import Dict, List, Optional, Any
from enum import Enum
from abc import ABC, abstractmethod

class RiskLevel(Enum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    BANNED = "banned"

class PolicyLayer(Enum):
    CONTENT = "content"
    INTENT = "intent"
    CONTEXT = "context"
    RECURSIVE = "recursive"

class GuardRailPolicy(ABC):
    """
    Abstract base class for guard-rail policies
    """
    
    def __init__(self, layer: PolicyLayer):
        self.layer = layer
        self.enabled = True
        self.priority = 1
    
    @abstractmethod
    async def evaluate(self, request_data: Dict) -> Dict:
        """Evaluate request and return risk assessment"""
        pass
    
    @abstractmethod
    def get_mitigation_strategy(self, risk_level: RiskLevel) -> str:
        """Get mitigation strategy for risk level"""
        pass

class ContentFilterPolicy(GuardRailPolicy):
    """
    Content-based filtering policy
    """
    
    def __init__(self):
        super().__init__(PolicyLayer.CONTENT)
        self.blocked_patterns = [
            r"hack\s+into",
            r"malicious\s+code",
            r"exploit\s+vulnerability",
            r"bypass\s+security",
            r"unauthorized\s+access",
            r"steal\s+password",
            r"crack\s+encryption",
            r"delete\s+system",
            r"format\s+drive",
            r"corrupt\s+data"
        ]
        self.warning_patterns = [
            r"security\s+test",
            r"penetration\s+test",
            r"vulnerability\s+assessment",
            r"ethical\s+hacking",
            r"security\s+research"
        ]
    
    async def evaluate(self, request_data: Dict) -> Dict:
        """Evaluate content for safety risks"""
        content = request_data.get("content", "").lower()
        
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, content):
                return {
                    "risk": RiskLevel.BANNED,
                    "reason": f"Blocked pattern detected: {pattern}",
                    "confidence": 0.95
                }
        
        # Check for warning patterns
        for pattern in self.warning_patterns:
            if re.search(pattern, content):
                return {
                    "risk": RiskLevel.MODERATE,
                    "reason": f"Warning pattern detected: {pattern}",
                    "confidence": 0.75
                }
        
        return {
            "risk": RiskLevel.NONE,
            "reason": "No safety concerns detected",
            "confidence": 0.90
        }
    
    def get_mitigation_strategy(self, risk_level: RiskLevel) -> str:
        """Get mitigation strategy"""
        strategies = {
            RiskLevel.BANNED: "Request blocked immediately",
            RiskLevel.HIGH: "Request blocked with explanation",
            RiskLevel.MODERATE: "Request allowed with warning",
            RiskLevel.LOW: "Request allowed with monitoring",
            RiskLevel.NONE: "Request allowed"
        }
        return strategies.get(risk_level, "Unknown risk level")

class IntentAnalysisPolicy(GuardRailPolicy):
    """
    Intent-based analysis policy
    """
    
    def __init__(self):
        super().__init__(PolicyLayer.INTENT)
        self.harmful_intents = [
            "harm", "damage", "destroy", "corrupt", "steal",
            "unauthorized", "illegal", "malicious", "exploit"
        ]
        self.suspicious_intents = [
            "test", "experiment", "research", "investigate",
            "explore", "analyze", "examine"
        ]
    
    async def evaluate(self, request_data: Dict) -> Dict:
        """Analyze request intent"""
        content = request_data.get("content", "").lower()
        context = request_data.get("context", {})
        
        # Check for harmful intent
        for intent in self.harmful_intents:
            if intent in content:
                return {
                    "risk": RiskLevel.HIGH,
                    "reason": f"Harmful intent detected: {intent}",
                    "confidence": 0.85
                }
        
        # Check for suspicious intent
        for intent in self.suspicious_intents:
            if intent in content:
                return {
                    "risk": RiskLevel.LOW,
                    "reason": f"Suspicious intent detected: {intent}",
                    "confidence": 0.70
                }
        
        return {
            "risk": RiskLevel.NONE,
            "reason": "No harmful intent detected",
            "confidence": 0.80
        }
    
    def get_mitigation_strategy(self, risk_level: RiskLevel) -> str:
        """Get mitigation strategy"""
        strategies = {
            RiskLevel.BANNED: "Request blocked immediately",
            RiskLevel.HIGH: "Request blocked with explanation",
            RiskLevel.MODERATE: "Request allowed with warning",
            RiskLevel.LOW: "Request allowed with monitoring",
            RiskLevel.NONE: "Request allowed"
        }
        return strategies.get(risk_level, "Unknown risk level")

class ContextValidationPolicy(GuardRailPolicy):
    """
    Context-based validation policy
    """
    
    def __init__(self):
        super().__init__(PolicyLayer.CONTEXT)
        self.suspicious_contexts = [
            "admin", "root", "system", "privileged",
            "sensitive", "confidential", "secret"
        ]
    
    async def evaluate(self, request_data: Dict) -> Dict:
        """Validate request context"""
        context = request_data.get("context", {})
        user_id = request_data.get("user_id", "")
        
        # Check for suspicious user context
        if any(suspicious in user_id.lower() for suspicious in self.suspicious_contexts):
            return {
                "risk": RiskLevel.MODERATE,
                "reason": "Suspicious user context detected",
                "confidence": 0.75
            }
        
        # Check for suspicious session context
        session_context = context.get("session", {})
        if session_context.get("privileged", False):
            return {
                "risk": RiskLevel.LOW,
                "reason": "Privileged session detected",
                "confidence": 0.60
            }
        
        return {
            "risk": RiskLevel.NONE,
            "reason": "Context validation passed",
            "confidence": 0.85
        }
    
    def get_mitigation_strategy(self, risk_level: RiskLevel) -> str:
        """Get mitigation strategy"""
        strategies = {
            RiskLevel.BANNED: "Request blocked immediately",
            RiskLevel.HIGH: "Request blocked with explanation",
            RiskLevel.MODERATE: "Request allowed with warning",
            RiskLevel.LOW: "Request allowed with monitoring",
            RiskLevel.NONE: "Request allowed"
        }
        return strategies.get(risk_level, "Unknown risk level")

class RecursiveSafetyPolicy(GuardRailPolicy):
    """
    Recursive safety checking policy
    """
    
    def __init__(self):
        super().__init__(PolicyLayer.RECURSIVE)
        self.max_depth = 10
        self.recursive_patterns = [
            r"recursive.*call",
            r"infinite.*loop",
            r"self.*reference",
            r"circular.*dependency"
        ]
    
    async def evaluate(self, request_data: Dict) -> Dict:
        """Check for recursive safety issues"""
        content = request_data.get("content", "").lower()
        context = request_data.get("context", {})
        depth = context.get("depth", 0)
        
        # Check recursion depth
        if depth > self.max_depth:
            return {
                "risk": RiskLevel.HIGH,
                "reason": f"Recursion depth exceeded: {depth}",
                "confidence": 0.90
            }
        
        # Check for recursive patterns
        for pattern in self.recursive_patterns:
            if re.search(pattern, content):
                return {
                    "risk": RiskLevel.MODERATE,
                    "reason": f"Recursive pattern detected: {pattern}",
                    "confidence": 0.80
                }
        
        return {
            "risk": RiskLevel.NONE,
            "reason": "No recursive safety issues",
            "confidence": 0.85
        }
    
    def get_mitigation_strategy(self, risk_level: RiskLevel) -> str:
        """Get mitigation strategy"""
        strategies = {
            RiskLevel.BANNED: "Request blocked immediately",
            RiskLevel.HIGH: "Request blocked with explanation",
            RiskLevel.MODERATE: "Request allowed with warning",
            RiskLevel.LOW: "Request allowed with monitoring",
            RiskLevel.NONE: "Request allowed"
        }
        return strategies.get(risk_level, "Unknown risk level")

class GuardRailSystem:
    """
    Multi-layer guard-rail safety system
    """
    
    def __init__(self):
        self.policies: List[GuardRailPolicy] = []
        self.risk_levels = list(RiskLevel)
        self.policy_layers = list(PolicyLayer)
        self.enabled = True
    
    def add_policy(self, policy: GuardRailPolicy):
        """Add a guard-rail policy"""
        self.policies.append(policy)
        # Sort by priority (higher priority first)
        self.policies.sort(key=lambda p: p.priority, reverse=True)
    
    async def check_request(self, request_data: Dict) -> Dict:
        """
        Multi-layer safety check for all requests
        
        Args:
            request_data: Dictionary containing request information
                - content: Request text
                - intent: User intent (if available)
                - context: Request context
                - user_id: User identifier
                - timestamp: Request timestamp
        
        Returns:
            Risk assessment dictionary
                - risk: Risk level (none, low, moderate, high, banned)
                - reason: Explanation of risk assessment
                - mitigation: Recommended mitigation strategy
                - confidence: Confidence in assessment (0.0-1.0)
                - layers_checked: List of policy layers evaluated
        """
        if not self.enabled:
            return {
                "risk": RiskLevel.NONE.value,
                "reason": "Guard-rail system disabled",
                "mitigation": "No action required",
                "confidence": 1.0,
                "layers_checked": []
            }
        
        layer_results = []
        highest_risk = RiskLevel.NONE
        reasons = []
        
        # Evaluate each policy layer
        for policy in self.policies:
            if policy.enabled:
                try:
                    result = await policy.evaluate(request_data)
                    layer_results.append({
                        "layer": policy.layer.value,
                        "risk": result["risk"],
                        "reason": result["reason"],
                        "confidence": result.get("confidence", 0.5)
                    })
                    
                    # Track highest risk level
                    if result["risk"].value > highest_risk.value:
                        highest_risk = result["risk"]
                        reasons = [result["reason"]]
                    elif result["risk"].value == highest_risk.value:
                        reasons.append(result["reason"])
                        
                except Exception as e:
                    layer_results.append({
                        "layer": policy.layer.value,
                        "risk": RiskLevel.HIGH,
                        "reason": f"Policy evaluation failed: {str(e)}",
                        "confidence": 0.0
                    })
        
        # Aggregate results
        final_risk = highest_risk
        final_reason = "; ".join(reasons) if reasons else "No specific reason"
        final_confidence = self.calculate_aggregate_confidence(layer_results)
        final_mitigation = self.get_final_mitigation_strategy(final_risk)
        
        return {
            "risk": final_risk.value,
            "reason": final_reason,
            "mitigation": final_mitigation,
            "confidence": final_confidence,
            "layers_checked": [r["layer"] for r in layer_results],
            "layer_details": layer_results
        }
    
    def calculate_aggregate_confidence(self, layer_results: List[Dict]) -> float:
        """Calculate aggregate confidence from layer results"""
        if not layer_results:
            return 0.0
        
        # Weight by confidence and layer priority
        total_weight = 0.0
        weighted_sum = 0.0
        
        for result in layer_results:
            confidence = result["confidence"]
            weight = 1.0  # Could be weighted by layer importance
            
            weighted_sum += confidence * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def get_final_mitigation_strategy(self, risk_level: RiskLevel) -> str:
        """Get final mitigation strategy based on risk level"""
        strategies = {
            RiskLevel.BANNED: "Request blocked immediately",
            RiskLevel.HIGH: "Request blocked with explanation",
            RiskLevel.MODERATE: "Request allowed with warning and monitoring",
            RiskLevel.LOW: "Request allowed with light monitoring",
            RiskLevel.NONE: "Request allowed"
        }
        return strategies.get(risk_level, "Unknown risk level")
    
    def assess_risk(self, operation_description: str) -> Dict[str, Any]:
        """
        Assess risk for a specific operation
        
        Args:
            operation_description: Description of the operation to assess
        
        Returns:
            Risk assessment dictionary
                - risk_level: Risk level (none, low, moderate, high, banned)
                - recommendations: List of safety recommendations
                - allowed: Whether operation is allowed
        """
        # Create a mock request for assessment
        mock_request = {
            "content": operation_description,
            "user_id": "system",
            "context": {"operation_type": "system_operation"}
        }
        
        # Use the existing check_request method
        try:
            # Since check_request is async, we'll create a simple synchronous assessment
            risk_level = RiskLevel.NONE
            recommendations = []
            
            # Basic risk assessment based on operation description
            operation_lower = operation_description.lower()
            
            # Check for high-risk operations
            high_risk_patterns = [
                "delete", "remove", "destroy", "corrupt", "format", "wipe",
                "hack", "exploit", "bypass", "unauthorized", "malicious"
            ]
            
            for pattern in high_risk_patterns:
                if pattern in operation_lower:
                    risk_level = RiskLevel.HIGH
                    recommendations.append(f"Operation contains high-risk pattern: {pattern}")
                    break
            
            # Check for moderate-risk operations
            moderate_risk_patterns = [
                "modify", "change", "alter", "update", "replace", "test",
                "experiment", "debug", "analyze"
            ]
            
            if risk_level == RiskLevel.NONE:
                for pattern in moderate_risk_patterns:
                    if pattern in operation_lower:
                        risk_level = RiskLevel.MODERATE
                        recommendations.append(f"Operation contains moderate-risk pattern: {pattern}")
                        break
            
            # Determine if operation is allowed
            allowed = risk_level not in [RiskLevel.HIGH, RiskLevel.BANNED]
            
            return {
                "risk_level": risk_level.value,
                "recommendations": recommendations,
                "allowed": allowed
            }
            
        except Exception as e:
            return {
                "risk_level": RiskLevel.HIGH.value,
                "recommendations": [f"Risk assessment failed: {str(e)}"],
                "allowed": False
            }

# Example usage
async def test_guard_rail_system():
    """Test the guard-rail system"""
    guard_rail = GuardRailSystem()
    
    # Add policies
    guard_rail.add_policy(ContentFilterPolicy())
    guard_rail.add_policy(IntentAnalysisPolicy())
    guard_rail.add_policy(ContextValidationPolicy())
    guard_rail.add_policy(RecursiveSafetyPolicy())
    
    # Test requests
    test_requests = [
        {
            "content": "What is the weather today?",
            "user_id": "user123",
            "context": {"session_id": "123"}
        },
        {
            "content": "How to hack into a system?",
            "user_id": "user123",
            "context": {"session_id": "123"}
        },
        {
            "content": "This is a security test",
            "user_id": "admin",
            "context": {"session_id": "123", "privileged": True}
        }
    ]
    
    for request in test_requests:
        result = await guard_rail.check_request(request)
        print(f"Request: {request['content']}")
        print(f"Risk: {result['risk']}")
        print(f"Reason: {result['reason']}")
        print(f"Mitigation: {result['mitigation']}")
        print("---")

if __name__ == "__main__":
    asyncio.run(test_guard_rail_system()) 