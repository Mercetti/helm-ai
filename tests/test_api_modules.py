"""
API modules test - focused on API endpoints, middleware, and validation
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, request, jsonify

def test_api_imports():
    """Test that API modules can be imported"""
    try:
        from src.api.middleware import api_middleware, APIResponse, require_auth, rate_limit
        from src.api.error_handling import error_handler, ValidationException, AuthenticationException
        from src.api.input_validation import input_validator, InputValidator
        from src.api.rate_limiting import rate_limit_manager, RateLimitException
        assert api_middleware is not None
        assert APIResponse is not None
        assert error_handler is not None
        assert input_validator is not None
        assert rate_limit_manager is not None
    except ImportError as e:
        pytest.fail(f"Failed to import API modules: {e}")

@pytest.mark.api
def test_api_response_creation():
    """Test API response creation"""
    from src.api.error_handling import APIResponse, ValidationException
    
    # Test success response
    success_response = APIResponse.success({"data": "test"}, "Success message")
    assert success_response is not None
    assert success_response["success"] is True
    assert success_response["data"]["data"] == "test"
    assert success_response["message"] == "Success message"
    assert "timestamp" in success_response
    
    # Test error response with exception
    validation_exc = ValidationException("Test error", field="test")
    error_response = APIResponse.error(validation_exc)
    assert error_response is not None
    assert error_response["success"] is False
    assert error_response["error"]["message"] == "Test error"
    assert error_response["error"]["error"] == "VALIDATION_ERROR"
    assert "timestamp" in error_response

@pytest.mark.api
def test_input_validation():
    """Test input validation functionality"""
    from src.api.input_validation import InputValidator, ValidationType
    
    # Test validator creation
    validator = InputValidator()
    assert validator is not None
    assert hasattr(validator, 'validate')
    assert hasattr(validator, 'create_schema')
    
    # Test schema creation
    schema = {
        'name': {'type': 'string', 'min_length': 2, 'max_length': 50, 'required': True},
        'email': {'type': 'email', 'required': True},
        'age': {'type': 'integer', 'min_value': 0, 'max_value': 120, 'required': False}
    }
    
    rules = validator.create_schema(schema)
    assert rules is not None
    assert 'name' in rules
    assert 'email' in rules
    assert 'age' in rules
    
    # Test validation with valid data
    valid_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'age': 25
    }
    
    # Apply rules to validator
    validator.rules = rules
    validated_data = validator.validate(valid_data)
    assert validated_data is not None
    assert validated_data['name'] == 'Test User'
    assert validated_data['email'] == 'test@example.com'
    assert validated_data['age'] == 25

@pytest.mark.api
def test_rate_limiting():
    """Test rate limiting functionality"""
    from src.api.rate_limiting import RateLimitException, RateLimitType, RateLimitAlgorithm
    
    # Test exception creation
    exception = RateLimitException(
        message="Rate limit exceeded",
        limit=100,
        window=60,
        context={"ip": "127.0.0.1"}
    )
    assert exception is not None
    assert str(exception) == "Rate limit exceeded"
    assert exception.limit == 100
    assert exception.window == 60
    assert exception.context["ip"] == "127.0.0.1"
    
    # Test rate limit manager
    from src.api.rate_limiting import rate_limit_manager
    
    # Test rate limit check
    result = rate_limit_manager.check_rate_limit("test_key", 10, 60)
    assert result is True  # First request should pass
    
    # Test rate limit exceeded
    for i in range(15):  # Exceed the limit of 10
        rate_limit_manager.check_rate_limit("test_key", 10, 60)
    
    exceeded = rate_limit_manager.check_rate_limit("test_key", 10, 60)
    assert exceeded is False  # Should be rate limited

@pytest.mark.api
def test_middleware_decorators():
    """Test middleware decorators"""
    from src.api.middleware import require_auth, rate_limit
    
    # Test decorator creation
    assert callable(require_auth)
    assert callable(rate_limit)
    
    # Test decorator application
    @require_auth
    def protected_function():
        return "protected"
    
    @rate_limit(requests_per_window=10, window_seconds=60)
    def rate_limited_function():
        return "rate_limited"
    
    assert callable(protected_function)
    assert callable(rate_limited_function)

@pytest.mark.api
def test_error_handling_exceptions():
    """Test error handling exceptions"""
    from src.api.error_handling import (
        ValidationException, 
        AuthenticationException, 
        BusinessException,
        SystemException
    )
    
    # Test validation exception
    validation_exc = ValidationException("Invalid input", field="email", value="invalid")
    assert validation_exc is not None
    assert validation_exc.http_status_code == 400
    assert validation_exc.error_code == "VALIDATION_ERROR"
    
    # Test authentication exception
    auth_exc = AuthenticationException("Unauthorized")
    assert auth_exc is not None
    assert auth_exc.http_status_code == 401
    assert auth_exc.error_code == "AUTHENTICATION_ERROR"
    
    # Test business exception
    business_exc = BusinessException("Business rule violation")
    assert business_exc is not None
    assert business_exc.http_status_code == 422
    assert business_exc.error_code == "BUSINESS_ERROR"
    
    # Test system exception
    system_exc = SystemException("System error")
    assert system_exc is not None
    assert system_exc.http_status_code == 500
    assert system_exc.error_code == "SYSTEM_ERROR"

@pytest.mark.api
def test_flask_integration():
    """Test Flask integration with API components"""
    from src.api.middleware import api_middleware, APIResponse
    from src.api.error_handling import error_handler
    
    # Create Flask app
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Initialize middleware
    api_middleware.init_app(app)
    
    # Test app has middleware attributes
    assert hasattr(app, 'before_request_funcs')
    assert hasattr(app, 'after_request_funcs')
    
    # Create test route
    @app.route('/test')
    def test_route():
        return jsonify(APIResponse.success({"test": "data"}))
    
    with app.test_client() as client:
        response = client.get('/test')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['test'] == "data"

@pytest.mark.api
def test_input_validation_types():
    """Test various input validation types"""
    from src.api.input_validation import InputValidator
    
    validator = InputValidator()
    
    # Test string validation
    schema = {
        'text': {'type': 'string', 'min_length': 5, 'max_length': 10, 'required': True}
    }
    validator.rules = validator.create_schema(schema)
    
    # Valid string
    valid_data = {'text': 'valid'}
    result = validator.validate(valid_data)
    assert result is not None
    assert result['text'] == 'valid'
    
    # Invalid string (too short)
    try:
        invalid_data = {'text': 'bad'}
        validator.validate(invalid_data)
        assert False, "Should have raised validation error"
    except ValueError:
        pass  # Expected
    
    # Test email validation
    email_schema = {
        'email': {'type': 'email', 'required': True}
    }
    validator.rules = validator.create_schema(email_schema)
    
    # Valid email
    valid_email = {'email': 'test@example.com'}
    result = validator.validate(valid_email)
    assert result is not None
    assert result['email'] == 'test@example.com'
    
    # Invalid email
    try:
        invalid_email = {'email': 'not-an-email'}
        validator.validate(invalid_email)
        assert False, "Should have raised validation error"
    except ValueError:
        pass  # Expected

@pytest.mark.api
def test_api_error_scenarios():
    """Test various API error scenarios"""
    from src.api.error_handling import ValidationException, AuthenticationException
    from src.api.middleware import api_middleware
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Initialize middleware
    api_middleware.init_app(app)
    
    # Create routes that raise exceptions
    @app.route('/validation-error')
    def validation_error():
        raise ValidationException("Invalid data", field="test")
    
    @app.route('/auth-error')
    def auth_error():
        raise AuthenticationException("Not authenticated")
    
    with app.test_client() as client:
        # Test validation error
        response = client.get('/validation-error')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['error'] == 'VALIDATION_ERROR'
        
        # Test authentication error
        response = client.get('/auth-error')
        assert response.status_code == 401
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['error'] == 'AUTHENTICATION_ERROR'

@pytest.mark.api
def test_rate_limiting_integration():
    """Test rate limiting integration with Flask"""
    from src.api.middleware import rate_limit
    from flask import Flask
    
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Create rate-limited route
    @app.route('/rate-limited')
    @rate_limit(requests_per_window=5, window_seconds=60)
    def rate_limited_route():
        return jsonify({"message": "success"})
    
    with app.test_client() as client:
        # First few requests should succeed
        for i in range(5):
            response = client.get('/rate-limited')
            assert response.status_code == 200
        
        # Sixth request should be rate limited
        response = client.get('/rate-limited')
        assert response.status_code == 429

@pytest.mark.api
def test_middleware_request_context():
    """Test middleware request context handling"""
    from src.api.middleware import api_middleware
    from flask import Flask, g
    
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Initialize middleware
    api_middleware.init_app(app)
    
    @app.route('/context-test')
    def context_test():
        # Check if middleware set request context
        assert hasattr(g, 'request_id')
        assert hasattr(g, 'start_time')
        return jsonify({
            'request_id': getattr(g, 'request_id', 'none'),
            'has_start_time': hasattr(g, 'start_time')
        })
    
    with app.test_client() as client:
        response = client.get('/context-test')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['request_id'] is not None
        assert data['has_start_time'] is True

@pytest.mark.api
def test_api_response_formats():
    """Test API response format consistency"""
    from src.api.error_handling import APIResponse, ValidationException
    
    # Test success response format
    success = APIResponse.success({"key": "value"})
    required_fields = ['success', 'message', 'data', 'timestamp']
    for field in required_fields:
        assert field in success
    
    # Test error response format
    error_exc = ValidationException("Test error")
    error = APIResponse.error(error_exc)
    required_error_fields = ['success', 'error', 'timestamp']
    for field in required_error_fields:
        assert field in error
    
    # Test error sub-format
    required_error_sub_fields = ['error', 'message', 'category', 'severity']
    for field in required_error_sub_fields:
        assert field in error['error']

@pytest.mark.api
def test_custom_validation_rules():
    """Test custom validation rules"""
    from src.api.input_validation import InputValidator
    
    validator = InputValidator()
    
    # Test custom schema with multiple rules
    schema = {
        'username': {
            'type': 'string',
            'min_length': 3,
            'max_length': 20,
            'pattern': '^[a-zA-Z0-9_]+$',
            'required': True
        },
        'password': {
            'type': 'string',
            'min_length': 8,
            'pattern': '^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d).+$',
            'required': True
        }
    }
    
    validator.rules = validator.create_schema(schema)
    
    # Valid data
    valid_data = {
        'username': 'test_user123',
        'password': 'Password123'
    }
    
    result = validator.validate(valid_data)
    assert result is not None
    assert result['username'] == 'test_user123'
    assert result['password'] == 'Password123'
    
    # Invalid username (contains invalid chars)
    try:
        invalid_data = {
            'username': 'test-user@123',
            'password': 'Password123'
        }
        validator.validate(invalid_data)
        assert False, "Should have raised validation error"
    except ValueError:
        pass  # Expected
    
    # Invalid password (doesn't meet complexity requirements)
    try:
        invalid_data = {
            'username': 'test_user123',
            'password': 'simple'
        }
        validator.validate(invalid_data)
        assert False, "Should have raised validation error"
    except ValueError:
        pass  # Expected

if __name__ == '__main__':
    pytest.main([__file__])
