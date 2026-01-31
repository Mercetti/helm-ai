"""
🧪 ENHANCED GAMING API TEST SUITE
Stellar Logic AI - Enhanced Gaming Security API Testing

Comprehensive testing for anti-cheat detection, player behavior analysis,
tournament integrity, and gaming platform security endpoints.
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

class EnhancedGamingAPITestSuite:
    """Test suite for Enhanced Gaming Platform Security API"""
    
    def __init__(self, base_url="http://localhost:5007"):
        self.base_url = base_url
        self.test_results = []
        self.performance_metrics = []
        
    def run_all_tests(self):
        """Run all API tests"""
        logger.info("Starting Enhanced Gaming API Test Suite")
        print("🧪 Enhanced Gaming API Test Suite")
        print("=" * 60)
        
        # Test endpoints
        self.test_health_check()
        self.test_gaming_analysis()
        self.test_dashboard_data()
        self.test_alerts_endpoint()
        self.test_anti_cheat_status()
        self.test_players_endpoint()
        self.test_tournaments_endpoint()
        self.test_behavior_analysis()
        self.test_account_integrity()
        self.test_games_endpoint()
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
    
    def test_gaming_analysis(self):
        """Test gaming analysis endpoint"""
        logger.info("Testing gaming analysis endpoint")
        
        test_events = [
            {
                'event_id': 'GAMING_001',
                'player_id': 'PLAYER_001',
                'game_id': 'GAME_001',
                'tournament_id': 'TOURNAMENT_001',
                'game_type': 'fps',
                'session_id': 'SESSION_001',
                'session_duration': 3600,
                'game_mode': 'competitive',
                'map_name': 'Dust2',
                'server_region': 'NA',
                'mouse_movements': [random.random() for _ in range(100)],
                'keyboard_inputs': [random.random() for _ in range(50)],
                'game_commands': ['shoot', 'move', 'jump', 'reload'],
                'movement_patterns': [random.random() for _ in range(75)],
                'reaction_times': [random.uniform(0.1, 0.5) for _ in range(20)],
                'accuracy_metrics': {
                    'headshot_percentage': 0.45,
                    'overall_accuracy': 0.68,
                    'kill_death_ratio': 1.8
                },
                'kdr': 1.8,
                'win_rate': 0.65,
                'spm': 320,
                'headshot_pct': 0.45,
                'damage_dealt': 15000,
                'damage_taken': 8000,
                'ping': 35,
                'packet_loss': 0.01,
                'connection_stability': 0.98,
                'bandwidth_usage': 0.5,
                'client_version': '1.2.3',
                'os': 'Windows 10',
                'hardware_specs': {
                    'cpu': 'Intel i7-9700K',
                    'gpu': 'NVIDIA RTX 3080',
                    'ram': '16GB'
                },
                'running_processes': ['game.exe', 'discord.exe', 'steam.exe'],
                'memory_usage': 0.65,
                'player_data': {
                    'skill_level': 85,
                    'play_time_hours': 1500,
                    'account_age_days': 365
                },
                'tournament_data': {
                    'prize_pool': 10000,
                    'participants': 128,
                    'current_round': 3
                },
                'platform_data': {
                    'platform': 'Steam',
                    'region': 'North America',
                    'server_type': 'competitive'
                }
            },
            {
                'event_id': 'GAMING_002',
                'player_id': 'PLAYER_002',
                'game_id': 'GAME_002',
                'tournament_id': 'TOURNAMENT_002',
                'game_type': 'moba',
                'session_id': 'SESSION_002',
                'session_duration': 2400,
                'game_mode': 'ranked',
                'map_name': 'Summoners Rift',
                'server_region': 'EU',
                'mouse_movements': [random.random() for _ in range(80)],
                'keyboard_inputs': [random.random() for _ in range(40)],
                'game_commands': ['attack', 'move', 'skill', 'ultimate'],
                'movement_patterns': [random.random() for _ in range(60)],
                'reaction_times': [random.uniform(0.15, 0.6) for _ in range(15)],
                'accuracy_metrics': {
                    'skill_accuracy': 0.72,
                    'cs_per_minute': 8.5,
                    'kill_participation': 0.68
                },
                'kdr': 2.2,
                'win_rate': 0.58,
                'spm': 280,
                'headshot_pct': 0.0,
                'damage_dealt': 25000,
                'damage_taken': 12000,
                'ping': 45,
                'packet_loss': 0.02,
                'connection_stability': 0.95,
                'bandwidth_usage': 0.3,
                'client_version': '2.1.4',
                'os': 'Windows 11',
                'hardware_specs': {
                    'cpu': 'AMD Ryzen 7 5800X',
                    'gpu': 'NVIDIA RTX 3070',
                    'ram': '32GB'
                },
                'running_processes': ['game.exe', 'teamspeak.exe', 'epic_games.exe'],
                'memory_usage': 0.72,
                'player_data': {
                    'skill_level': 78,
                    'play_time_hours': 2200,
                    'account_age_days': 730
                },
                'tournament_data': {
                    'prize_pool': 25000,
                    'participants': 64,
                    'current_round': 2
                },
                'platform_data': {
                    'platform': 'Epic Games',
                    'region': 'Europe',
                    'server_type': 'tournament'
                }
            }
        ]
        
        for i, event in enumerate(test_events):
            try:
                start_time = time.time()
                response = requests.post(f"{self.base_url}/api/gaming/analyze", json=event)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    self.test_results.append({
                        'test': f'Gaming Analysis {i+1}',
                        'status': 'PASS',
                        'response_time': response_time,
                        'details': f"Status: {data.get('status')}, Security Level: {data.get('alert', {}).get('security_level', 'N/A')}"
                    })
                    print(f"✅ Gaming Analysis {i+1}: PASS ({response_time:.2f}ms)")
                else:
                    self.test_results.append({
                        'test': f'Gaming Analysis {i+1}',
                        'status': 'FAIL',
                        'response_time': response_time,
                        'details': f"Status Code: {response.status_code}"
                    })
                    print(f"❌ Gaming Analysis {i+1}: FAIL ({response.status_code})")
                    
            except Exception as e:
                self.test_results.append({
                    'test': f'Gaming Analysis {i+1}',
                    'status': 'ERROR',
                    'response_time': 0,
                    'details': str(e)
                })
                print(f"❌ Gaming Analysis {i+1}: ERROR ({str(e)})")
    
    def test_dashboard_data(self):
        """Test dashboard data endpoint"""
        logger.info("Testing dashboard data endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/gaming/dashboard")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('metrics', {})
                self.test_results.append({
                    'test': 'Dashboard Data',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Players: {metrics.get('players_monitored')}, Security Score: {metrics.get('security_score')}%"
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
            response = requests.get(f"{self.base_url}/api/gaming/alerts?limit=10")
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
    
    def test_anti_cheat_status(self):
        """Test anti-cheat status endpoint"""
        logger.info("Testing anti-cheat status endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/gaming/anti-cheat")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('overall_anti_cheat_status')
                accuracy = data.get('detection_accuracy')
                self.test_results.append({
                    'test': 'Anti-Cheat Status',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Status: {status}, Accuracy: {accuracy}"
                })
                print(f"✅ Anti-Cheat Status: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Anti-Cheat Status',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Anti-Cheat Status: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Anti-Cheat Status',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Anti-Cheat Status: ERROR ({str(e)})")
    
    def test_players_endpoint(self):
        """Test players endpoint"""
        logger.info("Testing players endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/gaming/players")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                players = data.get('players', [])
                self.test_results.append({
                    'test': 'Players Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Players: {len(players)}, Active: {data.get('active_players')}"
                })
                print(f"✅ Players Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Players Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Players Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Players Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Players Endpoint: ERROR ({str(e)})")
    
    def test_tournaments_endpoint(self):
        """Test tournaments endpoint"""
        logger.info("Testing tournaments endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/gaming/tournaments")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                tournaments = data.get('tournaments', [])
                self.test_results.append({
                    'test': 'Tournaments Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Tournaments: {len(tournaments)}, Active: {data.get('active_tournaments')}"
                })
                print(f"✅ Tournaments Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Tournaments Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Tournaments Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Tournaments Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Tournaments Endpoint: ERROR ({str(e)})")
    
    def test_behavior_analysis(self):
        """Test behavior analysis endpoint"""
        logger.info("Testing behavior analysis endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/gaming/behavior-analysis")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('overall_behavior_status')
                patterns = data.get('behavior_patterns', {})
                self.test_results.append({
                    'test': 'Behavior Analysis',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Status: {status}, Skill Consistency: {patterns.get('skill_consistency')}"
                })
                print(f"✅ Behavior Analysis: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Behavior Analysis',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Behavior Analysis: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Behavior Analysis',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Behavior Analysis: ERROR ({str(e)})")
    
    def test_account_integrity(self):
        """Test account integrity endpoint"""
        logger.info("Testing account integrity endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/gaming/account-integrity")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('overall_integrity_status')
                metrics = data.get('integrity_metrics', {})
                self.test_results.append({
                    'test': 'Account Integrity',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Status: {status}, Login Consistency: {metrics.get('login_pattern_consistency')}"
                })
                print(f"✅ Account Integrity: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Account Integrity',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Account Integrity: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Account Integrity',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Account Integrity: ERROR ({str(e)})")
    
    def test_games_endpoint(self):
        """Test games endpoint"""
        logger.info("Testing games endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/gaming/games")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                games = data.get('games', [])
                self.test_results.append({
                    'test': 'Games Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Games: {len(games)}, Protected: {data.get('protected_games')}"
                })
                print(f"✅ Games Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Games Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Games Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Games Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Games Endpoint: ERROR ({str(e)})")
    
    def test_statistics_endpoint(self):
        """Test statistics endpoint"""
        logger.info("Testing statistics endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/gaming/stats")
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
                    'details': f"Players: {overview.get('players_monitored')}, Response Time: {performance.get('average_response_time')}ms"
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
        
        print("\n🎮 Enhanced Gaming API Test Complete!")

if __name__ == "__main__":
    # Run the test suite
    test_suite = EnhancedGamingAPITestSuite()
    test_suite.run_all_tests()
