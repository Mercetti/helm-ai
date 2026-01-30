"""
Helm AI Automated Compliance Checking System
Provides automated compliance monitoring and checking for multiple regulatory frameworks
"""

import os
import sys
import json
import time
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum
import logging

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from security.encryption import EncryptionManager

class ComplianceFramework(Enum):
    """Compliance framework enumeration"""
    GDPR = "gdpr"
    SOC2 = "soc2"
    HIPAA = "hipaa"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    CCPA = "ccpa"
    NIST_CSF = "nist_csf"
    CIS_CONTROLS = "cis_controls"

class ComplianceStatus(Enum):
    """Compliance status enumeration"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"

class ControlType(Enum):
    """Control type enumeration"""
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"
    COMPENSATORY = "compensatory"

class ControlCategory(Enum):
    """Control category enumeration"""
    ACCESS_CONTROL = "access_control"
    DATA_PROTECTION = "data_protection"
    INCIDENT_RESPONSE = "incident_response"
    RISK_MANAGEMENT = "risk_management"
    SECURITY_AWARENESS = "security_awareness"
    PHYSICAL_SECURITY = "physical_security"
    NETWORK_SECURITY = "network_security"
    APPLICATION_SECURITY = "application_security"
    BUSINESS_CONTINUITY = "business_continuity"
    COMPLIANCE_MANAGEMENT = "compliance_management"

@dataclass
class ComplianceControl:
    """Compliance control definition"""
    control_id: str
    framework: ComplianceFramework
    title: str
    description: str
    category: ControlCategory
    type: ControlType
    requirements: List[str]
    testing_procedures: List[str]
    evidence_requirements: List[str]
    frequency: str
    owner: str
    status: ComplianceStatus = ComplianceStatus.UNKNOWN
    last_assessed: Optional[datetime] = None
    next_assessment: Optional[datetime] = None
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    violations: List[Dict[str, Any]] = field(default_factory=list)
    score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert control to dictionary"""
        return {
            'control_id': self.control_id,
            'framework': self.framework.value,
            'title': self.title,
            'description': self.description,
            'category': self.category.value,
            'type': self.type.value,
            'requirements': self.requirements,
            'testing_procedures': self.testing_procedures,
            'evidence_requirements': self.evidence_requirements,
            'frequency': self.frequency,
            'owner': self.owner,
            'status': self.status.value,
            'last_assessed': self.last_assessed.isoformat() if self.last_assessed else None,
            'next_assessment': self.next_assessment.isoformat() if self.next_assessment else None,
            'evidence': self.evidence,
            'violations': self.violations,
            'score': self.score
        }

@dataclass
class ComplianceEvidence:
    """Compliance evidence item"""
    evidence_id: str
    control_id: str
    framework: ComplianceFramework
    evidence_type: str
    description: str
    file_path: Optional[str]
    content: Optional[str]
    metadata: Dict[str, Any]
    collected_at: datetime
    expires_at: Optional[datetime]
    verified: bool = False
    hash_value: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert evidence to dictionary"""
        return {
            'evidence_id': self.evidence_id,
            'control_id': self.control_id,
            'framework': self.framework.value,
            'evidence_type': self.evidence_type,
            'description': self.description,
            'file_path': self.file_path,
            'content': self.content,
            'metadata': self.metadata,
            'collected_at': self.collected_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'verified': self.verified,
            'hash_value': self.hash_value
        }

@dataclass
class ComplianceViolation:
    """Compliance violation record"""
    violation_id: str
    control_id: str
    framework: ComplianceFramework
    severity: str
    description: str
    discovered_at: datetime
    discovered_by: str
    remediation_plan: str
    due_date: datetime
    status: str
    assigned_to: str
    impact_assessment: str
    root_cause: str
    evidence: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary"""
        return {
            'violation_id': self.violation_id,
            'control_id': self.control_id,
            'framework': self.framework.value,
            'severity': self.severity,
            'description': self.description,
            'discovered_at': self.discovered_at.isoformat(),
            'discovered_by': self.discovered_by,
            'remediation_plan': self.remediation_plan,
            'due_date': self.due_date.isoformat(),
            'status': self.status,
            'assigned_to': self.assigned_to,
            'impact_assessment': self.impact_assessment,
            'root_cause': self.root_cause,
            'evidence': self.evidence
        }

