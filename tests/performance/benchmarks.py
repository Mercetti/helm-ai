"""
Helm AI Performance Benchmarks and Baselines
Provides performance testing, benchmarking, and baseline establishment
"""

import os
import sys
import time
import json
import statistics
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import concurrent.futures
import uuid

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.performance.locustfile import HelmAIUser, AdminUser, PERFORMANCE_CONFIG
from monitoring.performance_monitor import performance_monitor
from monitoring.performance_tuning import cache_manager, query_cache
from database.database_manager import get_database_manager
from monitoring.structured_logging import logger

@dataclass
class BenchmarkResult:
    """Result of a benchmark test"""
    test_name: str
    test_type: str
    start_time: datetime
    end_time: datetime
    duration: float
    samples: List[float]
    
    @property
    def avg_time(self) -> float:
        """Average execution time"""
        return statistics.mean(self.samples) if self.samples else 0.0
    
    @property
    def median_time(self) -> float:
        """Median execution time"""
        return statistics.median(self.samples) if self.samples else 0.0
    
    @property
    def min_time(self) -> float:
        """Minimum execution time"""
        return min(self.samples) if self.samples else 0.0
    
    @property
    def max_time(self) -> float:
        """Maximum execution time"""
        return max(self.samples) if self.samples else 0.0
    
    @property
    def p95_time(self) -> float:
        """95th percentile execution time"""
        if len(self.samples) >= 20:
            sorted_samples = sorted(self.samples)
            return sorted_samples[int(len(sorted_samples) * 0.95)]
        return self.max_time
    
    @property
    def p99_time(self) -> float:
        """99th percentile execution time"""
        if len(self.samples) >= 100:
            sorted_samples = sorted(self.samples)
            return sorted_samples[int(len(sorted_samples) * 0.99)]
        return self.max_time
    
    @property
    std_dev(self) -> float:
        """Standard deviation of execution times"""
        return statistics.stdev(self.samples) if len(self.samples) > 1 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'test_name': self.test_name,
            'test_type': self.test_type,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration': self.duration,
            'samples': self.samples,
            'avg_time': self.avg_time,
            'median_time': self.median_time,
            'min_time': self.min_time,
            'max_time': self.max_time,
            'p95_time': self.p95_time,
            'p99_time': self.p99_time,
            'std_dev': self.std_dev
        }

