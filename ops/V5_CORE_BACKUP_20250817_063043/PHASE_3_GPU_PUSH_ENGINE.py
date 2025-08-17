
# ============================================================================
# PHASE 3 CONSOLIDATED GPU ENGINE
# ============================================================================
# This file consolidates the following Phase 3 scripts:
# PHASE_3_CONTENT_ANALYSIS_OPTIMIZATION.py, PHASE_3_FINAL_PUSH_ENGINE.py, PHASE_3_GPU_ACCELERATION.py, PHASE_3_HYBRID_GENTLE_PUSH_ENGINE.py, PHASE_3_HYBRID_OPTIMIZATION_ENGINE.py, PHASE_3_HYBRID_PURE_PUSH_ENGINE.py, PHASE_3_HYBRID_TURBO_ENGINE.py, PHASE_3_IO_OPTIMIZATION_ENGINE.py, PHASE_3_MEMORY_MANAGEMENT.py, PHASE_3_PARALLEL_PROCESSING_ENGINE_FIXED.py, PHASE_3_PARALLEL_PROCESSING_ENGINE.py, PHASE_3_PERFORMANCE_BASELINE_SIMPLE.py, PHASE_3_PERFORMANCE_BASELINE.py, PHASE_3_SMART_OPTIMIZATION_ENGINE.py, PHASE_3_ULTIMATE_10K_PUSH.py, PHASE_3_ULTRA_TURBO_V5_UPGRADE.py
# 
# Consolidated on: 2025-08-17 05:44:30
# ============================================================================

#!/usr/bin/env python3
"""
PHASE 3 GPU PUSH ENGINE
GPU-Focused Optimization for 10K+ Files/sec

This engine focuses on maximizing GPU utilization while maintaining
the working hybrid approach that achieved 7,973 files/sec.
"""

import os
import time
import hashlib
import re
import json
import mmap
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
from datetime import datetime
from typing import Dict, List, Any, Optional
import torch
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define missing enums and classes
class AgentState:
    IDLE = "idle"
    THINKING = "thinking"
    ERROR = "error"

class AgentBelief:
    def __init__(self, belief_id: str, content: str, confidence: float = 0.5):
        self.belief_id = belief_id
        self.content = content
        self.confidence = confidence

class AgentMemory:
    def __init__(self, memory_id: str, content: str, timestamp: str):
        self.memory_id = memory_id
        self.content = content
        self.timestamp = timestamp

