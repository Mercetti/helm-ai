@echo off
REM SSL Certificate Generation for Stellar Logic AI
echo Generating SSL certificates...

REM Change to SSL directory
cd production\ssl

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
