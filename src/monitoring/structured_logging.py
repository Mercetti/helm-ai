"""
Helm AI Structured Logging
This module provides comprehensive structured logging with JSON formatting and log aggregation
"""

import os
import json
import logging
import sys
import traceback
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field, asdict
import threading
import queue
import time
from pythonjsonlogger import jsonlogger
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogCategory(Enum):
    """Log categories"""
    API = "api"
    AUTH = "auth"
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_SERVICE = "external_service"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    SYSTEM = "system"
    AUDIT = "audit"

@dataclass
class LogContext:
    """Log context information"""
    request_id: str = None
    user_id: str = None
    session_id: str = None
    ip_address: str = None
    user_agent: str = None
    endpoint: str = None
    method: str = None
    service_name: str = None
    environment: str = None
    version: str = None
    additional_fields: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StructuredLogEntry:
    """Structured log entry"""
    timestamp: str
    level: str
    category: str
    message: str
    context: LogContext = field(default_factory=LogContext)
    duration_ms: Optional[float] = None
    error: Optional[Dict[str, Any]] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    stack_trace: Optional[str] = None

class StructuredLogger:
    """Structured logger with JSON formatting"""
    
    def __init__(self, name: str, category: LogCategory = LogCategory.SYSTEM):
        self.logger = logging.getLogger(name)
        self.category = category
        self.context = LogContext()
        
        # Configure logger
        self._configure_logger()
    
    def _configure_logger(self):
        """Configure structured logger"""
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Set log level
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create JSON formatter
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S.%fZ'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        log_file = os.getenv('LOG_FILE', '/var/log/helm-ai/application.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Error file handler
        error_log_file = os.getenv('ERROR_LOG_FILE', '/var/log/helm-ai/error.log')
        error_handler = logging.FileHandler(error_log_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
    
    def set_context(self, **kwargs):
        """Set log context"""
        for key, value in kwargs.items():
            if hasattr(self.context, key):
                setattr(self.context, key, value)
            else:
                self.context.additional_fields[key] = value
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log(LogLevel.CRITICAL, message, **kwargs)
    
    def audit(self, message: str, **kwargs):
        """Log audit message"""
        kwargs['category'] = LogCategory.AUDIT
        self._log(LogLevel.INFO, message, **kwargs)
    
    def performance(self, message: str, duration_ms: float = None, **kwargs):
        """Log performance message"""
        kwargs['category'] = LogCategory.PERFORMANCE
        if duration_ms:
            kwargs['duration_ms'] = duration_ms
        self._log(LogLevel.INFO, message, **kwargs)
    
    def security(self, message: str, **kwargs):
        """Log security message"""
        kwargs['category'] = LogCategory.SECURITY
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def api_request(self, method: str, endpoint: str, status_code: int, duration_ms: float, **kwargs):
        """Log API request"""
        self.set_context(method=method, endpoint=endpoint)
        self.performance(
            f"API {method} {endpoint} - {status_code}",
            duration_ms=duration_ms,
            status_code=status_code,
            **kwargs
        )
    
    def database_query(self, query_type: str, table: str, duration_ms: float, rows_affected: int = None, **kwargs):
        """Log database query"""
        self.set_context(query_type=query_type, table=table)
        self.performance(
            f"Database {query_type} on {table}",
            duration_ms=duration_ms,
            rows_affected=rows_affected,
            **kwargs
        )
    
    def external_service_call(self, service_name: str, operation: str, status: str, duration_ms: float, **kwargs):
        """Log external service call"""
        self.set_context(service_name=service_name, operation=operation)
        self.performance(
            f"External service {service_name} {operation} - {status}",
            duration_ms=duration_ms,
            service_status=status,
            **kwargs
        )
    
    def _log(self, level: LogLevel, message: str, **kwargs):
        """Internal logging method"""
        # Create log entry
        log_entry = StructuredLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=level.value,
            category=kwargs.get('category', self.category).value,
            message=message,
            context=self._get_context_with_overrides(**kwargs),
            duration_ms=kwargs.get('duration_ms'),
            error=kwargs.get('error'),
            metrics=kwargs.get('metrics', {}),
            tags=kwargs.get('tags', []),
            stack_trace=kwargs.get('stack_trace')
        )
        
        # Add additional fields
        additional_fields = {k: v for k, v in kwargs.items() 
                            if k not in ['category', 'duration_ms', 'error', 'metrics', 'tags', 'stack_trace']}
        log_entry.metrics.update(additional_fields)
        
        # Log with standard logger
        log_level = getattr(logging, level.value)
        self.logger.log(log_level, json.dumps(asdict(log_entry), default=str))
    
    def _get_context_with_overrides(self, **kwargs) -> LogContext:
        """Get context with overrides"""
        context = LogContext()
        
        # Copy current context
        for field in ['request_id', 'user_id', 'session_id', 'ip_address', 'user_agent', 
                     'endpoint', 'method', 'service_name', 'environment', 'version']:
            current_value = getattr(self.context, field, None)
            override_value = kwargs.get(field)
            setattr(context, field, override_value or current_value)
        
        # Add additional fields
        context.additional_fields.update(self.context.additional_fields)
        context.additional_fields.update({k: v for k, v in kwargs.items() 
                                         if k not in ['request_id', 'user_id', 'session_id', 'ip_address', 
                                                   'user_agent', 'endpoint', 'method', 'service_name', 
                                                   'environment', 'version']})
        
        return context
    
    def exception(self, message: str, exception: Exception = None, **kwargs):
        """Log exception with stack trace"""
        if exception:
            kwargs['error'] = {
                'type': type(exception).__name__,
                'message': str(exception),
                'module': exception.__class__.__module__
            }
            kwargs['stack_trace'] = traceback.format_exc()
        
        self.error(message, **kwargs)


