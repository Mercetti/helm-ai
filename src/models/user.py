"""
Helm AI User Model
SQLAlchemy model for user management and authentication
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import enum

from . import Base

class UserStatus(enum.Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class UserRole(enum.Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"
    DEVELOPER = "developer"
    ANALYST = "analyst"

class User(Base):
    """User model for authentication and user management"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic user information
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=False)
    
    # Authentication fields
    password_hash = Column(String(255), nullable=True)  # For local auth
    auth_provider = Column(String(50), default="local")  # local, oauth2, saml
    provider_id = Column(String(255), nullable=True)  # External provider user ID
    
    # Status and roles
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    is_superuser = Column(Boolean, default=False)
    
    # Subscription and billing
    plan = Column(String(50), default="free")
    subscription_expires_at = Column(DateTime, nullable=True)
    trial_expires_at = Column(DateTime, nullable=True)
    
    # Profile information
    company = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    
    # Preferences and settings
    preferences = Column(JSON, default=dict)
    notification_settings = Column(JSON, default=dict)
    
    # Security fields
    last_login_at = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=True)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    security_events = relationship("SecurityEvent", foreign_keys="SecurityEvent.user_id", back_populates="user", cascade="all, delete-orphan")
    game_sessions = relationship("GameSession", foreign_keys="GameSession.user_id", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, status={self.status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if user is active and not locked"""
        if self.status != UserStatus.ACTIVE:
            return False
        
        if self.locked_until and self.locked_until > datetime.now():
            return False
        
        return True
    
    @property
    def is_trial_active(self) -> bool:
        """Check if user has an active trial"""
        if not self.trial_expires_at:
            return False
        
        return self.trial_expires_at > datetime.now()
    
    @property
    def is_subscription_active(self) -> bool:
        """Check if user has an active subscription"""
        if not self.subscription_expires_at:
            return False
        
        return self.subscription_expires_at > datetime.now()
    
    @property
    def requires_password_change(self) -> bool:
        """Check if user needs to change password"""
        if not self.password_changed_at:
            return True
        
        # Require password change every 90 days
        return datetime.now() - self.password_changed_at > timedelta(days=90)
    
    def get_permissions(self) -> List[str]:
        """Get user permissions based on role"""
        permissions = []
        
        if self.role == UserRole.USER:
            permissions.extend([
                "read_own_data",
                "create_api_keys",
                "manage_own_profile"
            ])
        
        elif self.role == UserRole.MODERATOR:
            permissions.extend([
                "read_own_data",
                "create_api_keys",
                "manage_own_profile",
                "moderate_content",
                "view_analytics"
            ])
        
        elif self.role == UserRole.DEVELOPER:
            permissions.extend([
                "read_own_data",
                "create_api_keys",
                "manage_own_profile",
                "access_developer_tools",
                "view_system_metrics",
                "debug_api_calls"
            ])
        
        elif self.role == UserRole.ANALYST:
            permissions.extend([
                "read_own_data",
                "create_api_keys",
                "manage_own_profile",
                "view_all_analytics",
                "export_reports",
                "manage_dashboards"
            ])
        
        elif self.role == UserRole.ADMIN:
            permissions.extend([
                "read_all_data",
                "manage_users",
                "manage_system",
                "view_all_analytics",
                "manage_integrations",
                "access_admin_panel"
            ])
        
        if self.is_superuser:
            permissions.append("superuser")
        
        return permissions
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in self.get_permissions()
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary"""
        data = {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "name": self.name,
            "status": self.status.value,
            "role": self.role.value,
            "plan": self.plan,
            "company": self.company,
            "job_title": self.job_title,
            "timezone": self.timezone,
            "language": self.language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "is_active": self.is_active,
            "is_trial_active": self.is_trial_active,
            "is_subscription_active": self.is_subscription_active,
            "permissions": self.get_permissions()
        }
        
        if include_sensitive:
            data.update({
                "auth_provider": self.auth_provider,
                "provider_id": self.provider_id,
                "failed_login_attempts": self.failed_login_attempts,
                "locked_until": self.locked_until.isoformat() if self.locked_until else None,
                "two_factor_enabled": self.two_factor_enabled,
                "preferences": self.preferences,
                "notification_settings": self.notification_settings
            })
        
        return data
    
    @classmethod
    def create_user(cls, email: str, name: str, **kwargs) -> "User":
        """Create new user with default settings"""
        defaults = {
            "status": UserStatus.ACTIVE,
            "role": UserRole.USER,
            "plan": "free",
            "preferences": {
                "theme": "light",
                "notifications": True,
                "email_marketing": True
            },
            "notification_settings": {
                "email": True,
                "push": False,
                "sms": False
            }
        }
        
        # Override defaults with provided kwargs
        defaults.update(kwargs)
        
        user = cls(
            email=email.lower().strip(),
            name=name.strip(),
            **defaults
        )
        
        return user
