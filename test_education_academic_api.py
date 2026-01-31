"""
🧪 EDUCATION & ACADEMIC API TEST SUITE
Stellar Logic AI - Education & Academic Integrity API Testing

Comprehensive testing for plagiarism detection, academic fraud prevention,
student behavior analysis, and educational institution security endpoints.
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

class EducationAcademicAPITestSuite:
    """Test suite for Education & Academic Integrity API"""
    
    def __init__(self, base_url="http://localhost:5008"):
        self.base_url = base_url
        self.test_results = []
        self.performance_metrics = []
        
    def run_all_tests(self):
        """Run all API tests"""
        logger.info("Starting Education & Academic API Test Suite")
        print("🧪 Education & Academic API Test Suite")
        print("=" * 60)
        
        # Test endpoints
        self.test_health_check()
        self.test_education_analysis()
        self.test_dashboard_data()
        self.test_alerts_endpoint()
        self.test_plagiarism_detection()
        self.test_students_endpoint()
        self.test_institutions_endpoint()
        self.test_assessments_endpoint()
        self.test_academic_integrity()
        self.test_research_integrity()
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
    
    def test_education_analysis(self):
        """Test education analysis endpoint"""
        logger.info("Testing education analysis endpoint")
        
        test_events = [
            {
                'event_id': 'EDU_001',
                'student_id': 'STUDENT_001',
                'institution_id': 'INST_001',
                'course_id': 'COURSE_001',
                'assessment_id': 'ASSESS_001',
                'academic_level': 'undergraduate',
                'institution_type': 'university',
                'assessment_type': 'assignment',
                'student_name': 'John Doe',
                'enrollment_date': '2020-09-01',
                'gpa': 3.7,
                'credits_completed': 45,
                'major': 'Computer Science',
                'attendance_rate': 0.92,
                'submission_date': '2024-01-15',
                'word_count': 2500,
                'submission_format': 'pdf',
                'time_spent': 180,
                'revision_count': 3,
                'text_content': 'This is a sample academic paper about artificial intelligence...',
                'writing_style': {
                    'complexity': 0.75,
                    'formality': 0.85,
                    'originality': 0.90
                },
                'citation_patterns': ['APA', 'MLA', 'Chicago'],
                'language_complexity': 0.78,
                'originality_score': 0.92,
                'grammar_score': 0.95,
                'login_patterns': ['2024-01-15 09:00', '2024-01-15 14:30', '2024-01-15 16:45'],
                'submission_patterns': ['on_time', 'on_time', 'late'],
                'study_time_patterns': [120, 90, 150, 180],
                'collaboration_patterns': ['individual', 'group', 'individual'],
                'resource_usage': {
                    'library_access': 15,
                    'database_queries': 25,
                    'online_resources': 30
                },
                'device_fingerprint': {
                    'browser': 'Chrome',
                    'os': 'Windows',
                    'screen_resolution': '1920x1080'
                },
                'previous_courses': ['CS101', 'CS102', 'MATH201'],
                'past_assessments': ['essay1', 'exam1', 'project1'],
                'academic_violations': [],
                'performance_trends': {
                    'improvement_rate': 0.15,
                    'consistency_score': 0.82
                },
                'skill_assessments': {
                    'critical_thinking': 0.85,
                    'writing_skills': 0.88,
                    'research_skills': 0.79
                },
                'student_data': {
                    'age': 20,
                    'gender': 'male',
                    'nationality': 'US'
                },
                'institution_data': {
                    'name': 'Tech University',
                    'location': 'California',
                    'type': 'public'
                },
                'assessment_data': {
                    'weight': 0.25,
                    'category': 'written_assignment',
                    'grading_rubric': 'standard'
                }
            },
            {
                'event_id': 'EDU_002',
                'student_id': 'STUDENT_002',
                'institution_id': 'INST_002',
                'course_id': 'COURSE_002',
                'assessment_id': 'ASSESS_002',
                'academic_level': 'graduate',
                'institution_type': 'university',
                'assessment_type': 'thesis',
                'student_name': 'Jane Smith',
                'enrollment_date': '2022-09-01',
                'gpa': 3.9,
                'credits_completed': 18,
                'major': 'Data Science',
                'attendance_rate': 0.96,
                'submission_date': '2024-01-20',
                'word_count': 15000,
                'submission_format': 'pdf',
                'time_spent': 720,
                'revision_count': 8,
                'text_content': 'This thesis explores advanced machine learning techniques...',
                'writing_style': {
                    'complexity': 0.92,
                    'formality': 0.95,
                    'originality': 0.88
                },
                'citation_patterns': ['APA', 'IEEE'],
                'language_complexity': 0.89,
                'originality_score': 0.85,
                'grammar_score': 0.97,
                'login_patterns': ['2024-01-20 08:00', '2024-01-20 13:00', '2024-01-20 18:00'],
                'submission_patterns': ['on_time', 'on_time', 'on_time'],
                'study_time_patterns': [240, 300, 180, 360],
                'collaboration_patterns': ['individual', 'advisor', 'individual'],
                'resource_usage': {
                    'library_access': 45,
                    'database_queries': 80,
                    'online_resources': 120
                },
                'device_fingerprint': {
                    'browser': 'Firefox',
                    'os': 'macOS',
                    'screen_resolution': '2560x1440'
                },
                'previous_courses': ['DS501', 'DS502', 'STAT601'],
                'past_assessments': ['research1', 'paper1', 'presentation1'],
                'academic_violations': [],
                'performance_trends': {
                    'improvement_rate': 0.08,
                    'consistency_score': 0.91
                },
                'skill_assessments': {
                    'critical_thinking': 0.94,
                    'writing_skills': 0.91,
                    'research_skills': 0.96
                },
                'student_data': {
                    'age': 25,
                    'gender': 'female',
                    'nationality': 'Canada'
                },
                'institution_data': {
                    'name': 'Research University',
                    'location': 'Boston',
                    'type': 'private'
                },
                'assessment_data': {
                    'weight': 0.60,
                    'category': 'graduate_thesis',
                    'grading_rubric': 'graduate_standard'
                }
            }
        ]
        
        for i, event in enumerate(test_events):
            try:
                start_time = time.time()
                response = requests.post(f"{self.base_url}/api/education/analyze", json=event)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    self.test_results.append({
                        'test': f'Education Analysis {i+1}',
                        'status': 'PASS',
                        'response_time': response_time,
                        'details': f"Status: {data.get('status')}, Security Level: {data.get('alert', {}).get('security_level', 'N/A')}"
                    })
                    print(f"✅ Education Analysis {i+1}: PASS ({response_time:.2f}ms)")
                else:
                    self.test_results.append({
                        'test': f'Education Analysis {i+1}',
                        'status': 'FAIL',
                        'response_time': response_time,
                        'details': f"Status Code: {response.status_code}"
                    })
                    print(f"❌ Education Analysis {i+1}: FAIL ({response.status_code})")
                    
            except Exception as e:
                self.test_results.append({
                    'test': f'Education Analysis {i+1}',
                    'status': 'ERROR',
                    'response_time': 0,
                    'details': str(e)
                })
                print(f"❌ Education Analysis {i+1}: ERROR ({str(e)})")
    
    def test_dashboard_data(self):
        """Test dashboard data endpoint"""
        logger.info("Testing dashboard data endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/education/dashboard")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('metrics', {})
                self.test_results.append({
                    'test': 'Dashboard Data',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Students: {metrics.get('students_monitored')}, Integrity Score: {metrics.get('integrity_score')}%"
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
            response = requests.get(f"{self.base_url}/api/education/alerts?limit=10")
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
    
    def test_plagiarism_detection(self):
        """Test plagiarism detection endpoint"""
        logger.info("Testing plagiarism detection endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/education/plagiarism-detection")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('overall_plagiarism_status')
                accuracy = data.get('detection_accuracy')
                self.test_results.append({
                    'test': 'Plagiarism Detection',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Status: {status}, Accuracy: {accuracy}"
                })
                print(f"✅ Plagiarism Detection: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Plagiarism Detection',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Plagiarism Detection: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Plagiarism Detection',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Plagiarism Detection: ERROR ({str(e)})")
    
    def test_students_endpoint(self):
        """Test students endpoint"""
        logger.info("Testing students endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/education/students")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                students = data.get('students', [])
                self.test_results.append({
                    'test': 'Students Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Students: {len(students)}, Active: {data.get('active_students')}"
                })
                print(f"✅ Students Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Students Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Students Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Students Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Students Endpoint: ERROR ({str(e)})")
    
    def test_institutions_endpoint(self):
        """Test institutions endpoint"""
        logger.info("Testing institutions endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/education/institutions")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                institutions = data.get('institutions', [])
                self.test_results.append({
                    'test': 'Institutions Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Institutions: {len(institutions)}, Active: {data.get('active_institutions')}"
                })
                print(f"✅ Institutions Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Institutions Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Institutions Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Institutions Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Institutions Endpoint: ERROR ({str(e)})")
    
    def test_assessments_endpoint(self):
        """Test assessments endpoint"""
        logger.info("Testing assessments endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/education/assessments")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                assessments = data.get('assessments', [])
                self.test_results.append({
                    'test': 'Assessments Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Assessments: {len(assessments)}, Active: {data.get('active_assessments')}"
                })
                print(f"✅ Assessments Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Assessments Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Assessments Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Assessments Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Assessments Endpoint: ERROR ({str(e)})")
    
    def test_academic_integrity(self):
        """Test academic integrity endpoint"""
        logger.info("Testing academic integrity endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/education/academic-integrity")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('overall_integrity_status')
                metrics = data.get('integrity_metrics', {})
                self.test_results.append({
                    'test': 'Academic Integrity',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Status: {status}, Performance Consistency: {metrics.get('performance_consistency')}"
                })
                print(f"✅ Academic Integrity: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Academic Integrity',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Academic Integrity: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Academic Integrity',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Academic Integrity: ERROR ({str(e)})")
    
    def test_research_integrity(self):
        """Test research integrity endpoint"""
        logger.info("Testing research integrity endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/education/research-integrity")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('overall_research_status')
                metrics = data.get('research_metrics', {})
                self.test_results.append({
                    'test': 'Research Integrity',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Status: {status}, Data Authenticity: {metrics.get('data_authenticity')}"
                })
                print(f"✅ Research Integrity: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Research Integrity',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Research Integrity: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Research Integrity',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Research Integrity: ERROR ({str(e)})")
    
    def test_statistics_endpoint(self):
        """Test statistics endpoint"""
        logger.info("Testing statistics endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/education/stats")
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
                    'details': f"Students: {overview.get('students_monitored')}, Response Time: {performance.get('average_response_time')}ms"
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
        
        print("\n🎓 Education & Academic API Test Complete!")

if __name__ == "__main__":
    # Run the test suite
    test_suite = EducationAcademicAPITestSuite()
    test_suite.run_all_tests()
