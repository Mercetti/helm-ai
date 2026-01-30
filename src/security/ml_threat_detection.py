"""
Helm AI ML-Based Advanced Threat Detection System
Implements machine learning models for sophisticated threat detection and analysis
"""

import os
import sys
import json
import time
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import threading
import logging
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from security.encryption import EncryptionManager

class ThreatType(Enum):
    """Threat type enumeration"""
    MALWARE = "malware"
    PHISHING = "phishing"
    DDOS = "ddos"
    INJECTION = "injection"
    BRUTE_FORCE = "brute_force"
    DATA_EXFILTRATION = "data_exfiltration"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    INSIDER_THREAT = "insider_threat"
    ADVANCED_PERSISTENT_THREAT = "apt"
    ZERO_DAY = "zero_day"

class ThreatSeverity(Enum):
    """Threat severity enumeration"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class DetectionModel(Enum):
    """Detection model type enumeration"""
    ISOLATION_FOREST = "isolation_forest"
    RANDOM_FOREST = "random_forest"
    NEURAL_NETWORK = "neural_network"
    LSTM = "lstm"
    AUTOENCODER = "autoencoder"
    ENSEMBLE = "ensemble"

@dataclass
class ThreatEvent:
    """Threat event data structure"""
    event_id: str
    timestamp: datetime
    threat_type: ThreatType
    severity: ThreatSeverity
    confidence: float
    source_ip: str
    target_resource: str
    user_id: Optional[str]
    session_id: Optional[str]
    features: Dict[str, Any] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    mitigation_actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert threat event to dictionary"""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'threat_type': self.threat_type.value,
            'severity': self.severity.value,
            'confidence': self.confidence,
            'source_ip': self.source_ip,
            'target_resource': self.target_resource,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'features': self.features,
            'raw_data': self.raw_data,
            'context': self.context,
            'mitigation_actions': self.mitigation_actions
        }

@dataclass
class FeatureVector:
    """Feature vector for ML models"""
    user_id: str
    session_id: str
    timestamp: datetime
    features: Dict[str, float]
    labels: Optional[int] = None
    anomaly_score: Optional[float] = None
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array"""
        return np.array(list(self.features.values()))
    
    def get_feature_names(self) -> List[str]:
        """Get feature names"""
        return list(self.features.keys())

class ThreatDetectionModel:
    """Base class for threat detection models"""
    
    def __init__(self, model_type: DetectionModel, name: str):
        self.model_type = model_type
        self.name = name
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
        self.training_history = []
        
    def train(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> None:
        """Train the model"""
        raise NotImplementedError
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        raise NotImplementedError
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get prediction probabilities"""
        raise NotImplementedError
    
    def save_model(self, filepath: str) -> None:
        """Save trained model"""
        if self.model is not None:
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'is_trained': self.is_trained,
                'training_history': self.training_history
            }, filepath)
    
    def load_model(self, filepath: str) -> None:
        """Load trained model"""
        data = joblib.load(filepath)
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        self.is_trained = data['is_trained']
        self.training_history = data['training_history']

class IsolationForestModel(ThreatDetectionModel):
    """Isolation Forest based anomaly detection model"""
    
    def __init__(self, name: str = "isolation_forest"):
        super().__init__(DetectionModel.ISOLATION_FOREST, name)
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.1,
            random_state=42,
            n_jobs=-1
        )
    
    def train(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> None:
        """Train isolation forest model"""
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled)
        self.is_trained = True
        
        # Store training history
        self.training_history.append({
            'timestamp': datetime.utcnow(),
            'samples': len(X),
            'features': X.shape[1],
            'model_type': self.model_type.value
        })
        
        logger.info(f"Isolation Forest model trained with {len(X)} samples")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict anomalies (-1 for anomaly, 1 for normal)"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get anomaly scores"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X_scaled = self.scaler.transform(X)
        scores = self.model.decision_function(X_scaled)
        
        # Convert to probabilities (higher = more anomalous)
        probabilities = (scores - scores.min()) / (scores.max() - scores.min())
        return probabilities

