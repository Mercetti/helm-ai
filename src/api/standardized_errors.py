"""
Standardized Error Response System for Helm AI
Provides consistent error response formats across all API endpoints
"""

import os
import json
import logging
import traceback
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from flask import jsonify, Response

logger = logging.getLogger(__name__)

class ErrorCategory(Enum):
    """Standard error categories"""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    SYSTEM = "system"
    RATE_LIMIT = "rate_limit"
    SECURITY = "security"

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ErrorContext:
    """Error context information"""
    request_id: str = None
    user_id: str = None
    ip_address: str = None
    endpoint: str = None
    method: str = None
    user_agent: str = None
    timestamp: datetime = field(default_factory=datetime.now)
    additional_data: Dict[str, Any] = field(default_factory=dict)

class StandardizedError(Exception):
    """Base standardized error class"""
    
    def __init__(self, 
                 message: str,
                 error_code: str = None,
                 category: ErrorCategory = ErrorCategory.SYSTEM,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 http_status_code: int = 500,
                 context: ErrorContext = None,
                 details: Dict[str, Any] = None,
                 cause: Exception = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.category = category
        self.severity = severity
        self.http_status_code = http_status_code
        self.context = context
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.now()
    
    def to_response_dict(self, include_stack_trace: bool = False) -> Dict[str, Any]:
        """Convert error to standardized response dictionary"""
        response = {
            "success": False,
            "error": {
                "code": self.error_code,
                "message": self.message,
                "category": self.category.value,
                "severity": self.severity.value,
                "timestamp": self.timestamp.isoformat(),
                "details": self.details
            }
        }
        
        # Add context information if available
        if self.context:
            response["error"]["request_id"] = self.context.request_id
            response["error"]["user_id"] = self.context.user_id
            response["error"]["ip_address"] = self.context.ip_address
            response["error"]["endpoint"] = self.context.endpoint
            response["error"]["method"] = self.context.method
        
        # Add stack trace in development mode
        if include_stack_trace and os.getenv('FLASK_ENV') == 'development':
            response["error"]["stack_trace"] = traceback.format_exc()
        
        return response
    
    def to_flask_response(self, include_stack_trace: bool = False) -> Response:
        """Convert error to Flask response"""
        response_dict = self.to_response_dict(include_stack_trace)
        response = jsonify(response_dict)
        response.status_code = self.http_status_code
        
        # Add standard headers
        response.headers['Content-Type'] = 'application/json'
        response.headers['X-Error-Code'] = self.error_code
        response.headers['X-Error-Category'] = self.category.value
        
        return response

# Specific error classes
class ValidationError(StandardizedError):
    """Validation error"""
    
    def __init__(self, message: str, field: str = None, value: Any = None, **kwargs):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            category=ErrorCategory.VALIDATION,
            http_status_code=400,
            **kwargs
        )
        if field:
            self.details["field"] = field
        if value is not None:
            self.details["invalid_value"] = str(value)

