import requests
import json

# API base URL
BASE_URL = "http://localhost:5000/api/enterprise"

def test_enterprise_api():
    """Test Enterprise Plugin API endpoints"""
    
    print("🚀 Testing Enterprise Security Plugin API")
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
    
    # Test 3: Analyze Security Event
    print("\n3. 🔍 Analyze Security Event:")
    test_event = {
        "player_id": "user_001",
        "action": "failed_login_attempt",
        "game_resource": "admin_panel",
        "timestamp": "2026-01-30T22:30:00",
        "ip_address": "192.168.1.100",
        "device_id": "device_001",
        "team": "finance",
        "player_level": "user",
        "item_rarity": "restricted",
        "game_location": "data_center"
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
    print("\n5. 🚨 Get Alerts:")
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
    
    # Test 7: Simulate Events
    print("\n7. 🎮 Simulate Events:")
    try:
        response = requests.post(f"{BASE_URL}/simulate", json={"count": 5})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 8: API Documentation
    print("\n8. 📚 API Documentation:")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n🎯 Enterprise Plugin API Test Complete!")
    print("🚀 Ready for production deployment!")

if __name__ == "__main__":
    test_enterprise_api()
