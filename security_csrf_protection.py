#!/usr/bin/env python3
"""
CSRF Protection Middleware
Comprehensive CSRF protection for Flask applications with token generation and validation
"""

import os
import secrets
import time
from flask import Flask, request, session, abort, current_app
from functools import wraps
from typing import Optional, Dict, Any
import hashlib
import hmac

class CSRFProtection:
    """CSRF protection middleware for Flask applications"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.token_length = 32
        self.token_expiry = 3600  # 1 hour
        self.cookie_name = 'csrf_token'
        self.header_name = 'X-CSRF-Token'
        self.field_name = 'csrf_token'
        self.secret_key = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize CSRF protection middleware"""
        self.app = app
        self.secret_key = app.config.get('SECRET_KEY', os.getenv('SECRET_KEY', 'dev-secret-key'))
        
        # Store CSRF middleware instance
        app.csrf = self
        
        # Register before request handler for validation
        app.before_request(self._validate_csrf)
        
        # Register after request handler for token injection
        app.after_request(self._inject_csrf_token)
    
    def generate_token(self) -> str:
        """Generate a new CSRF token"""
        # Create random token
        random_token = secrets.token_urlsafe(self.token_length)
        
        # Create timestamp
        timestamp = str(int(time.time()))
        
        # Create signature
        message = f"{random_token}:{timestamp}"
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Combine token, timestamp, and signature
        csrf_token = f"{random_token}:{timestamp}:{signature}"
        
        return csrf_token
    
    def validate_token(self, token: str) -> bool:
        """Validate CSRF token"""
        if not token:
            return False
        
        try:
            # Split token into parts
            parts = token.split(':')
            if len(parts) != 3:
                return False
            
            random_token, timestamp, signature = parts
            
            # Verify timestamp (prevent replay attacks)
            try:
                token_time = int(timestamp)
                current_time = int(time.time())
                
                # Check if token is expired
                if current_time - token_time > self.token_expiry:
                    return False
                
                # Check if token is from the future (clock skew tolerance)
                if token_time - current_time > 300:  # 5 minutes tolerance
                    return False
                    
            except ValueError:
                return False
            
            # Verify signature
            message = f"{random_token}:{timestamp}"
            expected_signature = hmac.new(
                self.secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Use constant-time comparison to prevent timing attacks
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception:
            return False
    
    def _validate_csrf_request(self) -> bool:
        """Validate CSRF token for current request"""
        # Skip CSRF validation for safe methods
        if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return True
        
        # Skip CSRF validation for API endpoints that use other auth methods
        if self._should_skip_csrf():
            return True
        
        # Get token from various sources
        token = self._get_csrf_token()
        
        if not token:
            return False
        
        return self.validate_token(token)
    
    def _validate_csrf(self):
        """Before request handler for CSRF validation"""
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if not self._should_skip_csrf():
                if not self._validate_csrf_request():
                    abort(403, description="CSRF token validation failed")
    
    def _inject_csrf_token(self, response):
        """After request handler for token injection"""
        # Only inject token for HTML responses
        if response.content_type and 'text/html' in response.content_type:
            # Generate new token if not present
            if self.cookie_name not in request.cookies:
                token = self.generate_token()
                response.set_cookie(
                    self.cookie_name,
                    token,
                    max_age=self.token_expiry,
                    httponly=True,
                    secure=request.is_secure,
                    samesite='Lax'
                )
        
        return response
    
    def _get_csrf_token(self) -> Optional[str]:
        """Get CSRF token from request"""
        # Check header first (preferred for AJAX requests)
        token = request.headers.get(self.header_name)
        if token:
            return token
        
        # Check form data
        token = request.form.get(self.field_name)
        if token:
            return token
        
        # Check JSON data
        if request.is_json:
            data = request.get_json(silent=True)
            if data and isinstance(data, dict):
                token = data.get(self.field_name)
                if token:
                    return token
        
        # Check cookie (fallback)
        token = request.cookies.get(self.cookie_name)
        if token:
            return token
        
        return None
    
    def _should_skip_csrf(self) -> bool:
        """Determine if CSRF validation should be skipped"""
        # Skip for API endpoints that use other authentication
        if request.path.startswith('/api/'):
            # Check if request has valid authentication
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                return True
        
        # Skip for health checks
        if request.path.startswith('/health'):
            return True
        
        # Skip for static files
        if request.path.startswith('/static'):
            return True
        
        # Skip for webhook endpoints
        if request.path.startswith('/webhook'):
            return True
        
        return False
    
    def get_token(self) -> str:
        """Get current CSRF token or generate new one"""
        token = self._get_csrf_token()
        if not token:
            token = self.generate_token()
        return token
    
    def get_token_field(self) -> str:
        """Generate HTML hidden field for CSRF token"""
        token = self.get_token()
        return f'<input type="hidden" name="{self.field_name}" value="{token}">'
    
    def get_meta_tag(self) -> str:
        """Generate meta tag for CSRF token"""
        token = self.get_token()
        return f'<meta name="csrf-token" content="{token}">'

# Decorator for CSRF protection
def csrf_protect(f):
    """Decorator to protect routes with CSRF validation"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get CSRF middleware instance
        csrf = current_app.csrf if hasattr(current_app, 'csrf') else None
        
        if csrf and not csrf._validate_csrf_request():
            abort(403, description="CSRF token validation failed")
        
        return f(*args, **kwargs)
    return decorated_function

# Decorator to exempt routes from CSRF protection
def csrf_exempt(f):
    """Decorator to exempt routes from CSRF validation"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Mark request as CSRF exempt
        request.csrf_exempt = True
        return f(*args, **kwargs)
    return decorated_function

# Flask extension factory
def create_csrf_protection(app: Flask = None) -> CSRFProtection:
    """Factory function to create CSRF protection middleware"""
    return CSRFProtection(app)

# Template context processor for CSRF tokens
def csrf_template_context():
    """Template context processor for CSRF tokens"""
    if hasattr(current_app, 'csrf'):
        csrf = current_app.csrf
        return {
            'csrf_token': csrf.get_token(),
            'csrf_token_field': csrf.get_token_field(),
            'csrf_meta_tag': csrf.get_meta_tag()
        }
    return {}

# Example usage
if __name__ == "__main__":
    # Test CSRF protection
    app = Flask(__name__)
    app.secret_key = 'test-secret-key-change-in-production'
    
    # Initialize CSRF protection
    csrf = create_csrf_protection(app)
    
    @app.route('/')
    def home():
        return """
        <html>
        <head>
            <title>CSRF Protection Test</title>
            {csrf_meta_tag}
        </head>
        <body>
            <h1>🛡️ CSRF Protection Active</h1>
            <form method="POST" action="/submit">
                {csrf_token_field}
                <input type="text" name="data" placeholder="Enter some data">
                <button type="submit">Submit</button>
            </form>
        </body>
        </html>
        """.format(
            csrf_meta_tag=csrf.get_meta_tag(),
            csrf_token_field=csrf.get_token_field()
        )
    
    @app.route('/submit', methods=['POST'])
    @csrf_protect
    def submit():
        data = request.form.get('data', '')
        return f"✅ Form submitted successfully! Data: {data}"
    
    @app.route('/api/data', methods=['POST'])
    @csrf_exempt  # API endpoint uses JWT auth instead
    def api_data():
        return {"status": "success", "message": "API endpoint - CSRF exempt"}
    
    @app.route('/health')
    def health():
        return {"status": "healthy", "csrf_protection": "active"}
    
    app.run(debug=True)
