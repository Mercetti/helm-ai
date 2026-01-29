"""
Working monitoring modules test - focused on actual working functionality
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

def test_monitoring_imports():
    """Test that monitoring modules can be imported"""
    try:
        from src.monitoring.health_checks import HealthChecker, HealthStatus, CheckType, HealthCheck
        from src.monitoring.performance_monitor import PerformanceMonitor, MetricType
        from src.monitoring.structured_logging import StructuredLogger, LogLevel
        assert HealthChecker is not None
        assert PerformanceMonitor is not None
        assert StructuredLogger is not None
        assert HealthStatus is not None
        assert CheckType is not None
        assert MetricType is not None
        assert LogLevel is not None
    except ImportError as e:
        pytest.fail(f"Failed to import monitoring modules: {e}")

@pytest.mark.unit
def test_health_checker_creation():
    """Test health checker creation and basic attributes"""
    from src.monitoring.health_checks import HealthChecker, HealthStatus, CheckType
    
    # Test health checker creation
    checker = HealthChecker()
    assert checker is not None
    assert hasattr(checker, 'add_check')
    assert hasattr(checker, 'run_all_checks')
    assert hasattr(checker, 'checks')
    assert hasattr(checker, 'results')
    
    # Test health status enum
    assert HealthStatus.HEALTHY.value == "healthy"
    assert HealthStatus.DEGRADED.value == "degraded"
    assert HealthStatus.UNHEALTHY.value == "unhealthy"
    assert HealthStatus.UNKNOWN.value == "unknown"
    
    # Test check type enum
    assert CheckType.SYSTEM.value == "system"
    assert CheckType.DATABASE.value == "database"
    assert CheckType.EXTERNAL.value == "external"
    assert CheckType.CUSTOM.value == "custom"

@pytest.mark.unit
def test_health_checker_default_checks():
    """Test that default health checks are initialized"""
    from src.monitoring.health_checks import HealthChecker
    
    # Create health checker (should initialize default checks)
    checker = HealthChecker()
    
    # Test that default checks were added
    checks = checker.checks
    assert len(checks) > 0
    
    # Check for common default checks
    expected_checks = ['database', 'cache', 'disk_space', 'memory', 'cpu']
    found_checks = [check_name for check_name in expected_checks if check_name in checks]
    assert len(found_checks) > 0

@pytest.mark.unit
def test_health_checker_run_checks():
    """Test running health checks"""
    from src.monitoring.health_checks import HealthChecker
    
    checker = HealthChecker()
    
    # Test running all checks (with mocking to avoid system dependencies)
    with patch('psutil.disk_usage'), \
         patch('psutil.virtual_memory'), \
         patch('psutil.cpu_percent', return_value=45.2):
        
        # Run all checks
        results = checker.run_all_checks()
        assert results is not None
        assert isinstance(results, dict)
        assert len(results) > 0

@pytest.mark.unit
def test_health_checker_add_custom_check():
    """Test adding custom health check"""
    from src.monitoring.health_checks import HealthChecker, HealthStatus, CheckType, HealthCheck
    
    checker = HealthChecker()
    
    # Create custom check function
    def custom_check():
        return HealthCheckResult(
            name="custom_test",
            status=HealthStatus.HEALTHY,
            message="Custom check passed",
            timestamp=datetime.now(),
            duration_ms=100.0
        )
    
    # Import HealthCheckResult
    from src.monitoring.health_checks import HealthCheckResult
    
    # Add custom check
    test_check = HealthCheck(
        name="custom_test",
        check_type=CheckType.CUSTOM,
        check_function=custom_check,
        enabled=True
    )
    
    checker.add_check(test_check)
    
    # Verify check was added
    assert "custom_test" in checker.checks
    assert checker.checks["custom_test"].name == "custom_test"

@pytest.mark.unit
def test_performance_monitor_creation():
    """Test performance monitor creation and basic attributes"""
    from src.monitoring.performance_monitor import PerformanceMonitor, MetricType
    
    # Test monitor creation
    monitor = PerformanceMonitor()
    assert monitor is not None
    assert hasattr(monitor, 'register_metric')
    assert hasattr(monitor, 'get_metric_stats')
    assert hasattr(monitor, 'metrics_collector')
    
    # Test metric type enum
    assert MetricType.COUNTER.value == "counter"
    assert MetricType.GAUGE.value == "gauge"
    assert MetricType.HISTOGRAM.value == "histogram"
    assert MetricType.TIMER.value == "timer"

@pytest.mark.unit
def test_performance_monitor_register_metric():
    """Test registering metrics"""
    from src.monitoring.performance_monitor import PerformanceMonitor, MetricType
    
    monitor = PerformanceMonitor()
    
    # Test registering a counter metric
    monitor.register_metric(
        name="test_counter",
        metric_type=MetricType.COUNTER,
        unit="count",
        description="Test counter metric"
    )
    
    # Test registering a gauge metric
    monitor.register_metric(
        name="test_gauge",
        metric_type=MetricType.GAUGE,
        unit="percent",
        description="Test gauge metric"
    )
    
    # Verify metrics were registered
    assert "test_counter" in monitor.metrics_collector.metrics
    assert "test_gauge" in monitor.metrics_collector.metrics

@pytest.mark.unit
def test_performance_monitor_get_stats():
    """Test getting metric statistics"""
    from src.monitoring.performance_monitor import PerformanceMonitor, MetricType
    
    monitor = PerformanceMonitor()
    
    # Register a metric
    monitor.register_metric(
        name="test_metric",
        metric_type=MetricType.COUNTER,
        unit="count",
        description="Test metric"
    )
    
    # Get metric stats
    stats = monitor.get_metric_stats("test_metric")
    assert stats is not None
    assert 'name' in stats
    assert 'type' in stats
    assert 'unit' in stats
    assert stats['name'] == "test_metric"
    assert stats['type'] == MetricType.COUNTER

@pytest.mark.unit
def test_structured_logger_creation():
    """Test structured logger creation and basic attributes"""
    from src.monitoring.structured_logging import StructuredLogger, LogLevel
    
    # Test logger creation with name
    logger = StructuredLogger("test_logger")
    assert logger is not None
    assert hasattr(logger, 'log')
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'error')
    assert hasattr(logger, 'warning')
    assert hasattr(logger, 'debug')
    
    # Test log level enum
    assert LogLevel.DEBUG.value == "DEBUG"
    assert LogLevel.INFO.value == "INFO"
    assert LogLevel.WARNING.value == "WARNING"
    assert LogLevel.ERROR.value == "ERROR"
    assert LogLevel.CRITICAL.value == "CRITICAL"

@pytest.mark.unit
def test_structured_logger_logging():
    """Test structured logging functionality"""
    from src.monitoring.structured_logging import StructuredLogger
    
    logger = StructuredLogger("test_logger")
    
    # Test that logging methods exist and are callable
    assert callable(logger.info)
    assert callable(logger.warning)
    assert callable(logger.error)
    assert callable(logger.debug)
    assert callable(logger.critical)
    
    # Test basic logging (should not raise exceptions)
    logger.info("Test info message", extra_data={'key': 'value'})
    logger.warning("Test warning message")
    logger.error("Test error message", error_code="TEST_ERROR")
    logger.debug("Test debug message")
    logger.critical("Test critical message")

@pytest.mark.unit
def test_monitoring_integration():
    """Test integration between monitoring modules"""
    from src.monitoring.health_checks import HealthChecker
    from src.monitoring.performance_monitor import PerformanceMonitor
    from src.monitoring.structured_logging import StructuredLogger
    
    # Create monitoring components
    health_checker = HealthChecker()
    performance_monitor = PerformanceMonitor()
    structured_logger = StructuredLogger("integration_test")
    
    # Test that all components can be created
    assert health_checker is not None
    assert performance_monitor is not None
    assert structured_logger is not None
    
    # Test basic integration
    performance_monitor.register_metric(
        "health_check_count",
        performance_monitor.MetricType.COUNTER,
        "count",
        "Number of health checks performed"
    )
    
    # Log integration test
    structured_logger.info("Monitoring components initialized", 
                          health_checks=len(health_checker.checks),
                          metrics_registered=len(performance_monitor.metrics_collector.metrics))

@pytest.mark.unit
def test_monitoring_error_handling():
    """Test monitoring error handling"""
    from src.monitoring.health_checks import HealthChecker, HealthStatus, CheckType, HealthCheck
    
    checker = HealthChecker()
    
    # Test health check failure handling
    def failing_check():
        raise RuntimeError("Simulated failure")
    
    # Import HealthCheckResult
    from src.monitoring.health_checks import HealthCheckResult
    
    # Add failing check
    test_check = HealthCheck(
        name="failing_test",
        check_type=CheckType.CUSTOM,
        check_function=failing_check,
        enabled=True
    )
    
    checker.add_check(test_check)
    
    # Run failing check (should handle gracefully)
    result = checker.run_check("failing_test")
    assert result is not None
    # Should be unhealthy due to exception
    assert result.status == HealthStatus.UNHEALTHY

@pytest.mark.unit
def test_monitoring_configuration():
    """Test monitoring configuration"""
    from src.monitoring.health_checks import HealthChecker
    from src.monitoring.performance_monitor import PerformanceMonitor
    from src.monitoring.structured_logging import StructuredLogger
    
    # Test creation with default configuration
    health_checker = HealthChecker()
    performance_monitor = PerformanceMonitor()
    structured_logger = StructuredLogger("config_test")
    
    # Test that components have expected configuration attributes
    assert hasattr(health_checker, 'default_timeout')
    assert hasattr(health_checker, 'max_history_size')
    assert hasattr(performance_monitor, 'retention_hours')
    assert hasattr(structured_logger, 'log_level')

@pytest.mark.unit
def test_monitoring_enums():
    """Test monitoring enums"""
    from src.monitoring.health_checks import HealthStatus, CheckType
    from src.monitoring.performance_monitor import MetricType
    from src.monitoring.structured_logging import LogLevel
    
    # Test enum values
    assert HealthStatus.HEALTHY.value == "healthy"
    assert HealthStatus.DEGRADED.value == "degraded"
    assert HealthStatus.UNHEALTHY.value == "unhealthy"
    assert HealthStatus.UNKNOWN.value == "unknown"
    
    assert CheckType.SYSTEM.value == "system"
    assert CheckType.DATABASE.value == "database"
    assert CheckType.EXTERNAL.value == "external"
    assert CheckType.CUSTOM.value == "custom"
    
    assert MetricType.COUNTER.value == "counter"
    assert MetricType.GAUGE.value == "gauge"
    assert MetricType.HISTOGRAM.value == "histogram"
    assert MetricType.TIMER.value == "timer"
    
    assert LogLevel.DEBUG.value == "DEBUG"
    assert LogLevel.INFO.value == "INFO"
    assert LogLevel.WARNING.value == "WARNING"
    assert LogLevel.ERROR.value == "ERROR"
    assert LogLevel.CRITICAL.value == "CRITICAL"

@pytest.mark.unit
def test_health_check_result_creation():
    """Test HealthCheckResult creation"""
    from src.monitoring.health_checks import HealthCheckResult, HealthStatus
    
    # Create a health check result
    result = HealthCheckResult(
        name="test_check",
        status=HealthStatus.HEALTHY,
        message="Check passed",
        timestamp=datetime.now(),
        duration_ms=150.0,
        details={"test": "data"}
    )
    
    # Verify result attributes
    assert result.name == "test_check"
    assert result.status == HealthStatus.HEALTHY
    assert result.message == "Check passed"
    assert result.duration_ms == 150.0
    assert result.details["test"] == "data"

@pytest.mark.unit
def test_health_check_creation():
    """Test HealthCheck creation"""
    from src.monitoring.health_checks import HealthCheck, CheckType
    
    # Create a health check
    def test_function():
        return {"status": "healthy"}
    
    check = HealthCheck(
        name="test_check",
        check_type=CheckType.CUSTOM,
        check_function=test_function,
        enabled=True,
        tags=["test", "custom"],
        metadata={"version": "1.0"}
    )
    
    # Verify check attributes
    assert check.name == "test_check"
    assert check.check_type == CheckType.CUSTOM
    assert check.enabled is True
    assert "test" in check.tags
    assert "custom" in check.tags
    assert check.metadata["version"] == "1.0"

if __name__ == '__main__':
    pytest.main([__file__])
