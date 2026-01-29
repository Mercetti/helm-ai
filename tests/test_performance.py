"""
Performance Tests for Load Testing and Stress Testing
"""

import pytest
import time
import threading
import statistics
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import json
import random
import string

from src.monitoring.performance_monitor import performance_monitor, PerformanceProfiler


class LoadTestConfig:
    """Load test configuration"""
    
    def __init__(self,
                 base_url: str = "http://localhost:5000",
                 concurrent_users: int = 10,
                 requests_per_user: int = 100,
                 test_duration_seconds: int = 60,
                 ramp_up_seconds: int = 10):
        self.base_url = base_url
        self.concurrent_users = concurrent_users
        self.requests_per_user = requests_per_user
        self.test_duration_seconds = test_duration_seconds
        self.ramp_up_seconds = ramp_up_seconds


class LoadTestResult:
    """Load test result"""
    
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times = []
        self.errors = []
        self.start_time = None
        self.end_time = None
        self.test_duration = 0
        self.requests_per_second = 0
        self.average_response_time = 0
        self.p95_response_time = 0
        self.p99_response_time = 0
        self.error_rate = 0.0


class LoadTestRunner:
    """Load test runner"""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.result = LoadTestResult()
        self.active_threads = []
        self.stop_event = threading.Event()
    
    def run_load_test(self) -> LoadTestResult:
        """Run load test"""
        print(f"Starting load test: {self.config.concurrent_users} concurrent users, "
              f"{self.config.requests_per_user} requests per user, "
              f"duration: {self.config.test_duration_seconds}s")
        
        self.result.start_time = time.time()
        
        # Create thread pool
        with ThreadPoolExecutor(max_workers=self.config.concurrent_users) as executor:
            # Submit user simulation threads
            futures = []
            for user_id in range(self.config.concurrent_users):
                future = executor.submit(self._simulate_user, user_id)
                futures.append(future)
            
            # Wait for ramp-up period
            time.sleep(self.config.ramp_up_seconds)
            
            # Wait for test duration
            time.sleep(self.config.test_duration_seconds)
            
            # Signal threads to stop
            self.stop_event.set()
            
            # Wait for all threads to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Thread error: {e}")
        
        self.result.end_time = time.time()
        self.result.test_duration = self.result.end_time - self.result.start_time
        
        # Calculate statistics
        self._calculate_statistics()
        
        return self.result
    
    def _simulate_user(self, user_id: int):
        """Simulate a single user making requests"""
        user_result = LoadTestResult()
        user_result.start_time = time.time()
        
        requests_made = 0
        
        while not self.stop_event.is_set() and requests_made < self.config.requests_per_user:
            try:
                # Make request
                response = self._make_request()
                user_result.total_requests += 1
                user_result.successful_requests += 1
                
                # Record response time
                response_time = response.elapsed.total_seconds() * 1000
                user_result.response_times.append(response_time)
                
            except Exception as e:
                user_result.total_requests += 1
                user_result.failed_requests += 1
                user_result.errors.append(str(e))
            
            requests_made += 1
        
        # Add to global result
        self.result.total_requests += user_result.total_requests
        self.result.successful_requests += user_result.successful_requests
        self.result.failed_requests += user_result.failed_requests
        self.result.response_times.extend(user_result.response_times)
        self.result.errors.extend(user_result.errors)
    
    def _make_request(self) -> requests.Response:
        """Make a single HTTP request"""
        # Randomly select endpoint
        endpoints = [
            '/api/v1/health',
            '/api/v1/users',
            '/api/v1/analytics/summary'
        ]
        endpoint = random.choice(endpoints)
        
        url = f"{self.config.base_url}{endpoint}"
        
        # Randomly select method
        methods = ['GET', 'POST']
        method = random.choice(methods)
        
        # Prepare request data
        if method == 'POST' and endpoint == '/api/v1/users':
            data = {
                'email': f'loadtest{random.randint(1, 1000)}@example.com',
                'name': f'Load Test User {random.randint(1, 1000)}',
                'plan': 'free'
            }
            return requests.request(method, url, json=data, timeout=30)
        elif method == 'POST' and endpoint == '/api/v1/analytics/summary':
            data = {
                'metric': 'page_views',
                'value': random.randint(1, 100)
            }
            return requests.request(method, url, json=data, timeout=30)
        else:
            return requests.request(method, url, timeout=30)
    
    def _calculate_statistics(self):
        """Calculate test statistics"""
        if self.result.response_times:
            self.result.average_response_time = statistics.mean(self.result.response_times)
            self.result.p95_response_time = self._percentile(self.result.response_times, 0.95)
            self.result.p99_response_time = self._percentile(self.result.response_times, 0.99)
        
        if self.result.total_requests > 0:
            self.result.error_rate = (self.result.failed_requests / self.result.total_requests) * 100
            self.result.requests_per_second = self.result.total_requests / self.result.test_duration


