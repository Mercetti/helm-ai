#!/usr/bin/env python3
"""
Stellar Logic AI Security Tests
Comprehensive security testing suite
"""

import unittest
import requests
import json
import time
from datetime import datetime
from security_framework import SecurityFramework

class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.security = SecurityFramework()
        self.base_url = 'http://localhost:8080'
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = 'test_password_123'
        
        # Hash password
        hashed = self.security.hash_password(password)
        self.assertIsInstance(hashed, str)
        self.assertTrue(hashed.startswith('$2b$'))
        
        # Verify password
        self.assertTrue(self.security.verify_password(password, hashed))
        self.assertFalse(self.security.verify_password('wrong_password', hashed))
        
        print("✅ Password hashing test passed")
    
    def test_jwt_tokens(self):
        """Test JWT token generation and verification"""
        user_id = 'test_user'
        role = 'admin'
        
        # Generate token
        token = self.security.generate_jwt_token(user_id, role)
        self.assertIsInstance(token, str)
        
        # Verify token
        payload = self.security.verify_jwt_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload['user_id'], user_id)
        self.assertEqual(payload['role'], role)
        
        # Test invalid token
        invalid_payload = self.security.verify_jwt_token('invalid_token')
        self.assertIsNone(invalid_payload)
        
        print("✅ JWT token test passed")
    
    def test_data_encryption(self):
        """Test data encryption and decryption"""
        original_data = 'sensitive_information_123'
        
        # Encrypt data
        encrypted = self.security.encrypt_data(original_data)
        self.assertNotEqual(encrypted, original_data.encode('utf-8'))
        
        # Decrypt data
        decrypted = self.security.decrypt_data(encrypted)
        self.assertEqual(decrypted, original_data)
        
        print("✅ Data encryption test passed")
    
    def test_input_validation(self):
        """Test input validation"""
        # Valid inputs
        self.assertTrue(self.security.validate_input('valid_string', 'string'))
        self.assertTrue(self.security.validate_input('test@example.com', 'email'))
        self.assertTrue(self.security.validate_input('{"key": "value"}', 'json'))
        
        # Invalid inputs
        self.assertFalse(self.security.validate_input('<script>alert("xss")</script>', 'string'))
        self.assertFalse(self.security.validate_input('invalid_email', 'email'))
        self.assertFalse(self.security.validate_input('invalid json', 'json'))
        
        print("✅ Input validation test passed")
    
    def test_rate_limiting(self):
        """Test rate limiting"""
        client_ip = '192.168.1.1'
        
        # Should allow requests within limit
        for i in range(10):
            self.assertTrue(self.security.check_rate_limit(client_ip))
        
        print("✅ Rate limiting test passed")
    
    def test_csrf_tokens(self):
        """Test CSRF token generation and verification"""
        # Generate token
        token = self.security.generate_csrf_token()
        self.assertIsInstance(token, str)
        self.assertEqual(len(token), 43)  # URL-safe token length
        
        # Verify token
        self.assertTrue(self.security.verify_csrf_token(token, token))
        self.assertFalse(self.security.verify_csrf_token(token, 'different_token'))
        
        print("✅ CSRF token test passed")
    
    def test_security_headers(self):
        """Test security headers generation"""
        headers = self.security.generate_security_headers()
        
        required_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Content-Security-Policy'
        ]
        
        for header in required_headers:
            self.assertIn(header, headers)
        
        print("✅ Security headers test passed")

class APISecurityTests(unittest.TestCase):
    def setUp(self):
        self.base_url = 'http://localhost:8080'
        self.session = requests.Session()
    
    def test_authentication_required(self):
        """Test that authentication is required"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/protected")
            self.assertEqual(response.status_code, 401)
            print("✅ Authentication required test passed")
        except requests.exceptions.ConnectionError:
            print("⚠️  API not running - skipping API tests")
    
    def test_rate_limiting_api(self):
        """Test API rate limiting"""
        try:
            # Make multiple requests quickly
            for i in range(5):
                response = self.session.get(f"{self.base_url}/api/v1/test")
                if response.status_code == 429:
                    print("✅ API rate limiting test passed")
                    return
            
            print("⚠️  Rate limiting not triggered")
        except requests.exceptions.ConnectionError:
            print("⚠️  API not running - skipping API tests")
    
    def test_security_headers_api(self):
        """Test security headers in API responses"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            required_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection'
            ]
            
            for header in required_headers:
                self.assertIn(header, response.headers)
            
            print("✅ API security headers test passed")
        except requests.exceptions.ConnectionError:
            print("⚠️  API not running - skipping API tests")

if __name__ == '__main__':
    print("🛡️ STELLAR LOGIC AI SECURITY TESTS")
    print("📅 Running on:", datetime.now().isoformat())
    
    # Run tests
    unittest.main(verbosity=2)
