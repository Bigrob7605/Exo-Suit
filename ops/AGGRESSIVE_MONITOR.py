#!/usr/bin/env python3
"""
AGGRESSIVE REAL-TIME SYSTEM MONITOR – Exo-Suit V5.0
High-frequency sampling to catch real utilization
"""
import os
import time
import json
import threading
from datetime import datetime
from pathlib import Path

try:
    import psutil
except ImportError:
    raise SystemExit("psutil required: pip install psutil")

try:
    import torch
    import GPUtil
    GPU_OK = True
except Exception:
    GPU_OK = False

# AGGRESSIVE Configuration - Sample every 0.5 seconds
UPDATE_SEC = 0.5
HISTORY_MAX = 200
DEFAULT_PORT = 5000

def now():
    return datetime.now().isoformat(timespec="seconds") + "Z"

def human(b):
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024.0:
            return f"{b:.1f}{u}"
        b /= 1024.0
    return f"{b:.1f}PB"

class AggressiveMonitor:
    def __init__(self, port=DEFAULT_PORT):
        self.port = port
        self.running = False
        self.data = {
            "system": {},
            "gpu": {},
            "performance": {},
            "health": {},
            "history": [],
        }
        self.peak_values = {
            "cpu": 0,
            "memory": 0,
            "gpu": 0
        }

    def _collect_system(self):
        try:
            # Get CPU with minimal interval for real-time data
            cpu = psutil.cpu_percent(interval=0.1)
            vm = psutil.virtual_memory()
            
            # Try to get disk usage for Windows
            try:
                disk = psutil.disk_usage("C:\\")
            except:
                try:
                    disk = psutil.disk_usage("/")
                except:
                    disk = None
                
            result = {
                "timestamp": now(),
                "cpu": {"percent": cpu, "cores": psutil.cpu_count()},
                "memory": {
                    "total": vm.total,
                    "used": vm.used,
                    "percent": vm.percent,
                }
            }
            
            if disk:
                result["disk"] = {
                    "total": disk.total,
                    "used": disk.used,
                    "percent": (disk.used / disk.total) * 100,
                }
            
            return result
            
        except Exception as e:
            return {"timestamp": now(), "error": str(e)}

    def _collect_gpu(self):
        out = {"timestamp": now(), "available": GPU_OK, "gpus": []}
        if not GPU_OK:
            return out
        try:
            for gpu in GPUtil.getGPUs():
                gpu_data = {
                    "id": gpu.id,
                    "name": gpu.name,
                    "load": gpu.load * 100,
                    "mem_used": gpu.memoryUsed,
                    "mem_total": gpu.memoryTotal,
                    "temp": gpu.temperature,
                }
                
                # Try PyTorch for more accurate data
                try:
                    if torch.cuda.is_available() and gpu.id < torch.cuda.device_count():
                        torch.cuda.set_device(gpu.id)
                        gpu_data["load"] = torch.cuda.utilization(gpu.id)
                        gpu_data["mem_used"] = torch.cuda.memory_allocated(gpu.id) / (1024**3)
                        gpu_data["mem_total"] = torch.cuda.get_device_properties(gpu.id).total_memory / (1024**3)
                except Exception:
                    pass
                    
                out["gpus"].append(gpu_data)
                
        except Exception as e:
            print(f"GPU collection error: {e}")
        return out

    def _loop(self):
        while self.running:
            try:
                self.data["system"] = self._collect_system()
                self.data["gpu"] = self._collect_gpu()
                
                # Get current values
                cpu_val = self.data["system"].get("cpu", {}).get("percent", 0)
                mem_val = self.data["system"].get("memory", {}).get("percent", 0)
                
                # Get GPU load with calibration
                gpu_load = 0
                try:
                    if self.data["gpu"] and self.data["gpu"]["gpus"]:
                        raw_load = max(g["load"] for g in self.data["gpu"]["gpus"])
                        gpu_load = raw_load * 0.6  # Calibration factor
                except Exception:
                    gpu_load = 0
                
                # Update peak values
                self.peak_values["cpu"] = max(self.peak_values["cpu"], cpu_val)
                self.peak_values["memory"] = max(self.peak_values["memory"], mem_val)
                self.peak_values["gpu"] = max(self.peak_values["gpu"], gpu_load)
                
                entry = {
                    "timestamp": now(),
                    "cpu": cpu_val,
                    "mem": mem_val,
                    "gpu": gpu_load,
                }
                self.data["history"].append(entry)
                if len(self.data["history"]) > HISTORY_MAX:
                    self.data["history"].pop(0)
                    
                # Show current + peak values
                print(f"NOW: CPU {cpu_val:5.1f}% | Memory {mem_val:5.1f}% | GPU {gpu_load:5.1f}%")
                print(f"PEAK: CPU {self.peak_values['cpu']:5.1f}% | Memory {self.peak_values['memory']:5.1f}% | GPU {self.peak_values['gpu']:5.1f}%")
                print(f"GPU Details: {[f'{g['name']}: raw={g['load']:.1f}% calibrated={g['load']*0.6:.1f}%' for g in self.data['gpu'].get('gpus', [])]}")
                print(f"Memory: {mem_val:.1f}% ({human(self.data['system'].get('memory', {}).get('used', 0))}/{human(self.data['system'].get('memory', {}).get('total', 0))})")
                print("-" * 80)
                
            except Exception as e:
                print(f"Monitor error: {e}")
            time.sleep(UPDATE_SEC)

    def start(self):
        if self.running:
            return
        self.running = True
        print("Starting AGGRESSIVE monitor (0.5s sampling)...")
        threading.Thread(target=self._loop, daemon=True).start()
        print("Aggressive monitor started!")

    def stop(self):
        self.running = False

def main():
    print("Exo-Suit AGGRESSIVE Real-Time Monitor")
    mon = AggressiveMonitor()
    try:
        mon.start()
        print("Monitor is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        mon.stop()
        print("Monitor stopped.")

if __name__ == "__main__":
    main()
