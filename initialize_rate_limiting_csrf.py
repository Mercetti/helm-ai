#!/usr/bin/env python3
"""
Stellar Logic AI - Rate Limiting and CSRF Protection Initialization
Initialize and configure rate limiting and CSRF protection for production
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

class RateLimitingCSRFInitializer:
    """Initialize rate limiting and CSRF protection for Stellar Logic AI"""
    
    def __init__(self):
        self.base_path = "c:/Users/merce/Documents/helm-ai"
        self.production_path = "c:/Users/merce/Documents/helm-ai/production"
        self.config_path = os.path.join(self.production_path, "config")
        
        # Rate limiting configuration
        self.rate_limit_config = {
            "enabled": True,
            "default_limits": {
                "requests_per_minute": 60,
                "requests_per_hour": 1000,
                "requests_per_day": 10000
            },
            "endpoint_limits": {
                "/login": {"requests_per_minute": 5, "requests_per_hour": 20},
                "/register": {"requests_per_minute": 3, "requests_per_hour": 10},
                "/api/auth": {"requests_per_minute": 10, "requests_per_hour": 100},
                "/api/data": {"requests_per_minute": 30, "requests_per_hour": 500},
                "/security-status": {"requests_per_minute": 20, "requests_per_hour": 200}
            },
            "ip_whitelist": ["127.0.0.1", "::1"],
            "penalty_threshold": 100,
            "penalty_duration": 300,  # 5 minutes
            "cleanup_interval": 3600  # 1 hour
        }
        
        # CSRF protection configuration
        self.csrf_config = {
            "enabled": True,
            "token_length": 32,
            "token_expiry": 3600,  # 1 hour
            "refresh_threshold": 300,  # 5 minutes before expiry
            "secure_cookie": True,
            "http_only": True,
            "same_site": "Strict",
            "exempt_endpoints": ["/health", "/security-status"],
            "header_name": "X-CSRF-Token",
            "form_field_name": "csrf_token",
            "cookie_name": "stellar_csrf_token"
        }
    
    def initialize_rate_limiting(self):
        """Initialize rate limiting configuration"""
        print("Initializing Rate Limiting Configuration...")
        
        # Create rate limiting configuration file
        rate_limit_file = os.path.join(self.config_path, "rate_limiting_config.json")
        
        with open(rate_limit_file, 'w') as f:
            json.dump(self.rate_limit_config, f, indent=2)
        
        print(f"✅ Rate limiting configuration saved")
        
        # Create rate limiting storage structure
        storage_dir = os.path.join(self.production_path, "storage", "rate_limiting")
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize rate limiting data files
        rate_limit_data = {
            "ip_requests": {},
            "endpoint_requests": {},
            "blocked_ips": {},
            "penalties": {},
            "statistics": {
                "total_requests": 0,
                "blocked_requests": 0,
                "active_ips": 0,
                "last_cleanup": datetime.now().isoformat()
            }
        }
        
        data_file = os.path.join(storage_dir, "rate_limit_data.json")
        with open(data_file, 'w') as f:
            json.dump(rate_limit_data, f, indent=2)
        
        print(f"✅ Rate limiting data storage initialized")
        
        return True
    
    def initialize_csrf_protection(self):
        """Initialize CSRF protection configuration"""
        print("Initializing CSRF Protection Configuration...")
        
        # Create CSRF protection configuration file
        csrf_file = os.path.join(self.config_path, "csrf_protection_config.json")
        
        with open(csrf_file, 'w') as f:
            json.dump(self.csrf_config, f, indent=2)
        
        print(f"✅ CSRF protection configuration saved")
        
        # Create CSRF token storage structure
        storage_dir = os.path.join(self.production_path, "storage", "csrf")
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize CSRF token data
        csrf_data = {
            "active_tokens": {},
            "token_statistics": {
                "tokens_generated": 0,
                "tokens_validated": 0,
                "tokens_expired": 0,
                "validation_failures": 0,
                "last_cleanup": datetime.now().isoformat()
            }
        }
        
        data_file = os.path.join(storage_dir, "csrf_data.json")
        with open(data_file, 'w') as f:
            json.dump(csrf_data, f, indent=2)
        
        print(f"✅ CSRF token storage initialized")
        
        return True
    
    def create_rate_limiting_middleware(self):
        """Create rate limiting middleware script"""
        print("Creating Rate Limiting Middleware...")
        
        middleware_script = """#!/usr/bin/env python3
