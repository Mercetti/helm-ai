# Helm AI - Unified Logging Configuration
"""
Centralized logging configuration with JSON formatting,
structured logging, and performance monitoring.
"""

import os
import json
import logging
import logging.config
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path

class JsonFormatter(logging.Formatter):
    """Format logs as JSON for better parsing and analysis"""

    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        # Base log data
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.thread
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present and enabled
        if self.include_extra:
            # Standard extra fields
            extra_fields = [
                "request_id", "user_id", "session_id", "ip_address",
                "endpoint", "method", "status_code", "duration_ms",
                "component", "operation", "resource_type", "resource_id"
            ]

            for field in extra_fields:
                if hasattr(record, field):
                    log_data[field] = getattr(record, field)

            # Add any additional fields from record.__dict__
            for key, value in record.__dict__.items():
                if key not in [
                    'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                    'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                    'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                    'thread', 'threadName', 'processName', 'process', 'message'
                ] and not key.startswith('_'):
                    log_data[key] = value

        return json.dumps(log_data, default=str)

class PerformanceFormatter(logging.Formatter):
    """Formatter for performance logs with timing information"""

    def format(self, record: logging.LogRecord) -> str:
        """Format performance log record"""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "PERFORMANCE",
            "logger": record.name,
            "message": record.getMessage(),
            "operation": getattr(record, 'operation', 'unknown'),
            "duration_ms": getattr(record, 'duration_ms', 0),
            "component": getattr(record, 'component', 'unknown')
        }

        # Add additional performance metrics
        perf_fields = ['cpu_percent', 'memory_mb', 'connections_active', 'queue_size']
        for field in perf_fields:
            if hasattr(record, field):
                log_data[field] = getattr(record, field)

        return json.dumps(log_data, default=str)

def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get configured logger with JSON formatting.

    Args:
        name: Logger name (usually __name__)
        level: Optional log level override

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        if level:
            logger.setLevel(getattr(logging, level.upper()))
        return logger

    # Set log level
    if level:
        logger.setLevel(getattr(logging, level.upper()))
    else:
        # Default to INFO, but allow environment override
        default_level = os.getenv('LOG_LEVEL', 'INFO')
        logger.setLevel(getattr(logging, default_level.upper()))

    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JsonFormatter())

    # Add handler to logger
    logger.addHandler(console_handler)

    # Prevent duplicate messages from parent loggers
    logger.propagate = False

    return logger

def get_performance_logger(name: str = "performance") -> logging.Logger:
    """Get performance-specific logger"""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Performance handler
    perf_handler = logging.StreamHandler(sys.stdout)
    perf_handler.setFormatter(PerformanceFormatter())
    logger.addHandler(perf_handler)

    logger.propagate = False

    return logger

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    enable_file_logging: bool = False,
    enable_performance_logging: bool = True
):
    """
    Setup comprehensive logging configuration.

    Args:
        level: Default log level
        log_file: Optional log file path
        enable_file_logging: Whether to enable file logging
        enable_performance_logging: Whether to enable performance logging
    """
    # Convert level to uppercase
    level = level.upper()

    # Base configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': JsonFormatter,
            },
            'performance': {
                '()': PerformanceFormatter,
            },
            'simple': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'json',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            '': {  # Root logger
                'level': level,
                'handlers': ['console']
            },
            'performance': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            }
        }
    }

    # Add file logging if enabled
    if enable_file_logging and log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'json',
            'filename': log_file,
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5
        }

        # Add file handler to root logger
        config['loggers']['']['handlers'].append('file')

    # Apply configuration
    logging.config.dictConfig(config)

    # Set up performance logging if enabled
    if enable_performance_logging:
        perf_logger = get_performance_logger()

    # Log configuration
    logger = get_logger(__name__)
    logger.info("Logging configuration initialized", extra={
        "level": level,
        "file_logging": enable_file_logging,
        "performance_logging": enable_performance_logging,
        "log_file": log_file
    })

class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter for adding context to all log messages"""

    def __init__(self, logger: logging.Logger, context: Dict[str, Any]):
        super().__init__(logger, context)

    def process(self, msg, kwargs):
        """Process log message with context"""
        # Merge context into extra
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        kwargs['extra'] = extra
        return msg, kwargs

def get_context_logger(name: str, context: Dict[str, Any]) -> LoggerAdapter:
    """
    Get logger with persistent context.

    Args:
        name: Logger name
        context: Context dictionary to include in all logs

    Returns:
        LoggerAdapter with context
    """
    logger = get_logger(name)
    return LoggerAdapter(logger, context)

# Performance logging utilities
def log_performance(
    operation: str,
    duration_ms: float,
    component: str = "unknown",
    **extra
):
    """Log performance metrics"""
    perf_logger = get_performance_logger()
    perf_logger.info(
        f"Performance: {operation}",
        extra={
            "operation": operation,
            "duration_ms": duration_ms,
            "component": component,
            **extra
        }
    )

def time_function(func):
    """Decorator to time function execution and log performance"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now(timezone.utc)
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds() * 1000
            log_performance(
                operation=f"{func.__module__}.{func.__name__}",
                duration_ms=duration,
                component=func.__module__
            )
    return wrapper

# Initialize default logging on import
setup_logging(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    enable_file_logging=os.getenv('ENABLE_FILE_LOGGING', 'false').lower() == 'true',
    enable_performance_logging=os.getenv('ENABLE_PERFORMANCE_LOGGING', 'true').lower() == 'true'
)