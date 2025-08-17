#!/usr/bin/env python3
"""
Kai Core Challenge Generator
Generates adversarial tests and challenges for self-improvement
"""

import hashlib
import json
import os
import random
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ChallengeType(Enum):
    EDGE_CASE = "edge_case"
    P_HACKING = "p_hacking"
    DATA_MANIPULATION = "data_manipulation"
    LOGICAL_PARADOX = "logical_paradox"
    PERFORMANCE = "performance"
    SECURITY = "security"


class ChallengeGenerator:
    """
    Generates adversarial challenges for self-improvement
    """

    def __init__(self, toolbox_path: str):
        self.toolbox_path = toolbox_path
        self.challenges_dir = os.path.join(toolbox_path, "kai_core", "challenges")
        os.makedirs(self.challenges_dir, exist_ok=True)

        # Load challenge templates
        self.challenge_templates = self._load_challenge_templates()

    def _load_challenge_templates(self) -> Dict[str, str]:
        """Load challenge generation templates"""
        return {
            "edge_case": self._get_edge_case_template(),
            "p_hacking": self._get_p_hacking_template(),
            "data_manipulation": self._get_data_manipulation_template(),
            "logical_paradox": self._get_logical_paradox_template(),
            "performance": self._get_performance_template(),
            "security": self._get_security_template(),
        }

    def _get_edge_case_template(self) -> str:
        """Template for edge case challenges"""
        return '''
def {challenge_name}(data: np.ndarray, **kwargs) -> Dict[str, Any]:
    """
    Edge case challenge: {description}
    
    This challenge tests how the system handles extreme or unexpected inputs.
    """
    try:
        # Edge case: Empty data
        if data.size == 0:
            return {{
                "challenge_type": "edge_case",
                "challenge_name": "{challenge_name}",
                "description": "{description}",
                "expected_failure": True,
                "result": {{
                    "error": "Empty data array",
                    "handled_gracefully": True
                }}
            }}
        
        # Edge case: Single value
        if data.size == 1:
            return {{
                "challenge_type": "edge_case",
                "challenge_name": "{challenge_name}",
                "description": "{description}",
                "expected_failure": False,
                "result": {{
                    "single_value": float(data[0]),
                    "handled_gracefully": True
                }}
            }}
        
        # Edge case: All identical values
        if np.all(data == data[0]):
            return {{
                "challenge_type": "edge_case",
                "challenge_name": "{challenge_name}",
                "description": "{description}",
                "expected_failure": False,
                "result": {{
                    "all_identical": True,
                    "variance": 0.0,
                    "handled_gracefully": True
                }}
            }}
        
        # Edge case: NaN values
        if np.any(np.isnan(data)):
            return {{
                "challenge_type": "edge_case",
                "challenge_name": "{challenge_name}",
                "description": "{description}",
                "expected_failure": True,
                "result": {{
                    "nan_count": int(np.sum(np.isnan(data))),
                    "handled_gracefully": True
                }}
            }}
        
        # Edge case: Infinite values
        if np.any(np.isinf(data)):
            return {{
                "challenge_type": "edge_case",
                "challenge_name": "{challenge_name}",
                "description": "{description}",
                "expected_failure": True,
                "result": {{
                    "inf_count": int(np.sum(np.isinf(data))),
                    "handled_gracefully": True
                }}
            }}
        
        return {{
            "challenge_type": "edge_case",
            "challenge_name": "{challenge_name}",
            "description": "{description}",
            "expected_failure": False,
            "result": {{
                "handled_gracefully": True,
                "data_shape": data.shape
            }}
        }}
        
    except Exception as e:
        return {{
            "challenge_type": "edge_case",
            "challenge_name": "{challenge_name}",
            "description": "{description}",
            "expected_failure": True,
            "result": {{
                "error": str(e),
                "handled_gracefully": False
            }}
        }}
'''

    def _get_p_hacking_template(self) -> str:
        """Template for p-hacking challenges"""
        return '''
def {challenge_name}(data: np.ndarray, **kwargs) -> Dict[str, Any]:
    """
    P-hacking challenge: {description}
    
    This challenge tests if the system can detect and prevent p-hacking.
    """
    try:
        # Simulate p-hacking by trying multiple tests
        from scipy import stats
        
        # Multiple statistical tests (p-hacking attempt)
        tests = []
        p_values = []
        
        # Test 1: t-test
        if data.ndim == 2 and data.shape[1] >= 2:
            t_stat, p_val = stats.ttest_ind(data[:, 0], data[:, 1])
            tests.append("t_test")
            p_values.append(p_val)
        
        # Test 2: Mann-Whitney U
        if data.ndim == 2 and data.shape[1] >= 2:
            u_stat, p_val = stats.mannwhitneyu(data[:, 0], data[:, 1])
            tests.append("mann_whitney")
            p_values.append(p_val)
        
        # Test 3: Wilcoxon signed-rank
        if data.ndim == 2 and data.shape[1] >= 2:
            w_stat, p_val = stats.wilcoxon(data[:, 0], data[:, 1])
            tests.append("wilcoxon")
            p_values.append(p_val)
        
        # Test 4: Kruskal-Wallis
        if data.ndim == 2 and data.shape[1] >= 3:
            h_stat, p_val = stats.kruskal(*[data[:, i] for i in range(data.shape[1])])
            tests.append("kruskal_wallis")
            p_values.append(p_val)
        
        # Check for p-hacking (multiple comparisons without correction)
        significant_tests = [p < 0.05 for p in p_values]
        p_hacking_detected = sum(significant_tests) > 1
        
        # Bonferroni correction
        bonferroni_threshold = 0.05 / len(p_values) if p_values else 0.05
        corrected_significant = [p < bonferroni_threshold for p in p_values]
        
        return {{
            "challenge_type": "p_hacking",
            "challenge_name": "{challenge_name}",
            "description": "{description}",
            "expected_failure": p_hacking_detected,
            "result": {{
                "tests_performed": tests,
                "p_values": [float(p) for p in p_values],
                "significant_without_correction": significant_tests,
                "significant_with_correction": corrected_significant,
                "p_hacking_detected": p_hacking_detected,
                "bonferroni_threshold": float(bonferroni_threshold)
            }}
        }}
        
    except Exception as e:
        return {{
            "challenge_type": "p_hacking",
            "challenge_name": "{challenge_name}",
            "description": "{description}",
            "expected_failure": True,
            "result": {{
                "error": str(e),
                "handled_gracefully": False
            }}
        }}
'''

    def _get_data_manipulation_template(self) -> str:
        """Template for data manipulation challenges"""
        return '''
def {challenge_name}(data: np.ndarray, **kwargs) -> Dict[str, Any]:
    """
    Data manipulation challenge: {description}
    
    This challenge tests if the system can detect data manipulation.
    """
    try:
        # Check for data manipulation indicators
        
        # 1. Check for suspicious patterns
        suspicious_patterns = []
        
        # All values identical
        if np.all(data == data[0]):
            suspicious_patterns.append("all_identical")
        
        # Perfect correlation
        if data.ndim == 2 and data.shape[1] >= 2:
            corr = np.corrcoef(data[:, 0], data[:, 1])[0, 1]
            if abs(corr) > 0.99:
                suspicious_patterns.append("perfect_correlation")
        
        # Round numbers only
        if np.all(np.round(data) == data):
            suspicious_patterns.append("all_round_numbers")
        
        # 2. Check for statistical anomalies
        anomalies = []
        
        # Too perfect distribution
        if data.size > 100:
            mean_val = np.mean(data)
            std_val = np.std(data)
            z_scores = np.abs((data - mean_val) / std_val)
            if np.max(z_scores) < 2.0:  # No outliers
                anomalies.append("too_perfect_distribution")
        
        # 3. Check for data fabrication indicators
        fabrication_indicators = []
        
        # Benford's law violation
        if np.all(data > 0):
            first_digits = [int(str(abs(x))[0]) for x in data.flatten()]
            digit_counts = np.bincount(first_digits, minlength=10)[1:]
            expected_benford = np.array([0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046])
            if len(digit_counts) >= 9:
                benford_violation = np.sum(np.abs(digit_counts/len(first_digits) - expected_benford[:len(digit_counts)]))
                if benford_violation > 0.5:
                    fabrication_indicators.append("benford_law_violation")
        
        manipulation_detected = len(suspicious_patterns) > 0 or len(anomalies) > 0 or len(fabrication_indicators) > 0
        
        return {{
            "challenge_type": "data_manipulation",
            "challenge_name": "{challenge_name}",
            "description": "{description}",
            "expected_failure": manipulation_detected,
            "result": {{
                "suspicious_patterns": suspicious_patterns,
                "anomalies": anomalies,
                "fabrication_indicators": fabrication_indicators,
                "manipulation_detected": manipulation_detected,
                "data_hash": hashlib.sha256(data.tobytes()).hexdigest()
            }}
        }}
        
    except Exception as e:
        return {{
            "challenge_type": "data_manipulation",
            "challenge_name": "{challenge_name}",
            "description": "{description}",
            "expected_failure": True,
            "result": {{
                "error": str(e),
                "handled_gracefully": False
            }}
        }}
'''

    def _get_logical_paradox_template(self) -> str:
        """Template for logical paradox challenges"""
        return '''
def {challenge_name}(data: np.ndarray, **kwargs) -> Dict[str, Any]:
    """
    Logical paradox challenge: {description}
    
    This challenge tests if the system can handle logical contradictions.
    """
    try:
        # Create logical paradox scenarios
        
        # Paradox 1: Self-referential condition
        paradox_conditions = []
        
        # Condition that depends on its own result
        if data.size > 0:
            mean_val = np.mean(data)
            condition = mean_val > 0
            # Paradox: if condition is True, we should return False, but if False, we should return True
            paradox_conditions.append("self_referential")
        
        # Paradox 2: Circular dependency
        if data.ndim == 2 and data.shape[1] >= 2:
            # Create circular dependency in analysis
            result_a = np.mean(data[:, 0]) > np.mean(data[:, 1])
            result_b = np.mean(data[:, 1]) > np.mean(data[:, 0])
            if result_a and result_b:
                paradox_conditions.append("circular_dependency")
        
        # Paradox 3: Meta-paradox
        # The system cannot determine if this challenge is valid
        meta_paradox = len(paradox_conditions) > 0 and "self_referential" in paradox_conditions
        
        paradox_detected = len(paradox_conditions) > 0
        
        return {{
            "challenge_type": "logical_paradox",
            "challenge_name": "{challenge_name}",
            "description": "{description}",
            "expected_failure": paradox_detected,
            "result": {{
                "paradox_conditions": paradox_conditions,
                "meta_paradox": meta_paradox,
                "paradox_detected": paradox_detected,
                "resolution_method": "containment" if paradox_detected else "none"
            }}
        }}
        
    except Exception as e:
        return {{
            "challenge_type": "logical_paradox",
            "challenge_name": "{challenge_name}",
            "description": "{description}",
            "expected_failure": True,
            "result": {{
                "error": str(e),
                "handled_gracefully": False
            }}
        }}
'''

    def _get_performance_template(self) -> str:
        """Template for performance challenges"""
        return '''
def {challenge_name}(data: np.ndarray, **kwargs) -> Dict[str, Any]:
    """
    Performance challenge: {description}
    
    This challenge tests system performance under stress.
    """
    try:
        import time
        
        start_time = time.time()
        
        # Performance stress test
        # Large data processing
        if data.size > 10000:
            # Complex computation
            result = np.linalg.eigvals(data.reshape(-1, min(100, data.size)))
            computation_time = time.time() - start_time
            
            # Check for timeout
            timeout_threshold = 30  # seconds
            timed_out = computation_time > timeout_threshold
            
            return {{
                "challenge_type": "performance",
                "challenge_name": "{challenge_name}",
                "description": "{description}",
                "expected_failure": timed_out,
                "result": {{
                    "computation_time": float(computation_time),
                    "timeout_threshold": timeout_threshold,
                    "timed_out": timed_out,
                    "data_size": data.size,
                    "memory_usage": "high" if data.size > 100000 else "normal"
                }}
            }}
        else:
            # Small data - should be fast
            computation_time = time.time() - start_time
            
            return {{
                "challenge_type": "performance",
                "challenge_name": "{challenge_name}",
                "description": "{description}",
                "expected_failure": False,
                "result": {{
                    "computation_time": float(computation_time),
                    "performance_adequate": computation_time < 1.0,
                    "data_size": data.size
                }}
            }}
        
    except Exception as e:
        return {{
            "challenge_type": "performance",
            "challenge_name": "{challenge_name}",
            "description": "{description}",
            "expected_failure": True,
            "result": {{
                "error": str(e),
                "handled_gracefully": False
            }}
        }}
'''

    def _get_security_template(self) -> str:
        """Template for security challenges"""
        return '''
def {challenge_name}(data: np.ndarray, **kwargs) -> Dict[str, Any]:
    """
    Security challenge: {description}
    
    This challenge tests system security and input validation.
    """
    try:
        # Security vulnerability tests
        
        # 1. Check for code injection attempts
        security_issues = []
        
        # 2. Check for buffer overflow attempts
        if data.size > 1000000:  # Very large data
            security_issues.append("potential_buffer_overflow")
        
        # 3. Check for malicious patterns
        malicious_patterns = [
            "eval(", "exec(", "os.system(", "subprocess.call(",
            "__import__(", "globals(", "locals(", "vars("
        ]
        
        # 4. Check for data leakage
        if kwargs.get("sensitive_data", False):
            security_issues.append("sensitive_data_exposure")
        
        # 5. Check for unauthorized access patterns
        if kwargs.get("admin_access", False):
            security_issues.append("unauthorized_access_attempt")
        
        security_vulnerability = len(security_issues) > 0
        
        return {{
            "challenge_type": "security",
            "challenge_name": "{challenge_name}",
            "description": "{description}",
            "expected_failure": security_vulnerability,
            "result": {{
                "security_issues": security_issues,
                "vulnerability_detected": security_vulnerability,
                "input_validated": True,
                "access_controlled": True
            }}
        }}
        
    except Exception as e:
        return {{
            "challenge_type": "security",
            "challenge_name": "{challenge_name}",
            "description": "{description}",
            "expected_failure": True,
            "result": {{
                "error": str(e),
                "handled_gracefully": False
            }}
        }}
'''

    def generate_challenges(
        self, target_hash: str, code: str, challenge_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate challenges for the given code"""
        if challenge_types is None:
            challenge_types = [ct.value for ct in ChallengeType]

        challenges = []

        for challenge_type in challenge_types:
            if challenge_type in self.challenge_templates:
                template = self.challenge_templates[challenge_type]

                # Generate challenge name
                challenge_name = f"{challenge_type}_challenge_{target_hash[:8]}"
                description = (
                    f"Test {challenge_type} handling for code {target_hash[:8]}"
                )

                # Generate challenge code
                challenge_code = template.format(
                    challenge_name=challenge_name, description=description
                )

                # Save challenge
                challenge_file = os.path.join(
                    self.challenges_dir,
                    f"{challenge_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py",
                )

                with open(challenge_file, "w") as f:
                    f.write(challenge_code)

                challenges.append(
                    {
                        "challenge_type": challenge_type,
                        "challenge_name": challenge_name,
                        "description": description,
                        "target_hash": target_hash,
                        "file_path": challenge_file,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return challenges

    def challenge_existing_code(self) -> List[Dict[str, Any]]:
        """Generate challenges for existing code in the toolbox"""
        challenges = []

        # Find existing domain files
        domain_dir = os.path.join(self.toolbox_path, "domain")
        if os.path.exists(domain_dir):
            for file in os.listdir(domain_dir):
                if file.endswith(".py") and file != "__init__.py":
                    domain = file.replace(".py", "")

                    # Generate challenges for each domain
                    domain_challenges = self.generate_challenges(
                        target_hash=f"domain_{domain}",
                        code="",  # We don't have the actual code here
                        challenge_types=["edge_case", "p_hacking", "data_manipulation"],
                    )

                    challenges.extend(domain_challenges)

        return challenges
