"""
Helm AI Security Incident Response Procedures
Provides incident response management, escalation, and remediation
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from database.database_manager import get_database_manager
from security.security_monitoring import SecurityAlert, security_monitor

class IncidentSeverity(Enum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(Enum):
    """Incident status values"""
    NEW = "new"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"

class IncidentCategory(Enum):
    """Incident categories"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    MALWARE = "malware"
    DENIAL_OF_SERVICE = "denial_of_service"
    INSIDER_THREAT = "insider_threat"
    PHISHING = "phishing"
    VULNERABILITY = "vulnerability"
    MISCONFIGURATION = "misconfiguration"
    OTHER = "other"

@dataclass
class Incident:
    """Security incident record"""
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    category: IncidentCategory
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
    detected_by: str
    assigned_to: Optional[str] = None
    affected_systems: List[str] = field(default_factory=list)
    affected_data: List[str] = field(default_factory=list)
    impact_assessment: Dict[str, Any] = field(default_factory=dict)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    actions_taken: List[str] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    root_cause: Optional[str] = None
    resolution: Optional[str] = None
    lessons_learned: List[str] = field(default_factory=list)
    prevention_measures: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'incident_id': self.incident_id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity.value,
            'category': self.category.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'detected_by': self.detected_by,
            'assigned_to': self.assigned_to,
            'affected_systems': self.affected_systems,
            'affected_data': self.affected_data,
            'impact_assessment': self.impact_assessment,
            'timeline': self.timeline,
            'actions_taken': self.actions_taken,
            'evidence': self.evidence,
            'root_cause': self.root_cause,
            'resolution': self.resolution,
            'lessons_learned': self.lessons_learned,
            'prevention_measures': self.prevention_measures
        }

@dataclass
class IncidentResponsePlan:
    """Incident response plan"""
    plan_id: str
    name: str
    description: str
    category: IncidentCategory
    severity: IncidentSeverity
    steps: List[Dict[str, Any]]
    escalation_rules: List[Dict[str, Any]]
    communication_plan: Dict[str, Any]
    recovery_procedures: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'plan_id': self.plan_id,
            'name': self.name,
            'description': self.description,
            'category': self.category.value,
            'severity': self.severity.value,
            'steps': self.steps,
            'escalation_rules': self.escalation_rules,
            'communication_plan': self.communication_plan,
            'recovery_procedures': self.recovery_procedures
        }

