#!/usr/bin/env python3
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
        print("
Rate limiting and CSRF protection initialized successfully!")
        print("Next steps:")
        print("1. Test with production server")
        print("2. Monitor security logs")
        print("3. Adjust thresholds as needed")
    else:
        print("
Initialization failed. Check configuration files.")
    
    # Create Flask example
    create_flask_integration_example()
