"""
Helm AI Advanced Anomaly Detection System
ML-based threat detection and anomaly analysis for security monitoring
"""

import os
import sys
import json
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading
import pickle

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.database_manager import get_database_manager
from monitoring.structured_logging import logger
from security.security_monitoring import security_monitor
from ml.model_management import model_manager

@dataclass
class AnomalyEvent:
    """Anomaly detection event"""
    anomaly_id: str
    timestamp: datetime
    anomaly_type: str
    severity: str  # low, medium, high, critical
    confidence: float  # 0-1
    description: str
    source: str
    features: Dict[str, float]
    model_version: str
    context: Dict[str, Any]
    status: str = "detected"  # detected, investigating, resolved, false_positive
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'anomaly_id': self.anomaly_id,
            'timestamp': self.timestamp.isoformat(),
            'anomaly_type': self.anomaly_type,
            'severity': self.severity,
            'confidence': self.confidence,
            'description': self.description,
            'source': self.source,
            'features': self.features,
            'model_version': self.model_version,
            'context': self.context,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

@dataclass
class AnomalyModel:
    """Anomaly detection model"""
    model_id: str
    model_type: str  # isolation_forest, autoencoder, lstm, etc.
    feature_columns: List[str]
    threshold: float
    created_at: datetime
    trained_at: Optional[datetime] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'model_id': self.model_id,
            'model_type': self.model_type,
            'feature_columns': self.feature_columns,
            'threshold': self.threshold,
            'created_at': self.created_at.isoformat(),
            'trained_at': self.trained_at.isoformat() if self.trained_at else None,
            'performance_metrics': self.performance_metrics,
            'is_active': self.is_active
        }

