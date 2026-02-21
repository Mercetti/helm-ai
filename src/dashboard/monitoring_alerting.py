#!/usr/bin/env python3
"""
Monitoring & Alerting System
Real-time system monitoring, alerting, and health checks
"""

import os
import sys
import time
import json
import logging
import threading
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

class MetricType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"

@dataclass
class Alert:
    """Alert data structure"""
    alert_id: str
    name: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    metric_type: MetricType
    current_value: float
    threshold_value: float
    triggered_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    acknowledged_by: Optional[str]
    resolved_by: Optional[str]
    affected_services: List[str]
    notification_sent: bool

@dataclass
class Metric:
    """Metric data structure"""
    metric_id: str
    name: str
    type: MetricType
    value: float
    unit: str
    timestamp: datetime
    service_name: str
    host_name: str
    tags: Dict[str, str]

@dataclass
class HealthCheck:
    """Health check data structure"""
    check_id: str
    name: str
    service_name: str
    endpoint: str
    status: str
    response_time_ms: float
    last_checked: datetime
    consecutive_failures: int
    max_failures: int
    timeout_seconds: int

@dataclass
class NotificationChannel:
    """Notification channel data structure"""
    channel_id: str
    name: str
    type: str
    config: Dict[str, Any]
    enabled: bool
    last_sent: Optional[datetime]

