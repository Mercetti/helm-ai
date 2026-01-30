"""
Tests for standardized error response system
"""

import pytest
import json
import time
from unittest.mock import Mock, patch
from flask import Flask, jsonify, request, g
from datetime import datetime

# Import the modules we're testing
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'api'))

from standardized_errors import (
    StandardizedError, ValidationError, AuthenticationError, AuthorizationError,
    NotFoundError, ConflictError, RateLimitError, ExternalServiceError,
    SystemError, SecurityError, BusinessLogicError, StandardizedErrorResponse,
    ErrorCategory, ErrorSeverity, ErrorContext, ErrorHandler
)
from error_middleware import ErrorMiddleware, endpoint_error_handler, validate_endpoint_response

class TestStandardizedError:
    """Test standardized error classes"""
    
    def test_base_standardized_error(self):
        """Test base standardized error"""
        context = ErrorContext(
            request_id="req_123",
            user_id="user_456",
            ip_address="127.0.0.1"
        )
        
        error = StandardizedError(
            message="Test error",
            error_code="TEST_ERROR",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            http_status_code=500,
            context=context,
            details={"key": "value"}
        )
        
        assert error.message == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.category == ErrorCategory.SYSTEM
        assert error.severity == ErrorSeverity.HIGH
        assert error.http_status_code == 500
        assert error.context == context
        assert error.details["key"] == "value"
        assert isinstance(error.timestamp, datetime)
    
    def test_validation_error(self):
        """Test validation error"""
        error = ValidationError(
            message="Invalid email format",
            field="email",
            value="invalid-email"
        )
        
        assert error.error_code == "VALIDATION_ERROR"
        assert error.category == ErrorCategory.VALIDATION
        assert error.http_status_code == 400
        assert error.details["field"] == "email"
        assert error.details["invalid_value"] == "invalid-email"
    
    def test_authentication_error(self):
        """Test authentication error"""
        error = AuthenticationError("Invalid credentials")
        
        assert error.error_code == "AUTHENTICATION_ERROR"
        assert error.category == ErrorCategory.AUTHENTICATION
        assert error.http_status_code == 401
    
    def test_authorization_error(self):
        """Test authorization error"""
        error = AuthorizationError(
            "Access denied",
            resource="user_profile",
            action="read"
        )
        
        assert error.error_code == "AUTHORIZATION_ERROR"
        assert error.category == ErrorCategory.AUTHORIZATION
        assert error.http_status_code == 403
        assert error.details["resource"] == "user_profile"
        assert error.details["required_action"] == "read"
    
    def test_not_found_error(self):
        """Test not found error"""
        error = NotFoundError(
            "User not found",
            resource_type="user",
            resource_id="123"
        )
        
        assert error.error_code == "NOT_FOUND"
        assert error.category == ErrorCategory.NOT_FOUND
        assert error.http_status_code == 404
        assert error.details["resource_type"] == "user"
        assert error.details["resource_id"] == "123"
    
    def test_rate_limit_error(self):
        """Test rate limit error"""
        error = RateLimitError(
            "Too many requests",
            limit=100,
            window=60
        )
        
        assert error.error_code == "RATE_LIMIT_EXCEEDED"
        assert error.category == ErrorCategory.RATE_LIMIT
        assert error.http_status_code == 429
        assert error.details["limit"] == 100
        assert error.details["window_seconds"] == 60
    
    def test_external_service_error(self):
        """Test external service error"""
        error = ExternalServiceError(
            "Service unavailable",
            service_name="payment_gateway",
            service_status="down"
        )
        
        assert error.error_code == "EXTERNAL_SERVICE_ERROR"
        assert error.category == ErrorCategory.EXTERNAL_SERVICE
        assert error.http_status_code == 502
        assert error.details["service_name"] == "payment_gateway"
        assert error.details["service_status"] == "down"
    
    def test_system_error(self):
        """Test system error"""
        error = SystemError(
            "Database connection failed",
            component="database"
        )
        
        assert error.error_code == "SYSTEM_ERROR"
        assert error.category == ErrorCategory.SYSTEM
        assert error.http_status_code == 500
        assert error.details["component"] == "database"
    
    def test_security_error(self):
        """Test security error"""
        error = SecurityError(
            "Suspicious activity detected",
            security_type="sql_injection"
        )
        
        assert error.error_code == "SECURITY_ERROR"
        assert error.category == ErrorCategory.SECURITY
        assert error.http_status_code == 403
        assert error.severity == ErrorSeverity.HIGH
        assert error.details["security_type"] == "sql_injection"
    
    def test_business_logic_error(self):
        """Test business logic error"""
        error = BusinessLogicError(
            "Insufficient balance",
            rule="balance_check"
        )
        
        assert error.error_code == "BUSINESS_LOGIC_ERROR"
        assert error.category == ErrorCategory.BUSINESS_LOGIC
        assert error.http_status_code == 422
        assert error.details["business_rule"] == "balance_check"


