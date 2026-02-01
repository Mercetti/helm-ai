#!/usr/bin/env python3
"""
Authentication Rate Limiting Middleware
Advanced rate limiting specifically for authentication endpoints to prevent brute force attacks
"""

import time
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from collections import defaultdict, deque
from flask import Flask, request, abort, g, current_app
from functools import wraps
import redis
import os

class AuthRateLimiter:
    """Advanced authentication rate limiting middleware"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.redis_client = None
        self.memory_store = defaultdict(lambda: defaultdict(deque))
        
        # Rate limiting configurations
        self.configs = {
            'login': {
                'max_attempts': 5,
                'window_seconds': 900,  # 15 minutes
                'penalty_minutes': 30,  # 30 minutes lockout
                'key_prefix': 'auth_rate_limit:login:'
            },
            'register': {
                'max_attempts': 3,
                'window_seconds': 3600,  # 1 hour
                'penalty_minutes': 60,  # 1 hour lockout
                'key_prefix': 'auth_rate_limit:register:'
            },
            'password_reset': {
                'max_attempts': 3,
                'window_seconds': 3600,  # 1 hour
                'penalty_minutes': 60,  # 1 hour lockout
                'key_prefix': 'auth_rate_limit:password_reset:'
            },
            'token_refresh': {
                'max_attempts': 10,
                'window_seconds': 300,  # 5 minutes
                'penalty_minutes': 15,  # 15 minutes lockout
                'key_prefix': 'auth_rate_limit:token_refresh:'
            },
            'api_auth': {
                'max_attempts': 20,
                'window_seconds': 60,  # 1 minute
                'penalty_minutes': 5,  # 5 minutes lockout
                'key_prefix': 'auth_rate_limit:api_auth:'
            }
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize auth rate limiter"""
        self.app = app
        
        # Initialize Redis if available
        self._init_redis()
        
        # Store rate limiter instance
        app.auth_rate_limiter = self
        
        # Register before request handler
        app.before_request(self._track_request)
    
    def _init_redis(self):
        """Initialize Redis client"""
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            
            # Test Redis connection
            self.redis_client.ping()
            print("✅ Redis connected for auth rate limiting")
            
        except Exception as e:
            print(f"⚠️ Redis not available, using memory store: {e}")
            self.redis_client = None
    
    def _get_client_ip(self) -> str:
        """Get client IP address with proxy support"""
        # Check for forwarded IP (behind proxy)
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr or 'unknown'
    
    def _get_user_identifier(self) -> str:
        """Get unique identifier for rate limiting"""
        client_ip = self._get_client_ip()
        user_agent = request.headers.get('User-Agent', 'unknown')
        
        # Create unique identifier
        identifier_data = f"{client_ip}:{user_agent}"
        identifier = hashlib.sha256(identifier_data.encode()).hexdigest()
        
        return identifier
    
    def _get_redis_key(self, auth_type: str, identifier: str) -> str:
        """Get Redis key for rate limiting"""
        config = self.configs.get(auth_type, self.configs['login'])
        return f"{config['key_prefix']}{identifier}"
    
    def _is_rate_limited(self, auth_type: str, identifier: str) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is rate limited"""
        config = self.configs.get(auth_type, self.configs['login'])
        current_time = int(time.time())
        window_start = current_time - config['window_seconds']
        
        if self.redis_client:
            return self._check_redis_rate_limit(auth_type, identifier, config, current_time, window_start)
        else:
            return self._check_memory_rate_limit(auth_type, identifier, config, current_time, window_start)
    
    def _check_redis_rate_limit(self, auth_type: str, identifier: str, config: Dict[str, Any], 
                              current_time: int, window_start: int) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit using Redis"""
        redis_key = self._get_redis_key(auth_type, identifier)
        
        # Check for existing penalty
        penalty_key = f"{redis_key}:penalty"
        penalty_end = self.redis_client.get(penalty_key)
        
        if penalty_end:
            penalty_end_time = int(penalty_end)
            if current_time < penalty_end_time:
                remaining_time = penalty_end_time - current_time
                return True, {
                    'limited': True,
                    'reason': 'penalty_active',
                    'remaining_seconds': remaining_time,
                    'penalty_minutes': config['penalty_minutes'],
                    'max_attempts': config['max_attempts'],
                    'window_seconds': config['window_seconds']
                }
            else:
                # Penalty expired, remove it
                self.redis_client.delete(penalty_key)
        
        # Check rate limit window
        pipe = self.redis_client.pipeline()
        pipe.zremrangebyscore(redis_key, 0, window_start)
        pipe.zcard(redis_key)
        pipe.expire(redis_key, config['window_seconds'] + 1)
        
        results = pipe.execute()
        current_attempts = results[1]
        
        if current_attempts >= config['max_attempts']:
            # Apply penalty
            penalty_end_time = current_time + (config['penalty_minutes'] * 60)
            self.redis_client.setex(penalty_key, config['penalty_minutes'] * 60, penalty_end_time)
            
            return True, {
                'limited': True,
                'reason': 'max_attempts_exceeded',
                'remaining_seconds': config['penalty_minutes'] * 60,
                'penalty_minutes': config['penalty_minutes'],
                'max_attempts': config['max_attempts'],
                'window_seconds': config['window_seconds'],
                'current_attempts': current_attempts
            }
        
        return False, {
            'limited': False,
            'current_attempts': current_attempts,
            'max_attempts': config['max_attempts'],
            'window_seconds': config['window_seconds'],
            'remaining_attempts': config['max_attempts'] - current_attempts
        }
    
    def _check_memory_rate_limit(self, auth_type: str, identifier: str, config: Dict[str, Any],
                                current_time: int, window_start: int) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit using memory store"""
        store = self.memory_store[auth_type][identifier]
        
        # Check for existing penalty
        penalty_key = f"{identifier}:penalty"
        if penalty_key in store:
            penalty_end_time = store[penalty_key]
            if current_time < penalty_end_time:
                remaining_time = penalty_end_time - current_time
                return True, {
                    'limited': True,
                    'reason': 'penalty_active',
                    'remaining_seconds': remaining_time,
                    'penalty_minutes': config['penalty_minutes'],
                    'max_attempts': config['max_attempts'],
                    'window_seconds': config['window_seconds']
                }
            else:
                del store[penalty_key]
        
        # Clean old entries
        while store['attempts'] and store['attempts'][0] < window_start:
            store['attempts'].popleft()
        
        current_attempts = len(store['attempts'])
        
        if current_attempts >= config['max_attempts']:
            # Apply penalty
            penalty_end_time = current_time + (config['penalty_minutes'] * 60)
            store[penalty_key] = penalty_end_time
            
            return True, {
                'limited': True,
                'reason': 'max_attempts_exceeded',
                'remaining_seconds': config['penalty_minutes'] * 60,
                'penalty_minutes': config['penalty_minutes'],
                'max_attempts': config['max_attempts'],
                'window_seconds': config['window_seconds'],
                'current_attempts': current_attempts
            }
        
        return False, {
            'limited': False,
            'current_attempts': current_attempts,
            'max_attempts': config['max_attempts'],
            'window_seconds': config['window_seconds'],
            'remaining_attempts': config['max_attempts'] - current_attempts
        }
    
    def _record_attempt(self, auth_type: str, identifier: str):
        """Record authentication attempt"""
        current_time = int(time.time())
        
        if self.redis_client:
            redis_key = self._get_redis_key(auth_type, identifier)
            self.redis_client.zadd(redis_key, {str(current_time): current_time})
            self.redis_client.expire(redis_key, self.configs[auth_type]['window_seconds'] + 1)
        else:
            store = self.memory_store[auth_type][identifier]
            store['attempts'].append(current_time)
    
    def _track_request(self):
        """Track authentication requests"""
        # Only track auth endpoints
        if not request.endpoint or not request.endpoint.startswith(('auth_', 'api_')):
            return
        
        # Determine auth type from endpoint
        auth_type = self._get_auth_type_from_endpoint(request.endpoint)
        if not auth_type:
            return
        
        # Check if this is an authentication attempt
        if request.method in ['POST', 'PUT', 'PATCH']:
            identifier = self._get_user_identifier()
            
            # Check rate limit
            is_limited, limit_info = self._is_rate_limited(auth_type, identifier)
            
            if is_limited:
                abort(429, description=f"Rate limit exceeded: {limit_info['reason']}")
            
            # Store limit info for later use
            g.auth_rate_limit_info = limit_info
    
    def _get_auth_type_from_endpoint(self, endpoint: str) -> Optional[str]:
        """Get auth type from endpoint name"""
        endpoint_lower = endpoint.lower()
        
        if 'login' in endpoint_lower:
            return 'login'
        elif 'register' in endpoint_lower or 'signup' in endpoint_lower:
            return 'register'
        elif 'password' in endpoint_lower and 'reset' in endpoint_lower:
            return 'password_reset'
        elif 'token' in endpoint_lower and 'refresh' in endpoint_lower:
            return 'token_refresh'
        elif 'api' in endpoint_lower and ('auth' in endpoint_lower or 'login' in endpoint_lower):
            return 'api_auth'
        
        return None
    
    def check_rate_limit(self, auth_type: str, identifier: str = None) -> Dict[str, Any]:
        """Check rate limit for specific auth type"""
        if identifier is None:
            identifier = self._get_user_identifier()
        
        is_limited, limit_info = self._is_rate_limited(auth_type, identifier)
        return limit_info
    
    def record_attempt(self, auth_type: str, identifier: str = None):
        """Record authentication attempt"""
        if identifier is None:
            identifier = self._get_user_identifier()
        
        self._record_attempt(auth_type, identifier)
    
    def get_rate_limit_headers(self, auth_type: str) -> Dict[str, str]:
        """Get rate limit headers for response"""
        config = self.configs.get(auth_type, self.configs['login'])
        
        headers = {
            'X-RateLimit-Limit': str(config['max_attempts']),
            'X-RateLimit-Window': str(config['window_seconds']),
            'X-RateLimit-Penalty': str(config['penalty_minutes'] * 60)
        }
        
        # Add remaining info if available
        if hasattr(g, 'auth_rate_limit_info'):
            info = g.auth_rate_limit_info
            headers['X-RateLimit-Remaining'] = str(info.get('remaining_attempts', config['max_attempts']))
            headers['X-RateLimit-Reset'] = str(info.get('remaining_seconds', 0))
        
        return headers

# Decorator for rate limiting
def auth_rate_limit(auth_type: str = 'login'):
    """Decorator to apply auth rate limiting to routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get rate limiter instance
            rate_limiter = current_app.auth_rate_limiter if hasattr(current_app, 'auth_rate_limiter') else None
            
            if rate_limiter:
                identifier = rate_limiter._get_user_identifier()
                is_limited, limit_info = rate_limiter._is_rate_limited(auth_type, identifier)
                
                if is_limited:
                    abort(429, description=f"Rate limit exceeded: {limit_info['reason']}")
                
                # Store limit info for headers
                g.auth_rate_limit_info = limit_info
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Flask extension factory
def create_auth_rate_limiter(app: Flask = None) -> AuthRateLimiter:
    """Factory function to create auth rate limiter"""
    return AuthRateLimiter(app)

