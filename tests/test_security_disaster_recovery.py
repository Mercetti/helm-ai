"""
Comprehensive tests for disaster recovery module
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from threading import Event

from src.security.disaster_recovery import (
    DisasterRecoveryManager, 
    DisasterType, 
    RecoveryStatus,
    DisasterEvent,
    RecoveryPlan,
    FailoverConfig,
    BackupStatus
)


class TestDisasterRecoveryManager:
    """Unit tests for DisasterRecoveryManager"""
    
    @pytest.fixture
    def recovery_manager(self):
        """Create disaster recovery manager for testing"""
        manager = DisasterRecoveryManager()
        # Clear any existing plans for clean testing
        manager.plans.clear()
        manager.events.clear()
        return manager
    
    @pytest.fixture
    def sample_recovery_plan(self):
        """Sample recovery plan for testing"""
        return RecoveryPlan(
            plan_id="test_plan_1",
            name="Test Data Recovery Plan",
            disaster_type=DisasterType.DATA_CORRUPTION,
            rto_minutes=1200,  # Recovery Time Objective
            rpo_minutes=60,   # Recovery Point Objective
            procedures=[
                "Identify corrupted data",
                "Restore from backup", 
                "Verify data integrity"
            ],
            contact_personnel=["admin@helm-ai.com", "ops@helm-ai.com"],
            critical_systems=["database", "storage", "api"],
            backup_requirements={
                "backup_frequency": "hourly",
                "backup_retention": "30_days",
                "backup_location": "s3://helm-ai-backups"
            }
        )
    
    @pytest.mark.unit
    def test_create_recovery_plan(self, recovery_manager, sample_recovery_plan):
        """Test creating a recovery plan"""
        result = recovery_manager.create_recovery_plan(
            name=sample_recovery_plan.name,
            disaster_type=sample_recovery_plan.disaster_type,
            rto_minutes=sample_recovery_plan.rto_minutes,
            rpo_minutes=sample_recovery_plan.rpo_minutes,
            procedures=sample_recovery_plan.procedures,
            contact_personnel=sample_recovery_plan.contact_personnel,
            critical_systems=sample_recovery_plan.critical_systems,
            backup_requirements=sample_recovery_plan.backup_requirements
        )
        
        assert result is not None
        assert result.name == "Test Data Recovery Plan"
        assert result.disaster_type == DisasterType.DATA_CORRUPTION
    
    @pytest.mark.unit
    def test_create_duplicate_recovery_plan(self, recovery_manager, sample_recovery_plan):
        """Test creating duplicate recovery plan"""
        # Create plan first time
        recovery_manager.create_recovery_plan(
            name=sample_recovery_plan.name,
            disaster_type=sample_recovery_plan.disaster_type,
            rto_minutes=sample_recovery_plan.rto_minutes,
            rpo_minutes=sample_recovery_plan.rpo_minutes,
            procedures=sample_recovery_plan.procedures,
            contact_personnel=sample_recovery_plan.contact_personnel,
            critical_systems=sample_recovery_plan.critical_systems,
            backup_requirements=sample_recovery_plan.backup_requirements
        )
        
        # Try to create same plan again
        result = recovery_manager.create_recovery_plan(
            name=sample_recovery_plan.name,
            disaster_type=sample_recovery_plan.disaster_type,
            rto_minutes=sample_recovery_plan.rto_minutes,
            rpo_minutes=sample_recovery_plan.rpo_minutes,
            procedures=sample_recovery_plan.procedures,
            contact_personnel=sample_recovery_plan.contact_personnel,
            critical_systems=sample_recovery_plan.critical_systems,
            backup_requirements=sample_recovery_plan.backup_requirements
        )
        
        assert result is None  # Should return None for duplicate
    
    @pytest.mark.unit
    def test_update_recovery_plan(self, recovery_manager, sample_recovery_plan):
        """Test updating a recovery plan"""
        recovery_manager.create_recovery_plan(sample_recovery_plan)
        
        # Update the plan
        updated_plan = RecoveryPlan(
            plan_id="test_plan_1",
            disaster_type=DisasterType.DATA_CORRUPTION,
            severity="critical",
            title="Updated Test Plan",
            description="Updated description",
            steps=[{"step": 1, "action": "New step", "timeout": 100}],
            rollback_procedures=[],
            dependencies=["database"],
            estimated_recovery_time=100,
            success_criteria=["test_criteria"]
        )
        
        result = recovery_manager.update_recovery_plan(updated_plan)
        
        assert result is True
        assert recovery_manager.plans["test_plan_1"].severity == "critical"
        assert recovery_manager.plans["test_plan_1"].title == "Updated Test Plan"
    
    @pytest.mark.unit
    def test_update_nonexistent_recovery_plan(self, recovery_manager):
        """Test updating non-existent recovery plan"""
        fake_plan = RecoveryPlan(
            plan_id="nonexistent",
            disaster_type=DisasterType.DATA_CORRUPTION,
            severity="high",
            title="Fake Plan",
            description="Fake description",
            steps=[],
            rollback_procedures=[],
            dependencies=[],
            estimated_recovery_time=0,
            success_criteria=[]
        )
        
        result = recovery_manager.update_recovery_plan(fake_plan)
        
        assert result is False
    
    @pytest.mark.unit
    def test_delete_recovery_plan(self, recovery_manager, sample_recovery_plan):
        """Test deleting a recovery plan"""
        recovery_manager.create_recovery_plan(sample_recovery_plan)
        
        result = recovery_manager.delete_recovery_plan("test_plan_1")
        
        assert result is True
        assert "test_plan_1" not in recovery_manager.plans
    
    @pytest.mark.unit
    def test_delete_nonexistent_recovery_plan(self, recovery_manager):
        """Test deleting non-existent recovery plan"""
        result = recovery_manager.delete_recovery_plan("nonexistent")
        
        assert result is False
    
    @pytest.mark.unit
    def test_declare_disaster(self, recovery_manager, sample_recovery_plan):
        """Test declaring a disaster event"""
        recovery_manager.create_recovery_plan(sample_recovery_plan)
        
        event = recovery_manager.declare_disaster(
            disaster_type=DisasterType.DATA_CORRUPTION,
            severity="high",
            description="Test disaster event",
            recovery_plan_id="test_plan_1"
        )
        
        assert event is not None
        assert event.disaster_type == DisasterType.DATA_CORRUPTION
        assert event.severity == "high"
        assert event.description == "Test disaster event"
        assert event.recovery_plan_id == "test_plan_1"
        assert event.status == "declared"
    
    @pytest.mark.unit
    def test_declare_disaster_auto_plan_selection(self, recovery_manager, sample_recovery_plan):
        """Test declaring disaster with automatic plan selection"""
        recovery_manager.create_recovery_plan(sample_recovery_plan)
        
        event = recovery_manager.declare_disaster(
            disaster_type=DisasterType.DATA_CORRUPTION,
            severity="high",
            description="Test disaster event"
            # No recovery_plan_id specified
        )
        
        assert event is not None
        assert event.recovery_plan_id == "test_plan_1"  # Should auto-select
    
    @pytest.mark.unit
    def test_execute_recovery_plan(self, recovery_manager, sample_recovery_plan):
        """Test executing a recovery plan"""
        recovery_manager.create_recovery_plan(sample_recovery_plan)
        
        # Mock the step execution
        with patch.object(recovery_manager, '_execute_recovery_step') as mock_step:
            mock_step.return_value = True
            
            event = recovery_manager.declare_disaster(
                disaster_type=DisasterType.DATA_CORRUPTION,
                severity="high",
                description="Test disaster",
                recovery_plan_id="test_plan_1"
            )
            
            result = recovery_manager.execute_recovery_plan(event.event_id)
            
            assert result is True
            assert mock_step.call_count == 3  # Should call for each step
    
    @pytest.mark.unit
    def test_execute_recovery_plan_nonexistent_event(self, recovery_manager):
        """Test executing recovery plan for non-existent event"""
        result = recovery_manager.execute_recovery_plan("nonexistent_event")
        
        assert result is False
    
    @pytest.mark.unit
    def test_get_disaster_event(self, recovery_manager, sample_recovery_plan):
        """Test getting a disaster event"""
        recovery_manager.create_recovery_plan(sample_recovery_plan)
        
        event = recovery_manager.declare_disaster(
            disaster_type=DisasterType.DATA_CORRUPTION,
            severity="high",
            description="Test disaster",
            recovery_plan_id="test_plan_1"
        )
        
        retrieved_event = recovery_manager.get_disaster_event(event.event_id)
        
        assert retrieved_event is not None
        assert retrieved_event.event_id == event.event_id
        assert retrieved_event.description == "Test disaster"
    
    @pytest.mark.unit
    def test_get_disaster_events_by_type(self, recovery_manager, sample_recovery_plan):
        """Test getting disaster events by type"""
        recovery_manager.create_recovery_plan(sample_recovery_plan)
        
        # Create multiple events
        event1 = recovery_manager.declare_disaster(
            disaster_type=DisasterType.DATA_CORRUPTION,
            severity="high",
            description="Data corruption event"
        )
        
        event2 = recovery_manager.declare_disaster(
            disaster_type=DisasterType.NETWORK_OUTAGE,
            severity="medium",
            description="Network outage event"
        )
        
        data_corruption_events = recovery_manager.get_disaster_events_by_type(DisasterType.DATA_CORRUPTION)
        
        assert len(data_corruption_events) == 1
        assert data_corruption_events[0].event_id == event1.event_id
    
    @pytest.mark.unit
    def test_get_active_disasters(self, recovery_manager, sample_recovery_plan):
        """Test getting active disasters"""
        recovery_manager.create_recovery_plan(sample_recovery_plan)
        
        # Create active disaster
        active_event = recovery_manager.declare_disaster(
            disaster_type=DisasterType.DATA_CORRUPTION,
            severity="high",
            description="Active disaster"
        )
        
        # Create resolved disaster
        resolved_event = recovery_manager.declare_disaster(
            disaster_type=DisasterType.NETWORK_OUTAGE,
            severity="medium",
            description="Resolved disaster"
        )
        resolved_event.status = "resolved"
        
        active_disasters = recovery_manager.get_active_disasters()
        
        assert len(active_disasters) == 1
        assert active_disasters[0].event_id == active_event.event_id
    
    @pytest.mark.unit
    def test_create_failover_config(self, recovery_manager):
        """Test creating failover configuration"""
        config = recovery_manager.create_failover_config(
            service_name="test_service",
            primary_endpoint="https://primary.example.com",
            failover_endpoint="https://failover.example.com",
            health_check_path="/health",
            failover_threshold=3,
            recovery_threshold=2
        )
        
        assert config is not None
        assert config.service_name == "test_service"
        assert config.primary_endpoint == "https://primary.example.com"
        assert config.failover_endpoint == "https://failover.example.com"
        assert config.health_check_path == "/health"
        assert config.failover_threshold == 3
        assert config.recovery_threshold == 2
    
    @pytest.mark.unit
    def test_check_service_health(self, recovery_manager):
        """Test checking service health"""
        config = recovery_manager.create_failover_config(
            service_name="test_service",
            primary_endpoint="https://primary.example.com",
            failover_endpoint="https://failover.example.com",
            health_check_path="/health"
        )
        
        # Mock HTTP request
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}
            mock_get.return_value = mock_response
            
            health_status = recovery_manager.check_service_health(config)
            
            assert health_status["primary_healthy"] is True
            assert health_status["failover_healthy"] is True
            assert health_status["current_endpoint"] == config.primary_endpoint
    
    @pytest.mark.unit
    def test_check_service_health_primary_failure(self, recovery_manager):
        """Test checking service health with primary failure"""
        config = recovery_manager.create_failover_config(
            service_name="test_service",
            primary_endpoint="https://primary.example.com",
            failover_endpoint="https://failover.example.com",
            health_check_path="/health"
        )
        
        # Mock HTTP request - primary fails, failover works
        with patch('requests.get') as mock_get:
            def side_effect(url, **kwargs):
                response = Mock()
                if "primary" in url:
                    response.status_code = 500
                else:
                    response.status_code = 200
                    response.json.return_value = {"status": "healthy"}
                return response
            
            mock_get.side_effect = side_effect
            
            health_status = recovery_manager.check_service_health(config)
            
            assert health_status["primary_healthy"] is False
            assert health_status["failover_healthy"] is True
            assert health_status["current_endpoint"] == config.primary_endpoint  # Still primary until failover
    
    @pytest.mark.unit
    def test_execute_failover(self, recovery_manager):
        """Test executing failover"""
        config = recovery_manager.create_failover_config(
            service_name="test_service",
            primary_endpoint="https://primary.example.com",
            failover_endpoint="https://failover.example.com"
        )
        
        # Mock the failover execution
        with patch.object(recovery_manager, '_execute_failover') as mock_failover:
            mock_failover.return_value = True
            
            result = recovery_manager.execute_failover(config.config_id)
            
            assert result is True
            mock_failover.assert_called_once_with(config)
    
    @pytest.mark.unit
    def test_get_recovery_statistics(self, recovery_manager, sample_recovery_plan):
        """Test getting recovery statistics"""
        recovery_manager.create_recovery_plan(sample_recovery_plan)
        
        # Create some test events
        event1 = recovery_manager.declare_disaster(
            disaster_type=DisasterType.DATA_CORRUPTION,
            severity="high",
            description="Event 1"
        )
        
        event2 = recovery_manager.declare_disaster(
            disaster_type=DisasterType.NETWORK_OUTAGE,
            severity="medium",
            description="Event 2"
        )
        
        # Mark one as resolved
        event2.status = "resolved"
        event2.resolved_at = datetime.now()
        
        stats = recovery_manager.get_recovery_statistics()
        
        assert stats["total_events"] == 2
        assert stats["active_events"] == 1
        assert stats["resolved_events"] == 1
        assert stats["total_recovery_plans"] == 1
        assert "data_corruption" in stats["events_by_type"]
        assert "network_outage" in stats["events_by_type"]
    
    @pytest.mark.unit
    def test_backup_integration(self, recovery_manager):
        """Test backup system integration"""
        with patch('src.security.backup_system.backup_manager') as mock_backup:
            mock_backup.create_backup.return_value = {
                "backup_id": "backup_123",
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            
            result = recovery_manager.create_emergency_backup(
                description="Emergency backup for disaster recovery"
            )
            
            assert result["status"] == "success"
            assert result["backup_id"] == "backup_123"
            mock_backup.create_backup.assert_called_once()
    
    @pytest.mark.unit
    def test_encryption_integration(self, recovery_manager):
        """Test encryption system integration"""
        with patch('src.security.encryption.encryption_manager') as mock_encryption:
            mock_encryption.encrypt_data.return_value = "encrypted_data"
            mock_encryption.decrypt_data.return_value = "decrypted_data"
            
            # Test encrypting sensitive data
            sensitive_data = {"key": "value", "secret": "password"}
            encrypted = recovery_manager.encrypt_sensitive_data(sensitive_data)
            
            assert encrypted == "encrypted_data"
            mock_encryption.encrypt_data.assert_called_once_with(sensitive_data)
            
            # Test decrypting sensitive data
            decrypted = recovery_manager.decrypt_sensitive_data(encrypted)
            
            assert decrypted == "decrypted_data"
            mock_encryption.decrypt_data.assert_called_once_with(encrypted)


class TestFailoverConfig:
    """Unit tests for FailoverConfig"""
    
    @pytest.mark.unit
    def test_failover_config_creation(self):
        """Test creating failover configuration"""
        config = FailoverConfig(
            config_id="test_config",
            service_name="test_service",
            primary_endpoint="https://primary.example.com",
            failover_endpoint="https://failover.example.com",
            health_check_path="/health",
            failover_threshold=3,
            recovery_threshold=2
        )
        
        assert config.config_id == "test_config"
        assert config.service_name == "test_service"
        assert config.primary_endpoint == "https://primary.example.com"
        assert config.failover_endpoint == "https://failover.example.com"
        assert config.health_check_path == "/health"
        assert config.failover_threshold == 3
        assert config.recovery_threshold == 2
        assert config.is_active is True
        assert config.current_endpoint == config.primary_endpoint
    
    @pytest.mark.unit
    def test_failover_config_to_dict(self):
        """Test converting failover config to dictionary"""
        config = FailoverConfig(
            config_id="test_config",
            service_name="test_service",
            primary_endpoint="https://primary.example.com",
            failover_endpoint="https://failover.example.com"
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["config_id"] == "test_config"
        assert config_dict["service_name"] == "test_service"
        assert config_dict["primary_endpoint"] == "https://primary.example.com"
        assert config_dict["failover_endpoint"] == "https://failover.example.com"


class TestDisasterEvent:
    """Unit tests for DisasterEvent"""
    
    @pytest.mark.unit
    def test_disaster_event_creation(self):
        """Test creating disaster event"""
        event = DisasterEvent(
            event_id="test_event",
            disaster_type=DisasterType.DATA_CORRUPTION,
            severity="high",
            description="Test disaster",
            recovery_plan_id="test_plan"
        )
        
        assert event.event_id == "test_event"
        assert event.disaster_type == DisasterType.DATA_CORRUPTION
        assert event.severity == "high"
        assert event.description == "Test disaster"
        assert event.recovery_plan_id == "test_plan"
        assert event.status == "declared"
        assert event.impact_assessment == {}
    
    @pytest.mark.unit
    def test_disaster_event_to_dict(self):
        """Test converting disaster event to dictionary"""
        event = DisasterEvent(
            event_id="test_event",
            disaster_type=DisasterType.DATA_CORRUPTION,
            severity="high",
            description="Test disaster"
        )
        
        event_dict = event.to_dict()
        
        assert event_dict["event_id"] == "test_event"
        assert event_dict["disaster_type"] == "data_corruption"
        assert event_dict["severity"] == "high"
        assert event_dict["description"] == "Test disaster"
        assert event_dict["status"] == "declared"


class TestRecoveryPlan:
    """Unit tests for RecoveryPlan"""
    
    @pytest.mark.unit
    def test_recovery_plan_creation(self):
        """Test creating recovery plan"""
        plan = RecoveryPlan(
            plan_id="test_plan",
            disaster_type=DisasterType.DATA_CORRUPTION,
            severity="high",
            title="Test Plan",
            description="Test description",
            steps=[{"step": 1, "action": "Test step", "timeout": 300}],
            rollback_procedures=[{"step": 1, "action": "Rollback", "timeout": 60}],
            dependencies=["database"],
            estimated_recovery_time=300,
            success_criteria=["test_criteria"]
        )
        
        assert plan.plan_id == "test_plan"
        assert plan.disaster_type == DisasterType.DATA_CORRUPTION
        assert plan.severity == "high"
        assert plan.title == "Test Plan"
        assert plan.description == "Test description"
        assert len(plan.steps) == 1
        assert len(plan.rollback_procedures) == 1
        assert plan.dependencies == ["database"]
        assert plan.estimated_recovery_time == 300
        assert plan.success_criteria == ["test_criteria"]
    
    @pytest.mark.unit
    def test_recovery_plan_to_dict(self):
        """Test converting recovery plan to dictionary"""
        plan = RecoveryPlan(
            plan_id="test_plan",
            disaster_type=DisasterType.DATA_CORRUPTION,
            severity="high",
            title="Test Plan",
            description="Test description",
            steps=[{"step": 1, "action": "Test step", "timeout": 300}],
            rollback_procedures=[],
            dependencies=[],
            estimated_recovery_time=300,
            success_criteria=[]
        )
        
        plan_dict = plan.to_dict()
        
        assert plan_dict["plan_id"] == "test_plan"
        assert plan_dict["disaster_type"] == "data_corruption"
        assert plan_dict["severity"] == "high"
        assert plan_dict["title"] == "Test Plan"
        assert plan_dict["description"] == "Test description"


if __name__ == '__main__':
    pytest.main([__file__])
