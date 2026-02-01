#!/usr/bin/env python3
"""
Stellar Logic AI - Active Defense System
Automatic threat neutralization and countermeasure deployment
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random
import math
import json
import hashlib
from collections import defaultdict, deque

class DefenseAction(Enum):
    """Types of defense actions"""
    BLOCK_IP = "block_ip"
    ISOLATE_SYSTEM = "isolate_system"
    TERMINATE_PROCESS = "terminate_process"
    PATCH_VULNERABILITY = "patch_vulnerability"
    DEPLOY_HONEYPOT = "deploy_honeypot"
    TRAFFIC_REDIRECT = "traffic_redirect"
    ENCRYPT_DATA = "encrypt_data"
    BACKUP_CRITICAL = "backup_critical"
    DISABLE_ACCOUNT = "disable_account"
    RATE_LIMIT = "rate_limit"
    NETWORK_SEGMENTATION = "network_segmentation"
    FORENSIC_CAPTURE = "forensic_capture"

class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DefenseStatus(Enum):
    """Defense action status"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class Threat:
    """Threat information"""
    threat_id: str
    threat_type: str
    severity: ThreatLevel
    source_ip: str
    target_system: str
    attack_vector: str
    confidence: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class DefenseAction:
    """Defense action information"""
    action_id: str
    action_type: str
    threat_id: str
    target: str
    parameters: Dict[str, Any]
    status: DefenseStatus
    execution_time: datetime
    completion_time: Optional[datetime]
    success_rate: float
    rollback_available: bool
    metadata: Dict[str, Any]

@dataclass
class DefenseResult:
    """Defense action result"""
    result_id: str
    action_id: str
    threat_id: str
    success: bool
    impact_assessment: Dict[str, float]
    side_effects: List[str]
    effectiveness_score: float
    timestamp: datetime
    evidence_collected: Dict[str, Any]

@dataclass
class ActiveDefenseProfile:
    """Active defense system profile"""
    system_id: str
    threats: deque
    defense_actions: deque
    defense_results: deque
    defense_rules: Dict[str, Any]
    system_status: Dict[str, Any]
    performance_metrics: Dict[str, float]
    last_updated: datetime
    total_threats: int
    total_actions: int

