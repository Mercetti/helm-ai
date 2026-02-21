#!/usr/bin/env python3
"""
Unified Alert System
Threshold-based alerting for performance, security, and system health issues
"""

import os
import sys
import time
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertCategory(Enum):
    """Alert categories"""
    PERFORMANCE = "performance"
    SECURITY = "security"
    SYSTEM_HEALTH = "system_health"
    DATABASE = "database"
    RESOURCE_USAGE = "resource_usage"
    USER_ENGAGEMENT = "user_engagement"
    FINANCIAL = "financial"

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    timestamp: datetime
    category: AlertCategory
    severity: AlertSeverity
    title: str
    message: str
    source: str
    metric_name: str
    current_value: float
    threshold_value: float
    threshold_type: str  # above, below, equal
    acknowledged: bool = False
    resolved: bool = False
    assigned_to: str = None
    resolution: str = None
    metadata: Dict[str, Any] = None

@dataclass
class AlertRule:
    """Alert rule configuration"""
    id: str
    category: AlertCategory
    metric_name: str
    threshold_type: str  # above, below, equal
    threshold_value: float
    severity: AlertSeverity
    enabled: bool
    cooldown_minutes: int
    description: str
    action_required: str
    notification_channels: List[str]

class UnifiedAlertSystem:
    """Unified Alert System for all monitoring components"""
    
    def __init__(self):
        self.logger = logging.getLogger("unified_alert_system")
        self.alerts = deque(maxlen=1000)  # Last 1000 alerts
        self.alert_rules = {}
        self.active_alerts = {}  # alert_id -> Alert
        self.notification_handlers = {}
        self.alert_statistics = {
            "total_alerts": 0,
            "active_alerts": 0,
            "resolved_alerts": 0,
            "acknowledged_alerts": 0,
            "alerts_by_category": defaultdict(int),
            "alerts_by_severity": defaultdict(int),
            "alerts_by_hour": defaultdict(int),
            "average_resolution_time_minutes": 0,
            "last_alert": None
        }
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_interval = 60  # seconds
        
        # Initialize default alert rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        default_rules = [
            # Performance alerts
            AlertRule(
                id="cpu_high",
                category=AlertCategory.PERFORMANCE,
                metric_name="cpu_usage",
                threshold_type="above",
                threshold_value=80.0,
                severity=AlertSeverity.WARNING,
                enabled=True,
                cooldown_minutes=15,
                description="High CPU usage detected",
                action_required="Investigate CPU-intensive processes",
                notification_channels=["email", "dashboard"]
            ),
            AlertRule(
                id="cpu_critical",
                category=AlertCategory.PERFORMANCE,
                metric_name="cpu_usage",
                threshold_type="above",
                threshold_value=95.0,
                severity=AlertSeverity.CRITICAL,
                enabled=True,
                cooldown_minutes=5,
                description="Critical CPU usage detected",
                action_required="Immediate CPU optimization required",
                notification_channels=["email", "sms", "dashboard"]
            ),
            AlertRule(
                id="memory_high",
                category=AlertCategory.PERFORMANCE,
                metric_name="memory_usage",
                threshold_type="above",
                threshold_value=85.0,
                severity=AlertSeverity.WARNING,
                enabled=True,
                cooldown_minutes=15,
                description="High memory usage detected",
                action_required="Investigate memory-intensive processes",
                notification_channels=["email", "dashboard"]
            ),
            AlertRule(
                id="memory_critical",
                category=AlertCategory.PERFORMANCE,
                metric_name="memory_usage",
                threshold_type="above",
                threshold_value=95.0,
                severity=AlertSeverity.CRITICAL,
                enabled=True,
                cooldown_minutes=5,
                description="Critical memory usage detected",
                action_required="Immediate memory optimization required",
                notification_channels=["email", "sms", "dashboard"]
            ),
            
            # System health alerts
            AlertRule(
                id="disk_high",
                category=AlertCategory.SYSTEM_HEALTH,
                metric_name="disk_usage",
                threshold_type="above",
                threshold_value=85.0,
                severity=AlertSeverity.WARNING,
                enabled=True,
                cooldown_minutes=30,
                description="High disk usage detected",
                action_required="Disk cleanup or expansion required",
                notification_channels=["email", "dashboard"]
            ),
            AlertRule(
                id="disk_critical",
                category=AlertCategory.SYSTEM_HEALTH,
                metric_name="disk_usage",
                threshold_type="above",
                threshold_value=95.0,
                severity=AlertSeverity.CRITICAL,
                enabled=True,
                cooldown_minutes=15,
                description="Critical disk usage detected",
                action_required="Immediate disk cleanup required",
                notification_channels=["email", "sms", "dashboard"]
            ),
            
            # Database alerts
            AlertRule(
                id="slow_queries",
                category=AlertCategory.DATABASE,
                metric_name="slow_query_rate",
                threshold_type="above",
                threshold_value=0.10,  # 10%
                severity=AlertSeverity.WARNING,
                enabled=True,
                cooldown_minutes=30,
                description="High slow query rate detected",
                action_required="Query optimization required",
                notification_channels=["email", "dashboard"]
            ),
            AlertRule(
                id="db_errors",
                category=AlertCategory.DATABASE,
                metric_name="error_rate",
                threshold_type="above",
                threshold_value=0.05,  # 5%
                severity=AlertSeverity.CRITICAL,
                enabled=True,
                cooldown_minutes=10,
                description="High database error rate detected",
                action_required="Database investigation required",
                notification_channels=["email", "sms", "dashboard"]
            ),
            
            # User engagement alerts
            AlertRule(
                id="high_bounce_rate",
                category=AlertCategory.USER_ENGAGEMENT,
                metric_name="bounce_rate",
                threshold_type="above",
                threshold_value=0.50,  # 50%
                severity=AlertSeverity.WARNING,
                enabled=True,
                cooldown_minutes=60,
                description="High bounce rate detected",
                action_required="User experience optimization required",
                notification_channels=["email", "dashboard"]
            ),
            
            # Financial alerts
            AlertRule(
                id="low_mrr",
                category=AlertCategory.FINANCIAL,
                metric_name="mrr",
                threshold_type="below",
                threshold_value=10000.0,  # $10,000
                severity=AlertSeverity.WARNING,
                enabled=True,
                cooldown_minutes=120,
                description="Low MRR detected",
                action_required="Revenue optimization required",
                notification_channels=["email", "dashboard"]
            ),
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.id] = rule
    
    def start_monitoring(self):
        """Start alert system monitoring"""
        if self.monitoring_active:
            self.logger.warning("Alert system monitoring is already running")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Unified alert system started")
    
    def stop_monitoring(self):
        """Stop alert system monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        self.logger.info("Unified alert system stopped")
    
    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule"""
        self.alert_rules[rule.id] = rule
        self.logger.info(f"Added alert rule: {rule.id} - {rule.description}")
    
    def remove_alert_rule(self, rule_id: str):
        """Remove an alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            self.logger.info(f"Removed alert rule: {rule_id}")
    
    def register_notification_handler(self, channel: str, handler: Callable[[Alert], None]):
        """Register a notification handler for a channel"""
        self.notification_handlers[channel] = handler
        self.logger.info(f"Registered notification handler for channel: {channel}")
    
    def check_metric_thresholds(self, category: AlertCategory, metric_name: str, current_value: float):
        """Check if a metric triggers any alert rules"""
        triggered_alerts = []
        
        for rule in self.alert_rules.values():
            if (rule.enabled and 
                rule.category == category and 
                rule.metric_name == metric_name and
                self._check_threshold(rule, current_value)):
                
                # Check cooldown
                if self._is_in_cooldown(rule):
                    continue
                
                # Create alert
                alert = Alert(
                    id=f"{rule.id}_{int(time.time())}",
                    timestamp=datetime.now(),
                    category=rule.category,
                    severity=rule.severity,
                    title=rule.description,
                    message=f"{metric_name} is {rule.threshold_type} threshold: {current_value:.2f} {rule.threshold_value:.2f}",
                    source="unified_alert_system",
                    metric_name=metric_name,
                    current_value=current_value,
                    threshold_value=rule.threshold_value,
                    threshold_type=rule.threshold_type,
                    metadata={
                        "rule_id": rule.id,
                        "action_required": rule.action_required,
                        "notification_channels": rule.notification_channels
                    }
                )
                
                triggered_alerts.append(alert)
                self.active_alerts[alert.id] = alert
                self.alerts.append(alert)
                
                # Update statistics
                self.alert_statistics["total_alerts"] += 1
                self.alert_statistics["active_alerts"] += 1
                self.alert_statistics["alerts_by_category"][rule.category.value] += 1
                self.alert_statistics["alerts_by_severity"][rule.severity.value] += 1
                self.alert_statistics["last_alert"] = alert
                
                # Send notifications
                self._send_notifications(alert)
                
                self.logger.warning(f"Alert triggered: {alert.title}")
        
        return triggered_alerts
    
    def _check_threshold(self, rule: AlertRule, current_value: float) -> bool:
        """Check if a value triggers the threshold rule"""
        if rule.threshold_type == "above":
            return current_value > rule.threshold_value
        elif rule.threshold_type == "below":
            return current_value < rule.threshold_value
        elif rule.threshold_type == "equal":
            return abs(current_value - rule.threshold_value) < 0.01
        else:
            return False
    
    def _is_in_cooldown(self, rule: AlertRule) -> bool:
        """Check if a rule is in cooldown period"""
        if not rule.id in self.active_alerts:
            return False
        
        alert = self.active_alerts[rule.id]
        cooldown_end = alert.timestamp + timedelta(minutes=rule.cooldown_minutes)
        return datetime.now() < cooldown_end
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = None):
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            self.active_alerts[alert_id].metadata["acknowledged_by"] = acknowledged_by
            self.active_alerts[alert_id].metadata["acknowledged_at"] = datetime.now().isoformat()
            
            self.alert_statistics["acknowledged_alerts"] += 1
            self.logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
            return True
        return False
    
    def resolve_alert(self, alert_id: str, resolution: str, resolved_by: str = None):
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolution = resolution
            alert.metadata["resolved_by"] = resolved_by
            alert.metadata["resolved_at"] = datetime.now().isoformat()
            
            # Move from active to resolved
            del self.active_alerts[alert_id]
            self.alert_statistics["active_alerts"] -= 1
            self.alert_statistics["resolved_alerts"] += 1
            
            # Calculate resolution time
            if alert.timestamp:
                resolution_time = (datetime.now() - alert.timestamp).total_seconds() / 60
                if self.alert_statistics["average_resolution_time_minutes"] == 0:
                    self.alert_statistics["average_resolution_time_minutes"] = resolution_time
                else:
                    self.alert_statistics["average_resolution_time_minutes"] = (
                        (self.alert_statistics["average_resolution_time_minutes"] + resolution_time) / 2
                    )
            
            self.logger.info(f"Alert resolved: {alert_id} - {resolution}")
            return True
        return False
    
    def get_active_alerts(self, category: AlertCategory = None, severity: AlertSeverity = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get active alerts with optional filtering"""
        alerts = list(self.active_alerts.values())
        
        if category:
            alerts = [a for a in alerts if a.category == category]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [asdict(a) for a in alerts[:limit]]
    
    def get_alert_history(self, hours: int = 24, category: AlertCategory = None, severity: AlertSeverity = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get alert history with optional filtering"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        alerts = [a for a in self.alerts if a.timestamp > cutoff_time]
        
        if category:
            alerts = [a for a in alerts if a.category == category]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [asdict(a) for a in alerts[:limit]]
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert system statistics"""
        return {
            "statistics": self.alert_statistics,
            "alert_rules": {rule_id: asdict(rule) for rule_id, rule in self.alert_rules.items()},
            "active_alerts_count": len(self.active_alerts),
            "total_alerts_in_history": len(self.alerts),
            "timestamp": datetime.now().isoformat()
        }
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Check for any expired alerts and clean up
                self._cleanup_expired_alerts()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in alert monitoring loop: {e}")
                time.sleep(5)
    
    def _cleanup_expired_alerts(self):
        """Clean up expired alerts"""
        current_time = datetime.now()
        expired_alerts = []
        
        for alert_id, alert in list(self.active_alerts.items()):
            # Auto-resolve alerts older than 24 hours
            if (current_time - alert.timestamp).total_seconds() > 24 * 3600:
                alert.resolved = True
                alert.resolution = "Auto-resolved (expired)"
                alert.metadata["resolved_at"] = current_time.isoformat()
                alert.metadata["auto_resolved"] = True
                
                expired_alerts.append(alert_id)
                del self.active_alerts[alert_id]
                
                self.alert_statistics["active_alerts"] -= 1
                self.alert_statistics["resolved_alerts"] += 1
                
                self.logger.info(f"Auto-resolved expired alert: {alert_id}")
        
        if expired_alerts:
            self.logger.info(f"Cleaned up {len(expired_alerts)} expired alerts")
    
    def _send_notifications(self, alert: Alert):
        """Send notifications for an alert"""
        for channel in alert.metadata["notification_channels"]:
            if channel in self.notification_handlers:
                try:
                    self.notification_handlers[channel](alert)
                except Exception as e:
                    self.logger.error(f"Error sending notification to {channel}: {e}")

# Global unified alert system instance
unified_alert_system = UnifiedAlertSystem()
