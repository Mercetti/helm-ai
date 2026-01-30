"""
Error Response Middleware for Helm AI
Ensures all API endpoints return standardized error responses
"""

import os
import json
import logging
import time
import traceback
from typing import Dict, Any, Callable
from functools import wraps
from flask import Flask, request, g, jsonify, Response
from werkzeug.exceptions import HTTPException

try:
    from .standardized_errors import (
        StandardizedError, ValidationError, AuthenticationError, 
        AuthorizationError, NotFoundError, StandardizedErrorResponse,
        ErrorContext, create_error_context, log_error
    )
except ImportError:
    # Fallback for direct execution
    from standardized_errors import (
        StandardizedError, ValidationError, AuthenticationError, 
        AuthorizationError, NotFoundError, StandardizedErrorResponse,
        ErrorContext, create_error_context, log_error
    )

logger = logging.getLogger(__name__)

class ErrorMiddleware:
    """Middleware for enforcing standardized error responses"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.original_error_handlers = {}
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize middleware with Flask app"""
        self.app = app
        
        # Store original error handlers
        self._backup_original_handlers(app)
        
        # Register standardized error handlers
        self._register_standardized_handlers(app)
        
        # Register request context processor
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        # Register teardown handlers
        app.teardown_request(self._teardown_request)
        
        logger.info("Error middleware initialized")
    
    def _backup_original_handlers(self, app: Flask):
        """Backup original error handlers"""
        # Store original handlers for potential restoration
        for code, handler in app.error_handler_spec.get(None, {}).items():
            self.original_error_handlers[code] = handler
    
    def _register_standardized_handlers(self, app: Flask):
        """Register standardized error handlers"""
        
        # Handle all exceptions
        @app.errorhandler(Exception)
        def handle_all_exceptions(error):
            return self._handle_exception(error)
        
        # Handle HTTP exceptions
        @app.errorhandler(HTTPException)
        def handle_http_exceptions(error):
            return self._handle_http_exception(error)
        
        # Handle specific HTTP status codes
        @app.errorhandler(400)
        def handle_400(error):
            return self._create_standardized_response(
                ValidationError("Bad request", details={"original_error": str(error)})
            )
        
        @app.errorhandler(401)
        def handle_401(error):
            return self._create_standardized_response(
                AuthenticationError("Unauthorized", details={"original_error": str(error)})
            )
        
        @app.errorhandler(403)
        def handle_403(error):
            return self._create_standardized_response(
                AuthorizationError("Forbidden", details={"original_error": str(error)})
            )
        
        @app.errorhandler(404)
        def handle_404(error):
            return self._create_standardized_response(
                NotFoundError("Resource not found", 
                            resource_type="endpoint", 
                            resource_id=request.endpoint,
                            details={"original_error": str(error)})
            )
        
        @app.errorhandler(405)
        def handle_405(error):
            return self._create_standardized_response(
                ValidationError(f"Method {request.method} not allowed",
                              field="method",
                              value=request.method,
                              details={"original_error": str(error)})
            )
        
        @app.errorhandler(409)
        def handle_409(error):
            return self._create_standardized_response(
                ValidationError("Resource conflict", details={"original_error": str(error)})
            )
        
        @app.errorhandler(422)
        def handle_422(error):
            return self._create_standardized_response(
                ValidationError("Unprocessable entity", details={"original_error": str(error)})
            )
        
        @app.errorhandler(429)
        def handle_429(error):
            return self._create_standardized_response(
                ValidationError("Rate limit exceeded", details={"original_error": str(error)})
            )
        
        @app.errorhandler(500)
        def handle_500(error):
            return self._create_standardized_response(
                ValidationError("Internal server error", details={"original_error": str(error)})
            )
        
        @app.errorhandler(502)
        def handle_502(error):
            return self._create_standardized_response(
                ValidationError("Bad gateway", details={"original_error": str(error)})
            )
    
    def _before_request(self):
        """Before request processing"""
        # Generate request ID if not present
        if not hasattr(g, 'request_id'):
            import uuid
            g.request_id = str(uuid.uuid4())
        
        # Store request start time
        g.request_start_time = time.time()
        
        # Store request details for error context
        g.request_method = request.method
        g.request_endpoint = request.endpoint
        g.request_path = request.path
    
    def _after_request(self, response):
        """After request processing"""
        # Add standard headers to all responses
        if not response.headers.get('X-Request-ID'):
            response.headers['X-Request-ID'] = getattr(g, 'request_id', '')
        
        # Add processing time header
        if hasattr(g, 'request_start_time'):
            import time
            processing_time = time.time() - g.request_start_time
            response.headers['X-Processing-Time'] = f"{processing_time:.3f}s"
        
        # Add API version header
        response.headers['X-API-Version'] = os.getenv('API_VERSION', '1.0')
        
        # Ensure content-type is set for JSON responses
        if response.is_json and not response.headers.get('Content-Type'):
            response.headers['Content-Type'] = 'application/json'
        
        return response
    
    def _teardown_request(self, exception):
        """Teardown request processing"""
        if exception:
            # Log any unhandled exceptions
            self._log_unhandled_exception(exception)
    
    def _handle_exception(self, error: Exception) -> Response:
        """Handle all exceptions"""
        # Create error context
        context = self._create_error_context()
        
        # Convert to standardized error if needed
        if not isinstance(error, StandardizedError):
            error = self._convert_to_standardized_error(error, context)
        else:
            error.context = context
        
        # Log the error
        log_error(error)
        
        # Create response
        return self._create_standardized_response(error)
    
    def _handle_http_exception(self, error: HTTPException) -> Response:
        """Handle HTTP exceptions"""
        # Create error context
        context = self._create_error_context()
        
        # Convert to standardized error
        standardized_error = self._convert_http_exception(error, context)
        
        # Log the error
        log_error(standardized_error)
        
        # Create response
        return self._create_standardized_response(standardized_error)
    
    def _convert_to_standardized_error(self, error: Exception, context: ErrorContext) -> StandardizedError:
        """Convert generic exception to standardized error"""
        from .standardized_errors import SystemError
        
        # Map common exception types to standardized errors
        if isinstance(error, ValueError):
            return ValidationError(str(error), context=context)
        elif isinstance(error, KeyError):
            return ValidationError(f"Missing required field: {str(error)}", context=context)
        elif isinstance(error, PermissionError):
            return AuthorizationError(str(error), context=context)
        elif isinstance(error, FileNotFoundError):
            return NotFoundError(str(error), resource_type="file", context=context)
        else:
            return SystemError(str(error), context=context, cause=error)
    
    def _convert_http_exception(self, error: HTTPException, context: ErrorContext) -> StandardizedError:
        """Convert HTTP exception to standardized error"""
        status_code = error.code
        
        if status_code == 400:
            return ValidationError(error.description or "Bad request", context=context)
        elif status_code == 401:
            return AuthenticationError(error.description or "Unauthorized", context=context)
        elif status_code == 403:
            return AuthorizationError(error.description or "Forbidden", context=context)
        elif status_code == 404:
            return NotFoundError(error.description or "Resource not found", context=context)
        elif status_code == 405:
            return ValidationError(error.description or "Method not allowed", context=context)
        elif status_code == 409:
            return ValidationError(error.description or "Resource conflict", context=context)
        elif status_code == 422:
            return ValidationError(error.description or "Unprocessable entity", context=context)
        elif status_code == 429:
            return ValidationError(error.description or "Rate limit exceeded", context=context)
        elif status_code == 500:
            return ValidationError(error.description or "Internal server error", context=context)
        elif status_code == 502:
            return ValidationError(error.description or "Bad gateway", context=context)
        else:
            return ValidationError(error.description or f"HTTP {status_code} error", context=context)
    
    def _create_error_context(self) -> ErrorContext:
        """Create error context from current request"""
        return create_error_context(request)
    
    def _create_standardized_response(self, error: StandardizedError) -> Response:
        """Create standardized error response"""
        include_stack_trace = os.getenv('FLASK_ENV') == 'development'
        response_dict = error.to_response_dict(include_stack_trace)
        
        response = jsonify(response_dict)
        response.status_code = error.http_status_code
        
        # Add standard headers
        response.headers['Content-Type'] = 'application/json'
        response.headers['X-Error-Code'] = error.error_code
        response.headers['X-Error-Category'] = error.category.value
        response.headers['X-Error-Severity'] = error.severity.value
        
        return response
    
    def _log_unhandled_exception(self, error: Exception):
        """Log unhandled exceptions"""
        logger.error(f"Unhandled exception in request {getattr(g, 'request_id', 'unknown')}: {error}")
        logger.error(f"Exception details: {traceback.format_exc()}")

