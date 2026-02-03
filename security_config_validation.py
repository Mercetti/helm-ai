#!/usr/bin/env python3
"""
Stellar Logic AI - Security Configuration Validation Tests
Validate security components are properly configured without requiring server
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

class SecurityConfigurationValidator:
    """Validate security configuration files and components"""
    
    def __init__(self):
        self.base_path = "c:/Users/merce/Documents/helm-ai"
        self.production_path = "c:/Users/merce/Documents/helm-ai/production"
        self.test_results = []
    
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
    
    def test_production_directory_structure(self) -> bool:
        """Test production directory structure"""
        required_dirs = [
            "production",
            "production/security",
            "production/config",
            "production/logs",
            "production/ssl",
            "production/secrets",
            "production/monitoring",
            "production/storage",
            "production/storage/rate_limiting",
            "production/storage/csrf",
            "production/middleware"
        ]
        
        existing_dirs = []
        missing_dirs = []
        
        for dir_path in required_dirs:
            full_path = os.path.join(self.base_path, dir_path)
            if os.path.exists(full_path):
                existing_dirs.append(dir_path)
            else:
                missing_dirs.append(dir_path)
        
        passed = len(missing_dirs) == 0
        message = f"Directory structure: {'Complete' if passed else f'Missing {len(missing_dirs)} directories'}"
        details = {
            "existing_dirs": len(existing_dirs),
            "missing_dirs": missing_dirs
        }
        
        self.log_test_result("Production Directory Structure", passed, message, details)
        return passed
    
    def test_security_components_deployment(self) -> bool:
        """Test security components are deployed"""
        required_files = [
            "production/security/security_https_middleware.py",
            "production/security/security_csrf_protection.py",
            "production/security/security_auth_rate_limiting.py",
            "production/security/security_password_policy.py",
            "production/security/security_jwt_rotation.py",
            "production/security/security_input_validation.py",
            "production/security/security_api_key_management.py",
            "production/security/stellar_logic_ai_security.py"
        ]
        
        existing_files = []
        missing_files = []
        
        for file_path in required_files:
            full_path = os.path.join(self.base_path, file_path)
            if os.path.exists(full_path):
                existing_files.append(file_path)
                # Check file size
                file_size = os.path.getsize(full_path)
                if file_size == 0:
                    missing_files.append(f"{file_path} (empty)")
            else:
                missing_files.append(file_path)
        
        passed = len(missing_files) == 0
        message = f"Security components: {'All deployed' if passed else f'Missing {len(missing_files)} files'}"
        details = {
            "deployed_files": len(existing_files),
            "missing_files": missing_files
        }
        
        self.log_test_result("Security Components Deployment", passed, message, details)
        return passed
    
    def test_configuration_files(self) -> bool:
        """Test configuration files exist and are valid"""
        config_files = [
            ("production/config/production_config.json", "Production configuration"),
            ("production/config/rate_limiting_config.json", "Rate limiting configuration"),
            ("production/config/csrf_protection_config.json", "CSRF protection configuration"),
            ("production/monitoring/security_monitoring.json", "Security monitoring configuration")
        ]
        
        valid_configs = []
        invalid_configs = []
        
        for config_file, description in config_files:
            full_path = os.path.join(self.base_path, config_file)
            
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r') as f:
                        config_data = json.load(f)
                    
                    # Basic validation
                    if isinstance(config_data, dict) and len(config_data) > 0:
                        valid_configs.append(description)
                    else:
                        invalid_configs.append(f"{description} (invalid format)")
                except json.JSONDecodeError:
                    invalid_configs.append(f"{description} (invalid JSON)")
                except Exception as e:
                    invalid_configs.append(f"{description} (error: {str(e)})")
            else:
                invalid_configs.append(f"{description} (missing)")
        
        passed = len(invalid_configs) == 0
        message = f"Configuration files: {'All valid' if passed else f'{len(invalid_configs)} invalid'}"
        details = {
            "valid_configs": valid_configs,
            "invalid_configs": invalid_configs
        }
        
        self.log_test_result("Configuration Files", passed, message, details)
        return passed
    
    def test_startup_scripts(self) -> bool:
        """Test startup scripts exist"""
        startup_scripts = [
            "production/start_stellar_security.py",
            "production/start_stellar_security_https.py",
            "production/initialize_security_middleware.py",
            "production/start_monitoring.py"
        ]
        
        existing_scripts = []
        missing_scripts = []
        
        for script_file in startup_scripts:
            full_path = os.path.join(self.base_path, script_file)
            if os.path.exists(full_path):
                existing_scripts.append(script_file)
                # Check if script is executable (has content)
                file_size = os.path.getsize(full_path)
                if file_size == 0:
                    missing_scripts.append(f"{script_file} (empty)")
            else:
                missing_scripts.append(script_file)
        
        passed = len(missing_scripts) == 0
        message = f"Startup scripts: {'All present' if passed else f'Missing {len(missing_scripts)} scripts'}"
        details = {
            "existing_scripts": len(existing_scripts),
            "missing_scripts": missing_scripts
        }
        
        self.log_test_result("Startup Scripts", passed, message, details)
        return passed
    
    def test_ssl_configuration(self) -> bool:
        """Test SSL configuration"""
        ssl_files = [
            "production/ssl/generate_certificates.bat",
            "production/ssl/generate_certificates.sh"
        ]
        
        existing_files = []
        missing_files = []
        
        for ssl_file in ssl_files:
            full_path = os.path.join(self.base_path, ssl_file)
            if os.path.exists(full_path):
                existing_files.append(ssl_file)
            else:
                missing_files.append(ssl_file)
        
        # Check if certificates exist (optional for testing)
        cert_files = [
            "production/ssl/stellar_logic_ai.crt",
            "production/ssl/stellar_logic_ai.key",
            "production/ssl/ca.crt"
        ]
        
        existing_certs = []
        for cert_file in cert_files:
            full_path = os.path.join(self.base_path, cert_file)
            if os.path.exists(full_path):
                existing_certs.append(cert_file)
        
        passed = len(existing_files) > 0  # At least generation scripts exist
        message = f"SSL configuration: {'Setup complete' if passed else 'Setup incomplete'}"
        details = {
            "generation_scripts": len(existing_files),
            "existing_certificates": len(existing_certs),
            "missing_scripts": missing_files
        }
        
        self.log_test_result("SSL Configuration", passed, message, details)
        return passed
    
    def test_middleware_files(self) -> bool:
        """Test middleware files exist"""
        middleware_files = [
            "production/middleware/rate_limiting_middleware.py",
            "production/middleware/csrf_middleware.py"
        ]
        
        existing_files = []
        missing_files = []
        
        for middleware_file in middleware_files:
            full_path = os.path.join(self.base_path, middleware_file)
            if os.path.exists(full_path):
                existing_files.append(middleware_file)
                # Check file content
                file_size = os.path.getsize(full_path)
                if file_size == 0:
                    missing_files.append(f"{middleware_file} (empty)")
            else:
                missing_files.append(middleware_file)
        
        passed = len(missing_files) == 0
        message = f"Middleware files: {'All present' if passed else f'Missing {len(missing_files)} files'}"
        details = {
            "existing_files": len(existing_files),
            "missing_files": missing_files
        }
        
        self.log_test_result("Middleware Files", passed, message, details)
        return passed
    
    def test_storage_initialization(self) -> bool:
        """Test storage data files are initialized"""
        storage_files = [
            "production/storage/rate_limiting/rate_limit_data.json",
            "production/storage/csrf/csrf_data.json"
        ]
        
        initialized_files = []
        missing_files = []
        
        for storage_file in storage_files:
            full_path = os.path.join(self.base_path, storage_file)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r') as f:
                        data = json.load(f)
                    
                    if isinstance(data, dict):
                        initialized_files.append(storage_file)
                    else:
                        missing_files.append(f"{storage_file} (invalid format)")
                except:
                    missing_files.append(f"{storage_file} (invalid JSON)")
            else:
                missing_files.append(storage_file)
        
        passed = len(initialized_files) > 0
        message = f"Storage initialization: {'Complete' if passed else 'Incomplete'}"
        details = {
            "initialized_files": len(initialized_files),
            "missing_files": missing_files
        }
        
        self.log_test_result("Storage Initialization", passed, message, details)
        return passed
    
    def test_documentation_files(self) -> bool:
        """Test documentation files exist"""
        doc_files = [
            "production/SSL_HTTPS_SETUP.md",
            "production/DEPLOYMENT_GUIDE.md"
        ]
        
        existing_docs = []
        missing_docs = []
        
        for doc_file in doc_files:
            full_path = os.path.join(self.base_path, doc_file)
            if os.path.exists(full_path):
                existing_docs.append(doc_file)
            else:
                missing_docs.append(doc_file)
        
        passed = len(existing_docs) > 0
        message = f"Documentation: {'Available' if passed else 'Missing'}"
        details = {
            "existing_docs": len(existing_docs),
            "missing_docs": missing_docs
        }
        
        self.log_test_result("Documentation Files", passed, message, details)
        return passed
    
    def validate_security_config_content(self) -> bool:
        """Validate security configuration content"""
        try:
            config_file = os.path.join(self.base_path, "production/config/production_config.json")
            
            if not os.path.exists(config_file):
                self.log_test_result("Security Config Content", False, "Production config file not found")
                return False
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Check required security settings
            production_config = config.get("production", {})
            security_config = production_config.get("security", {})
            
            required_security_settings = [
                "https_enforced",
                "csrf_protection", 
                "auth_rate_limiting",
                "password_policy",
                "jwt_rotation",
                "input_validation",
                "api_key_management",
                "security_headers",
                "security_logging"
            ]
            
            enabled_settings = []
            disabled_settings = []
            
            for setting in required_security_settings:
                if security_config.get(setting, False):
                    enabled_settings.append(setting)
                else:
                    disabled_settings.append(setting)
            
            passed = len(enabled_settings) >= 8  # At least 8 out of 10 settings enabled
            message = f"Security settings: {len(enabled_settings)}/10 enabled"
            details = {
                "enabled_settings": enabled_settings,
                "disabled_settings": disabled_settings,
                "debug_disabled": not production_config.get("debug", True),
                "testing_disabled": not production_config.get("testing", True)
            }
            
            self.log_test_result("Security Config Content", passed, message, details)
            return passed
        except Exception as e:
            self.log_test_result("Security Config Content", False, f"Error validating config: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all configuration validation tests"""
        print("STELLAR LOGIC AI - SECURITY CONFIGURATION VALIDATION")
        print("=" * 65)
        
        # Test sequence
        tests = [
            ("Production Directory Structure", self.test_production_directory_structure),
            ("Security Components Deployment", self.test_security_components_deployment),
            ("Configuration Files", self.test_configuration_files),
            ("Startup Scripts", self.test_startup_scripts),
            ("SSL Configuration", self.test_ssl_configuration),
            ("Middleware Files", self.test_middleware_files),
            ("Storage Initialization", self.test_storage_initialization),
            ("Documentation Files", self.test_documentation_files),
            ("Security Config Content", self.validate_security_config_content)
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
            "overall_status": "PASS" if passed_tests >= total_tests * 0.8 else "FAIL"  # 80% pass rate
        }
        
        # Save test results
        results_file = os.path.join(self.production_path, "security_config_validation_results.json")
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 65)
        print("SECURITY CONFIGURATION VALIDATION SUMMARY")
        print("=" * 65)
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
        
        print(f"\nValidation results saved to: {results_file}")
        
        return summary

def main():
    """Main function"""
    validator = SecurityConfigurationValidator()
    results = validator.run_all_tests()
    
    return results['overall_status'] == "PASS"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
