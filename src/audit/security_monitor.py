"""
Helm AI Security Monitor
This module provides security monitoring, threat detection, and incident response
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import re
import hashlib
import ipaddress
from collections import defaultdict, deque

from .audit_logger import AuditLogger, AuditEventType

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(Enum):
    """Security incident status"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"

class AlertType(Enum):
    """Security alert types"""
    BRUTE_FORCE = "brute_force"
    SUSPICIOUS_LOGIN = "suspicious_login"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    MALICIOUS_REQUEST = "malicious_request"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    PRIVILEGE_ESCALATION = "privilege_escalation"

@dataclass
class SecurityAlert:
    """Security alert data structure"""
    alert_id: str
    alert_type: AlertType
    threat_level: ThreatLevel
    title: str
    description: str
    source_ip: str
    user_id: str = None
    resource: str = None
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    indicators: List[str] = field(default_factory=list)
    confidence: float = 0.0  # 0.0-1.0
    status: str = "active"
    correlation_id: str = None

@dataclass
class SecurityIncident:
    """Security incident record"""
    incident_id: str
    title: str
    description: str
    severity: ThreatLevel
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    assigned_to: str = None
    alerts: List[str] = field(default_factory=list)  # Alert IDs
    affected_assets: List[str] = field(default_factory=list)
    containment_actions: List[str] = field(default_factory=list)
    remediation_steps: List[str] = field(default_factory=list)
    lessons_learned: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""
    indicator: str
    indicator_type: str  # ip, domain, hash, url
    threat_type: str
    confidence: float
    source: str
    first_seen: datetime
    last_seen: datetime
    description: str
    tags: List[str] = field(default_factory=list)

