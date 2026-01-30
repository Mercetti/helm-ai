"""
Helm AI Security Orchestration, Automation, and Response (SOAR) System
Provides automated security incident response and orchestration capabilities
"""

import os
import sys
import json
import time
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from security.encryption import EncryptionManager

class IncidentSeverity(Enum):
    """Incident severity enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(Enum):
    """Incident status enumeration"""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"

class IncidentType(Enum):
    """Incident type enumeration"""
    MALWARE = "malware"
    PHISHING = "phishing"
    DDOS = "ddos"
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    POLICY_VIOLATION = "policy_violation"
    SYSTEM_COMPROMISE = "system_compromise"
    INSIDER_THREAT = "insider_threat"
    VULNERABILITY = "vulnerability"
    OTHER = "other"

class PlaybookStatus(Enum):
    """Playbook status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    DEPRECATED = "deprecated"

class ActionType(Enum):
    """Action type enumeration"""
    AUTOMATED = "automated"
    MANUAL = "manual"
    SEMI_AUTOMATED = "semi_automated"
    APPROVAL_REQUIRED = "approval_required"

@dataclass
class SecurityIncident:
    """Security incident data structure"""
    incident_id: str
    title: str
    description: str
    incident_type: IncidentType
    severity: IncidentSeverity
    status: IncidentStatus
    source: str
    detected_at: datetime
    assigned_to: Optional[str]
    created_by: str
    affected_assets: List[str]
    indicators: List[Dict[str, Any]]
    timeline: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    tags: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert incident to dictionary"""
        return {
            'incident_id': self.incident_id,
            'title': self.title,
            'description': self.description,
            'incident_type': self.incident_type.value,
            'severity': self.severity.value,
            'status': self.status.value,
            'source': self.source,
            'detected_at': self.detected_at.isoformat(),
            'assigned_to': self.assigned_to,
            'created_by': self.created_by,
            'affected_assets': self.affected_assets,
            'indicators': self.indicators,
            'timeline': self.timeline,
            'evidence': self.evidence,
            'tags': self.tags,
            'metadata': self.metadata
        }

@dataclass
class PlaybookAction:
    """Playbook action definition"""
    action_id: str
    name: str
    description: str
    action_type: ActionType
    script_path: Optional[str]
    api_endpoint: Optional[str]
    parameters: Dict[str, Any]
    timeout: int
    retry_count: int
    dependencies: List[str]
    approval_required: bool
    approvers: List[str]
    success_criteria: Dict[str, Any]
    failure_criteria: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary"""
        return {
            'action_id': self.action_id,
            'name': self.name,
            'description': self.description,
            'action_type': self.action_type.value,
            'script_path': self.script_path,
            'api_endpoint': self.api_endpoint,
            'parameters': self.parameters,
            'timeout': self.timeout,
            'retry_count': self.retry_count,
            'dependencies': self.dependencies,
            'approval_required': self.approval_required,
            'approvers': self.approvers,
            'success_criteria': self.success_criteria,
            'failure_criteria': self.failure_criteria
        }

@dataclass
class Playbook:
    """Security playbook definition"""
    playbook_id: str
    name: str
    description: str
    incident_types: List[IncidentType]
    severity_levels: List[IncidentSeverity]
    status: PlaybookStatus
    version: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    actions: List[PlaybookAction]
    variables: Dict[str, Any]
    conditions: Dict[str, Any]
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert playbook to dictionary"""
        return {
            'playbook_id': self.playbook_id,
            'name': self.name,
            'description': self.description,
            'incident_types': [t.value for t in self.incident_types],
            'severity_levels': [s.value for s in self.severity_levels],
            'status': self.status.value,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'actions': [action.to_dict() for action in self.actions],
            'variables': self.variables,
            'conditions': self.conditions,
            'tags': self.tags
        }

@dataclass
class PlaybookExecution:
    """Playbook execution record"""
    execution_id: str
    playbook_id: str
    incident_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    status: str
    executed_by: str
    actions_executed: List[Dict[str, Any]]
    results: Dict[str, Any]
    errors: List[str]
    duration: Optional[float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert execution to dictionary"""
        return {
            'execution_id': self.execution_id,
            'playbook_id': self.playbook_id,
            'incident_id': self.incident_id,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'executed_by': self.executed_by,
            'actions_executed': self.actions_executed,
            'results': self.results,
            'errors': self.errors,
            'duration': self.duration
        }

