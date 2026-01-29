#!/bin/bash

# Helm AI SSL Certificate Generation Script
# This script generates SSL certificates for development and production environments

set -e

# Configuration
DOMAIN="helm-ai.com"
CERT_DIR="/etc/ssl/helm-ai"
VALIDITY_DAYS=365
COUNTRY="US"
STATE="California"
CITY="San Francisco"
ORGANIZATION="Helm AI Inc."
ORGANIZATIONAL_UNIT="Engineering"
EMAIL="admin@helm-ai.com"

# Create certificate directory
mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

echo "Generating SSL certificates for $DOMAIN..."

# Generate CA private key
openssl genrsa -out ca.key 4096

# Generate CA certificate
openssl req -new -x509 -days $VALIDITY_DAYS -key ca.key -out ca.crt \
    -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORGANIZATION/OU=$ORGANIZATIONAL_UNIT/CN=$DOMAIN CA/emailAddress=$EMAIL"

# Generate server private key
openssl genrsa -out server.key 2048

# Generate server CSR (Certificate Signing Request)
openssl req -new -key server.key -out server.csr \
    -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORGANIZATION/OU=$ORGANIZATIONAL_UNIT/CN=$DOMAIN/emailAddress=$EMAIL" \
    -addext "subjectAltName=DNS:helm-ai.com,DNS:www.helm-ai.com,DNS:api.helm-ai.com,DNS:grafana.helm-ai.com,DNS:*.helm-ai.com"

# Generate server certificate signed by CA
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out server.crt -days $VALIDITY_DAYS -sha256 \
    -extfile <(cat <<EOF
[v3_req]
subjectAltName = @alt_names
[alt_names]
DNS.1 = helm-ai.com
DNS.2 = www.helm-ai.com
DNS.3 = api.helm-ai.com
DNS.4 = grafana.helm-ai.com
DNS.5 = *.helm-ai.com
EOF
)

# Generate client private key for mTLS
openssl genrsa -out client.key 2048

# Generate client CSR
openssl req -new -key client.key -out client.csr \
    -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORGANIZATION/OU=$ORGANIZATIONAL_UNIT/CN=client.helm-ai.com/emailAddress=$EMAIL"

# Generate client certificate signed by CA
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out client.crt -days $VALIDITY_DAYS -sha256

# Generate DH parameters for perfect forward secrecy
openssl dhparam -out dhparam.pem 2048

# Set proper permissions
chmod 600 *.key
chmod 644 *.crt *.pem
chmod 600 ca.srl

# Create combined certificate bundle for clients
cat server.crt ca.crt > fullchain.pem

echo "SSL certificates generated successfully!"
echo "Files created:"
echo "  - ca.key: CA private key"
echo "  - ca.crt: CA certificate"
echo "  - server.key: Server private key"
echo "  - server.csr: Server certificate signing request"
echo "  - server.crt: Server certificate"
echo "  - client.key: Client private key"
echo "  - client.csr: Client certificate signing request"
echo "  - client.crt: Client certificate"
echo "  - dhparam.pem: Diffie-Hellman parameters"
echo "  - fullchain.pem: Combined server and CA certificate"

# Verify certificates
echo ""
echo "Verifying certificates..."
openssl x509 -in server.crt -text -noout | grep -E "(Subject:|Issuer:|Not Before:|Not After:|DNS:)"
openssl x509 -in client.crt -text -noout | grep -E "(Subject:|Issuer:|Not Before:|Not After:)"

echo ""
echo "Certificate setup complete!"
echo "CA certificate (ca.crt) should be distributed to clients for verification."
echo "Server certificates (server.key, server.crt) should be installed on the server."
