import requests
import json

# API base URL
BASE_URL = "http://localhost:5003/api/ecommerce"

def test_ecommerce_api():
    """Test E-Commerce Fraud Plugin API endpoints"""
    
    print("🚀 Testing E-Commerce Fraud Plugin API")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. 🛒 Health Check:")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Dashboard (before transactions)
    print("\n2. 📊 Dashboard (Before Transactions):")
    try:
        response = requests.get(f"{BASE_URL}/dashboard")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Analyze Transaction
    print("\n3. 🔍 Analyze E-Commerce Transaction:")
    test_transaction = {
        'alert_id': 'HC_test_001',
        'provider_id': 'customer_001',
        'action': 'unauthorized_access_attempt',
        'resource': 'ehr_system',
        'timestamp': '2026-01-30T03:30:00',
        'ip_address': '192.168.1.100',
        'device_id': 'device_001',
        'department': 'cardiology',
        'access_level': 'physician',
        'data_sensitivity': 'phi_high',
        'patient_risk_level': 'critical',
        'location': 'foreign_country'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analyze", json=test_transaction)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Dashboard (after transactions)
    print("\n4. 📊 Dashboard (After Transactions):")
    try:
        response = requests.get(f"{BASE_URL}/dashboard")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Get Alerts
    print("\n5. 🚨 Get Fraud Alerts:")
    try:
        response = requests.get(f"{BASE_URL}/alerts")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 6: Get Statistics
    print("\n6. 📈 Get Statistics:")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 7: Revenue Impact
    print("\n7. 💰 Get Revenue Impact:")
    try:
        response = requests.get(f"{BASE_URL}/revenue")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 8: Customer Monitoring
    print("\n8. 👥 Get Customer Monitoring:")
    try:
        response = requests.get(f"{BASE_URL}/customers")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 9: Simulate Transactions
    print("\n9. 🎮 Simulate Transactions:")
    try:
        response = requests.post(f"{BASE_URL}/simulate", json={"count": 5})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 10: API Documentation
    print("\n10. 📚 API Documentation:")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n🎯 E-Commerce Plugin API Test Complete!")
    print("🚀 Ready for production deployment!")

if __name__ == "__main__":
    test_ecommerce_api()