class LogAggregator:
    """Log aggregation and shipping service"""
    
    def __init__(self):
        self.log_queue = queue.Queue(maxsize=10000)
        self.batch_size = int(os.getenv('LOG_BATCH_SIZE', '100'))
        self.flush_interval = int(os.getenv('LOG_FLUSH_INTERVAL', '5'))  # seconds
        
        # Configuration
        self.use_cloudwatch = os.getenv('AWS_CLOUDWATCH_LOG_GROUP') is not None
        self.use_elasticsearch = os.getenv('ELASTICSEARCH_URL') is not None
        self.use_splunk = os.getenv('SPLUNK_HEC_URL') is not None
        
        # Initialize clients
        if self.use_cloudwatch:
            self.cloudwatch_client = boto3.client('logs')
            self.cloudwatch_group = os.getenv('AWS_CLOUDWATCH_LOG_GROUP')
            self.cloudwatch_stream = os.getenv('AWS_CLOUDWATCH_LOG_STREAM', 'helm-ai-logs')
        
        # Start aggregation thread
        self._start_aggregation_thread()
    
    def _start_aggregation_thread(self):
        """Start log aggregation thread"""
        def aggregate_logs():
            batch = []
            
            while True:
                try:
                    # Get log entry from queue
                    try:
                        log_entry = self.log_queue.get(timeout=1)
                        batch.append(log_entry)
                    except queue.Empty:
                        pass
                    
                    # Process batch if full or timeout
                    if len(batch) >= self.batch_size:
                        self._process_batch(batch)
                        batch = []
                    
                    # Sleep for flush interval
                    time.sleep(self.flush_interval)
                    
                except Exception as e:
                    logger.error(f"Log aggregation error: {e}")
                    time.sleep(5)  # Wait before retrying
        
        aggregation_thread = threading.Thread(target=aggregate_logs, daemon=True)
        aggregation_thread.start()
    
    def _process_batch(self, batch: List[Dict[str, Any]]):
        """Process batch of log entries"""
        try:
            if self.use_cloudwatch:
                self._send_to_cloudwatch(batch)
            
            if self.use_elasticsearch:
                self._send_to_elasticsearch(batch)
            
            if self.use_splunk:
                self._send_to_splunk(batch)
                
        except Exception as e:
            logger.error(f"Failed to process log batch: {e}")
    
    def _send_to_cloudwatch(self, batch: List[Dict[str, Any]]):
        """Send logs to CloudWatch Logs"""
        try:
            # Ensure log group and stream exist
            try:
                self.cloudwatch_client.create_log_group(logGroupName=self.cloudwatch_group)
            except self.cloudwatch_client.exceptions.ResourceAlreadyExistsException:
                pass
            
            try:
                self.cloudwatch_client.create_log_stream(
                    logGroupName=self.cloudwatch_group,
                    logStreamName=self.cloudwatch_stream
                )
            except self.cloudwatch_client.exceptions.ResourceAlreadyExistsException:
                pass
            
            # Format log events
            log_events = []
            for log_entry in batch:
                log_events.append({
                    'timestamp': int(datetime.fromisoformat(log_entry['timestamp'].replace('Z', '+00:00')).timestamp() * 1000),
                    'message': json.dumps(log_entry)
                })
            
            # Send to CloudWatch
            if log_events:
                self.cloudwatch_client.put_log_events(
                    logGroupName=self.cloudwatch_group,
                    logStreamName=self.cloudwatch_stream,
                    logEvents=log_events
                )
                
        except ClientError as e:
            logger.error(f"Failed to send logs to CloudWatch: {e}")
    
    def _send_to_elasticsearch(self, batch: List[Dict[str, Any]]):
        """Send logs to Elasticsearch"""
        try:
            import requests
            
            es_url = os.getenv('ELASTICSEARCH_URL')
            es_index = f"helm-ai-logs-{datetime.now().strftime('%Y.%m')}"
            
            # Bulk index
            bulk_data = []
            for log_entry in batch:
                bulk_data.append(json.dumps({"index": {"_index": es_index}}))
                bulk_data.append(json.dumps(log_entry))
            
            if bulk_data:
                response = requests.post(
                    f"{es_url}/_bulk",
                    data='\n'.join(bulk_data) + '\n',
                    headers={'Content-Type': 'application/x-ndjson'}
                )
                
                if response.status_code >= 400:
                    logger.error(f"Elasticsearch bulk indexing failed: {response.text}")
                    
        except Exception as e:
            logger.error(f"Failed to send logs to Elasticsearch: {e}")
    
    def _send_to_splunk(self, batch: List[Dict[str, Any]]):
        """Send logs to Splunk HEC"""
        try:
            import requests
            
            hec_url = os.getenv('SPLUNK_HEC_URL')
            hec_token = os.getenv('SPLUNK_HEC_TOKEN')
            
            headers = {
                'Authorization': f'Splunk {hec_token}',
                'Content-Type': 'application/json'
            }
            
            # Send batch as single event
            event_data = {
                'time': datetime.now().isoformat(),
                'host': os.getenv('HOSTNAME', 'helm-ai'),
                'source': 'helm-ai',
                'sourcetype': 'json',
                'index': 'main',
                'event': {
                    'batch_size': len(batch),
                    'logs': batch
                }
            }
            
            response = requests.post(hec_url, json=event_data, headers=headers)
            
            if response.status_code >= 400:
                logger.error(f"Splunk HEC request failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to send logs to Splunk: {e}")
    
    def add_log_entry(self, log_entry: Dict[str, Any]):
        """Add log entry to aggregation queue"""
        try:
            self.log_queue.put_nowait(log_entry)
        except queue.Full:
            # Drop log if queue is full
            logger.warning("Log aggregation queue full, dropping log entry")