class AgentSimulator:
    """
    Agent simulation and verification system.
    
    Provides paradox resolution, belief updating, and agent interaction simulation.
    """
    
    def __init__(self, agent_id: str, personality: Dict[str, Any] = None):
        """
        Initialize agent simulator.
        
        Args:
            agent_id: Unique identifier for the agent
            personality: Agent personality configuration
        """
        self.agent_id = agent_id
        self.personality = personality or {}
        self.state = AgentState.IDLE
        self.beliefs: List[AgentBelief] = []
        self.memories: List[AgentMemory] = []
        self.interactions: List[Dict[str, Any]] = []
        self.paradoxes: List[Dict[str, Any]] = []
        
        logger.info(f"Agent simulator initialized for {agent_id}")
    
    def simulate_response(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Simulate agent response to a prompt.
        
        Args:
            prompt: Input prompt
            context: Additional context
            
        Returns:
            Simulated response
        """
        try:
            self.state = AgentState.THINKING
            
            # Analyze prompt for contradictions with existing beliefs
            contradictions = self._detect_contradictions(prompt)
            
            # Update beliefs based on new information
            if contradictions:
                self._resolve_paradoxes(contradictions)
            
            # Generate response based on personality and beliefs
            response = self._generate_response(prompt, context)
            
            # Record interaction
            self._record_interaction(prompt, response, contradictions)
            
            self.state = AgentState.IDLE
            
            return {
                "agent_id": self.agent_id,
                "response": response,
                "contradictions": contradictions,
                "beliefs_updated": len(contradictions) > 0,
                "confidence": self._calculate_confidence(response),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            self.state = AgentState.ERROR
            return {
                "agent_id": self.agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _detect_contradictions(self, prompt: str) -> List[Dict[str, Any]]:
        """Detect contradictions with existing beliefs."""
        contradictions = []
        
        for belief in self.beliefs:
            # Simple contradiction detection (can be enhanced)
            if belief.confidence > 0.7:  # High confidence beliefs
                # Check for direct contradictions in prompt
                if self._is_contradictory(prompt, belief.content):
                    contradictions.append({
                        "belief_id": belief.belief_id,
                        "belief_content": belief.content,
                        "prompt_content": prompt,
                        "severity": "high" if belief.confidence > 0.8 else "medium"
                    })
        
        return contradictions
    
    def _is_contradictory(self, prompt: str, belief: str) -> bool:
        """Check if prompt contradicts belief."""
        # Simple contradiction detection (can be enhanced with NLP)
        prompt_lower = prompt.lower()
        belief_lower = belief.lower()
        
        # Check for negation patterns
        negation_words = ["not", "never", "no", "false", "wrong", "incorrect"]
        
        for neg_word in negation_words:
            if neg_word in prompt_lower and neg_word not in belief_lower:
                # Potential contradiction detected
                return True
        
        return False
    
    def _resolve_paradoxes(self, contradictions: List[Dict[str, Any]]):
        """Resolve paradoxes by updating beliefs."""
        for contradiction in contradictions:
            belief_id = contradiction["belief_id"]
            
            # Find the belief
            for belief in self.beliefs:
                if belief.belief_id == belief_id:
                    # Reduce confidence in contradictory belief
                    belief.confidence *= 0.8
                    belief.contradictions.append(contradiction["prompt_content"])
                    
                    # Add new paradox record
                    self.paradoxes.append({
                        "paradox_id": str(uuid.uuid4()),
                        "belief_id": belief_id,
                        "contradiction": contradiction,
                        "resolution": "confidence_reduced",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    logger.info(f"Paradox resolved for belief {belief_id}: confidence reduced to {belief.confidence}")
                    break
    
    def _generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate response based on personality and beliefs."""
        # Simple response generation (can be enhanced with LLM integration)
        
        # Check if we have relevant memories
        relevant_memories = self._get_relevant_memories(prompt)
        
        # Build response based on personality
        personality_traits = self.personality.get("traits", {})
        
        if "analytical" in personality_traits:
            response = f"Analytical response to: {prompt[:50]}..."
        elif "creative" in personality_traits:
            response = f"Creative response to: {prompt[:50]}..."
        else:
            response = f"Standard response to: {prompt[:50]}..."
        
        # Add memory context if available
        if relevant_memories:
            response += f"\n\nBased on {len(relevant_memories)} relevant memories."
        
        return response
    
    def _get_relevant_memories(self, prompt: str) -> List[AgentMemory]:
        """Get relevant memories for the prompt."""
        relevant = []
        prompt_lower = prompt.lower()
        
        for memory in self.memories:
            if memory.importance > 0.5:  # High importance memories
                if any(word in memory.content.lower() for word in prompt_lower.split()):
                    relevant.append(memory)
        
        return sorted(relevant, key=lambda m: m.importance, reverse=True)[:3]
    
    def _record_interaction(self, prompt: str, response: str, contradictions: List[Dict[str, Any]]):
        """Record interaction for learning."""
        interaction = {
            "interaction_id": str(uuid.uuid4()),
            "prompt": prompt,
            "response": response,
            "contradictions": contradictions,
            "timestamp": datetime.now().isoformat(),
            "state": self.state.value
        }
        
        self.interactions.append(interaction)
    
    def _calculate_confidence(self, response: str) -> float:
        """Calculate confidence in the response."""
        # Simple confidence calculation based on response length and complexity
        base_confidence = min(1.0, len(response) / 1000.0)
        
        # Adjust based on number of contradictions
        contradiction_penalty = len(self.paradoxes) * 0.1
        confidence = max(0.1, base_confidence - contradiction_penalty)
        
        return confidence
    
    def add_belief(self, content: str, confidence: float = 0.8, source: str = "simulation") -> str:
        """Add a new belief to the agent."""
        belief_id = str(uuid.uuid4())
        belief = AgentBelief(
            belief_id=belief_id,
            content=content,
            confidence=confidence,
            source=source,
            timestamp=datetime.now().isoformat()
        )
        
        self.beliefs.append(belief)
        logger.info(f"Added belief {belief_id}: {content[:50]}...")
        return belief_id
    
    def add_memory(self, content: str, importance: float = 0.5) -> str:
        """Add a new memory to the agent."""
        memory_id = str(uuid.uuid4())
        memory = AgentMemory(
            memory_id=memory_id,
            content=content,
            importance=importance,
            timestamp=datetime.now().isoformat()
        )
        
        self.memories.append(memory)
        logger.info(f"Added memory {memory_id}: {content[:50]}...")
        return memory_id
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent simulator status."""
        return {
            "agent_id": self.agent_id,
            "state": self.state.value,
            "beliefs_count": len(self.beliefs),
            "memories_count": len(self.memories),
            "interactions_count": len(self.interactions),
            "paradoxes_count": len(self.paradoxes),
            "average_confidence": sum(b.confidence for b in self.beliefs) / len(self.beliefs) if self.beliefs else 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    def export_state(self) -> Dict[str, Any]:
        """Export agent state for persistence."""
        return {
            "agent_id": self.agent_id,
            "personality": self.personality,
            "state": self.state.value,
            "beliefs": [belief.__dict__ for belief in self.beliefs],
            "memories": [memory.__dict__ for memory in self.memories],
            "interactions": self.interactions,
            "paradoxes": self.paradoxes
        }
    
    def load_state(self, state: Dict[str, Any]):
        """Load agent state from persistence."""
        self.agent_id = state.get("agent_id", self.agent_id)
        self.personality = state.get("personality", {})
        self.state = AgentState(state.get("state", "idle"))
        
        # Reconstruct beliefs
        self.beliefs = []
        for belief_data in state.get("beliefs", []):
            belief = AgentBelief(**belief_data)
            self.beliefs.append(belief)
        
        # Reconstruct memories
        self.memories = []
        for memory_data in state.get("memories", []):
            memory = AgentMemory(**memory_data)
            self.memories.append(memory)
        
        self.interactions = state.get("interactions", [])
        self.paradoxes = state.get("paradoxes", [])
        
        logger.info(f"Loaded state for agent {self.agent_id}")

class GPUIntensiveProcessor:
    """GPU-intensive content processor with aggressive tensor operations"""
    
    def __init__(self):
        self.gpu_available = torch.cuda.is_available()
        if self.gpu_available:
            self.device = torch.device('cuda')
            print(f"GPU: {torch.cuda.get_device_name()}")
            print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        else:
            self.device = torch.device('cpu')
            print("GPU not available, using CPU")
        
        # Aggressive GPU settings
        self.gpu_batch_size = 200  # Reduced from 300 for stability
        self.max_tensor_size = 1024  # Reduced from 2048 for stability
        self.gpu_content_threshold = 200  # Increased threshold for stability
        self.max_gpu_operations = 5  # Reduced from 10 for stability
        
        # Pre-compiled regex patterns
        self.patterns = {
            'code_blocks': re.compile(r'[\s\S]*?'),
            'markdown': re.compile(r'[#*\-+>|].*$', re.MULTILINE),
            'log_entries': re.compile(r'\d{4}-\d{2}-\d{2}.*$', re.MULTILINE),
            'text_paragraphs': re.compile(r'[A-Z][.!?]*[.!?]$', re.MULTILINE),
            'numbers': re.compile(r'\b\d+\.?\d*\b'),
            'urls': re.compile(r'https?://[\s]+'),
            'emails': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'ip_addresses': re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
            'hex_values': re.compile(r'\b[0-9a-fA-F]{6,}\b'),
            'json_patterns': re.compile(r'\{[{}]*\}'),
        }
        
        self.total_content_size = 0
        self.content_stats = Counter()
        
    
        # Ensemble system integration
        self.ensemble_system = AgentSimulator()
        self.multi_agent_coordination = True
        self.consensus_building_active = True
    
    def _gpu_intensive_processing(self, content):
        """Perform intensive GPU operations on content"""
        if not self.gpu_available or len(content) < self.gpu_content_threshold:
            return self._cpu_fallback_processing(content)
        
        try:
            # Convert content to tensor with aggressive sizing
            if len(content) > self.max_tensor_size:
                content = content[:self.max_tensor_size]
            
            # Create multiple tensors for batch processing
            tensors = []
            for i in range(0, len(content), self.gpu_batch_size):
                chunk = content[i:i + self.gpu_batch_size]
                # Pad to consistent size
                padded_chunk = chunk.ljust(self.gpu_batch_size, ' ')
                tensor = torch.tensor([ord(c) for c in padded_chunk], 
                                   dtype=torch.float32, device=self.device)
                tensors.append(tensor)
            
            if not tensors:
                return self._cpu_fallback_processing(content)
            
            # Stack tensors for batch processing
            batch_tensor = torch.stack(tensors)
            
            # Perform multiple GPU operations
            results = []
            for _ in range(self.max_gpu_operations):
                # Basic operations
                sum_result = torch.sum(batch_tensor)
                mean_result = torch.mean(batch_tensor)
                std_result = torch.std(batch_tensor)
                var_result = torch.var(batch_tensor)
                max_result = torch.max(batch_tensor)
                min_result = torch.min(batch_tensor)
                median_result = torch.median(batch_tensor)
                
                # Advanced operations
                norm_result = torch.norm(batch_tensor)
                abs_result = torch.abs(batch_tensor)
                sqrt_result = torch.sqrt(torch.abs(batch_tensor))
                
                # Matrix operations (simplified to avoid complex number issues)
                if batch_tensor.shape[0] > 1:
                    transpose_result = torch.transpose(batch_tensor, 0, 1)
                    matmul_result = torch.mm(batch_tensor, transpose_result)
                    # Use only real part of eigenvalues to avoid complex number issues
                    eigenvals = torch.linalg.eigvals(matmul_result)
                    eigenvals_real = torch.real(eigenvals)
                    eigenvals_mean = torch.mean(eigenvals_real)
                else:
                    eigenvals_mean = 0.0
                
                # Aggregate results
                batch_results = {
                    'sum': sum_result.item(),
                    'mean': mean_result.item(),
                    'std': std_result.item(),
                    'var': var_result.item(),
                    'max': max_result.item(),
                    'min': min_result.item(),
                    'median': median_result.item(),
                    'norm': norm_result.item(),
                    'eigenvals_mean': eigenvals_mean.item() if hasattr(eigenvals_mean, 'item') else eigenvals_mean
                }
                results.append(batch_results)
            
            # Calculate final metrics
            final_metrics = {}
            for key in results[0].keys():
                values = [r[key] for r in results]
                final_metrics[f'{key}_mean'] = np.mean(values)
                final_metrics[f'{key}_std'] = np.std(values)
                final_metrics[f'{key}_min'] = min(values)
                final_metrics[f'{key}_max'] = max(values)
            
            return final_metrics
            
        except Exception as e:
            # Don't print every GPU error to avoid spam
            if hasattr(self, '_error_count'):
                self._error_count += 1
                if self._error_count <= 5:  # Only print first 5 errors
                    print(f"GPU processing error: {e}")
                elif self._error_count == 6:
                    print("GPU processing errors continuing... (suppressing further error messages)")
            else:
                self._error_count = 1
                print(f"GPU processing error: {e}")
            return self._cpu_fallback_processing(content)
    
    def _cpu_fallback_processing(self, content):
        """CPU fallback for when GPU processing fails"""
        return {
            'cpu_sum': sum(ord(c) for c in content),
            'cpu_length': len(content),
            'cpu_hash': hashlib.md5(content.encode()).hexdigest()[:8]
        }
    
    def _analyze_content_intensive(self, file_path):
        """Intensive content analysis with aggressive GPU usage"""
        try:
            file_size = os.path.getsize(file_path)
            
            # Determine processing strategy based on file size
            if file_size < 1024:  # <1KB
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                processing_method = "direct"
                
            elif file_size < 1024 * 1024:  # <1MB
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        content = mm.read().decode('utf-8', errors='ignore')
                processing_method = "mmap"
                
            else:  # >=1MB
                # Stream processing for large files
                content = ""
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f):
                        if i >= 1000:  # Limit to first 1000 lines
                            break
                        content += line
                processing_method = "stream"
            
            # Update stats
            self.total_content_size += len(content)
            self.content_stats[processing_method] += 1
            
            # Perform intensive GPU processing
            gpu_results = self._gpu_intensive_processing(content)
            
            # Additional CPU analysis
            analysis_results = {
                'file_size': file_size,
                'content_length': len(content),
                'processing_method': processing_method,
                'word_count': len(content.split()),
                'line_count': content.count('\n') + 1,
                'gpu_metrics': gpu_results
            }
            
            # Pattern matching
            for pattern_name, pattern in self.patterns.items():
                matches = pattern.findall(content)
                analysis_results[f'{pattern_name}_count'] = len(matches)
            
            # Hash analysis
            analysis_results['md5_hash'] = hashlib.md5(content.encode()).hexdigest()
            analysis_results['sha256_hash'] = hashlib.sha256(content.encode()).hexdigest()
            
            return analysis_results
            
        except Exception as e:
            return {
                'error': str(e),
                'file_size': 0,
                'content_length': 0,
                'processing_method': 'error'
            }

class GPUIntensiveParallelProcessor:
    """Parallel processor with GPU-intensive operations"""
    
    def __init__(self, max_workers=None):
        if max_workers is None:
            # Aggressive worker scaling
            self.max_workers = min(28, (os.cpu_count() or 1) + 12)
        else:
            self.max_workers = max_workers
        
        self.processor = GPUIntensiveProcessor()
        self.batch_size = 1500  # Increased from 1200
        
        print(f"GPU-Intensive Parallel Processor initialized:")
        print(f"  Max Workers: {self.max_workers}")
        print(f"  Batch Size: {self.batch_size}")
        print(f"  GPU Batch Size: {self.processor.gpu_batch_size}")
        print(f"  Max Tensor Size: {self.processor.max_tensor_size}")
    
    def process_files(self, file_paths):
        """Process files in parallel with GPU-intensive operations"""
        start_time = time.time()
        total_files = len(file_paths)
        processed_files = 0
        
        print(f"Starting GPU-intensive processing of {total_files} files...")
        print(f"Using {self.max_workers} workers with batch size {self.batch_size}")
        
        # Process in batches
        for i in range(0, total_files, self.batch_size):
            batch = file_paths[i:i + self.batch_size]
            batch_start = time.time()
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit batch for processing
                future_to_file = {
                    executor.submit(self.processor._analyze_content_intensive, file_path): file_path 
                    for file_path in batch
                }
                
                # Process completed tasks
                batch_processed = 0
                for future in as_completed(future_to_file):
                    try:
                        result = future.result()
                        batch_processed += 1
                        
                        # Progress update
                        if batch_processed % 100 == 0:
                            elapsed = time.time() - batch_start
                            rate = batch_processed / elapsed if elapsed > 0 else 0
                            print(f"  Batch progress: {batch_processed}/{len(batch)} files "
                                  f"({rate:.1f} files/sec)")
                            
                    except Exception as e:
                        print(f"Error processing file: {e}")
            
            processed_files += len(batch)
            batch_time = time.time() - batch_start
            batch_rate = len(batch) / batch_time if batch_time > 0 else 0
            
            print(f"Batch {i//self.batch_size + 1} completed: "
                  f"{len(batch)} files in {batch_time:.2f}s ({batch_rate:.1f} files/sec)")
        
        total_time = time.time() - start_time
        overall_rate = total_files / total_time if total_time > 0 else 0
        
        print(f"\nGPU-Intensive Processing Complete:")
        print(f"  Total Files: {total_files}")
        print(f"  Total Time: {total_time:.3f}s")
        print(f"  Overall Rate: {overall_rate:.1f} files/sec")
        print(f"  Total Content: {self.processor.total_content_size / 1024 / 1024:.2f} MB")
        
        return {
            'total_files': total_files,
            'total_time': total_time,
            'files_per_sec': overall_rate,
            'total_content_mb': self.processor.total_content_size / 1024 / 1024,
            'processing_stats': dict(self.processor.content_stats)
        }

class GPUIntensiveTestEngine:
    """Test engine for GPU-intensive optimization"""
    
    def __init__(self):
        self.baseline_speed = 7973  # From hybrid optimization
        self.target_speed = 10000   # Phase 1 completion target
        
    def collect_test_files(self, num_files=50000):
        """Collect test files from archive and cleanup folders"""
        test_dirs = [
            'archive',
            'archive/obsolete_md_files',
            'archive/testing_artifacts',
            'archive/system_backups'
        ]
        
        all_files = []
        for test_dir in test_dirs:
            if os.path.exists(test_dir):
                for root, dirs, files in os.walk(test_dir):
                    for file in files:
                        if file.endswith(('.md', '.txt', '.py', '.json', '.ps1', '.bat')):
                            file_path = os.path.join(root, file)
                            all_files.append(file_path)
        
        # Limit to requested number of files
        if len(all_files) > num_files:
            all_files = all_files[:num_files]
        
        print(f"Collected {len(all_files)} test files")
        return all_files
    
    def run_gpu_intensive_test(self, num_files=50000):
        """Run the GPU-intensive optimization test"""
        print("=" * 60)
        print("PHASE 3 GPU-INTENSIVE OPTIMIZATION TEST")
        print("=" * 60)
        print(f"Target: {self.target_speed:,} files/sec")
        print(f"Baseline: {self.baseline_speed:,} files/sec")
        print(f"Files to process: {num_files:,}")
        print()
        
        # Collect test files
        test_files = self.collect_test_files(num_files)
        if not test_files:
            print("No test files found!")
            return
        
        # Initialize processor
        processor = GPUIntensiveParallelProcessor()
        
        # Run test
        start_time = time.time()
        results = processor.process_files(test_files)
        total_time = time.time() - start_time
        
        # Calculate improvement
        improvement = ((results['files_per_sec'] - self.baseline_speed) / 
                      self.baseline_speed * 100)
        
        # Display results
        print("\n" + "=" * 60)
        print("GPU-INTENSIVE OPTIMIZATION RESULTS")
        print("=" * 60)
        print(f"Files Processed: {results['total_files']:,}")
        print(f"Total Time: {results['total_time']:.3f}s")
        print(f"Processing Rate: {results['files_per_sec']:,.1f} files/sec")
        print(f"Content Processed: {results['total_content_mb']:.2f} MB")
        print(f"Baseline Speed: {self.baseline_speed:,} files/sec")
        print(f"Improvement: {improvement:+.1f}%")
        print(f"Target Met: {'YES' if results['files_per_sec'] >= self.target_speed else 'NO'}")
        
        # Processing stats
        print(f"\nProcessing Methods:")
        for method, count in results['processing_stats'].items():
            print(f"  {method}: {count:,} files")
        
        # Performance analysis
        if results['files_per_sec'] >= self.target_speed:
            print(f"\n TARGET ACHIEVED! GPU optimization successful!")
        elif improvement > 0:
            print(f"\n Improvement achieved: {improvement:+.1f}%")
        else:
            print(f"\n Performance regression: {improvement:+.1f}%")
        
        return results

def main():
    """Main execution function"""
    print("PHASE 3 GPU-INTENSIVE OPTIMIZATION ENGINE")
    print("Focusing on maximum GPU utilization for 10K+ files/sec")
    print()
    
    # Check GPU availability
    if not torch.cuda.is_available():
        print("WARNING: CUDA not available. GPU optimizations will be limited.")
        print("Consider installing PyTorch with CUDA support.")
        print()
    
    # Initialize test engine
    engine = GPUIntensiveTestEngine()
    
    # Run test
    try:
        results = engine.run_gpu_intensive_test(50000)
        
        # Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"ops/test_output/phase3_performance/phase3_gpu_intensive_results_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        
        # Save results
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {results_file}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
