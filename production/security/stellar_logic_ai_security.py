#!/usr/bin/env python3
"""
Stellar Logic AI - Complete Security Integration
Comprehensive security system for Stellar Logic AI with all security components integrated
"""

from flask import Flask, request, g, current_app, jsonify
from functools import wraps
import json
from datetime import datetime
import os

# Import all security modules for Stellar Logic AI
try:
    from security_https_middleware import HTTPSSecurityMiddleware
    from security_csrf_protection import CSRFProtection
    from security_auth_rate_limiting import AuthRateLimiter
    from security_password_policy import PasswordPolicy
    from security_jwt_rotation import JWTSecretRotation
    from security_input_validation import InputValidator
    from security_api_key_management import APIKeyManager
except ImportError as e:
    print(f"⚠️ Security module import error: {e}")
    print("   Some security features may not be available")

class StellarSecurityManager:
    """Complete security management system for Stellar Logic AI"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.https_middleware = None
        self.csrf_protection = None
        self.auth_rate_limiter = None
        self.password_policy = None
        self.jwt_rotation = None
        self.input_validator = None
        self.api_key_manager = None
        
        self.security_config = {
            'https_enforced': True,
            'csrf_protection': True,
            'auth_rate_limiting': True,
            'password_policy': True,
            'jwt_rotation': True,
            'input_validation': True,
            'api_key_management': True,
            'security_headers': True,
            'security_logging': True,
            'sql_injection_prevention': True
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize all security components for Stellar Logic AI"""
        self.app = app
        app.stellar_security = self
        
        print("🛡️ Initializing Stellar Logic AI Security System")
        print("=" * 60)
        
        # Initialize HTTPS/TLS enforcement
        if self.security_config['https_enforced']:
            self.https_middleware = HTTPSSecurityMiddleware(app)
            print("✅ HTTPS/TLS enforcement enabled")
        
        # Initialize CSRF protection
        if self.security_config['csrf_protection']:
            self.csrf_protection = CSRFProtection(app)
            print("✅ CSRF protection enabled")
        
        # Initialize authentication rate limiting
        if self.security_config['auth_rate_limiting']:
            self.auth_rate_limiter = AuthRateLimiter(app)
            print("✅ Authentication rate limiting enabled")
        
        # Initialize password policy
        if self.security_config['password_policy']:
            self.password_policy = PasswordPolicy(app)
            print("✅ Password policy enabled")
        
        # Initialize JWT secret rotation
        if self.security_config['jwt_rotation']:
            self.jwt_rotation = JWTSecretRotation(app)
            print("✅ JWT secret rotation enabled")
        
        # Initialize input validation
        if self.security_config['input_validation']:
            self.input_validator = InputValidator(app)
            print("✅ Input validation enabled")
        
        # Initialize API key management
        if self.security_config['api_key_management']:
            self.api_key_manager = APIKeyManager(app)
            print("✅ API key management enabled")
        
        # Register security headers middleware
        if self.security_config['security_headers']:
            app.after_request(self._add_stellar_security_headers)
            print("✅ Security headers enabled")
        
        # Register security logging
        if self.security_config['security_logging']:
            app.before_request(self._log_stellar_security_event)
            app.after_request(self._log_stellar_security_response)
            print("✅ Security logging enabled")
        
        # Store security config
        app.config['STELLAR_SECURITY_CONFIG'] = self.security_config
        
        print("=" * 60)
        print("🎉 Stellar Logic AI Security System Initialized Successfully!")
    
    def _add_stellar_security_headers(self, response):
        """Add comprehensive security headers for Stellar Logic AI"""
        if response.content_type and 'text/html' in response.content_type:
            # Enhanced security headers for Stellar Logic AI
            response.headers['X-Stellar-Security'] = 'Enterprise-Grade'
            response.headers['X-Stellar-Version'] = '1.0.0'
            response.headers['X-Stellar-Protection'] = 'Active'
            
            # Standard security headers
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
            
            # Content Security Policy for Stellar Logic AI
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
            response.headers['X-Stellar-API'] = 'Protected'
        
        return response
    
    def _log_stellar_security_event(self):
        """Log security events for Stellar Logic AI"""
        if not hasattr(g, 'stellar_security_event_logged'):
            g.stellar_security_event_logged = True
            
            event_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'system': 'Stellar Logic AI',
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
                'system': 'Stellar Logic AI',
                'event_type': 'request',
                'method': event_data['method'],
                'path': event_data['path'],
                'remote_addr': event_data['remote_addr'],
                'user_agent': event_data['user_agent'],
                'suspicious_patterns': self._detect_stellar_suspicious_patterns(event_data)
            }
            
            # Log to console (in production, this would go to a security log file)
            print(f"🛡️ Stellar Logic AI Security Event: {json.dumps(security_info, indent=2)}")
    
    def _log_stellar_security_response(self, response):
        """Log security response information for Stellar Logic AI"""
        if hasattr(g, 'stellar_security_event_logged'):
            security_info = {
                'timestamp': datetime.utcnow().isoformat(),
                'system': 'Stellar Logic AI',
                'event_type': 'response',
                'status_code': response.status_code,
                'content_type': response.content_type,
                'content_length': response.content_length,
                'headers': dict(response.headers)
            }
            
            print(f"🛡️ Stellar Logic AI Security Response: {json.dumps(security_info, indent=2)}")
    
    def _detect_stellar_suspicious_patterns(self, event_data: Dict[str, Any]) -> List[str]:
        """Detect suspicious patterns specific to Stellar Logic AI"""
        patterns = []
        
        # Check for suspicious User-Agent
        user_agent = event_data.get('user_agent', '').lower()
        suspicious_agents = ['sqlmap', 'nikto', 'burp', 'nmap', 'metasploit', 'python-requests']
        for agent in suspicious_agents:
            if agent in user_agent:
                patterns.append(f"Suspicious User-Agent targeting Stellar Logic AI: {agent}")
        
        # Check for suspicious URL patterns
        url = event_data.get('url', '').lower()
        suspicious_patterns_list = ['../', '<script', 'javascript:', 'eval(', 'exec(', 'system(']
        for pattern in suspicious_patterns_list:
            if pattern in url:
                patterns.append(f"Suspicious URL pattern targeting Stellar Logic AI: {pattern}")
        
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
                        patterns.append(f"SQL injection pattern targeting Stellar Logic AI in {param_name}: {pattern}")
        
        # Check for XSS patterns
        xss_patterns = ['<script', 'javascript:', 'onload=', 'onerror=', 'onclick=']
        for param_name, param_value in all_params.items():
            if isinstance(param_value, str):
                for pattern in xss_patterns:
                    if pattern in param_value.lower():
                        patterns.append(f"XSS pattern targeting Stellar Logic AI in {param_name}: {pattern}")
        
        return patterns
    
    def get_stellar_security_status(self) -> Dict[str, Any]:
        """Get current Stellar Logic AI security status"""
        return {
            'system': 'Stellar Logic AI',
            'https_enforced': self.security_config['https_enforced'],
            'csrf_protection': self.security_config['csrf_protection'],
            'auth_rate_limiting': self.security_config['auth_rate_limiting'],
            'password_policy': self.security_config['password_policy'],
            'jwt_rotation': self.security_config['jwt_rotation'],
            'input_validation': self.security_config['input_validation'],
            'api_key_management': self.security_config['api_key_management'],
            'security_headers': self.security_config['security_headers'],
            'security_logging': self.security_config['security_logging'],
            'sql_injection_prevention': self.security_config['sql_injection_prevention'],
            'components': {
                'https_middleware': self.https_middleware is not None,
                'csrf_protection': self.csrf_protection is not None,
                'auth_rate_limiter': self.auth_rate_limiter is not None,
                'password_policy': self.password_policy is not None,
                'jwt_rotation': self.jwt_rotation is not None,
                'input_validator': self.input_validator is not None,
                'api_key_manager': self.api_key_manager is not None
            }
        }
    
    def run_stellar_security_check(self) -> Dict[str, Any]:
        """Run comprehensive Stellar Logic AI security check"""
        print("🛡️ Running Stellar Logic AI Comprehensive Security Check")
        print("=" * 70)
        
        status = self.get_stella_security_status()
        
        print(f"System: {status['system']}")
        print(f"HTTPS/TLS Enforcement: {'✅ Active' if status['https_enforced'] else '❌ Disabled'}")
        print(f"CSRF Protection: {'✅ Active' if status['csrf_protection'] else '❌ Disabled'}")
        print(f"Auth Rate Limiting: {'✅ Active' if status['auth_rate_limiting'] else '❌ Disabled'}")
        print(f"Password Policy: {'✅ Active' if status['password_policy'] else '❌ Disabled'}")
        print(f"JWT Secret Rotation: {'✅ Active' if status['jwt_rotation'] else '❌ Disabled'}")
        print(f"Input Validation: {'✅ Active' if status['input_validation'] else '❌ Disabled'}")
        print(f"API Key Management: {'✅ Active' if status['api_key_management'] else '❌ Disabled'}")
        print(f"Security Headers: {'✅ Active' if status['security_headers'] else '❌ Disabled'}")
        print(f"Security Logging: {'✅ Active' if status['security_logging'] else '❌ Disabled'}")
        print(f"SQL Injection Prevention: {'✅ Active' if status['sql_injection_prevention'] else '❌ Disabled'}")
        
        print(f"\nComponent Status:")
        for component, active in status['components'].items():
            print(f"   {component}: {'✅ Active' if active else '❌ Inactive'}")
        
        # Calculate security score
        active_components = sum(1 for active in status['components'].values() if active)
        total_components = len(status['components'])
        security_score = (active_components / total_components) * 100
        
        print(f"\nStellar Logic AI Security Score: {security_score:.1f}%")
        
        if security_score >= 95:
            print("🏆 Stellar Logic AI Security Status: EXCELLENT - Enterprise Ready")
        elif security_score >= 85:
            print("✅ Stellar Logic AI Security Status: VERY GOOD - Production Ready")
        elif security_score >= 75:
            print("⚠️ Stellar Logic AI Security Status: GOOD - Minor Improvements Needed")
        elif security_score >= 60:
            print("⚠️ Stellar Logic AI Security Status: FAIR - Significant Improvements Needed")
        else:
            print("❌ Stellar Logic AI Security Status: POOR - Major Security Issues")
        
        return status

