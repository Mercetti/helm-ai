"""
Monitoring modules test - focused on health checks, performance monitoring, and structured logging
"""

import pytest
import json
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

def test_monitoring_imports():
    """Test that monitoring modules can be imported"""
    try:
        from src.monitoring.health_checks import HealthChecker, HealthStatus, CheckType
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

@pytest.mark.monitoring
def test_health_checker_basic():
    """Test basic health checker functionality"""
    from src.monitoring.health_checks import HealthChecker, HealthStatus, CheckType
    
    # Test health checker creation
    checker = HealthChecker()
    assert checker is not None
    assert hasattr(checker, 'register_check')
    assert hasattr(checker, 'run_all_checks')
    assert hasattr(checker, 'get_health_status')
    
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

@pytest.mark.monitoring
def test_health_checker_registration():
    """Test health check registration and execution"""
    from src.monitoring.health_checks import HealthChecker, HealthStatus, CheckType
    
    checker = HealthChecker()
    
    # Test custom check registration
    def custom_check():
        return {
            'status': HealthStatus.HEALTHY,
            'message': 'Custom check passed',
            'timestamp': datetime.now().isoformat(),
            'details': {'custom': 'data'}
        }
    
    checker.register_check('custom_test', custom_check, CheckType.CUSTOM)
    
    # Test system check registration
    def system_check():
        return {
            'status': HealthStatus.HEALTHY,
            'message': 'System is healthy',
            'timestamp': datetime.now().isoformat(),
            'details': {'cpu_usage': 45.2, 'memory_usage': 67.8}
        }
    
    checker.register_check('system_test', system_check, CheckType.SYSTEM)
    
    # Test running all checks
    results = checker.run_all_checks()
    assert results is not None
    assert 'custom_test' in results
    assert 'system_test' in results
    assert results['custom_test']['status'] == HealthStatus.HEALTHY
    assert results['system_test']['status'] == HealthStatus.HEALTHY

@pytest.mark.monitoring
def test_health_checker_database():
    """Test database health checks"""
    from src.monitoring.health_checks import HealthChecker, HealthStatus
    
    checker = HealthChecker()
    
    # Mock database connection
    with patch('psutil.disk_usage'), \
         patch('psutil.virtual_memory'), \
         patch('psutil.cpu_percent'), \
         patch('sqlite3.connect') as mock_connect:
        
        # Mock successful database connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Test database check
        def db_check():
            return {
                'status': HealthStatus.HEALTHY,
                'message': 'Database is healthy',
                'timestamp': datetime.now().isoformat(),
                'details': {
                    'connection_pool': {'active': 5, 'idle': 2},
                    'disk_usage': {'total': 100, 'used': 45},
                    'memory_usage': {'total': 1000, 'used': 200}
                }
            }
        
        checker.register_check('database_test', db_check, CheckType.DATABASE)
        results = checker.run_all_checks()
        
        assert 'database_test' in results
        assert results['database_test']['status'] == HealthStatus.HEALTHY

@pytest.mark.monitoring
def test_health_checker_external():
    """Test external service health checks"""
    from src.monitoring.health_checks import HealthChecker, HealthStatus
    
    checker = HealthChecker()
    
    # Mock external service check
    with patch('requests.get') as mock_get:
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'ok',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        }
        mock_get.return_value = mock_response
        
        # Test external check
        def external_check():
            response = checker._check_external_service('https://api.example.com/health')
            return {
                'status': HealthStatus.HEALTHY if response['status'] == 'ok' else HealthStatus.UNHEALTHY,
                'message': 'External service is healthy' if response['status'] == 'ok' else 'External service is down',
                'timestamp': datetime.now().isoformat(),
                'details': response
            }
        
        checker.register_check('external_test', external_check, CheckType.EXTERNAL)
        results = checker.run_all_checks()
        
        assert 'external_test' in results
        assert results['external_test']['status'] == HealthStatus.HEALTHY

@pytest.mark.monitoring
def test_performance_monitor_basic():
    """Test basic performance monitor functionality"""
    from src.monitoring.performance_monitor import PerformanceMonitor, MetricType
    
    # Test monitor creation
    monitor = PerformanceMonitor()
    assert monitor is not None
    assert hasattr(monitor, 'record_metric')
    assert hasattr(monitor, 'get_metrics')
    assert hasattr(monitor, 'create_timer')
    
    # Test metric type enum
    assert MetricType.COUNTER == "counter"
    assert MetricType.GAUGE == "gauge"
    assert MetricType.HISTOGRAM == "histogram"
    assert MetricType.TIMER == "timer"
    
    # Test metric recording
    monitor.record_metric('test_counter', 1, MetricType.COUNTER)
    monitor.record_metric('test_gauge', 42.5, MetricType.GAUGE)
    
    metrics = monitor.get_metrics()
    assert 'test_counter' in metrics
    assert 'test_gauge' in metrics
    assert metrics['test_counter']['type'] == 'counter'
    assert metrics['test_counter']['value'] == 1
    assert metrics['test_gauge']['type'] == 'gauge'
    assert metrics['test_gauge']['value'] == 42.5

