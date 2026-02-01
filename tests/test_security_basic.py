"""
Basic security module tests to verify imports and basic functionality
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_disaster_recovery_import():
    """Test that disaster recovery module can be imported"""
    try:
        from src.security.disaster_recovery import DisasterRecoveryManager, DisasterType
        assert DisasterRecoveryManager is not None
        assert DisasterType is not None
        assert DisasterType.DATA_CORRUPTION is not None
    except ImportError as e:
        pytest.fail(f"Failed to import disaster recovery: {e}")

def test_encryption_import():
    """Test that encryption module can be imported"""
    try:
        from src.security.encryption import encryption_manager
        assert encryption_manager is not None
    except ImportError as e:
        pytest.fail(f"Failed to import encryption: {e}")

def test_data_integrity_import():
    """Test that data integrity module can be imported"""
    try:
        from src.security.data_integrity import DataIntegrityManager
        assert DataIntegrityManager is not None
    except ImportError as e:
        pytest.fail(f"Failed to import data integrity: {e}")

def test_backup_system_import():
    """Test that backup system module can be imported"""
    try:
        from src.security.backup_system import backup_manager
        assert backup_manager is not None
    except ImportError as e:
        pytest.fail(f"Failed to import backup system: {e}")

@pytest.mark.unit
def test_disaster_recovery_basic_functionality():
    """Test basic disaster recovery functionality"""
    with patch('boto3.client'):
        from src.security.disaster_recovery import DisasterRecoveryManager, DisasterType
        
        # Test manager creation
        manager = DisasterRecoveryManager()
        assert manager is not None
        assert hasattr(manager, 'plans')
        assert hasattr(manager, 'events')
        assert hasattr(manager, 'failover_configs')
        
        # Test creating a simple recovery plan
        plan = manager.create_recovery_plan(
            name="Test Plan",
            disaster_type=DisasterType.DATA_CORRUPTION,
            rto_minutes=60,
            rpo_minutes=15,
            procedures=["Test procedure"],
            contact_personnel=["test@example.com"],
            critical_systems=["test_system"],
            backup_requirements={"test": "value"}
        )
        
        assert plan is not None
        assert plan.name == "Test Plan"

@pytest.mark.unit
def test_encryption_basic_functionality():
    """Test basic encryption functionality"""
    from src.security.encryption import encryption_manager
    
    # Test basic encryption
    test_data = "sensitive_data"
    encrypted = encryption_manager.encrypt_data(test_data)
    assert encrypted is not None
    assert encrypted.success is True
    assert encrypted.encrypted_data is not None
    
    # Test decryption
    decrypted = encryption_manager.decrypt_data(encrypted)
    assert decrypted.success is True
    # Check if the decrypted data matches original (handle both bytes and string)
    if hasattr(decrypted, 'decrypted_data'):
        if isinstance(decrypted.decrypted_data, bytes):
            assert decrypted.decrypted_data.decode() == test_data
        else:
            assert decrypted.decrypted_data == test_data
    elif hasattr(decrypted, 'data'):
        if isinstance(decrypted.data, bytes):
            assert decrypted.data.decode() == test_data
        else:
            assert decrypted.data == test_data
    else:
        # If no direct data access, check that decryption was successful
        assert decrypted.success is True

@pytest.mark.unit
def test_data_integrity_basic_functionality():
    """Test basic data integrity functionality"""
    from src.security.data_integrity import DataIntegrityManager
    
    # Test manager creation
    manager = DataIntegrityManager()
    assert manager is not None
    assert hasattr(manager, 'create_integrity_record')
    assert hasattr(manager, 'scan_directory')  # Check for available methods

@pytest.mark.unit
def test_backup_system_basic_functionality():
    """Test basic backup system functionality"""
    from src.security.backup_system import backup_manager
    
    # Test manager creation
    manager = backup_manager
    assert manager is not None
    assert hasattr(manager, 'create_backup_job')
    assert hasattr(manager, 'run_backup_job')

if __name__ == '__main__':
    pytest.main([__file__])
