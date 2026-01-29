"""
Helm AI User Management System
Complete user management with roles, permissions, and administrative functions
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime, timezone
import uuid
from enum import Enum

from database import get_db, User
from auth import get_current_active_user, get_current_superuser
from auth import UserProfile as AuthUserProfile

# Enums
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    SUPPORT = "support"
    SALES = "sales"
    DEVELOPER = "developer"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    role: UserRole = UserRole.USER
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    role: UserRole
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    email_verified_at: Optional[datetime]
    avatar_url: Optional[str]
    bio: Optional[str]
    
    class Config:
        from_attributes = True

class UserList(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class Permission(BaseModel):
    name: str
    description: str
    resource: str
    action: str

class Role(BaseModel):
    name: UserRole
    permissions: List[Permission]
    description: str

# Permission System
PERMISSIONS = {
    UserRole.USER: [
        Permission(name="read_profile", description="Read own profile", resource="profile", action="read"),
        Permission(name="update_profile", description="Update own profile", resource="profile", action="update"),
        Permission(name="read_own_data", description="Read own data", resource="data", action="read"),
    ],
    UserRole.SUPPORT: [
        Permission(name="read_users", description="Read user information", resource="users", action="read"),
        Permission(name="update_users", description="Update user information", resource="users", action="update"),
        Permission(name="read_tickets", description="Read support tickets", resource="tickets", action="read"),
        Permission(name="update_tickets", description="Update support tickets", resource="tickets", action="update"),
    ],
    UserRole.SALES: [
        Permission(name="read_customers", description="Read customer information", resource="customers", action="read"),
        Permission(name="create_customers", description="Create customer accounts", resource="customers", action="create"),
        Permission(name="update_customers", description="Update customer information", resource="customers", action="update"),
        Permission(name="read_analytics", description="Read sales analytics", resource="analytics", action="read"),
    ],
    UserRole.DEVELOPER: [
        Permission(name="read_system", description="Read system information", resource="system", action="read"),
        Permission(name="update_system", description="Update system configuration", resource="system", action="update"),
        Permission(name="read_logs", description="Read system logs", resource="logs", action="read"),
        Permission(name="deploy_code", description="Deploy code changes", resource="deployment", action="create"),
    ],
    UserRole.ADMIN: [
        Permission(name="read_all", description="Read all resources", resource="all", action="read"),
        Permission(name="update_all", description="Update all resources", resource="all", action="update"),
        Permission(name="create_all", description="Create all resources", resource="all", action="create"),
        Permission(name="delete_all", description="Delete all resources", resource="all", action="delete"),
    ],
    UserRole.SUPER_ADMIN: [
        Permission(name="god_mode", description="Full system access", resource="all", action="all"),
    ]
}

# Permission Checking Functions
def has_permission(user: User, resource: str, action: str) -> bool:
    """Check if user has permission for resource/action"""
    
    if user.is_superuser:
        return True
    
    user_permissions = PERMISSIONS.get(user.role, [])
    
    for permission in user_permissions:
        if permission.resource == resource and permission.action == action:
            return True
        if permission.resource == "all" and permission.action == action:
            return True
        if permission.resource == resource and permission.action == "all":
            return True
        if permission.resource == "all" and permission.action == "all":
            return True
    
    return False

def check_permission(resource: str, action: str):
    """Decorator to check permissions"""
    def permission_checker(current_user: User = Depends(get_current_active_user)):
        if not has_permission(current_user, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for {action} on {resource}"
            )
        return current_user
    return permission_checker

# User Management Functions
def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user"""
    from auth import get_password_hash
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        if existing_user.username == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        company=user_data.company,
        role=user_data.role,
        is_active=True,
        is_superuser=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    company: Optional[str] = None
) -> List[User]:
    """Get users with filters"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
                User.company.ilike(f"%{search}%")
            )
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if status:
        if status == UserStatus.ACTIVE:
            query = query.filter(User.is_active == True)
        elif status == UserStatus.INACTIVE:
            query = query.filter(User.is_active == False)
        elif status == UserStatus.SUSPENDED:
            query = query.filter(User.is_active == False, User.suspended_at.isnot(None))
        elif status == UserStatus.PENDING:
            query = query.filter(User.email_verified_at.is_(None))
    
    if company:
        query = query.filter(User.company.ilike(f"%{company}%"))
    
    return query.offset(skip).limit(limit).all()

def count_users(
    db: Session,
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    company: Optional[str] = None
) -> int:
    """Count users with filters"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
                User.company.ilike(f"%{search}%")
            )
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if status:
        if status == UserStatus.ACTIVE:
            query = query.filter(User.is_active == True)
        elif status == UserStatus.INACTIVE:
            query = query.filter(User.is_active == False)
        elif status == UserStatus.SUSPENDED:
            query = query.filter(User.is_active == False, User.suspended_at.isnot(None))
        elif status == UserStatus.PENDING:
            query = query.filter(User.email_verified_at.is_(None))
    
    if company:
        query = query.filter(User.company.ilike(f"%{company}%"))
    
    return query.count()

