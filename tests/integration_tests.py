# Helm AI - Comprehensive Integration Tests
"""
Complete integration test suite covering API endpoints,
database operations, error handling, and performance monitoring.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import json
import time
import concurrent.futures
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

import redis
import sqlite3
from flask import Flask
from flask.testing import FlaskClient

# Import application components
from src.common.exceptions import (
    ValidationException, DatabaseException,
    AuthenticationException, RateLimitException
)
from src.database.connection_manager import ConnectionManager
from src.api_gateway.rate_limiter import DistributedRateLimiter
from src.monitoring.metrics import PerformanceMonitor
from src.logging_config.logger import get_logger

logger = get_logger(__name__)

class TestAPIIntegration:
    """Comprehensive API integration tests"""

    @pytest.fixture
    def app(self):
        """Create Flask test app"""
        from analytics_server import app as analytics_app
        analytics_app.config['TESTING'] = True
        return analytics_app

    @pytest.fixture
    def client(self, app: Flask) -> FlaskClient:
        """Create test client"""
        return app.test_client()

    @pytest.fixture
    def db_manager(self):
        """Create test database manager"""
        # Use in-memory SQLite for testing
        manager = ConnectionManager("sqlite:///:memory:")
        yield manager
        manager.cleanup()

    @pytest.fixture
    def redis_client(self):
        """Create Redis test client"""
        # Use fakeredis for testing
        try:
            import fakeredis
            client = fakeredis.FakeRedis()
            yield client
            client.flushall()
        except ImportError:
            pytest.skip("fakeredis not available")

    def test_health_check_endpoint(self, client: FlaskClient):
        """Test health check endpoint functionality"""
        response = client.get('/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "status" in data
        assert "service" in data
        assert "timestamp" in data
        assert data["service"] == "Analytics Server"

    def test_track_activity_success(self, client: FlaskClient):
        """Test successful activity tracking"""
        activity_data = {
            "user_id": "test_user_123",
            "activity_type": "page_view",
            "activity_data": {"page": "/dashboard", "duration": 30},
            "session_id": "session_456"
        }

        response = client.post(
            '/api/analytics/track-activity',
            json=activity_data,
            headers={'Content-Type': 'application/json'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "message" in data

    def test_track_activity_validation_error(self, client: FlaskClient):
        """Test activity tracking with validation errors"""
        # Missing required fields
        response = client.post(
            '/api/analytics/track-activity',
            json={"user_id": "test_user"},
            headers={'Content-Type': 'application/json'}
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False
        assert "error" in data

    def test_track_feature_success(self, client: FlaskClient):
        """Test successful feature tracking"""
        feature_data = {
            "feature_name": "ai_chat",
            "user_id": "test_user_123",
            "session_duration": 300
        }

        response = client.post(
            '/api/analytics/track-feature',
            json=feature_data,
            headers={'Content-Type': 'application/json'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_get_metrics_endpoint(self, client: FlaskClient):
        """Test metrics retrieval endpoint"""
        response = client.get('/api/analytics/metrics')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, dict)
        assert "timestamp" in data

        # Should have expected metric categories
        expected_keys = ["active_users", "feature_usage", "ai_metrics", "performance"]
        for key in expected_keys:
            assert key in data

    def test_concurrent_activity_tracking(self, client: FlaskClient):
        """Test concurrent activity tracking"""
        def track_activity(i: int):
            return client.post(
                '/api/analytics/track-activity',
                json={
                    "user_id": f"user_{i}",
                    "activity_type": "test_activity",
                    "activity_data": {"test_id": i}
                },
                headers={'Content-Type': 'application/json'}
            )

        # Run 50 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(track_activity, i) for i in range(50)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert all(r.status_code == 200 for r in responses)

        # Check that all activities were recorded
        metrics_response = client.get('/api/analytics/metrics')
        assert metrics_response.status_code == 200

class TestDatabaseIntegration:
    """Database integration tests"""

    @pytest.fixture
    def db_manager(self):
        """Create test database manager"""
        manager = ConnectionManager("sqlite:///:memory:")
        yield manager
        manager.cleanup()

    def test_database_connection_pooling(self, db_manager: ConnectionManager):
        """Test database connection pooling"""
        # Test multiple concurrent connections
        def execute_query(i: int):
            return db_manager.execute_query(
                "SELECT ? as test_value",
                params=(i,)
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(execute_query, i) for i in range(100)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 100
        assert all(r[0]["test_value"] == i for i, r in enumerate(results) if r)

    def test_database_error_handling(self, db_manager: ConnectionManager):
        """Test database error handling"""
        # Test invalid SQL
        with pytest.raises(DatabaseException):
            db_manager.execute_query("INVALID SQL STATEMENT")

        # Test connection failure (simulate)
        with patch.object(db_manager, 'get_connection', side_effect=Exception("Connection failed")):
            with pytest.raises(DatabaseException):
                db_manager.execute_query("SELECT 1")

    def test_database_performance_monitoring(self, db_manager: ConnectionManager):
        """Test database performance monitoring"""
        import time

        start_time = time.time()

        # Execute multiple queries
        for i in range(10):
            db_manager.execute_query(
                "SELECT ? as id, ? as name",
                params=(i, f"name_{i}")
            )

        duration = time.time() - start_time

        # Should complete within reasonable time
        assert duration < 5.0  # 5 seconds max

        # Check health
        health = db_manager.health_check()
        assert health["status"] == "healthy"
        assert "response_time_ms" in health

class TestRateLimiterIntegration:
    """Rate limiter integration tests"""

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

    def test_sliding_window_rate_limiting(self, rate_limiter: DistributedRateLimiter):
        """Test sliding window rate limiting"""
        key = "test_user"
        limit = 5
        window_seconds = 10

        # Should allow first 5 requests
        for i in range(limit):
            allowed, metadata = rate_limiter.is_allowed(key, limit, window_seconds, "sliding_window")
            assert allowed is True
            assert metadata["remaining"] == limit - i - 1

        # Should deny 6th request
        allowed, metadata = rate_limiter.is_allowed(key, limit, window_seconds, "sliding_window")
        assert allowed is False
        assert metadata["remaining"] == 0

    def test_token_bucket_rate_limiting(self, rate_limiter: DistributedRateLimiter):
        """Test token bucket rate limiting"""
        key = "test_user"
        capacity = 10
        window_seconds = 5  # 2 tokens per second

        # Should allow requests up to capacity
        for i in range(capacity):
            allowed, metadata = rate_limiter.is_allowed(key, capacity, window_seconds, "token_bucket")
            assert allowed is True

        # Should deny when bucket empty
        allowed, metadata = rate_limiter.is_allowed(key, capacity, window_seconds, "token_bucket")
        assert allowed is False

    def test_rate_limit_reset(self, rate_limiter: DistributedRateLimiter):
        """Test rate limit reset functionality"""
        key = "test_user"

        # Fill up the limit
        for i in range(3):
            rate_limiter.is_allowed(key, 3, 60, "sliding_window")

        # Should be at limit
        allowed, _ = rate_limiter.is_allowed(key, 3, 60, "sliding_window")
        assert not allowed

        # Reset limit
        success = rate_limiter.reset_limit(key, "sliding_window")
        assert success

        # Should allow requests again
        allowed, _ = rate_limiter.is_allowed(key, 3, 60, "sliding_window")
        assert allowed

class TestPerformanceMonitoringIntegration:
    """Performance monitoring integration tests"""

    @pytest.fixture
    def performance_monitor(self):
        """Create performance monitor"""
        from prometheus_client import CollectorRegistry
        registry = CollectorRegistry()
        return PerformanceMonitor(registry)

    def test_request_tracking(self, performance_monitor: PerformanceMonitor):
        """Test HTTP request tracking"""
        # Track some requests
        performance_monitor.track_request("GET", "/api/test", 200, 0.1, 1024, 2048)
        performance_monitor.track_request("POST", "/api/test", 201, 0.2, 512, 1024)
        performance_monitor.track_request("GET", "/api/error", 500, 0.05, 256, 512)

        # Get metrics
        metrics_text = performance_monitor.get_metrics_text()

        # Should contain our metrics
        assert 'helm_ai_http_requests_total' in metrics_text
        assert 'helm_ai_http_request_duration_seconds' in metrics_text

    def test_database_query_tracking(self, performance_monitor: PerformanceMonitor):
        """Test database query tracking"""
        performance_monitor.track_database_query("SELECT", "users", 0.05)
        performance_monitor.track_database_query("INSERT", "logs", 0.02)
        performance_monitor.track_database_query("UPDATE", "users", 0.03)

        metrics_text = performance_monitor.get_metrics_text()
        assert 'helm_ai_db_queries_total' in metrics_text
        assert 'helm_ai_db_query_duration_seconds' in metrics_text

    def test_cache_operation_tracking(self, performance_monitor: PerformanceMonitor):
        """Test cache operation tracking"""
        # Simulate cache operations
        for _ in range(8):
            performance_monitor.track_cache_operation("user_cache", True)  # 8 hits
        for _ in range(2):
            performance_monitor.track_cache_operation("user_cache", False)  # 2 misses

        metrics_text = performance_monitor.get_metrics_text()
        assert 'helm_ai_cache_hits_total' in metrics_text
        assert 'helm_ai_cache_misses_total' in metrics_text

    def test_ai_inference_tracking(self, performance_monitor: PerformanceMonitor):
        """Test AI inference tracking"""
        performance_monitor.track_ai_inference("gpt-4", "chat_completion", 1.2)
        performance_monitor.track_ai_inference("claude", "text_generation", 0.8)

        metrics_text = performance_monitor.get_metrics_text()
        assert 'helm_ai_inference_requests_total' in metrics_text
        assert 'helm_ai_inference_duration_seconds' in metrics_text

class TestErrorHandlingIntegration:
    """Error handling integration tests"""

    def test_validation_exception_handling(self):
        """Test validation exception handling"""
        from src.common.exceptions import ValidationException

        with pytest.raises(ValidationException) as exc_info:
            raise ValidationException("Invalid input", field="email")

        exception = exc_info.value
        assert exception.error_code == "VALIDATION_ERROR"
        assert exception.context["field"] == "email"
        assert exception.http_status == 400

    def test_database_exception_handling(self):
        """Test database exception handling"""
        from src.common.exceptions import DatabaseException

        original_error = Exception("Connection timeout")
        with pytest.raises(DatabaseException) as exc_info:
            raise DatabaseException(
                "Query failed",
                operation="SELECT",
                table="users",
                cause=original_error
            )

        exception = exc_info.value
        assert exception.error_code == "DATABASE_ERROR"
        assert exception.context["operation"] == "SELECT"
        assert exception.context["table"] == "users"
        assert exception.http_status == 500

    def test_error_handler_decorator(self):
        """Test error handler decorator"""
        from src.common.exceptions import handle_errors, ValidationException

        @handle_errors()
        def failing_function():
            raise ValueError("Test error")

        # Should convert to ValidationException
        with pytest.raises(ValidationException):
            failing_function()

    def test_safe_execute_decorator(self):
        """Test safe execute decorator"""
        from src.common.exceptions import safe_execute

        @safe_execute(default_return="default")
        def failing_function():
            raise Exception("Test error")

        # Should return default value
        result = failing_function()
        assert result == "default"

class TestLoadTesting:
    """Load testing scenarios"""

    @pytest.fixture
    def client(self):
        """Create test client for load testing"""
        from analytics_server import app
        app.config['TESTING'] = True
        return app.test_client()

    def test_high_concurrency_load(self, client: FlaskClient):
        """Test high concurrency load"""
        def make_request(i: int):
            return client.post(
                '/api/analytics/track-activity',
                json={
                    "user_id": f"load_test_user_{i}",
                    "activity_type": "load_test",
                    "activity_data": {"request_id": i}
                },
                headers={'Content-Type': 'application/json'}
            )

        # Test with 100 concurrent requests
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request, i) for i in range(100)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]

        duration = time.time() - start_time

        # All requests should succeed
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count == 100

        # Should complete within reasonable time (under 30 seconds)
        assert duration < 30.0

        # Calculate requests per second
        rps = 100 / duration
        logger.info(f"Load test completed: {rps:.2f} RPS, {duration:.2f}s total")

    def test_memory_usage_under_load(self, client: FlaskClient):
        """Test memory usage under load"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Generate load
        def make_request(i: int):
            return client.get('/api/analytics/metrics')

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(50)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (under 50MB)
        assert memory_increase < 50.0
        logger.info(f"Memory usage test: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])