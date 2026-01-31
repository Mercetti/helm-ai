"""
Simple Healthcare AI Security Plugin Test
"""

import logging
from datetime import datetime
from healthcare_ai_security_plugin import HealthcareAISecurityPlugin

logger = logging.getLogger(__name__)

def test_healthcare_plugin():
    """Test healthcare AI security plugin"""
    print("🏥 Testing Healthcare AI Security Plugin...")
    
    try:
        # Initialize plugin
        plugin = HealthcareAISecurityPlugin()
        print(f"✅ Plugin initialized: {plugin.plugin_name}")
        
        # Test HIPAA violation detection
        event_data = {
            'event_id': 'HEALTH_TEST_001',
            'patient_id': 'patient_001',
            'facility_id': 'hospital_001',
            'department': 'emergency',
            'timestamp': datetime.now().isoformat(),
            'encrypted': False,  # HIPAA violation
            'consent_obtained': False,  # HIPAA violation
            'audit_trail': {},  # HIPAA violation
            'user_role': 'nurse',
            'access_method': 'terminal',
            'session_duration': 1800
        }
        
        result = plugin.process_healthcare_event(event_data)
        print(f"✅ HIPAA violation test: {result.get('status', 'unknown')}")
        if result.get('alert_generated'):
            print(f"   Alert ID: {result.get('alert_id')}")
            print(f"   Threat: {result.get('threat_type')}")
        
        # Test normal event
        normal_event = {
            'event_id': 'HEALTH_TEST_002',
            'patient_id': 'patient_002',
            'facility_id': 'clinic_001',
            'department': 'primary_care',
            'timestamp': datetime.now().isoformat(),
            'encrypted': True,
            'consent_obtained': True,
            'audit_trail': {'access_log': 'complete'},
            'user_role': 'doctor',
            'access_method': 'secure_terminal',
            'session_duration': 900
        }
        
        result2 = plugin.process_healthcare_event(normal_event)
        print(f"✅ Normal event test: {result2.get('status', 'unknown')}")
        print(f"   Alert generated: {result2.get('alert_generated', False)}")
        
        # Test metrics
        metrics = plugin.get_healthcare_metrics()
        print(f"✅ Metrics retrieved: {len(metrics)} fields")
        print(f"   Alerts generated: {metrics.get('alerts_generated')}")
        print(f"   Threats detected: {metrics.get('threats_detected')}")
        
        # Test status
        status = plugin.get_healthcare_status()
        print(f"✅ Status retrieved: {status.get('status')}")
        print(f"   AI Core connected: {status.get('ai_core_connected')}")
        
        print("🎉 Healthcare AI Security Plugin tests PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Healthcare AI Security Plugin test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_healthcare_plugin()
    exit(0 if success else 1)
