"""
Helm AI Role-Based Access Control (RBAC)
This module provides comprehensive RBAC functionality for enterprise users
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

class Permission(Enum):
    """System permissions"""
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    ROLE_CREATE = "role:create"
    ROLE_READ = "role:read"
    ROLE_UPDATE = "role:update"
    MODEL_CREATE = "model:create"
    MODEL_READ = "model:read"
    GAME_CREATE = "game:create"
    GAME_READ = "game:read"
    ANALYTICS_VIEW = "analytics:view"
    SUPPORT_CREATE = "support:create"
    SYSTEM_CONFIGURE = "system:configure"
    API_ACCESS = "api:access"

@dataclass
class Role:
    """Role definition"""
    name: str
    description: str
    permissions: Set[Permission] = field(default_factory=set)
    is_system_role: bool = False
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class User:
    """User with RBAC information"""
    user_id: str
    email: str
    name: str
    roles: Set[str] = field(default_factory=set)
    permissions: Set[Permission] = field(default_factory=set)
    is_active: bool = True
    is_superuser: bool = False

class RoleManager:
    """Role-Based Access Control Manager"""
    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}
        self._initialize_system_roles()
    
    def _initialize_system_roles(self):
        """Initialize system default roles"""
        # Super Admin
        super_admin = Role(
            name="super_admin",
            description="Full system access",
            permissions=set(Permission),
            is_system_role=True
        )
        self.roles["super_admin"] = super_admin
        
        # Admin
        admin_permissions = {
            Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
            Permission.ROLE_READ, Permission.MODEL_READ, Permission.GAME_READ,
            Permission.ANALYTICS_VIEW, Permission.SUPPORT_CREATE, Permission.SYSTEM_CONFIGURE,
            Permission.API_ACCESS
        }
        admin_role = Role(
            name="admin",
            description="Administrative access",
            permissions=admin_permissions,
            is_system_role=True
        )
        self.roles["admin"] = admin_role
        
        # Developer
        developer_permissions = {
            Permission.USER_READ, Permission.MODEL_CREATE, Permission.MODEL_READ,
            Permission.GAME_CREATE, Permission.GAME_READ, Permission.ANALYTICS_VIEW,
            Permission.API_ACCESS
        }
        developer_role = Role(
            name="developer",
            description="Developer access",
            permissions=developer_permissions,
            is_system_role=True
        )
        self.roles["developer"] = developer_role
    
    def create_role(self, name: str, description: str, permissions: Set[Permission]) -> Role:
        """Create new role"""
        if name in self.roles:
            raise ValueError(f"Role {name} already exists")
        
        role = Role(
            name=name,
            description=description,
            permissions=permissions
        )
        self.roles[name] = role
        return role
    
    def get_role(self, name: str) -> Optional[Role]:
        """Get role by name"""
        return self.roles.get(name)
    
    def update_role(self, name: str, description: str = None, permissions: Set[Permission] = None) -> Role:
        """Update existing role"""
        role = self.get_role(name)
        if not role:
            raise ValueError(f"Role {name} not found")
        
        if role.is_system_role:
            raise ValueError("Cannot modify system roles")
        
        if description:
            role.description = description
        if permissions:
            role.permissions = permissions
        
        role.updated_at = datetime.now()
        return role
    
    def delete_role(self, name: str) -> bool:
        """Delete role"""
        role = self.get_role(name)
        if not role:
            return False
        
        if role.is_system_role:
            raise ValueError("Cannot delete system roles")
        
        # Remove role from all users
        for user in self.users.values():
            user.roles.discard(name)
        
        del self.roles[name]
        return True
    
    def create_user(self, user_id: str, email: str, name: str, roles: List[str] = None) -> User:
        """Create new user"""
        if user_id in self.users:
            raise ValueError(f"User {user_id} already exists")
        
        user = User(
            user_id=user_id,
            email=email,
            name=name,
            roles=set(roles or [])
        )
        
        # Calculate user permissions from roles
        self._update_user_permissions(user)
        self.users[user_id] = user
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def update_user(self, user_id: str, email: str = None, name: str = None, roles: List[str] = None) -> User:
        """Update user"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        if email:
            user.email = email
        if name:
            user.name = name
        if roles is not None:
            user.roles = set(roles)
            self._update_user_permissions(user)
        
        user.updated_at = datetime.now()
        return user
    
    def assign_role(self, user_id: str, role_name: str) -> bool:
        """Assign role to user"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        role = self.get_role(role_name)
        if not role:
            return False
        
        user.roles.add(role_name)
        self._update_user_permissions(user)
        return True
    
    def remove_role(self, user_id: str, role_name: str) -> bool:
        """Remove role from user"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        user.roles.discard(role_name)
        self._update_user_permissions(user)
        return True
    
    def _update_user_permissions(self, user: User):
        """Update user permissions based on roles"""
        user.permissions = set()
        
        for role_name in user.roles:
            role = self.get_role(role_name)
            if role:
                user.permissions.update(role.permissions)
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        user = self.get_user(user_id)
        if not user or not user.is_active:
            return False
        
        if user.is_superuser:
            return True
        
        return permission in user.permissions
    
    def has_any_permission(self, user_id: str, permissions: List[Permission]) -> bool:
        """Check if user has any of the specified permissions"""
        return any(self.has_permission(user_id, perm) for perm in permissions)
    
    def has_all_permissions(self, user_id: str, permissions: List[Permission]) -> bool:
        """Check if user has all specified permissions"""
        return all(self.has_permission(user_id, perm) for perm in permissions)
    
    def get_users_with_permission(self, permission: Permission) -> List[User]:
        """Get all users with specific permission"""
        return [user for user in self.users.values() if self.has_permission(user.user_id, permission)]
    
    def get_all_roles(self) -> List[Role]:
        """Get all roles"""
        return list(self.roles.values())
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        return list(self.users.values())
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for user"""
        user = self.get_user(user_id)
        return user.permissions if user else set()
    
    def export_roles(self) -> Dict[str, Any]:
        """Export roles configuration"""
        return {
            "roles": {
                name: {
                    "description": role.description,
                    "permissions": [perm.value for perm in role.permissions],
                    "is_system_role": role.is_system_role
                }
                for name, role in self.roles.items()
            }
        }
    
    def import_roles(self, roles_data: Dict[str, Any]):
        """Import roles configuration"""
        for role_name, role_info in roles_data.get("roles", {}).items():
            if not self.get_role(role_name):
                permissions = {Permission(perm) for perm in role_info.get("permissions", [])}
                self.create_role(
                    name=role_name,
                    description=role_info.get("description", ""),
                    permissions=permissions
                )