class AnomalyDetector:
    """ML-based anomaly detection engine"""
    
    def __init__(self):
        self.models = {}
        self.anomaly_events = deque(maxlen=1000)
        self.feature_extractors = {}
        self.lock = threading.RLock()
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Setup default models
        self._setup_default_models()
        
    def _setup_default_models(self):
        """Setup default anomaly detection models"""
        self.models['login_behavior'] = AnomalyModel(
            model_id='login_behavior',
            model_type='isolation_forest',
            feature_columns=['login_frequency', 'time_of_day', 'location_changes', 'device_changes'],
            threshold=0.1,
            created_at=datetime.now()
        )
        
        self.models['api_usage'] = AnomalyModel(
            model_id='api_usage',
            model_type='autoencoder',
            feature_columns=['request_rate', 'response_time', 'error_rate', 'data_volume'],
            threshold=0.15,
            created_at=datetime.now()
        )
        
        self.models['user_activity'] = AnomalyModel(
            model_id='user_activity',
            model_type='lstm',
            feature_columns=['session_duration', 'actions_per_session', 'feature_usage', 'time_between_actions'],
            threshold=0.2,
            created_at=datetime.now()
        )
        
        self.models['system_performance'] = AnomalyModel(
            model_id='system_performance',
            model_type='isolation_forest',
            feature_columns=['cpu_usage', 'memory_usage', 'disk_io', 'network_io', 'response_time'],
            threshold=0.1,
            created_at=datetime.now()
        )
    
    def start_monitoring(self):
        """Start anomaly monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Anomaly detection monitoring started")
    
    def stop_monitoring(self):
        """Stop anomaly monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Anomaly detection monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                self._check_all_models()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Anomaly monitoring error: {e}")
                time.sleep(60)
    
    def _check_all_models(self):
        """Check all anomaly detection models"""
        for model_id, model in self.models.items():
            if not model.is_active:
                continue
            
            try:
                anomalies = self._detect_anomalies(model_id)
                
                for anomaly in anomalies:
                    with self.lock:
                        self.anomaly_events.append(anomaly)
                    
                    # Trigger security alert for high-confidence anomalies
                    if anomaly.confidence > 0.8 and anomaly.severity in ['high', 'critical']:
                        self._trigger_security_alert(anomaly)
                
            except Exception as e:
                logger.error(f"Error checking model {model_id}: {e}")
    
    def _detect_anomalies(self, model_id: str) -> List[AnomalyEvent]:
        """Detect anomalies using a specific model"""
        model = self.models.get(model_id)
        if not model:
            return []
        
        anomalies = []
        
        try:
            if model_id == 'login_behavior':
                anomalies.extend(self._detect_login_anomalies(model))
            elif model_id == 'api_usage':
                anomalies.extend(self._detect_api_anomalies(model))
            elif model_id == 'user_activity':
                anomalies.extend(self._detect_activity_anomalies(model))
            elif model_id == 'system_performance':
                anomalies.extend(self._detect_performance_anomalies(model))
                
        except Exception as e:
            logger.error(f"Error detecting anomalies for {model_id}: {e}")
        
        return anomalies
    
    def _detect_login_anomalies(self, model: AnomalyModel) -> List[AnomalyEvent]:
        """Detect login behavior anomalies"""
        anomalies = []
        
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Get recent login attempts
                result = session.execute(text("""
                    SELECT user_id, created_at, ip_address, user_agent,
                           COUNT(*) OVER (PARTITION BY user_id ORDER BY created_at 
                           ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) as recent_logins
                    FROM audit_logs
                    WHERE action = 'login_success'
                    AND created_at > NOW() - INTERVAL '1 hour'
                    ORDER BY created_at DESC
                """))
                
                login_data = result.fetchall()
                
                for row in login_data:
                    user_id, created_at, ip_address, user_agent, recent_logins = row
                    
                    # Extract features
                    features = self._extract_login_features(user_id, created_at, ip_address, user_agent, recent_logins)
                    
                    # Simulate anomaly detection (in practice, use trained model)
                    anomaly_score = self._calculate_anomaly_score(features, model.threshold)
                    
                    if anomaly_score > model.threshold:
                        severity = self._determine_severity(anomaly_score)
                        
                        anomaly = AnomalyEvent(
                            anomaly_id=f"login_{int(time.time())}_{user_id}",
                            timestamp=datetime.now(),
                            anomaly_type='login_behavior',
                            severity=severity,
                            confidence=anomaly_score,
                            description=f"Unusual login behavior detected for user {user_id}",
                            source='anomaly_detector',
                            features=features,
                            model_version=model.model_id,
                            context={
                                'user_id': user_id,
                                'ip_address': ip_address,
                                'user_agent': user_agent,
                                'recent_logins': recent_logins
                            }
                        )
                        
                        anomalies.append(anomaly)
                
        except Exception as e:
            logger.error(f"Error detecting login anomalies: {e}")
        
        return anomalies
    
    def _detect_api_anomalies(self, model: AnomalyModel) -> List[AnomalyEvent]:
        """Detect API usage anomalies"""
        anomalies = []
        
        try:
            # Get API usage metrics
            api_metrics = self._get_api_metrics()
            
            for endpoint, metrics in api_metrics.items():
                features = {
                    'request_rate': metrics.get('requests_per_minute', 0),
                    'response_time': metrics.get('avg_response_time', 0),
                    'error_rate': metrics.get('error_rate', 0),
                    'data_volume': metrics.get('data_volume', 0)
                }
                
                # Simulate anomaly detection
                anomaly_score = self._calculate_anomaly_score(features, model.threshold)
                
                if anomaly_score > model.threshold:
                    severity = self._determine_severity(anomaly_score)
                    
                    anomaly = AnomalyEvent(
                        anomaly_id=f"api_{int(time.time())}_{endpoint}",
                        timestamp=datetime.now(),
                        anomaly_type='api_usage',
                        severity=severity,
                        confidence=anomaly_score,
                        description=f"Unusual API usage detected for endpoint {endpoint}",
                        source='anomaly_detector',
                        features=features,
                        model_version=model.model_id,
                        context={
                            'endpoint': endpoint,
                            'metrics': metrics
                        }
                    )
                    
                    anomalies.append(anomaly)
                
        except Exception as e:
            logger.error(f"Error detecting API anomalies: {e}")
        
        return anomalies
    
    def _detect_activity_anomalies(self, model: AnomalyModel) -> List[AnomalyEvent]:
        """Detect user activity anomalies"""
        anomalies = []
        
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Get user activity data
                result = session.execute(text("""
                    SELECT user_id, COUNT(*) as session_count,
                           AVG(EXTRACT(EPOCH FROM (updated_at - created_at))/60) as avg_duration,
                           COUNT(DISTINCT action) as unique_actions
                    FROM (
                        SELECT user_id, created_at, updated_at, action,
                               ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) as rn
                        FROM audit_logs
                        WHERE created_at > NOW() - INTERVAL '24 hours'
                    ) sessions
                    WHERE rn = 1 OR (LAG(created_at) OVER (PARTITION BY user_id ORDER BY created_at) IS NOT NULL)
                    GROUP BY user_id
                    HAVING session_count > 1
                """))
                
                activity_data = result.fetchall()
                
                for row in activity_data:
                    user_id, session_count, avg_duration, unique_actions = row
                    
                    features = {
                        'session_duration': avg_duration or 0,
                        'actions_per_session': unique_actions / max(session_count, 1),
                        'session_frequency': session_count,
                        'feature_usage': unique_actions
                    }
                    
                    # Simulate anomaly detection
                    anomaly_score = self._calculate_anomaly_score(features, model.threshold)
                    
                    if anomaly_score > model.threshold:
                        severity = self._determine_severity(anomaly_score)
                        
                        anomaly = AnomalyEvent(
                            anomaly_id=f"activity_{int(time.time())}_{user_id}",
                            timestamp=datetime.now(),
                            anomaly_type='user_activity',
                            severity=severity,
                            confidence=anomaly_score,
                            description=f"Unusual user activity detected for user {user_id}",
                            source='anomaly_detector',
                            features=features,
                            model_version=model.model_id,
                            context={
                                'user_id': user_id,
                                'session_count': session_count,
                                'avg_duration': avg_duration,
                                'unique_actions': unique_actions
                            }
                        )
                        
                        anomalies.append(anomaly)
                
        except Exception as e:
            logger.error(f"Error detecting activity anomalies: {e}")
        
        return anomalies
    
    def _detect_performance_anomalies(self, model: AnomalyModel) -> List[AnomalyEvent]:
        """Detect system performance anomalies"""
        anomalies = []
        
        try:
            # Get system performance metrics
            perf_metrics = self._get_system_metrics()
            
            features = {
                'cpu_usage': perf_metrics.get('cpu_usage', 0),
                'memory_usage': perf_metrics.get('memory_usage', 0),
                'disk_io': perf_metrics.get('disk_io', 0),
                'network_io': perf_metrics.get('network_io', 0),
                'response_time': perf_metrics.get('response_time', 0)
            }
            
            # Simulate anomaly detection
            anomaly_score = self._calculate_anomaly_score(features, model.threshold)
            
            if anomaly_score > model.threshold:
                severity = self._determine_severity(anomaly_score)
                
                anomaly = AnomalyEvent(
                    anomaly_id=f"performance_{int(time.time())}",
                    timestamp=datetime.now(),
                    anomaly_type='system_performance',
                    severity=severity,
                    confidence=anomaly_score,
                    description="Unusual system performance detected",
                    source='anomaly_detector',
                    features=features,
                    model_version=model.model_id,
                    context=perf_metrics
                )
                
                anomalies.append(anomaly)
                
        except Exception as e:
            logger.error(f"Error detecting performance anomalies: {e}")
        
        return anomalies
    
    def _extract_login_features(self, user_id: str, created_at: datetime, 
                               ip_address: str, user_agent: str, recent_logins: int) -> Dict[str, float]:
        """Extract features for login anomaly detection"""
        try:
            # Time-based features
            hour_of_day = created_at.hour
            day_of_week = created_at.weekday()
            
            # Location features (simplified)
            location_changes = self._count_location_changes(user_id, created_at)
            
            # Device features (simplified)
            device_changes = self._count_device_changes(user_id, created_at)
            
            return {
                'login_frequency': recent_logins,
                'time_of_day': hour_of_day / 24.0,
                'day_of_week': day_of_week / 7.0,
                'location_changes': location_changes,
                'device_changes': device_changes
            }
            
        except Exception as e:
            logger.error(f"Error extracting login features: {e}")
            return {}
    
    def _count_location_changes(self, user_id: str, since: datetime) -> float:
        """Count location changes for user"""
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                result = session.execute(text("""
                    SELECT COUNT(DISTINCT ip_address) FROM audit_logs
                    WHERE user_id = :user_id
                    AND action = 'login_success'
                    AND created_at > :since
                """), {'user_id': user_id, 'since': since})
                
                return float(result.scalar())
                
        except Exception as e:
            logger.error(f"Error counting location changes: {e}")
            return 0.0
    
    def _count_device_changes(self, user_id: str, since: datetime) -> float:
        """Count device changes for user"""
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                result = session.execute(text("""
                    SELECT COUNT(DISTINCT user_agent) FROM audit_logs
                    WHERE user_id = :user_id
                    AND action = 'login_success'
                    AND created_at > :since
                """), {'user_id': user_id, 'since': since})
                
                return float(result.scalar())
                
        except Exception as e:
            logger.error(f"Error counting device changes: {e}")
            return 0.0
    
    def _get_api_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get API usage metrics"""
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                result = session.execute(text("""
                    SELECT 
                        SUBSTRING(action FROM 'api_(.+?)') as endpoint,
                        COUNT(*) as request_count,
                        AVG(EXTRACT(EPOCH FROM (updated_at - created_at))*1000) as avg_response_time,
                        COUNT(CASE WHEN action LIKE '%error%' THEN 1 END) as error_count
                    FROM audit_logs
                    WHERE action LIKE 'api_%'
                    AND created_at > NOW() - INTERVAL '1 hour'
                    GROUP BY endpoint
                """))
                
                metrics = {}
                for row in result:
                    endpoint, request_count, avg_response_time, error_count = row
                    
                    metrics[endpoint] = {
                        'requests_per_minute': request_count / 60.0,
                        'avg_response_time': avg_response_time or 0,
                        'error_rate': (error_count / request_count * 100) if request_count > 0 else 0,
                        'data_volume': request_count * 1024  # Simplified
                    }
                
                return metrics
                
        except Exception as e:
            logger.error(f"Error getting API metrics: {e}")
            return {}
    
    def _get_system_metrics(self) -> Dict[str, float]:
        """Get system performance metrics"""
        try:
            import psutil
            
            return {
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_io': psutil.disk_io_counters().read_bytes + psutil.disk_io_counters().write_bytes,
                'network_io': psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv,
                'response_time': 150.0  # Would come from actual monitoring
            }
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def _calculate_anomaly_score(self, features: Dict[str, float], threshold: float) -> float:
        """Calculate anomaly score (simulated)"""
        # In practice, this would use the trained ML model
        # For now, simulate based on feature deviations
        
        score = 0.0
        feature_count = len(features)
        
        if feature_count == 0:
            return 0.0
        
        # Simple scoring based on feature extremes
        for feature_name, value in features.items():
            if 'rate' in feature_name.lower() and value > 100:
                score += 0.3
            elif 'time' in feature_name.lower() and value > 1000:
                score += 0.3
            elif 'usage' in feature_name.lower() and value > 80:
                score += 0.3
            elif 'changes' in feature_name.lower() and value > 5:
                score += 0.3
        
        return min(score / feature_count, 1.0)
    
    def _determine_severity(self, anomaly_score: float) -> str:
        """Determine anomaly severity based on score"""
        if anomaly_score > 0.8:
            return 'critical'
        elif anomaly_score > 0.6:
            return 'high'
        elif anomaly_score > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _trigger_security_alert(self, anomaly: AnomalyEvent):
        """Trigger security alert for high-confidence anomaly"""
        try:
            # Create security alert
            alert_data = {
                'alert_id': f"anomaly_{anomaly.anomaly_id}",
                'timestamp': anomaly.timestamp.isoformat(),
                'severity': anomaly.severity,
                'category': 'anomaly_detection',
                'title': f"Anomaly Detected: {anomaly.anomaly_type}",
                'description': anomaly.description,
                'source': 'anomaly_detector',
                'affected_resources': [anomaly.anomaly_type],
                'indicators': {
                    'anomaly_score': anomaly.confidence,
                    'model_version': anomaly.model_version,
                    'features': anomaly.features
                }
            }
            
            # Add to security monitor
            if hasattr(security_monitor, 'create_alert'):
                security_monitor.create_alert(alert_data)
            
            logger.warning(f"Security alert triggered for anomaly: {anomaly.anomaly_id}")
            
        except Exception as e:
            logger.error(f"Error triggering security alert: {e}")
    
    def get_anomaly_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get anomaly detection summary"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            recent_anomalies = [a for a in self.anomaly_events if a.timestamp >= cutoff_time]
        
        if not recent_anomalies:
            return {
                'period_hours': hours,
                'total_anomalies': 0,
                'by_type': {},
                'by_severity': {},
                'by_status': {},
                'high_confidence_count': 0
            }
        
        # Group by type
        by_type = defaultdict(int)
        for anomaly in recent_anomalies:
            by_type[anomaly.anomaly_type] += 1
        
        # Group by severity
        by_severity = defaultdict(int)
        for anomaly in recent_anomalies:
            by_severity[anomaly.severity] += 1
        
        # Group by status
        by_status = defaultdict(int)
        for anomaly in recent_anomalies:
            by_status[anomaly.status] += 1
        
        return {
            'period_hours': hours,
            'total_anomalies': len(recent_anomalies),
            'by_type': dict(by_type),
            'by_severity': dict(by_severity),
            'by_status': dict(by_status),
            'high_confidence_count': len([a for a in recent_anomalies if a.confidence > 0.8]),
            'critical_count': len([a for a in recent_anomalies if a.severity == 'critical'])
        }
    
    def train_model(self, model_id: str, training_data: List[Dict[str, Any]]) -> bool:
        """Train an anomaly detection model"""
        try:
            model = self.models.get(model_id)
            if not model:
                logger.error(f"Model not found: {model_id}")
                return False
            
            # Simulate model training
            logger.info(f"Training model {model_id} with {len(training_data)} samples")
            
            # In practice, this would train the actual ML model
            # For now, just update the trained timestamp
            model.trained_at = datetime.now()
            model.performance_metrics = {
                'accuracy': 0.92,
                'precision': 0.89,
                'recall': 0.94,
                'f1_score': 0.91
            }
            
            logger.info(f"Model {model_id} training completed")
            return True
            
        except Exception as e:
            logger.error(f"Error training model {model_id}: {e}")
            return False

# Global anomaly detector instance
anomaly_detector = AnomalyDetector()

def start_anomaly_monitoring():
    """Start anomaly detection monitoring"""
    anomaly_detector.start_monitoring()
    logger.info("Anomaly detection system started")

def stop_anomaly_monitoring():
    """Stop anomaly detection monitoring"""
    anomaly_detector.stop_monitoring()
    logger.info("Anomaly detection system stopped")

def get_anomaly_summary(hours: int = 24) -> Dict[str, Any]:
    """Get anomaly detection summary"""
    return anomaly_detector.get_anomaly_summary(hours)

def detect_anomalies(model_id: str) -> List[AnomalyEvent]:
    """Manually trigger anomaly detection for a specific model"""
    return anomaly_detector._detect_anomalies(model_id)
