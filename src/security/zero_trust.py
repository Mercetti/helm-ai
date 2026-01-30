"""
Helm AI Zero Trust Security Architecture
Implements Zero Trust security model with continuous verification and least privilege access
"""

import os
import sys
import json
import time
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum
import threading
import jwt
import requests
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives import hashes

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from security.encryption import EncryptionManager

class TrustLevel(Enum):
    """Trust level enumeration"""
    UNTRUSTED = "untrusted"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AccessType(Enum):
    """Access type enumeration"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    SYSTEM = "system"

class DeviceType(Enum):
    """Device type enumeration"""
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    MOBILE = "mobile"
    SERVER = "server"
    IOT = "iot"
    API = "api"
    SERVICE = "service"

class RiskScore(Enum):
    """Risk score enumeration"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    UNKNOWN = 0

@dataclass
class TrustContext:
    """Trust context for access decisions"""
    user_id: str
    device_id: str
    session_id: str
    trust_level: TrustLevel
    risk_score: RiskScore
    location: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    authentication_factors: List[str] = field(default_factory=list)
    device_fingerprint: str = ""
    behavioral_score: float = 0.0
    anomaly_flags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trust context to dictionary"""
        return {
            'user_id': self.user_id,
            'device_id': self.device_id,
            'session_id': self.session_id,
            'trust_level': self.trust_level.value,
            'risk_score': self.risk_score.value,
            'location': self.location,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat(),
            'authentication_factors': self.authentication_factors,
            'device_fingerprint': self.device_fingerprint,
            'behavioral_score': self.behavioral_score,
            'anomaly_flags': self.anomaly_flags
        }

@dataclass
class AccessRequest:
    """Access request for Zero Trust evaluation"""
    user_id: str
    resource: str
    action: AccessType
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: str = ""
    user_agent: str = ""
    session_id: str = ""
    device_id: str = ""
    location: str = ""

@dataclass
class AccessDecision:
    """Access decision result"""
    allowed: bool
    trust_level: TrustLevel
    risk_score: RiskScore
    reason: str
    conditions: List[str] = field(default_factory=list)
    expires_at: Optional[datetime] = None
    requires_mfa: bool = False
    requires_device_verification: bool = False

class ZeroTrustEngine:
    """Zero Trust security engine"""
    
    def __init__(self, encryption_manager: Optional[EncryptionManager] = None):
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.trust_store: Dict[str, TrustContext] = {}
        self.risk_models: Dict[str, Any] = {}
        self.policy_engine = ZeroTrustPolicyEngine()
        self.behavioral_analyzer = BehavioralAnalyzer()
        self.device_analyzer = DeviceAnalyzer()
        self.location_analyzer = LocationAnalyzer()
        self.mfa_manager = MFAManager()
        self.session_manager = SessionManager()
        self.audit_logger = AuditLogger()
        self.lock = threading.Lock()
        
        # Configuration
        self.max_trust_duration = int(os.getenv('ZERO_TRUST_MAX_DURATION', '86400'))  # 24 hours
        self.min_trust_score = float(os.getenv('ZERO_TRUST_MIN_SCORE', '0.3'))
        self.high_risk_threshold = float(os.getenv('ZERO_TRUST_HIGH_RISK_THRESHOLD', '0.7'))
        self.critical_risk_threshold = float(os.getenv('ZERO_TRUST_CRITICAL_RISK_THRESHOLD', '0.9'))
        
    def evaluate_access(self, request: AccessRequest) -> AccessDecision:
        """Evaluate access request using Zero Trust principles"""
        try:
            # Get or create trust context
            trust_context = self._get_trust_context(request)
            
            # Analyze various factors
            risk_score = self._calculate_risk_score(request, trust_context)
            
            # Apply Zero Trust policies
            decision = self._apply_zero_trust_policies(request, trust_context, risk_score)
            
            # Update trust context
            self._update_trust_context(trust_context, decision)
            
            # Log decision
            self._log_access_decision(request, decision)
            
            return decision
            
        except Exception as e:
            logger.error(f"Zero Trust evaluation error: {e}")
            return AccessDecision(
                allowed=False,
                trust_level=TrustLevel.UNTRUSTED,
                risk_score=RiskScore.CRITICAL,
                reason=f"Security evaluation failed: {str(e)}"
            )
    
    def _get_trust_context(self, request: AccessRequest) -> TrustContext:
        """Get or create trust context for user/device"""
        with self.lock:
            # Check if we have existing context
            context_key = f"{request.user_id}:{request.device_id}"
            
            if context_key in self.trust_store:
                context = self.trust_store[context_key]
                
                # Update timestamp
                context.timestamp = datetime.utcnow()
                
                # Check if context is expired
                if (datetime.utcnow() - context.timestamp).total_seconds() > self.max_trust_duration):
                    # Expired context, create new one
                    context = self._create_trust_context(request)
            else:
                # Create new trust context
                context = self._create_trust_context(request)
            
            self.trust_store[context_key] = context
            return context
    
    def _create_trust_context(self, request: AccessRequest) -> TrustContext:
        """Create new trust context"""
        # Analyze device
        device_info = self.device_analyzer.analyze_device(request.user_agent, request.ip_address)
        
        # Analyze location
        location_info = self.location_analyzer.analyze_location(request.ip_address)
        
        # Calculate initial risk score
        initial_risk = self._calculate_initial_risk(request, device_info, location_info)
        
        # Calculate behavioral score
        behavioral_score = self.behavioral_analyzer.calculate_score(request.user_id, request.session_id)
        
        return TrustContext(
            user_id=request.user_id,
            device_id=request.device_id,
            session_id=request.session_id,
            trust_level=self._calculate_trust_level(initial_risk, behavioral_score),
            risk_score=self._calculate_risk_score_from_score(initial_risk),
            location=location_info.get('country', 'unknown'),
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            timestamp=datetime.utcnow(),
            authentication_factors=[],
            device_fingerprint=device_info.get('fingerprint', ''),
            behavioral_score=behavioral_score,
            anomaly_flags=[]
        )
    
    def _calculate_initial_risk(self, request: AccessRequest, device_info: Dict, location_info: Dict) -> float:
        """Calculate initial risk score"""
        risk_score = 0.0
        
        # Device risk
        device_risk = device_info.get('risk_score', 0.0)
        risk_score += device_risk * 0.3
        
        # Location risk
        location_risk = location_info.get('risk_score', 0.0)
        risk_score += location_risk * 0.2
        
        # Time-based risk
        current_hour = datetime.utcnow().hour
        if current_hour < 6 or current_hour > 22:
            risk_score += 0.1  # Off-hours access
        
        # New device penalty
        if not self._is_known_device(request.device_id):
            risk_score += 0.3
        
        # New session penalty
        if not self._is_known_session(request.session_id):
            risk_score += 0.2
        
        # Resource sensitivity
        resource_risk = self._get_resource_risk(request.resource, request.action)
        risk_score += resource_risk * 0.4
        
        return min(risk_score, 1.0)
    
    def _calculate_risk_score(self, request: AccessRequest, context: TrustContext) -> RiskScore:
        """Calculate comprehensive risk score"""
        risk_score = context.risk_score
        
        # Add behavioral component
        behavioral_weight = 0.3
        risk_score += context.behavioral_score * behavioral_weight
        
        # Add anomaly penalties
        anomaly_weight = 0.2
        for flag in context.anomaly_flags:
            risk_score += 0.1 * anomaly_weight
        
        # Add time decay for established trust
        if context.trust_level != TrustLevel.UNTRUSTED:
            trust_duration = (datetime.utcnow() - context.timestamp).total_seconds()
            trust_decay = max(0, 1 - (trust_duration / self.max_trust_duration))
            risk_score *= (1 - trust_decay * 0.5)
        
        return RiskScore(min(int(risk_score * 4), 4))
    
    def _calculate_trust_level(self, risk_score: float, behavioral_score: float) -> TrustLevel:
        """Calculate trust level from risk and behavioral scores"""
        combined_score = (risk_score * 0.7) + (behavioral_score * 0.3)
        
        if combined_score >= self.critical_risk_threshold:
            return TrustLevel.UNTRUSTED
        elif combined_score >= self.high_risk_threshold:
            return TrustLevel.LOW
        elif combined_score >= self.min_trust_score:
            return TrustLevel.MEDIUM
        else:
            return TrustLevel.HIGH
    
    def _calculate_risk_score_from_score(self, score: float) -> RiskScore:
        """Convert numeric score to RiskScore enum"""
        if score >= 0.75:
            return RiskScore.CRITICAL
        elif score >= 0.5:
            return RiskScore.HIGH
        elif score >= 0.25:
            return RiskScore.MEDIUM
        elif score > 0:
            return RiskScore.LOW
        else:
            return RiskScore.UNKNOWN
    
    def _apply_zero_trust_policies(self, request: AccessRequest, context: TrustContext, risk_score: RiskScore) -> AccessDecision:
        """Apply Zero Trust policies"""
        # Check if access is explicitly denied
        if self.policy_engine.is_explicitly_denied(request, context):
            return AccessDecision(
                allowed=False,
                trust_level=context.trust_level,
                risk_score=risk_score,
                reason="Access explicitly denied by policy"
            )
        
        # Check if access requires additional verification
        requires_mfa = self.policy_engine.requires_mfa(request, context)
        requires_device = self.policy_engine.requires_device_verification(request, context)
        
        # Make decision based on risk score and trust level
        if risk_score == RiskScore.CRITICAL:
            return AccessDecision(
                allowed=False,
                trust_level=context.trust_level,
                risk_score=risk_score,
                reason="Critical risk score - access denied",
                requires_mfa=requires_mfa,
                requires_device_verification=requires_device
            )
        elif risk_score == RiskScore.HIGH and context.trust_level == TrustLevel.UNTRUSTED:
            return AccessDecision(
                allowed=False,
                trust_level=context.trust_level,
                risk_score=risk_score,
                reason="High risk with untrusted context - access denied",
                requires_mfa=requires_mfa,
                requires_device_verification=requires_device
            )
        elif risk_score == RiskScore.HIGH and context.trust_level == TrustLevel.LOW:
            return AccessDecision(
                allowed=True,
                trust_level=context.trust_level,
                risk_score=risk_score,
                reason="High risk but some trust established - allowed with conditions",
                conditions=["mfa_required", "device_verification_required"],
                requires_mfa=requires_mfa,
                requires_device_verification=requires_device,
                expires_at=datetime.utcnow() + timedelta(minutes=15)
            )
        else:
            return AccessDecision(
                allowed=True,
                trust_level=context.trust_level,
                risk_score=risk_score,
                reason="Access allowed based on Zero Trust evaluation",
                requires_mfa=requires_mfa,
                requires_device_verification=requires_device_verification
            )
    
    def _update_trust_context(self, context: TrustContext, decision: AccessDecision) -> None:
        """Update trust context based on access decision"""
        if decision.allowed:
            # Increase trust for successful access
            if context.trust_level == TrustLevel.UNTRUSTED:
                context.trust_level = TrustLevel.LOW
            elif context.trust_level == TrustLevel.LOW:
                context.trust_level = TrustLevel.MEDIUM
            elif context.trust_level == TrustLevel.MEDIUM:
                context.trust_level = TrustLevel.HIGH
        else:
            # Decrease trust for denied access
            if context.trust_level == TrustLevel.HIGH:
                context.trust_level = TrustLevel.MEDIUM
            elif context.trust_level == TrustLevel.MEDIUM:
                context.trust_level = TrustLevel.LOW
            elif context.trust_level == TrustLevel.LOW:
                context.trust_level = TrustLevel.UNTRUSTED
        
        # Update risk score based on decision
        if decision.allowed:
            context.risk_score = RiskScore(max(0, context.risk_score.value - 1))
        else:
            context.risk_score = RiskScore(min(4, context.risk_score.value + 1))
    
    def _get_resource_risk(self, resource: str, action: AccessType) -> float:
        """Get risk score for resource and action"""
        resource_risk_map = {
            'admin': 0.8,
            'system': 0.7,
            'database': 0.6,
            'api': 0.5,
            'user_data': 0.4,
            'public': 0.1
        }
        
        action_risk_map = {
            AccessType.DELETE: 0.8,
            AccessType.ADMIN: 0.7,
            AccessType.WRITE: 0.5,
            AccessType.READ: 0.2
        }
        
        return (resource_risk_map.get(resource, 0.5) + action_risk_map[action]) / 2
    
    def _is_known_device(self, device_id: str) -> bool:
        """Check if device is known"""
        return device_id in self.trust_store or device_id in self.device_analyzer.known_devices
    
    def _is_known_session(self, session_id: str) -> bool:
        """Check if session is known"""
        return session_id in self.session_manager.active_sessions
    
    def _log_access_decision(self, request: AccessRequest, decision: AccessDecision) -> None:
        """Log access decision for audit"""
        self.audit_logger.log_access_event(
            user_id=request.user_id,
            resource=request.resource,
            action=request.action.value,
            allowed=decision.allowed,
            trust_level=decision.trust_level.value,
            risk_score=decision.risk_score.value,
            reason=decision.reason,
            ip_address=request.ip_address,
            timestamp=datetime.utcnow()
        )

class ZeroTrustPolicyEngine:
    """Zero Trust policy engine"""
    
    def __init__(self):
        self.policies = self._load_policies()
    
    def _load_policies(self) -> Dict[str, Any]:
        """Load Zero Trust policies from configuration"""
        return {
            'explicit_denials': [
                {
                    'resource': 'admin',
                    'action': 'delete',
                    'condition': 'user_role != "super_admin"'
                },
                {
                    'resource': 'system',
                    'action': 'delete',
                    'condition': 'user_role != "super_admin"'
                }
            ],
            'mfa_requirements': {
                'high_risk_resources': ['admin', 'system'],
                'external_access': True,
                'new_devices': True,
                'unusual_locations': True
            },
            'device_verification': {
                'high_risk_actions': ['delete', 'admin'],
                'external_access': True,
                'new_devices': True
            }
        }
    
    def is_explicitly_denied(self, request: AccessRequest, context: TrustContext) -> bool:
        """Check if access is explicitly denied"""
        for policy in self.policies['explicit_denials']:
            if (policy['resource'] == request.resource and 
                policy['action'] == request.action.value and
                self._evaluate_condition(policy['condition'], request, context)):
                return True
        return False
    
    def requires_mfa(self, request: AccessRequest, context: TrustContext) -> bool:
        """Check if MFA is required"""
        # High risk resources always require MFA
        if request.resource in self.policies['mfa_requirements']['high_risk_resources']:
            return True
        
        # External access requires MFA
        if self.policies['mfa_requirements']['external_access']:
            if self._is_external_access(request.ip_address):
                return True
        
        # New devices require MFA
        if self.policies['mfa_requirements']['new_devices']:
            if not self._is_known_device(request.device_id):
                return True
        
        # Unusual locations require MFA
        if self.policies_mfa_requirements['unusual_locations']:
            if self._is_unusual_location(context.location):
                return True
        
        return False
    
    def requires_device_verification(self, request: AccessRequest, context: TrustContext) -> bool:
        """Check if device verification is required"""
        # High risk actions require device verification
        if request.action.value in self.policies['device_verification']['high_risk_actions']:
            return True
        
        # External access requires device verification
        if self.policies['device_verification']['external_access']:
            if self._is_external_access(request.ip_address):
                return True
        
        # New devices require device verification
        if self.policies['device_verification']['new_devices']:
            if not self._is_known_device(request.device_id):
                return True
        
        return False
    
    def _evaluate_condition(self, condition: str, request: AccessRequest, context: TrustContext) -> bool:
        """Evaluate policy condition"""
        # Simple condition evaluation - can be enhanced
        if condition == 'user_role != "super_admin"':
            # In a real implementation, this would check user role from context
            return True  # Simplified for demo
        return False
    
    def _is_external_access(self, ip_address: str) -> bool:
        """Check if access is from external network"""
        # Simplified check - in production, this would use IP ranges
        internal_ranges = ['10.0.0.0/8', '192.168.0.0/16', '172.16.0.0/12']
        
        for ip_range in internal_ranges:
            if self._ip_in_range(ip_address, ip_range):
                return False
        
        return True
    
    def _is_unusual_location(self, location: str) -> bool:
        """Check if location is unusual"""
        unusual_countries = ['CN', 'RU', 'KP', 'IR']
        return location in unusual_countries
    
    def _ip_in_range(self, ip: str, cidr: str) -> bool:
        """Check if IP is in CIDR range"""
        import ipaddress
        try:
            return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr)
        except:
            return False

class BehavioralAnalyzer:
    """Behavioral analysis for Zero Trust"""
    
    def __init__(self):
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.session_profiles: Dict[str, List[Dict[str, Any]]] = {}
        self.lock = threading.Lock()
    
    def calculate_score(self, user_id: str, session_id: str) -> float:
        """Calculate behavioral score for user session"""
        with self.lock:
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = {
                    'access_count': 0,
                    'unique_ips': set(),
                    'unique_devices': set(),
                    'access_times': [],
                    'session_count': 0,
                    'avg_session_duration': 0,
                    'failed_attempts': 0
                }
            
            profile = self.user_profiles[user_id]
            
            # Update profile
            profile['access_count'] += 1
            profile['session_count'] += 1
            profile['access_times'].append(datetime.utcnow())
            
            # Calculate behavioral score
            score = 0.5  # Base score
            
            # Increase score for consistent patterns
            if profile['access_count'] > 10:
                score += 0.2
            
            # Decrease score for failed attempts
            if profile['failed_attempts'] > 0:
                score -= 0.3
            
            # Decrease score for too many unique IPs
            if len(profile['unique_ips']) > 5:
                score -= 0.2
            
            # Decrease score for too many unique devices
            if len(profile['unique_devices']) > 3:
                score -= 0.1
            
            return max(0.0, min(1.0, score))

class DeviceAnalyzer:
    """Device analysis for Zero Trust"""
    
    def __init__(self):
        self.known_devices: Dict[str, Dict[str, Any]] = {}
        self.device_fingerprints: Dict[str, str] = {}
        self.lock = threading.Lock()
    
    def analyze_device(self, user_agent: str, ip_address: str) -> Dict[str, Any]:
        """Analyze device from user agent and IP"""
        # Generate device fingerprint
        fingerprint = self._generate_fingerprint(user_agent, ip_address)
        
        device_type = self._detect_device_type(user_agent)
        
        # Check if device is known
        known = fingerprint in self.known_devices
        
        risk_score = 0.0
        if not known:
            risk_score += 0.3  # New device penalty
        
        # Mobile devices have slightly higher risk
        if device_type == DeviceType.MOBILE:
            risk_score += 0.1
        
        # Check for suspicious user agent patterns
        if self._is_suspicious_user_agent(user_agent):
            risk_score += 0.2
        
        return {
            'fingerprint': fingerprint,
            'device_type': device_type.value,
            'risk_score': risk_score,
            'known': known,
            'user_agent': user_agent,
            'ip_address': ip_address
        }
    
    def _generate_fingerprint(self, user_agent: str, ip_address: str) -> str:
        """Generate device fingerprint"""
        # Create fingerprint from user agent and IP
        fingerprint_data = f"{user_agent}:{ip_address}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:32]
    
    def _detect_device_type(self, user_agent: str) -> DeviceType:
        """Detect device type from user agent"""
        user_agent_lower = user_agent.lower()
        
        if 'mobile' in user_agent_lower:
            return DeviceType.MOBILE
        elif 'tablet' in user_agent_lower:
            return DeviceType.MOBILE  # Treat tablets as mobile for security
        elif 'server' in user_agent_lower:
            return DeviceType.SERVER
        elif 'curl' in user_agent_lower or 'wget' in user_agent_lower:
            return DeviceType.API
        elif 'python-requests' in user_agent_lower:
            return DeviceType.API
        else:
            return DeviceType.DESKTOP
    
    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check for suspicious user agent patterns"""
        suspicious_patterns = [
            'bot',
            'crawler',
            'scanner',
            'hack',
            'exploit',
            'attack'
        ]
        
        return any(pattern in user_agent_lower for pattern in suspicious_patterns)

