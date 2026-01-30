#!/usr/bin/env python3
"""
Stellar Logic AI - Continuous System Monitor
Real-time monitoring and automatic issue detection
"""

import requests
import json
import time
import threading
from datetime import datetime
import subprocess
import os

class ContinuousMonitor:
    def __init__(self):
        self.servers = {
            'dashboard': {'port': 5000, 'url': 'http://localhost:5000'},
            'llm': {'port': 5001, 'url': 'http://localhost:5001'},
            'team_chat': {'port': 5002, 'url': 'http://localhost:5002'},
            'voice_chat': {'port': 5003, 'url': 'http://localhost:5003'},
            'video_chat': {'port': 5004, 'url': 'http://localhost:5004'},
            'friends_system': {'port': 5005, 'url': 'http://localhost:5005'},
            'analytics': {'port': 5006, 'url': 'http://localhost:5006'},
            'security': {'port': 5007, 'url': 'http://localhost:5007'}
        }
        self.monitoring = True
        self.issues = []
        self.last_check = {}
        
    def check_server_health(self, server_name, server_info):
        """Check individual server health"""
        try:
            health_url = f"{server_info['url']}/api/health"
            response = requests.get(health_url, timeout=3)
            
            if response.status_code == 200:
                return {'status': 'healthy', 'response_time': response.elapsed.total_seconds()}
            else:
                return {'status': 'unhealthy', 'error': f"HTTP {response.status_code}"}
                
        except requests.exceptions.Timeout:
            return {'status': 'timeout', 'error': 'Request timeout'}
        except requests.exceptions.ConnectionError:
            return {'status': 'offline', 'error': 'Connection refused'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def check_server_port(self, server_name, port):
        """Check if server is listening on port"""
        try:
            result = subprocess.run(['netstat', '-ano', '|', 'findstr', f':{port}'], 
                                   capture_output=True, text=True, timeout=5)
            return result.returncode == 0 and str(port) in result.stdout
        except:
            return False
    
    def check_file_exists(self, file_path):
        """Check if file exists"""
        return os.path.exists(file_path)
    
    def check_ollama_connection(self):
        """Check Ollama connection"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def run_health_check(self):
        """Run comprehensive health check"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'servers': {},
            'files': {},
            'ollama': False,
            'overall_status': 'unknown'
        }
        
        # Check servers
        server_status = {}
        for server_name, server_info in self.servers.items():
            # Check port first
            port_active = self.check_server_port(server_name, server_info['port'])
            
            # Check health endpoint
            health = self.check_server_health(server_name, server_info)
            
            server_status[server_name] = {
                'port_active': port_active,
                'health': health,
                'status': 'healthy' if health['status'] == 'healthy' else 'unhealthy'
            }
        
        results['servers'] = server_status
        
        # Check critical files
        critical_files = [
            'dashboard.html',
            'mobile.html',
            'webrtc-client.js',
            'stellar_llm_server.py'
        ]
        
        file_status = {}
        for file_path in critical_files:
            file_status[file_path] = self.check_file_exists(file_path)
        
        results['files'] = file_status
        
        # Check Ollama
        results['ollama'] = self.check_ollama_connection()
        
        # Calculate overall status
        healthy_servers = sum(1 for s in server_status.values() if s['status'] == 'healthy')
        total_servers = len(server_status)
        files_exist = sum(1 for f in file_status.values() if f)
        total_files = len(file_status)
        
        if healthy_servers == total_servers and files_exist == total_files and results['ollama']:
            results['overall_status'] = 'healthy'
        elif healthy_servers >= total_servers * 0.8:
            results['overall_status'] = 'degraded'
        else:
            results['overall_status'] = 'unhealthy'
        
        return results
    
    def detect_issues(self, current_results):
        """Detect new issues"""
        new_issues = []
        
        # Check server issues
        for server_name, server_data in current_results['servers'].items():
            if server_data['status'] != 'healthy':
                issue = {
                    'type': 'server',
                    'component': server_name,
                    'issue': f"Server {server_data['health']['status']}: {server_data['health'].get('error', 'Unknown')}",
                    'timestamp': current_results['timestamp']
                }
                new_issues.append(issue)
        
        # Check file issues
        for file_name, exists in current_results['files'].items():
            if not exists:
                issue = {
                    'type': 'file',
                    'component': file_name,
                    'issue': 'File missing',
                    'timestamp': current_results['timestamp']
                }
                new_issues.append(issue)
        
        # Check Ollama
        if not current_results['ollama']:
            issue = {
                'type': 'service',
                'component': 'ollama',
                'issue': 'Ollama server not responding',
                'timestamp': current_results['timestamp']
            }
            new_issues.append(issue)
        
        return new_issues
    
    def print_status(self, results):
        """Print current status"""
        print(f"\n🔍 System Status - {results['timestamp']}")
        print("=" * 60)
        
        # Overall status
        status_emoji = {
            'healthy': '✅',
            'degraded': '⚠️',
            'unhealthy': '❌'
        }
        
        overall_emoji = status_emoji.get(results['overall_status'], '❓')
        print(f"Overall Status: {overall_emoji} {results['overall_status'].upper()}")
        
        # Server status
        print(f"\n🖥️ Servers ({len(results['servers'])}):")
        for server_name, server_data in results['servers'].items():
            server_emoji = '✅' if server_data['status'] == 'healthy' else '❌'
            port_emoji = '🟢' if server_data['port_active'] else '🔴'
            print(f"  {server_emoji} {port_emoji} {server_name} - {server_data['status']}")
        
        # File status
        print(f"\n📁 Files ({len(results['files'])}):")
        for file_name, exists in results['files'].items():
            file_emoji = '✅' if exists else '❌'
            print(f"  {file_emoji} {file_name}")
        
        # Ollama status
        ollama_emoji = '✅' if results['ollama'] else '❌'
        print(f"\n🤖 Ollama: {ollama_emoji} Connected")
        
        # Issues
        new_issues = self.detect_issues(results)
        if new_issues:
            print(f"\n⚠️ Issues Found ({len(new_issues)}):")
            for issue in new_issues:
                print(f"  ❌ {issue['component']}: {issue['issue']}")
        else:
            print(f"\n✅ No issues detected")
    
    def start_monitoring(self, interval=30):
        """Start continuous monitoring"""
        print("🚀 Starting Continuous System Monitor...")
        print(f"📊 Checking every {interval} seconds")
        print("Press Ctrl+C to stop monitoring\n")
        
        try:
            while self.monitoring:
                results = self.run_health_check()
                self.print_status(results)
                
                # Save last check
                self.last_check = results
                
                # Wait for next check
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")
            self.monitoring = False
    
    def get_current_status(self):
        """Get current system status"""
        return self.run_health_check()

def main():
    """Main monitoring function"""
    monitor = ContinuousMonitor()
    
    # Quick status check
    print("🔍 Quick System Status Check:")
    results = monitor.get_current_status()
    monitor.print_status(results)
    
    # Start continuous monitoring
    monitor.start_monitoring(interval=30)

if __name__ == '__main__':
    main()
