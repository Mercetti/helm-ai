#!/bin/bash
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
