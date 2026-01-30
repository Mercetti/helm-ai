"""
Helm AI Test Configuration
This module provides pytest configuration and shared test fixtures
"""

import os
import sys
import pytest
import tempfile
import shutil
from typing import Generator, Dict, Any, List
from unittest.mock import Mock, MagicMock
import json
import sqlite3
import redis
from datetime import datetime, timedelta

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture(scope='session')
def test_config():
    """Test configuration fixture"""
    return {
        'TEST_DATABASE_URL': 'sqlite:///:memory:',
        'TEST_REDIS_URL': 'redis://localhost:6379/1',
        'TEST_DATA_DIR': tempfile.mkdtemp(),
        'TEST_LOG_LEVEL': 'DEBUG',
        'ENVIRONMENT': 'test',
        'TESTING': 'true',
        'ENABLE_RATE_LIMITING': 'false',
        'ENABLE_INPUT_VALIDATION': 'true',
        'ENABLE_REQUEST_LOGGING': 'false',
        'ENABLE_SECURITY_HEADERS': 'true',
        'ENABLE_CORS': 'true'
    }

@pytest.fixture(scope='session')
def test_database(test_config):
    """Test database fixture"""
    # Create in-memory SQLite database
    conn = sqlite3.connect(':memory:')
    
    # Create tables
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            plan TEXT DEFAULT 'free',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # API keys table
    cursor.execute('''
        CREATE TABLE api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_id TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            name TEXT NOT NULL,
            permissions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Audit logs table
    cursor.execute('''
        CREATE TABLE audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            resource TEXT,
            details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Performance metrics table
    cursor.execute('''
        CREATE TABLE performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value REAL,
            metric_type TEXT,
            labels TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    
    yield conn
    
    conn.close()

@pytest.fixture(scope='session')
def test_redis(test_config):
    """Test Redis fixture"""
    try:
        # Try to connect to Redis
        client = redis.from_url(test_config['TEST_REDIS_URL'])
        
        # Test connection
        client.ping()
        
        # Clear test database
        client.flushdb()
        
        yield client
        
        # Cleanup
        client.flushdb()
        
    except redis.ConnectionError:
        # Skip Redis tests if not available
        pytest.skip("Redis not available for testing")

@pytest.fixture
def mock_s3_client():
    """Mock AWS S3 client"""
    mock_client = Mock()
    
    # Mock upload_file method
    mock_client.upload_file = Mock(return_value={'ETag': '"test-etag"'})
    
    # Mock download_file method
    mock_client.download_file = Mock()
    
    # Mock delete_object method
    mock_client.delete_object = Mock()
    
    # Mock list_objects_v2 method
    mock_client.list_objects_v2 = Mock(return_value={
        'Contents': [
            {'Key': 'test-file.txt', 'Size': 1024, 'LastModified': '2023-01-01T00:00:00Z'}
        ]
    })
    
    return mock_client

@pytest.fixture
def mock_kms_client():
    """Mock AWS KMS client"""
    mock_client = Mock()
    
    # Mock encrypt method
    mock_client.encrypt = Mock(return_value={
        'CiphertextBlob': b'encrypted-data'
    })
    
    # Mock decrypt method
    mock_client.decrypt = Mock(return_value={
        'Plaintext': b'decrypted-data'
    })
    
    return mock_client

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'email': 'test@example.com',
        'name': 'Test User',
        'plan': 'free'
    }

@pytest.fixture
def sample_api_key_data():
    """Sample API key data for testing"""
    return {
        'key_id': 'test-key-123',
        'name': 'Test API Key',
        'permissions': ['read', 'write']
    }

@pytest.fixture
def sample_github_data():
    """Sample GitHub data for testing"""
    return {
        'repository': 'test/repo',
        'commit': 'abc123',
        'author': 'testuser',
        'message': 'Test commit'
    }

@pytest.fixture
def sample_slack_data():
    """Sample Slack data for testing"""
    return {
        'webhook_url': 'https://hooks.slack.com/test',
        'channel': '#general',
        'message': 'Test message'
    }

@pytest.fixture
def temp_directory():
    """Temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_email_client():
    """Mock email client"""
    mock_client = Mock()
    
    # Mock send_email method
    mock_client.send_email = Mock(return_value={'message_id': 'test-message-id'})
    
    # Mock send_template method
    mock_client.send_template = Mock(return_value={'message_id': 'test-template-id'})
    
    return mock_client

@pytest.fixture
def mock_analytics_client():
    """Mock analytics client"""
    mock_client = Mock()
    
    # Mock track_event method
    mock_client.track_event = Mock(return_value={'status': 'success'})
    
    # Mock get_user_analytics method
    mock_client.get_user_analytics = Mock(return_value={
        'total_events': 100,
        'active_days': 30
    })
    
    return mock_client

@pytest.fixture
def mock_support_client():
    """Mock support client"""
    mock_client = Mock()
    
    # Mock create_ticket method
    mock_client.create_ticket = Mock(return_value={'id': 'ticket-123'})
    
    # Mock get_ticket method
    mock_client.get_ticket = Mock(return_value={
        'id': 'ticket-123',
        'subject': 'Test ticket',
        'status': 'open'
    })
    
    return mock_client

@pytest.fixture
def mock_encryption_manager():
    """Mock encryption manager"""
    mock_manager = Mock()
    
    # Mock encrypt method
    mock_manager.encrypt = Mock(return_value=b'encrypted-data')
    
    # Mock decrypt method
    mock_manager.decrypt = Mock(return_value=b'decrypted-data')
    
    # Mock encrypt_data method
    mock_manager.encrypt_data = Mock(return_value={
        'success': True,
        'encrypted_data': b'encrypted-data',
        'key_id': 'test-key'
    })
    
    # Mock decrypt_data method
    mock_manager.decrypt_data = Mock(return_value={
        'success': True,
        'decrypted_data': b'decrypted-data'
    })
    
    return mock_manager

@pytest.fixture
def mock_backup_manager():
    """Mock backup manager"""
    mock_manager = Mock()
    
    # Mock create_backup_job method
    mock_manager.create_backup_job = Mock(return_value={'job_id': 'backup-123'})
    
    # Mock run_backup_job method
    mock_manager.run_backup_job = Mock(return_value={'backup_id': 'backup-456'})
    
    return mock_manager

@pytest.fixture
def mock_rate_limit_manager():
    """Mock rate limit manager"""
    mock_manager = Mock()
    
    # Mock check_rate_limit method
    mock_manager.check_rate_limit = Mock(return_value=(True, None))
    
    # Mock get_rate_limit_status method
    mock_manager.get_rate_limit_status = Mock(return_value={
        'allowed': True,
        'limits': []
    })
    
    return mock_manager

@pytest.fixture
def sample_request_data():
    """Sample request data for testing"""
    return {
        'method': 'POST',
        'url': 'https://api.example.com/test',
        'headers': {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
        },
        'body': json.dumps({'test': 'data'})
    }

@pytest.fixture
def sample_response_data():
    """Sample response data for testing"""
    return {
        'status_code': 200,
        'headers': {
            'Content-Type': 'application/json',
            'X-Request-ID': 'test-request-id'
        },
        'body': json.dumps({'success': True, 'data': []})
    }

@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    logger = Mock()
    
    # Mock log methods
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    
    return logger

@pytest.fixture
def sample_compliance_data():
    """Sample compliance data for testing"""
    return {
        'framework': 'gdpr',
        'requirements': [
            'data_processing_records',
            'consent_management',
            'data_subject_requests'
        ],
        'violations': [],
        'score': 95.0
    }

@pytest.fixture
def sample_performance_data():
    """Sample performance data for testing"""
    return {
        'metrics': {
            'response_time': 150.5,
            'throughput': 1000,
            'error_rate': 0.02,
            'cpu_usage': 45.2,
            'memory_usage': 512.3
        },
        'timestamp': datetime.now().isoformat()
    }

@pytest.fixture
def sample_health_check_data():
    """Sample health check data for testing"""
    return {
        'status': 'healthy',
        'checks': {
            'database': {'status': 'healthy', 'message': 'OK'},
            'cache': {'status': 'healthy', 'message': 'OK'},
            'disk_space': {'status': 'healthy', 'message': '85% used'}
        },
        'timestamp': datetime.now().isoformat()
    }

# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    # Add custom markers
    config.addinivalue_line(
        "markers",
        "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers",
        "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers",
        "performance: Performance tests"
    )
    config.addinivalue_line(
        "markers",
        "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers",
        "external: Tests requiring external services"
    )
    
    # Test discovery patterns
    config.addinivalue_line(
        "python_files",
        "tests/test_*.py"
    )
    config.addinivalue_line(
        "python_classes",
        "Test*"
    )

# Custom markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.performance = pytest.mark.performance
pytest.mark.slow = pytest.mark.slow
pytest.mark.external = pytest.mark.external

# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Add slow marker to slow tests
    for item in items:
        if "performance" in str(item.fspath) or "load" in str(item.fspath):
            item.add_marker(pytest.mark.slow)
        
        if "external" in str(item.fspath) or "integration" in str(item.fspath):
            item.add_marker(pytest.mark.external)

# Environment setup
@pytest.fixture(scope='session', autouse=True)
def setup_test_environment():
    """Setup test environment"""
    # Set test environment variables
    os.environ['ENVIRONMENT'] = 'test'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    os.environ['TESTING'] = 'true'
    os.environ['ENABLE_RATE_LIMITING'] = 'false'
    os.environ['ENABLE_INPUT_VALIDATION'] = 'true'
    os.environ['ENABLE_REQUEST_LOGGING'] = 'false'
    os.environ['ENABLE_SECURITY_HEADERS'] = 'true'
    os.environ['ENABLE_CORS'] = 'true'
    
    # Create test directories if they don't exist
    test_dirs = [
        'tests/data',
        'tests/fixtures',
        'tests/reports'
    ]
    
    for dir_path in test_dirs:
        os.makedirs(dir_path, exist_ok=True)

# Cleanup after tests
@pytest.fixture(scope='session', autouse=True)
def cleanup_test_environment():
    """Cleanup test environment after tests"""
    yield
    
    # Cleanup test environment variables
    test_vars = ['TESTING']
    for var in test_vars:
        if var in os.environ:
            del os.environ[var]

# Test utilities
class TestDataGenerator:
    """Utility class for generating test data"""
    
    @staticmethod
    def create_test_user(email: str = None, name: str = None, plan: str = 'free') -> Dict[str, Any]:
        """Create test user data"""
        return {
            'email': email or f'test-{datetime.now().timestamp()}@example.com',
            'name': name or 'Test User',
            'plan': plan
        }
    
    @staticmethod
    def create_test_api_key(user_id: int = 1, permissions: List[str] = None) -> Dict[str, Any]:
        """Create test API key data"""
        return {
            'key_id': f'test-key-{datetime.now().timestamp()}',
            'user_id': user_id,
            'name': 'Test API Key',
            'permissions': permissions or ['read']
        }
    
    @staticmethod
    def create_test_session(user_id: int = 1, expires_hours: int = 1) -> Dict[str, Any]:
        """Create test session data"""
        expires_at = datetime.now() + timedelta(hours=expires_hours)
        return {
            'session_id': f'test-session-{datetime.now().timestamp()}',
            'user_id': user_id,
            'expires_at': expires_at.isoformat()
        }

@pytest.fixture
def test_data_generator():
    """Test data generator fixture"""
    return TestDataGenerator()

@pytest.fixture
def mock_ai_model():
    """Mock AI model for testing"""
    mock_model = Mock()
    
    # Mock predict method
    mock_model.predict = Mock(return_value={
        'prediction': 'cheat_detected',
        'confidence': 0.95,
        'features': {'aimbot': 0.8, 'wallhack': 0.6}
    })
    
    # Mock train method
    mock_model.train = Mock(return_value={'loss': 0.1, 'accuracy': 0.95})
    
    # Mock evaluate method
    mock_model.evaluate = Mock(return_value={'accuracy': 0.94, 'precision': 0.92})
    
    return mock_model

@pytest.fixture
def sample_gaming_data():
    """Sample gaming data for testing"""
    return {
        'player_id': 'player_123',
        'game_session': 'session_456',
        'actions': [
            {'action': 'aim', 'timestamp': '2026-01-28T20:30:00Z', 'precision': 0.95},
            {'action': 'shoot', 'timestamp': '2026-01-28T20:30:05Z', 'hit': True}
        ],
        'metadata': {
            'game_type': 'fps',
            'duration': 1800,
            'score': 2500
        }
    }

@pytest.fixture
def sample_security_event():
    """Sample security event for testing"""
    return {
        'event_id': 'event_789',
        'type': 'suspicious_activity',
        'severity': 'high',
        'player_id': 'player_123',
        'description': 'Unusual aiming patterns detected',
        'timestamp': '2026-01-28T20:30:00Z',
        'evidence': {
            'aim_precision': 0.99,
            'reaction_time': 0.05,
            'headshot_ratio': 0.95
        }
    }

@pytest.fixture
def mock_file_system():
    """Mock file system for testing"""
    import tempfile
    import os
    
    temp_dir = tempfile.mkdtemp()
    
    # Create test files
    test_files = {
        'config.json': '{"setting": "value"}',
        'data.csv': 'id,name,value\n1,test,100',
        'log.txt': '2026-01-28 INFO: Test log entry'
    }
    
    created_files = {}
    for filename, content in test_files.items():
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)
        created_files[filename] = file_path
    
    yield created_files, temp_dir
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