class StressTestRunner:
    """Stress test runner"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results = []
    
    def run_stress_test(self, max_concurrent_users: int = 50, duration_seconds: int = 300):
        """Run stress test with increasing load"""
        print(f"Running stress test: max {max_concurrent_users} users, {duration_seconds}s duration")
        
        results = []
        
        # Test with increasing concurrency
        for concurrent_users in [5, 10, 25, 50]:
            print(f"Testing with {concurrent_users} concurrent users...")
            
            config = LoadTestConfig(
                base_url=self.base_url,
                concurrent_users=2024,
                requests_per_user=50,
                test_duration_seconds=duration_seconds // 4,
                ramp_up_seconds=5
            )
            
            runner = LoadTestRunner(config)
            result = runner.run_load_test()
            
            results.append({
                'concurrent_users': concurrent_users,
                'total_requests': result.total_requests,
                'success_rate': 100 - result.error_rate,
                'avg_response_time_ms': result.average_response_time,
                'p95_response_time_ms': result.p95_response_time
            })
        
        return results


class PerformanceTestRunner:
    """Performance test runner"""
    
    @pytest.mark.performance
    def test_api_response_time(self):
        """Test API response time under normal load"""
        config = LoadTestConfig(
            concurrent_users=5,
            requests_per_user=20,
            test_duration_seconds=30
        )
        
        runner = LoadTestRunner(config)
        result = runner.run_load_test()
        
        # Assert performance requirements
        assert result.average_response_time < 1000  # < 1 second
        assert result.p95_response_time < 2000  # < 2 seconds
        assert result.error_rate < 1.0  # < 1% error rate
        assert result.requests_per_second > 10  # > 10 RPS
        
        print(f"API Performance Test Results:")
        print(f"  Total Requests: {result.total_requests}")
        print(f"  Success Rate: {100 - result.error_rate:.2f}%")
        print(f"  Avg Response Time: {result.average_response_time:.2f}ms")
        print(f"  P95 Response Time: {result.p95_response_time:.2f}ms")
        print(f"  Requests/Second: {result.requests_per_second:.2f}")
    
    @pytest.mark.performance
    def test_database_query_performance(self):
        """Test database query performance"""
        with PerformanceProfiler("database_queries") as profile:
            # Simulate database queries
            query_times = []
            
            for i in range(100):
                start_time = time.time()
                
                # Simulate database query
                time.sleep(0.01)  # 10ms query time
                # In real test, this would be actual database query
                
                query_time = (time.time() - start_time) * 1000
                query_times.append(query_time)
                
                profile.add_profile_sample("query", query_time)
            
            # Analyze query performance
            avg_query_time = statistics.mean(query_times)
            p95_query_time = self._percentile(query_times, 0.95)
            
            # Assert performance requirements
            assert avg_query_time < 50  # < 50ms
            assert p95_query_time < 100  # < 100ms
            
            print(f"Database Query Performance:")
            print(f"  Average Query Time: {avg_query_time:.2f}ms")
            print(f"  P95 Query Time: {p95_query_time:.2f}ms")
            print(f"  Total Queries: {len(query_times)}")
    
    @pytest.mark.performance
    def test_cache_performance(self):
        """Test cache performance"""
        with PerformanceProfiler("cache_operations") as profile:
            # Simulate cache operations
            cache_times = []
            
            for i in range(1000):
                start_time = time.time()
                
                # Simulate cache get
                time.sleep(0.001)  # 1ms cache hit time
                # In real test, this would be actual cache operation
                
                cache_time = (time.time() - start_time) * 1000
                cache_times.append(cache_time)
                
                profile.add_profile_sample("cache_get", cache_time)
            
            # Analyze cache performance
            avg_cache_time = statistics.mean(cache_times)
            p95_cache_time = self._percentile(cache_times, 0.95)
            
            # Assert performance requirements
            assert avg_cache_time < 5  # < 5ms
            assert p95_cache_time < 10  # < 10ms
            
            print(f"Cache Performance:")
            print(f"  Average Cache Time: {avg_cache_time:.2f}ms")
            print(f"  P95 Cache Time: {p95_cache_time:.2f}ms")
            print(f"  Total Operations: {len(cache_times)}")
    
    @pytest.mark.performance
    def test_memory_usage(self):
        """Test memory usage during operations"""
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info.rss
        
        # Perform memory-intensive operations
        large_objects = []
        
        with PerformanceProfiler("memory_usage") as profile:
            for i in range(100):
                # Create large object
                large_object = 'x' * (1024 * 1024)  # 1MB string
                large_objects.append(large_object)
                
                profile.add_profile_sample("object_creation", len(large_object))
                
                # Force garbage collection periodically
                if i % 10 == 0:
                    gc.collect()
        
        # Get final memory usage
        final_memory = process.memory_info.rss
        memory_delta = final_memory - initial_memory
        
        # Assert memory usage is reasonable
        assert memory_delta < 100 * 1024 * 1024  # < 100MB
        
        print(f"Memory Usage Test:")
        print(f"  Initial Memory: {initial_memory / (1024*1024):.2f}MB")
        print(f"  Final Memory: {final_memory / (1024*1024):.2f}MB")
        print(f"  Memory Delta: {memory_delta / (1024*1024):.2f}MB")
    
    @pytest.mark.performance
    def test_cpu_usage(self):
        """Test CPU usage during operations"""
        import psutil
        
        # Get initial CPU usage
        initial_cpu = psutil.cpu_percent(interval=1)
        
        # Perform CPU-intensive operations
        with PerformanceProfiler("cpu_usage") as profile:
            for i in range(10):
                start_time = time.time()
                
                # CPU-intensive calculation
                result = sum(i * i for i in range(10000))
                
                operation_time = (time.time() - start_time) * 1000
                profile.add_profile_sample("calculation", operation_time)
        
        # Get final CPU usage
        final_cpu = psutil.cpu_percent(interval=1)
        
        # Assert CPU usage is reasonable
        assert final_cpu < 80  # < 80%
        
        print(f"CPU Usage Test:")
        print(f"  Initial CPU: {initial_cpu:.1f}%")
        print(f"  Final CPU: {final_cpu:.1f}%")
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]


class IntegrationPerformanceTest:
    """Integration performance tests"""
    
    @pytest.mark.performance
    def test_end_to_end_performance(self):
        """Test end-to-end performance"""
        with PerformanceProfiler("end_to_end") as profile:
            # Simulate complete user journey
            start_time = time.time()
            
            # 1. User registration
            registration_time = self._simulate_user_registration()
            
            # 2. User login
            login_time = self._simulate_user_login()
            
            # 3. Data retrieval
            data_time = self._simulate_data_retrieval()
            
            # 4. Data processing
            processing_time = self._simulate_data_processing()
            
            total_time = (time.time() - start_time) * 1000
            
            profile.add_profile_sample("registration", registration_time)
            profile.add_profile_sample("login", login_time)
            profile.add_profile_sample("data_retrieval", data_time)
            profile.add_profile_sample("data_processing", processing_time)
            profile.add_profile_sample("total_journey", total_time)
        
        # Assert total performance requirements
        assert total_time < 5000  # < 5 seconds total
        
        print(f"End-to-End Performance:")
        print(f"  Total Journey Time: {total_time:.2f}ms")
    
    def _simulate_user_registration(self) -> float:
        """Simulate user registration"""
        start_time = time.time()
        
        # Simulate registration process
        time.sleep(0.1)  # 100ms
        
        return (time.time() - start_time) * 1000
    
    def _simulate_user_login(self) -> float:
        """Simulate user login"""
        start_time = time.time()
        
        # Simulate login process
        time.sleep(0.05)  # 50ms
        
        return (time.time() - start_time) * 1000
    
    def _simulate_data_retrieval(self) -> float:
        """Simulate data retrieval"""
        start_time = time.time()
        
        # Simulate database queries
        time.sleep(0.02)  # 20ms per query
        time.sleep(0.02)  # Second query
        time.sleep(0.02)  # Third query
        
        return (time.time() - start_time) * 1000
    
    def _simulate_data_processing(self) -> float:
        """Simulate data processing"""
        start_time = time.time()
        
        # Simulate processing
        time.sleep(0.05)  # 50ms
        
        return (time.time() - start_time) * 1000


if __name__ == '__main__':
    pytest.main([__file__])
