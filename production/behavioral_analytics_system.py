#!/usr/bin/env python3
"""
Stellar Logic AI - Behavioral Analytics for Anomaly Detection
Advanced machine learning-based behavioral analysis and anomaly detection
"""

import os
import sys
import json
import time
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
import math

@dataclass
class BehaviorProfile:
    """User behavior profile data structure"""
    user_id: str
    source_ip: str
    session_id: str
    created_at: datetime
    last_updated: datetime
    features: Dict[str, Any]
    risk_score: float
    anomaly_count: int
    baseline_established: bool

@dataclass
class AnomalyEvent:
    """Anomaly event data structure"""
    timestamp: datetime
    user_id: str
    source_ip: str
    session_id: str
    anomaly_type: str
    severity: str
    confidence: float
    description: str
    features: Dict[str, Any]
    anomaly_id: str

class BehavioralAnalytics:
    """Behavioral analytics system for anomaly detection"""
    
    def __init__(self):
        self.base_path = "c:/Users/merce/Documents/helm-ai"
        self.production_path = "c:/Users/merce/Documents/helm-ai/production"
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.production_path, "logs/behavioral_analytics.log")),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Behavior profiles storage
        self.user_profiles = {}
        
        # Anomaly detection models (simplified without sklearn)
        self.models = {
            "statistical": StatisticalAnomalyDetector()
        }
        
        # Analytics data storage
        self.behavior_history = deque(maxlen=10000)
        self.anomaly_events = []
        
        # Statistics
        self.stats = {
            "total_sessions": 0,
            "total_users": 0,
            "anomalies_detected": 0,
            "baseline_profiles": 0
        }
        
        # Load configuration
        self.load_configuration()
        
        self.logger.info("Behavioral Analytics System initialized")
    
    def load_configuration(self):
        """Load behavioral analytics configuration"""
        config_file = os.path.join(self.production_path, "config/behavioral_analytics_config.json")
        
        default_config = {
            "behavioral_analytics": {
                "enabled": True,
                "models": {
                    "statistical": {"enabled": True, "z_score_threshold": 3.0}
                },
                "anomaly_detection": {
                    "sensitivity": 0.7,
                    "min_confidence": 0.6,
                    "alert_threshold": 0.8,
                    "auto_response": True
                }
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                # Save default configuration
                with open(config_file, 'w') as f:
                    json.dump(self.config, f, indent=2)
                self.logger.info("Created default behavioral analytics configuration")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            self.config = default_config
    
    def analyze_behavior(self, event_data: Dict[str, Any]) -> List[AnomalyEvent]:
        """Analyze user behavior for anomalies"""
        anomalies = []
        
        try:
            # Extract features
            features = self.extract_features(event_data)
            
            # Get or create user profile
            user_id = event_data.get("user_id", "anonymous")
            profile = self.get_or_create_profile(user_id, event_data, features)
            
            # Update profile with new behavior
            self.update_profile(profile, features)
            
            # Check for anomalies using rules
            if profile.baseline_established:
                rule_anomalies = self.check_anomaly_rules(profile, features)
                anomalies.extend(rule_anomalies)
            
            # Update statistics
            self.stats["total_sessions"] += 1
            if anomalies:
                self.stats["anomalies_detected"] += len(anomalies)
            
            # Store behavior event
            self.behavior_history.append({
                "timestamp": datetime.now(),
                "user_id": user_id,
                "features": features,
                "anomalies": len(anomalies)
            })
            
        except Exception as e:
            self.logger.error(f"Error analyzing behavior: {str(e)}")
        
        return anomalies
    
    def extract_features(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from event data"""
        features = {}
        
        try:
            timestamp = event_data.get("timestamp", datetime.now())
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            features.update({
                "hour_of_day": timestamp.hour,
                "day_of_week": timestamp.weekday(),
                "is_weekend": timestamp.weekday() >= 5,
                "is_business_hours": 9 <= timestamp.hour <= 17,
                "is_unusual_hours": timestamp.hour < 6 or timestamp.hour > 22,
                "source_ip": event_data.get("source_ip", ""),
                "user_agent": event_data.get("user_agent", ""),
                "endpoint": event_data.get("endpoint", ""),
                "method": event_data.get("method", ""),
                "status_code": event_data.get("status_code", 200),
                "response_time": event_data.get("response_time", 0),
                "content_length": event_data.get("content_length", 0)
            })
            
            # Calculate derived features
            features.update({
                "ip_risk_score": self.calculate_ip_risk(features["source_ip"]),
                "user_agent_risk": self.calculate_user_agent_risk(features["user_agent"]),
                "endpoint_risk": self.calculate_endpoint_risk(features["endpoint"])
            })
            
        except Exception as e:
            self.logger.error(f"Error extracting features: {str(e)}")
        
        return features
    
    def get_or_create_profile(self, user_id: str, event_data: Dict[str, Any], features: Dict[str, Any]) -> BehaviorProfile:
        """Get or create user behavior profile"""
        if user_id not in self.user_profiles:
            profile = BehaviorProfile(
                user_id=user_id,
                source_ip=event_data.get("source_ip", ""),
                session_id=event_data.get("session_id", ""),
                created_at=datetime.now(),
                last_updated=datetime.now(),
                features=features,
                risk_score=0.0,
                anomaly_count=0,
                baseline_established=False
            )
            self.user_profiles[user_id] = profile
            self.stats["total_users"] += 1
        else:
            profile = self.user_profiles[user_id]
        
        return profile
    
    def update_profile(self, profile: BehaviorProfile, features: Dict[str, Any]):
        """Update user behavior profile"""
        try:
            # Update feature history
            for key, value in features.items():
                if key not in profile.features:
                    profile.features[key] = []
                if isinstance(profile.features[key], list):
                    profile.features[key].append(value)
                    # Keep only last 100 values
                    if len(profile.features[key]) > 100:
                        profile.features[key] = profile.features[key][-100:]
                else:
                    profile.features[key] = value
            
            # Update profile metadata
            profile.last_updated = datetime.now()
            
            # Check if baseline is established
            min_sessions = self.config["behavioral_analytics"]["profiling"]["min_sessions_for_baseline"]
            if not profile.baseline_established:
                session_count = len(profile.features.get("hour_of_day", []))
                if session_count >= min_sessions:
                    profile.baseline_established = True
                    self.stats["baseline_profiles"] += 1
                    self.logger.info(f"Baseline established for user {profile.user_id}")
            
            # Calculate risk score
            profile.risk_score = self.calculate_profile_risk(profile)
            
        except Exception as e:
            self.logger.error(f"Error updating profile: {str(e)}")
    
    def check_anomaly_rules(self, profile: BehaviorProfile, features: Dict[str, Any]) -> List[AnomalyEvent]:
        """Check for anomalies using rule-based detection"""
        anomalies = []
        
        try:
            for rule_name, rule in self.anomaly_rules.items():
                try:
                    anomaly = rule.check(profile, features)
                    if anomaly:
                        anomaly.anomaly_id = self.generate_anomaly_id()
                        anomalies.append(anomaly)
                except Exception as e:
                    self.logger.error(f"Error in rule {rule_name}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error checking anomaly rules: {str(e)}")
        
        return anomalies
    
    def calculate_ip_risk(self, source_ip: str) -> float:
        """Calculate IP risk score"""
        if not source_ip:
            return 0.5
        
        if source_ip.startswith("192.168.") or source_ip.startswith("10."):
            return 0.1  # Internal IP
        elif source_ip.startswith("172."):
            return 0.2  # Private IP
        else:
            return 0.3  # External IP
    
    def calculate_user_agent_risk(self, user_agent: str) -> float:
        """Calculate user agent risk score"""
        if not user_agent:
            return 0.5
        elif any(bot in user_agent.lower() for bot in ["bot", "crawler", "spider"]):
            return 0.4
        elif any(tool in user_agent.lower() for tool in ["curl", "wget", "python"]):
            return 0.3
        else:
            return 0.1
    
    def calculate_endpoint_risk(self, endpoint: str) -> float:
        """Calculate endpoint risk score"""
        if not endpoint:
            return 0.0
        
        high_risk_endpoints = ["/admin", "/config", "/system", "/root", "/api/keys"]
        for risky in high_risk_endpoints:
            if risky in endpoint.lower():
                return 0.6
        
        medium_risk_endpoints = ["/api", "/auth", "/user"]
        for medium in medium_risk_endpoints:
            if medium in endpoint.lower():
                return 0.3
        
        return 0.1
    
    def calculate_profile_risk(self, profile: BehaviorProfile) -> float:
        """Calculate overall profile risk score"""
        risk = 0.0
        
        try:
            # Anomaly count
            if profile.anomaly_count > 10:
                risk += 0.4
            elif profile.anomaly_count > 5:
                risk += 0.2
            elif profile.anomaly_count > 0:
                risk += 0.1
            
            # Recent anomalies
            recent_anomalies = sum(1 for a in self.anomaly_events 
                                 if a.user_id == profile.user_id 
                                 and (datetime.now() - a.timestamp).days <= 7)
            
            if recent_anomalies > 5:
                risk += 0.3
            elif recent_anomalies > 2:
                risk += 0.1
            
        except Exception as e:
            self.logger.error(f"Error calculating profile risk: {str(e)}")
        
        return min(risk, 1.0)
    
    def generate_anomaly_id(self) -> str:
        """Generate unique anomaly ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_hash = hashlib.md5(f"{timestamp}{os.urandom(8)}".encode()).hexdigest()[:8]
        return f"ANOMALY-{timestamp}-{random_hash}"
    
    def respond_to_anomaly(self, anomaly: AnomalyEvent) -> Dict[str, Any]:
        """Respond to detected anomaly"""
        response = {
            "anomaly_id": anomaly.anomaly_id,
            "actions_taken": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Log anomaly
            self.log_anomaly(anomaly)
            response["actions_taken"].append("ANOMALY_LOGGED")
            
            # Alert security team if high severity
            if anomaly.severity in ["HIGH", "CRITICAL"]:
                self.alert_security_team(anomaly)
                response["actions_taken"].append("SECURITY_TEAM_ALERTED")
            
            self.logger.info(f"Anomaly response completed for {anomaly.anomaly_id}")
            
        except Exception as e:
            self.logger.error(f"Error responding to anomaly: {str(e)}")
        
        return response
    
    def log_anomaly(self, anomaly: AnomalyEvent):
        """Log anomaly event"""
        anomaly_log = {
            "anomaly_id": anomaly.anomaly_id,
            "timestamp": anomaly.timestamp.isoformat(),
            "user_id": anomaly.user_id,
            "source_ip": anomaly.source_ip,
            "session_id": anomaly.session_id,
            "anomaly_type": anomaly.anomaly_type,
            "severity": anomaly.severity,
            "confidence": anomaly.confidence,
            "description": anomaly.description,
            "features": anomaly.features
        }
        
        # Store anomaly event
        self.anomaly_events.append(anomaly_log)
        
        # Save to file
        anomaly_log_file = os.path.join(self.production_path, "logs/behavioral_anomalies.json")
        try:
            if os.path.exists(anomaly_log_file):
                with open(anomaly_log_file, 'r') as f:
                    anomalies = json.load(f)
            else:
                anomalies = []
            
            anomalies.append(anomaly_log)
            
            # Keep only last 1000 anomalies
            if len(anomalies) > 1000:
                anomalies = anomalies[-1000:]
            
            with open(anomaly_log_file, 'w') as f:
                json.dump(anomalies, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error logging anomaly: {str(e)}")
    
    def alert_security_team(self, anomaly: AnomalyEvent):
        """Alert security team about anomaly"""
        alert_data = {
            "alert_type": "BEHAVIORAL_ANOMALY",
            "anomaly_id": anomaly.anomaly_id,
            "severity": anomaly.severity,
            "user_id": anomaly.user_id,
            "source_ip": anomaly.source_ip,
            "anomaly_type": anomaly.anomaly_type,
            "confidence": anomaly.confidence,
            "description": anomaly.description,
            "timestamp": anomaly.timestamp.isoformat()
        }
        
        # Log alert
        self.logger.warning(f"BEHAVIORAL ANOMALY ALERT: {json.dumps(alert_data)}")
    
    def get_analytics_statistics(self) -> Dict[str, Any]:
        """Get behavioral analytics statistics"""
        return {
            "statistics": self.stats,
            "profile_summary": self.get_profile_summary(),
            "anomaly_summary": self.get_anomaly_summary(),
            "recent_anomalies": self.get_recent_anomalies()
        }
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """Get profile summary statistics"""
        total_profiles = len(self.user_profiles)
        baseline_profiles = sum(1 for p in self.user_profiles.values() if p.baseline_established)
        high_risk_profiles = sum(1 for p in self.user_profiles.values() if p.risk_score > 0.7)
        
        return {
            "total_profiles": total_profiles,
            "baseline_profiles": baseline_profiles,
            "high_risk_profiles": high_risk_profiles,
            "baseline_percentage": (baseline_profiles / total_profiles * 100) if total_profiles > 0 else 0
        }
    
    def get_anomaly_summary(self) -> Dict[str, Any]:
        """Get anomaly summary statistics"""
        if not self.anomaly_events:
            return {"total_anomalies": 0}
        
        anomaly_types = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for anomaly in self.anomaly_events:
            anomaly_types[anomaly["anomaly_type"]] += 1
            severity_counts[anomaly["severity"]] += 1
        
        return {
            "total_anomalies": len(self.anomaly_events),
            "anomaly_types": dict(anomaly_types),
            "severity_distribution": dict(severity_counts)
        }
    
    def get_recent_anomalies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent anomalies"""
        return self.anomaly_events[-limit:] if self.anomaly_events else []

    def check_ml_anomalies(self, profile: BehaviorProfile, features: Dict[str, Any]) -> List[AnomalyEvent]:
        """Check for anomalies using machine learning models"""
        anomalies = []
        
        try:
            # Statistical anomaly detection
            if self.config["behavioral_analytics"]["models"]["statistical"]["enabled"]:
                try:
                    anomaly = self.models["statistical"].detect(profile, features)
                    if anomaly:
                        anomalies.append(anomaly)
                except Exception as e:
                    self.logger.error(f"Error in statistical anomaly detection: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Error in ML anomaly detection: {str(e)}")
        
        return None

# Statistical Anomaly Detector
class StatisticalAnomalyDetector:
    """Statistical anomaly detection using z-scores"""
    
    def detect(self, profile: BehaviorProfile, features: Dict[str, Any]) -> Optional[AnomalyEvent]:
        """Detect anomalies using statistical methods"""
        if not profile.baseline_established:
            return None
        
        # Check response time anomaly
        response_time = features.get("response_time", 0)
        response_times = profile.features.get("response_time", [])
        
        if response_times and len(response_times) > 5:
            mean_rt = sum(response_times) / len(response_times)
            variance_rt = sum((x - mean_rt) ** 2 for x in response_times) / len(response_times)
            std_rt = math.sqrt(variance_rt)
            
            if std_rt > 0:
                z_score = abs(response_time - mean_rt) / std_rt
                if z_score > 3.0:  # 3 standard deviations
                    return AnomalyEvent(
                        timestamp=datetime.now(),
                        user_id=profile.user_id,
                        source_ip=profile.source_ip,
                        session_id=profile.session_id,
                        anomaly_type="statistical_response_time",
                        severity="MEDIUM",
                        confidence=min(z_score / 3.0, 1.0),
                        description=f"Unusual response time: {response_time}ms (z-score: {z_score:.2f})",
                        features=features,
                        anomaly_id=""
                    )
        
        return None

# Anomaly Detection Rules
class UnusualAccessTimeRule:
    """Detect unusual access times"""
    
    def check(self, profile: BehaviorProfile, features: Dict[str, Any]) -> Optional[AnomalyEvent]:
        """Check for unusual access time"""
        if not profile.baseline_established:
            return None
        
        hour = features.get("hour_of_day", 12)
        is_unusual = features.get("is_unusual_hours", False)
        
        # Check if user normally accesses at this time
        access_hours = profile.features.get("hour_of_day", [])
        if access_hours and len(access_hours) > 5:
            hour_frequency = access_hours.count(hour) / len(access_hours)
            if hour_frequency < 0.05 and is_unusual:  # Less than 5% of accesses at this hour
                return AnomalyEvent(
                    timestamp=datetime.now(),
                    user_id=profile.user_id,
                    source_ip=profile.source_ip,
                    session_id=profile.session_id,
                    anomaly_type="unusual_access_time",
                    severity="MEDIUM",
                    confidence=0.7,
                    description=f"User accessing system at unusual hour: {hour}:00",
                    features=features,
                    anomaly_id=""
                )
        
        return None

class AbnormalRequestPatternRule:
    """Detect abnormal request patterns"""
    
    def check(self, profile: BehaviorProfile, features: Dict[str, Any]) -> Optional[AnomalyEvent]:
        """Check for abnormal request patterns"""
        if not profile.baseline_established:
            return None
        
        # Check for high error rate
        status_code = features.get("status_code", 200)
        if status_code >= 400:
            error_history = profile.features.get("status_code", [])
            recent_errors = sum(1 for code in error_history[-10:] if code >= 400)
            
            if recent_errors > 5:  # More than 5 errors in last 10 requests
                return AnomalyEvent(
                    timestamp=datetime.now(),
                    user_id=profile.user_id,
                    source_ip=profile.source_ip,
                    session_id=profile.session_id,
                    anomaly_type="abnormal_request_pattern",
                    severity="HIGH",
                    confidence=0.8,
                    description=f"High error rate detected: {recent_errors}/10 recent requests",
                    features=features,
                    anomaly_id=""
                )
        
        return None

class SuspiciousGeolocationRule:
    """Detect suspicious geolocation patterns"""
    
    def check(self, profile: BehaviorProfile, features: Dict[str, Any]) -> Optional[AnomalyEvent]:
        """Check for suspicious geolocation"""
        source_ip = features.get("source_ip", "")
        
        # Check for multiple IPs in short time (simplified)
        if source_ip != profile.source_ip and profile.source_ip:
            return AnomalyEvent(
                timestamp=datetime.now(),
                user_id=profile.user_id,
                source_ip=source_ip,
                session_id=profile.session_id,
                anomaly_type="suspicious_geolocation",
                severity="HIGH",
                confidence=0.7,
                description=f"User accessing from different IP: {source_ip} (usual: {profile.source_ip})",
                features=features,
                anomaly_id=""
            )
        
        return None

class HighErrorRateRule:
    """Detect high error rates"""
    
    def check(self, profile: BehaviorProfile, features: Dict[str, Any]) -> Optional[AnomalyEvent]:
        """Check for high error rates"""
        status_code = features.get("status_code", 200)
        
        if status_code >= 500:  # Server error
            return AnomalyEvent(
                timestamp=datetime.now(),
                user_id=profile.user_id,
                source_ip=profile.source_ip,
                session_id=profile.session_id,
                anomaly_type="high_error_rate",
                severity="MEDIUM",
                confidence=0.6,
                description=f"Server error detected: {status_code}",
                features=features,
                anomaly_id=""
            )
        
        return None

class AtypicalUserAgentRule:
    """Detect atypical user agent patterns"""
    
    def check(self, profile: BehaviorProfile, features: Dict[str, Any]) -> Optional[AnomalyEvent]:
        """Check for atypical user agent"""
        user_agent = features.get("user_agent", "")
        user_agent_risk = features.get("user_agent_risk", 0)
        
        if user_agent_risk > 0.5:  # High risk user agent
            return AnomalyEvent(
                timestamp=datetime.now(),
                user_id=profile.user_id,
                source_ip=profile.source_ip,
                session_id=profile.session_id,
                anomaly_type="atypical_user_agent",
                severity="MEDIUM",
                confidence=0.6,
                description=f"Suspicious user agent detected: {user_agent[:100]}",
                features=features,
                anomaly_id=""
            )
        
        return None

def main():
    """Main function to test behavioral analytics"""
    analytics = BehavioralAnalytics()
    
    # Test with sample events
    test_events = [
        {
            "user_id": "user123",
            "source_ip": "192.168.1.100",
            "session_id": "session_001",
            "endpoint": "/api/user/profile",
            "method": "GET",
            "status_code": 200,
            "response_time": 150,
            "content_length": 1024,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        {
            "user_id": "user123",
            "source_ip": "10.0.0.50",  # Different IP
            "session_id": "session_002",
            "endpoint": "/api/admin/config",
            "method": "POST",
            "status_code": 500,  # Server error
            "response_time": 5000,
            "content_length": 2048,
            "user_agent": "curl/7.68.0"  # Suspicious user agent
        },
        {
            "user_id": "user456",
            "source_ip": "203.0.113.1",
            "session_id": "session_003",
            "endpoint": "/api/login",
            "method": "POST",
            "status_code": 401,
            "response_time": 200,
            "content_length": 512,
            "user_agent": "python-requests/2.25.1"
        }
    ]
    
    print("🧠 STELLAR LOGIC AI - BEHAVIORAL ANALYTICS FOR ANOMALY DETECTION")
    print("=" * 70)
    
    for i, event in enumerate(test_events, 1):
        print(f"\n📊 Analyzing Event {i}:")
        anomalies = analytics.analyze_behavior(event)
        
        if anomalies:
            print(f"🚨 {len(anomalies)} anomaly(ies) detected:")
            for anomaly in anomalies:
                print(f"   - {anomaly.anomaly_type}: {anomaly.severity} (confidence: {anomaly.confidence:.2f})")
                print(f"     Description: {anomaly.description}")
                response = analytics.respond_to_anomaly(anomaly)
                print(f"     Actions taken: {', '.join(response['actions_taken'])}")
        else:
            print("✅ No anomalies detected")
    
    # Display statistics
    stats = analytics.get_analytics_statistics()
    print(f"\n📈 Behavioral Analytics Statistics:")
    print(f"   Total sessions: {stats['statistics']['total_sessions']}")
    print(f"   Total users: {stats['statistics']['total_users']}")
    print(f"   Anomalies detected: {stats['statistics']['anomalies_detected']}")
    print(f"   Baseline profiles: {stats['statistics']['baseline_profiles']}")
    
    profile_summary = stats['profile_summary']
    print(f"   Profile baseline percentage: {profile_summary['baseline_percentage']:.1f}%")
    
    anomaly_summary = stats['anomaly_summary']
    if anomaly_summary['total_anomalies'] > 0:
        print(f"   Anomaly types: {list(anomaly_summary['anomaly_types'].keys())}")
    
    print(f"\n🎯 Behavioral Analytics System is operational!")

if __name__ == "__main__":
    main()
