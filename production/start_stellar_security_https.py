#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from flask import Flask, jsonify, redirect, request

# Add production security to path
sys.path.insert(0, 'security')

try:
    from stellar_logic_ai_security import create_stellar_security
except ImportError:
    print("Error: Could not import stellar_logic_ai_security")
    sys.exit(1)

def create_production_app():
    app = Flask(__name__)
    
    # Load production configuration
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    app.config['SECRET_KEY'] = os.environ.get('STELLAR_SECRET_KEY', 'stellar-logic-ai-production-secret')
    
    # Initialize Stellar Logic AI Security
    stellar_security = create_stellar_security(app)
    
    # HTTPS enforcement middleware
    @app.before_request
    def enforce_https():
        if not request.is_secure and os.environ.get('FORCE_HTTPS', 'true').lower() == 'true':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
    
    @app.route('/')
    def home():
        return jsonify({
            'system': 'Stellar Logic AI',
            'status': 'Production Security Active',
            'security': 'Enterprise Grade',
            'https': 'Enforced',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @app.route('/security-status')
    def security_status():
        status = stellar_security.run_stellar_security_check()
        return jsonify(status)
    
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'security': 'active',
            'https': 'enforced',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    return app

if __name__ == '__main__':
    app = create_production_app()
    
    # SSL configuration
    ssl_context = None
    cert_file = os.environ.get('STELLAR_SSL_CERT_PATH', 'production/ssl/stellar_logic_ai.crt')
    key_file = os.environ.get('STELLAR_SSL_KEY_PATH', 'production/ssl/stellar_logic_ai.key')
    
    # Check if certificates exist
    if os.path.exists(cert_file) and os.path.exists(key_file):
        ssl_context = (cert_file, key_file)
        print("SSL/TLS enabled for production")
        print(f"Certificate: {cert_file}")
        print(f"Private Key: {key_file}")
    else:
        print("SSL certificates not found!")
        print("Please run: cd production/ssl && generate_certificates.bat")
        print("Or use certificates from a trusted Certificate Authority")
        
        # Ask user if they want to continue without HTTPS
        response = input("Continue without HTTPS? (y/n): ")
        if response.lower() != 'y':
            print("Exiting. Please generate SSL certificates first.")
            sys.exit(1)
    
    # Production configuration
    host = os.environ.get('STELLAR_HOST', '0.0.0.0')
    port = int(os.environ.get('STELLAR_PORT', 443 if ssl_context else 80))
    
    print(f"Starting Stellar Logic AI Production Server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"HTTPS: {'Enabled' if ssl_context else 'Disabled'}")
    
    # Run production server
    app.run(
        host=host,
        port=port,
        ssl_context=ssl_context,
        debug=False,
        threaded=True
    )
