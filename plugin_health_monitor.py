#!/usr/bin/env python3
"""
Plugin Health Monitoring System
Monitors the health and status of all Helm AI plugins
"""

import requests
import json
import time
import sys
import io
from datetime import datetime
from typing import Dict, List, Any
import concurrent.futures

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class PluginHealthMonitor:
    """Monitors health of all plugin services"""
    
    def __init__(self):
        self.plugin_configs = {
            'helm-api': {'port': 5001, 'name': 'Core API Server'},
            'healthcare-plugin': {'port': 5002, 'name': 'Healthcare Plugin'},
            'government-defense-plugin': {'port': 5005, 'name': 'Government & Defense Plugin'},
            'automotive-transportation-plugin': {'port': 5006, 'name': 'Automotive & Transportation Plugin'},
            'real-estate-plugin': {'port': 5007, 'name': 'Real Estate & Property Plugin'},
            'financial-plugin': {'port': 5008, 'name': 'Financial Services Plugin'},
            'manufacturing-plugin': {'port': 5009, 'name': 'Manufacturing & IoT Plugin'},
            'education-plugin': {'port': 5010, 'name': 'Education & Academic Plugin'},
            'ecommerce-plugin': {'port': 5011, 'name': 'E-Commerce Plugin'},
            'media-entertainment-plugin': {'port': 5012, 'name': 'Media & Entertainment Plugin'},
            'pharmaceutical-plugin': {'port': 5013, 'name': 'Pharmaceutical & Research Plugin'},
            'enterprise-plugin': {'port': 5014, 'name': 'Enterprise Solutions Plugin'},
            'gaming-plugin': {'port': 5015, 'name': 'Enhanced Gaming Plugin'}
        }
        
        self.health_results = {}
        
    def check_plugin_health(self, plugin_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of a single plugin"""
        port = config['port']
        name = config['name']
        
        health_data = {
            'plugin_id': plugin_id,
            'name': name,
            'port': port,
            'status': 'unknown',
            'response_time': None,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            start_time = time.time()
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            end_time = time.time()
            
            health_data['response_time'] = round((end_time - start_time) * 1000, 2)  # ms
            health_data['status'] = 'healthy' if response.status_code == 200 else 'unhealthy'
            health_data['response_code'] = response.status_code
            
            if response.status_code == 200:
                try:
                    health_data['health_info'] = response.json()
                except:
                    health_data['health_info'] = {'message': 'Invalid JSON response'}
            
        except requests.exceptions.ConnectionError:
            health_data['status'] = 'offline'
            health_data['error'] = 'Connection refused - plugin not running'
        except requests.exceptions.Timeout:
            health_data['status'] = 'timeout'
            health_data['error'] = 'Request timeout'
        except Exception as e:
            health_data['status'] = 'error'
            health_data['error'] = str(e)
        
        return health_data
    
    def check_all_plugins(self) -> Dict[str, Any]:
        """Check health of all plugins concurrently"""
        print("Plugin Health Monitoring System")
        print("=" * 60)
        print(f"Checking health of {len(self.plugin_configs)} plugins...")
        print()
        
        # Use ThreadPoolExecutor for concurrent health checks
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_plugin = {
                executor.submit(self.check_plugin_health, plugin_id, config): plugin_id
                for plugin_id, config in self.plugin_configs.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_plugin):
                plugin_id = future_to_plugin[future]
                try:
                    health_data = future.result()
                    self.health_results[plugin_id] = health_data
                except Exception as e:
                    print(f"Error checking {plugin_id}: {e}")
                    self.health_results[plugin_id] = {
                        'plugin_id': plugin_id,
                        'name': self.plugin_configs[plugin_id]['name'],
                        'status': 'error',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
        
        self.display_health_results()
        return self.health_results
    
    def display_health_results(self):
        """Display health check results"""
        print("Health Check Results")
        print("=" * 60)
        
        healthy_count = 0
        unhealthy_count = 0
        offline_count = 0
        error_count = 0
        
        for plugin_id, health_data in self.health_results.items():
            status = health_data['status']
            name = health_data['name']
            port = health_data['port']
            
            if status == 'healthy':
                icon = "✅"
                healthy_count += 1
                response_time = health_data.get('response_time', 'N/A')
                print(f"{icon} {name} (Port {port}): Healthy - {response_time}ms")
            elif status == 'unhealthy':
                icon = "⚠️"
                unhealthy_count += 1
                response_code = health_data.get('response_code', 'N/A')
                print(f"{icon} {name} (Port {port}): Unhealthy - HTTP {response_code}")
            elif status == 'offline':
                icon = "❌"
                offline_count += 1
                print(f"{icon} {name} (Port {port}): Offline - Not running")
            else:
                icon = "🔥"
                error_count += 1
                error_msg = health_data.get('error', 'Unknown error')
                print(f"{icon} {name} (Port {port}): Error - {error_msg}")
        
        print()
        print("Summary:")
        print(f"  Total Plugins: {len(self.health_results)}")
        print(f"  ✅ Healthy: {healthy_count}")
        print(f"  ⚠️ Unhealthy: {unhealthy_count}")
        print(f"  ❌ Offline: {offline_count}")
        print(f"  🔥 Error: {error_count}")
        
        # Calculate overall health percentage
        total_plugins = len(self.health_results)
        health_percentage = (healthy_count / total_plugins) * 100 if total_plugins > 0 else 0
        
        print(f"  Overall Health: {health_percentage:.1f}%")
        
        if health_percentage >= 90:
            print("  Status: 🏆 Excellent")
        elif health_percentage >= 75:
            print("  Status: ✅ Good")
        elif health_percentage >= 50:
            print("  Status: ⚠️ Fair")
        else:
            print("  Status: ❌ Poor")
    
    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_plugins': len(self.health_results),
            'healthy_plugins': sum(1 for h in self.health_results.values() if h['status'] == 'healthy'),
            'unhealthy_plugins': sum(1 for h in self.health_results.values() if h['status'] == 'unhealthy'),
            'offline_plugins': sum(1 for h in self.health_results.values() if h['status'] == 'offline'),
            'error_plugins': sum(1 for h in self.health_results.values() if h['status'] == 'error'),
            'health_percentage': (sum(1 for h in self.health_results.values() if h['status'] == 'healthy') / len(self.health_results)) * 100 if self.health_results else 0,
            'plugin_details': self.health_results
        }
        
        return report
    
    def save_health_report(self, filename: str = 'plugin_health_report.json'):
        """Save health report to file"""
        report = self.generate_health_report()
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nHealth report saved to: {filename}")
        except Exception as e:
            print(f"Error saving health report: {e}")
    
    def monitor_continuously(self, interval: int = 60):
        """Monitor plugins continuously"""
        print(f"Starting continuous monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop monitoring")
        print()
        
        try:
            while True:
                self.check_all_plugins()
                print(f"\nNext check in {interval} seconds...")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")

def main():
    """Main function"""
    monitor = PluginHealthMonitor()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--continuous':
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            monitor.monitor_continuously(interval)
        elif sys.argv[1] == '--save-report':
            monitor.check_all_plugins()
            monitor.save_health_report()
        else:
            print("Usage: python plugin_health_monitor.py [--continuous [interval]] [--save-report]")
    else:
        # Single health check
        monitor.check_all_plugins()
        
        # Save report
        save_report = input("\nSave health report to file? (y/n): ").lower().strip()
        if save_report == 'y':
            monitor.save_health_report()

if __name__ == "__main__":
    main()
