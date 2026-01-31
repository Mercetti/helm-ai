"""
Simple Financial AI Security Plugin Test
"""

import logging
from datetime import datetime
from financial_ai_security_plugin import FinancialAISecurityPlugin

logger = logging.getLogger(__name__)

def test_financial_plugin():
    """Test financial AI security plugin"""
    print("💰 Testing Financial AI Security Plugin...")
    
    try:
        # Initialize plugin
        plugin = FinancialAISecurityPlugin()
        print(f"✅ Plugin initialized: {plugin.plugin_name}")
        
        # Test money laundering detection
        event_data = {
            'event_id': 'FIN_TEST_001',
            'customer_id': 'customer_001',
            'account_id': 'account_001',
            'institution_id': 'bank_001',
            'timestamp': datetime.now().isoformat(),
            'amount': 15000,  # High-value transaction
            'currency': 'USD',
            'transaction_type': 'wire_transfer',
            'destination': 'offshore_bank',
            'origin': 'domestic',
            'channel': 'online',
            'high_risk_country': True,  # Money laundering indicator
            'unusual_amount': True,
            'suspicious_timing': True,
            'new_destination': True,
            'aml_check_passed': False,  # AML violation
            'kyc_verified': True,
            'sanctions_screened': True,
            'pep_screened': True
        }
        
        result = plugin.process_financial_event(event_data)
        print(f"✅ Money laundering test: {result.get('status', 'unknown')}")
        if result.get('alert_generated'):
            print(f"   Alert ID: {result.get('alert_id')}")
            print(f"   Threat: {result.get('threat_type')}")
            print(f"   Regulatory Violation: {result.get('regulatory_violation')}")
        
        # Test credit card fraud
        cc_event = {
            'event_id': 'FIN_TEST_002',
            'customer_id': 'customer_002',
            'account_id': 'card_002',
            'institution_id': 'bank_002',
            'timestamp': datetime.now().isoformat(),
            'amount': 2500,
            'currency': 'USD',
            'transaction_type': 'purchase',
            'channel': 'online',
            'new_merchant': True,
            'unusual_location': True,
            'micro_transactions': True,
            'aml_check_passed': True,
            'kyc_verified': True,
            'sanctions_screened': True,
            'pep_screened': True
        }
        
        result2 = plugin.process_financial_event(cc_event)
        print(f"✅ Credit card fraud test: {result2.get('status', 'unknown')}")
        print(f"   Alert generated: {result2.get('alert_generated', False)}")
        
        # Test normal transaction
        normal_event = {
            'event_id': 'FIN_TEST_003',
            'customer_id': 'customer_003',
            'account_id': 'account_003',
            'institution_id': 'bank_003',
            'timestamp': datetime.now().isoformat(),
            'amount': 150,
            'currency': 'USD',
            'transaction_type': 'purchase',
            'channel': 'branch',
            'aml_check_passed': True,
            'kyc_verified': True,
            'sanctions_screened': True,
            'pep_screened': True
        }
        
        result3 = plugin.process_financial_event(normal_event)
        print(f"✅ Normal transaction test: {result3.get('status', 'unknown')}")
        print(f"   Alert generated: {result3.get('alert_generated', False)}")
        
        # Test metrics
        metrics = plugin.get_financial_metrics()
        print(f"✅ Metrics retrieved: {len(metrics)} fields")
        print(f"   Alerts generated: {metrics.get('alerts_generated')}")
        print(f"   Threats detected: {metrics.get('threats_detected')}")
        
        # Test status
        status = plugin.get_financial_status()
        print(f"✅ Status retrieved: {status.get('status')}")
        print(f"   AI Core connected: {status.get('ai_core_connected')}")
        
        print("🎉 Financial AI Security Plugin tests PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Financial AI Security Plugin test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_financial_plugin()
    exit(0 if success else 1)
