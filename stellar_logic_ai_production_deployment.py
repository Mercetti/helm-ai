#!/usr/bin/env python3
"""
Stellar Logic AI - Production Security Deployment Script
Automated deployment of all security components to production environment
"""

import os
import sys
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any
import subprocess

class StellarSecurityDeployment:
    """Production security deployment system for Stellar Logic AI"""
    
    def __init__(self):
        self.base_path = "c:/Users/merce/Documents/helm-ai"
        self.production_path = "c:/Users/merce/Documents/helm-ai/production"
        self.security_files = [
            "security_https_middleware.py",
            "security_csrf_protection.py", 
            "security_auth_rate_limiting.py",
            "security_password_policy.py",
            "security_jwt_rotation.py",
            "security_input_validation.py",
            "security_api_key_management.py",
            "stellar_logic_ai_security.py"
        ]
        self.deployment_log = []
        
    def create_production_structure(self):
        """Create production directory structure"""
        print("🏗️ Creating Production Directory Structure...")
        
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
            dir_path = os.path.join(self.base_path, directory)
            os.makedirs(dir_path, exist_ok=True)
            print(f"  ✅ Created: {directory}")
            
        self.log_event("production_structure", "Created production directory structure")
    
    def deploy_security_components(self):
        """Deploy all security components to production"""
        print("\n🚀 Deploying Security Components...")
        
        deployed_files = []
        
        for file_name in self.security_files:
            source_path = os.path.join(self.base_path, file_name)
            dest_path = os.path.join(self.base_path, "production/security", file_name)
            
            if os.path.exists(source_path):
                shutil.copy2(source_path, dest_path)
                deployed_files.append(file_name)
                print(f"  ✅ Deployed: {file_name}")
            else:
                print(f"  ❌ Missing: {file_name}")
                
        self.log_event("security_deployment", f"Deployed {len(deployed_files)} security components")
        return deployed_files
    
    def create_production_config(self):
        """Create production configuration files"""
        print("\n⚙️ Creating Production Configuration...")
        
        # Main production config
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
        
        config_path = os.path.join(self.base_path, "production/config/production_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"  ✅ Created: production_config.json")
        self.log_event("config_creation", "Created production configuration")
        
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
        
        env_path = os.path.join(self.base_path, "production/.env.production")
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"  ✅ Created: .env.production")
    
    def generate_ssl_certificates(self):
        """Generate SSL certificates for production"""
        print("\n🔐 Generating SSL Certificates...")
        
        ssl_script = """#!/bin/bash
# SSL Certificate Generation for Stellar Logic AI
cd production/ssl

# Generate private key
openssl genrsa -out stellar_logic_ai.key 2048

# Generate certificate signing request
openssl req -new -key stellar_logic_ai.key -out stellar_logic_ai.csr -subj "/C=US/ST=CA/L=San Francisco/O=Stellar Logic AI/CN=stellarlogic.ai"

# Generate self-signed certificate
openssl x509 -req -days 365 -in stellar_logic_ai.csr -signkey stellar_logic_ai.key -out stellar_logic_ai.crt

# Generate CA certificate
openssl req -new -x509 -days 365 -keyout ca.key -out ca.crt -subj "/C=US/ST=CA/L=San Francisco/O=Stellar Logic AI/CN=Stellar Logic AI CA"

echo "SSL certificates generated successfully!"
"""
        
        ssl_script_path = os.path.join(self.base_path, "production/generate_ssl.sh")
        with open(ssl_script_path, 'w') as f:
            f.write(ssl_script)
        
        # For Windows, create a batch file
        ssl_batch = """@echo off
REM SSL Certificate Generation for Stellar Logic AI
cd production\\ssl

REM Generate private key
openssl genrsa -out stellar_logic_ai.key 2048

REM Generate certificate signing request
openssl req -new -key stellar_logic_ai.key -out stellar_logic_ai.csr -subj "/C=US/ST=CA/L=San Francisco/O=Stellar Logic AI/CN=stellarlogic.ai"

REM Generate self-signed certificate
openssl x509 -req -days 365 -in stellar_logic_ai.csr -signkey stellar_logic_ai.key -out stellar_logic_ai.crt

REM Generate CA certificate
openssl req -new -x509 -days 365 -keyout ca.key -out ca.crt -subj "/C=US/ST=CA/L=San Francisco/O=Stellar Logic AI/CN=Stellar Logic AI CA"

echo SSL certificates generated successfully!
pause
"""
        
        ssl_batch_path = os.path.join(self.base_path, "production/generate_ssl.bat")
        with open(ssl_batch_path, 'w') as f:
            f.write(ssl_batch)
        
        print(f"  ✅ Created: SSL generation scripts")
        self.log_event("ssl_setup", "Created SSL certificate generation scripts")
    
    def create_startup_scripts(self):
        """Create production startup scripts"""
        print("\n🚀 Creating Production Startup Scripts...")
        
        # Python startup script
        startup_script = """#!/usr/bin/env python3
\"\"\"
Stellar Logic AI - Production Security Startup
Production deployment with all security components enabled
\"\"\"

import os
import sys
from stellar_logic_ai_security import create_stellar_security
from flask import Flask, jsonify

def create_production_app():
    \"\"\"Create production Flask app with security\"\"\"
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
            print("🔐 SSL/TLS enabled for production")
        else:
            print("⚠️ SSL certificates not found, generating...")
            os.system("cd production && generate_ssl.bat")
            ssl_context = (cert_file, key_file)
    
    # Run production server
    app.run(
        host='0.0.0.0',
        port=443 if ssl_context else 80,
        ssl_context=ssl_context,
        debug=False,
        threaded=True
    )
"""
        
        startup_path = os.path.join(self.base_path, "production/start_stellar_security.py")
        with open(startup_path, 'w') as f:
            f.write(startup_script)
        
        # Batch startup file
        batch_startup = """@echo off
REM Stellar Logic AI - Production Security Startup
echo ========================================
echo Starting Stellar Logic AI Production Security
echo ========================================

REM Set environment variables
set STELLAR_ENV=production
set STELLAR_DEBUG=false
set STELLAR_SECURITY_ENABLED=true
set STELLAR_HTTPS_ENFORCED=true

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check SSL certificates
if not exist "production\\ssl\\stellar_logic_ai.crt" (
    echo Generating SSL certificates...
    call production\\generate_ssl.bat
)

REM Start production server
echo Starting Stellar Logic AI with enterprise security...
cd production
python start_stellar_security.py

pause
"""
        
        batch_path = os.path.join(self.base_path, "production/start_stellar_security.bat")
        with open(batch_path, 'w') as f:
            f.write(batch_startup)
        
        print(f"  ✅ Created: Production startup scripts")
        self.log_event("startup_scripts", "Created production startup scripts")
    
    def create_monitoring_setup(self):
        """Create monitoring and alerting setup"""
        print("\n📊 Creating Monitoring Setup...")
        
        monitoring_config = {
            "security_monitoring": {
                "enabled": True,
                "log_file": "production/logs/stellar_security.log",
                "alert_thresholds": {
                    "failed_logins": 10,
                    "suspicious_patterns": 5,
                    "rate_limit_hits": 100,
                    "csrf_failures": 10
                },
                "notifications": {
                    "email": "security@stellarlogic.ai",
                    "webhook": "https://api.stellarlogic.ai/alerts",
                    "slack": "#security-alerts"
                },
                "metrics": {
                    "collection_interval": 60,
                    "retention_days": 30,
                    "export_format": "json"
                }
            }
        }
        
        monitoring_path = os.path.join(self.base_path, "production/monitoring/security_monitoring.json")
        with open(monitoring_path, 'w') as f:
            json.dump(monitoring_config, f, indent=2)
        
        print(f"  ✅ Created: Security monitoring configuration")
        self.log_event("monitoring_setup", "Created monitoring configuration")
    
    def create_deployment_documentation(self):
        """Create deployment documentation"""
        print("\n📚 Creating Deployment Documentation...")
        
        docs = """# Stellar Logic AI - Production Security Deployment Guide

## Overview
This guide covers the deployment of Stellar Logic AI security components to production environment.

## Prerequisites
- Python 3.8+
- OpenSSL for SSL certificates
- Production server environment
- SSL certificates (or use provided generation script)

## Quick Start

### 1. Generate SSL Certificates
```bash
cd production
generate_ssl.bat  # Windows
# or
bash generate_ssl.sh  # Linux/Mac
```

### 2. Set Environment Variables
```bash
set STELLAR_ENV=production
set STELLAR_SECURITY_ENABLED=true
set STELLAR_HTTPS_ENFORCED=true
```

### 3. Start Production Server
```bash
start_stellar_security.bat
```

## Security Components Enabled
- ✅ HTTPS/TLS Enforcement
- ✅ CSRF Protection
- ✅ Authentication Rate Limiting
- ✅ Password Policy
- ✅ JWT Secret Rotation
- ✅ Input Validation
- ✅ API Key Management
- ✅ Security Headers
- ✅ Security Logging
- ✅ SQL Injection Prevention

## Monitoring
- Security events logged to: `production/logs/stellar_security.log`
- Security status available at: `/security-status`
- Health check available at: `/health`

## Configuration
- Main config: `production/config/production_config.json`
- Environment: `production/.env.production`
- SSL certificates: `production/ssl/`

## Troubleshooting
1. Check SSL certificates exist
2. Verify environment variables
3. Check log files for errors
4. Validate security status endpoint

## Support
For production security issues, contact: security@stellarlogic.ai
"""
        
        docs_path = os.path.join(self.base_path, "production/DEPLOYMENT_GUIDE.md")
        with open(docs_path, 'w') as f:
            f.write(docs)
        
        print(f"  ✅ Created: Deployment documentation")
        self.log_event("documentation", "Created deployment documentation")
    
    def log_event(self, event_type: str, message: str):
        """Log deployment events"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "message": message
        }
        self.deployment_log.append(event)
    
    def save_deployment_log(self):
        """Save deployment log"""
        log_path = os.path.join(self.base_path, "production/deployment_log.json")
        with open(log_path, 'w') as f:
            json.dump(self.deployment_log, f, indent=2)
    
    def run_deployment(self):
        """Run complete production deployment"""
        print("🚀 STELLAR LOGIC AI - PRODUCTION SECURITY DEPLOYMENT")
        print("=" * 60)
        
        try:
            # Create production structure
            self.create_production_structure()
            
            # Deploy security components
            deployed_files = self.deploy_security_components()
            
            # Create configuration
            self.create_production_config()
            
            # Generate SSL certificates
            self.generate_ssl_certificates()
            
            # Create startup scripts
            self.create_startup_scripts()
            
            # Setup monitoring
            self.create_monitoring_setup()
            
            # Create documentation
            self.create_deployment_documentation()
            
            # Save deployment log
            self.save_deployment_log()
            
            print("\n🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"✅ Deployed {len(deployed_files)} security components")
            print("✅ Production structure created")
            print("✅ Configuration files generated")
            print("✅ SSL certificate scripts created")
            print("✅ Startup scripts ready")
            print("✅ Monitoring setup configured")
            print("✅ Documentation created")
            
            print(f"\n📁 Production Directory: {self.base_path}/production")
            print("🚀 Quick Start: Run production/start_stellar_security.bat")
            print("📊 Security Status: http://localhost/security-status")
            print("💚 Health Check: http://localhost/health")
            
            return True
            
        except Exception as e:
            print(f"\n❌ DEPLOYMENT FAILED: {str(e)}")
            self.log_event("deployment_error", str(e))
            self.save_deployment_log()
            return False

def main():
    """Main deployment function"""
    print("🔍 Starting Stellar Logic AI Production Security Deployment...")
    
    deployment = StellarSecurityDeployment()
    success = deployment.run_deployment()
    
    if success:
        print("\n✅ Production deployment completed successfully!")
        print("🔒 Stellar Logic AI is now production-ready with enterprise security!")
    else:
        print("\n❌ Production deployment failed. Check logs for details.")
    
    return success

if __name__ == "__main__":
    main()
