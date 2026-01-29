"""
Helm AI Authentication System
Complete authentication and authorization system for enterprise SaaS platform
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import secrets
import re
import hashlib
import uuid
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, validator
import asyncio
from database import get_db, User
from sqlalchemy.orm import Session

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Login Manager
manager = LoginManager(SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)

# Pydantic Models
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserProfile(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

# Utility Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_password_reset_token(email: str) -> str:
    """Generate password reset token"""
    timestamp = str(int(datetime.now(timezone.utc).timestamp()))
    token_data = f"{email}:{timestamp}"
    token = hashlib.sha256(token_data.encode()).hexdigest()
    return token

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "access":
            raise credentials_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

async def get_current_superuser(current_user: User = Depends(get_current_user)):
    """Get current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Authentication Routes
def setup_auth_routes(app: FastAPI):
    """Setup authentication routes"""
    
    @app.post("/auth/register", response_model=Token)
    async def register(user_data: UserRegister, db: Session = Depends(get_db)):
        """Register a new user"""
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        
        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            phone=user_data.phone,
            company=user_data.company,
            is_active=False,  # Require email verification
            is_superuser=False,
            verification_token=verification_token,
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # TODO: Send verification email
        
        # Create tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user.username}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": new_user.username})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    @app.post("/auth/login", response_model=Token)
    async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
        """Login user"""
        
        # Authenticate user
        user = db.query(User).filter(User.username == form_data.username).first()
        
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account not verified"
            )
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        
        # Create tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": user.username})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    @app.post("/auth/refresh", response_model=Token)
    async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
        """Refresh access token"""
        
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            token_type: str = payload.get("type")
            
            if username is None or token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            user = db.query(User).filter(User.username == username).first()
            if user is None or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user"
                )
            
            # Create new access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.username}, expires_delta=access_token_expires
            )
            new_refresh_token = create_refresh_token(data={"sub": user.username})
            
            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    @app.post("/auth/logout")
    async def logout(current_user: User = Depends(get_current_active_user)):
        """Logout user"""
        # TODO: Implement token blacklisting
        return {"message": "Successfully logged out"}
    
    @app.post("/auth/verify-email/{token}")
    async def verify_email(token: str, db: Session = Depends(get_db)):
        """Verify email address"""
        
        user = db.query(User).filter(User.verification_token == token).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid verification token"
            )
        
        user.is_active = True
        user.verification_token = None
        user.email_verified_at = datetime.now(timezone.utc)
        db.commit()
        
        return {"message": "Email verified successfully"}
    
    @app.post("/auth/forgot-password")
    async def forgot_password(password_reset: PasswordReset, db: Session = Depends(get_db)):
        """Request password reset"""
        
        user = db.query(User).filter(User.email == password_reset.email).first()
        if not user:
            # Don't reveal if email exists
            return {"message": "Password reset email sent"}
        
        # Generate reset token
        reset_token = generate_password_reset_token(user.email)
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.commit()
        
        # TODO: Send password reset email
        
        return {"message": "Password reset email sent"}
    
    @app.post("/auth/reset-password/{token}")
    async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
        """Reset password"""
        
        user = db.query(User).filter(User.password_reset_token == token).first()
        if not user or user.password_reset_expires < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Validate new password
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        user.hashed_password = get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        db.commit()
        
        return {"message": "Password reset successfully"}
    
    @app.post("/auth/change-password")
    async def change_password(
        password_change: PasswordChange,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Change password"""
        
        if not verify_password(password_change.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        current_user.hashed_password = get_password_hash(password_change.new_password)
        db.commit()
        
        return {"message": "Password changed successfully"}
    
    @app.get("/auth/me")
    async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
        """Get current user information"""
        return {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "phone": current_user.phone,
            "company": current_user.company,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "is_superuser": current_user.is_superuser,
            "created_at": current_user.created_at,
            "last_login": current_user.last_login,
            "email_verified_at": current_user.email_verified_at
        }
    
    @app.put("/auth/profile")
    async def update_profile(
        profile_data: UserProfile,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Update user profile"""
        
        if profile_data.full_name is not None:
            current_user.full_name = profile_data.full_name
        if profile_data.phone is not None:
            current_user.phone = profile_data.phone
        if profile_data.company is not None:
            current_user.company = profile_data.company
        if profile_data.bio is not None:
            current_user.bio = profile_data.bio
        if profile_data.avatar_url is not None:
            current_user.avatar_url = profile_data.avatar_url
        if profile_data.preferences is not None:
            current_user.preferences = profile_data.preferences
        
        current_user.updated_at = datetime.now(timezone.utc)
        db.commit()
        
        return {"message": "Profile updated successfully"}

# Rate Limiting
class RateLimiter:
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed"""
        now = datetime.now(timezone.utc)
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < timedelta(seconds=window)
        ]
        
        if len(self.requests[key]) >= limit:
            return False
        
        self.requests[key].append(now)
        return True

rate_limiter = RateLimiter()

# Rate limiting middleware
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    
    # Get client IP
    client_ip = request.client.host
    
    # Check rate limit (100 requests per minute)
    if not rate_limiter.is_allowed(client_ip, 100, 60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    response = await call_next(request)
    return response

# Export functions
__all__ = [
    "setup_auth_routes",
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "rate_limit_middleware",
    "UserRegister",
    "UserLogin",
    "Token",
    "PasswordReset",
    "PasswordChange",
    "UserProfile"
]
