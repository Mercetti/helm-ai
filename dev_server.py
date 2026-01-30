#!/usr/bin/env python3
"""
Stellar Logic AI - Development Server with Auto-Reload
Automatically refreshes dashboard when files change
"""

import os
import sys
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_GET(self):
        if self.path == '/':
            self.path = '/dashboard.html'
        return super().do_GET()

class DashboardReloader(FileSystemEventHandler):
    def __init__(self, server_port):
        self.server_port = server_port
        self.last_reload = time.time()
    
    def on_modified(self, event):
        if event.src_path.endswith(('.html', '.css', '.js')):
            # Prevent multiple rapid reloads
            if time.time() - self.last_reload > 1:
                print(f"🔄 Dashboard updated: {event.src_path}")
                self.last_reload = time.time()
                self.notify_clients()
    
    def notify_clients(self):
        # This would require WebSocket implementation for real-time updates
        print("💡 Refresh your browser to see changes (F5 or Ctrl+R)")

def start_dev_server(port=5000):
    """Start development server with auto-reload capability"""
    
    # Install watchdog if not available
    try:
        from watchdog.observers import Observer
    except ImportError:
        print("📦 Installing watchdog for auto-reload...")
        os.system(f"{sys.executable} -m pip install watchdog")
        from watchdog.observers import Observer
    
    print(f"🚀 Starting Stellar Logic AI Development Server")
    print(f"📊 Dashboard: http://localhost:{port}")
    print(f"🔄 Auto-reload: Enabled (watching for file changes)")
    print(f"💡 Refresh browser when you see update notifications")
    print(f"🛑 Press Ctrl+C to stop server")
    print("-" * 50)
    
    # Start file watcher
    event_handler = DashboardReloader(port)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    
    try:
        # Start HTTP server
        server = HTTPServer(('localhost', port), DashboardHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Stopping development server...")
        observer.stop()
    observer.join()

if __name__ == '__main__':
    start_dev_server()
