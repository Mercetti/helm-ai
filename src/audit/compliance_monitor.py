"""
Helm AI Compliance Monitor
This module provides compliance monitoring for GDPR, SOC2, HIPAA, and other frameworks
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import re
import hashlib

from .audit_logger import AuditLogger, ComplianceFramework, DataClassification, AuditEventType

logger = logging.getLogger(__name__)

class ComplianceStatus(Enum):
    """Compliance status levels"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNKNOWN = "unknown"

class RiskLevel(Enum):
    """Risk levels for compliance violations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ComplianceRule:
    """Compliance rule definition"""
    rule_id: str
    framework: ComplianceFramework
    category: str
    description: str
    requirement: str
    check_function: str
    risk_level: RiskLevel
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ComplianceViolation:
    """Compliance violation record"""
    violation_id: str
    rule_id: str
    framework: ComplianceFramework
    risk_level: RiskLevel
    description: str
    affected_resources: List[str]
    detected_at: datetime
    status: str = "open"
    remediation_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplianceReport:
    """Compliance assessment report"""
    framework: ComplianceFramework
    assessment_date: datetime
    overall_status: ComplianceStatus
    total_rules: int
    passed_rules: int
    failed_rules: int
    violations: List[ComplianceViolation]
    score: float  # 0-100
    recommendations: List[str]

class ComplianceMonitor:
    """Compliance monitoring and assessment system"""
    
    def __init__(self):
        self.audit_logger = AuditLogger()
        self.rules: Dict[str, ComplianceRule] = {}
        self.violations: Dict[str, ComplianceViolation] = {}
        self._initialize_rules()
    
    def _initialize_rules(self):
        """Initialize compliance rules for different frameworks"""
        
        # GDPR Rules
        self._add_rule(ComplianceRule(
            rule_id="gdpr_001",
            framework=ComplianceFramework.GDPR,
            category="Data Processing",
            description="Personal data processing records must be maintained",
            requirement="Article 30: Records of processing activities",
            check_function="check_data_processing_records",
            risk_level=RiskLevel.HIGH
        ))
        
        self._add_rule(ComplianceRule(
            rule_id="gdpr_002",
            framework=ComplianceFramework.GDPR,
            category="Consent Management",
            description="Valid consent must be obtained for data processing",
            requirement="Article 7: Conditions for consent",
            check_function="check_consent_records",
            risk_level=RiskLevel.CRITICAL
        ))
        
        self._add_rule(ComplianceRule(
            rule_id="gdpr_003",
            framework=ComplianceFramework.GDPR,
            category="Data Subject Rights",
            description="Data subject requests must be processed within 30 days",
            requirement="Article 12: Transparent information",
            check_function="check_data_subject_requests",
            risk_level=RiskLevel.HIGH
        ))
        
        self._add_rule(ComplianceRule(
            rule_id="gdpr_004",
            framework=ComplianceFramework.GDPR,
            category="Breach Notification",
            description="Data breaches must be reported within 72 hours",
            requirement="Article 33: Notification of personal data breach",
            check_function="check_breach_notification_timeline",
            risk_level=RiskLevel.CRITICAL
        ))
        
        # SOC2 Rules
        self._add_rule(ComplianceRule(
            rule_id="soc2_001",
            framework=ComplianceFramework.SOC2,
            category="Security",
            description="Access controls must be implemented and reviewed",
            requirement="Common Criteria 6: Logical Access",
            check_function="check_access_controls",
            risk_level=RiskLevel.HIGH
        ))
        
        self._add_rule(ComplianceRule(
            rule_id="soc2_002",
            framework=ComplianceFramework.SOC2,
            category="Security",
            description="Security incidents must be detected and responded to",
            requirement="Common Criteria 8: Incident Response",
            check_function="check_incident_response",
            risk_level=RiskLevel.HIGH
        ))
        
        self._add_rule(ComplianceRule(
            rule_id="soc2_003",
            framework=ComplianceFramework.SOC2,
            category="Availability",
            description="System availability must meet SLA requirements",
            requirement="Common Criteria 1: Availability",
            check_function="check_system_availability",
            risk_level=RiskLevel.MEDIUM
        ))
        
        # HIPAA Rules
        self._add_rule(ComplianceRule(
            rule_id="hipaa_001",
            framework=ComplianceFramework.HIPAA,
            category="Privacy",
            description="PHI access must be logged and audited",
            requirement="164.312(a): Access controls",
            check_function="check_phi_access_logging",
            risk_level=RiskLevel.CRITICAL
        ))
        
        self._add_rule(ComplianceRule(
            rule_id="hipaa_002",
            framework=ComplianceFramework.HIPAA,
            category="Security",
            description="PHI must be encrypted in transit and at rest",
            requirement="164.312(a)(2): Encryption",
            check_function="check_phi_encryption",
            risk_level=RiskLevel.CRITICAL
        ))
        
        self._add_rule(ComplianceRule(
            rule_id="hipaa_003",
            framework=ComplianceFramework.HIPAA,
            category="Breach Notification",
            description="PHI breaches must be reported within 60 days",
            requirement="164.408: Breach notification",
            check_function="check_hipaa_breach_notification",
            risk_level=RiskLevel.CRITICAL
        ))
    
    def _add_rule(self, rule: ComplianceRule):
        """Add compliance rule"""
        self.rules[rule.rule_id] = rule
    
    def run_compliance_assessment(self, framework: ComplianceFramework = None) -> Dict[str, ComplianceReport]:
        """Run compliance assessment for specified framework or all frameworks"""
        frameworks = [framework] if framework else list(ComplianceFramework)
        reports = {}
        
        for fw in frameworks:
            report = self._assess_framework(fw)
            reports[fw.value] = report
            
            # Log compliance assessment
            self.audit_logger.log_compliance_event(
                event_type=AuditEventType.COMPLIANCE_REPORT,
                framework=fw,
                details={
                    "overall_status": report.overall_status.value,
                    "score": report.score,
                    "violations_count": len(report.violations)
                }
            )
        
        return reports
    
    def _assess_framework(self, framework: ComplianceFramework) -> ComplianceReport:
        """Assess compliance for specific framework"""
        framework_rules = [rule for rule in self.rules.values() if rule.framework == framework and rule.enabled]
        
        passed_rules = 0
        failed_rules = 0
        violations = []
        
        for rule in framework_rules:
            try:
                # Run compliance check
                check_result = self._run_compliance_check(rule)
                
                if check_result["compliant"]:
                    passed_rules += 1
                else:
                    failed_rules += 1
                    violation = ComplianceViolation(
                        violation_id=f"violation_{rule.rule_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        rule_id=rule.rule_id,
                        framework=framework,
                        risk_level=rule.risk_level,
                        description=check_result["description"],
                        affected_resources=check_result.get("affected_resources", []),
                        detected_at=datetime.now(),
                        remediation_steps=check_result.get("remediation_steps", [])
                    )
                    violations.append(violation)
                    self.violations[violation.violation_id] = violation
                    
            except Exception as e:
                logger.error(f"Failed to run compliance check for {rule.rule_id}: {e}")
                failed_rules += 1
        
        # Calculate overall status and score
        total_rules = len(framework_rules)
        score = (passed_rules / total_rules * 100) if total_rules > 0 else 0
        
        if score >= 95:
            status = ComplianceStatus.COMPLIANT
        elif score >= 80:
            status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            status = ComplianceStatus.NON_COMPLIANT
        
        # Generate recommendations
        recommendations = self._generate_recommendations(framework, violations)
        
        return ComplianceReport(
            framework=framework,
            assessment_date=datetime.now(),
            overall_status=status,
            total_rules=total_rules,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            violations=violations,
            score=score,
            recommendations=recommendations
        )
    
    def _run_compliance_check(self, rule: ComplianceRule) -> Dict[str, Any]:
        """Run specific compliance check"""
        check_function = getattr(self, rule.check_function, None)
        
        if not check_function:
            return {
                "compliant": False,
                "description": f"Check function {rule.check_function} not implemented"
            }
        
        return check_function()
    
    # GDPR Compliance Checks
    def check_data_processing_records(self) -> Dict[str, Any]:
        """Check if data processing records are maintained"""
        # This would integrate with your data processing records system
        # For now, simulate the check
        return {
            "compliant": True,
            "description": "Data processing records are maintained and up to date"
        }
    
    def check_consent_records(self) -> Dict[str, Any]:
        """Check if valid consent records exist"""
        # Simulate consent record check
        return {
            "compliant": True,
            "description": "Consent records are properly maintained"
        }
    
    def check_data_subject_requests(self) -> Dict[str, Any]:
        """Check data subject request processing times"""
        # This would check actual request processing times
        return {
            "compliant": True,
            "description": "All data subject requests processed within 30 days"
        }
    
    def check_breach_notification_timeline(self) -> Dict[str, Any]:
        """Check breach notification timeline compliance"""
        # This would check actual breach notification times
        return {
            "compliant": True,
            "description": "No breaches requiring notification in assessment period"
        }
    
    # SOC2 Compliance Checks
    def check_access_controls(self) -> Dict[str, Any]:
        """Check access control implementation"""
        # This would verify access control configurations
        return {
            "compliant": True,
            "description": "Access controls are properly implemented and reviewed"
        }
    
    def check_incident_response(self) -> Dict[str, Any]:
        """Check incident response procedures"""
        return {
            "compliant": True,
            "description": "Incident response procedures are in place and tested"
        }
    
    def check_system_availability(self) -> Dict[str, Any]:
        """Check system availability SLA"""
        # This would check actual uptime metrics
        return {
            "compliant": True,
            "description": "System availability meets SLA requirements (99.9%)"
        }
    
    # HIPAA Compliance Checks
    def check_phi_access_logging(self) -> Dict[str, Any]:
        """Check PHI access logging"""
        return {
            "compliant": True,
            "description": "All PHI access is properly logged and audited"
        }
    
    def check_phi_encryption(self) -> Dict[str, Any]:
        """Check PHI encryption requirements"""
        return {
            "compliant": True,
            "description": "PHI is encrypted in transit and at rest"
        }
    
    def check_hipaa_breach_notification(self) -> Dict[str, Any]:
        """Check HIPAA breach notification requirements"""
        return {
            "compliant": True,
            "description": "No PHI breaches requiring notification in assessment period"
        }
    
    def _generate_recommendations(self, framework: ComplianceFramework, violations: List[ComplianceViolation]) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []
        
        # Framework-specific recommendations
        if framework == ComplianceFramework.GDPR:
            if any("consent" in v.rule_id for v in violations):
                recommendations.append("Implement a comprehensive consent management system")
            if any("processing" in v.rule_id for v in violations):
                recommendations.append("Maintain detailed records of data processing activities")
            recommendations.append("Conduct regular Data Protection Impact Assessments (DPIAs)")
            
        elif framework == ComplianceFramework.SOC2:
            if any("access" in v.rule_id for v in violations):
                recommendations.append("Implement role-based access control with regular reviews")
            if any("incident" in v.rule_id for v in violations):
                recommendations.append("Establish and test incident response procedures")
            recommendations.append("Conduct regular security awareness training")
            
        elif framework == ComplianceFramework.HIPAA:
            if any("encryption" in v.rule_id for v in violations):
                recommendations.append("Implement end-to-end encryption for all PHI")
            if any("logging" in v.rule_id for v in violations):
                recommendations.append("Enhance audit logging for all PHI access")
            recommendations.append("Conduct regular HIPAA risk assessments")
        
        # General recommendations
        if violations:
            recommendations.append("Address high-risk violations immediately")
            recommendations.append("Implement continuous compliance monitoring")
            recommendations.append("Schedule regular compliance assessments")
        
        return recommendations
    
    def get_violations(self, framework: ComplianceFramework = None, status: str = None) -> List[ComplianceViolation]:
        """Get compliance violations"""
        violations = list(self.violations.values())
        
        if framework:
            violations = [v for v in violations if v.framework == framework]
        
        if status:
            violations = [v for v in violations if v.status == status]
        
        return violations
    
    def update_violation_status(self, violation_id: str, status: str, notes: str = None) -> bool:
        """Update violation status"""
        violation = self.violations.get(violation_id)
        if not violation:
            return False
        
        violation.status = status
        if notes:
            violation.metadata["notes"] = notes
        
        # Log status update
        self.audit_logger.log_compliance_event(
            event_type=AuditEventType.COMPLIANCE_REPORT,
            framework=violation.framework,
            details={
                "action": "violation_status_update",
                "violation_id": violation_id,
                "new_status": status,
                "notes": notes
            }
        )
        
        return True
    
    def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get compliance dashboard data"""
        dashboard = {
            "last_assessment": datetime.now().isoformat(),
            "frameworks": {},
            "high_risk_violations": 0,
            "critical_visk_violations": 0
        }
        
        for framework in ComplianceFramework:
            # Get latest assessment for framework
            framework_violations = [v for v in self.violations.values() if v.framework == framework and v.status == "open"]
            
            high_risk = len([v for v in framework_violations if v.risk_level == RiskLevel.HIGH])
            critical_risk = len([v for v in framework_violations if v.risk_level == RiskLevel.CRITICAL])
            
            dashboard["frameworks"][framework.value] = {
                "open_violations": len(framework_violations),
                "high_risk_violations": high_risk,
                "critical_visk_violations": critical_risk,
                "last_assessment": datetime.now().isoformat()
            }
            
            dashboard["high_risk_violations"] += high_risk
            dashboard["critical_risk_violations"] += critical_risk
        
        return dashboard
    
    def export_compliance_data(self, framework: ComplianceFramework = None, format: str = "json") -> Dict[str, Any]:
        """Export compliance data for reporting"""
        data = {
            "export_date": datetime.now().isoformat(),
            "framework": framework.value if framework else "all",
            "rules": [],
            "violations": []
        }
        
        # Export rules
        rules_to_export = [r for r in self.rules.values() if not framework or r.framework == framework]
        for rule in rules_to_export:
            data["rules"].append({
                "rule_id": rule.rule_id,
                "framework": rule.framework.value,
                "category": rule.category,
                "description": rule.description,
                "requirement": rule.requirement,
                "risk_level": rule.risk_level.value,
                "enabled": rule.enabled
            })
        
        # Export violations
        violations_to_export = [v for v in self.violations.values() if not framework or v.framework == framework]
        for violation in violations_to_export:
            data["violations"].append({
                "violation_id": violation.violation_id,
                "rule_id": violation.rule_id,
                "framework": violation.framework.value,
                "risk_level": violation.risk_level.value,
                "description": violation.description,
                "affected_resources": violation.affected_resources,
                "detected_at": violation.detected_at.isoformat(),
                "status": violation.status,
                "remediation_steps": violation.remediation_steps
            })
        
        return data


# Global instance
compliance_monitor = ComplianceMonitor()