import json
import time
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Any

class RateLimitingMiddleware:
    def __init__(self, app=None):
        self.app = app
        self.config_file = "production/config/rate_limiting_config.json"
        self.data_file = "production/storage/rate_limiting/rate_limit_data.json"
        self.load_configuration()
        self.load_data()
        
    def load_configuration(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {"enabled": False}
    
    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        except:
            self.data = {"ip_requests": {}, "blocked_ips": {}, "statistics": {}}
    
    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except:
            pass
    
    def is_rate_limited(self, ip_address: str, endpoint: str) -> Dict[str, Any]:
        if not self.config.get("enabled", False):
            return {"allowed": True, "reason": "Rate limiting disabled"}
        
        current_time = datetime.now()
        
        # Check if IP is blocked
        if ip_address in self.data.get("blocked_ips", {}):
            blocked_until = datetime.fromisoformat(self.data["blocked_ips"][ip_address])
            if current_time < blocked_until:
                return {"allowed": False, "reason": "IP blocked", "retry_after": int((blocked_until - current_time).total_seconds())}
            else:
                # Unblock IP
                del self.data["blocked_ips"][ip_address]
        
        # Get limits for this endpoint
        endpoint_limits = self.config.get("endpoint_limits", {}).get(endpoint, self.config.get("default_limits", {}))
        
        # Check IP-based limits
        ip_requests = self.data.get("ip_requests", {}).get(ip_address, {})
        
        for period, limit in endpoint_limits.items():
            if period == "requests_per_minute":
                window = timedelta(minutes=1)
            elif period == "requests_per_hour":
                window = timedelta(hours=1)
            elif period == "requests_per_day":
                window = timedelta(days=1)
            else:
                continue
            
            # Count requests in window
            requests_in_window = 0
            for timestamp in ip_requests.get(period, []):
                request_time = datetime.fromisoformat(timestamp)
                if current_time - request_time <= window:
                    requests_in_window += 1
            
            if requests_in_window >= limit:
                # Apply penalty if threshold exceeded
                penalty_threshold = self.config.get("penalty_threshold", 100)
                if requests_in_window >= penalty_threshold:
                    penalty_duration = self.config.get("penalty_duration", 300)
                    blocked_until = current_time + timedelta(seconds=penalty_duration)
                    self.data["blocked_ips"][ip_address] = blocked_until.isoformat()
                    self.save_data()
                    return {"allowed": False, "reason": "IP blocked for excessive requests", "retry_after": penalty_duration}
                
                return {"allowed": False, "reason": f"Rate limit exceeded: {period}", "retry_after": int(window.total_seconds())}
        
        return {"allowed": True, "reason": "Request allowed"}
    
    def record_request(self, ip_address: str, endpoint: str):
        if not self.config.get("enabled", False):
            return
        
        current_time = datetime.now().isoformat()
        
        # Update IP requests
        if "ip_requests" not in self.data:
            self.data["ip_requests"] = {}
        
        if ip_address not in self.data["ip_requests"]:
            self.data["ip_requests"][ip_address] = {
                "requests_per_minute": [],
                "requests_per_hour": [],
                "requests_per_day": []
            }
        
        # Add current request to all time windows
        for period in ["requests_per_minute", "requests_per_hour", "requests_per_day"]:
            self.data["ip_requests"][ip_address][period].append(current_time)
        
        # Update statistics
        if "statistics" not in self.data:
            self.data["statistics"] = {}
        
        self.data["statistics"]["total_requests"] = self.data["statistics"].get("total_requests", 0) + 1
        self.data["statistics"]["active_ips"] = len(self.data["ip_requests"])
        self.data["statistics"]["last_request"] = current_time
        
        self.save_data()
    
    def cleanup_old_data(self):
        current_time = datetime.now()
        cleanup_interval = self.config.get("cleanup_interval", 3600)
        last_cleanup = self.data.get("statistics", {}).get("last_cleanup")
        
        if last_cleanup:
            last_cleanup_time = datetime.fromisoformat(last_cleanup)
            if current_time - last_cleanup_time < timedelta(seconds=cleanup_interval):
                return
        
        # Clean up old request records
        for ip_address, ip_data in self.data.get("ip_requests", {}).items():
            for period, requests in ip_data.items():
                if period == "requests_per_minute":
                    window = timedelta(minutes=5)  # Keep 5 minutes
                elif period == "requests_per_hour":
                    window = timedelta(hours=2)  # Keep 2 hours
                elif period == "requests_per_day":
                    window = timedelta(days=2)  # Keep 2 days
                else:
                    continue
                
                # Filter old requests
                filtered_requests = []
                for timestamp in requests:
                    request_time = datetime.fromisoformat(timestamp)
                    if current_time - request_time <= window:
                        filtered_requests.append(timestamp)
                
                ip_data[period] = filtered_requests
        
        # Clean up blocked IPs
        blocked_ips = self.data.get("blocked_ips", {})
        for ip_address, blocked_until in list(blocked_ips.items()):
            if datetime.fromisoformat(blocked_until) < current_time:
                del blocked_ips[ip_address]
        
        # Update cleanup time
        self.data["statistics"]["last_cleanup"] = current_time.isoformat()
        self.save_data()
    
    def get_statistics(self) -> Dict[str, Any]:
        return self.data.get("statistics", {})
"""
        
        middleware_path = os.path.join(self.production_path, "middleware", "rate_limiting_middleware.py")
        os.makedirs(os.path.dirname(middleware_path), exist_ok=True)
        
        with open(middleware_path, 'w') as f:
            f.write(middleware_script)
        
        print(f"✅ Rate limiting middleware created")
        
        return True
    
    def create_csrf_middleware(self):
        """Create CSRF protection middleware script"""
        print("Creating CSRF Protection Middleware...")
        
        middleware_script = """#!/usr/bin/env python3
import json
import secrets
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class CSRFProtectionMiddleware:
    def __init__(self, app=None):
        self.app = app
        self.config_file = "production/config/csrf_protection_config.json"
        self.data_file = "production/storage/csrf/csrf_data.json"
        self.load_configuration()
        self.load_data()
        
    def load_configuration(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {"enabled": False}
    
    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        except:
            self.data = {"active_tokens": {}, "token_statistics": {}}
    
    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except:
            pass
    
    def generate_token(self, session_id: str = None) -> str:
        if not self.config.get("enabled", False):
            return ""
        
        token = secrets.token_urlsafe(self.config.get("token_length", 32))
        current_time = datetime.now()
        expiry = current_time + timedelta(seconds=self.config.get("token_expiry", 3600))
        
        token_data = {
            "token": token,
            "created_at": current_time.isoformat(),
            "expires_at": expiry.isoformat(),
            "session_id": session_id,
            "used": False
        }
        
        # Store token
        if "active_tokens" not in self.data:
            self.data["active_tokens"] = {}
        
        self.data["active_tokens"][token] = token_data
        
        # Update statistics
        if "token_statistics" not in self.data:
            self.data["token_statistics"] = {}
        
        self.data["token_statistics"]["tokens_generated"] = self.data["token_statistics"].get("tokens_generated", 0) + 1
        self.data["token_statistics"]["last_token_generated"] = current_time.isoformat()
        
        self.save_data()
        return token
    
    def validate_token(self, token: str, session_id: str = None) -> Dict[str, Any]:
        if not self.config.get("enabled", False):
            return {"valid": True, "reason": "CSRF protection disabled"}
        
        if not token:
            return {"valid": False, "reason": "No token provided"}
        
        # Check if token exists
        active_tokens = self.data.get("active_tokens", {})
        if token not in active_tokens:
            return {"valid": False, "reason": "Invalid token"}
        
        token_data = active_tokens[token]
        current_time = datetime.now()
        
        # Check if token has expired
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        if current_time > expires_at:
            # Remove expired token
            del active_tokens[token]
            self.data["token_statistics"]["tokens_expired"] = self.data["token_statistics"].get("tokens_expired", 0) + 1
            self.save_data()
            return {"valid": False, "reason": "Token expired"}
        
        # Check session ID if provided
        if session_id and token_data.get("session_id") and token_data["session_id"] != session_id:
            return {"valid": False, "reason": "Session mismatch"}
        
        # Mark token as used (optional one-time use)
        token_data["used"] = True
        
        # Update statistics
        self.data["token_statistics"]["tokens_validated"] = self.data["token_statistics"].get("tokens_validated", 0) + 1
        
        self.save_data()
        return {"valid": True, "reason": "Token valid"}
    
    def is_endpoint_exempt(self, endpoint: str) -> bool:
        exempt_endpoints = self.config.get("exempt_endpoints", [])
        return endpoint in exempt_endpoints
    
    def cleanup_expired_tokens(self):
        current_time = datetime.now()
        expired_tokens = []
        
        for token, token_data in self.data.get("active_tokens", {}).items():
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            if current_time > expires_at:
                expired_tokens.append(token)
        
        # Remove expired tokens
        for token in expired_tokens:
            del self.data["active_tokens"][token]
        
        if expired_tokens:
            self.data["token_statistics"]["tokens_expired"] = self.data["token_statistics"].get("tokens_expired", 0) + len(expired_tokens)
            self.data["token_statistics"]["last_cleanup"] = current_time.isoformat()
            self.save_data()
    
    def get_statistics(self) -> Dict[str, Any]:
        stats = self.data.get("token_statistics", {})
        stats["active_tokens"] = len(self.data.get("active_tokens", {}))
        return stats
    
    def refresh_token(self, old_token: str, session_id: str = None) -> Optional[str]:
        if not self.config.get("enabled", False):
            return None
        
        # Validate old token
        validation = self.validate_token(old_token, session_id)
        if not validation["valid"]:
            return None
        
        # Generate new token
        new_token = self.generate_token(session_id)
        
        # Invalidate old token
        if old_token in self.data.get("active_tokens", {}):
            del self.data["active_tokens"][old_token]
        
        return new_token
"""
        
        middleware_path = os.path.join(self.production_path, "middleware", "csrf_middleware.py")
        
        with open(middleware_path, 'w') as f:
            f.write(middleware_script)
        
        print(f"✅ CSRF protection middleware created")
        
        return True
    
    def create_integration_script(self):
        """Create integration script for rate limiting and CSRF"""
        print("Creating Rate Limiting and CSRF Integration Script...")
        
        integration_script = """#!/usr/bin/env python3
import os
import sys
from datetime import datetime

# Add production paths
sys.path.insert(0, 'production/middleware')
sys.path.insert(0, 'production/security')

def initialize_security_middleware():
    print("Initializing Stellar Logic AI Security Middleware...")
    
    try:
        # Import middleware classes
        from rate_limiting_middleware import RateLimitingMiddleware
        from csrf_middleware import CSRFProtectionMiddleware
        
        # Initialize middleware
        rate_limiter = RateLimitingMiddleware()
        csrf_protection = CSRFProtectionMiddleware()
        
        print("Rate limiting middleware initialized")
        print("CSRF protection middleware initialized")
        
        # Test token generation
        test_token = csrf_protection.generate_token("test_session")
        print(f"Generated test CSRF token: {test_token[:16]}...")
        
        # Test token validation
        validation = csrf_protection.validate_token(test_token, "test_session")
        print(f"Token validation: {validation['valid']}")
        
        # Test rate limiting
        rate_check = rate_limiter.is_rate_limited("127.0.0.1", "/test")
        print(f"Rate limiting check: {rate_check['allowed']}")
        
        # Get statistics
        rate_stats = rate_limiter.get_statistics()
        csrf_stats = csrf_protection.get_statistics()
        
        print(f"Rate limiting stats: {rate_stats}")
        print(f"CSRF protection stats: {csrf_stats}")
        
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Initialization error: {e}")
        return False

def create_flask_integration_example():
    print("Creating Flask integration example...")
    
    flask_example = '''
from flask import Flask, request, jsonify, session
from rate_limiting_middleware import RateLimitingMiddleware
from csrf_middleware import CSRFProtectionMiddleware

app = Flask(__name__)
app.secret_key = 'stellar-logic-ai-secret-key'

# Initialize security middleware
rate_limiter = RateLimitingMiddleware(app)
csrf_protection = CSRFProtectionMiddleware(app)

@app.before_request
def security_check():
    # Get client IP
    client_ip = request.remote_addr
    endpoint = request.endpoint
    
    # Rate limiting check
    rate_result = rate_limiter.is_rate_limited(client_ip, endpoint)
    if not rate_result['allowed']:
        return jsonify({'error': 'Rate limit exceeded', 'reason': rate_result['reason']}), 429
    
    # CSRF protection for POST/PUT/DELETE requests
    if request.method in ['POST', 'PUT', 'DELETE']:
        if not csrf_protection.is_endpoint_exempt(request.path):
            # Get token from header or form
            token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
            
            validation = csrf_protection.validate_token(token, session.get('session_id'))
            if not validation['valid']:
                return jsonify({'error': 'CSRF token invalid', 'reason': validation['reason']}), 403
    
    # Record request for rate limiting
    rate_limiter.record_request(client_ip, endpoint)

@app.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    session_id = session.get('session_id') or 'anonymous'
    token = csrf_protection.generate_token(session_id)
    return jsonify({'csrf_token': token})

@app.route('/api/protected', methods=['POST'])
def protected_endpoint():
    return jsonify({'message': 'Request protected by rate limiting and CSRF'})

if __name__ == '__main__':
    app.run(debug=True)
'''
    
    with open('production/flask_security_example.py', 'w') as f:
        f.write(flask_example)
    
    print("Flask integration example created")

if __name__ == "__main__":
    print("STELLAR LOGIC AI - RATE LIMITING AND CSRF INITIALIZATION")
    print("=" * 60)
    
    # Initialize middleware
    success = initialize_security_middleware()
    
    if success:
        print("\nRate limiting and CSRF protection initialized successfully!")
        print("Next steps:")
        print("1. Test with production server")
        print("2. Monitor security logs")
        print("3. Adjust thresholds as needed")
    else:
        print("\nInitialization failed. Check configuration files.")
    
    # Create Flask example
    create_flask_integration_example()
"""
        
        integration_path = os.path.join(self.production_path, "initialize_security_middleware.py")
        with open(integration_path, 'w') as f:
            f.write(integration_script)
        
        print(f"✅ Integration script created")
        
        return True
    
    def main(self):
        """Main initialization function"""
        print("STELLAR LOGIC AI - RATE LIMITING AND CSRF PROTECTION INITIALIZATION")
        print("=" * 70)
        
        success_count = 0
        total_tasks = 5
        
        # Initialize rate limiting
        if self.initialize_rate_limiting():
            success_count += 1
        
        # Initialize CSRF protection
        if self.initialize_csrf_protection():
            success_count += 1
        
        # Create rate limiting middleware
        if self.create_rate_limiting_middleware():
            success_count += 1
        
        # Create CSRF middleware
        if self.create_csrf_middleware():
            success_count += 1
        
        # Create integration script
        if self.create_integration_script():
            success_count += 1
        
        print(f"\nRate Limiting and CSRF Initialization: {success_count}/{total_tasks} tasks completed")
        
        if success_count == total_tasks:
            print("\n✅ Rate limiting and CSRF protection initialized successfully!")
            print("Features enabled:")
            print("- IP-based rate limiting")
            print("- Endpoint-specific rate limits")
            print("- Automatic IP blocking for abuse")
            print("- CSRF token generation and validation")
            print("- Session-based CSRF protection")
            print("- Automatic token cleanup")
            print("\nNext: Run 'python production/initialize_security_middleware.py' to test")
            return True
        else:
            print(f"\n⚠️ Partial initialization completed ({success_count}/{total_tasks})")
            return False

def main():
    """Main function"""
    initializer = RateLimitingCSRFInitializer()
    return initializer.main()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
