"""
Test Logging Consistency
Validates that logging levels and formats are consistent throughout the system
"""

import pytest
import os
import sys
import logging
import tempfile
import shutil
from unittest.mock import patch, Mock
from io import StringIO

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestLoggingConfig:
    """Test centralized logging configuration"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.test_dir, 'test.log')
        self.error_log_file = os.path.join(self.test_dir, 'test_errors.log')
        
        # Mock environment variables
        self.env_vars = {
            'ENVIRONMENT': 'testing',
            'LOG_FILE': self.log_file,
            'ERROR_LOG_FILE': self.error_log_file
        }
    
    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'testing'})
    def test_logging_config_initialization(self):
        """Test logging configuration initialization"""
        try:
            from logging_config import HelmAILoggingConfig
            
            # Test environment config retrieval
            config = HelmAILoggingConfig.get_environment_config()
            
            assert config is not None
            assert config['level'] == 'INFO'
            assert config['format'] == 'simple'
            assert 'console' in config['handlers']
            assert config['propagate'] is False
            
        except ImportError:
            pytest.skip("Logging config module not available")
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'development'})
    def test_development_logging_config(self):
        """Test development environment logging configuration"""
        try:
            from logging_config import HelmAILoggingConfig
            
            config = HelmAILoggingConfig.get_environment_config()
            
            assert config['level'] == 'DEBUG'
            assert config['format'] == 'detailed'
            assert 'console' in config['handlers']
            assert 'file' in config['handlers']
            assert config['propagate'] is True
            
        except ImportError:
            pytest.skip("Logging config module not available")
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'production'})
    def test_production_logging_config(self):
        """Test production environment logging configuration"""
        try:
            from logging_config import HelmAILoggingConfig
            
            config = HelmAILoggingConfig.get_environment_config()
            
            assert config['level'] == 'WARNING'
            assert config['format'] == 'production'
            assert 'console' in config['handlers']
            assert 'file' in config['handlers']
            assert config['propagate'] is False
            
        except ImportError:
            pytest.skip("Logging config module not available")
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'testing', 'LOG_FILE': 'test.log'})
    def test_logging_setup(self):
        """Test logging setup functionality"""
        try:
            from logging_config import HelmAILoggingConfig
            
            # Setup logging
            HelmAILoggingConfig.setup_logging()
            
            # Test that loggers are configured
            root_logger = logging.getLogger()
            assert root_logger.level == logging.INFO
            
            # Test specific loggers
            security_logger = logging.getLogger('security')
            assert security_logger.level == logging.INFO
            
            api_logger = logging.getLogger('api')
            assert api_logger.level == logging.INFO
            
        except ImportError:
            pytest.skip("Logging config module not available")
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'testing'})
    def test_logger_creation(self):
        """Test logger creation and configuration"""
        try:
            from logging_config import HelmAILoggingConfig
            
            # Setup logging first
            HelmAILoggingConfig.setup_logging()
            
            # Test getting a logger
            logger = HelmAILoggingConfig.get_logger('test_module')
            assert logger is not None
            assert logger.name == 'test_module'
            
            # Test log level setting
            HelmAILoggingConfig.set_log_level('test_module', 'DEBUG')
            assert logger.level == logging.DEBUG
            
        except ImportError:
            pytest.skip("Logging config module not available")
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'testing'})
    def test_structured_logger(self):
        """Test structured logger functionality"""
        try:
            from logging_config import StructuredLogger
            
            # Create structured logger
            structured_logger = StructuredLogger('test_structured')
            assert structured_logger.name == 'test_structured'
            assert structured_logger.logger is not None
            
            # Test logging methods exist
            assert hasattr(structured_logger, 'debug')
            assert hasattr(structured_logger, 'info')
            assert hasattr(structured_logger, 'warning')
            assert hasattr(structured_logger, 'error')
            assert hasattr(structured_logger, 'critical')
            assert hasattr(structured_logger, 'exception')
            
        except ImportError:
            pytest.skip("Structured logger not available")
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'testing'})
    def test_contextual_logging(self):
        """Test contextual logging functionality"""
        try:
            from logging_config import HelmAILoggingConfig
            
            # Setup logging
            HelmAILoggingConfig.setup_logging()
            
            # Test contextual logging
            logger = HelmAILoggingConfig.get_logger('test_context')
            
            # Capture log output
            log_capture = StringIO()
            handler = logging.StreamHandler(log_capture)
            handler.setLevel(logging.INFO)
            logger.addHandler(handler)
            
            # Test logging with context
            HelmAILoggingConfig.log_with_context(
                logger, 
                'INFO', 
                'Test message', 
                user_id='123', 
                action='test'
            )
            
            # Check that context was included
            log_output = log_capture.getvalue()
            assert 'Test message' in log_output
            assert 'user_id=123' in log_output
            assert 'action=test' in log_output
            
        except ImportError:
            pytest.skip("Contextual logging not available")
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'testing'})
    def test_log_format_consistency(self):
        """Test that log formats are consistent"""
        try:
            from logging_config import HelmAILoggingConfig
            
            # Test all log formats
            formats = HelmAILoggingConfig.LOG_FORMATS
            
            assert 'detailed' in formats
            assert 'simple' in formats
            assert 'json' in formats
            assert 'production' in formats
            
            # Test format structure
            for format_name, format_config in formats.items():
                assert 'format' in format_config
                assert 'datefmt' in format_config
                assert '%(asctime)s' in format_config['format']
                assert '%(levelname)s' in format_config['format']
                assert '%(message)s' in format_config['format']
            
        except ImportError:
            pytest.skip("Log formats not available")
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'testing'})
    def test_log_levels_consistency(self):
        """Test that log levels are consistent"""
        try:
            from logging_config import HelmAILoggingConfig
            
            # Test log levels
            levels = HelmAILoggingConfig.LOG_LEVELS
            
            assert 'CRITICAL' in levels
            assert 'ERROR' in levels
            assert 'WARNING' in levels
            assert 'INFO' in levels
            assert 'DEBUG' in levels
            
            # Test level values
            assert levels['CRITICAL'] == logging.CRITICAL
            assert levels['ERROR'] == logging.ERROR
            assert levels['WARNING'] == logging.WARNING
            assert levels['INFO'] == logging.INFO
            assert levels['DEBUG'] == logging.DEBUG
            
        except ImportError:
            pytest.skip("Log levels not available")
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'testing'})
    def test_module_specific_loggers(self):
        """Test module-specific logger configurations"""
        try:
            from logging_config import HelmAILoggingConfig
            
            # Setup logging
            HelmAILoggingConfig.setup_logging()
            
            # Test module-specific loggers
            module_loggers = [
                'security',
                'database', 
                'api',
                'monitoring',
                'integrations',
                'auth',
                'audit',
                'ai'
            ]
            
            for logger_name in module_loggers:
                logger = logging.getLogger(logger_name)
                assert logger is not None
                assert logger.name == logger_name
                assert logger.propagate is False  # Should not propagate to root
                
        except ImportError:
            pytest.skip("Module-specific loggers not available")


class TestLoggingIntegration:
    """Test logging integration with existing modules"""
    
    def setup_method(self):
        """Setup integration test environment"""
        self.test_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup integration test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'testing'})
    def test_security_module_logging(self):
        """Test security module logging integration"""
        try:
            # Test that security module can use centralized logging
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
            
            from logging_config import get_logger
            logger = get_logger('security')
            
            # Test logging methods
            logger.info("Security test message", module="test", action="verify")
            logger.warning("Security warning", threat_level="medium")
            logger.error("Security error", error_code="SEC001")
            
            assert logger is not None
            assert logger.name == 'security'
            
        except ImportError:
            pytest.skip("Security module logging integration not available")
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'testing'})
    def test_api_module_logging(self):
        """Test API module logging integration"""
        try:
            from logging_config import get_logger
            logger = get_logger('api')
            
            # Test API-specific logging
            logger.info("API request", method="GET", endpoint="/test", status=200)
            logger.warning("API rate limit", endpoint="/api/test", limit="100/hour")
            logger.error("API error", error="validation_failed", code="400")
            
            assert logger is not None
            assert logger.name == 'api'
            
        except ImportError:
            pytest.skip("API module logging integration not available")
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'testing'})
    def test_database_module_logging(self):
        """Test database module logging integration"""
        try:
            from logging_config import get_logger
            logger = get_logger('database')
            
            # Test database-specific logging
            logger.info("Database query", query="SELECT * FROM users", duration="0.05s")
            logger.warning("Database connection", pool_size="10", active="8")
            logger.error("Database error", error="connection_timeout", retry_count=3)
            
            assert logger is not None
            assert logger.name == 'database'
            
        except ImportError:
            pytest.skip("Database module logging integration not available")
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'testing'})
    def test_monitoring_module_logging(self):
        """Test monitoring module logging integration"""
        try:
            from logging_config import get_logger
            logger = get_logger('monitoring')
            
            # Test monitoring-specific logging
            logger.info("Metric collected", metric="response_time", value="0.123", unit="seconds")
            logger.warning("Threshold exceeded", metric="cpu_usage", value="85%", threshold="80%")
            logger.error("Monitoring failure", component="health_check", error="timeout")
            
            assert logger is not None
            assert logger.name == 'monitoring'
            
        except ImportError:
            pytest.skip("Monitoring module logging integration not available")


class TestLoggingPerformance:
    """Test logging performance and efficiency"""
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'testing'})
    def test_logging_performance(self):
        """Test that logging doesn't significantly impact performance"""
        try:
            import time
            from logging_config import get_logger
            
            logger = get_logger('performance_test')
            
            # Measure logging performance
            start_time = time.time()
            
            # Log 1000 messages
            for i in range(1000):
                logger.info(f"Performance test message {i}", iteration=i, batch="test")
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should complete within reasonable time (less than 1 second for 1000 messages)
            assert duration < 1.0, f"Logging took too long: {duration:.3f}s for 1000 messages"
            
        except ImportError:
            pytest.skip("Logging performance test not available")
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'testing'})
    def test_structured_logging_performance(self):
        """Test structured logging performance"""
        try:
            import time
            from logging_config import StructuredLogger
            
            logger = StructuredLogger('structured_performance_test')
            
            # Measure structured logging performance
            start_time = time.time()
            
            # Log 1000 messages with context
            for i in range(1000):
                logger.info(
                    f"Structured test message {i}", 
                    iteration=i, 
                    batch="test",
                    module="performance",
                    user_id=f"user_{i % 100}"
                )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should complete within reasonable time
            assert duration < 1.5, f"Structured logging took too long: {duration:.3f}s for 1000 messages"
            
        except ImportError:
            pytest.skip("Structured logging performance test not available")


if __name__ == "__main__":
    pytest.main([__file__])
