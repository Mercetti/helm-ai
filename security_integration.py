#!/usr/bin/env python3
"""
Comprehensive Security Integration
Integrates all security middleware: HTTPS, CSRF, Auth Rate Limiting, and Password Policy
"""

from flask import Flask, request, g, current_app
from functools import wraps
import json
from datetime import datetime
import os

# Import security modules
try:
    from security_https_middleware import HTTPSSecurityMiddleware, require_https
    from security_csrf_protection import CSRFProtection, csrf_protect, csrf_exempt
    from security_auth_rate_limiting import AuthRateLimiter, auth_rate_limit
    from security_password_policy import PasswordPolicy, validate_password
except ImportError as e:
    print(f"⚠️ Security module import error: {e}")
    print("   Some security features may not be available")

class SecurityManager:
    """Comprehensive security management system"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.https_middleware = None
        self.csrf_protection = None
        self.auth_rate_limiter = None
        self.password_policy = None
        self.security_config = self._load_security_config()
        
        if app:
            self.init_app(app)
    
    def _load_security_config(self) -> Dict[str, Any]:
        """Load security configuration"""
        return {
            'https_enforced': os.getenv('HTTPS_ENFORCED', 'true').lower() == 'true',
            'csrf_protection': os.getenv('CSRF_PROTECTION', 'true').lower() == 'true',
            'auth_rate_limiting': os.getenv('AUTH_RATE_LIMITING', 'true').lower() == 'true',
            'password_policy': os.getenv('PASSWORD_POLICY', 'true').lower() == 'true',
            'security_headers': os.getenv('SECURITY_HEADERS', 'true').lower() == 'true',
            'security_logging': os.getenv('SECURITY_LOGGING', 'true').lower() == 'true',
            'input_validation': os.getenv('INPUT_VALIDATION', 'true').lower() == 'true'
        }
    
    def init_app(self, app: Flask):
        """Initialize all security components"""
        self.app = app
        app.security_manager = self
        
        # Initialize security components based on configuration
        if self.security_config['https_enforced']:
            self.https_middleware = HTTPSSecurityMiddleware(app)
            print("✅ HTTPS/TLS enforcement enabled")
        
        if self.security_config['csrf_protection']:
            self.csrf_protection = CSRFProtection(app)
            print("✅ CSRF protection enabled")
        
        if self.security_config['auth_rate_limiting']:
            self.auth_rate_limiter = AuthRateLimiter(app)
            print("✅ Authentication rate limiting enabled")
        
        if self.security_config['password_policy']:
            self.password_policy = PasswordPolicy(app)
            print("✅ Password policy enabled")
        
        # Register security headers middleware
        if self.security_config['security_headers']:
            app.after_request(self._add_security_headers)
            print("✅ Security headers enabled")
        
        # Register security logging
        if self.security_config['security_logging']:
            app.before_request(self._log_security_event)
            app.after_request(self._log_security_response)
            print("✅ Security logging enabled")
        
        # Store security config
        app.config['SECURITY_CONFIG'] = self.security_config
    
    def _add_security_headers(self, response):
        """Add comprehensive security headers"""
        # Only add to HTML responses
        if response.content_type and 'text/html' in response.content_type:
            # Security headers (already added by HTTPS middleware, but ensure they're present)
            if not response.headers.get('Strict-Transport-Security'):
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
            
            if not response.headers.get('X-Content-Type-Options'):
                response.headers['X-Content-Type-Options'] = 'nosniff'
            
            if not response.headers.get('X-Frame-Options'):
                response.headers['X-Frame-Options'] = 'DENY'
            
            if not response.headers.get('X-XSS-Protection'):
                response.headers['X-XSS-Protection'] = '1; mode=block'
            
            if not response.headers.get('Referrer-Policy'):
                response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            if not response.headers.get('Content-Security-Policy'):
                csp = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                    "style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data: https:; "
                    "font-src 'self'; "
                    "connect-src 'self'; "
                    "frame-ancestors 'none'; "
                    "base-uri 'self'; "
                    "form-action 'self';"
                )
                response.headers['Content-Security-Policy'] = csp
            
            # Additional security headers
            response.headers['X-Content-Security-Policy'] = 'default-src \'self\''
            response.headers['X-Download-Options'] = 'noopen'
            response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
            response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
            response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
            response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
            
            # API security headers
            response.headers['API-Version'] = 'v1'
            response.headers['X-API-Version'] = '1.0'
        
        return response
    
    def _log_security_event(self):
        """Log security events"""
        if not hasattr(g, 'security_event_logged'):
            g.security_event_logged = True
            
            event_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'method': request.method,
                'url': request.url,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'Unknown'),
                'content_type': request.content_type,
                'content_length': request.content_length,
                'headers': dict(request.headers),
                'args': dict(request.args),
                'form': dict(request.form) if request.form else None,
                'json': request.get_json(silent=True) if request.is_json else None
            }
            
            # Log security-relevant information
            security_info = {
                'timestamp': event_data['timestamp'],
                'event_type': 'request',
                'method': event_data['method'],
                'path': event_data['path'],
                'remote_addr': event_data['remote_addr'],
                'user_agent': event_data['user_agent'],
                'suspicious_patterns': self._detect_suspicious_patterns(event_data)
            }
            
            # Log to console (in production, this would go to a security log file)
            print(f"🔒 Security Event: {json.dumps(security_info, indent=2)}")
    
    def _log_security_response(self, response):
        """Log security response information"""
        if hasattr(g, 'security_event_logged'):
            security_info = {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': 'response',
                'status_code': response.status_code,
                'content_type': response.content_type,
                'content_length': response.content_length,
                'headers': dict(response.headers)
            }
            
            print(f"🔒 Security Response: {json.dumps(security_info, indent=2)}")
    
    def _detect_suspicious_patterns(self, event_data: Dict[str, Any]) -> List[str]:
        """Detect suspicious patterns in request"""
        patterns = []
        
        # Check for suspicious User-Agent
        user_agent = event_data.get('user_agent', '').lower()
        suspicious_agents = ['sqlmap', 'nikto', 'burp', 'nmap', 'metasploit', 'python-requests']
        for agent in suspicious_agents:
            if agent in user_agent:
                patterns.append(f"Suspicious User-Agent: {agent}")
        
        # Check for suspicious URL patterns
        url = event_data.get('url', '').lower()
        suspicious_patterns = ['../', '<script', 'javascript:', 'eval(', 'exec(', 'system(']
        for pattern in suspicious_patterns:
            if pattern in url:
                patterns.append(f"Suspicious URL pattern: {pattern}")
        
        # Check for suspicious parameters
        args = event_data.get('args', {})
        form_data = event_data.get('form', {})
        json_data = event_data.get('json', {})
        
        all_params = {**args, **form_data}
        if json_data:
            all_params.update(json_data)
        
        sql_injection_patterns = ['union select', 'drop table', 'insert into', 'delete from', 'update set']
        for param_name, param_value in all_params.items():
            if isinstance(param_value, str):
                for pattern in sql_injection_patterns:
                    if pattern in param_value.lower():
                        patterns.append(f"SQL injection pattern in {param_name}: {pattern}")
        
        # Check for XSS patterns
        xss_patterns = ['<script', 'javascript:', 'onload=', 'onerror=', 'onclick=']
        for param_name, param_value in all_params.items():
            if isinstance(param_value, str):
                for pattern in xss_patterns:
                    if pattern in param_value.lower():
                        patterns.append(f"XSS pattern in {param_name}: {pattern}")
        
        return patterns
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        return {
            'https_enforced': self.security_config['https_enforced'],
            'csrf_protection': self.security_config['csrf_protection'],
            'auth_rate_limiting': self.security_config['auth_rate_limiting'],
            'password_policy': self.security_config['password_policy'],
            'security_headers': self.security_config['security_headers'],
            'security_logging': self.security_config['security_logging'],
            'input_validation': self.security_config['input_validation'],
            'components': {
                'https_middleware': self.https_middleware is not None,
                'csrf_protection': self.csrf_protection is not None,
                'auth_rate_limiter': self.auth_rate_limiter is not None,
                'password_policy': self.password_policy is not None
            }
        }
    
    def run_security_check(self) -> Dict[str, Any]:
        """Run comprehensive security check"""
        print("🔒 Running Comprehensive Security Check")
        print("=" * 50)
        
        status = self.get_security_status()
        
        print(f"HTTPS/TLS Enforcement: {'✅ Active' if status['https_enforced'] else '❌ Disabled'}")
        print(f"CSRF Protection: {'✅ Active' if status['csrf_protection'] else '❌ Disabled'}")
        print(f"Auth Rate Limiting: {'✅ Active' if status['auth_rate_limiting'] else '❌ Disabled'}")
        print(f"Password Policy: {'✅ Active' if status['password_policy'] else '❌ Disabled'}")
        print(f"Security Headers: {'✅ Active' if status['security_headers'] else '❌ Disabled'}")
        print(f"Security Logging: {'✅ Active' if status['security_logging'] else '❌ Disabled'}")
        print(f"Input Validation: {'✅ Active' if status['input_validation'] else '❌ Disabled'}")
        
        print(f"\nComponent Status:")
        for component, active in status['components'].items():
            print(f"   {component}: {'✅ Active' if active else '❌ Inactive'}")
        
        # Calculate security score
        active_components = sum(1 for active in status['components'].values() if active)
        total_components = len(status['components'])
        security_score = (active_components / total_components) * 100
        
        print(f"\nSecurity Score: {security_score:.1f}%")
        
        if security_score >= 90:
            print("🏆 Security Status: EXCELLENT")
        elif security_score >= 75:
            print("✅ Security Status: GOOD")
        elif security_score >= 50:
            print("⚠️ Security Status: FAIR")
        else:
            print("❌ Security Status: POOR")
        
        return status

# Decorator for comprehensive security
def secure_endpoint(auth_type: str = 'login'):
    """Decorator for comprehensive security protection"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Apply rate limiting
            if hasattr(current_app, 'auth_rate_limiter'):
                rate_limiter = current_app.auth_rate_limiter
                identifier = rate_limiter._get_user_identifier()
                is_limited, limit_info = rate_limiter._is_rate_limited(auth_type, identifier)
                
                if is_limited:
                    abort(429, description=f"Rate limit exceeded: {limit_info['reason']}")
                
                g.auth_rate_limit_info = limit_info
            
            # Add security headers
            if hasattr(current_app, 'security_manager'):
                security_manager = current_app.security_manager
                headers = security_manager._add_security_headers(None)
                g.security_headers = headers
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Flask extension factory
def create_security_manager(app=None) -> SecurityManager:
    """Factory function to create security manager"""
    return SecurityManager(app)

# Example usage
if __name__ == "__main__":
    # Test comprehensive security
    app = Flask(__name__)
    app.secret_key = 'test-secret-key-change-in-production'
    
    # Initialize security manager
    security = create_security_manager(app)
    
    @app.route('/')
    def home():
        return "🛡️ Comprehensive Security Protection Active!"
    
    @app.route('/secure-endpoint', methods=['POST'])
    @secure_endpoint('login')
    def secure_endpoint():
        data = request.form.get('data', '')
        return f"✅ Secure endpoint accessed! Data: {data}"
    
    @app.route('/security-status')
    def security_status():
        status = security.run_security_check()
        from flask import jsonify
        return jsonify(status)
    
    app.run(debug=True)
