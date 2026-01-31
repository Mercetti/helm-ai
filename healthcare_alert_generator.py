"""
Stellar Logic AI - Healthcare Alert Generator Module
"""

import logging
from datetime import datetime
from typing import Dict, Any
import random

logger = logging.getLogger(__name__)

class HealthcareAlertGenerator:
    """Healthcare security alert generator"""
    
    def generate_healthcare_alert(self, event_data: Dict[str, Any], analysis_result: Dict[str, Any], 
                                security_thresholds: Dict[str, float]):
        """Generate healthcare security alert"""
        try:
            from healthcare_ai_security_plugin import HealthcareAlert, HealthcareThreatType, HealthcareSecurityLevel
            
            threat_type = analysis_result.get('primary_threat', 'unknown')
            confidence_score = analysis_result.get('overall_risk_score', 0.0)
            
            if threat_type not in security_thresholds:
                return None
            
            threshold = security_thresholds[threat_type]
            if confidence_score < threshold:
                return None
            
            # Determine security level
            if confidence_score >= 0.9:
                security_level = HealthcareSecurityLevel.CRITICAL
            elif confidence_score >= 0.7:
                security_level = HealthcareSecurityLevel.HIGH
            elif confidence_score >= 0.5:
                security_level = HealthcareSecurityLevel.MEDIUM
            else:
                security_level = HealthcareSecurityLevel.LOW
            
            # Check for HIPAA violation
            compliance_status = analysis_result.get('compliance_status', {})
            hipaa_violation = compliance_status.get('hipaa_compliance', 1.0) < 0.7
            
            # Determine if report is required
            report_required = security_level in [HealthcareSecurityLevel.HIGH, HealthcareSecurityLevel.CRITICAL]
            
            alert_id = f"HEALTH_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            
            return HealthcareAlert(
                alert_id=alert_id,
                patient_id=event_data.get('patient_id', 'unknown'),
                facility_id=event_data.get('facility_id', 'unknown'),
                department=event_data.get('department', 'unknown'),
                alert_type=HealthcareThreatType(threat_type),
                security_level=security_level,
                confidence_score=confidence_score,
                timestamp=datetime.now(),
                description=f"{threat_type.replace('_', ' ').title()} detected with {confidence_score:.1%} confidence",
                hipaa_violation=hipaa_violation,
                report_required=report_required
            )
            
        except Exception as e:
            logger.error(f"Error generating alert: {e}")
            return None
