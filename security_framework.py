#!/usr/bin/env python3
"""
Stellar Logic AI Security Framework
Enterprise-grade security implementation
"""

import os
import json
import hashlib
import secrets
import jwt
import time
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g
import bcrypt
import ssl
from cryptography.fernet import Fernet
import logging

class SecurityFramework:
    def __init__(self):
        self.config = self.load_security_config()
        self.encryption_key = self.generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.session_store = {}
        self.rate_limiter = {}
        
        # Setup logging
        self.setup_logging()
        
        print("✅ Security Framework initialized")
    
    def load_security_config(self):
        """Load security configuration"""
        return {
            'authentication': {
                'jwt_secret': os.getenv('JWT_SECRET', secrets.token_urlsafe(32)),
                'token_expiry': 3600,  # 1 hour
                'refresh_token_expiry': 86400,  # 24 hours
                'max_login_attempts': 5,
                'lockout_duration': 900  # 15 minutes
            },
            'encryption': {
                'algorithm': 'AES-256-GCM',
                'key_rotation_days': 90,
                'data_at_rest_encryption': True,
                'data_in_transit_encryption': True
            },
            'rate_limiting': {
                'default_limit': 1000,  # requests per hour
                'burst_limit': 100,      # requests per minute
                'whitelist_ips': [],
                'blacklist_ips': []
            },
            'csrf': {
                'enabled': True,
                'token_expiry': 3600,
                'secure_cookie': True
            },
            'security_headers': {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'Content-Security-Policy': "default-src 'self'"
            }
        }
    
    def setup_logging(self):
        """Setup security logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('security.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SecurityFramework')
    
    def generate_encryption_key(self):
        """Generate encryption key"""
        key_file = 'encryption.key'
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def hash_password(self, password):
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password, hashed):
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except:
            return False
    
    def generate_jwt_token(self, user_id, role='user'):
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'role': role,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=self.config['authentication']['token_expiry'])
        }
        
        return jwt.encode(payload, self.config['authentication']['jwt_secret'], algorithm='HS256')
    
    def verify_jwt_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.config['authentication']['jwt_secret'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return self.cipher_suite.encrypt(data)
    
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        decrypted = self.cipher_suite.decrypt(encrypted_data)
        return decrypted.decode('utf-8')
    
    def generate_csrf_token(self):
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    def verify_csrf_token(self, token, session_token):
        """Verify CSRF token"""
        return secrets.compare_digest(token, session_token)
    
    def check_rate_limit(self, client_ip, endpoint=None):
        """Check rate limiting"""
        current_time = time.time()
        
        if client_ip not in self.rate_limiter:
            self.rate_limiter[client_ip] = []
        
        # Clean old entries
        self.rate_limiter[client_ip] = [
            req_time for req_time in self.rate_limiter[client_ip]
            if current_time - req_time < 3600  # 1 hour
        ]
        
        # Check limits
        hourly_limit = self.config['rate_limiting']['default_limit']
        if len(self.rate_limiter[client_ip]) >= hourly_limit:
            return False
        
        # Check burst limit (last minute)
        burst_requests = [
            req_time for req_time in self.rate_limiter[client_ip]
            if current_time - req_time < 60  # 1 minute
        ]
        
        if len(burst_requests) >= self.config['rate_limiting']['burst_limit']:
            return False
        
        self.rate_limiter[client_ip].append(current_time)
        return True
    
    def validate_input(self, data, input_type='string'):
        """Validate and sanitize input"""
        if input_type == 'string':
            if not isinstance(data, str):
                return False
            
            # Check for dangerous patterns
            dangerous_patterns = [
                '<script', '</script>', 'javascript:', 'vbscript:',
                'onload=', 'onerror=', 'onclick=', 'onmouseover=',
                'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP',
                'UNION', 'EXEC', 'EXECUTE', 'SP_', 'XP_'
            ]
            
            data_lower = data.lower()
            for pattern in dangerous_patterns:
                if pattern in data_lower:
                    return False
            
            # Length check
            if len(data) > 10000:  # 10KB max
                return False
            
            return True
        
        elif input_type == 'email':
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(email_pattern, str(data)) is not None
        
        elif input_type == 'json':
            try:
                json.loads(data)
                return True
            except:
                return False
        
        return False
    
    def sanitize_output(self, data):
        """Sanitize output for XSS prevention"""
        if isinstance(data, str):
            # HTML entity encoding
            data = data.replace('&', '&amp;')
            data = data.replace('<', '&lt;')
            data = data.replace('>', '&gt;')
            data = data.replace('"', '&quot;')
            data = data.replace("'", '&#x27;')
        
        return data
    
    def log_security_event(self, event_type, details, severity='INFO'):
        """Log security events"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details,
            'severity': severity,
            'client_ip': getattr(request, 'remote_addr', 'unknown') if 'request' in globals() else 'unknown'
        }
        
        if severity == 'CRITICAL':
            self.logger.critical(f"SECURITY EVENT: {event}")
        elif severity == 'WARNING':
            self.logger.warning(f"SECURITY EVENT: {event}")
        else:
            self.logger.info(f"SECURITY EVENT: {event}")
        
        # Store in security events file
        with open('security_events.json', 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def check_ip_reputation(self, ip_address):
        """Check IP reputation"""
        # Check blacklist
        if ip_address in self.config['rate_limiting']['blacklist_ips']:
            return False
        
        # Check whitelist
        if ip_address in self.config['rate_limiting']['whitelist_ips']:
            return True
        
        # In production, integrate with threat intelligence services
        return True
    
    def generate_secure_headers(self):
        """Generate security headers"""
        return self.config['security_headers']
    
    def create_ssl_context(self):
        """Create SSL context for HTTPS"""
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        context.load_cert_chain('server.crt', 'server.key')
        
        return context

# Decorators for security
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        
        payload = security_framework.verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
        
        g.user = payload
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user') or g.user.get('role') != required_role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def rate_limit(limit=1000, burst=100):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            
            if not security_framework.check_rate_limit(client_ip):
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def csrf_protect(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE']:
            csrf_token = request.headers.get('X-CSRF-Token')
            session_token = session.get('csrf_token')
            
            if not csrf_token or not session_token:
                return jsonify({'error': 'CSRF token missing'}), 403
            
            if not security_framework.verify_csrf_token(csrf_token, session_token):
                return jsonify({'error': 'Invalid CSRF token'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

# Global security framework instance
security_framework = SecurityFramework()

if __name__ == '__main__':
    print("🛡️ STELLAR LOGIC AI SECURITY FRAMEWORK")
    print(f"🔐 Encryption: {security_framework.config['encryption']['algorithm']}")
    print(f"🔑 JWT Secret: {security_framework.config['authentication']['jwt_secret'][:10]}...")
    print(f"📊 Rate Limit: {security_framework.config['rate_limiting']['default_limit']}/hour")
    print(f"🛡️ CSRF Protection: {security_framework.config['csrf']['enabled']}")
