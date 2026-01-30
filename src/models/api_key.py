"""
Helm AI API Key Model
SQLAlchemy model for API key management
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import enum
import secrets
import hashlib

from . import Base

class APIKeyStatus(enum.Enum):
    """API key status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    EXPIRED = "expired"

class APIKeyScope(enum.Enum):
    """API key scope enumeration"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    ANALYTICS = "analytics"
    INTEGRATIONS = "integrations"

class APIKey(Base):
    """API key model for authentication and authorization"""
    
    __tablename__ = "api_keys"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Key information
    key_id = Column(String(64), unique=True, index=True, nullable=False)
    key_hash = Column(String(255), nullable=False)  # Hash of the actual key
    key_prefix = Column(String(8), nullable=False)  # First 8 characters for display
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Key details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Status and permissions
    status = Column(SQLEnum(APIKeyStatus), default=APIKeyStatus.ACTIVE)
    scopes = Column(JSON, default=list)  # List of allowed scopes
    
    # Usage limits
    rate_limit_per_minute = Column(Integer, default=60)
    rate_limit_per_hour = Column(Integer, default=1000)
    rate_limit_per_day = Column(Integer, default=10000)
    
    # Expiration
    expires_at = Column(DateTime, nullable=True)
    
    # Usage tracking
    last_used_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    total_requests = Column(Integer, default=0)
    
    # IP restrictions
    allowed_ips = Column(JSON, default=list)  # List of allowed IP addresses
    allowed_domains = Column(JSON, default=list)  # List of allowed domains
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    usage_logs = relationship("APIUsageLog", back_populates="api_key", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<APIKey(id={self.id}, key_id={self.key_id}, user_id={self.user_id})>"
    
    @property
    def is_active(self) -> bool:
        """Check if API key is active and not expired"""
        if self.status != APIKeyStatus.ACTIVE:
            return False
        
        if self.expires_at and self.expires_at <= datetime.now():
            return False
        
        return True
    
    @property
    def is_expired(self) -> bool:
        """Check if API key is expired"""
        return self.expires_at and self.expires_at <= datetime.now()
    
    @property
    def days_until_expiry(self) -> Optional[int]:
        """Get days until expiry"""
        if not self.expires_at:
            return None
        
        delta = self.expires_at - datetime.now()
        return max(0, delta.days)
    
    @property
    def display_key(self) -> str:
        """Get display version of key (first 8 chars + masked)"""
        return f"{self.key_prefix}{'*' * 24}"
    
    def has_scope(self, scope: str) -> bool:
        """Check if API key has specific scope"""
        return scope in self.scopes
    
    def has_any_scope(self, scopes: List[str]) -> bool:
        """Check if API key has any of the specified scopes"""
        return any(scope in self.scopes for scope in scopes)
    
    def has_all_scopes(self, scopes: List[str]) -> bool:
        """Check if API key has all of the specified scopes"""
        return all(scope in self.scopes for scope in scopes)
    
    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed"""
        if not self.allowed_ips:
            return True  # No IP restrictions
        
        return ip_address in self.allowed_ips
    
    def is_domain_allowed(self, domain: str) -> bool:
        """Check if domain is allowed"""
        if not self.allowed_domains:
            return True  # No domain restrictions
        
        return domain in self.allowed_domains
    
    def check_rate_limit(self, period: str = "minute") -> bool:
        """Check if rate limit is exceeded for given period"""
        # This would integrate with the rate limiting system
        # For now, return True (no limit exceeded)
        return True
    
    def record_usage(self, request_count: int = 1):
        """Record API key usage"""
        self.last_used_at = datetime.now()
        self.usage_count += request_count
        self.total_requests += request_count
    
    def revoke(self):
        """Revoke API key"""
        self.status = APIKeyStatus.INACTIVE
        self.updated_at = datetime.now()
    
    def suspend(self):
        """Suspend API key"""
        self.status = APIKeyStatus.SUSPENDED
        self.updated_at = datetime.now()
    
    def reactivate(self):
        """Reactivate API key"""
        if self.is_expired:
            self.status = APIKeyStatus.EXPIRED
        else:
            self.status = APIKeyStatus.ACTIVE
        self.updated_at = datetime.now()
    
    def extend_expiry(self, days: int):
        """Extend expiry date"""
        if self.expires_at:
            self.expires_at = self.expires_at + timedelta(days=days)
        else:
            self.expires_at = datetime.now() + timedelta(days=days)
        self.updated_at = datetime.now()
    
    def add_scope(self, scope: str):
        """Add scope to API key"""
        if scope not in self.scopes:
            self.scopes.append(scope)
            self.updated_at = datetime.now()
    
    def remove_scope(self, scope: str):
        """Remove scope from API key"""
        if scope in self.scopes:
            self.scopes.remove(scope)
            self.updated_at = datetime.now()
    
    def set_scopes(self, scopes: List[str]):
        """Set API key scopes"""
        self.scopes = scopes
        self.updated_at = datetime.now()
    
    def add_allowed_ip(self, ip_address: str):
        """Add allowed IP address"""
        if ip_address not in self.allowed_ips:
            self.allowed_ips.append(ip_address)
            self.updated_at = datetime.now()
    
    def remove_allowed_ip(self, ip_address: str):
        """Remove allowed IP address"""
        if ip_address in self.allowed_ips:
            self.allowed_ips.remove(ip_address)
            self.updated_at = datetime.now()
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert API key to dictionary"""
        data = {
            "id": self.id,
            "key_id": self.key_id,
            "key_prefix": self.key_prefix,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "scopes": self.scopes,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "rate_limit_per_hour": self.rate_limit_per_hour,
            "rate_limit_per_day": self.rate_limit_per_day,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "usage_count": self.usage_count,
            "total_requests": self.total_requests,
            "allowed_ips": self.allowed_ips,
            "allowed_domains": self.allowed_domains,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "is_expired": self.is_expired,
            "days_until_expiry": self.days_until_expiry,
            "display_key": self.display_key
        }
        
        if include_sensitive:
            data["key_hash"] = self.key_hash
        
        return data
    
    @classmethod
    def generate_key(cls, prefix: str = "hk") -> tuple[str, str]:
        """Generate new API key and return (key, key_id)"""
        # Generate 32-character key
        key = f"{prefix}_{secrets.token_urlsafe(24)}"
        
        # Generate key_id (hash of key)
        key_id = hashlib.sha256(key.encode()).hexdigest()[:16]
        
        return key, key_id
    
    @classmethod
    def hash_key(cls, key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    @classmethod
    def create_api_key(cls, user_id: int, name: str, **kwargs) -> "APIKey":
        """Create new API key with default settings"""
        defaults = {
            "status": APIKeyStatus.ACTIVE,
            "scopes": [APIKeyScope.READ.value],
            "rate_limit_per_minute": 60,
            "rate_limit_per_hour": 1000,
            "rate_limit_per_day": 10000,
            "allowed_ips": [],
            "allowed_domains": []
        }
        
        # Override defaults with provided kwargs
        defaults.update(kwargs)
        
        # Generate key and key_id
        key, key_id = cls.generate_key()
        key_hash = cls.hash_key(key)
        key_prefix = key[:8]
        
        api_key = cls(
            key_id=key_id,
            key_hash=key_hash,
            key_prefix=key_prefix,
            user_id=user_id,
            name=name.strip(),
            **defaults
        )
        
        return api_key, key
