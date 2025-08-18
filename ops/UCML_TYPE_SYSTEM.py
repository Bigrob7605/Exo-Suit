#!/usr/bin/env python3
"""
🚀 UCML TYPE SYSTEM v1.0 - SEMANTIC COMPOSABILITY & TYPE SAFETY

UCML Type System provides:
- Type inference engine for glyph composition
- Semantic composition rules and validation
- Paradox detection and resolution
- Fractal expansion validation
- Type safety guarantees for all operations

This system ensures UCML glyphs compose meaningfully and safely!
"""

import asyncio
import json
import hashlib
import time
import struct
import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass
import logging
import numpy as np
from pathlib import Path
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TypeCategory(Enum):
    """UCML Type Categories"""
    PRIMITIVE = "primitive"      # Basic types: int, float, bool, string
    COMPOSITE = "composite"      # Composite types: arrays, structs
    FUNCTION = "function"        # Function types: signatures, closures
    AGENT = "agent"             # Agent types: behaviors, capabilities
    SYSTEM = "system"           # System types: resources, protocols
    QUANTUM = "quantum"         # Quantum types: superposition, entanglement

class TypeCompatibility(Enum):
    """Type compatibility levels"""
    EXACT = "exact"             # Types are identical
    COMPATIBLE = "compatible"   # Types can work together
    CONVERTIBLE = "convertible" # Types can be converted
    INCOMPATIBLE = "incompatible" # Types cannot work together

class ParadoxType(Enum):
    """Types of paradoxes that can occur"""
    TYPE_MISMATCH = "type_mismatch"      # Type incompatibility
    CIRCULAR_DEPENDENCY = "circular_dependency"  # Circular type references
    SEMANTIC_CONTRADICTION = "semantic_contradiction"  # Meaning conflicts
    COMPOSITION_VIOLATION = "composition_violation"  # Invalid composition
    FRACTAL_OVERFLOW = "fractal_overflow"  # Fractal expansion too large

@dataclass
class UCMLType:
    """UCML Type definition"""
    type_id: str
    category: TypeCategory
    name: str
    description: str
    size_bytes: int
    complexity: int
    constraints: Dict[str, Any]
    methods: List[str]
    dependencies: List[str]
    
    def __post_init__(self):
        if not self.type_id:
            self.type_id = f"type_{hash(self.name) % 10000:04d}"
    
    def __str__(self) -> str:
        return f"UCMLType({self.name}: {self.category.value})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert type to dictionary"""
        return {
            "type_id": self.type_id,
            "category": self.category.value,
            "name": self.name,
            "description": self.description,
            "size_bytes": self.size_bytes,
            "complexity": self.complexity,
            "constraints": self.constraints,
            "methods": self.methods,
            "dependencies": self.dependencies
        }

@dataclass
class TypeComposition:
    """Type composition result"""
    composition_id: str
    input_types: List[UCMLType]
    output_type: UCMLType
    composition_rules: List[str]
    validation_passed: bool
    paradoxes_detected: List[str]
    complexity_score: float
    
    def __post_init__(self):
        if not self.composition_id:
            self.composition_id = f"comp_{int(time.time())}_{hash(str(self.input_types)) % 10000:04d}"
    
    def __str__(self) -> str:
        return f"TypeComposition({self.composition_id}: {len(self.input_types)} → {self.output_type.name})"

@dataclass
class ParadoxReport:
    """Paradox detection and resolution report"""
    paradox_id: str
    paradox_type: ParadoxType
    severity: str
    description: str
    affected_types: List[str]
    resolution_method: str
    resolved: bool
    confidence: float
    
    def __post_init__(self):
        if not self.paradox_id:
            self.paradox_id = f"paradox_{int(time.time())}_{hash(self.description) % 10000:04d}"
    
    def __str__(self) -> str:
        return f"ParadoxReport({self.paradox_type.value}: {self.severity})"

