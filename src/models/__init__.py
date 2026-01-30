"""
Helm AI Database Models
SQLAlchemy models for the Helm AI application
"""

from sqlalchemy.ext.declarative import declarative_base

# Create Base class once
Base = declarative_base()

# Import models after Base is created
from .user import User, UserStatus, UserRole
from .api_key import APIKey, APIKeyStatus, APIKeyScope
from .audit_log import AuditLog, AuditAction, AuditSeverity, AuditCategory, APIUsageLog
from .security_event import SecurityEvent, SecurityEventType, SecuritySeverity, ThreatType, EventStatus
from .game_session import GameSession, GameSessionStatus, GameType, CheatDetectionStatus

# Export all models for easy importing
__all__ = [
    # Base class
    "Base",
    
    # User models
    "User",
    "UserStatus", 
    "UserRole",
    
    # API Key models
    "APIKey",
    "APIKeyStatus",
    "APIKeyScope",
    
    # Audit models
    "AuditLog",
    "AuditAction",
    "AuditSeverity", 
    "AuditCategory",
    "APIUsageLog",
    
    # Security models
    "SecurityEvent",
    "SecurityEventType",
    "SecuritySeverity",
    "ThreatType",
    "EventStatus",
    
    # Game session models
    "GameSession",
    "GameSessionStatus",
    "GameType",
    "CheatDetectionStatus"
]
