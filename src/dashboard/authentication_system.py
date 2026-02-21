#!/usr/bin/env python3
"""
Authentication & Authorization System
Enterprise-grade security with SSO, RBAC, and compliance
"""

import os
import sys
import time
import json
import logging
import threading
import hashlib
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class UserRole(Enum):
    ADMIN = "admin"
    EXECUTIVE = "executive"
    MANAGER = "manager"
    ANALYST = "analyst"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    GUEST = "guest"

class AuthProvider(Enum):
    LOCAL = "local"
    SAML = "saml"
    OAUTH = "oauth"
    LDAP = "ldap"
    ACTIVE_DIRECTORY = "active_directory"

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    MANAGE_USERS = "manage_users"
    MANAGE_SYSTEM = "manage_system"
    VIEW_REPORTS = "view_reports"
    EXPORT_DATA = "export_data"

@dataclass
class User:
    """User data structure"""
    user_id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    permissions: List[Permission]
    auth_provider: AuthProvider
    last_login: Optional[datetime]
    created_at: datetime
    is_active: bool
    is_verified: bool
    two_factor_enabled: bool
    department: str
    manager_id: Optional[str]
    session_timeout: int
    allowed_ips: List[str]
    mfa_secret: Optional[str]

@dataclass
class Session:
    """Session data structure"""
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    is_active: bool
    permissions: List[Permission]
    access_token: str
    refresh_token: str

@dataclass
class RolePermission:
    """Role permission mapping"""
    role: UserRole
    permissions: List[Permission]
    description: str
    level: int  # 1=lowest, 10=highest

@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    event_type: str
    user_id: Optional[str]
    ip_address: str
    timestamp: datetime
    description: str
    severity: str  # low, medium, high, critical
    resolved: bool
    resolution_notes: Optional[str]

