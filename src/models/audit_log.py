"""
Helm AI Audit Log Model
SQLAlchemy model for audit logging and compliance tracking
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import enum

from . import Base

class AuditAction(enum.Enum):
    """Audit action enumeration"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    FAILED_LOGIN = "failed_login"
    PASSWORD_CHANGE = "password_change"
    API_KEY_CREATE = "api_key_create"
    API_KEY_DELETE = "api_key_delete"
    PERMISSION_CHANGE = "permission_change"
    ROLE_CHANGE = "role_change"
    EXPORT = "export"
    IMPORT = "import"
    SYSTEM_CONFIG = "system_config"
    SECURITY_EVENT = "security_event"

class AuditSeverity(enum.Enum):
    """Audit severity enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditCategory(enum.Enum):
    """Audit category enumeration"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    SYSTEM_ADMIN = "system_admin"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    API_USAGE = "api_usage"
    USER_MANAGEMENT = "user_management"
    INTEGRATION = "integration"

class AuditLog(Base):
    """Audit log model for tracking all system activities"""
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Event information
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    category = Column(SQLEnum(AuditCategory), nullable=False, index=True)
    severity = Column(SQLEnum(AuditSeverity), default=AuditSeverity.LOW, index=True)
    
    # Resource information
    resource_type = Column(String(100), nullable=True, index=True)  # user, api_key, etc.
    resource_id = Column(String(255), nullable=True, index=True)    # ID of the resource
    resource_name = Column(String(255), nullable=True)             # Human-readable name
    
    # Description and details
    description = Column(Text, nullable=False)
    details = Column(JSON, default=dict)  # Additional event details
    
    # Request information
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(64), nullable=True, index=True)  # Correlation ID
    session_id = Column(String(64), nullable=True, index=True)
    
    # API information
    api_key_id = Column(String(64), nullable=True, index=True)  # API key used
    endpoint = Column(String(255), nullable=True, index=True)
    http_method = Column(String(10), nullable=True)
    http_status_code = Column(Integer, nullable=True)
    
    # Result information
    success = Column(Boolean, default=True, index=True)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(100), nullable=True)
    
    # Timing information
    duration_ms = Column(Integer, nullable=True)  # Request duration in milliseconds
    
    # Compliance information
    compliance_tags = Column(JSON, default=list)  # GDPR, SOX, HIPAA, etc.
    retention_days = Column(Integer, default=2555)  # Default 7 years
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"
    
    @property
    def is_security_event(self) -> bool:
        """Check if this is a security-related event"""
        return (
            self.category == AuditCategory.SECURITY or
            self.action in [
                AuditAction.FAILED_LOGIN,
                AuditAction.PASSWORD_CHANGE,
                AuditAction.PERMISSION_CHANGE,
                AuditAction.ROLE_CHANGE
            ]
        )
    
    @property
    def is_compliance_event(self) -> bool:
        """Check if this is a compliance-related event"""
        return (
            self.category == AuditCategory.COMPLIANCE or
            len(self.compliance_tags) > 0
        )
    
    @property
    def is_high_risk(self) -> bool:
        """Check if this is a high-risk event"""
        return (
            self.severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL] or
            self.action in [
                AuditAction.DELETE,
                AuditAction.PERMISSION_CHANGE,
                AuditAction.ROLE_CHANGE,
                AuditAction.EXPORT,
                AuditAction.SYSTEM_CONFIG
            ]
        )
    
    def add_compliance_tag(self, tag: str):
        """Add compliance tag"""
        if tag not in self.compliance_tags:
            self.compliance_tags.append(tag)
    
    def remove_compliance_tag(self, tag: str):
        """Remove compliance tag"""
        if tag in self.compliance_tags:
            self.compliance_tags.remove(tag)
    
    def set_retention_days(self, days: int):
        """Set retention period in days"""
        self.retention_days = max(30, days)  # Minimum 30 days
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action.value,
            "category": self.category.value,
            "severity": self.severity.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "resource_name": self.resource_name,
            "description": self.description,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "api_key_id": self.api_key_id,
            "endpoint": self.endpoint,
            "http_method": self.http_method,
            "http_status_code": self.http_status_code,
            "success": self.success,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "duration_ms": self.duration_ms,
            "compliance_tags": self.compliance_tags,
            "retention_days": self.retention_days,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_security_event": self.is_security_event,
            "is_compliance_event": self.is_compliance_event,
            "is_high_risk": self.is_high_risk
        }
    
    @classmethod
    def create_log(cls, action: AuditAction, category: AuditCategory, description: str, **kwargs) -> "AuditLog":
        """Create new audit log entry"""
        defaults = {
            "severity": AuditSeverity.LOW,
            "success": True,
            "compliance_tags": [],
            "retention_days": 2555  # 7 years default
        }
        
        # Override defaults with provided kwargs
        defaults.update(kwargs)
        
        return cls(
            action=action,
            category=category,
            description=description,
            **defaults
        )
    
    @classmethod
    def log_authentication_event(cls, user_id: int, action: AuditAction, success: bool, **kwargs) -> "AuditLog":
        """Create authentication audit log"""
        return cls.create_log(
            action=action,
            category=AuditCategory.AUTHENTICATION,
            description=f"Authentication {action.value}",
            user_id=user_id,
            success=success,
            severity=AuditSeverity.HIGH if not success else AuditSeverity.LOW,
            compliance_tags=["authentication"],
            **kwargs
        )
    
    @classmethod
    def log_authorization_event(cls, user_id: int, action: AuditAction, resource_type: str, resource_id: str, success: bool, **kwargs) -> "AuditLog":
        """Create authorization audit log"""
        return cls.create_log(
            action=action,
            category=AuditCategory.AUTHORIZATION,
            description=f"Authorization {action.value} on {resource_type}",
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            success=success,
            severity=AuditSeverity.MEDIUM,
            compliance_tags=["authorization"],
            **kwargs
        )
    
    @classmethod
    def log_data_access_event(cls, user_id: int, action: AuditAction, resource_type: str, resource_id: str, **kwargs) -> "AuditLog":
        """Create data access audit log"""
        return cls.create_log(
            action=action,
            category=AuditCategory.DATA_ACCESS,
            description=f"Data {action.value} on {resource_type}",
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            severity=AuditSeverity.LOW,
            compliance_tags=["data_access"],
            **kwargs
        )
    
    @classmethod
    def log_security_event(cls, action: AuditAction, description: str, severity: AuditSeverity = AuditSeverity.HIGH, **kwargs) -> "AuditLog":
        """Create security audit log"""
        return cls.create_log(
            action=action,
            category=AuditCategory.SECURITY,
            description=description,
            severity=severity,
            compliance_tags=["security"],
            **kwargs
        )
    
    @classmethod
    def log_compliance_event(cls, action: AuditAction, description: str, compliance_tags: List[str], **kwargs) -> "AuditLog":
        """Create compliance audit log"""
        return cls.create_log(
            action=action,
            category=AuditCategory.COMPLIANCE,
            description=description,
            severity=AuditSeverity.MEDIUM,
            compliance_tags=compliance_tags,
            **kwargs
        )
    
    @classmethod
    def log_api_usage_event(cls, user_id: int, api_key_id: str, endpoint: str, method: str, status_code: int, **kwargs) -> "AuditLog":
        """Create API usage audit log"""
        return cls.create_log(
            action=AuditAction.READ,
            category=AuditCategory.API_USAGE,
            description=f"API {method} {endpoint}",
            user_id=user_id,
            api_key_id=api_key_id,
            endpoint=endpoint,
            http_method=method,
            http_status_code=status_code,
            success=status_code < 400,
            severity=AuditSeverity.LOW,
            **kwargs
        )
    
    @classmethod
    def log_system_admin_event(cls, user_id: int, action: AuditAction, description: str, **kwargs) -> "AuditLog":
        """Create system admin audit log"""
        return cls.create_log(
            action=action,
            category=AuditCategory.SYSTEM_ADMIN,
            description=description,
            user_id=user_id,
            severity=AuditSeverity.HIGH,
            compliance_tags=["system_admin"],
            **kwargs
        )


