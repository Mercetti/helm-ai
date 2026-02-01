#!/usr/bin/env python3
"""
Plugin Server Startup Script
Manages startup and shutdown of all Helm AI plugins
"""

import os
import sys
import time
import signal
import subprocess
import threading
from typing import Dict, List, Any
from pathlib import Path
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plugin_config_manager import config_manager
from plugin_health_monitor import PluginHealthMonitor

class PluginServerManager:
    """Manages startup and shutdown of plugin servers"""
    
    def __init__(self):
        self.processes = {}
        self.startup_order = [
            'helm-api',
            'healthcare-plugin',
            'government-defense-plugin',
            'automotive-transportation-plugin',
            'real-estate-plugin',
            'financial-plugin',
            'manufacturing-plugin',
            'education-plugin',
            'ecommerce-plugin',
            'media-entertainment-plugin',
            'pharmaceutical-plugin',
            'enterprise-plugin',
            'gaming-plugin'
        ]
        self.health_monitor = PluginHealthMonitor()
        self.shutdown_requested = False
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        self.shutdown_requested = True
        self.shutdown_all_plugins()
        sys.exit(0)
    
    def start_plugin(self, plugin_id: str) -> bool:
        """Start a single plugin"""
        config = config_manager.get_plugin_config(plugin_id)
        if not config or not config.enabled:
            print(f"❌ Plugin {plugin_id} is not enabled or configured")
            return False
        
        print(f"🚀 Starting {config.name} on port {config.port}...")
        
        try:
            # Create startup command based on plugin type
            if plugin_id == 'helm-api':
                cmd = [
                    sys.executable, '-m', 'flask', 'run',
                    '--host', config.host,
                    '--port', str(config.port),
                    '--debug', str(config.debug).lower()
                ]
                env = os.environ.copy()
                env['FLASK_APP'] = 'api_server.py'
                env['FLASK_ENV'] = config.environment
            else:
                # For plugins, use the plugin-specific server
                plugin_file = f"{plugin_id.replace('-', '_')}_server.py"
                cmd = [sys.executable, plugin_file]
                env = os.environ.copy()
                env['PLUGIN_PORT'] = str(config.port)
                env['PLUGIN_TYPE'] = plugin_id.replace('-', '_')
                env['FLASK_ENV'] = config.environment
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[plugin_id] = process
            
            # Wait a moment for startup
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                print(f"✅ {config.name} started successfully (PID: {process.pid})")
                return True
            else:
                print(f"❌ {config.name} failed to start")
                stdout, stderr = process.communicate()
                if stderr:
                    print(f"   Error: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting {config.name}: {e}")
            return False
    
    def stop_plugin(self, plugin_id: str) -> bool:
        """Stop a single plugin"""
        if plugin_id not in self.processes:
            print(f"⚠️ Plugin {plugin_id} is not running")
            return True
        
        process = self.processes[plugin_id]
        config = config_manager.get_plugin_config(plugin_id)
        
        print(f"🛑 Stopping {config.name}...")
        
        try:
            # Try graceful shutdown first
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
                print(f"✅ {config.name} stopped gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                process.kill()
                print(f"⚠️ {config.name} force killed")
            
            del self.processes[plugin_id]
            return True
            
        except Exception as e:
            print(f"❌ Error stopping {config.name}: {e}")
            return False
    
    def start_all_plugins(self) -> Dict[str, bool]:
        """Start all enabled plugins"""
        print("Starting All Helm AI Plugins")
        print("=" * 50)
        
        results = {}
        enabled_plugins = config_manager.get_enabled_plugins()
        
        # Start plugins in order
        for plugin_id in self.startup_order:
            if plugin_id in enabled_plugins:
                results[plugin_id] = self.start_plugin(plugin_id)
                time.sleep(1)  # Brief pause between startups
            else:
                print(f"⏭️ Skipping {plugin_id} (disabled)")
                results[plugin_id] = True  # Not an error if disabled
        
        # Print startup summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        print(f"\nStartup Summary:")
        print(f"  Total: {total}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {total - successful}")
        
        if successful == total:
            print("🎉 All plugins started successfully!")
        else:
            print("⚠️ Some plugins failed to start")
        
        return results
    
    def shutdown_all_plugins(self):
        """Shutdown all running plugins"""
        print("\nShutting Down All Plugins")
        print("=" * 50)
        
        # Stop in reverse order
        for plugin_id in reversed(self.startup_order):
            if plugin_id in self.processes:
                self.stop_plugin(plugin_id)
        
        print("✅ All plugins shut down")
    
    def restart_plugin(self, plugin_id: str) -> bool:
        """Restart a specific plugin"""
        print(f"🔄 Restarting {plugin_id}...")
        
        # Stop if running
        if plugin_id in self.processes:
            self.stop_plugin(plugin_id)
            time.sleep(2)
        
        # Start again
        return self.start_plugin(plugin_id)
    
    def get_plugin_status(self) -> Dict[str, Any]:
        """Get status of all plugins"""
        status = {}
        
        for plugin_id, process in self.processes.items():
            config = config_manager.get_plugin_config(plugin_id)
            
            if process.poll() is None:
                status[plugin_id] = {
                    'name': config.name,
                    'status': 'running',
                    'pid': process.pid,
                    'port': config.port,
                    'uptime': 'unknown'  # Could track start time
                }
            else:
                status[plugin_id] = {
                    'name': config.name,
                    'status': 'stopped',
                    'port': config.port,
                    'exit_code': process.returncode
                }
        
        return status
    
    def monitor_plugins(self, interval: int = 30):
        """Monitor plugin health continuously"""
        print(f"Starting plugin monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            while not self.shutdown_requested:
                print(f"\n{'='*60}")
                print(f"Plugin Status Check - {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*60}")
                
                # Check process status
                status = self.get_plugin_status()
                for plugin_id, info in status.items():
                    if info['status'] == 'running':
                        print(f"✅ {info['name']}: Running (PID: {info['pid']}, Port: {info['port']})")
                    else:
                        print(f"❌ {info['name']}: Stopped (Exit code: {info.get('exit_code', 'unknown')})")
                
                # Check health endpoints
                print(f"\nHealth Check Results:")
                health_results = self.health_monitor.check_all_plugins()
                
                print(f"\nNext check in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
    
    def start_with_monitoring(self, interval: int = 30):
        """Start plugins and begin monitoring"""
        # Start all plugins
        startup_results = self.start_all_plugins()
        
        if all(startup_results.values()):
            # Start monitoring in a separate thread
            monitor_thread = threading.Thread(target=self.monitor_plugins, args=(interval,))
            monitor_thread.daemon = True
            monitor_thread.start()
            
            try:
                # Keep main thread alive
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down...")
                self.shutdown_all_plugins()
        else:
            print("❌ Not starting monitoring due to startup failures")
            self.shutdown_all_plugins()

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python plugin_server_manager.py <command> [options]")
        print("\nCommands:")
        print("  start              Start all plugins")
        print("  stop               Stop all plugins")
        print("  restart            Restart all plugins")
        print("  restart <plugin>   Restart specific plugin")
        print("  status             Show plugin status")
        print("  monitor            Start plugins and monitor")
        print("  health             Check plugin health")
        print("\nExamples:")
        print("  python plugin_server_manager.py start")
        print("  python plugin_server_manager.py restart healthcare-plugin")
        print("  python plugin_server_manager.py monitor")
        return
    
    command = sys.argv[1].lower()
    manager = PluginServerManager()
    
    if command == 'start':
        manager.start_all_plugins()
    
    elif command == 'stop':
        manager.shutdown_all_plugins()
    
    elif command == 'restart':
        if len(sys.argv) > 2:
            plugin_id = sys.argv[2]
            manager.restart_plugin(plugin_id)
        else:
            manager.shutdown_all_plugins()
            time.sleep(3)
            manager.start_all_plugins()
    
    elif command == 'status':
        status = manager.get_plugin_status()
        print("Plugin Status")
        print("=" * 50)
        for plugin_id, info in status.items():
            if info['status'] == 'running':
                print(f"✅ {info['name']}: Running (PID: {info['pid']}, Port: {info['port']})")
            else:
                print(f"❌ {info['name']}: Stopped")
    
    elif command == 'monitor':
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        manager.start_with_monitoring(interval)
    
    elif command == 'health':
        manager.health_monitor.check_all_plugins()
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