@dataclass
class BenchmarkSuite:
    """Collection of benchmark tests"""
    name: str
    description: str
    benchmarks: List[BenchmarkResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_result(self, result: BenchmarkResult):
        """Add a benchmark result"""
        self.benchmarks.append(result)
    
    def get_result(self, test_name: str) -> Optional[BenchmarkResult]:
        """Get a specific benchmark result"""
        for result in self.benchmarks:
            if result.test_name == test_name:
                return result
        return None
    
    def get_results_by_type(self, test_type: str) -> List[BenchmarkResult]:
        """Get all results of a specific type"""
        return [r for r in self.benchmarks if r.test_type == test_type]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        if not self.benchmarks:
            return {}
        
        # Group by test type
        by_type = defaultdict(list)
        for result in self.benchmarks:
            by_type[result.test_type].append(result)
        
        summary = {
            'suite_name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'total_benchmarks': len(self.benchmarks),
            'by_type': {}
        }
        
        for test_type, results in by_type.items():
            times = [r.avg_time for r in results]
            summary['by_type'][test_type] = {
                'count': len(results),
                'avg_time': statistics.mean(times),
                'min_time': min(times),
                'max_time': max(times),
                'std_dev': statistics.stdev(times) if len(times) > 1 else 0
            }
        
        return summary

class BenchmarkRunner:
    """Runs benchmark tests and collects results"""
    
    def __init__(self, warmup_iterations: int = 3):
        self.warmup_iterations = warmup_iterations
        self.current_suite = None
        self.results = []
        
    def run_benchmark(self, test_name: str, test_func: Callable, 
                     iterations: int = 100, warmup: bool = True) -> BenchmarkResult:
        """Run a single benchmark test"""
        logger.info(f"Running benchmark: {test_name} ({iterations} iterations)")
        
        samples = []
        
        # Warm up
        if warmup:
            logger.info(f"Warming up ({self.warmup_iterations} iterations)")
            for i in range(self.warmup_iterations):
                test_func()
        
        # Run benchmark
        start_time = datetime.now()
        
        for i in range(iterations):
            start = time.time()
            test_func()
            end = time.time()
            samples.append((end - start) * 1000)  # Convert to milliseconds
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i + 1}/{iterations}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        result = BenchmarkResult(
            test_name=test_name,
            test_type='performance',
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            samples=samples
        )
        
        logger.info(f"Benchmark completed: {test_name} (avg: {result.avg_time:.2f}ms)")
        
        return result
    
    def run_suite(self, suite: BenchmarkSuite) -> BenchmarkSuite:
        """Run a benchmark suite"""
        logger.info(f"Running benchmark suite: {suite.name}")
        
        self.current_suite = suite
        
        # Run all benchmarks
        for benchmark in suite.benchmarks:
            logger.info(f"Running benchmark: {benchmark.test_name}")
            # Benchmark would be run here
        
        suite.end_time = datetime.now()
        
        return suite
    
    def compare_results(self, baseline: BenchmarkSuite, comparison: BenchmarkSuite) -> Dict[str, Any]:
        """Compare two benchmark suites"""
        comparison = {
            'baseline': baseline.get_summary(),
            'comparison': comparison.get_summary(),
            'improvements': {},
            'regressions': {},
            'unchanged': []
        }
        
        # Compare each test type
        baseline_by_type = {r.test_type: r for r in baseline.benchmarks}
        comparison_by_type = {r.test_type: r for r in comparison.benchmarks}
        
        for test_type in set(baseline_by_type.keys()) | set(comparison_by_type.keys()):
            baseline_results = baseline_by_type.get(test_type, [])
            comparison_results = comparison_by_type.get(test_type, [])
            
            if baseline_results and comparison_results:
                baseline_avg = statistics.mean([r.avg_time for r in baseline_results])
                comparison_avg = statistics.mean([r.avg_time for r in comparison_results])
                
                improvement = ((baseline_avg - comparison_avg) / baseline_avg) * 100
                
                if improvement > 0:
                    comparison['improvements'][test_type] = improvement
                elif improvement < 0:
                    comparison['regressions'][test_type] = abs(improvement)
                else:
                    comparison['unchanged'].append(test_type)
        
        return comparison

class DatabaseBenchmarks:
    """Database-specific benchmarks"""
    
    def __init__(self):
        self.db_manager = get_database_manager()
    
    def benchmark_connection_pool(self) -> BenchmarkResult:
        """Benchmark database connection pool performance"""
        def test_connection():
            with self.db_manager.get_session() as session:
                session.execute(text("SELECT 1"))
        
        return self._run_benchmark("db_connection_pool", test_connection)
    
    def benchmark_simple_query(self) -> BenchmarkResult:
        """Benchmark simple database query"""
        def test_query():
            with self.db_manager.get_session() as session:
                session.execute(text("SELECT COUNT(*) FROM users"))
        
        return self._run_benchmark("db_simple_query", test_query)
    
    def benchmark_complex_query(self) -> BenchmarkResult:
        """Benchmark complex database query"""
        def test_query():
            with self.db_manager.get_session() as session:
                session.execute(text("""
                    SELECT u.name, COUNT(a.id) as api_key_count
                    FROM users u
                    LEFT JOIN api_keys a ON u.id = a.user_id
                    WHERE u.created_at > NOW() - INTERVAL '30 days'
                    GROUP BY u.name
                    ORDER BY api_key_count DESC
                """))
        
        return self._run_benchmark("db_complex_query", test_query)
    
    def benchmark_insert(self) -> BenchmarkResult:
        """Benchmark database insert operations"""
        def test_insert():
            with self.db_manager.get_session() as session:
                for i in range(10):
                    session.execute(text("""
                        INSERT INTO users (email, name, role, created_at, updated_at)
                        VALUES (:email, :name, :role, NOW(), NOW())
                    """), {
                        'email': f"bench_user_{i}@example.com",
                        'name': f"Benchmark User {i}",
                        'role': "USER"
                    })
                    session.commit()
        
        return self._run_benchmark("db_insert", test_insert)
    
    def _run_benchmark(self, test_name: str, test_func: Callable) -> BenchmarkResult:
        """Run a database benchmark"""
        return performance_tuner.run_benchmark(test_name, test_func)