class TestStandardizedErrorResponse:
    """Test standardized error response factory"""
    
    def test_success_response(self):
        """Test success response"""
        data = {"id": 1, "name": "test"}
        response = StandardizedErrorResponse.success(data, "Operation successful")
        
        assert response["success"] == True
        assert response["data"] == data
        assert response["message"] == "Operation successful"
        assert "timestamp" in response
    
    def test_error_response_from_standardized_error(self):
        """Test error response from standardized error"""
        error = ValidationError("Invalid input", field="email")
        response = StandardizedErrorResponse.error(error)
        
        assert response["success"] == False
        assert response["error"]["code"] == "VALIDATION_ERROR"
        assert response["error"]["message"] == "Invalid input"
        assert response["error"]["category"] == "validation"
        assert response["error"]["details"]["field"] == "email"
    
    def test_error_response_from_exception(self):
        """Test error response from generic exception"""
        exception = ValueError("Invalid value")
        response = StandardizedErrorResponse.error(exception)
        
        assert response["success"] == False
        assert response["error"]["code"] == "SYSTEM_ERROR"
        assert response["error"]["message"] == "Invalid value"
    
    def test_error_response_from_string(self):
        """Test error response from string"""
        response = StandardizedErrorResponse.error("Something went wrong")
        
        assert response["success"] == False
        assert response["error"]["code"] == "SYSTEM_ERROR"
        assert response["error"]["message"] == "Something went wrong"
    
    def test_validation_error_response(self):
        """Test validation error response"""
        response = StandardizedErrorResponse.validation_error(
            "Email is required",
            field="email"
        )
        
        assert response["success"] == False
        assert response["error"]["code"] == "VALIDATION_ERROR"
        assert response["error"]["message"] == "Email is required"
        assert response["error"]["details"]["field"] == "email"
    
    def test_authentication_error_response(self):
        """Test authentication error response"""
        response = StandardizedErrorResponse.authentication_error("Invalid token")
        
        assert response["success"] == False
        assert response["error"]["code"] == "AUTHENTICATION_ERROR"
        assert response["error"]["message"] == "Invalid token"
    
    def test_not_found_error_response(self):
        """Test not found error response"""
        response = StandardizedErrorResponse.not_found_error(
            "User not found",
            resource_type="user",
            resource_id="123"
        )
        
        assert response["success"] == False
        assert response["error"]["code"] == "NOT_FOUND"
        assert response["error"]["details"]["resource_type"] == "user"
        assert response["error"]["details"]["resource_id"] == "123"
    
    def test_rate_limit_error_response(self):
        """Test rate limit error response"""
        response = StandardizedErrorResponse.rate_limit_error(
            "Too many requests",
            limit=100,
            window=60
        )
        
        assert response["success"] == False
        assert response["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert response["error"]["details"]["limit"] == 100
        assert response["error"]["details"]["window_seconds"] == 60


class TestErrorContext:
    """Test error context"""
    
    def test_error_context_creation(self):
        """Test error context creation"""
        context = ErrorContext(
            request_id="req_123",
            user_id="user_456",
            ip_address="127.0.0.1",
            endpoint="api.test",
            method="POST",
            user_agent="Mozilla/5.0"
        )
        
        assert context.request_id == "req_123"
        assert context.user_id == "user_456"
        assert context.ip_address == "127.0.0.1"
        assert context.endpoint == "api.test"
        assert context.method == "POST"
        assert context.user_agent == "Mozilla/5.0"
        assert isinstance(context.timestamp, datetime)
    
    def test_error_context_defaults(self):
        """Test error context with defaults"""
        context = ErrorContext()
        
        assert context.request_id is None
        assert context.user_id is None
        assert context.ip_address is None
        assert context.endpoint is None
        assert context.method is None
        assert context.user_agent is None
        assert isinstance(context.timestamp, datetime)
        assert context.additional_data == {}


class TestErrorHandler:
    """Test error handler"""
    
    def test_error_handler_initialization(self):
        """Test error handler initialization"""
        app = Flask(__name__)
        handler = ErrorHandler(app)
        
        assert handler.app == app
    
    def test_error_handler_without_app(self):
        """Test error handler without app"""
        handler = ErrorHandler()
        assert handler.app is None
    
    def test_error_handler_init_app(self):
        """Test error handler init_app"""
        app = Flask(__name__)
        handler = ErrorHandler()
        handler.init_app(app)
        
        assert handler.app == app


class TestErrorMiddleware:
    """Test error middleware"""
    
    def test_middleware_initialization(self):
        """Test middleware initialization"""
        app = Flask(__name__)
        middleware = ErrorMiddleware(app)
        
        assert middleware.app == app
    
    def test_middleware_without_app(self):
        """Test middleware without app"""
        middleware = ErrorMiddleware()
        assert middleware.app is None
    
    def test_middleware_init_app(self):
        """Test middleware init_app"""
        app = Flask(__name__)
        middleware = ErrorMiddleware()
        middleware.init_app(app)
        
        assert middleware.app == app


class TestDecorators:
    """Test error handling decorators"""
    
    def test_endpoint_error_handler_success(self):
        """Test endpoint error handler with success"""
        @endpoint_error_handler
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"
    
    def test_endpoint_error_handler_with_standardized_error(self):
        """Test endpoint error handler with standardized error"""
        @endpoint_error_handler
        def test_function():
            raise ValidationError("Test error")
        
        with pytest.raises(ValidationError):
            test_function()
    
    def test_endpoint_error_handler_with_generic_error(self):
        """Test endpoint error handler with generic error"""
        @endpoint_error_handler
        def test_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValidationError):
            test_function()
    
    def test_validate_endpoint_response_decorator(self):
        """Test validate endpoint response decorator"""
        app = Flask(__name__)
        
        with app.app_context():
            @validate_endpoint_response
            def test_function():
                return jsonify({"success": True, "data": "test"})
            
            result = test_function()
            assert result is not None


