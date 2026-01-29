"""
Integration Tests for API Endpoints
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.api.middleware import api_middleware, APIResponse, require_auth, rate_limit
from src.api.rate_limiting import rate_limit_manager
from src.api.error_handling import error_handler, ValidationException, AuthenticationException
from src.api.input_validation import input_validator, InputValidator


class TestAPIEndpoints:
    """Integration tests for API endpoints"""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing"""
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Initialize middleware
        api_middleware.init_app(app)
        
        # Test endpoints
        @app.route('/api/v1/health', methods=['GET'])
        def health_check():
            return jsonify(APIResponse.success({'status': 'healthy'}))
        
        @app.route('/api/v1/users', methods=['GET', 'POST'])
        def users():
            if request.method == 'GET':
                return jsonify(APIResponse.success({'users': []}))
            else:
                data = request.get_json()
                return jsonify(APIResponse.success({'user': data}, 'User created'))
        
        @app.route('/api/v1/auth/login', methods=['POST'])
        def login():
            data = request.get_json()
            
            # Validate input
            schema = {
                'email': {'type': 'email', 'required': True},
                'password': {'type': 'string', 'min_length': 8, 'required': True}
            }
            
            # Create a temporary validator with this schema
            temp_validator = InputValidator()
            temp_validator.rules = input_validator.create_schema(schema)
            validated_data = temp_validator.validate(data)
            
            # Mock authentication
            if validated_data['email'] == 'test@example.com' and validated_data['password'] == 'password123':
                return jsonify(APIResponse.success({
                    'token': 'mock-jwt-token',
                    'user': {'id': 1, 'email': validated_data['email']}
                }))
            else:
                raise AuthenticationException("Invalid credentials")
        
        @app.route('/api/v1/protected', methods=['GET'])
        @require_auth
        def protected():
            return jsonify(APIResponse.success({'message': 'Protected endpoint accessed'}))
        
        @app.route('/api/v1/rate-limited', methods=['GET'])
        @rate_limit(requests_per_window=5, window_seconds=60)
        def rate_limited():
            return jsonify(APIResponse.success({'message': 'Rate limited endpoint'}))
        
        return app
    
    @pytest.mark.integration
    def test_health_check_endpoint(self, app):
        """Test health check endpoint"""
        with app.test_client() as client:
            response = client.get('/api/v1/health')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert data['data']['status'] == 'healthy'
    
    @pytest.mark.integration
    def test_users_get_endpoint(self, app):
        """Test users GET endpoint"""
        with app.test_client() as client:
            response = client.get('/api/v1/users')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert isinstance(data['data']['users'], list)
    
    @pytest.mark.integration
    def test_users_post_endpoint(self, app):
        """Test users POST endpoint"""
        user_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'plan': 'free'
        }
        
        with app.test_client() as client:
            response = client.post(
                '/api/v1/users',
                data=json.dumps(user_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert data['data']['user']['email'] == user_data['email']
    
    @pytest.mark.integration
    def test_login_success(self, app):
        """Test successful login"""
        login_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        
        with app.test_client() as client:
            response = client.post(
                '/api/v1/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert 'token' in data['data']
            assert data['data']['user']['email'] == login_data['email']
    
    @pytest.mark.integration
    def test_login_invalid_credentials(self, app):
        """Test login with invalid credentials"""
        login_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        with app.test_client() as client:
            response = client.post(
                '/api/v1/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            assert response.status_code == 401
            data = json.loads(response.data)
            
            assert data['success'] is False
            assert data['error']['error_code'] == 'AUTHENTICATION_ERROR'
    
    @pytest.mark.integration
    def test_login_validation_error(self, app):
        """Test login with validation error"""
        invalid_data = {
            'email': 'invalid-email',
            'password': '123'  # Too short
        }
        
        with app.test_client() as client:
            response = client.post(
                '/api/v1/auth/login',
                data=json.dumps(invalid_data),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            
            assert data['success'] is False
            assert data['error']['error_code'] == 'VALIDATION_ERROR'
    
    @pytest.mark.integration
    def test_protected_endpoint_without_auth(self, app):
        """Test protected endpoint without authentication"""
        with app.test_client() as client:
            response = client.get('/api/v1/protected')
            
            assert response.status_code == 401
            data = json.loads(response.data)
            
            assert data['success'] is False
            assert data['error']['error_code'] == 'AUTHENTICATION_ERROR'
    
    @pytest.mark.integration
    @patch('src.auth.middleware.g')
    def test_protected_endpoint_with_auth(self, mock_g, app):
        """Test protected endpoint with authentication"""
        # Mock authenticated user
        mock_g.user_id = 'test_user_123'
        mock_g.authenticated = True
        
        with app.test_client() as client:
            response = client.get('/api/v1/protected')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert data['data']['message'] == 'Protected endpoint accessed'
    
    @pytest.mark.integration
    def test_rate_limiting_within_limit(self, app):
        """Test rate limiting within limits"""
        with app.test_client() as client:
            # Make requests within limit
            for i in range(3):
                response = client.get('/api/v1/rate-limited')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
    
    @pytest.mark.integration
    def test_rate_limiting_exceeded(self, app):
        """Test rate limiting when exceeded"""
        with app.test_client() as client:
            # Make requests to exceed limit
            responses = []
            for i in range(7):  # Exceeds limit of 5
                response = client.get('/api/v1/rate-limited')
                responses.append(response)
            
            # Check that some requests were rate limited
            rate_limited_count = sum(1 for r in responses if r.status_code == 429)
            assert rate_limited_count >= 2
            
            # Check that some requests succeeded
            success_count = sum(1 for r in responses if r.status_code == 200)
            assert success_count <= 5
    
    @pytest.mark.integration
    def test_rate_limiting_headers(self, app):
        """Test rate limiting response headers"""
        with app.test_client() as client:
            # Make request that should be rate limited
            for i in range(6):
                response = client.get('/api/v1/rate-limited')
                if response.status_code == 429:
                    # Check for rate limit headers
                    assert 'Retry-After' in response.headers
                    assert 'X-RateLimit-Limit' in response.headers
                    assert 'X-RateLimit-Remaining' in response.headers
                    break
    
    @pytest.mark.integration
    def test_cors_headers(self, app):
        """Test CORS headers"""
        with app.test_client() as client:
            # Preflight request
            response = client.options('/api/v1/users')
            
            assert response.status_code == 200
            assert 'Access-Control-Allow-Origin' in response.headers
            assert 'Access-Control-Allow-Methods' in response.headers
            assert 'Access-Control-Allow-Headers' in response.headers
    
    @pytest.mark.integration
    def test_security_headers(self, app):
        """Test security headers"""
        with app.test_client() as client:
            response = client.get('/api/v1/health')
            
            assert response.status_code == 200
            assert 'X-Content-Type-Options' in response.headers
            assert 'X-Frame-Options' in response.headers
            assert 'X-XSS-Protection' in response.headers
            assert 'Strict-Transport-Security' in response.headers
    
    @pytest.mark.integration
    def test_request_id_header(self, app):
        """Test request ID header"""
        with app.test_client() as client:
            response = client.get('/api/v1/health')
            
            assert response.status_code == 200
            assert 'X-Request-ID' in response.headers
            assert len(response.headers['X-Request-ID']) > 0
    
    @pytest.mark.integration
    def test_response_time_header(self, app):
        """Test response time header"""
        with app.test_client() as client:
            response = client.get('/api/v1/health')
            
            assert response.status_code == 200
            assert 'X-Response-Time' in response.headers
            # Response time should be in seconds format
            assert response.headers['X-Response-Time'].endswith('s')


class TestAPIErrorHandling:
    """Integration tests for API error handling"""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing"""
        from flask import Flask, request
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Initialize middleware
        api_middleware.init_app(app)
        
        # Test endpoints that raise exceptions
        @app.route('/api/v1/error/validation')
        def validation_error():
            raise ValidationException("Test validation error")
        
        @app.route('/api/v1/error/authentication')
        def authentication_error():
            raise AuthenticationException("Test authentication error")
        
        @app.route('/api/v1/error/business')
        def business_error():
            from src.api.error_handling import BusinessException
            raise BusinessException("Test business error")
        
        @app.route('/api/v1/error/system')
        def system_error():
            raise Exception("Test system error")
        
        return app
    
    @pytest.mark.integration
    def test_validation_error_handling(self, app):
        """Test validation error handling"""
        with app.test_client() as client:
            response = client.get('/api/v1/error/validation')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            
            assert data['success'] is False
            assert data['error']['error_code'] == 'VALIDATION_ERROR'
            assert 'Test validation error' in data['error']['message']
    
    @pytest.mark.integration
    def test_authentication_error_handling(self, app):
        """Test authentication error handling"""
        with app.test_client() as client:
            response = client.get('/api/v1/error/authentication')
            
            assert response.status_code == 401
            data = json.loads(response.data)
            
            assert data['success'] is False
            assert data['error']['error_code'] == 'AUTHENTICATION_ERROR'
            assert 'Test authentication error' in data['error']['message']
    
    @pytest.mark.integration
    def test_business_error_handling(self, app):
        """Test business error handling"""
        with app.test_client() as client:
            response = client.get('/api/v1/error/business')
            
            assert response.status_code == 422
            data = json.loads(response.data)
            
            assert data['success'] is False
            assert data['error']['error_code'] == 'BUSINESS_ERROR'
            assert 'Test business error' in data['error']['message']
    
    @pytest.mark.integration
    def test_system_error_handling(self, app):
        """Test system error handling"""
        with app.test_client() as client:
            response = client.get('/api/v1/error/system')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            
            assert data['success'] is False
            assert data['error']['error_code'] == 'SYSTEM_ERROR'
            assert 'Test system error' in data['error']['message']


class TestAPIInputValidation:
    """Integration tests for API input validation"""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing"""
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Initialize middleware
        api_middleware.init_app(app)
        
        # Test endpoints with validation
        @app.route('/api/v1/validate/string', methods=['POST'])
        def validate_string():
            schema = {
                'name': {'type': 'string', 'min_length': 2, 'max_length': 50, 'required': True},
                'description': {'type': 'string', 'max_length': 200, 'required': False}
            }
            
            # Create a temporary validator with this schema
            temp_validator = InputValidator()
            temp_validator.rules = input_validator.create_schema(schema)
            validated_data = temp_validator.validate(request.get_json())
            return jsonify(APIResponse.success(validated_data))
        
        @app.route('/api/v1/validate/email', methods=['POST'])
        def validate_email():
            schema = {
                'email': {'type': 'email', 'required': True},
                'name': {'type': 'string', 'required': False}
            }
            
            # Create a temporary validator with this schema
            temp_validator = InputValidator()
            temp_validator.rules = input_validator.create_schema(schema)
            validated_data = temp_validator.validate(request.get_json())
            return jsonify(APIResponse.success(validated_data))
        
        @app.route('/api/v1/validate/integer', methods=['POST'])
        def validate_integer():
            schema = {
                'age': {'type': 'integer', 'min_value': 0, 'max_value': 120, 'required': True},
                'score': {'type': 'integer', 'min_value': 0, 'max_value': 100, 'required': False}
            }
            
            # Create a temporary validator with this schema
            temp_validator = InputValidator()
            temp_validator.rules = input_validator.create_schema(schema)
            validated_data = temp_validator.validate(request.get_json())
            return jsonify(APIResponse.success(validated_data))
        
        return app
    
    @pytest.mark.integration
    def test_string_validation_success(self, app):
        """Test successful string validation"""
        data = {
            'name': 'Test User',
            'description': 'A test user description'
        }
        
        with app.test_client() as client:
            response = client.post(
                '/api/v1/validate/string',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            result = json.loads(response.data)
            
            assert result['success'] is True
            assert result['data']['name'] == data['name']
            assert result['data']['description'] == data['description']
    
    @pytest.mark.integration
    def test_string_validation_too_short(self, app):
        """Test string validation with too short name"""
        data = {
            'name': 'A',  # Too short
            'description': 'Valid description'
        }
        
        with app.test_client() as client:
            response = client.post(
                '/api/v1/validate/string',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            result = json.loads(response.data)
            
            assert result['success'] is False
            assert result['error']['error'] == 'VALIDATION_ERROR'
    
    @pytest.mark.integration
    def test_string_validation_too_long(self, app):
        """Test string validation with too long name"""
        data = {
            'name': 'A' * 51,  # Too long
            'description': 'Valid description'
        }
        
        with app.test_client() as client:
            response = client.post(
                '/api/v1/validate/string',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            result = json.loads(response.data)
            
            assert result['success'] is False
            assert result['error']['error'] == 'VALIDATION_ERROR'
    
    @pytest.mark.integration
    def test_email_validation_success(self, app):
        """Test successful email validation"""
        data = {
            'email': 'test@example.com',
            'name': 'Test User'
        }
        
        with app.test_client() as client:
            response = client.post(
                '/api/v1/validate/email',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            result = json.loads(response.data)
            
            assert result['success'] is True
            assert result['data']['email'] == data['email']
            assert result['data']['name'] == data['name']
    
    @pytest.mark.integration
    def test_email_validation_invalid(self, app):
        """Test email validation with invalid email"""
        data = {
            'email': 'invalid-email',
            'name': 'Test User'
        }
        
        with app.test_client() as client:
            response = client.post(
                '/api/v1/validate/email',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            result = json.loads(response.data)
            
            assert result['success'] is False
            assert result['error']['error'] == 'VALIDATION_ERROR'
    
    @pytest.mark.integration
    def test_integer_validation_success(self, app):
        """Test successful integer validation"""
        data = {
            'age': 25,
            'score': 85
        }
        
        with app.test_client() as client:
            response = client.post(
                '/api/v1/validate/integer',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            result = json.loads(response.data)
            
            assert result['success'] is True
            assert result['data']['age'] == data['age']
            assert result['data']['score'] == data['score']
    
    @pytest.mark.integration
    def test_integer_validation_out_of_range(self, app):
        """Test integer validation with out of range value"""
        data = {
            'age': 150,  # Too high
            'score': 85
        }
        
        with app.test_client() as client:
            response = client.post(
                '/api/v1/validate/integer',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            result = json.loads(response.data)
            
            assert result['success'] is False
            assert result['error']['error'] == 'VALIDATION_ERROR'


if __name__ == '__main__':
    pytest.main([__file__])
