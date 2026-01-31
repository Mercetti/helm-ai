"""
Stellar Logic AI - Healthcare Data Adapter Module
"""

import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class HealthcareDataAdapter:
    """Adapt healthcare data for AI processing"""
    
    def adapt_healthcare_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt healthcare data for AI core processing"""
        try:
            adapted_data = {
                'patient_info': {
                    'patient_id': raw_data.get('patient_id', ''),
                    'age': raw_data.get('age', 0),
                    'gender': raw_data.get('gender', ''),
                    'medical_history': raw_data.get('medical_history', {}),
                    'medications': raw_data.get('medications', []),
                    'allergies': raw_data.get('allergies', [])
                },
                'facility_info': {
                    'facility_id': raw_data.get('facility_id', ''),
                    'department': raw_data.get('department', ''),
                    'location': raw_data.get('location', ''),
                    'staff_level': raw_data.get('staff_level', ''),
                    'accreditation': raw_data.get('accreditation', '')
                },
                'medical_data': {
                    'diagnosis': raw_data.get('diagnosis', ''),
                    'treatment': raw_data.get('treatment', ''),
                    'procedures': raw_data.get('procedures', []),
                    'medications_prescribed': raw_data.get('medications_prescribed', []),
                    'lab_results': raw_data.get('lab_results', {}),
                    'vital_signs': raw_data.get('vital_signs', {})
                },
                'access_patterns': {
                    'access_time': raw_data.get('timestamp', datetime.now().isoformat()),
                    'access_method': raw_data.get('access_method', ''),
                    'user_role': raw_data.get('user_role', ''),
                    'session_duration': raw_data.get('session_duration', 0),
                    'data_accessed': raw_data.get('data_accessed', [])
                },
                'compliance_data': {
                    'hipaa_required_fields': self._check_hipaa_compliance(raw_data),
                    'data_encryption': raw_data.get('encrypted', False),
                    'audit_trail': raw_data.get('audit_trail', {}),
                    'consent_obtained': raw_data.get('consent_obtained', False)
                },
                'risk_indicators': {
                    'unusual_access_patterns': self._detect_unusual_patterns(raw_data),
                    'data_volume_anomaly': self._detect_data_volume_anomaly(raw_data),
                    'time_based_anomaly': self._detect_time_anomaly(raw_data),
                    'location_anomaly': self._detect_location_anomaly(raw_data)
                }
            }
            
            return adapted_data
            
        except Exception as e:
            logger.error(f"Error adapting healthcare data: {e}")
            return {}
    
    def _check_hipaa_compliance(self, data: Dict[str, Any]) -> Dict[str, bool]:
        """Check HIPAA compliance requirements"""
        return {
            'patient_id_present': bool(data.get('patient_id')),
            'access_log_maintained': bool(data.get('audit_trail')),
            'minimum_necessary': self._check_minimum_necessary(data),
            'consent_documented': bool(data.get('consent_obtained')),
            'encryption_enabled': bool(data.get('encrypted', False))
        }
    
    def _check_minimum_necessary(self, data: Dict[str, Any]) -> bool:
        """Check if only minimum necessary data is collected"""
        sensitive_fields = ['ssn', 'credit_card', 'full_address']
        return not any(field in str(data).lower() for field in sensitive_fields)
    
    def _detect_unusual_patterns(self, data: Dict[str, Any]) -> bool:
        """Detect unusual access patterns"""
        access_time = data.get('timestamp', '')
        if access_time:
            try:
                dt = datetime.fromisoformat(access_time.replace('Z', '+00:00'))
                hour = dt.hour
                # Unusual access during late hours (11 PM - 6 AM)
                if hour >= 23 or hour <= 6:
                    return True
            except:
                pass
        return False
    
    def _detect_data_volume_anomaly(self, data: Dict[str, Any]) -> bool:
        """Detect data volume anomalies"""
        data_accessed = data.get('data_accessed', [])
        return len(data_accessed) > 50  # Threshold for unusual volume
    
    def _detect_time_anomaly(self, data: Dict[str, Any]) -> bool:
        """Detect time-based anomalies"""
        session_duration = data.get('session_duration', 0)
        return session_duration > 3600  # 1 hour threshold
    
    def _detect_location_anomaly(self, data: Dict[str, Any]) -> bool:
        """Detect location-based anomalies"""
        location = data.get('location', '').lower()
        unusual_locations = ['public_wifi', 'coffee_shop', 'airport']
        return any(loc in location for loc in unusual_locations)
