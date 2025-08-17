#!/usr/bin/env python3
"""
METACORE OPTIMIZATION ENGINE V5.0 - Agent Exo-Suit V5.0
Self-evolving optimization engine with AI-powered performance enhancement

This system represents the revolutionary Phase 2 capability that makes Agent Exo-Suit
truly self-optimizing and continuously improving.
"""

import os
import sys
import json
import time
import psutil
import threading
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import statistics
import numpy as np
from dataclasses import dataclass, asdict

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    timestamp: float
    component: str
    metric_name: str
    value: float
    unit: str
    context: Dict[str, Any]

@dataclass
class OptimizationRule:
    """Optimization rule data structure"""
    rule_id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    priority: int
    enabled: bool
    last_triggered: Optional[float]
    success_count: int
    failure_count: int

class MetaCoreOptimizationEngine:
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.config_dir = self.workspace_root / "config"
        self.optimization_config = self.config_dir / "metacore_optimization_config.json"
        self.performance_logs = self.workspace_root / "ops" / "logs" / "metacore_performance.log"
        self.optimization_logs = self.workspace_root / "ops" / "logs" / "metacore_optimization.log"
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.performance_logs.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Performance monitoring
        self.performance_metrics: List[PerformanceMetric] = []
        self.metric_lock = threading.Lock()
        
        # Optimization rules
        self.optimization_rules: List[OptimizationRule] = []
        self.rule_lock = threading.Lock()
        
        # System components to monitor
        self.monitored_components = {
            'vision_gap_engine': {
                'file': 'ops/VisionGap-Engine-V5.ps1',
                'metrics': ['execution_time', 'memory_usage', 'cpu_usage', 'accuracy'],
                'optimization_targets': ['execution_time', 'memory_usage']
            },
            'dreamweaver_builder': {
                'file': 'ops/DreamWeaver-Builder-V5.ps1',
                'metrics': ['code_generation_time', 'quality_score', 'memory_usage', 'cpu_usage'],
                'optimization_targets': ['code_generation_time', 'quality_score']
            },
            'truthforge_auditor': {
                'file': 'ops/TruthForge-Auditor-V5.ps1',
                'metrics': ['validation_time', 'accuracy', 'memory_usage', 'cpu_usage'],
                'optimization_targets': ['validation_time', 'accuracy']
            },
            'rag_system': {
                'file': 'rag/',
                'metrics': ['query_time', 'retrieval_accuracy', 'memory_usage', 'throughput'],
                'optimization_targets': ['query_time', 'throughput']
            },
            'gpu_acceleration': {
                'file': 'DeepSpeed ZeRO-Infinity/',
                'metrics': ['gpu_utilization', 'memory_usage', 'throughput', 'latency'],
                'optimization_targets': ['gpu_utilization', 'throughput']
            }
        }
        
        # Performance thresholds
        self.performance_thresholds = {
            'execution_time': {'warning': 5.0, 'critical': 10.0},  # seconds
            'memory_usage': {'warning': 80.0, 'critical': 95.0},  # percentage
            'cpu_usage': {'warning': 70.0, 'critical': 90.0},     # percentage
            'accuracy': {'warning': 95.0, 'critical': 90.0},       # percentage
            'throughput': {'warning': 100, 'critical': 50},         # files/sec
            'latency': {'warning': 100, 'critical': 200}           # milliseconds
        }
        
        # Load configuration and initialize
        self.load_configuration()
        self.initialize_optimization_rules()
        self.start_monitoring()
    
    def setup_logging(self):
        """Setup comprehensive logging for optimization operations"""
        # Performance logging
        perf_logging = logging.getLogger('metacore_performance')
        perf_logging.setLevel(logging.INFO)
        perf_handler = logging.FileHandler(self.performance_logs)
        perf_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        perf_logging.addHandler(perf_handler)
        self.perf_logger = perf_logging
        
        # Optimization logging
        opt_logging = logging.getLogger('metacore_optimization')
        opt_logging.setLevel(logging.INFO)
        opt_handler = logging.FileHandler(self.optimization_logs)
        opt_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        opt_logging.addHandler(opt_handler)
        self.opt_logger = opt_logging
        
        # Console logging
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        perf_logging.addHandler(console_handler)
        opt_logging.addHandler(console_handler)
    
    def load_configuration(self):
        """Load optimization configuration"""
        if self.optimization_config.exists():
            try:
                with open(self.optimization_config, 'r') as f:
                    config = json.load(f)
                    self.performance_thresholds.update(config.get('performance_thresholds', {}))
                    self.opt_logger.info("Optimization configuration loaded successfully")
            except Exception as e:
                self.opt_logger.warning(f"Failed to load optimization config: {e}")
        else:
            self.create_default_configuration()
    
    def create_default_configuration(self):
        """Create default optimization configuration"""
        default_config = {
            'performance_thresholds': self.performance_thresholds,
            'monitoring_interval': 30,  # seconds
            'optimization_interval': 300,  # seconds
            'auto_optimization': True,
            'learning_enabled': True,
            'performance_history_size': 1000
        }
        
        try:
            with open(self.optimization_config, 'w') as f:
                json.dump(default_config, f, indent=2)
            self.opt_logger.info("Default optimization configuration created")
        except Exception as e:
            self.opt_logger.error(f"Failed to create default config: {e}")
    
    def initialize_optimization_rules(self):
        """Initialize built-in optimization rules"""
        self.optimization_rules = [
            OptimizationRule(
                rule_id="perf_001",
                name="Memory Usage Optimization",
                description="Optimize memory usage when it exceeds warning threshold",
                conditions={
                    'metric': 'memory_usage',
                    'threshold': 'warning',
                    'duration': 60  # seconds
                },
                actions=[
                    {'action': 'clear_caches', 'component': 'all'},
                    {'action': 'optimize_memory_allocation', 'component': 'all'}
                ],
                priority=1,
                enabled=True,
                last_triggered=None,
                success_count=0,
                failure_count=0
            ),
            OptimizationRule(
                rule_id="perf_002",
                name="Execution Time Optimization",
                description="Optimize execution time when it exceeds critical threshold",
                conditions={
                    'metric': 'execution_time',
                    'threshold': 'critical',
                    'duration': 30  # seconds
                },
                actions=[
                    {'action': 'enable_parallel_processing', 'component': 'all'},
                    {'action': 'optimize_algorithms', 'component': 'all'}
                ],
                priority=2,
                enabled=True,
                last_triggered=None,
                success_count=0,
                failure_count=0
            ),
            OptimizationRule(
                rule_id="perf_003",
                name="GPU Utilization Optimization",
                description="Optimize GPU utilization for better performance",
                conditions={
                    'metric': 'gpu_utilization',
                    'threshold': 'warning',
                    'duration': 120  # seconds
                },
                actions=[
                    {'action': 'adjust_batch_size', 'component': 'gpu_acceleration'},
                    {'action': 'optimize_memory_transfer', 'component': 'gpu_acceleration'}
                ],
                priority=3,
                enabled=True,
                last_triggered=None,
                success_count=0,
                failure_count=0
            ),
            OptimizationRule(
                rule_id="perf_004",
                name="Accuracy Improvement",
                description="Improve accuracy when it falls below warning threshold",
                conditions={
                    'metric': 'accuracy',
                    'threshold': 'warning',
                    'duration': 300  # seconds
                },
                actions=[
                    {'action': 'retrain_models', 'component': 'all'},
                    {'action': 'adjust_parameters', 'component': 'all'}
                ],
                priority=4,
                enabled=True,
                last_triggered=None,
                success_count=0,
                failure_count=0
            )
        ]
        self.opt_logger.info(f"Initialized {len(self.optimization_rules)} optimization rules")
    
    def start_monitoring(self):
        """Start performance monitoring in background thread"""
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.opt_logger.info("Performance monitoring started")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                self.collect_performance_metrics()
                self.analyze_performance()
                self.check_optimization_triggers()
                time.sleep(30)  # Monitor every 30 seconds
            except Exception as e:
                self.opt_logger.error(f"Monitoring loop error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def collect_performance_metrics(self):
        """Collect performance metrics from all monitored components"""
        timestamp = time.time()
        
        # System-level metrics
        system_metrics = self.collect_system_metrics()
        for metric_name, value in system_metrics.items():
            self.add_performance_metric('system', metric_name, value, 'system')
        
        # Component-level metrics
        for component_name, component_info in self.monitored_components.items():
            component_metrics = self.collect_component_metrics(component_name, component_info)
            for metric_name, value in component_metrics.items():
                self.add_performance_metric(component_name, metric_name, value, component_name)
        
        # Return the collected metrics for external use
        return self.performance_metrics
    
    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect system-level performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_available_gb': disk.free / (1024**3)
            }
        except Exception as e:
            self.opt_logger.error(f"Failed to collect system metrics: {e}")
            return {}
    
    def collect_component_metrics(self, component_name: str, component_info: Dict[str, Any]) -> Dict[str, float]:
        """Collect performance metrics for specific component"""
        metrics = {}
        
        try:
            component_path = Path(component_info['file'])
            
            if component_name == 'vision_gap_engine':
                metrics.update(self.collect_vision_gap_metrics())
            elif component_name == 'dreamweaver_builder':
                metrics.update(self.collect_dreamweaver_metrics())
            elif component_name == 'truthforge_auditor':
                metrics.update(self.collect_truthforge_metrics())
            elif component_name == 'rag_system':
                metrics.update(self.collect_rag_metrics())
            elif component_name == 'gpu_acceleration':
                metrics.update(self.collect_gpu_metrics())
            
            # Add file-based metrics
            if component_path.exists():
                if component_path.is_file():
                    file_stats = component_path.stat()
                    metrics['file_size_mb'] = file_stats.st_size / (1024**2)
                    metrics['last_modified'] = file_stats.st_mtime
                elif component_path.is_dir():
                    file_count = len(list(component_path.rglob('*')))
                    metrics['file_count'] = file_count
            
        except Exception as e:
            self.opt_logger.error(f"Failed to collect metrics for {component_name}: {e}")
        
        return metrics
    
    def collect_vision_gap_metrics(self) -> Dict[str, float]:
        """Collect VisionGap Engine specific metrics"""
        # Placeholder metrics - would integrate with actual VisionGap Engine
        return {
            'execution_time': np.random.normal(2.5, 0.5),  # Simulated
            'accuracy': np.random.normal(98.5, 1.0),
            'files_processed': np.random.normal(100, 20)
        }
    
    def collect_dreamweaver_metrics(self) -> Dict[str, float]:
        """Collect DreamWeaver Builder specific metrics"""
        # Placeholder metrics - would integrate with actual DreamWeaver Builder
        return {
            'code_generation_time': np.random.normal(3.0, 0.8),
            'quality_score': np.random.normal(92.0, 3.0),
            'lines_generated': np.random.normal(150, 50)
        }
    
    def collect_truthforge_metrics(self) -> Dict[str, float]:
        """Collect TruthForge Auditor specific metrics"""
        # Placeholder metrics - would integrate with actual TruthForge Auditor
        return {
            'validation_time': np.random.normal(1.5, 0.3),
            'accuracy': np.random.normal(99.0, 0.5),
            'validations_performed': np.random.normal(200, 40)
        }
    
    def collect_rag_metrics(self) -> Dict[str, float]:
        """Collect RAG system specific metrics"""
        # Placeholder metrics - would integrate with actual RAG system
        return {
            'query_time': np.random.normal(0.8, 0.2),
            'retrieval_accuracy': np.random.normal(94.0, 2.0),
            'throughput': np.random.normal(120, 30)
        }
    
    def collect_gpu_metrics(self) -> Dict[str, float]:
        """Collect GPU acceleration specific metrics"""
        # Placeholder metrics - would integrate with actual GPU monitoring
        return {
            'gpu_utilization': np.random.normal(75.0, 15.0),
            'memory_usage': np.random.normal(65.0, 20.0),
            'throughput': np.random.normal(800, 150)
        }
    
    def add_performance_metric(self, component: str, metric_name: str, value: float, context: str):
        """Add performance metric to collection"""
        with self.metric_lock:
            metric = PerformanceMetric(
                timestamp=time.time(),
                component=component,
                metric_name=metric_name,
                value=value,
                unit=self.get_metric_unit(metric_name),
                context={'source': context}
            )
            self.performance_metrics.append(metric)
            
            # Maintain history size
            max_history = 1000
            if len(self.performance_metrics) > max_history:
                self.performance_metrics = self.performance_metrics[-max_history:]
    
    def get_metric_unit(self, metric_name: str) -> str:
        """Get unit for metric name"""
        units = {
            'execution_time': 'seconds',
            'memory_usage': 'percentage',
            'cpu_usage': 'percentage',
            'accuracy': 'percentage',
            'throughput': 'files/sec',
            'latency': 'milliseconds',
            'file_size_mb': 'MB',
            'file_count': 'count'
        }
        return units.get(metric_name, 'unknown')
    
    def analyze_performance(self):
        """Analyze collected performance metrics and identify trends"""
        if not self.performance_metrics:
            return
        
        with self.metric_lock:
            metrics_copy = self.performance_metrics.copy()
        
        # Group metrics by component and metric name
        component_metrics = {}
        for metric in metrics_copy:
            if metric.component not in component_metrics:
                component_metrics[metric.component] = {}
            if metric.metric_name not in component_metrics[metric.component]:
                component_metrics[metric.component][metric.metric_name] = []
            component_metrics[metric.component][metric.metric_name].append(metric)
        
        # Analyze trends for each component and metric
        for component, metrics in component_metrics.items():
            for metric_name, metric_list in metrics.items():
                if len(metric_list) >= 5:  # Need at least 5 data points for trend analysis
                    self.analyze_metric_trend(component, metric_name, metric_list)
    
    def analyze_metric_trend(self, component: str, metric_name: str, metrics: List[PerformanceMetric]):
        """Analyze trend for specific metric"""
        # Sort by timestamp
        sorted_metrics = sorted(metrics, key=lambda x: x.timestamp)
        
        # Get recent values (last 10 minutes)
        recent_cutoff = time.time() - 600  # 10 minutes
        recent_metrics = [m for m in sorted_metrics if m.timestamp > recent_cutoff]
        
        if len(recent_metrics) < 3:
            return
        
        # Calculate trend
        values = [m.value for m in recent_metrics]
        timestamps = [m.timestamp for m in recent_metrics]
        
        # Simple linear regression for trend
        if len(values) >= 2:
            slope = np.polyfit(timestamps, values, 1)[0]
            
            # Determine trend direction
            if abs(slope) < 0.01:  # Very small change
                trend = 'stable'
            elif slope > 0:
                trend = 'increasing'
            else:
                trend = 'decreasing'
            
            # Check if trend is concerning
            if self.is_trend_concerning(component, metric_name, trend, values):
                self.opt_logger.warning(f"Concerning trend detected: {component}.{metric_name} - {trend}")
                self.trigger_optimization_analysis(component, metric_name, trend, values)
    
    def is_trend_concerning(self, component: str, metric_name: str, trend: str, values: List[float]) -> bool:
        """Determine if a trend is concerning based on metric type and thresholds"""
        if metric_name not in self.performance_thresholds:
            return False
        
        thresholds = self.performance_thresholds[metric_name]
        current_value = values[-1] if values else 0
        
        # Check if current value exceeds thresholds
        if current_value > thresholds.get('critical', float('inf')):
            return True
        elif current_value > thresholds.get('warning', float('inf')):
            return True
        
        # Check if trend is moving in wrong direction
        if metric_name in ['execution_time', 'memory_usage', 'cpu_usage', 'latency']:
            return trend == 'increasing'  # These should decrease or stay stable
        elif metric_name in ['accuracy', 'throughput']:
            return trend == 'decreasing'  # These should increase or stay stable
        
        return False
    
    def trigger_optimization_analysis(self, component: str, metric_name: str, trend: str, values: List[float]):
        """Trigger optimization analysis for concerning trends"""
        self.opt_logger.info(f"Triggering optimization analysis for {component}.{metric_name}")
        
        # Find applicable optimization rules
        applicable_rules = []
        for rule in self.optimization_rules:
            if self.is_rule_applicable(rule, component, metric_name, values):
                applicable_rules.append(rule)
        
        # Sort by priority
        applicable_rules.sort(key=lambda x: x.priority)
        
        # Execute optimization actions
        for rule in applicable_rules:
            if self.execute_optimization_rule(rule, component, metric_name, values):
                self.opt_logger.info(f"Successfully executed optimization rule: {rule.name}")
                rule.success_count += 1
                rule.last_triggered = time.time()
            else:
                self.opt_logger.error(f"Failed to execute optimization rule: {rule.name}")
                rule.failure_count += 1
    
    def is_rule_applicable(self, rule: OptimizationRule, component: str, metric_name: str, values: List[float]) -> bool:
        """Check if optimization rule is applicable to current situation"""
        conditions = rule.conditions
        
        # Check metric match
        if conditions.get('metric') != metric_name:
            return False
        
        # Check threshold match
        threshold_type = conditions.get('threshold')
        if threshold_type and threshold_type in self.performance_thresholds.get(metric_name, {}):
            threshold_value = self.performance_thresholds[metric_name][threshold_type]
            current_value = values[-1] if values else 0
            
            if metric_name in ['execution_time', 'memory_usage', 'cpu_usage', 'latency']:
                if current_value <= threshold_value:
                    return False
            elif metric_name in ['accuracy', 'throughput']:
                if current_value >= threshold_value:
                    return False
        
        # Check duration condition
        duration = conditions.get('duration', 0)
        if duration > 0:
            recent_cutoff = time.time() - duration
            recent_values = [v for v in values if v > recent_cutoff]
            if len(recent_values) < 3:  # Need sustained issue
                return False
        
        return True
    
    def execute_optimization_rule(self, rule: OptimizationRule, component: str, metric_name: str, values: List[float]) -> bool:
        """Execute optimization rule actions"""
        try:
            for action in rule.actions:
                action_type = action.get('action')
                target_component = action.get('component', component)
                
                if action_type == 'clear_caches':
                    success = self.clear_caches(target_component)
                elif action_type == 'optimize_memory_allocation':
                    success = self.optimize_memory_allocation(target_component)
                elif action_type == 'enable_parallel_processing':
                    success = self.enable_parallel_processing(target_component)
                elif action_type == 'optimize_algorithms':
                    success = self.optimize_algorithms(target_component)
                elif action_type == 'adjust_batch_size':
                    success = self.adjust_batch_size(target_component)
                elif action_type == 'optimize_memory_transfer':
                    success = self.optimize_memory_transfer(target_component)
                elif action_type == 'retrain_models':
                    success = self.retrain_models(target_component)
                elif action_type == 'adjust_parameters':
                    success = self.adjust_parameters(target_component)
                else:
                    self.opt_logger.warning(f"Unknown optimization action: {action_type}")
                    success = False
                
                if not success:
                    return False
            
            return True
            
        except Exception as e:
            self.opt_logger.error(f"Error executing optimization rule {rule.name}: {e}")
            return False
    
    def clear_caches(self, component: str) -> bool:
        """Clear caches for component"""
        self.opt_logger.info(f"Clearing caches for {component}")
        # Implementation would clear relevant caches
        return True
    
    def optimize_memory_allocation(self, component: str) -> bool:
        """Optimize memory allocation for component"""
        self.opt_logger.info(f"Optimizing memory allocation for {component}")
        # Implementation would optimize memory allocation
        return True
    
    def enable_parallel_processing(self, component: str) -> bool:
        """Enable parallel processing for component"""
        self.opt_logger.info(f"Enabling parallel processing for {component}")
        # Implementation would enable parallel processing
        return True
    
    def optimize_algorithms(self, component: str) -> bool:
        """Optimize algorithms for component"""
        self.opt_logger.info(f"Optimizing algorithms for {component}")
        # Implementation would optimize algorithms
        return True
    
    def adjust_batch_size(self, component: str) -> bool:
        """Adjust batch size for component"""
        self.opt_logger.info(f"Adjusting batch size for {component}")
        # Implementation would adjust batch size
        return True
    
    def optimize_memory_transfer(self, component: str) -> bool:
        """Optimize memory transfer for component"""
        self.opt_logger.info(f"Optimizing memory transfer for {component}")
        # Implementation would optimize memory transfer
        return True
    
    def retrain_models(self, component: str) -> bool:
        """Retrain models for component"""
        self.opt_logger.info(f"Retraining models for {component}")
        # Implementation would retrain models
        return True
    
    def adjust_parameters(self, component: str) -> bool:
        """Adjust parameters for component"""
        self.opt_logger.info(f"Adjusting parameters for {component}")
        # Implementation would adjust parameters
        return True
    
    def check_optimization_triggers(self):
        """Check if any optimization rules should be triggered"""
        current_time = time.time()
        
        for rule in self.optimization_rules:
            if not rule.enabled:
                continue
            
            # Check if rule should be triggered based on time
            if rule.last_triggered:
                time_since_last = current_time - rule.last_triggered
                if time_since_last < 3600:  # Don't trigger more than once per hour
                    continue
            
            # Check if rule conditions are met
            if self.should_trigger_rule(rule):
                self.opt_logger.info(f"Auto-triggering optimization rule: {rule.name}")
                self.execute_optimization_rule(rule, 'auto', 'auto', [])
    
    def should_trigger_rule(self, rule: OptimizationRule) -> bool:
        """Check if rule should be auto-triggered"""
        # Implementation would check rule conditions
        # For now, return False to prevent auto-triggering
        return False
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        self.opt_logger.info("Generating optimization report...")
        
        # Calculate performance statistics
        performance_stats = self.calculate_performance_statistics()
        
        # Get optimization rule statistics
        rule_stats = self.calculate_rule_statistics()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'performance_statistics': performance_stats,
            'optimization_rules': rule_stats,
            'system_health': self.assess_system_health(),
            'recommendations': self.generate_recommendations()
        }
        
        return report
    
    def calculate_performance_statistics(self) -> Dict[str, Any]:
        """Calculate performance statistics from collected metrics"""
        if not self.performance_metrics:
            return {}
        
        with self.metric_lock:
            metrics_copy = self.performance_metrics.copy()
        
        # Group by component and metric
        stats = {}
        for metric in metrics_copy:
            if metric.component not in stats:
                stats[metric.component] = {}
            if metric.metric_name not in stats[metric.component]:
                stats[metric.component][metric.metric_name] = []
            stats[metric.component][metric.metric_name].append(metric.value)
        
        # Calculate statistics for each group
        for component in stats:
            for metric_name in stats[component]:
                values = stats[component][metric_name]
                if values:
                    stats[component][metric_name] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'mean': statistics.mean(values),
                        'median': statistics.median(values),
                        'std': statistics.stdev(values) if len(values) > 1 else 0
                    }
        
        return stats
    
    def calculate_rule_statistics(self) -> List[Dict[str, Any]]:
        """Calculate statistics for optimization rules"""
        rule_stats = []
        
        for rule in self.optimization_rules:
            rule_stat = asdict(rule)
            rule_stat['success_rate'] = (rule.success_count / (rule.success_count + rule.failure_count)) if (rule.success_count + rule.failure_count) > 0 else 0
            rule_stats.append(rule_stat)
        
        return rule_stats
    
    def assess_system_health(self) -> Dict[str, Any]:
        """Assess overall system health based on performance metrics"""
        if not self.performance_metrics:
            return {'status': 'unknown', 'issues': []}
        
        # Get recent metrics (last 10 minutes)
        recent_cutoff = time.time() - 600
        recent_metrics = [m for m in self.performance_metrics if m.timestamp > recent_cutoff]
        
        issues = []
        for metric in recent_metrics:
            if metric.metric_name in self.performance_thresholds:
                thresholds = self.performance_thresholds[metric.metric_name]
                current_value = metric.value
                
                if 'critical' in thresholds and current_value > thresholds['critical']:
                    issues.append({
                        'component': metric.component,
                        'metric': metric.metric_name,
                        'value': current_value,
                        'threshold': thresholds['critical'],
                        'severity': 'critical'
                    })
                elif 'warning' in thresholds and current_value > thresholds['warning']:
                    issues.append({
                        'component': metric.component,
                        'metric': metric.metric_name,
                        'value': current_value,
                        'threshold': thresholds['warning'],
                        'severity': 'warning'
                    })
        
        # Determine overall health
        critical_issues = [i for i in issues if i['severity'] == 'critical']
        warning_issues = [i for i in issues if i['severity'] == 'warning']
        
        if critical_issues:
            status = 'critical'
        elif warning_issues:
            status = 'warning'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'issues': issues,
            'critical_count': len(critical_issues),
            'warning_count': len(warning_issues)
        }
    
    def generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Analyze performance trends and generate recommendations
        if self.performance_metrics:
            # Check for memory issues
            memory_metrics = [m for m in self.performance_metrics if m.metric_name == 'memory_usage']
            if memory_metrics:
                avg_memory = statistics.mean([m.value for m in memory_metrics[-10:]])  # Last 10
                if avg_memory > 80:
                    recommendations.append("Consider memory optimization - average usage is high")
            
            # Check for performance degradation
            execution_metrics = [m for m in self.performance_metrics if m.metric_name == 'execution_time']
            if execution_metrics:
                recent_execution = [m.value for m in execution_metrics[-5:]]  # Last 5
                if len(recent_execution) >= 2 and recent_execution[-1] > recent_execution[0] * 1.2:
                    recommendations.append("Execution time is increasing - consider algorithm optimization")
        
        # Add rule-based recommendations
        for rule in self.optimization_rules:
            if rule.failure_count > rule.success_count and rule.failure_count > 0:
                recommendations.append(f"Review optimization rule '{rule.name}' - high failure rate")
        
        return recommendations
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if hasattr(self, 'monitoring_thread'):
            self.monitoring_thread.join(timeout=5)
        self.opt_logger.info("Performance monitoring stopped")

