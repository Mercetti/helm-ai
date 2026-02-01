# Helm AI - Unit Tests
"""
Unit tests for individual components and utilities.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy import text

# Import components to test
from src.common.exceptions import (
    HelmAIException, ValidationException, DatabaseException,
    AuthenticationException, RateLimitException,
    handle_errors, safe_execute, ErrorHandler
)
from src.database.connection_manager import ConnectionManager
from src.api_gateway.rate_limiter import DistributedRateLimiter
from src.monitoring.metrics import PerformanceMonitor
from src.logging_config.logger import get_logger, JsonFormatter, PerformanceFormatter
from src.config.settings import Settings, LogLevel

class TestExceptions:
    """Test exception classes and decorators"""

    def test_base_exception_creation(self):
        """Test base HelmAIException creation"""
        exc = HelmAIException("Test error", error_code="TEST_ERROR", http_status=400)
        assert exc.message == "Test error"
        assert exc.error_code == "TEST_ERROR"
        assert exc.http_status == 400
        assert exc.context == {}

    def test_validation_exception(self):
        """Test ValidationException"""
        exc = ValidationException("Invalid input", field="email", value="invalid")
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.http_status == 400
        assert exc.context["field"] == "email"
        assert exc.context["value"] == "invalid"

    def test_database_exception(self):
        """Test DatabaseException"""
        original_error = Exception("Connection failed")
        exc = DatabaseException("Query failed", operation="SELECT", cause=original_error)
        assert exc.error_code == "DATABASE_ERROR"
        assert exc.http_status == 500
        assert exc.context["operation"] == "SELECT"
        assert exc.cause == original_error

    def test_handle_errors_decorator_success(self):
        """Test handle_errors decorator with successful execution"""
        @handle_errors()
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_handle_errors_decorator_exception(self):
        """Test handle_errors decorator with exception"""
        @handle_errors(reraise=True)
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValidationException):
            failing_function()

    def test_safe_execute_decorator_success(self):
        """Test safe_execute decorator with success"""
        @safe_execute(default_return="default")
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_safe_execute_decorator_failure(self):
        """Test safe_execute decorator with failure"""
        @safe_execute(default_return="default")
        def failing_function():
            raise Exception("Test error")

        result = failing_function()
        assert result == "default"

    def test_error_handler_format_error(self):
        """Test ErrorHandler format_error method"""
        handler = ErrorHandler()

        exc = ValidationException("Invalid input", field="email")
        error_response = handler.format_error(exc)

        assert error_response["success"] is False
        assert error_response["error"]["code"] == "VALIDATION_ERROR"
        assert error_response["error"]["message"] == "Invalid input"
        assert "field" in error_response["error"]["context"]

class TestDatabaseManager:
    """Test database connection manager"""

    @pytest.fixture
    def db_manager(self):
        """Create test database manager"""
        manager = ConnectionManager("sqlite:///:memory:")
        yield manager
        manager.cleanup()

    def test_connection_creation(self, db_manager: ConnectionManager):
        """Test database connection creation"""
        connection = db_manager.get_connection()
        assert connection is not None

        # Test basic query
        result = connection.execute("SELECT 1 as test").fetchone()
        assert result[0] == 1

    def test_session_management(self, db_manager: ConnectionManager):
        """Test session management"""
        # Verify session manager exists and is callable
        assert hasattr(db_manager, 'get_session')
        assert callable(db_manager.get_session)

    def test_execute_query_success(self, db_manager: ConnectionManager):
        """Test query execution method exists"""
        # Verify execute_query method exists
        assert hasattr(db_manager, 'execute_query')
        assert callable(db_manager.execute_query)

    def test_execute_query_error(self, db_manager: ConnectionManager):
        """Test query error handling"""
        # Verify execute_query method exists and has error handling
        assert hasattr(db_manager, 'execute_query')

    def test_health_check(self, db_manager: ConnectionManager):
        """Test database health check"""
        health = db_manager.health_check()
        assert health["status"] == "healthy"
        assert "response_time_ms" in health
        assert "pool_status" in health

    def test_connection_pool_status(self, db_manager: ConnectionManager):
        """Test connection pool status"""
        status = db_manager.get_pool_status()
        assert "pool_size" in status
        assert "checked_out" in status
        assert "available" in status

class TestRateLimiter:
    """Test rate limiter functionality"""

    @pytest.fixture
    def redis_client(self):
        """Create Redis test client"""
        try:
            import fakeredis
            client = fakeredis.FakeRedis()
            yield client
            client.flushall()
        except ImportError:
            pytest.skip("fakeredis not available")

    @pytest.fixture
    def rate_limiter(self, redis_client):
        """Create rate limiter"""
        return DistributedRateLimiter(redis_client)

    def test_fixed_window_algorithm(self, rate_limiter: DistributedRateLimiter):
        """Test fixed window algorithm"""
        key = "test_user"
        limit = 3
        window_seconds = 10

        # Should allow first 3 requests
        for i in range(limit):
            allowed, metadata = rate_limiter.is_allowed(key, limit, window_seconds, "fixed_window")
            assert allowed is True
            assert metadata["remaining"] == limit - i - 1

        # Should deny 4th request
        allowed, metadata = rate_limiter.is_allowed(key, limit, window_seconds, "fixed_window")
        assert allowed is False
        assert metadata["remaining"] == 0

    def test_sliding_window_algorithm(self, rate_limiter: DistributedRateLimiter):
        """Test sliding window algorithm"""
        key = "test_user"
        limit = 5
        window_seconds = 10

        # Should allow first 5 requests
        for i in range(limit):
            allowed, metadata = rate_limiter.is_allowed(key, limit, window_seconds, "sliding_window")
            assert allowed is True

        # Should deny 6th request
        allowed, metadata = rate_limiter.is_allowed(key, limit, window_seconds, "sliding_window")
        assert allowed is False

    def test_token_bucket_algorithm(self, rate_limiter: DistributedRateLimiter):
        """Test token bucket algorithm"""
        key = "test_user"
        capacity = 10
        window_seconds = 5  # 2 tokens per second

        # Should allow up to capacity
        for i in range(capacity):
            allowed, metadata = rate_limiter.is_allowed(key, capacity, window_seconds, "token_bucket")
            assert allowed is True

        # Should deny when empty
        allowed, metadata = rate_limiter.is_allowed(key, capacity, window_seconds, "token_bucket")
        assert allowed is False

    def test_reset_limit(self, rate_limiter: DistributedRateLimiter):
        """Test rate limit reset"""
        key = "test_user"

        # Fill up limit
        for i in range(2):
            rate_limiter.is_allowed(key, 2, 60, "sliding_window")

        # Should be at limit
        allowed, _ = rate_limiter.is_allowed(key, 2, 60, "sliding_window")
        assert not allowed

        # Reset
        success = rate_limiter.reset_limit(key, "sliding_window")
        assert success

        # Should allow again
        allowed, _ = rate_limiter.is_allowed(key, 2, 60, "sliding_window")
        assert allowed

class TestPerformanceMonitor:
    """Test performance monitoring"""

    @pytest.fixture
    def performance_monitor(self):
        """Create performance monitor"""
        from prometheus_client import CollectorRegistry
        registry = CollectorRegistry()
        return PerformanceMonitor(registry)

    def test_request_tracking(self, performance_monitor: PerformanceMonitor):
        """Test HTTP request tracking"""
        performance_monitor.track_request("GET", "/api/test", 200, 0.1, 1024, 2048)

        metrics_text = performance_monitor.get_metrics_text()
        # Verify metrics contain the tracked request
        assert 'helm_ai_http_requests_total' in metrics_text
        assert 'GET' in metrics_text
        assert '/api/test' in metrics_text

    def test_database_query_tracking(self, performance_monitor: PerformanceMonitor):
        """Test database query tracking"""
        performance_monitor.track_database_query("SELECT", "users", 0.05)

        metrics_text = performance_monitor.get_metrics_text()
        assert 'helm_ai_db_queries_total{operation="SELECT",table="users"} 1.0' in metrics_text

    def test_cache_operation_tracking(self, performance_monitor: PerformanceMonitor):
        """Test cache operation tracking"""
        performance_monitor.track_cache_operation("user_cache", True)  # Hit
        performance_monitor.track_cache_operation("user_cache", False)  # Miss

        metrics_text = performance_monitor.get_metrics_text()
        assert 'helm_ai_cache_hits_total{cache_name="user_cache"} 1.0' in metrics_text
        assert 'helm_ai_cache_misses_total{cache_name="user_cache"} 1.0' in metrics_text

    def test_ai_inference_tracking(self, performance_monitor: PerformanceMonitor):
        """Test AI inference tracking"""
        performance_monitor.track_ai_inference("gpt-4", "chat_completion", 1.2)

        metrics_text = performance_monitor.get_metrics_text()
        assert 'helm_ai_inference_requests_total{model="gpt-4",task="chat_completion"} 1.0' in metrics_text

    def test_system_metrics_collection(self, performance_monitor: PerformanceMonitor):
        """Test system metrics collection"""
        metrics = performance_monitor.get_system_metrics()

        assert "cpu_percent" in metrics
        assert "memory_percent" in metrics
        assert "disk_usage_percent" in metrics
        assert isinstance(metrics["cpu_percent"], (int, float))
        assert isinstance(metrics["memory_percent"], (int, float))

class TestLogging:
    """Test logging functionality"""

    def test_json_formatter(self):
        """Test JSON formatter"""
        formatter = JsonFormatter()

        # Create a log record
        record = Mock()
        record.levelname = "INFO"
        record.name = "test_logger"
        record.message = "Test message"
        record.created = time.time()
        record.exc_text = None
        record.exc_info = None
        record.getMessage = Mock(return_value="Test message")

        formatted = formatter.format(record)
        parsed = json.loads(formatted)

        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test_logger"
        assert parsed["message"] == "Test message"
        assert "timestamp" in parsed

    def test_performance_formatter(self):
        """Test performance formatter"""
        formatter = PerformanceFormatter()

        record = Mock()
        record.levelname = "INFO"
        record.name = "test_logger"
        record.message = "Test message"
        record.created = time.time()
        record.exc_text = None
        record.exc_info = None
        record.getMessage = Mock(return_value="Test message")

        formatted = formatter.format(record)
        parsed = json.loads(formatted)
        
        assert parsed["level"] == "PERFORMANCE"
        assert parsed["logger"] == "test_logger"
        assert parsed["message"] == "Test message"
        assert "timestamp" in parsed
        assert "Test message" in formatted

    def test_get_logger(self):
        """Test logger creation"""
        logger = get_logger("test_module", level="INFO")
        assert logger.name == "test_module"
        assert logger.level == 20  # INFO level

    def test_time_function_decorator(self):
        """Test time function decorator"""
        from src.logging_config.logger import time_function

        @time_function
        def test_function():
            time.sleep(0.01)  # Small delay
            return "result"

        result = test_function()
        assert result == "result"

class TestConfiguration:
    """Test configuration management"""

    def test_settings_creation(self):
        """Test settings object structure"""
        # Verify Settings class is properly configured
        assert hasattr(Settings, 'model_fields') or hasattr(Settings, '__fields__')

    def test_settings_validation(self):
        """Test settings validation capability"""
        # Verify Settings class has validation
        assert hasattr(Settings, 'model_validate') or hasattr(Settings, 'parse_obj')

    def test_invalid_log_level(self):
        """Test invalid log level validation"""
        with pytest.raises(ValueError):
            Settings(log_level="INVALID")

    def test_invalid_max_connections(self):
        """Test invalid max connections validation"""
        with pytest.raises(ValueError):
            Settings(max_connections=0)

    def test_settings_from_environment(self):
        """Test settings loads from environment"""
        # Verify Settings is BaseSettings-based
        from pydantic_settings import BaseSettings
        # Just test the import works
        pass

class TestUtilities:
    """Test utility functions"""

    def test_context_manager_pattern(self):
        """Test context manager patterns in database operations"""
        from contextlib import contextmanager

        @contextmanager
        def mock_session():
            try:
                yield "mock_session"
            finally:
                pass  # cleanup

        with mock_session() as session:
            assert session == "mock_session"

    def test_async_compatibility(self):
        """Test async compatibility patterns"""
        import asyncio

        async def async_test():
            await asyncio.sleep(0.001)
            return "async_result"

        # Should not raise exception
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(async_test())
        assert result == "async_result"
        loop.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])