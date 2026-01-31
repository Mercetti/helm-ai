"""
🧪 MANUFACTURING API TEST SUITE
Stellar Logic AI - Manufacturing Security API Testing

Comprehensive testing for manufacturing security, predictive maintenance,
quality control, and supply chain integrity monitoring endpoints.
"""

import requests
import json
import time
import logging
from datetime import datetime
import random
import statistics

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
        logger.info("Starting Manufacturing API Test Suite")
        print("🧪 Manufacturing API Test Suite")
        print("=" * 60)
        
        # Test endpoints
        self.test_health_check()
        self.test_manufacturing_analysis()
        self.test_dashboard_data()
        self.test_alerts_endpoint()
        self.test_maintenance_status()
        self.test_quality_metrics()
        self.test_security_status()
        self.test_performance_metrics()
        self.test_facilities_endpoint()
        self.test_statistics_endpoint()
        
        # Generate summary
        self.generate_test_summary()
        
    def test_health_check(self):
        """Test health check endpoint"""
        logger.info("Testing health check endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                self.test_results.append({
                    'test': 'Health Check',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Status: {data.get('status')}, AI Core: {data.get('ai_core_status', {}).get('ai_core_connected')}"
                })
                print(f"✅ Health Check: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Health Check',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Health Check: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Health Check',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Health Check: ERROR ({str(e)})")
    
    def test_manufacturing_analysis(self):
        """Test manufacturing event analysis endpoint"""
        logger.info("Testing manufacturing analysis endpoint")
        
        test_events = [
            {
                'sensor_id': 'TEMP_001',
                'equipment_id': 'EQ_1234',
                'facility_id': 'FAC_001',
                'sensor_type': 'temperature',
                'sensor_value': 85.5,
                'sensor_unit': 'celsius',
                'location': 'production_line_3',
                'production_line': 'line_3',
                'shift': 'day',
                'operator_id': 'OP_001',
                'batch_id': 'BATCH_001',
                'quality_metrics': {
                    'dimensional_accuracy': 0.95,
                    'surface_finish': 0.92,
                    'material_composition': 0.94
                },
                'maintenance_data': {
                    'last_maintenance': '2024-01-15',
                    'maintenance_hours': 500
                },
                'security_context': {
                    'access_attempts': 10,
                    'failed_attempts': 1,
                    'unauthorized_access': 0
                },
                'performance_indicators': {
                    'efficiency': 0.88,
                    'output_rate': 150
                }
            },
            {
                'sensor_id': 'VIB_002',
                'equipment_id': 'EQ_5678',
                'facility_id': 'FAC_002',
                'sensor_type': 'vibration',
                'sensor_value': 12.3,
                'sensor_unit': 'mm/s',
                'location': 'production_line_1',
                'production_line': 'line_1',
                'shift': 'night',
                'operator_id': 'OP_002',
                'batch_id': 'BATCH_002',
                'quality_metrics': {
                    'dimensional_accuracy': 0.88,
                    'surface_finish': 0.85,
                    'material_composition': 0.90
                },
                'maintenance_data': {
                    'last_maintenance': '2024-01-10',
                    'maintenance_hours': 800
                },
                'security_context': {
                    'access_attempts': 5,
                    'failed_attempts': 2,
                    'unauthorized_access': 1
                },
                'performance_indicators': {
                    'efficiency': 0.75,
                    'output_rate': 120
                }
            }
        ]
        
        for i, event in enumerate(test_events):
            try:
                start_time = time.time()
                response = requests.post(f"{self.base_url}/api/manufacturing/analyze", json=event)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    self.test_results.append({
                        'test': f'Manufacturing Analysis {i+1}',
                        'status': 'PASS',
                        'response_time': response_time,
                        'details': f"Status: {data.get('status')}, Confidence: {data.get('alert', {}).get('confidence_score', 'N/A')}"
                    })
                    print(f"✅ Manufacturing Analysis {i+1}: PASS ({response_time:.2f}ms)")
                else:
                    self.test_results.append({
                        'test': f'Manufacturing Analysis {i+1}',
                        'status': 'FAIL',
                        'response_time': response_time,
                        'details': f"Status Code: {response.status_code}"
                    })
                    print(f"❌ Manufacturing Analysis {i+1}: FAIL ({response.status_code})")
                    
            except Exception as e:
                self.test_results.append({
                    'test': f'Manufacturing Analysis {i+1}',
                    'status': 'ERROR',
                    'response_time': 0,
                    'details': str(e)
                })
                print(f"❌ Manufacturing Analysis {i+1}: ERROR ({str(e)})")
    
    def test_dashboard_data(self):
        """Test dashboard data endpoint"""
        logger.info("Testing dashboard data endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/manufacturing/dashboard")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('metrics', {})
                self.test_results.append({
                    'test': 'Dashboard Data',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Equipment: {metrics.get('equipment_monitored')}, Quality: {metrics.get('quality_score')}%"
                })
                print(f"✅ Dashboard Data: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Dashboard Data',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Dashboard Data: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Dashboard Data',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Dashboard Data: ERROR ({str(e)})")
    
    def test_alerts_endpoint(self):
        """Test alerts endpoint"""
        logger.info("Testing alerts endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/manufacturing/alerts?limit=10")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                alerts = data.get('alerts', [])
                self.test_results.append({
                    'test': 'Alerts Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Alerts Count: {len(alerts)}, Total: {data.get('total_count')}"
                })
                print(f"✅ Alerts Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Alerts Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Alerts Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Alerts Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Alerts Endpoint: ERROR ({str(e)})")
    
    def test_maintenance_status(self):
        """Test maintenance status endpoint"""
        logger.info("Testing maintenance status endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/manufacturing/maintenance")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                predictions = data.get('maintenance_predictions', [])
                self.test_results.append({
                    'test': 'Maintenance Status',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Predictions: {len(predictions)}, Critical: {data.get('critical_maintenance')}"
                })
                print(f"✅ Maintenance Status: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Maintenance Status',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Maintenance Status: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Maintenance Status',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Maintenance Status: ERROR ({str(e)})")
    
    def test_quality_metrics(self):
        """Test quality metrics endpoint"""
        logger.info("Testing quality metrics endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/manufacturing/quality")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                quality_score = data.get('overall_quality_score')
                defect_rate = data.get('defect_rate')
                self.test_results.append({
                    'test': 'Quality Metrics',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Quality Score: {quality_score}%, Defect Rate: {defect_rate}%"
                })
                print(f"✅ Quality Metrics: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Quality Metrics',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Quality Metrics: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Quality Metrics',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Quality Metrics: ERROR ({str(e)})")
    
    def test_security_status(self):
        """Test security status endpoint"""
        logger.info("Testing security status endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/manufacturing/security")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                security_score = data.get('overall_security_score')
                events_today = data.get('security_events_today')
                self.test_results.append({
                    'test': 'Security Status',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Security Score: {security_score}%, Events Today: {events_today}"
                })
                print(f"✅ Security Status: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Security Status',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Security Status: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Security Status',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Security Status: ERROR ({str(e)})")
    
    def test_performance_metrics(self):
        """Test performance metrics endpoint"""
        logger.info("Testing performance metrics endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/manufacturing/performance")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                response_time_metric = data.get('response_time')
                accuracy = data.get('accuracy')
                self.test_results.append({
                    'test': 'Performance Metrics',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Response Time: {response_time_metric}ms, Accuracy: {accuracy}%"
                })
                print(f"✅ Performance Metrics: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Performance Metrics',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Performance Metrics: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Performance Metrics',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Performance Metrics: ERROR ({str(e)})")
    
    def test_facilities_endpoint(self):
        """Test facilities endpoint"""
        logger.info("Testing facilities endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/manufacturing/facilities")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                facilities = data.get('facilities', [])
                self.test_results.append({
                    'test': 'Facilities Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Facilities: {len(facilities)}, Operational: {data.get('operational_facilities')}"
                })
                print(f"✅ Facilities Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Facilities Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Facilities Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Facilities Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Facilities Endpoint: ERROR ({str(e)})")
    
    def test_statistics_endpoint(self):
        """Test statistics endpoint"""
        logger.info("Testing statistics endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/manufacturing/stats")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                overview = data.get('overview', {})
                performance = data.get('performance', {})
                self.test_results.append({
                    'test': 'Statistics Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Events: {overview.get('total_events_processed')}, Response Time: {performance.get('average_response_time')}ms"
                })
                print(f"✅ Statistics Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Statistics Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Statistics Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Statistics Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Statistics Endpoint: ERROR ({str(e)})")
    
    def generate_test_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.test_results if r['status'] == 'ERROR'])
        
        response_times = [r['response_time'] for r in self.test_results if r['response_time'] > 0]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"💥 Errors: {error_tests}")
        print(f"Success Rate: {(passed_tests / total_tests * 100):.1f}%")
        print(f"Average Response Time: {avg_response_time:.2f}ms")
        print(f"Min Response Time: {min_response_time:.2f}ms")
        print(f"Max Response Time: {max_response_time:.2f}ms")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "💥"
            print(f"{status_icon} {result['test']}: {result['status']} ({result['response_time']:.2f}ms)")
            print(f"   Details: {result['details']}")
        
        print("\n🎯 PERFORMANCE ANALYSIS:")
        if avg_response_time < 100:
            print("✅ EXCELLENT - Average response time under 100ms")
        elif avg_response_time < 200:
            print("✅ GOOD - Average response time under 200ms")
        else:
            print("⚠️ NEEDS IMPROVEMENT - Average response time above 200ms")
        
        if passed_tests / total_tests >= 0.95:
            print("✅ EXCELLENT - Success rate above 95%")
        elif passed_tests / total_tests >= 0.85:
            print("✅ GOOD - Success rate above 85%")
        else:
            print("⚠️ NEEDS IMPROVEMENT - Success rate below 85%")
        
        print("\n🚀 Manufacturing API Test Complete!")

if __name__ == "__main__":
    # Run the test suite
    test_suite = ManufacturingAPITestSuite()
    test_suite.run_all_tests()
