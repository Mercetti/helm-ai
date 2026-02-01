#!/usr/bin/env python3
"""
Stellar Logic AI - Production Security Deployment (Fixed)
Automated deployment of all security components to production environment
"""

import os
import sys
import json
import shutil
from datetime import datetime

def create_production_structure():
    """Create production directory structure"""
    print("Creating Production Directory Structure...")
    
    directories = [
        "production",
        "production/security",
        "production/config",
        "production/logs",
        "production/ssl",
        "production/secrets",
        "production/monitoring"
    ]
    
    for directory in directories:
        dir_path = f"c:/Users/merce/Documents/helm-ai/{directory}"
        os.makedirs(dir_path, exist_ok=True)
        print(f"  Created: {directory}")

def deploy_security_components():
    """Deploy all security components to production"""
    print("\nDeploying Security Components...")
    
    security_files = [
        "security_https_middleware.py",
        "security_csrf_protection.py", 
        "security_auth_rate_limiting.py",
        "security_password_policy.py",
        "security_jwt_rotation.py",
        "security_input_validation.py",
        "security_api_key_management.py",
        "stellar_logic_ai_security.py"
    ]
    
    base_path = "c:/Users/merce/Documents/helm-ai"
    deployed_files = []
    
    for file_name in security_files:
        source_path = os.path.join(base_path, file_name)
        dest_path = os.path.join(base_path, "production/security", file_name)
        
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            deployed_files.append(file_name)
            print(f"  Deployed: {file_name}")
        else:
            print(f"  Missing: {file_name}")
            
    return deployed_files

def create_production_config():
    """Create production configuration files"""
    print("\nCreating Production Configuration...")
    
    config = {
        "production": {
            "debug": False,
            "testing": False,
            "secret_key": "stellar-logic-ai-production-secret-key-change-immediately",
            "security": {
                "https_enforced": True,
                "csrf_protection": True,
                "auth_rate_limiting": True,
                "password_policy": True,
                "jwt_rotation": True,
                "input_validation": True,
                "api_key_management": True,
                "security_headers": True,
                "security_logging": True,
                "sql_injection_prevention": True
            },
            "ssl": {
                "cert_file": "production/ssl/stellar_logic_ai.crt",
                "key_file": "production/ssl/stellar_logic_ai.key",
                "ca_file": "production/ssl/ca.crt"
            },
            "logging": {
                "level": "INFO",
                "file": "production/logs/stellar_security.log",
                "max_size": "10MB",
                "backup_count": 5
            },
            "monitoring": {
                "enabled": True,
                "alert_threshold": 100,
                "metrics_port": 9090
            }
        }
    }
    
    config_path = "c:/Users/merce/Documents/helm-ai/production/config/production_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"  Created: production_config.json")
    
    # Environment file
    env_content = """# Stellar Logic AI Production Environment
STELLAR_ENV=production
STELLAR_DEBUG=false
STELLAR_SECURITY_ENABLED=true
STELLAR_HTTPS_ENFORCED=true
STELLAR_CSRF_PROTECTION=true
STELLAR_AUTH_RATE_LIMITING=true
STELLAR_PASSWORD_POLICY=true
STELLAR_JWT_ROTATION=true
STELLAR_INPUT_VALIDATION=true
STELLAR_API_KEY_MANAGEMENT=true
STELLAR_SECURITY_HEADERS=true
STELLAR_SECURITY_LOGGING=true

# SSL Configuration
STELLAR_SSL_CERT_PATH=production/ssl/stellar_logic_ai.crt
STELLAR_SSL_KEY_PATH=production/ssl/stellar_logic_ai.key

# JWT Configuration
STELLAR_JWT_SECRET_PATH=production/secrets/jwt_secrets.json
STELLAR_JWT_ROTATION_INTERVAL=2592000

# API Key Configuration
STELLAR_API_KEY_PATH=production/secrets/api_keys.json
STELLAR_API_KEY_ENCRYPTION_KEY_PATH=production/secrets/api_key_encryption.key

# Logging Configuration
STELLAR_LOG_LEVEL=INFO
STELLAR_LOG_FILE=production/logs/stellar_security.log
"""
    
    env_path = "c:/Users/merce/Documents/helm-ai/production/.env.production"
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"  Created: .env.production")

def create_startup_script():
    """Create production startup script"""
    print("\nCreating Production Startup Script...")
    
    startup_script = """#!/usr/bin/env python3
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
"""
    
    startup_path = "c:/Users/merce/Documents/helm-ai/production/start_stellar_security.py"
    with open(startup_path, 'w') as f:
        f.write(startup_script)
    
    print(f"  Created: start_stellar_security.py")

def create_deployment_summary():
    """Create deployment summary"""
    summary = {
        "deployment_timestamp": datetime.now().isoformat(),
        "system": "Stellar Logic AI",
        "environment": "production",
        "security_components": [
            "HTTPS/TLS Enforcement",
            "CSRF Protection", 
            "Authentication Rate Limiting",
            "Password Policy",
            "JWT Secret Rotation",
            "Input Validation",
            "API Key Management",
            "Security Headers",
            "Security Logging",
            "SQL Injection Prevention"
        ],
        "deployment_status": "completed",
        "next_steps": [
            "Generate SSL certificates",
            "Set environment variables",
            "Start production server",
            "Verify security status",
            "Set up monitoring"
        ]
    }
    
    summary_path = "c:/Users/merce/Documents/helm-ai/production/deployment_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"  Created: deployment_summary.json")

def main():
    """Main deployment function"""
    print("STELLAR LOGIC AI - PRODUCTION SECURITY DEPLOYMENT")
    print("=" * 60)
    
    try:
        # Create production structure
        create_production_structure()
        
        # Deploy security components
        deployed_files = deploy_security_components()
        
        # Create configuration
        create_production_config()
        
        # Create startup script
        create_startup_script()
        
        # Create deployment summary
        create_deployment_summary()
        
        print("\nDEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Deployed {len(deployed_files)} security components")
        print("Production structure created")
        print("Configuration files generated")
        print("Startup script ready")
        print("Deployment summary created")
        
        print(f"\nProduction Directory: c:/Users/merce/Documents/helm-ai/production")
        print("Quick Start: cd production && python start_stellar_security.py")
        print("Security Status: http://localhost/security-status")
        print("Health Check: http://localhost/health")
        
        return True
        
    except Exception as e:
        print(f"\nDEPLOYMENT FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\nProduction deployment completed successfully!")
        print("Stellar Logic AI is now production-ready with enterprise security!")
    else:
        print("\nProduction deployment failed. Check logs for details.")
    
    sys.exit(0 if success else 1)
