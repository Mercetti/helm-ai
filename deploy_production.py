#!/usr/bin/env python3
"""
Stellar Logic AI - Production Deployment Manager
Automated deployment and scaling for production environment
"""

import os
import sys
import subprocess
import time
import json
import logging
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionDeployment:
    def __init__(self):
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.servers = {
            'dashboard': {'port': 5000, 'process': None},
            'llm': {'port': 5001, 'process': None},
            'team_chat': {'port': 5002, 'process': None},
            'voice_chat': {'port': 5003, 'process': None},
            'video_chat': {'port': 5004, 'process': None},
            'friends_system': {'port': 5005, 'process': None},
            'analytics': {'port': 5006, 'process': None},
            'security': {'port': 5007, 'process': None}
        }
        
        self.health_checks = {}
        self.deployment_log = []
        
    def log_deployment(self, message, level='INFO'):
        """Log deployment events"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        self.deployment_log.append(log_entry)
        
        if level == 'ERROR':
            logger.error(f"[{timestamp}] {message}")
        elif level == 'WARNING':
            logger.warning(f"[{timestamp}] {message}")
        else:
            logger.info(f"[{timestamp}] {message}")
    
    def check_prerequisites(self):
        """Check deployment prerequisites"""
        self.log_deployment("Checking deployment prerequisites...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or python_version.minor < 8:
            self.log_deployment("Python 3.8+ required", "ERROR")
            return False
        
        # Check required packages
        required_packages = [
            'flask', 'flask-cors', 'flask-socketio', 
            'requests', 'sqlite3', 'watchdog'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.log_deployment(f"✅ {package} available")
            except ImportError:
                self.log_deployment(f"❌ {package} not found", "ERROR")
                return False
        
        # Check Ollama
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                self.log_deployment("✅ Ollama server running")
            else:
                self.log_deployment("❌ Ollama server not responding", "ERROR")
                return False
        except:
            self.log_deployment("❌ Ollama server not running", "ERROR")
            return False
        
        self.log_deployment("✅ All prerequisites met")
        return True
    
    def start_server(self, server_name, server_file):
        """Start a server process"""
        try:
            self.log_deployment(f"Starting {server_name} server...")
            
            # Start server process
            process = subprocess.Popen([
                sys.executable, server_file
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.servers[server_name]['process'] = process
            
            # Wait for server to start
            time.sleep(2)
            
            # Health check
            port = self.servers[server_name]['port']
            health_url = f'http://localhost:{port}/api/health'
            
            max_attempts = 10
            for attempt in range(max_attempts):
                try:
                    response = requests.get(health_url, timeout=2)
                    if response.status_code == 200:
                        self.log_deployment(f"✅ {server_name} server healthy on port {port}")
                        self.health_checks[server_name] = True
                        return True
                except:
                    time.sleep(1)
            
            self.log_deployment(f"❌ {server_name} server failed health check", "ERROR")
            return False
            
        except Exception as e:
            self.log_deployment(f"❌ Failed to start {server_name}: {str(e)}", "ERROR")
            return False
    
    def deploy_all_servers(self):
        """Deploy all servers"""
        self.log_deployment("Starting full deployment...")
        
        server_files = {
            'dashboard': 'dev_server.py',
            'llm': 'stellar_llm_server.py',
            'team_chat': 'team_chat_server.py',
            'voice_chat': 'voice_chat_server.py',
            'video_chat': 'video_chat_server.py',
            'friends_system': 'friends_system_server.py',
            'analytics': 'analytics_server.py',
            'security': 'security_server.py'
        }
        
        deployment_success = True
        
        for server_name, server_file in server_files.items():
            if not self.start_server(server_name, server_file):
                deployment_success = False
                break
        
        if deployment_success:
            self.log_deployment("✅ All servers deployed successfully")
        else:
            self.log_deployment("❌ Deployment failed", "ERROR")
            self.stop_all_servers()
        
        return deployment_success
    
    def health_check_all(self):
        """Perform health check on all servers"""
        self.log_deployment("Performing health checks...")
        
        all_healthy = True
        
        for server_name, server_info in self.servers.items():
            if server_info['process'] and server_info['process'].poll() is None:
                port = server_info['port']
                try:
                    response = requests.get(f'http://localhost:{port}/api/health', timeout=3)
                    if response.status_code == 200:
                        self.log_deployment(f"✅ {server_name} healthy")
                        self.health_checks[server_name] = True
                    else:
                        self.log_deployment(f"❌ {server_name} unhealthy", "WARNING")
                        self.health_checks[server_name] = False
                        all_healthy = False
                except:
                    self.log_deployment(f"❌ {server_name} not responding", "WARNING")
                    self.health_checks[server_name] = False
                    all_healthy = False
            else:
                self.log_deployment(f"❌ {server_name} not running", "WARNING")
                self.health_checks[server_name] = False
                all_healthy = False
        
        return all_healthy
    
    def stop_all_servers(self):
        """Stop all servers"""
        self.log_deployment("Stopping all servers...")
        
        for server_name, server_info in self.servers.items():
            if server_info['process']:
                try:
                    server_info['process'].terminate()
                    server_info['process'].wait(timeout=5)
                    self.log_deployment(f"✅ {server_name} stopped")
                except subprocess.TimeoutExpired:
                    server_info['process'].kill()
                    self.log_deployment(f"✅ {server_name} force killed")
                except:
                    self.log_deployment(f"❌ Failed to stop {server_name}", "WARNING")
                
                server_info['process'] = None
    
    def get_deployment_status(self):
        """Get current deployment status"""
        status = {
            'environment': self.environment,
            'timestamp': datetime.now().isoformat(),
            'servers': {},
            'health_checks': self.health_checks,
            'overall_status': 'healthy' if all(self.health_checks.values()) else 'unhealthy'
        }
        
        for server_name, server_info in self.servers.items():
            status['servers'][server_name] = {
                'port': server_info['port'],
                'running': server_info['process'] is not None and server_info['process'].poll() is None,
                'healthy': self.health_checks.get(server_name, False)
            }
        
        return status
    
    def generate_deployment_report(self):
        """Generate deployment report"""
        status = self.get_deployment_status()
        
        report = f"""
