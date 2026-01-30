"""
Automated Compliance Checking System for Helm AI
============================================

This module provides comprehensive compliance capabilities:
- Automated compliance monitoring
- Regulatory framework support (GDPR, HIPAA, SOX, PCI-DSS)
- Policy violation detection
- Compliance reporting and analytics
- Risk assessment and scoring
- Audit trail management
- Remediation tracking
- Compliance dashboard
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict

# Local imports
from src.monitoring.structured_logging import StructuredLogger
from src.database.database_manager import DatabaseManager

logger = StructuredLogger("compliance_system")


class ComplianceFramework(str, Enum):
    """Compliance frameworks"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    NIST = "nist"
    SOC_2 = "soc_2"
    CCPA = "ccpa"


class ComplianceStatus(str, Enum):
    """Compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_ASSESSED = "not_assessed"
    PENDING_REVIEW = "pending_review"


class RiskLevel(str, Enum):
    """Risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CheckType(str, Enum):
    """Types of compliance checks"""
    AUTOMATED = "automated"
    MANUAL = "manual"
    HYBRID = "hybrid"


@dataclass
class ComplianceRule:
    """Compliance rule configuration"""
    id: str
    name: str
    description: str
    framework: ComplianceFramework
    category: str
    requirement_id: str
    check_type: CheckType
    severity: RiskLevel
    check_script: Optional[str] = None
    manual_procedure: Optional[str] = None
    evidence_required: List[str] = field(default_factory=list)
    remediation_steps: List[str] = field(default_factory=list)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ComplianceCheck:
    """Compliance check result"""
    id: str
    rule_id: str
    status: ComplianceStatus
    score: float = 0.0
    findings: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    checked_at: datetime = field(default_factory=datetime.utcnow)
    checked_by: str = "system"
    notes: str = ""
    remediation_required: bool = False


@dataclass
class ComplianceReport:
    """Compliance report"""
    id: str
    framework: ComplianceFramework
    period_start: datetime
    period_end: datetime
    overall_score: float = 0.0
    total_rules: int = 0
    compliant_rules: int = 0
    non_compliant_rules: int = 0
    partially_compliant_rules: int = 0
    risk_score: float = 0.0
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ComplianceAudit:
    """Compliance audit trail"""
    id: str
    action: str
    entity_type: str
    entity_id: str
    user_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: str = ""
    user_agent: str = ""


