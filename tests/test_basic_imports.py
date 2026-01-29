"""
Basic import tests to identify missing dependencies and syntax errors
"""

import sys
import os
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_basic_python_imports():
    """Test basic Python imports"""
    import json
    import logging
    import datetime
    import threading
    import time
    import hashlib
    import base64
    assert True  # If we get here, basic imports work

def test_flask_imports():
    """Test Flask imports"""
    try:
        from flask import Flask, jsonify
        assert True
    except ImportError as e:
        pytest.skip(f"Flask not available: {e}")

def test_monitoring_imports():
    """Test monitoring module imports"""
    try:
        # Test without external dependencies
        from src.monitoring.health_checks import HealthStatus, CheckType
        assert HealthStatus.HEALTHY.value == "healthy"
        assert CheckType.DATABASE.value == "database"
    except ImportError as e:
        pytest.fail(f"Health checks import failed: {e}")

def test_api_imports():
    """Test API module imports"""
    try:
        from src.api.error_handling import ValidationException, AuthenticationException
        assert ValidationException("test").message == "test"
        assert AuthenticationException("test").message == "test"
    except ImportError as e:
        pytest.fail(f"API error handling import failed: {e}")

def test_auth_imports():
    """Test auth module imports"""
    try:
        from src.auth.rbac.role_manager import Permission, User
        assert Permission.USER_READ is not None
        user = User(user_id="test", email="test@example.com", name="Test")
        assert user.user_id == "test"
    except ImportError as e:
        pytest.fail(f"Auth RBAC import failed: {e}")

def test_database_imports():
    """Test database module imports"""
    try:
        from src.database.query_optimizer import QueryType, OptimizationLevel
        assert QueryType.SELECT.value == "select"
        assert OptimizationLevel.BASIC.value == "basic"
    except ImportError as e:
        pytest.fail(f"Database query optimizer import failed: {e}")

def test_security_imports():
    """Test security module imports"""
    try:
        from src.security.encryption import EncryptionType, KeyType
        assert EncryptionType.SYMMETRIC.value == "symmetric"
        assert KeyType.AES256.value == "aes256"
    except ImportError as e:
        pytest.fail(f"Security encryption import failed: {e}")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
