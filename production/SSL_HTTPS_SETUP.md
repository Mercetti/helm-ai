# Stellar Logic AI - SSL Certificate and HTTPS Setup

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
- Automatic HTTPS redirects
- HSTS (HTTP Strict Transport Security)
- SSL/TLS enforcement
- Secure cipher suites
- Certificate validation

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