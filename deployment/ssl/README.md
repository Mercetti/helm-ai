# Stellar Logic AI SSL Certificate Setup

## Production SSL Configuration

### Certificate Files Needed:
- `stellar-logic.ai.crt` - Main domain certificate
- `stellar-logic.ai.key` - Main domain private key
- `api.stellar-logic.ai.crt` - API subdomain certificate
- `api.stellar-logic.ai.key` - API subdomain private key
- `admin.stellar-logic.ai.crt` - Admin subdomain certificate
- `admin.stellar-logic.ai.key` - Admin subdomain private key
- `portal.stellar-logic.ai.crt` - Portal subdomain certificate
- `portal.stellar-logic.ai.key` - Portal subdomain private key
- `ca-bundle.crt` - Certificate authority bundle

### Certificate Generation Commands:

#### Self-Signed Certificates (Development):
```bash
# Generate private key
openssl genrsa -out stellar-logic.ai.key 2048

# Generate certificate signing request
openssl req -new -key stellar-logic.ai.key -out stellar-logic.ai.csr

# Generate self-signed certificate
openssl x509 -req -days 365 -in stellar-logic.ai.csr -signkey stellar-logic.ai.key -out stellar-logic.ai.crt
```

#### Let's Encrypt Certificates (Production):
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificates
sudo certbot --nginx -d stellar-logic.ai -d api.stellar-logic.ai -d admin.stellar-logic.ai -d portal.stellar-logic.ai

# Copy certificates to deployment directory
sudo cp /etc/letsencrypt/live/stellar-logic.ai/fullchain.pem deployment/ssl/stellar-logic.ai.crt
sudo cp /etc/letsencrypt/live/stellar-logic.ai/privkey.pem deployment/ssl/stellar-logic.ai.key
```

### Certificate Renewal:
```bash
# Auto-renewal setup
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Security Configuration:
- Use TLS 1.2 and 1.3 only
- Implement HSTS headers
- Use strong cipher suites
- Enable OCSP stapling
- Regular certificate monitoring
