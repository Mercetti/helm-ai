#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from flask import Flask, jsonify

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
    
    @app.route('/')
    def home():
        return jsonify({
            'system': 'Stellar Logic AI',
            'status': 'Production Security Active',
            'security': 'Enterprise Grade',
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
            'timestamp': datetime.utcnow().isoformat()
        })
    
    return app

if __name__ == '__main__':
    app = create_production_app()
    
    # Production configuration
    ssl_context = None
    if os.environ.get('STELLAR_HTTPS_ENFORCED', 'true').lower() == 'true':
        cert_file = os.environ.get('STELLAR_SSL_CERT_PATH', 'production/ssl/stellar_logic_ai.crt')
        key_file = os.environ.get('STELLAR_SSL_KEY_PATH', 'production/ssl/stellar_logic_ai.key')
        
        if os.path.exists(cert_file) and os.path.exists(key_file):
            ssl_context = (cert_file, key_file)
            print("SSL/TLS enabled for production")
        else:
            print("SSL certificates not found, running without HTTPS")
    
    # Run production server
    app.run(
        host='0.0.0.0',
        port=443 if ssl_context else 80,
        ssl_context=ssl_context,
        debug=False,
        threaded=True
    )
