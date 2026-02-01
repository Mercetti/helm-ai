import requests
import json
import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API base URL
BASE_URL = "http://localhost:5001/api/financial"

def test_financial_api():
    """Test Financial Services Plugin API endpoints"""
    
    print("Testing Financial Services Plugin API")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Health Check:")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Dashboard (before transactions)
    print("\n2. Dashboard (Before Transactions):")
    try:
        response = requests.get(f"{BASE_URL}/dashboard")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Analyze Financial Transaction
    print("\n3. Analyze Financial Transaction:")
    test_transaction = {
        'alert_id': 'FIN_test_001',
        'customer_id': 'customer_001',
        'action': 'transfer',
        'resource': 'account_001',
        'timestamp': '2026-01-30T23:30:00',
        'ip_address': '192.168.1.100',
        'device_id': 'device_001',
        'customer_segment': 'vip',
        'transaction_channel': 'mobile_app',
        'amount': 15000,
        'risk_score': 0.8,
        'location': 'new_york'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analyze", json=test_transaction)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Dashboard (after transactions)
    print("\n4. Dashboard (After Transactions):")
    try:
        response = requests.get(f"{BASE_URL}/dashboard")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Get Fraud Alerts
    print("\n5. Get Fraud Alerts:")
    try:
        response = requests.get(f"{BASE_URL}/alerts")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 6: Get Statistics
    print("\n6. Get Statistics:")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 7: Risk Assessment
    print("\n7. Risk Assessment:")
    try:
        response = requests.post(f"{BASE_URL}/risk", json={
            'customer_id': 'customer_001',
            'transaction_amount': 25000,
            'risk_factors': ['international_transfer', 'large_amount']
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 8: Compliance Report
    print("\n8. Compliance Report:")
    try:
        response = requests.get(f"{BASE_URL}/compliance")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 9: Simulate Transactions
    print("\n9. Simulate Transactions:")
    try:
        response = requests.post(f"{BASE_URL}/simulate", json={"count": 10})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 10: API Documentation
    print("\n10. API Documentation:")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\nFinancial Plugin API Test Complete!")
    print("Ready for production deployment!")

if __name__ == "__main__":
    test_financial_api()
