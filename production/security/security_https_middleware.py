#!/usr/bin/env python3
"""
HTTPS/TLS Security Middleware
Enforces HTTPS/TLS for all API endpoints with proper SSL configuration
"""

import os
from flask import Flask, request, redirect, url_for
from functools import wraps
from werkzeug.middleware.proxy_fix import ProxyFix
import ssl
from datetime import datetime, timedelta

class HTTPSSecurityMiddleware:
    """HTTPS/TLS enforcement middleware for Flask applications"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.ssl_context = None
        self.hsts_max_age = 31536000  # 1 year
        self.hsts_include_subdomains = True
        self.hsts_preload = True
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize HTTPS security middleware"""
        self.app = app
        
        # Configure proxy fix for proper HTTPS detection
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
        
        # Register before request handler
        app.before_request(self._enforce_https)
        
        # Register after request handler for security headers
        app.after_request(self._add_security_headers)
        
        # Configure SSL context
        self._configure_ssl_context()
        
        # Store middleware instance
        app.https_security = self
    
    def _configure_ssl_context(self):
        """Configure SSL context with strong security settings"""
        try:
            # Create SSL context with strong settings
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            
            # Set strong cipher suites
            self.ssl_context.set_ciphers('ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384')
            
            # Disable weak protocols
            self.ssl_context.options |= ssl.OP_NO_SSLv2
            self.ssl_context.options |= ssl.OP_NO_SSLv3
            self.ssl_context.options |= ssl.OP_NO_TLSv1
            self.ssl_context.options |= ssl.OP_NO_TLSv1_1
            
            # Enable forward secrecy
            self.ssl_context.options |= ssl.OP_NO_COMPRESSION
            
            # Set minimum TLS version
            self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
            
            # Load certificates if available
            cert_file = os.getenv('SSL_CERT_FILE', 'certs/server.crt')
            key_file = os.getenv('SSL_KEY_FILE', 'certs/server.key')
            ca_file = os.getenv('SSL_CA_FILE', 'certs/ca.crt')
            
            if os.path.exists(cert_file) and os.path.exists(key_file):
                self.ssl_context.load_cert_chain(cert_file, key_file, ca_file)
                print(f"✅ SSL certificates loaded from {cert_file}")
            else:
                print(f"⚠️ SSL certificates not found at {cert_file}/{key_file}")
                print("   Using self-signed certificate for development")
                self._create_self_signed_cert()
                
        except Exception as e:
            print(f"❌ Error configuring SSL context: {e}")
            self.ssl_context = None
    
    def _create_self_signed_cert(self):
        """Create self-signed certificate for development"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            import ipaddress
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Helm AI"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.DNSName("127.0.0.1"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                    x509.IPAddress(ipaddress.IPv6Address("::1")),
                ])
            ).sign(private_key, hashes.SHA256())
            
            # Ensure certs directory exists
            os.makedirs('certs', exist_ok=True)
            
            # Save certificate
            with open('certs/server.crt', 'wb') as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # Save private key
            with open('certs/server.key', 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Load into SSL context
            self.ssl_context.load_cert_chain('certs/server.crt', 'certs/server.key')
            
            print("✅ Self-signed certificate created for development")
            
        except ImportError:
            print("⚠️ Cryptography library not available, skipping self-signed cert")
        except Exception as e:
            print(f"❌ Error creating self-signed certificate: {e}")
    
    def _enforce_https(self):
        """Enforce HTTPS for all requests"""
        # Skip enforcement for health checks and static files
        if request.path.startswith('/health') or request.path.startswith('/static'):
            return None
        
        # Check if request is secure
        if not request.is_secure:
            # Check if we're behind a proxy
            if request.headers.get('X-Forwarded-Proto') != 'https':
                # Redirect to HTTPS
                url = request.url.replace('http://', 'https://', 1)
                return redirect(url, code=301)
        
        return None
    
    def _add_security_headers(self, response):
        """Add security headers to response"""
        # Strict Transport Security (HSTS)
        if self.hsts_max_age:
            hsts_value = f"max-age={self.hsts_max_age}"
            if self.hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            if self.hsts_preload:
                hsts_value += "; preload"
            response.headers['Strict-Transport-Security'] = hsts_value
        
        # X-Content-Type-Options
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options
        response.headers['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
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
        
        # Permissions Policy
        permissions_policy = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        response.headers['Permissions-Policy'] = permissions_policy
        
        return response
    
    def get_ssl_context(self):
        """Get configured SSL context"""
        return self.ssl_context
    
    def run_https_server(self, app: Flask, host='0.0.0.0', port=5000, debug=False):
        """Run Flask app with HTTPS"""
        if self.ssl_context:
            print(f"🔒 Starting HTTPS server on https://{host}:{port}")
            app.run(
                host=host,
                port=port,
                debug=debug,
                ssl_context=self.ssl_context,
                threaded=True
            )
        else:
            print("❌ SSL context not available, falling back to HTTP")
            print("   ⚠️ This is not recommended for production!")
            app.run(host=host, port=port, debug=debug)

# Decorator for requiring HTTPS on specific routes
def require_https(f):
    """Decorator to require HTTPS for specific routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and request.headers.get('X-Forwarded-Proto') != 'https':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
        return f(*args, **kwargs)
    return decorated_function

# Flask extension factory
def create_https_security(app: Flask = None) -> HTTPSSecurityMiddleware:
    """Factory function to create HTTPS security middleware"""
    return HTTPSSecurityMiddleware(app)

# Example usage
if __name__ == "__main__":
    # Test HTTPS security middleware
    app = Flask(__name__)
    
    # Initialize HTTPS security
    https_security = create_https_security(app)
    
    @app.route('/')
    def home():
        return "🔒 Secure HTTPS Connection Active!"
    
    @app.route('/test')
    @require_https
    def test_secure():
        return "🛡️ This route requires HTTPS!"
    
    @app.route('/health')
    def health():
        return {"status": "healthy", "https": "enforced"}
    
    # Run with HTTPS
    https_security.run_https_server(app, host='localhost', port=5000)
