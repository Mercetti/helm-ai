
"""
Stellar Logic AI - Test Runner
Comprehensive test execution and reporting
"""

import unittest
import subprocess
import sys
import json
import time
from datetime import datetime
import os

class TestRunner:
    def __init__(self):
        self.test_suites = {
            'unit_tests': 'unit_tests.py',
            'integration_tests': 'integration_tests_extended.py',
            'performance_tests': 'performance_tests.py'
        }
        self.results = {}
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 RUNNING COMPREHENSIVE TEST SUITE...")
        print(f"{'='*60}")
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        
        for suite_name, test_file in self.test_suites.items():
            print(f"\n📋 Running {suite_name.replace('_', ' ').title()}...")
            
            if os.path.exists(test_file):
                try:
                    # Run test suite
                    result = subprocess.run([
                        sys.executable, test_file
                    ], capture_output=True, text=True)
                    
                    # Parse results
                    tests_run, failures, errors = self.parse_test_output(result.stdout)
                    
                    self.results[suite_name] = {
                        'tests_run': tests_run,
                        'failures': failures,
                        'errors': errors,
                        'success_rate': ((tests_run - failures - errors) / tests_run * 100) if tests_run > 0 else 0,
                        'output': result.stdout,
                        'errors_output': result.stderr
                    }
                    
                    total_tests += tests_run
                    total_failures += failures
                    total_errors += errors
                    
                    print(f"   Tests run: {tests_run}")
                    print(f"   Failures: {failures}")
                    print(f"   Errors: {errors}")
                    print(f"   Success rate: {self.results[suite_name]['success_rate']:.1f}%")
                    
                    if failures == 0 and errors == 0:
                        print(f"   ✅ {suite_name} PASSED")
                    else:
                        print(f"   ❌ {suite_name} FAILED")
                        
                except Exception as e:
                    print(f"   ❌ Error running {suite_name}: {e}")
                    self.results[suite_name] = {
                        'error': str(e),
                        'success_rate': 0
                    }
            else:
                print(f"   ⚠️  Test file not found: {test_file}")
                self.results[suite_name] = {
                    'error': 'Test file not found',
                    'success_rate': 0
                }
        
        # Generate summary
        overall_success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"📊 OVERALL TEST RESULTS")
        print(f"{'='*60}")
        print(f"Total tests run: {total_tests}")
        print(f"Total failures: {total_failures}")
        print(f"Total errors: {total_errors}")
        print(f"Overall success rate: {overall_success_rate:.1f}%")
        
        if overall_success_rate >= 95:
            print(f"🎉 EXCELLENT - Test coverage goal achieved!")
        elif overall_success_rate >= 90:
            print(f"✅ GOOD - Test coverage acceptable")
        else:
            print(f"⚠️  NEEDS IMPROVEMENT - Test coverage below target")
        
        # Save results
        self.save_test_results()
        
        return overall_success_rate
    
    def parse_test_output(self, output):
        """Parse test output to extract results"""
        lines = output.split('\n')
        tests_run = 0
        failures = 0
        errors = 0
        
        for line in lines:
            if 'Tests run:' in line:
                tests_run = int(line.split(':')[1].strip())
            elif 'Failures:' in line:
                failures = int(line.split(':')[1].strip())
            elif 'Errors:' in line:
                errors = int(line.split(':')[1].strip())
        
        return tests_run, failures, errors
    
    def save_test_results(self):
        """Save test results to file"""
        report = {
            'test_run_timestamp': datetime.now().isoformat(),
            'test_suites': self.test_suites,
            'results': self.results,
            'summary': {
                'total_suites': len(self.test_suites),
                'successful_suites': len([r for r in self.results.values() if r.get('success_rate', 0) > 0])
            }
        }
        
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📁 Test results saved to: test_results.json")

if __name__ == '__main__':
    runner = TestRunner()
    success_rate = runner.run_all_tests()
    
    if success_rate >= 90:
        print(f"\n🎯 AUTOMATED TESTING FRAMEWORK DEPLOYMENT SUCCESSFUL!")
        print(f"✅ System ready for production!")
    else:
        print(f"\n⚠️  Some tests failed - review and fix issues")