class AuthenticationError(StandardizedError):
    """Authentication error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            category=ErrorCategory.AUTHENTICATION,
            http_status_code=401,
            **kwargs
        )

class AuthorizationError(StandardizedError):
    """Authorization error"""
    
    def __init__(self, message: str, resource: str = None, action: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            category=ErrorCategory.AUTHORIZATION,
            http_status_code=403,
            **kwargs
        )
        if resource:
            self.details["resource"] = resource
        if action:
            self.details["required_action"] = action

class NotFoundError(StandardizedError):
    """Resource not found error"""
    
    def __init__(self, message: str, resource_type: str = None, resource_id: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            category=ErrorCategory.NOT_FOUND,
            http_status_code=404,
            **kwargs
        )
        if resource_type:
            self.details["resource_type"] = resource_type
        if resource_id:
            self.details["resource_id"] = resource_id

class ConflictError(StandardizedError):
    """Conflict error"""
    
    def __init__(self, message: str, conflict_type: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            category=ErrorCategory.BUSINESS_LOGIC,
            http_status_code=409,
            **kwargs
        )
        if conflict_type:
            self.details["conflict_type"] = conflict_type

class RateLimitError(StandardizedError):
    """Rate limit error"""
    
    def __init__(self, message: str, limit: int = None, window: int = None, **kwargs):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            category=ErrorCategory.RATE_LIMIT,
            http_status_code=429,
            **kwargs
        )
        if limit:
            self.details["limit"] = limit
        if window:
            self.details["window_seconds"] = window

class ExternalServiceError(StandardizedError):
    """External service error"""
    
    def __init__(self, message: str, service_name: str = None, service_status: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            category=ErrorCategory.EXTERNAL_SERVICE,
            http_status_code=502,
            **kwargs
        )
        if service_name:
            self.details["service_name"] = service_name
        if service_status:
            self.details["service_status"] = service_status

class SystemError(StandardizedError):
    """System error"""
    
    def __init__(self, message: str, component: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="SYSTEM_ERROR",
            category=ErrorCategory.SYSTEM,
            http_status_code=500,
            **kwargs
        )
        if component:
            self.details["component"] = component

class SecurityError(StandardizedError):
    """Security error"""
    
    def __init__(self, message: str, security_type: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="SECURITY_ERROR",
            category=ErrorCategory.SECURITY,
            http_status_code=403,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        if security_type:
            self.details["security_type"] = security_type

class BusinessLogicError(StandardizedError):
    """Business logic error"""
    
    def __init__(self, message: str, rule: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            category=ErrorCategory.BUSINESS_LOGIC,
            http_status_code=422,
            **kwargs
        )
        if rule:
            self.details["business_rule"] = rule

class StandardizedErrorResponse:
    """Factory for creating standardized error responses"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Operation successful") -> Dict[str, Any]:
        """Create standardized success response"""
        response = {
            "success": True,
            "data": data,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        return response
    
    @staticmethod
    def error(error: Union[StandardizedError, Exception, str], 
              context: ErrorContext = None,
              include_stack_trace: bool = False) -> Dict[str, Any]:
        """Create standardized error response"""
        if isinstance(error, StandardizedError):
            return error.to_response_dict(include_stack_trace)
        elif isinstance(error, Exception):
            # Convert generic exception to SystemError
            system_error = SystemError(
                message=str(error),
                context=context,
                cause=error
            )
            return system_error.to_response_dict(include_stack_trace)
        elif isinstance(error, str):
            # Convert string to SystemError
            system_error = SystemError(
                message=error,
                context=context
            )
            return system_error.to_response_dict(include_stack_trace)
        else:
            # Fallback
            system_error = SystemError(
                message="Unknown error occurred",
                context=context
            )
            return system_error.to_response_dict(include_stack_trace)
    
    @staticmethod
    def validation_error(message: str, field: str = None, value: Any = None, 
                        context: ErrorContext = None) -> Dict[str, Any]:
        """Create validation error response"""
        error = ValidationError(message, field=field, value=value, context=context)
        return error.to_response_dict()
    
    @staticmethod
    def authentication_error(message: str, context: ErrorContext = None) -> Dict[str, Any]:
        """Create authentication error response"""
        error = AuthenticationError(message, context=context)
        return error.to_response_dict()
    
    @staticmethod
    def authorization_error(message: str, resource: str = None, action: str = None,
                          context: ErrorContext = None) -> Dict[str, Any]:
        """Create authorization error response"""
        error = AuthorizationError(message, resource=resource, action=action, context=context)
        return error.to_response_dict()
    
    @staticmethod
    def not_found_error(message: str, resource_type: str = None, resource_id: str = None,
                       context: ErrorContext = None) -> Dict[str, Any]:
        """Create not found error response"""
        error = NotFoundError(message, resource_type=resource_type, resource_id=resource_id, context=context)
        return error.to_response_dict()
    
    @staticmethod
    def rate_limit_error(message: str, limit: int = None, window: int = None,
                         context: ErrorContext = None) -> Dict[str, Any]:
        """Create rate limit error response"""
        error = RateLimitError(message, limit=limit, window=window, context=context)
        return error.to_response_dict()
    
    @staticmethod
    def external_service_error(message: str, service_name: str = None, service_status: str = None,
                              context: ErrorContext = None) -> Dict[str, Any]:
        """Create external service error response"""
        error = ExternalServiceError(message, service_name=service_name, service_status=service_status, context=context)
        return error.to_response_dict()
    
    @staticmethod
    def system_error(message: str, component: str = None, context: ErrorContext = None) -> Dict[str, Any]:
        """Create system error response"""
        error = SystemError(message, component=component, context=context)
        return error.to_response_dict()
    
    @staticmethod
    def security_error(message: str, security_type: str = None, context: ErrorContext = None) -> Dict[str, Any]:
        """Create security error response"""
        error = SecurityError(message, security_type=security_type, context=context)
        return error.to_response_dict()
    
    @staticmethod
    def business_logic_error(message: str, rule: str = None, context: ErrorContext = None) -> Dict[str, Any]:
        """Create business logic error response"""
        error = BusinessLogicError(message, rule=rule, context=context)
        return error.to_response_dict()

class ErrorHandler:
    """Centralized error handler for Flask applications"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize error handler with Flask app"""
        self.app = app
        
        # Register error handlers
        app.errorhandler(ValidationError)(self._handle_validation_error)
        app.errorhandler(AuthenticationError)(self._handle_authentication_error)
        app.errorhandler(AuthorizationError)(self._handle_authorization_error)
        app.errorhandler(NotFoundError)(self._handle_not_found_error)
        app.errorhandler(ConflictError)(self._handle_conflict_error)
        app.errorhandler(RateLimitError)(self._handle_rate_limit_error)
        app.errorhandler(ExternalServiceError)(self._handle_external_service_error)
        app.errorhandler(SystemError)(self._handle_system_error)
        app.errorhandler(SecurityError)(self._handle_security_error)
        app.errorhandler(BusinessLogicError)(self._handle_business_logic_error)
        app.errorhandler(Exception)(self._handle_generic_error)
        
        # Register HTTP error handlers
        app.errorhandler(400)(self._handle_400)
        app.errorhandler(401)(self._handle_401)
        app.errorhandler(403)(self._handle_403)
        app.errorhandler(404)(self._handle_404)
        app.errorhandler(405)(self._handle_405)
        app.errorhandler(409)(self._handle_409)
        app.errorhandler(422)(self._handle_422)
        app.errorhandler(429)(self._handle_429)
        app.errorhandler(500)(self._handle_500)
        app.errorhandler(502)(self._handle_502)
    
    def _handle_validation_error(self, error):
        """Handle validation errors"""
        return self._create_response(error)
    
    def _handle_authentication_error(self, error):
        """Handle authentication errors"""
        return self._create_response(error)
    
    def _handle_authorization_error(self, error):
        """Handle authorization errors"""
        return self._create_response(error)
    
    def _handle_not_found_error(self, error):
        """Handle not found errors"""
        return self._create_response(error)
    
    def _handle_conflict_error(self, error):
        """Handle conflict errors"""
        return self._create_response(error)
    
    def _handle_rate_limit_error(self, error):
        """Handle rate limit errors"""
        return self._create_response(error)
    
    def _handle_external_service_error(self, error):
        """Handle external service errors"""
        return self._create_response(error)
    
    def _handle_system_error(self, error):
        """Handle system errors"""
        return self._create_response(error)
    
    def _handle_security_error(self, error):
        """Handle security errors"""
        return self._create_response(error)
    
    def _handle_business_logic_error(self, error):
        """Handle business logic errors"""
        return self._create_response(error)
    
    def _handle_generic_error(self, error):
        """Handle generic exceptions"""
        # Convert to SystemError if not already a StandardizedError
        if not isinstance(error, StandardizedError):
            error = SystemError(
                message=str(error),
                cause=error
            )
        return self._create_response(error)
    
    def _handle_400(self, error):
        """Handle 400 Bad Request"""
        return self._create_response(ValidationError("Bad request"))
    
    def _handle_401(self, error):
        """Handle 401 Unauthorized"""
        return self._create_response(AuthenticationError("Unauthorized"))
    
    def _handle_403(self, error):
        """Handle 403 Forbidden"""
        return self._create_response(AuthorizationError("Forbidden"))
    
    def _handle_404(self, error):
        """Handle 404 Not Found"""
        return self._create_response(NotFoundError("Resource not found"))
    
    def _handle_405(self, error):
        """Handle 405 Method Not Allowed"""
        return self._create_response(BusinessLogicError("Method not allowed"))
    
    def _handle_409(self, error):
        """Handle 409 Conflict"""
        return self._create_response(ConflictError("Resource conflict"))
    
    def _handle_422(self, error):
        """Handle 422 Unprocessable Entity"""
        return self._create_response(ValidationError("Unprocessable entity"))
    
    def _handle_429(self, error):
        """Handle 429 Too Many Requests"""
        return self._create_response(RateLimitError("Rate limit exceeded"))
    
    def _handle_500(self, error):
        """Handle 500 Internal Server Error"""
        return self._create_response(SystemError("Internal server error"))
    
    def _handle_502(self, error):
        """Handle 502 Bad Gateway"""
        return self._create_response(ExternalServiceError("Bad gateway"))
    
    def _create_response(self, error: StandardizedError) -> Response:
        """Create Flask response from error"""
        include_stack_trace = os.getenv('FLASK_ENV') == 'development'
        return error.to_flask_response(include_stack_trace)

# Decorator for consistent error handling
def handle_errors(func):
    """Decorator for consistent error handling"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StandardizedError:
            raise  # Re-raise standardized errors
        except Exception as e:
            # Convert to SystemError
            raise SystemError(
                message=str(e),
                cause=e
            )
    return wrapper

# Utility functions
def create_error_context(request=None) -> ErrorContext:
    """Create error context from Flask request"""
    if not request:
        return ErrorContext()
    
    from flask import g
    
    return ErrorContext(
        request_id=getattr(g, 'request_id', None),
        user_id=getattr(g, 'user_id', None),
        ip_address=request.remote_addr,
        endpoint=request.endpoint,
        method=request.method,
        user_agent=request.headers.get('User-Agent')
    )

def log_error(error: StandardizedError, level: str = "error"):
    """Log standardized error"""
    log_message = f"{error.error_code}: {error.message}"
    
    if error.context:
        log_message += f" (Request: {error.context.request_id}, User: {error.context.user_id})"
    
    if error.details:
        log_message += f" Details: {json.dumps(error.details)}"
    
    if error.cause:
        log_message += f" Cause: {str(error.cause)}"
    
    getattr(logger, level)(log_message)
    
    # Log stack trace for critical errors
    if error.severity == ErrorSeverity.CRITICAL:
        logger.error(f"Critical error stack trace: {traceback.format_exc()}")

# Global error handler instance
error_handler = ErrorHandler()
