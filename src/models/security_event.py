"""
Helm AI Security Event Model
SQLAlchemy model for security event tracking and threat detection
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum as SQLEnum, ForeignKey, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import enum

from . import Base

class SecurityEventType(enum.Enum):
    """Security event type enumeration"""
    LOGIN_FAILURE = "login_failure"
    LOGIN_SUCCESS = "login_success"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    ACCOUNT_LOCKOUT = "account_lockout"
    ACCOUNT_UNLOCK = "account_unlock"
    API_KEY_CREATED = "api_key_created"
    API_KEY_DELETED = "api_key_deleted"
    API_KEY_SUSPENDED = "api_key_suspended"
    PERMISSION_ESCALATION = "permission_escalation"
    ROLE_CHANGE = "role_change"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    THREAT_DETECTED = "threat_detected"
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    SYSTEM_COMPROMISE = "system_compromise"
    MALICIOUS_REQUEST = "malicious_request"
    UNAUTHORIZED_ACCESS = "unauthorized_access"

class SecuritySeverity(enum.Enum):
    """Security event severity enumeration"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(enum.Enum):
    """Threat type enumeration"""
    BRUTE_FORCE = "brute_force"
    CREDENTIAL_STUFFING = "credential_stuffing"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    CSRF_ATTACK = "csrf_attack"
    DOS_ATTACK = "dos_attack"
    MALWARE = "malware"
    PHISHING = "phishing"
    INSIDER_THREAT = "insider_threat"
    DATA_EXFILTRATION = "data_exfiltration"
    ACCOUNT_TAKEOVER = "account_takeover"
    API_ABUSE = "api_abuse"
    UNAUTHORIZED_API = "unauthorized_api"
    SUSPICIOUS_PATTERN = "suspicious_pattern"

class EventStatus(enum.Enum):
    """Event status enumeration"""
    NEW = "new"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    IGNORED = "ignored"

