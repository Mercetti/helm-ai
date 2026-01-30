"""
Helm AI Security Monitoring and Alerting
Provides real-time security monitoring, threat detection, and alerting
"""

import os
import sys
import json
import time
import threading
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from database.database_manager import get_database_manager
from security.security_hardening import security_auditor, vulnerability_scanner

@dataclass
class SecurityAlert:
    """Security alert record"""
    alert_id: str
    timestamp: datetime
    severity: str  # low, medium, high, critical
    category: str
    title: str
    description: str
    source: str
    affected_resources: List[str]
    indicators: Dict[str, Any]
    status: str = "open"  # open, acknowledged, investigating, resolved
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'alert_id': self.alert_id,
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'affected_resources': self.affected_resources,
            'indicators': self.indicators,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution_notes': self.resolution_notes
        }

@dataclass
class SecurityRule:
    """Security monitoring rule"""
    rule_id: str
    name: str
    description: str
    severity: str
    category: str
    enabled: bool = True
    threshold: Optional[float] = None
    time_window: Optional[int] = None  # minutes
    conditions: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'description': self.description,
            'severity': self.severity,
            'category': self.category,
            'enabled': self.enabled,
            'threshold': self.threshold,
            'time_window': self.time_window,
            'conditions': self.conditions,
            'actions': self.actions
        }

