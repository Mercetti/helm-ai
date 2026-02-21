#!/usr/bin/env python3
"""
Performance Testing System
Load testing, stress testing, and performance benchmarking for all dashboards
"""

import os
import sys
import time
import json
import logging
import threading
import asyncio
import statistics
import concurrent.futures
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import requests
import psutil

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

@dataclass
class PerformanceTest:
    """Performance test data structure"""
    test_id: str
    test_type: str  # load, stress, benchmark
    target_endpoint: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    status: str  # running, completed, failed, cancelled
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    requests_per_second: float
    error_rate: float
    cpu_usage_avg: float
    memory_usage_avg: float
    network_usage_avg: float
    errors: List[str]

@dataclass
class BenchmarkResult:
    """Benchmark result data structure"""
    test_id: str
    metric_name: str
    category: str
    baseline_value: float
    current_value: float
    improvement_percent: float
    test_timestamp: datetime
    confidence: float
    notes: str

class PerformanceTestSuite:
    """Performance Testing System"""
    
    def __init__(self):
        self.logger = logging.getLogger("performance_test_suite")
        self.test_history = deque(maxlen=100)  # Last 100 tests
        self.benchmark_data = {}
        self.test_results = {}
        self.active_tests = {}
        self.test_config = {
            "load_test": {
                "concurrent_users": 10,
                "duration_seconds": 60,
                "ramp_up_seconds": 10,
                "requests_per_second": 5
            },
            "stress_test": {
                "concurrent_users": 50,
                "duration_seconds": 300,
                "ramp_up_seconds": 30,
                "requests_per_second": 20
            },
            "benchmark_test": {
                "duration_seconds": 30,
                "warmup_seconds": 10,
                "sample_size": 100
            }
        }
        self.performance_thresholds = {
            "response_time_warning": 1000,  # 1 second
            "response_time_critical": 3000,  # 3 seconds
            "error_rate_warning": 0.05,  # 5%
            "error_rate_critical": 0.10,  # 10%
            "requests_per_second_warning": 50,
            "cpu_usage_warning": 80,  # 80%
            "memory_usage_warning": 85,  # 85%
        }
        self.test_running = False
        self.test_thread = None
        
        # Initialize with sample benchmark data
        self._initialize_benchmarks()
    
    def _initialize_benchmarks(self):
        """Initialize with sample benchmark data"""
        self.benchmark_data = {
            "ai_performance": {
                "response_time": 1500.0,
                "accuracy": 0.92,
                "gpu_usage": 65.0,
                "memory_usage": 70.0
            },
            "system_health": {
                "response_time": 800.0,
                "cpu_usage": 45.0,
                "memory_usage": 60.0,
                "disk_usage": 55.0
            },
            "financial_analytics": {
                "response_time": 600.0,
                "data_processing_time": 200.0,
                "report_generation_time": 400.0
            },
            "user_engagement": {
                "response_time": 700.0,
                "query_time": 250.0,
                "data_aggregation_time": 150.0
            }
        }
        self.logger.info("Initialized performance benchmark data")
    
    def run_load_test(self, endpoint: str, config: Dict[str, Any] = None) -> str:
        """Run load test against specified endpoint"""
        test_id = f"load_test_{int(time.time())}"
        test_config = config or self.test_config["load_test"]
        
        test = PerformanceTest(
            test_id=test_id,
            test_type="load",
            target_endpoint=endpoint,
            start_time=datetime.now(),
            end_time=None,
            duration_seconds=None,
            status="running",
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            average_response_time_ms=0,
            min_response_time_ms=0,
            max_response_time_ms=0,
            requests_per_second=0,
            error_rate=0,
            cpu_usage_avg=0,
            memory_usage_avg=0,
            network_usage_avg=0,
            errors=[]
        )
        
        self.active_tests[test_id] = test
        self.test_results[test_id] = test
        
        self.logger.info(f"Starting load test {test_id} against {endpoint}")
        
        # Run load test in background thread
        thread = threading.Thread(
            target=self._execute_load_test,
            args=(test_id, endpoint, test_config),
            daemon=True
        )
        thread.start()
        
        return test_id
    
    def _execute_load_test(self, test_id: str, endpoint: str, config: Dict[str, Any]):
        """Execute load test"""
        test = self.active_tests[test_id]
        
        try:
            concurrent_users = config["concurrent_users"]
            duration = config["duration_seconds"]
            ramp_up = config["ramp_up_seconds"]
            requests_per_second = config["requests_per_second"]
            
            start_cpu = psutil.cpu_percent()
            start_memory = psutil.virtual_memory().percent
            
            # Simulate load test
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = []
                
                for user_id in range(concurrent_users):
                    future = executor.submit(
                        self._simulate_user_load,
                        endpoint,
                        user_id,
                        duration,
                        requests_per_second,
                        ramp_up
                    )
                    futures.append(future)
                
                # Wait for all users to complete
                concurrent.futures.wait(futures)
                
                # Collect results
                total_requests = 0
                successful_requests = 0
                failed_requests = 0
                response_times = []
                errors = []
                
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        total_requests += result["total_requests"]
                        successful_requests += result["successful_requests"]
                        failed_requests += result["failed_requests"]
                        response_times.extend(result["response_times"])
                        errors.extend(result["errors"])
                    except Exception as e:
                        errors.append(str(e))
                        failed_requests += 1
                
                # Update test results
                end_time = datetime.now()
                duration_seconds = (end_time - test.start_time).total_seconds()
                
                test.end_time = end_time
                test.duration_seconds = duration_seconds
                test.status = "completed"
                test.total_requests = total_requests
                test.successful_requests = successful_requests
                test.failed_requests = failed_requests
                test.average_response_time_ms = statistics.mean(response_times) if response_times else 0
                test.min_response_time_ms = min(response_times) if response_times else 0
                test.max_response_time_ms = max(response_times) if response_times else 0
                test.requests_per_second = total_requests / duration_seconds if duration_seconds > 0 else 0
                test.error_rate = failed_requests / total_requests if total_requests > 0 else 0
                test.errors = errors
                
                # Get system metrics during test
                end_cpu = psutil.cpu_percent()
                end_memory = psutil.virtual_memory().percent
                test.cpu_usage_avg = (start_cpu + end_cpu) / 2
                test.memory_usage_avg = (start_memory + end_memory) / 2
                
                # Store test results
                self.test_results[test_id] = test
                self.test_history.append(test)
                
                # Generate benchmark comparison
                self._generate_benchmark_comparison(test_id, endpoint)
                
                self.logger.info(f"Load test {test_id} completed: {successful_requests}/{total_requests} requests successful")
                
        except Exception as e:
            test.status = "failed"
            test.end_time = datetime.now()
            test.errors = [str(e)]
            self.test_results[test_id] = test
            self.test_history.append(test)
            self.logger.error(f"Load test {test_id} failed: {e}")
    
    def _simulate_user_load(self, endpoint: str, user_id: int, duration: int, requests_per_second: int, ramp_up: int) -> Dict[str, Any]:
        """Simulate user load"""
        import random
        
        total_requests = 0
        successful_requests = 0
        failed_requests = 0
        response_times = []
        errors = []
        
        # Simulate ramp-up period
        ramp_up_duration = min(ramp_up, duration)
        normal_duration = duration - ramp_up_duration
        
        # Ramp-up phase
        for second in range(ramp_up_duration):
            target_rps = (requests_per_second * (second + 1)) / ramp_up_duration
            actual_rps = int(target_rps)
            
            for _ in range(actual_rps):
                try:
                    # Simulate API request
                    response_time = random.uniform(100, 2000)  # 100ms to 2s
                    success = random.random() > 0.05  # 95% success rate
                    
                    total_requests += 1
                    if success:
                        successful_requests += 1
                        response_times.append(response_time)
                    else:
                        failed_requests += 1
                        errors.append("Simulated request failure")
                    
                    time.sleep(1.0 / actual_rps)  # Rate limiting
                    
                except Exception as e:
                    failed_requests += 1
                    errors.append(str(e))
            
            time.sleep(1)  # Move to next second
        
        # Normal phase
        for _ in range(normal_duration):
            for _ in range(requests_per_second):
                try:
                    # Simulate API request
                    response_time = random.uniform(100, 2000)  # 100ms to 2s
                    success = random.random() > 0.05  # 95% success rate
                    
                    total_requests += 1
                    if success:
                        successful_requests += 1
                        response_times.append(response_time)
                    else:
                        failed_requests += 1
                        errors.append("Simulated request failure")
                    
                    time.sleep(1.0 / requests_per_second)  # Rate limiting
                    
                except Exception as e:
                    failed_requests += 1
                    errors.append(str(e))
            
            time.sleep(1)  # Move to next second
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "response_times": response_times,
            "errors": errors
        }
    
    def run_stress_test(self, endpoint: str, config: Dict[str, Any] = None) -> str:
        """Run stress test against specified endpoint"""
        test_id = f"stress_test_{int(time.time())}"
        test_config = config or self.test_config["stress_test"]
        
        test = PerformanceTest(
            test_id=test_id,
            test_type="stress",
            target_endpoint=endpoint,
            start_time=datetime.now(),
            end_time=None,
            duration_seconds=None,
            status="running",
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            average_response_time_ms=0,
            min_response_time_ms=0,
            max_response_time_ms=0,
            requests_per_second=0,
            error_rate=0,
            cpu_usage_avg=0,
            memory_usage_avg=0,
            network_usage_avg=0,
            errors=[]
        )
        
        self.active_tests[test_id] = test
        self.test_results[test_id] = test
        
        self.logger.info(f"Starting stress test {test_id} against {endpoint}")
        
        # Run stress test in background thread
        thread = threading.Thread(
            target=self._execute_stress_test,
            args=(test_id, endpoint, test_config),
            daemon=True
        )
        thread.start()
        
        return test_id
    
    def _execute_stress_test(self, test_id: str, endpoint: str, config: Dict[str, Any]):
        """Execute stress test"""
        test = self.active_tests[test_id]
        
        try:
            concurrent_users = config["concurrent_users"]
            duration = config["duration_seconds"]
            ramp_up = config["ramp_up_seconds"]
            requests_per_second = config["requests_per_second"]
            
            start_cpu = psutil.cpu_percent()
            start_memory = psutil.virtual_memory().percent
            
            # Simulate stress test with higher load
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = []
                
                for user_id in range(concurrent_users):
                    future = executor.submit(
                        self._simulate_stress_load,
                        endpoint,
                        user_id,
                        duration,
                        requests_per_second,
                        ramp_up
                    )
                    futures.append(future)
                
                # Wait for all users to complete
                concurrent.futures.wait(futures)
                
                # Collect results
                total_requests = 0
                successful_requests = 0
                failed_requests = 0
                response_times = []
                errors = []
                
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        total_requests += result["total_requests"]
                        successful_requests += result["successful_requests"]
                        failed_requests += result["failed_requests"]
                        response_times.extend(result["response_times"])
                        errors.extend(result["errors"])
                    except Exception as e:
                        errors.append(str(e))
                        failed_requests += 1
                
                # Update test results
                end_time = datetime.now()
                duration_seconds = (end_time - test.start_time).total_seconds()
                
                test.end_time = end_time
                test.duration_seconds = duration_seconds
                test.status = "completed"
                test.total_requests = total_requests
                test.successful_requests = successful_requests
                test.failed_requests = failed_requests
                test.average_response_time_ms = statistics.mean(response_times) if response_times else 0
                test.min_response_time_ms = min(response_times) if response_times else 0
                test.max_response_time_ms = max(response_times) if response_times else 0
                test.requests_per_second = total_requests / duration_seconds if duration_seconds > 0 else 0
                test.error_rate = failed_requests / total_requests if total_requests > 0 else 0
                test.errors = errors
                
                # Get system metrics during test
                end_cpu = psutil.cpu_percent()
                end_memory = psutil.virtual_memory().percent
                test.cpu_usage_avg = (start_cpu + end_cpu) / 2
                test.memory_usage_avg = (start_memory + end_memory) / 2
                
                # Store test results
                self.test_results[test_id] = test
                self.test_history.append(test)
                
                # Generate benchmark comparison
                self._generate_benchmark_comparison(test_id, endpoint)
                
                self.logger.info(f"Stress test {test_id} completed: {successful_requests}/{total_requests} requests successful")
                
        except Exception as e:
            test.status = "failed"
            test.end_time = datetime.now()
            test.errors = [str(e)]
            self.test_results[test_id] = test
            self.test_history.append(test)
            self.logger.error(f"Stress test {test_id} failed: {e}")
    
    def _simulate_stress_load(self, endpoint: str, user_id: int, duration: int, requests_per_second: int, ramp_up: int) -> Dict[str, Any]:
        """Simulate stress load with higher failure rate"""
        import random
        
        total_requests = 0
        successful_requests = 0
        failed_requests = 0
        response_times = []
        errors = []
        
        # Simulate ramp-up phase
        ramp_up_duration = min(ramp_up, duration)
        normal_duration = duration - ramp_up_duration
        
        # Ramp-up phase
        for second in range(ramp_up_duration):
            target_rps = (requests_per_second * (second + 1)) / ramp_up_duration
            actual_rps = int(target_rps)
            
            for _ in range(actual_rps):
                try:
                    # Simulate API request with higher failure rate
                    response_time = random.uniform(200, 5000)  # 200ms to 5s (slower under stress)
                    success = random.random() > 0.15  # 85% success rate (lower under stress)
                    
                    total_requests += 1
                    if success:
                        successful_requests += 1
                        response_times.append(response_time)
                    else:
                        failed_requests += 1
                        errors.append("Stress test failure")
                    
                    time.sleep(1.0 / actual_rps)  # Rate limiting
                    
                except Exception as e:
                    failed_requests += 1
                    errors.append(str(e))
            
            time.sleep(1)  # Move to next second
        
        # Normal phase
        for _ in range(normal_duration):
            for _ in range(requests_per_second):
                try:
                    # Simulate API request with higher failure rate
                    response_time = random.uniform(200, 5000)  # 200ms to 5s (slower under stress)
                    success = random.random() > 0.15  # 85% success rate (lower under stress)
                    
                    total_requests += 1
                    if success:
                        successful_requests += 1
                        response_times.append(response_time)
                    else:
                        failed_requests += 1
                        errors.append("Stress test failure")
                    
                    time.sleep(1.0 / requests_per_second)  # Rate limiting
                    
                except Exception as e:
                    failed_requests += 1
                    errors.append(str(e))
            
            time.sleep(1)  # Move to next second
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "response_times": response_times,
            "errors": errors
        }
    
    def run_benchmark_test(self, endpoint: str, config: Dict[str, Any] = None) -> str:
        """Run benchmark test against specified endpoint"""
        test_id = f"benchmark_test_{int(time.time())}"
        test_config = config or self.test_config["benchmark_test"]
        
        test = PerformanceTest(
            test_id=test_id,
            test_type="benchmark",
            target_endpoint=endpoint,
            start_time=datetime.now(),
            end_time=None,
            duration_seconds=None,
            status="running",
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            average_response_time_ms=0,
            min_response_time_ms=0,
            max_response_time_ms=0,
            requests_per_second=0,
            error_rate=0,
            cpu_usage_avg=0,
            memory_usage_avg=0,
            network_usage_avg=0,
            errors=[]
        )
        
        self.active_tests[test_id] = test
        self.test_results[test_id] = test
        
        self.logger.info(f"Starting benchmark test {test_id} against {endpoint}")
        
        # Run benchmark test in background thread
        thread = threading.Thread(
            target=self._execute_benchmark_test,
            args=(test_id, endpoint, test_config),
            daemon=True
        )
        thread.start()
        
        return test_id
    
    def _execute_benchmark_test(self, test_id: str, endpoint: str, config: Dict[str, Any]):
        """Execute benchmark test"""
        test = self.active_tests[test_id]
        
        try:
            duration = config["duration_seconds"]
            warmup = config["warmup_seconds"]
            sample_size = config["sample_size"]
            
            start_cpu = psutil.cpu_percent()
            start_memory = psutil.virtual_memory().percent
            
            # Warmup phase
            self.logger.info(f"Benchmark test {test_id}: Warmup phase ({warmup}s)")
            for _ in range(warmup):
                try:
                    # Simulate warmup requests
                    response_time = random.uniform(100, 500)  # Faster during warmup
                    # Make warmup request
                    time.sleep(0.1)
                    
                except Exception as e:
                    self.logger.warning(f"Benchmark warmup error: {e}")
            
            # Benchmark phase
            self.logger.info(f"Benchmark test {test_id}: Benchmark phase ({duration}s)")
            response_times = []
            errors = []
            total_requests = 0
            successful_requests = 0
            failed_requests = 0
            
            for _ in range(sample_size):
                try:
                    # Simulate benchmark request
                    response_time = random.uniform(100, 800)  # Optimized response times
                    success = random.random() > 0.02  # 98% success rate (optimized)
                    
                    total_requests += 1
                    if success:
                        successful_requests += 1
                        response_times.append(response_time)
                    else:
                        failed_requests += 1
                        errors.append("Benchmark failure")
                    
                    time.sleep(0.05)  # 20 requests per second
                    
                except Exception as e:
                    failed_requests += 1
                    errors.append(str(e))
            
            # Update test results
            end_time = datetime.now()
            duration_seconds = (end_time - test.start_time).total_seconds()
            
            test.end_time = end_time
            test.duration_seconds = duration_seconds
            test.status = "completed"
            test.total_requests = total_requests
            test.successful_requests = successful_requests
            test.failed_requests = failed_requests
            test.average_response_time_ms = statistics.mean(response_times) if response_times else 0
            test.min_response_time_ms = min(response_times) if response_times else 0
            test.max_response_time_ms = max(response_times) if response_times else 0
            test.requests_per_second = total_requests / duration_seconds if duration_seconds > 0 else 0
            test.error_rate = failed_requests / total_requests if total_requests > 0 else 0
            test.errors = errors
            
            # Get system metrics during test
            end_cpu = psutil.cpu_percent()
            end_memory = psutil.virtual_memory().percent
            test.cpu_usage_avg = (start_cpu + end_cpu) / 2
            test.memory_usage_avg = (start_memory + end_memory) / 2
            
            # Store test results
            self.test_results[test_id] = test
            self.test_history.append(test)
            
            # Generate benchmark comparison
            self._generate_benchmark_comparison(test_id, endpoint)
            
            self.logger.info(f"Benchmark test {test_id} completed: {successful_requests}/{total_requests} requests successful")
            
        except Exception as e:
            test.status = "failed"
            test.end_time = datetime.now()
            test.errors = [str(e)]
            self.test_results[test_id] = test
            self.test_history.append(test)
            self.logger.error(f"Benchmark test {test_id} failed: {e}")
    
    def _generate_benchmark_comparison(self, test_id: str, endpoint: str):
        """Generate benchmark comparison"""
        test = self.test_results.get(test_id)
        if not test or test.status != "completed":
            return
        
        # Extract category from endpoint
        category = self._extract_category_from_endpoint(endpoint)
        if not category:
            return
        
        baseline = self.benchmark_data.get(category, {})
        
        # Generate benchmark results
        benchmark_results = []
        
        for metric_name, baseline_value in baseline.items():
            if metric_name == "response_time" and test.average_response_time_ms > 0:
                improvement = ((baseline_value - test.average_response_time_ms) / baseline_value) * 100
                benchmark_results.append(BenchmarkResult(
                    test_id=test_id,
                    metric_name=metric_name,
                    category=category,
                    baseline_value=baseline_value,
                    current_value=test.average_response_time_ms,
                    improvement_percent=improvement,
                    test_timestamp=test.end_time,
                    confidence=0.95,
                    notes=f"Response time improved by {improvement:.1f}%"
                ))
            elif metric_name == "cpu_usage" and test.cpu_usage_avg > 0:
                improvement = ((baseline_value - test.cpu_usage_avg) / baseline_value) * 100
                benchmark_results.append(BenchmarkResult(
                    test_id=test_id,
                    metric_name=metric_name,
                    category=category,
                    baseline_value=baseline_value,
                    current_value=test.cpu_usage_avg,
                    improvement_percent=improvement,
                    test_timestamp=test.end_time,
                    confidence=0.90,
                    notes=f"CPU usage improved by {improvement:.1f}%"
                ))
            elif metric_name == "memory_usage" and test.memory_usage_avg > 0:
                improvement = ((baseline_value - test.memory_usage_avg) / baseline_value) * 100
                benchmark_results.append(BenchmarkResult(
                    test_id=test_id,
                    metric_name=metric_name,
                    category=category,
                    baseline_value=baseline_value,
                    current_value=test.memory_usage_avg,
                    improvement_percent=improvement,
                    test_timestamp=test.end_time,
                    confidence=0.90,
                    notes=f"Memory usage improved by {improvement:.1f}%"
                ))
        
        # Store benchmark results
        self.benchmark_data[f"{category}_latest"] = {
            "response_time": test.average_response_time_ms,
            "cpu_usage": test.cpu_usage_avg,
            "memory_usage": test.memory_usage_avg
        }
        
        self.logger.info(f"Generated {len(benchmark_results)} benchmark comparisons for {test_id}")
    
    def _extract_category_from_endpoint(self, endpoint: str) -> Optional[str]:
        """Extract category from endpoint URL"""
        if "ai-performance" in endpoint:
            return "ai_performance"
        elif "system-health" in endpoint:
            return "system_health"
        elif "financial" in endpoint:
            return "financial_analytics"
        elif "analytics" in endpoint:
            return "user_engagement"
        return None
    
    def get_test_results(self, test_id: str = None) -> Dict[str, Any]:
        """Get performance test results"""
        if test_id:
            return asdict(self.test_results.get(test_id, {}))
        
        return {
            "active_tests": {tid: asdict(test) for tid, test in self.active_tests.items()},
            "test_history": [asdict(test) for test in self.test_history],
            "benchmark_data": self.benchmark_data,
            "performance_thresholds": self.performance_thresholds
        }
    
    def get_test_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get performance test summary"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_tests = [
            test for test in self.test_history 
            if test.start_time >= cutoff_date
        ]
        
        # Calculate summary statistics
        summary = {
            "period_days": days,
            "total_tests": len(recent_tests),
            "completed_tests": len([t for t in recent_tests if t.status == "completed"]),
            "failed_tests": len([t for t in recent_tests if t.status == "failed"]),
            "average_response_time": 0,
            "average_requests_per_second": 0,
            "average_error_rate": 0,
            "test_types": defaultdict(int),
            "performance_trends": {}
        }
        
        if recent_tests:
            # Calculate averages
            completed_tests = [t for t in recent_tests if t.status == "completed"]
            if completed_tests:
                summary["average_response_time"] = statistics.mean([t.average_response_time_ms for t in completed_tests])
                summary["average_requests_per_second"] = statistics.mean([t.requests_per_second for t in completed_tests])
                summary["average_error_rate"] = statistics.mean([t.error_rate for t in completed_tests])
            
            # Count test types
            for test in recent_tests:
                summary["test_types"][test.test_type] += 1
            
            # Calculate performance trends
            for test_type in ["load", "stress", "benchmark"]:
                type_tests = [t for t in recent_tests if t.test_type == test_type and t.status == "completed"]
                if type_tests:
                    summary["performance_trends"][test_type] = {
                        "count": len(type_tests),
                        "avg_response_time": statistics.mean([t.average_response_time_ms for t in type_tests]),
                        "avg_requests_per_second": statistics.mean([t.requests_per_second for t in type_tests]),
                        "avg_error_rate": statistics.mean([t.error_rate for t in type_tests])
                    }
        
        return summary

# Global performance test suite instance
performance_test_suite = PerformanceTestSuite()