class SecurityEvent(Base):
    """Security event model for tracking security incidents"""
    
    __tablename__ = "security_events"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Event information
    event_type = Column(SQLEnum(SecurityEventType), nullable=False, index=True)
    severity = Column(SQLEnum(SecuritySeverity), nullable=False, index=True)
    threat_type = Column(SQLEnum(ThreatType), nullable=True, index=True)
    status = Column(SQLEnum(EventStatus), default=EventStatus.NEW, index=True)
    
    # Event details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    details = Column(JSON, default=dict)  # Detailed event information
    
    # Source information
    source_ip = Column(String(45), nullable=True, index=True)
    source_country = Column(String(2), nullable=True, index=True)
    source_user_agent = Column(Text, nullable=True)
    source_api_key = Column(String(64), nullable=True, index=True)
    
    # Target information
    target_resource = Column(String(255), nullable=True)  # What was targeted
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    target_endpoint = Column(String(255), nullable=True)
    
    # Detection information
    detection_method = Column(String(100), nullable=True)  # How it was detected
    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    risk_score = Column(Float, nullable=True)  # 0.0 to 100.0
    
    # Geographic information
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    city = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    
    # Temporal information
    occurred_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    detected_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Investigation information
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    investigation_notes = Column(Text, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Automated response
    auto_response_taken = Column(Boolean, default=False)
    auto_response_details = Column(JSON, default=dict)
    
    # Related events
    parent_event_id = Column(Integer, ForeignKey("security_events.id"), nullable=True, index=True)
    related_events = Column(JSON, default=list)  # List of related event IDs
    
    # Compliance information
    compliance_tags = Column(JSON, default=list)  # GDPR, SOX, HIPAA, etc.
    requires_reporting = Column(Boolean, default=False)
    reported_at = Column(DateTime, nullable=True)
    
    # Retention
    retention_days = Column(Integer, default=2555)  # Default 7 years for security events
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="security_events")
    target_user = relationship("User", foreign_keys=[target_user_id])
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    resolved_user = relationship("User", foreign_keys=[resolved_by])
    parent_event = relationship("SecurityEvent", remote_side=[id])
    
    def __repr__(self):
        return f"<SecurityEvent(id={self.id}, type={self.event_type}, severity={self.severity})>"
    
    @property
    def is_critical(self) -> bool:
        """Check if this is a critical security event"""
        return self.severity == SecuritySeverity.CRITICAL
    
    @property
    def is_high_risk(self) -> bool:
        """Check if this is a high-risk event"""
        return (
            self.severity in [SecuritySeverity.HIGH, SecuritySeverity.CRITICAL] or
            self.threat_type in [
                ThreatType.SYSTEM_COMPROMISE,
                ThreatType.DATA_BREACH_ATTEMPT,
                ThreatType.ACCOUNT_TAKEOVER
            ] or
            (self.risk_score and self.risk_score >= 70)
        )
    
    @property
    def requires_immediate_action(self) -> bool:
        """Check if this event requires immediate action"""
        return (
            self.is_critical or
            self.threat_type in [
                ThreatType.SYSTEM_COMPROMISE,
                ThreatType.DATA_BREACH_ATTEMPT,
                ThreatType.ACCOUNT_TAKEOVER
            ]
        )
    
    @property
    def is_recent(self, hours: int = 24) -> bool:
        """Check if event occurred within specified hours"""
        return datetime.now() - self.occurred_at <= timedelta(hours=hours)
    
    @property
    def age_hours(self) -> float:
        """Get event age in hours"""
        return (datetime.now() - self.occurred_at).total_seconds() / 3600
    
    @property
    def is_resolved(self) -> bool:
        """Check if event is resolved"""
        return self.status in [EventStatus.RESOLVED, EventStatus.FALSE_POSITIVE, EventStatus.IGNORED]
    
    def assign_to_user(self, user_id: int):
        """Assign event to user for investigation"""
        self.assigned_to = user_id
        self.status = EventStatus.INVESTIGATING
        self.updated_at = datetime.now()
    
    def mark_resolved(self, user_id: int, notes: str = None):
        """Mark event as resolved"""
        self.status = EventStatus.RESOLVED
        self.resolved_at = datetime.now()
        self.resolved_by = user_id
        self.resolution_notes = notes
        self.updated_at = datetime.now()
    
    def mark_false_positive(self, user_id: int, notes: str = None):
        """Mark event as false positive"""
        self.status = EventStatus.FALSE_POSITIVE
        self.resolved_at = datetime.now()
        self.resolved_by = user_id
        self.resolution_notes = notes
        self.updated_at = datetime.now()
    
    def mark_ignored(self, user_id: int, notes: str = None):
        """Mark event as ignored"""
        self.status = EventStatus.IGNORED
        self.resolved_at = datetime.now()
        self.resolved_by = user_id
        self.resolution_notes = notes
        self.updated_at = datetime.now()
    
    def add_related_event(self, event_id: int):
        """Add related event ID"""
        if event_id not in self.related_events:
            self.related_events.append(event_id)
    
    def add_compliance_tag(self, tag: str):
        """Add compliance tag"""
        if tag not in self.compliance_tags:
            self.compliance_tags.append(tag)
            if tag in ["GDPR", "HIPAA", "SOX"]:
                self.requires_reporting = True
    
    def calculate_risk_score(self) -> float:
        """Calculate risk score based on various factors"""
        score = 0.0
        
        # Base score from severity
        severity_scores = {
            SecuritySeverity.INFO: 10,
            SecuritySeverity.LOW: 25,
            SecuritySeverity.MEDIUM: 50,
            SecuritySeverity.HIGH: 75,
            SecuritySeverity.CRITICAL: 95
        }
        score += severity_scores.get(self.severity, 25)
        
        # Threat type adjustments
        threat_multipliers = {
            ThreatType.BRUTE_FORCE: 1.2,
            ThreatType.CREDENTIAL_STUFFING: 1.3,
            ThreatType.SQL_INJECTION: 1.5,
            ThreatType.SYSTEM_COMPROMISE: 2.0,
            ThreatType.DATA_BREACH_ATTEMPT: 1.8,
            ThreatType.ACCOUNT_TAKEOVER: 1.7
        }
        
        if self.threat_type:
            score *= threat_multipliers.get(self.threat_type, 1.0)
        
        # Confidence score adjustment
        if self.confidence_score:
            score *= (0.5 + self.confidence_score * 0.5)  # Scale between 0.5x and 1.0x
        
        # Add points for multiple cheat types
        score += len(self.cheat_types_detected) * 10  # 10 points per cheat type
        
        # Add points for suspicious behavior patterns
        if self.variance_score and self.variance_score > 0.8:
            score += 15
        
        if self.aggression_score and self.aggression_score > 0.9:
            score += 10
        
        # Add points for unusual performance metrics
        if self.avg_decision_time_ms and self.avg_decision_time_ms < 100:  # Too fast
            score += 10
        
        if self.win_rate and self.win_rate > 0.8:  # Too high win rate
            score += 15
        
        # Cap at 100
        return min(100.0, score)
    
    def update_risk_score(self):
        """Update risk score"""
        self.risk_score = self.calculate_risk_score()
        self.updated_at = datetime.now()
    
    def set_retention_days(self, days: int):
        """Set retention period in days"""
        if self.is_critical or self.requires_reporting:
            self.retention_days = max(2555, days)  # Minimum 7 years for critical events
        else:
            self.retention_days = max(365, days)  # Minimum 1 year for other events
    
    def to_dict(self, include_sensitive: bool = True) -> Dict[str, Any]:
        """Convert security event to dictionary"""
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "threat_type": self.threat_type.value if self.threat_type else None,
            "status": self.status.value,
            "title": self.title,
            "description": self.description,
            "source_ip": self.source_ip,
            "source_country": self.source_country,
            "source_api_key": self.source_api_key,
            "target_resource": self.target_resource,
            "target_user_id": self.target_user_id,
            "target_endpoint": self.target_endpoint,
            "detection_method": self.detection_method,
            "confidence_score": self.confidence_score,
            "risk_score": self.risk_score,
            "occurred_at": self.occurred_at.isoformat() if self.occurred_at else None,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "assigned_to": self.assigned_to,
            "investigation_notes": self.investigation_notes,
            "resolution_notes": self.resolution_notes,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "auto_response_taken": self.auto_response_taken,
            "related_events": self.related_events,
            "compliance_tags": self.compliance_tags,
            "requires_reporting": self.requires_reporting,
            "reported_at": self.reported_at.isoformat() if self.reported_at else None,
            "retention_days": self.retention_days,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_critical": self.is_critical,
            "is_high_risk": self.is_high_risk,
            "requires_immediate_action": self.requires_immediate_action,
            "is_resolved": self.is_resolved,
            "age_hours": self.age_hours
        }
        
        if include_sensitive:
            data.update({
                "details": self.details,
                "source_user_agent": self.source_user_agent,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "city": self.city,
                "region": self.region,
                "auto_response_details": self.auto_response_details
            })
        
        return data
    
    @classmethod
    def create_event(cls, event_type: SecurityEventType, severity: SecuritySeverity, title: str, description: str, **kwargs) -> "SecurityEvent":
        """Create new security event"""
        defaults = {
            "status": EventStatus.NEW,
            "compliance_tags": [],
            "retention_days": 2555,  # 7 years default for security events
            "requires_reporting": False
        }
        
        # Override defaults with provided kwargs
        defaults.update(kwargs)
        
        event = cls(
            event_type=event_type,
            severity=severity,
            title=title,
            description=description,
            **defaults
        )
        
        # Calculate initial risk score
        event.update_risk_score()
        
        return event
    
    @classmethod
    def create_login_event(cls, user_id: int, success: bool, ip_address: str, **kwargs) -> "SecurityEvent":
        """Create login security event"""
        event_type = SecurityEventType.LOGIN_SUCCESS if success else SecurityEventType.LOGIN_FAILURE
        severity = SecuritySeverity.INFO if success else SecuritySeverity.MEDIUM
        
        return cls.create_event(
            event_type=event_type,
            severity=severity,
            title=f"Login {'Success' if success else 'Failure'}",
            description=f"User login {'succeeded' if success else 'failed'} from {ip_address}",
            user_id=user_id,
            source_ip=ip_address,
            **kwargs
        )
    
    @classmethod
    def create_threat_event(cls, threat_type: ThreatType, severity: SecuritySeverity, title: str, description: str, **kwargs) -> "SecurityEvent":
        """Create threat detection event"""
        return cls.create_event(
            event_type=SecurityEventType.THREAT_DETECTED,
            severity=severity,
            title=title,
            description=description,
            threat_type=threat_type,
            requires_immediate_action=True,
            compliance_tags=["security", "threat_detection"],
            **kwargs
        )
    
    @classmethod
    def create_api_security_event(cls, event_type: SecurityEventType, api_key_id: str, ip_address: str, **kwargs) -> "SecurityEvent":
        """Create API security event"""
        return cls.create_event(
            event_type=event_type,
            severity=SecuritySeverity.MEDIUM,
            title=f"API Security: {event_type.value}",
            description=f"API security event: {event_type.value} from {ip_address}",
            source_api_key=api_key_id,
            source_ip=ip_address,
            compliance_tags=["api_security"],
            **kwargs
        )