class SecurityMonitor:
    """Real-time security monitoring and threat detection"""
    
    def __init__(self):
        self.alerts = deque(maxlen=1000)
        self.rules = self._setup_default_rules()
        self.monitoring_active = False
        self.monitor_thread = None
        self.alert_handlers = []
        self.lock = threading.RLock()
        
    def _setup_default_rules(self) -> Dict[str, SecurityRule]:
        """Setup default security monitoring rules"""
        return {
            'failed_login_attempts': SecurityRule(
                rule_id='failed_login_attempts',
                name='Failed Login Attempts',
                description='Detect multiple failed login attempts',
                severity='medium',
                category='authentication',
                threshold=5,
                time_window=15,
                conditions=['failed_login_count > threshold'],
                actions=['alert', 'lock_account']
            ),
            'suspicious_api_usage': SecurityRule(
                rule_id='suspicious_api_usage',
                name='Suspicious API Usage',
                description='Detect unusual API usage patterns',
                severity='high',
                category='api_security',
                threshold=1000,
                time_window=60,
                conditions=['api_requests_per_minute > threshold'],
                actions=['alert', 'rate_limit']
            ),
            'privilege_escalation': SecurityRule(
                rule_id='privilege_escalation',
                name='Privilege Escalation',
                description='Detect privilege escalation attempts',
                severity='critical',
                category='authorization',
                conditions=['role_change_detected'],
                actions=['alert', 'investigate']
            ),
            'data_exfiltration': SecurityRule(
                rule_id='data_exfiltration',
                name='Data Exfiltration',
                description='Detect potential data exfiltration',
                severity='critical',
                category='data_security',
                threshold=10000,
                time_window=60,
                conditions=['data_export_volume > threshold'],
                actions=['alert', 'block_access']
            ),
            'unusual_access_patterns': SecurityRule(
                rule_id='unusual_access_patterns',
                name='Unusual Access Patterns',
                description='Detect unusual access patterns',
                severity='medium',
                category='behavioral',
                conditions=['access_pattern_anomaly'],
                actions=['alert', 'require_mfa']
            ),
            'security_event_spike': SecurityRule(
                rule_id='security_event_spike',
                name='Security Event Spike',
                description='Detect spike in security events',
                severity='high',
                category='monitoring',
                threshold=50,
                time_window=5,
                conditions=['security_events_per_minute > threshold'],
                actions=['alert', 'investigate']
            )
        }
    
    def start_monitoring(self):
        """Start security monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Security monitoring started")
    
    def stop_monitoring(self):
        """Stop security monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Security monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                self._check_security_rules()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Security monitoring error: {e}")
                time.sleep(60)
    
    def _check_security_rules(self):
        """Check all security rules"""
        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            try:
                if self._evaluate_rule(rule):
                    self._create_alert(rule)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule_id}: {e}")
    
    def _evaluate_rule(self, rule: SecurityRule) -> bool:
        """Evaluate a security rule"""
        if rule.rule_id == 'failed_login_attempts':
            return self._check_failed_login_attempts(rule)
        elif rule.rule_id == 'suspicious_api_usage':
            return self._check_suspicious_api_usage(rule)
        elif rule.rule_id == 'privilege_escalation':
            return self._check_privilege_escalation(rule)
        elif rule.rule_id == 'data_exfiltration':
            return self._check_data_exfiltration(rule)
        elif rule.rule_id == 'unusual_access_patterns':
            return self._check_unusual_access_patterns(rule)
        elif rule.rule_id == 'security_event_spike':
            return self._check_security_event_spike(rule)
        
        return False
    
    def _check_failed_login_attempts(self, rule: SecurityRule) -> bool:
        """Check for failed login attempts"""
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Check failed login attempts in time window
                time_threshold = datetime.now() - timedelta(minutes=rule.time_window)
                
                result = session.execute(text("""
                    SELECT COUNT(*) FROM security_events
                    WHERE event_type = 'failed_login'
                    AND created_at > :time_threshold
                """), {'time_threshold': time_threshold})
                
                failed_attempts = result.scalar()
                
                return failed_attempts > rule.threshold
                
        except Exception as e:
            logger.error(f"Failed login check error: {e}")
            return False
    
    def _check_suspicious_api_usage(self, rule: SecurityRule) -> bool:
        """Check for suspicious API usage"""
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Check API requests per minute
                time_threshold = datetime.now() - timedelta(minutes=rule.time_window)
                
                result = session.execute(text("""
                    SELECT COUNT(*) FROM audit_logs
                    WHERE action LIKE '%api_%'
                    AND created_at > :time_threshold
                """), {'time_threshold': time_threshold})
                
                api_requests = result.scalar()
                
                return api_requests > rule.threshold
                
        except Exception as e:
            logger.error(f"API usage check error: {e}")
            return False
    
    def _check_privilege_escalation(self, rule: SecurityRule) -> bool:
        """Check for privilege escalation attempts"""
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Check for role changes
                time_threshold = datetime.now() - timedelta(minutes=rule.time_window or 60)
                
                result = session.execute(text("""
                    SELECT COUNT(*) FROM audit_logs
                    WHERE action = 'user_role_changed'
                    AND created_at > :time_threshold
                """), {'time_threshold': time_threshold})
                
                role_changes = result.scalar()
                
                return role_changes > 0
                
        except Exception as e:
            logger.error(f"Privilege escalation check error: {e}")
            return False
    
    def _check_data_exfiltration(self, rule: SecurityRule) -> bool:
        """Check for data exfiltration"""
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Check for large data exports
                time_threshold = datetime.now() - timedelta(minutes=rule.time_window)
                
                result = session.execute(text("""
                    SELECT COUNT(*) FROM audit_logs
                    WHERE action = 'data_exported'
                    AND created_at > :time_threshold
                """), {'time_threshold': time_threshold})
                
                data_exports = result.scalar()
                
                return data_exports > rule.threshold
                
        except Exception as e:
            logger.error(f"Data exfiltration check error: {e}")
            return False
    
    def _check_unusual_access_patterns(self, rule: SecurityRule) -> bool:
        """Check for unusual access patterns"""
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Check for access from unusual locations or times
                time_threshold = datetime.now() - timedelta(minutes=rule.time_window or 60)
                
                result = session.execute(text("""
                    SELECT COUNT(DISTINCT ip_address) FROM audit_logs
                    WHERE created_at > :time_threshold
                """), {'time_threshold': time_threshold})
                
                unique_ips = result.scalar()
                
                # If more than 50 unique IPs in short time, flag as unusual
                return unique_ips > 50
                
        except Exception as e:
            logger.error(f"Access pattern check error: {e}")
            return False
    
    def _check_security_event_spike(self, rule: SecurityRule) -> bool:
        """Check for security event spike"""
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Check security events in time window
                time_threshold = datetime.now() - timedelta(minutes=rule.time_window)
                
                result = session.execute(text("""
                    SELECT COUNT(*) FROM security_events
                    WHERE created_at > :time_threshold
                """), {'time_threshold': time_threshold})
                
                security_events = result.scalar()
                
                return security_events > rule.threshold
                
        except Exception as e:
            logger.error(f"Security event spike check error: {e}")
            return False
    
    def _create_alert(self, rule: SecurityRule):
        """Create security alert"""
        alert = SecurityAlert(
            alert_id=secrets.token_hex(8),
            timestamp=datetime.now(),
            severity=rule.severity,
            category=rule.category,
            title=rule.name,
            description=rule.description,
            source='security_monitor',
            affected_resources=[],
            indicators={'rule_id': rule.rule_id, 'threshold': rule.threshold}
        )
        
        with self.lock:
            self.alerts.append(alert)
        
        # Trigger alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
        
        logger.warning(f"Security alert created: {alert.title}")
    
    def add_alert_handler(self, handler: Callable[[SecurityAlert], None]):
        """Add alert handler"""
        self.alert_handlers.append(handler)
    
    def get_alerts(self, severity: Optional[str] = None, hours: int = 24) -> List[SecurityAlert]:
        """Get security alerts"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            alerts = [a for a in self.alerts if a.timestamp >= cutoff_time]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return alerts
    
    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get alert summary"""
        alerts = self.get_alerts(hours=hours)
        
        if not alerts:
            return {
                'period_hours': hours,
                'total_alerts': 0,
                'by_severity': {},
                'by_category': {},
                'by_status': {}
            }
        
        # Group by severity
        by_severity = defaultdict(int)
        for alert in alerts:
            by_severity[alert.severity] += 1
        
        # Group by category
        by_category = defaultdict(int)
        for alert in alerts:
            by_category[alert.category] += 1
        
        # Group by status
        by_status = defaultdict(int)
        for alert in alerts:
            by_status[alert.status] += 1
        
        return {
            'period_hours': hours,
            'total_alerts': len(alerts),
            'by_severity': dict(by_severity),
            'by_category': dict(by_category),
            'by_status': dict(by_status),
            'critical_count': len([a for a in alerts if a.severity == 'critical']),
            'high_count': len([a for a in alerts if a.severity == 'high']),
            'resolution_rate': (len([a for a in alerts if a.status == 'resolved']) / len(alerts)) * 100
        }