class LocationAnalyzer:
    """Location analysis for Zero Trust"""
    
    def analyze_location(self, ip_address: str) -> Dict[str, Any]:
        """Analyze location from IP address"""
        # In a real implementation, this would use a GeoIP database
        # For demo purposes, we'll use a simple mapping
        
        location_map = {
            '10.0.0.0/8': {'country': 'US', 'city': 'New York', 'risk_score': 0.0},
            '192.168.0.0/16': {'country': 'US', 'city': 'Private', 'risk_score': 0.1},
            '172.16.0.0/12': {'country': 'US', 'city': 'Private', 'risk_score': 0.1},
            '8.8.8.8': {'country': 'US', 'city': 'Google DNS', 'risk_score': 0.4},
            '203.0.113.42': {'country': 'CN', 'city': 'Shanghai', 'risk_score': 0.8},
            '31.13.66.0': {'country': 'KR', 'city': 'Seoul', 'risk_score': 0.7},
            '185.220.101.0': {'country': 'RU', 'city': 'Moscow', 'risk_score': 0.9},
            '45.113.134.0': {'country': 'IN', 'city': 'Mumbai', 'risk_score': 0.8}
        }
        
        for cidr, info in location_map.items():
            if self._ip_in_range(ip_address, cidr):
                return info
        
        # Unknown location
        return {
            'country': 'Unknown',
            'city': 'Unknown',
            'risk_score': 0.5
        }
    
    def _ip_in_range(self, ip: str, cidr: str) -> bool:
        """Check if IP is in CIDR range"""
        import ipaddress
        try:
            return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr)
        except:
            return False

