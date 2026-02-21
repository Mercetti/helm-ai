#!/usr/bin/env python3
"""
Compliance & Audit Dashboard
Audit logging, compliance monitoring, risk assessment, policy management, and incident tracking
"""

import os
import sys
import time
import json
import logging
import threading
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING = "pending"
    EXEMPT = "exempt"
    UNKNOWN = "unknown"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditEventType(Enum):
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    DATA_ACCESS = "data_access"
    SYSTEM_CHANGE = "system_change"
    CONFIG_UPDATE = "config_update"
    SECURITY_EVENT = "security_event"
    COMPLIANCE_CHECK = "compliance_check"
    POLICY_VIOLATION = "policy_violation"
    INCIDENT_REPORT = "incident_report"

@dataclass
class AuditLogEntry:
    """Audit log entry structure"""
    timestamp: datetime
    event_type: AuditEventType
    user_id: str
    session_id: str
    ip_address: str
    user_agent: str
    resource_accessed: str
    action_performed: str
    outcome: str  # success, failure, warning
    risk_level: RiskLevel
    compliance_impact: str
    details: Dict[str, Any]
    correlation_id: str

@dataclass
class ComplianceCheck:
    """Compliance check data structure"""
    check_id: str
    name: str
    category: str  # security, privacy, operational, regulatory
    description: str
    status: ComplianceStatus
    last_checked: datetime
    next_check: datetime
    score: float  # 0-100
    risk_level: RiskLevel
    requirements_met: List[str]
    requirements_failed: List[str]
    evidence: List[str]
    remediation_steps: List[str]
    assigned_to: str
    due_date: Optional[datetime]

@dataclass
class PolicyViolation:
    """Policy violation data structure"""
    violation_id: str
    policy_name: str
    policy_category: str
    severity: RiskLevel
    detected_at: datetime
    user_id: str
    description: str
    impact_assessment: str
    remediation_required: bool
    remediation_due: Optional[datetime]
    status: str  # open, in_progress, resolved, false_positive
    assigned_to: str
    resolution_notes: str

@dataclass
class SecurityIncident:
    """Security incident data structure"""
    incident_id: str
    incident_type: str
    severity: RiskLevel
    detected_at: datetime
    reported_by: str
    description: str
    affected_systems: List[str]
    affected_users: List[str]
    containment_status: str  # not_contained, contained, resolved
    investigation_status: str  # open, investigating, resolved, closed
    root_cause: str
    impact_assessment: str
    lessons_learned: str
    prevention_measures: List[str]

