@echo off
REM SSL Certificate Generation for Stellar Logic AI
cd production\ssl

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
