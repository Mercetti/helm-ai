"""
Helm AI API Middleware
This module provides comprehensive API middleware for security, validation, and monitoring
"""

import os
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from functools import wraps
import hashlib
import hmac

from flask import request, g, jsonify
from werkzeug.exceptions import HTTPException

from .rate_limiting import rate_limit_manager, RateLimitException
from .error_handling import error_handler, ErrorContext, HelmAIException, APIResponse
from .input_validation import input_validator

logger = logging.getLogger(__name__)

class APIMiddleware:
    """Comprehensive API middleware"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
        
        # Configuration
        self.enable_rate_limiting = os.getenv('ENABLE_RATE_LIMITING', 'true').lower() == 'true'
        self.enable_input_validation = os.getenv('ENABLE_INPUT_VALIDATION', 'true').lower() == 'true'
        self.enable_request_logging = os.getenv('ENABLE_REQUEST_LOGGING', 'true').lower() == 'true'
        self.enable_security_headers = os.getenv('ENABLE_SECURITY_HEADERS', 'true').lower() == 'true'
        self.enable_cors = os.getenv('ENABLE_CORS', 'true').lower() == 'true'
        
        # Security configuration
        self.allowed_origins = os.getenv('CORS_ALLOWED_ORIGINS', '*').split(',')
        self.allowed_methods = os.getenv('CORS_ALLOWED_METHODS', 'GET,POST,PUT,DELETE,OPTIONS').split(',')
        self.allowed_headers = os.getenv('CORS_ALLOWED_HEADERS', 'Content-Type,Authorization,X-API-Key').split(',')
    
    def init_app(self, app):
        """Initialize Flask app with middleware"""
        # Register before/after request handlers
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Register error handlers
        app.errorhandler(Exception)(self.handle_exception)
        app.error_handler_spec[None][404] = self.handle_not_found
        app.error_handler_spec[None][405] = self.handle_method_not_allowed
        app.error_handler_spec[None][429] = self.handle_rate_limit_exceeded
        app.error_handler_spec[None][500] = self.handle_server_error
    
    def before_request(self):
        """Process request before handling"""
        # Generate request ID
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()
        
        # Extract request information
        g.ip_address = self._get_client_ip()
        g.user_agent = request.headers.get('User-Agent', '')
        g.endpoint = request.endpoint
        g.method = request.method
        
        # Log request start
        if self.enable_request_logging:
            self._log_request_start()
        
        # Apply CORS headers
        if self.enable_cors:
            self._apply_cors_headers()
        
        # Apply security headers
        if self.enable_security_headers:
            self._apply_security_headers()
        
        # Rate limiting
        if self.enable_rate_limiting:
            self._check_rate_limit()
        
        # Input validation
        if self.enable_input_validation and request.method in ['POST', 'PUT', 'PATCH']:
            self._validate_input()
    
    def after_request(self, response):
        """Process response after handling"""
        # Calculate request duration
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        # Add request ID to response
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        # Log request completion
        if self.enable_request_logging:
            self._log_request_completion(response)
        
        return response
    
    def _get_client_ip(self) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def _log_request_start(self):
        """Log request start"""
        log_data = {
            'request_id': g.request_id,
            'method': request.method,
            'url': request.url,
            'ip_address': g.ip_address,
            'user_agent': g.user_agent,
            'content_length': request.content_length or 0
        }
        
        logger.info(f"Request started: {json.dumps(log_data)}")
    
    def _log_request_completion(self, response):
        """Log request completion"""
        log_data = {
            'request_id': g.request_id,
            'method': request.method,
            'url': request.url,
            'status_code': response.status_code,
            'response_size': len(response.get_data()) if hasattr(response, 'get_data') else 0
        }
        
        if hasattr(g, 'start_time'):
            log_data['duration_ms'] = (time.time() - g.start_time) * 1000
        
        level = logging.ERROR if response.status_code >= 400 else logging.INFO
        logger.log(level, f"Request completed: {json.dumps(log_data)}")
    
    def _apply_cors_headers(self):
        """Apply CORS headers"""
        origin = request.headers.get('Origin', '')
        
        if self.allowed_origins == '*' or origin in self.allowed_origins:
            if hasattr(g, 'cors_applied'):
                return  # Already applied for OPTIONS request
            
            g.cors_applied = True
            
            # This will be handled in the response
            pass
    
    def _apply_security_headers(self):
        """Apply security headers"""
        # These will be added to the response in after_request
        g.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
    
    def _check_rate_limit(self):
        """Check rate limits"""
        try:
            # Get identifiers for rate limiting
            user_id = getattr(g, 'user_id', None)
            api_key = request.headers.get('X-API-Key')
            
            # Check rate limits
            is_allowed, violating_rule = rate_limit_manager.check_rate_limit(
                identifier=g.request_id,
                endpoint=request.endpoint,
                ip_address=g.ip_address,
                user_id=user_id,
                api_key=api_key
            )
            
            if not is_allowed:
                # Create error context
                context = ErrorContext(
                    request_id=g.request_id,
                    ip_address=g.ip_address,
                    endpoint=request.endpoint,
                    method=request.method,
                    user_agent=g.user_agent
                )
                
                # Create rate limit exception
                raise RateLimitException(
                    message="Rate limit exceeded",
                    limit=violating_rule.requests_per_window,
                    window=violating_rule.window_seconds,
                    context=context
                )
        
        except Exception as e:
            if isinstance(e, RateLimitException):
                raise
            logger.error(f"Rate limiting check failed: {e}")
    
    def _validate_input(self):
        """Validate input data"""
        try:
            if request.is_json:
                data = request.get_json()
                if data:
                    # Sanitize input
                    sanitized_data = input_validator.sanitize_input(data)
                    
                    # Store sanitized data for use in endpoints
                    g.validated_data = sanitized_data
            
            elif request.form:
                # Handle form data
                form_data = dict(request.form)
                sanitized_data = input_validator.sanitize_input(form_data)
                g.validated_data = sanitized_data
        
        except Exception as e:
            # Create error context
            context = ErrorContext(
                request_id=g.request_id,
                ip_address=g.ip_address,
                endpoint=request.endpoint,
                method=request.method,
                user_agent=g.user_agent
            )
            
            # Create validation exception
            from .error_handling import ValidationException
            raise ValidationException(
                message=f"Input validation failed: {str(e)}",
                context=context
            )
    
    def handle_exception(self, exception):
        """Handle all exceptions"""
        # Create error context
        context = ErrorContext(
            request_id=getattr(g, 'request_id', None),
            ip_address=getattr(g, 'ip_address', None),
            endpoint=getattr(g, 'endpoint', None),
            method=getattr(g, 'method', None),
            user_agent=getattr(g, 'user_agent', None)
        )
        
        # Handle the exception
        handled_exception = error_handler.handle_exception(exception, context)
        
        # Return error response
        response_data = APIResponse.error(handled_exception)
        
        # Convert to Flask response
        response = jsonify(response_data)
        
        # Add security headers if enabled
        if self.enable_security_headers and hasattr(g, 'security_headers'):
            for header, value in g.security_headers.items():
                response.headers[header] = value
        
        return response, handled_exception.http_status_code
    
    def handle_not_found(self, error):
        """Handle 404 errors"""
        context = ErrorContext(
            request_id=getattr(g, 'request_id', None),
            ip_address=getattr(g, 'ip_address', None),
            endpoint=request.endpoint,
            method=request.method,
            user_agent=getattr(g, 'user_agent', None)
        )
        
        from .error_handling import NotFoundException
        exception = NotFoundException(
            message="Endpoint not found",
            resource_type="endpoint",
            resource_id=request.endpoint,
            context=context
        )
        
        response = APIResponse.error(exception)
        return jsonify(response), 404
    
    def handle_method_not_allowed(self, error):
        """Handle 405 errors"""
        context = ErrorContext(
            request_id=getattr(g, 'request_id', None),
            ip_address=getattr(g, 'ip_address', None),
            endpoint=request.endpoint,
            method=request.method,
            user_agent=getattr(g, 'user_agent', None)
        )
        
        from .error_handling import BusinessException
        exception = BusinessException(
            message=f"Method {request.method} not allowed for this endpoint",
            business_rule="http_method_allowed",
            context=context
        )
        
        response = APIResponse.error(exception)
        return jsonify(response), 405
    
    def handle_rate_limit_exceeded(self, error):
        """Handle 429 errors"""
        context = ErrorContext(
            request_id=getattr(g, 'request_id', None),
            ip_address=getattr(g, 'ip_address', None),
            endpoint=request.endpoint,
            method=request.method,
            user_agent=getattr(g, 'user_agent', None)
        )
        
        from .rate_limiting import RateLimitException
        if isinstance(error, RateLimitException):
            exception = error
        else:
            exception = RateLimitException(
                message="Rate limit exceeded",
                context=context
            )
        
        response = APIResponse.error(exception)
        return jsonify(response), 429
    
    def handle_server_error(self, error):
        """Handle 500 errors"""
        context = ErrorContext(
            request_id=getattr(g, 'request_id', None),
            ip_address=getattr(g, 'ip_address', None),
            endpoint=request.endpoint,
            method=request.method,
            user_agent=getattr(g, 'user_agent', None)
        )
        
        from .error_handling import SystemException
        exception = SystemException(
            message="Internal server error",
            system_component="api_server",
            context=context,
            cause=error
        )
        
        response = APIResponse.error(exception)
        return jsonify(response), 500


# Decorators for common middleware functionality
def require_api_key(func):
    """Decorator to require API key"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            from .error_handling import AuthenticationException
            raise AuthenticationException("API key required")
        
        # Store API key for rate limiting
        g.api_key = api_key
        
        return func(*args, **kwargs)
    return wrapper


