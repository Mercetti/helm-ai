# Helm AI - Unified Error Handling System
"""
Centralized error handling for all Helm AI components.
Provides consistent error responses, logging, and monitoring.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import traceback
import logging
import json

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Severity levels for all errors"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for classification"""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATABASE = "database"
    EXTERNAL_SERVICE = "external_service"
    RATE_LIMIT = "rate_limit"
    SYSTEM = "system"
    BUSINESS_LOGIC = "business_logic"
    SECURITY = "security"

class HelmAIException(Exception):
    """Base exception for all Helm AI errors"""

    def __init__(
        self,
        message: str,
        error_code: str,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        http_status: int = 500
    ):
        self.message = message
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.cause = cause
        self.http_status = http_status
        self.timestamp = datetime.now(timezone.utc).isoformat()

        # Add stack trace if available
        if cause:
            self.context["cause"] = str(cause)
            self.context["traceback"] = traceback.format_exc()

        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API response format"""
        return {
            "success": False,
            "error": {
                "code": self.error_code,
                "message": self.message,
                "category": self.category.value,
                "severity": self.severity.value,
                "timestamp": self.timestamp,
                "context": self.context
            }
        }

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to standardized API response"""
        return self.to_dict()

    def log_error(self):
        """Log the error with appropriate level"""
        log_data = {
            "error_code": self.error_code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "context": self.context,
            "timestamp": self.timestamp
        }

        if self.cause:
            log_data["cause"] = str(self.cause)

        # Log at appropriate level
        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical(json.dumps(log_data))
        elif self.severity == ErrorSeverity.ERROR:
            logger.error(json.dumps(log_data))
        elif self.severity == ErrorSeverity.WARNING:
            logger.warning(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))

# Specialized exceptions
class ValidationException(HelmAIException):
    """Validation error exception"""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.WARNING,
            http_status=400,
            **kwargs
        )
        if field:
            self.context["field"] = field
        if value is not None:
            self.context["value"] = str(value)

class AuthenticationException(HelmAIException):
    """Authentication error exception"""

    def __init__(self, message: str = "Authentication required", **kwargs):
        super().__init__(
            message,
            error_code="AUTHENTICATION_ERROR",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.WARNING,
            http_status=401,
            **kwargs
        )

class AuthorizationException(HelmAIException):
    """Authorization error exception"""

    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(
            message,
            error_code="AUTHORIZATION_ERROR",
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.WARNING,
            http_status=403,
            **kwargs
        )

class NotFoundException(HelmAIException):
    """Resource not found exception"""

    def __init__(
        self,
        message: str,
        resource_type: str = "resource",
        resource_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            error_code="NOT_FOUND_ERROR",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.WARNING,
            http_status=404,
            **kwargs
        )
        self.context["resource_type"] = resource_type
        if resource_id:
            self.context["resource_id"] = resource_id

class DatabaseException(HelmAIException):
    """Database error exception"""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            error_code="DATABASE_ERROR",
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.ERROR,
            http_status=500,
            **kwargs
        )
        if operation:
            self.context["operation"] = operation
        if table:
            self.context["table"] = table

class RateLimitException(HelmAIException):
    """Rate limit exceeded exception"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: int = 0,
        window_seconds: int = 0,
        **kwargs
    ):
        super().__init__(
            message,
            error_code="RATE_LIMIT_EXCEEDED",
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.WARNING,
            http_status=429,
            **kwargs
        )
        self.context["limit"] = limit
        self.context["window_seconds"] = window_seconds

class ExternalServiceException(HelmAIException):
    """External service error exception"""

    def __init__(
        self,
        message: str,
        service_name: str = "external_service",
        service_error: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            error_code="EXTERNAL_SERVICE_ERROR",
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.ERROR,
            http_status=502,
            **kwargs
        )
        self.context["service_name"] = service_name
        if service_error:
            self.context["service_error"] = service_error

class BusinessLogicException(HelmAIException):
    """Business logic error exception"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="BUSINESS_LOGIC_ERROR",
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.ERROR,
            http_status=400,
            **kwargs
        )

class SecurityException(HelmAIException):
    """Security-related exception"""

    def __init__(self, message: str, threat_level: str = "medium", **kwargs):
        super().__init__(
            message,
            error_code="SECURITY_ERROR",
            category=ErrorCategory.SECURITY,
            severity=ErrorSeverity.ERROR,
            http_status=403,
            **kwargs
        )
        self.context["threat_level"] = threat_level

class SystemException(HelmAIException):
    """System error exception"""

    def __init__(
        self,
        message: str,
        component: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            error_code="SYSTEM_ERROR",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            http_status=500,
            **kwargs
        )
        if component:
            self.context["component"] = component