# Example usage
if __name__ == "__main__":
    # Test auth rate limiting
    app = Flask(__name__)
    
    # Initialize auth rate limiter
    rate_limiter = create_auth_rate_limiter(app)
    
    @app.route('/login', methods=['POST'])
    @auth_rate_limit('login')
    def login():
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Record attempt (successful or failed)
        rate_limiter.record_attempt('login')
        
        # Add rate limit headers
        headers = rate_limiter.get_rate_limit_headers('login')
        response_data = {"status": "success", "message": "Login attempt recorded"}
        
        from flask import jsonify
        response = jsonify(response_data)
        
        # Add headers to response
        for key, value in headers.items():
            response.headers[key] = value
        
        return response
    
    @app.route('/register', methods=['POST'])
    @auth_rate_limit('register')
    def register():
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Record attempt
        rate_limiter.record_attempt('register')
        
        # Add rate limit headers
        headers = rate_limiter.get_rate_limit_headers('register')
        
        from flask import jsonify
        response = jsonify({"status": "success", "message": "Registration attempt recorded"})
        
        for key, value in headers.items():
            response.headers[key] = value
        
        return response
    
    @app.route('/check-rate-limit')
    def check_rate_limit():
        auth_type = request.args.get('type', 'login')
        limit_info = rate_limiter.check_rate_limit(auth_type)
        
        from flask import jsonify
        return jsonify(limit_info)
    
    app.run(debug=True)
