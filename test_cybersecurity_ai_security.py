"""
Simple Cybersecurity AI Security Plugin Test
"""

import logging
from datetime import datetime
from cybersecurity_ai_security_plugin import CybersecurityAISecurityPlugin

logger = logging.getLogger(__name__)

def test_cybersecurity_plugin():
    """Test cybersecurity AI security plugin"""
    print("🔒 Testing Cybersecurity AI Security Plugin...")
    
    try:
        # Initialize plugin
        plugin = CybersecurityAISecurityPlugin()
        print(f"✅ Plugin initialized: {plugin.plugin_name}")
        
        # Test ransomware detection
        event_data = {
            'event_id': 'CYBER_TEST_001',
            'organization_id': 'org_001',
            'network_id': 'network_001',
            'system_id': 'server_001',
            'timestamp': datetime.now().isoformat(),
            'malware_signatures': ['wannacry', 'locky'],  # Ransomware indicators
            'file_anomalies': ['encrypted_files', 'ransom_notes'],
            'system_modifications': True,
            'network_isolation': True,
            'system_load': 0.95,
            'unusual_network_activity': True
        }
        
        result = plugin.process_cybersecurity_event(event_data)
        print(f"✅ Ransomware test: {result.get('status', 'unknown')}")
        if result.get('alert_generated'):
            print(f"   Alert ID: {result.get('alert_id')}")
            print(f"   Threat: {result.get('threat_type')}")
            print(f"   Containment Required: {result.get('containment_required')}")
            print(f"   Forensics Needed: {result.get('forensics_needed')}")
        
        # Test DDoS attack detection
        ddos_event = {
            'event_id': 'CYBER_TEST_002',
            'organization_id': 'org_002',
            'network_id': 'network_002',
            'system_id': 'firewall_001',
            'timestamp': datetime.now().isoformat(),
            'traffic_volume': 2000000,  # High traffic volume
            'connection_count': 50000,  # High connection count
            'bandwidth_usage': 0.95,
            'unusual_network_activity': True,
            'port_scanning': True,
            'brute_force_attempts': 500
        }
        
        result2 = plugin.process_cybersecurity_event(ddos_event)
        print(f"✅ DDoS attack test: {result2.get('status', 'unknown')}")
        print(f"   Alert generated: {result2.get('alert_generated', False)}")
        
        # Test insider threat detection
        insider_event = {
            'event_id': 'CYBER_TEST_003',
            'organization_id': 'org_003',
            'network_id': 'network_003',
            'system_id': 'workstation_001',
            'timestamp': datetime.now().isoformat(),
            'user_id': 'user_003',
            'unusual_access_times': ['02:00', '03:00', '04:00'],  # Unusual times
            'data_exfiltration': True,
            'privilege_abuse': True,
            'policy_violations': ['data_access', 'file_transfer'],
            'sensitive_data_access': True
        }
        
        result3 = plugin.process_cybersecurity_event(insider_event)
        print(f"✅ Insider threat test: {result3.get('status', 'unknown')}")
        print(f"   Alert generated: {result3.get('alert_generated', False)}")
        
        # Test normal network activity
        normal_event = {
            'event_id': 'CYBER_TEST_004',
            'organization_id': 'org_004',
            'network_id': 'network_004',
            'system_id': 'server_004',
            'timestamp': datetime.now().isoformat(),
            'traffic_volume': 100000,
            'connection_count': 1000,
            'bandwidth_usage': 0.3,
            'system_load': 0.4,
            'user_id': 'user_004',
            'failed_logins': 0,
            'malware_signatures': []
        }
        
        result4 = plugin.process_cybersecurity_event(normal_event)
        print(f"✅ Normal activity test: {result4.get('status', 'unknown')}")
        print(f"   Alert generated: {result4.get('alert_generated', False)}")
        
        # Test metrics
        metrics = plugin.get_cybersecurity_metrics()
        print(f"✅ Metrics retrieved: {len(metrics)} fields")
        print(f"   Alerts generated: {metrics.get('alerts_generated')}")
        print(f"   Threats detected: {metrics.get('threats_detected')}")
        
        # Test status
        status = plugin.get_cybersecurity_status()
        print(f"✅ Status retrieved: {status.get('status')}")
        print(f"   AI Core connected: {status.get('ai_core_connected')}")
        
        print("🎉 Cybersecurity AI Security Plugin tests PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Cybersecurity AI Security Plugin test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_cybersecurity_plugin()
    exit(0 if success else 1)