class LogManager:
    """Centralized log management"""
    
    def __init__(self):
        self.loggers: Dict[str, StructuredLogger] = {}
        self.aggregator = LogAggregator()
        
        # Global context
        self.global_context = LogContext(
            service_name=os.getenv('SERVICE_NAME', 'helm-ai'),
            environment=os.getenv('ENVIRONMENT', 'development'),
            version=os.getenv('APP_VERSION', '1.0.0')
        )
        
        # Initialize default loggers
        self._initialize_loggers()
    
    def _initialize_loggers(self):
        """Initialize default loggers"""
        self.get_logger('api', LogCategory.API)
        self.get_logger('auth', LogCategory.AUTH)
        self.get_logger('database', LogCategory.DATABASE)
        self.get_logger('cache', LogCategory.CACHE)
        self.get_logger('external', LogCategory.EXTERNAL_SERVICE)
        self.get_logger('security', LogCategory.SECURITY)
        self.get_logger('performance', LogCategory.PERFORMANCE)
        self.get_logger('business', LogCategory.BUSINESS)
        self.get_logger('system', LogCategory.SYSTEM)
        self.get_logger('audit', LogCategory.AUDIT)
    
    def get_logger(self, name: str, category: LogCategory = LogCategory.SYSTEM) -> StructuredLogger:
        """Get or create structured logger"""
        if name not in self.loggers:
            logger_instance = StructuredLogger(f"helm_ai.{name}", category)
            
            # Set global context
            for field in ['service_name', 'environment', 'version']:
                value = getattr(self.global_context, field, None)
                if value:
                    setattr(logger_instance.context, field, value)
            
            self.loggers[name] = logger_instance
        
        return self.loggers[name]
    
    def set_global_context(self, **kwargs):
        """Set global context for all loggers"""
        for key, value in kwargs.items():
            if hasattr(self.global_context, key):
                setattr(self.global_context, key, value)
            else:
                self.global_context.additional_fields[key] = value
        
        # Update all existing loggers
        for logger in self.loggers.values():
            logger.set_context(**kwargs)
    
    def create_request_logger(self, request_id: str, **context) -> StructuredLogger:
        """Create logger for specific request"""
        logger_name = f"request_{request_id}"
        logger_instance = self.get_logger(logger_name)
        
        # Set request context
        logger_instance.set_context(request_id=request_id, **context)
        
        return logger_instance
    
    def get_log_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get logging statistics"""
        # This would typically query log aggregation systems
        # For now, return placeholder data
        return {
            "period_hours": hours,
            "total_logs": 0,
            "logs_by_level": {},
            "logs_by_category": {},
            "error_rate": 0.0,
            "average_log_size": 0.0
        }
    
    def search_logs(self, 
                   query: str = None,
                   level: LogLevel = None,
                   category: LogCategory = None,
                   start_time: datetime = None,
                   end_time: datetime = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """Search logs (placeholder implementation)"""
        # This would integrate with log search systems
        return []


# Global log manager instance
log_manager = LogManager()
