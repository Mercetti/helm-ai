"""
🧪 GOVERNMENT & DEFENSE API TEST SUITE
Stellar Logic AI - Government Security API Testing

Comprehensive testing for national security, cyber defense, threat intelligence,
critical infrastructure protection, and intelligence analysis endpoints.
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

class GovernmentDefenseAPITestSuite:
    """Test suite for Government & Defense Security API"""
    
    def __init__(self, base_url="http://localhost:5005"):
        self.base_url = base_url
        self.test_results = []
        self.performance_metrics = []
        
    def run_all_tests(self):
        """Run all API tests"""
        logger.info("Starting Government & Defense API Test Suite")
        print("🧪 Government & Defense API Test Suite")
        print("=" * 60)
        
        # Test endpoints
        self.test_health_check()
        self.test_intelligence_analysis()
        self.test_dashboard_data()
        self.test_alerts_endpoint()
        self.test_threat_intelligence()
        self.test_cyber_threats()
        self.test_physical_security()
        self.test_intelligence_analysis_endpoint()
        self.test_agencies_endpoint()
        self.test_critical_infrastructure()
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
    
    def test_intelligence_analysis(self):
        """Test intelligence analysis endpoint"""
        logger.info("Testing intelligence analysis endpoint")
        
        test_events = [
            {
                'intelligence_id': 'INTEL_001',
                'agency_id': 'AGENCY_001',
                'facility_id': 'FAC_001',
                'intelligence_type': 'threat_intelligence',
                'source_classification': 'secret',
                'threat_indicators': {
                    'threat_level': 'high',
                    'target_assets': ['critical_infrastructure', 'government_networks'],
                    'attack_vectors': ['cyber_attack', 'physical_breach']
                },
                'cyber_threat_data': {
                    'attack_patterns': ['apt_activity', 'malware_deployment'],
                    'target_systems': ['government_networks', 'military_systems']
                },
                'physical_security_data': {
                    'perimeter_status': 'secure',
                    'access_control': 'active',
                    'surveillance_coverage': 0.95
                },
                'intelligence_sources': ['human_intelligence', 'signals_intelligence'],
                'geographic_location': {
                    'region': 'north_america',
                    'country': 'united_states',
                    'specific_location': 'washington_dc'
                },
                'threat_actors': ['state_sponsored', 'proxy_groups'],
                'national_security_context': {
                    'threat_level': 'elevated',
                    'strategic_importance': 'high'
                }
            },
            {
                'intelligence_id': 'INTEL_002',
                'agency_id': 'AGENCY_002',
                'facility_id': 'FAC_002',
                'intelligence_type': 'cyber_threat',
                'source_classification': 'top_secret',
                'threat_indicators': {
                    'threat_level': 'critical',
                    'target_assets': ['defense_networks', 'classified_systems'],
                    'attack_vectors': ['zero_day_exploit', 'supply_chain_attack']
                },
                'cyber_threat_data': {
                    'attack_patterns': ['zero_day_exploit', 'advanced_persistent_threat'],
                    'target_systems': ['defense_networks', 'classified_systems']
                },
                'physical_security_data': {
                    'perimeter_status': 'enhanced',
                    'access_control': 'restricted',
                    'surveillance_coverage': 0.98
                },
                'intelligence_sources': ['signals_intelligence', 'cyber_intelligence'],
                'geographic_location': {
                    'region': 'europe',
                    'country': 'germany',
                    'specific_location': 'military_base'
                },
                'threat_actors': ['nation_state', 'apt_groups'],
                'national_security_context': {
                    'threat_level': 'critical',
                    'strategic_importance': 'critical'
                }
            }
        ]
        
        for i, event in enumerate(test_events):
            try:
                start_time = time.time()
                response = requests.post(f"{self.base_url}/api/government/analyze", json=event)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    self.test_results.append({
                        'test': f'Intelligence Analysis {i+1}',
                        'status': 'PASS',
                        'response_time': response_time,
                        'details': f"Status: {data.get('status')}, Threat Level: {data.get('alert', {}).get('threat_level', 'N/A')}"
                    })
                    print(f"✅ Intelligence Analysis {i+1}: PASS ({response_time:.2f}ms)")
                else:
                    self.test_results.append({
                        'test': f'Intelligence Analysis {i+1}',
                        'status': 'FAIL',
                        'response_time': response_time,
                        'details': f"Status Code: {response.status_code}"
                    })
                    print(f"❌ Intelligence Analysis {i+1}: FAIL ({response.status_code})")
                    
            except Exception as e:
                self.test_results.append({
                    'test': f'Intelligence Analysis {i+1}',
                    'status': 'ERROR',
                    'response_time': 0,
                    'details': str(e)
                })
                print(f"❌ Intelligence Analysis {i+1}: ERROR ({str(e)})")
    
    def test_dashboard_data(self):
        """Test dashboard data endpoint"""
        logger.info("Testing dashboard data endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/government/dashboard")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('metrics', {})
                self.test_results.append({
                    'test': 'Dashboard Data',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Agencies: {metrics.get('agencies_monitored')}, Security Score: {metrics.get('security_score')}%"
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
            response = requests.get(f"{self.base_url}/api/government/alerts?limit=10")
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
    
    def test_threat_intelligence(self):
        """Test threat intelligence endpoint"""
        logger.info("Testing threat intelligence endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/government/threat-intelligence")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                threat_level = data.get('overall_threat_level')
                threat_score = data.get('threat_score')
                self.test_results.append({
                    'test': 'Threat Intelligence',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Threat Level: {threat_level}, Score: {threat_score}"
                })
                print(f"✅ Threat Intelligence: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Threat Intelligence',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Threat Intelligence: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Threat Intelligence',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Threat Intelligence: ERROR ({str(e)})")
    
    def test_cyber_threats(self):
        """Test cyber threats endpoint"""
        logger.info("Testing cyber threats endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/government/cyber-threats")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                cyber_threat_level = data.get('overall_cyber_threat_level')
                cyber_threat_score = data.get('cyber_threat_score')
                self.test_results.append({
                    'test': 'Cyber Threats',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Cyber Threat Level: {cyber_threat_level}, Score: {cyber_threat_score}"
                })
                print(f"✅ Cyber Threats: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Cyber Threats',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Cyber Threats: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Cyber Threats',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Cyber Threats: ERROR ({str(e)})")
    
    def test_physical_security(self):
        """Test physical security endpoint"""
        logger.info("Testing physical security endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/government/physical-security")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                security_level = data.get('overall_security_level')
                security_score = data.get('physical_security_score')
                self.test_results.append({
                    'test': 'Physical Security',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Security Level: {security_level}, Score: {security_score}"
                })
                print(f"✅ Physical Security: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Physical Security',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Physical Security: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Physical Security',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Physical Security: ERROR ({str(e)})")
    
    def test_intelligence_analysis_endpoint(self):
        """Test intelligence analysis endpoint"""
        logger.info("Testing intelligence analysis endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/government/intelligence")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                intelligence_score = data.get('overall_intelligence_score')
                source_reliability = data.get('source_reliability', {}).get('confidence_level')
                self.test_results.append({
                    'test': 'Intelligence Analysis',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Intelligence Score: {intelligence_score}, Source Reliability: {source_reliability}"
                })
                print(f"✅ Intelligence Analysis: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Intelligence Analysis',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Intelligence Analysis: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Intelligence Analysis',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Intelligence Analysis: ERROR ({str(e)})")
    
    def test_agencies_endpoint(self):
        """Test agencies endpoint"""
        logger.info("Testing agencies endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/government/agencies")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                agencies = data.get('agencies', [])
                self.test_results.append({
                    'test': 'Agencies Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Agencies: {len(agencies)}, Operational: {data.get('fully_operational')}"
                })
                print(f"✅ Agencies Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Agencies Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Agencies Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Agencies Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Agencies Endpoint: ERROR ({str(e)})")
    
    def test_critical_infrastructure(self):
        """Test critical infrastructure endpoint"""
        logger.info("Testing critical infrastructure endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/government/critical-infrastructure")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                total_facilities = data.get('total_facilities')
                protected_facilities = data.get('protected_facilities')
                self.test_results.append({
                    'test': 'Critical Infrastructure',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Total: {total_facilities}, Protected: {protected_facilities}"
                })
                print(f"✅ Critical Infrastructure: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Critical Infrastructure',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Critical Infrastructure: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Critical Infrastructure',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Critical Infrastructure: ERROR ({str(e)})")
    
    def test_statistics_endpoint(self):
        """Test statistics endpoint"""
        logger.info("Testing statistics endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/government/stats")
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
                    'details': f"Agencies: {overview.get('agencies_monitored')}, Response Time: {performance.get('average_response_time')}ms"
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
        
        print("\n🚀 Government & Defense API Test Complete!")

if __name__ == "__main__":
    # Run the test suite
    test_suite = GovernmentDefenseAPITestSuite()
    test_suite.run_all_tests()
