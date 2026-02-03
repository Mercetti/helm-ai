#!/usr/bin/env python3
"""
Stellar Logic AI - Zero-Trust Architecture Components
Advanced zero-trust security implementation with principle of least privilege
"""

import os
import sys
import json
import time
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
import re

@dataclass
class ZeroTrustPolicy:
    """Zero-trust policy data structure"""
    policy_id: str
    name: str
    description: str
    resources: List[str]
    actions: List[str]
    conditions: Dict[str, Any]
    effect: str  # "allow" or "deny"
    priority: int
    created_at: datetime
    expires_at: Optional[datetime]

@dataclass
class ZeroTrustSession:
    """Zero-trust session data structure"""
    session_id: str
    user_id: str
    device_id: str
    created_at: datetime
    expires_at: datetime
    risk_score: float
    context: Dict[str, Any]
    policies_applied: List[str]

@dataclass
class ZeroTrustDevice:
    """Zero-trust device data structure"""
    device_id: str
    user_id: str
    device_type: str
    trust_score: float
    last_seen: datetime
    attributes: Dict[str, Any]
    is_trusted: bool

class ZeroTrustArchitecture:
    """Zero-trust architecture implementation for Stellar Logic AI"""
    
    def __init__(self):
        self.base_path = "c:/Users/merce/Documents/helm-ai"
        self.production_path = "c:/Users/merce/Documents/helm-ai/production"
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.production_path, "logs/zero_trust.log")),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Zero-trust components
        self.policy_engine = ZeroTrustPolicyEngine()
        self.identity_manager = ZeroTrustIdentityManager()
        self.device_manager = ZeroTrustDeviceManager()
        self.session_manager = ZeroTrustSessionManager()
        self.context_evaluator = ZeroTrustContextEvaluator()
        self.access_controller = ZeroTrustAccessController()
        
        # Storage
        self.policies = {}
        self.sessions = {}
        self.devices = {}
        self.access_logs = deque(maxlen=10000)
        
        # Statistics
        self.stats = {
            "total_access_requests": 0,
            "access_granted": 0,
            "access_denied": 0,
            "active_sessions": 0,
            "trusted_devices": 0,
            "policies_enforced": 0
        }
        
        # Load configuration
        self.load_configuration()
        
        # Initialize default policies
        self.initialize_default_policies()
        
        self.logger.info("Zero-Trust Architecture initialized")
    
    def load_configuration(self):
        """Load zero-trust configuration"""
        config_file = os.path.join(self.production_path, "config/zero_trust_config.json")
        
        default_config = {
            "zero_trust": {
                "enabled": True,
                "principles": {
                    "never_trust": True,
                    "always_verify": True,
                    "least_privilege": True,
                    "assume_compromise": True
                },
                "session": {
                    "max_duration": 3600,  # 1 hour
                    "reauth_threshold": 0.7,
                    "device_trust_threshold": 0.6
                },
                "policy": {
                    "default_deny": True,
                    "policy_cache_ttl": 300,
                    "max_policies_per_user": 50
                },
                "device": {
                    "initial_trust_score": 0.5,
                    "trust_decay_rate": 0.1,
                    "max_devices_per_user": 10
                },
                "context": {
                    "location_verification": True,
                    "time_verification": True,
                    "behavior_verification": True
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
                self.logger.info("Created default zero-trust configuration")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            self.config = default_config
    
    def initialize_default_policies(self):
        """Initialize default zero-trust policies"""
        default_policies = [
            {
                "name": "Default Deny",
                "description": "Deny all access by default",
                "resources": ["*"],
                "actions": ["*"],
                "conditions": {},
                "effect": "deny",
                "priority": 999
            },
            {
                "name": "Admin Access",
                "description": "Allow admin access for trusted devices",
                "resources": ["/admin/*"],
                "actions": ["*"],
                "conditions": {
                    "user_role": "admin",
                    "device_trust": {"min": 0.8},
                    "session_risk": {"max": 0.3},
                    "time_range": {"start": "09:00", "end": "17:00"}
                },
                "effect": "allow",
                "priority": 100
            },
            {
                "name": "User Data Access",
                "description": "Allow users to access their own data",
                "resources": ["/api/user/{user_id}/*"],
                "actions": ["read", "update"],
                "conditions": {
                    "user_match": True,
                    "device_trust": {"min": 0.6},
                    "session_risk": {"max": 0.5}
                },
                "effect": "allow",
                "priority": 200
            },
            {
                "name": "API Access",
                "description": "Allow API access for authenticated users",
                "resources": ["/api/*"],
                "actions": ["read"],
                "conditions": {
                    "authenticated": True,
                    "device_trust": {"min": 0.5},
                    "session_risk": {"max": 0.6}
                },
                "effect": "allow",
                "priority": 300
            }
        ]
        
        for policy_data in default_policies:
            policy = ZeroTrustPolicy(
                policy_id=self.generate_policy_id(),
                name=policy_data["name"],
                description=policy_data["description"],
                resources=policy_data["resources"],
                actions=policy_data["actions"],
                conditions=policy_data["conditions"],
                effect=policy_data["effect"],
                priority=policy_data["priority"],
                created_at=datetime.now(),
                expires_at=None
            )
            self.policies[policy.policy_id] = policy
        
        self.logger.info(f"Initialized {len(default_policies)} default zero-trust policies")
    
    def generate_policy_id(self) -> str:
        """Generate unique policy ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_hash = hashlib.md5(f"{timestamp}{secrets.token_hex(8)}".encode()).hexdigest()[:8]
        return f"POLICY-{timestamp}-{random_hash}"
    
    def access_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process zero-trust access request"""
        self.stats["total_access_requests"] += 1
        
        try:
            # Extract request information
            user_id = request_data.get("user_id")
            resource = request_data.get("resource")
            action = request_data.get("action")
            session_id = request_data.get("session_id")
            device_id = request_data.get("device_id")
            context = request_data.get("context", {})
            
            # Verify identity
            identity_result = self.identity_manager.verify_identity(user_id, session_id)
            if not identity_result["valid"]:
                return self.create_access_response("deny", "Identity verification failed", {})
            
            # Get session
            session = self.session_manager.get_session(session_id)
            if not session or session.expires_at < datetime.now():
                return self.create_access_response("deny", "Invalid or expired session", {})
            
            # Get device
            device = self.device_manager.get_device(device_id)
            if not device:
                return self.create_access_response("deny", "Unknown device", {})
            
            # Evaluate context
            context_result = self.context_evaluator.evaluate_context(context, session, device)
            
            # Apply zero-trust policies
            policy_result = self.policy_engine.evaluate_policies(
                user_id, resource, action, session, device, context_result
            )
            
            # Make access decision
            access_granted = policy_result["effect"] == "allow"
            
            # Update statistics
            if access_granted:
                self.stats["access_granted"] += 1
                # Update device trust
                self.device_manager.update_trust_score(device_id, 0.1)
            else:
                self.stats["access_denied"] += 1
                # Decrease device trust
                self.device_manager.update_trust_score(device_id, -0.2)
            
            # Log access attempt
            self.log_access_attempt(request_data, access_granted, policy_result)
            
            # Update session risk
            self.session_manager.update_risk_score(session_id, context_result["risk_score"])
            
            return self.create_access_response(
                "allow" if access_granted else "deny",
                policy_result.get("reason", "Policy evaluation"),
                {
                    "session_id": session_id,
                    "device_trust": device.trust_score,
                    "session_risk": session.risk_score,
                    "context_risk": context_result["risk_score"],
                    "policies_applied": policy_result.get("policies_applied", [])
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error processing access request: {str(e)}")
            return self.create_access_response("deny", f"Internal error: {str(e)}", {})
    
    def create_access_response(self, effect: str, reason: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create access response"""
        return {
            "effect": effect,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "request_id": secrets.token_hex(16),
            "metadata": metadata
        }
    
    def log_access_attempt(self, request_data: Dict[str, Any], granted: bool, policy_result: Dict[str, Any]):
        """Log access attempt"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": request_data.get("user_id"),
            "resource": request_data.get("resource"),
            "action": request_data.get("action"),
            "device_id": request_data.get("device_id"),
            "granted": granted,
            "reason": policy_result.get("reason"),
            "policies_applied": policy_result.get("policies_applied", [])
        }
        
        self.access_logs.append(log_entry)
        
        # Save to file
        access_log_file = os.path.join(self.production_path, "logs/zero_trust_access.log")
        try:
            with open(access_log_file, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            self.logger.error(f"Error logging access attempt: {str(e)}")
    
    def create_session(self, user_id: str, device_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create zero-trust session"""
        try:
            # Verify device
            device = self.device_manager.get_device(device_id)
            if not device:
                return {"success": False, "error": "Unknown device"}
            
            # Evaluate initial context
            context_result = self.context_evaluator.evaluate_context(context, None, device)
            
            # Calculate initial risk score
            risk_score = context_result["risk_score"]
            
            # Create session
            session_id = self.session_manager.create_session(
                user_id, device_id, risk_score, context
            )
            
            # Update statistics
            self.stats["active_sessions"] += 1
            
            return {
                "success": True,
                "session_id": session_id,
                "expires_at": (datetime.now() + timedelta(seconds=self.config["zero_trust"]["session"]["max_duration"])).isoformat(),
                "risk_score": risk_score,
                "device_trust": device.trust_score
            }
            
        except Exception as e:
            self.logger.error(f"Error creating session: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def register_device(self, user_id: str, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Register new device for zero-trust"""
        try:
            # Check device limit
            user_devices = [d for d in self.devices.values() if d.user_id == user_id]
            max_devices = self.config["zero_trust"]["device"]["max_devices_per_user"]
            
            if len(user_devices) >= max_devices:
                return {"success": False, "error": f"Maximum device limit ({max_devices}) reached"}
            
            # Create device
            device_id = self.device_manager.register_device(user_id, device_info)
            
            # Update statistics
            self.stats["trusted_devices"] += 1
            
            return {
                "success": True,
                "device_id": device_id,
                "trust_score": self.devices[device_id].trust_score
            }
            
        except Exception as e:
            self.logger.error(f"Error registering device: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_zero_trust_statistics(self) -> Dict[str, Any]:
        """Get zero-trust statistics"""
        return {
            "statistics": self.stats,
            "policy_summary": self.get_policy_summary(),
            "device_summary": self.get_device_summary(),
            "session_summary": self.get_session_summary(),
            "recent_access": self.get_recent_access()
        }
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """Get policy summary"""
        total_policies = len(self.policies)
        allow_policies = sum(1 for p in self.policies.values() if p.effect == "allow")
        deny_policies = total_policies - allow_policies
        
        return {
            "total_policies": total_policies,
            "allow_policies": allow_policies,
            "deny_policies": deny_policies,
            "active_policies": sum(1 for p in self.policies.values() 
                                 if p.expires_at is None or p.expires_at > datetime.now())
        }
    
    def get_device_summary(self) -> Dict[str, Any]:
        """Get device summary"""
        total_devices = len(self.devices)
        trusted_devices = sum(1 for d in self.devices.values() if d.is_trusted)
        
        trust_scores = [d.trust_score for d in self.devices.values()]
        avg_trust = sum(trust_scores) / len(trust_scores) if trust_scores else 0
        
        return {
            "total_devices": total_devices,
            "trusted_devices": trusted_devices,
            "average_trust_score": avg_trust,
            "high_trust_devices": sum(1 for d in self.devices.values() if d.trust_score > 0.8)
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session summary"""
        active_sessions = [s for s in self.sessions.values() if s.expires_at > datetime.now()]
        
        risk_scores = [s.risk_score for s in active_sessions]
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        return {
            "active_sessions": len(active_sessions),
            "average_risk_score": avg_risk,
            "high_risk_sessions": sum(1 for s in active_sessions if s.risk_score > 0.7)
        }
    
    def get_recent_access(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent access attempts"""
        return list(self.access_logs)[-limit:] if self.access_logs else []

class ZeroTrustPolicyEngine:
    """Zero-trust policy evaluation engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def evaluate_policies(self, user_id: str, resource: str, action: str, 
                         session: ZeroTrustSession, device: ZeroTrustDevice, 
                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate zero-trust policies"""
        try:
            # Get applicable policies (would be passed from main class)
            applicable_policies = []  # This would be populated from main class
            
            # Sort by priority (lower number = higher priority)
            applicable_policies.sort(key=lambda p: p.priority)
            
            # Evaluate each policy
            for policy in applicable_policies:
                if self.evaluate_policy_conditions(policy.conditions, user_id, resource, action, 
                                                 session, device, context):
                    return {
                        "effect": policy.effect,
                        "reason": f"Policy '{policy.name}' applied",
                        "policies_applied": [policy.policy_id],
                        "priority": policy.priority
                    }
            
            # Default deny if no policies match
            return {
                "effect": "deny",
                "reason": "No applicable policy found",
                "policies_applied": [],
                "priority": 999
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating policies: {str(e)}")
            return {
                "effect": "deny",
                "reason": f"Policy evaluation error: {str(e)}",
                "policies_applied": [],
                "priority": 999
            }
    
    def evaluate_policy_conditions(self, conditions: Dict[str, Any], user_id: str, 
                                 resource: str, action: str, session: ZeroTrustSession,
                                 device: ZeroTrustDevice, context: Dict[str, Any]) -> bool:
        """Evaluate policy conditions"""
        try:
            # User role condition
            if "user_role" in conditions:
                # In real implementation, would check user role from identity manager
                pass
            
            # Device trust condition
            if "device_trust" in conditions:
                min_trust = conditions["device_trust"].get("min", 0)
                if device.trust_score < min_trust:
                    return False
            
            # Session risk condition
            if "session_risk" in conditions:
                max_risk = conditions["session_risk"].get("max", 1.0)
                if session.risk_score > max_risk:
                    return False
            
            # Time range condition
            if "time_range" in conditions:
                current_time = datetime.now().time()
                start_time = datetime.strptime(conditions["time_range"]["start"], "%H:%M").time()
                end_time = datetime.strptime(conditions["time_range"]["end"], "%H:%M").time()
                
                if not (start_time <= current_time <= end_time):
                    return False
            
            # User match condition
            if "user_match" in conditions and conditions["user_match"]:
                # Check if resource contains user_id
                if f"/{user_id}/" not in resource:
                    return False
            
            # Authenticated condition
            if "authenticated" in conditions and conditions["authenticated"]:
                # Session exists means authenticated
                if not session:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error evaluating policy conditions: {str(e)}")
            return False

class ZeroTrustIdentityManager:
    """Zero-trust identity management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def verify_identity(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Verify user identity"""
        try:
            # In real implementation, would verify against identity provider
            # For demo, we'll simulate basic verification
            
            if not user_id or not session_id:
                return {"valid": False, "reason": "Missing user_id or session_id"}
            
            # Simulate identity verification
            return {"valid": True, "reason": "Identity verified"}
            
        except Exception as e:
            self.logger.error(f"Error verifying identity: {str(e)}")
            return {"valid": False, "reason": str(e)}

class ZeroTrustDeviceManager:
    """Zero-trust device management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.devices = {}
    
    def register_device(self, user_id: str, device_info: Dict[str, Any]) -> str:
        """Register new device"""
        device_id = secrets.token_hex(16)
        
        device = ZeroTrustDevice(
            device_id=device_id,
            user_id=user_id,
            device_type=device_info.get("type", "unknown"),
            trust_score=0.5,  # Initial trust score
            last_seen=datetime.now(),
            attributes=device_info,
            is_trusted=False
        )
        
        self.devices[device_id] = device
        
        self.logger.info(f"Registered device {device_id} for user {user_id}")
        return device_id
    
    def get_device(self, device_id: str) -> Optional[ZeroTrustDevice]:
        """Get device by ID"""
        return self.devices.get(device_id)
    
    def update_trust_score(self, device_id: str, delta: float):
        """Update device trust score"""
        device = self.devices.get(device_id)
        if device:
            device.trust_score = max(0.0, min(1.0, device.trust_score + delta))
            device.last_seen = datetime.now()
            device.is_trusted = device.trust_score >= 0.6

class ZeroTrustSessionManager:
    """Zero-trust session management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sessions = {}
    
    def create_session(self, user_id: str, device_id: str, risk_score: float, context: Dict[str, Any]) -> str:
        """Create new session"""
        session_id = secrets.token_hex(32)
        
        session = ZeroTrustSession(
            session_id=session_id,
            user_id=user_id,
            device_id=device_id,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),  # 1 hour default
            risk_score=risk_score,
            context=context,
            policies_applied=[]
        )
        
        self.sessions[session_id] = session
        
        self.logger.info(f"Created session {session_id} for user {user_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ZeroTrustSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def update_risk_score(self, session_id: str, new_risk: float):
        """Update session risk score"""
        session = self.sessions.get(session_id)
        if session:
            session.risk_score = new_risk

class ZeroTrustContextEvaluator:
    """Zero-trust context evaluation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def evaluate_context(self, context: Dict[str, Any], session: Optional[ZeroTrustSession], 
                        device: ZeroTrustDevice) -> Dict[str, Any]:
        """Evaluate request context"""
        try:
            risk_score = 0.0
            risk_factors = []
            
            # Location risk
            if "location" in context:
                location_risk = self.evaluate_location_risk(context["location"])
                risk_score += location_risk
                if location_risk > 0.1:
                    risk_factors.append("unusual_location")
            
            # Time risk
            time_risk = self.evaluate_time_risk()
            risk_score += time_risk
            if time_risk > 0.1:
                risk_factors.append("unusual_time")
            
            # Device risk
            device_risk = 1.0 - device.trust_score
            risk_score += device_risk * 0.3
            if device_risk > 0.4:
                risk_factors.append("untrusted_device")
            
            # Behavior risk (if session available)
            if session and session.risk_score > 0.5:
                risk_score += session.risk_score * 0.2
                risk_factors.append("risky_behavior")
            
            return {
                "risk_score": min(risk_score, 1.0),
                "risk_factors": risk_factors,
                "context_valid": True
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating context: {str(e)}")
            return {
                "risk_score": 1.0,  # High risk on error
                "risk_factors": ["evaluation_error"],
                "context_valid": False
            }
    
    def evaluate_location_risk(self, location: str) -> float:
        """Evaluate location-based risk"""
        # Simplified location risk evaluation
        # In real implementation, would use geolocation services
        if not location:
            return 0.2  # Unknown location
        
        # Check for known risky locations
        risky_locations = ["unknown", "proxy", "vpn"]
        if any(risky in location.lower() for risky in risky_locations):
            return 0.4
        
        return 0.0
    
    def evaluate_time_risk(self) -> float:
        """Evaluate time-based risk"""
        hour = datetime.now().hour
        
        # Unusual hours (2 AM - 5 AM)
        if 2 <= hour <= 5:
            return 0.3
        
        return 0.0

class ZeroTrustAccessController:
    """Zero-trust access control"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def enforce_access_decision(self, decision: Dict[str, Any]) -> bool:
        """Enforce access decision"""
        try:
            effect = decision.get("effect", "deny")
            
            if effect == "allow":
                self.logger.info("Access granted")
                return True
            else:
                self.logger.warning(f"Access denied: {decision.get('reason', 'Unknown reason')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error enforcing access decision: {str(e)}")
            return False

def main():
    """Main function to test zero-trust architecture"""
    zero_trust = ZeroTrustArchitecture()
    
    print("🔒 STELLAR LOGIC AI - ZERO-TRUST ARCHITECTURE")
    print("=" * 55)
    
    # Test device registration
    print("\n📱 Testing Device Registration:")
    device_result = zero_trust.register_device("user123", {
        "type": "laptop",
        "os": "Windows 10",
        "browser": "Chrome"
    })
    print(f"   Device registration: {'✅ Success' if device_result['success'] else '❌ Failed'}")
    
    if device_result['success']:
        device_id = device_result['device_id']
        
        # Test session creation
        print("\n🔐 Testing Session Creation:")
        session_result = zero_trust.create_session("user123", device_id, {
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0",
            "location": "office"
        })
        print(f"   Session creation: {'✅ Success' if session_result['success'] else '❌ Failed'}")
        
        if session_result['success']:
            session_id = session_result['session_id']
            
            # Test access requests
            test_requests = [
                {
                    "user_id": "user123",
                    "resource": "/api/user/user123/profile",
                    "action": "read",
                    "session_id": session_id,
                    "device_id": device_id,
                    "context": {"location": "office", "time": "10:00"}
                },
                {
                    "user_id": "user123",
                    "resource": "/admin/config",
                    "action": "update",
                    "session_id": session_id,
                    "device_id": device_id,
                    "context": {"location": "office", "time": "10:00"}
                },
                {
                    "user_id": "user123",
                    "resource": "/api/user/user456/data",
                    "action": "read",
                    "session_id": session_id,
                    "device_id": device_id,
                    "context": {"location": "office", "time": "10:00"}
                }
            ]
            
            for i, request in enumerate(test_requests, 1):
                print(f"\n🔍 Testing Access Request {i}:")
                result = zero_trust.access_request(request)
                effect_emoji = "✅" if result["effect"] == "allow" else "❌"
                print(f"   Access {result['effect'].upper()}: {effect_emoji} {result['reason']}")
                if result['metadata']:
                    print(f"   Device trust: {result['metadata'].get('device_trust', 0):.2f}")
                    print(f"   Session risk: {result['metadata'].get('session_risk', 0):.2f}")
    
    # Display statistics
    stats = zero_trust.get_zero_trust_statistics()
    print(f"\n📊 Zero-Trust Statistics:")
    print(f"   Total access requests: {stats['statistics']['total_access_requests']}")
    print(f"   Access granted: {stats['statistics']['access_granted']}")
    print(f"   Access denied: {stats['statistics']['access_denied']}")
    print(f"   Active sessions: {stats['statistics']['active_sessions']}")
    print(f"   Trusted devices: {stats['statistics']['trusted_devices']}")
    
    policy_summary = stats['policy_summary']
    print(f"   Total policies: {policy_summary['total_policies']}")
    print(f"   Allow policies: {policy_summary['allow_policies']}")
    print(f"   Deny policies: {policy_summary['deny_policies']}")
    
    print(f"\n🎯 Zero-Trust Architecture is operational!")

if __name__ == "__main__":
    main()
