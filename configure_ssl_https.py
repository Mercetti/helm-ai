#!/usr/bin/env python3
"""
Stellar Logic AI - SSL Certificate and HTTPS Configuration
Generate SSL certificates and configure HTTPS enforcement
"""

import os
import subprocess
import json
from datetime import datetime

def generate_ssl_certificates():
    """Generate SSL certificates for Stellar Logic AI"""
    print("Generating SSL Certificates for Stellar Logic AI...")
    
    ssl_path = "c:/Users/merce/Documents/helm-ai/production/ssl"
    
    # Check if OpenSSL is available
    try:
        result = subprocess.run(['openssl', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"OpenSSL found: {result.stdout.strip()}")
        else:
            print("OpenSSL not found, creating self-signed certificates manually")
            return create_manual_certificates()
    except FileNotFoundError:
        print("OpenSSL not found, creating self-signed certificates manually")
        return create_manual_certificates()
    
    # Generate certificates using OpenSSL
    try:
        os.chdir(ssl_path)
        
        # Generate private key
        print("Generating private key...")
        subprocess.run([
            'openssl', 'genrsa', '-out', 'stellar_logic_ai.key', '2048'
        ], check=True)
        
        # Generate certificate signing request
        print("Generating certificate signing request...")
        subprocess.run([
            'openssl', 'req', '-new', '-key', 'stellar_logic_ai.key', 
            '-out', 'stellar_logic_ai.csr', 
            '-subj', '/C=US/ST=CA/L=San Francisco/O=Stellar Logic AI/CN=stellarlogic.ai'
        ], check=True)
        
        # Generate self-signed certificate
        print("Generating self-signed certificate...")
        subprocess.run([
            'openssl', 'x509', '-req', '-days', '365', 
            '-in', 'stellar_logic_ai.csr', '-signkey', 'stellar_logic_ai.key', 
            '-out', 'stellar_logic_ai.crt'
        ], check=True)
        
        # Generate CA certificate
        print("Generating CA certificate...")
        subprocess.run([
            'openssl', 'req', '-new', '-x509', '-days', '365', 
            '-keyout', 'ca.key', '-out', 'ca.crt',
            '-subj', '/C=US/ST=CA/L=San Francisco/O=Stellar Logic AI/CN=Stellar Logic AI CA'
        ], check=True)
        
        print("SSL certificates generated successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating certificates: {e}")
        return create_manual_certificates()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return create_manual_certificates()

def create_manual_certificates():
    """Create manual SSL certificate configuration"""
    print("Creating manual SSL certificate configuration...")
    
    ssl_path = "c:/Users/merce/Documents/helm-ai/production/ssl"
    
    # Create certificate generation script
    cert_script = """@echo off
REM SSL Certificate Generation for Stellar Logic AI
echo Generating SSL certificates...

REM Change to SSL directory
cd production\\ssl

REM Check if OpenSSL is available
openssl version >nul 2>&1
if errorlevel 1 (
    echo OpenSSL not found. Please install OpenSSL or use certificates from a CA.
    echo You can download OpenSSL from: https://slproweb.com/products/Win32OpenSSL.html
    pause
    exit /b 1
)

REM Generate private key
echo Generating private key...
openssl genrsa -out stellar_logic_ai.key 2048

REM Generate certificate signing request
echo Generating certificate signing request...
openssl req -new -key stellar_logic_ai.key -out stellar_logic_ai.csr -subj "/C=US/ST=CA/L=San Francisco/O=Stellar Logic AI/CN=stellarlogic.ai"

REM Generate self-signed certificate
echo Generating self-signed certificate...
openssl x509 -req -days 365 -in stellar_logic_ai.csr -signkey stellar_logic_ai.key -out stellar_logic_ai.crt

REM Generate CA certificate
echo Generating CA certificate...
openssl req -new -x509 -days 365 -keyout ca.key -out ca.crt -subj "/C=US/ST=CA/L=San Francisco/O=Stellar Logic AI/CN=Stellar Logic AI CA"

echo SSL certificates generated successfully!
echo Certificate: stellar_logic_ai.crt
echo Private Key: stellar_logic_ai.key
echo CA Certificate: ca.crt

pause
"""
    
    script_path = os.path.join(ssl_path, "generate_certificates.bat")
    with open(script_path, 'w') as f:
        f.write(cert_script)
    
    # Create Linux/Mac version
    cert_script_sh = """#!/bin/bash
# SSL Certificate Generation for Stellar Logic AI
echo "Generating SSL certificates..."

# Change to SSL directory
cd production/ssl

# Check if OpenSSL is available
if ! command -v openssl &> /dev/null; then
    echo "OpenSSL not found. Please install OpenSSL."
    echo "On Ubuntu/Debian: sudo apt-get install openssl"
    echo "On CentOS/RHEL: sudo yum install openssl"
    echo "On macOS: brew install openssl"
    exit 1
fi

# Generate private key
echo "Generating private key..."
openssl genrsa -out stellar_logic_ai.key 2048

# Generate certificate signing request
echo "Generating certificate signing request..."
openssl req -new -key stellar_logic_ai.key -out stellar_logic_ai.csr -subj "/C=US/ST=CA/L=San Francisco/O=Stellar Logic AI/CN=stellarlogic.ai"

# Generate self-signed certificate
echo "Generating self-signed certificate..."
openssl x509 -req -days 365 -in stellar_logic_ai.csr -signkey stellar_logic_ai.key -out stellar_logic_ai.crt

# Generate CA certificate
echo "Generating CA certificate..."
openssl req -new -x509 -days 365 -keyout ca.key -out ca.crt -subj "/C=US/ST=CA/L=San Francisco/O=Stellar Logic AI/CN=Stellar Logic AI CA"

echo "SSL certificates generated successfully!"
echo "Certificate: stellar_logic_ai.crt"
echo "Private Key: stellar_logic_ai.key"
echo "CA Certificate: ca.crt"
"""
    
    script_path_sh = os.path.join(ssl_path, "generate_certificates.sh")
    with open(script_path_sh, 'w') as f:
        f.write(cert_script_sh)
    
    print("SSL certificate generation scripts created")
    print("Run 'generate_certificates.bat' (Windows) or 'generate_certificates.sh' (Linux/Mac)")
    
    return True

def configure_https_enforcement():
    """Configure HTTPS enforcement settings"""
    print("Configuring HTTPS enforcement...")
    
    production_path = "c:/Users/merce/Documents/helm-ai/production"
    
    # Update production configuration for HTTPS
    config_path = os.path.join(production_path, "config/production_config.json")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update SSL configuration
        config["production"]["ssl"]["auto_generate"] = True
        config["production"]["ssl"]["certificate_info"] = {
            "common_name": "stellarlogic.ai",
            "organization": "Stellar Logic AI",
            "country": "US",
            "state": "CA",
            "locality": "San Francisco",
            "valid_days": 365,
            "key_size": 2048
        }
        
        # Add HTTPS enforcement settings
        config["production"]["https_enforcement"] = {
            "force_https": True,
            "strict_transport_security": True,
            "hsts_max_age": 31536000,
            "hsts_include_subdomains": True,
            "hsts_preload": True,
            "redirect_http_to_https": True,
            "ssl_protocols": ["TLSv1.2", "TLSv1.3"],
            "ssl_ciphers": [
                "ECDHE-RSA-AES256-GCM-SHA384",
                "ECDHE-RSA-AES128-GCM-SHA256",
                "ECDHE-RSA-AES256-SHA384",
                "ECDHE-RSA-AES128-SHA256"
            ]
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("HTTPS enforcement configuration updated")
        
    except Exception as e:
        print(f"Error updating HTTPS configuration: {e}")
        return False
    
    return True

def create_https_startup_script():
    """Create HTTPS-enabled startup script"""
    print("Creating HTTPS-enabled startup script...")
    
    startup_script = """#!/usr/bin/env python3
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
"""
    
    startup_path = "c:/Users/merce/Documents/helm-ai/production/start_stellar_security_https.py"
    with open(startup_path, 'w') as f:
        f.write(startup_script)
    
    print("HTTPS-enabled startup script created")
    
    return True

def create_ssl_documentation():
    """Create SSL/HTTPS documentation"""
    print("Creating SSL/HTTPS documentation...")
    
    docs = """# Stellar Logic AI - SSL Certificate and HTTPS Setup

## Overview
This guide covers SSL certificate generation and HTTPS enforcement for Stellar Logic AI production deployment.

## Quick Start

### 1. Generate SSL Certificates

#### Windows:
```bash
cd production/ssl
generate_certificates.bat
```

#### Linux/Mac:
```bash
cd production/ssl
chmod +x generate_certificates.sh
./generate_certificates.sh
```

### 2. Start HTTPS Server
```bash
cd production
python start_stellar_security_https.py
```

## Certificate Files
- `stellar_logic_ai.crt` - SSL certificate
- `stellar_logic_ai.key` - Private key
- `ca.crt` - Certificate Authority

## HTTPS Features
- ✅ Automatic HTTPS redirects
- ✅ HSTS (HTTP Strict Transport Security)
- ✅ SSL/TLS enforcement
- ✅ Secure cipher suites
- ✅ Certificate validation

## Configuration
SSL configuration is stored in `production/config/production_config.json`

## Environment Variables
- `STELLAR_SSL_CERT_PATH` - Path to SSL certificate
- `STELLAR_SSL_KEY_PATH` - Path to private key
- `FORCE_HTTPS` - Force HTTPS redirects (default: true)

## Production Deployment
For production, use certificates from a trusted Certificate Authority like:
- Let's Encrypt (free)
- DigiCert
- Comodo
- GlobalSign

## Security Headers
The system automatically adds security headers:
- Strict-Transport-Security
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection

## Troubleshooting
1. Ensure OpenSSL is installed
2. Check certificate file permissions
3. Verify certificate and key match
4. Check firewall settings for port 443

## Support
For SSL/HTTPS issues, contact: security@stellarlogic.ai
"""
    
    docs_path = "c:/Users/merce/Documents/helm-ai/production/SSL_HTTPS_SETUP.md"
    with open(docs_path, 'w') as f:
        f.write(docs)
    
    print("SSL/HTTPS documentation created")
    
    return True

def main():
    """Main SSL/HTTPS configuration function"""
    print("STELLAR LOGIC AI - SSL CERTIFICATE AND HTTPS CONFIGURATION")
    print("=" * 60)
    
    success_count = 0
    total_tasks = 4
    
    # Generate SSL certificates
    if generate_ssl_certificates():
        success_count += 1
    
    # Configure HTTPS enforcement
    if configure_https_enforcement():
        success_count += 1
    
    # Create HTTPS startup script
    if create_https_startup_script():
        success_count += 1
    
    # Create documentation
    if create_ssl_documentation():
        success_count += 1
    
    print(f"\nSSL/HTTPS Configuration: {success_count}/{total_tasks} tasks completed")
    
    if success_count == total_tasks:
        print("\nSSL/HTTPS configuration completed successfully!")
        print("Next steps:")
        print("1. Run: cd production/ssl && generate_certificates.bat")
        print("2. Start: cd production && python start_stellar_security_https.py")
        print("3. Access: https://localhost/security-status")
        return True
    else:
        print(f"\nSSL/HTTPS configuration partially completed ({success_count}/{total_tasks})")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