class AutomatedComplianceSystem:
    """Automated Compliance Checking System"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        
        # Storage
        self.rules: Dict[str, ComplianceRule] = {}
        self.checks: Dict[str, ComplianceCheck] = {}
        self.reports: Dict[str, ComplianceReport] = {}
        self.audits: List[ComplianceAudit] = []
        
        # Initialize default compliance rules
        self._initialize_default_rules()
        
        logger.info("Automated Compliance System initialized")
    
    def _initialize_default_rules(self):
        """Initialize default compliance rules"""
        default_rules = [
            # GDPR Rules
            ComplianceRule(
                id="gdpr_data_consent",
                name="Data Processing Consent",
                description="Ensure explicit consent is obtained for data processing",
                framework=ComplianceFramework.GDPR,
                category="Data Protection",
                requirement_id="Art.6(1)(a)",
                check_type=CheckType.AUTOMATED,
                severity=RiskLevel.HIGH,
                check_script="check_data_consent",
                evidence_required=["consent_records", "privacy_policy", "consent_forms"],
                remediation_steps=["Update consent mechanism", "Review consent records", "Update privacy policy"]
            ),
            ComplianceRule(
                id="gdpr_data_breach_notification",
                name="Data Breach Notification",
                description="Notify supervisory authority within 72 hours of data breach",
                framework=ComplianceFramework.GDPR,
                category="Incident Response",
                requirement_id="Art.33",
                check_type=CheckType.HYBRID,
                severity=RiskLevel.CRITICAL,
                check_script="check_breach_notification_process",
                manual_procedure="Verify breach notification procedures and timelines",
                evidence_required=["breach_procedure", "notification_templates", "incident_logs"],
                remediation_steps=["Update breach procedures", "Train staff on notification requirements", "Implement automated alerts"]
            ),
            ComplianceRule(
                id="gdpr_right_to_access",
                name="Right to Access",
                description="Provide data subjects with access to their personal data",
                framework=ComplianceFramework.GDPR,
                category="Data Subject Rights",
                requirement_id="Art.15",
                check_type=CheckType.AUTOMATED,
                severity=RiskLevel.MEDIUM,
                check_script="check_data_access_procedure",
                evidence_required=["access_request_procedure", "response_templates", "access_logs"],
                remediation_steps=["Implement data access portal", "Update access procedures", "Train support staff"]
            ),
            
            # HIPAA Rules
            ComplianceRule(
                id="hipaa_encryption_at_rest",
                name="Encryption at Rest",
                description="Encrypt all PHI stored in systems",
                framework=ComplianceFramework.HIPAA,
                category="Security",
                requirement_id="164.312(a)(2)(iv)",
                check_type=CheckType.AUTOMATED,
                severity=RiskLevel.HIGH,
                check_script="check_encryption_at_rest",
                evidence_required=["encryption_certificates", "encryption_policies", "system_configs"],
                remediation_steps=["Implement encryption", "Update security policies", "Train staff on encryption"]
            ),
            ComplianceRule(
                id="hipaa_access_controls",
                name="Access Controls",
                description="Implement unique user identification and access controls",
                framework=ComplianceFramework.HIPAA,
                category="Access Management",
                requirement_id="164.312(a)(1)",
                check_type=CheckType.AUTOMATED,
                severity=RiskLevel.HIGH,
                check_script="check_access_controls",
                evidence_required=["access_logs", "user_accounts", "access_policies"],
                remediation_steps=["Implement role-based access", "Review user accounts", "Update access policies"]
            ),
            
            # SOX Rules
            ComplianceRule(
                id="sox_financial_controls",
                name="Financial Controls",
                description="Maintain internal controls over financial reporting",
                framework=ComplianceFramework.SOX,
                category="Financial Controls",
                requirement_id="302",
                check_type=CheckType.HYBRID,
                severity=RiskLevel.CRITICAL,
                check_script="check_financial_controls",
                manual_procedure="Review financial control documentation and procedures",
                evidence_required=["control_documentation", "audit_reports", "financial_statements"],
                remediation_steps=["Update control procedures", "Implement additional controls", "Train finance staff"]
            ),
            
            # PCI-DSS Rules
            ComplianceRule(
                id="pci_encryption_transmission",
                name="Encryption of Cardholder Data",
                description="Encrypt cardholder data during transmission",
                framework=ComplianceFramework.PCI_DSS,
                category="Data Protection",
                requirement_id="4.1",
                check_type=CheckType.AUTOMATED,
                severity=RiskLevel.CRITICAL,
                check_script="check_transmission_encryption",
                evidence_required=["ssl_certificates", "encryption_configs", "network_logs"],
                remediation_steps=["Implement SSL/TLS", "Update encryption policies", "Configure secure transmission"]
            ),
            
            # ISO 27001 Rules
            ComplianceRule(
                id="iso27001_risk_assessment",
                name="Risk Assessment",
                description="Conduct regular risk assessments",
                framework=ComplianceFramework.ISO_27001,
                category="Risk Management",
                requirement_id="A.5.1.1",
                check_type=CheckType.HYBRID,
                severity=RiskLevel.MEDIUM,
                check_script="check_risk_assessment_process",
                manual_procedure="Review risk assessment methodology and documentation",
                evidence_required=["risk_assessment_reports", "risk_registers", "mitigation_plans"],
                remediation_steps=["Update risk assessment process", "Conduct new assessment", "Update risk register"]
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.id] = rule
    
    def add_compliance_rule(self, rule: ComplianceRule) -> bool:
        """Add a new compliance rule"""
        try:
            self.rules[rule.id] = rule
            logger.info(f"Compliance rule added: {rule.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add compliance rule: {e}")
            return False
    
    async def run_compliance_check(self, rule_id: str, context: Dict[str, Any] = None) -> ComplianceCheck:
        """Run a compliance check"""
        try:
            if rule_id not in self.rules:
                raise ValueError(f"Rule {rule_id} not found")
            
            rule = self.rules[rule_id]
            
            # Create compliance check
            check = ComplianceCheck(
                id=str(uuid.uuid4()),
                rule_id=rule_id,
                status=ComplianceStatus.NOT_ASSESSED
            )
            
            # Run check based on type
            if rule.check_type == CheckType.AUTOMATED:
                result = await self._run_automated_check(rule, context or {})
            elif rule.check_type == CheckType.MANUAL:
                result = await self._run_manual_check(rule, context or {})
            else:  # HYBRID
                result = await self._run_hybrid_check(rule, context or {})
            
            # Update check with results
            check.status = result["status"]
            check.score = result["score"]
            check.findings = result["findings"]
            check.evidence = result["evidence"]
            check.notes = result["notes"]
            check.remediation_required = result["remediation_required"]
            
            # Store check
            self.checks[check.id] = check
            
            # Log audit trail
            self._log_audit("compliance_check", "rule", rule_id, {
                "check_id": check.id,
                "status": check.status.value,
                "score": check.score
            })
            
            logger.info(f"Compliance check completed: {check.id}")
            return check
            
        except Exception as e:
            logger.error(f"Compliance check failed for {rule_id}: {e}")
            raise
    
    async def _run_automated_check(self, rule: ComplianceRule, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run automated compliance check"""
        try:
            # Simulate automated check execution
            check_script = rule.check_script
            
            if check_script == "check_data_consent":
                result = await self._check_data_consent(context)
            elif check_script == "check_breach_notification_process":
                result = await self._check_breach_notification_process(context)
            elif check_script == "check_data_access_procedure":
                result = await self._check_data_access_procedure(context)
            elif check_script == "check_encryption_at_rest":
                result = await self._check_encryption_at_rest(context)
            elif check_script == "check_access_controls":
                result = await self._check_access_controls(context)
            elif check_script == "check_financial_controls":
                result = await self._check_financial_controls(context)
            elif check_script == "check_transmission_encryption":
                result = await self._check_transmission_encryption(context)
            elif check_script == "check_risk_assessment_process":
                result = await self._check_risk_assessment_process(context)
            else:
                result = {
                    "status": ComplianceStatus.NOT_ASSESSED,
                    "score": 0.0,
                    "findings": ["Check script not implemented"],
                    "evidence": [],
                    "notes": "Automated check not available",
                    "remediation_required": False
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Automated check failed: {e}")
            return {
                "status": ComplianceStatus.NOT_ASSESSED,
                "score": 0.0,
                "findings": [f"Check execution failed: {str(e)}"],
                "evidence": [],
                "notes": "Error during automated check",
                "remediation_required": True
            }
    
    async def _check_data_consent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check data consent compliance"""
        try:
            # Simulate consent check
            consent_records = context.get("consent_records", [])
            privacy_policy = context.get("privacy_policy", {})
            
            findings = []
            score = 100.0
            evidence = []
            remediation_required = False
            
            # Check if consent records exist
            if not consent_records:
                findings.append("No consent records found")
                score -= 50
                remediation_required = True
            else:
                evidence.append("Consent records available")
                
                # Check consent validity
                valid_consents = sum(1 for record in consent_records if record.get("valid", False))
                if valid_consents < len(consent_records) * 0.9:
                    findings.append(f"Only {valid_consents}/{len(consents)} consent records are valid")
                    score -= 30
                    remediation_required = True
                else:
                    evidence.append(f"{valid_consents} valid consent records")
            
            # Check privacy policy
            if not privacy_policy:
                findings.append("Privacy policy not found")
                score -= 20
                remediation_required = True
            else:
                evidence.append("Privacy policy available")
                
                # Check policy completeness
                required_sections = ["data_collection", "data_usage", "user_rights", "contact_info"]
                missing_sections = [s for s in required_sections if s not in privacy_policy]
                if missing_sections:
                    findings.append(f"Privacy policy missing sections: {', '.join(missing_sections)}")
                    score -= 10 * len(missing_sections)
                    remediation_required = True
                else:
                    evidence.append("Privacy policy contains all required sections")
            
            # Determine status
            if score >= 90:
                status = ComplianceStatus.COMPLIANT
            elif score >= 70:
                status = ComplianceStatus.PARTIALLY_COMPLIANT
            else:
                status = ComplianceStatus.NON_COMPLIANT
            
            return {
                "status": status,
                "score": score,
                "findings": findings,
                "evidence": evidence,
                "notes": f"GDPR consent check completed with score {score:.1f}%",
                "remediation_required": remediation_required
            }
            
        except Exception as e:
            logger.error(f"Data consent check failed: {e}")
            raise
    
    async def _check_encryption_at_rest(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check encryption at rest compliance"""
        try:
            # Simulate encryption check
            systems = context.get("systems", [])
            encryption_policies = context.get("encryption_policies", {})
            
            findings = []
            score = 100.0
            evidence = []
            remediation_required = False
            
            # Check system encryption
            encrypted_systems = 0
            for system in systems:
                if system.get("encrypted", False):
                    encrypted_systems += 1
                    evidence.append(f"System {system.get('name', 'Unknown')} is encrypted")
                else:
                    findings.append(f"System {system.get('name', 'Unknown')} is not encrypted")
                    score -= 20
                    remediation_required = True
            
            if systems:
                encryption_rate = encrypted_systems / len(systems)
                if encryption_rate < 1.0:
                    findings.append(f"Only {encryption_rate:.1%} of systems are encrypted")
                    score -= 30 * (1 - encryption_rate)
                    remediation_required = True
                else:
                    evidence.append("All systems are encrypted")
            
            # Check encryption policies
            if not encryption_policies:
                findings.append("No encryption policies found")
                score -= 20
                remediation_required = True
            else:
                evidence.append("Encryption policies available")
                
                # Check policy completeness
                required_policies = ["data_encryption", "key_management", "access_control"]
                missing_policies = [p for p in required_policies if p not in encryption_policies]
                if missing_policies:
                    findings.append(f"Missing encryption policies: {', '.join(missing_policies)}")
                    score -= 10 * len(missing_policies)
                    remediation_required = True
                else:
                    evidence.append("All required encryption policies in place")
            
            # Determine status
            if score >= 95:
                status = ComplianceStatus.COMPLIANT
            elif score >= 80:
                status = ComplianceStatus.PARTIALLY_COMPLIANT
            else:
                status = ComplianceStatus.NON_COMPLIANT
            
            return {
                "status": status,
                "score": score,
                "findings": findings,
                "evidence": evidence,
                "notes": f"Encryption at rest check completed with score {score:.1f}%",
                "remediation_required": remediation_required
            }
            
        except Exception as e:
            logger.error(f"Encryption check failed: {e}")
            raise
    
    async def _run_manual_check(self, rule: ComplianceRule, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run manual compliance check"""
        try:
            # For manual checks, return pending status
            return {
                "status": ComplianceStatus.PENDING_REVIEW,
                "score": 0.0,
                "findings": [f"Manual review required: {rule.manual_procedure}"],
                "evidence": [],
                "notes": "Manual check pending review by compliance officer",
                "remediation_required": False
            }
            
        except Exception as e:
            logger.error(f"Manual check failed: {e}")
            raise
    
    async def _run_hybrid_check(self, rule: ComplianceRule, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run hybrid compliance check"""
        try:
            # Run automated part first
            automated_result = await self._run_automated_check(rule, context)
            
            # Add manual review requirement
            automated_result["findings"].append(f"Manual verification required: {rule.manual_procedure}")
            automated_result["notes"] += " + Manual review required"
            
            # Adjust status for hybrid checks
            if automated_result["status"] == ComplianceStatus.COMPLIANT:
                automated_result["status"] = ComplianceStatus.PENDING_REVIEW
            
            return automated_result
            
        except Exception as e:
            logger.error(f"Hybrid check failed: {e}")
            raise
    
    async def generate_compliance_report(self, framework: ComplianceFramework, 
                                       period_start: datetime, period_end: datetime) -> ComplianceReport:
        """Generate compliance report"""
        try:
            # Get framework rules
            framework_rules = [rule for rule in self.rules.values() if rule.framework == framework]
            
            # Get checks for the period
            period_checks = [
                check for check in self.checks.values()
                if period_start <= check.checked_at <= period_end
            ]
            
            # Calculate metrics
            total_rules = len(framework_rules)
            compliant_rules = 0
            non_compliant_rules = 0
            partially_compliant_rules = 0
            
            findings = []
            recommendations = []
            
            for rule in framework_rules:
                rule_checks = [check for check in period_checks if check.rule_id == rule.id]
                
                if rule_checks:
                    latest_check = max(rule_checks, key=lambda c: c.checked_at)
                    
                    if latest_check.status == ComplianceStatus.COMPLIANT:
                        compliant_rules += 1
                    elif latest_check.status == ComplianceStatus.NON_COMPLIANT:
                        non_compliant_rules += 1
                        findings.append({
                            "rule_id": rule.id,
                            "rule_name": rule.name,
                            "severity": rule.severity.value,
                            "findings": latest_check.findings,
                            "remediation_steps": rule.remediation_steps
                        })
                    elif latest_check.status == ComplianceStatus.PARTIALLY_COMPLIANT:
                        partially_compliant_rules += 1
                        findings.append({
                            "rule_id": rule.id,
                            "rule_name": rule.name,
                            "severity": rule.severity.value,
                            "findings": latest_check.findings,
                            "remediation_steps": rule.remediation_steps
                        })
                else:
                    # Rule not checked
                    findings.append({
                        "rule_id": rule.id,
                        "rule_name": rule.name,
                        "severity": rule.severity.value,
                        "findings": ["Rule not assessed during period"],
                        "remediation_steps": rule.remediation_steps
                    })
            
            # Calculate overall score
            if total_rules > 0:
                overall_score = (compliant_rules / total_rules) * 100
            else:
                overall_score = 0.0
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(framework_rules, period_checks)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(framework, findings)
            
            # Create report
            report = ComplianceReport(
                id=str(uuid.uuid4()),
                framework=framework,
                period_start=period_start,
                period_end=period_end,
                overall_score=overall_score,
                total_rules=total_rules,
                compliant_rules=compliant_rules,
                non_compliant_rules=non_compliant_rules,
                partially_compliant_rules=partially_compliant_rules,
                risk_score=risk_score,
                findings=findings,
                recommendations=recommendations
            )
            
            # Store report
            self.reports[report.id] = report
            
            # Log audit trail
            self._log_audit("report_generated", "framework", framework.value, {
                "report_id": report.id,
                "overall_score": overall_score,
                "risk_score": risk_score
            })
            
            logger.info(f"Compliance report generated: {report.id}")
            return report
            
        except Exception as e:
            logger.error(f"Compliance report generation failed: {e}")
            raise
    
    def _calculate_risk_score(self, rules: List[ComplianceRule], checks: List[ComplianceCheck]) -> float:
        """Calculate risk score based on compliance status and rule severity"""
        try:
            severity_weights = {
                RiskLevel.LOW: 1,
                RiskLevel.MEDIUM: 2,
                RiskLevel.HIGH: 3,
                RiskLevel.CRITICAL: 4
            }
            
            total_risk = 0.0
            max_risk = 0.0
            
            for rule in rules:
                rule_checks = [check for check in checks if check.rule_id == rule.id]
                
                if rule_checks:
                    latest_check = max(rule_checks, key=lambda c: c.checked_at)
                    
                    # Calculate risk based on status and severity
                    if latest_check.status == ComplianceStatus.NON_COMPLIANT:
                        risk_weight = severity_weights[rule.severity]
                        total_risk += risk_weight
                    elif latest_check.status == ComplianceStatus.PARTIALLY_COMPLIANT:
                        risk_weight = severity_weights[rule.severity] * 0.5
                        total_risk += risk_weight
                
                max_risk += severity_weights[rule.severity]
            
            # Convert to 0-100 scale (lower is better)
            if max_risk > 0:
                risk_score = (total_risk / max_risk) * 100
            else:
                risk_score = 0.0
            
            return risk_score
            
        except Exception as e:
            logger.error(f"Risk score calculation failed: {e}")
            return 0.0
    
    def _generate_recommendations(self, framework: ComplianceFramework, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate compliance recommendations"""
        try:
            recommendations = []
            
            # Group findings by severity
            critical_findings = [f for f in findings if f.get("severity") == "critical"]
            high_findings = [f for f in findings if f.get("severity") == "high"]
            medium_findings = [f for f in findings if f.get("severity") == "medium"]
            low_findings = [f for f in findings if f.get("severity") == "low"]
            
            # Framework-specific recommendations
            if framework == ComplianceFramework.GDPR:
                if critical_findings or high_findings:
                    recommendations.append("Immediately address critical GDPR compliance gaps to avoid significant penalties")
                recommendations.append("Review and update data processing agreements with all third parties")
                recommendations.append("Implement regular data protection impact assessments (DPIAs)")
                recommendations.append("Conduct staff training on GDPR requirements and data protection principles")
            
            elif framework == ComplianceFramework.HIPAA:
                if critical_findings or high_findings:
                    recommendations.append("Address critical HIPAA security requirements immediately to protect patient data")
                recommendations.append("Implement regular security awareness training for all staff")
                recommendations.append("Conduct annual risk assessments and security evaluations")
                recommendations.append("Review and update business associate agreements")
            
            elif framework == ComplianceFramework.PCI_DSS:
                if critical_findings or high_findings:
                    recommendations.append("Immediately address critical PCI-DSS requirements to protect cardholder data")
                recommendations.append("Implement quarterly vulnerability scanning and penetration testing")
                recommendations.append("Review and update network segmentation and access controls")
                recommendations.append("Conduct annual PCI-DSS assessment by qualified security assessor")
            
            # General recommendations based on findings
            if len(findings) > 10:
                recommendations.append("Prioritize addressing high-severity compliance gaps first")
                recommendations.append("Implement a compliance management system for ongoing monitoring")
            
            if any("not assessed" in str(f.get("findings", [])).lower() for f in findings):
                recommendations.append("Complete all pending compliance assessments")
            
            # Add specific remediation recommendations
            unique_remediations = set()
            for finding in findings:
                for step in finding.get("remediation_steps", []):
                    unique_remediations.add(step)
            
            recommendations.extend(list(unique_remediations)[:5])  # Limit to top 5
            
            return recommendations[:10]  # Limit to 10 recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Review compliance requirements and implement necessary controls"]
    
    def _log_audit(self, action: str, entity_type: str, entity_id: str, details: Dict[str, Any]):
        """Log compliance audit trail"""
        try:
            audit = ComplianceAudit(
                id=str(uuid.uuid4()),
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=details.get("user_id", "system"),
                details=details,
                ip_address=details.get("ip_address", ""),
                user_agent=details.get("user_agent", "")
            )
            
            self.audits.append(audit)
            
            # Keep only last 10000 audit entries
            if len(self.audits) > 10000:
                self.audits = self.audits[-10000:]
            
        except Exception as e:
            logger.error(f"Audit logging failed: {e}")
    
    def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get compliance dashboard data"""
        try:
            dashboard = {
                "frameworks": {},
                "overall_status": {},
                "recent_checks": [],
                "upcoming_deadlines": [],
                "risk_trends": {}
            }
            
            # Framework status
            for framework in ComplianceFramework:
                framework_rules = [rule for rule in self.rules.values() if rule.framework == framework]
                framework_checks = [check for check in self.checks.values() 
                                 if any(rule.framework == framework for rule in self.rules.values() 
                                     if rule.id == check.rule_id)]
                
                if framework_checks:
                    latest_checks = {}
                    for rule in framework_rules:
                        rule_checks = [check for check in framework_checks if check.rule_id == rule.id]
                        if rule_checks:
                            latest_checks[rule.id] = max(rule_checks, key=lambda c: c.checked_at)
                    
                    compliant = sum(1 for check in latest_checks.values() 
                                  if check.status == ComplianceStatus.COMPLIANT)
                    non_compliant = sum(1 for check in latest_checks.values() 
                                      if check.status == ComplianceStatus.NON_COMPLIANT)
                    partially_compliant = sum(1 for check in latest_checks.values() 
                                            if check.status == ComplianceStatus.PARTIALLY_COMPLIANT)
                    
                    dashboard["frameworks"][framework.value] = {
                        "total_rules": len(framework_rules),
                        "compliant": compliant,
                        "non_compliant": non_compliant,
                        "partially_compliant": partially_compliant,
                        "compliance_rate": (compliant / len(framework_rules)) * 100 if framework_rules else 0
                    }
            
            # Recent checks
            recent_checks = sorted(self.checks.values(), key=lambda c: c.checked_at, reverse=True)[:10]
            dashboard["recent_checks"] = [
                {
                    "id": check.id,
                    "rule_id": check.rule_id,
                    "rule_name": self.rules.get(check.rule_id, {}).name if check.rule_id in self.rules else "Unknown",
                    "status": check.status.value,
                    "score": check.score,
                    "checked_at": check.checked_at.isoformat()
                }
                for check in recent_checks
            ]
            
            # Overall status
            total_rules = len(self.rules)
            if total_rules > 0:
                total_compliant = sum(1 for check in self.checks.values() 
                                    if check.status == ComplianceStatus.COMPLIANT)
                dashboard["overall_status"] = {
                    "total_rules": total_rules,
                    "compliance_rate": (total_compliant / total_rules) * 100,
                    "last_updated": datetime.utcnow().isoformat()
                }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Dashboard generation failed: {e}")
            return {"error": str(e)}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "total_rules": len(self.rules),
            "total_checks": len(self.checks),
            "total_reports": len(self.reports),
            "total_audits": len(self.audits),
            "supported_frameworks": [f.value for f in ComplianceFramework],
            "check_types": [t.value for t in CheckType],
            "system_uptime": datetime.utcnow().isoformat()
        }


# Configuration
COMPLIANCE_CONFIG = {
    "database": {
        "connection_string": os.getenv("DATABASE_URL")
    },
    "automation": {
        "check_interval": 24,  # hours
        "report_frequency": "monthly",
        "alert_threshold": 0.8
    },
    "frameworks": {
        "enabled": ["gdpr", "hipaa", "sox", "pci_dss", "iso_27001"]
    }
}


# Initialize automated compliance system
automated_compliance_system = AutomatedComplianceSystem(COMPLIANCE_CONFIG)

# Export main components
__all__ = [
    'AutomatedComplianceSystem',
    'ComplianceRule',
    'ComplianceCheck',
    'ComplianceReport',
    'ComplianceAudit',
    'ComplianceFramework',
    'ComplianceStatus',
    'RiskLevel',
    'CheckType',
    'automated_compliance_system'
]