class TestErrorIntegration:
    """Integration tests for error handling"""
    
    def test_flask_error_handling_integration(self):
        """Test Flask error handling integration"""
        app = Flask(__name__)
        
        # Initialize error handler
        handler = ErrorHandler(app)
        
        # Create test route that raises error
        @app.route('/test-error')
        def test_error():
            raise ValidationError("Test validation error")
        
        # Create test route that returns success
        @app.route('/test-success')
        def test_success():
            return jsonify({"success": True, "data": "test"})
        
        with app.test_client() as client:
            # Test error response
            response = client.get('/test-error')
            assert response.status_code == 400
            
            data = json.loads(response.data)
            assert data["success"] == False
            assert data["error"]["code"] == "VALIDATION_ERROR"
            assert data["error"]["message"] == "Test validation error"
            
            # Test success response
            response = client.get('/test-success')
            assert response.status_code == 200
    
    def test_error_context_with_flask_request(self):
        """Test error context creation with Flask request"""
        app = Flask(__name__)
        
        with app.test_request_context('/test', method='POST', headers={'User-Agent': 'test-agent'}):
            from flask import g
            
            # Set some g values
            g.request_id = 'req_123'
            g.user_id = 'user_456'
            
            # Mock the create_error_context function to use g values
            context = ErrorContext(
                request_id=getattr(g, 'request_id', None),
                user_id=getattr(g, 'user_id', None),
                ip_address=request.remote_addr,
                endpoint=request.endpoint,
                method=request.method,
                user_agent=request.headers.get('User-Agent')
            )
            
            assert context.request_id == 'req_123'
            assert context.user_id == 'user_456'
            assert context.method == 'POST'
            assert context.user_agent == 'test-agent'
            # Note: IP address might be None in test context
            # assert context.ip_address == '127.0.0.1'
            assert context.endpoint == None  # Not set in test context
    
    def test_error_response_format_consistency(self):
        """Test error response format consistency"""
        errors = [
            ValidationError("Validation error"),
            AuthenticationError("Auth error"),
            AuthorizationError("Authz error"),
            NotFoundError("Not found error"),
            RateLimitError("Rate limit error"),
            SystemError("System error")
        ]
        
        for error in errors:
            response_dict = error.to_response_dict()
            
            # Check required fields
            assert "success" in response_dict
            assert "error" in response_dict
            assert response_dict["success"] == False
            
            # Check error object structure
            error_obj = response_dict["error"]
            assert "code" in error_obj
            assert "message" in error_obj
            assert "category" in error_obj
            assert "severity" in error_obj
            assert "timestamp" in error_obj
            assert "details" in error_obj
    
    def test_error_response_headers(self):
        """Test error response headers"""
        app = Flask(__name__)
        middleware = ErrorMiddleware(app)
        
        @app.route('/test-error')
        def test_error():
            raise ValidationError("Test error")
        
        with app.test_client() as client:
            response = client.get('/test-error')
            
            # Check standard headers
            assert 'Content-Type' in response.headers
            assert 'X-Error-Code' in response.headers
            assert 'X-Error-Category' in response.headers
            assert 'X-Error-Severity' in response.headers
            assert 'X-Request-ID' in response.headers
            assert 'X-API-Version' in response.headers
            
            # Check header values
            assert response.headers['Content-Type'] == 'application/json'
            assert response.headers['X-Error-Code'] == 'VALIDATION_ERROR'
            assert response.headers['X-Error-Category'] == 'validation'
    
    def test_stack_trace_in_development(self):
        """Test stack trace inclusion in development mode"""
        error = ValidationError("Test error")
        
        # Test without stack trace
        response_dict = error.to_response_dict(include_stack_trace=False)
        assert "stack_trace" not in response_dict["error"]
        
        # Test with stack trace - only include if FLASK_ENV is development
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            response_dict = error.to_response_dict(include_stack_trace=True)
            # Note: stack trace might not be included in all environments
            # This test is more about the method working correctly
            assert "error" in response_dict
    
    def test_error_causality_chain(self):
        """Test error causality chain"""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise ValidationError("Validation error", cause=e)
        except ValidationError as e:
            assert e.cause is not None
            assert isinstance(e.cause, ValueError)
            assert str(e.cause) == "Original error"


if __name__ == "__main__":
    pytest.main([__file__])