@pytest.mark.monitoring
def test_performance_monitor_timer():
    """Test performance monitor timer functionality"""
    from src.monitoring.performance_monitor import PerformanceMonitor, MetricType
    
    monitor = PerformanceMonitor()
    
    # Test timer decorator
    @monitor.create_timer('test_operation_timer')
    def test_operation():
        time.sleep(0.1)  # Simulate work
        return "operation_result"
    
    result = test_operation()
    assert result == "operation_result"
    
    # Check that timer was recorded
    metrics = monitor.get_metrics()
    assert 'test_operation_timer' in metrics
    assert metrics['test_operation_timer']['type'] == 'timer'
    assert metrics['test_operation_timer']['count'] > 0
    assert metrics['test_operation_timer']['avg_time'] > 0

@pytest.mark.monitoring
def test_performance_monitor_histogram():
    """Test performance monitor histogram functionality"""
    from src.monitoring.performance_monitor import PerformanceMonitor, MetricType
    
    monitor = PerformanceMonitor()
    
    # Test histogram recording
    test_values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    for value in test_values:
        monitor.record_metric('test_histogram', value, MetricType.HISTOGRAM)
    
    metrics = monitor.get_metrics()
    assert 'test_histogram' in metrics
    assert metrics['test_histogram']['type'] == 'histogram'
    assert metrics['test_histogram']['count'] == len(test_values)
    assert 'min' in metrics['test_histogram']
    assert 'max' in metrics['test_histogram']
    assert 'avg' in metrics['test_histogram']
    assert metrics['test_histogram']['min'] == min(test_values)
    assert metrics['test_histogram']['max'] == max(test_values)

@pytest.mark.monitoring
def test_performance_monitor_system_metrics():
    """Test system metrics collection"""
    from src.monitoring.performance_monitor import PerformanceMonitor
    
    monitor = PerformanceMonitor()
    
    # Test system metrics collection
    with patch('psutil.cpu_percent', return_value=45.2), \
         patch('psutil.virtual_memory', return_value=Mock(used=67.8, total=100)), \
         patch('psutil.disk_usage', return_value=[Mock(free=50, total=100)]):
        
        system_metrics = monitor.get_system_metrics()
        assert system_metrics is not None
        assert 'cpu_usage' in system_metrics
        assert 'memory_usage' in system_metrics
        assert 'disk_usage' in system_metrics
        assert system_metrics['cpu_usage'] == 45.2
        assert system_metrics['memory_usage']['used'] == 67.8
        assert system_metrics['memory_usage']['total'] == 100

@pytest.mark.monitoring
def test_structured_logger_basic():
    """Test basic structured logger functionality"""
    from src.monitoring.structured_logging import StructuredLogger, LogLevel
    
    # Test logger creation
    logger = StructuredLogger()
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

@pytest.mark.monitoring
def test_structured_logger_logging():
    """Test structured logging functionality"""
    from src.monitoring.structured_logging import StructuredLogger, LogLevel
    
    logger = StructuredLogger()
    
    # Test different log levels
    logger.info("Test info message", extra_data={'key': 'value'})
    logger.warning("Test warning message")
    logger.error("Test error message", error_code="TEST_ERROR")
    logger.debug("Test debug message")
    
    # Test structured log format
    with patch('pythonjsonlogger.logger') as mock_logger:
        # Mock the logger to capture calls
        mock_logger.info.assert_called()
        mock_logger.warning.assert_called()
        mock_logger.error.assert_called()
        
        # Test info log with structured data
        logger.info("Test message", user_id="user123", action="test")
        
        # Verify the call was made with correct parameters
        call_args = mock_logger.info.call_args
        assert call_args[0][0] == "Test message"
        assert call_args[1]['user_id'] == "user123"
        assert call_args[1]['action'] == "test"

@pytest.mark.monitoring
def test_structured_logger_context():
    """Test structured logger context management"""
    from src.monitoring.structured_logging import StructuredLogger
    
    logger = StructuredLogger()
    
    # Test context logging
    with logger.context(request_id="req_123", user_id="user_456"):
        logger.info("Context test message")
        logger.warning("Context warning")
    
    # Test context extraction
    context = logger.get_current_context()
    assert context is not None
    assert 'request_id' in context
    assert 'user_id' in context
    assert context['request_id'] == "req_123"
    assert context['user_id'] == "user_456"

@pytest.mark.monitoring
def test_structured_logger_error_handling():
    """Test structured logger error handling"""
    from src.monitoring.structured_logging import StructuredLogger
    
    logger = StructuredLogger()
    
    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception as e:
        logger.error("Exception occurred", exception=e, error_code="TEST_EXCEPTION")
    
    # Test error logging with traceback
    with patch('traceback.format_exc', return_value="Test traceback"):
        logger.error("Error with traceback", error_code="TEST_TRACEBACK", include_traceback=True)