class ActiveDefenseSystem:
    """Active defense system with automatic threat neutralization"""
    
    def __init__(self):
        self.profiles = {}
        self.threats = {}
        self.defense_actions = {}
        self.defense_results = {}
        
        # Defense configuration
        self.defense_config = {
            'auto_response_enabled': True,
            'response_delay': 0.1,  # seconds
            'max_concurrent_actions': 10,
            'rollback_timeout': 300,  # seconds
            'evidence_retention': 90,  # days
            'min_confidence_threshold': 0.7,
            'critical_response_immediate': True
        }
        
        # Defense rules matrix
        self.defense_rules = {
            'ddos_attack': [
                {'action': 'block_ip', 'priority': 1, 'threshold': 0.8},
                {'action': 'traffic_redirect', 'priority': 2, 'threshold': 0.9},
                {'action': 'network_segmentation', 'priority': 3, 'threshold': 0.95}
            ],
            'brute_force': [
                {'action': 'disable_account', 'priority': 1, 'threshold': 0.7},
                {'action': 'rate_limit', 'priority': 2, 'threshold': 0.8},
                {'action': 'block_ip', 'priority': 3, 'threshold': 0.9}
            ],
            'malware_infection': [
                {'action': 'isolate_system', 'priority': 1, 'threshold': 0.8},
                {'action': 'terminate_process', 'priority': 2, 'threshold': 0.85},
                {'action': 'forensic_capture', 'priority': 3, 'threshold': 0.9}
            ],
            'data_exfiltration': [
                {'action': 'encrypt_data', 'priority': 1, 'threshold': 0.7},
                {'action': 'isolate_system', 'priority': 2, 'threshold': 0.8},
                {'action': 'backup_critical', 'priority': 3, 'threshold': 0.9}
            ],
            'vulnerability_exploit': [
                {'action': 'patch_vulnerability', 'priority': 1, 'threshold': 0.8},
                {'action': 'network_segmentation', 'priority': 2, 'threshold': 0.9},
                {'action': 'deploy_honeypot', 'priority': 3, 'threshold': 0.95}
            ]
        }
        
        # Performance metrics
        self.total_threats = 0
        self.total_actions = 0
        self.successful_defenses = 0
        self.failed_defenses = 0
        
        # Initialize defense engines
        self._initialize_defense_engines()
        
    def _initialize_defense_engines(self):
        """Initialize defense execution engines"""
        self.defense_engines = {
            'network_defense': {
                'ip_blocking': self._execute_ip_blocking,
                'traffic_redirect': self._execute_traffic_redirect,
                'network_segmentation': self._execute_network_segmentation,
                'rate_limiting': self._execute_rate_limiting
            },
            'system_defense': {
                'process_termination': self._execute_process_termination,
                'system_isolation': self._execute_system_isolation,
                'data_encryption': self._execute_data_encryption,
                'backup_creation': self._execute_backup_creation
            },
            'account_defense': {
                'account_disabling': self._execute_account_disabling,
                'privilege_revocation': self._execute_privilege_revocation
            },
            'forensic_defense': {
                'evidence_capture': self._execute_evidence_capture,
                'honeypot_deployment': self._execute_honeypot_deployment
            }
        }
    
    def create_profile(self, system_id: str) -> ActiveDefenseProfile:
        """Create active defense profile"""
        profile = ActiveDefenseProfile(
            system_id=system_id,
            threats=deque(maxlen=10000),
            defense_actions=deque(maxlen=50000),
            defense_results=deque(maxlen=50000),
            defense_rules=self.defense_rules.copy(),
            system_status={
                'defense_status': 'active',
                'current_threats': 0,
                'active_defenses': 0,
                'system_health': 1.0
            },
            performance_metrics={
                'response_time': 0.0,
                'success_rate': 1.0,
                'false_positive_rate': 0.0,
                'defense_effectiveness': 1.0
            },
            last_updated=datetime.now(),
            total_threats=0,
            total_actions=0
        )
        
        self.profiles[system_id] = profile
        return profile
    
    def detect_threat(self, system_id: str, threat: Threat) -> List[DefenseAction]:
        """Detect threat and initiate defense actions"""
        profile = self.profiles.get(system_id)
        if not profile:
            profile = self.create_profile(system_id)
        
        # Add threat to profile
        profile.threats.append(threat)
        profile.total_threats = len(profile.threats)
        profile.last_updated = datetime.now()
        
        # Update global threats
        self.threats[threat.threat_id] = threat
        self.total_threats = len(self.threats)
        
        # Update system status
        profile.system_status['current_threats'] = len([t for t in profile.threats if t.severity == ThreatLevel.CRITICAL])
        
        # Initiate defense actions
        defense_actions = self._initiate_defense_actions(profile, threat)
        
        # Store defense actions
        for action in defense_actions:
            profile.defense_actions.append(action)
            profile.total_actions = len(profile.defense_actions)
            self.defense_actions[action.action_id] = action
            self.total_actions = len(self.defense_actions)
        
        return defense_actions
    
    def _initiate_defense_actions(self, profile: ActiveDefenseProfile, threat: Threat) -> List[DefenseAction]:
        """Initiate appropriate defense actions based on threat"""
        actions = []
        
        # Get defense rules for threat type
        rules = profile.defense_rules.get(threat.threat_type, [])
        
        # Filter rules based on confidence and priority
        applicable_rules = [
            rule for rule in rules 
            if threat.confidence >= rule['threshold']
        ]
        
        # Sort by priority
        applicable_rules.sort(key=lambda x: x['priority'])
        
        # Execute defense actions
        for rule in applicable_rules:
            action = self._create_defense_action(profile, threat, rule)
            if action:
                actions.append(action)
                
                # Execute action asynchronously
                if self.defense_config['auto_response_enabled']:
                    self._execute_defense_action(profile, action)
        
        return actions
    
    def _create_defense_action(self, profile: ActiveDefenseProfile, threat: Threat, rule: Dict[str, Any]) -> Optional[DefenseAction]:
        """Create defense action based on rule"""
        action_type_str = rule['action']
        
        # Determine action target and parameters
        target, parameters = self._determine_action_parameters(threat, action_type_str)
        
        action = DefenseAction(
            action_id=f"action_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
            action_type=action_type_str,
            threat_id=threat.threat_id,
            target=target,
            parameters=parameters,
            status=DefenseStatus.PENDING,
            execution_time=datetime.now(),
            completion_time=None,
            success_rate=0.0,
            rollback_available=True,
            metadata={
                'rule_priority': rule['priority'],
                'threshold': rule['threshold'],
                'threat_confidence': threat.confidence
            }
        )
        
        return action
    
    def _determine_action_parameters(self, threat: Threat, action_type_str: str) -> Tuple[str, Dict[str, Any]]:
        """Determine action target and parameters"""
        if action_type_str == 'block_ip':
            return threat.source_ip, {'duration': 3600, 'reason': f'Threat: {threat.threat_type}'}
        
        elif action_type_str == 'isolate_system':
            return threat.target_system, {'isolation_type': 'network', 'preserve_evidence': True}
        
        elif action_type_str == 'terminate_process':
            return threat.target_system, {'process_id': threat.metadata.get('process_id'), 'force': True}
        
        elif action_type_str == 'disable_account':
            return threat.metadata.get('account_id', 'unknown'), {'reason': 'Security breach detected'}
        
        elif action_type_str == 'rate_limit':
            return threat.source_ip, {'requests_per_second': 10, 'duration': 1800}
        
        elif action_type_str == 'traffic_redirect':
            return threat.source_ip, {'redirect_to': 'honeypot', 'preserve_headers': True}
        
        elif action_type_str == 'network_segmentation':
            return threat.target_system, {'segment_id': 'isolated', 'block_external': True}
        
        elif action_type_str == 'encrypt_data':
            return threat.target_system, {'encryption_algorithm': 'AES-256', 'backup_original': True}
        
        elif action_type_str == 'backup_critical':
            return threat.target_system, {'backup_type': 'full', 'destination': 'secure_storage'}
        
        elif action_type_str == 'patch_vulnerability':
            return threat.target_system, {'vulnerability_id': threat.metadata.get('vuln_id'), 'restart_required': False}
        
        elif action_type_str == 'deploy_honeypot':
            return threat.target_system, {'honeypot_type': threat.threat_type, 'logging_enabled': True}
        
        elif action_type_str == 'forensic_capture':
            return threat.target_system, {'capture_memory': True, 'capture_disk': True, 'capture_network': True}
        
        else:
            return 'unknown', {}
    
    def _execute_defense_action(self, profile: ActiveDefenseProfile, action: DefenseAction) -> DefenseResult:
        """Execute defense action and return result"""
        # Update action status
        action.status = DefenseStatus.EXECUTING
        profile.system_status['active_defenses'] += 1
        
        # Simulate action execution
        execution_time = random.uniform(0.1, 2.0)  # Simulated execution time
        
        # Determine success based on action type and threat
        success_probability = self._calculate_success_probability(action)
        success = random.random() < success_probability
        
        # Create defense result
        result = DefenseResult(
            result_id=f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
            action_id=action.action_id,
            threat_id=action.threat_id,
            success=success,
            impact_assessment=self._calculate_impact_assessment(action, success),
            side_effects=self._calculate_side_effects(action, success),
            effectiveness_score=success_probability if success else 0.0,
            timestamp=datetime.now(),
            evidence_collected=self._collect_evidence(action, success)
        )
        
        # Update action
        action.status = DefenseStatus.COMPLETED if success else DefenseStatus.FAILED
        action.completion_time = datetime.now()
        action.success_rate = success_probability
        
        # Update profile
        profile.defense_results.append(result)
        profile.system_status['active_defenses'] -= 1
        
        # Update global metrics
        self.defense_results[result.result_id] = result
        if success:
            self.successful_defenses += 1
        else:
            self.failed_defenses += 1
        
        # Update performance metrics
        self._update_performance_metrics(profile, action, result)
        
        return result
    
    def _calculate_success_probability(self, action: DefenseAction) -> float:
        """Calculate success probability for defense action"""
        base_success = 0.85
        
        # Adjust based on action type
        action_multipliers = {
            'block_ip': 0.95,
            'isolate_system': 0.90,
            'terminate_process': 0.85,
            'disable_account': 0.92,
            'rate_limit': 0.88,
            'traffic_redirect': 0.83,
            'network_segmentation': 0.87,
            'encrypt_data': 0.94,
            'backup_critical': 0.96,
            'patch_vulnerability': 0.89,
            'deploy_honeypot': 0.91,
            'forensic_capture': 0.93
        }
        
        multiplier = action_multipliers.get(action.action_type, 1.0)
        return min(1.0, base_success * multiplier)
    
    def _calculate_impact_assessment(self, action: DefenseAction, success: bool) -> Dict[str, float]:
        """Calculate impact assessment of defense action"""
        if success:
            return {
                'threat_neutralization': random.uniform(0.8, 1.0),
                'system_protection': random.uniform(0.9, 1.0),
                'data_integrity': random.uniform(0.85, 1.0),
                'service_availability': random.uniform(0.7, 0.95)
            }
        else:
            return {
                'threat_neutralization': random.uniform(0.0, 0.3),
                'system_protection': random.uniform(0.1, 0.5),
                'data_integrity': random.uniform(0.2, 0.6),
                'service_availability': random.uniform(0.3, 0.7)
            }
    
    def _calculate_side_effects(self, action: DefenseAction, success: bool) -> List[str]:
        """Calculate potential side effects of defense action"""
        side_effects = []
        
        if not success:
            side_effects.append("Defense action failed - threat may still be active")
        
        # Action-specific side effects
        if action.action_type == 'block_ip':
            side_effects.append("Legitimate users from blocked IP may be affected")
        elif action.action_type == 'isolate_system':
            side_effects.append("Isolated system unavailable for normal operations")
        elif action.action_type == 'terminate_process':
            side_effects.append("Process termination may cause data loss")
        elif action.action_type == 'disable_account':
            side_effects.append("User account temporarily disabled")
        elif action.action_type == 'network_segmentation':
            side_effects.append("Network communication between segments disrupted")
        
        return side_effects
    
    def _collect_evidence(self, action: DefenseAction, success: bool) -> Dict[str, Any]:
        """Collect evidence from defense action"""
        evidence = {
            'action_id': action.action_id,
            'action_type': action.action_type,
            'target': action.target,
            'execution_time': action.execution_time.isoformat(),
            'success': success,
            'parameters': action.parameters
        }
        
        # Add action-specific evidence
        if action.action_type == 'block_ip':
            evidence['blocked_ip'] = action.target
            evidence['block_duration'] = action.parameters.get('duration')
        elif action.action_type == 'isolate_system':
            evidence['isolated_system'] = action.target
            evidence['isolation_type'] = action.parameters.get('isolation_type')
        elif action.action_type == 'forensic_capture':
            evidence['memory_dump'] = True
            evidence['network_capture'] = True
            evidence['disk_image'] = True
        
        return evidence
    
    def _update_performance_metrics(self, profile: ActiveDefenseProfile, action: DefenseAction, result: DefenseResult) -> None:
        """Update performance metrics"""
        # Update response time
        response_time = (action.completion_time - action.execution_time).total_seconds()
        profile.performance_metrics['response_time'] = (
            profile.performance_metrics['response_time'] * 0.9 + response_time * 0.1
        )
        
        # Update success rate
        total_actions = len(profile.defense_actions)
        successful_actions = len([r for r in profile.defense_results if r.success])
        profile.performance_metrics['success_rate'] = successful_actions / total_actions if total_actions > 0 else 1.0
        
        # Update defense effectiveness
        effectiveness_scores = [r.effectiveness_score for r in profile.defense_results]
        profile.performance_metrics['defense_effectiveness'] = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 1.0
    
    # Defense action execution methods (simulated)
    def _execute_ip_blocking(self, target: str, parameters: Dict[str, Any]) -> bool:
        """Execute IP blocking"""
        print(f"🔒 Blocking IP: {target} for {parameters.get('duration', 3600)} seconds")
        return random.random() < 0.95
    
    def _execute_traffic_redirect(self, target: str, parameters: Dict[str, Any]) -> bool:
        """Execute traffic redirection"""
        print(f"🔄 Redirecting traffic from {target} to {parameters.get('redirect_to', 'honeypot')}")
        return random.random() < 0.83
    
    def _execute_network_segmentation(self, target: str, parameters: Dict[str, Any]) -> bool:
        """Execute network segmentation"""
        print(f"🌐 Segmenting network: {target}")
        return random.random() < 0.87
    
    def _execute_rate_limiting(self, target: str, parameters: Dict[str, Any]) -> bool:
        """Execute rate limiting"""
        print(f"⏱️ Rate limiting {target} to {parameters.get('requests_per_second', 10)} req/s")
        return random.random() < 0.88
    
    def _execute_process_termination(self, target: str, parameters: Dict[str, Any]) -> bool:
        """Execute process termination"""
        print(f"⚡ Terminating process on {target}")
        return random.random() < 0.85
    
    def _execute_system_isolation(self, target: str, parameters: Dict[str, Any]) -> bool:
        """Execute system isolation"""
        print(f"🔒 Isolating system: {target}")
        return random.random() < 0.90
    
    def _execute_data_encryption(self, target: str, parameters: Dict[str, Any]) -> bool:
        """Execute data encryption"""
        print(f"🔐 Encrypting data on {target}")
        return random.random() < 0.94
    
    def _execute_backup_creation(self, target: str, parameters: Dict[str, Any]) -> bool:
        """Execute backup creation"""
        print(f"💾 Creating backup of {target}")
        return random.random() < 0.96
    
    def _execute_account_disabling(self, target: str, parameters: Dict[str, Any]) -> bool:
        """Execute account disabling"""
        print(f"🚫 Disabling account: {target}")
        return random.random() < 0.92
    
    def _execute_privilege_revocation(self, target: str, parameters: Dict[str, Any]) -> bool:
        """Execute privilege revocation"""
        print(f"🔑 Revoking privileges for: {target}")
        return random.random() < 0.89
    
    def _execute_evidence_capture(self, target: str, parameters: Dict[str, Any]) -> bool:
        """Execute evidence capture"""
        print(f"🔍 Capturing forensic evidence from {target}")
        return random.random() < 0.93
    
    def _execute_honeypot_deployment(self, target: str, parameters: Dict[str, Any]) -> bool:
        """Execute honeypot deployment"""
        print(f"🎯 Deploying honeypot on {target}")
        return random.random() < 0.91
    
    def get_profile_summary(self, system_id: str) -> Dict[str, Any]:
        """Get active defense profile summary"""
        profile = self.profiles.get(system_id)
        if not profile:
            return {'error': 'Profile not found'}
        
        # Calculate statistics
        recent_actions = list(profile.defense_actions)[-100:]
        recent_results = list(profile.defense_results)[-100:]
        
        action_success_rate = len([r for r in recent_results if r.success]) / len(recent_results) if recent_results else 1.0
        
        return {
            'system_id': system_id,
            'total_threats': profile.total_threats,
            'total_actions': profile.total_actions,
            'current_threats': profile.system_status['current_threats'],
            'active_defenses': profile.system_status['active_defenses'],
            'system_health': profile.system_status['system_health'],
            'success_rate': action_success_rate,
            'performance_metrics': profile.performance_metrics,
            'last_updated': profile.last_updated.isoformat()
        }
    
    def get_system_performance(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        total_success_rate = self.successful_defenses / max(1, self.total_actions)
        
        return {
            'total_threats': self.total_threats,
            'total_actions': self.total_actions,
            'successful_defenses': self.successful_defenses,
            'failed_defenses': self.failed_defenses,
            'overall_success_rate': total_success_rate,
            'active_profiles': len(self.profiles),
            'defense_config': self.defense_config,
            'defense_engines': list(self.defense_engines.keys())
        }

# Test the active defense system
def test_active_defense_system():
    """Test the active defense system"""
    print("🛡️ Testing Active Defense System")
    print("=" * 50)
    
    defense_system = ActiveDefenseSystem()
    
    # Create test system profile
    print("\n🖥️ Creating Test System Profile...")
    
    system_id = "production_server_001"
    profile = defense_system.create_profile(system_id)
    
    # Simulate various threats
    print("\n🚨 Simulating Security Threats...")
    
    # DDoS attack
    threat1 = Threat(
        threat_id="ddos_attack_001",
        threat_type="ddos_attack",
        severity=ThreatLevel.CRITICAL,
        source_ip="192.168.1.100",
        target_system="web_server_01",
        attack_vector="HTTP Flood",
        confidence=0.92,
        timestamp=datetime.now(),
        metadata={'requests_per_second': 10000, 'attack_duration': 300}
    )
    
    actions1 = defense_system.detect_threat(system_id, threat1)
    print(f"   DDoS Attack: {len(actions1)} defense actions initiated")
    
    # Brute force attack
    threat2 = Threat(
        threat_id="brute_force_001",
        threat_type="brute_force",
        severity=ThreatLevel.HIGH,
        source_ip="10.0.0.50",
        target_system="auth_server_01",
        attack_vector="Password Spraying",
        confidence=0.85,
        timestamp=datetime.now(),
        metadata={'account_id': 'admin_user', 'failed_attempts': 50}
    )
    
    actions2 = defense_system.detect_threat(system_id, threat2)
    print(f"   Brute Force Attack: {len(actions2)} defense actions initiated")
    
    # Malware infection
    threat3 = Threat(
        threat_id="malware_001",
        threat_type="malware_infection",
        severity=ThreatLevel.CRITICAL,
        source_ip="172.16.0.25",
        target_system="database_server_01",
        attack_vector="Ransomware",
        confidence=0.94,
        timestamp=datetime.now(),
        metadata={'process_id': 1234, 'malware_hash': 'a1b2c3d4'}
    )
    
    actions3 = defense_system.detect_threat(system_id, threat3)
    print(f"   Malware Infection: {len(actions3)} defense actions initiated")
    
    # Data exfiltration attempt
    threat4 = Threat(
        threat_id="data_exfil_001",
        threat_type="data_exfiltration",
        severity=ThreatLevel.HIGH,
        source_ip="203.0.113.10",
        target_system="file_server_01",
        attack_vector="Unauthorized Data Transfer",
        confidence=0.88,
        timestamp=datetime.now(),
        metadata={'data_volume': 5000000000, 'file_types': ['csv', 'json']}
    )
    
    actions4 = defense_system.detect_threat(system_id, threat4)
    print(f"   Data Exfiltration: {len(actions4)} defense actions initiated")
    
    # Vulnerability exploit
    threat5 = Threat(
        threat_id="vuln_exploit_001",
        threat_type="vulnerability_exploit",
        severity=ThreatLevel.CRITICAL,
        source_ip="198.51.100.5",
        target_system="app_server_01",
        attack_vector="SQL Injection",
        confidence=0.91,
        timestamp=datetime.now(),
        metadata={'vuln_id': 'CVE-2024-0001', 'exploit_payload': 'SELECT * FROM users'}
    )
    
    actions5 = defense_system.detect_threat(system_id, threat5)
    print(f"   Vulnerability Exploit: {len(actions5)} defense actions initiated")
    
    # Generate defense report
    print("\n📋 Generating Defense Report...")
    
    summary = defense_system.get_profile_summary(system_id)
    
    print("\n📄 ACTIVE DEFENSE SUMMARY:")
    print(f"   Total Threats Detected: {summary['total_threats']}")
    print(f"   Total Defense Actions: {summary['total_actions']}")
    print(f"   Current Active Threats: {summary['current_threats']}")
    print(f"   Active Defenses: {summary['active_defenses']}")
    print(f"   System Health: {summary['system_health']:.3f}")
    print(f"   Defense Success Rate: {summary['success_rate']:.2%}")
    
    print("\n📊 PERFORMANCE METRICS:")
    metrics = summary['performance_metrics']
    print(f"   Average Response Time: {metrics['response_time']:.3f}s")
    print(f"   Success Rate: {metrics['success_rate']:.2%}")
    print(f"   False Positive Rate: {metrics['false_positive_rate']:.2%}")
    print(f"   Defense Effectiveness: {metrics['defense_effectiveness']:.2%}")
    
    print("\n🎯 DEFENSE ACTIONS BREAKDOWN:")
    action_counts = defaultdict(int)
    for action in profile.defense_actions:
        action_counts[action.action_type] += 1
    
    for action_type, count in action_counts.items():
        print(f"   {action_type}: {count} actions")
    
    print("\n📈 DEFENSE RESULTS:")
    successful_results = len([r for r in profile.defense_results if r.success])
    total_results = len(profile.defense_results)
    print(f"   Successful Defenses: {successful_results}/{total_results}")
    print(f"   Overall Success Rate: {successful_results/total_results:.2%}" if total_results > 0 else "   Overall Success Rate: N/A")
    
    # System performance
    print("\n📊 SYSTEM PERFORMANCE:")
    performance = defense_system.get_system_performance()
    print(f"   Total Threats: {performance['total_threats']}")
    print(f"   Total Actions: {performance['total_actions']}")
    print(f"   Successful Defenses: {performance['successful_defenses']}")
    print(f"   Failed Defenses: {performance['failed_defenses']}")
    print(f"   Overall Success Rate: {performance['overall_success_rate']:.2%}")
    print(f"   Active Profiles: {performance['active_profiles']}")
    
    return defense_system

if __name__ == "__main__":
    test_active_defense_system()
