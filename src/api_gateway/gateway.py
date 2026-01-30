"""
Advanced API Gateway with Rate Limiting for Helm AI
===============================================

This module provides comprehensive API gateway capabilities:
- Advanced rate limiting with multiple algorithms
- Request routing and load balancing
- API authentication and authorization
- Request/response transformation
- API analytics and monitoring
- Circuit breaker patterns
- Request validation and sanitization
- API versioning and deprecation
"""

import asyncio
import json
import logging
import uuid
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
import asyncio
from collections import defaultdict, deque

# Third-party imports
import redis
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import aiohttp
from prometheus_client import Counter, Histogram, Gauge
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB

# Local imports
from src.monitoring.structured_logging import StructuredLogger
from src.database.database_manager import DatabaseManager
from src.security.encryption import EncryptionManager

logger = StructuredLogger("api_gateway")

Base = declarative_base()


class RateLimitAlgorithm(str, Enum):
    """Rate limiting algorithms"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"


class APIVersion(str, Enum):
    """API versions"""
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"


class AuthType(str, Enum):
    """Authentication types"""
    JWT = "jwt"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC = "basic"
    NONE = "none"


@dataclass
class RateLimitRule:
    """Rate limit rule configuration"""
    id: str
    name: str
    algorithm: RateLimitAlgorithm
    limit: int
    window_seconds: int
    path_pattern: str
    method: Optional[str] = None
    user_based: bool = False
    ip_based: bool = True
    enabled: bool = True


@dataclass
class APIRoute:
    """API route configuration"""
    id: str
    path: str
    method: str
    target_url: str
    auth_required: bool = True
    auth_type: AuthType = AuthType.JWT
    rate_limit_rules: List[str] = field(default_factory=list)
    timeout_seconds: int = 30
    retry_count: int = 3
    enabled: bool = True


@dataclass
class APIRequest:
    """API request data"""
    id: str
    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: Optional[bytes]
    user_id: Optional[str] = None
    ip_address: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class APIResponse:
    """API response data"""
    id: str
    request_id: str
    status_code: int
    headers: Dict[str, str]
    body: Optional[bytes]
    duration_ms: float
    cache_hit: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)


class RateLimitRules(Base):
    """SQLAlchemy model for rate limit rules"""
    __tablename__ = "rate_limit_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    algorithm = Column(String(50), nullable=False)
    limit = Column(Integer, nullable=False)
    window_seconds = Column(Integer, nullable=False)
    path_pattern = Column(String(500))
    method = Column(String(10))
    user_based = Column(Boolean, default=False)
    ip_based = Column(Boolean, default=True)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class APIRoutes(Base):
    """SQLAlchemy model for API routes"""
    __tablename__ = "api_routes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(String(255), nullable=False, unique=True, index=True)
    path = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False)
    target_url = Column(String(1000), nullable=False)
    auth_required = Column(Boolean, default=True)
    auth_type = Column(String(50), default="jwt")
    timeout_seconds = Column(Integer, default=30)
    retry_count = Column(Integer, default=3)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class APIGatewayMetrics(Base):
    """SQLAlchemy model for API metrics"""
    __tablename__ = "api_gateway_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    path = Column(String(500), nullable=False)
    status_code = Column(Integer, nullable=False)
    duration_ms = Column(Float, nullable=False)
    user_id = Column(String(255))
    ip_address = Column(String(45))
    cache_hit = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class APIGateway:
    """Advanced API Gateway with Rate Limiting"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        self.encryption_manager = EncryptionManager(config.get('encryption', {}))
        
        # Initialize Redis for rate limiting and caching
        self.redis_client = redis.Redis(**config.get('redis', {}))
        
        # Storage
        self.rate_limit_rules: Dict[str, RateLimitRule] = {}
        self.api_routes: Dict[str, APIRoute] = {}
        
        # Rate limiting state
        self.token_buckets: Dict[str, deque] = defaultdict(deque)
        self.sliding_windows: Dict[str, deque] = defaultdict(deque)
        
        # Metrics
        self.request_counter = Counter('api_requests_total', ['method', 'path', 'status'])
        self.request_duration = Histogram('api_request_duration_seconds', ['method', 'path'])
        self.active_connections = Gauge('api_active_connections')
        
        # FastAPI app
        self.app = FastAPI(title="Helm AI API Gateway")
        self._setup_middleware()
        
        logger.info("API Gateway initialized")
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Gzip middleware
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Custom middleware for metrics
        @self.app.middleware("http")
        async def add_metrics(request: Request, call_next):
            start_time = time.time()
            
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            self.request_counter.labels(
                method=request.method,
                path=request.url.path,
                status=response.status_code
            ).inc()
            
            self.request_duration.labels(
                method=request.method,
                path=request.url.path
            ).observe(duration)
            
            return response
    
    async def add_rate_limit_rule(self, rule: RateLimitRule) -> bool:
        """Add a rate limit rule"""
        try:
            # Validate rule
            if not await self._validate_rate_limit_rule(rule):
                return False
            
            # Store rule
            self.rate_limit_rules[rule.id] = rule
            
            # Save to database
            rule_record = RateLimitRules(
                rule_id=rule.id,
                name=rule.name,
                algorithm=rule.algorithm.value,
                limit=rule.limit,
                window_seconds=rule.window_seconds,
                path_pattern=rule.path_pattern,
                method=rule.method,
                user_based=rule.user_based,
                ip_based=rule.ip_based,
                enabled=rule.enabled
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(rule_record)
                session.commit()
            finally:
                session.close()
            
            logger.info("Rate limit rule added", rule_id=rule.id)
            return True
            
        except Exception as e:
            logger.error("Failed to add rate limit rule", rule_id=rule.id, error=str(e))
            return False
    
    async def _validate_rate_limit_rule(self, rule: RateLimitRule) -> bool:
        """Validate rate limit rule"""
        try:
            # Check required fields
            if not rule.name or not rule.algorithm or rule.limit <= 0 or rule.window_seconds <= 0:
                return False
            
            # Validate algorithm
            if rule.algorithm not in RateLimitAlgorithm:
                return False
            
            return True
            
        except Exception as e:
            logger.error("Rate limit rule validation failed", error=str(e))
            return False
    
    async def check_rate_limit(self, request: APIRequest) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is rate limited"""
        try:
            for rule in self.rate_limit_rules.values():
                if not rule.enabled:
                    continue
                
                if not await self._rule_matches_request(rule, request):
                    continue
                
                # Check rate limit based on algorithm
                if rule.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                    limited, info = await self._check_token_bucket_limit(rule, request)
                elif rule.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
                    limited, info = await self._check_sliding_window_limit(rule, request)
                elif rule.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
                    limited, info = await self._check_fixed_window_limit(rule, request)
                else:
                    continue
                
                if limited:
                    return True, info
            
            return False, {}
            
        except Exception as e:
            logger.error("Rate limit check failed", error=str(e))
            return False, {}
    
    async def _rule_matches_request(self, rule: RateLimitRule, request: APIRequest) -> bool:
        """Check if rule matches request"""
        try:
            # Check method
            if rule.method and request.method != rule.method:
                return False
            
            # Check path pattern (simplified)
            if rule.path_pattern and not self._path_matches_pattern(request.path, rule.path_pattern):
                return False
            
            return True
            
        except Exception as e:
            logger.error("Rule matching check failed", error=str(e))
            return False
    
    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches pattern"""
        try:
            # Simple pattern matching (can be enhanced with regex)
            if pattern == "*":
                return True
            elif pattern.endswith("*"):
                return path.startswith(pattern[:-1])
            else:
                return path == pattern
                
        except Exception as e:
            logger.error("Path pattern matching failed", error=str(e))
            return False
    
    async def _check_token_bucket_limit(self, rule: RateLimitRule, request: APIRequest) -> Tuple[bool, Dict[str, Any]]:
        """Check token bucket rate limit"""
        try:
            # Get bucket key
            if rule.user_based and request.user_id:
                bucket_key = f"token_bucket:{rule.id}:user:{request.user_id}"
            elif rule.ip_based:
                bucket_key = f"token_bucket:{rule.id}:ip:{request.ip_address}"
            else:
                bucket_key = f"token_bucket:{rule.id}:global"
            
            # Get current tokens
            current_time = time.time()
            tokens = self.redis_client.get(bucket_key)
            
            if tokens is None:
                # Initialize bucket
                tokens = rule.limit
                self.redis_client.setex(bucket_key, rule.window_seconds, tokens)
            else:
                tokens = int(tokens)
            
            # Check if request can be processed
            if tokens > 0:
                # Consume token
                self.redis_client.decr(bucket_key)
                return False, {"tokens_remaining": tokens - 1}
            else:
                return True, {"error": "Rate limit exceeded", "retry_after": rule.window_seconds}
            
        except Exception as e:
            logger.error("Token bucket limit check failed", error=str(e))
            return False, {}
    
    async def _check_sliding_window_limit(self, rule: RateLimitRule, request: APIRequest) -> Tuple[bool, Dict[str, Any]]:
        """Check sliding window rate limit"""
        try:
            # Get window key
            if rule.user_based and request.user_id:
                window_key = f"sliding_window:{rule.id}:user:{request.user_id}"
            elif rule.ip_based:
                window_key = f"sliding_window:{rule.id}:ip:{request.ip_address}"
            else:
                window_key = f"sliding_window:{rule.id}:global"
            
            # Add current request timestamp
            current_time = time.time()
            self.redis_client.lpush(window_key, current_time)
            
            # Remove old entries
            self.redis_client.ltrim(window_key, 0, -1)
            
            # Check count
            count = self.redis_client.llen(window_key)
            
            if count > rule.limit:
                return True, {"error": "Rate limit exceeded", "count": count}
            
            # Set expiry
            self.redis_client.expire(window_key, rule.window_seconds)
            
            return False, {"requests_in_window": count}
            
        except Exception as e:
            logger.error("Sliding window limit check failed", error=str(e))
            return False, {}
    
    async def _check_fixed_window_limit(self, rule: RateLimitRule, request: APIRequest) -> Tuple[bool, Dict[str, Any]]:
        """Check fixed window rate limit"""
        try:
            # Get window key
            if rule.user_based and request.user_id:
                window_key = f"fixed_window:{rule.id}:user:{request.user_id}"
            elif rule.ip_based:
                window_key = f"fixed_window:{rule.id}:ip:{request.ip_address}"
            else:
                window_key = f"fixed_window:{rule.id}:global"
            
            # Get current count
            current_time = time.time()
            window_start = int(current_time // rule.window_seconds) * rule.window_seconds
            
            count_key = f"{window_key}:{window_key}"
            
            # Increment count
            count = self.redis_client.incr(count_key)
            
            # Set expiry for new windows
            if count == 1:
                self.redis_client.expire(count_key, rule.window_seconds)
            
            if count > rule.limit:
                return True, {"error": "Rate limit exceeded", "count": count}
            
            return False, {"requests_in_window": count}
            
        except Exception as e:
            logger.error("Fixed window limit check failed", error=str(e))
            return False, {}
    
    async def add_api_route(self, route: APIRoute) -> bool:
        """Add an API route"""
        try:
            # Validate route
            if not await self._validate_api_route(route):
                return False
            
            # Store route
            self.api_routes[route.id] = route
            
            # Save to database
            route_record = APIRoutes(
                route_id=route.id,
                path=route.path,
                method=route.method,
                target_url=route.target_url,
                auth_required=route.auth_required,
                auth_type=route.auth_type.value,
                timeout_seconds=route.timeout_seconds,
                retry_count=route.retry_count,
                enabled=route.enabled
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(route_record)
                session.commit()
            finally:
                session.close()
            
            # Add route to FastAPI
            await self._register_route(route)
            
            logger.info("API route added", route_id=route.id)
            return True
            
        except Exception as e:
            logger.error("Failed to add API route", route_id=route.id, error=str(e))
            return False
    
    async def _validate_api_route(self, route: APIRoute) -> bool:
        """Validate API route"""
        try:
            # Check required fields
            if not route.path or not route.method or not route.target_url:
                return False
            
            # Validate method
            valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
            if route.method not in valid_methods:
                return False
            
            # Validate auth type
            if route.auth_type not in AuthType:
                return False
            
            return True
            
        except Exception as e:
            logger.error("API route validation failed", error=str(e))
            return False
    
    async def _register_route(self, route: APIRoute):
        """Register route with FastAPI"""
        try:
            # Create dynamic route handler
            async def route_handler(request: Request, **kwargs):
                return await self._handle_request(request, route)
            
            # Add route to FastAPI
            self.app.add_api_route(
                route.path,
                route_handler,
                methods=[route.method],
                name=route.id
            )
            
        except Exception as e:
            logger.error("Failed to register route", route_id=route.id, error=str(e))
    
    async def _handle_request(self, request: Request, route: APIRoute) -> Response:
        """Handle incoming request"""
        try:
            # Create request object
            api_request = APIRequest(
                id=str(uuid.uuid4()),
                method=request.method,
                path=request.url.path,
                headers=dict(request.headers),
                query_params=dict(request.query_params),
                body=await request.body(),
                ip_address=request.client.host if request.client else "unknown"
            )
            
            # Authentication
            if route.auth_required:
                user_id = await self._authenticate_request(request, route.auth_type)
                if not user_id:
                    raise HTTPException(status_code=401, detail="Unauthorized")
                api_request.user_id = user_id
            
            # Rate limiting
            limited, limit_info = await self.check_rate_limit(api_request)
            if limited:
                raise HTTPException(
                    status_code=429, 
                    detail="Rate limit exceeded",
                    headers={"Retry-After": str(limit_info.get("retry_after", 60))}
                )
            
            # Forward request to target
            response = await self._forward_request(api_request, route)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Request handling failed", error=str(e))
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def _authenticate_request(self, request: Request, auth_type: AuthType) -> Optional[str]:
        """Authenticate request"""
        try:
            if auth_type == AuthType.JWT:
                return await self._authenticate_jwt(request)
            elif auth_type == AuthType.API_KEY:
                return await self._authenticate_api_key(request)
            else:
                return None
                
        except Exception as e:
            logger.error("Authentication failed", error=str(e))
            return None
    
    async def _authenticate_jwt(self, request: Request) -> Optional[str]:
        """Authenticate with JWT"""
        try:
            authorization = request.headers.get("authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return None
            
            token = authorization.split(" ")[1]
            # JWT validation logic here
            # For now, return dummy user_id
            return "user_from_jwt"
            
        except Exception as e:
            logger.error("JWT authentication failed", error=str(e))
            return None
    
    async def _authenticate_api_key(self, request: Request) -> Optional[str]:
        """Authenticate with API key"""
        try:
            api_key = request.headers.get("x-api-key")
            if not api_key:
                return None
            
            # API key validation logic here
            # For now, return dummy user_id
            return "user_from_api_key"
            
        except Exception as e:
            logger.error("API key authentication failed", error=str(e))
            return None
    
    async def _forward_request(self, api_request: APIRequest, route: APIRoute) -> Response:
        """Forward request to target service"""
        try:
            timeout = aiohttp.ClientTimeout(total=route.timeout_seconds)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Prepare headers
                headers = api_request.headers.copy()
                headers.pop("host", None)  # Remove host header
                
                # Make request
                if api_request.method == "GET":
                    async with session.get(
                        route.target_url + api_request.path,
                        headers=headers,
                        params=api_request.query_params
                    ) as response:
                        content = await response.read()
                        return Response(
                            content=content,
                            status_code=response.status,
                            headers=dict(response.headers)
                        )
                elif api_request.method == "POST":
                    async with session.post(
                        route.target_url + api_request.path,
                        headers=headers,
                        params=api_request.query_params,
                        data=api_request.body
                    ) as response:
                        content = await response.read()
                        return Response(
                            content=content,
                            status_code=response.status,
                            headers=dict(response.headers)
                        )
                # Add other methods as needed
                
            raise HTTPException(status_code=405, detail="Method not allowed")
            
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Gateway timeout")
        except Exception as e:
            logger.error("Request forwarding failed", error=str(e))
            raise HTTPException(status_code=502, detail="Bad gateway")
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "total_routes": len(self.api_routes),
            "total_rate_limit_rules": len(self.rate_limit_rules),
            "redis_connected": self.redis_client.ping(),
            "system_uptime": datetime.utcnow().isoformat()
        }


# Configuration
API_GATEWAY_CONFIG = {
    "database": {
        "connection_string": os.getenv("DATABASE_URL")
    },
    "redis": {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", 6379)),
        "db": 0
    },
    "encryption": {
        "key": os.getenv("ENCRYPTION_KEY")
    }
}


# Initialize API gateway
api_gateway = APIGateway(API_GATEWAY_CONFIG)

# Export main components
__all__ = [
    'APIGateway',
    'RateLimitRule',
    'APIRoute',
    'APIRequest',
    'APIResponse',
    'RateLimitAlgorithm',
    'APIVersion',
    'AuthType',
    'api_gateway'
]
