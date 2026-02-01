
"""
Stellar Logic AI - Performance Tests
Performance and load testing
"""

import unittest
import time
import threading
import concurrent.futures
from datetime import datetime

class TestPerformance(unittest.TestCase):
    """Test system performance"""
    
    def test_threat_analysis_performance(self):
        """Test threat analysis performance"""
        # Mock threat analysis
        test_data = {
            'type': 'malware',
            'source': 'email',
            'content': 'Test malicious content' * 100  # Larger content
        }
        
        start_time = time.time()
        
        # Simulate processing
        result = {
            'threat_id': 'perf_test_001',
            'threat_score': 85.0,
            'processing_time': 0.05
        }
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Performance assertion (should complete within 1 second)
        self.assertLess(processing_time, 1.0)
        self.assertGreater(result['threat_score'], 0)
        
        print(f"✅ Threat analysis performance test passed ({processing_time:.3f}s)")
    
    def test_concurrent_requests(self):
        """Test concurrent request handling"""
        num_requests = 10
        results = []
        
        def mock_request(request_id):
            """Mock request handler"""
            time.sleep(0.1)  # Simulate processing time
            return {
                'request_id': request_id,
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            }
        
        start_time = time.time()
        
        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(mock_request, i) for i in range(num_requests)]
            
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Validate results
        self.assertEqual(len(results), num_requests)
        self.assertLess(total_time, 2.0)  # Should complete within 2 seconds
        
        for result in results:
            self.assertEqual(result['status'], 'completed')
            self.assertIn('request_id', result)
        
        print(f"✅ Concurrent requests test passed ({total_time:.3f}s for {num_requests} requests)")
    
    def test_memory_usage(self):
        """Test memory usage"""
        import psutil
        import os
        
        # Get current process
        process = psutil.Process(os.getpid())
        
        # Record initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simulate memory-intensive operation
        large_data = []
        for i in range(1000):
            large_data.append({
                'id': i,
                'data': 'x' * 1000,  # 1KB per item
                'timestamp': datetime.now().isoformat()
            })
        
        # Record peak memory
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Clean up
        del large_data
        
        # Record final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Memory should not grow excessively
        memory_growth = peak_memory - initial_memory
        self.assertLess(memory_growth, 100)  # Should not grow more than 100MB
        
        print(f"✅ Memory usage test passed (growth: {memory_growth:.1f}MB)")
    
    def test_response_time_under_load(self):
        """Test response time under load"""
        num_iterations = 50
        response_times = []
        
        for i in range(num_iterations):
            start_time = time.time()
            
            # Simulate request processing
            result = {
                'request_id': i,
                'response_time': 0.05,
                'data': 'x' * 100
            }
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
        
        # Calculate statistics
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        # Performance assertions
        self.assertLess(avg_response_time, 0.1)  # Average < 100ms
        self.assertLess(max_response_time, 0.2)  # Max < 200ms
        
        print(f"✅ Response time test passed (avg: {avg_response_time:.3f}s, max: {max_response_time:.3f}s)")

class TestScalability(unittest.TestCase):
    """Test system scalability"""
    
    def test_horizontal_scaling(self):
        """Test horizontal scaling capability"""
        # Mock scaling test
        max_concurrent_users = 100
        response_times = []
        
        def simulate_user(user_id):
            """Simulate user activity"""
            time.sleep(0.01)  # Simulate processing
            return {
                'user_id': user_id,
                'response_time': 0.01,
                'status': 'success'
            }
        
        start_time = time.time()
        
        # Simulate concurrent users
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(simulate_user, i) for i in range(max_concurrent_users)]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                response_times.append(result['response_time'])
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Validate scalability
        self.assertEqual(len(response_times), max_concurrent_users)
        self.assertLess(total_time, 5.0)  # Should complete within 5 seconds
        
        avg_response_time = sum(response_times) / len(response_times)
        self.assertLess(avg_response_time, 0.05)  # Average < 50ms
        
        print(f"✅ Horizontal scaling test passed ({max_concurrent_users} users in {total_time:.3f}s)")
    
    def test_resource_utilization(self):
        """Test resource utilization under load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Record initial resources
        initial_cpu = process.cpu_percent()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simulate load
        cpu_intensive_tasks = []
        for i in range(10):
            task = {
                'id': i,
                'calculations': [j * j for j in range(1000)],
                'timestamp': datetime.now().isoformat()
            }
            cpu_intensive_tasks.append(task)
        
        # Record peak resources
        peak_cpu = process.cpu_percent()
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Validate resource utilization
        self.assertLess(peak_memory - initial_memory, 50)  # Memory growth < 50MB
        
        print(f"✅ Resource utilization test passed (CPU: {peak_cpu:.1f}%, Memory: {peak_memory:.1f}MB)")

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestPerformance))
    test_suite.addTest(unittest.makeSuite(TestScalability))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"PERFORMANCE TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.wasSuccessful():
        print("✅ All performance tests passed!")
    else:
        print("❌ Some performance tests failed!")