class SecurityMonitor:
    """Security monitoring and threat detection system"""
    
    def __init__(self):
        self.audit_logger = AuditLogger()
        
        # In-memory storage (would use database in production)
        self.alerts: Dict[str, SecurityAlert] = {}
        self.incidents: Dict[str, SecurityIncident] = {}
        self.threat_intel: Dict[str, ThreatIntelligence] = {}
        
        # Monitoring state
        self.failed_login_attempts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))
        self.suspicious_ips: Set[str] = set()
        self.blocked_ips: Set[str] = set()
        self.rate_limit_tracker: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Configuration
        self.max_failed_attempts = int(os.getenv('SECURITY_MAX_FAILED_ATTEMPTS', '5'))
        self.failed_attempt_window = int(os.getenv('SECURITY_FAILED_ATTEMPT_WINDOW', '300'))  # 5 minutes
        self.rate_limit_requests = int(os.getenv('SECURITY_RATE_LIMIT_REQUESTS', '100'))
        self.rate_limit_window = int(os.getenv('SECURITY_RATE_LIMIT_WINDOW', '60'))  # 1 minute
        
        # Load threat intelligence
        self._load_threat_intelligence()
        
        # Start monitoring thread
        self._start_background_monitoring()
    
    def _load_threat_intelligence(self):
        """Load threat intelligence data"""
        # Load known malicious IPs
        known_malicious_ips = [
            "192.168.1.100",  # Example malicious IP
            "10.0.0.50",      # Example malicious IP
        ]
        
        for ip in known_malicious_ips:
            intel = ThreatIntelligence(
                indicator=ip,
                indicator_type="ip",
                threat_type="malicious_ip",
                confidence=0.9,
                source="internal_threat_feed",
                first_seen=datetime.now() - timedelta(days=30),
                last_seen=datetime.now(),
                description="Known malicious IP address",
                tags=["malware", "botnet"]
            )
            self.threat_intel[ip] = intel
        
        # Load known malicious domains
        known_malicious_domains = [
            "malicious-example.com",
            "phishing-site.net"
        ]
        
        for domain in known_malicious_domains:
            intel = ThreatIntelligence(
                indicator=domain,
                indicator_type="domain",
                threat_type="malicious_domain",
                confidence=0.8,
                source="internal_threat_feed",
                first_seen=datetime.now() - timedelta(days=15),
                last_seen=datetime.now(),
                description="Known malicious domain",
                tags=["phishing", "malware"]
            )
            self.threat_intel[domain] = intel
    
    def _start_background_monitoring(self):
        """Start background monitoring thread"""
        import threading
        
        def monitor_loop():
            while True:
                try:
                    self._cleanup_old_data()
                    self._analyze_patterns()
                    threading.Event().wait(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Error in security monitoring loop: {e}")
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def check_login_attempt(self, 
                           user_id: str,
                           ip_address: str,
                           user_agent: str,
                           success: bool,
                           details: Dict[str, Any] = None) -> Optional[SecurityAlert]:
        """Check login attempt for security threats"""
        current_time = datetime.now()
        
        if not success:
            # Track failed attempts
            self.failed_login_attempts[user_id].append(current_time)
            
            # Check for brute force
            recent_failures = [
                attempt for attempt in self.failed_login_attempts[user_id]
                if (current_time - attempt).seconds <= self.failed_attempt_window
            ]
            
            if len(recent_failures) >= self.max_failed_attempts:
                alert = self._create_alert(
                    alert_type=AlertType.BRUTE_FORCE,
                    threat_level=ThreatLevel.HIGH,
                    title=f"Brute force attack detected for user {user_id}",
                    description=f"{len(recent_failures)} failed login attempts in {self.failed_attempt_window} seconds",
                    source_ip=ip_address,
                    user_id=user_id,
                    details={
                        "failed_attempts": len(recent_failures),
                        "time_window": self.failed_attempt_window,
                        "user_agent": user_agent
                    }
                )
                return alert
        
        # Check for suspicious login patterns
        if success:
            alert = self._check_suspicious_login(user_id, ip_address, user_agent)
            if alert:
                return alert
        
        return None
    
    def _check_suspicious_login(self, user_id: str, ip_address: str, user_agent: str) -> Optional[SecurityAlert]:
        """Check for suspicious login patterns"""
        # Check if IP is in threat intelligence
        if ip_address in self.threat_intel:
            intel = self.threat_intel[ip_address]
            if intel.confidence > 0.7:
                return self._create_alert(
                    alert_type=AlertType.SUSPICIOUS_LOGIN,
                    threat_level=ThreatLevel.HIGH,
                    title=f"Login from known malicious IP: {ip_address}",
                    description=f"User {user_id} logged in from IP address in threat intelligence",
                    source_ip=ip_address,
                    user_id=user_id,
                    details={
                        "threat_intel": intel.description,
                        "confidence": intel.confidence,
                        "user_agent": user_agent
                    }
                )
        
        # Check for impossible travel (geolocation would be needed here)
        # This is a placeholder for geolocation-based detection
        
        return None
    
    def check_api_request(self, 
                         user_id: str,
                         ip_address: str,
                         endpoint: str,
                         method: str,
                         user_agent: str,
                         status_code: int,
                         details: Dict[str, Any] = None) -> Optional[SecurityAlert]:
        """Check API request for security threats"""
        # Rate limiting check
        rate_key = f"{ip_address}:{endpoint}"
        current_time = datetime.now()
        
        self.rate_limit_tracker[rate_key].append(current_time)
        
        recent_requests = [
            req for req in self.rate_limit_tracker[rate_key]
            if (current_time - req).seconds <= self.rate_limit_window
        ]
        
        if len(recent_requests) >= self.rate_limit_requests:
            return self._create_alert(
                alert_type=AlertType.RATE_LIMIT_EXCEEDED,
                threat_level=ThreatLevel.MEDIUM,
                title=f"Rate limit exceeded for {endpoint}",
                description=f"{len(recent_requests)} requests in {self.rate_limit_window} seconds",
                source_ip=ip_address,
                user_id=user_id,
                details={
                    "endpoint": endpoint,
                    "method": method,
                    "requests_count": len(recent_requests),
                    "time_window": self.rate_limit_window
                }
            )
        
        # Check for malicious request patterns
        if self._is_malicious_request(endpoint, method, details):
            return self._create_alert(
                alert_type=AlertType.MALICIOUS_REQUEST,
                threat_level=ThreatLevel.HIGH,
                title=f"Malicious request detected: {method} {endpoint}",
                description="Request contains suspicious patterns",
                source_ip=ip_address,
                user_id=user_id,
                details={
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": status_code,
                    "user_agent": user_agent
                }
            )
        
        return None
    
    def _is_malicious_request(self, endpoint: str, method: str, details: Dict[str, Any]) -> bool:
        """Check if request contains malicious patterns"""
        # Check for SQL injection patterns
        sql_injection_patterns = [
            r"union\s+select",
            r"drop\s+table",
            r"insert\s+into",
            r"delete\s+from",
            r"update\s+set",
            r"exec\s*\(",
            r"script\s*>",
            r"<\s*script"
        ]
        
        request_data = json.dumps(details or {}).lower()
        
        for pattern in sql_injection_patterns:
            if re.search(pattern, request_data, re.IGNORECASE):
                return True
        
        # Check for XSS patterns
        xss_patterns = [
            r"<script",
            r"javascript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*="
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, request_data, re.IGNORECASE):
                return True
        
        return False
    
    def check_data_access(self, 
                         user_id: str,
                         resource_id: str,
                         resource_type: str,
                         action: str,
                         ip_address: str,
                         data_volume: int = None) -> Optional[SecurityAlert]:
        """Check data access for potential exfiltration"""
        # Check for unusual data access patterns
        if data_volume and data_volume > 1000000:  # 1MB threshold
            return self._create_alert(
                alert_type=AlertType.DATA_EXFILTRATION,
                threat_level=ThreatLevel.MEDIUM,
                title=f"Large data access detected",
                description=f"User {user_id} accessed {data_volume} bytes of data",
                source_ip=ip_address,
                user_id=user_id,
                resource=resource_id,
                details={
                    "resource_type": resource_type,
                    "action": action,
                    "data_volume": data_volume
                }
            )
        
        # Check for access to sensitive resources
        sensitive_resources = ["admin", "config", "keys", "secrets"]
        if any(sensitive in resource_id.lower() for sensitive in sensitive_resources):
            return self._create_alert(
                alert_type=AlertType.UNAUTHORIZED_ACCESS,
                threat_level=ThreatLevel.HIGH,
                title=f"Access to sensitive resource: {resource_id}",
                description=f"User {user_id} accessed sensitive resource {resource_id}",
                source_ip=ip_address,
                user_id=user_id,
                resource=resource_id,
                details={
                    "resource_type": resource_type,
                    "action": action
                }
            )
        
        return None
    
    def _create_alert(self, 
                     alert_type: AlertType,
                     threat_level: ThreatLevel,
                     title: str,
                     description: str,
                     source_ip: str,
                     user_id: str = None,
                     resource: str = None,
                     details: Dict[str, Any] = None) -> SecurityAlert:
        """Create security alert"""
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.sha256(title.encode()).hexdigest()[:8]}"
        
        alert = SecurityAlert(
            alert_id=alert_id,
            alert_type=alert_type,
            threat_level=threat_level,
            title=title,
            description=description,
            source_ip=source_ip,
            user_id=user_id,
            resource=resource,
            details=details or {},
            confidence=self._calculate_confidence(alert_type, threat_level, details),
            correlation_id=f"corr_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.sha256(source_ip.encode()).hexdigest()[:8]}"
        )
        
        self.alerts[alert_id] = alert
        
        # Log security event
        self.audit_logger.log_security_event(
            event_type=AuditEventType.SECURITY_BREACH if threat_level == ThreatLevel.CRITICAL else AuditEventType.SUSPICIOUS_ACTIVITY,
            user_id=user_id,
            ip_address=source_ip,
            details={
                "alert_id": alert_id,
                "alert_type": alert_type.value,
                "threat_level": threat_level.value,
                "title": title
            },
            risk_score=self._threat_level_to_score(threat_level)
        )
        
        # Auto-create incident for critical alerts
        if threat_level == ThreatLevel.CRITICAL:
            self._create_incident_from_alert(alert)
        
        return alert
    
    def _calculate_confidence(self, alert_type: AlertType, threat_level: ThreatLevel, details: Dict[str, Any]) -> float:
        """Calculate confidence score for alert"""
        base_confidence = {
            AlertType.BRUTE_FORCE: 0.9,
            AlertType.SUSPICIOUS_LOGIN: 0.7,
            AlertType.UNAUTHORIZED_ACCESS: 0.8,
            AlertType.DATA_EXFILTRATION: 0.6,
            AlertType.MALICIOUS_REQUEST: 0.8,
            AlertType.RATE_LIMIT_EXCEEDED: 0.5,
            AlertType.PRIVILEGE_ESCALATION: 0.9
        }
        
        confidence = base_confidence.get(alert_type, 0.5)
        
        # Adjust based on threat level
        if threat_level == ThreatLevel.CRITICAL:
            confidence = min(confidence + 0.2, 1.0)
        elif threat_level == ThreatLevel.LOW:
            confidence = max(confidence - 0.2, 0.0)
        
        return confidence
    
    def _threat_level_to_score(self, threat_level: ThreatLevel) -> int:
        """Convert threat level to risk score"""
        score_mapping = {
            ThreatLevel.LOW: 25,
            ThreatLevel.MEDIUM: 50,
            ThreatLevel.HIGH: 75,
            ThreatLevel.CRITICAL: 100
        }
        return score_mapping.get(threat_level, 50)
    
    def _create_incident_from_alert(self, alert: SecurityAlert) -> SecurityIncident:
        """Create security incident from alert"""
        incident_id = f"incident_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.sha256(alert.title.encode()).hexdigest()[:8]}"
        
        incident = SecurityIncident(
            incident_id=incident_id,
            title=alert.title,
            description=alert.description,
            severity=alert.threat_level,
            status=IncidentStatus.OPEN,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            alerts=[alert.alert_id],
            affected_assets=[alert.resource] if alert.resource else [],
            metadata={
                "source_alert": alert.alert_id,
                "correlation_id": alert.correlation_id
            }
        )
        
        self.incidents[incident_id] = incident
        
        # Log incident creation
        self.audit_logger.log_security_event(
            event_type=AuditEventType.SECURITY_BREACH,
            user_id=alert.user_id,
            ip_address=alert.source_ip,
            details={
                "incident_id": incident_id,
                "action": "incident_created",
                "severity": alert.threat_level.value
            },
            risk_score=self._threat_level_to_score(alert.threat_level)
        )
        
        return incident
    
    def get_alerts(self, 
                  alert_type: AlertType = None,
                  threat_level: ThreatLevel = None,
                  status: str = None,
                  limit: int = 100) -> List[SecurityAlert]:
        """Get security alerts with filters"""
        alerts = list(self.alerts.values())
        
        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]
        
        if threat_level:
            alerts = [a for a in alerts if a.threat_level == threat_level]
        
        if status:
            alerts = [a for a in alerts if a.status == status]
        
        # Sort by timestamp (most recent first)
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        return alerts[:limit]
    
    def get_incidents(self, 
                     severity: ThreatLevel = None,
                     status: IncidentStatus = None,
                     limit: int = 100) -> List[SecurityIncident]:
        """Get security incidents with filters"""
        incidents = list(self.incidents.values())
        
        if severity:
            incidents = [i for i in incidents if i.severity == severity]
        
        if status:
            incidents = [i for i in incidents if i.status == status]
        
        # Sort by created_at (most recent first)
        incidents.sort(key=lambda x: x.created_at, reverse=True)
        
        return incidents[:limit]
    
    def update_incident_status(self, incident_id: str, status: IncidentStatus, notes: str = None) -> bool:
        """Update incident status"""
        incident = self.incidents.get(incident_id)
        if not incident:
            return False
        
        old_status = incident.status
        incident.status = status
        incident.updated_at = datetime.now()
        
        if status == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.now()
        
        if notes:
            incident.metadata["status_notes"] = notes
        
        # Log status update
        self.audit_logger.log_security_event(
            event_type=AuditEventType.SECURITY_BREACH,
            details={
                "incident_id": incident_id,
                "action": "status_updated",
                "old_status": old_status.value,
                "new_status": status.value,
                "notes": notes
            }
        )
        
        return True
    
    def block_ip_address(self, ip_address: str, reason: str = None, duration_hours: int = 24) -> bool:
        """Block IP address"""
        try:
            # Validate IP address
            ipaddress.ip_address(ip_address)
            
            self.blocked_ips.add(ip_address)
            
            # Log IP blocking
            self.audit_logger.log_security_event(
                event_type=AuditEventType.SECURITY_BREACH,
                ip_address=ip_address,
                details={
                    "action": "ip_blocked",
                    "reason": reason,
                    "duration_hours": duration_hours
                },
                risk_score=80
            )
            
            return True
            
        except ValueError:
            logger.error(f"Invalid IP address: {ip_address}")
            return False
    
    def unblock_ip_address(self, ip_address: str) -> bool:
        """Unblock IP address"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            
            # Log IP unblocking
            self.audit_logger.log_security_event(
                event_type=AuditEventType.SECURITY_BREACH,
                ip_address=ip_address,
                details={
                    "action": "ip_unblocked"
                }
            )
            
            return True
        
        return False
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        return ip_address in self.blocked_ips
    
    def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Clean up failed login attempts
        for user_id in list(self.failed_login_attempts.keys()):
            self.failed_login_attempts[user_id] = deque(
                [attempt for attempt in self.failed_login_attempts[user_id] 
                 if attempt > cutoff_time],
                maxlen=50
            )
        
        # Clean up rate limit tracker
        for key in list(self.rate_limit_tracker.keys()):
            self.rate_limit_tracker[key] = deque(
                [req for req in self.rate_limit_tracker[key] 
                 if req > cutoff_time],
                maxlen=1000
            )
    
    def _analyze_patterns(self):
        """Analyze security patterns for anomalies"""
        # This would implement more sophisticated pattern analysis
        # For now, it's a placeholder for future enhancements
        pass
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """Get security monitoring dashboard"""
        dashboard = {
            "generated_at": datetime.now().isoformat(),
            "alert_summary": {},
            "incident_summary": {},
            "threat_intelligence": {},
            "blocked_ips": len(self.blocked_ips)
        }
        
        # Alert summary
        total_alerts = len(self.alerts)
        active_alerts = len([a for a in self.alerts.values() if a.status == "active"])
        
        alerts_by_level = defaultdict(int)
        alerts_by_type = defaultdict(int)
        
        for alert in self.alerts.values():
            if alert.status == "active":
                alerts_by_level[alert.threat_level.value] += 1
                alerts_by_type[alert.alert_type.value] += 1
        
        dashboard["alert_summary"] = {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "by_threat_level": dict(alerts_by_level),
            "by_type": dict(alerts_by_type)
        }
        
        # Incident summary
        total_incidents = len(self.incidents)
        open_incidents = len([i for i in self.incidents.values() if i.status in [IncidentStatus.OPEN, IncidentStatus.INVESTIGATING]])
        
        incidents_by_severity = defaultdict(int)
        for incident in self.incidents.values():
            incidents_by_severity[incident.severity.value] += 1
        
        dashboard["incident_summary"] = {
            "total_incidents": total_incidents,
            "open_incidents": open_incidents,
            "by_severity": dict(incidents_by_severity)
        }
        
        # Threat intelligence summary
        intel_by_type = defaultdict(int)
        for intel in self.threat_intel.values():
            intel_by_type[intel.indicator_type] += 1
        
        dashboard["threat_intelligence"] = {
            "total_indicators": len(self.threat_intel),
            "by_type": dict(intel_by_type)
        }
        
        return dashboard


# Global instance
security_monitor = SecurityMonitor()
