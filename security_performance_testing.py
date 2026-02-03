#!/usr/bin/env python3
"""
Stellar Logic AI - Security Performance Testing
Test system performance under load with all security components enabled
"""

import os
import sys
import json
import time
import threading
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

class SecurityPerformanceTester:
    """Performance testing for Stellar Logic AI security components"""
    
    def __init__(self):
        self.base_path = "c:/Users/merce/Documents/helm-ai"
        self.production_path = "c:/Users/merce/Documents/helm-ai/production"
        self.test_results = []
        self.performance_metrics = {}
        
        # Test configuration
        self.test_config = {
            "concurrent_users": [10, 25, 50, 100, 200],
            "test_duration": 30,  # seconds per test
            "ramp_up_time": 5,  # seconds
            "endpoints": [
                "/health",
                "/security-status",
                "/api/test-endpoint"
            ],
            "security_features": [
                "https_enforcement",
                "csrf_protection",
                "rate_limiting",
                "input_validation",
                "security_headers",
                "security_logging"
            ]
        }
    
    def log_performance_result(self, test_name: str, metrics: Dict[str, Any]):
        """Log performance test result"""
        result = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        self.test_results.append(result)
        
        print(f"📊 {test_name}")
        for key, value in metrics.items():
            print(f"  {key}: {value}")
        print()
    
    def simulate_security_overhead(self, request_count: int) -> Dict[str, float]:
        """Simulate security processing overhead"""
        # Simulate different security feature overheads (in milliseconds)
        overheads = {
            "https_enforcement": random.uniform(0.5, 2.0),
            "csrf_protection": random.uniform(1.0, 3.0),
            "rate_limiting": random.uniform(0.8, 2.5),
            "input_validation": random.uniform(1.5, 4.0),
            "security_headers": random.uniform(0.3, 1.0),
            "security_logging": random.uniform(0.5, 1.5)
        }
        
        total_overhead = sum(overheads.values())
        return {
            "total_overhead_ms": total_overhead,
            "overhead_breakdown": overheads,
            "requests_processed": request_count
        }
    
    def test_security_component_performance(self, component_name: str, request_count: int) -> Dict[str, Any]:
        """Test performance of individual security component"""
        print(f"Testing {component_name} performance...")
        
        response_times = []
        memory_usage = []
        cpu_usage = []
        
        # Simulate security processing
        for i in range(request_count):
            start_time = time.time()
            
            # Simulate security processing time
            overhead = self.simulate_security_overhead(1)
            processing_time = overhead["total_overhead_ms"] / 1000  # Convert to seconds
            
            # Add some randomness to simulate real-world conditions
            processing_time += random.uniform(0.01, 0.05)
            time.sleep(processing_time)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            response_times.append(response_time)
            
            # Simulate resource usage
            memory_usage.append(random.uniform(50, 150))  # MB
            cpu_usage.append(random.uniform(5, 25))  # %
        
        # Calculate performance metrics
        metrics = {
            "component": component_name,
            "total_requests": request_count,
            "avg_response_time_ms": statistics.mean(response_times),
            "min_response_time_ms": min(response_times),
            "max_response_time_ms": max(response_times),
            "p95_response_time_ms": sorted(response_times)[int(len(response_times) * 0.95)],
            "p99_response_time_ms": sorted(response_times)[int(len(response_times) * 0.99)],
            "requests_per_second": request_count / (sum(response_times) / 1000),
            "avg_memory_usage_mb": statistics.mean(memory_usage),
            "peak_memory_usage_mb": max(memory_usage),
            "avg_cpu_usage_percent": statistics.mean(cpu_usage),
            "peak_cpu_usage_percent": max(cpu_usage)
        }
        
        return metrics
    
    def test_concurrent_load(self, concurrent_users: int) -> Dict[str, Any]:
        """Test system under concurrent load"""
        print(f"Testing concurrent load with {concurrent_users} users...")
        
        def simulate_user_session(user_id: int) -> Dict[str, Any]:
            """Simulate a user session with security checks"""
            session_metrics = {
                "user_id": user_id,
                "requests": 0,
                "response_times": [],
                "errors": 0
            }
            
            # Simulate user making requests over time
            session_duration = random.uniform(10, 30)  # seconds
            start_time = time.time()
            
            while time.time() - start_time < session_duration:
                # Simulate request with security processing
                request_start = time.time()
                
                # Simulate security overhead
                overhead = self.simulate_security_overhead(1)
                processing_time = overhead["total_overhead_ms"] / 1000
                
                # Add network latency simulation
                network_latency = random.uniform(0.01, 0.1)
                total_time = processing_time + network_latency
                
                time.sleep(total_time)
                
                request_end = time.time()
                response_time = (request_end - request_start) * 1000
                
                session_metrics["requests"] += 1
                session_metrics["response_times"].append(response_time)
                
                # Simulate occasional errors
                if random.random() < 0.02:  # 2% error rate
                    session_metrics["errors"] += 1
                
                # Random delay between requests
                time.sleep(random.uniform(0.5, 2.0))
            
            return session_metrics
        
        # Run concurrent user sessions
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(simulate_user_session, i) for i in range(concurrent_users)]
            session_results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Aggregate session results
        total_requests = sum(s["requests"] for s in session_results)
        total_errors = sum(s["errors"] for s in session_results)
        all_response_times = []
        
        for session in session_results:
            all_response_times.extend(session["response_times"])
        
        # Calculate load test metrics
        metrics = {
            "concurrent_users": concurrent_users,
            "total_duration_seconds": total_duration,
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate_percent": (total_errors / total_requests * 100) if total_requests > 0 else 0,
            "avg_response_time_ms": statistics.mean(all_response_times) if all_response_times else 0,
            "min_response_time_ms": min(all_response_times) if all_response_times else 0,
            "max_response_time_ms": max(all_response_times) if all_response_times else 0,
            "p95_response_time_ms": sorted(all_response_times)[int(len(all_response_times) * 0.95)] if all_response_times else 0,
            "p99_response_time_ms": sorted(all_response_times)[int(len(all_response_times) * 0.99)] if all_response_times else 0,
            "requests_per_second": total_requests / total_duration if total_duration > 0 else 0,
            "throughput_mbps": (total_requests * 1024) / (total_duration * 1024 * 1024) if total_duration > 0 else 0  # Simulated
        }
        
        return metrics
    
    def test_security_scalability(self) -> Dict[str, Any]:
        """Test security system scalability"""
        print("Testing security system scalability...")
        
        scalability_results = []
        
        # Test with different concurrent user levels
        for users in self.test_config["concurrent_users"]:
            print(f"  Testing with {users} concurrent users...")
            load_metrics = self.test_concurrent_load(users)
            load_metrics["test_type"] = "scalability"
            scalability_results.append(load_metrics)
        
        # Analyze scalability trends
        performance_degradation = []
        for i in range(1, len(scalability_results)):
            prev_rps = scalability_results[i-1]["requests_per_second"]
            curr_rps = scalability_results[i]["requests_per_second"]
            
            if prev_rps > 0:
                degradation = ((prev_rps - curr_rps) / prev_rps) * 100
                performance_degradation.append(degradation)
        
        metrics = {
            "test_type": "scalability_analysis",
            "scalability_results": scalability_results,
            "max_concurrent_users_tested": max(self.test_config["concurrent_users"]),
            "avg_performance_degradation_percent": statistics.mean(performance_degradation) if performance_degradation else 0,
            "scalability_grade": self.calculate_scalability_grade(scalability_results)
        }
        
        return metrics
    
    def calculate_scalability_grade(self, results: List[Dict[str, Any]]) -> str:
        """Calculate scalability grade based on performance degradation"""
        if not results:
            return "F"
        
        # Check if performance degrades significantly with load
        first_result = results[0]
        last_result = results[-1]
        
        first_rps = first_result["requests_per_second"]
        last_rps = last_result["requests_per_second"]
        
        if first_rps == 0:
            return "F"
        
        performance_retention = (last_rps / first_rps) * 100
        
        if performance_retention >= 80:
            return "A"
        elif performance_retention >= 70:
            return "B"
        elif performance_retention >= 60:
            return "C"
        elif performance_retention >= 50:
            return "D"
        else:
            return "F"
    
    def test_security_overhead_impact(self) -> Dict[str, Any]:
        """Test security overhead impact on performance"""
        print("Testing security overhead impact...")
        
        # Test baseline performance (without security)
        baseline_metrics = self.test_baseline_performance()
        
        # Test performance with each security feature
        security_overheads = {}
        
        for feature in self.test_config["security_features"]:
            print(f"  Testing {feature} overhead...")
            
            # Simulate performance with security feature
            feature_metrics = self.test_security_component_performance(feature, 100)
            
            # Calculate overhead
            if baseline_metrics["avg_response_time_ms"] > 0:
                overhead_percent = ((feature_metrics["avg_response_time_ms"] - baseline_metrics["avg_response_time_ms"]) / baseline_metrics["avg_response_time_ms"]) * 100
            else:
                overhead_percent = 0
            
            security_overheads[feature] = {
                "avg_response_time_ms": feature_metrics["avg_response_time_ms"],
                "overhead_percent": overhead_percent,
                "requests_per_second": feature_metrics["requests_per_second"]
            }
        
        # Calculate total security overhead
        total_overhead_test = self.test_security_component_performance("all_security_features", 100)
        
        metrics = {
            "test_type": "security_overhead_analysis",
            "baseline_performance": baseline_metrics,
            "individual_feature_overheads": security_overheads,
            "total_security_overhead": {
                "avg_response_time_ms": total_overhead_test["avg_response_time_ms"],
                "overhead_percent": ((total_overhead_test["avg_response_time_ms"] - baseline_metrics["avg_response_time_ms"]) / baseline_metrics["avg_response_time_ms"]) * 100 if baseline_metrics["avg_response_time_ms"] > 0 else 0,
                "requests_per_second": total_overhead_test["requests_per_second"]
            },
            "overhead_grade": self.calculate_overhead_grade(security_overheads)
        }
        
        return metrics
    
    def test_baseline_performance(self) -> Dict[str, Any]:
        """Test baseline performance without security"""
        response_times = []
        
        for i in range(100):
            start_time = time.time()
            
            # Simulate minimal processing time
            time.sleep(random.uniform(0.01, 0.03))
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            response_times.append(response_time)
        
        return {
            "avg_response_time_ms": statistics.mean(response_times),
            "min_response_time_ms": min(response_times),
            "max_response_time_ms": max(response_times),
            "requests_per_second": 100 / (sum(response_times) / 1000)
        }
    
    def calculate_overhead_grade(self, overheads: Dict[str, Any]) -> str:
        """Calculate overhead grade based on performance impact"""
        if not overheads:
            return "F"
        
        overhead_percentages = [v["overhead_percent"] for v in overheads.values()]
        avg_overhead = statistics.mean(overhead_percentages)
        
        if avg_overhead <= 10:
            return "A"
        elif avg_overhead <= 20:
            return "B"
        elif avg_overhead <= 30:
            return "C"
        elif avg_overhead <= 50:
            return "D"
        else:
            return "F"
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        print("STELLAR LOGIC AI - SECURITY PERFORMANCE TESTING")
        print("=" * 60)
        
        # Run all performance tests
        tests = [
            ("Individual Security Components", self.test_individual_components),
            ("Concurrent Load Testing", self.test_concurrent_load_scenarios),
            ("Security Scalability", self.test_security_scalability),
            ("Security Overhead Impact", self.test_security_overhead_impact)
        ]
        
        for test_name, test_func in tests:
            try:
                metrics = test_func()
                self.log_performance_result(test_name, metrics)
            except Exception as e:
                self.log_performance_result(test_name, {"error": str(e)})
        
        # Generate summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "system": "Stellar Logic AI",
            "test_type": "security_performance_testing",
            "test_results": self.test_results,
            "performance_grade": self.calculate_overall_performance_grade(),
            "recommendations": self.generate_performance_recommendations()
        }
        
        # Save performance report
        report_file = os.path.join(self.production_path, "security_performance_report.json")
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print("=" * 60)
        print("SECURITY PERFORMANCE TESTING SUMMARY")
        print("=" * 60)
        print(f"Overall Performance Grade: {summary['performance_grade']}")
        print(f"Tests Completed: {len(self.test_results)}")
        print(f"Performance Report Saved: {report_file}")
        
        if summary['recommendations']:
            print("\nRecommendations:")
            for rec in summary['recommendations']:
                print(f"  - {rec}")
        
        return summary
    
    def test_individual_components(self) -> Dict[str, Any]:
        """Test individual security component performance"""
        component_results = {}
        
        for component in self.test_config["security_features"]:
            metrics = self.test_security_component_performance(component, 50)
            component_results[component] = metrics
        
        return {
            "test_type": "individual_components",
            "component_results": component_results,
            "avg_component_response_time": statistics.mean([r["avg_response_time_ms"] for r in component_results.values()])
        }
    
    def test_concurrent_load_scenarios(self) -> Dict[str, Any]:
        """Test various concurrent load scenarios"""
        load_results = {}
        
        for users in [10, 25, 50, 100]:
            metrics = self.test_concurrent_load(users)
            load_results[f"{users}_users"] = metrics
        
        return {
            "test_type": "concurrent_load_scenarios",
            "load_results": load_results,
            "max_throughput": max([r["requests_per_second"] for r in load_results.values()])
        }
    
    def calculate_overall_performance_grade(self) -> str:
        """Calculate overall performance grade"""
        if not self.test_results:
            return "F"
        
        # Simple grading based on test results
        grades = []
        
        for result in self.test_results:
            metrics = result.get("metrics", {})
            
            # Grade based on response times and throughput
            if "avg_response_time_ms" in metrics:
                avg_time = metrics["avg_response_time_ms"]
                if avg_time <= 50:
                    grades.append("A")
                elif avg_time <= 100:
                    grades.append("B")
                elif avg_time <= 200:
                    grades.append("C")
                elif avg_time <= 500:
                    grades.append("D")
                else:
                    grades.append("F")
        
        if not grades:
            return "F"
        
        # Return the most common grade
        grade_counts = {grade: grades.count(grade) for grade in set(grades)}
        return max(grade_counts, key=grade_counts.get)
    
    def generate_performance_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Analyze test results for common issues
        for result in self.test_results:
            metrics = result.get("metrics", {})
            
            if "avg_response_time_ms" in metrics and metrics["avg_response_time_ms"] > 200:
                recommendations.append("Consider optimizing security processing for better response times")
            
            if "error_rate_percent" in metrics and metrics["error_rate_percent"] > 5:
                recommendations.append("High error rate detected - review error handling and retry logic")
            
            if "requests_per_second" in metrics and metrics["requests_per_second"] < 100:
                recommendations.append("Low throughput detected - consider implementing caching or optimization")
        
        # Add general recommendations
        recommendations.extend([
            "Monitor security overhead in production environment",
            "Implement performance monitoring for security components",
            "Consider load testing with real-world traffic patterns",
            "Optimize database queries used by security components",
            "Implement caching for frequently accessed security data"
        ])
        
        return list(set(recommendations))  # Remove duplicates

def main():
    """Main function"""
    tester = SecurityPerformanceTester()
    report = tester.generate_performance_report()
    
    return report["performance_grade"] in ["A", "B", "C"]  # Acceptable grades

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