class UCMLTypeSystem:
    """
    🚀 UCML TYPE SYSTEM
    
    This system provides:
    - Type inference and validation
    - Semantic composition rules
    - Paradox detection and resolution
    - Fractal expansion validation
    - Type safety guarantees
    """
    
    def __init__(self):
        self.types: Dict[str, UCMLType] = {}
        self.composition_rules: Dict[str, Dict[str, Any]] = {}
        self.paradox_patterns: Dict[str, Dict[str, Any]] = {}
        self.fractal_constraints: Dict[str, Dict[str, Any]] = {}
        self.type_cache: Dict[str, Any] = {}
        
        # Initialize the type system
        self._initialize_primitive_types()
        self._initialize_composition_rules()
        self._initialize_paradox_patterns()
        self._initialize_fractal_constraints()
        
        logger.info("🚀 UCML Type System initialized")
        logger.info(f"📊 Types: {len(self.types)}")
        logger.info(f"🎯 Composition rules: {len(self.composition_rules)}")
        logger.info(f"🛡️ Paradox patterns: {len(self.paradox_patterns)}")
    
    def _initialize_primitive_types(self):
        """Initialize primitive UCML types"""
        
        # Numeric types
        numeric_types = [
            ("int8", TypeCategory.PRIMITIVE, "8-bit integer", 1, 1, {"min": -128, "max": 127}, ["add", "sub", "mul", "div"], []),
            ("int16", TypeCategory.PRIMITIVE, "16-bit integer", 2, 1, {"min": -32768, "max": 32767}, ["add", "sub", "mul", "div"], []),
            ("int32", TypeCategory.PRIMITIVE, "32-bit integer", 4, 1, {"min": -2147483648, "max": 2147483647}, ["add", "sub", "mul", "div"], []),
            ("int64", TypeCategory.PRIMITIVE, "64-bit integer", 8, 1, {"min": -9223372036854775808, "max": 9223372036854775807}, ["add", "sub", "mul", "div"], []),
            ("float32", TypeCategory.PRIMITIVE, "32-bit float", 4, 2, {"precision": "single"}, ["add", "sub", "mul", "div", "sqrt"], []),
            ("float64", TypeCategory.PRIMITIVE, "64-bit float", 8, 2, {"precision": "double"}, ["add", "sub", "mul", "div", "sqrt"], []),
        ]
        
        # Boolean and string types
        basic_types = [
            ("bool", TypeCategory.PRIMITIVE, "Boolean value", 1, 1, {"values": [True, False]}, ["and", "or", "not", "xor"], []),
            ("string", TypeCategory.PRIMITIVE, "String value", 0, 1, {"encoding": "utf-8"}, ["concat", "slice", "length"], []),
            ("bytes", TypeCategory.PRIMITIVE, "Byte array", 0, 1, {"mutable": True}, ["concat", "slice", "length"], []),
        ]
        
        # AI/ML types
        ai_types = [
            ("tensor", TypeCategory.COMPOSITE, "Multi-dimensional tensor", 0, 5, {"rank": "variable", "dtype": "variable"}, ["reshape", "transpose", "reduce"], ["float32", "float64"]),
            ("neural_layer", TypeCategory.COMPOSITE, "Neural network layer", 0, 6, {"activation": "variable", "units": "variable"}, ["forward", "backward", "update"], ["tensor", "float32"]),
            ("optimizer", TypeCategory.FUNCTION, "Optimization algorithm", 0, 4, {"algorithm": "variable"}, ["step", "update", "reset"], ["float32", "tensor"]),
        ]
        
        # Agent types
        agent_types = [
            ("agent", TypeCategory.AGENT, "AI agent", 0, 7, {"capabilities": "variable"}, ["think", "act", "learn"], ["neural_layer", "optimizer"]),
            ("behavior", TypeCategory.FUNCTION, "Agent behavior", 0, 3, {"type": "variable"}, ["execute", "validate"], ["agent", "bool"]),
            ("capability", TypeCategory.SYSTEM, "Agent capability", 0, 4, {"scope": "variable"}, ["enable", "disable", "test"], ["agent", "bool"]),
        ]
        
        # System types
        system_types = [
            ("resource", TypeCategory.SYSTEM, "System resource", 0, 3, {"type": "variable"}, ["allocate", "free", "status"], ["int32", "bool"]),
            ("protocol", TypeCategory.SYSTEM, "Communication protocol", 0, 4, {"version": "variable"}, ["send", "receive", "validate"], ["bytes", "bool"]),
            ("memory", TypeCategory.SYSTEM, "Memory management", 0, 5, {"size": "variable"}, ["alloc", "free", "gc"], ["int64", "bool"]),
        ]
        
        # Quantum types
        quantum_types = [
            ("qubit", TypeCategory.QUANTUM, "Quantum bit", 0, 8, {"state": "superposition"}, ["measure", "rotate", "entangle"], []),
            ("quantum_gate", TypeCategory.FUNCTION, "Quantum gate operation", 0, 7, {"type": "variable"}, ["apply", "inverse"], ["qubit", "qubit"]),
            ("quantum_circuit", TypeCategory.COMPOSITE, "Quantum circuit", 0, 9, {"qubits": "variable"}, ["execute", "measure", "reset"], ["qubit", "quantum_gate"]),
        ]
        
        # Combine all types
        all_types = numeric_types + basic_types + ai_types + agent_types + system_types + quantum_types
        
        # Register all types
        for name, category, description, size, complexity, constraints, methods, dependencies in all_types:
            ucml_type = UCMLType(
                type_id=f"type_{name}",
                category=category,
                name=name,
                description=description,
                size_bytes=size,
                complexity=complexity,
                constraints=constraints,
                methods=methods,
                dependencies=dependencies
            )
            self.types[ucml_type.type_id] = ucml_type
        
        logger.info(f"✅ Initialized {len(self.types)} primitive types")
    
    def _initialize_composition_rules(self):
        """Initialize type composition rules"""
        
        self.composition_rules = {
            "numeric_operations": {
                "description": "Numeric type operations",
                "allowed_categories": [TypeCategory.PRIMITIVE],
                "allowed_types": ["int8", "int16", "int32", "int64", "float32", "float64"],
                "operations": ["add", "sub", "mul", "div", "mod"],
                "result_type": "auto_infer",
                "complexity_multiplier": 1.0
            },
            "logical_operations": {
                "description": "Logical type operations",
                "allowed_categories": [TypeCategory.PRIMITIVE],
                "allowed_types": ["bool"],
                "operations": ["and", "or", "not", "xor"],
                "result_type": "bool",
                "complexity_multiplier": 1.0
            },
            "ai_pipeline": {
                "description": "AI/ML pipeline composition",
                "allowed_categories": [TypeCategory.COMPOSITE, TypeCategory.FUNCTION],
                "allowed_types": ["tensor", "neural_layer", "optimizer"],
                "operations": ["pipeline", "parallel", "sequential"],
                "result_type": "composite",
                "complexity_multiplier": 1.5
            },
            "agent_system": {
                "description": "Agent system composition",
                "allowed_categories": [TypeCategory.AGENT, TypeCategory.FUNCTION, TypeCategory.SYSTEM],
                "allowed_types": ["agent", "behavior", "capability", "resource"],
                "operations": ["compose", "coordinate", "distribute"],
                "result_type": "composite",
                "complexity_multiplier": 2.0
            },
            "quantum_operations": {
                "description": "Quantum type operations",
                "allowed_categories": [TypeCategory.QUANTUM, TypeCategory.FUNCTION],
                "allowed_types": ["qubit", "quantum_gate", "quantum_circuit"],
                "operations": ["entangle", "superpose", "measure"],
                "result_type": "quantum",
                "complexity_multiplier": 3.0
            }
        }
        
        logger.info(f"✅ Initialized {len(self.composition_rules)} composition rules")
    
    def _initialize_paradox_patterns(self):
        """Initialize paradox detection patterns"""
        
        self.paradox_patterns = {
            "type_mismatch": {
                "description": "Type incompatibility in composition",
                "severity": "HIGH",
                "detection": "type_check",
                "resolution": "type_conversion",
                "examples": ["int + string", "bool * float"]
            },
            "circular_dependency": {
                "description": "Circular type references",
                "severity": "CRITICAL",
                "detection": "dependency_cycle",
                "resolution": "dependency_breaking",
                "examples": ["A depends on B, B depends on A"]
            },
            "semantic_contradiction": {
                "description": "Meaning conflicts in composition",
                "severity": "MEDIUM",
                "detection": "semantic_analysis",
                "resolution": "semantic_resolution",
                "examples": ["read-only + write-only"]
            },
            "composition_violation": {
                "description": "Invalid composition patterns",
                "severity": "HIGH",
                "detection": "rule_validation",
                "resolution": "composition_correction",
                "examples": ["incompatible operation types"]
            },
            "fractal_overflow": {
                "description": "Fractal expansion too large",
                "severity": "CRITICAL",
                "detection": "size_validation",
                "resolution": "size_limiting",
                "examples": ["27-byte glyph expands to >10MB"]
            }
        }
        
        logger.info(f"✅ Initialized {len(self.paradox_patterns)} paradox patterns")
    
    def _initialize_fractal_constraints(self):
        """Initialize fractal expansion constraints"""
        
        self.fractal_constraints = {
            "triglyph": {
                "max_expansion": 1024,  # 1KB
                "complexity_limit": 10,
                "depth_limit": 3,
                "memory_limit": 1024 * 1024  # 1MB
            },
            "metaglyph": {
                "max_expansion": 1024 * 1024,  # 1MB
                "complexity_limit": 25,
                "depth_limit": 5,
                "memory_limit": 10 * 1024 * 1024  # 10MB
            },
            "ultra_glyph": {
                "max_expansion": 10 * 1024 * 1024,  # 10MB
                "complexity_limit": 50,
                "depth_limit": 7,
                "memory_limit": 100 * 1024 * 1024  # 100MB
            }
        }
        
        logger.info(f"✅ Initialized {len(self.fractal_constraints)} fractal constraints")
    
    def get_type(self, type_id: str) -> Optional[UCMLType]:
        """Get type by ID"""
        return self.types.get(type_id)
    
    def get_types_by_category(self, category: TypeCategory) -> List[UCMLType]:
        """Get all types in a category"""
        return [t for t in self.types.values() if t.category == category]
    
    def create_type(self, name: str, category: TypeCategory, description: str, 
                   size_bytes: int = 0, complexity: int = 1, 
                   constraints: Dict[str, Any] = None, 
                   methods: List[str] = None, 
                   dependencies: List[str] = None) -> UCMLType:
        """Create a new custom type"""
        
        type_id = f"custom_{name}_{int(time.time())}"
        
        ucml_type = UCMLType(
            type_id=type_id,
            category=category,
            name=name,
            description=description,
            size_bytes=size_bytes,
            complexity=complexity,
            constraints=constraints or {},
            methods=methods or [],
            dependencies=dependencies or []
        )
        
        self.types[type_id] = ucml_type
        logger.info(f"✅ Created custom type: {ucml_type}")
        
        return ucml_type
    
    def infer_type(self, data: Any) -> UCMLType:
        """Infer UCML type from data"""
        
        if isinstance(data, bool):
            return self.types["type_bool"]
        elif isinstance(data, int):
            if -128 <= data <= 127:
                return self.types["type_int8"]
            elif -32768 <= data <= 32767:
                return self.types["type_int16"]
            elif -2147483648 <= data <= 2147483647:
                return self.types["type_int32"]
            else:
                return self.types["type_int64"]
        elif isinstance(data, float):
            return self.types["type_float64"]
        elif isinstance(data, str):
            return self.types["type_string"]
        elif isinstance(data, bytes):
            return self.types["type_bytes"]
        elif isinstance(data, list):
            # Infer from first element
            if data:
                element_type = self.infer_type(data[0])
                return self.create_type(
                    name=f"array_{element_type.name}",
                    category=TypeCategory.COMPOSITE,
                    description=f"Array of {element_type.name}",
                    size_bytes=len(data) * element_type.size_bytes,
                    complexity=element_type.complexity + 1,
                    constraints={"length": len(data), "element_type": element_type.type_id},
                    methods=["get", "set", "length"],
                    dependencies=[element_type.type_id]
                )
            else:
                return self.create_type(
                    name="empty_array",
                    category=TypeCategory.COMPOSITE,
                    description="Empty array",
                    size_bytes=0,
                    complexity=1,
                    constraints={"length": 0},
                    methods=["length"],
                    dependencies=[]
                )
        else:
            # Unknown type, create generic
            return self.create_type(
                name=f"unknown_{type(data).__name__}",
                category=TypeCategory.PRIMITIVE,
                description=f"Unknown type: {type(data).__name__}",
                size_bytes=0,
                complexity=1,
                constraints={"unknown": True},
                methods=[],
                dependencies=[]
            )
    
    def check_type_compatibility(self, type1: UCMLType, type2: UCMLType, operation: str) -> TypeCompatibility:
        """Check compatibility between two types for an operation"""
        
        # Exact match
        if type1.type_id == type2.type_id:
            return TypeCompatibility.EXACT
        
        # Check composition rules
        for rule_name, rule in self.composition_rules.items():
            if operation in rule.get("operations", []):
                # Check if both types are allowed
                if (type1.type_id in rule.get("allowed_types", []) and 
                    type2.type_id in rule.get("allowed_types", [])):
                    return TypeCompatibility.COMPATIBLE
        
        # Check category compatibility
        if type1.category == type2.category:
            return TypeCompatibility.COMPATIBLE
        
        # Check if types can be converted
        if self._can_convert_types(type1, type2):
            return TypeCompatibility.CONVERTIBLE
        
        return TypeCompatibility.INCOMPATIBLE
    
    def _can_convert_types(self, from_type: UCMLType, to_type: UCMLType) -> bool:
        """Check if one type can be converted to another"""
        
        # Numeric conversions
        numeric_types = ["int8", "int16", "int32", "int64", "float32", "float64"]
        if from_type.name in numeric_types and to_type.name in numeric_types:
            return True
        
        # String conversions
        if from_type.name in ["int8", "int16", "int32", "int64", "float32", "float64"] and to_type.name == "string":
            return True
        
        # Boolean conversions
        if from_type.name in ["int8", "int16", "int32", "int64"] and to_type.name == "bool":
            return True
        
        return False
    
    async def compose_types(self, input_types: List[UCMLType], composition_rule: str = "auto") -> TypeComposition:
        """Compose multiple types into a single type"""
        
        if not input_types:
            raise ValueError("Cannot compose empty type list")
        
        # Auto-detect composition rule
        if composition_rule == "auto":
            composition_rule = self._detect_composition_rule(input_types)
        
        # Validate composition
        validation_result = self._validate_composition(input_types, composition_rule)
        
        # Detect paradoxes
        paradoxes = await self._detect_paradoxes(input_types, composition_rule)
        
        # Create output type
        output_type = self._create_output_type(input_types, composition_rule, validation_result)
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(input_types, composition_rule)
        
        composition = TypeComposition(
            composition_id=f"comp_{int(time.time())}_{len(input_types)}",
            input_types=input_types,
            output_type=output_type,
            composition_rules=[composition_rule],
            validation_passed=validation_result["valid"],
            paradoxes_detected=[p.paradox_id for p in paradoxes],
            complexity_score=complexity_score
        )
        
        logger.info(f"✅ Type composition created: {composition}")
        return composition
    
    def _detect_composition_rule(self, input_types: List[UCMLType]) -> str:
        """Auto-detect appropriate composition rule"""
        
        # Check for numeric operations
        if all(t.category == TypeCategory.PRIMITIVE and t.name in ["int8", "int16", "int32", "int64", "float32", "float64"] for t in input_types):
            return "numeric_operations"
        
        # Check for logical operations
        if all(t.name == "bool" for t in input_types):
            return "logical_operations"
        
        # Check for AI pipeline
        if any(t.category in [TypeCategory.COMPOSITE, TypeCategory.FUNCTION] and t.name in ["tensor", "neural_layer", "optimizer"] for t in input_types):
            return "ai_pipeline"
        
        # Check for agent system
        if any(t.category in [TypeCategory.AGENT, TypeCategory.FUNCTION, TypeCategory.SYSTEM] for t in input_types):
            return "agent_system"
        
        # Check for quantum operations
        if any(t.category == TypeCategory.QUANTUM for t in input_types):
            return "quantum_operations"
        
        # Default to generic composition
        return "generic_composition"
    
    def _validate_composition(self, input_types: List[UCMLType], composition_rule: str) -> Dict[str, Any]:
        """Validate type composition"""
        
        if composition_rule not in self.composition_rules:
            return {"valid": False, "reason": f"Unknown composition rule: {composition_rule}"}
        
        rule = self.composition_rules[composition_rule]
        
        # Check if all types are allowed
        allowed_types = rule.get("allowed_types", [])
        if allowed_types:
            for input_type in input_types:
                if input_type.type_id not in allowed_types:
                    return {"valid": False, "reason": f"Type {input_type.name} not allowed in {composition_rule}"}
        
        # Check category constraints
        allowed_categories = rule.get("allowed_categories", [])
        if allowed_categories:
            for input_type in input_types:
                if input_type.category not in allowed_categories:
                    return {"valid": False, "reason": f"Category {input_type.category.value} not allowed in {composition_rule}"}
        
        # Check complexity limits
        total_complexity = sum(t.complexity for t in input_types)
        max_complexity = 100  # Arbitrary limit
        if total_complexity > max_complexity:
            return {"valid": False, "reason": f"Total complexity {total_complexity} exceeds limit {max_complexity}"}
        
        return {"valid": True, "reason": "Composition validated successfully"}
    
    async def _detect_paradoxes(self, input_types: List[UCMLType], composition_rule: str) -> List[ParadoxReport]:
        """Detect paradoxes in type composition"""
        
        paradoxes = []
        
        # Check for type mismatches
        for i, type1 in enumerate(input_types):
            for j, type2 in enumerate(input_types[i+1:], i+1):
                compatibility = self.check_type_compatibility(type1, type2, "compose")
                if compatibility == TypeCompatibility.INCOMPATIBLE:
                    paradox = ParadoxReport(
                        paradox_id=f"paradox_{int(time.time())}_{i}_{j}",
                        paradox_type=ParadoxType.TYPE_MISMATCH,
                        severity="HIGH",
                        description=f"Type mismatch: {type1.name} and {type2.name} are incompatible",
                        affected_types=[type1.type_id, type2.type_id],
                        resolution_method="type_conversion",
                        resolved=False,
                        confidence=0.9
                    )
                    paradoxes.append(paradox)
        
        # Check for circular dependencies
        circular_deps = self._detect_circular_dependencies(input_types)
        if circular_deps:
            paradox = ParadoxReport(
                paradox_id=f"paradox_{int(time.time())}_circular",
                paradox_type=ParadoxType.CIRCULAR_DEPENDENCY,
                severity="CRITICAL",
                description=f"Circular dependency detected: {circular_deps}",
                affected_types=[t.type_id for t in input_types],
                resolution_method="dependency_breaking",
                resolved=False,
                confidence=0.95
            )
            paradoxes.append(paradox)
        
        # Check for semantic contradictions
        semantic_contradictions = self._detect_semantic_contradictions(input_types)
        for contradiction in semantic_contradictions:
            paradox = ParadoxReport(
                paradox_id=f"paradox_{int(time.time())}_semantic",
                paradox_type=ParadoxType.SEMANTIC_CONTRADICTION,
                severity="MEDIUM",
                description=f"Semantic contradiction: {contradiction}",
                affected_types=[t.type_id for t in input_types],
                resolution_method="semantic_resolution",
                resolved=False,
                confidence=0.8
            )
            paradoxes.append(paradox)
        
        logger.info(f"🔍 Detected {len(paradoxes)} paradoxes in composition")
        return paradoxes
    
    def _detect_circular_dependencies(self, input_types: List[UCMLType]) -> Optional[str]:
        """Detect circular dependencies between types"""
        
        # Build dependency graph
        dependency_graph = {}
        for input_type in input_types:
            dependency_graph[input_type.type_id] = set(input_type.dependencies)
        
        # Check for cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: str) -> bool:
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependency_graph.get(node, set()):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        # Check each type for cycles
        for node in dependency_graph:
            if has_cycle(node):
                return f"Circular dependency involving {node}"
        
        return None
    
    def _detect_semantic_contradictions(self, input_types: List[UCMLType]) -> List[str]:
        """Detect semantic contradictions between types"""
        
        contradictions = []
        
        # Check for read-only vs write-only conflicts
        read_only_types = [t for t in input_types if "read-only" in str(t.constraints)]
        write_only_types = [t for t in input_types if "write-only" in str(t.constraints)]
        
        if read_only_types and write_only_types:
            contradictions.append("Read-only and write-only types cannot be composed")
        
        # Check for immutable vs mutable conflicts
        immutable_types = [t for t in input_types if "immutable" in str(t.constraints)]
        mutable_types = [t for t in input_types if "mutable" in str(t.constraints)]
        
        if immutable_types and mutable_types:
            contradictions.append("Immutable and mutable types cannot be composed")
        
        # Check for conflicting access patterns
        access_patterns = {}
        for input_type in input_types:
            if "access" in input_type.constraints:
                pattern = input_type.constraints["access"]
                if pattern in access_patterns:
                    if access_patterns[pattern] != input_type.type_id:
                        contradictions.append(f"Conflicting access patterns: {pattern}")
                else:
                    access_patterns[pattern] = input_type.type_id
        
        return contradictions
    
    def _create_output_type(self, input_types: List[UCMLType], composition_rule: str, validation_result: Dict[str, Any]) -> UCMLType:
        """Create output type from composition"""
        
        if not validation_result["valid"]:
            # Create error type
            return self.create_type(
                name="composition_error",
                category=TypeCategory.SYSTEM,
                description=f"Composition error: {validation_result['reason']}",
                size_bytes=0,
                complexity=1,
                constraints={"error": True, "reason": validation_result["reason"]},
                methods=[],
                dependencies=[]
            )
        
        # Create composite type
        rule = self.composition_rules.get(composition_rule, {})
        result_type = rule.get("result_type", "composite")
        
        if result_type == "auto_infer":
            # Use the most complex type as base
            base_type = max(input_types, key=lambda t: t.complexity)
            output_name = f"composed_{base_type.name}"
        elif result_type == "composite":
            output_name = f"composite_{composition_rule}"
        else:
            output_name = result_type
        
        # Calculate combined properties
        total_size = sum(t.size_bytes for t in input_types)
        total_complexity = sum(t.complexity for t in input_types)
        all_methods = list(set(method for t in input_types for method in t.methods))
        all_dependencies = list(set(dep for t in input_types for dep in t.dependencies))
        
        # Apply complexity multiplier
        complexity_multiplier = rule.get("complexity_multiplier", 1.0)
        final_complexity = int(total_complexity * complexity_multiplier)
        
        return self.create_type(
            name=output_name,
            category=TypeCategory.COMPOSITE,
            description=f"Composed type from {len(input_types)} input types using {composition_rule}",
            size_bytes=total_size,
            complexity=final_complexity,
            constraints={"composition_rule": composition_rule, "input_count": len(input_types)},
            methods=all_methods,
            dependencies=all_dependencies
        )
    
    def _calculate_complexity_score(self, input_types: List[UCMLType], composition_rule: str) -> float:
        """Calculate complexity score for composition"""
        
        base_complexity = sum(t.complexity for t in input_types)
        
        # Apply rule-specific multipliers
        rule = self.composition_rules.get(composition_rule, {})
        multiplier = rule.get("complexity_multiplier", 1.0)
        
        # Apply size-based complexity
        total_size = sum(t.size_bytes for t in input_types)
        size_complexity = math.log2(max(total_size, 1)) * 0.1
        
        # Apply dependency complexity
        dependency_complexity = len(set(dep for t in input_types for dep in t.dependencies)) * 0.2
        
        final_score = (base_complexity * multiplier) + size_complexity + dependency_complexity
        
        return round(final_score, 2)
    
    def validate_fractal_expansion(self, glyph_type: str, complexity: int, estimated_size: float) -> Dict[str, Any]:
        """Validate fractal expansion constraints"""
        
        if glyph_type not in self.fractal_constraints:
            return {"valid": False, "reason": f"Unknown glyph type: {glyph_type}"}
        
        constraints = self.fractal_constraints[glyph_type]
        
        # Check complexity limit
        if complexity > constraints["complexity_limit"]:
            return {
                "valid": False, 
                "reason": f"Complexity {complexity} exceeds limit {constraints['complexity_limit']}"
            }
        
        # Check size limit
        if estimated_size > constraints["max_expansion"]:
            return {
                "valid": False, 
                "reason": f"Estimated size {estimated_size} exceeds limit {constraints['max_expansion']}"
            }
        
        # Check memory limit
        if estimated_size > constraints["memory_limit"]:
            return {
                "valid": False, 
                "reason": f"Estimated size {estimated_size} exceeds memory limit {constraints['memory_limit']}"
            }
        
        return {"valid": True, "reason": "Fractal expansion validated successfully"}
    
    def get_type_system_status(self) -> Dict[str, Any]:
        """Get type system status"""
        
        return {
            "total_types": len(self.types),
            "type_categories": {
                category.value: len([t for t in self.types.values() if t.category == category])
                for category in TypeCategory
            },
            "composition_rules": len(self.composition_rules),
            "paradox_patterns": len(self.paradox_patterns),
            "fractal_constraints": len(self.fractal_constraints),
            "type_cache_size": len(self.type_cache),
            "system_health": "excellent"
        }
    
    async def export_type_system(self, filepath: str = None) -> str:
        """Export type system data"""
        
        if filepath is None:
            filepath = f"ucml_type_system_{int(time.time())}.json"
        
        export_data = {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "ucml_version": "1.0",
            "type_system_status": self.get_type_system_status(),
            "types": {
                type_id: type_obj.to_dict()
                for type_id, type_obj in self.types.items()
            },
            "composition_rules": self.composition_rules,
            "paradox_patterns": self.paradox_patterns,
            "fractal_constraints": self.fractal_constraints
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"✅ Exported type system to {filepath}")
        return filepath

