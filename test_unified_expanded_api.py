"""
🧪 UNIFIED EXPANDED PLATFORM TEST SUITE
Stellar Logic AI - Multi-Plugin Security Platform API Testing

Comprehensive testing for unified platform management, cross-plugin
threat intelligence, and integrated security operations across all 8 plugins.
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

class UnifiedPlatformAPITestSuite:
    """Test suite for Unified Expanded Platform API"""
    
    def __init__(self, base_url="http://localhost:5010"):
        self.base_url = base_url
        self.test_results = []
        self.performance_metrics = []
        
    def run_all_tests(self):
        """Run all API tests"""
        logger.info("Starting Unified Expanded Platform API Test Suite")
        print("🧪 Unified Expanded Platform API Test Suite")
        print("=" * 60)
        
        # Test endpoints
        self.test_health_check()
        self.test_unified_analysis()
        self.test_unified_dashboard()
        self.test_unified_alerts()
        self.test_plugins_status()
        self.test_cross_plugin_correlations()
        self.test_threat_intelligence()
        self.test_platform_performance()
        self.test_market_analysis()
        self.test_compliance_status()
        self.test_enterprise_metrics()
        self.test_comprehensive_statistics()
        
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
                    'details': f"Status: {data.get('status')}, Platform: {data.get('service')}"
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
    
    def test_unified_analysis(self):
        """Test unified event analysis endpoint"""
        logger.info("Testing unified analysis endpoint")
        
        test_events = [
            {
                'event_id': 'UNIFIED_001',
                'plugin_type': 'manufacturing_iot',
                'source_plugin': 'manufacturing_iot',
                'event_type': 'security_threat',
                'severity': 'high',
                'timestamp': datetime.now().isoformat(),
                'event_data': {
                    'threat_type': 'industrial_control_system_attack',
                    'affected_systems': ['PLC_001', 'SCADA_002'],
                    'attack_vector': 'malware_injection',
                    'impact_assessment': 'critical',
                    'geographic_location': 'North America',
                    'industry_sector': 'manufacturing'
                },
                'correlation_data': {
                    'cross_plugin_indicators': True,
                    'related_plugins': ['government_defense', 'automotive_transportation'],
                    'threat_pattern': 'coordinated_attack'
                }
            },
            {
                'event_id': 'UNIFIED_002',
                'plugin_type': 'government_defense',
                'source_plugin': 'government_defense',
                'event_type': 'security_threat',
                'severity': 'critical',
                'timestamp': datetime.now().isoformat(),
                'event_data': {
                    'threat_type': 'nation_state_attack',
                    'target_systems': ['defense_network', 'critical_infrastructure'],
                    'attack_vector': 'advanced_persistent_threat',
                    'impact_assessment': 'severe',
                    'geographic_location': 'Europe',
                    'industry_sector': 'government'
                },
                'correlation_data': {
                    'cross_plugin_indicators': True,
                    'related_plugins': ['manufacturing_iot', 'automotive_transportation', 'media_entertainment'],
                    'threat_pattern': 'multi_sector_attack'
                }
            },
            {
                'event_id': 'UNIFIED_003',
                'plugin_type': 'automotive_transportation',
                'source_plugin': 'automotive_transportation',
                'event_type': 'security_threat',
                'severity': 'high',
                'timestamp': datetime.now().isoformat(),
                'event_data': {
                    'threat_type': 'vehicle_hacking',
                    'affected_vehicles': ['autonomous_fleet_001'],
                    'attack_vector': 'can_bus_exploit',
                    'impact_assessment': 'significant',
                    'geographic_location': 'Asia',
                    'industry_sector': 'automotive'
                },
                'correlation_data': {
                    'cross_plugin_indicators': True,
                    'related_plugins': ['manufacturing_iot', 'government_defense'],
                    'threat_pattern': 'supply_chain_attack'
                }
            }
        ]
        
        for i, event in enumerate(test_events):
            try:
                start_time = time.time()
                response = requests.post(f"{self.base_url}/api/unified/analyze", json=event)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    self.test_results.append({
                        'test': f'Unified Analysis {i+1}',
                        'status': 'PASS',
                        'response_time': response_time,
                        'details': f"Status: {data.get('status')}, Correlation: {data.get('alert', {}).get('cross_plugin_correlation', False)}"
                    })
                    print(f"✅ Unified Analysis {i+1}: PASS ({response_time:.2f}ms)")
                else:
                    self.test_results.append({
                        'test': f'Unified Analysis {i+1}',
                        'status': 'FAIL',
                        'response_time': response_time,
                        'details': f"Status Code: {response.status_code}"
                    })
                    print(f"❌ Unified Analysis {i+1}: FAIL ({response.status_code})")
                    
            except Exception as e:
                self.test_results.append({
                    'test': f'Unified Analysis {i+1}',
                    'status': 'ERROR',
                    'response_time': 0,
                    'details': str(e)
                })
                print(f"❌ Unified Analysis {i+1}: ERROR ({str(e)})")
    
    def test_unified_dashboard(self):
        """Test unified dashboard endpoint"""
        logger.info("Testing unified dashboard endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/unified/dashboard")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                platform_status = data.get('platform_status', {})
                self.test_results.append({
                    'test': 'Unified Dashboard',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Plugins: {platform_status.get('active_plugins')}, Market: ${platform_status.get('total_market_coverage', 0)/1000000000:.0f}B"
                })
                print(f"✅ Unified Dashboard: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Unified Dashboard',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Unified Dashboard: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Unified Dashboard',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Unified Dashboard: ERROR ({str(e)})")
    
    def test_unified_alerts(self):
        """Test unified alerts endpoint"""
        logger.info("Testing unified alerts endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/unified/alerts?limit=10")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                alerts = data.get('alerts', [])
                self.test_results.append({
                    'test': 'Unified Alerts',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Alerts: {len(alerts)}, Correlations: {data.get('correlation_count', 0)}"
                })
                print(f"✅ Unified Alerts: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Unified Alerts',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Unified Alerts: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Unified Alerts',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Unified Alerts: ERROR ({str(e)})")
    
    def test_plugins_status(self):
        """Test plugins status endpoint"""
        logger.info("Testing plugins status endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/unified/plugins")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                plugins = data.get('plugins', [])
                self.test_results.append({
                    'test': 'Plugins Status',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Plugins: {len(plugins)}, Active: {data.get('active_plugins')}"
                })
                print(f"✅ Plugins Status: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Plugins Status',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Plugins Status: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Plugins Status',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Plugins Status: ERROR ({str(e)})")
    
    def test_cross_plugin_correlations(self):
        """Test cross-plugin correlations endpoint"""
        logger.info("Testing cross-plugin correlations endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/unified/correlations")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                correlations = data.get('total_correlations', 0)
                rules = data.get('correlation_rules', 0)
                self.test_results.append({
                    'test': 'Cross-Plugin Correlations',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Correlations: {correlations}, Rules: {rules}"
                })
                print(f"✅ Cross-Plugin Correlations: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Cross-Plugin Correlations',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Cross-Plugin Correlations: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Cross-Plugin Correlations',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Cross-Plugin Correlations: ERROR ({str(e)})")
    
    def test_threat_intelligence(self):
        """Test threat intelligence endpoint"""
        logger.info("Testing threat intelligence endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/unified/threat-intelligence")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                threat_patterns = data.get('threat_patterns', {})
                self.test_results.append({
                    'test': 'Threat Intelligence',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Threat Patterns: {len(threat_patterns)}, Attack Vectors: {len(data.get('attack_vectors', {}))}"
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
    
    def test_platform_performance(self):
        """Test platform performance endpoint"""
        logger.info("Testing platform performance endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/unified/performance")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                platform_perf = data.get('platform_performance', {})
                self.test_results.append({
                    'test': 'Platform Performance',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Response Time: {platform_perf.get('average_response_time', 0):.2f}ms, Accuracy: {platform_perf.get('average_accuracy', 0):.2f}%"
                })
                print(f"✅ Platform Performance: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Platform Performance',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Platform Performance: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Platform Performance',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Platform Performance: ERROR ({str(e)})")
    
    def test_market_analysis(self):
        """Test market analysis endpoint"""
        logger.info("Testing market analysis endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/unified/market-analysis")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                market_coverage = data.get('total_market_coverage', 0)
                breakdown = data.get('market_breakdown', {})
                self.test_results.append({
                    'test': 'Market Analysis',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Market Coverage: ${market_coverage/1000000000:.0f}B, Segments: {len(breakdown)}"
                })
                print(f"✅ Market Analysis: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Market Analysis',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Market Analysis: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Market Analysis',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Market Analysis: ERROR ({str(e)})")
    
    def test_compliance_status(self):
        """Test compliance status endpoint"""
        logger.info("Testing compliance status endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/unified/compliance")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                frameworks = data.get('compliance_frameworks', {})
                self.test_results.append({
                    'test': 'Compliance Status',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Frameworks: {len(frameworks)}, Status: {data.get('overall_compliance_status')}"
                })
                print(f"✅ Compliance Status: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Compliance Status',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Compliance Status: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Compliance Status',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Compliance Status: ERROR ({str(e)})")
    
    def test_enterprise_metrics(self):
        """Test enterprise metrics endpoint"""
        logger.info("Testing enterprise metrics endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/unified/enterprise")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                clients = data.get('enterprise_clients', {})
                self.test_results.append({
                    'test': 'Enterprise Metrics',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Total Clients: {clients.get('total_clients')}, Satisfaction: {clients.get('client_satisfaction_score')}"
                })
                print(f"✅ Enterprise Metrics: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Enterprise Metrics',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Enterprise Metrics: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Enterprise Metrics',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Enterprise Metrics: ERROR ({str(e)})")
    
    def test_comprehensive_statistics(self):
        """Test comprehensive statistics endpoint"""
        logger.info("Testing comprehensive statistics endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/unified/stats")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                overview = data.get('platform_overview', {})
                performance = data.get('performance_metrics', {})
                self.test_results.append({
                    'test': 'Comprehensive Statistics',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Plugins: {overview.get('active_plugins')}, Response Time: {performance.get('average_response_time', 0):.2f}ms"
                })
                print(f"✅ Comprehensive Statistics: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Comprehensive Statistics',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Comprehensive Statistics: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Comprehensive Statistics',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Comprehensive Statistics: ERROR ({str(e)})")
    
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
        
        print("\n🌐 Unified Expanded Platform API Test Complete!")

if __name__ == "__main__":
    # Run the test suite
    test_suite = UnifiedPlatformAPITestSuite()
    test_suite.run_all_tests()
