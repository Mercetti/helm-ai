#!/usr/bin/env python3
"""
Stellar Logic AI - Complete Security System Validation
Final validation of all security components working together
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

class CompleteSecurityValidator:
    """Complete validation of Stellar Logic AI security system"""
    
    def __init__(self):
        self.base_path = "c:/Users/merce/Documents/helm-ai"
        self.production_path = "c:/Users/merce/Documents/helm-ai/production"
        self.validation_results = []
    
    def log_validation(self, component: str, status: str, message: str, details: Dict[str, Any] = None):
        """Log validation result"""
        result = {
            "component": component,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.validation_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {component}: {message}")
        
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")
    
    def validate_security_components_integration(self) -> bool:
        """Validate all security components are integrated"""
        integration_file = os.path.join(self.production_path, "security/stellar_logic_ai_security.py")
        
        if not os.path.exists(integration_file):
            self.log_validation("Security Integration", "FAIL", "Main security integration file not found")
            return False
        
        # Check integration file content
        with open(integration_file, 'r') as f:
            content = f.read()
        
        # Check for key integration components
        required_components = [
            "StellarSecurityManager",
            "create_stellar_security",
            "stellar_secure_endpoint",
            "HTTPS/TLS",
            "CSRF Protection",
            "Rate Limiting",
            "Password Policy",
            "JWT Rotation",
            "Input Validation",
            "API Key Management"
        ]
        
        found_components = []
        missing_components = []
        
        for component in required_components:
            if component.lower().replace(" ", "_") in content.lower() or component in content:
                found_components.append(component)
            else:
                missing_components.append(component)
        
        passed = len(missing_components) == 0
        message = f"Security integration: {'Complete' if passed else f'Missing {len(missing_components)} components'}"
        details = {
            "found_components": len(found_components),
            "missing_components": missing_components
        }
        
        self.log_validation("Security Components Integration", "PASS" if passed else "FAIL", message, details)
        return passed
    
    def validate_production_readiness(self) -> bool:
        """Validate production readiness"""
        readiness_checks = {
            "production_config": os.path.exists(os.path.join(self.production_path, "config/production_config.json")),
            "security_components": all([
                os.path.exists(os.path.join(self.production_path, "security", f))
                for f in ["stellar_logic_ai_security.py", "security_https_middleware.py"]
            ]),
            "startup_script": os.path.exists(os.path.join(self.production_path, "start_stellar_security.py")),
            "https_startup": os.path.exists(os.path.join(self.production_path, "start_stellar_security_https.py")),
            "monitoring_config": os.path.exists(os.path.join(self.production_path, "monitoring/security_monitoring.json")),
            "ssl_setup": os.path.exists(os.path.join(self.production_path, "ssl/generate_certificates.bat")),
            "rate_limiting_config": os.path.exists(os.path.join(self.production_path, "config/rate_limiting_config.json")),
            "csrf_config": os.path.exists(os.path.join(self.production_path, "config/csrf_protection_config.json"))
        }
        
        passed_checks = [k for k, v in readiness_checks.items() if v]
        failed_checks = [k for k, v in readiness_checks.items() if not v]
        
        passed = len(failed_checks) == 0
        message = f"Production readiness: {'Ready' if passed else f'{len(failed_checks)} issues remaining'}"
        details = {
            "passed_checks": len(passed_checks),
            "failed_checks": failed_checks,
            "total_checks": len(readiness_checks)
        }
        
        self.log_validation("Production Readiness", "PASS" if passed else "FAIL", message, details)
        return passed
    
    def validate_security_coverage(self) -> bool:
        """Validate comprehensive security coverage"""
        try:
            config_file = os.path.join(self.production_path, "config/production_config.json")
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            security_config = config.get("production", {}).get("security", {})
            
            # Calculate security coverage
            total_security_features = 10
            enabled_features = sum(1 for v in security_config.values() if v)
            coverage_percentage = (enabled_features / total_security_features) * 100
            
            passed = coverage_percentage >= 90  # 90% coverage required
            message = f"Security coverage: {coverage_percentage:.1f}% ({enabled_features}/{total_security_features} features)"
            details = {
                "coverage_percentage": coverage_percentage,
                "enabled_features": enabled_features,
                "total_features": total_security_features,
                "security_settings": security_config
            }
            
            self.log_validation("Security Coverage", "PASS" if passed else "FAIL", message, details)
            return passed
        except Exception as e:
            self.log_validation("Security Coverage", "FAIL", f"Error calculating coverage: {str(e)}")
            return False
    
    def validate_monitoring_setup(self) -> bool:
        """Validate monitoring and alerting setup"""
        monitoring_checks = {
            "monitoring_config": os.path.exists(os.path.join(self.production_path, "monitoring/security_monitoring.json")),
            "initial_report": os.path.exists(os.path.join(self.production_path, "monitoring/initial_security_report.json")),
            "monitoring_script": os.path.exists(os.path.join(self.production_path, "start_monitoring.py")),
            "log_directory": os.path.exists(os.path.join(self.production_path, "logs")),
            "storage_directory": os.path.exists(os.path.join(self.production_path, "storage"))
        }
        
        passed_checks = [k for k, v in monitoring_checks.items() if v]
        failed_checks = [k for k, v in monitoring_checks.items() if not v]
        
        passed = len(passed_checks) >= 4  # At least 4 out of 5 checks
        message = f"Monitoring setup: {'Complete' if passed else f'Partial ({len(passed_checks)}/5)'}"
        details = {
            "passed_checks": len(passed_checks),
            "failed_checks": failed_checks
        }
        
        self.log_validation("Monitoring Setup", "PASS" if passed else "WARN", message, details)
        return passed
    
    def validate_ssl_https_readiness(self) -> bool:
        """Validate SSL/HTTPS readiness"""
        ssl_checks = {
            "generation_script": os.path.exists(os.path.join(self.production_path, "ssl/generate_certificates.bat")),
            "linux_script": os.path.exists(os.path.join(self.production_path, "ssl/generate_certificates.sh")),
            "https_startup": os.path.exists(os.path.join(self.production_path, "start_stellar_security_https.py")),
            "ssl_documentation": os.path.exists(os.path.join(self.production_path, "SSL_HTTPS_SETUP.md"))
        }
        
        passed_checks = [k for k, v in ssl_checks.items() if v]
        failed_checks = [k for k, v in ssl_checks.items() if not v]
        
        passed = len(passed_checks) >= 3  # At least 3 out of 4 checks
        message = f"SSL/HTTPS readiness: {'Ready' if passed else f'Partial ({len(passed_checks)}/4)'}"
        details = {
            "passed_checks": len(passed_checks),
            "failed_checks": failed_checks
        }
        
        self.log_validation("SSL/HTTPS Readiness", "PASS" if passed else "WARN", message, details)
        return passed
    
    def validate_rate_limiting_csrf_setup(self) -> bool:
        """Validate rate limiting and CSRF protection setup"""
        protection_checks = {
            "rate_limiting_config": os.path.exists(os.path.join(self.production_path, "config/rate_limiting_config.json")),
            "csrf_config": os.path.exists(os.path.join(self.production_path, "config/csrf_protection_config.json")),
            "rate_limiting_middleware": os.path.exists(os.path.join(self.production_path, "middleware/rate_limiting_middleware.py")),
            "csrf_middleware": os.path.exists(os.path.join(self.production_path, "middleware/csrf_middleware.py")),
            "rate_limiting_storage": os.path.exists(os.path.join(self.production_path, "storage/rate_limiting/rate_limit_data.json")),
            "csrf_storage": os.path.exists(os.path.join(self.production_path, "storage/csrf/csrf_data.json")),
            "integration_script": os.path.exists(os.path.join(self.production_path, "initialize_security_middleware.py"))
        }
        
        passed_checks = [k for k, v in protection_checks.items() if v]
        failed_checks = [k for k, v in protection_checks.items() if not v]
        
        passed = len(passed_checks) >= 6  # At least 6 out of 7 checks
        message = f"Rate limiting & CSRF setup: {'Complete' if passed else f'Partial ({len(passed_checks)}/7)'}"
        details = {
            "passed_checks": len(passed_checks),
            "failed_checks": failed_checks
        }
        
        self.log_validation("Rate Limiting & CSRF Setup", "PASS" if passed else "WARN", message, details)
        return passed
    
    def calculate_overall_security_score(self) -> Dict[str, Any]:
        """Calculate overall security score"""
        try:
            # Load configuration validation results
            config_results_file = os.path.join(self.production_path, "security_config_validation_results.json")
            if os.path.exists(config_results_file):
                with open(config_results_file, 'r') as f:
                    config_results = json.load(f)
                config_score = config_results.get("success_rate", 0) * 100
            else:
                config_score = 0
            
            # Calculate component integration score
            integration_score = 100 if self.validate_security_components_integration() else 0
            
            # Calculate production readiness score
            readiness_score = 100 if self.validate_production_readiness() else 0
            
            # Calculate security coverage score
            coverage_score = 0
            try:
                config_file = os.path.join(self.production_path, "config/production_config.json")
                with open(config_file, 'r') as f:
                    config = json.load(f)
                security_config = config.get("production", {}).get("security", {})
                enabled_features = sum(1 for v in security_config.values() if v)
                coverage_score = (enabled_features / 10) * 100
            except:
                coverage_score = 0
            
            # Calculate monitoring score
            monitoring_score = 100 if self.validate_monitoring_setup() else 50
            
            # Calculate SSL/HTTPS score
            ssl_score = 100 if self.validate_ssl_https_readiness() else 50
            
            # Calculate rate limiting/CSRF score
            protection_score = 100 if self.validate_rate_limiting_csrf_setup() else 50
            
            # Calculate weighted overall score
            weights = {
                "configuration": 0.2,
                "integration": 0.2,
                "readiness": 0.2,
                "coverage": 0.15,
                "monitoring": 0.1,
                "ssl": 0.1,
                "protection": 0.05
            }
            
            overall_score = (
                config_score * weights["configuration"] +
                integration_score * weights["integration"] +
                readiness_score * weights["readiness"] +
                coverage_score * weights["coverage"] +
                monitoring_score * weights["monitoring"] +
                ssl_score * weights["ssl"] +
                protection_score * weights["protection"]
            )
            
            return {
                "overall_score": overall_score,
                "component_scores": {
                    "configuration": config_score,
                    "integration": integration_score,
                    "readiness": readiness_score,
                    "coverage": coverage_score,
                    "monitoring": monitoring_score,
                    "ssl": ssl_score,
                    "protection": protection_score
                },
                "security_grade": self.get_security_grade(overall_score)
            }
        except Exception as e:
            return {
                "overall_score": 0,
                "error": str(e),
                "security_grade": "F"
            }
    
    def get_security_grade(self, score: float) -> str:
        """Get security grade based on score"""
        if score >= 95:
            return "A+ (Enterprise Grade)"
        elif score >= 90:
            return "A (Excellent)"
        elif score >= 85:
            return "B+ (Very Good)"
        elif score >= 80:
            return "B (Good)"
        elif score >= 70:
            return "C (Fair)"
        elif score >= 60:
            return "D (Poor)"
        else:
            return "F (Critical)"
    
    def generate_final_validation_report(self) -> Dict[str, Any]:
        """Generate final validation report"""
        print("STELLAR LOGIC AI - COMPLETE SECURITY SYSTEM VALIDATION")
        print("=" * 70)
        
        # Run all validations
        validations = [
            ("Security Components Integration", self.validate_security_components_integration),
            ("Production Readiness", self.validate_production_readiness),
            ("Security Coverage", self.validate_security_coverage),
            ("Monitoring Setup", self.validate_monitoring_setup),
            ("SSL/HTTPS Readiness", self.validate_ssl_https_readiness),
            ("Rate Limiting & CSRF Setup", self.validate_rate_limiting_csrf_setup)
        ]
        
        for validation_name, validation_func in validations:
            try:
                validation_func()
            except Exception as e:
                self.log_validation(validation_name, "FAIL", f"Validation failed: {str(e)}")
        
        # Calculate overall security score
        security_score = self.calculate_overall_security_score()
        
        # Generate final report
        passed_validations = len([v for v in self.validation_results if v["status"] == "PASS"])
        warn_validations = len([v for v in self.validation_results if v["status"] == "WARN"])
        failed_validations = len([v for v in self.validation_results if v["status"] == "FAIL"])
        total_validations = len(self.validation_results)
        
        final_report = {
            "timestamp": datetime.now().isoformat(),
            "system": "Stellar Logic AI",
            "report_type": "complete_security_validation",
            "validation_summary": {
                "total_validations": total_validations,
                "passed_validations": passed_validations,
                "warn_validations": warn_validations,
                "failed_validations": failed_validations,
                "success_rate": (passed_validations / total_validations) * 100 if total_validations > 0 else 0
            },
            "security_score": security_score,
            "validation_results": self.validation_results,
            "overall_status": "PRODUCTION_READY" if security_score["overall_score"] >= 85 else "NEEDS_IMPROVEMENT",
            "recommendations": self.generate_recommendations(security_score, self.validation_results)
        }
        
        # Save final report
        report_file = os.path.join(self.production_path, "complete_security_validation_report.json")
        with open(report_file, 'w') as f:
            json.dump(final_report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 70)
        print("COMPLETE SECURITY VALIDATION SUMMARY")
        print("=" * 70)
        print(f"Overall Security Score: {security_score['overall_score']:.1f}%")
        print(f"Security Grade: {security_score['security_grade']}")
        print(f"Overall Status: {final_report['overall_status']}")
        print(f"Validations Passed: {passed_validations}/{total_validations}")
        
        print("\nComponent Scores:")
        component_scores = security_score.get("component_scores", {})
        if component_scores:
            for component, score in component_scores.items():
                print(f"  {component.title()}: {score:.1f}%")
        else:
            print("  Component scores not available due to integration validation error")
        
        if final_report["recommendations"]:
            print("\nRecommendations:")
            for rec in final_report["recommendations"]:
                print(f"  - {rec}")
        
        print(f"\nFinal validation report saved to: {report_file}")
        
        return final_report
    
    def generate_recommendations(self, security_score: Dict[str, Any], validation_results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Analyze validation results
        for result in validation_results:
            if result["status"] == "FAIL":
                recommendations.append(f"Fix {result['component']}: {result['message']}")
            elif result["status"] == "WARN":
                recommendations.append(f"Improve {result['component']}: {result['message']}")
        
        # Analyze security scores
        component_scores = security_score.get("component_scores", {})
        
        if component_scores.get("configuration", 0) < 90:
            recommendations.append("Complete security configuration setup")
        
        if component_scores.get("monitoring", 0) < 90:
            recommendations.append("Enhance monitoring and alerting setup")
        
        if component_scores.get("ssl", 0) < 90:
            recommendations.append("Complete SSL certificate generation")
        
        if component_scores.get("protection", 0) < 90:
            recommendations.append("Finalize rate limiting and CSRF protection")
        
        # General recommendations
        if security_score["overall_score"] >= 90:
            recommendations.append("System is production-ready - proceed with deployment")
        elif security_score["overall_score"] >= 80:
            recommendations.append("System is nearly ready - address minor issues")
        else:
            recommendations.append("System needs significant improvements before production")
        
        return recommendations

def main():
    """Main function"""
    validator = CompleteSecurityValidator()
    report = validator.generate_final_validation_report()
    
    return report["overall_status"] == "PRODUCTION_READY"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
