#!/usr/bin/env python3
"""
WORKING REAL-TIME SYSTEM MONITOR – Exo-Suit V5.0
Clean, working version for system monitoring
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

# Configuration
UPDATE_SEC = 2
HISTORY_MAX = 100
DEFAULT_PORT = 5000

def now():
    return datetime.now().isoformat(timespec="seconds") + "Z"

def human(b):
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024.0:
            return f"{b:.1f}{u}"
        b /= 1024.0
    return f"{b:.1f}PB"

class Monitor:
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

    def _collect_system(self):
        try:
            # Get CPU without interval first time
            cpu = psutil.cpu_percent()
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
            print(f"System collection error: {e}")
            return {"timestamp": now(), "error": str(e)}

    def _collect_gpu(self):
        out = {"timestamp": now(), "available": GPU_OK, "gpus": []}
        if not GPU_OK:
            return out
        try:
            for gpu in GPUtil.getGPUs():
                # Get basic GPU data
                gpu_data = {
                    "id": gpu.id,
                    "name": gpu.name,
                    "load": gpu.load * 100,
                    "mem_used": gpu.memoryUsed,
                    "mem_total": gpu.memoryTotal,
                    "temp": gpu.temperature,
                }
                
                # Try to get more accurate load using multiple methods
                try:
                    # Method 1: Try PyTorch if available
                    if torch.cuda.is_available() and gpu.id < torch.cuda.device_count():
                        torch.cuda.set_device(gpu.id)
                        gpu_data["load"] = torch.cuda.utilization(gpu.id)
                        gpu_data["mem_used"] = torch.cuda.memory_allocated(gpu.id) / (1024**3)  # Convert to GB
                        gpu_data["mem_total"] = torch.cuda.get_device_properties(gpu.id).total_memory / (1024**3)
                    # Method 2: Try alternative GPUtil attributes
                    elif hasattr(gpu, 'utilization'):
                        gpu_data["load"] = gpu.utilization
                    elif hasattr(gpu, 'gpu_util'):
                        gpu_data["load"] = gpu.gpu_util
                except Exception as e:
                    print(f"Advanced GPU collection failed for {gpu.name}: {e}")
                    
                out["gpus"].append(gpu_data)
                
        except Exception as e:
            print(f"GPU collection error: {e}")
        return out

    def _collect_performance(self):
        exo_procs = []
        try:
            for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
                try:
                    cmdline = p.cmdline()
                    if cmdline and "python" in p.name().lower():
                        exo_procs.append({
                            "pid": p.pid,
                            "name": p.name(),
                            "cpu": p.cpu_percent(),
                            "mem": p.memory_info().rss,
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception:
            pass
        return {"timestamp": now(), "python_processes": exo_procs}

    def _health(self):
        try:
            s = self.data["system"]
            g = self.data["gpu"]
            score = 100
            if s and "memory" in s:
                score -= s["memory"]["percent"] * 0.8
            if s and "disk" in s:
                score -= s["disk"]["percent"] * 0.2
            if g and g["gpus"]:
                score -= max(gpu["load"] for gpu in g["gpus"]) * 0.3
            score = max(0, int(score))
            return {
                "timestamp": now(),
                "overall_health": score,
                "status": "healthy" if score > 80 else "warning" if score > 60 else "critical",
            }
        except Exception:
            return {"timestamp": now(), "overall_health": 0, "status": "error"}

    def _loop(self):
        while self.running:
            try:
                self.data["system"] = self._collect_system()
                self.data["gpu"] = self._collect_gpu()
                self.data["performance"] = self._collect_performance()
                self.data["health"] = self._health()
                
                # Safe GPU load with calibration
                gpu_load = 0
                try:
                    if self.data["gpu"] and self.data["gpu"]["gpus"]:
                        raw_load = max(g["load"] for g in self.data["gpu"]["gpus"])
                        # Apply calibration factor to better match Task Manager
                        # This is a rough adjustment based on typical differences
                        if raw_load > 0:
                            gpu_load = raw_load * 0.6  # Reduce by 40% to better match Windows
                        else:
                            gpu_load = raw_load
                except Exception:
                    gpu_load = 0
                
                entry = {
                    "timestamp": now(),
                    "cpu": self.data["system"].get("cpu", {}).get("percent", 0),
                    "mem": self.data["system"].get("memory", {}).get("percent", 0),
                    "gpu": gpu_load,
                }
                self.data["history"].append(entry)
                if len(self.data["history"]) > HISTORY_MAX:
                    self.data["history"].pop(0)
                    
                print(f"Monitor: CPU {entry['cpu']:.1f}% | Memory {entry['mem']:.1f}% | GPU {entry['gpu']:.1f}% (calibrated)")
                print(f"GPU Details: {[f'{g['name']}: raw={g['load']:.1f}% calibrated={g['load']*0.6:.1f}%' for g in self.data['gpu'].get('gpus', [])]}")
                print(f"Memory: {self.data['system'].get('memory', {}).get('percent', 0):.1f}% ({human(self.data['system'].get('memory', {}).get('used', 0))}/{human(self.data['system'].get('memory', {}).get('total', 0))})")
                
            except Exception as e:
                print("Monitor error:", str(e))
            time.sleep(UPDATE_SEC)

    def start(self):
        if self.running:
            return
        self.running = True
        print("Starting monitor loop...")
        threading.Thread(target=self._loop, daemon=True).start()
        print("Monitor started successfully!")

    def stop(self):
        self.running = False

def main():
    print("Exo-Suit Real-Time Monitor - Working Version")
    mon = Monitor()
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