def require_auth(func):
    """Decorator to require authentication"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if user is authenticated
        if not hasattr(g, 'user_id') or not g.user_id:
            from .error_handling import AuthenticationException
            raise AuthenticationException("Authentication required")
        
        return func(*args, **kwargs)
    return wrapper


def validate_params(schema: Dict[str, Any], location: str = 'json'):
    """Decorator to validate request parameters"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Get data based on location
                if location == 'json':
                    data = request.get_json() or {}
                elif location == 'form':
                    data = dict(request.form)
                elif location == 'args':
                    data = request.args.to_dict()
                else:
                    data = {}
                
                # Validate against schema
                validation_schema = input_validator.create_schema(schema)
                validated_data = input_validator.validate(data)
                
                # Store validated data
                g.validated_params = validated_data
                
                return func(*args, **kwargs)
            
            except ValueError as e:
                from .error_handling import ValidationException
                raise ValidationException(str(e))
        
        return wrapper
    return decorator


def rate_limit(requests_per_window: int, window_seconds: int, identifier: str = None):
    """Decorator for custom rate limiting"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use custom identifier or generate one
            limit_identifier = identifier or f"{request.endpoint}:{g.request_id}"
            
            # Create temporary rule
            from .rate_limiting import RateLimitRule, RateLimitType, RateLimitAlgorithm
            temp_rule = RateLimitRule(
                rule_id=f"temp_{func.__name__}",
                name=f"temp_{func.__name__}",
                limit_type=RateLimitType.ENDPOINT_BASED,
                algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
                requests_per_window=requests_per_window,
                window_seconds=window_seconds
            )
            
            # Check rate limit
            is_allowed, violating_rule = rate_limit_manager.check_rate_limit(
                identifier=limit_identifier,
                endpoint=request.endpoint,
                ip_address=g.ip_address,
                user_id=getattr(g, 'user_id', None)
            )
            
            if not is_allowed:
                from .rate_limiting import RateLimitException
                raise RateLimitException(
                    message="Rate limit exceeded",
                    limit=requests_per_window,
                    window=window_seconds
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def log_requests(include_body: bool = False):
    """Decorator to log requests"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Log request
        log_data = {
            'request_id': getattr(g, 'request_id', 'unknown'),
            'method': request.method,
            'url': request.url,
            'ip_address': getattr(g, 'ip_address', 'unknown'),
            'user_agent': request.headers.get('User-Agent', ''),
            'function': func.__name__
        }
        
        if include_body and request.is_json:
            log_data['body'] = request.get_json()
        
        logger.info(f"API Request: {json.dumps(log_data)}")
        
        try:
            result = func(*args, **kwargs)
            
            # Log response
            duration = time.time() - start_time
            logger.info(f"API Response: {json.dumps({
                'request_id': getattr(g, 'request_id', 'unknown'),
                'function': func.__name__,
                'duration_ms': duration * 1000,
                'status': 'success'
            })}")
            
            return result
        
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            logger.error(f"API Error: {json.dumps({
                'request_id': getattr(g, 'request_id', 'unknown'),
                'function': func.__name__,
                'duration_ms': duration * 1000,
                'error': str(e)
            })}")
            
            raise
    
    return wrapper


def cache_response(timeout: int = 300, key_func: Callable = None):
    """Decorator to cache responses"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hashlib.sha256(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
            
            # This would integrate with Redis or other cache
            # For now, just execute the function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Global middleware instance
api_middleware = APIMiddleware()