class ActionExecutor:
    """Action execution engine"""
    
    def __init__(self, encryption_manager: Optional[EncryptionManager] = None):
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.script_directory = os.getenv('SOAR_SCRIPTS_DIR', 'scripts/soar')
        self.api_endpoints = {}
        self.credentials = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Ensure script directory exists
        os.makedirs(self.script_directory, exist_ok=True)
    
    def execute_action(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a playbook action"""
        try:
            execution_start = time.time()
            
            # Prepare execution context
            execution_context = self._prepare_context(action, context)
            
            # Execute based on action type
            if action.script_path:
                result = self._execute_script(action, execution_context)
            elif action.api_endpoint:
                result = self._execute_api_call(action, execution_context)
            else:
                result = self._execute_builtin_action(action, execution_context)
            
            execution_duration = time.time() - execution_start
            
            # Check success criteria
            success = self._check_success_criteria(action, result)
            
            return {
                'action_id': action.action_id,
                'status': 'success' if success else 'failed',
                'result': result,
                'duration': execution_duration,
                'executed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return {
                'action_id': action.action_id,
                'status': 'error',
                'error': str(e),
                'executed_at': datetime.utcnow().isoformat()
            }
    
    def _prepare_context(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare execution context"""
        execution_context = context.copy()
        
        # Add action parameters
        execution_context.update(action.parameters)
        
        # Add system variables
        execution_context.update({
            'execution_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'script_directory': self.script_directory
        })
        
        return execution_context
    
    def _execute_script(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute script action"""
        script_path = os.path.join(self.script_directory, action.script_path)
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        # Execute script with timeout
        try:
            import subprocess
            
            # Prepare command
            cmd = ['python', script_path]
            
            # Add parameters as environment variables
            env = os.environ.copy()
            for key, value in context.items():
                env[f'SOAR_{key.upper()}'] = str(value)
            
            # Execute script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=action.timeout,
                env=env
            )
            
            return {
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Script execution timed out after {action.timeout} seconds")
    
    def _execute_api_call(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call action"""
        import requests
        
        # Prepare request
        method = action.parameters.get('method', 'POST')
        headers = action.parameters.get('headers', {})
        data = action.parameters.get('data', {})
        
        # Add context to data
        data.update(context)
        
        # Make API call
        response = requests.request(
            method=method,
            url=action.api_endpoint,
            headers=headers,
            json=data,
            timeout=action.timeout
        )
        
        return {
            'status_code': response.status_code,
            'response': response.json() if response.content else {},
            'headers': dict(response.headers),
            'success': response.status_code < 400
        }
    
    def _execute_builtin_action(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute built-in action"""
        action_name = action.action_id.lower()
        
        if 'block_ip' in action_name:
            return self._block_ip_action(action, context)
        elif 'isolate_system' in action_name:
            return self._isolate_system_action(action, context)
        elif 'disable_account' in action_name:
            return self._disable_account_action(action, context)
        elif 'collect_evidence' in action_name:
            return self._collect_evidence_action(action, context)
        elif 'notify_team' in action_name:
            return self._notify_team_action(action, context)
        elif 'create_ticket' in action_name:
            return self._create_ticket_action(action, context)
        else:
            raise ValueError(f"Unknown built-in action: {action_name}")
    
    def _block_ip_action(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Block IP address action"""
        ip_address = context.get('ip_address')
        if not ip_address:
            raise ValueError("IP address not provided")
        
        # In production, this would integrate with firewall/IPS
        logger.info(f"Blocking IP address: {ip_address}")
        
        return {
            'action': 'block_ip',
            'ip_address': ip_address,
            'blocked': True,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _isolate_system_action(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Isolate system action"""
        system_id = context.get('system_id')
        if not system_id:
            raise ValueError("System ID not provided")
        
        # In production, this would integrate with EDR/network isolation
        logger.info(f"Isolating system: {system_id}")
        
        return {
            'action': 'isolate_system',
            'system_id': system_id,
            'isolated': True,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _disable_account_action(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Disable user account action"""
        user_id = context.get('user_id')
        if not user_id:
            raise ValueError("User ID not provided")
        
        # In production, this would integrate with Active Directory/LDAP
        logger.info(f"Disabling account: {user_id}")
        
        return {
            'action': 'disable_account',
            'user_id': user_id,
            'disabled': True,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _collect_evidence_action(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect evidence action"""
        incident_id = context.get('incident_id')
        evidence_type = context.get('evidence_type', 'logs')
        
        # In production, this would collect actual evidence
        logger.info(f"Collecting evidence for incident {incident_id}: {evidence_type}")
        
        return {
            'action': 'collect_evidence',
            'incident_id': incident_id,
            'evidence_type': evidence_type,
            'collected': True,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _notify_team_action(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Notify security team action"""
        team = context.get('team', 'security')
        message = context.get('message', 'Security incident detected')
        
        # In production, this would send actual notifications
        logger.info(f"Notifying {team} team: {message}")
        
        return {
            'action': 'notify_team',
            'team': team,
            'message': message,
            'notified': True,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _create_ticket_action(self, action: PlaybookAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create support ticket action"""
        title = context.get('title', 'Security Incident')
        description = context.get('description', 'Security incident requires investigation')
        
        # In production, this would integrate with ticketing system
        logger.info(f"Creating ticket: {title}")
        
        return {
            'action': 'create_ticket',
            'title': title,
            'description': description,
            'ticket_id': f"SEC-{uuid.uuid4().hex[:8]}",
            'created': True,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _check_success_criteria(self, action: PlaybookAction, result: Dict[str, Any]) -> bool:
        """Check if action meets success criteria"""
        if not action.success_criteria:
            return result.get('success', False)
        
        # Check each success criterion
        for criterion, expected_value in action.success_criteria.items():
            actual_value = result.get(criterion)
            if actual_value != expected_value:
                return False
        
        return True

class PlaybookEngine:
    """Playbook execution engine"""
    
    def __init__(self, action_executor: ActionExecutor):
        self.action_executor = action_executor
        self.playbooks: Dict[str, Playbook] = {}
        self.executions: Dict[str, PlaybookExecution] = {}
        self.active_executions: Dict[str, threading.Thread] = {}
        self.lock = threading.Lock()
        
        # Load default playbooks
        self._load_default_playbooks()
    
    def _load_default_playbooks(self) -> None:
        """Load default security playbooks"""
        # Malware Response Playbook
        malware_playbook = Playbook(
            playbook_id="malware_response",
            name="Malware Incident Response",
            description="Automated response to malware incidents",
            incident_types=[IncidentType.MALWARE],
            severity_levels=[IncidentSeverity.HIGH, IncidentSeverity.CRITICAL],
            status=PlaybookStatus.ACTIVE,
            version="1.0",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by="system",
            actions=[
                PlaybookAction(
                    action_id="isolate_affected_systems",
                    name="Isolate Affected Systems",
                    description="Isolate systems affected by malware",
                    action_type=ActionType.AUTOMATED,
                    script_path=None,
                    api_endpoint=None,
                    parameters={},
                    timeout=300,
                    retry_count=3,
                    dependencies=[],
                    approval_required=False,
                    approvers=[],
                    success_criteria={'isolated': True},
                    failure_criteria={}
                ),
                PlaybookAction(
                    action_id="block_malicious_ips",
                    name="Block Malicious IPs",
                    description="Block IP addresses associated with malware",
                    action_type=ActionType.AUTOMATED,
                    script_path=None,
                    api_endpoint=None,
                    parameters={},
                    timeout=60,
                    retry_count=2,
                    dependencies=[],
                    approval_required=False,
                    approvers=[],
                    success_criteria={'blocked': True},
                    failure_criteria={}
                ),
                PlaybookAction(
                    action_id="collect_forensic_evidence",
                    name="Collect Forensic Evidence",
                    description="Collect forensic evidence from affected systems",
                    action_type=ActionType.SEMI_AUTOMATED,
                    script_path=None,
                    api_endpoint=None,
                    parameters={},
                    timeout=600,
                    retry_count=1,
                    dependencies=["isolate_affected_systems"],
                    approval_required=True,
                    approvers=["security_manager"],
                    success_criteria={'collected': True},
                    failure_criteria={}
                ),
                PlaybookAction(
                    action_id="notify_security_team",
                    name="Notify Security Team",
                    description="Notify security team of malware incident",
                    action_type=ActionType.AUTOMATED,
                    script_path=None,
                    api_endpoint=None,
                    parameters={},
                    timeout=30,
                    retry_count=3,
                    dependencies=[],
                    approval_required=False,
                    approvers=[],
                    success_criteria={'notified': True},
                    failure_criteria={}
                )
            ],
            variables={},
            conditions={},
            tags=["malware", "automated", "critical"]
        )
        
        # Phishing Response Playbook
        phishing_playbook = Playbook(
            playbook_id="phishing_response",
            name="Phishing Incident Response",
            description="Automated response to phishing incidents",
            incident_types=[IncidentType.PHISHING],
            severity_levels=[IncidentSeverity.MEDIUM, IncidentSeverity.HIGH, IncidentSeverity.CRITICAL],
            status=PlaybookStatus.ACTIVE,
            version="1.0",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by="system",
            actions=[
                PlaybookAction(
                    action_id="block_phishing_domain",
                    name="Block Phishing Domain",
                    description="Block phishing domain in DNS and web filters",
                    action_type=ActionType.AUTOMATED,
                    script_path=None,
                    api_endpoint=None,
                    parameters={},
                    timeout=60,
                    retry_count=2,
                    dependencies=[],
                    approval_required=False,
                    approvers=[],
                    success_criteria={'blocked': True},
                    failure_criteria={}
                ),
                PlaybookAction(
                    action_id="quarantine_phishing_emails",
                    name="Quarantine Phishing Emails",
                    description="Quarantine phishing emails from mailboxes",
                    action_type=ActionType.AUTOMATED,
                    script_path=None,
                    api_endpoint=None,
                    parameters={},
                    timeout=300,
                    retry_count=1,
                    dependencies=[],
                    approval_required=False,
                    approvers=[],
                    success_criteria={'quarantined': True},
                    failure_criteria={}
                ),
                PlaybookAction(
                    action_id="notify_affected_users",
                    name="Notify Affected Users",
                    description="Notify users who may have been affected",
                    action_type=ActionType.SEMI_AUTOMATED,
                    script_path=None,
                    api_endpoint=None,
                    parameters={},
                    timeout=180,
                    retry_count=1,
                    dependencies=["quarantine_phishing_emails"],
                    approval_required=True,
                    approvers=["communications_manager"],
                    success_criteria={'notified': True},
                    failure_criteria={}
                )
            ],
            variables={},
            conditions={},
            tags=["phishing", "automated", "email"]
        )
        
        # DDoS Response Playbook
        ddos_playbook = Playbook(
            playbook_id="ddos_response",
            name="DDoS Mitigation",
            description="Automated DDoS attack mitigation",
            incident_types=[IncidentType.DDOS],
            severity_levels=[IncidentSeverity.HIGH, IncidentSeverity.CRITICAL],
            status=PlaybookStatus.ACTIVE,
            version="1.0",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by="system",
            actions=[
                PlaybookAction(
                    action_id="activate_ddos_protection",
                    name="Activate DDoS Protection",
                    description="Activate DDoS protection services",
                    action_type=ActionType.AUTOMATED,
                    script_path=None,
                    api_endpoint=None,
                    parameters={},
                    timeout=60,
                    retry_count=3,
                    dependencies=[],
                    approval_required=False,
                    approvers=[],
                    success_criteria={'activated': True},
                    failure_criteria={}
                ),
                PlaybookAction(
                    action_id="block_attack_ips",
                    name="Block Attack IPs",
                    description="Block IP addresses participating in attack",
                    action_type=ActionType.AUTOMATED,
                    script_path=None,
                    api_endpoint=None,
                    parameters={},
                    timeout=120,
                    retry_count=2,
                    dependencies=["activate_ddos_protection"],
                    approval_required=False,
                    approvers=[],
                    success_criteria={'blocked': True},
                    failure_criteria={}
                ),
                PlaybookAction(
                    action_id="scale_infrastructure",
                    name="Scale Infrastructure",
                    description="Scale infrastructure to handle increased load",
                    action_type=ActionType.AUTOMATED,
                    script_path=None,
                    api_endpoint=None,
                    parameters={},
                    timeout=300,
                    retry_count=1,
                    dependencies=["activate_ddos_protection"],
                    approval_required=True,
                    approvers=["infrastructure_manager"],
                    success_criteria={'scaled': True},
                    failure_criteria={}
                )
            ],
            variables={},
            conditions={},
            tags=["ddos", "automated", "network"]
        )
        
        # Add playbooks to registry
        self.playbooks[malware_playbook.playbook_id] = malware_playbook
        self.playbooks[phishing_playbook.playbook_id] = phishing_playbook
        self.playbooks[ddos_playbook.playbook_id] = ddos_playbook
        
        logger.info(f"Loaded {len(self.playbooks)} default playbooks")
    
    def register_playbook(self, playbook: Playbook) -> None:
        """Register a new playbook"""
        with self.lock:
            self.playbooks[playbook.playbook_id] = playbook
            logger.info(f"Registered playbook: {playbook.playbook_id}")
    
    def find_playbook(self, incident_type: IncidentType, severity: IncidentSeverity) -> Optional[Playbook]:
        """Find matching playbook for incident"""
        matching_playbooks = []
        
        for playbook in self.playbooks.values():
            if (playbook.status == PlaybookStatus.ACTIVE and
                incident_type in playbook.incident_types and
                severity in playbook.severity_levels):
                matching_playbooks.append(playbook)
        
        # Return the most recently updated playbook
        if matching_playbooks:
            return max(matching_playbooks, key=lambda p: p.updated_at)
        
        return None
    
    def execute_playbook(self, playbook: Playbook, incident: SecurityIncident, context: Dict[str, Any]) -> PlaybookExecution:
        """Execute a playbook"""
        execution_id = str(uuid.uuid4())
        
        execution = PlaybookExecution(
            execution_id=execution_id,
            playbook_id=playbook.playbook_id,
            incident_id=incident.incident_id,
            started_at=datetime.utcnow(),
            completed_at=None,
            status="running",
            executed_by="system",
            actions_executed=[],
            results={},
            errors=[],
            duration=None
        )
        
        with self.lock:
            self.executions[execution_id] = execution
        
        # Start execution in background thread
        execution_thread = threading.Thread(
            target=self._execute_playbook_async,
            args=(playbook, incident, execution, context),
            daemon=True
        )
        
        with self.lock:
            self.active_executions[execution_id] = execution_thread
        
        execution_thread.start()
        
        return execution
    
    def _execute_playbook_async(self, playbook: Playbook, incident: SecurityIncident, execution: PlaybookExecution, context: Dict[str, Any]) -> None:
        """Execute playbook asynchronously"""
        try:
            # Prepare execution context
            execution_context = context.copy()
            execution_context.update({
                'incident_id': incident.incident_id,
                'incident_type': incident.incident_type.value,
                'severity': incident.severity.value,
                'affected_assets': incident.affected_assets,
                'indicators': incident.indicators
            })
            
            # Execute actions in dependency order
            executed_actions = set()
            action_results = {}
            
            for action in playbook.actions:
                # Check dependencies
                if action.dependencies:
                    dependencies_met = all(dep in executed_actions for dep in action.dependencies)
                    if not dependencies_met:
                        continue
                
                # Check approval requirements
                if action.approval_required:
                    # In production, this would wait for approval
                    logger.info(f"Action {action.action_id} requires approval - auto-approving for demo")
                
                # Execute action
                action_result = self.action_executor.execute_action(action, execution_context)
                action_results[action.action_id] = action_result
                executed_actions.add(action.action_id)
                
                # Update execution
                execution.actions_executed.append(action_result)
                
                # Check if action failed
                if action_result['status'] != 'success':
                    execution.errors.append(f"Action {action.action_id} failed: {action_result.get('error', 'Unknown error')}")
                    
                    # Stop execution on critical action failure
                    if action.action_id in ['isolate_affected_systems', 'activate_ddos_protection']:
                        break
            
            # Complete execution
            execution.completed_at = datetime.utcnow()
            execution.duration = (execution.completed_at - execution.started_at).total_seconds()
            execution.results = action_results
            execution.status = "completed" if not execution.errors else "completed_with_errors"
            
            # Update incident status
            if execution.status == "completed":
                incident.status = IncidentStatus.CONTAINED
            
            # Log execution completion
            logger.info(f"Playbook execution {execution.execution_id} completed with status {execution.status}")
            
        except Exception as e:
            logger.error(f"Playbook execution failed: {e}")
            execution.completed_at = datetime.utcnow()
            execution.duration = (execution.completed_at - execution.started_at).total_seconds()
            execution.status = "failed"
            execution.errors.append(str(e))
        
        finally:
            # Clean up active execution
            with self.lock:
                if execution.execution_id in self.active_executions:
                    del self.active_executions[execution.execution_id]
    
    def get_execution_status(self, execution_id: str) -> Optional[PlaybookExecution]:
        """Get execution status"""
        with self.lock:
            return self.executions.get(execution_id)
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel playbook execution"""
        with self.lock:
            if execution_id in self.active_executions:
                # In production, this would properly cancel the execution
                execution = self.executions[execution_id]
                execution.status = "cancelled"
                execution.completed_at = datetime.utcnow()
                execution.duration = (execution.completed_at - execution.started_at).total_seconds()
                
                del self.active_executions[execution_id]
                return True
        
        return False

class SOARPlatform:
    """Security Orchestration, Automation, and Response Platform"""
    
    def __init__(self, encryption_manager: Optional[EncryptionManager] = None):
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.action_executor = ActionExecutor(encryption_manager)
        self.playbook_engine = PlaybookEngine(self.action_executor)
        self.incidents: Dict[str, SecurityIncident] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.metrics: Dict[str, Any] = defaultdict(int)
        self.lock = threading.Lock()
        
        # Configuration
        self.auto_triage_enabled = os.getenv('SOAR_AUTO_TRIAGE', 'true').lower() == 'true'
        self.auto_response_enabled = os.getenv('SOAR_AUTO_RESPONSE', 'true').lower() == 'true'
        self.alert_retention_days = int(os.getenv('SOAR_ALERT_RETENTION', '30'))
        
        # Start background tasks
        self._start_background_tasks()
    
    def create_incident(self, incident_data: Dict[str, Any]) -> SecurityIncident:
        """Create a new security incident"""
        incident_id = str(uuid.uuid4())
        
        incident = SecurityIncident(
            incident_id=incident_id,
            title=incident_data.get('title', 'Security Incident'),
            description=incident_data.get('description', ''),
            incident_type=IncidentType(incident_data.get('incident_type', 'other')),
            severity=IncidentSeverity(incident_data.get('severity', 'medium')),
            status=IncidentStatus.NEW,
            source=incident_data.get('source', 'manual'),
            detected_at=datetime.utcnow(),
            assigned_to=incident_data.get('assigned_to'),
            created_by=incident_data.get('created_by', 'system'),
            affected_assets=incident_data.get('affected_assets', []),
            indicators=incident_data.get('indicators', []),
            timeline=[],
            evidence=incident_data.get('evidence', []),
            tags=incident_data.get('tags', []),
            metadata=incident_data.get('metadata', {})
        )
        
        with self.lock:
            self.incidents[incident_id] = incident
            self.metrics['incidents_created'] += 1
            self.metrics[f'incidents_{incident.severity.value}'] += 1
        
        # Auto-triage and auto-response if enabled
        if self.auto_triage_enabled:
            self._auto_triage_incident(incident)
        
        if self.auto_response_enabled:
            self._auto_respond_incident(incident)
        
        logger.info(f"Created incident {incident_id}: {incident.title}")
        
        return incident
    
    def _auto_triage_incident(self, incident: SecurityIncident) -> None:
        """Automatically triage incident"""
        # Update incident status based on severity and type
        if incident.severity == IncidentSeverity.CRITICAL:
            incident.status = IncidentStatus.IN_PROGRESS
            incident.assigned_to = "security_team_lead"
        elif incident.severity == IncidentSeverity.HIGH:
            incident.status = IncidentStatus.INVESTIGATING
            incident.assigned_to = "security_analyst"
        elif incident.severity == IncidentSeverity.MEDIUM:
            incident.status = IncidentStatus.IN_PROGRESS
        else:
            incident.status = IncidentStatus.NEW
        
        # Add timeline entry
        incident.timeline.append({
            'timestamp': datetime.utcnow().isoformat(),
            'action': 'auto_triage',
            'description': f'Incident auto-triaged with status {incident.status.value}',
            'automated': True
        })
        
        self.metrics['incidents_auto_triaged'] += 1
    
    def _auto_respond_incident(self, incident: SecurityIncident) -> None:
        """Automatically respond to incident"""
        # Find matching playbook
        playbook = self.playbook_engine.find_playbook(incident.incident_type, incident.severity)
        
        if playbook:
            # Execute playbook
            execution = self.playbook_engine.execute_playbook(
                playbook, 
                incident, 
                {'auto_response': True}
            )
            
            # Update incident
            incident.status = IncidentStatus.IN_PROGRESS
            
            # Add timeline entry
            incident.timeline.append({
                'timestamp': datetime.utcnow().isoformat(),
                'action': 'auto_response',
                'description': f'Auto-response initiated with playbook {playbook.playbook_id}',
                'playbook_id': playbook.playbook_id,
                'execution_id': execution.execution_id,
                'automated': True
            })
            
            self.metrics['incidents_auto_responded'] += 1
            logger.info(f"Auto-response initiated for incident {incident.incident_id}")
        else:
            logger.warning(f"No playbook found for incident {incident.incident_id}")
    
    def update_incident(self, incident_id: str, updates: Dict[str, Any]) -> bool:
        """Update incident details"""
        with self.lock:
            if incident_id not in self.incidents:
                return False
            
            incident = self.incidents[incident_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(incident, key):
                    setattr(incident, key, value)
            
            # Add timeline entry
            incident.timeline.append({
                'timestamp': datetime.utcnow().isoformat(),
                'action': 'update',
                'description': 'Incident updated',
                'updates': updates
            })
            
            self.metrics['incidents_updated'] += 1
            return True
    
    def get_incident(self, incident_id: str) -> Optional[SecurityIncident]:
        """Get incident by ID"""
        with self.lock:
            return self.incidents.get(incident_id)
    
    def list_incidents(self, filters: Optional[Dict[str, Any]] = None) -> List[SecurityIncident]:
        """List incidents with optional filters"""
        incidents = list(self.incidents.values())
        
        if filters:
            filtered_incidents = []
            
            for incident in incidents:
                match = True
                
                for key, value in filters.items():
                    if hasattr(incident, key):
                        incident_value = getattr(incident, key)
                        if hasattr(incident_value, 'value'):
                            incident_value = incident_value.value
                        
                        if incident_value != value:
                            match = False
                            break
                
                if match:
                    filtered_incidents.append(incident)
            
            return filtered_incidents
        
        return incidents
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get SOAR platform metrics"""
        with self.lock:
            metrics = dict(self.metrics)
            
            # Add additional metrics
            metrics['total_incidents'] = len(self.incidents)
            metrics['active_incidents'] = len([i for i in self.incidents.values() if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]])
            metrics['total_playbooks'] = len(self.playbook_engine.playbooks)
            metrics['active_executions'] = len(self.playbook_engine.active_executions)
            
            # Incident status breakdown
            status_counts = defaultdict(int)
            for incident in self.incidents.values():
                status_counts[incident.status.value] += 1
            metrics['incident_status_breakdown'] = dict(status_counts)
            
            return metrics
    
    def _start_background_tasks(self) -> None:
        """Start background SOAR tasks"""
        # Start metrics collection thread
        metrics_thread = threading.Thread(target=self._collect_metrics, daemon=True)
        metrics_thread.start()
        
        # Start alert cleanup thread
        cleanup_thread = threading.Thread(target=self._cleanup_alerts, daemon=True)
        cleanup_thread.start()
    
    def _collect_metrics(self) -> None:
        """Collect and update metrics periodically"""
        while True:
            try:
                # Collect metrics every 5 minutes
                time.sleep(300)
                
                # Update metrics
                current_metrics = self.get_metrics()
                
                # Log key metrics
                logger.info(f"SOAR Metrics: {current_metrics}")
                
            except Exception as e:
                logger.error(f"Metrics collection failed: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _cleanup_alerts(self) -> None:
        """Clean up old alerts"""
        while True:
            try:
                # Run cleanup daily
                time.sleep(86400)  # 24 hours
                
                cutoff_date = datetime.utcnow() - timedelta(days=self.alert_retention_days)
                
                with self.lock:
                    # Remove old alerts
                    self.alerts = [
                        alert for alert in self.alerts 
                        if datetime.fromisoformat(alert['timestamp']) > cutoff_date
                    ]
                
                logger.info(f"Alert cleanup completed")
                
            except Exception as e:
                logger.error(f"Alert cleanup failed: {e}")
                time.sleep(3600)  # Wait 1 hour before retrying

# Global SOAR platform instance
soar_platform = SOARPlatform()

# Export main components
__all__ = [
    'SOARPlatform',
    'SecurityIncident',
    'Playbook',
    'PlaybookAction',
    'PlaybookExecution',
    'ActionExecutor',
    'PlaybookEngine',
    'IncidentSeverity',
    'IncidentStatus',
    'IncidentType',
    'PlaybookStatus',
    'ActionType',
    'soar_platform'
]
