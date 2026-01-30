#!/usr/bin/env python3
"""
Helm AI Performance Testing Runner
This script orchestrates various performance testing scenarios
"""

import os
import sys
import time
import json
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PerformanceTestRunner:
    """Manages and runs performance tests for Helm AI"""
    
    def __init__(self, config_file=None):
        self.config = self.load_config(config_file)
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        
    def load_config(self, config_file):
        """Load performance test configuration"""
        default_config = {
            "host": "http://localhost:5000",
            "scenarios": {
                "smoke": {
                    "users": 10,
                    "spawn_rate": 2,
                    "run_time": "60s",
                    "description": "Quick smoke test"
                },
                "load": {
                    "users": 50,
                    "spawn_rate": 5,
                    "run_time": "300s",
                    "description": "Standard load test"
                },
                "stress": {
                    "users": 200,
                    "spawn_rate": 20,
                    "run_time": "600s",
                    "description": "Stress test"
                },
                "spike": {
                    "users": 500,
                    "spawn_rate": 50,
                    "run_time": "120s",
                    "description": "Spike test"
                },
                "endurance": {
                    "users": 30,
                    "spawn_rate": 3,
                    "run_time": "3600s",
                    "description": "Endurance test (1 hour)"
                }
            },
            "user_types": {
                "regular": 70,
                "admin": 5,
                "api": 20,
                "mobile": 5
            }
        }
        
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                user_config = json.load(f)
            default_config.update(user_config)
        
        return default_config
    
    def run_scenario(self, scenario_name, user_type="regular"):
        """Run a specific performance test scenario"""
        scenario = self.config["scenarios"].get(scenario_name)
        if not scenario:
            logger.error(f"Scenario '{scenario_name}' not found")
            return False
        
        logger.info(f"Running scenario: {scenario_name}")
        logger.info(f"Description: {scenario['description']}")
        logger.info(f"Users: {scenario['users']}, Spawn rate: {scenario['spawn_rate']}")
        logger.info(f"Run time: {scenario['run_time']}")
        
        # Prepare command
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = self.results_dir / f"{scenario_name}_{user_type}_{timestamp}.csv"
        html_file = self.reports_dir / f"{scenario_name}_{user_type}_{timestamp}.html"
        log_file = self.results_dir / f"{scenario_name}_{user_type}_{timestamp}.log"
        
        cmd = [
            "locust",
            "-f", "locustfile.py",
            "--host", self.config["host"],
            "--users", str(scenario["users"]),
            "--spawn-rate", str(scenario["spawn_rate"]),
            "--run-time", scenario["run_time"],
            "--csv", str(csv_file),
            "--html", str(html_file),
            "--logfile", str(log_file),
            "--headless",
            f"--user-class={self.get_user_class(user_type)}"
        ]
        
        # Add user type weights if specified
        if user_type == "mixed":
            cmd.extend([
                "--user-class=HelmAIUser:70",
                "--user-class=AdminUser:5", 
                "--user-class=APIUser:20",
                "--user-class=MobileUser:5"
            ])
        
        logger.info(f"Command: {' '.join(cmd)}")
        
        # Run the test
        start_time = time.time()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
            end_time = time.time()
            
            # Log results
            logger.info(f"Test completed in {end_time - start_time:.2f} seconds")
            logger.info(f"CSV results: {csv_file}")
            logger.info(f"HTML report: {html_file}")
            
            if result.returncode == 0:
                logger.info("Test completed successfully")
                self.save_test_results(scenario_name, user_type, {
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": end_time - start_time,
                    "csv_file": str(csv_file),
                    "html_file": str(html_file),
                    "log_file": str(log_file),
                    "stdout": result.stdout,
                    "stderr": result.stderr
                })
                return True
            else:
                logger.error(f"Test failed with return code {result.returncode}")
                logger.error(f"STDERR: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error running test: {e}")
            return False
    
    def get_user_class(self, user_type):
        """Get the appropriate user class for the user type"""
        user_classes = {
            "regular": "HelmAIUser",
            "admin": "AdminUser", 
            "api": "APIUser",
            "mobile": "MobileUser",
            "enterprise": "EnterpriseUser"
        }
        return user_classes.get(user_type, "HelmAIUser")
    
    def save_test_results(self, scenario_name, user_type, results):
        """Save test results to JSON file"""
        result_file = self.results_dir / f"{scenario_name}_{user_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_results.json"
        
        with open(result_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to: {result_file}")
    
    def run_all_scenarios(self):
        """Run all configured scenarios"""
        logger.info("Starting comprehensive performance test suite")
        
        results = {}
        total_start = time.time()
        
        for scenario_name in self.config["scenarios"]:
            logger.info(f"\n{'='*60}")
            logger.info(f"Running scenario: {scenario_name}")
            logger.info(f"{'='*60}")
            
            # Run with mixed user types
            success = self.run_scenario(scenario_name, "mixed")
            results[scenario_name] = {
                "success": success,
                "timestamp": datetime.now().isoformat()
            }
            
            # Wait between scenarios
            if scenario_name != list(self.config["scenarios"].keys())[-1]:
                logger.info("Waiting 30 seconds before next scenario...")
                time.sleep(30)
        
        total_end = time.time()
        total_duration = total_end - total_start
        
        logger.info(f"\n{'='*60}")
        logger.info("PERFORMANCE TEST SUITE COMPLETED")
        logger.info(f"{'='*60}")
        logger.info(f"Total duration: {total_duration:.2f} seconds")
        
        # Generate summary report
        self.generate_summary_report(results, total_duration)
        
        return results
    
    def generate_summary_report(self, results, total_duration):
        """Generate a summary report of all tests"""
        summary = {
            "test_suite": "Helm AI Performance Tests",
            "timestamp": datetime.now().isoformat(),
            "total_duration": total_duration,
            "scenarios": results,
            "host": self.config["host"],
            "summary": {
                "total_scenarios": len(results),
                "successful_scenarios": sum(1 for r in results.values() if r["success"]),
                "failed_scenarios": sum(1 for r in results.values() if not r["success"])
            }
        }
        
        summary_file = self.results_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Summary report saved to: {summary_file}")
        
        # Print summary
        logger.info(f"\nSUMMARY:")
        logger.info(f"Total scenarios: {summary['summary']['total_scenarios']}")
        logger.info(f"Successful: {summary['summary']['successful_scenarios']}")
        logger.info(f"Failed: {summary['summary']['failed_scenarios']}")
        logger.info(f"Success rate: {summary['summary']['successful_scenarios']/summary['summary']['total_scenarios']*100:.1f}%")
    
    def run_smoke_test(self):
        """Run a quick smoke test"""
        logger.info("Running smoke test...")
        return self.run_scenario("smoke", "regular")
    
    def run_load_test(self):
        """Run standard load test"""
        logger.info("Running load test...")
        return self.run_scenario("load", "mixed")
    
    def run_stress_test(self):
        """Run stress test"""
        logger.info("Running stress test...")
        return self.run_scenario("stress", "mixed")
    
    def check_server_health(self):
        """Check if the target server is healthy"""
        import requests
        
        try:
            response = requests.get(f"{self.config['host']}/api/health", timeout=10)
            if response.status_code == 200:
                logger.info("Server health check passed")
                return True
            else:
                logger.error(f"Server health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Server health check error: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Helm AI Performance Test Runner")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--scenario", help="Specific scenario to run")
    parser.add_argument("--user-type", default="regular", 
                       choices=["regular", "admin", "api", "mobile", "enterprise", "mixed"],
                       help="User type to simulate")
    parser.add_argument("--smoke", action="store_true", help="Run smoke test only")
    parser.add_argument("--load", action="store_true", help="Run load test only")
    parser.add_argument("--stress", action="store_true", help="Run stress test only")
    parser.add_argument("--all", action="store_true", help="Run all scenarios")
    parser.add_argument("--host", help="Override target host")
    parser.add_argument("--check-health", action="store_true", help="Check server health only")
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = PerformanceTestRunner(args.config)
    
    # Override host if specified
    if args.host:
        runner.config["host"] = args.host
    
    # Check server health first
    if not runner.check_server_health():
        logger.error("Server health check failed. Exiting.")
        sys.exit(1)
    
    # Run appropriate tests
    if args.check_health:
        logger.info("Health check completed successfully")
        sys.exit(0)
    elif args.smoke:
        success = runner.run_smoke_test()
    elif args.load:
        success = runner.run_load_test()
    elif args.stress:
        success = runner.run_stress_test()
    elif args.scenario:
        success = runner.run_scenario(args.scenario, args.user_type)
    elif args.all:
        success = runner.run_all_scenarios()
    else:
        logger.error("Please specify a test type: --smoke, --load, --stress, --scenario, or --all")
        sys.exit(1)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