# 🚀 Stellar Logic AI Deployment Report

## 📊 Deployment Status
- **Environment:** {status['environment']}
- **Timestamp:** {status['timestamp']}
- **Overall Status:** {status['overall_status'].upper()}

## 🖥️ Server Status
"""
        
        for server_name, server_info in status['servers'].items():
            status_icon = "✅" if server_info['healthy'] else "❌"
            report += f"- **{server_name.replace('_', ' ').title()}** {status_icon} Port {server_info['port']}\n"
        
        report += f"""
## 📋 Deployment Log
"""
        
        for log_entry in self.deployment_log[-10:]:  # Last 10 entries
            report += f"- [{log_entry['timestamp']}] {log_entry['level']}: {log_entry['message']}\n"
        
        return report
    
    def monitor_deployment(self, duration_minutes=60):
        """Monitor deployment for specified duration"""
        self.log_deployment(f"Starting deployment monitoring for {duration_minutes} minutes...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            if not self.health_check_all():
                self.log_deployment("⚠️ Health check failed - attempting recovery", "WARNING")
                # Could implement auto-recovery here
            
            time.sleep(30)  # Check every 30 seconds
        
        self.log_deployment("Deployment monitoring completed")

def main():
    """Main deployment function"""
    print("🚀 Stellar Logic AI - Production Deployment Manager")
    print("=" * 60)
    
    deployment = ProductionDeployment()
    
    # Check prerequisites
    if not deployment.check_prerequisites():
        print("❌ Prerequisites check failed. Deployment aborted.")
        return False
    
    # Deploy all servers
    if not deployment.deploy_all_servers():
        print("❌ Deployment failed.")
        return False
    
    # Final health check
    if deployment.health_check_all():
        print("✅ Deployment successful!")
        print("\n📊 Deployment Status:")
        status = deployment.get_deployment_status()
        for server_name, server_info in status['servers'].items():
            status_icon = "✅" if server_info['healthy'] else "❌"
            print(f"  {status_icon} {server_name.replace('_', ' ').title()} - Port {server_info['port']}")
        
        print(f"\n🌐 Access your platform at: http://localhost:5000/dashboard.html")
        print(f"📱 Mobile interface: http://localhost:5000/mobile.html")
        
        # Generate report
        report = deployment.generate_deployment_report()
        
        # Save report
        with open('deployment_report.md', 'w') as f:
            f.write(report)
        
        print(f"\n📄 Deployment report saved to: deployment_report.md")
        
        # Start monitoring (optional)
        try:
            print("\n🔍 Starting deployment monitoring (Press Ctrl+C to stop)...")
            deployment.monitor_deployment(duration_minutes=60)
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")
        
        return True
    else:
        print("❌ Post-deployment health check failed.")
        deployment.stop_all_servers()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
