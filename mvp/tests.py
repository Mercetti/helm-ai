#!/usr/bin/env python3
"""
Helm AI - Comprehensive Test Suite
Production-ready testing for anti-cheat detection system
"""

import pytest
import torch
import numpy as np
from PIL import Image
import io
import base64
import json
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from models import VisionDetector, AudioDetector, NetworkDetector, MultiModalFusion, ModelEnsemble
from database import DatabaseManager, DetectionResult, RiskLevel, UserProfile
from api_server import app, get_detection_result, save_detection_result
from config import HelmAIConfig

class TestModels:
    """Test suite for AI models"""
    
    @pytest.fixture
    def vision_model(self):
        """Create vision model for testing"""
        return VisionDetector(num_classes=3)
    
    @pytest.fixture
    def audio_model(self):
        """Create audio model for testing"""
        return AudioDetector(num_classes=3)
    
    @pytest.fixture
    def network_model(self):
        """Create network model for testing"""
        return NetworkDetector(num_classes=3)
    
    @pytest.fixture
    def multimodal_model(self):
        """Create multi-modal model for testing"""
        return MultiModalFusion()
    
    @pytest.fixture
    def model_ensemble(self):
        """Create model ensemble for testing"""
        return ModelEnsemble()
    
    @pytest.fixture
    def sample_image(self):
        """Create sample image for testing"""
        # Create a simple test image
        image = Image.new('RGB', (224, 224), color='red')
        return image
    
    @pytest.fixture
    def sample_audio(self):
        """Create sample audio for testing"""
        # Generate dummy audio data
        return np.random.randn(16000)  # 1 second at 16kHz
    
    @pytest.fixture
    def sample_network(self):
        """Create sample network data for testing"""
        return np.random.randn(100, 10)  # 100 time steps, 10 features
    
    def test_vision_model_initialization(self, vision_model):
        """Test vision model initialization"""
        assert vision_model is not None
        assert hasattr(vision_model, 'backbone')
        assert hasattr(vision_model, 'aim_detector')
        assert hasattr(vision_model, 'esp_detector')
        assert hasattr(vision_model, 'overlay_detector')
    
    def test_audio_model_initialization(self, audio_model):
        """Test audio model initialization"""
        assert audio_model is not None
        assert hasattr(audio_model, 'conv1d_layers')
        assert hasattr(audio_model, 'classifier')
        assert hasattr(audio_model, 'voice_stress_detector')
    
    def test_network_model_initialization(self, network_model):
        """Test network model initialization"""
        assert network_model is not None
        assert hasattr(network_model, 'feature_extractor')
        assert hasattr(network_model, 'lstm')
        assert hasattr(network_model, 'classifier')
    
    def test_multimodal_model_initialization(self, multimodal_model):
        """Test multi-modal model initialization"""
        assert multimodal_model is not None
        assert hasattr(multimodal_model, 'vision_fc')
        assert hasattr(multimodal_model, 'audio_fc')
        assert hasattr(multimodal_model, 'network_fc')
        assert hasattr(multimodal_model, 'attention')
    
    def test_vision_model_forward(self, vision_model, sample_image):
        """Test vision model forward pass"""
        import torchvision.transforms as transforms
        
        # Preprocess image
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        image_tensor = transform(sample_image).unsqueeze(0)
        
        # Forward pass
        with torch.no_grad():
            result = vision_model(image_tensor)
        
        # Check output structure
        assert isinstance(result, dict)
        assert 'classification' in result
        assert 'aim_detection' in result
        assert 'esp_detection' in result
        assert 'overlay_detection' in result
        
        # Check output shapes
        assert result['classification'].shape[0] == 1  # batch size
        assert result['classification'].shape[1] == 3  # num classes
    
    def test_audio_model_forward(self, audio_model, sample_audio):
        """Test audio model forward pass"""
        # Convert to tensor
        audio_tensor = torch.FloatTensor(sample_audio).unsqueeze(0).unsqueeze(0)
        
        # Forward pass
        with torch.no_grad():
            result = audio_model(audio_tensor)
        
        # Check output structure
        assert isinstance(result, dict)
        assert 'classification' in result
        assert 'voice_stress' in result
        assert 'background_noise' in result
        assert 'suspicious_patterns' in result
    
    def test_network_model_forward(self, network_model, sample_network):
        """Test network model forward pass"""
        # Convert to tensor
        network_tensor = torch.FloatTensor(sample_network).unsqueeze(0)
        
        # Forward pass
        with torch.no_grad():
            result = network_model(network_tensor)
        
        # Check output structure
        assert isinstance(result, dict)
        assert 'classification' in result
        assert 'packet_anomalies' in result
        assert 'timing_irregularities' in result
        assert 'suspicious_connections' in result
    
    def test_model_ensemble_prediction(self, model_ensemble, sample_image, sample_audio, sample_network):
        """Test model ensemble prediction"""
        # Preprocess inputs
        import torchvision.transforms as transforms
        
        image_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        image_tensor = image_transform(sample_image).unsqueeze(0)
        audio_tensor = torch.FloatTensor(sample_audio).unsqueeze(0).unsqueeze(0)
        network_tensor = torch.FloatTensor(sample_network).unsqueeze(0)
        
        # Move to device
        device = model_ensemble.device
        image_tensor = image_tensor.to(device)
        audio_tensor = audio_tensor.to(device)
        network_tensor = network_tensor.to(device)
        
        # Prediction
        with torch.no_grad():
            result = model_ensemble.predict(image_tensor, audio_tensor, network_tensor)
        
        # Check result
        assert isinstance(result, dict)
        assert 'vision' in result
        assert 'audio' in result
        assert 'network' in result
        assert 'fusion' in result
    
    def test_risk_level_classification(self, model_ensemble):
        """Test risk level classification"""
        # Create dummy prediction
        dummy_prediction = {
            'fusion': {
                'classification': torch.tensor([[0.1, 0.3, 0.6]])
            }
        }
        
        risk_level, confidence = model_ensemble.get_risk_level(dummy_prediction)
        
        assert risk_level in ["Safe", "Suspicious", "Cheating Detected"]
        assert 0 <= confidence <= 1