# Decorator for endpoint error handling
def endpoint_error_handler(func):
    """Decorator for consistent endpoint error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StandardizedError:
            raise  # Re-raise standardized errors
        except Exception as e:
            # Convert to standardized error
            context = create_error_context(request)
            raise ValidationError(
                message=f"Endpoint error: {str(e)}",
                context=context,
                cause=e
            )
    return wrapper

# Decorator for API endpoint validation
def validate_endpoint_response(func):
    """Decorator to validate endpoint responses are standardized"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # Check if response is a Flask Response
        if hasattr(result, 'get_json'):
            try:
                json_data = result.get_json()
                if json_data and 'success' not in json_data:
                    logger.warning(f"Endpoint {request.endpoint} returned non-standard response format")
            except:
                pass
        
        return result
    return wrapper

# Utility functions for common error patterns
def handle_validation_errors(validation_errors: Dict[str, str]) -> StandardizedError:
    """Handle multiple validation errors"""
    if len(validation_errors) == 1:
        field, message = next(iter(validation_errors.items()))
        return ValidationError(message, field=field)
    else:
        return ValidationError(
            "Multiple validation errors occurred",
            details={"validation_errors": validation_errors}
        )

def handle_database_errors(error: Exception, operation: str = "database operation") -> StandardizedError:
    """Handle database errors"""
    from .standardized_errors import SystemError
    
    error_str = str(error).lower()
    
    if "connection" in error_str or "timeout" in error_str:
        return SystemError(
            f"Database connection failed during {operation}",
            component="database",
            details={"operation": operation, "original_error": str(error)},
            cause=error
        )
    elif "constraint" in error_str or "duplicate" in error_str:
        return ValidationError(
            f"Data constraint violation during {operation}",
            details={"operation": operation, "original_error": str(error)},
            cause=error
        )
    elif "not found" in error_str:
        return NotFoundError(
            f"Data not found during {operation}",
            resource_type="database_record",
            details={"operation": operation, "original_error": str(error)},
            cause=error
        )
    else:
        return SystemError(
            f"Database error during {operation}",
            component="database",
            details={"operation": operation, "original_error": str(error)},
            cause=error
        )

def handle_external_service_errors(error: Exception, service_name: str, operation: str = None) -> StandardizedError:
    """Handle external service errors"""
    from .standardized_errors import ExternalServiceError
    
    error_str = str(error).lower()
    
    if "timeout" in error_str:
        return ExternalServiceError(
            f"Service {service_name} timeout",
            service_name=service_name,
            service_status="timeout",
            details={"operation": operation, "original_error": str(error)},
            cause=error
        )
    elif "connection" in error_str:
        return ExternalServiceError(
            f"Failed to connect to service {service_name}",
            service_name=service_name,
            service_status="connection_failed",
            details={"operation": operation, "original_error": str(error)},
            cause=error
        )
    elif "rate limit" in error_str:
        return ExternalServiceError(
            f"Service {service_name} rate limit exceeded",
            service_name=service_name,
            service_status="rate_limited",
            details={"operation": operation, "original_error": str(error)},
            cause=error
        )
    else:
        return ExternalServiceError(
            f"Service {service_name} error",
            service_name=service_name,
            service_status="error",
            details={"operation": operation, "original_error": str(error)},
            cause=error
        )

# Global middleware instance
error_middleware = ErrorMiddleware()
