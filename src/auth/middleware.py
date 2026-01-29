"""
Helm AI Authentication Middleware
This module provides middleware for API authentication and authorization
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
from datetime import datetime
from flask import request, jsonify, g
import jwt

from .auth_manager import auth_manager, Permission

logger = logging.getLogger(__name__)

class AuthMiddleware:
    """Authentication middleware for API endpoints"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Flask app with auth middleware"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Add error handlers
        app.error_handler_spec[None][401] = self.handle_unauthorized
        app.error_handler_spec[None][403] = self.handle_forbidden
    
    def before_request(self):
        """Process request before handling"""
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        token = None
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # Validate token and set user context
        if token:
            try:
                payload = auth_manager.validate_token(token)
                if payload:
                    g.user_id = payload['user_id']
                    g.provider = payload['provider']
                    g.authenticated = True
                else:
                    g.authenticated = False
            except Exception as e:
                logger.warning(f"Token validation failed: {e}")
                g.authenticated = False
        else:
            g.authenticated = False
        
        # Log request
        self._log_request()
    
    def after_request(self, response):
        """Process response after handling"""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    def handle_unauthorized(self, error):
        """Handle unauthorized requests"""
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required',
            'timestamp': datetime.now().isoformat()
        }), 401
    
    def handle_forbidden(self, error):
        """Handle forbidden requests"""
        return jsonify({
            'error': 'Forbidden',
            'message': 'Insufficient permissions',
            'timestamp': datetime.now().isoformat()
        }), 403
    
    def _log_request(self):
        """Log request for audit purposes"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'method': request.method,
            'endpoint': request.endpoint,
            'path': request.path,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'user_id': getattr(g, 'user_id', None),
            'authenticated': getattr(g, 'authenticated', False)
        }
        
        logger.info(f"API Request: {json.dumps(log_data)}")


def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(g, 'authenticated', False):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication required',
                'timestamp': datetime.now().isoformat()
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_permission(permission: Union[str, Permission]) -> Callable:
    """Decorator to require specific permission"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not getattr(g, 'authenticated', False):
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Authentication required',
                    'timestamp': datetime.now().isoformat()
                }), 401
            
            user_id = getattr(g, 'user_id', None)
            if not user_id or not auth_manager.check_permission(user_id, permission):
                return jsonify({
                    'error': 'Forbidden',
                    'message': f'Permission {permission} required',
                    'timestamp': datetime.now().isoformat()
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_permissions(permissions: List[Union[str, Permission]], require_all: bool = False) -> Callable:
    """Decorator to require multiple permissions"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not getattr(g, 'authenticated', False):
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Authentication required',
                    'timestamp': datetime.now().isoformat()
                }), 401
            
            user_id = getattr(g, 'user_id', None)
            if not user_id or not auth_manager.check_permissions(user_id, permissions, require_all):
                return jsonify({
                    'error': 'Forbidden',
                    'message': f'Permissions {permissions} required',
                    'timestamp': datetime.now().isoformat()
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_role(role: str) -> Callable:
    """Decorator to require specific role"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not getattr(g, 'authenticated', False):
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Authentication required',
                    'timestamp': datetime.now().isoformat()
                }), 401
            
            user_id = getattr(g, 'user_id', None)
            user_info = auth_manager.get_user_info(user_id)
            
            if not user_info or role not in user_info.get('roles', []):
                return jsonify({
                    'error': 'Forbidden',
                    'message': f'Role {role} required',
                    'timestamp': datetime.now().isoformat()
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_superuser(f: Callable) -> Callable:
    """Decorator to require superuser access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(g, 'authenticated', False):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication required',
                'timestamp': datetime.now().isoformat()
            }), 401
        
        user_id = getattr(g, 'user_id', None)
        user_info = auth_manager.get_user_info(user_id)
        
        if not user_info or not user_info.get('is_superuser', False):
            return jsonify({
                'error': 'Forbidden',
                'message': 'Superuser access required',
                'timestamp': datetime.now().isoformat()
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def optional_auth(f: Callable) -> Callable:
    """Decorator for optional authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Token is already validated in before_request
        # Just pass through - function can check g.authenticated
        return f(*args, **kwargs)
    
    return decorated_function


def rate_limit(max_requests: int = 100, window_seconds: int = 3600) -> Callable:
    """Simple rate limiting decorator"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This would integrate with a proper rate limiting system like Redis
            # For now, just pass through
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


class APIKeyAuth:
    """API Key authentication for service-to-service communication"""
    
    def __init__(self):
        self.api_keys = {}
        self._load_api_keys()
    
    def _load_api_keys(self):
        """Load API keys from environment"""
        # Load service API keys
        service_keys = os.getenv('SERVICE_API_KEYS', '').split(',')
        for key in service_keys:
            if ':' in key:
                service, api_key = key.split(':', 1)
                self.api_keys[api_key] = service
    
    def validate_api_key(self, api_key: str) -> Optional[str]:
        """Validate API key and return service name"""
        return self.api_keys.get(api_key)
    
    def require_api_key(f: Callable) -> Callable:
        """Decorator to require API key authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'API key required',
                    'timestamp': datetime.now().isoformat()
                }), 401
            
            service = api_key_auth.validate_api_key(api_key)
            if not service:
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Invalid API key',
                    'timestamp': datetime.now().isoformat()
                }), 401
            
            g.service = service
            g.authenticated = True
            
            return f(*args, **kwargs)
        
        return decorated_function


# Global instance
api_key_auth = APIKeyAuth()


def cors_handler(f: Callable) -> Callable:
    """CORS handler decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-API-Key')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
        
        response = f(*args, **kwargs)
        if hasattr(response, 'headers'):
            response.headers.add('Access-Control-Allow-Origin', '*')
        
        return response
    
    return decorated_function


def security_headers(f: Callable) -> Callable:
    """Add security headers decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        if hasattr(response, 'headers'):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = "default-src 'self'"
        
        return response
    
    return decorated_function


def audit_log(action: str = None) -> Callable:
    """Audit logging decorator"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = datetime.now()
            
            try:
                result = f(*args, **kwargs)
                status = 'success'
                return result
            except Exception as e:
                status = 'error'
                error_message = str(e)
                raise
            finally:
                # Log audit entry
                audit_data = {
                    'timestamp': start_time.isoformat(),
                    'action': action or f.__name__,
                    'endpoint': request.endpoint,
                    'method': request.method,
                    'path': request.path,
                    'user_id': getattr(g, 'user_id', None),
                    'service': getattr(g, 'service', None),
                    'ip_address': request.remote_addr,
                    'status': status,
                    'duration_ms': (datetime.now() - start_time).total_seconds() * 1000
                }
                
                if status == 'error':
                    audit_data['error'] = error_message
                
                logger.info(f"Audit Log: {json.dumps(audit_data)}")
        
        return decorated_function
    return decorator
