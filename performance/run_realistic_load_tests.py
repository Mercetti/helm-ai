#!/usr/bin/env python3
"""
Realistic Load Testing Runner for Helm AI
Uses realistic traffic patterns and user behavior scenarios
"""

import sys
import os
import time
import json
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from traffic_patterns import TrafficPatternGenerator, LoadTestScenarioGenerator
from realistic_scenarios import BusinessUser, CasualUser, PowerUser, MobileAppUser

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('realistic_load_tests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealisticLoadTestRunner:
    """
    Runs realistic load tests based on traffic patterns and user behavior
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self.load_config(config_file)
        self.traffic_generator = TrafficPatternGenerator()
        self.scenario_generator = LoadTestScenarioGenerator()
        self.results_dir = Path("realistic_results")
        self.results_dir.mkdir(exist_ok=True)
        self.reports_dir = Path("realistic_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
    def load_config(self, config_file: Optional[str]) -> Dict:
        """Load configuration for realistic load tests"""
        default_config = {
            "host": "http://localhost:5000",
            "base_users": 100,
            "scenarios": {
                "daily_pattern": {
                    "enabled": True,
                    "description": "Daily traffic pattern simulation"
                },
                "business_hours": {
                    "enabled": True,
                    "description": "Business hours focused testing"
                },
                "weekend_pattern": {
                    "enabled": True,
                    "description": "Weekend traffic pattern"
                },
                "product_launch": {
                    "enabled": True,
                    "description": "Product launch high traffic scenario"
                },
                "maintenance_window": {
                    "enabled": True,
                    "description": "Maintenance window low traffic"
                },
                "burst_traffic": {
                    "enabled": True,
                    "description": "Sudden traffic burst simulation"
                },
                "gradual_ramp": {
                    "enabled": True,
                    "description": "Gradual user ramp-up scenario"
                }
            },
            "user_types": {
                "BusinessUser": 60,
                "CasualUser": 25,
                "PowerUser": 10,
                "MobileAppUser": 5
            },
            "monitoring": {
                "enable_metrics": True,
                "metrics_interval": 30,
                "save_user_journeys": True
            },
            "reporting": {
                "generate_charts": True,
                "compare_patterns": True,
                "export_csv": True
            }
        }
        
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                user_config = json.load(f)
            default_config.update(user_config)
        
        return default_config
    
    def run_daily_pattern_test(self, date: Optional[datetime] = None) -> bool:
        """Run daily traffic pattern test"""
        if date is None:
            date = datetime.now()
        
        logger.info(f"Running daily pattern test for {date.strftime('%Y-%m-%d')}")
        
        # Generate daily pattern
        pattern = self.traffic_generator.generate_daily_pattern(date, self.config["base_users"])
        
        # Run hourly tests
        results = []
        for hour, users in enumerate(pattern["hourly_users"]):
            if users > 0:
                logger.info(f"Running hour {hour:02d}:00 with {users} users")
                
                result = self.run_hourly_test(hour, users, f"daily_pattern_hour_{hour}")
                if result:
                    results.append({
                        "hour": hour,
                        "users": users,
                        "result": result
                    })
                
                # Wait between hourly tests
                if hour < 23:
                    time.sleep(60)  # 1 minute between tests
        
        # Save results
        self.save_daily_results(date, pattern, results)
        
        return len(results) > 0
    
    def run_business_hours_test(self, date: Optional[datetime] = None) -> bool:
        """Run business hours focused test"""
        if date is None:
            date = datetime.now()
        
        logger.info(f"Running business hours test for {date.strftime('%Y-%m-%d')}")
        
        # Generate business hours pattern
        pattern = self.scenario_generator.generate_business_hours_scenario(date)
        
        # Focus on business hours (9am-5pm)
        business_hours = range(9, 17)
        results = []
        
        for hour in business_hours:
            users = pattern["hourly_users"][hour]
            if users > 0:
                logger.info(f"Running business hour {hour:02d}:00 with {users} users")
                
                result = self.run_hourly_test(hour, users, f"business_hours_hour_{hour}")
                if result:
                    results.append({
                        "hour": hour,
                        "users": users,
                        "result": result
                    })
        
        # Save results
        self.save_scenario_results("business_hours", date, pattern, results)
        
        return len(results) > 0
    
    def run_weekend_pattern_test(self, date: Optional[datetime] = None) -> bool:
        """Run weekend traffic pattern test"""
        if date is None:
            # Get next Saturday
            today = datetime.now()
            days_until_saturday = (5 - today.weekday()) % 7
            date = today + timedelta(days=days_until_saturday)
        
        logger.info(f"Running weekend pattern test for {date.strftime('%Y-%m-%d')}")
        
        # Generate weekend pattern
        pattern = self.scenario_generator.generate_weekend_scenario(date)
        
        # Focus on evening hours (6pm-10pm)
        evening_hours = range(18, 23)
        results = []
        
        for hour in evening_hours:
            users = pattern["hourly_users"][hour]
            if users > 0:
                logger.info(f"Running weekend evening {hour:02d}:00 with {users} users")
                
                result = self.run_hourly_test(hour, users, f"weekend_hour_{hour}")
                if result:
                    results.append({
                        "hour": hour,
                        "users": users,
                        "result": result
                    })
        
        # Save results
        self.save_scenario_results("weekend_pattern", date, pattern, results)
        
        return len(results) > 0
    
    def run_product_launch_test(self, date: Optional[datetime] = None) -> bool:
        """Run product launch high traffic test"""
        if date is None:
            date = datetime.now()
        
        logger.info(f"Running product launch test for {date.strftime('%Y-%m-%d')}")
        
        # Generate product launch pattern
        pattern = self.scenario_generator.generate_product_launch_scenario(date)
        
        # Run continuous test for peak hours
        peak_hours = [pattern["peak_hour"]]
        
        # Add adjacent hours for comprehensive testing
        for offset in [-1, 1]:
            adj_hour = (pattern["peak_hour"] + offset) % 24
            if adj_hour not in peak_hours:
                peak_hours.append(adj_hour)
        
        results = []
        
        for hour in peak_hours:
            users = pattern["hourly_users"][hour]
            if users > 0:
                logger.info(f"Running product launch hour {hour:02d}:00 with {users} users")
                
                # Use shorter run time for high traffic
                result = self.run_hourly_test(hour, users, f"product_launch_hour_{hour}", run_time="1800s")
                if result:
                    results.append({
                        "hour": hour,
                        "users": users,
                        "result": result
                    })
        
        # Save results
        self.save_scenario_results("product_launch", date, pattern, results)
        
        return len(results) > 0
    
    def run_burst_traffic_test(self, burst_factor: float = 3.0, duration_minutes: int = 30) -> bool:
        """Run burst traffic test"""
        logger.info(f"Running burst traffic test (factor: {burst_factor}x, duration: {duration_minutes}min)")
        
        # Generate burst pattern
        pattern = self.traffic_generator.generate_burst_pattern(
            self.config["base_users"], burst_factor, duration_minutes
        )
        
        # Run test for burst period
        current_hour = datetime.now().hour
        users = pattern["hourly_users"][current_hour]
        
        if users > 0:
            logger.info(f"Running burst test with {users} users")
            
            # Use short run time for burst
            run_time = f"{duration_minutes * 60}s"
            result = self.run_hourly_test(current_hour, users, "burst_traffic", run_time=run_time)
            
            if result:
                self.save_burst_results(pattern, result)
                return True
        
        return False
    
    def run_gradual_ramp_test(self, start_users: int = 50, end_users: int = 200, duration_hours: int = 4) -> bool:
        """Run gradual ramp-up test"""
        logger.info(f"Running gradual ramp test ({start_users} -> {end_users} users over {duration_hours} hours)")
        
        # Generate ramp pattern
        pattern = self.traffic_generator.generate_gradual_ramp_pattern(start_users, end_users, duration_hours)
        
        # Run test for ramp period
        current_hour = datetime.now().hour
        users = pattern["hourly_users"][current_hour]
        
        if users > 0:
            logger.info(f"Running ramp test with {users} users")
            
            # Use appropriate run time
            run_time = f"{duration_hours * 3600}s"
            result = self.run_hourly_test(current_hour, users, "gradual_ramp", run_time=run_time)
            
            if result:
                self.save_ramp_results(pattern, result)
                return True
        
        return False
    
    def run_hourly_test(self, hour: int, users: int, test_name: str, run_time: str = "3600s") -> Optional[Dict]:
        """Run a single hourly test"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare command
        csv_file = self.results_dir / f"{test_name}_{timestamp}.csv"
        html_file = self.reports_dir / f"{test_name}_{timestamp}.html"
        log_file = self.results_dir / f"{test_name}_{timestamp}.log"
        
        # Build user class string
        user_classes = []
        for user_class, weight in self.config["user_types"].items():
            user_classes.append(f"{user_class}:{weight}")
        
        cmd = [
            "locust",
            "-f", "realistic_scenarios.py",
            "--host", self.config["host"],
            "--users", str(users),
            "--spawn-rate", str(max(1, users // 10)),
            "--run-time", run_time,
            "--csv", str(csv_file),
            "--html", str(html_file),
            "--logfile", str(log_file),
            "--headless"
        ]
        
        # Add user classes
        for user_class in user_classes:
            cmd.extend(["--user-class", user_class])
        
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
                return {
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": end_time - start_time,
                    "csv_file": str(csv_file),
                    "html_file": str(html_file),
                    "log_file": str(log_file),
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "users": users,
                    "hour": hour
                }
            else:
                logger.error(f"Test failed with return code {result.returncode}")
                logger.error(f"STDERR: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error running test: {e}")
            return None
    
    def save_daily_results(self, date: datetime, pattern: Dict, results: List[Dict]):
        """Save daily pattern test results"""
        result_data = {
            "test_type": "daily_pattern",
            "date": date.strftime("%Y-%m-%d"),
            "pattern": pattern,
            "results": results,
            "summary": {
                "total_hours_tested": len(results),
                "total_users_tested": sum(r["users"] for r in results),
                "avg_response_time": 0,  # Would be calculated from CSV data
                "peak_hour": pattern["peak_hour"],
                "peak_users": pattern["peak_users"]
            }
        }
        
        result_file = self.results_dir / f"daily_pattern_{date.strftime('%Y%m%d')}.json"
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        logger.info(f"Daily results saved to: {result_file}")
    
    def save_scenario_results(self, scenario_type: str, date: datetime, pattern: Dict, results: List[Dict]):
        """Save scenario test results"""
        result_data = {
            "test_type": scenario_type,
            "date": date.strftime("%Y-%m-%d"),
            "pattern": pattern,
            "results": results,
            "summary": {
                "total_hours_tested": len(results),
                "total_users_tested": sum(r["users"] for r in results),
                "scenario_type": scenario_type,
                "peak_hour": pattern["peak_hour"],
                "peak_users": pattern["peak_users"]
            }
        }
        
        result_file = self.results_dir / f"{scenario_type}_{date.strftime('%Y%m%d')}.json"
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        logger.info(f"Scenario results saved to: {result_file}")
    
    def save_burst_results(self, pattern: Dict, result: Dict):
        """Save burst test results"""
        result_data = {
            "test_type": "burst_traffic",
            "timestamp": datetime.now().isoformat(),
            "pattern": pattern,
            "result": result,
            "summary": {
                "burst_factor": pattern["burst_factor"],
                "burst_duration": pattern["burst_duration"],
                "peak_users": pattern["peak_users"]
            }
        }
        
        result_file = self.results_dir / f"burst_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        logger.info(f"Burst results saved to: {result_file}")
    
    def save_ramp_results(self, pattern: Dict, result: Dict):
        """Save ramp test results"""
        result_data = {
            "test_type": "gradual_ramp",
            "timestamp": datetime.now().isoformat(),
            "pattern": pattern,
            "result": result,
            "summary": {
                "start_users": pattern["start_users"],
                "end_users": pattern["end_users"],
                "duration_hours": pattern["duration_hours"]
            }
        }
        
        result_file = self.results_dir / f"ramp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        logger.info(f"Ramp results saved to: {result_file}")
    
    def run_all_scenarios(self) -> Dict[str, bool]:
        """Run all enabled scenarios"""
        logger.info("Starting comprehensive realistic load testing")
        
        results = {}
        total_start = time.time()
        
        # Check which scenarios are enabled
        enabled_scenarios = self.config["scenarios"]
        
        if enabled_scenarios.get("daily_pattern", {}).get("enabled", False):
            logger.info("Running daily pattern test...")
            results["daily_pattern"] = self.run_daily_pattern_test()
            time.sleep(60)  # Wait between scenarios
        
        if enabled_scenarios.get("business_hours", {}).get("enabled", False):
            logger.info("Running business hours test...")
            results["business_hours"] = self.run_business_hours_test()
            time.sleep(60)
        
        if enabled_scenarios.get("weekend_pattern", {}).get("enabled", False):
            logger.info("Running weekend pattern test...")
            results["weekend_pattern"] = self.run_weekend_pattern_test()
            time.sleep(60)
        
        if enabled_scenarios.get("product_launch", {}).get("enabled", False):
            logger.info("Running product launch test...")
            results["product_launch"] = self.run_product_launch_test()
            time.sleep(60)
        
        if enabled_scenarios.get("burst_traffic", {}).get("enabled", False):
            logger.info("Running burst traffic test...")
            results["burst_traffic"] = self.run_burst_traffic_test()
            time.sleep(60)
        
        if enabled_scenarios.get("gradual_ramp", {}).get("enabled", False):
            logger.info("Running gradual ramp test...")
            results["gradual_ramp"] = self.run_gradual_ramp_test()
        
        total_end = time.time()
        total_duration = total_end - total_start
        
        # Generate summary report
        self.generate_summary_report(results, total_duration)
        
        return results
    
    def generate_summary_report(self, results: Dict[str, bool], total_duration: float):
        """Generate summary report of all realistic tests"""
        summary = {
            "test_suite": "Helm AI Realistic Load Tests",
            "timestamp": datetime.now().isoformat(),
            "total_duration": total_duration,
            "scenarios": results,
            "host": self.config["host"],
            "base_users": self.config["base_users"],
            "summary": {
                "total_scenarios": len(results),
                "successful_scenarios": sum(1 for r in results.values() if r),
                "failed_scenarios": sum(1 for r in results.values() if not r)
            },
            "user_types": self.config["user_types"]
        }
        
        summary_file = self.results_dir / f"realistic_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Realistic summary report saved to: {summary_file}")
        
        # Print summary
        logger.info(f"\nREALISTIC LOAD TEST SUMMARY:")
        logger.info(f"Total scenarios: {summary['summary']['total_scenarios']}")
        logger.info(f"Successful: {summary['summary']['successful_scenarios']}")
        logger.info(f"Failed: {summary['summary']['failed_scenarios']}")
        logger.info(f"Success rate: {summary['summary']['successful_scenarios']/summary['summary']['total_scenarios']*100:.1f}%")
        logger.info(f"Total duration: {total_duration:.2f} seconds")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Helm AI Realistic Load Test Runner")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--scenario", help="Specific scenario to run")
    parser.add_argument("--date", help="Date for pattern testing (YYYY-MM-DD)")
    parser.add_argument("--host", help="Override target host")
    parser.add_argument("--base-users", type=int, help="Override base user count")
    parser.add_argument("--burst-factor", type=float, default=3.0, help="Burst traffic multiplier")
    parser.add_argument("--burst-duration", type=int, default=30, help="Burst duration in minutes")
    parser.add_argument("--ramp-start", type=int, default=50, help="Ramp start users")
    parser.add_argument("--ramp-end", type=int, default=200, help="Ramp end users")
    parser.add_argument("--ramp-hours", type=int, default=4, help="Ramp duration in hours")
    parser.add_argument("--all", action="store_true", help="Run all scenarios")
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = RealisticLoadTestRunner(args.config)
    
    # Override configuration if specified
    if args.host:
        runner.config["host"] = args.host
    if args.base_users:
        runner.config["base_users"] = args.base_users
    
    # Parse date if specified
    test_date = None
    if args.date:
        try:
            test_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            logger.error(f"Invalid date format: {args.date}. Use YYYY-MM-DD")
            sys.exit(1)
    
    # Run appropriate tests
    if args.scenario == "daily_pattern":
        success = runner.run_daily_pattern_test(test_date)
    elif args.scenario == "business_hours":
        success = runner.run_business_hours_test(test_date)
    elif args.scenario == "weekend_pattern":
        success = runner.run_weekend_pattern_test(test_date)
    elif args.scenario == "product_launch":
        success = runner.run_product_launch_test(test_date)
    elif args.scenario == "burst_traffic":
        success = runner.run_burst_traffic_test(args.burst_factor, args.burst_duration)
    elif args.scenario == "gradual_ramp":
        success = runner.run_gradual_ramp_test(args.ramp_start, args.ramp_end, args.ramp_hours)
    elif args.all:
        success = runner.run_all_scenarios()
    else:
        logger.error("Please specify a scenario: --scenario <name> or --all")
        logger.info("Available scenarios: daily_pattern, business_hours, weekend_pattern, product_launch, burst_traffic, gradual_ramp")
        sys.exit(1)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