def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """Update user"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    # Update fields
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.phone is not None:
        user.phone = user_data.phone
    if user_data.company is not None:
        user.company = user_data.company
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.bio is not None:
        user.bio = user_data.bio
    if user_data.avatar_url is not None:
        user.avatar_url = user_data.avatar_url
    if user_data.preferences is not None:
        user.preferences = user_data.preferences
    
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    
    return user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete user"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    return True

def suspend_user(db: Session, user_id: int, reason: str = "") -> Optional[User]:
    """Suspend user"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    user.is_active = False
    user.suspended_at = datetime.now(timezone.utc)
    user.suspension_reason = reason
    user.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(user)
    
    return user

def unsuspend_user(db: Session, user_id: int) -> Optional[User]:
    """Unsuspend user"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    user.is_active = True
    user.suspended_at = None
    user.suspension_reason = None
    user.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(user)
    
    return user

# API Routes
def setup_user_management_routes(app: FastAPI):
    """Setup user management routes"""
    
    @app.get("/users", response_model=UserList)
    async def get_users_list(
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100),
        search: Optional[str] = Query(None),
        role: Optional[UserRole] = Query(None),
        status: Optional[UserStatus] = Query(None),
        company: Optional[str] = Query(None),
        current_user: User = Depends(check_permission("users", "read")),
        db: Session = Depends(get_db)
    ):
        """Get users list (admin only)"""
        
        skip = (page - 1) * per_page
        users = get_users(db, skip=skip, limit=per_page, search=search, role=role, status=status, company=company)
        total = count_users(db, search=search, role=role, status=status, company=company)
        total_pages = (total + per_page - 1) // per_page
        
        return UserList(
            users=[UserResponse.from_orm(user) for user in users],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    
    @app.get("/users/{user_id}", response_model=UserResponse)
    async def get_user(
        user_id: int,
        current_user: User = Depends(check_permission("users", "read")),
        db: Session = Depends(get_db)
    ):
        """Get user by ID"""
        
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.from_orm(user)
    
    @app.post("/users", response_model=UserResponse)
    async def create_new_user(
        user_data: UserCreate,
        current_user: User = Depends(check_permission("users", "create")),
        db: Session = Depends(get_db)
    ):
        """Create new user (admin only)"""
        
        user = create_user(db, user_data)
        return UserResponse.from_orm(user)
    
    @app.put("/users/{user_id}", response_model=UserResponse)
    async def update_user_info(
        user_id: int,
        user_data: UserUpdate,
        current_user: User = Depends(check_permission("users", "update")),
        db: Session = Depends(get_db)
    ):
        """Update user (admin only)"""
        
        user = update_user(db, user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.from_orm(user)
    
    @app.delete("/users/{user_id}")
    async def delete_user_account(
        user_id: int,
        current_user: User = Depends(check_permission("users", "delete")),
        db: Session = Depends(get_db)
    ):
        """Delete user (admin only)"""
        
        if not delete_user(db, user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "User deleted successfully"}
    
    @app.post("/users/{user_id}/suspend")
    async def suspend_user_account(
        user_id: int,
        reason: str = "",
        current_user: User = Depends(check_permission("users", "update")),
        db: Session = Depends(get_db)
    ):
        """Suspend user (admin only)"""
        
        user = suspend_user(db, user_id, reason)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "User suspended successfully"}
    
    @app.post("/users/{user_id}/unsuspend")
    async def unsuspend_user_account(
        user_id: int,
        current_user: User = Depends(check_permission("users", "update")),
        db: Session = Depends(get_db)
    ):
        """Unsuspend user (admin only)"""
        
        user = unsuspend_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "User unsuspended successfully"}
    
    @app.get("/roles", response_model=List[Role])
    async def get_roles(
        current_user: User = Depends(get_current_active_user)
    ):
        """Get all available roles"""
        
        roles = []
        for role_name, permissions in PERMISSIONS.items():
            roles.append(Role(
                name=role_name,
                permissions=permissions,
                description=f"Role: {role_name}"
            ))
        
        return roles
    
    @app.get("/users/{user_id}/permissions", response_model=List[Permission])
    async def get_user_permissions(
        user_id: int,
        current_user: User = Depends(check_permission("users", "read")),
        db: Session = Depends(get_db)
    ):
        """Get user permissions"""
        
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return PERMISSIONS.get(user.role, [])
    
    @app.get("/users/me", response_model=UserResponse)
    async def get_current_user_info(
        current_user: User = Depends(get_current_active_user)
    ):
        """Get current user information"""
        
        return UserResponse.from_orm(current_user)
    
    @app.put("/users/me", response_model=UserResponse)
    async def update_current_user_info(
        user_data: UserUpdate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Update current user information"""
        
        # Users can only update certain fields
        allowed_updates = UserUpdate(
            full_name=user_data.full_name,
            phone=user_data.phone,
            company=user_data.company,
            bio=user_data.bio,
            avatar_url=user_data.avatar_url,
            preferences=user_data.preferences
        )
        
        user = update_user(db, current_user.id, allowed_updates)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.from_orm(user)

# Export functions
__all__ = [
    "setup_user_management_routes",
    "create_user",
    "get_user_by_id",
    "get_user_by_username",
    "get_user_by_email",
    "get_users",
    "count_users",
    "update_user",
    "delete_user",
    "suspend_user",
    "unsuspend_user",
    "has_permission",
    "check_permission",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserList",
    "UserRole",
    "UserStatus",
    "PERMISSIONS"
]
