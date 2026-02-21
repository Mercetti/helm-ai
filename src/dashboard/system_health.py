#!/usr/bin/env python3
"""
System Health Monitor
Real-time monitoring and analytics for system infrastructure health
"""

import os
import sys
import time
import json
import logging
import psutil
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

@dataclass
class SystemMetric:
    """System metric data structure"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    category: str  # cpu, memory, disk, network, database, server
    status: str  # healthy, warning, critical
    tags: List[str] = None

@dataclass
class ServiceHealth:
    """Service health status"""
    timestamp: datetime
    service_name: str
    status: str  # up, down, degraded
    response_time_ms: float
    error_rate: float
    uptime_percentage: float
    last_check: datetime
    details: Dict[str, Any] = None

class SystemHealthMonitor:
    """System Health Monitoring System"""
    
    def __init__(self):
        self.logger = logging.getLogger("system_health")
        self.metrics_history = deque(maxlen=1000)  # Last 1000 metrics
        self.service_health = {}
        self.alert_thresholds = {
            "cpu_warning": 70.0,      # 70%
            "cpu_critical": 90.0,     # 90%
            "memory_warning": 80.0,   # 80%
            "memory_critical": 95.0,  # 95%
            "disk_warning": 80.0,     # 80%
            "disk_critical": 95.0,    # 95%
            "response_time_warning": 1000,  # 1 second
            "response_time_critical": 5000, # 5 seconds
            "error_rate_warning": 0.05,  # 5%
            "error_rate_critical": 0.10, # 10%
            "uptime_warning": 99.0,     # 99%
            "uptime_critical": 95.0,    # 95%
        }
        self.system_info = self._get_system_info()
        self.health_stats = {
            "total_checks": 0,
            "healthy_checks": 0,
            "warning_checks": 0,
            "critical_checks": 0,
            "avg_uptime": 100.0,
            "last_restart": None
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "boot_time": datetime.now() - timedelta(hours=24)  # Mock boot time
        }
    
    def record_metric(self, metric_name: str, value: float, unit: str, category: str, status: str = "healthy", tags: List[str] = None):
        """Record a system metric"""
        metric = SystemMetric(
            timestamp=datetime.now(),
            metric_name=metric_name,
            value=value,
            unit=unit,
            category=category,
            status=status,
            tags=tags or []
        )
        
        self.metrics_history.append(metric)
        self.logger.info(f"Recorded metric: {metric_name} = {value} {unit} ({status})")
    
    def record_service_health(self, service_name: str, status: str, response_time_ms: float = 0, 
                          error_rate: float = 0, uptime_percentage: float = 100, details: Dict[str, Any] = None):
        """Record service health status"""
        health = ServiceHealth(
            timestamp=datetime.now(),
            service_name=service_name,
            status=status,
            response_time_ms=response_time_ms,
            error_rate=error_rate,
            uptime_percentage=uptime_percentage,
            last_check=datetime.now(),
            details=details or {}
        )
        
        self.service_health[service_name] = health
        self.logger.info(f"Service health updated: {service_name} = {status}")
    
    def collect_system_metrics(self):
        """Collect current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_status = self._get_status(cpu_percent, "cpu")
            self.record_metric("cpu_usage", cpu_percent, "%", "cpu", cpu_status)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_status = self._get_status(memory_percent, "memory")
            self.record_metric("memory_usage", memory_percent, "%", "memory", memory_status)
            self.record_metric("memory_available_gb", memory.available / (1024**3), "GB", "memory")
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_status = self._get_status(disk_percent, "disk")
            self.record_metric("disk_usage", disk_percent, "%", "disk", disk_status)
            self.record_metric("disk_free_gb", disk.free / (1024**3), "GB", "disk")
            
            # Network metrics
            network = psutil.net_io_counters()
            bytes_sent = network.bytes_sent
            bytes_recv = network.bytes_recv
            self.record_metric("network_bytes_sent", bytes_sent / (1024**2), "MB", "network")
            self.record_metric("network_bytes_recv", bytes_recv / (1024**2), "MB", "network")
            
            # Process metrics
            process_count = len(psutil.pids())
            self.record_metric("process_count", process_count, "count", "system")
            
            # Load average (Unix-like systems)
            if hasattr(psutil, 'getloadavg'):
                load_avg = psutil.getloadavg()[0]  # 1-minute average
                load_status = self._get_status(load_avg * 100, "cpu")  # Normalize to percentage
                self.record_metric("load_average", load_avg, "load", "cpu", load_status)
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    def _get_status(self, value: float, category: str) -> str:
        """Get status based on value and thresholds"""
        if category == "cpu":
            if value >= self.alert_thresholds["cpu_critical"]:
                return "critical"
            elif value >= self.alert_thresholds["cpu_warning"]:
                return "warning"
            else:
                return "healthy"
        elif category == "memory":
            if value >= self.alert_thresholds["memory_critical"]:
                return "critical"
            elif value >= self.alert_thresholds["memory_warning"]:
                return "warning"
            else:
                return "healthy"
        elif category == "disk":
            if value >= self.alert_thresholds["disk_critical"]:
                return "critical"
            elif value >= self.alert_thresholds["disk_warning"]:
                return "warning"
            else:
                return "healthy"
        else:
            return "healthy"
    
    def check_service_health(self):
        """Check health of various services"""
        services = [
            {
                "name": "web_server",
                "check_func": self._check_web_server
            },
            {
                "name": "database",
                "check_func": self._check_database
            },
            {
                "name": "api_gateway",
                "check_func": self._check_api_gateway
            },
            {
                "name": "llm_service",
                "check_func": self._check_llm_service
            }
        ]
        
        for service in services:
            try:
                start_time = time.time()
                health_info = service["check_func"]()
                response_time = (time.time() - start_time) * 1000
                
                self.record_service_health(
                    service_name=service["name"],
                    status=health_info["status"],
                    response_time_ms=response_time,
                    error_rate=health_info.get("error_rate", 0),
                    uptime_percentage=health_info.get("uptime", 100),
                    details=health_info.get("details", {})
                )
            except Exception as e:
                self.logger.error(f"Error checking service {service['name']}: {e}")
                self.record_service_health(
                    service_name=service["name"],
                    status="down",
                    response_time_ms=0,
                    error_rate=1.0,
                    uptime_percentage=0,
                    details={"error": str(e)}
                )
    
    def _check_web_server(self) -> Dict[str, Any]:
        """Check web server health"""
        # Mock web server check
        return {
            "status": "healthy",
            "uptime": 99.9,
            "details": {
                "connections": 150,
                "requests_per_second": 25
            }
        }
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database health"""
        # Mock database check
        return {
            "status": "healthy",
            "uptime": 99.5,
            "details": {
                "connection_pool": "8/10 active",
                "query_time_avg": 45.2,
                "slow_queries": 2
            }
        }
    
    def _check_api_gateway(self) -> Dict[str, Any]:
        """Check API gateway health"""
        # Mock API gateway check
        return {
            "status": "healthy",
            "uptime": 99.8,
            "details": {
                "endpoints_healthy": 15,
                "endpoints_total": 16,
                "rate_limit_active": True
            }
        }
    
    def _check_llm_service(self) -> Dict[str, Any]:
        """Check LLM service health"""
        # Mock LLM service check
        return {
            "status": "healthy",
            "uptime": 99.7,
            "details": {
                "models_loaded": True,
                "response_time_avg": 1250.5,
                "accuracy": 0.92
            }
        }
    
    def get_health_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get health summary for specified time period"""
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
            "system_info": self.system_info,
            "service_health": dict(self.service_health),
            "health_stats": self.health_stats,
            "alerts": self._get_recent_alerts(hours),
            "rends": self._calculate_trends(recent_metrics),
            "recommendations": self._generate_recommendations()
        }
        
        return summary
    
    def _get_recent_alerts(self, hours: int) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        alerts = []
        
        # Check service health for alerts
        for service_name, health in self.service_health.items():
            if health.timestamp > cutoff_time and health.status != "healthy":
                alerts.append({
                    "timestamp": health.timestamp.isoformat(),
                    "type": "service",
                    "severity": "critical" if health.status == "down" else "warning",
                    "service": service_name,
                    "message": f"Service {service_name} is {health.status}"
                })
        
        # Check metrics for alerts
        for metric in self.metrics_history:
            if metric.timestamp > cutoff_time and metric.status != "healthy":
                alerts.append({
                    "timestamp": metric.timestamp.isoformat(),
                    "type": "resource",
                    "severity": metric.status,
                    "metric": metric.metric_name,
                    "message": f"{metric.metric_name} is {metric.status}: {metric.value}{metric.unit}"
                })
        
        return alerts
    
    def _calculate_trends(self, metrics: List[SystemMetric]) -> Dict[str, Any]:
        """Calculate system health trends"""
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
                    
                    trend = "improving" if recent_avg < older_avg else "degrading" if recent_avg > older_avg else "stable"
                    change_percent = ((recent_avg - older_avg) / older_avg) * 100 if older_avg != 0 else 0
                    
                    trends[category] = {
                        "trend": trend,
                        "change_percent": change_percent,
                        "recent_avg": recent_avg,
                        "older_avg": older_avg
                    }
        
        return trends
    
    def _generate_recommendations(self) -> List[str]:
        """Generate system health recommendations"""
        recommendations = []
        
        # Check current metrics for recommendations
        current_metrics = {}
        for metric in list(self.metrics_history)[-10:]:  # Last 10 metrics
            current_metrics[metric.metric_name] = metric.value
        
        # CPU recommendations
        if current_metrics.get("cpu_usage", 0) > self.alert_thresholds["cpu_warning"]:
            recommendations.append("Consider scaling CPU resources or optimizing processes")
        
        # Memory recommendations
        if current_metrics.get("memory_usage", 0) > self.alert_thresholds["memory_warning"]:
            recommendations.append("Consider adding more RAM or optimizing memory usage")
        
        # Disk recommendations
        if current_metrics.get("disk_usage", 0) > self.alert_thresholds["disk_warning"]:
            recommendations.append("Consider disk cleanup or storage expansion")
        
        # Service recommendations
        for service_name, health in self.service_health.items():
            if health.status == "down":
                recommendations.append(f"URGENT: Service {service_name} is down - investigate immediately")
            elif health.status == "degraded":
                recommendations.append(f"Service {service_name} is degraded - monitor closely")
        
        return recommendations

# Global system health monitor instance
system_health_monitor = SystemHealthMonitor()