class RandomForestModel(ThreatDetectionModel):
    """Random Forest based classification model"""
    
    def __init__(self, name: str = "random_forest"):
        super().__init__(DetectionModel.RANDOM_FOREST, name)
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train random forest model"""
        if y is None:
            raise ValueError("Random Forest requires labeled data")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Store training history
        self.training_history.append({
            'timestamp': datetime.utcnow(),
            'samples': len(X),
            'features': X.shape[1],
            'model_type': self.model_type.value,
            'accuracy': self.model.score(X_scaled, y)
        })
        
        logger.info(f"Random Forest model trained with {len(X)} samples")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict threat classes"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get prediction probabilities"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)

class EnsembleModel(ThreatDetectionModel):
    """Ensemble model combining multiple detection models"""
    
    def __init__(self, name: str = "ensemble"):
        super().__init__(DetectionModel.ENSEMBLE, name)
        self.models = {}
        self.weights = {}
        
    def add_model(self, model: ThreatDetectionModel, weight: float = 1.0) -> None:
        """Add model to ensemble"""
        self.models[model.name] = model
        self.weights[model.name] = weight
    
    def train(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> None:
        """Train all models in ensemble"""
        for model in self.models.values():
            model.train(X, y)
        
        self.is_trained = True
        logger.info(f"Ensemble model trained with {len(self.models)} sub-models")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make ensemble predictions"""
        if not self.is_trained:
            raise ValueError("Models must be trained before making predictions")
        
        predictions = {}
        for name, model in self.models.items():
            predictions[name] = model.predict(X)
        
        # Weighted voting for classification
        if len(predictions) > 0:
            ensemble_pred = np.zeros(len(X))
            for name, pred in predictions.items():
                ensemble_pred += pred * self.weights[name]
            
            # Normalize
            ensemble_pred = ensemble_pred / sum(self.weights.values())
            return ensemble_pred.astype(int)
        
        return np.zeros(len(X))
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get ensemble probabilities"""
        if not self.is_trained:
            raise ValueError("Models must be trained before making predictions")
        
        probabilities = {}
        for name, model in self.models.values():
            probabilities[name] = model.predict_proba(X)
        
        # Weighted averaging
        if len(probabilities) > 0:
            ensemble_prob = np.zeros_like(list(probabilities.values())[0])
            for name, prob in probabilities.items():
                ensemble_prob += prob * self.weights[name]
            
            # Normalize
            ensemble_prob = ensemble_prob / sum(self.weights.values())
            return ensemble_prob
        
        return np.zeros((len(X), 2))

class FeatureExtractor:
    """Feature extraction for threat detection"""
    
    def __init__(self):
        self.feature_extractors = {
            'network': self._extract_network_features,
            'user_behavior': self._extract_user_behavior_features,
            'system': self._extract_system_features,
            'temporal': self._extract_temporal_features,
            'content': self._extract_content_features
        }
    
    def extract_features(self, event_data: Dict[str, Any]) -> FeatureVector:
        """Extract features from event data"""
        features = {}
        
        # Extract features from different domains
        for domain, extractor in self.feature_extractors.items():
            try:
                domain_features = extractor(event_data)
                features.update(domain_features)
            except Exception as e:
                logger.warning(f"Feature extraction failed for {domain}: {e}")
        
        return FeatureVector(
            user_id=event_data.get('user_id', ''),
            session_id=event_data.get('session_id', ''),
            timestamp=datetime.fromisoformat(event_data.get('timestamp', datetime.utcnow().isoformat())),
            features=features
        )
    
    def _extract_network_features(self, event_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract network-related features"""
        features = {}
        
        # IP-based features
        ip_address = event_data.get('source_ip', '')
        if ip_address:
            features['ip_octet_sum'] = sum(int(octet) for octet in ip_address.split('.'))
            features['ip_is_private'] = float(self._is_private_ip(ip_address))
            features['ip_is_datacenter'] = float(self._is_datacenter_ip(ip_address))
        
        # Request-based features
        features['request_size'] = float(len(str(event_data.get('request_body', ''))))
        features['response_size'] = float(len(str(event_data.get('response_body', ''))))
        features['request_duration'] = float(event_data.get('duration', 0))
        
        # Protocol features
        method = event_data.get('method', '').upper()
        features['method_get'] = float(method == 'GET')
        features['method_post'] = float(method == 'POST')
        features['method_put'] = float(method == 'PUT')
        features['method_delete'] = float(method == 'DELETE')
        
        return features
    
    def _extract_user_behavior_features(self, event_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract user behavior features"""
        features = {}
        
        # Time-based features
        timestamp = datetime.fromisoformat(event_data.get('timestamp', datetime.utcnow().isoformat()))
        features['hour_of_day'] = float(timestamp.hour)
        features['day_of_week'] = float(timestamp.weekday())
        features['is_weekend'] = float(timestamp.weekday() >= 5)
        features['is_business_hours'] = float(9 <= timestamp.hour <= 17)
        
        # User session features
        features['session_age_minutes'] = float(event_data.get('session_age', 0))
        features['requests_per_session'] = float(event_data.get('session_requests', 0))
        features['unique_endpoints'] = float(len(event_data.get('endpoints', [])))
        
        # Geographic features
        location = event_data.get('location', {})
        features['geo_risk_score'] = float(location.get('risk_score', 0))
        features['is_known_location'] = float(location.get('known', False))
        
        return features
    
    def _extract_system_features(self, event_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract system-related features"""
        features = {}
        
        # Device features
        device = event_data.get('device', {})
        features['device_trust_score'] = float(device.get('trust_score', 0))
        features['device_is_mobile'] = float(device.get('is_mobile', False))
        features['device_is_new'] = float(not device.get('known', True))
        
        # Authentication features
        auth = event_data.get('auth', {})
        features['auth_mfa_used'] = float(auth.get('mfa_used', False))
        features['auth_failed_attempts'] = float(auth.get('failed_attempts', 0))
        features['auth_password_strength'] = float(auth.get('password_strength', 0))
        
        # System load features
        system = event_data.get('system', {})
        features['cpu_usage'] = float(system.get('cpu_usage', 0))
        features['memory_usage'] = float(system.get('memory_usage', 0))
        features['disk_usage'] = float(system.get('disk_usage', 0))
        
        return features
    
    def _extract_temporal_features(self, event_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract temporal features"""
        features = {}
        
        timestamp = datetime.fromisoformat(event_data.get('timestamp', datetime.utcnow().isoformat()))
        
        # Time patterns
        features['minute_of_hour'] = float(timestamp.minute)
        features['second_of_minute'] = float(timestamp.second)
        features['day_of_month'] = float(timestamp.day)
        features['month_of_year'] = float(timestamp.month)
        
        # Periodic patterns
        features['is_quarter_end'] = float(timestamp.month in [3, 6, 9, 12] and timestamp.day >= 28)
        features['is_month_end'] = float(timestamp.day >= 28)
        features['is_year_end'] = float(timestamp.month == 12 and timestamp.day >= 30)
        
        return features
    
    def _extract_content_features(self, event_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract content-based features"""
        features = {}
        
        # URL features
        url = event_data.get('url', '')
        features['url_length'] = float(len(url))
        features['url_params_count'] = float(url.count('?') + url.count('&'))
        features['url_path_depth'] = float(url.count('/'))
        
        # Content features
        content = str(event_data.get('content', ''))
        features['content_length'] = float(len(content))
        features['content_entropy'] = float(self._calculate_entropy(content))
        features['content_has_sql'] = float(self._contains_sql_injection(content))
        features['content_has_xss'] = float(self._contains_xss(content))
        features['content_has_cmd'] = float(self._contains_command_injection(content))
        
        return features
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private"""
        try:
            import ipaddress
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except:
            return False
    
    def _is_datacenter_ip(self, ip: str) -> bool:
        """Check if IP is from data center"""
        # Simplified check - in production, use proper IP ranges
        datacenter_ranges = ['8.8.8.8', '1.1.1.1', '208.67.222.222']
        return ip in datacenter_ranges
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        if not text:
            return 0.0
        
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        entropy = 0.0
        text_len = len(text)
        
        for count in char_counts.values():
            probability = count / text_len
            entropy -= probability * np.log2(probability)
        
        return entropy
    
    def _contains_sql_injection(self, content: str) -> bool:
        """Check for SQL injection patterns"""
        sql_patterns = [
            'union select', 'drop table', 'insert into', 'delete from',
            'exec(', 'xp_cmdshell', 'sp_executesql', 'waitfor delay'
        ]
        content_lower = content.lower()
        return any(pattern in content_lower for pattern in sql_patterns)
    
    def _contains_xss(self, content: str) -> bool:
        """Check for XSS patterns"""
        xss_patterns = [
            '<script>', 'javascript:', 'onerror=', 'onload=',
            'eval(', 'alert(', 'document.cookie', 'window.location'
        ]
        content_lower = content.lower()
        return any(pattern in content_lower for pattern in xss_patterns)
    
    def _contains_command_injection(self, content: str) -> bool:
        """Check for command injection patterns"""
        cmd_patterns = [
            ';cat ', ';ls ', ';pwd', ';whoami', '&&', '||',
            '`', '$(', '${', 'exec(', 'system('
        ]
        return any(pattern in content for pattern in cmd_patterns)

class MLThreatDetector:
    """Machine Learning based threat detection system"""
    
    def __init__(self, encryption_manager: Optional[EncryptionManager] = None):
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.models: Dict[str, ThreatDetectionModel] = {}
        self.feature_extractor = FeatureExtractor()
        self.threat_history = deque(maxlen=10000)
        self.model_registry = ModelRegistry()
        self.training_data = []
        self.lock = threading.Lock()
        
        # Configuration
        self.model_dir = os.getenv('ML_MODELS_DIR', 'models/threat_detection')
        self.retrain_interval = int(os.getenv('ML_RETRAIN_INTERVAL', '86400'))  # 24 hours
        self.min_training_samples = int(os.getenv('ML_MIN_TRAINING_SAMPLES', '1000'))
        self.anomaly_threshold = float(os.getenv('ML_ANOMALY_THRESHOLD', '0.7'))
        
        # Ensure model directory exists
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Initialize default models
        self._initialize_models()
    
    def _initialize_models(self) -> None:
        """Initialize default detection models"""
        # Isolation Forest for anomaly detection
        iso_model = IsolationForestModel("anomaly_detector")
        self.models["anomaly_detector"] = iso_model
        
        # Random Forest for classification
        rf_model = RandomForestModel("threat_classifier")
        self.models["threat_classifier"] = rf_model
        
        # Ensemble model
        ensemble = EnsembleModel("ensemble_detector")
        ensemble.add_model(iso_model, weight=0.6)
        ensemble.add_model(rf_model, weight=0.4)
        self.models["ensemble"] = ensemble
        
        # Try to load existing models
        self._load_models()
    
    def detect_threat(self, event_data: Dict[str, Any]) -> ThreatEvent:
        """Detect threats in event data"""
        try:
            # Extract features
            feature_vector = self.feature_extractor.extract_features(event_data)
            
            # Get predictions from all models
            predictions = {}
            confidences = {}
            
            for model_name, model in self.models.items():
                if model.is_trained:
                    try:
                        X = feature_vector.to_array().reshape(1, -1)
                        
                        if model.model_type == DetectionModel.ISOLATION_FOREST:
                            # Anomaly detection
                            anomaly_score = model.predict_proba(X)[0]
                            predictions[model_name] = -1 if anomaly_score > self.anomaly_threshold else 1
                            confidences[model_name] = anomaly_score
                        else:
                            # Classification
                            pred = model.predict(X)[0]
                            proba = model.predict_proba(X)[0]
                            predictions[model_name] = pred
                            confidences[model_name] = max(proba)
                    except Exception as e:
                        logger.warning(f"Model {model_name} prediction failed: {e}")
                        continue
            
            # Determine final threat assessment
            threat_type, severity, confidence = self._assess_threat(predictions, confidences, event_data)
            
            # Create threat event
            threat_event = ThreatEvent(
                event_id=self._generate_event_id(),
                timestamp=datetime.utcnow(),
                threat_type=threat_type,
                severity=severity,
                confidence=confidence,
                source_ip=event_data.get('source_ip', ''),
                target_resource=event_data.get('resource', ''),
                user_id=event_data.get('user_id'),
                session_id=event_data.get('session_id'),
                features=feature_vector.features,
                raw_data=event_data,
                context=self._build_context(event_data, predictions),
                mitigation_actions=self._get_mitigation_actions(threat_type, severity)
            )
            
            # Store in history
            with self.lock:
                self.threat_history.append(threat_event)
            
            # Log detection
            self._log_threat_detection(threat_event)
            
            return threat_event
            
        except Exception as e:
            logger.error(f"Threat detection failed: {e}")
            # Return safe default
            return ThreatEvent(
                event_id=self._generate_event_id(),
                timestamp=datetime.utcnow(),
                threat_type=ThreatType.ANOMALOUS_BEHAVIOR,
                severity=ThreatSeverity.LOW,
                confidence=0.0,
                source_ip=event_data.get('source_ip', ''),
                target_resource=event_data.get('resource', ''),
                user_id=event_data.get('user_id'),
                session_id=event_data.get('session_id')
            )
    
    def _assess_threat(self, predictions: Dict[str, Any], confidences: Dict[str, float], event_data: Dict[str, Any]) -> Tuple[ThreatType, ThreatSeverity, float]:
        """Assess threat type, severity, and confidence"""
        # Default values
        threat_type = ThreatType.ANOMALOUS_BEHAVIOR
        severity = ThreatSeverity.LOW
        confidence = 0.0
        
        # Ensemble model takes precedence
        if "ensemble" in predictions:
            ensemble_pred = predictions["ensemble"]
            ensemble_conf = confidences["ensemble"]
            
            if ensemble_pred == -1 or ensemble_pred == 1:  # Threat detected
                confidence = ensemble_conf
                
                # Determine severity based on confidence
                if confidence > 0.9:
                    severity = ThreatSeverity.CRITICAL
                elif confidence > 0.7:
                    severity = ThreatSeverity.HIGH
                elif confidence > 0.5:
                    severity = ThreatSeverity.MEDIUM
                else:
                    severity = ThreatSeverity.LOW
                
                # Determine threat type based on event characteristics
                threat_type = self._classify_threat_type(event_data, confidence)
        
        return threat_type, severity, confidence
    
    def _classify_threat_type(self, event_data: Dict[str, Any], confidence: float) -> ThreatType:
        """Classify threat type based on event characteristics"""
        content = str(event_data.get('content', '')).lower()
        url = event_data.get('url', '').lower()
        user_agent = event_data.get('user_agent', '').lower()
        
        # Check for specific threat patterns
        if self._contains_sql_injection(content):
            return ThreatType.INJECTION
        elif self._contains_xss(content):
            return ThreatType.INJECTION
        elif 'bot' in user_agent or 'crawler' in user_agent:
            return ThreatType.DDOS
        elif 'phishing' in content or 'password' in content and 'login' in content:
            return ThreatType.PHISHING
        elif confidence > 0.8 and event_data.get('user_id'):
            return ThreatType.INSIDER_THREAT
        elif confidence > 0.9:
            return ThreatType.ADVANCED_PERSISTENT_THREAT
        else:
            return ThreatType.ANOMALOUS_BEHAVIOR
    
    def _build_context(self, event_data: Dict[str, Any], predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Build context information for threat event"""
        return {
            'model_predictions': predictions,
            'event_type': event_data.get('event_type', 'unknown'),
            'user_agent': event_data.get('user_agent', ''),
            'location': event_data.get('location', {}),
            'device': event_data.get('device', {}),
            'timestamp': event_data.get('timestamp', datetime.utcnow().isoformat())
        }
    
    def _get_mitigation_actions(self, threat_type: ThreatType, severity: ThreatSeverity) -> List[str]:
        """Get recommended mitigation actions"""
        actions = []
        
        # Base actions for all threats
        actions.append("log_event")
        actions.append("notify_security_team")
        
        # Severity-based actions
        if severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL]:
            actions.append("block_ip")
            actions.append("terminate_session")
            actions.append("require_mfa")
        
        # Threat-type specific actions
        if threat_type == ThreatType.DDOS:
            actions.append("rate_limit_ip")
            actions.append("enable_captcha")
        elif threat_type == ThreatType.INJECTION:
            actions.append("sanitize_input")
            actions.append("validate_parameters")
        elif threat_type == ThreatType.PHISHING:
            actions.append("block_url")
            actions.append("warn_user")
        elif threat_type == ThreatType.INSIDER_THREAT:
            actions.append("escalate_to_management")
            actions.append("audit_user_activity")
        
        return actions
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _load_models(self) -> None:
        """Load trained models from disk"""
        for model_name, model in self.models.items():
            model_path = os.path.join(self.model_dir, f"{model_name}.pkl")
            if os.path.exists(model_path):
                try:
                    model.load_model(model_path)
                    logger.info(f"Loaded model: {model_name}")
                except Exception as e:
                    logger.warning(f"Failed to load model {model_name}: {e}")
    
    def _save_models(self) -> None:
        """Save trained models to disk"""
        for model_name, model in self.models.items():
            if model.is_trained:
                model_path = os.path.join(self.model_dir, f"{model_name}.pkl")
                try:
                    model.save_model(model_path)
                    logger.info(f"Saved model: {model_name}")
                except Exception as e:
                    logger.warning(f"Failed to save model {model_name}: {e}")
    
    def _log_threat_detection(self, threat_event: ThreatEvent) -> None:
        """Log threat detection for audit"""
        log_data = {
            'event_id': threat_event.event_id,
            'timestamp': threat_event.timestamp.isoformat(),
            'threat_type': threat_event.threat_type.value,
            'severity': threat_event.severity.value,
            'confidence': threat_event.confidence,
            'source_ip': threat_event.source_ip,
            'user_id': threat_event.user_id,
            'mitigation_actions': threat_event.mitigation_actions
        }
        
        logger.warning(f"Threat detected: {json.dumps(log_data)}")
    
    def add_training_data(self, event_data: Dict[str, Any], label: Optional[int] = None) -> None:
        """Add training data for model retraining"""
        feature_vector = self.feature_extractor.extract_features(event_data)
        feature_vector.labels = label
        
        with self.lock:
            self.training_data.append(feature_vector)
            
            # Retrain if we have enough data
            if len(self.training_data) >= self.min_training_samples:
                self._retrain_models()
    
    def _retrain_models(self) -> None:
        """Retrain models with new data"""
        try:
            # Prepare training data
            X = np.array([fv.to_array() for fv in self.training_data])
            y = np.array([fv.labels for fv in self.training_data if fv.labels is not None])
            
            # Train models
            for model in self.models.values():
                if model.model_type == DetectionModel.ISOLATION_FOREST:
                    model.train(X)
                elif model.model_type == DetectionModel.RANDOM_FOREST and len(y) > 0:
                    model.train(X, y)
                elif model.model_type == DetectionModel.ENSEMBLE:
                    model.train(X, y if len(y) > 0 else None)
            
            # Save models
            self._save_models()
            
            # Clear training data
            self.training_data.clear()
            
            logger.info("Models retrained successfully")
            
        except Exception as e:
            logger.error(f"Model retraining failed: {e}")

class ModelRegistry:
    """Registry for managing ML models"""
    
    def __init__(self):
        self.registered_models = {}
        self.model_metadata = {}
    
    def register_model(self, model: ThreatDetectionModel, metadata: Dict[str, Any]) -> None:
        """Register a model"""
        self.registered_models[model.name] = model
        self.model_metadata[model.name] = metadata
    
    def get_model(self, name: str) -> Optional[ThreatDetectionModel]:
        """Get registered model"""
        return self.registered_models.get(name)
    
    def list_models(self) -> List[str]:
        """List all registered models"""
        return list(self.registered_models.keys())

# Global ML threat detector instance
ml_threat_detector = MLThreatDetector()

# Export main components
__all__ = [
    'MLThreatDetector',
    'ThreatEvent',
    'FeatureVector',
    'ThreatDetectionModel',
    'IsolationForestModel',
    'RandomForestModel',
    'EnsembleModel',
    'FeatureExtractor',
    'ModelRegistry',
    'ThreatType',
    'ThreatSeverity',
    'DetectionModel',
    'ml_threat_detector'
]
