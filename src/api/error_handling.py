"""
Helm AI API Error Handling
This module provides comprehensive error handling and custom exceptions
"""

import os
import json
import logging
import traceback
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import functools

logger = logging.getLogger(__name__)

class ErrorCategory(Enum):
    """Error categories"""
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

class HelmAIException(Exception):
    """Base exception class for Helm AI"""
    
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary"""
        return {
            "error": self.error_code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "request_id": self.context.request_id if self.context else None
        }

class ValidationException(HelmAIException):
    """Validation error exception"""
    
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

class AuthenticationException(HelmAIException):
    """Authentication error exception"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            category=ErrorCategory.AUTHENTICATION,
            http_status_code=401,
            **kwargs
        )

class AuthorizationException(HelmAIException):
    """Authorization error exception"""
    
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            category=ErrorCategory.AUTHORIZATION,
            http_status_code=403,
            **kwargs
        )

class NotFoundException(HelmAIException):
    """Resource not found exception"""
    
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

class BusinessException(HelmAIException):
    """Business logic error exception"""
    
    def __init__(self, message: str, business_rule: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="BUSINESS_ERROR",
            category=ErrorCategory.BUSINESS_LOGIC,
            http_status_code=422,
            **kwargs
        )
        if business_rule:
            self.details["business_rule"] = business_rule

class ExternalServiceException(HelmAIException):
    """External service error exception"""
    
    def __init__(self, message: str, service_name: str = None, service_error: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            category=ErrorCategory.EXTERNAL_SERVICE,
            http_status_code=502,
            **kwargs
        )
        if service_name:
            self.details["service_name"] = service_name
        if service_error:
            self.details["service_error"] = service_error

class RateLimitException(HelmAIException):
    """Rate limit exceeded exception"""
    
    def __init__(self, message: str = "Rate limit exceeded", limit: int = None, window: int = None, **kwargs):
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
            self.details["window"] = window