class AuthenticationSystem:
    """Authentication & Authorization System"""
    
    def __init__(self):
        self.logger = logging.getLogger("authentication_system")
        self.users = {}
        self.sessions = {}
        self.role_permissions = {}
        self.security_events = deque(maxlen=10000)
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
        self.jwt_expiry = 3600  # 1 hour
        self.refresh_expiry = 86400  # 24 hours
        self.max_failed_attempts = 5
        self.lockout_duration = 900  # 15 minutes
        self.failed_attempts = defaultdict(list)
        
        # Initialize with sample users and roles
        self._initialize_role_permissions()
        self._initialize_sample_users()
        self._initialize_security_events()
    
    def _initialize_role_permissions(self):
        """Initialize role permissions"""
        permissions = [
            RolePermission(
                role=UserRole.ADMIN,
                permissions=list(Permission),
                description="Full system access and management",
                level=10
            ),
            RolePermission(
                role=UserRole.EXECUTIVE,
                permissions=[Permission.READ, Permission.VIEW_REPORTS, Permission.EXPORT_DATA],
                description="Executive access to reports and analytics",
                level=8
            ),
            RolePermission(
                role=UserRole.MANAGER,
                permissions=[Permission.READ, Permission.WRITE, Permission.VIEW_REPORTS],
                description="Manager access with write permissions",
                level=6
            ),
            RolePermission(
                role=UserRole.ANALYST,
                permissions=[Permission.READ, Permission.VIEW_REPORTS, Permission.EXPORT_DATA],
                description="Analyst access to data and reports",
                level=5
            ),
            RolePermission(
                role=UserRole.DEVELOPER,
                permissions=[Permission.READ, Permission.WRITE, Permission.MANAGE_SYSTEM],
                description="Developer access to system management",
                level=7
            ),
            RolePermission(
                role=UserRole.VIEWER,
                permissions=[Permission.READ],
                description="Read-only access to system data",
                level=3
            ),
            RolePermission(
                role=UserRole.GUEST,
                permissions=[Permission.READ],
                description="Limited read access for guests",
                level=1
            )
        ]
        
        for perm in permissions:
            self.role_permissions[perm.role] = perm
        
        self.logger.info(f"Initialized {len(permissions)} role permissions")
    
    def _initialize_sample_users(self):
        """Initialize with sample users"""
        users = [
            {
                "user_id": "admin_001",
                "username": "admin",
                "email": "admin@stellarlogica.ai",
                "full_name": "System Administrator",
                "role": UserRole.ADMIN,
                "permissions": list(Permission),
                "auth_provider": AuthProvider.LOCAL,
                "last_login": datetime.now() - timedelta(hours=2),
                "created_at": datetime.now() - timedelta(days=365),
                "is_active": True,
                "is_verified": True,
                "two_factor_enabled": True,
                "department": "IT",
                "manager_id": None,
                "session_timeout": 480,  # 8 hours
                "allowed_ips": ["*"],  # All IPs allowed for admin
                "mfa_secret": None
            },
            {
                "user_id": "exec_001",
                "username": "ceo",
                "email": "ceo@stellarlogica.ai",
                "full_name": "Chief Executive Officer",
                "role": UserRole.EXECUTIVE,
                "permissions": [Permission.READ, Permission.VIEW_REPORTS, Permission.EXPORT_DATA],
                "auth_provider": AuthProvider.SAML,
                "last_login": datetime.now() - timedelta(hours=6),
                "created_at": datetime.now() - timedelta(days=180),
                "is_active": True,
                "is_verified": True,
                "two_factor_enabled": True,
                "department": "Executive",
                "manager_id": None,
                "session_timeout": 240,  # 4 hours
                "allowed_ips": ["*"],
                "mfa_secret": None
            },
            {
                "user_id": "mgr_001",
                "username": "manager",
                "email": "manager@stellarlogica.ai",
                "full_name": "Operations Manager",
                "role": UserRole.MANAGER,
                "permissions": [Permission.READ, Permission.WRITE, Permission.VIEW_REPORTS],
                "auth_provider": AuthProvider.LOCAL,
                "last_login": datetime.now() - timedelta(hours=4),
                "created_at": datetime.now() - timedelta(days=90),
                "is_active": True,
                "is_verified": True,
                "two_factor_enabled": False,
                "department": "Operations",
                "manager_id": "exec_001",
                "session_timeout": 180,  # 3 hours
                "allowed_ips": ["192.168.1.*", "10.0.0.*"],
                "mfa_secret": None
            },
            {
                "user_id": "analyst_001",
                "username": "analyst",
                "email": "analyst@stellarlogica.ai",
                "full_name": "Data Analyst",
                "role": UserRole.ANALYST,
                "permissions": [Permission.READ, Permission.VIEW_REPORTS, Permission.EXPORT_DATA],
                "auth_provider": AuthProvider.OAUTH,
                "last_login": datetime.now() - timedelta(hours=1),
                "created_at": datetime.now() - timedelta(days=60),
                "is_active": True,
                "is_verified": True,
                "two_factor_enabled": False,
                "department": "Analytics",
                "manager_id": "mgr_001",
                "session_timeout": 120,  # 2 hours
                "allowed_ips": ["*"],
                "mfa_secret": None
            }
        ]
        
        for user_data in users:
            user = User(**user_data)
            self.users[user.user_id] = user
        
        self.logger.info(f"Initialized {len(users)} sample users")
    
    def _initialize_security_events(self):
        """Initialize with sample security events"""
        events = [
            {
                "event_id": "sec_001",
                "event_type": "login_success",
                "user_id": "admin_001",
                "ip_address": "192.168.1.100",
                "timestamp": datetime.now() - timedelta(hours=2),
                "description": "Successful login from admin account",
                "severity": "low",
                "resolved": True,
                "resolution_notes": None
            },
            {
                "event_id": "sec_002",
                "event_type": "failed_login",
                "user_id": None,
                "ip_address": "192.168.1.200",
                "timestamp": datetime.now() - timedelta(hours=3),
                "description": "Failed login attempt - invalid credentials",
                "severity": "medium",
                "resolved": True,
                "resolution_notes": "IP monitored for suspicious activity"
            },
            {
                "event_id": "sec_003",
                "event_type": "password_change",
                "user_id": "mgr_001",
                "ip_address": "192.168.1.150",
                "timestamp": datetime.now() - timedelta(hours=6),
                "description": "Password changed successfully",
                "severity": "low",
                "resolved": True,
                "resolution_notes": None
            },
            {
                "event_id": "sec_004",
                "event_type": "mfa_enabled",
                "user_id": "exec_001",
                "ip_address": "192.168.1.101",
                "timestamp": datetime.now() - timedelta(days=1),
                "description": "Multi-factor authentication enabled",
                "severity": "low",
                "resolved": True,
                "resolution_notes": None
            }
        ]
        
        for event_data in events:
            event = SecurityEvent(**event_data)
            self.security_events.append(event)
        
        self.logger.info(f"Initialized {len(events)} security events")
    
    def authenticate_user(self, username: str, password: str, ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Authenticate user and create session"""
        try:
            # Check for account lockout
            if self._is_account_locked(username, ip_address):
                self._log_security_event("account_locked", None, ip_address, "Account locked due to failed attempts")
                return {"success": False, "error": "Account locked. Please try again later."}
            
            # Find user
            user = None
            for u in self.users.values():
                if u.username == username:
                    user = u
                    break
            
            if not user:
                self._record_failed_attempt(username, ip_address)
                self._log_security_event("failed_login", None, ip_address, f"Failed login attempt for unknown user: {username}")
                return {"success": False, "error": "Invalid credentials"}
            
            if not user.is_active:
                self._log_security_event("failed_login", user.user_id, ip_address, "Login attempt on inactive account")
                return {"success": False, "error": "Account is inactive"}
            
            # Verify password (simplified for demo)
            if not self._verify_password(password, user):
                self._record_failed_attempt(username, ip_address)
                self._log_security_event("failed_login", user.user_id, ip_address, "Failed login attempt - invalid password")
                return {"success": False, "error": "Invalid credentials"}
            
            # Check IP restrictions
            if not self._is_ip_allowed(ip_address, user):
                self._log_security_event("blocked_ip", user.user_id, ip_address, "Login attempt from blocked IP")
                return {"success": False, "error": "Access denied from this IP address"}
            
            # Create session
            session = self._create_session(user, ip_address, user_agent)
            
            # Update user last login
            user.last_login = datetime.now()
            
            # Clear failed attempts
            self.failed_attempts[username] = []
            
            # Log successful login
            self._log_security_event("login_success", user.user_id, ip_address, "Successful login")
            
            return {
                "success": True,
                "session_id": session.session_id,
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
                "expires_at": session.expires_at.isoformat(),
                "user": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "permissions": [p.value for p in user.permissions]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return {"success": False, "error": "Authentication failed"}
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return user info"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Check if session exists and is active
            session = self.sessions.get(payload.get('session_id'))
            if not session or not session.is_active or session.expires_at < datetime.now():
                return {"valid": False, "error": "Invalid or expired session"}
            
            # Update last activity
            session.last_activity = datetime.now()
            
            return {
                "valid": True,
                "user_id": payload.get('user_id'),
                "role": payload.get('role'),
                "permissions": payload.get('permissions'),
                "session_id": payload.get('session_id')
            }
            
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"valid": False, "error": "Invalid token"}
        except Exception as e:
            self.logger.error(f"Token verification error: {e}")
            return {"valid": False, "error": "Token verification failed"}
    
    def logout_user(self, session_id: str) -> Dict[str, Any]:
        """Logout user and invalidate session"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            # Invalidate session
            session.is_active = False
            
            # Log logout
            self._log_security_event("logout", session.user_id, session.ip_address, "User logged out")
            
            return {"success": True, "message": "Logged out successfully"}
            
        except Exception as e:
            self.logger.error(f"Logout error: {e}")
            return {"success": False, "error": "Logout failed"}
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission"""
        try:
            user = self.users.get(user_id)
            if not user:
                return False
            
            return permission in [p.value for p in user.permissions]
            
        except Exception as e:
            self.logger.error(f"Permission check error: {e}")
            return False
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active sessions for a user"""
        try:
            user_sessions = []
            for session in self.sessions.values():
                if session.user_id == user_id and session.is_active:
                    user_sessions.append({
                        "session_id": session.session_id,
                        "created_at": session.created_at.isoformat(),
                        "expires_at": session.expires_at.isoformat(),
                        "last_activity": session.last_activity.isoformat(),
                        "ip_address": session.ip_address,
                        "user_agent": session.user_agent
                    })
            
            return user_sessions
            
        except Exception as e:
            self.logger.error(f"Get user sessions error: {e}")
            return []
    
    def revoke_session(self, session_id: str) -> Dict[str, Any]:
        """Revoke a specific session"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            session.is_active = False
            
            # Log session revocation
            self._log_security_event("session_revoked", session.user_id, session.ip_address, "Session revoked by administrator")
            
            return {"success": True, "message": "Session revoked successfully"}
            
        except Exception as e:
            self.logger.error(f"Revoke session error: {e}")
            return {"success": False, "error": "Failed to revoke session"}
    
    def get_security_events(self, hours: int = 24, severity: str = None) -> List[Dict[str, Any]]:
        """Get security events filtered by time and severity"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            events = []
            
            for event in self.security_events:
                if event.timestamp >= cutoff_time:
                    if severity is None or event.severity == severity:
                        events.append({
                            "event_id": event.event_id,
                            "event_type": event.event_type,
                            "user_id": event.user_id,
                            "ip_address": event.ip_address,
                            "timestamp": event.timestamp.isoformat(),
                            "description": event.description,
                            "severity": event.severity,
                            "resolved": event.resolved,
                            "resolution_notes": event.resolution_notes
                        })
            
            # Sort by timestamp (newest first)
            events.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return events
            
        except Exception as e:
            self.logger.error(f"Get security events error: {e}")
            return []
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user"""
        try:
            # Validate required fields
            required_fields = ['username', 'email', 'full_name', 'role']
            for field in required_fields:
                if field not in user_data:
                    return {"success": False, "error": f"Missing required field: {field}"}
            
            # Check if username already exists
            for user in self.users.values():
                if user.username == user_data['username']:
                    return {"success": False, "error": "Username already exists"}
            
            # Create user
            user_id = f"user_{int(time.time())}"
            role = UserRole(user_data['role'])
            permissions = self.role_permissions[role].permissions
            
            user = User(
                user_id=user_id,
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                role=role,
                permissions=permissions,
                auth_provider=AuthProvider.LOCAL,
                last_login=None,
                created_at=datetime.now(),
                is_active=True,
                is_verified=False,
                two_factor_enabled=False,
                department=user_data.get('department', 'General'),
                manager_id=user_data.get('manager_id'),
                session_timeout=120,
                allowed_ips=['*'],
                mfa_secret=None
            )
            
            self.users[user_id] = user
            
            # Log user creation
            self._log_security_event("user_created", user_id, "system", f"User created: {user.username}")
            
            return {"success": True, "user_id": user_id, "message": "User created successfully"}
            
        except Exception as e:
            self.logger.error(f"Create user error: {e}")
            return {"success": False, "error": "Failed to create user"}
    
    def _verify_password(self, password: str, user: User) -> bool:
        """Verify password (simplified for demo)"""
        # In production, use bcrypt or similar
        return password == "password123"  # Simplified for demo
    
    def _create_session(self, user: User, ip_address: str, user_agent: str) -> Session:
        """Create new session for user"""
        session_id = hashlib.sha256(f"{user.user_id}_{time.time()}".encode()).hexdigest()
        
        # Create JWT tokens
        access_payload = {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role.value,
            'permissions': [p.value for p in user.permissions],
            'session_id': session_id,
            'exp': datetime.now() + timedelta(seconds=self.jwt_expiry)
        }
        
        refresh_payload = {
            'user_id': user.user_id,
            'session_id': session_id,
            'exp': datetime.now() + timedelta(seconds=self.refresh_expiry)
        }
        
        access_token = jwt.encode(access_payload, self.jwt_secret, algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, self.jwt_secret, algorithm='HS256')
        
        session = Session(
            session_id=session_id,
            user_id=user.user_id,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=user.session_timeout * 60),
            last_activity=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True,
            permissions=user.permissions,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        self.sessions[session_id] = session
        return session
    
    def _is_account_locked(self, username: str, ip_address: str) -> bool:
        """Check if account is locked due to failed attempts"""
        failed_attempts = self.failed_attempts.get(username, [])
        recent_attempts = [attempt for attempt in failed_attempts 
                          if datetime.now() - attempt < timedelta(seconds=self.lockout_duration)]
        
        return len(recent_attempts) >= self.max_failed_attempts
    
    def _record_failed_attempt(self, username: str, ip_address: str):
        """Record failed login attempt"""
        self.failed_attempts[username].append(datetime.now())
    
    def _is_ip_allowed(self, ip_address: str, user: User) -> bool:
        """Check if IP address is allowed for user"""
        if "*" in user.allowed_ips:
            return True
        
        for allowed_ip in user.allowed_ips:
            if allowed_ip.endswith("*"):
                if ip_address.startswith(allowed_ip[:-1]):
                    return True
            elif ip_address == allowed_ip:
                return True
        
        return False
    
    def _log_security_event(self, event_type: str, user_id: Optional[str], ip_address: str, description: str):
        """Log security event"""
        event = SecurityEvent(
            event_id=f"sec_{int(time.time())}",
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            timestamp=datetime.now(),
            description=description,
            severity="medium",  # Default severity
            resolved=False,
            resolution_notes=None
        )
        
        self.security_events.append(event)
        self.logger.info(f"Security event: {event_type} - {description}")

# Global authentication system instance
authentication_system = AuthenticationSystem()
