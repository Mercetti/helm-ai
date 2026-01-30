"""
Helm AI Compliance Monitoring and Reporting
Provides compliance monitoring, reporting, and audit trail management
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import csv
import io

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from database.database_manager import get_database_manager
from security.security_hardening import security_auditor

@dataclass
class ComplianceFramework:
    """Compliance framework definition"""
    name: str
    version: str
    description: str
    requirements: List[str] = field(default_factory=list)
    controls: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'requirements': self.requirements,
            'controls': self.controls
        }

@dataclass
class ComplianceReport:
    """Compliance assessment report"""
    report_id: str
    framework: str
    timestamp: datetime
    period_start: datetime
    period_end: datetime
    overall_score: float  # 0-100
    requirements_met: int
    requirements_total: int
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'report_id': self.report_id,
            'framework': self.framework,
            'timestamp': self.timestamp.isoformat(),
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'overall_score': self.overall_score,
            'requirements_met': self.requirements_met,
            'requirements_total': self.requirements_total,
            'findings': self.findings,
            'recommendations': self.recommendations,
            'evidence': self.evidence
        }

@dataclass
class ComplianceControl:
    """Compliance control implementation"""
    control_id: str
    name: str
    description: str
    category: str
    framework: str
    implemented: bool
    last_assessed: datetime
    evidence_count: int
    gaps: List[str] = field(default_factory=list)
    remediation_plan: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'control_id': self.control_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'framework': self.framework,
            'implemented': self.implemented,
            'last_assessed': self.last_assessed.isoformat(),
            'evidence_count': self.evidence_count,
            'gaps': self.gaps,
            'remediation_plan': self.remediation_plan
        }

class ComplianceMonitor:
    """Compliance monitoring and assessment"""
    
    def __init__(self):
        self.frameworks = self._setup_frameworks()
        self.controls = self._setup_controls()
        self.reports = deque(maxlen=100)
        self.monitoring_active = False
        self.monitor_thread = None
        self.lock = threading.RLock()
        
    def _setup_frameworks(self) -> Dict[str, ComplianceFramework]:
        """Setup compliance frameworks"""
        return {
            'GDPR': ComplianceFramework(
                name='GDPR',
                version='2018',
                description='General Data Protection Regulation',
                requirements=[
                    'Lawful basis for processing',
                    'Data subject rights',
                    'Data protection by design',
                    'Data breach notification',
                    'Data protection impact assessment',
                    'Record keeping',
                    'International data transfers',
                    'Data retention policies'
                ]
            ),
            'SOC2': ComplianceFramework(
                name='SOC 2 Type II',
                version='2017',
                description='Service Organization Control 2',
                requirements=[
                    'Security',
                    'Availability',
                    'Processing integrity',
                    'Confidentiality',
                    'Privacy'
                ]
            ),
            'HIPAA': ComplianceFramework(
                name='HIPAA',
                version='2013',
                description='Health Insurance Portability and Accountability Act',
                requirements=[
                    'Administrative safeguards',
                    'Physical safeguards',
                    'Technical safeguards',
                    'Breach notification',
                    'Risk assessment',
                    'Policies and procedures'
                ]
            ),
            'ISO27001': ComplianceFramework(
                name='ISO 27001',
                version='2013',
                description='Information Security Management',
                requirements=[
                    'Information security policies',
                    'Risk assessment',
                    'Risk treatment',
                    'Statement of applicability',
                    'Information security objectives',
                    'Internal audit',
                    'Management review',
                    'Continual improvement'
                ]
            )
        }
    
    def _setup_controls(self) -> Dict[str, ComplianceControl]:
        """Setup compliance controls"""
        controls = {}
        
        # GDPR Controls
        controls.update({
            'GDPR_1': ComplianceControl(
                control_id='GDPR_1',
                name='Lawful Basis for Processing',
                description='Ensure lawful basis for all data processing activities',
                category='Data Processing',
                framework='GDPR',
                implemented=True,
                last_assessed=datetime.now(),
                evidence_count=5
            ),
            'GDPR_2': ComplianceControl(
                control_id='GDPR_2',
                name='Data Subject Rights',
                description='Implement mechanisms for data subject rights',
                category='Data Rights',
                framework='GDPR',
                implemented=True,
                last_assessed=datetime.now(),
                evidence_count=3
            ),
            'GDPR_3': ComplianceControl(
                control_id='GDPR_3',
                name='Data Protection by Design',
                description='Implement data protection by design principles',
                category='Data Protection',
                framework='GDPR',
                implemented=True,
                last_assessed=datetime.now(),
                evidence_count=7
            )
        })
        
        # SOC2 Controls
        controls.update({
            'SOC2_1': ComplianceControl(
                control_id='SOC2_1',
                name='Access Controls',
                description='Implement logical access controls',
                category='Security',
                framework='SOC2',
                implemented=True,
                last_assessed=datetime.now(),
                evidence_count=10
            ),
            'SOC2_2': ComplianceControl(
                control_id='SOC2_2',
                name='Incident Response',
                description='Implement incident response procedures',
                category='Security',
                framework='SOC2',
                implemented=True,
                last_assessed=datetime.now(),
                evidence_count=4
            )
        })
        
        return controls
    
    def start_monitoring(self):
        """Start compliance monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Compliance monitoring started")
    
    def stop_monitoring(self):
        """Stop compliance monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Compliance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                self._check_compliance_status()
                time.sleep(3600)  # Check every hour
            except Exception as e:
                logger.error(f"Compliance monitoring error: {e}")
                time.sleep(3600)
    
    def _check_compliance_status(self):
        """Check compliance status"""
        # This would run periodic compliance checks
        pass
    
    def assess_compliance(self, framework: str, period_days: int = 30) -> ComplianceReport:
        """Assess compliance for a framework"""
        logger.info(f"Starting compliance assessment for {framework}")
        
        framework_obj = self.frameworks.get(framework)
        if not framework_obj:
            raise ValueError(f"Unknown framework: {framework}")
        
        period_end = datetime.now()
        period_start = period_end - timedelta(days=period_days)
        
        # Get framework controls
        framework_controls = [c for c in self.controls.values() if c.framework == framework]
        
        # Assess each control
        findings = []
        requirements_met = 0
        total_requirements = len(framework_controls)
        
        for control in framework_controls:
            control_assessment = self._assess_control(control, period_start, period_end)
            findings.append(control_assessment)
            
            if control_assessment['compliant']:
                requirements_met += 1
        
        # Calculate overall score
        overall_score = (requirements_met / total_requirements) * 100 if total_requirements > 0 else 0
        
        # Generate recommendations
        recommendations = self._generate_recommendations(findings, framework)
        
        # Collect evidence
        evidence = self._collect_evidence(framework, period_start, period_end)
        
        report = ComplianceReport(
            report_id=secrets.token_hex(8),
            framework=framework,
            timestamp=datetime.now(),
            period_start=period_start,
            period_end=period_end,
            overall_score=overall_score,
            requirements_met=requirements_met,
            requirements_total=total_requirements,
            findings=findings,
            recommendations=recommendations,
            evidence=evidence
        )
        
        # Store report
        with self.lock:
            self.reports.append(report)
        
        logger.info(f"Compliance assessment completed: {framework} - {overall_score:.1f}%")
        
        return report
    
    def _assess_control(self, control: ComplianceControl, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Assess a specific control"""
        try:
            # Check if control is implemented
            if not control.implemented:
                return {
                    'control_id': control.control_id,
                    'name': control.name,
                    'compliant': False,
                    'findings': ['Control not implemented'],
                    'evidence_count': 0
                }
            
            # Collect evidence for the control
            evidence = self._collect_control_evidence(control, period_start, period_end)
            
            # Assess compliance based on evidence
            compliant = len(evidence) >= control.evidence_count
            
            findings = []
            if not compliant:
                findings.append(f"Insufficient evidence: {len(evidence)}/{control.evidence_count}")
            
            return {
                'control_id': control.control_id,
                'name': control.name,
                'compliant': compliant,
                'findings': findings,
                'evidence_count': len(evidence),
                'evidence': evidence[:5]  # Return first 5 evidence items
            }
            
        except Exception as e:
            logger.error(f"Error assessing control {control.control_id}: {e}")
            return {
                'control_id': control.control_id,
                'name': control.name,
                'compliant': False,
                'findings': [f"Assessment error: {str(e)}"],
                'evidence_count': 0
            }
    
    def _collect_control_evidence(self, control: ComplianceControl, period_start: datetime, period_end: datetime) -> List[Dict[str, Any]]:
        """Collect evidence for a control"""
        evidence = []
        
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                if control.framework == 'GDPR':
                    if 'Data Subject Rights' in control.name:
                        # Check for data subject request logs
                        result = session.execute(text("""
                            SELECT COUNT(*) FROM audit_logs
                            WHERE action LIKE '%data_subject%'
                            AND created_at BETWEEN :start AND :end
                        """), {'start': period_start, 'end': period_end})
                        
                        count = result.scalar()
                        if count > 0:
                            evidence.append({
                                'type': 'audit_log',
                                'description': f'Data subject requests processed: {count}',
                                'timestamp': datetime.now().isoformat()
                            })
                    
                    elif 'Data Protection by Design' in control.name:
                        # Check for security measures
                        result = session.execute(text("""
                            SELECT COUNT(*) FROM security_events
                            WHERE created_at BETWEEN :start AND :end
                        """), {'start': period_start, 'end': period_end})
                        
                        count = result.scalar()
                        evidence.append({
                            'type': 'security_monitoring',
                            'description': f'Security events monitored: {count}',
                            'timestamp': datetime.now().isoformat()
                        })
                
                elif control.framework == 'SOC2':
                    if 'Access Controls' in control.name:
                        # Check for access control logs
                        result = session.execute(text("""
                            SELECT COUNT(*) FROM audit_logs
                            WHERE action LIKE '%login%' OR action LIKE '%access%'
                            AND created_at BETWEEN :start AND :end
                        """), {'start': period_start, 'end': period_end})
                        
                        count = result.scalar()
                        if count > 0:
                            evidence.append({
                                'type': 'access_control',
                                'description': f'Access control events: {count}',
                                'timestamp': datetime.now().isoformat()
                            })
                    
                    elif 'Incident Response' in control.name:
                        # Check for incident response activities
                        result = session.execute(text("""
                            SELECT COUNT(*) FROM security_events
                            WHERE severity IN ('high', 'critical')
                            AND created_at BETWEEN :start AND :end
                        """), {'start': period_start, 'end': period_end})
                        
                        count = result.scalar()
                        evidence.append({
                            'type': 'incident_response',
                            'description': f'Security incidents handled: {count}',
                            'timestamp': datetime.now().isoformat()
                        })
                
        except Exception as e:
            logger.error(f"Error collecting evidence for {control.control_id}: {e}")
        
        return evidence
    
    def _generate_recommendations(self, findings: List[Dict[str, Any]], framework: str) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        # Find non-compliant controls
        non_compliant = [f for f in findings if not f['compliant']]
        
        if non_compliant:
            recommendations.append(f"Address {len(non_compliant)} non-compliant controls")
            
            for finding in non_compliant:
                recommendations.append(f"Implement control: {finding['name']}")
        
        # Framework-specific recommendations
        if framework == 'GDPR':
            recommendations.extend([
                "Review data processing activities",
                "Update privacy policies",
                "Conduct DPIA for high-risk processing"
            ])
        elif framework == 'SOC2':
            recommendations.extend([
                "Enhance security monitoring",
                "Update incident response procedures",
                "Conduct regular security assessments"
            ])
        elif framework == 'HIPAA':
            recommendations.extend([
                "Review PHI handling procedures",
                "Update security policies",
                "Conduct risk assessment"
            ])
        elif framework == 'ISO27001':
            recommendations.extend([
                "Update information security policies",
                "Conduct risk assessment",
                "Implement continuous monitoring"
            ])
        
        return recommendations
    
    def _collect_evidence(self, framework: str, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Collect compliance evidence"""
        evidence = {
            'audit_logs': 0,
            'security_events': 0,
            'user_activities': 0,
            'system_changes': 0
        }
        
        try:
            db_manager = get_database_manager()
            
            with db_manager.get_session() as session:
                # Count audit logs
                result = session.execute(text("""
                    SELECT COUNT(*) FROM audit_logs
                    WHERE created_at BETWEEN :start AND :end
                """), {'start': period_start, 'end': period_end})
                evidence['audit_logs'] = result.scalar()
                
                # Count security events
                result = session.execute(text("""
                    SELECT COUNT(*) FROM security_events
                    WHERE created_at BETWEEN :start AND :end
                """), {'start': period_start, 'end': period_end})
                evidence['security_events'] = result.scalar()
                
                # Count user activities
                result = session.execute(text("""
                    SELECT COUNT(*) FROM audit_logs
                    WHERE action LIKE '%user_%'
                    AND created_at BETWEEN :start AND :end
                """), {'start': period_start, 'end': period_end})
                evidence['user_activities'] = result.scalar()
                
                # Count system changes
                result = session.execute(text("""
                    SELECT COUNT(*) FROM audit_logs
                    WHERE action LIKE '%config_%' OR action LIKE '%system_%'
                    AND created_at BETWEEN :start AND :end
                """), {'start': period_start, 'end': period_end})
                evidence['system_changes'] = result.scalar()
                
        except Exception as e:
            logger.error(f"Error collecting evidence: {e}")
        
        return evidence
    
    def get_compliance_summary(self, framework: Optional[str] = None) -> Dict[str, Any]:
        """Get compliance summary"""
        with self.lock:
            reports = list(self.reports)
        
        if framework:
            reports = [r for r in reports if r.framework == framework]
        
        if not reports:
            return {
                'framework': framework,
                'total_reports': 0,
                'latest_score': 0,
                'average_score': 0,
                'trend': 'stable'
            }
        
        latest_report = reports[-1]
        average_score = sum(r.overall_score for r in reports) / len(reports)
        
        # Calculate trend
        if len(reports) >= 3:
            recent_scores = [r.overall_score for r in reports[-3:]]
            if recent_scores[-1] > recent_scores[0]:
                trend = 'improving'
            elif recent_scores[-1] < recent_scores[0]:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'framework': framework,
            'total_reports': len(reports),
            'latest_score': latest_report.overall_score,
            'average_score': average_score,
            'trend': trend,
            'last_assessment': latest_report.timestamp.isoformat()
        }
    
    def export_report(self, report_id: str, format: str = 'json') -> str:
        """Export compliance report"""
        with self.lock:
            report = next((r for r in self.reports if r.report_id == report_id), None)
        
        if not report:
            raise ValueError(f"Report not found: {report_id}")
        
        if format == 'json':
            return json.dumps(report.to_dict(), indent=2)
        elif format == 'csv':
            return self._export_csv(report)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_csv(self, report: ComplianceReport) -> str:
        """Export report as CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Control ID', 'Control Name', 'Compliant', 'Findings', 'Evidence Count'])
        
        # Write findings
        for finding in report.findings:
            writer.writerow([
                finding['control_id'],
                finding['name'],
                finding['compliant'],
                '; '.join(finding['findings']),
                finding['evidence_count']
            ])
        
        return output.getvalue()

# Global compliance monitoring instance
compliance_monitor = ComplianceMonitor()

def start_compliance_monitoring():
    """Start compliance monitoring"""
    compliance_monitor.start_monitoring()
    logger.info("Compliance monitoring system started")

def stop_compliance_monitoring():
    """Stop compliance monitoring"""
    compliance_monitor.stop_monitoring()
    logger.info("Compliance monitoring system stopped")

def assess_compliance(framework: str, period_days: int = 30) -> ComplianceReport:
    """Assess compliance for a framework"""
    return compliance_monitor.assess_compliance(framework, period_days)

def get_compliance_status() -> Dict[str, Any]:
    """Get comprehensive compliance status"""
    return {
        'timestamp': datetime.now().isoformat(),
        'monitoring_active': compliance_monitor.monitoring_active,
        'frameworks': {k: v.to_dict() for k, v in compliance_monitor.frameworks.items()},
        'controls': {k: v.to_dict() for k, v in compliance_monitor.controls.items()},
        'summaries': {
            framework: compliance_monitor.get_compliance_summary(framework)
            for framework in compliance_monitor.frameworks.keys()
        }
    }