class AlertNotifier:
    """Security alert notification system"""
    
    def __init__(self):
        self.email_config = self._load_email_config()
        self.slack_config = self._load_slack_config()
        
    def _load_email_config(self) -> Dict[str, Any]:
        """Load email configuration"""
        return {
            'smtp_server': os.getenv('SMTP_SERVER', 'localhost'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('SMTP_USERNAME', ''),
            'password': os.getenv('SMTP_PASSWORD', ''),
            'from_email': os.getenv('ALERT_FROM_EMAIL', 'security@helm-ai.com'),
            'to_emails': os.getenv('ALERT_TO_EMAILS', 'admin@helm-ai.com').split(',')
        }
    
    def _load_slack_config(self) -> Dict[str, Any]:
        """Load Slack configuration"""
        return {
            'webhook_url': os.getenv('SLACK_WEBHOOK_URL', ''),
            'channel': os.getenv('SLACK_CHANNEL', '#security-alerts')
        }
    
    def send_email_alert(self, alert: SecurityAlert):
        """Send email alert"""
        try:
            if not self.email_config['username'] or not self.email_config['password']:
                logger.warning("Email configuration not complete, skipping email alert")
                return
            
            subject = f"[HELM AI SECURITY] {alert.severity.upper()}: {alert.title}"
            
            body = f"""
Security Alert Details:

Alert ID: {alert.alert_id}
Timestamp: {alert.timestamp}
Severity: {alert.severity}
Category: {alert.category}
Title: {alert.title}
Description: {alert.description}
Source: {alert.source}

Affected Resources:
{chr(10).join(alert.affected_resources) if alert.affected_resources else 'None'}

Indicators:
{json.dumps(alert.indicators, indent=2)}

Status: {alert.status}
Assigned To: {alert.assigned_to or 'Unassigned'}

This is an automated security alert from Helm AI Security Monitoring System.
            """
            
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = ', '.join(self.email_config['to_emails'])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            
            for to_email in self.email_config['to_emails']:
                server.send_message(msg, to_addrs=[to_email])
            
            server.quit()
            
            logger.info(f"Email alert sent for {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def send_slack_alert(self, alert: SecurityAlert):
        """Send Slack alert"""
        try:
            if not self.slack_config['webhook_url']:
                logger.warning("Slack configuration not complete, skipping Slack alert")
                return
            
            import requests
            
            color = {
                'low': 'good',
                'medium': 'warning',
                'high': 'danger',
                'critical': 'danger'
            }.get(alert.severity, 'warning')
            
            payload = {
                'channel': self.slack_config['channel'],
                'username': 'Helm AI Security',
                'icon_emoji': ':lock:',
                'attachments': [{
                    'color': color,
                    'title': f"{alert.severity.upper()}: {alert.title}",
                    'text': alert.description,
                    'fields': [
                        {'title': 'Alert ID', 'value': alert.alert_id, 'short': True},
                        {'title': 'Category', 'value': alert.category, 'short': True},
                        {'title': 'Severity', 'value': alert.severity, 'short': True},
                        {'title': 'Status', 'value': alert.status, 'short': True},
                        {'title': 'Source', 'value': alert.source, 'short': True},
                        {'title': 'Timestamp', 'value': alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'short': True}
                    ],
                    'footer': 'Helm AI Security Monitoring',
                    'ts': int(alert.timestamp.timestamp())
                }]
            }
            
            response = requests.post(self.slack_config['webhook_url'], json=payload)
            response.raise_for_status()
            
            logger.info(f"Slack alert sent for {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    def handle_alert(self, alert: SecurityAlert):
        """Handle security alert"""
        # Send email for high and critical alerts
        if alert.severity in ['high', 'critical']:
            self.send_email_alert(alert)
        
        # Send Slack for all alerts
        self.send_slack_alert(alert)

class ThreatIntelligence:
    """Threat intelligence and analysis"""
    
    def __init__(self):
        self.threat_feeds = {}
        self.indicators = deque(maxlen=1000)
        
    def analyze_threats(self) -> Dict[str, Any]:
        """Analyze current threat landscape"""
        return {
            'timestamp': datetime.now().isoformat(),
            'threat_level': 'medium',
            'active_threats': [],
            'recommendations': [
                'Monitor for unusual login patterns',
                'Review API usage for anomalies',
                'Check for data exfiltration attempts'
            ]
        }

# Global security monitoring instances
security_monitor = SecurityMonitor()
alert_notifier = AlertNotifier()
threat_intelligence = ThreatIntelligence()

def start_security_monitoring():
    """Start security monitoring"""
    # Add alert notifier as handler
    security_monitor.add_alert_handler(alert_notifier.handle_alert)
    
    # Start monitoring
    security_monitor.start_monitoring()
    logger.info("Security monitoring system started")

def stop_security_monitoring():
    """Stop security monitoring"""
    security_monitor.stop_monitoring()
    logger.info("Security monitoring system stopped")

def get_security_status() -> Dict[str, Any]:
    """Get comprehensive security status"""
    return {
        'timestamp': datetime.now().isoformat(),
        'monitoring_active': security_monitor.monitoring_active,
        'alert_summary': security_monitor.get_alert_summary(),
        'security_rules': {k: v.to_dict() for k, v in security_monitor.rules.items()},
        'threat_intelligence': threat_intelligence.analyze_threats()
    }
