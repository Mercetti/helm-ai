#!/bin/bash

# Helm AI Let's Encrypt Certificate Setup Script
# This script sets up automatic SSL certificate renewal with Certbot

set -e

# Configuration
DOMAIN="helm-ai.com"
EMAIL="admin@helm-ai.com"
WEBROOT="/var/www/certbot"
NGINX_CONF_DIR="/etc/nginx/sites-available"
CERTBOT_CONF_DIR="/etc/letsencrypt"

# Install Certbot and Nginx plugin
echo "Installing Certbot..."
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Create webroot directory for Certbot challenges
mkdir -p "$WEBROOT"
chown -R www-data:www-data "$WEBROOT"

# Create initial Nginx config for HTTP validation
cat > "$NGINX_CONF_DIR/helm-ai-http.conf" << EOF
server {
    listen 80;
    server_name helm-ai.com www.helm-ai.com api.helm-ai.com grafana.helm-ai.com;
    
    location /.well-known/acme-challenge/ {
        root $WEBROOT;
    }
    
    location / {
        return 301 https://\$host\$request_uri;
    }
}
EOF

# Enable the HTTP config
ln -sf "$NGINX_CONF_DIR/helm-ai-http.conf" "/etc/nginx/sites-enabled/"

# Test Nginx configuration
nginx -t

# Reload Nginx
systemctl reload nginx

# Obtain SSL certificates
echo "Obtaining SSL certificates for $DOMAIN..."
certbot certonly \
    --webroot \
    --webroot-path="$WEBROOT" \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --non-interactive \
    -d "helm-ai.com" \
    -d "www.helm-ai.com" \
    -d "api.helm-ai.com" \
    -d "grafana.helm-ai.com"

# Create strong Diffie-Hellman parameters
echo "Generating Diffie-Hellman parameters..."
openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048

# Setup automatic renewal
echo "Setting up automatic certificate renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook 'systemctl reload nginx'") | crontab -

# Create renewal hook for Nginx reload
cat > /etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh << 'EOF'
#!/bin/bash
systemctl reload nginx
EOF
chmod +x /etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh

# Test renewal process
echo "Testing certificate renewal process..."
certbot renew --dry-run

echo ""
echo "SSL certificate setup complete!"
echo "Certificates are located in: $CERTBOT_CONF_DIR/live/$DOMAIN/"
echo ""
echo "Next steps:"
echo "1. Update your Nginx configuration to use the Let's Encrypt certificates"
echo "2. Replace the certificate paths in nginx-https.conf with:"
echo "   - ssl_certificate: $CERTBOT_CONF_DIR/live/$DOMAIN/fullchain.pem"
echo "   - ssl_certificate_key: $CERTBOT_CONF_DIR/live/$DOMAIN/privkey.pem"
echo "   - ssl_trusted_certificate: $CERTBOT_CONF_DIR/live/$DOMAIN/chain.pem"
echo "3. Test Nginx configuration and reload"
echo ""
echo "Automatic renewal is configured and will run daily at 12:00 PM."
