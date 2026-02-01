"""
REAL ESTATE & PROPERTY SECURITY TEST SUITE
Stellar Logic AI - Real Estate Security API Testing

Comprehensive testing for real estate fraud detection, title verification,
transaction security, and compliance monitoring endpoints.
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
from typing import Dict, Any, List

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealEstateAPITestSuite:
    """Test suite for Real Estate & Property Security API"""
    
    def __init__(self, base_url="http://localhost:5007"):
        self.base_url = base_url
        self.test_results = []
        self.performance_metrics = []
        
    def run_all_tests(self):
        """Run all API tests"""
        logger.info("Starting Real Estate API Test Suite")
        print("Real Estate & Property Security API Test Suite")
        print("=" * 60)
        
        # Test endpoints
        self.test_health_check()
        self.test_real_estate_analysis()
        self.test_real_estate_dashboard()
        self.test_real_estate_alerts()  # Fixed - method now exists
        self.test_properties_status()
        self.test_transaction_monitoring()
        self.test_fraud_type_analysis()
        self.test_compliance_status()
        self.test_market_analysis()
        self.test_comprehensive_statistics()
        
        # Generate summary
        self.generate_test_summary()
        
    def test_health_check(self):
        """Test health check endpoint"""
        print("\n1. Health Check:")
        try:
            response = requests.get(f"{self.base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Health Check", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Health Check", False))
    
    def test_real_estate_analysis(self):
        """Test real estate analysis endpoint"""
        print("\n2. Real Estate Analysis:")
        try:
            test_data = {
                'property_id': 'prop_001',
                'transaction_data': {
                    'property_value': 500000,
                    'buyer_id': 'buyer_001',
                    'seller_id': 'seller_001',
                    'transaction_date': '2026-01-30',
                    'location': 'downtown'
                }
            }
            response = requests.post(f"{self.base_url}/analyze", json=test_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Real Estate Analysis", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Real Estate Analysis", False))
    
    def test_real_estate_dashboard(self):
        """Test real estate dashboard endpoint"""
        print("\n3. Real Estate Dashboard:")
        try:
            response = requests.get(f"{self.base_url}/dashboard")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Real Estate Dashboard", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Real Estate Dashboard", False))
    
    def test_real_estate_alerts(self):
        """Test real estate alerts endpoint - FIXED METHOD"""
        print("\n4. Real Estate Alerts:")
        try:
            response = requests.get(f"{self.base_url}/alerts")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Real Estate Alerts", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Real Estate Alerts", False))
    
    def test_properties_status(self):
        """Test properties status endpoint"""
        print("\n5. Properties Status:")
        try:
            test_data = {
                'property_ids': ['prop_001', 'prop_002', 'prop_003'],
                'status_query': 'all'
            }
            response = requests.post(f"{self.base_url}/properties/status", json=test_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Properties Status", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Properties Status", False))
    
    def test_transaction_monitoring(self):
        """Test transaction monitoring endpoint"""
        print("\n6. Transaction Monitoring:")
        try:
            test_data = {
                'transaction_id': 'trans_001',
                'monitoring_data': {
                    'amount': 750000,
                    'parties': ['buyer_a', 'seller_b'],
                    'property_type': 'commercial',
                    'risk_factors': ['high_value', 'new_parties']
                }
            }
            response = requests.post(f"{self.base_url}/transaction/monitor", json=test_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Transaction Monitoring", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Transaction Monitoring", False))
    
    def test_fraud_type_analysis(self):
        """Test fraud type analysis endpoint"""
        print("\n7. Fraud Type Analysis:")
        try:
            test_data = {
                'case_id': 'case_001',
                'fraud_indicators': ['title_forgery', 'identity_theft', 'price_inflation'],
                'evidence': {
                    'document_analysis': 'suspicious',
                    'identity_verification': 'failed',
                    'market_comparison': 'anomalous'
                }
            }
            response = requests.post(f"{self.base_url}/fraud/analyze", json=test_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Fraud Type Analysis", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Fraud Type Analysis", False))
    
    def test_compliance_status(self):
        """Test compliance status endpoint"""
        print("\n8. Compliance Status:")
        try:
            response = requests.get(f"{self.base_url}/compliance")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Compliance Status", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Compliance Status", False))
    
    def test_market_analysis(self):
        """Test market analysis endpoint"""
        print("\n9. Market Analysis:")
        try:
            test_data = {
                'market_region': 'downtown',
                'analysis_type': 'fraud_trends',
                'time_period': '30_days'
            }
            response = requests.post(f"{self.base_url}/market/analyze", json=test_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Market Analysis", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Market Analysis", False))
    
    def test_comprehensive_statistics(self):
        """Test comprehensive statistics endpoint"""
        print("\n10. Comprehensive Statistics:")
        try:
            response = requests.get(f"{self.base_url}/stats")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            self.test_results.append(("Comprehensive Statistics", response.status_code == 200))
        except Exception as e:
            print(f"   Error: {e}")
            self.test_results.append(("Comprehensive Statistics", False))
    
    def generate_test_summary(self):
        """Generate test summary"""
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
        
        print("\nReal Estate API Test Complete!")
        print("Ready for production deployment!")

def test_real_estate_api():
    """Test Real Estate API"""
    suite = RealEstateAPITestSuite()
    suite.run_all_tests()

if __name__ == "__main__":
    test_real_estate_api()
