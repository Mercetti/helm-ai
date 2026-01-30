#!/usr/bin/env python3
"""
Test script to validate the performance testing framework
"""

import sys
import os
import subprocess
from pathlib import Path

def test_framework_setup():
    """Test that the performance testing framework is properly set up"""
    print("🧪 Testing Performance Testing Framework Setup...")
    
    # Check required files exist
    required_files = [
        "locustfile.py",
        "run_performance_tests.py", 
        "performance_config.py",
        "locust.conf",
        "requirements.txt",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
    
    # Test configuration loading
    try:
        from performance_config import PERFORMANCE_CONFIG
        print("✅ Configuration loaded successfully")
        
        # Validate configuration structure
        required_keys = ["host", "scenarios", "user_types", "thresholds"]
        for key in required_keys:
            if key not in PERFORMANCE_CONFIG:
                print(f"❌ Missing configuration key: {key}")
                return False
        
        print("✅ Configuration structure valid")
        
    except ImportError as e:
        print(f"❌ Failed to load configuration: {e}")
        return False
    
    # Test Locust installation
    try:
        result = subprocess.run([sys.executable, "-c", "import locust"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Locust is installed")
        else:
            print("❌ Locust is not installed")
            return False
    except Exception as e:
        print(f"❌ Error checking Locust: {e}")
        return False
    
    # Test locustfile syntax
    try:
        result = subprocess.run([sys.executable, "-m", "py_compile", "locustfile.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Locustfile syntax is valid")
        else:
            print(f"❌ Locustfile syntax error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking locustfile: {e}")
        return False
    
    # Test runner script syntax
    try:
        result = subprocess.run([sys.executable, "-m", "py_compile", "run_performance_tests.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Runner script syntax is valid")
        else:
            print(f"❌ Runner script syntax error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking runner script: {e}")
        return False
    
    print("🎉 Performance testing framework setup is valid!")
    return True

def test_configuration_scenarios():
    """Test that all scenarios in configuration are valid"""
    print("\n🧪 Testing Configuration Scenarios...")
    
    try:
        from performance_config import PERFORMANCE_CONFIG
        scenarios = PERFORMANCE_CONFIG["scenarios"]
        
        for name, scenario in scenarios.items():
            # Check required scenario fields
            required_fields = ["users", "spawn_rate", "run_time", "description"]
            for field in required_fields:
                if field not in scenario:
                    print(f"❌ Scenario '{name}' missing field: {field}")
                    return False
            
            # Validate values
            if scenario["users"] <= 0:
                print(f"❌ Scenario '{name}' has invalid users count: {scenario['users']}")
                return False
            
            if scenario["spawn_rate"] <= 0:
                print(f"❌ Scenario '{name}' has invalid spawn rate: {scenario['spawn_rate']}")
                return False
            
            if not scenario["run_time"].endswith(('s', 'm', 'h')):
                print(f"❌ Scenario '{name}' has invalid run time format: {scenario['run_time']}")
                return False
            
            print(f"✅ Scenario '{name}' is valid")
        
        print("🎉 All configuration scenarios are valid!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing scenarios: {e}")
        return False

def test_user_classes():
    """Test that all user classes in locustfile are valid"""
    print("\n🧪 Testing User Classes...")
    
    try:
        # Import locustfile to check user classes
        sys.path.insert(0, '.')
        import locustfile
        
        user_classes = [
            "HelmAIUser",
            "AdminUser", 
            "APIUser",
            "MobileUser",
            "EnterpriseUser"
        ]
        
        for class_name in user_classes:
            if not hasattr(locustfile, class_name):
                print(f"❌ User class '{class_name}' not found")
                return False
            else:
                print(f"✅ User class '{class_name}' found")
        
        print("🎉 All user classes are valid!")
        return True
        
    except ImportError as e:
        print(f"❌ Error importing locustfile: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing user classes: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Helm AI Performance Testing Framework Validation")
    print("=" * 60)
    
    tests = [
        test_framework_setup,
        test_configuration_scenarios,
        test_user_classes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The performance testing framework is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before using the framework.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
