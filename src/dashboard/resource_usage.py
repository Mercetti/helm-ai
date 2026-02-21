#!/usr/bin/env python3
"""
Resource Usage Monitoring
Real-time monitoring and analytics for CPU, memory, disk, and network usage with alerting
"""

import os
import sys
import time
import json
import logging
import threading
import psutil
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

@dataclass
class ResourceMetric:
    """Resource usage metric data structure"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    category: str  # cpu, memory, disk, network
    tags: List[str] = None

@dataclass
class CPUMetrics:
    """CPU metrics data structure"""
    timestamp: datetime
    cpu_percent: float
    cpu_count: int
    load_average: List[float]
    per_cpu_percent: List[float]
    cpu_freq_mhz: float
    context_switches: int
    interrupts: int

@dataclass
class MemoryMetrics:
    """Memory metrics data structure"""
    timestamp: datetime
    total_gb: float
    available_gb: float
    used_gb: float
    percent_used: float
    swap_total_gb: float
    swap_used_gb: float
    swap_percent: float
    buffers_gb: float
    cached_gb: float

@dataclass
class DiskMetrics:
    """Disk metrics data structure"""
    timestamp: datetime
    device_name: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent_used: float
    read_mb_per_sec: float
    write_mb_per_sec: float
    read_count: int
    write_count: int
    read_time_ms: float
    write_time_ms: float

@dataclass
class NetworkMetrics:
    """Network metrics data structure"""
    timestamp: datetime
    interface_name: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int

class ResourceUsageMonitor:
    """Resource Usage Monitoring System"""
    
    def __init__(self):
        self.logger = logging.getLogger("resource_usage")
        self.metrics_history = deque(maxlen=1000)  # Last 1000 metrics
        self.cpu_metrics = {}
        self.memory_metrics = {}
        self.disk_metrics = {}
        self.network_metrics = {}
        self.alert_thresholds = {
            "cpu_warning": 70.0,      # 70%
            "cpu_critical": 90.0,     # 90%
            "memory_warning": 80.0,   # 80%
            "memory_critical": 95.0,   # 95%
            "disk_warning": 80.0,     # 80%
            "disk_critical": 95.0,    # 95%
            "network_error_warning": 100,  # 100 errors/min
            "network_error_critical": 500, # 500 errors/min
        }
        self.resource_stats = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0,
            "network_throughput": 0,
            "system_load": 0,
            "active_processes": 0,
            "uptime_hours": 0,
            "last_update": datetime.now()
        }
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_interval = 30  # seconds
    
    def start_monitoring(self):
        """Start resource usage monitoring"""
        if self.monitoring_active:
            self.logger.warning("Resource usage monitoring is already running")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Resource usage monitoring started")
    
    def stop_monitoring(self):
        """Stop resource usage monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        self.logger.info("Resource usage monitoring stopped")
    
    def record_metric(self, metric_name: str, value: float, unit: str, category: str, tags: List[str] = None):
        """Record a resource usage metric"""
        metric = ResourceMetric(
            timestamp=datetime.now(),
            metric_name=metric_name,
            value=value,
            unit=unit,
            category=category,
            tags=tags or []
        )
        
        self.metrics_history.append(metric)
        self.logger.info(f"Recorded resource metric: {metric_name} = {value} {unit}")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect resource metrics
                self._collect_cpu_metrics()
                self._collect_memory_metrics()
                self._collect_disk_metrics()
                self._collect_network_metrics()
                
                # Update resource stats
                self._update_resource_stats()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in resource monitoring loop: {e}")
                time.sleep(5)
    
    def _collect_cpu_metrics(self):
        """Collect CPU metrics"""
        try:
            # CPU percentage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # CPU count
            cpu_count = psutil.cpu_count()
            
            # Load average
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            
            # Per-CPU percentage
            per_cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            
            # CPU frequency
            cpu_freq = psutil.cpu_freq()
            cpu_freq_mhz = cpu_freq.current if cpu_freq else 0
            
            # Context switches and interrupts
            cpu_stats = psutil.cpu_stats()
            context_switches = cpu_stats.ctx_switches if cpu_stats else 0
            interrupts = cpu_stats.interrupts if cpu_stats else 0
            
            metrics = CPUMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                cpu_count=cpu_count,
                load_average=list(load_avg),
                per_cpu_percent=list(per_cpu_percent),
                cpu_freq_mhz=cpu_freq_mhz,
                context_switches=context_switches,
                interrupts=interrupts
            )
            
            self.cpu_metrics = metrics
            self.record_metric("cpu_usage", cpu_percent, "%", "cpu")
            
        except Exception as e:
            self.logger.error(f"Error collecting CPU metrics: {e}")
    
    def _collect_memory_metrics(self):
        """Collect memory metrics"""
        try:
            # Virtual memory
            virtual_memory = psutil.virtual_memory()
            total_gb = virtual_memory.total / (1024**3)
            available_gb = virtual_memory.available / (1024**3)
            used_gb = virtual_memory.used / (1024**3)
            percent_used = virtual_memory.percent
            
            # Swap memory
            swap_memory = psutil.swap_memory()
            swap_total_gb = swap_memory.total / (1024**3)
            swap_used_gb = swap_memory.used / (1024**3)
            swap_percent = swap_memory.percent
            
            # Buffers and cached
            if hasattr(virtual_memory, 'buffers'):
                buffers_gb = virtual_memory.buffers / (1024**3)
            else:
                buffers_gb = 0
            
            if hasattr(virtual_memory, 'cached'):
                cached_gb = virtual_memory.cached / (1024**3)
            else:
                cached_gb = 0
            
            metrics = MemoryMetrics(
                timestamp=datetime.now(),
                total_gb=total_gb,
                available_gb=available_gb,
                used_gb=used_gb,
                percent_used=percent_used,
                swap_total_gb=swap_total_gb,
                swap_used_gb=swap_used_gb,
                swap_percent=swap_percent,
                buffers_gb=buffers_gb,
                cached_gb=cached_gb
            )
            
            self.memory_metrics = metrics
            self.record_metric("memory_usage", percent_used, "%", "memory")
            
        except Exception as e:
            self.logger.error(f"Error collecting memory metrics: {e}")
    
    def _collect_disk_metrics(self):
        """Collect disk metrics"""
        try:
            # Get disk partitions
            disk_partitions = psutil.disk_partitions()
            
            for partition in disk_partitions:
                if partition.device.startswith('/dev/'):  # Linux/Unix style
                    try:
                        disk_usage = psutil.disk_usage(partition.mountpoint)
                        disk_io = psutil.disk_io_counters(perdisk=True)
                        
                        # Get device name without path
                        device_name = partition.device.split('/')[-1]
                        
                        total_gb = disk_usage.total / (1024**3)
                        used_gb = disk_usage.used / (1024**3)
                        free_gb = disk_usage.free / (1024**3)
                        percent_used = (used_gb / total_gb) * 100 if total_gb > 0 else 0
                        
                        # Get I/O stats for this device
                        io_stats = disk_io.get(device_name, {})
                        read_mb_per_sec = io_stats.get('read_bytes', 0) / (1024**2) if io_stats else 0
                        write_mb_per_sec = io_stats.get('write_bytes', 0) / (1024**2) if io_stats else 0
                        read_count = io_stats.get('read_count', 0) if io_stats else 0
                        write_count = io_stats.get('write_count', 0) if io_stats else 0
                        read_time_ms = io_stats.get('read_time', 0) if io_stats else 0
                        write_time_ms = io_stats.get('write_time', 0) if io_stats else 0
                        
                        metrics = DiskMetrics(
                            timestamp=datetime.now(),
                            device_name=device_name,
                            total_gb=total_gb,
                            used_gb=used_gb,
                            free_gb=free_gb,
                            percent_used=percent_used,
                            read_mb_per_sec=read_mb_per_sec,
                            write_mb_per_sec=write_mb_per_sec,
                            read_count=read_count,
                            write_count=write_count,
                            read_time_ms=read_time_ms,
                            write_time_ms=write_time_ms
                        )
                        
                        self.disk_metrics[device_name] = metrics
                        self.record_metric(f"disk_usage_{device_name}", percent_used, "%", "disk")
                        
                    except Exception as e:
                        self.logger.error(f"Error collecting disk metrics for {partition.device}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error collecting disk metrics: {e}")
    
    def _collect_network_metrics(self):
        """Collect network metrics"""
        try:
            # Get network interfaces
            network_interfaces = psutil.net_io_counters(pernic=True)
            
            for interface_name, interface_stats in network_interfaces.items():
                # Skip loopback interfaces
                if not interface_name.startswith('lo'):
                    metrics = NetworkMetrics(
                        timestamp=datetime.now(),
                        interface_name=interface_name,
                        bytes_sent=interface_stats.bytes_sent,
                        bytes_recv=interface_stats.bytes_recv,
                        packets_sent=interface_stats.packets_sent,
                        packets_recv=interface_stats.packets_recv,
                        errin=interface_stats.errin,
                        errout=interface_stats.errout,
                        dropin=interface_stats.dropin,
                        dropout=interface_stats.dropout
                    )
                    
                    self.network_metrics[interface_name] = metrics
                    
                    # Calculate throughput (bytes per second)
                    total_bytes = interface_stats.bytes_sent + interface_stats.bytes_recv
                    self.record_metric(f"network_throughput_{interface_name}", total_bytes, "bytes", "network")
                    
        except Exception as e:
            self.logger.error(f"Error collecting network metrics: {e}")
    
    def _update_resource_stats(self):
        """Update overall resource statistics"""
        try:
            # Update CPU usage
            if self.cpu_metrics:
                self.resource_stats["cpu_usage"] = self.cpu_metrics.cpu_percent
                self.resource_stats["system_load"] = self.cpu_metrics.load_average[0] if self.cpu_metrics.load_average else 0
            
            # Update memory usage
            if self.memory_metrics:
                self.resource_stats["memory_usage"] = self.memory_metrics.percent_used
            
            # Update disk usage (average across all disks)
            if self.disk_metrics:
                disk_usages = [m.percent_used for m in self.disk_metrics.values()]
                if disk_usages:
                    self.resource_stats["disk_usage"] = sum(disk_usages) / len(disk_usages)
            
            # Update network throughput
            if self.network_metrics:
                total_bytes = sum(m.bytes_sent + m.bytes_recv for m in self.network_metrics.values())
                self.resource_stats["network_throughput"] = total_bytes
            
            # Update process count
            self.resource_stats["active_processes"] = len(psutil.pids())
            
            # Update uptime (mock calculation)
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            self.resource_stats["uptime_hours"] = uptime_seconds / 3600
            
            self.resource_stats["last_update"] = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error updating resource stats: {e}")
    
    def get_resource_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get resource usage summary for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp > cutoff_time
        ]
        
        # Calculate summary
        summary = {
            "period_hours": hours,
            "total_metrics": len(recent_metrics),
            "resource_stats": self.resource_stats,
            "cpu_metrics": dict(self.cpu_metrics),
            "memory_metrics": dict(self.memory_metrics),
            "disk_metrics": dict(self.disk_metrics),
            "network_metrics": dict(self.network_metrics),
            "alerts": self._get_recent_alerts(hours),
            "rends": self._calculate_trends(recent_metrics),
            "recommendations": self._generate_recommendations()
        }
        
        return summary
    
    def _get_recent_alerts(self, hours: int) -> List[Dict[str, Any]]:
        """Get recent resource usage alerts"""
        alerts = []
        
        # Check CPU alerts
        if self.resource_stats["cpu_usage"] > self.alert_thresholds["cpu_critical"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "cpu",
                "severity": "critical",
                "message": f"CPU usage ({self.resource_stats['cpu_usage']:.1f}%) exceeds critical threshold ({self.alert_thresholds['cpu_critical']}%)"
            })
        elif self.resource_stats["cpu_usage"] > self.alert_thresholds["cpu_warning"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "cpu",
                "severity": "warning",
                "message": f"CPU usage ({self.resource_stats['cpu_usage']:.1f}%) exceeds warning threshold ({self.alert_thresholds['cpu_warning']}%)"
            })
        
        # Check memory alerts
        if self.resource_stats["memory_usage"] > self.alert_thresholds["memory_critical"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "memory",
                "severity": "critical",
                "message": f"Memory usage ({self.resource_stats['memory_usage']:.1f}%) exceeds critical threshold ({self.alert_thresholds['memory_critical']}%)"
            })
        elif self.resource_stats["memory_usage"] > self.alert_thresholds["memory_warning"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "memory",
                "severity": "warning",
                "message": f"Memory usage ({self.resource_stats['memory_usage']:.1f}%) exceeds warning threshold ({self.alert_thresholds['memory_warning']}%)"
            })
        
        # Check disk alerts
        if self.resource_stats["disk_usage"] > self.alert_thresholds["disk_critical"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "disk",
                "severity": "critical",
                "message": f"Disk usage ({self.resource_stats['disk_usage']:.1f}%) exceeds critical threshold ({self.alert_thresholds['disk_critical']}%)"
            })
        elif self.resource_stats["disk_usage"] > self.alert_thresholds["disk_warning"]:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "disk",
                "severity": "warning",
                "message": f"Disk usage ({self.resource_stats['disk_usage']:.1f}%) exceeds warning threshold ({self.alert_thresholds['disk_warning']}%)"
            })
        
        return alerts
    
    def _calculate_trends(self, metrics: List[ResourceMetric]) -> Dict[str, Any]:
        """Calculate resource usage trends"""
        if len(metrics) < 10:
            return {}
        
        # Group metrics by category
        categories = defaultdict(list)
        for metric in metrics:
            categories[metric.category].append(metric)
        
        trends = {}
        for category, category_metrics in categories.items():
            if len(category_metrics) >= 2:
                recent_values = [m.value for m in category_metrics[-10:]]
                older_values = [m.value for m in category_metrics[-20:-10]]
                
                if recent_values and older_values:
                    recent_avg = sum(recent_values) / len(recent_values)
                    older_avg = sum(older_values) / len(older_values)
                    
                    trend = "increasing" if recent_avg > older_avg else "decreasing" if recent_avg < older_avg else "stable"
                    change_percent = ((recent_avg - older_avg) / older_avg) * 100 if older_avg != 0 else 0
                    
                    trends[category] = {
                        "trend": trend,
                        "change_percent": change_percent,
                        "recent_avg": recent_avg,
                        "older_avg": older_avg
                    }
        
        return trends
    
    def _generate_recommendations(self) -> List[str]:
        """Generate resource usage recommendations"""
        recommendations = []
        
        # CPU recommendations
        if self.resource_stats["cpu_usage"] > self.alert_thresholds["cpu_warning"]:
            recommendations.append("Consider scaling CPU resources or optimizing CPU-intensive processes")
        
        # Memory recommendations
        if self.resource_stats["memory_usage"] > self.alert_thresholds["memory_warning"]:
            recommendations.append("Consider adding more RAM or optimizing memory usage")
        
        # Disk recommendations
        if self.resource_stats["disk_usage"] > self.alert_thresholds["disk_warning"]:
            recommendations.append("Consider disk cleanup or storage expansion")
        
        # System load recommendations
        if self.resource_stats["system_load"] > 2.0:  # High system load
            recommendations.append("Investigate high system load and optimize processes")
        
        # Process recommendations
        if self.resource_stats["active_processes"] > 500:  # High process count
            recommendations.append("Review and optimize running processes")
        
        return recommendations

# Global resource usage monitor instance
resource_usage_monitor = ResourceUsageMonitor()