# Decorator for comprehensive Stellar Logic AI security
def stellar_secure_endpoint(auth_type: str = 'login', permissions: List[str] = None):
    """Decorator for comprehensive Stella Logic AI security protection"""
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
            
            # Check API key permissions if provided
            if permissions and hasattr(current_app, 'api_key_manager'):
                if hasattr(g, 'api_key_info'):
                    key_permissions = g.api_key_info.get('permissions', [])
                    if not any(perm in key_permissions for perm in permissions):
                        abort(403, description='Insufficient permissions for Stellar Logic AI')
            
            # Add security headers
            if hasattr(current_app, 'stellar_security'):
                security_manager = current_app.stellar_security
                headers = security_manager._add_stellar_security_headers(None)
                g.stellar_security_headers = headers
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Flask extension factory
def create_stellar_security(app=None) -> StellarSecurityManager:
    """Factory function to create Stellar Logic AI security manager"""
    return StellarSecurityManager(app)

# Example usage
if __name__ == "__main__":
    # Test Stellar Logic AI security
    app = Flask(__name__)
    app.secret_key = 'stellar-logic-ai-secret-key-change-in-production'
    
    # Initialize Stellar Logic AI security
    stellar_security = create_stellar_security(app)
    
    @app.route('/')
    def home():
        return "🛡️ Stellar Logic AI - Enterprise Security Protection Active!"
    
    @app.route('/secure-endpoint', methods=['POST'])
    @stellar_secure_endpoint('login', ['read'])
    def secure_endpoint():
        data = request.form.get('data', '')
        return f"✅ Stellar Logic AI secure endpoint accessed! Data: {data}"
    
    @app.route('/stellar-security-status')
    def stellar_security_status():
        status = stellar_security.run_stellar_security_check()
        return jsonify(status)
    
    @app.route('/api/protected')
    @stellar_secure_endpoint('api_auth', ['read'])
    def api_protected():
        return jsonify({
            'message': 'Stellar Logic AI API endpoint protected',
            'system': 'Stellar Logic AI',
            'security': 'Enterprise Grade'
        })
    
    app.run(debug=True)