# Error handler decorator
def handle_errors(
    error_category: Optional[ErrorCategory] = None,
    reraise: bool = False,
    log_errors: bool = True
):
    """
    Decorator for handling errors in functions.

    Args:
        error_category: Category to assign to caught exceptions
        reraise: Whether to re-raise the exception after handling
        log_errors: Whether to log the errors
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HelmAIException:
                # Re-raise HelmAI exceptions as-is
                raise
            except Exception as e:
                # Convert other exceptions to HelmAI exceptions
                if error_category:
                    category = error_category
                else:
                    # Auto-detect category based on exception type
                    if isinstance(e, ValueError):
                        category = ErrorCategory.VALIDATION
                    elif isinstance(e, PermissionError):
                        category = ErrorCategory.AUTHORIZATION
                    elif isinstance(e, ConnectionError):
                        category = ErrorCategory.EXTERNAL_SERVICE
                    else:
                        category = ErrorCategory.SYSTEM

                # Create appropriate exception type based on category
                if category == ErrorCategory.VALIDATION:
                    helm_exception = ValidationException(
                        message=f"Validation error in {func.__name__}: {str(e)}",
                        context={"function": func.__name__, "args": str(args)},
                        cause=e
                    )
                elif category == ErrorCategory.AUTHORIZATION:
                    helm_exception = AuthenticationException(
                        message=f"Authorization error in {func.__name__}: {str(e)}",
                        context={"function": func.__name__, "args": str(args)},
                        cause=e
                    )
                elif category == ErrorCategory.EXTERNAL_SERVICE:
                    helm_exception = ExternalServiceException(
                        message=f"External service error in {func.__name__}: {str(e)}",
                        context={"function": func.__name__, "args": str(args)},
                        cause=e
                    )
                else:
                    helm_exception = SystemException(
                        message=f"Unexpected error in {func.__name__}: {str(e)}",
                        component=func.__name__,
                        context={"function": func.__name__, "args": str(args)},
                        cause=e
                    )

                if log_errors:
                    helm_exception.log_error()

                if reraise:
                    raise helm_exception

                # Return error response for API functions
                return helm_exception.to_api_response()

        return wrapper
    return decorator

# Safe execution decorator
def safe_execute(
    default_return=None,
    log_errors: bool = True,
    error_category: Optional[ErrorCategory] = None
):
    """
    Decorator for safe execution with error handling.

    Args:
        default_return: Default value to return on error
        log_errors: Whether to log errors
        error_category: Category for errors
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"Error in {func.__name__}: {e}")
                    logger.debug(traceback.format_exc())

                if callable(default_return):
                    return default_return()
                else:
                    return default_return
        return wrapper
    return decorator

# Global error handler instance
error_handler = None

def init_error_handler():
    """Initialize global error handler"""
    global error_handler
    if error_handler is None:
        error_handler = ErrorHandler()

class ErrorHandler:
    """Centralized error handler for Flask applications"""

    def __init__(self):
        self.error_counts = {}
        self._setup_error_handlers()

    def _setup_error_handlers(self):
        """Setup error handlers for Flask app"""
        pass  # Will be called when Flask app is available

    def format_error(self, exception: Exception) -> Dict[str, Any]:
        """Format exception for API response"""
        if isinstance(exception, HelmAIException):
            return exception.to_dict()
        else:
            # Convert to HelmAI exception first
            helm_exception = self.handle_exception(exception)
            return helm_exception.to_dict()
        """Convert any exception to HelmAI exception"""
        if isinstance(exception, HelmAIException):
            return exception

        # Convert based on exception type
        if isinstance(exception, ValueError):
            return ValidationException(str(exception), context=context)
        elif isinstance(exception, KeyError):
            return NotFoundException(f"Required key missing: {str(exception)}", context=context)
        elif isinstance(exception, PermissionError):
            return AuthorizationException(str(exception), context=context)
        elif isinstance(exception, ConnectionError):
            return ExternalServiceException("Connection error", service_error=str(exception), context=context)
        else:
            return SystemException(
                f"Unexpected error: {str(exception)}",
                context=context,
                cause=exception
            )

    def register_flask_handlers(self, app):
        """Register error handlers with Flask app"""
        @app.errorhandler(HelmAIException)
        def handle_helm_exception(e):
            e.log_error()
            return e.to_api_response(), e.http_status

        @app.errorhandler(400)
        def handle_400(e):
            return ValidationException("Bad request").to_api_response(), 400

        @app.errorhandler(401)
        def handle_401(e):
            return AuthenticationException().to_api_response(), 401

        @app.errorhandler(403)
        def handle_403(e):
            return AuthorizationException().to_api_response(), 403

        @app.errorhandler(404)
        def handle_404(e):
            return NotFoundException("Resource not found").to_api_response(), 404

        @app.errorhandler(429)
        def handle_429(e):
            return RateLimitException().to_api_response(), 429

        @app.errorhandler(500)
        def handle_500(e):
            return SystemException("Internal server error").to_api_response(), 500

# Initialize error handler
init_error_handler()