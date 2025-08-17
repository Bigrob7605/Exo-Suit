#!/usr/bin/env python3
"""
Simplified Performance Monitor for Phoenix System
Basic system resource monitoring without external dependencies
"""

import time
import psutil
import json
from datetime import datetime
from typing import Dict, List, Any

class SimplePerformanceMonitor:
    """Monitor basic system performance during operations"""
    
    def __init__(self):
        self.start_time = None
        self.cpu_usage = []
        self.ram_usage = []
        self.disk_usage = []
        self.operation_times = []
        
    def start_monitoring(self):
        """Start monitoring"""
        self.start_time = time.time()
        print("Performance monitoring started...")
        
    def record_metrics(self):
        """Record current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_usage.append({
                'timestamp': time.time() - self.start_time if self.start_time else 0,
                'cpu_percent': cpu_percent
            })
            
            # RAM metrics
            ram = psutil.virtual_memory()
            self.ram_usage.append({
                'timestamp': time.time() - self.start_time if self.start_time else 0,
                'used_gb': ram.used / (1024**3),
                'total_gb': ram.total / (1024**3),
                'percent': ram.percent
            })
            
            # Disk metrics - use current working directory for Windows compatibility
            try:
                disk = psutil.disk_usage('.')
            except:
                # Fallback to C: drive on Windows
                disk = psutil.disk_usage('C:\\')
            
            self.disk_usage.append({
                'timestamp': time.time() - self.start_time if self.start_time else 0,
                'used_gb': disk.used / (1024**3),
                'total_gb': disk.total / (1024**3),
                'percent': disk.percent
            })
            
        except Exception as e:
            print(f"Performance monitoring error: {e}")
    
    def record_operation_time(self, operation_name: str, duration: float):
        """Record time for a specific operation"""
        self.operation_times.append({
            'operation': operation_name,
            'duration': duration,
            'timestamp': time.time() - self.start_time if self.start_time else 0
        })
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory()
            # Disk metrics - use current working directory for Windows compatibility
            try:
                disk = psutil.disk_usage('.')
            except:
                # Fallback to C: drive on Windows
                disk = psutil.disk_usage('C:\\')
            
            return {
                'cpu_percent': cpu_percent,
                'ram_used_gb': round(ram.used / (1024**3), 2),
                'ram_total_gb': round(ram.total / (1024**3), 2),
                'ram_percent': ram.percent,
                'disk_used_gb': round(disk.used / (1024**3), 2),
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'disk_percent': disk.percent
            }
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def print_current_status(self):
        """Print current system status"""
        try:
            status = self.get_current_status()
            if 'error' not in status:
                print(f"\n{'='*50}")
                print("CURRENT SYSTEM STATUS")
                print(f"{'='*50}")
                print(f"CPU Usage: {status['cpu_percent']:.1f}%")
                print(f"RAM: {status['ram_used_gb']:.1f}GB / {status['ram_total_gb']:.1f}GB ({status['ram_percent']:.1f}%)")
                print(f"Disk: {status['disk_used_gb']:.1f}GB / {status['disk_total_gb']:.1f}GB ({status['disk_percent']:.1f}%)")
                print(f"{'='*50}")
        except Exception as e:
            print(f"Error printing status: {e}")
    
    def save_report(self, filename="performance_report.json"):
        """Save performance report to file"""
        try:
            report = {
                'test_date': datetime.now().isoformat(),
                'system_info': {
                    'total_ram_gb': psutil.virtual_memory().total / (1024**3),
                    'total_disk_gb': psutil.disk_usage('C:\\').total / (1024**3)
                },
                'cpu_usage': self.cpu_usage,
                'ram_usage': self.ram_usage,
                'disk_usage': self.disk_usage,
                'operation_times': self.operation_times,
                'test_duration': time.time() - self.start_time if self.start_time else 0
            }
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"Performance report saved to: {filename}")
            return True
        except Exception as e:
            print(f"Error saving report: {e}")
            return False
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        try:
            if not self.start_time:
                return {'status': 'Monitoring not started'}
            
            duration = time.time() - self.start_time
            avg_cpu = sum(entry['cpu_percent'] for entry in self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0
            avg_ram = sum(entry['percent'] for entry in self.ram_usage) / len(self.ram_usage) if self.ram_usage else 0
            
            return {
                'monitoring_duration': round(duration, 2),
                'avg_cpu_usage': round(avg_cpu, 2),
                'avg_ram_usage': round(avg_ram, 2),
                'metrics_recorded': len(self.cpu_usage),
                'operations_timed': len(self.operation_times)
            }
        except Exception as e:
            return {
                'error': str(e)
            }

# Test function
def test_simple_performance_monitor():
    """Test the simple performance monitor"""
    monitor = SimplePerformanceMonitor()
    
    print("Testing Simple Performance Monitor...")
    
    # Start monitoring
    monitor.start_monitoring()
    
    # Record some metrics
    for i in range(3):
        monitor.record_metrics()
        time.sleep(0.5)
    
    # Record operation time
    monitor.record_operation_time("test_operation", 1.5)
    
    # Print current status
    monitor.print_current_status()
    
    # Get summary
    summary = monitor.get_summary()
    print(f"\nPerformance Summary: {summary}")
    
    # Save report
    monitor.save_report("test_performance_report.json")
    
    print("Simple Performance Monitor test completed!")

if __name__ == "__main__":
    test_simple_performance_monitor()
