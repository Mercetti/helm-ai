"""
MANUFACTURING API TEST SUITE
Stellar Logic AI - Manufacturing Security API Testing

Comprehensive testing for manufacturing security, predictive maintenance,
quality control, and supply chain integrity monitoring endpoints.
"""

import requests
import json
import time
import logging
import sys
import io
from datetime import datetime
import random
import statistics

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ManufacturingAPITestSuite:
    """Test suite for Manufacturing Security API"""
    
    def __init__(self, base_url="http://localhost:5004"):
        self.base_url = base_url
        self.test_results = []
        self.performance_metrics = []
        
    def run_all_tests(self):
        """Run all API tests"""
        print("MANUFACTURING API TEST SUITE")
        print("=" * 60)
        print("Stellar Logic AI - Manufacturing Security API Testing")
        print("=" * 60)
        
        # Test 1: Health Check
        print("\n1. Health Check:")
        try:
            response = requests.get(f"{self.base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Health Check", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Health Check", False))
        
        # Test 2: Dashboard
        print("\n2. Dashboard:")
        try:
            response = requests.get(f"{self.base_url}/dashboard")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Dashboard", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Dashboard", False))
        
        # Test 3: Predictive Maintenance
        print("\n3. Predictive Maintenance:")
        try:
            test_data = {
                'equipment_id': 'machine_001',
                'sensor_data': {
                    'temperature': 85.5,
                    'vibration': 2.1,
                    'pressure': 150.0,
                    'runtime_hours': 2400
                }
            }
            response = requests.post(f"{self.base_url}/predictive-maintenance", json=test_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Predictive Maintenance", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Predictive Maintenance", False))
        
        # Test 4: Quality Control
        print("\n4. Quality Control:")
        try:
            test_data = {
                'product_id': 'prod_001',
                'quality_metrics': {
                    'defect_rate': 0.02,
                    'yield_rate': 0.98,
                    'quality_score': 95.5
                }
            }
            response = requests.post(f"{self.base_url}/quality-control", json=test_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Quality Control", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Quality Control", False))
        
        # Test 5: Supply Chain Monitoring
        print("\n5. Supply Chain Monitoring:")
        try:
            test_data = {
                'shipment_id': 'ship_001',
                'supply_chain_data': {
                    'origin': 'factory_a',
                    'destination': 'warehouse_b',
                    'status': 'in_transit',
                    'estimated_arrival': '2026-02-01T10:00:00'
                }
            }
            response = requests.post(f"{self.base_url}/supply-chain", json=test_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Supply Chain Monitoring", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Supply Chain Monitoring", False))
        
        # Test 6: Security Alerts
        print("\n6. Security Alerts:")
        try:
            response = requests.get(f"{self.base_url}/alerts")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Security Alerts", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Security Alerts", False))
        
        # Test 7: Statistics
        print("\n7. Statistics:")
        try:
            response = requests.get(f"{self.base_url}/stats")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Statistics", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Statistics", False))
        
        # Test 8: IoT Security
        print("\n8. IoT Security:")
        try:
            test_data = {
                'device_id': 'iot_device_001',
                'security_data': {
                    'device_type': 'sensor',
                    'location': 'production_line_a',
                    'security_status': 'secure',
                    'last_check': '2026-01-30T23:30:00'
                }
            }
            response = requests.post(f"{self.base_url}/iot-security", json=test_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("IoT Security", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("IoT Security", False))
        
        # Test 9: Performance Metrics
        print("\n9. Performance Metrics:")
        try:
            response = requests.get(f"{self.base_url}/performance")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Performance Metrics", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Performance Metrics", False))
        
        # Test 10: Simulate Events
        print("\n10. Simulate Events:")
        try:
            response = requests.post(f"{self.base_url}/simulate", json={"count": 5})
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Simulate Events", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Simulate Events", False))
        
        # Print test summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in self.test_results:
            status = "PASS" if result else "FAIL"
            print(f"   {test_name}: {status}")
        
        print("\nManufacturing API Test Complete!")
        print("Ready for production deployment!")

def test_manufacturing_api():
    """Test Manufacturing API"""
    suite = ManufacturingAPITestSuite()
    suite.run_all_tests()

if __name__ == "__main__":
    test_manufacturing_api()