class MonitoringAlertingSystem:
    """Monitoring & Alerting System"""
    
    def __init__(self):
        self.logger = logging.getLogger("monitoring_alerting_system")
        self.alerts = {}
        self.metrics = deque(maxlen=10000)
        self.health_checks = {}
        self.notification_channels = {}
        self.alert_rules = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Initialize with sample data
        self._initialize_alert_rules()
        self._initialize_notification_channels()
        self._initialize_health_checks()
        self._initialize_sample_metrics()
    
    def _initialize_alert_rules(self):
        """Initialize with sample alert rules"""
        rules = [
            {
                "rule_id": "cpu_high",
                "name": "High CPU Usage",
                "description": "CPU usage exceeds 80%",
                "metric_type": MetricType.CPU,
                "threshold": 80.0,
                "operator": ">",
                "duration_seconds": 300,
                "severity": AlertSeverity.WARNING,
                "enabled": True
            },
            {
                "rule_id": "cpu_critical",
                "name": "Critical CPU Usage",
                "description": "CPU usage exceeds 95%",
                "metric_type": MetricType.CPU,
                "threshold": 95.0,
                "operator": ">",
                "duration_seconds": 60,
                "severity": AlertSeverity.CRITICAL,
                "enabled": True
            },
            {
                "rule_id": "memory_high",
                "name": "High Memory Usage",
                "description": "Memory usage exceeds 85%",
                "metric_type": MetricType.MEMORY,
                "threshold": 85.0,
                "operator": ">",
                "duration_seconds": 300,
                "severity": AlertSeverity.WARNING,
                "enabled": True
            },
            {
                "rule_id": "disk_space_low",
                "name": "Low Disk Space",
                "description": "Disk usage exceeds 90%",
                "metric_type": MetricType.DISK,
                "threshold": 90.0,
                "operator": ">",
                "duration_seconds": 600,
                "severity": AlertSeverity.ERROR,
                "enabled": True
            },
            {
                "rule_id": "response_time_high",
                "name": "High Response Time",
                "description": "Response time exceeds 2000ms",
                "metric_type": MetricType.RESPONSE_TIME,
                "threshold": 2000.0,
                "operator": ">",
                "duration_seconds": 180,
                "severity": AlertSeverity.WARNING,
                "enabled": True
            },
            {
                "rule_id": "error_rate_high",
                "name": "High Error Rate",
                "description": "Error rate exceeds 5%",
                "metric_type": MetricType.ERROR_RATE,
                "threshold": 5.0,
                "operator": ">",
                "duration_seconds": 120,
                "severity": AlertSeverity.ERROR,
                "enabled": True
            }
        ]
        
        for rule_data in rules:
            self.alert_rules[rule_data["rule_id"]] = rule_data
        
        self.logger.info(f"Initialized {len(rules)} alert rules")
    
    def _initialize_notification_channels(self):
        """Initialize with sample notification channels"""
        channels = [
            {
                "channel_id": "email_alerts",
                "name": "Email Alerts",
                "type": "email",
                "config": {
                    "smtp_server": "smtp.stellarlogica.ai",
                    "smtp_port": 587,
                    "username": "alerts@stellarlogica.ai",
                    "password_encrypted": "encrypted_password",
                    "recipients": ["admin@stellarlogica.ai", "ops@stellarlogica.ai"],
                    "use_tls": True
                },
                "enabled": True,
                "last_sent": None
            },
            {
                "channel_id": "slack_alerts",
                "name": "Slack Alerts",
                "type": "slack",
                "config": {
                    "webhook_url": "https://hooks.slack.com/services/...",
                    "channel": "#alerts",
                    "username": "StellarLogic Monitor",
                    "icon_emoji": ":warning:"
                },
                "enabled": True,
                "last_sent": None
            },
            {
                "channel_id": "pagerduty_alerts",
                "name": "PagerDuty Alerts",
                "type": "pagerduty",
                "config": {
                    "integration_key": "encrypted_integration_key",
                    "service_key": "encrypted_service_key",
                    "escalation_policy": "default"
                },
                "enabled": True,
                "last_sent": None
            }
        ]
        
        for channel_data in channels:
            channel = NotificationChannel(**channel_data)
            self.notification_channels[channel.channel_id] = channel
        
        self.logger.info(f"Initialized {len(channels)} notification channels")
    
    def _initialize_health_checks(self):
        """Initialize with sample health checks"""
        checks = [
            {
                "check_id": "api_health",
                "name": "API Health Check",
                "service_name": "API Service",
                "endpoint": "https://api.stellarlogica.ai/health",
                "status": "healthy",
                "response_time_ms": 145.2,
                "last_checked": datetime.now() - timedelta(minutes=2),
                "consecutive_failures": 0,
                "max_failures": 3,
                "timeout_seconds": 30
            },
            {
                "check_id": "database_health",
                "name": "Database Health Check",
                "service_name": "Database Service",
                "endpoint": "postgresql://db.stellarlogica.ai:5432/stellarlogic",
                "status": "healthy",
                "response_time_ms": 23.5,
                "last_checked": datetime.now() - timedelta(minutes=1),
                "consecutive_failures": 0,
                "max_failures": 3,
                "timeout_seconds": 10
            },
            {
                "check_id": "redis_health",
                "name": "Redis Health Check",
                "service_name": "Cache Service",
                "endpoint": "redis://redis.stellarlogica.ai:6379",
                "status": "healthy",
                "response_time_ms": 8.7,
                "last_checked": datetime.now() - timedelta(minutes=1),
                "consecutive_failures": 0,
                "max_failures": 3,
                "timeout_seconds": 5
            },
            {
                "check_id": "web_app_health",
                "name": "Web App Health Check",
                "service_name": "Web Application",
                "endpoint": "https://stellarlogica.ai/health",
                "status": "degraded",
                "response_time_ms": 2850.3,
                "last_checked": datetime.now() - timedelta(minutes=3),
                "consecutive_failures": 1,
                "max_failures": 3,
                "timeout_seconds": 30
            }
        ]
        
        for check_data in checks:
            check = HealthCheck(**check_data)
            self.health_checks[check.check_id] = check
        
        self.logger.info(f"Initialized {len(checks)} health checks")
    
    def _initialize_sample_metrics(self):
        """Initialize with sample metrics"""
        import random
        
        services = ["API Service", "Database Service", "Cache Service", "Web Application"]
        hosts = ["server-01", "server-02", "server-03", "server-04"]
        
        for i in range(100):
            metric = Metric(
                metric_id=f"metric_{i}",
                name=f"Sample Metric {i}",
                type=random.choice(list(MetricType)),
                value=random.uniform(10, 100),
                unit="%",
                timestamp=datetime.now() - timedelta(minutes=random.randint(0, 60)),
                service_name=random.choice(services),
                host_name=random.choice(hosts),
                tags={"environment": "production", "region": "us-east-1"}
            )
            self.metrics.append(metric)
        
        self.logger.info(f"Initialized {len(self.metrics)} sample metrics")
    
    def start_monitoring(self):
        """Start monitoring system"""
        if self.monitoring_active:
            return {"success": False, "error": "Monitoring already active"}
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        return {"success": True, "message": "Monitoring started"}
    
    def stop_monitoring(self):
        """Stop monitoring system"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        return {"success": True, "message": "Monitoring stopped"}
    
    def add_metric(self, metric_type: str, value: float, service_name: str, 
                   host_name: str, tags: Dict[str, str] = None) -> Dict[str, Any]:
        """Add new metric"""
        try:
            mt = MetricType(metric_type)
            
            metric = Metric(
                metric_id=f"metric_{int(time.time())}",
                name=f"{metric_type.value.title()} Usage",
                type=mt,
                value=value,
                unit="%",
                timestamp=datetime.now(),
                service_name=service_name,
                host_name=host_name,
                tags=tags or {}
            )
            
            self.metrics.append(metric)
            
            # Check alert rules
            self._check_alert_rules(metric)
            
            return {"success": True, "metric_id": metric.metric_id}
            
        except Exception as e:
            self.logger.error(f"Add metric error: {e}")
            return {"success": False, "error": "Failed to add metric"}
    
    def run_health_check(self, check_id: str) -> Dict[str, Any]:
        """Run health check"""
        try:
            check = self.health_checks.get(check_id)
            if not check:
                return {"success": False, "error": "Health check not found"}
            
            # Simulate health check execution
            import random
            response_time = random.uniform(10, 500)
            
            # Random failure (5% chance)
            if random.random() < 0.05:
                check.status = "unhealthy"
                check.response_time_ms = response_time
                check.consecutive_failures += 1
            else:
                check.status = "healthy" if response_time < 1000 else "degraded"
                check.response_time_ms = response_time
                check.consecutive_failures = 0
            
            check.last_checked = datetime.now()
            
            # Create alert if threshold exceeded
            if check.consecutive_failures >= check.max_failures:
                self._create_health_alert(check)
            
            return {
                "success": True,
                "check_id": check_id,
                "status": check.status,
                "response_time_ms": check.response_time_ms,
                "consecutive_failures": check.consecutive_failures
            }
            
        except Exception as e:
            self.logger.error(f"Run health check error: {e}")
            return {"success": False, "error": "Failed to run health check"}
    
    def get_alerts(self, severity: str = None, status: str = None, 
                   hours: int = 24) -> Dict[str, Any]:
        """Get alerts"""
        try:
            alerts = list(self.alerts.values())
            
            if severity:
                alerts = [a for a in alerts if a.severity.value == severity]
            
            if status:
                alerts = [a for a in alerts if a.status.value == status]
            
            # Filter by time
            cutoff_time = datetime.now() - timedelta(hours=hours)
            alerts = [a for a in alerts if a.triggered_at >= cutoff_time]
            
            # Sort by triggered_at (newest first)
            alerts.sort(key=lambda x: x.triggered_at, reverse=True)
            
            return {
                "total_alerts": len(alerts),
                "severity_filter": severity,
                "status_filter": status,
                "time_hours": hours,
                "alerts": [asdict(alert) for alert in alerts]
            }
            
        except Exception as e:
            self.logger.error(f"Get alerts error: {e}")
            return {"error": "Failed to get alerts"}
    
    def get_metrics(self, metric_type: str = None, service_name: str = None, 
                   hours: int = 1) -> Dict[str, Any]:
        """Get metrics"""
        try:
            metrics = list(self.metrics)
            
            if metric_type:
                mt = MetricType(metric_type)
                metrics = [m for m in metrics if m.type == mt]
            
            if service_name:
                metrics = [m for m in metrics if m.service_name == service_name]
            
            # Filter by time
            cutoff_time = datetime.now() - timedelta(hours=hours)
            metrics = [m for m in metrics if m.timestamp >= cutoff_time]
            
            # Sort by timestamp (newest first)
            metrics.sort(key=lambda x: x.timestamp, reverse=True)
            
            return {
                "total_metrics": len(metrics),
                "metric_type_filter": metric_type,
                "service_filter": service_name,
                "time_hours": hours,
                "metrics": [asdict(metric) for metric in metrics]
            }
            
        except Exception as e:
            self.logger.error(f"Get metrics error: {e}")
            return {"error": "Failed to get metrics"}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        try:
            checks = list(self.health_checks.values())
            
            total_checks = len(checks)
            healthy_checks = len([c for c in checks if c.status == "healthy"])
            degraded_checks = len([c for c in checks if c.status == "degraded"])
            unhealthy_checks = len([c for c in checks if c.status == "unhealthy"])
            
            overall_health = (healthy_checks / total_checks * 100) if total_checks > 0 else 0
            
            return {
                "total_checks": total_checks,
                "healthy_checks": healthy_checks,
                "degraded_checks": degraded_checks,
                "unhealthy_checks": unhealthy_checks,
                "overall_health_percentage": round(overall_health, 2),
                "health_checks": [asdict(check) for check in checks],
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Get health status error: {e}")
            return {"error": "Failed to get health status"}
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> Dict[str, Any]:
        """Acknowledge alert"""
        try:
            alert = self.alerts.get(alert_id)
            if not alert:
                return {"success": False, "error": "Alert not found"}
            
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = acknowledged_by
            
            return {
                "success": True,
                "alert_id": alert_id,
                "status": "acknowledged",
                "acknowledged_by": acknowledged_by
            }
            
        except Exception as e:
            self.logger.error(f"Acknowledge alert error: {e}")
            return {"success": False, "error": "Failed to acknowledge alert"}
    
    def resolve_alert(self, alert_id: str, resolved_by: str) -> Dict[str, Any]:
        """Resolve alert"""
        try:
            alert = self.alerts.get(alert_id)
            if not alert:
                return {"success": False, "error": "Alert not found"}
            
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            alert.resolved_by = resolved_by
            
            return {
                "success": True,
                "alert_id": alert_id,
                "status": "resolved",
                "resolved_by": resolved_by
            }
            
        except Exception as e:
            self.logger.error(f"Resolve alert error: {e}")
            return {"success": False, "error": "Failed to resolve alert"}
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Run health checks
                for check_id in self.health_checks:
                    self.run_health_check(check_id)
                
                # Generate sample metrics
                self._generate_sample_metrics()
                
                # Sleep for 30 seconds
                time.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(30)
    
    def _check_alert_rules(self, metric: Metric):
        """Check if metric triggers any alert rules"""
        for rule in self.alert_rules.values():
            if not rule["enabled"]:
                continue
            
            if rule["metric_type"] != metric.type:
                continue
            
            # Check threshold
            if rule["operator"] == ">" and metric.value > rule["threshold"]:
                self._create_metric_alert(metric, rule)
            elif rule["operator"] == "<" and metric.value < rule["threshold"]:
                self._create_metric_alert(metric, rule)
    
    def _create_metric_alert(self, metric: Metric, rule: Dict[str, Any]):
        """Create alert from metric"""
        alert_id = f"alert_{int(time.time())}"
        
        alert = Alert(
            alert_id=alert_id,
            name=rule["name"],
            description=rule["description"],
            severity=rule["severity"],
            status=AlertStatus.ACTIVE,
            metric_type=metric.type,
            current_value=metric.value,
            threshold_value=rule["threshold"],
            triggered_at=datetime.now(),
            acknowledged_at=None,
            resolved_at=None,
            acknowledged_by=None,
            resolved_by=None,
            affected_services=[metric.service_name],
            notification_sent=False
        )
        
        self.alerts[alert_id] = alert
        
        # Send notifications
        self._send_notifications(alert)
    
    def _create_health_alert(self, check: HealthCheck):
        """Create alert from health check"""
        alert_id = f"alert_{int(time.time())}"
        
        alert = Alert(
            alert_id=alert_id,
            name=f"Health Check Failed: {check.name}",
            description=f"Service {check.service_name} has failed {check.consecutive_failures} consecutive health checks",
            severity=AlertSeverity.ERROR,
            status=AlertStatus.ACTIVE,
            metric_type=MetricType.RESPONSE_TIME,
            current_value=check.response_time_ms,
            threshold_value=1000.0,
            triggered_at=datetime.now(),
            acknowledged_at=None,
            resolved_at=None,
            acknowledged_by=None,
            resolved_by=None,
            affected_services=[check.service_name],
            notification_sent=False
        )
        
        self.alerts[alert_id] = alert
        
        # Send notifications
        self._send_notifications(alert)
    
    def _send_notifications(self, alert: Alert):
        """Send notifications for alert"""
        for channel in self.notification_channels.values():
            if not channel.enabled:
                continue
            
            # Simulate notification sending
            channel.last_sent = datetime.now()
            alert.notification_sent = True
        
        self.logger.info(f"Sent notifications for alert {alert.alert_id}")
    
    def _generate_sample_metrics(self):
        """Generate sample metrics for monitoring"""
        import random
        
        services = ["API Service", "Database Service", "Cache Service", "Web Application"]
        hosts = ["server-01", "server-02", "server-03", "server-04"]
        
        for _ in range(5):
            metric = Metric(
                metric_id=f"metric_{int(time.time())}_{random.randint(1, 1000)}",
                name=random.choice(["CPU Usage", "Memory Usage", "Disk Usage", "Response Time"]),
                type=random.choice(list(MetricType)),
                value=random.uniform(10, 100),
                unit="%",
                timestamp=datetime.now(),
                service_name=random.choice(services),
                host_name=random.choice(hosts),
                tags={"environment": "production", "region": "us-east-1"}
            )
            self.metrics.append(metric)

# Global monitoring & alerting system instance
monitoring_alerting_system = MonitoringAlertingSystem()