class SecurityException(HelmAIException):
    """Security-related exception"""
    
    def __init__(self, message: str, security_issue: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="SECURITY_ERROR",
            category=ErrorCategory.SECURITY,
            http_status_code=403,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        if security_issue:
            self.details["security_issue"] = security_issue

class SystemException(HelmAIException):
    """System error exception"""
    
    def __init__(self, message: str, system_component: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="SYSTEM_ERROR",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        if system_component:
            self.details["system_component"] = system_component

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self):
        self.error_loggers = {
            ErrorCategory.VALIDATION: logging.getLogger("helm_ai.errors.validation"),
            ErrorCategory.AUTHENTICATION: logging.getLogger("helm_ai.errors.auth"),
            ErrorCategory.AUTHORIZATION: logging.getLogger("helm_ai.errors.authz"),
            ErrorCategory.NOT_FOUND: logging.getLogger("helm_ai.errors.not_found"),
            ErrorCategory.BUSINESS_LOGIC: logging.getLogger("helm_ai.errors.business"),
            ErrorCategory.EXTERNAL_SERVICE: logging.getLogger("helm_ai.errors.external"),
            ErrorCategory.SYSTEM: logging.getLogger("helm_ai.errors.system"),
            ErrorCategory.RATE_LIMIT: logging.getLogger("helm_ai.errors.rate_limit"),
            ErrorCategory.SECURITY: logging.getLogger("helm_ai.errors.security")
        }
        
        # Configure error logging
        self._configure_error_logging()
    
    def _configure_error_logging(self):
        """Configure error logging with formatters"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create file handler for errors
        log_file = os.getenv('ERROR_LOG_FILE', os.path.join(os.getcwd(), 'logs', 'errors.log'))
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.ERROR)
        
        # Add handler to all error loggers
        for error_logger in self.error_loggers.values():
            error_logger.addHandler(file_handler)
            error_logger.setLevel(logging.ERROR)
    
    def handle_exception(self, exception: Exception, context: ErrorContext = None) -> HelmAIException:
        """Handle and log exception"""
        if isinstance(exception, HelmAIException):
            helm_exception = exception
        else:
            # Convert standard exception to HelmAIException
            helm_exception = self._convert_to_helm_exception(exception, context)
        
        # Log the exception
        self._log_exception(helm_exception)
        
        # Send to external monitoring if critical
        if helm_exception.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self._send_to_monitoring(helm_exception)
        
        return helm_exception
    
    def _convert_to_helm_exception(self, exception: Exception, context: ErrorContext = None) -> HelmAIException:
        """Convert standard exception to HelmAIException"""
        exception_type = type(exception).__name__
        message = str(exception)
        
        # Map common exceptions to HelmAI exceptions
        if isinstance(exception, ValueError):
            return ValidationException(message, context=context)
        elif isinstance(exception, KeyError):
            return NotFoundException(f"Required key missing: {message}", context=context)
        elif isinstance(exception, PermissionError):
            return AuthorizationException(message, context=context)
        elif isinstance(exception, ConnectionError):
            return ExternalServiceException("Connection error", service_error=message, context=context)
        elif isinstance(exception, TimeoutError):
            return ExternalServiceException("Timeout error", service_error=message, context=context)
        else:
            # Default to system exception
            return SystemException(
                f"Unexpected error: {message}",
                system_component=exception_type,
                context=context,
                cause=exception
            )
    
    def _log_exception(self, exception: HelmAIException):
        """Log exception with appropriate logger"""
        error_logger = self.error_loggers.get(exception.category, logger)
        
        log_data = {
            "error_code": exception.error_code,
            "message": exception.message,
            "category": exception.category.value,
            "severity": exception.severity.value,
            "http_status": exception.http_status_code,
            "details": exception.details,
            "timestamp": exception.timestamp.isoformat()
        }
        
        if exception.context:
            log_data.update({
                "request_id": exception.context.request_id,
                "user_id": exception.context.user_id,
                "ip_address": exception.context.ip_address,
                "endpoint": exception.context.endpoint,
                "method": exception.context.method
            })
        
        if exception.cause:
            log_data["cause"] = str(exception.cause)
            log_data["traceback"] = traceback.format_exc()
        
        # Log based on severity
        if exception.severity == ErrorSeverity.CRITICAL:
            error_logger.critical(json.dumps(log_data))
        elif exception.severity == ErrorSeverity.HIGH:
            error_logger.error(json.dumps(log_data))
        elif exception.severity == ErrorSeverity.MEDIUM:
            error_logger.warning(json.dumps(log_data))
        else:
            error_logger.info(json.dumps(log_data))
    
    def _send_to_monitoring(self, exception: HelmAIException):
        """Send critical errors to external monitoring"""
        try:
            # This would integrate with monitoring systems like PagerDuty, DataDog, etc.
            monitoring_data = {
                "alert_type": "error",
                "error_code": exception.error_code,
                "message": exception.message,
                "severity": exception.severity.value,
                "category": exception.category.value,
                "timestamp": exception.timestamp.isoformat(),
                "details": exception.details
            }
            
            if exception.context:
                monitoring_data.update({
                    "request_id": exception.context.request_id,
                    "user_id": exception.context.user_id,
                    "ip_address": exception.context.ip_address
                })
            
            # Log that we would send to monitoring
            logger.critical(f"MONITORING ALERT: {json.dumps(monitoring_data)}")
            
        except Exception as e:
            logger.error(f"Failed to send error to monitoring: {e}")
    
    def create_error_context(self, 
                           request_id: str = None,
                           user_id: str = None,
                           ip_address: str = None,
                           endpoint: str = None,
                           method: str = None,
                           user_agent: str = None,
                           **additional_data) -> ErrorContext:
        """Create error context"""
        return ErrorContext(
            request_id=request_id,
            user_id=user_id,
            ip_address=ip_address,
            endpoint=endpoint,
            method=method,
            user_agent=user_agent,
            additional_data=additional_data
        )
    
    def get_error_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get error statistics"""
        # This would typically query a database or log aggregation system
        # For now, return placeholder data
        return {
            "period_hours": hours,
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_severity": {},
            "top_errors": [],
            "error_rate": 0.0
        }


def handle_errors(error_category: ErrorCategory = None, reraise: bool = True):
    """Decorator for handling errors in functions"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Create context from function arguments if available
                context = None
                if args and hasattr(args[0], '__dict__'):
                    # Try to extract context from first argument (usually self)
                    obj = args[0]
                    context_data = {}
                    
                    for attr in ['request_id', 'user_id', 'ip_address', 'endpoint', 'method']:
                        if hasattr(obj, attr):
                            context_data[attr] = getattr(obj, attr)
                    
                    if context_data:
                        context = ErrorContext(**context_data)
                
                # Handle the exception
                handled_exception = error_handler.handle_exception(e, context)
                
                if reraise:
                    raise handled_exception
                
                # Return error response if not reraising
                return {
                    "error": handled_exception.to_dict(),
                    "status_code": handled_exception.http_status_code
                }
        
        return wrapper
    return decorator


def validate_input(validation_func=None, **validators):
    """Decorator for input validation"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract arguments for validation
            if args and hasattr(args[0], '__dict__'):
                obj = args[0]
                for field, validator in validators.items():
                    if hasattr(obj, field):
                        value = getattr(obj, field)
                        try:
                            if callable(validator):
                                validator(value)
                            else:
                                # Simple type checking
                                if not isinstance(value, validator):
                                    raise ValidationException(
                                        f"Invalid type for {field}: expected {validator.__name__}, got {type(value).__name__}",
                                        field=field,
                                        value=value
                                    )
                        except (ValueError, TypeError) as e:
                            raise ValidationException(
                                f"Validation failed for {field}: {str(e)}",
                                field=field,
                                value=value
                            )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def safe_execute(default_return=None, log_errors: bool = True):
    """Decorator for safe execution with error handling"""
    def decorator(func):
        @functools.wraps(func)
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


class APIResponse:
    """Standardized API response format"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Success", meta: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create success response"""
        response = {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        if meta:
            response["meta"] = meta
        
        return response
    
    @staticmethod
    def error(exception: HelmAIException, include_traceback: bool = False) -> Dict[str, Any]:
        """Create error response"""
        response = {
            "success": False,
            "error": exception.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        
        if include_traceback and exception.cause:
            response["traceback"] = traceback.format_exc()
        
        return response
    
    @staticmethod
    def validation_error(errors: List[Dict[str, Any]], message: str = "Validation failed") -> Dict[str, Any]:
        """Create validation error response"""
        return {
            "success": False,
            "error": {
                "error_code": "VALIDATION_ERROR",
                "message": message,
                "category": ErrorCategory.VALIDATION.value,
                "details": {"validation_errors": errors},
                "timestamp": datetime.now().isoformat()
            }
        }


# Global error handler instance
error_handler = ErrorHandler()
