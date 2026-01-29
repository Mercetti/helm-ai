"""
Basic monitoring modules test - focused on actual working functionality
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
def test_health_checker_basic():
    """Test basic health checker functionality"""
    from src.monitoring.health_checks import HealthChecker, HealthStatus, CheckType
    
    # Test health checker creation
    checker = HealthChecker()
    assert checker is not None
    assert hasattr(checker, 'add_check')
    assert hasattr(checker, 'run_all_checks')
    assert hasattr(checker, 'get_health_summary')
    
    # Test health status enum
    assert HealthStatus.HEALTHY == "healthy"
    assert HealthStatus.DEGRADED == "degraded"
    assert HealthStatus.UNHEALTHY == "unhealthy"
    assert HealthStatus.UNKNOWN == "unknown"
    
    # Test check type enum
    assert CheckType.SYSTEM == "system"
    assert CheckType.DATABASE == "database"
    assert CheckType.EXTERNAL == "external"
    assert CheckType.CUSTOM == "custom"

@pytest.mark.unit
def test_health_checker_add_check():
    """Test adding and running custom health checks"""
    from src.monitoring.health_checks import HealthChecker, HealthStatus, CheckType, HealthCheck
    
    checker = HealthChecker()
    
    # Test custom check creation
    def custom_check():
        return {
            'status': HealthStatus.HEALTHY,
            'message': 'Custom check passed',
            'timestamp': datetime.now().isoformat(),
            'details': {'custom': 'data'}
        }
    
    # Add custom check
    test_check = HealthCheck(
        name="custom_test",
        check_type=CheckType.CUSTOM,
        check_function=custom_check,
        enabled=True,
        timeout=30
    )
    
    checker.add_check(test_check)
    
    # Test running the check
    result = checker.run_check("custom_test")
    assert result is not None
    assert result.status == HealthStatus.HEALTHY
    assert result.message == "Custom check passed"

@pytest.mark.unit
def test_health_checker_run_all():
    """Test running all health checks"""
    from src.monitoring.health_checks import HealthChecker, HealthStatus, CheckType, HealthCheck
    
    checker = HealthChecker()
    
    # Add multiple checks
    def check1():
        return {
            'status': HealthStatus.HEALTHY,
            'message': 'Check 1 passed',
            'timestamp': datetime.now().isoformat()
        }
    
    def check2():
        return {
            'status': HealthStatus.DEGRADED,
            'message': 'Check 2 degraded',
            'timestamp': datetime.now().isoformat()
        }
    
    test_check1 = HealthCheck("test1", CheckType.CUSTOM, check1, True, 30)
    test_check2 = HealthCheck("test2", CheckType.CUSTOM, check2, True, 30)
    
    checker.add_check(test_check1)
    checker.add_check(test_check2)
    
    # Run all checks
    results = checker.run_all_checks()
    assert results is not None
    assert "test1" in results
    assert "test2" in results
    assert results["test1"].status == HealthStatus.HEALTHY
    assert results["test2"].status == HealthStatus.DEGRADED

@pytest.mark.unit
def test_health_checker_summary():
    """Test health summary generation"""
    from src.monitoring.health_checks import HealthChecker, HealthStatus, CheckType, HealthCheck
    
    checker = HealthChecker()
    
    # Add checks with different statuses
    def healthy_check():
        return {
            'status': HealthStatus.HEALTHY,
            'message': 'Healthy',
            'timestamp': datetime.now().isoformat()
        }
    
    def unhealthy_check():
        return {
            'status': HealthStatus.UNHEALTHY,
            'message': 'Unhealthy',
            'timestamp': datetime.now().isoformat()
        }
    
    checker.add_check(HealthCheck("healthy", CheckType.CUSTOM, healthy_check, True, 30))
    checker.add_check(HealthCheck("unhealthy", CheckType.CUSTOM, unhealthy_check, True, 30))
    
    # Get health summary
    summary = checker.get_health_summary()
    assert summary is not None
    assert 'overall_status' in summary
    assert 'total_checks' in summary
    assert 'healthy_count' in summary
    assert 'unhealthy_count' in summary
    assert summary['total_checks'] >= 2
    assert summary['healthy_count'] >= 1
    assert summary['unhealthy_count'] >= 1

@pytest.mark.unit
def test_performance_monitor_basic():
    """Test basic performance monitor functionality"""
    from src.monitoring.performance_monitor import PerformanceMonitor, MetricType
    
    # Test monitor creation
    monitor = PerformanceMonitor()
    assert monitor is not None
    assert hasattr(monitor, 'record_metric')
    assert hasattr(monitor, 'get_metrics')
    assert hasattr(monitor, 'get_performance_summary')
    
    # Test metric type enum
    assert MetricType.COUNTER == "counter"
    assert MetricType.GAUGE == "gauge"
    assert MetricType.HISTOGRAM == "histogram"
    assert MetricType.TIMER == "timer"

@pytest.mark.unit
def test_performance_monitor_metrics():
    """Test performance monitor metrics recording"""
    from src.monitoring.performance_monitor import PerformanceMonitor, MetricType
    
    monitor = PerformanceMonitor()
    
    # Test metric recording
    monitor.record_metric('test_counter', 1, MetricType.COUNTER)
    monitor.record_metric('test_gauge', 42.5, MetricType.GAUGE)
    
    # Get metrics
    metrics = monitor.get_metrics()
    assert metrics is not None
    assert 'test_counter' in metrics
    assert 'test_gauge' in metrics
    
    # Test performance summary
    summary = monitor.get_performance_summary()
    assert summary is not None
    assert 'timestamp' in summary
    assert 'total_metrics' in summary

@pytest.mark.unit
def test_structured_logger_basic():
    """Test basic structured logger functionality"""
    from src.monitoring.structured_logging import StructuredLogger, LogLevel
    
    # Test logger creation with name
    logger = StructuredLogger("test_logger")
    assert logger is not None
    assert hasattr(logger, 'log')
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'error')
    assert hasattr(logger, 'warning')
    
    # Test log level enum
    assert LogLevel.DEBUG == "DEBUG"
    assert LogLevel.INFO == "INFO"
    assert LogLevel.WARNING == "WARNING"
    assert LogLevel.ERROR == "ERROR"
    assert LogLevel.CRITICAL == "CRITICAL"

@pytest.mark.unit
def test_structured_logger_logging():
    """Test structured logging functionality"""
    from src.monitoring.structured_logging import StructuredLogger
    
    logger = StructuredLogger("test_logger")
    
    # Test different log levels
    logger.info("Test info message", extra_data={'key': 'value'})
    logger.warning("Test warning message")
    logger.error("Test error message", error_code="TEST_ERROR")
    logger.debug("Test debug message")
    
    # Test that logger methods exist and are callable
    assert callable(logger.info)
    assert callable(logger.warning)
    assert callable(logger.error)
    assert callable(logger.debug)

@pytest.mark.unit
def test_monitoring_integration():
    """Test integration between monitoring modules"""
    from src.monitoring.health_checks import HealthChecker, HealthStatus, CheckType, HealthCheck
    from src.monitoring.performance_monitor import PerformanceMonitor, MetricType
    from src.monitoring.structured_logging import StructuredLogger
    
    # Create monitoring components
    health_checker = HealthChecker()
    performance_monitor = PerformanceMonitor()
    structured_logger = StructuredLogger("integration_test")
    
    # Test that all components can be created
    assert health_checker is not None
    assert performance_monitor is not None
    assert structured_logger is not None
    
    # Test integration scenario
    def integrated_health_check():
        # Record performance metric
        performance_monitor.record_metric('health_check_count', 1, MetricType.COUNTER)
        
        return {
            'status': HealthStatus.HEALTHY,
            'message': 'Integrated health check',
            'timestamp': datetime.now().isoformat(),
            'details': {'performance_metrics': performance_monitor.get_metrics()}
        }
    
    # Add integrated check
    health_checker.add_check(HealthCheck(
        "integrated_check",
        CheckType.CUSTOM,
        integrated_health_check,
        True,
        30
    ))
    
    # Run integrated check
    result = health_checker.run_check("integrated_check")
    assert result.status == HealthStatus.HEALTHY
    
    # Log the result
    structured_logger.info("Health check completed", check_result=result.status)
    
    # Verify metric was recorded
    metrics = performance_monitor.get_metrics()
    assert 'health_check_count' in metrics

@pytest.mark.unit
def test_monitoring_error_handling():
    """Test monitoring error handling"""
    from src.monitoring.health_checks import HealthChecker, HealthStatus, CheckType, HealthCheck
    from src.monitoring.performance_monitor import PerformanceMonitor
    
    # Test health check failure
    health_checker = HealthChecker()
    
    def failing_check():
        raise RuntimeError("Simulated failure")
    
    health_checker.add_check(HealthCheck(
        "failing_test",
        CheckType.CUSTOM,
        failing_check,
        True,
        30
    ))
    
    # Run failing check
    result = health_checker.run_check("failing_test")
    assert result is not None
    assert result.status == HealthStatus.UNHEALTHY
    
    # Test performance monitoring with errors
    monitor = PerformanceMonitor()
    
    # Test with invalid metric (should handle gracefully)
    try:
        monitor.record_metric('invalid_metric', 'invalid_value', 'invalid_type')
        assert False, "Should have raised error for invalid metric type"
    except (ValueError, TypeError):
        pass  # Expected

@pytest.mark.unit
def test_monitoring_thread_safety():
    """Test monitoring thread safety"""
    from src.monitoring.performance_monitor import PerformanceMonitor, MetricType
    from src.monitoring.structured_logging import StructuredLogger
    import threading
    
    monitor = PerformanceMonitor()
    logger = StructuredLogger("thread_test")
    
    # Test concurrent metric recording
    def worker_thread(thread_id):
        for i in range(10):
            monitor.record_metric(f'thread_{thread_id}_counter', i, MetricType.COUNTER)
            logger.info(f'Thread {thread_id} iteration {i}')
    
    # Create multiple threads
    threads = []
    for i in range(2):
        thread = threading.Thread(target=worker_thread, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify metrics were recorded
    metrics = monitor.get_metrics()
    assert 'thread_0_counter' in metrics
    assert 'thread_1_counter' in metrics

@pytest.mark.unit
def test_monitoring_default_checks():
    """Test default health checks"""
    from src.monitoring.health_checks import HealthChecker
    
    # Create health checker (should initialize default checks)
    checker = HealthChecker()
    
    # Test that default checks were added
    checks = checker.checks
    assert len(checks) > 0
    
    # Test running default checks (with mocking)
    with patch('psutil.disk_usage'), \
         patch('psutil.virtual_memory'), \
         patch('psutil.cpu_percent', return_value=45.2):
        
        # Run all checks
        results = checker.run_all_checks()
        assert results is not None
        assert len(results) > 0

@pytest.mark.unit
def test_performance_monitor_summary():
    """Test performance monitor summary functionality"""
    from src.monitoring.performance_monitor import PerformanceMonitor, MetricType
    
    monitor = PerformanceMonitor()
    
    # Add various metrics
    monitor.record_metric('counter1', 10, MetricType.COUNTER)
    monitor.record_metric('gauge1', 25.5, MetricType.GAUGE)
    monitor.record_metric('timer1', 0.1, MetricType.TIMER)
    
    # Get performance summary
    summary = monitor.get_performance_summary()
    assert summary is not None
    assert 'timestamp' in summary
    assert 'total_metrics' in summary
    assert summary['total_metrics'] >= 3

@pytest.mark.unit
def test_structured_logger_configuration():
    """Test structured logger configuration"""
    from src.monitoring.structured_logging import StructuredLogger
    
    # Test logger with different configurations
    logger1 = StructuredLogger("logger1")
    logger2 = StructuredLogger("logger2")
    
    # Test that loggers are independent
    assert logger1.name == "logger1"
    assert logger2.name == "logger2"
    
    # Test basic logging functionality
    logger1.info("Test message from logger1")
    logger2.info("Test message from logger2")

if __name__ == '__main__':
    pytest.main([__file__])