class ComplianceRule:
    """Compliance rule definition"""
    
    def __init__(self, rule_id: str, framework: ComplianceFramework, name: str, description: str):
        self.rule_id = rule_id
        self.framework = framework
        self.name = name
        self.description = description
        self.conditions = []
        self.actions = []
        self.severity = "medium"
        self.enabled = True
    
    def add_condition(self, condition: str, description: str) -> None:
        """Add condition to rule"""
        self.conditions.append({
            'condition': condition,
            'description': description
        })
    
    def add_action(self, action: str, description: str) -> None:
        """Add action to rule"""
        self.actions.append({
            'action': action,
            'description': description
        })
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate rule against context"""
        if not self.enabled:
            return True
        
        # Simple rule evaluation - can be enhanced with more complex logic
        for condition in self.conditions:
            if not self._evaluate_condition(condition['condition'], context):
                return False
        
        return True
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate individual condition"""
        # Simple evaluation - in production, use proper expression parser
        try:
            # Replace placeholders with actual values
            for key, value in context.items():
                condition = condition.replace(f"${key}", str(value))
            
            # Safe evaluation
            return eval(condition)
        except:
            return False

class ComplianceChecker:
    """Automated compliance checking engine"""
    
    def __init__(self, encryption_manager: Optional[EncryptionManager] = None):
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.controls: Dict[str, ComplianceControl] = {}
        self.rules: Dict[str, ComplianceRule] = {}
        self.evidence: Dict[str, ComplianceEvidence] = {}
        self.violations: Dict[str, ComplianceViolation] = {}
        self.assessment_history: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        
        # Configuration
        self.evidence_retention_days = int(os.getenv('COMPLIANCE_EVIDENCE_RETENTION', '2555'))
        self.violation_retention_days = int(os.getenv('COMPLIANCE_VIOLATION_RETENTION', '1825'))
        self.assessment_frequency = os.getenv('COMPLIANCE_ASSESSMENT_FREQUENCY', 'weekly')
        self.alert_threshold = float(os.getenv('COMPLIANCE_ALERT_THRESHOLD', '0.8'))
        
        # Initialize compliance frameworks
        self._initialize_frameworks()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _initialize_frameworks(self) -> None:
        """Initialize compliance frameworks and controls"""
        # GDPR Controls
        self._initialize_gdpr_controls()
        
        # SOC2 Controls
        self._initialize_soc2_controls()
        
        # HIPAA Controls
        self._initialize_hipaa_controls()
        
        # ISO27001 Controls
        self._initialize_iso27001_controls()
        
        # PCI DSS Controls
        self._initialize_pci_dss_controls()
        
        logger.info(f"Initialized {len(self.controls)} compliance controls")
    
    def _initialize_gdpr_controls(self) -> None:
        """Initialize GDPR compliance controls"""
        gdpr_controls = [
            ComplianceControl(
                control_id="GDPR-001",
                framework=ComplianceFramework.GDPR,
                title="Lawful Basis for Processing",
                description="Ensure personal data is processed only with valid lawful basis",
                category=ControlCategory.DATA_PROTECTION,
                type=ControlType.PREVENTIVE,
                requirements=[
                    "Identify lawful basis for all data processing",
                    "Document lawful basis in privacy policy",
                    "Obtain consent where required",
                    "Maintain records of processing activities"
                ],
                testing_procedures=[
                    "Review privacy policy for lawful basis documentation",
                    "Audit consent management system",
                    "Verify processing records are maintained"
                ],
                evidence_requirements=[
                    "Privacy policy",
                    "Consent records",
                    "Processing register",
                    "Lawful basis documentation"
                ],
                frequency="quarterly",
                owner="Data Protection Officer"
            ),
            ComplianceControl(
                control_id="GDPR-002",
                framework=ComplianceFramework.GDPR,
                title="Data Subject Rights",
                description="Implement procedures to handle data subject rights requests",
                category=ControlCategory.DATA_PROTECTION,
                type=ControlType.DETECTIVE,
                requirements=[
                    "Provide information on data processing",
                    "Allow data access requests",
                    "Enable data rectification",
                    "Support data erasure requests",
                    "Process data portability requests",
                    "Handle objection requests"
                ],
                testing_procedures=[
                    "Test data subject request process",
                    "Verify response time compliance",
                    "Validate data access procedures"
                ],
                evidence_requirements=[
                    "Data subject request procedures",
                    "Request logs",
                    "Response records",
                    "Process documentation"
                ],
                frequency="monthly",
                owner="Data Protection Officer"
            ),
            ComplianceControl(
                control_id="GDPR-003",
                framework=ComplianceFramework.GDPR,
                title="Data Breach Notification",
                description="Implement procedures for data breach notification",
                category=ControlCategory.INCIDENT_RESPONSE,
                type=ControlType.DETECTIVE,
                requirements=[
                    "Detect data breaches within 72 hours",
                    "Notify supervisory authority when required",
                    "Notify affected individuals when required",
                    "Maintain breach register",
                    "Document breach response procedures"
                ],
                testing_procedures=[
                    "Test breach detection systems",
                    "Verify notification procedures",
                    "Conduct breach response drills"
                ],
                evidence_requirements=[
                    "Breach detection logs",
                    "Notification records",
                    "Breach register",
                    "Response procedures"
                ],
                frequency="quarterly",
                owner="Security Team"
            ),
            ComplianceControl(
                control_id="GDPR-004",
                framework=ComplianceFramework.GDPR,
                title="Data Protection by Design",
                description="Implement data protection by design and by default",
                category=ControlCategory.APPLICATION_SECURITY,
                type=ControlType.PREVENTIVE,
                requirements=[
                    "Conduct DPIAs for new systems",
                    "Implement privacy by design principles",
                    "Use privacy-enhancing technologies",
                    "Minimize data collection",
                    "Implement data retention policies"
                ],
                testing_procedures=[
                    "Review DPIA documentation",
                    "Verify privacy controls implementation",
                    "Audit data minimization practices"
                ],
                evidence_requirements=[
                    "DPIA reports",
                    "Privacy impact assessments",
                    "Design documentation",
                    "Retention policies"
                ],
                frequency="annually",
                owner="Development Team"
            )
        ]
        
        for control in gdpr_controls:
            self.controls[control.control_id] = control
    
    def _initialize_soc2_controls(self) -> None:
        """Initialize SOC2 compliance controls"""
        soc2_controls = [
            ComplianceControl(
                control_id="SOC2-001",
                framework=ComplianceFramework.SOC2,
                title="Security",
                description="Implement security controls to protect systems and data",
                category=ControlCategory.NETWORK_SECURITY,
                type=ControlType.PREVENTIVE,
                requirements=[
                    "Implement access controls",
                    "Use multi-factor authentication",
                    "Encrypt data in transit",
                    "Monitor system access",
                    "Conduct security testing"
                ],
                testing_procedures=[
                    "Test access control systems",
                    "Verify MFA implementation",
                    "Audit encryption configurations",
                    "Review access logs"
                ],
                evidence_requirements=[
                    "Access control policies",
                    "MFA configuration",
                    "Encryption certificates",
                    "Access logs"
                ],
                frequency="quarterly",
                owner="Security Team"
            ),
            ComplianceControl(
                control_id="SOC2-002",
                framework=ComplianceFramework.SOC2,
                title="Availability",
                description="Ensure systems are available and reliable",
                category=ControlCategory.BUSINESS_CONTINUITY,
                type=ControlType.DETECTIVE,
                requirements=[
                    "Implement redundancy",
                    "Monitor system performance",
                    "Conduct disaster recovery testing",
                    "Maintain backup systems",
                    "Document availability procedures"
                ],
                testing_procedures=[
                    "Test redundancy systems",
                    "Verify backup procedures",
                    "Conduct disaster recovery drills"
                ],
                evidence_requirements=[
                    "Redundancy documentation",
                    "Backup logs",
                    "DR test reports",
                    "Availability metrics"
                ],
                frequency="monthly",
                owner="Infrastructure Team"
            ),
            ComplianceControl(
                control_id="SOC2-003",
                framework=ComplianceFramework.SOC2,
                title="Processing Integrity",
                description="Ensure data processing is complete, accurate, timely, and authorized",
                category=ControlCategory.APPLICATION_SECURITY,
                type=ControlType.PREVENTIVE,
                requirements=[
                    "Implement input validation",
                    "Use error detection",
                    "Maintain processing logs",
                    "Conduct data reconciliation",
                    "Implement change management"
                ],
                testing_procedures=[
                    "Test input validation",
                    "Verify error handling",
                    "Review processing logs"
                ],
                evidence_requirements=[
                    "Validation rules",
                    "Error logs",
                    "Processing records",
                    "Change logs"
                ],
                frequency="monthly",
                owner="Application Team"
            )
        ]
        
        for control in soc2_controls:
            self.controls[control.control_id] = control
    
    def _initialize_hipaa_controls(self) -> None:
        """Initialize HIPAA compliance controls"""
        hipaa_controls = [
            ComplianceControl(
                control_id="HIPAA-001",
                framework=ComplianceFramework.HIPAA,
                title="Administrative Safeguards",
                description="Implement administrative safeguards for PHI protection",
                category=ControlCategory.COMPLIANCE_MANAGEMENT,
                type=ControlType.PREVENTIVE,
                requirements=[
                    "Security officer designation",
                    "Workforce security training",
                    "Information access management",
                    "Security management process",
                    "Contingency planning"
                ],
                testing_procedures=[
                    "Review security policies",
                    "Verify training records",
                    "Audit access controls"
                ],
                evidence_requirements=[
                    "Security policies",
                    "Training records",
                    "Access logs",
                    "Contingency plans"
                ],
                frequency="quarterly",
                owner="Compliance Officer"
            ),
            ComplianceControl(
                control_id="HIPAA-002",
                framework=ComplianceFramework.HIPAA,
                title="Physical Safeguards",
                description="Implement physical safeguards for PHI protection",
                category=ControlCategory.PHYSICAL_SECURITY,
                type=ControlType.PREVENTIVE,
                requirements=[
                    "Facility access controls",
                    "Workstation security",
                    "Device and media controls",
                    "Workforce security"
                ],
                testing_procedures=[
                    "Test physical access controls",
                    "Verify workstation security",
                    "Audit device management"
                ],
                evidence_requirements=[
                    "Access logs",
                    "Security policies",
                    "Device inventories"
                ],
                frequency="monthly",
                owner="Facilities Manager"
            ),
            ComplianceControl(
                control_id="HIPAA-003",
                framework=ComplianceFramework.HIPAA,
                title="Technical Safeguards",
                description="Implement technical safeguards for PHI protection",
                category=ControlCategory.NETWORK_SECURITY,
                type=ControlType.PREVENTIVE,
                requirements=[
                    "Access control",
                    "Audit controls",
                    "Integrity controls",
                    "Transmission security"
                ],
                testing_procedures=[
                    "Test access controls",
                    "Verify audit logging",
                    "Test encryption"
                ],
                evidence_requirements=[
                    "Access policies",
                    "Audit logs",
                    "Encryption certificates"
                ],
                frequency="monthly",
                owner="IT Security Team"
            )
        ]
        
        for control in hipaa_controls:
            self.controls[control.control_id] = control
    
    def _initialize_iso27001_controls(self) -> None:
        """Initialize ISO27001 compliance controls"""
        iso_controls = [
            ComplianceControl(
                control_id="ISO27001-001",
                framework=ComplianceFramework.ISO27001,
                title="Information Security Policies",
                description="Implement comprehensive information security policies",
                category=ControlCategory.COMPLIANCE_MANAGEMENT,
                type=ControlType.PREVENTIVE,
                requirements=[
                    "Information security policy",
                    "Risk assessment policy",
                    "Security incident management",
                    "Business continuity planning"
                ],
                testing_procedures=[
                    "Review policy documentation",
                    "Verify policy implementation"
                ],
                evidence_requirements=[
                    "Policy documents",
                    "Implementation records"
                ],
                frequency="annually",
                owner="Information Security Manager"
            ),
            ComplianceControl(
                control_id="ISO27001-002",
                framework=ComplianceFramework.ISO27001,
                title="Organization of Information Security",
                description="Establish information security management structure",
                category=ControlCategory.RISK_MANAGEMENT,
                type=ControlType.PREVENTIVE,
                requirements=[
                    "Security roles and responsibilities",
                    "Information security coordination",
                    "Contact with authorities",
                    "Project management"
                ],
                testing_procedures=[
                    "Review organizational structure",
                    "Verify role definitions"
                ],
                evidence_requirements=[
                    "Organizational charts",
                    "Role definitions"
                ],
                frequency="quarterly",
                owner="Management"
            )
        ]
        
        for control in iso_controls:
            self.controls[control.control_id] = control
    
    def _initialize_pci_dss_controls(self) -> None:
        """Initialize PCI DSS compliance controls"""
        pci_controls = [
            ComplianceControl(
                control_id="PCI-001",
                framework=ComplianceFramework.PCI_DSS,
                title="Build and Maintain Secure Networks",
                description="Implement secure network architecture and systems",
                category=ControlCategory.NETWORK_SECURITY,
                type=ControlType.PREVENTIVE,
                requirements=[
                    "Firewall configuration",
                    "Secure network architecture",
                    "Secure wireless networks",
                    "Network segmentation"
                ],
                testing_procedures=[
                    "Test firewall rules",
                    "Verify network segmentation"
                ],
                evidence_requirements=[
                    "Firewall configurations",
                    "Network diagrams"
                ],
                frequency="quarterly",
                owner="Network Security Team"
            ),
            ComplianceControl(
                control_id="PCI-002",
                framework=ComplianceFramework.PCI_DSS,
                title="Protect Cardholder Data",
                description="Implement strong cryptography and access controls",
                category=ControlCategory.DATA_PROTECTION,
                type=ControlType.PREVENTIVE,
                requirements=[
                    "Data encryption at rest",
                    "Data encryption in transit",
                    "Access control mechanisms",
                    "Key management"
                ],
                testing_procedures=[
                    "Verify encryption implementation",
                    "Test access controls"
                ],
                evidence_requirements=[
                    "Encryption certificates",
                    "Access control policies"
                ],
                frequency="monthly",
                owner="Security Team"
            )
        ]
        
        for control in pci_controls:
            self.controls[control.control_id] = control
    
    def assess_compliance(self, framework: Optional[ComplianceFramework] = None) -> Dict[str, Any]:
        """Assess compliance status"""
        try:
            assessment_id = self._generate_assessment_id()
            assessment_date = datetime.utcnow()
            
            # Filter controls by framework if specified
            controls_to_assess = self.controls.values()
            if framework:
                controls_to_assess = [c for c in controls_to_assess if c.framework == framework]
            
            results = {
                'assessment_id': assessment_id,
                'date': assessment_date.isoformat(),
                'framework': framework.value if framework else 'all',
                'controls': {},
                'overall_score': 0.0,
                'compliance_status': ComplianceStatus.UNKNOWN.value,
                'violations': [],
                'recommendations': []
            }
            
            total_score = 0.0
            control_count = 0
            
            # Assess each control
            for control in controls_to_assess:
                control_result = self._assess_control(control)
                results['controls'][control.control_id] = control_result
                
                total_score += control_result['score']
                control_count += 1
                
                # Collect violations
                if control_result['status'] == ComplianceStatus.NON_COMPLIANT.value:
                    results['violations'].extend(control_result['violations'])
            
            # Calculate overall score
            if control_count > 0:
                results['overall_score'] = total_score / control_count
            
            # Determine overall status
            if results['overall_score'] >= 0.9:
                results['compliance_status'] = ComplianceStatus.COMPLIANT.value
            elif results['overall_score'] >= 0.7:
                results['compliance_status'] = ComplianceStatus.PARTIALLY_COMPLIANT.value
            elif results['overall_score'] >= 0.5:
                results['compliance_status'] = ComplianceStatus.NON_COMPLIANT.value
            else:
                results['compliance_status'] = ComplianceStatus.CRITICAL.value
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results['controls'])
            
            # Store assessment history
            with self.lock:
                self.assessment_history.append(results)
            
            # Log assessment
            self._log_assessment(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Compliance assessment failed: {e}")
            return {
                'assessment_id': self._generate_assessment_id(),
                'date': datetime.utcnow().isoformat(),
                'framework': framework.value if framework else 'all',
                'error': str(e)
            }
    
    def _assess_control(self, control: ComplianceControl) -> Dict[str, Any]:
        """Assess individual control compliance"""
        try:
            # Check if assessment is due
            if control.next_assessment and datetime.utcnow() < control.next_assessment:
                return {
                    'control_id': control.control_id,
                    'status': control.status.value,
                    'score': control.score,
                    'last_assessed': control.last_assessed.isoformat() if control.last_assessed else None,
                    'next_assessment': control.next_assessment.isoformat() if control.next_assessment else None,
                    'violations': control.violations,
                    'evidence_count': len(control.evidence),
                    'message': 'Assessment not due'
                }
            
            # Check evidence requirements
            evidence_compliance = self._check_evidence_compliance(control)
            
            # Check for violations
            active_violations = [v for v in control.violations if v['status'] == 'open']
            
            # Calculate score
            score = self._calculate_control_score(evidence_compliance, active_violations)
            
            # Determine status
            if score >= 0.9 and len(active_violations) == 0:
                status = ComplianceStatus.COMPLIANT
            elif score >= 0.7 and len(active_violations) == 0:
                status = ComplianceStatus.PARTIALLY_COMPLIANT
            elif score >= 0.5:
                status = ComplianceStatus.NON_COMPLIANT
            else:
                status = ComplianceStatus.CRITICAL
            
            # Update control
            control.status = status
            control.score = score
            control.last_assessed = datetime.utcnow()
            control.next_assessment = self._calculate_next_assessment(control.frequency)
            
            return {
                'control_id': control.control_id,
                'status': status.value,
                'score': score,
                'last_assessed': control.last_assessed.isoformat(),
                'next_assessment': control.next_assessment.isoformat(),
                'violations': active_violations,
                'evidence_count': len(control.evidence),
                'evidence_compliance': evidence_compliance,
                'message': f"Control assessed with score {score:.2f}"
            }
            
        except Exception as e:
            logger.error(f"Control assessment failed for {control.control_id}: {e}")
            return {
                'control_id': control.control_id,
                'status': ComplianceStatus.UNKNOWN.value,
                'score': 0.0,
                'error': str(e)
            }
    
    def _check_evidence_compliance(self, control: ComplianceControl) -> Dict[str, Any]:
        """Check evidence compliance for control"""
        required_evidence = control.evidence_requirements
        available_evidence = [e.evidence_type for e in control.evidence]
        
        compliance = {
            'required_count': len(required_evidence),
            'available_count': len(available_evidence),
            'compliant': True,
            'missing_evidence': []
        }
        
        for evidence_type in required_evidence:
            if evidence_type not in available_evidence:
                compliance['missing_evidence'].append(evidence_type)
                compliance['compliant'] = False
        
        return compliance
    
    def _calculate_control_score(self, evidence_compliance: Dict[str, Any], violations: List[Dict[str, Any]]) -> float:
        """Calculate compliance score for control"""
        # Base score from evidence compliance
        if evidence_compliance['required_count'] > 0:
            evidence_score = evidence_compliance['available_count'] / evidence_compliance['required_count']
        else:
            evidence_score = 1.0
        
        # Penalty for violations
        violation_penalty = len(violations) * 0.2
        
        # Calculate final score
        score = max(0.0, evidence_score - violation_penalty)
        
        return score
    
    def _calculate_next_assessment(self, frequency: str) -> datetime:
        """Calculate next assessment date"""
        now = datetime.utcnow()
        
        if frequency == "daily":
            return now + timedelta(days=1)
        elif frequency == "weekly":
            return now + timedelta(weeks=1)
        elif frequency == "monthly":
            return now + timedelta(days=30)
        elif frequency == "quarterly":
            return now + timedelta(days=90)
        elif frequency == "semi_annually":
            return now + timedelta(days=180)
        elif frequency == "annually":
            return now + timedelta(days=365)
        else:
            return now + timedelta(days=30)  # Default to monthly
    
    def _generate_recommendations(self, control_results: Dict[str, Any]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        for control_id, result in control_results.items():
            if result['status'] == ComplianceStatus.NON_COMPLIANT.value:
                recommendations.append(f"Address non-compliance in control {control_id}")
            elif result['status'] == ComplianceStatus.PARTIALLY_COMPLIANT.value:
                recommendations.append(f"Improve compliance for control {control_id}")
            
            # Evidence-based recommendations
            if 'evidence_compliance' in result:
                evidence_compliance = result['evidence_compliance']
                if not evidence_compliance['compliant']:
                    missing = evidence_compliance['missing_evidence']
                    recommendations.append(f"Collect missing evidence for control {control_id}: {', '.join(missing)}")
        
        return recommendations
    
    def add_evidence(self, evidence: ComplianceEvidence) -> None:
        """Add compliance evidence"""
        with self.lock:
            # Calculate hash for integrity
            if evidence.content:
                evidence.hash_value = hashlib.sha256(evidence.content.encode()).hexdigest()
            
            self.evidence[evidence.evidence_id] = evidence
            
            # Update control evidence
            if evidence.control_id in self.controls:
                self.controls[evidence.control_id].evidence.append(evidence)
    
    def add_violation(self, violation: ComplianceViolation) -> None:
        """Add compliance violation"""
        with self.lock:
            self.violations[violation.violation_id] = violation
            
            # Update control violations
            if violation.control_id in self.controls:
                self.controls[violation.control_id].violations.append(violation.to_dict())
    
    def get_compliance_report(self, framework: Optional[ComplianceFramework] = None) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        assessment = self.assess_compliance(framework)
        
        report = {
            'report_id': self._generate_report_id(),
            'generated_at': datetime.utcnow().isoformat(),
            'framework': framework.value if framework else 'all',
            'summary': {
                'total_controls': len(self.controls),
                'compliant_controls': len([c for c in self.controls.values() if c.status == ComplianceStatus.COMPLIANT]),
                'non_compliant_controls': len([c for c in self.controls.values() if c.status == ComplianceStatus.NON_COMPLIANT]),
                'partially_compliant_controls': len([c for c in self.controls.values() if c.status == ComplianceStatus.PARTIALLY_COMPLIANT]),
                'overall_score': assessment['overall_score'],
                'compliance_status': assessment['compliance_status']
            },
            'assessment': assessment,
            'violations': list(self.violations.values()),
            'evidence': list(self.evidence.values()),
            'recommendations': assessment['recommendations']
        }
        
        return report
    
    def _generate_assessment_id(self) -> str:
        """Generate unique assessment ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _start_background_tasks(self) -> None:
        """Start background compliance tasks"""
        # Start periodic assessment thread
        assessment_thread = threading.Thread(target=self._periodic_assessment, daemon=True)
        assessment_thread.start()
        
        # Start evidence cleanup thread
        cleanup_thread = threading.Thread(target=self._evidence_cleanup, daemon=True)
        cleanup_thread.start()
    
    def _periodic_assessment(self) -> None:
        """Run periodic compliance assessments"""
        while True:
            try:
                # Sleep based on assessment frequency
                if self.assessment_frequency == "daily":
                    sleep_time = 86400  # 24 hours
                elif self.assessment_frequency == "weekly":
                    sleep_time = 604800  # 7 days
                elif self.assessment_frequency == "monthly":
                    sleep_time = 2592000  # 30 days
                else:
                    sleep_time = 604800  # Default to weekly
                
                time.sleep(sleep_time)
                
                # Run assessment
                self.assess_compliance()
                
            except Exception as e:
                logger.error(f"Periodic assessment failed: {e}")
                time.sleep(3600)  # Wait 1 hour before retrying
    
    def _evidence_cleanup(self) -> None:
        """Clean up expired evidence"""
        while True:
            try:
                # Run cleanup daily
                time.sleep(86400)  # 24 hours
                
                current_time = datetime.utcnow()
                expired_evidence = []
                
                for evidence_id, evidence in self.evidence.items():
                    if evidence.expires_at and current_time > evidence.expires_at:
                        expired_evidence.append(evidence_id)
                
                # Remove expired evidence
                for evidence_id in expired_evidence:
                    with self.lock:
                        del self.evidence[evidence_id]
                
                if expired_evidence:
                    logger.info(f"Cleaned up {len(expired_evidence)} expired evidence items")
                
            except Exception as e:
                logger.error(f"Evidence cleanup failed: {e}")
                time.sleep(3600)  # Wait 1 hour before retrying
    
    def _log_assessment(self, assessment: Dict[str, Any]) -> None:
        """Log compliance assessment"""
        log_data = {
            'assessment_id': assessment['assessment_id'],
            'date': assessment['date'],
            'framework': assessment['framework'],
            'overall_score': assessment['overall_score'],
            'compliance_status': assessment['compliance_status'],
            'violations_count': len(assessment['violations']),
            'recommendations_count': len(assessment['recommendations'])
        }
        
        logger.info(f"Compliance assessment completed: {json.dumps(log_data)}")

# Global compliance checker instance
compliance_checker = ComplianceChecker()

# Export main components
__all__ = [
    'ComplianceChecker',
    'ComplianceControl',
    'ComplianceEvidence',
    'ComplianceViolation',
    'ComplianceRule',
    'ComplianceFramework',
    'ComplianceStatus',
    'ControlType',
    'ControlCategory',
    'compliance_checker'
]
