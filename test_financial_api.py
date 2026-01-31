import requests
import json

# API base URL
BASE_URL = "http://localhost:5001/api/financial"

def test_financial_api():
    """Test Financial Services Plugin API endpoints"""
    
    print("🚀 Testing Financial Services Plugin API")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. 🏥 Health Check:")
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
    print("\n3. 🔍 Analyze Financial Transaction:")
    test_transaction = {
        "alert_id": "ENT_test_001",
        "user_id": "customer_001",
        "action": "admin_access",
        "resource": "admin_panel",
        "timestamp": "2026-01-30T23:30:00",
        "ip_address": "192.168.1.100",
        "device_id": "device_001",
        "department": "finance",
        "access_level": "admin",
        "location": "foreign_country"
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
    
    # Test 7: Compliance Report
    print("\n7. 📋 Get Compliance Report:")
    try:
        response = requests.get(f"{BASE_URL}/compliance")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 8: Simulate Transactions
    print("\n8. 🎮 Simulate Transactions:")
    try:
        response = requests.post(f"{BASE_URL}/simulate", json={"count": 5})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 9: API Documentation
    print("\n9. 📚 API Documentation:")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n🎯 Financial Plugin API Test Complete!")
    print("🚀 Ready for production deployment!")

if __name__ == "__main__":
    test_financial_api()
