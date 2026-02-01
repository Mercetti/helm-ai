#!/usr/bin/env python3
"""
Stellar Logic AI SSL Certificate Setup
Generate self-signed certificates for development
"""

import subprocess
import os
from datetime import datetime

def generate_ssl_certificates():
    """Generate self-signed SSL certificates"""
    
    # Check if OpenSSL is available
    try:
        subprocess.run(['openssl', 'version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ OpenSSL not found. Please install OpenSSL to generate certificates.")
        return False
    
    # Generate private key
    try:
        subprocess.run([
            'openssl', 'genrsa', '-out', 'server.key', '2048'
        ], check=True)
        print("✅ Generated private key: server.key")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate private key: {e}")
        return False
    
    # Generate certificate signing request
    try:
        subprocess.run([
            'openssl', 'req', '-new', '-key', 'server.key',
            '-out', 'server.csr',
            '-subj', '/C=US/ST=CA/L=San Francisco/O=Stellar Logic AI/CN=localhost'
        ], check=True)
        print("✅ Generated CSR: server.csr")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate CSR: {e}")
        return False
    
    # Generate self-signed certificate
    try:
        subprocess.run([
            'openssl', 'x509', '-req', '-days', '365',
            '-in', 'server.csr', '-signkey', 'server.key',
            '-out', 'server.crt'
        ], check=True)
        print("✅ Generated certificate: server.crt")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate certificate: {e}")
        return False
    
    # Generate DH parameters
    try:
        subprocess.run([
            'openssl', 'dhparam', '-out', 'dhparam.pem', '2048'
        ], check=True)
        print("✅ Generated DH parameters: dhparam.pem")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate DH parameters: {e}")
        return False
    
    # Clean up CSR
    os.remove('server.csr')
    
    print("🔐 SSL certificates generated successfully!")
    print("📁 Files created:")
    print("  • server.key - Private key")
    print("  • server.crt - SSL certificate")
    print("  • dhparam.pem - DH parameters")
    
    return True

if __name__ == '__main__':
    print("🔐 GENERATING SSL CERTIFICATES...")
    print("📅 Generated on:", datetime.now().isoformat())
    print("🔒 Valid for: 365 days")
    print("🌐 For: localhost")
    
    success = generate_ssl_certificates()
    
    if success:
        print("✅ SSL setup complete!")
    else:
        print("❌ SSL setup failed!")
