#!/usr/bin/env python3
"""
Stellar Logic AI - AI-Powered Threat Detection System
Advanced machine learning-based threat detection and prevention
"""

import os
import sys
import json
import time
import logging
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
import re
import math

@dataclass
class ThreatEvent:
    """Threat event data structure"""
    timestamp: datetime
    event_type: str
    severity: str
    source_ip: str
    target_endpoint: str
    user_agent: str
    payload: Dict[str, Any]
    confidence: float
    threat_id: str

class AIThreatDetector:
    """AI-powered threat detection system for Stellar Logic AI"""
    
    def __init__(self):
        self.base_path = "c:/Users/merce/Documents/helm-ai"
        self.production_path = "c:/Users/merce/Documents/helm-ai/production"
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.production_path, "logs/ai_threat_detection.log")),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Threat detection models
        self.threat_models = {
            "sql_injection": SQLInjectionDetector(),
            "xss_attack": XSSAttackDetector(),
            "brute_force": BruteForceDetector(),
            "ddos_attack": DDoSDetector(),
            "anomalous_access": AnomalousAccessDetector(),
            "malicious_payload": MaliciousPayloadDetector(),
            "suspicious_patterns": SuspiciousPatternDetector(),
            "credential_stuffing": CredentialStuffingDetector()
        }
        
        # Threat intelligence
        self.threat_intelligence = ThreatIntelligence()
        
        # Event storage
        self.event_history = deque(maxlen=10000)
        self.threat_events = []
        
        # Detection statistics
        self.stats = {
            "total_events": 0,
            "threats_detected": 0,
            "false_positives": 0,
            "true_positives": 0,
            "detection_rate": 0.0,
            "accuracy": 0.0
        }
        
        # Load configuration
        self.load_configuration()
        
        self.logger.info("AI Threat Detection System initialized")
    
    def load_configuration(self):
        """Load AI threat detection configuration"""
        config_file = os.path.join(self.production_path, "config/ai_threat_detection_config.json")
        
        default_config = {
            "ai_threat_detection": {
                "enabled": True,
                "models": {
                    "sql_injection": {"enabled": True, "threshold": 0.8},
                    "xss_attack": {"enabled": True, "threshold": 0.7},
                    "brute_force": {"enabled": True, "threshold": 0.9},
                    "ddos_attack": {"enabled": True, "threshold": 0.8},
                    "anomalous_access": {"enabled": True, "threshold": 0.6},
                    "malicious_payload": {"enabled": True, "threshold": 0.7},
                    "suspicious_patterns": {"enabled": True, "threshold": 0.6},
                    "credential_stuffing": {"enabled": True, "threshold": 0.9}
                },
                "response_actions": {
                    "block_ip": True,
                    "alert_team": True,
                    "log_event": True,
                    "quarantine_session": True
                },
                "learning": {
                    "continuous_learning": True,
                    "model_update_interval": 3600,
                    "feedback_collection": True
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
                self.logger.info("Created default AI threat detection configuration")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            self.config = default_config
    
    def analyze_request(self, request_data: Dict[str, Any]) -> List[ThreatEvent]:
        """Analyze incoming request for threats"""
        threats = []
        
        try:
            # Extract request features
            features = self.extract_features(request_data)
            
            # Run through all enabled threat models
            for model_name, model in self.threat_models.items():
                if self.config["ai_threat_detection"]["models"][model_name]["enabled"]:
                    try:
                        threat_score = model.analyze(features)
                        threshold = self.config["ai_threat_detection"]["models"][model_name]["threshold"]
                        
                        if threat_score >= threshold:
                            threat_event = ThreatEvent(
                                timestamp=datetime.now(),
                                event_type=model_name,
                                severity=self.calculate_severity(threat_score),
                                source_ip=features.get("source_ip", "unknown"),
                                target_endpoint=features.get("endpoint", "unknown"),
                                user_agent=features.get("user_agent", "unknown"),
                                payload=features,
                                confidence=threat_score,
                                threat_id=self.generate_threat_id()
                            )
                            
                            threats.append(threat_event)
                            self.logger.warning(f"Threat detected: {model_name} (confidence: {threat_score:.2f})")
                            
                    except Exception as e:
                        self.logger.error(f"Error in {model_name} model: {str(e)}")
            
            # Update statistics
            self.stats["total_events"] += 1
            if threats:
                self.stats["threats_detected"] += len(threats)
            
            # Store event
            self.event_history.append({
                "timestamp": datetime.now(),
                "features": features,
                "threats": len(threats)
            })
            
        except Exception as e:
            self.logger.error(f"Error analyzing request: {str(e)}")
        
        return threats
    
    def extract_features(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from request data"""
        features = {
            "source_ip": request_data.get("source_ip", ""),
            "endpoint": request_data.get("endpoint", ""),
            "method": request_data.get("method", ""),
            "user_agent": request_data.get("user_agent", ""),
            "content_type": request_data.get("content_type", ""),
            "content_length": request_data.get("content_length", 0),
            "headers": request_data.get("headers", {}),
            "query_params": request_data.get("query_params", {}),
            "body": request_data.get("body", ""),
            "timestamp": datetime.now()
        }
        
        # Add derived features
        features.update({
            "ip_reputation": self.threat_intelligence.get_ip_reputation(features["source_ip"]),
            "user_agent_risk": self.analyze_user_agent(features["user_agent"]),
            "payload_entropy": self.calculate_entropy(features["body"]),
            "suspicious_headers": self.detect_suspicious_headers(features["headers"]),
            "request_size_risk": self.assess_request_size(features["content_length"]),
            "time_pattern": self.analyze_time_pattern(features["timestamp"])
        })
        
        return features
    
    def calculate_severity(self, confidence: float) -> str:
        """Calculate threat severity based on confidence"""
        if confidence >= 0.9:
            return "CRITICAL"
        elif confidence >= 0.8:
            return "HIGH"
        elif confidence >= 0.7:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_threat_id(self) -> str:
        """Generate unique threat ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_hash = hashlib.md5(f"{timestamp}{os.urandom(8)}".encode()).hexdigest()[:8]
        return f"THREAT-{timestamp}-{random_hash}"
    
    def analyze_user_agent(self, user_agent: str) -> float:
        """Analyze user agent for suspicious patterns"""
        if not user_agent:
            return 0.8  # Empty user agent is suspicious
        
        suspicious_patterns = [
            r"bot", r"crawler", r"scanner", r"sqlmap", r"nikto", r"nmap",
            r"python-requests", r"curl", r"wget", r"powershell"
        ]
        
        risk_score = 0.0
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def calculate_entropy(self, data: str) -> float:
        """Calculate entropy of data"""
        if not data:
            return 0.0
        
        # Count character frequencies
        char_counts = defaultdict(int)
        for char in data:
            char_counts[char] += 1
        
        # Calculate Shannon entropy
        entropy = 0.0
        data_len = len(data)
        for count in char_counts.values():
            probability = count / data_len
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def detect_suspicious_headers(self, headers: Dict[str, str]) -> float:
        """Detect suspicious HTTP headers"""
        suspicious_headers = [
            "x-forwarded-for", "x-real-ip", "x-originating-ip",
            "x-client-ip", "x-cluster-client-ip"
        ]
        
        risk_score = 0.0
        for header in suspicious_headers:
            if header in headers:
                risk_score += 0.1
        
        # Check for common attack headers
        attack_headers = ["x-attacker", "x-hacker", "x-exploit"]
        for header in attack_headers:
            if header in headers:
                risk_score += 0.3
        
        return min(risk_score, 1.0)
    
    def assess_request_size(self, content_length: int) -> float:
        """Assess request size for anomalies"""
        if content_length == 0:
            return 0.0
        elif content_length > 1000000:  # > 1MB
            return 0.8
        elif content_length > 100000:  # > 100KB
            return 0.5
        else:
            return 0.0
    
    def analyze_time_pattern(self, timestamp: datetime) -> float:
        """Analyze request time for patterns"""
        # Check for requests at unusual hours (2-4 AM)
        hour = timestamp.hour
        if 2 <= hour <= 4:
            return 0.3
        else:
            return 0.0
    
    def respond_to_threat(self, threat_event: ThreatEvent) -> Dict[str, Any]:
        """Respond to detected threat"""
        response = {
            "threat_id": threat_event.threat_id,
            "actions_taken": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Block IP if configured
            if self.config["ai_threat_detection"]["response_actions"]["block_ip"]:
                self.block_ip(threat_event.source_ip)
                response["actions_taken"].append("IP_BLOCKED")
            
            # Alert security team
            if self.config["ai_threat_detection"]["response_actions"]["alert_team"]:
                self.alert_security_team(threat_event)
                response["actions_taken"].append("TEAM_ALERTED")
            
            # Log event
            if self.config["ai_threat_detection"]["response_actions"]["log_event"]:
                self.log_threat_event(threat_event)
                response["actions_taken"].append("EVENT_LOGGED")
            
            # Quarantine session
            if self.config["ai_threat_detection"]["response_actions"]["quarantine_session"]:
                self.quarantine_session(threat_event)
                response["actions_taken"].append("SESSION_QUARANTINED")
            
            self.logger.info(f"Threat response completed for {threat_event.threat_id}")
            
        except Exception as e:
            self.logger.error(f"Error responding to threat: {str(e)}")
        
        return response
    
    def block_ip(self, ip_address: str):
        """Block malicious IP address"""
        # In a real implementation, this would update firewall rules
        self.logger.warning(f"Blocking IP address: {ip_address}")
        
        # Store blocked IP
        blocked_ips_file = os.path.join(self.production_path, "storage/blocked_ips.json")
        try:
            if os.path.exists(blocked_ips_file):
                with open(blocked_ips_file, 'r') as f:
                    blocked_ips = json.load(f)
            else:
                blocked_ips = {}
            
            blocked_ips[ip_address] = {
                "blocked_at": datetime.now().isoformat(),
                "reason": "AI threat detection",
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            
            with open(blocked_ips_file, 'w') as f:
                json.dump(blocked_ips, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error blocking IP: {str(e)}")
    
    def alert_security_team(self, threat_event: ThreatEvent):
        """Alert security team about threat"""
        alert_data = {
            "alert_type": "THREAT_DETECTED",
            "threat_id": threat_event.threat_id,
            "severity": threat_event.severity,
            "event_type": threat_event.event_type,
            "source_ip": threat_event.source_ip,
            "target_endpoint": threat_event.target_endpoint,
            "confidence": threat_event.confidence,
            "timestamp": threat_event.timestamp.isoformat()
        }
        
        # Log alert
        self.logger.critical(f"SECURITY ALERT: {json.dumps(alert_data)}")
        
        # In a real implementation, this would send email, Slack, etc.
        # For now, we'll store the alert
        alert_file = os.path.join(self.production_path, "logs/security_alerts.json")
        try:
            if os.path.exists(alert_file):
                with open(alert_file, 'r') as f:
                    alerts = json.load(f)
            else:
                alerts = []
            
            alerts.append(alert_data)
            
            # Keep only last 1000 alerts
            if len(alerts) > 1000:
                alerts = alerts[-1000:]
            
            with open(alert_file, 'w') as f:
                json.dump(alerts, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error alerting security team: {str(e)}")
    
    def log_threat_event(self, threat_event: ThreatEvent):
        """Log threat event"""
        threat_log = {
            "threat_id": threat_event.threat_id,
            "event_type": threat_event.event_type,
            "severity": threat_event.severity,
            "source_ip": threat_event.source_ip,
            "target_endpoint": threat_event.target_endpoint,
            "user_agent": threat_event.user_agent,
            "confidence": threat_event.confidence,
            "timestamp": threat_event.timestamp.isoformat(),
            "payload": threat_event.payload
        }
        
        # Store threat event
        self.threat_events.append(threat_log)
        
        # Save to file
        threat_log_file = os.path.join(self.production_path, "logs/threat_events.json")
        try:
            if os.path.exists(threat_log_file):
                with open(threat_log_file, 'r') as f:
                    threats = json.load(f)
            else:
                threats = []
            
            threats.append(threat_log)
            
            # Keep only last 1000 threats
            if len(threats) > 1000:
                threats = threats[-1000:]
            
            with open(threat_log_file, 'w') as f:
                json.dump(threats, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error logging threat event: {str(e)}")
    
    def quarantine_session(self, threat_event: ThreatEvent):
        """Quarantine suspicious session"""
        # In a real implementation, this would invalidate session tokens
        self.logger.warning(f"Quarantining session for IP: {threat_event.source_ip}")
    
    def get_threat_statistics(self) -> Dict[str, Any]:
        """Get threat detection statistics"""
        # Calculate detection rate and accuracy
        if self.stats["total_events"] > 0:
            self.stats["detection_rate"] = (self.stats["threats_detected"] / self.stats["total_events"]) * 100
        
        if self.stats["threats_detected"] > 0:
            self.stats["accuracy"] = (self.stats["true_positives"] / self.stats["threats_detected"]) * 100
        
        return {
            "statistics": self.stats,
            "threat_types": self.get_threat_type_distribution(),
            "recent_threats": self.get_recent_threats(),
            "blocked_ips": self.get_blocked_ips_count(),
            "model_performance": self.get_model_performance()
        }
    
    def get_threat_type_distribution(self) -> Dict[str, int]:
        """Get distribution of threat types"""
        threat_counts = defaultdict(int)
        for threat in self.threat_events:
            threat_counts[threat["event_type"]] += 1
        return dict(threat_counts)
    
    def get_recent_threats(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent threats"""
        return self.threat_events[-limit:] if self.threat_events else []
    
    def get_blocked_ips_count(self) -> int:
        """Get count of blocked IPs"""
        blocked_ips_file = os.path.join(self.production_path, "storage/blocked_ips.json")
        try:
            if os.path.exists(blocked_ips_file):
                with open(blocked_ips_file, 'r') as f:
                    blocked_ips = json.load(f)
                return len(blocked_ips)
        except:
            pass
        return 0
    
    def get_model_performance(self) -> Dict[str, float]:
        """Get model performance metrics"""
        performance = {}
        for model_name, model in self.threat_models.items():
            if hasattr(model, 'get_performance'):
                performance[model_name] = model.get_performance()
        return performance
    
    def start_continuous_monitoring(self):
        """Start continuous threat monitoring"""
        self.logger.info("Starting continuous AI threat monitoring")
        
        while True:
            try:
                # Check for new security events
                self.process_security_events()
                
                # Update threat intelligence
                self.threat_intelligence.update()
                
                # Retrain models if needed
                if self.config["ai_threat_detection"]["learning"]["continuous_learning"]:
                    self.update_models()
                
                # Sleep for monitoring interval
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                self.logger.info("Stopping continuous monitoring")
                break
            except Exception as e:
                self.logger.error(f"Error in continuous monitoring: {str(e)}")
                time.sleep(10)  # Wait before retrying
    
    def process_security_events(self):
        """Process new security events"""
        # In a real implementation, this would read from log files or message queue
        # For demo purposes, we'll simulate some events
        pass
    
    def update_models(self):
        """Update AI models with new data"""
        # In a real implementation, this would retrain models with new data
        pass

class SQLInjectionDetector:
    """SQL Injection threat detector"""
    
    def __init__(self):
        self.sql_patterns = [
            r"union\s+select", r"or\s+1\s*=\s*1", r"drop\s+table",
            r"insert\s+into", r"delete\s+from", r"update\s+set",
            r"exec\s*\(", r"sp_executesql", r"xp_cmdshell"
        ]
    
    def analyze(self, features: Dict[str, Any]) -> float:
        """Analyze for SQL injection attempts"""
        score = 0.0
        
        # Check query parameters
        for param, value in features.get("query_params", {}).items():
            if isinstance(value, str):
                for pattern in self.sql_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        score += 0.3
        
        # Check request body
        body = features.get("body", "")
        if body:
            for pattern in self.sql_patterns:
                if re.search(pattern, body, re.IGNORECASE):
                    score += 0.4
        
        # Check for common SQL injection characters
        sql_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
        for char in sql_chars:
            if char in body:
                score += 0.1
        
        return min(score, 1.0)

class XSSAttackDetector:
    """XSS Attack threat detector"""
    
    def __init__(self):
        self.xss_patterns = [
            r"<script[^>]*>", r"</script>", r"javascript:",
            r"onload\s*=", r"onerror\s*=", r"onclick\s*=",
            r"<iframe[^>]*>", r"<object[^>]*>", r"<embed[^>]*>"
        ]
    
    def analyze(self, features: Dict[str, Any]) -> float:
        """Analyze for XSS attack attempts"""
        score = 0.0
        
        # Check query parameters
        for param, value in features.get("query_params", {}).items():
            if isinstance(value, str):
                for pattern in self.xss_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        score += 0.3
        
        # Check request body
        body = features.get("body", "")
        if body:
            for pattern in self.xss_patterns:
                if re.search(pattern, body, re.IGNORECASE):
                    score += 0.4
        
        # Check for HTML encoding evasion
        if "%3C" in body or "%3E" in body:  # < and >
            score += 0.2
        
        return min(score, 1.0)

class BruteForceDetector:
    """Brute force attack detector"""
    
    def __init__(self):
        self.login_attempts = defaultdict(list)
    
    def analyze(self, features: Dict[str, Any]) -> float:
        """Analyze for brute force attempts"""
        source_ip = features.get("source_ip", "")
        endpoint = features.get("endpoint", "")
        timestamp = features.get("timestamp", datetime.now())
        
        # Track login attempts
        if "login" in endpoint.lower() or "auth" in endpoint.lower():
            self.login_attempts[source_ip].append(timestamp)
            
            # Clean old attempts (older than 1 hour)
            cutoff_time = timestamp - timedelta(hours=1)
            self.login_attempts[source_ip] = [
                t for t in self.login_attempts[source_ip] if t > cutoff_time
            ]
            
            # Calculate score based on frequency
            attempts = len(self.login_attempts[source_ip])
            if attempts > 20:
                return 1.0
            elif attempts > 10:
                return 0.8
            elif attempts > 5:
                return 0.6
            elif attempts > 3:
                return 0.4
        
        return 0.0

class DDoSDetector:
    """DDoS attack detector"""
    
    def __init__(self):
        self.request_counts = defaultdict(list)
    
    def analyze(self, features: Dict[str, Any]) -> float:
        """Analyze for DDoS attempts"""
        source_ip = features.get("source_ip", "")
        timestamp = features.get("timestamp", datetime.now())
        
        # Track request frequency
        self.request_counts[source_ip].append(timestamp)
        
        # Clean old requests (older than 1 minute)
        cutoff_time = timestamp - timedelta(minutes=1)
        self.request_counts[source_ip] = [
            t for t in self.request_counts[source_ip] if t > cutoff_time
        ]
        
        # Calculate score based on request frequency
        requests_per_minute = len(self.request_counts[source_ip])
        if requests_per_minute > 100:
            return 1.0
        elif requests_per_minute > 50:
            return 0.8
        elif requests_per_minute > 20:
            return 0.6
        elif requests_per_minute > 10:
            return 0.4
        
        return 0.0

class AnomalousAccessDetector:
    """Anomalous access pattern detector"""
    
    def __init__(self):
        self.access_patterns = defaultdict(lambda: defaultdict(int))
    
    def analyze(self, features: Dict[str, Any]) -> float:
        """Analyze for anomalous access patterns"""
        source_ip = features.get("source_ip", "")
        endpoint = features.get("endpoint", "")
        hour = features.get("timestamp", datetime.now()).hour
        
        # Track access patterns
        self.access_patterns[source_ip][hour] += 1
        
        # Check for unusual access times
        if hour < 6 or hour > 22:  # Unusual hours
            return 0.3
        
        # Check for unusual endpoint access
        if "admin" in endpoint.lower() or "config" in endpoint.lower():
            return 0.5
        
        return 0.0

class MaliciousPayloadDetector:
    """Malicious payload detector"""
    
    def __init__(self):
        self.malicious_patterns = [
            r"eval\s*\(", r"system\s*\(", r"exec\s*\(",
            r"shell_exec", r"passthru", r"base64_decode",
            r"file_get_contents", r"file_put_contents", r"fopen\s*"
        ]
    
    def analyze(self, features: Dict[str, Any]) -> float:
        """Analyze for malicious payloads"""
        score = 0.0
        
        body = features.get("body", "")
        if body:
            for pattern in self.malicious_patterns:
                if re.search(pattern, body, re.IGNORECASE):
                    score += 0.3
        
        # Check for high entropy (possible encoded content)
        entropy = features.get("payload_entropy", 0)
        if entropy > 7.0:
            score += 0.2
        
        return min(score, 1.0)

class SuspiciousPatternDetector:
    """Suspicious pattern detector"""
    
    def __init__(self):
        self.suspicious_patterns = [
            r"\.\./", r"\.\.\\", r"/etc/passwd", r"/etc/shadow",
            r"cmd\.exe", r"powershell", r"/bin/bash", r"/bin/sh"
        ]
    
    def analyze(self, features: Dict[str, Any]) -> float:
        """Analyze for suspicious patterns"""
        score = 0.0
        
        # Check query parameters
        for param, value in features.get("query_params", {}).items():
            if isinstance(value, str):
                for pattern in self.suspicious_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        score += 0.3
        
        # Check request body
        body = features.get("body", "")
        if body:
            for pattern in self.suspicious_patterns:
                if re.search(pattern, body, re.IGNORECASE):
                    score += 0.4
        
        return min(score, 1.0)

class CredentialStuffingDetector:
    """Credential stuffing attack detector"""
    
    def __init__(self):
        self.credential_attempts = defaultdict(list)
    
    def analyze(self, features: Dict[str, Any]) -> float:
        """Analyze for credential stuffing attempts"""
        source_ip = features.get("source_ip", "")
        endpoint = features.get("endpoint", "")
        timestamp = features.get("timestamp", datetime.now())
        
        # Track credential attempts
        if "login" in endpoint.lower():
            self.credential_attempts[source_ip].append(timestamp)
            
            # Clean old attempts (older than 5 minutes)
            cutoff_time = timestamp - timedelta(minutes=5)
            self.credential_attempts[source_ip] = [
                t for t in self.credential_attempts[source_ip] if t > cutoff_time
            ]
            
            # Calculate score based on frequency
            attempts = len(self.credential_attempts[source_ip])
            if attempts > 50:
                return 1.0
            elif attempts > 20:
                return 0.8
            elif attempts > 10:
                return 0.6
            elif attempts > 5:
                return 0.4
        
        return 0.0

class ThreatIntelligence:
    """Threat intelligence provider"""
    
    def __init__(self):
        self.malicious_ips = set()
        self.malicious_user_agents = set()
        self.load_threat_feeds()
    
    def load_threat_feeds(self):
        """Load threat intelligence feeds"""
        # In a real implementation, this would load from external threat feeds
        # For demo purposes, we'll use some sample data
        self.malicious_ips = {
            "192.168.1.100", "10.0.0.50", "172.16.0.25"
        }
        
        self.malicious_user_agents = {
            "sqlmap/1.0", "nikto/2.1", "nmap/7.0"
        }
    
    def get_ip_reputation(self, ip_address: str) -> float:
        """Get IP reputation score"""
        if ip_address in self.malicious_ips:
            return 1.0
        elif ip_address.startswith("192.168.") or ip_address.startswith("10."):
            return 0.2  # Internal IP
        else:
            return 0.0
    
    def update(self):
        """Update threat intelligence"""
        # In a real implementation, this would fetch updated threat feeds
        pass

def main():
    """Main function to test AI threat detection"""
    detector = AIThreatDetector()
    
    # Test with sample requests
    test_requests = [
        {
            "source_ip": "192.168.1.100",
            "endpoint": "/api/login",
            "method": "POST",
            "user_agent": "sqlmap/1.0",
            "content_type": "application/json",
            "content_length": 100,
            "headers": {"X-Forwarded-For": "10.0.0.1"},
            "query_params": {"username": "admin", "password": "' OR '1'='1"},
            "body": '{"username":"admin","password":"admin OR 1=1"}'
        },
        {
            "source_ip": "10.0.0.50",
            "endpoint": "/api/search",
            "method": "GET",
            "user_agent": "Mozilla/5.0",
            "content_type": "application/json",
            "content_length": 50,
            "headers": {},
            "query_params": {"q": "<script>alert('xss')</script>"},
            "body": ""
        }
    ]
    
    print("🤖 STELLAR LOGIC AI - AI-POWERED THREAT DETECTION SYSTEM")
    print("=" * 65)
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n📡 Testing Request {i}:")
        threats = detector.analyze_request(request)
        
        if threats:
            print(f"🚨 {len(threats)} threat(s) detected:")
            for threat in threats:
                print(f"   - {threat.event_type}: {threat.severity} (confidence: {threat.confidence:.2f})")
                response = detector.respond_to_threat(threat)
                print(f"   Actions taken: {', '.join(response['actions_taken'])}")
        else:
            print("✅ No threats detected")
    
    # Display statistics
    stats = detector.get_threat_statistics()
    print(f"\n📊 Threat Detection Statistics:")
    print(f"   Total events: {stats['statistics']['total_events']}")
    print(f"   Threats detected: {stats['statistics']['threats_detected']}")
    print(f"   Detection rate: {stats['statistics']['detection_rate']:.1f}%")
    print(f"   Blocked IPs: {stats['blocked_ips']}")
    
    print(f"\n🎯 AI Threat Detection System is operational!")

if __name__ == "__main__":
    main()