class APIBenchmarks:
    """API endpoint benchmarks"""
    
    def __init__(self):
        self.base_url = PERFORMANCE_CONFIG["host"]
        
    def benchmark_health_check(self) -> BenchmarkResult:
        """Benchmark health check endpoint"""
        def test_health_check():
            import requests
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
        
        return self._run_benchmark("api_health_check", test_health_check)
    
    def benchmark_user_profile(self) -> BenchmarkResult:
        """Benchmark user profile endpoint"""
        def test_user_profile():
            import requests
            response = requests.get(f"{self.base_url}/api/users/profile", timeout=10)
            response.raise_for_status()
        
        return self._run_benchmark("api_user_profile", test_user_profile)
    
    def benchmark_api_keys(self) -> BenchmarkResult:
        """Benchmark API keys endpoint"""
        def test_api_keys():
            import requests
            response = requests.get(f"{self.base_url}/api/keys", timeout=10)
            response.raise_for_status()
        
        return self._run_benchmark("api_api_keys", test_api_keys)
    
    def _run_benchmark(self, test_name: str, test_func: Callable) -> BenchmarkResult:
        """Run an API benchmark"""
        return performance_tuner.run_benchmark(test_name, test_func)

class CacheBenchmarks:
    """Cache performance benchmarks"""
    
    def __init__(self):
        self.cache_manager = cache_manager
        
    def benchmark_cache_get(self) -> BenchmarkResult:
        """Benchmark cache get operations"""
        def test_cache_get():
            # Test cache hit
            cache_manager.set("test_key", "test_value")
            result = cache_manager.get("test_key")
            assert result == "test_value"
        
        return self._run_benchmark("cache_get", test_cache_get)
    
    def benchmark_cache_set(self) -> BenchmarkResult:
        """Benchmark cache set operations"""
        def test_cache_set():
            for i in range(100):
                cache_manager.set(f"test_key_{i}", f"test_value_{i}")
        
        return self._run_benchmark("cache_set", test_cache_set)
    
    def benchmark_cache_clear(self) -> BenchmarkResult:
        """Benchmark cache clear operations"""
        def test_cache_clear():
            # Fill cache first
            for i in range(50):
                cache_manager.set(f"test_key_{i}", f"test_value_{i}")
            
            # Clear cache
            cache_manager.clear()
        
        return self._run_benchmark("cache_clear", test_cache_clear)
    
    def _run_benchmark(self, test_name: str, test_func: Callable) -> BenchmarkResult:
        """Run a cache benchmark"""
        return performance_tuner.run_benchmark(test_name, test_func)

class PerformanceBaselines:
    """Manages performance baselines for comparison"""
    
    def __init__(self):
        self.baselines = {}
        self.baseline_file = "performance_baselines.json"
        
    def load_baselines(self):
        """Load baselines from file"""
        try:
            if os.path.exists(self.baseline_file):
                with open(self.baseline_file, 'r') as f:
                    self.baselines = json.load(f)
                logger.info(f"Loaded {len(self.baselines)} performance baselines")
        except Exception as e:
            logger.error(f"Failed to load baselines: {e}")
    
    def save_baselines(self):
        """Save baselines to file"""
        try:
            with open(self.baseline_file, 'w') as f:
                json.dump(self.baselines, f, indent=2)
            logger.info(f"Saved {len(self.baselines)} performance baselines")
        except Exception as e:
            logger.error(f"Failed to save baselines: {e}")
    
    def add_baseline(self, test_name: str, result: BenchmarkResult):
        """Add a baseline measurement"""
        self.baselines[test_name] = result.to_dict()
        self.save_baselines()
    
    def get_baseline(self, test_name: str) -> Optional[BenchmarkResult]:
        """Get a baseline measurement"""
        baseline_data = self.baselines.get(test_name)
        if baseline_data:
            return BenchmarkResult(
                test_name=baseline_data['test_name'],
                test_type=baseline_data['test_type'],
                start_time=datetime.fromisoformat(baseline_data['start_time']),
                end_time=datetime.fromisoformat(baseline_data['end_time']),
                duration=baseline_data['duration'],
                samples=baseline_data['samples']
            )
        return None
    
    def compare_to_baseline(self, test_name: str, result: BenchmarkResult) -> Dict[str, Any]:
        """Compare result to baseline"""
        baseline = self.get_baseline(test_name)
        
        if not baseline:
            return {
                'status': 'no_baseline',
                'message': f"No baseline found for {test_name}",
                'improvement': 0.0
            }
        
        baseline_avg = baseline.avg_time
        result_avg = result.avg_time
        improvement = ((baseline_avg - result_avg) / baseline_avg) * 100
        
        return {
            'status': 'success',
            'baseline_avg': baseline_avg,
            'current_avg': result_avg,
            'improvement': improvement,
            'better': improvement > 0
        }

