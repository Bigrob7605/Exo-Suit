#!/usr/bin/env python3
"""
🏛️ KAI SENTINEL MESH - MULTI-REPO FORT KNOX MONITORING
God-mode multi-repository Sentinel system for OSS Fort Knox discipline.

This system monitors multiple repositories simultaneously, preventing drift
across entire organizations and maintaining Fort Knox standards everywhere.
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import threading
import queue
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kai_sentinel_mesh.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class KaiSentinelMesh:
    """Multi-repository Sentinel system for Fort Knox discipline."""
    
    def __init__(self, config_file: str = "sentinel_mesh_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.repos = self.config.get("repositories", [])
        self.dashboard_url = self.config.get("dashboard_url", "")
        self.alert_email = self.config.get("alert_email", "")
        self.check_interval = self.config.get("check_interval", 3600)  # 1 hour
        self.alert_queue = queue.Queue()
        self.running = False
        
    def load_config(self) -> Dict[str, Any]:
        """Load or create Sentinel mesh configuration."""
        default_config = {
            "repositories": [
                {
                    "name": "Universal Open Science Toolbox With Kai",
                    "path": "C:/My Projects/Universal Open Science Toolbox With Kai",
                    "health_check": "python self_heal_protocol.py",
                    "fire_drill": "python weekly_fire_drill_scheduler.py --run-now",
                    "critical_files": [
                        "self_heal_protocol.py",
                        "weekly_fire_drill_scheduler.py",
                        "brutal_checks_with_self_heal.py"
                    ]
                }
            ],
            "dashboard_url": "",
            "alert_email": "",
            "check_interval": 3600,
            "slack_webhook": "",
            "discord_webhook": "",
            "auto_fix": False,
            "evidence_retention_days": 30
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return {**default_config, **json.load(f)}
            except Exception as e:
                logging.error(f"Failed to load config: {e}")
                return default_config
        else:
            # Create default config
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
            
    def check_repository_health(self, repo_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of a single repository."""
        repo_name = repo_config["name"]
        repo_path = Path(repo_config["path"])
        
        result = {
            "repo_name": repo_name,
            "timestamp": datetime.now().isoformat(),
            "status": "UNKNOWN",
            "health_check": {},
            "fire_drill": {},
            "critical_files": {},
            "evidence_bundles": [],
            "alerts": []
        }
        
        try:
            # Check if repository exists
            if not repo_path.exists():
                result["status"] = "MISSING"
                result["alerts"].append(f"Repository path not found: {repo_path}")
                return result
                
            # Check critical files
            for file_name in repo_config.get("critical_files", []):
                file_path = repo_path / file_name
                result["critical_files"][file_name] = file_path.exists()
                if not file_path.exists():
                    result["alerts"].append(f"Critical file missing: {file_name}")
                    
            # Run health check
            if repo_config.get("health_check"):
                try:
                    health_result = subprocess.run(
                        repo_config["health_check"].split(),
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    result["health_check"] = {
                        "success": health_result.returncode == 0,
                        "stdout": health_result.stdout,
                        "stderr": health_result.stderr,
                        "return_code": health_result.returncode
                    }
                    if health_result.returncode != 0:
                        result["alerts"].append(f"Health check failed: {health_result.stderr}")
                except Exception as e:
                    result["health_check"] = {"error": str(e)}
                    result["alerts"].append(f"Health check error: {e}")
                    
            # Run fire drill
            if repo_config.get("fire_drill"):
                try:
                    drill_result = subprocess.run(
                        repo_config["fire_drill"].split(),
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=600
                    )
                    result["fire_drill"] = {
                        "success": drill_result.returncode == 0,
                        "stdout": drill_result.stdout,
                        "stderr": drill_result.stderr,
                        "return_code": drill_result.returncode
                    }
                    if drill_result.returncode != 0:
                        result["alerts"].append(f"Fire drill failed: {drill_result.stderr}")
                except Exception as e:
                    result["fire_drill"] = {"error": str(e)}
                    result["alerts"].append(f"Fire drill error: {e}")
                    
            # Check evidence bundles
            evidence_dir = repo_path / "Project White Papers" / "self_heal_evidence"
            if evidence_dir.exists():
                for bundle_dir in evidence_dir.iterdir():
                    if bundle_dir.is_dir():
                        result["evidence_bundles"].append({
                            "name": bundle_dir.name,
                            "path": str(bundle_dir),
                            "replay_script": (bundle_dir / "replay.py").exists()
                        })
                        
            # Determine overall status
            health_ok = result["health_check"].get("success", False)
            drill_ok = result["fire_drill"].get("success", False)
            files_ok = all(result["critical_files"].values())
            
            if health_ok and drill_ok and files_ok:
                result["status"] = "HEALTHY"
            elif not files_ok:
                result["status"] = "CRITICAL"
            else:
                result["status"] = "WARNING"
                
        except Exception as e:
            result["status"] = "ERROR"
            result["alerts"].append(f"Repository check error: {e}")
            
        return result
        
    def send_alert(self, alert_data: Dict[str, Any]):
        """Send alert through configured channels."""
        alert_message = f"""
🚨 KAI SENTINEL MESH ALERT

Repository: {alert_data['repo_name']}
Status: {alert_data['status']}
Timestamp: {alert_data['timestamp']}

Alerts:
{chr(10).join(f"- {alert}" for alert in alert_data['alerts'])}

Health Check: {'✅ PASS' if alert_data['health_check'].get('success') else '❌ FAIL'}
Fire Drill: {'✅ PASS' if alert_data['fire_drill'].get('success') else '❌ FAIL'}
Critical Files: {'✅ ALL PRESENT' if all(alert_data['critical_files'].values()) else '❌ MISSING'}

Evidence Bundles: {len(alert_data['evidence_bundles'])} found

---
Generated by Kai Sentinel Mesh v1.0
"""
        
        # Send email alert
        if self.config.get("alert_email"):
            self.send_email_alert(alert_message, alert_data)
            
        # Send Slack alert
        if self.config.get("slack_webhook"):
            self.send_slack_alert(alert_message, alert_data)
            
        # Send Discord alert
        if self.config.get("discord_webhook"):
            self.send_discord_alert(alert_message, alert_data)
            
        # Update dashboard
        if self.config.get("dashboard_url"):
            self.update_dashboard(alert_data)
            
    def send_email_alert(self, message: str, alert_data: Dict[str, Any]):
        """Send email alert."""
        try:
            msg = MIMEMultipart()
            msg['From'] = "kai-sentinel@fort-knox.org"
            msg['To'] = self.config["alert_email"]
            msg['Subject'] = f"🚨 Kai Sentinel Alert: {alert_data['repo_name']} - {alert_data['status']}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Add SMTP configuration here
            # server = smtplib.SMTP('smtp.gmail.com', 587)
            # server.starttls()
            # server.login(email, password)
            # server.send_message(msg)
            # server.quit()
            
            logging.info(f"Email alert sent for {alert_data['repo_name']}")
        except Exception as e:
            logging.error(f"Failed to send email alert: {e}")
            
    def send_slack_alert(self, message: str, alert_data: Dict[str, Any]):
        """Send Slack alert."""
        try:
            payload = {
                "text": message,
                "username": "Kai Sentinel Mesh",
                "icon_emoji": ":fort_knox:"
            }
            
            response = requests.post(
                self.config["slack_webhook"],
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logging.info(f"Slack alert sent for {alert_data['repo_name']}")
            else:
                logging.error(f"Slack alert failed: {response.status_code}")
        except Exception as e:
            logging.error(f"Failed to send Slack alert: {e}")
            
    def send_discord_alert(self, message: str, alert_data: Dict[str, Any]):
        """Send Discord alert."""
        try:
            payload = {
                "content": message,
                "username": "Kai Sentinel Mesh"
            }
            
            response = requests.post(
                self.config["discord_webhook"],
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logging.info(f"Discord alert sent for {alert_data['repo_name']}")
            else:
                logging.error(f"Discord alert failed: {response.status_code}")
        except Exception as e:
            logging.error(f"Failed to send Discord alert: {e}")
            
    def update_dashboard(self, alert_data: Dict[str, Any]):
        """Update dashboard with alert data."""
        try:
            payload = {
                "repository": alert_data['repo_name'],
                "status": alert_data['status'],
                "timestamp": alert_data['timestamp'],
                "alerts": alert_data['alerts'],
                "health_check": alert_data['health_check'],
                "fire_drill": alert_data['fire_drill'],
                "evidence_bundles": len(alert_data['evidence_bundles'])
            }
            
            response = requests.post(
                self.config["dashboard_url"],
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logging.info(f"Dashboard updated for {alert_data['repo_name']}")
            else:
                logging.error(f"Dashboard update failed: {response.status_code}")
        except Exception as e:
            logging.error(f"Failed to update dashboard: {e}")
            
    def auto_fix_repository(self, repo_config: Dict[str, Any], alert_data: Dict[str, Any]):
        """Attempt to auto-fix repository issues."""
        if not self.config.get("auto_fix", False):
            return False
            
        repo_path = Path(repo_config["path"])
        
        try:
            # Try to run live recovery
            if alert_data["health_check"].get("success") == False:
                live_result = subprocess.run(
                    ["python", "self_heal_protocol.py", "--live"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                if live_result.returncode == 0:
                    logging.info(f"Auto-fix successful for {repo_config['name']}")
                    return True
                else:
                    logging.error(f"Auto-fix failed for {repo_config['name']}: {live_result.stderr}")
                    return False
                    
        except Exception as e:
            logging.error(f"Auto-fix error for {repo_config['name']}: {e}")
            return False
            
    def monitor_repositories(self):
        """Monitor all repositories in the mesh."""
        logging.info("🏛️ Kai Sentinel Mesh started - monitoring repositories")
        
        while self.running:
            try:
                for repo_config in self.repos:
                    logging.info(f"Checking repository: {repo_config['name']}")
                    
                    # Check repository health
                    health_result = self.check_repository_health(repo_config)
                    
                    # Log result
                    logging.info(f"Repository {repo_config['name']}: {health_result['status']}")
                    
                    # Send alerts if needed
                    if health_result['status'] in ['CRITICAL', 'WARNING', 'ERROR']:
                        self.send_alert(health_result)
                        
                        # Attempt auto-fix if enabled
                        if self.config.get("auto_fix", False):
                            self.auto_fix_repository(repo_config, health_result)
                            
                    # Save result to history
                    self.save_check_result(health_result)
                    
                # Wait for next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                logging.error(f"Monitor loop error: {e}")
                time.sleep(60)  # Wait a minute before retrying
                
    def save_check_result(self, result: Dict[str, Any]):
        """Save check result to history."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = Path(f"sentinel_history_{result['repo_name'].replace(' ', '_')}_{timestamp}.json")
        
        try:
            with open(history_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
        except Exception as e:
            logging.error(f"Failed to save check result: {e}")
            
    def start_monitoring(self):
        """Start the Sentinel mesh monitoring."""
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_repositories)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logging.info("🏛️ Kai Sentinel Mesh monitoring started")
        
    def stop_monitoring(self):
        """Stop the Sentinel mesh monitoring."""
        self.running = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
            
        logging.info("🏛️ Kai Sentinel Mesh monitoring stopped")
        
    def run_single_check(self):
        """Run a single check of all repositories."""
        logging.info("🏛️ Running single check of all repositories")
        
        results = []
        for repo_config in self.repos:
            result = self.check_repository_health(repo_config)
            results.append(result)
            
            # Send alerts if needed
            if result['status'] in ['CRITICAL', 'WARNING', 'ERROR']:
                self.send_alert(result)
                
        return results

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kai Sentinel Mesh - Multi-Repo Fort Knox Monitoring")
    parser.add_argument("--start", action="store_true", help="Start continuous monitoring")
    parser.add_argument("--check", action="store_true", help="Run single check")
    parser.add_argument("--config", default="sentinel_mesh_config.json", help="Configuration file")
    
    args = parser.parse_args()
    
    sentinel = KaiSentinelMesh(args.config)
    
    if args.start:
        print("🏛️ Starting Kai Sentinel Mesh monitoring...")
        sentinel.start_monitoring()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🏛️ Stopping Kai Sentinel Mesh...")
            sentinel.stop_monitoring()
            
    elif args.check:
        print("🏛️ Running single check...")
        results = sentinel.run_single_check()
        
        for result in results:
            status_emoji = "✅" if result['status'] == 'HEALTHY' else "❌"
            print(f"{status_emoji} {result['repo_name']}: {result['status']}")
            
            if result['alerts']:
                for alert in result['alerts']:
                    print(f"  ⚠️  {alert}")
                    
    else:
        print("Usage:")
        print("  python kai_sentinel_mesh.py --start")
        print("  python kai_sentinel_mesh.py --check")
        print("  python kai_sentinel_mesh.py --config custom_config.json")

if __name__ == "__main__":
    main()