class IncidentManager:
    """Security incident management system"""
    
    def __init__(self):
        self.incidents = deque(maxlen=1000)
        self.response_plans = self._setup_response_plans()
        self.escalation_matrix = self._setup_escalation_matrix()
        self.response_team = self._setup_response_team()
        self.active_incidents = {}
        self.lock = threading.RLock()
        
    def _setup_response_plans(self) -> Dict[str, IncidentResponsePlan]:
        """Setup incident response plans"""
        plans = {}
        
        # Unauthorized Access Response Plan
        plans['unauthorized_access'] = IncidentResponsePlan(
            plan_id='unauthorized_access',
            name='Unauthorized Access Response',
            description='Response plan for unauthorized access incidents',
            category=IncidentCategory.UNAUTHORIZED_ACCESS,
            severity=IncidentSeverity.HIGH,
            steps=[
                {'step': 1, 'action': 'Isolate affected systems', 'timeout': 15},
                {'step': 2, 'action': 'Preserve evidence', 'timeout': 30},
                {'step': 3, 'action': 'Identify unauthorized access points', 'timeout': 60},
                {'step': 4, 'action': 'Block malicious IPs', 'timeout': 30},
                {'step': 5, 'action': 'Reset compromised credentials', 'timeout': 45},
                {'step': 6, 'action': 'Patch vulnerabilities', 'timeout': 120},
                {'step': 7, 'action': 'Monitor for recurrence', 'timeout': 0}
            ],
            escalation_rules=[
                {'condition': 'critical_systems_affected', 'escalate_to': 'executive', 'timeout': 30},
                {'condition': 'data_exfiltration_detected', 'escalate_to': 'legal', 'timeout': 15}
            ],
            communication_plan={
                'internal': ['security_team', 'management', 'affected_teams'],
                'external': ['customers', 'regulators', 'law_enforcement'],
                'templates': ['initial_notification', 'progress_update', 'resolution_notice']
            },
            recovery_procedures=[
                'System restoration from backup',
                'Security hardening',
                'Access review',
                'User education'
            ]
        )
        
        # Data Breach Response Plan
        plans['data_breach'] = IncidentResponsePlan(
            plan_id='data_breach',
            name='Data Breach Response',
            description='Response plan for data breach incidents',
            category=IncidentCategory.DATA_BREACH,
            severity=IncidentSeverity.CRITICAL,
            steps=[
                {'step': 1, 'action': 'Contain breach', 'timeout': 15},
                {'step': 2, 'action': 'Assess data exposure', 'timeout': 60},
                {'step': 3, 'action': 'Notify legal team', 'timeout': 30},
                {'step': 4, 'action': 'Identify affected parties', 'timeout': 120},
                {'step': 5, 'action': 'Prepare regulatory notifications', 'timeout': 180},
                {'step': 6, 'action': 'Implement remediation', 'timeout': 240},
                {'step': 7, 'action': 'Post-incident review', 'timeout': 480}
            ],
            escalation_rules=[
                {'condition': 'pii_exposed', 'escalate_to': 'executive', 'timeout': 15},
                {'condition': 'regulatory_reporting_required', 'escalate_to': 'legal', 'timeout': 30}
            ],
            communication_plan={
                'internal': ['security_team', 'legal', 'executive', 'compliance'],
                'external': ['customers', 'regulators', 'media'],
                'templates': ['breach_notification', 'regulatory_filing', 'press_statement']
            },
            recovery_procedures=[
                'Data breach notification',
                'Credit monitoring services',
                'Security improvements',
                'Policy updates'
            ]
        )
        
        return plans
    
    def _setup_escalation_matrix(self) -> Dict[str, Dict[str, Any]]:
        """Setup escalation matrix"""
        return {
            'LOW': {
                'response_time': 24,  # hours
                'escalation_time': 72,
                'notification_level': 'team_lead',
                'required_actions': ['document', 'monitor', 'assess']
            },
            'MEDIUM': {
                'response_time': 8,
                'escalation_time': 24,
                'notification_level': 'manager',
                'required_actions': ['document', 'contain', 'investigate', 'report']
            },
            'HIGH': {
                'response_time': 4,
                'escalation_time': 12,
                'notification_level': 'director',
                'required_actions': ['document', 'contain', 'investigate', 'escalate', 'report']
            },
            'CRITICAL': {
                'response_time': 1,
                'escalation_time': 4,
                'notification_level': 'executive',
                'required_actions': ['document', 'contain', 'investigate', 'escalate', 'notify', 'report']
            }
        }
    
    def _setup_response_team(self) -> Dict[str, List[str]]:
        """Setup incident response team"""
        return {
            'security_team': ['security_lead', 'security_analyst', 'forensic_specialist'],
            'technical_team': ['system_admin', 'network_engineer', 'database_admin'],
            'management': ['cto', 'security_manager', 'operations_manager'],
            'legal': ['legal_counsel', 'compliance_officer'],
            'communications': ['pr_manager', 'customer_support'],
            'executive': ['ceo', 'ciso', 'board_members']
        }
    
    def create_incident(self, title: str, description: str, severity: IncidentSeverity,
                      category: IncidentCategory, detected_by: str,
                      affected_systems: List[str] = None,
                      affected_data: List[str] = None) -> Incident:
        """Create a new security incident"""
        incident = Incident(
            incident_id=secrets.token_hex(8),
            title=title,
            description=description,
            severity=severity,
            category=category,
            status=IncidentStatus.NEW,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            detected_by=detected_by,
            affected_systems=affected_systems or [],
            affected_data=affected_data or [],
            timeline=[{
                'timestamp': datetime.now().isoformat(),
                'event': 'incident_created',
                'description': f'Incident created by {detected_by}',
                'user': detected_by
            }]
        )
        
        with self.lock:
            self.incidents.append(incident)
            self.active_incidents[incident.incident_id] = incident
        
        # Trigger initial response
        self._trigger_initial_response(incident)
        
        logger.warning(f"Security incident created: {incident.incident_id} - {title}")
        
        return incident
    
    def _trigger_initial_response(self, incident: Incident):
        """Trigger initial incident response"""
        # Get response plan
        plan_key = incident.category.value
        response_plan = self.response_plans.get(plan_key)
        
        if not response_plan:
            logger.warning(f"No response plan found for category: {plan_key}")
            return
        
        # Get escalation rules
        escalation_rules = self.escalation_matrix[incident.severity.value]
        
        # Notify response team
        notification_level = escalation_rules['notification_level']
        team_members = self.response_team.get(notification_level, [])
        
        # Log notification
        incident.timeline.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'team_notified',
            'description': f'Notified {notification_level}: {team_members}',
            'user': 'system'
        })
        
        # Start response timer
        response_deadline = datetime.now() + timedelta(hours=escalation_rules['response_time'])
        
        incident.timeline.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'response_deadline_set',
            'description': f'Response deadline: {response_deadline.isoformat()}',
            'user': 'system'
        })
        
        # Update incident status
        incident.status = IncidentStatus.INVESTIGATING
        incident.updated_at = datetime.now()
        
        logger.info(f"Initial response triggered for incident {incident.incident_id}")
    
    def update_incident(self, incident_id: str, updates: Dict[str, Any], updated_by: str) -> bool:
        """Update incident with new information"""
        with self.lock:
            incident = self.active_incidents.get(incident_id)
            
            if not incident:
                logger.error(f"Incident not found: {incident_id}")
                return False
            
            # Update fields
            for field, value in updates.items():
                if hasattr(incident, field):
                    setattr(incident, field, value)
            
            incident.updated_at = datetime.now()
            
            # Add to timeline
            incident.timeline.append({
                'timestamp': datetime.now().isoformat(),
                'event': 'incident_updated',
                'description': f'Updated by {updated_by}: {list(updates.keys())}',
                'user': updated_by
            })
            
            logger.info(f"Incident {incident_id} updated by {updated_by}")
            
            return True
    
    def add_action(self, incident_id: str, action: str, taken_by: str) -> bool:
        """Add action taken to incident"""
        with self.lock:
            incident = self.active_incidents.get(incident_id)
            
            if not incident:
                logger.error(f"Incident not found: {incident_id}")
                return False
            
            incident.actions_taken.append(f"{datetime.now().isoformat()}: {action} (by {taken_by})")
            incident.updated_at = datetime.now()
            
            # Add to timeline
            incident.timeline.append({
                'timestamp': datetime.now().isoformat(),
                'event': 'action_taken',
                'description': f'Action: {action}',
                'user': taken_by
            })
            
            logger.info(f"Action added to incident {incident_id}: {action}")
            
            return True
    
    def add_evidence(self, incident_id: str, evidence_type: str, evidence_data: Dict[str, Any], collected_by: str) -> bool:
        """Add evidence to incident"""
        with self.lock:
            incident = self.active_incidents.get(incident_id)
            
            if not incident:
                logger.error(f"Incident not found: {incident_id}")
                return False
            
            evidence = {
                'type': evidence_type,
                'data': evidence_data,
                'collected_at': datetime.now().isoformat(),
                'collected_by': collected_by
            }
            
            incident.evidence.append(evidence)
            incident.updated_at = datetime.now()
            
            # Add to timeline
            incident.timeline.append({
                'timestamp': datetime.now().isoformat(),
                'event': 'evidence_collected',
                'description': f'Evidence type: {evidence_type}',
                'user': collected_by
            })
            
            logger.info(f"Evidence added to incident {incident_id}: {evidence_type}")
            
            return True
    
    def escalate_incident(self, incident_id: str, reason: str, escalated_by: str) -> bool:
        """Escalate incident to higher level"""
        with self.lock:
            incident = self.active_incidents.get(incident_id)
            
            if not incident:
                logger.error(f"Incident not found: {incident_id}")
                return False
            
            # Determine next severity level
            severity_levels = [IncidentSeverity.LOW, IncidentSeverity.MEDIUM, IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]
            current_index = severity_levels.index(incident.severity)
            
            if current_index < len(severity_levels) - 1:
                incident.severity = severity_levels[current_index + 1]
                
                # Add to timeline
                incident.timeline.append({
                    'timestamp': datetime.now().isoformat(),
                    'event': 'incident_escalated',
                    'description': f'Escalated to {incident.severity.value}. Reason: {reason}',
                    'user': escalated_by
                })
                
                incident.updated_at = datetime.now()
                
                # Re-trigger response with new severity
                self._trigger_initial_response(incident)
                
                logger.warning(f"Incident {incident_id} escalated to {incident.severity.value}")
                
                return True
            else:
                logger.warning(f"Incident {incident_id} already at maximum severity")
                return False
    
    def resolve_incident(self, incident_id: str, resolution: str, root_cause: str, resolved_by: str) -> bool:
        """Resolve incident"""
        with self.lock:
            incident = self.active_incidents.get(incident_id)
            
            if not incident:
                logger.error(f"Incident not found: {incident_id}")
                return False
            
            incident.status = IncidentStatus.RESOLVED
            incident.resolution = resolution
            incident.root_cause = root_cause
            incident.updated_at = datetime.now()
            
            # Add to timeline
            incident.timeline.append({
                'timestamp': datetime.now().isoformat(),
                'event': 'incident_resolved',
                'description': f'Resolved by {resolved_by}. Root cause: {root_cause}',
                'user': resolved_by
            })
            
            # Remove from active incidents
            self.active_incidents.pop(incident_id, None)
            
            logger.info(f"Incident {incident_id} resolved by {resolved_by}")
            
            return True
    
    def close_incident(self, incident_id: str, lessons_learned: List[str], prevention_measures: List[str], closed_by: str) -> bool:
        """Close incident with lessons learned"""
        with self.lock:
            incident = self.active_incidents.get(incident_id)
            
            if not incident:
                # Check in closed incidents
                incident = next((i for i in self.incidents if i.incident_id == incident_id), None)
                if not incident:
                    logger.error(f"Incident not found: {incident_id}")
                    return False
            
            incident.status = IncidentStatus.CLOSED
            incident.lessons_learned = lessons_learned
            incident.prevention_measures = prevention_measures
            incident.updated_at = datetime.now()
            
            # Add to timeline
            incident.timeline.append({
                'timestamp': datetime.now().isoformat(),
                'event': 'incident_closed',
                'description': f'Closed by {closed_by}',
                'user': closed_by
            })
            
            logger.info(f"Incident {incident_id} closed by {closed_by}")
            
            return True
    
    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get incident by ID"""
        with self.lock:
            return self.active_incidents.get(incident_id)
    
    def get_active_incidents(self) -> List[Incident]:
        """Get all active incidents"""
        with self.lock:
            return list(self.active_incidents.values())
    
    def get_incident_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get incident summary for specified period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.lock:
            recent_incidents = [i for i in self.incidents if i.created_at >= cutoff_date]
        
        if not recent_incidents:
            return {
                'period_days': days,
                'total_incidents': 0,
                'by_severity': {},
                'by_category': {},
                'by_status': {},
                'average_resolution_time': 0
            }
        
        # Group by severity
        by_severity = defaultdict(int)
        for incident in recent_incidents:
            by_severity[incident.severity.value] += 1
        
        # Group by category
        by_category = defaultdict(int)
        for incident in recent_incidents:
            by_category[incident.category.value] += 1
        
        # Group by status
        by_status = defaultdict(int)
        for incident in recent_incidents:
            by_status[incident.status.value] += 1
        
        # Calculate average resolution time
        resolved_incidents = [i for i in recent_incidents if i.status == IncidentStatus.RESOLVED]
        if resolved_incidents:
            resolution_times = [(i.updated_at - i.created_at).total_seconds() / 3600 for i in resolved_incidents]
            avg_resolution_time = sum(resolution_times) / len(resolution_times)
        else:
            avg_resolution_time = 0
        
        return {
            'period_days': days,
            'total_incidents': len(recent_incidents),
            'by_severity': dict(by_severity),
            'by_category': dict(by_category),
            'by_status': dict(by_status),
            'average_resolution_time': avg_resolution_time,
            'critical_count': len([i for i in recent_incidents if i.severity == IncidentSeverity.CRITICAL]),
            'high_count': len([i for i in recent_incidents if i.severity == IncidentSeverity.HIGH]),
            'resolution_rate': (len(resolved_incidents) / len(recent_incidents)) * 100 if recent_incidents else 0
        }

# Global incident manager instance
incident_manager = IncidentManager()

def create_incident(title: str, description: str, severity: str, category: str, detected_by: str,
                   affected_systems: List[str] = None, affected_data: List[str] = None) -> Incident:
    """Create a new security incident"""
    severity_enum = IncidentSeverity(severity.lower())
    category_enum = IncidentCategory(category.lower())
    
    return incident_manager.create_incident(
        title=title,
        description=description,
        severity=severity_enum,
        category=category_enum,
        detected_by=detected_by,
        affected_systems=affected_systems,
        affected_data=affected_data
    )

def get_incident_status() -> Dict[str, Any]:
    """Get comprehensive incident status"""
    return {
        'timestamp': datetime.now().isoformat(),
        'active_incidents': len(incident_manager.active_incidents),
        'incident_summary': incident_manager.get_incident_summary(),
        'response_plans': {k: v.to_dict() for k, v in incident_manager.response_plans.items()},
        'escalation_matrix': incident_manager.escalation_matrix,
        'response_team': incident_manager.response_team
    }
