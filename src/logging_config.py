"""
Helm AI Centralized Logging Configuration
Provides consistent logging levels and formats throughout the system
"""

import os
import logging
import logging.config
import json
from datetime import datetime
from typing import Dict, Any, Optional

class HelmAILoggingConfig:
    """Centralized logging configuration for Helm AI"""
    
    # Standardized log levels
    LOG_LEVELS = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG
    }
    
    # Standardized log formats
    LOG_FORMATS = {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(funcName)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(asctime)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "module": "%(module)s", "line": %(lineno)d, "function": "%(funcName)s", "message": "%(message)s"}',
            'datefmt': '%Y-%m-%dT%H:%M:%S'
        },
        'production': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    }
    
    # Environment-specific configurations
    ENVIRONMENT_CONFIGS = {
        'development': {
            'level': 'DEBUG',
            'format': 'detailed',
            'handlers': ['console', 'file'],
            'propagate': True
        },
        'testing': {
            'level': 'INFO',
            'format': 'simple',
            'handlers': ['console'],
            'propagate': False
        },
        'staging': {
            'level': 'INFO',
            'format': 'production',
            'handlers': ['console', 'file'],
            'propagate': True
        },
        'production': {
            'level': 'WARNING',
            'format': 'production',
            'handlers': ['console', 'file'],
            'propagate': False
        }
    }
    
    @classmethod
    def get_environment_config(cls) -> Dict[str, Any]:
        """Get logging configuration based on current environment"""
        env = os.getenv('ENVIRONMENT', 'development').lower()
        return cls.ENVIRONMENT_CONFIGS.get(env, cls.ENVIRONMENT_CONFIGS['development'])
    
    @classmethod
    def setup_logging(cls, config_file: Optional[str] = None) -> None:
        """Setup centralized logging configuration"""
        # Load environment-specific config
        env_config = cls.get_environment_config()
        
        # Create logging configuration
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'detailed': cls.LOG_FORMATS['detailed'],
                'simple': cls.LOG_FORMATS['simple'],
                'json': cls.LOG_FORMATS['json'],
                'production': cls.LOG_FORMATS['production']
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': env_config['level'],
                    'formatter': env_config['format'],
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': env_config['level'],
                    'formatter': env_config['format'],
                    'filename': os.getenv('LOG_FILE', 'logs/stellar_logic_ai.log'),
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'encoding': 'utf8'
                },
                'error_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'ERROR',
                    'formatter': env_config['format'],
                    'filename': os.getenv('ERROR_LOG_FILE', 'logs/stellar_logic_ai_errors.log'),
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'encoding': 'utf8'
                }
            },
            'loggers': {
                '': {  # Root logger
                    'level': env_config['level'],
                    'handlers': env_config['handlers'],
                    'propagate': env_config['propagate']
                },
                'stellar_logic_ai': {  # Application logger
                    'level': env_config['level'],
                    'handlers': env_config['handlers'],
                    'propagate': False
                },
                'security': {  # Security logger
                    'level': 'INFO',
                    'handlers': ['console', 'file', 'error_file'],
                    'propagate': False
                },
                'database': {  # Database logger
                    'level': 'INFO',
                    'handlers': env_config['handlers'],
                    'propagate': False
                },
                'api': {  # API logger
                    'level': 'INFO',
                    'handlers': env_config['handlers'],
                    'propagate': False
                },
                'monitoring': {  # Monitoring logger
                    'level': 'INFO',
                    'handlers': env_config['handlers'],
                    'propagate': False
                },
                'integrations': {  # Integrations logger
                    'level': 'INFO',
                    'handlers': env_config['handlers'],
                    'propagate': False
                },
                'auth': {  # Authentication logger
                    'level': 'INFO',
                    'handlers': ['console', 'file', 'error_file'],
                    'propagate': False
                },
                'audit': {  # Audit logger
                    'level': 'INFO',
                    'handlers': ['console', 'file'],
                    'propagate': False
                },
                'ai': {  # AI modules logger
                    'level': 'INFO',
                    'handlers': env_config['handlers'],
                    'propagate': False
                }
            }
        }
        
        # Apply configuration
        logging.config.dictConfig(logging_config)
        
        # Create log directory if it doesn't exist
        log_file_path = os.getenv('LOG_FILE', 'logs/stellar_logic_ai.log')
        log_dir = os.path.dirname(log_file_path)
        if log_dir:  # Only create directory if path is not empty
            os.makedirs(log_dir, exist_ok=True)
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a properly configured logger"""
        return logging.getLogger(name)
    
    @classmethod
    def set_log_level(cls, logger_name: str, level: str) -> None:
        """Set log level for a specific logger"""
        logger = logging.getLogger(logger_name)
        if level.upper() in cls.LOG_LEVELS:
            logger.setLevel(cls.LOG_LEVELS[level.upper()])
    
    @classmethod
    def add_handler(cls, logger_name: str, handler: logging.Handler) -> None:
        """Add a handler to a specific logger"""
        logger = logging.getLogger(logger_name)
        logger.addHandler(handler)
    
    @classmethod
    def log_with_context(cls, logger: logging.Logger, level: str, message: str, **context) -> None:
        """Log a message with additional context"""
        if context:
            formatted_context = " | ".join([f"{k}={v}" for k, v in context.items()])
            full_message = f"{message} | {formatted_context}"
        else:
            full_message = message
        
        getattr(logger, level.lower())(full_message)


class StructuredLogger:
    """Structured logger with consistent formatting"""
    
    def __init__(self, name: str):
        self.logger = HelmAILoggingConfig.get_logger(name)
        self.name = name
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with optional context"""
        HelmAILoggingConfig.log_with_context(self.logger, 'DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with optional context"""
        HelmAILoggingConfig.log_with_context(self.logger, 'INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with optional context"""
        HelmAILoggingConfig.log_with_context(self.logger, 'WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with optional context"""
        HelmAILoggingConfig.log_with_context(self.logger, 'ERROR', message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with optional context"""
        HelmAILoggingConfig.log_with_context(self.logger, 'CRITICAL', message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback"""
        HelmAILoggingConfig.log_with_context(self.logger, 'ERROR', message, **kwargs)
        self.logger.exception(message)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name)


# Initialize logging on import
HelmAILoggingConfig.setup_logging()

# Export commonly used functions
__all__ = [
    'HelmAILoggingConfig',
    'StructuredLogger', 
    'get_logger'
]