class TestDatabase:
    """Test suite for database operations"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        os.unlink(db_path)
    
    @pytest.fixture
    def db_manager(self, temp_db):
        """Create database manager for testing"""
        return DatabaseManager(temp_db)
    
    @pytest.fixture
    def sample_detection_result(self):
        """Create sample detection result"""
        return DetectionResult(
            request_id="test_123",
            user_id="user_456",
            game_id="game_789",
            session_id="session_101",
            risk_level=RiskLevel.SUSPICIOUS,
            confidence=0.75,
            processing_time_ms=85.5,
            modalities_used=["vision", "audio"],
            details={"test": "data"},
            timestamp=datetime.now()
        )
    
    def test_database_initialization(self, db_manager):
        """Test database initialization"""
        assert db_manager is not None
        assert db_manager.db_path is not None
    
    def test_save_detection_result(self, db_manager, sample_detection_result):
        """Test saving detection result"""
        success = db_manager.save_detection_result(sample_detection_result)
        assert success is True
    
    def test_get_detection_result(self, db_manager, sample_detection_result):
        """Test retrieving detection result"""
        # Save first
        db_manager.save_detection_result(sample_detection_result)
        
        # Retrieve
        retrieved = db_manager.get_detection_result(sample_detection_result.request_id)
        
        assert retrieved is not None
        assert retrieved.request_id == sample_detection_result.request_id
        assert retrieved.user_id == sample_detection_result.user_id
        assert retrieved.risk_level == sample_detection_result.risk_level
        assert retrieved.confidence == sample_detection_result.confidence
    
    def test_get_user_profile(self, db_manager, sample_detection_result):
        """Test getting user profile"""
        # Save detection result first
        db_manager.save_detection_result(sample_detection_result)
        
        # Get user profile
        profile = db_manager.get_user_profile(sample_detection_result.user_id)
        
        assert profile is not None
        assert profile.user_id == sample_detection_result.user_id
        assert profile.total_detections >= 1
    
    def test_get_user_detections(self, db_manager, sample_detection_result):
        """Test getting user detections"""
        # Save detection result first
        db_manager.save_detection_result(sample_detection_result)
        
        # Get user detections
        detections = db_manager.get_user_detections(sample_detection_result.user_id)
        
        assert len(detections) >= 1
        assert detections[0].user_id == sample_detection_result.user_id
    
    def test_get_game_statistics(self, db_manager, sample_detection_result):
        """Test getting game statistics"""
        # Save detection result first
        db_manager.save_detection_result(sample_detection_result)
        
        # Get game statistics
        stats = db_manager.get_game_statistics(sample_detection_result.game_id)
        
        assert isinstance(stats, dict)
        assert 'total_detections' in stats
        assert 'risk_distribution' in stats
        assert 'unique_users' in stats

class TestAPI:
    """Test suite for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_detect_endpoint_missing_data(self, client):
        """Test detect endpoint with missing data"""
        response = client.post("/api/v1/detect", json={})
        assert response.status_code == 422  # Validation error
    
    def test_detect_endpoint_invalid_base64(self, client):
        """Test detect endpoint with invalid base64"""
        invalid_data = {
            "user_id": "test_user",
            "game_id": "test_game",
            "image_data": "invalid_base64_data"
        }
        
        response = client.post("/api/v1/detect", json=invalid_data)
        assert response.status_code == 400  # Bad request

