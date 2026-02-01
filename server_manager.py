#!/usr/bin/env python3
"""
Stellar Logic AI Plugin Server Manager
Manages startup and shutdown of all plugin servers
"""

import subprocess
import time
import signal
import sys
import os

# Plugin configurations
PLUGINS = {
    'healthcare': {'port': 5001, 'script': 'healthcare_server.py'},
    'financial': {'port': 5002, 'script': 'financial_server.py'},
    'manufacturing': {'port': 5003, 'script': 'manufacturing_server.py'},
    'automotive': {'port': 5004, 'script': 'automotive_server.py'},
    'government': {'port': 5005, 'script': 'government_server.py'},
    'real_estate': {'port': 5006, 'script': 'real_estate_server.py'},
    'education': {'port': 5007, 'script': 'education_server.py'},
    'ecommerce': {'port': 5008, 'script': 'ecommerce_server.py'},
    'cybersecurity': {'port': 5009, 'script': 'cybersecurity_server.py'},
    'gaming': {'port': 5010, 'script': 'gaming_server.py'},
    'mobile': {'port': 5011, 'script': 'mobile_server.py'},
    'iot': {'port': 5012, 'script': 'iot_server.py'},
    'blockchain': {'port': 5013, 'script': 'blockchain_server.py'},
    'ai_core': {'port': 5014, 'script': 'ai_core_server.py'},
}

class ServerManager:
    def __init__(self):
        self.processes = {}
    
    def start_server(self, plugin_name, config):
        """Start a single plugin server"""
        try:
            print(f"Starting {plugin_name} server on port {config['port']}...")
            
            # Check if port is available
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', config['port'])) == 0:
                    print(f"Port {config['port']} already in use for {plugin_name}")
                    return False
            
            # Start the server
            process = subprocess.Popen([
                sys.executable, config['script']
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes[plugin_name] = process
            time.sleep(2)  # Give server time to start
            
            # Check if process is still running
            if process.poll() is None:
                print(f"✅ {plugin_name} server started successfully")
                return True
            else:
                print(f"❌ {plugin_name} server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting {plugin_name}: {e}")
            return False
    
    def start_all_servers(self):
        """Start all plugin servers"""
        print("🚀 Starting all Stellar Logic AI plugin servers...")
        
        success_count = 0
        for plugin_name, config in PLUGINS.items():
            if self.start_server(plugin_name, config):
                success_count += 1
        
        print(f"\n✅ Started {success_count}/{len(PLUGINS)} servers")
        
        if success_count == len(PLUGINS):
            print("🎉 All plugin servers are running!")
        else:
            print("⚠️  Some servers failed to start")
        
        return success_count
    
    def stop_server(self, plugin_name):
        """Stop a single plugin server"""
        if plugin_name in self.processes:
            try:
                self.processes[plugin_name].terminate()
                self.processes[plugin_name].wait(timeout=5)
                print(f"✅ Stopped {plugin_name} server")
                del self.processes[plugin_name]
            except subprocess.TimeoutExpired:
                self.processes[plugin_name].kill()
                print(f"🔨 Force killed {plugin_name} server")
                del self.processes[plugin_name]
            except Exception as e:
                print(f"❌ Error stopping {plugin_name}: {e}")
    
    def stop_all_servers(self):
        """Stop all plugin servers"""
        print("🛑 Stopping all plugin servers...")
        
        for plugin_name in list(self.processes.keys()):
            self.stop_server(plugin_name)
        
        print("✅ All servers stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Received shutdown signal...")
        self.stop_all_servers()
        sys.exit(0)

def main():
    if len(sys.argv) < 2:
        print("Usage: python server_manager.py [start|stop|restart]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    manager = ServerManager()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    if command == 'start':
        manager.start_all_servers()
        try:
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop_all_servers()
    
    elif command == 'stop':
        manager.stop_all_servers()
    
    elif command == 'restart':
        manager.stop_all_servers()
        time.sleep(2)
        manager.start_all_servers()
    
    else:
        print("Unknown command. Use start, stop, or restart")

if __name__ == '__main__':
    main()