class ComplianceAuditSystem:
    """Compliance & Audit Management System"""
    
    def __init__(self):
        self.logger = logging.getLogger("compliance_audit_system")
        self.audit_logs = deque(maxlen=10000)  # Last 10,000 audit entries
        self.compliance_checks = {}
        self.policy_violations = {}
        self.security_incidents = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        self.check_interval = 300  # 5 minutes
        
        # Compliance frameworks configuration
        self.compliance_frameworks = {
            "GDPR": {
                "name": "General Data Protection Regulation",
                "requirements": [
                    "data_protection_by_design",
                    "data_minimization",
                    "consent_management",
                    "data_subject_rights",
                    "breach_notification",
                    "privacy_impact_assessment"
                ]
            },
            "SOC2": {
                "name": "Service Organization Control 2",
                "requirements": [
                    "security_controls",
                    "availability_controls",
                    "processing_integrity",
                    "confidentiality_controls",
                    "privacy_controls"
                ]
            },
            "HIPAA": {
                "name": "Health Insurance Portability and Accountability Act",
                "requirements": [
                    "administrative_safeguards",
                    "physical_safeguards",
                    "technical_safeguards",
                    "breach_notification",
                    "risk_assessment"
                ]
            },
            "ISO27001": {
                "name": "ISO 27001 Information Security Management",
                "requirements": [
                    "information_security_policy",
                    "risk_assessment",
                    "security_controls",
                    "incident_management",
                    "business_continuity"
                ]
            }
        }
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample compliance and audit data"""
        import random
        
        # Generate sample audit logs
        event_types = list(AuditEventType)
        risk_levels = list(RiskLevel)
        outcomes = ["success", "failure", "warning"]
        
        for i in range(100):
            timestamp = datetime.now() - timedelta(hours=random.randint(1, 168))  # Last week
            event_type = random.choice(event_types)
            risk_level = random.choice(risk_levels)
            outcome = random.choice(outcomes)
            
            audit_entry = AuditLogEntry(
                timestamp=timestamp,
                event_type=event_type,
                user_id=f"user_{random.randint(1, 50)}",
                session_id=str(uuid.uuid4()),
                ip_address=f"192.168.1.{random.randint(1, 254)}",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                resource_accessed=f"/api/v1/{random.choice(['ai-performance', 'system-health', 'financial', 'analytics'])}",
                action_performed=random.choice(["GET", "POST", "PUT", "DELETE"]),
                outcome=outcome,
                risk_level=risk_level,
                compliance_impact=random.choice(["none", "low", "medium", "high"]),
                details={
                    "request_id": str(uuid.uuid4()),
                    "response_time": random.uniform(100, 2000),
                    "data_volume": random.randint(1, 1000)
                },
                correlation_id=str(uuid.uuid4())
            )
            
            self.audit_logs.append(audit_entry)
        
        # Generate sample compliance checks
        categories = ["security", "privacy", "operational", "regulatory"]
        statuses = list(ComplianceStatus)
        
        for framework, config in self.compliance_frameworks.items():
            for requirement in config["requirements"]:
                check_id = f"{framework}_{requirement}"
                status = random.choice(statuses)
                score = random.uniform(60, 100) if status == ComplianceStatus.COMPLIANT else random.uniform(0, 60)
                
                compliance_check = ComplianceCheck(
                    check_id=check_id,
                    name=f"{framework} - {requirement.replace('_', ' ').title()}",
                    category=random.choice(categories),
                    description=f"Compliance check for {requirement} under {framework}",
                    status=status,
                    last_checked=datetime.now() - timedelta(days=random.randint(1, 30)),
                    next_check=datetime.now() + timedelta(days=random.randint(1, 90)),
                    score=score,
                    risk_level=RiskLevel.LOW if score > 80 else RiskLevel.MEDIUM if score > 60 else RiskLevel.HIGH,
                    requirements_met=random.sample(config["requirements"], random.randint(1, 3)),
                    requirements_failed=random.sample(config["requirements"], random.randint(0, 2)),
                    evidence=[f"evidence_{i}" for i in range(random.randint(1, 5))],
                    remediation_steps=[f"step_{i}" for i in range(random.randint(1, 3))],
                    assigned_to=f"compliance_officer_{random.randint(1, 5)}",
                    due_date=datetime.now() + timedelta(days=random.randint(1, 90)) if status != ComplianceStatus.COMPLIANT else None
                )
                
                self.compliance_checks[check_id] = compliance_check
        
        # Generate sample policy violations
        policies = [
            "Data Access Policy",
            "Password Policy",
            "Encryption Policy",
            "Incident Response Policy",
            "Change Management Policy"
        ]
        
        for i in range(20):
            violation_id = f"violation_{i+1}"
            policy = random.choice(policies)
            
            violation = PolicyViolation(
                violation_id=violation_id,
                policy_name=policy,
                policy_category=random.choice(["security", "privacy", "operational"]),
                severity=random.choice(list(RiskLevel)),
                detected_at=datetime.now() - timedelta(days=random.randint(1, 60)),
                user_id=f"user_{random.randint(1, 50)}",
                description=f"Violation of {policy} detected",
                impact_assessment=random.choice(["low", "medium", "high", "critical"]),
                remediation_required=random.choice([True, False]),
                remediation_due=datetime.now() + timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
                status=random.choice(["open", "in_progress", "resolved", "false_positive"]),
                assigned_to=f"security_analyst_{random.randint(1, 5)}",
                resolution_notes=random.choice(["", "Resolved by updating configuration", "False positive - no action needed"])
            )
            
            self.policy_violations[violation_id] = violation
        
        # Generate sample security incidents
        incident_types = [
            "Unauthorized Access Attempt",
            "Data Breach",
            "Malware Detection",
            "Phishing Attack",
            "Denial of Service",
            "Insider Threat"
        ]
        
        for i in range(10):
            incident_id = f"incident_{i+1}"
            incident_type = random.choice(incident_types)
            
            incident = SecurityIncident(
                incident_id=incident_id,
                incident_type=incident_type,
                severity=random.choice(list(RiskLevel)),
                detected_at=datetime.now() - timedelta(days=random.randint(1, 90)),
                reported_by=f"user_{random.randint(1, 50)}",
                description=f"{incident_type} detected and reported",
                affected_systems=random.sample(["AI System", "Database", "API Gateway", "Web Server"], random.randint(1, 3)),
                affected_users=[f"user_{j}" for j in random.sample(range(1, 50), random.randint(0, 10))],
                containment_status=random.choice(["not_contained", "contained", "resolved"]),
                investigation_status=random.choice(["open", "investigating", "resolved", "closed"]),
                root_cause=random.choice(["", "Misconfigured firewall", "Weak password", "Software vulnerability"]),
                impact_assessment=random.choice(["low", "medium", "high", "critical"]),
                lessons_learned=random.choice(["", "Need better monitoring", "Update security policies", "Improve user training"]),
                prevention_measures=random.sample(["Update firewall rules", "Implement MFA", "Regular security training"], random.randint(1, 3))
            )
            
            self.security_incidents[incident_id] = incident
        
        self.logger.info(f"Initialized compliance audit system with {len(self.audit_logs)} audit logs, {len(self.compliance_checks)} compliance checks, {len(self.policy_violations)} policy violations, and {len(self.security_incidents)} security incidents")
    
    def start_monitoring(self):
        """Start compliance monitoring"""
        if self.monitoring_active:
            self.logger.warning("Compliance monitoring is already running")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Compliance monitoring started")
    
    def stop_monitoring(self):
        """Stop compliance monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        self.logger.info("Compliance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Perform compliance checks
                self._perform_compliance_checks()
                
                # Analyze audit logs for anomalies
                self._analyze_audit_anomalies()
                
                # Check for policy violations
                self._check_policy_violations()
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in compliance monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _perform_compliance_checks(self):
        """Perform automated compliance checks"""
        for check_id, check in self.compliance_checks.items():
            # Simulate compliance check
            import random
            
            # Update last checked time
            check.last_checked = datetime.now()
            
            # Simulate check results
            if random.random() > 0.9:  # 10% chance of status change
                if check.status == ComplianceStatus.COMPLIANT:
                    check.status = ComplianceStatus.PENDING
                    check.score = random.uniform(70, 90)
                elif check.status == ComplianceStatus.PENDING:
                    check.status = ComplianceStatus.NON_COMPLIANT
                    check.score = random.uniform(30, 70)
                else:
                    check.status = ComplianceStatus.COMPLIANT
                    check.score = random.uniform(85, 100)
                
                # Update risk level based on score
                if check.score > 80:
                    check.risk_level = RiskLevel.LOW
                elif check.score > 60:
                    check.risk_level = RiskLevel.MEDIUM
                else:
                    check.risk_level = RiskLevel.HIGH
            
            # Log compliance check
            audit_entry = AuditLogEntry(
                timestamp=datetime.now(),
                event_type=AuditEventType.COMPLIANCE_CHECK,
                user_id="system",
                session_id="system",
                ip_address="127.0.0.1",
                user_agent="Compliance Monitor",
                resource_accessed=f"/compliance/check/{check_id}",
                action_performed="COMPLIANCE_CHECK",
                outcome="success" if check.status == ComplianceStatus.COMPLIANT else "warning",
                risk_level=check.risk_level,
                compliance_impact="high" if check.status != ComplianceStatus.COMPLIANT else "low",
                details={
                    "check_id": check_id,
                    "check_name": check.name,
                    "score": check.score,
                    "status": check.status.value
                },
                correlation_id=str(uuid.uuid4())
            )
            
            self.audit_logs.append(audit_entry)
    
    def _analyze_audit_anomalies(self):
        """Analyze audit logs for anomalies"""
        if len(self.audit_logs) < 10:
            return
        
        # Get recent logs (last hour)
        recent_logs = [
            log for log in self.audit_logs
            if datetime.now() - log.timestamp < timedelta(hours=1)
        ]
        
        # Check for failed login attempts
        failed_logins = [
            log for log in recent_logs
            if log.event_type == AuditEventType.USER_LOGIN and log.outcome == "failure"
        ]
        
        # Detect brute force attempts
        user_failed_attempts = defaultdict(int)
        for log in failed_logins:
            user_failed_attempts[log.user_id] += 1
        
        for user_id, count in user_failed_attempts.items():
            if count > 5:  # More than 5 failed attempts in an hour
                # Create security incident
                incident_id = f"brute_force_{user_id}_{int(time.time())}"
                
                incident = SecurityIncident(
                    incident_id=incident_id,
                    incident_type="Brute Force Attack",
                    severity=RiskLevel.HIGH if count > 10 else RiskLevel.MEDIUM,
                    detected_at=datetime.now(),
                    reported_by="system",
                    description=f"Multiple failed login attempts detected for user {user_id}",
                    affected_systems=["Authentication System"],
                    affected_users=[user_id],
                    containment_status="contained",
                    investigation_status="open",
                    root_cause="Potential brute force attack",
                    impact_assessment="medium",
                    lessons_learned="",
                    prevention_measures=["Account lockout policy", "Rate limiting"]
                )
                
                self.security_incidents[incident_id] = incident
                
                # Log the detection
                audit_entry = AuditLogEntry(
                    timestamp=datetime.now(),
                    event_type=AuditEventType.SECURITY_EVENT,
                    user_id="system",
                    session_id="system",
                    ip_address="127.0.0.1",
                    user_agent="Security Monitor",
                    resource_accessed=f"/security/incident/{incident_id}",
                    action_performed="SECURITY_INCIDENT_CREATED",
                    outcome="success",
                    risk_level=RiskLevel.HIGH,
                    compliance_impact="high",
                    details={
                        "incident_id": incident_id,
                        "incident_type": "Brute Force Attack",
                        "target_user": user_id,
                        "failed_attempts": count
                    },
                    correlation_id=str(uuid.uuid4())
                )
                
                self.audit_logs.append(audit_entry)
    
    def _check_policy_violations(self):
        """Check for policy violations"""
        # Simulate policy violation detection
        import random
        
        if random.random() > 0.95:  # 5% chance of detecting a violation
            violation_id = f"violation_{int(time.time())}"
            policies = ["Data Access Policy", "Password Policy", "Encryption Policy"]
            policy = random.choice(policies)
            
            violation = PolicyViolation(
                violation_id=violation_id,
                policy_name=policy,
                policy_category="security",
                severity=random.choice([RiskLevel.MEDIUM, RiskLevel.HIGH]),
                detected_at=datetime.now(),
                user_id=f"user_{random.randint(1, 50)}",
                description=f"Violation of {policy} detected",
                impact_assessment=random.choice(["medium", "high"]),
                remediation_required=True,
                remediation_due=datetime.now() + timedelta(days=7),
                status="open",
                assigned_to=f"security_analyst_{random.randint(1, 5)}",
                resolution_notes=""
            )
            
            self.policy_violations[violation_id] = violation
            
            # Log the violation
            audit_entry = AuditLogEntry(
                timestamp=datetime.now(),
                event_type=AuditEventType.POLICY_VIOLATION,
                user_id="system",
                session_id="system",
                ip_address="127.0.0.1",
                user_agent="Policy Monitor",
                resource_accessed=f"/policy/violation/{violation_id}",
                action_performed="POLICY_VIOLATION_DETECTED",
                outcome="warning",
                risk_level=violation.severity,
                compliance_impact="high",
                details={
                    "violation_id": violation_id,
                    "policy_name": policy,
                    "user_id": violation.user_id
                },
                correlation_id=str(uuid.uuid4())
            )
            
            self.audit_logs.append(audit_entry)
    
    def log_audit_event(self, event_type: AuditEventType, user_id: str, resource_accessed: str, 
                       action_performed: str, outcome: str, risk_level: RiskLevel,
                       details: Dict[str, Any] = None) -> str:
        """Log an audit event"""
        audit_entry = AuditLogEntry(
            timestamp=datetime.now(),
            event_type=event_type,
            user_id=user_id,
            session_id=str(uuid.uuid4()),
            ip_address="127.0.0.1",  # Would get from request
            user_agent="Stellar Logic AI Dashboard",
            resource_accessed=resource_accessed,
            action_performed=action_performed,
            outcome=outcome,
            risk_level=risk_level,
            compliance_impact="low",  # Would calculate based on event
            details=details or {},
            correlation_id=str(uuid.uuid4())
        )
        
        self.audit_logs.append(audit_entry)
        return audit_entry.correlation_id
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get compliance summary"""
        total_checks = len(self.compliance_checks)
        compliant_checks = len([c for c in self.compliance_checks.values() if c.status == ComplianceStatus.COMPLIANT])
        non_compliant_checks = len([c for c in self.compliance_checks.values() if c.status == ComplianceStatus.NON_COMPLIANT])
        pending_checks = len([c for c in self.compliance_checks.values() if c.status == ComplianceStatus.PENDING])
        
        # Calculate overall compliance score
        if total_checks > 0:
            overall_score = sum(c.score for c in self.compliance_checks.values()) / total_checks
        else:
            overall_score = 0
        
        # Count by risk level
        risk_counts = defaultdict(int)
        for check in self.compliance_checks.values():
            risk_counts[check.risk_level.value] += 1
        
        return {
            "total_checks": total_checks,
            "compliant_checks": compliant_checks,
            "non_compliant_checks": non_compliant_checks,
            "pending_checks": pending_checks,
            "overall_compliance_score": round(overall_score, 2),
            "compliance_percentage": round((compliant_checks / total_checks * 100) if total_checks > 0 else 0, 2),
            "risk_distribution": dict(risk_counts),
            "last_updated": datetime.now().isoformat()
        }
    
    def get_audit_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get audit summary for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_logs = [log for log in self.audit_logs if log.timestamp >= cutoff_time]
        
        # Count by event type
        event_counts = defaultdict(int)
        for log in recent_logs:
            event_counts[log.event_type.value] += 1
        
        # Count by outcome
        outcome_counts = defaultdict(int)
        for log in recent_logs:
            outcome_counts[log.outcome] += 1
        
        # Count by risk level
        risk_counts = defaultdict(int)
        for log in recent_logs:
            risk_counts[log.risk_level.value] += 1
        
        # Get top users by activity
        user_counts = defaultdict(int)
        for log in recent_logs:
            user_counts[log.user_id] += 1
        
        top_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "period_hours": hours,
            "total_events": len(recent_logs),
            "event_distribution": dict(event_counts),
            "outcome_distribution": dict(outcome_counts),
            "risk_distribution": dict(risk_counts),
            "top_users": [{"user_id": user, "event_count": count} for user, count in top_users],
            "last_updated": datetime.now().isoformat()
        }
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary"""
        total_incidents = len(self.security_incidents)
        total_violations = len(self.policy_violations)
        
        # Count incidents by status
        incident_status_counts = defaultdict(int)
        for incident in self.security_incidents.values():
            incident_status_counts[incident.investigation_status] += 1
        
        # Count incidents by severity
        incident_severity_counts = defaultdict(int)
        for incident in self.security_incidents.values():
            incident_severity_counts[incident.severity.value] += 1
        
        # Count violations by status
        violation_status_counts = defaultdict(int)
        for violation in self.policy_violations.values():
            violation_status_counts[violation.status] += 1
        
        # Count violations by severity
        violation_severity_counts = defaultdict(int)
        for violation in self.policy_violations.values():
            violation_severity_counts[violation.severity.value] += 1
        
        # Get recent incidents (last 7 days)
        recent_incidents = [
            incident for incident in self.security_incidents.values()
            if datetime.now() - incident.detected_at < timedelta(days=7)
        ]
        
        # Get recent violations (last 7 days)
        recent_violations = [
            violation for violation in self.policy_violations.values()
            if datetime.now() - violation.detected_at < timedelta(days=7)
        ]
        
        return {
            "total_incidents": total_incidents,
            "total_violations": total_violations,
            "recent_incidents": len(recent_incidents),
            "recent_violations": len(recent_violations),
            "incident_status_distribution": dict(incident_status_counts),
            "incident_severity_distribution": dict(incident_severity_counts),
            "violation_status_distribution": dict(violation_status_counts),
            "violation_severity_distribution": dict(violation_severity_counts),
            "last_updated": datetime.now().isoformat()
        }

# Global compliance audit system instance
compliance_audit_system = ComplianceAuditSystem()