class APIUsageLog(Base):
    """API usage log model for detailed API tracking"""
    
    __tablename__ = "api_usage_logs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # API key relationship
    api_key_id = Column(String(64), ForeignKey("api_keys.key_id"), nullable=False, index=True)
    
    # Request information
    endpoint = Column(String(255), nullable=False, index=True)
    http_method = Column(String(10), nullable=False, index=True)
    http_status_code = Column(Integer, nullable=False, index=True)
    
    # Timing information
    request_timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)
    duration_ms = Column(Integer, nullable=False)
    
    # Request details
    request_size_bytes = Column(Integer, nullable=True)
    response_size_bytes = Column(Integer, nullable=True)
    
    # Client information
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(64), nullable=True, index=True)
    
    # Additional metadata
    request_metadata = Column(JSON, default=dict)
    
    # Relationships
    api_key = relationship("APIKey", back_populates="usage_logs")
    
    def __repr__(self):
        return f"<APIUsageLog(id={self.id}, api_key_id={self.api_key_id}, endpoint={self.endpoint})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert API usage log to dictionary"""
        return {
            "id": self.id,
            "api_key_id": self.api_key_id,
            "endpoint": self.endpoint,
            "http_method": self.http_method,
            "http_status_code": self.http_status_code,
            "request_timestamp": self.request_timestamp.isoformat() if self.request_timestamp else None,
            "duration_ms": self.duration_ms,
            "request_size_bytes": self.request_size_bytes,
            "response_size_bytes": self.response_size_bytes,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_id": self.request_id,
            "request_metadata": self.request_metadata
        }
