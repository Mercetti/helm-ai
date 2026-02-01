#!/usr/bin/env python3
"""
Stellar Logic AI Performance Monitoring
Real-time performance monitoring and alerting
"""

import time
import threading
import psutil
from datetime import datetime
from collections import deque

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'cpu_usage': deque(maxlen=60),
            'memory_usage': deque(maxlen=60),
            'response_time': deque(maxlen=1000),
            'throughput': deque(maxlen=60),
            'error_rate': deque(maxlen=60)
        }
        
        self.thresholds = {
            'cpu_warning': 70.0,
            'cpu_critical': 90.0,
            'memory_warning': 70.0,
            'memory_critical': 90.0,
            'response_time_warning': 1.0,
            'response_time_critical': 2.0,
            'error_rate_warning': 5.0,
            'error_rate_critical': 10.0
        }
        
        self.alerts = []
        self.monitoring = True
        self.monitor_thread = None
        self.lock = threading.Lock()
        
        # Start monitoring
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("✅ Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("🛑 Performance monitoring stopped")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                
                # Store metrics
                with self.lock:
                    self.metrics['cpu_usage'].append(cpu_percent)
                    self.metrics['memory_usage'].append(memory_percent)
                    self.metrics['throughput'].append(self.get_current_throughput())
                    self.metrics['error_rate'].append(self.get_current_error_rate())
                
                # Check thresholds
                self.check_thresholds()
                
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
    
    def get_current_throughput(self):
        """Get current throughput (requests per second)"""
        return 100.0  # Simulated throughput
    
    def get_current_error_rate(self):
        """Get current error rate"""
        return 0.5  # Simulated error rate
    
    def check_thresholds(self):
        """Check performance thresholds and create alerts"""
        current_time = datetime.now()
        
        # Check CPU usage
        if self.metrics['cpu_usage']:
            cpu_avg = sum(self.metrics['cpu_usage']) / len(self.metrics['cpu_usage'])
            
            if cpu_avg > self.thresholds['cpu_critical']:
                self.create_alert('CRITICAL', 'CPU', f"CPU usage: {cpu_avg:.1f}%")
            elif cpu_avg > self.thresholds['cpu_warning']:
                self.create_alert('WARNING', 'CPU', f"CPU usage: {cpu_avg:.1f}%")
        
        # Check memory usage
        if self.metrics['memory_usage']:
            memory_avg = sum(self.metrics['memory_usage']) / len(self.metrics['memory_usage'])
            
            if memory_avg > self.thresholds['memory_critical']:
                self.create_alert('CRITICAL', 'Memory', f"Memory usage: {memory_avg:.1f}%")
            elif memory_avg > self.thresholds['memory_warning']:
                self.create_alert('WARNING', 'Memory', f"Memory usage: {memory_avg:.1f}%")
    
    def create_alert(self, severity, metric, message):
        """Create performance alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'metric': metric,
            'message': message
        }
        
        # Avoid duplicate alerts
        if self.alerts:
            last_alert = self.alerts[-1]
            if (last_alert['severity'] == severity and 
                last_alert['metric'] == metric and 
                last_alert['message'] == message):
                return
        
        self.alerts.append(alert)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        print(f"🚨 {severity} ALERT - {metric}: {message}")
    
    def get_metrics(self):
        """Get current metrics"""
        with self.lock:
            return {
                'cpu_usage': {
                    'current': self.metrics['cpu_usage'][-1] if self.metrics['cpu_usage'] else 0,
                    'average': sum(self.metrics['cpu_usage']) / len(self.metrics['cpu_usage']) if self.metrics['cpu_usage'] else 0,
                    'max': max(self.metrics['cpu_usage']) if self.metrics['cpu_usage'] else 0
                },
                'memory_usage': {
                    'current': self.metrics['memory_usage'][-1] if self.metrics['memory_usage'] else 0,
                    'average': sum(self.metrics['memory_usage']) / len(self.metrics['memory_usage']) if self.metrics['memory_usage'] else 0,
                    'max': max(self.metrics['memory_usage']) if self.metrics['memory_usage'] else 0
                },
                'alerts': self.alerts[-10:]  # Last 10 alerts
            }

# Global performance monitor
performance_monitor = PerformanceMonitor()

if __name__ == '__main__':
    print("📊 STELLAR LOGIC AI PERFORMANCE MONITOR")
    print(f"📊 Current Metrics: {performance_monitor.get_metrics()}")
