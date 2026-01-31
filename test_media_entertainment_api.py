"""
🧪 MEDIA & ENTERTAINMENT SECURITY TEST SUITE
Stellar Logic AI - Media Security API Testing

Comprehensive testing for content piracy detection, copyright protection,
digital rights management, and compliance monitoring endpoints.
"""

import requests
import json
import time
import logging
from datetime import datetime
import random
import statistics
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MediaEntertainmentAPITestSuite:
    """Test suite for Media & Entertainment Security API"""
    
    def __init__(self, base_url="http://localhost:5008"):
        self.base_url = base_url
        self.test_results = []
        self.performance_metrics = []
        
    def run_all_tests(self):
        """Run all API tests"""
        logger.info("Starting Media Entertainment API Test Suite")
        print("🧪 Media & Entertainment Security API Test Suite")
        print("=" * 60)
        
        # Test endpoints
        self.test_health_check()
        self.test_media_analysis()
        self.test_media_dashboard()
        self.test_media_alerts()
        self.test_content_status()
        self.test_violation_monitoring()
        self.test_threat_type_analysis()
        self.test_compliance_status()
        self.test_market_analysis()
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
                    'details': f"Status: {data.get('status')}, Service: {data.get('service')}"
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
            logger.error(f"Error in health check: {e}")
            self.test_results.append({
                'test': 'Health Check',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Health Check: ERROR ({str(e)})")
    
    def test_media_analysis(self):
        """Test media analysis endpoint"""
        logger.info("Testing media analysis endpoint")
        
        test_events = [
            {
                'content_id': 'MEDIA_TEST_001',
                'content_type': 'movie',
                'title': 'Test Movie',
                'creator': 'Test Studio',
                'distribution_channels': ['netflix', 'amazon', 'hulu'],
                'copyright_info': {
                    'registered': True,
                    'registration_date': '2020-01-01',
                    'owner': 'Test Studio'
                },
                'license_info': {
                    'type': 'exclusive',
                    'territory': 'worldwide',
                    'duration': 'perpetual'
                },
                'risk_indicators': ['high_value_content', 'popular_title']
            },
            {
                'content_id': 'MEDIA_TEST_002',
                'content_type': 'music',
                'title': 'Test Song',
                'creator': 'Test Artist',
                'distribution_channels': ['spotify', 'apple_music', 'youtube'],
                'copyright_info': {
                    'registered': True,
                    'registration_date': '2021-01-01',
                    'owner': 'Test Label'
                },
                'license_info': {
                    'type': 'non_exclusive',
                    'territory': 'north_america',
                    'duration': '5_years'
                },
                'risk_indicators': ['viral_content', 'high_streams']
            },
            {
                'content_id': 'MEDIA_TEST_003',
                'content_type': 'tv_show',
                'title': 'Test Series',
                'creator': 'Test Network',
                'distribution_channels': ['hbo_max', 'disney_plus', 'amazon'],
                'copyright_info': {
                    'registered': True,
                    'registration_date': '2019-01-01',
                    'owner': 'Test Network'
                },
                'license_info': {
                    'type': 'exclusive',
                    'territory': 'global',
                    'duration': '10_years'
                },
                'risk_indicators': ['premium_content', 'high_demand']
            }
        ]
        
        for i, event in enumerate(test_events):
            try:
                start_time = time.time()
                response = requests.post(f"{self.base_url}/api/media/analyze", json=event)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    self.test_results.append({
                        'test': f'Media Analysis {i+1}',
                        'status': 'PASS',
                        'response_time': response_time,
                        'details': f"Status: {data.get('status')}, Threat: {data.get('threat_analysis', {}).get('threat_detected', False)}"
                    })
                    print(f"✅ Media Analysis {i+1}: PASS ({response_time:.2f}ms)")
                else:
                    self.test_results.append({
                        'test': f'Media Analysis {i+1}',
                        'status': 'FAIL',
                        'response_time': response_time,
                        'details': f"Status Code: {response.status_code}"
                    })
                    print(f"❌ Media Analysis {i+1}: FAIL ({response.status_code})")
                    
            except Exception as e:
                self.test_results.append({
                    'test': f'Media Analysis {i+1}',
                    'status': 'ERROR',
                    'response_time': 0,
                    'details': str(e)
                })
                print(f"❌ Media Analysis {i+1}: ERROR ({str(e)})")
    
    def test_media_dashboard(self):
        """Test media dashboard endpoint"""
        logger.info("Testing media dashboard endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/media/dashboard")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('metrics', {})
                self.test_results.append({
                    'test': 'Media Dashboard',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Content: {metrics.get('total_content_analyzed', 0)}, Alerts: {metrics.get('alerts_generated', 0)}"
                })
                print(f"✅ Media Dashboard: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Media Dashboard',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Media Dashboard: FAIL ({response.status_code})")
                
        except Exception as e:
            logger.error(f"Error in media dashboard: {e}")
            self.test_results.append({
                'test': 'Media Dashboard',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Media Dashboard: ERROR ({str(e)})")
    
    def test_media_alerts(self):
        """Test media alerts endpoint"""
        logger.info("Testing media alerts endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/media/alerts?limit=10")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                alerts = data.get('alerts', [])
                self.test_results.append({
                    'test': 'Media Alerts',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Alerts: {len(alerts)}, Total Count: {data.get('total_count', 0)}"
                })
                print(f"✅ Media Alerts: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Media Alerts',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Media Alerts: FAIL ({response.status_code})")
                
        except Exception as e:
            logger.error(f"Error in media alerts: {e}")
            self.test_results.append({
                'test': 'Media Alerts',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Media Alerts: ERROR ({str(e)})")
    
    def test_content_status(self):
        """Test content status endpoint"""
        logger.info("Testing content status endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/media/content?limit=10")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                content = data.get('content', [])
                self.test_results.append({
                    'test': 'Content Status',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Content: {len(content)}, Total Count: {data.get('total_count', 0)}"
                })
                print(f"✅ Content Status: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Content Status',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Content Status: FAIL ({response.status_code})")
                
        except Exception as e:
            logger.error(f"Error in content status: {e}")
            self.test_results.append({
                'test': 'Content Status',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Content Status: ERROR ({str(e)})")
    
    def test_violation_monitoring(self):
        """Test violation monitoring endpoint"""
        logger.info("Testing violation monitoring endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/media/violations?limit=10")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                violations = data.get('violations', [])
                self.test_results.append({
                    'test': 'Violation Monitoring',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Violations: {len(violations)}, Total Count: {data.get('total_count', 0)}"
                })
                print(f"✅ Violation Monitoring: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Violation Monitoring',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Violation Monitoring: FAIL ({response.status_code})")
                
        except Exception as e:
            logger.error(f"Error in violation monitoring: {e}")
            self.test_results.append({
                'test': 'Violation Monitoring',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Violation Monitoring: ERROR ({str(e)})")
    
    def test_threat_type_analysis(self):
        """Test threat type analysis endpoint"""
        logger.info("Testing threat type analysis endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/media/threat-types")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                threat_stats = data.get('threat_type_statistics', {})
                self.test_results.append({
                    'test': 'Threat Type Analysis',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Total Cases: {data.get('total_threat_cases', 0)}, Types: {len(threat_stats)}"
                })
                print(f"✅ Threat Type Analysis: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Threat Type Analysis',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Threat Type Analysis: FAIL ({response.status_code})")
                
        except Exception as e:
            logger.error(f"Error in threat type analysis: {e}")
            self.test_results.append({
                'test': 'Threat Type Analysis',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Threat Type Analysis: ERROR ({str(e)})")
    
    def test_compliance_status(self):
        """Test compliance status endpoint"""
        logger.info("Testing compliance status endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/media/compliance")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                compliance_score = data.get('compliance_score', 0)
                frameworks = data.get('compliance_frameworks', {})
                self.test_results.append({
                    'test': 'Compliance Status',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Compliance Score: {compliance_score:.2f}, Frameworks: {len(frameworks)}"
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
            logger.error(f"Error in compliance status: {e}")
            self.test_results.append({
                'test': 'Compliance Status',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Compliance Status: ERROR ({str(e)})")
    
    def test_market_analysis(self):
        """Test market analysis endpoint"""
        logger.info("Testing market analysis endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/media/market-analysis")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                market_value = data.get('total_market_value', 0)
                piracy_rate = data.get('piracy_detection_rate', 0)
                self.test_results.append({
                    'test': 'Market Analysis',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Market Value: ${market_value:,}, Piracy Rate: {piracy_rate:.2f}"
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
            logger.error(f"Error in market analysis: {e}")
            self.test_results.append({
                'test': 'Market Analysis',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Market Analysis: ERROR ({str(e)})")
    
    def test_comprehensive_statistics(self):
        """Test comprehensive statistics endpoint"""
        logger.info("Testing comprehensive statistics endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/media/statistics")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                overview = data.get('platform_overview', {})
                performance = data.get('performance_metrics', {})
                business = data.get('business_metrics', {})
                self.test_results.append({
                    'test': 'Comprehensive Statistics',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Content: {overview.get('total_content_analyzed', 0)}, Alerts: {overview.get('alerts_generated', 0)}"
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
            logger.error(f"Error in comprehensive statistics: {e}")
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
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"💥 Errors: {error_tests}")
        print(f"Success Rate: {(passed_tests / total_tests * 100):.1f}%")
        print(f"Average Response Time: {avg_response_time:.2f}ms")
        
        print("\n🚀 MEDIA ENTERTAINMENT API TEST COMPLETE!")
        print("=" * 60)

if __name__ == "__main__":
    # Run the test suite
    test_suite = MediaEntertainmentAPITestSuite()
    test_suite.run_all_tests()