class TestConfiguration:
    """Test suite for configuration management"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = HelmAIConfig()
        
        assert config.environment == "development"
        assert config.api.host == "0.0.0.0"
        assert config.api.port == 8000
        assert config.model.device in ["cpu", "cuda"]
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = HelmAIConfig()
        is_valid = config.validate()
        assert is_valid is True
    
    def test_config_to_dict(self):
        """Test configuration to dictionary conversion"""
        config = HelmAIConfig()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "environment" in config_dict
        assert "database" in config_dict
        assert "api" in config_dict
        assert "model" in config_dict

class TestIntegration:
    """Integration tests"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        os.unlink(db_path)
    
    def test_end_to_end_detection(self, temp_db):
        """Test end-to-end detection pipeline"""
        # Setup database
        db_manager = DatabaseManager(temp_db)
        
        # Create model ensemble
        model_ensemble = ModelEnsemble()
        
        # Create sample data
        image = Image.new('RGB', (224, 224), color='blue')
        audio = np.random.randn(16000)
        network = np.random.randn(100, 10)
        
        # Preprocess data
        import torchvision.transforms as transforms
        
        image_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        image_tensor = image_transform(image).unsqueeze(0)
        audio_tensor = torch.FloatTensor(audio).unsqueeze(0).unsqueeze(0)
        network_tensor = torch.FloatTensor(network).unsqueeze(0)
        
        # Make prediction
        with torch.no_grad():
            result = model_ensemble.predict(image_tensor, audio_tensor, network_tensor)
        
        # Get risk level
        risk_level, confidence = model_ensemble.get_risk_level(result)
        
        # Create detection result
        detection_result = DetectionResult(
            request_id="integration_test",
            user_id="test_user",
            game_id="test_game",
            session_id="test_session",
            risk_level=RiskLevel(risk_level),
            confidence=confidence,
            processing_time_ms=100.0,
            modalities_used=["vision", "audio", "network"],
            details=result,
            timestamp=datetime.now()
        )
        
        # Save to database
        success = db_manager.save_detection_result(detection_result)
        assert success is True
        
        # Retrieve from database
        retrieved = db_manager.get_detection_result("integration_test")
        assert retrieved is not None
        assert retrieved.risk_level == detection_result.risk_level
        assert retrieved.confidence == detection_result.confidence

# Performance tests
class TestPerformance:
    """Performance tests"""
    
    def test_model_inference_speed(self):
        """Test model inference speed"""
        model = VisionDetector()
        model.eval()
        
        # Create sample input
        input_tensor = torch.randn(1, 3, 224, 224)
        
        # Measure inference time
        import time
        start_time = time.time()
        
        with torch.no_grad():
            for _ in range(100):
                result = model(input_tensor)
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 100
        
        # Should be under 100ms per inference
        assert avg_time < 0.1, f"Average inference time: {avg_time:.3f}s"
    
    def test_database_performance(self):
        """Test database performance"""
        db_manager = DatabaseManager(":memory:")  # In-memory database
        
        # Create sample data
        detection_result = DetectionResult(
            request_id="perf_test",
            user_id="perf_user",
            game_id="perf_game",
            session_id="perf_session",
            risk_level=RiskLevel.SAFE,
            confidence=0.95,
            processing_time_ms=50.0,
            modalities_used=["vision"],
            details={},
            timestamp=datetime.now()
        )
        
        # Measure insert performance
        import time
        start_time = time.time()
        
        for i in range(1000):
            detection_result.request_id = f"perf_test_{i}"
            db_manager.save_detection_result(detection_result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle 1000 inserts in under 5 seconds
        assert total_time < 5.0, f"Total time for 1000 inserts: {total_time:.3f}s"

# Test utilities
def create_test_image(width=224, height=224, color='red'):
    """Create test image for testing"""
    return Image.new('RGB', (width, height), color=color)

def create_test_audio(duration=1.0, sample_rate=16000):
    """Create test audio for testing"""
    samples = int(duration * sample_rate)
    return np.random.randn(samples)

def create_test_network_data(sequence_length=100, features=10):
    """Create test network data for testing"""
    return np.random.randn(sequence_length, features)

# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addoption("--runslow", action="store_true", default=False, help="run slow tests")
    config.addoption("--skipintegration", action="store_true", default=False, help="skip integration tests")

# Custom markers
pytest.mark.slow = pytest.mark.slow
pytest.mark.integration = pytest.mark.integration

if __name__ == "__main__":
    # Run tests
    print("Running Helm AI Test Suite...")
    
    # Run specific test classes
    pytest.main([__file__, "-v", "--tb=short"])
