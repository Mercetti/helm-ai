#!/usr/bin/env python3
"""
Helm AI Performance Testing Script
Runs comprehensive performance tests and generates reports
"""

import os
import sys
import json
import argparse
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tests.performance.benchmarks import (
    create_database_suite, create_api_suite, create_cache_suite,
    run_performance_tests
)
from tests.performance.locustfile import PERFORMANCE_CONFIG
from monitoring.performance_monitoring import start_performance_monitoring, stop_performance_monitoring

def run_performance_test(test_type: str = "all", iterations: int = 100, duration: int = 300):
    """Run performance tests"""
    print(f"🚀 Starting Helm AI Performance Tests")
    print("=" * 50)
    
    # Update configuration
    PERFORMANCE_CONFIG["max_users"] = iterations
    PERFORMANCE_CONFIG["test_duration"] = duration
    
    print(f"Configuration:")
    print(f"  - Max Users: {PERFORMANCE_CONFIG['max_users']}")
    print(f"  - Test Duration: {PERFORMANCE_CONFIG['test_duration']} seconds")
    print(f"  - Base URL: {PERFORMANCE_CONFIG['host']}")
    print()
    
    # Start performance monitoring
    start_performance_monitoring()
    
    try:
        if test_type == "all":
            print("🔄 Running all performance tests...")
            report = run_performance_tests()
        elif test_type == "database":
            print("🗄️ Running database performance tests...")
            suite = create_database_suite()
            runner = BenchmarkRunner()
            result = runner.run_suite(suite)
            print(f"Database test completed: {result.get_summary()}")
        elif test_type == "api":
            print("🌐 Running API performance tests...")
            suite = create_api_suite()
            runner = BenchmarkRunner()
            result = runner.run_suite(suite)
            print(f"API test completed: {result.get_summary()}")
        elif test_type == "cache":
            print("💾 Running cache performance tests...")
            suite = create_cache_suite()
            runner = BenchmarkRunner()
            result = runner.run_suite(suite)
            print(f"Cache test completed: {result.get_summary()}")
        else:
            print(f"Unknown test type: {test_type}")
            return
        
        print("\n📊 Performance Test Summary:")
        if isinstance(report, dict):
            print(f"  Total Tests: {report['total_benchmarks']}")
            print(f"  Duration: {report.get('duration', 0):.2f}s")
            
            for suite in report.get('suites', []):
                print(f"\n{suite['suite_name']}:")
                print(f"  Tests: {suite['total_benchmarks']}")
                print(f"  Duration: {suite.get('duration', 0):.2f}s")
                
                # Show top slowest tests
                top_tests = sorted(
                    suite.get('by_type', {}).items(),
                    key=lambda x: x[1]['avg_time'],
                    reverse=True
                )
                
                if top_tests:
                    print(f"  Top 3 Slowest Tests:")
                    for test_type, stats in top_tests[:3]:
                        print(f"    {test_type}: {stats['avg_time']:.2f}ms")
        else:
            print("No report generated")
        
        print("\n✅ Performance tests completed successfully!")
        
    finally:
        # Stop performance monitoring
        stop_performance_monitoring()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Helm AI Performance Testing")
    parser.add_argument(
        '--test-type',
        choices=['all', 'database', 'api', 'cache'],
        default='all',
        help='Type of performance test to run'
    )
    parser.add_argument(
        '--iterations',
        type=int,
        default=100,
        help='Number of iterations for each test'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=300,
        help='Duration of test in seconds'
    )
    
    args = parser.parse_args()
    
    run_performance_test(args.test_type, args.iterations, args.duration)

if __name__ == "__main__":
    main()
