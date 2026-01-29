"""
Helm AI Authentication Manager
This module provides unified authentication and authorization for enterprise SSO and RBAC
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import jwt
import hashlib
import secrets
from dataclasses import dataclass

from .sso.oauth2_provider import SSOManager
from .rbac.role_manager import RoleManager, Permission, User

logger = logging.getLogger(__name__)

@dataclass
class AuthToken:
    """Authentication token data"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    scope: str = "api"
    user_id: str = None
    created_at: datetime = None

@dataclass
class AuthSession:
    """Authentication session data"""
    session_id: str
    user_id: str
    provider: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    created_at: datetime
    last_activity: datetime
    ip_address: str = None
    user_agent: str = None

class AuthManager:
    """Unified authentication and authorization manager"""
    
    def __init__(self):
        self.sso_manager = SSOManager()
        self.role_manager = RoleManager()
        self.sessions: Dict[str, AuthSession] = {}
        self.jwt_secret = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
        self.jwt_algorithm = 'HS256'
        self.token_expiry = int(os.getenv('TOKEN_EXPIRY_HOURS', '24')) * 3600
        self.refresh_token_expiry = int(os.getenv('REFRESH_TOKEN_EXPIRY_DAYS', '30')) * 24 * 3600
    
    def get_sso_providers(self) -> List[str]:
        """Get available SSO providers"""
        return self.sso_manager.get_available_providers()
    
    def get_sso_authorization_url(self, provider: str, redirect_uri: str = None) -> Dict[str, Any]:
        """Get SSO authorization URL"""
        sso_provider = self.sso_manager.get_provider(provider)
        if not sso_provider:
            raise ValueError(f"SSO provider {provider} not available")
        
        state = secrets.token_urlsafe(32)
        auth_url = sso_provider.get_authorization_url(state=state)
        
        return {
            "authorization_url": auth_url,
            "state": state,
            "provider": provider
        }
    
    def authenticate_with_sso(self, 
                            provider: str, 
                            code: str, 
                            state: str = None,
                            ip_address: str = None,
                            user_agent: str = None) -> Dict[str, Any]:
        """Authenticate user using SSO"""
        try:
            # Authenticate with SSO provider
            auth_result = self.sso_manager.authenticate_user(provider, code, state)
            user_info = auth_result['user_info']
            token_data = auth_result['token_data']
            
            # Create or update user
            user_id = self._get_or_create_user(provider, user_info)
            
            # Create auth session
            session_id = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(seconds=self.token_expiry)
            
            session = AuthSession(
                session_id=session_id,
                user_id=user_id,
                provider=provider,
                access_token=token_data.get('access_token'),
                refresh_token=token_data.get('refresh_token'),
                expires_at=expires_at,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.sessions[session_id] = session
            
            # Generate JWT tokens
            jwt_token = self._generate_jwt_token(user_id, provider)
            refresh_token = self._generate_refresh_token(user_id, session_id)
            
            return {
                "user_id": user_id,
                "access_token": jwt_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": self.token_expiry,
                "provider": provider,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"SSO authentication failed: {e}")
            raise
    
    def _get_or_create_user(self, provider: str, user_info: Dict[str, Any]) -> str:
        """Get or create user from SSO info"""
        email = user_info.get('email')
        name = user_info.get('name', email)
        
        # Generate user ID from provider and email
        user_id = f"{provider}:{hashlib.sha256(email.encode()).hexdigest()[:16]}"
        
        # Check if user exists
        user = self.role_manager.get_user(user_id)
        if not user:
            # Create new user with default role
            default_roles = ['user']  # Would need to create this role
            user = self.role_manager.create_user(
                user_id=user_id,
                email=email,
                name=name,
                roles=default_roles
            )
        
        return user_id
    
    def _generate_jwt_token(self, user_id: str, provider: str) -> str:
        """Generate JWT access token"""
        payload = {
            'user_id': user_id,
            'provider': provider,
            'exp': datetime.now() + timedelta(seconds=self.token_expiry),
            'iat': datetime.now(),
            'type': 'access'
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _generate_refresh_token(self, user_id: str, session_id: str) -> str:
        """Generate refresh token"""
        payload = {
            'user_id': user_id,
            'session_id': session_id,
            'exp': datetime.now() + timedelta(seconds=self.refresh_token_expiry),
            'iat': datetime.now(),
            'type': 'refresh'
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            if payload.get('type') != 'access':
                return None
            
            # Check if user is active
            user = self.role_manager.get_user(payload['user_id'])
            if not user or not user.is_active:
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(refresh_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            if payload.get('type') != 'refresh':
                return None
            
            user_id = payload['user_id']
            session_id = payload['session_id']
            
            # Check if session exists and is valid
            session = self.sessions.get(session_id)
            if not session or session.user_id != user_id:
                return None
            
            # Check if user is active
            user = self.role_manager.get_user(user_id)
            if not user or not user.is_active:
                return None
            
            # Generate new access token
            new_access_token = self._generate_jwt_token(user_id, session.provider)
            
            return {
                "access_token": new_access_token,
                "token_type": "Bearer",
                "expires_in": self.token_expiry
            }
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid refresh token: {e}")
            return None
    
    def logout(self, token: str) -> bool:
        """Logout user and invalidate session"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id = payload['user_id']
            
            # Remove all sessions for user
            sessions_to_remove = [
                session_id for session_id, session in self.sessions.items()
                if session.user_id == user_id
            ]
            
            for session_id in sessions_to_remove:
                del self.sessions[session_id]
            
            return True
            
        except jwt.InvalidTokenError:
            return False
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions"""
        permissions = self.role_manager.get_user_permissions(user_id)
        return [perm.value for perm in permissions]
    
    def check_permission(self, user_id: str, permission: Union[str, Permission]) -> bool:
        """Check if user has specific permission"""
        if isinstance(permission, str):
            try:
                permission = Permission(permission)
            except ValueError:
                return False
        
        return self.role_manager.has_permission(user_id, permission)
    
    def check_permissions(self, user_id: str, permissions: List[Union[str, Permission]], require_all: bool = False) -> bool:
        """Check if user has permissions"""
        if require_all:
            return all(self.check_permission(user_id, perm) for perm in permissions)
        else:
            return any(self.check_permission(user_id, perm) for perm in permissions)
    
    def assign_role(self, user_id: str, role_name: str) -> bool:
        """Assign role to user"""
        return self.role_manager.assign_role(user_id, role_name)
    
    def remove_role(self, user_id: str, role_name: str) -> bool:
        """Remove role from user"""
        return self.role_manager.remove_role(user_id, role_name)
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information"""
        user = self.role_manager.get_user(user_id)
        if not user:
            return None
        
        return {
            "user_id": user.user_id,
            "email": user.email,
            "name": user.name,
            "roles": list(user.roles),
            "permissions": [perm.value for perm in user.permissions],
            "is_active": user.is_active,
            "is_superuser": user.is_superuser
        }
    
    def create_role(self, name: str, description: str, permissions: List[str]) -> Dict[str, Any]:
        """Create new role"""
        perm_set = {Permission(perm) for perm in permissions}
        role = self.role_manager.create_role(name, description, perm_set)
        
        return {
            "name": role.name,
            "description": role.description,
            "permissions": [perm.value for perm in role.permissions],
            "is_system_role": role.is_system_role
        }
    
    def get_all_roles(self) -> List[Dict[str, Any]]:
        """Get all roles"""
        roles = self.role_manager.get_all_roles()
        return [
            {
                "name": role.name,
                "description": role.description,
                "permissions": [perm.value for perm in role.permissions],
                "is_system_role": role.is_system_role
            }
            for role in roles
        ]
    
    def get_active_sessions(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get active sessions"""
        sessions = self.sessions.values()
        
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        
        return [
            {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "provider": session.provider,
                "expires_at": session.expires_at.isoformat(),
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "ip_address": session.ip_address
            }
            for session in sessions
        ]
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.now()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.expires_at < current_time
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_audit_log(self, user_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get authentication audit log"""
        # This would integrate with a proper audit logging system
        # For now, return basic session information
        sessions = self.get_active_sessions(user_id)
        
        return {
            "period": f"Last {days} days",
            "total_sessions": len(sessions),
            "active_sessions": sessions,
            "user_id": user_id
        }


# Singleton instance for easy access
auth_manager = AuthManager()