class MFAManager:
    """Multi-Factor Authentication manager for Zero Trust"""
    
    def __init__(self):
        self.mfa_methods = ['totp', 'sms', 'email', 'push', 'biometric']
        self.user_mfa_preferences: Dict[str, str] = {}
        self.mfa_challenges: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
    
    def generate_mfa_challenge(self, user_id: str, method: str) -> Dict[str, Any]:
        """Generate MFA challenge"""
        if method not in self.mfa_methods:
            raise ValueError(f"Unsupported MFA method: {method}")
        
        challenge_id = secrets.token_urlsafe(16)
        
        if method == 'totp':
            secret = self._generate_totp_secret()
            return {
                'challenge_id': challenge_id,
                'method': method,
                'secret': secret,
                'expires_at': (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            }
        elif method == 'sms':
            code = self._generate_sms_code()
            return {
                'challenge_id': challenge_id,
                'method': method,
                'code': code,
                'expires_at': (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            }
        elif method == 'email':
            code = self._generate_email_code()
            return {
                'challenge_id': challenge_id,
                'method': method,
                'code': code,
                'expires_at': (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            }
        else:
            raise ValueError(f"MFA method {method} not implemented")
    
    def verify_mfa_response(self, challenge_id: str, response: str, method: str) -> bool:
        """Verify MFA response"""
        if challenge_id not in self.mfa_challenges:
            return False
        
        challenge = self.mfa_challenges[challenge_id]
        
        if method == 'totp':
            return self._verify_totp_response(challenge, response)
        elif method == 'sms':
            return self._verify_sms_response(challenge, response)
        elif method == 'email':
            return self._verify_email_response(challenge, response)
        else:
            return False
    
    def _generate_totp_secret(self) -> str:
        """Generate TOTP secret"""
        return self.encryption_manager.generate_totp_secret()
    
    def _generate_sms_code(self) -> str:
        """Generate SMS verification code"""
        return f"{secrets.randbelow(9000000) + 1000000:06d}"
    
    def _generate_email_code(self) -> str:
        """Generate email verification code"""
        return f"{secrets.randbelow(9000000) + 1000000:06d}"
    
    def _verify_totp_response(self, challenge: Dict[str, Any], response: str) -> bool:
        """Verify TOTP response"""
        try:
            return self.encryption_manager.verify_totp_token(challenge['secret'], response)
        except:
            return False
    
    def _verify_sms_response(self, challenge: Dict[str, Any], response: str) -> bool:
        """Verify SMS response"""
        return response == challenge['code']
    
    def _verify_email_response(self, challenge: Dict[str, Any], response: str) -> bool:
        """Verify email response"""
        return response == challenge['code']

class SessionManager:
    """Session manager for Zero Trust"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = int(os.getenv('SESSION_TIMEOUT', '3600'))  # 1 hour
        self.max_sessions_per_user = int(os.getenv('MAX_SESSIONS_PER_USER', '5'))
        self.lock = threading.Lock()
    
    def create_session(self, user_id: str, device_id: str, ip_address: str) -> Dict[str, Any]:
        """Create new session"""
        session_id = secrets.token_urlsafe(32)
        
        session = {
            'session_id': session_id,
            'user_id': user_id,
            'device_id': device_id,
            'ip_address': ip_address,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(seconds=self.session_timeout),
            'last_activity': datetime.utcnow(),
            'is_active': True
        }
        
        with self.lock:
            # Check user session limit
            user_sessions = [s for s in self.active_sessions.values() if s['user_id'] == user_id and s['is_active']]
            if len(user_sessions) >= self.max_sessions_per_user:
                # Deactivate oldest session
                oldest_session = min(user_sessions, key=lambda s: s['created_at'])
                oldest_session['is_active'] = False
            
            self.active_sessions[session_id] = session
        
        return session
    
    def validate_session(self, session_id: str, user_id: str) -> bool:
        """Validate session"""
        with self.lock:
            if session_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[session_id]
            
            # Check if session belongs to user
            if session['user_id'] != user_id:
                return False
            
            # Check if session is expired
            if datetime.utcnow() > session['expires_at']:
                session['is_active'] = False
                return False
            
            # Update last activity
            session['last_activity'] = datetime.utcnow()
            
            return session['is_active']
    
    def revoke_session(self, session_id: str) -> None:
        """Revoke session"""
        with self.lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['is_active'] = False

class AuditLogger:
    """Audit logger for Zero Trust events"""
    
    def __init__(self):
        self.log_file = os.getenv('ZERO_TRUST_AUDIT_LOG', 'logs/zero_trust_audit.log')
        self.lock = threading.Lock()
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def log_access_event(self, user_id: str, resource: str, action: str, allowed: bool, 
                        trust_level: str, risk_score: int, reason: str, 
                        ip_address: str, timestamp: datetime) -> None:
        """Log access event"""
        with self.lock:
            log_entry = {
                'timestamp': timestamp.isoformat(),
                'user_id': user_id,
                'resource': resource,
                'action': action,
                'allowed': allowed,
                'trust_level': trust_level,
                'risk_score': risk_score,
                'reason': reason,
                'ip_address': ip_address
            }
            
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
    
    def log_trust_update(self, user_id: str, old_level: str, new_level: str, reason: str, timestamp: datetime) -> None:
        """Log trust level update"""
        with self.lock:
            log_entry = {
                'timestamp': timestamp.isoformat(),
                'user_id': user_id,
                'event': 'trust_level_change',
                'old_level': old_level,
                'new_level': new_level,
                'reason': reason
            }
            
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

# Global Zero Trust engine instance
zero_trust_engine = ZeroTrustEngine()

# Export main components
__all__ = [
    'ZeroTrustEngine',
    'TrustContext',
    'AccessRequest',
    'AccessDecision',
    'TrustLevel',
    'AccessType',
    'DeviceType',
    'RiskScore',
    'ZeroTrustPolicyEngine',
    'BehavioralAnalyzer',
    'DeviceAnalyzer',
    'LocationAnalyzer',
    'MFAManager',
    'SessionManager',
    'AuditLogger',
    'zero_trust_engine'
]