# Global benchmark instances
database_benchmarks = DatabaseBenchmarks()
api_benchmarks = APIBenchmarks()
cache_benchmarks = CacheBenchmarks()
performance_baselines = PerformanceBaselines()

# Benchmark suite definitions
def create_database_suite() -> BenchmarkSuite:
    """Create database benchmark suite"""
    suite = BenchmarkSuite(
        name="Database Performance",
        description="Database query and connection performance benchmarks"
    )
    
    suite.add_result(database_benchmarks.benchmark_connection_pool())
    suite.add_result(database_benchmarks.benchmark_simple_query())
    suite.add_result(database_benchmarks.benchmark_complex_query())
    suite.add_result(database_benchmarks.benchmark_insert())
    
    return suite

def create_api_suite() -> BenchmarkSuite:
    """Create API benchmark suite"""
    suite = BenchmarkSuite(
        name="API Performance",
        description="API endpoint performance benchmarks"
    )
    
    suite.add_result(api_benchmarks.benchmark_health_check())
    suite.add_result(api_benchmarks.benchmark_user_profile())
    suite.add_result(api_benchmarks.benchmark_api_keys())
    
    return suite

def create_cache_suite() -> BenchmarkSuite:
    """Create cache benchmark suite"""
    suite = BenchmarkSuite(
        name="Cache Performance",
        description="Cache performance benchmarks"
    )
    
    suite.add_result(cache_benchmarks.benchmark_cache_get())
    suite.add_result(cache_benchmarks.benchmark_cache_set())
    suite.add_result(cache_benchmarks.benchmark_cache_clear())
    
    return suite

def run_performance_tests():
    """Run all performance tests"""
    logger.info("Starting performance test suite")
    
    # Load baselines
    performance_baselines.load_baselines()
    
    # Create test suites
    suites = [
        create_database_suite(),
        create_api_suite(),
        create_cache_suite()
    ]
    
    results = []
    
    for suite in suites:
        logger.info(f"Running {suite.name}")
        result = benchmark_runner.run_suite(suite)
        results.append(result)
    
    # Compare to baselines
    for suite in results:
        for benchmark in suite.benchmarks:
            comparison = performance_baselines.compare_to_baseline(benchmark.test_name, benchmark)
            logger.info(f"Benchmark {benchmark.test_name}: {comparison['status']} - {comparison.get('improvement', 0):.2f}%")
    
    # Save new baselines
    for suite in results:
        for benchmark in suite.benchmarks:
            performance_baselines.add_baseline(benchmark.test_name, benchmark)
    
    # Generate report
    report = {
        'timestamp': datetime.now().isoformat(),
        'suites': [suite.get_summary() for suite in results],
        'total_benchmarks': sum(len(suite.benchmarks) for suite in results],
        'baselines': performance_baselines.get_baseline_file()
    }
    
    # Save report
    report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Performance test completed - report saved to {report_file}")
    
    return report

# Main benchmark execution
if __name__main__":
    run_performance_tests()
