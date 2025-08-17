#!/usr/bin/env python3
"""
REAL-TIME SYSTEM MONITOR – Exo-Suit V5.0
Zero-dependency core + optional web endpoint
Copy-paste ready.
"""
import os, time, json, threading
from datetime import datetime
from pathlib import Path

try:
    import psutil
except ImportError:
    raise SystemExit("psutil required: pip install psutil")

try:
    import torch, GPUtil
    GPU_OK = True
except Exception:
    GPU_OK = False

try:
    from flask import Flask, jsonify
    from flask_cors import CORS
    WEB_OK = True
except Exception:
    WEB_OK = False

# ---------- CONFIG ----------
UPDATE_SEC = 2
HISTORY_MAX = 100
DEFAULT_PORT = 5000

# ---------- UTILITY ----------
def now():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def human(b: int) -> str:
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024.0:
            return f"{b:.1f}{u}"
        b /= 1024.0
    return f"{b:.1f}PB"

# ---------- DATA ----------
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

        if WEB_OK:
            self.app = Flask(__name__)
            CORS(self.app)
            self._routes()
        else:
            self.app = None

    # ---------- WEB ROUTES ----------
    def _routes(self):
        @self.app.route("/")
        def root():
            return jsonify({"status": "Exo-Suit Real-Time Monitor", "endpoints": list(self.data)})

        for k in ["system", "gpu", "performance", "health", "history"]:
            self.app.add_url_rule(f"/{k}", k, lambda k=k: jsonify(self.data[k]))

    # ---------- COLLECT ----------
    def _collect_system(self):
        cpu = psutil.cpu_percent(interval=None)
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        return {
            "timestamp": now(),
            "cpu": {"percent": cpu, "cores": psutil.cpu_count()},
            "memory": {
                "total": vm.total,
                "used": vm.used,
                "percent": vm.percent,
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "percent": (disk.used / disk.total) * 100,
            },
        }

    def _collect_gpu(self):
        out = {"timestamp": now(), "available": GPU_OK, "gpus": []}
        if not GPU_OK:
            return out
        try:
            for gpu in GPUtil.getGPUs():
                out["gpus"].append(
                    {
                        "id": gpu.id,
                        "name": gpu.name,
                        "load": gpu.load * 100,
                        "mem_used": gpu.memoryUsed,
                        "mem_total": gpu.memoryTotal,
                        "temp": gpu.temperature,
                    }
                )
        except Exception:
            pass
        return out

    def _collect_performance(self):
        exo_procs = []
        try:
            for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
                try:
                    cmdline = p.cmdline()
                    if cmdline and "python" in p.name().lower() and any("exo" in str(arg).lower() for arg in cmdline):
                        exo_procs.append({
                            "pid": p.pid,
                            "name": p.name(),
                            "cpu": p.cpu_percent(),
                            "mem": p.memory_info().rss,
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"Performance collection error: {e}")
        return {"timestamp": now(), "exosuit_processes": exo_procs}

    def _health(self):
        s = self.data["system"]
        g = self.data["gpu"]
        score = 100
        if s:
            score -= s["memory"]["percent"] * 0.8
            score -= s["disk"]["percent"] * 0.2
        if g and g["gpus"]:
            score -= max(gpu["load"] for gpu in g["gpus"]) * 0.3
        score = max(0, int(score))
        return {
            "timestamp": now(),
            "overall_health": score,
            "status": "healthy" if score > 80 else "warning" if score > 60 else "critical",
        }

    # ---------- LOOP ----------
    def _loop(self):
        while self.running:
            try:
                self.data["system"] = self._collect_system()
                self.data["gpu"] = self._collect_gpu()
                self.data["performance"] = self._collect_performance()
                self.data["health"] = self._health()
                
                # Safely get GPU load
                gpu_load = 0
                try:
                    if self.data["gpu"] and self.data["gpu"]["gpus"]:
                        gpu_load = max(g["load"] for g in self.data["gpu"]["gpus"])
                except Exception:
                    gpu_load = 0
                
                entry = {
                    "timestamp": now(),
                    "cpu": self.data["system"]["cpu"]["percent"],
                    "mem": self.data["system"]["memory"]["percent"],
                    "gpu": gpu_load,
                }
                self.data["history"].append(entry)
                if len(self.data["history"]) > HISTORY_MAX:
                    self.data["history"].pop(0)
            except Exception as e:
                print("monitor error:", e)
            time.sleep(UPDATE_SEC)

    # ---------- PUBLIC ----------
    def start(self):
        if self.running:
            return
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()
        if self.app:
            self.app.run(host="0.0.0.0", port=self.port, debug=False, use_reloader=False)

    def stop(self):
        self.running = False

# ---------- CLI ----------
def main():
    print("Exo-Suit Real-Time Monitor")
    mon = Monitor()
    try:
        mon.start()
    except KeyboardInterrupt:
        mon.stop()
        print("stopped")

if __name__ == "__main__":
    main()
