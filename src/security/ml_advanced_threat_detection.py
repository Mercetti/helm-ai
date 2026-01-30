"""
ML-based Advanced Threat Detection for Helm AI
============================================

This module provides comprehensive ML-powered security capabilities:
- Real-time threat detection using machine learning
- Anomaly detection for user behavior
- Network traffic analysis
- Malware detection and classification
- Phishing detection
- Zero-day threat identification
- Threat intelligence integration
- Automated response and mitigation
"""

import asyncio
import json
import logging
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict

# ML imports
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.svm import OneClassSVM
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Local imports
from src.monitoring.structured_logging import StructuredLogger
from src.database.database_manager import DatabaseManager

logger = StructuredLogger("threat_detection")


class ThreatType(str, Enum):
    """Types of security threats"""
    MALWARE = "malware"
    PHISHING = "phishing"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    DDOS = "ddos"
    BRUTE_FORCE = "brute_force"
    DATA_EXFILTRATION = "data_exfiltration"
    INSIDER_THREAT = "insider_threat"
    ZERO_DAY = "zero_day"
    ANOMALY = "anomaly"


class ThreatSeverity(str, Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionModel(str, Enum):
    """ML detection models"""
    ISOLATION_FOREST = "isolation_forest"
    ONE_CLASS_SVM = "one_class_svm"
    RANDOM_FOREST = "random_forest"
    NEURAL_NETWORK = "neural_network"
    ENSEMBLE = "ensemble"


@dataclass
class ThreatEvent:
    """Threat event data"""
    id: str
    type: ThreatType
    severity: ThreatSeverity
    source_ip: str
    target_ip: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    features: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    description: str = ""
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class DetectionModel:
    """ML detection model configuration"""
    id: str
    name: str
    model_type: DetectionModel
    target_threats: List[ThreatType]
    features: List[str]
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    trained_at: Optional[datetime] = None
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ThreatAlert:
    """Threat alert configuration"""
    id: str
    event_id: str
    model_id: str
    severity: ThreatSeverity
    message: str
    recommendations: List[str] = field(default_factory=list)
    auto_response: bool = False
    response_actions: List[str] = field(default_factory=list)
    acknowledged: bool = False
    resolved: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


class MLThreatDetection:
    """ML-based Advanced Threat Detection System"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        
        # Storage
        self.models: Dict[str, DetectionModel] = {}
        self.threat_events: List[ThreatEvent] = []
        self.alerts: Dict[str, ThreatAlert] = {}
        
        # ML components
        self.scalers: Dict[str, StandardScaler] = {}
        self.encoders: Dict[str, LabelEncoder] = {}
        self.trained_models: Dict[str, Any] = {}
        
        # Initialize default models
        self._initialize_default_models()
        
        logger.info("ML Threat Detection System initialized")
    
    def _initialize_default_models(self):
        """Initialize default detection models"""
        default_models = [
            DetectionModel(
                id="malware_detector",
                name="Malware Detection Model",
                model_type=DetectionModel.RANDOM_FOREST,
                target_threats=[ThreatType.MALWARE],
                features=[
                    "file_size", "file_entropy", "file_type", "hash_pattern",
                    "api_calls", "network_connections", "registry_access",
                    "process_creation", "memory_usage", "cpu_usage"
                ],
                hyperparameters={
                    "n_estimators": 100,
                    "max_depth": 10,
                    "random_state": 42
                }
            ),
            DetectionModel(
                id="phishing_detector",
                name="Phishing Detection Model",
                model_type=DetectionModel.NEURAL_NETWORK,
                target_threats=[ThreatType.PHISHING],
                features=[
                    "url_length", "domain_age", "https_present", "suspicious_words",
                    "special_chars", "subdomain_count", "domain_similarity",
                    "brand_presence", "form_fields", "external_links"
                ],
                hyperparameters={
                    "hidden_layer_sizes": (100, 50),
                    "activation": "relu",
                    "solver": "adam",
                    "max_iter": 1000,
                    "random_state": 42
                }
            ),
            DetectionModel(
                id="anomaly_detector",
                name="Anomaly Detection Model",
                model_type=DetectionModel.ISOLATION_FOREST,
                target_threats=[ThreatType.ANOMALY],
                features=[
                    "login_frequency", "login_time_variance", "device_count",
                    "location_changes", "failed_attempts", "session_duration",
                    "data_access_volume", "api_calls_per_minute", "error_rate"
                ],
                hyperparameters={
                    "contamination": 0.1,
                    "random_state": 42
                }
            ),
            DetectionModel(
                id="network_threat_detector",
                name="Network Threat Detection Model",
                model_type=DetectionModel.ONE_CLASS_SVM,
                target_threats=[ThreatType.DDOS, ThreatType.SQL_INJECTION, ThreatType.XSS],
                features=[
                    "packet_size", "protocol", "port", "connection_duration",
                    "bytes_transferred", "packet_rate", "connection_count",
                    "source_entropy", "payload_entropy", "header_anomalies"
                ],
                hyperparameters={
                    "kernel": "rbf",
                    "gamma": "scale",
                    "nu": 0.1
                }
            )
        ]
        
        for model in default_models:
            self.models[model.id] = model
    
    def add_detection_model(self, model: DetectionModel) -> bool:
        """Add a new detection model"""
        try:
            self.models[model.id] = model
            logger.info(f"Detection model added: {model.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add detection model: {e}")
            return False
    
    def train_model(self, model_id: str, training_data: pd.DataFrame) -> Dict[str, Any]:
        """Train a detection model"""
        try:
            if model_id not in self.models:
                return {"error": "Model not found"}
            
            model = self.models[model_id]
            
            # Prepare training data
            X, y = self._prepare_training_data(training_data, model)
            
            if X is None or y is None:
                return {"error": "Failed to prepare training data"}
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model based on type
            trained_model = self._train_model_by_type(
                model.model_type, X_train_scaled, y_train, model.hyperparameters
            )
            
            # Evaluate model
            y_pred = trained_model.predict(X_test_scaled)
            
            # Calculate metrics
            accuracy = (y_pred == y_test).mean()
            
            if model.model_type != DetectionModel.ISOLATION_FOREST and model.model_type != DetectionModel.ONE_CLASS_SVM:
                # For supervised models
                report = classification_report(y_test, y_pred, output_dict=True)
                precision = report['weighted avg']['precision']
                recall = report['weighted avg']['recall']
                f1_score = report['weighted avg']['f1-score']
            else:
                # For unsupervised models
                precision = accuracy
                recall = accuracy
                f1_score = accuracy
            
            # Update model metrics
            model.accuracy = accuracy
            model.precision = precision
            model.recall = recall
            model.f1_score = f1_score
            model.trained_at = datetime.utcnow()
            
            # Store trained model and scaler
            self.trained_models[model_id] = trained_model
            self.scalers[model_id] = scaler
            
            logger.info(f"Model {model_id} trained successfully")
            
            return {
                "model_id": model_id,
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Model training failed for {model_id}: {e}")
            return {"error": str(e)}
    
    def _prepare_training_data(self, data: pd.DataFrame, model: DetectionModel) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Prepare training data for model"""
        try:
            # Check if required features exist
            missing_features = [f for f in model.features if f not in data.columns]
            if missing_features:
                logger.error(f"Missing features: {missing_features}")
                return None, None
            
            # Extract features
            X = data[model.features].values
            
            # Handle labels (for supervised models)
            if 'label' in data.columns:
                y = data['label'].values
            elif model.model_type not in [DetectionModel.ISOLATION_FOREST, DetectionModel.ONE_CLASS_SVM]:
                # For supervised models without labels, create dummy labels
                y = np.zeros(len(data))
            else:
                # For unsupervised models
                y = None
            
            return X, y
            
        except Exception as e:
            logger.error(f"Training data preparation failed: {e}")
            return None, None
    
    def _train_model_by_type(self, model_type: DetectionModel, X: np.ndarray, y: Optional[np.ndarray], 
                           hyperparameters: Dict[str, Any]) -> Any:
        """Train model based on type"""
        try:
            if model_type == DetectionModel.RANDOM_FOREST:
                model = RandomForestClassifier(**hyperparameters)
                model.fit(X, y)
            elif model_type == DetectionModel.NEURAL_NETWORK:
                model = MLPClassifier(**hyperparameters)
                model.fit(X, y)
            elif model_type == DetectionModel.ISOLATION_FOREST:
                model = IsolationForest(**hyperparameters)
                model.fit(X)
            elif model_type == DetectionModel.ONE_CLASS_SVM:
                model = OneClassSVM(**hyperparameters)
                model.fit(X)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            return model
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise
    
    def detect_threats(self, event_data: Dict[str, Any]) -> List[ThreatEvent]:
        """Detect threats using trained models"""
        try:
            detected_threats = []
            
            # Process each enabled model
            for model_id, model in self.models.items():
                if not model.enabled or model_id not in self.trained_models:
                    continue
                
                try:
                    # Extract features
                    features = self._extract_features(event_data, model)
                    
                    if not features:
                        continue
                    
                    # Make prediction
                    threat_type, confidence = self._predict_threat(model_id, features)
                    
                    if threat_type and confidence > 0.5:  # Confidence threshold
                        # Determine severity
                        severity = self._determine_severity(threat_type, confidence)
                        
                        # Create threat event
                        threat_event = ThreatEvent(
                            id=str(uuid.uuid4()),
                            type=threat_type,
                            severity=severity,
                            source_ip=event_data.get('source_ip', 'unknown'),
                            target_ip=event_data.get('target_ip'),
                            user_id=event_data.get('user_id'),
                            features=features,
                            confidence=confidence,
                            description=self._generate_threat_description(threat_type, confidence),
                            raw_data=event_data
                        )
                        
                        detected_threats.append(threat_event)
                        
                        # Create alert
                        self._create_alert(threat_event, model_id)
                        
                except Exception as e:
                    logger.error(f"Threat detection failed for model {model_id}: {e}")
            
            # Store threat events
            self.threat_events.extend(detected_threats)
            
            return detected_threats
            
        except Exception as e:
            logger.error(f"Threat detection failed: {e}")
            return []
    
    def _extract_features(self, event_data: Dict[str, Any], model: DetectionModel) -> Optional[Dict[str, float]]:
        """Extract features from event data"""
        try:
            features = {}
            
            for feature_name in model.features:
                if feature_name in event_data:
                    value = event_data[feature_name]
                    
                    # Convert to float
                    if isinstance(value, (int, float)):
                        features[feature_name] = float(value)
                    elif isinstance(value, str):
                        # Handle categorical features
                        if feature_name.endswith('_type') or feature_name.endswith('_protocol'):
                            # Simple encoding for categorical features
                            features[feature_name] = hash(value) % 1000
                        else:
                            # For other string features, use length or other numeric representation
                            features[feature_name] = float(len(value))
                    elif isinstance(value, bool):
                        features[feature_name] = 1.0 if value else 0.0
                    else:
                        features[feature_name] = 0.0
                else:
                    # Missing feature - use default value
                    features[feature_name] = 0.0
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return None
    
    def _predict_threat(self, model_id: str, features: Dict[str, float]) -> Tuple[Optional[ThreatType], float]:
        """Predict threat using trained model"""
        try:
            model = self.models[model_id]
            trained_model = self.trained_models[model_id]
            scaler = self.scalers[model_id]
            
            # Prepare feature vector
            feature_vector = np.array([features[f] for f in model.features]).reshape(1, -1)
            
            # Scale features
            feature_vector_scaled = scaler.transform(feature_vector)
            
            # Make prediction
            if model.model_type in [DetectionModel.ISOLATION_FOREST, DetectionModel.ONE_CLASS_SVM]:
                # Unsupervised models - predict anomaly
                prediction = trained_model.predict(feature_vector_scaled)[0]
                confidence = trained_model.decision_function(feature_vector_scaled)[0]
                
                if prediction == -1:  # Anomaly detected
                    threat_type = model.target_threats[0] if model.target_threats else ThreatType.ANOMALY
                    confidence_score = abs(confidence)
                else:
                    return None, 0.0
            else:
                # Supervised models
                prediction = trained_model.predict(feature_vector_scaled)[0]
                probabilities = trained_model.predict_proba(feature_vector_scaled)[0]
                
                if prediction != 0:  # Threat detected
                    threat_type = model.target_threats[prediction - 1] if prediction - 1 < len(model.target_threats) else ThreatType.ANOMALY
                    confidence_score = max(probabilities)
                else:
                    return None, 0.0
            
            return threat_type, confidence_score
            
        except Exception as e:
            logger.error(f"Threat prediction failed for model {model_id}: {e}")
            return None, 0.0
    
    def _determine_severity(self, threat_type: ThreatType, confidence: float) -> ThreatSeverity:
        """Determine threat severity based on type and confidence"""
        try:
            # Base severity by threat type
            base_severity = {
                ThreatType.ZERO_DAY: ThreatSeverity.CRITICAL,
                ThreatType.DATA_EXFILTRATION: ThreatSeverity.CRITICAL,
                ThreatType.MALWARE: ThreatSeverity.HIGH,
                ThreatType.DDOS: ThreatSeverity.HIGH,
                ThreatType.SQL_INJECTION: ThreatSeverity.HIGH,
                ThreatType.INSIDER_THREAT: ThreatSeverity.HIGH,
                ThreatType.PHISHING: ThreatSeverity.MEDIUM,
                ThreatType.XSS: ThreatSeverity.MEDIUM,
                ThreatType.BRUTE_FORCE: ThreatSeverity.MEDIUM,
                ThreatType.ANOMALY: ThreatSeverity.LOW
            }
            
            severity = base_severity.get(threat_type, ThreatSeverity.MEDIUM)
            
            # Adjust based on confidence
            if confidence > 0.9:
                # High confidence - upgrade severity
                if severity == ThreatSeverity.LOW:
                    severity = ThreatSeverity.MEDIUM
                elif severity == ThreatSeverity.MEDIUM:
                    severity = ThreatSeverity.HIGH
            elif confidence < 0.6:
                # Low confidence - downgrade severity
                if severity == ThreatSeverity.CRITICAL:
                    severity = ThreatSeverity.HIGH
                elif severity == ThreatSeverity.HIGH:
                    severity = ThreatSeverity.MEDIUM
                elif severity == ThreatSeverity.MEDIUM:
                    severity = ThreatSeverity.LOW
            
            return severity
            
        except Exception as e:
            logger.error(f"Severity determination failed: {e}")
            return ThreatSeverity.MEDIUM
    
    def _generate_threat_description(self, threat_type: ThreatType, confidence: float) -> str:
        """Generate threat description"""
        try:
            descriptions = {
                ThreatType.MALWARE: f"Malicious software detected with {confidence:.2%} confidence",
                ThreatType.PHISHING: f"Phishing attempt detected with {confidence:.2%} confidence",
                ThreatType.SQL_INJECTION: f"SQL injection attack detected with {confidence:.2%} confidence",
                ThreatType.XSS: f"Cross-site scripting attack detected with {confidence:.2%} confidence",
                ThreatType.DDOS: f"DDoS attack detected with {confidence:.2%} confidence",
                ThreatType.BRUTE_FORCE: f"Brute force attack detected with {confidence:.2%} confidence",
                ThreatType.DATA_EXFILTRATION: f"Data exfiltration attempt detected with {confidence:.2%} confidence",
                ThreatType.INSIDER_THREAT: f"Insider threat activity detected with {confidence:.2%} confidence",
                ThreatType.ZERO_DAY: f"Zero-day exploit detected with {confidence:.2%} confidence",
                ThreatType.ANOMALY: f"Anomalous activity detected with {confidence:.2%} confidence"
            }
            
            return descriptions.get(threat_type, f"Threat detected with {confidence:.2%} confidence")
            
        except Exception as e:
            logger.error(f"Threat description generation failed: {e}")
            return f"Threat detected with {confidence:.2%} confidence"
    
    def _create_alert(self, threat_event: ThreatEvent, model_id: str):
        """Create threat alert"""
        try:
            alert = ThreatAlert(
                id=str(uuid.uuid4()),
                event_id=threat_event.id,
                model_id=model_id,
                severity=threat_event.severity,
                message=f"Threat detected: {threat_event.description}",
                recommendations=self._generate_recommendations(threat_event),
                auto_response=threat_event.severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL],
                response_actions=self._get_response_actions(threat_event)
            )
            
            self.alerts[alert.id] = alert
            
            logger.info(f"Threat alert created: {alert.id}")
            
        except Exception as e:
            logger.error(f"Alert creation failed: {e}")
    
    def _generate_recommendations(self, threat_event: ThreatEvent) -> List[str]:
        """Generate threat mitigation recommendations"""
        try:
            recommendations = {
                ThreatType.MALWARE: [
                    "Isolate affected system from network",
                    "Run comprehensive malware scan",
                    "Update antivirus definitions",
                    "Review system logs for additional infections"
                ],
                ThreatType.PHISHING: [
                    "Block malicious sender/domain",
                    "Educate users about phishing techniques",
                    "Review email security policies",
                    "Enable advanced email filtering"
                ],
                ThreatType.SQL_INJECTION: [
                    "Block source IP address",
                    "Review and patch vulnerable applications",
                    "Implement input validation",
                    "Audit database access logs"
                ],
                ThreatType.XSS: [
                    "Sanitize user input in web applications",
                    "Implement Content Security Policy",
                    "Update web application firewall rules",
                    "Review web application code"
                ],
                ThreatType.DDOS: [
                    "Enable DDoS protection",
                    "Rate limit traffic from source IP",
                    "Scale up infrastructure",
                    "Contact CDN provider for assistance"
                ],
                ThreatType.BRUTE_FORCE: [
                    "Block source IP address",
                    "Implement account lockout policies",
                    "Enable multi-factor authentication",
                    "Review authentication logs"
                ],
                ThreatType.DATA_EXFILTRATION: [
                    "Block data transfer to external destinations",
                    "Review data access permissions",
                    "Implement data loss prevention",
                    "Audit user activity logs"
                ],
                ThreatType.INSIDER_THREAT: [
                    "Review user activity logs",
                    "Implement principle of least privilege",
                    "Monitor privileged account usage",
                    "Conduct security awareness training"
                ],
                ThreatType.ZERO_DAY: [
                    "Isolate affected systems",
                    "Implement network segmentation",
                    "Monitor for similar activity",
                    "Contact security vendors for updates"
                ],
                ThreatType.ANOMALY: [
                    "Investigate anomalous activity",
                    "Review user behavior patterns",
                    "Monitor for additional anomalies",
                    "Update security baselines"
                ]
            }
            
            return recommendations.get(threat_event.type, ["Investigate the threat", "Review security logs", "Update security policies"])
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Investigate the threat", "Review security logs"]
    
    def _get_response_actions(self, threat_event: ThreatEvent) -> List[str]:
        """Get automated response actions"""
        try:
            actions = {
                ThreatType.MALWARE: ["isolate_system", "scan_malware", "update_signatures"],
                ThreatType.PHISHING: ["block_sender", "quarantine_email", "update_filters"],
                ThreatType.SQL_INJECTION: ["block_ip", "patch_vulnerability", "audit_database"],
                ThreatType.XSS: ["block_ip", "update_waf_rules", "sanitize_input"],
                ThreatType.DDOS: ["enable_ddos_protection", "rate_limit", "scale_infrastructure"],
                ThreatType.BRUTE_FORCE: ["block_ip", "lock_account", "enable_mfa"],
                ThreatType.DATA_EXFILTRATION: ["block_transfer", "audit_permissions", "enable_dlp"],
                ThreatType.INSIDER_THREAT: ["monitor_user", "restrict_access", "audit_activity"],
                ThreatType.ZERO_DAY: ["isolate_system", "segment_network", "monitor_activity"],
                ThreatType.ANOMALY: ["investigate", "monitor", "update_baselines"]
            }
            
            return actions.get(threat_event.type, ["monitor", "investigate"])
            
        except Exception as e:
            logger.error(f"Response actions generation failed: {e}")
            return ["monitor", "investigate"]
    
    def get_threat_statistics(self, time_window: int = 24) -> Dict[str, Any]:
        """Get threat statistics for time window"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window)
            
            # Filter recent threats
            recent_threats = [
                threat for threat in self.threat_events
                if threat.timestamp >= cutoff_time
            ]
            
            # Calculate statistics
            stats = {
                "total_threats": len(recent_threats),
                "threats_by_type": defaultdict(int),
                "threats_by_severity": defaultdict(int),
                "threats_by_hour": defaultdict(int),
                "top_source_ips": defaultdict(int),
                "top_users": defaultdict(int),
                "model_performance": {}
            }
            
            for threat in recent_threats:
                stats["threats_by_type"][threat.type.value] += 1
                stats["threats_by_severity"][threat.severity.value] += 1
                stats["threats_by_hour"][threat.timestamp.hour] += 1
                stats["top_source_ips"][threat.source_ip] += 1
                
                if threat.user_id:
                    stats["top_users"][threat.user_id] += 1
            
            # Model performance
            for model_id, model in self.models.items():
                if model.trained_at:
                    stats["model_performance"][model_id] = {
                        "accuracy": model.accuracy,
                        "precision": model.precision,
                        "recall": model.recall,
                        "f1_score": model.f1_score,
                        "trained_at": model.trained_at.isoformat()
                    }
            
            # Convert defaultdicts to regular dicts and sort
            stats["threats_by_type"] = dict(sorted(stats["threats_by_type"].items(), key=lambda x: x[1], reverse=True))
            stats["threats_by_severity"] = dict(sorted(stats["threats_by_severity"].items(), key=lambda x: x[1], reverse=True))
            stats["top_source_ips"] = dict(sorted(stats["top_source_ips"].items(), key=lambda x: x[1], reverse=True)[:10])
            stats["top_users"] = dict(sorted(stats["top_users"].items(), key=lambda x: x[1], reverse=True)[:10])
            
            return stats
            
        except Exception as e:
            logger.error(f"Threat statistics calculation failed: {e}")
            return {"error": str(e)}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "total_models": len(self.models),
            "trained_models": len(self.trained_models),
            "total_threats": len(self.threat_events),
            "active_alerts": len([a for a in self.alerts.values() if not a.resolved]),
            "supported_threat_types": [t.value for t in ThreatType],
            "model_types": [m.value for m in DetectionModel],
            "system_uptime": datetime.utcnow().isoformat()
        }


# Configuration
THREAT_DETECTION_CONFIG = {
    "database": {
        "connection_string": os.getenv("DATABASE_URL")
    },
    "models": {
        "retrain_interval": 7,  # days
        "confidence_threshold": 0.5,
        "max_training_samples": 10000
    },
    "alerts": {
        "auto_response_threshold": 0.8,
        "alert_retention_days": 30
    }
}


# Initialize ML threat detection system
ml_threat_detection = MLThreatDetection(THREAT_DETECTION_CONFIG)

# Export main components
__all__ = [
    'MLThreatDetection',
    'ThreatEvent',
    'DetectionModel',
    'ThreatAlert',
    'ThreatType',
    'ThreatSeverity',
    'DetectionModel',
    'ml_threat_detection'
]