@pytest.mark.monitoring
def test_monitoring_integration():
    """Test integration between monitoring modules"""
    from src.monitoring.health_checks import HealthChecker
    from src.monitoring.performance_monitor import PerformanceMonitor
    from src.monitoring.structured_logging import StructuredLogger
    
    # Create monitoring components
    health_checker = HealthChecker()
    performance_monitor = PerformanceMonitor()
    structured_logger = StructuredLogger()
    
    # Test that all components can be created
    assert health_checker is not None
    assert performance_monitor is not None
    assert structured_logger is not None
    
    # Test integration scenario
    def integrated_health_check():
        # Record performance metrics during health check
        start_time = time.time()
        
        # Simulate health check work
        time.sleep(0.05)
        
        # Record timing metric
        end_time = time.time()
        performance_monitor.record_metric('health_check_duration', end_time - start_time, 'timer')
        
        return {
            'status': 'healthy',
            'message': 'Integrated health check',
            'performance_metrics': performance_monitor.get_metrics()
        }
    
    health_checker.register_check('integrated_check', integrated_health_check)
    
    # Run integrated check and log results
    results = health_checker.run_all_checks()
    structured_logger.info("Health check completed", results=results)
    
    assert 'integrated_check' in results
    assert results['integrated_check']['status'] == 'healthy'

@pytest.mark.monitoring
def test_monitoring_error_scenarios():
    """Test monitoring error scenarios"""
    from src.monitoring.health_checks import HealthChecker, HealthStatus
    from src.monitoring.performance_monitor import PerformanceMonitor
    
    # Test health check failure
    health_checker = HealthChecker()
    
    def failing_check():
        return {
            'status': HealthStatus.UNHEALTHY,
            'message': 'Check failed',
            'timestamp': datetime.now().isoformat(),
            'error': 'Simulated failure'
        }
    
    health_checker.register_check('failing_test', failing_check)
    results = health_checker.run_all_checks()
    
    assert 'failing_test' in results
    assert results['failing_test']['status'] == HealthStatus.UNHEALTHY
    
    # Test performance monitoring with errors
    monitor = PerformanceMonitor()
    
    # Test with invalid metric type
    try:
        monitor.record_metric('invalid_metric', 'invalid_value', 'invalid_type')
        assert False, "Should have raised error for invalid metric type"
    except (ValueError, TypeError):
        pass  # Expected
    
    # Test timer with exception
    @monitor.create_timer('error_timer')
    def error_function():
        raise RuntimeError("Simulated error")
    
    try:
        error_function()
    except RuntimeError:
        pass  # Expected
    
    # Check that error was recorded
    metrics = monitor.get_metrics()
    assert 'error_timer' in metrics
    assert metrics['error_timer']['error_count'] > 0

@pytest.mark.monitoring
def test_monitoring_configuration():
    """Test monitoring configuration"""
    from src.monitoring.health_checks import HealthChecker
    from src.monitoring.performance_monitor import PerformanceMonitor
    from src.monitoring.structured_logging import StructuredLogger
    
    # Test configuration options
    health_checker = HealthChecker(
        check_interval=30,
        timeout=10,
        retry_attempts=3
    )
    
    performance_monitor = PerformanceMonitor(
        metrics_retention_hours=24,
        aggregation_interval=60,
        max_metrics_per_type=1000
    )
    
    structured_logger = StructuredLogger(
        log_level="INFO",
        enable_console=True,
        enable_file=False,
        enable_cloud=False
    )
    
    # Verify configuration was applied
    assert health_checker.check_interval == 30
    assert health_checker.timeout == 10
    assert health_checker.retry_attempts == 3
    assert performance_monitor.metrics_retention_hours == 24
    assert structured_logger.log_level == "INFO"

@pytest.mark.monitoring
def test_monitoring_thread_safety():
    """Test monitoring thread safety"""
    from src.monitoring.performance_monitor import PerformanceMonitor
    from src.monitoring.structured_logging import StructuredLogger
    
    monitor = PerformanceMonitor()
    logger = StructuredLogger()
    
    # Test concurrent metric recording
    def worker_thread(thread_id):
        for i in range(100):
            monitor.record_metric(f'thread_{thread_id}_counter', i, 'counter')
            logger.info(f'Thread {thread_id} iteration {i}')
    
    # Create multiple threads
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker_thread, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify all metrics were recorded
    metrics = monitor.get_metrics()
    assert 'thread_0_counter' in metrics
    assert 'thread_1_counter' in metrics
    assert 'thread_2_counter' in metrics
    assert metrics['thread_0_counter']['value'] == 99
    assert metrics['thread_1_counter']['value'] == 99
    assert metrics['thread_2_counter']['value'] == 99

if __name__ == '__main__':
    pytest.main([__file__])