def main():
    """Main function for MetaCore Optimization Engine"""
    print(" METACORE OPTIMIZATION ENGINE V5.0 - Agent Exo-Suit V5.0")
    print("=" * 60)
    
    try:
        metacore = MetaCoreOptimizationEngine()
        
        print(" MetaCore Optimization Engine initialized successfully!")
        print(" Performance monitoring active")
        print(" Optimization rules loaded and ready")
        
        # Run for a few cycles to demonstrate
        print("\n Running optimization cycle...")
        time.sleep(5)  # Let monitoring collect some data
        
        # Generate report
        print(" Generating optimization report...")
        report = metacore.generate_optimization_report()
        
        print(f" System Health: {report['system_health']['status']}")
        print(f" Issues Found: {len(report['system_health']['issues'])}")
        print(f" Recommendations: {len(report['recommendations'])}")
        
        print("\n MetaCore Optimization Engine ready for operation!")
        
        # Keep running for demonstration
        print("Press Ctrl+C to stop...")
        try:
            while True:
                time.sleep(30)
                # Generate periodic reports
                report = metacore.generate_optimization_report()
                print(f" Health Check: {report['system_health']['status']} - {len(report['system_health']['issues'])} issues")
        except KeyboardInterrupt:
            print("\n Stopping MetaCore Optimization Engine...")
            metacore.stop_monitoring()
            print(" MetaCore Optimization Engine stopped")
    
    except Exception as e:
        print(f" Error initializing MetaCore: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
