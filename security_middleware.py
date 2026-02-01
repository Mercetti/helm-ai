#!/usr/bin/env python3
"""
Stellar Logic AI Security Middleware
Flask middleware for security hardening
"""

from flask import Flask, request, g, jsonify, make_response
from functools import wraps
import time
import hashlib
import secrets
from security_framework import security_framework

class SecurityMiddleware:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Flask application with security middleware"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.errorhandler(Exception)(self.handle_exception)
        
        # Register security event handlers
        app.register_error_handler(401, self.unauthorized)
        app.register_error_handler(403, self.forbidden)
        app.register_error_handler(429, self.rate_limit_exceeded)
        app.register_error_handler(500, self.internal_error)
    
    def before_request(self):
        """Before request security checks"""
        # Store request start time
        g.start_time = time.time()
        
        # Get client IP
        g.client_ip = request.remote_addr
        
        # Check IP reputation
        if not security_framework.check_ip_reputation(g.client_ip):
            security_framework.log_security_event(
                'BLOCKED_IP',
                {'ip': g.client_ip, 'endpoint': request.path},
                'WARNING'
            )
            return jsonify({'error': 'Access denied'}), 403
        
        # Rate limiting
        if not security_framework.check_rate_limit(g.client_ip, request.endpoint):
            security_framework.log_security_event(
                'RATE_LIMIT_EXCEEDED',
                {'ip': g.client_ip, 'endpoint': request.path},
                'WARNING'
            )
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        # Validate request size
        content_length = request.content_length or 0
        if content_length > 10 * 1024 * 1024:  # 10MB limit
            return jsonify({'error': 'Request too large'}), 413
    
    def after_request(self, response):
        """After request security headers"""
        # Add security headers
        security_headers = security_framework.generate_secure_headers()
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # Add custom headers
        response.headers['X-Request-ID'] = secrets.token_urlsafe(16)
        response.headers['X-Response-Time'] = f"{time.time() - g.start_time:.3f}s"
        
        # Log request
        security_framework.log_security_event(
            'API_REQUEST',
            {
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'ip': g.client_ip,
                'duration': time.time() - g.start_time
            },
            'INFO'
        )
        
        return response
    
    def handle_exception(self, exception):
        """Handle security exceptions"""
        security_framework.log_security_event(
            'SECURITY_EXCEPTION',
            {
                'exception': str(exception),
                'path': request.path,
                'method': request.method,
                'ip': g.client_ip
            },
            'CRITICAL'
        )
        
        return jsonify({
            'error': 'Internal server error',
            'request_id': getattr(g, 'request_id', 'unknown')
        }), 500
    
    def unauthorized(self, error):
        """Handle unauthorized access"""
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    def forbidden(self, error):
        """Handle forbidden access"""
        return jsonify({
            'error': 'Forbidden',
            'message': 'Insufficient permissions'
        }), 403
    
    def rate_limit_exceeded(self, error):
        """Handle rate limit exceeded"""
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests'
        }), 429
    
    def internal_error(self, error):
        """Handle internal server error"""
        return jsonify({
            'error': 'Internal server error',
            'message': 'Something went wrong'
        }), 500

# Flask extension
class Security:
    def __init__(self, app=None):
        self.middleware = SecurityMiddleware()
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Flask application with security"""
        self.middleware.init_app(app)
        app.security = self

# Security decorators
def secure_input(input_type='string'):
    """Decorator for input validation"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Validate JSON input
            if request.is_json:
                data = request.get_json()
                if not security_framework.validate_input(data, 'json'):
                    return jsonify({'error': 'Invalid input'}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_output(f):
    """Decorator for output sanitization"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        if hasattr(response, 'data'):
            response.data = security_framework.sanitize_output(response.data)
        
        return response
    return decorated_function

if __name__ == '__main__':
    print("🛡️ STELLAR LOGIC AI SECURITY MIDDLEWARE")
    print("✅ Security middleware ready for Flask applications")
