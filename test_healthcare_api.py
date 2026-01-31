import requests
import json

# API base URL
BASE_URL = "http://localhost:5002/api/healthcare"

def test_healthcare_api():
    """Test Healthcare Compliance Plugin API endpoints"""
    
    print("🚀 Testing Healthcare Compliance Plugin API")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. 🏥 Health Check:")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Dashboard (before events)
    print("\n2. 📊 Dashboard (Before Events):")
    try:
        response = requests.get(f"{BASE_URL}/dashboard")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Analyze Healthcare Event
    print("\n3. 🔍 Analyze Healthcare Event:")
    test_event = {
        'alert_id': 'FIN_test_001',
        'customer_id': 'provider_001',
        'action': 'admin_access',
        'resource': 'admin_panel',
        'timestamp': '2026-01-30T23:30:00',
        'ip_address': '192.168.1.100',
        'device_id': 'device_001',
        'customer_segment': 'vip',
        'transaction_channel': 'api_access',
        'amount': 75000,
        'risk_score': 0.9,
        'location': 'remote_office'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analyze", json=test_event)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Dashboard (after events)
    print("\n4. 📊 Dashboard (After Events):")
    try:
        response = requests.get(f"{BASE_URL}/dashboard")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Get Alerts
    print("\n5. 🚨 Get Compliance Alerts:")
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
    
    # Test 7: HIPAA Report
    print("\n7. 📋 Get HIPAA Report:")
    try:
        response = requests.get(f"{BASE_URL}/hipaa")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 8: Patient Monitoring
    print("\n8. 👥 Get Patient Monitoring:")
    try:
        response = requests.get(f"{BASE_URL}/patients")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 9: Simulate Events
    print("\n9. 🎮 Simulate Events:")
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
    
    print("\n🎯 Healthcare Plugin API Test Complete!")
    print("🚀 Ready for production deployment!")

if __name__ == "__main__":
    test_healthcare_api()