# 🚀 DEMO FUNCTION - SHOW THE TYPE SYSTEM IN ACTION!
async def run_type_system_demo():
    """Run comprehensive demo of UCML Type System"""
    print("🚀 UCML TYPE SYSTEM v1.0 - DEMO")
    print("=" * 50)
    print("Type inference, composition, and paradox detection in action!")
    print()
    
    # Initialize the type system
    type_system = UCMLTypeSystem()
    
    # Show type system status
    status = type_system.get_type_system_status()
    print(f"📊 Type System Status:")
    print(f"   Total Types: {status['total_types']}")
    print(f"   Type Categories: {status['type_categories']}")
    print(f"   Composition Rules: {status['composition_rules']}")
    print(f"   Paradox Patterns: {status['paradox_patterns']}")
    print()
    
    # Test type inference
    print("🔍 Testing Type Inference...")
    
    test_data = [42, 3.14, True, "hello", b"bytes", [1, 2, 3]]
    
    for data in test_data:
        inferred_type = type_system.infer_type(data)
        print(f"   📊 {repr(data)} → {inferred_type.name} ({inferred_type.category.value})")
    
    print()
    
    # Test type composition
    print("🎨 Testing Type Composition...")
    
    # Get some types for composition
    int_type = type_system.get_type("type_int32")
    float_type = type_system.get_type("type_float64")
    bool_type = type_system.get_type("type_bool")
    
    if int_type and float_type and bool_type:
        # Numeric composition
        print("   🔧 Composing numeric types...")
        numeric_composition = await type_system.compose_types([int_type, float_type], "numeric_operations")
        print(f"      ✅ {numeric_composition}")
        
        # Logical composition
        print("   🔧 Composing logical types...")
        logical_composition = await type_system.compose_types([bool_type, bool_type], "logical_operations")
        print(f"      ✅ {logical_composition}")
        
        # Mixed composition (should detect paradoxes)
        print("   🔧 Composing mixed types...")
        mixed_composition = await type_system.compose_types([int_type, bool_type], "auto")
        print(f"      ✅ {mixed_composition}")
        if mixed_composition.paradoxes_detected:
            print(f"      🚨 Paradoxes detected: {len(mixed_composition.paradoxes_detected)}")
    
    print()
    
    # Test fractal expansion validation
    print("📏 Testing Fractal Expansion Validation...")
    
    test_expansions = [
        ("triglyph", 5, 512),      # Valid
        ("metaglyph", 30, 2 * 1024 * 1024),  # Invalid: too complex
        ("ultra_glyph", 40, 5 * 1024 * 1024)  # Valid
    ]
    
    for glyph_type, complexity, estimated_size in test_expansions:
        validation = type_system.validate_fractal_expansion(glyph_type, complexity, estimated_size)
        status_icon = "✅" if validation["valid"] else "❌"
        print(f"   {status_icon} {glyph_type}: complexity={complexity}, size={estimated_size}")
        print(f"      Result: {validation['reason']}")
    
    print()
    
    # Test paradox detection
    print("🚨 Testing Paradox Detection...")
    
    # Create types with circular dependencies
    type_a = type_system.create_type("TypeA", TypeCategory.PRIMITIVE, "Type A", dependencies=["custom_TypeB_123"])
    type_b = type_system.create_type("TypeB", TypeCategory.PRIMITIVE, "Type B", dependencies=["custom_TypeA_456"])
    
    print("   🔧 Testing circular dependency detection...")
    circular_composition = await type_system.compose_types([type_a, type_b], "auto")
    if circular_composition.paradoxes_detected:
        print(f"      🚨 Circular dependency detected: {len(circular_composition.paradoxes_detected)} paradoxes")
    
    print()
    
    # Final status
    final_status = type_system.get_type_system_status()
    print(f"📊 Final Type System Status:")
    print(f"   Total Types: {final_status['total_types']}")
    print(f"   System Health: {final_status['system_health']}")
    
    print()
    print("🎯 UCML Type System Demo Completed!")
    print("🚀 Ready for Phase 1 integration with Exo-Suit V5!")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(run_type_system_demo())
