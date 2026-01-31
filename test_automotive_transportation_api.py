"""
🧪 AUTOMOTIVE & TRANSPORTATION API TEST SUITE
Stellar Logic AI - Automotive Security API Testing

Comprehensive testing for autonomous vehicle security, fleet management,
supply chain logistics, and smart transportation systems endpoints.
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

class AutomotiveTransportationAPITestSuite:
    """Test suite for Automotive & Transportation Security API"""
    
    def __init__(self, base_url="http://localhost:5006"):
        self.base_url = base_url
        self.test_results = []
        self.performance_metrics = []
        
    def run_all_tests(self):
        """Run all API tests"""
        logger.info("Starting Automotive & Transportation API Test Suite")
        print("🧪 Automotive & Transportation API Test Suite")
        print("=" * 60)
        
        # Test endpoints
        self.test_health_check()
        self.test_automotive_analysis()
        self.test_dashboard_data()
        self.test_alerts_endpoint()
        self.test_autonomous_systems()
        self.test_fleet_management()
        self.test_supply_chain()
        self.test_smart_transportation()
        self.test_vehicles_endpoint()
        self.test_routes_endpoint()
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
    
    def test_automotive_analysis(self):
        """Test automotive analysis endpoint"""
        logger.info("Testing automotive analysis endpoint")
        
        test_events = [
            {
                'event_id': 'AUTO_001',
                'vehicle_id': 'VEH_001',
                'fleet_id': 'FLEET_001',
                'vehicle_type': 'autonomous',
                'transportation_mode': 'road',
                'sensor_data': {
                    'lidar_data': [random.random() for _ in range(100)],
                    'camera_data': [random.random() for _ in range(50)],
                    'radar_data': [random.random() for _ in range(75)],
                    'gps_data': {'latitude': 40.7128, 'longitude': -74.0060},
                    'imu_data': {'acceleration': [0.1, 0.2, 0.3], 'gyroscope': [0.01, 0.02, 0.03]},
                    'can_bus_data': {'speed': 65.5, 'rpm': 2500, 'fuel_level': 0.75}
                },
                'vehicle_status': {
                    'engine_status': 'normal',
                    'battery_level': 0.85,
                    'tire_pressure': 'normal',
                    'brake_system': 'operational'
                },
                'environmental_conditions': {
                    'weather': 'clear',
                    'temperature': 72.5,
                    'visibility': 'good',
                    'road_conditions': 'dry'
                },
                'communication_data': {
                    'v2v_active': True,
                    'v2i_active': True,
                    'encryption_status': 'active'
                },
                'autonomous_system_status': {
                    'autonomy_level': 4,
                    'system_health': 'optimal',
                    'sensor_fusion_active': True,
                    'path_planning_active': True
                },
                'location': {
                    'latitude': 40.7128,
                    'longitude': -74.0060,
                    'altitude': 10.5
                }
            },
            {
                'event_id': 'AUTO_002',
                'vehicle_id': 'VEH_002',
                'fleet_id': 'FLEET_002',
                'vehicle_type': 'electric',
                'transportation_mode': 'road',
                'sensor_data': {
                    'lidar_data': [random.random() for _ in range(80)],
                    'camera_data': [random.random() for _ in range(40)],
                    'radar_data': [random.random() for _ in range(60)],
                    'gps_data': {'latitude': 34.0522, 'longitude': -118.2437},
                    'imu_data': {'acceleration': [0.05, 0.15, 0.25], 'gyroscope': [0.005, 0.015, 0.025]},
                    'can_bus_data': {'speed': 55.2, 'rpm': 1800, 'battery_level': 0.65}
                },
                'vehicle_status': {
                    'engine_status': 'electric_motor_normal',
                    'battery_level': 0.65,
                    'tire_pressure': 'normal',
                    'brake_system': 'operational'
                },
                'environmental_conditions': {
                    'weather': 'cloudy',
                    'temperature': 68.3,
                    'visibility': 'good',
                    'road_conditions': 'dry'
                },
                'communication_data': {
                    'v2v_active': True,
                    'v2i_active': False,
                    'encryption_status': 'active'
                },
                'autonomous_system_status': {
                    'autonomy_level': 2,
                    'system_health': 'good',
                    'sensor_fusion_active': True,
                    'path_planning_active': False
                },
                'location': {
                    'latitude': 34.0522,
                    'longitude': -118.2437,
                    'altitude': 85.0
                }
            }
        ]
        
        for i, event in enumerate(test_events):
            try:
                start_time = time.time()
                response = requests.post(f"{self.base_url}/api/automotive/analyze", json=event)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    self.test_results.append({
                        'test': f'Automotive Analysis {i+1}',
                        'status': 'PASS',
                        'response_time': response_time,
                        'details': f"Status: {data.get('status')}, Security Level: {data.get('alert', {}).get('security_level', 'N/A')}"
                    })
                    print(f"✅ Automotive Analysis {i+1}: PASS ({response_time:.2f}ms)")
                else:
                    self.test_results.append({
                        'test': f'Automotive Analysis {i+1}',
                        'status': 'FAIL',
                        'response_time': response_time,
                        'details': f"Status Code: {response.status_code}"
                    })
                    print(f"❌ Automotive Analysis {i+1}: FAIL ({response.status_code})")
                    
            except Exception as e:
                self.test_results.append({
                    'test': f'Automotive Analysis {i+1}',
                    'status': 'ERROR',
                    'response_time': 0,
                    'details': str(e)
                })
                print(f"❌ Automotive Analysis {i+1}: ERROR ({str(e)})")
    
    def test_dashboard_data(self):
        """Test dashboard data endpoint"""
        logger.info("Testing dashboard data endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/automotive/dashboard")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('metrics', {})
                self.test_results.append({
                    'test': 'Dashboard Data',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Vehicles: {metrics.get('vehicles_monitored')}, Security Score: {metrics.get('security_score')}%"
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
            response = requests.get(f"{self.base_url}/api/automotive/alerts?limit=10")
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
    
    def test_autonomous_systems(self):
        """Test autonomous systems endpoint"""
        logger.info("Testing autonomous systems endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/automotive/autonomous-systems")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                security_level = data.get('overall_security_level')
                security_score = data.get('autonomous_security_score')
                self.test_results.append({
                    'test': 'Autonomous Systems',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Security Level: {security_level}, Score: {security_score}"
                })
                print(f"✅ Autonomous Systems: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Autonomous Systems',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Autonomous Systems: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Autonomous Systems',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Autonomous Systems: ERROR ({str(e)})")
    
    def test_fleet_management(self):
        """Test fleet management endpoint"""
        logger.info("Testing fleet management endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/automotive/fleet-management")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                fleet_status = data.get('overall_fleet_status')
                fleet_score = data.get('fleet_security_score')
                self.test_results.append({
                    'test': 'Fleet Management',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Fleet Status: {fleet_status}, Score: {fleet_score}"
                })
                print(f"✅ Fleet Management: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Fleet Management',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Fleet Management: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Fleet Management',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Fleet Management: ERROR ({str(e)})")
    
    def test_supply_chain(self):
        """Test supply chain endpoint"""
        logger.info("Testing supply chain endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/automotive/supply-chain")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                supply_chain_status = data.get('overall_supply_chain_status')
                supply_chain_score = data.get('supply_chain_security_score')
                self.test_results.append({
                    'test': 'Supply Chain',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Supply Chain Status: {supply_chain_status}, Score: {supply_chain_score}"
                })
                print(f"✅ Supply Chain: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Supply Chain',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Supply Chain: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Supply Chain',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Supply Chain: ERROR ({str(e)})")
    
    def test_smart_transportation(self):
        """Test smart transportation endpoint"""
        logger.info("Testing smart transportation endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/automotive/smart-transportation")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                transport_status = data.get('overall_smart_transport_status')
                transport_score = data.get('smart_transport_security_score')
                self.test_results.append({
                    'test': 'Smart Transportation',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Transport Status: {transport_status}, Score: {transport_score}"
                })
                print(f"✅ Smart Transportation: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Smart Transportation',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Smart Transportation: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Smart Transportation',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Smart Transportation: ERROR ({str(e)})")
    
    def test_vehicles_endpoint(self):
        """Test vehicles endpoint"""
        logger.info("Testing vehicles endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/automotive/vehicles")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                vehicles = data.get('vehicles', [])
                self.test_results.append({
                    'test': 'Vehicles Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Vehicles: {len(vehicles)}, Active: {data.get('active_vehicles')}"
                })
                print(f"✅ Vehicles Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Vehicles Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Vehicles Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Vehicles Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Vehicles Endpoint: ERROR ({str(e)})")
    
    def test_routes_endpoint(self):
        """Test routes endpoint"""
        logger.info("Testing routes endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/automotive/routes")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                routes = data.get('routes', [])
                self.test_results.append({
                    'test': 'Routes Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Routes: {len(routes)}, Active: {data.get('active_routes')}"
                })
                print(f"✅ Routes Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Routes Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Routes Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Routes Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Routes Endpoint: ERROR ({str(e)})")
    
    def test_statistics_endpoint(self):
        """Test statistics endpoint"""
        logger.info("Testing statistics endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/automotive/stats")
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
                    'details': f"Vehicles: {overview.get('vehicles_monitored')}, Response Time: {performance.get('average_response_time')}ms"
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
        
        print("\n🚀 Automotive & Transportation API Test Complete!")

if __name__ == "__main__":
    # Run the test suite
    test_suite = AutomotiveTransportationAPITestSuite()
    test_suite.run_all_tests()
